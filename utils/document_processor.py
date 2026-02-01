import os
import json
from typing import List, Dict
import PyPDF2
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """Manages document processing and indexing for multiple contexts"""

    def __init__(self, context_name: str = None, persist_directory: str = None):
        """
        Initializes the DocumentProcessor for a specific context

        Args:
            context_name: Normalized context name
            persist_directory: Directory where to save ChromaDB (optional, calculated from context_name)
        """
        self.context_name = context_name

        # Se non viene fornita una directory specifica, usa quella del contesto
        if persist_directory:
            self.persist_directory = persist_directory
        elif context_name:
            self.persist_directory = f"./data/contexts/{context_name}/chroma_db"
        else:
            # Fallback alla directory predefinita se non viene specificato nulla
            self.persist_directory = "./data/chroma_db"

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._embeddings = None  # Lazy loading: carica solo quando necessario
        self.client = None
        self.collection = None

    @property
    def embeddings(self):
        """Property for lazy loading of embedding model - loads only when needed"""
        if self._embeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        return self._embeddings

    def initialize_db(self):
        """Initializes the ChromaDB database for the current context"""
        # Crea la directory se non esiste
        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Prova prima a recuperare una collection esistente
        # Questo è importante per la retrocompatibilità con i dati migrati da v1
        existing_collections = self.client.list_collections()

        if existing_collections:
            # Usa la prima collection disponibile (per retrocompatibilità)
            self.collection = existing_collections[0]
        else:
            # Crea una nuova collection con nome specifico per il contesto
            collection_name = f"knowledge_base_{self.context_name}" if self.context_name else "knowledge_base"
            # Normalizza il nome della collection (ChromaDB ha restrizioni sui nomi)
            collection_name = self._normalize_collection_name(collection_name)

            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine", "context": self.context_name or "default"}
            )

    def release_connections(self):
        """Releases all connections to the ChromaDB database"""
        try:
            if self.collection:
                # Reset della collection
                self.collection = None
            if self.client:
                # Forza la chiusura del client
                # ChromaDB non ha un metodo close esplicito, ma possiamo resettare il riferimento
                self.client = None
        except Exception as e:
            print(f"Error releasing connections: {e}")

    def clear_database(self):
        """Clears the existing database for the current context"""
        # Prima rilascia tutte le connessioni
        self.release_connections()

        # Crea un nuovo client temporaneo per l'eliminazione
        try:
            temp_client = chromadb.PersistentClient(path=self.persist_directory)
            collections = temp_client.list_collections()

            # Elimina tutte le collections esistenti per questo contesto
            for collection in collections:
                try:
                    temp_client.delete_collection(collection.name)
                except Exception as e:
                    print(f"Error deleting collection {collection.name}: {e}")

            # Reset del client temporaneo
            temp_client = None
        except Exception as e:
            print(f"Error clearing database: {e}")

        # Re-inizializza il database con un nuovo client
        self.initialize_db()

    def process_pdf(self, file) -> List[str]:
        """Extracts text from a PDF file"""
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return self.text_splitter.split_text(text)

    def process_text(self, file) -> List[str]:
        """Processes text or markdown files"""
        content = file.read().decode('utf-8')
        return self.text_splitter.split_text(content)

    def process_url(self, url: str) -> List[str]:
        """Extracts text from a web page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Rimuovi script e style
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return self.text_splitter.split_text(text)
        except Exception as e:
            raise Exception(f"Error retrieving URL: {str(e)}")

    def add_documents(self, chunks: List[str], source: str):
        """Adds documents to the vector database of the current context"""
        if not self.collection:
            self.initialize_db()

        # Genera embeddings
        embeddings = self.embeddings.embed_documents(chunks)

        # Aggiungi al database
        ids = [f"{source}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk_id": i, "context": self.context_name or "default"} for i in range(len(chunks))]

        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Queries the vector database of the current context"""
        if not self.collection:
            self.initialize_db()

        query_embedding = self.embeddings.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results

    def get_stats(self) -> Dict:
        """Returns statistics on the current context database"""
        if not self.collection:
            self.initialize_db()

        count = self.collection.count()
        return {
            "document_count": count,
            "status": "active" if count > 0 else "empty",
            "context": self.context_name or "default"
        }

    def get_all_sources(self) -> List[str]:
        """Returns all source names (documents) present in the current context database"""
        if not self.collection:
            self.initialize_db()

        count = self.collection.count()
        if count == 0:
            return []

        # Recupera tutti i documenti con i loro metadati
        results = self.collection.get()

        # Estrai le fonti uniche dai metadati
        sources = set()
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if metadata and 'source' in metadata:
                    sources.add(metadata['source'])

        return list(sources)

    def get_all_documents(self) -> List[Dict]:
        """
        Returns all documents of the current context with their metadata

        Returns:
            List of dictionaries with 'text' and 'metadata' for each chunk
        """
        if not self.collection:
            self.initialize_db()

        count = self.collection.count()
        if count == 0:
            return []

        # Recupera tutti i documenti
        results = self.collection.get()

        documents = []
        if results and 'documents' in results and 'metadatas' in results:
            for doc, metadata in zip(results['documents'], results['metadatas']):
                documents.append({
                    'text': doc,
                    'metadata': metadata
                })

        return documents

    @staticmethod
    def _normalize_collection_name(name: str) -> str:
        """
        Normalizes a name for use as a ChromaDB collection name
        ChromaDB requires collection names of length 3-63 characters,
        containing only alphanumeric characters, underscores and hyphens

        Args:
            name: Name to normalize

        Returns:
            Normalized name
        """
        import re
        # Sostituisci caratteri non validi con underscore
        normalized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Assicurati che la lunghezza sia tra 3 e 63 caratteri
        if len(normalized) < 3:
            normalized = normalized + "_kb"
        elif len(normalized) > 63:
            normalized = normalized[:63]
        return normalized

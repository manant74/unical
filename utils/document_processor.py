import os
import json
from typing import List, Dict
import PyPDF2
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings


class DocumentProcessor:
    """Gestisce l'elaborazione e l'indicizzazione dei documenti per contesti multipli"""

    def __init__(self, context_name: str = None, persist_directory: str = None):
        """
        Inizializza il DocumentProcessor per un contesto specifico

        Args:
            context_name: Nome normalizzato del contesto
            persist_directory: Directory dove salvare il ChromaDB (opzionale, calcolato dal context_name)
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
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.client = None
        self.collection = None

    def initialize_db(self):
        """Inizializza il database ChromaDB per il contesto corrente"""
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

    def clear_database(self):
        """Cancella il database esistente per il contesto corrente"""
        if self.client and self.collection:
            try:
                # Elimina la collection corrente, qualunque sia il suo nome
                self.client.delete_collection(self.collection.name)
            except:
                pass
        self.initialize_db()

    def process_pdf(self, file) -> List[str]:
        """Estrae il testo da un file PDF"""
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return self.text_splitter.split_text(text)

    def process_text(self, file) -> List[str]:
        """Processa file di testo o markdown"""
        content = file.read().decode('utf-8')
        return self.text_splitter.split_text(content)

    def process_url(self, url: str) -> List[str]:
        """Estrae il testo da una pagina web"""
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
            raise Exception(f"Errore durante il recupero dell'URL: {str(e)}")

    def add_documents(self, chunks: List[str], source: str):
        """Aggiunge documenti al database vettoriale del contesto corrente"""
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
        """Interroga il database vettoriale del contesto corrente"""
        if not self.collection:
            self.initialize_db()

        query_embedding = self.embeddings.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results

    def get_stats(self) -> Dict:
        """Restituisce statistiche sul database del contesto corrente"""
        if not self.collection:
            self.initialize_db()

        count = self.collection.count()
        return {
            "document_count": count,
            "status": "active" if count > 0 else "empty",
            "context": self.context_name or "default"
        }

    def get_all_sources(self) -> List[str]:
        """Restituisce tutti i nomi delle fonti (documenti) presenti nel database del contesto corrente"""
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
        Restituisce tutti i documenti del contesto corrente con i loro metadati

        Returns:
            Lista di dizionari con 'text' e 'metadata' per ogni chunk
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
        Normalizza un nome per l'uso come nome di collection ChromaDB
        ChromaDB richiede nomi di collection di lunghezza 3-63 caratteri,
        contenenti solo caratteri alfanumerici, underscore e trattini

        Args:
            name: Nome da normalizzare

        Returns:
            Nome normalizzato
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

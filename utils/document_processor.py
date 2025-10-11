import os
import json
from typing import List, Dict
import PyPDF2
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Importa dalla nuova versione per evitare deprecation warning
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback alla vecchia versione se langchain-huggingface non è installato
    from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentProcessor:
    """Gestisce l'elaborazione e l'indicizzazione dei documenti"""

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
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
        """Inizializza il database ChromaDB"""
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def clear_database(self):
        """Cancella il database esistente"""
        if self.client:
            try:
                self.client.delete_collection("knowledge_base")
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
        """Aggiunge documenti al database vettoriale"""
        if not self.collection:
            self.initialize_db()

        # Genera embeddings
        embeddings = self.embeddings.embed_documents(chunks)

        # Aggiungi al database
        ids = [f"{source}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk_id": i} for i in range(len(chunks))]

        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Interroga il database vettoriale"""
        if not self.collection:
            self.initialize_db()

        query_embedding = self.embeddings.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results

    def get_stats(self) -> Dict:
        """Restituisce statistiche sul database"""
        if not self.collection:
            self.initialize_db()

        count = self.collection.count()
        return {
            "document_count": count,
            "status": "active" if count > 0 else "empty"
        }

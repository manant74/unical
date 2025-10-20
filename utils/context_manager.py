import os
import json
import shutil
from typing import List, Dict, Optional
from datetime import datetime


class ContextManager:
    """Gestisce la creazione, selezione ed eliminazione di contesti multipli"""

    def __init__(self, base_directory: str = "./data/contexts"):
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)

    def create_context(self, name: str, description: str = "") -> Dict:
        """
        Crea un nuovo contesto con la sua struttura di cartelle

        Args:
            name: Nome del contesto (verrà normalizzato)
            description: Descrizione opzionale del contesto

        Returns:
            Dict con le informazioni del contesto creato
        """
        # Normalizza il nome del contesto (rimuovi spazi, caratteri speciali)
        normalized_name = self._normalize_name(name)
        context_path = os.path.join(self.base_directory, normalized_name)

        # Verifica se il contesto esiste già
        if os.path.exists(context_path):
            raise ValueError(f"Il contesto '{name}' esiste già")

        # Crea la struttura delle cartelle
        os.makedirs(context_path, exist_ok=True)
        os.makedirs(os.path.join(context_path, "chroma_db"), exist_ok=True)

        # Crea il file metadata
        metadata = {
            "name": name,
            "normalized_name": normalized_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "document_count": 0,
            "belief_count": 0
        }

        metadata_path = os.path.join(context_path, "context_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return metadata

    def get_all_contexts(self) -> List[Dict]:
        """
        Recupera tutti i contesti disponibili

        Returns:
            Lista di dizionari con le informazioni dei contesti
        """
        contexts = []

        if not os.path.exists(self.base_directory):
            return contexts

        for item in os.listdir(self.base_directory):
            context_path = os.path.join(self.base_directory, item)
            if os.path.isdir(context_path):
                metadata_path = os.path.join(context_path, "context_metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            contexts.append(metadata)
                    except Exception as e:
                        print(f"Errore nel caricamento del contesto {item}: {e}")

        # Ordina per data di creazione (più recente prima)
        contexts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return contexts

    def get_context(self, normalized_name: str) -> Optional[Dict]:
        """
        Recupera un contesto specifico

        Args:
            normalized_name: Nome normalizzato del contesto

        Returns:
            Dict con le informazioni del contesto o None se non esiste
        """
        context_path = os.path.join(self.base_directory, normalized_name)
        metadata_path = os.path.join(context_path, "context_metadata.json")

        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Errore nel caricamento del contesto: {e}")

        return None

    def update_context_metadata(self, normalized_name: str, updates: Dict) -> bool:
        """
        Aggiorna i metadati di un contesto

        Args:
            normalized_name: Nome normalizzato del contesto
            updates: Dizionario con i campi da aggiornare

        Returns:
            True se l'aggiornamento è riuscito, False altrimenti
        """
        context_path = os.path.join(self.base_directory, normalized_name)
        metadata_path = os.path.join(context_path, "context_metadata.json")

        if not os.path.exists(metadata_path):
            return False

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Aggiorna i campi
            metadata.update(updates)
            metadata['updated_at'] = datetime.now().isoformat()

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Errore nell'aggiornamento del contesto: {e}")
            return False

    def delete_context(self, normalized_name: str) -> bool:
        """
        Elimina un contesto e tutti i suoi dati

        Args:
            normalized_name: Nome normalizzato del contesto

        Returns:
            True se l'eliminazione è riuscita, False altrimenti
        """
        context_path = os.path.join(self.base_directory, normalized_name)

        if not os.path.exists(context_path):
            return False

        try:
            shutil.rmtree(context_path)
            return True
        except Exception as e:
            print(f"Errore nell'eliminazione del contesto: {e}")
            return False

    def get_context_path(self, normalized_name: str) -> str:
        """
        Restituisce il percorso completo di un contesto

        Args:
            normalized_name: Nome normalizzato del contesto

        Returns:
            Percorso completo del contesto
        """
        return os.path.join(self.base_directory, normalized_name)

    def get_chroma_db_path(self, normalized_name: str) -> str:
        """
        Restituisce il percorso del ChromaDB di un contesto

        Args:
            normalized_name: Nome normalizzato del contesto

        Returns:
            Percorso del ChromaDB del contesto
        """
        return os.path.join(self.base_directory, normalized_name, "chroma_db")

    def get_belief_base_path(self, normalized_name: str) -> str:
        """
        Restituisce il percorso del file belief_base di un contesto

        Args:
            normalized_name: Nome normalizzato del contesto

        Returns:
            Percorso del file belief_base.json del contesto
        """
        return os.path.join(self.base_directory, normalized_name, "belief_base.json")

    def export_context(self, normalized_name: str, export_path: str) -> bool:
        """
        Esporta un contesto in un file ZIP

        Args:
            normalized_name: Nome normalizzato del contesto
            export_path: Percorso dove salvare il file ZIP

        Returns:
            True se l'export è riuscito, False altrimenti
        """
        context_path = self.get_context_path(normalized_name)

        if not os.path.exists(context_path):
            return False

        try:
            shutil.make_archive(export_path.replace('.zip', ''), 'zip', context_path)
            return True
        except Exception as e:
            print(f"Errore nell'export del contesto: {e}")
            return False

    def import_context(self, zip_path: str) -> Optional[Dict]:
        """
        Importa un contesto da un file ZIP

        Args:
            zip_path: Percorso del file ZIP da importare

        Returns:
            Dict con le informazioni del contesto importato o None se fallisce
        """
        try:
            # Estrai il file ZIP
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(zip_path, temp_dir, 'zip')

                # Leggi i metadati
                metadata_path = os.path.join(temp_dir, "context_metadata.json")
                if not os.path.exists(metadata_path):
                    return None

                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                normalized_name = metadata['normalized_name']
                context_path = self.get_context_path(normalized_name)

                # Se il contesto esiste già, aggiungi un suffisso
                if os.path.exists(context_path):
                    counter = 1
                    while os.path.exists(f"{context_path}_{counter}"):
                        counter += 1
                    normalized_name = f"{normalized_name}_{counter}"
                    context_path = self.get_context_path(normalized_name)
                    metadata['normalized_name'] = normalized_name
                    metadata['name'] = f"{metadata['name']} ({counter})"

                # Copia i file
                shutil.copytree(temp_dir, context_path)

                # Aggiorna i metadati
                metadata['imported_at'] = datetime.now().isoformat()
                metadata_path = os.path.join(context_path, "context_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                return metadata
        except Exception as e:
            print(f"Errore nell'import del contesto: {e}")
            return None

    def get_global_stats(self) -> Dict:
        """
        Restituisce statistiche globali su tutti i contesti

        Returns:
            Dict con statistiche aggregate
        """
        contexts = self.get_all_contexts()

        total_documents = sum(c.get('document_count', 0) for c in contexts)
        total_beliefs = sum(c.get('belief_count', 0) for c in contexts)

        return {
            "total_contexts": len(contexts),
            "total_documents": total_documents,
            "total_beliefs": total_beliefs,
            "contexts": contexts
        }

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalizza un nome per l'uso come nome di cartella

        Args:
            name: Nome da normalizzare

        Returns:
            Nome normalizzato
        """
        # Rimuovi caratteri non validi per i nomi di file
        import re
        normalized = re.sub(r'[<>:"/\\|?*]', '', name)
        normalized = normalized.replace(' ', '_').lower()
        return normalized

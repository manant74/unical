import os
import json
import shutil
from typing import List, Dict, Optional
from datetime import datetime


class ContextManager:
    """Manages the creation, selection, and deletion of multiple contexts"""

    def __init__(self, base_directory: str = "./data/contexts"):
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)

    def create_context(self, name: str, description: str = "") -> Dict:
        """
        Creates a new context with its folder structure

        Args:
            name: Context name (will be normalized)
            description: Optional context description

        Returns:
            Dict with the created context information
        """
        # Normalizza il nome del contesto (rimuovi spazi, caratteri speciali)
        normalized_name = self._normalize_name(name)
        context_path = os.path.join(self.base_directory, normalized_name)

        # Verifica se il contesto esiste già
        if os.path.exists(context_path):
            raise ValueError(f"The context '{name}' already exists")

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
        Retrieves all available contexts

        Returns:
            List of dictionaries with context information
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
                        print(f"Error loading context {item}: {e}")

        # Ordina per data di creazione (più recente prima)
        contexts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return contexts

    def get_context(self, normalized_name: str) -> Optional[Dict]:
        """
        Retrieves a specific context

        Args:
            normalized_name: Normalized context name

        Returns:
            Dict with context information or None if it doesn't exist
        """
        context_path = os.path.join(self.base_directory, normalized_name)
        metadata_path = os.path.join(context_path, "context_metadata.json")

        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading context: {e}")

        return None

    def update_context_metadata(self, normalized_name: str, updates: Dict) -> bool:
        """
        Updates context metadata

        Args:
            normalized_name: Normalized context name
            updates: Dictionary with fields to update

        Returns:
            True if update succeeded, False otherwise
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
            print(f"Error updating context: {e}")
            return False

    def delete_context(self, normalized_name: str) -> bool:
        """
        Deletes a context and all its data

        Args:
            normalized_name: Normalized context name

        Returns:
            True if deletion succeeded, False otherwise
        """
        context_path = os.path.join(self.base_directory, normalized_name)

        if not os.path.exists(context_path):
            return False

        try:
            shutil.rmtree(context_path)
            return True
        except Exception as e:
            print(f"Error deleting context: {e}")
            return False

    def get_context_path(self, normalized_name: str) -> str:
        """
        Returns the full path of a context

        Args:
            normalized_name: Normalized context name

        Returns:
            Full path of the context
        """
        return os.path.join(self.base_directory, normalized_name)

    def get_chroma_db_path(self, normalized_name: str) -> str:
        """
        Returns the ChromaDB path of a context

        Args:
            normalized_name: Normalized context name

        Returns:
            ChromaDB path of the context
        """
        return os.path.join(self.base_directory, normalized_name, "chroma_db")

    def get_belief_base_path(self, normalized_name: str) -> str:
        """
        Returns the belief_base file path of a context

        Args:
            normalized_name: Normalized context name

        Returns:
            Path of the context's belief_base.json file
        """
        return os.path.join(self.base_directory, normalized_name, "belief_base.json")

    def export_context(self, normalized_name: str, export_path: str) -> bool:
        """
        Exports a context to a ZIP file

        Args:
            normalized_name: Normalized context name
            export_path: Path where to save the ZIP file

        Returns:
            True if export succeeded, False otherwise
        """
        context_path = self.get_context_path(normalized_name)

        if not os.path.exists(context_path):
            return False

        try:
            shutil.make_archive(export_path.replace('.zip', ''), 'zip', context_path)
            return True
        except Exception as e:
            print(f"Error exporting context: {e}")
            return False

    def import_context(self, zip_path: str) -> Optional[Dict]:
        """
        Imports a context from a ZIP file

        Args:
            zip_path: Path of the ZIP file to import

        Returns:
            Dict with imported context information or None if it fails
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
            print(f"Error importing context: {e}")
            return None

    def get_global_stats(self) -> Dict:
        """
        Returns global statistics on all contexts

        Returns:
            Dict with aggregated statistics
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
        Normalizes a name for use as a folder name

        Args:
            name: Name to normalize

        Returns:
            Normalized name
        """
        # Rimuovi caratteri non validi per i nomi di file
        import re
        normalized = re.sub(r'[<>:"/\\|?*]', '', name)
        normalized = normalized.replace(' ', '_').lower()
        return normalized

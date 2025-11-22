import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class SessionManager:
    """Gestisce le sessioni utente per LUMIA Studio"""

    def __init__(self, base_dir: str = "./data/sessions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        name: str,
        context: str,
        llm_provider: str,
        llm_model: str,
        description: str = "",
        tags: List[str] = None,
        llm_settings: Dict[str, Any] = None
    ) -> str:
        """
        Crea una nuova sessione

        Args:
            name: Nome della sessione
            context: Nome del contesto selezionato
            llm_provider: Provider LLM (gemini, claude, openai)
            llm_model: Modello LLM
            description: Descrizione opzionale
            tags: Tag opzionali
            llm_settings: Impostazioni avanzate LLM

        Returns:
            session_id: ID univoco della sessione creata
        """
        session_id = str(uuid.uuid4())
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Crea subdirectory
        (session_dir / "chat_history").mkdir(exist_ok=True)

        # Metadata
        metadata = {
            "session_id": session_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "status": "active"  # active, archived, draft
        }

        # Configuration
        config = {
            "context": context,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "llm_settings": llm_settings or {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9
            }
        }

        # Salva i file
        self._save_json(session_dir / "metadata.json", metadata)
        self._save_json(session_dir / "config.json", config)

        # Inizializza file vuoti
        self._save_json(session_dir / "belief_base.json", {"beliefs": []})
        self._save_json(session_dir / "current_bdi.json", {
            "domain_summary": "",
            "persona": {},
            "desires": [],
            "beliefs": [],
            "intentions": []
        })

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera i dati completi di una sessione"""
        session_dir = self.base_dir / session_id

        if not session_dir.exists():
            return None

        metadata = self._load_json(session_dir / "metadata.json")
        config = self._load_json(session_dir / "config.json")

        if metadata is None or config is None:
            return None

        # Aggiorna last_accessed
        metadata["last_accessed"] = datetime.now().isoformat()
        self._save_json(session_dir / "metadata.json", metadata)

        return {
            "session_id": session_id,
            "metadata": metadata,
            "config": config,
            "session_dir": str(session_dir)
        }

    def get_all_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera tutte le sessioni

        Args:
            status: Filtra per status (active, archived, draft). None per tutte.

        Returns:
            Lista di sessioni ordinate per data (più recenti prima)
        """
        sessions = []

        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                metadata = self._load_json(session_dir / "metadata.json")
                config = self._load_json(session_dir / "config.json")

                if metadata and config:
                    if status is None or metadata.get("status") == status:
                        sessions.append({
                            "session_id": session_dir.name,
                            "metadata": metadata,
                            "config": config,
                            "session_dir": str(session_dir)
                        })

        # Ordina per data di ultimo accesso (più recenti prima)
        sessions.sort(
            key=lambda x: x["metadata"].get("last_accessed", ""),
            reverse=True
        )

        return sessions

    def update_session_metadata(
        self,
        session_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> bool:
        """Aggiorna i metadata di una sessione"""
        session_dir = self.base_dir / session_id
        metadata_file = session_dir / "metadata.json"

        if not metadata_file.exists():
            return False

        metadata = self._load_json(metadata_file)

        if name is not None:
            metadata["name"] = name
        if description is not None:
            metadata["description"] = description
        if tags is not None:
            metadata["tags"] = tags
        if status is not None:
            metadata["status"] = status

        metadata["last_accessed"] = datetime.now().isoformat()

        self._save_json(metadata_file, metadata)
        return True

    def update_session_config(
        self,
        session_id: str,
        context: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Aggiorna la configurazione di una sessione"""
        session_dir = self.base_dir / session_id
        config_file = session_dir / "config.json"

        if not config_file.exists():
            return False

        config = self._load_json(config_file)

        if context is not None:
            config["context"] = context
        if llm_provider is not None:
            config["llm_provider"] = llm_provider
        if llm_model is not None:
            config["llm_model"] = llm_model
        if llm_settings is not None:
            config["llm_settings"] = llm_settings

        self._save_json(config_file, config)
        return True

    def get_belief_base(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera i belief base di una sessione"""
        session_dir = self.base_dir / session_id
        belief_file = session_dir / "belief_base.json"

        if not belief_file.exists():
            return None

        return self._load_json(belief_file)

    def update_belief_base(self, session_id: str, beliefs: List[Dict[str, Any]]) -> bool:
        """Aggiorna i belief base di una sessione"""
        session_dir = self.base_dir / session_id
        belief_file = session_dir / "belief_base.json"

        self._save_json(belief_file, {"beliefs": beliefs})
        return True

    def delete_session(self, session_id: str) -> bool:
        """Elimina una sessione (soft delete -> status archived)"""
        return self.update_session_metadata(session_id, status="archived")

    def get_bdi_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera i dati BDI (Beliefs, Desires, Intentions) di una sessione"""
        session_dir = self.base_dir / session_id
        bdi_file = session_dir / "current_bdi.json"

        if not bdi_file.exists():
            return None

        return self._load_json(bdi_file)

    def update_bdi_data(
        self,
        session_id: str,
        desires: List[Dict[str, Any]] = None,
        beliefs: List[Dict[str, Any]] = None,
        intentions: List[Dict[str, Any]] = None,
        persona: Dict[str, Any] = None,
        domain_summary: Optional[str] = None
    ) -> bool:
        """
        Aggiorna i dati BDI di una sessione normalizzandoli sul modello single-persona.

        Qualsiasi struttura legacy (es. domains/personas) viene scartata in favore del
        nuovo schema: domain_summary, persona, desires, beliefs, intentions.
        """
        session_dir = self.base_dir / session_id
        bdi_file = session_dir / "current_bdi.json"

        # Carica dati esistenti o inizializza
        current_bdi = self.get_bdi_data(session_id) or {}
        normalized_bdi = {
            "domain_summary": current_bdi.get("domain_summary", ""),
            "persona": current_bdi.get("persona", {}),
            "desires": current_bdi.get("desires", []),
            "beliefs": current_bdi.get("beliefs", []),
            "intentions": current_bdi.get("intentions", [])
        }

        # Aggiorna solo i campi forniti
        if desires is not None:
            normalized_bdi["desires"] = desires
        if beliefs is not None:
            normalized_bdi["beliefs"] = beliefs
        if intentions is not None:
            normalized_bdi["intentions"] = intentions
        if persona is not None:
            normalized_bdi["persona"] = persona
        if domain_summary is not None:
            normalized_bdi["domain_summary"] = domain_summary

        self._save_json(bdi_file, normalized_bdi)
        return True

    def get_session_path(self, session_id: str, file_name: str) -> Optional[Path]:
        """Restituisce il path completo di un file nella sessione"""
        session_dir = self.base_dir / session_id

        if not session_dir.exists():
            return None

        return session_dir / file_name

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Salva dati in formato JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Carica dati da file JSON"""
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

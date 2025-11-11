# 🗺️ ROADMAP MIGLIORAMENTI LUMIA STUDIO

**Documento**: Piano strategico di interventi tecnici
**Versione**: 1.0
**Data**: 10 Novembre 2025
**Obiettivo**: Portare LUMIA Studio da 7.2/10 a 8.5+/10

---

## 📊 OVERVIEW ROADMAP

```
┌──────────────────────────────────────────────────────────────────┐
│  FASE 1: SECURITY & STABILITY (1-2 settimane) - CRITICO         │
│  → Fix vulnerabilità + Logging + Input validation               │
├──────────────────────────────────────────────────────────────────┤
│  FASE 2: QUALITY FOUNDATIONS (2-3 settimane) - ALTA             │
│  → Testing suite + Performance optimization                      │
├──────────────────────────────────────────────────────────────────┤
│  FASE 3: ARCHITECTURE REFACTORING (3-4 settimane) - MEDIA       │
│  → Service layer + DI + Code cleanup                            │
├──────────────────────────────────────────────────────────────────┤
│  FASE 4: SCALABILITY & POLISH (2-3 settimane) - BASSA           │
│  → CI/CD + Monitoring + Documentation                           │
└──────────────────────────────────────────────────────────────────┘

Total Effort: 8-12 settimane (2-3 mesi)
Score Incremento: 7.2 → 8.5+ (target 9.0)
```

---

## 🔴 FASE 1: SECURITY & STABILITY (Settimane 1-2)

**Obiettivo**: Eliminare vulnerabilità critiche e stabilizzare la base del codice
**Priorità**: CRITICA
**Effort Totale**: 5-7 giorni lavorativi
**Score Atteso**: 7.2 → 7.8

### 1.1 Implementazione Logging Strutturato

**Priorità**: 🔴 CRITICA
**Effort**: 4-6 ore
**Dependencies**: Nessuna

#### Task Breakdown

##### 1.1.1 Setup Logging Infrastructure
```bash
# Creare utils/logger.py
touch utils/logger.py
```

**Contenuto file**:
```python
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.INFO, log_file="./logs/lumia.log"):
    """
    Configura il sistema di logging per LUMIA Studio

    Args:
        level: Livello di logging (default: INFO)
        log_file: Path del file di log
    """
    # Crea directory logs
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File Handler con rotazione (max 10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log startup message
    logging.info("=" * 80)
    logging.info("LUMIA Studio - Logging System Initialized")
    logging.info("=" * 80)

    return root_logger

# Per usare in altri file:
# import logging
# logger = logging.getLogger(__name__)
# logger.info("Message")
```

##### 1.1.2 Sostituire print() con logging

**Files da modificare** (10 file):
1. `utils/context_manager.py` (6 print statements)
2. `utils/document_processor.py` (4 print statements)
3. `utils/session_manager.py` (1 print statement)
4. Tutti i `pages/*.py` (occasionali print per debug)

**Esempio refactoring**:
```python
# PRIMA
except Exception as e:
    print(f"Errore nel caricamento: {e}")

# DOPO
import logging
logger = logging.getLogger(__name__)

except Exception as e:
    logger.error(f"Errore nel caricamento del contesto: {e}", exc_info=True)
```

**Checklist**:
- [ ] Creare `utils/logger.py`
- [ ] Aggiungere `setup_logging()` in `app.py` (startup)
- [ ] Refactorare `utils/context_manager.py`
- [ ] Refactorare `utils/document_processor.py`
- [ ] Refactorare `utils/session_manager.py`
- [ ] Refactorare `utils/llm_manager.py`
- [ ] Test logging output (check file `./logs/lumia.log`)

**Testing**:
```bash
# Verificare che i log vengano scritti
python -c "from utils.logger import setup_logging; setup_logging()"
cat logs/lumia.log
```

---

### 1.2 Fix Vulnerabilità Sicurezza

**Priorità**: 🔴 CRITICA
**Effort**: 3-4 ore
**Dependencies**: Nessuna

#### 1.2.1 Path Traversal Vulnerability

**File**: `utils/session_manager.py:260-267`

**Fix**:
```python
from pathlib import Path

def get_session_path(self, session_id: str, file_name: str) -> Optional[Path]:
    """
    Restituisce il path completo di un file nella sessione

    Args:
        session_id: ID della sessione
        file_name: Nome del file

    Returns:
        Path assoluto validato del file

    Raises:
        ValueError: Se il path risultante è fuori dalla directory sessione
    """
    import logging
    logger = logging.getLogger(__name__)

    session_dir = self.base_dir / session_id

    if not session_dir.exists():
        logger.warning(f"Session directory non esiste: {session_dir}")
        return None

    # Costruisci path completo
    full_path = (session_dir / file_name).resolve()

    # SECURITY CHECK: Verifica che il path sia dentro session_dir
    if not str(full_path).startswith(str(session_dir.resolve())):
        logger.error(f"Path traversal attempt blocked: {file_name}")
        raise ValueError(f"Invalid file path: {file_name}")

    return full_path
```

**Test**:
```python
# test_session_manager.py
def test_path_traversal_blocked():
    manager = SessionManager()
    with pytest.raises(ValueError, match="Invalid file path"):
        manager.get_session_path("valid_id", "../../../etc/passwd")
```

#### 1.2.2 SSRF Vulnerability

**File**: `utils/document_processor.py:123-141`

**Fix**:
```python
import urllib.parse
import socket
import logging

logger = logging.getLogger(__name__)

# Configurazione sicurezza URL
ALLOWED_SCHEMES = ['http', 'https']
BLOCKED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '169.254.169.254',  # AWS metadata
    '::1',  # IPv6 localhost
]
BLOCKED_NETWORKS = [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
]

def is_safe_url(url: str) -> bool:
    """Valida se un URL è sicuro per il fetching"""
    try:
        parsed = urllib.parse.urlparse(url)

        # Check schema
        if parsed.scheme not in ALLOWED_SCHEMES:
            logger.warning(f"URL schema non permesso: {parsed.scheme}")
            return False

        # Check hostname
        hostname = parsed.hostname
        if not hostname:
            logger.warning("URL senza hostname")
            return False

        if hostname.lower() in BLOCKED_HOSTS:
            logger.warning(f"Hostname bloccato: {hostname}")
            return False

        # Risolvi IP e controlla network privati
        try:
            ip = socket.gethostbyname(hostname)
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)

            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                logger.warning(f"IP privato/loopback bloccato: {ip}")
                return False
        except socket.gaierror:
            logger.warning(f"Impossibile risolvere hostname: {hostname}")
            return False

        return True

    except Exception as e:
        logger.error(f"Errore validazione URL: {e}")
        return False

def process_url(self, url: str) -> List[str]:
    """
    Estrae il testo da una pagina web (con validazione sicurezza)

    Args:
        url: URL da processare

    Returns:
        Lista di chunks di testo

    Raises:
        ValueError: Se l'URL non è sicuro
    """
    if not is_safe_url(url):
        raise ValueError(f"URL non sicuro o bloccato: {url}")

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={'User-Agent': 'LUMIA-Studio/1.0'}
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        # ... resto del codice
```

**Test**:
```python
def test_ssrf_blocked():
    processor = DocumentProcessor()

    # Dovrebbe bloccare localhost
    with pytest.raises(ValueError, match="non sicuro"):
        processor.process_url("http://localhost:22")

    # Dovrebbe bloccare AWS metadata
    with pytest.raises(ValueError, match="non sicuro"):
        processor.process_url("http://169.254.169.254/latest/meta-data/")
```

#### 1.2.3 Validazione API Keys

**File**: `utils/llm_manager.py:44-53`

**Fix**:
```python
import re
import logging

logger = logging.getLogger(__name__)

# Pattern regex per API keys
API_KEY_PATTERNS = {
    "OpenAI": r"^sk-[A-Za-z0-9]{48,}$",
    "Gemini": r"^[A-Za-z0-9_-]{39}$"
}

def _validate_api_key(self, key: str, provider: str) -> bool:
    """
    Valida formato API key per un provider

    Args:
        key: API key da validare
        provider: Nome provider (OpenAI, Gemini)

    Returns:
        True se valida, False altrimenti
    """
    if not key or not key.strip():
        logger.warning(f"{provider} API key vuota")
        return False

    pattern = API_KEY_PATTERNS.get(provider)
    if not pattern:
        logger.warning(f"Pattern validazione non definito per {provider}")
        return True  # Fallback: accetta key

    if not re.match(pattern, key):
        logger.error(f"{provider} API key formato invalido")
        return False

    return True

def _initialize_clients(self):
    """Inizializza i client per i diversi provider (con validazione)"""
    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and self._validate_api_key(openai_key, "OpenAI"):
        try:
            self.clients["OpenAI"] = OpenAI(api_key=openai_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Errore inizializzazione OpenAI: {e}")
    elif openai_key:
        logger.error("OpenAI API key presente ma invalida")

    # Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and self._validate_api_key(google_key, "Gemini"):
        try:
            genai.configure(api_key=google_key)
            self.clients["Gemini"] = genai
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Errore inizializzazione Gemini: {e}")
    elif google_key:
        logger.error("Gemini API key presente ma invalida")

    if not self.clients:
        logger.critical("Nessun provider LLM disponibile! Verifica le API keys.")
```

**Checklist**:
- [ ] Fix path traversal in `session_manager.py`
- [ ] Fix SSRF in `document_processor.py`
- [ ] Validazione API keys in `llm_manager.py`
- [ ] Aggiungere test per ogni fix
- [ ] Code review sicurezza

---

### 1.3 Input Validation con Pydantic

**Priorità**: 🔴 CRITICA
**Effort**: 6-8 ore
**Dependencies**: 1.1 (logging)

#### 1.3.1 Installare Pydantic (già presente)

```bash
# Già in requirements.txt:
# pydantic>=2.0.0
# pydantic-settings>=2.0.0
```

#### 1.3.2 Creare Schema Models

**File**: `utils/schemas.py` (NUOVO)

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SessionStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RelevanceLevel(str, Enum):
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BASSO = "BASSO"

# Session Models
class LLMSettings(BaseModel):
    use_defaults: bool = True
    temperature: float = Field(ge=0.0, le=2.0, default=1.0)
    top_p: float = Field(ge=0.0, le=1.0, default=0.95)
    max_output_tokens: Optional[int] = Field(ge=1, le=65536, default=None)
    max_tokens: Optional[int] = Field(ge=1, le=16384, default=None)
    reasoning_effort: Optional[str] = Field(default="medium", pattern="^(minimal|low|medium|high)$")

class SessionConfig(BaseModel):
    context: str
    llm_provider: str = Field(pattern="^(Gemini|OpenAI)$")
    llm_model: str
    llm_settings: LLMSettings = Field(default_factory=LLMSettings)

class SessionMetadata(BaseModel):
    session_id: str = Field(min_length=32, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    last_accessed: datetime
    status: SessionStatus = SessionStatus.ACTIVE

    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Massimo 10 tags per sessione")
        return v

class Session(BaseModel):
    """Modello completo per una sessione"""
    metadata: SessionMetadata
    config: SessionConfig

# BDI Models
class Desire(BaseModel):
    desire_id: str
    desire_statement: str = Field(min_length=10, max_length=500)
    priority: PriorityLevel = PriorityLevel.MEDIUM
    context: Optional[str] = None
    success_criteria: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class BeliefDesireCorrelation(BaseModel):
    desire_id: str
    livello_rilevanza: RelevanceLevel
    spiegazione: str = Field(min_length=10, max_length=300)

class Belief(BaseModel):
    soggetto: str = Field(min_length=1, max_length=200)
    relazione: str = Field(min_length=1, max_length=100)
    oggetto: str = Field(min_length=1, max_length=200)
    fonte: str = Field(min_length=10, max_length=1000)
    metadati: Dict[str, Any] = Field(default_factory=dict)
    desires_correlati: List[BeliefDesireCorrelation] = Field(default_factory=list)

class BDIData(BaseModel):
    desires: List[Desire] = Field(default_factory=list)
    beliefs: List[Belief] = Field(default_factory=list)
    intentions: List[Dict[str, Any]] = Field(default_factory=list)

# Context Models
class ContextMetadata(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    normalized_name: str = Field(pattern="^[a-z0-9_-]+$")
    description: str = Field(default="", max_length=500)
    created_at: datetime
    updated_at: datetime
    document_count: int = Field(ge=0, default=0)
    belief_count: int = Field(ge=0, default=0)
```

#### 1.3.3 Integrare Validation in SessionManager

**File**: `utils/session_manager.py`

```python
from utils.schemas import SessionMetadata, SessionConfig, Session, LLMSettings
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class SessionManager:
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
        Crea una nuova sessione con validazione Pydantic
        """
        try:
            # Valida llm_settings
            validated_settings = LLMSettings(**(llm_settings or {}))

            # Crea config
            config = SessionConfig(
                context=context,
                llm_provider=llm_provider,
                llm_model=llm_model,
                llm_settings=validated_settings
            )

            # Crea metadata
            session_id = str(uuid.uuid4())
            metadata = SessionMetadata(
                session_id=session_id,
                name=name,
                description=description,
                tags=tags or [],
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                status="active"
            )

            # Crea sessione completa
            session = Session(metadata=metadata, config=config)

            # Salva su filesystem
            session_dir = self.base_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Salva files (Pydantic model_dump())
            self._save_json(session_dir / "metadata.json", metadata.model_dump())
            self._save_json(session_dir / "config.json", config.model_dump())

            logger.info(f"Session created successfully: {session_id}")
            return session_id

        except ValidationError as e:
            logger.error(f"Validation error creating session: {e}")
            raise ValueError(f"Dati sessione non validi: {e}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera sessione con validazione"""
        try:
            metadata_dict = self._load_json(self.base_dir / session_id / "metadata.json")
            config_dict = self._load_json(self.base_dir / session_id / "config.json")

            if not metadata_dict or not config_dict:
                return None

            # Valida con Pydantic
            metadata = SessionMetadata(**metadata_dict)
            config = SessionConfig(**config_dict)

            # Update last_accessed
            metadata.last_accessed = datetime.now()
            self._save_json(self.base_dir / session_id / "metadata.json", metadata.model_dump())

            return {
                "session_id": session_id,
                "metadata": metadata.model_dump(),
                "config": config.model_dump(),
                "session_dir": str(self.base_dir / session_id)
            }

        except ValidationError as e:
            logger.error(f"Session data validation failed: {e}")
            return None
```

**Checklist**:
- [ ] Creare `utils/schemas.py` con tutti i modelli
- [ ] Refactorare `SessionManager` per usare Pydantic
- [ ] Refactorare `ContextManager` per usare Pydantic
- [ ] Validare BDI data in `update_bdi_data()`
- [ ] Test validation con dati invalidi

---

### 1.4 Exception Handling Refactoring

**Priorità**: 🟡 ALTA
**Effort**: 4-5 ore
**Dependencies**: 1.1 (logging)

#### Refactoring Template

**PRIMA**:
```python
try:
    # operazione
except Exception as e:
    print(f"Errore: {e}")
```

**DOPO**:
```python
import logging
logger = logging.getLogger(__name__)

try:
    # operazione
except FileNotFoundError as e:
    logger.warning(f"File non trovato: {e}")
    return None
except json.JSONDecodeError as e:
    logger.error(f"JSON invalido: {e}", exc_info=True)
    raise ValueError(f"Formato JSON non valido") from e
except IOError as e:
    logger.error(f"Errore I/O: {e}", exc_info=True)
    raise
except Exception as e:
    logger.critical(f"Errore non gestito: {e}", exc_info=True)
    raise
```

**Files da refactorare**:
1. `utils/context_manager.py` (6 exceptions)
2. `utils/document_processor.py` (4 exceptions)
3. `utils/session_manager.py` (1 exception)
4. `pages/1_Knol.py` (10 exceptions)
5. `pages/0_Compass.py` (2 exceptions)
6. `pages/2_Ali.py` (3 exceptions)
7. `pages/3_Believer.py` (5 exceptions)

**Checklist**:
- [ ] Refactorare ogni file con eccezioni specifiche
- [ ] Aggiungere `exc_info=True` per stack traces
- [ ] Rimuovere tutti i `# pylint: disable=broad-except`
- [ ] Test error handling con mock

---

## 🟡 FASE 2: QUALITY FOUNDATIONS (Settimane 3-5)

**Obiettivo**: Stabilire basi solide per qualità e performance
**Priorità**: ALTA
**Effort Totale**: 10-12 giorni lavorativi
**Score Atteso**: 7.8 → 8.3

### 2.1 Testing Suite Implementation

**Priorità**: 🟡 ALTA
**Effort**: 3-4 giorni
**Dependencies**: 1.3 (schemas), 1.1 (logging)

#### 2.1.1 Setup Test Infrastructure

**Creare struttura**:
```bash
mkdir -p tests/{unit,integration,fixtures}
touch tests/__init__.py
touch tests/conftest.py
```

**File**: `tests/conftest.py`
```python
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

@pytest.fixture
def temp_data_dir():
    """Crea directory temporanea per test"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_llm_manager():
    """Mock LLMManager per test"""
    manager = Mock()
    manager.chat.return_value = "Mock LLM response"
    manager.get_available_providers.return_value = ["Gemini", "OpenAI"]
    return manager

@pytest.fixture
def sample_session_data():
    """Dati sessione di esempio per test"""
    return {
        "session_id": "test-session-123",
        "metadata": {
            "name": "Test Session",
            "description": "Session per testing",
            "created_at": "2025-11-10T10:00:00",
            "last_accessed": "2025-11-10T10:00:00",
            "status": "active"
        },
        "config": {
            "context": "test_context",
            "llm_provider": "Gemini",
            "llm_model": "gemini-2.5-pro",
            "llm_settings": {
                "use_defaults": True,
                "temperature": 1.0,
                "top_p": 0.95
            }
        }
    }

@pytest.fixture
def sample_desires():
    """Desires di esempio"""
    return [
        {
            "desire_id": "D1",
            "desire_statement": "Test desire 1",
            "priority": "high"
        },
        {
            "desire_id": "D2",
            "desire_statement": "Test desire 2",
            "priority": "medium"
        }
    ]
```

#### 2.1.2 Unit Tests - LLMManager

**File**: `tests/unit/test_llm_manager.py`
```python
import pytest
from unittest.mock import Mock, patch
from utils.llm_manager import LLMManager

class TestLLMManager:
    def test_initialization_without_api_keys(self):
        """Test inizializzazione senza API keys"""
        with patch.dict('os.environ', {}, clear=True):
            manager = LLMManager()
            assert manager.get_available_providers() == []

    def test_get_models_for_provider(self):
        """Test recupero modelli per provider"""
        manager = LLMManager()
        gemini_models = manager.get_models_for_provider("Gemini")

        assert "gemini-2.5-pro" in gemini_models
        assert "gemini-2.5-flash" in gemini_models

    def test_use_defaults_flag_gemini(self):
        """Test flag use_defaults con Gemini"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_chat = Mock()
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_chat.send_message.return_value = mock_response
            mock_model.return_value.start_chat.return_value = mock_chat

            manager = LLMManager()
            # Mock client
            manager.clients["Gemini"] = Mock()

            # Test con use_defaults=True
            manager.chat(
                provider="Gemini",
                model="gemini-2.5-pro",
                messages=[{"role": "user", "content": "test"}],
                use_defaults=True
            )

            # Verifica: generation_config deve essere None
            call_args = mock_model.call_args
            assert call_args[1].get('generation_config') is None

    def test_reasoning_effort_gpt5(self):
        """Test reasoning_effort per GPT-5"""
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_client.chat.completions.create.return_value = mock_response

            manager = LLMManager()
            manager.clients["OpenAI"] = mock_client

            manager.chat(
                provider="OpenAI",
                model="gpt-5",
                messages=[{"role": "user", "content": "test"}],
                reasoning_effort="high"
            )

            # Verifica: reasoning_effort presente in kwargs
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs.get('reasoning_effort') == 'high'

    def test_invalid_provider_raises_error(self):
        """Test che provider invalido sollevi errore"""
        manager = LLMManager()
        with pytest.raises(ValueError, match="non disponibile"):
            manager.chat(
                provider="InvalidProvider",
                model="invalid-model",
                messages=[{"role": "user", "content": "test"}]
            )
```

#### 2.1.3 Unit Tests - SessionManager

**File**: `tests/unit/test_session_manager.py`
```python
import pytest
from utils.session_manager import SessionManager
from pydantic import ValidationError

class TestSessionManager:
    def test_create_session_valid_data(self, temp_data_dir):
        """Test creazione sessione con dati validi"""
        manager = SessionManager(base_dir=str(temp_data_dir))

        session_id = manager.create_session(
            name="Test Session",
            context="test_context",
            llm_provider="Gemini",
            llm_model="gemini-2.5-pro",
            description="Test description"
        )

        assert session_id is not None
        assert len(session_id) == 36  # UUID length

        # Verifica file creati
        session_dir = temp_data_dir / session_id
        assert (session_dir / "metadata.json").exists()
        assert (session_dir / "config.json").exists()

    def test_create_session_invalid_provider(self, temp_data_dir):
        """Test che provider invalido sollevi errore"""
        manager = SessionManager(base_dir=str(temp_data_dir))

        with pytest.raises(ValueError):
            manager.create_session(
                name="Test",
                context="test",
                llm_provider="InvalidProvider",
                llm_model="invalid"
            )

    def test_get_session(self, temp_data_dir, sample_session_data):
        """Test recupero sessione"""
        manager = SessionManager(base_dir=str(temp_data_dir))

        # Crea sessione
        session_id = manager.create_session(
            name="Test Session",
            context="test",
            llm_provider="Gemini",
            llm_model="gemini-2.5-pro"
        )

        # Recupera sessione
        session = manager.get_session(session_id)

        assert session is not None
        assert session['metadata']['name'] == "Test Session"
        assert session['config']['llm_provider'] == "Gemini"

    def test_get_session_path_security(self, temp_data_dir):
        """Test sicurezza path traversal"""
        manager = SessionManager(base_dir=str(temp_data_dir))

        # Crea sessione valida
        session_id = manager.create_session(
            name="Test",
            context="test",
            llm_provider="Gemini",
            llm_model="gemini-2.5-pro"
        )

        # Test path traversal attack
        with pytest.raises(ValueError, match="Invalid file path"):
            manager.get_session_path(session_id, "../../../etc/passwd")
```

#### 2.1.4 Integration Tests - Mix Beliefs

**File**: `tests/integration/test_mix_beliefs_workflow.py`
```python
import pytest
from unittest.mock import Mock, patch
from utils.llm_manager import LLMManager
from utils.session_manager import SessionManager
from utils.prompts import get_prompt

class TestMixBeliefsWorkflow:
    @pytest.fixture
    def setup_test_environment(self, temp_data_dir):
        """Setup ambiente test completo"""
        session_manager = SessionManager(base_dir=str(temp_data_dir))

        # Crea sessione
        session_id = session_manager.create_session(
            name="Mix Beliefs Test",
            context="test_context",
            llm_provider="Gemini",
            llm_model="gemini-2.5-pro"
        )

        # Mock desires
        desires = [
            {
                "desire_id": "D1",
                "desire_statement": "Improve user experience",
                "priority": "high"
            }
        ]
        session_manager.update_bdi_data(session_id, desires=desires)

        return session_manager, session_id

    def test_mix_beliefs_end_to_end(self, setup_test_environment):
        """Test completo workflow mix beliefs"""
        session_manager, session_id = setup_test_environment

        # Mock LLM response (JSON valido)
        mock_llm_response = '''
        {
          "beliefs": [
            {
              "soggetto": "Users",
              "relazione": "need",
              "oggetto": "intuitive interface",
              "fonte": "Generated from desire",
              "metadati": {"tipo_fonte": "generated"},
              "desires_correlati": [
                {
                  "desire_id": "D1",
                  "livello_rilevanza": "CRITICO",
                  "spiegazione": "Directly supports UX improvement"
                }
              ]
            }
          ]
        }
        '''

        with patch.object(LLMManager, 'chat', return_value=mock_llm_response):
            llm_manager = LLMManager()

            # Carica prompt
            prompt = get_prompt('believer_mix_beliefs')
            assert prompt is not None

            # Simula chiamata LLM
            response = llm_manager.chat(
                provider="Gemini",
                model="gemini-2.5-pro",
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON
            import json
            beliefs_data = json.loads(response)

            # Validate
            assert 'beliefs' in beliefs_data
            assert len(beliefs_data['beliefs']) > 0

            # Save to session
            session_manager.update_bdi_data(
                session_id,
                beliefs=beliefs_data['beliefs']
            )

            # Verify save
            bdi = session_manager.get_bdi_data(session_id)
            assert len(bdi['beliefs']) == 1
            assert bdi['beliefs'][0]['soggetto'] == "Users"
```

**Checklist Testing**:
- [ ] Setup `conftest.py` con fixtures comuni
- [ ] Unit tests per `llm_manager.py` (target: 90% coverage)
- [ ] Unit tests per `session_manager.py` (target: 85%)
- [ ] Unit tests per `document_processor.py` (target: 80%)
- [ ] Unit tests per `context_manager.py` (target: 80%)
- [ ] Integration test per mix beliefs workflow
- [ ] Integration test per session lifecycle
- [ ] Configurare pytest-cov per coverage report

**Comandi**:
```bash
# Run tests
pytest tests/

# Con coverage
pytest --cov=utils --cov=pages tests/

# Coverage report HTML
pytest --cov=utils --cov-report=html tests/
open htmlcov/index.html
```

---

### 2.2 Performance Optimization

**Priorità**: 🟡 ALTA
**Effort**: 2-3 giorni
**Dependencies**: 2.1 (tests come safety net)

#### 2.2.1 Embeddings Model Singleton

**File**: `utils/embeddings_cache.py` (NUOVO)

```python
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

_embeddings_cache = {}

@lru_cache(maxsize=None)
def get_embeddings_model(model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    """
    Restituisce istanza cached del modello embeddings

    Args:
        model_name: Nome del modello HuggingFace

    Returns:
        HuggingFaceEmbeddings instance (singleton)
    """
    if model_name not in _embeddings_cache:
        logger.info(f"Loading embeddings model: {model_name}")
        _embeddings_cache[model_name] = HuggingFaceEmbeddings(model_name=model_name)
        logger.info(f"Embeddings model loaded successfully: {model_name}")

    return _embeddings_cache[model_name]

def clear_embeddings_cache():
    """Cancella cache embeddings (per test)"""
    global _embeddings_cache
    _embeddings_cache.clear()
    get_embeddings_model.cache_clear()
```

**Refactoring**: `utils/document_processor.py`

```python
from utils.embeddings_cache import get_embeddings_model

class DocumentProcessor:
    def __init__(self, context_name: str = None, persist_directory: str = None):
        # ... setup paths ...

        # PRIMA: caricava sempre il modello
        # self.embeddings = HuggingFaceEmbeddings(...)

        # DOPO: usa singleton cached
        self.embeddings = get_embeddings_model()

        # ... resto codice ...
```

**Performance Gain**:
- Prima: 5-8s per ogni istanza DocumentProcessor
- Dopo: 5-8s solo per PRIMA istanza, <100ms per istanze successive
- Risparmio RAM: ~500MB per istanza salvati

#### 2.2.2 RAG Query Cache

**File**: `utils/document_processor.py`

```python
from functools import lru_cache
import hashlib

def _hash_query(query_text: str, n_results: int) -> str:
    """Crea hash per cache query"""
    key = f"{query_text}:{n_results}"
    return hashlib.sha256(key.encode()).hexdigest()

@lru_cache(maxsize=100)
def _query_cached(self, query_hash: str, query_text: str, n_results: int):
    """Query con cache LRU"""
    return self._query_internal(query_text, n_results)

def _query_internal(self, query_text: str, n_results: int):
    """Query interna senza cache"""
    if not self.collection:
        self.initialize_db()

    query_embedding = self.embeddings.embed_query(query_text)

    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results

def query(self, query_text: str, n_results: int = 5, use_cache: bool = True):
    """
    Query con cache opzionale

    Args:
        query_text: Testo query
        n_results: Numero risultati
        use_cache: Usa cache LRU (default True)

    Returns:
        Results dict
    """
    if use_cache:
        query_hash = self._hash_query(query_text, n_results)
        return self._query_cached(query_hash, query_text, n_results)
    else:
        return self._query_internal(query_text, n_results)

def clear_query_cache(self):
    """Cancella cache query"""
    self._query_cached.cache_clear()
```

**Performance Gain**:
- Query ripetute: da ~1-2s a <50ms
- Hit rate atteso: 20-30% in sessione tipica

#### 2.2.3 Eager Initialization ChromaDB

**File**: `utils/document_processor.py`

```python
class DocumentProcessor:
    def __init__(self, context_name: str = None, persist_directory: str = None):
        # ... setup ...

        self.client = None
        self.collection = None

        # NUOVO: eager initialization se directory esiste
        if os.path.exists(self.persist_directory):
            try:
                self.initialize_db()
                logger.info(f"ChromaDB initialized eagerly for context: {context_name}")
            except Exception as e:
                logger.warning(f"Eager init failed, will use lazy: {e}")
                # Fallback a lazy init
```

#### 2.2.4 Paginazione per get_all_documents

**File**: `utils/document_processor.py`

```python
def get_all_documents(
    self,
    page: int = 0,
    page_size: int = 100,
    return_total: bool = False
) -> Union[List[Dict], tuple]:
    """
    Restituisce documenti paginati

    Args:
        page: Numero pagina (0-indexed)
        page_size: Documenti per pagina
        return_total: Se True, ritorna anche totale documenti

    Returns:
        Lista documenti o (lista, totale) se return_total=True
    """
    if not self.collection:
        self.initialize_db()

    total_count = self.collection.count()

    if total_count == 0:
        return ([], 0) if return_total else []

    # Calcola offset
    offset = page * page_size
    if offset >= total_count:
        return ([], total_count) if return_total else []

    # Recupera pagina
    results = self.collection.get(
        limit=page_size,
        offset=offset
    )

    documents = []
    if results and 'documents' in results and 'metadatas' in results:
        for doc, metadata in zip(results['documents'], results['metadatas']):
            documents.append({
                'text': doc,
                'metadata': metadata
            })

    if return_total:
        return documents, total_count
    return documents
```

**Checklist Performance**:
- [ ] Implementare singleton embeddings
- [ ] Aggiungere LRU cache per query RAG
- [ ] Eager initialization ChromaDB
- [ ] Paginazione get_all_documents
- [ ] Benchmark before/after (pytest-benchmark)
- [ ] Load testing con 1000+ documenti

---

### 2.3 Configuration Optimization

**Priorità**: 🟢 MEDIA
**Effort**: 1 giorno
**Dependencies**: Nessuna

#### 2.3.1 Configurazione Centralizzata

**File**: `config.py` (NUOVO ROOT FILE)

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class RAGConfig:
    """Configurazione RAG e Document Processing"""
    DEFAULT_N_RESULTS: int = 3
    MAX_N_RESULTS: int = 10
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDINGS_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    QUERY_CACHE_SIZE: int = 100

@dataclass
class LLMConfig:
    """Configurazione LLM defaults"""
    DEFAULT_TEMPERATURE: float = 1.0
    DEFAULT_TOP_P_GEMINI: float = 0.95
    DEFAULT_TOP_P_OPENAI: float = 1.0
    DEFAULT_MAX_OUTPUT_TOKENS_GEMINI: int = 65536
    DEFAULT_MAX_TOKENS_OPENAI: int = 4096
    DEFAULT_REASONING_EFFORT: str = "medium"

@dataclass
class AuditorConfig:
    """Configurazione Auditor"""
    HISTORY_LIMIT: int = 8
    TEMPERATURE: float = 0.15
    MAX_TOKENS: int = 900
    TOP_P: float = 0.6

@dataclass
class SecurityConfig:
    """Configurazione sicurezza"""
    ALLOWED_URL_SCHEMES: list = ("http", "https")
    BLOCKED_HOSTS: list = ("localhost", "127.0.0.1", "169.254.169.254", "::1")
    RATE_LIMIT_CALLS_PER_MINUTE: int = 60

@dataclass
class SessionConfig:
    """Configurazione sessioni"""
    BASE_DIR: str = "./data/sessions"
    MAX_SESSIONS: int = 100
    SESSION_TIMEOUT_DAYS: int = 30

@dataclass
class AppConfig:
    """Configurazione completa applicazione"""
    rag: RAGConfig = RAGConfig()
    llm: LLMConfig = LLMConfig()
    auditor: AuditorConfig = AuditorConfig()
    security: SecurityConfig = SecurityConfig()
    session: SessionConfig = SessionConfig()

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/lumia.log"
    DEBUG_MODE: bool = False

# Singleton config
_config = None

def get_config() -> AppConfig:
    """Restituisce configurazione applicazione (singleton)"""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
```

**Usage Example**:
```python
from config import get_config

config = get_config()

# In document_processor.py
query_results = self.query(prompt, n_results=config.rag.DEFAULT_N_RESULTS)

# In auditor.py
self.review(..., temperature=config.auditor.TEMPERATURE)
```

**Checklist**:
- [ ] Creare `config.py`
- [ ] Refactorare tutti i magic numbers
- [ ] Update documentazione con config options

---

## 🟢 FASE 3: ARCHITECTURE REFACTORING (Settimane 6-9)

**Obiettivo**: Migliorare architettura e manutenibilità
**Priorità**: MEDIA
**Effort Totale**: 12-15 giorni lavorativi
**Score Atteso**: 8.3 → 8.7

### 3.1 Service Layer Implementation

**Priorità**: 🟢 MEDIA
**Effort**: 5-6 giorni
**Dependencies**: 2.1 (tests), 1.3 (schemas)

#### 3.1.1 Creare Service Classes

**Struttura**:
```bash
mkdir -p services
touch services/__init__.py
touch services/belief_service.py
touch services/desire_service.py
touch services/llm_service.py
```

**File**: `services/belief_service.py`

```python
from typing import List, Dict, Optional
import json
import logging
from utils.llm_manager import LLMManager
from utils.document_processor import DocumentProcessor
from utils.prompts import get_prompt
from utils.schemas import Belief, BeliefDesireCorrelation
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class BeliefService:
    """
    Service per gestione Beliefs

    Responsabilità:
    - Generazione beliefs da LLM
    - Validazione beliefs
    - Mix beliefs (desires + base beliefs)
    - Parsing e trasformazione JSON
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        doc_processor: DocumentProcessor
    ):
        self.llm = llm_manager
        self.doc = doc_processor

    def generate_mix_beliefs(
        self,
        desires: List[Dict],
        base_beliefs: List[Dict],
        provider: str,
        model: str,
        llm_params: Optional[Dict] = None
    ) -> List[Belief]:
        """
        Genera mix beliefs da desires e base beliefs

        Args:
            desires: Lista desires utente
            base_beliefs: Lista base beliefs dal contesto
            provider: LLM provider
            model: LLM model
            llm_params: Parametri LLM opzionali

        Returns:
            Lista Belief validati

        Raises:
            ValueError: Se generazione fallisce o JSON invalido
        """
        logger.info(f"Generating mix beliefs for {len(desires)} desires")

        try:
            # 1. Prepara context
            context = self._prepare_mix_beliefs_context(desires, base_beliefs)

            # 2. Carica prompt
            prompt_template = get_prompt('believer_mix_beliefs')
            prompt = prompt_template.format(context=context)

            # 3. Chiama LLM
            response = self.llm.chat(
                provider=provider,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                system_prompt=get_prompt('believer'),
                **(llm_params or {})
            )

            # 4. Parse JSON
            beliefs_json = self._extract_json_from_response(response)
            if not beliefs_json or 'beliefs' not in beliefs_json:
                raise ValueError("Invalid JSON structure in LLM response")

            # 5. Valida con Pydantic
            beliefs = []
            for belief_dict in beliefs_json['beliefs']:
                try:
                    belief = Belief(**belief_dict)
                    beliefs.append(belief)
                except ValidationError as e:
                    logger.warning(f"Skipping invalid belief: {e}")
                    continue

            logger.info(f"Successfully generated {len(beliefs)} valid beliefs")
            return beliefs

        except Exception as e:
            logger.error(f"Error generating mix beliefs: {e}", exc_info=True)
            raise

    def _prepare_mix_beliefs_context(
        self,
        desires: List[Dict],
        base_beliefs: List[Dict]
    ) -> str:
        """Prepara context per prompt mix beliefs"""
        # Formato desires
        desires_text = "DESIRES DELL'UTENTE:\n"
        for idx, desire in enumerate(desires, 1):
            desire_id = desire.get('desire_id', desire.get('id', f'D{idx}'))
            desc = desire.get('desire_statement', desire.get('description', 'N/A'))
            desires_text += f"  [{desire_id}] {desc}\n"

        # Formato base beliefs (sample)
        beliefs_text = "\nBASE BELIEFS (campione):\n"
        for belief in base_beliefs[:10]:  # Primi 10
            subj = belief.get('soggetto', 'N/A')
            rel = belief.get('relazione', 'N/A')
            obj = belief.get('oggetto', 'N/A')
            beliefs_text += f"  - {subj} {rel} {obj}\n"

        if len(base_beliefs) > 10:
            beliefs_text += f"  ... e altri {len(base_beliefs) - 10} beliefs\n"

        return desires_text + beliefs_text

    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Estrae JSON da risposta LLM"""
        import re

        # Try parse diretto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extract da code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try extract prima struttura JSON
        match = re.search(r"(\{.*\})", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        logger.error("Failed to extract JSON from LLM response")
        return None

    def validate_belief(self, belief: Dict) -> Optional[Belief]:
        """
        Valida un belief dict

        Returns:
            Belief validato o None se invalido
        """
        try:
            return Belief(**belief)
        except ValidationError as e:
            logger.warning(f"Belief validation failed: {e}")
            return None

    def filter_beliefs_by_relevance(
        self,
        beliefs: List[Belief],
        min_relevance: str = "MEDIO"
    ) -> List[Belief]:
        """
        Filtra beliefs per livello rilevanza minimo

        Args:
            beliefs: Lista beliefs
            min_relevance: Livello minimo (CRITICO, ALTO, MEDIO, BASSO)

        Returns:
            Lista beliefs filtrati
        """
        relevance_order = ["CRITICO", "ALTO", "MEDIO", "BASSO"]
        min_idx = relevance_order.index(min_relevance)

        filtered = []
        for belief in beliefs:
            for corr in belief.desires_correlati:
                if relevance_order.index(corr.livello_rilevanza) <= min_idx:
                    filtered.append(belief)
                    break

        logger.info(f"Filtered {len(filtered)}/{len(beliefs)} beliefs (>= {min_relevance})")
        return filtered
```

**Usage Example** (pages/3_Believer.py):
```python
# PRIMA: 75+ linee inline
# with st.spinner("Sto analizzando..."):
#     # Prepare context
#     # Call LLM
#     # Parse JSON
#     # Save to session

# DOPO: 5 linee
from services.belief_service import BeliefService

belief_service = BeliefService(
    llm_manager=st.session_state.llm_manager,
    doc_processor=st.session_state.doc_processor
)

beliefs = belief_service.generate_mix_beliefs(
    desires=st.session_state.loaded_desires,
    base_beliefs=base_beliefs,
    provider=provider,
    model=model,
    llm_params=llm_params
)

# Salva
st.session_state.session_manager.update_bdi_data(
    st.session_state.active_session,
    beliefs=[b.model_dump() for b in beliefs]
)
```

**Checklist Service Layer**:
- [ ] Creare `BeliefService`
- [ ] Creare `DesireService`
- [ ] Creare `LLMService` (wrapper con rate limiting)
- [ ] Refactorare pages per usare services
- [ ] Unit tests per ogni service (90% coverage)
- [ ] Integration tests workflow completi

---

### 3.2 Dependency Injection

**Priorità**: 🟢 MEDIA
**Effort**: 2-3 giorni
**Dependencies**: 3.1 (services)

#### 3.2.1 Setup DI Container

**Installare**: `dependency-injector`

```bash
pip install dependency-injector
echo "dependency-injector>=4.41.0" >> requirements.txt
```

**File**: `containers.py` (NUOVO ROOT FILE)

```python
from dependency_injector import containers, providers
from utils.llm_manager import LLMManager
from utils.session_manager import SessionManager
from utils.context_manager import ContextManager
from utils.document_processor import DocumentProcessor
from services.belief_service import BeliefService
from services.desire_service import DesireService
from config import get_config

class Container(containers.DeclarativeContainer):
    """DI Container per LUMIA Studio"""

    config = providers.Configuration()

    # Singletons
    llm_manager = providers.Singleton(LLMManager)

    session_manager = providers.Singleton(
        SessionManager,
        base_dir=config.session.BASE_DIR
    )

    context_manager = providers.Singleton(
        ContextManager,
        base_directory=config.context.BASE_DIR
    )

    # Factories (creano nuove istanze)
    document_processor = providers.Factory(
        DocumentProcessor,
        context_name=None  # Override in runtime
    )

    # Services
    belief_service = providers.Factory(
        BeliefService,
        llm_manager=llm_manager,
        doc_processor=document_processor
    )

    desire_service = providers.Factory(
        DesireService,
        llm_manager=llm_manager,
        doc_processor=document_processor
    )
```

**Usage** (app.py):
```python
import streamlit as st
from containers import Container
from config import get_config

# Initialize DI container
if 'container' not in st.session_state:
    container = Container()
    container.config.from_dict(get_config().__dict__)
    st.session_state.container = container

# Usage in pages
llm_manager = st.session_state.container.llm_manager()
session_manager = st.session_state.container.session_manager()
```

**Checklist DI**:
- [ ] Setup `dependency-injector`
- [ ] Creare `containers.py`
- [ ] Refactorare app.py per usare container
- [ ] Refactorare tutte le pages per DI
- [ ] Test container wiring

---

### 3.3 Code Cleanup & Refactoring

**Priorità**: 🟢 MEDIA
**Effort**: 4-5 giorni
**Dependencies**: 3.1 (services), 3.2 (DI)

#### 3.3.1 Ridurre LOC dei God Classes

**Target**:
- `0_Compass.py`: da 1070 → <500 LOC
- `3_Believer.py`: da 1100+ → <500 LOC
- `2_Ali.py`: da 778 → <400 LOC

**Strategy**: Estrarre funzioni helper in moduli separati

**File**: `pages/helpers/compass_helpers.py` (NUOVO)

```python
def render_session_selector(session_manager):
    """Helper per rendering session selector"""
    # 50+ linee estratte da Compass
    pass

def render_llm_config_form(providers, current_config):
    """Helper per form configurazione LLM"""
    # 80+ linee estratte
    pass

def render_belief_base_editor(session_id, session_manager):
    """Helper per editor belief base"""
    # 100+ linee estratte
    pass
```

#### 3.3.2 Eliminare Codice Duplicato

**Creare**: `utils/session_helpers.py`

```python
def load_active_session(session_manager):
    """
    Carica sessione attiva con fallback a ultima attiva

    Usato in: Ali, Believer, Cuma, Genius (4 duplicati)
    """
    import streamlit as st

    if 'active_session' not in st.session_state or not st.session_state.active_session:
        all_sessions = session_manager.get_all_sessions(status="active")
        if all_sessions:
            latest = max(all_sessions, key=lambda s: s['metadata'].get('last_accessed', ''))
            st.session_state.active_session = latest['session_id']
            return latest['session_id']
    return st.session_state.get('active_session')
```

#### 3.3.3 Standardizzare Naming

**Creare**: `STYLE_GUIDE.md`

```markdown
# LUMIA Studio Style Guide

## Naming Conventions

### Language
- **Code**: English (variables, functions, classes)
- **UI**: Italian (user-facing strings)
- **Comments**: Italian (inline comments)
- **Docstrings**: English (API documentation)

### Variables
- `snake_case` for variables and functions
- `PascalCase` for classes
- `UPPER_CASE` for constants

### Acronyms
- BDI → maintain case: `bdi_data` (not `BDIData`)
- LLM → maintain case: `llm_manager`
- RAG → maintain case: `rag_config`

## Code Organization
- Max line length: 100 characters
- Max function length: 50 lines
- Max file length: 400 lines
```

**Checklist Cleanup**:
- [ ] Estrarre helpers da Compass
- [ ] Estrarre helpers da Believer
- [ ] Estrarre helpers da Ali
- [ ] Consolidare codice duplicato
- [ ] Standardizzare naming (run rename script)
- [ ] Lint con pylint/black
- [ ] Target: riduzione 30% LOC totale

---

## 🌟 FASE 4: SCALABILITY & POLISH (Settimane 10-12)

**Obiettivo**: Production-ready deployment
**Priorità**: BASSA
**Effort Totale**: 8-10 giorni lavorativi
**Score Atteso**: 8.7 → 9.0+

### 4.1 CI/CD Pipeline

**Priorità**: 🟢 MEDIA
**Effort**: 1-2 giorni
**Dependencies**: 2.1 (tests)

#### 4.1.1 GitHub Actions Workflow

**File**: `.github/workflows/ci.yml` (NUOVO)

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pylint black isort mypy
          pip install -r requirements.txt
      - name: Lint with pylint
        run: pylint utils/ services/ --fail-under=8.0
      - name: Check formatting
        run: black --check utils/ services/ pages/
      - name: Check imports
        run: isort --check-only utils/ services/ pages/
      - name: Type check
        run: mypy utils/ services/ --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov pytest-mock
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=utils --cov=services --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r utils/ services/ pages/ -f json -o bandit-report.json
      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
```

#### 4.1.2 Pre-commit Hooks

**File**: `.pre-commit-config.yaml` (NUOVO)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.0
    hooks:
      - id: pylint
        args: ['--fail-under=8.0']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Setup**:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Test
```

---

### 4.2 Monitoring & Observability

**Priorità**: 🟢 MEDIA
**Effort**: 2-3 giorni
**Dependencies**: 1.1 (logging)

#### 4.2.1 Metrics Collection

**File**: `utils/metrics.py` (NUOVO)

```python
import time
from functools import wraps
from typing import Callable
import logging
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Metrics:
    """Collector per metriche applicazione"""
    llm_calls: int = 0
    llm_errors: int = 0
    llm_total_time: float = 0.0
    rag_queries: int = 0
    rag_total_time: float = 0.0
    sessions_created: int = 0
    beliefs_generated: int = 0
    desires_identified: int = 0

    call_times: dict = field(default_factory=lambda: defaultdict(list))

    def record_llm_call(self, duration: float, success: bool = True):
        """Registra chiamata LLM"""
        self.llm_calls += 1
        self.llm_total_time += duration
        if not success:
            self.llm_errors += 1
        self.call_times['llm'].append(duration)

    def record_rag_query(self, duration: float):
        """Registra query RAG"""
        self.rag_queries += 1
        self.rag_total_time += duration
        self.call_times['rag'].append(duration)

    def get_stats(self) -> dict:
        """Restituisce statistiche"""
        return {
            'llm': {
                'calls': self.llm_calls,
                'errors': self.llm_errors,
                'avg_time': self.llm_total_time / self.llm_calls if self.llm_calls > 0 else 0,
                'error_rate': self.llm_errors / self.llm_calls if self.llm_calls > 0 else 0
            },
            'rag': {
                'queries': self.rag_queries,
                'avg_time': self.rag_total_time / self.rag_queries if self.rag_queries > 0 else 0
            },
            'sessions': self.sessions_created,
            'beliefs': self.beliefs_generated,
            'desires': self.desires_identified
        }

# Singleton metrics
_metrics = Metrics()

def get_metrics() -> Metrics:
    """Restituisce istanza metrics singleton"""
    return _metrics

def timer(metric_name: str):
    """Decorator per timing automatico"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.debug(f"{metric_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"{metric_name} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator
```

**Usage**:
```python
from utils.metrics import get_metrics, timer

@timer("llm_call")
def chat(self, ...):
    start = time.time()
    try:
        response = self.llm.chat(...)
        get_metrics().record_llm_call(time.time() - start, success=True)
        return response
    except Exception as e:
        get_metrics().record_llm_call(time.time() - start, success=False)
        raise
```

#### 4.2.2 Metrics Dashboard

**File**: `pages/7_Metrics.py` (NUOVO)

```python
import streamlit as st
from utils.metrics import get_metrics
import plotly.graph_objects as go

st.set_page_config(page_title="Metrics - LumIA Studio", page_icon="📊")

st.title("📊 Metrics Dashboard")

metrics = get_metrics()
stats = metrics.get_stats()

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("LLM Calls", stats['llm']['calls'])
    st.caption(f"Avg: {stats['llm']['avg_time']:.2f}s")

with col2:
    st.metric("RAG Queries", stats['rag']['queries'])
    st.caption(f"Avg: {stats['rag']['avg_time']:.2f}s")

with col3:
    st.metric("Sessions Created", stats['sessions'])

with col4:
    st.metric("LLM Error Rate", f"{stats['llm']['error_rate']*100:.1f}%")

# Charts
st.subheader("LLM Call Times Distribution")
if metrics.call_times['llm']:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=metrics.call_times['llm'], nbinsx=20))
    fig.update_layout(xaxis_title="Time (seconds)", yaxis_title="Count")
    st.plotly_chart(fig)
```

---

### 4.3 Documentation & Polish

**Priorità**: 🟢 BASSA
**Effort**: 3-4 giorni
**Dependencies**: Tutte le fasi precedenti

#### 4.3.1 API Documentation con Sphinx

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
mkdir docs/api
cd docs/api
sphinx-quickstart
```

**File**: `docs/api/conf.py`

```python
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints'
]

html_theme = 'sphinx_rtd_theme'
```

**Build**:
```bash
cd docs/api
make html
open _build/html/index.html
```

#### 4.3.2 Architecture Decision Records

**File**: `docs/ADRs/001-remove-claude-support.md`

```markdown
# ADR 001: Rimozione supporto Claude

## Stato
Accettata (10 Novembre 2025)

## Contesto
LUMIA Studio supportava 3 provider LLM: Gemini, Claude, OpenAI.
Mantenere 3 provider aumentava complessità testing e gestione.

## Decisione
Rimosso supporto Anthropic Claude.

## Motivazioni
- Riduzione complessità codebase (~25 linee rimosse)
- Focus su 2 provider stabili
- Costi: Claude più costoso per use case LUMIA
- Claude API cambia frequentemente

## Conseguenze
**Pro**:
- Codebase più semplice
- Meno dipendenze (anthropic package rimosso)
- Testing più veloce

**Contro**:
- Meno opzioni per utenti
- Claude Sonnet 4 ha performance eccellenti (perdiamo qualità)

## Alternative Considerate
1. Mantenere solo Gemini (rejected: troppo vendor lock-in)
2. Mantenere solo OpenAI (rejected: costi alti)
3. Mantenere tutti e 3 (rejected: complessità)
```

#### 4.3.3 Contribution Guidelines

**File**: `CONTRIBUTING.md` (NUOVO)

```markdown
# Contributing to LUMIA Studio

## Setup Development Environment

1. Fork repository
2. Clone your fork
3. Create virtual environment
4. Install dependencies including dev tools:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Write tests (required: 80%+ coverage)
4. Run tests: `pytest tests/ --cov`
5. Lint code: `pylint utils/ services/`
6. Format code: `black utils/ services/ pages/`
7. Commit with conventional commits: `feat: add new feature`
8. Push and create PR

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Max line length: 100
- Use English for code, Italian for UI

## Testing

- Unit tests required for new functions
- Integration tests for new workflows
- Minimum 80% coverage

## Pull Request Process

1. Update README if needed
2. Add entry to CHANGELOG.md
3. Ensure all tests pass
4. Request review from maintainers
5. Address feedback
```

---

## 📊 TRACKING & METRICHE

### Progress Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: SECURITY & STABILITY                               │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20%         │
│  - Logging: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%           │
│  - Security Fixes: ░░░░░░░░░░░░░░░░░░░░░░░░░  0%           │
│  - Input Validation: ░░░░░░░░░░░░░░░░░░░░░░░  0%           │
├─────────────────────────────────────────────────────────────┤
│  FASE 2: QUALITY FOUNDATIONS                                │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%          │
├─────────────────────────────────────────────────────────────┤
│  FASE 3: ARCHITECTURE REFACTORING                           │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%          │
├─────────────────────────────────────────────────────────────┤
│  FASE 4: SCALABILITY & POLISH                               │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%          │
└─────────────────────────────────────────────────────────────┘

Overall Progress: 0/100 tasks completed (0%)
Estimated Time Remaining: 8-12 settimane
Current Quality Score: 7.2/10
Target Score: 9.0/10
```

### Metrics Obiettivo

| Metrica | Attuale | Target | Status |
|---------|---------|--------|--------|
| Test Coverage | 0% | 80%+ | 🔴 |
| Code Quality (Pylint) | N/A | 8.5/10 | 🔴 |
| Vulnerabilità | 3 critiche | 0 | 🔴 |
| LOC per file (avg) | 650 | <400 | 🔴 |
| Performance (startup) | 3-5s | <2s | 🟡 |
| Documentation Coverage | 70% | 90% | 🟡 |

---

## 🎯 CHECKLIST FINALE

### Pre-Production Checklist

- [ ] **Security**
  - [ ] Path traversal fixed
  - [ ] SSRF fixed
  - [ ] Input validation implemented
  - [ ] API keys validated
  - [ ] Rate limiting active

- [ ] **Quality**
  - [ ] Test coverage >80%
  - [ ] Pylint score >8.5
  - [ ] All critical issues resolved
  - [ ] No TODO/FIXME in production code

- [ ] **Performance**
  - [ ] Embeddings singleton
  - [ ] RAG cache active
  - [ ] Startup time <2s
  - [ ] Memory usage optimized

- [ ] **Documentation**
  - [ ] README updated
  - [ ] API docs generated
  - [ ] ADRs for major decisions
  - [ ] CONTRIBUTING.md created

- [ ] **DevOps**
  - [ ] CI/CD pipeline working
  - [ ] Pre-commit hooks active
  - [ ] Monitoring dashboard
  - [ ] Logging properly configured

---

## 📞 SUPPORT & QUESTIONS

Per domande su questa roadmap:
- **Technical Lead**: [Your Name]
- **Email**: [email]
- **Slack**: #lumia-studio-dev

**Meeting Schedule**:
- Sprint Planning: Lunedì 9:00
- Daily Standup: 9:30 (async su Slack)
- Sprint Review: Venerdì 16:00
- Retrospective: Venerdì 17:00

---

**Document Version**: 1.0
**Last Updated**: 10 Novembre 2025
**Next Review**: Inizio di ogni Fase

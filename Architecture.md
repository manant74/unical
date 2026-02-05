# LUMIA Studio - Architettura della Soluzione

## Indice

1. [Panoramica Generale](#panoramica-generale)
2. [Architettura a Livelli](#architettura-a-livelli)
3. [Layer Frontend](#layer-frontend)
4. [Layer Backend](#layer-backend)
5. [Layer Database e Vector Store](#layer-database-e-vector-store)
6. [Sistema RAG (Retrieval Augmented Generation)](#sistema-rag-retrieval-augmented-generation)
7. [Integrazione LLM](#integrazione-llm)
8. [Sistema Agenti BDI](#sistema-agenti-bdi)
9. [Flussi di Lavoro Principali](#flussi-di-lavoro-principali)
10. [Stack Tecnologico Completo](#stack-tecnologico-completo)

---

## Panoramica Generale

**LUMIA Studio** (Learning Unified Model for Intelligent Agents) è una piattaforma avanzata di knowledge engineering basata su AI che trasforma conoscenza non strutturata in insights strategici strutturati attraverso agenti conversazionali intelligenti.

### Framework Architetturale: BDI (Belief-Desire-Intention)

Il sistema implementa il framework cognitivo BDI, tipico dell'AI simbolica:

- **Beliefs (Credenze)**: Fatti estratti dalla knowledge base aziendale
- **Desires (Desideri)**: Obiettivi strategici degli utenti/stakeholder
- **Intentions (Intenzioni)**: Piani d'azione derivati dall'analisi BDI

### Struttura del Progetto

```text
unical/
├── app.py                          # Entry point principale (Homepage, 549 righe)
├── pages/                          # Applicazione multi-pagina Streamlit
│   ├── 0_Compass.py               # Gestione sessioni & visualizzazione BDI (2,392 righe)
│   ├── 1_Knol.py                  # Builder knowledge base (778 righe)
│   ├── 2_Ali.py                   # Agente estrazione desires (906 righe)
│   ├── 3_Believer.py              # Agente estrazione beliefs (1,374 righe)
│   ├── 4_Cuma.py                  # Pianificazione intenzioni (577 righe, WIP)
│   └── 6_Genius.py                # Execution coach BDI (778 righe, ACTIVE)
├── utils/                          # Core business logic
│   ├── llm_manager.py             # Orchestrazione LLM multi-provider (188 righe)
│   ├── llm_manager_config.py      # Configurazione parametri per modello (204 righe)
│   ├── document_processor.py      # RAG & processamento documenti (263 righe)
│   ├── session_manager.py         # Gestione lifecycle sessioni (311 righe)
│   ├── context_manager.py         # Gestione multi-context KB (304 righe)
│   ├── auditor.py                 # Quality assurance conversazioni (392 righe)
│   ├── genius_engine.py           # Engine generazione piani Genius (1,239 righe)
│   ├── prompts.py                 # Caricamento system prompt (121 righe)
│   └── ui_messages.py             # Messaggi UI castuali (91 righe)
├── prompts/                        # System prompt agenti (14 file Markdown)
│   ├── ali_system_prompt.md
│   ├── believer_system_prompt.md
│   ├── believer_from_scratch_prompt.md
│   ├── believer_mix_beliefs_prompt.md
│   ├── belief_base_prompt.md
│   ├── cuma_system_prompt.md
│   ├── auditor_system_prompt.md
│   ├── desires_auditor_system_prompt.md
│   ├── belief_auditor_system_prompt.md
│   ├── genius_system_prompt.md
│   ├── genius_discovery_prompt.md
│   ├── genius_plan_generation_prompt.md
│   ├── genius_step_tips_prompt.md
│   └── genius_coach_template.md
├── data/                           # Storage persistente (filesystem-based)
│   ├── bdi_frameworks/            # BDI frameworks esportati e riutilizzabili
│   ├── genius_plans/              # Piani d'azione generati da Genius
│   ├── contexts/                  # Knowledge bases isolate
│   └── sessions/                  # Sessioni di lavoro
├── docs/                           # Documentazione tecnica
├── lib/                            # Librerie JavaScript frontend
│   ├── tom-select/                # Componente select dropdown
│   └── vis-9.1.2/                 # Visualizzazioni network
├── requirements.txt                # Dipendenze Python
├── .env.example                    # Template variabili ambiente
└── setup_models.py                 # Script di setup modelli
```

**Statistiche codice:**
- **Python totale**: 10,468 righe
- **Pagine applicazione**: 6 moduli
- **Moduli utility**: 9 file
- **System prompt**: 14 file Markdown
- **Provider LLM supportati**: 2 (Google Gemini, OpenAI)
- **Modelli supportati**: 12+ tra i due provider

---

## Architettura a Livelli

```text
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Streamlit Multi-Page Application                   │   │
│   │  • app.py (Homepage)                                │   │
│   │  • Compass (Session Management & Analytics)         │   │
│   │  • Knol (Knowledge Base Builder)                    │   │
│   │  • Alì (Desires Extraction Agent)                   │   │
│   │  • Believer (Beliefs Extraction Agent)              │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Core Services (utils/)                             │   │
│   │  • SessionManager: CRUD sessioni + stato attivo     │   │
│   │  • ContextManager: Gestione multi-KB + ChromaDB     │   │
│   │  • LLMManager: Interfaccia unificata multi-provider │   │
│   │  • DocumentProcessor: RAG pipeline + chunking       │   │
│   │  • ConversationAuditor: QA agenti + validazione     │   │
│   │  • PromptsLoader: Caricamento prompt da Markdown    │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   DATA ACCESS LAYER                         │
│   ┌──────────────────┐    ┌──────────────────────────────┐  │
│   │  JSON Storage    │    │  ChromaDB Vector Store       │  │
│   │  • Sessions      │    │  • Document embeddings       │  │
│   │  • Contexts      │    │  • Semantic search           │  │
│   │  • BDI Data      │    │  • Context-isolated          │  │
│   │  • Metadata      │    │  • HNSW indexing             │  │
│   └──────────────────┘    └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Frontend

### Framework: **Streamlit 1.31.0+**

Streamlit è stato scelto per la sua capacità di creare rapidamente interfacce web interattive con Python puro, ideale per applicazioni AI/ML.

#### Architettura Multi-Page Application (MPA)

Ogni pagina rappresenta un modulo funzionale indipendente:

| Pagina | File | Righe | Status | Funzione |
|--------|------|-------|--------|----------|
| **Homepage** | `app.py` | 549 | Active | Landing page con descrizione del sistema |
| **Compass** | `pages/0_Compass.py` | 2,392 | Active | Gestione sessioni, visualizzazione BDI, analytics |
| **Knol** | `pages/1_Knol.py` | 778 | Active | Creazione/gestione knowledge bases |
| **Alì** | `pages/2_Ali.py` | 906 | Active | Interfaccia agente estrazione desires |
| **Believer** | `pages/3_Believer.py` | 1,374 | Active | Interfaccia agente estrazione beliefs |
| **Cuma** | `pages/4_Cuma.py` | 577 | WIP | Pianificazione intenzioni |
| **Genius** | `pages/6_Genius.py` | 778 | Active (MVP) | Execution coach: genera piani d'azione da BDI |

#### Componenti UI Avanzati

##### 1. Theming Personalizzato

- Gradiente animato personalizzato
- Toggle dark/light mode
- CSS custom injection per nascondere elementi Streamlit nativi

##### 2. Visualizzazioni Interattive**

- **Plotly**: Grafici a barre interattivi per analisi desires/beliefs
- **NetworkX**: Grafi di correlazione desires-beliefs
- **Pandas DataFrames**: Tabelle interattive con sorting/filtering

##### 3. Editing Avanzato**

- **streamlit-code-editor**: Editor JSON con syntax highlighting
- **Modal dialogs**: Editing in-app dei dati BDI
- **Validazione real-time**: Controllo JSON syntax

##### 4. Navigation Flow**

- **Session Badges**: Indicatori visivi dello stato sessione (Active, Draft, Archived)
- **Quick Access**: Pulsanti di navigazione tra Compass → Alì → Believer
- **Contextual Greetings**: Saluti personalizzati basati su KB description

#### Tecnologie Frontend

```python
# Principali librerie UI
streamlit >= 1.31.0              # Framework web
streamlit-code-editor            # JSON/code editor
plotly >= 5.18.0                 # Grafici interattivi
pandas >= 2.0.0                  # Data manipulation
```

---

## Layer Backend

### Core: **Python 3.9+**

Tutto il business logic è scritto in Python, con architettura modulare basata su classi manager.

### Moduli Principali (utils/)

#### 1. **SessionManager** (`utils/session_manager.py`)

Gestisce il lifecycle completo delle sessioni di lavoro.

**Responsabilità:**

- Creazione/lettura/aggiornamento/eliminazione sessioni
- Gestione stato attivo (una sessione attiva per volta)
- Persistenza metadati e configurazione LLM
- Auto-save dati BDI (desires, beliefs, intentions)

**Struttura Dati Sessione:**

```json
{
  "metadata": {
    "session_id": "uuid-generato",
    "name": "Nome Sessione",
    "description": "Descrizione progetto",
    "tags": ["tag1", "tag2"],
    "created_at": "2025-11-25T10:30:00",
    "last_accessed": "2025-11-25T12:45:00",
    "status": "active"  // active|draft|archived
  },
  "config": {
    "context": "nome_context_normalizzato",
    "llm_provider": "Gemini",
    "llm_model": "gemini-2.5-flash",
    "llm_settings": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 0.9
    }
  }
}
```

**Metodi Chiave:**

```python
create_session(name, description, tags, context, llm_config)
list_sessions()
get_session(session_id)
update_session(session_id, updates)
delete_session(session_id)
set_active_session(session_id)
get_active_session()
```

#### 2. **ContextManager** (`utils/context_manager.py`)

Gestisce knowledge bases multiple e isolate.

**Responsabilità:**

- CRUD per contexts (knowledge bases)
- Integrazione ChromaDB per ogni context
- Gestione belief base estratta da LLM
- Lazy initialization dei database

**Struttura Directory Context:**

```text
data/contexts/{context_name}/
├── chroma_db/                  # ChromaDB files
│   ├── {collection_id}/        # HNSW index
│   └── chroma.sqlite3          # Metadata DB
├── context_metadata.json       # Info context
└── belief_base.json           # Beliefs estratte da KB
```

**Metodi Chiave:**

```python
create_context(name, description, domain)
list_contexts()
get_context(context_name)
get_chroma_client(context_name)  # Lazy init
release_chroma_client(context_name)
save_belief_base(context_name, beliefs)
```

#### 3. **LLMManager** (`utils/llm_manager.py`)

Interfaccia unificata per multiple provider LLM.

**Architettura:**

```python
class LLMManager:
    def __init__(self):
        self._initialize_clients()  # Auto-detect API keys

    def chat(self, provider, model, messages, settings):
        # Routing verso provider specifico
        if provider == "Gemini":
            return self._chat_gemini(...)
        elif provider == "OpenAI":
            return self._chat_openai(...)
```

**Provider Supportati:**

- **Google Gemini**: Via `google-generativeai` SDK
- **OpenAI**: Via OpenAI Python SDK ufficiale

**Gestione Errori:**

- Try-except per ogni provider
- Fallback messages in caso di errore API
- Logging dettagliato

#### 4. **DocumentProcessor** (`utils/document_processor.py`)

Pipeline completa RAG per ingestione documenti.

**Formati Supportati:**

- PDF (via PyPDF2)
- URLs (web scraping con BeautifulSoup4)
- File di testo (.txt)
- Markdown (.md)

**Pipeline di Processamento:**

```python
1. load_document(source, type)
   ↓
2. chunk_text(text)  # RecursiveCharacterTextSplitter
   ↓
3. generate_embeddings(chunks)  # sentence-transformers
   ↓
4. store_in_chromadb(embeddings, metadata)
   ↓
5. extract_belief_base(context)  # LLM analysis
```

**Configurazione Chunking:**

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Caratteri per chunk
    chunk_overlap=200,      # Overlap tra chunk adiacenti
    length_function=len,
    is_separator_regex=False
)
```

#### 5. **GeniusEngine** (`utils/genius_engine.py` — 1,239 righe)

Engine di business logic per l'agente Genius. Gestisce il ciclo completo dalla selezione del BDI alla generazione e persistenza dei piani d'azione.

**Responsabilità:**

- Caricamento e validazione dei BDI framework da `data/bdi_frameworks/`
- Filtro beliefs per rilevanza (CRITICO/ALTO) relativa a un desire target
- Creazione del profilo utente (ruolo, timeline, vincoli)
- Generazione struttura piano tramite LLM con prompt dedicato
- Persistenza piani in `data/genius_plans/` e tracking dello stato attivo
- Aggiornamento progressivo degli step (pending → in_progress → completed)

**Metodi principali:**

```python
class GeniusEngine:
    # Caricamento BDI
    load_bdi_frameworks() -> List[Dict]
    load_bdi(filename: str) -> Optional[Dict]

    # Belief filtering
    filter_beliefs(bdi_data, desire_id, min_relevance_level="ALTO") -> List[Dict]

    # Generazione piano
    generate_plan_structure(llm_manager, bdi_data, desire_id, user_profile) -> Dict
    create_full_plan(plan_structure, bdi_data, desire_id, user_profile, bdi_source) -> Dict

    # Persistenza
    save_plan(plan, session_id=None) -> str
    load_plan(plan_id, session_id=None) -> Optional[Dict]
    get_active_plan(session_id=None) -> Optional[Dict]
    list_plans(session_id=None) -> List[Dict]
    update_plan_progress(plan_id, step_id, new_status, user_notes="") -> bool
```

**Struttura piano generato:**

```json
{
  "plan_id": "abc123",
  "bdi_source": "perizia_immobiliare_bdi.json",
  "target_desire": { "desire_id": "D2", "desire_statement": "...", "success_metrics": [] },
  "user_profile": { "role": "Product Manager", "timeline_weeks": 12, "constraints": ["small_team"] },
  "plan_structure": {
    "phases": [
      {
        "phase_id": "P1",
        "phase_name": "Research & Analysis",
        "duration_weeks": 2,
        "status": "pending",
        "steps": [
          {
            "step_id": "S1.1",
            "description": "...",
            "tasks": ["Task 1", "Task 2"],
            "supporting_beliefs": [{ "subject": "...", "relevance_level": "CRITICO" }],
            "verification_criteria": ["..."],
            "estimated_effort_days": 3,
            "status": "pending"
          }
        ]
      }
    ]
  },
  "overall_progress": { "total_steps": 12, "completed_steps": 0, "percentage_complete": 0.0 }
}
```

#### 6. **UI Messages** (`utils/ui_messages.py`)

Modulo utility per messaggi di attesa variabili e contestuali.

**Responsabilità:**

- Gestione lista di messaggi sulla gestione della conoscenza e riferimenti fantascientifici
- Selezione casuale per spinner e indicatori di caricamento
- Tono professionale e creativo durante l'elaborazione

**Utilizzo:**

```python
from utils.ui_messages import get_random_thinking_message

with st.spinner(get_random_thinking_message()):
    # Elaborazione LLM o RAG
    pass
```

**Lista Messaggi (86 totali):**

- Messaggi originali sulla gestione della conoscenza
- Riferimenti fantascientifici: Borges, Asimov, Star Trek, Blade Runner, Star Wars, 2001: A Space Odyssey, Dune, Hitchhiker's Guide, Doctor Who, Neuromancer e altri

#### 6. **ConversationAuditor** (`utils/auditor.py`)

Sistema di quality assurance avanzato con auditor specializzati e valutazione rubric-based.

**Architettura Auditor (v2.7 - Gennaio 2026):**

- **Auditor Separati**: Due auditor dedicati per validazione specifica
  - **Desires Auditor**: Validazione per agente Alì (`prompts/desires_auditor_system_prompt.md`)
  - **Beliefs Auditor**: Validazione per agente Believer (`prompts/belief_auditor_system_prompt.md`)

**Sistema Rubric-Based:**

**Desires Auditor - Criteri di Valutazione (0-10):**
1. **Persona Inference**: Segnali raccolti, inferenza logica, categoria chiara
2. **Desire Structure**: Statement chiaro, azionabile, specifico
3. **Completeness**: Campi presenti, priorità assegnata, contesto fornito
4. **Semantic Coherence**: Desires correlati, no contraddizioni, allineamento dominio

**Beliefs Auditor - Criteri di Valutazione (0-10):**
1. **Belief Structure**: Formato subject-relation-object, definition completa (WHAT/WHY/HOW), semantic relations
2. **Source Citation**: Fonte esatta, riferimento verificabile, pagina/sezione specificata
3. **Desire Correlation**: Desires rilevanti identificati, livello rilevanza appropriato, spiegazione chiara
4. **Semantic Richness**: Prerequisites, related concepts, enables/part_of/sub_concepts

**Output Auditor (Enhanced):**

```json
{
  "issues": ["Issue 1: Desire D3 manca success metrics quantitativi"],
  "improvements": ["Considera aggiungere time-bound targets a D2"],
  "quick_replies": ["Aggiungiamo altri desires?", "Procediamo con beliefs?"],
  "rubric_scores": {
    "persona_inference": 9.0,
    "desire_structure": 8.5,
    "completeness": 8.0,
    "semantic_coherence": 9.5
  },
  "overall_score": 8.75,
  "is_finalization_request": false
}
```

**Parametri LLM Auditor:**

- Temperature: **0.15** (molto bassa per consistenza e riproducibilità)
- Max tokens: 1500
- Top P: 0.9
- Provider: Stesso della sessione attiva

**Benefici Sistema Rubric:**
- Validazione oggettiva con metriche quantitative
- Feedback strutturato e azionabile
- Tracciabilità della qualità nel tempo
- Separazione concerns (desires vs beliefs validation)

---

## Layer Database e Vector Store

### Vector Database: **ChromaDB 0.4.22+**

ChromaDB è un database vettoriale open-source ottimizzato per semantic search e RAG.

#### Caratteristiche Tecniche

##### 1. Architettura di Storage

- **Tipo**: Persistent client (storage locale su filesystem)
- **Indice**: HNSW (Hierarchical Navigable Small World) per ricerca approssimata veloce
- **Distanza**: Cosine similarity (default)
- **Backend**: SQLite per metadata + binari per vettori

##### 2. Isolamento per Context**

Ogni knowledge base ha la propria collection ChromaDB:

```python
# Creazione collection
collection = client.get_or_create_collection(
    name=f"context_{context_name}",
    metadata={"hnsw:space": "cosine"}
)

# Query semantica
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,  # Top-5 chunk più rilevanti
    include=["documents", "metadatas", "distances"]
)
```

##### 3. Metadata Tracking**

Ogni chunk memorizzato include:

```json
{
  "source": "nome_file.pdf",
  "chunk_id": "uuid-chunk",
  "context_name": "corso_inglese",
  "page": 5,  // se PDF
  "timestamp": "2025-11-25T10:30:00"
}
```

#### Modello di Embedding: **sentence-transformers**

**Modello Specifico:**

```python
"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

**Caratteristiche:**

- **Dimensionalità**: 384
- **Multilingue**: Ottimizzato per lingue europee (italiano, inglese, etc.)
- **Velocità**: Bilanciamento tra performance e qualità
- **Provider**: HuggingFace

**Vantaggi:**

- Semantic search efficace in italiano
- Dimensionalità contenuta (storage efficiente)
- Modello compatto (inferenza veloce)

### Storage JSON: Filesystem-Based

**Vantaggi Architetturali:**

- **Portabilità**: Facile backup/export
- **Nessuna dipendenza DB**: Zero overhead configurazione
- **Human-readable**: Facilità debug e ispezione
- **Version control**: Possibilità di tracciare cambiamenti

**Struttura Directory:**

```text
data/
├── contexts/
│   ├── corso_inglese/
│   │   ├── chroma_db/
│   │   ├── context_metadata.json
│   │   └── belief_base.json
│   └── lumi_agents/
│       └── ...
└── sessions/
    ├── {session-uuid-1}/
    │   ├── metadata.json
    │   ├── config.json
    │   └── current_bdi.json
    └── {session-uuid-2}/
        └── ...
```

---

## Sistema RAG (Retrieval Augmented Generation)

### Definizione

RAG combina la potenza generativa degli LLM con informazioni contestuali recuperate da una knowledge base, riducendo allucinazioni e aumentando la rilevanza delle risposte.

### Architettura RAG in LUMIA

```text
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                             │
└─────────────────────────────────────────────────────────────┘

1. DOCUMENT INGESTION
   User Upload → DocumentProcessor
   ├── PDF Parsing (PyPDF2)
   ├── Web Scraping (BeautifulSoup4 + requests)
   ├── Text/Markdown Reading
   └── Text Cleaning

2. TEXT CHUNKING
   Full Text → RecursiveCharacterTextSplitter
   ├── chunk_size: 1000 chars
   ├── chunk_overlap: 200 chars
   └── Preserve semantic coherence

3. EMBEDDING GENERATION
   Text Chunks → sentence-transformers
   ├── Model: paraphrase-multilingual-MiniLM-L12-v2
   ├── Output: 384-dim vectors
   └── Batch processing

4. VECTOR STORAGE
   Embeddings → ChromaDB
   ├── Collection per context
   ├── HNSW indexing
   └── Metadata attachment

5. QUERY PROCESSING
   User Question → Embedding → ChromaDB.query()
   ├── Top-K retrieval (K=5)
   ├── Cosine similarity ranking
   └── Distance threshold filtering

6. CONTEXT AUGMENTATION
   Retrieved Chunks → Prompt Enhancement
   ├── Format: "Contesto: {chunks}\nDomanda: {question}"
   ├── Inject into system/user message
   └── Send to LLM

7. LLM GENERATION
   Augmented Prompt → LLM
   ├── Provider: Gemini/OpenAI
   ├── Model-specific parameters
   └── Response generation
```

### Componenti RAG Dettagliati

#### 1. Document Ingestion

**Supporto Multi-Formato:**

```python
# PDF
def process_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# URL (Web Scraping)
def process_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Remove scripts, styles
    for tag in soup(['script', 'style']):
        tag.decompose()
    return soup.get_text()

# Text/Markdown
def process_text(file):
    return file.read().decode('utf-8')
```

#### 2. Semantic Chunking

**Strategia RecursiveCharacterTextSplitter:**

Divide il testo in chunk semanticamente coerenti usando separatori gerarchici:

1. Paragrafi (`\n\n`)
2. Frasi (`.`, `!`, `?`)
3. Parole (` `)

**Configurazione:**

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False
)

chunks = splitter.split_text(document_text)
```

**Rationale:**

- 1000 chars: Bilanciamento contesto/granularità
- 200 overlap: Preserva continuità semantica ai bordi

#### 3. Embedding & Indexing

**Modello Embedding:**

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Genera embedding
vectors = embeddings.embed_documents(chunks)
```

**Inserimento in ChromaDB:**

```python
collection.add(
    documents=chunks,
    embeddings=vectors,
    metadatas=[{"source": filename, "chunk_id": i} for i in range(len(chunks))],
    ids=[f"{context_name}_{i}" for i in range(len(chunks))]
)
```

#### 4. Retrieval Semantico

**Query Processing:**

```python
def retrieve_context(query, context_name, top_k=5):
    # Get ChromaDB client
    client = context_manager.get_chroma_client(context_name)
    collection = client.get_collection(f"context_{context_name}")

    # Embed query
    query_vector = embeddings.embed_query(query)

    # Semantic search
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    context_chunks = results['documents'][0]
    return "\n\n".join(context_chunks)
```

#### 5. Prompt Augmentation

**Integrazione nei Prompt Agenti:**

**Esempio Alì (Desires):**

```python
context_chunks = retrieve_context(user_message, session_context)

augmented_message = f"""
CONTESTO DALLA KNOWLEDGE BASE:
{context_chunks}

---

DOMANDA UTENTE:
{user_message}

Usa il contesto sopra per rispondere in modo pertinente.
"""

# Invia a LLM
response = llm_manager.chat(
    provider="Gemini",
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": augmented_message}
    ]
)
```

**Esempio Believer (Beliefs):**

```python
# Retrieval più specifico per credenze
belief_context = retrieve_context(
    f"Fatti rilevanti per: {desire_statement}",
    session_context,
    top_k=10  # Più chunk per beliefs
)

# Inietta nel prompt per estrazione atomica
```

### Belief Base Extraction

**Processo Automatizzato:**

Oltre al RAG real-time, il sistema estrae una belief base statica dalla KB:

```python
def extract_belief_base(context_name):
    # Carica tutti i documenti del context
    documents = load_all_context_documents(context_name)

    # Prompt LLM per estrazione strutturata
    prompt = f"""
    Analizza il seguente testo e estrai tutti i fatti rilevanti
    nella struttura Belief con grafo di conoscenza.

    TESTO:
    {documents}

    OUTPUT (JSON):
    [
      {{
        "subject": "...",
        "definition": "Descrizione completa (COSA, PERCHÉ, COME)",
        "semantic_relations": [
          {{"relation": "...", "object": "...", "description": "..."}}
        ],
        "prerequisites": ["concetto1", "concetto2"],
        "enables": ["concetto3"],
        "importance": 0.8,
        "confidence": 0.9,
        "tags": ["tag1", "tag2"]
      }
    ]
    """

    # Chiamata LLM
    beliefs = llm_manager.chat(provider, model, [{"role": "user", "content": prompt}])

    # Salva belief base
    context_manager.save_belief_base(context_name, beliefs)
```

**Utilizzo Belief Base:**

- Pre-caricata in Believer per accelerare estrazione
- Filtrata/correlata ai desires durante conversazione
- Classificata per rilevanza (CRITICO/ALTO/MEDIO/BASSO)

---

## Integrazione LLM

### Provider Supportati

#### 1. **Google Gemini**

**SDK:** `google-generativeai >= 0.3.0`

**Modelli disponibili:**

- `gemini-2.5-flash-lite`: Ultra-veloce, task semplici (max 65,536 token, default 4,096)
- `gemini-2.5-flash`: Bilanciato velocità/qualità — raccomandato (max 65,536 token, default 8,192)
- `gemini-2.5-pro`: Massima qualità, ragionamento complesso (max 65,536 token, default 8,192)
- `gemini-3-pro-preview`: Next-generation con capacità avanzate (Beta, max 65,536 token, default 8,192)

**Implementazione:**

```python
import google.generativeai as genai

class LLMManager:
    def _initialize_gemini(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_client = genai

    def _chat_gemini(self, model, messages, settings):
        # Separa system message da user messages
        system_instruction = next(
            (m['content'] for m in messages if m['role'] == 'system'),
            None
        )
        user_messages = [m for m in messages if m['role'] != 'system']

        # Configura model
        model_instance = self.gemini_client.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction,
            generation_config={
                "temperature": settings.get("temperature", 0.7),
                "max_output_tokens": settings.get("max_tokens", 2000),
                "top_p": settings.get("top_p", 0.9)
            }
        )

        # Chat
        response = model_instance.generate_content(
            [m['content'] for m in user_messages]
        )

        return response.text
```

**Caratteristiche Gemini:**

- System instructions native
- Multimodalità (testo, immagini - non usato attualmente)
- Token limit elevati (fino a 1M per Pro)
- Latenza contenuta

#### 2. **OpenAI**

**SDK:** `openai >= 1.12.0`

**Modelli Disponibili:**

**GPT-5 Series (reasoning_effort: low/medium/high):**
- `gpt-5`: Modello avanzato con reasoning
- `gpt-5-nano`: Versione leggera GPT-5
- `gpt-5-mini`: Versione media GPT-5

**GPT-5.1 Series — Novembre 2025+ (reasoning_effort: none/low/medium/high):**

- `gpt-5.1`: Ragionamento adattivo (thinking model)
- `gpt-5.1-chat-latest`: Istantanea ottimizzata per latenza (default reasoning_effort: none)

**GPT-5.2 Series — Dicembre 2025+ (reasoning_effort: none/low/medium/high):**

- `gpt-5.2`: Ragionamento adattivo (thinking model)
- `gpt-5.2-pro`: Versione pro con reasoning profondo (default reasoning_effort: high)
- `gpt-5.2-chat-latest`: Istantanea ottimizzata per latenza (default reasoning_effort: none)

**Implementazione:**

```python
from openai import OpenAI

class LLMManager:
    def _initialize_openai(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)

    def _chat_openai(self, model, messages, settings):
        # Prepara parametri
        params = {
            "model": model,
            "messages": messages,
            "temperature": settings.get("temperature", 0.7),
            "max_tokens": settings.get("max_tokens", 2000),
            "top_p": settings.get("top_p", 0.9)
        }

        # Reasoning effort per GPT-5/o1
        if model.startswith("gpt-5") or model.startswith("o1"):
            reasoning = settings.get("reasoning_effort", "medium")
            params["reasoning_effort"] = reasoning

        # Chat completion
        response = self.openai_client.chat.completions.create(**params)

        return response.choices[0].message.content
```

**Caratteristiche OpenAI:**

- Supporto reasoning effort (GPT-5/GPT-5.1/o1/o3)
- Function calling (non usato attualmente)
- JSON mode per output strutturato (potenziale uso futuro)
- Extended prompt caching (GPT-5.1, fino a 24 ore di retention)

**Gestione Parametri per Modelli con Reasoning (GPT-5/GPT-5.1/o1/o3):**

I modelli con reasoning hanno restrizioni sui parametri:
- ❌ `temperature`: Non supportato (ignorato)
- ❌ `top_p`: Non supportato (ignorato)
- ✅ `max_tokens`: Supportato (opzionale, varia per modello)
- ✅ `reasoning_effort`: **"none"**, **"low"**, **"medium"**, **"high"**
  - `"none"`: Disabilita il reasoning (utile per latenza bassa)
  - `"low"`: Reasoning minimo
  - `"medium"`: Ragionamento bilanciato (default)
  - `"high"`: Ragionamento profondo (latenza più alta)

**Esempio GPT-5.1 con Reasoning:**

```python
response = llm_manager.chat(
    provider="OpenAI",
    model="gpt-5.1",
    messages=[...],
    reasoning_effort="medium"  # Usa reasoning adattivo
)

# Per comportamento non-reasoning (latenza bassa):
response = llm_manager.chat(
    provider="OpenAI",
    model="gpt-5.1",
    messages=[...],
    reasoning_effort="none"  # Disabilita reasoning
)
```

### Configurazione Parametri per Modello (`utils/llm_manager_config.py`)

Il modulo `llm_manager_config.py` centralizza i vincoli e i default dei parametri per ogni modello supportato. `LLMManager` lo consulta per determinare quali parametri sono validi e quali valori predefiniti applicare.

**Struttura `MODEL_PARAMETERS`:**

```python
MODEL_PARAMETERS = {
    # --- Gemini: temperature, max_output_tokens, top_p ---
    "gemini-2.5-flash-lite": {
        "temperature":        {"min": 0.0, "max": 2.0,    "default": 1.0},
        "max_output_tokens":  {"min": 1,   "max": 65536,  "default": 4096},
        "top_p":              {"min": 0.0, "max": 1.0,    "default": 1.0}
    },
    "gemini-2.5-flash": {
        "temperature":        {"min": 0.0, "max": 2.0,    "default": 1.0},
        "max_output_tokens":  {"min": 1,   "max": 65536,  "default": 8192},
        "top_p":              {"min": 0.0, "max": 1.0,    "default": 1.0}
    },
    # gemini-2.5-pro e gemini-3-pro-preview: stessa struttura di flash

    # --- GPT-5 Series: reasoning_effort [low, medium, high] ---
    "gpt-5":      { "reasoning_effort": {"options": ["low","medium","high"], "default": "medium"} },
    "gpt-5-nano": { "reasoning_effort": {"options": ["low","medium","high"], "default": "medium"} },
    "gpt-5-mini": { "reasoning_effort": {"options": ["low","medium","high"], "default": "medium"} },

    # --- GPT-5.1 Series: reasoning_effort [none, low, medium, high] ---
    "gpt-5.1":              { "reasoning_effort": {"options": ["none","low","medium","high"], "default": "medium"} },
    "gpt-5.1-chat-latest":  { "reasoning_effort": {"options": ["none","low","medium","high"], "default": "none"} },

    # --- GPT-5.2 Series: reasoning_effort [none, low, medium, high] ---
    "gpt-5.2":              { "reasoning_effort": {"options": ["none","low","medium","high"], "default": "medium"} },
    "gpt-5.2-pro":          { "reasoning_effort": {"options": ["none","low","medium","high"], "default": "high"} },
    "gpt-5.2-chat-latest":  { "reasoning_effort": {"options": ["none","low","medium","high"], "default": "none"} },
}
```

**Vincoli parametri per tipologia modello:**

| Parametro | Gemini | OpenAI Standard | GPT-5/5.1/5.2 Reasoning |
|-----------|--------|-----------------|-------------------------|
| temperature | Sì (0.0–2.0) | Sì (0.0–2.0) | Ignorato |
| max_tokens | Sì (variabile) | Sì (variabile) | Sì (limiti maggiori) |
| top_p | Sì (0.0–1.0) | Sì (0.0–1.0) | Ignorato |
| reasoning_effort | N/A | N/A | Sì (none/low/medium/high) |

### Parametri LLM Configurabili

**Interfaccia Utente in Compass:**

```python
# Temperature
st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
# Controlla creatività: 0 = deterministico, 2 = molto creativo

# Max Tokens
st.slider("Max Tokens", 100, 8000, 2000, 100)
# Lunghezza massima risposta

# Top P (Nucleus Sampling)
st.slider("Top P", 0.0, 1.0, 0.9, 0.05)
# Campionamento probabilistico: 0.9 = top 90% massa probabilità

# Reasoning Effort (solo GPT-5/o1)
st.selectbox("Reasoning Effort", ["low", "medium", "high"])
# Profondità ragionamento chain-of-thought
```

**Configurazioni Predefinite per Agente:**

| Agente | Temperature | Max Tokens | Rationale |
|--------|-------------|------------|-----------|
| **Alì** | 0.7 | 2000 | Creatività moderata per esplorare desires |
| **Believer** | 0.5 | 3000 | Precisione per estrazione fatti |
| **Auditor** | 0.15 | 1500 | Consistenza per validazione |

### Gestione Messaggi e Conversazioni

**Formato Standard:**

```python
messages = [
    {
        "role": "system",
        "content": "Sei Alì, esperto di product strategy..."
    },
    {
        "role": "user",
        "content": "Quali sono i bisogni principali?"
    },
    {
        "role": "assistant",
        "content": "Basandomi sul contesto..."
    },
    {
        "role": "user",
        "content": "Approfondisci il primo punto"
    }
]
```

**Storico Conversazioni:**

- Memorizzato in `st.session_state.messages`
- Persistenza in sessione Streamlit (non su disco)
- Replay completo per ogni chiamata LLM (context window)

---

## Sistema Agenti BDI

### Framework BDI Implementato

**Belief-Desire-Intention** è un'architettura cognitiva classica dell'AI che modella agenti razionali:

1. **Beliefs (Credenze)**: Rappresentazione della conoscenza sul mondo
2. **Desires (Desideri)**: Obiettivi che l'agente vuole raggiungere
3. **Intentions (Intenzioni)**: Piani concreti per raggiungere i desires

**In LUMIA:**

- **Beliefs**: Fatti estratti dalla knowledge base aziendale
- **Desires**: Goal strategici degli stakeholder (utenti, manager, etc.)
- **Intentions**: Azioni derivate dall'analisi desires-beliefs (Cuma: WIP; Genius: MVP attivo)

### Architettura Agenti

```text
┌─────────────────────────────────────────────────────────────┐
│                   AGENT SYSTEM FLOW                         │
└─────────────────────────────────────────────────────────────┘

1. KNOL (Knowledge Base Builder)
   ↓
   Upload Docs → RAG Pipeline → ChromaDB + Belief Base
   ↓
2. COMPASS (Session Management)
   ↓
   Create Session → Configure LLM → Select Context
   ↓
3. ALÌ AGENT (Desires Extraction)
   ↓
   Domain Analysis → User Signals → Single Beneficiario → Desires → JSON
   ↓
   Save to session BDI data
   ↓
4. BELIEVER AGENT (Beliefs Extraction)
   ↓
   Load Desires → RAG Query → Extract Beliefs → Classify Relevance → Correlate
   ↓
   Save to session BDI data
   ↓
5. COMPASS (Analytics & Visualization)
   ↓
   View/Edit BDI → Graphs → Export BDI Framework
   ↓
6. GENIUS (Execution Coach — MVP Attivo)
   ↓
   Load BDI Framework → Select Desire → User Profile → Generate Plan → Track Progress
   ↓
7. CUMA (Intentions Planning — WIP)
   ↓
   Load Desires + Beliefs → Scenario Analysis → Intentions → Action Steps
```

### Agente Alì - Desires Extraction

**Ruolo:** Esperto di product strategy e user research

**System Prompt:** [prompts/ali.md](prompts/ali.md)

**Fasi Operative:**

#### Fase 1: Identificazione Dominio

```text
Input: Descrizione iniziale progetto
Output: Domain summary (breve sintesi dominio strategico)
```

#### Fase 2: Raccolta Segnali Utente

**Approccio Socratico:**

- Domande aperte per inferire persona
- NO multi-selezione esplicita
- Raccolta implicita di:
  - Ruolo stakeholder
  - Obiettivi strategici
  - Pain points
  - Contesto operativo

**Esempio Conversazione:**

```text
Alì: "Raccontami quale sfida principale stai affrontando in questo progetto"
User: "Dobbiamo migliorare l'engagement degli studenti nei corsi online"
[Alì inferisce: Persona = Instructional Designer / Course Manager]

Alì: "Quali metriche usi per misurare il successo attualmente?"
User: "Tasso di completamento e feedback surveys"
[Alì inferisce: Focus su retention e satisfaction]
```

#### Fase 3: Formalizzazione Beneficiario Singolo

**Output:**

```json
{
  "beneficiario_name": "Course Manager",
  "beneficiario_description": "Responsabile della progettazione e gestione corsi online, focalizzato su engagement e learning outcomes",
  "beneficiario_inference_notes": [
    "Menzionato engagement studenti come sfida primaria",
    "Usa metriche quantitative (completion rate)",
    "Interesse per feedback qualitativo"
  ]
}
```

**Nota Architetturale:** Versione precedente supportava multi-persona, ora rimosso per focus su singolo beneficiario primario (v2.5+).

#### Fase 4: Estrazione Desires con Checkpoint

**Sistema Checkpoint:**

- Ogni 3-5 scambi: Alì propone un **checkpoint 🧭**
- Riassume desires emersi
- Chiede conferma o raffinamento
- Evita deriva conversazionale

**Esempio Checkpoint:**

```text
🧭 CHECKPOINT

Finora abbiamo identificato questi desires:

D1: Aumentare il tasso di completamento corsi dal 45% al 70%
   • Priorità: ALTA
   • Success metric: Completion rate tracking

D2: Raccogliere feedback strutturato post-lezione
   • Priorità: MEDIA
   • Success metric: Response rate >50%

Questi rispecchiano le tue priorità? Vuoi aggiungere o modificare qualcosa?
```

#### Fase 5: Generazione Report JSON

**Trigger:** Utente richiede finalizzazione o Alì rileva convergenza

**Output Strutturato:**

```json
{
  "domain_summary": "Piattaforma e-learning per corsi universitari con focus su engagement e learning outcomes",
  "beneficiario": {
    "beneficiario_name": "Course Manager",
    "beneficiario_description": "...",
    "beneficiario_inference_notes": ["..."]
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "Aumentare il tasso di completamento dei corsi online dal 45% al 70% entro 6 mesi",
      "priority": "high",
      "success_metrics": [
        "Completion rate >= 70%",
        "Drop-off rate < 15%",
        "Student satisfaction score >= 4/5"
      ]
    },
    {
      "desire_id": "D2",
      "desire_statement": "Implementare sistema di feedback post-lezione per identificare criticità",
      "priority": "medium",
      "success_metrics": [
        "Response rate >= 50%",
        "Time to insight < 48h",
        "Actionable feedback >= 60%"
      ]
    }
  ]
}
```

**Auto-save:** JSON salvato automaticamente in `data/sessions/{session_id}/current_bdi.json`

### Agente Believer - Beliefs Extraction

**Ruolo:** Knowledge engineer specializzato in estrazione fatti strutturati

**System Prompt:** [prompts/believer.md](prompts/believer.md)

**Fasi Operative:**

#### Fase 1: Caricamento Desires

```python
# Legge desires da sessione attiva
desires = session_manager.get_bdi_data(session_id)['desires']
```

#### Fase 2: Interrogazione RAG Interattiva

**Approccio:**

- Utente guida l'esplorazione della KB
- Believer recupera contesto via RAG
- Estrae beliefs atomici pertinenti

**Esempio:**

```text
User: "Cerca informazioni sulle metriche di engagement nel corso di inglese"

Believer:
[RAG retrieval con query embedding]
Trovati 5 chunk rilevanti:

BELIEF ESTRATTO:
{
  "subject": "Corso di Inglese B2",
  "definition": "Corso di lingua inglese livello B2 con contenuti multimediali interattivi",
  "semantic_relations": [
    {
      "relation": "ha_metrica_engagement",
      "object": "Video completion rate 65%",
      "description": "Metrica di completamento video del corso"
    }
  ],
  "prerequisites": ["Livello B1 inglese"],
  "enables": ["Certificazione B2"],
  "importance": 0.9,
  "confidence": 0.95,
  "tags": ["engagement", "metriche", "video"],
  "fonte": "corso_inglese_stats.pdf, pagina 12"
}

Questo belief è CRITICO per il desire D1 (aumentare completion rate).
```

#### Fase 3: Classificazione Rilevanza

**Livelli:**

- **CRITICO**: Belief indispensabile per desire (blocca se mancante)
- **ALTO**: Molto rilevante, impatta direttamente
- **MEDIO**: Utile per contesto
- **BASSO**: Marginalmente collegato

**Logica Classificazione:**

```python
def classify_relevance(belief, desire):
    # LLM-driven con prompt specifico
    prompt = f"""
    Desire: {desire['desire_statement']}
    Belief: {belief['subject']} - {belief['definition']}
    Relations: {belief['semantic_relations']}

    Classifica rilevanza: CRITICO/ALTO/MEDIO/BASSO
    Assegna relevance_score (0.0-1.0)
    Spiega perché.
    """
    return llm_response
```

#### Fase 4: Correlazione Desires-Beliefs

**Struttura:**

```json
{
  "subject": "Corso di Inglese B2",
  "definition": "Corso di lingua inglese livello B2 con approccio multimediale e interattivo",
  "semantic_relations": [
    {
      "relation": "ha_video_interattivi",
      "object": "15 video con quiz embedded",
      "description": "Contenuti video con elementi di verifica integrati"
    }
  ],
  "prerequisites": ["Livello B1 inglese", "Competenze digitali base"],
  "enables": ["Certificazione B2", "Inglese professionale"],
  "importance": 0.85,
  "confidence": 0.95,
  "tags": ["video", "interattività", "quiz"],
  "source": "syllabus.pdf",
  "metadata": {
    "source_type": "base",
    "extraction_method": "rag_retrieval",
    "subject_type": "Corso",
    "object_type": "Risorsa Didattica"
  },
  "related_desires": [
    {
      "desire_id": "D1",
      "relevance_level": "ALTO",
      "definition": "I video interattivi aumentano engagement e possono migliorare completion rate"
    },
    {
      "desire_id": "D2",
      "relevance_level": "MEDIO",
      "definition": "Quiz embedded forniscono feedback implicito ma non sostituiscono survey esplicite"
    }
  ]
}
```

#### Fase 5: Generazione Report Beliefs

**Output:**

```json
{
  "beliefs": [
    {
      "subject": "...",
      "relazione": "...",
      "object": "...",
      "source": "...",
      "metadata": {...},
      "related_desires": [...]
    },
    ...
  ]
}
```

**Auto-merge:** Beliefs aggiunti a `current_bdi.json` della sessione

### Agente Auditor - Quality Assurance

**Ruolo:** Meta-agente di controllo qualità

**System Prompt:** [prompts/auditor.md](prompts/auditor.md) (ipotizzato)

**Funzioni:**

#### 1. Rilevamento Finalizzazione

```python
# Rileva se utente chiede JSON
user_message = "Dammi il report finale in JSON"

auditor_check = auditor.analyze(user_message, agent_response)
if auditor_check['is_finalization_request']:
    # Forza generazione JSON da agente
    enforce_json_output()
```

#### 2. Validazione Output

```python
# Verifica formato JSON
if agent_response.contains('```json'):
    json_content = extract_json(agent_response)
    validation = validate_schema(json_content, expected_schema)

    if validation.errors:
        return {
            "issues": ["JSON malformato", "Campo 'desires' mancante"],
            "improvements": ["Aggiungi campo 'domain_summary'"]
        }
```

#### 3. Suggerimenti Miglioramento

```python
{
  "issues": [],
  "improvements": [
    "Potresti essere più specifico sui success metrics del D3",
    "Manca correlazione belief B5 con desire D2"
  ],
  "quick_replies": [
    "Vuoi aggiungere altri desires?",
    "Procediamo con l'estrazione beliefs?"
  ]
}
```

**Parametri Auditor:**

- Temperature: **0.15** (molto bassa per consistenza)
- Max tokens: 1500
- Provider: Eredita da sessione

### Agente Cuma - Intentions Planning (Beta)

**Ruolo:** Specialista in pianificazione strategica e generazione intentions

**System Prompt:** `prompts/cuma_system_prompt.md`

**Status:** Beta (Gennaio 2026) - Funzionale, in attesa integrazione Auditor

**Fasi Operative:**

#### Fase 1: Caricamento BDI Context

```python
# Carica desires e beliefs dalla sessione
desires = session_manager.get_bdi_data(session_id)['desires']
beliefs = session_manager.get_bdi_data(session_id)['beliefs']
```

#### Fase 2: Analisi Desire-Belief Mapping

- Identifica desires prioritari
- Mappa beliefs rilevanti (CRITICO/ALTO) per ogni desire
- Identifica gap di conoscenza

#### Fase 3: Generazione Intentions

**Output Strutturato:**

```json
{
  "intention_id": "I1",
  "intention_statement": "Implementare sistema di onboarding interattivo per studenti",
  "linked_desire_id": "D1",
  "linked_beliefs": ["B1", "B3", "B5", "B7"],
  "action_steps": [
    {
      "step_id": "S1",
      "description": "Analisi drop-off points nel corso attuale",
      "estimated_effort": "1 settimana",
      "dependencies": [],
      "resources_needed": ["Analytics access", "UX researcher"]
    },
    {
      "step_id": "S2",
      "description": "Design wireframes onboarding flow",
      "estimated_effort": "2 settimane",
      "dependencies": ["S1"],
      "resources_needed": ["UI/UX designer", "Feedback da belief B3"]
    }
  ],
  "expected_outcomes": [
    "Riduzione drop-off del 30%",
    "Aumento completion rate a 70%"
  ],
  "risks": [
    {
      "risk": "Resistenza utenti a flow più lungo",
      "mitigation": "A/B testing con skip option"
    }
  ]
}
```

**Caratteristiche:**

- **Tracciamento Relazioni**: Collegamenti espliciti `linked_desire_id`, `linked_beliefs`
- **Action Steps Strutturati**: Effort estimates, dependencies, resources
- **Risk Assessment**: Identificazione rischi e strategie di mitigazione
- **Auto-save**: Intentions salvati in session BDI data

**Prossimi Sviluppi:**

- Integrazione Auditor per validazione intentions
- Sistema di prioritizzazione automatica
- Timeline generation

### Agente Genius - Execution Coach (MVP Attivo — v2.7)

**File:** `pages/6_Genius.py` (778 righe) + `utils/genius_engine.py` (1,239 righe)

**Prompts:** `genius_system_prompt.md`, `genius_discovery_prompt.md`, `genius_plan_generation_prompt.md`, `genius_step_tips_prompt.md`, `genius_coach_template.md`

**Obiettivo:** Trasformare un desire strategico estratto dal BDI in un piano d'azione personalizzato e strutturato, basandosi sui beliefs correlati come evidenza.

**Fasi Operative:**

#### Fase 1: Selezione BDI Framework

- Carica i BDI esportati da `data/bdi_frameworks/`
- Visualizza come card con metadati (desires, beliefs, tags, domain)
- Utente seleziona il BDI su cui operare

#### Fase 2: Selezione Desire Target

- Genius elenca tutti i desires del BDI caricato
- Utente seleziona il desire obiettivo (es. "D2")
- Detection tramite linguaggio naturale o ID diretto

#### Fase 3: Raccolta Profilo Utente (Conversazionale)

```text
Genius: "Qual è il tuo ruolo?"
User:   "Product Manager"
Genius: "Quanto tempo hai a disposizione?"
User:   "3 mesi"
Genius: "Qual è la situazione attuale?"
User:   "Onboarding basilare da migliorare"
Genius: "Ci sono vincoli?"
User:   "Team piccolo, solo 2 persone"
```

**Output:** oggetto `user_profile` con role, timeline_weeks, current_situation, constraints.

#### Fase 4: Generazione Piano (LLM-powered)

- Filtro beliefs rilevanti (CRITICO + ALTO) tramite `GeniusEngine.filter_beliefs()`
- Prompt a LLM con: desire target + beliefs filtrati + profilo utente
- Output strutturato: 3–5 fasi, 8–15 step totali, task per step, criteri di verifica
- Arricchimento metadati (status, timestamp)
- Auto-save in `data/genius_plans/`

#### Fase 5: Visualizzazione Piano

- Metriche sommarie (fasi, step, durata totale)
- Expander per fase con dettaglio step
- Per ogni step: tasks, criteri di verifica, beliefs di supporto
- Pulsante di salvataggio manuale

**Interazione con altri moduli:**

- **Compass** → esporta BDI framework che Genius consuma
- **Knol** → knowledge base → beliefs nel BDI
- **Alì** → definizione desires → target per Genius
- **Believer** → estrazione beliefs + correlazione → evidenza nel piano

**Sviluppi futuri pianificati:**

- Progress tracking interattivo nell'UI
- Q&A coaching durante l'esecuzione del piano
- Note utente per step
- Export piano in Markdown
- Integrazione sessione per storico piani
- Tips pratici per step (LLM enrichment)

---

## Flussi di Lavoro Principali

### Workflow Completo: Dalla KB al BDI Report

```text
FASE 1: SETUP KNOWLEDGE BASE (KNOL)
┌─────────────────────────────────────────┐
│ 1. Crea nuovo context                   │
│    • Nome: "corso_inglese"              │
│    • Descrizione: "Materiali corso..."  │
│    • Dominio: "Education"               │
├─────────────────────────────────────────┤
│ 2. Upload documenti                     │
│    • PDF: syllabus.pdf, stats.pdf       │
│    • URL: https://course-portal.com     │
│    • TXT: note_docenti.txt              │
├─────────────────────────────────────────┤
│ 3. Processamento automatico             │
│    • Chunking (1000 chars, 200 overlap) │
│    • Embedding generation               │
│    • ChromaDB indexing                  │
│    • Belief base extraction (LLM)       │
└─────────────────────────────────────────┘
                   ↓
FASE 2: CONFIGURAZIONE SESSIONE (COMPASS)
┌─────────────────────────────────────────┐
│ 1. Crea nuova sessione                  │
│    • Nome: "Improvement Plan Q1 2025"   │
│    • Tag: ["engagement", "analytics"]   │
├─────────────────────────────────────────┤
│ 2. Selezione knowledge base             │
│    • Context: "corso_inglese"           │
├─────────────────────────────────────────┤
│ 3. Configurazione LLM                   │
│    • Provider: Gemini                   │
│    • Model: gemini-2.5-flash            │
│    • Temperature: 0.7                   │
│    • Max tokens: 2000                   │
├─────────────────────────────────────────┤
│ 4. Attivazione sessione                 │
│    • Status: ACTIVE                     │
│    • Auto-save config                   │
└─────────────────────────────────────────┘
                   ↓
FASE 3: ESTRAZIONE DESIRES (ALÌ)
┌─────────────────────────────────────────┐
│ 1. Conversazione esplorativa            │
│    User: "Voglio migliorare engagement" │
│    Alì: [RAG context] "Quali metriche?" │
│    User: "Completion rate è al 45%"     │
│    Alì: "Target desiderato?"            │
│    User: "70% in 6 mesi"                │
├─────────────────────────────────────────┤
│ 2. Checkpoint intermedi                 │
│    🧭 Alì: "Riassumendo: D1=Aumentare   │
│    completion... D2=Feedback system..." │
│    User: "Confermo"                     │
├─────────────────────────────────────────┤
│ 3. Finalizzazione                       │
│    User: "Dammi il report"              │
│    Auditor: [Rileva richiesta JSON]     │
│    Alì: [Genera JSON desires]           │
│    Sistema: [Auto-save in session BDI]  │
└─────────────────────────────────────────┘
                   ↓
FASE 4: ESTRAZIONE BELIEFS (BELIEVER)
┌─────────────────────────────────────────┐
│ 1. Caricamento desires                  │
│    Believer: [Legge D1, D2 da session]  │
│    Believer: "Ho caricato 2 desires"    │
├─────────────────────────────────────────┤
│ 2. Interrogazione KB guidata            │
│    User: "Cerca stats engagement"       │
│    Believer: [RAG query] "Trovato:      │
│    Completion rate video=65%"           │
│    → Estrae belief B1                   │
│    → Classifica CRITICO per D1          │
├─────────────────────────────────────────┤
│ 3. Correlazione iterativa               │
│    Believer: "B1 è CRITICO per D1       │
│    perché impatta direttamente target"  │
│    User: "Cerca info su feedback"       │
│    [Ripeti per altri beliefs]           │
├─────────────────────────────────────────┤
│ 4. Finalizzazione                       │
│    User: "Genera report beliefs"        │
│    Believer: [JSON con correlazioni]    │
│    Sistema: [Merge in session BDI]      │
└─────────────────────────────────────────┘
                   ↓
FASE 5: ANALISI & VISUALIZZAZIONE (COMPASS)
┌─────────────────────────────────────────┐
│ 1. Dashboard BDI                        │
│    • Desires count: 2                   │
│    • Beliefs count: 15                  │
│    • Avg beliefs/desire: 7.5            │
├─────────────────────────────────────────┤
│ 2. Grafici interattivi (Plotly)         │
│    • Bar chart: Beliefs per desire      │
│    • Pie chart: Rilevanza distribution  │
│    • Network: Desires-Beliefs graph     │
├─────────────────────────────────────────┤
│ 3. Editing JSON                         │
│    • Modal editor con syntax highlight  │
│    • Validazione real-time              │
│    • Save changes                       │
├─────────────────────────────────────────┤
│ 4. Export BDI Framework                 │
│    • Download current_bdi.json          │
│    • Export in data/bdi_frameworks/     │
│    • Copy to clipboard                  │
└─────────────────────────────────────────┘
                   ↓
FASE 6: GENERAZIONE PIANO (GENIUS — MVP)
┌─────────────────────────────────────────┐
│ 1. Selezione BDI Framework              │
│    • Carica da data/bdi_frameworks/     │
│    • Seleziona il BDI esportato         │
├─────────────────────────────────────────┤
│ 2. Selezione Desire Target              │
│    • Genius elenca desires disponibili  │
│    • User: "Voglio lavorare su D2"      │
├─────────────────────────────────────────┤
│ 3. Profilo Utente (conversazionale)     │
│    • Ruolo, timeline, situazione        │
│    • Vincoli (team, budget)             │
├─────────────────────────────────────────┤
│ 4. Generazione Piano (LLM)             │
│    • Filter beliefs CRITICO + ALTO      │
│    • LLM genera struttura piano         │
│    • 3-5 fasi, 8-15 step               │
│    • Auto-save in genius_plans/         │
├─────────────────────────────────────────┤
│ 5. Visualizzazione & Tracking           │
│    • Metriche: fasi, step, durata       │
│    • Expander fase → step → tasks       │
│    • Beliefs di supporto per step       │
└─────────────────────────────────────────┘
```

### Workflow Alternativo: Update Existing Session

```text
SCENARIO: Aggiungere nuovi desires a sessione esistente

1. COMPASS → Select Session
   • Carica "Improvement Plan Q1 2025"
   • Status: ACTIVE

2. ALÌ → Continue Conversation
   • Alì: [Carica desires esistenti D1, D2]
   • Alì: "Vuoi aggiungere altri desires?"
   • User: "Sì, voglio anche ridurre churn studenti"
   • [Conversazione porta a D3]

3. ALÌ → Update Report
   • Genera JSON con D1, D2, D3 (merge)
   • Auto-save aggiorna session BDI

4. BELIEVER → Extract New Beliefs
   • Carica D3
   • RAG query per churn-related facts
   • Estrae beliefs B16-B20
   • Correla a D3

5. COMPASS → View Updated Analytics
   • Dashboard mostra 3 desires, 20 beliefs
   • Graph aggiornato
```

---

## Stack Tecnologico Completo

### Tabella Riepilogativa

| Layer | Componente | Tecnologia | Versione | Ruolo |
|-------|------------|------------|----------|-------|
| **Frontend** | Web Framework | Streamlit | 1.31.0+ | Interfaccia utente multi-page |
| | UI Components | streamlit-code-editor | latest | Editor JSON/code |
| | Grafici | Plotly | 5.18.0+ | Grafici interattivi |
| | Network Graph | PyVis | 0.3.2+ | Visualizzazioni network |
| **Backend** | Runtime | Python | 3.9+ | Core business logic |
| | Config Management | python-dotenv | 1.0.0+ | Variabili ambiente |
| | Data Validation | Pydantic + Settings | 2.0.0+ | Schema validation |
| | Plan Engine | GeniusEngine | - | Generazione/persistenza piani |
| | UI Messages | random | - | 86 messaggi variabili di attesa |
| **RAG** | Text Chunking | LangChain | 0.1.0+ | Orchestrazione RAG |
| | | langchain-text-splitters | 0.0.1+ | RecursiveCharacterTextSplitter |
| | Embeddings | sentence-transformers | 2.3.0+ | Generazione vettori |
| | | langchain-huggingface | 0.0.1+ | Integrazione HuggingFace |
| | Embedding Model | paraphrase-multilingual-MiniLM-L12-v2 | - | 384-dim, multilingue |
| **Vector DB** | Database | ChromaDB | 0.4.22+ | Storage embeddings |
| | Indexing | HNSW | - | Ricerca approssimata |
| | Similarity | Cosine | - | Metrica distanza |
| **LLM** | Provider 1 | Google Gemini | - | gemini-2.5-flash-lite/flash/pro + 3-pro-preview |
| | SDK Gemini | google-generativeai | 0.3.0+ | API client |
| | Config | llm_manager_config | - | Vincoli parametri per modello |
| | Provider 2 | OpenAI | - | GPT-5 / 5.1 / 5.2 series |
| | SDK OpenAI | openai | 1.12.0+ | API client |
| **Doc Processing** | PDF Parser | PyPDF2 | 3.0.0+ | Estrazione testo PDF |
| | HTML Parser | BeautifulSoup4 | 4.12.0+ | Web scraping |
| | HTTP Client | requests | 2.31.0+ | Fetch URLs |
| **Storage** | Sessioni/BDI | JSON | - | Filesystem persistence |
| | Piani Genius | JSON | - | `data/genius_plans/` |
| | BDI Framework | JSON | - | `data/bdi_frameworks/` |

### Dipendenze Python (requirements.txt)

```txt
# Web Framework
streamlit>=1.31.0
streamlit-code-editor

# Document Processing
PyPDF2>=3.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0

# Vector DB & RAG
chromadb>=0.4.22
langchain>=0.1.0
langchain-community>=0.0.20
langchain-text-splitters>=0.0.1
langchain-huggingface>=0.0.1
sentence-transformers>=2.3.0

# LLM Providers
google-generativeai>=0.3.0
openai>=1.12.0

# Data & Visualization
plotly>=5.18.0
pyvis>=0.3.2

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

### Configurazione Ambiente (.env)

```bash
# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### Requisiti Sistema

**Hardware Minimo:**

- CPU: 2 cores
- RAM: 4 GB (8 GB raccomandati)
- Storage: 2 GB (dipende da dimensione KB)

**Software:**

- Python: 3.9+
- OS: Windows/Linux/MacOS
- Browser: Chrome/Firefox/Safari (per UI Streamlit)

**Note:**

- Embedding model scaricato automaticamente da HuggingFace (~ 400 MB)
- ChromaDB crea file locali (dimensione proporzionale a KB)

---

## Considerazioni Architetturali Avanzate

### Scalabilità

**Limitazioni Attuali:**

- Single-user deployment (Streamlit session-based)
- Filesystem storage (non adatto a scale enterprise)
- No autenticazione/autorizzazione

**Percorsi di Scalabilità Futuri:**

- **Backend API**: FastAPI/Flask per multi-tenancy
- **Database**: PostgreSQL per metadata + ChromaDB managed
- **Auth**: OAuth2/JWT
- **Deployment**: Docker + Kubernetes

### Sicurezza

**Gestione API Keys:**

- Environment variables (`.env` non committato)
- **Raccomandazione:** Usare secret manager (AWS Secrets, Azure Key Vault)

**Data Privacy:**

- Knowledge bases locali (no cloud upload senza consenso)
- Session data su filesystem (potenziale risk se shared hosting)

**Validazione Input:**

- Pydantic per schema validation
- **Miglioramento futuro:** Sanitizzazione input utente contro injection

### Performance

**Ottimizzazioni Implementate:**

- Lazy initialization ChromaDB clients
- Caching embeddings (ChromaDB gestisce internamente)
- Batch embedding generation

**Bottleneck Potenziali:**

- LLM API latency (dipende da provider)
- Embedding generation per documenti grandi (parallelizzabile)
- ChromaDB query su KB massicce (HNSW mitiga)

**Miglioramenti Futuri:**

- Async API calls (aiohttp)
- GPU acceleration per embeddings (sentence-transformers su CUDA)
- Redis caching per query frequenti

### Manutenibilità

**Best Practices Adottate:**

- Separation of concerns (manager classes)
- Markdown-based prompts (facili da aggiornare)
- JSON schemas documentati

**Aree di Miglioramento:**

- **Testing**: Unit tests per utils/, integration tests per agenti
- **Logging**: Logging strutturato (attualmente minimale)
- **Monitoring**: Metriche su performance LLM, RAG retrieval quality

---

## Diagrammi Architetturali

### Diagramma Componenti

```text
┌──────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                                │
│  ┌─────────┐ ┌──────┐ ┌─────────┐ ┌─────────┐ ┌──────┐ ┌─────────┐  │
│  │ Compass │ │ Knol │ │   Alì   │ │Believer │ │ Cuma │ │ Genius  │  │
│  │ (Mgmt)  │ │ (KB) │ │(Desires)│ │(Beliefs)│ │(WIP) │ │ (Coach) │  │
│  └────┬────┘ └──┬───┘ └────┬────┘ └────┬────┘ └──┬───┘ └────┬────┘  │
└───────┼─────────┼──────────┼───────────┼─────────┼───────────┼──────┘
        │         │          │           │         │           │
        └─────────┴──────────┴───────────┴─────────┴───────────┘
                             │
        ┌────────────────────▼──────────────────────┐
        │        STREAMLIT SESSION STATE            │
        │   • Active session ID                     │
        │   • Conversation histories (per agente)   │
        │   • Temp UI state                         │
        └────────────────────┬──────────────────────┘
                             │
        ┌────────────────────▼────────────────────────────────────┐
        │                BUSINESS LOGIC LAYER                     │
        │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
        │  │SessionManager│  │ContextManager│  │  GeniusEngine │  │
        │  └──────┬───────┘  └───────┬──────┘  └───────┬───────┘  │
        │         │                  │                  │          │
        │  ┌──────▼───────┐  ┌──────▼──────────────┐   │          │
        │  │  LLMManager  │  │  DocumentProcessor  │   │          │
        │  │  (Multi-LLM) │  │  (RAG Pipeline)     │   │          │
        │  │  + Config    │  │                     │   │          │
        │  └──────┬───────┘  └──────┬─────────────┘   │          │
        │         │                 │                  │          │
        │  ┌──────▼─────────────────▼──────────────────▼──────┐   │
        │  │          ConversationAuditor                      │   │
        │  │    (Desires Auditor + Beliefs Auditor)            │   │
        │  └───────────────────────────────────────────────────┘   │
        └─────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────▼───────────────────────────────────┐
        │              DATA PERSISTENCE LAYER                     │
        │  ┌───────────────────────┐   ┌──────────────────────┐   │
        │  │ JSON Files            │   │   ChromaDB           │   │
        │  │ • sessions/           │   │ • Vector store       │   │
        │  │ • contexts/           │   │ • HNSW index         │   │
        │  │ • bdi_frameworks/     │   │ • Embeddings         │   │
        │  │ • genius_plans/       │   │ • Context-isolated   │   │
        │  └───────────────────────┘   └──────────────────────┘   │
        └─────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────▼───────────────────────────────────┐
        │              EXTERNAL SERVICES                          │
        │  ┌────────────────┐      ┌──────────────────┐           │
        │  │  Gemini API    │      │   OpenAI API     │           │
        │  │  (Google)      │      │   (GPT-5 series) │           │
        │  └────────────────┘      └──────────────────┘           │
        │  ┌──────────────────────────────────────────┐           │
        │  │  HuggingFace Model Hub                   │           │
        │  │  (paraphrase-multilingual-MiniLM-L12-v2) │           │
        │  └──────────────────────────────────────────┘           │
        └─────────────────────────────────────────────────────────┘
```

### Diagramma Flusso RAG

```text
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────┐
│ Embed Query                        │
│ (sentence-transformers)            │
│ Input: "Quali metriche di successo"│
│ Output: [0.12, -0.34, ..., 0.56]  │  (384-dim vector)
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ ChromaDB Query                     │
│ collection.query(                  │
│   query_embeddings=[vector],       │
│   n_results=5                      │
│ )                                  │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Similarity Search (HNSW)           │
│ Cosine similarity ranking          │
│ Return top-5 chunks                │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Retrieved Chunks                   │
│ [                                  │
│   "Chunk 1: Completion rate 65%",  │
│   "Chunk 2: Engagement metrics...", │
│   ...                              │
│ ]                                  │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Context Augmentation               │
│ Prompt = f"""                      │
│ CONTESTO: {chunks}                 │
│ DOMANDA: {query}                   │
│ """                                │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ LLM Generation                     │
│ (Gemini/OpenAI)                    │
│ → Contextual Response              │
└────────────────────────────────────┘
```
---

## Riferimenti

### Documentazione Tecnica

- [Streamlit Docs](https://docs.streamlit.io)
- [ChromaDB Docs](https://docs.trychroma.com)
- [LangChain Docs](https://python.langchain.com)
- [Gemini API Docs](https://ai.google.dev/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)

### Paper & Framework

- BDI Architecture: Rao & Georgeff (1995)
- RAG: Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- HNSW: Malkov & Yashunin (2016)

### Modelli

- [sentence-transformers](https://www.sbert.net/docs/pretrained_models.html)
- [Gemini Models](https://ai.google.dev/models/gemini)
- [OpenAI GPT Models](https://platform.openai.com/docs/models)

---

**Documento generato:** 10 Gennaio 2026
**Ultimo aggiornamento:** 5 Febbraio 2026 — allineamento completo al codice (Genius MVP, GeniusEngine, llm_manager_config, modelli corretti, diagrammi)
**Versione Architettura:** v2.7
**Autore:** LUMIA Development Team

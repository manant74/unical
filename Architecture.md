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
├── app.py                      # Entry point principale (Homepage)
├── pages/                      # Applicazione multi-pagina Streamlit
│   ├── 0_Compass.py           # Gestione sessioni & visualizzazione BDI
│   ├── 1_Knol.py              # Builder knowledge base
│   ├── 2_Ali.py               # Agente estrazione desires
│   ├── 3_Believer.py          # Agente estrazione beliefs
│   ├── 5_Cuma.py              # Scenario planning (in sviluppo)
│   └── 6_Genius.py            # Ottimizzazione BDI (in sviluppo)
├── utils/                      # Core business logic
│   ├── llm_manager.py         # Orchestrazione LLM multi-provider
│   ├── document_processor.py  # RAG & processamento documenti
│   ├── session_manager.py     # Gestione lifecycle sessioni
│   ├── context_manager.py     # Gestione multi-context KB
│   ├── auditor.py             # Quality assurance conversazioni
│   └── prompts.py             # Caricamento system prompt
├── prompts/                    # System prompt agenti (Markdown)
├── data/                       # Storage persistente
│   ├── contexts/              # Knowledge bases multiple
│   └── sessions/              # Sessioni di lavoro
└── docs/                       # Documentazione tecnica
```

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

| Pagina | File | Funzione |
|--------|------|----------|
| **Homepage** | `app.py` | Landing page con descrizione del sistema |
| **Compass** | `pages/0_Compass.py` | Gestione sessioni, visualizzazione BDI, analytics |
| **Knol** | `pages/1_Knol.py` | Creazione/gestione knowledge bases |
| **Alì** | `pages/2_Ali.py` | Interfaccia agente estrazione desires |
| **Believer** | `pages/3_Believer.py` | Interfaccia agente estrazione beliefs |
| **Cuma** | `pages/5_Cuma.py` | Scenario planning (futuro) |
| **Genius** | `pages/6_Genius.py` | Ottimizzazione BDI (futuro) |

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

#### 5. **UI Messages** (`utils/ui_messages.py`)

Modulo utility per messaggi di attesa variabili e contestuali.

**Responsabilità:**

- Gestione lista di messaggi simpatici sulla gestione della conoscenza
- Selezione casuale di messaggi per spinner e indicatori di caricamento
- Mantenimento di tono professionale e creativo durante l'elaborazione

**Messaggio Randomico:**

```python
def get_random_thinking_message():
    """Restituisce un messaggio casuale dalla lista dei 25 messaggi approvati."""
    return random.choice(THINKING_MESSAGES)
```

**Utilizzo:**

```python
from utils.ui_messages import get_random_thinking_message

with st.spinner(get_random_thinking_message()):
    # Elaborazione LLM o RAG
    pass
```

**Lista Messaggi (25):**

- 7 messaggi originali sulla gestione della conoscenza
- 18 messaggi con riferimenti fantascientifici (Borges, Asimov, Star Trek, Blade Runner, Dick, Star Wars)

#### 6. **ConversationAuditor** (`utils/auditor.py`)

Meta-agente di quality assurance per risposte degli agenti.

**Funzionalità:**

- Monitoraggio conversazioni Alì e Believer
- Rilevamento richieste di finalizzazione (generazione JSON)
- Validazione formato output strutturato
- Suggerimenti di miglioramento
- Quick replies per l'utente

**Output Auditor:**

```json
{
  "issues": ["Issue 1", "Issue 2"],
  "improvements": ["Miglioramento 1"],
  "quick_replies": ["Domanda 1?", "Domanda 2?"]
}
```

**Parametri LLM Auditor:**

- Temperature: 0.15 (bassa per consistenza)
- Max tokens: 1500
- Provider: Stesso della sessione attiva

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

**Modelli Disponibili:**

- `gemini-2.5-flash-lite`: Ultra-veloce, uso generale
- `gemini-2.5-flash`: Bilanciato velocità/qualità
- `gemini-2.5-pro`: Massima qualità, ragionamento complesso

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

- `gpt-4o`: Ottimizzato per velocità
- `gpt-4o-mini`: Versione compatta
- `gpt-5`: Modello avanzato con reasoning
- `gpt-5-nano`: Versione leggera GPT-5
- `gpt-5-mini`: Versione media GPT-5

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

- Supporto reasoning effort (GPT-5/o1)
- Function calling (non usato attualmente)
- JSON mode per output strutturato (potenziale uso futuro)

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
- **Intentions**: Azioni derivate dall'analisi desires-beliefs (futuro: Genius)

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
   Domain Analysis → User Signals → Single Persona → Desires → JSON
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
   View/Edit BDI → Graphs → Export
   ↓
6. CUMA & GENIUS (Future: Scenario Planning & Optimization)
```text

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

#### Fase 3: Formalizzazione Persona Singola

**Output:**

```json
{
  "persona_name": "Course Manager",
  "persona_description": "Responsabile della progettazione e gestione corsi online, focalizzato su engagement e learning outcomes",
  "persona_inference_notes": [
    "Menzionato engagement studenti come sfida primaria",
    "Usa metriche quantitative (completion rate)",
    "Interesse per feedback qualitativo"
  ]
}
```

**Nota Architetturale:** Versione precedente supportava multi-persona, ora rimosso per focus su singolo stakeholder primario.

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
  "persona": {
    "persona_name": "Course Manager",
    "persona_description": "...",
    "persona_inference_notes": ["..."]
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

### Agenti Futuri (In Sviluppo)

#### **Cuma** - Scenario Planning

**Obiettivo:** Analisi predittiva e scenario what-if

**Funzionalità Pianificate:**

- Simulazione scenari alternativi
- Impact analysis desires-beliefs
- Identificazione gap critici

#### **Genius** - BDI Optimization

**Obiettivo:** Generazione intentions e piani d'azione

**Funzionalità Pianificate:**

- Analisi gap desires-beliefs
- Generazione intentions strutturate
- Prioritizzazione azioni
- Resource allocation suggestions

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
│ 4. Export                               │
│    • Download current_bdi.json          │
│    • Copy to clipboard                  │
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
| | Visualizzazioni | Plotly | 5.18.0+ | Grafici interattivi |
| | Data Manipulation | Pandas | 2.0.0+ | Tabelle e analytics |
| | Graph Analytics | NetworkX | 3.2+ | Grafi desires-beliefs |
| **Backend** | Runtime | Python | 3.9+ | Core business logic |
| | Config Management | python-dotenv | 1.0.0+ | Variabili ambiente |
| | Data Validation | Pydantic | 2.0.0+ | Schema validation |
| | UI Messages | random | - | Messaggi variabili di attesa |
| **RAG** | Text Chunking | LangChain | 0.1.0+ | Orchestrazione RAG |
| | | langchain-text-splitters | 0.0.1+ | RecursiveCharacterTextSplitter |
| | Embeddings | sentence-transformers | 2.3.0+ | Generazione vettori |
| | | langchain-huggingface | 0.0.1+ | Integrazione HuggingFace |
| | Embedding Model | paraphrase-multilingual-MiniLM-L12-v2 | - | 384-dim, multilingue |
| **Vector DB** | Database | ChromaDB | 0.4.22+ | Storage embeddings |
| | Indexing | HNSW | - | Ricerca approssimata |
| | Similarity | Cosine | - | Metric distanza |
| **LLM** | Provider 1 | Google Gemini | - | gemini-2.5-flash/pro/lite |
| | SDK Gemini | google-generativeai | 0.3.0+ | API client |
| | Provider 2 | OpenAI | - | GPT-4o, GPT-5 series |
| | SDK OpenAI | openai | 1.12.0+ | API client |
| **Document Processing** | PDF Parser | PyPDF2 | 3.0.0+ | Estrazione testo PDF |
| | HTML Parser | BeautifulSoup4 | 4.12.0+ | Web scraping |
| | HTTP Client | requests | 2.31.0+ | Fetch URLs |
| **Storage** | Format | JSON | - | Filesystem persistence |
| | Encoding | UTF-8 | - | Testo multilingue |

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
networkx>=3.2
pandas>=2.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
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
┌───────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ Compass │  │  Knol   │  │   Alì   │  │Believer │          │
│  │ (Mgmt)  │  │  (KB)   │  │(Desires)│  │(Beliefs)│          │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
└───────┼───────────┼────────────┼────────────┼────────────────┘
        │           │            │            │
        └───────────┴────────────┴────────────┘
                    │
        ┌───────────▼───────────────────────┐
        │   STREAMLIT SESSION STATE         │
        │   • Active session ID             │
        │   • Conversation history          │
        │   • Temp UI state                 │
        └───────────┬───────────────────────┘
                    │
        ┌───────────▼───────────────────────────────────────┐
        │             BUSINESS LOGIC LAYER                  │
        │  ┌──────────────┐  ┌──────────────┐              │
        │  │SessionManager│  │ContextManager│              │
        │  └──────┬───────┘  └───────┬──────┘              │
        │         │                   │                     │
        │  ┌──────▼───────┐  ┌───────▼──────────────────┐  │
        │  │  LLMManager  │  │  DocumentProcessor       │  │
        │  │  (Multi-LLM) │  │  (RAG Pipeline)          │  │
        │  └──────┬───────┘  └───────┬──────────────────┘  │
        │         │                   │                     │
        │  ┌──────▼──────────────────▼─────────┐           │
        │  │     ConversationAuditor            │           │
        │  │     (Quality Assurance)            │           │
        │  └────────────────────────────────────┘           │
        └───────────────┬──────────────────────────────────┘
                        │
        ┌───────────────▼──────────────────────────────────┐
        │           DATA PERSISTENCE LAYER                 │
        │  ┌──────────────────┐   ┌───────────────────┐   │
        │  │ JSON Files       │   │   ChromaDB        │   │
        │  │ • sessions/      │   │ • Vector store    │   │
        │  │ • contexts/      │   │ • HNSW index      │   │
        │  │ • BDI data       │   │ • Embeddings      │   │
        │  └──────────────────┘   └───────────────────┘   │
        └──────────────────────────────────────────────────┘
                        │
        ┌───────────────▼──────────────────────────────────┐
        │            EXTERNAL SERVICES                     │
        │  ┌────────────────┐      ┌──────────────────┐   │
        │  │  Gemini API    │      │   OpenAI API     │   │
        │  │  (Google)      │      │   (GPT-4o/5)     │   │
        │  └────────────────┘      └──────────────────┘   │
        │  ┌────────────────────────────────────────────┐  │
        │  │  HuggingFace Model Hub                     │  │
        │  │  (sentence-transformers embeddings)        │  │
        │  └────────────────────────────────────────────┘  │
        └──────────────────────────────────────────────────┘
```text

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

## Changelog Architetturale

### v2.5 (Novembre 2025) - Architettura Corrente

**Breaking Changes:**

- ✂️ Rimossa architettura multi-persona
- ✂️ Rimosso supporto Anthropic Claude

**Aggiunte:**

- ✨ Agente Auditor per QA conversazioni
- ✨ Analytics dashboard con Plotly/NetworkX
- ✨ Modal editor JSON in-app
- ✨ Normalizzazione parametri LLM cross-provider

**Miglioramenti:**

- 🔧 Single-persona architecture (focus stakeholder primario)
- 🔧 Reasoning effort parameter per GPT-5/o1
- 🔧 Backward compatibility handling session data

### v2.0 (Ipotetica - Pre-2025)

**Features:**

- Multi-persona desires extraction
- Anthropic Claude support
- Basic Compass session management

---

## Conclusioni e Direzioni Future

### Punti di Forza Architetturali

1. **Modularità**: Manager classes ben separati, facili da estendere
2. **Flessibilità LLM**: Provider-agnostic, facile aggiunta nuovi provider
3. **RAG Efficace**: ChromaDB + sentence-transformers offre semantic search di qualità
4. **BDI Framework**: Approccio strutturato e teoricamente fondato
5. **UX Streamlit**: Rapid prototyping con UI pulita

### Aree di Miglioramento

1. **Multi-Tenancy**: Attualmente single-user, necessità autenticazione
2. **Testing**: Coverage limitato, aggiungere unit/integration tests
3. **Monitoring**: Mancano metriche su performance/qualità RAG
4. **Scalabilità Storage**: Filesystem limita deployment cloud
5. **Async Operations**: Molte operazioni bloccanti (LLM calls, embedding)

### Roadmap Tecnologica Suggerita

**Short-term (3-6 mesi):**

- Completare Cuma e Genius agents
- Aggiungere export multi-formato (CSV, Excel)
- Migliorare analytics dashboard (trend analysis)
- Implementare caching query frequenti

**Medium-term (6-12 mesi):**

- Backend API REST/GraphQL
- Database relazionale per metadata
- Autenticazione e multi-tenancy
- Docker containerization

**Long-term (12+ mesi):**

- Cloud deployment (AWS/Azure/GCP)
- Advanced analytics (ML-driven insights)
- Collaborative features (team sessions)
- Integration con strumenti esterni (Jira, Notion, etc.)

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

**Documento generato:** 25 Novembre 2025
**Versione Architettura:** v2.5
**Autore:** LUMIA Development Team

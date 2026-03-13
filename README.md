# LUMIA Studio

**LUMIA Studio** is an AI-powered knowledge engineering platform that transforms unstructured documents into structured strategic insights using the BDI (Belief-Desire-Intention) cognitive framework. It's a multi-page Streamlit app with a RAG pipeline and a multi-agent conversational system.

> **LUMIA** = **L**earning **U**nified **M**odel for **I**ntelligent **A**gents

---

## What is LUMIA Studio?

LUMIA Studio is a **knowledge engineering** and **strategic planning** tool that helps domain experts:

1. **Structure knowledge** — Transforms unstructured documents (PDF, web, text) into a queryable knowledge base via RAG (Retrieval Augmented Generation)
2. **Identify strategic objectives (Desires)** — Through guided conversations with AI agents, identifies and formalizes the needs and goals of your domain's end users
3. **Extract relevant knowledge (Beliefs)** — Automatically analyzes the knowledge base to extract only the facts pertinent to identified objectives, with priority classification
4. **Plan and execute (Intentions)** — Transforms the BDI framework into concrete, trackable action plans

### The BDI Framework

The **Belief-Desire-Intention** model separates cognition into three layers:

- **Beliefs** — Facts, principles, and assumptions about the domain: *"what I know about the world"*
- **Desires** — Goals and desired states: *"what I want to achieve"*
- **Intentions** — Action plans to reach desires: *"how I get there"*

---

## Agents

LUMIA Studio is organized around six specialized agents, each accessible as a Streamlit page:

| Agent | Page | Role |
| ----- | ---- | ---- |
| **Compass** | `0_Compass.py` | Session management, BDI dashboard, and analytics |
| **Knol** | `1_Knol.py` | Knowledge base builder (document upload + RAG indexing) |
| **Alì** | `2_Ali.py` | Desires extraction via Socratic conversation |
| **Believer** | `3_Believer.py` | Beliefs extraction with desire-correlation |
| **Cuma** | `4_Cuma.py` | Intentions planning — Beta |
| **Genius** | `6_Genius.py` | BDI-powered execution coach |

### Compass — Session & BDI Management

Central control panel and mandatory starting point for every LUMIA project.

**Session management:**

- Create sessions with name, description, and tags
- Select the knowledge context to use (or "None" for blank projects)
- Configure LLM provider (Gemini / OpenAI) and model
- Tune model-specific parameters: temperature (0.0–2.0), max output tokens (up to 65,536), top-p, and reasoning effort (`none` / `low` / `medium` / `high` for GPT-5 series)
- Test the LLM connection before starting
- Load, switch, or delete recent sessions
- **Export as Framework** — exports the session BDI to `data/bdi_frameworks/` for use in Genius

**BDI data management (tabbed UI):**

- **Desires tab** — view, edit, and delete desires extracted by Alì
- **Beliefs tab** — view, edit, and delete beliefs extracted by Believer
- **Intentions tab** — view and manage intentions from Cuma
- **BDI Graph tab** — interactive desire-belief graph with dynamic node sizing by graph weight; switchable layouts: BarnesHut, ForceAtlas2, Hierarchical, Repulsion, Circular, Radial
- JSON editor with syntax highlighting, real-time validation, and safe save

**Context & belief base:**

- Import beliefs from the selected context's belief base
- Expandable/collapsible editor for large JSON payloads
- Backward-compatible with legacy `personas` format

---

### Knol — Knowledge Base Builder

Manages all knowledge contexts and feeds the RAG pipeline used by downstream agents.

**Context management:**

- Create and switch between multiple named contexts
- Per-context statistics: document count, belief count, last updated
- ZIP export and import for full context portability

**Document ingestion:**

- Supported formats: PDF, web URLs (scraped via BeautifulSoup), `.txt`, `.md`
- Chunking: RecursiveCharacterTextSplitter — 1,000-char chunks, 200-char overlap
- Embedding: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, multilingual)
- Storage: ChromaDB persistent vector store, one collection per context

**Belief base extraction:**

- **Extract Belief Base** button — generates a structured belief base from the indexed documents using the LLM
- Auto-generates a 20-word context description if none exists
- Saves to `belief_base.json` in the context directory

**Testing & maintenance:**

- **Test KB** — send a free-text query and inspect the retrieved chunks with similarity scores
- **Clear KB** — wipe the ChromaDB index while keeping the context
- **Delete context** — remove the context and all associated data
- **Belief Base editor** — modal JSON editor with syntax highlighting for manual corrections

---

### Alì — Desires Agent

Socratic conversational agent specialized in product strategy, user research, and design thinking.

**Conversation flow:**

1. Greets the user with a context-aware welcome (reads context description from Knol metadata)
2. Explores the domain without asking the user to list beneficiaries explicitly
3. Infers the primary beneficiary category from signals, examples, and behaviors in the conversation
4. Elicits desires through strategic questions, capturing: desire statement, deep motivation, and success metrics
5. Generates a structured JSON report with the inferred beneficiary and all desires on request

**Quality assurance:**

- Dedicated rubric-based auditor (`desires_auditor_system_prompt.md`) scores every response on 6 dimensions (0–5): query coherence, module alignment, context preservation, dialogue progression, beneficiary focus, finalization/JSON handling
- Auditor provides issues, improvement suggestions, and quick replies

**UX & persistence:**

- Session badge in sidebar; quick link to Compass
- LLM parameters inherited from the active session (temporary override available)
- Desires auto-saved to the session BDI in real time
- **Add desire manually** — sidebar form with full metadata: statement, priority, context, success criteria
- **New conversation** button to reset chat without losing saved desires

---

### Believer — Beliefs Agent

Knowledge engineering agent that extracts structured, desire-correlated facts from the RAG knowledge base.

**Extraction modes:**

- **Interactive** (default) — guided conversation; Believer queries the KB per topic and extracts beliefs one by one
- **From belief base** — generates beliefs from the context's pre-extracted belief base, correlating with desires
- **Mixed** — combines belief base entries with new RAG-retrieved chunks
- **From scratch** — ignores the belief base entirely and derives beliefs directly from KB chunks and desires; useful when the belief base is absent or noisy

**Belief structure per entry:**

- `subject` / `definition` (WHAT it is, WHY it matters, HOW it works)
- `semantic_relations` — typed, annotated relations to other concepts
- `source` — exact source citation
- `importance` and `confidence` scores
- `related_desires` — relevance level per desire: **CRITICO** / **ALTO** / **MEDIO** / **BASSO**

**Quality assurance:**

- Dedicated rubric-based auditor (`belief_auditor_system_prompt.md`) scores every response on 6 dimensions: query coherence, context preservation, belief specificity, belief structure, evidence/source, finalization/JSON handling

**UX & persistence:**

- Desires from the active session displayed in the sidebar
- Beliefs auto-saved to the session BDI in real time
- **Add belief manually** — sidebar form with type, confidence, multi-select correlated desires, and evidence
- LLM parameters inherited from the session (temporary override available)

---

### Cuma — Intentions Agent *(Beta)*

Converts the session's desires and beliefs into structured, executable action plans.

**Features:**

- Two conversation modes: **Map multiple Intentions** (broad domain coverage) and **Deep dive** (focused exploration of a single aspect)
- Each intention includes: linked desire ID, linked belief IDs, action steps with effort estimates and dependencies, expected outcomes, and risk/mitigation pairs
- Intentions auto-saved to the session BDI

**Status:** functional; Auditor integration pending.

---

### Genius — Execution Coach

Personal execution coach that works on exported BDI frameworks, independent of the active session.

**Workflow:**

1. Load a BDI framework from `data/bdi_frameworks/` (exported from Compass) or restore a previously saved plan
2. Select the target desire via conversation (by ID or description)
3. Answer discovery questions: role, timeline, current situation, constraints
4. Genius generates a phased action plan, prioritizing beliefs with CRITICO and ALTO relevance
5. Optionally enrich each step with practical tips and tools
6. Track step completion via sidebar checkboxes; progress persisted to disk

**Features:**

- Dedicated engine (`genius_engine.py`) for BDI loading, belief filtering, plan generation, and persistence
- Plans saved in `data/genius_plans/` with active plan marker (`.active_plan`)
- **Export Markdown** — download the full plan as a `.md` file
- Sidebar progress bar and per-phase status
- Same BDI framework reusable for multiple plans targeting different desires

---

## Workflow

```text
Compass (configure session)
    → Knol (build knowledge base)
    → Alì (extract desires)
    → Believer (extract beliefs)
    → Compass (review & validate BDI)
    → Cuma (optional: plan intentions)
    → Genius (generate & track action plan)
```

---

## Deploy

### Local

**Prerequisites:** Python 3.9+, pip

```bash
# 1. Clone the repository
git clone <repository-url>
cd unical

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pre-download the embedding model (~120 MB, one-time)
python setup_models.py

# 5. Configure API keys
cp .env.example .env
# Edit .env — set at least one of GOOGLE_API_KEY or OPENAI_API_KEY

# 6. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`. To use a different port:

```bash
streamlit run app.py --server.port 8502
```

---

### Streamlit Community Cloud

1. Push the repository to GitHub (ensure `.env` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select the repository, branch, and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, add your API keys in TOML format:

```toml
GOOGLE_API_KEY = "your_google_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
```

1. Click **Deploy**.

> **Note:** The embedding model (~120 MB) is downloaded on first run. Streamlit Cloud instances are ephemeral — the `data/` directory (sessions, contexts, plans) is not persisted between restarts. For production use, mount external storage or use a persistent database.

---

### Docker

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ChromaDB and PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download the embedding model at build time
RUN python setup_models.py

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
```

Build and run:

```bash
# Build the image
docker build -t lumia-studio .

# Run with API keys passed as environment variables
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_google_api_key \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/data:/app/data \
  lumia-studio
```

The `-v $(pwd)/data:/app/data` mount persists sessions, contexts, and plans across container restarts.

With **Docker Compose** (`docker-compose.yml`):

```yaml
services:
  lumia-studio:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

```bash
# Start
docker compose up -d

# Stop
docker compose down
```

---

## Architecture

### Layered structure

- **`pages/`** — Streamlit pages (presentation layer). Each page is a self-contained agent UI.
- **`utils/`** — Business logic managers (no Streamlit imports).
- **`prompts/`** — Agent system prompts as Markdown files, loaded with LRU cache via `utils/prompts.py`.
- **`data/`** — Filesystem-based persistence (JSON + ChromaDB vector stores).

### Core utilities

| Module | Role |
| ------ | ---- |
| `llm_manager.py` | Multi-provider LLM interface (Gemini + OpenAI). `LLMManager.chat()` is the single entry point for all LLM calls |
| `llm_manager_config.py` | Per-model parameter configuration (used for dynamic UI in Compass) |
| `session_manager.py` | Session CRUD. Active session tracked via `data/sessions/.active_session` |
| `context_manager.py` | ChromaDB lifecycle management with lazy initialization. Always call `release_chroma_client()` after use |
| `document_processor.py` | RAG pipeline: PDF/URL/text → chunk (1000 chars, 200 overlap) → embed → ChromaDB |
| `auditor.py` | Quality validation meta-agent. Separate prompts for Desires and Beliefs auditors |
| `genius_engine.py` | Plan generation and persistence for Genius |
| `prompts.py` | Loads system prompts from `prompts/` with LRU cache |
| `ui_messages.py` | Dynamic spinner messages during LLM calls |

### Data flow

1. Documents uploaded via Knol → chunked → embedded (`paraphrase-multilingual-MiniLM-L12-v2`, 384-dim) → ChromaDB
2. Alì converses → extracts **desires** → saved to `data/sessions/{id}/current_bdi.json`
3. Believer retrieves chunks via RAG → extracts **beliefs** with desire-correlation → saved to same BDI file
4. Compass exports BDI to `data/bdi_frameworks/`
5. Genius loads BDI → generates action plan → saves to `data/genius_plans/`

### Project structure

```text
unical/
├── app.py                          # Homepage with agent cards + dark/light toggle
├── pages/
│   ├── 0_Compass.py               # Session management, BDI dashboard
│   ├── 1_Knol.py                  # Knowledge base builder
│   ├── 2_Ali.py                   # Desires agent
│   ├── 3_Believer.py              # Beliefs agent
│   ├── 4_Cuma.py                  # Intentions agent (Beta)
│   └── 6_Genius.py                # Execution coach
├── prompts/
│   ├── ali_system_prompt.md
│   ├── believer_system_prompt.md
│   ├── believer_from_scratch_prompt.md
│   ├── believer_mix_beliefs_prompt.md
│   ├── belief_base_prompt.md
│   ├── cuma_system_prompt.md
│   ├── desires_auditor_system_prompt.md
│   ├── belief_auditor_system_prompt.md
│   ├── genius_discovery_prompt.md
│   ├── genius_plan_generation_prompt.md
│   ├── genius_step_tips_prompt.md
│   └── genius_coach_template.md
├── utils/
│   ├── llm_manager.py
│   ├── llm_manager_config.py
│   ├── session_manager.py
│   ├── context_manager.py
│   ├── document_processor.py
│   ├── auditor.py
│   ├── genius_engine.py
│   ├── prompts.py
│   └── ui_messages.py
├── data/
│   ├── contexts/{name}/           # ChromaDB + metadata + belief_base.json
│   ├── sessions/{id}/             # metadata, config, current_bdi.json
│   ├── bdi_frameworks/            # Exported BDI for Genius
│   └── genius_plans/              # Generated action plans
├── docs/
├── requirements.txt
├── setup_models.py                 # One-time embedding model download
├── .env.example
└── README.md
```

---

## BDI Data Model

Core JSON structure in `data/sessions/{id}/current_bdi.json`:

```json
{
  "domain_summary": "...",
  "beneficiario": {
    "beneficiario_name": "...",
    "beneficiario_description": "...",
    "beneficiario_inference_notes": []
  },
  "desires": [
    {
      "desire_id": "D1",
      "desire_statement": "...",
      "priority": "high|medium|low",
      "motivation": "...",
      "success_metrics": [],
      "context": "..."
    }
  ],
  "beliefs": [
    {
      "subject": "...",
      "definition": "WHAT it is. WHY it matters. HOW it works.",
      "semantic_relations": [
        { "relation": "...", "object": "...", "description": "..." }
      ],
      "source": "...",
      "importance": 0.9,
      "confidence": 0.9,
      "related_desires": [
        { "desire_id": "D1", "relevance_level": "CRITICO|ALTO|MEDIO|BASSO", "definition": "..." }
      ]
    }
  ],
  "intentions": []
}
```

Belief relevance levels:

- **CRITICO** — Directly answers the desire; quantitative data or absolute constraints
- **ALTO** — Significantly supports the desire; essential information
- **MEDIO** — Useful context and background information
- **BASSO** — Marginally relevant; indirect connection

---

## LLM Providers

### Google Gemini

- `gemini-2.5-pro` — Maximum quality, complex reasoning
- `gemini-2.5-flash` — Balanced speed/quality (recommended)
- `gemini-2.5-flash-lite` — Maximum speed, simple tasks

Parameters: `temperature` (0.0–2.0), `max_output_tokens` (up to 65536), `top_p` (0.0–1.0)

### OpenAI

- `gpt-5`, `gpt-5-nano`, `gpt-5-mini`
- `gpt-5.1`, `gpt-5.1-chat-latest`
- `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.2-chat-latest`

GPT-5/5.1/5.2 models use `reasoning_effort` (`none` / `low` / `medium` / `high`) and do not support `temperature` or `top_p`.

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Frontend/Backend | Streamlit 1.x |
| LLMs | Google Gemini, OpenAI GPT-5 series |
| Embeddings | `sentence-transformers` — `paraphrase-multilingual-MiniLM-L12-v2` (384-dim) |
| Vector DB | ChromaDB (persistent client) |
| Document processing | PyPDF2, BeautifulSoup4, LangChain text splitters |
| Visualization | Plotly, PyVis |
| Persistence | JSON files |
| Config | python-dotenv |

---

## Contributing

Contributions, issues, and feature requests are welcome.

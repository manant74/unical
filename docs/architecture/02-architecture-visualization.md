# 2. Architecture Visualization

← [Back to Index](index.md)

---

## Interactive Diagram (Excalidraw)

The full layered architecture is available as an editable Excalidraw diagram:

📄 [lumia-architecture.excalidraw](../lumia-architecture.excalidraw)

To open it: drag-and-drop the file on [excalidraw.com](https://excalidraw.com), or use the **Excalidraw** VS Code extension.

The diagram shows the three layers (Presentation → Business Logic → Data), the BDI agent flow, and the connections to LLM providers.

---

## C4 — System Context

```text
┌─────────────────────────────────────────────────────────────────┐
│                         LUMIA Studio                            │
│                                                                 │
│  User ──► Streamlit UI ──► Agent Pages ──► Utils ──► Data       │
│                                    │                            │
│                                    ▼                            │
│                          ┌─────────────────┐                   │
│                          │   LLM Providers  │                   │
│                          │  Google Gemini   │                   │
│                          │  OpenAI GPT      │                   │
│                          └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## C4 — Container Diagram

```text
┌──────────────────────────────────────────────────────────────────────┐
│  LUMIA Studio (Streamlit App)                                        │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  0_Compass   │  │   1_Knol     │  │    2_Ali     │               │
│  │  Session Mgmt│  │  Knowledge   │  │  Desires     │               │
│  │  BDI Dashboard│  │  Base Builder│  │  Extraction  │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                  │                       │
│  ┌──────▼─────────────────▼──────────────────▼───────┐              │
│  │              utils/ (Business Logic)               │              │
│  │                                                    │              │
│  │  LLMManager ◄──── llm_manager_config.py            │              │
│  │  SessionManager                                    │              │
│  │  ContextManager                                    │              │
│  │  DocumentProcessor ◄──── ChromaDB                  │              │
│  │  ConversationAuditor                               │              │
│  │  GeniusEngine                                      │              │
│  │  PromptsManager ◄──── prompts/*.md                 │              │
│  └──────────────────────────┬─────────────────────────┘              │
│                             │                                        │
│  ┌──────────────────────────▼─────────────────────────┐              │
│  │                data/ (Persistence)                  │              │
│  │  sessions/{id}/current_bdi.json                     │              │
│  │  contexts/{name}/chroma_db/                         │              │
│  │  bdi_frameworks/*.json                              │              │
│  │  genius_plans/plan_*.json                           │              │
│  └────────────────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

## BDI Cognitive Model — Data Flow

```text
Documents ──► Knol (Chunking+Embedding) ──► ChromaDB
                                               │
                                               ▼ RAG retrieval
                 Alì (Socratic Conversation) ──► Desires → current_bdi.json
                                               │
                 Believer (RAG + Extraction) ───► Beliefs → current_bdi.json
                                               │
                 Cuma (WIP Planning) ───────────► Intentions → current_bdi.json
                                               │
Compass (Export) ────────────────────────────► bdi_frameworks/*.json
                                               │
Genius (Execution Coaching) ─────────────────► genius_plans/plan_*.json
```

---

← [Previous: Architectural Overview](01-architectural-overview.md) | [Back to Index](index.md) | Next: [Core Architectural Components →](03-core-architectural-components.md)

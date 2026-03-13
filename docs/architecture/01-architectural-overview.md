# 1. Architectural Overview

← [Back to Index](index.md)

---

**LUMIA Studio** (Learning Unified Model for Intelligent Agents) is an AI-powered knowledge engineering platform that transforms unstructured documents into structured strategic insights using the **BDI (Belief-Desire-Intention)** cognitive framework.

## Guiding Principles

| Principle | Implementation |
|-----------|---------------|
| **Separation of Concerns** | Pages handle UI/interaction; `utils/` handles all business logic — no Streamlit imports in `utils/` |
| **Single Responsibility** | Each manager class has one domain (session, context, document, LLM, plan) |
| **Lazy Initialization** | Heavy components (LLM client, embeddings, ChromaDB) are initialized only on first use |
| **LRU-Cached Prompts** | System prompts loaded from Markdown files with `@lru_cache` to avoid repeated disk I/O |
| **Filesystem as Database** | JSON files for structured data; ChromaDB for vector embeddings — no external RDBMS |
| **Provider Abstraction** | `LLMManager` is the single entry point for all LLM calls, hiding Gemini vs. OpenAI specifics |
| **BDI Cognitive Model** | All agents map to one BDI layer: Alì→Desires, Believer→Beliefs, Cuma/Genius→Intentions |

## Architectural Pattern

**Layered Multi-Agent Architecture** with a RAG (Retrieval-Augmented Generation) pipeline:

```
┌──────────────────────────────────────────────────────┐
│           PRESENTATION LAYER (pages/)                │
│  Compass  │  Knol  │  Alì  │  Believer  │  Genius   │
└──────────────────────┬───────────────────────────────┘
                       │ calls
┌──────────────────────▼───────────────────────────────┐
│           BUSINESS LOGIC LAYER (utils/)              │
│  LLMManager │ SessionManager │ DocumentProcessor      │
│  ContextManager │ Auditor │ GeniusEngine │ Prompts    │
└──────────────────────┬───────────────────────────────┘
                       │ reads/writes
┌──────────────────────▼───────────────────────────────┐
│           PERSISTENCE LAYER (data/)                  │
│  sessions/ (JSON) │ contexts/ (JSON + ChromaDB)       │
│  bdi_frameworks/ (JSON) │ genius_plans/ (JSON)        │
└──────────────────────────────────────────────────────┘
```

---

← [Back to Index](index.md) | Next: [Architecture Visualization →](02-architecture-visualization.md)

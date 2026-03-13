# 14. Architectural Decision Records

← [Back to Index](index.md)

---

## ADR-001: Streamlit as Application Framework

**Context**: Need a rapid-development Python web framework for a multi-page AI application.

**Decision**: Use Streamlit with multi-page app convention (`pages/` directory).

**Consequences**:
- (+) Extremely fast development for data/AI apps
- (+) Built-in session state, widgets, chat UI components
- (-) No async support; LLM calls block the UI thread
- (-) Single-user only (one Streamlit instance per user)
- (-) Stateless-by-design requires `st.session_state` workarounds for persistence

---

## ADR-002: Filesystem as Primary Database

**Context**: Need persistent storage for sessions, BDI data, and knowledge bases.

**Decision**: JSON files for structured data; ChromaDB for vector embeddings. No relational database.

**Consequences**:
- (+) Zero infrastructure setup
- (+) Human-readable data (JSON)
- (+) Easy backup/export (zip the `data/` directory)
- (-) No ACID transactions; concurrent writes could corrupt data
- (-) No query capabilities beyond what the managers implement
- (-) ChromaDB file locks on Windows require explicit cleanup

---

## ADR-003: LLMManager as Single Provider Abstraction

**Context**: Need to support multiple LLM providers (Gemini, OpenAI) without scattering provider-specific logic across pages.

**Decision**: `LLMManager` class with a single `chat()` method as the entry point.

**Consequences**:
- (+) Pages are provider-agnostic
- (+) Easy to add new providers
- (+) Centralized RAG context injection
- (-) Large switch statement inside LLMManager as providers grow

---

## ADR-004: BDI Cognitive Framework as Core Data Model

**Context**: Need a structured way to capture knowledge from unstructured documents.

**Decision**: Adopt the Beliefs-Desires-Intentions (BDI) agent model as the domain model.

**Consequences**:
- (+) Clear semantic structure for knowledge capture
- (+) Natural pipeline: Documents→Beliefs, Conversation→Desires, Planning→Intentions
- (+) Enables actionable output (Genius execution plans)
- (-) Adds cognitive overhead for non-expert users

---

## ADR-005: Markdown Files for System Prompts

**Context**: System prompts are long, frequently iterated, and benefit from rich text editing.

**Decision**: Store prompts as `.md` files in `prompts/` with LRU caching in Python.

**Consequences**:
- (+) Prompts can be edited without touching Python code
- (+) LRU cache avoids repeated disk I/O
- (+) Supports versioning prompts alongside code in Git
- (-) Cache must be manually invalidated after editing (`clear_cache()`)

---

## ADR-006: Italian-First UI

**Context**: Initial deployment target is Italian-speaking domain experts.

**Decision**: UI strings and agent prompts are in Italian; embedding model is multilingual.

**Consequences**:
- (+) Better user experience for target audience
- (+) Multilingual embedding model handles Italian documents natively
- (-) Limits adoption beyond Italian-speaking users without translation effort

---

← [Previous: Architectural Pattern Examples](13-architectural-pattern-examples.md) | [Back to Index](index.md) | Next: [Blueprint for New Development →](15-blueprint-for-new-development.md)

# 4. Architectural Layers and Dependencies

← [Back to Index](index.md)

---

## Layer Dependency Rules

```
pages/  ──► utils/  ──► data/
  │                       ▲
  └───────────────────────┘ (read/write JSON + ChromaDB)
```

**Strict Rules**:
1. `pages/` MAY import from `utils/` — ✅
2. `pages/` MUST NOT import from other `pages/` — ❌
3. `utils/` MUST NOT import from `pages/` — ❌ (no Streamlit imports in utils/)
4. `utils/` MAY import from other `utils/` — ✅ (e.g., `auditor.py` uses `llm_manager.py`)
5. All data access goes through the appropriate manager class — ✅

## Dependency Graph (`utils/`)

```
pages/* ──► llm_manager.py ◄── llm_manager_config.py
         ──► session_manager.py
         ──► context_manager.py
         ──► document_processor.py ◄── context_manager.py (path resolution)
         ──► auditor.py ──► llm_manager.py, prompts.py
         ──► genius_engine.py ──► llm_manager.py, prompts.py
         ──► prompts.py
         ──► ui_messages.py
```

---

← [Previous: Core Architectural Components](03-core-architectural-components.md) | [Back to Index](index.md) | Next: [Data Architecture →](05-data-architecture.md)

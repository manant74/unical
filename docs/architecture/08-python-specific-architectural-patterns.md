# 8. Python-Specific Architectural Patterns

← [Back to Index](index.md)

---

## Module Organization

```python
# utils/__init__.py — explicit re-exports for clean imports
from utils.session_manager import SessionManager
from utils.llm_manager import LLMManager
# etc.
```

## Lazy Initialization with `st.session_state`

```python
# Heavy objects initialized once, stored in session state
if 'llm_manager' not in st.session_state:
    from utils.llm_manager import LLMManager
    st.session_state.llm_manager = LLMManager()

if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor(context_name=ctx)
    st.session_state.doc_processor.initialize_db()
```

## LRU Cache for Prompts

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _load_prompt_from_file(agent_name, prompt_suffix) -> str:
    path = f"prompts/{agent_name}_{prompt_suffix}.md"
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

## OOP Manager Pattern

All business logic components are classes with clear ownership:
- `SessionManager` owns `data/sessions/`
- `ContextManager` owns `data/contexts/`
- `GeniusEngine` owns `data/bdi_frameworks/` + `data/genius_plans/`
- `DocumentProcessor` owns ChromaDB for one context

## Dependency Injection (Manual)

Pages explicitly instantiate and pass managers; no DI container:
```python
session_manager = SessionManager()
context_manager = ContextManager()
doc_processor = DocumentProcessor(context_name=selected_context)
```

---

← [Previous: Service Communication Patterns](07-service-communication-patterns.md) | [Back to Index](index.md) | Next: [Implementation Patterns →](09-implementation-patterns.md)

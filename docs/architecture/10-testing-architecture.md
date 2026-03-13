# 10. Testing Architecture

← [Back to Index](index.md)

---

**Current State**: No test suite (known technical debt).

## Recommended Testing Approach (when added)

| Layer | Test Type | Scope |
|-------|-----------|-------|
| `utils/llm_manager.py` | Unit + Integration | Mock providers; test routing logic |
| `utils/session_manager.py` | Integration | Temp directories; test CRUD |
| `utils/document_processor.py` | Integration | Real ChromaDB in tmp dir; test full pipeline |
| `utils/auditor.py` | Unit | Mock LLM; test rubric scoring logic |
| `pages/` | E2E (Streamlit) | Streamlit testing library |

## Testing Boundaries

- `utils/` classes are **easily unit-testable** (no Streamlit dependency)
- Pages require Streamlit test runner or manual testing
- LLM calls should be mocked in unit tests to control cost/latency

---

← [Previous: Implementation Patterns](09-implementation-patterns.md) | [Back to Index](index.md) | Next: [Deployment Architecture →](11-deployment-architecture.md)

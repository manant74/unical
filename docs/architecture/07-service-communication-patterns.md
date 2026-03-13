# 7. Service Communication Patterns

← [Back to Index](index.md)

---

## Intra-App Communication

All communication is **synchronous and in-process**. No message queues, no HTTP between components.

| Pattern | Usage |
|---------|-------|
| **Direct method call** | Pages call manager class methods |
| **Streamlit session state** | State passing between rerenders on same page |
| **Filesystem** | Data sharing between pages (BDI JSON, belief base) |

## LLM API Communication

- **Gemini**: `google-generativeai` SDK → `GenerativeModel.generate_content()`
- **OpenAI**: `openai` SDK → `client.chat.completions.create()`
- **Blocking I/O**: All LLM calls block the Streamlit render thread
- **UX Pattern**: `st.spinner()` with `ui_messages.py` random messages during LLM calls

## RAG Retrieval Pattern

```
User input ──► DocumentProcessor.query(text, top_k=5)
                        │
                        ▼
              ChromaDB similarity search (cosine)
                        │
                        ▼
              Top-k chunks returned as List[Dict]
                        │
                        ▼
              Chunks concatenated as RAG context string
                        │
                        ▼
              Prepended to first message in LLM call
```

---

← [Previous: Cross-Cutting Concerns](06-cross-cutting-concerns.md) | [Back to Index](index.md) | Next: [Python-Specific Architectural Patterns →](08-python-specific-architectural-patterns.md)

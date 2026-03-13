# 6. Cross-Cutting Concerns

← [Back to Index](index.md)

---

## Authentication & Authorization

- **Pattern**: None (single-user only by design)
- **Scope**: One Streamlit instance per user; no authentication, no concurrency
- **Known Gap**: Multi-user support requires auth layer addition

## Error Handling & Resilience

- **LLM Errors**: Wrapped in try/except in each page; shown via `st.error()`
- **ChromaDB Errors**: Manual cleanup via `release_connections()` prevents file lock issues
- **Missing Session**: Pages enforce mandatory active session with `st.stop()` pattern
- **Missing API Keys**: LLMManager returns available providers based on environment variables

```python
# Mandatory session guard (every agent page)
if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("No active session. Please create a session in Compass.")
    st.stop()
```

## Logging & Monitoring

- **UX Feedback**: Spinner messages from `utils/ui_messages.py` (sci-fi themed thinking messages)
- **No structured logging**: No file-based or external logging system
- **Known Gap**: No observability, tracing, or metrics

## Validation

- **BDI JSON Validation**: Code editor in Compass validates JSON before save
- **LLM Input Validation**: None (trusts well-formed messages)
- **Belief Finalization**: Auditor evaluates quality before user can finalize

## Configuration Management

- **Environment Variables**: `.env` file via `python-dotenv` (API keys)
- **Session Config**: Per-session LLM settings stored in `config.json`
- **Model Parameters**: Metadata-driven in `llm_manager_config.py`
- **Feature Configuration**: No feature flags; functionality is hard-coded per page

---

← [Previous: Data Architecture](05-data-architecture.md) | [Back to Index](index.md) | Next: [Service Communication Patterns →](07-service-communication-patterns.md)

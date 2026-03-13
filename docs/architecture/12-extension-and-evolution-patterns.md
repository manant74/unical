# 12. Extension and Evolution Patterns

← [Back to Index](index.md)

---

## Adding a New Agent (Page)

1. **Create system prompt**: `prompts/{agent}_system_prompt.md`
2. **Create page**: `pages/N_{Agent}.py` with mandatory session guard
3. **Register prompt**: Add to `PromptsManager` supported agents list
4. **Update homepage**: Add feature card to `app.py`

**Page Template**:
```python
import streamlit as st
from utils.session_manager import SessionManager
from utils.llm_manager import LLMManager
from utils.prompts import get_prompt

# Session guard
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("No active session. Please create a session in Compass.")
    st.stop()

session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
system_prompt = get_prompt('{agent}')

# Agent logic here...
```

## Adding a New LLM Provider

1. Add provider initialization in `LLMManager.__init__()`
2. Add `_chat_{provider}()` method
3. Add `use_defaults` config in `llm_manager_config.py`
4. Update `get_available_providers()` and `get_models_for_provider()`
5. Update Compass UI provider selection if needed

## Adding a New Document Type

1. Add `process_{type}(file)` method to `DocumentProcessor`
2. Return `List[str]` (chunks) following the existing pattern
3. Add file type to Knol's upload widget `type` parameter

## Extending the BDI Data Model

1. Update `current_bdi.json` schema (add fields to `save_bdi_data()` defaults)
2. Update Compass BDI editor tabs to display/edit new fields
3. Ensure backward compatibility with existing sessions (check for key existence)
4. Update export logic in Compass and GeniusEngine if Genius consumes new fields

## Adding an Auditor for a New Module

1. Create `prompts/{module}_auditor_system_prompt.md` with rubric dimensions
2. Add module recognition in `ConversationAuditor.evaluate_response()`
3. Add finalization keywords in `ConversationAuditor.detect_finalization()`

---

← [Previous: Deployment Architecture](11-deployment-architecture.md) | [Back to Index](index.md) | Next: [Architectural Pattern Examples →](13-architectural-pattern-examples.md)

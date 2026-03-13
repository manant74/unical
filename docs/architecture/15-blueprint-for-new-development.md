# 15. Blueprint for New Development

← [Back to Index](index.md)

---

## Development Workflow

### Adding a New Feature (General)

1. Identify the architectural layer: UI (`pages/`), business logic (`utils/`), or data schema
2. Read existing code in the relevant layer before writing new code
3. For new utils: create a class with a clear ownership domain
4. For new pages: use the session guard template + lazy manager init pattern
5. For new prompts: create `.md` file, register in `PromptsManager`
6. Test manually by running `streamlit run app.py`

### Starting Points by Feature Type

| Feature Type | Starting Point |
|-------------|---------------|
| New agent/page | Create `pages/N_AgentName.py` + `prompts/agentname_system_prompt.md` |
| New LLM provider | `utils/llm_manager.py` + `utils/llm_manager_config.py` |
| New document type | `utils/document_processor.py` → add `process_{type}()` |
| BDI schema extension | `utils/session_manager.py` defaults + `pages/0_Compass.py` editor |
| New visualization | `pages/0_Compass.py` BDI graph section (pyvis) |
| New belief extraction mode | `pages/3_Believer.py` + corresponding prompt file |

---

## Implementation Templates

### New Manager Class

```python
# utils/new_manager.py
import json
import os
from typing import Dict, List, Optional


class NewManager:
    """Manages [domain description]."""

    BASE_DIR = "data/new_domain"

    def __init__(self):
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def create_item(self, name: str) -> str:
        """Create a new item. Returns item_id."""
        item_id = str(uuid.uuid4())
        item_path = os.path.join(self.BASE_DIR, item_id)
        os.makedirs(item_path, exist_ok=True)

        metadata = {"id": item_id, "name": name, "created_at": datetime.now().isoformat()}
        self._save_json(os.path.join(item_path, "metadata.json"), metadata)

        return item_id

    def get_item(self, item_id: str) -> Optional[Dict]:
        metadata_path = os.path.join(self.BASE_DIR, item_id, "metadata.json")
        if not os.path.exists(metadata_path):
            return None
        return self._load_json(metadata_path)

    @staticmethod
    def _load_json(path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _save_json(path: str, data: Dict) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

### New Agent Page

```python
# pages/N_NewAgent.py
import streamlit as st
import random
from utils.session_manager import SessionManager
from utils.llm_manager import LLMManager
from utils.prompts import get_prompt
from utils import ui_messages

# ── 1. Session guard ──────────────────────────────────────────────────────────
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'active_session' not in st.session_state or not st.session_state.active_session:
    all_sessions = st.session_state.session_manager.get_all_sessions(status="active")
    if all_sessions:
        latest = max(all_sessions, key=lambda s: s['metadata'].get('last_accessed', ''))
        st.session_state.active_session = latest['session_id']

if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("No active session. Please create a session in Compass.")
    st.stop()

session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
session_config = session_data['config']

# ── 2. Lazy manager init ──────────────────────────────────────────────────────
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

# ── 3. Load system prompt (cached) ───────────────────────────────────────────
SYSTEM_PROMPT = get_prompt('new_agent')

# ── 4. Chat state ─────────────────────────────────────────────────────────────
if 'new_agent_messages' not in st.session_state:
    st.session_state.new_agent_messages = []

# ── 5. Page UI ────────────────────────────────────────────────────────────────
st.title("New Agent")

for msg in st.session_state.new_agent_messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if user_input := st.chat_input("Type here..."):
    st.session_state.new_agent_messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(random.choice(ui_messages.THINKING_MESSAGES)):
            response = st.session_state.llm_manager.chat(
                provider=session_config['llm_provider'],
                model=session_config['llm_model'],
                messages=st.session_state.new_agent_messages,
                system_prompt=SYSTEM_PROMPT
            )
        st.markdown(response)

    st.session_state.new_agent_messages.append({"role": "assistant", "content": response})
```

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| Importing Streamlit in `utils/` | Never import `streamlit` in utils/ files |
| Not releasing ChromaDB | Always call `release_connections()` in a `finally` block |
| Modifying prompts without clearing cache | Call `clear_cache()` after editing `.md` files in development |
| Using relative paths for data access | Always use `os.path.join()` from project root |
| Forgetting session guard | Every agent page MUST start with the session guard pattern |
| Using `ensure_ascii=True` | Always use `ensure_ascii=False` for Italian/multilingual content |
| Creating sessions without context | Sessions require a valid context for RAG to work in Believer |
| Passing `max_tokens` to reasoning models | Check `MODEL_PARAMETERS` in `llm_manager_config.py` first |

---

*This blueprint was generated on 2026-03-13. Update this document when:*
- *New agents or pages are added*
- *New LLM providers or models are added*
- *The BDI data model schema changes*
- *New utilities or managers are introduced*
- *Architectural decisions are made that change the above patterns*

---

← [Previous: Architectural Decision Records](14-architectural-decision-records.md) | [Back to Index](index.md)

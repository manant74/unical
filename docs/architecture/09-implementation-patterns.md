# 9. Implementation Patterns

← [Back to Index](index.md)

---

## Pattern 1: Session State Initialization (Every Agent Page)

```python
# Top of every agent page
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
```

## Pattern 2: Chat Loop with Auditor Feedback

```python
# 1. Get user input
user_input = st.chat_input("...")
if user_input:
    # 2. Append to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 3. Retrieve RAG context
    chunks = doc_processor.query(user_input, top_k=5)
    rag_context = "\n".join([c['text'] for c in chunks])

    # 4. Call LLM
    with st.spinner(random.choice(ui_messages.THINKING_MESSAGES)):
        response = llm_manager.chat(
            provider=session_config['llm_provider'],
            model=session_config['llm_model'],
            messages=st.session_state.chat_history,
            system_prompt=system_prompt,
            context=rag_context
        )

    # 5. Append response
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # 6. Run auditor
    feedback = auditor.evaluate_response(response, context={...}, module="ali")
    suggestions = auditor.generate_suggestions(feedback)

    # 7. Render quick-reply suggestions
    render_quick_replies(suggestions_placeholder, suggestions, "pending_input", "btn")

    # 8. Detect finalization and extract/save JSON
    if auditor.detect_finalization(user_input, module="ali"):
        bdi_data = extract_json_from_response(response)
        session_manager.save_bdi_data(session_id, bdi_data)
```

## Pattern 3: JSON Persistence

```python
# Safe read
def load_json(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Safe write
def save_json(path: str, data: Dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## Pattern 4: DocumentProcessor Lifecycle

```python
# Initialize once
processor = DocumentProcessor(context_name="my_context")
processor.initialize_db()

try:
    # Use
    chunks = processor.process_pdf(uploaded_file)
    processor.add_documents(chunks, source="report.pdf")
    results = processor.query("user query", top_k=5)
finally:
    # ⚠️ Always release (prevents ChromaDB file locks on Windows)
    processor.release_connections()
```

## Pattern 5: Quick-Reply Buttons

```python
def render_quick_replies(placeholder, suggestions, pending_state_key, button_prefix):
    placeholder.empty()
    with placeholder:
        for i in range(0, len(suggestions), 3):
            row = suggestions[i:i + 3]
            cols = st.columns(len(row))
            for col_idx, (col, suggestion) in enumerate(zip(cols, row)):
                with col:
                    if st.button(suggestion['label'], key=f"{button_prefix}_{i+col_idx}", width='stretch'):
                        st.session_state[pending_state_key] = suggestion['message']
                        st.rerun()
```

## Pattern 6: Modal JSON Editor (Streamlit Dialog)

```python
@st.dialog("JSON Editor", width="large")
def json_editor_modal(data_path: str):
    with open(data_path, 'r', encoding='utf-8') as f:
        current_data = json.load(f)

    response = code_editor(
        code=json.dumps(current_data, indent=2),
        lang="json",
        theme="default"
    )

    if st.button("Save", type="primary") and response.get('text'):
        try:
            parsed = json.loads(response['text'])
            save_json(data_path, parsed)
            st.success("Saved successfully!")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
```

---

← [Previous: Python-Specific Architectural Patterns](08-python-specific-architectural-patterns.md) | [Back to Index](index.md) | Next: [Testing Architecture →](10-testing-architecture.md)

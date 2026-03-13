# 13. Architectural Pattern Examples

← [Back to Index](index.md)

---

## Example 1: Full LLM Call Chain

```python
# In a page (e.g., 2_Ali.py)
from utils.llm_manager import LLMManager
from utils.document_processor import DocumentProcessor
from utils.prompts import get_prompt

# Load system prompt (cached)
system_prompt = get_prompt('ali')

# Initialize (lazy, once per session)
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor(context_name=ctx_normalized)
    st.session_state.doc_processor.initialize_db()

# On user input
relevant_chunks = st.session_state.doc_processor.query(user_input, top_k=5)
rag_context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])

response = st.session_state.llm_manager.chat(
    provider=session_config['llm_provider'],
    model=session_config['llm_model'],
    messages=st.session_state.ali_chat_history,
    system_prompt=system_prompt,
    context=rag_context,             # <-- RAG injected here
    temperature=session_config.get('llm_settings', {}).get('temperature', 0.7)
)
```

## Example 2: Document Ingestion Pipeline

```python
# In 1_Knol.py
processor = DocumentProcessor(context_name=normalized_context)
processor.initialize_db()

try:
    if uploaded_file.type == "application/pdf":
        chunks = processor.process_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        chunks = processor.process_text(uploaded_file)

    processor.add_documents(chunks, source=uploaded_file.name)

    # Update metadata
    context_manager.update_context_metadata(normalized_context, {
        'document_count': current_count + 1,
        'updated_at': datetime.now().isoformat()
    })
finally:
    processor.release_connections()  # ⚠️ Always release
```

## Example 3: BDI Export → Genius Workflow

```python
# In 0_Compass.py — export current session BDI as reusable framework
def export_as_framework(session_id: str):
    bdi_data = session_manager.get_bdi_data(session_id)
    domain = bdi_data.get('domain_summary', 'unnamed').replace(' ', '_')[:50]

    framework_path = f"data/bdi_frameworks/{domain}_bdi.json"
    os.makedirs("data/bdi_frameworks", exist_ok=True)
    with open(framework_path, 'w', encoding='utf-8') as f:
        json.dump(bdi_data, f, indent=2, ensure_ascii=False)

    return framework_path

# In 6_Genius.py — load and use the framework
frameworks = genius_engine.load_bdi_frameworks()
selected_bdi = genius_engine.load_bdi(selected_filename)
filtered_beliefs = genius_engine.filter_beliefs_by_relevance(selected_bdi, threshold='ALTO')
plan = genius_engine.generate_plan(selected_desire, user_profile, selected_bdi)
plan_id = genius_engine.save_plan(plan)
```

---

← [Previous: Extension and Evolution Patterns](12-extension-and-evolution-patterns.md) | [Back to Index](index.md) | Next: [Architectural Decision Records →](14-architectural-decision-records.md)

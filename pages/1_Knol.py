import streamlit as st
import os
import sys
import json
from code_editor import code_editor

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.context_manager import ContextManager

st.set_page_config(
    page_title="Knol - LumIA Studio",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza il context manager
if 'context_manager' not in st.session_state:
    st.session_state.context_manager = ContextManager()

# Inizializza il contesto corrente (può essere None se non ce n'è uno selezionato)
if 'current_context' not in st.session_state:
    # Prova a caricare il contesto attivo dalle impostazioni
    contexts = st.session_state.context_manager.get_all_contexts()
    if contexts:
        st.session_state.current_context = contexts[0]['normalized_name']
    else:
        st.session_state.current_context = None

# Inizializza il document processor solo se c'è un contesto selezionato
if 'doc_processor' not in st.session_state or st.session_state.get('context_changed', False):
    if st.session_state.current_context:
        st.session_state.doc_processor = DocumentProcessor(
            context_name=st.session_state.current_context
        )
        st.session_state.doc_processor.initialize_db()
        st.session_state.context_changed = False
    else:
        st.session_state.doc_processor = None

# LLMManager non viene inizializzato qui - viene caricato lazy quando serve (Estrai Belief)

# Inizializza flag per modale editor
if 'show_belief_editor' not in st.session_state:
    st.session_state.show_belief_editor = False

# Funzione helper per caricare i belief base
def load_belief_count():
    """Returns the number of beliefs stored in the active context's belief base.

    Reads ``belief_base.json`` from the path provided by ``ContextManager``
    only when a context is selected.  The file is opened on every call (no
    Streamlit cache) to always reflect the latest on-disk state.

    Returns:
        int: Number of beliefs in the ``beliefs_base`` array.
            Returns ``0`` when no context is selected, the file does not
            exist, or any read / parse error occurs.
    """
    if not st.session_state.current_context:
        return 0

    belief_base_path = st.session_state.context_manager.get_belief_base_path(
        st.session_state.current_context
    )

    if not os.path.exists(belief_base_path):
        return 0

    try:
        with open(belief_base_path, 'r', encoding='utf-8') as f:
            belief_base = json.load(f)
            return len(belief_base.get('beliefs_base', []))
    except:
        return 0

# Funzione dialog per editor beliefs
@st.dialog("📝 Beliefs Editor", width="large")
def belief_editor_modal():
    """Opens a full-screen modal for editing the active context's belief base as JSON.

    The modal loads the current ``belief_base.json``, presents it in a
    syntax-highlighted code editor (VSCode shortcuts), and exposes four
    actions:

    * **Validate** – parses the JSON and reports the belief count.
    * **Save** – writes the edited JSON back to disk and updates
      context metadata.
    * **Clear All** – replaces the belief base with an empty array
      (requires a second click for confirmation).
    * **Close** – discards unsaved changes and closes the dialog.

    The function mutates ``st.session_state`` directly: it clears
    ``show_belief_editor`` on save / close and triggers ``st.rerun()``.

    Raises:
        No exceptions are raised; all errors are caught and displayed
        via ``st.error``.
    """

    # Carica belief base
    belief_base_path = st.session_state.context_manager.get_belief_base_path(
        st.session_state.current_context
    )

    beliefs = []
    if os.path.exists(belief_base_path):
        try:
            with open(belief_base_path, 'r', encoding='utf-8') as f:
                belief_data = json.load(f)
                beliefs = belief_data.get('beliefs_base', belief_data.get('beliefs', []))
        except Exception as e:
            st.error(f"Error loading beliefs: {str(e)}")
            beliefs = []

    # Prepara JSON per l'editor
    beliefs_json = json.dumps({"beliefs_base": beliefs}, indent=2, ensure_ascii=False)

    st.markdown("**Edit beliefs in JSON format**")
    st.caption("💡 You can edit, add, or remove beliefs directly in the JSON below")

    # Code editor
    response = code_editor(
        code=beliefs_json,
        lang="json",
        height=[30, 40],
        theme="default",
        shortcuts="vscode",
        allow_reset=True,
        options={
            "wrap": True,
            "showLineNumbers": True,
            "highlightActiveLine": True,
            "fontSize": 14,
        }
    )

    # Estrai il testo editato
    if response and 'text' in response and response['text'].strip():
        edited_json = response['text']
    else:
        edited_json = beliefs_json

    st.divider()

    # Pulsanti di azione
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Validate JSON", width='stretch'):
            try:
                parsed = json.loads(edited_json)
                if 'beliefs_base' in parsed and isinstance(parsed['beliefs_base'], list):
                    st.success(f"✅ Valid JSON! {len(parsed['beliefs_base'])} beliefs found.")
                else:
                    st.error("❌ JSON must contain a 'beliefs_base' array")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {str(e)}")

    with col2:
        if st.button("💾 Save", width='stretch', type="primary"):
            try:
                parsed = json.loads(edited_json)
                if 'beliefs_base' in parsed and isinstance(parsed['beliefs_base'], list):
                    # Salva nel file
                    with open(belief_base_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed, f, ensure_ascii=False, indent=2)

                    # Aggiorna metadata
                    belief_count = len(parsed['beliefs_base'])
                    st.session_state.context_manager.update_context_metadata(
                        st.session_state.current_context,
                        {'belief_count': belief_count}
                    )

                    st.success(f"✅ Beliefs saved! ({belief_count} beliefs)")
                    st.session_state.show_belief_editor = False
                    st.rerun()
                else:
                    st.error("❌ JSON must contain a 'beliefs_base' array")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {str(e)}")
            except Exception as e:
                st.error(f"❌ Save error: {str(e)}")

    with col3:
        if st.button("🗑️ Cancella Tutto", width='stretch'):
            if st.session_state.get('confirm_clear_beliefs_modal', False):
                # Conferma e cancella
                empty_data = {"beliefs_base": []}
                with open(belief_base_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, ensure_ascii=False, indent=2)

                st.session_state.context_manager.update_context_metadata(
                    st.session_state.current_context,
                    {'belief_count': 0}
                )
                st.session_state.confirm_clear_beliefs_modal = False
                st.success("✅ Tutti i beliefs sono stati cancellati!")
                st.rerun()
            else:
                # Prima richiesta di conferma
                st.session_state.confirm_clear_beliefs_modal = True
                st.warning("⚠️ Clicca di nuovo per confermare la cancellazione")

    with col4:
        if st.button("❌ Chiudi", width='stretch'):
            st.session_state.show_belief_editor = False
            st.session_state.confirm_clear_beliefs_modal = False
            st.rerun()

    # Info
    st.divider()
    st.caption(f"📊 Beliefs attuali: {len(beliefs)}")

# CSS per nascondere menu Streamlit e styling
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}

    /* Riduce spessore delle righe di divisione */
    hr {
        margin: 0.1 rem 0;
        border: none;
        border-top: 0.5px solid rgba(49, 51, 63, 0.2);
    }

    /* Divider nella sidebar */
    section[data-testid="stSidebar"] hr {
        margin: 0.2rem 0;
        border-top: 0.5px solid rgba(49, 51, 63, 0.15);
    }

    /* Riduce spazio superiore del titolo della pagina */
    .block-container {
        padding-top: 2rem !important;
    }

</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    # Header con logo e pulsante home sulla stessa riga
    col_logo, col_home = st.columns([3, 1])

    with col_logo:
        st.markdown("<div style='padding-top: 0px;'><h2>✨ LumIA Studio</h2></div>", unsafe_allow_html=True)

    with col_home:
        if st.button("🏠", width='stretch', type="secondary", help="Back to Home"):
            st.switch_page("app.py")

    st.divider()

    # Sezione lista contesti
    st.markdown("### 📋 Available Contexts")

    contexts = st.session_state.context_manager.get_all_contexts()

    if not contexts:
        st.info("No context available. Create one!")
    else:
        for idx, ctx in enumerate(contexts):
            is_active = ctx['normalized_name'] == st.session_state.current_context

            # Container per ogni contesto
            with st.container():
                # Prima riga: Nome contesto con pulsanti laterali
                col_name, col_activate, col_delete = st.columns([4, 1.3, 1.3])

                with col_name:
                    # Nome del contesto come punto elenco (allineato verticalmente)
                    icon = "🟢" if is_active else "⚪"
                    st.markdown(f"<div style='padding-top: 4px;'><strong>{icon} {ctx['name']}</strong></div>",
                               unsafe_allow_html=True)

                with col_activate:
                    # Pulsante attiva (usa sempre stessa emoji, disabilitato se attivo)
                    if st.button("⚡", key=f"activate_{ctx['normalized_name']}",
                               help="Active context" if is_active else "Activate context",
                               disabled=is_active, width='stretch'):
                        st.session_state.current_context = ctx['normalized_name']
                        st.session_state.context_changed = True
                        st.rerun()

                with col_delete:
                    # Pulsante elimina
                    if st.button("🗑️", key=f"delete_{ctx['normalized_name']}",
                               help="Delete context", width='stretch'):
                        if st.session_state.context_manager.delete_context(ctx['normalized_name']):
                            st.success(f"Context '{ctx['name']}' deleted!")
                            # Se era il contesto corrente, deselezionalo
                            if st.session_state.current_context == ctx['normalized_name']:
                                remaining = st.session_state.context_manager.get_all_contexts()
                                st.session_state.current_context = remaining[0]['normalized_name'] if remaining else None
                                st.session_state.context_changed = True
                            st.rerun()
                        else:
                            st.error("Deletion error")

                # Seconda riga: Descrizione del contesto (con spazio ridotto)
                testo =" "
                if ctx.get('description'):
                    testo = f"{ctx['description']}"
                else:
                    testo ="Nessuna descrizione"

                testo = (f"{testo} (📦 Chunks: {ctx.get('document_count', 0)} | 🧠 Beliefs: {ctx.get('belief_count', 0)}")

                st.markdown(testo)

            # Riga divisoria tra i contesti (tranne dopo l'ultimo)
            if idx < len(contexts) - 1:
                st.markdown("---")

    st.divider()

    # Sezione creazione nuovo contesto
    st.markdown("### ➕ New Context")

    with st.form("new_context_form", clear_on_submit=True):
        new_context_name = st.text_input("Context name", placeholder="e.g. Project X")
        new_context_desc = st.text_area("Description (optional)", placeholder="Brief context description...")
        create_btn = st.form_submit_button("Create Context", width='stretch', type="primary")

        if create_btn and new_context_name:
            try:
                metadata = st.session_state.context_manager.create_context(
                    name=new_context_name,
                    description=new_context_desc
                )
                st.success(f"✅ Context '{new_context_name}' created!")
                # Seleziona automaticamente il nuovo contesto
                st.session_state.current_context = metadata['normalized_name']
                st.session_state.context_changed = True
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Creation error: {str(e)}")

    st.divider()

    # Statistiche globali
    st.markdown("### 📊 Global Statistics")
    global_stats = st.session_state.context_manager.get_global_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Contesti", global_stats['total_contexts'])
    with col2:
        st.metric("Chunks", global_stats['total_documents'])

    st.divider()

    # Funzionalità avanzate
    st.markdown("### ⚙️ Funzioni Avanzate")

    # Export contesto
    if st.session_state.current_context:
        if st.button("📦 Esporta Contesto", width='stretch'):
            try:
                export_path = f"./exports/{st.session_state.current_context}.zip"
                os.makedirs("./exports", exist_ok=True)
                if st.session_state.context_manager.export_context(
                    st.session_state.current_context,
                    export_path
                ):
                    st.success(f"✅ Contesto esportato in {export_path}")
                else:
                    st.error("❌ Errore nell'export")
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")

    # Import contesto
    uploaded_zip = st.file_uploader("📥 Importa Contesto (ZIP)", type=['zip'], key="import_context")
    if uploaded_zip:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp.write(uploaded_zip.read())
                tmp_path = tmp.name

            metadata = st.session_state.context_manager.import_context(tmp_path)
            if metadata:
                st.success(f"✅ Contesto '{metadata['name']}' importato!")
                os.unlink(tmp_path)
                st.rerun()
            else:
                st.error("❌ Errore nell'import")
                os.unlink(tmp_path)
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

# ===== MAIN CONTENT =====

# Header
st.title("📚 Knol")
st.markdown("**Gestisci contesti multipli e crea knowledge base specializzate**")

# Verifica se c'è un contesto selezionato
if not st.session_state.current_context:
    st.warning("⚠️ Nessun contesto selezionato. Crea o seleziona un contesto dalla sidebar per iniziare!")
    st.stop()

# Mostra informazioni contesto corrente
current_ctx = st.session_state.context_manager.get_context(st.session_state.current_context)
if current_ctx:
    st.info(f"🟢 **Contesto attivo:** {current_ctx['name']}" +
            (f" - {current_ctx['description']}" if current_ctx.get('description') else ""))

st.divider()

# Carica statistiche una volta sola
stats = st.session_state.doc_processor.get_stats()
sources = st.session_state.doc_processor.get_all_sources()

# Layout a due colonne
col1, col2 = st.columns([1.5, 1])

with col1:
    # Stato della Knowledge Base
    st.markdown("#### 📊 Stato Knowledge Base")
    # Metriche principali in row orizzontale
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Chunks", stats['document_count'])
    with metric_col2:
        st.metric("Fonti", len(sources))
    with metric_col3:
        belief_count = load_belief_count()
        st.metric("Beliefs", belief_count)
    with metric_col4:
        # Valuta altri KPI
        avg_chunks_per_source = round(stats['document_count'] / len(sources), 1) if sources else 0
        st.metric("Chunk/Fonte", avg_chunks_per_source)

    st.divider()

    st.markdown("#### 📤 Load Sources")

    # Tabs per diversi tipi di input
    tab1, tab2, tab3, tab4 = st.tabs(["📕 PDF", "🌐 Web Pages", "📑 Text Files", "📋 Markdown"])

    with tab1:
        st.markdown("Load PDF files to extract text content")
        pdf_files = st.file_uploader(
            "Select PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_uploader"
        )

        if pdf_files and st.button("Process PDF", key="process_pdf"):
            with st.spinner("Processing PDF files..."):
                for pdf_file in pdf_files:
                    try:
                        chunks = st.session_state.doc_processor.process_pdf(pdf_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"PDF: {pdf_file.name}"
                        )
                        st.success(f"✅ {pdf_file.name} processed successfully ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Error processing {pdf_file.name}: {str(e)}")

    with tab2:
        st.markdown("Enter web page URLs to extract content")
        url_input = st.text_input("Web page URL", placeholder="https://example.com")

        if url_input and st.button("Load from Web", key="process_url"):
            with st.spinner(f"Loading {url_input}..."):
                try:
                    chunks = st.session_state.doc_processor.process_url(url_input)
                    st.session_state.doc_processor.add_documents(
                        chunks,
                        source=f"Web: {url_input}"
                    )
                    st.success(f"✅ Web page loaded successfully ({len(chunks)} chunks)")

                    # Aggiorna il conteggio documenti nel metadata
                    stats = st.session_state.doc_processor.get_stats()
                    st.session_state.context_manager.update_context_metadata(
                        st.session_state.current_context,
                        {'document_count': stats['document_count']}
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with tab3:
        st.markdown("Load text files (.txt)")
        txt_files = st.file_uploader(
            "Select text files",
            type=['txt'],
            accept_multiple_files=True,
            key="txt_uploader"
        )

        if txt_files and st.button("Process Text Files", key="process_txt"):
            with st.spinner("Processing text files..."):
                for txt_file in txt_files:
                    try:
                        chunks = st.session_state.doc_processor.process_text(txt_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"TXT: {txt_file.name}"
                        )
                        st.success(f"✅ {txt_file.name} processed successfully ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Error processing {txt_file.name}: {str(e)}")

    with tab4:
        st.markdown("Load Markdown files (.md)")
        md_files = st.file_uploader(
            "Select Markdown files",
            type=['md'],
            accept_multiple_files=True,
            key="md_uploader"
        )

        if md_files and st.button("Process Markdown", key="process_md"):
            with st.spinner("Processing Markdown files..."):
                for md_file in md_files:
                    try:
                        chunks = st.session_state.doc_processor.process_text(md_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"MD: {md_file.name}"
                        )
                        st.success(f"✅ {md_file.name} processed successfully ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Error processing {md_file.name}: {str(e)}")

    # Suggerimento
    st.markdown("---")
    st.markdown("💡 **Tip**: After loading sources, extract the Belief Base and proceed to **Alì** to define your Desires.")
    # Pulsanti per estrarre belief base, editor e cancellare contesto
    st.markdown("---")

    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        extract_belief = st.button("🧠 Extract Beliefs", width='stretch')

    with btn_col2:
        edit_belief = st.button("📝 Edit Beliefs", width='stretch')

    with btn_col3:
        clear_context = st.button("🗑️ Clear KB", type="secondary", width='stretch')


with col2:
    st.markdown("##### 📄 Loaded Sources")

    # Lista dei contenuti caricati dal database
    if sources:
        for idx, source in enumerate(sources, 1):
            # Determina il tipo dal prefisso della source
            if source.startswith("PDF:"):
                icon = "📕"
                source_type = "PDF"
                name = source.replace("PDF: ", "")
            elif source.startswith("Web:"):
                icon = "🌐"
                source_type = "Web"
                name = source.replace("Web: ", "")
            elif source.startswith("TXT:"):
                icon = "📑"
                source_type = "Text"
                name = source.replace("TXT: ", "")
            elif source.startswith("MD:"):
                icon = "📋"
                source_type = "Markdown"
                name = source.replace("MD: ", "")
            else:
                icon = "📄"
                source_type = "Unknown"
                name = source

            with st.expander(f"{icon} {source_type}: {name}"):
                st.caption(f"**Source ID:** {source}")
    else:
        st.info("📭 No sources loaded yet")

    # Logica per estrazione belief base
    if extract_belief:
        if stats['document_count'] > 0:
            with st.spinner("Estrazione dei belief di base in corso..."):
                try:
                    # STEP 1: Verifica se la descrizione del contesto è vuota
                    context_metadata = st.session_state.context_manager.get_context(
                        st.session_state.current_context
                    )

                    generate_description = False
                    if not context_metadata.get('description') or context_metadata.get('description').strip() == '':
                        generate_description = True
                        st.info("📝 Generating context description...")

                    # Recupera tutti i documenti dalla knowledge base
                    all_docs = st.session_state.doc_processor.collection.get()

                    # Concatena tutti i documenti
                    context = "\n\n---\n\n".join(all_docs['documents'])

                    # Chiama l'LLM (usa il primo provider disponibile)
                    # Lazy load LLMManager solo quando necessario
                    if 'llm_manager' not in st.session_state:
                        from utils.llm_manager import LLMManager
                        st.session_state.llm_manager = LLMManager()

                    available_providers = st.session_state.llm_manager.get_available_providers()
                    if not available_providers:
                        st.error("❌ Nessun provider LLM configurato. Verifica le API keys.")
                    else:
                        provider = available_providers[0]
                        #provider='OpenAI'
                        # Rimosso print che non dava output su Streamlit; seleziona provider e modello normalmente

                        models = st.session_state.llm_manager.get_models_for_provider(provider)
                        model = list(models.keys())[2]
                        #model = 'GPT-5'

                        # STEP 2: Genera descrizione contesto se necessario
                        if generate_description:
                            sources = st.session_state.doc_processor.get_all_sources()
                            sources_list = "\n".join([f"- {source}" for source in sources])

                            description_prompt = f"""Analizza i seguenti titoli/nomi di documenti caricati nella knowledge base e genera una descrizione concisa del contesto in esattamente 20 parole che sintetizza il tema principale.
                            Documenti:
                            {sources_list}
                            Rispondi SOLO con la descrizione (20 parole esatte), senza JSON o altri formati."""

                            description_response = st.session_state.llm_manager.chat(
                                provider=provider,
                                model=model,
                                messages=[{"role": "user", "content": description_prompt}],
                                system_prompt="Sei un assistente che analizza documenti e genera descrizioni concise."
                            )

                            # Salva la descrizione nel metadata
                            description = description_response.strip()
                            st.session_state.context_manager.update_context_metadata(
                                st.session_state.current_context,
                                {'description': description}
                            )
                            st.success(f"✅ Descrizione generata: {description}")

                        # STEP 3: Estrai belief base
                        st.info("🧠 Estrazione belief di base...")

                        # Carica il prompt per i belief base
                        prompt_path = "./prompts/belief_base_prompt.md"
                        with open(prompt_path, 'r', encoding='utf-8') as f:
                            belief_base_prompt = f.read()

                        # Prepara il messaggio per l'LLM
                        user_message = f"Analizza la seguente base di conoscenza ed estrai tutti i belief di base secondo le istruzioni fornite.\n\nBASE DI CONOSCENZA:\n{context}"

                        response = st.session_state.llm_manager.chat(
                            provider=provider,
                            model=model,
                            messages=[{"role": "user", "content": user_message}],
                            system_prompt=belief_base_prompt
                        )

                        # Estrai il JSON dalla risposta
                        json_start = response.find('{')
                        json_end = response.rfind('}') + 1

                        if json_start != -1 and json_end > json_start:
                            json_str = response[json_start:json_end]
                            try:
                                belief_base = json.loads(json_str)

                                # Verifica che abbia la chiave richiesta
                                if 'beliefs_base' not in belief_base:
                                    st.error("❌ Errore: JSON non contiene la chiave 'beliefs_base'")
                                    st.code(json_str[:500])
                                else:
                                    # Salva nel file belief_base.json del contesto
                                    belief_base_path = st.session_state.context_manager.get_belief_base_path(
                                        st.session_state.current_context
                                    )
                                    with open(belief_base_path, 'w', encoding='utf-8') as f:
                                        json.dump(belief_base, f, ensure_ascii=False, indent=2)

                                    # Aggiorna il conteggio nel metadata
                                    belief_count = len(belief_base.get('beliefs_base', []))
                                    st.session_state.context_manager.update_context_metadata(
                                        st.session_state.current_context,
                                        {'belief_count': belief_count}
                                    )

                                    st.success(f"✅ Belief Base extracted successfully! {belief_count} beliefs identified.")
                                    st.rerun()
                            except json.JSONDecodeError as e:
                                st.error(f"❌ JSON parsing error: {str(e)}")
                                st.warning("Showing first 1000 characters of response for debugging:")
                                st.code(response[:1000])
                        else:
                            st.error("❌ Error: LLM response does not contain valid JSON (no '{' or '}' found)")
                            st.warning("Showing complete response:")
                            st.code(response)

                except Exception as e:
                    st.error(f"❌ Error extracting beliefs: {e}")
        else:
            st.warning("⚠️ Load some documents into the knowledge base first!")

    # Logica per aprire editor beliefs
    if edit_belief:
        st.session_state.show_belief_editor = True
        st.rerun()

    # Logica per cancellare knowledge base del contesto
    if clear_context:
        if stats['document_count'] > 0:
            try:
                # Rilascia le connessioni e cancella il database
                st.session_state.doc_processor.clear_database()

                # Cancella anche il file belief base se esiste
                belief_base_path = st.session_state.context_manager.get_belief_base_path(
                    st.session_state.current_context
                )
                if os.path.exists(belief_base_path):
                    try:
                        os.remove(belief_base_path)
                    except Exception as e:
                        st.warning(f"⚠️ Cannot delete belief_base.json: {e}")

                # Forza la re-inizializzazione del DocumentProcessor
                st.session_state.doc_processor = DocumentProcessor(
                    context_name=st.session_state.current_context
                )
                st.session_state.doc_processor.initialize_db()

                # Aggiorna i metadata
                st.session_state.context_manager.update_context_metadata(
                    st.session_state.current_context,
                    {'document_count': 0, 'belief_count': 0}
                )

                st.success("✅ Knowledge Base cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Deletion error: {str(e)}")
        else:
            st.info("No content to delete")

# Apri modale editor se richiesto
if st.session_state.show_belief_editor:
    belief_editor_modal()
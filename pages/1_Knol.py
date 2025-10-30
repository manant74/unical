import streamlit as st
import os
import sys
import json

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.context_manager import ContextManager
from utils.llm_manager import LLMManager

st.set_page_config(
    page_title="Knol - LUMIA Studio",
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

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

# CSS per nascondere menu Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### ✨ LUMIA Studio")

    if st.button("🏠 Torna alla Home", width='stretch', type="secondary"):
        st.switch_page("app.py")

    st.divider()

    # Sezione creazione nuovo contesto
    st.markdown("### ➕ Nuovo Contesto")

    with st.form("new_context_form", clear_on_submit=True):
        new_context_name = st.text_input("Nome del contesto", placeholder="es. Progetto X")
        new_context_desc = st.text_area("Descrizione (opzionale)", placeholder="Breve descrizione del contesto...")
        create_btn = st.form_submit_button("Crea Contesto", use_container_width=True, type="primary")

        if create_btn and new_context_name:
            try:
                metadata = st.session_state.context_manager.create_context(
                    name=new_context_name,
                    description=new_context_desc
                )
                st.success(f"✅ Contesto '{new_context_name}' creato!")
                # Seleziona automaticamente il nuovo contesto
                st.session_state.current_context = metadata['normalized_name']
                st.session_state.context_changed = True
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Errore nella creazione: {str(e)}")

    st.divider()

    # Sezione lista contesti
    st.markdown("### 📋 Contesti Disponibili")

    contexts = st.session_state.context_manager.get_all_contexts()

    if not contexts:
        st.info("Nessun contesto disponibile. Creane uno!")
    else:
        for ctx in contexts:
            is_active = ctx['normalized_name'] == st.session_state.current_context

            # Container per ogni contesto
            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Indicatore contesto attivo
                    icon = "🟢" if is_active else "⚪"
                    if st.button(
                        f"{icon} {ctx['name']}",
                        key=f"select_{ctx['normalized_name']}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        if not is_active:
                            st.session_state.current_context = ctx['normalized_name']
                            st.session_state.context_changed = True
                            st.rerun()

                with col2:
                    # Pulsante elimina
                    if st.button("🗑️", key=f"delete_{ctx['normalized_name']}", help="Elimina contesto"):
                        if st.session_state.context_manager.delete_context(ctx['normalized_name']):
                            st.success(f"Contesto '{ctx['name']}' eliminato!")
                            # Se era il contesto corrente, deselezionalo
                            if st.session_state.current_context == ctx['normalized_name']:
                                remaining = st.session_state.context_manager.get_all_contexts()
                                st.session_state.current_context = remaining[0]['normalized_name'] if remaining else None
                                st.session_state.context_changed = True
                            st.rerun()
                        else:
                            st.error("Errore nell'eliminazione")

                # Mostra info del contesto se attivo
                if is_active:
                    st.caption(f"📦 Chunks: {ctx.get('document_count', 0)} | 🧠 Beliefs: {ctx.get('belief_count', 0)}")
                    if ctx.get('description'):
                        st.caption(f"📝 {ctx['description']}")

            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    st.divider()

    # Statistiche globali
    st.markdown("### 📊 Statistiche Globali")
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
        if st.button("📦 Esporta Contesto", use_container_width=True):
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

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Carica Fonti")

    # Tabs per diversi tipi di input
    tab1, tab2, tab3, tab4 = st.tabs(["📕 PDF", "🌐 Pagine Web", "📑 File di Testo", "📋 Markdown"])

    with tab1:
        st.markdown("Carica file PDF per estrarre il contenuto testuale")
        pdf_files = st.file_uploader(
            "Seleziona file PDF",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_uploader"
        )

        if pdf_files and st.button("Processa PDF", key="process_pdf"):
            with st.spinner("Elaborazione dei file PDF in corso..."):
                for pdf_file in pdf_files:
                    try:
                        chunks = st.session_state.doc_processor.process_pdf(pdf_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"PDF: {pdf_file.name}"
                        )
                        st.success(f"✅ {pdf_file.name} processato con successo ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Errore durante l'elaborazione di {pdf_file.name}: {str(e)}")

    with tab2:
        st.markdown("Inserisci URL di pagine web per estrarre il contenuto")
        url_input = st.text_input("URL della pagina web", placeholder="https://esempio.com")

        if url_input and st.button("Carica da Web", key="process_url"):
            with st.spinner(f"Caricamento di {url_input}..."):
                try:
                    chunks = st.session_state.doc_processor.process_url(url_input)
                    st.session_state.doc_processor.add_documents(
                        chunks,
                        source=f"Web: {url_input}"
                    )
                    st.success(f"✅ Pagina web caricata con successo ({len(chunks)} chunks)")

                    # Aggiorna il conteggio documenti nel metadata
                    stats = st.session_state.doc_processor.get_stats()
                    st.session_state.context_manager.update_context_metadata(
                        st.session_state.current_context,
                        {'document_count': stats['document_count']}
                    )
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")

    with tab3:
        st.markdown("Carica file di testo (.txt)")
        txt_files = st.file_uploader(
            "Seleziona file di testo",
            type=['txt'],
            accept_multiple_files=True,
            key="txt_uploader"
        )

        if txt_files and st.button("Processa File di Testo", key="process_txt"):
            with st.spinner("Elaborazione dei file di testo..."):
                for txt_file in txt_files:
                    try:
                        chunks = st.session_state.doc_processor.process_text(txt_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"TXT: {txt_file.name}"
                        )
                        st.success(f"✅ {txt_file.name} processato con successo ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Errore durante l'elaborazione di {txt_file.name}: {str(e)}")

    with tab4:
        st.markdown("Carica file Markdown (.md)")
        md_files = st.file_uploader(
            "Seleziona file Markdown",
            type=['md'],
            accept_multiple_files=True,
            key="md_uploader"
        )

        if md_files and st.button("Processa Markdown", key="process_md"):
            with st.spinner("Elaborazione dei file Markdown..."):
                for md_file in md_files:
                    try:
                        chunks = st.session_state.doc_processor.process_text(md_file)
                        st.session_state.doc_processor.add_documents(
                            chunks,
                            source=f"MD: {md_file.name}"
                        )
                        st.success(f"✅ {md_file.name} processato con successo ({len(chunks)} chunks)")

                        # Aggiorna il conteggio documenti nel metadata
                        stats = st.session_state.doc_processor.get_stats()
                        st.session_state.context_manager.update_context_metadata(
                            st.session_state.current_context,
                            {'document_count': stats['document_count']}
                        )
                    except Exception as e:
                        st.error(f"❌ Errore durante l'elaborazione di {md_file.name}: {str(e)}")

    # Test della ricerca
    st.markdown("---")
    st.markdown(" ")
    st.subheader("🔍 Test sulla Knowledge Base")

    col_test1, col_test2 = st.columns([3, 1])

    with col_test1:
        query = st.text_input(
            "Prova a cercare qualcosa nella tua Knowledge Base",
            placeholder="Inserisci una query di test..."
        )

    with col_test2:
        n_results = st.number_input("N. risultati", min_value=1, max_value=10, value=3)

    if query and st.button("Cerca", key="search_btn"):
        stats = st.session_state.doc_processor.get_stats()
        if stats['document_count'] > 0:
            with st.spinner("Ricerca in corso..."):
                results = st.session_state.doc_processor.query(query, n_results=n_results)

                if results and results['documents'] and results['documents'][0]:
                    st.markdown("**Risultati trovati:**")
                    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                        with st.expander(f"Risultato {i} - {metadata.get('source', 'Unknown')}"):
                            st.write(doc)
                else:
                    st.warning("Nessun risultato trovato")
        else:
            st.warning("⚠️ Carica prima alcuni documenti nella base di conoscenza!")

with col2:
    st.markdown("##### 📊 Stato Knowledge Base")

    # Statistiche del contesto corrente
    stats = st.session_state.doc_processor.get_stats()
    sources = st.session_state.doc_processor.get_all_sources()

    # Calcola belief count
    belief_base_path = st.session_state.context_manager.get_belief_base_path(st.session_state.current_context)
    belief_count = 0
    if os.path.exists(belief_base_path):
        try:
            with open(belief_base_path, 'r', encoding='utf-8') as f:
                belief_base = json.load(f)
                belief_count = len(belief_base.get('beliefs_base', []))
        except:
            belief_count = 0

    # Metriche
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Chunks", stats['document_count'])
    with metric_col2:
        st.metric("Fonti", len(sources))
    with metric_col3:
        st.metric("Beliefs", belief_count)

    # Lista dei contenuti caricati dal database
    if sources:
        st.markdown("---")
        st.markdown("##### 📄 Fonti Caricate")
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

    # Pulsanti per estrarre belief base e cancellare contesto
    st.markdown(" ")
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        extract_belief = st.button("🧠 Estrai Belief", use_container_width=True)

    with btn_col2:
        clear_context = st.button("🗑️ Cancella KB", type="secondary", use_container_width=True)

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
                        st.info("📝 Generazione descrizione del contesto...")

                    # Recupera tutti i documenti dalla knowledge base
                    all_docs = st.session_state.doc_processor.collection.get()

                    # Concatena tutti i documenti
                    context = "\n\n---\n\n".join(all_docs['documents'])

                    # Chiama l'LLM (usa il primo provider disponibile)
                    available_providers = st.session_state.llm_manager.get_available_providers()
                    if not available_providers:
                        st.error("❌ Nessun provider LLM configurato. Verifica le API keys.")
                    else:
                        provider = available_providers[0]
                        models = st.session_state.llm_manager.get_models_for_provider(provider)
                        model = list(models.keys())[0]

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
                            belief_base = json.loads(json_str)

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

                            st.success(f"✅ Belief Base estratta con successo! {belief_count} belief individuati.")
                            st.rerun()
                        else:
                            st.error("❌ Errore: risposta LLM non contiene JSON valido")
                            st.code(response)

                except Exception as e:
                    st.error(f"❌ Errore durante l'estrazione dei belief: {str(e)}")
        else:
            st.warning("⚠️ Carica prima alcuni documenti nella base di conoscenza!")

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
                        st.warning(f"⚠️ Impossibile cancellare belief_base.json: {e}")

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

                st.success("✅ Knowledge Base cancellata con successo!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Errore durante la cancellazione: {str(e)}")
        else:
            st.info("Nessun contenuto da cancellare")

# Suggerimento
st.markdown("---")
st.markdown("💡 **Suggerimento**: Dopo aver caricato le fonti, estrai i Belief Base e passa ad **Alì** per definire i tuoi Desire.")
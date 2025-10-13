import streamlit as st
import os
import sys

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor

st.set_page_config(
    page_title="Contextual - LUMIA Studio",
    page_icon="📚",
    layout="wide"
)

# Inizializza il session state
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
    st.session_state.doc_processor.initialize_db()

if 'uploaded_files_info' not in st.session_state:
    st.session_state.uploaded_files_info = []

# CSS per nascondere menu Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    
</style>
""", unsafe_allow_html=True)

# Header con pulsante Home
col_title, col_home = st.columns([5, 1])
with col_title:
    st.title("📚 Contextual")
    st.markdown("**Crea la tua base di conoscenza caricando documenti, pagine web e file di testo**")
with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

st.divider()

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Carica Documenti")

    # Tabs per diversi tipi di input
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF", "🌐 Pagine Web", "📝 File di Testo", "📋 Markdown"])

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
                        st.session_state.uploaded_files_info.append({
                            "type": "PDF",
                            "name": pdf_file.name,
                            "chunks": len(chunks)
                        })
                        st.success(f"✅ {pdf_file.name} processato con successo ({len(chunks)} chunks)")
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
                    st.session_state.uploaded_files_info.append({
                        "type": "Web",
                        "name": url_input,
                        "chunks": len(chunks)
                    })
                    st.success(f"✅ Pagina web caricata con successo ({len(chunks)} chunks)")
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
                        st.session_state.uploaded_files_info.append({
                            "type": "TXT",
                            "name": txt_file.name,
                            "chunks": len(chunks)
                        })
                        st.success(f"✅ {txt_file.name} processato con successo ({len(chunks)} chunks)")
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
                        st.session_state.uploaded_files_info.append({
                            "type": "Markdown",
                            "name": md_file.name,
                            "chunks": len(chunks)
                        })
                        st.success(f"✅ {md_file.name} processato con successo ({len(chunks)} chunks)")
                    except Exception as e:
                        st.error(f"❌ Errore durante l'elaborazione di {md_file.name}: {str(e)}")

with col2:
    st.subheader("📊 Stato della Base di Conoscenza")

    # Statistiche
    stats = st.session_state.doc_processor.get_stats()

    st.metric("Contenuti nel Database", stats['document_count'])
    st.metric("File Caricati", len(st.session_state.uploaded_files_info))

    # Lista dei file caricati
    if st.session_state.uploaded_files_info:
        st.markdown("---")
        st.markdown("**File Caricati:**")
        for idx, file_info in enumerate(st.session_state.uploaded_files_info, 1):
            with st.expander(f"{file_info['type']}: {file_info['name']}"):
                st.write(f"Chunks: {file_info['chunks']}")

    # Pulsante per cancellare tutto
    st.markdown("---")
    if st.button("🗑️ Cancella Contesto", type="secondary", use_container_width=True):
        if st.session_state.uploaded_files_info:
            st.session_state.doc_processor.clear_database()
            st.session_state.uploaded_files_info = []

            # Cancella anche il file current_context.json se esiste
            context_file = "./data/current_context.json"
            if os.path.exists(context_file):
                try:
                    os.remove(context_file)
                except Exception as e:
                    st.warning(f"⚠️ Impossibile cancellare current_context.json: {e}")

            st.success("✅ Contesto cancellato con successo!")
            st.rerun()
        else:
            st.info("Nessun contesto da cancellare")

# Test della ricerca
st.markdown("---")
st.subheader("🔍 Test della Base di Conoscenza")

col_test1, col_test2 = st.columns([3, 1])

with col_test1:
    query = st.text_input(
        "Prova a cercare qualcosa nella tua base di conoscenza",
        placeholder="Inserisci una query di test..."
    )

with col_test2:
    n_results = st.number_input("N. risultati", min_value=1, max_value=10, value=3)

if query and st.button("Cerca", key="search_btn"):
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

# Suggerimento
st.markdown("---")
st.markdown("💡 **Suggerimento**: Dopo aver caricato i documenti, passa ad **Alì** per iniziare a definire i tuoi Desire.")

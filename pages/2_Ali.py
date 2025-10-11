import streamlit as st
import os
import sys
import json
from datetime import datetime

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.llm_manager import LLMManager
from utils.prompts import get_prompt

st.set_page_config(
    page_title="Alì - BDI Framework",
    page_icon="🎯",
    layout="wide"
)

# Inizializza il session state
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
    st.session_state.doc_processor.initialize_db()

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

if 'ali_chat_history' not in st.session_state:
    st.session_state.ali_chat_history = []
    st.session_state.ali_greeted = False

if 'desires' not in st.session_state:
    st.session_state.desires = []

# Carica il system prompt da file
ALI_SYSTEM_PROMPT = get_prompt('ali')

# Sidebar per configurazione
with st.sidebar:
    # Pulsante Home in alto
    st.markdown("### 🧠 BDI Framework")
    if st.button("🏠 Torna alla Home", use_container_width=True, type="secondary"):
        st.switch_page("app.py")

    st.divider()

    # Configurazione
    st.header("⚙️ Configurazione Alì")

    # Selezione provider e modello
    available_providers = st.session_state.llm_manager.get_available_providers()

    if not available_providers:
        st.error("⚠️ Nessun provider LLM disponibile!")
        st.info("Configura le API keys nel file .env:\n- GOOGLE_API_KEY\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY")
        provider = None
    else:
        provider = st.selectbox(
            "Provider LLM",
            available_providers,
            key="ali_provider"
        )

        if provider:
            models = st.session_state.llm_manager.get_models_for_provider(provider)
            model = st.selectbox(
                "Modello",
                options=list(models.keys()),
                format_func=lambda x: models[x],
                key="ali_model"
            )

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    if st.button("🔄 Nuova Conversazione", use_container_width=True):
        st.session_state.ali_chat_history = []
        st.session_state.ali_greeted = False
        st.rerun()

    if st.button("✅ Completa Sessione", type="primary", use_container_width=True):
        if st.session_state.desires:
            # Salva i desires
            desires_data = {
                "timestamp": datetime.now().isoformat(),
                "desires": st.session_state.desires,
                "chat_history": st.session_state.ali_chat_history
            }

            os.makedirs("./data/sessions", exist_ok=True)
            filename = f"./data/sessions/desires_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(desires_data, f, ensure_ascii=False, indent=2)

            # Salva anche come file corrente
            with open("./data/current_desires.json", 'w', encoding='utf-8') as f:
                json.dump(desires_data, f, ensure_ascii=False, indent=2)

            st.success(f"✅ Sessione completata! Desires salvati in:\n{filename}")
            st.balloons()
        else:
            st.warning("⚠️ Nessun desire identificato ancora!")

    st.divider()

    # Visualizza desires
    if st.session_state.desires:
        st.subheader("🎯 Desire Identificati")
        for desire in st.session_state.desires:
            with st.expander(f"#{desire['id']}: {desire['description'][:30]}..."):
                st.json(desire)

    # Spacer per spingere le statistiche in basso
    st.markdown("<br>" * 5, unsafe_allow_html=True)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistiche")
    st.metric("Messaggi", len(st.session_state.ali_chat_history))
    st.metric("Desire Identificati", len(st.session_state.desires))

    stats = st.session_state.doc_processor.get_stats()
    st.metric("Documenti in KB", stats['document_count'])

# Main content
st.title("🎯 Alì - Agent for Desires")
st.markdown("**Benvenuto! Sono qui per aiutarti a identificare e definire i tuoi Desire**")
st.divider()

# Check se la KB è vuota
kb_stats = st.session_state.doc_processor.get_stats()
if kb_stats['document_count'] == 0:
    st.warning("⚠️ La base di conoscenza è vuota! Vai a Contextual per caricare documenti prima di iniziare.")
    if st.button("📚 Vai a Contextual"):
        st.switch_page("pages/1_Contextual.py")
    st.stop()

# Check provider disponibile
if not available_providers or provider is None:
    st.error("❌ Nessun provider LLM configurato. Configura le API keys per continuare.")
    st.stop()

# Saluto iniziale
if not st.session_state.ali_greeted:
    greeting = "Ciao! Sono Alì e sono qui per aiutarti a trovare i tuoi Desire. 🎯\n\nHo accesso alla tua base di conoscenza e posso aiutarti a identificare obiettivi chiari e raggiungibili nel tuo dominio. Dimmi, cosa vuoi ottenere?"
    st.session_state.ali_chat_history.append({
        "role": "assistant",
        "content": greeting
    })
    st.session_state.ali_greeted = True

# Display chat history
for message in st.session_state.ali_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Scrivi il tuo messaggio..."):
    # Add user message
    st.session_state.ali_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get context from RAG
    with st.spinner("Sto pensando..."):
        try:
            # Query the knowledge base
            rag_results = st.session_state.doc_processor.query(prompt, n_results=3)

            context = ""
            if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                context = "\n\n".join(rag_results['documents'][0])

            # Get response from LLM
            response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=st.session_state.ali_chat_history,
                system_prompt=ALI_SYSTEM_PROMPT,
                context=context if context else None
            )

            # Add assistant response
            st.session_state.ali_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            # Check if a desire was mentioned (simple heuristic)
            if any(keyword in response.lower() for keyword in ["desire identificato", "registriamo", "aggiungiamo questo desire"]):
                st.info("💡 Sembra che abbiamo identificato un desire! Puoi confermarlo usando il pannello laterale.")

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

# Sezione di aiuto
st.markdown("---")
st.markdown("💡 **Suggerimento**: Usa la sidebar per configurare il provider LLM, gestire la sessione e visualizzare le statistiche.")

# Quick action: Add desire manually
with st.expander("➕ Aggiungi Desire Manualmente"):
    st.markdown("Compila i campi per aggiungere un desire manualmente")

    desire_desc = st.text_area("Descrizione", key="manual_desire_desc")
    desire_priority = st.selectbox("Priorità", ["high", "medium", "low"], key="manual_desire_priority")
    desire_context = st.text_area("Contesto", key="manual_desire_context")
    desire_criteria = st.text_area("Criteri di Successo", key="manual_desire_criteria")

    if st.button("Aggiungi Desire"):
        if desire_desc:
            new_desire = {
                "id": len(st.session_state.desires) + 1,
                "description": desire_desc,
                "priority": desire_priority,
                "context": desire_context,
                "success_criteria": desire_criteria,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.desires.append(new_desire)
            st.success("✅ Desire aggiunto!")
            st.rerun()
        else:
            st.warning("⚠️ Inserisci almeno una descrizione")

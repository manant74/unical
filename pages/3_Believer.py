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
    page_title="Believer - BDI Framework",
    page_icon="💡",
    layout="wide"
)

# Inizializza il session state
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
    st.session_state.doc_processor.initialize_db()

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

if 'believer_chat_history' not in st.session_state:
    st.session_state.believer_chat_history = []
    st.session_state.believer_greeted = False

if 'beliefs' not in st.session_state:
    st.session_state.beliefs = []

if 'loaded_desires' not in st.session_state:
    st.session_state.loaded_desires = None

# Carica il system prompt da file
BELIEVER_SYSTEM_PROMPT = get_prompt('believer')

# Carica i desires se disponibili
def load_desires():
    """Carica i desires dal file salvato"""
    try:
        if os.path.exists("./data/current_desires.json"):
            with open("./data/current_desires.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('desires', [])
    except Exception as e:
        st.error(f"Errore nel caricamento dei desires: {str(e)}")
    return None

# Sidebar per configurazione
with st.sidebar:
    # Pulsante Home in alto
    st.markdown("### 🧠 BDI Framework")
    if st.button("🏠 Torna alla Home", use_container_width=True, type="secondary"):
        st.switch_page("app.py")

    st.divider()

    # Configurazione
    st.header("⚙️ Configurazione Believer")

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
            key="believer_provider"
        )

        if provider:
            models = st.session_state.llm_manager.get_models_for_provider(provider)
            model = st.selectbox(
                "Modello",
                options=list(models.keys()),
                format_func=lambda x: models[x],
                key="believer_model"
            )

    st.divider()

    # Carica desires
    if st.session_state.loaded_desires is None:
        st.session_state.loaded_desires = load_desires()

    if st.session_state.loaded_desires:
        st.success(f"✅ {len(st.session_state.loaded_desires)} Desire caricati")

        with st.expander("🎯 Desires Disponibili"):
            for desire in st.session_state.loaded_desires:
                st.markdown(f"**#{desire['id']}**: {desire['description']}")
    else:
        st.warning("⚠️ Nessun desire trovato!")

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    if st.button("🔄 Nuova Conversazione", use_container_width=True):
        st.session_state.believer_chat_history = []
        st.session_state.believer_greeted = False
        st.rerun()

    if st.button("✅ Completa Sessione", type="primary", use_container_width=True):
        if st.session_state.beliefs:
            # Crea il JSON finale con desires e beliefs
            final_data = {
                "timestamp": datetime.now().isoformat(),
                "desires": st.session_state.loaded_desires or [],
                "beliefs": st.session_state.beliefs,
                "chat_history": st.session_state.believer_chat_history
            }

            os.makedirs("./data/sessions", exist_ok=True)
            filename = f"./data/sessions/bdi_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)

            # Salva anche come file corrente
            with open("./data/current_bdi.json", 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)

            st.success(f"✅ Sessione completata! BDI salvato in:\n{filename}")
            st.balloons()
        else:
            st.warning("⚠️ Nessun belief identificato ancora!")

    st.divider()

    # Visualizza beliefs
    if st.session_state.beliefs:
        st.subheader("💡 Belief Identificati")
        for belief in st.session_state.beliefs:
            with st.expander(f"#{belief['id']}: {belief['description'][:30]}..."):
                st.json(belief)

    # Spacer per spingere le statistiche in basso
    st.markdown("<br>" * 5, unsafe_allow_html=True)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistiche")
    st.metric("Messaggi", len(st.session_state.believer_chat_history))
    st.metric("Belief Identificati", len(st.session_state.beliefs))

    stats = st.session_state.doc_processor.get_stats()
    st.metric("Documenti in KB", stats['document_count'])

# Main content
st.title("💡 Believer - Agent for Beliefs")
st.markdown("**Benvenuto! Sono Believer e sono qui per aiutarti a individuare i Belief**")
st.divider()

# Check prerequisites
kb_stats = st.session_state.doc_processor.get_stats()
if kb_stats['document_count'] == 0:
    st.warning("⚠️ La base di conoscenza è vuota! Vai a Contextual per caricare documenti prima di iniziare.")
    if st.button("📚 Vai a Contextual"):
        st.switch_page("pages/1_Contextual.py")
    st.stop()

if not st.session_state.loaded_desires:
    st.warning("⚠️ Nessun desire trovato! Completa prima la sessione con Alì.")
    if st.button("🎯 Vai ad Alì"):
        st.switch_page("pages/2_Ali.py")
    st.stop()

if not available_providers or provider is None:
    st.error("❌ Nessun provider LLM configurato. Configura le API keys per continuare.")
    st.stop()

# Saluto iniziale
if not st.session_state.believer_greeted:
    desires_summary = "\n".join([f"- Desire #{d['id']}: {d['description']}" for d in st.session_state.loaded_desires[:3]])
    greeting = f"""Ciao! Sono Believer e sono qui per aiutarti a individuare i Belief. 💡

Ho caricato i tuoi Desire:
{desires_summary}
{"..." if len(st.session_state.loaded_desires) > 3 else ""}

Ora lavoreremo insieme per identificare le credenze, i fatti e i principi che sono rilevanti per raggiungere questi desire. Iniziamo a esplorare la tua base di conoscenza!"""

    st.session_state.believer_chat_history.append({
        "role": "assistant",
        "content": greeting
    })
    st.session_state.believer_greeted = True

# Display chat history
for message in st.session_state.believer_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Scrivi il tuo messaggio..."):
    # Add user message
    st.session_state.believer_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get context from RAG including desires
    with st.spinner("Sto analizzando..."):
        try:
            # Query the knowledge base
            rag_results = st.session_state.doc_processor.query(prompt, n_results=3)

            # Build context with KB results and desires
            context = ""

            # Add desires to context
            desires_context = "DESIRES DELL'UTENTE:\n"
            for desire in st.session_state.loaded_desires:
                desires_context += f"- Desire #{desire['id']}: {desire['description']} (Priorità: {desire.get('priority', 'N/A')})\n"

            context = desires_context + "\n\n"

            # Add KB results
            if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                kb_context = "INFORMAZIONI DALLA BASE DI CONOSCENZA:\n"
                kb_context += "\n\n".join(rag_results['documents'][0])
                context += kb_context

            # Get response from LLM
            response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=st.session_state.believer_chat_history,
                system_prompt=BELIEVER_SYSTEM_PROMPT,
                context=context if context else None
            )

            # Add assistant response
            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

# Sezione di aiuto ed export
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("💡 **Suggerimento**: Usa la sidebar per configurare il provider LLM, gestire la sessione e visualizzare le statistiche.")

with col2:
    if st.session_state.beliefs:
        export_data = {
            "desires": st.session_state.loaded_desires,
            "beliefs": st.session_state.beliefs
        }
        st.download_button(
            "📊 Esporta BDI",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"bdi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Quick action: Add belief manually
with st.expander("➕ Aggiungi Belief Manualmente"):
    st.markdown("Compila i campi per aggiungere un belief manualmente")

    belief_desc = st.text_area("Descrizione", key="manual_belief_desc")
    belief_type = st.selectbox("Tipo", ["fact", "assumption", "principle", "constraint"], key="manual_belief_type")
    belief_confidence = st.selectbox("Confidenza", ["high", "medium", "low"], key="manual_belief_confidence")

    # Multi-select per desires correlati
    desire_options = {d['id']: f"#{d['id']}: {d['description'][:50]}" for d in st.session_state.loaded_desires}
    selected_desires = st.multiselect(
        "Desires Correlati",
        options=list(desire_options.keys()),
        format_func=lambda x: desire_options[x],
        key="manual_belief_desires"
    )

    belief_evidence = st.text_area("Evidenze", key="manual_belief_evidence")

    if st.button("Aggiungi Belief"):
        if belief_desc:
            new_belief = {
                "id": len(st.session_state.beliefs) + 1,
                "description": belief_desc,
                "type": belief_type,
                "confidence": belief_confidence,
                "related_desires": selected_desires,
                "evidence": belief_evidence,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.beliefs.append(new_belief)
            st.success("✅ Belief aggiunto!")
            st.rerun()
        else:
            st.warning("⚠️ Inserisci almeno una descrizione")

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
    page_title="Alì - LUMIA Studio",
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

# CSS per nascondere menu Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    
</style>
""", unsafe_allow_html=True)

# Sidebar per configurazione
with st.sidebar:
    # Pulsante Home in alto
    st.markdown("### ✨ LUMIA Studio")
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
        # Imposta Gemini come default se disponibile
        default_provider = "Gemini" if "Gemini" in available_providers else available_providers[0]
        provider = st.selectbox(
            "Provider LLM",
            available_providers,
            index=available_providers.index(default_provider),
            key="ali_provider"
        )

        if provider:
            models = st.session_state.llm_manager.get_models_for_provider(provider)
            # Imposta Gemini 2.5 Pro come default se disponibile
            default_model = "gemini-2.5-pro" if provider == "Gemini" and "gemini-2.5-pro" in models else list(models.keys())[0]
            model = st.selectbox(
                "Modello",
                options=list(models.keys()),
                format_func=lambda x: models[x],
                index=list(models.keys()).index(default_model),
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

            st.success(f"✅ Sessione completata! {len(st.session_state.desires)} Desires salvati in:\n{filename}")
            st.balloons()
        elif len(st.session_state.ali_chat_history) > 1:
            # Se ci sono messaggi ma nessun desire estratto, salva comunque la chat
            chat_only_data = {
                "timestamp": datetime.now().isoformat(),
                "desires": [],
                "chat_history": st.session_state.ali_chat_history
            }

            os.makedirs("./data/sessions", exist_ok=True)
            filename = f"./data/sessions/desires_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_only_data, f, ensure_ascii=False, indent=2)

            with open("./data/current_desires.json", 'w', encoding='utf-8') as f:
                json.dump(chat_only_data, f, ensure_ascii=False, indent=2)

            st.warning("⚠️ Nessun desire identificato, ma la conversazione è stata salvata.")
            st.info("💡 Suggerimento: Chiedi ad Alì di generare il report finale con i desires identificati.")
        else:
            st.warning("⚠️ Nessuna conversazione da salvare!")

    st.divider()

    # Visualizza desires
    if st.session_state.desires:
        st.subheader("🎯 Desire Identificati")
        for desire in st.session_state.desires:
            with st.expander(f"#{desire['id']}: {desire['description'][:30]}..."):
                st.json(desire)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistiche")
    st.metric("Messaggi", len(st.session_state.ali_chat_history))
    st.metric("Desire Identificati", len(st.session_state.desires))

    stats = st.session_state.doc_processor.get_stats()
    st.metric("Contenuti in KB", stats['document_count'])

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

            # --- NUOVA LOGICA PER PARSARE IL JSON ---
            if response.strip().startswith("```json"):
                try:
                    # Estrai il contenuto JSON dal blocco di codice
                    json_content_str = response.strip().replace("```json", "").replace("```", "").strip()
                    
                    # Parsa il JSON
                    parsed_json = json.loads(json_content_str)

                    # Estrai i desires dal report
                    extracted_desires = []
                    if "personas" in parsed_json and isinstance(parsed_json["personas"], list):
                        for persona in parsed_json["personas"]:
                            if "desires" in persona and isinstance(persona["desires"], list):
                                for desire in persona["desires"]:
                                    extracted_desires.append({
                                        "id": desire.get("desire_id", len(st.session_state.desires) + len(extracted_desires) + 1),
                                        "description": desire.get("desire_statement", "N/A"),
                                        "priority": "medium",  # Default priority
                                        "context": f"Persona: {persona.get('persona_name', 'N/A')}",
                                        "success_criteria": "\n".join(desire.get("success_metrics", [])),
                                        "timestamp": datetime.now().isoformat()
                                    })
                    
                    if extracted_desires:
                        st.session_state.desires = extracted_desires
                        st.success(f"✅ Report finale rilevato! {len(extracted_desires)} desires sono stati estratti e caricati nella sessione.")
                        st.info("Puoi ora completare la sessione o aggiungere altri desires manualmente.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Il report JSON è stato rilevato ma non contiene desires nel formato atteso.")

                except json.JSONDecodeError:
                    st.error("❌ Il report finale JSON generato dall'agente non è valido e non può essere parsato.")
                except Exception as e:
                    st.error(f"An unexpected error occurred while parsing the report: {e}")
            # --- FINE NUOVA LOGICA ---

            # Check if a desire was mentioned (simple heuristic)
            elif any(keyword in response.lower() for keyword in ["desire identificato", "registriamo", "aggiungiamo questo desire"]):
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

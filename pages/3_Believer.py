import streamlit as st
import os
import sys
import json
from datetime import datetime
import re
# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.llm_manager import LLMManager
from utils.prompts import get_prompt

st.set_page_config(
    page_title="Believer - LUMIA Studio",
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

# CSS per nascondere solo il menu di navigazione Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

def load_desires():
    """Carica i desires dal file salvato, gestendo sia la struttura semplice che quella complessa."""
    file_path = "./data/current_desires.json"
    absolute_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        st.error(fr"""**File Non Trovato!**

        Impossibile trovare il file `current_desires.json`.

        **Percorso Controllato:** `{absolute_path}`

        **Possibili Soluzioni:**
        1.  **Verifica la Directory di Lavoro:** Assicurati di eseguire il comando `streamlit run app.py` dalla directory principale del progetto (`C:\Users\anton\workspace\unical`).
        2.  **Controlla il Nome del File:** Verifica che il file si chiami esattamente `current_desires.json` (tutto minuscolo) e si trovi nella cartella `data`.
        """)
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            st.warning(f"Il file `{file_path}` è vuoto.")
            return []

        # Controlla la struttura semplice (usata da versioni precedenti o manualmente)
        if 'desires' in data and isinstance(data['desires'], list):
            return data['desires']

        # Controlla la struttura complessa (output dell'agente Alì)
        elif 'personas' in data and isinstance(data['personas'], list):
            extracted_desires = []
            for persona in data["personas"]:
                if "desires" in persona and isinstance(persona["desires"], list):
                    for desire in persona["desires"]:
                        extracted_desires.append({
                            "id": desire.get("desire_id", f"gen_{len(extracted_desires) + 1}"),
                            "description": desire.get("desire_statement", "N/A"),
                            "priority": "medium",
                            "context": f"Persona: {persona.get('persona_name', 'N/A')}",
                            "success_criteria": "\n".join(desire.get("success_metrics", [])),
                            "timestamp": datetime.now().isoformat()
                        })
            if not extracted_desires:
                 st.warning(f"Il file `{file_path}` ha una struttura a 'personas' ma non sono stati trovati desires al suo interno.")
            return extracted_desires

        else:
            st.error(f"**Struttura JSON Non Riconosciuta!**\n\nIl file `{file_path}` non sembra contenere né una chiave 'desires' né una chiave 'personas'.")
            return None

    except json.JSONDecodeError as e:
        st.error(f"**Errore di Formato JSON!**\n\nIl file `{file_path}` contiene un errore e non può essere letto.\n\n**Dettagli:** {e}")
        return None
    except Exception as e:
        st.error(f"**Errore Inaspettato!**\n\nSi è verificato un errore durante la lettura del file: {e}")
        return None

# Sidebar per configurazione
with st.sidebar:
    # Pulsante Home in alto
    st.markdown("### 🧠 LUMIA Studio")
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
        # Imposta Gemini come default se disponibile
        default_provider = "Gemini" if "Gemini" in available_providers else available_providers[0]
        provider = st.selectbox(
            "Provider LLM",
            available_providers,
            index=available_providers.index(default_provider),
            key="believer_provider"
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
        # Il messaggio di errore/warning viene già mostrato da load_desires()
        pass

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    if st.button("🔄 Nuova Conversazione", use_container_width=True):
        st.session_state.believer_chat_history = []
        st.session_state.believer_greeted = False
        st.session_state.loaded_desires = None # Forza il ricaricamento
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

            st.success(f"✅ Sessione completata! {len(st.session_state.beliefs)} Beliefs salvati in:\n{filename}")
            st.balloons()
        elif len(st.session_state.believer_chat_history) > 1:
            # Se ci sono messaggi ma nessun belief estratto, salva comunque la chat
            chat_only_data = {
                "timestamp": datetime.now().isoformat(),
                "desires": st.session_state.loaded_desires or [],
                "beliefs": [],
                "chat_history": st.session_state.believer_chat_history
            }

            os.makedirs("./data/sessions", exist_ok=True)
            filename = f"./data/sessions/bdi_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_only_data, f, ensure_ascii=False, indent=2)

            with open("./data/current_bdi.json", 'w', encoding='utf-8') as f:
                json.dump(chat_only_data, f, ensure_ascii=False, indent=2)

            st.warning("⚠️ Nessun belief identificato, ma la conversazione è stata salvata.")
            st.info("💡 Suggerimento: Chiedi a Believer di generare il report finale con i beliefs identificati.")
        else:
            st.warning("⚠️ Nessuna conversazione da salvare!")

    st.divider()

    # Quick action: Add belief manually
    with st.expander("➕ Aggiungi Belief Manualmente"):
        st.markdown("Compila i campi per aggiungere un belief manualmente")

        belief_desc = st.text_area("Descrizione", key="manual_belief_desc")
        belief_type = st.selectbox("Tipo", ["fact", "assumption", "principle", "constraint"], key="manual_belief_type")
        belief_confidence = st.selectbox("Confidenza", ["high", "medium", "low"], key="manual_belief_confidence")

        # Multi-select per desires correlati
        if st.session_state.loaded_desires:
            desire_options = {d['id']: f"#{d['id']}: {d['description'][:50]}" for d in st.session_state.loaded_desires}
            selected_desires = st.multiselect(
                "Desires Correlati",
                options=list(desire_options.keys()),
                format_func=lambda x: desire_options[x],
                key="manual_belief_desires"
            )
        else:
            selected_desires = []

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

    # Visualizza beliefs
    if st.session_state.beliefs:
        st.subheader("💡 Belief Identificati")
        for belief in st.session_state.beliefs:
            with st.expander(f"#{belief['id']}: {belief['description'][:30]}..."):
                st.json(belief)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistiche")
    st.metric("Messaggi", len(st.session_state.believer_chat_history))
    st.metric("Belief Identificati", len(st.session_state.beliefs))

    stats = st.session_state.doc_processor.get_stats()
    st.metric("Contenuti in KB", stats['document_count'])

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
    # La funzione load_desires() viene chiamata nella sidebar e mostra già un errore se necessario
    st.warning("⚠️ Nessun desire trovato o il file non è valido. Controlla i messaggi nella sidebar.")
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
            json_match = re.search(r'```json(.*?)```', response, re.DOTALL) or re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    json_str = json_match.group(1).strip() if '```' in json_match.group(0) else json_match.group(0).strip()
                    parsed_json = json.loads(json_str)

                    extracted_beliefs = []

                    if "beliefs" in parsed_json and isinstance(parsed_json["beliefs"], list):
                        for b in parsed_json["beliefs"]:
                            description_parts = []
                            soggetto = b.get("soggetto", "")
                            relazione = b.get("relazione", "")
                            oggetto = b.get("oggetto", "")
                            if soggetto or relazione or oggetto:
                                description_parts.append(f"{soggetto} {relazione} {oggetto}".strip())
                            else:
                                description_parts.append("N/A")

                            extracted_beliefs.append({
                                "id": len(st.session_state.beliefs) + len(extracted_beliefs) + 1,
                                "description": " ".join(description_parts),
                                "type": b.get("metadati", {}).get("tipo_soggetto", "fact"),
                                "confidence": "medium",
                                "related_desires": [d.get("desire_id") for d in b.get("desires_correlati", [])],
                                "evidence": b.get("fonte", ""),
                                "timestamp": datetime.now().isoformat()
                            })

                    elif "personas" in parsed_json and isinstance(parsed_json["personas"], list):
                        for persona in parsed_json["personas"]:
                            if "beliefs" in persona and isinstance(persona["beliefs"], list):
                                for b in persona["beliefs"]:
                                    soggetto = b.get("soggetto", "")
                                    relazione = b.get("relazione", "")
                                    oggetto = b.get("oggetto", "")
                                    description = f"{soggetto} {relazione} {oggetto}".strip() or "N/A"

                                    extracted_beliefs.append({
                                        "id": len(st.session_state.beliefs) + len(extracted_beliefs) + 1,
                                        "description": description,
                                        "type": b.get("metadati", {}).get("tipo_soggetto", "fact"),
                                        "confidence": "medium",
                                        "related_desires": [d.get("desire_id") for d in b.get("desires_correlati", [])],
                                        "evidence": b.get("fonte", ""),
                                        "timestamp": datetime.now().isoformat()
                                    })

                    if extracted_beliefs:
                        st.session_state.beliefs = extracted_beliefs
                        st.success(f"✅ {len(extracted_beliefs)} beliefs estratti correttamente dal report JSON!")
                        st.rerun()
                    else:
                        st.warning("⚠️ JSON rilevato, ma nessun belief valido trovato.")

                except json.JSONDecodeError:
                    st.error("❌ Il JSON rilevato non è valido.")
                except Exception as e:
                    st.error(f"❌ Errore durante il parsing del report JSON: {e}")

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

# Export button
st.markdown("---")
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
        use_container_width=False
    )

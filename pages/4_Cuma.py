import streamlit as st
import os
import sys
import json
from datetime import datetime
import re

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompts import get_prompt
from utils.session_manager import SessionManager
from utils.ui_messages import get_random_thinking_message

CUMA_MODULE_GOAL = (
    "Mappare diverse Intenzioni strategiche possibili per uno specifico dominio, aiutando esperti "
    "di dominio a esplorare il massimo numero di scenari strategici basandosi su Beliefs e Desires."
)
CUMA_EXPECTED_OUTCOME = (
    "Una mapping completa di molteplici Intenzioni strategiche alternative, ognuna con un Piano d'Azione "
    "dettagliato, pronte per essere assegnate successivamente a singoli utenti in base ai loro bisogni."
)

st.set_page_config(
    page_title="CUMA - LumIA Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione session state
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'cuma_chat_history' not in st.session_state:
    st.session_state.cuma_chat_history = []
    st.session_state.cuma_greeted = False

if 'intentions_list' not in st.session_state:
    st.session_state.intentions_list = []

if 'loaded_beliefs' not in st.session_state:
    st.session_state.loaded_beliefs = []

if 'loaded_desires' not in st.session_state:
    st.session_state.loaded_desires = []

# CSS per nascondere menu Streamlit e styling
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}

    /* Riduce spessore delle righe di divisione */
    hr {
        margin: 0.5rem 0;
        border: none;
        border-top: 0.5px solid rgba(49, 51, 63, 0.2);
    }

    /* Divider nella sidebar */
    section[data-testid="stSidebar"] hr {
        margin: 0.3rem 0;
        border-top: 0.5px solid rgba(49, 51, 63, 0.15);
    }

    /* Riduce spazio superiore del titolo della pagina */
    .block-container {
        padding-top: 2rem !important;
    }

</style>
""", unsafe_allow_html=True)

# Carica il system prompt da file
CUMA_SYSTEM_PROMPT = get_prompt('cuma')

def load_bdi_data():
    """Carica Beliefs e Desires dalla sessione attiva."""
    if 'active_session' not in st.session_state or not st.session_state.active_session:
        return None, None

    try:
        bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.active_session)
        if not bdi_data:
            return None, None

        # Estrai beliefs
        beliefs = []
        if bdi_data.get("beliefs"):
            for belief in bdi_data.get("beliefs", []):
                beliefs.append({
                    "id": belief.get("belief_id", f"belief_{len(beliefs)+1}"),
                    "statement": belief.get("belief_statement") or belief.get("description", "N/A"),
                    "source": belief.get("source", "N/A"),
                    "confidence": belief.get("confidence_level", "medium")
                })

        # Estrai desires
        desires = []
        if bdi_data.get("desires"):
            for desire in bdi_data.get("desires", []):
                desires.append({
                    "id": desire.get("desire_id", f"desire_{len(desires)+1}"),
                    "statement": desire.get("desire_statement") or desire.get("description", "N/A"),
                    "priority": desire.get("priority", "medium"),
                    "success_metrics": desire.get("success_metrics", [])
                })

        return beliefs, desires

    except Exception as e:
        st.error(f"**Errore nel caricamento dei dati BDI:** {e}")
        return None, None

def save_intentions_to_bdi(intentions):
    """Salva le Intentions nel file current_bdi.json."""
    if 'active_session' not in st.session_state or not st.session_state.active_session:
        st.warning("Nessuna sessione attiva. Impossibile salvare le Intentions.")
        return False

    try:
        # Salva le intentions tramite SessionManager
        st.session_state.session_manager.update_bdi_data(
            st.session_state.active_session,
            intentions=intentions
        )

        st.success(f"✅ {len(intentions)} Intenzioni salvate nella sessione!")
        return True

    except Exception as e:
        st.error(f"**Errore nel salvataggio delle Intentions:** {e}")
        return False

def extract_intention_from_response(response_text):
    """
    Estrae una intenzione strutturata dal testo della risposta dell'AI.
    Ritorna un dict con intention e action_plan.
    """
    # Pattern semplice per estrarre intenzioni proposte
    intent_pattern = r"intenzione[:\s]*([^.!?\n]*[.!?])"
    plan_pattern = r"piano[:\s]*([^.!?\n]*[.!?])"

    intention = None
    plan = None

    intent_match = re.search(intent_pattern, response_text, re.IGNORECASE)
    if intent_match:
        intention = intent_match.group(1).strip()

    plan_match = re.search(plan_pattern, response_text, re.IGNORECASE)
    if plan_match:
        plan = plan_match.group(1).strip()

    if intention:
        return {
            "intention": {
                "id": f"INT-{len(st.session_state.intentions_list) + 1:03d}",
                "statement": intention,
                "linked_desire_id": st.session_state.loaded_desires[0]['id'] if st.session_state.loaded_desires else "N/A",
                "rationale": "Proposta dallo Strategic Architect basata su Beliefs e Desires"
            },
            "action_plan": {
                "plan_id": f"PLAN-{len(st.session_state.intentions_list) + 1:03d}",
                "steps": [
                    {
                        "step_number": 1,
                        "action": plan or "Azione da definire nella validazione",
                        "required_beliefs": [b['id'] for b in st.session_state.loaded_beliefs[:2]] if st.session_state.loaded_beliefs else []
                    }
                ],
                "expected_outcome": "Raggiungimento della intenzione attraverso l'esecuzione ordinata dei passi",
                "estimated_effort": "Medio"
            }
        }

    return None

# Carica la sessione attiva se presente
# Se non c'è active_session, prova a caricare l'ultima sessione attiva
if 'active_session' not in st.session_state or not st.session_state.active_session:
    # Fallback: carica l'ultima sessione attiva disponibile
    all_sessions = st.session_state.session_manager.get_all_sessions(status="active")
    if all_sessions:
        # Usa la più recentemente acceduta
        latest_session = max(all_sessions, key=lambda s: s['metadata'].get('last_accessed', ''))
        st.session_state.active_session = latest_session['session_id']

# CONTROLLO SESSIONE OBBLIGATORIO
if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("⚠️ Nessuna sessione attiva! Cuma richiede una sessione attiva per funzionare.")
    st.info("📝 Configura una sessione in Compass prima di usare Cuma.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧭 Vai a Compass", width='stretch', type="primary"):
            st.switch_page("pages/0_Compass.py")

    st.stop()

# Se arriviamo qui, la sessione esiste - caricala
active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
if not active_session_data:
    st.error("❌ Errore: Sessione attiva non trovata nel database!")
    if st.button("🧭 Vai a Compass", type="primary"):
        st.switch_page("pages/0_Compass.py")
    st.stop()

# Carica Beliefs e Desires automaticamente
if not st.session_state.loaded_beliefs and not st.session_state.loaded_desires:
    beliefs, desires = load_bdi_data()
    if beliefs:
        st.session_state.loaded_beliefs = beliefs
    if desires:
        st.session_state.loaded_desires = desires

# SIDEBAR (struttura simile ad Alì)
with st.sidebar:
    # Header con logo e pulsante home sulla stessa riga
    col_logo, col_home = st.columns([3, 1])

    with col_logo:
        st.markdown("<div style='padding-top: 0px;'><h2>✨ LumIA Studio</h2></div>", unsafe_allow_html=True)

    with col_home:
        if st.button("🏠", width='stretch', type="secondary", help="Torna alla Home"):
            st.switch_page("app.py")

    st.divider()

    # Mostra sessione attiva
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.success(f"📍 Sessione Attiva: **{active_session_data['metadata']['name']}**")
            st.caption(f"🗂️ Context: {active_session_data['config'].get('context', 'N/A')}")

            if st.button("🧭 Vai a Compass", width='stretch'):
                st.switch_page("pages/0_Compass.py")
        else:
            st.warning("⚠️ Sessione attiva non trovata")
    else:
        st.info("ℹ️ Nessuna sessione attiva")
        if st.button("🧭 Attiva una sessione", width='stretch'):
            st.switch_page("pages/0_Compass.py")

    st.divider()

    # Configurazione
    st.header("⚙️ Configurazione CUMA")

    # Lazy load LLMManager e conversation_auditor quando serve
    if 'llm_manager' not in st.session_state:
        from utils.llm_manager import LLMManager
        st.session_state.llm_manager = LLMManager()

    # Selezione provider e modello (default dalla sessione)
    available_providers = st.session_state.llm_manager.get_available_providers()
    model = None

    if not available_providers:
        st.error("⚠️ Nessun provider LLM disponibile!")
        st.info("Configura le API keys nel file .env:\n- GOOGLE_API_KEY\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY")
        provider = None
    else:
        # Usa il provider della sessione come default
        session_provider = active_session_data['config'].get('llm_provider')
        if session_provider and session_provider in available_providers:
            default_provider = session_provider
        else:
            default_provider = "Gemini" if "Gemini" in available_providers else available_providers[0]

        col_config1, col_config2 = st.columns(2)
        with col_config1:
            provider = st.selectbox(
                "Provider LLM",
                available_providers,
                index=available_providers.index(default_provider),
                key="cuma_provider",
                help="Provider configurato dalla sessione attiva"
            )

        with col_config2:
            if provider:
                models = st.session_state.llm_manager.get_models_for_provider(provider)
                # Usa il modello della sessione come default
                session_model = active_session_data['config'].get('llm_model')
                if session_model and session_model in models:
                    default_model = session_model
                else:
                    default_model = "gemini-2.5-pro" if provider == "Gemini" and "gemini-2.5-pro" in models else list(models.keys())[0]

                model = st.selectbox(
                    "Modello",
                    options=list(models.keys()),
                    format_func=lambda x: models[x],
                    index=list(models.keys()).index(default_model),
                    key="cuma_model",
                    help="Modello configurato dalla sessione attiva"
                )

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    col_new, col_complete = st.columns(2)
    with col_new:
        if st.button("🔄 Nuova Conversazione", width='stretch'):
            st.session_state.cuma_chat_history = []
            st.session_state.cuma_greeted = False
            st.session_state.intentions_list = []
            st.rerun()

    with col_complete:
        if st.button("💾 Completa Sessione", type="primary", width='stretch'):
            if st.session_state.intentions_list:
                if save_intentions_to_bdi(st.session_state.intentions_list):
                    st.success(f"✅ Sessione completata! {len(st.session_state.intentions_list)} Intenzioni salvate.")
                    st.balloons()
                st.rerun()
            else:
                st.warning("Nessuna intenzione da salvare!")

    st.divider()

    # Visualizza dati caricati
    st.subheader("📊 Dati Caricati")

    col_desires, col_beliefs = st.columns(2)

    with col_desires:
        if st.session_state.loaded_desires:
            st.metric("Desires", len(st.session_state.loaded_desires))

    with col_beliefs:
        if st.session_state.loaded_beliefs:
            st.metric("Beliefs", len(st.session_state.loaded_beliefs))

    if st.session_state.intentions_list:
        st.metric("Intenzioni Definite", len(st.session_state.intentions_list))

    st.divider()

    # Statistiche
    st.subheader("📈 Statistiche")
    col_messages, col_intentions = st.columns(2)
    with col_messages:
        st.metric("Messaggi", len(st.session_state.cuma_chat_history))
    with col_intentions:
        st.metric("Intenzioni Create", len(st.session_state.intentions_list))

# MAIN CONTENT
st.title("🗺️ CUMA - Domain Strategy Mapper")
st.markdown("**Mappa diverse Intenzioni strategiche per il tuo dominio**")
st.divider()

# Verifica che ci siano Beliefs e Desires caricati
if not st.session_state.loaded_desires:
    st.warning("⚠️ Nessun Desire trovato nella sessione. Completa la fase Alì prima di continuare.")
    if st.button("🎯 Vai ad Alì"):
        st.switch_page("pages/2_Ali.py")
    st.stop()

if not st.session_state.loaded_beliefs:
    st.info("ℹ️ Nessun Belief trovato nella sessione. Completa la fase Believer per migliorare i risultati.")

# Saluto iniziale
if not st.session_state.cuma_greeted:
    greeting = (
        "Ciao! Sono CUMA, il Domain Strategy Mapper. 🗺️\n\n"
        "Il mio ruolo è aiutare gli esperti di dominio a **mappare le diverse Intenzioni strategiche** "
        "possibili per uno specifico ambito.\n\n"
        "Non cercherò una sola soluzione 'giusta', ma esplorerò **molteplici scenari strategici** "
        "basandomi sui Beliefs e Desires che hai fornito. In questo modo, avrai una visione completa "
        "di tutte le possibili direzioni che il dominio può prendere.\n\n"
        "Successivamente, potrai decidere quale Intenzione proporre a quali utenti.\n\n"
        "**Iniziamo a esplorare le possibilità?**"
    )

    st.session_state.cuma_chat_history.append({
        "role": "assistant",
        "content": greeting
    })
    st.session_state.cuma_greeted = True


# Display chat history
for idx, message in enumerate(st.session_state.cuma_chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funzione per gestire la risposta dell'AI
def get_ai_system_context():
    """Prepara il contesto di sistema per l'AI"""
    beliefs_context = "\n".join([
        f"- {b['statement']} (Confidence: {b['confidence']})"
        for b in st.session_state.loaded_beliefs
    ]) if st.session_state.loaded_beliefs else "Nessun belief disponibile."

    desires_context = "\n".join([
        f"- {d['statement']} (Priorità: {d['priority']})"
        for d in st.session_state.loaded_desires
    ]) if st.session_state.loaded_desires else "Nessun desire disponibile."

    intentions_context = ""
    if st.session_state.intentions_list:
        intentions_context = "\n\nIntenzioni definite finora:\n"
        for idx, intention in enumerate(st.session_state.intentions_list, 1):
            intentions_context += f"{idx}. {intention.get('intention', {}).get('statement', 'N/A')}\n"

    return (
        f"{CUMA_SYSTEM_PROMPT}\n\n"
        f"### BELIEFS DISPONIBILI:\n{beliefs_context}\n\n"
        f"### DESIRES DISPONIBILI:\n{desires_context}\n"
        f"{intentions_context}"
    )

def process_ai_response(response):
    """Elabora la risposta dell'AI"""
    if not response:
        st.error("❌ Nessuna risposta ricevuta dall'AI. Riprova.")
        st.session_state.cuma_chat_history.pop()
        return False

    # Sostituisci il placeholder con la risposta reale
    st.session_state.cuma_chat_history[-1]["content"] = response

    # Cerca di estrarre una intenzione dalla risposta
    if "intenzione" in response.lower() or "intention" in response.lower():
        extracted = extract_intention_from_response(response)
        if extracted:
            st.session_state.intentions_list.append(extracted)

    # Cerca di estrarre il JSON dalla risposta
    if "json" in response.lower() or "{" in response:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                json_str = json_match.group()
                parsed_json = json.loads(json_str)
                if "intentions" in parsed_json:
                    st.session_state.intentions_list = parsed_json["intentions"]
                    st.success("✅ Report JSON estratto con successo!")
                else:
                    if parsed_json and parsed_json not in st.session_state.intentions_list:
                        st.session_state.intentions_list.append(parsed_json)
            except json.JSONDecodeError:
                pass

    return True

def handle_ai_response(user_message):
    """Gestisce l'aggiunta del messaggio utente e la risposta dell'AI"""
    # Aggiungi il messaggio dell'utente alla history
    st.session_state.cuma_chat_history.append({
        "role": "user",
        "content": user_message
    })

    # Lazy load LLMManager quando serve
    if 'llm_manager' not in st.session_state:
        from utils.llm_manager import LLMManager
        st.session_state.llm_manager = LLMManager()

    # Aggiungi placeholder nella chat
    thinking_msg = get_random_thinking_message()
    st.session_state.cuma_chat_history.append({
        "role": "assistant",
        "content": f"__{thinking_msg}__"
    })

    # Mostra loading state
    with st.spinner(f"🤔 {thinking_msg}"):
        try:
            system_with_context = get_ai_system_context()

            # Ottieni la risposta dall'AI
            active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
            provider = active_session_data['config'].get('llm_provider', 'Gemini')
            model = active_session_data['config'].get('llm_model', 'gemini-2.5-pro')

            response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=st.session_state.cuma_chat_history,
                system_prompt=system_with_context
            )

            if process_ai_response(response):
                st.rerun()
            else:
                st.rerun()

        except Exception as e:
            st.error(f"❌ Errore nella comunicazione con l'AI: {e}")
            import traceback
            st.write(traceback.format_exc())
            st.session_state.cuma_chat_history.pop()
            st.rerun()

# Mostra pulsanti di avvio solo la prima volta (dopo il saluto)
if st.session_state.cuma_greeted and len(st.session_state.cuma_chat_history) == 1:
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🗺️ Mappa diverse Intenzioni per il dominio",
            width='stretch',
            key="btn_generate_proposal"
        ):
            user_msg = "Genera diverse Intenzioni strategiche possibili per questo dominio. Proponi almeno 3-5 scenari alternativi basandoti sui Beliefs e Desires forniti."
            handle_ai_response(user_msg)

    with col2:
        if st.button(
            "🔍 Approfondisci un aspetto specifico",
            width='stretch',
            key="btn_user_objective"
        ):
            st.session_state.user_input_prompt = "Su quale aspetto del dominio vorresti che approfondissi ulteriormente?"
            st.rerun()

    st.divider()

# Chat input
user_input = st.chat_input("Scrivi il tuo messaggio per Cuma...")

if user_input:
    handle_ai_response(user_input)

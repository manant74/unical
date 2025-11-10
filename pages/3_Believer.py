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
from utils.session_manager import SessionManager
from utils.auditor import ConversationAuditor

BELIEVER_MODULE_GOAL = (
    "Guidare il responsabile a estrarre e formalizzare belief verificabili che supportano i desire identificati, "
    "specificando soggetto, relazione, oggetto ed evidenze."
)
BELIEVER_EXPECTED_OUTCOME = (
    "Progredire verso un belief chiaro e collegato ai desire pertinenti, includendo contesto, fonte e livello di confidenza."
)

st.set_page_config(
    page_title="Believer - LumIA Studio",
    page_icon="💡",
    layout="wide"
)

# Inizializza il session state (senza doc_processor che dipende dalla sessione)
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'believer_chat_history' not in st.session_state:
    st.session_state.believer_chat_history = []
    st.session_state.believer_greeted = False

if 'beliefs' not in st.session_state:
    st.session_state.beliefs = []

if 'loaded_desires' not in st.session_state:
    st.session_state.loaded_desires = None

if 'base_beliefs_checked' not in st.session_state:
    st.session_state.base_beliefs_checked = False

if 'base_beliefs_available' not in st.session_state:
    st.session_state.base_beliefs_available = None

if 'believer_audit_trail' not in st.session_state:
    st.session_state.believer_audit_trail = []

if 'believer_suggestions' not in st.session_state:
    st.session_state.believer_suggestions = []

if 'believer_pending_prompt' not in st.session_state:
    st.session_state.believer_pending_prompt = None

if 'believer_last_audited_index' not in st.session_state:
    st.session_state.believer_last_audited_index = -1

if 'conversation_auditor' not in st.session_state:
    st.session_state.conversation_auditor = ConversationAuditor(st.session_state.llm_manager)

# Carica il system prompt da file
BELIEVER_SYSTEM_PROMPT = get_prompt('believer')


def render_quick_replies(placeholder, suggestions, pending_state_key, button_prefix):
    """Renderizza i suggerimenti rapidi dell'Auditor in un container dedicato."""
    placeholder.empty()

    if not suggestions:
        return

    with placeholder:
        st.markdown("**🎯 Suggerimenti rapidi dell'Auditor**")

        for i in range(0, len(suggestions), 3):
            row = suggestions[i:i + 3]
            cols = st.columns(len(row))

            for col_idx, col in enumerate(cols):
                suggestion = row[col_idx]
                message_text = suggestion.get("message", "").strip()
                label = suggestion.get("label") or message_text or f"Opzione {i + col_idx + 1}"
                reason = suggestion.get("why")

                with col:
                    if st.button(label, key=f"{button_prefix}_suggestion_{i + col_idx}", use_container_width=True):
                        if message_text:
                            st.session_state[pending_state_key] = message_text
                    if reason:
                        st.caption(reason)

# CSS per nascondere solo il menu di navigazione Streamlit e styling
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

# Carica la sessione attiva se presente
# Se non c'è active_session, prova a caricare l'ultima sessione attiva
if 'active_session' not in st.session_state or not st.session_state.active_session:
    # Fallback: carica l'ultima sessione attiva disponibile
    all_sessions = st.session_state.session_manager.get_all_sessions(status="active")
    if all_sessions:
        # Usa la più recentemente acceduta
        latest_session = max(all_sessions, key=lambda s: s['metadata'].get('last_accessed', ''))
        st.session_state.active_session = latest_session['session_id']

    st.session_state.show_compass_button = False

# CONTROLLO SESSIONE OBBLIGATORIO
if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("⚠️ Nessuna sessione attiva! Believer richiede una sessione attiva per funzionare.")
    st.info("📝 Configura una sessione in Compass prima di usare Believer.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧭 Vai a Compass", use_container_width=True, type="primary"):
            st.switch_page("pages/0_Compass.py")

    st.stop()  # Ferma l'esecuzione se non c'è sessione

# Se arriviamo qui, la sessione esiste - caricala
active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
if not active_session_data:
    st.error("❌ Errore: Sessione attiva non trovata nel database!")
    if st.button("🧭 Vai a Compass", type="primary"):
        st.switch_page("pages/0_Compass.py")
    st.stop()

# Ora inizializza il DocumentProcessor con il contesto della sessione attiva
session_context = active_session_data['config'].get('context')
if session_context:
    # Normalizza il nome del contesto per il path
    from utils.context_manager import ContextManager
    context_manager = ContextManager()
    normalized_context = context_manager._normalize_name(session_context)
    
    # Inizializza o aggiorna il DocumentProcessor per il contesto della sessione
    if 'doc_processor' not in st.session_state or st.session_state.get('current_context') != normalized_context:
        st.session_state.doc_processor = DocumentProcessor(context_name=normalized_context)
        st.session_state.doc_processor.initialize_db()
        st.session_state.current_context = normalized_context
else:
    # Fallback alla directory predefinita se non c'è contesto
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
        st.session_state.doc_processor.initialize_db()

def load_desires():
    """Carica i desires dalla sessione attiva.

    Supporta la nuova struttura BDI con `domains -> personas -> desires` e mantiene
    compatibilità con la vecchia struttura piatta `desires` se presente.
    """

    if 'active_session' not in st.session_state or not st.session_state.active_session:
        return None

    try:
        bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.active_session)
        if not bdi_data:
            st.warning("⚠️ Nessun BDI disponibile per la sessione attiva.")
            return []

        # Nuova struttura: domains -> personas -> desires
        if isinstance(bdi_data.get('domains'), list) and bdi_data['domains']:
            converted: list = []
            for domain in bdi_data['domains']:
                domain_name = domain.get('domain_name', 'default')
                for persona in domain.get('personas', []) or []:
                    persona_name = persona.get('persona_name', 'N/A')
                    for desire in persona.get('desires', []) or []:
                        converted.append({
                            "id": desire.get("desire_id", f"gen_{len(converted) + 1}"),
                            # Supporta sia desire_statement (nuovo) sia descrizione (vecchio)
                            "description": desire.get("desire_statement") or desire.get("descrizione", "N/A"),
                            "priority": desire.get("priorità") or desire.get("priority", "medium"),
                            "context": f"Domain: {domain_name} · Persona: {persona_name}",
                            "timestamp": datetime.now().isoformat()
                        })
            return converted

        # Vecchia struttura: lista piatta di desires
        if isinstance(bdi_data.get('desires'), list) and bdi_data['desires']:
            converted: list = []
            for desire in bdi_data['desires']:
                converted.append({
                    "id": desire.get("desire_id", f"gen_{len(converted) + 1}"),
                    "description": desire.get("descrizione", "N/A"),
                    "priority": desire.get("priorità", "medium"),
                    "context": "Sessione Attiva",
                    "timestamp": datetime.now().isoformat()
                })
            return converted

        st.warning("⚠️ Nessun desire trovato nel BDI della sessione attiva.")
        return []
    except Exception as e:
        st.error(f"**Errore nel caricamento dei desires dalla sessione:** {e}")
        return None

def load_base_beliefs():
    """Carica i belief di base dalla sessione attiva.

    Returns:
        Lista di belief di base o None se non ce ne sono
    """
    if 'active_session' not in st.session_state or not st.session_state.active_session:
        return None

    try:
        # Carica i belief di base dalla sessione usando il SessionManager
        belief_data = st.session_state.session_manager.get_belief_base(st.session_state.active_session)

        if not belief_data:
            return None

        beliefs = belief_data.get('beliefs', [])
        return beliefs if beliefs else None

    except Exception as e:
        print(f"Errore nel caricamento dei belief di base: {e}")
        return None

# Sidebar per configurazione
with st.sidebar:
    # Header con logo e pulsante home sulla stessa riga
    col_logo, col_home = st.columns([3, 1])

    with col_logo:
        st.markdown("<div style='padding-top: 0px;'><h3>✨ LumIA Studio</h3></div>", unsafe_allow_html=True)

    with col_home:
        if st.button("🏠", width='stretch', type="secondary", help="Torna alla Home"):
            st.switch_page("app.py")

    st.divider()

    # Mostra sessione attiva
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.success(f"📍 Sessione Attiva: **{active_session_data['metadata']['name']}**")
            
            # Mostra informazioni sulla base di conoscenza caricata
            kb_stats = st.session_state.doc_processor.get_stats()
            if kb_stats['document_count'] > 0:
                st.caption(f"🗂️ Context: {active_session_data['config'].get('context', 'N/A')} (KB : {kb_stats['document_count']} chunks)")           
            else:
                st.warning("⚠️ Base di conoscenza vuota per questo contesto")

            # Mostra il pulsante Compass solo se l'utente ha scelto di verificare i belief di base
            if st.session_state.get('show_compass_button', False):
                if st.button("🧭 Vai a Compass", use_container_width=True, type="primary"):
                    st.switch_page("pages/0_Compass.py")
        else:
            st.warning("⚠️ Sessione attiva non trovata")
    else:
        st.info("ℹ️ Nessuna sessione attiva")
        if st.button("🧭 Attiva una sessione", use_container_width=True):
            st.switch_page("pages/0_Compass.py")

    st.divider()

    # Carica desires
    if st.session_state.loaded_desires is None:
        st.session_state.loaded_desires = load_desires()

    if st.session_state.loaded_desires:
        # Determina la fonte dei desires
        source_info = "dalla Sessione Attiva" if st.session_state.loaded_desires[0].get('context') == 'Sessione Attiva' else "dal file globale"
        st.info(f"✅ {len(st.session_state.loaded_desires)} Desire caricati {source_info}")

        with st.expander("🎯 Desires Disponibili"):
            for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                # Usa 'id' se presente, altrimenti usa l'indice
                desire_id = desire.get('id', idx)
                desire_desc = desire.get('description', desire.get('content', 'N/A'))
                st.markdown(f"**#{desire_id}**: {desire_desc}")
    else:
        # Il messaggio di errore/warning viene già mostrato da load_desires()
        pass

    # Carica belief di base se disponibili
    if st.session_state.base_beliefs_available is None:
        st.session_state.base_beliefs_available = load_base_beliefs()

    if st.session_state.base_beliefs_available:
        st.info(f"📚 {len(st.session_state.base_beliefs_available)} Belief di Base disponibili nel contesto")
        with st.expander("💡 Belief di Base Disponibili"):
            for idx, belief in enumerate(st.session_state.base_beliefs_available, 1):
                belief_desc = belief.get('belief_statement', belief.get('fonte', 'N/A'))
                st.markdown(f"**{idx}**. {belief_desc[:100]}...")

   # Quick action: Add belief manually
    with st.expander("➕ Aggiungi Belief Manualmente"):
        st.markdown("Compila i campi per aggiungere un belief manualmente")

        belief_desc = st.text_area("Descrizione", key="manual_belief_desc")
        belief_type = st.selectbox("Tipo", ["fact", "assumption", "principle", "constraint"], key="manual_belief_type")
        belief_confidence = st.selectbox("Confidenza", ["high", "medium", "low"], key="manual_belief_confidence")

        # Multi-select per desires correlati
        if st.session_state.loaded_desires:
            # Crea options gestendo campi mancanti
            desire_options = {}
            for idx, d in enumerate(st.session_state.loaded_desires, 1):
                d_id = d.get('id', idx)
                d_desc = d.get('description', d.get('content', 'N/A'))
                desire_options[d_id] = f"#{d_id}: {d_desc[:50]}"

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

    st.divider()

    # Configurazione
    st.header("⚙️ Configurazione Believer")
    
    # Selezione provider e modello (default dalla sessione)
    available_providers = st.session_state.llm_manager.get_available_providers()

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
            # Puoi aggiungere qui i controlli o le impostazioni desiderate per la colonna 2
            provider = st.selectbox(
                "Provider LLM",
                available_providers,
                index=available_providers.index(default_provider),
                key="believer_provider",
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
                    key="believer_model",
                    help="Modello configurato dalla sessione attiva"
                )

    st.divider()


    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    col_left, col_right = st.columns(2)

    with col_left:
        if st.button("🔄 Nuova", use_container_width=True):
            st.session_state.believer_chat_history = []
            st.session_state.believer_greeted = False
            st.session_state.loaded_desires = None  # Forza il ricaricamento
            st.session_state.base_beliefs_checked = False  # Reset del check belief di base
            st.session_state.base_beliefs_available = None  # Forza ricaricamento belief di base
            st.session_state.show_compass_button = False  # Nascondi il pulsante Compass
            st.session_state.believer_audit_trail = []
            st.session_state.believer_suggestions = []
            st.session_state.believer_pending_prompt = None
            st.rerun()

    with col_right:
        if st.button("✅ Completa", type="primary", use_container_width=True):
            # Verifica se c'è una sessione attiva
            if 'active_session' in st.session_state and st.session_state.active_session:
                if st.session_state.beliefs:
                    # Salva i beliefs nella sessione corrente usando BDI data
                    st.session_state.session_manager.update_bdi_data(
                        st.session_state.active_session,
                        beliefs=st.session_state.beliefs
                    )

                    # Salva anche la chat history come metadati della sessione
                    st.session_state.session_manager.update_session_metadata(
                        st.session_state.active_session,
                        chat_history_believer=st.session_state.believer_chat_history
                    )

                    st.success(f"✅ Sessione completata! {len(st.session_state.beliefs)} Beliefs salvati nella sessione attiva!")
                    st.balloons()
                elif len(st.session_state.believer_chat_history) > 1:
                    # Se ci sono messaggi ma nessun belief, salva solo la chat
                    st.session_state.session_manager.update_session_metadata(
                        st.session_state.active_session,
                        chat_history_believer=st.session_state.believer_chat_history
                    )

                    st.warning("⚠️ Nessun belief identificato, ma la conversazione è stata salvata nella sessione.")
                    st.info("💡 Suggerimento: Chiedi a Believer di generare il report finale con i beliefs identificati.")
                else:
                    st.warning("⚠️ Nessuna conversazione da salvare!")
            else:
                # Fallback: salva come prima in file locali se non c'è sessione attiva
                st.warning("⚠️ Nessuna sessione attiva! Salvataggio in file locali...")

                if st.session_state.beliefs:
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

                    with open("./data/current_bdi.json", 'w', encoding='utf-8') as f:
                        json.dump(final_data, f, ensure_ascii=False, indent=2)

                    st.info(f"💾 Beliefs salvati in: {filename}")
                    st.info("💡 Suggerimento: Attiva una sessione in Compass per integrarla nel sistema!")
                else:
                    st.warning("⚠️ Nessun dato da salvare!")

    st.divider()

    # Visualizza beliefs
    if st.session_state.beliefs:
        st.subheader("💡 Belief Identificati")
        for idx, belief in enumerate(st.session_state.beliefs, 1):
            # Usa .get() per accedere all'ID in modo sicuro, con un fallback all'indice del loop
            belief_id = belief.get('id', idx)
            belief_desc = belief.get('description', 'N/A')
            with st.expander(f"#{belief_id}: {belief_desc[:30]}..."):
                st.json(belief)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistiche")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Messaggi", len(st.session_state.believer_chat_history))
    with col2:
        st.metric("Belief Identificati", len(st.session_state.beliefs))
    with col3:
        stats = st.session_state.doc_processor.get_stats()
        st.metric("Contenuti in KB", stats['document_count'])

# Main content
st.title("💡 Believer - Agent for Beliefs")
st.markdown("**Benvenuto! Sono Believer e sono qui per aiutarti a individuare i Belief**")
st.divider()

# Check prerequisites
kb_stats = st.session_state.doc_processor.get_stats()
if kb_stats['document_count'] == 0:
    context_name = kb_stats.get('context', 'default')
    st.warning(f"⚠️ La base di conoscenza per il contesto '{context_name}' è vuota! Vai a Knol per caricare documenti prima di iniziare.")
    st.info(f"🎯 Contesto attuale: {active_session_data['config'].get('context', 'N/A')}")
    if st.button("📚 Vai a Knol"):
        st.switch_page("pages/1_Knol.py")
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

# Saluto inizialex\
if not st.session_state.believer_greeted:
    # Crea summary desires gestendo campi mancanti
    desires_list = []
    for idx, d in enumerate(st.session_state.loaded_desires[:3], 1):
        d_id = d.get('id', idx)
        d_desc = d.get('description', d.get('content', 'N/A'))
        desires_list.append(f"- Desire #{d_id}: {d_desc}")
    desires_summary = "\n".join(desires_list)

    # Check se ci sono belief di base
    if st.session_state.base_beliefs_available and not st.session_state.base_beliefs_checked:
        # Ci sono belief di base - chiedi all'utente cosa vuole fare
        greeting = f"""Ciao! Sono Believer e sono qui per aiutarti a individuare i Belief. 💡

Ho caricato i tuoi Desire:
{desires_summary}
{"..." if len(st.session_state.loaded_desires) > 3 else ""}

🔍 **Ho notato che esistono già {len(st.session_state.base_beliefs_available)} Belief di Base configurati nel contesto di questa sessione.**

Puoi scegliere tra tre opzioni:

**1. Chat per creare i Belief Specializzati** 🎯
   Possiamo lavorare insieme in modalità conversazionale per identificare belief più specifici e dettagliati, focalizzati sui tuoi Desire. Questi saranno complementari ai belief di base e più contestualizzati.

**2. Verificare i Belief di Base** 📋
   Se preferisci prima consultare i belief di base già definiti, puoi visualizzarli in Compass nella sezione del contesto attivo.

**3. Crea un mix tra Belief di Base e Belief per Desire** 🔄
   Genererò automaticamente un set completo senza richiedere ulteriori input. Analizzerò i tuoi Desire, genererò Belief specializzati per ciascuno, e selezionerò solo i Belief di Base pertinenti. Il processo è completamente automatico.

**Cosa preferisci fare?** Rispondi "1" per la chat interattiva, "2" per verificare i belief di base, oppure "3" per la generazione automatica completa."""
    else:
        # Nessun belief di base o già controllato - procedi normalmente
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
believer_audit_map = {
    item["message_index"]: item.get("result", {})
    for item in st.session_state.believer_audit_trail
    if isinstance(item, dict) and "message_index" in item
}

for idx, message in enumerate(st.session_state.believer_chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    if message.get("role") == "assistant" and idx in believer_audit_map:
        audit_payload = believer_audit_map[idx] or {}
        with st.chat_message("system"):
            status = audit_payload.get("status", "pass")
            icon = "✅" if status == "pass" else "⚠️"
            summary = audit_payload.get("summary")

            st.markdown(f"**Auditor {icon}**")
            if summary:
                st.markdown(summary)

            issues = audit_payload.get("issues") or []
            if issues:
                st.markdown("**Problemi rilevati:**")
                for issue in issues:
                    issue_type = issue.get("type", "issue")
                    severity = issue.get("severity", "low")
                    message_text = issue.get("message", "")
                    st.write(f"- ({severity.upper()} · {issue_type}) {message_text}")

            improvements = audit_payload.get("assistant_improvements") or []
            if improvements:
                st.markdown("**Suggerimenti per l'agente:**")
                for idea in improvements:
                    st.write(f"- {idea}")

            next_focus = audit_payload.get("next_focus")
            if next_focus:
                st.caption(f"Prossimo focus: {next_focus}")

            confidence = audit_payload.get("confidence")
            if confidence:
                st.caption(f"Sicurezza valutazione: {confidence}")

believer_suggestions_placeholder = st.empty()

# Mostra i pulsanti pills se ci sono belief di base e l'utente non ha ancora scelto
if st.session_state.base_beliefs_available and not st.session_state.base_beliefs_checked and st.session_state.believer_greeted:
    st.markdown("---")

    # Usa columns per mettere i pulsanti in fila
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎯 Chat per creare i Belief Specializzati", key="btn_create_beliefs", use_container_width=True):
            # Simula la scelta dell'opzione 1
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "1"
            })
            st.session_state.base_beliefs_checked = True

            response = """Ottimo! Procediamo a creare belief specializzati sui tuoi Desire in modalità conversazionale. 🎯

Questi belief saranno più specifici e dettagliati rispetto ai belief di base, e saranno direttamente collegati ai tuoi obiettivi.

Iniziamo a esplorare la tua base di conoscenza per identificare i belief rilevanti. Dimmi, su quale desire vuoi concentrarti per primo?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    with col2:
        if st.button("📋 Verificare i Belief di Base", key="btn_verify_beliefs", use_container_width=True):
            # Simula la scelta dell'opzione 2
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "2"
            })

            # Marca i belief di base come controllati per nascondere i pulsanti
            st.session_state.base_beliefs_checked = True

            response = """Perfetto! Ti consiglio di andare su **Compass** per visualizzare i Belief di Base della tua sessione.

In Compass puoi:
- 📋 Visualizzare tutti i belief di base configurati
- ✏️ Modificarli o aggiornarli se necessario
- 🔍 Analizzarli nel dettaglio

Una volta verificati i belief di base, torna qui se vuoi creare belief più specializzati sui tuoi Desire.

👉 Usa il pulsante "🧭 Vai a Compass" nella sidebar per navigare!"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            # Imposta un flag per mostrare il pulsante Compass
            st.session_state.show_compass_button = True
            st.rerun()

    with col3:
        if st.button("🔄 Crea un mix tra Belief di Base e Desire", key="btn_mix_beliefs", use_container_width=True):
            # Simula la scelta dell'opzione 3
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "3"
            })
            st.session_state.base_beliefs_checked = True

            # Avvia il processo automatico di mix
            with st.spinner("Sto analizzando i Desire e selezionando i Belief di Base rilevanti..."):
                try:
                    # Prepara il contesto per l'LLM
                    desires_context = "DESIRES DELL'UTENTE:\n"
                    for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                        desire_id = desire.get('id', idx)
                        desire_desc = desire.get('description', desire.get('content', 'N/A'))
                        desire_priority = desire.get('priority', 'N/A')
                        desires_context += f"- Desire #{desire_id}: {desire_desc} (Priorità: {desire_priority})\n"

                    # Passa l'intero JSON dei belief di base per un'analisi completa
                    base_beliefs_json = json.dumps(st.session_state.base_beliefs_available, indent=2, ensure_ascii=False)
                    base_beliefs_context = f"\n\nBELIEF DI BASE DISPONIBILI (in formato JSON):\n```json\n{base_beliefs_json}\n```"

                    # Carica il prompt template dal file
                    mix_prompt_template = get_prompt('believer', use_cache=False, prompt_suffix='mix_beliefs_prompt')

                    # Sostituisci i placeholder con i valori effettivi
                    mix_prompt = mix_prompt_template.replace('{desires_context}', desires_context)
                    mix_prompt = mix_prompt.replace('{base_beliefs_context}', base_beliefs_context)

                    # Get LLM settings from session
                    llm_settings = active_session_data['config'].get('llm_settings', {})
                    use_defaults = llm_settings.get('use_defaults', False)

                    # Prepara i parametri della chiamata
                    chat_params = {
                        'provider': provider,
                        'model': model,
                        'messages': [{"role": "user", "content": mix_prompt}],
                        'system_prompt': None  # Nessun system prompt, tutto è nel prompt utente
                    }

                    # Aggiungi parametri custom solo se use_defaults è False
                    if not use_defaults:
                        chat_params['temperature'] = llm_settings.get('temperature', 1.0)
                        chat_params['top_p'] = llm_settings.get('top_p', 0.95 if provider == "Gemini" else 1.0)

                        # Max tokens - parametro diverso per provider (aumentato per il mix)
                        if provider == "Gemini":
                            chat_params['max_output_tokens'] = min(llm_settings.get('max_tokens', 65536), 65536)
                        else:
                            chat_params['max_tokens'] = min(llm_settings.get('max_tokens', 4096), 8000)

                        # Reasoning effort - solo per GPT-5
                        if model.startswith('gpt-5'):
                            chat_params['reasoning_effort'] = llm_settings.get('reasoning_effort', 'medium')

                    # Chiama l'LLM per generare il mix
                    mix_response = st.session_state.llm_manager.chat(**chat_params)
                    response = f"""Perfetto! Ho completato l'analisi automatica dei tuoi Desire e dei Belief di Base. 🔄

Ho creato un set completo e ottimale che include:
- ✨ **Belief specializzati**: Generati specificamente per supportare ciascuno dei tuoi Desire
- 📚 **Belief di Base selezionati**: Solo quelli rilevanti e direttamente collegati ai tuoi obiettivi

Ecco il risultato:

{mix_response}

✅ I belief sono stati generati e salvati automaticamente. Puoi visualizzarli nella sidebar o esportarli usando il pulsante in fondo alla pagina."""

                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    response = f"❌ Si è verificato un errore durante la generazione del mix: {str(e)}\n\nPuoi provare a scegliere una delle altre opzioni o contattare il supporto."
                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

            st.rerun()

    st.markdown("---")

# Chat input (supporta suggerimenti automatici dell'Auditor)
auto_prompt = None
if isinstance(st.session_state.believer_pending_prompt, str):
    auto_prompt = st.session_state.believer_pending_prompt.strip()
    st.session_state.believer_pending_prompt = None

user_prompt = st.chat_input("Scrivi il tuo messaggio...")
prompt = auto_prompt or user_prompt

if prompt:
    # Add user message
    st.session_state.believer_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Check se l'utente sta rispondendo alla domanda sui belief di base
    if st.session_state.base_beliefs_available and not st.session_state.base_beliefs_checked:
        if "2" in prompt.strip() or "verificare" in prompt.lower() or "belief di base" in prompt.lower():
            # L'utente vuole verificare i belief di base
            response = """Perfetto! Ti consiglio di andare su **Compass** per visualizzare i Belief di Base del tuo contesto.

In Compass puoi:
- 📋 Visualizzare tutti i belief di base configurati
- ✏️ Modificarli o aggiornarli se necessario
- 🔍 Analizzarli nel dettaglio

Una volta verificati i belief di base, torna qui se vuoi creare belief più specializzati sui tuoi Desire.

👉 Usa il pulsante "🧭 Vai a Compass" nella sidebar per navigare!"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            st.stop()

        elif "1" in prompt.strip() or "creare" in prompt.lower() or "nuovi" in prompt.lower() or "specializzati" in prompt.lower() or "chat" in prompt.lower():
            # L'utente vuole creare nuovi belief specializzati
            st.session_state.base_beliefs_checked = True

            response = """Ottimo! Procediamo a creare belief specializzati sui tuoi Desire in modalità conversazionale. 🎯

Questi belief saranno più specifici e dettagliati rispetto ai belief di base, e saranno direttamente collegati ai tuoi obiettivi.

Iniziamo a esplorare la tua base di conoscenza per identificare i belief rilevanti. Dimmi, su quale desire vuoi concentrarti per primo?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            st.stop()

        elif "3" in prompt.strip() or "mix" in prompt.lower() or "automatico" in prompt.lower():
            # L'utente vuole creare il mix automatico
            st.session_state.base_beliefs_checked = True

            # Avvia il processo automatico di mix
            with st.spinner("Sto analizzando i Desire e selezionando i Belief di Base rilevanti..."):
                try:
                    # Prepara il contesto per l'LLM
                    desires_context = "DESIRES DELL'UTENTE:\n"
                    for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                        desire_id = desire.get('id', idx)
                        desire_desc = desire.get('description', desire.get('content', 'N/A'))
                        desire_priority = desire.get('priority', 'N/A')
                        desires_context += f"- Desire #{desire_id}: {desire_desc} (Priorità: {desire_priority})\n"

                    # Passa l'intero JSON dei belief di base per un'analisi completa
                    base_beliefs_json = json.dumps(st.session_state.base_beliefs_available, indent=2, ensure_ascii=False)
                    base_beliefs_context = f"\n\nBELIEF DI BASE DISPONIBILI (in formato JSON):\n```json\n{base_beliefs_json}\n```"

                    # Carica il prompt template dal file
                    mix_prompt_template = get_prompt('believer', use_cache=False, prompt_suffix='mix_beliefs_prompt')

                    # Sostituisci i placeholder con i valori effettivi
                    mix_prompt = mix_prompt_template.replace('{desires_context}', desires_context)
                    mix_prompt = mix_prompt.replace('{base_beliefs_context}', base_beliefs_context)

                    # Get LLM settings from session
                    llm_settings = active_session_data['config'].get('llm_settings', {})
                    use_defaults = llm_settings.get('use_defaults', False)

                    # Prepara i parametri della chiamata
                    chat_params = {
                        'provider': provider,
                        'model': model,
                        'messages': [{"role": "user", "content": mix_prompt}],
                        'system_prompt': None  # Nessun system prompt, tutto è nel prompt utente
                    }

                    # Aggiungi parametri custom solo se use_defaults è False
                    if not use_defaults:
                        chat_params['temperature'] = llm_settings.get('temperature', 1.0)
                        chat_params['top_p'] = llm_settings.get('top_p', 0.95 if provider == "Gemini" else 1.0)

                        # Max tokens - parametro diverso per provider (aumentato per il mix)
                        if provider == "Gemini":
                            chat_params['max_tokens'] = min(llm_settings.get('max_output_tokens', 65536), 65536)
                        else:
                            chat_params['max_tokens'] = min(llm_settings.get('max_tokens', 4096), 8000)

                        # Reasoning effort - solo per GPT-5
                        if model.startswith('gpt-5'):
                            chat_params['reasoning_effort'] = llm_settings.get('reasoning_effort', 'medium')

                    # Chiama l'LLM per generare il mix
                    mix_response = st.session_state.llm_manager.chat(**chat_params)
                    response = f"""Perfetto! Ho completato l'analisi automatica dei tuoi Desire e dei Belief di Base. 🔄

Ho creato un set completo e ottimale che include:
- ✨ **Belief specializzati**: Generati specificamente per supportare ciascuno dei tuoi Desire
- 📚 **Belief di Base selezionati**: Solo quelli rilevanti e direttamente collegati ai tuoi obiettivi

Ecco il risultato:

{mix_response}

✅ I belief sono stati generati e salvati automaticamente. Puoi visualizzarli nella sidebar o esportarli usando il pulsante in fondo alla pagina."""

                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                    # --- LOGICA DI PARSING JSON SPOSTATA QUI ---
                    json_match = re.search(r'```json(.*?)```', mix_response, re.DOTALL) or re.search(r'\{[\s\S]*\}', mix_response)
                    if json_match:
                        try:
                            json_str = json_match.group(1).strip() if '```' in json_match.group(0) else json_match.group(0).strip()
                            parsed_json = json.loads(json_str)

                            if "beliefs" in parsed_json and isinstance(parsed_json["beliefs"], list):
                                extracted_beliefs = []
                                existing_ids = [b.get("id", 0) for b in st.session_state.beliefs]
                                next_id = max(existing_ids) + 1 if existing_ids else 1

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
                                        "id": next_id + len(extracted_beliefs),
                                        "description": " ".join(description_parts),
                                        "type": b.get("metadati", {}).get("tipo_soggetto", "fact"),
                                        "confidence": "medium",
                                        "related_desires": [d.get("desire_id") for d in b.get("desires_correlati", [])],
                                        "evidence": b.get("fonte", ""),
                                        "timestamp": datetime.now().isoformat()
                                    })

                                if extracted_beliefs:
                                    st.session_state.beliefs.extend(extracted_beliefs)
                                    st.session_state.session_manager.update_bdi_data(
                                        st.session_state.active_session,
                                        beliefs=st.session_state.beliefs
                                    )
                                    st.success(f"✅ Mix automatico completato! {len(extracted_beliefs)} nuovi beliefs aggiunti.")
                                else:
                                    st.warning("⚠️ JSON ricevuto, ma nessun belief valido trovato.")
                        except json.JSONDecodeError:
                            st.error("❌ Il JSON generato dall'LLM per il mix non è valido.")
                        except Exception as parse_exc:
                            st.error(f"❌ Errore durante il parsing del JSON del mix: {parse_exc}")
                    # --- FINE LOGICA DI PARSING ---

                    with st.chat_message("assistant"):
                        st.markdown(response)

                except Exception as e:
                    response = f"❌ Si è verificato un errore durante la generazione del mix: {str(e)}\n\nPuoi provare a scegliere una delle altre opzioni o contattare il supporto."
                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                    # --- LOGICA DI PARSING JSON SPOSTATA QUI ---
                    json_match = re.search(r'```json(.*?)```', mix_response, re.DOTALL) or re.search(r'\{[\s\S]*\}', mix_response)
                    if json_match:
                        try:
                            json_str = json_match.group(1).strip() if '```' in json_match.group(0) else json_match.group(0).strip()
                            parsed_json = json.loads(json_str)

                            if "beliefs" in parsed_json and isinstance(parsed_json["beliefs"], list):
                                extracted_beliefs = []
                                existing_ids = [b.get("id", 0) for b in st.session_state.beliefs]
                                next_id = max(existing_ids) + 1 if existing_ids else 1

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
                                        "id": next_id + len(extracted_beliefs),
                                        "description": " ".join(description_parts),
                                        "type": b.get("metadati", {}).get("tipo_soggetto", "fact"),
                                        "confidence": "medium",
                                        "related_desires": [d.get("desire_id") for d in b.get("desires_correlati", [])],
                                        "evidence": b.get("fonte", ""),
                                        "timestamp": datetime.now().isoformat()
                                    })

                                if extracted_beliefs:
                                    st.session_state.beliefs.extend(extracted_beliefs)
                                    st.session_state.session_manager.update_bdi_data(
                                        st.session_state.active_session,
                                        beliefs=st.session_state.beliefs
                                    )
                                    st.success(f"✅ Mix automatico completato! {len(extracted_beliefs)} nuovi beliefs aggiunti.")
                                else:
                                    st.warning("⚠️ JSON ricevuto, ma nessun belief valido trovato.")
                        except json.JSONDecodeError:
                            st.error("❌ Il JSON generato dall'LLM per il mix non è valido.")
                        except Exception as parse_exc:
                            st.error(f"❌ Errore durante il parsing del JSON del mix: {parse_exc}")
                    # --- FINE LOGICA DI PARSING ---
                    with st.chat_message("assistant"):
                        st.markdown(response)

            st.stop()

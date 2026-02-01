import streamlit as st
import os
import sys
import json
from datetime import datetime
import re
# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.prompts import get_prompt
from utils.session_manager import SessionManager
from utils.ui_messages import get_random_thinking_message

BELIEVER_MODULE_GOAL = (
    "Guide the domain owner to extract and formalize verifiable beliefs that support identified desires, "
    "specifying subject, relation, object, and evidence."
)
BELIEVER_EXPECTED_OUTCOME = (
    "Progress toward a clear belief connected to relevant desires, including context, source, and confidence level."
)

st.set_page_config(
    page_title="Believer - LumIA Studio",
    page_icon="💡",
    layout="wide"
)

# LLMManager non viene inizializzato qui - viene caricato lazy quando serve (Configurazione Believer)

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

if 'believer_specialized_chat_active' not in st.session_state:
    st.session_state.believer_specialized_chat_active = False

# belief_auditor viene inizializzato quando serve con LLMManager

# Carica il system prompt da file
BELIEVER_SYSTEM_PROMPT = get_prompt('believer')


def render_quick_replies(placeholder, suggestions, pending_state_key, button_prefix):
    """Renderizza i suggerimenti rapidi dell'Auditor in un container dedicato."""
    placeholder.empty()

    if not suggestions:
        return

    with placeholder:
        st.markdown("**🎯 Auditor Quick Suggestions**")

        for i in range(0, len(suggestions), 3):
            row = suggestions[i:i + 3]
            cols = st.columns(len(row))

            for col_idx, col in enumerate(cols):
                suggestion = row[col_idx]
                message_text = suggestion.get("message", "").strip()
                label = suggestion.get("label") or message_text or f"Option {i + col_idx + 1}"
                reason = suggestion.get("why")

                with col:
                    if st.button(label, key=f"{button_prefix}_suggestion_{i + col_idx}", width='stretch'):
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
    st.error("⚠️ No active session! Believer requires an active session to function.")
    st.info("📝 Configure a session in Compass before using Believer.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧭 Go to Compass", width='stretch', type="primary"):
            st.switch_page("pages/0_Compass.py")

    st.stop()  # Ferma l'esecuzione se non c'è sessione

# Se arriviamo qui, la sessione esiste - caricala
active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
if not active_session_data:
    st.error("❌ Error: Active session not found in database!")
    if st.button("🧭 Go to Compass", type="primary"):
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
    """Carica i desires dalla sessione attiva in formato single-beneficiario."""

    if 'active_session' not in st.session_state or not st.session_state.active_session:
        return None

    try:
        bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.active_session)
        if not bdi_data:
            st.warning("No BDI available for active session.")
            return []

        beneficiario_info = bdi_data.get("beneficiario") or bdi_data.get("persona") or {}
        beneficiario_name = beneficiario_info.get("beneficiario_name") or beneficiario_info.get("persona_name", "Beneficiario primario")
        desires = bdi_data.get("desires", []) or []
        if desires:
            converted: list = []
            for desire in desires:
                converted.append({
                    "id": desire.get("desire_id", f"gen_{len(converted) + 1}"),
                    "description": desire.get("desire_statement") or desire.get("description", "N/A"),
                    "priority": desire.get("priority", "medium"),
                    "context": f"Beneficiario: {beneficiario_name}",
                    "timestamp": desire.get("timestamp", datetime.now().isoformat())
                })
            return converted

        st.warning("No desires found in active session's BDI.")
        return []
    except Exception as e:
        st.error(f"**Error loading desires from session:** {e}")
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
        if st.button("🏠", width='stretch', type="secondary", help="Back to Home"):
            st.switch_page("app.py")

    st.divider()

    # Mostra sessione attiva
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.success(f"📍 Active Session: **{active_session_data['metadata']['name']}**")

            # Mostra informazioni sulla base di conoscenza caricata
            kb_stats = st.session_state.doc_processor.get_stats()
            if kb_stats['document_count'] > 0:
                st.caption(f"🗂️ Context: {active_session_data['config'].get('context', 'N/A')} (KB: {kb_stats['document_count']} chunks)")
            else:
                st.warning("⚠️ Empty knowledge base for this context")

            # Mostra il pulsante Compass solo se l'utente ha scelto di verificare i belief di base
            if st.session_state.get('show_compass_button', False):
                if st.button("🧭 Go to Compass", width='stretch', type="primary"):
                    st.switch_page("pages/0_Compass.py")
        else:
            st.warning("⚠️ Active session not found")
    else:
        st.info("ℹ️ No active session")
        if st.button("🧭 Activate a session", width='stretch'):
            st.switch_page("pages/0_Compass.py")

    st.divider()

    # Carica desires
    if st.session_state.loaded_desires is None:
        st.session_state.loaded_desires = load_desires()

    if st.session_state.loaded_desires:
        # Determina la fonte dei desires
        source_info = "from Active Session" if st.session_state.loaded_desires[0].get('context') == 'Sessione Attiva' else "from global file"
        st.info(f"✅ {len(st.session_state.loaded_desires)} Desires loaded {source_info}")

        with st.expander("🎯 Available Desires"):
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
        st.info(f"📚 {len(st.session_state.base_beliefs_available)} Base Beliefs available in context")
        with st.expander("💡 Available Base Beliefs"):
            for idx, belief in enumerate(st.session_state.base_beliefs_available, 1):
                belief_desc = belief.get('belief_statement', belief.get('source', 'N/A'))
                st.markdown(f"**{idx}**. {belief_desc[:100]}...")

   # Quick action: Add belief manually
    with st.expander("➕ Add Belief Manually"):
        st.markdown("Fill in the fields to add a belief manually")

        belief_desc = st.text_area("Description", key="manual_belief_desc")
        belief_type = st.selectbox("Type", ["fact", "assumption", "principle", "constraint"], key="manual_belief_type")
        belief_confidence = st.selectbox("Confidence", ["high", "medium", "low"], key="manual_belief_confidence")

        # Multi-select per desires correlati
        if st.session_state.loaded_desires:
            # Crea options gestendo campi mancanti
            desire_options = {}
            for idx, d in enumerate(st.session_state.loaded_desires, 1):
                d_id = d.get('id', idx)
                d_desc = d.get('description', d.get('content', 'N/A'))
                desire_options[d_id] = f"#{d_id}: {d_desc[:50]}"

            selected_desires = st.multiselect(
                "Related Desires",
                options=list(desire_options.keys()),
                format_func=lambda x: desire_options[x],
                key="manual_belief_desires"
            )
        else:
            selected_desires = []

        belief_evidence = st.text_area("Evidence", key="manual_belief_evidence")

        if st.button("Add Belief"):
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
                st.success("✅ Belief added!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter at least a description")

    st.divider()

    # Configurazione
    st.header("⚙️ Believer Configuration")

    # Lazy load LLMManager e belief_auditor quando serve
    if 'llm_manager' not in st.session_state:
        from utils.llm_manager import LLMManager
        st.session_state.llm_manager = LLMManager()

    if 'belief_auditor' not in st.session_state:
        from utils.auditor import ConversationAuditor
        st.session_state.belief_auditor = ConversationAuditor(
            st.session_state.llm_manager,
            auditor_agent_name="belief_auditor"
        )

    # Selezione provider e modello (default dalla sessione)
    available_providers = st.session_state.llm_manager.get_available_providers()

    if not available_providers:
        st.error("⚠️ No LLM providers available!")
        st.info("Configure API keys in .env file:\n- GOOGLE_API_KEY\n- ANTHROPIC_API_KEY\n- OPENAI_API_KEY")
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
                "LLM Provider",
                available_providers,
                index=available_providers.index(default_provider),
                key="believer_provider",
                help="Provider configured from active session"
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
                    "Model",
                    options=list(models.keys()),
                    format_func=lambda x: models[x],
                    index=list(models.keys()).index(default_model),
                    key="believer_model",
                    help="Model configured from active session"
                )

    st.divider()


    # Controllo sessione
    st.subheader("🎬 Session Control")

    col_left, col_right = st.columns(2)

    with col_left:
        if st.button("🔄 New", width='stretch'):
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
        if st.button("✅ Complete", type="primary", width='stretch'):
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

                    st.success(f"✅ Session completed! {len(st.session_state.beliefs)} Beliefs saved to active session!")
                    st.balloons()
                elif len(st.session_state.believer_chat_history) > 1:
                    # Se ci sono messaggi ma nessun belief, salva solo la chat
                    st.session_state.session_manager.update_session_metadata(
                        st.session_state.active_session,
                        chat_history_believer=st.session_state.believer_chat_history
                    )

                    st.warning("⚠️ No beliefs identified, but the conversation has been saved to the session.")
                    st.info("💡 Tip: Ask Believer to generate the final report with identified beliefs.")
                else:
                    st.warning("⚠️ No conversation to save!")
            else:
                # Fallback: salva come prima in file locali se non c'è sessione attiva
                st.warning("⚠️ No active session! Saving to local files...")

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

                    st.info(f"💾 Beliefs saved to: {filename}")
                    st.info("💡 Tip: Activate a session in Compass to integrate it into the system!")
                else:
                    st.warning("⚠️ No data to save!")

    st.divider()

    # Visualizza beliefs
    if st.session_state.beliefs:
        st.subheader("💡 Identified Beliefs")
        for idx, belief in enumerate(st.session_state.beliefs, 1):
            # Usa .get() per accedere all'ID in modo sicuro, con un fallback all'indice del loop
            belief_id = belief.get('id', idx)
            belief_desc = belief.get('description', 'N/A')
            with st.expander(f"#{belief_id}: {belief_desc[:30]}..."):
                st.json(belief)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Messages", len(st.session_state.believer_chat_history))
    with col2:
        st.metric("Identified Beliefs", len(st.session_state.beliefs))
    with col3:
        stats = st.session_state.doc_processor.get_stats()
        st.metric("KB Contents", stats['document_count'])

# Main content
st.title("💡 Believer - Agent for Beliefs")
st.markdown("**Welcome! I am Believer and I'm here to help you identify Beliefs**")
st.divider()

# Check prerequisites
kb_stats = st.session_state.doc_processor.get_stats()
if kb_stats['document_count'] == 0:
    context_name = kb_stats.get('context', 'default')
    st.warning(f"⚠️ The knowledge base for context '{context_name}' is empty! Go to Knol to load documents before starting.")
    st.info(f"🎯 Current context: {active_session_data['config'].get('context', 'N/A')}")
    if st.button("📚 Go to Knol"):
        st.switch_page("pages/1_Knol.py")
    st.stop()

if not st.session_state.loaded_desires:
    # La funzione load_desires() viene chiamata nella sidebar e mostra già un errore se necessario
    st.warning("⚠️ No desires found or file is invalid. Check messages in sidebar.")
    if st.button("🎯 Go to Alì"):
        st.switch_page("pages/2_Ali.py")
    st.stop()

if not available_providers or provider is None:
    st.error("❌ No LLM provider configured. Configure API keys to continue.")
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
        greeting = f"""Hi! I'm Believer and I'm here to help you identify Beliefs. 💡

I've loaded your Desires:
{desires_summary}
{"..." if len(st.session_state.loaded_desires) > 3 else ""}

🔍 **I noticed there are already {len(st.session_state.base_beliefs_available)} Base Beliefs configured in this session's context.**

You can choose from four options:

**1. Chat to Create Specialized Beliefs** 🎯
   We can work together in conversational mode to identify more specific and detailed beliefs, focused on your Desires. These will complement the base beliefs and be more contextualized.

**2. Review Base Beliefs** 📋
   If you prefer to first review the already defined base beliefs, you can view them in Compass in the active context section.

**3. Create a Mix of Base Beliefs and Desire Beliefs** 🔄
   I will automatically generate a complete set without requiring further input. I'll analyze your Desires, generate specialized Beliefs for each one, and select only relevant Base Beliefs. The process is completely automatic.

**4. Generate Beliefs from Scratch** 🔄
   I will automatically generate a complete set without requiring further input, ignoring existing base beliefs and regenerating Beliefs by comparing the knowledge base with desires.

**What would you like to do?** Answer "1" for interactive chat, "2" to review base beliefs, "3" for complete automatic generation, or "4" for generation from scratch."""
    else:
        # Nessun belief di base o già controllato - procedi normalmente
        greeting = f"""Hi! I'm Believer and I'm here to help you identify Beliefs. 💡

I've loaded your Desires:
{desires_summary}
{"..." if len(st.session_state.loaded_desires) > 3 else ""}

Now we'll work together to identify the beliefs, facts, and principles that are relevant to achieving these desires. Let's start exploring your knowledge base!"""

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

            rubric = audit_payload.get("rubric") or {}
            if isinstance(rubric, dict) and rubric:
                rubric_labels = [
                    ("coerenza_domanda", "Question coherence"),
                    ("contesto_conservato", "Context preserved"),
                    ("specificita_belief", "Belief specificity"),
                    ("struttura_belief", "Belief structure"),
                    ("evidenze_fonte", "Evidence or source"),
                    ("gestione_json", "Finalization/JSON handling"),
                ]
                st.markdown("**Rubric scores:**")
                for key, label in rubric_labels:
                    item = rubric.get(key) or {}
                    score = item.get("score")
                    notes = (item.get("notes") or "").strip()
                    score_text = f"{score}/5" if isinstance(score, int) else "N/D"
                    if notes:
                        st.write(f"- {label}: {score_text} — {notes}")
                    else:
                        st.write(f"- {label}: {score_text}")

            issues = audit_payload.get("issues") or []
            if issues:
                st.markdown("**Detected issues:**")
                for issue in issues:
                    issue_type = issue.get("type", "issue")
                    severity = issue.get("severity", "low")
                    message_text = issue.get("message", "")
                    st.write(f"- ({severity.upper()} · {issue_type}) {message_text}")

            improvements = audit_payload.get("assistant_improvements") or []
            if improvements:
                st.markdown("**Suggestions for agent:**")
                for idea in improvements:
                    st.write(f"- {idea}")

            next_focus = audit_payload.get("next_focus")
            if next_focus:
                st.caption(f"Next focus: {next_focus}")

            confidence = audit_payload.get("confidence")
            if confidence:
                st.caption(f"Assessment confidence: {confidence}")

believer_suggestions_placeholder = st.empty()

# Gestisci la chat conversazionale per i belief specializzati
if st.session_state.believer_specialized_chat_active and not st.session_state.base_beliefs_available:
    # In modalità chat specializzata senza belief di base
    pass  # La chat continuerà normalmente sotto
elif st.session_state.believer_specialized_chat_active and st.session_state.base_beliefs_available:
    # In modalità chat specializzata con belief di base già caricati
    pass  # La chat continuerà normalmente sotto

# Mostra i pulsanti pills se ci sono belief di base e l'utente non ha ancora scelto
if st.session_state.base_beliefs_available and not st.session_state.base_beliefs_checked and st.session_state.believer_greeted and not st.session_state.believer_specialized_chat_active:
    st.markdown("---")

    # Usa columns per mettere i pulsanti in fila
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🎯 Chat to Create Specialized Beliefs", key="btn_create_beliefs", width='stretch'):
            # Simula la scelta dell'opzione 1
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "1"
            })
            st.session_state.base_beliefs_checked = True
            st.session_state.believer_specialized_chat_active = True

            response = """Great! Let's proceed to create specialized beliefs for your Desires in conversational mode. 🎯

These beliefs will be more specific and detailed compared to base beliefs, and will be directly linked to your objectives.

Let's start exploring your knowledge base to identify relevant beliefs. Tell me, which desire do you want to focus on first?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    with col2:
        if st.button("📋 Review Base Beliefs", key="btn_verify_beliefs", width='stretch'):
            # Simula la scelta dell'opzione 2
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "2"
            })

            # Marca i belief di base come controllati per nascondere i pulsanti
            st.session_state.base_beliefs_checked = True

            response = """Perfect! I recommend going to **Compass** to view your session's Base Beliefs.

In Compass you can:
- 📋 View all configured base beliefs
- ✏️ Modify or update them if necessary
- 🔍 Analyze them in detail

Once you've reviewed the base beliefs, come back here if you want to create more specialized beliefs for your Desires.

👉 Use the "🧭 Go to Compass" button in the sidebar to navigate!"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            # Imposta un flag per mostrare il pulsante Compass
            st.session_state.show_compass_button = True
            st.rerun()

    with col3:
        if st.button("🔄 Create Mix of Base Beliefs and Desire Beliefs", key="btn_mix_beliefs", width='stretch'):
            # Simula la scelta dell'opzione 3
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "3"
            })
            st.session_state.base_beliefs_checked = True

            # Avvia il processo automatico di mix
            with st.spinner(get_random_thinking_message()):
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
                    response = f"""Perfect! I've completed automatic analysis of your Desires and Base Beliefs. 🔄

I created a complete and optimal set that includes:
- ✨ **Specialized beliefs**: Generated specifically to support each of your Desires
- 📚 **Selected Base Beliefs**: Only those relevant and directly linked to your objectives

Here's the result:

{mix_response}

✅ Beliefs have been generated and saved automatically. You can view them in the sidebar or export them using the button at the bottom of the page."""

                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                    # Parsing JSON per estrarre i beliefs dal mix
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
                                    # Mantieni la struttura completa del belief dal JSON dell'LLM
                                    belief_copy = b.copy()
                                    belief_copy["id"] = next_id + len(extracted_beliefs)

                                    # Aggiungi timestamp se non presente
                                    if "timestamp" not in belief_copy:
                                        belief_copy["timestamp"] = datetime.now().isoformat()

                                    extracted_beliefs.append(belief_copy)

                                if extracted_beliefs:
                                    st.session_state.beliefs.extend(extracted_beliefs)
                                    st.session_state.session_manager.update_bdi_data(
                                        st.session_state.active_session,
                                        beliefs=st.session_state.beliefs
                                    )
                        except (json.JSONDecodeError, Exception):
                            pass  # Se il parsing fallisce, ignora silenziosamente

                except Exception as e:
                    response = f"❌ An error occurred during mix generation: {str(e)}\n\nYou can try choosing one of the other options or contact support."
                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

            st.rerun()

    with col4:
        if st.button("🎯 Generate Beliefs from Scratch", key="btn_from_scratch", width='stretch', help="Generate beliefs directly from KB chunks, ignoring base beliefs"):
            # Simula la scelta dell'opzione 4
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "4"
            })
            st.session_state.base_beliefs_checked = True

            # Imposta flag per avviare generazione da zero
            st.session_state.from_scratch_generation_requested = True
            st.rerun()

    st.markdown("---")

# === MODE 4: FROM SCRATCH GENERATION ===
if 'from_scratch_generation_requested' in st.session_state and st.session_state.from_scratch_generation_requested:
    st.session_state.from_scratch_generation_requested = False  # Reset flag

    # Verifica desires disponibili
    if not st.session_state.loaded_desires:
        st.error("⚠️ No desires available. Go to Alì to define desires first.")
        st.stop()

    # Verifica KB non vuota
    kb_stats = st.session_state.doc_processor.get_stats()
    if kb_stats['document_count'] == 0:
        st.error("⚠️ Empty knowledge base. Load documents in Knol first.")
        st.stop()

    # Mostra messaggio di avvio nella chat
    with st.chat_message("assistant"):
        progress_placeholder = st.empty()
        progress_placeholder.markdown("🎯 **Starting belief generation from scratch...**\n\n⏳ Preparing context...")

    # Avvia processo con spinner
    with st.spinner(get_random_thinking_message()):
        try:
            # STEP 1: Prepare desires context
            desires_context = "USER DESIRES:\n\n"
            for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                desire_id = desire.get('id', f'D{idx}')
                desire_desc = desire.get('description', desire.get('content', 'N/A'))
                desire_priority = desire.get('priority', 'N/A')
                desires_context += f"- **Desire {desire_id}**: {desire_desc} (Priority: {desire_priority})\n"

            # STEP 2: Query KB for each desire
            progress_placeholder.markdown("🎯 **Generating beliefs from scratch...**\n\n🔍 Querying knowledge base for desires...")

            desire_to_chunks = {}
            query_details = []

            for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                desire_id = desire.get('id', f'D{idx}')
                desire_desc = desire.get('description', desire.get('content', 'N/A'))

                # Query top-10 chunks (user preference: balanced coverage)
                query_results = st.session_state.doc_processor.query(
                    query_text=desire_desc,
                    n_results=10
                )

                # Format chunks
                chunks_text = []
                if query_results and 'documents' in query_results:
                    for doc_list in query_results['documents']:
                        for doc in doc_list:
                            chunks_text.append(doc)

                desire_to_chunks[desire_id] = chunks_text
                query_details.append(f"- Desire {desire_id}: {len(chunks_text)} chunks found")

            # STEP 3: Format chunks context
            progress_placeholder.markdown(f"🎯 **Generating beliefs from scratch...**\n\n📝 Formatting context...\n\n" + "\n".join(query_details))

            chunks_context = "CHUNKS FROM KNOWLEDGE BASE:\n\n"
            for desire_id, chunks in desire_to_chunks.items():
                chunks_context += f"### [Desire {desire_id}]\n\n"
                for i, chunk in enumerate(chunks, 1):
                    chunks_context += f"**Chunk {i}:**\n{chunk}\n\n"

            # STEP 4: Load prompt template
            from_scratch_template = get_prompt('believer', use_cache=False, prompt_suffix='from_scratch_prompt')

            # Template substitution
            from_scratch_prompt = from_scratch_template.replace('{desires_context}', desires_context)
            from_scratch_prompt = from_scratch_prompt.replace('{chunks_context}', chunks_context)

            # STEP 5: LLM call
            progress_placeholder.markdown(f"🎯 **Generating beliefs from scratch...**\n\n🤖 Analyzing with LLM...\n\n" + "\n".join(query_details))

            from_scratch_response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=[{"role": "user", "content": from_scratch_prompt}],
                system_prompt=None,
                max_tokens=8192,
                temperature=0.5  # Balanced mode: medium-high relevance (user preference)
            )

            # STEP 6: Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', from_scratch_response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{[\s\S]*\}', from_scratch_response)

            if json_match:
                json_text = json_match.group(1) if '```json' in from_scratch_response else json_match.group(0)
                parsed_json = json.loads(json_text)

                extracted_beliefs = parsed_json.get("beliefs", [])

                if extracted_beliefs:
                    # STEP 7: Assign IDs & timestamps
                    existing_ids = [b.get("id", 0) for b in st.session_state.beliefs]
                    next_id = max(existing_ids) + 1 if existing_ids else 1

                    for i, b in enumerate(extracted_beliefs):
                        belief_copy = b.copy()
                        belief_copy["id"] = next_id + i
                        if "timestamp" not in belief_copy:
                            belief_copy["timestamp"] = datetime.now().isoformat()
                        st.session_state.beliefs.append(belief_copy)

                    # STEP 8: Save to session
                    st.session_state.session_manager.update_bdi_data(
                        st.session_state.active_session,
                        beliefs=st.session_state.beliefs
                    )

                    # Update final message
                    success_msg = f"""✅ **Generation from scratch completed!** {len(extracted_beliefs)} new beliefs added.

Beliefs have been extracted directly from knowledge base chunks and are now available in the sidebar. Each belief has been classified for relevance to desires and includes citation of the original source.

📊 **Generation summary:**
- Desires analyzed: {len(st.session_state.loaded_desires)}
- Chunks processed: {sum(len(chunks) for chunks in desire_to_chunks.values())}
- Beliefs extracted: {len(extracted_beliefs)}

You can view beliefs in the sidebar or export them using the button at the bottom of the page."""

                    progress_placeholder.markdown(success_msg)

                    st.session_state.believer_chat_history.append({
                        "role": "assistant",
                        "content": success_msg
                    })

                    st.rerun()
                else:
                    error_msg = "⚠️ No beliefs extracted from JSON."
                    progress_placeholder.error(error_msg)
            else:
                # User preference: generic error message (no raw response)
                error_msg = "⚠️ Unable to extract JSON from LLM response. Please try again or contact support."
                progress_placeholder.error(error_msg)

        except json.JSONDecodeError as e:
            # User preference: generic error message
            error_msg = "❌ JSON parsing error. Response format is invalid."
            progress_placeholder.error(error_msg)
        except Exception as e:
            error_msg = f"❌ Error during generation: {str(e)}"
            progress_placeholder.error(error_msg)

# Chat input (supporta suggerimenti automatici dell'Auditor)
auto_prompt = None
if isinstance(st.session_state.believer_pending_prompt, str):
    auto_prompt = st.session_state.believer_pending_prompt.strip()
    st.session_state.believer_pending_prompt = None

user_prompt = st.chat_input("Write your message...")
prompt = auto_prompt or user_prompt

# Gestisci la conversazione della chat specializzata
if st.session_state.believer_specialized_chat_active and prompt and prompt.strip() not in ["1", "2", "3"]:
    # L'utente sta scrivendo nella chat specializzata (non è una risposta ai pulsanti)

    # Add user message
    st.session_state.believer_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Chiama l'LLM con il system prompt di Believer
    with st.spinner(get_random_thinking_message()):
        try:
            # Prepara il contesto da includere nel prompt
            desires_context = "\n## DESIRES DELL'UTENTE:\n"
            for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                desire_id = desire.get('id', idx)
                desire_desc = desire.get('description', desire.get('content', 'N/A'))
                desire_priority = desire.get('priority', 'N/A')
                desires_context += f"- **Desire #{desire_id}**: {desire_desc} (Priorità: {desire_priority})\n"

            # Prepara i parametri per la chiamata LLM
            messages = st.session_state.believer_chat_history.copy()

            # Aggiorna il messaggio di sistema per includere i desire
            system_prompt = BELIEVER_SYSTEM_PROMPT + desires_context

            # Get LLM settings from session
            llm_settings = active_session_data['config'].get('llm_settings', {})
            use_defaults = llm_settings.get('use_defaults', False)

            # Prepara i parametri della chiamata
            chat_params = {
                'provider': provider,
                'model': model,
                'messages': messages,
                'system_prompt': system_prompt
            }

            # Aggiungi parametri custom solo se use_defaults è False
            if not use_defaults:
                chat_params['temperature'] = llm_settings.get('temperature', 1.0)
                chat_params['top_p'] = llm_settings.get('top_p', 0.95 if provider == "Gemini" else 1.0)

                # Max tokens
                if provider == "Gemini":
                    chat_params['max_output_tokens'] = min(llm_settings.get('max_output_tokens', 8192), 8192)
                else:
                    chat_params['max_tokens'] = min(llm_settings.get('max_tokens', 4096), 4096)

                # Reasoning effort - solo per GPT-5
                if model and model.startswith('gpt-5'):
                    chat_params['reasoning_effort'] = llm_settings.get('reasoning_effort', 'medium')

            # Chiama l'LLM
            response = st.session_state.llm_manager.chat(**chat_params)

            # Aggiungi la risposta alla chat history
            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            # Mostra la risposta
            with st.chat_message("assistant"):
                st.markdown(response)

            # Visualizzazione compressa del RAG context e Desires
            with st.expander("📚 Context & Desires Details", expanded=False):
                if st.session_state.loaded_desires:
                    st.markdown("**🎯 User Desires:**")
                    for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                        desire_id = desire.get('id', idx)
                        desire_desc = desire.get('description', desire.get('content', 'N/A'))
                        desire_priority = desire.get('priority', 'N/A')
                        st.markdown(f"- **#{desire_id}**: {desire_desc} (Priority: {desire_priority})")
                    st.divider()

                if st.session_state.base_beliefs_available:
                    st.markdown("**💡 Available Base Beliefs:**")
                    for idx, belief in enumerate(st.session_state.base_beliefs_available, 1):
                        belief_desc = belief.get('belief_statement', belief.get('source', 'N/A'))
                        with st.expander(f"Base Belief {idx}", expanded=False):
                            st.markdown(belief_desc)
                else:
                    st.info("No base beliefs available")

        except Exception as e:
            error_msg = f"❌ Chat error: {str(e)}"
            st.error(error_msg)
            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": error_msg
            })

    st.rerun()

elif prompt:
    # Add user message
    st.session_state.believer_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Check se l'utente sta rispondendo alla domanda sui belief di base
    if st.session_state.base_beliefs_available and not st.session_state.base_beliefs_checked:
        if "2" in prompt.strip() or "review" in prompt.lower() or "base beliefs" in prompt.lower():
            # L'utente vuole verificare i belief di base
            response = """Perfect! I recommend going to **Compass** to view the Base Beliefs of your context.

In Compass you can:
- 📋 View all configured base beliefs
- ✏️ Modify or update them if necessary
- 🔍 Analyze them in detail

Once you've reviewed the base beliefs, come back here if you want to create more specialized beliefs for your Desires.

👉 Use the "🧭 Go to Compass" button in the sidebar to navigate!"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            st.stop()

        elif "1" in prompt.strip() or "create" in prompt.lower() or "new" in prompt.lower() or "specialized" in prompt.lower() or "chat" in prompt.lower():
            # L'utente vuole creare nuovi belief specializzati
            st.session_state.base_beliefs_checked = True
            st.session_state.believer_specialized_chat_active = True

            response = """Great! Let's proceed to create specialized beliefs for your Desires in conversational mode. 🎯

These beliefs will be more specific and detailed compared to base beliefs, and will be directly linked to your objectives.

Let's start exploring your knowledge base to identify relevant beliefs. Tell me, which desire do you want to focus on first?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            st.rerun()

        elif "3" in prompt.strip() or "mix" in prompt.lower() or "automatic" in prompt.lower():
            # L'utente vuole creare il mix automatico
            st.session_state.base_beliefs_checked = True

            # Avvia il processo automatico di mix
            with st.spinner(get_random_thinking_message()):
                try:
                    # Prepara il contesto per l'LLM
                    desires_context = "USER DESIRES:\n"
                    for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                        desire_id = desire.get('id', idx)
                        desire_desc = desire.get('description', desire.get('content', 'N/A'))
                        desire_priority = desire.get('priority', 'N/A')
                        desires_context += f"- Desire #{desire_id}: {desire_desc} (Priority: {desire_priority})\n"

                    # Passa l'intero JSON dei belief di base per un'analisi completa
                    base_beliefs_json = json.dumps(st.session_state.base_beliefs_available, indent=2, ensure_ascii=False)
                    base_beliefs_context = f"\n\nAVAILABLE BASE BELIEFS (in JSON format):\n```json\n{base_beliefs_json}\n```"

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
                    response = f"""Perfect! I've completed automatic analysis of your Desires and Base Beliefs. 🔄

I created a complete and optimal set that includes:
- ✨ **Specialized beliefs**: Generated specifically to support each of your Desires
- 📚 **Selected Base Beliefs**: Only those relevant and directly linked to your objectives

Here's the result:

{mix_response}

✅ Beliefs have been generated and saved automatically. You can view them in the sidebar or export them using the button at the bottom of the page."""

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
                                    # Mantieni la struttura completa del belief dal JSON dell'LLM
                                    belief_copy = b.copy()
                                    belief_copy["id"] = next_id + len(extracted_beliefs)

                                    # Aggiungi timestamp se non presente
                                    if "timestamp" not in belief_copy:
                                        belief_copy["timestamp"] = datetime.now().isoformat()

                                    extracted_beliefs.append(belief_copy)

                                if extracted_beliefs:
                                    st.session_state.beliefs.extend(extracted_beliefs)
                                    st.session_state.session_manager.update_bdi_data(
                                        st.session_state.active_session,
                                        beliefs=st.session_state.beliefs
                                    )
                                    st.success(f"✅ Automatic mix completed! {len(extracted_beliefs)} new beliefs added.")
                                else:
                                    st.warning("⚠️ JSON received, but no valid beliefs found.")
                        except json.JSONDecodeError:
                            st.error("❌ The JSON generated by the LLM for the mix is invalid.")
                        except Exception as parse_exc:
                            st.error(f"❌ Error during JSON parsing for the mix: {parse_exc}")
                    # --- FINE LOGICA DI PARSING ---

                    with st.chat_message("assistant"):
                        st.markdown(response)

                except Exception as e:
                    response = f"❌ An error occurred during mix generation: {str(e)}\n\nYou can try choosing one of the other options or contact support."
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
                                    # Mantieni la struttura completa del belief dal JSON dell'LLM
                                    belief_copy = b.copy()
                                    belief_copy["id"] = next_id + len(extracted_beliefs)

                                    # Aggiungi timestamp se non presente
                                    if "timestamp" not in belief_copy:
                                        belief_copy["timestamp"] = datetime.now().isoformat()

                                    extracted_beliefs.append(belief_copy)

                                if extracted_beliefs:
                                    st.session_state.beliefs.extend(extracted_beliefs)
                                    st.session_state.session_manager.update_bdi_data(
                                        st.session_state.active_session,
                                        beliefs=st.session_state.beliefs
                                    )
                                    st.success(f"✅ Automatic mix completed! {len(extracted_beliefs)} new beliefs added.")
                                else:
                                    st.warning("⚠️ JSON received, but no valid beliefs found.")
                        except json.JSONDecodeError:
                            st.error("❌ The JSON generated by the LLM for the mix is invalid.")
                        except Exception as parse_exc:
                            st.error(f"❌ Error during JSON parsing for the mix: {parse_exc}")
                    # --- FINE LOGICA DI PARSING ---
                    with st.chat_message("assistant"):
                        st.markdown(response)

            st.stop()

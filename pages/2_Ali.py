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
from utils.context_manager import ContextManager
from utils.auditor import ConversationAuditor
from utils.ui_messages import get_random_thinking_message

ALI_MODULE_GOAL = (
    "Guide the domain owner to collect and formalize concrete desires, "
    "motivations and success metrics for a single user category inferred from the conversation."
)
ALI_EXPECTED_OUTCOME = (
    "Progress towards confirming or creating a well-formulated desire, "
    "keeping the dialogue focused and action-oriented."
)

st.set_page_config(
    page_title="Alì - LumIA Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LLMManager non viene inizializzato qui - viene caricato lazy quando serve (Configurazione Alì)

if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'context_manager' not in st.session_state:
    st.session_state.context_manager = ContextManager()

if 'ali_chat_history' not in st.session_state:
    st.session_state.ali_chat_history = []
    st.session_state.ali_greeted = False

if 'desires' not in st.session_state:
    st.session_state.desires = []

if 'ali_audit_trail' not in st.session_state:
    st.session_state.ali_audit_trail = []

if 'ali_suggestions' not in st.session_state:
    st.session_state.ali_suggestions = []

if 'ali_pending_prompt' not in st.session_state:
    st.session_state.ali_pending_prompt = None

# desires_auditor viene inizializzato quando serve con LLMManager

# Carica la sessione attiva se presente
# Se non c'è active_session, prova a caricare l'ultima sessione attiva
if 'active_session' not in st.session_state or not st.session_state.active_session:
    # Fallback: carica l'ultima sessione attiva disponibile
    all_sessions = st.session_state.session_manager.get_all_sessions(status="active")
    if all_sessions:
        # Usa la più recentemente acceduta
        latest_session = max(all_sessions, key=lambda s: s['metadata'].get('last_accessed', ''))
        st.session_state.active_session = latest_session['session_id']

if 'active_session' in st.session_state and st.session_state.active_session:
    active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
    if active_session_data:
        # Carica i desires dalla sessione (formato single-beneficiario)
        bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.active_session)
        if bdi_data:
            st.session_state.active_beneficiario = (
                bdi_data.get("beneficiario")
                or bdi_data.get("persona")
                or st.session_state.get("active_beneficiario")
            )
        if bdi_data and not st.session_state.desires:
            extracted = []
            beneficiario = bdi_data.get("beneficiario") or bdi_data.get("persona") or {}
            beneficiario_name = (
                beneficiario.get("beneficiario_name")
                or beneficiario.get("persona_name")
                or "Beneficiario primario"
            )
            # Memorizza il beneficiario della sessione per riuso automatico
            st.session_state.active_beneficiario = beneficiario
            for desire in bdi_data.get("desires", []) or []:
                extracted.append({
                    "id": desire.get("desire_id", f"gen_{len(extracted)+1}"),
                    "description": desire.get("desire_statement") or desire.get("description", "N/A"),
                    "priority": desire.get("priority", "medium"),
                    "context": f"Beneficiario: {beneficiario_name}",
                    "success_criteria": "\n".join(desire.get("success_metrics", [])),
                    "timestamp": desire.get("timestamp", datetime.now().isoformat())
                })
            st.session_state.desires = extracted
        
        # Prepara il DocumentProcessor con il contesto della sessione (lazy initialization)
        session_context = active_session_data['config'].get('context')
        if session_context and session_context != 'none':
            # Normalizza il nome del contesto per il path
            normalized_context = st.session_state.context_manager._normalize_name(session_context)

            # Inizializza o aggiorna il DocumentProcessor per il contesto della sessione
            # NOTA: initialize_db() viene chiamato solo al primo uso (query RAG)
            if 'doc_processor' not in st.session_state or st.session_state.get('current_context') != normalized_context:
                st.session_state.doc_processor = DocumentProcessor(context_name=normalized_context)
                st.session_state.current_context = normalized_context
                st.session_state.doc_processor_initialized = False  # Flag per lazy init
        else:
            # Fallback alla directory predefinita se non c'è contesto
            if 'doc_processor' not in st.session_state:
                st.session_state.doc_processor = DocumentProcessor()
                st.session_state.doc_processor_initialized = False
else:
    # Se non c'è sessione attiva, usa directory predefinita (lazy init)
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
        st.session_state.doc_processor_initialized = False

# Carica il system prompt da file
ALI_SYSTEM_PROMPT = get_prompt('ali')

def get_context_description():
    """Retrieves the knowledge-base description for the active session's context.

    The description is generated automatically in Knol during belief
    extraction and stored in ``context_metadata.json``.  It is used here
    to personalise Alì's opening greeting so the user immediately sees
    which domain they are working in.

    Returns:
        str | None: The trimmed description string, or ``None`` when any
        of the following conditions are true:

        * No active session exists.
        * The session has no associated context.
        * The context metadata file is missing or has an empty description.
        * Any unexpected exception is raised during the lookup.
    """
    try:
        # Ottieni il contesto dalla sessione attiva
        if 'active_session' not in st.session_state or not st.session_state.active_session:
            return None

        session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if not session_data:
            return None

        context_name = session_data['config'].get('context')
        if not context_name or context_name == 'none':
            return None

        # Carica il metadata del contesto
        context_metadata = st.session_state.context_manager.get_context(context_name)
        if not context_metadata:
            return None

        # Ritorna la descrizione se presente
        description = context_metadata.get('description', '').strip()
        return description if description else None

    except Exception as e:
        # Non mostrare warning se è solo mancanza di descrizione
        return None


def render_quick_replies(placeholder, suggestions, pending_state_key, button_prefix):
    """Renders the Auditor's quick-reply suggestion buttons inside a Streamlit placeholder.

    Each suggestion is shown as a clickable button laid out in rows of
    three.  When a button is pressed its ``message`` value is written to
    ``st.session_state[pending_state_key]``; the main chat loop picks
    that value up on the next rerun and injects it as the user's input.

    The placeholder is emptied first so that stale suggestions from a
    previous turn are cleared before new ones appear.

    Args:
        placeholder: A ``st.empty()`` placeholder that owns the rendered
            widgets.
        suggestions: List of suggestion dicts, each expected to contain:

            * ``"message"`` (str) – the text injected as user input.
            * ``"label"`` (str, optional) – button display text; falls
              back to ``message``.
            * ``"why"`` (str, optional) – a caption shown below the
              button explaining the suggestion.
        pending_state_key: The ``st.session_state`` key where the
            selected message is stored for the chat loop to consume.
        button_prefix: A unique string prepended to each button's
            ``key`` to avoid Streamlit key collisions across reruns.
    """
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
                    if st.button(label, key=f"{button_prefix}_suggestion_{i + col_idx}", width='stretch'):
                        if message_text:
                            st.session_state[pending_state_key] = message_text
                    if reason:
                        st.caption(reason)

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

# CONTROLLO SESSIONE OBBLIGATORIO
if 'active_session' not in st.session_state or not st.session_state.active_session:
    st.error("⚠️ No active session! Alì requires an active session to work.")
    st.info("📝 Configure a session in Compass before using Alì.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧭 Go to Compass", width='stretch', type="primary"):
            st.switch_page("pages/0_Compass.py")

    st.stop()  # Ferma l'esecuzione se non c'è sessione

# Se arriviamo qui, la sessione esiste - caricala
active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
if not active_session_data:
    st.error("❌ Error: Active session not found in database!")
    if st.button("🧭 Go to Compass", type="primary", width='stretch'):
        st.switch_page("pages/0_Compass.py")
    st.stop()

# Sidebar per configurazione
with st.sidebar:
    # Header con logo e pulsante home sulla stessa riga
    col_logo, col_home = st.columns([3, 1])

    with col_logo:
        st.markdown("<div style='padding-top: 0px;'><h2>✨ LumIA Studio</h2></div>", unsafe_allow_html=True)

    with col_home:
        if st.button("🏠", width='stretch', type="secondary", help="Back to Home"):
            st.switch_page("app.py")

    st.divider()

    # Mostra sessione attiva
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.success(f"📍 Active Session: **{active_session_data['metadata']['name']}**")
            st.caption(f"🗂️ Context: {active_session_data['config'].get('context', 'N/A')}")
            if st.session_state.get("active_beneficiario"):
                beneficiario = st.session_state["active_beneficiario"]
                beneficiario_name = beneficiario.get("beneficiario_name") or beneficiario.get("persona_name", "N/A")
                beneficiario_desc = (beneficiario.get("beneficiario_description") or beneficiario.get("persona_description", "")).strip()
                st.info(f"Current beneficiary: **{beneficiario_name}**" + (f" - {beneficiario_desc}" if beneficiario_desc else ""))

            # Mostra informazioni sulla base di conoscenza caricata
            kb_stats = st.session_state.doc_processor.get_stats()
            if kb_stats['document_count'] > 0:
                st.success(f"📚 KB Loaded: {kb_stats['document_count']} documents")
                st.caption(f"🎯 Context: {kb_stats['context']}")
            else:
                st.warning("⚠️ Empty knowledge base for this context")
                st.caption(f"🎯 Context: {kb_stats['context']}")

            if st.button("🧭 Go to Compass", width='stretch'):
                st.switch_page("pages/0_Compass.py")
        else:
            st.warning("⚠️ Active session not found")
    else:
        st.info("ℹ️ No active session")
        if st.button("🧭 Activate a session", width='stretch'):
            st.switch_page("pages/0_Compass.py")

    st.divider()

    # Configurazione
    st.header("⚙️ Alì Configuration")

    # Lazy load LLMManager e desires_auditor quando serve
    if 'llm_manager' not in st.session_state:
        from utils.llm_manager import LLMManager
        st.session_state.llm_manager = LLMManager()

    if 'desires_auditor' not in st.session_state:
        st.session_state.desires_auditor = ConversationAuditor(
            st.session_state.llm_manager,
            auditor_agent_name="desires_auditor"
        )

    # Selezione provider e modello (default dalla sessione)
    available_providers = st.session_state.llm_manager.get_available_providers()
    model = None

    if not available_providers:
        st.error("⚠️ No LLM provider available!")
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
            provider = st.selectbox(
                "LLM Provider",
                available_providers,
                index=available_providers.index(default_provider),
                key="ali_provider",
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
                    key="ali_model",
                    help="Model configured from active session"
                )

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Session Control")

    if st.button("🔄 New Conversation", width='stretch'):
        st.session_state.ali_chat_history = []
        st.session_state.ali_greeted = False
        st.session_state.ali_audit_trail = []
        st.session_state.ali_suggestions = []
        st.session_state.ali_pending_prompt = None
        st.rerun()

    if st.button("Complete Session", type="primary", width='stretch'):
        # Verifica se c'e' una sessione attiva
        if 'active_session' in st.session_state and st.session_state.active_session:
            if st.session_state.desires:
                existing_bdi = st.session_state.session_manager.get_bdi_data(st.session_state.active_session) or {}
                beneficiario_info = existing_bdi.get("beneficiario") or existing_bdi.get("persona") or {}
                domain_summary = existing_bdi.get("domain_summary", "")

                bdi_desires = []
                for i, d in enumerate(st.session_state.desires):
                    success_metrics = (d.get("success_criteria") or "").splitlines() if d.get("success_criteria") else []
                    bdi_desires.append({
                        "desire_id": d.get("id", f"gen_{i+1}"),
                        "desire_statement": d.get("description", "N/A"),
                        "priority": d.get("priority", "medium"),
                        "success_metrics": success_metrics
                    })

                st.session_state.session_manager.update_bdi_data(
                    st.session_state.active_session,
                    desires=bdi_desires,
                    beneficiario=beneficiario_info,
                    domain_summary=domain_summary
                )

                st.session_state.session_manager.update_session_metadata(
                    st.session_state.active_session,
                    
                )

                st.success(f"Session completed! {len(st.session_state.desires)} Desires saved in active session.")
                st.balloons()
            elif len(st.session_state.ali_chat_history) > 1:
                st.session_state.session_manager.update_session_metadata(
                    st.session_state.active_session,

                )

                st.warning("No desires identified, but the conversation has been saved in the session.")
                st.info("Tip: ask Alì to generate the final report with identified desires.")
            else:
                st.warning("No conversation to save!")
        else:
            # Fallback: salva su file locali se non c'e' sessione attiva
            st.warning("No active session! Saving to local files...")

            if st.session_state.desires:
                fallback_bdi = {
                    "timestamp": datetime.now().isoformat(),
                    "domain_summary": "",
                    "beneficiario": {
                        "beneficiario_name": "Utente",
                        "beneficiario_description": "",
                        "beneficiario_inference_notes": []
                    },
                    "desires": [
                        {
                            "desire_id": d.get("id", f"gen_{i+1}"),
                            "desire_statement": d.get("description", "N/A"),
                            "priority": d.get("priority", "medium"),
                            "success_metrics": (d.get("success_criteria") or "").splitlines() if d.get("success_criteria") else []
                        }
                        for i, d in enumerate(st.session_state.desires)
                    ],
                    "beliefs": [],
                    "intentions": []
                }

                os.makedirs("./data/sessions", exist_ok=True)
                filename = f"./data/sessions/bdi_desires_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(fallback_bdi, f, ensure_ascii=False, indent=2)

                with open("./data/current_bdi.json", 'w', encoding='utf-8') as f:
                    json.dump(fallback_bdi, f, ensure_ascii=False, indent=2)

                st.info(f"BDI (desires) saved in: {filename}")
                st.info("Tip: Activate a session in Compass to integrate it into the system!")
            else:
                st.warning("No data to save!")

    st.divider()

    # Quick action: Add desire manually
    with st.expander("➕ Add Desire Manually"):
        st.markdown("Fill in the fields to add a desire manually")

        desire_desc = st.text_area("Description", key="manual_desire_desc")
        desire_priority = st.selectbox("Priority", ["high", "medium", "low"], key="manual_desire_priority")
        desire_context = st.text_area("Context", key="manual_desire_context")
        desire_criteria = st.text_area("Success Criteria", key="manual_desire_criteria")

        if st.button("Add Desire", width='stretch'):
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
                st.success("✅ Desire added!")
                st.rerun()
            else:
                st.warning("⚠️ Enter at least a description")

    # Visualizza desires
    if st.session_state.desires:
        st.subheader("🎯 Identified Desires")
        for idx, desire in enumerate(st.session_state.desires, 1):
            # Usa 'id' se presente, altrimenti usa l'indice
            desire_id = desire.get('id', idx)
            desire_desc = desire.get('description', desire.get('content', 'N/A'))
            with st.expander(f"#{desire_id}: {desire_desc[:50]}..."):
                st.json(desire)

    # Statistiche in basso
    st.divider()
    st.subheader("📊 Statistics")
    st.metric("Messages", len(st.session_state.ali_chat_history))
    st.metric("Identified Desires", len(st.session_state.desires))

    stats = st.session_state.doc_processor.get_stats()
    st.metric("KB Contents", stats['document_count'])

# Main content
st.title("🎯 Alì - Agent for Desires")
st.markdown("**Welcome! I'm here to help you identify and define your Desires**")
st.divider()

# Check se la KB è vuota
kb_stats = st.session_state.doc_processor.get_stats()
if kb_stats['document_count'] == 0:
    context_name = kb_stats.get('context', 'default')
    st.warning(f"⚠️ The knowledge base for context '{context_name}' is empty! Go to Knol to upload documents before starting.")
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.info(f"🎯 Current context: {active_session_data['config'].get('context', 'N/A')}")
    if st.button("📚 Go to Knol", width='stretch'):
        st.switch_page("pages/1_Knol.py")
    st.stop()

# Check provider disponibile
if not available_providers or provider is None:
    st.error("❌ No LLM provider configured. Configure API keys to continue.")
    st.stop()

# Saluto iniziale
if not st.session_state.ali_greeted:
    # Carica la descrizione del contesto dal metadata
    context_description = get_context_description()

    # Costruisci il messaggio di saluto
    if context_description:
        greeting = f"Hello! I'm Alì and I'm here to help you find your Desires. 🎯\n\nYou created a context about: {context_description}\n\nNow I can help you identify clear and achievable goals in your domain. Tell me, what do you want to accomplish?"
    else:
        greeting = "Hello! I'm Alì and I'm here to help you find your Desires. 🎯\n\nI have access to your knowledge base and can help you identify clear and achievable goals in your domain. Tell me, what do you want to accomplish?"

    st.session_state.ali_chat_history.append({
        "role": "assistant",
        "content": greeting
    })
    st.session_state.ali_greeted = True

# Display chat history
audit_map = {
    item["message_index"]: item.get("result", {})
    for item in st.session_state.ali_audit_trail
    if isinstance(item, dict) and "message_index" in item
}

for idx, message in enumerate(st.session_state.ali_chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    if message.get("role") == "assistant" and idx in audit_map:
        audit_payload = audit_map[idx] or {}
        with st.chat_message("system"):
            status = audit_payload.get("status", "pass")
            icon = "✅" if status == "pass" else "⚠️"
            summary = audit_payload.get("summary")

            st.markdown(f"**Auditor {icon}**")
            if summary:
                st.markdown(summary)

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
                st.markdown("**Suggestions for the agent:**")
                for idea in improvements:
                    st.write(f"- {idea}")

            next_focus = audit_payload.get("next_focus")
            if next_focus:
                st.caption(f"Next focus: {next_focus}")

            confidence = audit_payload.get("confidence")
            if confidence:
                st.caption(f"Assessment confidence: {confidence}")

            if idx == len(st.session_state.ali_chat_history) - 1:
                quick_reply_placeholder = st.empty()
                render_quick_replies(
                    placeholder=quick_reply_placeholder,
                    suggestions=st.session_state.ali_suggestions,
                    pending_state_key="ali_pending_prompt",
                    button_prefix=f"ali_{idx}"
                )

# Chat input (supporta suggerimenti automatici dell'Auditor)
auto_prompt = None
if isinstance(st.session_state.ali_pending_prompt, str):
    auto_prompt = st.session_state.ali_pending_prompt.strip()
    st.session_state.ali_pending_prompt = None

user_prompt = st.chat_input("Write your message...")
prompt = auto_prompt or user_prompt

if prompt:
    # Add user message
    st.session_state.ali_chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get context from RAG + beneficiario corrente
    with st.spinner(get_random_thinking_message()):
        try:
            # Lazy initialization del database (solo al primo uso)
            if not st.session_state.get('doc_processor_initialized', False):
                st.session_state.doc_processor.initialize_db()
                st.session_state.doc_processor_initialized = True

            # Query the knowledge base
            rag_results = st.session_state.doc_processor.query(prompt, n_results=3)

            context_parts = []
            beneficiario_ctx = ""
            if st.session_state.get("active_beneficiario"):
                beneficiario = st.session_state["active_beneficiario"]
                beneficiario_ctx = "BENEFICIARIO CORRENTE (da sessione):\n"
                beneficiario_ctx += f"- Nome: {beneficiario.get('beneficiario_name', beneficiario.get('persona_name', 'N/A'))}\n"
                descr = beneficiario.get("beneficiario_description") or beneficiario.get("persona_description")
                if descr:
                    beneficiario_ctx += f"- Descrizione: {descr}\n"
                notes = beneficiario.get("beneficiario_inference_notes") or beneficiario.get("persona_inference_notes") or []
                if notes:
                    beneficiario_ctx += "- Note: " + "; ".join(notes) + "\n"
                context_parts.append(beneficiario_ctx.strip())

            if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                context_parts.append("\n\n".join(rag_results['documents'][0]))

            context = "\n\n".join([c for c in context_parts if c])

            # Get LLM settings from session
            llm_settings = active_session_data['config'].get('llm_settings', {})
            use_defaults = llm_settings.get('use_defaults', False)

            # Prepara i parametri della chiamata
            chat_params = {
                'provider': provider,
                'model': model,
                'messages': st.session_state.ali_chat_history,
                'system_prompt': ALI_SYSTEM_PROMPT,
                'context': context if context else None
            }

            # Aggiungi parametri custom solo se use_defaults è False
            if not use_defaults:
                chat_params['temperature'] = llm_settings.get('temperature', 1.0)
                chat_params['top_p'] = llm_settings.get('top_p', 0.95 if provider == "Gemini" else 1.0)

                # Max tokens - parametro diverso per provider
                if provider == "Gemini":
                    chat_params['max_output_tokens'] = llm_settings.get('max_output_tokens', 65536)
                else:
                    chat_params['max_tokens'] = llm_settings.get('max_tokens', 4096)

                # Reasoning effort - solo per GPT-5
                if model.startswith('gpt-5'):
                    chat_params['reasoning_effort'] = llm_settings.get('reasoning_effort', 'medium')

            # Get response from LLM
            response = st.session_state.llm_manager.chat(**chat_params)

            # Add assistant response
            st.session_state.ali_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            # Visualizzazione compressa del RAG context e beneficiario
            with st.expander("📚 RAG & Context Details", expanded=False):
                if beneficiario_ctx:
                    st.markdown("**👤 Beneficiary Context:**")
                    st.markdown(beneficiario_ctx)
                    st.divider()

                if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                    st.markdown("**📖 Retrieved RAG Documents:**")
                    for i, (doc, metadata) in enumerate(zip(rag_results['documents'][0], rag_results['metadatas'][0] if 'metadatas' in rag_results else [{}] * len(rag_results['documents'][0])), 1):
                        source = metadata.get('source', 'Unknown') if isinstance(metadata, dict) else 'Unknown'
                        with st.expander(f"Document {i} - {source}", expanded=False):
                            st.markdown(doc)
                else:
                    st.info("No RAG documents used for this response")

            auditor_result = None
            auditor = st.session_state.get("desires_auditor")
            if auditor and provider and model:
                context_summary = {
                    "session_name": active_session_data['metadata'].get('name'),
                    "context_name": active_session_data['config'].get('context'),
                    "desire_count": len(st.session_state.desires),
                    "knowledge_documents": st.session_state.doc_processor.get_stats().get('document_count', 0),
                    "rag_used": bool(context),
                }
                context_description = get_context_description()
                if context_description:
                    context_summary["domain_description"] = context_description
                if st.session_state.get("active_beneficiario"):
                    beneficiario = st.session_state["active_beneficiario"]
                    context_summary["beneficiario_name"] = beneficiario.get("beneficiario_name") or beneficiario.get("persona_name")

                try:
                    auditor_result = auditor.review(
                        provider=provider,
                        model=model,
                        conversation=[msg.copy() for msg in st.session_state.ali_chat_history],
                        module_name="ali",
                        module_goal=ALI_MODULE_GOAL,
                        expected_outcome=ALI_EXPECTED_OUTCOME,
                        context_summary=context_summary,
                        last_user_message=prompt,
                        assistant_message=response,
                    )
                except Exception as audit_exc:  # pylint: disable=broad-except
                    auditor_result = {"error": str(audit_exc)}

            if auditor_result and "error" not in auditor_result:
                message_index = len(st.session_state.ali_chat_history) - 1
                existing_entry = next(
                    (item for item in st.session_state.ali_audit_trail if item.get("message_index") == message_index),
                    None
                )
                audit_record = {
                    "message_index": message_index,
                    "result": auditor_result,
                    "timestamp": datetime.now().isoformat()
                }

                if existing_entry:
                    existing_entry.update(audit_record)
                else:
                    st.session_state.ali_audit_trail.append(audit_record)

                st.session_state.ali_suggestions = (auditor_result.get("suggested_user_replies") or [])[:3]

                with st.chat_message("system"):
                    status = auditor_result.get("status", "pass")
                    icon = "✅" if status == "pass" else "⚠️"
                    summary = auditor_result.get("summary")

                    st.markdown(f"**Auditor {icon}**")
                    if summary:
                        st.markdown(summary)

                    rubric = auditor_result.get("rubric") or {}
                    if isinstance(rubric, dict) and rubric:
                        rubric_labels = [
                            ("coerenza_domanda", "Coerenza con la domanda"),
                            ("allineamento_modulo", "Allineamento al modulo"),
                            ("contesto_conservato", "Contesto conservato"),
                            ("progressione_dialogo", "Progressione dialogo"),
                            ("focus_beneficiario", "Focus sul beneficiario"),
                            ("gestione_json", "Gestione finalizzazione/JSON"),
                        ]
                        st.markdown("**Rubric scores:**")
                        for key, label in rubric_labels:
                            item = rubric.get(key) or {}
                            score = item.get("score")
                            notes = (item.get("notes") or "").strip()
                            score_text = f"{score}/5" if isinstance(score, int) else "N/A"
                            if notes:
                                st.write(f"- {label}: {score_text} — {notes}")
                            else:
                                st.write(f"- {label}: {score_text}")

                    issues = auditor_result.get("issues") or []
                    if issues:
                        st.markdown("**Detected issues:**")
                        for issue in issues:
                            issue_type = issue.get("type", "issue")
                            severity = issue.get("severity", "low")
                            message_text = issue.get("message", "")
                            st.write(f"- ({severity.upper()} · {issue_type}) {message_text}")

                    improvements = auditor_result.get("assistant_improvements") or []
                    if improvements:
                        st.markdown("**Suggestions for the agent:**")
                        for idea in improvements:
                            st.write(f"- {idea}")

                    next_focus = auditor_result.get("next_focus")
                    if next_focus:
                        st.caption(f"Next focus: {next_focus}")

                    confidence = auditor_result.get("confidence")
                    if confidence:
                        st.caption(f"Assessment confidence: {confidence}")

                    quick_reply_placeholder = st.empty()
                    render_quick_replies(
                        placeholder=quick_reply_placeholder,
                        suggestions=st.session_state.ali_suggestions,
                        pending_state_key="ali_pending_prompt",
                        button_prefix=f"ali_{message_index}"
                    )

            elif auditor_result and "error" in auditor_result:
                st.session_state.ali_suggestions = []
                st.warning(f"Auditor not available: {auditor_result['error']}")

            # --- NUOVA LOGICA PER PARSARE IL JSON ---
            json_content_str = None
            if "```" in response:
                json_block = re.search(r"```json\s*(.*?)\s*```", response, re.IGNORECASE | re.DOTALL)
                if not json_block:
                    json_block = re.search(r"```[^{]*({.*?})\s*```", response, re.DOTALL)
                if json_block:
                    json_content_str = json_block.group(1).strip()
            elif response.strip().startswith("{"):
                json_content_str = response.strip()

            if json_content_str:
                try:
                    parsed_json = json.loads(json_content_str)

                    beneficiario_info = parsed_json.get("beneficiario") or parsed_json.get("persona") or {}
                    domain_summary = parsed_json.get("domain_summary")
                    desires_payload = parsed_json.get("desires") if isinstance(parsed_json.get("desires"), list) else []

                    extracted_desires = []
                    bdi_desires = []

                    existing_ids = [d.get("id", 0) for d in st.session_state.desires if isinstance(d.get("id"), int)]
                    next_id = max(existing_ids) + 1 if existing_ids else 1

                    for desire in desires_payload:
                        bdi_desire = {
                            "desire_id": desire.get("desire_id", f"gen_{next_id + len(bdi_desires)}"),
                            "desire_statement": desire.get("desire_statement", "N/A"),
                            "motivation": desire.get("motivation", ""),
                            "success_metrics": desire.get("success_metrics", []),
                            "priority": desire.get("priority", "medium")
                        }
                        bdi_desires.append(bdi_desire)
                        extracted_desires.append({
                            "id": next_id + len(extracted_desires),
                            "description": bdi_desire["desire_statement"],
                            "priority": bdi_desire["priority"],
                            "context": f"Beneficiario: {beneficiario_info.get('beneficiario_name', beneficiario_info.get('persona_name', 'Beneficiario primario'))}",
                            "success_criteria": "\\n".join(bdi_desire["success_metrics"]),
                            "timestamp": datetime.now().isoformat()
                        })

                    if extracted_desires:
                        st.session_state.desires.extend(extracted_desires)

                        if 'active_session' in st.session_state and st.session_state.active_session:
                            existing_bdi = st.session_state.session_manager.get_bdi_data(st.session_state.active_session) or {}
                            existing_structured_desires = existing_bdi.get("desires", []) if isinstance(existing_bdi.get("desires"), list) else []
                            combined_desires = existing_structured_desires + bdi_desires

                            st.session_state.session_manager.update_bdi_data(
                                st.session_state.active_session,
                                desires=combined_desires,
                                beneficiario=beneficiario_info or existing_bdi.get("beneficiario") or existing_bdi.get("persona") or {},
                                domain_summary=domain_summary if domain_summary is not None else existing_bdi.get("domain_summary", "")
                            )
                            st.success(f"✅ Final report detected! {len(extracted_desires)} new desires extracted and added! Total: {len(st.session_state.desires)}")
                        else:
                            st.success(f"✅ Final report detected! {len(extracted_desires)} desires extracted! Total: {len(st.session_state.desires)}")

                        st.info("You can now complete the session or add more desires manually.")
                        st.rerun()
                    else:
                        st.warning("⚠️ The JSON report was detected but doesn't contain desires in the expected format.")

                except json.JSONDecodeError:
                    st.error("❌ The final JSON report generated by the agent is invalid and cannot be parsed.")
                except Exception as e:
                    st.error(f"An unexpected error occurred while parsing the report: {e}")
            # --- FINE NUOVA LOGICA ---

            # Check if a desire was mentioned (simple heuristic)
            elif any(keyword in response.lower() for keyword in ["desire identificato", "registriamo", "aggiungiamo questo desire"]):
                st.info("💡 It looks like we identified a desire! You can confirm it using the sidebar.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

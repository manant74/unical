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
    "Guidare il responsabile di dominio a raccogliere e formalizzare desire concreti, "
    "motivazioni e metriche di successo per una sola categoria di utenti dedotta dalla conversazione."
)
ALI_EXPECTED_OUTCOME = (
    "Progredire verso la conferma o la creazione di un desire ben formulato, "
    "mantenendo il dialogo focalizzato e orientato all'azione."
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

# conversation_auditor viene inizializzato quando serve con LLMManager

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
    """
    Ottiene la descrizione del contesto dal metadata della sessione attiva.
    La descrizione viene ora generata in Knol durante l'estrazione dei belief.
    Se non c'è sessione o contesto, ritorna None.
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
    st.error("⚠️ Nessuna sessione attiva! Alì richiede una sessione attiva per funzionare.")
    st.info("📝 Configura una sessione in Compass prima di usare Alì.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧭 Vai a Compass", use_container_width=True, type="primary"):
            st.switch_page("pages/0_Compass.py")

    st.stop()  # Ferma l'esecuzione se non c'è sessione

# Se arriviamo qui, la sessione esiste - caricala
active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
if not active_session_data:
    st.error("❌ Errore: Sessione attiva non trovata nel database!")
    if st.button("🧭 Vai a Compass", type="primary", width='stretch'):
        st.switch_page("pages/0_Compass.py")
    st.stop()

# Sidebar per configurazione
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
            if st.session_state.get("active_beneficiario"):
                beneficiario = st.session_state["active_beneficiario"]
                beneficiario_name = beneficiario.get("beneficiario_name") or beneficiario.get("persona_name", "N/A")
                beneficiario_desc = (beneficiario.get("beneficiario_description") or beneficiario.get("persona_description", "")).strip()
                st.info(f"Beneficiario corrente: **{beneficiario_name}**" + (f" - {beneficiario_desc}" if beneficiario_desc else ""))
            
            # Mostra informazioni sulla base di conoscenza caricata
            kb_stats = st.session_state.doc_processor.get_stats()
            if kb_stats['document_count'] > 0:
                st.success(f"📚 KB Caricata: {kb_stats['document_count']} documenti")
                st.caption(f"🎯 Contesto: {kb_stats['context']}")
            else:
                st.warning("⚠️ Base di conoscenza vuota per questo contesto")
                st.caption(f"🎯 Contesto: {kb_stats['context']}")
            
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
    st.header("⚙️ Configurazione Alì")

    # Lazy load LLMManager e conversation_auditor quando serve
    if 'llm_manager' not in st.session_state:
        from utils.llm_manager import LLMManager
        st.session_state.llm_manager = LLMManager()

    if 'conversation_auditor' not in st.session_state:
        st.session_state.conversation_auditor = ConversationAuditor(st.session_state.llm_manager)

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
                key="ali_provider",
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
                    key="ali_model",
                    help="Modello configurato dalla sessione attiva"
                )

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    if st.button("🔄 Nuova Conversazione", width='stretch'):
        st.session_state.ali_chat_history = []
        st.session_state.ali_greeted = False
        st.session_state.ali_audit_trail = []
        st.session_state.ali_suggestions = []
        st.session_state.ali_pending_prompt = None
        st.rerun()

    if st.button("Completa Sessione", type="primary", width='stretch'):
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

                st.success(f"Sessione completata! {len(st.session_state.desires)} Desires salvati nella sessione attiva.")
                st.balloons()
            elif len(st.session_state.ali_chat_history) > 1:
                st.session_state.session_manager.update_session_metadata(
                    st.session_state.active_session,
                    
                )

                st.warning("Nessun desire identificato, ma la conversazione e' stata salvata nella sessione.")
                st.info("Suggerimento: chiedi ad Ali di generare il report finale con i desires identificati.")
            else:
                st.warning("Nessuna conversazione da salvare!")
        else:
            # Fallback: salva su file locali se non c'e' sessione attiva
            st.warning("Nessuna sessione attiva! Salvataggio in file locali...")

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

                st.info(f"BDI (desires) salvato in: {filename}")
                st.info("Suggerimento: Attiva una sessione in Compass per integrarla nel sistema!")
            else:
                st.warning("Nessun dato da salvare!")

    st.divider()

    # Quick action: Add desire manually
    with st.expander("➕ Aggiungi Desire Manualmente"):
        st.markdown("Compila i campi per aggiungere un desire manualmente")

        desire_desc = st.text_area("Descrizione", key="manual_desire_desc")
        desire_priority = st.selectbox("Priorità", ["high", "medium", "low"], key="manual_desire_priority")
        desire_context = st.text_area("Contesto", key="manual_desire_context")
        desire_criteria = st.text_area("Criteri di Successo", key="manual_desire_criteria")

        if st.button("Aggiungi Desire", width='stretch'):
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

    # Visualizza desires
    if st.session_state.desires:
        st.subheader("🎯 Desire Identificati")
        for idx, desire in enumerate(st.session_state.desires, 1):
            # Usa 'id' se presente, altrimenti usa l'indice
            desire_id = desire.get('id', idx)
            desire_desc = desire.get('description', desire.get('content', 'N/A'))
            with st.expander(f"#{desire_id}: {desire_desc[:50]}..."):
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
    context_name = kb_stats.get('context', 'default')
    st.warning(f"⚠️ La base di conoscenza per il contesto '{context_name}' è vuota! Vai a Knol per caricare documenti prima di iniziare.")
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.info(f"🎯 Contesto attuale: {active_session_data['config'].get('context', 'N/A')}")
    if st.button("📚 Vai a Knol", width='stretch'):
        st.switch_page("pages/1_Knol.py")
    st.stop()

# Check provider disponibile
if not available_providers or provider is None:
    st.error("❌ Nessun provider LLM configurato. Configura le API keys per continuare.")
    st.stop()

# Saluto iniziale
if not st.session_state.ali_greeted:
    # Carica la descrizione del contesto dal metadata
    context_description = get_context_description()

    # Costruisci il messaggio di saluto
    if context_description:
        greeting = f"Ciao! Sono Alì e sono qui per aiutarti a trovare i tuoi Desire. 🎯\n\nHai creato un contesto che parla di: {context_description}\n\nOra posso aiutarti a identificare obiettivi chiari e raggiungibili nel tuo dominio. Dimmi, cosa vuoi ottenere?"
    else:
        greeting = "Ciao! Sono Alì e sono qui per aiutarti a trovare i tuoi Desire. 🎯\n\nHo accesso alla tua base di conoscenza e posso aiutarti a identificare obiettivi chiari e raggiungibili nel tuo dominio. Dimmi, cosa vuoi ottenere?"

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

user_prompt = st.chat_input("Scrivi il tuo messaggio...")
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
            with st.expander("📚 Dettagli RAG & Contesto", expanded=False):
                if beneficiario_ctx:
                    st.markdown("**👤 Beneficiario Contesto:**")
                    st.markdown(beneficiario_ctx)
                    st.divider()

                if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                    st.markdown("**📖 Documenti RAG Recuperati:**")
                    for i, (doc, metadata) in enumerate(zip(rag_results['documents'][0], rag_results['metadatas'][0] if 'metadatas' in rag_results else [{}] * len(rag_results['documents'][0])), 1):
                        source = metadata.get('source', 'Unknown') if isinstance(metadata, dict) else 'Unknown'
                        with st.expander(f"Documento {i} - {source}", expanded=False):
                            st.markdown(doc)
                else:
                    st.info("Nessun documento RAG utilizzato per questa risposta")

            auditor_result = None
            auditor = st.session_state.get("conversation_auditor")
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

                    issues = auditor_result.get("issues") or []
                    if issues:
                        st.markdown("**Problemi rilevati:**")
                        for issue in issues:
                            issue_type = issue.get("type", "issue")
                            severity = issue.get("severity", "low")
                            message_text = issue.get("message", "")
                            st.write(f"- ({severity.upper()} · {issue_type}) {message_text}")

                    improvements = auditor_result.get("assistant_improvements") or []
                    if improvements:
                        st.markdown("**Suggerimenti per l'agente:**")
                        for idea in improvements:
                            st.write(f"- {idea}")

                    next_focus = auditor_result.get("next_focus")
                    if next_focus:
                        st.caption(f"Prossimo focus: {next_focus}")

                    confidence = auditor_result.get("confidence")
                    if confidence:
                        st.caption(f"Sicurezza valutazione: {confidence}")

                    quick_reply_placeholder = st.empty()
                    render_quick_replies(
                        placeholder=quick_reply_placeholder,
                        suggestions=st.session_state.ali_suggestions,
                        pending_state_key="ali_pending_prompt",
                        button_prefix=f"ali_{message_index}"
                    )

            elif auditor_result and "error" in auditor_result:
                st.session_state.ali_suggestions = []
                st.warning(f"Auditor non disponibile: {auditor_result['error']}")

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
                            st.success(f"?o. Report finale rilevato! {len(extracted_desires)} nuovi desires estratti e aggiunti! Totale: {len(st.session_state.desires)}")
                        else:
                            st.success(f"?o. Report finale rilevato! {len(extracted_desires)} desires estratti! Totale: {len(st.session_state.desires)}")

                        st.info("Puoi ora completare la sessione o aggiungere altri desires manualmente.")
                        st.rerun()
                    else:
                        st.warning("?s???? Il report JSON ?? stato rilevato ma non contiene desires nel formato atteso.")

                except json.JSONDecodeError:
                    st.error("??O Il report finale JSON generato dall'agente non ?? valido e non pu?? essere parsato.")
                except Exception as e:
                    st.error(f"An unexpected error occurred while parsing the report: {e}")
            # --- FINE NUOVA LOGICA ---

            # Check if a desire was mentioned (simple heuristic)
            elif any(keyword in response.lower() for keyword in ["desire identificato", "registriamo", "aggiungiamo questo desire"]):
                st.info("💡 Sembra che abbiamo identificato un desire! Puoi confermarlo usando il pannello laterale.")

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

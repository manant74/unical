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
from utils.context_manager import ContextManager
from utils.auditor import ConversationAuditor

ALI_MODULE_GOAL = (
    "Guidare il responsabile di dominio a raccogliere e formalizzare desire concreti, "
    "motivazioni e metriche di successo per ogni persona rilevante."
)
ALI_EXPECTED_OUTCOME = (
    "Progredire verso la conferma o la creazione di un desire ben formulato, "
    "mantenendo il dialogo focalizzato e orientato all'azione."
)

st.set_page_config(
    page_title="Alì - LUMIA Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza il session state (senza doc_processor che dipende dalla sessione)
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

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

if 'conversation_auditor' not in st.session_state:
    st.session_state.conversation_auditor = ConversationAuditor(st.session_state.llm_manager)

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
        # Carica i desires dalla sessione (supporto domains/personas e fallback legacy)
        bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.active_session)
        if bdi_data and not st.session_state.desires:
            extracted = []
            if isinstance(bdi_data.get('domains'), list):
                for domain in bdi_data['domains']:
                    domain_name = domain.get('domain_name', 'default')
                    for persona in domain.get('personas', []) or []:
                        persona_name = persona.get('persona_name', 'N/A')
                        for desire in persona.get('desires', []) or []:
                            extracted.append({
                                "id": desire.get("desire_id", f"gen_{len(extracted)+1}"),
                                "description": desire.get("desire_statement") or desire.get("descrizione", "N/A"),
                                "priority": desire.get("priorità") or desire.get("priority", "medium"),
                                "context": f"Domain: {domain_name} · Persona: {persona_name}",
                                "success_criteria": "\n".join(desire.get("success_metrics", [])),
                                "timestamp": datetime.now().isoformat()
                            })
            elif isinstance(bdi_data.get('desires'), list):
                for desire in bdi_data['desires']:
                    extracted.append({
                        "id": desire.get("desire_id", f"gen_{len(extracted)+1}"),
                        "description": desire.get("descrizione", "N/A"),
                        "priority": desire.get("priorità", "medium"),
                        "context": "Sessione Attiva",
                        "timestamp": datetime.now().isoformat()
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
                label = suggestion.get("label") or f"Opzione {i + col_idx + 1}"
                message_text = suggestion.get("message", "").strip()
                reason = suggestion.get("why")

                with col:
                    if st.button(label, key=f"{button_prefix}_suggestion_{i + col_idx}", use_container_width=True):
                        if message_text:
                            st.session_state[pending_state_key] = message_text
                    if reason:
                        st.caption(reason)

# CSS per nascondere menu Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}

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
    if st.button("🧭 Vai a Compass", type="primary"):
        st.switch_page("pages/0_Compass.py")
    st.stop()

# Sidebar per configurazione
with st.sidebar:
    # Pulsante Home in alto
    st.markdown("### ✨ LUMIA Studio")
    if st.button("🏠 Torna alla Home", use_container_width=True, type="secondary"):
        st.switch_page("app.py")

    st.divider()

    # Mostra sessione attiva
    if 'active_session' in st.session_state and st.session_state.active_session:
        active_session_data = st.session_state.session_manager.get_session(st.session_state.active_session)
        if active_session_data:
            st.success(f"📍 Sessione Attiva: **{active_session_data['metadata']['name']}**")
            st.caption(f"🗂️ Context: {active_session_data['config'].get('context', 'N/A')}")
            
            # Mostra informazioni sulla base di conoscenza caricata
            kb_stats = st.session_state.doc_processor.get_stats()
            if kb_stats['document_count'] > 0:
                st.success(f"📚 KB Caricata: {kb_stats['document_count']} documenti")
                st.caption(f"🎯 Contesto: {kb_stats['context']}")
            else:
                st.warning("⚠️ Base di conoscenza vuota per questo contesto")
                st.caption(f"🎯 Contesto: {kb_stats['context']}")
            
            if st.button("🧭 Vai a Compass", use_container_width=True):
                st.switch_page("pages/0_Compass.py")
        else:
            st.warning("⚠️ Sessione attiva non trovata")
    else:
        st.info("ℹ️ Nessuna sessione attiva")
        if st.button("🧭 Attiva una sessione", use_container_width=True):
            st.switch_page("pages/0_Compass.py")

    st.divider()

    # Configurazione
    st.header("⚙️ Configurazione Alì")

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

        provider = st.selectbox(
            "Provider LLM",
            available_providers,
            index=available_providers.index(default_provider),
            key="ali_provider",
            help="Provider configurato dalla sessione attiva"
        )

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

    if st.button("🔄 Nuova Conversazione", use_container_width=True):
        st.session_state.ali_chat_history = []
        st.session_state.ali_greeted = False
        st.session_state.ali_audit_trail = []
        st.session_state.ali_suggestions = []
        st.session_state.ali_pending_prompt = None
        st.rerun()

    if st.button("✅ Completa Sessione", type="primary", use_container_width=True):
        # Verifica se c'è una sessione attiva
        if 'active_session' in st.session_state and st.session_state.active_session:
            if st.session_state.desires:
                # Salva i desires nella sessione corrente usando BDI data
                st.session_state.session_manager.update_bdi_data(
                    st.session_state.active_session,
                    desires=st.session_state.desires
                )

                # Salva anche la chat history come metadati della sessione
                st.session_state.session_manager.update_session_metadata(
                    st.session_state.active_session,
                    chat_history=st.session_state.ali_chat_history
                )

                st.success(f"✅ Sessione completata! {len(st.session_state.desires)} Desires salvati nella sessione attiva!")
                st.balloons()
            elif len(st.session_state.ali_chat_history) > 1:
                # Se ci sono messaggi ma nessun desire, salva solo la chat
                st.session_state.session_manager.update_session_metadata(
                    st.session_state.active_session,
                    chat_history=st.session_state.ali_chat_history
                )

                st.warning("⚠️ Nessun desire identificato, ma la conversazione è stata salvata nella sessione.")
                st.info("💡 Suggerimento: Chiedi ad Alì di generare il report finale con i desires identificati.")
            else:
                st.warning("⚠️ Nessuna conversazione da salvare!")
        else:
            # Fallback: salva come prima in file locali se non c'è sessione attiva
            st.warning("⚠️ Nessuna sessione attiva! Salvataggio in file locali...")

            if st.session_state.desires:
                # Salvataggio fallback in formato BDI domains/personas
                fallback_bdi = {
                    "timestamp": datetime.now().isoformat(),
                    "domains": [
                        {
                            "domain_name": active_session_data['config'].get('context', 'default'),
                            "personas": [
                                {
                                    "persona_name": "Utente",
                                    "desires": [
                                        {
                                            "desire_id": d.get("id", f"gen_{i+1}"),
                                            "desire_statement": d.get("description", "N/A"),
                                            "priority": d.get("priority", "medium"),
                                            "success_metrics": (d.get("success_criteria") or "").split("\n") if d.get("success_criteria") else []
                                        }
                                        for i, d in enumerate(st.session_state.desires)
                                    ]
                                }
                            ]
                        }
                    ]
                }

                os.makedirs("./data/sessions", exist_ok=True)
                filename = f"./data/sessions/bdi_desires_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(fallback_bdi, f, ensure_ascii=False, indent=2)

                with open("./data/current_bdi.json", 'w', encoding='utf-8') as f:
                    json.dump(fallback_bdi, f, ensure_ascii=False, indent=2)

                st.info(f"💾 BDI (desires) salvato in: {filename}")
                st.info("💡 Suggerimento: Attiva una sessione in Compass per integrarla nel sistema!")
            else:
                st.warning("⚠️ Nessun dato da salvare!")

    st.divider()

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
    if st.button("📚 Vai a Knol"):
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

    # Get context from RAG
    with st.spinner("Sto pensando..."):
        try:
            # Lazy initialization del database (solo al primo uso)
            if not st.session_state.get('doc_processor_initialized', False):
                st.session_state.doc_processor.initialize_db()
                st.session_state.doc_processor_initialized = True

            # Query the knowledge base
            rag_results = st.session_state.doc_processor.query(prompt, n_results=3)

            context = ""
            if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                context = "\n\n".join(rag_results['documents'][0])

            # Get LLM settings from session
            llm_settings = active_session_data['config'].get('llm_settings', {})

            # Get response from LLM
            response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=st.session_state.ali_chat_history,
                system_prompt=ALI_SYSTEM_PROMPT,
                context=context if context else None,
                temperature=llm_settings.get('temperature', 0.7),
                max_tokens=llm_settings.get('max_tokens', 2000),
                top_p=llm_settings.get('top_p', 0.9),
                stop_sequences=llm_settings.get('stop_sequences')
            )

            # Add assistant response
            st.session_state.ali_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

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

                    # Estrai i desires dal report
                    extracted_desires = []

                    # Calcola il prossimo ID basandoti sul massimo ID esistente
                    existing_ids = [d.get("id", 0) for d in st.session_state.desires if isinstance(d.get("id"), int)]
                    next_id = max(existing_ids) + 1 if existing_ids else 1

                    if "personas" in parsed_json and isinstance(parsed_json["personas"], list):
                        for persona in parsed_json["personas"]:
                            if "desires" in persona and isinstance(persona["desires"], list):
                                for desire in persona["desires"]:
                                    extracted_desires.append({
                                        "id": next_id + len(extracted_desires),
                                        "description": desire.get("desire_statement", "N/A"),
                                        "priority": "medium",  # Default priority
                                        "context": f"Persona: {persona.get('persona_name', 'N/A')}",
                                        "success_criteria": "\n".join(desire.get("success_metrics", [])),
                                        "timestamp": datetime.now().isoformat()
                                    })

                    if extracted_desires:
                        # Aggiungi i nuovi desires a quelli esistenti invece di sovrascriverli
                        st.session_state.desires.extend(extracted_desires)

                        # Salva automaticamente i desires nella sessione attiva se presente
                        if 'active_session' in st.session_state and st.session_state.active_session:
                            st.session_state.session_manager.update_bdi_data(
                                st.session_state.active_session,
                                desires=st.session_state.desires  # Salva la lista completa
                            )
                            st.success(f"✅ Report finale rilevato! {len(extracted_desires)} nuovi desires estratti e aggiunti! Totale: {len(st.session_state.desires)}")
                        else:
                            st.success(f"✅ Report finale rilevato! {len(extracted_desires)} desires estratti! Totale: {len(st.session_state.desires)}")

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

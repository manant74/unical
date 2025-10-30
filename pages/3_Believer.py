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
    page_title="Believer - LUMIA Studio",
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

# CSS per nascondere solo il menu di navigazione Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
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

        provider = st.selectbox(
            "Provider LLM",
            available_providers,
            index=available_providers.index(default_provider),
            key="believer_provider",
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
                key="believer_model",
                help="Modello configurato dalla sessione attiva"
            )

    st.divider()

    # Carica desires
    if st.session_state.loaded_desires is None:
        st.session_state.loaded_desires = load_desires()

    if st.session_state.loaded_desires:
        # Determina la fonte dei desires
        source_info = "dalla Sessione Attiva" if st.session_state.loaded_desires[0].get('context') == 'Sessione Attiva' else "dal file globale"
        st.success(f"✅ {len(st.session_state.loaded_desires)} Desire caricati {source_info}")

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
                belief_desc = belief.get('belief_statement', belief.get('description', 'N/A'))
                st.markdown(f"**{idx}**. {belief_desc[:100]}...")

    st.divider()

    # Controllo sessione
    st.subheader("🎬 Controllo Sessione")

    if st.button("🔄 Nuova Conversazione", use_container_width=True):
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

    if st.button("✅ Completa Sessione", type="primary", use_container_width=True):
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

Puoi scegliere tra due opzioni:

**1. Creare Belief Specializzati** 🎯
   Possiamo lavorare insieme per identificare belief più specifici e dettagliati, focalizzati sui tuoi Desire. Questi saranno complementari ai belief di base e più contestualizzati.

**2. Verificare Belief di Base** 📋
   Se preferisci prima consultare i belief di base già definiti, puoi visualizzarli in Compass nella sezione del contesto attivo.

**Cosa preferisci fare?** Rispondi "1" per creare nuovi belief specializzati, oppure "2" se vuoi prima verificare i belief di base esistenti."""
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
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 Creare Belief Specializzati", key="btn_create_beliefs", use_container_width=True):
            # Simula la scelta dell'opzione 1
            st.session_state.believer_chat_history.append({
                "role": "user",
                "content": "1"
            })
            st.session_state.base_beliefs_checked = True

            response = """Ottimo! Procediamo a creare belief specializzati sui tuoi Desire. 🎯

Questi belief saranno più specifici e dettagliati rispetto ai belief di base, e saranno direttamente collegati ai tuoi obiettivi.

Iniziamo a esplorare la tua base di conoscenza per identificare i belief rilevanti. Dimmi, su quale desire vuoi concentrarti per primo?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    with col2:
        if st.button("📋 Verificare Belief di Base", key="btn_verify_beliefs", use_container_width=True):
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

        elif "1" in prompt.strip() or "creare" in prompt.lower() or "nuovi" in prompt.lower() or "specializzati" in prompt.lower():
            # L'utente vuole creare nuovi belief specializzati
            st.session_state.base_beliefs_checked = True

            response = """Ottimo! Procediamo a creare belief specializzati sui tuoi Desire. 🎯

Questi belief saranno più specifici e dettagliati rispetto ai belief di base, e saranno direttamente collegati ai tuoi obiettivi.

Iniziamo a esplorare la tua base di conoscenza per identificare i belief rilevanti. Dimmi, su quale desire vuoi concentrarti per primo?"""

            st.session_state.believer_chat_history.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

            st.stop()

    # Get context from RAG including desires
    with st.spinner("Sto analizzando..."):
        try:
            # Query the knowledge base
            rag_results = st.session_state.doc_processor.query(prompt, n_results=3)

            # Build context with KB results and desires
            context = ""

            # Add desires to context
            desires_context = "DESIRES DELL'UTENTE:\n"
            for idx, desire in enumerate(st.session_state.loaded_desires, 1):
                desire_id = desire.get('id', idx)
                desire_desc = desire.get('description', desire.get('content', 'N/A'))
                desire_priority = desire.get('priority', 'N/A')
                desires_context += f"- Desire #{desire_id}: {desire_desc} (Priorità: {desire_priority})\n"

            context = desires_context + "\n\n"

            # Add KB results
            if rag_results and rag_results['documents'] and rag_results['documents'][0]:
                kb_context = "INFORMAZIONI DALLA BASE DI CONOSCENZA:\n"
                kb_context += "\n\n".join(rag_results['documents'][0])
                context += kb_context

            # Get LLM settings from session
            llm_settings = active_session_data['config'].get('llm_settings', {})

            # Get response from LLM
            response = st.session_state.llm_manager.chat(
                provider=provider,
                model=model,
                messages=st.session_state.believer_chat_history,
                system_prompt=BELIEVER_SYSTEM_PROMPT,
                context=context if context else None,
                temperature=llm_settings.get('temperature', 0.7),
                max_tokens=llm_settings.get('max_tokens', 2000),
                top_p=llm_settings.get('top_p', 0.9)
            )

            # Add assistant response
            st.session_state.believer_chat_history.append({
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
                    "desire_count": len(st.session_state.loaded_desires or []),
                    "belief_count": len(st.session_state.beliefs),
                    "knowledge_documents": st.session_state.doc_processor.get_stats().get('document_count', 0),
                }
                try:
                    auditor_result = auditor.review(
                        provider=provider,
                        model=model,
                        conversation=[msg.copy() for msg in st.session_state.believer_chat_history],
                        module_name="believer",
                        module_goal=BELIEVER_MODULE_GOAL,
                        expected_outcome=BELIEVER_EXPECTED_OUTCOME,
                        context_summary=context_summary,
                        last_user_message=prompt,
                        assistant_message=response,
                    )
                except Exception as audit_exc:  # pylint: disable=broad-except
                    auditor_result = {"error": str(audit_exc)}

            if auditor_result and "error" not in auditor_result:
                message_index = len(st.session_state.believer_chat_history) - 1
                existing_entry = next(
                    (item for item in st.session_state.believer_audit_trail if item.get("message_index") == message_index),
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
                    st.session_state.believer_audit_trail.append(audit_record)

                st.session_state.believer_suggestions = (auditor_result.get("suggested_user_replies") or [])[:3]

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

            elif auditor_result and "error" in auditor_result:
                st.session_state.believer_suggestions = []
                st.warning(f"Auditor non disponibile: {auditor_result['error']}")

            json_match = re.search(r'```json(.*?)```', response, re.DOTALL) or re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    json_str = json_match.group(1).strip() if '```' in json_match.group(0) else json_match.group(0).strip()
                    parsed_json = json.loads(json_str)

                    extracted_beliefs = []

                    # Calcola il prossimo ID basandoti sul massimo ID esistente
                    existing_ids = [b.get("id", 0) for b in st.session_state.beliefs]
                    next_id = max(existing_ids) + 1 if existing_ids else 1

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
                                "id": next_id + len(extracted_beliefs),
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
                                        "id": next_id + len(extracted_beliefs),
                                        "description": description,
                                        "type": b.get("metadati", {}).get("tipo_soggetto", "fact"),
                                        "confidence": "medium",
                                        "related_desires": [d.get("desire_id") for d in b.get("desires_correlati", [])],
                                        "evidence": b.get("fonte", ""),
                                        "timestamp": datetime.now().isoformat()
                                    })

                    if extracted_beliefs:
                        # Aggiungi i nuovi beliefs a quelli esistenti invece di sovrascriverli
                        st.session_state.beliefs.extend(extracted_beliefs)

                        # Salva automaticamente i beliefs nella sessione attiva se presente
                        if 'active_session' in st.session_state and st.session_state.active_session:
                            st.session_state.session_manager.update_bdi_data(
                                st.session_state.active_session,
                                beliefs=st.session_state.beliefs  # Salva la lista completa
                            )
                            st.success(f"✅ {len(extracted_beliefs)} nuovi beliefs estratti e aggiunti! Totale: {len(st.session_state.beliefs)}")
                        else:
                            st.success(f"✅ {len(extracted_beliefs)} beliefs estratti! Totale: {len(st.session_state.beliefs)}")

                        st.rerun()
                    else:
                        st.warning("⚠️ JSON rilevato, ma nessun belief valido trovato.")

                except json.JSONDecodeError:
                    st.error("❌ Il JSON rilevato non è valido.")
                except Exception as e:
                    st.error(f"❌ Errore durante il parsing del report JSON: {e}")

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")

render_quick_replies(
    placeholder=believer_suggestions_placeholder,
    suggestions=st.session_state.believer_suggestions,
    pending_state_key="believer_pending_prompt",
    button_prefix="believer"
)

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

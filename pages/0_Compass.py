import streamlit as st
import os
import sys
import json
from datetime import datetime
from code_editor import code_editor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.session_manager import SessionManager
from utils.context_manager import ContextManager

st.set_page_config(
    page_title="Compass - LumIA Studio",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per nascondere menu Streamlit
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}

    .compass-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
    }

    /* Font monospace per l'editor JSON */
    textarea {
        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

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

# Inizializza i manager
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

if 'context_manager' not in st.session_state:
    st.session_state.context_manager = ContextManager()

# LLMManager non viene inizializzato qui - viene caricato lazy quando serve (New Session, ecc)

# Cache per get_bdi_data() - evita multiple chiamhe al disco
@st.cache_data
def get_cached_bdi_data(session_id: str):
    """Returns cached BDI data for a session, avoiding repeated disk reads.

    Wraps ``SessionManager.get_bdi_data`` with Streamlit's ``@cache_data``
    so that multiple calls within the same page rerun share one disk read.

    Args:
        session_id: Unique identifier of the target session.

    Returns:
        dict: The full BDI payload (desires, beliefs, intentions, etc.)
            as stored in ``current_bdi.json``, or ``None`` if the session
            has no BDI data yet.
    """
    return st.session_state.session_manager.get_bdi_data(session_id)

# Inizializza editing mode
if 'editing_session_id' not in st.session_state:
    st.session_state.editing_session_id = None

# Inizializza flag per nuova sessione
if 'new_session_requested' not in st.session_state:
    st.session_state.new_session_requested = False

# Header
st.markdown("<h1 class='compass-header'>🧭 Compass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Configure and manage your working sessions</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Header con logo e pulsante home sulla stessa riga
    col_logo, col_home = st.columns([3, 1])

    with col_logo:
        st.markdown("<div style='padding-top: 0px;'><h2>✨ LumIA Studio</h2></div>", unsafe_allow_html=True)

    with col_home:
        if st.button("🏠", width='stretch', type="secondary", help="Back to Home"):
            st.switch_page("app.py")

    st.markdown("---")

    # New Session button in alto
    if st.button("➕ New Session", width='stretch', type="primary"):
        st.session_state.editing_session_id = None
        st.session_state.new_session_requested = True
        st.rerun()

    st.markdown("---")

    st.markdown("### 👩🏻‍💻 Recent Sessions")
    recent_sessions = st.session_state.session_manager.get_all_sessions(status="active")

    if recent_sessions:
        for session in recent_sessions[:5]:
            metadata = session['metadata']
            config = session['config']

            with st.container():
                # Layout compatto: info a sinistra, pulsanti a destra
                col_info, col_actions = st.columns([3, 1])

                with col_info:
                    st.markdown(f"**{metadata['name']}**")
                    st.caption(f"KB: {config['context']}")
                    st.caption(f"LLM: {config['llm_provider']}")

                with col_actions:
                    if st.button("📂", key=f"load_{session['session_id']}", help="Load session", width='stretch'):
                        st.session_state.editing_session_id = session['session_id']
                        st.session_state.active_session = session['session_id']
                        st.session_state.new_session_requested = False
                        st.success(f"Session '{metadata['name']}' loaded!")
                        st.rerun()

                    if st.button("🗑️", key=f"del_{session['session_id']}", help="Delete session", width='stretch'):
                        st.session_state.session_manager.delete_session(session['session_id'])
                        if st.session_state.editing_session_id == session['session_id']:
                            st.session_state.editing_session_id = None
                        st.rerun()

                st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    else:
        st.info("No sessions yet. Create your first one!")

    # Export as Framework button (visible only when a session is loaded)
    if st.session_state.editing_session_id:
        st.markdown("---")
        st.markdown("### ⚡ Genius")

        # Initialize export state
        if 'pending_framework_export' not in st.session_state:
            st.session_state.pending_framework_export = None

        # Show overwrite confirmation if needed
        if st.session_state.pending_framework_export:
            framework_info = st.session_state.pending_framework_export
            st.warning(f"⚠️ Framework '{framework_info['filename']}' already exists.")

            col_cancel, col_overwrite = st.columns(2)
            with col_cancel:
                if st.button("❌ Cancel", key="cancel_overwrite_framework", width='stretch'):
                    st.session_state.pending_framework_export = None
                    st.rerun()

            with col_overwrite:
                if st.button("✅ Overwrite", key="confirm_overwrite_framework", width='stretch', type="primary"):
                    try:
                        # Save BDI to framework
                        with open(framework_info['path'], 'w', encoding='utf-8') as f:
                            json.dump(framework_info['bdi_data'], f, indent=2, ensure_ascii=False)
                        st.success(f"✅ Exported:\n`{framework_info['filename']}`")
                        st.info("💡 Use it in Genius!")
                        st.session_state.pending_framework_export = None
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                        st.session_state.pending_framework_export = None
        else:
            # Show export button
            if st.button("📤 Export as Framework", width='stretch', type="secondary", key="export_framework_sidebar", help="Export BDI as reusable framework for Genius"):
                try:
                    # Get complete BDI data
                    bdi_data = get_cached_bdi_data(st.session_state.editing_session_id)

                    if not bdi_data:
                        st.error("❌ No BDI data to export")
                    elif not bdi_data.get('desires') or not bdi_data.get('beliefs'):
                        st.warning("⚠️ BDI must have both Desires and Beliefs to export")
                    else:
                        # Get session for naming
                        current_session_export = st.session_state.session_manager.get_session(st.session_state.editing_session_id)
                        session_name = current_session_export['metadata']['name']

                        # Normalize filename: lowercase, replace spaces with underscores, remove special chars
                        framework_name = session_name.lower().replace(' ', '_')
                        framework_name = ''.join(c for c in framework_name if c.isalnum() or c == '_')
                        framework_filename = f"{framework_name}_bdi.json"

                        # Path to frameworks directory
                        frameworks_dir = os.path.join("data", "bdi_frameworks")
                        os.makedirs(frameworks_dir, exist_ok=True)

                        framework_path = os.path.join(frameworks_dir, framework_filename)

                        # Check if file exists
                        if os.path.exists(framework_path):
                            # Store export info for confirmation
                            st.session_state.pending_framework_export = {
                                'filename': framework_filename,
                                'path': framework_path,
                                'bdi_data': bdi_data
                            }
                            st.rerun()
                        else:
                            # Save BDI to framework
                            with open(framework_path, 'w', encoding='utf-8') as f:
                                json.dump(bdi_data, f, indent=2, ensure_ascii=False)
                            st.success(f"✅ Exported:\n`{framework_filename}`")
                            st.info("💡 Use it in Genius!")

                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")

# Main content - Tabs
# Carica i dati della sessione corrente se in editing
current_session = None
if st.session_state.editing_session_id:
    current_session = st.session_state.session_manager.get_session(st.session_state.editing_session_id)

# Se non c'è nessuna sessione selezionata, mostra il form di creazione
if not current_session:
    # Verifica se c'è stata una richiesta esplicita di "New Session"
    if st.session_state.editing_session_id is None and 'new_session_requested' in st.session_state and st.session_state.new_session_requested:
        # Form per creare una nuova sessione
        st.markdown("## ➕ Create New Session")

        contexts = st.session_state.context_manager.get_all_contexts()

        # Lazy load LLMManager solo quando serve
        if 'llm_manager' not in st.session_state:
            from utils.llm_manager import LLMManager
            st.session_state.llm_manager = LLMManager()

        providers = st.session_state.llm_manager.get_available_providers()

        if not contexts:
            st.error("⚠️ No contexts available. Please create a context in Knol first.")
            if st.button("Go to Knol"):
                st.switch_page("pages/1_Knol.py")
            st.stop()

        if not providers:
            st.error("⚠️ No LLM providers configured. Please add API keys in your .env file.")
            st.stop()

        with st.form("new_session_form"):
            session_name = st.text_input(
                "Session Name *",
                placeholder="e.g., My Research Project"
            )

            session_description = st.text_area(
                "Description",
                placeholder="Brief description of what you want to achieve...",
                height=100
            )

            col1, col2 = st.columns(2)

            with col1:
                selected_context = st.selectbox(
                    "Context *",
                    options=[ctx['normalized_name'] for ctx in contexts],
                    format_func=lambda x: next(ctx['name'] for ctx in contexts if ctx['normalized_name'] == x)
                )

            with col2:
                selected_provider = st.selectbox("LLM Provider *", providers)

            models = st.session_state.llm_manager.get_models_for_provider(selected_provider)
            model_keys = list(models.keys())
            model_display = list(models.values())

            selected_model_idx = st.selectbox(
                "Model *",
                range(len(model_keys)),
                format_func=lambda i: model_display[i]
            )
            selected_model = model_keys[selected_model_idx]

            submitted = st.form_submit_button("Create Session", type="primary", width='stretch')

            if submitted:
                if not session_name:
                    st.error("Please provide a session name")
                else:
                    session_id = st.session_state.session_manager.create_session(
                        name=session_name,
                        context=selected_context,
                        llm_provider=selected_provider,
                        llm_model=selected_model,
                        description=session_description
                    )

                    st.session_state.editing_session_id = session_id
                    st.session_state.new_session_requested = False
                    st.success(f"✅ Session '{session_name}' created successfully!")
                    st.rerun()
    else:
        # Empty state - Mostra solo istruzioni
        st.markdown("")
        # Centra il contenuto usando colonne
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.info("""
            ### 🚀 Getting Started

            **To start configuring a session:**

            1. Click **"➕ New Session"** in the sidebar to create a new session
            2. Or click **"📂"** on an existing session to load and edit it
            3. Configure your session and activate it with **"🚀 Activate"**
            """)

            st.markdown("")
            st.caption("💡 A session includes: Name, Description, Context, LLM Configuration, and Belief Base")
else:
    # Sessione selezionata - Mostra le tab di editing
    st.info(f"📝 Session Name Selected: **{current_session['metadata']['name']}**")

    # Tabs principali
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📋 Session Settings", "🗂️ Context & Beliefs", "💭 Desires", "🧠 Beliefs", "🎯 Intentions", "📊 Analytics", "🕸️ Grafo BDI"])

    # ============================================================================
    # TAB 1: Session Info (nome, descrizione, LLM)
    # ============================================================================
    with tab1:
        # Lazy load LLMManager per le operazioni di salvataggio e configurazione
        if 'llm_manager' not in st.session_state:
            from utils.llm_manager import LLMManager
            st.session_state.llm_manager = LLMManager()

        # Carica dati esistenti se in editing
        session_name = current_session['metadata']['name'] if current_session else ""
        session_description = current_session['metadata']['description'] if current_session else ""

        col1, col2 = st.columns([2, 1])

        with col1:
            # Nome sessione
            new_session_name = st.text_input(
                "Session Name *",
                value=session_name,
                placeholder="e.g., My Research Project",
                help="Give your session a memorable name"
            )

            # Descrizione
            new_session_description = st.text_area(
                "Description",
                value=session_description,
                placeholder="Brief description of what you want to achieve...",
                height=100
            )

        with col2:
            # Per salvare, serve almeno un contesto
            can_save = new_session_name and (current_session or st.session_state.context_manager.get_all_contexts())

            if current_session:
                if st.button("🚀 Activate", width='stretch', type="primary"):
                    st.session_state.active_session = st.session_state.editing_session_id
                    st.success(f"🎉 Session '{new_session_name}' is now active!")
                    st.balloons()

            if st.button("💾 Save", width='stretch', type="secondary", disabled=not can_save):
                if current_session:
                    # Update existing session (solo metadata)
                    st.session_state.session_manager.update_session_metadata(
                        st.session_state.editing_session_id,
                        name=new_session_name,
                        description=new_session_description
                    )
                    st.success("✅ Session info saved!")
                else:
                    # Per creare nuova sessione serve un contesto
                    contexts = st.session_state.context_manager.get_all_contexts()
                    if contexts:
                        # Usa il primo contesto disponibile come default
                        default_context = contexts[0]['normalized_name']
                        # Usa provider di default se disponibile
                        available_providers = st.session_state.llm_manager.get_available_providers()
                        if available_providers:
                            default_provider = available_providers[0]
                            default_model = list(st.session_state.llm_manager.get_models_for_provider(default_provider).keys())[0]

                            session_id = st.session_state.session_manager.create_session(
                                name=new_session_name,
                                context=default_context,
                                llm_provider=default_provider,
                                llm_model=default_model,
                                description=new_session_description
                            )
                            st.session_state.editing_session_id = session_id
                            st.success("✅ New session created!")
                            st.rerun()
                        else:
                            st.error("No LLM providers configured!")
                    else:
                        st.error("Please configure a context first!")

        st.markdown("---")
        st.markdown("#### 🤖 LLM Configuration")

        available_providers = st.session_state.llm_manager.get_available_providers()

        if not available_providers:
            st.error("⚠️ No LLM providers configured. Please add API keys in your .env file.")
        else:
            col1, col2 = st.columns(2)

            # Funzione helper per ottenere defaults dinamici dal modello
            def get_default_settings_for_model(model):
                """Builds the default LLM-settings dict for a specific model.

                Reads per-model parameter definitions from ``LLMManager`` and
                extracts each parameter's ``default`` value so the UI can
                pre-populate sliders / selectors without user input.

                Args:
                    model: The model identifier string (e.g. ``"gemini-2.5-flash"``).

                Returns:
                    dict: Mapping of parameter names to their default values,
                    plus ``use_defaults: True`` as a sentinel flag.
                """
                params = st.session_state.llm_manager.get_model_parameters(model)
                defaults = {'use_defaults': True}
                for param_name, config_item in params.items():
                    defaults[param_name] = config_item.get('default')
                return defaults

            # Carica configurazione LLM esistente
            if current_session:
                config = current_session['config']
                current_provider = config.get('llm_provider', available_providers[0])
                current_model = config.get('llm_model')
                llm_settings = config.get('llm_settings', {})
            else:
                current_provider = available_providers[0]
                current_model = None
                llm_settings = {}

            # Se non ci sono settings salvati, usa defaults per il modello corrente
            if not llm_settings and current_model:
                llm_settings = get_default_settings_for_model(current_model)

            with col1:
                # Provider selection
                provider_idx = 0
                if current_provider in available_providers:
                    provider_idx = available_providers.index(current_provider)

                selected_provider = st.selectbox(
                    "LLM Provider",
                    available_providers,
                    index=provider_idx,
                    key="llm_provider"
                )

                # Model selection
                available_models = st.session_state.llm_manager.get_models_for_provider(selected_provider)
                model_keys = list(available_models.keys())
                model_display = list(available_models.values())

                model_idx = 0
                if current_model in model_keys:
                    model_idx = model_keys.index(current_model)

                selected_model_idx = st.selectbox(
                    "Model",
                    range(len(model_keys)),
                    format_func=lambda i: model_display[i],
                    index=model_idx,
                    key="llm_model"
                )

                selected_model = model_keys[selected_model_idx]

            with col2:
                # Checkbox per usare i parametri di default
                use_defaults = st.checkbox(
                    "Use Default Parameters",
                    value=llm_settings.get('use_defaults', True),
                    help="Se attivo, usa parametri ottimali per il modello"
                )

                # Ottieni parametri dinamici per il modello selezionato
                model_params = st.session_state.llm_manager.get_model_parameters(selected_model)

                # Inizializza new_llm_settings
                new_llm_settings = {'use_defaults': use_defaults}

                if not model_params:
                    st.warning(f"⚠️ Parametri per '{selected_model}' non configurati.")
                else:
                    # Renderizza dinamicamente ogni parametro per questo modello
                    for param_name, param_config in model_params.items():
                        param_type = param_config.get("type")
                        label = param_config.get("label", param_name)
                        help_text = param_config.get("help", "")
                        default_value = param_config.get("default")

                        # Recupera valore corrente o default
                        current_value = llm_settings.get(param_name, default_value)

                        if param_type == "slider":
                            new_llm_settings[param_name] = st.slider(
                                label,
                                min_value=param_config["min"],
                                max_value=param_config["max"],
                                value=current_value,
                                step=param_config["step"],
                                disabled=use_defaults,
                                help=help_text
                            )

                        elif param_type == "number":
                            new_llm_settings[param_name] = st.number_input(
                                label,
                                min_value=param_config["min"],
                                max_value=param_config["max"],
                                value=current_value,
                                step=param_config["step"],
                                disabled=use_defaults,
                                help=help_text
                            )

                        elif param_type == "selectbox":
                            options = param_config["options"]
                            try:
                                index = options.index(current_value)
                            except (ValueError, TypeError):
                                index = options.index(default_value) if default_value in options else 0

                            new_llm_settings[param_name] = st.selectbox(
                                label,
                                options=options,
                                index=index,
                                disabled=use_defaults,
                                help=help_text
                            )

            # Test connection e Save
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔌 Test Connection", width='stretch'):
                    with st.spinner("Testing LLM connection..."):
                        try:
                            test_response = st.session_state.llm_manager.chat(
                                provider=selected_provider,
                                model=selected_model,
                                messages=[{"role": "user", "content": "Hello! Please respond with 'OK' if you can read this."}],
                                system_prompt="You are a helpful assistant."
                            )
                            st.success(f"✅ Connection successful! Response: {test_response[:100]}...")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")

            with col2:
                if current_session:
                    if st.button("💾 Save LLM Config", width='stretch', type="primary"):
                        st.session_state.session_manager.update_session_config(
                            st.session_state.editing_session_id,
                            llm_provider=selected_provider,
                            llm_model=selected_model,
                            llm_settings=new_llm_settings
                        )
                        st.success("✅ LLM configuration saved!")
                else:
                    st.info("Save session info first to configure LLM")

    # ============================================================================
    # TAB 2: Context
    # ============================================================================
    with tab2:
        st.markdown("### 🗂️ Context Selection")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before selecting a context.")
        else:
            contexts = st.session_state.context_manager.get_all_contexts()
            session_context = current_session['config']['context']

            # Prepara le opzioni con "Nessuno" come prima scelta
            context_options = ["none"] + [ctx['normalized_name'] for ctx in contexts]
            context_display_names = ["🚫 Nessuno"] + [f"{ctx.get('name', ctx['normalized_name'])} ({ctx['normalized_name']})" for ctx in contexts]

            # Trova indice default
            default_idx = 0
            if session_context:
                if session_context in context_options:
                    default_idx = context_options.index(session_context)

            col1, col2 = st.columns([4, 1])

            with col1:
                selected_idx = st.selectbox(
                    "Select Context",
                    range(len(context_options)),
                    format_func=lambda i: context_display_names[i],
                    index=default_idx,
                    key="context_select"
                )

                new_session_context = context_options[selected_idx]

            with col2:
                st.markdown("")
                st.markdown("")
                # Mostra info icon solo se un contesto è selezionato (non "Nessuno")
                if selected_idx > 0:
                    if st.button("ℹ️ Info", width='stretch'):
                        context_info = contexts[selected_idx - 1]  # -1 perché "Nessuno" è al primo posto

                        # Mostra popup con informazioni
                        st.info(f"""
                        **📊 Context Information**

                        **Name:** {context_info.get('name', 'N/A')}
                        **Documents:** {context_info.get('document_count', 0)}
                        **Base Beliefs:** {context_info.get('belief_count', 0)}
                        **Created:** {context_info.get('created_at', 'N/A')[:10] if context_info.get('created_at') else 'N/A'}
                        **Last Updated:** {context_info.get('updated_at', 'N/A')[:10] if context_info.get('updated_at') else 'N/A'}
                        """)

            # Link to Knol if no contexts available
            if not contexts:
                st.warning("⚠️ No contexts available. Create a context in Knol module.")
                if st.button("Go to Knol"):
                    st.switch_page("pages/1_Knol.py")

            # ============================================================================
            # Belief Base Management - Appare solo se un contesto è selezionato
            # ============================================================================
            if selected_idx > 0:  # Solo se non è "Nessuno"
                st.markdown("---")
                st.markdown("### 💡 Belief Base Management")

                # Toggle per espandere l'editor
                if 'editor_expanded' not in st.session_state:
                    st.session_state.editor_expanded = False

                # Layout: Editor JSON a sinistra, pulsanti a destra (o full width se espanso)
                if st.session_state.editor_expanded:
                    # Modalità espansa: editor a schermo intero
                    col1 = st.container()
                    col2 = None
                else:
                    # Modalità normale: 2 colonne
                    col1, col2 = st.columns([3, 1])

                with col1:
                    # Carica belief base
                    belief_base = st.session_state.session_manager.get_belief_base(st.session_state.editing_session_id)
                    beliefs = belief_base.get('beliefs', []) if belief_base else []

                    # JSON editor con syntax highlighting
                    beliefs_json = json.dumps({"beliefs": beliefs}, indent=2, ensure_ascii=False)

                    # Header con pulsante expand inline
                    col_label, col_spacer, col_btn = st.columns([3, 0.6, 0.4])
                    with col_label:
                        st.markdown("**Edit beliefs as JSON**")
                    with col_btn:
                        expand_icon = "🔼" if st.session_state.editor_expanded else "🔽"
                        if st.button(expand_icon, key="toggle_editor", help="Expand/Collapse editor", width='stretch'):
                            st.session_state.editor_expanded = not st.session_state.editor_expanded
                            st.rerun()

                    # Configurazione del code editor (altezza dinamica in base allo stato)
                    editor_height = [40, 60] if st.session_state.editor_expanded else [20, 25]

                    response = code_editor(
                        code=beliefs_json,
                        lang="json",
                        height=editor_height,
                        theme="default",
                        shortcuts="vscode",
                        allow_reset=True,
                        key=f"beliefs_editor_{st.session_state.editing_session_id}",
                        options={
                            "wrap": True,
                            "showLineNumbers": True,
                            "highlightActiveLine": True,
                            "fontSize": 14,
                        }
                    )

                    # Il valore editato è in response['text']
                    # Se il code editor non ha ancora un valore, usa il JSON originale
                    if response and 'text' in response and response['text'].strip():
                        edited_json = response['text']
                    else:
                        edited_json = beliefs_json

                # Pulsanti laterali (solo se NON espanso)
                if not st.session_state.editor_expanded and col2:
                    with col2:
                        st.markdown("###")

                        # Save All (Context + Beliefs)
                        if st.button("💾 Save All", width='stretch', type="primary", key="save_all"):
                            try:
                                # Salva il contesto
                                context_to_save = new_session_context if new_session_context != "none" else None
                                st.session_state.session_manager.update_session_config(
                                    st.session_state.editing_session_id,
                                    context=context_to_save
                                )

                                # Salva i belief
                                parsed = json.loads(edited_json)
                                if 'beliefs' in parsed and isinstance(parsed['beliefs'], list):
                                    st.session_state.session_manager.update_belief_base(
                                        st.session_state.editing_session_id,
                                        parsed['beliefs']
                                    )
                                    st.success("✅ Context and beliefs saved!")
                                    st.rerun()
                                else:
                                    st.error("❌ JSON must contain a 'beliefs' array")
                            except json.JSONDecodeError as e:
                                st.error(f"❌ Invalid JSON: {str(e)}")

                        # Import from context
                        if st.button("📥 Import from Context", width='stretch', key="import_beliefs"):
                            with st.spinner("Loading beliefs from context..."):
                                try:
                                # Usa il contesto selezionato nel selectbox (non quello salvato)
                                    context_name = new_session_context

                                    if context_name == "none":
                                        st.warning("⚠️ No context selected. Please select a context first.")
                                    else:
                                    # Ottieni il path del file belief_base del contesto
                                        belief_base_path = st.session_state.context_manager.get_belief_base_path(context_name)

                                    # Verifica se il file esiste
                                        if not os.path.exists(belief_base_path):
                                            st.warning(f"⚠️ No belief base found in this context. File path: {belief_base_path}")
                                        else:
                                        # Carica i belief dal file del contesto
                                            with open(belief_base_path, 'r', encoding='utf-8') as f:
                                                context_beliefs_data = json.load(f)

                                        # Prova sia 'beliefs' che 'beliefs_base' per compatibilità
                                            context_beliefs = context_beliefs_data.get('beliefs',
                                                             context_beliefs_data.get('beliefs_base', []))

                                            if not context_beliefs:
                                                st.info("ℹ️ The belief base in this context is empty.")
                                            else:
                                            # Aggiungi timestamp e metadata ai belief importati
                                                for belief in context_beliefs:
                                                    if 'imported_at' not in belief:
                                                        belief['imported_at'] = datetime.now().isoformat()
                                                    if 'imported_from' not in belief:
                                                        belief['imported_from'] = context_name

                                            # Aggiungi ai belief esistenti (evita duplicati basati su content)
                                                existing_contents = {b.get('content') for b in beliefs}
                                                new_beliefs = [b for b in context_beliefs if b.get('content') not in existing_contents]

                                                if new_beliefs:
                                                    beliefs.extend(new_beliefs)

                                                # Salva
                                                    st.session_state.session_manager.update_belief_base(
                                                        st.session_state.editing_session_id,
                                                        beliefs
                                                    )

                                                    st.success(f"✅ Imported {len(new_beliefs)} beliefs from context '{context_name}'!")
                                                    st.rerun()
                                                else:
                                                    st.info("ℹ️ All beliefs from the context are already in the session.")

                                except json.JSONDecodeError as e:
                                    st.error(f"❌ Error parsing belief base file: {str(e)}")
                                except Exception as e:
                                    st.error(f"❌ Error importing beliefs: {str(e)}")

                        # Clear all beliefs
                        if 'confirm_clear' not in st.session_state:
                            st.session_state.confirm_clear = False

                        if not st.session_state.confirm_clear:
                            if st.button("🗑️ Clear All", width='stretch', key="clear_beliefs"):
                                st.session_state.confirm_clear = True
                                st.rerun()
                        else:
                            st.warning("⚠️ Sure?")
                            if st.button("✅ Yes", width='stretch', key="btn_confirm_clear"):
                                st.session_state.session_manager.update_belief_base(
                                    st.session_state.editing_session_id,
                                    []
                                )
                                st.session_state.confirm_clear = False
                                st.success("✅ Cleared!")
                                st.rerun()
                            if st.button("❌ No", width='stretch', key="btn_cancel_clear"):
                                st.session_state.confirm_clear = False
                                st.rerun()

                        # Validate JSON
                        if st.button("✅ Validate JSON", width='stretch', key="validate_json"):
                            try:
                                parsed = json.loads(edited_json)
                                if 'beliefs' in parsed and isinstance(parsed['beliefs'], list):
                                    st.success(f"✅ Valid JSON! Found {len(parsed['beliefs'])} beliefs.")
                                else:
                                    st.error("❌ JSON must contain a 'beliefs' array")
                            except json.JSONDecodeError as e:
                                st.error(f"❌ Invalid JSON: {str(e)}")

                        # Stats
                        st.metric("Total Beliefs", len(beliefs))

    
    
    # ============================================================================
    # TAB 3: Desires Management
    # ============================================================================
    with tab3:
        st.markdown("### Desires Management")

        if not current_session:
            st.warning("Please save session info in the first tab before managing desires.")
        else:
            # Toggle per espandere l'editor desires
            if 'desires_editor_expanded' not in st.session_state:
                st.session_state.desires_editor_expanded = False

            # Layout: Editor JSON a sinistra, pulsanti a destra (o full width se espanso)
            if st.session_state.desires_editor_expanded:
                col1 = st.container()
                col2 = None
            else:
                col1, col2 = st.columns([3, 1])

            with col1:
                # Carica beneficiario e desires dal BDI single-beneficiario (compatibile con legacy 'persona')
                bdi_data = get_cached_bdi_data(st.session_state.editing_session_id) or {}
                beneficiario_data = bdi_data.get("beneficiario") or bdi_data.get("persona") or {}
                domain_summary = bdi_data.get("domain_summary", "")
                desires = bdi_data.get("desires", []) or []

                editor_payload = {
                    "domain_summary": domain_summary,
                    "beneficiario": beneficiario_data or {
                        "beneficiario_name": "",
                        "beneficiario_description": "",
                        "beneficiario_inference_notes": []
                    },
                    "desires": desires
                }
                desires_json = json.dumps(editor_payload, indent=2, ensure_ascii=False)

                col_label, col_spacer, col_btn = st.columns([3, 0.6, 0.4])
                with col_label:
                    st.markdown("**Edit beneficiario & desires**")
                with col_btn:
                    expand_icon = "[-]" if st.session_state.desires_editor_expanded else "[+]"
                    if st.button(expand_icon, key="toggle_desires_editor", help="Expand/Collapse editor", width='stretch'):
                        st.session_state.desires_editor_expanded = not st.session_state.desires_editor_expanded
                        st.rerun()

                # Configurazione del code editor (altezza dinamica in base allo stato)
                editor_height = [40, 60] if st.session_state.desires_editor_expanded else [20, 25]

                response = code_editor(
                    code=desires_json,
                    lang="json",
                    height=editor_height,
                    theme="default",
                    shortcuts="vscode",
                    allow_reset=True,
                    key=f"desires_editor_{st.session_state.editing_session_id}",
                    options={
                        "wrap": True,
                        "showLineNumbers": True,
                        "highlightActiveLine": True,
                        "fontSize": 14,
                    }
                )

                if response and 'text' in response and response['text'].strip():
                    edited_desires_json = response['text']
                else:
                    edited_desires_json = desires_json

            if not st.session_state.desires_editor_expanded and col2:
                with col2:
                    st.markdown("###")

                    if st.button("Save Desires", width='stretch', type="primary", key="save_desires"):
                        try:
                            parsed = json.loads(edited_desires_json)
                            beneficiario_payload = parsed.get("beneficiario") or parsed.get("persona")
                            if not isinstance(beneficiario_payload, dict):
                                st.error("JSON must contain a 'beneficiario' object (legacy: 'persona')")
                            elif not isinstance(parsed.get("desires"), list):
                                st.error("JSON must contain a 'desires' array")
                            else:
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    beneficiario=beneficiario_payload or {},
                                    desires=parsed.get("desires") or [],
                                    domain_summary=parsed.get("domain_summary", "")
                                )
                                st.success("Beneficiario e desires salvati!")
                            st.rerun()
                        except AttributeError:
                            st.error("SessionManager non aggiornato. Riavvia l'applicazione.")
                        except json.JSONDecodeError as e:
                            st.error(f"Invalid JSON: {str(e)}")

                    if 'confirm_clear_desires' not in st.session_state:
                        st.session_state.confirm_clear_desires = False

                    if not st.session_state.confirm_clear_desires:
                        if st.button("Clear All", width='stretch', key="clear_desires"):
                            st.session_state.confirm_clear_desires = True
                            st.rerun()
                    else:
                        st.warning("Sure?")
                        if st.button("Yes", width='stretch', key="btn_confirm_clear_desires"):
                            try:
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    beneficiario={},
                                    desires=[],
                                    domain_summary=""
                                )
                                st.session_state.confirm_clear_desires = False
                                st.success("Beneficiario e desires azzerati!")
                                st.rerun()
                            except AttributeError:
                                st.error("SessionManager non aggiornato. Riavvia l'applicazione.")
                        if st.button("No", width='stretch', key="btn_cancel_clear_desires"):
                            st.session_state.confirm_clear_desires = False
                            st.rerun()

                    if st.button("Validate JSON", width='stretch', key="validate_desires_json"):
                        try:
                            parsed = json.loads(edited_desires_json)
                            beneficiario_payload = parsed.get("beneficiario") or parsed.get("persona")
                            if not isinstance(beneficiario_payload, dict):
                                st.error("JSON must contain a 'beneficiario' object (legacy: 'persona')")
                            elif not isinstance(parsed.get("desires"), list):
                                st.error("JSON must contain a 'desires' array")
                            else:
                                total_desires = len(parsed.get("desires") or [])
                                st.success(f"JSON valido! Trovati {total_desires} desires sul beneficiario primario.")
                        except json.JSONDecodeError as e:
                            st.error(f"Invalid JSON: {str(e)}")

                    st.metric("Total Desires", len(desires))

    # ============================================================================
    # TAB 4: BDI Beliefs Management
    # ============================================================================
    with tab4:
        st.markdown("### 🧠 BDI Beliefs Management")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before managing BDI beliefs.")
        else:
            # Toggle per espandere l'editor BDI beliefs
            if 'bdi_beliefs_editor_expanded' not in st.session_state:
                st.session_state.bdi_beliefs_editor_expanded = False

            # Layout: Editor JSON a sinistra, pulsanti a destra (o full width se espanso)
            if st.session_state.bdi_beliefs_editor_expanded:
                # Modalità espansa: editor a schermo intero
                col1 = st.container()
                col2 = None
            else:
                # Modalità normale: 2 colonne
                col1, col2 = st.columns([3, 1])

            with col1:
                # Carica beliefs dal BDI
                try:
                    bdi_data = get_cached_bdi_data(st.session_state.editing_session_id)
                    bdi_beliefs = bdi_data.get('beliefs', []) if bdi_data else []
                except AttributeError:
                    # Fallback se il metodo non è ancora disponibile
                    st.warning("⚠️ SessionManager non aggiornato. Riavvia l'applicazione per caricare le nuove funzionalità.")
                    bdi_beliefs = []

                # JSON editor con syntax highlighting
                bdi_beliefs_json = json.dumps({"beliefs": bdi_beliefs}, indent=2, ensure_ascii=False)

                # Header con pulsante expand inline
                col_label, col_spacer, col_btn = st.columns([3, 0.6, 0.4])
                with col_label:
                    st.markdown("**Edit BDI beliefs as JSON**")
                with col_btn:
                    expand_icon = "🔼" if st.session_state.bdi_beliefs_editor_expanded else "🔽"
                    if st.button(expand_icon, key="toggle_bdi_beliefs_editor", help="Expand/Collapse editor", width='stretch'):
                        st.session_state.bdi_beliefs_editor_expanded = not st.session_state.bdi_beliefs_editor_expanded
                        st.rerun()

                # Configurazione del code editor (altezza dinamica in base allo stato)
                editor_height = [40, 60] if st.session_state.bdi_beliefs_editor_expanded else [20, 25]

                response = code_editor(
                    code=bdi_beliefs_json,
                    lang="json",
                    height=editor_height,
                    theme="default",
                    shortcuts="vscode",
                    allow_reset=True,
                    key=f"bdi_beliefs_editor_{st.session_state.editing_session_id}",
                    options={
                        "wrap": True,
                        "showLineNumbers": True,
                        "highlightActiveLine": True,
                        "fontSize": 14,
                    }
                )

                # Il valore editato è in response['text']
                # Se il code editor non ha ancora un valore, usa il JSON originale
                if response and 'text' in response and response['text'].strip():
                    edited_bdi_beliefs_json = response['text']
                else:
                    edited_bdi_beliefs_json = bdi_beliefs_json

            # Pulsanti laterali (solo se NON espanso)
            if not st.session_state.bdi_beliefs_editor_expanded and col2:
                with col2:
                    st.markdown("###")

                    # Save BDI Beliefs
                    if st.button("💾 Save Beliefs", width='stretch', type="primary", key="save_bdi_beliefs"):
                        try:
                            parsed = json.loads(edited_bdi_beliefs_json)
                            if 'beliefs' in parsed and isinstance(parsed['beliefs'], list):
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    beliefs=parsed['beliefs']
                                )
                                st.success("✅ BDI Beliefs saved!")
                                st.rerun()
                            else:
                                st.error("❌ JSON must contain a 'beliefs' array")
                        except AttributeError:
                            st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    st.markdown("---")

                    # Clear all BDI beliefs
                    if 'confirm_clear_bdi_beliefs' not in st.session_state:
                        st.session_state.confirm_clear_bdi_beliefs = False

                    if not st.session_state.confirm_clear_bdi_beliefs:
                        if st.button("🗑️ Clear All", width='stretch', key="clear_bdi_beliefs"):
                            st.session_state.confirm_clear_bdi_beliefs = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Sure?")
                        if st.button("✅ Yes", width='stretch', key="btn_confirm_clear_bdi_beliefs"):
                            try:
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    beliefs=[]
                                )
                                st.session_state.confirm_clear_bdi_beliefs = False
                                st.success("✅ Cleared!")
                                st.rerun()
                            except AttributeError:
                                st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        if st.button("❌ No", width='stretch', key="btn_cancel_clear_bdi_beliefs"):
                            st.session_state.confirm_clear_bdi_beliefs = False
                            st.rerun()

                    # Validate JSON
                    if st.button("✅ Validate JSON", width='stretch', key="validate_bdi_beliefs_json"):
                        try:
                            parsed = json.loads(edited_bdi_beliefs_json)
                            if 'beliefs' in parsed and isinstance(parsed['beliefs'], list):
                                st.success(f"✅ Valid JSON! Found {len(parsed['beliefs'])} BDI beliefs.")
                            else:
                                st.error("❌ JSON must contain a 'beliefs' array")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    # Stats
                    st.metric("Total BDI Beliefs", len(bdi_beliefs))

    # ============================================================================
    # TAB 5: Intentions Management
    # ============================================================================
    with tab5:
        st.markdown("### 🎯 Intentions Management")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before managing intentions.")
        else:
            # Toggle per espandere l'editor intentions
            if 'intentions_editor_expanded' not in st.session_state:
                st.session_state.intentions_editor_expanded = False

            # Layout: Editor JSON a sinistra, pulsanti a destra (o full width se espanso)
            if st.session_state.intentions_editor_expanded:
                # Modalità espansa: editor a schermo intero
                col1 = st.container()
                col2 = None
            else:
                # Modalità normale: 2 colonne
                col1, col2 = st.columns([3, 1])

            with col1:
                # Carica intentions dal BDI
                try:
                    bdi_data = get_cached_bdi_data(st.session_state.editing_session_id)
                    intentions = bdi_data.get('intentions', []) if bdi_data else []
                except AttributeError:
                    # Fallback se il metodo non è ancora disponibile
                    st.warning("⚠️ SessionManager non aggiornato. Riavvia l'applicazione per caricare le nuove funzionalità.")
                    intentions = []

                # JSON editor con syntax highlighting
                intentions_json = json.dumps({"intentions": intentions}, indent=2, ensure_ascii=False)

                # Header con pulsante expand inline
                col_label, col_spacer, col_btn = st.columns([3, 0.6, 0.4])
                with col_label:
                    st.markdown("**Edit Intentions as JSON**")
                with col_btn:
                    expand_icon = "🔼" if st.session_state.intentions_editor_expanded else "🔽"
                    if st.button(expand_icon, key="toggle_intentions_editor", help="Expand/Collapse editor", width='stretch'):
                        st.session_state.intentions_editor_expanded = not st.session_state.intentions_editor_expanded
                        st.rerun()

                # Configurazione del code editor (altezza dinamica in base allo stato)
                editor_height = [40, 60] if st.session_state.intentions_editor_expanded else [20, 25]

                response = code_editor(
                    code=intentions_json,
                    lang="json",
                    height=editor_height,
                    theme="default",
                    shortcuts="vscode",
                    allow_reset=True,
                    key=f"intentions_editor_{st.session_state.editing_session_id}",
                    options={
                        "wrap": True,
                        "showLineNumbers": True,
                        "highlightActiveLine": True,
                        "fontSize": 14,
                    }
                )

                # Il valore editato è in response['text']
                # Se il code editor non ha ancora un valore, usa il JSON originale
                if response and 'text' in response and response['text'].strip():
                    edited_intentions_json = response['text']
                else:
                    edited_intentions_json = intentions_json

            # Pulsanti laterali (solo se NON espanso)
            if not st.session_state.intentions_editor_expanded and col2:
                with col2:
                    st.markdown("###")

                    # Save Intentions
                    if st.button("💾 Save Intentions", width='stretch', type="primary", key="save_intentions"):
                        try:
                            parsed = json.loads(edited_intentions_json)
                            if 'intentions' in parsed and isinstance(parsed['intentions'], list):
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    intentions=parsed['intentions']
                                )
                                st.success("✅ Intentions saved!")
                                st.rerun()
                            else:
                                st.error("❌ JSON must contain an 'intentions' array")
                        except AttributeError:
                            st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    # Clear all Intentions
                    if 'confirm_clear_intentions' not in st.session_state:
                        st.session_state.confirm_clear_intentions = False

                    if not st.session_state.confirm_clear_intentions:
                        if st.button("🗑️ Clear All", width='stretch', key="clear_intentions"):
                            st.session_state.confirm_clear_intentions = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Sure?")
                        if st.button("✅ Yes", width='stretch', key="btn_confirm_clear_intentions"):
                            try:
                                st.session_state.session_manager.update_bdi_data(
                                    st.session_state.editing_session_id,
                                    intentions=[]
                                )
                                st.session_state.confirm_clear_intentions = False
                                st.success("✅ Cleared!")
                                st.rerun()
                            except AttributeError:
                                st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        if st.button("❌ No", width='stretch', key="btn_cancel_clear_intentions"):
                            st.session_state.confirm_clear_intentions = False
                            st.rerun()

                    # Validate JSON
                    if st.button("✅ Validate JSON", width='stretch', key="validate_intentions_json"):
                        try:
                            parsed = json.loads(edited_intentions_json)
                            if 'intentions' in parsed and isinstance(parsed['intentions'], list):
                                st.success(f"✅ Valid JSON! Found {len(parsed['intentions'])} intentions.")
                            else:
                                st.error("❌ JSON must contain an 'intentions' array")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    # Stats
                    st.metric("Total Intentions", len(intentions))

    # ============================================================================
    # TAB 6: Analytics
    # ============================================================================
    with tab6:
        st.markdown("### 📊 Analytics")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before viewing analytics.")
        else:
            # Lazy load Plotly (solo nel tab6 Analytics)
            import plotly.graph_objects as go
            import plotly.express as px

            # Carica i dati BDI
            try:
                bdi_data = get_cached_bdi_data(st.session_state.editing_session_id)

                # Estrai desires e beliefs
                if bdi_data:
                    # Nuova struttura: domains -> beneficiari -> desires (compatibile con legacy 'personas')
                    if isinstance(bdi_data.get('domains'), list) and bdi_data['domains']:
                        desires = []
                        for idx, domain in enumerate(bdi_data['domains']):
                            # Estrai nome domain: prova 'name', poi le prime 5 parole di 'domain_summary', altrimenti usa indice
                            domain_name = domain.get('name')
                            if not domain_name and 'domain_summary' in domain:
                                # Prendi le prime 5 parole del domain_summary
                                words = domain['domain_summary'].split()[:5]
                                domain_name = ' '.join(words) + ('...' if len(domain['domain_summary'].split()) > 5 else '')
                            if not domain_name:
                                domain_name = f'Domain {idx + 1}'

                            for beneficiario in domain.get('beneficiari', []) or domain.get('personas', []) or []:
                                # Estrai nome beneficiario: prova 'name', poi 'beneficiario_name'/'persona_name', altrimenti 'Unknown'
                                beneficiario_name = (
                                    beneficiario.get('name')
                                    or beneficiario.get('beneficiario_name')
                                    or beneficiario.get('persona_name', 'Unknown')
                                )

                                for desire in beneficiario.get('desires', []) or []:
                                    desire['domain'] = domain_name
                                    desire['beneficiario'] = beneficiario_name
                                    desires.append(desire)
                    # Vecchia struttura: lista piatta
                    elif isinstance(bdi_data.get('desires'), list):
                        desires = bdi_data['desires']
                    else:
                        desires = []

                    # Beliefs
                    bdi_beliefs = bdi_data.get('beliefs', [])
                else:
                    desires = []
                    bdi_beliefs = []

            except AttributeError:
                st.warning("⚠️ SessionManager non aggiornato. Riavvia l'applicazione per caricare le nuove funzionalità.")
                desires = []
                bdi_beliefs = []

            # Estrai intentions (per usarle in tutta la sezione Analytics)
            intentions = bdi_data.get('intentions', []) if bdi_data else []

            # ============================================================================
            # SEZIONE 1: STATISTICHE AGGREGATE
            # ============================================================================
            st.markdown("#### 📈 Aggregate Statistics")

            # Metriche generali
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Desires", len(desires))

            with col2:
                st.metric("Total Intentions", len(intentions))

            with col3:
                st.metric("Total Beliefs", len(bdi_beliefs))

            with col4:
                # Calcola coverage: desires con almeno un belief collegato
                desires_with_beliefs = 0
                if desires and bdi_beliefs:
                    for desire in desires:
                        # Supporta sia 'id' che 'desire_id' per compatibilità
                        desire_id = desire.get('desire_id') or desire.get('id')
                        for belief in bdi_beliefs:
                            related = belief.get('related_desires', [])

                            # Supporta sia array semplice che array di oggetti
                            for item in related:
                                if isinstance(item, dict):
                                    related_id = item.get('desire_id')
                                else:
                                    related_id = item

                                if desire_id == related_id:
                                    desires_with_beliefs += 1
                                    break
                            else:
                                continue
                            break
                coverage_pct = (desires_with_beliefs / len(desires) * 100) if desires else 0
                st.metric("Coverage %", f"{coverage_pct:.1f}%")

            with col5:
                # Calcola numero di domini e beneficiari
                domains_count = len(bdi_data.get('domains', [])) if bdi_data else 0
                beneficiari_count = sum(
                    len(d.get('beneficiari', []) or d.get('personas', []))
                    for d in bdi_data.get('domains', [])
                ) if bdi_data and bdi_data.get('domains') else 0
                st.metric("Domains/Beneficiari", f"{domains_count}/{beneficiari_count}")

            st.markdown("---")

            # Checkbox per abilitare l'analisi dettagliata (lazy render charts)
            show_detailed_analysis = st.checkbox(
                "📊 Show Detailed Analysis (Beliefs, Desires, Intentions charts)",
                value=True,
                help="Disabilita per velocizzare il caricamento della pagina"
            )

            if show_detailed_analysis:
                # ============================================================================
                # SEZIONE 1: BELIEFS ANALYSIS (2 colonne)
                # ============================================================================
                col_left_beliefs, col_right_beliefs = st.columns(2)

                with col_left_beliefs:
                    st.markdown("##### 🧠 Beliefs Analysis - Relations")

                    # Grafico tipologie di relazioni beliefs
                    if bdi_beliefs:
                        # Supporta sia 'type' che 'relazione' per compatibilità
                        belief_relations = {}
                        for belief in bdi_beliefs:
                            # Prova prima 'semantic_relations', poi 'type' come fallback
                            relation = belief.get('semantic_relations') or belief.get('type', 'undefined')
                            belief_relations[relation] = belief_relations.get(relation, 0) + 1

                        # Mostra solo se ci sono dati significativi (non solo 'undefined')
                        if len(belief_relations) > 1 or 'undefined' not in belief_relations:
                            fig_relations = px.pie(
                                values=list(belief_relations.values()),
                                names=list(belief_relations.keys()),
                                title="Beliefs by Relation Type",
                                color_discrete_sequence=px.colors.sequential.Teal
                            )
                            st.plotly_chart(fig_relations, width='stretch')  

                        st.info("No beliefs found. Generate some beliefs in Believer to see statistics.")

                with col_right_beliefs:
                    st.markdown("##### 🧠 Beliefs Analysis - Relevance")

                    if bdi_beliefs:
                        # Grafico relevance scores (se disponibile)
                        relevance_scores = []
                        for belief in bdi_beliefs:
                            if 'relevance_score' in belief:
                                relevance_scores.append(belief['relevance_score'])

                        if relevance_scores:
                            fig_relevance = px.histogram(
                                x=relevance_scores,
                                nbins=20,
                                title="Relevance Scores Distribution",
                                labels={'x': 'Relevance Score', 'y': 'Count'},
                                color_discrete_sequence=['#A23B72']
                            )
                            st.plotly_chart(fig_relevance, width='stretch')  

                        # Grafico livelli di rilevanza (se struttura related_desires)
                        relevance_levels = []
                        for belief in bdi_beliefs:
                            if 'related_desires' in belief:
                                for rd in belief.get('related_desires', []):
                                    if 'relevance_level' in rd:
                                        relevance_levels.append(rd['relevance_level'])

                        if relevance_levels:
                            level_counts = {}
                            for level in relevance_levels:
                                level_counts[level] = level_counts.get(level, 0) + 1

                            fig_levels = px.bar(
                                x=list(level_counts.keys()),
                                y=list(level_counts.values()),
                                title="Relevance Levels Distribution",
                                labels={'x': 'Level', 'y': 'Count'},
                                color=list(level_counts.values()),
                                color_continuous_scale='Reds'
                            )
                            st.plotly_chart(fig_levels, width='stretch')  
                    else:
                        st.info("No beliefs found. Generate some beliefs in Believer to see statistics.")

                st.markdown("---")

                # ============================================================================
                # SEZIONE 2: DESIRES ANALYSIS (2 colonne)
                # ============================================================================
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("##### 💭 Desires Analysis - Metrics")

                    # Grafico Success Metrics per Desire
                    if desires:
                        # Calcola quanti success metrics ha ogni desire
                        desire_metrics = {}
                        for desire in desires:
                            desire_id = desire.get('desire_id') or desire.get('id', 'Unknown')
                            metrics_count = len(desire.get('success_metrics', []))
                            # Usa una label più corta per il grafico
                            short_label = f"{desire_id}"
                            desire_metrics[short_label] = metrics_count

                        # Crea grafico a barre
                        fig_metrics = px.bar(
                            x=list(desire_metrics.keys()),
                            y=list(desire_metrics.values()),
                            title="Success Metrics per Desire",
                            labels={'x': 'Desire ID', 'y': 'Number of Success Metrics'},
                            color=list(desire_metrics.values()),
                            color_continuous_scale='Blues',
                            text=list(desire_metrics.values())
                        )
                        fig_metrics.update_traces(textposition='outside')
                        st.plotly_chart(fig_metrics, width='stretch')  
                    else:
                        st.info("No desires found. Create some desires in Alì to see statistics.")

                with col_right:
                    st.markdown("##### 💭 Desires Analysis - Beliefs")

                    if desires and bdi_beliefs:
                        # Conta quanti beliefs sono collegati a ogni desire
                        beliefs_per_desire = {}
                        for desire in desires:
                            desire_id = desire.get('desire_id') or desire.get('id')
                            beliefs_per_desire[desire_id] = 0

                        # Conta i collegamenti
                        for belief in bdi_beliefs:
                            related = belief.get('related_desires', [])

                            for item in related:
                                # Supporta sia array semplice di stringhe che array di oggetti
                                if isinstance(item, dict):
                                    desire_id = item.get('desire_id')
                                else:
                                    desire_id = item

                                if desire_id in beliefs_per_desire:
                                    beliefs_per_desire[desire_id] += 1

                        # Crea grafico a barre
                        fig_beliefs_count = px.bar(
                            x=list(beliefs_per_desire.keys()),
                            y=list(beliefs_per_desire.values()),
                            title="Beliefs per Desire",
                            labels={'x': 'Desire ID', 'y': 'Number of Beliefs'},
                            color=list(beliefs_per_desire.values()),
                            color_continuous_scale='Greens',
                            text=list(beliefs_per_desire.values())
                        )
                        fig_beliefs_count.update_traces(textposition='outside')
                        st.plotly_chart(fig_beliefs_count, width='stretch')  
                    else:
                        st.info("No desires or beliefs found.")

                st.markdown("---")

                # ============================================================================
                # SEZIONE 3: INTENTIONS ANALYSIS (2 colonne)
                # ============================================================================
                col_int_left, col_int_right = st.columns(2)

                with col_int_left:
                    st.markdown("##### 🎯 Intentions Analysis - Distribution")

                    if intentions:
                        # Grafico 1: Distribuzione Intentions per Desire
                        intentions_per_desire = {}
                        for intention in intentions:
                            # Estrai desire IDs (supporta diverse naming conventions)
                            related_desires = (
                                intention.get('related_desires', []) or
                                intention.get('desires', []) or
                                intention.get('intention', {}).get('related_desires', []) or
                                intention.get('intention', {}).get('desires', []) or
                                []
                            )
                            if intention.get('linked_desire_id'):
                                related_desires = list(related_desires) + [intention.get('linked_desire_id')]
                            if intention.get('intention', {}).get('linked_desire_id'):
                                related_desires = list(related_desires) + [intention['intention'].get('linked_desire_id')]

                            # Se nessun desire è collegato, usa "Unassigned"
                            if not related_desires:
                                intentions_per_desire['Unassigned'] = intentions_per_desire.get('Unassigned', 0) + 1
                            else:
                                for item in related_desires:
                                    desire_id = item.get('desire_id') or item.get('id') if isinstance(item, dict) else item
                                    if desire_id:
                                        desire_key = f"{desire_id}"
                                        intentions_per_desire[desire_key] = intentions_per_desire.get(desire_key, 0) + 1

                        if intentions_per_desire:
                            fig_intentions_per_desire = px.bar(
                                x=list(intentions_per_desire.values()),
                                y=list(intentions_per_desire.keys()),
                                orientation='h',
                                title="Intentions Distribution per Desire",
                                labels={'x': 'Count', 'y': 'Desire'},
                                color=list(intentions_per_desire.values()),
                                color_continuous_scale='Viridis',
                                text=list(intentions_per_desire.values())
                            )
                            fig_intentions_per_desire.update_traces(textposition='outside')
                            st.plotly_chart(fig_intentions_per_desire, width='stretch')
                    else:
                        st.info("No intentions found. Create some intentions to see statistics.")

                with col_int_right:
                    st.markdown("##### 🎯 Intentions Analysis - Steps")

                    if intentions:
                        # Grafico 2: Steps per Intention
                        intention_steps = {}
                        for idx, intention in enumerate(intentions):
                            # Estrai intention ID
                            intention_id = (
                                intention.get('intention_id') or
                                intention.get('id') or
                                intention.get('intention', {}).get('intention_id') or
                                intention.get('intention', {}).get('id') or
                                f"I{idx+1}"
                            )

                            # Conta i steps (supporta diverse naming conventions: steps, plan, actions, tasks, action_plan)
                            steps_count = 0

                            # Primo livello: steps direttamente nell'intention
                            if 'steps' in intention:
                                steps_count = len(intention.get('steps', []))
                            elif 'plan' in intention:
                                steps_count = len(intention.get('plan', []))
                            elif 'actions' in intention:
                                steps_count = len(intention.get('actions', []))
                            elif 'tasks' in intention:
                                steps_count = len(intention.get('tasks', []))
                            # Secondo livello: dentro action_plan
                            elif 'action_plan' in intention:
                                action_plan = intention.get('action_plan', {})
                                if 'steps' in action_plan:
                                    steps_count = len(action_plan.get('steps', []))
                            # Terzo livello: dentro intention (struttura annidata)
                            elif 'intention' in intention:
                                nested = intention.get('intention', {})
                                if 'steps' in nested:
                                    steps_count = len(nested.get('steps', []))
                                elif 'plan' in nested:
                                    steps_count = len(nested.get('plan', []))
                                elif 'actions' in nested:
                                    steps_count = len(nested.get('actions', []))
                                elif 'tasks' in nested:
                                    steps_count = len(nested.get('tasks', []))
                                elif 'action_plan' in nested:
                                    action_plan = nested.get('action_plan', {})
                                    if 'steps' in action_plan:
                                        steps_count = len(action_plan.get('steps', []))

                            # Ottieni priority per colore (se disponibile)
                            priority = intention.get('priority') or intention.get('intention', {}).get('priority', 'Medium')

                            intention_steps[f"{intention_id}"] = {
                                'steps': steps_count,
                                'priority': priority
                            }

                        if intention_steps:
                            # Prepara dati per il grafico
                            intentions_labels = list(intention_steps.keys())
                            steps_values = [intention_steps[k]['steps'] for k in intentions_labels]

                            fig_steps = go.Figure(data=[
                                go.Bar(
                                    x=steps_values,
                                    y=intentions_labels,
                                    orientation='h',
                                    marker=dict(color='#5DADE2'),  # Colore freddo rassicurante (blu azzurro)
                                    text=steps_values,
                                    textposition='outside',
                                    hovertemplate='<b>%{y}</b><br>Steps: %{x}<extra></extra>'
                                )
                            ])

                            fig_steps.update_layout(
                                title="Steps per Intention",
                                xaxis_title="Number of Steps",
                                yaxis_title="Intention",
                                showlegend=False,
                                height=max(300, 50 * len(intentions_labels))
                            )

                            st.plotly_chart(fig_steps, width='stretch')
                    else:
                        st.info("No intentions found. Create some intentions to see statistics.")

                st.markdown("---")

                
    # ============================================================================
    # TAB 7: Grafo BDI
    # ============================================================================
    with tab7:

        # ============================================================================
                # SEZIONE 4: GRAFO DELLE RELAZIONI INTERATTIVO (PyVis)
                # ============================================================================
                st.markdown("#### 🕸️ Interactive Relationship Graph")

                try:
                    from pyvis.network import Network
                    import streamlit.components.v1 as components
                    import tempfile
                    import os

                    if desires or bdi_beliefs or intentions:
                        # Tentativo di rilevare il tema di base dalla configurazione (non live)
                        try:
                            theme_base = st.get_option("theme.base")
                            default_idx = 1 if theme_base == "light" else 0
                        except:
                            default_idx = 0

                        # Leggi tema precedente dalla session state
                        if "graph_theme_toggle" not in st.session_state:
                            st.session_state.graph_theme_toggle = default_idx == 0  # True = Dark

                        if "graph_layout_choice" not in st.session_state:
                            st.session_state.graph_layout_choice = "No Physics (Static)"

                        st.markdown("---")

                        # Riga con pulsanti layout e tema
                        layout_options = [
                            ("No Physics", "No Physics (Static)"),
                            ("BarnesHut", "BarnesHut (Force-Directed)"),
                            ("ForceAtlas2", "ForceAtlas2Based"),
                            ("Hierarchical", "Hierarchical"),
                            ("Repulsion", "Repulsion"),
                            ("Circular", "Circular"),
                            ("Radial", "Radial")
                        ]

                        # Crea colonne con etichetta e pulsanti layout
                        col_label, *layout_cols_list, col_separator, col_theme = st.columns([0.8] + [1] * len(layout_options) + [0.2, 0.6])

                        # Etichetta "Layouts:"
                        with col_label:
                            st.markdown("**Layouts:**")

                        # Pulsanti layout
                        for idx, (label, value) in enumerate(layout_options):
                            with layout_cols_list[idx]:
                                if st.button(label, key=f"btn_layout_{value}", width='stretch'):
                                    st.session_state.graph_layout_choice = value
                                    st.rerun()

                        # Separatore visivo
                        with col_separator:
                            st.markdown("")
                        with col_theme:
                            col_d, col_l = st.columns(2)
                            with col_d:
                                if st.button("🌙", key="btn_dark_theme", help="Dark", type="secondary", width='stretch'):
                                    st.session_state.graph_theme_toggle = True
                                    st.rerun()
                            with col_l:
                                if st.button("☀️", key="btn_light_theme", help="Light", type="secondary", width='stretch'):
                                    st.session_state.graph_theme_toggle = False
                                    st.rerun()

                        layout_choice = st.session_state.graph_layout_choice
                        graph_theme = "Dark" if st.session_state.graph_theme_toggle else "Light"

                        # Imposta sfondo trasparente per adattarsi alla pagina
                        bg_color = "rgba(0,0,0,0)"

                        # Determina i colori del contenuto in base al tema selezionato
                        if graph_theme == "Dark":
                            font_color = "#fafafa"
                            edge_color = "#555555"
                        else:
                            font_color = "#333333"
                            edge_color = "#888888"

                        # Crea network PyVis
                        net = Network(
                            height="600px",
                            width="100%",
                            bgcolor=bg_color,
                            font_color=font_color,
                            notebook=False,
                            directed=False
                        )

                        # Configura physics in base al layout selezionato
                        if layout_choice == "BarnesHut (Force-Directed)":
                            physics_config = {
                                "enabled": True,
                                "barnesHut": {
                                    "gravitationalConstant": -8000,
                                    "centralGravity": 0.3,
                                    "springLength": 95,
                                    "springConstant": 0.04,
                                    "damping": 0.09
                                },
                                "solver": "barnesHut",
                                "stabilization": {
                                    "enabled": True,
                                    "iterations": 200
                                }
                            }
                        elif layout_choice == "ForceAtlas2Based":
                            physics_config = {
                                "enabled": True,
                                "forceAtlas2Based": {
                                    "gravitationalConstant": -50,
                                    "centralGravity": 0.01,
                                    "springLength": 200,
                                    "springConstant": 0.08,
                                    "damping": 0.4,
                                    "avoidOverlap": 0.5
                                },
                                "solver": "forceAtlas2Based",
                                "stabilization": {
                                    "enabled": True,
                                    "iterations": 200
                                }
                            }
                        elif layout_choice == "Hierarchical":
                            physics_config = {
                                "enabled": True,
                                "hierarchicalRepulsion": {
                                    "centralGravity": 0.0,
                                    "springLength": 100,
                                    "nodeDistance": 200,
                                    "damping": 0.3
                                },
                                "solver": "hierarchicalRepulsion",
                                "stabilization": {
                                    "enabled": True,
                                    "iterations": 200
                                }
                            }
                        elif layout_choice == "Repulsion":
                            physics_config = {
                                "enabled": True,
                                "repulsion": {
                                    "nodeDistance": 200,
                                    "centralGravity": 0.2,
                                    "springLength": 200,
                                    "springConstant": 0.05,
                                    "damping": 0.09
                                },
                                "solver": "repulsion",
                                "stabilization": {
                                    "enabled": True,
                                    "iterations": 200
                                }
                            }
                        elif layout_choice == "Circular":
                            # Per layout circolare, disabilitiamo la fisica e posizioneremo i nodi in cerchio dopo
                            physics_config = {
                                "enabled": False
                            }
                        elif layout_choice == "Radial":
                            # Per layout radiale, disabilitiamo la fisica e posizioneremo i nodi in modo radiale dopo
                            physics_config = {
                                "enabled": False
                            }
                        else:  # No Physics (Static)
                            physics_config = {
                                "enabled": False
                            }

                        options_dict = {
                            "physics": physics_config,
                            "interaction": {
                                "hover": True,
                                "tooltipDelay": 100,
                                "navigationButtons": True,
                                "keyboard": True
                            },
                            "nodes": {
                                "font": {
                                    "size": 14,
                                    "face": "arial"
                                }
                            },
                            "edges": {
                                "smooth": {
                                    "type": "continuous"
                                }
                            }
                        }

                        import json
                        net.set_options(json.dumps(options_dict))

                        # Funzione helper per normalizzare gli ID durante il matching
                        def normalize_id(id_value, prefix=''):
                            """Strips a known prefix and leading zeros from an ID for robust matching.

                            Handles the inconsistent ID formats that may appear in BDI
                            data (e.g. ``"B1"``, ``"B01"``, ``"1"``), producing a
                            canonical numeric string so belief-to-desire edges can be
                            resolved reliably.

                            Args:
                                id_value: The raw ID (str or int).
                                prefix: Optional alphabetic prefix to strip before
                                    removing leading zeros (e.g. ``"B"`` or ``"D"``).

                            Returns:
                                str: The normalized numeric portion of the ID.
                                Returns ``"0"`` when the result would otherwise be empty.
                            """
                            if isinstance(id_value, str):
                                normalized = id_value.replace(prefix, '').lstrip('0') if prefix else id_value.lstrip('0')
                                return normalized or '0'
                            return str(id_value)

                        # Funzione helper per layout circolare
                        def apply_circular_layout(network, nodes_list):
                            """Arranges all nodes in a single circle around the origin.

                            Each node is placed at an equal angular interval on a circle
                            of fixed radius so the graph is immediately readable without
                            relying on the physics solver.

                            Args:
                                network: A ``pyvis.network.Network`` instance whose
                                    ``.nodes`` list will be mutated in place.
                                nodes_list: Ordered list of node IDs to position.
                            """
                            import math
                            center_x, center_y = 0, 0
                            radius = 300
                            num_nodes = len(nodes_list)

                            for idx, node_id in enumerate(nodes_list):
                                angle = 2 * math.pi * idx / num_nodes
                                x = center_x + radius * math.cos(angle)
                                y = center_y + radius * math.sin(angle)
                                network.nodes[idx]['x'] = x
                                network.nodes[idx]['y'] = y
                                network.nodes[idx]['fixed'] = False

                        # Funzione helper per layout radiale
                        def apply_radial_layout(network, nodes_list, center_idx=0):
                            """Places one node at the center and distributes the rest in concentric rings.

                            Useful when a single "hub" node (e.g. a high-priority Desire)
                            should visually dominate the graph.  Remaining nodes are
                            spread across up to three rings with increasing radius.

                            Args:
                                network: A ``pyvis.network.Network`` instance whose
                                    ``.nodes`` list will be mutated in place.
                                nodes_list: Ordered list of node IDs to position.
                                center_idx: Index within *nodes_list* of the node that
                                    should be placed at the origin.  Defaults to ``0``.
                            """
                            import math
                            center_x, center_y = 0, 0
                            num_rings = 3

                            # Nodo al centro
                            if len(nodes_list) > 0:
                                center_node_id = nodes_list[center_idx]
                                # Trova l'indice del nodo nel network
                                for idx, node in enumerate(network.nodes):
                                    if node['id'] == center_node_id:
                                        network.nodes[idx]['x'] = center_x
                                        network.nodes[idx]['y'] = center_y
                                        network.nodes[idx]['fixed'] = False
                                        break

                            # Nodi in anelli concentrici
                            remaining_nodes = [n for i, n in enumerate(nodes_list) if i != center_idx]
                            nodes_per_ring = max(3, len(remaining_nodes) // num_rings)

                            for ring_idx in range(num_rings):
                                radius = 150 + (ring_idx + 1) * 150
                                start_idx = ring_idx * nodes_per_ring
                                end_idx = start_idx + nodes_per_ring if ring_idx < num_rings - 1 else len(remaining_nodes)
                                ring_nodes = remaining_nodes[start_idx:end_idx]
                                num_in_ring = len(ring_nodes)

                                for pos_idx, node_id in enumerate(ring_nodes):
                                    angle = 2 * math.pi * pos_idx / max(1, num_in_ring)
                                    x = center_x + radius * math.cos(angle)
                                    y = center_y + radius * math.sin(angle)

                                    # Trova l'indice del nodo nel network
                                    for idx, node in enumerate(network.nodes):
                                        if node['id'] == node_id:
                                            network.nodes[idx]['x'] = x
                                            network.nodes[idx]['y'] = y
                                            network.nodes[idx]['fixed'] = False
                                            break

                        # Funzione helper per creare tooltip HTML
                        def create_tooltip(node_type, node_id, full_desc, data):
                            """Builds a plain-text tooltip string for a BDI graph node.

                            Plain text is used instead of HTML because PyVis renders
                            raw HTML tags as visible characters in some browsers.
                            The description is truncated at 200 characters.  Extra
                            metadata fields are appended depending on the node type:

                            * **Desire** – priority and success-metric count.
                            * **Belief** – importance and confidence scores.
                            * **Intention** – action-plan step count and effort estimate.

                            Args:
                                node_type: One of ``"Desire"``, ``"Belief"``,
                                    or ``"Intention"``.
                                node_id: Display identifier shown at the top of the
                                    tooltip (e.g. ``"D1"``).
                                full_desc: Full description text; will be truncated if
                                    longer than 200 characters.
                                data: The raw BDI dict for this node, used to extract
                                    type-specific metadata.

                            Returns:
                                str: Formatted tooltip string ready for PyVis.
                            """
                            tooltip = f"{node_id} ({node_type})\n\n"

                            # Trunca descrizione se troppo lunga
                            if len(full_desc) > 200:
                                full_desc = full_desc[:197] + "..."
                            tooltip += f"Description:\n{full_desc}\n\n"

                            # Info specifiche per tipo
                            if node_type == 'Desire':
                                priority = data.get('priority', 'N/A')
                                metrics_count = len(data.get('success_metrics', []))
                                tooltip += f"Priority: {priority}\n"
                                tooltip += f"Success Metrics: {metrics_count}\n"
                            elif node_type == 'Belief':
                                importance = data.get('importance', 'N/A')
                                confidence = data.get('confidence', 'N/A')
                                tooltip += f"Importance: {importance}\n"
                                tooltip += f"Confidence: {confidence}\n"
                            elif node_type == 'Intention':
                                steps = 0
                                effort = 'N/A'
                                # Controlla prima action_plan a livello root
                                if 'action_plan' in data:
                                    steps = len(data.get('action_plan', {}).get('steps', []))
                                    effort = data.get('action_plan', {}).get('estimated_effort', 'N/A')
                                else:
                                    # Poi controlla dentro 'intention'
                                    intention_data = data.get('intention', {})
                                    if 'action_plan' in intention_data:
                                        steps = len(intention_data.get('action_plan', {}).get('steps', []))
                                        effort = intention_data.get('action_plan', {}).get('estimated_effort', 'N/A')
                                    elif 'steps' in intention_data:
                                        steps = len(intention_data.get('steps', []))
                                tooltip += f"Steps: {steps}\n"
                                tooltip += f"Effort: {effort}"

                            return tooltip

                        # Aggiungi nodi Desires
                        for desire in desires:
                            desire_id = desire.get('desire_id') or desire.get('id')
                            desc = desire.get('desire_statement') or desire.get('description', 'No desc')
                            label = f"{desire_id}"

                            tooltip = create_tooltip('Desire', f"{desire_id}", desc, desire)

                            # Dimensione basata su priorità
                            priority = desire.get('priority', 'medium')
                            if isinstance(priority, str):
                                priority = priority.lower()
                            priority_sizes = {
                                'high': 35,
                                'alta': 35,
                                'medium': 25,
                                'media': 25,
                                'low': 18,
                                'bassa': 18
                            }
                            desire_size = priority_sizes.get(priority, 25)

                            net.add_node(
                                label,
                                label=label,
                                title=tooltip,
                                color='#FF6B6B',
                                size=desire_size,
                                shape='dot'
                            )

                        # Filtra beliefs: mantieni solo quelli collegati a desires o intentions
                        filtered_beliefs = []
                        for idx, belief in enumerate(bdi_beliefs):
                            belief_id = belief.get('id', idx+1)
                            has_relation = False

                            # Controlla se il belief è collegato a desires
                            related_desires = belief.get('related_desires', [])
                            if related_desires:
                                has_relation = True

                            # Controlla se il belief è collegato a intentions
                            if not has_relation:
                                for intention in intentions:
                                    linked_beliefs = (
                                        intention.get('linked_beliefs', []) or
                                        intention.get('intention', {}).get('linked_beliefs', []) or
                                        []
                                    )
                                    for item in linked_beliefs:
                                        # Item può essere una stringa (es. "B2") o un numero
                                        if isinstance(item, dict):
                                            belief_id_check = item.get('id')
                                        elif isinstance(item, str):
                                            # Estrai il numero da "B2" -> "2"
                                            belief_id_check = int(item.replace('B', '')) if item.startswith('B') else int(item)
                                        else:
                                            belief_id_check = item

                                        # Converti belief_id a int per confronto uniforme
                                        if int(belief_id) == int(belief_id_check):
                                            has_relation = True
                                            break
                                    if has_relation:
                                        break

                            if has_relation:
                                filtered_beliefs.append(belief)

                        # Aggiungi nodi Beliefs (solo quelli con relazioni)
                        for idx, belief in enumerate(filtered_beliefs):
                            belief_id = belief.get('id', f"{idx+1}")
                            content = belief.get('subject') or belief.get('content') or belief.get('description', 'No content')
                            label = f"B{belief_id}"

                            tooltip = create_tooltip('Belief', f"B{belief_id}", belief.get('definition', content), belief)

                            # Dimensione basata su importance score (0.0-1.0)
                            importance = belief.get('importance', 0.5)
                            # Scala: da 15 (importance=0.0) a 35 (importance=1.0)
                            belief_size = 15 + int(importance * 20)

                            net.add_node(
                                label,
                                label=label,
                                title=tooltip,
                                color='#4ECDC4',
                                size=belief_size,
                                shape='dot'
                            )

                        # Aggiungi nodi Intentions
                        for idx, intention in enumerate(intentions):
                            intention_id = (
                                intention.get('id') or
                                intention.get('intention', {}).get('id') or
                                f"I{idx+1}"
                            )
                            content = (
                                intention.get('statement') or
                                intention.get('intention', {}).get('statement') or
                                'No content'
                            )
                            label = f"{intention_id}"

                            tooltip = create_tooltip('Intention', label, content, intention)

                            # Dimensione basata su numero di beliefs + desires collegati
                            linked_beliefs = (
                                intention.get('linked_beliefs', []) or
                                intention.get('intention', {}).get('linked_beliefs', []) or
                                []
                            )
                            linked_desires = (
                                intention.get('linked_desires', []) or
                                intention.get('intention', {}).get('linked_desires', []) or
                                []
                            )
                            total_connections = len(linked_beliefs) + len(linked_desires)
                            # Scala: base 20, +3 per ogni connessione
                            intention_size = 20 + (total_connections * 3)
                            # Cap massimo a 50 per evitare nodi troppo grandi
                            intention_size = min(intention_size, 50)

                            net.add_node(
                                label,
                                label=label,
                                title=tooltip,
                                color='#FFD93D',
                                size=intention_size,
                                shape='dot'
                            )

                        # Crea set di nodi esistenti per validazione rapida
                        # In PyVis, net.nodes è una lista di dizionari, non un dict
                        existing_nodes = set([node['id'] for node in net.nodes])

                        # Aggiungi edges Belief -> Desire (con validazione nodi e normalizzazione ID)
                        for idx, belief in enumerate(filtered_beliefs):
                            belief_id = belief.get('id')
                            belief_label = f"B{belief_id}"
                            related = belief.get('related_desires', [])

                            for item in related:
                                if isinstance(item, dict):
                                    desire_id = item.get('desire_id')
                                else:
                                    desire_id = item

                                # Trova il nodo desire corrispondente e verifica esistenza con normalizzazione ID
                                for desire in desires:
                                    d_id = desire.get('desire_id') or desire.get('id')
                                    # Normalizza per matching robusto (D1, D01, 1, ecc.)
                                    normalized_linked = normalize_id(str(desire_id), prefix='D')
                                    normalized_d_id = normalize_id(str(d_id), prefix='D')

                                    if d_id == desire_id or normalized_d_id == normalized_linked:
                                        # Usa d_id (che include già "D" prefix) come label
                                        desire_label = f"{d_id}"
                                        # Verifica che entrambi i nodi esistono
                                        if belief_label in existing_nodes and desire_label in existing_nodes:
                                            net.add_edge(belief_label, desire_label, color=edge_color)
                                        break

                        # Aggiungi edges Intention -> Desire (con validazione nodi)
                        for idx, intention in enumerate(intentions):
                            intention_id = (
                                intention.get('intention_id') or
                                intention.get('id') or
                                intention.get('intention', {}).get('intention_id') or
                                intention.get('intention', {}).get('id') or
                                f"I{idx+1}"
                            )
                            intention_label = f"{intention_id}"

                            # Verifica che il nodo intention esiste
                            if intention_label not in existing_nodes:
                                continue

                            # Estrai related desires
                            related_desires = (
                                intention.get('related_desires', []) or
                                intention.get('desires', []) or
                                intention.get('intention', {}).get('related_desires', []) or
                                intention.get('intention', {}).get('desires', []) or
                                []
                            )

                            # Aggiungi linked_desire_id se presente
                            if intention.get('linked_desire_id'):
                                related_desires = list(related_desires) + [intention.get('linked_desire_id')]
                            if intention.get('intention', {}).get('linked_desire_id'):
                                related_desires = list(related_desires) + [intention['intention'].get('linked_desire_id')]

                            for item in related_desires:
                                if isinstance(item, dict):
                                    desire_id = item.get('desire_id') or item.get('id')
                                else:
                                    desire_id = item

                                if desire_id:
                                    # Assicura che desire_id abbia il prefisso "D"
                                    if not str(desire_id).startswith('D'):
                                        desire_label = f"D{desire_id}"
                                    else:
                                        desire_label = f"{desire_id}"
                                    # Verifica che il nodo desire esiste
                                    if desire_label in existing_nodes:
                                        net.add_edge(intention_label, desire_label, color=edge_color)

                        # Aggiungi edges Intention -> Belief (con validazione nodi e normalizzazione ID)
                        for idx, intention in enumerate(intentions):
                            intention_id = (
                                intention.get('intention_id') or
                                intention.get('id') or
                                intention.get('intention', {}).get('intention_id') or
                                intention.get('intention', {}).get('id') or
                                f"I{idx+1}"
                            )
                            intention_label = f"{intention_id}"

                            # Verifica che il nodo intention esiste
                            if intention_label not in existing_nodes:
                                continue

                            related_beliefs = (
                                intention.get('linked_beliefs', []) or
                                intention.get('intention', {}).get('linked_beliefs', []) or
                                intention.get('related_beliefs', []) or
                                intention.get('intention', {}).get('related_beliefs', []) or
                                intention.get('beliefs', []) or
                                intention.get('intention', {}).get('beliefs', []) or
                                []
                            )

                            for item in related_beliefs:
                                if isinstance(item, dict):
                                    linked_belief_id = item.get('belief_id') or item.get('id')
                                else:
                                    linked_belief_id = item

                                if linked_belief_id:
                                    # Normalizza per matching robusto (B1, B01, 1, ecc.)
                                    normalized_linked = normalize_id(str(linked_belief_id), prefix='B')

                                    # Cerca il belief corrispondente nel grafo
                                    for belief_node in existing_nodes:
                                        belief_node_str = str(belief_node)
                                        if belief_node_str.startswith('B'):
                                            normalized_belief = normalize_id(belief_node_str, prefix='B')
                                            if normalized_belief == normalized_linked:
                                                # Verifica che il nodo belief esiste
                                                if belief_node in existing_nodes:
                                                    net.add_edge(intention_label, belief_node, color=edge_color)
                                                break

                        # Applica layout circolare o radiale se selezionato
                        all_node_ids = [node['id'] for node in net.nodes]

                        if layout_choice == "Circular":
                            apply_circular_layout(net, all_node_ids)
                        elif layout_choice == "Radial":
                            # Per layout radiale, metti il primo nodo al centro
                            apply_radial_layout(net, all_node_ids, center_idx=0)

                        # Genera HTML
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                            net.save_graph(f.name)
                            temp_file = f.name

                        # Leggi il file e mostra in Streamlit
                        with open(temp_file, 'r', encoding='utf-8') as html_file:
                            html_content = html_file.read()

                            # Aggiungi CSS per il tema selezionato
                            if graph_theme == "Dark":
                                theme_css = '''<style>
                                * {
                                    border: none !important;
                                }
                                html, body, #mynetwork, canvas {
                                    background-color: #0e1117 !important;
                                    color: #fafafa !important;
                                    border: none !important;
                                    margin: 0;
                                    padding: 0;
                                }
                                .vis-network {
                                    background-color: #0e1117 !important;
                                    border: none !important;
                                }
                                .vis-tooltip {
                                    max-width: 400px !important;
                                    white-space: normal !important;
                                    word-break: break-word !important;
                                    word-wrap: break-word !important;
                                    overflow-wrap: break-word !important;
                                }
                                </style>'''
                            else:
                                theme_css = '''<style>
                                html, body, #mynetwork, canvas {
                                    background-color: #ffffff !important;
                                    color: #333333 !important;
                                    border: none !important;
                                    margin: 0;
                                    padding: 0;
                                }
                                .vis-network {
                                    background-color: #ffffff !important;
                                    border: none !important;
                                }
                                .vis-tooltip {
                                    max-width: 400px !important;
                                    white-space: normal !important;
                                    word-break: break-word !important;
                                    word-wrap: break-word !important;
                                    overflow-wrap: break-word !important;
                                }
                                </style>'''

                            html_content = html_content.replace('</head>', theme_css + '</head>')
                            components.html(html_content, height=650, scrolling=True)

                        # Cleanup
                        try:
                            os.unlink(temp_file)
                        except:
                            pass

                        # Info box
                        st.info("""
                        💡 **PyVis Graph Features:**
                        - 🖱️ **Drag nodes** to reposition them
                        - 🔍 **Zoom** with mouse wheel
                        - 👆 **Hover** over nodes for detailed tooltips
                        - 🎯 **Click** nodes to highlight connections
                        - ⌨️ **Use arrow keys** to navigate
                        """)

                    else:
                        st.info("No data available for PyVis graph visualization.")

                except ImportError:
                    st.error("❌ PyVis library not installed. Run: `pip install pyvis>=0.3.2`")
                except Exception as e:
                    st.error(f"❌ Error creating PyVis graph: {str(e)}")
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem;'>
    <p><strong>🧭 Compass</strong> - Session Configuration Module</p>
    <p style='font-size: 0.85rem;'>Configure once, work seamlessly across all LumIA modules</p>
</div>
""", unsafe_allow_html=True)

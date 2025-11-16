import streamlit as st
import os
import sys
import json
from datetime import datetime
from code_editor import code_editor
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.session_manager import SessionManager
from utils.context_manager import ContextManager
from utils.llm_manager import LLMManager

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

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

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
        if st.button("🏠", width='stretch', type="secondary", help="Torna alla Home"):
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
                    if st.button("📂", key=f"load_{session['session_id']}", help="Load session", use_container_width=True):
                        st.session_state.editing_session_id = session['session_id']
                        st.session_state.active_session = session['session_id']
                        st.session_state.new_session_requested = False
                        st.success(f"Session '{metadata['name']}' loaded!")
                        st.rerun()

                    if st.button("🗑️", key=f"del_{session['session_id']}", help="Delete session", use_container_width=True):
                        st.session_state.session_manager.delete_session(session['session_id'])
                        if st.session_state.editing_session_id == session['session_id']:
                            st.session_state.editing_session_id = None
                        st.rerun()

                st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    else:
        st.info("No sessions yet. Create your first one!")

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

            submitted = st.form_submit_button("Create Session", type="primary", use_container_width=True)

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Session Settings", "🗂️ Context & Beliefs", "💭 Desires", "🧠 Beliefs", "📊 Analytics"])

    # ============================================================================
    # TAB 1: Session Info (nome, descrizione, LLM)
    # ============================================================================
    with tab1:
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

            # Carica configurazione LLM esistente
            if current_session:
                config = current_session['config']
                current_provider = config.get('llm_provider', available_providers[0])
                current_model = config.get('llm_model')
                llm_settings = config.get('llm_settings', {
                    'use_defaults': True,
                    'temperature': 1.0,
                    'top_p': 0.95,  # Default Gemini
                    'max_output_tokens': 65536,  # Gemini
                    'max_tokens': 4096,  # OpenAI
                    'reasoning_effort': 'medium'  # GPT-5
                })
            else:
                current_provider = available_providers[0]
                current_model = None
                llm_settings = {
                    'use_defaults': True,
                    'temperature': 1.0,
                    'top_p': 0.95,
                    'max_output_tokens': 65536,
                    'max_tokens': 4096,
                    'reasoning_effort': 'medium'
                }

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
                    help="Use LLM provider's default parameters. Uncheck to customize."
                )

                # Determina i valori di default in base al provider
                is_gemini = selected_provider == "Gemini"
                is_gpt5 = selected_model.startswith("gpt-5")

                default_top_p = 0.95 if is_gemini else 1.0

                # Disabilita i parametri se use_defaults è True
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=llm_settings.get('temperature', 1.0),
                    step=0.1,
                    help="Controls randomness. Default: 1.0 for all providers",
                    disabled=use_defaults
                )

                top_p = st.slider(
                    "Top P",
                    min_value=0.0,
                    max_value=1.0,
                    value=llm_settings.get('top_p', default_top_p),
                    step=0.05,
                    help=f"Nucleus sampling. Default: {default_top_p} ({'Gemini' if is_gemini else 'OpenAI'})",
                    disabled=use_defaults
                )

                # Max tokens - diverso per provider
                if is_gemini:
                    max_output_tokens = st.number_input(
                        "Max Output Tokens",
                        min_value=1,
                        max_value=65536,
                        value=llm_settings.get('max_output_tokens', 65536),
                        step=1024,
                        help="Maximum output tokens for Gemini. Default: 65536",
                        disabled=use_defaults
                    )
                    max_tokens = None
                else:
                    max_tokens = st.number_input(
                        "Max Tokens",
                        min_value=1,
                        max_value=16384,
                        value=llm_settings.get('max_tokens', 4096),
                        step=512,
                        help="Maximum tokens for OpenAI. Default: 4096",
                        disabled=use_defaults
                    )
                    max_output_tokens = None

                # Reasoning effort - solo per GPT-5
                if is_gpt5:
                    reasoning_effort = st.selectbox(
                        "Reasoning Effort",
                        options=['minimal', 'low', 'medium', 'high'],
                        index=['minimal', 'low', 'medium', 'high'].index(llm_settings.get('reasoning_effort', 'medium')),
                        help="Controls reasoning depth for GPT-5. Default: medium",
                        disabled=use_defaults
                    )
                else:
                    reasoning_effort = None

            # Prepara llm_settings
            new_llm_settings = {
                'use_defaults': use_defaults,
                'temperature': temperature,
                'top_p': top_p
            }

            if is_gemini:
                new_llm_settings['max_output_tokens'] = max_output_tokens
            else:
                new_llm_settings['max_tokens'] = max_tokens

            if is_gpt5:
                new_llm_settings['reasoning_effort'] = reasoning_effort

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
                        if st.button(expand_icon, key="toggle_editor", help="Expand/Collapse editor", use_container_width=True):
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
        st.markdown("### 💭 Desires Management")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before managing desires.")
        else:
            # Toggle per espandere l'editor desires
            if 'desires_editor_expanded' not in st.session_state:
                st.session_state.desires_editor_expanded = False

            # Layout: Editor JSON a sinistra, pulsanti a destra (o full width se espanso)
            if st.session_state.desires_editor_expanded:
                # Modalità espansa: editor a schermo intero
                col1 = st.container()
                col2 = None
            else:
                # Modalità normale: 2 colonne
                col1, col2 = st.columns([3, 1])

            with col1:
                # Carica desires dal BDI (supporta nuova struttura domains/personas e legacy)
                try:
                    bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.editing_session_id)
                    if bdi_data:
                        # Nuova struttura: domains -> personas -> desires
                        if isinstance(bdi_data.get('domains'), list) and bdi_data['domains']:
                            desires = []
                            for domain in bdi_data['domains']:
                                for persona in domain.get('personas', []) or []:
                                    for desire in persona.get('desires', []) or []:
                                        desires.append(desire)
                        # Vecchia struttura: lista piatta
                        elif isinstance(bdi_data.get('desires'), list):
                            desires = bdi_data['desires']
                        else:
                            desires = []
                    else:
                        desires = []
                except AttributeError:
                    # Fallback se il metodo non è ancora disponibile
                    st.warning("⚠️ SessionManager non aggiornato. Riavvia l'applicazione per caricare le nuove funzionalità.")
                    desires = []

                # JSON editor con syntax highlighting
                # Mostra solo la collection domains per editing
                if isinstance(bdi_data, dict) and bdi_data:
                    # Estrai solo la collection domains per l'editing
                    domains_data = bdi_data.get('domains', [])
                    if domains_data:
                        desires_json = json.dumps({"domains": domains_data}, indent=2, ensure_ascii=False)
                    else:
                        # Se non ci sono domains, mostra struttura vuota
                        desires_json = json.dumps({"domains": []}, indent=2, ensure_ascii=False)
                else:
                    # Fallback per struttura legacy o dati vuoti
                    desires_json = json.dumps({"domains": []}, indent=2, ensure_ascii=False)

                # Header con pulsante expand inline
                col_label, col_spacer, col_btn = st.columns([3, 0.6, 0.4])
                with col_label:
                    st.markdown("**Edit domains structure**")
                with col_btn:
                    expand_icon = "🔼" if st.session_state.desires_editor_expanded else "🔽"
                    if st.button(expand_icon, key="toggle_desires_editor", help="Expand/Collapse editor", use_container_width=True):
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
                    edited_desires_json = response['text']
                else:
                    edited_desires_json = desires_json

            # Pulsanti laterali (solo se NON espanso)
            if not st.session_state.desires_editor_expanded and col2:
                with col2:
                    st.markdown("###")

                    # Save Desires
                    if st.button("💾 Save Desires", width='stretch', type="primary", key="save_desires"):
                        try:
                            parsed = json.loads(edited_desires_json)
                            
                            # Salva solo la collection domains, preservando il resto del BDI
                            if 'domains' in parsed and isinstance(parsed['domains'], list):
                                # Carica il BDI esistente per preservare beliefs e altri dati
                                existing_bdi = st.session_state.session_manager.get_bdi_data(st.session_state.editing_session_id) or {}
                                
                                # Aggiorna solo la collection domains
                                updated_bdi = {
                                    **existing_bdi,  # Preserva tutto il contenuto esistente
                                    "domains": parsed['domains']  # Aggiorna solo domains
                                }
                                
                                # Salva il BDI aggiornato
                                session_dir = st.session_state.session_manager.base_dir / st.session_state.editing_session_id
                                bdi_file = session_dir / "current_bdi.json"
                                with open(bdi_file, 'w', encoding='utf-8') as f:
                                    json.dump(updated_bdi, f, ensure_ascii=False, indent=2)
                                
                                st.success("✅ Domains structure saved!")
                            else:
                                st.error("❌ JSON must contain a 'domains' array")
                            st.rerun()
                        except AttributeError:
                            st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    # Clear all domains
                    if 'confirm_clear_desires' not in st.session_state:
                        st.session_state.confirm_clear_desires = False

                    if not st.session_state.confirm_clear_desires:
                        if st.button("🗑️ Clear All", width='stretch', key="clear_desires"):
                            st.session_state.confirm_clear_desires = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Sure?")
                        if st.button("✅ Yes", width='stretch', key="btn_confirm_clear_desires"):
                            try:
                                # Carica il BDI esistente e cancella solo domains
                                existing_bdi = st.session_state.session_manager.get_bdi_data(st.session_state.editing_session_id) or {}
                                updated_bdi = {
                                    **existing_bdi,  # Preserva tutto il contenuto esistente
                                    "domains": []  # Cancella solo domains
                                }
                                
                                # Salva il BDI aggiornato
                                session_dir = st.session_state.session_manager.base_dir / st.session_state.editing_session_id
                                bdi_file = session_dir / "current_bdi.json"
                                with open(bdi_file, 'w', encoding='utf-8') as f:
                                    json.dump(updated_bdi, f, ensure_ascii=False, indent=2)
                                
                                st.session_state.confirm_clear_desires = False
                                st.success("✅ Domains cleared!")
                                st.rerun()
                            except AttributeError:
                                st.error("❌ SessionManager non aggiornato. Riavvia l'applicazione.")
                        if st.button("❌ No", width='stretch', key="btn_cancel_clear_desires"):
                            st.session_state.confirm_clear_desires = False
                            st.rerun()

                    # Validate JSON
                    if st.button("✅ Validate JSON", width='stretch', key="validate_desires_json"):
                        try:
                            parsed = json.loads(edited_desires_json)
                            if 'domains' in parsed and isinstance(parsed['domains'], list):
                                # Conta desires in domains/personas
                                total_desires = 0
                                for domain in parsed['domains']:
                                    for persona in domain.get('personas', []) or []:
                                        total_desires += len(persona.get('desires', []) or [])
                                st.success(f"✅ Valid domains JSON! Found {total_desires} desires across {len(parsed['domains'])} domains.")
                            else:
                                st.error("❌ JSON must contain a 'domains' array")
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                    # Stats
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
                    bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.editing_session_id)
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
                    if st.button(expand_icon, key="toggle_bdi_beliefs_editor", help="Expand/Collapse editor", use_container_width=True):
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
    # TAB 5: Analytics
    # ============================================================================
    with tab5:
        st.markdown("### 📊 Analytics")

        if not current_session:
            st.warning("⚠️ Please save session info in the first tab before viewing analytics.")
        else:
            # Carica i dati BDI
            try:
                bdi_data = st.session_state.session_manager.get_bdi_data(st.session_state.editing_session_id)

                # Estrai desires e beliefs
                if bdi_data:
                    # Nuova struttura: domains -> personas -> desires
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

                            for persona in domain.get('personas', []) or []:
                                # Estrai nome persona: prova 'name', poi 'persona_name', altrimenti 'Unknown'
                                persona_name = persona.get('name') or persona.get('persona_name', 'Unknown')

                                for desire in persona.get('desires', []) or []:
                                    desire['domain'] = domain_name
                                    desire['persona'] = persona_name
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

            # ============================================================================
            # SEZIONE 1: STATISTICHE AGGREGATE
            # ============================================================================
            st.markdown("#### 📈 Aggregate Statistics")

            # Metriche generali
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Desires", len(desires))

            with col2:
                st.metric("Total Beliefs", len(bdi_beliefs))

            with col3:
                # Calcola coverage: desires con almeno un belief collegato
                desires_with_beliefs = 0
                if desires and bdi_beliefs:
                    for desire in desires:
                        # Supporta sia 'id' che 'desire_id' per compatibilità
                        desire_id = desire.get('desire_id') or desire.get('id')
                        for belief in bdi_beliefs:
                            # Supporta sia 'related_desires' (array semplice) che 'desires_correlati' (array di oggetti)
                            related = belief.get('related_desires', [])
                            if not related and 'desires_correlati' in belief:
                                # Estrai gli ID dagli oggetti desires_correlati
                                related = [dc.get('desire_id') for dc in belief.get('desires_correlati', []) if dc.get('desire_id')]

                            if desire_id in related:
                                desires_with_beliefs += 1
                                break
                coverage_pct = (desires_with_beliefs / len(desires) * 100) if desires else 0
                st.metric("Coverage %", f"{coverage_pct:.1f}%")

            with col4:
                # Calcola numero di domini e personas
                domains_count = len(bdi_data.get('domains', [])) if bdi_data else 0
                personas_count = sum(len(d.get('personas', [])) for d in bdi_data.get('domains', [])) if bdi_data and bdi_data.get('domains') else 0
                st.metric("Domains/Personas", f"{domains_count}/{personas_count}")

            st.markdown("---")

            # Layout a 2 colonne per i grafici delle statistiche
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("##### 💭 Desires Analysis")

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
                    st.plotly_chart(fig_metrics, use_container_width=True)

                    # Grafico Beliefs per Desire
                    if bdi_beliefs:
                        # Conta quanti beliefs sono collegati a ogni desire
                        beliefs_per_desire = {}
                        for desire in desires:
                            desire_id = desire.get('desire_id') or desire.get('id')
                            beliefs_per_desire[desire_id] = 0

                        # Conta i collegamenti
                        for belief in bdi_beliefs:
                            # Supporta sia 'related_desires' che 'desires_correlati'
                            related = belief.get('related_desires', [])
                            if not related and 'desires_correlati' in belief:
                                related = [dc.get('desire_id') for dc in belief.get('desires_correlati', []) if dc.get('desire_id')]

                            for desire_id in related:
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
                        st.plotly_chart(fig_beliefs_count, use_container_width=True)
                else:
                    st.info("No desires found. Create some desires in Alì to see statistics.")

            with col_right:
                st.markdown("##### 🧠 Beliefs Analysis")

                # Grafico tipologie di relazioni beliefs
                if bdi_beliefs:
                    # Supporta sia 'type' che 'relazione' per compatibilità
                    belief_relations = {}
                    for belief in bdi_beliefs:
                        # Prova prima 'relazione', poi 'type' come fallback
                        relation = belief.get('relazione') or belief.get('type', 'undefined')
                        belief_relations[relation] = belief_relations.get(relation, 0) + 1

                    # Mostra solo se ci sono dati significativi (non solo 'undefined')
                    if len(belief_relations) > 1 or 'undefined' not in belief_relations:
                        fig_relations = px.pie(
                            values=list(belief_relations.values()),
                            names=list(belief_relations.keys()),
                            title="Beliefs by Relation Type",
                            color_discrete_sequence=px.colors.sequential.Teal
                        )
                        st.plotly_chart(fig_relations, use_container_width=True)

                    # Grafico livelli di confidenza (se disponibile)
                    confidence_levels = []
                    for belief in bdi_beliefs:
                        if 'confidence' in belief:
                            confidence_levels.append(belief['confidence'])

                    if confidence_levels:
                        fig_confidence = px.histogram(
                            x=confidence_levels,
                            nbins=20,
                            title="Confidence Levels Distribution",
                            labels={'x': 'Confidence', 'y': 'Count'},
                            color_discrete_sequence=['#2E86AB']
                        )
                        st.plotly_chart(fig_confidence, use_container_width=True)

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
                        st.plotly_chart(fig_relevance, use_container_width=True)

                    # Grafico livelli di rilevanza (se struttura desires_correlati)
                    relevance_levels = []
                    for belief in bdi_beliefs:
                        if 'desires_correlati' in belief:
                            for dc in belief.get('desires_correlati', []):
                                if 'livello_rilevanza' in dc:
                                    relevance_levels.append(dc['livello_rilevanza'])

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
                        st.plotly_chart(fig_levels, use_container_width=True)
                else:
                    st.info("No beliefs found. Generate some beliefs in Believer to see statistics.")

            # ============================================================================
            # SEZIONE 2: GRAFO DELLE RELAZIONI
            # ============================================================================
            st.markdown("---")
            st.markdown("#### 🕸️ Relationship Graph")

            # Selettore layout
            col_title, col_layout = st.columns([3, 1])
            with col_layout:
                layout_type = st.selectbox(
                    "Layout",
                    ["Bipartite", "Spring", "Circular", "Kamada-Kawai"],
                    help="Choose the graph layout algorithm"
                )

            if desires or bdi_beliefs:
                # Crea il grafo NetworkX
                G = nx.Graph()

                # Dizionari per tracciare nodi e colori
                node_colors = {}
                node_types = {}

                # Aggiungi nodi Desire
                for desire in desires:
                    # Supporta sia 'id' che 'desire_id' per compatibilità
                    desire_id = desire.get('desire_id') or desire.get('id')
                    if desire_id:
                        # Usa 'desire_statement' se disponibile, altrimenti 'description'
                        desc = desire.get('desire_statement') or desire.get('description', 'No desc')
                        node_label = f"D{desire_id}: {desc[:30]}..."
                        G.add_node(node_label)
                        node_colors[node_label] = '#FF6B6B'  # Rosso per desires
                        node_types[node_label] = 'Desire'

                # Aggiungi nodi Belief (usa indice come ID se non presente)
                for idx, belief in enumerate(bdi_beliefs):
                    belief_id = belief.get('id', f"B{idx+1}")
                    # Usa diversi campi per il contenuto del belief
                    content = belief.get('content') or belief.get('soggetto', 'No content')
                    node_label = f"{belief_id}: {content[:30]}..."
                    G.add_node(node_label)
                    node_colors[node_label] = '#4ECDC4'  # Teal per beliefs
                    node_types[node_label] = 'Belief'

                # Aggiungi edge tra Belief e Desire
                for idx, belief in enumerate(bdi_beliefs):
                    belief_id = belief.get('id', f"B{idx+1}")
                    content = belief.get('content') or belief.get('soggetto', 'No content')
                    belief_label = f"{belief_id}: {content[:30]}..."

                    # Supporta sia 'related_desires' (array semplice) che 'desires_correlati' (array di oggetti)
                    related = belief.get('related_desires', [])
                    if not related and 'desires_correlati' in belief:
                        # Estrai gli ID dagli oggetti desires_correlati
                        related = [dc.get('desire_id') for dc in belief.get('desires_correlati', []) if dc.get('desire_id')]

                    for desire_id in related:
                        # Trova il desire corrispondente
                        for desire in desires:
                            d_id = desire.get('desire_id') or desire.get('id')
                            if d_id == desire_id:
                                desc = desire.get('desire_statement') or desire.get('description', 'No desc')
                                desire_label = f"D{desire_id}: {desc[:30]}..."
                                if belief_label in G.nodes and desire_label in G.nodes:
                                    G.add_edge(belief_label, desire_label)
                                break

                # Calcola posizioni dei nodi in base al layout selezionato
                if len(G.nodes) > 0:
                    if layout_type == "Bipartite":
                        # Layout bipartito: Desires a sinistra, Beliefs a destra
                        pos = {}
                        desires_nodes = [n for n in G.nodes() if node_types[n] == 'Desire']
                        beliefs_nodes = [n for n in G.nodes() if node_types[n] == 'Belief']

                        # Posiziona Desires a sinistra (x=0)
                        for i, node in enumerate(desires_nodes):
                            pos[node] = (0, i - len(desires_nodes)/2)

                        # Posiziona Beliefs a destra (x=1)
                        for i, node in enumerate(beliefs_nodes):
                            pos[node] = (1, i - len(beliefs_nodes)/2)

                    elif layout_type == "Spring":
                        pos = nx.spring_layout(G, k=1, iterations=50)

                    elif layout_type == "Circular":
                        pos = nx.circular_layout(G)

                    elif layout_type == "Kamada-Kawai":
                        pos = nx.kamada_kawai_layout(G)

                    # Prepara edge traces
                    edge_x = []
                    edge_y = []
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])

                    edge_trace = go.Scatter(
                        x=edge_x, y=edge_y,
                        line=dict(width=1, color='#888'),
                        hoverinfo='none',
                        mode='lines'
                    )

                    # Prepara node traces (separati per tipo per avere colori diversi)
                    desire_nodes_x = []
                    desire_nodes_y = []
                    desire_nodes_text = []

                    belief_nodes_x = []
                    belief_nodes_y = []
                    belief_nodes_text = []

                    for node in G.nodes():
                        x, y = pos[node]
                        if node_types[node] == 'Desire':
                            desire_nodes_x.append(x)
                            desire_nodes_y.append(y)
                            desire_nodes_text.append(node)
                        else:
                            belief_nodes_x.append(x)
                            belief_nodes_y.append(y)
                            belief_nodes_text.append(node)

                    desire_trace = go.Scatter(
                        x=desire_nodes_x, y=desire_nodes_y,
                        mode='markers+text',
                        hoverinfo='text',
                        text=desire_nodes_text,
                        textposition="top center",
                        marker=dict(
                            color='#FF6B6B',
                            size=20,
                            line=dict(width=2, color='white')
                        ),
                        name='Desires'
                    )

                    belief_trace = go.Scatter(
                        x=belief_nodes_x, y=belief_nodes_y,
                        mode='markers+text',
                        hoverinfo='text',
                        text=belief_nodes_text,
                        textposition="top center",
                        marker=dict(
                            color='#4ECDC4',
                            size=20,
                            line=dict(width=2, color='white')
                        ),
                        name='Beliefs'
                    )

                    # Crea figura
                    fig = go.Figure(data=[edge_trace, desire_trace, belief_trace],
                                    layout=go.Layout(
                                        title=dict(
                                            text='Desire-Belief Relationship Graph',
                                            font=dict(size=16)
                                        ),
                                        showlegend=True,
                                        hovermode='closest',
                                        margin=dict(b=20, l=5, r=5, t=40),
                                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                        height=600
                                    ))

                    st.plotly_chart(fig, use_container_width=True)

                    # Statistiche del grafo
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Nodes", len(G.nodes))
                    with col2:
                        st.metric("Total Edges", len(G.edges))
                    with col3:
                        # Calcola densità
                        density = nx.density(G) if len(G.nodes) > 1 else 0
                        st.metric("Graph Density", f"{density:.2f}")
                    with col4:
                        # Calcola componenti connesse
                        components = nx.number_connected_components(G)
                        st.metric("Connected Components", components)
                else:
                    st.info("No nodes to display. Create desires and beliefs with relationships to see the graph.")
            else:
                st.info("No data available for graph visualization. Create desires and beliefs to see the relationship graph.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem;'>
    <p><strong>🧭 Compass</strong> - Session Configuration Module</p>
    <p style='font-size: 0.85rem;'>Configure once, work seamlessly across all LumIA modules</p>
</div>
""", unsafe_allow_html=True)

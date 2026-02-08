import streamlit as st

# Page configuration
st.set_page_config(
    page_title="LumIA Studio - BDI Framework",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Toggle button for theme
col_theme1, col_theme2, col_theme3 = st.columns([6, 1, 1])
with col_theme3:
    theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    theme_text = "Dark" if not st.session_state.dark_mode else "Light"
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle", width='stretch'):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Generate dynamic CSS based on theme
theme_colors = {
    'light': {
        'bg_gradient': 'linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe)',
        'container_bg': 'rgba(255, 255, 255, 0.95)',
        'text_primary': '#333',
        'text_secondary': '#666',
        'text_tertiary': '#888',
        'card_bg': 'white',
        'workflow_bg': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        'workflow_step_bg': 'white',
        'workflow_text': '#555',
        'border_color': '#eee',
        'shadow': 'rgba(0,0,0,0.1)',
        'shadow_hover': 'rgba(102, 126, 234, 0.4)',
        'footer_border': '#eee',
        'footer_text': '#888',
    },
    'dark': {
        'bg_gradient': 'linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #533483)',
        'container_bg': 'rgba(26, 26, 46, 0.95)',
        'text_primary': '#e0e0e0',
        'text_secondary': '#b0b0b0',
        'text_tertiary': '#888',
        'card_bg': '#1e1e2e',
        'workflow_bg': 'linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%)',
        'workflow_step_bg': '#2a2a3e',
        'workflow_text': '#b0b0b0',
        'border_color': '#333',
        'shadow': 'rgba(0,0,0,0.5)',
        'shadow_hover': 'rgba(102, 126, 234, 0.6)',
        'footer_border': '#333',
        'footer_text': '#666',
    }
}

current_theme = 'dark' if st.session_state.dark_mode else 'light'
colors = theme_colors[current_theme]

bg_gradient = colors['bg_gradient']
container_bg = colors['container_bg']
text_primary = colors['text_primary']
text_secondary = colors['text_secondary']
text_tertiary = colors['text_tertiary']
card_bg = colors['card_bg']
workflow_bg = colors['workflow_bg']
workflow_step_bg = colors['workflow_step_bg']
workflow_text = colors['workflow_text']
shadow = colors['shadow']
shadow_hover = colors['shadow_hover']
footer_text = colors['footer_text']
footer_border = colors['footer_border']

# Advanced custom CSS
st.markdown(f"""
<style>
    /* Import Google fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* Reset and base font */
    * {{{{
        font-family: 'Poppins', sans-serif;
    }}}}

    /* Hide unnecessary Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Hide sidebar completely on homepage */
    [data-testid="stSidebarNav"] {{display: none;}}
    section[data-testid="stSidebar"] {{display: none;}}

    /* Animated gradient background */
    .main {{
        background: {bg_gradient};
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        transition: background 0.5s ease;
    }}

    @keyframes gradientBG {{{{ 
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}}}

    /* Main container */
    .block-container {{
        background: {container_bg};
        padding: 3rem 2rem !important;
        box-shadow: 0 20px 60px {shadow};
        backdrop-filter: blur(10px);
        transition: all 0.5s ease;
    }}

    /* Animated header */
    .main-header {{
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeInDown 1s ease;
    }}

    @keyframes fadeInDown {{{{ 
        from {{
            opacity: 0;
            transform: translateY(-30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}}}

    .main-title {{
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}

    .main-subtitle {{
        font-size: 1.3rem;
        color: {text_secondary};
        font-weight: 300;
        margin-bottom: 1rem;
    }}

    .main-description {{
        font-size: 1rem;
        color: {text_tertiary};
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
    }}

    /* Workflow section */
    .workflow-section {{
        background: {workflow_bg};
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
    }}

    .workflow-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {text_primary};
        margin-bottom: 1rem;
    }}

    .workflow-steps {{
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1.5rem;
    }}

    .workflow-step {{
        background: {workflow_step_bg};
        border-radius: 15px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 6px {shadow};
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: {workflow_text};
        transition: all 0.3s ease;
    }}

    .workflow-step:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 12px {shadow};
    }}

    .workflow-arrow {{
        font-size: 1.5rem;
        color: #667eea;
    }}

    /* Feature cards - IMPROVED ALIGNMENT */
    .feature-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px {shadow};
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
        height: 100%;
        min-height: 320px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 0;
    }}

    .feature-card:hover::before {{
        opacity: 0.1;
    }}

    .feature-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px {shadow_hover};
        border-color: #667eea;
    }}

    .feature-title-container {{
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }}

    .feature-emoji {{
        font-size: 2.5rem;
        margin-right: 1rem;
        display: block;
        position: relative;
        z-index: 1;
        transition: transform 0.3s ease;
    }}

    .feature-card:hover .feature-emoji {{
        transform: scale(1.1);
    }}

    .feature-title {{
        font-size: 1.6rem;
        font-weight: 600;
        color: {text_primary};
        position: relative;
        z-index: 1;
    }}

    .feature-description {{
        font-size: 0.95rem;
        color: {text_secondary};
        line-height: 1.6;
        position: relative;
        z-index: 1;
        flex-grow: 1;
        margin-bottom: 1.5rem;
    }}

    .feature-status {{
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        z-index: 1;
    }}

    .status-active {{
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }}

    .status-dev {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }}

    .feature-button {{
        display: inline-block;
        text-decoration: none;
        background: linear-gradient(135deg, #4facfe 0%, #667eea 100%);
        color: white !important;
        padding: 0.75rem 1.5rem;
        border-radius: 15px;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        z-index: 1;
        border: none;
    }}

    .feature-button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        color: white !important;
        text-decoration: none;
    }}

    /* Footer */
    .custom-footer {{
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: {footer_text};
        font-size: 0.9rem;
        border-top: 1px solid {footer_border};
        margin-top: 3rem;
    }}

    /* Stats badges */
    .stats-container {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }}

    .stat-badge {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        text-align: center;
        min-width: 150px;
    }}

    .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        display: block;
    }}

    .stat-label {{
        font-size: 0.9rem;
        opacity: 0.9;
    }}

    /* Responsive */
    @media (max-width: 768px) {{{{ 
        .main-title {{ font-size: 2.5rem; }}
        .main-subtitle {{ font-size: 1rem; }}
        .feature-card {{ padding: 1.5rem; min-height: 280px; }}
        .workflow-steps {{ flex-direction: column; }}
    }}}}
</style>
""", unsafe_allow_html=True)

# Header principale con animazione
st.markdown(f"""
<div class='main-header'>
    <div class='main-title'>✨ LumIA Studio</div>
    <div class='main-subtitle'>Belief · Desire · Intention System</div>
    <div class='main-description'>
        Transform knowledge into action. An intelligent framework to define goals,
        identify beliefs, and plan actions through conversational AI agents.
    </div>
</div>
""", unsafe_allow_html=True)

# Workflow section (updated)
st.markdown("""
<div class='workflow-section'>
    <div class='workflow-title'>🚀 Recommended Workflow</div>
    <div class='workflow-steps'>
        <div class='workflow-step'>📚 <strong>Knol</strong> - Load & Define Knowledge Base</div>
        <div class='workflow-arrow'>→</div>
        <div class='workflow-step'>🧭 <strong>Compass</strong> - Configure your Working Session</div>
        <div class='workflow-arrow'>→</div>
        <div class='workflow-step'>🎯 <strong>Alì</strong> - Define Desire in your session</div>
        <div class='workflow-arrow'>→</div>
        <div class='workflow-step'>💡 <strong>Believer</strong> - Define & Review Beliefs in your session</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Feature definitions (organized by category)
features_configuration = [
    {
        "name": "Knol",
        "emoji": "📚",
        "description": "Load and manage PDF documents, web pages, text or markdown files to build a rich and structured knowledge base of your domain.",
        "page": "pages/1_Knol.py",
        "status": "active",
    },
    {
        "name": "Compass",
        "emoji": "🧭",
        "description": "Configure your working session: name it, select context, choose LLM engine and model, review and edit base beliefs before starting your BDI journey.",
        "page": "pages/0_Compass.py",
        "status": "active",
    }
]

features_domain = [
    {
        "name": "Alì",
        "emoji": "🎯",
        "description": "Chat with Alì, the AI agent specialized in helping you identify and define Desires (goals) associated with your domain in a clear and structured way.",
        "page": "pages/2_Ali.py",
        "status": "active",
    },
    {
        "name": "Believer",
        "emoji": "💡",
        "description": "Believer guides you in identifying Beliefs (convictions, facts, principles) that support your Desires, connecting them to your knowledge base.",
        "page": "pages/3_Believer.py",
        "status": "active",
    },
    {
        "name": "Cuma",
        "emoji": "🔮",
        "description": "Advanced module for predictive analysis and scenario planning. Uses your Beliefs and Desires to simulate possible future outcomes.",
        "page": "pages/5_Cuma.py",
        "status": "active",
    }
]

features_live = [
    {
        "name": "Genius",
        "emoji": "⚡",
        "description": "Intelligent optimization system that analyzes your complete BDI framework and suggests improvements and innovative strategies.",
        "page": "pages/6_Genius.py",
        "status": "active",
    }
]

# Helper function to create cards
def create_feature_card(feature):
    status_class = "status-active" if feature["status"] == "active" else "status-dev"
    status_text = "✓ Active" if feature["status"] == "active" else "🚧 In Development"
    page_link = feature['page'].split('/')[-1].split('.')[0].split('_', 1)[-1]

    return f"""
    <div class='feature-card'>
        <span class='feature-status {status_class}'>{status_text}</span>
        <div>
            <div class='feature-title-container'>
                <span class='feature-emoji'>{feature['emoji']}</span>
                <div class='feature-title'>{feature['name']}</div>
            </div>
            <div class='feature-description'>{feature['description']}</div>
        </div>
        <a href='/{page_link}' target='_self' class='feature-button'>Open {feature['name']}</a>
    </div>
    """

st.markdown("<br>", unsafe_allow_html=True)

# Modules section
st.markdown(f"<h2 style='text-align: center; color: {text_primary}; font-weight: 600; margin-bottom: 0;'>🎨 Explore Modules</h2>", unsafe_allow_html=True)

# CSS for grouped boxes
st.markdown(f"""
<style>
    .section-divider {{
        border-top: 3px solid rgba(102, 126, 234, 0.3);
        margin: 2rem 0 0.5rem 0;
    }}

    .section-label {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
        display: inline-block;
    }}
</style>
""", unsafe_allow_html=True)

# Configuration Section
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">⚙️ Configuration</div>', unsafe_allow_html=True)
cols = st.columns([0.5, 1, 1, 0.5])
with cols[1]:
    st.markdown(create_feature_card(features_configuration[0]), unsafe_allow_html=True)
with cols[2]:
    st.markdown(create_feature_card(features_configuration[1]), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Domain Definition Section
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">🎯 Domain Definition</div>', unsafe_allow_html=True)
cols = st.columns(3)
for idx, col in enumerate(cols):
    with col:
        st.markdown(create_feature_card(features_domain[idx]), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Live Sessions Section
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">⚡ Live Sessions</div>', unsafe_allow_html=True)
cols = st.columns([1.1, 1.8, 1.1])
with cols[1]:
    st.markdown(create_feature_card(features_live[0]), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class='custom-footer'>
    <p style='color: {text_primary};'><strong>✨ LumIA Studio</strong> - Belief · Desire · Intention System</p>
    <p style='font-size: 0.85rem; color: {text_tertiary}; margin-top: 0.5rem;'>
        Powered by AI • Streamlit • ChromaDB • LangChain
    </p>
    <p style='font-size: 0.8rem; color: {text_tertiary}; margin-top: 0.5rem;'>
        Version 1.0 • Theme: {theme_text}
    </p>
</div>
""", unsafe_allow_html=True)


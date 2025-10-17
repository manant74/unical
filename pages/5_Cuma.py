import streamlit as st

st.set_page_config(
    page_title="Cuma - LUMIA Studio",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔮 Cuma")
st.markdown("**Funzionalità in fase di sviluppo**")
st.divider()

# Contenuto placeholder
col1, col2 = st.columns([1, 1])

with col1:
    st.image("https://via.placeholder.com/400x300.png?text=Cuma+Coming+Soon", use_container_width=True)

with col2:
    st.info("""
    ### 🚧 In Costruzione

    La funzionalità **Cuma** è attualmente in fase di analisi e sviluppo.

    Questa sezione sarà disponibile nelle prossime versioni dell'applicazione.

    **Cosa aspettarsi:**
    - Nuove funzionalità per il framework BDI
    - Integrazione con Desires e Beliefs
    - Strumenti avanzati di analisi

    Resta sintonizzato per gli aggiornamenti!
    """)

st.markdown("---")

# Sezione per feedback
st.subheader("💬 Hai suggerimenti per questa funzionalità?")

feedback = st.text_area(
    "Condividi le tue idee",
    placeholder="Scrivi qui i tuoi suggerimenti per la funzionalità Cuma...",
    key="cuma_feedback"
)

if st.button("Invia Feedback", type="primary"):
    if feedback:
        # In futuro, qui si potrebbe salvare il feedback
        st.success("✅ Grazie per il tuo feedback! Lo prenderemo in considerazione.")
    else:
        st.warning("⚠️ Scrivi qualcosa prima di inviare!")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Torna alla Home", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("💡 Vai a Believer", use_container_width=True):
        st.switch_page("pages/3_Believer.py")

with col3:
    if st.button("⚡ Vai a Genius", use_container_width=True):
        st.switch_page("pages/5_Genius.py")

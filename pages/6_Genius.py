import streamlit as st

st.set_page_config(
    page_title="Genius - LumIA Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ Genius")
st.markdown("**Funzionalità in fase di sviluppo**")
st.divider()

# Contenuto placeholder
col1, col2 = st.columns([1, 1])

with col1:
    st.info("""
    ### 🚧 In Costruzione

    La funzionalità **Genius** è attualmente in fase di analisi e sviluppo.

    Questa sezione sarà disponibile nelle prossime versioni dell'applicazione.

    **Cosa aspettarsi:**
    - Funzionalità avanzate per il framework BDI
    - Analisi intelligente dei dati
    - Nuovi strumenti per ottimizzare Desires e Beliefs

    Resta sintonizzato per gli aggiornamenti!
    """)

with col2:
    st.image("https://via.placeholder.com/400x300.png?text=Genius+Coming+Soon", use_container_width=True)

st.markdown("---")

# Sezione per feedback
st.subheader("💬 Hai suggerimenti per questa funzionalità?")

feedback = st.text_area(
    "Condividi le tue idee",
    placeholder="Scrivi qui i tuoi suggerimenti per la funzionalità Genius...",
    key="genius_feedback"
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
    if st.button("🔮 Vai a Cuma", use_container_width=True):
        st.switch_page("pages/4_Cuma.py")

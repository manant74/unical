import streamlit as st
import json
import os
import sys

# Aggiungi la directory parent al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Validator - LUMIA Studio",
    page_icon="✅",
    layout="wide"
)

# CSS per nascondere menu Streamlit e applicare font monospazio
st.markdown("""<style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stTextArea"] textarea {
        font-family: 'Courier New', monospace !important;
        line-height: 1.5;
    }
</style>""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ✅ Validator")
    if st.button("🏠 Torna alla Home", use_container_width=True, type="secondary"):
        st.switch_page("app.py")
    st.divider()
    st.info("Usa questa pagina per modificare e validare manualmente il JSON del framework BDI prima di procedere.")

# --- Contenuto Principale ---
st.title("✅ Validator")
st.markdown("**Valida e modifica il framework BDI generato**")
st.divider()

BDI_FILE_PATH = "./data/current_bdi.json"

def load_bdi_data():
    if os.path.exists(BDI_FILE_PATH):
        with open(BDI_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_bdi_data(data):
    with open(BDI_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

bdi_data = load_bdi_data()

if bdi_data is None:
    st.warning("⚠️ Nessun dato BDI trovato. Completa prima la sessione con Believer.")
    if st.button("💡 Vai a Believer"):
        st.switch_page("pages/3_Believer.py")
    st.stop()

st.subheader("Editor JSON del framework BDI")

# Tabs per visualizzazione e editing
tab1, tab2 = st.tabs(["📝 Editor", "👁️ Preview"])

json_string = json.dumps(bdi_data, indent=2)

with tab1:
    st.markdown("Modifica il JSON qui sotto:")
    edited_json = st.text_area(
        "Modifica il JSON",
        value=json_string,
        height=500,
        key="json_editor",
        label_visibility="collapsed"
    )

with tab2:
    st.markdown("Preview del JSON con numeri di riga:")
    # Mostra JSON con numeri di riga usando st.code
    try:
        # Tenta di formattare il JSON corrente dall'editor
        formatted_json = json.dumps(json.loads(edited_json), indent=2)
        st.code(formatted_json, language="json", line_numbers=True)
    except json.JSONDecodeError:
        # Se il JSON non è valido, mostra comunque con numeri di riga
        st.code(edited_json, language="json", line_numbers=True)
        st.error("⚠️ JSON non valido - mostrando preview del testo corrente")

col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    if st.button("💾 Salva Modifiche", use_container_width=True, type="primary"):
        try:
            new_data = json.loads(edited_json)
            save_bdi_data(new_data)
            st.success("✅ Dati BDI salvati con successo!")
        except json.JSONDecodeError:
            st.error("❌ Errore: Il JSON non è valido.")

with col2:
    if st.button("✔️ Valida JSON", use_container_width=True):
        try:
            json.loads(edited_json)
            st.success("✅ Il JSON è valido!")
        except json.JSONDecodeError as e:
            st.error(f"❌ Errore di validazione JSON: {e}")

st.divider()
st.markdown("💡 **Suggerimento**: Dopo aver validato il JSON, puoi procedere con i moduli successivi come Cuma e Genius.")

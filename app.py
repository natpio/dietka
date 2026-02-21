import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="BioTracker Pro", page_icon="⚖️", layout="wide")

# --- CUSTOM CSS (Design) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #2E7D32; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2E7D32; color: white; }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0") # ttl=0 wymusza odświeżenie danych przy każdym przeładowaniu

df = load_data()
df['Data'] = pd.to_datetime(df['Data'])

# --- SIDEBAR (Wprowadzanie danych) ---
with st.sidebar:
    st.header("➕ Nowy pomiar")
    with st.form("add_entry", clear_on_submit=True):
        date = st.date_input("Data", datetime.now())
        weight = st.number_input("Waga (kg)", min_value=40.0, max_value=200.0, step=0.1)
        dose = st.selectbox("Dawka (mg)", [0.25, 0.5, 1.0, 1.5, 2.0])
        mood = st.slider("Samopoczucie", 1, 5, 3)
        note = st.text_area("Notatki")
        submit = st.form_submit_button("Zapisz w dzienniku")

    if submit:
        # Tutaj logika dopisywania do Google Sheets
        new_data = pd.DataFrame([{"Data": date, "Waga": weight, "Dawka": dose, "Samopoczucie": mood, "Notatki": note}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(data=updated_df)
        st.success("Dane zapisane!")
        st.rerun()

# --- GŁÓWNY DASHBOARD ---
st.title("🛡️ BioTracker: Kuracja GLP-1")

# Sekcja Metryk
col1, col2, col3, col4 = st.columns(4)
if not df.empty:
    current_w = df['Waga'].iloc[-1]
    start_w = df['Waga'].iloc[0]
    diff = current_w - start_w
    
    col1.metric("Waga aktualna", f"{current_w} kg", f"{diff:.1f} kg", delta_color="inverse")
    col2.metric("Ostatnia dawka", f"{df['Dawka'].iloc[-1]} mg")
    col3.metric("Dni kuracji", (datetime.now() - df['Data'].iloc[0]).days)
    col4.metric("Cel (przykład)", "85 kg", f"{current_w - 85:.1f} kg do celu")

st.divider()

# Sekcja Wykresów
tab1, tab2 = st.tabs(["📈 Analiza Trendu", "🗓️ Historia Wpisów"])

with tab1:
    if not df.empty:
        # Wykres Wagi (Plotly)
        fig = px.line(df, x="Data", y="Waga", title="Postęp redukcji wagi",
                      markers=True, line_shape="spline", color_discrete_sequence=["#2E7D32"])
        fig.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        # Wykres słupkowy Dawka vs Samopoczucie
        fig2 = px.bar(df, x="Data", y="Dawka", color="Samopoczucie", 
                      title="Dawkowanie a samopoczucie",
                      color_continuous_scale=px.colors.sequential.Greens)
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)

# Pasek postępu do celu
if not df.empty:
    progress = 0.4 # Tu możesz wyliczyć dynamicznie: (start-obecna)/(start-cel)
    st.write("### Postęp do celu sylwetkowego")
    st.progress(progress)

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="LUMINA Wellness", layout="wide")

# --- ZEN CLINIC CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;600&display=swap');

    /* Tło i baza */
    .stApp {
        background: linear-gradient(180deg, #fdfbf7 0%, #f5f0e6 100%);
        color: #4a4a4a;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówki - Elegancki Szeryf */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #2c3e50 !important;
        font-weight: 400 !important;
    }

    /* Karty Metryk */
    div[data-testid="stMetric"] {
        background: white !important;
        border: 1px solid #e9e0d2 !important;
        border-radius: 2px !important; /* Kwadratowy, klasyczny look */
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }

    /* Przyciski */
    .stButton>button {
        background-color: #2c3e50 !important;
        color: #fdfbf7 !important;
        border-radius: 0px !important;
        border: none !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 12px;
        padding: 15px 30px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background-color: #d4af37 !important; /* Gold on hover */
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9e0d2;
    }

    /* Dataframe i Tabele */
    .stDataFrame {
        border: 1px solid #e9e0d2;
    }
    
    /* Ukrycie logo Streamlit */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- HEADER ---
st.markdown("<p style='text-align: center; letter-spacing: 6px; color: #bca07e; font-size: 14px;'>EST. 2024</p>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 3.5rem; margin-top: -20px;'>Lumina Wellness</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #7f8c8d;'>Personalizowany protokół zdrowia: Piotr & Natalia</p>", unsafe_allow_html=True)
st.divider()

# --- NAVIGATION & INPUT ---
with st.sidebar:
    st.markdown("### PANEL KLIENTA")
    user = st.radio("Zalogowany profil:", ["Piotr", "Natalia"])
    st.divider()
    
    with st.expander("DODAJ NOWY POMIAR", expanded=False):
        with st.form("entry_form"):
            d = st.date_input("Data wizyty", datetime.now())
            w = st.number_input("Masa ciała (kg)", min_value=40.0, step=0.1)
            ds = st.selectbox("Dawka leku (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            mood = st.slider("Samopoczucie", 1, 10, 8)
            note = st.text_input("Notatki / Uwagi")
            if st.form_submit_button("ZAPISZ WPIS"):
                new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Dawka": ds, "Samopoczucie": mood, "Notatki": note}])
                conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
                st.rerun()

# --- ANALIZA ---
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # Metryki
    c1, c2, c3 = st.columns(3)
    curr = df_u['Waga'].iloc[-1]
    diff = curr - df_u['Waga'].iloc[0]
    
    c1.metric("BIEŻĄCA MASA", f"{curr} kg", f"{diff:.1f} kg", delta_color="inverse")
    c2.metric("OSTATNIA DAWKA", f"{df_u['Dawka'].iloc[-1]} mg")
    c3.metric("DNI PROTOKOŁU", (datetime.now().date() - df_u['Data'].iloc[0]).days)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Główny wykres
    st.markdown("### Historia Transformacji")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Waga'],
        mode='lines+markers',
        line=dict(color='#2c3e50', width=1),
        marker=dict(size=8, color='#d4af37'),
        name='Waga'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, linecolor='#e9e0d2'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', linecolor='#e9e0d2'),
        font=dict(family="Inter", size=12)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Porównanie i Historia
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### Ostatnie logi")
        st.dataframe(df_u.tail(5), use_container_width=True)
    with col_r:
        st.markdown("### Wspólna progresja")
        fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik",
                          color_discrete_map={"Piotr": "#2c3e50", "Natalia": "#d4af37"})
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.info("Oczekiwanie na pierwszą synchronizację danych...")

st.markdown("<br><hr><p style='text-align: center; color: #95a5a6; font-size: 12px;'>LUMINA HEALTH CARE | DISCRETION & PROGRESS</p>", unsafe_allow_html=True)

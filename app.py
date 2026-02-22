import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="BioRitual Premium", layout="centered", page_icon="🍃")

# --- ADVANCED VISUAL OVERHAUL (AURORA & GLASS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400;600&display=swap');

    /* Dynamiczne tło Aurora */
    .stApp {
        background-color: #f8f9fa;
        background-image: 
            radial-gradient(at 0% 0%, rgba(122, 139, 132, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(212, 175, 55, 0.1) 0px, transparent 50%);
        font-family: 'Inter', sans-serif;
    }

    /* Grafika dekoracyjna w nagłówku */
    .header-icon {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 80px;
        opacity: 0.8;
        filter: sepia(0.5) hue-rotate(90deg);
    }

    /* Szklane metryki */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 30px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }

    /* Hero Weight - Jeszcze bardziej elegancki */
    .hero-weight {
        font-size: 9rem;
        font-weight: 200;
        letter-spacing: -6px;
        text-align: center;
        color: #2c3e50;
        margin-top: -20px;
    }

    /* Przycisk akcji z efektem blur */
    .stButton>button {
        background: rgba(44, 62, 80, 0.9) !important;
        backdrop-filter: blur(5px);
        color: white !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        border: none !important;
        font-weight: 400 !important;
        letter-spacing: 2px !important;
        transition: 0.5s;
    }
    
    .stButton>button:hover {
        background: #d4af37 !important;
        transform: translateY(-2px);
    }

    /* Customizacja Expanderów */
    .stExpander {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 20px !important;
    }

    /* Ukrycie elementów technicznych */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- HEADER SECTION ---
# Dodajemy grafikę wektorową (ikona liścia/zdrowia)
st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/2913/2913520.png" class="header-icon">', unsafe_allow_html=True)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")

df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

# --- HERO ---
if not df_u.empty:
    curr_w = df_u['Waga'].iloc[-1]
    st.markdown(f"<div class='hero-weight'>{curr_w:.1f}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:8px; color:#95a5a6; margin-top:-30px; margin-bottom:40px;'>KILOGRAMÓW</p>", unsafe_allow_html=True)

    # Metryki w układzie horyzontalnym
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("CIŚNIENIE", f"{int(df_u['Cisnienie_S'].iloc[-1])}/{int(df_u['Cisnienie_D'].iloc[-1])}" if not pd.isna(df_u['Cisnienie_S'].iloc[-1]) else "--")
    with c2:
        st.metric("PROTOKÓŁ", f"{df_u['Dawka'].iloc[-1]} mg")
    with c3:
        diff = curr_w - df_u['Waga'].iloc[0]
        st.metric("ZMIANA", f"{diff:.1f} kg", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# --- WYKRES (SUBTELNY) ---
if not df_u.empty:
    # Wykres z gradientem pod linią
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Waga'],
        mode='lines',
        line=dict(color='#2c3e50', width=3),
        fill='tozeroy',
        fillcolor='rgba(44, 62, 80, 0.03)'
    ))
    fig.update_layout(
        height=300, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='#bdc3c7'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', side='right')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- AKCJE ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("✨ REJESTRACJA NOWYCH DANYCH"):
    with st.form("entry_form", clear_on_submit=True):
        col_x, col_y = st.columns(2)
        d = col_x.date_input("Dzień", datetime.now())
        w = col_y.number_input("Waga", step=0.1)
        
        col_z1, col_z2 = st.columns(2)
        sys = col_z1.number_input("SYS", value=120)
        dia = col_z2.number_input("DIA", value=80)
        
        dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        note = st.text_input("Krótka notatka (opcjonalnie)")
        
        if st.form_submit_button("ZAAKCEPTUJ"):
            new_data = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys, "Cisnienie_D": dia, "Dawka": dose, "Samopoczucie": 8, "Notatki": note}])
            conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
            st.toast("Dane zsynchronizowane")
            st.rerun()

with st.expander("📖 HISTORIA PROTOKOŁU"):
    st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown(f"<p style='text-align: center; color: #bdc3c7; font-size: 11px; margin-top: 50px; letter-spacing: 2px;'>AETERNA BIOMEDICAL | {user.upper()} SESSION</p>", unsafe_allow_html=True)

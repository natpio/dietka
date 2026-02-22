import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Lumina Vital Monitor", layout="wide")

# --- STYLE CSS (DARK MEDICAL UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;400;600&family=JetBrains+Mono&display=swap');

    .stApp {
        background-color: #0a0c10;
        color: #e6edf3;
        font-family: 'Outfit', sans-serif;
    }

    /* Karta parametrów */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }

    /* Animacja pulsu tętna */
    .pulse-dot {
        height: 10px; width: 10px;
        background-color: #ff3e3e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #ff3e3e;
        animation: pulse 1s infinite;
        margin-right: 10px;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.5); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }

    h1 { font-family: 'JetBrains Mono', monospace; font-weight: 100; color: #00d4ff; text-align: center; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    # Konwersja 3 parametrów + reszta
    cols = ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']
    for c in cols:
        if c in df_all.columns:
            df_all[c] = pd.to_numeric(df_all[c], errors='coerce')

# --- HEADER ---
st.markdown("<h1><span class='pulse-dot'></span>Vital intelligence</h1>", unsafe_allow_html=True)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- METRYKI ---
    m1, m2, m3, m4 = st.columns(4)
    last = df_u.iloc[-1]
    
    m1.metric("WAGA", f"{last['Waga']:.1f} kg")
    m2.metric("CIŚNIENIE", f"{int(last['Cisnienie_S'])}/{int(last['Cisnienie_D'])}")
    m3.metric("TĘTNO (BPM)", f"{int(last['Tetno'])}" if not pd.isna(last['Tetno']) else "--")
    m4.metric("DAWKA", f"{last['Dawka']} mg")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- WYKRES "TRI-METRIC MONITOR" ---
    fig = go.Figure()

    # 1. Skurczowe (Górna granica)
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Cisnienie_S'],
        name="Skurczowe (SYS)",
        line=dict(color='#00d4ff', width=3, shape='spline'),
        mode='lines+markers'
    ))

    # 2. Rozkurczowe (Dolna granica)
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Cisnienie_D'],
        name="Rozkurczowe (DIA)",
        line=dict(color='#00ff88', width=2, shape='spline'),
        mode='lines+markers'
    ))

    # 3. Tętno (Jako słupki w tle lub kropki)
    fig.add_trace(go.Bar(
        x=df_u['Data'], y=df_u['Tetno'],
        name="Tętno (BPM)",
        marker_color='rgba(255, 62, 62, 0.2)',
        width=80000000 # dostosowanie szerokości słupków do daty
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=500, margin=dict(l=0,r=0,t=20,b=0),
        legend=dict(orientation="h", y=1.1, x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Wartości Biometryczne")
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- INPUT ---
st.markdown("<br>", unsafe_allow_html=True)
col_l, col_r = st.columns(2)

with col_l:
    with st.popover("➕ NOWY POMIAR", use_container_width=True):
        with st.form("vital_form"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1)
            c1, c2, c3 = st.columns(3)
            s = c1.number_input("SYS", value=120)
            di = c2.number_input("DIA", value=80)
            t = c3.number_input("Tętno", value=70)
            ds = st.selectbox("Dawka", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s, "Cisnienie_D": di, "Tetno": t, "Dawka": ds}])
                conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
                st.rerun()

with col_r:
    with st.popover("📑 LOGI", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

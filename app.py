import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="AETERNA PRO", layout="wide", initial_sidebar_state="expanded")

# --- ULTRA-LUX CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@200;400;600&family=Bodoni+Moda:ital,wght@0,400;1,400&display=swap');

    /* Tło i baza */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1e2632 0%, #0a0c10 100%);
        color: #d1d5db;
        font-family: 'Montserrat', sans-serif;
    }

    /* Nagłówki - High Fashion Style */
    h1 {
        font-family: 'Bodoni Moda', serif !important;
        background: linear-gradient(135deg, #f3e5f5 0%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem !important;
        letter-spacing: -2px;
        font-style: italic;
        text-align: center;
        margin-bottom: 0 !important;
    }

    /* Karty metryk (Glassmorphism Premium) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        border-radius: 24px !important;
        padding: 25px !important;
        backdrop-filter: blur(20px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4) !important;
        transition: all 0.4s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #d4af37 !important;
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05) !important;
    }

    /* Sidebar - Elegancka czerń */
    [data-testid="stSidebar"] {
        background-color: #050608 !important;
        border-right: 1px solid rgba(212, 175, 55, 0.1);
    }

    /* Przyciski - Złoty metalik */
    .stButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #b8860b 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 40px !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2) !important;
        transition: 0.3s !important;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.5) !important;
        transform: scale(1.02);
    }

    /* Inputy */
    .stTextInput, .stNumberInput, .stSelectbox {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Wykresy - Czystość */
    .js-plotly-plot {
        border-radius: 24px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- SIDEBAR & LOGGING ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; font-family:Bodoni Moda; color:#d4af37; font-size:2rem;'>AETERNA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:10px; letter-spacing:3px;'>PROTOCOL MANAGER</p>", unsafe_allow_html=True)
    st.divider()
    
    user = st.radio("SELECT OPERATOR", ["Piotr", "Natalia"])
    
    st.markdown("### DATA SYNCHRONIZATION")
    with st.form("entry_lux"):
        d = st.date_input("CYCLE DATE", datetime.now())
        w = st.number_input("BODY MASS (KG)", min_value=40.0, step=0.1)
        
        st.markdown("**BLOOD PRESSURE**")
        c1, c2 = st.columns(2)
        sys = c1.number_input("SYS", value=120)
        dia = c2.number_input("DIA", value=80)
        
        ds = st.selectbox("PROTOCOL LEVEL (MG)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("BIO-STATUS", 1, 10, 8)
        note = st.text_area("CLINICAL NOTES")
        
        if st.form_submit_button("AUTHORIZE ENTRY"):
            new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys, "Cisnienie_D": dia, "Dawka": ds, "Samopoczucie": mood, "Notatki": note}])
            conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
            st.rerun()

# --- MAIN INTERFACE ---
st.markdown("<h1>Aeterna Protocol</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; letter-spacing:10px; color:#d4af37; margin-bottom:50px;'>LIVE BIOMETRICS: {user.upper()}</p>", unsafe_allow_html=True)

df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # Metryki
    m1, m2, m3, m4 = st.columns(4)
    curr_w = df_u['Waga'].iloc[-1]
    diff_w = curr_w - df_u['Waga'].iloc[0]
    
    try:
        sys_v = int(df_u['Cisnienie_S'].dropna().iloc[-1])
        dia_v = int(df_u['Cisnienie_D'].dropna().iloc[-1])
        bp_label = f"{sys_v}/{dia_v}"
    except:
        bp_label = "PENDING"

    m1.metric("CURRENT MASS", f"{curr_w} KG", f"{diff_w:.1f} KG", delta_color="inverse")
    m2.metric("HEART RATE STATUS", bp_label)
    m3.metric("DOSAGE LEVEL", f"{df_u['Dawka'].iloc[-1]} MG")
    m4.metric("CYCLE PROGRESS", f"{len(df_u)} DAYS")

    st.markdown("<br>", unsafe_allow_html=True)

    # Wykresy Premium
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown("<p style='color:#d4af37; letter-spacing:2px;'>WEIGHT TRAJECTORY</p>", unsafe_allow_html=True)
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], fill='tozeroy', 
                                   line=dict(color='#d4af37', width=1),
                                   fillcolor='rgba(212, 175, 55, 0.05)'))
        fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color='#888'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1a1a1a'))
        st.plotly_chart(fig_w, use_container_width=True)

    with col_r:
        st.markdown("<p style='color:#d4af37; letter-spacing:2px;'>VITAL ANALYTICS</p>", unsafe_allow_html=True)
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#fff', width=1)))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#d4af37', width=1)))
        fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color='#888'), legend=dict(orientation="h", y=1.1, x=1))
        st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#d4af37; letter-spacing:2px;'>PROTOCOL HISTORY</p>", unsafe_allow_html=True)
    st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

else:
    st.markdown("<h3 style='text-align:center; color:#444;'>AWAITING INITIAL CALIBRATION...</h3>", unsafe_allow_html=True)

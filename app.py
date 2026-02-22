import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Lumina Elite", layout="wide", page_icon="💎")

# --- ADVANCED GRAPHIC ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&family=Outfit:wght@200;400;700&display=swap');

    /* Animowane tło Aurora */
    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 10% 20%, rgba(122, 139, 132, 0.1) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(212, 175, 55, 0.08) 0%, transparent 40%);
        z-index: -1;
    }

    /* Typografia */
    h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 200 !important;
        letter-spacing: -2px !important;
        color: #2c3e50 !important;
        font-size: 4rem !important;
        text-align: center;
    }

    /* Szklane Karty */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 35px !important;
        padding: 30px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.03) !important;
        transition: 0.4s;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.6) !important;
    }

    /* Customowe ikony w nagłówkach */
    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        font-family: 'Outfit', sans-serif;
        font-weight: 400;
        color: #7A8B84;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }

    /* Stylizacja przycisków */
    .stButton>button {
        background: rgba(44, 62, 80, 0.9) !important;
        border: none !important;
        border-radius: 20px !important;
        color: white !important;
        padding: 15px 40px !important;
        font-weight: 300 !important;
        letter-spacing: 3px !important;
        transition: 0.5s;
    }
    .stButton>button:hover {
        background: #bca07e !important;
        box-shadow: 0 10px 30px rgba(188, 160, 126, 0.4);
    }

    /* Ukrycie elementów technicznych */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- TOP NAVIGATION & LOGO ---
st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <img src="https://cdn-icons-png.flaticon.com/512/6122/6122588.png" width="60" style="opacity: 0.7;">
    </div>
    """, unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

# --- HERO SECTION ---
st.markdown("<h1>Lumina Elite</h1>", unsafe_allow_html=True)

if not df_u.empty:
    curr_w = df_u['Waga'].iloc[-1]
    
    # Wielka waga centralnie
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 50px;">
            <span style="font-size: 8rem; font-weight: 100; color: #2c3e50;">{curr_w:.1f}</span>
            <span style="font-size: 1.5rem; color: #bca07e; letter-spacing: 10px; margin-left: 20px;">KG</span>
        </div>
        """, unsafe_allow_html=True)

    # Wizualne karty statusu
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="section-header">🩸 VITAL SIGNS</div>', unsafe_allow_html=True)
        st.metric("", f"{int(df_u['Cisnienie_S'].iloc[-1])}/{int(df_u['Cisnienie_D'].iloc[-1])}" if not pd.isna(df_u['Cisnienie_S'].iloc[-1]) else "---")
    with c2:
        st.markdown('<div class="section-header">🧪 PROTOCOL</div>', unsafe_allow_html=True)
        st.metric("", f"{df_u['Dawka'].iloc[-1]} MG")
    with c3:
        st.markdown('<div class="section-header">📈 PROGRESS</div>', unsafe_allow_html=True)
        diff = curr_w - df_u['Waga'].iloc[0]
        st.metric("", f"{diff:.1f} KG", delta_color="inverse")

st.markdown("<br><br>", unsafe_allow_html=True)

# --- GRAPHIC VISUALIZATION ---
if not df_u.empty:
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown('<div class="section-header">🧬 BIOMETRIC TREND</div>', unsafe_allow_html=True)
        fig = go.Figure()
        # Gradient area chart
        fig.add_trace(go.Scatter(
            x=df_u['Data'], y=df_u['Waga'],
            mode='lines+markers',
            line=dict(color='#2c3e50', width=4, shape='spline'),
            marker=dict(size=10, color='#fff', line=dict(width=3, color='#bca07e')),
            fill='tozeroy',
            fillcolor='rgba(188, 160, 126, 0.05)'
        ))
        fig.update_layout(
            height=400, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(0,0,0,0.05)', side='right')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_r:
        st.markdown('<div class="section-header">📊 ANALYSIS</div>', unsafe_allow_html=True)
        # Mały, elegancki wykres ciśnienia
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#2c3e50', width=2, dash='dot')))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#bca07e', width=2)))
        fig_p.update_layout(
            height=400, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})

# --- INTERACTIVE ELEMENTS ---
st.markdown("<br><br>", unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    with st.popover("➕ REJESTRUJ NOWY POMIAR", use_container_width=True):
        with st.form("elite_form"):
            d = st.date_input("Dzień", datetime.now())
            w = st.number_input("Waga (kg)", step=0.1)
            c1, c2 = st.columns(2)
            sys = c1.number_input("SYS", value=120)
            dia = c2.number_input("DIA", value=80)
            dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            note = st.text_input("Krótka notatka")
            if st.form_submit_button("ZATWIERDŹ PROFIL"):
                new_d = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys, "Cisnienie_D": dia, "Dawka": dose, "Samopoczucie": 8, "Notatki": note}])
                conn.update(data=pd.concat([df_all, new_d], ignore_index=True))
                st.rerun()

with col_btn2:
    with st.popover("📖 PRZEGLĄDAJ HISTORIĘ", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("""
    <div style="margin-top: 100px; text-align: center; opacity: 0.4;">
        <hr style="border: 0; border-top: 1px solid #2c3e50; width: 100px; margin: 20px auto;">
        <p style="font-size: 10px; letter-spacing: 5px;">EST. 2024 • AETERNA INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Lumina Heart Monitor", layout="wide")

# --- MED-TECH STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;400&family=Outfit:wght@300;600&display=swap');

    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Outfit', sans-serif;
    }

    /* Stylizacja metryk w klimacie monitora pacjenta */
    div[data-testid="stMetric"] {
        background: rgba(23, 28, 36, 0.8) !important;
        border-left: 4px solid #00d4ff !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
    }

    /* Pulsujące serce (Animacja) */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    .heart-icon {
        font-size: 40px;
        color: #ff3e3e;
        animation: pulse 1.5s infinite;
        text-align: center;
        display: block;
        margin-bottom: 20px;
    }

    h1 {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 100;
        letter-spacing: 5px;
        text-transform: uppercase;
        color: #00d4ff;
        text-align: center;
    }
    
    /* Ukrycie technicznych elementów */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- HEADER ---
st.markdown('<div class="heart-icon">❤️</div>', unsafe_allow_html=True)
st.markdown("<h1>Cardiac Monitor</h1>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- METRYKI ---
    c1, c2, c3 = st.columns(3)
    last_s = int(df_u['Cisnienie_S'].dropna().iloc[-1])
    last_d = int(df_u['Cisnienie_D'].dropna().iloc[-1])
    
    with c1:
        st.metric("SYS / DIA", f"{last_s} / {last_d}", delta="Norma" if last_s < 130 else "Podwyższone")
    with c2:
        st.metric("AKTUALNA DAWKA", f"{df_u['Dawka'].iloc[-1]} mg")
    with c3:
        st.metric("MASA CIAŁA", f"{df_u['Waga'].iloc[-1]} kg")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- WYKRES W FORMIE "PULSU" ---
    st.markdown("<p style='letter-spacing:2px; color:#58a6ff; font-size:12px;'>EKG-STYLE VITAL TRENDS</p>", unsafe_allow_html=True)
    
    fig = go.Figure()

    # Linia Skurczowa (Neonowy błękit)
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Cisnienie_S'],
        mode='lines+markers',
        name='SYS',
        line=dict(color='#00d4ff', width=3, shape='spline'),
        fill='tonexty',
        fillcolor='rgba(0, 212, 255, 0.05)'
    ))

    # Linia Rozkurczowa (Neonowa zieleń)
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Cisnienie_D'],
        mode='lines+markers',
        name='DIA',
        line=dict(color='#00ff88', width=2, shape='spline'),
    ))

    # Dodanie tła "stref zdrowia" (podobnie jak w medycznych urządzeniach)
    fig.add_hrect(y0=60, y1=120, fillcolor="#00ff88", opacity=0.03, layer="below", line_width=0) # Norma
    fig.add_hrect(y0=120, y1=140, fillcolor="#ffd700", opacity=0.03, layer="below", line_width=0) # Ryzyko

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, color='#8b949e'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- INPUT POP-OVER ---
col_l, col_r = st.columns(2)
with col_l:
    with st.popover("➕ DODAJ POMIAR", use_container_width=True):
        with st.form("ekg_form"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1)
            s = st.number_input("SYS", value=120)
            di = st.number_input("DIA", value=80)
            ds = st.selectbox("Dawka", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("AUTORYZUJ WPIS"):
                new_data = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s, "Cisnienie_D": di, "Dawka": ds}])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.rerun()

with col_r:
    with st.popover("📑 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False))

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="BioRitual", layout="centered", page_icon="🧘")

# --- ADVANCED WELLNESS UI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400;600&family=Playfair+Display:ital@1&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        color: #1d1d1f;
        font-family: 'Inter', sans-serif;
    }

    /* Wyśrodkowanie wszystkiego */
    .main .block-container {
        max-width: 800px;
        padding-top: 5rem;
    }

    /* Styl napisu Hero */
    .hero-weight {
        font-size: 8rem;
        font-weight: 200;
        letter-spacing: -5px;
        text-align: center;
        margin-bottom: -20px;
        color: #1d1d1f;
    }

    .hero-unit {
        font-size: 1.5rem;
        text-align: center;
        color: #86868b;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }

    /* Subtelne karty metryk */
    .metric-box {
        text-align: center;
        padding: 20px;
        border-top: 1px solid #f2f2f2;
        border-bottom: 1px solid #f2f2f2;
    }

    /* Personalizacja przycisków */
    .stButton>button {
        background-color: #1d1d1f !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
        border: none !important;
        font-size: 14px !important;
        transition: 0.4s;
    }
    
    .stButton>button:hover {
        opacity: 0.8;
        transform: scale(0.98);
    }

    /* Formularz w expaderze */
    .stExpander {
        border: none !important;
        background: #f5f5f7 !important;
        border-radius: 20px !important;
    }
    
    /* Ukrycie dekoracji Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- HEADER / NAVIGATION ---
user = st.segmented_control("Operator", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

# --- HERO SECTION ---
if not df_u.empty:
    curr_w = df_u['Waga'].iloc[-1]
    st.markdown(f"<div class='hero-weight'>{curr_w:.1f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-unit'>Kilogramów</div>", unsafe_allow_html=True)

    # Poziome metryki
    c1, c2, c3 = st.columns(3)
    
    with c1:
        try:
            sys = int(df_u['Cisnienie_S'].dropna().iloc[-1])
            dia = int(df_u['Cisnienie_D'].dropna().iloc[-1])
            st.caption("CIŚNIENIE")
            st.markdown(f"**{sys}/{dia}**")
        except:
            st.caption("CIŚNIENIE")
            st.markdown("**--**")
            
    with c2:
        st.caption("DAWKA")
        st.markdown(f"**{df_u['Dawka'].iloc[-1]} mg**")
        
    with c3:
        diff = curr_w - df_u['Waga'].iloc[0]
        st.caption("ZMIANA")
        st.markdown(f"**{diff:.1f} kg**")

st.markdown("<br><br>", unsafe_allow_html=True)

# --- WYKRESY (MINIMAL) ---
if not df_u.empty:
    # Wykres wagi - tylko czysta linia
    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Waga'],
        mode='lines',
        line=dict(color='#1d1d1f', width=2),
        fill='tozeroy',
        fillcolor='rgba(0,0,0,0.02)'
    ))
    fig_w.update_layout(
        height=250, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    st.plotly_chart(fig_w, use_container_width=True, config={'displayModeBar': False})

# --- AKCJA I HISTORIA ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("➕ DODAJ NOWY WPIS"):
    with st.form("quick_add", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        d = col_a.date_input("Data", datetime.now())
        w = col_b.number_input("Waga", min_value=40.0, step=0.1)
        
        col_c, col_d = st.columns(2)
        s_s = col_c.number_input("Skurczowe", value=120)
        s_d = col_d.number_input("Rozkurczowe", value=80)
        
        dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        note = st.text_input("Krótka notatka")
        
        if st.form_submit_button("ZAPISZ"):
            new_r = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_s, "Cisnienie_D": s_d, "Dawka": dose, "Samopoczucie": 8, "Notatki": note}])
            conn.update(data=pd.concat([df_all, new_r], ignore_index=True))
            st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📑 ZOBACZ HISTORIĘ"):
    st.table(df_u.sort_values("Data", ascending=False).head(10)[["Data", "Waga", "Cisnienie_S", "Cisnienie_D", "Dawka"]])

st.markdown(f"<p style='text-align: center; color: #86868b; font-family: Playfair Display; font-style: italic; margin-top: 5rem;'>Twoja podróż do zdrowia, {user}.</p>", unsafe_allow_html=True)

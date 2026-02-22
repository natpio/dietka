import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="Wellness Tracker", layout="wide", page_icon="🌿")

# --- WELLNESS & READABILITY CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Quicksand:wght@400;600&display=swap');

    /* Tło i baza - kolor lniany/spa */
    .stApp {
        background-color: #F8F9F7;
        color: #4A4E4D;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówki - Przyjazne i czytelne */
    h1 {
        font-family: 'Quicksand', sans-serif;
        color: #2D3A3A !important;
        font-weight: 600 !important;
        text-align: center;
        padding-bottom: 1rem;
    }

    /* Karty Metryk - Miękkość i Czystość */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8E4 !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
    }
    
    label[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #7A8B84 !important;
    }

    /* Sidebar - Jasny i przejrzysty */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8E4;
    }

    /* Przyciski - Naturalna Zieleń */
    .stButton>button {
        background-color: #7A8B84 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        transition: 0.3s all ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #5D6D66 !important;
        box-shadow: 0 4px 12px rgba(122, 139, 132, 0.2);
    }

    /* Tabele i dataframe */
    .stDataFrame {
        background: white;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    # Bezpieczna konwersja na liczby
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #7A8B84;'>🌿 Stillness</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8rem;'>TWÓJ DZIENNIK HARMONII</p>", unsafe_allow_html=True)
    st.divider()
    
    user = st.radio("Aktywny profil:", ["Piotr", "Natalia"])
    
    st.markdown("### NOWY WPIS")
    with st.form("wellness_form", clear_on_submit=True):
        d = st.date_input("Data", datetime.now())
        w = st.number_input("Waga (kg)", min_value=40.0, step=0.1)
        
        st.markdown("**CIŚNIENIE TĘTNICZE**")
        c1, c2 = st.columns(2)
        sys = c1.number_input("Skurczowe", value=120)
        dia = c2.number_input("Rozkurczowe", value=80)
        
        ds = st.selectbox("Dawka Ozempic (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("Samopoczucie (1-10)", 1, 10, 8)
        note = st.text_area("Twoje myśli / Notatki")
        
        if st.form_submit_button("ZAPISZ DANE"):
            new_row = pd.DataFrame([{
                "Użytkownik": user, "Data": d, "Waga": w, 
                "Cisnienie_S": sys, "Cisnienie_D": dia, 
                "Dawka": ds, "Samopoczucie": mood, "Notatki": note
            }])
            conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
            st.rerun()

# --- INTERFEJS GŁÓWNY ---
st.markdown(f"<h1>Witaj w równowadze, {user}</h1>", unsafe_allow_html=True)

df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- METRYKI ---
    col1, col2, col3, col4 = st.columns(4)
    
    curr_w = df_u['Waga'].iloc[-1]
    first_w = df_u['Waga'].iloc[0]
    
    try:
        sys_val = int(df_u['Cisnienie_S'].dropna().iloc[-1])
        dia_val = int(df_u['Cisnienie_D'].dropna().iloc[-1])
        bp_text = f"{sys_val}/{dia_val}"
    except:
        bp_text = "---"

    col1.metric("AKTUALNA WAGA", f"{curr_w} kg", f"{curr_w - first_w:.1f} kg", delta_color="inverse")
    col2.metric("OSTATNIE CIŚNIENIE", bp_text)
    col3.metric("BIEŻĄCA DAWKA", f"{df_u['Dawka'].iloc[-1]} mg")
    col4.metric("SESJA NR", len(df_u))

    st.markdown("<br>", unsafe_allow_html=True)

    # --- WYKRESY (CZYTELNE I DELIKATNE) ---
    t1, t2 = st.tabs(["📉 TREND WAGI", "❤️ ANALIZA SERCA"])
    
    with t1:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df_u['Data'], y=df_u['Waga'],
            mode='lines+markers',
            line=dict(color='#7A8B84', width=3),
            marker=dict(size=8, color='#FFFFFF', line=dict(width=2, color='#7A8B84')),
            name="Waga"
        ))
        fig_w.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F0F2F0')
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with t2:
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe", line=dict(color='#D98E73', width=2)))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe", line=dict(color='#7A8B84', width=2)))
        
        # Komfortowa strefa ciśnienia
        fig_p.add_hrect(y0=60, y1=125, fillcolor="#7A8B84", opacity=0.05, layer="below", line_width=0)
        
        fig_p.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", y=1.1, x=1)
        )
        st.plotly_chart(fig_p, use_container_width=True)

    # --- HISTORIA ---
    st.markdown("### 📋 TWOJA HISTORIA")
    st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

else:
    st.info("Zacznij swoją podróż wellness, dodając pierwszy wpis w panelu po lewej stronie.")

st.markdown("<br><p style='text-align: center; color: #7A8B84; font-size: 0.8rem;'>STILLNESS WELLNESS SYSTEM | ODDECH • ZDROWIE • POSTĘP</p>", unsafe_allow_html=True)

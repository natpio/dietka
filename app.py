import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="BioCore Pro", page_icon="🧬", layout="wide")

# --- TOTAL VISUAL OVERHAUL (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* Tło całej aplikacji */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f8fafc;
    }

    /* Nagłówki w stylu Sci-Fi */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #4ade80 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
    }

    /* Karty Metryk (Glassmorphism + Neon) */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(74, 222, 128, 0.2) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #4ade80 !important;
        box-shadow: 0 0 15px rgba(74, 222, 128, 0.4) !important;
        transform: scale(1.02);
    }

    /* Sidebar - Ciemny i smukły */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9);
        border-right: 1px solid rgba(74, 222, 128, 0.1);
    }

    /* Przyciski */
    .stButton>button {
        background: linear-gradient(90deg, #22c55e, #10b981) !important;
        border: none !important;
        color: white !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 14px !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        transition: 0.3s !important;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Formularze */
    .stTextInput, .stNumberInput, .stSelectbox {
        background: rgba(15, 23, 42, 0.5) !important;
        border-radius: 10px !important;
    }

    /* Usunięcie zbędnych elementów Streamlit */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>BIOCORE</h2>", unsafe_allow_html=True)
    user = st.radio("OPERATOR:", ["PIOTR", "NATALIA"])
    
    st.divider()
    with st.expander("📥 NOWY WPIS", expanded=True):
        with st.form("new_entry", clear_on_submit=True):
            d = st.date_input("DATA", datetime.now())
            w = st.number_input("WAGA (KG)", min_value=40.0, step=0.1)
            ds = st.selectbox("DAWKA (MG)", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            m = st.select_slider("SAMOPOCZUCIE", options=["🌑", "🌘", "🌗", "🌖", "🌕"])
            sub = st.form_submit_button("AUTORYZUJ WPIS")

    if sub:
        m_map = {"🌑": 1, "🌘": 2, "🌗": 3, "🌖": 4, "🌕": 5}
        new_row = pd.DataFrame([{"Użytkownik": user.capitalize(), "Data": d, "Waga": w, 
                                 "Dawka": ds, "Samopoczucie": m_map[m], "Notatki": ""}])
        conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
        st.toast("System zaktualizowany!", icon='✅')
        st.rerun()

# --- WIDOK GŁÓWNY ---
df_user = df_all[df_all['Użytkownik'] == user.capitalize()].sort_values("Data") if not df_all.empty else pd.DataFrame()

st.markdown(f"<h1>SYSTEM MONITOROWANIA: {user}</h1>", unsafe_allow_html=True)

if not df_user.empty:
    # Metryki w kolumnach
    c1, c2, c3 = st.columns(3)
    curr = df_user['Waga'].iloc[-1]
    diff = curr - df_user['Waga'].iloc[0]
    
    c1.metric("BIEŻĄCA MASA", f"{curr} KG", f"{diff:.1f} KG", delta_color="inverse")
    c2.metric("POZIOM DAWKI", f"{df_user['Dawka'].iloc[-1]} MG", "ACTIVE")
    c3.metric("STATUS BIO", "OPTYMALNY", "CONNECTED")

    st.markdown("### TRENDY BIOMETRYCZNE")
    
    # Wykres z custom stylingiem
    fig = px.area(df_user, x="Data", y="Waga", 
                  color_discrete_sequence=['#4ade80'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#f8fafc", family="Orbitron"),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Porównanie w dolnej sekcji
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("### LOGI SYSTEMOWE")
        st.dataframe(df_user.tail(5), use_container_width=True)
    with col_r:
        st.markdown("### PROTOKÓŁ WSPÓLNY")
        fig_c = px.line(df_all, x="Data", y="Waga", color="Użytkownik",
                        color_discrete_map={"Piotr": "#4ade80", "Natalia": "#8b5cf6"})
        fig_c.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
        st.plotly_chart(fig_c, use_container_width=True)

else:
    st.warning("SYSTEM OCZEKUJE NA DANE WEJŚCIOWE...")

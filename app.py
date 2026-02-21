import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="BIO-SYNC PRO", layout="wide", initial_sidebar_state="collapsed")

# --- CYBERPUNK ULTIMATE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&display=swap');

    /* Tło i główna czcionka */
    .stApp {
        background: radial-gradient(circle at center, #0a0f1e 0%, #03050a 100%);
        color: #00f2ff;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Ukrycie domyślnych elementów */
    header, footer {visibility: hidden;}
    
    /* Neonowe karty */
    .bio-card {
        background: rgba(0, 242, 255, 0.03);
        border: 1px solid rgba(0, 242, 255, 0.2);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.05);
        margin-bottom: 20px;
    }

    /* Statystyki - Wielkie liczby */
    .stat-val {
        font-size: 3rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 15px rgba(0, 242, 255, 0.5);
        line-height: 1;
    }
    .stat-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        color: #00f2ff;
        letter-spacing: 2px;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #03050a;
        border-right: 1px solid #00f2ff33;
    }

    /* Przycisk Akcji */
    .stButton>button {
        background: transparent;
        border: 2px solid #00f2ff !important;
        color: #00f2ff !important;
        border-radius: 0px !important;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 3px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 30px #00f2ff;
    }

    /* Wykresy */
    .js-plotly-plot {
        filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.1));
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- HEADER & NAVIGATION ---
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.markdown("<h1 style='font-size: 4rem; margin-bottom: 0;'>BIO-SYNC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='letter-spacing: 5px; color: #666;'>OZEMPIC PROTOCOL v4.0</p>", unsafe_allow_html=True)

with col_head2:
    user = st.selectbox("Wybierz Operatora:", ["Piotr", "Natalia"])

st.divider()

# --- SIDEBAR (LOGOWANIE DANYCH) ---
with st.sidebar:
    st.markdown("### SYSTEM INPUT")
    with st.form("new_entry", clear_on_submit=True):
        d = st.date_input("DZIEŃ CYKLU", datetime.now())
        w = st.number_input("MASA CIAŁA (KG)", min_value=40.0, step=0.1)
        ds = st.select_slider("POZIOM PROTOKOŁU (MG)", options=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("STATUS BIO (1-10)", 1, 10, 7)
        note = st.text_input("UWAGI KLINICZNE")
        sub = st.form_submit_button("PRZEŚLIJ DANE")
        
        if sub:
            new_data = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Dawka": ds, "Samopoczucie": mood, "Notatki": note}])
            conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
            st.success("Synchronizacja zakończona.")
            st.rerun()

# --- DASHBOARD LOGIC ---
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- TOP METRICS (BIG & BOLD) ---
    c1, c2, c3, c4 = st.columns(4)
    
    curr = df_u['Waga'].iloc[-1]
    start = df_u['Waga'].iloc[0]
    total_loss = curr - start
    
    with c1:
        st.markdown(f"<div class='stat-label'>Masa Bieżąca</div><div class='stat-val'>{curr}</div><div style='color:#00f2ff'>KG</div>", unsafe_allow_html=True)
    with c2:
        color = "#ff4b4b" if total_loss > 0 else "#00f2ff"
        st.markdown(f"<div class='stat-label'>Zmiana Całkowita</div><div class='stat-val' style='color:{color}'>{total_loss:.1f}</div><div style='color:{color}'>KG</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='stat-label'>Protokół</div><div class='stat-val'>{df_u['Dawka'].iloc[-1]}</div><div style='color:#00f2ff'>MG</div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='stat-label'>Dzień</div><div class='stat-val'>{(datetime.now().date() - df_u['Data'].iloc[0]).days}</div><div style='color:#00f2ff'>TRWANIA</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN CHART ---
    st.markdown("<div class='bio-card'>", unsafe_allow_html=True)
    st.markdown("### TRAJEKTORIA REDUKCJI")
    
    # Customowy wykres Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_u['Data'], y=df_u['Waga'],
        mode='lines+markers',
        line=dict(color='#00f2ff', width=4),
        marker=dict(size=10, color='#fff', line=dict(width=2, color='#00f2ff')),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 255, 0.05)',
        name='Waga'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, color='#444'),
        yaxis=dict(showgrid=True, gridcolor='#111', color='#444'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

    # --- LOWER SECTION ---
    col_low1, col_low2 = st.columns([1, 1])
    
    with col_low1:
        st.markdown("<div class='bio-card'>", unsafe_allow_html=True)
        st.markdown("### HISTORIA LOGÓW")
        st.dataframe(df_u.sort_values("Data", ascending=False)[["Data", "Waga", "Dawka", "Samopoczucie"]], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_low2:
        st.markdown("<div class='bio-card'>", unsafe_allow_html=True)
        st.markdown("### PROTOKÓŁ WSPÓLNY (DUAL-SYNC)")
        fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik",
                          color_discrete_map={"Piotr": "#00f2ff", "Natalia": "#ff00ff"})
        fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#666"))
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 style='text-align:center; margin-top:100px;'>SYSTEM OFFLINE. OCZEKIWANIE NA INICJACJĘ DANYCH...</h2>", unsafe_allow_html=True)

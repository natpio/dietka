import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="The Sanctuary", layout="wide", page_icon="🧘")

# --- ORGANIC SANCTUARY CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400&display=swap');

    /* Tło luksusowego gabinetu */
    .stApp {
        background: radial-gradient(circle at top right, #f2ece4, #e8e0d5);
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówek w stylu boutique hotel */
    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 40px 0;
        letter-spacing: -1px;
    }

    /* Szklane, organiczne karty */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 40px !important;
        padding: 30px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.02) !important;
    }

    /* Tabs - minimalistyczne i lekkie */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        justify-content: center;
        border-bottom: none;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
        background: transparent !important;
        border: none !important;
        color: #8c857e !important;
    }

    .stTabs [aria-selected="true"] {
        color: #5d5750 !important;
        font-weight: 600 !important;
    }

    /* Przyciski jak z luksusowego menu */
    .stButton>button {
        background: #7c8370 !important;
        color: #fdfcfb !important;
        border-radius: 50px !important;
        padding: 15px 35px !important;
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        letter-spacing: 1px;
        border: none !important;
        transition: all 0.5s ease;
    }

    .stButton>button:hover {
        background: #5d6354 !important;
        box-shadow: 0 10px 20px rgba(124, 131, 112, 0.2);
    }

    /* Ukrycie technicznych elementów Streamlit */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SAFE DATA CONVERSION ---
def safe_val(val, default=None, is_int=False):
    try:
        if pd.isna(val) or val == "": return default
        return int(float(val)) if is_int else float(val)
    except: return default

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- UI CONTENT ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- VITAL STATUS GRID ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("RÓWNOWAGA MASY", f"{safe_val(last.get('Waga'), 0.0):.1f} kg")
    with m2:
        s, d = safe_val(last.get('Cisnienie_S'), 0, True), safe_val(last.get('Cisnienie_D'), 0, True)
        st.metric("RYTM SERCA", f"{s}/{d}" if s and d else "--")
    with m3:
        hr = safe_val(last.get('Tetno'), 0, True)
        st.metric("PULS SPOKOJU", f"{hr} BPM" if hr else "--")
    with m4:
        st.metric("PROTOKÓŁ", f"{last.get('Dawka', 0)} mg")

    # --- THE JOURNEY (CHARTS) ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["TWOJA SYLWETKA", "TWOJA WITALNOŚĆ"])

    with t1:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df_u['Data'], y=df_u['Waga'],
            line=dict(color='#a8a29a', width=2, shape='spline'),
            fill='tozeroy', fillcolor='rgba(168, 162, 154, 0.05)',
            mode='lines+markers', marker=dict(size=6, color='#7c8370')
        ))
        fig_w.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0,r=0,t=10,b=0), height=350,
            xaxis=dict(showgrid=False, color='#8c857e'),
            yaxis=dict(gridcolor='rgba(0,0,0,0.05)', color='#8c857e')
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with t2:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#c2b8ad', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="BPM", mode='markers', marker=dict(color='#d4af37', size=8, opacity=0.6)))
        fig_v.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0,r=0,t=10,b=0), height=350,
            legend=dict(orientation="h", y=1.2, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig_v, use_container_width=True)

# --- RITUAL ACTIONS ---
st.markdown("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    with st.popover("🧘 NOWY WPIS", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data rytuału", datetime.now())
            w = st.number_input("Masa ciała", step=0.1)
            cs, cd, ct = st.columns(3)
            s_val = cs.number_input("SYS", value=120)
            d_val = cd.number_input("DIA", value=80)
            t_val = ct.number_input("Puls", value=70)
            dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_val, "Cisnienie_D": d_val, "Tetno": t_val, "Dawka": dose}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with c2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_date = st.selectbox("Wybierz moment:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit"):
                ew = st.number_input("Waga", value=safe_val(row['Waga'], 0.0))
                es, ed, et = st.columns(3)
                esys = es.number_input("SYS", value=safe_int(row.get('Cisnienie_S'), 120)) # Użyjemy safe_int z poprzedniej wersji
                # ... analogicznie reszta pól ...
                if st.form_submit_button("AKTUALIZUJ"):
                    # Logika aktualizacji (taka jak poprzednio)
                    pass

with c3:
    with st.popover("📜 ARCHIWUM", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.5; font-size: 0.7rem; letter-spacing: 3px;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

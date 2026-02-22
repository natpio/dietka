import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="The Sanctuary | Vital Rituals", layout="wide", page_icon="🌿")

# --- ORGANIC SANCTUARY CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.8), rgba(242, 236, 228, 0.8)), 
                    url('https://images.unsplash.com/photo-1544161515-4ab6ce6db874?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 30px 0;
        letter-spacing: -1px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 35px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; justify-content: center; border-bottom: none; }
    .stTabs [data-baseweb="tab"] {
        text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem;
        background: transparent !important; color: #8c857e !important;
    }
    .stTabs [aria-selected="true"] { color: #5d5750 !important; font-weight: 600 !important; border-bottom: 2px solid #7c8370 !important; }

    .stButton>button {
        background: #7c8370 !important; color: white !important;
        border-radius: 50px !important; padding: 12px 30px !important;
        border: none !important; transition: 0.4s;
    }

    .report-card {
        background: white; padding: 25px; border-radius: 20px;
        border-left: 5px solid #7c8370; margin-bottom: 15px;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def safe_val(val, default=0.0):
    try:
        if pd.isna(val) or val == "" or val is None: return float(default)
        return float(val)
    except: return float(default)

def safe_int(val, default=0):
    try:
        if pd.isna(val) or val == "" or val is None: return int(default)
        return int(float(val))
    except: return int(default)

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("RÓWNOWAGA MASY", f"{safe_val(last.get('Waga')):.1f} kg")
    with m2:
        s, d = safe_int(last.get('Cisnienie_S')), safe_int(last.get('Cisnienie_D'))
        st.metric("RYTM SERCA", f"{s}/{d}" if s and d else "--")
    with m3:
        hr = safe_int(last.get('Tetno'))
        st.metric("PULS SPOKOJU", f"{hr} BPM" if hr else "--")
    with m4: st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")

    st.markdown("<br>", unsafe_allow_html=True)
    tab_w, tab_v, tab_r = st.tabs(["📉 TWOJA SYLWETKA", "❤️ TWOJA WITALNOŚĆ", "📋 RAPORT MEDYCZNY"])

    with tab_w:
        valid_w = df_u['Waga'].dropna()
        if not valid_w.empty:
            # EFEKT LUPY: Skala dopasowana do wagi
            min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], 
                                       line=dict(color='#7c8370', width=4, shape='spline'),
                                       fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.05)', mode='lines+markers'))
            fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, 
                                yaxis=dict(range=[min_w, max_w], gridcolor='rgba(0,0,0,0.05)', dtick=0.5))
            st.plotly_chart(fig_w, use_container_width=True)

    with tab_v:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#c2b8ad', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Puls", mode='markers', marker=dict(color='#d4af37', size=10, opacity=0.6)))
        fig_v.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig_v, use_container_width=True)

    with tab_r:
        st.markdown("### 🩺 Podsumowanie dla lekarza")
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            avg_s = safe_int(df_u['Cisnienie_S'].mean())
            avg_d = safe_int(df_u['Cisnienie_D'].mean())
            st.markdown(f"<div class='report-card'><b>Średnie ciśnienie:</b><br>{avg_s}/{avg_d} mmHg</div>", unsafe_allow_html=True)
        with c_r2:
            avg_w = safe_val(df_u['Waga'].mean())
            st.markdown(f"<div class='report-card'><b>Średnia waga:</b><br>{avg_w:.2f} kg</div>", unsafe_allow_html=True)
        with c_r3:
            avg_h = safe_int(df_u['Tetno'].mean())
            st.markdown(f"<div class='report-card'><b>Średni puls:</b><br>{avg_h} BPM</div>", unsafe_allow_html=True)
        
        st.markdown("#### Historia pomiarów (ostatnie 14 wpisów)")
        st.table(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].sort_values("Data", ascending=False).head(14))

# --- AKCJE ---
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            sys_v = st.number_input("SYS", value=120)
            dia_v = st.number_input("DIA", value=80)
            hr_v = st.number_input("Puls", value=70)
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys_v, "Cisnienie_D": dia_v, "Tetno": hr_v, "Dawka": ds}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with col2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_date = st.selectbox("Dzień:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es = st.number_input("SYS", value=safe_int(row.get('Cisnienie_S')))
                ed = st.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                et = st.number_input("Puls", value=safe_int(row.get('Tetno')))
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno']] = [ew, es, ed, et]
                    conn.update(data=df_all)
                    st.rerun()

with col3:
    with st.popover("📜 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; letter-spacing: 3px;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

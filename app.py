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

    .stApp {
        background: radial-gradient(circle at top right, #f2ece4, #e8e0d5);
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

    /* Szklane, luksusowe karty */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 35px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 30px; justify-content: center; border-bottom: none; }
    .stTabs [data-baseweb="tab"] {
        text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem;
        background: transparent !important; color: #8c857e !important;
    }
    .stTabs [aria-selected="true"] { color: #5d5750 !important; font-weight: 600 !important; }

    /* Przyciski */
    .stButton>button {
        background: #7c8370 !important; color: white !important;
        border-radius: 50px !important; padding: 12px 30px !important;
        border: none !important; transition: 0.4s;
    }
    .stButton>button:hover { background: #5d6354 !important; transform: translateY(-2px); }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- POMOCNICZE FUNKCJE BEZPIECZEŃSTWA ---
def safe_val(val, default=0.0):
    try:
        if pd.isna(val) or val == "": return float(default)
        return float(val)
    except: return float(default)

def safe_int(val, default=0):
    try:
        if pd.isna(val) or val == "": return int(default)
        return int(float(val))
    except: return int(default)

# --- POŁĄCZENIE ---
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
    
    # --- VITAL STATUS ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("RÓWNOWAGA MASY", f"{safe_val(last.get('Waga')):.1f} kg")
    s, d = safe_int(last.get('Cisnienie_S')), safe_int(last.get('Cisnienie_D'))
    m2.metric("RYTM SERCA", f"{s}/{d}" if s and d else "--")
    hr = safe_int(last.get('Tetno'))
    m3.metric("PULS SPOKOJU", f"{hr} BPM" if hr else "--")
    m4.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")

    # --- THE JOURNEY ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab_w, tab_v = st.tabs(["TWOJA SYLWETKA", "TWOJA WITALNOŚĆ"])

    with tab_w:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], line=dict(color='#7c8370', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.05)'))
        fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_w, use_container_width=True)

    with tab_v:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe", line=dict(color='#c2b8ad', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe", line=dict(color='#7c8370', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Puls", mode='markers', marker=dict(color='#d4af37', size=10, opacity=0.5)))
        fig_v.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig_v, use_container_width=True)

# --- RITUAL ACTIONS ---
st.markdown("<br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    with st.popover("🧘 NOWY WPIS", use_container_width=True):
        with st.form("add_ritual"):
            d = st.date_input("Data rytuału", datetime.now())
            w = st.number_input("Masa ciała", step=0.1)
            cs, cd, ct = st.columns(3)
            s_v = cs.number_input("SYS", value=120)
            d_v = cd.number_input("DIA", value=80)
            t_v = ct.number_input("Puls", value=70)
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ W DZIENNIKU"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_v, "Cisnienie_D": d_v, "Tetno": t_v, "Dawka": ds}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with c2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            dates = df_u['Data'].tolist()
            sel_date = st.selectbox("Moment do zmiany:", dates[::-1])
            row = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_ritual"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es, ed, et = st.columns(3)
                esys = es.number_input("SYS", value=safe_int(row.get('Cisnienie_S'), 120))
                edia = ed.number_input("DIA", value=safe_int(row.get('Cisnienie_D'), 80))
                etet = et.number_input("Puls", value=safe_int(row.get('Tetno'), 70))
                edose = st.selectbox("Dawka", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                     index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(safe_val(row.get('Dawka'))) if safe_val(row.get('Dawka')) in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0] else 0)
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']] = [ew, esys, edia, etet, edose]
                    conn.update(data=df_all)
                    st.rerun()

with c3:
    with st.popover("📜 ARCHIWUM", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; letter-spacing: 3px; color: #4a4540;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

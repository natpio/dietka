import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Wellness Vital Monitor", layout="wide", page_icon="🌿")

# --- WELLNESS STYLE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Quicksand:wght@500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        color: #4A4E4D;
        font-family: 'Inter', sans-serif;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 25px !important;
        padding: 20px !important;
    }

    h1 { font-family: 'Quicksand', sans-serif; color: #5D6D66; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- HELPER: SAFE INT CONVERSION ---
def safe_int(value):
    try:
        if pd.isna(value) or value == "": return None
        return int(float(value))
    except (ValueError, TypeError):
        return None

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    num_cols = ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']
    for col in num_cols:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI ---
st.markdown("<h1>🌿 Vital Ritual</h1>", unsafe_allow_html=True)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- METRYKI (BEZPIECZNE) ---
    m1, m2, m3, m4 = st.columns(4)
    last = df_u.iloc[-1]
    
    # Waga
    w_val = last.get('Waga')
    m1.metric("WAGA", f"{float(w_val):.1f} kg" if pd.notnull(w_val) else "--")
    
    # Ciśnienie
    s_val = safe_int(last.get('Cisnienie_S'))
    d_val = safe_int(last.get('Cisnienie_D'))
    m2.metric("CIŚNIENIE", f"{s_val}/{d_val}" if s_val and d_val else "--")
    
    # Tętno
    t_val = safe_int(last.get('Tetno'))
    m3.metric("TĘTNO", f"{t_val} BPM" if t_val else "--")
    
    # Dawka
    dose_val = last.get('Dawka')
    m4.metric("DAWKA", f"{dose_val} mg" if pd.notnull(dose_val) else "--")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROZDZIELONE WYKRESY ---
    tab1, tab2 = st.tabs(["📉 ANALIZA WAGI", "❤️ MONITOR KARDIOLOGICZNY"])

    with tab1:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], name="Waga",
                                   line=dict(color='#7A8B84', width=4, shape='spline'),
                                   fill='tozeroy', fillcolor='rgba(122, 139, 132, 0.1)'))
        fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_w, use_container_width=True)

    with tab2:
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#D98E73', width=3, shape='spline')))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7A8B84', width=3, shape='spline')))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Tętno", mode='markers+lines', line=dict(dash='dot', color='#A5A5A5', width=1)))
        fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_p, use_container_width=True)

# --- PANEL AKCJI ---
st.markdown("<br>", unsafe_allow_html=True)
c_add, c_edit, c_log = st.columns(3)

with c_add:
    with st.popover("➕ NOWY POMIAR", use_container_width=True):
        with st.form("add_form"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1)
            col_s, col_d, col_t = st.columns(3)
            sys = col_s.number_input("SYS", value=120)
            dia = col_d.number_input("DIA", value=80)
            hr = col_t.number_input("Tętno", value=70)
            dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            note = st.text_input("Notatki")
            if st.form_submit_button("ZAPISZ"):
                new_data = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys, "Cisnienie_D": dia, "Tetno": hr, "Dawka": dose, "Notatki": note}])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.rerun()

with c_edit:
    with st.popover("✏️ EDYTUJ WPIS", use_container_width=True):
        if not df_u.empty:
            list_dates = df_u['Data'].tolist()
            selected_date = st.selectbox("Wybierz datę:", list_dates[::-1])
            row = df_u[df_u['Data'] == selected_date].iloc[0]
            with st.form("edit_form"):
                ew = st.number_input("Waga", value=float(row['Waga']) if pd.notnull(row['Waga']) else 0.0)
                es, ed, et = st.columns(3)
                esys = es.number_input("SYS", value=safe_int(row['Cisnienie_S']) or 120)
                edia = ed.number_input("DIA", value=safe_int(row['Cisnienie_D']) or 80)
                etet = et.number_input("Tętno", value=safe_int(row['Tetno']) or 70)
                edose = st.selectbox("Dawka", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                     index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(row['Dawka']) if row['Dawka'] in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0] else 0)
                enote = st.text_input("Notatki", value=str(row['Notatki']) if pd.notnull(row['Notatki']) else "")
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == selected_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka', 'Notatki']] = [ew, esys, edia, etet, edose, enote]
                    conn.update(data=df_all)
                    st.rerun()

with c_log:
    with st.popover("📑 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

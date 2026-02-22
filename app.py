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

    h1 {
        font-family: 'Quicksand', sans-serif;
        color: #5D6D66;
        text-align: center;
    }
    
    .stButton>button {
        border-radius: 15px !important;
    }

    /* Stylizacja zakładek */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

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
    # --- METRYKI (PODSUMOWANIE) ---
    m1, m2, m3, m4 = st.columns(4)
    last = df_u.iloc[-1]
    m1.metric("WAGA", f"{last.get('Waga', 0):.1f} kg")
    m2.metric("CIŚNIENIE", f"{int(last.get('Cisnienie_S', 0))}/{int(last.get('Cisnienie_D', 0))}")
    m3.metric("TĘTNO", f"{int(last.get('Tetno', 0))} BPM")
    m4.metric("DAWKA", f"{last.get('Dawka', 0)} mg")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROZDZIELONE WYKRESY W ZAKŁADKACH ---
    tab1, tab2 = st.tabs(["📉 ANALIZA WAGI", "❤️ MONITOR KARDIOLOGICZNY"])

    with tab1:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df_u['Data'], y=df_u['Waga'],
            name="Waga",
            line=dict(color='#7A8B84', width=4, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(122, 139, 132, 0.1)'
        ))
        fig_w.update_layout(
            title="Trend masy ciała (kg)",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=400, xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with tab2:
        fig_p = go.Figure()
        # Skurczowe
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS (Skurczowe)", 
                                   line=dict(color='#D98E73', width=3, shape='spline')))
        # Rozkurczowe
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA (Rozkurczowe)", 
                                   line=dict(color='#7A8B84', width=3, shape='spline')))
        # Tętno
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Tętno (BPM)", 
                                   mode='markers+lines', line=dict(dash='dot', color='#A5A5A5', width=1)))
        
        fig_p.update_layout(
            title="Ciśnienie tętnicze i Tętno",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=400, legend=dict(orientation="h", y=1.1),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
        )
        st.plotly_chart(fig_p, use_container_width=True)

# --- PANEL AKCJI (BEZ ZMIAN) ---
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
            selected_date = st.selectbox("Wybierz datę do zmiany:", list_dates[::-1])
            row_to_edit = df_u[df_u['Data'] == selected_date].iloc[0]
            with st.form("edit_form"):
                new_w = st.number_input("Waga", value=float(row_to_edit['Waga']))
                c_s, c_d, c_t = st.columns(3)
                new_sys = c_s.number_input("SYS", value=int(row_to_edit['Cisnienie_S']))
                new_dia = c_d.number_input("DIA", value=int(row_to_edit['Cisnienie_D']))
                new_hr = c_t.number_input("Tętno", value=int(row_to_edit['Tetno']))
                new_dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                         index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(row_to_edit['Dawka']))
                new_note = st.text_input("Notatki", value=row_to_edit['Notatki'])
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == selected_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka', 'Notatki']] = [new_w, new_sys, new_dia, new_hr, new_dose, new_note]
                    conn.update(data=df_all)
                    st.rerun()

with c_log:
    with st.popover("📑 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

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

    /* Karty Metryk Wellness */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 25px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05) !important;
    }

    h1 {
        font-family: 'Quicksand', sans-serif;
        color: #5D6D66;
        font-weight: 500;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .stButton>button {
        background-color: #7A8B84 !important;
        border-radius: 15px !important;
        color: white !important;
        border: none !important;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

# --- NAPRAWA KOLUMN (KLUCZOWE!) ---
if not df_all.empty:
    # Standaryzacja nazw kolumn, aby uniknąć KeyError
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    
    # Bezpieczne wymuszenie typów numerycznych
    num_cols = ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']
    for col in num_cols:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')
        else:
            # Jeśli kolumny brakuje, stwórz ją z NaN, żeby kod się nie wywalił
            df_all[col] = None

# --- UI ---
st.markdown("<h1>🌿 Vital Ritual</h1>", unsafe_allow_html=True)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    # --- METRYKI ---
    m1, m2, m3, m4 = st.columns(4)
    last = df_u.iloc[-1]
    
    m1.metric("WAGA", f"{last.get('Waga', 0):.1f} kg")
    
    # Bezpieczne wyświetlanie Ciśnienia
    sys = last.get('Cisnienie_S')
    dia = last.get('Cisnienie_D')
    m2.metric("CIŚNIENIE", f"{int(sys)}/{int(dia)}" if pd.notnull(sys) else "--")
    
    # Bezpieczne wyświetlanie Tętna
    hr = last.get('Tetno')
    m3.metric("TĘTNO", f"{int(hr)} BPM" if pd.notnull(hr) else "Brak kolumny")
    
    m4.metric("DAWKA", f"{last.get('Dawka', 0)} mg")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- WYKRES (WELLNESS STYLE) ---
    fig = go.Figure()
    
    # Skurczowe
    fig.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe", 
                             line=dict(color='#D98E73', width=3, shape='spline')))
    # Rozkurczowe
    fig.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe", 
                             line=dict(color='#7A8B84', width=3, shape='spline')))
    # Tętno (jako kropki z linią pomocniczą)
    fig.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Tętno", 
                             mode='markers+lines', line=dict(dash='dot', color='#A5A5A5', width=1),
                             marker=dict(size=8, color='#D98E73')))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=450, margin=dict(l=10,r=10,t=20,b=10),
        legend=dict(orientation="h", y=1.1),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True)

# --- PANEL AKCJI ---
st.markdown("<br>", unsafe_allow_html=True)
c_left, c_right = st.columns(2)

with c_left:
    with st.popover("➕ NOWY POMIAR", use_container_width=True):
        with st.form("wellness_vital_form"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1)
            col_s, col_d, col_t = st.columns(3)
            sys_val = col_s.number_input("SYS", value=120)
            dia_val = col_d.number_input("DIA", value=80)
            hr_val = col_t.number_input("Tętno", value=70)
            dose = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            note = st.text_input("Notatki")
            
            if st.form_submit_button("ZAPISZ"):
                new_data = pd.DataFrame([{
                    "Użytkownik": user, "Data": d, "Waga": w, 
                    "Cisnienie_S": sys_val, "Cisnienie_D": dia_val, 
                    "Tetno": hr_val, "Dawka": dose, "Notatki": note
                }])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.rerun()

with c_right:
    with st.popover("📑 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

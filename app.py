import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="Lumina Medical Dashboard", layout="wide")

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
    
    .stApp { background-color: #fdfcfb; color: #2c3e50; font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Playfair Display', serif; color: #1a2a3a; font-size: 3rem !important; }
    
    /* Stylizacja metryk */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    
    /* Przyciski */
    .stButton>button {
        background-color: #1a2a3a !important;
        color: white !important;
        border-radius: 5px !important;
        border: none;
        padding: 12px;
        width: 100%;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #d4af37 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- PANEL BOCZNY (LOGOWANIE) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>LUMINA</h2>", unsafe_allow_html=True)
    user = st.radio("Zalogowany operator:", ["Piotr", "Natalia"])
    st.divider()
    
    st.markdown("### NOWY POMIAR")
    with st.form("medical_entry", clear_on_submit=True):
        d = st.date_input("Data pomiaru", datetime.now())
        w = st.number_input("Waga (kg)", min_value=40.0, step=0.1, format="%.1f")
        
        st.markdown("---")
        st.markdown("**CIŚNIENIE TĘTNICZE**")
        c1, c2 = st.columns(2)
        sys = c1.number_input("Skurczowe (SYS)", value=120)
        dia = c2.number_input("Rozkurczowe (DIA)", value=80)
        
        st.markdown("---")
        ds = st.selectbox("DAWKA (MG)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("SAMOPOCZUCIE (1-10)", 1, 10, 8)
        note = st.text_area("NOTATKI / SYMPTOMY")
        
        if st.form_submit_button("ZAPISZ W PROTOKOLE"):
            new_row = pd.DataFrame([{
                "Użytkownik": user, "Data": d, "Waga": w, 
                "Cisnienie_S": sys, "Cisnienie_D": dia, 
                "Dawka": ds, "Samopoczucie": mood, "Notatki": note
            }])
            updated_df = pd.concat([df_all, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Synchronizacja zakończona pomyślnie.")
            st.rerun()

# --- WIDOK GŁÓWNY ---
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

st.title(f"Dziennik Transformacji: {user}")

if not df_u.empty:
    # Metryki
    m1, m2, m3, m4 = st.columns(4)
    curr_w = df_u['Waga'].iloc[-1]
    prev_w = df_u['Waga'].iloc[0]
    sys_now = int(df_u['Cisnienie_S'].iloc[-1])
    dia_now = int(df_u['Cisnienie_D'].iloc[-1])
    
    m1.metric("Waga Obecna", f"{curr_w} kg", f"{curr_w - prev_w:.1f} kg", delta_color="inverse")
    m2.metric("Ostatnie Ciśnienie", f"{sys_now}/{dia_now}")
    m3.metric("Dawka", f"{df_u['Dawka'].iloc[-1]} mg")
    m4.metric("Status", "Stabilny", delta=None)

    st.divider()

    # Wykresy
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📉 Trend Masy Ciała")
        fig_w = px.line(df_u, x="Data", y="Waga", markers=True, 
                         color_discrete_sequence=['#1a2a3a'])
        fig_w.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_w, use_container_width=True)

    with col_chart2:
        st.markdown("### ❤️ Analiza Kardiologiczna")
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe", line=dict(color='#c0392b', width=2)))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe", line=dict(color='#2980b9', width=2)))
        
        # Strefa normy
        fig_p.add_hrect(y0=60, y1=125, fillcolor="#27ae60", opacity=0.05, layer="below", line_width=0)
        
        fig_p.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                            margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", y=1.1, x=1))
        st.plotly_chart(fig_p, use_container_width=True)

    # Tabela z historią
    st.markdown("### 📋 Kompletne Logi Systemowe")
    st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

else:
    st.info("Brak danych do wyświetlenia. Skorzystaj z panelu bocznego, aby dodać pierwszy wpis.")

st.caption("Lumina Wellness Protocol | Data Accuracy Mode Enabled")

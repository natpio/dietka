import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="BioMonitor Pro", layout="wide")

# --- STYLE CSS (LUXURY WELLNESS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    .stMetric {
        background: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    .sidebar-content {
        padding: 20px;
        background: #ffffff;
    }
    
    .stButton>button {
        background: #1a73e8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/822/822143.png", width=80)
    st.title("BioMonitor")
    user = st.radio("Operator systemu:", ["Piotr", "Natalia"])
    
    st.divider()
    with st.expander("📝 DODAJ NOWE POMIARY", expanded=True):
        with st.form("medical_form", clear_on_submit=True):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga (kg)", min_value=40.0, step=0.1)
            
            st.markdown("**Ciśnienie tętnicze**")
            c1, c2 = st.columns(2)
            sys = c1.number_input("Skurczowe", value=120)
            dia = c2.number_input("Rozkurczowe", value=80)
            
            st.markdown("**Protokół**")
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            mood = st.slider("Samopoczucie", 1, 10, 8)
            
            if st.form_submit_button("ZAPISZ W BAZIE"):
                new_data = pd.DataFrame([{
                    "Użytkownik": user, "Data": d, "Waga": w, 
                    "Cisnienie_S": sys, "Cisnienie_D": dia, 
                    "Dawka": ds, "Samopoczucie": mood
                }])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.balloons()
                st.rerun()

# --- MAIN DASHBOARD ---
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

st.title(f"Raport Biometryczny: {user}")

if not df_u.empty:
    # --- METRYKI ---
    m1, m2, m3, m4 = st.columns(4)
    curr_w = df_u['Waga'].iloc[-1]
    curr_s = int(df_u['Cisnienie_S'].iloc[-1])
    curr_d = int(df_u['Cisnienie_D'].iloc[-1])
    
    m1.metric("Masa Ciała", f"{curr_w} kg")
    m2.metric("Ciśnienie", f"{curr_s}/{curr_d}", "Norma" if curr_s < 135 else "Podwyższone")
    m3.metric("Ostatnia Dawka", f"{df_u['Dawka'].iloc[-1]} mg")
    m4.metric("Dzień Kuracji", len(df_u))

    st.divider()

    # --- WYKRESY ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📉 Trend spadku masy")
        fig_w = px.line(df_u, x="Data", y="Waga", markers=True, 
                         color_discrete_sequence=['#1a73e8'])
        fig_w.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_w, use_container_width=True)

    with col_chart2:
        st.subheader("❤️ Monitor ciśnienia")
        # Wykres kardiologiczny z dwiema liniami
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe (SYS)",
                                   line=dict(color='#e74c3c', width=3)))
        fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe (DIA)",
                                   line=dict(color='#3498db', width=3)))
        
        # Dodanie strefy normy ciśnienia
        fig_p.add_hrect(y0=60, y1=120, fillcolor="green", opacity=0.1, layer="below", line_width=0)
        
        fig_p.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_p, use_container_width=True)

    # --- TABELA ---
    st.subheader("📋 Pełna historia medyczna")
    st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

else:
    st.info("Oczekiwanie na pierwsze dane biometryczne...")

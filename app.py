import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Lumina Wellness Protocol", layout="wide", page_icon="⚖️")

# --- CUSTOM CSS (STYLIZACJA PREMIUM WELLNESS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #fdfcfb;
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
    
    h1 {
        font-family: 'Playfair Display', serif;
        color: #1a2a3a;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }

    /* Stylizacja kart metryk */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }

    /* Przyciski */
    .stButton>button {
        background-color: #1a2a3a !important;
        color: white !important;
        border-radius: 8px !important;
        border: none;
        padding: 12px;
        width: 100%;
        font-weight: 600;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #d4af37 !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f0e6d2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJACJA POŁĄCZENIA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    data = conn.read(ttl="0")
    if not data.empty:
        # Konwersja daty
        data['Data'] = pd.to_datetime(data['Data']).dt.date
        # Wymuszenie formatu numerycznego dla kluczowych kolumn (bezpieczeństwo)
        cols_to_fix = ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Dawka', 'Samopoczucie']
        for col in cols_to_fix:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
    return data

df_all = get_data()

# --- PANEL BOCZNY (REJESTRACJA POMIARÓW) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #bca07e;'>LUMINA</h2>", unsafe_allow_html=True)
    user = st.radio("Zalogowany profil:", ["Piotr", "Natalia"])
    st.divider()
    
    st.markdown("### ✍️ NOWY WPIS")
    with st.form("medical_entry_form", clear_on_submit=True):
        d = st.date_input("Data pomiaru", datetime.now())
        w = st.number_input("Waga (kg)", min_value=40.0, step=0.1, format="%.1f")
        
        st.markdown("---")
        st.markdown("**CIŚNIENIE TĘTNICZE**")
        c1, c2 = st.columns(2)
        sys = c1.number_input("Skurczowe (SYS)", value=120)
        dia = c2.number_input("Rozkurczowe (DIA)", value=80)
        
        st.markdown("---")
        ds = st.selectbox("DAWKA OZEMPIC (MG)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("SAMOPOCZUCIE (1-10)", 1, 10, 8)
        note = st.text_area("NOTATKI / SYMPTOMY")
        
        if st.form_submit_button("ZAPISZ DANE"):
            new_row = pd.DataFrame([{
                "Użytkownik": user, 
                "Data": d, 
                "Waga": w, 
                "Cisnienie_S": sys, 
                "Cisnienie_D": dia, 
                "Dawka": ds, 
                "Samopoczucie": mood, 
                "Notatki": note
            }])
            updated_df = pd.concat([df_all, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Synchronizacja zakończona!")
            st.rerun()

# --- WIDOK GŁÓWNY (DASHBOARD) ---
st.markdown(f"<h1>Dziennik Transformacji</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #7f8c8d; font-style: italic;'>Profil: {user}</p>", unsafe_allow_html=True)

df_user = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_user.empty:
    # --- METRYKI (ZABEZPIECZONE) ---
    m1, m2, m3, m4 = st.columns(4)
    
    # Masa ciała
    curr_w = df_user['Waga'].iloc[-1]
    first_w = df_user['Waga'].iloc[0]
    w_delta = curr_w - first_w
    
    # Ciśnienie (obsługa błędów konwersji)
    try:
        last_s = int(df_user['Cisnienie_S'].dropna().iloc[-1])
        last_d = int(df_user['Cisnienie_D'].dropna().iloc[-1])
        bp_val = f"{last_s}/{last_d}"
    except:
        bp_val = "Brak danych"
        
    m1.metric("Waga Obecna", f"{curr_w} kg", f"{w_delta:.1f} kg", delta_color="inverse")
    m2.metric("Ostatnie Ciśnienie", bp_val)
    m3.metric("Dawka", f"{df_user['Dawka'].iloc[-1]} mg")
    m4.metric("Pomiary", len(df_user))

    st.divider()

    # --- WYKRESY ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📉 Progresja Masy")
        fig_w = px.line(df_user, x="Data", y="Waga", markers=True, 
                        color_discrete_sequence=['#1a2a3a'])
        fig_w.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with col2:
        st.markdown("### ❤️ Profil Kardiologiczny")
        fig_p = go.Figure()
        
        # Filtrujemy dane do wykresu, by uniknąć przerw przy brakach danych
        plot_df = df_user.dropna(subset=['Cisnienie_S', 'Cisnienie_D'])
        
        fig_p.add_trace(go.Scatter(x=plot_df['Data'], y=plot_df['Cisnienie_S'], 
                                   name="Skurczowe", line=dict(color='#c0392b', width=2)))
        fig_p.add_trace(go.Scatter(x=plot_df['Data'], y=plot_df['Cisnienie_D'], 
                                   name="Rozkurczowe", line=dict(color='#2980b9', width=2)))
        
        # Strefa normy klinicznej
        fig_p.add_hrect(y0=60, y1=125, fillcolor="#27ae60", opacity=0.05, layer="below", line_width=0)
        
        fig_p.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_p, use_container_width=True)

    # --- HISTORIA I NOTATKI ---
    st.markdown("### 📋 Historia Logów")
    # Wyświetlamy tabelę od najnowszych
    st.dataframe(df_user.sort_values("Data", ascending=False), use_container_width=True)

else:
    st.info("System gotowy do pracy. Proszę wprowadzić pierwszy pomiar w panelu bocznym.")

st.markdown("<br><hr><p style='text-align: center; color: #95a5a6; font-size: 12px;'>LUMINA MEDICAL | Piotr & Natalia | v5.1 Clean Data Edition</p>", unsafe_allow_html=True)

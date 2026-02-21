import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="BioTracker Pro", page_icon="✨", layout="wide")

# --- ZAAWANSOWANY UI/CSS (Stylizacja Premium) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); /* Jasny, elegancki gradient */
    }

    /* Stylizacja kart (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    /* Personalizacja przycisków */
    .stButton>button {
        background: linear-gradient(45deg, #2E7D32, #4CAF50);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 25px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Nagłówki */
    h1 {
        color: #1a3a3a;
        font-weight: 600 !important;
        letter-spacing: -1px;
    }
    
    /* Ukrycie menu Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")
if not df_all.empty:
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date

# --- PANEL BOCZNY ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=100) # Ikona zdrowia
    st.title("BioTracker")
    user = st.radio("Zaloguj jako:", ["Piotr", "Natalia"])
    
    with st.expander("➕ DODAJ POMIAR", expanded=True):
        with st.form("new_entry", clear_on_submit=True):
            date = st.date_input("Kiedy?", datetime.now())
            weight = st.number_input("Waga (kg)", min_value=40.0, step=0.1)
            dose = st.selectbox("Dawka (mg)", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            mood = st.select_slider("Samopoczucie", options=["😢", "😕", "😐", "🙂", "🤩"], value="😐")
            submit = st.form_submit_button("ZAPISZ DANE")

    if submit:
        # Mapowanie emotek na cyfry dla wykresów
        mood_map = {"😢": 1, "😕": 2, "😐": 3, "🙂": 4, "🤩": 5}
        new_row = pd.DataFrame([{"Użytkownik": user, "Data": date, "Waga": weight, 
                                 "Dawka": dose, "Samopoczucie": mood_map[mood], "Notatki": ""}])
        conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
        st.balloons()
        st.rerun()

# --- DASHBOARD ---
df_user = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

st.title(f"Witaj, {user} 👋")
st.markdown(f"Twój postęp w kuracji Ozempic")

if not df_user.empty:
    # Sekcja wizualna
    m1, m2, m3 = st.columns(3)
    curr = df_user['Waga'].iloc[-1]
    prev = df_user['Waga'].iloc[0]
    diff = curr - prev
    
    m1.metric("Waga Obecna", f"{curr} kg", f"{diff:.1f} kg", delta_color="inverse")
    m2.metric("Ostatnia Dawka", f"{df_user['Dawka'].iloc[-1]} mg", "Dostępna")
    m3.metric("Nastrój", "Dobry", "Stable")

    # Wykresy w wersji "Clean Design"
    st.subheader("📊 Analiza Postępów")
    
    fig = px.area(df_user, x="Data", y="Waga", 
                  title="Trend spadku masy ciała",
                  color_discrete_sequence=['#2E7D32'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Poppins",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Druga kolumna z porównaniem
    col_left, col_right = st.columns(2)
    with col_left:
        st.write("### Ostatnie wpisy")
        st.dataframe(df_user.tail(5), use_container_width=True)
    with col_right:
        st.write("### Piotr vs Natalia")
        fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik", 
                           color_discrete_map={"Piotr": "#2E7D32", "Natalia": "#E91E63"})
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.info("Dodaj pierwszy pomiar, aby odblokować dashboard.")

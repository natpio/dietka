import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="BioTracker: Piotr i Natalia", page_icon="💊", layout="wide")

# --- CUSTOM CSS (Dla lepszego wyglądu) ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0")

df_all = get_data()

# --- SIDEBAR: WYBÓR PROFILU I WPISYWANIE ---
with st.sidebar:
    st.title("👤 Profil")
    user = st.radio("Kto używa aplikacji?", ["Piotr", "Natalia"])
    st.divider()
    
    st.header(f"➕ Nowy wpis: {user}")
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Data", datetime.now())
        weight = st.number_input("Waga (kg)", min_value=40.0, step=0.1)
        dose = st.selectbox("Dawka Ozempic (mg)", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("Samopoczucie (1-5)", 1, 5, 3)
        note = st.text_area("Notatki / Skutki uboczne")
        submit = st.form_submit_button("Zapisz w bazie")

    if submit:
        new_row = pd.DataFrame([{
            "Użytkownik": user,
            "Data": date.strftime('%Y-%m-%d'),
            "Waga": weight,
            "Dawka": dose,
            "Samopoczucie": mood,
            "Notatki": note
        }])
        updated_df = pd.concat([df_all, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success(f"Brawo {user}! Dane zapisane.")
        st.rerun()

# --- FILTROWANIE DANYCH DLA WIDOKU ---
df_user = df_all[df_all['Użytkownik'] == user].copy() if not df_all.empty else pd.DataFrame()

# --- GŁÓWNY DASHBOARD ---
st.title(f"📊 Dziennik Kuracji: {user}")

if not df_user.empty:
    # Metryki na górze
    m1, m2, m3 = st.columns(3)
    current_w = df_user['Waga'].iloc[-1]
    start_w = df_user['Waga'].iloc[0]
    diff = current_w - start_w
    
    m1.metric("Waga aktualna", f"{current_w} kg", f"{diff:.1f} kg", delta_color="inverse")
    m2.metric("Twoja ostatnia dawka", f"{df_user['Dawka'].iloc[-1]} mg")
    m3.metric("Postępy", f"{len(df_user)} wpisów")

    # Zakładki
    tab1, tab2, tab3 = st.tabs(["📈 Twój Trend", "🏆 Porównanie", "📋 Historia"])

    with tab1:
        fig = px.line(df_user, x="Data", y="Waga", title="Twoja droga do celu",
                      markers=True, line_shape="spline", color_discrete_sequence=["#2E7D32"])
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Piotr vs Natalia")
        if not df_all.empty:
            # Wykres porównawczy (wszystkie dane)
            fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik",
                               title="Wspólny postęp (kg)", markers=True)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.write("Potrzeba więcej danych od Was obojga.")

    with tab3:
        st.dataframe(df_user.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info(f"Cześć {user}! Tutaj pojawią się Twoje postępy. Dodaj swój pierwszy pomiar w panelu po lewej stronie.")

# Stopka motywacyjna
st.caption("Pamiętajcie o piciu dużej ilości wody i białku! Powodzenia! 💪")

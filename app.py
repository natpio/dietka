import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="BioTracker: Piotr i Natalia", page_icon="💊", layout="wide")

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Pobieramy dane i upewniamy się, że Data jest formatem daty
    data = conn.read(ttl="0")
    if not data.empty:
        data['Data'] = pd.to_datetime(data['Data']).dt.date
    return data

df_all = get_data()

# --- SIDEBAR: PROFIL I NOWY WPIS ---
with st.sidebar:
    st.title("👤 Profil")
    user = st.radio("Kto używa aplikacji?", ["Piotr", "Natalia"])
    st.divider()
    
    st.header(f"➕ Nowy wpis: {user}")
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Data", datetime.now())
        weight = st.number_input("Waga (kg)", min_value=40.0, step=0.1)
        dose = st.selectbox("Dawka (mg)", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("Samopoczucie", 1, 5, 3)
        note = st.text_area("Notatki")
        submit = st.form_submit_button("Zapisz w bazie")

    if submit:
        new_row = pd.DataFrame([{
            "Użytkownik": user,
            "Data": date,
            "Waga": weight,
            "Dawka": dose,
            "Samopoczucie": mood,
            "Notatki": note
        }])
        updated_df = pd.concat([df_all, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success("Dane zapisane!")
        st.rerun()

# --- FILTROWANIE ---
df_user = df_all[df_all['Użytkownik'] == user].copy() if not df_all.empty else pd.DataFrame()

# --- GŁÓWNY DASHBOARD ---
st.title(f"📊 Dziennik: {user}")

if not df_user.empty:
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Wykresy", "🏆 Porównanie", "📋 Historia", "🛠️ Zarządzaj"])

    with tab1:
        fig = px.line(df_user, x="Data", y="Waga", title="Twoja waga", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Piotr vs Natalia")
        fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik", markers=True)
        st.plotly_chart(fig_comp, use_container_width=True)

    with tab3:
        st.dataframe(df_user.sort_values(by="Data", ascending=False), use_container_width=True)

    with tab4:
        st.subheader("Edytuj lub usuń wpis")
        # Wybór wiersza do edycji na podstawie daty (pokazujemy listę wpisów użytkownika)
        df_user_to_edit = df_user.copy()
        df_user_to_edit['Display'] = df_user_to_edit['Data'].astype(str) + " - " + df_user_to_edit['Waga'].astype(str) + "kg"
        
        selected_option = st.selectbox("Wybierz wpis do zmiany:", df_user_to_edit['Display'])
        idx_to_edit = df_user_to_edit[df_user_to_edit['Display'] == selected_option].index[0]
        
        row = df_all.iloc[idx_to_edit]

        col1, col2 = st.columns(2)
        with col1:
            new_w = st.number_input("Popraw wagę", value=float(row['Waga']), step=0.1)
            new_d = st.selectbox("Popraw dawkę", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0], index=[0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(row['Dawka']))
        with col2:
            new_m = st.slider("Popraw samopoczucie", 1, 5, int(row['Samopoczucie']))
            new_n = st.text_area("Popraw notatkę", value=row['Notatki'])

        c_edit, c_del = st.columns(2)
        if c_edit.button("💾 Zapisz zmiany", use_container_width=True):
            df_all.at[idx_to_edit, 'Waga'] = new_w
            df_all.at[idx_to_edit, 'Dawka'] = new_d
            df_all.at[idx_to_edit, 'Samopoczucie'] = new_m
            df_all.at[idx_to_edit, 'Notatki'] = new_n
            conn.update(data=df_all)
            st.success("Zaktualizowano!")
            st.rerun()
            
        if c_del.button("🗑️ Usuń ten wpis", use_container_width=True, type="primary"):
            df_all = df_all.drop(idx_to_edit)
            conn.update(data=df_all)
            st.warning("Wpis usunięty.")
            st.rerun()
else:
    st.info("Brak danych. Dodaj pierwszy wpis w panelu bocznym!")

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="BioTracker: Piotr & Natalia", 
    page_icon="⚖️", 
    layout="wide"
)

# --- STYLIZACJA CSS ---
st.markdown("""
    <style>
    .main { background-color: #f9fbfd; }
    .stMetric { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Odczyt danych z arkusza (ttl=0 wymusza brak cache, czyli zawsze świeże dane)
    data = conn.read(ttl="0")
    if not data.empty:
        # Konwersja kolumny Data na typ daty, aby wykresy działały poprawnie
        data['Data'] = pd.to_datetime(data['Data']).dt.date
    return data

df_all = load_data()

# --- PANEL BOCZNY (SIDEBAR) ---
with st.sidebar:
    st.title("👤 Profil")
    user = st.radio("Kto używa aplikacji?", ["Piotr", "Natalia"])
    st.divider()
    
    st.header(f"➕ Nowy wpis: {user}")
    with st.form("new_entry_form", clear_on_submit=True):
        date = st.date_input("Data pomiaru", datetime.now())
        weight = st.number_input("Waga (kg)", min_value=30.0, max_value=200.0, step=0.1, format="%.1f")
        dose = st.selectbox("Dawka Ozempic (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        mood = st.slider("Samopoczucie (1-źle, 5-świetnie)", 1, 5, 3)
        note = st.text_area("Notatki (opcjonalnie)")
        
        submit = st.form_submit_button("Zapisz w dzienniku")

    if submit:
        new_row = pd.DataFrame([{
            "Użytkownik": user,
            "Data": date.strftime('%Y-%m-%d'),
            "Waga": weight,
            "Dawka": dose,
            "Samopoczucie": mood,
            "Notatki": note
        }])
        # Łączenie starych danych z nowym wierszem
        updated_df = pd.concat([df_all, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success(f"Brawo {user}! Dane zostały zapisane.")
        st.rerun()

# --- FILTROWANIE DANYCH DLA UŻYTKOWNIKA ---
if not df_all.empty:
    df_user = df_all[df_all['Użytkownik'] == user].sort_values("Data")
else:
    df_user = pd.DataFrame()

# --- WIDOK GŁÓWNY ---
st.title(f"📈 Dashboard: {user}")

if not df_user.empty:
    # Sekcja Metryk
    col1, col2, col3 = st.columns(3)
    
    current_w = df_user['Waga'].iloc[-1]
    first_w = df_user['Waga'].iloc[0]
    total_diff = current_w - first_w
    
    col1.metric("Waga aktualna", f"{current_w} kg", f"{total_diff:.1f} kg", delta_color="inverse")
    col2.metric("Ostatnia dawka", f"{df_user['Dawka'].iloc[-1]} mg")
    col3.metric("Dni kuracji", (datetime.now().date() - df_user['Data'].iloc[0]).days)

    st.divider()

    # Zakładki
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Wykresy", "🏆 Bitwa o zdrowie", "📋 Historia", "🛠️ Zarządzaj"])

    with tab1:
        # Wykres wagi
        fig_weight = px.line(df_user, x="Data", y="Waga", title="Zmiana wagi w czasie",
                             markers=True, line_shape="spline", color_discrete_sequence=["#2E7D32"])
        fig_weight.update_layout(plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
        st.plotly_chart(fig_weight, use_container_width=True)
        
        # Wykres dawka vs samopoczucie
        fig_dose = px.bar(df_user, x="Data", y="Dawka", color="Samopoczucie",
                          title="Historia dawkowania i samopoczucie",
                          color_continuous_scale=px.colors.sequential.Greens)
        st.plotly_chart(fig_dose, use_container_width=True)

    with tab2:
        st.subheader("Piotr 🆚 Natalia")
        if not df_all.empty:
            fig_comp = px.line(df_all, x="Data", y="Waga", color="Użytkownik",
                               title="Wspólny postęp wagowy", markers=True)
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Procentowa utrata wagi (opcjonalnie)
            st.info("💡 Porada: Skupcie się na trendzie, nie na pojedynczych dniach!")
        
    with tab3:
        st.subheader("Wszystkie Twoje wpisy")
        st.dataframe(df_user.sort_values("Data", ascending=False), use_container_width=True)

    with tab4:
        st.subheader("Edytuj lub usuń wpis")
        # Tworzymy listę do wyboru na podstawie daty i wagi
        df_edit = df_user.copy()
        df_edit['label'] = df_edit['Data'].astype(str) + " (" + df_edit['Waga'].astype(str) + " kg)"
        
        selected_label = st.selectbox("Wybierz wpis do modyfikacji:", df_edit['label'].tolist())
        
        # Pobieramy index z oryginalnego df_all
        original_idx = df_edit[df_edit['label'] == selected_label].index[0]
        row_data = df_all.loc[original_idx]

        with st.expander("Otwórz formularz edycji"):
            edit_w = st.number_input("Popraw wagę", value=float(row_data['Waga']), step=0.1)
            edit_d = st.selectbox("Popraw dawkę", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                  index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(row_data['Dawka']))
            edit_m = st.slider("Popraw samopoczucie", 1, 5, int(row_data['Samopoczucie']))
            edit_n = st.text_area("Popraw notatkę", value=str(row_data['Notatki']))

            col_a, col_b = st.columns(2)
            if col_a.button("💾 Zapisz zmiany"):
                df_all.at[original_idx, 'Waga'] = edit_w
                df_all.at[original_idx, 'Dawka'] = edit_d
                df_all.at[original_idx, 'Samopoczucie'] = edit_m
                df_all.at[original_idx, 'Notatki'] = edit_n
                conn.update(data=df_all)
                st.success("Zmiany zapisane!")
                st.rerun()

            if col_b.button("🗑️ Usuń ten wpis", type="primary"):
                df_all = df_all.drop(original_idx)
                conn.update(data=df_all)
                st.warning("Wpis został usunięty.")
                st.rerun()

else:
    st.info(f"Cześć {user}! Twój dziennik jest jeszcze pusty. Dodaj pierwszy pomiar w panelu bocznym ⬅️")

st.caption("BioTracker v2.0 | Piotr & Natalia | Powodzenia!")

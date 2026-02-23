import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="The Sanctuary 2.2 | Personalized Longevity",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# --- 2. PERSONALIZACJA PROFILI ---
USER_PROFILES = {
    "Piotr": {"height": 1.70, "age": 38, "gender": "male"},
    "Natalia": {"height": 1.62, "age": 37, "gender": "female"}
}

# --- 3. ORGANIC SANCTUARY STYLE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.9), rgba(242, 236, 228, 0.9)), 
                    url('https://images.unsplash.com/photo-1544161515-4ab6ce6db874?q=80&w=2070');
        background-size: cover; background-attachment: fixed;
        color: #5d5750; font-family: 'Inter', sans-serif;
    }

    .sanctuary-title {
        font-family: 'Playfair Display', serif; font-size: 3.8rem; font-style: italic;
        text-align: center; color: #4a4540; padding: 25px 0 5px 0;
    }

    .sanctuary-subtitle {
        text-align: center; font-size: 0.8rem; letter-spacing: 5px; color: #8c857e;
        margin-bottom: 30px; text-transform: uppercase;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px); border-radius: 30px !important;
        padding: 22px !important; border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }

    .status-norm { color: #7c8370; font-weight: 600; }
    .status-warn { color: #d98e73; font-weight: 600; }
    .status-alert { color: #b04b4b; font-weight: 600; }

    header, footer {visibility: hidden;}
    
    /* Usunięcie obramowania tabel */
    .stDataFrame { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA I FUNKCJE POMOCNICZE ---
def safe_val(val, default=0.0):
    try:
        if pd.isna(val) or val == "" or val is None: return float(default)
        return float(val)
    except: return float(default)

def safe_int(val, default=0):
    try:
        if pd.isna(val) or val == "" or val is None: return int(default)
        return int(float(val))
    except: return int(default)

def get_bmi_category(bmi):
    if bmi < 18.5: return "Niedowaga", "status-warn"
    if bmi < 25: return "Waga Prawidłowa", "status-norm"
    if bmi < 30: return "Nadwaga", "status-warn"
    return "Otyłość", "status-alert"

def calculate_metrics(df, height):
    """Oblicza PP, MAP i BMI dla całego DataFrame."""
    if df.empty:
        return df
    df = df.copy()
    # Konwersja na numeryczne dla pewności obliczeń
    for col in ['Cisnienie_S', 'Cisnienie_D', 'Waga']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['PP'] = df['Cisnienie_S'] - df['Cisnienie_D']
    df['MAP'] = df['Cisnienie_D'] + (1/3 * df['PP'])
    df['BMI'] = df['Waga'] / (height ** 2)
    return df

# --- 5. POŁĄCZENIE Z DANYMI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_all = conn.read(ttl="0")
except Exception as e:
    st.error(f"Błąd połączenia z bazą: {e}")
    df_all = pd.DataFrame()

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    if 'Mood' not in df_all.columns: df_all['Mood'] = "🌿 Równowaga"
    # Normalizacja daty
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- 6. INTERFEJS UŻYTKOWNIKA ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>PERSONAL VITALITY HUB</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")

# Parametry profilu
current_height = USER_PROFILES[user]["height"]
current_age = USER_PROFILES[user]["age"]

# Filtrowanie i obliczenia dla konkretnego użytkownika
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()
df_u = calculate_metrics(df_u, current_height)

if not df_u.empty:
    last = df_u.iloc[-1]
    bmi_val = round(last['BMI'], 1)
    bmi_label, bmi_class = get_bmi_category(bmi_val)
    map_val = round(last['MAP'], 1)
    pp_val = int(last['PP'])
    
    # --- PANEL GŁÓWNYCH METRYK ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("MASA CIAŁA", f"{safe_val(last.get('Waga')):.1f} kg")
        st.markdown(f"<span class='{bmi_class}'>{bmi_label} (BMI: {bmi_val})</span>", unsafe_allow_html=True)
        
    with m2:
        st.metric("CIŚNIENIE", f"{safe_int(last.get('Cisnienie_S'))}/{safe_int(last.get('Cisnienie_D'))}")
        st.markdown(f"Wiek: **{current_age} lat** | Wzrost: **{int(current_height*100)} cm**")
        
    with m3:
        st.metric("ŚREDNIE (MAP)", f"{map_val} mmHg")
        map_status = "Optymalne" if 70 <= map_val <= 100 else "Poza normą"
        st.markdown(f"Status perfuzji: **{map_status}**")
        
    with m4:
        st.metric("CIŚNIENIE TĘTNA", f"{pp_val} mmHg")
        pp_class = "Elastyczne" if pp_val <= 60 else "Sztywne"
        st.markdown(f"Naczynia: **{pp_class}**")

    # --- WYKRESY ---
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📉 TRENDY", "📊 KARDIOLOGIA", "🩺 RAPORT"])

    with t1:
        c_l, c_r = st.columns(2)
        with c_l:
            v_w = df_u['Waga'].dropna()
            if not v_w.empty:
                fig_w = go.Figure()
                fig_w.add_trace(go.Scatter(
                    x=df_u['Data'], y=df_u['Waga'], name="Waga", 
                    line=dict(color='#7c8370', width=4, shape='spline'), 
                    fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)'
                ))
                fig_w.update_layout(
                    title="Masa ciała (kg)", 
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    height=380, margin=dict(l=20, r=20, t=40, b=20),
                    yaxis=dict(range=[v_w.min()-1, v_w.max()+1])
                )
                st.plotly_chart(fig_w, use_container_width=True)
        with c_r:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS (Skurczowe)", line=dict(color='#d98e73', width=3)))
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA (Rozkurczowe)", line=dict(color='#7c8370', width=3)))
            fig_p.update_layout(title="Ciśnienie tętnicze", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_p, use_container_width=True)

    with t2:
        st.markdown("#### Zaawansowana hemodynamika")
        fig_adv = go.Figure()
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['MAP'], name="MAP (Średnie)", line=dict(color='#7c8370', width=4)))
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['PP'], name="PP (Ciśnienie Tętna)", line=dict(color='#d98e73', dash='dot')))
        fig_adv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_adv, use_container_width=True)

    with t3:
        # Wyświetlamy najważniejsze kolumny w raporcie
        cols_to_show = ['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka', 'Mood']
        st.dataframe(df_u[cols_to_show].sort_values("Data", ascending=False), use_container_width=True)

# --- 7. PANEL AKCJI ---
st.markdown("<br>", unsafe_allow_html=True)
ca, ce, ch = st.columns(3)

with ca:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga (kg)", value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 70.0, step=0.1, min_value=30.0, max_value=200.0)
            s = st.number_input("SYS (Skurczowe)", value=120, min_value=60, max_value=250)
            di = st.number_input("DIA (Rozkurczowe)", value=80, min_value=30, max_value=150)
            p = st.number_input("Puls", value=70, min_value=30, max_value=220)
            mo = st.selectbox("Nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres"])
            dw = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            
            if st.form_submit_button("ZAPISZ W BAZIE"):
                new_row = pd.DataFrame([{
                    "Użytkownik": user, 
                    "Data": d, 
                    "Waga": w, 
                    "Cisnienie_S": s, 
                    "Cisnienie_D": di, 
                    "Tetno": p, 
                    "Dawka": dw, 
                    "Mood": mo
                }])
                updated_df = pd.concat([df_all, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Dane zapisane!")
                st.rerun()

with ce:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            # Wybór daty do edycji (tylko daty obecne u danego użytkownika)
            available_dates = df_u['Data'].tolist()[::-1]
            sel_d = st.selectbox("Wybierz datę do poprawy:", available_dates)
            row = df_u[df_u['Data'] == sel_d].iloc[0]
            
            with st.form("edit"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es = st.number_input("SYS", value=safe_int(row.get('Cisnienie_S')))
                ed = st.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                
                if st.form_submit_button("AKTUALIZUJ"):
                    # Znalezienie indeksu w głównym DataFrame
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_d)].index
                    if not idx.empty:
                        df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [ew, es, ed]
                        conn.update(data=df_all)
                        st.success("Dane zaktualizowane!")
                        st.rerun()
        else:
            st.write("Brak danych do edycji.")

with ch:
    st.markdown(f"<div style='text-align: center; opacity: 0.3; font-size: 0.7rem;'>THE SANCTUARY v2.2<br>{user} ({int(current_height*100)}cm)</div>", unsafe_allow_html=True)

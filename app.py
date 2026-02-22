import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="The Sanctuary 2.1 | Longevity Hub",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# --- ORGANIC SANCTUARY STYLE (KOMPLETNY CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.88), rgba(242, 236, 228, 0.88)), 
                    url('https://images.unsplash.com/photo-1544161515-4ab6ce6db874?q=80&w=2070');
        background-size: cover;
        background-attachment: fixed;
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.8rem;
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 30px 0 5px 0;
        letter-spacing: -1px;
    }

    .sanctuary-subtitle {
        text-align: center;
        font-size: 0.85rem;
        letter-spacing: 5px;
        color: #8c857e;
        margin-bottom: 35px;
        text-transform: uppercase;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 30px !important;
        padding: 22px !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.03) !important;
    }

    .status-norm { color: #7c8370; font-weight: 600; }
    .status-warn { color: #d98e73; font-weight: 600; }
    .status-alert { color: #b04b4b; font-weight: 600; }

    .report-card {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #7c8370;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .stButton>button {
        background: #7c8370 !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 12px 35px !important;
        border: none !important;
        transition: all 0.4s ease;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: #5d6354 !important;
        box-shadow: 0 8px 20px rgba(124, 131, 112, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 40px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE LOGICZNE (NAPRAWIONE DEFINICJE) ---
def safe_val(val, default=0.0):
    try:
        if pd.isna(val) or val == "" or val is None: return float(default)
        return float(val)
    except: return float(default)

def safe_int(val, default=0):
    """Funkcja konwertująca na int, której brakowało w poprzednim błędzie."""
    try:
        if pd.isna(val) or val == "" or val is None: return int(default)
        return int(float(val))
    except: return int(default)

def calc_advanced_bp(sys, dia):
    s, d = safe_val(sys), safe_val(dia)
    if s == 0 or d == 0: return 0.0, 0.0
    pp = s - d
    map_v = d + (1/3 * pp)
    return round(pp, 1), round(map_v, 1)

def get_bmi(weight, height=1.80):
    w = safe_val(weight)
    if w == 0: return 0, "Brak danych", "status-norm"
    bmi = w / (height ** 2)
    if bmi < 18.5: return bmi, "Niedowaga", "status-warn"
    if bmi < 25: return bmi, "Waga Prawidłowa", "status-norm"
    return bmi, "Nadwaga", "status-warn"

# --- POŁĄCZENIE I DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    if 'Mood' not in df_all.columns: df_all['Mood'] = "🌿 Równowaga"
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- STRUKTURA GŁÓWNA ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>Advanced Longevity Monitoring</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    pp_val, map_val = calc_advanced_bp(last.get('Cisnienie_S'), last.get('Cisnienie_D'))
    
    # --- PANEL METRYK ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        w_v = safe_val(last.get('Waga'))
        bmi_v, bmi_c, bmi_s = get_bmi(w_v)
        st.metric("MASA CIAŁA", f"{w_v:.1f} kg")
        st.markdown(f"<span class='{bmi_s}'>{bmi_c} (BMI: {bmi_v:.1f})</span>", unsafe_allow_html=True)
    with m2:
        st.metric("CIŚNIENIE (SYS/DIA)", f"{safe_int(last.get('Cisnienie_S'))}/{safe_int(last.get('Cisnienie_D'))}")
        st.markdown(f"Status: **Aktywny**")
    with m3:
        st.metric("ŚREDNIE TĘTNICZE (MAP)", f"{map_val} mmHg")
        map_status = "Norma" if 70 <= map_val <= 100 else "Obserwacja"
        st.markdown(f"Status: **{map_status}**")
    with m4:
        st.metric("CIŚNIENIE TĘTNA (PP)", f"{int(pp_val)} mmHg")
        pp_class = "status-norm" if pp_val <= 60 else "status-warn"
        st.markdown(f"<span class='{pp_class}'>{'Optymalne' if pp_val <= 60 else 'Szerokie'}</span>", unsafe_allow_html=True)

    # --- ZAKŁADKI ---
    tab1, tab2, tab3 = st.tabs(["📊 ANALIZA KRĄŻENIA", "🩺 RAPORT LEKARSKI", "✨ RYTUAŁY"])

    with tab1:
        st.markdown("#### Dynamika MAP i Pulse Pressure")
        
        
        fig_adv = go.Figure()
        df_u['PP'] = df_u['Cisnienie_S'] - df_u['Cisnienie_D']
        df_u['MAP'] = df_u['Cisnienie_D'] + (1/3 * df_u['PP'])
        
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['MAP'], name="MAP (Średnie)", line=dict(color='#7c8370', width=4, shape='spline')))
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['PP'], name="PP (Tętna)", line=dict(color='#d98e73', dash='dot')))
        
        fig_adv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, 
                             legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig_adv, use_container_width=True)

    with tab2:
        st.markdown("### Dane Historyczne")
        st.table(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].sort_values("Data", ascending=False).head(10))
        csv = df_u.to_csv(index=False).encode('utf-8')
        st.download_button("📥 EKSPORT CSV", csv, f"sanctuary_{user}.csv", "text/csv")

    with tab3:
        st.info("💡 Czy wiesz, że MAP poniżej 60 mmHg może powodować niedokrwienie narządów, a powyżej 100 mmHg obciąża serce?")

# --- STOPKA Z FORMULARZAMI (POPRAWIONE REFERENCJE) ---
st.markdown("<br><br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)

with b1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add_new"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            s_v = st.number_input("SYS", value=120)
            d_v = st.number_input("DIA", value=80)
            p_v = st.number_input("Puls", value=70)
            mood_v = st.selectbox("Nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres"])
            ds_v = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("DODAJ"):
                new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_v, "Cisnienie_D": d_v, "Tetno": p_v, "Dawka": ds_v, "Mood": mood_v}])
                conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
                st.rerun()

with b2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_date = st.selectbox("Data do edycji:", df_u['Data'].tolist()[::-1])
            row_to_edit = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_existing"):
                new_w = st.number_input("Waga", value=safe_val(row_to_edit.get('Waga')))
                # TUTAJ BYŁ BŁĄD - TERAZ safe_int JEST ZDEFINIOWANA
                new_s = st.number_input("SYS", value=safe_int(row_to_edit.get('Cisnienie_S')))
                new_d = st.number_input("DIA", value=safe_int(row_to_edit.get('Cisnienie_D')))
                if st.form_submit_button("ZAPISZ ZMIANY"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [new_w, new_s, new_d]
                    conn.update(data=df_all)
                    st.rerun()

with b3:
    with st.popover("📜 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.3; font-size: 0.7rem;'>THE SANCTUARY • BIOMETRYCZNA HARMONIA</div>", unsafe_allow_html=True)

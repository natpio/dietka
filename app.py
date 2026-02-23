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
    "Natalia": {"height": 1.62, "age": 38, "gender": "female"}
}

# --- 3. ORGANIC SANCTUARY STYLE (FULL CSS) ---
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

def get_advanced_metrics(sys, dia, weight, height):
    s, d, w = safe_val(sys), safe_val(dia), safe_val(weight)
    pp = s - d if s > 0 else 0
    map_v = d + (1/3 * pp) if s > 0 else 0
    bmi = w / (height ** 2) if w > 0 else 0
    return round(pp, 1), round(map_v, 1), round(bmi, 1)

# --- 5. POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    if 'Mood' not in df_all.columns: df_all['Mood'] = "🌿 Równowaga"
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- 6. INTERFEJS UŻYTKOWNIKA ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>PERSONAL VITALITY HUB</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")

# Pobranie parametrów profilu
current_height = USER_PROFILES[user]["height"]
current_age = USER_PROFILES[user]["age"]

df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    pp, map_val, bmi = get_advanced_metrics(last.get('Cisnienie_S'), last.get('Cisnienie_D'), last.get('Waga'), current_height)
    bmi_label, bmi_class = get_bmi_category(bmi)
    
    # --- PANEL GŁÓWNYCH METRYK ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("MASA CIAŁA", f"{safe_val(last.get('Waga')):.1f} kg")
        st.markdown(f"<span class='{bmi_class}'>{bmi_label} (BMI: {bmi})</span>", unsafe_allow_html=True)
        
    with m2:
        st.metric("CIŚNIENIE", f"{safe_int(last.get('Cisnienie_S'))}/{safe_int(last.get('Cisnienie_D'))}")
        st.markdown(f"Wiek: **{current_age} lat** | Wzrost: **{int(current_height*100)} cm**")
        
    with m3:
        st.metric("ŚREDNIE (MAP)", f"{map_val} mmHg")
        map_status = "Optymalne" if 70 <= map_val <= 100 else "Poza normą"
        st.markdown(f"Status perfuzji: **{map_status}**")
        
    with m4:
        st.metric("TĘTNA (PP)", f"{int(pp)} mmHg")
        pp_class = "Elastyczne" if pp <= 60 else "Sztywne"
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
                fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], name="Waga", line=dict(color='#7c8370', width=4, shape='spline'), fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)'))
                fig_w.update_layout(title="Masa ciała (kg)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, yaxis=dict(range=[v_w.min()-1, v_w.max()+1]))
                st.plotly_chart(fig_w, use_container_width=True)
        with c_r:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#d98e73', width=3)))
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3)))
            fig_p.update_layout(title="Ciśnienie tętnicze", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380)
            st.plotly_chart(fig_p, use_container_width=True)

    with t2:
        st.markdown("#### Zaawansowana hemodynamika")
        
        fig_adv = go.Figure()
        df_u['PP_v'] = df_u['Cisnienie_S'] - df_u['Cisnienie_D']
        df_u['MAP_v'] = df_u['Cisnienie_D'] + (1/3 * df_u['PP_v'])
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['MAP_v'], name="MAP (Średnie)", line=dict(color='#7c8370', width=4)))
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['PP_v'], name="PP (Tętna)", line=dict(color='#d98e73', dash='dot')))
        fig_adv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_adv, use_container_width=True)

    with t3:
        st.dataframe(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka', 'Mood']].sort_values("Data", ascending=False), use_container_width=True)

# --- PANEL AKCJI ---
st.markdown("<br>", unsafe_allow_html=True)
ca, ce, ch = st.columns(3)
with ca:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 70.0, step=0.1)
            s = st.number_input("SYS", value=120)
            di = st.number_input("DIA", value=80)
            p = st.number_input("Puls", value=70)
            mo = st.selectbox("Nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres"])
            dw = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s, "Cisnienie_D": di, "Tetno": p, "Dawka": dw, "Mood": mo}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with ce:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_d = st.selectbox("Data:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_d].iloc[0]
            with st.form("edit"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es = st.number_input("SYS", value=safe_int(row.get('Cisnienie_S')))
                ed = st.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_d)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [ew, es, ed]
                    conn.update(data=df_all)
                    st.rerun()

with ch:
    st.markdown("<div style='text-align: center; opacity: 0.3; font-size: 0.7rem;'>THE SANCTUARY v2.2<br>Piotr (170cm) & Natalia (162cm)</div>", unsafe_allow_html=True)

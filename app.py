import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="The Sanctuary 2.0 | Vital Rituals",
    layout="wide",
    page_icon="🌿"
)

# --- ORGANIC SANCTUARY STYLE (FULL CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.85), rgba(242, 236, 228, 0.85)), 
                    url('https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=2070&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed;
        color: #5d5750; font-family: 'Inter', sans-serif;
    }

    .sanctuary-title {
        font-family: 'Playfair Display', serif; font-size: 3.5rem; font-style: italic;
        text-align: center; color: #4a4540; padding: 30px 0 5px 0;
    }

    .sanctuary-subtitle {
        text-align: center; font-size: 0.8rem; letter-spacing: 4px; color: #8c857e;
        margin-bottom: 30px; text-transform: uppercase;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px); border-radius: 30px !important;
        padding: 20px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }

    .status-norm { color: #7c8370; font-weight: 600; border-bottom: 2px solid #7c8370; }
    .status-warn { color: #d98e73; font-weight: 600; border-bottom: 2px solid #d98e73; }
    .status-alert { color: #b04b4b; font-weight: 600; border-bottom: 2px solid #b04b4b; }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; justify-content: center; border-bottom: none; }
    .stTabs [data-baseweb="tab"] { text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem; color: #8c857e !important; }
    .stTabs [aria-selected="true"] { color: #5d5750 !important; font-weight: 600 !important; border-bottom: 3px solid #7c8370 !important; }

    .stButton>button {
        background: #7c8370 !important; color: white !important;
        border-radius: 50px !important; padding: 12px 35px !important;
        border: none !important; transition: 0.4s; letter-spacing: 1px;
    }

    .report-card {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 6px solid #7c8370; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
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

def get_bp_status(s, d):
    s, d = safe_int(s), safe_int(d)
    if s < 120 and d < 80: return "Optymalne", "status-norm"
    if s < 130 and d < 85: return "Prawidłowe", "status-norm"
    if s < 140 or d < 90: return "Wysokie Prawidłowe", "status-warn"
    return "Nadciśnienie", "status-alert"

def get_bmi(weight, height=1.80):
    w = safe_val(weight)
    if w == 0: return 0, "Brak danych", "status-norm"
    bmi = w / (height ** 2)
    if bmi < 18.5: return bmi, "Niedowaga", "status-warn"
    if bmi < 25: return bmi, "Waga Prawidłowa", "status-norm"
    return bmi, "Nadwaga", "status-warn"

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    # Zapewnienie istnienia kolumny Mood
    if 'Mood' not in df_all.columns:
        df_all['Mood'] = None
    
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- METRYKI ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        w_v = safe_val(last.get('Waga'))
        bmi_v, bmi_c, bmi_s = get_bmi(w_v)
        st.metric("MASA CIAŁA", f"{w_v:.1f} kg")
        st.markdown(f"<span class='{bmi_s}'>{bmi_c} (BMI: {bmi_v:.1f})</span>", unsafe_allow_html=True)
    with m2:
        sys, dia = safe_int(last.get('Cisnienie_S')), safe_int(last.get('Cisnienie_D'))
        bp_c, bp_s = get_bp_status(sys, dia)
        st.metric("CIŚNIENIE", f"{sys}/{dia}")
        st.markdown(f"<span class='{bp_s}'>{bp_c}</span>", unsafe_allow_html=True)
    with m3:
        p_v = safe_int(last.get('Tetno'))
        mood_v = last.get('Mood') if pd.notna(last.get('Mood')) else "🌿 Równowaga"
        st.metric("PULS", f"{p_v} BPM")
        st.markdown(f"Nastrój: **{mood_v}**")
    with m4:
        st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")
        st.markdown("Dawka dobowa")

    # --- ZAKŁADKI ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📉 TWOJA ANALIZA", "📋 RAPORT MEDYCZNY", "✨ RYTUAŁY"])

    with tab1:
        cl, cr = st.columns(2)
        with cl:
            valid_w = df_u['Waga'].dropna()
            if not valid_w.empty:
                min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
                fig_w = go.Figure()
                fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], line=dict(color='#7c8370', width=4, shape='spline'), fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)'))
                fig_w.update_layout(title="Dynamika masy ciała", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, yaxis=dict(range=[min_w, max_w], dtick=0.5))
                st.plotly_chart(fig_w, use_container_width=True)
        with cr:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#d98e73', width=3)))
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3)))
            fig_p.update_layout(title="Ciśnienie tętnicze", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_p, use_container_width=True)

    with tab2:
        st.markdown("### Podsumowanie Kliniczne")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"<div class='report-card'><b>Średnie Ciśnienie:</b><br>{int(df_u['Cisnienie_S'].mean())}/{int(df_u['Cisnienie_D'].mean())} mmHg</div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='report-card'><b>Zakres Wagi:</b><br>{df_u['Waga'].min():.1f} - {df_u['Waga'].max():.1f} kg</div>", unsafe_allow_html=True)
        with r3:
            # FIX DLA KEYERROR 0:
            mood_modes = df_u['Mood'].dropna().mode()
            fav_mood = mood_modes[0] if not mood_modes.empty else "🌿 Równowaga"
            st.markdown(f"<div class='report-card'><b>Dominujący Nastrój:</b><br>{fav_mood}</div>", unsafe_allow_html=True)
        st.table(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].tail(10))
        csv = df_u.to_csv(index=False).encode('utf-8')
        st.download_button("📥 POBIERZ CSV", csv, "raport.csv", "text/csv")

    with tab3:
        st.info("💡 Porada SPA: Pomiar wykonuj zawsze na lewej ręce, po 5 minutach ciszy.")
        st.write("- [ ] Medytacja poranna")
        st.write("- [ ] Szklanka wody przed pomiarem")

# --- STOPKA ---
st.markdown("<br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            s_v, d_v, p_v = st.number_input("SYS", value=120), st.number_input("DIA", value=80), st.number_input("Puls", value=70)
            m_v = st.selectbox("Nastrój", ["🌿 Równowaga", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres"])
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_v, "Cisnienie_D": d_v, "Tetno": p_v, "Dawka": ds, "Mood": m_v}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()
with b2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sd = st.selectbox("Data:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sd].iloc[0]
            with st.form("edit"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es, ed = st.number_input("SYS", value=safe_int(row.get('Cisnienie_S'))), st.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sd)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [ew, es, ed]
                    conn.update(data=df_all)
                    st.rerun()
with b3:
    with st.popover("📜 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 30px; opacity: 0.4; font-size: 0.7rem;'>THE SANCTUARY • 2026</div>", unsafe_allow_html=True)

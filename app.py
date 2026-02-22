import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="The Sanctuary 2.1 | Longevity Hub",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# --- 2. ORGANIC SANCTUARY STYLE (FULL CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    /* Główny styl aplikacji */
    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.9), rgba(242, 236, 228, 0.9)), 
                    url('https://images.unsplash.com/photo-1544161515-4ab6ce6db874?q=80&w=2070');
        background-size: cover;
        background-attachment: fixed;
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówek SPA */
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
        font-size: 0.8rem;
        letter-spacing: 5px;
        color: #8c857e;
        margin-bottom: 35px;
        text-transform: uppercase;
    }

    /* Karty Metryk (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 30px !important;
        padding: 22px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }

    /* Przyciski */
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

    /* Tabela i Raporty */
    .report-card {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border-left: 6px solid #7c8370;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA I FUNKCJE POMOCNICZE ---
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

def get_advanced_metrics(sys, dia, weight):
    s, d, w = safe_val(sys), safe_val(dia), safe_val(weight)
    pp = s - d if s > 0 else 0
    map_v = d + (1/3 * pp) if s > 0 else 0
    bmi = w / (1.80 ** 2) if w > 0 else 0 # Wzrost statyczny 1.80m
    return round(pp, 1), round(map_v, 1), round(bmi, 1)

# --- 4. POŁĄCZENIE Z DANYMI (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    # Inicjalizacja kolumny Mood jeśli nie istnieje
    if 'Mood' not in df_all.columns:
        df_all['Mood'] = "🌿 Równowaga"
    
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    # Konwersja numeryczna dla stabilności
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- 5. STRUKTURA INTERFEJSU ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

# Segmentowy wybór profilu
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    pp, map_val, bmi = get_advanced_metrics(last.get('Cisnienie_S'), last.get('Cisnienie_D'), last.get('Waga'))
    
    # --- PANEL GŁÓWNYCH METRYK ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("MASA CIAŁA", f"{safe_val(last.get('Waga')):.1f} kg")
        st.markdown(f"BMI: **{bmi}**")
        
    with m2:
        st.metric("CIŚNIENIE", f"{safe_int(last.get('Cisnienie_S'))}/{safe_int(last.get('Cisnienie_D'))}")
        st.markdown(f"Puls: **{safe_int(last.get('Tetno'))} BPM**")
        
    with m3:
        st.metric("ŚREDNIE (MAP)", f"{map_val} mmHg")
        map_status = "Norma" if 70 <= map_val <= 100 else "Obserwacja"
        st.markdown(f"Status: **{map_status}**")
        
    with m4:
        st.metric("TĘTNA (PP)", f"{int(pp)} mmHg")
        pp_class = "Optymalne" if pp <= 60 else "Podwyższone"
        st.markdown(f"Stan naczyń: **{pp_class}**")

    # --- ZAKŁADKI ANALITYCZNE ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📉 TRENDY PODSTAWOWE", "📊 KARDIOLOGIA PRO", "🩺 RAPORT KLINICZNY"])

    with tab1:
        col_left, col_right = st.columns(2)
        with col_left:
            # WYKRES WAGI Z EFEKTEM LUPY
            valid_w = df_u['Waga'].dropna()
            if not valid_w.empty:
                min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
                fig_w = go.Figure()
                fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], name="Waga", 
                                           line=dict(color='#7c8370', width=4, shape='spline'),
                                           fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)'))
                fig_w.update_layout(title="Dynamika masy ciała (kg)", paper_bgcolor='rgba(0,0,0,0)', 
                                    plot_bgcolor='rgba(0,0,0,0)', height=400, yaxis=dict(range=[min_w, max_w]))
                st.plotly_chart(fig_w, use_container_width=True)
        
        with col_right:
            # KLASYCZNY WYKRES CIŚNIENIA
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#d98e73', width=3)))
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3)))
            fig_p.update_layout(title="Trendy ciśnienia (mmHg)", paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_p, use_container_width=True)

    with tab2:
        st.markdown("#### Zaawansowana Hemodynamika (Analiza MAP i PP)")
        
        
        fig_adv = go.Figure()
        df_u['PP_v'] = df_u['Cisnienie_S'] - df_u['Cisnienie_D']
        df_u['MAP_v'] = df_u['Cisnienie_D'] + (1/3 * df_u['PP_v'])
        
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['MAP_v'], name="MAP (Średnie)", line=dict(color='#7c8370', width=4, shape='spline')))
        fig_adv.add_trace(go.Scatter(x=df_u['Data'], y=df_u['PP_v'], name="PP (Ciśnienie Tętna)", line=dict(color='#d98e73', dash='dot')))
        
        fig_adv.update_layout(title="Obciążenie naczyń i perfuzja", paper_bgcolor='rgba(0,0,0,0)', 
                             plot_bgcolor='rgba(0,0,0,0)', height=450, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_adv, use_container_width=True)
        
        st.info("💡 MAP (Mean Arterial Pressure) to średnie ciśnienie napędowe krwi. PP (Pulse Pressure) powyżej 60 mmHg może sugerować sztywnienie tętnic.")

    with tab3:
        st.markdown("### Historia pomiarów i eksport")
        st.dataframe(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka', 'Mood']].sort_values("Data", ascending=False), use_container_width=True)
        
        csv = df_u.to_csv(index=False).encode('utf-8')
        st.download_button("📥 POBIERZ DANE DO EXCEL (CSV)", csv, f"raport_{user}_{datetime.now().date()}.csv", "text/csv")

# --- 6. PANEL AKCJI (STOPKA) ---
st.markdown("<br><br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)

with b1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add_form"):
            new_date = st.date_input("Data pomiaru", datetime.now())
            new_w = st.number_input("Waga (kg)", value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0, step=0.1)
            c1, c2, c3 = st.columns(3)
            new_s = c1.number_input("SYS", value=120)
            new_d = c2.number_input("DIA", value=80)
            new_p = c3.number_input("Puls", value=70)
            new_mood = st.selectbox("Nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres", "🌊 Równowaga"])
            new_ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            
            if st.form_submit_button("ZAPISZ W DZIENNIKU"):
                new_data = pd.DataFrame([{
                    "Użytkownik": user, "Data": new_date, "Waga": new_w, 
                    "Cisnienie_S": new_s, "Cisnienie_D": new_d, "Tetno": new_p, 
                    "Dawka": new_ds, "Mood": new_mood
                }])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.rerun()

with b2:
    with st.popover("✨ KOREKTA DANYCH", use_container_width=True):
        if not df_u.empty:
            sel_date = st.selectbox("Wybierz datę do edycji:", df_u['Data'].tolist()[::-1])
            row_edit = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_form"):
                edit_w = st.number_input("Popraw wagę", value=safe_val(row_edit.get('Waga')))
                edit_s = st.number_input("Popraw SYS", value=safe_int(row_edit.get('Cisnienie_S')))
                edit_d = st.number_input("Popraw DIA", value=safe_int(row_edit.get('Cisnienie_D')))
                if st.form_submit_button("ZAKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [edit_w, edit_s, edit_d]
                    conn.update(data=df_all)
                    st.rerun()

with b3:
    st.markdown("<div style='text-align: center; opacity: 0.5; font-size: 0.7rem;'>THE SANCTUARY v2.1<br>Longevity Hub</div>", unsafe_allow_html=True)

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="The Sanctuary 2.0 | Vital Rituals",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed"
)

# --- ORGANIC SANCTUARY STYLE (FULL CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    /* Tło i ogólna estetyka */
    .stApp {
        background: linear-gradient(rgba(242, 236, 228, 0.85), rgba(242, 236, 228, 0.85)), 
                    url('https://images.unsplash.com/photo-1540555700478-4be289fbecef?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówek luksusowy */
    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 40px 0 10px 0;
        letter-spacing: -1px;
    }

    .sanctuary-subtitle {
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 4px;
        color: #8c857e;
        margin-bottom: 40px;
        text-transform: uppercase;
    }

    /* Karty Metryk - Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 35px !important;
        padding: 25px !important;
        box-shadow: 0 12px 35px rgba(0,0,0,0.03) !important;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    /* Statusy zdrowotne */
    .status-norm { color: #7c8370; font-weight: 600; border-bottom: 2px solid #7c8370; }
    .status-warn { color: #d98e73; font-weight: 600; border-bottom: 2px solid #d98e73; }
    .status-alert { color: #b04b4b; font-weight: 600; border-bottom: 2px solid #b04b4b; }

    /* Zakładki */
    .stTabs [data-baseweb="tab-list"] {
        gap: 40px;
        justify-content: center;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
        background: transparent !important;
        color: #8c857e !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #5d5750 !important;
        font-weight: 600 !important;
        border-bottom: 3px solid #7c8370 !important;
    }

    /* Przyciski luksusowe */
    .stButton>button {
        background: #7c8370 !important;
        color: #fdfcfb !important;
        border-radius: 50px !important;
        padding: 15px 40px !important;
        font-family: 'Inter', sans-serif;
        border: none !important;
        transition: all 0.4s ease;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: #5d6354 !important;
        transform: scale(1.02);
        box-shadow: 0 10px 25px rgba(124, 131, 112, 0.3);
    }

    /* Raport kliniczny */
    .report-card {
        background: rgba(255, 255, 255, 0.8);
        padding: 25px;
        border-radius: 20px;
        border-left: 6px solid #7c8370;
        margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE (LOGIKA I BEZPIECZEŃSTWO) ---
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
    if bmi < 30: return bmi, "Nadwaga", "status-warn"
    return bmi, "Otyłość", "status-alert"

# --- POŁĄCZENIE Z GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    # Konwersja typów
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- NAGŁÓWEK ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

# Wybór profilu (Natalia/Piotr)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- PANEL METRYK ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        w_val = safe_val(last.get('Waga'))
        bmi_v, bmi_c, bmi_s = get_bmi(w_val)
        st.metric("MASA CIAŁA", f"{w_val:.1f} kg")
        st.markdown(f"<span class='{bmi_s}'>{bmi_c} (BMI: {bmi_v:.1f})</span>", unsafe_allow_html=True)
    
    with m2:
        sys, dia = safe_int(last.get('Cisnienie_S')), safe_int(last.get('Cisnienie_D'))
        bp_c, bp_s = get_bp_status(sys, dia)
        st.metric("CIŚNIENIE", f"{sys}/{dia}")
        st.markdown(f"<span class='{bp_s}'>{bp_c}</span>", unsafe_allow_html=True)
        
    with m3:
        puls = safe_int(last.get('Tetno'))
        mood = last.get('Mood', '🌿 Równowaga')
        st.metric("PULS", f"{puls} BPM")
        st.markdown(f"Nastrój: **{mood}**")
        
    with m4:
        st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")
        st.markdown("Dawka dobowa")

    # --- ZAKŁADKI ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    tab_graph, tab_report, tab_rituals = st.tabs(["📉 TWOJA ANALIZA", "📋 RAPORT MEDYCZNY", "✨ RYTUAŁY"])

    with tab_graph:
        c_left, c_right = st.columns(2)
        
        with c_left:
            valid_w = df_u['Waga'].dropna()
            if not valid_w.empty:
                # EFEKT LUPY DLA WAGI
                min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
                fig_w = go.Figure()
                fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], line=dict(color='#7c8370', width=4, shape='spline'),
                                           fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)', mode='lines+markers'))
                fig_w.update_layout(title="Dynamika masy ciała", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                    height=400, yaxis=dict(range=[min_w, max_w], gridcolor='rgba(0,0,0,0.05)', dtick=0.5))
                st.plotly_chart(fig_w, use_container_width=True)

        with c_right:
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#d98e73', width=3, shape='spline')))
            fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3, shape='spline')))
            fig_v.update_layout(title="Monitoring kardiologiczny", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_v, use_container_width=True)

    with tab_report:
        st.markdown("### Podsumowanie dla lekarza prowadzącego")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"<div class='report-card'><b>Średnie ciśnienie:</b><br>{int(df_u['Cisnienie_S'].mean())}/{int(df_u['Cisnienie_D'].mean())} mmHg</div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='report-card'><b>Zakres wagi:</b><br>{df_u['Waga'].min():.1f} - {df_u['Waga'].max():.1f} kg</div>", unsafe_allow_html=True)
        with r3:
            fav_mood = df_u['Mood'].mode()[0] if 'Mood' in df_u and not df_u['Mood'].empty else "Brak danych"
            st.markdown(f"<div class='report-card'><b>Dominujący nastrój:</b><br>{fav_mood}</div>", unsafe_allow_html=True)
        
        st.markdown("#### Ostatnie 14 pomiarów")
        st.table(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].sort_values("Data", ascending=False).head(14))
        
        # EKSPORT DO CSV
        csv_data = df_u.to_csv(index=False).encode('utf-8')
        st.download_button("📥 POBIERZ PEŁNĄ HISTORIĘ (CSV)", csv_data, f"sanctuary_report_{user}.csv", "text/csv")

    with tab_rituals:
        st.markdown("#### 🧘 Sugestie Wellness")
        st.info("💡 Porada: Pomiary ciśnienia są najdokładniejsze rano, przed posiłkiem i kawą.")
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.write("**Twoje zdrowe nawyki:**")
            st.write("- [ ] 10 minut medytacji")
            st.write("- [ ] Szklanka ciepłej wody z cytryną")
            st.write("- [ ] Krótki spacer")
        with c_v2:
            st.write("**Notatki:**")
            st.caption("Użyj pola notatek w nowym wpisie, aby śledzić reakcje na dawkowanie.")

# --- STOPKA Z PRZYCISKAMI AKCJI ---
st.markdown("<br><br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)

with b1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add_zen_form"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            sys_v = st.number_input("SYS (Skurczowe)", value=120)
            dia_v = st.number_input("DIA (Rozkurczowe)", value=80)
            hr_v = st.number_input("Puls", value=70)
            mood_v = st.selectbox("Twój nastrój", ["🌿 Równowaga", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres", "🌊 Spokój"])
            ds_v = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ RYTUAŁ"):
                new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys_v, "Cisnienie_D": dia_v, "Tetno": hr_v, "Dawka": ds_v, "Mood": mood_v}])
                conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
                st.rerun()

with b2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_date = st.selectbox("Wybierz datę:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_zen_form"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es = st.number_input("SYS", value=safe_int(row.get('Cisnienie_S')))
                ed = st.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                if st.form_submit_button("AKTUALIZUJ DANE"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [ew, es, ed]
                    conn.update(data=df_all)
                    st.rerun()

with b3:
    with st.popover("📜 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

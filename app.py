import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="The Sanctuary 2.1 | Longevity Hub", layout="wide", page_icon="🌿")

# --- CSS: ZEN CLINIC STYLE ---
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
        font-family: 'Playfair Display', serif; font-size: 3.5rem; font-style: italic;
        text-align: center; color: #4a4540; padding: 20px 0 0 0;
    }
    .sanctuary-subtitle {
        text-align: center; font-size: 0.8rem; letter-spacing: 5px; color: #8c857e;
        margin-bottom: 30px; text-transform: uppercase;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(15px); border-radius: 25px !important;
        padding: 20px !important; border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }
    .analysis-card {
        background: rgba(124, 131, 112, 0.1); padding: 15px; border-radius: 15px;
        border-left: 4px solid #7c8370; margin: 10px 0; font-size: 0.9rem;
    }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA MATEMATYCZNA ---
def safe_val(val, default=0.0):
    try: return float(val) if pd.notnull(val) and val != "" else float(default)
    except: return float(default)

def calc_advanced_bp(sys, dia):
    s, d = safe_val(sys), safe_val(dia)
    pp = s - d
    map_v = d + (1/3 * pp)
    return round(pp, 1), round(map_v, 1)

# --- DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    if 'Mood' not in df_all.columns: df_all['Mood'] = "🌿 Równowaga"
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns: df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
st.markdown("<div class='sanctuary-subtitle'>Advanced Longevity Monitoring</div>", unsafe_allow_html=True)

user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    pp, map_val = calc_advanced_bp(last['Cisnienie_S'], last['Cisnienie_D'])
    
    # --- METRYKI GŁÓWNE ---
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("MASA CIAŁA", f"{safe_val(last['Waga']):.1f} kg")
    with m2: st.metric("CIŚNIENIE (SYS/DIA)", f"{int(last['Cisnienie_S'])}/{int(last['Cisnienie_D'])}")
    with m3: st.metric("ŚREDNIE TĘTNICZE (MAP)", f"{map_val} mmHg")
    with m4: st.metric("CIŚNIENIE TĘTNA (PP)", f"{int(pp)} mmHg")

    tab1, tab2, tab3 = st.tabs(["📊 KARDIOLOGIA", "🩺 RAPORT KLINICZNY", "🌿 RYTUAŁY"])

    with tab1:
        st.markdown("#### Zaawansowana Analiza Przepływu")
        # Wykres MAP i Pulse Pressure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'] - df_u['Cisnienie_D'], 
                                 name="Pulse Pressure (PP)", line=dict(color='#d98e73', dash='dot')))
        map_series = df_u['Cisnienie_D'] + (1/3 * (df_u['Cisnienie_S'] - df_u['Cisnienie_D']))
        fig.add_trace(go.Scatter(x=df_u['Data'], y=map_series, name="MAP (Średnie)", line=dict(color='#7c8370', width=4)))
        
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Górna norma MAP")
        fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Norma PP")
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)
        
        # Wskazówki automatyczne
        c1, c2 = st.columns(2)
        with c1:
            if pp > 60:
                st.warning("⚠️ Wysokie Ciśnienie Tętna (PP): Może to sugerować zwiększoną sztywność naczyń. Skonsultuj to z lekarzem przy najbliższej wizycie.")
            else:
                st.success("✅ Ciśnienie tętna w normie. Twoje naczynia zachowują dobrą elastyczność.")
        with c2:
            st.info(f"💡 Twój aktualny wskaźnik MAP to {map_val}. Norma wynosi zazwyczaj 70-100 mmHg.")

    with tab2:
        st.markdown("### Zestawienie dla Specjalisty")
        # Obliczanie średnich z ostatnich 7 dni
        last_7 = df_u.tail(7)
        avg_pp = (last_7['Cisnienie_S'] - last_7['Cisnienie_D']).mean()
        
        st.markdown(f"""
        <div class='report-card'>
            <b>Średnie PP (7 dni):</b> {avg_pp:.1f} mmHg | 
            <b>Średnie MAP (7 dni):</b> {map_series.tail(7).mean():.1f} mmHg | 
            <b>Stabilność Pulsu:</b> {int(last_7['Tetno'].std())} (odchylenie)
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga']].sort_values("Data", ascending=False), use_container_width=True)
        
    with tab3:
        st.markdown("#### Rytuały wspierające układ krążenia")
        st.write("🌿 **Magnez i Potas:** Zadbaj o podaż w diecie, aby wspierać elastyczność naczyń.")
        st.write("🌊 **Zimne prysznice:** Świetny trening dla Twoich tętnic (PP).")
        st.write("🧘 **Oddech 4-7-8:** Wykonaj teraz 3 cykle, aby naturalnie obniżyć MAP.")

# --- AKCJE ---
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    with st.popover("🧘 DODAJ POMIAR", use_container_width=True):
        with st.form("add"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0, step=0.1)
            s, di, p = st.number_input("SYS", value=120), st.number_input("DIA", value=80), st.number_input("Puls", value=70)
            mood = st.selectbox("Nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres"])
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s, "Cisnienie_D": di, "Tetno": p, "Dawka": ds, "Mood": mood}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with col2:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_d = st.selectbox("Data:", df_u['Data'].tolist()[::-1])
            if st.form_submit_button("USUŃ TEN WPIS (OPCJA)"): # Uproszczone dla bezpieczeństwa
                st.warning("Funkcja usuwania w Sheets wymaga ostrożności.")
with col3:
    csv = df_u.to_csv(index=False).encode('utf-8')
    st.download_button("📥 POBIERZ RAPORT", csv, "sanctuary_full_report.csv", "text/csv", use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.3; font-size: 0.7rem;'>THE SANCTUARY • BIOMETRYCZNA HARMONIA</div>", unsafe_allow_html=True)

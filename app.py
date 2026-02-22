import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="The Sanctuary 2.0", layout="wide", page_icon="🌿")

# --- CSS: ORGANIC LUXURY & MOOD COLORS ---
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
        font-family: 'Playfair Display', serif; font-size: 3.8rem; font-style: italic;
        text-align: center; color: #4a4540; padding: 20px 0; letter-spacing: -1px;
    }

    /* Karty Metryk */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px); border-radius: 30px !important;
        padding: 20px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }

    /* Style dla statusów zdrowia */
    .status-norm { color: #7c8370; font-weight: 600; }
    .status-warn { color: #d98e73; font-weight: 600; }
    .status-alert { color: #b04b4b; font-weight: 600; }

    .report-card {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 5px solid #7c8370; margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def safe_val(val, default=0.0):
    try: return float(val) if pd.notnull(val) and val != "" else float(default)
    except: return float(default)

def get_bp_status(s, d):
    if s < 120 and d < 80: return "Optymalne", "status-norm"
    if s < 130 and d < 85: return "Prawidłowe", "status-norm"
    if s < 140 or d < 90: return "Wysokie Prawidłowe", "status-warn"
    return "Nadciśnienie", "status-alert"

def get_bmi(weight, height=1.80): # Założyłem 180cm, można dodać input w profilu
    bmi = weight / (height ** 2)
    if bmi < 18.5: return bmi, "Niedowaga", "status-warn"
    if bmi < 25: return bmi, "Waga Prawidłowa", "status-norm"
    return bmi, "Nadwaga", "status-warn"

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    num_cols = ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']
    for col in num_cols:
        if col in df_all.columns: df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- MAIN UI ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- METRICS GRID ---
    m1, m2, m3, m4 = st.columns(4)
    
    # Waga & BMI
    bmi_val, bmi_cat, bmi_class = get_bmi(safe_val(last.get('Waga')))
    with m1:
        st.metric("MASA CIAŁA", f"{safe_val(last.get('Waga')):.1f} kg")
        st.markdown(f"<span class='{bmi_class}'>{bmi_cat} (BMI: {bmi_val:.1f})</span>", unsafe_allow_html=True)
    
    # Ciśnienie
    s, d = int(safe_val(last.get('Cisnienie_S'), 120)), int(safe_val(last.get('Cisnienie_D'), 80))
    bp_cat, bp_class = get_bp_status(s, d)
    with m2:
        st.metric("CIŚNIENIE", f"{s}/{d}")
        st.markdown(f"<span class='{bp_class}'>{bp_cat}</span>", unsafe_allow_html=True)
        
    # Tętno & Nastrój
    mood = last.get('Mood', '🌿')
    with m3:
        st.metric("PULS", f"{int(safe_val(last.get('Tetno'), 70))} BPM")
        st.markdown(f"Nastrój: {mood}")
        
    # Dawka
    with m4:
        st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")
        st.markdown("Dawka dobowa")

    # --- TABS ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📉 ANALIZA TRENDÓW", "📋 RAPORT MEDYCZNY", "✨ RYTUAŁY"])

    with tab1:
        col_w, col_p = st.columns([1, 1])
        with col_w:
            valid_w = df_u['Waga'].dropna()
            min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], name="Waga", line=dict(color='#7c8370', width=4, shape='spline'), fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.1)'))
            fig_w.update_layout(title="Dynamika masy ciała", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, yaxis=dict(range=[min_w, max_w], gridcolor='rgba(0,0,0,0.05)'))
            st.plotly_chart(fig_w, use_container_width=True)
        
        with col_p:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="SYS", line=dict(color='#d98e73', width=3)))
            fig_p.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="DIA", line=dict(color='#7c8370', width=3)))
            fig_p.update_layout(title="Monitoring ciśnienia", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, legend=dict(orientation="h"))
            st.plotly_chart(fig_p, use_container_width=True)

    with tab2:
        st.markdown("### Podsumowanie dla lekarza prowadzącego")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='report-card'><b>Średnie Ciśnienie:</b><br>{int(df_u['Cisnienie_S'].mean())}/{int(df_u['Cisnienie_D'].mean())} mmHg</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='report-card'><b>Zmienność wagi:</b><br>{df_u['Waga'].min():.1f} - {df_u['Waga'].max():.1f} kg</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='report-card'><b>Najczęstszy nastrój:</b><br>{df_u['Mood'].mode()[0] if 'Mood' in df_u else '🌿'}</div>", unsafe_allow_html=True)
        
        st.table(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].tail(14))
        
        csv = df_u.to_csv(index=False).encode('utf-8')
        st.download_button("📥 POBIERZ PEŁNE DANE (CSV)", csv, f"raport_{user}_{datetime.now().date()}.csv", "text/csv")

    with tab3:
        st.info("💡 Porada Zen: Pamiętaj, aby pomiaru ciśnienia dokonywać po 5 minutach odpoczynku w pozycji siedzącej.")
        st.markdown("#### Twoje Rytuały")
        st.write("- Pij min. 2L wody dziennie 💧")
        st.write("- 10 minut medytacji po porannym pomiarze 🧘")

# --- ACTIONS ---
st.markdown("<br>", unsafe_allow_html=True)
ca, ce, ch = st.columns(3)

with ca:
    with st.popover("🧘 NOWY WPIS", use_container_width=True):
        with st.form("add_zen"):
            d = st.date_input("Data", datetime.now())
            w = st.number_input("Waga", value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0, step=0.1)
            sys_v = st.number_input("SYS", value=120)
            dia_v = st.number_input("DIA", value=80)
            hr_v = st.number_input("Puls", value=70)
            mood_v = st.selectbox("Twój nastrój", ["🌿 Spokój", "☀️ Energia", "☁️ Zmęczenie", "⚡ Stres", "🌊 Równowaga"])
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ W DZIENNIKU"):
                new_data = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": sys_v, "Cisnienie_D": dia_v, "Tetno": hr_v, "Dawka": ds, "Mood": mood_v}])
                conn.update(data=pd.concat([df_all, new_data], ignore_index=True))
                st.rerun()

with ce:
    with st.popover("✨ KOREKTA", use_container_width=True):
        if not df_u.empty:
            sel_d = st.selectbox("Wybierz datę:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_d].iloc[0]
            with st.form("edit_zen"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                es = st.number_input("SYS", value=int(safe_val(row.get('Cisnienie_S'))))
                ed = st.number_input("DIA", value=int(safe_val(row.get('Cisnienie_D'))))
                if st.form_submit_button("AKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_d)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D']] = [ew, es, ed]
                    conn.update(data=df_all)
                    st.rerun()

with ch:
    with st.popover("📜 HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 30px; opacity: 0.5; font-size: 0.8rem;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

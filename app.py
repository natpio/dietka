import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="The Sanctuary | Vital Rituals", layout="wide", page_icon="🧘")

# --- ORGANIC SANCTUARY CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    /* Tło luksusowego gabinetu */
    .stApp {
        background: radial-gradient(circle at top right, #f2ece4, #e8e0d5);
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    /* Nagłówek w stylu boutique hotel */
    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 30px 0;
        letter-spacing: -1px;
    }

    /* Szklane, organiczne karty metryk */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 35px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }

    /* Zakładki (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        justify-content: center;
        border-bottom: none;
    }

    .stTabs [data-baseweb="tab"] {
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
        background: transparent !important;
        border: none !important;
        color: #8c857e !important;
    }

    .stTabs [aria-selected="true"] {
        color: #5d5750 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #7c8370 !important;
    }

    /* Przyciski luksusowe */
    .stButton>button {
        background: #7c8370 !important;
        color: #fdfcfb !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        letter-spacing: 1px;
        border: none !important;
        transition: all 0.4s ease;
    }

    .stButton>button:hover {
        background: #5d6354 !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(124, 131, 112, 0.2);
    }

    /* Estetyka raportu lekarskiego */
    .report-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid #7c8370;
        margin-bottom: 20px;
    }

    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE (BEZPIECZEŃSTWO DANYCH) ---
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

# --- POŁĄCZENIE Z GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_all = conn.read(ttl="0")

if not df_all.empty:
    # Czyszczenie nazw kolumn
    df_all.columns = [c.strip() for c in df_all.columns]
    # Konwersja daty
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    # Konwersja typów numerycznych dla całej bazy
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI CONTENT ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)

# Wybór profilu
user = st.segmented_control("", ["Piotr", "Natalia"], default="Piotr")
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- GŁÓWNE METRYKI ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("RÓWNOWAGA MASY", f"{safe_val(last.get('Waga')):.1f} kg")
    with m2:
        sys = safe_int(last.get('Cisnienie_S'))
        dia = safe_int(last.get('Cisnienie_D'))
        st.metric("RYTM SERCA", f"{sys}/{dia}" if sys and dia else "--")
    with m3:
        hr = safe_int(last.get('Tetno'))
        st.metric("PULS SPOKOJU", f"{hr} BPM" if hr else "--")
    with m4:
        st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- ZAKŁADKI ANALITYCZNE ---
    tab_w, tab_v, tab_r = st.tabs(["📉 TWOJA SYLWETKA", "❤️ TWOJA WITALNOŚĆ", "📋 RAPORT MEDYCZNY"])

    # 1. ANALIZA WAGI (Z DOPASOWANĄ SKALĄ)
    with tab_w:
        min_w = safe_val(df_u['Waga'].min()) - 0.5
        max_w = safe_val(df_u['Waga'].max()) + 0.5
        
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df_u['Data'], y=df_u['Waga'],
            line=dict(color='#7c8370', width=4, shape='spline'),
            fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.05)',
            mode='lines+markers', marker=dict(size=8, color='#7c8370', line=dict(width=2, color='white'))
        ))
        fig_w.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=450, margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, color='#8c857e'),
            yaxis=dict(range=[min_w, max_w], gridcolor='rgba(0,0,0,0.05)', color='#8c857e', dtick=0.5)
        )
        st.plotly_chart(fig_w, use_container_width=True)

    # 2. MONITORING KARDIOLOGICZNY
    with tab_v:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe (SYS)", line=dict(color='#c2b8ad', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe (DIA)", line=dict(color='#7c8370', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Puls (BPM)", mode='markers', marker=dict(color='#d4af37', size=10, opacity=0.6)))
        fig_v.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=450, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            xaxis=dict(showgrid=False, color='#8c857e'),
            yaxis=dict(gridcolor='rgba(0,0,0,0.05)', color='#8c857e')
        )
        st.plotly_chart(fig_v, use_container_width=True)

    # 3. RAPORT DLA LEKARZA
    with tab_r:
        st.markdown("### 🩺 Podsumowanie kliniczne")
        st.write("Wygenerowano automatycznie na podstawie dziennika Sanctuary.")
        
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            avg_sys = int(df_u['Cisnienie_S'].mean())
            avg_dia = int(df_u['Cisnienie_D'].mean())
            st.markdown(f"<div class='report-card'><b>Średnie ciśnienie:</b><br><span style='font-size:20px;'>{avg_sys}/{avg_dia} mmHg</span></div>", unsafe_allow_html=True)
        with c_r2:
            avg_weight = df_u['Waga'].mean()
            st.markdown(f"<div class='report-card'><b>Średnia masa ciała:</b><br><span style='font-size:20px;'>{avg_weight:.2f} kg</span></div>", unsafe_allow_html=True)
        with c_r3:
            avg_hr = int(df_u['Tetno'].mean())
            st.markdown(f"<div class='report-card'><b>Średni puls:</b><br><span style='font-size:20px;'>{avg_hr} BPM</span></div>", unsafe_allow_html=True)
        
        st.markdown("#### Ostatnie pomiary (Tabela lekarska)")
        report_df = df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].sort_values("Data", ascending=False)
        report_df.columns = ['Data', 'SYS', 'DIA', 'Puls', 'Waga (kg)', 'Dawka (mg)']
        st.table(report_df.head(14)) # Ostatnie 2 tygodnie

# --- PANEL AKCJI (STOPKA) ---
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        with st.form("add_form"):
            d = st.date_input("Data pomiaru", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            cs, cd, ct = st.columns(3)
            s_v = cs.number_input("SYS", value=120)
            d_v = cd.number_input("DIA", value=80)
            t_v = ct.number_input("Puls", value=70)
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            note = st.text_input("Notatki (opcjonalnie)")
            if st.form_submit_button("DODAJ DO DZIENNIKA"):
                new_row = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_v, "Cisnienie_D": d_v, "Tetno": t_v, "Dawka": ds, "Notatki": note}])
                conn.update(data=pd.concat([df_all, new_row], ignore_index=True))
                st.rerun()

with col2:
    with st.popover("✨ KOREKTA DANYCH", use_container_width=True):
        if not df_u.empty:
            dates = df_u['Data'].tolist()
            sel_date = st.selectbox("Wybierz dzień do edycji:", dates[::-1])
            row_edit = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_form"):
                ew = st.number_input("Popraw wagę", value=safe_val(row_edit.get('Waga')))
                es, ed, et = st.columns(3)
                esys = es.number_input("SYS", value=safe_int(row_edit.get('Cisnienie_S')))
                edia = ed.number_input("DIA", value=safe_int(row_edit.get('Cisnienie_D')))
                etet = et.number_input("Puls", value=safe_int(row_edit.get('Tetno')))
                edose = st.selectbox("Popraw dawkę", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                     index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(safe_val(row_edit.get('Dawka'))) if safe_val(row_edit.get('Dawka')) in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0] else 0)
                if st.form_submit_button("ZAKTUALIZUJ"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']] = [ew, esys, edia, etet, edose]
                    conn.update(data=df_all)
                    st.rerun()

with col3:
    with st.popover("📜 PEŁNA HISTORIA", use_container_width=True):
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; letter-spacing: 3px; color: #4a4540;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="The Sanctuary | Your Zen Journey", layout="wide", page_icon="🧘‍♀️")

# --- ORGANIC SANCTUARY CSS WITH GRAPHICS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@0;1&family=Inter:wght@300;400;600&display=swap');

    /* Główne tło - subtelna mgiełka zen */
    .stApp {
        background: url(https://via.placeholder.com/1920x1080/f2ece4/e8e0d5?text=Zen+Garden+Mist); /* Placeholder: Imagine a soft, blurry zen garden with misty light */
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #5d5750;
        font-family: 'Inter', sans-serif;
    }

    .sanctuary-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.8rem; /* Większy nagłówek */
        font-style: italic;
        text-align: center;
        color: #4a4540;
        padding: 40px 0 20px 0; /* Więcej przestrzeni */
        letter-spacing: -1px;
        position: relative;
        z-index: 1; /* Nad elementami tła */
        text-shadow: 0 2px 5px rgba(0,0,0,0.05); /* Delikatny cień */
    }

    /* Szklane, organiczne karty metryk */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 40px !important; /* Bardziej zaokrąglone */
        padding: 30px !important; /* Większy padding */
        box-shadow: 0 15px 40px rgba(0,0,0,0.03) !important; /* Subtelniejszy cień */
        backdrop-filter: blur(8px); /* Efekt rozmycia za kartą */
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s ease; /* Płynne przejścia */
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px); /* Lekkie uniesienie na hover */
        box-shadow: 0 20px 50px rgba(0,0,0,0.05) !important;
    }

    /* Zakładki (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 35px; /* Więcej miejsca między zakładkami */
        justify-content: center;
        border-bottom: none;
        margin-top: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        text-transform: uppercase;
        letter-spacing: 2.5px;
        font-size: 0.85rem;
        background: rgba(255,255,255,0.2) !important; /* Subtelne tło dla nieaktywnych */
        border: none !important;
        color: #8c857e !important;
        padding: 12px 25px;
        border-radius: 20px 20px 0 0;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #5d5750 !important;
        font-weight: 600 !important;
        background: rgba(255,255,255,0.7) !important; /* Aktywna zakładka jaśniejsza */
        border-bottom: 3px solid #7c8370 !important; /* Grubsza linia */
        transform: translateY(-2px);
    }

    /* Przyciski luksusowe */
    .stButton>button {
        background: #7c8370 !important;
        color: #fdfcfb !important;
        border-radius: 50px !important;
        padding: 15px 35px !important; /* Większe przyciski */
        font-weight: 400; /* Delikatniejszy tekst */
        letter-spacing: 1.5px;
        border: none !important;
        transition: all 0.5s ease;
    }
    .stButton>button:hover {
        background: #5d6354 !important;
        transform: translateY(-3px); /* Większe uniesienie */
        box-shadow: 0 15px 25px rgba(124, 131, 112, 0.3);
    }

    /* Estetyka raportu lekarskiego */
    .report-card {
        background: rgba(255, 255, 255, 0.6);
        padding: 25px;
        border-radius: 20px;
        border-left: 5px solid #7c8370;
        margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }

    /* Sekcje wizualne - obrazy generowane przez AI */
    .visual-section {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
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
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all['Data'] = pd.to_datetime(df_all['Data']).dt.date
    for col in ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# --- UI CONTENT ---
st.markdown("<div class='sanctuary-title'>The Sanctuary</div>", unsafe_allow_html=True)

# --- WIZUALNE WPROWADZENIE ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 30px; opacity: 0.8;">
        <p style="font-size: 1.1rem; color: #6a645e;">
            Witaj w Twojej przestrzeni równowagi. Zanurz się w podróży ku harmonii ciała i umysłu.
        </p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("

") # Obrazek: Delikatny, rozmyty widok kamieni zen ułożonych w stos, w tle bambus i mgiełka.

# Wybór profilu
st.markdown("<br>", unsafe_allow_html=True)
user = st.segmented_control("Wybierz swój profil:", ["Piotr", "Natalia"], default="Piotr") # Zmieniona etykieta
df_u = df_all[df_all['Użytkownik'] == user].sort_values("Data") if not df_all.empty else pd.DataFrame()

if not df_u.empty:
    last = df_u.iloc[-1]
    
    # --- GŁÓWNE METRYKI ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1: 
        st.markdown(f"<p style='text-align:center; font-size:0.9rem; color:#8c857e; margin-bottom:5px;'>Ostatnia waga</p>", unsafe_allow_html=True)
        st.metric("RÓWNOWAGA MASY", f"{safe_val(last.get('Waga')):.1f} kg")
    with m2:
        st.markdown(f"<p style='text-align:center; font-size:0.9rem; color:#8c857e; margin-bottom:5px;'>Ostatnie ciśnienie</p>", unsafe_allow_html=True)
        sys = safe_int(last.get('Cisnienie_S'))
        dia = safe_int(last.get('Cisnienie_D'))
        st.metric("RYTM SERCA", f"{sys}/{dia}" if sys and dia else "--")
    with m3:
        st.markdown(f"<p style='text-align:center; font-size:0.9rem; color:#8c857e; margin-bottom:5px;'>Ostatni puls</p>", unsafe_allow_html=True)
        hr = safe_int(last.get('Tetno'))
        st.metric("PULS SPOKOJU", f"{hr} BPM" if hr else "--")
    with m4: 
        st.markdown(f"<p style='text-align:center; font-size:0.9rem; color:#8c857e; margin-bottom:5px;'>Aktualna dawka</p>", unsafe_allow_html=True)
        st.metric("PROTOKÓŁ", f"{safe_val(last.get('Dawka'))} mg")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- WIZUALNA SEKCJA WYKRESÓW ---
    st.markdown("""
        <div class="visual-section" style="text-align: center;">
            <h3 style="color: #6a645e; font-family: 'Playfair Display', serif; font-weight: normal; font-style: italic;">
                Ścieżka Postępu
            </h3>
            <p style="font-size: 0.9rem; color: #8c857e; margin-bottom: 20px;">
                Tutaj wizualizujemy Twoją drogę ku lepszemu samopoczuciu.
            </p>
            
    """, unsafe_allow_html=True)
    st.markdown("

") # Obrazek: Grafika przedstawiająca subtelne, płynne linie przypominające fale wody, w tle zachód słońca.
    st.markdown("</div>", unsafe_allow_html=True) # Zamknięcie visual-section

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ZAKŁADKI ANALITYCZNE ---
    tab_w, tab_v, tab_r = st.tabs(["📉 TWOJA SYLWETKA", "❤️ TWOJA WITALNOŚĆ", "📋 RAPORT MEDYCZNY"])

    with tab_w:
        valid_w = df_u['Waga'].dropna()
        if not valid_w.empty:
            min_w, max_w = valid_w.min() - 0.5, valid_w.max() + 0.5
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Waga'], line=dict(color='#7c8370', width=4, shape='spline'),
                                       fill='tozeroy', fillcolor='rgba(124, 131, 112, 0.05)', mode='lines+markers'))
            fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, 
                                yaxis=dict(range=[min_w, max_w], gridcolor='rgba(0,0,0,0.05)', dtick=0.5, title_text="Waga (kg)"))
            st.plotly_chart(fig_w, use_container_width=True)

    with tab_v:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_S'], name="Skurczowe (SYS)", line=dict(color='#c2b8ad', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Cisnienie_D'], name="Rozkurczowe (DIA)", line=dict(color='#7c8370', width=3, shape='spline')))
        fig_v.add_trace(go.Scatter(x=df_u['Data'], y=df_u['Tetno'], name="Puls (BPM)", mode='markers', marker=dict(color='#d4af37', size=10, opacity=0.6)))
        fig_v.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
                            yaxis=dict(gridcolor='rgba(0,0,0,0.05)', title_text="Wartość"))
        st.plotly_chart(fig_v, use_container_width=True)

    with tab_r:
        st.markdown("""
            <div class="visual-section" style="text-align: center;">
                <h3 style="color: #6a645e; font-family: 'Playfair Display', serif; font-weight: normal; font-style: italic;">
                    Dla Twojego Lekarza
                </h3>
                <p style="font-size: 0.9rem; color: #8c857e; margin-bottom: 20px;">
                    Przejrzyste podsumowanie Twojej podróży zdrowotnej.
                </p>
        """, unsafe_allow_html=True)
        st.markdown("

") # Obrazek: Czysty, minimalistyczny notatnik z piórem i ziołami obok, rozmyte tło medyczne.
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 🩺 Podsumowanie kliniczne")
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            avg_s = safe_int(df_u['Cisnienie_S'].mean())
            avg_d = safe_int(df_u['Cisnienie_D'].mean())
            st.markdown(f"<div class='report-card'><b>Średnie ciśnienie:</b><br>{avg_s}/{avg_d} mmHg</div>", unsafe_allow_html=True)
        with c_r2:
            avg_w = safe_val(df_u['Waga'].mean())
            st.markdown(f"<div class='report-card'><b>Średnia masa ciała:</b><br>{avg_w:.2f} kg</div>", unsafe_allow_html=True)
        with c_r3:
            avg_h = safe_int(df_u['Tetno'].mean())
            st.markdown(f"<div class='report-card'><b>Średni puls:</b><br>{avg_h} BPM</div>", unsafe_allow_html=True)
        
        st.markdown("#### Ostatnie pomiary (przejrzyj i wydrukuj)")
        st.dataframe(df_u[['Data', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Waga', 'Dawka']].sort_values("Data", ascending=False).head(14), use_container_width=True)

# --- PANEL AKCJI (STOPKA) ---
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    with st.popover("🧘 NOWY POMIAR", use_container_width=True):
        st.markdown(f"<p style='font-size:1.1rem; color:#6a645e; text-align:center;'>Wprowadź swoje codzienne dane, aby kontynuować podróż.</p>", unsafe_allow_html=True)
        st.markdown("

") # Obrazek: Delikatna ręka zapisująca w dzienniku, obok filiżanka herbaty ziołowej.
        with st.form("add_f"):
            d = st.date_input("Data pomiaru", datetime.now())
            w = st.number_input("Waga", step=0.1, value=safe_val(df_u['Waga'].iloc[-1]) if not df_u.empty else 80.0)
            c_s, c_d, c_t = st.columns(3)
            s_v, d_v, t_v = c_s.number_input("SYS", value=120), c_d.number_input("DIA", value=80), c_t.number_input("Puls", value=70)
            ds = st.selectbox("Dawka (mg)", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
            if st.form_submit_button("ZAPISZ SWÓJ WPIS"):
                new = pd.DataFrame([{"Użytkownik": user, "Data": d, "Waga": w, "Cisnienie_S": s_v, "Cisnienie_D": d_v, "Tetno": t_v, "Dawka": ds}])
                conn.update(data=pd.concat([df_all, new], ignore_index=True))
                st.rerun()

with col2:
    with st.popover("✨ KOREKTA DANYCH", use_container_width=True):
        st.markdown(f"<p style='font-size:1.1rem; color:#6a645e; text-align:center;'>Potrzebujesz coś zmienić? To naturalne.</p>", unsafe_allow_html=True)
        st.markdown("

") # Obrazek: Ręka poprawiająca zapiski w eleganckim notatniku, symbol precyzji.
        if not df_u.empty:
            sel_date = st.selectbox("Wybierz dzień do edycji:", df_u['Data'].tolist()[::-1])
            row = df_u[df_u['Data'] == sel_date].iloc[0]
            with st.form("edit_f"):
                ew = st.number_input("Waga", value=safe_val(row.get('Waga')))
                e_s, e_d, e_t = st.columns(3)
                esys = e_s.number_input("SYS", value=safe_int(row.get('Cisnienie_S')))
                edia = e_d.number_input("DIA", value=safe_int(row.get('Cisnienie_D')))
                etet = e_t.number_input("Puls", value=safe_int(row.get('Tetno')))
                edose = st.selectbox("Dawka", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], 
                                     index=[0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0].index(safe_val(row.get('Dawka'))) if safe_val(row.get('Dawka')) in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0] else 0)
                if st.form_submit_button("ZAKTUALIZUJ WPIS"):
                    idx = df_all[(df_all['Użytkownik'] == user) & (df_all['Data'] == sel_date)].index
                    df_all.loc[idx, ['Waga', 'Cisnienie_S', 'Cisnienie_D', 'Tetno', 'Dawka']] = [ew, esys, edia, etet, edose]
                    conn.update(data=df_all)
                    st.rerun()

with col3:
    with st.popover("📜 PEŁNA HISTORIA", use_container_width=True):
        st.markdown(f"<p style='font-size:1.1rem; color:#6a645e; text-align:center;'>Przejrzyj całą swoją historię pomiarów.</p>", unsafe_allow_html=True)
        st.markdown("

") # Obrazek: Elegancka, otwarta księga ze starożytnymi symbolami, w tle świece i kadzidła.
        st.dataframe(df_u.sort_values("Data", ascending=False), use_container_width=True)

st.markdown("<div style='text-align: center; margin-top: 50px; opacity: 0.4; font-size: 0.7rem; letter-spacing: 3px; color: #4a4540;'>ODDECH • RÓWNOWAGA • ZDROWIE</div>", unsafe_allow_html=True)

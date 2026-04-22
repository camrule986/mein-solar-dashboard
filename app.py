import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Seiteneinstellungen
st.set_page_config(page_title="ANKER SOLIX Energie-Dashboard", layout="wide", initial_sidebar_state="collapsed")

# CSS für das professionelle Design und die Anordnung
st.markdown("""
    <style>
    /* Hintergrund und Karten-Design */
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #eaeaea;
        margin-bottom: 10px;
    }
    .metric-card h3 { margin: 10px 0; font-size: 1.5rem; color: #1a1a1a; }
    .metric-card small { color: #6c757d; font-weight: bold; text-transform: uppercase; }
    
    /* Buttons oben rechts */
    .filter-btn {
        display: inline-flex;
        gap: 5px;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

# OBERE ZEILE: Titel und Filter-Buttons
header_left, header_right = st.columns([2, 1])

with header_left:
    st.markdown("<h2 style='color: #1c3d5a; margin-top: 0;'>ANKER SOLIX <span style='font-weight: normal; font-size: 1.2rem;'>ENERGIE-DASHBOARD</span></h2>", unsafe_allow_html=True)

with header_right:
    # Die Filter-Buttons wie im Bild
    f1, f2, f3, f4, f5, f6 = st.columns([1,1,1,1,1,2])
    f1.button("Tag")
    f2.button("Wo.")
    f3.button("Mo.")
    f4.button("Ja.")
    if f5.button("📷"): # Screenshot Symbol
        st.toast("Screenshot-Funktion bereit am PC (Druck-Taste)")
    if f6.button("➕ Neu"):
        st.rerun()

# Datei-Upload (dezent platziert)
uploaded_file = st.file_uploader("CSV auswählen", type=["csv"], label_visibility="collapsed")

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    df.columns = [str(col).strip() for col in df.columns]
    date_col = next((c for c in df.columns if 'Date' in c or 'Datum' in c), None)
    prod_col = next((c for c in df.columns if 'Production' in c or 'Erzeugung' in c), None)

    if date_col and prod_col:
        df[date_col] = pd.to_datetime(df[date_col])
        if df[prod_col].dtype == object:
            df[prod_col] = df[prod_col].str.replace(',', '.').astype(float)

        # --- REIHE 1: Die 5 Info-Karten ---
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="metric-card"><span style="color:#f39c12">⚡</span><br><small>Erzeugung</small><h3>{df[prod_col].sum():.2f} kWh</h3><p style="font-size:0.7rem; color:gray">Aktuell</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card"><span style="color:#3498db">🏠</span><br><small>Hausverbrauch</small><h3>-- kWh</h3><p style="font-size:0.7rem; color:gray">Netz: --</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card"><span style="color:#2ecc71">🍃</span><br><small>Autarkiequote</small><h3>-- %</h3><p style="font-size:0.7rem; color:gray">Solaranteil</p></div>', unsafe_allow_html=True)
        with m4:
            co2 = df[prod_col].sum() * 0.35
            st.markdown(f'<div class="metric-card"><span style="color:#9b59b6">⬇️</span><br><small>CO2 Ersparnis</small><h3>{co2:.2f} kg</h3><p style="font-size:0.7rem; color:gray">Umwelt</p></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="metric-card"><span style="color:#e67e22">🏆</span><br><small>All-Time Peak</small><h3>{df[prod_col].max():.2f} kWh</h3><p style="font-size:0.7rem; color:gray">am {df.loc[df[prod_col].idxmax(), date_col].strftime("%d.%m.")}</p></div>', unsafe_allow_html=True)

        st.write("") # Abstand

        # --- REIHE 2: Energiefluss (links) und Strings (rechts) ---
        col_main, col_side = st.columns([2, 1])

        with col_main:
            with st.container(border=True):
                st.markdown("**📊 Energiefluss**")
                # Dropdown für KW (wie im Bild)
                kws = df[date_col].dt.isocalendar().week.unique()
                st.selectbox("Zeitraum", options=kws, format_func=lambda x: f"KW {x} 2024", label_visibility="collapsed")
                
                fig_fluss = px.area(df, x=date_col, y=prod_col, color_discrete_sequence=['#f39c12'])
                fig_fluss.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=300, plot_bgcolor='white')
                st.plotly_chart(fig_fluss, use_container_width=True)

        with col_side:
            with st.container(border=True):
                st.markdown("**☀️ String Verteilung**")
                fig_pie = go.Figure(data=[go.Pie(labels=['PV1', 'PV2', 'PV3', 'PV4'], values=[1,1,1,1], hole=.7, marker=dict(colors=['#f1c40f', '#3498db', '#2ecc71', '#e74c3c']))])
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.caption("PV1: -- kWh | PV2: -- kWh")

        # --- REIHE 3: Details (links) und Speicher (rechts) ---
        col_bot_left, col_bot_right = st.columns([2, 1])
        
        with col_bot_left:
            with st.container(border=True):
                st.markdown("**Perioden-Details**")
                st.dataframe(df.sort_values(by=date_col, ascending=False), hide_index=True, use_container_width=True)

        with col_bot_right:
            with st.container(border=True):
                st.markdown("**🔋 Speichernutzung**")
                # Dummy Grafik für Speicher
                st.write("Warte auf Solarbank 2...")
                st.bar_chart([0, 0, 0, 0])

else:
    st.info("Bitte CSV-Datei hochladen, um die Ansicht zu generieren.")

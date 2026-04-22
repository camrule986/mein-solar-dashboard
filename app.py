import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Seiteneinstellungen für Breitbild
st.set_page_config(page_title="ANKER SOLIX Energie-Dashboard", layout="wide")

# CSS für das Styling (weißes Design, abgerundete Karten)
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #f0f2f6;
    }
    .stButton>button {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header-Bereich
col_title, col_tools = st.columns([2, 1])
with col_title:
    st.title("ANKER SOLIX ENERGIE-DASHBOARD")

with col_tools:
    st.write("") # Platzhalter
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.button("Tag")
    t2.button("Woche")
    t3.button("Monat")
    t4.button("Jahr")
    if t5.button("❌ Neue Datei"):
        st.rerun()

# Datei-Upload
uploaded_file = st.file_uploader("CSV Datei hochladen", type=["csv"], label_visibility="collapsed")

if uploaded_file:
    # Daten einlesen
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    df.columns = [str(col).strip() for col in df.columns]
    
    # Spaltenzuordnung (flexibel)
    date_col = next((c for c in df.columns if 'Date' in c or 'Datum' in c), None)
    prod_col = next((c for c in df.columns if 'Production' in c or 'Erzeugung' in c), None)

    if date_col and prod_col:
        df[date_col] = pd.to_datetime(df[date_col])
        if df[prod_col].dtype == object:
            df[prod_col] = df[prod_col].str.replace(',', '.').astype(float)

        # --- REIHE 1: Metriken ---
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="metric-card">⚡<br><small>ERZEUGUNG</small><h3>{df[prod_col].sum():.2f} kWh</h3></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card">🏠<br><small>HAUSVERBRAUCH</small><h3>-- kWh</h3><small>Netz: --</small></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card">🍃<br><small>AUTARKIEQUOTE</small><h3>-- %</h3><small>Solaranteil</small></div>', unsafe_allow_html=True)
        with m4:
            # CO2 Ersparnis (ca. 0.35kg pro kWh)
            co2 = df[prod_col].sum() * 0.35
            st.markdown(f'<div class="metric-card">⬇️<br><small>CO2 ERSPARNIS</small><h3>{co2:.2f} kg</h3><small>Umwelt</small></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="metric-card">🏆<br><small>ALL-TIME PEAK</small><h3>{df[prod_col].max():.2f} kWh</h3></div>', unsafe_allow_html=True)

        st.write("---")

        # --- REIHE 2: Energiefluss & String Verteilung ---
        c_fluss, c_strings = st.columns([2, 1])
        
        with c_fluss:
            st.subheader("📊 Energiefluss")
            # Auswahl für KW (Kalenderwoche)
            kws = df[date_col].dt.isocalendar().week.unique()
            st.selectbox("Zeitraum wählen", options=kws, format_func=lambda x: f"KW {x} 2024")
            
            fig_fluss = px.area(df, x=date_col, y=prod_col, title="Solarerzeugung vs. Verbrauch")
            fig_fluss.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_fluss, use_container_width=True)

        with c_strings:
            st.subheader("🔆 String Verteilung")
            # Donut Chart (Platzhalter da aktuell keine String-Daten)
            fig_strings = go.Figure(data=[go.Pie(labels=['PV1', 'PV2', 'PV3', 'PV4'], 
                                             values=[0, 0, 0, 0], hole=.6)])
            fig_strings.update_layout(showlegend=True)
            st.plotly_chart(fig_strings, use_container_width=True)
            st.info("Daten verfügbar sobald Solarbank 2 Pro installiert ist.")

        # --- REIHE 3: Details & Speicher ---
        c_det, c_batt = st.columns([2, 1])
        with c_det:
            st.subheader("Perioden-Details")
            st.dataframe(df, use_container_width=True)
            
        with c_batt:
            st.subheader("🔋 Speichernutzung")
            st.write("Kein Akku erkannt.")
            # Hier käme später das Balkendiagramm für Ladung/Entladung hin

else:
    st.info("Bitte lade deine CSV-Datei hoch, um das Dashboard zu aktivieren.")
    st.image("https://img.freepik.com/free-vector/solar-energy-concept-illustration_114360-6457.jpg", width=400)

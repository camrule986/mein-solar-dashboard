import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Seiteneinstellungen
st.set_page_config(page_title="ANKER SOLIX Dashboard", layout="wide", initial_sidebar_state="collapsed")

# CSS für Design und Layout-Anpassungen
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;
        border: 1px solid #eaeaea; margin-bottom: 10px;
    }
    .metric-card h3 { margin: 5px 0; font-size: 1.4rem; color: #1a1a1a; }
    .metric-card small { color: #6c757d; font-weight: bold; text-transform: uppercase; font-size: 0.7rem; }
    
    /* Buttons Styling */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #dcdcdc;
        background-color: white;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisierung SessionState
if 'filter_type' not in st.session_state:
    st.session_state.filter_type = 'Tag'

# Header
header_left, header_right = st.columns([1.5, 2])

with header_left:
    st.markdown("<h2 style='color: #1c3d5a; margin: 0;'>ANKER SOLIX <span style='font-weight: normal; font-size: 1.2rem;'>ENERGIE-DASHBOARD</span></h2>", unsafe_allow_html=True)

with header_right:
    # Buttons nebeneinander mit ausgeschriebenem Text
    f1, f2, f3, f4, f5, f6 = st.columns([1, 1, 1, 1, 0.8, 1])
    if f1.button("Tag"): st.session_state.filter_type = 'Tag'
    if f2.button("Woche"): st.session_state.filter_type = 'Woche'
    if f3.button("Monat"): st.session_state.filter_type = 'Monat'
    if f4.button("Jahr"): st.session_state.filter_type = 'Jahr'
    f5.button("📷")
    if f6.button("Neue Datei"): st.rerun()

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
        
        # Hilfsspalten für zeitlose Filterung
        df['Jahr_Label'] = df[date_col].dt.year
        df['Monat_Label'] = df[date_col].dt.strftime('%B %Y')
        df['KW_Label'] = df[date_col].apply(lambda x: f"KW {x.isocalendar().week} {x.year}")
        df['Tag_Label'] = df[date_col].dt.strftime('%d.%m.%Y')

        # --- Globaler Filter Bereich ---
        st.write(f"**Aktueller Filter:** {st.session_state.filter_type}")
        sel_col1, _ = st.columns([1.5, 3])
        
        with sel_col1:
            if st.session_state.filter_type == 'Jahr':
                options = sorted(df['Jahr_Label'].unique(), reverse=True)
                selection = st.selectbox("Jahr wählen", options)
                filtered_df = df[df['Jahr_Label'] == selection]
            elif st.session_state.filter_type == 'Monat':
                options = df.sort_values(by=date_col, ascending=False)['Monat_Label'].unique()
                selection = st.selectbox("Monat wählen", options)
                filtered_df = df[df['Monat_Label'] == selection]
            elif st.session_state.filter_type == 'Woche':
                options = df.sort_values(by=date_col, ascending=False)['KW_Label'].unique()
                selection = st.selectbox("Woche wählen", options)
                filtered_df = df[df['KW_Label'] == selection]
            else: # Tag
                options = df.sort_values(by=date_col, ascending=False)['Tag_Label'].unique()
                selection = st.selectbox("Tag wählen", options)
                filtered_df = df[df['Tag_Label'] == selection]

        # --- REIHE 1: Metriken ---
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="metric-card"><small>Erzeugung</small><h3>{filtered_df[prod_col].sum():.2f} kWh</h3></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card"><small>Hausverbrauch</small><h3>-- kWh</h3></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card"><small>Autarkie</small><h3>-- %</h3></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><small>CO2 Ersparnis</small><h3>{filtered_df[prod_col].sum()*0.35:.2f} kg</h3></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="metric-card"><small>Peak</small><h3>{filtered_df[prod_col].max():.2f} kWh</h3></div>', unsafe_allow_html=True)

        # --- REIHE 2: Energiefluss & Strings ---
        col_main, col_side = st.columns([2, 1])

        with col_main:
            with st.container(border=True):
                st.markdown("**📊 Energiefluss**")
                # Energiefluss Filter ohne Jahresbegrenzung
                all_kws = df.sort_values(by=date_col, ascending=False)['KW_Label'].unique()
                kw_selection = st.selectbox("Zeitraum wählen", all_kws, key="kw_flow_unlimited")
                flow_df = df[df['KW_Label'] == kw_selection].sort_values(by=date_col)
                
                fig_fluss = px.area(flow_df, x=date_col, y=prod_col, color_discrete_sequence=['#f39c12'])
                fig_fluss.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0), height=300, 
                    xaxis_title=None, yaxis_title="kWh",
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_fluss, use_container_width=True, config={'displayModeBar': False})

        with col_side:
            with st.container(border=True):
                st.markdown("**☀️ String Verteilung**")
                fig_pie = go.Figure(data=[go.Pie(labels=['PV1', 'PV2', 'PV3', 'PV4'], values=[1,1,1,1], hole=.7)])
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=10), height=250, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                st.caption("Daten ab Solarbank 2 verfügbar")

        # --- REIHE 3: Details ---
        col_bot_left, col_bot_right = st.columns([2, 1])
        with col_bot_left:
            with st.container(border=True):
                st.markdown("**Perioden-Details**")
                st.dataframe(filtered_df[[date_col, prod_col]].sort_values(by=date_col, ascending=False), hide_index=True, use_container_width=True)
        with col_bot_right:
            with st.container(border=True):
                st.markdown("**🔋 Speichernutzung**")
                st.write("Warte auf Akku-Daten...")
                st.bar_chart([0, 0, 0, 0])

else:
    st.info("Bitte CSV-Datei hochladen.")

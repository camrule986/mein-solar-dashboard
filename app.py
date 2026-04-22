import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Seiteneinstellungen
st.set_page_config(page_title="ANKER SOLIX Dashboard", layout="wide", initial_sidebar_state="collapsed")

# CSS für Design
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
    
    div.stButton > button {
        width: 100%; border-radius: 10px; border: 1px solid #dcdcdc;
        background-color: white; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

if 'filter_type' not in st.session_state:
    st.session_state.filter_type = 'Tag'

# Header
header_left, header_right = st.columns([1.5, 2.5])
with header_left:
    st.markdown("<h2 style='color: #1c3d5a; margin: 0;'>ANKER SOLIX <span style='font-weight: normal; font-size: 1.2rem;'>ENERGIE-DASHBOARD</span></h2>", unsafe_allow_html=True)

with header_right:
    f1, f2, f3, f4, f5, f6 = st.columns([1, 1, 1, 1, 0.8, 1.2])
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
        
        # Zeit-Hilfsspalten
        df['Jahr_Val'] = df[date_col].dt.year
        df['Monat_Label'] = df[date_col].dt.strftime('%B %Y')
        df['KW_Label'] = df[date_col].apply(lambda x: f"KW {x.isocalendar().week} {x.year}")
        df['Tag_Label'] = df[date_col].dt.strftime('%d.%m.%Y')
        df['Quartal'] = df[date_col].dt.quarter

        # --- Globaler Filter (Karten & Details) ---
        sel_col_global, _ = st.columns([1.5, 3])
        with sel_col_global:
            if st.session_state.filter_type == 'Jahr':
                sel_g = st.selectbox("Jahr wählen", sorted(df['Jahr_Val'].unique(), reverse=True))
                filtered_df = df[df['Jahr_Val'] == sel_g]
            elif st.session_state.filter_type == 'Monat':
                sel_g = st.selectbox("Monat wählen", df.sort_values(by=date_col, ascending=False)['Monat_Label'].unique())
                filtered_df = df[df['Monat_Label'] == sel_g]
            elif st.session_state.filter_type == 'Woche':
                sel_g = st.selectbox("Woche wählen", df.sort_values(by=date_col, ascending=False)['KW_Label'].unique())
                filtered_df = df[df['KW_Label'] == sel_g]
            else:
                sel_g = st.selectbox("Tag wählen", df.sort_values(by=date_col, ascending=False)['Tag_Label'].unique())
                filtered_df = df[df['Tag_Label'] == sel_g]

        # --- REIHE 1: Metriken ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(f'<div class="metric-card"><small>Erzeugung</small><h3>{filtered_df[prod_col].sum():.2f} kWh</h3></div>', unsafe_allow_html=True)
        m2.markdown('<div class="metric-card"><small>Hausverbrauch</small><h3>-- kWh</h3></div>', unsafe_allow_html=True)
        m3.markdown('<div class="metric-card"><small>Autarkie</small><h3>-- %</h3></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><small>CO2 Ersparnis</small><h3>{filtered_df[prod_col].sum()*0.35:.2f} kg</h3></div>', unsafe_allow_html=True)
        m5.markdown(f'<div class="metric-card"><small>Peak</small><h3>{filtered_df[prod_col].max():.2f} kWh</h3></div>', unsafe_allow_html=True)

        # --- REIHE 2: Energiefluss (Erweiterte Filter) & Strings ---
        col_main, col_side = st.columns([2, 1])
        with col_main:
            with st.container(border=True):
                st.markdown("**📊 Energiefluss**")
                # Neue Filter-Ebene für Energiefluss
                ef1, ef2 = st.columns(2)
                with ef1:
                    ef_mode = st.radio("Ansicht", ["Woche", "Quartal", "Jahr"], horizontal=True, label_visibility="collapsed")
                with ef2:
                    if ef_mode == "Woche":
                        all_kws = df.sort_values(by=date_col, ascending=False)['KW_Label'].unique()
                        kw_sel = st.selectbox("Zeitraum", all_kws, label_visibility="collapsed")
                        flow_df = df[df['KW_Label'] == kw_sel]
                    elif ef_mode == "Quartal":
                        q_options = sorted(df[df['Jahr_Val'] == datetime.now().year]['Quartal'].unique())
                        q_sel = st.selectbox("Quartal (2026)", q_options, format_func=lambda x: f"{x}. Quartal", label_visibility="collapsed")
                        flow_df = df[(df['Jahr_Val'] == datetime.now().year) & (df['Quartal'] == q_sel)]
                    else:
                        y_options = sorted(df['Jahr_Val'].unique(), reverse=True)
                        y_sel = st.selectbox("Jahr", y_options, label_visibility="collapsed")
                        flow_df = df[df['Jahr_Val'] == y_sel]
                
                fig_fluss = px.area(flow_df.sort_values(by=date_col), x=date_col, y=prod_col, color_discrete_sequence=['#f39c12'])
                fig_fluss.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, xaxis_title=None, yaxis_title="kWh", plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_fluss, use_container_width=True, config={'displayModeBar': False})

        with col_side:
            with st.container(border=True):
                st.markdown("**☀️ String Verteilung**")
                fig_pie = go.Figure(data=[go.Pie(labels=['PV1', 'PV2', 'PV3', 'PV4'], values=[1,1,1,1], hole=.7)])
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=10), height=250, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        # --- REIHE 3: Details & Speicher ---
        col_bot_left, col_bot_right = st.columns([2, 1])
        with col_bot_left:
            with st.container(border=True):
                st.markdown("**Perioden-Details**")
                st.dataframe(filtered_df[[date_col, prod_col]].sort_values(by=date_col, ascending=False), hide_index=True, use_container_width=True)
        with col_bot_right:
            with st.container(border=True):
                st.markdown("**🔋 Speichernutzung**")
                st.write("Warte auf Akku...")
                st.bar_chart([0, 0, 0, 0])
else:
    st.info("Bitte CSV-Datei hochladen.")

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
    </style>
    """, unsafe_allow_html=True)

# Initialisierung der Filter im SessionState
if 'filter_type' not in st.session_state:
    st.session_state.filter_type = 'Tag'

# Header
header_left, header_right = st.columns([2, 1.5])

with header_left:
    st.markdown("<h2 style='color: #1c3d5a; margin: 0;'>ANKER SOLIX <span style='font-weight: normal; font-size: 1.2rem;'>ENERGIE-DASHBOARD</span></h2>", unsafe_allow_html=True)

with header_right:
    f1, f2, f3, f4, f5, f6 = st.columns([1,1,1,1,1,1.5])
    if f1.button("Tag"): st.session_state.filter_type = 'Tag'
    if f2.button("Wo."): st.session_state.filter_type = 'Woche'
    if f3.button("Mo."): st.session_state.filter_type = 'Monat'
    if f4.button("Ja."): st.session_state.filter_type = 'Jahr'
    f5.button("📷")
    if f6.button("➕ Neu"): st.rerun()

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
        
        # Hilfsspalten für Filterung
        df['Jahr'] = df[date_col].dt.year
        df['Monat'] = df[date_col].dt.month
        df['KW'] = df[date_col].dt.isocalendar().week
        df['Tag'] = df[date_col].dt.day

        # --- Filter-Auswahl-Logik ---
        st.write(f"**Filter aktiv:** {st.session_state.filter_type}")
        sel_col1, sel_col2 = st.columns([1, 3])
        
        with sel_col1:
            if st.session_state.filter_type == 'Jahr':
                selection = st.selectbox("Jahr wählen", sorted(df['Jahr'].unique(), reverse=True))
                filtered_df = df[df['Jahr'] == selection]
            elif st.session_state.filter_type == 'Monat':
                selection = st.selectbox("Monat wählen", sorted(df[df['Jahr'] == datetime.now().year]['Monat'].unique(), reverse=True))
                filtered_df = df[(df['Jahr'] == datetime.now().year) & (df['Monat'] == selection)]
            elif st.session_state.filter_type == 'Woche':
                selection = st.selectbox("Woche wählen", sorted(df[df['Jahr'] == datetime.now().year]['KW'].unique(), reverse=True))
                filtered_df = df[(df['Jahr'] == datetime.now().year) & (df['KW'] == selection)]
            else: # Tag
                # Nur Tage des aktuellen Monats/Jahres anzeigen
                current_month_days = df[(df['Jahr'] == datetime.now().year) & (df['Monat'] == datetime.now().month)]
                selection = st.selectbox("Tag wählen", sorted(current_month_days[date_col].dt.strftime('%Y-%m-%d').unique(), reverse=True))
                filtered_df = df[df[date_col].dt.strftime('%Y-%m-%d') == selection]

        # --- REIHE 1: Metriken (basierend auf filtered_df) ---
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="metric-card"><span style="color:#f39c12">⚡</span><br><small>Erzeugung</small><h3>{filtered_df[prod_col].sum():.2f} kWh</h3></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card"><span style="color:#3498db">🏠</span><br><small>Hausverbrauch</small><h3>-- kWh</h3></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card"><span style="color:#2ecc71">🍃</span><br><small>Autarkie</small><h3>-- %</h3></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><span style="color:#9b59b6">⬇️</span><br><small>CO2 Ersparnis</small><h3>{filtered_df[prod_col].sum()*0.35:.2f} kg</h3></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="metric-card"><span style="color:#e67e22">🏆</span><br><small>Peak</small><h3>{filtered_df[prod_col].max():.2f} kWh</h3></div>', unsafe_allow_html=True)

        # --- REIHE 2: Energiefluss (separater Filter) ---
        col_main, col_side = st.columns([2, 1])

        with col_main:
            with st.container(border=True):
                st.markdown("**📊 Energiefluss**")
                kw_selection = st.selectbox("KW wählen", sorted(df['KW'].unique(), reverse=True), format_func=lambda x: f"KW {x} 2024", key="kw_flow")
                flow_df = df[df['KW'] == kw_selection].sort_values(by=date_col)
                
                fig_fluss = px.area(flow_df, x=date_col, y=prod_col, color_discrete_sequence=['#f39c12'])
                fig_fluss.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_fluss, use_container_width=True, config={'displayModeBar': False})

        with col_side:
            with st.container(border=True):
                st.markdown("**☀️ String Verteilung**")
                fig_pie = go.Figure(data=[go.Pie(labels=['PV1', 'PV2', 'PV3', 'PV4'], values=[1,1,1,1], hole=.7)])
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        # --- REIHE 3: Details ---
        col_bot_left, col_bot_right = st.columns([2, 1])
        with col_bot_left:
            with st.container(border=True):
                st.markdown("**Perioden-Details**")
                st.dataframe(filtered_df[[date_col, prod_col]].sort_values(by=date_col, ascending=False), hide_index=True, use_container_width=True)
        with col_bot_right:
            with st.container(border=True):
                st.markdown("**🔋 Speichernutzung**")
                st.write("Warte auf Daten...")

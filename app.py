import streamlit as st
import pandas as pd
import plotly.express as px

# Seiteneinstellungen
st.set_page_config(page_title="Florians Solar-Dashboard", layout="wide")

st.title("☀️ Florians Solar-Dashboard")
st.write("Analysiere deine Erträge und optimiere deine Autarkie.")

# Datei-Upload Funktion
uploaded_file = st.file_uploader("Lade deine Anker/Solar-CSV hoch", type=["csv"])

if uploaded_file is not None:
    # Daten einlesen (Trennzeichen bei Anker-Exports oft Tabulator oder Komma)
    df = pd.read_csv(uploaded_file, sep='\t')
    
    # Spaltennamen bereinigen (Leerzeichen entfernen)
    df.columns = df.columns.str.strip()
    
    # Datum konvertieren
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Kennzahlen berechnen
    total_production = df['Electricity Production-(kWh)'].sum()
    avg_production = df['Electricity Production-(kWh)'].mean()
    max_day = df.loc[df['Electricity Production-(kWh)'].idxmax()]

    # Layout: Drei Spalten für die wichtigsten Zahlen
    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamtertrag", f"{total_production:.2f} kWh")
    col2.metric("Ø Ertrag/Tag", f"{avg_production:.2f} kWh")
    col3.metric("Bester Tag", f"{max_day['Electricity Production-(kWh)']:.2f} kWh", delta=max_day['Date'].strftime('%d.%m.%Y'))

    # Grafik: Ertragsverlauf
    st.subheader("Ertragsverlauf über die Zeit")
    fig = px.line(df, x='Date', y='Electricity Production-(kWh)', 
                  title='Tageserträge in kWh',
                  line_shape='spline',
                  render_mode='svg')
    fig.update_traces(line_color='#FFA500')
    st.plotly_chart(fig, use_container_width=True)

    # Tabelle für Details
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(df.sort_values(by='Date', ascending=False))

else:
    st.info("Bitte lade eine CSV-Datei hoch, um die Analyse zu starten.")


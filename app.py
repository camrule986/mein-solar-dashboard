import streamlit as st
import pandas as pd
import plotly.express as px

# Seiteneinstellungen
st.set_page_config(page_title="Florians Solar-Dashboard", layout="wide")

st.title("☀️ Florians Solar-Dashboard")
st.write("Analysiere deine Erträge.")

uploaded_file = st.file_uploader("Lade deine CSV hoch", type=["csv"])

if uploaded_file is not None:
    # Versuche verschiedene Trennzeichen (Anker/Excel nutzen oft Tab oder Semikolon)
    try:
        # Erst mit Tabulator versuchen
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        
        # Spaltennamen säubern (Leerzeichen und Tabs entfernen)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Suche die richtige Spalte, auch wenn sie leicht anders heißt
        prod_col = None
        for col in df.columns:
            if 'Production' in col or 'Erzeugung' in col or 'kWh' in col:
                prod_col = col
                break
        
        date_col = None
        for col in df.columns:
            if 'Date' in col or 'Datum' in col or 'Zeit' in col:
                date_col = col
                break

        if prod_col and date_col:
            # Daten konvertieren
            df[date_col] = pd.to_datetime(df[date_col])
            # Sicherstellen, dass die Werte Zahlen sind (Punkte/Kommas korrigieren)
            if df[prod_col].dtype == object:
                df[prod_col] = df[prod_col].str.replace(',', '.').astype(float)
            
            # Kennzahlen
            total_production = df[prod_col].sum()
            avg_production = df[prod_col].mean()

            col1, col2 = st.columns(2)
            col1.metric("Gesamtertrag", f"{total_production:.2f} kWh")
            col2.metric("Ø Ertrag/Tag", f"{avg_production:.2f} kWh")

            # Grafik
            fig = px.line(df, x=date_col, y=prod_col, title='Ertragsverlauf')
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df)
        else:
            st.error(f"Spalten nicht gefunden. Vorhanden sind: {list(df.columns)}")
            
    except Exception as e:
        st.error(f"Fehler beim Lesen der Datei: {e}")
else:
    st.info("Bitte lade eine Datei hoch.")

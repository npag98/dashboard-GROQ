import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from groq import Groq

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Stock Insight", layout="wide")

# 2. Funzione per l'AI con Groq
def chiedi_a_groq(prompt_testo):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt_testo}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Errore AI: {e}"

st.title("📊 Dashboard Finanziaria Intelligente")

# 3. Barra Laterale: Scelta Mercato
st.sidebar.header("Configurazione Mercato")

mercato = st.sidebar.selectbox(
    "Seleziona Mercato",
    ["USA (NASDAQ/NYSE)", "Italia (Borsa Italiana)", "Germania (XETRA)", "Cripto"]
)

# Gestione suffissi
if mercato == "Italia (Borsa Italiana)":
    suffisso = ".MI"
elif mercato == "Germania (XETRA)":
    suffisso = ".F"
elif mercato == "Cripto":
    suffisso = "-USD"
else:
    suffisso = ""

input_ticker = st.sidebar.text_input(f"Simbolo {mercato}", "AAPL").upper()
ticker = f"{input_ticker}{suffisso}"

# 4. Logica Principale
if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # --- SEZIONE METRICHE ---
        st.header(f"Analisi: {info.get('longName', ticker)}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Prezzo", f"{info.get('currentPrice', 'N/A')} {info.get('currency', '')}")
        c2.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
        c3.metric("Settore", info.get('sector', 'N/A'))

        # --- SEZIONE GRAFICI ---
        st.subheader("Fatturato e Utili")
        df = stock.financials.T[['Total Revenue', 'Net Income']].dropna().head(3)
        if not df.empty:
            fig = go.Figure(data=[
                go.Bar(name='Fatturato', x=df.index.year, y=df['Total Revenue']),
                go.Bar(name='Utile Netto', x=df.index.year, y=df['Net Income'])
            ])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dati finanziari storici non disponibili per questo ticker.")

        # --- SEZIONE AI ---
        st.divider()
        if st.button("🤖 Genera Analisi con AI"):
            with st.spinner("L'AI sta studiando i dati per te..."):
                dati_stringa = f"Ticker: {ticker}, Mercato: {mercato}, P/E: {info.get('trailingPE')}, Target: {info.get('targetMeanPrice')}"
                prompt = f"Agisci come esperto finanziario. Analizza brevemente {ticker} ({mercato}). Dati: {dati_stringa}. Sii sintetico."
                risposta = chiedi_a_groq(prompt)
                st.info(risposta)

    except Exception as e:
        st.error(f"Errore: Il ticker '{ticker}' non è stato trovato o i dati sono incompleti.")

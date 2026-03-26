import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from groq import Groq

# Configurazione Pagina
st.set_page_config(page_title="AI Stock Insight", layout="wide")

# Funzione per l'AI con Groq
def chiedi_a_groq(prompt_testo):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Modello potentissimo e veloce
        messages=[{"role": "user", "content": prompt_testo}],
    )
    return completion.choices[0].message.content

st.title("📊 Dashboard Finanziaria Intelligente")

# Input Ticker
ticker = st.sidebar.text_input("Digita Ticker (es. NVDA, TSLA, ISP.MI)", "AAPL").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # --- SEZIONE METRICHE ---
        st.header(f"Analisi: {info.get('longName', ticker)}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Prezzo", f"{info.get('currentPrice')} {info.get('currency')}")
        c2.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
        c3.metric("Settore", info.get('sector', 'N/A'))

        # --- SEZIONE GRAFICI ---
        st.subheader("Fatturato e Utili")
        # Dati annuali (ultimi 3 anni)
        df = stock.financials.T[['Total Revenue', 'Net Income']].dropna().head(3)
        fig = go.Figure(data=[
            go.Bar(name='Fatturato', x=df.index.year, y=df['Total Revenue']),
            go.Bar(name='Utile Netto', x=df.index.year, y=df['Net Income'])
        ])
        st.plotly_chart(fig, use_container_width=True)

        # --- SEZIONE AI ---
        st.divider()
        if st.button("🤖 Genera Analisi con AI"):
            with st.spinner("L'AI sta studiando i dati per te..."):
                dati_stringa = f"Ticker: {ticker}, P/E: {info.get('trailingPE')}, Target: {info.get('targetMeanPrice')}"
                risposta = chiedi_a_groq(f"Analizza brevemente questa azione come un esperto finanziario. Sii critico e diretto: {dati_stringa}")
                st.info(risposta)
        # --- BARRA LATERALE: SCELTA MERCATO E TICKER ---
st.sidebar.header("Configurazione Mercato")

# Menu a tendina per i mercati principali
mercato = st.sidebar.selectbox(
    "Seleziona Mercato",
    ["USA (NASDAQ/NYSE)", "Italia (Borsa Italiana)", "Germania (XETRA)", "Cripto"]
)

# Gestione automatica del suffisso
if mercato == "Italia (Borsa Italiana)":
    suffisso = ".MI"
    placeholder = "Es: ISP o ENI"
elif mercato == "Germania (XETRA)":
    suffisso = ".F"
    placeholder = "Es: BMW"
elif mercato == "Cripto":
    suffisso = "-USD"
    placeholder = "Es: BTC o ETH"
else:
    suffisso = ""
    placeholder = "Es: AAPL o NVDA"

# Input del ticker (senza dover scrivere il punto MI ogni volta)
input_ticker = st.sidebar.text_input(f"Inserisci Simbolo {mercato}", "AAPL").upper()

# Ticker finale pulito
ticker = f"{input_ticker}{suffisso}"

    except Exception as e:
        st.error("Errore nel caricamento. Controlla il ticker o riprova tra poco.")

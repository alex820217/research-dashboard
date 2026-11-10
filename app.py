import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(
    page_title="📈 Börsen Research Dashboard",
    layout="wide"
)

st.title("📈 Börsen Research Dashboard")

# ---------------------------
# Märkte oben
# ---------------------------

st.subheader("🌍 Marktübersicht")

markets = {
    "DAX": "^GDAXI",
    "Nasdaq": "^NDX",
    "S&P500": "^GSPC",
    "Gold": "GC=F",
    "Öl": "CL=F",
    "EUR/USD": "EURUSD=X"
}

cols = st.columns(3)

i = 0

for name, symbol in markets.items():

    try:

        df = yf.download(
            symbol,
            period="1mo",
            auto_adjust=True,
            progress=False
        )

        close = df["Close"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        last_price = round(
            float(close.iloc[-1]),
            2
        )

        change = round(
            ((close.iloc[-1] / close.iloc[0]) - 1) * 100,
            2
        )

        with cols[i % 3]:

            st.metric(
                name,
                last_price,
                f"{change}%"
            )

        i += 1

    except

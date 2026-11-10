import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(
    page_title="📈 Börsen Research Dashboard",
    layout="wide"
)

st.title("📈 Börsen Research Dashboard")

WATCHLIST = {
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Nvidia": "NVDA",
    "Amazon": "AMZN",
    "DAX": "^GDAXI",
    "Gold": "GC=F",
    "Öl": "CL=F",
    "EUR/USD": "EURUSD=X"
}

asset = st.selectbox(
    "Markt auswählen",
    list(WATCHLIST.keys())
)

ticker = WATCHLIST[asset]

try:

    data = yf.download(
        ticker,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        st.warning("Keine Daten gefunden")
        st.stop()

    close = data["Close"]

    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    # RSI
    rsi = ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()

    # EMA50
    ema50 = ta.trend.EMAIndicator(
        close=close,
        window=50
    ).ema_indicator()

    aktueller_kurs = round(
        float(close.iloc[-1]),
        2
    )

    aktueller_rsi = round(
        float(rsi.iloc[-1]),
        1
    )

    ema50_aktuell = float(
        ema50.iloc[-1]
    )

    # Score
    score = 0

    if aktueller_kurs > ema50_aktuell:
        score += 50

    if aktueller_rsi > 50:
        score += 50

    # Marktampel

    if score >= 80:
        ampel = "🟢 Bullisch"

    elif score >= 50:
        ampel = "🟡 Neutral"

    else:
        ampel = "🔴 Schwach"

    # Trend

    if aktueller_kurs > ema50_aktuell:
        trend = "📈 Aufwärtstrend"
    else:
        trend = "📉 Abwärtstrend"

    st.subheader(asset)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Kurs",
            aktueller_kurs
        )

    with col2:
        st.metric(
            "RSI",
            aktueller_rsi
        )

    st.subheader("Research Score")

    st.progress(score)

    st.write(
        f"Score: {score}/100"
    )

    st.write(
        f"Trend: {trend}"
    )

    st.write(
        f"Marktstatus: {ampel}"
    )

    st.subheader("Kursverlauf")

    st.line_chart(close)

except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

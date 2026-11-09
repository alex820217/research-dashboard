import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="📈 Börsen Dashboard",
    layout="wide"
)

st.title("📈 Research Dashboard")

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
        st.warning("Keine Daten gefunden.")
        st.stop()

    close = data["Close"]

    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    aktueller_kurs = round(close.iloc[-1], 2)

    performance = round(
        ((close.iloc[-1] / close.iloc[0]) - 1) * 100,
        2
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Aktueller Kurs",
            aktueller_kurs
        )

    with col2:
        st.metric(
            "1 Jahr %",
            performance
        )

    st.subheader("Kursverlauf")

    chart = pd.DataFrame({
        "Kurs": close
    })

    st.line_chart(chart)

except Exception as e:
    st.error(str(e))

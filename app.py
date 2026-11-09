import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Research Dashboard",
    layout="wide"
)

st.title("📈 Research Dashboard")

ticker = st.text_input(
    "Ticker",
    value="MSFT"
)

data = yf.download(
    ticker,
    period="1y"
)

if not data.empty:

    st.line_chart(data["Close"])

    latest = float(data["Close"].iloc[-1])

    st.metric(
        "Aktueller Kurs",
        f"{latest:.2f}"
    )

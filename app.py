import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(
    page_title="📈 Research Dashboard",
    layout="wide"
)

st.title("📈 Börsen Research Dashboard")

WATCHLIST = {
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Nvidia": "NVDA",
    "Amazon": "AMZN",
    "DAX": "^GDAXI",
    "Nasdaq 100": "^NDX",
    "S&P500": "^GSPC",
    "Gold": "GC=F",
    "Öl": "CL=F",
    "EUR/USD": "EURUSD=X"
}

# -----------------------
# Marktübersicht
# -----------------------

st.header("🌍 Marktübersicht")

overview = []

for name, ticker in WATCHLIST.items():

    try:

        data = yf.download(
            ticker,
            period="6mo",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            continue

        close = data["Close"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        rsi = ta.momentum.RSIIndicator(
            close=close
        ).rsi()

        ema20 = ta.trend.EMAIndicator(
            close=close,
            window=20
        ).ema_indicator()

        ema50 = ta.trend.EMAIndicator(
            close=close,
            window=50
        ).ema_indicator()

        price = float(close.iloc[-1])
        last_rsi = float(rsi.iloc[-1])

        score = 0

        if float(ema20.iloc[-1]) > float(ema50.iloc[-1]):
            score += 25

        if price > float(ema50.iloc[-1]):
            score += 25

        if last_rsi > 50:
            score += 25

        if (close.iloc[-1] / close.iloc[0]) > 1:
            score += 25

        if score >= 75:
            signal = "🟢"

        elif score >= 50:
            signal = "🟡"

        else:
            signal = "🔴"

        overview.append({
            "Asset": name,
            "Kurs": round(price, 2),
            "RSI": round(last_rsi, 1),
            "Score": score,
            "Trend": signal
        })

    except Exception:
        pass

if len(overview) > 0:

    df = pd.DataFrame(overview)

    df = df.sort_values(
        "Score",
        ascending=False
    )

    st.dataframe(
        df,
        use_container_width=True
    )

# -----------------------
# Einzelanalyse
# -----------------------

asset = st.selectbox(
    "📌 Asset auswählen",
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

    close = data["Close"]

    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    rsi = ta.momentum.RSIIndicator(
        close=close
    ).rsi()

    aktueller_kurs = round(
        float(close.iloc[-1]),
        2
    )

    aktueller_rsi = round(
        float(rsi.iloc[-1]),
        1
    )

    st.header(asset)

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

    st.line_chart(close)

except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

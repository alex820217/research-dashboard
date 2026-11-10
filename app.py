import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

st.set_page_config(
    page_title="📈 Börsen Research Dashboard",
    layout="wide"
)

st.title("📈 Börsen Research Dashboard")

# --------------------------------------------------
# Watchlist
# --------------------------------------------------

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

# --------------------------------------------------
# Marktstatus
# --------------------------------------------------

st.header("🕒 Marktstatus")

hour = datetime.now().hour

if 9 <= hour < 17:
    dax_status = "🟢 Offen"
else:
    dax_status = "🔴 Geschlossen"

if 15 <= hour < 22:
    usa_status = "🟢 Offen"
else:
    usa_status = "🔴 Geschlossen"

col1, col2 = st.columns(2)

with col1:
    st.info(f"DAX: {dax_status}")

with col2:
    st.info(f"USA: {usa_status}")

# --------------------------------------------------
# Marktübersicht
# --------------------------------------------------

st.header("🌍 Marktübersicht")

overview = []

for name, ticker in WATCHLIST.items():

    try:

        data = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            continue

        close = data["Close"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        if len(close) < 220:
            continue

        rsi = ta.momentum.RSIIndicator(
            close=close,
            window=14
        ).rsi()

        ema20 = ta.trend.EMAIndicator(
            close=close,
            window=20
        ).ema_indicator()

        ema50 = ta.trend.EMAIndicator(
            close=close,
            window=50
        ).ema_indicator()

        ema200 = ta.trend.EMAIndicator(
            close=close,
            window=200
        ).ema_indicator()

        price = float(close.iloc[-1])

        current_rsi = float(rsi.iloc[-1])
        current_ema20 = float(ema20.iloc[-1])
        current_ema50 = float(ema50.iloc[-1])
        current_ema200 = float(ema200.iloc[-1])

        perf6m = (
            (close.iloc[-1] /
             close.iloc[-126]) - 1
        ) * 100

        score = 0

        # EMA20 > EMA50
        if current_ema20 > current_ema50:
            score += 20

        # EMA50 > EMA200
        if current_ema50 > current_ema200:
            score += 20

        # Kurs > EMA50
        if price > current_ema50:
            score += 15

        # RSI
        if 50 <= current_rsi <= 70:
            score += 15

        # 6M Performance
        if perf6m > 0:
            score += 10

        if perf6m > 10:
            score += 10

        if perf6m > 20:
            score += 10

        if score >= 75:
            trend = "🟢"

        elif score >= 50:
            trend = "🟡"

        else:
            trend = "🔴"

        overview.append({
            "Asset": name,
            "Kurs": round(price, 2),
            "RSI": round(current_rsi, 1),
            "6M %": round(perf6m, 1),
            "Score": score,
            "Trend": trend
        })

    except Exception:
        continue

# --------------------------------------------------
# Ranking
# --------------------------------------------------

if len(overview) > 0:

    overview_df = pd.DataFrame(overview)

    overview_df = overview_df.sort_values(
        "Score",
        ascending=False
    )

    st.dataframe(
        overview_df,
        use_container_width=True
    )

    st.header("🏆 Top 3")

    top3 = overview_df.head(3)

    for _, row in top3.iterrows():

        st.success(
            f"{row['Asset']} | Score {row['Score']}"
        )

    st.header("⚠ Schwächste 3")

    weakest = overview_df.tail(3)

    for _, row in weakest.iterrows():

        st.error(
            f"{row['Asset']} | Score {row['Score']}"
        )

else:

    st.warning(
        "Keine Daten für die Marktübersicht verfügbar."
    )

# --------------------------------------------------
# Detailanalyse
# --------------------------------------------------

st.header("🔍 Detailanalyse")

asset = st.selectbox(
    "Asset auswählen",
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
        close=close,
        window=14
    ).rsi()

    ema50 = ta.trend.EMAIndicator(
        close=close,
        window=50
    ).ema_indicator()

    current_price = round(
        float(close.iloc[-1]),
        2
    )

    current_rsi = round(
        float(rsi.iloc[-1]),
        1
    )

    trend = (
        "📈 Aufwärtstrend"
        if current_price >
        float(ema50.iloc[-1])
        else "📉 Abwärtstrend"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Kurs",
            current_price
        )

    with col2:
        st.metric(
            "RSI",
            current_rsi
        )

    st.write(trend)

    st.subheader("📊 Kursverlauf")

    st.line_chart(close)

except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

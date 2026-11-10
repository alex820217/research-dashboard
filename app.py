import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

st.set_page_config(
    page_title="📈 Research Dashboard",
    layout="wide"
)

st.title("📈 Börsen Research Dashboard")

# ------------------------------------------------
# Märkte
# ------------------------------------------------

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

# ------------------------------------------------
# Marktstatus
# ------------------------------------------------

hour = datetime.now().hour

if 9 <= hour < 17:
    dax_status = "🟢 Offen"
else:
    dax_status = "🔴 Geschlossen"

if 15 <= hour < 22:
    us_status = "🟢 Offen"
else:
    us_status = "🔴 Geschlossen"

st.subheader("🕒 Marktstatus")

col1, col2 = st.columns(2)

with col1:
    st.info(f"DAX: {dax_status}")

with col2:
    st.info(f"USA: {us_status}")

# ------------------------------------------------
# Marktübersicht
# ------------------------------------------------

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

        ema200 = ta.trend.EMAIndicator(
            close=close,
            window=200
        ).ema_indicator()

        atr = ta.volatility.AverageTrueRange(
            high=data["High"],
            low=data["Low"],
            close=close,
            window=14
        ).average_true_range()

        price = float(close.iloc[-1])

        current_rsi = float(
            rsi.iloc[-1]
        )

        current_atr = float(
            atr.iloc[-1]
        )

        atr_percent = (
            current_atr / price
        ) * 100

        score = 0

        # Trend

        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 20

        if ema50.iloc[-1] > ema200.iloc[-1]:
            score += 20

        # Kurs

        if price > ema50.iloc[-1]:
            score += 15

        # RSI

        if 50 <= current_rsi <= 70:
            score += 15

        # ATR

        if atr_percent < 2:
            score += 10

        # Performance

        perf6m = (
            (close.iloc[-1] /
             close.iloc[-126]) - 1
        ) * 100

        if perf6m > 0:
            score += 10

        # Relative Stärke

        if perf6m > 15:
            score += 10

        # KO Risiko

        if atr_percent < 2:
            risiko = "🟢 Niedrig"

        elif atr_percent < 4:
            risiko = "🟡 Mittel"

        else:
            risiko = "🔴 Hoch"

        overview.append({
            "Asset": name,
            "Kurs": round(price, 2),
            "RSI": round(current_rsi, 1),
            "ATR %": round(
                atr_percent, 2
            ),
            "Score": score,
            "KO Risiko": risiko
        })

    except:
        pass

overview_df = pd.DataFrame(
    overview
)

overview_df = overview_df.sort_values(
    "Score",
    ascending=False
)

st.dataframe(
    overview_df,
    use_container_width=True
)

# ------------------------------------------------
# Top Listen
# ------------------------------------------------

st.header("🏆 Top Research Scores")

top3 = overview_df.head(3)

for _, row in top3.iterrows():

    st.success(
        f"{row['Asset']} | Score {row['Score']}"
    )

st.header("⚠ Schwächste Märkte")

bottom3 = overview_df.tail(3)

for _, row in bottom3.iterrows():

    st.error(
        f"{row['Asset']} | Score {row['Score']}"
    )

# ------------------------------------------------
# Detailanalyse
# ------------------------------------------------

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

    atr = ta.volatility.AverageTrueRange(
        high=data["High"],
        low=data["Low"],
        close=close,
        window=14
    ).average_true_range()

    st.header(asset)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Kurs",
            round(
                float(close.iloc[-1]),
                2
            )
        )

    with col2:
        st.metric(
            "RSI",
            round(
                float(rsi.iloc[-1]),
                1
            )
        )

    with col3:
        st.metric(
            "ATR",
            round(
                float(atr.iloc[-1]),
                2
            )
        )

    st.subheader("📊 Kursverlauf")

    st.line_chart(close)

except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

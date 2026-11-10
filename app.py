import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

st.set_page_config(
    page_title="📈 Intraday Market Scanner",
    layout="wide"
)

st.title("📈 Intraday Market Scanner")

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

dax_open = 9 <= hour < 17
us_open = 15 <= hour < 22

col1, col2 = st.columns(2)

with col1:
    st.info(
        f"DAX: {'🟢 Offen' if dax_open else '🔴 Geschlossen'}"
    )

with col2:
    st.info(
        f"USA: {'🟢 Offen' if us_open else '🔴 Geschlossen'}"
    )

# --------------------------------------------------
# Marktübersicht
# --------------------------------------------------

st.header("🌍 Intraday Übersicht")

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
        high = data["High"]
        low = data["Low"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        if hasattr(high, "columns"):
            high = high.iloc[:, 0]

        if hasattr(low, "columns"):
            low = low.iloc[:, 0]

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

        try:

            atr = ta.volatility.AverageTrueRange(
                high=high,
                low=low,
                close=close,
                window=14
            ).average_true_range()

            atr_value = float(
                atr.iloc[-1]
            )

        except:

            atr_value = 0

        price = float(close.iloc[-1])

        current_rsi = float(rsi.iloc[-1])

        current_ema20 = float(
            ema20.iloc[-1]
        )

        current_ema50 = float(
            ema50.iloc[-1]
        )

        current_ema200 = float(
            ema200.iloc[-1]
        )

        if atr_value > 0:
            atr_percent = (
                atr_value / price
            ) * 100
        else:
            atr_percent = 0

        perf20 = (
            (close.iloc[-1] /
             close.iloc[-20]) - 1
        ) * 100

        # ------------------------
        # Intraday Score
        # ------------------------

        score = 0

        if current_ema20 > current_ema50:
            score += 20

        if current_ema50 > current_ema200:
            score += 20

        if price > current_ema20:
            score += 20

        if 50 <= current_rsi <= 70:
            score += 15

        if atr_percent < 2:
            score += 15

        elif atr_percent < 4:
            score += 10

        else:
            score += 5

        if perf20 > 0:
            score += 10

        # ------------------------
        # KO Risiko
        # ------------------------

        if atr_percent < 2:
            ko_risk = "🟢 Niedrig"

        elif atr_percent < 4:
            ko_risk = "🟡 Mittel"

        else:
            ko_risk = "🔴 Hoch"

        # ------------------------
        # Marktstatus
        # ------------------------

        market_open = "✅"

        if ticker in [
            "MSFT",
            "AAPL",
            "NVDA",
            "AMZN",
            "^NDX",
            "^GSPC"
        ]:
            market_open = (
                "✅" if us_open else "⛔"
            )

        elif ticker == "^GDAXI":
            market_open = (
                "✅" if dax_open else "⛔"
            )

        overview.append({
            "Asset": name,
            "Kurs": round(price, 2),
            "RSI": round(current_rsi, 1),
            "ATR %": round(atr_percent, 2),
            "Markt": market_open,
            "KO Risiko": ko_risk,
            "Score": score
        })

    except Exception:
        continue

# --------------------------------------------------
# Ranking
# --------------------------------------------------

if len(overview) > 0:

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

    st.header("🔥 Top 3 Intraday Kandidaten")

    for _, row in (
        overview_df.head(3)
        .iterrows()
    ):

        st.success(
            f"{row['Asset']} | "
            f"Score {row['Score']} | "
            f"{row['KO Risiko']}"
        )

    st.header("⚠ Schwächste Märkte")

    for _, row in (
        overview_df.tail(3)
        .iterrows()
    ):

        st.error(
            f"{row['Asset']} | "
            f"Score {row['Score']}"
        )

else:

    st.warning(
        "Keine Daten verfügbar."
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
        close=close
    ).rsi()

    current_price = round(
        float(close.iloc[-1]),
        2
    )

    current_rsi = round(
        float(rsi.iloc[-1]),
        1
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

    st.line_chart(close)

except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

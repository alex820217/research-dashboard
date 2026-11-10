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

    st.line_chart(close)st.divider()

st.header("🌍 Marktübersicht")

overview = []

for name, symbol in WATCHLIST.items():

    try:

        d = yf.download(
            symbol,
            period="6mo",
            auto_adjust=True,
            progress=False
        )

        if d.empty:
            continue

        c = d["Close"]

        if hasattr(c, "columns"):
            c = c.iloc[:, 0]

        rsi_all = ta.momentum.RSIIndicator(
            close=c
        ).rsi()

        ema50_all = ta.trend.EMAIndicator(
            close=c,
            window=50
        ).ema_indicator()

        last_price = float(c.iloc[-1])

        last_rsi = float(
            rsi_all.iloc[-1]
        )

        last_ema = float(
            ema50_all.iloc[-1]
        )

        s = 0

        if last_price > last_ema:
            s += 50

        if last_rsi > 50:
            s += 50

        if s >= 80:
            trend_icon = "🟢"

        elif s >= 50:
            trend_icon = "🟡"

        else:
            trend_icon = "🔴"

        overview.append({

            "Asset": name,

            "Kurs":
                round(last_price, 2),

            "RSI":
                round(last_rsi, 1),

            "Score":
                s,

            "Trend":
                trend_icon

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


except Exception as e:

    st.error(
        f"Fehler: {e}"
    )

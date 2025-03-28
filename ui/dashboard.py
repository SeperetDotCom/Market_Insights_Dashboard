import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objs as go
import pandas as pd

from core.api import fetch_tickers
from core.api import fetch_tickers_cached
from core.fetch_data import get_stock_data

from core.presets import load_presets
from core.indicators import get_indicator  # For later plugin-style indicator support

# Load strategy presets
presets = load_presets()
preset_names = list(presets.keys())
selected_preset = st.sidebar.selectbox("Strategy Preset", preset_names)
active_indicators = presets[selected_preset]["indicators"]

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="SeperetPulse",
    page_icon = os.path.join("../..", "assets", "Seperet_NightVision_Slam.gif"),  # Favicon
    layout="wide"
)

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Market Dashboard by seperet.com")

# ---- TICKER DATA ----
regions_to_load = ["US", "TO", "CN", "HK", "LSE"]  # Add/remove global exchanges as needed
regions_key = ",".join(regions_to_load)

# Optional refresh
if st.sidebar.button("🔄 Refresh Ticker List"):
    fetch_tickers_cached.cache_clear()

all_ticker_list = fetch_tickers_cached(regions_key)

# Build dictionary for dropdown and filtering
ticker_data = {
    item["symbol"]: {
        "name": item["name"],
        "exchange": item["exchange"]
    }
    for item in all_ticker_list
    if item["symbol"] and item["name"] and item["exchange"]
}

# ---- SIDEBAR CONTROLS ----
exchange_filter = st.sidebar.selectbox("Filter by Exchange", ["All", "NASDAQ", "NYSE"])

# Filter and sort ticker list
filtered_tickers = {
    k: v for k, v in ticker_data.items()
    if exchange_filter == "All" or v["exchange"] == exchange_filter
}
sorted_tickers = sorted(filtered_tickers.keys())

# Select multiple tickers using multiselect
selected_tickers = st.sidebar.multiselect(
    "Choose Ticker(s)", sorted_tickers, default=[sorted_tickers[0]] if sorted_tickers else []
)

# ---- Period and Interval Controls with Validation ----
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

# Define which intervals are allowed for each period
interval_options = {
    "1mo": ["1d", "1h", "15m"],
    "3mo": ["1d", "1h", "15m"],
    "6mo": ["1d", "1h"],
    "1y":  ["1d", "1h"],
    "2y":  ["1d", "1h"],
    "5y":  ["1d"]
}
allowed_intervals = interval_options.get(period, ["1d"])
interval = st.sidebar.selectbox("Interval", allowed_intervals)

# ---- TABS FOR MULTI-TICKER VIEW ----
if selected_tickers:
    tab_objects = st.tabs(selected_tickers)

    for i, ticker in enumerate(selected_tickers):
        with tab_objects[i]:
            company_name = filtered_tickers[ticker]["name"]
            st.subheader(f"{ticker} - {company_name}")

            # Load data and validate
            df = get_stock_data(ticker, period=period, interval=interval)

            # (Debugging)
            st.write(f"Data for {ticker}")
            st.dataframe(df.head(5))  # shows first rows

            if df.empty or not all(col in df.columns for col in ["Date", "Open", "High", "Low", "Close"]):
                st.warning(f"⚠️ No valid price data available for {ticker}.")
                continue

            # --- Main Candlestick Chart ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            ))

            # --- Moving Average (default show) ---
            if active_indicators.get("ma_20", False):
                ma_func = get_indicator("ma_20")
                ma = ma_func(df) if ma_func else pd.Series()
                if isinstance(ma, pd.Series) and not ma.isna().all():
                    hide_ma = st.toggle(f"Hide 20-day MA", value=False, key=f"hide_ma_{ticker}")
                    if not hide_ma:
                        fig.add_trace(go.Scatter(x=df["Date"], y=ma, mode="lines", name="20-day MA"))

            # --- Render Main Chart ---
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- RSI (default show) ---
            if active_indicators.get("rsi", False):
                rsi_func = get_indicator("rsi")
                rsi = rsi_func(df) if rsi_func else pd.Series()
                if isinstance(rsi, pd.Series) and not rsi.isna().all():
                    hide_rsi = st.toggle(f"Hide RSI", value=False, key=f"hide_rsi_{ticker}")
                    if not hide_rsi:
                        st.line_chart(rsi, height=150)

else:
    st.info("Please select at least one ticker to begin.")
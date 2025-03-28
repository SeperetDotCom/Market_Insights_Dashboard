import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="SeperetPulse",
    page_icon=os.path.join("../..", "assets", "Seperet_NightVision_Slam.gif"),  # Favicon
    layout="wide"
)

if st.session_state.get("page_refresh"):
    st.session_state.page_refresh = False

import plotly.graph_objs as go
import pandas as pd
from core.api import fetch_tickers_cached
from core.fetch_data import get_stock_data
from core.presets import load_presets
from core.indicators import get_indicator

# Load strategy presets
presets = load_presets()
preset_names = list(presets.keys())
selected_preset = st.sidebar.selectbox("Strategy Preset", preset_names)
active_indicators = presets[selected_preset]["indicators"]

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Market Dashboard by seperet.com")

# ---- TICKER DATA ----

# Add/remove global exchanges here as needed (in "regions_to_load").
# **NOTES** Finnhub requires paid API plan for global exhanges. If you add them, you will get an error. 
regions_to_load = ["US"]
regions_key = ",".join(regions_to_load)

if st.sidebar.button("Refresh Ticker List"):
    fetch_tickers_cached.cache_clear()

all_ticker_list = fetch_tickers_cached(regions_key)

# Build dictionary and group by exchange
ticker_data = {}
exchange_groups = {}
for item in all_ticker_list:
    exchange = item.get("exchange", "")
    if (
        item["symbol"]
        and item["name"]
        and exchange
        and not exchange.startswith("BATS")
        and not exchange.startswith("OOTC")
        and exchange in ["XNAS", "XNYS", "XASE"]
    ):
        ticker_data[item["symbol"]] = {
            "name": item["name"],
            "exchange": item["exchange"]
        }
        exchange_groups.setdefault(item["exchange"], []).append(item["symbol"])

# ---- SIDEBAR CONTROLS ----
available_exchanges = sorted(exchange_groups.keys())
selected_exchange = st.sidebar.selectbox("Select Exchange", ["All"] + available_exchanges)

import json

preset_path = os.path.join(os.path.dirname(__file__), "..", "core", "user_dashboard.json")

# Save Dashboard
if st.sidebar.button("💾 Save Tickers as Preset"):
    with open(preset_path, "w") as f:
        json.dump(st.session_state.selected_tickers, f)
    st.sidebar.success("Preset saved!")

# Load Dashboard
if st.sidebar.button("📂 Load Ticker Preset"):
    try:
        with open(preset_path, "r") as f:
            st.session_state.selected_tickers = json.load(f)
            st.session_state.page_refresh = True
            st.stop()
    except FileNotFoundError:
        st.sidebar.warning("No saved preset found.")


# Filter tickers based on selected exchange
filtered_tickers = (
    ticker_data if selected_exchange == "All"
    else {k: v for k, v in ticker_data.items() if v["exchange"] == selected_exchange}
)
sorted_filtered_tickers = sorted(filtered_tickers.keys())

# Select one ticker at a time to add
ticker_display_map = {
    f"{symbol} - {filtered_tickers[symbol]['name']}": symbol
    for symbol in sorted_filtered_tickers
}
selected_label = st.sidebar.selectbox("Search or select Ticker", list(ticker_display_map.keys()) if ticker_display_map else ["None"])
selected_ticker = ticker_display_map.get(selected_label, "None")

# Track selected tickers for viewing (use session state)
if "selected_tickers" not in st.session_state:
    st.session_state.selected_tickers = []

# Auto-add selected ticker
if (
    selected_ticker
    and selected_ticker != "None"
    and selected_ticker not in st.session_state.selected_tickers
):
    st.session_state.selected_tickers.append(selected_ticker)
    st.rerun()

# Sidebar option to clear all tickers
if st.sidebar.button("🧹 Clear All Tickers"):
    st.session_state.selected_tickers = []

# ---- Period and Interval Controls with Validation ----
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
interval_options = {
    "1mo": ["1d", "1h", "15m"],
    "3mo": ["1d", "1h", "15m"],
    "6mo": ["1d", "1h"],
    "1y": ["1d", "1h"],
    "2y": ["1d", "1h"],
    "5y": ["1d"]
}
allowed_intervals = interval_options.get(period, ["1d"])
interval = st.sidebar.selectbox("Interval", allowed_intervals)

# ---- TABS FOR MULTI-TICKER VIEW ----
if st.session_state.selected_tickers:
    tab_objects = st.tabs(st.session_state.selected_tickers)

    for i, ticker in enumerate(st.session_state.selected_tickers):
        with tab_objects[i]:
            company_name = ticker_data[ticker]["name"]

            # Option to remove this tab
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.subheader(f"{ticker} - {company_name}")
            with col2:
                if st.button("✖️", key=f"remove_{ticker}"):
                    st.session_state.selected_tickers.remove(ticker)
                    st.session_state.page_refresh = True
                    st.stop()

            # Load data and validate
            df = get_stock_data(ticker, period=period, interval=interval)

            if df.empty or not all(col in df.columns for col in ["Date", "Open", "High", "Low", "Close"]):
                st.warning(f"\u26a0\ufe0f No valid price data available for {ticker}.")
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
    st.info("Please select a ticker from the left to begin.")

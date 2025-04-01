# Main dashboard file called via "streamlit run ui/dashboard.py"

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import json

from core.api import fetch_tickers_cached
from core.fetch_data import get_stock_data
from core.presets import load_presets
from core.indicators import get_indicator

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="SeperetPulse",
    page_icon=os.path.join("../..", "assets", "Seperet_NightVision_Slam.gif"),
    layout="wide"
)

# ---- SESSION INIT ----
if "selected_tickers" not in st.session_state:
    st.session_state.selected_tickers = []
if "confirm_remove" not in st.session_state:
    st.session_state.confirm_remove = {}

# ---- HEADER ----
st.title("Market Dashboard")
st.subheader("by seperet.com")
st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

# ---- STYLES ----
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #ddd;
    padding-bottom: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"] {
    padding: 6px 14px;
    border-radius: 8px 8px 0 0;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #f1f1f1;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
.stButton>button {
    background-color: transparent;
    color: white;
    border-radius: 6px;
    border: 1px solid transparent;
}
.stButton>button:hover {
    background-color: #fee2e2;
    border: 1px solid #b91c1c;
    color: #b91c1c;
}
#refresh_tickers button {
    background-color: #2563eb !important;
    color: white !important;
}
#refresh_tickers button:hover {
    background-color: #1e40af !important;
}
</style>
""", unsafe_allow_html=True)

# ---- LOAD TICKERS ----
regions_to_load = ["US"]
regions_key = ",".join(regions_to_load)

if st.sidebar.button("Refresh Ticker List", key="refresh_tickers"):
    fetch_tickers_cached.cache_clear()

all_ticker_list = fetch_tickers_cached(regions_key)

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

# ---- SIDEBAR ----
available_exchanges = sorted(exchange_groups.keys())
selected_exchange = st.sidebar.selectbox("Select Exchange", ["All"] + available_exchanges)

filtered_tickers = (
    ticker_data if selected_exchange == "All"
    else {k: v for k, v in ticker_data.items() if v["exchange"] == selected_exchange}
)
sorted_filtered_tickers = sorted(filtered_tickers.keys())

ticker_display_map = {
    f"{symbol} - {filtered_tickers[symbol]['name']}": symbol
    for symbol in sorted_filtered_tickers
}
selected_label = st.sidebar.selectbox("Search or select Ticker", list(ticker_display_map.keys()) if ticker_display_map else ["None"])
selected_ticker = ticker_display_map.get(selected_label, "None")

if (
    selected_ticker
    and selected_ticker != "None"
    and selected_ticker not in st.session_state.selected_tickers
):
    st.session_state.selected_tickers.append(selected_ticker)
    st.rerun()

# ---- PERIOD + INTERVAL ----
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
interval_options = {
    "1mo": ["1d", "1h", "15m"],
    "3mo": ["1d", "1h", "15m"],
    "6mo": ["1d", "1h"],
    "1y": ["1d", "1h"],
    "2y": ["1d", "1h"],
    "5y": ["1d"]
}
interval = st.sidebar.selectbox("Interval", interval_options.get(period, ["1d"]))

# ---- STRATEGY PRESETS ----
presets = load_presets()
preset_names = list(presets.keys())
selected_preset = st.sidebar.selectbox("Strategy Preset", preset_names)
active_indicators = presets[selected_preset]["indicators"]

st.sidebar.markdown("---")
preset_path = os.path.join(os.path.dirname(__file__), "..", "core", "user_dashboard.json")

if st.sidebar.button("💾 Save Tickers as Preset"):
    with open(preset_path, "w") as f:
        json.dump(st.session_state.selected_tickers, f)
    st.sidebar.success("Preset saved!")

if st.sidebar.button("📂 Load Ticker Preset"):
    try:
        with open(preset_path, "r") as f:
            st.session_state.selected_tickers = json.load(f)
            st.rerun()
    except FileNotFoundError:
        st.sidebar.warning("No saved preset found.")

if st.sidebar.button("🧹 Clear All Tickers"):
    st.session_state.selected_tickers = []
    st.session_state.confirm_remove.clear()
    st.rerun()

# ---- TABS VIEW ----
if st.session_state.selected_tickers:
    tabs = st.tabs(st.session_state.selected_tickers)

    for i, ticker in enumerate(st.session_state.selected_tickers.copy()):  # copy to avoid mutation during loop
        with tabs[i]:
            company_name = ticker_data[ticker]["name"]
            col1, col2 = st.columns([0.88, 0.12])

            with col1:
                st.subheader(f"{ticker} - {company_name}")
            with col2:
                # Tab remove logic
                if ticker in st.session_state.confirm_remove:
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Yes", key=f"yes_{ticker}"):
                            st.session_state.selected_tickers.remove(ticker)
                            st.session_state.confirm_remove.pop(ticker, None)
                            st.rerun()
                    with col_no:
                        if st.button("❌ No", key=f"no_{ticker}"):
                            st.session_state.confirm_remove.pop(ticker, None)
                            st.rerun()
                else:
                    if st.button("❌", key=f"remove_{ticker}"):
                        st.session_state.confirm_remove[ticker] = True
                        st.rerun()

            # Load chart data
            df = get_stock_data(ticker, period=period, interval=interval)
            if df.empty or not all(col in df.columns for col in ["Date", "Open", "High", "Low", "Close"]):
                st.warning(f"⚠️ No valid price data available for {ticker}.")
                continue

            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            ))

            if active_indicators.get("ma_20", False):
                ma_func = get_indicator("ma_20")
                ma = ma_func(df) if ma_func else pd.Series()
                if isinstance(ma, pd.Series) and not ma.isna().all():
                    hide_ma = st.toggle(f"Hide 20-day MA", value=False, key=f"hide_ma_{ticker}")
                    if not hide_ma:
                        fig.add_trace(go.Scatter(x=df["Date"], y=ma, mode="lines", name="20-day MA"))

            fig.update_layout(
                xaxis_rangeslider_visible=False,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            if active_indicators.get("rsi", False):
                rsi_func = get_indicator("rsi")
                rsi = rsi_func(df) if rsi_func else pd.Series()
                if isinstance(rsi, pd.Series) and not rsi.isna().all():
                    hide_rsi = st.toggle(f"Hide RSI", value=False, key=f"hide_rsi_{ticker}")
                    if not hide_rsi:
                        st.line_chart(rsi, height=150)
else:
    st.info("Please select a ticker from the left to begin.")

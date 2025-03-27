import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objs as go
from core.fetch_data import get_stock_data
from core.analysis import moving_average, relative_strength_index

st.set_page_config(layout="wide")
st.title("SeperetPulse - Market Analysis Dashboard")

ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "15m"])

if ticker:
    df = get_stock_data(ticker, period=period, interval=interval)
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))

        if st.sidebar.checkbox("Show 20-day MA"):
            ma = moving_average(df)
            fig.add_trace(go.Scatter(x=df['Date'], y=ma, mode='lines', name='20-day MA'))

        if st.sidebar.checkbox("Show RSI"):
            rsi = relative_strength_index(df)
            st.line_chart(rsi, height=150)

        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to retrieve data. Please check the ticker symbol.")

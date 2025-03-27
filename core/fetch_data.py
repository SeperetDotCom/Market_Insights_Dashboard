import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="6mo", interval="1d"):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )

        if data.empty:
            return pd.DataFrame()

        data.reset_index(inplace=True)

        # Flatten MultiIndex columns if needed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)


        # Rename 'index' to 'Date' if needed
        if 'Date' not in data.columns and 'index' in data.columns:
            data.rename(columns={"index": "Date"}, inplace=True)

        return data

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

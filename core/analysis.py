# Analytical formulas

# ------------------------

# Current:
# - MA
# - RA

import pandas as pd

def moving_average(data, window=20):
    if "Close" not in data.columns or data["Close"].dropna().empty:
        return pd.Series()
    return data["Close"].rolling(window=window).mean()

def relative_strength_index(data, window=14):
    if "Close" not in data.columns or data["Close"].dropna().empty:
        return pd.Series()
    delta = data["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

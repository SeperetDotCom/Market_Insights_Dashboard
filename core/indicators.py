import pandas as pd

# Registry of available indicators
_INDICATOR_REGISTRY = {}

def register_indicator(name):
    """
    Decorator to register a new indicator under a given name.
    """
    def decorator(func):
        _INDICATOR_REGISTRY[name] = func
        return func
    return decorator

def get_indicator(name):
    """
    Retrieve an indicator function by name.
    """
    return _INDICATOR_REGISTRY.get(name)

def list_indicators():
    """
    Return a list of all registered indicator names.
    """
    return list(_INDICATOR_REGISTRY.keys())

# --- Built-in Indicators ---

@register_indicator("ma_20")
def moving_average(data, window=20):
    if "Close" not in data.columns or data["Close"].dropna().empty:
        return pd.Series()
    return data["Close"].rolling(window=window).mean()

@register_indicator("rsi")
def relative_strength_index(data, window=14):
    if "Close" not in data.columns or data["Close"].dropna().empty:
        return pd.Series()
    delta = data["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@register_indicator("bollinger")
def bollinger_bands(data, window=20):
    if "Close" not in data.columns or data["Close"].dropna().empty:
        return pd.DataFrame()
    ma = data["Close"].rolling(window=window).mean()
    std = data["Close"].rolling(window=window).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    return pd.DataFrame({"upper": upper, "lower": lower, "ma": ma})

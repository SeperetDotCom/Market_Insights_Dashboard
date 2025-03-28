import os
import requests
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")

@lru_cache(maxsize=1)
def fetch_tickers_cached(regions_str):
    """
    Cached version of fetch_tickers that takes a single hashable string (comma-separated region codes).
    """
    regions = regions_str.split(",")
    return fetch_tickers(regions)

def fetch_tickers(regions=["US"]):
    all_data = []

    for region in regions:
        url = f"https://finnhub.io/api/v1/stock/symbol?exchange={region}&token={FINNHUB_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            tickers = [
                {
                    "symbol": item["symbol"],
                    "name": item["description"],
                    "exchange": item["mic"]
                }
                for item in data if item.get("type") == "Common Stock"
            ]
            all_data.extend(tickers)

        except Exception as e:
            print(f"API Error for region {region}: {e}")
    
    return all_data

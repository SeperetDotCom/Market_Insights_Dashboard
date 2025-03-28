import os
import requests
from dotenv import load_dotenv

load_dotenv()
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_tickers(region="US"):
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange={region}&token={FINNHUB_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Parse only active tickers with displayable names
        tickers = [
            {
                "symbol": item["symbol"],
                "name": item["description"],
                "exchange": item["mic"]
            }
            for item in data if item.get("type") == "Common Stock"
        ]
        return tickers
    except Exception as e:
        print(f"API Error: {e}")
        return []

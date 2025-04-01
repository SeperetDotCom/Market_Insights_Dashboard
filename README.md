# SeperetPulse Market Insights Dashboard

![Repo Size](https://img.shields.io/github/repo-size/denv3rr/Market_Insights_Dashboard)
![Last Commit](https://img.shields.io/github/last-commit/denv3rr/Market_Insights_Dashboard)
![Issues](https://img.shields.io/github/issues/denv3rr/Market_Insights_Dashboard)
![License](https://img.shields.io/github/license/denv3rr/Market_Insights_Dashboard)
![Website](https://img.shields.io/website?url=https%3A%2F%2Fseperet.com&label=seperet.com)

- A lightweight, open-source market analysis dashboard designed for traders, analysts, and researchers.
- Fetches live market data and displays interactive charts with technical indicators.

<br></br>
<br></br>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">

## Features

- Fetch live stock data via Yahoo Finance and Finnhub.io
- Interactive candlestick charts (Plotly)
- Toggle overlays like:
  - 20-day MA (Moving Average)
  - RSI (Relative Strength Index)
- Sidebar input for custom ticker, timeframe, and interval
- Drag/drop-ready preset support (coming soon)

---

## Usage

### 1. Clone the Repo or Download ZIP

```bash
git clone https://github.com/denv3rr/Market_Insights_Dashboard.git
cd SeperetPulse
```

### 2. Install Requirements

- streamlit  
- yfinance  
- plotly  
- pandas
- python-dotenv  
- requests (for Finnhub API)

```bash
pip install -r requirements.txt
```

### 3. Set Up Finnhub.io API Key

To use stock symbol data from [Finnhub](https://finnhub.io):

1. Create a free account at: [https://finnhub.io/register](https://finnhub.io/register)
2. Go to your [API dashboard](https://finnhub.io/dashboard) to get your token.
3. Add this token to your environment variables or `.env` file:
    ```bash
    export FINNHUB_API_KEY=your_api_key_here
    ```
4. Alternatively, update the key directly in `core/api.py` if needed.

> ⚠️ **Note:** Some international exchanges require a paid plan with Finnhub.

### 4. Launch UI Dashboard

```bash
streamlit run ui/dashboard.py
```

Or double-click `run_dashboard.bat` (Windows only).

---

## Roadmap

- Add drawing tools (trend lines, zones)
- Enable backtesting custom strategies
- Import/export preset overlays
- Real-time data streaming (WebSockets)
- Modular quant strategy plugin system

---

## Reminders / To-Do

- ⏳ Tab auto-close timeout if no confirmation
- ⏳ Transition/fade animations
- ⏳ Tab reordering support
- ⏳ Dark/light mode toggle
- ⏳ Sidebar hover & dropdown styling polish
- ⏳ Improve tab confirmation UX (click-away, no flicker)
- ⏳ Optional logging/export feature (CSV or JSON)

---

<div align="center">
  <a href="https://seperet.com">
    <img src="https://github.com/denv3rr/denv3rr/blob/main/Seperet_Slam_White.gif"/>
  </a>
</div>

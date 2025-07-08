import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TWELVEDATA_API_KEY")

def search_ticker_options(company_name):
    """
    Searches NSE symbols using Twelve Data API and returns a list like:
    ['INFY.NS - Infosys Ltd']
    """
    if not API_KEY:
        print("❌ Twelve Data API key not set in .env")
        return []

    url = f"https://api.twelvedata.com/symbol_search?symbol={company_name}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        results = response.json().get("data", [])
        options = []

        for stock in results:
            symbol = stock.get("symbol", "")
            name = stock.get("instrument_name", "")
            exchange = stock.get("exchange", "")

            if exchange == "NSE":
                options.append(f"{symbol}.NS - {name}")

        return options

    except Exception as e:
        print("❌ Twelve Data error:", e)
        return []

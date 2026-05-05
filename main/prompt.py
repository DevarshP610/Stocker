import yfinance as yf

def fetch_market_data(ticker):
    """Fetches real-time price action for a given ticker."""
    try:
        asset = yf.Ticker(ticker)
        data = asset.history(period="1d")
        
        if data.empty:
            return {"status": "error", "message": f"No data found for {ticker}."}
        
        current_price = data['Close'].iloc[-1]
        daily_high = data['High'].iloc[-1]
        daily_low = data['Low'].iloc[-1]
        volume = data['Volume'].iloc[-1]
        
        return {
            "status": "success",
            "data": {
                "price": round(current_price, 4),
                "high": round(daily_high, 4),
                "low": round(daily_low, 4),
                "volume": int(volume)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# This allows the file to be run by itself for testing!
if __name__ == "__main__":
    test_ticker = "BTC-USD"
    print(f"Running standalone data test for {test_ticker}...")
    print(fetch_market_data(test_ticker))
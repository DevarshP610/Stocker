import yfinance as yf

def fetch_market_intelligence(ticker_symbol: str, period: str = "6mo", interval: str = "1d") -> dict:
    """Fetches chart data and news, supporting dynamic timeframes."""
    try:
        # Auto-correct common crypto tickers for Yahoo Finance
        if ticker_symbol.upper() in ["BTC", "ETH", "SOL", "DOGE", "XRP"]:
            ticker_symbol = f"{ticker_symbol.upper()}-USD"

        ticker = yf.Ticker(ticker_symbol)
        
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            return {"status": "error", "message": f"No market data found for {ticker_symbol}."}
        
        chart_data = []
        for i in range(len(hist)):
            row = hist.iloc[i]
            chart_data.append((i, row['Open'], row['Close'], row['Low'], row['High']))
            
        current_price = hist['Close'].iloc[-1]
        
        recent_trend = hist['Close'].tail(5).tolist()
        trend_str = " -> ".join([f"${p:.2f}" for p in recent_trend])

        news_data = ticker.news[:5] if ticker.news else []
        if news_data:
            news_text = "\n".join([f"• {n.get('title', 'Headline')} (Source: {n.get('publisher', 'Unknown')})" for n in news_data])
        else:
            news_text = "No recent news headlines available in the datastream."

        return {
            "status": "success",
            "current_price": current_price,
            "chart_data": chart_data,
            "trend": trend_str,
            "news": news_text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
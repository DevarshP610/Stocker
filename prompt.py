import ollama
import yfinance as yf
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%B %d, %Y, %H:%M:%S")

def generate_response(prompt):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Llama 3.2 is analyzing...")
    response = ollama.chat(
        model='llama3.2:3b', 
        messages=[{'role': 'user', 'content': prompt}],
    )
    return response['message']['content']

def get_live_data(ticker):
    try:
        # Create a session to help bypass basic blocks
        stock = yf.Ticker(ticker)
        
        
        df = stock.history(period="3d", interval="1h")
        
        if df.empty:

            df = stock.history(period="1mo", interval="1d")

        if not df.empty:
            current_price = df['Close'].iloc[-1]
            try:
                news_items = stock.news[:2]
                headlines = [n['title'] for n in news_items] if news_items else ["Stable market action."]
            except:
                headlines = ["News data temporarily restricted by provider."]
            
            return current_price, headlines
            
        return None, ["Yahoo returned an empty dataset."]
        
    except Exception as e:
        return None, [f"Connection error: {str(e)}"]

watchlist = ["NVDA", "TSLA", "BTC-USD", "ETH-USD", "EURUSD=X"]

print(f"--- Market Analysis for {current_time} ---")
print("Fetching real-time data for high-volume assets...")

market_context = ""
for symbol in watchlist:
    price, news = get_live_data(symbol)
    if price:
        news_block = " | ".join(news)
        market_context += f"Asset: {symbol} | Price: ${price:.2f} | News: {news_block}\n"
    else:
        print(f"Skipping {symbol}: Could not retrieve data.")

prompt = f"""You are an elite quantitative analyst AI. 
Current Time: {current_time}

LIVE MARKET DATA:
{market_context}

YOUR TASK:
Using ONLY the data provided above, identify the top 3 trades. 
Cross-reference the current price with the news sentiment.

OUTPUT FORMAT:
- Ticker: [Symbol]
- Direction: [Long/Short]
- Catalyst: [1 sentence based on the news provided]
- Target: [Exact price]
- Stop: [Exact price]
"""

#execution
if market_context.strip():
    result = generate_response(prompt)
    print("\n" + "="*30)
    print("AI TRADING SIGNALS")
    print("="*30)
    print(result)
else:
    print("Error: No market data could be retrieved. Check your internet connection.")
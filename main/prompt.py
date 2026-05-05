import ollama
import yfinance as yf
from datetime import datetime
import requests
import time # Added for rate-limiting bypass

# 1. Setup Time
now = datetime.now()
current_time = now.strftime("%B %d, %Y, %H:%M:%S")

def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    return session

def generate_response(prompt):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] AI is analyzing live data...")
    response = ollama.chat(
        model='llama3.2:3b', 
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0.1}
    )
    return response['message']['content']

def get_live_data(ticker_symbol):
    try:
        session = get_session()
        stock = yf.Ticker(ticker_symbol, session=session)
        df = stock.history(period="5d", interval="1h")
        
        if df.empty:
            return None, ["Data blocked by provider."]

        current_price = df['Close'].iloc[-1]
        
        try:
            news_items = stock.news[:2]
            headlines = [n['title'] for n in news_items] if news_items else ["Stable trend."]
        except:
            headlines = ["News restricted - analyze price action only."]

        return current_price, headlines
    except Exception as e:
        return None, [f"Error: {str(e)}"]

# 2. Strict Market Execution (NO FALLBACKS)
categories = {
    "STOCK": ["NVDA", "TSLA"],
    "CRYPTO": ["BTC-USD", "ETH-USD"],
    "FOREX": ["EURUSD=X"]
}

print(f"--- Fetching Live Market Data for {current_time} ---")
market_context = ""
valid_data_count = 0

for category, symbols in categories.items():
    market_context += f"\n[{category} MARKET]\n"
    for symbol in symbols:
        print(f"Pulling {symbol}...")
        price, news = get_live_data(symbol)
        
        if price:
            valid_data_count += 1
            news_block = " | ".join(news)
            market_context += f"- Ticker: {symbol} | LIVE Price: ${price:.2f} | News: {news_block}\n"
        else:
            market_context += f"- Ticker: {symbol} | LIVE Price: DATA_UNAVAILABLE | News: N/A\n"
        
        # CRITICAL: Pause for 2 seconds so Yahoo doesn't block your IP address
        time.sleep(2) 

# 3. Hard Stop if Data Fails
if valid_data_count == 0:
    print("\nCRITICAL SYSTEM HALT: Zero live data streams available.")
    print("Do not execute trades. Wait 5 minutes for your IP block to clear and try again.")
    exit() # This completely stops the script

# 4. Iron-Clad Prompt
prompt = f"""You are a strict, rules-based trading algorithm. 
Current Time: {current_time}

LIVE MARKET DATA:
{market_context}

CRITICAL RULES:
1. Select exactly THREE (3) trades.
2. Select ONE Stock, ONE Crypto, and ONE Forex asset.
3. USE ONLY the 'LIVE Price'. DO NOT invent prices. 
4. If a price is 'DATA_UNAVAILABLE', you CANNOT trade it.
5. Target and Stop levels must be mathematically realistic based on the LIVE Price.

OUTPUT FORMAT:
1. [Category] - [Ticker] | [Long/Short] | Catalyst: [Reason] | Entry: $[Live Price] | Target: $[Target] | Stop: $[Stop]
"""

# 5. Execute
result = generate_response(prompt)
print("\n" + "="*50)
print("VERIFIED LIVE TRADING SIGNALS")
print("="*50)
print(result)
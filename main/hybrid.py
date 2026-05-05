import os
import time
import ollama
from typing import Dict, Any

# Import your custom modules
import screen_analyzer
import prompt

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def generate_trade_signal(ticker: str, market_data: Dict[str, Any], vision_report: str) -> str:
    brain_prompt = f"""You are a strict quantitative algorithmic trading bot. Evaluate this combined data stream:

[LIVE MARKET DATA FOR {ticker}]
- Current Exact Price: ${market_data['price']}
- Daily High: ${market_data['high']}
- Daily Low: ${market_data['low']}
- Volume: {market_data['volume']}

[VISUAL CHART ANALYSIS]
{vision_report}

Based on this data, output a strict execution order. Format EXACTLY like this:
ACTION: [LONG, SHORT, or HOLD]
ENTRY: ${market_data['price']}
TARGET: [Calculate realistic target]
STOP: [Calculate tight stop-loss]
REASON: [One sentence mathematical & visual justification]"""

    try:
        response = ollama.chat(
            model='llama3.1', 
            messages=[{'role': 'user', 'content': brain_prompt}],
            options={'temperature': 0.1, 'num_ctx': 4096} 
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"Brain AI Error: {e}"

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}{Colors.BOLD}============================================{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}   HYBRID QUANTITATIVE TRADING TERMINAL     {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}============================================{Colors.ENDC}")
    
    # Keep it simple and stable: Just ask for the ticker
    ticker = input(f"\n{Colors.BLUE}Enter Asset Ticker (e.g., BTC-USD): {Colors.ENDC}").upper()
    
    print(f"\n{Colors.WARNING}Prepare your chart. Scanning screen in 3 seconds...{Colors.ENDC}")
    time.sleep(3)

    # 1. Execute Vision Agent
    print(f"\n{Colors.BLUE}👁️  [1/3] Initializing LLaVA Vision Agent on Chart Region...{Colors.ENDC}")
    vision_response: Dict[str, Any] = screen_analyzer.run_vision_agent()
    
    if vision_response.get('status') == 'error':
        print(f"{Colors.FAIL}Vision Error: {vision_response.get('message')}{Colors.ENDC}")
        return
    print(f"{Colors.GREEN}✓ Visual Data Extracted.{Colors.ENDC}")
    vision_data: str = str(vision_response.get('data', ''))

    # 2. Execute Data Agent
    print(f"\n{Colors.BLUE}📡 [2/3] Fetching Live API Data for {ticker}...{Colors.ENDC}")
    market_response: Dict[str, Any] = prompt.fetch_market_data(ticker)
    
    if market_response.get('status') == 'error':
        print(f"{Colors.FAIL}API Error: {market_response.get('message')}{Colors.ENDC}")
        return
        
    market_data: Dict[str, Any] = market_response['data']
    print(f"{Colors.GREEN}✓ Live Price Confirmed: ${market_data['price']}{Colors.ENDC}")

    # 3. Execute Quant Agent (The Brain)
    print(f"\n{Colors.BLUE}🧠 [3/3] Initializing Llama 3.1 Quant Logic...{Colors.ENDC}")
    final_signal: str = generate_trade_signal(ticker, market_data, vision_data)

    # 4. Final Output
    print(f"\n{Colors.GREEN}{Colors.BOLD}============================================{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}            FINAL EXECUTION ORDER           {Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}============================================{Colors.ENDC}")
    print(final_signal)
    print(f"{Colors.GREEN}{Colors.BOLD}============================================{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
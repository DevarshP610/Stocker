import requests

def generate_trade_signal(ticker: str, intel_data: dict) -> str:
    prompt = f"""You are an elite quantitative analyst.
Analyze the following live API data stream for {ticker}:

CURRENT MARKET PRICE: ${intel_data['current_price']:.2f}
LAST 5 CLOSING PERIODS: {intel_data['trend']}

LATEST GLOBAL NEWS & SENTIMENT:
{intel_data['news']}

=== MACRO SYNTHESIS ===
[3-4 sentence objective analytical breakdown]

=== EXECUTION DIRECTIVE ===
ACTION: [LONG, SHORT, or NEUTRAL]
ENTRY: $[Price]
TARGET: $[Price]
STOP: $[Price]
REASON: [One sentence trigger]
"""

    payload = {
        "model": "llama3.1", # <--- BACK TO 3.1
        "messages": [
            {"role": "system", "content": "You are a precise quant algorithm. Output only the requested format."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.2}
    }

    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status()
        return response.json()['message']['content'].strip()
    except Exception as e:
        return f"Neural API Link Failed: {str(e)}"
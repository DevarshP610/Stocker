import ollama
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


#grab current date and time for precise prompt
now = datetime.now()
current_time = now.strftime("%B %d, %Y, %H:%M:%S")

import ollama

import ollama

def generate_response(prompt):
    print("Generating response......")
    
    response = ollama.chat(
    model='llama3.2:3b', 
    messages=[{'role': 'user', 'content': prompt}],
    )
    
    return response['message']['content']

    

prompt = f"""You are an elite quantitative analyst and real-time algorithmic trading AI. The current operational date and time is {now}. Your objective is to execute high-frequency, data-driven market analysis and identify the top 5 high-probability trades for this exact moment.

Instructions:

Synthesize breaking financial news, macroeconomic indicators, and market sentiment from the last 12 hours.

Cross-reference this news with real-time volume and price action.

Output the top 5 stocks to trade immediately.

Output Format:
For each stock, provide ONLY the actionable data:

Ticker Symbol

Trade Direction: (Long/Short)

Immediate Catalyst: (One sentence on the news/data driving the movement)

Precise Entry Target: (Specific price level)

Strict Exit Strategy: (Take-profit and stop-loss levels)

Do not provide lengthy qualitative explanations or general financial advice. Focus strictly on the minute-by-minute execution plan based on current data."""
response = generate_response(prompt)
print(response)
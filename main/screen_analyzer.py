import json
import ollama
import pyautogui
import time
import os

def analyze_screen():
    print("Preparing screenshot... Switch to your chart now!")
    time.sleep(3)

    image_path = "current_screen.png"
    
    try:
        # 1. Load the dynamic coordinates from the setup tool
        if not os.path.exists("config.json"):
            print("\nERROR: config.json not found!")
            print("Please run 'python setup_bounds.py' first to select your chart area.")
            return
            
        with open("config.json", "r") as f:
            config = json.load(f)
            # Convert the list back into a tuple format (X, Y, Width, Height)
            chart_region = tuple(config["region"])
            
        # 2. Take a screenshot of ONLY that specific region
        pyautogui.screenshot(image_path, region=chart_region)
        print(f"Screenshot saved using dynamic bounds {chart_region}.")
        print("Sending to LLaVA (The Heavyweight Vision Model)...")

    except Exception as e:
        print(f"PyAutoGUI Error: {e}")
        return

    try:
        # 3. THE UPGRADED PROMPT: Asking for real technical analysis
        prompt = """You are an expert quantitative analyst. Look at the provided trading terminal screenshot. 
Please provide a highly structured analysis with the following exactly:

PRICE: [Extract the exact current trading price]
TREND: [Analyze the recent candles: Bullish, Bearish, or Ranging]
KEY PATTERN: [Name any visible candlestick patterns or support/resistance levels]
SIGNAL: [LONG or SHORT]
RATIONALE: [One sentence explaining the technical reason for this signal]"""
        
        response = ollama.chat(
            model='llava', 
            messages=[{
                'role': 'user', 
                'content': prompt,
                'images': [image_path] 
            }],
            options={'temperature': 0.1} # Keeps the AI analytical and grounded
        )
        
        # 4. Print the final output
        print("\n" + "="*40)
        print("LLaVA TECHNICAL ANALYSIS")
        print("="*40)
        print(response['message']['content'].strip())
        print("="*40)
        
    except Exception as e:
        print(f"\nOllama Error: {e}")
        print("Tip: Make sure Ollama is running in the background and 'llava' is downloaded.")

if __name__ == "__main__":
    analyze_screen()
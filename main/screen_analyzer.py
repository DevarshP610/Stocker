import ollama
import pyautogui
import time
import os

def analyze_screen():
    print("Preparing screenshot... Switch to your chart now!")
    time.sleep(3)

    image_path = "current_screen.png"
    
    try:
        # We can go back to taking a full screenshot, LLaVA is smart enough to handle it!
        pyautogui.screenshot(image_path)
        print(f"Screenshot saved. Sending to LLaVA (The Heavyweight Vision Model)...")
        
        if not os.path.exists(image_path):
            print("Error: Screenshot file was not created.")
            return

    except Exception as e:
        print(f"PyAutoGUI Error: {e}")
        return

    try:
        # THE UPGRADED PROMPT: We can now ask for real technical analysis
        prompt = """You are an expert quantitative analyst. Look at the provided trading terminal screenshot. 
Please provide a highly structured analysis with the following exactly:

PRICE: [Extract the exact current trading price]
TREND: [Analyze the recent candles: Bullish, Bearish, or Ranging]
KEY PATTERN: [Name any visible candlestick patterns or support/resistance levels]
SIGNAL: [LONG or SHORT]
RATIONALE: [One sentence explaining the technical reason for this signal]"""
        
        response = ollama.chat(
            model='llava', # <--- UPGRADED MODEL
            messages=[{
                'role': 'user', 
                'content': prompt,
                'images': [image_path] 
            }],
            options={'temperature': 0.1} 
        )
        
        print("\n" + "="*40)
        print("LLaVA TECHNICAL ANALYSIS")
        print("="*40)
        print(response['message']['content'].strip())
        print("="*40)
        
    except Exception as e:
        print(f"Ollama Error: {e}")

if __name__ == "__main__":
    analyze_screen()
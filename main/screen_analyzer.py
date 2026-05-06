import json
import pyautogui
import time
import os
import base64
import requests
from PIL import Image

def run_vision_agent() -> dict:
    # --- ABSOLUTE PATH LOGIC ---
    # This finds the directory where THIS file (screen_analyzer.py) lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We join that directory with the filenames to get full absolute paths
    config_path = os.path.join(current_dir, "config.json")
    image_path = os.path.join(current_dir, "current_screen.jpg")
    
    try:
        # Check if config exists using the absolute path
        if not os.path.exists(config_path):
            return {"status": "error", "message": f"config.json not found at {config_path}. Run set_bounds.py first."}
            
        with open(config_path, "r") as f:
            config = json.load(f)
            chart_region = tuple(config["region"])
            

        raw_img = pyautogui.screenshot(region=chart_region)
        raw_img = raw_img.convert('RGB')
        

        raw_img.thumbnail((336, 336), Image.Resampling.LANCZOS) 
        

        raw_img.save(image_path, "JPEG", quality=75)

        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    except Exception as e:
        return {"status": "error", "message": f"Screenshot failed: {e}"}


    vision_prompt = """Focus ONLY on the far right side of this chart (most recent 10-15 candles). Do NOT guess the price.
Answer with exactly these three lines:
TREND: [Bullish, Bearish, or Ranging]
PATTERN: [Name any visible candlestick patterns or momentum shifts]
MOMENTUM: [Up or Down]"""
    
    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": vision_prompt,
                "images": [img_b64]
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096
        },
        "keep_alive": 0 # Flushes model from RAM immediately after use
    }

    try:
        # Native HTTP request to Ollama
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status() 
        data = response.json()
        
        return {"status": "success", "data": data['message']['content'].strip()}
        
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"HTTP Error: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Ollama Error: {e}"}

if __name__ == "__main__":
    print("Running standalone vision test...")
    # Delay to give you time to switch to the chart window
    time.sleep(3)
    result = run_vision_agent()
    print(result)
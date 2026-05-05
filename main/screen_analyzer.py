import json
import ollama
import pyautogui
import time
import os
from PIL import Image

def run_vision_agent() -> dict:
    image_path = "current_screen.jpg"
    
    try:
        if not os.path.exists("config.json"):
            return {"status": "error", "message": "config.json not found. Run set_bounds.py first."}
            
        with open("config.json", "r") as f:
            config = json.load(f)
            chart_region = tuple(config["region"])
            
        # Take screenshot
        raw_img = pyautogui.screenshot(region=chart_region)
        
        # THE FIX: Strip Alpha channel and force exact native 336x336 resolution
        raw_img = raw_img.convert('RGB')
        raw_img.thumbnail((336, 336), Image.Resampling.LANCZOS) 
        raw_img.save(image_path, "JPEG", quality=75)

    except Exception as e:
        return {"status": "error", "message": f"Screenshot failed: {e}"}

    try:
        vision_prompt = """Focus ONLY on the far right side of this chart (most recent 10-15 candles). Do NOT guess the price.
Answer with exactly these three lines:
TREND: [Bullish, Bearish, or Ranging]
PATTERN: [Name any visible candlestick patterns or momentum shifts]
MOMENTUM: [Up or Down]"""
        
        response = ollama.chat(
            model='llava', 
            messages=[{'role': 'user', 'content': vision_prompt, 'images': [image_path]}],
            options={
                'temperature': 0.1,
                'num_ctx': 4096  # THE FIX: Expand the memory buffer so it doesn't crash
            } 
        )
        return {"status": "success", "data": response['message']['content'].strip()}
        
    except Exception as e:
        return {"status": "error", "message": f"LLaVA Error: {e}"}
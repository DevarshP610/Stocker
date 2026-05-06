import customtkinter as ctk
import threading
import sys
import os
import time
from typing import Dict, Any, cast

# --- [DEBUG] THE MODULAR BRIDGE ---
print("--- [DEBUG] GUI STARTUP SEQUENCE INITIATED ---")

# 1. Find the root 'AI-Stock-Investor' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 2. Find the 'main' directory where your agents live
MAIN_PATH = os.path.join(BASE_DIR, 'main')

# 3. Force Python to look inside the 'main' folder
if MAIN_PATH not in sys.path:
    sys.path.append(MAIN_PATH)

print(f"--- [DEBUG] MAIN_PATH added to sys.path: {MAIN_PATH}")

try:
    # Now we can import them directly because the folder is in sys.path
    import screen_analyzer # type: ignore
    import prompt          # type: ignore
    import hybrid          # type: ignore
    print("--- [DEBUG] ✓ All agents imported successfully.")
except Exception as e:
    print(f"--- [DEBUG] ❌ FATAL IMPORT ERROR: {e}")
    sys.exit(1)

# --- UI CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TradingTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Quant Terminal - v1.0")
        self.geometry("600x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self, text="HYBRID QUANTITATIVE TERMINAL", 
                                        font=ctk.CTkFont(size=22, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Controls
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1)

        self.ticker_entry = ctk.CTkEntry(self.control_frame, placeholder_text="Enter Ticker (e.g. BTC-USD)", height=40)
        self.ticker_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.execute_btn = ctk.CTkButton(self.control_frame, text="RUN HYBRID ANALYSIS", height=45, 
                                        fg_color="#1f538d", font=ctk.CTkFont(weight="bold"), 
                                        command=self.start_analysis_thread)
        self.execute_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Console
        self.console_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13))
        self.console_textbox.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.log_to_console("System Ready. All agents connected.")

    def log_to_console(self, text):
        self.console_textbox.insert("end", f"> {text}\n")
        self.console_textbox.see("end")

    def start_analysis_thread(self):
        ticker = self.ticker_entry.get().upper().strip()
        if not ticker:
            self.log_to_console("ERROR: Please enter a ticker.")
            return
        self.execute_btn.configure(state="disabled", text="ANALYSIS IN PROGRESS...")
        self.console_textbox.delete("1.0", "end")
        threading.Thread(target=self._run_workflow, args=(ticker,), daemon=True).start()

    def _run_workflow(self, ticker):
        self.log_to_console(f"Initiating workflow for {ticker}...")
        time.sleep(2)
        try:
            # 1. Vision
            self.log_to_console("Step 1: Analyzing Chart Patterns (LLaVA)...")
            vision_res = cast(Dict[str, Any], screen_analyzer.run_vision_agent())
            
            if vision_res.get('status') == 'error':
                self.log_to_console(f"CRITICAL VISION ERROR: {vision_res['message']}")
            else:
                self.log_to_console("Success: Patterns identified.")
                
                # 2. Market Data
                self.log_to_console("Step 2: Fetching Market Data...")
                market_res = cast(Dict[str, Any], prompt.fetch_market_data(ticker))
                
                if market_res.get('status') == 'error':
                    self.log_to_console(f"DATA ERROR: {market_res['message']}")
                else:
                    market_data = cast(Dict[str, Any], market_res['data'])
                    self.log_to_console(f"Current Price: ${market_data.get('price', 'N/A')}")

                    # 3. Quant Logic
                    self.log_to_console("Step 3: Generating Final Signal (Llama 3.1)...")
                    signal = hybrid.generate_trade_signal(ticker, market_data, cast(str, vision_res['data']))
                    self.log_to_console("\n" + "="*35 + "\n" + signal + "\n" + "="*35)

        except Exception as e:
            self.log_to_console(f"UNEXPECTED RUNTIME ERROR: {e}")

        self.execute_btn.configure(state="normal", text="RUN HYBRID ANALYSIS")

if __name__ == "__main__":
    print("--- [DEBUG] Launching App Window...")
    app = TradingTerminal()
    app.mainloop()
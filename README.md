STOCKER

AI-Stock-Investor is an open-source, 100% local algorithmic trading assistant. It combines live market data scraping with advanced local AI models (Llama 3.1 / 3.2 for quantitative reasoning) and local Vision models (LLaVA for real-time chart pattern recognition) to generate actionable Long/Short signals.

Best of all? It runs entirely on your local hardware. No OpenAI API keys, no subscription fees, and complete data privacy.

🌟 Key Features
👀 Vision-Based Technical Analysis: Uses LLaVA (7B) to "look" at your trading terminal screen, read current prices, and identify bullish/bearish candlestick patterns using PyAutoGUI.

🧠 Advanced Quantitative Logic: Utilizes Meta's Llama 3 models to process live data streams and calculate realistic Entry, Target, and Stop-Loss levels.

💻 Desktop Automation: Ready to be paired with GUI automation to physically execute trades on any broker terminal (TradingView, MetaTrader, Web Brokers).

🔒 100% Local & Private: Your financial data never leaves your machine.

📡 Live Market Data Bypass: Includes custom user-agent sessions to pull live Yahoo Finance data without getting rate-limited.

🚀 Installation Guide
Step 1: Clone the Repository
Bash
git clone https://github.com/DevarshP610/Stocker.git
cd AI-Stock-Investor
Step 2: Install Python Dependencies
Make sure you have Python installed, then run:

Bash
pip install -r requirements.txt
(If you don't have a requirements.txt yet, run: pip install ollama pyautogui yfinance pandas requests Pillow)

Step 3: Install Ollama (The AI Engine)
This project relies on Ollama to run Large Language Models locally.

Windows: Download and install from Ollama's official website.

Mac/Linux: Run the terminal command: curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh

Step 4: Download the AI Models
Once Ollama is installed, open a new terminal window and pull the required models.

For the Vision Analyzer (Chart Reading):

Bash
ollama pull llava
For the Quantitative Analyzer (Text/Data Reasoning):
(Note: If you have 8GB RAM, use llama3.2:3b. If you have 16GB+ RAM, use llama3.1 for better logic).

Bash
ollama pull llama3.2:3b
# OR
ollama pull llama3.1
💻 Usage
1. The Screen Analyzer (Vision Bot)
This script takes a screenshot of your active chart and uses LLaVA to read the technicals.

Open your trading chart (e.g., TradingView) and maximize it.

Run the script:

Bash
python screen-analyzer.py
You have 3 seconds to Alt+Tab to your chart. The AI will snap a screenshot and provide a structured Long/Short signal based on visible patterns.

2. The Data Prompt (Text Bot)
This script pulls live pricing and news data for Stocks, Crypto, and Forex, feeding it into Llama for signal generation.

Bash
python prompt.py
🛠 Hardware Requirements
Minimum: 8GB RAM (Runs Moondream/Llama 3.2:3b comfortably).

Recommended: 16GB+ RAM (Required for LLaVA 7B and Llama 3.1 8B).

OS: Windows, macOS, or Linux.

🤝 Contributing & Support
If you find this project helpful for your algorithmic trading journey, please leave a ⭐️ Star on this repository! It helps the project rank higher on GitHub and Google Search, bringing in more contributors to build better features.

Pull requests are actively welcome! If you have ideas for better prompts, new data sources, or improved UI automation, feel free to fork and submit a PR.

⚠️ Disclaimer
This project is for educational and research purposes only. The AI models can and will hallucinate or misinterpret technical charts. Do not use this bot to trade real money without thorough testing in a paper-trading environment. The creators are not responsible for any financial losses incurred using this software.
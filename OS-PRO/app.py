import sys
import os
import time
import threading
import subprocess
import numpy as np
import pyqtgraph as pg
from typing import Dict, Any, cast

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QTextEdit, QFrame, QProgressBar, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPointF, QRectF
from PyQt6.QtGui import QFont, QColor, QPicture, QPainter

# --- THE MODULAR BRIDGE ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PATH = os.path.join(BASE_DIR, 'main')
if MAIN_PATH not in sys.path:
    sys.path.append(MAIN_PATH)

try:
    import screen_analyzer # type: ignore
    import prompt          # type: ignore
    import hybrid          # type: ignore
except ImportError as e:
    print(f"FATAL IMPORT ERROR: {e}")
    sys.exit(1)

# --- CUSTOM CANDLESTICK CLASS FOR PYQTGRAPH ---
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, chart_data):
        pg.GraphicsObject.__init__(self)
        self.chart_data = chart_data  # [ (time, open, close, min, max), ... ]
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('#71717A', width=1)) # Wick color
        
        # Calculate candle width safely
        if len(self.chart_data) > 1:
            w = (self.chart_data[1][0] - self.chart_data[0][0]) / 3.0
        else:
            w = 0.3
        
        for (t, open_p, close_p, min_p, max_p) in self.chart_data:
            # Draw wick
            p.drawLine(QPointF(t, min_p), QPointF(t, max_p))
            
            # Draw body
            if open_p > close_p:
                p.setBrush(pg.mkBrush('#F43F5E')) # Bearish (Soft Red)
                p.setPen(pg.mkPen('#F43F5E'))
            else:
                p.setBrush(pg.mkBrush('#2DD4BF')) # Bullish (Teal)
                p.setPen(pg.mkPen('#2DD4BF'))
            
            p.drawRect(QRectF(t - w, open_p, w * 2, close_p - open_p))
            
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

# --- BACKGROUND THREAD SIGNALS ---
class WorkerSignals(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str) # ticker, signal_text
    error = pyqtSignal(str)

# --- AI INSIGHT UI PANEL ---
class AIAnalysisCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("AI SYNTHESIS")
        header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #A1A1AA; letter-spacing: 2px;")
        layout.addWidget(header)

        self.signal_label = QLabel("AWAITING DATA")
        self.signal_label.setFont(QFont("Inter", 22, QFont.Weight.Bold))
        self.signal_label.setStyleSheet("color: #71717A;")
        layout.addWidget(self.signal_label)

        layout.addWidget(QLabel("Analysis Output:"))
        self.insight_box = QTextEdit()
        self.insight_box.setReadOnly(True)
        self.insight_box.setPlaceholderText("System idle. Initialize analysis to generate insights.")
        layout.addWidget(self.insight_box)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready.")
        self.status_label.setStyleSheet("color: #A1A1AA; font-size: 11px;")
        layout.addWidget(self.status_label)

    def update_insight(self, text):
        self.insight_box.append(text + "\n")
        text_upper = text.upper()
        if "LONG" in text_upper or "BULLISH" in text_upper:
            self.signal_label.setText("LONG BIAS")
            self.signal_label.setStyleSheet("color: #2DD4BF;") 
        elif "SHORT" in text_upper or "BEARISH" in text_upper:
            self.signal_label.setText("SHORT BIAS")
            self.signal_label.setStyleSheet("color: #F43F5E;") 
        elif "NEUTRAL" in text_upper:
            self.signal_label.setText("NEUTRAL")
            self.signal_label.setStyleSheet("color: #A1A1AA;")

# --- MAIN APPLICATION WINDOW ---
class ResearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Vision & Quant Interface")
        self.resize(1200, 750)

        # Load Stylesheet
        try:
            with open("theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("theme.qss not found. Using default styles.")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- TOP CONTROL BAR ---
        control_bar = QFrame()
        control_bar.setObjectName("Card")
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(20, 15, 20, 15)

        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Target Asset (e.g., AAPL)")
        self.ticker_input.setFixedWidth(200)
        control_layout.addWidget(self.ticker_input)

        self.bounds_btn = QPushButton("1. Calibrate Vision (Set Bounds)")
        self.bounds_btn.setObjectName("ToolBtn")
        self.bounds_btn.clicked.connect(self.run_bounds_tool)
        control_layout.addWidget(self.bounds_btn)

        control_layout.addStretch()

        self.analyze_btn = QPushButton("2. Initialize AI Analysis")
        self.analyze_btn.setObjectName("PrimaryBtn")
        self.analyze_btn.clicked.connect(self.start_analysis)
        control_layout.addWidget(self.analyze_btn)

        main_layout.addWidget(control_bar)

        # --- LOWER SPLIT AREA ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Chart Display
        chart_frame = QFrame()
        chart_frame.setObjectName("Card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        
        chart_title = QLabel("DATA VISUALIZATION")
        chart_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #71717A;")
        chart_layout.addWidget(chart_title)

        # Initialize PyQtGraph
        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget()
        self.plot.setBackground('transparent')
        self.plot.showGrid(x=True, y=True, alpha=0.1)
        self.plot.getAxis('left').setPen('#3F3F46')
        self.plot.getAxis('bottom').setPen('#3F3F46')
        
        chart_layout.addWidget(self.plot)
        splitter.addWidget(chart_frame)

        # Right: AI Insights
        self.ai_card = AIAnalysisCard()
        splitter.addWidget(self.ai_card)
        
        # Sizing Rules
        splitter.setSizes([700, 450])
        main_layout.addWidget(splitter, stretch=1)

        # Connect Signals
        self.signals = WorkerSignals()
        self.signals.log.connect(self.update_status)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.analysis_complete)
        self.signals.error.connect(self.analysis_error)

        # Generate initial mock candles so it looks like a real chart
        self.generate_mock_candles()

    def generate_mock_candles(self, start_price=2350):
        """Generates realistic looking candle data to populate the graph."""
        self.plot.clear()
        data = []
        current_price = start_price
        for i in range(60):
            open_p = current_price
            close_p = open_p + np.random.normal(0, 10)
            high_p = max(open_p, close_p) + abs(np.random.normal(0, 5))
            low_p = min(open_p, close_p) - abs(np.random.normal(0, 5))
            data.append((i, open_p, close_p, low_p, high_p))
            current_price = close_p
            
        self.last_candle_x = 59
        self.last_candle_close = current_price
            
        candlesticks = CandlestickItem(data)
        self.plot.addItem(candlesticks)

    def add_ai_target_dot(self, signal_text):
        """Parses the AI text for ENTRY or TARGET prices and drops a dot on the chart."""
        target_price = None
        
        # Super simple parser: Looks for a '$' and grabs the number after it
        if "$" in signal_text:
            try:
                # Find the first dollar amount mentioned (usually ENTRY or TARGET)
                parts = signal_text.split("$")
                price_str = parts[1].split()[0].replace(',', '')
                target_price = float(price_str)
            except:
                pass

        # If we couldn't find a price, just place it near the last candle
        if not target_price:
            target_price = self.last_candle_close

        # Create the visual targeting dot
        scatter = pg.ScatterPlotItem(
            size=15, 
            pen=pg.mkPen(None), 
            brush=pg.mkBrush('#8B5CF6'), # Violet Dot
            symbol='o'
        )
        scatter.addPoints([{'pos': (self.last_candle_x + 2, target_price)}])
        self.plot.addItem(scatter)

        # Add the text label next to the dot
        text = pg.TextItem("AI Target / Entry", anchor=(0, 0.5), color="#D4D4D8")
        text.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        text.setPos(self.last_candle_x + 3, target_price)
        self.plot.addItem(text)

    def run_bounds_tool(self):
        self.update_status("Launching bounding box tool...")
        script_path = os.path.join(MAIN_PATH, 'set_bounds.py')
        try:
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            self.update_status(f"Error launching bounds tool: {e}")

    def update_status(self, msg):
        self.ai_card.status_label.setText(msg)
        self.ai_card.insight_box.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def update_progress(self, val):
        self.ai_card.progress_bar.setValue(val)

    def start_analysis(self):
        ticker = self.ticker_input.text().upper().strip()
        if not ticker:
            self.update_status("Error: Provide a target asset.")
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Synthesizing...")
        self.ai_card.insight_box.clear()
        self.ai_card.signal_label.setText("ANALYZING...")
        self.ai_card.signal_label.setStyleSheet("color: #D4D4D8;")
        
        # Hide the UI to prevent photobombing the chart screenshot
        self.showMinimized() 
        
        threading.Thread(target=self._worker, args=(ticker,), daemon=True).start()

    def _worker(self, ticker):
        try:
            self.signals.log.emit("Switching context to chart region. Wait 3s...")
            self.signals.progress.emit(10)
            time.sleep(3)

            self.signals.log.emit("Executing LLaVA Vision Agent...")
            vision_res = cast(Dict[str, Any], screen_analyzer.run_vision_agent())
            self.signals.progress.emit(40)
            
            if vision_res.get('status') == 'error':
                self.signals.error.emit(vision_res['message'])
                return
            
            self.signals.log.emit("Fetching API Market Parameters...")
            market_res = cast(Dict[str, Any], prompt.fetch_market_data(ticker))
            self.signals.progress.emit(70)
            
            if market_res.get('status') == 'error':
                self.signals.error.emit(market_res['message'])
                return
            
            market_data = cast(Dict[str, Any], market_res['data'])

            self.signals.log.emit("Compiling Final Hybrid Signal...")
            signal = hybrid.generate_trade_signal(ticker, market_data, cast(str, vision_res['data']))
            self.signals.progress.emit(100)
            
            self.signals.finished.emit(ticker, signal)

        except Exception as e:
            self.signals.error.emit(str(e))

    def analysis_complete(self, ticker, signal):
        # Bring window back up
        self.showNormal()
        self.activateWindow()

        self.update_status("Analysis Complete.")
        self.ai_card.update_insight(signal)
        
        # Drop the AI analysis dot on the chart
        self.add_ai_target_dot(signal)
        
        self.reset_ui()

    def analysis_error(self, error_msg):
        self.showNormal()
        self.update_status(f"CRITICAL ERROR: {error_msg}")
        self.ai_card.signal_label.setText("SYSTEM FAULT")
        self.ai_card.signal_label.setStyleSheet("color: #F43F5E;")
        self.reset_ui()

    def reset_ui(self):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("2. Initialize AI Analysis")
        QApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use Fusion style as a solid base for dark mode
    app.setStyle("Fusion")
    
    window = ResearchApp()
    window.show()
    sys.exit(app.exec())
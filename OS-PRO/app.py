import sys
import os
import threading
from typing import Dict, Any

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QTextEdit, QFrame, QProgressBar, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPointF, QRectF
from PyQt6.QtGui import QFont, QPicture, QPainter
import pyqtgraph as pg

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PATH = os.path.join(BASE_DIR, 'main')
if MAIN_PATH not in sys.path:
    sys.path.append(MAIN_PATH)

try:
    import data_engine # type: ignore
    import hybrid      # type: ignore
except ImportError as e:
    print(f"FATAL IMPORT ERROR: {e}")
    sys.exit(1)

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, chart_data):
        pg.GraphicsObject.__init__(self)
        self.chart_data = chart_data 
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('#71717A', width=1)) 
        
        if len(self.chart_data) > 1:
            w = (self.chart_data[1][0] - self.chart_data[0][0]) / 3.0
        else:
            w = 0.3
            
        for (t, open_p, close_p, min_p, max_p) in self.chart_data:
            p.drawLine(QPointF(t, min_p), QPointF(t, max_p))
            if open_p > close_p:
                p.setBrush(pg.mkBrush('#F43F5E')) 
                p.setPen(pg.mkPen('#F43F5E'))
            else:
                p.setBrush(pg.mkBrush('#2DD4BF')) 
                p.setPen(pg.mkPen('#2DD4BF'))
            p.drawRect(QRectF(t - w, open_p, w * 2, close_p - open_p))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

class WorkerSignals(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    api_data_ready = pyqtSignal(list, str) 
    finished = pyqtSignal(str, str) 
    error = pyqtSignal(str)

class ResearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuantOS Intelligence Node")
        self.resize(1300, 800)

        try:
            with open("theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass
            
        self.active_period = "6mo"
        self.active_interval = "1d"

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # TOP CONTROL BAR
        control_bar = QFrame()
        control_bar.setObjectName("Card")
        control_layout = QHBoxLayout(control_bar)
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Enter Asset (e.g., AAPL, BTC-USD)")
        self.ticker_input.setFixedWidth(300)
        control_layout.addWidget(self.ticker_input)

        control_layout.addStretch()

        self.analyze_btn = QPushButton("INITIATE NEURAL SCAN")
        self.analyze_btn.setObjectName("PrimaryBtn")
        self.analyze_btn.clicked.connect(self.start_analysis)
        control_layout.addWidget(self.analyze_btn)

        main_layout.addWidget(control_bar)

        # SPLIT LAYOUT
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # CHART FRAME
        chart_frame = QFrame()
        chart_frame.setObjectName("Card")
        chart_layout = QVBoxLayout(chart_frame)
        
        # --- TIMEFRAME TOOLBAR ---
        tf_layout = QHBoxLayout()
        chart_title = QLabel("LIVE API DATA VISUALIZATION")
        chart_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #71717A;")
        tf_layout.addWidget(chart_title)
        tf_layout.addStretch()
        
        timeframes = [("1D", "1d", "1m"), ("1W", "5d", "5m"), ("1M", "1mo", "1h"), 
                      ("6M", "6mo", "1d"), ("1Y", "1y", "1d"), ("2Y", "2y", "1d")]
        
        for name, p, i in timeframes:
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: #27272A; color: #A1A1AA; border-radius: 4px; padding: 4px 8px;")
            # Use default arguments in lambda to capture the current values of p and i
            btn.clicked.connect(lambda checked=False, per=p, inv=i: self.update_timeframe(per, inv))
            tf_layout.addWidget(btn)
            
        chart_layout.addLayout(tf_layout)

        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget()
        self.plot.setBackground('transparent')
        self.plot.showGrid(x=True, y=True, alpha=0.1)
        chart_layout.addWidget(self.plot)
        left_layout.addWidget(chart_frame, stretch=2)

        # NEWS FRAME
        news_frame = QFrame()
        news_frame.setObjectName("Card")
        news_layout = QVBoxLayout(news_frame)
        news_title = QLabel("MACRO SYNTHESIS & NEWS STREAM")
        news_title.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        news_title.setStyleSheet("color: #71717A;")
        news_layout.addWidget(news_title)

        self.news_box = QTextEdit()
        self.news_box.setReadOnly(True)
        news_layout.addWidget(self.news_box)
        left_layout.addWidget(news_frame, stretch=1)

        main_splitter.addWidget(left_panel)

        # RIGHT PANEL
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_layout = QVBoxLayout(right_panel)
        
        exec_title = QLabel("EXECUTION DIRECTIVE")
        exec_title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        exec_title.setStyleSheet("color: #A1A1AA; letter-spacing: 2px;")
        right_layout.addWidget(exec_title)

        self.signal_label = QLabel("STANDBY")
        self.signal_label.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        self.signal_label.setStyleSheet("color: #71717A;")
        right_layout.addWidget(self.signal_label)

        right_layout.addWidget(QLabel("Quant Logic Output:"))
        self.insight_box = QTextEdit()
        self.insight_box.setReadOnly(True)
        right_layout.addWidget(self.insight_box)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        right_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready.")
        self.status_label.setStyleSheet("color: #A1A1AA;")
        right_layout.addWidget(self.status_label)

        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([800, 400])
        main_layout.addWidget(main_splitter, stretch=1)

        self.signals = WorkerSignals()
        self.signals.log.connect(self.update_status)
        self.signals.progress.connect(self.update_progress)
        self.signals.api_data_ready.connect(self.render_api_chart)
        self.signals.finished.connect(self.analysis_complete)
        self.signals.error.connect(self.analysis_error)

    def update_timeframe(self, period, interval):
        """Called when user clicks a timeframe button like 1D, 1W, 1Y"""
        self.active_period = period
        self.active_interval = interval
        ticker = self.ticker_input.text().upper().strip()
        if not ticker: return
        self.update_status(f"Fetching {period} chart data...")
        threading.Thread(target=self._quick_fetch, args=(ticker, period, interval), daemon=True).start()

    def _quick_fetch(self, ticker, period, interval):
        """Silently updates the chart without triggering the AI"""
        intel = data_engine.fetch_market_intelligence(ticker, period, interval)
        if intel['status'] == 'success':
            self.signals.api_data_ready.emit(intel['chart_data'], intel['news'])

    def update_status(self, msg):
        self.status_label.setText(msg)

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def render_api_chart(self, chart_data, news_text):
        self.plot.clear()
        candlesticks = CandlestickItem(chart_data)
        self.plot.addItem(candlesticks)
        
        # --- FIX: FORCE THE CHART TO AUTO-ZOOM TO THE CANDLES ---
        self.plot.autoRange()
        
        if news_text:
            self.news_box.clear()
            self.news_box.append("=== LIVE API NEWS FEED ===\n")
            self.news_box.append(news_text)

    def start_analysis(self):
        ticker = self.ticker_input.text().upper().strip()
        if not ticker:
            self.update_status("Error: Provide a target asset.")
            return

        self.analyze_btn.setEnabled(False)
        self.insight_box.clear()
        self.signal_label.setText("ANALYZING...")
        self.signal_label.setStyleSheet("color: #D4D4D8;")
        
        threading.Thread(target=self._worker, args=(ticker,), daemon=True).start()

    def _worker(self, ticker):
        try:
            self.signals.log.emit(f"Opening global API datalink for {ticker}...")
            self.signals.progress.emit(20)
            
            # Fetch data using the currently selected timeframe
            intel = data_engine.fetch_market_intelligence(ticker, self.active_period, self.active_interval)
            if intel['status'] == 'error':
                self.signals.error.emit(intel['message'])
                return
            
            self.signals.progress.emit(50)
            
            self.signals.api_data_ready.emit(intel['chart_data'], intel['news'])
            self.signals.log.emit("Data acquired. Compiling quantitative report...")

            signal = hybrid.generate_trade_signal(ticker, intel)
            self.signals.progress.emit(100)
            
            self.signals.finished.emit(ticker, signal)

        except Exception as e:
            self.signals.error.emit(str(e))

    def analysis_complete(self, ticker, signal):
        self.update_status("API Datalink Terminated. Analysis Complete.")
        
        if "=== EXECUTION DIRECTIVE ===" in signal:
            parts = signal.split("=== EXECUTION DIRECTIVE ===")
            self.news_box.append("\n" + parts[0].strip())
            self.insight_box.setText("=== EXECUTION DIRECTIVE ===\n" + parts[1].strip())
        else:
            self.insight_box.setText(signal)
            
        text_upper = signal.upper()
        if "ACTION: LONG" in text_upper:
            self.signal_label.setText("EXECUTE: LONG")
            self.signal_label.setStyleSheet("color: #2DD4BF;") 
        elif "ACTION: SHORT" in text_upper:
            self.signal_label.setText("EXECUTE: SHORT")
            self.signal_label.setStyleSheet("color: #F43F5E;") 
        else:
            self.signal_label.setText("HOLD POSITION")
            self.signal_label.setStyleSheet("color: #A1A1AA;")

        self.analyze_btn.setEnabled(True)

    def analysis_error(self, error_msg):
        self.update_status(f"CRITICAL ERROR: {error_msg}")
        self.signal_label.setText("DATALINK FAULT")
        self.signal_label.setStyleSheet("color: #F43F5E;")
        self.analyze_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ResearchApp()
    window.show()
    sys.exit(app.exec())
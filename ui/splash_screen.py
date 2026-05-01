# ui/splash_screen.py

import os
from ui.qt_compat import (
    QSplashScreen,
    QProgressBar,
    QPixmap,
    QPainter,
    QColor,
    Qt,
    QTimer,
    QApplication
)

class GBASplashScreen(QSplashScreen):
    def __init__(self, translator=None):
        self.translator = translator
        
        splash_width = 500
        splash_height = 300
        
        splash_path = os.path.join("assets", "splash.png")
        if os.path.exists(splash_path):
            try:
                pixmap = QPixmap(splash_path)
            except Exception as e:
                pixmap = QPixmap(splash_width, splash_height)
                pixmap.fill(QColor(40, 40, 60))
        else:
            pixmap = QPixmap(splash_width, splash_height)
            pixmap.fill(QColor(40, 40, 60))
        
        if pixmap.width() == 500 and pixmap.height() == 300:
            pass
        else:
            background = QPixmap(splash_width, splash_height)
            background.fill(QColor(40, 40, 60))
            
            painter = QPainter(background)
            scaled = pixmap.scaled(splash_width, splash_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (splash_width - scaled.width()) // 2
            y = (splash_height - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()
            
            pixmap = background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        presents_text = self._tr_splash("splash_presents", "CompuMax Productions Present:")
        
        font = painter.font()
        font.setPointSize(12)
        font.setItalic(True)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        painter.drawText(0, 175, splash_width, 30, Qt.AlignCenter, presents_text)
        painter.end()
        
        super().__init__(pixmap)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 250, 400, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2C2C4C;
                border-radius: 6px;
                text-align: center;
                background: #1A1A2E;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #FF6B6B, stop: 0.5 #4ECDC4, stop: 1 #45B7D1
                );
                border-radius: 4px;
            }
        """)
        
        self.setCursor(Qt.BusyCursor)

    def _tr_splash(self, key, default_text):
        if self.translator and hasattr(self.translator, 'tr'):
            return self.translator.tr(key, **{})
        return default_text

    def set_progress(self, value, message=""):
        self.progress_bar.setValue(value)
        if message:
            self.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        
        QTimer.singleShot(10, self._process_events)
    
    def _process_events(self):

        QApplication.processEvents()

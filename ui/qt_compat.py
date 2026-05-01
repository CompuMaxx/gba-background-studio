# ui/qt_compat.py
import sys


def _detect_backend():
    if sys.version_info >= (3, 10):
        try:
            import PySide6
            return "PySide6"
        except ImportError:
            pass
    try:
        import PySide2
        return "PySide2"
    except ImportError:
        pass
    try:
        import PySide6
        return "PySide6"
    except ImportError:
        pass

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    raise ImportError(
        f"No Qt backend found (Python {py_ver}).\n"
        f"Install PySide6 (Python >= 3.10) or PySide2 (Python 3.8/3.9):\n"
        f"  pip install PySide6    # Python 3.10+\n"
        f"  pip install PySide2==5.15.2  # Python 3.8/3.9"
    )

QT_BACKEND: str = _detect_backend()

if QT_BACKEND == "PySide6":
    from PySide6.QtCore import (
        Qt, Signal, Slot, QTimer, QThread, QObject,
        QSize, QRect, QPoint, QRectF, QPointF,
    )
    from PySide6.QtGui import (
        QFont, QColor, QPen, QBrush, QPixmap, QImage,
        QPainter, QIcon, QCursor, QKeySequence,
        QIntValidator, QValidator, QKeyEvent,
        QBrush, QAction,
    )
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDialog,
        QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QStackedWidget, QSplitter, QTabWidget, QTabBar,
        QLabel, QPushButton, QToolButton, QCheckBox, QRadioButton,
        QLineEdit, QSpinBox, QComboBox, QSlider, QProgressBar,
        QListWidget, QListWidgetItem,
        QGraphicsView, QGraphicsScene, QGraphicsLineItem,
        QGraphicsRectItem, QGraphicsPixmapItem,
        QFrame, QGroupBox, QSizePolicy,
        QFileDialog, QMessageBox, QColorDialog,
        QDialogButtonBox, QButtonGroup,
        QSplashScreen, QScrollArea,
        QMenu,
    )

    def exec_dialog(dlg) -> int:
        return dlg.exec()

    def exec_app(app) -> int:
        return app.exec()

else:
    from PySide2.QtCore import (
        Qt, Signal, Slot, QTimer, QThread, QObject,
        QSize, QRect, QPoint, QRectF, QPointF,
    )
    from PySide2.QtGui import (
        QFont, QColor, QPen, QBrush, QPixmap, QImage,
        QPainter, QIcon, QCursor, QKeySequence,
        QIntValidator, QValidator, QKeyEvent,
        QBrush,
    )
    from PySide2.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDialog,
        QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QStackedWidget, QSplitter, QTabWidget, QTabBar,
        QLabel, QPushButton, QToolButton, QCheckBox, QRadioButton,
        QLineEdit, QSpinBox, QComboBox, QSlider, QProgressBar,
        QListWidget, QListWidgetItem,
        QGraphicsView, QGraphicsScene, QGraphicsLineItem,
        QGraphicsRectItem, QGraphicsPixmapItem,
        QFrame, QGroupBox, QSizePolicy,
        QFileDialog, QMessageBox, QColorDialog,
        QDialogButtonBox, QButtonGroup,
        QSplashScreen, QScrollArea,
        QMenu, QAction,
    )

    def exec_dialog(dlg) -> int:
        return dlg.exec_()

    def exec_app(app) -> int:
        return app.exec_()

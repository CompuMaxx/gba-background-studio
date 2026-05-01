# ui/dialogs/gba_compatibility_dialog.py

from utils.translator import Translator
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    Qt
)

translator = Translator()

class GBACompatibilityDialog(QDialog):
    def __init__(self, original_w, original_h, adjusted_w, adjusted_h, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.tr("gba_compat_title"))
        self.setFixedSize(400, 140)
        self.setModal(True)

        layout = QVBoxLayout(self)

        msg = QLabel(translator.tr(
            "gba_compat_message",
            w=original_w, h=original_h,
            wpx=original_w * 8, hpx=original_h * 8,
            aw=adjusted_w, ah=adjusted_h,
            awpx=adjusted_w * 8, ahpx=adjusted_h * 8
        ))
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignLeft)
        layout.addWidget(msg)

        btn_layout = QHBoxLayout()
        btn_adjust = QPushButton(translator.tr("gba_compat_adjust"))
        btn_keep   = QPushButton(translator.tr("gba_compat_cancel"))
        btn_adjust.setDefault(True)
        btn_adjust.clicked.connect(self.accept)
        btn_keep.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_adjust)
        btn_layout.addWidget(btn_keep)
        layout.addLayout(btn_layout)

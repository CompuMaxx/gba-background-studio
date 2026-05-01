# ui/dialogs/new_tilemap_dialog.py

from core.config import ROT_SIZES as _ROT_SIZES
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QComboBox,
    QPushButton,
    QStackedWidget,
    QWidget,
    QFormLayout
)

class NewTilemapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else lambda k, **kw: k
        self.setWindowTitle(self._tr("dlg_new_tilemap_title"))
        self.setModal(True)
        self.setFixedSize(280, 200)

        layout = QVBoxLayout(self)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel(self._tr("dlg_mode_label")))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self._tr("dlg_text_mode"), self._tr("dlg_rot_mode")])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo)
        layout.addLayout(mode_row)

        current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4

        bpp_row = QHBoxLayout()
        bpp_row.addWidget(QLabel(self._tr("dlg_bit_depth_label")))
        self.bpp_combo = QComboBox()
        self.bpp_combo.addItems([self._tr("dlg_4bpp"), self._tr("dlg_8bpp")])
        if current_bpp == 8:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
        else:
            self.bpp_combo.setCurrentIndex(0)
        bpp_row.addWidget(self.bpp_combo)
        layout.addLayout(bpp_row)

        self.size_stack = QStackedWidget()

        text_page = QWidget()
        text_layout = QFormLayout(text_page)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 64)
        self.width_spin.setValue(32)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 256)
        self.height_spin.setValue(32)
        text_layout.addRow(self._tr("dlg_width_tiles"), self.width_spin)
        text_layout.addRow(self._tr("dlg_height_tiles"), self.height_spin)
        self.size_stack.addWidget(text_page)

        rot_page = QWidget()
        rot_layout = QHBoxLayout(rot_page)
        rot_layout.addWidget(QLabel(self._tr("dlg_size_label")))
        self.rot_size_combo = QComboBox()
        for w, h in _ROT_SIZES:
            self.rot_size_combo.addItem(f"{w}×{h}  ({w*8}×{h*8} px)", (w, h))
        rot_layout.addWidget(self.rot_size_combo)
        self.size_stack.addWidget(rot_page)

        layout.addWidget(self.size_stack)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton(self._tr("dlg_create_btn"))
        cancel_btn = QPushButton(self._tr("cancel"))
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _on_mode_changed(self, index):
        is_rot = index == 1
        self.size_stack.setCurrentIndex(1 if is_rot else 0)
        if is_rot:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
        else:
            current_bpp = getattr(self.parent(), 'current_bpp', 4) if self.parent() else 4
            self.bpp_combo.setEnabled(current_bpp != 8)
            if current_bpp != 8:
                self.bpp_combo.setCurrentIndex(0)

    def get_values(self):
        is_rot = self.mode_combo.currentIndex() == 1
        if is_rot:
            w, h = self.rot_size_combo.currentData()
            return w, h, 8, True
        bpp = 4 if self.bpp_combo.currentIndex() == 0 else 8
        return self.width_spin.value(), self.height_spin.value(), bpp, False

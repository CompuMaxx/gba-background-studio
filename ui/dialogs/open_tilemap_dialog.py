# ui/dialogs/open_tilemap_dialog.py

from core.config import ROT_SIZES as _ROT_SIZES
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)

def _get_possible_dimensions(total_tiles):
    priority_w = [32, 20, 64]
    priority = []
    others = []

    for w in range(1, total_tiles + 1):
        if total_tiles % w == 0:
            h = total_tiles // w
            if 1 <= h <= 512:
                if w == 32 or w == 20:
                    priority.append((w, h))
                elif w == 64 and h % 32 == 0:
                    priority.append((w, h))
                elif w < 32 and w != 20:
                    others.append((w, h))

    order = {32: 0, 20: 1, 64: 2}
    priority.sort(key=lambda p: (order.get(p[0], 99), p[1]))
    others.sort(key=lambda p: p[0])

    return priority + others

class OpenTilemapDialog(QDialog):
    def __init__(self, total_tiles, parent=None):
        super().__init__(parent)
        self._tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else lambda k, **kw: k
        self.setWindowTitle(self._tr("dlg_open_tilemap_title"))
        self.setModal(True)
        self.setFixedSize(300, 180)

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

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel(self._tr("dlg_size_tiles")))
        self.size_combo = QComboBox()
        self._total_bytes = total_tiles
        self._total_tiles = total_tiles // 2
        self._text_dims = _get_possible_dimensions(self._total_tiles)
        self._populate_text_sizes()
        size_row.addWidget(self.size_combo)
        layout.addLayout(size_row)

        btn_row = QHBoxLayout()
        self._ok_btn = QPushButton(self._tr("dlg_open_btn"))
        cancel_btn = QPushButton(self._tr("cancel"))
        self._ok_btn.setDefault(True)
        self._ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self._ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _populate_text_sizes(self):
        self.size_combo.clear()
        if self._text_dims:
            for w, h in self._text_dims:
                self.size_combo.addItem(f"{w} × {h}  ({w*8}×{h*8} px)", (w, h))
        else:
            self.size_combo.addItem(f"{self._total_tiles} × 1", (self._total_tiles, 1))

    def _populate_rot_sizes(self):
        self.size_combo.clear()
        valid = [(w, h) for w, h in _ROT_SIZES if w * h == self._total_bytes]
        if valid:
            for w, h in valid:
                self.size_combo.addItem(f"{w}×{h}  ({w*8}×{h*8} px)", (w, h))
            self.size_combo.setEnabled(True)
            self._ok_btn.setEnabled(True)
        else:
            self.size_combo.addItem(self._tr("dlg_no_valid_rot_size"))
            self.size_combo.setEnabled(False)
            self._ok_btn.setEnabled(False)

    def _on_mode_changed(self, index):
        is_rot = index == 1
        if is_rot:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
            self._populate_rot_sizes()
        else:
            current_bpp = getattr(self.parent(), 'current_bpp', 4) if self.parent() else 4
            self.bpp_combo.setEnabled(current_bpp != 8)
            if current_bpp != 8:
                self.bpp_combo.setCurrentIndex(0)
            self.size_combo.setEnabled(True)
            self._ok_btn.setEnabled(True)
            self._populate_text_sizes()

    def get_values(self):
        is_rot = self.mode_combo.currentIndex() == 1
        bpp = 8 if (is_rot or self.bpp_combo.currentIndex() == 1) else 4
        w, h = self.size_combo.currentData()
        return w, h, bpp, is_rot

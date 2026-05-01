# ui/dialogs/save_tilemap_dialog.py

from core.config import ROT_SIZES_SET as _ROT_SIZES
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)

_TEXT_TO_ROT_SIZES = {(32, 32), (64, 64)}

def _is_text_rot_compatible(w, h):
    return (w, h) in _TEXT_TO_ROT_SIZES

def _is_rot_text_compatible(w, h):
    if w <= 32:
        return True
    if w == 64 and h % 32 == 0:
        return True
    return False

def _has_flips(tilemap_data):
    for i in range(len(tilemap_data) // 2):
        entry = tilemap_data[i*2] | (tilemap_data[i*2+1] << 8)
        if entry & (1 << 10) or entry & (1 << 11):
            return True
    return False

def _text_to_rotation(tilemap_data, w, h):
    n = w * h
    if w > 32:
        from core.final_assets import revert_gba_tilemap_reorganization
        linear = revert_gba_tilemap_reorganization(tilemap_data, w, h, w, h)
    else:
        linear = tilemap_data
    out = bytearray(n)
    for i in range(n):
        entry = linear[i*2] | (linear[i*2+1] << 8)
        out[i] = entry & 0xFF
    return bytes(out)

def _rotation_to_text(tilemap_data, w, h):
    n = w * h
    linear = bytearray(n * 2)
    for i in range(n):
        tile_idx = tilemap_data[i] & 0xFF
        linear[i*2]   = tile_idx
        linear[i*2+1] = 0

    if w > 32:
        from core.final_assets import reorganize_tilemap_for_gba_bg
        tile_list = []
        for i in range(n):
            tile_idx = tilemap_data[i] & 0xFF
            tile_list.append((tile_idx, 0, 0, 0))
        reorganized = reorganize_tilemap_for_gba_bg(tile_list, w * 8, h * 8)
        out = bytearray()
        for tile_id, hf, vf, pal in reorganized:
            out.extend((tile_id & 0x3FF).to_bytes(2, 'little'))
        return bytes(out)
    return bytes(linear)

class SaveTilemapDialog(QDialog):
    def __init__(self, parent=None, sel_w=None, sel_h=None):
        super().__init__(parent)
        self._tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else lambda k, **kw: k
        self.setWindowTitle(self._tr("dlg_save_tilemap_title"))
        self.setModal(True)
        self.setFixedSize(340, 170)

        self._current_rot = getattr(parent, 'current_rotation_mode', False) if parent else False
        self._current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4
        et = getattr(parent, 'edit_tiles_tab', None) if parent else None
        self._tilemap_data = getattr(et, 'tilemap_data', None)
        self._w = sel_w if sel_w is not None else getattr(et, 'tilemap_width',  0)
        self._h = sel_h if sel_h is not None else getattr(et, 'tilemap_height', 0)
        if not self._tilemap_data:
            import os
            map_path = os.path.join('output', 'map.bin')
            if os.path.exists(map_path):
                with open(map_path, 'rb') as _f:
                    self._tilemap_data = _f.read()

        self._switch_blocked_reason = None
        self._can_switch = True
        
        if self._current_rot:
            if not _is_rot_text_compatible(self._w, self._h):
                self._switch_blocked_reason = self._tr(
                    'save_tilemap_rot_incompatible',
                    w=self._w, h=self._h
                )
                self._can_switch = False
        else:
            if not _is_text_rot_compatible(self._w, self._h):
                self._switch_blocked_reason = self._tr(
                    'save_tilemap_text_incompatible',
                    w=self._w, h=self._h
                )
                self._can_switch = False
            elif self._tilemap_data and _has_flips(self._tilemap_data):
                self._switch_blocked_reason = self._tr('save_tilemap_has_flips')
                self._can_switch = False

        layout = QVBoxLayout(self)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel(self._tr("dlg_mode_label")))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self._tr("dlg_text_mode"), self._tr("dlg_rot_mode")])
        if not self._can_switch:
            self.mode_combo.setCurrentIndex(1 if self._current_rot else 0)
            self.mode_combo.setEnabled(False)
        else:
            self.mode_combo.setCurrentIndex(1 if self._current_rot else 0)
            self.mode_combo.setEnabled(True)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo)
        layout.addLayout(mode_row)

        bpp_row = QHBoxLayout()
        bpp_row.addWidget(QLabel(self._tr("dlg_bit_depth_label")))
        self.bpp_combo = QComboBox()
        self.bpp_combo.addItems([self._tr("dlg_4bpp"), self._tr("dlg_8bpp")])
        if self._current_bpp == 8 or self._current_rot:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
        else:
            self.bpp_combo.setCurrentIndex(0)
        bpp_row.addWidget(self.bpp_combo)
        layout.addLayout(bpp_row)

        self._info_label = QLabel("")
        self._info_label.setWordWrap(True)
        self._info_label.setStyleSheet("QLabel { font-size: 8pt; }")
        layout.addWidget(self._info_label)

        btn_row = QHBoxLayout()
        self._save_btn = QPushButton(self._tr("dlg_save_btn"))
        cancel_btn = QPushButton(self._tr("cancel"))
        self._save_btn.setDefault(True)
        self._save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self._save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)
        
        self._update_info()

    def _on_mode_changed(self, index):
        is_rot = index == 1
        
        if is_rot:
            self.bpp_combo.setCurrentIndex(1)
            self.bpp_combo.setEnabled(False)
        else:
            self.bpp_combo.setEnabled(self._current_bpp != 8)
            if self._current_bpp != 8:
                self.bpp_combo.setCurrentIndex(0)
        self._update_info()

    def _update_info(self):
        is_rot_selected = self.mode_combo.currentIndex() == 1
        converting = is_rot_selected != self._current_rot

        if not self._can_switch and self._switch_blocked_reason:
            self._info_label.setStyleSheet("QLabel { font-size: 8pt; color: #888; }")
            self._info_label.setText(f"ℹ️ {self._switch_blocked_reason}")
            self._save_btn.setEnabled(True)
            return

        self._save_btn.setEnabled(True)
        self._info_label.setStyleSheet("QLabel { font-size: 8pt; color: #555; }")

        if not converting:
            self._info_label.setText("")
            return

        if self._current_rot and not is_rot_selected:
            self._info_label.setText(self._tr("dlg_rot_to_text_info"))
        else:
            self._info_label.setText(self._tr("dlg_text_to_rot_info"))

    def get_values(self):
        is_rot = self.mode_combo.currentIndex() == 1
        bpp = 8 if (is_rot or self.bpp_combo.currentIndex() == 1) else 4
        converted = None
        if self._tilemap_data and is_rot != self._current_rot:
            if self._current_rot and not is_rot:
                converted = _rotation_to_text(self._tilemap_data, self._w, self._h)
            else:
                converted = _text_to_rotation(self._tilemap_data, self._w, self._h)
        return bpp, is_rot, converted

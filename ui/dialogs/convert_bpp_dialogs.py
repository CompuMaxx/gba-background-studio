# ui/dialogs/convert_bpp_dialogs.py

from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QGridLayout,
    QWidget,
    QFrame,
    Qt
)
class Convert4BppDialog(QDialog):
    def __init__(self, color_count, parent=None):
        super().__init__(parent)
        
        # Get translator from parent window
        self._tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else lambda k, **kw: k
        
        self.setWindowTitle(self._tr("convert_4bpp_dialog_title"))
        self.setModal(True)
        self.setFixedWidth(360)
        self._single_mode = color_count <= 16

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        if self._single_mode:
            info = QLabel(self._tr("convert_4bpp_info_single", count=color_count))
        else:
            info = QLabel(self._tr("convert_4bpp_info_multi", count=color_count))
        info.setWordWrap(True)
        layout.addWidget(info)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)

        self._checks = []
        for i in range(16):
            col_label = QLabel(f"{i:X}")
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #555;")
            col_label.setFixedWidth(18)
            grid.addWidget(col_label, 0, i)

            cb = QCheckBox()
            cb.setFixedSize(18, 18)
            cb.setChecked(i == 0)
            cb.toggled.connect(self._on_toggled)
            self._checks.append(cb)
            grid.addWidget(cb, 1, i)

        layout.addWidget(grid_widget)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._ok_btn = QPushButton(self._tr("convert_btn"))
        self._ok_btn.setDefault(True)
        cancel_btn = QPushButton(self._tr("cancel"))
        self._ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _on_toggled(self, checked):
        if self._single_mode:
            sender = self.sender()
            if checked:
                for cb in self._checks:
                    if cb is not sender and cb.isChecked():
                        cb.blockSignals(True)
                        cb.setChecked(False)
                        cb.blockSignals(False)
        if not any(cb.isChecked() for cb in self._checks):
            self.sender().blockSignals(True)
            self.sender().setChecked(True)
            self.sender().blockSignals(False)

    def selected_palettes(self):
        return [i for i, cb in enumerate(self._checks) if cb.isChecked()]

class Convert8BppDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get translator from parent window
        self._tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else lambda k, **kw: k
        
        self.setWindowTitle(self._tr("convert_8bpp_dialog_title"))
        self.setModal(True)
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(6)

        form_layout.addWidget(QLabel(self._tr("convert_8bpp_start_index")), 0, 0)
        self._start_index = QSpinBox()
        self._start_index.setRange(0, 255)
        self._start_index.setValue(0)
        form_layout.addWidget(self._start_index, 0, 1)

        form_layout.addWidget(QLabel(self._tr("convert_8bpp_palette_size")), 1, 0)
        self._palette_size = QSpinBox()
        self._palette_size.setRange(0, 256)
        self._palette_size.setValue(0)
        self._palette_size.setSpecialValueText(self._tr("convert_8bpp_auto_size", n=256))
        form_layout.addWidget(self._palette_size, 1, 1)

        layout.addWidget(form)

        self._start_index.valueChanged.connect(self._update_auto_label)

        try:
            if parent and hasattr(parent, 'config_manager'):
                cfg = parent.config_manager
                self._start_index.setValue(int(cfg.get('CONVERSION', 'start_index', '0')))
                self._palette_size.setValue(int(cfg.get('CONVERSION', 'palette_size', '0')))
        except Exception:
            pass

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton(self._tr("convert_btn"))
        ok_btn.setDefault(True)
        cancel_btn = QPushButton(self._tr("cancel"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _update_auto_label(self, start_val):
        auto_size = 256 - start_val
        self._palette_size.setSpecialValueText(self._tr("convert_8bpp_auto_size", n=auto_size))
        if self._palette_size.value() > 0 and start_val + self._palette_size.value() > 256:
            self._palette_size.setValue(0)

    def get_values(self):
        start = self._start_index.value()
        size = self._palette_size.value()
        if size == 0:
            size = 256 - start
        return start, size

# ui/dialogs/display_settings_dialog.py

from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QDialogButtonBox,
    QFrame,
    QColor,
    Qt,
    QColorDialog
)
class ColorButton(QPushButton):
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.set_color(color)

    def set_color(self, color: QColor):
        self._color = color
        self.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #888;"
        )

    def color(self) -> QColor:
        return self._color

def _make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line

def _parse_color(value: str) -> QColor:
    try:
        r, g, b = [int(x) for x in value.split(',')]
        return QColor(r, g, b)
    except Exception:
        return QColor(0, 0, 0)

class DisplaySettingsDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        tr = main_window.translator.tr
        self.setWindowTitle(tr("display_settings"))
        self.setMinimumWidth(320)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # --- Grid color ---
        layout.addWidget(QLabel(f"<b>{tr('grid_color')}</b>"))
        grid_color_row = QHBoxLayout()
        cfg = main_window.config_manager
        gc = _parse_color(cfg.get('DISPLAY', 'grid_color', '255,255,255'))
        self._grid_color_btn = ColorButton(gc)
        self._grid_color_btn.clicked.connect(self._pick_grid_color)
        grid_color_row.addWidget(QLabel(tr('color') + ":"))
        grid_color_row.addWidget(self._grid_color_btn)
        grid_color_row.addStretch()
        layout.addLayout(grid_color_row)

        # --- Grid alpha ---
        grid_alpha_row = QHBoxLayout()
        self._grid_alpha_label = QLabel()
        self._grid_alpha_slider = QSlider(Qt.Horizontal)
        self._grid_alpha_slider.setRange(0, 100)
        ga = int(cfg.get('DISPLAY', 'grid_alpha', '180'))
        self._grid_alpha_slider.setValue(round(ga * 100 / 255))
        self._grid_alpha_label.setText(f"{self._grid_alpha_slider.value()}%")
        self._grid_alpha_slider.valueChanged.connect(self._on_grid_alpha_changed)
        grid_alpha_row.addWidget(QLabel(tr('opacity') + ":"))
        grid_alpha_row.addWidget(self._grid_alpha_slider)
        grid_alpha_row.addWidget(self._grid_alpha_label)
        layout.addLayout(grid_alpha_row)

        layout.addWidget(_make_separator())

        # --- Overlay text color ---
        layout.addWidget(QLabel(f"<b>{tr('overlay_text_color')}</b>"))
        overlay_color_row = QHBoxLayout()
        oc = _parse_color(cfg.get('DISPLAY', 'overlay_text_color', '0,0,0'))
        self._overlay_color_btn = ColorButton(oc)
        self._overlay_color_btn.clicked.connect(self._pick_overlay_color)
        overlay_color_row.addWidget(QLabel(tr('color') + ":"))
        overlay_color_row.addWidget(self._overlay_color_btn)
        overlay_color_row.addStretch()
        layout.addLayout(overlay_color_row)

        # --- Overlay alpha ---
        overlay_alpha_row = QHBoxLayout()
        self._overlay_alpha_label = QLabel()
        self._overlay_alpha_slider = QSlider(Qt.Horizontal)
        self._overlay_alpha_slider.setRange(0, 100)
        oa = int(cfg.get('DISPLAY', 'overlay_alpha', '76'))
        self._overlay_alpha_slider.setValue(round(oa * 100 / 255))
        self._overlay_alpha_label.setText(f"{self._overlay_alpha_slider.value()}%")
        self._overlay_alpha_slider.valueChanged.connect(self._on_overlay_alpha_changed)
        overlay_alpha_row.addWidget(QLabel(tr('opacity') + ":"))
        overlay_alpha_row.addWidget(self._overlay_alpha_slider)
        overlay_alpha_row.addWidget(self._overlay_alpha_label)
        layout.addLayout(overlay_alpha_row)

        # --- Buttons ---
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self._on_reject)
        layout.addWidget(buttons)

        # Snapshot for cancel (store as 0-255 internally)
        self._snapshot = {
            'grid_color': gc,
            'grid_alpha': ga,
            'overlay_color': oc,
            'overlay_alpha': oa,
        }

    def _pick_grid_color(self):
        color = QColorDialog.getColor(self._grid_color_btn.color(), self)
        if color.isValid():
            self._grid_color_btn.set_color(color)
            self.main_window.grid_manager.set_grid_color(
                color.red(), color.green(), color.blue()
            )

    def _on_grid_alpha_changed(self, value):
        self._grid_alpha_label.setText(f"{value}%")
        self.main_window.grid_manager.set_grid_alpha(round(value * 255 / 100))

    def _pick_overlay_color(self):
        color = QColorDialog.getColor(self._overlay_color_btn.color(), self)
        if color.isValid():
            self._overlay_color_btn.set_color(color)
            ep = self.main_window.edit_palettes_tab
            ep.set_overlay_text_color(color.red(), color.green(), color.blue())

    def _on_overlay_alpha_changed(self, value):
        self._overlay_alpha_label.setText(f"{value}%")
        self.main_window.edit_palettes_tab.set_overlay_alpha(round(value * 255 / 100))

    def _on_accept(self):
        cfg = self.main_window.config_manager
        gc = self._grid_color_btn.color()
        cfg.set('DISPLAY', 'grid_color', f"{gc.red()},{gc.green()},{gc.blue()}")
        cfg.set('DISPLAY', 'grid_alpha', str(round(self._grid_alpha_slider.value() * 255 / 100)))
        oc = self._overlay_color_btn.color()
        cfg.set('DISPLAY', 'overlay_text_color', f"{oc.red()},{oc.green()},{oc.blue()}")
        cfg.set('DISPLAY', 'overlay_alpha', str(round(self._overlay_alpha_slider.value() * 255 / 100)))
        self.accept()

    def _on_reject(self):
        s = self._snapshot
        gm = self.main_window.grid_manager
        gm.set_grid_color(s['grid_color'].red(), s['grid_color'].green(), s['grid_color'].blue())
        gm.set_grid_alpha(s['grid_alpha'])
        ep = self.main_window.edit_palettes_tab
        ep.set_overlay_text_color(s['overlay_color'].red(), s['overlay_color'].green(), s['overlay_color'].blue())
        ep.set_overlay_alpha(s['overlay_alpha'])
        self.reject()

# ui/color_editor.py

from ui.qt_compat import (
    QWidget,
    QGridLayout,
    QLabel,
    QSlider,
    QLineEdit,
    QHBoxLayout,
    QFont,
    QColor,
    QIntValidator,
    QKeyEvent,
    QBrush,
    QValidator,
    Qt,
    Signal
)
class Max255Validator(QValidator):
    def validate(self, input, pos):
        if not input:
            return (QValidator.Intermediate, input, pos)
        if input == '-':
            return (QValidator.Intermediate, input, pos)
        try:
            value = int(input)
            if value < 0:
                return (QValidator.Invalid, input, pos)
            if value > 255:
                return (QValidator.Intermediate, input, pos)
            return (QValidator.Acceptable, input, pos)
        except ValueError:
            return (QValidator.Invalid, input, pos)

class NoUndoLineEdit(QLineEdit):
    def keyPressEvent(self, event: QKeyEvent):
        if (event.modifiers() & Qt.ControlModifier and
            event.key() in [Qt.Key_Z, Qt.Key_Y]):
            event.ignore()
            return
            
        super().keyPressEvent(event)

class ColorEditor(QWidget):
    color_updated = Signal(int, int, int, int, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color_index = -1
        self.selected_color = QColor(0, 0, 0)
        self.original_color = (0, 0, 0)
        self.setup_ui()
        self.updating_from_sliders = False
        self.updating_from_text = False
        self.toggle_controls_enabled(False)

    def toggle_controls_enabled(self, enabled):
        self.red_slider.setEnabled(enabled)
        self.green_slider.setEnabled(enabled)
        self.blue_slider.setEnabled(enabled)
        self.red_text.setEnabled(enabled)
        self.green_text.setEnabled(enabled)
        self.blue_text.setEnabled(enabled)

    def on_color_changed(self):
        if self.updating_from_text:
            return
        self.updating_from_sliders = True
        r_slider = self.red_slider.value()
        g_slider = self.green_slider.value()
        b_slider = self.blue_slider.value()
        r = min((r_slider * 8 + 4) // 8 * 8, 248)
        g = min((g_slider * 8 + 4) // 8 * 8, 248)
        b = min((b_slider * 8 + 4) // 8 * 8, 248)
        self.red_value.setText(str(r_slider))
        self.green_value.setText(str(g_slider))
        self.blue_value.setText(str(b_slider))
        self.red_text.setText(str(r))
        self.green_text.setText(str(g))
        self.blue_text.setText(str(b))
        self.selected_color = QColor(r, g, b)
        self.color_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #000;")
        if self.selected_color_index >= 0:
            main_window = self.get_main_window()
            if (main_window and hasattr(main_window, 'edit_palettes_tab') and
                self.selected_color_index < len(main_window.edit_palettes_tab.palette_colors) and
                self.selected_color_index < len(main_window.edit_palettes_tab.palette_rects)):
                main_window.edit_palettes_tab.palette_colors[self.selected_color_index] = (r, g, b)
                main_window.edit_palettes_tab.palette_rects[self.selected_color_index].setBrush(QBrush(QColor(r, g, b)))
                self.color_updated.emit(self.selected_color_index, r, g, b, False)
        self.updating_from_sliders = False

    def limit_text_values(self):
        try:
            if self.red_text.text():
                r = int(self.red_text.text())
                r = max(0, min(255, r))
                self.red_text.setText(str(r))
            
            if self.green_text.text():
                g = int(self.green_text.text())
                g = max(0, min(255, g))
                self.green_text.setText(str(g))
            
            if self.blue_text.text():
                b = int(self.blue_text.text())
                b = max(0, min(255, b))
                self.blue_text.setText(str(b))
                
        except ValueError:
            self.red_text.setText("0")
            self.green_text.setText("0")
            self.blue_text.setText("0")

    def on_text_changed(self):
        if self.updating_from_sliders or self.updating_from_text:
            return
        self.updating_from_text = True
        try:
            r_text = self.red_text.text() or "0"
            g_text = self.green_text.text() or "0"
            b_text = self.blue_text.text() or "0"
            r = int(r_text) if r_text.lstrip('-').isdigit() else 0
            r = max(0, min(255, r))
            g = int(g_text) if g_text.lstrip('-').isdigit() else 0
            g = max(0, min(255, g))
            b = int(b_text) if b_text.lstrip('-').isdigit() else 0
            b = max(0, min(255, b))
            current_red = self.red_text.text()
            if current_red and (not current_red.isdigit() or int(current_red) != r):
                self.red_text.setText(str(r))
                self.updating_from_text = False
                return
            current_green = self.green_text.text()
            if current_green and (not current_green.isdigit() or int(current_green) != g):
                self.green_text.setText(str(g))
                self.updating_from_text = False
                return
            current_blue = self.blue_text.text()
            if current_blue and (not current_blue.isdigit() or int(current_blue) != b):
                self.blue_text.setText(str(b))
                self.updating_from_text = False
                return
            red_val = min((r + 4) // 8, 31)
            green_val = min((g + 4) // 8, 31)
            blue_val = min((b + 4) // 8, 31)
            self.red_slider.setValue(red_val)
            self.green_slider.setValue(green_val)
            self.blue_slider.setValue(blue_val)
            self.red_value.setText(str(red_val))
            self.green_value.setText(str(green_val))
            self.blue_value.setText(str(blue_val))
            r_rounded = min((red_val * 8 + 4) // 8 * 8, 248)
            g_rounded = min((green_val * 8 + 4) // 8 * 8, 248)
            b_rounded = min((blue_val * 8 + 4) // 8 * 8, 248)
            self.selected_color = QColor(r_rounded, g_rounded, b_rounded)
            self.color_preview.setStyleSheet(f"background-color: rgb({r_rounded}, {g_rounded}, {b_rounded}); border: 1px solid #000;")
            if self.selected_color_index >= 0:
                main_window = self.get_main_window()
                if (main_window and hasattr(main_window, 'edit_palettes_tab') and
                    self.selected_color_index < len(main_window.edit_palettes_tab.palette_colors) and
                    self.selected_color_index < len(main_window.edit_palettes_tab.palette_rects)):
                    main_window.edit_palettes_tab.palette_colors[self.selected_color_index] = (r_rounded, g_rounded, b_rounded)
                    main_window.edit_palettes_tab.palette_rects[self.selected_color_index].setBrush(QBrush(QColor(r_rounded, g_rounded, b_rounded)))
                    self.color_updated.emit(self.selected_color_index, r_rounded, g_rounded, b_rounded, True)
        except ValueError:
            pass
        self.updating_from_text = False

    def get_main_window(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'edit_palettes_tab') and hasattr(parent, 'edit_tiles_tab'):
                return parent
            parent = parent.parent()
        return None

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)
        layout.setVerticalSpacing(0)

        red_label = QLabel("R")
        red_label.setFont(QFont("Arial", 7, QFont.Bold))
        red_label.setFixedWidth(8)
        red_label.setFixedHeight(12)
        red_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        layout.addWidget(red_label, 0, 0)
        
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setRange(0, 31)
        self.red_slider.setValue(0)
        self.red_slider.setFixedWidth(120)
        self.red_slider.setFixedHeight(12)
        self.red_slider.valueChanged.connect(self.on_color_changed)
        layout.addWidget(self.red_slider, 0, 1)
        
        self.red_value = QLabel("0")
        self.red_value.setFont(QFont("Arial", 7))
        self.red_value.setFixedWidth(10)
        self.red_value.setFixedHeight(12)
        self.red_value.setStyleSheet("QLabel { border: none; background: transparent; }")
        self.red_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.red_value, 0, 2)

        green_label = QLabel("G")
        green_label.setFont(QFont("Arial", 7, QFont.Bold))
        green_label.setFixedWidth(8)
        green_label.setFixedHeight(12)
        green_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        layout.addWidget(green_label, 1, 0)
        
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setRange(0, 31)
        self.green_slider.setValue(0)
        self.green_slider.setFixedWidth(120)
        self.green_slider.setFixedHeight(12)
        self.green_slider.valueChanged.connect(self.on_color_changed)
        layout.addWidget(self.green_slider, 1, 1)
        
        self.green_value = QLabel("0")
        self.green_value.setFont(QFont("Arial", 7))
        self.green_value.setFixedWidth(10)
        self.green_value.setFixedHeight(12)
        self.green_value.setStyleSheet("QLabel { border: none; background: transparent; }")
        self.green_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.green_value, 1, 2)

        blue_label = QLabel("B")
        blue_label.setFont(QFont("Arial", 7, QFont.Bold))
        blue_label.setFixedWidth(8)
        blue_label.setFixedHeight(12)
        blue_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        layout.addWidget(blue_label, 2, 0)
        
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setRange(0, 31)
        self.blue_slider.setValue(0)
        self.blue_slider.setFixedWidth(120)
        self.blue_slider.setFixedHeight(12)
        self.blue_slider.valueChanged.connect(self.on_color_changed)
        layout.addWidget(self.blue_slider, 2, 1)
        
        self.blue_value = QLabel("0")
        self.blue_value.setFont(QFont("Arial", 7))
        self.blue_value.setFixedWidth(10)
        self.blue_value.setFixedHeight(12)
        self.blue_value.setStyleSheet("QLabel { border: none; background: transparent; }")
        self.blue_value.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.blue_value, 2, 2)

        self.color_preview = QLabel()
        self.color_preview.setFixedSize(35, 35)
        self.color_preview.setStyleSheet("background-color: black; border: 1px solid #000;")
        layout.addWidget(self.color_preview, 0, 3, 3, 1, Qt.AlignCenter)

        rgb_layout = QHBoxLayout()
        rgb_layout.setContentsMargins(0, 0, 0, 0)
        rgb_layout.setSpacing(3)
        
        r_label = QLabel("R:")
        r_label.setFont(QFont("Arial", 7, QFont.Bold))
        r_label.setFixedWidth(8)
        r_label.setFixedHeight(12)
        r_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        rgb_layout.addWidget(r_label)
        
        self.red_text = NoUndoLineEdit("0")
        self.red_text.setFont(QFont("Arial", 7))
        self.red_text.setFixedWidth(30)
        self.red_text.setFixedHeight(16)
        self.red_text.setValidator(QIntValidator(0, 255))
        self.red_text.setValidator(Max255Validator())
        self.red_text.textChanged.connect(self.on_text_changed)
        self.red_text.editingFinished.connect(self.limit_text_values)
        rgb_layout.addWidget(self.red_text)
        
        g_label = QLabel("G:")
        g_label.setFont(QFont("Arial", 7, QFont.Bold))
        g_label.setFixedWidth(8)
        g_label.setFixedHeight(12)
        g_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        rgb_layout.addWidget(g_label)
        
        self.green_text = NoUndoLineEdit("0")
        self.green_text.setFont(QFont("Arial", 7))
        self.green_text.setFixedWidth(30)
        self.green_text.setFixedHeight(16)
        self.green_text.setValidator(QIntValidator(0, 255))
        self.green_text.setValidator(Max255Validator())
        self.green_text.textChanged.connect(self.on_text_changed)
        self.green_text.editingFinished.connect(self.limit_text_values)
        rgb_layout.addWidget(self.green_text)
        
        b_label = QLabel("B:")
        b_label.setFont(QFont("Arial", 7, QFont.Bold))
        b_label.setFixedWidth(8)
        b_label.setFixedHeight(12)
        b_label.setStyleSheet("QLabel { border: none; background: transparent; }")
        rgb_layout.addWidget(b_label)
        
        self.blue_text = NoUndoLineEdit("0")
        self.blue_text.setFont(QFont("Arial", 7))
        self.blue_text.setFixedWidth(30)
        self.blue_text.setFixedHeight(16)
        self.blue_text.setValidator(QIntValidator(0, 255))
        self.blue_text.setValidator(Max255Validator())
        self.blue_text.textChanged.connect(self.on_text_changed)
        self.blue_text.editingFinished.connect(self.limit_text_values)
        rgb_layout.addWidget(self.blue_text)
        
        layout.addLayout(rgb_layout, 3, 0, 1, 4)

    def set_color(self, index, r, g, b):
        self.original_color = (r, g, b)
        self.selected_color_index = index
        
        red_val = min((r + 4) // 8, 31)
        green_val = min((g + 4) // 8, 31)
        blue_val = min((b + 4) // 8, 31)
        
        r_rounded = min((red_val * 8 + 4) // 8 * 8, 248)
        g_rounded = min((green_val * 8 + 4) // 8 * 8, 248)
        b_rounded = min((blue_val * 8 + 4) // 8 * 8, 248)
        
        try:
            self.red_slider.valueChanged.disconnect()
            self.green_slider.valueChanged.disconnect()
            self.blue_slider.valueChanged.disconnect()
            self.red_text.textChanged.disconnect()
            self.green_text.textChanged.disconnect()
            self.blue_text.textChanged.disconnect()
        except:
            pass
            
        self.red_slider.setValue(red_val)
        self.green_slider.setValue(green_val)
        self.blue_slider.setValue(blue_val)
        
        self.red_value.setText(str(red_val))
        self.green_value.setText(str(green_val))
        self.blue_value.setText(str(blue_val))
        
        self.red_text.setText(str(r_rounded))
        self.green_text.setText(str(g_rounded))
        self.blue_text.setText(str(b_rounded))
        
        self.red_slider.valueChanged.connect(self.on_color_changed)
        self.green_slider.valueChanged.connect(self.on_color_changed)
        self.blue_slider.valueChanged.connect(self.on_color_changed)
        self.red_text.textChanged.connect(self.on_text_changed)
        self.green_text.textChanged.connect(self.on_text_changed)
        self.blue_text.textChanged.connect(self.on_text_changed)
        
        self.selected_color = QColor(r_rounded, g_rounded, b_rounded)
        self.color_preview.setStyleSheet(f"background-color: rgb({r_rounded}, {g_rounded}, {b_rounded}); border: 1px solid #000;")
    
    def get_current_color(self):
        try:
            r = int(self.red_text.text()) if self.red_text.text() else 0
            g = int(self.green_text.text()) if self.green_text.text() else 0
            b = int(self.blue_text.text()) if self.blue_text.text() else 0
            return (r, g, b)
        except ValueError:
            r = self.red_slider.value() * 8
            g = self.green_slider.value() * 8
            b = self.blue_slider.value() * 8
            return (r, g, b)
    
    def has_changes(self):
        if self.selected_color_index < 0:
            return False
        current_color = self.get_current_color()
        return current_color != self.original_color

# ui/dialogs/auto_spinbox.py

from ui.qt_compat import QSpinBox
class AutoSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_auto = True
        self.setRange(0, 256)
        super().setValue(0)
        self.dialog = None

    def set_dialog(self, dialog):
        self.dialog = dialog
        if hasattr(self.dialog, 'start_index'):
            self.dialog.start_index.valueChanged.connect(
                lambda value: self.check_and_update(value)
            )

    def check_and_update(self, start_value):
        if self._is_auto:
            self.update()
            if self.lineEdit():
                self.lineEdit().setText(self.textFromValue(0))
        else:
            current_size = self.value()
            if start_value + current_size > 256:
                self._is_auto = True
                super().setValue(0)
                self.update()
                if self.lineEdit():
                    self.lineEdit().setText(self.textFromValue(0))

    def setValue(self, value):
        if value == 0:
            self._is_auto = True
        else:
            self._is_auto = False
        super().setValue(value)
        self.update()

    def value(self):
        return super().value()

    def textFromValue(self, value):
        if self._is_auto and hasattr(self, 'dialog') and self.dialog:
            try:
                start_val = self.dialog.start_index.value()
                calculated = 256 - start_val
                return str(calculated)
            except:
                return "256"
        return super().textFromValue(value)

    def valueFromText(self, text):
        if text == "0":
            self._is_auto = True
            return 0
        
        if hasattr(self, 'dialog') and self.dialog:
            try:
                start_val = self.dialog.start_index.value()
                auto_value = 256 - start_val
                if text == str(auto_value):
                    self._is_auto = True
                    return 0
            except:
                pass
        
        self._is_auto = False
        try:
            return int(text)
        except:
            return 0

    def stepEnabled(self):
        if self._is_auto:
            return QSpinBox.StepNone
        return super().stepEnabled()

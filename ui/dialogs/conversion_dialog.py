# ui/dialogs/conversion_dialog.py

from PIL import Image as PilImage
from .conversion_dialog_ui import ConversionDialogUI
from .conversion_dialog_logic import ConversionDialogLogic
from .conversion_dialog_config import ConversionDialogConfig
from .auto_spinbox import AutoSpinBox
from ui.qt_compat import QDialog

class ConversionDialog(QDialog, ConversionDialogUI, ConversionDialogLogic, ConversionDialogConfig):
    @property
    def _tr(self):
        if self.parent() and hasattr(self.parent(), 'translator'):
            return self.parent().translator.tr
        return lambda key, **kw: key
    
    PRESETS_TEXT = {
        "preset_original": None,
        "preset_screen_256x160": (32, 20),
        "preset_screen_256x256": (32, 32),
        "preset_screen_512x256": (64, 32),
        "preset_screen_256x512": (32, 64),
        "preset_screen_512x512": (64, 64),
        "preset_custom": None
    }
    PRESETS_ROT = {
        "16×16 (128×128)": (16, 16),
        "32×32 (256×256)": (32, 32),
        "64×64 (512×512)": (64, 64),
        "128×128 (1024×1024)": (128, 128),
    }
    PRESETS = PRESETS_TEXT

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.result = None
        self.img_width_tiles = 32
        self.img_height_tiles = 32
        self.output_width_tiles = 32
        self.output_height_tiles = 20
        self.grid_was_visible = False

        try:
            pil_img = PilImage.open(image_path)
            self.img_width_tiles = (pil_img.width // 8)
            self.img_height_tiles = (pil_img.height // 8)
        except:
            pass

        self.setWindowTitle(self._tr("conv_dialog_title"))
        self.setFixedSize(894, 558) #(844, 558)
        self.setup_ui()
        self.retranslate_presets()
        self.load_conversion_settings()
        
    def retranslate_presets(self):
        self.output_combo.clear()
        for key in self.PRESETS_TEXT.keys():
            translated_name = self._tr(key) 
            self.output_combo.addItem(translated_name, key)

# core/library_loader.py
import importlib
import time
import os
from types import ModuleType
from typing import Dict, List, Tuple
from utils.translator import Translator
from ui.qt_compat import QFileDialog
translator = Translator()

class LibraryLoader:
    def __init__(self):
        self.libraries_to_preload = [
            "PySide2.QtCore",
            "PySide2.QtGui", 
            "PySide2.QtWidgets",
            "PIL.Image",
            "PIL.ImageOps",
            "numpy",
            "cv2",
        ]
    
    def preload_libraries(self, progress_callback=None):
        total = len(self.libraries_to_preload)
        
        for i, module_name in enumerate(self.libraries_to_preload):
            try:
                if progress_callback:
                    progress = int((i / total) * 100)
                    msg = translator.tr("preloading_library").format(module_name=module_name)
                    progress_callback(progress, msg)
                
                module = importlib.import_module(module_name)
                
                if module_name == "numpy":
                    import numpy as np
                    dummy = np.zeros(10, dtype=np.uint8)
                    lut = np.arange(10, dtype=np.uint8)
                    _ = lut[dummy]
                
                elif module_name == "PIL.Image":
                    from PIL import Image
                    dummy_img = Image.new('P', (8, 8))
                    _ = dummy_img.getpalette()

                elif module_name == "PySide2.QtWidgets":

                    _ = QFileDialog

                time.sleep(0.02)
                
            except ImportError as e:
                print(translator.tr("warning_loading_library").format(module_name=module_name, e=e))
                continue
        
        if progress_callback:
            progress_callback(100, translator.tr("preload_complete"))

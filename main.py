# main.py
import os
import sys
import importlib
import time
import threading
from ui.qt_compat import QApplication, QMessageBox, QFileDialog, QIcon, exec_dialog, exec_app

os.environ['JOBLIB_WORKER_COUNT'] = '4'
os.environ['JOBLIB_MULTIPROCESSING'] = '0'
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

if os.name == 'nt':
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

def _install_exception_hook(translator=None):
    import traceback
    _tr = translator.tr if translator else lambda k, **kw: k

    def handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(tb_str)
        try:

            app = QApplication.instance()
            if app is not None:
                msg = QMessageBox()
                msg.setWindowTitle(_tr('error_dialog_title'))
                msg.setIcon(QMessageBox.Critical)
                msg.setText(_tr('error_dialog_text'))
                msg.setDetailedText(tb_str)
                msg.setStandardButtons(QMessageBox.Ok)
                exec_dialog(msg)
        except Exception:
            pass

    sys.excepthook = handle_exception

def warm_up_system_resources():
    try:

        _ = QFileDialog()
    except:
        pass

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    

    app = QApplication(sys.argv)

    if os.name == 'nt':
        app.setStyle("windowsvista")
        app.setProperty("darkMode", False)
    
    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        try:
            app_icon = QIcon(icon_path)
            app.setWindowIcon(app_icon)
        except Exception as e:
            pass
    else:
        pass
    
    language = "english"
    try:
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        language = config_manager.get('SETTINGS', 'language', 'english')
    except Exception as e:
        pass
    
    from utils.translator import Translator
    translator = Translator(lang_dir="lang", default_lang=language)
    _install_exception_hook(translator)
    
    from ui.splash_screen import GBASplashScreen
    splash = GBASplashScreen(translator)
    splash.show()
    
    libraries_to_preload = [
        "PySide2.QtCore",
        "PySide2.QtGui", 
        "PySide2.QtWidgets",
        "PIL.Image",
        "PIL.ImageOps",
        "core.image_utils",
        "core.palette_utils",
        "core.config_manager",
        "ui.dialogs.conversion_dialog"
    ]
    
    total = len(libraries_to_preload)
    _tr = translator.tr
    for i, module_name in enumerate(libraries_to_preload):
        try:
            progress = int((i / total) * 80)
            module_display_name = module_name.split('.')[-1]
            splash.set_progress(progress, _tr('splash_loading') + ' ' + module_display_name + '...')
            
            importlib.import_module(module_name)
            time.sleep(0.03)
            
        except Exception as e:
            continue
    
    splash.set_progress(90, _tr('splash_initializing_interface'))
    time.sleep(0.3)
    
    from ui.main_window.main import GBABackgroundStudio
    window = GBABackgroundStudio()
    
    if os.path.exists(icon_path):
        try:
            window.setWindowIcon(app_icon)
        except Exception as e:
            pass
    
    splash.set_progress(100, _tr('splash_ready'))
    time.sleep(0.2)
    
    window.show()
    splash.finish(window)

    threading.Thread(target=warm_up_system_resources, daemon=True).start()
    
    sys.exit(exec_app(app))

if __name__ == "__main__":
    main()

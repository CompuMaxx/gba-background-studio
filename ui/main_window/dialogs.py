# ui/main_window/dialogs.py
from ui.qt_compat import QMessageBox, Qt, exec_dialog

def show_contribute(main_window):
    contribute_text = main_window.translator.tr("contribute_text")
    
    msg_box = QMessageBox(main_window)
    msg_box.setWindowTitle(main_window.translator.tr("contribute_title"))
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(contribute_text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    exec_dialog(msg_box)

def show_about(main_window):
    from ui.dialogs.about_dialog import AboutDialog
    dlg = AboutDialog(main_window)
    exec_dialog(dlg)

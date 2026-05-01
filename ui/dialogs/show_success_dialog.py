# ui/dialogs/show_success_dialog.py
import os
import sys
import subprocess
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    Qt,
    exec_dialog,
)

def show_success_dialog(parent):
    main_window = parent.parent() if parent else None
    _tr = main_window.translator.tr if (main_window and hasattr(main_window, 'translator')) else lambda k, **kw: k
    
    dialog = QDialog(parent)
    dialog.setWindowTitle(_tr("success_dialog_title"))
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    title = QLabel(_tr("success_dialog_message"))
    title.setStyleSheet("font-weight: bold; font-size: 14px; color: #006600;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    layout.addWidget(QLabel(_tr("success_dialog_files")))

    list_widget = QListWidget()
    output_dir = "output"
    if os.path.exists(output_dir):
        for file in sorted(os.listdir(output_dir)):
            list_widget.addItem(file)
    else:
        list_widget.addItem(_tr("success_dialog_no_output"))
    layout.addWidget(list_widget)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()

    open_btn = QPushButton(_tr("success_dialog_open_folder"))

    def open_folder():
        path = os.path.abspath(output_dir)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    open_btn.clicked.connect(open_folder)
    btn_layout.addWidget(open_btn)

    close_btn = QPushButton(_tr("success_dialog_close"))
    close_btn.setDefault(True)
    close_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(close_btn)

    layout.addLayout(btn_layout)

    dialog.setLayout(layout)
    exec_dialog(dialog)

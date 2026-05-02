# ui/dialogs/about_dialog.py
import sys
import ssl
import tempfile
import webbrowser
import urllib.request
import urllib.error
import json
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    Qt,
    QThread,
    Signal
)

def _make_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass

    if sys.platform == "win32":
        try:
            ctx = ssl.create_default_context()
            import ctypes
            import ctypes.wintypes
            ctx.load_default_certs(ssl.Purpose.SERVER_AUTH)
            return ctx
        except Exception:
            pass

        try:
            import tempfile, os, subprocess
            tmp = tempfile.NamedTemporaryFile(suffix='.pem', delete=False)
            tmp.close()
            result = subprocess.run(
                ['certutil', '-exportPFX', '-p', '', 'Root', tmp.name],
                capture_output=True, timeout=5
            )
            if os.path.exists(tmp.name) and os.path.getsize(tmp.name) > 0:
                ctx = ssl.create_default_context(cafile=tmp.name)
                os.unlink(tmp.name)
                return ctx
            os.unlink(tmp.name)
        except Exception:
            pass

    try:
        ctx = ssl.create_default_context()
        ctx.load_default_certs()
        return ctx
    except Exception:
        pass

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

GITHUB_API_URL = "https://api.github.com/repos/CompuMaxx/gba-background-studio/releases/latest"
RELEASES_URL   = "https://github.com/CompuMaxx/gba-background-studio/releases"
REGISTRY_KEY   = r"Software\CompuMax\GBABackgroundStudio"
REGISTRY_VALUE = "InstallPath"

class UpdateChecker(QThread):
    result_ready = Signal(dict)
    error        = Signal(str)

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self._tr = translator.tr if translator else lambda k, **kw: k

    def run(self):
        try:
            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={"User-Agent": "GBABackgroundStudio-UpdateChecker"}
            )
            ctx = _make_ssl_context()
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode())
            self.result_ready.emit({
                "tag":  data.get("tag_name", ""),
                "body": data.get("body", ""),
                "assets": data.get("assets", [])
            })
        except urllib.error.URLError as e:
            reason = str(e.reason)
            if "CERTIFICATE_VERIFY_FAILED" in reason or "SSL" in reason.upper():
                self.error.emit(
                    self._tr("update_ssl_error", error=reason)
                )
            else:
                self.error.emit(reason)
        except Exception as e:
            self.error.emit(str(e))

class UpdateDownloader(QThread):
    finished = Signal(str)
    error    = Signal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url

    def run(self):
        try:
            dest = tempfile.gettempdir() + "\\GBABackgroundStudio_Updater.exe"
            ctx = _make_ssl_context()
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ctx)
            )
            with opener.open(self._url, timeout=60) as resp:
                with open(dest, 'wb') as f:
                    f.write(resp.read())
            self.finished.emit(dest)
        except Exception as e:
            self.error.emit(str(e))

class AboutDialog(QDialog):

    def __init__(self, main_window):
        super().__init__(main_window)
        self._mw = main_window
        self._tr = main_window.translator.tr
        self._version = main_window.config_manager.APP_VERSION
        self._checker = None
        self._downloader = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._tr("about_title"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(420, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._text_label = QLabel(self._tr("about_text", version=self._version))
        self._text_label.setTextFormat(Qt.RichText)
        self._text_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._text_label.setWordWrap(True)
        self._text_label.setOpenExternalLinks(True)
        layout.addWidget(self._text_label)

        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._check_btn = QPushButton(self._tr("check_for_updates"))
        self._check_btn.clicked.connect(self._on_check_updates)
        btn_layout.addWidget(self._check_btn)

        close_btn = QPushButton(self._tr("close"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _on_check_updates(self):
        self._check_btn.setEnabled(False)
        self._set_status(self._tr("checking_updates"), "gray")
        self._checker = UpdateChecker(self, translator=self._mw.translator)
        self._checker.result_ready.connect(self._on_check_result)
        self._checker.error.connect(self._on_check_error)
        self._checker.start()

    def _on_check_error(self, msg: str):
        self._check_btn.setEnabled(True)
        self._set_status(self._tr("update_check_failed"), "red")
        QMessageBox.warning(self, self._tr("update_error_title"),
                            self._tr("update_error_msg", error=msg))

    def _on_check_result(self, data: dict):
        self._check_btn.setEnabled(True)
        self._set_status("", "")

        remote_tag = data.get("tag", "").lstrip("v")
        local_tag  = self._version.lstrip("v")

        def parse(v):
            try:
                return tuple(int(x) for x in v.split("."))
            except ValueError:
                return (0,)

        if not remote_tag or parse(remote_tag) <= parse(local_tag):
            self._set_status(self._tr("already_up_to_date"), "green")
            return

        notes = data.get("body", "")[:500]
        reply = QMessageBox.question(
            self,
            self._tr("update_available_title"),
            self._tr("update_available_msg",
                     remote=remote_tag, local=local_tag, notes=notes),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self._start_update(data)

    def _start_update(self, data: dict):
        install_path = self._get_install_path()

        if install_path:
            import sys
            is_legacy = sys.version_info < (3, 9)
            asset_name = "Updater_Legacy.exe" if is_legacy else "Updater.exe"

            updater_url = self._find_asset_url(data.get("assets", []), asset_name)
            if not updater_url:
                webbrowser.open(RELEASES_URL)
                return
            self._check_btn.setEnabled(False)
            self._set_status(self._tr("downloading_update"), "gray")
            self._downloader = UpdateDownloader(updater_url, self)
            self._downloader.finished.connect(
                lambda path: self._on_updater_downloaded(path, install_path))
            self._downloader.error.connect(self._on_download_error)
            self._downloader.start()
        else:
            webbrowser.open(RELEASES_URL)

    def _on_updater_downloaded(self, exe_path: str, install_path: str):
        import subprocess
        try:
            subprocess.Popen(
                [
                    exe_path,
                    f"/DIR={install_path}",
                ],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
            )
        except Exception as e:
            QMessageBox.critical(self, self._tr("update_error_title"), str(e))
            return
        sys.exit()

    def _on_download_error(self, msg: str):
        self._check_btn.setEnabled(True)
        self._set_status(self._tr("update_check_failed"), "red")
        QMessageBox.warning(self, self._tr("update_error_title"),
                            self._tr("update_error_msg", error=msg))

    def _get_install_path(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
                value, _ = winreg.QueryValueEx(key, REGISTRY_VALUE)
                return value if value else None
        except Exception:
            return None

    def _find_asset_url(self, assets: list, name: str):
        for asset in assets:
            if asset.get("name", "").lower() == name.lower():
                return asset.get("browser_download_url")
        return None

    def _set_status(self, text: str, color: str):
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {color};" if color else "")
        self._status_label.setVisible(bool(text))

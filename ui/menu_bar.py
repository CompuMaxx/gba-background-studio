# ui/menu_bar.py

import os
import shutil
from ui.qt_compat import (
    QMenu,
    QMessageBox,
    QFileDialog,
    QAction,
    QKeySequence,
    Qt
)

class MenuBar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()
        self.create_menus()

    def create_menus(self):
        # File menu
        file_menu = self.menu_bar.addMenu(self.main_window.translator.tr("file_menu"))
        
        self.action_open_image = file_menu.addAction(self.main_window.translator.tr("open_image"))
        self.action_open_image.setShortcut("Ctrl+O")
        self.action_open_image.triggered.connect(self.main_window.open_image_for_conversion)
        
        file_menu.addSeparator()
        
        self.action_export_files = file_menu.addAction(self.main_window.translator.tr("export_files"))
        self.action_export_files.setShortcut("Ctrl+E")
        self.action_export_files.triggered.connect(self.export_files)
        
        file_menu.addSeparator()
        
        self.action_exit = file_menu.addAction(self.main_window.translator.tr("exit_app"))
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.triggered.connect(self.main_window.close)

        # Tileset menu
        tileset_menu = self.menu_bar.addMenu(self.main_window.translator.tr("tileset_menu"))
        
        self.action_open_tileset = tileset_menu.addAction(self.main_window.translator.tr("open_tileset"))
        self.action_open_tileset.setShortcut("Ctrl+T")
        self.action_open_tileset.triggered.connect(self.main_window.open_tileset)
        
        self.action_save_tileset = tileset_menu.addAction(self.main_window.translator.tr("save_tileset"))
        self.action_save_tileset.setShortcut("Ctrl+S")
        self.action_save_tileset.triggered.connect(self.main_window.save_tileset)
        self.action_save_tileset.setEnabled(False)

        tileset_menu.addSeparator()

        self.action_optimize_tiles = tileset_menu.addAction(self.main_window.translator.tr("optimize_tiles"))
        self.action_optimize_tiles.setShortcut("Ctrl+Alt+O")
        self.action_optimize_tiles.triggered.connect(self.main_window.optimize_tiles)
        self.action_optimize_tiles.setEnabled(False)

        self.action_deoptimize_tiles = tileset_menu.addAction(self.main_window.translator.tr("deoptimize_tiles"))
        self.action_deoptimize_tiles.setShortcut("Ctrl+Alt+D")
        self.action_deoptimize_tiles.triggered.connect(self.main_window.deoptimize_tiles)
        self.action_deoptimize_tiles.setEnabled(False)

        tileset_menu.addSeparator()

        self.action_convert_to_4bpp = tileset_menu.addAction(self.main_window.translator.tr("convert_to_4bpp"))
        self.action_convert_to_4bpp.setShortcut("Ctrl+4")
        self.action_convert_to_4bpp.triggered.connect(self.main_window.convert_to_4bpp)
        self.action_convert_to_4bpp.setEnabled(False)

        self.action_convert_to_8bpp = tileset_menu.addAction(self.main_window.translator.tr("convert_to_8bpp"))
        self.action_convert_to_8bpp.setShortcut("Ctrl+8")
        self.action_convert_to_8bpp.triggered.connect(self.main_window.convert_to_8bpp)
        self.action_convert_to_8bpp.setEnabled(False)
        
        # Tilemap menu
        tilemap_menu = self.menu_bar.addMenu(self.main_window.translator.tr("tilemap_menu"))
        
        self.action_open_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("open_tilemap"))
        self.action_open_tilemap.setShortcut("Ctrl+Shift+O")
        self.action_open_tilemap.triggered.connect(self.main_window.open_tilemap)
        self.action_open_tilemap.setEnabled(False)
        
        self.action_new_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("new_tilemap"))
        self.action_new_tilemap.setShortcut("Ctrl+Shift+N")
        self.action_new_tilemap.triggered.connect(self.main_window.new_tilemap)
        self.action_new_tilemap.setEnabled(False)
        
        self.action_save_tilemap = tilemap_menu.addAction(self.main_window.translator.tr("save_tilemap"))
        self.action_save_tilemap.setShortcut("Ctrl+Shift+S")
        self.action_save_tilemap.triggered.connect(self.main_window.save_tilemap)
        self.action_save_tilemap.setEnabled(False)
        
        self.action_save_selection = tilemap_menu.addAction(self.main_window.translator.tr("save_selection"))
        self.action_save_selection.setShortcut("Ctrl+Shift+B")
        self.action_save_selection.triggered.connect(self.main_window.save_selection)
        self.action_save_selection.setEnabled(False)

        tilemap_menu.addSeparator()

        self.action_convert_to_text_mode = tilemap_menu.addAction(self.main_window.translator.tr("convert_to_text_mode"))
        self.action_convert_to_text_mode.setShortcut("Ctrl+Shift+0")
        self.action_convert_to_text_mode.triggered.connect(self.main_window.convert_to_text_mode)
        self.action_convert_to_text_mode.setEnabled(False)

        self.action_convert_to_rot_mode = tilemap_menu.addAction(self.main_window.translator.tr("convert_to_rot_mode"))
        self.action_convert_to_rot_mode.setShortcut("Ctrl+Shift+1")
        self.action_convert_to_rot_mode.triggered.connect(self.main_window.convert_to_rot_mode)
        self.action_convert_to_rot_mode.setEnabled(False)

        # Palette menu
        palette_menu = self.menu_bar.addMenu(self.main_window.translator.tr("palette_menu"))
        
        self.action_open_palette = palette_menu.addAction(self.main_window.translator.tr("open_palette"))
        self.action_open_palette.setShortcut("Ctrl+P")
        self.action_open_palette.triggered.connect(self.main_window.open_palette)
        
        self.action_save_palette = palette_menu.addAction(self.main_window.translator.tr("save_palette"))
        self.action_save_palette.setShortcut("Ctrl+Shift+P")
        self.action_save_palette.triggered.connect(self.main_window.save_palette)
        self.action_save_palette.setEnabled(False)

        # Edit menu
        edit_menu = self.menu_bar.addMenu(self.main_window.translator.tr("edit_menu"))
        
        self.action_undo = edit_menu.addAction(self.main_window.translator.tr("undo"))
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.main_window.undo)
        self.action_undo.setEnabled(False)

        self.action_redo = edit_menu.addAction(self.main_window.translator.tr("redo"))
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.main_window.redo)
        self.action_redo.setEnabled(False)

        # View menu
        view_menu = self.menu_bar.addMenu(self.main_window.translator.tr("view_menu"))
        
        # Tab navigation
        self.action_preview_tab = view_menu.addAction(self.main_window.translator.tr("preview_tab_menu"))
        self.action_preview_tab.triggered.connect(lambda checked=False: self.main_window.main_tabs.setCurrentIndex(0))
        self.action_edit_tiles_tab = view_menu.addAction(self.main_window.translator.tr("edit_tiles_tab_menu"))
        self.action_edit_tiles_tab.triggered.connect(lambda checked=False: self.main_window.main_tabs.setCurrentIndex(1))
        self.action_edit_palettes_tab = view_menu.addAction(self.main_window.translator.tr("edit_palettes_tab_menu"))
        self.action_edit_palettes_tab.triggered.connect(lambda checked=False: self.main_window.main_tabs.setCurrentIndex(2))
        
        view_menu.addSeparator()
        
        self.action_reset_zoom = view_menu.addAction(self.main_window.translator.tr("reset_zoom"))
        self.action_reset_zoom.setShortcut("Ctrl+0")
        self.action_reset_zoom.triggered.connect(self.main_window.reset_zoom)
        
        self.action_zoom_in = view_menu.addAction(self.main_window.translator.tr("zoom_in"))
        self.action_zoom_in.setShortcut("Ctrl++")
        self.action_zoom_in.triggered.connect(self.main_window.zoom_in)
        
        self.action_zoom_out = view_menu.addAction(self.main_window.translator.tr("zoom_out"))
        self.action_zoom_out.setShortcut("Ctrl+-")
        self.action_zoom_out.triggered.connect(self.main_window.zoom_out)
        
        view_menu.addSeparator()
        
        # Grid toggle action
        self.action_grid = view_menu.addAction(self.main_window.translator.tr("grid_toggle"))
        self.action_grid.setShortcut("Ctrl+G")
        self.action_grid.setCheckable(True)

        grid_visible = self.main_window.config_manager.getboolean('SETTINGS', 'show_grid', False)
        self.action_grid.setChecked(grid_visible)
        self.action_grid.triggered.connect(self.main_window.toggle_grid)

        view_menu.addSeparator()
        
        self.action_status_bar = view_menu.addAction(self.main_window.translator.tr("status_bar_toggle"))
        self.action_status_bar.setCheckable(True)
        self.action_status_bar.setChecked(True)
        self.action_status_bar.triggered.connect(self.main_window.toggle_status_bar)

        # Settings menu
        settings_menu = self.menu_bar.addMenu(self.main_window.translator.tr("settings_menu"))
        
        # Language submenu
        self.language_menu = QMenu(self.main_window.translator.tr("language_menu"), self.main_window)
        language_menu = self.language_menu
        self.language_actions = {}
        languages = {
                "english": "English",
                "spanish": "Español",
                "br_portuguese": "Português (BR)",
                "french": "Français",
                "german": "Deutsch",
                "italian": "Italiano",
                "portuguese": "Português",
                "dutch": "Nederlands",
                "polish": "Polski",
                "turkish": "Türkçe",
                "vietnamese": "Tiếng Việt",
                "indonesian": "Bahasa Indonesia",
                "hindi": "हिन्दी",
                "russian": "Русский",
                "japanese": "日本語",
                "chinese_simplified": "简体中文",
                "chinese_traditional": "繁體中文",
                "korean": "한국어",
            }
        
        for lang_code, lang_name in languages.items():
            action = language_menu.addAction(lang_name)
            action.setCheckable(True)
            action.triggered.connect(lambda checked=False, lc=lang_code: self.main_window.change_language(lc))
            self.language_actions[lang_code] = action
        
        settings_menu.addMenu(language_menu)

        settings_menu.addSeparator()

        self.action_display_settings = settings_menu.addAction(
            self.main_window.translator.tr("display_settings")
        )
        self.action_display_settings.triggered.connect(self.main_window.open_display_settings)

        settings_menu.addSeparator()
        
        # Option's Settings
        self.action_save_preview = settings_menu.addAction(self.main_window.translator.tr("save_preview"))
        self.action_save_preview.setCheckable(True)
        self.action_save_preview.triggered.connect(self.main_window.toggle_save_preview)
        
        self.action_keep_transparent = settings_menu.addAction(self.main_window.translator.tr("keep_transparent"))
        self.action_keep_transparent.setCheckable(True)
        self.action_keep_transparent.triggered.connect(self.main_window.toggle_keep_transparent)
        
        self.action_keep_temp = settings_menu.addAction(self.main_window.translator.tr("keep_temp"))
        self.action_keep_temp.setCheckable(True)
        self.action_keep_temp.triggered.connect(self.main_window.toggle_keep_temp)

        self.action_load_last_output = settings_menu.addAction(self.main_window.translator.tr("load_last_output"))
        self.action_load_last_output.setCheckable(True)
        self.action_load_last_output.setChecked(self.main_window.load_last_output)
        self.action_load_last_output.triggered.connect(self.main_window.toggle_load_last_output)

        self.action_save_conversion_params = settings_menu.addAction(self.main_window.translator.tr("save_conversion_params"))
        self.action_save_conversion_params.setCheckable(True)
        self.action_save_conversion_params.setChecked(self.main_window.save_conversion_params)
        self.action_save_conversion_params.triggered.connect(self.main_window.toggle_save_conversion_params)

        self.action_show_success_dialog = settings_menu.addAction(self.main_window.translator.tr("show_success_dialog"))
        self.action_show_success_dialog.setCheckable(True)
        self.action_show_success_dialog.triggered.connect(self.main_window.toggle_show_success_dialog)

        self.action_remember_file_paths = settings_menu.addAction(self.main_window.translator.tr("remember_file_paths"))
        self.action_remember_file_paths.setCheckable(True)
        self.action_remember_file_paths.setChecked(self.main_window.config_manager.getboolean('SETTINGS', 'remember_file_paths', True))
        self.action_remember_file_paths.triggered.connect(self.main_window.toggle_remember_file_paths)

        # Help menu
        help_menu = self.menu_bar.addMenu(self.main_window.translator.tr("help_menu"))
        
        self.action_about = help_menu.addAction(self.main_window.translator.tr("about"))
        self.action_about.triggered.connect(self.main_window.show_about)
        
        self.action_contribute = help_menu.addAction(self.main_window.translator.tr("contribute"))
        self.action_contribute.triggered.connect(self.main_window.show_contribute)

    def retranslate_menus(self):
        tr = self.main_window.translator.tr
        menus = self.menu_bar.actions()
        labels = ["file_menu", "tileset_menu", "tilemap_menu", "palette_menu",
                  "edit_menu", "view_menu", "settings_menu", "help_menu"]
        for action, key in zip(menus, labels):
            action.setText(tr(key))

        # File
        self.action_open_image.setText(tr("open_image"))
        self.action_export_files.setText(tr("export_files"))
        self.action_exit.setText(tr("exit_app"))
        # Tileset
        self.action_open_tileset.setText(tr("open_tileset"))
        self.action_save_tileset.setText(tr("save_tileset"))
        self.action_optimize_tiles.setText(tr("optimize_tiles"))
        self.action_deoptimize_tiles.setText(tr("deoptimize_tiles"))
        self.action_convert_to_4bpp.setText(tr("convert_to_4bpp"))
        self.action_convert_to_8bpp.setText(tr("convert_to_8bpp"))
        # Tilemap
        self.action_open_tilemap.setText(tr("open_tilemap"))
        self.action_new_tilemap.setText(tr("new_tilemap"))
        self.action_save_tilemap.setText(tr("save_tilemap"))
        self.action_save_selection.setText(tr("save_selection"))
        self.action_convert_to_text_mode.setText(tr("convert_to_text_mode"))
        self.action_convert_to_rot_mode.setText(tr("convert_to_rot_mode"))
        # Palette
        self.action_open_palette.setText(tr("open_palette"))
        self.action_save_palette.setText(tr("save_palette"))
        # Edit
        self.action_undo.setText(tr("undo"))
        self.action_redo.setText(tr("redo"))
        # View
        self.action_preview_tab.setText(tr("preview_tab_menu"))
        self.action_edit_tiles_tab.setText(tr("edit_tiles_tab_menu"))
        self.action_edit_palettes_tab.setText(tr("edit_palettes_tab_menu"))
        self.action_reset_zoom.setText(tr("reset_zoom"))
        self.action_zoom_in.setText(tr("zoom_in"))
        self.action_zoom_out.setText(tr("zoom_out"))
        self.action_grid.setText(tr("grid_toggle"))
        self.action_display_settings.setText(tr("display_settings"))
        self.action_status_bar.setText(tr("status_bar_toggle"))
        # Settings submenus
        self.language_menu.setTitle(tr("language_menu"))
        self.action_save_preview.setText(tr("save_preview"))
        self.action_keep_transparent.setText(tr("keep_transparent"))
        self.action_keep_temp.setText(tr("keep_temp"))
        self.action_load_last_output.setText(tr("load_last_output"))
        self.action_save_conversion_params.setText(tr("save_conversion_params"))
        self.action_show_success_dialog.setText(tr("show_success_dialog"))
        self.action_remember_file_paths.setText(tr("remember_file_paths"))
        # Help
        self.action_about.setText(tr("about"))
        self.action_contribute.setText(tr("contribute"))

    def export_files(self, checked=False):
        output_dir = "output"
        if not os.path.exists(output_dir) or not os.listdir(output_dir):
            QMessageBox.information(self.main_window, self.main_window.translator.tr("export_files"), 
                                  self.main_window.translator.tr("no_files_to_export"))
            return
        
        target_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            self.main_window.translator.tr("select_export_directory"),
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not target_dir:
            return

        files_to_copy = [
            f for f in os.listdir(output_dir)
            if os.path.isfile(os.path.join(output_dir, f))
        ]
        existing = [f for f in files_to_copy if os.path.exists(os.path.join(target_dir, f))]
        if existing:
            reply = QMessageBox.question(
                self.main_window,
                self.main_window.translator.tr("export_files"),
                self.main_window.translator.tr("export_overwrite_confirm", files="\n".join(existing)),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        try:
            for file_name in files_to_copy:
                source_path = os.path.join(output_dir, file_name)
                target_path = os.path.join(target_dir, file_name)
                shutil.copy2(source_path, target_path)
            
            QMessageBox.information(self.main_window, self.main_window.translator.tr("export_complete"), 
                                  self.main_window.translator.tr("export_success").format(path=target_dir))
            
        except Exception as e:
            error_msg = self.main_window.translator.tr("export_error").format(error=str(e))
            QMessageBox.warning(self.main_window, self.main_window.translator.tr("export_error_title"), error_msg)

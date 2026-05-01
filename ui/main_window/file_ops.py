# ui/main_window/file_ops.py
import os
import shutil
from pathlib import Path
from PIL import Image as PilImage

from core.image_utils import create_gbagfx_preview
from ui.shared_utils import pil_to_qimage, CustomGraphicsView, update_status_bar_shared
from core.palette_utils import generate_grayscale_palette
from core.config import ROT_SIZES_SET as _ROT_SIZES
from ui.qt_compat import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QPixmap,
    QBrush,
    QColor,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    exec_dialog,
)

def get_documents_folder():
    try:
        if os.name == 'nt':  # Windows
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                documents_path = winreg.QueryValueEx(key, "Personal")[0]
                return documents_path
        else:  # macOS and Linux
            home = Path.home()
            documents = home / "Documents"
            if documents.exists():
                return str(documents)
            return str(home)
    except Exception:
        return str(Path.home())

def _get_save_directory(main_window):
    if hasattr(main_window, '_last_save_directory') and main_window._last_save_directory:
        return main_window._last_save_directory
    
    remember_paths = main_window.config_manager.getboolean('SETTINGS', 'remember_file_paths', False)
    if remember_paths:
        saved = main_window.config_manager.get('PATHS', 'last_save_directory', '')
        if saved and os.path.isdir(saved):
            return saved
    
    return get_documents_folder()

def _update_save_directory(main_window, file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    main_window._last_save_directory = directory
    main_window.config_manager.set('PATHS', 'last_save_directory', directory)

def _get_image_directory(main_window):
    if hasattr(main_window, '_last_image_directory') and main_window._last_image_directory:
        return main_window._last_image_directory
    
    remember_paths = main_window.config_manager.getboolean('SETTINGS', 'remember_file_paths', False)
    if remember_paths:
        saved = main_window.config_manager.get('PATHS', 'last_image_directory', '')
        if saved and os.path.isdir(saved):
            return saved
    
    return get_documents_folder()

def _update_image_directory(main_window, file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    main_window._last_image_directory = directory
    main_window.config_manager.set('PATHS', 'last_image_directory', directory)

class PaletteApplyDialog(QDialog):
    ADD     = "add"
    SYNC    = "sync"
    REPLACE = "replace"

    def __init__(self, parent=None, need_bpp=False):
        super().__init__(parent)
        tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else (lambda k, **kw: k)
        self.setWindowTitle(tr("palette_apply_title"))
        self.setModal(True)
        self.setFixedSize(400, 200 if need_bpp else 160)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("palette_apply_question")))

        self._add_radio     = QRadioButton(tr("palette_apply_add"))
        self._sync_radio    = QRadioButton(tr("palette_apply_sync"))
        self._replace_radio = QRadioButton(tr("palette_apply_replace"))
        self._add_radio.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self._add_radio)
        grp.addButton(self._sync_radio)
        grp.addButton(self._replace_radio)
        layout.addWidget(self._add_radio)
        layout.addWidget(self._sync_radio)
        layout.addWidget(self._replace_radio)

        self._bpp_combo = None
        if need_bpp:
            current_bpp = getattr(parent, 'current_bpp', 4) if parent else 4
            bpp_row = QHBoxLayout()
            bpp_row.addWidget(QLabel(tr("palette_apply_color_depth")))
            self._bpp_combo = QComboBox()
            self._bpp_combo.addItems(["4bpp", "8bpp"])
            if current_bpp == 8:
                self._bpp_combo.setCurrentIndex(1)
                self._bpp_combo.setEnabled(False)
            bpp_row.addWidget(self._bpp_combo)
            layout.addLayout(bpp_row)

        btn_row = QHBoxLayout()
        ok_btn     = QPushButton(tr("ok"))
        cancel_btn = QPushButton(tr("cancel"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def get_values(self):
        mode = self.ADD if self._add_radio.isChecked() else (self.SYNC if self._sync_radio.isChecked() else self.REPLACE)
        bpp  = 8 if (self._bpp_combo and self._bpp_combo.currentIndex() == 1) else 4
        return mode, bpp

class PaletteLoadDialog(QDialog):
    def __init__(self, parent=None, palette_length=256):
        super().__init__(parent)
        tr = parent.translator.tr if (parent and hasattr(parent, 'translator')) else (lambda k, **kw: k)
        self.setWindowTitle(tr("palette_load_title"))
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        index_layout = QHBoxLayout()
        index_layout.addWidget(QLabel(tr("palette_load_start_index")))
        self.index_spin = QSpinBox()
        self.index_spin.setRange(0, 255)
        self.index_spin.setValue(0)
        index_layout.addWidget(self.index_spin)
        layout.addLayout(index_layout)
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel(tr("palette_load_length", max=palette_length)))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(1, palette_length)
        self.length_spin.setValue(palette_length)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton(tr("ok"))
        cancel_btn = QPushButton(tr("cancel"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.index_spin.valueChanged.connect(self._update_length_max)
        self.palette_length = palette_length
    
    def _update_length_max(self):
        max_length = min(self.palette_length, 256 - self.index_spin.value())
        self.length_spin.setMaximum(max_length)
        if self.length_spin.value() > max_length:
            self.length_spin.setValue(max_length)
    
    def get_values(self):
        return self.index_spin.value(), self.length_spin.value()
        
def load_last_output_files(main_window):
    tiles_path = "output/tiles.png"
    preview_path = "temp/preview/preview.png"
    palette_path = "temp/preview/palette.pal"
    tilemap_path = "output/map.bin"
    
    if not (os.path.exists(tiles_path) and os.path.exists(tilemap_path)):
        return False
    
    try:
        with PilImage.open(tiles_path) as f:
            tiles_img = f.copy()
        main_window.display_tileset(tiles_img)
        main_window.menu_bar.action_save_tileset.setEnabled(True)
        main_window.menu_bar.action_open_tilemap.setEnabled(True)
        main_window.menu_bar.action_new_tilemap.setEnabled(True)
        main_window.tileset_from_conversion = True
        selected = main_window.config_manager.get('CONVERSION', 'selected_palettes', '0')
        main_window.conversion_palette_count = len([p for p in selected.split(',') if p.strip()]) if main_window.current_bpp == 4 else 16
        is_8bpp = main_window.current_bpp == 8
        palette_count = len([p for p in selected.split(',') if p.strip()])
        main_window.current_rotation_mode = main_window.config_manager.getboolean('CONVERSION', 'rotation_mode', False)
        
        with open(tilemap_path, 'rb') as f:
            tilemap_data = f.read()
        main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path if os.path.exists(preview_path) else None)
        main_window.menu_bar.action_save_tilemap.setEnabled(True)

        _update_convert_actions(main_window)

        if hasattr(main_window, 'history_manager'):
            main_window.history_manager.clear()

        if os.path.exists(preview_path):
            with PilImage.open(preview_path) as f:
                preview_img = f.copy()
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            main_window.preview_tab.preview_image_scene.clear()
            main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())

            main_window.edit_tiles_tab.edit_tilemap_scene.clear()
            main_window.edit_tiles_tab.edit_tilemap_scene.addPixmap(preview_pixmap)
            main_window.edit_tiles_tab.edit_tilemap_scene.setSceneRect(preview_pixmap.rect())
            
            from .view_ops import apply_zoom_to_view
            apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)
            if main_window.preview_tab.preview_image_scene.items():
                main_window.preview_tab.preview_image_view.centerOn(main_window.preview_tab.preview_image_scene.items()[0])
        
        if os.path.exists(palette_path):
            palette_colors = [(0, 0, 0)] * 256
            try:
                with open(palette_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f 
                            if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
                if lines:
                    color_count = int(lines[0])
                    for i in range(1, min(1 + color_count, 257)):
                        r, g, b = map(int, lines[i].split())
                        palette_colors[i - 1] = (r, g, b)
                main_window.preview_tab.display_palette_colors(palette_colors)
                if hasattr(main_window, 'edit_palettes_tab'):
                    main_window.edit_palettes_tab.display_palette_colors(palette_colors)
            except Exception as e:
                print(f"Error loading palette: {e}")
                grayscale_colors = generate_grayscale_palette()
                main_window.preview_tab.display_palette_colors(grayscale_colors)
                if hasattr(main_window, 'edit_palettes_tab'):
                    main_window.edit_palettes_tab.display_palette_colors(grayscale_colors)

        main_window.menu_bar.action_save_palette.setEnabled(True)
        main_window.sync_palettes_tab()

        ep = main_window.edit_palettes_tab
        et = main_window.edit_tiles_tab
        if getattr(et, 'tilemap_data', None):
            ep.toggle_tilemap_controls_enabled(True)
            ep.tilemap_width_spin.setValue(et.tilemap_width)
            ep.tilemap_height_spin.setValue(et.tilemap_height)

        if hasattr(main_window, 'output_loaded_for_zoom'):
            main_window.output_loaded_for_zoom = True

        if hasattr(main_window, 'context_toolbar'):
            main_window.context_toolbar.show_for_tab(main_window.main_tabs.currentIndex())

        return True
        
    except Exception as e:
        print(f"Error loading last output: {e}")
        return False

def _apply_palette_colors(main_window, colors):
    if not hasattr(main_window, 'edit_palettes_tab'):
        QMessageBox.warning(main_window, main_window.translator.tr("error"),
                            main_window.translator.tr("palette_load_editor_error"))
        return

    palette_tab = main_window.edit_palettes_tab
    has_tilemap = bool(getattr(palette_tab, 'tilemap_data', None))
    need_bpp    = not has_tilemap

    apply_dlg = PaletteApplyDialog(main_window, need_bpp=need_bpp)
    if exec_dialog(apply_dlg) != QDialog.Accepted:
        return
    mode, dlg_bpp = apply_dlg.get_values()

    bpp = getattr(main_window, 'current_bpp', 4) if has_tilemap else dlg_bpp

    load_dlg = PaletteLoadDialog(main_window, len(colors))
    if exec_dialog(load_dlg) != QDialog.Accepted:
        return
    index, length = load_dlg.get_values()

    if length > len(colors):
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("apply_palette_invalid_length_title"),
            main_window.translator.tr("apply_palette_invalid_length", count=len(colors), length=length)
        )
        return

    if mode == PaletteApplyDialog.ADD:
        new_palette = list(palette_tab.palette_colors)
        for i in range(length):
            if index + i < 256:
                new_palette[index + i] = colors[i]
    else:
        new_palette = [(0, 0, 0)] * 256
        for i in range(length):
            if index + i < 256:
                new_palette[index + i] = colors[i]

    tiles_path = "output/tiles.png"
    if os.path.exists(tiles_path):
        try:
            with PilImage.open(tiles_path) as _t:
                can_update = _t.mode == 'P'
        except Exception:
            can_update = False
    else:
        can_update = False

    if can_update:
        if mode == PaletteApplyDialog.SYNC:
            _sync_tileset_to_palette(tiles_path, palette_tab.palette_colors, new_palette, bpp)
        elif mode in (PaletteApplyDialog.REPLACE, PaletteApplyDialog.ADD):
            _replace_tileset_palette(tiles_path, new_palette)

    for i in range(256):
        palette_tab.palette_colors[i] = new_palette[i]
        if i < len(palette_tab.palette_rects):
            r, g, b = new_palette[i]
            palette_tab.palette_rects[i].setBrush(QBrush(QColor(r, g, b)))

    palette_tab._save_and_update_all()
    palette_tab.color_editor.toggle_controls_enabled(True)
    idx = palette_tab.current_editing_index
    if 0 <= idx < len(palette_tab.palette_colors):
        r, g, b = palette_tab.palette_colors[idx]
        palette_tab.color_editor.set_color(idx, r, g, b)
    main_window.menu_bar.action_save_palette.setEnabled(True)

    if hasattr(main_window, 'context_toolbar'):
        main_window.context_toolbar.on_palette_loaded()

    QMessageBox.information(
        main_window,
        main_window.translator.tr("apply_palette_loaded_title"),
        main_window.translator.tr("apply_palette_loaded", length=length, index=index)
    )

def _sync_tileset_to_palette(tiles_path, old_palette, new_palette, bpp):
    import numpy as np
    try:
        with PilImage.open(tiles_path) as f:
            arr = np.array(f).copy()

        old_rgb = np.array(
            [old_palette[i] if i < len(old_palette) else (0, 0, 0) for i in range(256)],
            dtype=np.int32
        )
        new_rgb = np.array(
            [new_palette[i] if i < len(new_palette) else (0, 0, 0) for i in range(256)],
            dtype=np.int32
        )

        slot_size = 16 if bpp == 4 else 256
        remap = np.arange(256, dtype=np.uint8)

        for old_idx in range(256):
            oc = old_rgb[old_idx]
            slot_start = (old_idx // slot_size) * slot_size
            slot_end   = slot_start + slot_size
            candidates = np.arange(slot_start, slot_end)
            dists = np.sum((new_rgb[candidates] - oc) ** 2, axis=1)
            min_dist = dists.min()
            ties = candidates[dists == min_dist]
            remap[old_idx] = old_idx if old_idx in ties else ties[0]

        lut = remap
        remapped = lut[arr]

        out_img = PilImage.fromarray(remapped, mode='P')
        flat = [c for rgb in new_palette for c in (int(rgb[0]), int(rgb[1]), int(rgb[2]))]
        while len(flat) < 768:
            flat.append(0)
        out_img.putpalette(flat)
        out_img.save(tiles_path)
    except Exception as e:
        print(f"Error syncing tileset: {e}")

def _replace_tileset_palette(tiles_path, new_palette):
    try:
        with PilImage.open(tiles_path) as f:
            import numpy as np
            arr = np.array(f).copy()
            size = f.size
        out_img = PilImage.fromarray(arr, mode='P')
        flat = [c for rgb in new_palette for c in (int(rgb[0]), int(rgb[1]), int(rgb[2]))]
        while len(flat) < 768:
            flat.append(0)
        out_img.putpalette(flat)
        out_img.save(tiles_path)
    except Exception as e:
        print(f"Error replacing tileset palette: {e}")

def open_image_for_conversion(main_window):
    from ui.dialogs.conversion_dialog import ConversionDialog
    
    start_dir = _get_image_directory(main_window)
    
    input_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_image"),
        start_dir,
        main_window.translator.tr("filter_images")
    )
    if not input_path:
        return

    _update_image_directory(main_window, input_path)

    dialog = ConversionDialog(image_path=input_path, parent=main_window)
    exec_dialog(dialog)

def _reset_tilemap(main_window):
    et = main_window.edit_tiles_tab
    ep = main_window.edit_palettes_tab

    for tab in (et, ep):
        tab.tilemap_data   = None
        tab.tilemap_width  = 0
        tab.tilemap_height = 0
        tab.tilemap_width_spin.setValue(32)
        tab.tilemap_height_spin.setValue(32)
        tab.edit_tilemap_scene.clear() if hasattr(tab, 'edit_tilemap_scene') else None
        tab._set_tilemap_controls_enabled(False)

    if hasattr(ep, 'edit_tilemap2_scene'):
        ep.edit_tilemap2_scene.clear()
        ep.overlay_items.clear()

    main_window.menu_bar.action_save_tilemap.setEnabled(False)
    main_window.menu_bar.action_save_selection.setEnabled(False)
    main_window.menu_bar.action_open_tilemap.setEnabled(True)
    main_window.menu_bar.action_new_tilemap.setEnabled(True)

def _reset_palette(main_window):
    from core.palette_utils import generate_grayscale_palette
    grayscale = generate_grayscale_palette()

    ep = main_window.edit_palettes_tab
    ep.palette_colors = list(grayscale)
    ep.display_palette_colors(grayscale, enable_editor=False)

    if hasattr(main_window, 'preview_tab'):
        main_window.preview_tab.display_palette_colors(grayscale)

    main_window.menu_bar.action_save_palette.setEnabled(False)

def _update_convert_actions(main_window):
    is_8bpp = getattr(main_window, 'current_bpp', 4) == 8
    is_rot  = getattr(main_window, 'current_rotation_mode', False)
    main_window.menu_bar.action_convert_to_4bpp.setEnabled(is_8bpp and not is_rot)
    main_window.menu_bar.action_convert_to_8bpp.setEnabled(not is_8bpp)
    et = getattr(main_window, 'edit_tiles_tab', None)
    has_tileset = et is not None and bool(getattr(et, 'tileset_img', None))
    has_tilemap = et is not None and bool(getattr(et, 'tilemap_data', None))
    main_window.menu_bar.action_optimize_tiles.setEnabled(has_tileset and not is_rot)
    main_window.menu_bar.action_deoptimize_tiles.setEnabled(has_tileset and not is_rot)
    main_window.menu_bar.action_convert_to_text_mode.setEnabled(has_tilemap and is_rot)
    main_window.menu_bar.action_convert_to_rot_mode.setEnabled(has_tilemap and not is_rot)

def _apply_mode_conversion(main_window, mode):
    """Shared implementation for convert_to_text_mode and convert_to_rot_mode."""
    from core.tile_optimizer import convert_text_to_rotation, convert_rotation_to_text

    et = main_window.edit_tiles_tab
    if not et.tileset_img or not et.tilemap_data:
        return

    tr = main_window.translator.tr
    title     = tr('convert_to_text_mode' if mode == 'to_text' else 'convert_to_rot_mode')
    confirm   = tr('convert_to_text_mode_confirm' if mode == 'to_text' else 'convert_to_rot_mode_confirm')
    result_key = 'convert_to_text_mode_result' if mode == 'to_text' else 'convert_to_rot_mode_result'

    reply = QMessageBox.question(main_window, title, confirm, QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    if mode == 'to_text' and (et.tilemap_width > 64 or et.tilemap_height > 64):
        QMessageBox.critical(
            main_window, title,
            tr('convert_to_text_mode_too_large',
               w=et.tilemap_width, h=et.tilemap_height)
        )
        return

    from core.config import ROT_SIZES_SET
    if mode == 'to_rot' and (et.tilemap_width, et.tilemap_height) not in ROT_SIZES_SET:
        valid = ', '.join(f'{w}x{h}' for w, h in sorted(ROT_SIZES_SET))
        QMessageBox.critical(
            main_window, title,
            tr('convert_to_rot_mode_invalid_size',
               w=et.tilemap_width, h=et.tilemap_height, valid=valid)
        )
        return

    def tilemap_index(tx, ty):
        w = et.tilemap_width
        if w <= 32:
            return ty * w + tx
        bx, by = tx // 32, ty // 32
        return (by * (w // 32) + bx) * 1024 + (ty % 32) * 32 + (tx % 32)

    old_tileset = et.tileset_img
    old_tilemap = et.tilemap_data

    if mode == 'to_text':
        new_ts, new_tm, old_count, new_count = convert_rotation_to_text(
            et.tileset_img, et.tilemap_data, et.tilemap_width, et.tilemap_height
        )
    else:
        new_ts, new_tm, old_count, new_count = convert_text_to_rotation(
            et.tileset_img, et.tilemap_data,
            et.tilemap_width, et.tilemap_height, tilemap_index
        )
        if new_ts is None:
            QMessageBox.critical(main_window, title,
                                 tr('convert_to_rot_mode_too_many', n=new_count))
            return

    new_is_rot = (mode == 'to_rot')
    main_window.current_rotation_mode = new_is_rot
    if new_is_rot:
        main_window.current_bpp = 8
    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'rotation_mode', '1' if new_is_rot else '0')
        if new_is_rot:
            main_window.config_manager.set('CONVERSION', 'bpp', '1')

    for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
        tab = getattr(main_window, attr, None)
        if tab:
            tab.tilemap_data = new_tm

    et.tileset_img = new_ts
    et.tileset_img_original = new_ts
    total = (new_ts.width // 8) * (new_ts.height // 8)
    w = et.tiles_per_row if et.tiles_per_row > 0 else new_ts.width // 8
    et.render_tileset_with_padding(w, (total + w - 1) // w, total)

    os.makedirs('output', exist_ok=True)
    new_ts.save('output/tiles.png')
    with open('output/map.bin', 'wb') as f:
        f.write(new_tm)

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.record_state(
            state_type='tile_optimizer',
            editor_type='tiles',
            data={
                'old_tilemap': old_tilemap,
                'new_tilemap': new_tm,
                'old_tileset_bytes': old_tileset.tobytes(),
                'old_tileset_size': old_tileset.size,
                'old_tileset_palette': old_tileset.getpalette(),
                'new_tileset_bytes': new_ts.tobytes(),
                'new_tileset_size': new_ts.size,
                'new_tileset_palette': new_ts.getpalette(),
                'w': et.tilemap_width, 'h': et.tilemap_height,
            },
            description=tr(result_key, old=old_count, new=new_count)
        )

    main_window._save_map_and_refresh()
    _update_convert_actions(main_window)
    QMessageBox.information(main_window, title, tr(result_key, old=old_count, new=new_count))

def convert_to_text_mode(main_window):
    _apply_mode_conversion(main_window, 'to_text')

def convert_to_rot_mode(main_window):
    _apply_mode_conversion(main_window, 'to_rot')

def _apply_tile_optimizer(main_window, mode):
    """Shared implementation for optimize/deoptimize tiles."""
    from core.tile_optimizer import optimize_tiles, deoptimize_tiles

    et = main_window.edit_tiles_tab
    if not et.tileset_img:
        return

    tr = main_window.translator.tr
    title = tr(mode + '_tiles')

    reply = QMessageBox.question(
        main_window, title,
        tr(mode + '_tiles_confirm'),
        QMessageBox.Yes | QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return

    fn = optimize_tiles if mode == 'optimize' else deoptimize_tiles
    result_key    = mode + '_tiles_result'
    no_change_key = mode + '_tiles_no_change'
    too_many_key  = 'deoptimize_tiles_too_many'

    def tilemap_index(tx, ty):
        w = et.tilemap_width
        if w <= 32:
            return ty * w + tx
        bx, by = tx // 32, ty // 32
        return (by * (w // 32) + bx) * 1024 + (ty % 32) * 32 + (tx % 32)

    old_tileset = et.tileset_img
    old_tilemap = et.tilemap_data

    new_tileset, new_tilemap, old_count, new_count = fn(
        et.tileset_img, et.tilemap_data,
        et.tilemap_width, et.tilemap_height, tilemap_index
    )

    if et.tilemap_data:
        old_count = len(set(
            (et.tilemap_data[i*2] | (et.tilemap_data[i*2+1] << 8)) & 0x3FF
            for i in range(et.tilemap_width * et.tilemap_height)
        ))
        new_count = len(set(
            (new_tilemap[i*2] | (new_tilemap[i*2+1] << 8)) & 0x3FF
            for i in range(et.tilemap_width * et.tilemap_height)
        )) if new_tilemap else new_count

    if mode == 'deoptimize' and new_count > 1024:
        QMessageBox.critical(main_window, title, tr(too_many_key, n=new_count))
        return

    if new_count == old_count and new_tilemap == old_tilemap:
        QMessageBox.information(main_window, title, tr(no_change_key))
        return

    et.tileset_img = new_tileset
    et.tileset_img_original = new_tileset
    total = (new_tileset.width // 8) * (new_tileset.height // 8)
    w = et.tiles_per_row if et.tiles_per_row > 0 else new_tileset.width // 8
    et.render_tileset_with_padding(w, (total + w - 1) // w, total)

    for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
        tab = getattr(main_window, attr, None)
        if tab and new_tilemap:
            tab.tilemap_data = new_tilemap

    os.makedirs('output', exist_ok=True)
    new_tileset.save('output/tiles.png')
    if new_tilemap:
        with open('output/map.bin', 'wb') as f:
            f.write(new_tilemap)

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.record_state(
            state_type='tile_optimizer',
            editor_type='tiles',
            data={
                'old_tilemap': old_tilemap,
                'new_tilemap': new_tilemap,
                'old_tileset_bytes': old_tileset.tobytes(),
                'old_tileset_size': old_tileset.size,
                'old_tileset_palette': old_tileset.getpalette(),
                'new_tileset_bytes': new_tileset.tobytes(),
                'new_tileset_size': new_tileset.size,
                'new_tileset_palette': new_tileset.getpalette(),
                'w': et.tilemap_width, 'h': et.tilemap_height,
            },
            description=tr(result_key, old=old_count, new=new_count)
        )

    if new_tilemap:
        main_window._save_map_and_refresh()

    QMessageBox.information(main_window, title, tr(result_key, old=old_count, new=new_count))

def optimize_tiles(main_window):
    _apply_tile_optimizer(main_window, 'optimize')

def deoptimize_tiles(main_window):
    _apply_tile_optimizer(main_window, 'deoptimize')

def convert_to_4bpp(main_window):

    from core.main import main as converter_main
    from ui.dialogs.convert_bpp_dialogs import Convert4BppDialog
    import sys

    preview_path = 'temp/preview/preview.png'
    if not os.path.exists(preview_path):
        QMessageBox.warning(main_window, main_window.translator.tr("convert_to_4bpp"),
                            main_window.translator.tr("convert_to_4bpp_error_no_preview"))
        return

    with PilImage.open(preview_path) as img:
        color_count = len(set(img.convert('RGB').getdata()))
        w_tiles = img.width  // 8
        h_tiles = img.height // 8

    if color_count > 16:
        reply = QMessageBox.warning(
            main_window,
            main_window.translator.tr("convert_to_4bpp"),
            main_window.translator.tr("convert_to_4bpp_warn_colors", count=color_count),
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if reply != QMessageBox.Ok:
            return

    dlg = Convert4BppDialog(color_count, parent=main_window)
    if exec_dialog(dlg) != Convert4BppDialog.Accepted:
        return
    selected_palettes = dlg.selected_palettes()

    reply = QMessageBox.warning(
        main_window,
        main_window.translator.tr("convert_to_4bpp"),
        main_window.translator.tr("convert_irreversible_warning"),
        QMessageBox.Ok | QMessageBox.Cancel
    )
    if reply != QMessageBox.Ok:
        return

    keep_transparent = getattr(main_window, 'keep_transparent_color', False)
    save_preview     = getattr(main_window, 'save_preview_files', False)
    keep_temp        = getattr(main_window, 'keep_temp_files', False)

    tc_str = main_window.config_manager.get('CONVERSION', 'transparent_color', '0,0,0').strip() if hasattr(main_window, 'config_manager') else '0,0,0'
    transparent_color = tuple(map(int, tc_str.split(','))) if tc_str else (0, 0, 0)
    try:
        with PilImage.open(preview_path) as _pi:
            _pal = _pi.getpalette()
            if _pal:
                transparent_color = (_pal[0], _pal[1], _pal[2])
    except Exception:
        pass

    rgba_tmp = os.path.join('temp', '_conv4bpp_input.png')
    os.makedirs('temp', exist_ok=True)
    with PilImage.open(preview_path) as img:
        img.convert('RGBA').save(rgba_tmp)

    params = {
        'input_path':              rgba_tmp,
        'tilemap_path':            None,
        'selected_palettes':       selected_palettes,
        'transparent_color':       transparent_color,
        'extra_transparent_tiles': 0,
        'tile_width':              None,
        'origin':                  '0,0',
        'end':                     None,
        'output_size':             f'{w_tiles}t,{h_tiles}t',
        'save_preview':            save_preview,
        'keep_temp':               keep_temp,
        'keep_transparent':        keep_transparent,
        'bpp':                     4,
        'start_index':             0,
        'palette_size':            256,
        'rotation_mode':           False,
    }

    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    try:
        converter_main(**params)
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'bpp', '0')
        main_window.config_manager.set('CONVERSION', 'rotation_mode', '0')
        main_window.config_manager.set('CONVERSION', 'selected_palettes',
                                       ','.join(str(p) for p in selected_palettes))
    main_window.current_bpp = 4
    main_window.current_rotation_mode = False
    main_window.load_conversion_results()

def convert_to_8bpp(main_window):

    from core.main import main as converter_main
    from ui.dialogs.convert_bpp_dialogs import Convert8BppDialog
    import sys

    preview_path = 'temp/preview/preview.png'
    if not os.path.exists(preview_path):
        QMessageBox.warning(main_window, main_window.translator.tr("convert_to_8bpp"),
                            main_window.translator.tr("convert_to_8bpp_error_no_preview"))
        return

    dlg = Convert8BppDialog(parent=main_window)
    if exec_dialog(dlg) != Convert8BppDialog.Accepted:
        return
    start_index, palette_size = dlg.get_values()

    reply = QMessageBox.warning(
        main_window,
        main_window.translator.tr("convert_to_8bpp"),
        main_window.translator.tr("convert_irreversible_warning"),
        QMessageBox.Ok | QMessageBox.Cancel
    )
    if reply != QMessageBox.Ok:
        return

    keep_transparent = getattr(main_window, 'keep_transparent_color', False)
    save_preview     = getattr(main_window, 'save_preview_files', False)
    keep_temp        = getattr(main_window, 'keep_temp_files', False)

    tc_str = main_window.config_manager.get('CONVERSION', 'transparent_color', '0,0,0').strip() if hasattr(main_window, 'config_manager') else '0,0,0'
    transparent_color = tuple(map(int, tc_str.split(','))) if tc_str else (0, 0, 0)
    try:
        _tmap = open('output/map.bin', 'rb').read()
        _slots = set()
        for _i in range(0, len(_tmap) - 1, 2):
            _entry = _tmap[_i] | (_tmap[_i+1] << 8)
            _slots.add((_entry >> 12) & 0xF)
        if _slots:
            _pal_file = os.path.join('output', f'palette_{min(_slots):02d}.pal')
            if os.path.exists(_pal_file):
                with open(_pal_file, 'r', encoding='utf-8') as _pf:
                    _plines = [l.strip() for l in _pf
                               if l.strip() and not l.startswith(('JASC-PAL', '0100'))]
                if len(_plines) > 1:
                    transparent_color = tuple(map(int, _plines[1].split()))
    except Exception:
        pass

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'transparent_color',
                                       f'{transparent_color[0]},{transparent_color[1]},{transparent_color[2]}')

    with PilImage.open(preview_path) as img:
        w_tiles = img.width  // 8
        h_tiles = img.height // 8

    params = {
        'input_path':              preview_path,
        'tilemap_path':            None,
        'selected_palettes':       None,
        'transparent_color':       transparent_color,
        'extra_transparent_tiles': 0,
        'tile_width':              None,
        'origin':                  '0,0',
        'end':                     None,
        'output_size':             f'{w_tiles}t,{h_tiles}t',
        'save_preview':            save_preview,
        'keep_temp':               keep_temp,
        'keep_transparent':        True,
        'bpp':                     8,
        'start_index':             start_index,
        'palette_size':            palette_size,
        'rotation_mode':           False,
    }

    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    try:
        converter_main(**params)
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'bpp', '1')
        main_window.config_manager.set('CONVERSION', 'rotation_mode', '0')
    main_window.current_bpp = 8
    main_window.current_rotation_mode = False
    main_window.load_conversion_results()

def open_tileset(main_window):
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_tileset"),
        "",
        main_window.translator.tr("filter_images")
    )
    if not file_path:
        return

    try:
        with PilImage.open(file_path) as f:
            if f.mode != 'P':
                QMessageBox.warning(
                    main_window,
                    main_window.translator.tr("error"),
                    main_window.translator.tr("tileset_not_indexed")
                )
                return
            pil_img = f.copy()
            raw_palette = f.getpalette()
    except Exception as e:
        QMessageBox.warning(main_window, main_window.translator.tr("error"),
                            main_window.translator.tr("could_not_load_tileset").format(error=str(e)))
        return

    os.makedirs('output', exist_ok=True)

    for fname in os.listdir('output'):
        if fname != 'tiles.png':
            fpath = os.path.join('output', fname)
            try:
                os.remove(fpath)
            except Exception:
                pass

    for fpath in ('temp/preview/preview.png', 'temp/preview/palette.pal'):
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

    pil_img.save('output/tiles.png')

    from core.image_utils import analyze_tiles_bpp
    detected_bpp = analyze_tiles_bpp('output/tiles.png')
    if detected_bpp is None:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("error"),
            main_window.translator.tr("tileset_invalid_bpp")
        )
        return
    main_window.current_bpp = detected_bpp
    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'bpp', '1' if detected_bpp == 8 else '0')

    _reset_tilemap(main_window)

    palette_colors = [(0, 0, 0)] * 256
    for i in range(min(256, len(raw_palette) // 3)):
        palette_colors[i] = (raw_palette[i * 3], raw_palette[i * 3 + 1], raw_palette[i * 3 + 2])

    ep = main_window.edit_palettes_tab
    ep.palette_colors = list(palette_colors)
    ep.display_palette_colors(palette_colors, enable_editor=True)
    if hasattr(main_window, 'preview_tab'):
        main_window.preview_tab.display_palette_colors(palette_colors)
    main_window.menu_bar.action_save_palette.setEnabled(True)

    main_window.display_tileset(pil_img)
    main_window.menu_bar.action_save_tileset.setEnabled(True)
    main_window.tileset_from_conversion = False
    main_window.conversion_palette_count = 0

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

    main_window.main_tabs.setCurrentIndex(1)

def save_tileset(main_window):
    source_path = os.path.join("output", "tiles.png")

    if not os.path.exists(source_path):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("no_tileset_to_save")
        )
        return

    start_dir = _get_save_directory(main_window)
    target_path, selected_filter = QFileDialog.getSaveFileName(
        main_window,
        main_window.translator.tr("save_tileset"),
        os.path.join(start_dir, "tiles"),
        main_window.translator.tr("filter_png_bmp")
    )

    if not target_path:
        return

    _update_save_directory(main_window, target_path)

    try:
        if "bmp" in selected_filter.lower() or target_path.lower().endswith(".bmp"):
            img = PilImage.open(source_path)
            img.save(target_path, format="BMP")
        else:
            shutil.copy2(source_path, target_path)

        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("tileset_exported", path=target_path)
        )
    except Exception as e:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("save_tileset"),
            main_window.translator.tr("error_saving_tileset", error=str(e))
        )

def open_tilemap(main_window):
    from ui.dialogs.open_tilemap_dialog import OpenTilemapDialog

    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_tilemap"),
        "",
        main_window.translator.tr("filter_bin")
    )
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
    except Exception as e:
        QMessageBox.warning(main_window, main_window.translator.tr("error"),
                            main_window.translator.tr("open_tilemap_read_error", error=str(e)))
        return

    if len(raw_data) == 0:
        QMessageBox.warning(main_window, main_window.translator.tr("open_tilemap_invalid"),
                            main_window.translator.tr("open_tilemap_empty"))
        return

    can_be_text = len(raw_data) % 2 == 0
    total_tiles_text = len(raw_data) // 2 if can_be_text else 0

    dlg = OpenTilemapDialog(len(raw_data), main_window)
    if exec_dialog(dlg) != QDialog.Accepted:
        return

    w, h, bpp, is_rot = dlg.get_values()

    if is_rot:
        tilemap_data = raw_data
        expected = w * h
        if len(tilemap_data) != expected:
            QMessageBox.warning(
                main_window,
                main_window.translator.tr("open_tilemap_incompatible"),
                main_window.translator.tr("open_tilemap_incompatible_rot",
                                          expected=expected, w=w, h=h, got=len(tilemap_data))
            )
            return
    else:
        if not can_be_text:
            QMessageBox.warning(main_window, main_window.translator.tr("open_tilemap_invalid"),
                                main_window.translator.tr("open_tilemap_invalid_text_mode"))
            return
        tilemap_data = raw_data
        tiles_path = "output/tiles.png"
        if os.path.exists(tiles_path):
            try:
                with PilImage.open(tiles_path) as img:
                    tileset_tile_count = (img.width // 8) * (img.height // 8)
            except Exception:
                tileset_tile_count = None

            if tileset_tile_count is not None:
                max_tile_idx = max(
                    (tilemap_data[i * 2] | (tilemap_data[i * 2 + 1] << 8)) & 0x3FF
                    for i in range(total_tiles_text)
                )
                if max_tile_idx >= tileset_tile_count:
                    QMessageBox.warning(
                        main_window,
                        main_window.translator.tr("open_tilemap_incompatible"),
                        main_window.translator.tr("open_tilemap_incompatible_tiles",
                                                  max_idx=max_tile_idx, count=tileset_tile_count,
                                                  last=tileset_tile_count - 1)
                    )
                    return

    os.makedirs('output', exist_ok=True)
    shutil.copy2(file_path, 'output/map.bin')

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(w))
        main_window.config_manager.set('CONVERSION', 'tilemap_height', str(h))
        main_window.config_manager.set('CONVERSION', 'bpp', '1' if bpp == 8 else '0')
        main_window.config_manager.set('CONVERSION', 'rotation_mode', '1' if is_rot else '0')

    main_window.current_bpp = bpp
    main_window.current_rotation_mode = is_rot

    et = main_window.edit_tiles_tab
    et.tilemap_data   = tilemap_data
    et.tilemap_width  = w
    et.tilemap_height = h
    et.tilemap_width_spin.setValue(w)
    et.tilemap_height_spin.setValue(h)
    et.enable_tilemap_controls()

    from ui.shared_utils import pil_to_qimage as _pil_to_qimage

    save_preview     = main_window.config_manager.getboolean('SETTINGS', 'save_preview_files',     False) if hasattr(main_window, 'config_manager') else False
    keep_transparent = main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(main_window, 'config_manager') else False
    create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)

    preview_path = 'temp/preview/preview.png'
    if os.path.exists(preview_path):
        with PilImage.open(preview_path) as _f:
            preview_img = _f.copy()
        preview_pixmap = _QPixmap.fromImage(_pil_to_qimage(preview_img))

        main_window.preview_tab.preview_image_scene.clear()
        main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
        main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())

        et.edit_tilemap_scene.clear()
        et.edit_tilemap_scene.addPixmap(preview_pixmap)
        et.edit_tilemap_scene.setSceneRect(preview_pixmap.rect())

        main_window.edit_palettes_tab.display_tilemap_replica(et.edit_tilemap_scene)
        if not is_rot:
            main_window.edit_palettes_tab.update_palette_overlay(
                et.edit_tilemap_scene, tilemap_data, w, h
            )

        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)

    main_window.menu_bar.action_save_tilemap.setEnabled(True)
    main_window.sync_palettes_tab()

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

def new_tilemap(main_window):
    from ui.dialogs.new_tilemap_dialog import NewTilemapDialog
    from ui.dialogs.gba_compatibility_dialog import GBACompatibilityDialog
    from core.final_assets import reorganize_tilemap_for_gba_bg

    dlg = NewTilemapDialog(main_window)
    if exec_dialog(dlg) != QDialog.Accepted:
        return

    w, h, bpp, is_rot = dlg.get_values()

    if is_rot:
        tilemap_data = bytes(w * h)
    else:
        requires_gba_adjustment = False
        adjusted_w, adjusted_h = w, h
        if w > 32:
            if w != 64:
                requires_gba_adjustment = True
                adjusted_w = 64
            if h % 32 != 0:
                requires_gba_adjustment = True
                adjusted_h = ((h + 31) // 32) * 32

        if requires_gba_adjustment:
            compat_dlg = GBACompatibilityDialog(w, h, adjusted_w, adjusted_h, main_window)
            if not exec_dialog(compat_dlg):
                return
            w, h = adjusted_w, adjusted_h

        raw_data = b'\x00\x00' * (w * h)

        if w > 32:
            tile_list = [(0, 0, 0, 0)] * (w * h)
            reorganized = reorganize_tilemap_for_gba_bg(tile_list, w * 8, h * 8)
            final_data = bytearray()
            for tile_id, hf, vf, pal in reorganized:
                entry = tile_id & 0x3FF
                if hf: entry |= (1 << 10)
                if vf: entry |= (1 << 11)
                entry |= (pal << 12)
                final_data.extend(entry.to_bytes(2, 'little'))
            tilemap_data = bytes(final_data)
        else:
            tilemap_data = raw_data

    import os
    os.makedirs('output', exist_ok=True)
    with open(os.path.join('output', 'map.bin'), 'wb') as f:
        f.write(tilemap_data)

    if hasattr(main_window, 'config_manager'):
        main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(w))
        main_window.config_manager.set('CONVERSION', 'tilemap_height', str(h))
        main_window.config_manager.set('CONVERSION', 'bpp', str(bpp))

    main_window.current_bpp = bpp
    main_window.current_rotation_mode = is_rot

    tiles_path   = 'output/tiles.png' if os.path.exists('output/tiles.png') else None
    preview_path = 'temp/preview/preview.png' if os.path.exists('temp/preview/preview.png') else None
    main_window.edit_tiles_tab.load_tilemap(tilemap_data, tiles_path, preview_path)
    main_window.edit_tiles_tab.tilemap_width  = w
    main_window.edit_tiles_tab.tilemap_height = h
    main_window.edit_tiles_tab.tilemap_width_spin.setValue(w)
    main_window.edit_tiles_tab.tilemap_height_spin.setValue(h)
    main_window.menu_bar.action_save_tilemap.setEnabled(True)

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

    save_preview     = main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False) if hasattr(main_window, 'config_manager') else False
    keep_transparent = main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(main_window, 'config_manager') else False
    result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
    if result:
        main_window.refresh_preview_display()

def save_tilemap(main_window):
    from ui.dialogs.save_tilemap_dialog import SaveTilemapDialog

    source_path = os.path.join('output', 'map.bin')
    if not os.path.exists(source_path):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_tilemap"),
            main_window.translator.tr("no_tilemap_to_save")
        )
        return

    dlg = SaveTilemapDialog(main_window)
    if exec_dialog(dlg) != QDialog.Accepted:
        return

    bpp, is_rot, converted = dlg.get_values()

    start_dir = _get_save_directory(main_window)
    target_path, _ = QFileDialog.getSaveFileName(
        main_window,
        main_window.translator.tr("save_tilemap_dialog_title"),
        os.path.join(start_dir, "map"),
        main_window.translator.tr("filter_bin")
    )
    if not target_path:
        return

    _update_save_directory(main_window, target_path)

    try:
        if converted is not None:
            with open(target_path, 'wb') as f:
                f.write(converted)
        else:
            shutil.copy2(source_path, target_path)
        QMessageBox.information(main_window, main_window.translator.tr("save_tilemap_dialog_title"),
                                main_window.translator.tr("save_tilemap_saved", path=target_path))
    except Exception as e:
        QMessageBox.warning(main_window, main_window.translator.tr("save_tilemap_dialog_title"),
                            main_window.translator.tr("save_tilemap_error", error=str(e)))

def save_selection(main_window):
    from ui.dialogs.save_tilemap_dialog import SaveTilemapDialog

    et = main_window.edit_tiles_tab
    ep = main_window.edit_palettes_tab

    if not getattr(et, 'tilemap_data', None):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_selection"),
            main_window.translator.tr("no_tileset_to_save")
        )
        return

    current_tab = main_window.main_tabs.currentIndex()
    active_tab = ep if current_tab == 2 else et
    
    x1, y1, x2, y2 = active_tab._tilemap_sel_area
    sel_w = x2 - x1 + 1
    sel_h = y2 - y1 + 1

    reply = QMessageBox.question(
        main_window,
        main_window.translator.tr("save_selection"),
        main_window.translator.tr("save_selection_confirm",
                                  w=sel_w, h=sel_h, wpx=sel_w*8, hpx=sel_h*8,
                                  x1=x1, y1=y1, x2=x2, y2=y2),
        QMessageBox.Yes | QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return

    dlg = SaveTilemapDialog(main_window, sel_w=sel_w, sel_h=sel_h)
    if exec_dialog(dlg) != QDialog.Accepted:
        return
    bpp, is_rot, _converted = dlg.get_values()

    if is_rot:
        if (sel_w, sel_h) not in _ROT_SIZES:
            valid = ', '.join(f'{w}×{h}' for w, h in sorted(_ROT_SIZES))
            QMessageBox.warning(
                main_window,
                main_window.translator.tr("invalid_rot_size_title"),
                main_window.translator.tr("save_selection_invalid_rot_size",
                                          w=sel_w, h=sel_h, valid=valid)
            )
            return

    tilemap_data = et.tilemap_data
    tilemap_w    = et.tilemap_width
    is_rot_map   = getattr(main_window, 'current_rotation_mode', False)

    def tilemap_index(tx, ty):
        if is_rot_map or tilemap_w <= 32:
            return ty * tilemap_w + tx
        bx, by = tx // 32, ty // 32
        bxs = tilemap_w // 32
        return (by * bxs + bx) * 1024 + (ty % 32) * 32 + (tx % 32)

    entry_size = 1 if is_rot_map else 2
    sel_data = bytearray()
    for row in range(y1, y2 + 1):
        for col in range(x1, x2 + 1):
            idx = tilemap_index(col, row)
            if idx * entry_size + entry_size <= len(tilemap_data):
                sel_data.extend(tilemap_data[idx*entry_size:idx*entry_size+entry_size])
            else:
                sel_data.extend(b'\x00' * entry_size)

    if is_rot != is_rot_map:
        converted_sel = bytearray()
        if is_rot_map and not is_rot:
            for b in sel_data:
                converted_sel.extend(bytes([b & 0xFF, 0]))
        else:
            for i in range(0, len(sel_data), 2):
                converted_sel.append(sel_data[i] & 0xFF)
        sel_data = converted_sel

    start_dir = _get_save_directory(main_window)
    target_path, _ = QFileDialog.getSaveFileName(
        main_window,
        main_window.translator.tr("save_selection"),
        os.path.join(start_dir, "selection"),
        main_window.translator.tr("filter_bin")
    )
    if not target_path:
        return

    _update_save_directory(main_window, target_path)

    try:
        with open(target_path, 'wb') as f:
            f.write(sel_data)
        if hasattr(main_window, 'config_manager'):
            main_window.config_manager.set('CONVERSION', 'bpp', '1' if bpp == 8 else '0')
        main_window.current_bpp = bpp
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_selection"),
            main_window.translator.tr("save_selection_saved", path=target_path))
    except Exception as e:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("save_selection"),
            main_window.translator.tr("save_selection_error", error=str(e)))

def open_palette(main_window):

    palette_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.translator.tr("open_palette_title"),
        "",
        main_window.translator.tr("filter_palette")
    )

    if not palette_path:
        return

    colors = []
    ext = os.path.splitext(palette_path)[1].lower()

    if ext in ('.png', '.bmp'):
        try:
            with PilImage.open(palette_path) as img:
                if img.mode != 'P':
                    QMessageBox.warning(
                        main_window,
                        main_window.translator.tr("open_palette_not_indexed_title"),
                        main_window.translator.tr("open_palette_not_indexed", mode=img.mode)
                    )
                    return
                raw = img.getpalette()
            for i in range(0, min(len(raw), 768), 3):
                colors.append((raw[i], raw[i+1], raw[i+2]))
        except Exception as e:
            QMessageBox.warning(main_window,
                                main_window.translator.tr("open_palette_image_error_title"),
                                main_window.translator.tr("open_palette_image_error", error=str(e)))
            return
    else:
        try:
            with open(palette_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f
                         if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            if not lines:
                raise ValueError("Invalid palette file format")
            color_count = int(lines[0])
            for i in range(1, min(1 + color_count, len(lines))):
                r, g, b = map(int, lines[i].split())
                colors.append((r, g, b))
        except Exception as e:
            QMessageBox.warning(main_window,
                                main_window.translator.tr("open_palette_file_error_title"),
                                main_window.translator.tr("open_palette_file_error", error=str(e)))
            return

    if not colors:
        QMessageBox.warning(main_window,
                            main_window.translator.tr("open_palette_empty_title"),
                            main_window.translator.tr("open_palette_empty"))
        return

    _apply_palette_colors(main_window, colors)

def save_palette(main_window):
    output_dir = "output"

    if not os.path.exists(output_dir):
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette"),
            main_window.translator.tr("no_palette_files_to_save")
        )
        return

    palette_files = sorted(
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith("palette_") and f.endswith(".pal")
    )
    
    if not palette_files:
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette"),
            main_window.translator.tr("no_palette_files_to_save")
        )
        return
    
    target_dir = QFileDialog.getExistingDirectory(
        main_window,
        main_window.translator.tr("select_palette_save_directory"),
        "",
        QFileDialog.ShowDirsOnly
    )
    
    if not target_dir:
        return

    existing = [
        os.path.basename(p) for p in palette_files
        if os.path.exists(os.path.join(target_dir, os.path.basename(p)))
    ]
    if existing:
        tr = main_window.translator.tr
        reply = QMessageBox.question(
            main_window,
            tr("save_palette"),
            tr("export_overwrite_confirm", files="\n".join(existing)),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

    try:
        for source_path in palette_files:
            file_name = os.path.basename(source_path)
            target_path = os.path.join(target_dir, file_name)
            shutil.copy2(source_path, target_path)
        
        QMessageBox.information(
            main_window,
            main_window.translator.tr("save_palette_complete"),
            main_window.translator.tr(
                "palette_files_saved", 
                count=len(palette_files), 
                path=target_dir
            )
        )
        
    except Exception as e:
        QMessageBox.warning(
            main_window,
            main_window.translator.tr("save_palette_error"),
            main_window.translator.tr("error_saving_palette", error=str(e))
        )

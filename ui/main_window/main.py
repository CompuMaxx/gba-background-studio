# ui/main_window/main.py
import os
from PIL import Image as PilImage

from ..custom_status_bar import CustomStatusBar
from ..preview_tab import PreviewTab
from ..edit_tiles_tab import EditTilesTab
from ..edit_palettes_tab import EditPalettesTab
from ..menu_bar import MenuBar
from utils.translator import Translator
from core.config_manager import ConfigManager
from ..hover_manager import HoverManager
from ..grid_manager import GridManager
from ..history_manager import HistoryManager
from ui.qt_compat import (
    Qt,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPixmap,
    QIcon,
    QBrush,
    QColor,
    exec_dialog,
)

class GBABackgroundStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        from core.app_mode import set_gui_mode
        set_gui_mode(True)
        self.config_manager = ConfigManager()

        self.current_bpp = 4
        self.current_rotation_mode = False
        self.tileset_from_conversion = False
        self.set_window_icon()

        from .config import load_configuration
        load_configuration(self)

        self.translator = Translator(lang_dir="lang", default_lang=self.config_manager.get('SETTINGS', 'language', 'english'))

        self.setWindowTitle("GBA Background Studio")
        self.resize(754, 644)

        self.tile_size = 8
        self.zoom_level = 100
        self.zoom_levels = [100, 200, 300, 400, 500, 600, 700, 800]
        self.current_zoom_index = 0
        self.output_loaded_for_zoom = False
        self.selected_tile_id = 0
        self.selected_tile_image = None
        self.tileset_columns = 0
        self.tileset_rows = 0
        self.tileset_tiles = []
        self.tileset_ids = {}
        self.tilemap_ids = []
        self.tilemap_tiles = []
        self.tilemap_columns = 0
        self.tilemap_rows = 0
        self.current_tileset = None
        self.is_drawing = False
        self.current_status_message = self.translator.tr("ready_status")
        self.last_tile_pos = (-1, -1)
        self._last_image_directory = None
        self._last_save_directory = None

        self.hover_manager = HoverManager()
        self.grid_manager = GridManager()

        self.setup_ui()

        self.history_manager = HistoryManager()
        self.history_manager.history_changed.connect(self.update_undo_redo_actions)
        self.main_tabs.currentChanged.connect(self.on_tab_changed)

        from .config import setup_grids
        setup_grids(self)

        load_configuration(self)
        
        if self.load_last_output:
            from .file_ops import load_last_output_files
            load_last_output_files(self)

    def setup_ui(self):
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.North)
        self.main_tabs.setStyleSheet("QTabBar::tab { min-height: 32px; }")
        main_layout.addWidget(self.main_tabs)

        self.preview_tab = PreviewTab(self)
        self.edit_tiles_tab = EditTilesTab(self)
        self.edit_palettes_tab = EditPalettesTab(self)
        
        self.main_tabs.addTab(self.preview_tab, self.translator.tr("preview_tab"))
        self.main_tabs.addTab(self.edit_tiles_tab, self.translator.tr("edit_tiles_tab"))
        self.main_tabs.addTab(self.edit_palettes_tab, self.translator.tr("edit_palettes_tab"))

        from .toolbar import ContextToolbar
        self.context_toolbar = ContextToolbar(self, self.main_tabs)

        self.custom_status_bar = CustomStatusBar(translator=self.translator)
        main_layout.addWidget(self.custom_status_bar)

        self.custom_status_bar.update_status(
            selection_type="Tile",
            selection_id="-",
            tilemap_pos=(-1, -1),
            tile_id="-",
            palette_id="-",
            flip_state="None",
            zoom_level=100
        )

        self.menu_bar = MenuBar(self)
        
        from .config import apply_configuration_to_menu
        apply_configuration_to_menu(self)
        
        from .view_ops import setup_wheel_events
        setup_wheel_events(self)

        self.hover_manager.register_view(self.edit_tiles_tab.edit_tilemap_view)
        self.hover_manager.register_view(self.edit_palettes_tab.edit_tilemap2_view)
        self.update_undo_redo_actions()

        if hasattr(self, 'history_manager'):
            self.history_manager.history_changed.connect(self.update_undo_redo_actions)
        
        self.update_undo_redo_actions()

    def keyPressEvent(self, event):
        focused_widget = self.focusWidget()
        is_color_edit_field = False
        
        if focused_widget:
            widget = focused_widget
            for _ in range(10):
                if widget is None:
                    break
                try:
                    if (hasattr(widget, '__class__') and 
                        widget.__class__.__name__ == 'ColorEditor'):
                        is_color_edit_field = True
                        break
                        
                    if (hasattr(widget, 'parent') and 
                        callable(getattr(widget, 'parent', None))):
                        parent = widget.parent()
                        if (parent is not None and 
                            hasattr(parent, '__class__') and 
                            parent.__class__.__name__ == 'ColorEditor'):
                            is_color_edit_field = True
                            break
                            
                    if hasattr(widget, 'parent') and callable(getattr(widget, 'parent', None)):
                        widget = widget.parent()
                    else:
                        break
                except:
                    break
        
        if is_color_edit_field and event.modifiers() & Qt.ControlModifier:
            if event.key() in [Qt.Key_Z, Qt.Key_Y]:
                event.ignore()
                return
        
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo()
            event.accept()
            return
            
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.redo()
            event.accept()
            return
            
        elif (event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier) and 
              event.key() == Qt.Key_Z):
            self.redo()
            event.accept()
            return
            
        super().keyPressEvent(event)

    def update_undo_redo_actions(self):
        if not hasattr(self, 'menu_bar') or not hasattr(self, 'history_manager'):
            return
        
        can_undo = self.history_manager.can_undo()
        can_redo = self.history_manager.can_redo()
        
        if hasattr(self.menu_bar, 'action_undo'):
            self.menu_bar.action_undo.setEnabled(can_undo)
        
        if hasattr(self.menu_bar, 'action_redo'):
            self.menu_bar.action_redo.setEnabled(can_redo)

    def set_window_icon(self):
        try:

            
            app_icon = QIcon()
            icon_sizes = [
                ("icons/icon_16x16.png", 16),
                ("icons/icon_32x32.png", 32),
                ("icons/icon_64x64.png", 64),
                ("icons/icon_128x128.png", 128),
                ("icons/icon_256x256.png", 256),
                ("icon.png", 512)
            ]
            
            for icon_path, size in icon_sizes:
                full_path = os.path.join("assets", icon_path)
                if os.path.exists(full_path):
                    app_icon.addFile(full_path)
            
            if not app_icon.isNull():
                self.setWindowIcon(app_icon)
                
        except Exception as e:
            print(f"Error setting window icon: {e}")

    def refresh_preview_display(self):
        preview_path = "temp/preview/preview.png"
        if not os.path.exists(preview_path):
            print("Preview not found, skipping refresh")
            return
        
        try:
            from PIL import Image
            from ui.shared_utils import pil_to_qimage

            
            with Image.open(preview_path) as f:
                preview_img = f.copy()
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            self.preview_tab.preview_image_scene.clear()
            self.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            self.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())

            self.edit_tiles_tab.edit_tilemap_scene.clear()
            self.edit_tiles_tab.edit_tilemap_scene.addPixmap(preview_pixmap)
            self.edit_tiles_tab.edit_tilemap_scene.setSceneRect(preview_pixmap.rect())
            
            self.edit_palettes_tab.tilemap_data = self.edit_tiles_tab.tilemap_data
            self.edit_palettes_tab.tilemap_width = preview_img.width // 8
            self.edit_palettes_tab.tilemap_height = preview_img.height // 8
            self.edit_tiles_tab.tilemap_width = self.edit_palettes_tab.tilemap_width
            self.edit_tiles_tab.tilemap_height = self.edit_palettes_tab.tilemap_height
            self.edit_palettes_tab.display_tilemap_replica(self.edit_tiles_tab.edit_tilemap_scene)
            
            if hasattr(self, 'apply_zoom_to_all'):
                self.apply_zoom_to_all()

            for tab in (self.edit_tiles_tab, self.edit_palettes_tab):
                if hasattr(tab, '_restore_tilemap_selection'):
                    tab._restore_tilemap_selection()
                
        except Exception as e:
            print(f"Error refreshing preview display: {e}")
            import traceback
            traceback.print_exc()

    def undo(self, checked=False):
        if hasattr(self, 'history_manager'):
            state = self.history_manager.undo()
            if state:
                self.apply_history_state(state, is_undo=True)

    def redo(self, checked=False):
        if hasattr(self, 'history_manager'):
            state = self.history_manager.redo()
            if state:
                self.apply_history_state(state, is_undo=False)

    def apply_history_state(self, state, is_undo=True):
        try:
            if state['type'] == 'tile_change':
                self.apply_tile_change(state, is_undo)
            elif state['type'] == 'palette_change':
                self.apply_palette_change(state, is_undo)
            elif state['type'] == 'color_edit' and state['editor'] == 'palettes':
                data = state['data']
                if is_undo:
                    r, g, b = data['old_color']
                else:
                    r, g, b = data['new_color']
                self.edit_palettes_tab.apply_color_change(data['index'], r, g, b)

            elif state['type'] == 'move_color':
                self.apply_move_color(state, is_undo)
                
            elif state['type'] == 'tilemap_resize':
                self.apply_tilemap_resize(state, is_undo)
            elif state['type'] in ('pal_replace', 'pal_swap'):
                self.apply_pal_tilemap_op(state, is_undo)
            elif state['type'] == 'tilemap_cut':
                self.apply_tilemap_cut(state, is_undo)
            elif state['type'] in ('tilemap_transform', 'tilemap_paste'):
                self.apply_tilemap_cut(state, is_undo)
            elif state['type'] == 'tile_optimizer':
                self.apply_tile_optimizer(state, is_undo)
            elif state['type'] == 'tilemap_shift':
                self.apply_tilemap_shift(state, is_undo)
            elif state['type'] == 'tileset_reshape':
                self.apply_tileset_reshape(state, is_undo)
        except Exception as e:
            print(f"Error applying history state: {e}")

    def apply_move_color(self, state, is_undo):
        import numpy as np
        from PIL import Image as _Img
        data = state['data']
        colors        = data['old_colors']       if is_undo else data['new_colors']
        tiles_data    = data['old_tiles_data']   if is_undo else data['new_tiles_data']
        tiles_shape   = data['tiles_shape']
        preview_data  = data.get('old_preview_data' if is_undo else 'new_preview_data')
        preview_shape = data.get('preview_shape')

        ep = self.edit_palettes_tab
        ep.palette_colors = list(colors)

        for i, (r, g, b) in enumerate(colors):
            if i < len(ep.palette_rects):
                ep.palette_rects[i].setBrush(QBrush(QColor(r, g, b)))

        flat = [c for rgb in colors for c in rgb]
        while len(flat) < 768:
            flat.append(0)

        def _restore_image(path, raw_data, shape):
            if not raw_data or not shape:
                return
            arr = np.frombuffer(raw_data, dtype=np.uint8).reshape(shape)
            out = _Img.fromarray(arr, mode='P')
            out.putpalette(flat)
            out.save(path)

        _restore_image('output/tiles.png', tiles_data, tiles_shape)
        _restore_image('temp/preview/preview.png', preview_data, preview_shape)

        if tiles_data and tiles_shape:
            try:
                et = self.edit_tiles_tab
                with _Img.open('output/tiles.png') as f:
                    et.tileset_img = f.copy()
                    et.tileset_img_original = et.tileset_img
                total = (et.tileset_img.width // 8) * (et.tileset_img.height // 8)
                w = et.tiles_per_row if et.tiles_per_row > 0 else et.tileset_img.width // 8
                et.render_tileset_with_padding(w, (total + w - 1) // w, total)
            except Exception as e:
                print(f"apply_move_color tiles error: {e}")

        ep._save_and_update_all(skip_tiles=True)

        if ep.palette_colors:
            idx = ep.current_editing_index
            idx = max(0, min(idx, len(ep.palette_colors) - 1))
            r, g, b = ep.palette_colors[idx]
            ep.color_editor.set_color(idx, r, g, b)
            ep.draw_selection_rectangle(idx)

    def apply_tileset_reshape(self, state, is_undo):
        if not hasattr(self, 'edit_tiles_tab') or not self.edit_tiles_tab.tileset_img_original:
            return

        data = state['data']
        target_width = data['old_width'] if is_undo else data['new_width']
        target_height = data['old_height'] if is_undo else data['new_height']
        total_tiles = (self.edit_tiles_tab.tileset_img_original.width // 8) * \
                    (self.edit_tiles_tab.tileset_img_original.height // 8)

        self.edit_tiles_tab.tile_width_spin.blockSignals(True)
        self.edit_tiles_tab.tile_width_spin.setValue(target_width)
        self.edit_tiles_tab.tile_width_spin.blockSignals(False)
        self.edit_tiles_tab.tileset_height_label.setText(str(target_height))
        self.edit_tiles_tab.tiles_per_row = target_width
        self.edit_tiles_tab._tileset_width_before_edit = target_width
        self.edit_tiles_tab.render_tileset_with_padding(target_width, target_height, total_tiles)

        if self.edit_tiles_tab.tileset_img:
            self.edit_tiles_tab.tileset_img.save("output/tiles.png")

    def apply_tile_optimizer(self, state, is_undo):
        import os
        from PIL import Image as PilImage
        import numpy as np
        data = state['data']
        tilemap = data['old_tilemap'] if is_undo else data['new_tilemap']
        ts_bytes  = data['old_tileset_bytes']   if is_undo else data['new_tileset_bytes']
        ts_size   = data['old_tileset_size']     if is_undo else data['new_tileset_size']
        ts_pal    = data['old_tileset_palette']  if is_undo else data['new_tileset_palette']
        arr = np.frombuffer(ts_bytes, dtype=np.uint8).reshape(ts_size[1], ts_size[0])
        tileset = PilImage.fromarray(arr, mode='P')
        tileset.putpalette(ts_pal)
        os.makedirs('output', exist_ok=True)
        tileset.save('output/tiles.png')
        with open('output/map.bin', 'wb') as f:
            f.write(tilemap)
        et = self.edit_tiles_tab
        et.tileset_img = tileset
        et.tileset_img_original = tileset
        et.tilemap_data = tilemap
        self.edit_palettes_tab.tilemap_data = tilemap
        total = (tileset.width // 8) * (tileset.height // 8)
        w = et.tiles_per_row if et.tiles_per_row > 0 else tileset.width // 8
        et.render_tileset_with_padding(w, (total + w - 1) // w, total)
        self._save_map_and_refresh()

    def apply_tilemap_cut(self, state, is_undo):
        data = state['data']
        new_data = data['old_data'] if is_undo else data['new_data']
        self.edit_tiles_tab.tilemap_data = new_data
        self.edit_palettes_tab.tilemap_data = new_data
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)
        self._save_map_and_refresh()

    def apply_pal_tilemap_op(self, state, is_undo):
        data = state['data']
        new_data = data['old_data'] if is_undo else data['new_data']
        self.edit_tiles_tab.tilemap_data = new_data
        self.edit_palettes_tab.tilemap_data = new_data
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)
        ep = self.edit_palettes_tab
        for ty in range(ep.tilemap_height):
            for tx in range(ep.tilemap_width):
                idx = ep._tilemap_index(tx, ty)
                if idx * 2 + 2 > len(new_data):
                    continue
                entry = new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)
                ep.update_palette_overlay_for_tile(tx, ty, (entry >> 12) & 0xF)
        self._save_map_and_refresh()

    def apply_tilemap_shift(self, state, is_undo):
        data = state['data']
        new_data = data['old_data'] if is_undo else data['new_data']

        self.edit_tiles_tab.tilemap_data = new_data
        self.edit_palettes_tab.tilemap_data = new_data

        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)

        from core.image_utils import create_gbagfx_preview
        save_preview     = self.config_manager.getboolean('SETTINGS', 'save_preview_files',     False) if hasattr(self, 'config_manager') else False
        keep_transparent = self.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(self, 'config_manager') else False
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result:
            self.refresh_preview_display()

    def apply_tilemap_resize(self, state, is_undo):
        if not hasattr(self, 'edit_tiles_tab'):
            return

        data = state['data']
        
        if is_undo:
            new_data = data['old_data']
            new_w = data['old_w']
            new_h = data['old_h']
        else:
            new_data = data['new_data']
            new_w = data['new_w']
            new_h = data['new_h']
            
        self.edit_tiles_tab.tilemap_data = new_data
        self.edit_tiles_tab.tilemap_width = new_w
        self.edit_tiles_tab.tilemap_height = new_h
        self.edit_tiles_tab.tilemap_width_spin.setValue(new_w)
        self.edit_tiles_tab.tilemap_height_spin.setValue(new_h)

        if hasattr(self, 'edit_palettes_tab'):
            self.edit_palettes_tab.tilemap_data = new_data
            self.edit_palettes_tab.tilemap_width = new_w
            self.edit_palettes_tab.tilemap_height = new_h
            self.edit_palettes_tab.tilemap_width_spin.setValue(new_w)
            self.edit_palettes_tab.tilemap_height_spin.setValue(new_h)

        if hasattr(self, 'config_manager'):
            self.config_manager.set('CONVERSION', 'tilemap_width',  str(new_w))
            self.config_manager.set('CONVERSION', 'tilemap_height', str(new_h))

        import os
        os.makedirs('output', exist_ok=True)
        with open(os.path.join('output', 'map.bin'), 'wb') as f:
            f.write(new_data)

        from core.image_utils import create_gbagfx_preview
        save_preview = self.config_manager.getboolean('SETTINGS', 'save_preview_files', False) if hasattr(self, 'config_manager') else False
        keep_transparent = self.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(self, 'config_manager') else False
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result:
            self.refresh_preview_display()
    
    def _save_map_and_refresh(self):
        import os
        tilemap_data = getattr(self.edit_tiles_tab, 'tilemap_data', None)
        if not tilemap_data:
            return
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(tilemap_data)
        from core.image_utils import create_gbagfx_preview
        save_preview     = self.config_manager.getboolean('SETTINGS', 'save_preview_files',     False) if hasattr(self, 'config_manager') else False
        keep_transparent = self.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False) if hasattr(self, 'config_manager') else False
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result:
            self.refresh_preview_display()

    def apply_tile_change(self, state, is_undo):
        if not hasattr(self, 'edit_tiles_tab') or not self.edit_tiles_tab.tilemap_data:
            return

        if hasattr(self, 'history_manager'):
            self.history_manager.is_undoing = True
        
        try:
            tile_x = state['data']['tile_x']
            tile_y = state['data']['tile_y']

            if is_undo:
                tile_id = state['data']['old_tile_id']
                palette_id = state['data']['old_palette_id']
                h_flip = state['data']['old_h_flip']
                v_flip = state['data']['old_v_flip']
            else:
                tile_id = state['data']['new_tile_id']
                h_flip = state['data']['new_h_flip']
                v_flip = state['data']['new_v_flip']
                
                tile_index = tile_y * self.edit_tiles_tab.tilemap_width + tile_x
                current_entry = self.edit_tiles_tab.tilemap_data[tile_index * 2] | (self.edit_tiles_tab.tilemap_data[tile_index * 2 + 1] << 8)
                palette_id = (current_entry >> 12) & 0xF

            new_entry = tile_id

            if h_flip:
                new_entry |= (1 << 10)

            if v_flip:
                new_entry |= (1 << 11)

            new_entry |= (palette_id << 12)

            tilemap_data = bytearray(self.edit_tiles_tab.tilemap_data)
            tile_index = tile_y * self.edit_tiles_tab.tilemap_width + tile_x
            tilemap_data[tile_index * 2] = new_entry & 0xFF
            tilemap_data[tile_index * 2 + 1] = (new_entry >> 8) & 0xFF
            self.edit_tiles_tab.tilemap_data = bytes(tilemap_data)

            self.edit_tiles_tab.update_single_tile_visual(tile_x, tile_y)

            if hasattr(self, 'edit_palettes_tab'):
                self.edit_palettes_tab.tilemap_data = self.edit_tiles_tab.tilemap_data
                self.edit_palettes_tab.update_single_tile_replica(tile_x, tile_y)

            self._save_map_and_refresh()

        finally:
            if hasattr(self, 'history_manager'):
                self.history_manager.is_undoing = False

    def apply_palette_change(self, state, is_undo):
        if not hasattr(self, 'edit_palettes_tab') or not self.edit_palettes_tab.tilemap_data:
            return
            
        tile_x = state['data']['tile_x']
        tile_y = state['data']['tile_y']
        
        if is_undo:
            palette_id = state['data']['old_palette_id']
        else:
            palette_id = state['data']['new_palette_id']
        
        tile_index = tile_y * self.edit_palettes_tab.tilemap_width + tile_x
        current_entry = self.edit_palettes_tab.tilemap_data[tile_index * 2] | (self.edit_palettes_tab.tilemap_data[tile_index * 2 + 1] << 8)
        
        tile_id = current_entry & 0x3FF
        h_flip = bool(current_entry & (1 << 10))
        v_flip = bool(current_entry & (1 << 11))
        
        new_entry = tile_id
        if h_flip:
            new_entry |= (1 << 10)
        if v_flip:
            new_entry |= (1 << 11)
        new_entry |= (palette_id << 12)

        tilemap_data = bytearray(self.edit_palettes_tab.tilemap_data)
        tilemap_data[tile_index * 2] = new_entry & 0xFF
        tilemap_data[tile_index * 2 + 1] = (new_entry >> 8) & 0xFF
        
        self.edit_palettes_tab.tilemap_data = bytes(tilemap_data)
        self.edit_palettes_tab.update_palette_overlay_for_tile(tile_x, tile_y, palette_id)
        
        if hasattr(self, 'edit_tiles_tab'):
            self.edit_tiles_tab.tilemap_data = self.edit_palettes_tab.tilemap_data
            self.edit_tiles_tab.update_single_tile_visual(tile_x, tile_y)

        self._save_map_and_refresh()

    def sync_between_editors(self):
        if hasattr(self, 'edit_tiles_tab') and hasattr(self, 'edit_palettes_tab'):
            if hasattr(self.edit_tiles_tab, 'tilemap_data'):
                self.edit_palettes_tab.tilemap_data = self.edit_tiles_tab.tilemap_data
            
            if hasattr(self.edit_palettes_tab, 'tilemap_data'):
                self.edit_tiles_tab.tilemap_data = self.edit_palettes_tab.tilemap_data
            
            if hasattr(self.edit_tiles_tab, 'tilemap_data') and self.edit_tiles_tab.tilemap_data:
                self.edit_tiles_tab.load_tilemap(
                    self.edit_tiles_tab.tilemap_data,
                    "output/tiles.png" if hasattr(self.edit_tiles_tab, 'tileset_img') and self.edit_tiles_tab.tileset_img else None,
                    "temp/preview/preview.png" if os.path.exists("temp/preview/preview.png") else None
                )
            
            if hasattr(self.edit_palettes_tab, 'tilemap_data') and self.edit_palettes_tab.tilemap_data:
                self.edit_palettes_tab.update_palette_overlay(
                    self.edit_tiles_tab.edit_tilemap_scene,
                    self.edit_palettes_tab.tilemap_data,
                    self.edit_palettes_tab.tilemap_width,
                    self.edit_palettes_tab.tilemap_height
                )

    def load_configuration(self):
        from .config import load_configuration
        load_configuration(self)
    
    def apply_configuration_to_menu(self):
        from .config import apply_configuration_to_menu
        apply_configuration_to_menu(self)
    
    def toggle_show_success_dialog(self, checked):
        from .config import toggle_show_success_dialog
        toggle_show_success_dialog(self, checked)
    
    def toggle_load_last_output(self, checked):
        from .config import toggle_load_last_output
        toggle_load_last_output(self, checked)
    
    def toggle_save_conversion_params(self, checked):
        from .config import toggle_save_conversion_params
        toggle_save_conversion_params(self, checked)
    
    def on_tab_changed(self, index):
        from .tab_ops import on_tab_changed
        on_tab_changed(self, index)
    
    def setup_wheel_events(self):
        from .view_ops import setup_wheel_events
        setup_wheel_events(self)
    
    def open_image_for_conversion(self, checked=False):
        from .file_ops import open_image_for_conversion
        open_image_for_conversion(self)
    
    def convert_to_4bpp(self, checked=False):
        from .file_ops import convert_to_4bpp
        convert_to_4bpp(self)

    def convert_to_8bpp(self, checked=False):
        from .file_ops import convert_to_8bpp
        convert_to_8bpp(self)

    def convert_to_text_mode(self, checked=False):
        from .file_ops import convert_to_text_mode
        convert_to_text_mode(self)

    def convert_to_rot_mode(self, checked=False):
        from .file_ops import convert_to_rot_mode
        convert_to_rot_mode(self)

    def optimize_tiles(self, checked=False):
        from .file_ops import optimize_tiles
        optimize_tiles(self)

    def deoptimize_tiles(self, checked=False):
        from .file_ops import deoptimize_tiles
        deoptimize_tiles(self)

    def open_tileset(self, checked=False):
        from .file_ops import open_tileset
        open_tileset(self)
    
    def save_tileset(self, checked=False):
        from .file_ops import save_tileset
        save_tileset(self)
    
    def open_tilemap(self, checked=False):
        from .file_ops import open_tilemap
        open_tilemap(self)
    
    def new_tilemap(self, checked=False):
        from .file_ops import new_tilemap
        new_tilemap(self)
    
    def save_tilemap(self, checked=False):
        from .file_ops import save_tilemap
        save_tilemap(self)
    
    def save_selection(self, checked=False):
        from .file_ops import save_selection
        save_selection(self)
    
    def open_palette(self, checked=False):
        from .file_ops import open_palette
        open_palette(self)
    
    def save_palette(self, checked=False):
        from .file_ops import save_palette
        save_palette(self)
    
    def toggle_save_preview(self, checked):
        from .config import toggle_save_preview
        toggle_save_preview(self, checked)
    
    def toggle_keep_transparent(self, checked):
        from .config import toggle_keep_transparent
        toggle_keep_transparent(self, checked)
    
    def toggle_keep_temp(self, checked):
        from .config import toggle_keep_temp
        toggle_keep_temp(self, checked)
    
    def reset_zoom(self, checked=False):
        from .view_ops import reset_zoom
        reset_zoom(self)
    
    def zoom_in(self, checked=False):
        from .view_ops import zoom_in
        zoom_in(self)
    
    def zoom_out(self, checked=False):
        from .view_ops import zoom_out
        zoom_out(self)
    
    def apply_zoom_to_all(self):
        from .view_ops import apply_zoom_to_all
        apply_zoom_to_all(self)
    
    def apply_zoom_to_view(self, view, zoom_factor):
        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(self, view, zoom_factor)
    
    def update_hover_from_current_cursor(self):
        from .tab_ops import update_hover_from_current_cursor
        update_hover_from_current_cursor(self)
    
    def apply_zoom_to_new_content(self, view):
        from .view_ops import apply_zoom_to_new_content
        apply_zoom_to_new_content(self, view)
    
    def toggle_grid(self, checked):
        from .config import toggle_grid
        toggle_grid(self, checked)

    def open_display_settings(self, checked=False):
        from ui.dialogs.display_settings_dialog import DisplaySettingsDialog
        dlg = DisplaySettingsDialog(self, parent=self)
        exec_dialog(dlg)
    
    def toggle_status_bar(self, checked):
        from .config import toggle_status_bar
        toggle_status_bar(self, checked)
    
    def toggle_remember_file_paths(self, checked):
        from .config import toggle_remember_file_paths
        toggle_remember_file_paths(self, checked)
    
    def change_language(self, language_code):
        from .utils import change_language
        change_language(self, language_code)
    
    def retranslate_ui(self):
        from .utils import retranslate_ui
        retranslate_ui(self)
    
    def recreate_menu(self):
        from .utils import recreate_menu
        recreate_menu(self)
    
    def show_contribute(self, checked=False):
        from .dialogs import show_contribute
        show_contribute(self)
    
    def show_about(self, checked=False):
        from .dialogs import show_about
        show_about(self)
    
    def display_tileset(self, pil_img):
        from .tab_ops import display_tileset
        display_tileset(self, pil_img)
    
    def sync_palettes_tab(self):
        from .tab_ops import sync_palettes_tab
        sync_palettes_tab(self)
    
    def load_conversion_results(self):
        from .tab_ops import load_conversion_results
        load_conversion_results(self)
    
    def load_last_output_files(self):
        from .file_ops import load_last_output_files
        load_last_output_files(self)

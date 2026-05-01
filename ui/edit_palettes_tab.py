# ui/edit_palettes_tab.py
import os

from PIL import Image as PilImage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared, pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared
from ui.palette_grid_view import PaletteGridView
from ui.color_editor import ColorEditor
from ui.tilemap_utils import TilemapUtils
from ui.qt_compat import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QGraphicsView,
    QGraphicsScene,
    QHBoxLayout,
    QGraphicsPixmapItem,
    QFrame,
    QSlider,
    QSizePolicy,
    QGridLayout,
    QGraphicsRectItem,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QCheckBox,
    QFont,
    QBrush,
    QPen,
    QColor,
    QPainter,
    QPixmap,
    QIntValidator,
    Qt,
    Signal,
    QTimer,
    QSize,
    QImage
)

EMPTY_TILE_ENTRY = b'\x00\x00'

def _invert_lut(lut):
    inv = list(range(256))
    for old, new in enumerate(lut):
        inv[new] = old
    return inv

class EditPalettesTab(TilemapUtils, QWidget):
    @property
    def _tr(self):
        """Get translator from main_window if available, otherwise use module-level fallback."""
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'translator'):
            return self.main_window.translator.tr
        return lambda key, **kw: key

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.selected_palette_id = 0
        self.last_palette_pos = (-1, -1)
        self.last_hover_pos = (-1, -1)
        self.tilemap_width = 0
        self.tilemap_height = 0
        self.tilemap_data = None
        self.overlay_items = {}
        self.palette_colors = [(0, 0, 0)] * 256
        self._overlay_text_color = QColor(0, 0, 0)
        self._overlay_alpha = 0.3
        self.selection_rect = None
        self.palette_rects = []

        self.last_edited_index = -1
        self.last_edited_color = (0, 0, 0)
        self.current_editing_index = -1
        self._move_color_src = None
        self._swap_color_src = None
        self._move_palette_src = None
        self._move_palette_drag_item = None
        self._syncing_splitter = False

        self.setup_ui()
        self.setup_tilemap_interaction()
        self.highlight_selected_palette(0, 0)
      
        QTimer.singleShot(100, lambda: self.draw_selection_rectangle(0))
        QTimer.singleShot(100, self.connect_tab_signals)
        QTimer.singleShot(100, self.initialize_color_editor)
        QTimer.singleShot(0, self._init_grayscale_palette)

        self.update_status_bar(-1, -1)

    def _on_splitter_moved(self, pos, index):
        """Handle splitter movement and sync with tiles tab"""
        if self._syncing_splitter or not self.main_window or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        
        sizes = self.splitter.sizes()
        if len(sizes) != 2:
            return
            
        total_width = sum(sizes)
        min_left_width = self._get_min_left_container_width()
        max_tilemap_width = total_width - min_left_width
        
        tilemap_width = min(sizes[1], max_tilemap_width)
        left_width = total_width - tilemap_width
        
        if sizes[0] != left_width or sizes[1] != tilemap_width:
            self._syncing_splitter = True
            self.splitter.setSizes([left_width, tilemap_width])
            self._syncing_splitter = False
        
        self._sync_tilemap_width_to_tiles_tab(tilemap_width)
    
    def _get_min_left_container_width(self):
        """Get true minimum width for the palettes container based on widget hints"""
        if hasattr(self, 'splitter') and self.splitter.count() > 0:
            left_widget = self.splitter.widget(0)
            if left_widget is not None:
                hint = left_widget.minimumSizeHint()
                if hint.isValid() and hint.width() > 0:
                    return hint.width()
        return 250
    
    def _sync_tilemap_width_to_tiles_tab(self, tilemap_width):
        """Sync tilemap width to tiles tab"""
        if not self.main_window or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
            
        tiles_tab = self.main_window.edit_tiles_tab
        if not hasattr(tiles_tab, 'splitter') or getattr(tiles_tab, '_syncing_splitter', False):
            return
            
        tiles_sizes = tiles_tab.splitter.sizes()
        if len(tiles_sizes) != 2:
            return
            
        tiles_total_width = sum(tiles_sizes)
        tiles_min_left_width = tiles_tab._get_min_left_container_width()
        tiles_max_tilemap_width = tiles_total_width - tiles_min_left_width
        
        new_tiles_tilemap_width = min(tilemap_width, tiles_max_tilemap_width)
        new_tiles_left_width = tiles_total_width - new_tiles_tilemap_width
        
        tiles_tab._syncing_splitter = True
        tiles_tab.splitter.setSizes([new_tiles_left_width, new_tiles_tilemap_width])
        tiles_tab._syncing_splitter = False
    
    def sync_splitter_on_tab_change(self):
        """Sync THIS tab's splitter to match the tiles tab when Edit Palettes becomes active"""
        if not self.main_window or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
            
        tiles_tab = self.main_window.edit_tiles_tab
        if not hasattr(tiles_tab, 'splitter'):
            return
            
        tiles_sizes = tiles_tab.splitter.sizes()
        pal_sizes = self.splitter.sizes()
        
        if len(tiles_sizes) != 2 or len(pal_sizes) != 2:
            return
            
        tiles_left_width = tiles_sizes[0]
        tiles_tilemap_width = tiles_sizes[1]
        
        pal_total_width = sum(pal_sizes)
        pal_min_left_width = self._get_min_left_container_width()
        
        new_pal_left_width = max(tiles_left_width, pal_min_left_width)
        new_pal_tilemap_width = pal_total_width - new_pal_left_width
        
        if new_pal_tilemap_width < 0:
            new_pal_tilemap_width = 0
            new_pal_left_width = pal_total_width
        
        self._syncing_splitter = True
        self.splitter.setSizes([new_pal_left_width, new_pal_tilemap_width])
        self._syncing_splitter = False

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header = QLabel(self._tr("tab_header_edit_palettes"))
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)
        self._header_label = header

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)
        self.splitter = main_splitter

        palettes_container = self.create_palettes_container()
        main_splitter.addWidget(palettes_container)

        tilemap_container = self.create_tilemap_container()
        main_splitter.addWidget(tilemap_container)
        
        main_splitter.setSizes([500, 500])
        main_splitter.splitterMoved.connect(self._on_splitter_moved)
        self.layout.addWidget(main_splitter)

        self.colors = self.grid_view.colors
        self._pixmap_item = None

    def create_palettes_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        palettes_label = QLabel(self._tr("section_palettes"))
        palettes_label.setFont(QFont("Arial", 9, QFont.Bold))
        palettes_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(palettes_label)
        self._palettes_section_label = palettes_label

        layout.addWidget(self._create_palette_ops_toolbar())

        bordered_frame = QFrame()
        bordered_frame.setFrameShape(QFrame.StyledPanel)
        bordered_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }")
        bordered_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        inner_layout = QHBoxLayout(bordered_frame)
        inner_layout.setContentsMargins(4, 4, 4, 4)
        inner_layout.setSpacing(4)

        left_container = self.create_left_palette_container()
        inner_layout.addWidget(left_container)

        right_container = self.create_right_palette_container()
        inner_layout.addWidget(right_container)

        layout.addWidget(bordered_frame)

        return container

    def _create_palette_ops_toolbar(self):
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.StyledPanel)
        toolbar.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }")
        toolbar.setFixedHeight(28)

        outer = QVBoxLayout(toolbar)
        outer.setSpacing(1)
        outer.setContentsMargins(3, 3, 3, 3)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 0)
        row.setAlignment(Qt.AlignLeft)

        cb_style = "QCheckBox { font-size: 8pt; }"

        self._cb_move_color = QCheckBox(self._tr("palette_op_move_color"))
        self._cb_move_color.setStyleSheet(cb_style)
        self._cb_move_color.setFixedHeight(18)
        self._cb_move_color.setEnabled(False)

        self._cb_swap_color = QCheckBox(self._tr("palette_op_swap_color"))
        self._cb_swap_color.setStyleSheet(cb_style)
        self._cb_swap_color.setFixedHeight(18)
        self._cb_swap_color.setEnabled(False)

        self._cb_move_palette = QCheckBox(self._tr("palette_op_move_palette"))
        self._cb_move_palette.setStyleSheet(cb_style)
        self._cb_move_palette.setFixedHeight(18)
        self._cb_move_palette.setEnabled(False)

        def _on_move_toggled(checked):
            if checked:
                self._cb_swap_color.setChecked(False)
                self._cb_move_palette.setChecked(False)
            self._on_palette_op_mode_changed()

        def _on_swap_toggled(checked):
            if checked:
                self._cb_move_color.setChecked(False)
                self._cb_move_palette.setChecked(False)
            self._on_palette_op_mode_changed()

        def _on_move_palette_toggled(checked):
            if checked:
                self._cb_move_color.setChecked(False)
                self._cb_swap_color.setChecked(False)
            self._on_palette_op_mode_changed()

        self._cb_move_color.toggled.connect(_on_move_toggled)
        self._cb_swap_color.toggled.connect(_on_swap_toggled)
        self._cb_move_palette.toggled.connect(_on_move_palette_toggled)

        self._palette_op_btns = [self._cb_move_color, self._cb_swap_color, self._cb_move_palette]

        row.addWidget(self._cb_move_color)
        row.addWidget(self._cb_swap_color)
        row.addWidget(self._cb_move_palette)
        row.addStretch()
        outer.addLayout(row)
        return toolbar

    def _on_palette_op_mode_changed(self):
        if self._cb_move_color.isChecked():
            self.full_palette_view.setCursor(Qt.PointingHandCursor)
            self.full_palette_view.mousePressEvent   = self._move_color_press
            self.full_palette_view.mouseMoveEvent    = self._move_color_move
            self.full_palette_view.mouseReleaseEvent = self._move_color_release
            self._move_color_src = None
        elif self._cb_swap_color.isChecked():
            self.full_palette_view.setCursor(Qt.PointingHandCursor)
            self.full_palette_view.mousePressEvent   = self._swap_color_press
            self.full_palette_view.mouseMoveEvent    = self._swap_color_move
            self.full_palette_view.mouseReleaseEvent = self._swap_color_release
            self._swap_color_src = None
        elif self._cb_move_palette.isChecked():
            self.full_palette_view.setCursor(Qt.PointingHandCursor)
            self.full_palette_view.mousePressEvent   = self._move_palette_press
            self.full_palette_view.mouseMoveEvent    = self._move_palette_move
            self.full_palette_view.mouseReleaseEvent = self._move_palette_release
            self._move_palette_src = None
        else:
            self.full_palette_view.setCursor(Qt.ArrowCursor)
            self.full_palette_view.mousePressEvent   = lambda e: type(self.full_palette_view).mousePressEvent(self.full_palette_view, e)
            self.full_palette_view.mouseMoveEvent    = lambda e: type(self.full_palette_view).mouseMoveEvent(self.full_palette_view, e)
            self.full_palette_view.mouseReleaseEvent = lambda e: type(self.full_palette_view).mouseReleaseEvent(self.full_palette_view, e)

    def _palette_index_at(self, view_pos):
        scene_pos = self.full_palette_view.mapToScene(view_pos)
        TILE = 12
        col = int(scene_pos.x()) // TILE
        row = int(scene_pos.y()) // TILE
        if 0 <= col < 16 and 0 <= row < 16:
            return row * 16 + col
        return -1

    def _move_color_press(self, event):

        if event.button() == Qt.LeftButton:
            self._move_color_src = self._palette_index_at(event.pos())
        QGraphicsView.mousePressEvent(self.full_palette_view, event)

    def _move_color_move(self, event):

        QGraphicsView.mouseMoveEvent(self.full_palette_view, event)

    def _move_color_release(self, event):

        if event.button() == Qt.LeftButton and self._move_color_src is not None:
            dst = self._palette_index_at(event.pos())
            src = self._move_color_src
            self._move_color_src = None
            if dst >= 0 and src != dst:
                self._apply_move_color(src, dst)
        QGraphicsView.mouseReleaseEvent(self.full_palette_view, event)

    def _swap_color_press(self, event):

        if event.button() == Qt.LeftButton:
            self._swap_color_src = self._palette_index_at(event.pos())
        QGraphicsView.mousePressEvent(self.full_palette_view, event)

    def _swap_color_move(self, event):

        QGraphicsView.mouseMoveEvent(self.full_palette_view, event)

    def _swap_color_release(self, event):

        if event.button() == Qt.LeftButton and self._swap_color_src is not None:
            dst = self._palette_index_at(event.pos())
            src = self._swap_color_src
            self._swap_color_src = None
            bpp = getattr(self.main_window, 'current_bpp', 4) if self.main_window else 4
            if bpp == 4:
                slot_size = 16
                dst = (src // slot_size) * slot_size + (dst % slot_size)
            if dst >= 0 and src != dst:
                self._apply_swap_color(src, dst)
        QGraphicsView.mouseReleaseEvent(self.full_palette_view, event)

    def _apply_swap_color(self, src, dst):
        new_colors = list(self.palette_colors)
        new_colors[src], new_colors[dst] = new_colors[dst], new_colors[src]
        lut = list(range(256))
        lut[src] = dst
        lut[dst] = src
        self._apply_palette_op(new_colors, lut, f"Swap colors {src} <> {dst}",
                               cursor_index=src, remap_images=False)

    def _apply_move_color(self, src, dst):
        bpp = getattr(self.main_window, 'current_bpp', 4) if self.main_window else 4
        slot_size = 16 if bpp == 4 else 256
        slot = src // slot_size
        if bpp == 4:
            dst = slot * slot_size + (dst % slot_size)

        s0 = slot * slot_size
        local_src = src - s0
        local_dst = dst - s0

        slot_colors = list(self.palette_colors[s0 : s0 + slot_size])
        color = slot_colors.pop(local_src)
        slot_colors.insert(local_dst, color)
        new_colors = list(self.palette_colors)
        new_colors[s0 : s0 + slot_size] = slot_colors

        lut = list(range(256))
        if local_src < local_dst:
            lut[s0 + local_src] = s0 + local_dst
            for i in range(local_src + 1, local_dst + 1):
                lut[s0 + i] = s0 + i - 1
        else:
            lut[s0 + local_src] = s0 + local_dst
            for i in range(local_dst, local_src):
                lut[s0 + i] = s0 + i + 1

        self._apply_palette_op(new_colors, lut, f"Move color {src} -> {dst}", cursor_index=lut[src], remap_images=True)

    def _move_palette_press(self, event):

        if event.button() == Qt.LeftButton:
            idx = self._palette_index_at(event.pos())
            if idx >= 0:
                self._move_palette_src = idx // 16  # slot 0-15
                self._move_palette_drag_item = self._build_palette_drag_pixmap(self._move_palette_src)
                self._show_palette_drag(event.pos())
        QGraphicsView.mousePressEvent(self.full_palette_view, event)

    def _move_palette_move(self, event):

        if self._move_palette_src is not None and self._move_palette_drag_item is not None:
            self._show_palette_drag(event.pos())
        QGraphicsView.mouseMoveEvent(self.full_palette_view, event)

    def _move_palette_release(self, event):

        self._hide_palette_drag()
        if event.button() == Qt.LeftButton and self._move_palette_src is not None:
            idx = self._palette_index_at(event.pos())
            dst_slot = idx // 16 if idx >= 0 else -1
            src_slot = self._move_palette_src
            self._move_palette_src = None
            bpp = getattr(self.main_window, 'current_bpp', 4) if self.main_window else 4
            if bpp == 4 and dst_slot >= 0 and src_slot != dst_slot:
                src_colors = self.palette_colors[src_slot * 16 : src_slot * 16 + 16]
                if any(c != (0, 0, 0) for c in src_colors):
                    self._apply_move_palette(src_slot, dst_slot)
        QGraphicsView.mouseReleaseEvent(self.full_palette_view, event)

    def _build_palette_drag_pixmap(self, slot):
        """Build a QGraphicsPixmapItem (16x1 grid, 12px cells) for the 16 colors of a slot."""

        CELL = 12
        px = QPixmap(16 * CELL, CELL)
        px.fill(Qt.transparent)
        painter = QPainter(px)
        start = slot * 16
        for i in range(16):
            r, g, b = self.palette_colors[start + i]
            painter.fillRect(i * CELL, 0, CELL, CELL, QColor(r, g, b))
        painter.end()
        item = QGraphicsPixmapItem(px)
        return item

    def _show_palette_drag(self, view_pos):
        """Place/move the drag pixmap item in the scene under the cursor."""
        scene_pos = self.full_palette_view.mapToScene(view_pos)
        if self._move_palette_drag_item is None:
            return
        if self._move_palette_drag_item.scene() is None:
            self.full_palette_scene.addItem(self._move_palette_drag_item)
            self._move_palette_drag_item.setOpacity(0.75)
            self._move_palette_drag_item.setZValue(100)
        self._move_palette_drag_item.setPos(scene_pos.x() - 96, scene_pos.y() - 6)

    def _hide_palette_drag(self):
        """Remove the drag pixmap from the scene."""
        if self._move_palette_drag_item is not None:
            try:
                if self._move_palette_drag_item.scene():
                    self.full_palette_scene.removeItem(self._move_palette_drag_item)
            except RuntimeError:
                pass
            self._move_palette_drag_item = None

    def _apply_move_palette(self, src_slot, dst_slot):
        old_colors = list(self.palette_colors)
        new_colors = list(self.palette_colors)

        src_start = src_slot * 16
        dst_start = dst_slot * 16

        new_colors[dst_start:dst_start + 16] = old_colors[src_start:src_start + 16]
        new_colors[src_start:src_start + 16] = [(0, 0, 0)] * 16

        identity_lut = list(range(256))
        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='move_color',
                editor_type='palettes',
                data={
                    'old_colors':       old_colors,
                    'new_colors':       new_colors,
                    'lut':              identity_lut,
                    'inv_lut':          identity_lut,
                    'old_tiles_data':   None,
                    'new_tiles_data':   None,
                    'tiles_shape':      None,
                    'old_preview_data': None,
                    'new_preview_data': None,
                    'preview_shape':    None,
                },
                description=f"Move palette {src_slot} -> {dst_slot}"
            )

        self.palette_colors = new_colors
        for i, (r, g, b) in enumerate(new_colors):
            if i < len(self.palette_rects):
                self.palette_rects[i].setBrush(QBrush(QColor(r, g, b)))

        self.current_editing_index = dst_start
        r, g, b = new_colors[dst_start]
        self.color_editor.set_color(dst_start, r, g, b)
        self.draw_selection_rectangle(dst_start)

        self._save_output_palette()
        if self.main_window and hasattr(self.main_window, 'preview_tab'):
            self.main_window.preview_tab.palette_colors = self.palette_colors.copy()
            self.main_window.preview_tab.display_palette_colors(self.palette_colors)
        if self.main_window and hasattr(self.main_window, '_save_map_and_refresh'):
            self.main_window._save_map_and_refresh()

    def _apply_palette_op(self, new_colors, lut, description, cursor_index, remap_images=True):
        import numpy as np
        from PIL import Image as _Img

        old_colors = list(self.palette_colors)
        flat_new = [c for rgb in new_colors for c in rgb]
        while len(flat_new) < 768:
            flat_new.append(0)

        old_tiles_data = new_tiles_data = tiles_shape = None
        old_preview_data = new_preview_data = preview_shape = None

        if remap_images:
            lut_arr = np.array(lut, dtype=np.uint8)

            def _remap_image(path):
                if not os.path.exists(path):
                    return None, None, None
                with _Img.open(path) as f:
                    a = np.array(f).copy()
                remapped = lut_arr[a]
                out = _Img.fromarray(remapped, mode='P')
                out.putpalette(flat_new)
                out.save(path)
                return a.tobytes(), remapped.tobytes(), a.shape

            try:
                old_tiles_data, new_tiles_data, tiles_shape = _remap_image('output/tiles.png')
                if old_tiles_data and self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
                    et = self.main_window.edit_tiles_tab
                    with _Img.open('output/tiles.png') as f:
                        et.tileset_img = f.copy()
                        et.tileset_img_original = et.tileset_img
                    total = (et.tileset_img.width // 8) * (et.tileset_img.height // 8)
                    w = et.tiles_per_row if et.tiles_per_row > 0 else et.tileset_img.width // 8
                    et.render_tileset_with_padding(w, (total + w - 1) // w, total)
            except Exception as e:
                print(f"palette_op remap tiles error: {e}")

            try:
                old_preview_data, new_preview_data, preview_shape = _remap_image('temp/preview/preview.png')
            except Exception as e:
                print(f"palette_op remap preview error: {e}")
        else:
            def _update_palette_only(path):
                if not os.path.exists(path):
                    return None, None, None
                with _Img.open(path) as f:
                    img = f.copy()
                if img.mode != 'P':
                    return None, None, None
                old_data = np.array(img).tobytes()
                shape = np.array(img).shape
                img.putpalette(flat_new)
                img.save(path)
                return old_data, old_data, shape

            try:
                old_tiles_data, new_tiles_data, tiles_shape = _update_palette_only('output/tiles.png')
                if old_tiles_data and self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
                    et = self.main_window.edit_tiles_tab
                    with _Img.open('output/tiles.png') as f:
                        et.tileset_img = f.copy()
                        et.tileset_img_original = et.tileset_img
                    total = (et.tileset_img.width // 8) * (et.tileset_img.height // 8)
                    w = et.tiles_per_row if et.tiles_per_row > 0 else et.tileset_img.width // 8
                    et.render_tileset_with_padding(w, (total + w - 1) // w, total)
            except Exception as e:
                print(f"palette_op swap tiles error: {e}")

            try:
                old_preview_data, new_preview_data, preview_shape = _update_palette_only('temp/preview/preview.png')
            except Exception as e:
                print(f"palette_op swap preview error: {e}")

        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='move_color',
                editor_type='palettes',
                data={
                    'old_colors':       old_colors,
                    'new_colors':       new_colors,
                    'lut':              lut,
                    'inv_lut':          _invert_lut(lut),
                    'old_tiles_data':   old_tiles_data,
                    'new_tiles_data':   new_tiles_data,
                    'tiles_shape':      tiles_shape,
                    'old_preview_data': old_preview_data,
                    'new_preview_data': new_preview_data,
                    'preview_shape':    preview_shape,
                },
                description=description
            )

        self.palette_colors = new_colors
        for i, (r, g, b) in enumerate(new_colors):
            if i < len(self.palette_rects):
                self.palette_rects[i].setBrush(QBrush(QColor(r, g, b)))

        self.current_editing_index = cursor_index
        r, g, b = new_colors[cursor_index]
        self.color_editor.set_color(cursor_index, r, g, b)
        self.draw_selection_rectangle(cursor_index)

        self._save_and_update_all(skip_tiles=True)
        if self.main_window and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

    def create_left_palette_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.grid_view = PaletteGridView()
        self.grid_view.setMouseTracking(True)
        self.grid_view.mouseMoveEvent = self.on_palette_grid_hover
        self.grid_view.leaveEvent = self.on_palette_grid_leave
        self.grid_view.mousePressEvent = self.on_palette_grid_click
        self.grid_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: none; }")
        layout.addWidget(self.grid_view)
        
        return container

    def on_palette_grid_click(self, event):
        if event.button() != Qt.LeftButton:
            return
        super(QGraphicsView, self.grid_view).mousePressEvent(event)
        pos = self.grid_view.mapToScene(event.pos())
        if not (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
            return
        palette_x = max(0, min(int(pos.x()) // 8, 3))
        palette_y = max(0, min(int(pos.y()) // 8, 3))
        self.selected_palette_id = palette_y * 4 + palette_x
        self.highlight_selected_palette(palette_x, palette_y)
        self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], palette_id=self.selected_palette_id)

    def create_right_palette_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        self.full_palette_view = QGraphicsView()
        self.full_palette_scene = QGraphicsScene()
        self.full_palette_view.setScene(self.full_palette_scene)
        self.full_palette_view.setRenderHint(QPainter.Antialiasing, False)
        self.full_palette_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.full_palette_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: none; }")
        self.full_palette_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.full_palette_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.full_palette_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.full_palette_view.setFixedSize(192, 192)
        layout.addWidget(self.full_palette_view)
        
        editor_container = QWidget()
        editor_container.setFixedSize(195, 65)
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        self.color_editor = ColorEditor(self)
        editor_layout.addWidget(self.color_editor)
        self.color_editor.color_updated.connect(lambda index, r, g, b, record: self.update_selected_color(index, r, g, b, record))

        layout.addWidget(editor_container)
        
        return container

    def create_tilemap_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        tilemap_label = QLabel(self._tr("section_tilemap"))
        tilemap_label.setFont(QFont("Arial", 9, QFont.Bold))
        tilemap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tilemap_label)
        self._tilemap_section_label = tilemap_label

        tilemap_toolbar = self.create_tilemap_toolbar()
        layout.addWidget(tilemap_toolbar)

        self.edit_tilemap2_view = CustomGraphicsView()
        self.edit_tilemap2_scene = QGraphicsScene()
        self.edit_tilemap2_view.setScene(self.edit_tilemap2_scene)
        self.edit_tilemap2_view.setRenderHint(QPainter.Antialiasing, False)
        self.edit_tilemap2_view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.edit_tilemap2_view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        self.edit_tilemap2_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.edit_tilemap2_view.setMouseTracking(True)
        layout.addWidget(self.edit_tilemap2_view)
        self.tilemap_view  = self.edit_tilemap2_view
        self.tilemap_scene = self.edit_tilemap2_scene

        return container

    def create_tilemap_toolbar(self):
        return self.build_tilemap_toolbar()

    def initialize_color_editor(self):
        if (hasattr(self, 'palette_colors') and 
            len(self.palette_colors) > 0 and
            hasattr(self, 'color_editor')):
            
            r, g, b = self.palette_colors[0]
            self.color_editor.set_color(0, r, g, b)
            self.draw_selection_rectangle(0)
            
            self.current_editing_index = 0
            self.last_edited_index = -1
            self.last_edited_color = (r, g, b)

    def _init_grayscale_palette(self):
        from core.palette_utils import generate_grayscale_palette
        if any(c != (0, 0, 0) for c in self.palette_colors):
            return
        self.display_palette_colors(generate_grayscale_palette(), enable_editor=False)
        for btn in self._palette_op_btns:
            btn.setEnabled(False)

    def retranslate_ui(self):
        self._header_label.setText(self._tr("tab_header_edit_palettes"))
        self._palettes_section_label.setText(self._tr("section_palettes"))
        self._tilemap_section_label.setText(self._tr("section_tilemap"))
        self._cb_move_color.setText(self._tr("palette_op_move_color"))
        self._cb_swap_color.setText(self._tr("palette_op_swap_color"))
        self._cb_move_palette.setText(self._tr("palette_op_move_palette"))
        self.retranslate_tilemap_toolbar()

    def setup_tilemap_interaction(self):
        super().setup_tilemap_interaction()

    def on_tilemap_leave(self):
        super().on_tilemap_leave()

    def on_tilemap_hover(self, tile_x, tile_y):
        super().on_tilemap_hover(tile_x, tile_y)

    def on_tilemap_drawing(self, tile_x, tile_y):
        self.finalize_color_editing()
        if event.button() == Qt.LeftButton:
            pos = self.grid_view.mapToScene(event.pos())
            
            if not (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
                return
            
            palette_x = max(0, min(int(pos.x()) // 8, 3))
            palette_y = max(0, min(int(pos.y()) // 8, 3))
            self.selected_palette_id = palette_y * 4 + palette_x
            self.highlight_selected_palette(palette_x, palette_y)
            self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], palette_id=self.selected_palette_id)

    def on_palette_grid_hover(self, event):
        super(QGraphicsView, self.grid_view).mouseMoveEvent(event)
        
        pos = self.grid_view.mapToScene(event.pos())
        
        if (0 <= pos.x() < 32 and 0 <= pos.y() < 32):
            palette_x = max(0, min(int(pos.x()) // 8, 3))
            palette_y = max(0, min(int(pos.y()) // 8, 3))
            palette_id = palette_y * 4 + palette_x
            self.update_status_bar(-1, -1, palette_id=palette_id)
        else:
            self.update_status_bar(-1, -1, palette_id=self.selected_palette_id)

    def on_palette_grid_leave(self, event):
        QGraphicsView.leaveEvent(self.grid_view, event)
        
        if hasattr(self, 'last_hover_pos') and self.last_hover_pos != (-1, -1):
            self.update_status_bar(*self.last_hover_pos)
        else:
            self.update_status_bar(-1, -1, palette_id=self.selected_palette_id)

    def highlight_selected_palette(self, palette_x, palette_y):
        self.finalize_color_editing()
        self.grid_view.highlight_selected_palette(palette_x, palette_y)

    def on_tilemap_leave(self):
        self.main_window.hover_manager.hide_hover(self.edit_tilemap2_view)
        self.last_hover_pos = (-1, -1)
        self.update_status_bar(-1, -1)

    def on_tilemap_hover(self, tile_x, tile_y):
        scene_rect = self.edit_tilemap2_scene.sceneRect()
        max_tile_x = int(scene_rect.width()) // 8 - 1
        max_tile_y = int(scene_rect.height()) // 8 - 1
        
        if (0 <= tile_x <= max_tile_x and 0 <= tile_y <= max_tile_y):
            self.last_hover_pos = (tile_x, tile_y)
            self.main_window.hover_manager.update_hover(tile_x, tile_y, self.edit_tilemap2_view)
            self.update_status_bar(tile_x, tile_y)
        else:
            self.last_hover_pos = (-1, -1)
            self.main_window.hover_manager.hide_hover(self.edit_tilemap2_view)
            self.update_status_bar(-1, -1)

    def on_tilemap_drawing(self, tile_x, tile_y):
        self.finalize_color_editing()
        if self.selected_palette_id is None or not self.tilemap_data or self._palette_edit_disabled():
            return
        self.on_tilemap_hover(tile_x, tile_y)
        self.edit_palette_at(tile_x, tile_y)

    def on_tilemap_release(self):
        if not self.tilemap_data:
            return
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        if self.main_window:
            if hasattr(self.main_window, 'edit_tiles_tab'):
                self.main_window.edit_tiles_tab.tilemap_data = self.tilemap_data
            if hasattr(self.main_window, '_save_map_and_refresh'):
                self.main_window._save_map_and_refresh()

    def _is_rotation(self):
        return getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False

    def _is_8bpp(self):
        return getattr(self.main_window, 'current_bpp', 4) == 8 if self.main_window else False

    def _palette_edit_disabled(self):
        return self._is_rotation() or self._is_8bpp()

    def on_tilemap_right_click(self, tile_x, tile_y):
        self.finalize_color_editing()
        if not self.tilemap_data or self._palette_edit_disabled():
            return
        tile_index = self._tilemap_index(tile_x, tile_y)
        if 0 <= tile_index < len(self.tilemap_data) // 2:
            entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
            palette_id = (entry >> 12) & 0xF
            self.selected_palette_id = palette_id
            self.highlight_selected_palette(palette_id % 4, palette_id // 4)
        self.on_tilemap_hover(tile_x, tile_y)

    def focusOutEvent(self, event):
        self.finalize_color_editing()
        super().focusOutEvent(event)

    def connect_tab_signals(self):
        if self.main_window and hasattr(self.main_window, 'main_tabs'):
            self.main_window.main_tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        current_tab = self.main_window.main_tabs.widget(index)
        if current_tab != self:
            self.finalize_color_editing()

    def _apply_pal_replace(self):
        if not self.tilemap_data:
            return
        dst_id = self.selected_palette_id
        old_data = self.tilemap_data
        new_data = bytearray(old_data)
        affected = []

        if self._tilemap_sel_area is not None:
            x1, y1, x2, y2 = self._tilemap_sel_area
            for ty in range(y1, y2 + 1):
                for tx in range(x1, x2 + 1):
                    idx = self._tilemap_index(tx, ty)
                    if idx * 2 + 2 > len(new_data):
                        continue
                    entry = new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)
                    if (entry >> 12) & 0xF == dst_id:
                        continue
                    entry = (entry & 0x0FFF) | (dst_id << 12)
                    new_data[idx * 2]     = entry & 0xFF
                    new_data[idx * 2 + 1] = (entry >> 8) & 0xFF
                    affected.append((tx, ty))
            if not affected:
                return
            src_desc = f"area ({x1},{y1})-({x2},{y2})"
        else:
            if not self._pal_sel_items:
                return
            src_id = self._pal_sel_palette_id
            if src_id == dst_id:
                return
            for item in self._pal_sel_items:
                try:
                    r = item.rect()
                    tx = int(r.x()) // 8
                    ty = int(r.y()) // 8
                except RuntimeError:
                    continue
                idx = self._tilemap_index(tx, ty)
                if idx * 2 + 2 > len(new_data):
                    continue
                entry = new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)
                entry = (entry & 0x0FFF) | (dst_id << 12)
                new_data[idx * 2]     = entry & 0xFF
                new_data[idx * 2 + 1] = (entry >> 8) & 0xFF
                affected.append((tx, ty))
            src_desc = f"palette {src_id}"

        self._commit_tilemap_op(bytes(new_data), old_data, affected,
                                'pal_replace',
                                f"Replace palette {src_desc} -> {dst_id}")

    def _apply_pal_swap(self):
        if not self.tilemap_data:
            return
        dst_id = self.selected_palette_id

        if self._tilemap_sel_area is not None:
            x1, y1, x2, y2 = self._tilemap_sel_area
            src_id = None
            for ty in range(y1, y2 + 1):
                for tx in range(x1, x2 + 1):
                    idx = self._tilemap_index(tx, ty)
                    if idx * 2 + 2 > len(self.tilemap_data):
                        continue
                    entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
                    src_id = (entry >> 12) & 0xF
                    break
                if src_id is not None:
                    break
            if src_id is None or src_id == dst_id:
                return
        else:
            if not self._pal_sel_items:
                return
            src_id = self._pal_sel_palette_id
            if src_id == dst_id:
                return

        old_data = self.tilemap_data
        new_data = bytearray(old_data)
        affected = []
        for ty in range(self.tilemap_height):
            for tx in range(self.tilemap_width):
                idx = self._tilemap_index(tx, ty)
                if idx * 2 + 2 > len(new_data):
                    continue
                entry = new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)
                pal = (entry >> 12) & 0xF
                if pal == src_id:
                    entry = (entry & 0x0FFF) | (dst_id << 12)
                elif pal == dst_id:
                    entry = (entry & 0x0FFF) | (src_id << 12)
                else:
                    continue
                new_data[idx * 2]     = entry & 0xFF
                new_data[idx * 2 + 1] = (entry >> 8) & 0xFF
                affected.append((tx, ty))
        self._commit_tilemap_op(bytes(new_data), old_data, affected,
                                'pal_swap',
                                f"Swap palettes {src_id} <-> {dst_id}")

    def _commit_tilemap_op(self, new_data, old_data, affected_tiles, state_type, description):
        import os
        self.tilemap_data = new_data
        if self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
            self.main_window.edit_tiles_tab.tilemap_data = new_data
        for tx, ty in affected_tiles:
            idx = self._tilemap_index(tx, ty)
            entry = new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)
            self.update_palette_overlay_for_tile(tx, ty, (entry >> 12) & 0xF)
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)
        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type=state_type,
                editor_type='palettes',
                data={'old_data': old_data, 'new_data': new_data,
                      'w': self.tilemap_width, 'h': self.tilemap_height},
                description=description
            )
        if self.main_window and hasattr(self.main_window, '_save_map_and_refresh'):
            self.main_window._save_map_and_refresh()
        self._clear_pal_selection()
        self._clear_tilemap_area_selection()

    def _tilemap_index(self, tile_x, tile_y):
        w = self.tilemap_width
        if w <= 32:
            return tile_y * w + tile_x
        block_x = tile_x // 32
        block_y = tile_y // 32
        blocks_x = w // 32
        local_x = tile_x % 32
        local_y = tile_y % 32
        block_index = block_y * blocks_x + block_x
        return block_index * 1024 + local_y * 32 + local_x

    def edit_palette_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return

        tile_index = self._tilemap_index(tile_x, tile_y)
        if tile_index >= len(self.tilemap_data) // 2:
            return

        current_entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        old_palette_id = (current_entry >> 12) & 0xF
        old_state = {
            'tile_x': tile_x,
            'tile_y': tile_y,
            'old_palette_id': old_palette_id,
            'new_palette_id': self.selected_palette_id,
            'tile_id': current_entry & 0x3FF,
            'h_flip': bool(current_entry & (1 << 10)),
            'v_flip': bool(current_entry & (1 << 11))
        }

        if old_palette_id == self.selected_palette_id:
            return

        tile_id = current_entry & 0x3FF
        h_flip = bool(current_entry & (1 << 10))
        v_flip = bool(current_entry & (1 << 11))
        
        new_entry = tile_id
        if h_flip:
            new_entry |= (1 << 10)
        if v_flip:
            new_entry |= (1 << 11)
        new_entry |= (self.selected_palette_id << 12)

        tilemap_data = bytearray(self.tilemap_data)
        tilemap_data[tile_index * 2] = new_entry & 0xFF
        tilemap_data[tile_index * 2 + 1] = (new_entry >> 8) & 0xFF
        self.tilemap_data = bytes(tilemap_data)

        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='palette_change',
                editor_type='palettes',
                data=old_state,
                description=f"Palette changed at ({tile_x}, {tile_y})"
            )

        self.update_palette_overlay_for_tile(tile_x, tile_y, self.selected_palette_id)
        self._repaint_tile_in_scene(tile_x, tile_y, self.selected_palette_id)

        if self.main_window and hasattr(self.main_window, 'edit_tiles_tab'):
            self.main_window.edit_tiles_tab.tilemap_data = self.tilemap_data

    def _repaint_tile_in_scene(self, tile_x, tile_y, palette_id):
        if not self._pixmap_item:
            return
        et = getattr(self.main_window, 'edit_tiles_tab', None)
        if not et or not et.tileset_img or not et.tilemap_data:
            return

        tile_index = self._tilemap_index(tile_x, tile_y)
        if tile_index >= len(et.tilemap_data) // 2:
            return

        entry = et.tilemap_data[tile_index * 2] | (et.tilemap_data[tile_index * 2 + 1] << 8)
        tile_id  = entry & 0x3FF
        h_flip   = bool(entry & (1 << 10))
        v_flip   = bool(entry & (1 << 11))

        import numpy as np
        ts = et.tileset_img
        tx = (tile_id % et.tiles_per_row) * 8
        ty = (tile_id // et.tiles_per_row) * 8
        if tx + 8 > ts.width or ty + 8 > ts.height:
            return

        tile_arr = np.array(ts)[ty:ty+8, tx:tx+8].copy()
        if h_flip:
            tile_arr = np.fliplr(tile_arr)
        if v_flip:
            tile_arr = np.flipud(tile_arr)

        slot_start = palette_id * 16
        slot_colors = self.palette_colors[slot_start:slot_start + 16]

        lut = np.array(slot_colors, dtype=np.uint8)
        indices = (tile_arr % 16).astype(np.uint8)
        rgb = lut[indices]

        rgb_data = rgb.tobytes()
        tile_img = QImage(rgb_data, 8, 8, 8 * 3, QImage.Format_RGB888)
        tile_pixmap = QPixmap.fromImage(tile_img.copy())

        scene_pixmap = self._pixmap_item.pixmap()
        painter = QPainter(scene_pixmap)
        painter.drawPixmap(tile_x * 8, tile_y * 8, tile_pixmap)
        painter.end()
        self._pixmap_item.setPixmap(scene_pixmap)

    def set_overlay_text_color(self, r, g, b):
        self._overlay_text_color = QColor(r, g, b)
        for rect_item, text_item in self.overlay_items.values():
            text_item.setDefaultTextColor(self._overlay_text_color)

    def set_overlay_alpha(self, alpha):
        self._overlay_alpha = alpha / 255.0
        for rect_item, _ in self.overlay_items.values():
            rect_item.setOpacity(self._overlay_alpha)

    def update_palette_overlay_for_tile(self, tile_x, tile_y, palette_id):
        x = tile_x * 8
        y = tile_y * 8
        color = self.colors[palette_id]
        tile_key = (tile_x, tile_y)

        if tile_key in self.overlay_items:
            rect_item, text_item = self.overlay_items[tile_key]
            rect_item.setBrush(QBrush(color))
            text_item.setPlainText(f"{palette_id:X}")
            rect = text_item.boundingRect()
            text_item.setPos(x + (8 - rect.width()) / 2, y + (8 - rect.height()) * 0.5)
            return

        rect_item = self.edit_tilemap2_scene.addRect(x, y, 8, 8, QPen(Qt.NoPen), QBrush(color))
        rect_item.setZValue(1)
        rect_item.setOpacity(self._overlay_alpha)

        font = QFont("Arial", 5, QFont.Normal)
        text_item = self.edit_tilemap2_scene.addText(f"{palette_id:X}")
        text_item.setFont(font)
        text_item.setDefaultTextColor(self._overlay_text_color)
        rect = text_item.boundingRect()
        text_item.setPos(x + (8 - rect.width()) / 2, y + (8 - rect.height()) * 0.5)
        text_item.setZValue(2)

        self.overlay_items[tile_key] = [rect_item, text_item]

    def display_tilemap_replica(self, source_scene):
        self.edit_tilemap2_scene.clear()
        self.overlay_items.clear()
        self._tilemap_items = {}

        pixmap_item = None
        for item in source_scene.items():
            if hasattr(item, 'pixmap'):
                pixmap_item = item
                break

        if pixmap_item:
            pixmap = pixmap_item.pixmap()
            self._pixmap_item = self.edit_tilemap2_scene.addPixmap(pixmap)
            self.edit_tilemap2_scene.setSceneRect(pixmap.rect())

            if hasattr(self.main_window, 'edit_tiles_tab'):
                tiles_tab = self.main_window.edit_tiles_tab
                tiles_tab.edit_tilemap_scene.clear()
                tiles_tab.edit_tilemap_scene.addPixmap(pixmap)
                tiles_tab.edit_tilemap_scene.setSceneRect(pixmap.rect())

                if self.main_window and hasattr(self.main_window, 'grid_manager'):
                    if self.main_window.grid_manager.is_grid_visible():
                        self.main_window.grid_manager.update_grid_for_view("tilemap_edit")

        if not self._palette_edit_disabled() and hasattr(self, 'tilemap_data') and self.tilemap_data:
            scene_rect = self.edit_tilemap2_scene.sceneRect()
            w = int(scene_rect.width()) // 8
            h = int(scene_rect.height()) // 8
            if w > 0 and h > 0:
                self.tilemap_width = w
                self.tilemap_height = h
                for y in range(h):
                    for x in range(w):
                        idx = self._tilemap_index(x, y)
                        if idx >= len(self.tilemap_data) // 2:
                            continue
                        entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
                        palette_id = (entry >> 12) & 0xF
                        self.update_palette_overlay_for_tile(x, y, palette_id)

        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")

    def toggle_tilemap_controls_enabled(self, enabled):
        self._set_tilemap_controls_enabled(enabled)

    def update_palette_overlay(self, source_scene, tilemap_data, tile_width, tile_height):
        if not tilemap_data:
            return

        self.tilemap_data = tilemap_data
        self.tilemap_width = tile_width
        self.tilemap_height = tile_height
        self.overlay_items.clear()
        self.tilemap_width_spin.setValue(tile_width)
        self.tilemap_height_spin.setValue(tile_height)
        self.enable_tilemap_controls()

        if not source_scene.items():
            return

        self.overlay_items.clear()
        self.edit_tilemap2_scene.clear()
        self._tilemap_items = {}

        pixmap_item = None
        for item in source_scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                pixmap_item = item
                break

        if pixmap_item:
            pixmap = pixmap_item.pixmap()
            self._pixmap_item = self.edit_tilemap2_scene.addPixmap(pixmap)
            self.edit_tilemap2_scene.setSceneRect(pixmap.rect())
            self._pixmap_item.setZValue(0)

        if self._is_rotation():
            if self.main_window and hasattr(self.main_window, 'grid_manager'):
                if self.main_window.grid_manager.is_grid_visible():
                    self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")
            return

        for i in range(tile_height):
            for j in range(tile_width):
                idx = self._tilemap_index(j, i)
                if idx >= len(tilemap_data) // 2:
                    continue
                entry = tilemap_data[idx * 2] | (tilemap_data[idx * 2 + 1] << 8)
                palette_id = (entry >> 12) & 0xF
                self.update_palette_overlay_for_tile(j, i, palette_id)

        self.enable_tilemap_controls()
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_palettes")

    def update_single_tile_replica(self, tile_x, tile_y):
        if not self._pixmap_item:
            return
        et = getattr(self.main_window, 'edit_tiles_tab', None)
        if not et or not et.tileset_img or not et.tilemap_data:
            return

        tile_index = self._tilemap_index(tile_x, tile_y)
        if tile_index >= len(et.tilemap_data) // 2:
            return

        entry = et.tilemap_data[tile_index * 2] | (et.tilemap_data[tile_index * 2 + 1] << 8)
        palette_id = (entry >> 12) & 0xF

        self._repaint_tile_in_scene(tile_x, tile_y, palette_id)
        self.update_palette_overlay_for_tile(tile_x, tile_y, palette_id)

    def apply_zoom(self, factor):
        self.grid_view.set_zoom_factor(factor)
        self.edit_tilemap2_view.resetTransform()
        self.edit_tilemap2_view.scale(factor, factor)

    def display_palette_colors(self, colors, enable_editor=True):

        self.palette_colors = [(r, g, b) for r, g, b in colors]
        self.draw_full_palette(self.palette_colors)
        
        self.current_editing_index = 0
        if len(self.palette_colors) > 0:
            r, g, b = self.palette_colors[0]
            self.color_editor.set_color(0, r, g, b)
            self.draw_selection_rectangle(0)
            self.color_editor.toggle_controls_enabled(enable_editor)

        if hasattr(self, '_palette_op_btns'):
            for btn in self._palette_op_btns:
                btn.setEnabled(True)
            bpp = getattr(self.main_window, 'current_bpp', 4) if self.main_window else 4
            if bpp != 4:
                self._cb_move_palette.setEnabled(False)
                self._cb_move_palette.setChecked(False)
            if not enable_editor:
                for btn in self._palette_op_btns:
                    btn.setChecked(False)
                self._on_palette_op_mode_changed()

        self.selected_palette_id = 0
        self.highlight_selected_palette(0, 0)

        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("palettes")

    def draw_full_palette(self, colors):
        self.full_palette_scene.clear()
        tile_size = 12
        self.palette_rects = []
        self.selection_rect = None

        self.full_palette_scene.setSceneRect(0, 0, 16 * tile_size, 16 * tile_size)
        self.full_palette_view.resetTransform()
        
        for i, (r, g, b) in enumerate(colors):
            if i >= 256:
                break
                
            row = i // 16
            col = i % 16
            
            rect = QGraphicsRectItem(col * tile_size, row * tile_size, tile_size, tile_size)
            rect.setPen(QPen(Qt.gray, 0.5))
            rect.setBrush(QBrush(QColor(r, g, b)))
            
            rect.setAcceptHoverEvents(True)
            rect.setAcceptedMouseButtons(Qt.LeftButton)
            
            def make_handler(idx, red, green, blue):
                def handler(event):
                    self.on_palette_color_clicked(idx, red, green, blue)
                    if idx < len(self.palette_rects):
                        QGraphicsRectItem.mousePressEvent(self.palette_rects[idx], event)
                    event.accept()
                return handler
            rect.mousePressEvent = make_handler(i, r, g, b)
            
            self.full_palette_scene.addItem(rect)
            self.palette_rects.append(rect)
            
            def make_click_handler(idx, red, green, blue):
                def handler(event):
                    self.on_palette_color_clicked(idx, red, green, blue)
                return handler
            
            rect.mousePressEvent = make_click_handler(i, r, g, b)

    def on_palette_color_clicked(self, index, r, g, b):
        self.finalize_color_editing()
        
        current_r, current_g, current_b = self.palette_colors[index]
        
        self.current_editing_index = index
        self.color_editor.set_color(index, current_r, current_g, current_b)
        self.draw_selection_rectangle(index)

    def _regenerate_preview(self):
        if not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        tiles_tab = self.main_window.edit_tiles_tab
        if not getattr(tiles_tab, 'tileset_img', None) or not getattr(tiles_tab, 'tilemap_data', None):
            return
        try:
            if hasattr(self.main_window, 'config_manager') and tiles_tab.tilemap_width > 0:
                self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(tiles_tab.tilemap_width))
                self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(tiles_tab.tilemap_height))

            preview_path = "temp/preview/preview.png"
            if os.path.exists(preview_path):
                from PIL import Image as PilImage
                with PilImage.open(preview_path) as f:
                    preview_img = f.copy()
                if preview_img.mode == 'P':
                    flat = []
                    for r, g, b in self.palette_colors:
                        flat.extend([int(r), int(g), int(b)])
                    while len(flat) < 768:
                        flat.append(0)
                    preview_img.putpalette(flat)
                    preview_img.save(preview_path)
                    if hasattr(self.main_window, 'refresh_preview_display'):
                        self.main_window.refresh_preview_display()
                    return

            from core.image_utils import create_gbagfx_preview
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files',      False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
            result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
            if result and hasattr(self.main_window, 'refresh_preview_display'):
                self.main_window.refresh_preview_display()
        except Exception as e:
            print(self._tr("error_regenerating_preview", e=e))
    
    def _update_all_tiles(self):
        if not self.tilemap_data or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        
        tiles_tab = self.main_window.edit_tiles_tab
        
        for y in range(self.tilemap_height):
            for x in range(self.tilemap_width):
                tile_idx = y * self.tilemap_width + x
                if tile_idx >= len(self.tilemap_data) // 2:
                    continue
                
                tiles_tab.update_single_tile_visual(x, y)
                self.update_single_tile_replica(x, y)

    def _save_output_palette(self):
        import os
        
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        if self.main_window.current_bpp == 4:
            self._save_output_palette_4bpp(output_dir)
        else:
            self._save_output_palette_8bpp(output_dir)

    def _reload_tileset(self):
        if not self.main_window or not hasattr(self.main_window, 'edit_tiles_tab'):
            return
        
        tiles_tab = self.main_window.edit_tiles_tab
        
        if hasattr(tiles_tab, 'tileset_img') and tiles_tab.tileset_img:
            tiles_path = "output/tiles.png"
            if os.path.exists(tiles_path):
                try:
                    from PIL import Image as PilImage
                    with PilImage.open(tiles_path) as f:
                        new_tileset_img = f.copy()
                    tiles_tab.display_tileset(new_tileset_img)
                    
                except Exception as e:
                     print(self._tr("error_reloading_tileset", e=e))

    def _save_output_palette_4bpp(self, output_dir):
            import os

            for slot_idx in range(16):
                start_idx = slot_idx * 16
                end_idx = start_idx + 16
                
                slot_colors = self.palette_colors[start_idx:end_idx]
                
                is_used = any(color != (0, 0, 0) for color in slot_colors)
                
                filename = f"palette_{slot_idx:02d}.pal"
                filepath = os.path.join(output_dir, filename)
                
                if is_used:
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write("JASC-PAL\n0100\n16\n")
                        for r, g, b in slot_colors:
                            f.write(f"{int(r)} {int(g)} {int(b)}\n")
                else:
                    if os.path.exists(filepath):
                        os.remove(filepath)
    
    def _save_output_palette_8bpp(self, output_dir):
        start_idx = 0
        for i in range(1, len(self.palette_colors)):
            if self.palette_colors[i] != (0, 0, 0):
                start_idx = i
                break

        last_idx = start_idx
        for i in range(start_idx, len(self.palette_colors)):
            if self.palette_colors[i] != (0, 0, 0):
                last_idx = i

        colors_to_save = self.palette_colors[start_idx:last_idx + 1]

        for f in os.listdir(output_dir):
            if f.startswith("palette_") and f.endswith(".pal"):
                os.remove(os.path.join(output_dir, f))

        filename = f"palette_{start_idx:03d}.pal"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write("JASC-PAL\n0100\n")
            f.write(f"{len(colors_to_save)}\n")
            for r, g, b in colors_to_save:
                f.write(f"{r} {g} {b}\n")

    def _save_and_update_all(self, skip_tiles=False):       
            preview_palette_path = "temp/preview/palette.pal"
            os.makedirs(os.path.dirname(preview_palette_path), exist_ok=True)
            
            try:
                with open(preview_palette_path, 'w', encoding='utf-8') as f:
                    f.write("JASC-PAL\n0100\n256\n")
                    for r, g, b in self.palette_colors:
                        f.write(f"{r} {g} {b}\n")
            except Exception as e:
                 print(self._tr("error_saving_preview_palette", e=e))
            
            self._save_output_palette()
            if not skip_tiles:
                self._update_output_tiles()
            
            if (self.main_window and hasattr(self.main_window, 'preview_tab')):
                self.main_window.preview_tab.palette_colors = self.palette_colors.copy()
                self.main_window.preview_tab.display_palette_colors(self.palette_colors)
            
            self._regenerate_preview()
    
    def _update_output_tiles(self):
        from PIL import Image

        mw = self.main_window
        tiles_path = "output/tiles.png"
        if not os.path.exists(tiles_path):
            return

        try:
            with Image.open(tiles_path) as f:
                tiles_img = f.copy()
            if tiles_img.mode != 'P':
                return

            is_8bpp = getattr(mw, 'current_bpp', 4) == 8
            if is_8bpp:
                src_colors = self.palette_colors
            else:
                selected_str = mw.config_manager.get('CONVERSION', 'selected_palettes', '0')
                selected_slots = [s.strip() for s in selected_str.split(',') if s.strip()]
                if len(selected_slots) > 1:
                    return
                slot = int(selected_slots[0]) if selected_slots else 0
                src_colors = self.palette_colors[slot * 16 : slot * 16 + 16]
                src_colors = list(src_colors) + [(0, 0, 0)] * (256 - len(src_colors))

            flat_palette = []
            for r, g, b in src_colors:
                flat_palette.extend([int(r), int(g), int(b)])
            while len(flat_palette) < 768:
                flat_palette.extend([0, 0, 0])

            tiles_img.putpalette(flat_palette[:768])
            tiles_img.save(tiles_path)

            if hasattr(mw, 'edit_tiles_tab'):
                with Image.open(tiles_path) as f:
                    updated = f.copy()
                et = mw.edit_tiles_tab
                et.tileset_img = updated
                et.tileset_img_original = updated
                total_tiles = (updated.width // 8) * (updated.height // 8)
                w = et.tiles_per_row if et.tiles_per_row > 0 else updated.width // 8
                h = (total_tiles + w - 1) // w
                et.render_tileset_with_padding(w, h, total_tiles)

        except Exception as e:
            print(self._tr("error_updating_output_tiles", e=e))
        
    def finalize_color_editing(self):
        if (self.color_editor.has_changes() and 
            self.current_editing_index >= 0 and
            self.current_editing_index < len(self.palette_colors)):
            
            current_color = self.color_editor.get_current_color()
            original_color = self.color_editor.original_color
            
            if self.main_window and hasattr(self.main_window, 'history_manager'):
                self.main_window.history_manager.record_state(
                    state_type='color_edit',
                    editor_type='palettes',
                    data={
                        'index': self.current_editing_index,
                        'old_color': original_color,
                        'new_color': current_color
                    },
                    description=f"Color {self.current_editing_index} edited: RGB{original_color} → RGB{current_color}"
                )
            
            self.color_editor.original_color = current_color
            self.palette_colors[self.current_editing_index] = current_color
            
            rect = self.palette_rects[self.current_editing_index]
            rect.setBrush(QBrush(QColor(*current_color)))
            
            self._save_and_update_all()
            
    def draw_selection_rectangle(self, index):
        if self.selection_rect:
            self.full_palette_scene.removeItem(self.selection_rect)
        
        if index < 0 or index >= len(self.palette_rects):
            return
            
        rect = self.palette_rects[index]
        
        self.selection_rect = self.full_palette_scene.addRect(
            rect.rect().x(),
            rect.rect().y(),
            rect.rect().width(),
            rect.rect().height(),
            QPen(QColor(255, 255, 0), 1),
            Qt.NoBrush
        )
        self.selection_rect.setZValue(1)

    def update_selected_color(self, index, r, g, b, record_history=False):
        if index < 0 or index >= len(self.palette_rects):
            return
        
        rect = self.palette_rects[index]
        rect.setBrush(QBrush(QColor(r, g, b)))
        
        self.palette_colors[index] = (r, g, b)
        
        if (self.main_window and hasattr(self.main_window, 'preview_tab')):
            if hasattr(self.main_window.preview_tab, 'palette_colors'):
                self.main_window.preview_tab.palette_colors[index] = (r, g, b)
            
            self.main_window.preview_tab.display_palette_colors(self.main_window.preview_tab.palette_colors)

    def apply_color_change(self, index, r, g, b):
        if index < 0 or index >= len(self.palette_rects):
            return
        
        rect = self.palette_rects[index]
        rect.setBrush(QBrush(QColor(r, g, b)))
        
        self.palette_colors[index] = (r, g, b)
        
        if index == self.current_editing_index:
            self.color_editor.set_color(index, r, g, b)
        
        self._save_and_update_all()

    def update_status_bar(self, tile_x, tile_y, tile_id=None, palette_id=None, flip_state=None):
        update_status_bar_shared(
            main_window=self.main_window,
            selection_type=self._tr("type_palette"),
            selection_id=self.selected_palette_id,
            tile_x=tile_x,
            tile_y=tile_y,
            tilemap_data=self.tilemap_data if hasattr(self, 'tilemap_data') else None,
            tilemap_width=self.tilemap_width if hasattr(self, 'tilemap_width') else 0,
            tilemap_height=self.tilemap_height if hasattr(self, 'tilemap_height') else 0,
            tile_id=tile_id,
            palette_id=palette_id,
            flip_state=flip_state
        )

# ui/edit_tiles_tab.py
import os

from PIL import Image as PilImage
from core.final_assets import revert_gba_tilemap_reorganization
from core.image_utils import create_gbagfx_preview
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared, pil_to_qimage
from ui.shared_utils import CustomGraphicsView, update_status_bar_shared
from ui.tilemap_utils import TilemapUtils
from ui.qt_compat import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QGraphicsPixmapItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QHBoxLayout,
    QSpinBox,
    QPushButton,
    QCheckBox,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QFont,
    QPainter,
    QPixmap,
    QPen,
    QColor,
    Qt
)

EMPTY_TILE_ENTRY = b'\x00\x00'

class EditTilesTab(TilemapUtils, QWidget):
    @property
    def _tr(self):
        """Get translator from main_window if available, otherwise use module-level fallback."""
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'translator'):
            return self.main_window.translator.tr
        return lambda key, **kw: key

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.selected_tile_id = 0
        self.last_tile_pos = (-1, -1)
        self.last_hover_pos = (-1, -1)
        self.tileset_img = None
        self.tiles_per_row = 0
        self.tilemap_width = 0
        self.tilemap_height = 0
        self.tilemap_data = None
        self.selected_tile_pos = (-1, -1)
        self._syncing_splitter = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._header_label = self.create_header(self._tr("tab_header_edit_tiles"))
        self.layout.addWidget(self._header_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(6)
        self.splitter = splitter

        tileset_container = self.create_section(self._tr("section_tileset"))
        self._tileset_section_label = tileset_container.layout().itemAt(0).widget()
        self.setup_tileset_controls(tileset_container)
        self.edit_tileset_view = QGraphicsView()
        self.edit_tileset_scene = QGraphicsScene()
        self.edit_tileset_view.setScene(self.edit_tileset_scene)
        self.setup_view(self.edit_tileset_view)
        tileset_container.layout().addWidget(self.edit_tileset_view)
        
        splitter.addWidget(tileset_container)

        tilemap_container = self.create_section(self._tr("section_tilemap"))
        self._tilemap_section_label = tilemap_container.layout().itemAt(0).widget()
        self.setup_tilemap_controls(tilemap_container)
        self.edit_tilemap_view = CustomGraphicsView()
        self.edit_tilemap_scene = QGraphicsScene()
        self.edit_tilemap_view.setScene(self.edit_tilemap_scene)
        self.setup_view(self.edit_tilemap_view)
        tilemap_container.layout().addWidget(self.edit_tilemap_view)
        self.tilemap_view  = self.edit_tilemap_view
        self.tilemap_scene = self.edit_tilemap_scene
        splitter.addWidget(tilemap_container)

        splitter.setSizes([500, 500])
        splitter.splitterMoved.connect(self._on_splitter_moved)
        self.layout.addWidget(splitter)

        self.edit_tileset_view.setMouseTracking(True)
        self.edit_tileset_view.mouseMoveEvent = self.on_tileset_hover
        self.edit_tileset_view.leaveEvent = self.on_tileset_leave
        self.edit_tileset_view.mousePressEvent = self.on_tileset_click

        self.setup_tileset_interaction()
        self.setup_tilemap_interaction()
        self.last_scene_pos = None
        
        self.update_status_bar(-1, -1)

    def _on_splitter_moved(self, pos, index):
        """Handle splitter movement and sync with palettes tab"""
        if self._syncing_splitter or not self.main_window or not hasattr(self.main_window, 'edit_palettes_tab'):
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
        
        self._sync_tilemap_width_to_palettes_tab(tilemap_width)
    
    def _get_min_left_container_width(self):
        """Get true minimum width for the tileset container based on widget hints"""
        if hasattr(self, 'splitter') and self.splitter.count() > 0:
            left_widget = self.splitter.widget(0)
            if left_widget is not None:
                hint = left_widget.minimumSizeHint()
                if hint.isValid() and hint.width() > 0:
                    return hint.width()
        return 200
    
    def _sync_tilemap_width_to_palettes_tab(self, tilemap_width):
        """Sync tilemap width to palettes tab"""
        if not self.main_window or not hasattr(self.main_window, 'edit_palettes_tab'):
            return
            
        palettes_tab = self.main_window.edit_palettes_tab
        if not hasattr(palettes_tab, 'splitter') or getattr(palettes_tab, '_syncing_splitter', False):
            return
            
        pal_sizes = palettes_tab.splitter.sizes()
        if len(pal_sizes) != 2:
            return
            
        pal_total_width = sum(pal_sizes)
        pal_min_left_width = palettes_tab._get_min_left_container_width()
        pal_max_tilemap_width = pal_total_width - pal_min_left_width
        
        new_pal_tilemap_width = min(tilemap_width, pal_max_tilemap_width)
        new_pal_left_width = pal_total_width - new_pal_tilemap_width
        
        palettes_tab._syncing_splitter = True
        palettes_tab.splitter.setSizes([new_pal_left_width, new_pal_tilemap_width])
        palettes_tab._syncing_splitter = False
    
    def sync_splitter_on_tab_change(self):
        """Sync THIS tab's splitter to match the palettes tab when Edit Tiles becomes active"""
        if not self.main_window or not hasattr(self.main_window, 'edit_palettes_tab'):
            return
            
        palettes_tab = self.main_window.edit_palettes_tab
        if not hasattr(palettes_tab, 'splitter'):
            return
            
        pal_sizes = palettes_tab.splitter.sizes()
        tiles_sizes = self.splitter.sizes()
        
        if len(pal_sizes) != 2 or len(tiles_sizes) != 2:
            return
            
        pal_left_width = pal_sizes[0]
        pal_tilemap_width = pal_sizes[1]
        
        tiles_total_width = sum(tiles_sizes)
        tiles_min_left_width = self._get_min_left_container_width()
        
        new_tiles_left_width = max(pal_left_width, tiles_min_left_width)
        new_tiles_tilemap_width = tiles_total_width - new_tiles_left_width
        
        if new_tiles_tilemap_width < 0:
            new_tiles_tilemap_width = 0
            new_tiles_left_width = tiles_total_width
        
        self._syncing_splitter = True
        self.splitter.setSizes([new_tiles_left_width, new_tiles_tilemap_width])
        self._syncing_splitter = False

    def setup_tileset_controls(self, container):
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }")
        controls_frame.setFixedHeight(28)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(1)
        controls_layout.setContentsMargins(3, 3, 3, 3)
        controls_main_layout = QHBoxLayout()
        controls_main_layout.setSpacing(3)
        controls_main_layout.setContentsMargins(0, 0, 0, 0)
        controls_main_layout.setAlignment(Qt.AlignLeft)
        width_label = QLabel(self._tr("tileset_width_label"))
        width_label.setStyleSheet("QLabel { border: none; }")
        controls_main_layout.addWidget(width_label)
        self._tileset_width_label = width_label
        self.tile_width_spin = QSpinBox()
        self.tile_width_spin.setRange(0, 64)
        self.tile_width_spin.setValue(0)
        self.tile_width_spin.setFixedWidth(45)
        self.tile_width_spin.setFixedHeight(18)
        self.tile_width_spin.setStyleSheet("QSpinBox { font-size: 8pt; }")
        controls_main_layout.addWidget(self.tile_width_spin)
        height_label = QLabel(self._tr("tileset_height_label"))
        height_label.setStyleSheet("QLabel { border: none; }")
        controls_main_layout.addWidget(height_label)
        self._tileset_height_static_label = height_label
        self.tileset_height_label = QLabel("0")
        self.tileset_height_label.setFixedWidth(45)
        self.tileset_height_label.setFixedHeight(18)
        self.tileset_height_label.setAlignment(Qt.AlignCenter)
        self.tileset_height_label.setStyleSheet("QLabel { font-size: 8pt; border: 1px solid #ccc; background: #eee; padding: 1px; }")
        controls_main_layout.addWidget(self.tileset_height_label)
        self.flip_h_checkbox = QCheckBox(self._tr("flip_h_label"))
        self.flip_h_checkbox.setStyleSheet("QCheckBox { font-size: 8pt; }")
        self.flip_h_checkbox.setFixedHeight(18)
        self.flip_v_checkbox = QCheckBox(self._tr("flip_v_label"))
        self.flip_v_checkbox.setStyleSheet("QCheckBox { font-size: 8pt; }")
        self.flip_v_checkbox.setFixedHeight(18)
        controls_main_layout.addWidget(self.flip_h_checkbox)
        controls_main_layout.addWidget(self.flip_v_checkbox)
        controls_main_layout.addStretch()
        controls_layout.addLayout(controls_main_layout)
        self.tile_width_spin.valueChanged.connect(self._on_tileset_width_preview)
        self.tile_width_spin.editingFinished.connect(self._on_tileset_width_commit)

        self.flip_h_checkbox.toggled.connect(self._sync_flip_h_to_toolbar)
        self.flip_v_checkbox.toggled.connect(self._sync_flip_v_to_toolbar)

        container.layout().addWidget(controls_frame)
        
        self.tile_width_spin.setEnabled(False)
        self.flip_h_checkbox.setEnabled(False)
        self.flip_v_checkbox.setEnabled(False)
    
    def _on_tileset_width_preview(self, new_width):
        if not hasattr(self, 'tileset_img_original') or not self.tileset_img_original:
            return
        if new_width <= 0:
            self.tileset_height_label.setText("0")
            return

        original_w_px = self.tileset_img_original.width
        original_h_px = self.tileset_img_original.height
        total_tiles_original = (original_w_px // 8) * (original_h_px // 8)

        if new_width <= 0:
            new_width = 1
            self.tile_width_spin.setValue(1)

        new_height = (total_tiles_original + new_width - 1) // new_width
        self.tileset_height_label.setText(str(new_height))
        self.tiles_per_row = new_width
        self.render_tileset_with_padding(new_width, new_height, total_tiles_original)

    def _on_tileset_width_commit(self):
        if not hasattr(self, 'tileset_img_original') or not self.tileset_img_original:
            return

        new_width = self.tile_width_spin.value()
        old_width = getattr(self, '_tileset_width_before_edit', new_width)

        if new_width == old_width:
            return

        original_w_px = self.tileset_img_original.width
        original_h_px = self.tileset_img_original.height
        total_tiles = (original_w_px // 8) * (original_h_px // 8)
        old_height = (total_tiles + old_width - 1) // old_width
        new_height = (total_tiles + new_width - 1) // new_width

        if self.tileset_img:
            self.tileset_img.save("output/tiles.png")

        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tileset_reshape',
                editor_type='tiles',
                data={
                    'old_width': old_width, 'old_height': old_height,
                    'new_width': new_width, 'new_height': new_height,
                },
                description=self._tr('tileset_reshape_desc', old_w=old_width, old_h=old_height, new_w=new_width, new_h=new_height)
            )

        self._tileset_width_before_edit = new_width

    def _sync_flip_h_to_toolbar(self, checked):
        tb = getattr(getattr(self, 'main_window', None), 'context_toolbar', None)
        if tb and tb.btn_flip_h.isChecked() != checked:
            tb.btn_flip_h.blockSignals(True)
            tb.btn_flip_h.setChecked(checked)
            tb.btn_flip_h.blockSignals(False)

    def _sync_flip_v_to_toolbar(self, checked):
        tb = getattr(getattr(self, 'main_window', None), 'context_toolbar', None)
        if tb and tb.btn_flip_v.isChecked() != checked:
            tb.btn_flip_v.blockSignals(True)
            tb.btn_flip_v.setChecked(checked)
            tb.btn_flip_v.blockSignals(False)

    def render_tileset_with_padding(self, width_tiles, height_tiles, total_tiles_original):
        if not self.tileset_img_original:
            return

        img_width_px = width_tiles * 8
        img_height_px = height_tiles * 8
        
        if img_width_px == self.tileset_img_original.width and img_height_px == self.tileset_img_original.height:
            final_img = self.tileset_img_original
        else:
            mode = self.tileset_img_original.mode
            
            from PIL import Image as PilImage 

            final_img = PilImage.new(mode, (img_width_px, img_height_px), color=0)
            
            if mode == 'P':
                final_img.putpalette(self.tileset_img_original.getpalette())

            original_tiles_across = self.tileset_img_original.width // 8
            
            for i in range(total_tiles_original):
                tile_x_orig = (i % original_tiles_across) * 8
                tile_y_orig = (i // original_tiles_across) * 8
                
                tile_x_new = (i % width_tiles) * 8
                tile_y_new = (i // width_tiles) * 8
                
                box_orig = (tile_x_orig, tile_y_orig, tile_x_orig + 8, tile_y_orig + 8)
                tile = self.tileset_img_original.crop(box_orig)
                final_img.paste(tile, (tile_x_new, tile_y_new))

        self.tileset_img = final_img 
        

        from ui.shared_utils import pil_to_qimage 

        qimg = pil_to_qimage(final_img)
        pixmap = QPixmap.fromImage(qimg)
        
        self.edit_tileset_scene.clear()
        self.edit_tileset_scene.addPixmap(pixmap)
        self.edit_tileset_scene.setSceneRect(0, 0, img_width_px, img_height_px)
        
        self.main_window.apply_zoom_to_view(self.edit_tileset_view, self.main_window.zoom_level / 100.0)
        
        if self.selected_tile_pos != (-1, -1):
            self.highlight_selected_tile(*self.selected_tile_pos)
        
        if self.main_window.grid_manager.is_grid_visible():
            self.main_window.grid_manager.update_grid_for_view("tileset")

    def setup_tilemap_controls(self, container):
        container.layout().addWidget(self.build_tilemap_toolbar())

    def retranslate_ui(self):
        self._header_label.setText(self._tr("tab_header_edit_tiles"))
        self._tileset_section_label.setText(self._tr("section_tileset"))
        self._tilemap_section_label.setText(self._tr("section_tilemap"))
        self._tileset_width_label.setText(self._tr("tileset_width_label"))
        self._tileset_height_static_label.setText(self._tr("tileset_height_label"))
        self.flip_h_checkbox.setText(self._tr("flip_h_label"))
        self.flip_v_checkbox.setText(self._tr("flip_v_label"))
        self.retranslate_tilemap_toolbar()

    def create_header(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 10, QFont.Bold))
        label.setStyleSheet("QLabel { background: #555; color: white; padding: 4px; border-radius: 4px; }")
        label.setFixedHeight(30)
        label.setAlignment(Qt.AlignCenter)
        return label

    def create_section(self, title):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        label = QLabel(title)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return container

    def setup_view(self, view):
        view.setRenderHint(QPainter.Antialiasing, False)
        view.setRenderHint(QPainter.SmoothPixmapTransform, False)
        view.setStyleSheet("QGraphicsView { background: #f0f0f0; border: 1px solid #ccc; }")
        view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        view.setMouseTracking(True)
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def on_tileset_click(self, event):
        if event.button() != Qt.LeftButton or not self.tileset_img:
            return
        pos = self.edit_tileset_view.mapToScene(event.pos())
        
        scene_rect = self.edit_tileset_scene.sceneRect()
        if not (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            return
        
        tile_x = max(0, min(int(pos.x()) // 8, self.tiles_per_row - 1))
        max_tile_y = (self.tileset_img.height // 8) - 1
        tile_y = max(0, min(int(pos.y()) // 8, max_tile_y))
        self.selected_tile_id = tile_y * self.tiles_per_row + tile_x
        self.highlight_selected_tile(tile_x, tile_y)
        self.update_status_bar(self.last_hover_pos[0], self.last_hover_pos[1], tile_id=self.selected_tile_id)

    def setup_tileset_interaction(self):
        self.edit_tileset_view.setMouseTracking(True)
        self.edit_tileset_view.mouseMoveEvent = self.on_tileset_hover
        self.edit_tileset_view.leaveEvent = self.on_tileset_leave

    def on_tileset_hover(self, event):
        super(QGraphicsView, self.edit_tileset_view).mouseMoveEvent(event)
        
        if not self.tileset_img:
            return
            
        pos = self.edit_tileset_view.mapToScene(event.pos())
        scene_rect = self.edit_tileset_scene.sceneRect()
        
        if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            tile_x = max(0, min(int(pos.x()) // 8, self.tiles_per_row - 1))
            max_tile_y = (self.tileset_img.height // 8) - 1
            tile_y = max(0, min(int(pos.y()) // 8, max_tile_y))
            
            tile_id = tile_y * self.tiles_per_row + tile_x
            self.update_status_bar(-1, -1, tile_id=self.selected_tile_id if self.tileset_img else None)
        else:
            self.update_status_bar(-1, -1, tile_id=self.selected_tile_id if self.tileset_img else None)

    def on_tileset_leave(self, event):
        super(QGraphicsView, self.edit_tileset_view).leaveEvent(event)
        
        if hasattr(self, 'last_hover_pos') and self.last_hover_pos != (-1, -1):
            self.update_status_bar(*self.last_hover_pos)
        else:
            self.update_status_bar(-1, -1, tile_id=self.selected_tile_id if self.tileset_img else None)

    def highlight_selected_tile(self, tile_x, tile_y):
        self.selected_tile_pos = (tile_x, tile_y)
        
        for item in self.edit_tileset_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.edit_tileset_scene.removeItem(item)
        
        zoom_factor = self.edit_tileset_view.transform().m11()
        pen = QPen(QColor(255, 255, 0), 1.0)
        pen.setCosmetic(True)
        
        scene_size = 8 - (1 / zoom_factor)
        
        rect_item = self.edit_tileset_scene.addRect(
            tile_x * 8,
            tile_y * 8,
            scene_size,
            scene_size,
            pen
        )
        rect_item.setZValue(100)

    def on_tilemap_drawing(self, tile_x, tile_y):
        if self.selected_tile_id is None or not self.tilemap_data:
            return
        self.on_tilemap_hover(tile_x, tile_y)
        self.edit_tile_at(tile_x, tile_y)

    def on_tilemap_release(self):
        if not self.tilemap_data:
            return
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        self._update_all_displays()

    def _tilemap_index(self, tile_x, tile_y):
        w = self.tilemap_width
        if w <= 32:
            return tile_y * w + tile_x
        block_x = tile_x // 32
        block_y = tile_y // 32
        blocks_x = w // 32
        local_x = tile_x % 32
        local_y = tile_y % 32
        return (block_y * blocks_x + block_x) * 1024 + local_y * 32 + local_x

    def _is_rotation(self):
        return getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False

    def _entry_size(self):
        return 1 if self._is_rotation() else 2

    def _read_entry(self, tile_index):
        if self._is_rotation():
            return self.tilemap_data[tile_index], 0, 0, 0
        entry = self.tilemap_data[tile_index * 2] | (self.tilemap_data[tile_index * 2 + 1] << 8)
        return entry & 0x3FF, bool(entry & (1 << 10)), bool(entry & (1 << 11)), (entry >> 12) & 0xF

    def _write_entry(self, data, tile_index, tile_id, h_flip, v_flip, pal_id):
        if self._is_rotation():
            data[tile_index] = tile_id & 0xFF
        else:
            entry = tile_id & 0x3FF
            if h_flip: entry |= (1 << 10)
            if v_flip: entry |= (1 << 11)
            entry |= (pal_id << 12)
            data[tile_index * 2] = entry & 0xFF
            data[tile_index * 2 + 1] = (entry >> 8) & 0xFF

    def on_tilemap_right_click(self, tile_x, tile_y):
        if not self.tilemap_data:
            return
        tile_index = self._tilemap_index(tile_x, tile_y)
        es = self._entry_size()
        if tile_index * es + es > len(self.tilemap_data):
            return
        tile_id, h_flip, v_flip, _ = self._read_entry(tile_index)
        self.selected_tile_id = tile_id
        tx = tile_id % self.tiles_per_row
        ty = tile_id // self.tiles_per_row
        self.highlight_selected_tile(tx, ty)
        self.flip_h_checkbox.setChecked(h_flip)
        self.flip_v_checkbox.setChecked(v_flip)
        self.on_tilemap_hover(tile_x, tile_y)

    def edit_tile_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return
        tile_index = self._tilemap_index(tile_x, tile_y)
        es = self._entry_size()
        if tile_index * es + es > len(self.tilemap_data):
            return

        old_tile_id, old_h, old_v, old_pal = self._read_entry(tile_index)
        new_h = self.flip_h_checkbox.isChecked()
        new_v = self.flip_v_checkbox.isChecked()

        if old_tile_id == self.selected_tile_id and old_h == new_h and old_v == new_v:
            return

        old_state = {
            'tile_x': tile_x, 'tile_y': tile_y,
            'old_tile_id': old_tile_id, 'old_palette_id': old_pal,
            'old_h_flip': old_h, 'old_v_flip': old_v,
            'new_tile_id': self.selected_tile_id,
            'new_h_flip': new_h, 'new_v_flip': new_v
        }

        tilemap_data = bytearray(self.tilemap_data)
        self._write_entry(tilemap_data, tile_index, self.selected_tile_id, new_h, new_v, old_pal)
        self.tilemap_data = bytes(tilemap_data)

        if self.main_window and hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tile_change', editor_type='tiles',
                data=old_state,
                description=self._tr('tile_change_desc', x=tile_x, y=tile_y)
            )

        self.update_single_tile_visual(tile_x, tile_y, sync_palettes=False)
        if self.main_window and hasattr(self.main_window, 'edit_palettes_tab'):
            self.main_window.edit_palettes_tab.tilemap_data = self.tilemap_data
            self.main_window.edit_palettes_tab.update_single_tile_replica(tile_x, tile_y)

    def update_single_tile_visual(self, tile_x, tile_y, sync_palettes=True):
        if not self.tileset_img or not self.tilemap_data:
            return
        tile_index = self._tilemap_index(tile_x, tile_y)
        es = self._entry_size()
        if tile_index * es + es > len(self.tilemap_data):
            return

        tile_id, h_flip, v_flip, _ = self._read_entry(tile_index)
        tx = (tile_id % self.tiles_per_row) * 8
        ty = (tile_id // self.tiles_per_row) * 8
        if tx + 8 > self.tileset_img.width or ty + 8 > self.tileset_img.height:
            return

        tile = self.tileset_img.crop((tx, ty, tx + 8, ty + 8))
        if h_flip:
            tile = tile.transpose(PilImage.FLIP_LEFT_RIGHT)
        if v_flip:
            tile = tile.transpose(PilImage.FLIP_TOP_BOTTOM)

        qimg = pil_to_qimage(tile)
        pixmap = QPixmap.fromImage(qimg)

        x = tile_x * 8
        y = tile_y * 8

        if not hasattr(self, '_tilemap_items'):
            self._tilemap_items = {}

        old = self._tilemap_items.get((tile_x, tile_y))
        if old and old in self.edit_tilemap_scene.items():
            self.edit_tilemap_scene.removeItem(old)

        tile_item = self.edit_tilemap_scene.addPixmap(pixmap)
        tile_item.setPos(x, y)
        tile_item.setZValue(0)
        self._tilemap_items[(tile_x, tile_y)] = tile_item

        if sync_palettes and hasattr(self.main_window, 'edit_palettes_tab'):
            self.main_window.edit_palettes_tab.tilemap_data = self.tilemap_data
            self.main_window.edit_palettes_tab.update_single_tile_replica(tile_x, tile_y)

        self.on_tilemap_hover(tile_x, tile_y)

    def display_tileset(self, pil_img):
        self.edit_tileset_scene.clear()
        self.tileset_img_original = pil_img
        original_w_px = pil_img.width
        initial_width = original_w_px // 8
        self._tileset_width_before_edit = initial_width
        if hasattr(self, 'tile_width_spin'):
            self.tile_width_spin.setValue(initial_width)
        self._on_tileset_width_preview(initial_width)
        self.highlight_selected_tile(0, 0)

        is_rot = getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False
        if hasattr(self, 'tile_width_spin'):
            self.tile_width_spin.setEnabled(True)
            self.flip_h_checkbox.setEnabled(not is_rot)
            self.flip_v_checkbox.setEnabled(not is_rot)

        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tileset")

    def load_tilemap(self, tilemap_data, tileset_path, preview_path=None):
        self.tilemap_data = tilemap_data
        self._tilemap_items = {}
        if tileset_path and os.path.exists(tileset_path):
            with PilImage.open(tileset_path) as f:
                self.tileset_img = f.copy()
        self.tiles_per_row = self.tileset_img.width // 8 if self.tileset_img else 16

        is_rot = getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False
        entry_size = 1 if is_rot else 2

        if preview_path:
            try:
                with PilImage.open(preview_path) as f:
                    preview_img = f.copy()
                self.tilemap_width = preview_img.width // 8
                self.tilemap_height = preview_img.height // 8
            except:
                self.tilemap_width = 32
                self.tilemap_height = (len(tilemap_data) // entry_size + 31) // 32
        else:
            total_tiles = len(tilemap_data) // entry_size
            if total_tiles == 256:
                self.tilemap_width = 16
                self.tilemap_height = 16
            elif total_tiles == 1024:
                self.tilemap_width = 32
                self.tilemap_height = 32
            else:
                self.tilemap_width = 32
                self.tilemap_height = (total_tiles + 31) // 32

        self.tilemap_width_spin.setValue(self.tilemap_width)
        self.tilemap_height_spin.setValue(self.tilemap_height)
        self.enable_tilemap_controls()
        
        if hasattr(self.main_window, 'sync_palettes_tab'):
            self.main_window.sync_palettes_tab()
        if self.main_window and hasattr(self.main_window, 'grid_manager'):
            if self.main_window.grid_manager.is_grid_visible():
                self.main_window.grid_manager.update_grid_for_view("tilemap_edit")

    def apply_zoom(self, factor):
        self.edit_tileset_view.resetTransform()
        self.edit_tileset_view.scale(factor, factor)
        
        if self.selected_tile_pos != (-1, -1):
            self.highlight_selected_tile(*self.selected_tile_pos)

    def update_status_bar(self, tile_x, tile_y, tile_id=None, palette_id=None, flip_state=None):
        update_status_bar_shared(
            main_window=self.main_window,
            selection_type="Tile",
            selection_id=self.selected_tile_id if self.tileset_img else None,
            tile_x=tile_x,
            tile_y=tile_y,
            tilemap_data=self.tilemap_data if hasattr(self, 'tilemap_data') else None,
            tilemap_width=self.tilemap_width if hasattr(self, 'tilemap_width') else 0,
            tilemap_height=self.tilemap_height if hasattr(self, 'tilemap_height') else 0,
            tile_id=tile_id,
            palette_id=palette_id,
            flip_state=flip_state
        )

    def _update_all_displays(self):
        try:
            save_preview = False
            keep_transparent = False
            
            if hasattr(self.main_window, 'config_manager'):
                save_preview = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
                keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)
            
            from core.image_utils import create_gbagfx_preview
            result = create_gbagfx_preview(
                save_preview=save_preview,
                keep_transparent=keep_transparent
            )
            
            if result and hasattr(self.main_window, 'refresh_preview_display'):
                self.main_window.refresh_preview_display()
            elif result:
                self._manual_refresh_display()
                
        except Exception as e:
            print(f"Error updating displays: {e}")
            import traceback
            traceback.print_exc()

    def _manual_refresh_display(self):
        preview_path = "temp/preview/preview.png"
        if not os.path.exists(preview_path):
            return
        
        try:
            from PIL import Image
            from ui.shared_utils import pil_to_qimage

            
            with Image.open(preview_path) as f:
                preview_img = f.copy()
            preview_qimg = pil_to_qimage(preview_img)
            preview_pixmap = QPixmap.fromImage(preview_qimg)
            
            self.main_window.preview_tab.preview_image_scene.clear()
            self.main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
            self.main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())
            
            self.display_tilemap_replica(self.main_window.preview_tab.preview_image_scene)
            
        except Exception as e:
            print(f"Error in manual refresh: {e}")

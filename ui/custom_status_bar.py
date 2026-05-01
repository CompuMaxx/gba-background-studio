# ui/custom_status_bar.py

from ui.qt_compat import QWidget, QHBoxLayout, QLabel, Qt
class CustomStatusBar(QWidget):
    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self.tr = translator.tr if translator else lambda k, **kw: k
        self.setFixedHeight(24)
        self.setStyleSheet("""
            background: #f0f0f0; 
            border-top: 1px solid #ccc;
            font-size: 11px;
            color: #333;
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        
        self.selection_label = QLabel(self.tr("status_selected", type="Tile", id="0"))
        self.tilemap_label = QLabel(self.tr("status_tilemap", pos="(0, 0)"))
        self.tile_label = QLabel(self.tr("status_tile", id="0"))
        self.palette_label = QLabel(self.tr("status_palette", id="0"))
        self.flip_label = QLabel(self.tr("status_flip", state="None"))
        self.zoom_label = QLabel(self.tr("zoom_level", level=100))
        self.sel_area_label = QLabel()
        self.sel_area_label.hide()
        self._sel_area_wh = None

        layout.addWidget(self.selection_label)
        layout.addWidget(self.tilemap_label)
        layout.addWidget(self.tile_label)
        layout.addWidget(self.palette_label)
        layout.addWidget(self.flip_label)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.sel_area_label)
        layout.addStretch()
        
    def update_status(self, selection_type="Tile", selection_id="-", tilemap_pos=(-1, -1),
                     tile_id="-", palette_id="-", flip_state="None", zoom_level=100):
        self.selection_label.setText(self.tr("status_selected", type=selection_type, id=selection_id))
        tilemap_display = f"({tilemap_pos[0]}, {tilemap_pos[1]})" if tilemap_pos != (-1, -1) else "(-, -)"
        self.tilemap_label.setText(self.tr("status_tilemap", pos=tilemap_display))
        self.tile_label.setText(self.tr("status_tile", id=tile_id))
        self.palette_label.setText(self.tr("status_palette", id=palette_id))
        self.flip_label.setText(self.tr("status_flip", state=flip_state))
        self.zoom_label.setText(self.tr("zoom_level", level=zoom_level))

    def update_selection_status(self, x1, y1, x2, y2, zoom_level=None):
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        self.selection_label.setText(self.tr("status_origin", x=x1, y=y1))
        self.tilemap_label.setText(self.tr("status_end", x=x2, y=y2))
        self.tile_label.setText(self.tr("status_width_tiles", n=w))
        self.palette_label.setText(self.tr("status_height_tiles", n=h))
        self.flip_label.setText(self.tr("status_size_px", w=w*8, h=h*8))
        if zoom_level is not None:
            self.zoom_label.setText(self.tr("zoom_level", level=zoom_level))

    def restore_default_status(self, zoom_level=100):
        self.selection_label.setText(self.tr("status_selected", type=self.tr("type_tile"), id="-"))
        self.tilemap_label.setText(self.tr("status_tilemap", pos="(-, -)"))
        self.tile_label.setText(self.tr("status_tile", id="-"))
        self.palette_label.setText(self.tr("status_palette", id="-"))
        self.flip_label.setText(self.tr("status_flip", state="None"))
        self.zoom_label.setText(self.tr("zoom_level", level=zoom_level))

    def set_sel_area_info(self, w, h):
        self._sel_area_wh = (w, h)
        self.sel_area_label.setText(self.tr("status_sel_area", w=w, h=h, wpx=w*8, hpx=h*8))
        self.sel_area_label.show()

    def clear_sel_area_info(self):
        self._sel_area_wh = None
        self.sel_area_label.hide()
        self.sel_area_label.setText("")

    def retranslate_ui(self, zoom_level=100):
        self.restore_default_status(zoom_level)
        if self._sel_area_wh:
            w, h = self._sel_area_wh
            self.sel_area_label.setText(self.tr("status_sel_area", w=w, h=h, wpx=w*8, hpx=h*8))

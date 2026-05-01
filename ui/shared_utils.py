# ui/shared_utils.py

from ui.qt_compat import (
    QGraphicsView,
    QPen,
    QColor,
    QImage,
    Qt,
    QRect,
    QPoint,
    QSize,
    QGraphicsPixmapItem
)
_SEL_PEN = QPen(QColor(255, 255, 0), 2.0)
_SEL_PEN.setCosmetic(True)

def pil_to_qimage(pil_img):
    if pil_img.mode == "RGBA":
        data = pil_img.tobytes("raw", "RGBA")
        img = QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGBA8888)
        return img.copy()
    else:
        rgb_img = pil_img.convert("RGB")
        data = rgb_img.tobytes("raw", "RGB")
        img = QImage(data, rgb_img.size[0], rgb_img.size[1], QImage.Format_RGB888)
        return img.copy()

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._is_drawing = False
        self._had_drawing = False
        self.on_tile_drawing = None
        self.on_tile_selected = None
        self.on_tile_hover = None
        self.on_tile_leave = None
        self.on_tile_release = None
        self.selection_mode = False
        self.on_selection_complete = None
        self.on_selection_hover = None
        self._sel_origin = None
        self._sel_drag_item = None
        self.paste_mode = False
        self.on_paste = None
        self.on_paste_cancel = None
        self._paste_preview_item = None
        self._paste_pixmap = None

    def _scene_tile(self, pos):
        scene_rect = self.scene().sceneRect()
        tx = max(0, min(int(pos.x()) // 8, int(scene_rect.width())  // 8 - 1))
        ty = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))
        return tx, ty

    def _tile_to_viewport(self, tx, ty):
        scene_p1 = self.mapFromScene(tx * 8, ty * 8)
        scene_p2 = self.mapFromScene((tx + 1) * 8, (ty + 1) * 8)
        return scene_p1, scene_p2

    def _remove_paste_preview(self):
        try:
            if self._paste_preview_item is not None and self._paste_preview_item.scene():
                self.scene().removeItem(self._paste_preview_item)
        except RuntimeError:
            pass
        self._paste_preview_item = None

    def _update_paste_preview(self, tx, ty):
        self._remove_paste_preview()
        if self._paste_pixmap and self.scene():

            item = self.scene().addPixmap(self._paste_pixmap)
            item.setPos(tx * 8, ty * 8)
            item.setOpacity(0.6)
            item.setZValue(202)
            self._paste_preview_item = item

    def _remove_drag_item(self):
        try:
            if self._sel_drag_item is not None and self._sel_drag_item.scene():
                self.scene().removeItem(self._sel_drag_item)
        except RuntimeError:
            pass
        self._sel_drag_item = None

    def mousePressEvent(self, event):
        if self.paste_mode:
            scene_pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                tx, ty = self._scene_tile(scene_pos)
                if event.button() == Qt.LeftButton:
                    if self.on_paste:
                        self.on_paste(tx, ty)
                elif event.button() == Qt.RightButton:
                    self._remove_paste_preview()
                    if self.on_paste_cancel:
                        self.on_paste_cancel()
            event.accept()
            return
        if self.selection_mode and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                tx, ty = self._scene_tile(scene_pos)
                self._sel_tile_origin = (tx, ty)
                self._sel_origin = (tx, ty)
                self._remove_drag_item()
                self._sel_drag_item = self.scene().addRect(tx * 8, ty * 8, 8, 8, _SEL_PEN)
                self._sel_drag_item.setZValue(201)
            else:
                self._sel_origin = None
                self._sel_tile_origin = None
            event.accept()
            return
        if event.button() == Qt.LeftButton:
            self._is_drawing = True
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                scene_rect = self.scene().sceneRect()
                if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
                    tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
                    tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))
                    if self.on_tile_drawing:
                        self.on_tile_drawing(tile_x, tile_y)
                        self._had_drawing = True
            event.accept()
        elif event.button() == Qt.RightButton:
            pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                scene_rect = self.scene().sceneRect()
                if (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
                    tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
                    tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))
                    if self.on_tile_selected:
                        self.on_tile_selected(tile_x, tile_y)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.paste_mode:
            scene_pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                tx, ty = self._scene_tile(scene_pos)
                self._update_paste_preview(tx, ty)
            event.accept()
            return
        if self.selection_mode and self._sel_origin is not None:
            scene_pos = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid():
                ox, oy = self._sel_origin
                tx2, ty2 = self._scene_tile(scene_pos)
                x1, x2 = min(ox, tx2), max(ox, tx2)
                y1, y2 = min(oy, ty2), max(oy, ty2)
                self._remove_drag_item()
                w = (x2 - x1 + 1) * 8
                h = (y2 - y1 + 1) * 8
                self._sel_drag_item = self.scene().addRect(x1 * 8, y1 * 8, w, h, _SEL_PEN)
                self._sel_drag_item.setZValue(201)
                if self.on_selection_hover:
                    self.on_selection_hover(x1, y1, x2, y2)
            event.accept()
            return
        pos = self.mapToScene(event.pos())
        if not self.scene() or not pos or not self.scene().sceneRect().isValid():
            if self.on_tile_leave:
                self.on_tile_leave()
            super().mouseMoveEvent(event)
            return

        scene_rect = self.scene().sceneRect()
        if not (0 <= pos.x() < scene_rect.width() and 0 <= pos.y() < scene_rect.height()):
            if self.on_tile_leave:
                self.on_tile_leave()
            super().mouseMoveEvent(event)
            return

        tile_x = max(0, min(int(pos.x()) // 8, int(scene_rect.width()) // 8 - 1))
        tile_y = max(0, min(int(pos.y()) // 8, int(scene_rect.height()) // 8 - 1))

        if self.on_tile_hover:
            self.on_tile_hover(tile_x, tile_y)

        if self._is_drawing and (event.buttons() & Qt.LeftButton) and self.on_tile_drawing:
            self.on_tile_drawing(tile_x, tile_y)
            self._had_drawing = True
            event.accept()
        else:
            event.accept()
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.selection_mode and event.button() == Qt.LeftButton and self._sel_origin is not None:
            self._remove_drag_item()
            scene_p2 = self.mapToScene(event.pos())
            if self.scene() and self.scene().sceneRect().isValid() and hasattr(self, '_sel_tile_origin') and self._sel_tile_origin:
                ox, oy = self._sel_tile_origin
                tx2, ty2 = self._scene_tile(scene_p2)
                x1, x2 = min(ox, tx2), max(ox, tx2)
                y1, y2 = min(oy, ty2), max(oy, ty2)
                if self.on_selection_complete:
                    self.on_selection_complete(x1, y1, x2, y2)
            self._sel_origin = None
            self._sel_tile_origin = None
            event.accept()
            return
        if event.button() == Qt.LeftButton:
            self._is_drawing = False
            if self._had_drawing and self.on_tile_release:
                self.on_tile_release()
            self._had_drawing = False
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self.on_tile_leave:
            self.on_tile_leave()
        super().leaveEvent(event)

def update_status_bar_shared(main_window, selection_type, selection_id, tile_x, tile_y, 
                           tilemap_data=None, tilemap_width=0, tilemap_height=0, 
                           tile_id=None, palette_id=None, flip_state=None):
    if not main_window or not hasattr(main_window, 'custom_status_bar'):
        return
    
    if (tile_x, tile_y) == (-1, -1):
        tilemap_display = "(-, -)"
        flip_state_display = "None"
    else:
        if tile_id is None and tilemap_data:
            tile_index = tile_y * tilemap_width + tile_x
            if 0 <= tile_index < len(tilemap_data) // 2:
                entry = tilemap_data[tile_index * 2] | (tilemap_data[tile_index * 2 + 1] << 8)
                tile_id = entry & 0x3FF
        
        if palette_id is None and tilemap_data:
            tile_index = tile_y * tilemap_width + tile_x
            if 0 <= tile_index < len(tilemap_data) // 2:
                entry = tilemap_data[tile_index * 2] | (tilemap_data[tile_index * 2 + 1] << 8)
                palette_id = (entry >> 12) & 0xF
                h_flip = bool(entry & (1 << 10))
                v_flip = bool(entry & (1 << 11))
                if h_flip and v_flip:
                    flip_state = "XY"
                elif h_flip:
                    flip_state = "X"
                elif v_flip:
                    flip_state = "Y"
                else:
                    flip_state = "None"
        
        tilemap_display = f"({tile_x}, {tile_y})"
        flip_state_display = flip_state if flip_state is not None else "None"
    
    tile_display = str(tile_id) if tile_id is not None else "-"
    palette_display = f"{palette_id:X}" if palette_id is not None else "-"
    selection_display = str(selection_id) if selection_id is not None else "-"
    
    zoom_level = int(main_window.zoom_level) if hasattr(main_window, 'zoom_level') else 100
    
    main_window.custom_status_bar.update_status(
        selection_type=selection_type,
        selection_id=selection_display,
        tilemap_pos=(tile_x, tile_y),
        tile_id=tile_display,
        palette_id=palette_display,
        flip_state=flip_state if flip_state is not None else "None",
        zoom_level=zoom_level
    )

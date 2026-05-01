# ui/hover_manager.py

from ui.qt_compat import (
    QWidget,
    QPainter,
    QPen,
    QColor,
    QCursor,
    Qt
)
class HoverManager:
    def __init__(self):
        self._overlays = {}
        self.hover_pos = (-1, -1)

    def register_view(self, view):
        if view in self._overlays:
            return
        overlay = self._HoverOverlay(view, self)
        self._overlays[view] = overlay

    def update_hover(self, tile_x, tile_y, view):
        if view not in self._overlays:
            return
        self.hover_pos = (tile_x, tile_y)
        self._overlays[view].update_hover(tile_x, tile_y)

    def update_hover_from_cursor(self, view):
        if view not in self._overlays or not view.scene():
            self.hide_hover(view)
            return
            
        cursor_pos = view.mapFromGlobal(QCursor.pos())
        
        viewport_rect = view.viewport().rect()
        if not viewport_rect.contains(cursor_pos):
            self.hide_hover(view)
            return
        
        scene_pos = view.mapToScene(cursor_pos)
        
        tile_x = int(scene_pos.x() // 8)
        tile_y = int(scene_pos.y() // 8)
        
        scene_rect = view.scene().sceneRect()
        if (0 <= tile_x < scene_rect.width() // 8 and 
            0 <= tile_y < scene_rect.height() // 8):
            self.update_hover(tile_x, tile_y, view)
        else:
            self.hide_hover(view)

    def hide_hover(self, view):
        if view in self._overlays:
            self._overlays[view].hide()
            self.hover_pos = (-1, -1)

    def get_hover_pos(self):
        return self.hover_pos

    def sync_to_view(self, view):
        tile_x, tile_y = self.get_hover_pos()
        if tile_x == -1 or tile_y == -1:
            self.hide_hover(view)
            return
        self.update_hover(tile_x, tile_y, view)

    class _HoverOverlay(QWidget):
        def __init__(self, parent_view, manager):
            super().__init__(parent_view)
            self.parent_view = parent_view
            self.manager = manager
            self.tile_x = -1
            self.tile_y = -1
            self.visible = False
            self.pen = QPen(QColor(255, 0, 0), 1.0)
            self.pen.setCosmetic(True)

            self.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.resize(parent_view.viewport().size())

            def resize_event(event):
                self.resize(parent_view.viewport().size())
                if self.visible:
                    self.update_hover(self.tile_x, self.tile_y)
                parent_view.__class__.resizeEvent(parent_view, event)

            parent_view.resizeEvent = resize_event

        def update_hover(self, tile_x, tile_y):
            self.tile_x = tile_x
            self.tile_y = tile_y
            self.visible = True

            scene_x = tile_x * 8
            scene_y = tile_y * 8

            point = self.parent_view.mapFromScene(scene_x, scene_y)

            zoom_factor = self.parent_view.transform().m11()
            size = int(8 * zoom_factor)
            
            corrected_x = point.x() + 1
            corrected_y = point.y() + 1
            
            self.setGeometry(corrected_x, corrected_y, size, size)
            self.update()

        def hide(self):
            self.visible = False
            self.tile_x = -1
            self.tile_y = -1
            self.update()

        def paintEvent(self, event):
            if not self.visible or self.tile_x == -1 or self.tile_y == -1:
                return

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.setPen(self.pen)
            painter.setBrush(Qt.NoBrush)
            
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

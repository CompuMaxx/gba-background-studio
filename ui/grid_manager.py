# ui/grid_manager.py

from ui.qt_compat import (
    Qt,
    QPen,
    QColor,
    QPainter,
    QGraphicsLineItem
)
class GridManager:
    def __init__(self):
        self._grid_visible = False
        self._grid_items = {}
        self._grid_color = QColor(255, 255, 255)
        self._grid_alpha = 180
        self._grid_pen = self._make_pen()

    def _make_pen(self):
        color = QColor(self._grid_color)
        color.setAlpha(self._grid_alpha)
        pen = QPen(color, 1.0, Qt.DashLine)
        pen.setCosmetic(True)
        pen.setDashPattern([2, 2])
        return pen

    def set_grid_color(self, r, g, b):
        self._grid_color = QColor(r, g, b)
        self._grid_pen = self._make_pen()
        self._refresh_all_pens()

    def set_grid_alpha(self, alpha):
        self._grid_alpha = alpha
        self._grid_pen = self._make_pen()
        self._refresh_all_pens()

    def _refresh_all_pens(self):
        for view_data in self._grid_items.values():
            for item in view_data['items']:
                item.setPen(self._grid_pen)

    def register_view(self, view, view_name):
        if view_name not in self._grid_items:
            self._grid_items[view_name] = {
                'view': view,
                'items': [],
                'scene': view.scene() if hasattr(view, 'scene') else None
            }

    def set_grid_visible(self, visible):
        if self._grid_visible == visible:
            return
            
        self._grid_visible = visible
        
        for view_data in self._grid_items.values():
            if view_data['scene']:
                for item in view_data['items']:
                    if item in view_data['scene'].items():
                        view_data['scene'].removeItem(item)
                view_data['items'].clear()
                
                if visible:
                    self._create_grid_for_view(view_data)

    def toggle_grid(self):
        self.set_grid_visible(not self._grid_visible)

    def is_grid_visible(self):
        return self._grid_visible

    def update_grid_for_view(self, view_name):
        if view_name not in self._grid_items:
            return
            
        view_data = self._grid_items[view_name]
        
        for item in view_data['items']:
            if item in view_data['scene'].items():
                view_data['scene'].removeItem(item)
        view_data['items'].clear()
        
        if self._grid_visible:
            self._create_grid_for_view(view_data)

    def _create_grid_for_view(self, view_data):
        if not view_data['scene'] or not view_data['scene'].sceneRect().isValid():
            return
            
        scene_rect = view_data['scene'].sceneRect()
        width = scene_rect.width()
        height = scene_rect.height()
        
        for x in range(0, int(width) + 1, 8):
            line = QGraphicsLineItem(x, 0, x, height)
            line.setPen(self._grid_pen)
            line.setZValue(5)
            view_data['scene'].addItem(line)
            view_data['items'].append(line)
        
        for y in range(0, int(height) + 1, 8):
            line = QGraphicsLineItem(0, y, width, y)
            line.setPen(self._grid_pen)
            line.setZValue(5)
            view_data['scene'].addItem(line)
            view_data['items'].append(line)

    def clear_all_grids(self):
        for view_data in self._grid_items.values():
            if view_data['scene']:
                for item in view_data['items']:
                    if item in view_data['scene'].items():
                        view_data['scene'].removeItem(item)
                view_data['items'].clear()

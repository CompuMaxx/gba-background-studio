# ui/palette_grid_view.py

from ui.qt_compat import (
    QGraphicsView,
    QGraphicsScene,
    QWidget,
    QPen,
    QBrush,
    QColor,
    QPainter,
    QFont,
    Qt
)
class PaletteGridView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QGraphicsView { border: none; background: transparent; }")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene(0, 0, 32, 32)
        self.setScene(self.scene)
        self.colors = [
            QColor(238, 136, 116), QColor(248, 210, 144), QColor(160, 218, 228), QColor(244, 156, 178),
            QColor(190, 180, 223), QColor(164, 248, 140), QColor(224, 154, 102), QColor(246, 230, 175),
            QColor(190, 228, 226), QColor(232, 180, 190), QColor(220, 200, 240), QColor(134, 200, 120),
            QColor(246, 188, 104), QColor(148, 196, 218), QColor(248, 146, 198), QColor(180, 160, 200)
        ]
        
        self.selection_overlay = QWidget(self.viewport())
        self.selection_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.selection_overlay.hide()
        self.selection_overlay.setStyleSheet("QWidget { background: transparent; }")
        
        self.selection_pen = QPen(QColor(0, 0, 0), 1.0)
        self.selection_pen.setCosmetic(True)
        
        self.draw_grid()
        self.selected_palette_pos = (-1, -1)

        self.selection_overlay.paintEvent = self.paintSelectionOverlay

    def draw_grid(self):
        self.scene.clear()
        font = QFont("Arial", 5, QFont.Normal)
        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                x = j * 8
                y = i * 8
                self.scene.addRect(x, y, 8, 8, pen=QPen(Qt.NoPen), brush=QBrush(self.colors[idx]))
                
                text = self.scene.addText(f"{idx:X}")
                text.setDefaultTextColor(Qt.black)
                text.setFont(font)
                rect = text.boundingRect()
                cx = x + (8 - rect.width()) / 2
                cy = y + (8 - rect.height()) * 0.5
                text.setPos(cx, cy)

    def highlight_selected_palette(self, palette_x, palette_y):
        self.selected_palette_pos = (palette_x, palette_y)
        
        if palette_x == -1 or palette_y == -1:
            self.selection_overlay.hide()
            return
            
        zoom_factor = self.transform().m11()
        x = palette_x * 8 * zoom_factor
        y = palette_y * 8 * zoom_factor
        size = 8 * zoom_factor
        
        self.selection_overlay.setGeometry(int(x), int(y), int(size), int(size))
        self.selection_overlay.show()
        self.selection_overlay.update()

    def set_zoom_factor(self, factor):
        self.resetTransform()
        self.scale(factor, factor)
        self.setFixedSize(32 * factor, 32 * factor)
        
        if self.selected_palette_pos != (-1, -1):
            self.highlight_selected_palette(*self.selected_palette_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.selection_overlay.resize(self.viewport().size())
        
        if self.selected_palette_pos != (-1, -1):
            self.highlight_selected_palette(*self.selected_palette_pos)

    def paintSelectionOverlay(self, event):
        if self.selected_palette_pos == (-1, -1):
            return
            
        painter = QPainter(self.selection_overlay)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setPen(self.selection_pen)
        painter.setBrush(Qt.NoBrush)
        
        painter.drawRect(0.5, 0.5, self.selection_overlay.width() - 1, self.selection_overlay.height() - 1)

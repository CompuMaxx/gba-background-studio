# ui/tilemap_utils.py

from core.config import ROT_SIZES, ROT_SIZES_SET
from ui.qt_compat import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QCheckBox,
    Qt,
    QPen,
    QColor,
    QPixmap,
    QPainter,
    QImage,
    QBrush,
    QGraphicsRectItem,
    QDialog,
    QListWidget,
    QDialogButtonBox,
    exec_dialog,
)

class TilemapUtils:
    @property
    def _tr(self):
        """Get translator function, with fallback for subclasses that don't define it."""
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'translator'):
            return self.main_window.translator.tr
        return lambda key, **kw: key

    def setup_tilemap_interaction(self):
        self._tilemap_sel_area = None
        self._tilemap_sel_area_item = None
        self._pal_sel_items = []
        self._pal_sel_palette_id = -1
        self._pal_sel_origin = None
        self.tilemap_view.on_tile_drawing       = self._on_tile_drawing_dispatch
        self.tilemap_view.on_tile_selected      = self._on_tile_selected_dispatch
        self.tilemap_view.on_tile_hover         = self.on_tilemap_hover
        self.tilemap_view.on_tile_leave         = self.on_tilemap_leave
        self.tilemap_view.on_tile_release       = self._on_tile_release_dispatch
        self.tilemap_view.on_selection_complete = self._on_area_selection_complete
        self.tilemap_view.on_selection_hover = self._on_area_selection_hover

    def _toolbar(self):
        return getattr(getattr(self, 'main_window', None), 'context_toolbar', None)

    def _select_area_active(self):
        tb = self._toolbar()
        return tb is not None and hasattr(self, 'edit_tileset_view') and tb.btn_select_rect.isChecked()

    def _pal_select_area_active(self):
        tb = self._toolbar()
        return tb is not None and not hasattr(self, 'edit_tileset_view') and tb.btn_pal_select_rect.isChecked()

    def _wand_active(self):
        tb = self._toolbar()
        return tb is not None and not hasattr(self, 'edit_tileset_view') and tb.btn_pencil_pal.isChecked()

    def _fill_active(self):
        tb = self._toolbar()
        return tb is not None and not hasattr(self, 'edit_tileset_view') and tb.btn_fill.isChecked()

    def _get_palette_id_at(self, tile_x, tile_y):
        if not self.tilemap_data:
            return -1
        idx = self._tilemap_index(tile_x, tile_y) if hasattr(self, '_tilemap_index') else tile_y * self.tilemap_width + tile_x
        if idx * 2 + 2 > len(self.tilemap_data):
            return -1
        entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
        return (entry >> 12) & 0xF

    def _select_tiles_by_palette(self, palette_id):

        self._clear_pal_selection()
        if not self.tilemap_data or self.tilemap_width == 0 or self.tilemap_height == 0:
            return
        self._pal_sel_palette_id = palette_id
        pen = QPen(QColor(255, 255, 0), 2.0)
        pen.setCosmetic(True)
        get_idx = (self._tilemap_index if hasattr(self, '_tilemap_index')
                   else lambda x, y: y * self.tilemap_width + x)
        for ty in range(self.tilemap_height):
            for tx in range(self.tilemap_width):
                idx = get_idx(tx, ty)
                if idx * 2 + 2 > len(self.tilemap_data):
                    continue
                entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
                if (entry >> 12) & 0xF == palette_id:
                    item = self.tilemap_scene.addRect(tx * 8, ty * 8, 8, 8, pen)
                    item.setZValue(200)
                    self._pal_sel_items.append(item)
        self.tilemap_view.viewport().update()
        tb = self._toolbar()
        if tb is not None:
            tb.on_pal_selection_changed(bool(self._pal_sel_items))

    def _flood_fill_by_palette(self, start_x, start_y, palette_id):

        from collections import deque
        self._clear_pal_selection()
        if not self.tilemap_data or self.tilemap_width == 0 or self.tilemap_height == 0:
            return
        self._pal_sel_palette_id = palette_id
        self._pal_sel_origin = (start_x, start_y)
        pen = QPen(QColor(255, 255, 0), 2.0)
        pen.setCosmetic(True)
        get_idx = (self._tilemap_index if hasattr(self, '_tilemap_index')
                   else lambda x, y: y * self.tilemap_width + x)
        visited = set()
        queue = deque([(start_x, start_y)])
        while queue:
            tx, ty = queue.popleft()
            if (tx, ty) in visited:
                continue
            if not (0 <= tx < self.tilemap_width and 0 <= ty < self.tilemap_height):
                continue
            idx = get_idx(tx, ty)
            if idx * 2 + 2 > len(self.tilemap_data):
                continue
            entry = self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8)
            if (entry >> 12) & 0xF != palette_id:
                continue
            visited.add((tx, ty))
            item = self.tilemap_scene.addRect(tx * 8, ty * 8, 8, 8, pen)
            item.setZValue(200)
            self._pal_sel_items.append(item)
            queue.extend([(tx+1, ty), (tx-1, ty), (tx, ty+1), (tx, ty-1)])
        self.tilemap_view.viewport().update()
        tb = self._toolbar()
        if tb is not None:
            tb.on_pal_selection_changed(bool(self._pal_sel_items))

    def _clear_pal_selection(self):
        for item in self._pal_sel_items:
            try:
                if item.scene():
                    self.tilemap_scene.removeItem(item)
            except RuntimeError:
                pass
        self._pal_sel_items = []
        self._pal_sel_palette_id = -1
        self._pal_sel_origin = None
        tb = self._toolbar()
        if tb is not None:
            tb.on_pal_selection_changed(False)

    def _restore_pal_selection(self):
        if self._pal_sel_palette_id < 0:
            return
        if self._pal_sel_origin is not None:
            self._flood_fill_by_palette(*self._pal_sel_origin, self._pal_sel_palette_id)
        else:
            self._select_tiles_by_palette(self._pal_sel_palette_id)

    def set_area_selection_mode(self, active: bool):
        self.tilemap_view.selection_mode = active
        if not active:
            self._clear_tilemap_area_selection()

    def _on_area_selection_hover(self, x1, y1, x2, y2):
        mw = getattr(self, 'main_window', None)
        if mw and hasattr(mw, 'custom_status_bar'):
            mw.custom_status_bar.update_selection_status(x1, y1, x2, y2, mw.zoom_level)

    def _on_area_selection_complete(self, x1, y1, x2, y2):
        self._clear_tilemap_selection()
        self._tilemap_sel_area = (x1, y1, x2, y2)
        self._draw_tilemap_area_rect(x1, y1, x2, y2)
        tb = self._toolbar()
        if tb is not None:
            tb.on_area_selected(True)
        mw = getattr(self, 'main_window', None)
        if mw and hasattr(mw, 'custom_status_bar'):
            mw.custom_status_bar.update_selection_status(x1, y1, x2, y2, mw.zoom_level)
            mw.custom_status_bar.set_sel_area_info(x2 - x1 + 1, y2 - y1 + 1)

    def _clear_tilemap_area_selection(self):
        self._tilemap_sel_area = None
        try:
            if self._tilemap_sel_area_item is not None:
                if self._tilemap_sel_area_item.scene():
                    self.tilemap_scene.removeItem(self._tilemap_sel_area_item)
        except RuntimeError:
            pass
        self._tilemap_sel_area_item = None
        tb = self._toolbar()
        if tb is not None:
            tb.on_area_selected(False)
        mw = getattr(self, 'main_window', None)
        if mw and hasattr(mw, 'custom_status_bar'):
            mw.custom_status_bar.restore_default_status(mw.zoom_level)
            mw.custom_status_bar.clear_sel_area_info()

    def _draw_tilemap_area_rect(self, x1, y1, x2, y2):

        try:
            if self._tilemap_sel_area_item is not None:
                if self._tilemap_sel_area_item.scene():
                    self.tilemap_scene.removeItem(self._tilemap_sel_area_item)
        except RuntimeError:
            pass
        self._tilemap_sel_area_item = None
        pen = QPen(QColor(255, 255, 0), 2.0)
        pen.setCosmetic(True)
        w = (x2 - x1 + 1) * 8
        h = (y2 - y1 + 1) * 8
        self._tilemap_sel_area_item = self.tilemap_scene.addRect(x1 * 8, y1 * 8, w, h, pen)
        self._tilemap_sel_area_item.setZValue(200)
        self.tilemap_view.viewport().update()

    def _restore_tilemap_area_selection(self):
        if self._tilemap_sel_area is not None:
            self._draw_tilemap_area_rect(*self._tilemap_sel_area)

    def _on_tile_release_dispatch(self):
        self.on_tilemap_release()
        self._restore_tilemap_selection()

    def _restore_tilemap_selection(self):
        self._restore_tilemap_area_selection()
        self._restore_pal_selection()

    def _on_tile_drawing_dispatch(self, tile_x, tile_y):
        if self._select_area_active() or self._pal_select_area_active():
            pass
        elif self._wand_active():
            pal_id = self._get_palette_id_at(tile_x, tile_y)
            if pal_id >= 0:
                self._select_tiles_by_palette(pal_id)
        elif self._fill_active():
            pal_id = self._get_palette_id_at(tile_x, tile_y)
            if pal_id >= 0:
                self._flood_fill_by_palette(tile_x, tile_y, pal_id)
        else:
            self.on_tilemap_drawing(tile_x, tile_y)

    def _on_tile_selected_dispatch(self, tile_x, tile_y):
        if self._select_area_active() or self._pal_select_area_active():
            self._clear_tilemap_area_selection()
        elif self._wand_active() or self._fill_active():
            self._clear_pal_selection()
        else:
            self.on_tilemap_right_click(tile_x, tile_y)

    def _set_tilemap_selection(self, tile_x, tile_y):
        pass

    def _clear_tilemap_selection(self):
        self._clear_tilemap_area_selection()

    def _draw_tilemap_selection_rect(self, tile_x, tile_y):
        pass

    def _apply_transform(self, op):
        if not self._tilemap_sel_area or not self.tilemap_data:
            return
        x1, y1, x2, y2 = self._tilemap_sel_area
        old_data = self.tilemap_data
        new_data = bytearray(old_data)

        def get_entry(tx, ty):
            idx = (self._tilemap_index(tx, ty) if hasattr(self, '_tilemap_index')
                   else ty * self.tilemap_width + tx)
            if idx * 2 + 2 > len(new_data):
                return 0
            return new_data[idx * 2] | (new_data[idx * 2 + 1] << 8)

        def set_entry(tx, ty, entry):
            idx = (self._tilemap_index(tx, ty) if hasattr(self, '_tilemap_index')
                   else ty * self.tilemap_width + tx)
            if idx * 2 + 2 > len(new_data):
                return
            new_data[idx * 2]     = entry & 0xFF
            new_data[idx * 2 + 1] = (entry >> 8) & 0xFF

        w = x2 - x1 + 1
        h = y2 - y1 + 1

        if op == 'flip_h':
            for ty in range(y1, y2 + 1):
                for tx in range(x1, x2 + 1):
                    e = get_entry(tx, ty)
                    set_entry(tx, ty, e ^ (1 << 10))

        elif op == 'flip_v':
            for ty in range(y1, y2 + 1):
                for tx in range(x1, x2 + 1):
                    e = get_entry(tx, ty)
                    set_entry(tx, ty, e ^ (1 << 11))

        elif op == 'swap_h':
            for ty in range(y1, y2 + 1):
                for dx in range(w // 2):
                    lx, rx = x1 + dx, x2 - dx
                    l, r = get_entry(lx, ty), get_entry(rx, ty)
                    set_entry(lx, ty, r)
                    set_entry(rx, ty, l)

        elif op == 'swap_v':
            for tx in range(x1, x2 + 1):
                for dy in range(h // 2):
                    ty_top, ty_bot = y1 + dy, y2 - dy
                    t, b = get_entry(tx, ty_top), get_entry(tx, ty_bot)
                    set_entry(tx, ty_top, b)
                    set_entry(tx, ty_bot, t)

        elif op == 'mirror_h':
            for ty in range(y1, y2 + 1):
                for dx in range(w // 2):
                    lx, rx = x1 + dx, x2 - dx
                    l, r = get_entry(lx, ty), get_entry(rx, ty)
                    set_entry(lx, ty, r ^ (1 << 10))
                    set_entry(rx, ty, l ^ (1 << 10))
            if w % 2 == 1:
                cx = x1 + w // 2
                for ty in range(y1, y2 + 1):
                    set_entry(cx, ty, get_entry(cx, ty) ^ (1 << 10))

        elif op == 'mirror_v':
            for tx in range(x1, x2 + 1):
                for dy in range(h // 2):
                    ty_top, ty_bot = y1 + dy, y2 - dy
                    t, b = get_entry(tx, ty_top), get_entry(tx, ty_bot)
                    set_entry(tx, ty_top, b ^ (1 << 11))
                    set_entry(tx, ty_bot, t ^ (1 << 11))
            if h % 2 == 1:
                cy = y1 + h // 2
                for tx in range(x1, x2 + 1):
                    set_entry(tx, cy, get_entry(tx, cy) ^ (1 << 11))

        self.tilemap_data = bytes(new_data)
        mw = getattr(self, 'main_window', None)
        if mw:
            for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
                other = getattr(mw, attr, None)
                if other and other is not self:
                    other.tilemap_data = self.tilemap_data
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        if mw and hasattr(mw, 'history_manager'):
            mw.history_manager.record_state(
                state_type='tilemap_transform',
                editor_type='tiles',
                data={'old_data': old_data, 'new_data': self.tilemap_data,
                      'op': op, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                description=f"{op} ({x1},{y1})-({x2},{y2})"
            )
        if mw and hasattr(mw, '_save_map_and_refresh'):
            mw._save_map_and_refresh()
        self._clear_tilemap_area_selection()
        tb = self._toolbar()
        if tb is not None:
            tb.on_area_selected(False)

    def _copy_selection(self, is_cut=False):
        if not self._tilemap_sel_area or not self.tilemap_data:
            return
        x1, y1, x2, y2 = self._tilemap_sel_area
        buf_w = x2 - x1 + 1
        buf_h = y2 - y1 + 1
        buf = []
        for ty in range(y1, y2 + 1):
            row = []
            for tx in range(x1, x2 + 1):
                idx = (self._tilemap_index(tx, ty) if hasattr(self, '_tilemap_index')
                       else ty * self.tilemap_width + tx)
                if idx * 2 + 2 <= len(self.tilemap_data):
                    row.append(self.tilemap_data[idx * 2] | (self.tilemap_data[idx * 2 + 1] << 8))
                else:
                    row.append(0)
            buf.append(row)
        self._paste_buffer = buf
        self._paste_buf_w = buf_w
        self._paste_buf_h = buf_h
        if is_cut:
            self._cut_selection(defer_refresh=True)
            mw = getattr(self, 'main_window', None)
            if mw and hasattr(mw, '_save_map_and_refresh'):
                mw._save_map_and_refresh()
        else:
            self._clear_tilemap_area_selection()
        self._start_paste_mode()

    def _build_paste_pixmap(self):

        et = getattr(getattr(self, 'main_window', None), 'edit_tiles_tab', None)
        if not et or not getattr(et, 'tileset_img', None):
            px = QPixmap(self._paste_buf_w * 8, self._paste_buf_h * 8)
            px.fill(QColor(255, 255, 0, 80))
            return px
        import numpy as np
        ts = et.tileset_img
        tpr = et.tiles_per_row if et.tiles_per_row > 0 else ts.width // 8
        ep = getattr(self.main_window, 'edit_palettes_tab', None)
        palette = ep.palette_colors if ep else [(i, i, i) for i in range(256)]
        w_px = self._paste_buf_w * 8
        h_px = self._paste_buf_h * 8
        canvas = np.zeros((h_px, w_px, 4), dtype=np.uint8)
        ts_arr = np.array(ts)
        for row_i, row in enumerate(self._paste_buffer):
            for col_i, entry in enumerate(row):
                tile_id = entry & 0x3FF
                h_flip  = bool(entry & (1 << 10))
                v_flip  = bool(entry & (1 << 11))
                pal_id  = (entry >> 12) & 0xF
                src_x = (tile_id % tpr) * 8
                src_y = (tile_id // tpr) * 8
                if src_x + 8 > ts.width or src_y + 8 > ts.height:
                    continue
                tile = ts_arr[src_y:src_y+8, src_x:src_x+8].copy()
                if h_flip: tile = np.fliplr(tile)
                if v_flip: tile = np.flipud(tile)
                slot = pal_id * 16
                for py in range(8):
                    for px_i in range(8):
                        idx_c = int(tile[py, px_i]) % 16
                        r, g, b = palette[slot + idx_c]
                        canvas[row_i*8+py, col_i*8+px_i] = [r, g, b, 180]
        img_data = canvas.tobytes()
        img = QImage(img_data, w_px, h_px, w_px * 4, QImage.Format_RGBA8888)
        return QPixmap.fromImage(img.copy())

    def _start_paste_mode(self):
        pixmap = self._build_paste_pixmap()
        self.tilemap_view.paste_mode = True
        self.tilemap_view._paste_pixmap = pixmap
        self.tilemap_view.on_paste = self._do_paste
        self.tilemap_view.on_paste_cancel = self._cancel_paste
        self.tilemap_view.viewport().setCursor(Qt.CrossCursor)
        tb = self._toolbar()
        if tb is not None:
            tb.on_paste_mode_active(True)

    def _do_paste(self, tx, ty):
        if not hasattr(self, '_paste_buffer') or not self.tilemap_data:
            return
        old_data = self.tilemap_data
        new_data = bytearray(old_data)
        for row_i, row in enumerate(self._paste_buffer):
            for col_i, entry in enumerate(row):
                dst_x = tx + col_i
                dst_y = ty + row_i
                if dst_x >= self.tilemap_width or dst_y >= self.tilemap_height:
                    continue
                if dst_x < 0 or dst_y < 0:
                    continue
                idx = (self._tilemap_index(dst_x, dst_y) if hasattr(self, '_tilemap_index')
                       else dst_y * self.tilemap_width + dst_x)
                if idx * 2 + 2 > len(new_data):
                    continue
                new_data[idx * 2]     = entry & 0xFF
                new_data[idx * 2 + 1] = (entry >> 8) & 0xFF
        self.tilemap_data = bytes(new_data)
        mw = getattr(self, 'main_window', None)
        if mw:
            for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
                other = getattr(mw, attr, None)
                if other and other is not self:
                    other.tilemap_data = self.tilemap_data
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        if mw and hasattr(mw, 'history_manager'):
            mw.history_manager.record_state(
                state_type='tilemap_paste',
                editor_type='tiles',
                data={'old_data': old_data, 'new_data': self.tilemap_data,
                      'tx': tx, 'ty': ty},
                description=f"Paste at ({tx},{ty})"
            )
        if mw and hasattr(mw, '_save_map_and_refresh'):
            mw._save_map_and_refresh()

    def _cancel_paste(self):
        self.tilemap_view.paste_mode = False
        self.tilemap_view._paste_pixmap = None
        self.tilemap_view.on_paste = None
        self.tilemap_view.on_paste_cancel = None
        self.tilemap_view._remove_paste_preview()
        self.tilemap_view.viewport().setCursor(Qt.ArrowCursor)
        self._paste_buffer = None
        tb = self._toolbar()
        if tb is not None:
            tb.on_paste_mode_active(False)

    def _cut_selection(self, defer_refresh=False):
        if not self._tilemap_sel_area or not self.tilemap_data:
            return
        x1, y1, x2, y2 = self._tilemap_sel_area
        old_data = self.tilemap_data
        new_data = bytearray(old_data)
        affected = []
        for ty in range(y1, y2 + 1):
            for tx in range(x1, x2 + 1):
                idx = (self._tilemap_index(tx, ty) if hasattr(self, '_tilemap_index')
                       else ty * self.tilemap_width + tx)
                if idx * 2 + 2 > len(new_data):
                    continue
                new_data[idx * 2]     = 0x00
                new_data[idx * 2 + 1] = 0x00
                affected.append((tx, ty))
        self.tilemap_data = bytes(new_data)
        mw = getattr(self, 'main_window', None)
        if mw:
            for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
                other = getattr(mw, attr, None)
                if other and other is not self:
                    other.tilemap_data = self.tilemap_data
        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(self.tilemap_data)
        if mw and hasattr(mw, 'history_manager'):
            mw.history_manager.record_state(
                state_type='tilemap_cut',
                editor_type='tiles',
                data={'old_data': old_data, 'new_data': self.tilemap_data,
                      'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                description=f"Cut ({x1},{y1})-({x2},{y2})"
            )
        self._clear_tilemap_area_selection()
        tb = self._toolbar()
        if tb is not None:
            tb.on_area_selected(False)
        if not defer_refresh and mw and hasattr(mw, '_save_map_and_refresh'):
            mw._save_map_and_refresh()

    def on_tilemap_release(self):
        pass

    def on_tilemap_hover(self, tile_x, tile_y):
        scene_rect  = self.tilemap_scene.sceneRect()
        max_tile_x  = int(scene_rect.width())  // 8 - 1
        max_tile_y  = int(scene_rect.height()) // 8 - 1

        if 0 <= tile_x <= max_tile_x and 0 <= tile_y <= max_tile_y:
            self.last_hover_pos = (tile_x, tile_y)
            self.main_window.hover_manager.update_hover(tile_x, tile_y, self.tilemap_view)
            self.update_status_bar(tile_x, tile_y)
        else:
            self.last_hover_pos = (-1, -1)
            self.main_window.hover_manager.hide_hover(self.tilemap_view)
            self.update_status_bar(-1, -1)

    def on_tilemap_leave(self):
        self.main_window.hover_manager.hide_hover(self.tilemap_view)
        self.last_hover_pos = (-1, -1)
        self.update_status_bar(-1, -1)

    def on_tilemap_shift(self, direction):
        if not self.tilemap_data:
            return

        w = self.tilemap_width
        h = self.tilemap_height
        is_cyclic = self.cyclic_checkbox.isChecked()
        EMPTY = b'\x00\x00'
        old_data = self.tilemap_data

        if w > 32:
            from core.final_assets import revert_gba_tilemap_reorganization
            linear = bytearray(revert_gba_tilemap_reorganization(self.tilemap_data, w, h, w, h))
        else:
            linear = bytearray(self.tilemap_data)

        def get(x, y):  return linear[(y * w + x) * 2 : (y * w + x) * 2 + 2]
        def set_(x, y, v): linear[(y * w + x) * 2 : (y * w + x) * 2 + 2] = v

        if direction == 'up':
            first_row = [bytes(get(x, 0)) for x in range(w)]
            for y in range(h - 1):
                for x in range(w):
                    set_(x, y, get(x, y + 1))
            for x in range(w):
                set_(x, h - 1, first_row[x] if is_cyclic else EMPTY)

        elif direction == 'down':
            last_row = [bytes(get(x, h - 1)) for x in range(w)]
            for y in range(h - 1, 0, -1):
                for x in range(w):
                    set_(x, y, get(x, y - 1))
            for x in range(w):
                set_(x, 0, last_row[x] if is_cyclic else EMPTY)

        elif direction == 'left':
            first_col = [bytes(get(0, y)) for y in range(h)]
            for x in range(w - 1):
                for y in range(h):
                    set_(x, y, get(x + 1, y))
            for y in range(h):
                set_(w - 1, y, first_col[y] if is_cyclic else EMPTY)

        elif direction == 'right':
            last_col = [bytes(get(w - 1, y)) for y in range(h)]
            for x in range(w - 1, 0, -1):
                for y in range(h):
                    set_(x, y, get(x - 1, y))
            for y in range(h):
                set_(0, y, last_col[y] if is_cyclic else EMPTY)

        if w > 32:
            from core.final_assets import reorganize_tilemap_for_gba_bg
            tile_list = []
            for i in range(w * h):
                entry = int.from_bytes(linear[i*2:i*2+2], 'little')
                tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))
            reorganized = reorganize_tilemap_for_gba_bg(tile_list, w * 8, h * 8)
            final = bytearray()
            for tile_id, hf, vf, pal in reorganized:
                e = (tile_id & 0x3FF) | (hf << 10) | (vf << 11) | (pal << 12)
                final.extend(e.to_bytes(2, 'little'))
            new_data = bytes(final)
        else:
            new_data = bytes(linear)

        self.tilemap_data = new_data

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_shift',
                editor_type='tiles',
                data={'old_data': old_data, 'new_data': new_data, 'w': w, 'h': h},
                description=self._tr('tilemap_shift_desc', direction=direction)
            )

        import os
        os.makedirs('output', exist_ok=True)
        with open('output/map.bin', 'wb') as f:
            f.write(new_data)

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data = new_data

        save_preview = keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

    def on_tilemap_resize(self):
        new_w = self.tilemap_width_spin.value()
        new_h = self.tilemap_height_spin.value()

        if not self.tilemap_data or (new_w == self.tilemap_width and new_h == self.tilemap_height):
            return

        is_rot = getattr(self.main_window, 'current_rotation_mode', False) if self.main_window else False
        if is_rot:
            if (new_w, new_h) not in ROT_SIZES_SET:
                chosen = self._ask_rotation_size(new_w, new_h)
                self.tilemap_width_spin.setValue(self.tilemap_width)
                self.tilemap_height_spin.setValue(self.tilemap_height)
                if chosen is None:
                    return
                new_w, new_h = chosen
                self.tilemap_width_spin.setValue(new_w)
                self.tilemap_height_spin.setValue(new_h)
            self._resize_rotation_tilemap(new_w, new_h)
            return

        old_w = self.tilemap_width
        old_h = self.tilemap_height
        old_data = self.tilemap_data

        save_preview = False
        keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview    = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        resize_performed = False
        final_new_w = new_w
        final_new_h = new_h
        final_new_data = None

        requires_gba_adjustment = False
        adjusted_w = new_w
        adjusted_h = new_h

        if new_w > 32:
            if new_w != 64:
                requires_gba_adjustment = True
                adjusted_w = 64
            if new_h % 32 != 0:
                requires_gba_adjustment = True
                adjusted_h = ((new_h + 31) // 32) * 32

        if requires_gba_adjustment:
            from ui.dialogs.gba_compatibility_dialog import GBACompatibilityDialog
            dlg = GBACompatibilityDialog(new_w, new_h, adjusted_w, adjusted_h, self)
            if exec_dialog(dlg):
                final_new_w = adjusted_w
                final_new_h = adjusted_h
                self.tilemap_width_spin.setValue(final_new_w)
                self.tilemap_height_spin.setValue(final_new_h)

                if final_new_w == old_w and final_new_h == old_h:
                    return

                if old_w > 32:
                    from core.final_assets import revert_gba_tilemap_reorganization
                    linear_old = revert_gba_tilemap_reorganization(old_data, old_w, old_h, old_w, old_h)
                else:
                    linear_old = old_data

                new_data = bytearray(b'\x00\x00' * (final_new_w * final_new_h))
                for y in range(min(old_h, final_new_h)):
                    for x in range(min(old_w, final_new_w)):
                        old_idx = y * old_w + x
                        new_idx = y * final_new_w + x
                        if old_idx < len(linear_old) // 2:
                            new_data[new_idx*2:new_idx*2+2] = linear_old[old_idx*2:old_idx*2+2]

                from core.final_assets import reorganize_tilemap_for_gba_bg
                tile_list = []
                for i in range(final_new_w * final_new_h):
                    entry  = int.from_bytes(new_data[i*2:i*2+2], 'little')
                    tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))

                reorganized = reorganize_tilemap_for_gba_bg(tile_list, final_new_w * 8, final_new_h * 8)

                final_data = bytearray()
                for tile_id, h_flip, v_flip, pal in reorganized:
                    entry = tile_id & 0x3FF
                    if h_flip: entry |= (1 << 10)
                    if v_flip: entry |= (1 << 11)
                    entry |= (pal << 12)
                    final_data.extend(entry.to_bytes(2, 'little'))

                final_new_data = bytes(final_data)
                resize_performed = True
            else:
                self.tilemap_width_spin.setValue(self.tilemap_width)
                self.tilemap_height_spin.setValue(self.tilemap_height)
                return

        elif self.tilemap_width > 32 and new_w <= 32:
            from core.final_assets import revert_gba_tilemap_reorganization
            final_new_data = revert_gba_tilemap_reorganization(
                self.tilemap_data, self.tilemap_width, self.tilemap_height, new_w, new_h
            )
            final_new_w = new_w
            final_new_h = new_h
            resize_performed = True

        else:
            min_w = min(new_w, old_w)
            min_h = min(new_h, old_h)
            new_data = bytearray()

            for y in range(min_h):
                start = y * old_w * 2
                new_data.extend(old_data[start : start + min_w * 2])
                if new_w > old_w:
                    new_data.extend(b'\x00\x00' * (new_w - old_w))

            if new_h > old_h:
                new_data.extend(b'\x00\x00' * new_w * (new_h - old_h))

            final_new_data = bytes(new_data)
            final_new_w = new_w
            final_new_h = new_h
            resize_performed = True

        if resize_performed and final_new_w > 32 and old_w <= 32 and not requires_gba_adjustment:
            min_w = min(old_w, final_new_w)
            min_h = min(old_h, final_new_h)
            linear_data = bytearray(b'\x00\x00' * (final_new_w * final_new_h))
            for y in range(min_h):
                for x in range(min_w):
                    old_idx = y * old_w + x
                    new_idx = y * final_new_w + x
                    if old_idx < len(old_data) // 2:
                        linear_data[new_idx*2:new_idx*2+2] = old_data[old_idx*2:old_idx*2+2]

            from core.final_assets import reorganize_tilemap_for_gba_bg
            tile_list = []
            for i in range(final_new_w * final_new_h):
                entry = int.from_bytes(linear_data[i*2:i*2+2], 'little')
                tile_list.append((entry & 0x3FF, (entry >> 10) & 1, (entry >> 11) & 1, (entry >> 12) & 0xF))

            reorganized = reorganize_tilemap_for_gba_bg(tile_list, final_new_w * 8, final_new_h * 8)

            final_data = bytearray()
            for tile_id, h_flip, v_flip, pal in reorganized:
                entry = tile_id & 0x3FF
                if h_flip: entry |= (1 << 10)
                if v_flip: entry |= (1 << 11)
                entry |= (pal << 12)
                final_data.extend(entry.to_bytes(2, 'little'))
            final_new_data = bytes(final_data)

        if not resize_performed:
            return

        self.tilemap_data   = final_new_data
        self.tilemap_width  = final_new_w
        self.tilemap_height = final_new_h
        self.tilemap_width_spin.setValue(final_new_w)
        self.tilemap_height_spin.setValue(final_new_h)

        import os
        os.makedirs('output', exist_ok=True)
        with open(os.path.join('output', 'map.bin'), 'wb') as f:
            f.write(final_new_data)

        if hasattr(self.main_window, 'config_manager'):
            self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(final_new_w))
            self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(final_new_h))

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data   = final_new_data
                other.tilemap_width  = final_new_w
                other.tilemap_height = final_new_h
                other.tilemap_width_spin.setValue(final_new_w)
                other.tilemap_height_spin.setValue(final_new_h)

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_resize',
                editor_type='palettes',
                data={
                    'old_w': old_w, 'old_h': old_h,
                    'new_w': final_new_w, 'new_h': final_new_h,
                    'old_data': old_data, 'new_data': final_new_data
                },
                description=self._tr('tilemap_resize_desc', old_w=old_w, old_h=old_h, new_w=final_new_w, new_h=final_new_h)
            )

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)

        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

    def build_tilemap_toolbar(self):
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_frame.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }"
        )
        controls_frame.setFixedHeight(28)

        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(1)
        controls_layout.setContentsMargins(3, 3, 3, 3)

        row = QHBoxLayout()
        row.setSpacing(3)
        row.setContentsMargins(0, 0, 0, 0)
        row.setAlignment(Qt.AlignLeft)

        def _label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("QLabel { border: none; }")
            return lbl

        self._toolbar_width_label = _label(self._tr("tilemap_width_label"))
        row.addWidget(self._toolbar_width_label)
        self.tilemap_width_spin = QSpinBox()
        self.tilemap_width_spin.setRange(1, 999)
        self.tilemap_width_spin.setValue(32)
        self.tilemap_width_spin.setFixedWidth(45)
        self.tilemap_width_spin.setFixedHeight(18)
        self.tilemap_width_spin.setStyleSheet("QSpinBox { font-size: 8pt; }")
        row.addWidget(self.tilemap_width_spin)

        self._toolbar_height_label = _label(self._tr("tilemap_height_label"))
        row.addWidget(self._toolbar_height_label)
        self.tilemap_height_spin = QSpinBox()
        self.tilemap_height_spin.setRange(1, 999)
        self.tilemap_height_spin.setValue(32)
        self.tilemap_height_spin.setFixedWidth(45)
        self.tilemap_height_spin.setFixedHeight(18)
        self.tilemap_height_spin.setStyleSheet("QSpinBox { font-size: 8pt; }")
        row.addWidget(self.tilemap_height_spin)

        self.resize_button = QPushButton(self._tr("tilemap_resize_btn"))
        self.resize_button.setFixedWidth(100)
        self.resize_button.setFixedHeight(20)
        self.resize_button.setStyleSheet("QPushButton { font-size: 8pt; padding: 0px; }")
        self.resize_button.clicked.connect(self._on_resize_clicked)
        row.addWidget(self.resize_button)
        btn_style = "QPushButton { font-weight: bold; padding: 0px; font-size: 7pt; }"
        self.btn_up    = QPushButton("↑")
        self.btn_left  = QPushButton("←")
        self.btn_right = QPushButton("→")
        self.btn_down  = QPushButton("↓")
        for btn in (self.btn_up, self.btn_left, self.btn_right, self.btn_down):
            btn.setFixedSize(20, 20)
            btn.setStyleSheet(btn_style)

        self.btn_up.clicked.connect(lambda: self.on_tilemap_shift("up"))
        self.btn_down.clicked.connect(lambda: self.on_tilemap_shift("down"))
        self.btn_left.clicked.connect(lambda: self.on_tilemap_shift("left"))
        self.btn_right.clicked.connect(lambda: self.on_tilemap_shift("right"))

        self.move_label = QLabel(self._tr("tilemap_move_label"))
        self.move_label.setStyleSheet("QLabel { border: none; }")

        row.addWidget(self.btn_left)
        row.addWidget(self.btn_up)
        row.addWidget(self.move_label)
        row.addWidget(self.btn_down)
        row.addWidget(self.btn_right)

        self.cyclic_checkbox = QCheckBox(self._tr("tilemap_cyclic_shift"))
        self.cyclic_checkbox.setStyleSheet("QCheckBox { font-size: 8pt; }")
        self.cyclic_checkbox.setFixedHeight(18)
        row.addWidget(self.cyclic_checkbox)

        controls_layout.addLayout(row)

        self.tilemap_width_spin.valueChanged.connect(self._update_crop_mask)
        self.tilemap_height_spin.valueChanged.connect(self._update_crop_mask)

        self._set_tilemap_controls_enabled(False)
        return controls_frame

    def _update_crop_mask(self):
        self._clear_crop_mask()
        if not getattr(self, 'tilemap_data', None) or not getattr(self, 'tilemap_width', 0) or not getattr(self, 'tilemap_height', 0):
            return
        new_w = self.tilemap_width_spin.value()
        new_h = self.tilemap_height_spin.value()
        cur_w = self.tilemap_width
        cur_h = self.tilemap_height
        if new_w >= cur_w and new_h >= cur_h:
            return

        mask_color = QColor(220, 50, 50, 100)
        no_pen = QPen(Qt.NoPen)
        self._crop_mask_items = []
        scene = self.tilemap_scene
        if new_w < cur_w:
            x = new_w * 8
            w = (cur_w - new_w) * 8
            h = min(new_h, cur_h) * 8
            if h > 0:
                item = scene.addRect(x, 0, w, h, no_pen, QBrush(mask_color))
                item.setZValue(150)
                self._crop_mask_items.append(item)
        if new_h < cur_h:
            y = new_h * 8
            w = cur_w * 8
            h = (cur_h - new_h) * 8
            item = scene.addRect(0, y, w, h, no_pen, QBrush(mask_color))
            item.setZValue(150)
            self._crop_mask_items.append(item)
        self.tilemap_view.viewport().update()

    def _clear_crop_mask(self):
        for item in getattr(self, '_crop_mask_items', []):
            try:
                if item.scene():
                    self.tilemap_scene.removeItem(item)
            except RuntimeError:
                pass
        self._crop_mask_items = []

    def _on_resize_clicked(self):
        self._clear_crop_mask()
        self.on_tilemap_resize()

    def retranslate_tilemap_toolbar(self):
        self._toolbar_width_label.setText(self._tr("tilemap_width_label"))
        self._toolbar_height_label.setText(self._tr("tilemap_height_label"))
        self.resize_button.setText(self._tr("tilemap_resize_btn"))
        self.move_label.setText(self._tr("tilemap_move_label"))
        self.cyclic_checkbox.setText(self._tr("tilemap_cyclic_shift"))

    def _set_tilemap_controls_enabled(self, enabled: bool):
        for widget in (
            self.tilemap_width_spin, self.tilemap_height_spin,
            self.resize_button,
            self.btn_up, self.btn_down, self.btn_left, self.btn_right,
            self.cyclic_checkbox,
        ):
            widget.setEnabled(enabled)
        if not enabled:
            self._clear_crop_mask()

    def enable_tilemap_controls(self):
        self._set_tilemap_controls_enabled(True)

    def _ask_rotation_size(self, attempted_w, attempted_h):

        dlg = QDialog(self.main_window if self.main_window else None)
        dlg.setWindowTitle(self._tr("invalid_rot_size_title_dialog"))
        dlg.setFixedWidth(320)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(
            self._tr("invalid_rot_size_message", w=attempted_w, h=attempted_h)
        ))
        lst = QListWidget()
        labels = ["16×16 (128×128 px)", "32×32 (256×256 px)",
                  "64×64 (512×512 px)", "128×128 (1024×1024 px)"]
        for lbl in labels:
            lst.addItem(lbl)
        lst.setCurrentRow(0)
        layout.addWidget(lst)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        if exec_dialog(dlg) != QDialog.Accepted:
            return None
        return ROT_SIZES[lst.currentRow()]

    def _resize_rotation_tilemap(self, new_w, new_h):
        old_w, old_h = self.tilemap_width, self.tilemap_height
        old_data = self.tilemap_data

        new_data = bytearray(new_w * new_h)
        for y in range(min(old_h, new_h)):
            for x in range(min(old_w, new_w)):
                new_data[y * new_w + x] = old_data[y * old_w + x]

        new_data = bytes(new_data)
        self.tilemap_data  = new_data
        self.tilemap_width  = new_w
        self.tilemap_height = new_h
        self.tilemap_width_spin.setValue(new_w)
        self.tilemap_height_spin.setValue(new_h)

        import os
        os.makedirs('output', exist_ok=True)
        with open(os.path.join('output', 'map.bin'), 'wb') as f:
            f.write(new_data)

        if hasattr(self.main_window, 'config_manager'):
            self.main_window.config_manager.set('CONVERSION', 'tilemap_width',  str(new_w))
            self.main_window.config_manager.set('CONVERSION', 'tilemap_height', str(new_h))

        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            other = getattr(self.main_window, attr, None)
            if other and other is not self:
                other.tilemap_data   = new_data
                other.tilemap_width  = new_w
                other.tilemap_height = new_h
                other.tilemap_width_spin.setValue(new_w)
                other.tilemap_height_spin.setValue(new_h)

        if hasattr(self.main_window, 'history_manager'):
            self.main_window.history_manager.record_state(
                state_type='tilemap_resize', editor_type='tiles',
                data={'old_w': old_w, 'old_h': old_h,
                      'new_w': new_w, 'new_h': new_h,
                      'old_data': old_data, 'new_data': new_data},
                description=self._tr('tilemap_resize_desc', old_w=old_w, old_h=old_h, new_w=new_w, new_h=new_h)
            )

        save_preview = keep_transparent = False
        if hasattr(self.main_window, 'config_manager'):
            save_preview     = self.main_window.config_manager.getboolean('SETTINGS', 'save_preview_files', False)
            keep_transparent = self.main_window.config_manager.getboolean('SETTINGS', 'keep_transparent_color', False)

        from core.image_utils import create_gbagfx_preview
        result = create_gbagfx_preview(save_preview=save_preview, keep_transparent=keep_transparent)
        if result and hasattr(self.main_window, 'refresh_preview_display'):
            self.main_window.refresh_preview_display()

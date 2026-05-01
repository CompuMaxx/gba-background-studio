# ui/main_window/toolbar.py
import os
from ui.qt_compat import (
    QFrame,
    QHBoxLayout,
    QToolButton,
    QWidget,
    QTabBar,
    QIcon,
    QKeySequence,
    QPixmap,
    QCursor,
    Qt,
    QSize
)

def _icon(name):
    path = os.path.join("assets", "toolbar", f"{name}.svg")
    return QIcon(path) if os.path.exists(path) else QIcon()

def _cursor_from_svg(name, size=24, hotspot=(0, 0)):
    path = os.path.join("assets", "toolbar", f"{name}.svg")
    if not os.path.exists(path):
        return Qt.ArrowCursor
    px = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return QCursor(px, hotspot[0], hotspot[1])

def _btn(icon_name, tooltip_key, checkable=False, shortcut=None, translator=None):
    b = QToolButton()
    b.setIcon(_icon(icon_name))
    b.setIconSize(QSize(16, 16))
    b.setFixedSize(24, 24)
    _tr = translator.tr if translator else lambda k, **kw: k
    b.setToolTip(_tr(tooltip_key))
    b.setCheckable(checkable)
    b.setAutoRaise(True)
    if shortcut:
        b.setShortcut(QKeySequence(shortcut))
    return b

def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFrameShadow(QFrame.Sunken)
    f.setFixedWidth(5)
    return f

def _make_group(buttons_and_seps):
    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(2, 0, 2, 0)
    row.setSpacing(2)
    for item in buttons_and_seps:
        row.addWidget(item)
    w.adjustSize()
    return w

class ContextToolbar:
    def __init__(self, main_window, tab_widget):
        self.main_window = main_window
        self._tab_widget = tab_widget
        self._tr = main_window.translator.tr if hasattr(main_window, 'translator') else lambda k, **kw: k

        self.btn_select_rect  = _btn("select_rect", "toolbar_select_area",  checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_copy         = _btn("copy",        "toolbar_copy",         shortcut="Ctrl+C", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_cut          = _btn("cut",         "toolbar_cut",          shortcut="Ctrl+X", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_paste        = _btn("paste",       "toolbar_paste",        shortcut="Ctrl+V", checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_flip_h       = _btn("flip_h",      "toolbar_flip_h", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_flip_v       = _btn("flip_v",      "toolbar_flip_v", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_mirror_h     = _btn("mirror_h",    "toolbar_mirror_h", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_mirror_v     = _btn("mirror_v",    "toolbar_mirror_v", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_swap_h       = _btn("swap_h",      "toolbar_swap_h", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_swap_v       = _btn("swap_v",      "toolbar_swap_v", translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        for b in (self.btn_select_rect,
                  self.btn_copy, self.btn_cut, self.btn_paste,
                  self.btn_flip_h, self.btn_flip_v,
                  self.btn_mirror_h, self.btn_mirror_v,
                  self.btn_swap_h, self.btn_swap_v):
            b.setChecked(False)
            b.setEnabled(False)

        self.btn_select_rect.toggled.connect(self._on_select_rect_toggled)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        self.btn_cut.clicked.connect(self._on_cut_clicked)
        self.btn_flip_h.clicked.connect(lambda: self._on_transform_clicked('flip_h'))
        self.btn_flip_v.clicked.connect(lambda: self._on_transform_clicked('flip_v'))
        self.btn_mirror_h.clicked.connect(lambda: self._on_transform_clicked('mirror_h'))
        self.btn_mirror_v.clicked.connect(lambda: self._on_transform_clicked('mirror_v'))
        self.btn_swap_h.clicked.connect(lambda: self._on_transform_clicked('swap_h'))
        self.btn_swap_v.clicked.connect(lambda: self._on_transform_clicked('swap_v'))

        self._tiles = _make_group([
            self.btn_select_rect, _sep(),
            self.btn_copy, self.btn_cut, self.btn_paste, _sep(),
            self.btn_flip_h, self.btn_flip_v, _sep(),
            self.btn_mirror_h, self.btn_mirror_v, _sep(),
            self.btn_swap_h, self.btn_swap_v,
        ])

        self.btn_pencil_pal  = _btn("wand",        "toolbar_select_tiles", checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_fill        = _btn("fill",        "toolbar_fill",        checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_pal_replace = _btn("pal_replace", "toolbar_pal_replace", checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_pal_swap    = _btn("swap",        "toolbar_pal_swap",    checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_pal_select_rect = _btn("select_rect", "toolbar_select_area", checkable=True, translator=self.main_window.translator if hasattr(main_window, 'translator') else None)
        self.btn_pencil_pal.setChecked(True)
        for b in (self.btn_pal_select_rect, self.btn_pencil_pal, self.btn_fill,
                  self.btn_pal_replace, self.btn_pal_swap):
            b.setChecked(False)
            b.setEnabled(False)

        self.btn_pal_select_rect.toggled.connect(self._on_pal_select_rect_toggled)
        self.btn_pencil_pal.toggled.connect(lambda c: self._on_pal_mode(self.btn_pencil_pal, self.btn_fill, c))
        self.btn_fill.toggled.connect(lambda c: self._on_pal_mode(self.btn_fill, self.btn_pencil_pal, c))
        self.btn_pal_replace.toggled.connect(self._on_pal_replace_toggled)
        self.btn_pal_swap.toggled.connect(self._on_pal_swap_toggled)

        self._palettes = _make_group([
            self.btn_pal_select_rect,
            self.btn_pencil_pal, self.btn_fill, _sep(),
            self.btn_pal_replace, self.btn_pal_swap,
        ])

        self._placeholder = QWidget()
        tab_widget.addTab(self._placeholder, "")
        self._placeholder_index = tab_widget.count() - 1
        tab_bar = tab_widget.tabBar()

        self._tiles.setParent(tab_bar)
        self._palettes.setParent(tab_bar)
        self._tiles.hide()
        self._palettes.hide()
        tab_bar.setTabButton(self._placeholder_index, QTabBar.LeftSide, self._tiles)

        self._tab_bar = tab_bar
        self._tab_bar.setTabVisible(self._placeholder_index, False)

    def retranslate_ui(self):
        tr = self.main_window.translator.tr
        self.btn_select_rect.setToolTip(tr("toolbar_select_area"))
        self.btn_copy.setToolTip(tr("toolbar_copy"))
        self.btn_cut.setToolTip(tr("toolbar_cut"))
        self.btn_paste.setToolTip(tr("toolbar_paste"))
        self.btn_flip_h.setToolTip(tr("toolbar_flip_h"))
        self.btn_flip_v.setToolTip(tr("toolbar_flip_v"))
        self.btn_mirror_h.setToolTip(tr("toolbar_mirror_h"))
        self.btn_mirror_v.setToolTip(tr("toolbar_mirror_v"))
        self.btn_swap_h.setToolTip(tr("toolbar_swap_h"))
        self.btn_swap_v.setToolTip(tr("toolbar_swap_v"))
        self.btn_pencil_pal.setToolTip(tr("toolbar_select_tiles"))
        self.btn_fill.setToolTip(tr("toolbar_fill"))
        self.btn_pal_replace.setToolTip(tr("toolbar_pal_replace"))
        self.btn_pal_swap.setToolTip(tr("toolbar_pal_swap"))
        self.btn_pal_select_rect.setToolTip(tr("toolbar_select_area"))

    def _rotation_mode(self):
        return getattr(self.main_window, 'current_rotation_mode', False)

    def _is_8bpp(self):
        return getattr(self.main_window, 'current_bpp', 4) == 8

    def _selected_palette_count(self):
        try:
            s = self.main_window.config_manager.get('CONVERSION', 'selected_palettes', '0')
            return len([p for p in s.split(',') if p.strip()])
        except Exception:
            return 1

    def on_tileset_loaded(self):
        et = getattr(self.main_window, 'edit_tiles_tab', None)
        has_tilemap = et is not None and bool(getattr(et, 'tilemap_data', None))
        self.btn_select_rect.setEnabled(has_tilemap)

    def on_tileset_unloaded(self):
        for b in (self.btn_select_rect,
                  self.btn_copy, self.btn_cut, self.btn_paste,
                  self.btn_flip_h, self.btn_flip_v,
                  self.btn_mirror_h, self.btn_mirror_v,
                  self.btn_swap_h, self.btn_swap_v):
            b.setEnabled(False)
            if b.isCheckable():
                b.setChecked(False)

    def on_palette_loaded(self):
        et = getattr(self.main_window, 'edit_tiles_tab', None)
        has_tilemap = et is not None and bool(getattr(et, 'tilemap_data', None))
        rot = self._rotation_mode()
        bpp8 = self._is_8bpp()
        enabled = has_tilemap and not rot and not bpp8
        self.btn_pal_select_rect.setEnabled(has_tilemap)
        for b in (self.btn_pencil_pal, self.btn_fill):
            b.setEnabled(enabled)

    def on_palette_unloaded(self):
        for b in (self.btn_pal_select_rect, self.btn_pencil_pal, self.btn_fill,
                  self.btn_pal_replace, self.btn_pal_swap):
            b.setEnabled(False)
            if b.isCheckable():
                b.setChecked(False)

    def show_for_tab(self, index):
        tab = self._active_tab()
        if tab is not None and getattr(getattr(tab, 'tilemap_view', None), 'paste_mode', False):
            tab._cancel_paste()
        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            tab = getattr(self.main_window, attr, None)
            if tab is not None:
                tab._clear_tilemap_selection()
                tab.set_area_selection_mode(False)
                if hasattr(tab, '_clear_pal_selection'):
                    tab._clear_pal_selection()
        self.on_area_selected(False)
        for b in (self.btn_select_rect, self.btn_pal_select_rect,
                  self.btn_pencil_pal, self.btn_fill):
            b.blockSignals(True)
            b.setChecked(False)
            b.blockSignals(False)
        self.btn_pal_replace.setEnabled(False)
        self.btn_pal_swap.setEnabled(False)
        for attr in ('edit_tiles_tab', 'edit_palettes_tab'):
            tab = getattr(self.main_window, attr, None)
            if tab is not None:
                view = getattr(tab, 'tilemap_view', None)
                if view is not None:
                    view.viewport().setCursor(Qt.ArrowCursor)
        if index == 1:
            self._tab_bar.setTabVisible(self._placeholder_index, True)
            self._tab_bar.setTabButton(self._placeholder_index, QTabBar.LeftSide, self._tiles)
            self._tiles.show()
            self._palettes.hide()
            self.on_tileset_loaded()
        elif index == 2:
            self._tab_bar.setTabVisible(self._placeholder_index, True)
            self._tab_bar.setTabButton(self._placeholder_index, QTabBar.LeftSide, self._palettes)
            self._palettes.show()
            self._tiles.hide()
            self.on_palette_loaded()
        else:
            self._tiles.hide()
            self._palettes.hide()
            self._tab_bar.setTabVisible(self._placeholder_index, False)

    def on_tile_selected(self, has_selection: bool):
        for b in (self.btn_copy, self.btn_cut, self.btn_flip_h, self.btn_flip_v):
            b.setEnabled(has_selection)

    def on_area_selected(self, has_selection: bool):
        rot = self._rotation_mode()
        for b in (self.btn_copy, self.btn_cut):
            b.setEnabled(has_selection)
        for b in (self.btn_flip_h, self.btn_flip_v,
                  self.btn_mirror_h, self.btn_mirror_v,
                  self.btn_swap_h, self.btn_swap_v):
            b.setEnabled(has_selection and not rot)
        if self._tab_widget.currentIndex() == 2:
            self.btn_pal_replace.setEnabled(has_selection)
            swap_ok = False
            if has_selection and self._selected_palette_count() > 1:
                tab = self._active_tab()
                if tab is not None and getattr(tab, '_tilemap_sel_area', None) is not None:
                    x1, y1, x2, y2 = tab._tilemap_sel_area
                    from collections import Counter
                    counts = Counter()
                    for ty in range(y1, y2 + 1):
                        for tx in range(x1, x2 + 1):
                            idx = tab._tilemap_index(tx, ty)
                            if idx * 2 + 2 > len(tab.tilemap_data):
                                continue
                            entry = tab.tilemap_data[idx * 2] | (tab.tilemap_data[idx * 2 + 1] << 8)
                            counts[(entry >> 12) & 0xF] += 1
                    if len(counts) == 1:
                        pal_id = next(iter(counts))
                        area_count = counts[pal_id]
                        total = sum(
                            1 for ty in range(tab.tilemap_height)
                            for tx in range(tab.tilemap_width)
                            if ((tab.tilemap_data[tab._tilemap_index(tx, ty) * 2] |
                                 (tab.tilemap_data[tab._tilemap_index(tx, ty) * 2 + 1] << 8)) >> 12) & 0xF == pal_id
                        )
                        swap_ok = area_count == total
            self.btn_pal_swap.setEnabled(swap_ok)
        
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.menu_bar.action_save_selection.setEnabled(has_selection)

    def on_pal_selection_changed(self, has_selection: bool):
        mode_active = self.btn_pencil_pal.isChecked() or self.btn_fill.isChecked()
        replace_ok = mode_active and has_selection
        swap_ok = False
        if replace_ok and self._selected_palette_count() > 1:
            tab = self._active_tab()
            if tab is not None:
                sel_count = len(getattr(tab, '_pal_sel_items', []))
                pal_id = getattr(tab, '_pal_sel_palette_id', -1)
                total = 0
                if pal_id >= 0 and getattr(tab, 'tilemap_data', None):
                    get_idx = (tab._tilemap_index if hasattr(tab, '_tilemap_index')
                               else lambda x, y: y * tab.tilemap_width + x)
                    for ty in range(tab.tilemap_height):
                        for tx in range(tab.tilemap_width):
                            idx = get_idx(tx, ty)
                            if idx * 2 + 2 > len(tab.tilemap_data):
                                continue
                            entry = tab.tilemap_data[idx * 2] | (tab.tilemap_data[idx * 2 + 1] << 8)
                            if (entry >> 12) & 0xF == pal_id:
                                total += 1
                swap_ok = sel_count == total
        self.btn_pal_replace.setEnabled(replace_ok)
        self.btn_pal_swap.setEnabled(swap_ok)

    def _active_tab(self):
        idx = self._tab_widget.currentIndex()
        if idx == 1:
            return getattr(self.main_window, 'edit_tiles_tab', None)
        if idx == 2:
            return getattr(self.main_window, 'edit_palettes_tab', None)
        return None

    def _set_tilemap_cursor(self, cursor):
        tab = self._active_tab()
        if tab is None:
            return
        view = getattr(tab, 'tilemap_view', None)
        if view is not None:
            view.viewport().setCursor(cursor)

    def _on_pal_select_rect_toggled(self, checked):
        if checked:
            for b in (self.btn_pencil_pal, self.btn_fill):
                b.blockSignals(True)
                b.setChecked(False)
                b.blockSignals(False)
            tab = self._active_tab()
            if tab is not None and hasattr(tab, '_clear_pal_selection'):
                tab._clear_pal_selection()
            self.btn_pal_replace.setEnabled(False)
            self.btn_pal_swap.setEnabled(False)
        tab = self._active_tab()
        if tab is not None:
            tab.set_area_selection_mode(checked)
        if not checked:
            self.on_area_selected(False)
        self._set_tilemap_cursor(Qt.CrossCursor if checked else Qt.ArrowCursor)

    def _on_transform_clicked(self, op):
        tab = self._active_tab()
        if tab is not None and hasattr(tab, '_apply_transform'):
            tab._apply_transform(op)

    def on_paste_mode_active(self, active: bool):
        if active:
            self.btn_paste.setEnabled(True)
            self.btn_paste.setChecked(True)
            for b in (self.btn_select_rect, self.btn_copy, self.btn_cut,
                      self.btn_flip_h, self.btn_flip_v,
                      self.btn_mirror_h, self.btn_mirror_v,
                      self.btn_swap_h, self.btn_swap_v):
                b.setEnabled(False)
        else:
            self.btn_paste.setChecked(False)
            self.btn_paste.setEnabled(False)
            self.on_tileset_loaded()
            self.btn_select_rect.blockSignals(True)
            self.btn_select_rect.setChecked(True)
            self.btn_select_rect.blockSignals(False)
            tab = self._active_tab()
            if tab is not None:
                tab.set_area_selection_mode(True)
            self._set_tilemap_cursor(Qt.CrossCursor)

    def _on_copy_clicked(self):
        tab = self._active_tab()
        if tab is not None and hasattr(tab, '_copy_selection'):
            tab._copy_selection(is_cut=False)

    def _on_cut_clicked(self):
        tab = self._active_tab()
        if tab is not None and hasattr(tab, '_copy_selection'):
            tab._copy_selection(is_cut=True)

    def _on_select_rect_toggled(self, checked):
        tab = self._active_tab()
        if tab is not None:
            tab.set_area_selection_mode(checked)
        if not checked:
            self.on_area_selected(False)
        self._set_tilemap_cursor(Qt.CrossCursor if checked else Qt.ArrowCursor)

    def _on_pal_mode(self, active_btn, other_btn, checked):
        if checked:
            other_btn.blockSignals(True)
            other_btn.setChecked(False)
            other_btn.blockSignals(False)
            self.btn_pal_select_rect.blockSignals(True)
            self.btn_pal_select_rect.setChecked(False)
            self.btn_pal_select_rect.blockSignals(False)
            tab = self._active_tab()
            if tab is not None:
                tab.set_area_selection_mode(False)
            self._set_tilemap_cursor(Qt.ArrowCursor)
        if not checked and active_btn in (self.btn_pencil_pal, self.btn_fill):
            tab = self._active_tab()
            if tab is not None and hasattr(tab, '_clear_pal_selection'):
                tab._clear_pal_selection()
        if not (self.btn_pencil_pal.isChecked() or self.btn_fill.isChecked()):
            self.btn_pal_replace.setEnabled(False)
            self.btn_pal_swap.setEnabled(False)
        if self.btn_pencil_pal.isChecked():
            self._set_tilemap_cursor(_cursor_from_svg('wand'))
        elif self.btn_fill.isChecked():
            self._set_tilemap_cursor(_cursor_from_svg('fill'))
        else:
            self._set_tilemap_cursor(Qt.ArrowCursor)

    def _on_pal_replace_toggled(self, checked):
        if checked and self.btn_pal_swap.isChecked():
            self.btn_pal_swap.blockSignals(True)
            self.btn_pal_swap.setChecked(False)
            self.btn_pal_swap.blockSignals(False)
        if checked:
            tab = self._active_tab()
            if tab is not None and hasattr(tab, '_apply_pal_replace'):
                tab._apply_pal_replace()
            self.btn_pal_replace.blockSignals(True)
            self.btn_pal_replace.setChecked(False)
            self.btn_pal_replace.blockSignals(False)

    def _on_pal_swap_toggled(self, checked):
        if checked and self.btn_pal_replace.isChecked():
            self.btn_pal_replace.blockSignals(True)
            self.btn_pal_replace.setChecked(False)
            self.btn_pal_replace.blockSignals(False)
        if checked:
            tab = self._active_tab()
            if tab is not None and hasattr(tab, '_apply_pal_swap'):
                tab._apply_pal_swap()
            self.btn_pal_swap.blockSignals(True)
            self.btn_pal_swap.setChecked(False)
            self.btn_pal_swap.blockSignals(False)

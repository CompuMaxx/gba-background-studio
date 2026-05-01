# ui/main_window/view_ops.py
from ui.qt_compat import Qt, QGraphicsView

def setup_wheel_events(main_window):
    main_window.preview_tab.preview_image_view.wheelEvent = lambda event: zoom_wheel_event(main_window, main_window.preview_tab.preview_image_view, event)
    main_window.edit_tiles_tab.edit_tileset_view.wheelEvent = lambda event: zoom_wheel_event(main_window, main_window.edit_tiles_tab.edit_tileset_view, event)
    main_window.edit_tiles_tab.edit_tilemap_view.wheelEvent = lambda event: zoom_wheel_event(main_window, main_window.edit_tiles_tab.edit_tilemap_view, event)
    main_window.edit_palettes_tab.edit_tilemap2_view.wheelEvent = lambda event: zoom_wheel_event(main_window, main_window.edit_palettes_tab.edit_tilemap2_view, event)

def zoom_wheel_event(main_window, view, event):
    if not main_window.output_loaded_for_zoom:
        QGraphicsView.wheelEvent(view, event)
        return
    
    if event.modifiers() & Qt.ControlModifier:
        if event.angleDelta().y() > 0:
            zoom_in(main_window)
        else:
            zoom_out(main_window)
        event.accept()
        
        from .tab_ops import update_hover_from_current_cursor
        update_hover_from_current_cursor(main_window)
    else:
        QGraphicsView.wheelEvent(view, event)

def reset_zoom(main_window):
    main_window.current_zoom_index = 0
    main_window.zoom_level = main_window.zoom_levels[main_window.current_zoom_index]
    apply_zoom_to_all(main_window)
    from .tab_ops import update_hover_from_current_cursor
    update_hover_from_current_cursor(main_window)

def zoom_in(main_window):
    if not main_window.output_loaded_for_zoom:
        return
    if main_window.current_zoom_index < len(main_window.zoom_levels) - 1:
        main_window.current_zoom_index += 1
        main_window.zoom_level = main_window.zoom_levels[main_window.current_zoom_index]
        apply_zoom_to_all(main_window)
        from .tab_ops import update_hover_from_current_cursor
        update_hover_from_current_cursor(main_window)

def zoom_out(main_window):
    if not main_window.output_loaded_for_zoom:
        return
    if main_window.current_zoom_index > 0:
        main_window.current_zoom_index -= 1
        main_window.zoom_level = main_window.zoom_levels[main_window.current_zoom_index]
        apply_zoom_to_all(main_window)
        from .tab_ops import update_hover_from_current_cursor
        update_hover_from_current_cursor(main_window)

def apply_zoom_to_all(main_window):
    zoom_factor = main_window.zoom_level / 100.0

    apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, zoom_factor)
    apply_zoom_to_view(main_window, main_window.edit_tiles_tab.edit_tileset_view, zoom_factor)
    apply_zoom_to_view(main_window, main_window.edit_tiles_tab.edit_tilemap_view, zoom_factor)
    main_window.edit_palettes_tab.apply_zoom(zoom_factor)
    apply_zoom_to_view(main_window, main_window.edit_palettes_tab.edit_tilemap2_view, zoom_factor)

    from .tab_ops import update_hover_from_current_cursor
    update_hover_from_current_cursor(main_window)

    current_tab = main_window.main_tabs.currentWidget()

    if current_tab == main_window.preview_tab:
        main_window.custom_status_bar.update_status(
            selection_type="Tile",
            selection_id="-",
            tilemap_pos=(-1, -1),
            tile_id="-",
            palette_id="-",
            flip_state="None",
            zoom_level=main_window.zoom_level
        )
    elif current_tab == main_window.edit_tiles_tab:
        main_window.edit_tiles_tab.update_status_bar(*main_window.edit_tiles_tab.last_hover_pos)
    elif current_tab == main_window.edit_palettes_tab:
        main_window.edit_palettes_tab.update_status_bar(*main_window.edit_palettes_tab.last_hover_pos)

def apply_zoom_to_view(main_window, view, zoom_factor):
    if view and view.scene() and view.scene().items():
        h_bar = view.horizontalScrollBar()
        v_bar = view.verticalScrollBar()
        h_range = h_bar.maximum() - h_bar.minimum()
        v_range = v_bar.maximum() - v_bar.minimum()
        h_frac = (h_bar.value() - h_bar.minimum()) / h_range if h_range > 0 else 0.5
        v_frac = (v_bar.value() - v_bar.minimum()) / v_range if v_range > 0 else 0.5
        has_scroll = h_range > 0 or v_range > 0

        view.resetTransform()
        view.scale(zoom_factor, zoom_factor)
        if not has_scroll:
            view.centerOn(view.scene().items()[0])
        else:
            new_h_range = view.horizontalScrollBar().maximum() - view.horizontalScrollBar().minimum()
            new_v_range = view.verticalScrollBar().maximum() - view.verticalScrollBar().minimum()
            view.horizontalScrollBar().setValue(int(view.horizontalScrollBar().minimum() + h_frac * new_h_range))
            view.verticalScrollBar().setValue(int(view.verticalScrollBar().minimum() + v_frac * new_v_range))
        
        if (main_window.grid_manager.is_grid_visible() and 
            _is_editor_view(main_window, view)):
            view_name = _get_view_name(main_window, view)
            if view_name:
                main_window.grid_manager.update_grid_for_view(view_name)
        
        if view == main_window.edit_tiles_tab.edit_tileset_view:
            if hasattr(main_window.edit_tiles_tab, 'selected_tile_pos') and main_window.edit_tiles_tab.selected_tile_pos != (-1, -1):
                tile_x, tile_y = main_window.edit_tiles_tab.selected_tile_pos
                main_window.edit_tiles_tab.highlight_selected_tile(tile_x, tile_y)

def _is_editor_view(main_window, view):
    editor_views = [
        main_window.edit_tiles_tab.edit_tileset_view,
        main_window.edit_tiles_tab.edit_tilemap_view,
        main_window.edit_palettes_tab.full_palette_view,
        main_window.edit_palettes_tab.edit_tilemap2_view
    ]
    return view in editor_views

def _get_view_name(main_window, view):
    if view == main_window.edit_tiles_tab.edit_tileset_view:
        return "tileset"
    elif view == main_window.edit_tiles_tab.edit_tilemap_view:
        return "tilemap_edit"
    elif view == main_window.edit_palettes_tab.full_palette_view:
        return "palettes"
    elif view == main_window.edit_palettes_tab.edit_tilemap2_view:
        return "tilemap_palettes"
    return None

def apply_zoom_to_new_content(main_window, view):
    if view:
        apply_zoom_to_view(main_window, view, main_window.zoom_level / 100.0)

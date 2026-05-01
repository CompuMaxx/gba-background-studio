# ui/main_window/tab_ops.py
import os
from PIL import Image as PilImage
from ui.shared_utils import pil_to_qimage
from core.palette_utils import generate_grayscale_palette
from ui.qt_compat import QPixmap

def on_tab_changed(main_window, index):
    if hasattr(main_window, 'context_toolbar'):
        if index == main_window.context_toolbar._placeholder_index:
            prev = getattr(main_window, '_last_tab_index', 0)
            main_window.main_tabs.blockSignals(True)
            main_window.main_tabs.setCurrentIndex(prev)
            main_window.main_tabs.blockSignals(False)
            return
    main_window._last_tab_index = index

    current_tab = main_window.main_tabs.widget(index)
    
    if hasattr(main_window, 'edit_tiles_tab') and hasattr(main_window.edit_tiles_tab, 'edit_tilemap_view'):
        main_window.hover_manager.hide_hover(main_window.edit_tiles_tab.edit_tilemap_view)
    if hasattr(main_window, 'edit_palettes_tab') and hasattr(main_window.edit_palettes_tab, 'edit_tilemap2_view'):
        main_window.hover_manager.hide_hover(main_window.edit_palettes_tab.edit_tilemap2_view)
    
    if hasattr(main_window, 'context_toolbar'):
        main_window.context_toolbar.show_for_tab(index)

    if current_tab == main_window.edit_tiles_tab:
        if hasattr(main_window.edit_tiles_tab, 'sync_splitter_on_tab_change'):
            main_window.edit_tiles_tab.sync_splitter_on_tab_change()
        update_hover_from_current_cursor(main_window)
        main_window.edit_tiles_tab.update_status_bar(-1, -1)
    elif current_tab == main_window.edit_palettes_tab:
        if hasattr(main_window.edit_palettes_tab, 'sync_splitter_on_tab_change'):
            main_window.edit_palettes_tab.sync_splitter_on_tab_change()
        update_hover_from_current_cursor(main_window)
        main_window.edit_palettes_tab.update_status_bar(-1, -1)
    elif current_tab == main_window.preview_tab:
        main_window.custom_status_bar.update_status(
            selection_type="Tile",
            selection_id="-",
            tilemap_pos=(-1, -1),
            tile_id="-",
            palette_id="-",
            flip_state="None",
            zoom_level=main_window.zoom_level
        )

def update_hover_from_current_cursor(main_window):
    current_tab = main_window.main_tabs.currentWidget()
    
    if current_tab == main_window.edit_tiles_tab:
        main_window.hover_manager.update_hover_from_cursor(main_window.edit_tiles_tab.edit_tilemap_view)
    elif current_tab == main_window.edit_palettes_tab:
        main_window.hover_manager.update_hover_from_cursor(main_window.edit_palettes_tab.edit_tilemap2_view)

def display_tileset(main_window, pil_img):
    main_window.edit_tiles_tab.display_tileset(pil_img)
    from .view_ops import apply_zoom_to_view
    apply_zoom_to_view(main_window, main_window.edit_tiles_tab.edit_tileset_view, main_window.zoom_level / 100.0)

def sync_palettes_tab(main_window):
    grid_was_visible = main_window.grid_manager.is_grid_visible()
    if grid_was_visible:
        main_window.grid_manager.set_grid_visible(False)
    
    try:
        ep = main_window.edit_palettes_tab
        editor_enabled = ep.color_editor.red_slider.isEnabled()

        if hasattr(main_window, 'preview_tab') and hasattr(main_window.preview_tab, 'palette_colors'):
            colors_copy = [(r, g, b) for r, g, b in main_window.preview_tab.palette_colors]
            ep.display_palette_colors(colors_copy, enable_editor=editor_enabled)

        if hasattr(main_window, 'edit_tiles_tab') and hasattr(main_window.edit_tiles_tab, 'edit_tilemap_scene'):
            main_window.edit_palettes_tab.tilemap_data = main_window.edit_tiles_tab.tilemap_data
            main_window.edit_palettes_tab.tilemap_width = main_window.edit_tiles_tab.tilemap_width
            main_window.edit_palettes_tab.tilemap_height = main_window.edit_tiles_tab.tilemap_height
            main_window.edit_palettes_tab.display_tilemap_replica(main_window.edit_tiles_tab.edit_tilemap_scene)
        
        if grid_was_visible:
            main_window.grid_manager.set_grid_visible(True)
            
    except Exception as e:
        print(f"Error syncing palettes tab: {e}")
        if grid_was_visible:
            main_window.grid_manager.set_grid_visible(True)

def load_conversion_results(main_window):
    tiles_path = "output/tiles.png"
    preview_path = "temp/preview/preview.png"
    palette_path = "temp/preview/palette.pal"
    tilemap_path = "output/map.bin"

    bpp_index = int(main_window.config_manager.get('CONVERSION', 'bpp', '0'))
    main_window.current_bpp = 8 if bpp_index == 1 else 4
    main_window.current_rotation_mode = main_window.config_manager.getboolean('CONVERSION', 'rotation_mode', False)
    main_window.start_index = int(main_window.config_manager.get('CONVERSION', 'start_index', '0'))

    tilemap_width  = int(main_window.config_manager.get('CONVERSION', 'tilemap_width',  '32'))
    tilemap_height = int(main_window.config_manager.get('CONVERSION', 'tilemap_height', '32'))

    if os.path.exists(tiles_path):
        display_tileset(main_window, PilImage.open(tiles_path))

    if os.path.exists(tilemap_path):
        with open(tilemap_path, 'rb') as f:
            tilemap_data = f.read()

        for tab in [main_window.edit_tiles_tab, main_window.edit_palettes_tab]:
            tab.tilemap_data   = tilemap_data
            tab.tilemap_width  = tilemap_width
            tab.tilemap_height = tilemap_height

        main_window.edit_tiles_tab.tilemap_width_spin.blockSignals(True)
        main_window.edit_tiles_tab.tilemap_height_spin.blockSignals(True)
        main_window.edit_tiles_tab.tilemap_width_spin.setValue(tilemap_width)
        main_window.edit_tiles_tab.tilemap_height_spin.setValue(tilemap_height)
        main_window.edit_tiles_tab.tilemap_width_spin.blockSignals(False)
        main_window.edit_tiles_tab.tilemap_height_spin.blockSignals(False)

        for ctrl in [main_window.edit_tiles_tab.tilemap_width_spin,
                     main_window.edit_tiles_tab.tilemap_height_spin,
                     main_window.edit_tiles_tab.resize_button,
                     main_window.edit_tiles_tab.btn_up, main_window.edit_tiles_tab.btn_down,
                     main_window.edit_tiles_tab.btn_left, main_window.edit_tiles_tab.btn_right,
                     main_window.edit_tiles_tab.cyclic_checkbox]:
            ctrl.setEnabled(True)

        et = main_window.edit_tiles_tab
        for cb in [et.flip_h_checkbox, et.flip_v_checkbox, et.cyclic_checkbox]:
            cb.setChecked(False)
        ep = main_window.edit_palettes_tab
        for cb in ep._palette_op_btns:
            cb.setChecked(False)
        ep._on_palette_op_mode_changed()

        main_window.edit_palettes_tab.toggle_tilemap_controls_enabled(True)
        main_window.edit_palettes_tab.tilemap_width_spin.setValue(tilemap_width)
        main_window.edit_palettes_tab.tilemap_height_spin.setValue(tilemap_height)

    if hasattr(main_window, 'history_manager'):
        main_window.history_manager.clear()

    if os.path.exists(palette_path):
        palette_colors = [(0, 0, 0)] * 256
        try:
            with open(palette_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f
                        if line.strip() and not line.startswith(("JASC-PAL", "0100"))]
            if lines:
                color_count = int(lines[0])
                for i in range(1, min(1 + color_count, 257)):
                    r, g, b = map(int, lines[i].split())
                    palette_colors[i - 1] = (r, g, b)
            main_window.preview_tab.display_palette_colors(palette_colors)
            if hasattr(main_window, 'edit_palettes_tab'):
                main_window.edit_palettes_tab.display_palette_colors(palette_colors)
        except Exception as e:
            print(f"Error loading palette: {e}")
            grayscale_colors = generate_grayscale_palette()
            main_window.preview_tab.display_palette_colors(grayscale_colors)
            if hasattr(main_window, 'edit_palettes_tab'):
                main_window.edit_palettes_tab.display_palette_colors(grayscale_colors)

    if os.path.exists(preview_path):
        preview_img = PilImage.open(preview_path)
        preview_qimg = pil_to_qimage(preview_img)
        preview_pixmap = QPixmap.fromImage(preview_qimg)

        main_window.preview_tab.preview_image_scene.clear()
        main_window.preview_tab.preview_image_scene.addPixmap(preview_pixmap)
        main_window.preview_tab.preview_image_scene.setSceneRect(preview_pixmap.rect())

        main_window.edit_tiles_tab.edit_tilemap_scene.clear()
        main_window.edit_tiles_tab.edit_tilemap_scene.addPixmap(preview_pixmap)
        main_window.edit_tiles_tab.edit_tilemap_scene.setSceneRect(preview_pixmap.rect())

        main_window.edit_palettes_tab.display_tilemap_replica(
            main_window.edit_tiles_tab.edit_tilemap_scene
        )

        from .view_ops import apply_zoom_to_view
        apply_zoom_to_view(main_window, main_window.preview_tab.preview_image_view, main_window.zoom_level / 100.0)
        main_window.preview_tab.preview_image_view.centerOn(
            main_window.preview_tab.preview_image_scene.items()[0]
        )

    main_window.menu_bar.action_save_tileset.setEnabled(True)
    from .file_ops import _update_convert_actions
    _update_convert_actions(main_window)
    main_window.menu_bar.action_open_tilemap.setEnabled(True)
    main_window.menu_bar.action_new_tilemap.setEnabled(True)
    main_window.menu_bar.action_save_tilemap.setEnabled(True)
    main_window.menu_bar.action_save_palette.setEnabled(True)

    if hasattr(main_window, 'context_toolbar'):
        main_window.context_toolbar.show_for_tab(main_window.main_tabs.currentIndex())

    main_window.tileset_from_conversion = True

    if hasattr(main_window, 'output_loaded_for_zoom'):
        main_window.output_loaded_for_zoom = True

    main_window.main_tabs.setCurrentIndex(1)

    from core.image_utils import create_gbagfx_preview
    create_gbagfx_preview(
        save_preview=main_window.save_preview_files,
        keep_transparent=main_window.keep_transparent_color
    )
    main_window.refresh_preview_display()

    if os.path.exists(palette_path):
        try:
            with open(palette_path, 'r', encoding='utf-8') as f:
                plines = [l.strip() for l in f
                          if l.strip() and not l.startswith(('JASC-PAL', '0100'))]
            if plines:
                palette_colors = [(0, 0, 0)] * 256
                for i in range(1, min(1 + int(plines[0]), 257)):
                    palette_colors[i - 1] = tuple(map(int, plines[i].split()))
                main_window.preview_tab.display_palette_colors(palette_colors)
                main_window.edit_palettes_tab.display_palette_colors(palette_colors)
        except Exception as e:
            print(f"Error reloading palette after preview: {e}")

# core/quantization.py
import os
import sys
import platform
import subprocess
import shutil
import numpy as np
from PIL import Image
from core.palette_utils import rgb_to_gba_rounded, calculate_relative_luminance
from core.config import MARKER_COLOR
from utils.translator import Translator
translator = Translator()


def quantize_to_n_colors_4bpp(groups_dir, selected_palettes=None, transparent_color=(0,0,0), keep_transparent=False):
    from sklearn.cluster import KMeans
    
    indexed_dir = os.path.join(groups_dir, "01_indexed")
    reindexed_dir = os.path.join(groups_dir, "02_reindexed")
    os.makedirs(indexed_dir, exist_ok=True)
    os.makedirs(reindexed_dir, exist_ok=True)

    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)
    marker_gba = rgb_to_gba_rounded(MARKER_COLOR)
    
    for i in range(16):
        input_path = os.path.abspath(os.path.join(groups_dir, f"group_{i}.png"))
        if not os.path.exists(input_path):
            continue

        output_1 = os.path.abspath(os.path.join(indexed_dir, f"group_{i}_indexed.png"))
        output_2 = os.path.abspath(os.path.join(reindexed_dir, f"group_{i}_indexed.png"))

        try:
            img = Image.open(input_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            arr = np.array(img)
            h, w, _ = arr.shape

            alpha = arr[:, :, 3]
            opaque_mask = alpha > 128
            transparent_mask = alpha <= 128
            
            opaque_pixels = arr[opaque_mask][:, :3]
            
            if len(opaque_pixels) == 0:
                indexed_img = Image.new("P", (w, h))
                flat_palette = [0] * 768
                indexed_img.putpalette(flat_palette)
                indexed_img.save(output_1)
                indexed_img.save(output_2)
                continue

            mask_marker = (arr[:, :, 0] == MARKER_COLOR[0]) & \
                         (arr[:, :, 1] == MARKER_COLOR[1]) & \
                         (arr[:, :, 2] == MARKER_COLOR[2]) & \
                         (opaque_mask)
            has_marker = np.any(mask_marker)
            
            cluster_pixels = opaque_pixels.copy()
            if has_marker:
                not_marker = ~((opaque_pixels[:, 0] == MARKER_COLOR[0]) & 
                              (opaque_pixels[:, 1] == MARKER_COLOR[1]) & 
                              (opaque_pixels[:, 2] == MARKER_COLOR[2]))
                cluster_pixels = opaque_pixels[not_marker]

            unique_colors = np.unique(cluster_pixels, axis=0)
            max_possible_clusters = min(15, len(unique_colors))
            n_clusters = min(max_possible_clusters, len(cluster_pixels))

            if n_clusters > 0:
                import warnings
                from sklearn.exceptions import ConvergenceWarning
                
                if len(cluster_pixels) > 5000:
                    np.random.seed(42)
                    
                    sample_size = min(5000, len(cluster_pixels))
                    indices = np.random.choice(len(cluster_pixels), sample_size, replace=False)
                    sample_pixels = cluster_pixels[indices]
                    
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=ConvergenceWarning)
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=30, tol=1e-5)
                        kmeans.fit(sample_pixels)
                    
                    labels = kmeans.predict(cluster_pixels)
                    cluster_centers = kmeans.cluster_centers_.round().astype(int)
                else:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=ConvergenceWarning)
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=30, tol=1e-5)
                        labels = kmeans.fit_predict(cluster_pixels)
                    cluster_centers = kmeans.cluster_centers_.round().astype(int)
                
                initial_palette = [final_color_0]
                for center in cluster_centers:
                    initial_palette.append(tuple(center))
                
                while len(initial_palette) < 16:
                    initial_palette.append((0, 0, 0))
            else:
                initial_palette = [final_color_0] + [(0, 0, 0)] * 15

            indexed_data = np.zeros((h, w), dtype=np.uint8)
            indexed_data[transparent_mask] = 0
            
            if n_clusters > 0:
                opaque_indices = labels + 1
                
                opaque_non_marker = opaque_mask & ~mask_marker
                indexed_data[opaque_non_marker] = opaque_indices
                
                indexed_data[mask_marker] = 0
            else:
                indexed_data[mask_marker] = 0

            indexed_img = Image.fromarray(indexed_data, mode="P")
            flat_palette_1 = []
            for color in initial_palette:
                flat_palette_1.extend(color)
            while len(flat_palette_1) < 768:
                flat_palette_1.append(0)
            indexed_img.putpalette(flat_palette_1)
            indexed_img.save(output_1)

            palette = indexed_img.getpalette()
            rgb_palette = []
            for j in range(16):
                r = palette[j*3]
                g = palette[j*3+1]
                b = palette[j*3+2]
                rgb_palette.append((r, g, b))

            work_colors = rgb_palette[1:]
            
            work_colors = [color for color in work_colors if color != MARKER_COLOR]
            
            unique_work_colors = []
            filler_count = 0
            for color in work_colors:
                if color != (0, 0, 0):
                    unique_work_colors.append(color)
                else:
                    filler_count += 1
            
            unique_work_colors_sorted = sorted(unique_work_colors, key=lambda x: (
                calculate_relative_luminance(x),
                x[0], x[1], x[2]
            ))
            
            reordered_rgb = [rgb_palette[0]] + unique_work_colors_sorted
            
            while len(reordered_rgb) < 16:
                reordered_rgb.append((0, 0, 0))

            for i in range(1, 16):
                if reordered_rgb[i] == MARKER_COLOR:
                    reordered_rgb[i] = (
                        (MARKER_COLOR[0] + 1) % 256,
                        (MARKER_COLOR[1] + 1) % 256, 
                        (MARKER_COLOR[2] + 1) % 256
                    )

            reordered_rgb[0] = MARKER_COLOR
            
            print(translator.tr("applying_gba_palette"), flush=True)
            
            if keep_transparent:
                reordered_rgb[0] = transparent_color_gba
            else:
                reordered_rgb[0] = (0, 0, 0)

            img_data = np.array(indexed_img)
            new_img = Image.new("P", indexed_img.size)

            flat_palette = []
            for color in reordered_rgb:
                flat_palette.extend(color)
            while len(flat_palette) < 768:
                flat_palette.append(0)
            new_img.putpalette(flat_palette)

            old_to_new = {}
            for old_idx in range(16):
                old_color = rgb_palette[old_idx]
                best_new_idx = 0
                best_dist = float('inf')
                for new_idx in range(16):
                    new_color = reordered_rgb[new_idx]
                    dr = old_color[0] - new_color[0]
                    dg = old_color[1] - new_color[1]
                    db = old_color[2] - new_color[2]
                    dist = dr*dr + dg*dg + db*db
                    if dist < best_dist:
                        best_dist = dist
                        best_new_idx = new_idx
                old_to_new[old_idx] = best_new_idx

            img_flat = img_data.flatten()
            new_flat = np.array([old_to_new.get(idx, 0) for idx in img_flat])
            new_img.putdata(new_flat.tolist())

            new_img.save(output_2)

        except Exception as e:
            print(translator.tr("error_ensure_gba", e=e))
            try:
                default_img = Image.new("P", (w, h))
                flat_palette = [0] * 768
                default_img.putpalette(flat_palette)
                default_img.save(output_1)
                default_img.save(output_2)
            except:
                pass

    return reindexed_dir

def quantize_to_n_colors_8bpp(img, n_colors, start_index=0, transparent_color=(0, 0, 0), keep_transparent=False):
    from sklearn.cluster import KMeans
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    h, w, _ = arr.shape

    alpha = arr[:, :, 3]
    opaque = alpha > 128
    pixels = arr[opaque][:, :3]

    if len(pixels) == 0:
        raise ValueError(translator.tr("error_no_valid_pixels"))

    mask_marker = (arr[:, :, 0] == MARKER_COLOR[0]) & \
                  (arr[:, :, 1] == MARKER_COLOR[1]) & \
                  (arr[:, :, 2] == MARKER_COLOR[2]) & \
                  (opaque)
    has_marker = np.any(mask_marker)

    cluster_pixels = pixels.copy()
    if has_marker:
        not_marker = ~((pixels[:, 0] == MARKER_COLOR[0]) & 
                       (pixels[:, 1] == MARKER_COLOR[1]) & 
                       (pixels[:, 2] == MARKER_COLOR[2]))
        cluster_pixels = pixels[not_marker]

    unique_colors = np.unique(cluster_pixels, axis=0)

    if start_index == 0:
        max_possible_clusters = min(n_colors - 1, len(unique_colors)) if n_colors > 1 else 1
        n_clusters = min(max_possible_clusters, len(cluster_pixels))
    else:
        max_possible_clusters = min(n_colors, len(unique_colors))
        n_clusters = min(max_possible_clusters, len(cluster_pixels))

    if n_clusters <= 0:
        n_clusters = 1

    import warnings
    from sklearn.exceptions import ConvergenceWarning

    if len(cluster_pixels) > 5000:
        np.random.seed(42)
        
        sample_size = min(5000, len(cluster_pixels))
        indices = np.random.choice(len(cluster_pixels), sample_size, replace=False)
        sample_pixels = cluster_pixels[indices]
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=30, tol=1e-5)
            kmeans.fit(sample_pixels)
        
        labels = kmeans.predict(cluster_pixels)
        cluster_centers = kmeans.cluster_centers_.round(0).astype(int)
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=30, tol=1e-5)
            labels = kmeans.fit_predict(cluster_pixels)
        cluster_centers = kmeans.cluster_centers_.round(0).astype(int)

    reduced_palette = []
    if start_index == 0:
        for i in range(n_colors - 1):
            if i < len(cluster_centers):
                r, g, b = cluster_centers[i]
                reduced_palette.append((int(r), int(g), int(b)))
            else:
                reduced_palette.append((0, 0, 0))
    else:
        for i in range(n_colors):
            if i < len(cluster_centers):
                r, g, b = cluster_centers[i]
                reduced_palette.append((int(r), int(g), int(b)))
            else:
                reduced_palette.append((0, 0, 0))

    print(translator.tr("applying_gba_palette"), flush=True)
    transparent_color_gba = rgb_to_gba_rounded(transparent_color)
    final_color_0 = transparent_color_gba if keep_transparent else (0, 0, 0)

    if start_index == 0:
        unique_colors_list = [c for c in reduced_palette if c != (0, 0, 0)]
        filler_count = len(reduced_palette) - len(unique_colors_list)
        
        indexed_unique = [(i, color) for i, color in enumerate(unique_colors_list)]
        indexed_unique.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        
        reordered_palette = [final_color_0]
        for _, color in indexed_unique:
            reordered_palette.append(color)
        
        for _ in range(filler_count):
            reordered_palette.append((0, 0, 0))
    else:
        unique_colors_list = [c for c in reduced_palette if c != (0, 0, 0)]
        filler_count = len(reduced_palette) - len(unique_colors_list)
        
        indexed_unique = [(i, color) for i, color in enumerate(unique_colors_list)]
        indexed_unique.sort(key=lambda x: (calculate_relative_luminance(x[1]), x[1][0], x[1][1], x[1][2]))
        
        reordered_palette = []
        for _, color in indexed_unique:
            reordered_palette.append(color)
        
        for _ in range(filler_count):
            reordered_palette.append((0, 0, 0))

    palette_rgb_list = reordered_palette[1:] if start_index == 0 else reordered_palette

    if not palette_rgb_list:
        palette_rgb = np.array([[0, 0, 0]], dtype=int)
    else:
        palette_rgb = np.array(palette_rgb_list, dtype=int)

    indices = np.zeros((h, w), dtype=np.uint8)

    valid_mask = opaque & ~(
        (arr[:, :, 0] == MARKER_COLOR[0]) & 
        (arr[:, :, 1] == MARKER_COLOR[1]) & 
        (arr[:, :, 2] == MARKER_COLOR[2])
    )
    
    valid_coords = np.argwhere(valid_mask)
    if len(valid_coords) > 0:
        valid_pixels = arr[valid_mask][:, :3]
        
        distances = np.sum((valid_pixels[:, np.newaxis] - palette_rgb) ** 2, axis=2)
        closest_indices = np.argmin(distances, axis=1)
        
        if start_index == 0:
            indices[valid_mask] = closest_indices + 1
        else:
            indices[valid_mask] = start_index + closest_indices

    indices[alpha <= 128] = 0
    indices[mask_marker] = 0

    full_palette_gba = [(255, 255, 255)] * 256 

    full_palette_gba[0] = final_color_0
    if start_index == 0:
        for i, (r, g, b) in enumerate(reordered_palette[1:], start=1):
            if i < 256:
                full_palette_gba[i] = rgb_to_gba_rounded((r, g, b))
    else:
        for i, (r, g, b) in enumerate(reordered_palette):
            idx = start_index + i
            if idx < 256:
                full_palette_gba[idx] = rgb_to_gba_rounded((r, g, b))

    print(translator.tr("rebuilding_image"), flush=True)
    out_img = Image.fromarray(indices, mode="P")

    final_palette = []
    for color in full_palette_gba:
        if color == (255, 255, 255):
            final_palette.append((0, 0, 0))
        else:
            final_palette.append(color)
            
    flat_palette = [c for color in final_palette for c in color]
    while len(flat_palette) < 768:
        flat_palette.append(0)
    out_img.putpalette(flat_palette)

    return out_img, final_palette

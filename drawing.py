import bpy
import blf
import gpu
import math
from gpu_extras.batch import batch_for_shader

draw_handler = None
_is_animation_playing = False
_shader = None

def draw_callback_px(self, context):
    global _is_animation_playing, _shader
    
    try:
        # Resolve dynamic context
        context = bpy.context
        
        # Safe check on space_data
        if not hasattr(context, "space_data") or not context.space_data or context.space_data.type != 'VIEW_3D':
            return
            
        if not hasattr(bpy.context.preferences, 'addons') or __package__ not in bpy.context.preferences.addons:
            return
            
        prefs = bpy.context.preferences.addons[__package__].preferences
        
        # Determine states
        playing_active = getattr(prefs, "draw_playback_overlay", True) and (
            _is_animation_playing or getattr(prefs, "playback_overlay_preview_show", False)
        )
        
        is_local_view = getattr(context.space_data, "local_view", None) is not None
        local_active = getattr(prefs, "draw_local_view_overlay", True) and (
            is_local_view or getattr(prefs, "local_view_overlay_preview_show", False)
        )
        
        # Check early exit if neither overlay needs drawing
        if not playing_active and not local_active:
            return

        font_id = 0
        region = context.region
        width = region.width
        height = region.height
        border_w = 3.0    # 3px accent border on the left

        # 1. Measure and compute dimensions for active overlays
        box_w_play = box_h_play = 0.0
        radius_play = pad_left_play = gap_play = pad_right_play = 0.0
        text_w_play = text_h_play = 0.0
        frame_text = ""
        font_size_play = 13
        if playing_active:
            font_size_play = getattr(prefs, "playback_overlay_font_size", 13)
            blf.size(font_id, font_size_play)
            frame_text = f"PLAYING: {context.scene.frame_current}"
            text_w_play, text_h_play = blf.dimensions(font_id, frame_text)

            radius_play = font_size_play * 0.3
            radius_play = max(2.5, min(radius_play, 8.0))
            pad_left_play = font_size_play * 0.9
            gap_play = font_size_play * 0.6
            pad_right_play = font_size_play * 1.1
            
            box_w_play = border_w + pad_left_play + (radius_play * 2.0) + gap_play + text_w_play + pad_right_play
            box_h_play = text_h_play + (font_size_play * 1.0)

        box_w_local = box_h_local = 0.0
        radius_local = pad_left_local = gap_local = pad_right_local = 0.0
        text_w_local = text_h_local = 0.0
        local_text = "LOCAL VIEW"
        font_size_local = 13
        if local_active:
            font_size_local = getattr(prefs, "local_view_overlay_font_size", 13)
            blf.size(font_id, font_size_local)
            text_w_local, text_h_local = blf.dimensions(font_id, local_text)

            radius_local = font_size_local * 0.3
            radius_local = max(2.5, min(radius_local, 8.0))
            pad_left_local = font_size_local * 0.9
            gap_local = font_size_local * 0.6
            pad_right_local = font_size_local * 1.1
            
            box_w_local = border_w + pad_left_local + (radius_local * 2.0) + gap_local + text_w_local + pad_right_local
            box_h_local = text_h_local + (font_size_local * 1.0)

        # 2. Position calculations
        bx1_play = by1_play = bx2_play = by2_play = y_center_play = 0.0
        if playing_active:
            pos_mode_play = getattr(prefs, "playback_overlay_pos_mode", 'CENTER_TOP')
            if pos_mode_play == 'CUSTOM':
                percent_x = getattr(prefs, "playback_overlay_percent_x", 50.0)
                percent_y = getattr(prefs, "playback_overlay_percent_y", 90.0)
                target_x = width * (percent_x / 100.0)
                target_y = height * (percent_y / 100.0)
                
                bx1_play = max(10.0, min(target_x - (box_w_play / 2.0), width - box_w_play - 10.0))
                by1_play = max(10.0, min(target_y - (box_h_play / 2.0), height - box_h_play - 10.0))
            else:
                # CENTER_TOP
                y_center_play = height - 50.0
                bx1_play = (width - box_w_play) / 2.0
                by1_play = y_center_play - (box_h_play / 2.0)
            bx2_play = bx1_play + box_w_play
            by2_play = by1_play + box_h_play
            y_center_play = by1_play + (box_h_play / 2.0)

        bx1_local = by1_local = bx2_local = by2_local = y_center_local = 0.0
        if local_active:
            pos_mode_local = getattr(prefs, "local_view_overlay_pos_mode", 'CENTER_TOP')
            if pos_mode_local == 'CUSTOM':
                percent_x = getattr(prefs, "local_view_overlay_percent_x", 50.0)
                percent_y = getattr(prefs, "local_view_overlay_percent_y", 90.0)
                target_x = width * (percent_x / 100.0)
                target_y = height * (percent_y / 100.0)
                
                bx1_local = max(10.0, min(target_x - (box_w_local / 2.0), width - box_w_local - 10.0))
                by1_local = max(10.0, min(target_y - (box_h_local / 2.0), height - box_h_local - 10.0))
            else:
                # CENTER_TOP
                y_center_local = height - 50.0
                bx1_local = (width - box_w_local) / 2.0
                by1_local = y_center_local - (box_h_local / 2.0)
            bx2_local = bx1_local + box_w_local
            by2_local = by1_local + box_h_local
            y_center_local = by1_local + (box_h_local / 2.0)

        # 3. Overlap resolution (Horizontal offset)
        if playing_active and local_active:
            pos_mode_play = getattr(prefs, "playback_overlay_pos_mode", 'CENTER_TOP')
            pos_mode_local = getattr(prefs, "local_view_overlay_pos_mode", 'CENTER_TOP')
            
            if pos_mode_play == 'CENTER_TOP' and pos_mode_local == 'CENTER_TOP':
                # Center both side-by-side
                total_w = box_w_play + box_w_local + 10.0
                bx1_play = (width - total_w) / 2.0
                bx2_play = bx1_play + box_w_play
                y_center_play = height - 50.0
                by1_play = y_center_play - (box_h_play / 2.0)
                by2_play = by1_play + box_h_play
                
                bx1_local = bx2_play + 10.0
                bx2_local = bx1_local + box_w_local
                y_center_local = height - 50.0
                by1_local = y_center_local - (box_h_local / 2.0)
                by2_local = by1_local + box_h_local
            else:
                # General overlap check (e.g. if they collide in custom coordinate modes)
                overlap_x = not (bx2_play < bx1_local or bx2_local < bx1_play)
                overlap_y = not (by2_play < by1_local or by2_local < by1_play)
                if overlap_x and overlap_y:
                    # Offset Local View to the right of Playing card
                    bx1_local = bx2_play + 10.0
                    # Clamp to screen boundary
                    if bx1_local + box_w_local > width - 10.0:
                        # If it exceeds the right edge, shift left instead of right
                        bx1_local = max(10.0, bx1_play - box_w_local - 10.0)
                    bx2_local = bx1_local + box_w_local
                    y_center_local = by1_local + (box_h_local / 2.0)

        # 4. Initialize shader
        if _shader is None:
            try:
                _shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            except Exception:
                _shader = gpu.shader.from_builtin('UNIFORM_COLOR')

        gpu.state.blend_set('ALPHA')
        _shader.bind()
        indices = ((0, 1, 2), (2, 1, 3))

        # --- Draw Playing Card (if active) ---
        if playing_active:
            cx_play = bx1_play + border_w + pad_left_play + radius_play
            cy_play = y_center_play
            tx_play = cx_play + radius_play + gap_play
            text_y_play = y_center_play - (text_h_play / 2.0) + 1.0

            # Background
            bg_verts = ((bx1_play, by1_play), (bx2_play, by1_play), (bx1_play, by2_play), (bx2_play, by2_play))
            bg_batch = batch_for_shader(_shader, 'TRIS', {"pos": bg_verts}, indices=indices)
            bg_col = list(getattr(prefs, "playback_overlay_bg_color", (0.08, 0.08, 0.08)))
            bg_alpha = getattr(prefs, "playback_overlay_bg_alpha", 0.85)
            _shader.uniform_float("color", (bg_col[0], bg_col[1], bg_col[2], bg_alpha))
            bg_batch.draw(_shader)

            # Left accent border
            if getattr(prefs, "playback_overlay_use_custom_accent", False):
                accent_col = list(getattr(prefs, "playback_overlay_accent_color", (0.08, 0.45, 0.18, 1.0)))
            else:
                if prefs.header_colors.use_animation_play_color:
                    accent_col = list(prefs.header_colors.animation_play_color)
                else:
                    accent_col = [0.08, 0.45, 0.18, 1.0]
            accent_col[3] = 1.0
            border_verts = ((bx1_play, by1_play), (bx1_play + border_w, by1_play), (bx1_play, by2_play), (bx1_play + border_w, by2_play))
            border_batch = batch_for_shader(_shader, 'TRIS', {"pos": border_verts}, indices=indices)
            _shader.uniform_float("color", accent_col)
            border_batch.draw(_shader)

            # Pulsing red circle
            num_segments = 16
            pulse = math.sin(context.scene.frame_current * 0.15) * 0.325 + 0.675
            circle_vertices = [(cx_play, cy_play)]
            for i in range(num_segments + 1):
                angle = i * (2.0 * math.pi / num_segments)
                circle_vertices.append((cx_play + math.cos(angle) * radius_play, cy_play + math.sin(angle) * radius_play))
            circle_indices = []
            for i in range(1, num_segments + 1):
                circle_indices.append((0, i, i + 1))
            circle_batch = batch_for_shader(_shader, 'TRIS', {"pos": circle_vertices}, indices=circle_indices)
            _shader.uniform_float("color", (0.9, 0.15, 0.15, pulse))
            circle_batch.draw(_shader)

        # --- Draw Local View Card (if active) ---
        if local_active:
            cx_local = bx1_local + border_w + pad_left_local + radius_local
            cy_local = y_center_local
            tx_local = cx_local + radius_local + gap_local
            text_y_local = y_center_local - (text_h_local / 2.0) + 1.0

            # Background
            bg_verts = ((bx1_local, by1_local), (bx2_local, by1_local), (bx1_local, by2_local), (bx2_local, by2_local))
            bg_batch = batch_for_shader(_shader, 'TRIS', {"pos": bg_verts}, indices=indices)
            bg_col = list(getattr(prefs, "local_view_overlay_bg_color", (0.08, 0.08, 0.08)))
            bg_alpha = getattr(prefs, "local_view_overlay_bg_alpha", 0.85)
            _shader.uniform_float("color", (bg_col[0], bg_col[1], bg_col[2], bg_alpha))
            bg_batch.draw(_shader)

            # Left accent border
            if getattr(prefs, "local_view_overlay_use_custom_accent", False):
                accent_col = list(getattr(prefs, "local_view_overlay_accent_color", (0.8, 0.45, 0.08, 1.0)))
            else:
                accent_col = [0.8, 0.45, 0.08, 1.0]
            accent_col[3] = 1.0
            border_verts = ((bx1_local, by1_local), (bx1_local + border_w, by1_local), (bx1_local, by2_local), (bx1_local + border_w, by2_local))
            border_batch = batch_for_shader(_shader, 'TRIS', {"pos": border_verts}, indices=indices)
            _shader.uniform_float("color", accent_col)
            border_batch.draw(_shader)

            # Steady circle matching the accent color
            num_segments = 16
            circle_vertices = [(cx_local, cy_local)]
            for i in range(num_segments + 1):
                angle = i * (2.0 * math.pi / num_segments)
                circle_vertices.append((cx_local + math.cos(angle) * radius_local, cy_local + math.sin(angle) * radius_local))
            circle_indices = []
            for i in range(1, num_segments + 1):
                circle_indices.append((0, i, i + 1))
            circle_batch = batch_for_shader(_shader, 'TRIS', {"pos": circle_vertices}, indices=circle_indices)
            _shader.uniform_float("color", (accent_col[0], accent_col[1], accent_col[2], 0.9))
            circle_batch.draw(_shader)

        gpu.state.blend_set('NONE')

        # --- Draw Text (if active) ---
        if playing_active:
            blf.size(font_id, font_size_play)
            # Shadow
            blf.color(font_id, 0.0, 0.0, 0.0, 0.5)
            blf.position(font_id, tx_play + 1, text_y_play - 1, 0)
            blf.draw(font_id, frame_text)
            
            # Main white text
            blf.color(font_id, 0.95, 0.95, 0.95, 1.0)
            blf.position(font_id, tx_play, text_y_play, 0)
            blf.draw(font_id, frame_text)

        if local_active:
            blf.size(font_id, font_size_local)
            # Shadow
            blf.color(font_id, 0.0, 0.0, 0.0, 0.5)
            blf.position(font_id, tx_local + 1, text_y_local - 1, 0)
            blf.draw(font_id, local_text)
            
            # Main white text
            blf.color(font_id, 0.95, 0.95, 0.95, 1.0)
            blf.position(font_id, tx_local, text_y_local, 0)
            blf.draw(font_id, local_text)
        
    except Exception as e:
        import traceback
        print(f"[Mode Highlight] Error in draw_callback_px: {e}")
        traceback.print_exc()


mode_handler = None

def _region_insets(context, region):
    """Insets (left, right, top, bottom) of the WINDOW region covered by overlapping UI regions."""
    l = r = t = b = 0.0
    area = context.area
    if not area:
        return l, r, t, b
    for reg in area.regions:
        if reg.type in {'WINDOW', 'HUD'} or reg.width <= 1 or reg.height <= 1:
            continue
        al = reg.alignment
        # TOP regions (Header / Tool Header) are ignored: the outline runs to the
        # very top of the area so it joins the header instead of sitting below it.
        if al == 'BOTTOM':
            b = max(b, (reg.y + reg.height) - region.y)
        # LEFT/RIGHT regions (Toolbar / N-Panel) are intentionally ignored:
        # the outline runs to the full viewport edge behind them.
    return l, r, t, b

def draw_mode_overlay_px(self, context):
    """Draws the optional mode-colored viewport outline and mode name."""
    global _shader
    try:
        from .core import get_mode_config, MODE_LABELS
        context = bpy.context
        space = context.space_data
        if not space or space.type != 'VIEW_3D' or not context.region:
            return
        if __package__ not in context.preferences.addons:
            return
        prefs = context.preferences.addons[__package__].preferences
        if not (prefs.draw_mode_outline or prefs.draw_mode_name):
            return

        obj = context.active_object
        mode = obj.mode if obj else 'OBJECT'
        color, enabled = get_mode_config(prefs.header_colors, mode)
        if not enabled:
            return

        region = context.region
        il, ir, it, ib = _region_insets(context, region)
        x0, y0 = max(il, 0.0), max(ib, 0.0)
        x1, y1 = region.width - max(ir, 0.0), region.height - max(it, 0.0)
        if x1 - x0 < 20 or y1 - y0 < 20:
            return

        if _shader is None:
            try:
                _shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            except Exception:
                _shader = gpu.shader.from_builtin('UNIFORM_COLOR')

        gpu.state.blend_set('ALPHA')
        _shader.bind()
        indices = ((0, 1, 2), (2, 1, 3))

        def rect(ax, ay, bx, by, col):
            verts = ((ax, ay), (bx, ay), (ax, by), (bx, by))
            batch = batch_for_shader(_shader, 'TRIS', {"pos": verts}, indices=indices)
            _shader.uniform_float("color", col)
            batch.draw(_shader)

        if prefs.draw_mode_outline:
            t = float(prefs.mode_outline_thickness)
            col = (color[0], color[1], color[2], prefs.mode_outline_opacity)
            rect(x0, y1 - t, x1, y1, col)          # top
            rect(x0, y0, x1, y0 + t, col)          # bottom
            rect(x0, y0 + t, x0 + t, y1 - t, col)  # left
            rect(x1 - t, y0 + t, x1, y1 - t, col)  # right

        if prefs.draw_mode_name:
            label = MODE_LABELS.get(mode, mode.replace('_', ' '))
            font_id = 0
            size = prefs.mode_name_font_size
            blf.size(font_id, size)
            tw, th = blf.dimensions(font_id, label)
            border_w = 3.0
            pad_x = size * 0.9
            box_w = border_w + pad_x * 2 + tw
            box_h = th + size
            vw, vh = x1 - x0, y1 - y0
            tx = x0 + vw * prefs.mode_name_percent_x / 100.0
            ty = y0 + vh * prefs.mode_name_percent_y / 100.0
            bx = max(x0 + 10.0, min(tx - box_w / 2.0, x1 - box_w - 10.0))
            by = max(y0 + 10.0, min(ty - box_h / 2.0, y1 - box_h - 10.0))
            rect(bx, by, bx + box_w, by + box_h, (0.08, 0.08, 0.08, 0.85))
            rect(bx, by, bx + border_w, by + box_h, (color[0], color[1], color[2], 1.0))
            gpu.state.blend_set('NONE')
            text_x = bx + border_w + pad_x
            text_y = by + (box_h - th) / 2.0 + 1.0
            blf.color(font_id, 0.0, 0.0, 0.0, 0.5)
            blf.position(font_id, text_x + 1, text_y - 1, 0)
            blf.draw(font_id, label)
            blf.color(font_id, 0.95, 0.95, 0.95, 1.0)
            blf.position(font_id, text_x, text_y, 0)
            blf.draw(font_id, label)

        gpu.state.blend_set('NONE')
    except Exception as e:
        import traceback
        print(f"[Mode Highlight] Error in draw_mode_overlay_px: {e}")
        traceback.print_exc()

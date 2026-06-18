import bpy

def get_contrast_text_color(bg_color):
    """Calculates appropriate text and highlight text colors based on background color luminance."""
    r, g, b = bg_color[0], bg_color[1], bg_color[2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    if luminance > 0.5:
        return (0.08, 0.08, 0.08), (0.0, 0.0, 0.0)
    else:
        return (0.92, 0.92, 0.92), (1.0, 1.0, 1.0)

def adjust_bg_for_contrast(bg_color, text_color):
    """
    Adjusts the background color's brightness if necessary to ensure legibility
    against the theme's default text color.
    """
    r, g, b = bg_color[0], bg_color[1], bg_color[2]
    bg_luma = 0.299 * r + 0.587 * g + 0.114 * b
    
    tx_r, tx_g, tx_b = text_color[0], text_color[1], text_color[2]
    text_luma = 0.299 * tx_r + 0.587 * tx_g + 0.114 * tx_b
    
    a = bg_color[3] if len(bg_color) > 3 else 0.9
    
    # If the default text is light (Dark Theme), we need a dark background
    if text_luma > 0.5:
        max_bg_luma = 0.38
        if bg_luma > max_bg_luma:
            factor = max_bg_luma / bg_luma
            return (r * factor, g * factor, b * factor, a)
    # If the default text is dark (Light Theme), we need a light background
    else:
        min_bg_luma = 0.62
        if bg_luma < min_bg_luma:
            factor = min_bg_luma / max(bg_luma, 0.01)
            return (min(r * factor, 1.0), min(g * factor, 1.0), min(b * factor, 1.0), a)
            
    return (r, g, b, a)

def restore_theme(prefs, theme):
    """Restores the original theme colors if a backup exists."""
    if prefs.header_colors.has_backup:
        colors = prefs.header_colors
        theme.view_3d.space.header = colors.original_view3d_color
        theme.properties.space.header = colors.original_props_color
        theme.dopesheet_editor.space.header = colors.original_dopesheet_color
        theme.graph_editor.space.header = colors.original_graph_color
        theme.nla_editor.space.header = colors.original_nla_color
        
        # Restore text colors
        theme.view_3d.space.header_text = colors.original_view3d_text
        theme.view_3d.space.header_text_hi = colors.original_view3d_text_hi
        
        theme.properties.space.header_text = colors.original_props_text
        theme.properties.space.header_text_hi = colors.original_props_text_hi
        
        theme.dopesheet_editor.space.header_text = colors.original_dopesheet_text
        theme.dopesheet_editor.space.header_text_hi = colors.original_dopesheet_text_hi
        
        theme.graph_editor.space.header_text = colors.original_graph_text
        theme.graph_editor.space.header_text_hi = colors.original_graph_text_hi
        
        theme.nla_editor.space.header_text = colors.original_nla_text
        theme.nla_editor.space.header_text_hi = colors.original_nla_text_hi

def update_header_color(is_playing=None):
    try:
        if not hasattr(bpy.context.preferences, 'addons') or __package__ not in bpy.context.preferences.addons:
            return
        
        prefs = bpy.context.preferences.addons[__package__].preferences
        theme = bpy.context.preferences.themes[0]
        colors = prefs.header_colors

        # Detect theme changes
        theme_path = theme.filepath if hasattr(theme, "filepath") else ""
        if colors.theme_filepath != theme_path:
            colors.has_backup = False
            colors.theme_filepath = theme_path

        # 1. Backup Phase: Save original colors once (if not already saved)
        if not colors.has_backup:
            colors.original_view3d_color = tuple(theme.view_3d.space.header)
            colors.original_props_color = tuple(theme.properties.space.header)
            colors.original_dopesheet_color = tuple(theme.dopesheet_editor.space.header)
            colors.original_graph_color = tuple(theme.graph_editor.space.header)
            colors.original_nla_color = tuple(theme.nla_editor.space.header)
            
            colors.original_view3d_text = tuple(theme.view_3d.space.header_text)
            colors.original_view3d_text_hi = tuple(theme.view_3d.space.header_text_hi)
            colors.original_props_text = tuple(theme.properties.space.header_text)
            colors.original_props_text_hi = tuple(theme.properties.space.header_text_hi)
            colors.original_dopesheet_text = tuple(theme.dopesheet_editor.space.header_text)
            colors.original_dopesheet_text_hi = tuple(theme.dopesheet_editor.space.header_text_hi)
            colors.original_graph_text = tuple(theme.graph_editor.space.header_text)
            colors.original_graph_text_hi = tuple(theme.graph_editor.space.header_text_hi)
            colors.original_nla_text = tuple(theme.nla_editor.space.header_text)
            colors.original_nla_text_hi = tuple(theme.nla_editor.space.header_text_hi)
            
            colors.has_backup = True
        else:
            # Safeguard in case has_backup was already True from a previous version,
            # but the new backups are not yet initialized (i.e. default zeros)
            if list(colors.original_dopesheet_color) == [0.0, 0.0, 0.0, 0.0]:
                colors.original_dopesheet_color = tuple(theme.dopesheet_editor.space.header)
            if list(colors.original_graph_color) == [0.0, 0.0, 0.0, 0.0]:
                colors.original_graph_color = tuple(theme.graph_editor.space.header)
            if list(colors.original_nla_color) == [0.0, 0.0, 0.0, 0.0]:
                colors.original_nla_color = tuple(theme.nla_editor.space.header)
                
            if list(colors.original_view3d_text) == [0.0, 0.0, 0.0, 0.0]:
                colors.original_view3d_text = tuple(theme.view_3d.space.header_text)
                colors.original_view3d_text_hi = tuple(theme.view_3d.space.header_text_hi)
                colors.original_props_text = tuple(theme.properties.space.header_text)
                colors.original_props_text_hi = tuple(theme.properties.space.header_text_hi)
                colors.original_dopesheet_text = tuple(theme.dopesheet_editor.space.header_text)
                colors.original_dopesheet_text_hi = tuple(theme.dopesheet_editor.space.header_text_hi)
                colors.original_graph_text = tuple(theme.graph_editor.space.header_text)
                colors.original_graph_text_hi = tuple(theme.graph_editor.space.header_text_hi)
                colors.original_nla_text = tuple(theme.nla_editor.space.header_text)
                colors.original_nla_text_hi = tuple(theme.nla_editor.space.header_text_hi)

        # 2. Disable Phase: Restore originals if addon is disabled via checkbox
        if not prefs.header_color_enabled:
            restore_theme(prefs, theme)
            colors.has_backup = False
            _redraw_ui()
            return
        
        # 3. Active Phase: Determine target color and if it is enabled
        obj = bpy.context.active_object
        mode = obj.mode if obj else 'OBJECT'
        
        mode_configs = {
            'OBJECT': (colors.object_mode_color, colors.use_object_mode_color),
            'EDIT': (colors.edit_mode_color, colors.use_edit_mode_color),
            'SCULPT': (colors.sculpt_mode_color, colors.use_sculpt_mode_color),
            'VERTEX_PAINT': (colors.vertex_paint_color, colors.use_vertex_paint_color),
            'WEIGHT_PAINT': (colors.weight_paint_color, colors.use_weight_paint_color),
            'TEXTURE_PAINT': (colors.texture_paint_color, colors.use_texture_paint_color),
            'POSE': (colors.pose_mode_color, colors.use_pose_mode_color),
            
            # Legacy Grease Pencil (Blender < 4.3)
            'PAINT_GPENCIL': (colors.gpencil_draw_color, colors.use_gpencil_draw_color),
            'EDIT_GPENCIL': (colors.edit_mode_color, colors.use_edit_mode_color),
            'SCULPT_GPENCIL': (colors.sculpt_mode_color, colors.use_sculpt_mode_color),
            'VERTEX_GPENCIL': (colors.vertex_paint_color, colors.use_vertex_paint_color),
            'WEIGHT_GPENCIL': (colors.weight_paint_color, colors.use_weight_paint_color),
            
            # New Grease Pencil v3 (Blender 4.3+)
            'PAINT_GREASE_PENCIL': (colors.gpencil_draw_color, colors.use_gpencil_draw_color),
            'SCULPT_GREASE_PENCIL': (colors.sculpt_mode_color, colors.use_sculpt_mode_color),
            'VERTEX_GREASE_PENCIL': (colors.vertex_paint_color, colors.use_vertex_paint_color),
            'WEIGHT_GREASE_PENCIL': (colors.weight_paint_color, colors.use_weight_paint_color),
            
            # Others
            'SCULPT_CURVES': (colors.sculpt_mode_color, colors.use_sculpt_mode_color),
            'PARTICLE_EDIT': (colors.edit_mode_color, colors.use_edit_mode_color),
        }
        
        target_color, is_mode_enabled = mode_configs.get(
            mode, (colors.object_mode_color, colors.use_object_mode_color)
        )

        # Apply Colors
        if prefs.affect_view3d_editor and is_mode_enabled:
            bg_color = target_color
            if prefs.use_auto_contrast_text:
                ref_txt = colors.original_view3d_text if colors.has_backup else (0.92, 0.92, 0.92)
                bg_color = adjust_bg_for_contrast(target_color, ref_txt)
                
                txt, txt_hi = get_contrast_text_color(bg_color)
                theme.view_3d.space.header_text = txt
                theme.view_3d.space.header_text_hi = txt_hi
            else:
                if colors.has_backup:
                    theme.view_3d.space.header_text = colors.original_view3d_text
                    theme.view_3d.space.header_text_hi = colors.original_view3d_text_hi
            theme.view_3d.space.header = bg_color
        else:
            if colors.has_backup:
                theme.view_3d.space.header = colors.original_view3d_color
                theme.view_3d.space.header_text = colors.original_view3d_text
                theme.view_3d.space.header_text_hi = colors.original_view3d_text_hi
        
        if prefs.affect_properties_editor and is_mode_enabled:
            bg_color = target_color
            if prefs.use_auto_contrast_text:
                ref_txt = colors.original_props_text if colors.has_backup else (0.92, 0.92, 0.92)
                bg_color = adjust_bg_for_contrast(target_color, ref_txt)
                
                txt, txt_hi = get_contrast_text_color(bg_color)
                theme.properties.space.header_text = txt
                theme.properties.space.header_text_hi = txt_hi
            else:
                if colors.has_backup:
                    theme.properties.space.header_text = colors.original_props_text
                    theme.properties.space.header_text_hi = colors.original_props_text_hi
            theme.properties.space.header = bg_color
        else:
            if colors.has_backup:
                theme.properties.space.header = colors.original_props_color
                theme.properties.space.header_text = colors.original_props_text
                theme.properties.space.header_text_hi = colors.original_props_text_hi

        # 4. Handle Animation Playback Highlight
        if is_playing is None:
            screen = bpy.context.screen
            is_playing = screen.is_animation_playing if (screen and hasattr(screen, "is_animation_playing")) else False
        
        use_anim_color = colors.use_animation_play_color
        
        if prefs.affect_animation_editors and is_playing and use_anim_color:
            if prefs.color_timeline_dopesheet:
                bg_color = colors.animation_play_color
                if prefs.use_auto_contrast_text:
                    ref_txt = colors.original_dopesheet_text if colors.has_backup else (0.92, 0.92, 0.92)
                    bg_color = adjust_bg_for_contrast(colors.animation_play_color, ref_txt)
                    
                    txt, txt_hi = get_contrast_text_color(bg_color)
                    theme.dopesheet_editor.space.header_text = txt
                    theme.dopesheet_editor.space.header_text_hi = txt_hi
                else:
                    if colors.has_backup:
                        theme.dopesheet_editor.space.header_text = colors.original_dopesheet_text
                        theme.dopesheet_editor.space.header_text_hi = colors.original_dopesheet_text_hi
                theme.dopesheet_editor.space.header = bg_color
            else:
                if colors.has_backup:
                    theme.dopesheet_editor.space.header = colors.original_dopesheet_color
                    theme.dopesheet_editor.space.header_text = colors.original_dopesheet_text
                    theme.dopesheet_editor.space.header_text_hi = colors.original_dopesheet_text_hi

            if prefs.color_graph_editor:
                bg_color = colors.animation_play_color
                if prefs.use_auto_contrast_text:
                    ref_txt = colors.original_graph_text if colors.has_backup else (0.92, 0.92, 0.92)
                    bg_color = adjust_bg_for_contrast(colors.animation_play_color, ref_txt)
                    
                    txt, txt_hi = get_contrast_text_color(bg_color)
                    theme.graph_editor.space.header_text = txt
                    theme.graph_editor.space.header_text_hi = txt_hi
                else:
                    if colors.has_backup:
                        theme.graph_editor.space.header_text = colors.original_graph_text
                        theme.graph_editor.space.header_text_hi = colors.original_graph_text_hi
                theme.graph_editor.space.header = bg_color
            else:
                if colors.has_backup:
                    theme.graph_editor.space.header = colors.original_graph_color
                    theme.graph_editor.space.header_text = colors.original_graph_text
                    theme.graph_editor.space.header_text_hi = colors.original_graph_text_hi

            if prefs.color_nla_editor:
                bg_color = colors.animation_play_color
                if prefs.use_auto_contrast_text:
                    ref_txt = colors.original_nla_text if colors.has_backup else (0.92, 0.92, 0.92)
                    bg_color = adjust_bg_for_contrast(colors.animation_play_color, ref_txt)
                    
                    txt, txt_hi = get_contrast_text_color(bg_color)
                    theme.nla_editor.space.header_text = txt
                    theme.nla_editor.space.header_text_hi = txt_hi
                else:
                    if colors.has_backup:
                        theme.nla_editor.space.header_text = colors.original_nla_text
                        theme.nla_editor.space.header_text_hi = colors.original_nla_text_hi
                theme.nla_editor.space.header = bg_color
            else:
                if colors.has_backup:
                    theme.nla_editor.space.header = colors.original_nla_color
                    theme.nla_editor.space.header_text = colors.original_nla_text
                    theme.nla_editor.space.header_text_hi = colors.original_nla_text_hi
        else:
            if colors.has_backup:
                theme.dopesheet_editor.space.header = colors.original_dopesheet_color
                theme.dopesheet_editor.space.header_text = colors.original_dopesheet_text
                theme.dopesheet_editor.space.header_text_hi = colors.original_dopesheet_text_hi
                
                theme.graph_editor.space.header = colors.original_graph_color
                theme.graph_editor.space.header_text = colors.original_graph_text
                theme.graph_editor.space.header_text_hi = colors.original_graph_text_hi
                
                theme.nla_editor.space.header = colors.original_nla_color
                theme.nla_editor.space.header_text = colors.original_nla_text
                theme.nla_editor.space.header_text_hi = colors.original_nla_text_hi

        _redraw_ui()
                
    except Exception:
        pass

def _redraw_ui():
    for area in bpy.context.screen.areas:
        if area.type in {'VIEW_3D', 'PROPERTIES', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}:
            area.tag_redraw()

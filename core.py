import bpy

def restore_theme(prefs, theme):
    """Restores the original theme colors if a backup exists."""
    if prefs.header_colors.has_backup:
        theme.view_3d.space.header = prefs.header_colors.original_view3d_color
        theme.properties.space.header = prefs.header_colors.original_props_color
        theme.dopesheet_editor.space.header = prefs.header_colors.original_dopesheet_color
        theme.graph_editor.space.header = prefs.header_colors.original_graph_color
        theme.nla_editor.space.header = prefs.header_colors.original_nla_color

def update_header_color(is_playing=None):
    try:
        if not hasattr(bpy.context.preferences, 'addons') or __package__ not in bpy.context.preferences.addons:
            return
        
        prefs = bpy.context.preferences.addons[__package__].preferences
        theme = bpy.context.preferences.themes[0]
        colors = prefs.header_colors

        # 1. Backup Phase: Save original colors once (if not already saved)
        if not colors.has_backup:
            colors.original_view3d_color = tuple(theme.view_3d.space.header)
            colors.original_props_color = tuple(theme.properties.space.header)
            colors.original_dopesheet_color = tuple(theme.dopesheet_editor.space.header)
            colors.original_graph_color = tuple(theme.graph_editor.space.header)
            colors.original_nla_color = tuple(theme.nla_editor.space.header)
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

        # 2. Disable Phase: Restore originals if addon is disabled via checkbox
        if not prefs.header_color_enabled:
            restore_theme(prefs, theme)
            _redraw_ui()
            return
        
        # 3. Active Phase: Determine target color
        obj = bpy.context.active_object
        mode = obj.mode if obj else 'OBJECT'
        
        # Default fallback
        target_color = colors.object_mode_color
        
        mode_map = {
            'OBJECT': colors.object_mode_color,
            'EDIT': colors.edit_mode_color,
            'SCULPT': colors.sculpt_mode_color,
            'VERTEX_PAINT': colors.vertex_paint_color,
            'WEIGHT_PAINT': colors.weight_paint_color,
            'TEXTURE_PAINT': colors.texture_paint_color,
            'POSE': colors.pose_mode_color,
            'PAINT_GPENCIL': colors.gpencil_draw_color,
            'EDIT_GPENCIL': colors.edit_mode_color,
            'SCULPT_GPENCIL': colors.sculpt_mode_color,
            'VERTEX_GPENCIL': colors.vertex_paint_color,
            'WEIGHT_GPENCIL': colors.weight_paint_color,
            'SCULPT_CURVES': colors.sculpt_mode_color,
            'PARTICLE_EDIT': colors.edit_mode_color,
        }
        
        if mode in mode_map:
            target_color = mode_map[mode]

        # Apply Colors
        theme.view_3d.space.header = target_color
        
        if prefs.affect_properties_editor:
            theme.properties.space.header = target_color
        else:
            if colors.has_backup:
                theme.properties.space.header = colors.original_props_color

        # 4. Handle Animation Playback Highlight
        if is_playing is None:
            screen = bpy.context.screen
            is_playing = screen.is_animation_playing if (screen and hasattr(screen, "is_animation_playing")) else False
        
        if prefs.affect_animation_editors and is_playing:
            if prefs.color_timeline_dopesheet:
                theme.dopesheet_editor.space.header = colors.animation_play_color
            else:
                if colors.has_backup:
                    theme.dopesheet_editor.space.header = colors.original_dopesheet_color

            if prefs.color_graph_editor:
                theme.graph_editor.space.header = colors.animation_play_color
            else:
                if colors.has_backup:
                    theme.graph_editor.space.header = colors.original_graph_color

            if prefs.color_nla_editor:
                theme.nla_editor.space.header = colors.animation_play_color
            else:
                if colors.has_backup:
                    theme.nla_editor.space.header = colors.original_nla_color
        else:
            if colors.has_backup:
                theme.dopesheet_editor.space.header = colors.original_dopesheet_color
                theme.graph_editor.space.header = colors.original_graph_color
                theme.nla_editor.space.header = colors.original_nla_color

        _redraw_ui()
                
    except Exception:
        pass

def _redraw_ui():
    for area in bpy.context.screen.areas:
        if area.type in {'VIEW_3D', 'PROPERTIES', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}:
            area.tag_redraw()

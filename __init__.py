import bpy

# Support for dynamic reloading in Blender
if "properties" in locals():
    import importlib
    importlib.reload(palettes)
    importlib.reload(properties)
    importlib.reload(core)
    importlib.reload(operators)
    importlib.reload(preferences)
    importlib.reload(drawing)
    importlib.reload(handlers)
else:
    from . import palettes
    from . import properties
    from . import core
    from . import operators
    from . import preferences
    from . import drawing
    from . import handlers

classes = (
    properties.HeaderColorProperties,
    operators.PREFERENCES_OT_save_preset,
    operators.PREFERENCES_OT_load_preset,
    operators.PREFERENCES_OT_reset_header_colors,
    operators.PREFERENCES_OT_cycle_palette,
    preferences.HeaderColorAddonPreferences,
    operators.HEADER_OT_toggle_color_mode,
    preferences.VIEW3D_PT_header_color_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    handlers.subscribe_to_mode_changes()
    
    # Register animation playback handlers
    if handlers.playback_started_handler not in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.append(handlers.playback_started_handler)
    if handlers.playback_stopped_handler not in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.append(handlers.playback_stopped_handler)
        
    # Register GPU overlay handler
    if drawing.draw_handler is None:
        drawing.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            drawing.draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL'
        )
        
    bpy.app.timers.register(lambda: (core.update_header_color(), None)[1], first_interval=0.1)
    bpy.app.handlers.load_post.append(handlers.load_post_handler)

def unregister():
    handlers.unsubscribe_from_mode_changes()

    # Unregister animation playback handlers
    if handlers.playback_started_handler in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.remove(handlers.playback_started_handler)
    if handlers.playback_stopped_handler in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.remove(handlers.playback_stopped_handler)

    # Unregister GPU overlay handler
    if drawing.draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(drawing.draw_handler, 'WINDOW')
        drawing.draw_handler = None
    drawing._shader = None
    drawing._is_animation_playing = False

    # Restore theme on unregister
    try:
        if __package__ in bpy.context.preferences.addons:
            prefs = bpy.context.preferences.addons[__package__].preferences
            theme = bpy.context.preferences.themes[0]
            core.restore_theme(prefs, theme)
    except Exception:
        pass

    if handlers.load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(handlers.load_post_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
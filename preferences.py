import bpy
from bpy.types import AddonPreferences, Panel
from bpy.props import BoolProperty, PointerProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty
from .properties import HeaderColorProperties
from .core import update_header_color

def tag_redraw_all_view3d():
    if not bpy.context or not bpy.context.window_manager:
        return
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

import time

PREVIEW_TIMEOUT = 15.0  # seconds of inactivity before HUD previews turn off
_last_touch = 0.0
_timer_running = False

def _get_prefs():
    addons = bpy.context.preferences.addons
    if __package__ not in addons:
        return None
    return addons[__package__].preferences

def reset_previews():
    """Turns both HUD previews off (used on register, file load and timeout)."""
    try:
        prefs = _get_prefs()
        if prefs is None:
            return
        if prefs.playback_overlay_preview_show:
            prefs.playback_overlay_preview_show = False
        if prefs.local_view_overlay_preview_show:
            prefs.local_view_overlay_preview_show = False
        tag_redraw_all_view3d()
    except Exception:
        pass

def _preview_timer():
    global _timer_running
    prefs = _get_prefs()
    if prefs is None or not (prefs.playback_overlay_preview_show or prefs.local_view_overlay_preview_show):
        _timer_running = False
        return None
    remaining = PREVIEW_TIMEOUT - (time.monotonic() - _last_touch)
    if remaining <= 0.0:
        _timer_running = False
        reset_previews()
        return None
    return max(remaining, 0.5)

def touch_preview(self=None, context=None):
    """Registers activity on a card setting and arms the auto-off timer if a preview is on."""
    global _last_touch, _timer_running
    tag_redraw_all_view3d()
    if self is None:
        return
    if not (self.playback_overlay_preview_show or self.local_view_overlay_preview_show):
        return
    _last_touch = time.monotonic()
    if not _timer_running:
        _timer_running = True
        bpy.app.timers.register(_preview_timer, first_interval=PREVIEW_TIMEOUT)

class HeaderColorAddonPreferences(AddonPreferences):
    bl_idname = __package__
    
    def _update_palette_preset(self, context):
        def deferred_update():
            try:
                from .palettes import PALETTES
                if not hasattr(bpy.context.preferences, 'addons') or __package__ not in bpy.context.preferences.addons:
                    return None
                prefs = bpy.context.preferences.addons[__package__].preferences
                preset_key = prefs.active_palette_preset
                if preset_key in PALETTES:
                    palette = PALETTES[preset_key]
                    from . import properties
                    properties._block_updates = True
                    try:
                        for prop_name, val in palette['colors'].items():
                            if hasattr(prefs, prop_name):
                                setattr(prefs, prop_name, val)
                            elif hasattr(prefs.header_colors, prop_name):
                                setattr(prefs.header_colors, prop_name, val)
                    finally:
                        properties._block_updates = False
                    from .core import update_header_color
                    update_header_color()
            except Exception as e:
                print(f"[Mode Highlight] Error updating preset: {e}")
            return None

        bpy.app.timers.register(deferred_update)

    active_palette_preset: EnumProperty( # type: ignore
        name="Theme Preset",
        description="Choose a built-in color scheme",
        items=[
            ('PREMIUM', "Premium Vibrant", "A modern, professional, and vibrant palette"),
            ('SUBTLE', "Classic Subtle", "The classic desaturated mode colors"),
            ('CYBERPUNK', "Neon Cyberpunk", "High-contrast glowing neon colors"),
            ('PASTEL', "Pastel Dream", "Soft, calming pastel tones"),
            ('SOFTIMAGE', "Softimage XSI", "A classic palette styled after Softimage XSI"),
        ],
        default='SUBTLE',
        update=_update_palette_preset
    )

    header_color_enabled: BoolProperty( # type: ignore
        name="Enable Header Color Changes",
        default=True,
        description="Enable automatic header color changes based on mode",
        update=lambda self, context: update_header_color()
    )

    use_auto_contrast_text: BoolProperty( # type: ignore
        name="Auto Contrast Legibility",
        default=False,
        description="Automatically adjust header background brightness to ensure text and menus remain readable",
        update=lambda self, context: update_header_color()
    )
    
    show_in_n_panel: BoolProperty( # type: ignore
        name="Show in N-Panel (N-Panel > View > Mode Highlight)",
        default=False,
        description="Show the addon panel in the 3D View Sidebar (N-Panel)",
    )

    affect_view3d_editor: BoolProperty( # type: ignore
        name="Colorize 3D Viewport Header",
        default=True,
        description="Change the Header color of the 3D Viewport.",
        update=lambda self, context: update_header_color()
    )

    affect_properties_editor: BoolProperty( # type: ignore
        name="Colorize Properties Editor Header",
        default=True,
        description="Change the Header color of the Properties Editor.",
        update=lambda self, context: update_header_color()
    )

    affect_animation_editors: BoolProperty( # type: ignore
        name="Colorize Animation Editors",
        default=True,
        description="Change the Header color of the selected Animation editors during playback.",
        update=lambda self, context: update_header_color()
    )

    color_timeline_dopesheet: BoolProperty( # type: ignore
        name="Timeline/Dope Sheet",
        default=True,
        description="Colorize Timeline/Dope Sheet header during playback.",
        update=lambda self, context: update_header_color()
    )

    color_graph_editor: BoolProperty( # type: ignore
        name="Graph Editor",
        default=True,
        description="Colorize Graph Editor header during playback.",
        update=lambda self, context: update_header_color()
    )

    color_nla_editor: BoolProperty( # type: ignore
        name="NLA Editor",
        default=True,
        description="Colorize Non-Linear Animation (NLA) Editor header during playback.",
        update=lambda self, context: update_header_color()
    )

    draw_playback_overlay: BoolProperty( # type: ignore
        name="Show Viewport Playback Overlay",
        default=True,
        description="Draw a visual PLAY indicator in the 3D Viewport when animation is playing.",
        update=lambda self, context: tag_redraw_all_view3d()
    )

    playback_overlay_pos_mode: EnumProperty( # type: ignore
        name="Position Mode",
        description="Choose where the playback overlay is positioned",
        items=[
            ('CENTER_TOP', "Center Top", "Centered at the top of the viewport"),
            ('CUSTOM', "Custom Coordinate", "Manually position using percentages"),
        ],
        default='CENTER_TOP',
        update=touch_preview
    )

    playback_overlay_percent_x: FloatProperty( # type: ignore
        name="X Position %",
        description="Horizontal position as a percentage of viewport width",
        min=0.0,
        max=100.0,
        default=50.0,
        update=touch_preview
    )

    playback_overlay_percent_y: FloatProperty( # type: ignore
        name="Y Position %",
        description="Vertical position as a percentage of viewport height",
        min=0.0,
        max=100.0,
        default=90.0,
        update=touch_preview
    )

    playback_overlay_font_size: IntProperty( # type: ignore
        name="Font Size",
        description="Font size of the overlay text",
        min=8,
        max=32,
        default=13,
        update=touch_preview
    )

    playback_overlay_use_custom_accent: BoolProperty( # type: ignore
        name="Use Custom Accent Color",
        description="Override the playback color with a custom accent color",
        default=False,
        update=touch_preview
    )

    playback_overlay_accent_color: FloatVectorProperty( # type: ignore
        name="Accent Color",
        description="Color of the left border accent line",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.08, 0.45, 0.18, 1.0),
        update=touch_preview
    )

    playback_overlay_bg_color: FloatVectorProperty( # type: ignore
        name="Background Color",
        description="Color of the overlay card background",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.08, 0.08, 0.08),
        update=touch_preview
    )

    playback_overlay_bg_alpha: FloatProperty( # type: ignore
        name="Background Opacity",
        description="Transparency of the overlay card background",
        min=0.0,
        max=1.0,
        default=0.85,
        update=touch_preview
    )

    playback_overlay_preview_show: BoolProperty( # type: ignore
        name="Show HUD Preview",
        description="Force-draw the playing overlay in the viewport for positioning and testing",
        default=False,
        update=touch_preview
    )

    playback_overlay_show_customization: BoolProperty( # type: ignore
        name="Show Customization",
        description="Show/hide customization options for the playback overlay",
        default=False
    )

    draw_local_view_overlay: BoolProperty( # type: ignore
        name="Show Local View Overlay",
        default=True,
        description="Draw a visual LOCAL VIEW indicator in the 3D Viewport when in Local View mode.",
        update=lambda self, context: tag_redraw_all_view3d()
    )

    local_view_overlay_pos_mode: EnumProperty( # type: ignore
        name="Position Mode",
        description="Choose where the local view overlay is positioned",
        items=[
            ('CENTER_TOP', "Center Top", "Centered at the top of the viewport"),
            ('CUSTOM', "Custom Coordinate", "Manually position using percentages"),
        ],
        default='CENTER_TOP',
        update=touch_preview
    )

    local_view_overlay_percent_x: FloatProperty( # type: ignore
        name="X Position %",
        description="Horizontal position as a percentage of viewport width",
        min=0.0,
        max=100.0,
        default=50.0,
        update=touch_preview
    )

    local_view_overlay_percent_y: FloatProperty( # type: ignore
        name="Y Position %",
        description="Vertical position as a percentage of viewport height",
        min=0.0,
        max=100.0,
        default=90.0,
        update=touch_preview
    )

    local_view_overlay_font_size: IntProperty( # type: ignore
        name="Font Size",
        description="Font size of the overlay text",
        min=8,
        max=32,
        default=13,
        update=touch_preview
    )

    local_view_overlay_use_custom_accent: BoolProperty( # type: ignore
        name="Use Custom Accent Color",
        description="Override the local view color with a custom accent color",
        default=False,
        update=touch_preview
    )

    local_view_overlay_accent_color: FloatVectorProperty( # type: ignore
        name="Accent Color",
        description="Color of the left border accent line",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.8, 0.45, 0.08, 1.0),
        update=touch_preview
    )

    local_view_overlay_bg_color: FloatVectorProperty( # type: ignore
        name="Background Color",
        description="Color of the overlay card background",
        subtype='COLOR_GAMMA',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.08, 0.08, 0.08),
        update=touch_preview
    )

    local_view_overlay_bg_alpha: FloatProperty( # type: ignore
        name="Background Opacity",
        description="Transparency of the overlay card background",
        min=0.0,
        max=1.0,
        default=0.85,
        update=touch_preview
    )

    local_view_overlay_preview_show: BoolProperty( # type: ignore
        name="Show HUD Preview",
        description="Force-draw the local view overlay in the viewport for positioning and testing",
        default=False,
        update=touch_preview
    )

    local_view_overlay_show_customization: BoolProperty( # type: ignore
        name="Show Customization",
        description="Show/hide customization options for the local view overlay",
        default=False
    )
    
    draw_mode_outline: BoolProperty( # type: ignore
        name="Show Viewport Outline",
        default=False,
        description="Draw a colored outline around the 3D Viewport using the active mode color",
        update=lambda self, context: tag_redraw_all_view3d()
    )

    mode_outline_thickness: IntProperty( # type: ignore
        name="Thickness",
        description="Outline thickness in pixels",
        min=1, max=30, default=4,
        update=lambda self, context: tag_redraw_all_view3d()
    )

    mode_outline_opacity: FloatProperty( # type: ignore
        name="Opacity",
        description="Opacity of the outline",
        min=0.0, max=1.0, default=0.9,
        update=lambda self, context: tag_redraw_all_view3d()
    )

    draw_mode_name: BoolProperty( # type: ignore
        name="Show Mode Name",
        default=False,
        description="Draw the name of the active mode in the 3D Viewport",
        update=lambda self, context: tag_redraw_all_view3d()
    )

    mode_name_percent_x: FloatProperty( # type: ignore
        name="X Position %",
        description="Horizontal position as a percentage of viewport width",
        min=0.0, max=100.0, default=50.0,
        update=lambda self, context: tag_redraw_all_view3d()
    )

    mode_name_percent_y: FloatProperty( # type: ignore
        name="Y Position %",
        description="Vertical position as a percentage of viewport height",
        min=0.0, max=100.0, default=5.0,
        update=lambda self, context: tag_redraw_all_view3d()
    )

    mode_name_font_size: IntProperty( # type: ignore
        name="Font Size",
        description="Font size of the mode name",
        min=8, max=48, default=14,
        update=lambda self, context: tag_redraw_all_view3d()
    )

    settings_tab: EnumProperty( # type: ignore
        name="Settings Tab",
        description="Choose which settings to display",
        items=[
            ('GENERAL', "General", "General settings for the addon", 'PREFERENCES', 0),
            ('HEADER', "Header Highlight", "Customize header coloring per mode", 'COLOR', 1),
            ('CARDS', "Card Highlight", "Customize viewport card overlays", 'STICKY_UVS_LOC', 2),
            ('OUTLINE', "Outline & Name", "Viewport outline and mode name", 'MESH_PLANE', 3),
        ],
        default='GENERAL'
    )

    header_colors: PointerProperty( # type: ignore
        type=HeaderColorProperties
        )

    def draw(self, context):
        layout = self.layout
        
        # Tab selector
        row_tabs = layout.row(align=True)
        row_tabs.prop(self, "settings_tab", expand=True)
        layout.separator()
        
        if self.settings_tab == 'GENERAL':
            col = layout.column(align=True)
            col.prop(self, "header_color_enabled")
            col.prop(self, "use_auto_contrast_text")
            col.prop(self, "affect_view3d_editor")
            col.prop(self, "affect_properties_editor")
            col.prop(self, "affect_animation_editors")
            col.prop(self, "show_in_n_panel")
            
        elif self.settings_tab == 'HEADER':
            if not self.header_color_enabled:
                layout.label(text="Header coloring is disabled. Enable it in the General tab.", icon="INFO")
            else:
                row_preset = layout.row(align=True)
                row_preset.label(text="Theme Preset:")
                row_preset.prop(self, "active_palette_preset", text="")
                row_preset.operator("preferences.cycle_palette", text="Cycle Theme", icon="LOOP_BACK")
                
                layout.separator()
                
                row = layout.row()
                row.label(text="Mode Colors:", icon="COLOR")
                row.operator("preferences.save_preset", text="Save Preset", icon="EXPORT")
                row.operator("preferences.load_preset", text="Load Preset", icon="IMPORT")
                
                split = layout.split(factor=0.5)
                
                col1 = split.column(align=True)
                # Object Mode
                row = col1.row(align=True)
                row.prop(self.header_colors, "use_object_mode_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_object_mode_color
                sub.prop(self.header_colors, "object_mode_color")
                
                # Edit Mode
                row = col1.row(align=True)
                row.prop(self.header_colors, "use_edit_mode_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_edit_mode_color
                sub.prop(self.header_colors, "edit_mode_color")
                
                # Sculpt Mode
                row = col1.row(align=True)
                row.prop(self.header_colors, "use_sculpt_mode_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_sculpt_mode_color
                sub.prop(self.header_colors, "sculpt_mode_color")
                
                # Pose Mode
                row = col1.row(align=True)
                row.prop(self.header_colors, "use_pose_mode_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_pose_mode_color
                sub.prop(self.header_colors, "pose_mode_color")
                
                col2 = split.column(align=True)
                # Vertex Paint
                row = col2.row(align=True)
                row.prop(self.header_colors, "use_vertex_paint_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_vertex_paint_color
                sub.prop(self.header_colors, "vertex_paint_color")
                
                # Weight Paint
                row = col2.row(align=True)
                row.prop(self.header_colors, "use_weight_paint_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_weight_paint_color
                sub.prop(self.header_colors, "weight_paint_color")
                
                # Texture Paint
                row = col2.row(align=True)
                row.prop(self.header_colors, "use_texture_paint_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_texture_paint_color
                sub.prop(self.header_colors, "texture_paint_color")
                
                # Grease Pencil
                row = col2.row(align=True)
                row.prop(self.header_colors, "use_gpencil_draw_color", text="")
                sub = row.row(align=True)
                sub.active = self.header_colors.use_gpencil_draw_color
                sub.prop(self.header_colors, "gpencil_draw_color")
                
                if self.affect_animation_editors:
                    layout.separator()
                    row = layout.row(align=True)
                    row.prop(self.header_colors, "use_animation_play_color", text="")
                    sub = row.row(align=True)
                    sub.active = self.header_colors.use_animation_play_color
                    sub.prop(self.header_colors, "animation_play_color")
                    
                    col_sub = layout.column(align=True)
                    col_sub.label(text="Animation Target Editors:")
                    row_sub = col_sub.row(align=True)
                    row_sub.prop(self, "color_timeline_dopesheet")
                    row_sub.prop(self, "color_graph_editor")
                    row_sub.prop(self, "color_nla_editor")
                    
        elif self.settings_tab == 'CARDS':
            split = layout.split(factor=0.5)
            
            # --- Column 1: Playback Overlay ---
            col_play = split.column()
            col_play.label(text="Viewport Playback Overlay", icon="PLAY")
            col_play.prop(self, "draw_playback_overlay", text="Enable Overlay")
            
            sub_play = col_play.column(align=True)
            sub_play.active = self.draw_playback_overlay
            sub_play.prop(self, "playback_overlay_pos_mode", text="Position Mode")
            
            if self.playback_overlay_pos_mode == 'CUSTOM':
                row_pos = sub_play.row(align=True)
                row_pos.prop(self, "playback_overlay_percent_x", text="X %")
                row_pos.prop(self, "playback_overlay_percent_y", text="Y %")
                
            sub_play.prop(self, "playback_overlay_font_size", text="Font Size")
            
            row_bg = sub_play.row(align=True)
            row_bg.prop(self, "playback_overlay_bg_color", text="Background")
            row_bg.prop(self, "playback_overlay_bg_alpha", text="Opacity")
            
            col_accent = sub_play.column(align=True)
            col_accent.prop(self, "playback_overlay_use_custom_accent", text="Custom Accent Color")
            if self.playback_overlay_use_custom_accent:
                col_accent.prop(self, "playback_overlay_accent_color", text="")
            
            sub_play.separator()
            preview_icon = 'HIDE_OFF' if self.playback_overlay_preview_show else 'HIDE_ON'
            preview_text = "Hide HUD Preview" if self.playback_overlay_preview_show else "Show HUD Preview"
            sub_play.prop(self, "playback_overlay_preview_show", text=preview_text, icon=preview_icon, toggle=True)
            
            # --- Column 2: Local View Overlay ---
            col_local = split.column()
            col_local.label(text="Viewport Local View Overlay", icon="STICKY_UVS_LOC")
            col_local.prop(self, "draw_local_view_overlay", text="Enable Overlay")
            
            sub_local = col_local.column(align=True)
            sub_local.active = self.draw_local_view_overlay
            sub_local.prop(self, "local_view_overlay_pos_mode", text="Position Mode")
            
            if self.local_view_overlay_pos_mode == 'CUSTOM':
                row_pos = sub_local.row(align=True)
                row_pos.prop(self, "local_view_overlay_percent_x", text="X %")
                row_pos.prop(self, "local_view_overlay_percent_y", text="Y %")
                
            sub_local.prop(self, "local_view_overlay_font_size", text="Font Size")
            
            row_bg = sub_local.row(align=True)
            row_bg.prop(self, "local_view_overlay_bg_color", text="Background")
            row_bg.prop(self, "local_view_overlay_bg_alpha", text="Opacity")
            
            col_accent = sub_local.column(align=True)
            col_accent.prop(self, "local_view_overlay_use_custom_accent", text="Custom Accent Color")
            if self.local_view_overlay_use_custom_accent:
                col_accent.prop(self, "local_view_overlay_accent_color", text="")
            
            sub_local.separator()
            preview_icon = 'HIDE_OFF' if self.local_view_overlay_preview_show else 'HIDE_ON'
            preview_text = "Hide HUD Preview" if self.local_view_overlay_preview_show else "Show HUD Preview"
            sub_local.prop(self, "local_view_overlay_preview_show", text=preview_text, icon=preview_icon, toggle=True)
            
        elif self.settings_tab == 'OUTLINE':
            col = layout.column(align=True)
            col.prop(self, "draw_mode_outline")
            sub = col.column(align=True)
            sub.active = self.draw_mode_outline
            sub.prop(self, "mode_outline_thickness")
            sub.prop(self, "mode_outline_opacity")
            layout.label(text="Uses the mode colors from the Header Highlight tab.", icon="INFO")

            layout.separator()
            col = layout.column(align=True)
            col.prop(self, "draw_mode_name")
            sub = col.column(align=True)
            sub.active = self.draw_mode_name
            row = sub.row(align=True)
            row.prop(self, "mode_name_percent_x", text="X %")
            row.prop(self, "mode_name_percent_y", text="Y %")
            sub.prop(self, "mode_name_font_size")

        layout.separator()
        reset_row = layout.row()
        reset_row.operator("preferences.reset_header_colors", text="Reset to Defaults", icon="LOOP_BACK")

class VIEW3D_PT_header_color_panel(Panel):
    bl_label = "Mode Highlight"
    bl_idname = "VIEW3D_PT_header_color_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.preferences.addons.get(__package__):
            return False
        return context.preferences.addons[__package__].preferences.show_in_n_panel
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="BRUSH_DATA")
    
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        layout.prop(prefs, "header_color_enabled", text="Enable Mode Colors")
        
        if prefs.header_color_enabled:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Theme Preset:")
            row = col.row(align=True)
            row.prop(prefs, "active_palette_preset", text="")
            row.operator("preferences.cycle_palette", text="", icon="LOOP_BACK")
        
        layout.operator("preferences.addon_show", text="Open Preferences", icon="PREFERENCES").module = __package__

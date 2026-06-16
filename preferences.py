import bpy
from bpy.types import AddonPreferences, Panel
from bpy.props import BoolProperty, PointerProperty, EnumProperty
from .properties import HeaderColorProperties
from .core import update_header_color

class HeaderColorAddonPreferences(AddonPreferences):
    bl_idname = __package__
    
    def _update_palette_preset(self, context):
        from .palettes import PALETTES
        if self.active_palette_preset in PALETTES:
            palette = PALETTES[self.active_palette_preset]
            for prop_name, color_val in palette['colors'].items():
                setattr(self.header_colors, prop_name, color_val)
            update_header_color()

    active_palette_preset: EnumProperty( # type: ignore
        name="Theme Preset",
        description="Choose a built-in color scheme",
        items=[
            ('PREMIUM', "Premium Vibrant", "A modern, professional, and vibrant palette"),
            ('SUBTLE', "Classic Subtle", "The classic desaturated mode colors"),
            ('CYBERPUNK', "Neon Cyberpunk", "High-contrast glowing neon colors"),
            ('PASTEL', "Pastel Dream", "Soft, calming pastel tones"),
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
    
    show_in_n_panel: BoolProperty( # type: ignore
        name="Show in N-Panel (N-Panel > View > Mode Highlight)",
        default=False,
        description="Show the addon panel in the 3D View Sidebar (N-Panel)",
    )

    affect_properties_editor: BoolProperty( # type: ignore
        name="Colorize Properties Editor Header",
        default=True,
        description="Also change the Navigation Bar and Header of the Properties Editor.",
        update=lambda self, context: update_header_color()
    )

    affect_animation_editors: BoolProperty( # type: ignore
        name="Colorize Animation Editors Header",
        default=True,
        description="Also change designated animation editor headers when playing animation.",
        update=lambda self, context: update_header_color()
    )

    color_timeline_dopesheet: BoolProperty( # type: ignore
        name="Timeline / Dope Sheet",
        default=True,
        description="Colorize Timeline and Dope Sheet headers during playback.",
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
        update=lambda self, context: context.area.tag_redraw() if context.area else None
    )
    
    header_colors: PointerProperty( # type: ignore
        type=HeaderColorProperties
        )

    def draw(self, context):
        layout = self.layout
        
        # General Settings
        box = layout.box()
        box.label(text="General Settings", icon="PREFERENCES")

        col = box.column(align=True)
        col.prop(self, "header_color_enabled")
        col.prop(self, "affect_properties_editor")
        col.prop(self, "affect_animation_editors")
        col.prop(self, "draw_playback_overlay")
        col.prop(self, "show_in_n_panel")
        
        # Color Settings
        if self.header_color_enabled:
            # 1. Mode Colors Box
            box_colors = layout.box()
            
            # Theme Preset row
            row_preset = box_colors.row(align=True)
            row_preset.label(text="Theme Preset:")
            row_preset.prop(self, "active_palette_preset", text="")
            row_preset.operator("preferences.cycle_palette", text="Cycle Theme", icon="LOOP_BACK")
            
            box_colors.separator()
            
            row = box_colors.row()
            row.label(text="Mode Colors:", icon="COLOR")
            
            # JSON Preset Buttons
            row.operator("preferences.save_preset", text="Save Preset", icon="EXPORT")
            row.operator("preferences.load_preset", text="Load Preset", icon="IMPORT")

            split = box_colors.split(factor=0.5)
            
            col1 = split.column(align=True)
            col1.prop(self.header_colors, "object_mode_color")
            col1.prop(self.header_colors, "edit_mode_color")
            col1.prop(self.header_colors, "sculpt_mode_color")
            col1.prop(self.header_colors, "pose_mode_color")
            
            col2 = split.column(align=True)
            col2.prop(self.header_colors, "vertex_paint_color")
            col2.prop(self.header_colors, "weight_paint_color")
            col2.prop(self.header_colors, "texture_paint_color")
            col2.prop(self.header_colors, "gpencil_draw_color")
            
            # 2. Animation Playback (Sibling Box)
            if self.affect_animation_editors:
                box_anim = layout.box()
                box_anim.label(text="Animation Playback:", icon="PLAY")
                box_anim.prop(self.header_colors, "animation_play_color")
                
                col_sub = box_anim.column(align=True)
                col_sub.label(text="Target Editors:")
                row_sub = col_sub.row(align=True)
                row_sub.prop(self, "color_timeline_dopesheet")
                row_sub.prop(self, "color_graph_editor")
                row_sub.prop(self, "color_nla_editor")
            
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

import bpy
import json
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from .core import update_header_color

class PREFERENCES_OT_save_preset(Operator, ExportHelper):
    bl_idname = "preferences.save_preset"
    bl_label = "Save Color Preset"
    bl_description = "Save current color configuration to a JSON file"
    bl_options = {'INTERNAL'}
    
    filename_ext = ".json"
    filter_glob: StringProperty( # type: ignore
        default="*.json", 
        options={'HIDDEN'}
        )
    
    filepath: StringProperty( # type: ignore
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = "mode_highlight_color_preset_01.json"
        return super().invoke(context, event)

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        colors = prefs.header_colors
        
        data = {
            "object_mode_color": list(colors.object_mode_color),
            "edit_mode_color": list(colors.edit_mode_color),
            "sculpt_mode_color": list(colors.sculpt_mode_color),
            "pose_mode_color": list(colors.pose_mode_color),
            "vertex_paint_color": list(colors.vertex_paint_color),
            "weight_paint_color": list(colors.weight_paint_color),
            "texture_paint_color": list(colors.texture_paint_color),
            "gpencil_draw_color": list(colors.gpencil_draw_color),
            "animation_play_color": list(colors.animation_play_color),
            "color_timeline_dopesheet": prefs.color_timeline_dopesheet,
            "color_graph_editor": prefs.color_graph_editor,
            "color_nla_editor": prefs.color_nla_editor,
            "draw_playback_overlay": prefs.draw_playback_overlay,
            "draw_local_view_overlay": prefs.draw_local_view_overlay,
            "local_view_overlay_pos_mode": prefs.local_view_overlay_pos_mode,
            "local_view_overlay_percent_x": prefs.local_view_overlay_percent_x,
            "local_view_overlay_percent_y": prefs.local_view_overlay_percent_y,
            "local_view_overlay_font_size": prefs.local_view_overlay_font_size,
            "local_view_overlay_use_custom_accent": prefs.local_view_overlay_use_custom_accent,
            "local_view_overlay_accent_color": list(prefs.local_view_overlay_accent_color),
            "local_view_overlay_bg_color": list(prefs.local_view_overlay_bg_color),
            "local_view_overlay_bg_alpha": prefs.local_view_overlay_bg_alpha,
        }
        
        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=4)
            self.report({'INFO'}, f"Preset saved: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save preset: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

class PREFERENCES_OT_load_preset(Operator, ImportHelper):
    bl_idname = "preferences.load_preset"
    bl_label = "Load Color Preset"
    bl_description = "Load color configuration from a JSON file"
    bl_options = {'INTERNAL'}
    
    filename_ext = ".json"
    filter_glob: StringProperty( # type: ignore
        default="*.json", 
        options={'HIDDEN'}
        )

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        colors = prefs.header_colors
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            
            if "object_mode_color" in data: colors.object_mode_color = data["object_mode_color"]
            if "edit_mode_color" in data: colors.edit_mode_color = data["edit_mode_color"]
            if "sculpt_mode_color" in data: colors.sculpt_mode_color = data["sculpt_mode_color"]
            if "pose_mode_color" in data: colors.pose_mode_color = data["pose_mode_color"]
            if "vertex_paint_color" in data: colors.vertex_paint_color = data["vertex_paint_color"]
            if "weight_paint_color" in data: colors.weight_paint_color = data["weight_paint_color"]
            if "texture_paint_color" in data: colors.texture_paint_color = data["texture_paint_color"]
            if "gpencil_draw_color" in data: colors.gpencil_draw_color = data["gpencil_draw_color"]
            if "animation_play_color" in data: colors.animation_play_color = data["animation_play_color"]
            if "color_timeline_dopesheet" in data: prefs.color_timeline_dopesheet = data["color_timeline_dopesheet"]
            if "color_graph_editor" in data: prefs.color_graph_editor = data["color_graph_editor"]
            if "color_nla_editor" in data: prefs.color_nla_editor = data["color_nla_editor"]
            if "draw_playback_overlay" in data: prefs.draw_playback_overlay = data["draw_playback_overlay"]
            if "draw_local_view_overlay" in data: prefs.draw_local_view_overlay = data["draw_local_view_overlay"]
            if "local_view_overlay_pos_mode" in data: prefs.local_view_overlay_pos_mode = data["local_view_overlay_pos_mode"]
            if "local_view_overlay_percent_x" in data: prefs.local_view_overlay_percent_x = data["local_view_overlay_percent_x"]
            if "local_view_overlay_percent_y" in data: prefs.local_view_overlay_percent_y = data["local_view_overlay_percent_y"]
            if "local_view_overlay_font_size" in data: prefs.local_view_overlay_font_size = data["local_view_overlay_font_size"]
            if "local_view_overlay_use_custom_accent" in data: prefs.local_view_overlay_use_custom_accent = data["local_view_overlay_use_custom_accent"]
            if "local_view_overlay_accent_color" in data: prefs.local_view_overlay_accent_color = data["local_view_overlay_accent_color"]
            if "local_view_overlay_bg_color" in data: prefs.local_view_overlay_bg_color = data["local_view_overlay_bg_color"]
            if "local_view_overlay_bg_alpha" in data: prefs.local_view_overlay_bg_alpha = data["local_view_overlay_bg_alpha"]

            update_header_color()
            self.report({'INFO'}, "Preset loaded successfully")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load preset: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class PREFERENCES_OT_reset_header_colors(Operator):
    bl_idname = "preferences.reset_header_colors"
    bl_label = "Reset Header Colors"
    bl_description = "Reset all header colors to default values"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        colors = prefs.header_colors
        
        colors.object_mode_color = (0.16, 0.16, 0.18, 0.9)
        colors.edit_mode_color = (0.14, 0.35, 0.58, 0.9)
        colors.sculpt_mode_color = (0.52, 0.26, 0.16, 0.9)
        colors.pose_mode_color = (0.44, 0.20, 0.52, 0.9)
        colors.vertex_paint_color = (0.15, 0.45, 0.28, 0.9)
        colors.weight_paint_color = (0.54, 0.38, 0.08, 0.9)
        colors.texture_paint_color = (0.10, 0.45, 0.45, 0.9)
        colors.gpencil_draw_color = (0.58, 0.18, 0.32, 0.9)
        colors.animation_play_color = (0.08, 0.45, 0.18, 0.9)

        colors.use_object_mode_color = True
        colors.use_edit_mode_color = True
        colors.use_sculpt_mode_color = True
        colors.use_pose_mode_color = True
        colors.use_vertex_paint_color = True
        colors.use_weight_paint_color = True
        colors.use_texture_paint_color = True
        colors.use_gpencil_draw_color = True
        colors.use_animation_play_color = True

        prefs.affect_view3d_editor = True
        prefs.affect_properties_editor = True
        prefs.affect_animation_editors = True
        prefs.color_timeline_dopesheet = True
        prefs.color_graph_editor = True
        prefs.color_nla_editor = True
        prefs.draw_playback_overlay = True
        prefs.draw_local_view_overlay = True
        prefs.local_view_overlay_pos_mode = 'CENTER_TOP'
        prefs.local_view_overlay_percent_x = 50.0
        prefs.local_view_overlay_percent_y = 90.0
        prefs.local_view_overlay_font_size = 13
        prefs.local_view_overlay_use_custom_accent = False
        prefs.local_view_overlay_accent_color = (0.8, 0.45, 0.08, 1.0)
        prefs.local_view_overlay_bg_color = (0.08, 0.08, 0.08)
        prefs.local_view_overlay_bg_alpha = 0.85
        prefs.local_view_overlay_preview_show = False
        prefs.use_auto_contrast_text = True
        prefs.draw_mode_outline = False
        prefs.mode_outline_thickness = 4
        prefs.mode_outline_opacity = 0.9
        prefs.draw_mode_name = False
        prefs.mode_name_percent_x = 50.0
        prefs.mode_name_percent_y = 5.0
        prefs.mode_name_font_size = 14
        prefs.settings_tab = 'GENERAL'

        update_header_color()
        self.report({'INFO'}, "Header colors reset to defaults")
        return {'FINISHED'}

class HEADER_OT_toggle_color_mode(Operator):
    bl_idname = "view3d.toggle_header_color_mode"
    bl_label = "Toggle Header Color Mode"
    bl_description = "Enable/Disable automatic header color changes"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.header_color_enabled = not prefs.header_color_enabled
        update_header_color()
        return {'FINISHED'}

class PREFERENCES_OT_cycle_palette(Operator):
    bl_idname = "preferences.cycle_palette"
    bl_label = "Cycle Color Theme"
    bl_description = "Cycle to the next built-in color preset theme"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        from .palettes import PALETTES
        keys = list(PALETTES.keys())
        
        current_preset = prefs.active_palette_preset
        if current_preset in keys:
            current_index = keys.index(current_preset)
            next_index = (current_index + 1) % len(keys)
        else:
            next_index = 0
            
        next_key = keys[next_index]
        prefs.active_palette_preset = next_key
        
        self.report({'INFO'}, f"Theme loaded: {PALETTES[next_key]['name']}")
        return {'FINISHED'}

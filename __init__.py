import bpy
import json
import blf
import gpu
import math
from gpu_extras.batch import batch_for_shader
from bpy.types import Panel, Operator, PropertyGroup, AddonPreferences
from bpy.props import FloatVectorProperty, BoolProperty, PointerProperty, StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy import msgbus
from bpy.app.handlers import persistent

# -------------------------------------------------------------------
# Data & Properties
# -------------------------------------------------------------------

class HeaderColorProperties(PropertyGroup):
    """Stores the color configuration and original theme backups."""
    
    # --- User Colors ---
    object_mode_color: FloatVectorProperty( # type: ignore
        name="Object Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.2, 0.2, 0.2, 0.8),
        update=lambda s, c: update_header_color()
    )
    edit_mode_color: FloatVectorProperty( # type: ignore
        name="Edit Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.2, 0.25, 0.35, 0.8),
        update=lambda s, c: update_header_color()
    )
    sculpt_mode_color: FloatVectorProperty( # type: ignore
        name="Sculpt Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.35, 0.25, 0.2, 0.8),
        update=lambda s, c: update_header_color()
    )
    pose_mode_color: FloatVectorProperty( # type: ignore
        name="Pose Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.3, 0.22, 0.28, 0.8),
        update=lambda s, c: update_header_color()
    )
    vertex_paint_color: FloatVectorProperty( # type: ignore
        name="Vertex Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.22, 0.3, 0.22, 0.8),
        update=lambda s, c: update_header_color()
    )
    weight_paint_color: FloatVectorProperty( # type: ignore
        name="Weight Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.35, 0.35, 0.2, 0.8),
        update=lambda s, c: update_header_color()
    )
    texture_paint_color: FloatVectorProperty( # type: ignore
        name="Texture Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.2, 0.3, 0.3, 0.8),
        update=lambda s, c: update_header_color()
    )
    gpencil_draw_color: FloatVectorProperty( # type: ignore
        name="Grease Pencil", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.28, 0.2, 0.35, 0.8),
        update=lambda s, c: update_header_color()
    )

    animation_play_color: FloatVectorProperty( # type: ignore
        name="Animation Playing", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.15, 0.35, 0.2, 0.8),
        update=lambda s, c: update_header_color()
    )

    # --- Backup Properties (Hidden) ---
    original_view3d_color: FloatVectorProperty( # type: ignore
        name="Original View3D", size=4, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    
    original_props_color: FloatVectorProperty( # type: ignore
        name="Original Properties", size=4, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_dopesheet_color: FloatVectorProperty( # type: ignore
        name="Original Dope Sheet", size=4, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_graph_color: FloatVectorProperty( # type: ignore
        name="Original Graph Editor", size=4, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_nla_color: FloatVectorProperty( # type: ignore
        name="Original NLA Editor", size=4, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    
    has_backup: BoolProperty( # type: ignore
        default=False, 
        options={'HIDDEN'}
        )

class HeaderColorAddonPreferences(AddonPreferences):
    bl_idname = __package__
    
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

# -------------------------------------------------------------------
# Operators (Presets JSON)
# -------------------------------------------------------------------

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

    # Método invoke garante que o nome padrão seja sempre aplicado
    def invoke(self, context, event):
        # Define o nome padrão ANTES de abrir o file browser
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
            
            # Apply keys if they exist in the JSON
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

            update_header_color()
            self.report({'INFO'}, "Preset loaded successfully")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load preset: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# -------------------------------------------------------------------
# Operators (General)
# -------------------------------------------------------------------

class PREFERENCES_OT_reset_header_colors(Operator):
    bl_idname = "preferences.reset_header_colors"
    bl_label = "Reset Header Colors"
    bl_description = "Reset all header colors to default values"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        colors = prefs.header_colors
        
        # Defaults
        colors.object_mode_color = (0.2, 0.2, 0.2, 0.8)
        colors.edit_mode_color = (0.2, 0.25, 0.35, 0.8)
        colors.sculpt_mode_color = (0.35, 0.25, 0.2, 0.8)
        colors.pose_mode_color = (0.3, 0.22, 0.28, 0.8)
        colors.vertex_paint_color = (0.22, 0.3, 0.22, 0.8)
        colors.weight_paint_color = (0.35, 0.35, 0.2, 0.8)
        colors.texture_paint_color = (0.2, 0.3, 0.3, 0.8)
        colors.gpencil_draw_color = (0.28, 0.2, 0.35, 0.8)
        colors.animation_play_color = (0.15, 0.35, 0.2, 0.8)

        prefs.color_timeline_dopesheet = True
        prefs.color_graph_editor = True
        prefs.color_nla_editor = True
        prefs.draw_playback_overlay = True

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

# -------------------------------------------------------------------
# UI Panel
# -------------------------------------------------------------------

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
        layout.prop(prefs, "header_color_enabled", text="Enable 'Mode Highlight' Switching")
        
        layout.operator("preferences.addon_show", text="Open Preferences", icon="PREFERENCES").module = __package__

# -------------------------------------------------------------------
# Core Logic
# -------------------------------------------------------------------

def restore_theme(prefs, theme):
    """Restores the original theme colors if a backup exists."""
    if prefs.header_colors.has_backup:
        theme.view_3d.space.header = prefs.header_colors.original_view3d_color
        # Restore properties editor color if backup exists
        theme.properties.space.header = prefs.header_colors.original_props_color
        # Restore animation editors colors if backup exists
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
            # If property editor coloring is OFF but addon is ON, keep prop editor original
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

# -------------------------------------------------------------------
# GPU Drawing Overlay
# -------------------------------------------------------------------

draw_handler = None
_is_animation_playing = False
_shader = None

def draw_callback_px(self, context):
    global _is_animation_playing, _shader
    
    # Ultra-fast early exit
    if not _is_animation_playing:
        return
        
    try:
        # Resolve dynamic context
        context = bpy.context
        
        # Safe check on space_data
        if not hasattr(context, "space_data") or not context.space_data or context.space_data.type != 'VIEW_3D':
            return
            
        if not hasattr(bpy.context.preferences, 'addons') or __package__ not in bpy.context.preferences.addons:
            return
            
        prefs = bpy.context.preferences.addons[__package__].preferences
        if not prefs.draw_playback_overlay:
            return

        # Setup font and text first to measure dimensions
        font_id = 0
        blf.size(font_id, 15)
        frame_text = f"PLAYING: {context.scene.frame_current}"
        text_w, text_h = blf.dimensions(font_id, frame_text)

        region = context.region
        width = region.width
        height = region.height

        # Dynamic layout parameters
        radius = 7
        spacing = 10
        total_w = radius * 2 + spacing + text_w

        # Position offset: Center horizontally, near the top
        start_x = (width - total_w) / 2
        y = height - 50

        # Circle position
        circle_x = start_x + radius
        # Text position
        text_x = start_x + radius * 2 + spacing

        # 1. Circle approximation via triangle fan (Pulsing Red)
        num_segments = 16
        
        # Pulse alpha between 0.35 and 1.0 based on current frame
        pulse = math.sin(context.scene.frame_current * 0.15) * 0.325 + 0.675
        
        vertices = [(circle_x, y)]
        for i in range(num_segments + 1):
            angle = i * (2.0 * math.pi / num_segments)
            vertices.append((circle_x + math.cos(angle) * radius, y + math.sin(angle) * radius))
            
        if _shader is None:
            _shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            
        batch = batch_for_shader(_shader, 'TRI_FAN', {"pos": vertices})
        
        gpu.state.blend_set('ALPHA')
        _shader.bind()
        _shader.uniform_float("color", (0.9, 0.15, 0.15, pulse))
        batch.draw(_shader)
        gpu.state.blend_set('NONE')

        # 2. Text using blf module
        # Shadow/glow effect: draw a subtle black offset first
        blf.color(font_id, 0.0, 0.0, 0.0, 0.6)
        blf.position(font_id, text_x + 1, y - 6, 0)
        blf.draw(font_id, frame_text)
        
        # Main white text
        blf.color(font_id, 1.0, 1.0, 1.0, 0.95)
        blf.position(font_id, text_x, y - 5, 0)
        blf.draw(font_id, frame_text)
        
    except Exception as e:
        import traceback
        print(f"[Mode Highlight] Error in draw_callback_px: {e}")
        traceback.print_exc()

# -------------------------------------------------------------------
# Message Bus / Registration
# -------------------------------------------------------------------

msgbus_owner = object()

def subscribe_to_mode_changes():
    msgbus.clear_by_owner(msgbus_owner)
    
    msgbus.subscribe_rna(
        key=(bpy.types.Object, "mode"),
        owner=msgbus_owner,
        args=(),
        notify=lambda: update_header_color(),
        options={'PERSISTENT'}
    )
    
    msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, "active"),
        owner=msgbus_owner,
        args=(),
        notify=lambda: update_header_color(),
        options={'PERSISTENT'}
    )

def unsubscribe_from_mode_changes():
    msgbus.clear_by_owner(msgbus_owner)

classes = (
    HeaderColorProperties,
    PREFERENCES_OT_save_preset,
    PREFERENCES_OT_load_preset,
    PREFERENCES_OT_reset_header_colors,
    HeaderColorAddonPreferences,
    HEADER_OT_toggle_color_mode,
    VIEW3D_PT_header_color_panel,
)

@persistent
def load_post_handler(dummy):
    subscribe_to_mode_changes()
    update_header_color()

@persistent
def playback_started_handler(scene, depsgraph=None):
    global _is_animation_playing
    _is_animation_playing = True
    #print("[Mode Highlight] Playback Started")
    update_header_color(is_playing=True)

@persistent
def playback_stopped_handler(scene, depsgraph=None):
    global _is_animation_playing
    _is_animation_playing = False
    #print("[Mode Highlight] Playback Stopped")
    update_header_color(is_playing=False)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    subscribe_to_mode_changes()
    
    # Register animation playback handlers
    if playback_started_handler not in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.append(playback_started_handler)
    if playback_stopped_handler not in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.append(playback_stopped_handler)
        
    # Register GPU overlay handler
    global draw_handler
    if draw_handler is None:
        draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')
        
    bpy.app.timers.register(lambda: (update_header_color(), None)[1], first_interval=0.1)
    bpy.app.handlers.load_post.append(load_post_handler)

def unregister():
    unsubscribe_from_mode_changes()

    # Unregister animation playback handlers
    if playback_started_handler in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.remove(playback_started_handler)
    if playback_stopped_handler in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.remove(playback_stopped_handler)

    # Unregister GPU overlay handler
    global draw_handler, _shader, _is_animation_playing
    if draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
        draw_handler = None
    _shader = None
    _is_animation_playing = False

    # Restore theme on unregister
    try:
        if __package__ in bpy.context.preferences.addons:
            prefs = bpy.context.preferences.addons[__package__].preferences
            theme = bpy.context.preferences.themes[0]
            restore_theme(prefs, theme)
    except Exception:
        pass

    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
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

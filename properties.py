import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatVectorProperty, BoolProperty

def _trigger_update(self, context):
    from .core import update_header_color
    update_header_color()

class HeaderColorProperties(PropertyGroup):
    """Stores the color configuration and original theme backups."""
    
    # --- User Colors ---
    object_mode_color: FloatVectorProperty( # type: ignore
        name="Object Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.16, 0.16, 0.18, 0.9),
        update=_trigger_update
    )
    edit_mode_color: FloatVectorProperty( # type: ignore
        name="Edit Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.14, 0.35, 0.58, 0.9),
        update=_trigger_update
    )
    sculpt_mode_color: FloatVectorProperty( # type: ignore
        name="Sculpt Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.52, 0.26, 0.16, 0.9),
        update=_trigger_update
    )
    pose_mode_color: FloatVectorProperty( # type: ignore
        name="Pose Mode", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.44, 0.20, 0.52, 0.9),
        update=_trigger_update
    )
    vertex_paint_color: FloatVectorProperty( # type: ignore
        name="Vertex Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.15, 0.45, 0.28, 0.9),
        update=_trigger_update
    )
    weight_paint_color: FloatVectorProperty( # type: ignore
        name="Weight Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.54, 0.38, 0.08, 0.9),
        update=_trigger_update
    )
    texture_paint_color: FloatVectorProperty( # type: ignore
        name="Texture Paint", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.10, 0.45, 0.45, 0.9),
        update=_trigger_update
    )
    gpencil_draw_color: FloatVectorProperty( # type: ignore
        name="Grease Pencil", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.58, 0.18, 0.32, 0.9),
        update=_trigger_update
    )

    animation_play_color: FloatVectorProperty( # type: ignore
        name="Animation Playing", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.08, 0.45, 0.18, 0.9),
        update=_trigger_update
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

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatVectorProperty, BoolProperty, StringProperty

_block_updates = False

def _trigger_update(self, context):
    if _block_updates:
        return
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

    # --- Mode Enable Toggles ---
    use_object_mode_color: BoolProperty( # type: ignore
        name="Use Object Mode Color", default=True, update=_trigger_update
    )
    use_edit_mode_color: BoolProperty( # type: ignore
        name="Use Edit Mode Color", default=True, update=_trigger_update
    )
    use_sculpt_mode_color: BoolProperty( # type: ignore
        name="Use Sculpt Mode Color", default=True, update=_trigger_update
    )
    use_pose_mode_color: BoolProperty( # type: ignore
        name="Use Pose Mode Color", default=True, update=_trigger_update
    )
    use_vertex_paint_color: BoolProperty( # type: ignore
        name="Use Vertex Paint Color", default=True, update=_trigger_update
    )
    use_weight_paint_color: BoolProperty( # type: ignore
        name="Use Weight Paint Color", default=True, update=_trigger_update
    )
    use_texture_paint_color: BoolProperty( # type: ignore
        name="Use Texture Paint Color", default=True, update=_trigger_update
    )
    use_gpencil_draw_color: BoolProperty( # type: ignore
        name="Use Grease Pencil Color", default=True, update=_trigger_update
    )
    use_animation_play_color: BoolProperty( # type: ignore
        name="Use Animation Play Color", default=True, update=_trigger_update
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

    # --- Backup Text Colors (Hidden) ---
    original_view3d_text: FloatVectorProperty( # type: ignore
        name="Original View3D Text", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    original_view3d_text_hi: FloatVectorProperty( # type: ignore
        name="Original View3D Text Highlight", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_props_text: FloatVectorProperty( # type: ignore
        name="Original Properties Text", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    original_props_text_hi: FloatVectorProperty( # type: ignore
        name="Original Properties Text Highlight", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_dopesheet_text: FloatVectorProperty( # type: ignore
        name="Original Dopesheet Text", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    original_dopesheet_text_hi: FloatVectorProperty( # type: ignore
        name="Original Dopesheet Text Highlight", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_graph_text: FloatVectorProperty( # type: ignore
        name="Original Graph Text", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    original_graph_text_hi: FloatVectorProperty( # type: ignore
        name="Original Graph Text Highlight", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )

    original_nla_text: FloatVectorProperty( # type: ignore
        name="Original NLA Text", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    original_nla_text_hi: FloatVectorProperty( # type: ignore
        name="Original NLA Text Highlight", size=3, subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0), options={'HIDDEN'}
    )
    
    has_backup: BoolProperty( # type: ignore
        default=False, 
        options={'HIDDEN'}
        )
    
    theme_filepath: StringProperty( # type: ignore
        default="",
        options={'HIDDEN'}
    )

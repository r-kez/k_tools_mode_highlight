import bpy
from bpy import msgbus
from bpy.app.handlers import persistent
from .core import update_header_color
from . import drawing

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

@persistent
def load_post_handler(dummy):
    subscribe_to_mode_changes()
    update_header_color()

@persistent
def playback_started_handler(scene, depsgraph=None):
    drawing._is_animation_playing = True
    update_header_color(is_playing=True)

@persistent
def playback_stopped_handler(scene, depsgraph=None):
    drawing._is_animation_playing = False
    update_header_color(is_playing=False)

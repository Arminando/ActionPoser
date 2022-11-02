import bpy

from . import ui_operators
from . import ui
from . import properties
from . import operators
from . import action_operators

bl_info = {
    "name": "Action poser",
    "description": "Action constraint based rigging",
    "author": "Armin Halac",
    "blender": (3, 1, 0),
    "version": (1, 0, 0),
    "category": "Rigging",
    "location": "Side Panel (N) -> Rig Tools",
    "wiki_url": "https://github.com/Arminando/ActionPoser",
    "doc_url": "https://github.com/Arminando/ActionPoser",
}

def register():
    from bpy.utils import register_class

    properties.register()
    operators.register()
    action_operators.register()
    ui_operators.register()
    ui.register()

def unregister():
    from bpy.utils import unregister_class

    properties.unregister()
    operators.unregister()
    action_operators.unregister()
    ui_operators.unregister()
    ui.unregister()
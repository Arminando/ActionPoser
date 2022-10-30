from email.policy import default
import bpy
from . utilities import is_valid_pose, purge_poses, create_pose, enable_pose_constraints, disable_pose_constraints, reset_bone_transforms

class DATA_OT_ap_action_new(bpy.types.Operator):
    bl_idname = "armature.ap_action_new"
    bl_label = "New Action"
    bl_description = "Creates a new action"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        prefs = context.scene.ap_preferences
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        pose_name = ap_pose.name

        action = bpy.data.actions.new(name=pose_name)
        action.use_fake_user = True

        ap_pose.action = action

        if ap_pose.type == 'POSE':
            action.name = prefs.pose_prefix + action.name
        elif ap_pose.type == 'COMBO':
            action.name = prefs.combo_prefix + action.name

        return {'FINISHED'}


class DATA_OT_ap_action_duplicate(bpy.types.Operator):
    bl_idname = "armature.ap_action_duplicate"
    bl_label = "Duplicate action"
    bl_description = "Duplicate action that is assigned to pose"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            idx = context.active_object.data.ap_poses_index
            if context.active_object.data.ap_poses[idx].action:
                return True
        return False

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        action = ap_pose.action

        new_action = action.copy()
        ap_pose.action = new_action

        return {'FINISHED'}


class DATA_OT_ap_action_delete(bpy.types.Operator):
    bl_idname = "armature.ap_action_delete"
    bl_label = "Delete action"
    bl_description = "Permanently deletes action that is assigned to pose"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            idx = context.active_object.data.ap_poses_index
            if context.active_object.data.ap_poses[idx].action:
                return True
        return False

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        action = ap_pose.action
        bpy.data.actions.remove(action)

        return {'FINISHED'}

        
### Adapted from https://github.com/Muream/actionman
class DATA_OT_ap_remove_flat_curves(bpy.types.Operator):
    bl_idname = "armature.ap_remove_flat_curves"
    bl_label = "Remove Flat Curves"
    bl_description = "Removes all curves that have no value change between keyframes"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses and ap_poses[armature.ap_poses_index].action

    def execute(self, context):
        obj = context.active_object
        armature = context.active_object.data
        armature_pose = context.active_object.pose
        ap_pose = armature.ap_poses[self.idx]
        action = ap_pose.action
        ap_state = armature.ap_state
        ap_bone_transforms = armature.ap_bone_transforms

        for fcurve in action.fcurves:
            points = fcurve.keyframe_points
            first_value = None
            is_flat_curve = True
            for point in points:
                coordinates = point.co
                value = round(coordinates[1], 5)
                if first_value is None:  # storing the value of the first point.
                    first_value = value
                else:  # comparing every point's value to the first value.
                    if value != first_value:
                        is_flat_curve = False
                        break
            if is_flat_curve:
                action.fcurves.remove(fcurve)
        
        for group in action.groups:
            if len(group.channels) == 0:
                action.groups.remove(group)
                
        self.report({'INFO'}, 'Flat curves removed')
        return {'FINISHED'}


class DATA_OT_ap_action_rename(bpy.types.Operator):
    bl_idname = "armature.ap_action_rename"
    bl_label = "Rename Action"
    bl_description = "Rename action."
    bl_options = {"REGISTER", "UNDO"}

    text: bpy.props.StringProperty(name="Name", default='')

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            idx = context.active_object.data.ap_poses_index
            if context.active_object.data.ap_poses[idx].action:
                return True
        return False

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[armature.ap_poses_index]
        action = ap_pose.action
        action.name = self.text

        return {'FINISHED'}

    def invoke(self, context, event):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[armature.ap_poses_index]
        action = ap_pose.action
        self.text = action.name
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


classes = [
    DATA_OT_ap_remove_flat_curves,
    DATA_OT_ap_action_new,
    DATA_OT_ap_action_duplicate,
    DATA_OT_ap_action_delete,
    DATA_OT_ap_action_rename,
]

register, unregister = bpy.utils.register_classes_factory(classes)
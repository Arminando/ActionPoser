import bpy
from . utilities import (find_opposite_bone_name,
                         find_opposite_object_name,
                         find_opposite_action_name, find_opposite_pose_name,
                         swap_side_suffix,
                         )

class DATA_OT_ap_pose_remove(bpy.types.Operator):
    bl_idname = "armature.ap_pose_remove"
    bl_label = "Remove action pose"
    bl_description = "Permanently deletes the pose and all of its information"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        if context.mode == 'POSE' and armature.ap_poses and armature.ap_poses[armature.ap_poses_index]:
            return True
        else:
            return False

    def execute(self, context):
        context.active_object.data.ap_poses.remove(self.idx)

        armature = context.active_object.data
        armature.ap_poses_index = 0 if self.idx == 0 else self.idx -1

        return {'FINISHED'}

PROPERTIES = [
                'name',
                'build',
                'type',
                'target_type',
                'target',
                'bone',
                'data_path',
                'channel',
                'mix',
                'space',
                'rot_mode',
                'transform_min',
                'transform_max',
                'action',
                'start_frame',
                'end_frame',
                'corr_pose_A',
                'corr_pose_B'
            ]

class DATA_OT_ap_pose_duplicate(bpy.types.Operator):
    bl_idname = "armature.ap_pose_duplicate"
    bl_label = "Duplicate action pose"
    bl_description = "Duplicates the pose including all of its properties. Does not duplicate action."
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        if context.mode == 'POSE' and armature.ap_poses and armature.ap_poses[armature.ap_poses_index]:
            return True
        else:
            return False

    def execute(self, context):
        new_pose = context.active_object.data.ap_poses.add()
        old_pose = context.active_object.data.ap_poses[self.idx]

        for prop in PROPERTIES:
            setattr(new_pose, prop, getattr(old_pose, prop))

        if old_pose.bones:
            for bone in old_pose.bones:
                new_bone = new_pose.bones.add()
                new_bone.bone = bone.bone
                new_bone.influence = bone.influence

        armature = context.active_object.data
        armature.ap_poses.move(len(armature.ap_poses) - 1, self.idx+1)
        armature.ap_poses_index = self.idx+1

        return {'FINISHED'}


class DATA_OT_ap_pose_mirror(bpy.types.Operator):
    bl_idname = "armature.ap_pose_mirror"
    bl_label = "Mirror action pose"
    bl_description = "Duplicates pose and attempts to mirror find opposite target, action and bones"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        if context.mode == 'POSE' and armature.ap_poses and armature.ap_poses[armature.ap_poses_index]:
            return True
        else:
            return False

    def execute(self, context):
        new_pose = context.active_object.data.ap_poses.add()
        old_pose = context.active_object.data.ap_poses[self.idx]
        for prop in PROPERTIES:
            setattr(new_pose, prop, getattr(old_pose, prop))

        new_pose.name = swap_side_suffix(new_pose.name)

        opposite_target = find_opposite_object_name(new_pose.target)
        if opposite_target:
            new_pose.target = opposite_target

        opposite_bone = find_opposite_bone_name(new_pose.bone)
        if opposite_bone:
            new_pose.bone = opposite_bone

        opposite_action = find_opposite_action_name(new_pose.action)
        if opposite_action:
            new_pose.bone = opposite_action

        if old_pose.bones:
            for bone in old_pose.bones:
                new_bone = new_pose.bones.add()

                opposite_bone = find_opposite_bone_name(bone.bone)
                if opposite_bone:
                    new_bone.bone = opposite_bone
                else:
                    new_bone.bone = bone.bone
                new_bone.influence = bone.influence

        opposite_pose_A = find_opposite_pose_name(old_pose.corr_pose_A)
        opposite_pose_B = find_opposite_pose_name(old_pose.corr_pose_B)
        if opposite_pose_A:
            new_pose.corr_pose_A = opposite_pose_A
        if opposite_pose_B:
            new_pose.corr_pose_B = opposite_pose_B

        armature = context.active_object.data
        armature.ap_poses.move(len(armature.ap_poses) - 1, self.idx+1)
        armature.ap_poses_index = self.idx+1

        return {'FINISHED'}


class DATA_OT_ap_pose_move(bpy.types.Operator):
    bl_idname = "armature.ap_pose_move"
    bl_label = "Move pose Up or Down"
    bl_description = "Move pose up or down in the list"
    bl_options = {"REGISTER", "UNDO"}

    direction: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        if context.mode == 'POSE' and armature.ap_poses and armature.ap_poses[armature.ap_poses_index]:
            return True
        else:
            return False

    def execute(self, context):
        armature = context.active_object.data
        idx = armature.ap_poses_index

        if self.direction == 'UP' and idx >= 1:
            armature.ap_poses.move(idx, idx-1)
            armature.ap_poses_index = idx-1

        elif self.direction == 'DOWN' and idx<len(armature.ap_poses)-1:
            armature.ap_poses.move(idx, idx+1)
            armature.ap_poses_index = idx+1

        elif self.direction == 'TOP' and idx >= 1:
            armature.ap_poses.move(idx, 0)
            armature.ap_poses_index = 0

        elif self.direction == 'BOTTOM' and idx<len(armature.ap_poses)-1:
            armature.ap_poses.move(idx, len(armature.ap_poses)-1)
            armature.ap_poses_index = len(armature.ap_poses)-1


        return {'FINISHED'}


class DATA_OT_ap_bone_add(bpy.types.Operator):
    bl_idname = "armature.ap_bone_add"
    bl_label = "Add bone to pose"
    bl_description = "Adds new item to bones list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        bones = context.active_object.data.ap_poses[self.idx].bones
        bones.add()

        context.active_object.data.ap_bones_index = len(bones) - 1

        return {'FINISHED'}

class DATA_OT_ap_bone_remove(bpy.types.Operator):
    bl_idname = "armature.ap_bone_remove"
    bl_label = "Remove bone from pose"
    bl_description = "Deletes bone from list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()
    bone_idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        context.active_object.data.ap_poses[self.idx].bones.remove(self.bone_idx)

        context.active_object.data.ap_bones_index = 0 if self.bone_idx == 0 else self.bone_idx -1

        return {'FINISHED'}

class DATA_OT_ap_bone_add_selected(bpy.types.Operator):
    bl_idname = "armature.ap_bone_add_selected"
    bl_label = "Add selected bones to pose"
    bl_description = "Adds all selected bones to list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' and context.selected_pose_bones

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        ap_bones = ap_pose.bones
        sel_bones = context.selected_pose_bones

        for sel_bone in sel_bones:
            if sel_bone.name not in [x.bone for x in ap_bones]:
                ap_bones.add()
                last_idx = len(ap_bones)
                ap_bones[last_idx-1].bone = sel_bone.name

        context.active_object.data.ap_bones_index = len(ap_bones) - 1

        return {'FINISHED'}


class DATA_OT_ap_bone_remove_selected(bpy.types.Operator):
    bl_idname = "armature.ap_bone_remove_selected"
    bl_label = "Remove selected bones to pose"
    bl_description = "Removes bones selected in scene from the list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' and context.selected_pose_bones

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        ap_bones = ap_pose.bones

        sel_bones = [x.name for x in context.selected_pose_bones]
        
        if sel_bones:
            for (i, bone) in sorted(enumerate(ap_bones), reverse=True):
                if bone.bone in sel_bones:
                    ap_bones.remove(i)


        return {'FINISHED'}


class DATA_OT_ap_bone_select_from_pose(bpy.types.Operator):
    bl_idname = "armature.ap_bone_select_from_pose"
    bl_label = "Select Pose Bones"
    bl_description = "Selects all bones that are in Bones list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            idx = context.active_object.data.ap_poses_index
            if context.active_object.data.ap_poses[idx].bones:
                return True
        return False

    def execute(self, context):
        armature = context.active_object.data
        ap_pose = armature.ap_poses[self.idx]
        ap_bones = ap_pose.bones
        
        if ap_bones:
            for ap_bone in ap_bones:
                bone = armature.bones[ap_bone.bone]
                bone.select = True

        return {'FINISHED'}


class DATA_OT_ap_bone_add_from_action(bpy.types.Operator):
    bl_idname = "armature.ap_bone_add_from_action"
    bl_label = "Add From Action"
    bl_description = "Add all bones that are keyframed in action, or select them"
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses and ap_poses[armature.ap_poses_index].action

    def execute(self, context):
        armature = context.active_object.data
        armature_pose = context.active_object.pose
        idx = armature.ap_poses_index
        ap_pose = armature.ap_poses[idx]
        ap_bones = ap_pose.bones
        action = ap_pose.action
        groups = [x.name for x in action.groups] # Groups equals to bone names
        bones_names = [x.bone for x in ap_bones]
        if self.mode == 'ADD':
            for group in groups:
                if group not in bones_names and group in armature.bones:
                    ap_bones.add()
                    last_idx = len(ap_bones)
                    ap_bones[last_idx-1].bone = group

            context.active_object.data.ap_bones_index = len(ap_bones) - 1
            

        elif self.mode == 'SELECT':
            for group in groups:
                armature_pose.bones[group].bone.select = True
                
        return {'FINISHED'}
        

class DATA_OT_ap_bone_remove_all(bpy.types.Operator):
    bl_idname = "armature.ap_bone_remove_all"
    bl_label = "Remove all bones from list"
    bl_options = {"REGISTER", "UNDO"}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses and ap_poses[armature.ap_poses_index].bones

    def execute(self, context):
        context.active_object.data.ap_poses[self.idx].bones.clear()

        return {'FINISHED'}


class DATA_OT_ap_target_set_active(bpy.types.Operator):
    bl_idname = "armature.ap_target_set_active"
    bl_label = "Use Active Bone"
    bl_description = "Set active bone as the target"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses and ap_poses[armature.ap_poses_index].type=='POSE'

    def execute(self, context):
        armature = context.active_object.data
        idx = armature.ap_poses_index
        ap_pose = armature.ap_poses[idx]

        ap_pose.target = context.active_object
        ap_pose.target_type = 'BONE'
        ap_pose.bone = context.active_pose_bone.name
                
        return {'FINISHED'}


class DATA_OT_ap_target_select(bpy.types.Operator):
    bl_idname = "armature.ap_target_select"
    bl_label = "Select Target Bone"
    bl_description = "Select target bone"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses and ap_poses[armature.ap_poses_index].bone

    def execute(self, context):
        armature = context.active_object.data
        idx = armature.ap_poses_index
        ap_pose = armature.ap_poses[idx]

        if context.active_object.name != ap_pose.target:
                bpy.ops.object.mode_set(mode='OBJECT')
                context.view_layer.objects.active = ap_pose.target
                bpy.ops.object.mode_set(mode='POSE')

        ap_pose.target.pose.bones[ap_pose.bone].bone.select = True
        ap_pose.target.data.bones.active = ap_pose.target.data.bones[ap_pose.bone]
                
        return {'FINISHED'}


classes = [
    DATA_OT_ap_pose_remove,
    DATA_OT_ap_pose_duplicate,
    DATA_OT_ap_pose_mirror,
    DATA_OT_ap_pose_move,
    DATA_OT_ap_bone_add,
    DATA_OT_ap_bone_remove,
    DATA_OT_ap_bone_remove_all,
    DATA_OT_ap_bone_add_selected,
    DATA_OT_ap_bone_remove_selected,
    DATA_OT_ap_bone_select_from_pose,
    DATA_OT_ap_bone_add_from_action,
    DATA_OT_ap_target_set_active,
    DATA_OT_ap_target_select,
]

register, unregister = bpy.utils.register_classes_factory(classes)
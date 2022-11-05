import bpy
from . utilities import (is_valid_pose,
                        purge_poses,
                        create_pose,
                        enable_pose_constraints,
                        disable_pose_constraints,
                        reset_bone_transforms,
                        delete_temp_constraints)

class DATA_OT_ap_execute(bpy.types.Operator):
    bl_idname = "armature.ap_execute"
    bl_label = "Execute"
    bl_description = "Run the creation of all poses"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        return context.mode == 'POSE' and ap_poses

    def execute(self, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        if armature.ap_state.editing:
            bpy.ops.armature.ap_action_edit(idx = armature.ap_poses_index)

        purge_poses()
        for pose in ap_poses:
            if is_valid_pose(pose) and pose.build:
                create_pose(pose)

        self.report({'INFO'}, 'Poses Created Successfully')
        return {'FINISHED'}


class DATA_OT_ap_purge(bpy.types.Operator):
    bl_idname = "armature.ap_purge"
    bl_label = "Purge"
    bl_description = "Remove all shapes data from bones"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        
        return context.mode == 'POSE'

    def execute(self, context):
        armature = context.active_object.data
        ap_poses = armature.ap_poses

        purge_poses()
        self.report({'INFO'}, 'Poses Purged Successfully')
        return {'FINISHED'}


class DATA_OT_ap_action_edit(bpy.types.Operator):
    bl_idname = "armature.ap_action_edit"
    bl_label = "Edit action"
    bl_description = "Toggle action editing mode"
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
        obj = context.active_object
        armature = context.active_object.data
        armature_pose = context.active_object.pose
        ap_pose = armature.ap_poses[self.idx]
        action = ap_pose.action
        ap_state = armature.ap_state
        ap_bone_transforms = armature.ap_bone_transforms

        if ap_state.editing == False:
            ap_state.editing = True

            # Active object store
            ap_state.active_object = obj.name

            # Active action store
            if obj.animation_data and obj.animation_data.action:
                ap_state.active_action = obj.animation_data.action.name
            
            # Selected bones store
            pose_bones = context.selected_pose_bones
            if pose_bones:
                for bone in pose_bones:
                    ap_state.selected_bones.add().name = bone.name
            
            # Active bone store
            active_bone = context.active_pose_bone
            if active_bone:
                ap_state.active_bone = active_bone.name

            # Store bone transforms
            for pose_bone in armature_pose.bones:
                bone_transform = ap_bone_transforms.add()
                bone_transform.name = pose_bone.name
                bone_transform.location = pose_bone.location
                bone_transform.rotation_euler = pose_bone.rotation_euler
                bone_transform.rotation_quaternion = pose_bone.rotation_quaternion
                bone_transform.rotation_mode = pose_bone.rotation_mode
                bone_transform.scale = pose_bone.scale
                reset_bone_transforms(pose_bone.name)

            # Assign pose action
            if not obj.animation_data:
                obj.animation_data_create()
            try:
                obj.animation_data.action = action
            except:
                self.report({'ERROR'}, "Action couldn't be assigned: %s" %(action))

            # Autokey store and set
            ap_state.autokey = context.scene.tool_settings.use_keyframe_insert_auto
            context.scene.tool_settings.use_keyframe_insert_auto = True

            # Disable constraints
            disable_pose_constraints()
            
            # Recursive enabling of combo poses.
            # Needed so that the edit combines all poses that go into combos+combos
            if ap_pose.type == 'COMBO':
                nested_pose_list = [ap_pose.corr_pose_A, ap_pose.corr_pose_B]
                while nested_pose_list:
                    pose = armature.ap_poses[nested_pose_list.pop(0)]
                    if pose.type == 'COMBO':
                        nested_pose_list.append(pose.corr_pose_A)
                        nested_pose_list.append(pose.corr_pose_B)
                    create_pose(pose, for_edit=True)
            self.report({'INFO'}, 'Action Edit engaged')

        else:
            ap_state.editing = False
            context.scene.tool_settings.use_keyframe_insert_auto = False

            # Active object restore
            if context.active_object.name != ap_state.active_object:
                bpy.ops.object.mode_set(mode='OBJECT')
                context.view_layer.objects.active = bpy.data.objects[ap_state.active_object]
                bpy.ops.object.mode_set(mode='POSE')
            ap_state.active_object = ""

            # Active action restore
            if not obj.animation_data:
                obj.animation_data_create()

            if ap_state.active_action:
                try:
                    obj.animation_data.action = bpy.data.actions[ap_state.active_action]
                except:
                    self.report({'ERROR'}, "Action couldn't be assigned: %s" %(ap_state.active_action))
            else:
                obj.animation_data.action = None
            ap_state.active_action = ""

            # Selected bones restore
            for bone in armature_pose.bones:
                bone.bone.select = False
                reset_bone_transforms(bone.name)
                bone.location = ap_bone_transforms[bone.name].location
                bone.rotation_euler = ap_bone_transforms[bone.name].rotation_euler
                bone.rotation_quaternion = ap_bone_transforms[bone.name].rotation_quaternion
                bone.rotation_mode = ap_bone_transforms[bone.name].rotation_mode
                bone.scale = ap_bone_transforms[bone.name].scale
            if ap_state.selected_bones:
                for bone in ap_state.selected_bones:
                    armature_pose.bones[bone.name].bone.select = True
            ap_state.selected_bones.clear()

            # Active bone restore
            if ap_state.active_bone:
                armature.bones.active = armature.bones[ap_state.active_bone]
            ap_state.active_bone = ""

            # Bone transforms clear
            ap_bone_transforms.clear()

            # Enable Constraints
            delete_temp_constraints()
            enable_pose_constraints()

            #Autokey restore
            context.scene.tool_settings.use_keyframe_insert_auto = ap_state.autokey
                
            self.report({'INFO'}, 'Action Edit disabled')

        return {'FINISHED'}

class DATA_OT_ap_copy(bpy.types.Operator):
    bl_idname = "armature.ap_copy"
    bl_label = "Copy to Selected"
    bl_description = "Copy Action Poses data from active to selected"
    bl_options = {"REGISTER", "UNDO"}

    mode : bpy.props.EnumProperty(name='Mode', description='Choose copy mode', items={('ALL', 'All', 'All', 0), ('ACTIVE', 'Active', 'Active', 1)}, default='ALL')

    @classmethod
    def poll(cls, context):

        return context.mode == 'POSE' and context.active_object and len(context.selected_objects)>=2

    def execute(self, context):
        source_obj = context.active_object
        target_objs = context.selected_objects
        target_objs.remove(source_obj)

        source = source_obj.data.ap_poses

        for target_obj in target_objs:
            target = target_obj.data.ap_poses

            if self.mode=='ALL':
                for source_pose in source:
                    pose = target.add()
                    for k, v in source_pose.items():
                        pose[k] = v
            elif self.mode=='ACTIVE':
                source_pose_index = source_obj.data.ap_poses_index
                pose = target.add()
                for k,v in source_obj.data.ap_poses[source_pose_index].items():
                    pose[k] = v

        self.report({'INFO'}, 'Poses Copied Successfully')
        return {'FINISHED'}


class DATA_OT_ap_clear(bpy.types.Operator):
    bl_idname = "armature.ap_clear"
    bl_label = "Delete All"
    bl_description = "Remove all Action Poses"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):

        return context.mode == 'POSE' and context.active_object

    def execute(self, context):
        context.active_object.data.ap_poses.clear()

        self.report({'INFO'}, 'Poses Deleted Successfully')
        return {'FINISHED'}

classes = [
    DATA_OT_ap_execute,
    DATA_OT_ap_purge,
    DATA_OT_ap_action_edit,
    DATA_OT_ap_copy,
    DATA_OT_ap_clear,
]

register, unregister = bpy.utils.register_classes_factory(classes)
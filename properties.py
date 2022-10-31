import bpy
from . utilities import poll_is_armature_object, update_ap_poses_index

class APBones(bpy.types.PropertyGroup):
    bone : bpy.props.StringProperty(name='Bone', default='', description='Bone that will be animated in pose.')
    influence : bpy.props.FloatProperty(name='Influnce', default=1.0, min=0.0, max=1.0, precision=3)

class APPoses(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Pose Name", default="",description="Name of pose")
    build : bpy.props.BoolProperty(name="Build", default = True, description="Exclude pose when build is executed")
    type : bpy.props.EnumProperty(name='Type', description='Type of action pose', items={('POSE', 'Pose', 'Pose', 0), ('COMBO', 'Combo', 'Combo', 1)}, default='POSE')
    target_type : bpy.props.EnumProperty(name='Target Type', description='Choose if the pose will be driven by a property or bone transform', items={('BONE', 'Bone', 'Bone', 0), ('PROP', 'Property', 'Property', 1)}, default='BONE')

    # Pose type
    target : bpy.props.PointerProperty(type=bpy.types.Object, poll=poll_is_armature_object, name='Target', description='Target object')
    bone : bpy.props.StringProperty(name='Bone', default='', description='Target bone that will be the shape driver')
    data_path : bpy.props.StringProperty(name='Path', default='', description='Target path that will be the shape driver')
    channel : bpy.props.EnumProperty(name='Channel', description='Bone channel that will drive the action', items={
                                                                                                                    ('LOCATION_X', 'Location X', 'Location X', 0),
                                                                                                                    ('LOCATION_Y', 'Location Y', 'Location Y', 1),
                                                                                                                    ('LOCATION_Z', 'Location Z', 'Location Z', 2),
                                                                                                                    ('ROTATION_X', 'Rotation X', 'Rotation X', 3),
                                                                                                                    ('ROTATION_Y', 'Rotation Y', 'Rotation Y', 4),
                                                                                                                    ('ROTATION_Z', 'Rotation Z', 'Rotation Z', 5),
                                                                                                                    ('SCALE_X', 'Scale X', 'Scale X', 6),
                                                                                                                    ('SCALE_Y', 'Scale Y', 'Scale Y', 7),
                                                                                                                    ('SCALE_Z', 'Scale Z', 'Scale Z', 8),})
    mix : bpy.props.EnumProperty(name='Mix', description='Bone channel that will drive the action', items={
                                                                                                                    ('BEFORE_FULL', 'Before Original(Full)', 'Before Original(Full)', 0),
                                                                                                                    ('BEFORE', 'Before Original(Aligned)', 'Before Original(Aligned)', 1),
                                                                                                                    ('BEFORE_SPLIT', 'Before Original(Split Channels)', 'Before Original(Split Channels)', 2),
                                                                                                                    ('AFTER_FULL', 'After Original (Full)', 'After Original (Full)', 3),
                                                                                                                    ('AFTER', 'After Original (Aligned)', 'After Original (Aligned)', 4),
                                                                                                                    ('AFTER_SPLIT', 'After Original (Split Channels)', 'After Original (Split Channels)', 5)}, default='BEFORE_FULL')
    space : bpy.props.EnumProperty(name='Space', description='Choose which space to use for driver transform', items={('LOCAL', 'Local', 'Local Space', 0), ('WORLD', 'World', 'World', 1)}, default='LOCAL')
    transform_min : bpy.props.FloatProperty(name='Min', default = 0.0, description='Starting value for the driver', precision=4)
    transform_max : bpy.props.FloatProperty(name='Max', default = 1.0, description='Finishing value for the driver', precision=4)

    corr_pose_A : bpy.props.StringProperty(name='Pose A', description='Pose that will trigger the combo')
    corr_pose_B : bpy.props.StringProperty(name='Pose B', description='Pose that will trigger the combo')

    action : bpy.props.PointerProperty(type=bpy.types.Action, name='Action', description='Target action')
    start_frame : bpy.props.IntProperty(name='Start Frame', default = 0, description='Start frame for the action')
    end_frame : bpy.props.IntProperty(name='End Frame', default = 10, description='End frame for the action')

    influence : bpy.props.FloatProperty(name='Influence', default = 0, min = 0, max = 1)

    bones : bpy.props.CollectionProperty(type=APBones)

class APPreferences(bpy.types.PropertyGroup):
    constraint_prefix : bpy.props.StringProperty(name='Constraint Prefix', default='AP-', description='Prefix that will be added to all constraints made by Action Poser. Purging will not work if prefix changes after poses are created.')
    left_suffix : bpy.props.StringProperty(name='Left Suffix', default='.L', description='Set this to the convention you have used on bones')
    right_suffix : bpy.props.StringProperty(name='Right Suffix', default='.R', description='Set this to the convention you have used on bones')
    pose_prefix : bpy.props.StringProperty(name='Pose Prefix', default='AP-', description='Prefix that will be added when creating a new pose action')
    combo_prefix : bpy.props.StringProperty(name='Combo Prefix', default='AC-', description='Prefix that will be added when creating a new combo action')
    default_name : bpy.props.StringProperty(name='Default Name', default='Pose', description='Defines how new poses will be named')


class APStringList(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name='name', default='')

class APBoneTransform(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name='name', default='')
    location : bpy.props.FloatVectorProperty(name='location', subtype='TRANSLATION')
    rotation_euler : bpy.props.FloatVectorProperty(name='rotation_euler', subtype='EULER')
    rotation_quaternion : bpy.props.FloatVectorProperty(name='rotation_quaternion', subtype='QUATERNION',size=4)
    rotation_mode : bpy.props.StringProperty(name='rotation_mode', default='')
    scale : bpy.props.FloatVectorProperty(name='scale', subtype='XYZ')

class APState(bpy.types.PropertyGroup):
    active_object : bpy.props.StringProperty(name='Active Object', default='')
    active_action : bpy.props.StringProperty(name='Active Action', default='')
    selected_bones : bpy.props.CollectionProperty(type=APStringList)
    active_bone : bpy.props.StringProperty(name='Active Bone', default='')
    editing : bpy.props.BoolProperty(default=False)
    autokey : bpy.props.BoolProperty(default=False)


classes = [
    APBones,
    APPoses,
    APPreferences,
    APStringList,
    APState,
    APBoneTransform,
]


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Armature.ap_poses = bpy.props.CollectionProperty(type=APPoses)
    bpy.types.Armature.ap_state = bpy.props.PointerProperty(type=APState)
    bpy.types.Armature.ap_bone_transforms = bpy.props.CollectionProperty(type=APBoneTransform)
    bpy.types.Scene.ap_preferences = bpy.props.PointerProperty(type=APPreferences)
    bpy.types.Armature.ap_poses_index = bpy.props.IntProperty(default=-1, update = update_ap_poses_index)
    bpy.types.Armature.ap_bones_index = bpy.props.IntProperty(default=-1)

def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Armature.ap_poses
    del bpy.types.Armature.ap_state
    del bpy.types.Scene.ap_preferences
    del bpy.types.Armature.ap_poses_index
    del bpy.types.Armature.ap_bones_index

    for cls in reversed(classes):
        unregister_class(cls)
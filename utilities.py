import bpy

def poll_is_mesh_object(self,obj):
    if obj.type == 'MESH':
        return True
    else:
        return False

def poll_is_armature_object(self,obj):
    if obj.type == 'ARMATURE':
        return True
    else:
        return False

def is_valid_path(pose):
    command = 'import bpy; bpy.data.objects["' + pose.target.name + '"].' + pose.data_path

    try:
        exec(command)
    except:
        return False
    return True


def is_valid_pose(pose):
    if not pose.name: return False
    
    if pose.type == 'POSE':
        if not pose.target: return False

        if pose.target_type == 'BONE':
            if not pose.bone: return False
        else:
            if not is_valid_path(pose): return False

    if not pose.action: return False
    
    return True


def purge_poses():
    context = bpy.context
    bones = context.active_object.pose.bones
    prefs = context.scene.ap_preferences

    anim_data = context.active_object.animation_data
    if anim_data:
        drivers = anim_data.drivers
        for driver in drivers:
            path = driver.data_path
            if "constraints[\"" + prefs.constraint_prefix in path:
                drivers.remove(driver)


    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if prefs.constraint_prefix in constraint.name:
                bone.constraints.remove(constraint)

    for ap_pose in context.active_object.data.ap_poses:
        try:
            ap_pose.driver_remove('influence')
        except:
            pass

def influence_has_driver(pose):
    context = bpy.context
    anim_data = context.active_object.animation_data
    if anim_data:
        drivers = anim_data.drivers
        for driver in drivers:
            path = driver.data_path
            if path == 'Influence (' + pose.name + ')':
                return True
    return False


def disable_pose_constraints():
    context = bpy.context
    bones = context.active_object.pose.bones
    prefs = context.scene.ap_preferences

    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if prefs.constraint_prefix in constraint.name:
                constraint.enabled = False


def enable_pose_constraints():
    context = bpy.context
    bones = context.active_object.pose.bones
    prefs = context.scene.ap_preferences

    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if prefs.constraint_prefix in constraint.name:
                constraint.enabled = True

def delete_temp_constraints():
    context = bpy.context
    bones = context.active_object.pose.bones
    prefs = context.scene.ap_preferences

    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if 'AP-edit_mode_temp_constraint' in constraint.name:
                constraints.remove(constraint)

def create_pose(pose, for_edit=False):
    context = bpy.context
    armature = context.active_object.data
    pose_bones = context.active_object.pose.bones
    ap_bones = pose.bones
    prefs = context.scene.ap_preferences

    constraint_name = prefs.constraint_prefix + pose.name
    armature[constraint_name] = 0.0
    
    if pose.type == 'COMBO':
        add_driver_combo(pose)
    else:
        add_driver_influence(pose)

    for ap_bone in ap_bones:
        if ap_bone.bone not in pose_bones:
            print("Unable to constrain bone: ", ap_bone.bone, " in pose: ", pose.name)
            continue
        bone = pose_bones[ap_bone.bone]
        influence = ap_bone.influence

        constraint = bone.constraints.new('ACTION')
        constraint.name = constraint_name

        constraint.action = pose.action
        constraint.frame_start = pose.start_frame
        constraint.frame_end = pose.end_frame
        constraint.mix_mode = pose.mix
        constraint.influence = influence
        constraint.use_eval_time = True

        if not for_edit:
            add_driver_constraint(constraint, pose)
        else:
            constraint.use_eval_time = True
            constraint.eval_time = 1.0
            constraint.name = 'AP-edit_mode_temp_constraint'



def find_opposite_bone_name(bone: str) -> str:
    try:
        return bpy.context.active_object.data.bones[swap_side_suffix(bone)].name
    except:
        return None

def find_opposite_object_name(object: str) -> str:
    try:
        return bpy.data.objects[swap_side_suffix(object)].name
    except:
        return None

def find_opposite_action_name(action: str) -> str:
    try:
        return bpy.data.actions[swap_side_suffix(object)].name
    except:
        return None

def find_opposite_pose_name(pose: str) -> str:
    try:
        return bpy.context.active_object.data.ap_poses[swap_side_suffix(pose)].name
    except:
        return None

def swap_side_suffix(name: str) -> str:
    prefs = bpy.context.scene.ap_preferences

    if name.endswith(prefs.left_suffix):
        return name[:-len(prefs.left_suffix)] + prefs.right_suffix
    elif name.endswith(prefs.right_suffix):
        return name[:-len(prefs.right_suffix)] + prefs.left_suffix
    else:
        return name

def reset_bone_transforms(name: str) -> None:
    pose_bone = bpy.context.active_object.pose.bones[name]
    pose_bone.location = (0.0, 0.0, 0.0)
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    pose_bone.scale = (1.0, 1.0, 1.0)

def map_channel_enum(channel: str) -> list:
    
    dict = {'LOCATION_X': ('location', 0),
            'LOCATION_Y': ('location', 1),
            'LOCATION_Z': ('location', 2),
            'ROTATION_X': ('rotation', 0),
            'ROTATION_Y': ('rotation', 1),
            'ROTATION_Z': ('rotation', 2),
            'SCALE_X': ('scale', 0),
            'SCALE_Y': ('scale', 1),
            'SCALE_Z': ('scale', 2)}

    return dict[channel][0], dict[channel][1]


def map_channel_driver(channel: str) -> list:
    
    dict = {'LOCATION_X': 'LOC_X',
            'LOCATION_Y': 'LOC_Y',
            'LOCATION_Z': 'LOC_Z',
            'ROTATION_X': 'ROT_X',
            'ROTATION_Y': 'ROT_Y',
            'ROTATION_Z': 'ROT_Z',
            'SCALE_X': 'SCALE_X',
            'SCALE_Y': 'SCALE_Y',
            'SCALE_Z': 'SCALE_Z'}
    return dict[channel]

def map_space_driver(space: str) -> list:
    
    dict = {'LOCAL': 'LOCAL_SPACE',
            'WORLD': 'WORLD_SPACE'}
    return dict[space]


def normalize_min_max(value: float, value_min: float, value_max: float) -> float:
        return max(0.0, (value - value_min) / (value_max - value_min))


def add_driver_constraint(constraint: bpy.types.Constraint, pose) -> bpy.types.Driver:
    """Adds driver to property"""
    
    driver = constraint.driver_add('eval_time').driver
    driver.type = 'AVERAGE'
    variable = driver.variables.new()
    variable.name = 'source'
    variable.targets[0].id_type = 'ARMATURE'
    variable.targets[0].id = bpy.context.active_object.data
    variable.targets[0].data_path = 'ap_poses["' + pose.name + '"].influence'

    return driver

def add_driver_combo(pose) -> bpy.types.Driver:
    """Adds driver to property"""
    if not pose.corr_pose_A or not pose.corr_pose_B:
        return
    variable_names = ['corrA', 'corrB']
    poses = [pose.corr_pose_A, pose.corr_pose_B]

    driver = pose.driver_add('influence').driver
    driver.type = 'MIN'
    for i in range(0,2):       
        variable = driver.variables.new()
        variable.name = variable_names[i]
        variable.targets[0].id_type = 'ARMATURE'
        variable.targets[0].id = bpy.context.active_object.data
        variable.targets[0].data_path = 'ap_poses["' + poses[i] + '"].influence'

    return driver

def add_driver_influence(pose):
    """Adds driver to property"""
    
    driver = pose.driver_add('influence').driver
    variable = driver.variables.new()
    variable.name = 'driver'
    variable.targets[0].id = pose.target
    if pose.target_type == 'BONE':
        variable.type = 'TRANSFORMS'
        variable.targets[0].bone_target = pose.bone
        variable.targets[0].transform_type = map_channel_driver(pose.channel)
        variable.targets[0].transform_space = map_space_driver(pose.space)
    elif pose.target_type == 'PROP':
        variable.targets[0].data_path = pose.data_path

    driver.expression = '(driver - ' + str(pose.transform_min) + ') / (' + str(pose.transform_max) + ' - ' + str(pose.transform_min) + ')'

    return driver

def update_ap_poses_index(self, context):
    armature = context.active_object.data

    if armature.ap_state.editing:
        #Leave current action edit
        bpy.ops.armature.ap_action_edit(idx = armature.ap_poses_index)
        #Enter new action edit with updated action
        bpy.ops.armature.ap_action_edit(idx = armature.ap_poses_index)

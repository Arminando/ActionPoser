import bpy

def poll_is_mesh_object(self,obj: bpy.types.Object) -> bool:
    """Checks if the object is a mesh object."""
    if obj.type == 'MESH':
        return True
    else:
        return False

def poll_is_armature_object(self,obj: bpy.types.Object) -> bool:
    """Checks if the object is an armature object."""
    if obj.type == 'ARMATURE':
        return True
    else:
        return False

def is_valid_path(pose: bpy.types.PropertyGroup) -> bool:
    """Checks if the data path is valid."""
    command = 'import bpy; bpy.data.objects["' + pose.target.name + '"].' + pose.data_path
    try:
        exec(command)
    except:
        return False
    return True


def is_valid_pose(pose: bpy.types.PropertyGroup) -> bool:
    """Checks if the pose can be created successfully."""
    if not pose.name: return False
    
    if pose.type == 'POSE':
        if not pose.target: return False

        if pose.target_type == 'BONE':
            if not pose.bone: return False
        else:
            if not is_valid_path(pose): return False

    return True


def purge_poses() -> None:
    """Cleanup function which removes all poses and drivers"""
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

def influence_has_driver(pose: bpy.types.PropertyGroup) -> bool:
    """Checks if the pose has a driver on the influence property."""
    context = bpy.context
    anim_data = context.active_object.animation_data
    if anim_data:
        drivers = anim_data.drivers
        for driver in drivers:
            path = driver.data_path
            if path == 'Influence (' + pose.name + ')':
                return True
    return False


def toggle_pose_constraints(value: bool) -> None:
    """Disables all bone constraints. Used in Edit Action mode."""
    context = bpy.context
    bones = context.active_object.pose.bones
    prefs = context.scene.ap_preferences

    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if prefs.constraint_prefix in constraint.name:
                constraint.enabled = value

def delete_temp_constraints() -> None:
    """Deletes all temporary constraints. Used in Edit Action mode."""
    context = bpy.context
    bones = context.active_object.pose.bones

    for bone in bones:
        constraints = bone.constraints

        for constraint in constraints:
            if 'AP-edit_mode_temp_constraint' in constraint.name:
                try:
                    constraint.driver_remove('eval_time')
                except:
                    pass
                
                constraints.remove(constraint)



def create_pose(pose: bpy.types.PropertyGroup, for_edit: bool=False) -> None:
    """Creates the pose. Handles both regular and combo poses."""
    context = bpy.context
    armature = context.active_object.data
    pose_bones = context.active_object.pose.bones
    ap_bones = pose.bones
    prefs = context.scene.ap_preferences

    constraint_name = prefs.constraint_prefix + pose.name
    armature[constraint_name] = 0.0
    
    variables = {}
    collect_all_variables(pose, variables)

    for ap_bone in ap_bones:
        if ap_bone.bone not in pose_bones:
            print("Could not find bone: ", ap_bone.bone, " for pose: ", pose.name)
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

        # add driver to constraint
        add_action_driver(pose, constraint, 'eval_time', variables)
        if for_edit:
            constraint.name = 'AP-edit_mode_temp_constraint'

    add_action_driver(pose, pose, 'influence', variables)

def find_opposite_bone_name(bone: str) -> str:
    """Returns for the symmetrical bone name."""
    try:
        return bpy.context.active_object.data.bones[swap_side_suffix(bone)].name
    except:
        return None

def find_opposite_object_name(object: str) -> str:
    """Returns for the symmetrical object name."""
    try:
        return bpy.data.objects[swap_side_suffix(object)].name
    except:
        return None

def find_opposite_action_name(action: str) -> str:
    """Returns the opposite action name."""
    try:
        return bpy.data.actions[swap_side_suffix(object)].name
    except:
        return None

def find_opposite_pose_name(pose: str) -> str:
    """Returns the opposite pose name."""
    try:
        return bpy.context.active_object.data.ap_poses[swap_side_suffix(pose)].name
    except:
        return None

def swap_side_suffix(name: str) -> str:
    """String operation that swaps the side suffixes."""
    prefs = bpy.context.scene.ap_preferences

    if name.endswith(prefs.left_suffix):
        return name[:-len(prefs.left_suffix)] + prefs.right_suffix
    elif name.endswith(prefs.right_suffix):
        return name[:-len(prefs.right_suffix)] + prefs.left_suffix
    else:
        return name

def reset_bone_transforms(name: str) -> None:
    """Resets the bone transforms to default."""
    pose_bone = bpy.context.active_object.pose.bones[name]
    pose_bone.location = (0.0, 0.0, 0.0)
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    pose_bone.scale = (1.0, 1.0, 1.0)

def add_driver_constraint(constraint: bpy.types.Constraint, pose: bpy.types.PropertyGroup) -> bpy.types.Driver:
    """Adds a driver to the Action Constraint's evaluation time."""
    
    driver = constraint.driver_add('eval_time').driver
    driver.type = 'AVERAGE'
    variable = driver.variables.new()
    variable.name = 'source'
    variable.targets[0].id_type = 'ARMATURE'
    variable.targets[0].id = bpy.context.active_object.data
    variable.targets[0].data_path = 'ap_poses["' + pose.name + '"].influence'

    return driver

def add_driver_combo(pose: bpy.types.PropertyGroup) -> bpy.types.Driver:
    """Adds combo driver to influence property of the pose.
        Currently produces a cycle error. Needs to be fixed.
    """
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

def add_driver_influence(pose: bpy.types.PropertyGroup) -> bpy.types.Driver:
    """Adds driver to a pose's influence property."""
    
    driver = pose.driver_add('influence').driver
    variable = driver.variables.new()
    variable.name = 'driver'
    variable.targets[0].id = pose.target
    if pose.target_type == 'BONE':
        variable.type = 'TRANSFORMS'
        variable.targets[0].bone_target = pose.bone
        variable.targets[0].transform_type = pose.channel
        variable.targets[0].transform_space = pose.space
        if 'ROT' in pose.channel:
            variable.targets[0].rotation_mode = pose.rot_mode
    elif pose.target_type == 'PROP':
        variable.targets[0].data_path = pose.data_path
    
    driver_str = '(driver - '
    if 'ROT' in pose.channel:
        driver_str = '(degrees(driver) - '
    driver.expression = driver_str + str(pose.transform_min) + ') / (' + str(pose.transform_max) + ' - ' + str(pose.transform_min) + ')'

    return driver

def update_ap_poses_index(self, context: bpy.types.Context) -> None:
    """Switches active action when switching between poses in Edit Action mode."""
    armature = context.active_object.data

    if armature.ap_state.editing:
        #Leave current action edit
        bpy.ops.armature.ap_action_edit(idx = armature.ap_poses_index)
        #Enter new action edit with updated action
        bpy.ops.armature.ap_action_edit(idx = armature.ap_poses_index)

def collect_all_variables(pose: bpy.types.PropertyGroup, variables: dict) -> dict:
    """Collects all the variables to be used in the pose's driver expression."""

    if pose.type == 'COMBO':
        if not pose.corr_pose_A or not pose.corr_pose_B:
            return
        collect_all_variables(bpy.context.active_object.data.ap_poses[pose.corr_pose_A], variables)
        collect_all_variables(bpy.context.active_object.data.ap_poses[pose.corr_pose_B], variables)
    else:
        var_name = "var" + str(len(variables.keys()))
        variables[var_name] = {}
        variables[var_name]['target'] = pose.target

        if pose.target_type == 'BONE':
            variables[var_name]['bone_target'] = pose.bone
            variables[var_name]['transform_type'] = pose.channel
            variables[var_name]['transform_space'] = pose.space
            variables[var_name]['transform_min'] = pose.transform_min
            variables[var_name]['transform_max'] = pose.transform_max
            if 'ROT' in pose.channel:
                variables[var_name]['rot_mode'] = pose.rot_mode
        elif pose.target_type == 'PROP':
            variables[var_name]['data_path'] = pose.data_path

def add_action_driver(pose: bpy.types.PropertyGroup, target_obj: bpy.types.ActionConstraint, property: str, variables: dict) -> None:
    """Adds a driver to the action constraint with the given variables"""

    driver = target_obj.driver_add(property).driver
    driver.type = 'SCRIPTED'

    expression = 'min('

    for key in variables.keys():
        variable = driver.variables.new()
        variable.name = key
        variable.targets[0].id = variables[key]['target']

        if pose.target_type == 'BONE':
            variable.type = 'TRANSFORMS'
            variable.targets[0].bone_target = variables[key]['bone_target']
            variable.targets[0].transform_type = variables[key]['transform_type']
            variable.targets[0].transform_space = variables[key]['transform_space']
            if 'rot_mode' in variables[key].keys():
                variable.targets[0].rotation_mode = variables[key]['rot_mode']
        elif pose.target_type == 'PROP':
            variable.targets[0].data_path = variables[key]['data_path']

        var_expression = '( ' + key + ' - '
        if 'ROT' in pose.channel:
            var_expression = '(degrees( ' + key + ') - '
        expression += var_expression + str(variables[key]['transform_min']) + ') / (' + str(variables[key]['transform_max']) + ' - ' + str(variables[key]['transform_min']) + '), '

    expression = expression[:-2] + ')'

    driver.expression = expression


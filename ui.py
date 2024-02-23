import bpy
from bpy.types import Context, Panel, UIList

from . utilities import is_valid_path

class ActionPoserPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_action_poser"
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE' and context.mode == 'POSE'

class VIEW3D_PT_action_poser(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"
    bl_label = 'Action Poser'
    
    def draw(self, context: Context) -> None:
        pass


class VIEW3D_PT_action_poses(ActionPoserPanel):
    bl_label = 'Poses'

    def draw(self, context: Context) -> None:
        layout = self.layout
        armature = context.active_object.data

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.template_list("VIEW3D_UL_actions_list", "", armature, "ap_poses", armature, "ap_poses_index")

        col = row.column(align=True)
        col.operator("armature.ap_pose_add", icon='ADD', text="")
        col.operator("armature.ap_pose_remove", icon='REMOVE', text="").idx = armature.ap_poses_index
        col.separator()
        col.operator("armature.ap_pose_duplicate", icon='DUPLICATE', text="").idx = armature.ap_poses_index
        col.operator("armature.ap_pose_mirror", icon='MOD_MIRROR', text="").idx = armature.ap_poses_index
        col.separator()
        col.operator("armature.ap_pose_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("armature.ap_pose_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
        col.menu("VIEW3D_MT_poses_menu", icon='DOWNARROW_HLT', text="")

        row = layout.split(factor=0.8)
        row.operator('armature.ap_execute', icon='PLAY')
        row.operator('armature.ap_purge', icon='X')


class VIEW3D_PT_action_poser_driver(ActionPoserPanel):
    bl_label = "Driver"

    def draw(self, context: Context) -> None:
        scene = context.scene
        layout = self.layout
        armature = context.active_object.data

        try:
            active_pose = armature.ap_poses[armature.ap_poses_index]
        except:
            active_pose = None

        if active_pose:
            layout.use_property_split = True
            layout.use_property_decorate = False

            col = layout.column(align=True)
            row = col.row()
            row.prop(active_pose, 'type', expand=True)
            col.separator()

            if active_pose.type == 'POSE':
                col.separator()
                row = col.row()
                row.prop(active_pose, 'target')
                row.menu("VIEW3D_MT_target_menu", icon='DOWNARROW_HLT', text="")

                col.separator()
                row = col.row()
                row.prop(active_pose, 'target_type', expand=True)
                col.separator()
                if active_pose.target:
                    if active_pose.target_type == 'BONE':            
                    
                        # col.prop(active_pose, 'bone')
                        col.prop_search(active_pose, 'bone', active_pose.target.data, 'bones')

                        if active_pose.bone:
                            col = layout.column()
                            col.prop(active_pose, 'channel')
                            if 'ROT' in active_pose.channel:
                                col.prop(active_pose, 'rot_mode')
                            col.prop(active_pose, 'space')
                            col.prop(active_pose, 'mix')

                    else:

                        col.alert = not is_valid_path(active_pose)
                        col.prop(active_pose, 'data_path', icon='RNA')

                    col.prop(active_pose, 'transform_min')
                    col.prop(active_pose, 'transform_max')
            elif active_pose.type == 'COMBO':
                col.separator()
                col.prop_search(active_pose, 'corr_pose_A', armature, 'ap_poses')
                col.prop_search(active_pose, 'corr_pose_B', armature, 'ap_poses')
                col.separator()
                col.prop(active_pose, 'mix')

            
class VIEW3D_PT_action_poser_action(ActionPoserPanel):
    bl_parent_id = "VIEW3D_PT_action_poser"
    bl_label = "Action"

    def draw(self, context: Context) -> None:
        scene = context.scene
        layout = self.layout
        armature = context.active_object.data

        try:
            active_pose = armature.ap_poses[armature.ap_poses_index]
        except:
            active_pose = None

        if active_pose:
            layout.use_property_split = True
            layout.use_property_decorate = False

            if active_pose.action:
                if not armature.ap_state.editing:
                    label = "Edit Action"
                else:
                    label = "Finish Editing"
                col = layout.column()
                col.alert = armature.ap_state.editing
                
                col.operator("armature.ap_action_edit", icon='ACTION_TWEAK', text=label).idx = armature.ap_poses_index
            row = layout.row(align=True)
            
            row.prop(active_pose, 'action', text='')
            if active_pose.action:
                row.prop(active_pose.action, 'use_fake_user', text='')
            
            row.separator()
            row.menu("VIEW3D_MT_action_menu", icon='DOWNARROW_HLT', text="")


            col = layout.column()
            col.prop(active_pose, 'start_frame', text="Frame Start")
            col.prop(active_pose, 'end_frame', text = 'End')


                


class VIEW3D_PT_action_poser_targets(ActionPoserPanel):
    bl_parent_id = "VIEW3D_PT_action_poser"
    bl_label = "Target Bones"

    def draw(self, context: Context) -> None:
        scene = context.scene
        layout = self.layout
        armature = context.active_object.data

        try:
            active_pose = armature.ap_poses[armature.ap_poses_index]
        except:
            active_pose = None

        if active_pose:
            layout.use_property_split = True
            layout.use_property_decorate = False

            row = layout.row()
            row.template_list("VIEW3D_UL_bones_list", "", active_pose, "bones", armature, "ap_bones_index")

            col = row.column(align=True)
            col.operator("armature.ap_bone_add", icon='ADD', text="").idx = armature.ap_poses_index
            op = col.operator("armature.ap_bone_remove", icon='REMOVE', text="")
            op.idx = armature.ap_poses_index
            op.bone_idx = armature.ap_bones_index
            col.separator()
            col.operator("armature.ap_bone_add_selected", icon='SELECT_EXTEND', text="").idx = armature.ap_poses_index
            col.operator("armature.ap_bone_remove_selected", icon='SELECT_SUBTRACT', text="").idx = armature.ap_poses_index
            col.operator("armature.ap_bone_add_from_action", icon='ACTION_TWEAK', text="").mode = 'ADD'
            col.separator()
            col.menu("VIEW3D_MT_bones_menu", icon='DOWNARROW_HLT', text="")


class VIEW3D_PT_action_poser_prefs(ActionPoserPanel):
    bl_parent_id = "VIEW3D_PT_action_poser"
    bl_label = "Preferences"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        scene = context.scene
        prefs = scene.ap_preferences
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(prefs, 'constraint_prefix')
        col.prop(prefs, 'left_suffix')
        col.prop(prefs, 'right_suffix')
        col.prop(prefs, 'pose_prefix')
        col.prop(prefs, 'combo_prefix')
        col.prop(prefs, 'default_name')


class VIEW3D_UL_actions_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.use_property_split = False
        
        row = layout.row()
        split = row.split(factor=0.65)
        if item.type == 'COMBO':
            icon = 'PLUS'
        else:
            icon = 'NONE'
        split.prop(item, "name", text="", icon=icon, emboss = False)
        
        split.prop(item, "influence", text="", slider = True)
        
        if item.build:
            icon = 'HIDE_OFF'
        else:
            icon = 'HIDE_ON'
        row.prop(item, 'build', icon=icon, text='')
                

class VIEW3D_MT_poses_menu(bpy.types.Menu):
    bl_label = 'Additional Operators'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object.data

        layout.operator("armature.ap_pose_move", icon='ANCHOR_TOP', text="Move to Top").direction = 'TOP'
        layout.operator("armature.ap_pose_move", icon='ANCHOR_BOTTOM', text="Move to Bottom").direction = 'BOTTOM'
        layout.separator()
        layout.operator("armature.ap_copy", text = 'Copy All to Selected').mode = 'ALL'
        layout.operator("armature.ap_copy", text = 'Copy Active to Selected').mode = 'ACTIVE'
        layout.separator()
        layout.operator("armature.ap_clear")


class VIEW3D_MT_target_menu(bpy.types.Menu):
    bl_label = 'Additional Operators'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object.data

        layout.operator("armature.ap_target_set_active")
        layout.operator("armature.ap_target_select")


class VIEW3D_MT_action_menu(bpy.types.Menu):
    bl_label = 'Additional Operators'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object.data

        layout.operator("armature.ap_action_new", icon='FILE_NEW').idx = armature.ap_poses_index
        layout.operator("armature.ap_action_duplicate", icon='DUPLICATE').idx = armature.ap_poses_index
        layout.separator()
        layout.operator("armature.ap_action_rename", icon='FONT_DATA')
        layout.operator('armature.ap_remove_flat_curves', icon='NOCURVE').idx = armature.ap_poses_index
        layout.separator()
        layout.operator("armature.ap_action_delete", icon='REMOVE').idx = armature.ap_poses_index


class VIEW3D_MT_bones_menu(bpy.types.Menu):
    bl_label = 'Additional Operators'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object.data

        layout.operator("armature.ap_bone_select_from_pose", icon='SELECT_SET').idx = armature.ap_poses_index
        layout.operator("armature.ap_bone_add_from_action", icon='ACTION_TWEAK', text="Select From Action").mode = 'SELECT'
        layout.operator("pose.select_mirror", text="Select Mirror").extend = False
        layout.operator("pose.select_mirror", text="Select Mirror Extend").extend = True
        layout.separator()
        layout.operator("armature.ap_bone_remove_all", icon='X').idx = armature.ap_poses_index


class VIEW3D_UL_bones_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.use_property_split = False
        
        row = layout.row()
        split = row.split(factor=0.7)
        split.prop_search(item, 'bone', context.active_object.data, 'bones', text = '')
        split = split.split(factor=0.15)
        split.label(text='')
        split.prop(item, "influence", emboss=True, text='', slider = True)

    def filter_items(self, context, data, propname):
        # This function gets the collection property (as the usual tuple (data, propname)), and must return two lists:
        # * The first one is for filtering, it must contain 32bit integers were self.bitflag_filter_item marks the
        #   matching item as filtered (i.e. to be shown), and 31 other bits are free for custom needs. Here we use the
        #   first one to mark VGROUP_EMPTY.
        # * The second one is for reordering, it must return a list containing the new indices of the items (which
        #   gives us a mapping org_idx -> new_idx).
        # Please note that the default UI_UL_list defines helper functions for common tasks (see its doc for more info).
        # If you do not make filtering and/or ordering, return empty list(s) (this will be more efficient than
        # returning full lists doing nothing!).
        ap_bones = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # Default return values.
        flt_flags = []
        flt_neworder = []

        # # Pre-compute of vgroups data, CPU-intensive. :/
        # vgroups_empty = self.filter_items_empty_vgroups(context, vgroups)

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, ap_bones, "bone",
                                                          reverse=self.use_filter_sort_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(ap_bones)

        # Reorder by name.
        if self.use_filter_sort_alpha:
            sorted_names = [x.bone for x in ap_bones]
            sorted_names.sort()
            if self.use_filter_sort_reverse:
                sorted_names.reverse()
            for name in sorted_names:
                flt_neworder.append(ap_bones[name])

            # flt_neworder = helper_funcs.sort_items_helper(ap_bones, "bone", reverse=self.use_filter_sort_reverse)

        return flt_flags, flt_neworder
        

classes = [
    VIEW3D_MT_poses_menu,
    VIEW3D_MT_target_menu,
    VIEW3D_MT_action_menu,
    VIEW3D_MT_bones_menu,
    VIEW3D_PT_action_poser,
    VIEW3D_UL_actions_list,
    VIEW3D_UL_bones_list,
    VIEW3D_PT_action_poses,
    VIEW3D_PT_action_poser_driver,
    VIEW3D_PT_action_poser_action,
    VIEW3D_PT_action_poser_targets,
    VIEW3D_PT_action_poser_prefs,
]

register, unregister = bpy.utils.register_classes_factory(classes)
import bpy, math, traceback

from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )

import bmesh
from mathutils.geometry import (
                distance_point_to_plane,
                normal)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "SierraRenamer",
    "author" : "Ant",
    "description" : "",
    "blender" : (3, 8, 0),
    "version" : (0, 0, 3),
    "location" : "",
    "warning" : "",
    "category" : "Mesh"
}


class MySettings(bpy.types.PropertyGroup):

    string_prefix : bpy.props.StringProperty(
        name="Prefix",
        description="String to rename to",
        default="SM"
    )
    string_suffix : bpy.props.StringProperty(
        name="Suffix",
        description="String to rename to",
        default="X"
    )
    int_leading : bpy.props.IntProperty(
        name="Leading 0s",
        description="Amount Of Leading 0s",
        default=1
    )

    enum_suffixAction: bpy.props.EnumProperty(
        name= "Suffix Options",
        description="Action Selecting",
        items=[
        ("0", "None", ""),
        ("1", "String", ""),
        ("2", "Number", ""),
        ("3", "String + Number", "")
        ],
        default="2"
    )

    string_rename : bpy.props.StringProperty(
        name="Rename To",
        description="String to rename to",
        default="object"
    )

class Renamer_PT_Panel(bpy.types.Panel):
    bl_idname="VIEW3D_T_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label="Sierra Renamer"
    bl_category="Renamer"


    def draw(self, context):
        scene = context.scene
        mytool = scene.my_tool
        layout = self.layout

        renamebox = layout.box()
        renamebox.label(text="Sierra Renamer")
        row = renamebox.prop(mytool, "string_prefix")
        row = renamebox.prop(mytool, "enum_suffixAction")
        if mytool.enum_suffixAction == "1":
            row = renamebox.prop(mytool, "string_suffix")
        elif mytool.enum_suffixAction == "2":
            row = renamebox.prop(mytool, "int_leading")
        elif mytool.enum_suffixAction == "3":
            row = renamebox.prop(mytool, "string_suffix")
            row = renamebox.prop(mytool, "int_leading")
        row = renamebox.prop(mytool, "string_rename")
        row = renamebox.row()
        row.operator("object.sierrarename", text="Rename")
        row.operator("object.showconcave", text="Show Concave")


class SierraRenamer_OT_Operator(bpy.types.Operator):
    bl_idname= "object.sierrarename"
    bl_label="renamer"
    bl_description="Rename current objects to the string"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        OBs = bpy.context.selected_objects
        for i, obj in enumerate(OBs, 1):
            bpy.context.view_layer.objects.active = obj
            prefix = "" if mytool.string_prefix == "" else mytool.string_prefix + "_"
            obj.name = prefix + mytool.string_rename 
            obj.name += "_" if int(mytool.enum_suffixAction) > 0 else ""
            
            if mytool.enum_suffixAction == "1":
                obj.name += mytool.string_suffix
            elif mytool.enum_suffixAction == "2":
                obj.name += str(format(i,f'0{mytool.int_leading + 1}'))
            elif mytool.enum_suffixAction == "3":
                obj.name += mytool.string_suffix + str(format(i,f'0{mytool.int_leading + 1}'))

        return {"FINISHED"}

class ShowConcave_OT_Operator(bpy.types.Operator):
    bl_idname= "object.showconcave"
    bl_label="showconcave"
    bl_description="Flips Normals Of Concave"

    def execute(self, context):
        OBs = bpy.context.selected_objects
        mode = context.active_object.mode
        for ob in OBs:
            bpy.ops.object.mode_set(mode='EDIT')
            mesh = ob.data

            TOL = 0.0001

            # select None
            bpy.ops.mesh.select_all(action='DESELECT')
            bm = bmesh.from_edit_mesh(mesh)
            ngons = [f for f in bm.faces if len(f.verts) > 3]

            for ngon in ngons:
                # define a plane from first 3 points
                co = ngon.verts[0].co
                norm = normal([v.co for v in ngon.verts[:3]])

                ngon.select =  not all(
                    [(distance_point_to_plane(v.co, co, norm)) < TOL
                    for v in ngon.verts[3:]])
                if ngon.select: 
                    bpy.ops.mesh.normals_make_consistent(inside=True)

                print(([distance_point_to_plane(v.co, co, norm) for v in ngon.verts[3:]]))

            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode=mode)
        bpy.context.space_data.overlay.show_face_orientation = True
        return{'FINISHED'}



classes = (MySettings, SierraRenamer_OT_Operator, Renamer_PT_Panel, ShowConcave_OT_Operator)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MySettings)

def unregister():
    del bpy.types.Scene.my_tool
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



'''
class NAME_OT_Operator(bpy.types.Operator):
    bl_idname= "object.name"
    bl_label="label"
    bl_description=""

    def execute(self, context):
        scene = context.scene
        C = bpy.context
        mytool = scene.my_tool
        

        return {"FINISHED"}

'''


if __name__ == "__main__":
    register()




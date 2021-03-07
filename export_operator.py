import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .export_dxf import DXFExporter
from .shared_properties import (
    dxf_face_type,
    dxf_line_type,
    dxf_point_type,
    entity_layer,
    entity_color,
)


class DXFExporter_OT_Export(Operator, ExportHelper):
    """File selection operator to export objects in DXF file"""
    bl_idname = "dxf_exporter.export"
    bl_label = "Export As DXF"

    filename_ext = ".dxf"

    only_selected: BoolProperty(
        name="Export Only Selected Objects", 
        default=True,
        description="What object will be exported? Only selected / All objects")

    faces_export:EnumProperty(
        name="Export Faces", 
        default=dxf_face_type.FACES3D.value,
        items=[(f_t.value,)*3 for f_t in dxf_face_type])
    
    lines_export:EnumProperty(
        name="Export Lines", 
        default=dxf_line_type.NONE.value,
        items=[(l_t.value,)*3 for l_t in dxf_line_type])

    points_export:EnumProperty(
        name="Export Points", 
        default=dxf_point_type.NONE.value,
        items=[(p_t.value,)*3 for p_t in dxf_point_type])

    entity_layer_to: EnumProperty(
        name="Object Layer", 
        default=entity_layer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,)*3 for e_l in entity_layer])
    
    entity_layer_separate: BoolProperty(
        name="Separate Entity Types",
        description="Check for faces, lines and points to be drawn on separate layers",
        # TODO : Add customization in addonprefs
        default=False,
    )
        
    entity_color_to: EnumProperty(
        name="Object Color", 
        default=entity_color.BYLAYER.value,
        description="Entity COLOR assigned to ?",
        items=[(e_c.value,)*3 for e_c in entity_color])

    verbose: BoolProperty(
        name="Verbose", 
        default=False,
        description="Run the exporter in debug mode.  Check the console for output")

    filter_glob: StringProperty(
        default="*.dxf",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath: StringProperty(name="File Name",
                             description="filepath",
                             default="",
                             maxlen=1024,
                             options={'ANIMATABLE'},
                             subtype='NONE')

    def execute(self, context):
        exporter = DXFExporter(
            debug_mode=self.verbose,
        )
        exporter.write_objects(
            objects=context.selected_objects if self.only_selected else context.scene.objects,
            context=context,
            faces_as=self.faces_export,
            lines_as=self.lines_export,
            points_as=self.points_export,
            color=self.entity_color_to,
            layer=self.entity_layer_to,
            layer_separate=self.entity_layer_separate,
            )

        exporter.export_file(self.filepath)
        if self.verbose:
            for line in exporter.log:
                print(line)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "only_selected")
        for prop, name in zip(
                ("faces_export", "lines_export", "points_export"),
                ("Export Faces", "Export Edges", "Export Vertices")
                ):
            box = layout.box()
            faces_split = box.split(factor=0.6)
            faces_split.label(text=name)
            faces_split.props_enum(self, prop)

        layer_box = layout.box()
        layer_box.label(text="Object Layer")
        layer_box.prop(self, "entity_layer_to", text="")
        layer_box.prop(self, "entity_layer_separate")
        layout.prop(self, "entity_color_to")
        layout.prop(self, "verbose")


def menu_func_export(self, context):
    self.layout.operator(DXFExporter_OT_Export.bl_idname,
                         text="Drawing Interchange File (.dxf)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

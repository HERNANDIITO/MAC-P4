"""
See YouTube tutorial here: https://youtu.be/0_QskeU8CPo
"""

bl_info = {
    "name": "My Custom Panel",
    "author": "Victor Stepanov",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > My Custom Panel category",
    "description": "My custom operator buttons",
    "category": "Development",
}


import bpy
import math

# Funcion encargada de dibujar cada uno de los keyframes
def set_gravity(t0, g, v0, yf):
    # Comienza recogiendo todos los objetos seleccionados
    items = bpy.context.selected_objects

    for i in items: # Itera por cada objeto de la lista
        # Reestablece el temporizador e imprime informacion basica
        t = 0
        h = i.location[2]
        print(f"item: {i}, location:{i.location}, z:{i.location[2]}")
        i.keyframe_insert(data_path="location", frame=t0)
        
        i.location[2] = yf
        tf = int(abs(pow((2 * h-yf) / g, 0.5)))
        print(f"tf: {tf}")

        i.keyframe_insert(data_path="location", frame=t0 + (24 * tf))

        for fcurve in i.animation_data.action.fcurves:
            kf = fcurve.keyframe_points[-2]
            kf.interpolation = 'BOUNCE'
            kf.easing = 'EASE_OUT'

class ANIM_OT_set_gravity(bpy.types.Operator):

    # Declaracion de la clase
    bl_idname = "anim.set_gravity"
    bl_label = "Gravity settings"
    bl_options = {"REGISTER", "UNDO"}

    # Parametro instante cero
    t0: bpy.props.IntProperty(
        name="Start time",
        default=0,
        description="Choose the moment when the object starts falling",
    )

    # Parametro de aceleracion
    gravity: bpy.props.FloatProperty(
        name="Force",
        default=-9.81,
        description="Choose the force of attraction",
    )
    
    # Parametro de velocidad inicial
    v0: bpy.props.FloatProperty(
        name="Initial speed",
        default=0,
        description="Choose the initial speed of the object",
    )
    
    # Parametro de posicion final
    finalPos: bpy.props.FloatProperty(
        name="Final position",
        default=0,
        description="Choose the final position of an object",
    )

    def execute(self, context):

        # Trigger de la funcion de los keyframes
        set_gravity(self.t0, self.gravity, self.v0, self.finalPos)

        return {"FINISHED"}

class VIEW3D_PT_gravity(bpy.types.Panel): 

    # Posicionamiento del panel
    bl_space_type = "VIEW_3D"  # Donde se añade el menu
    bl_region_type = "UI"  # En que parte de la interfaz

    # Texto
    bl_category = "Gravity"  # Texto del sidebar
    bl_label = "Gravity addon"  # Texto del panel

    def draw(self, context):
        # Definimos el layout
        row = self.layout.row()
        row.operator("anim.set_gravity", text="Set gravity")


# Registrar contenidos
def register():
    bpy.utils.register_class(VIEW3D_PT_gravity)
    bpy.utils.register_class(ANIM_OT_set_gravity)

# "Desregistrar" contenidos por si ya existen
def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_gravity)
    bpy.utils.unregister_class(ANIM_OT_set_gravity)


if __name__ == "__main__":
    register()
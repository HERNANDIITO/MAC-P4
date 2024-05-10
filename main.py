bl_info = {
    "name": "Gravity addon",
    "author": "Pablo Hernández",
    "version": (1, 1, 0),
    "blender": (4, 1, 1),
    "location": "3D Viewport > Sidebar > Gravity",
    "description": "Allows to easily create gravity related animations",
    "category": "Animation",
}

import bpy

# Funcion encargada de dibujar cada uno de los keyframes
def set_gravity(t0, g, v0, yf, bouncy, axis):
    # Comienza recogiendo todos los objetos seleccionados
    items = bpy.context.selected_objects


    for i in items: # Itera por cada objeto de la lista
        # Reestablece el temporizador e imprime informacion basica
        t = 0

        axis = int(axis)
        h = i.location[axis]

        if ( yf == h ): return
        print(f"item: {i}, location:{i.location}, z:{i.location[axis]}")
        i.keyframe_insert(data_path="location", frame=t0)
        
        i.location[axis] = yf
        tf = int(abs(pow((2 * h-yf) / g, 0.5)))
        print(f"tf: {tf}")

        if bouncy:
            i.keyframe_insert(data_path="location", frame=t0 + (24 * tf))
        else:
            i.keyframe_insert(data_path="location", frame=t0 + ((24 * tf)/2))

        for fcurve in i.animation_data.action.fcurves:
            kf = fcurve.keyframe_points[-2]
            if bouncy: 
                kf.interpolation = 'BOUNCE'
                kf.easing = 'EASE_OUT'
            else:
                kf.interpolation = 'CUBIC'
                kf.easing = 'EASE_IN'


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

    # Parametro de rebote
    bounciness: bpy.props.BoolProperty(
        name="Bounciness",
        default=True,
        description="Choose between bouncy falling or non-bouncy",
    )

    # Parametro del eje
    axis: bpy.props.EnumProperty(
        items = [
            ("0", "X", "X Axis", 0),
            ("1", "Y", "Y Axis", 1),
            ("2", "Z", "Z Axis", 2),
        ],
        name = "Axis",
        description = "Choose the axis in wich the item will be falling",
        default = "2"
    )

    def execute(self, context):

        # Trigger de la funcion de los keyframes
        set_gravity(self.t0, self.gravity, self.v0, self.finalPos, self.bounciness, self.axis)

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
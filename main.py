bl_info = {
    "name": "Gravity addon",
    "author": "Pablo Hernández",
    "version": (2, 0, 0),
    "blender": (4, 1, 1),
    "location": "3D Viewport > Sidebar > Gravity",
    "description": "Allows to easily create gravity related animations",
    "category": "Animation",
}

particle_cont = 0

import bpy
import mathutils
import numpy
import math
import os

# Convierte los vectores globales a relativos
def globalToLocal(objectForLocal, vectorOrTupleToConv):
    vectorified = mathutils.Vector(vectorOrTupleToConv)
    return objectForLocal.matrix_world.inverted() @ vectorified
    
# Convierte los vectores relativos a globale
def localToGlobal(obj, vectorOrTupleToConv):
    vectorified = mathutils.Vector(vectorOrTupleToConv)
    return obj.matrix_world @ vectorified

# Obtiene la colision dada la lista de obstaculos, la direccion, el objeto y el eje
def getCollission(obstacles, gDirection, i, axis):
    result = False # Valor por defecto para comparar

    # Iteramos por cada posible obstaculo en la escena
    for obstacle in obstacles:
        # Comprobamos que sea un objeto tipo mesh y que no sea el propio objeto
        if obstacle.type != "MESH" or obstacle == i:
            continue
        
        if obstacle.name == "particles" or obstacle.name == "force_field" or obstacle.name == "dust":
            continue

        # Declaracion de variables
        # Convertimos las coorenadas del obstaculo en relativas al objeto
        origin = globalToLocal(obstacle, i.location)

        # Origen del obstaculo
        obstacle_origin = mathutils.Vector((0,0,0))

        # Direccion
        direction = obstacle_origin - origin

        # Comprobamos
        is_hit, location, _, _ = obstacle.ray_cast(origin, direction)

        # Comprobamos que el otro objeto este justo "debajo"
        if ( axis == 0 ):
            if ( location[1] != 0 or location[2] != 0 ): continue
            
        if ( axis == 1 ):
            if ( location[0] != 0 or location[2] != 0 ): continue

        if ( axis == 2 ):
            if ( location[1] != 0 or location[0] != 0 ): continue

        # Comprobamos que haya habido hit y direccion
        if is_hit and direction:
            # Convertimos el 
            world_loc = localToGlobal(obstacle, location)
            print("wordl_loc:", world_loc)
            result = world_loc[axis] - (i.dimensions[axis]/2 * gDirection)
            break
        
    return result

def particle_setup(i, yf, axis, gDirection, tf):
    global particle_cont

    dotCont = (f"{particle_cont}").zfill(3)
    file_loc = os.getcwd() + "\\particles\\dust.blend\\Collection\\"
    bpy.ops.wm.append(directory=file_loc, filename="dust_particles")
    print(i.name)
    col = bpy.data.collections.get("dust_particles")
    col.name = f"{i.name}-particles-{dotCont}"

    print("dust." + (f"{particle_cont}").zfill(3))
    print("particles." + (f"{particle_cont}").zfill(3))

    if particle_cont == 0:
        particleEmitter = col.all_objects.get("particles")
    else:            
        particleEmitter = col.all_objects.get(f"particles.{dotCont}")

    print("particle Axis: ", axis)

    
    mirror = True
    if ( numpy.sign(gDirection) == -1 ):
        mirror = False

    if ( axis == 0 ):
        if mirror:
            particleEmitter.rotation_euler = mathutils.Euler((0.0, math.radians(-90.0) * gDirection, 0.0), 'XYZ')
        else:
            particleEmitter.rotation_euler = mathutils.Euler((0.0, math.radians(90.0) * gDirection, 0.0), 'XYZ')

        
    if ( axis == 1 ):
        if mirror:
            particleEmitter.rotation_euler = mathutils.Euler((math.radians(90.0) * gDirection, 0, 0.0), 'XYZ')
        else:
            particleEmitter.rotation_euler = mathutils.Euler((math.radians(-90.0) * gDirection, 0, 0.0), 'XYZ')


    if ( axis == 2 ):
        if mirror:
            particleEmitter.rotation_euler = mathutils.Euler((math.radians(90)), 0, 0, 'XYZ')

    particleEmitter.location = i.location
    particleEmitter.location[axis] = particleEmitter.location[axis] + ((i.dimensions[axis]/2) * gDirection)

    pSys = particleEmitter.particle_systems[0]

    pSys.settings.frame_start = tf
    pSys.settings.frame_end = tf + 24


# Funcion encargada de dibujar cada uno de los keyframes
def set_gravity(t0, g, v0, yf, bouncy, axis, calculateCollissions, getParticles):
    # Comienza recogiendo todos los objetos seleccionados
    items = bpy.context.selected_objects
    context = bpy.context

    for i in items: # Itera por cada objeto de la lista

        # Reestablece el temporizador e imprime informacion basica
        t = 0
        gDirection = numpy.sign(g)
        axis = int(axis)
        h = i.location[axis]
        d = h-yf

        # Comprobamos si el usuario quiere que calculemos colisiones
        if calculateCollissions:
            # Las calculamos (mas info en la funcion)
            collission = getCollission(obstacles=context.scene.objects, gDirection=gDirection, i=i, axis=axis)

            # En caso de encontrarla, sobreescribimos la posicion final
            if ( collission != False ):
                yf = collission

        # Comprobamos que el objeto no este ya en la posicion final
        if ( yf == h ): return
        print(f"item: {i}, location:{i.location}, z:{i.location[axis]}")

        # Insertamos el keyframe en la posicion inicial
        i.keyframe_insert(data_path="location", frame=t0)
        
        # Colocamos el objeto en la posicion final
        i.location[axis] = yf - (i.dimensions[axis]/2 * gDirection)
        print(f"h - yf: {h} - {yf} = {h- yf}")

        # Calculamos el tiempo que tardara en caer
        tf = int(abs(pow(abs((2 * (h-yf)) / g), 0.5)))
        print(f"tf: {tf}")

        # Dependiendo de si se busca una animacion con rebote o no establecemos un tiempo u otro
        if bouncy:
            i.keyframe_insert(data_path="location", frame=t0 + (24 * tf))
        else:
            i.keyframe_insert(data_path="location", frame=t0 + ((24 * tf)/2))

        # Dependiendo de si se busca una animacion con rebote o no ponemos un tipo de interpolacion u otra
        
        if getParticles:
            particle_setup(i, yf, axis, gDirection, tf*24)
            
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

    # Parametro de colision
    colissions: bpy.props.BoolProperty(
        name="Collide with objects",
        default=True,
        description="Choose if the object is going to collide with meshes or not",
    )

    # Parametro de particulas
    particles: bpy.props.BoolProperty(
        name="Display particles",
        default=True,
        description="Choose if the object is going to emit particles on collission or not",
    )

    def execute(self, context):
        # Trigger de la funcion de los keyframes
        set_gravity(self.t0, self.gravity, self.v0, self.finalPos, self.bounciness, self.axis, self.colissions, self.particles)

        return {"FINISHED"}

class ANIM_OT_inc_cont(bpy.types.Operator):

    # Declaracion de la clase
    bl_idname = "anim.inc_cont"
    bl_label = "Increment particle counter"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global particle_cont
        particle_cont += 1

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
        row = self.layout.row()
        row.operator("anim.inc_cont", text="Increment particle counter")

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
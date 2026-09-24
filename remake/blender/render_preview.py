"""
render_preview.py -- quick visual check of a built structure (.blend from gblib.finish).

  flatpak run org.blender.Blender -b <abs .blend> --python <abs render_preview.py> -- OUT_PREFIX VIEW...

VIEW = "ext:<az_deg>:<elev_deg>:<dist>"  orbit camera at the model centre
     | "int:<x>:<y>:<z>:<yaw_deg>:<pitch_deg>"  eye point inside, looking along yaw (0 = +Y/north)
"""
import math
import sys

import bpy
from mathutils import Euler, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out, views = argv[0], argv[1:]

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1280, 800
sc.render.film_transparent = False
try:
    sc.eevee.taa_render_samples = 12
except Exception:
    pass
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.world = world

sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4.0
sun.rotation_euler = Euler((math.radians(50), math.radians(10), math.radians(35)))
sc.collection.objects.link(sun)
ground = bpy.data.meshes.new("g")
ground.from_pydata([(-80, -80, -0.01), (80, -80, -0.01), (80, 80, -0.01), (-80, 80, -0.01)], [], [(0, 1, 2, 3)])
gm = bpy.data.materials.new("grass")
gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.36, 0.16, 1)
ground.materials.append(gm)
if not any(o.name.startswith("terrain") for o in bpy.data.objects):
    sc.collection.objects.link(bpy.data.objects.new("ground", ground))

# interior lights from the light_* empties
for ob in list(bpy.data.objects):
    if ob.name.startswith("light_"):
        L = bpy.data.objects.new("pl", bpy.data.lights.new("pl", "POINT"))
        L.data.energy = 150
        L.data.use_shadow = False
        L.location = ob.matrix_world.translation
        sc.collection.objects.link(L)

mins = Vector((1e9, 1e9, 1e9))
maxs = -mins
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name not in ("ground",):
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mins = Vector(map(min, mins, w))
            maxs = Vector(map(max, maxs, w))
centre = (mins + maxs) / 2

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
for i, v in enumerate(views):
    p = v.split(":")
    if p[0] == "ext":
        az, el, dist = map(float, p[1:4])
        a, e = math.radians(az), math.radians(el)
        cam.location = centre + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        d = centre - cam.location
        cam.data.lens = 35
    else:
        x, y, z, yaw, pitch = map(float, p[1:6])
        cam.location = Vector((x, y, z))
        d = Vector((math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), math.tan(math.radians(pitch))))
        cam.data.lens = 18
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)

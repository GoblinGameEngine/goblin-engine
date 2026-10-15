"""render.py -- render warren-kit preview glbs from explicit cameras (Blender):

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render.py -- OUT_PREFIX "GLB;GLB..." CAM [CAM...]

CAM = "x,y,z>tx,ty,tz[@lens_mm]" in the glTF frame (Y up; converted to Blender's Z up: (x, -z, y)).
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out, glbs, cams = argv[0], argv[1].split(";"), argv[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
for g in glbs:
    if g:
        bpy.ops.import_scene.gltf(filepath=g)
sc = bpy.context.scene
names = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in names else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1280, 860
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.62, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.2
sun.rotation_euler = (math.radians(38), math.radians(8), math.radians(140))
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 5000


def bl(p):
    return Vector((p[0], -p[2], p[1]))


for i, c in enumerate(cams):
    lens = 24.0
    if "@" in c:
        c, l = c.split("@")
        lens = float(l)
    a, t = c.split(">")
    pa = bl([float(v) for v in a.split(",")])
    pt = bl([float(v) for v in t.split(",")])
    cam.location = pa
    cam.rotation_euler = (pt - pa).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)

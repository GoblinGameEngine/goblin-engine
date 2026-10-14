"""render_glb.py -- quick look at one or more glbs (the sky islands' previews).

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_glb.py -- OUT_PREFIX GLB [GLB...] -- VIEW...

VIEW = "<az_deg>:<elev_deg>:<dist>[:ortho_scale]" orbiting the bounds' centre (az 0 looks from -Y toward +Y in
Blender, i.e. from the glTF +Z side); ortho_scale > 0 renders orthographic.
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
rest = argv[1:]
cut = rest.index("--")
glbs, views = rest[:cut], rest[cut + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
for gp in glbs:
    bpy.ops.import_scene.gltf(filepath=gp)
for ob in list(bpy.data.objects):
    if ob.name.endswith("-colonly") or "-colonly" in ob.name:
        ob.hide_render = True
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1280, 860
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
sc.collection.objects.link(sun)
lo = Vector((1e9, 1e9, 1e9))
hi = -lo
for ob in sc.objects:
    if ob.type == "MESH" and not ob.hide_render:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
ctr = (lo + hi) / 2
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 20000
for i, v in enumerate(views):
    f = [float(t) for t in v.split(":")]
    az, el, dist = math.radians(f[0]), math.radians(f[1]), f[2]
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = ctr + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    if len(f) > 3 and f[3] > 0:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = f[3]
    else:
        cam.data.type = "PERSP"
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)

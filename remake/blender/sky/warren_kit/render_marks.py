"""render_marks.py -- the family mark sheets, lit like the game: a low sun with shadows, slot materials (glass
glossy, metal metallic, emissive glowing), Freestyle outlines, and each piece labelled with its id (Blender):

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_marks.py -- OUT_PREFIX GLB [night]

writes OUT_PREFIX_0.png (3/4 view from the lane side) and OUT_PREFIX_1.png (square-on elevation).
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out, glb = argv[0], argv[1]
night = len(argv) > 2 and argv[2] == "night"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
names = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in names else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "Standard"
try:
    sc.eevee.use_shadows = True
except AttributeError:
    pass

# materials: vertex colour into a principled shader per slot
for mat in bpy.data.materials:
    slot = mat.name.replace("wk_", "").split(".")[0]
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(bs.outputs[0], o.inputs[0])
    bs.inputs["Roughness"].default_value = 0.85
    if slot == "glass":
        bs.inputs["Roughness"].default_value = 0.12
        bs.inputs["Metallic"].default_value = 0.35
    elif slot in ("metal",):
        bs.inputs["Metallic"].default_value = 0.6
        bs.inputs["Roughness"].default_value = 0.45
    elif slot == "accent":
        bs.inputs["Roughness"].default_value = 0.55
    elif slot == "emissive":
        nt.links.new(ca.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = 6.0 if night else 0.35

w = bpy.data.worlds.new("w")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.04, 0.05, 0.1, 1) if night else (0.55, 0.68, 0.88, 1)
bg.inputs[1].default_value = 0.25 if night else 0.7
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 0.15 if night else 4.0
sun.data.angle = math.radians(2)
sun.rotation_euler = (math.radians(52), 0, math.radians(-38))      # from the front-left, high afternoon
sc.collection.objects.link(sun)

meshes = [ob for ob in sc.objects if ob.type == "MESH"]
lo = Vector((1e9, 1e9, 1e9))
hi = -lo
for ob in meshes:
    blo = Vector((1e9, 1e9, 1e9))
    bhi = -blo
    for c in ob.bound_box:
        p = ob.matrix_world @ Vector(c)
        blo = Vector(map(min, blo, p))
        bhi = Vector(map(max, bhi, p))
    lo = Vector(map(min, lo, blo))
    hi = Vector(map(max, hi, bhi))
    # the label: the piece id on the ground in front of it (Blender: -Y is the street side, glTF +Z)
    cu = bpy.data.curves.new(ob.name + "_lbl", "FONT")
    cu.body = ob.name.split(".")[0]
    cu.size = 0.26
    cu.align_x = "CENTER"
    tx = bpy.data.objects.new(ob.name + "_lbl", cu)
    tx.location = ((blo.x + bhi.x) / 2, blo.y - 0.35, max(blo.z, -0.5) - 0.02)
    sc.collection.objects.link(tx)
    tm = bpy.data.materials.new("lbl")
    tm.use_nodes = True
    tm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1)
    if night:
        tm.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.9, 0.9, 0.9, 1)
        tm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
    cu.materials.append(tm)
    lo.y = min(lo.y, blo.y - 0.6)

pl = bpy.data.meshes.new("ground")                                   # a pale ground catching the shadows
g0, g1 = lo - Vector((3, 3, 0)), hi + Vector((3, 3, 0))
lows = [min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box) for ob in meshes]
gz = min([z for z in lows if z > -1.0] + [0.0]) - 0.03          # under eaves that dip below 0, above deep stilts
pl.from_pydata([(g0.x, g0.y, gz), (g1.x, g0.y, gz), (g1.x, g1.y, gz), (g0.x, g1.y, gz)], [], [(0, 1, 2, 3)])
gob = bpy.data.objects.new("ground", pl)
gm = bpy.data.materials.new("ground")
gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.08, 0.09, 1) if night else (0.62, 0.6, 0.56, 1)
pl.materials.append(gm)
sc.collection.objects.link(gob)

sc.render.use_freestyle = True
sc.render.line_thickness_mode = "ABSOLUTE"
sc.render.line_thickness = 1.1
vl = sc.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
fs.crease_angle = math.radians(140)
ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("lines")
ls.select_by_visibility = True
ls.select_silhouette = ls.select_border = ls.select_crease = True
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("ink")
ls.linestyle.color = (0.08, 0.06, 0.05)
ls.linestyle.thickness = 1.1
ls.linestyle.chaining = "PLAIN"                  # (no stroke chaining across near-collinear edges: it drew strays)
ls.linestyle.use_same_object = True

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 5000
ctr = (lo + hi) / 2
ext = hi - lo
views = [(math.radians(-22), math.radians(24)), (0.0, math.radians(4))]
for i, (az, el) in enumerate(views):
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.data.type = "ORTHO"
    cam.location = ctr + d * (ext.length + 20)
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()                      # fit the pieces (not the ground) in the frame
    pts = [inv @ (ob.matrix_world @ Vector(c)) for ob in meshes for c in ob.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts) - 0.6, max(p.y for p in pts)
    aspect = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(x1 - x0, (y1 - y0) * aspect) * 1.04
    cam.location = cam.matrix_world @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0.0))
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)

"""
Small yard/lot and street-furniture props per
research/scenery_asset_checklist.txt sections 8-9: storage shed,
detached workshop, deck, fire pit, doghouse, post-mounted mailbox,
trash/recycling bin, park bench, bike rack, driveway basketball hoop.
Simple primitive geometry (boxes/cylinders) -- these are small,
low-detail background props, not walkable structures, so they don't use
building_helpers.py's hollow-shell machinery.

Real-world meters. Run headless:
    blender --background --python build_yard_props.py
"""

import sys
import os
import json
import bpy
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_shed(prop_id, width, depth, wall_h, roof_h, tex):
	body = make_box(prop_id + "_body", (width, depth, wall_h), (0.0, 0.0, wall_h / 2.0))
	mat = load_material(prop_id, tex)
	body.data.materials.append(mat)
	cube_uv(body)
	# Simple shallow shed-roof slab (a single tilted box, not a full
	# gable -- sheds/workshops commonly use a plain lean-to roof).
	roof = make_box(prop_id + "_roof", (width * 1.05, depth * 1.05, 0.1), (0.0, 0.0, wall_h + roof_h / 2.0))
	roof.rotation_euler = (math.radians(8.0), 0.0, 0.0)
	bpy.context.view_layer.objects.active = roof
	bpy.ops.object.select_all(action="DESELECT")
	roof.select_set(True)
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
	roof.data.materials.append(mat)
	cube_uv(roof)
	combined = join_objects([body, roof])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": width, "depth": depth, "height": wall_h + roof_h}


def build_deck(prop_id, width, depth, height, tex):
	platform = make_box(prop_id + "_platform", (width, depth, 0.15), (0.0, 0.0, height))
	mat = load_material(prop_id, tex)
	platform.data.materials.append(mat)
	cube_uv(platform)
	objs = [platform]
	rail_h = 0.9
	for sign, axis_w in ((1, width), (-1, width)):
		rail = make_box(prop_id + "_rail_%d" % sign, (axis_w, 0.06, rail_h),
			(0.0, sign * depth / 2.0, height + rail_h / 2.0))
		rail.data.materials.append(mat)
		cube_uv(rail)
		objs.append(rail)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": width, "depth": depth, "height": height}


def build_cylinder_prop(prop_id, radius, height, tex, z_offset=0.0, vertices=16):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, z_offset + height / 2.0), vertices=vertices)
	obj = bpy.context.active_object
	obj.name = prop_id + "-col"
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "radius": radius, "height": height}


def build_doghouse(prop_id, width, depth, wall_h, tex):
	body = make_box(prop_id + "_body", (width, depth, wall_h), (0.0, 0.0, wall_h / 2.0))
	mat = load_material(prop_id, tex)
	body.data.materials.append(mat)
	cube_uv(body)
	import bmesh
	hw, hd = width / 2.0 * 1.1, depth / 2.0 * 1.1
	rise = hw * 0.7
	bm = bmesh.new()
	fl = bm.verts.new((-hw, -hd, wall_h))
	fr = bm.verts.new((hw, -hd, wall_h))
	bl = bm.verts.new((-hw, hd, wall_h))
	br = bm.verts.new((hw, hd, wall_h))
	rl = bm.verts.new((0.0, -hd, wall_h + rise))
	rr = bm.verts.new((0.0, hd, wall_h + rise))
	bm.faces.new((fl, rl, rr, bl))
	bm.faces.new((rl, fr, br, rr))
	bm.faces.new((fl, fr, rl))
	bm.faces.new((bl, rr, br))
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
	mesh = bpy.data.meshes.new(prop_id + "_roof_mesh")
	bm.to_mesh(mesh)
	bm.free()
	roof = bpy.data.objects.new(prop_id + "_roof", mesh)
	bpy.context.collection.objects.link(roof)
	roof.data.materials.append(mat)
	cube_uv(roof)
	combined = join_objects([body, roof])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": width, "depth": depth, "height": wall_h + hw * 0.7}


def build_mailbox_post(prop_id, tex):
	post = make_box(prop_id + "_post", (0.08, 0.08, 1.05), (0.0, 0.0, 0.525))
	box = make_box(prop_id + "_box", (0.45, 0.18, 0.2), (0.0, 0.0, 1.05 + 0.1))
	mat = load_material(prop_id, tex)
	for o in (post, box):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([post, box])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "height": 1.25}


def build_bin(prop_id, tex):
	return build_cylinder_prop(prop_id, radius=0.3, height=0.95, tex=tex, vertices=12)


def build_bench(prop_id, tex):
	seat = make_box(prop_id + "_seat", (1.8, 0.45, 0.08), (0.0, 0.0, 0.45))
	back = make_box(prop_id + "_back", (1.8, 0.06, 0.5), (0.0, -0.2, 0.7))
	mat = load_material(prop_id, tex)
	objs = [seat, back]
	for i, sign in enumerate((-1, 1)):
		leg = make_box(prop_id + "_leg_%d" % i, (0.08, 0.45, 0.45), (sign * 0.75, 0.0, 0.225))
		objs.append(leg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": 1.8}


def build_bike_rack(prop_id, tex):
	mat = load_material(prop_id, tex)
	objs = []
	for i in range(4):
		x = -0.9 + i * 0.6
		hoop = make_box(prop_id + "_hoop_%d" % i, (0.04, 0.04, 0.7), (x, 0.0, 0.35))
		hoop.data.materials.append(mat)
		cube_uv(hoop)
		objs.append(hoop)
	rail = make_box(prop_id + "_rail", (2.0, 0.04, 0.04), (0.0, 0.0, 0.68))
	rail.data.materials.append(mat)
	cube_uv(rail)
	objs.append(rail)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": 2.0}


def build_basketball_hoop(prop_id, tex):
	post = make_box(prop_id + "_post", (0.15, 0.15, 3.05), (0.0, 0.0, 1.525))
	backboard = make_box(prop_id + "_backboard", (1.05, 0.05, 0.7), (0.0, 0.4, 3.05))
	mat = load_material(prop_id, tex)
	for o in (post, backboard):
		o.data.materials.append(mat)
		cube_uv(o)
	bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.02, location=(0.0, 0.55, 2.9))
	rim = bpy.context.active_object
	rim.data.materials.append(mat)
	cube_uv(rim)
	combined = join_objects([post, backboard, rim])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "height": 3.05}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("yard_props", [])

	clear_scene()
	manifest["yard_props"].append(build_shed("shed_storage", width=2.4, depth=3.0, wall_h=2.1, roof_h=0.3, tex="wall_tinted_3.png"))
	clear_scene()
	manifest["yard_props"].append(build_shed("workshop_detached", width=4.0, depth=5.0, wall_h=2.5, roof_h=0.4, tex="wall_tinted_7.png"))
	clear_scene()
	manifest["yard_props"].append(build_deck("deck_backyard", width=4.0, depth=3.0, height=0.5, tex="wall_tinted_2.png"))
	clear_scene()
	manifest["yard_props"].append(build_cylinder_prop("fire_pit", radius=0.5, height=0.35, tex="roof_tinted_3.png"))
	clear_scene()
	manifest["yard_props"].append(build_doghouse("doghouse", width=0.8, depth=1.0, wall_h=0.6, tex="wall_tinted_5.png"))
	clear_scene()
	manifest["yard_props"].append(build_mailbox_post("mailbox_post_curbside", tex="wall_tinted_9.png"))
	clear_scene()
	manifest["yard_props"].append(build_bin("trash_bin", tex="wall_tinted_6.png"))
	clear_scene()
	manifest["yard_props"].append(build_bin("recycling_bin", tex="wall_tinted_8.png"))
	clear_scene()
	manifest["yard_props"].append(build_bench("park_bench", tex="wall_tinted_4.png"))
	clear_scene()
	manifest["yard_props"].append(build_bike_rack("bike_rack", tex="wall_tinted_10.png"))
	clear_scene()
	manifest["yard_props"].append(build_basketball_hoop("basketball_hoop_driveway", tex="wall_tinted_0.png"))
	clear_scene()
	manifest["yard_props"].append(build_cylinder_prop("propane_tank_farm", radius=0.35, height=2.0, tex="wall_tinted_1.png", z_offset=0.35))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_yard_props: wrote %d yard/street props to %s" % (len(manifest["yard_props"]), OUT_DIR))


if __name__ == "__main__":
	main()

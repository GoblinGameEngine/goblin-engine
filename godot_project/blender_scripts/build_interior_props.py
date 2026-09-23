"""
Interior furniture/fixture props -- the 18 items flagged [UNIVERSAL] in
research/interior_props_master_list.md (highest reuse across the 49
building archetypes, build first). Simple primitive box/cylinder
geometry -- small furniture-scale props, not walkable structures, so
building_helpers.py's hollow-shell machinery isn't used here.

Real-world meters. Run headless:
    blender --background --python build_interior_props.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "interior_props_assets")


def build_box_prop(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "size": list(size)}


def build_sofa(prop_id, tex):
	seat = make_box(prop_id + "_seat", (1.8, 0.8, 0.4), (0.0, 0.0, 0.2))
	back = make_box(prop_id + "_back", (1.8, 0.2, 0.6), (0.0, -0.3, 0.5))
	mat = load_material(prop_id, tex)
	objs = [seat, back]
	for sign in (-1, 1):
		arm = make_box(prop_id + "_arm", (0.15, 0.8, 0.55), (sign * 0.83, 0.0, 0.28))
		objs.append(arm)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": 1.8}


def build_armchair(prop_id, tex):
	seat = make_box(prop_id + "_seat", (0.75, 0.75, 0.4), (0.0, 0.0, 0.2))
	back = make_box(prop_id + "_back", (0.75, 0.15, 0.6), (0.0, -0.3, 0.5))
	mat = load_material(prop_id, tex)
	objs = [seat, back]
	for sign in (-1, 1):
		arm = make_box(prop_id + "_arm", (0.12, 0.75, 0.5), (sign * 0.31, 0.0, 0.25))
		objs.append(arm)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_table_with_legs(prop_id, top_w, top_d, top_h, leg_size, tex):
	top = make_box(prop_id + "_top", (top_w, top_d, 0.05), (0.0, 0.0, top_h))
	mat = load_material(prop_id, tex)
	objs = [top]
	for sx in (-1, 1):
		for sy in (-1, 1):
			leg = make_box(prop_id + "_leg_%d_%d" % (sx, sy), (leg_size, leg_size, top_h),
				(sx * (top_w / 2.0 - leg_size), sy * (top_d / 2.0 - leg_size), top_h / 2.0))
			objs.append(leg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "top_w": top_w, "top_d": top_d}


def build_bed_frame(prop_id, tex):
	base = make_box(prop_id + "_base", (1.5, 2.0, 0.3), (0.0, 0.0, 0.15))
	mattress = make_box(prop_id + "_mattress", (1.45, 1.95, 0.25), (0.0, 0.0, 0.3 + 0.125))
	headboard = make_box(prop_id + "_headboard", (1.5, 0.08, 0.9), (0.0, -1.0, 0.45))
	mat = load_material(prop_id, tex)
	objs = [base, mattress, headboard]
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_toilet(prop_id, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4, location=(0.0, 0.0, 0.2), vertices=16)
	bowl = bpy.context.active_object
	tank = make_box(prop_id + "_tank", (0.4, 0.18, 0.35), (0.0, -0.22, 0.55))
	mat = load_material(prop_id, tex)
	for o in (bowl, tank):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([bowl, tank])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_tub(prop_id, tex):
	obj = make_box(prop_id, (0.75, 1.5, 0.5), (0.0, 0.0, 0.25))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_mirror(prop_id, tex):
	obj = make_box(prop_id, (0.6, 0.03, 0.8), (0.0, 0.0, 1.2))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_towel_rack(prop_id, tex):
	bar = make_box(prop_id + "_bar", (0.5, 0.04, 0.04), (0.0, 0.0, 1.0))
	mat = load_material(prop_id, tex)
	objs = [bar]
	for sign in (-1, 1):
		bracket = make_box(prop_id + "_bracket", (0.03, 0.08, 0.03), (sign * 0.24, 0.0, 1.0))
		objs.append(bracket)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_tv_stand(prop_id, tex):
	stand = make_box(prop_id + "_stand", (1.2, 0.4, 0.45), (0.0, 0.0, 0.225))
	tv = make_box(prop_id + "_tv", (1.0, 0.06, 0.55), (0.0, -0.05, 0.45 + 0.275))
	mat = load_material(prop_id, tex)
	for o in (stand, tv):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([stand, tv])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_cash_register(prop_id, tex):
	body = make_box(prop_id + "_body", (0.4, 0.35, 0.25), (0.0, 0.0, 0.125))
	display = make_box(prop_id + "_display", (0.15, 0.05, 0.15), (0.0, -0.15, 0.25 + 0.075))
	mat = load_material(prop_id, tex)
	for o in (body, display):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([body, display])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_bookshelf(prop_id, tex):
	frame = make_box(prop_id + "_frame", (0.9, 0.3, 1.8), (0.0, 0.0, 0.9))
	mat = load_material(prop_id, tex)
	objs = [frame]
	for i in range(4):
		shelf = make_box(prop_id + "_shelf_%d" % i, (0.85, 0.28, 0.03), (0.0, 0.0, 0.3 + i * 0.4))
		objs.append(shelf)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("interior_props", [])
	items = manifest["interior_props"]

	clear_scene(); items.append(build_sofa("sofa", tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_armchair("armchair", tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("coffee_table", (0.9, 0.5, 0.4), 0.2, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_table_with_legs("dining_table", top_w=1.5, top_d=0.9, top_h=0.75, leg_size=0.06, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_table_with_legs("kitchen_table", top_w=1.0, top_d=0.8, top_h=0.75, leg_size=0.05, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_bed_frame("bed_frame", tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("nightstand", (0.45, 0.4, 0.55), 0.275, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("dresser", (1.0, 0.5, 0.9), 0.45, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("refrigerator", (0.7, 0.7, 1.7), 0.85, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("stove_range", (0.75, 0.65, 0.9), 0.45, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("kitchen_sink", (0.7, 0.55, 0.2), 0.85, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_toilet("toilet", tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("bathroom_sink_vanity", (0.6, 0.45, 0.85), 0.425, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_tub("tub_shower", tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_mirror("mirror", tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_towel_rack("towel_rack", tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_tv_stand("tv_entertainment_stand", tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_cash_register("cash_register", tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_bookshelf("bookshelf", tex="wall_tinted_7.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_interior_props: wrote %d interior props to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()

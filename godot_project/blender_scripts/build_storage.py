"""
Remaining Furniture -- Storage (27 of 28; bookshelf already
[UNIVERSAL]-built) from research/interior_props_master_list.md section
3. Mostly box-primitive cabinets/shelving/cases.

Real-world meters. Run headless:
    blender --background --python build_storage.py
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
	return {"id": prop_id}


def build_coat_rack(prop_id, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.8, location=(0.0, 0.0, 0.9), vertices=8)
	post = bpy.context.active_object
	mat = load_material(prop_id, tex)
	objs = [post]
	for i in range(4):
		import math
		ang = i * math.pi / 2.0
		peg = make_box(prop_id + "_peg_%d" % i, (0.15, 0.04, 0.04),
			(0.12 * math.cos(ang), 0.12 * math.sin(ang), 1.6))
		objs.append(peg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_cylinder_prop(prop_id, radius, height, tex, z_offset=0.0, vertices=12):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, z_offset + height / 2.0), vertices=vertices)
	obj = bpy.context.active_object
	obj.name = prop_id + "-col"
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_pigeonhole_wall(prop_id, width, height, depth, rows, cols, tex):
	frame = make_box(prop_id + "_frame", (width, depth, height), (0.0, 0.0, height / 2.0))
	mat = load_material(prop_id, tex)
	objs = [frame]
	cell_w = width / cols
	cell_h = height / rows
	for r in range(rows):
		shelf = make_box(prop_id + "_shelf_%d" % r, (width * 0.98, depth * 0.9, 0.02), (0.0, 0.0, r * cell_h + 0.05))
		objs.append(shelf)
	for c in range(1, cols):
		div = make_box(prop_id + "_div_%d" % c, (0.02, depth * 0.9, height * 0.98), (-width / 2.0 + c * cell_w, 0.0, height / 2.0))
		objs.append(div)
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
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_box_prop("library_stack_range", (1.0, 0.6, 2.2), 1.1, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("china_cabinet_hutch", (1.1, 0.45, 1.9), 0.95, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("sideboard_buffet", (1.3, 0.5, 0.9), 0.45, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("curio_cabinet", (0.7, 0.4, 1.7), 0.85, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("filing_cabinet", (0.45, 0.6, 1.3), 0.65, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("small_office_personal_safe", (0.4, 0.4, 0.4), 0.2, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("retail_shelving_unit", (1.2, 0.4, 2.0), 1.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("pantry_cabinet_shelving", (0.9, 0.4, 2.0), 1.0, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("linen_cabinet", (0.55, 0.4, 1.6), 0.8, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_coat_rack("coat_rack_hall_tree", tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_cylinder_prop("umbrella_stand", radius=0.14, height=0.55, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("gun_cabinet_safe", (0.55, 0.35, 1.5), 0.75, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("toy_storage_bins", (0.6, 0.4, 0.35), 0.175, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("canning_preserve_shelving", (1.0, 0.35, 1.8), 0.9, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("hoosier_pantry_cabinet", (1.0, 0.5, 1.85), 0.925, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("glass_front_retail_display_case", (1.1, 0.5, 1.1), 0.55, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("gym_style_locker", (0.35, 0.45, 1.8), 0.9, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("turnout_gear_rack", (1.5, 0.35, 1.9), 0.95, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("evidence_storage_shelving", (1.2, 0.45, 2.0), 1.0, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_pigeonhole_wall("mail_cubby_key_rack", width=1.0, height=0.8, depth=0.15, rows=4, cols=6, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_pigeonhole_wall("po_box_wall", width=2.0, height=1.8, depth=0.3, rows=8, cols=12, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_pigeonhole_wall("safe_deposit_box_wall", width=1.8, height=1.6, depth=0.4, rows=6, cols=10, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("card_catalog", (0.9, 0.45, 1.1), 0.55, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_pigeonhole_wall("sorting_case_pigeonhole", width=1.6, height=1.2, depth=0.25, rows=6, cols=8, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("heavy_duty_pallet_rack", (2.4, 1.0, 3.0), 1.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("tool_chest_rolling_cabinet", (0.7, 0.45, 0.95), 0.475, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("butlers_pantry_glass_cabinet", (1.0, 0.4, 2.1), 1.05, tex="wall_tinted_8.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_storage: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

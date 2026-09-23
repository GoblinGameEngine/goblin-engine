"""
Civic/Institutional Fixtures (23 items) from
research/interior_props_master_list.md section 10 -- church liturgical
furniture, courthouse/police fixtures, town hall/library/school
fixtures. Mostly box-primitive props.

Real-world meters. Run headless:
    blender --background --python build_civic_fixtures.py
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


def build_cross(prop_id, tex):
	vert = make_box(prop_id + "_vert", (0.08, 0.05, 1.2), (0.0, 0.0, 0.6))
	horiz = make_box(prop_id + "_horiz", (0.6, 0.05, 0.08), (0.0, 0.0, 0.85))
	mat = load_material(prop_id, tex)
	for o in (vert, horiz):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([vert, horiz])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_cell_door(prop_id, tex):
	frame = make_box(prop_id + "_frame", (1.0, 0.1, 2.1), (0.0, 0.0, 1.05))
	mat = load_material(prop_id, tex)
	objs = [frame]
	for i in range(6):
		bar = make_box(prop_id + "_bar_%d" % i, (0.03, 0.03, 2.0), (-0.45 + i * 0.18, 0.0, 1.05))
		objs.append(bar)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_flagpole_set(prop_id, tex):
	mat = load_material(prop_id, tex)
	objs = []
	for sx, h in ((-0.4, 2.4), (0.4, 2.4)):
		bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=h, location=(sx, 0.0, h / 2.0), vertices=8)
		pole = bpy.context.active_object
		objs.append(pole)
		flag = make_box(prop_id + "_flag_%.1f" % sx, (0.35, 0.02, 0.25), (sx + 0.18, 0.0, h - 0.2))
		objs.append(flag)
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

	clear_scene(); items.append(build_box_prop("altar_communion_table", (1.5, 0.6, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("baptismal_font", (0.5, 0.5, 0.9), 0.45, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_cross("cross_crucifix", tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("altar_rail", (2.5, 0.15, 0.75), 0.375, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("vestment_cabinet", (1.0, 0.5, 1.8), 0.9, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("hymnal_rack", (0.4, 0.1, 0.15), 0.5, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("witness_stand", (0.9, 0.9, 1.1), 0.55, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("bailiffs_desk", (1.1, 0.6, 0.8), 0.4, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("holding_cell_bench_bunk", (1.8, 0.5, 0.5), 0.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_cell_door("barred_cell_door", tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("booking_fingerprint_desk", (1.4, 0.6, 1.0), 0.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("mugshot_backdrop", (1.2, 0.05, 1.8), 0.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("bulletproof_glass_partition", (1.5, 0.05, 2.0), 1.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("council_dais_raised_table", (3.0, 1.0, 1.0), 0.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("circulation_desk_library", (1.8, 0.7, 1.05), 0.525, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("study_carrel", (0.75, 0.6, 1.3), 0.65, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("book_repair_table_cart", (0.8, 0.5, 0.85), 0.425, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("chalkboard_whiteboard", (2.0, 0.05, 1.1), 1.4, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("potbelly_wood_stove", (0.5, 0.5, 0.8), 0.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("basketball_hoop_gym", (1.05, 0.1, 3.05), 1.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("gymnasium_stage_platform", (6.0, 3.0, 0.6), 0.3, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("cafeteria_serving_line", (3.0, 0.9, 1.0), 0.5, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_flagpole_set("flag_set_indoor", tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("wanted_poster_notice_board", (0.9, 0.05, 0.7), 1.3, tex="wall_tinted_6.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_civic_fixtures: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

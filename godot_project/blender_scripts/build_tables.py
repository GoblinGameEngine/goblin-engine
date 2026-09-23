"""
Remaining Furniture -- Tables/Surfaces (25 of 28; coffee_table,
dining_table, kitchen_table already [UNIVERSAL]-built) from
research/interior_props_master_list.md section 2. Mostly box-primitive
counters/desks/tables, reusing build_table_with_legs where a
leg-and-top silhouette fits.

Real-world meters. Run headless:
    blender --background --python build_tables.py
"""

import sys
import os
import json

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
	return {"id": prop_id}


def build_counter(prop_id, width, depth, height, tex, with_back=False, back_h=1.2):
	base = make_box(prop_id + "_base", (width, depth, height), (0.0, 0.0, height / 2.0))
	mat = load_material(prop_id, tex)
	objs = [base]
	if with_back:
		back = make_box(prop_id + "_back", (width, 0.1, back_h), (0.0, -depth / 2.0, height + back_h / 2.0))
		objs.append(back)
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

	clear_scene(); items.append(build_box_prop("end_side_table", (0.45, 0.45, 0.5), 0.25, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_table_with_legs("console_table", top_w=1.0, top_d=0.35, top_h=0.75, leg_size=0.04, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_table_with_legs("home_office_desk", top_w=1.2, top_d=0.6, top_h=0.75, leg_size=0.05, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_counter("workbench", width=1.8, depth=0.6, height=0.85, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_table_with_legs("card_games_table", top_w=0.9, top_d=0.9, top_h=0.72, leg_size=0.04, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_counter("bar_counter_backbar", width=2.5, depth=0.6, height=1.05, tex="wall_tinted_8.png", with_back=True, back_h=1.5))
	clear_scene(); items.append(build_counter("checkout_sales_counter", width=1.5, depth=0.6, height=1.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_counter("service_teller_counter", width=2.0, depth=0.6, height=1.1, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_counter("reception_front_desk", width=1.8, depth=0.7, height=1.05, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_counter("pharmacy_dispensing_counter", width=1.6, depth=0.6, height=1.15, tex="wall_tinted_1.png", with_back=True, back_h=1.0))
	clear_scene(); items.append(build_counter("soda_fountain_counter", width=2.2, depth=0.65, height=1.05, tex="wall_tinted_5.png", with_back=True, back_h=1.6))
	clear_scene(); items.append(build_counter("commercial_prep_counter", width=1.8, depth=0.7, height=0.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_counter("butcher_block_counter", width=1.4, depth=0.7, height=0.9, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_table_with_legs("conference_jury_table", top_w=2.4, top_d=1.2, top_h=0.75, leg_size=0.08, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_table_with_legs("teachers_desk", top_w=1.3, top_d=0.65, top_h=0.75, leg_size=0.05, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_table_with_legs("student_desk", top_w=0.55, top_d=0.45, top_h=0.7, leg_size=0.03, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_table_with_legs("drafting_table", top_w=1.1, top_d=0.75, top_h=0.9, leg_size=0.04, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("podium_lectern_pulpit", (0.55, 0.45, 1.1), 0.55, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_counter("judges_bench", width=2.2, depth=0.7, height=1.3, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_table_with_legs("counsel_table", top_w=1.8, top_d=0.8, top_h=0.75, leg_size=0.06, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_table_with_legs("cafeteria_table_bench", top_w=1.8, top_d=0.7, top_h=0.72, leg_size=0.06, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_table_with_legs("long_folding_table", top_w=1.8, top_d=0.75, top_h=0.74, leg_size=0.04, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_box_prop("shop_scale", (0.35, 0.3, 0.2), 0.1, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_table_with_legs("cutting_alterations_table", top_w=1.6, top_d=1.0, top_h=0.85, leg_size=0.06, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("rolltop_desk", (1.1, 0.6, 1.2), 0.6, tex="wall_tinted_5.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_tables: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

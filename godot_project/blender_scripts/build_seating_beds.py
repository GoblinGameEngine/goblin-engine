"""
Remaining Furniture -- Seating (16 of 18; sofa/armchair already
[UNIVERSAL]-built) and Furniture -- Beds/Bedroom (3 of 6; bed_frame/
nightstand/dresser already [UNIVERSAL]-built), from
research/interior_props_master_list.md sections 1 and 4.

Real-world meters. Run headless:
    blender --background --python build_seating_beds.py
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


def build_chair(prop_id, seat_w, seat_d, seat_h, back_h, tex, has_arms=False, reclined=False):
	seat = make_box(prop_id + "_seat", (seat_w, seat_d, 0.06), (0.0, 0.0, seat_h))
	back_tilt = -0.3 if reclined else -seat_d / 2.0 + 0.05
	back = make_box(prop_id + "_back", (seat_w, 0.06, back_h), (0.0, back_tilt, seat_h + back_h / 2.0))
	mat = load_material(prop_id, tex)
	objs = [seat, back]
	for sx in (-1, 1):
		leg = make_box(prop_id + "_leg_%d" % sx, (0.05, 0.05, seat_h), (sx * (seat_w / 2.0 - 0.05), seat_d / 2.0 - 0.05, seat_h / 2.0))
		objs.append(leg)
		leg2 = make_box(prop_id + "_legb_%d" % sx, (0.05, 0.05, seat_h), (sx * (seat_w / 2.0 - 0.05), -seat_d / 2.0 + 0.05, seat_h / 2.0))
		objs.append(leg2)
	if has_arms:
		for sx in (-1, 1):
			arm = make_box(prop_id + "_arm_%d" % sx, (0.06, seat_d, 0.25), (sx * (seat_w / 2.0 - 0.03), 0.0, seat_h + 0.125))
			objs.append(arm)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_bench_row(prop_id, width, depth, seat_h, back_h, has_back, tex):
	seat = make_box(prop_id + "_seat", (width, depth, 0.06), (0.0, 0.0, seat_h))
	mat = load_material(prop_id, tex)
	objs = [seat]
	if has_back:
		back = make_box(prop_id + "_back", (width, 0.06, back_h), (0.0, -depth / 2.0, seat_h + back_h / 2.0))
		objs.append(back)
	for sx in (-1, 0, 1):
		leg = make_box(prop_id + "_leg_%d" % sx, (0.06, depth, seat_h), (sx * width / 2.0 * 0.9, 0.0, seat_h / 2.0))
		objs.append(leg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "width": width}


def build_stool(prop_id, radius, height, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.06, location=(0.0, 0.0, height), vertices=12)
	seat = bpy.context.active_object
	bpy.ops.mesh.primitive_cylinder_add(radius=radius * 0.15, depth=height, location=(0.0, 0.0, height / 2.0), vertices=8)
	pole = bpy.context.active_object
	mat = load_material(prop_id, tex)
	for o in (seat, pole):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([seat, pole])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_booth(prop_id, tex):
	mat = load_material(prop_id, tex)
	objs = []
	table = make_box(prop_id + "_table", (0.8, 0.7, 0.05), (0.0, 0.0, 0.75))
	objs.append(table)
	for sy in (-1, 1):
		seat = make_box(prop_id + "_seat_%d" % sy, (0.9, 0.5, 0.42), (0.0, sy * 0.75, 0.21))
		back = make_box(prop_id + "_back_%d" % sy, (0.9, 0.1, 0.7), (0.0, sy * 1.0, 0.35))
		objs.extend([seat, back])
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_bunk_bed(prop_id, tex):
	mat = load_material(prop_id, tex)
	objs = []
	for level, z in ((0, 0.3), (1, 1.5)):
		bed = make_box(prop_id + "_bed_%d" % level, (0.95, 1.9, 0.25), (0.0, 0.0, z))
		objs.append(bed)
	for sx in (-1, 1):
		post = make_box(prop_id + "_post_%d" % sx, (0.08, 0.08, 1.9), (sx * 0.47, -0.95, 0.95))
		objs.append(post)
		post2 = make_box(prop_id + "_post2_%d" % sx, (0.08, 0.08, 1.9), (sx * 0.47, 0.95, 0.95))
		objs.append(post2)
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

	clear_scene(); items.append(build_box_prop("loveseat_settee", (1.3, 0.75, 0.65), 0.325, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("sectional_sofa", (2.4, 2.0, 0.65), 0.325, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_chair("wicker_rattan_chair", seat_w=0.65, seat_d=0.65, seat_h=0.42, back_h=0.5, tex="wall_tinted_7.png", has_arms=True))
	clear_scene(); items.append(build_stool("bar_counter_stool", radius=0.18, height=0.75, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_chair("barber_styling_chair", seat_w=0.6, seat_d=0.6, seat_h=0.55, back_h=0.7, tex="wall_tinted_5.png", has_arms=True, reclined=True))
	clear_scene(); items.append(build_bench_row("waiting_bench", width=1.5, depth=0.5, seat_h=0.45, back_h=0.5, has_back=True, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_booth("booth_seating", tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_bench_row("church_pew", width=2.5, depth=0.45, seat_h=0.45, back_h=0.8, has_back=True, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_chair("folding_stacking_chair", seat_w=0.45, seat_d=0.45, seat_h=0.45, back_h=0.45, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_bench_row("gymnasium_bleachers", width=4.0, depth=1.2, seat_h=0.4, back_h=0.0, has_back=False, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_bench_row("theater_seating_row", width=3.0, depth=0.6, seat_h=0.45, back_h=0.7, has_back=True, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_bench_row("courtroom_gallery_bench", width=2.5, depth=0.5, seat_h=0.45, back_h=0.75, has_back=True, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("jury_box_seating", (3.5, 1.5, 0.9), 0.45, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_bench_row("locker_room_bench", width=1.8, depth=0.35, seat_h=0.4, back_h=0.0, has_back=False, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_chair("porch_rocking_chair", seat_w=0.55, seat_d=0.55, seat_h=0.42, back_h=0.6, tex="wall_tinted_7.png", has_arms=True))
	clear_scene(); items.append(build_chair("task_office_chair", seat_w=0.5, seat_d=0.5, seat_h=0.45, back_h=0.45, tex="wall_tinted_9.png", has_arms=True))

	clear_scene(); items.append(build_bunk_bed("bunk_bed", tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("wardrobe_armoire", (1.1, 0.55, 1.9), 0.95, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("washstand", (0.6, 0.4, 0.85), 0.425, tex="wall_tinted_0.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_seating_beds: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

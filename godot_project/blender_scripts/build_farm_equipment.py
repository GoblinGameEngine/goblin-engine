"""
Industrial/Farm Equipment (30 items) from
research/interior_props_master_list.md section 11 -- farm machinery,
barn/dairy fixtures, chicken coop fixtures, corn crib tools, workshop
equipment, factory/grain-elevator machinery. Mostly box-primitive props.

Real-world meters. Run headless:
    blender --background --python build_farm_equipment.py
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


def build_tractor(prop_id, tex):
	body = make_box(prop_id + "_body", (1.1, 2.4, 1.0), (0.0, 0.0, 0.8))
	cabin = make_box(prop_id + "_cabin", (1.0, 0.9, 0.9), (0.0, -0.5, 1.5))
	mat = load_material(prop_id, tex)
	objs = [body, cabin]
	for sx, r in ((-1, 0.55), (1, 0.55)):
		wheel = make_box(prop_id + "_wheel_r_%d" % sx, (0.3, 1.1, 1.1), (sx * 0.65, 0.7, 0.55))
		objs.append(wheel)
	for sx in (-1, 1):
		wheel = make_box(prop_id + "_wheel_f_%d" % sx, (0.2, 0.6, 0.6), (sx * 0.55, -1.0, 0.3))
		objs.append(wheel)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_implement(prop_id, width, length, height, tex):
	frame = make_box(prop_id + "_frame", (width, length, 0.2), (0.0, 0.0, height * 0.3))
	arm = make_box(prop_id + "_arm", (0.15, length * 1.3, 0.15), (0.0, 0.0, height * 0.5))
	mat = load_material(prop_id, tex)
	for o in (frame, arm):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([frame, arm])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_tractor("tractor", tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_box_prop("combine_large_implement", (2.6, 5.0, 2.5), 1.25, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_implement("plow", width=1.5, length=2.0, height=0.8, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_implement("disc", width=2.2, length=1.2, height=0.9, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_implement("planter", width=3.0, length=1.5, height=1.0, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_implement("mower", width=1.8, length=1.5, height=0.7, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_implement("baler", width=1.5, length=2.5, height=1.4, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("farm_wagon", (1.5, 3.0, 0.8), 0.6, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("hay_bale_stack", (0.5, 0.5, 0.4), 0.2, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("stanchion_stall_partition", (1.2, 0.1, 1.3), 0.65, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("feed_trough", (1.5, 0.4, 0.4), 0.2, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_cylinder_prop("water_bowl_bucket_livestock", radius=0.2, height=0.3, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("harness_rack", (0.8, 0.2, 1.4), 0.7, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("saddle_stand", (0.4, 0.9, 0.6), 0.3, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("milking_stanchion", (0.7, 1.5, 1.1), 0.55, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_cylinder_prop("milk_can_bulk_tank", radius=0.3, height=0.9, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("nest_box_row", (1.2, 0.35, 0.35), 0.5, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("roosting_bar_perch", (1.0, 0.06, 0.06), 0.6, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("poultry_feeder_waterer", (0.3, 0.3, 0.4), 0.2, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("corn_hook_husking_peg", (0.15, 0.03, 0.03), 0.9, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("grain_scoop_corn_fork", (0.3, 0.1, 0.8), 0.4, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_cylinder_prop("coiled_fence_wire_post_stack", radius=0.35, height=0.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("welding_equipment", (0.5, 0.4, 1.0), 0.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("vise", (0.3, 0.15, 0.2), 0.9, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("production_floor_machinery", (2.0, 3.0, 1.8), 0.9, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("conveyor_line", (0.8, 6.0, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("overhead_lineshaft_crane_track", (0.3, 8.0, 0.3), 4.0, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("truck_scale", (3.5, 8.0, 0.3), 0.15, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("bucket_elevator_leg", (1.0, 1.0, 6.0), 3.0, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("silage_unloader_auger", (0.4, 4.0, 0.5), 0.25, tex="wall_tinted_9.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_farm_equipment: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

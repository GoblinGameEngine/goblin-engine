"""
Retail/Commercial Fixtures (40 items, the largest category) from
research/interior_props_master_list.md section 9 -- clothing store,
general store, movie theater, auto repair/gas station, bank, grocery,
warehouse, and hardware store fixtures. Mostly box-primitive props, a
few cylinders for tanks/lifts.

Real-world meters. Run headless:
    blender --background --python build_retail_fixtures.py
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


def build_rack_frame(prop_id, width, depth, height, tex):
	mat = load_material(prop_id, tex)
	objs = []
	for sx in (-1, 1):
		for sy in (-1, 1):
			post = make_box(prop_id + "_post_%d_%d" % (sx, sy), (0.03, 0.03, height),
				(sx * width / 2.0, sy * depth / 2.0, height / 2.0))
			objs.append(post)
	bar = make_box(prop_id + "_bar", (width, 0.03, 0.03), (0.0, 0.0, height))
	objs.append(bar)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_pole(prop_id, radius, height, tex):
	return build_cylinder_prop(prop_id, radius, height, tex, vertices=10)


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_rack_frame("clothing_rack", width=1.2, depth=0.5, height=1.5, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("mannequin", (0.35, 0.25, 1.7), 0.85, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("glass_display_case_retail", (1.2, 0.55, 1.1), 0.55, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_cylinder_prop("period_barrel", radius=0.3, height=0.7, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("grain_feed_bin_display", (1.0, 0.8, 1.2), 0.6, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_rack_frame("hanging_goods_rack", width=1.5, depth=0.4, height=2.0, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_pole("barber_pole", radius=0.1, height=1.5, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("directory_board", (0.9, 0.08, 1.2), 1.3, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("buzzer_intercom_panel", (0.25, 0.06, 0.35), 1.4, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("bulletin_notice_board", (1.0, 0.06, 0.7), 1.4, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("guest_book_stand", (0.45, 0.35, 1.0), 0.5, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("fitting_room_set", (1.1, 1.1, 2.0), 1.0, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("poster_display_case", (0.8, 0.1, 1.2), 1.1, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("ticket_taker_podium", (0.5, 0.4, 1.1), 0.55, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("box_office_kiosk", (1.2, 1.0, 2.4), 1.2, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("concession_stand_counter", (2.2, 0.7, 1.1), 0.55, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("gas_pump_island", (0.6, 0.4, 1.4), 0.7, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_cylinder_prop("farm_fuel_tank_stand", radius=0.45, height=1.6, tex="wall_tinted_1.png", z_offset=0.8))
	clear_scene(); items.append(build_box_prop("hydraulic_lift", (2.2, 1.0, 0.2), 0.9, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("tire_changer_balancer", (0.8, 0.8, 1.5), 0.75, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_cylinder_prop("tire_rack_stack", radius=0.35, height=1.2, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("air_compressor", (0.6, 0.4, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("engine_hoist", (1.5, 1.2, 2.0), 1.0, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("bank_teller_cage_window", (1.5, 0.6, 2.2), 1.1, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_cylinder_prop("bank_vault_door", radius=1.0, height=0.3, tex="wall_tinted_10.png", vertices=24))
	clear_scene(); items.append(build_pole("velvet_rope_stanchion", radius=0.06, height=1.0, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("standing_writing_counter", (1.2, 0.4, 1.1), 0.55, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("shopping_cart", (0.5, 0.9, 1.0), 0.5, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("cart_corral", (1.5, 1.0, 1.1), 0.55, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("produce_bin_table", (1.2, 0.7, 0.7), 0.35, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("misting_rack", (1.2, 0.3, 1.6), 0.8, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("endcap_display", (0.8, 0.6, 1.6), 0.8, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("forklift", (1.0, 2.0, 1.8), 0.9, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("hand_truck_dolly_pallet_jack", (0.5, 0.6, 1.0), 0.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("loading_dock_leveler", (1.8, 1.5, 0.15), 0.075, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("paint_mixer_can_display", (0.9, 0.6, 1.3), 0.65, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("fastener_bin_wall", (1.4, 0.3, 1.6), 0.8, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("rolling_display_ladder", (0.4, 1.2, 2.2), 1.1, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("key_cutting_station", (0.7, 0.5, 1.0), 0.5, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("tool_pegboard_wall", (1.6, 0.08, 1.6), 1.2, tex="wall_tinted_7.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_retail_fixtures: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

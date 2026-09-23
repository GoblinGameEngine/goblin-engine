"""
Remaining Electronics (14 of 16; tv_entertainment_stand and
cash_register already [UNIVERSAL]-built) from
research/interior_props_master_list.md section 8. Box-primitive props.

Real-world meters. Run headless:
    blender --background --python build_electronics.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "interior_props_assets")


def build_box_prop(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_box_prop("period_radio_cabinet_console", (0.6, 0.4, 0.9), 0.45, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("second_tv_game_console", (0.7, 0.1, 0.45), 1.1, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("computer_library_terminal", (0.45, 0.5, 0.5), 0.85, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("adding_machine_typewriter", (0.3, 0.25, 0.2), 0.85, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("telephone", (0.15, 0.15, 0.15), 0.8, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("police_dispatch_console", (1.4, 0.6, 1.1), 0.55, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("radio_scanner", (0.3, 0.2, 0.25), 0.9, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("security_camera_monitor", (0.4, 0.35, 0.35), 1.2, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("film_projector", (0.6, 0.4, 0.5), 1.0, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("film_reel_storage_rack", (1.0, 0.4, 1.8), 0.9, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("microfilm_reader", (0.5, 0.55, 0.55), 0.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("jukebox", (0.8, 0.5, 1.4), 0.7, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("piano_organ", (1.4, 0.6, 1.1), 0.55, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("interrogation_recording_equipment", (0.4, 0.3, 0.3), 0.85, tex="wall_tinted_9.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_electronics: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()

"""
Farm zone buildings: two farmhouse styles (American Foursquare, gable-
front vernacular), a gambrel-roofed barn, and a pole building. Geometry
helpers (hollow wall shell, door cutting/registration, roof shapes) live
in building_helpers.py, shared with build_downtown_buildings.py.

Real-world feet-derived meters (1ft = 0.3048m), matching
DowntownGenerator.gd/FarmGenerator.gd's own scale convention.

Run headless:
    blender --background --python build_farm_buildings.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_gable_roof, build_gambrel_roof, export_glb, DOOR_HEIGHT,
)

OUT_DIR = os.path.join(REPO, "assets", "farm_assets")


def build_building(building_id, width, depth, wall_h, roof_fn, wall_tex, roof_tex, door_x_frac=0.5):
	openings = []
	shell = build_shell(width, depth, wall_h)
	door_x = (door_x_frac - 0.5) * width
	cut_front_door(shell, door_x, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, door_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = roof_fn(width, depth, wall_h, roof_mat)

	combined = join_objects([shell, roof])
	# "-col" is Godot's glTF-import node-name-suffix convention for real
	# collision -- see building_helpers.py's module docstring for why
	# RingCoords.add_trimesh_collision() is what actually provides it at
	# runtime regardless.
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id,
		"stories": 1,
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest = {"farm_buildings": []}

	# American Foursquare: near-square footprint, 2 full stories, low-
	# pitch roof (approximated as a shallow gable -- a true hip roof is a
	# later visual refinement, not required for the interior/opening spec).
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"farmhouse_foursquare", width=29.0 * FT, depth=29.0 * FT, wall_h=2 * 2.75,
		roof_fn=lambda w, d, base_z, mat: build_gable_roof(w, d, base_z, pitch_deg=22.0, overhang=0.5, material=mat),
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_0.png"))

	# Gable-front vernacular: more elongated, steep gable roof.
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"farmhouse_gable", width=32.0 * FT, depth=40.0 * FT, wall_h=4.3,
		roof_fn=lambda w, d, base_z, mat: build_gable_roof(w, d, base_z, pitch_deg=40.0, overhang=0.6, material=mat),
		wall_tex="wall_tinted_5.png", roof_tex="roof_tinted_2.png"))

	# Barn: gambrel roof (steep lower slope, shallow upper), red siding.
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"barn", width=40.0 * FT, depth=60.0 * FT, wall_h=11.0 * FT,
		roof_fn=lambda w, d, base_z, mat: build_gambrel_roof(
			w, d, base_z, lower_pitch_deg=63.0, upper_pitch_deg=37.0, lower_frac=0.4, overhang=0.4, material=mat),
		wall_tex="wall_tinted_8.png", roof_tex="roof_tinted_1.png", door_x_frac=0.5))

	# Pole building: shallow gable, plain siding -- the "modern equipment
	# shed" contrast alongside the traditional barn.
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"pole_building", width=40.0 * FT, depth=60.0 * FT, wall_h=12.0 * FT,
		roof_fn=lambda w, d, base_z, mat: build_gable_roof(w, d, base_z, pitch_deg=18.0, overhang=0.3, material=mat),
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_3.png"))

	with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_farm_buildings: wrote %d buildings to %s" % (len(manifest["farm_buildings"]), OUT_DIR))


if __name__ == "__main__":
	main()

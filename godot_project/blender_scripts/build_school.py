"""
The two school sub-templates researched in
research/building_catalog/commercial_civic_farm/school.md: a small
one-room rural schoolhouse (gable roof, village tier) and a much larger
consolidated school (flat parapet roof, institutional -- town/city
tier). Completes the 27-archetype commercial/civic/farm building set.
Geometry helpers live in building_helpers.py.

Real-world feet-derived meters (1ft = 0.3048m), matching this project's
established scale convention.

Run headless:
    blender --background --python build_school.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_gable_roof, build_parapet, export_glb, DOOR_HEIGHT,
)

OUT_DIR = os.path.join(REPO, "assets", "downtown_assets")

PARAPET_HEIGHT = 0.6
PARAPET_THICKNESS = 0.15
STORY_H = 3.66


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {"downtown_buildings": []}

	# One-room rural schoolhouse: researched 6-9m x 8-150m(sic, footprint
	# range) -- village-tier, single small room, simple gable roof.
	clear_scene()
	openings = []
	shell = build_shell(8.0, 10.0, 3.2)
	cut_front_door(shell, 0.0, 10.0, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, 10.0)
	wall_mat = load_material("school_oneroom_wall", "wall_tinted_1.png")
	shell.data.materials.append(wall_mat)
	cube_uv(shell)
	roof_mat = load_material("school_oneroom_roof", "roof_tinted_0.png")
	roof = build_gable_roof(8.0, 10.0, 3.2, pitch_deg=25.0, overhang=0.4, material=roof_mat)
	combined = join_objects([shell, roof])
	combined.name = "school_oneroom-col"
	export_glb(combined, OUT_DIR, "school_oneroom.glb")
	manifest["downtown_buildings"].append({
		"id": "school_oneroom", "archetype": "school_oneroom",
		"stories": 1, "wall_h": 3.2, "width": 8.0, "depth": 10.0, "openings": openings,
	})

	# Consolidated school: researched 30-120m x 8-150m(sic) -- town/city
	# tier, large institutional footprint, flat parapet roof (the common
	# mid-20th-century consolidated-school architectural style).
	clear_scene()
	openings = []
	width, depth, wall_h = 40.0, 55.0, STORY_H * 1.3
	shell = build_shell(width, depth, wall_h)
	cut_front_door(shell, 0.0, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, depth)
	wall_mat = load_material("school_consolidated_wall", "wall_tinted_5.png")
	shell.data.materials.append(wall_mat)
	cube_uv(shell)
	roof_mat = load_material("school_consolidated_roof", "roof_tinted_1.png")
	parapet = build_parapet(width, depth, wall_h, PARAPET_HEIGHT, PARAPET_THICKNESS, roof_mat)
	combined = join_objects([shell, parapet])
	combined.name = "school_consolidated-col"
	export_glb(combined, OUT_DIR, "school_consolidated.glb")
	manifest["downtown_buildings"].append({
		"id": "school_consolidated", "archetype": "school_consolidated",
		"stories": max(1, round(wall_h / 3.5)), "wall_h": wall_h,
		"width": width, "depth": depth, "openings": openings,
	})

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_school: manifest now has %d total downtown buildings" % len(manifest["downtown_buildings"]))


if __name__ == "__main__":
	main()

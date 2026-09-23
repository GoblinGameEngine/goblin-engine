"""
New residential building archetypes beyond the original house1/2/3 and
the two farmhouse styles: Ranch, Bungalow/Craftsman, Cape Cod. First
batch of the 17-archetype residential set researched in
research/building_catalog/residential/ -- footprints/wall heights below
are sampled from each archetype file's stated size range. Geometry
helpers (hollow wall shell, door cutting/registration, roof shapes) live
in building_helpers.py, shared with build_downtown_buildings.py and
build_farm_buildings.py.

Kept in its own assets/residential_assets/manifest.json rather than
editor_assets/manifest.json, matching the documented precedent for
downtown_assets/farm_assets: keeps MapEditorUI.gd's existing house
picker (house1/2/3) unaffected by this new set.

Real-world feet-derived meters (1ft = 0.3048m), matching this project's
established scale convention.

Run headless:
    blender --background --python build_residential_buildings.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_gable_roof, export_glb, DOOR_HEIGHT,
)

OUT_DIR = os.path.join(REPO, "assets", "residential_assets")


def build_building(building_id, width, depth, wall_h, roof_pitch_deg, roof_overhang, wall_tex, roof_tex, door_x_frac=0.5):
	openings = []
	shell = build_shell(width, depth, wall_h)
	door_x = (door_x_frac - 0.5) * width
	cut_front_door(shell, door_x, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, door_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = build_gable_roof(width, depth, wall_h, pitch_deg=roof_pitch_deg, overhang=roof_overhang, material=roof_mat)

	combined = join_objects([shell, roof])
	# "-col" is Godot's glTF-import node-name-suffix convention for real
	# collision -- see building_helpers.py's module docstring for why
	# RingCoords.add_trimesh_collision() is what actually provides it at
	# runtime regardless.
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id,
		"archetype": building_id,
		"stories": 1,
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest = {"residential_buildings": []}

	# Ranch house: single story, low-pitch wide gable roof, the
	# archetype-defining case for postwar_suburban_lots.md's attached-
	# garage/wide-driveway-apron pattern (garage itself not modeled here --
	# a separate yard-prop item per generator_rules.md SS13). Footprint
	# sampled from the researched 12.2-18.3m x 9.1-12.2m range, toward the
	# compact end since a very long ranch reads better as a variant later.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"ranch", width=14.0, depth=10.0, wall_h=2.6,
		roof_pitch_deg=18.0, roof_overhang=0.5,
		wall_tex="wall_tinted_3.png", roof_tex="roof_tinted_1.png"))

	# Bungalow/Craftsman: low-slung 1-1.5 story, shallower roof pitch than
	# a farmhouse gable, wider overhang (the classic deep Craftsman eave).
	# Footprint sampled from the researched 8.5-10.7m x 9.1-12.2m range.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"bungalow_craftsman", width=9.5, depth=10.5, wall_h=2.8,
		roof_pitch_deg=20.0, roof_overhang=0.7,
		wall_tex="wall_tinted_7.png", roof_tex="roof_tinted_2.png"))

	# Cape Cod: compact footprint, distinctively STEEP gable roof (the
	# defining silhouette trait) -- researched 7.6-10.7m x 7.6-9.1m range.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"cape_cod", width=8.5, depth=8.0, wall_h=2.6,
		roof_pitch_deg=45.0, roof_overhang=0.4,
		wall_tex="wall_tinted_4.png", roof_tex="roof_tinted_0.png"))

	# Small starter home (Minimal Traditional): smallest single-story
	# footprint in this batch, modest roof pitch, plain massing --
	# researched 7.3-9.1m x 7.6-9.8m range, toward the compact end.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"starter_home_minimal_traditional", width=7.5, depth=8.5, wall_h=2.5,
		roof_pitch_deg=25.0, roof_overhang=0.4,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_3.png"))

	# Colonial Revival: 2-story symmetric massing, moderate roof pitch --
	# researched 9.8-13.7m x 9.1-11m range.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"colonial_revival", width=11.0, depth=9.5, wall_h=2 * 2.6,
		roof_pitch_deg=32.0, roof_overhang=0.45,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_1.png"))

	# Tudor Revival cottage: 1.5-2 story, distinctively STEEP gable (the
	# defining Tudor trait, steeper even than Cape Cod) -- researched
	# 9.1-11.6m x 8.5-10.4m range.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"tudor_revival_cottage", width=10.0, depth=9.5, wall_h=4.4,
		roof_pitch_deg=52.0, roof_overhang=0.35,
		wall_tex="wall_tinted_10.png", roof_tex="roof_tinted_2.png"))

	with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_residential_buildings: wrote %d buildings to %s" % (len(manifest["residential_buildings"]), OUT_DIR))


if __name__ == "__main__":
	main()

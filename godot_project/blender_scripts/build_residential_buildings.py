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
	build_gable_roof, build_gable_roof_frontfacing, build_parapet,
	export_glb, DOOR_HEIGHT, DOOR_WIDTH,
)

OUT_DIR = os.path.join(REPO, "assets", "residential_assets")


def build_building(building_id, width, depth, wall_h, roof_pitch_deg, roof_overhang, wall_tex, roof_tex,
		door_x_frac=0.5, roof_fn=build_gable_roof, stories=1):
	openings = []
	shell = build_shell(width, depth, wall_h)
	door_x = (door_x_frac - 0.5) * width
	cut_front_door(shell, door_x, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, door_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = roof_fn(width, depth, wall_h, pitch_deg=roof_pitch_deg, overhang=roof_overhang, material=roof_mat)

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
		"stories": stories,
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"openings": openings,
	}


def build_multiunit_building(building_id, unit_width, depth, wall_h, unit_count, wall_tex, roof_tex,
		roof_height=1.2, parapet_thickness=0.2, stories=1):
	"""Duplex/rowhouse-style block: ONE shell spanning `unit_count` units
	side by side, with one front door per unit rather than one door for
	the whole footprint -- a duplex or rowhouse genuinely IS a single
	building with several units, not several separately-placeable
	buildings glued together, so this builds it as such rather than
	trying to make individual units independently attachable. Flat
	parapet roofline (via build_parapet, already proven for downtown
	storefronts) rather than a pitched gable -- the common real
	rowhouse/duplex roofline, and simpler to get right across an
	arbitrary unit count than replicating one gable per unit."""
	width = unit_width * unit_count
	openings = []
	shell = build_shell(width, depth, wall_h)

	for i in range(unit_count):
		unit_center_x = (i + 0.5) * unit_width - width / 2.0
		cut_front_door(shell, unit_center_x, depth, DOOR_HEIGHT / 2.0)
		register_front_door(openings, unit_center_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = build_parapet(width, depth, wall_h, height=roof_height, thickness=parapet_thickness, material=roof_mat)

	combined = join_objects([shell, roof])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id,
		"archetype": building_id,
		"stories": stories,
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"unit_count": unit_count,
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

	# Shotgun house: narrow street-facing footprint, one room wide --
	# researched 3.7-4.3m x 12-18m range. Uses the FRONT-FACING gable
	# roof (gable end toward the door wall), the archetype's defining
	# silhouette trait, unlike every house above which is eave-front.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"shotgun", width=4.0, depth=15.0, wall_h=2.5,
		roof_pitch_deg=28.0, roof_overhang=0.35,
		wall_tex="wall_tinted_1.png", roof_tex="roof_tinted_0.png",
		roof_fn=build_gable_roof_frontfacing))

	# Mobile/manufactured home (single-wide): narrow, elongated, very
	# shallow near-flat roof pitch (the defining low-profile silhouette,
	# distinct from the shotgun's steep front gable despite a similar
	# narrow-long footprint) -- researched 4.3-9.8m x 17-24m range,
	# single-wide end.
	clear_scene()
	manifest["residential_buildings"].append(build_building(
		"mobile_home", width=4.6, depth=18.0, wall_h=2.4,
		roof_pitch_deg=6.0, roof_overhang=0.3,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_3.png"))

	# Duplex (side-by-side variant): ONE shell, two units, two front
	# doors -- researched per-building 12.2-15.2m x 8.5-10.4m range.
	clear_scene()
	manifest["residential_buildings"].append(build_multiunit_building(
		"duplex_side_by_side", unit_width=6.5, depth=9.5, wall_h=2.6, unit_count=2,
		wall_tex="wall_tinted_5.png", roof_tex="roof_tinted_1.png"))

	# Rowhouse/townhouse block: three attached units, flat parapet
	# roofline -- researched per-unit 5.5-6.7m x 12.2-15.2m range,
	# 2-3 stories (approximated here as a single taller wall height
	# rather than distinct floor slabs, consistent with how the existing
	# 2-story archetypes above are built).
	clear_scene()
	manifest["residential_buildings"].append(build_multiunit_building(
		"rowhouse_townhouse", unit_width=6.0, depth=13.0, wall_h=2 * 2.7, unit_count=3,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_2.png", stories=2))

	with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_residential_buildings: wrote %d buildings to %s" % (len(manifest["residential_buildings"]), OUT_DIR))


if __name__ == "__main__":
	main()

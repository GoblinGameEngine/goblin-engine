"""
Civic/institutional buildings: town hall, library, fire department,
police station, courthouse (flat-roofed parapet boxes, same convention
as downtown storefronts -- small-town civic buildings are very commonly
flat-roofed brick buildings too), plus a church (gable roof + a simple
steeple tower, the one archetype in this batch needing a distinct
silhouette element). Researched in
research/building_catalog/commercial_civic_farm/. Geometry helpers live
in building_helpers.py.

Courthouse note: per generator_rules.md SS9/SS11, generate at most ONE per
county seat, not per settlement -- this script still only needs to
produce one model; the "once per county seat" rule is a PLACEMENT
constraint for the future generator, not a modeling constraint.

Real-world feet-derived meters (1ft = 0.3048m), matching this project's
established scale convention.

Run headless:
    blender --background --python build_civic_buildings.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_parapet, build_gable_roof, export_glb, make_box,
	DOOR_HEIGHT, DOOR_WIDTH,
)

OUT_DIR = os.path.join(REPO, "assets", "downtown_assets")

PARAPET_HEIGHT = 0.6
PARAPET_THICKNESS = 0.15
STORY_H = 3.66


def build_flat_civic(building_id, width, depth, wall_h, wall_tex, roof_tex, door_x_frac=0.5):
	openings = []
	shell = build_shell(width, depth, wall_h)
	door_x = (door_x_frac - 0.5) * width
	cut_front_door(shell, door_x, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, door_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	parapet = build_parapet(width, depth, wall_h, PARAPET_HEIGHT, PARAPET_THICKNESS, roof_mat)

	combined = join_objects([shell, parapet])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": max(1, round(wall_h / 3.5)), "wall_h": wall_h,
		"width": width, "depth": depth, "openings": openings,
	}


def build_church(building_id, width, depth, wall_h, steeple_size, steeple_h, wall_tex, roof_tex):
	"""Gable-roofed nave + a square steeple tower rising from the front
	roofline, centered on the front wall. The steeple is a simple tall
	box (no spire/belfry louvers at this pass) -- the single cheapest
	addition that reads as "this is a church" from a distance, which is
	the goal for this modeling pass; ornamentation is a later visual
	refinement."""
	openings = []
	shell = build_shell(width, depth, wall_h)
	cut_front_door(shell, 0.0, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = build_gable_roof(width, depth, wall_h, pitch_deg=35.0, overhang=0.4, material=roof_mat)

	steeple = make_box(building_id + "_steeple", (steeple_size, steeple_size, steeple_h),
		(0.0, -depth / 2.0 + steeple_size / 2.0, wall_h + steeple_h / 2.0))
	steeple.data.materials.append(wall_mat)
	cube_uv(steeple)
	# Small pyramidal cap on top of the steeple, same construction
	# technique as build_gable_roof's ridge (a bmesh apex instead of a
	# ridge line -- four triangular faces meeting at one point).
	import bmesh
	import math
	hw = steeple_size / 2.0 * 1.15
	base_z = wall_h + steeple_h
	cap_h = steeple_size * 0.9
	bm = bmesh.new()
	fl = bm.verts.new((-hw, -hw, base_z))
	fr = bm.verts.new((hw, -hw, base_z))
	bl = bm.verts.new((-hw, hw, base_z))
	br = bm.verts.new((hw, hw, base_z))
	apex = bm.verts.new((0.0, 0.0, base_z + cap_h))
	bm.faces.new((fl, fr, apex))
	bm.faces.new((fr, br, apex))
	bm.faces.new((br, bl, apex))
	bm.faces.new((bl, fl, apex))
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
	cap_mesh = bpy.data.meshes.new("steeple_cap_mesh")
	bm.to_mesh(cap_mesh)
	bm.free()
	cap = bpy.data.objects.new("steeple_cap", cap_mesh)
	bpy.context.collection.objects.link(cap)
	cap.data.materials.append(roof_mat)
	cube_uv(cap)

	combined = join_objects([shell, roof, steeple, cap])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": max(1, round(wall_h / 3.5)), "wall_h": wall_h,
		"width": width, "depth": depth, "openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {"downtown_buildings": []}

	# Researched 8-25m x 10-40m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_civic(
		"town_hall", width=14.0, depth=20.0, wall_h=STORY_H * 2.0,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_1.png"))

	# Researched 8-30m x 10-40m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_civic(
		"library", width=16.0, depth=22.0, wall_h=STORY_H * 1.3,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))

	# Researched 8-28m x 10-35m range -- taller for the apparatus bay door.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_civic(
		"fire_department", width=16.0, depth=20.0, wall_h=STORY_H * 1.4,
		wall_tex="wall_tinted_4.png", roof_tex="roof_tinted_3.png"))

	# Researched 15-25m x 20-35m range (city tier; town-tier folds into
	# town_hall per generator_rules.md SS9).
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_civic(
		"police_station", width=18.0, depth=25.0, wall_h=STORY_H * 1.5,
		wall_tex="wall_tinted_10.png", roof_tex="roof_tinted_0.png"))

	# Researched 25-35m x 30-45m range -- the largest, most formal civic
	# building, generate-once-per-county-seat per generator_rules.md.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_civic(
		"courthouse", width=28.0, depth=35.0, wall_h=STORY_H * 3.0,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_1.png", door_x_frac=0.5))

	# Church: gable nave + steeple -- researched 10-24m x 18-45m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_church(
		"church", width=14.0, depth=30.0, wall_h=6.0,
		steeple_size=3.0, steeple_h=8.0,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_2.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_civic_buildings: manifest now has %d total downtown buildings" % len(manifest["downtown_buildings"]))


if __name__ == "__main__":
	main()

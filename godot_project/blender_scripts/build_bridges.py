"""
Bridge/crossing models per research/scenery_asset_checklist.txt section
3 -- split into BIG (main ~45m river channel) and SMALL (4-10m tributary
creeks) per generator_rules.md SS10's channel-width numbers, plus two
simple culvert headwalls for the smallest (2-4m farm ditch) crossings.
A bridge here is a flat deck (a box) spanning the gap, with two low side
rails (thin boxes) -- generic enough to reuse across every span/width
combination in the checklist via one parameterized function.

Real-world meters matching generator_rules.md SS10's own channel-width
figures (45m main channel, 4-10m tributary, 2-4m farm ditch).

Run headless:
    blender --background --python build_bridges.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	REPO, clear_scene, load_material, cube_uv, join_objects,
	make_box, export_glb,
)

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")

DECK_THICKNESS = 0.25
RAIL_HEIGHT = 0.9
RAIL_THICKNESS = 0.12


def build_bridge(bridge_id, span, deck_width, deck_tex, rail_tex, clearance=0.3):
	"""span = gap crossed (channel/creek width, along the bridge's own
	X axis); deck_width = roadway width (along Y). Deck sits `clearance`
	above the water/ditch surface (z=0); rails run along both long
	edges."""
	deck = make_box(bridge_id + "_deck", (span, deck_width, DECK_THICKNESS),
		(0.0, 0.0, clearance + DECK_THICKNESS / 2.0))
	deck_mat = load_material(bridge_id + "_deck", deck_tex)
	deck.data.materials.append(deck_mat)
	cube_uv(deck)

	rail_mat = load_material(bridge_id + "_rail", rail_tex)
	rail_z = clearance + DECK_THICKNESS + RAIL_HEIGHT / 2.0
	rail_a = make_box(bridge_id + "_rail_a", (span, RAIL_THICKNESS, RAIL_HEIGHT),
		(0.0, deck_width / 2.0 - RAIL_THICKNESS / 2.0, rail_z))
	rail_a.data.materials.append(rail_mat)
	cube_uv(rail_a)
	rail_b = make_box(bridge_id + "_rail_b", (span, RAIL_THICKNESS, RAIL_HEIGHT),
		(0.0, -deck_width / 2.0 + RAIL_THICKNESS / 2.0, rail_z))
	rail_b.data.materials.append(rail_mat)
	cube_uv(rail_b)

	combined = join_objects([deck, rail_a, rail_b])
	combined.name = bridge_id + "-col"
	export_glb(combined, OUT_DIR, bridge_id + ".glb")
	return {"id": bridge_id, "span": span, "deck_width": deck_width, "clearance": clearance}


def build_culvert(culvert_id, road_width, ditch_width, tex):
	"""Simplified as a low concrete headwall box spanning the ditch
	beneath a continuous road surface (no separate visible deck -- the
	road itself is unbroken, per how a real culvert reads at grade;
	only the headwall end is visible from the ditch side)."""
	headwall = make_box(culvert_id + "_headwall", (road_width, 0.3, 0.6), (0.0, 0.0, 0.3))
	mat = load_material(culvert_id, tex)
	headwall.data.materials.append(mat)
	cube_uv(headwall)
	headwall.name = culvert_id + "-col"
	export_glb(headwall, OUT_DIR, culvert_id + ".glb")
	return {"id": culvert_id, "road_width": road_width, "ditch_width": ditch_width}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest = {"bridges": [], "culverts": []}

	# --- Big bridges: main river channel, 45m per generator_rules.md SS10 ---
	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_main_downtown", span=45.0, deck_width=20.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_0.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_main_residential", span=45.0, deck_width=10.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_2.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_main_farmroad", span=45.0, deck_width=6.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_4.png"))

	# --- Small bridges: tributary creeks, 4-10m per SS10 ---
	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_small_residential", span=7.0, deck_width=8.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_3.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_small_downtown_sidestreet", span=7.0, deck_width=12.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_5.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_small_farm_lane", span=6.0, deck_width=4.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_6.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"footbridge", span=8.0, deck_width=2.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_7.png"))

	clear_scene()
	manifest["bridges"].append(build_bridge(
		"bridge_minor_spur", span=4.0, deck_width=3.0,
		deck_tex="road_tinted.png", rail_tex="wall_tinted_8.png"))

	# --- Culverts: farm ditches, 2-4m per SS10 ---
	clear_scene()
	manifest["culverts"].append(build_culvert(
		"culvert_creek", road_width=8.0, ditch_width=6.0, tex="wall_tinted_9.png"))

	clear_scene()
	manifest["culverts"].append(build_culvert(
		"culvert_ditch", road_width=6.0, ditch_width=3.0, tex="wall_tinted_10.png"))

	with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_bridges: wrote %d bridges + %d culverts to %s" % (
		len(manifest["bridges"]), len(manifest["culverts"]), OUT_DIR))


if __name__ == "__main__":
	main()

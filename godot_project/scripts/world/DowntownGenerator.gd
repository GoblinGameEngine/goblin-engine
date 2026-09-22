extends Node
class_name DowntownGenerator

# Midwestern downtown zone: a strict, tight grid -- 5 parallel tangential
# streets (4 building-deep bands between them), Main Street the center
# one, running the FULL zone arc length at the width-midline, TWICE as
# wide as the other 4. Cross streets every 6 building-lots along the
# arc. Every downtown street (Main included) is wide enough for on-street
# parking on one side, per spec -- unlike the earlier "slightly
# labyrinthine" jogged version of this zone, downtown does NOT curve or
# kink anywhere: it's the one deliberately strict/rectilinear zone,
# contrasted with residential's and the lake zone's curving streets.
# Buildings (storefronts, post office) are a later phase (Phase C) --
# this only lays down the street/sidewalk skeleton those will sit
# against, flush to the sidewalk edge with zero setback.
#
# Buildings (Phase C): 5 storefront types (general/bank/hardware/diner +
# post office) from blender_scripts/build_downtown_buildings.py's output
# (assets/downtown_assets/*.glb + manifest.json), placed flush to the
# sidewalk of whichever street their band faces, lot-line-to-lot-line
# along the arc. The bank (3-story) and post office (double-wide,
# symmetrical) are placed once each, on the two Main-Street-facing
# bands specifically -- Main Street is where the researched "post office
# and different buildings along it" civic/anchor presence belongs, not
# the two outer, secondary streets.
#
# Real-world feet-derived meters throughout, no compression (see the
# plan's scale-decision rationale): house1/2/3.glb's own footprints
# already read as real-scale, and every dimension here fits comfortably
# within a 785m zone / 200m width.

const FT := 0.3048

const DOWNTOWN_ST_WIDTH := 30.0 * FT   # curb-to-curb: 2 travel lanes + 1 parking lane (one side only)
const MAIN_ST_WIDTH := DOWNTOWN_ST_WIDTH * 2.0
const SIDEWALK_WIDTH := 10.0 * FT      # each side
const HALF_DOWNTOWN_ST := DOWNTOWN_ST_WIDTH * 0.5 + SIDEWALK_WIDTH  # centerline to sidewalk's outer edge, a secondary street
const HALF_MAIN_ST := MAIN_ST_WIDTH * 0.5 + SIDEWALK_WIDTH          # ...Main Street
const BLOCK_SIZE := 6.0 * (25.0 * FT)  # 6 storefront lots (25ft each) per block, along the arc
const UV_TILE := 8.0                   # meters per texture tile, matches StationRingBuilder's TILE_* convention

const DOWNTOWN_ASSETS_DIR := "res://assets/downtown_assets/"
const DOWNTOWN_MANIFEST_PATH := "res://assets/downtown_assets/manifest.json"

# Spacing, requested directly: buildings need real air around them instead
# of sitting flush to the sidewalk and to each other -- fewer buildings
# per block as a result, which is an accepted tradeoff, not a bug.
const SIDEWALK_SETBACK := 3.0  # meters, sidewalk's outer edge to building FRONT
const BUILDING_GAP := 8.0      # meters, between adjacent buildings along the same row

# Gravel alley behind each row of buildings, requested directly: 75% of
# DOWNTOWN_ST_WIDTH, with a little clearance on each side (building-to-
# alley, alley-to-next-street) so it doesn't touch either. MAX_BUILDING_
# DEPTH is the deepest current building (post_office, 27.43m -- see
# assets/downtown_assets/manifest.json).
const ALLEY_WIDTH := DOWNTOWN_ST_WIDTH * 0.75
const ALLEY_CLEARANCE := 2.0    # meters, building-back-to-alley and alley-to-next-sidewalk
const MAX_BUILDING_DEPTH := 28.0
# BAND_DEPTH is budgeted additively from real dimensions -- worst case (a
# band bounded by two SECONDARY streets, not Main, which has more room
# not less): this street's own half-width+sidewalk (flush_x already
# starts measuring from there), then setback + deepest building + both
# alley clearances + alley width, then the FAR street's own half-width+
# sidewalk so the alley clears it too. A guessed constant could silently
# overlap once any of the pieces above changed; this can't.
const BAND_DEPTH := HALF_DOWNTOWN_ST + SIDEWALK_SETBACK + MAX_BUILDING_DEPTH + ALLEY_CLEARANCE + ALLEY_WIDTH + ALLEY_CLEARANCE + HALF_DOWNTOWN_ST

# Building sequences per band -- outer bands (0 and 3, facing the
# secondary streets) never get the bank/post office; the two
# Main-Street-facing bands (1 and 2) each place the anchor bank once,
# then the post office once, then cycle ordinary storefronts for the
# rest of the block run.
const OUTER_SEQUENCE := ["storefront_general", "storefront_hardware", "storefront_diner"]
const MAIN_SEQUENCE := ["storefront_bank", "post_office", "storefront_general", "storefront_diner", "storefront_hardware"]

## `x_center` is the zone-width position Main Street runs along (0 =
## zone-width center). `s_start`/`s_end` are the zone's arc-length
## bounds (see RingCoords.gd for what `s` means). Cross streets span
## from the outermost parallel street to the outermost, connecting the
## whole grid; NeighborhoodGenerator.gd uses the returned entry_x/exit_x
## lists to connect this zone's 5 streets to its neighbors' through the
## inter-zone buffer.
##
## Roads/sidewalks only -- cheap, stays loaded for the whole ring
## regardless of player position (see ZoneStreamer.gd). Buildings +
## street furniture are build_detail_async(), streamed in/out
## separately -- a downtown block can run to 100+ buildings, measured as
## a real stutter done synchronously all at once while the player is
## already nearby. "street_x" is returned (alongside entry_x/exit_x, same
## values) so build_detail_async() doesn't have to recompute it.
static func build_roads(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, width: float, x_center: float = 0.0) -> Dictionary:
	var mesh := ArrayMesh.new()

	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var sidewalk_mat := StandardMaterial3D.new()
	sidewalk_mat.albedo_texture = load("res://assets/textures/sidewalk_tinted_0.png")
	var gravel_mat := StandardMaterial3D.new()
	gravel_mat.albedo_texture = load("res://assets/textures/gravel_tinted.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_sidewalk := SurfaceTool.new()
	st_sidewalk.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_alley := SurfaceTool.new()
	st_alley.begin(Mesh.PRIMITIVE_TRIANGLES)

	# 5 parallel tangential streets: Main at the center, 2 flanking pairs
	# at +/-BAND_DEPTH and +/-2*BAND_DEPTH, giving 4 building-deep bands.
	var street_x := [x_center - 2.0 * BAND_DEPTH, x_center - BAND_DEPTH, x_center,
		x_center + BAND_DEPTH, x_center + 2.0 * BAND_DEPTH]

	for x in street_x:
		var road_width: float = MAIN_ST_WIDTH if is_equal_approx(x, x_center) else DOWNTOWN_ST_WIDTH
		StreetBuilder.build_tangential_strip(st_road, radius, segments, s_start, s_end, x, x, road_width, UV_TILE)
		var hw := road_width * 0.5
		StreetBuilder.build_tangential_strip(st_sidewalk, radius, segments, s_start, s_end,
			x - hw - SIDEWALK_WIDTH * 0.5, x - hw - SIDEWALK_WIDTH * 0.5, SIDEWALK_WIDTH, UV_TILE)
		StreetBuilder.build_tangential_strip(st_sidewalk, radius, segments, s_start, s_end,
			x + hw + SIDEWALK_WIDTH * 0.5, x + hw + SIDEWALK_WIDTH * 0.5, SIDEWALK_WIDTH, UV_TILE)

	var cross_x_start: float = street_x[0] - DOWNTOWN_ST_WIDTH * 0.5 - SIDEWALK_WIDTH
	var cross_x_end: float = street_x[street_x.size() - 1] + DOWNTOWN_ST_WIDTH * 0.5 + SIDEWALK_WIDTH

	var zone_len := s_end - s_start
	var n_blocks := int(floor(zone_len / BLOCK_SIZE))
	for i in range(n_blocks + 1):
		var s_cross := s_start + float(i) * BLOCK_SIZE
		if s_cross > s_end:
			break
		StreetBuilder.build_axial_strip(st_road, radius, segments, s_cross, cross_x_start, cross_x_end, DOWNTOWN_ST_WIDTH, UV_TILE)

	# Gravel alley behind each of the 4 bands' single row of buildings --
	# same flush_x/face_sign per band as _place_buildings_async() uses
	# (must match exactly, or the alley and the buildings it's meant to
	# sit behind land in different places). Positioned at the far end of
	# BAND_DEPTH's own budget: setback + deepest building + one
	# clearance in from the row's front, centered on the alley's own
	# width, with ALLEY_CLEARANCE still free on its far side before the
	# next street's sidewalk (see BAND_DEPTH's own comment).
	var alley_offset := SIDEWALK_SETBACK + MAX_BUILDING_DEPTH + ALLEY_CLEARANCE + ALLEY_WIDTH * 0.5
	var band_fronts := [
		[street_x[1] - HALF_DOWNTOWN_ST, 1.0],
		[street_x[2] - HALF_MAIN_ST, 1.0],
		[street_x[2] + HALF_MAIN_ST, -1.0],
		[street_x[3] + HALF_DOWNTOWN_ST, -1.0],
	]
	for band in band_fronts:
		var flush_x: float = band[0]
		var face_sign: float = band[1]
		var alley_x := flush_x - face_sign * alley_offset
		StreetBuilder.build_tangential_strip(st_alley, radius, segments, s_start, s_end, alley_x, alley_x, ALLEY_WIDTH, UV_TILE)

	st_road.set_material(road_mat)
	st_road.commit(mesh)
	st_sidewalk.set_material(sidewalk_mat)
	st_sidewalk.commit(mesh)
	st_alley.set_material(gravel_mat)
	st_alley.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	# Deliberately NOT named with DistanceCulling's "structure" keyword --
	# roads paint the ground itself and should stay visible as far as the
	# floor does (Main Street runs the full 785m zone length), not
	# disappear at HOUSE_RANGE like an actual building would.
	mesh_instance.name = "DowntownStreets"
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

	return {"entry_x": street_x.duplicate(), "exit_x": street_x.duplicate(), "street_x": street_x.duplicate()}

## Buildings + street furniture -- the expensive, streamed part.
## `street_x`/`x_center` must be build_roads()'s own values for this zone.
static func build_detail_async(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, street_x: Array, x_center: float) -> void:
	await _place_buildings_async(parent, radius, segments, s_start, s_end, street_x)
	await _place_furniture_async(parent, radius, segments, s_start, s_end, street_x, x_center)

## Lamp posts at the curb line (between road and sidewalk, so they clear
## both moving traffic and the buildings sitting flush to the sidewalk's
## OUTER edge with zero setback) on both sides of every street; fire
## hydrants at the sparser interval on one side only.
static func _place_furniture_async(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, street_x: Array, x_center: float) -> void:
	for x in street_x:
		var street_x_val: float = x
		var road_width: float = MAIN_ST_WIDTH if is_equal_approx(street_x_val, x_center) else DOWNTOWN_ST_WIDTH
		var hw := road_width * 0.5
		var x_at := func(_s: float) -> float: return street_x_val
		await StreetFurniture.place_along_async(parent, radius, segments, s_start, s_end, x_at, [-hw, hw])

static func _load_manifest() -> Dictionary:
	var f := FileAccess.open(DOWNTOWN_MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("DowntownGenerator: could not open " + DOWNTOWN_MANIFEST_PATH)
		return {}
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	var by_id := {}
	if not (data is Dictionary):
		push_warning("DowntownGenerator: malformed " + DOWNTOWN_MANIFEST_PATH)
		return by_id
	for entry in data.get("downtown_buildings", []):
		by_id[entry["id"]] = entry
	return by_id

## One building instance, its door flush to (facing_street_x's sidewalk
## edge), `face_sign` toward that street -- see FarmGenerator.gd's
## _place_building() doc comment for the yaw derivation this matches.
static func _place_one(parent: Node3D, manifest: Dictionary, building_id: String,
		radius: float, segments: int, s: float, flush_x: float, face_sign: float, index: int) -> float:
	if not manifest.has(building_id):
		push_warning("DowntownGenerator: no manifest entry for " + building_id)
		return 0.0
	var entry: Dictionary = manifest[building_id]
	var scene: PackedScene = load(DOWNTOWN_ASSETS_DIR + building_id + ".glb")
	if scene == null:
		push_warning("DowntownGenerator: could not load " + building_id + ".glb")
		return 0.0
	var depth: float = entry["depth"]
	var inst := scene.instantiate()
	inst.name = building_id.capitalize().replace(" ", "") + "_structure_%d" % index
	# See FarmGenerator._place_building()'s identical comment: the
	# wrapper's own name above is for OcclusionSetup; DistanceCulling
	# needs the tag on the actual mesh, done here via RingCoords.
	RingCoords.tag_structure_meshes(inst)
	var yaw := PI * 0.5 if face_sign > 0.0 else -PI * 0.5
	# SIDEWALK_SETBACK pushes the building's FRONT face back from the
	# sidewalk edge (flush_x) by 3m, per spec -- center_x is that front
	# face's position, then another half-depth further back to the
	# building's own center.
	var front_x := flush_x - face_sign * SIDEWALK_SETBACK
	var center_x := front_x - face_sign * (depth * 0.5)
	RingCoords.place_on_ring(inst, radius, segments, s, center_x, yaw)
	parent.add_child(inst)
	RingCoords.add_trimesh_collision(inst)
	OpeningsSetup.setup_transformed(inst, entry.get("openings", []))
	return float(entry["width"])

## Fills one band's whole arc-length run with buildings from `sequence`,
## cycled in order, each placed BUILDING_GAP apart along s starting at
## s_start -- fewer buildings per block than the old flush/near-zero-gap
## layout, an accepted tradeoff (see BUILDING_GAP's own comment). Yields
## every building (each one carries a create_trimesh_collision() call,
## the expensive part) so a long block streams in over several frames
## instead of one.
static func _fill_band_async(parent: Node3D, manifest: Dictionary, sequence: Array,
		radius: float, segments: int, s_start: float, s_end: float, flush_x: float, face_sign: float) -> void:
	var s := s_start
	var i := 0
	while s < s_end:
		var building_id: String = sequence[i % sequence.size()]
		var width := _place_one(parent, manifest, building_id, radius, segments, s, flush_x, face_sign, i)
		if width <= 0.0:
			break
		s += width + BUILDING_GAP
		i += 1
		await RingCoords.yield_frame()

static func _place_buildings_async(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, street_x: Array) -> void:
	var manifest := _load_manifest()
	if manifest.is_empty():
		return

	# Band 0 [street_x[0], street_x[1]]: faces street_x[1], from its -X side.
	await _fill_band_async(parent, manifest, OUTER_SEQUENCE, radius, segments, s_start, s_end,
		street_x[1] - HALF_DOWNTOWN_ST, 1.0)
	# Band 1 [street_x[1], Main]: faces Main, from its -X side.
	await _fill_band_async(parent, manifest, MAIN_SEQUENCE, radius, segments, s_start, s_end,
		street_x[2] - HALF_MAIN_ST, 1.0)
	# Band 2 [Main, street_x[3]]: faces Main, from its +X side.
	await _fill_band_async(parent, manifest, MAIN_SEQUENCE, radius, segments, s_start, s_end,
		street_x[2] + HALF_MAIN_ST, -1.0)
	# Band 3 [street_x[3], street_x[4]]: faces street_x[3], from its +X side.
	await _fill_band_async(parent, manifest, OUTER_SEQUENCE, radius, segments, s_start, s_end,
		street_x[3] + HALF_DOWNTOWN_ST, -1.0)

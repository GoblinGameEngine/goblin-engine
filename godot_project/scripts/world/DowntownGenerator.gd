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
const BLOCK_SIZE := 6.0 * (25.0 * FT)  # 6 storefront lots (25ft each) per block, along the arc
const BAND_DEPTH := 120.0 * FT         # one building-deep band, between adjacent parallel streets
const UV_TILE := 8.0                   # meters per texture tile, matches StationRingBuilder's TILE_* convention

const DOWNTOWN_ASSETS_DIR := "res://assets/downtown_assets/"
const DOWNTOWN_MANIFEST_PATH := "res://assets/downtown_assets/manifest.json"
const LOT_GAP := 0.3  # meters, a hair of clearance between adjacent lot-line-to-lot-line buildings

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
static func build(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, width: float, x_center: float = 0.0) -> Dictionary:
	var mesh := ArrayMesh.new()

	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var sidewalk_mat := StandardMaterial3D.new()
	sidewalk_mat.albedo_texture = load("res://assets/textures/sidewalk_tinted_0.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_sidewalk := SurfaceTool.new()
	st_sidewalk.begin(Mesh.PRIMITIVE_TRIANGLES)

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

	st_road.set_material(road_mat)
	st_road.commit(mesh)
	st_sidewalk.set_material(sidewalk_mat)
	st_sidewalk.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	# Deliberately NOT named with DistanceCulling's "structure" keyword --
	# roads paint the ground itself and should stay visible as far as the
	# floor does (Main Street runs the full 785m zone length), not
	# disappear at HOUSE_RANGE like an actual building would.
	mesh_instance.name = "DowntownStreets"
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

	_place_buildings(parent, radius, segments, s_start, s_end, street_x)

	return {"entry_x": street_x.duplicate(), "exit_x": street_x.duplicate()}

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
	var yaw := PI * 0.5 if face_sign > 0.0 else -PI * 0.5
	var center_x := flush_x - face_sign * (depth * 0.5)
	RingCoords.place_on_ring(inst, radius, segments, s, center_x, yaw)
	parent.add_child(inst)
	RingCoords.add_trimesh_collision(inst)
	OpeningsSetup.setup_transformed(inst, entry.get("openings", []))
	return float(entry["width"])

## Fills one band's whole arc-length run with buildings from `sequence`,
## cycled in order, each placed lot-line-to-lot-line (a LOT_GAP hair
## apart) along s starting at s_start.
static func _fill_band(parent: Node3D, manifest: Dictionary, sequence: Array,
		radius: float, segments: int, s_start: float, s_end: float, flush_x: float, face_sign: float) -> void:
	var s := s_start
	var i := 0
	while s < s_end:
		var building_id: String = sequence[i % sequence.size()]
		var width := _place_one(parent, manifest, building_id, radius, segments, s, flush_x, face_sign, i)
		if width <= 0.0:
			break
		s += width + LOT_GAP
		i += 1

static func _place_buildings(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, street_x: Array) -> void:
	var manifest := _load_manifest()
	if manifest.is_empty():
		return
	var half_downtown := DOWNTOWN_ST_WIDTH * 0.5 + SIDEWALK_WIDTH
	var half_main := MAIN_ST_WIDTH * 0.5 + SIDEWALK_WIDTH

	# Band 0 [street_x[0], street_x[1]]: faces street_x[1], from its -X side.
	_fill_band(parent, manifest, OUTER_SEQUENCE, radius, segments, s_start, s_end,
		street_x[1] - half_downtown, 1.0)
	# Band 1 [street_x[1], Main]: faces Main, from its -X side.
	_fill_band(parent, manifest, MAIN_SEQUENCE, radius, segments, s_start, s_end,
		street_x[2] - half_main, 1.0)
	# Band 2 [Main, street_x[3]]: faces Main, from its +X side.
	_fill_band(parent, manifest, MAIN_SEQUENCE, radius, segments, s_start, s_end,
		street_x[2] + half_main, -1.0)
	# Band 3 [street_x[3], street_x[4]]: faces street_x[3], from its +X side.
	_fill_band(parent, manifest, OUTER_SEQUENCE, radius, segments, s_start, s_end,
		street_x[3] + half_downtown, -1.0)

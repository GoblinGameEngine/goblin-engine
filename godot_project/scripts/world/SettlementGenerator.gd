extends Node
class_name SettlementGenerator

# Builds one settlement's roads + buildings, per SettlementLayout.gd's
# axially-oriented grid (Main Street and its parallel rows run ALONG
# the width, cross streets run tangentially, spaced by block_size --
# see that file's header for why). Replaces DowntownGenerator.gd/
# ResidentialGenerator.gd/FarmGenerator.gd/LakeGenerator.gd's road-
# building role entirely: "We are completely abandoning my rules about
# the commercial residential agricultural and lake zones."
#
# Storefronts near each row's own center (the Main-Street segment,
# [-main_street_len/2, main_street_len/2]) reuse the existing downtown_
# assets manifest/models; houses further out (the residential band)
# reuse the existing house1/2/3.glb -- both already-built, already-
# textured, already-cel-shaded asset sets, just placed on a different
# grid now. Only the settlement's MAIN row gets storefronts; every
# other row is purely residential its whole length.
#
# Built synchronously (no per-settlement async streaming, unlike the
# old 4-zone system's ZoneStreamer.gd) -- 9 much smaller settlements add
# up to a comparable or smaller total building count than the old 4
# large zones, and this keeps the change surface much smaller. A
# follow-up could reintroduce streaming if a later density increase
# makes it worth it.

const UV_TILE := 8.0
const DOWNTOWN_ASSETS_DIR := "res://assets/downtown_assets/"
const DOWNTOWN_MANIFEST_PATH := "res://assets/downtown_assets/manifest.json"
const HOUSE_DIR := "res://assets/editor_assets/"
const HOUSE_MANIFEST_PATH := "res://assets/editor_assets/manifest.json"

const STORE_SEQUENCE := ["storefront_general", "storefront_hardware", "storefront_diner", "storefront_bank"]
const HOUSE_IDS := ["house1", "house2", "house3"]

const BUILDING_GAP := 6.0
const HOUSE_SPACING := 22.0
const SIDEWALK_SETBACK := 3.0
const HOUSE_SETBACK := 14.0

static var _downtown_manifest: Dictionary = {}
static var _house_manifest: Dictionary = {}

static func _load_downtown_manifest() -> Dictionary:
	if not _downtown_manifest.is_empty():
		return _downtown_manifest
	var f := FileAccess.open(DOWNTOWN_MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("SettlementGenerator: could not open " + DOWNTOWN_MANIFEST_PATH)
		return {}
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	var by_id := {}
	if data is Dictionary:
		for entry in data.get("downtown_buildings", []):
			by_id[entry["id"]] = entry
	_downtown_manifest = by_id
	return by_id

static func _load_house_manifest() -> Dictionary:
	if not _house_manifest.is_empty():
		return _house_manifest
	var f := FileAccess.open(HOUSE_MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("SettlementGenerator: could not open " + HOUSE_MANIFEST_PATH)
		return {}
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	var by_id := {}
	if data is Dictionary:
		for entry in data.get("houses", []):
			by_id[entry["id"]] = entry
	_house_manifest = by_id
	return by_id

## Builds one settlement's road grid (cheap, synchronous -- meant to
## stay resident for the whole ring's lifetime, matching the old 4-zone
## system's own "always-on skeleton" convention). Buildings are the
## expensive part (RingCoords.add_trimesh_collision() per storefront)
## and are a SEPARATE async call -- see build_buildings_async() below --
## since generating all 9 settlements' buildings synchronously in one
## call was measured live to block the main thread for minutes (the
## whole point of the old system's per-zone async streaming, which this
## rediscovered the hard way rather than skip).
static func build_roads(parent: Node3D, radius: float, segments: int, entry: Dictionary) -> void:
	var mesh := ArrayMesh.new()
	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var sidewalk_mat := StandardMaterial3D.new()
	sidewalk_mat.albedo_texture = load("res://assets/textures/sidewalk_tinted_0.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_sidewalk := SurfaceTool.new()
	st_sidewalk.begin(Mesh.PRIMITIVE_TRIANGLES)

	var cfg: Dictionary = entry["config"]
	var rows := SettlementLayout.axial_row_positions(entry)
	var main_i := SettlementLayout.main_row_index(entry["tier"])
	var res_extent := SettlementLayout.residential_x_extent(entry)
	var main_half: float = cfg["main_street_len"] * 0.5
	var cross_xs := SettlementLayout.cross_street_x_positions(entry)

	for i in range(rows.size()):
		var row_s: float = rows[i]
		var is_main := i == main_i
		var w: float = cfg["main_st_width"] if is_main else cfg["secondary_st_width"]
		StreetBuilder.build_axial_strip(st_road, radius, segments, row_s, -res_extent, res_extent, w, UV_TILE)
		var hw := w * 0.5
		var sw_gap: float = hw + float(cfg["sidewalk_width"]) * 0.5
		StreetBuilder.build_axial_strip(st_sidewalk, radius, segments, row_s - sw_gap, -res_extent, res_extent, cfg["sidewalk_width"], UV_TILE)
		StreetBuilder.build_axial_strip(st_sidewalk, radius, segments, row_s + sw_gap, -res_extent, res_extent, cfg["sidewalk_width"], UV_TILE)

	for cx in cross_xs:
		StreetBuilder.build_tangential_strip(st_road, radius, segments, entry["s_start"], entry["s_end"], cx, cx, cfg["secondary_st_width"], UV_TILE)

	st_road.set_material(road_mat)
	st_road.commit(mesh)
	st_sidewalk.set_material(sidewalk_mat)
	st_sidewalk.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "SettlementRoads_%d" % int(entry["index"])
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

## Buildings -- the expensive part (RingCoords.add_trimesh_collision()
## per storefront is real per-building cost; measured live blocking
## the main thread for minutes across all 9 settlements done
## synchronously). Yields (RingCoords.yield_frame()) every few
## buildings so this streams in across many frames instead of one huge
## hitch -- callers should NOT await this synchronously if the goal is
## a hitch-free load; NeighborhoodGenerator.build_detail_async() fires
## it and lets it run in the background.
const BUILDINGS_PER_YIELD := 3

static func build_buildings_async(parent: Node3D, radius: float, segments: int, entry: Dictionary) -> void:
	var downtown_manifest := _load_downtown_manifest()
	var house_manifest := _load_house_manifest()
	if downtown_manifest.is_empty() or house_manifest.is_empty():
		return
	var rows := SettlementLayout.axial_row_positions(entry)
	var main_i := SettlementLayout.main_row_index(entry["tier"])
	var res_extent := SettlementLayout.residential_x_extent(entry)
	var cfg: Dictionary = entry["config"]
	var main_half: float = float(cfg["main_street_len"]) * 0.5

	var idx := 0
	for i in range(rows.size()):
		var row_s: float = rows[i]
		var is_main := i == main_i
		for face_sign in [1.0, -1.0]:
			if is_main:
				idx = await _fill_storefronts(parent, downtown_manifest, radius, segments, row_s, -main_half, main_half, face_sign, idx)
				idx = await _fill_houses(parent, house_manifest, radius, segments, row_s, main_half, res_extent, face_sign, idx)
				idx = await _fill_houses(parent, house_manifest, radius, segments, row_s, -res_extent, -main_half, face_sign, idx)
			else:
				idx = await _fill_houses(parent, house_manifest, radius, segments, row_s, -res_extent, res_extent, face_sign, idx)

## Fills [x_lo, x_hi] along `row_s` with storefronts, cycling STORE_
## SEQUENCE, spaced by each building's own real width + BUILDING_GAP --
## mirrors the old DowntownGenerator._fill_band_async(), just walking X
## instead of S.
static func _fill_storefronts(parent: Node3D, manifest: Dictionary, radius: float, segments: int,
		row_s: float, x_lo: float, x_hi: float, face_sign: float, idx: int) -> int:
	var x := x_lo
	var k := 0
	while x < x_hi:
		var bid: String = STORE_SEQUENCE[k % STORE_SEQUENCE.size()]
		var width := _place_storefront(parent, manifest, bid, radius, segments, row_s, x, face_sign, idx)
		if width <= 0.0:
			break
		x += width + BUILDING_GAP
		k += 1
		idx += 1
		if idx % BUILDINGS_PER_YIELD == 0:
			await RingCoords.yield_frame()
	return idx

static func _fill_houses(parent: Node3D, manifest: Dictionary, radius: float, segments: int,
		row_s: float, x_lo: float, x_hi: float, face_sign: float, idx: int) -> int:
	var x := x_lo + HOUSE_SPACING * 0.5
	var h := 0
	while x < x_hi:
		var hid: String = HOUSE_IDS[h % HOUSE_IDS.size()]
		_place_house(parent, manifest, hid, radius, segments, row_s, x, face_sign, idx)
		x += HOUSE_SPACING
		h += 1
		idx += 1
		if idx % (BUILDINGS_PER_YIELD * 4) == 0:  # houses have no trimesh collision call -- much cheaper, yield less often
			await RingCoords.yield_frame()
	return idx

## One storefront at (row_s +/- setback, x), door facing back toward the
## row. `face_sign>0` places it on the +S side of the row with yaw=0
## (RingCoords' default orientation already has "forward" = +S, and the
## door sits at -forward per this project's established convention --
## confirmed live in FarmGenerator._place_building()'s own comment --
## so yaw=0 correctly faces the door back toward -S, i.e. toward the
## row); `face_sign<0` mirrors with yaw=PI.
static func _place_storefront(parent: Node3D, manifest: Dictionary, building_id: String,
		radius: float, segments: int, row_s: float, x: float, face_sign: float, index: int) -> float:
	if not manifest.has(building_id):
		return 0.0
	var entry: Dictionary = manifest[building_id]
	var scene: PackedScene = load(DOWNTOWN_ASSETS_DIR + building_id + ".glb")
	if scene == null:
		return 0.0
	var depth: float = entry["depth"]
	var inst := scene.instantiate()
	inst.name = building_id.capitalize().replace(" ", "") + "_structure_%d" % index
	RingCoords.tag_structure_meshes(inst)
	var yaw := 0.0 if face_sign > 0.0 else PI
	var front_s := row_s + face_sign * SIDEWALK_SETBACK
	var center_s := front_s + face_sign * (depth * 0.5)
	RingCoords.place_on_ring(inst, radius, segments, center_s, x, yaw)
	parent.add_child(inst)
	RingCoords.add_trimesh_collision(inst)
	OpeningsSetup.setup_transformed(inst, entry.get("openings", []))
	return float(entry["width"])

## house1/2/3.glb already carry real collision baked in from their
## original export pipeline (same fact ResidentialGenerator.gd's own
## comment already established) -- no add_trimesh_collision() call here.
static func _place_house(parent: Node3D, manifest: Dictionary, house_id: String,
		radius: float, segments: int, row_s: float, x: float, face_sign: float, index: int) -> void:
	if not manifest.has(house_id):
		return
	var entry: Dictionary = manifest[house_id]
	var scene: PackedScene = load(HOUSE_DIR + house_id + ".glb")
	if scene == null:
		return
	var inst := scene.instantiate()
	inst.name = house_id.capitalize() + "_structure_%d" % index
	var yaw := 0.0 if face_sign > 0.0 else PI
	var house_s := row_s + face_sign * HOUSE_SETBACK
	RingCoords.place_on_ring(inst, radius, segments, house_s, x, yaw)
	parent.add_child(inst)
	OpeningsSetup.setup_transformed(inst, entry.get("openings", []))

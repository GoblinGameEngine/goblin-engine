extends Node
class_name FarmGenerator

# Agricultural zone roads: two straight parallel main roads, each
# positioned 25% of the zone's width in from its nearest wall (so at
# WIDTH*0.25 from the wall on each side -- x = +/-(WIDTH*0.5 -
# WIDTH*0.25) = +/-WIDTH*0.25 from center), connected by exactly 4
# straight wall-to-wall streets spaced equally across the zone's arc
# length. No curves here -- unlike residential/lake, the spec gives this
# zone a simple, straight layout, which also just reads as correct for
# farm access roads.
#
# Buildings: 2 farmhouses (1 per main road, each facing its own road) +
# a barn and pole building clustered near farmhouse A, all from
# blender_scripts/build_farm_buildings.py's output (assets/farm_assets/
# *.glb + manifest.json). Crop fields are still a later phase (Phase D,
# once the MultiMesh billboard system is ready).
#
# Setback distances are adapted from the researched real-world figures
# (100+ft farmhouse-to-road, 150ft to the barn, 50-75ft barn-to-pole-
# building) rather than used literally -- the zone is only WIDTH=200m
# wide with both roads already 50m in from each wall, so there isn't
# 150ft (45.7m) of room to spare past a road without crossing the
# zone's far wall. Relative ordering (farmhouse nearest the road, barn
## further out, pole building beside the barn) is what's preserved.
#
# Real-world feet-derived meters, no compression (see DowntownGenerator.gd).

const FT := 0.3048

const MAIN_ROAD_WIDTH := 24.0 * FT   # 2 lanes, no shoulder parking -- farm traffic, not residential
const CONNECTOR_WIDTH := 20.0 * FT
const N_CONNECTORS := 4

const UV_TILE := 8.0

const FARM_ASSETS_DIR := "res://assets/farm_assets/"
const FARM_MANIFEST_PATH := "res://assets/farm_assets/manifest.json"

static func build(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, width: float) -> Dictionary:
	var mesh := ArrayMesh.new()

	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)

	var x_a := -width * 0.25
	var x_b := width * 0.25

	StreetBuilder.build_tangential_strip(st_road, radius, segments, s_start, s_end, x_a, x_a, MAIN_ROAD_WIDTH, UV_TILE)
	StreetBuilder.build_tangential_strip(st_road, radius, segments, s_start, s_end, x_b, x_b, MAIN_ROAD_WIDTH, UV_TILE)

	# 4 connectors, equally spaced -- dividing the zone into 5 equal
	# intervals (4 interior dividers), so the connectors themselves sit
	# evenly spaced with equal margin at each end too.
	var zone_len := s_end - s_start
	var half_width := width * 0.5
	var connector_s: Array = []
	for i in range(1, N_CONNECTORS + 1):
		var s_conn := s_start + zone_len * float(i) / float(N_CONNECTORS + 1)
		connector_s.append(s_conn)
		StreetBuilder.build_axial_strip(st_road, radius, segments, s_conn, -half_width, half_width, CONNECTOR_WIDTH, UV_TILE)

	st_road.set_material(road_mat)
	st_road.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "FarmRoads"  # no "structure" keyword -- see DowntownGenerator.gd's note
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

	_place_buildings(parent, radius, segments, s_start, s_end, x_a, x_b)
	_place_crop_fields(parent, radius, segments, s_start, s_end, x_a, x_b, connector_s)

	return {"entry_x": [x_a, x_b], "exit_x": [x_a, x_b]}

## Fills the open ground BETWEEN the two farm roads (x_a..x_b) with the
## zone's two required fields -- corn on the x_a-facing half, soy on the
## x_b-facing half, split down the zone's own x midline so both read as
## one contiguous field each rather than an interleaved checkerboard.
## The MAIN_ROAD_WIDTH*0.5 inset keeps stalks off the road shoulder;
## connector_s lets CropFieldGenerator skip the 4 cross-streets.
static func _place_crop_fields(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, x_a: float, x_b: float, connector_s: Array) -> void:
	var road_inset := MAIN_ROAD_WIDTH * 0.5 + 2.0
	var field_gap := 3.0  # meters of bare ground straddling the midline between the two fields
	var rng := RandomNumberGenerator.new()
	rng.seed = 20260921  # deterministic field layout, regenerable like the rest of this pipeline

	CropFieldGenerator.build(parent, radius, segments, s_start, s_end,
		x_a + road_inset, -field_gap, "corn", connector_s, rng)
	CropFieldGenerator.build(parent, radius, segments, s_start, s_end,
		field_gap, x_b - road_inset, "soy", connector_s, rng)

static func _load_manifest() -> Dictionary:
	var f := FileAccess.open(FARM_MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("FarmGenerator: could not open " + FARM_MANIFEST_PATH)
		return {}
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	var by_id := {}
	if not (data is Dictionary):
		push_warning("FarmGenerator: malformed " + FARM_MANIFEST_PATH)
		return by_id
	for entry in data.get("farm_buildings", []):
		by_id[entry["id"]] = entry
	return by_id

## Instantiates `building_id`.glb at (s, x) on the ring, its DOOR facing
## toward `face_sign` (+1 = door faces increasing x, -1 = faces
## decreasing x). Confirmed live and initially got this backwards: a
## building's own "forward" (-basis.z) points from the door THROUGH the
## building toward its back wall, not out through the door -- because
## the door is cut into the shell's local +Z wall (building_helpers.py's
## cut_front_door(), Blender y=-depth/2 -> Godot z=+depth/2 on export),
## so walking in -Z (into "forward") is how you walk INTO the building
## through it. A farmhouse placed with the naive "+1 -> forward=+X"
## mapping ended up with its door on the far side from its own road,
## confirmed by comparing door.global_position.x against the road's --
## the fix is the yaw sign below, not the door/geometry convention
## (matches OpeningsSetup.gd/house1's own established front-wall
## convention, no reason to special-case that instead).
## Then spawns the manifest-recorded door/window openings through
## OpeningsSetup.setup_transformed() so they inherit this instance's own
## placement correctly (not a flat Y-rotation -- see that function's
## docstring for why that distinction matters here).
static func _place_building(parent: Node3D, manifest: Dictionary, building_id: String,
		radius: float, segments: int, s: float, x: float, face_sign: float) -> void:
	if not manifest.has(building_id):
		push_warning("FarmGenerator: no manifest entry for " + building_id)
		return
	var entry: Dictionary = manifest[building_id]
	var scene: PackedScene = load(FARM_ASSETS_DIR + building_id + ".glb")
	if scene == null:
		push_warning("FarmGenerator: could not load " + building_id + ".glb")
		return
	var inst := scene.instantiate()
	inst.name = building_id.capitalize().replace(" ", "") + "_structure"
	var yaw := PI * 0.5 if face_sign > 0.0 else -PI * 0.5
	RingCoords.place_on_ring(inst, radius, segments, s, x, yaw)
	parent.add_child(inst)
	RingCoords.add_trimesh_collision(inst)
	OpeningsSetup.setup_transformed(inst, entry.get("openings", []))

static func _place_buildings(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, x_a: float, x_b: float) -> void:
	var manifest := _load_manifest()
	if manifest.is_empty():
		return
	var zone_len := s_end - s_start
	var setback := 12.0  # meters, road shoulder to farmhouse front

	# Farmhouse A, near road A (x_a, the negative-X side): the house sits
	# further toward -X than the road (deeper from center), facing back
	# toward +X to face the road.
	var s_house_a := s_start + zone_len * 0.28
	var x_house_a := x_a - setback
	_place_building(parent, manifest, "farmhouse_foursquare", radius, segments, s_house_a, x_house_a, 1.0)

	# Barn and pole building, clustered further from the road than the
	# farmhouse, offset along the arc so they don't overlap it or each other.
	var s_barn := s_house_a + 45.0
	_place_building(parent, manifest, "barn", radius, segments, s_barn, x_a - setback - 10.0, 1.0)
	var s_pole := s_barn + 55.0
	_place_building(parent, manifest, "pole_building", radius, segments, s_pole, x_a - setback - 10.0, 1.0)

	# Farmhouse B, near road B (x_b, positive side), facing back toward
	# the road (-X direction).
	var s_house_b := s_start + zone_len * 0.65
	var x_house_b := x_b + setback
	_place_building(parent, manifest, "farmhouse_gable", radius, segments, s_house_b, x_house_b, -1.0)

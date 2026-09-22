extends Node
class_name ResidentialGenerator

# Residential subdivision zone: NOT a grid -- two curving main paths
# running the length of the zone, connected by short curving spur roads
# at intervals. Every spur meets each main path at a T -- a 3-way
# intersection (the main path continuing through both directions, plus
# the spur) -- so the intersection mix is "mostly 3-way" by construction,
# with a stop sign posted at each spur where it joins a main path. Roads
# curve via StreetBuilder.build_curved_road()'s smoothstep easing, whose
# derivative is exactly zero at every waypoint -- i.e. each road runs
# straight through every intersection and does its curving in the
# middle of each leg, per spec ("curving, with the only straight
# sections being at intersections").
#
# House placement (Phase B): house1/2/3.glb -- the SAME standalone glb
# PackedScenes + manifest.json MapEditorUI.gd already uses for the flat
# neighborhood map -- alternated along each curving path at even arc-
# length spacing, offset from the path's OWN curve (not its average/base
# line: at any given s the road may be jogged partway through a leg's
# smoothstep ease, and a house set back from the base line instead of
# the actual built curve would drift off its lot at the peak of a bend).
# Real-world feet-derived meters, no compression (see DowntownGenerator.gd).

const FT := 0.3048

const LOCAL_ST_WIDTH := 34.0 * FT      # curb-to-curb, parking both sides
const SIDEWALK_WIDTH := 5.0 * FT       # each side, plus a grass verge gap
const VERGE_WIDTH := 4.0 * FT
const UV_TILE := 8.0

const N_SECTIONS := 9           # cross-section waypoints per main path across the zone
const MEANDER_AMPLITUDE := 20.0 # meters either side of each path's base line
const MEANDER_FREQ := 0.9       # radians per section -- how quickly the meander wanders
const SPUR_EVERY := 2           # a connector spur every SPUR_EVERY-th cross-section

const HOUSE_SPACING := 26.0     # meters, arc-length spacing between houses along a path
const HOUSE_SETBACK := 15.0     # meters, house front to road centerline
const HOUSE_IDS := ["house1", "house2", "house3"]
const HOUSE_DIR := "res://assets/editor_assets/"
const HOUSE_MANIFEST_PATH := "res://assets/editor_assets/manifest.json"

static func _meander_x(base: float, k: int, phase: float) -> float:
	return base + MEANDER_AMPLITUDE * sin(float(k) * MEANDER_FREQ + phase)

## Two curving collector streets (one nearer the downtown boundary, one
## further), each meandering around its own base axial position, joined
## by curving spur roads at every SPUR_EVERY-th cross-section -- each
## spur a 3-way T at both ends, with a stop sign posted at each end.
## Returns each collector's axial position AT the zone boundaries (for
## NeighborhoodGenerator.gd's inter-zone connectors) under "entry_x"/
## "exit_x".
static func build(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, width: float) -> Dictionary:
	var mesh := ArrayMesh.new()

	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var sidewalk_mat := StandardMaterial3D.new()
	sidewalk_mat.albedo_texture = load("res://assets/textures/sidewalk_tinted_0.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_sidewalk := SurfaceTool.new()
	st_sidewalk.begin(Mesh.PRIMITIVE_TRIANGLES)

	var half_width_margin := width * 0.5 - 15.0
	var base_a := -half_width_margin * 0.5
	var base_b := half_width_margin * 0.5

	var wp_a: Array = []
	var wp_b: Array = []
	for k in range(N_SECTIONS + 1):
		var s: float = s_start + (s_end - s_start) * float(k) / float(N_SECTIONS)
		wp_a.append(Vector2(s, _meander_x(base_a, k, 0.0)))
		wp_b.append(Vector2(s, _meander_x(base_b, k, PI * 0.5)))

	var local_hw := LOCAL_ST_WIDTH * 0.5
	var sidewalk_gap := local_hw + VERGE_WIDTH + SIDEWALK_WIDTH * 0.5
	StreetBuilder.build_curved_road(st_road, radius, segments, wp_a, LOCAL_ST_WIDTH, UV_TILE, 1.0,
		st_sidewalk, SIDEWALK_WIDTH, UV_TILE)
	StreetBuilder.build_curved_road(st_road, radius, segments, wp_b, LOCAL_ST_WIDTH, UV_TILE, 1.0,
		st_sidewalk, SIDEWALK_WIDTH, UV_TILE)

	var spur_hw := (LOCAL_ST_WIDTH * 0.8) * 0.5  # spurs read as slightly lower-order than the main paths
	for k in range(N_SECTIONS + 1):
		if k % SPUR_EVERY != 0:
			continue
		var a: Vector2 = wp_a[k]
		var b: Vector2 = wp_b[k]
		# A short curved spur, not a straight cross-connector -- its own
		# waypoints are just its two endpoints, so build_curved_road()'s
		# easing bows it gently between them (zero-derivative at both
		# ends, so it still meets each main path straight-on).
		StreetBuilder.build_curved_road(st_road, radius, segments, [a, b], LOCAL_ST_WIDTH * 0.8, UV_TILE, 1.0)

		StreetBuilder.place_stop_sign(parent, radius, segments, a.x, a.y + spur_hw + 1.0)
		StreetBuilder.place_stop_sign(parent, radius, segments, b.x, b.y - spur_hw - 1.0)

	st_road.set_material(road_mat)
	st_road.commit(mesh)
	st_sidewalk.set_material(sidewalk_mat)
	st_sidewalk.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "ResidentialStreets"  # no "structure" keyword -- see DowntownGenerator.gd's note
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

	_place_houses(parent, radius, segments, wp_a, +1.0)
	_place_houses(parent, radius, segments, wp_b, -1.0)

	return {
		"entry_x": [wp_a[0].y, wp_b[0].y],
		"exit_x": [wp_a[N_SECTIONS].y, wp_b[N_SECTIONS].y],
	}

## The road's actual axial position at arc length `s`, using the SAME
## smoothstep easing StreetBuilder.build_curved_road() built it with --
## finds which [waypoints[i], waypoints[i+1]] leg `s` falls in and
## interpolates within just that leg, matching the real curve rather
## than a straight line between the path's far-apart cross-sections.
static func _curve_x_at(waypoints: Array, s: float) -> float:
	for i in range(waypoints.size() - 1):
		var a: Vector2 = waypoints[i]
		var b: Vector2 = waypoints[i + 1]
		if s >= a.x and s <= b.x:
			return StreetBuilder._curved_x(a.y, b.y, a.x, b.x - a.x, s, 1.0)
	var last: Vector2 = waypoints[waypoints.size() - 1]
	return last.y

static func _load_house_manifest() -> Dictionary:
	var f := FileAccess.open(HOUSE_MANIFEST_PATH, FileAccess.READ)
	if f == null:
		push_warning("ResidentialGenerator: could not open " + HOUSE_MANIFEST_PATH)
		return {}
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	var by_id := {}
	if not (data is Dictionary):
		push_warning("ResidentialGenerator: malformed " + HOUSE_MANIFEST_PATH)
		return by_id
	for entry in data.get("houses", []):
		by_id[entry["id"]] = entry
	return by_id

## Places alternating house1/2/3 instances along `waypoints` at
## HOUSE_SPACING arc-length intervals, set back HOUSE_SETBACK from the
## path's own curve (see _curve_x_at()) on the side `outward_sign`
## points to (+1 = toward -X from the path, i.e. path A's outer/street-
## opposite side; -1 = toward +X, path B's), doors facing back toward
## the road -- see FarmGenerator._place_building()'s doc comment for the
## yaw derivation (confirmed live there that a building's own "forward"
## points THROUGH it from the door to the back wall, not out through the
## door, so +1 needs +90deg here and -1 needs -90deg, not the reverse).
static func _place_houses(parent: Node3D, radius: float, segments: int, waypoints: Array, outward_sign: float) -> void:
	var manifest := _load_house_manifest()
	if manifest.is_empty():
		return
	var s0: float = waypoints[0].x
	var s1: float = waypoints[waypoints.size() - 1].x
	var yaw := PI * 0.5 if outward_sign > 0.0 else -PI * 0.5
	var i := 0
	var s := s0 + HOUSE_SPACING * 0.5
	while s < s1:
		var house_id: String = HOUSE_IDS[i % HOUSE_IDS.size()]
		if manifest.has(house_id):
			var entry: Dictionary = manifest[house_id]
			var scene: PackedScene = load(HOUSE_DIR + house_id + ".glb")
			if scene:
				var inst := scene.instantiate()
				inst.name = house_id.capitalize() + "_structure_%d" % i
				var road_x := _curve_x_at(waypoints, s)
				var house_x := road_x - outward_sign * HOUSE_SETBACK
				RingCoords.place_on_ring(inst, radius, segments, s, house_x, yaw)
				parent.add_child(inst)
				OpeningsSetup.setup_transformed(inst, entry.get("openings", []))
		s += HOUSE_SPACING
		i += 1

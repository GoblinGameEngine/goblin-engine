extends Node
class_name RiverGenerator

# Full ring-spanning river: a swimmable water ribbon following
# TerrainHeight.river_x(s)'s closed-loop meander all the way around,
# plus visual water for the curated ponds and their tributary creeks,
# plus a handful of decorative bridge props at the cleanest road
# crossings (Farm's 4 axial connectors -- see _place_farm_connector_
# bridges()'s own comment for why only those). Everywhere else a road
# crosses this river or its tributaries, TerrainHeight._is_under_road()
# has already kept the ground flat there (see that file) -- this
# generator's job is purely the visible water + a few decorative
# crossing props, not keeping anything from breaking; that part already
# works with zero changes here.
#
# Skips the Lake zone's own [lake_s0, lake_s1] span entirely --
# LakeGenerator.build_water() already covers that stretch with its own
# wider basin (the river flows INTO the lake there, by construction --
# see TerrainHeight.gd's header for the phase tuning that makes this
# land exactly on the lake's existing footprint).
#
# Called once from NeighborhoodGenerator.build_skeleton() (like the
# lake) -- a permanent, always-on landmark, not per-zone streamed detail.

const RIVER_WATER_DROP := 1.5
const POND_WATER_DROP := 1.0
const CREEK_WATER_DROP := 0.6
const TRIGGER_MARGIN := 0.5
const UV_TILE_WATER := 12.0

## Computes bed+depth here (RiverGenerator, unlike TerrainHeight itself,
## is safe to call RingCoords -- see TerrainHeight.gd's dependency-rule
## comment) then hands them to TerrainHeight.water_surface_point().
static func _wsp(radius: float, segments: int, s: float, x: float, up: Vector3, drop: float) -> Vector3:
	var bed := RingCoords.floor_point(radius, segments, s, x)
	var depth := TerrainHeight.depth_at(radius, segments, s, x)
	return TerrainHeight.water_surface_point(bed, depth, up, drop)

static func build(root: Node3D, radius: float, segments: int) -> void:
	var water_mat := StandardMaterial3D.new()
	water_mat.albedo_texture = load("res://assets/textures/water_tinted_0.png")
	water_mat.cull_mode = BaseMaterial3D.CULL_DISABLED  # visible from below while submerged, not just from above
	water_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water_mat.albedo_color = Color(1.0, 1.0, 1.0, 0.92)

	var st_water := SurfaceTool.new()
	st_water.begin(Mesh.PRIMITIVE_TRIANGLES)

	var water_volume := Area3D.new()
	water_volume.name = "RiverWaterVolume"
	water_volume.set_script(load("res://scripts/world/WaterVolume.gd"))
	root.add_child(water_volume)

	var lake_rng := TerrainHeight._lake_s_range(radius)
	var lake_s0: float = lake_rng.x
	var lake_s1: float = lake_rng.y

	var seg_arc := (TAU / segments) * radius
	for i in range(segments):
		var seg_s0 := float(i) * seg_arc
		var seg_s1 := float(i + 1) * seg_arc
		if seg_s1 > lake_s0 and seg_s0 < lake_s1:
			continue  # the lake's own water covers this stretch
		_build_channel_segment(st_water, water_volume, radius, segments, seg_s0, seg_s1)

	_build_ponds_and_creeks(st_water, water_volume, radius, segments)

	st_water.set_material(water_mat)
	var mesh := ArrayMesh.new()
	st_water.commit(mesh)
	var water_instance := MeshInstance3D.new()
	water_instance.name = "river_water_surface"
	water_instance.mesh = mesh
	water_instance.set_script(load("res://scripts/world/LakeWater.gd"))  # same cosmetic UV-scroll, no flow physics
	root.add_child(water_instance)

	_place_farm_connector_bridges(root, radius, segments)

## One segment's worth of the plain river channel: a fixed CHANNEL_BED_
## HALF_WIDTH-wide ribbon following river_x(s) as its centerline. Skips
## its own swim-trigger box wherever a road already crosses here (the
## ground is flat there -- see TerrainHeight._is_under_road() -- and the
## water surface itself dips below that flat grade by construction,
## since water_surface_point() reads depth_at()==0 there too, which
## reads as the river ducking out of sight under the crossing and
## reappearing past it, without any separate bridge-deck cutout needed).
static func _build_channel_segment(st: SurfaceTool, volume: Area3D, radius: float, segments: int,
		seg_s0: float, seg_s1: float) -> void:
	var center0 := TerrainHeight.river_x(radius, seg_s0)
	var center1 := TerrainHeight.river_x(radius, seg_s1)
	var hw := TerrainHeight.CHANNEL_BED_HALF_WIDTH
	var mid_s := (seg_s0 + seg_s1) * 0.5
	var mid_x := TerrainHeight.river_x(radius, mid_s)
	var up := RingCoords.floor_basis(radius, segments, mid_s).y
	var p0 := _wsp(radius, segments, seg_s0, center0 - hw, up, RIVER_WATER_DROP)
	var p1 := _wsp(radius, segments, seg_s0, center0 + hw, up, RIVER_WATER_DROP)
	var p2 := _wsp(radius, segments, seg_s1, center1 + hw, up, RIVER_WATER_DROP)
	var p3 := _wsp(radius, segments, seg_s1, center1 - hw, up, RIVER_WATER_DROP)
	var v0 := seg_s0 / UV_TILE_WATER
	var v1 := seg_s1 / UV_TILE_WATER
	StationRingBuilder._quad(st, p0, p1, p2, p3, up,
		Vector2(-hw / UV_TILE_WATER, v0), Vector2(hw / UV_TILE_WATER, v0),
		Vector2(hw / UV_TILE_WATER, v1), Vector2(-hw / UV_TILE_WATER, v1))

	if TerrainHeight._is_under_road(radius, segments, mid_s, mid_x):
		return
	_add_trigger_box(volume, radius, segments, mid_s, mid_x, hw * 2.2, seg_s1 - seg_s0, RIVER_WATER_DROP)

static func _add_trigger_box(volume: Area3D, radius: float, segments: int,
		mid_s: float, mid_x: float, width: float, chord: float, drop: float) -> void:
	var depth := TerrainHeight.depth_at(radius, segments, mid_s, mid_x)
	var water_depth_here := maxf(0.1, depth - drop)
	var col_h := water_depth_here + TRIGGER_MARGIN
	var basis := RingCoords.floor_basis(radius, segments, mid_s)
	var bed := RingCoords.floor_point(radius, segments, mid_s, mid_x)
	var center := bed + basis.y * (col_h * 0.5)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, col_h, chord * 1.08)
	cs.shape = box
	cs.transform = Transform3D(basis, center)
	volume.add_child(cs)

## Ponds: a simple rectangle of open water (the carved bed underneath is
## a rounded stadium shape via TerrainHeight's own distance formula --
## keeping the WATER polygon a plain rect over the flat bed is a
## deliberate simplification, the rounded banks still show at the very
## edges). Each pond's own creek follows a straight line from the pond
## center to the river's centerline at CREEK_RIVER_S[i], sampled into a
## short chain of ribbon quads (not a single quad -- creeks can run
## diagonally across s AND x, so this can't reuse the channel's
## per-segment-only loop).
static func _build_ponds_and_creeks(st: SurfaceTool, volume: Area3D, radius: float, segments: int) -> void:
	for pond in TerrainHeight.PONDS:
		var s_c: float = pond[0]
		var x_c: float = pond[1]
		var half_len: float = pond[2] * 0.5
		var hw: float = pond[3]
		_build_water_rect(st, volume, radius, segments, s_c - half_len, s_c + half_len, x_c - hw, x_c + hw, POND_WATER_DROP)

	for i in range(TerrainHeight.PONDS.size()):
		var pond: Array = TerrainHeight.PONDS[i]
		var s_c: float = pond[0]
		var x_c: float = pond[1]
		var s_river: float = TerrainHeight.CREEK_RIVER_S[i]
		var x_river := TerrainHeight.river_x(radius, s_river)
		_build_water_strip(st, volume, radius, segments, s_c, x_c, s_river, x_river,
			TerrainHeight.CREEK_HALF_WIDTH, CREEK_WATER_DROP)

static func _build_water_rect(st: SurfaceTool, volume: Area3D, radius: float, segments: int,
		s0: float, s1: float, x0: float, x1: float, drop: float) -> void:
	var seg_arc := (TAU / segments) * radius
	var i0 := int(floor(s0 / seg_arc))
	var i1 := int(ceil(s1 / seg_arc))
	for i in range(i0, i1):
		var seg_s0: float = max(s0, float(i) * seg_arc)
		var seg_s1: float = min(s1, float(i + 1) * seg_arc)
		if seg_s1 <= seg_s0:
			continue
		var mid_s := (seg_s0 + seg_s1) * 0.5
		var up := RingCoords.floor_basis(radius, segments, mid_s).y
		var p0 := _wsp(radius, segments, seg_s0, x0, up, drop)
		var p1 := _wsp(radius, segments, seg_s0, x1, up, drop)
		var p2 := _wsp(radius, segments, seg_s1, x1, up, drop)
		var p3 := _wsp(radius, segments, seg_s1, x0, up, drop)
		var v0 := seg_s0 / UV_TILE_WATER
		var v1 := seg_s1 / UV_TILE_WATER
		StationRingBuilder._quad(st, p0, p1, p2, p3, up,
			Vector2(x0 / UV_TILE_WATER, v0), Vector2(x1 / UV_TILE_WATER, v0),
			Vector2(x1 / UV_TILE_WATER, v1), Vector2(x0 / UV_TILE_WATER, v1))
		if not TerrainHeight._is_under_road(radius, segments, mid_s, (x0 + x1) * 0.5):
			_add_trigger_box(volume, radius, segments, mid_s, (x0 + x1) * 0.5, absf(x1 - x0) * 1.02, seg_s1 - seg_s0, drop)

## A creek from (s_a,x_a) to (s_b,x_b), sampled into N_STEPS straight
## ribbon segments (a creek can run diagonally across both s and x, so
## it needs its own perpendicular-offset quads rather than the channel's
## fixed-width-in-x loop).
const CREEK_STEPS := 8

static func _build_water_strip(st: SurfaceTool, volume: Area3D, radius: float, segments: int,
		s_a: float, x_a: float, s_b: float, x_b: float, half_w: float, drop: float) -> void:
	var prev_s := s_a
	var prev_x := x_a
	for k in range(1, CREEK_STEPS + 1):
		var t := float(k) / float(CREEK_STEPS)
		var s: float = lerpf(s_a, s_b, t)
		var x: float = lerpf(x_a, x_b, t)
		_build_ribbon_quad(st, volume, radius, segments, prev_s, prev_x, s, x, half_w, drop)
		prev_s = s
		prev_x = x

static func _build_ribbon_quad(st: SurfaceTool, volume: Area3D, radius: float, segments: int,
		sa: float, xa: float, sb: float, xb: float, half_w: float, drop: float) -> void:
	var dir := Vector2(sb - sa, xb - xa)
	if dir.length() < 0.01:
		return
	var perp := Vector2(-dir.y, dir.x).normalized() * half_w
	var mid_s := (sa + sb) * 0.5
	var mid_x := (xa + xb) * 0.5
	var up := RingCoords.floor_basis(radius, segments, mid_s).y
	var p0 := _wsp(radius, segments, sa + perp.x, xa + perp.y, up, drop)
	var p1 := _wsp(radius, segments, sa - perp.x, xa - perp.y, up, drop)
	var p2 := _wsp(radius, segments, sb - perp.x, xb - perp.y, up, drop)
	var p3 := _wsp(radius, segments, sb + perp.x, xb + perp.y, up, drop)
	var v0 := sa / UV_TILE_WATER
	var v1 := sb / UV_TILE_WATER
	StationRingBuilder._quad(st, p0, p1, p2, p3, up,
		Vector2(-half_w / UV_TILE_WATER, v0), Vector2(half_w / UV_TILE_WATER, v0),
		Vector2(half_w / UV_TILE_WATER, v1), Vector2(-half_w / UV_TILE_WATER, v1))
	if not TerrainHeight._is_under_road(radius, segments, mid_s, mid_x):
		_add_trigger_box(volume, radius, segments, mid_s, mid_x, half_w * 2.0, dir.length() * 1.1, drop)

## Decorative bridge props wherever a settlement's own Main Street
## (SettlementLayout's axial "main row") crosses the river -- the
## cleanest crossing case available: Main Street runs axially (along x,
## fixed s), so the crossing point is just wherever river_x() at that
## fixed s falls, and the bridge deck naturally needs to span along x,
## matching an axially-placed bridge model's own long axis. Every other
## crossing (a settlement's other rows, cross streets) is left
## undecorated this pass (the ground there is already flat/intact via
## TerrainHeight._is_under_road(), just without a bridge model on top)
## -- a deliberate scope cut, not an oversight.
static func _place_farm_connector_bridges(root: Node3D, radius: float, segments: int) -> void:
	var scene: PackedScene = load("res://assets/infrastructure_assets/bridge_main_farmroad.glb")
	if scene == null:
		return
	var i := 0
	for entry in SettlementLayout.build_layout(radius):
		var main_i := SettlementLayout.main_row_index(entry["tier"])
		var rows := SettlementLayout.axial_row_positions(entry)
		var main_s: float = rows[main_i]
		var x_conn := TerrainHeight.river_x(radius, main_s)
		var main_range := SettlementLayout.main_street_x_range(entry)
		if x_conn < main_range.x or x_conn > main_range.y:
			continue  # this settlement's Main Street doesn't actually reach the river
		var inst := scene.instantiate()
		inst.name = "SettlementRiverBridge_%d" % i
		RingCoords.place_on_ring(inst, radius, segments, main_s, x_conn, PI * 0.5)
		root.add_child(inst)
		i += 1

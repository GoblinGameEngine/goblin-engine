extends Node
class_name LakeGenerator

# The lake's water surface + swimmable volume -- no dedicated shore-road
# loop any more (that whole "Lake zone" concept is gone; see
# SettlementLayout.gd's header). The lake now just sits as a widened
# stretch of the river, centered on the water-founded settlement, built
# using the same assumed water footprint (LAKE_HALF_WIDTH either side of
# centerline) TerrainHeight.gd carves for it.
#
# Real-world feet-derived meters, no compression.

const FT := 0.3048

const LAKE_HALF_WIDTH := 65.0          # assumed water extent either side of centerline
const END_CAP_LEN := 40.0              # arc length each necked-down end uses

const UV_TILE := 8.0

## The lake now sits in a REAL carved basin (TerrainHeight.lake_depth(),
## via RingCoords.floor_point()) rather than the earlier "forced
## perspective" water-above-flat-floor hack -- "the lake will need to be
## a lower elevation as water flows downhill." The water SURFACE is
## still a flat plane (a real body of water has a level surface), placed
## WATER_SURFACE_DROP below the original, ungraded shoreline grade --
## always shallower than TerrainHeight's own minimum carved depth within
## the lake's footprint (CHANNEL_DEPTH, at the necked ends), so there is
## always a real bed below the water anywhere this mesh is built.
const WATER_SURFACE_DROP := 2.0
const WATER_TRIGGER_MARGIN := 0.6  # extra headroom above the surface the swim volume still counts as "in water"
const UV_TILE_WATER := 12.0

## The carved bed at (s, x), then lifted back up to the flat water
## surface level (WATER_SURFACE_DROP below original grade) along `up`.
static func _water_surface_point(radius: float, segments: int, s: float, x: float, up: Vector3) -> Vector3:
	var bed := RingCoords.floor_point(radius, segments, s, x)
	var depth := TerrainHeight.depth_at(radius, segments, s, x)
	return bed + up * (depth - WATER_SURFACE_DROP)

## Builds the lake's water surface + swimmable volume. Called once from
## NeighborhoodGenerator.build_skeleton() (NOT from build_detail_async
## above) -- water is a permanent landmark like the roads, not streamed
## buildings/crops the player has to walk up to first; see that call
## site's own comment. Water plane sits a shallow WATER_HEIGHT above the
## ordinary shared floor (see the constant's own comment) and tapers to
## 0 width at both ends of [s_start, s_end] over END_CAP_LEN, echoing the
## road loop's own rounded end caps.
static func build_water(root: Node3D, radius: float, segments: int, s_start: float, s_end: float) -> void:
	var straight_s0 := s_start + END_CAP_LEN
	var straight_s1 := s_end - END_CAP_LEN

	var water_mat := StandardMaterial3D.new()
	water_mat.albedo_texture = load("res://assets/textures/water_tinted_0.png")
	water_mat.cull_mode = BaseMaterial3D.CULL_DISABLED  # visible from below while submerged, not just from above
	water_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water_mat.albedo_color = Color(1.0, 1.0, 1.0, 0.92)

	var st_water := SurfaceTool.new()
	st_water.begin(Mesh.PRIMITIVE_TRIANGLES)

	var water_volume := Area3D.new()
	water_volume.name = "LakeWaterVolume"
	water_volume.set_script(load("res://scripts/world/WaterVolume.gd"))
	root.add_child(water_volume)

	var seg_arc := (TAU / segments) * radius
	var i0 := int(floor(s_start / seg_arc))
	var i1 := int(ceil(s_end / seg_arc))
	for i in range(i0, i1):
		var seg_s0: float = max(s_start, float(i) * seg_arc)
		var seg_s1: float = min(s_end, float(i + 1) * seg_arc)
		if seg_s1 <= seg_s0:
			continue
		var hw_a := _lake_half_width(seg_s0, s_start, s_end, straight_s0, straight_s1)
		var hw_b := _lake_half_width(seg_s1, s_start, s_end, straight_s0, straight_s1)
		if hw_a <= 0.1 and hw_b <= 0.1:
			continue
		var mid_s := (seg_s0 + seg_s1) * 0.5
		var up := RingCoords.floor_basis(radius, segments, mid_s).y
		var p0 := _water_surface_point(radius, segments, seg_s0, -hw_a, up)
		var p1 := _water_surface_point(radius, segments, seg_s0, hw_a, up)
		var p2 := _water_surface_point(radius, segments, seg_s1, hw_b, up)
		var p3 := _water_surface_point(radius, segments, seg_s1, -hw_b, up)
		var v0 := seg_s0 / UV_TILE_WATER
		var v1 := seg_s1 / UV_TILE_WATER
		StationRingBuilder._quad(st_water, p0, p1, p2, p3, up,
			Vector2(-hw_a / UV_TILE_WATER, v0), Vector2(hw_a / UV_TILE_WATER, v0),
			Vector2(hw_b / UV_TILE_WATER, v1), Vector2(-hw_b / UV_TILE_WATER, v1))

		var box_hw: float = max(hw_a, hw_b)
		if box_hw > 0.1:
			_add_water_trigger_box(water_volume, radius, segments, mid_s, seg_s1 - seg_s0, box_hw)

	st_water.set_material(water_mat)
	var water_mesh := ArrayMesh.new()
	st_water.commit(water_mesh)
	var water_instance := MeshInstance3D.new()
	water_instance.name = "lake_water_surface"  # LakeSetup._find() matches this prefix
	water_instance.mesh = water_mesh
	root.add_child(water_instance)

	LakeSetup.setup(root)  # attaches LakeWater.gd's cosmetic UV-scroll to the mesh just built above

## Half-width of the water polygon at arc length `s`: full LAKE_HALF_WIDTH
## in the straight middle section, smoothstepped down to 0 over the last
## END_CAP_LEN at each end so the lake reads as a rounded oval rather than
## a sharp-cornered rectangle.
static func _lake_half_width(s: float, s_start: float, s_end: float, straight_s0: float, straight_s1: float) -> float:
	if s < straight_s0:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clamp((s - s_start) / (straight_s0 - s_start), 0.0, 1.0))
	if s > straight_s1:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clamp((s_end - s) / (s_end - straight_s1), 0.0, 1.0))
	return LAKE_HALF_WIDTH

## One convex swim-trigger box for one ring segment's worth of lake,
## spanning from the carved bed (at x=0, the basin's deepest point this
## segment) up through WATER_TRIGGER_MARGIN above the water surface.
## `chord` and `half_width` bound the box's footprint; `radius`/
## `segments`/`mid_s` place and orient it via the same flat-quad floor
## math everything else on the ring uses (RingCoords), so it never
## floats off the real segment the way an idealized-circle placement would.
static func _add_water_trigger_box(parent: Node3D, radius: float, segments: int,
		mid_s: float, chord: float, half_width: float) -> void:
	var basis := RingCoords.floor_basis(radius, segments, mid_s)
	var depth := TerrainHeight.depth_at(radius, segments, mid_s, 0.0)
	var water_depth_here := maxf(0.1, depth - WATER_SURFACE_DROP)  # bed-to-surface, along "up"
	var col_h := water_depth_here + WATER_TRIGGER_MARGIN
	var bed := RingCoords.floor_point(radius, segments, mid_s, 0.0)
	var center := bed + basis.y * (col_h * 0.5)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(half_width * 2.0, col_h, chord * 1.08)
	cs.shape = box
	cs.transform = Transform3D(basis, center)
	parent.add_child(cs)

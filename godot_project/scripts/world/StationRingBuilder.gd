extends Node
class_name StationRingBuilder

# Procedurally builds a straight-segment polygon approximation of a
# circular ring corridor (floor + ceiling + 2 side walls per segment) for
# the rotating space-station map (see scripts/SpaceStation.gd and the
# plan this came from, .claude/plans/warm-popping-elephant.md, for the
# physics rationale). A straight-line polygon approximation rather than a
# true curved surface deliberately -- collision is then ordinary flat
# triangle geometry (no curved-collision edge cases to fight), while
# still reading as smoothly round at this scale: SEGMENTS=96 is 3.75
# degrees per segment.
#
# Built around local X, the ring's central axis (ring_body never moves --
# see StationPlayer.gd for the matching radial-gravity math) -- angle 0
# points along +Y, sweeping toward +Z.

const TILE_FLOOR := 8.0
const TILE_WALL := 6.0
# "Just make a BIG animated sky texture for the ceiling" -- sky_day.png/
# sky_night.png are now upscaled real photos (blender_scripts/
# upscale_sky_wallpapers.py), not a tileable procedural pattern, so this
# is chosen for "big" (one tile spans a real chunk of the ceiling) more
# than for hiding the repeat seam, which a real photo can't avoid the
# way the earlier GIMP-drawn art could.
const TILE_CEILING := 200.0

## Adds two triangles for the quad a->b->c->d (a proper perimeter walk,
## not a crossed one) with `desired_normal` set explicitly on every
## vertex, picking winding so the quad's own geometric normal agrees
## with it -- lets every call site just state the physically correct
## in/out direction instead of hand-deriving triangle order.
static func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3,
		desired_normal: Vector3, uv_a: Vector2, uv_b: Vector2, uv_c: Vector2, uv_d: Vector2) -> void:
	var geo_normal := (b - a).cross(d - a)
	var flip := geo_normal.dot(desired_normal) < 0.0
	var ordered: Array
	if not flip:
		ordered = [[a, uv_a], [b, uv_b], [c, uv_c], [a, uv_a], [c, uv_c], [d, uv_d]]
	else:
		ordered = [[a, uv_a], [c, uv_c], [b, uv_b], [a, uv_a], [d, uv_d], [c, uv_c]]
	for pair in ordered:
		st.set_normal(desired_normal)
		st.set_uv(pair[1])
		st.add_vertex(pair[0])

## Commits the floor surface (adaptively x-sliced per TerrainHeight's
## carved/raised terrain breakpoints) into `mesh` as a new surface.
## Factored out of build() so FlatMapRenderer.gd can build just the
## floor (with RingCoords.FLAT_MODE unrolling it instead of wrapping it
## around the cylinder) without the ceiling/walls, which are built in
## real, non-flat 3D space and aren't part of the overhead map.
static func build_floor_surface(mesh: ArrayMesh, radius: float, segments: int, half_w: float, floor_material: Material) -> void:
	var st_floor := SurfaceTool.new()
	st_floor.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(segments):
		var a0 := (TAU / segments) * i
		var a1 := (TAU / segments) * (i + 1)
		var s0 := a0 * radius
		var s1 := a1 * radius
		var mid := (a0 + a1) * 0.5
		# In RingCoords.FLAT_MODE (FlatMapRenderer.gd only) the mesh itself
		# is unrolled flat -- Vector3.UP is the correct normal there, not
		# this per-segment cylindrical one.
		var floor_normal := Vector3.UP if RingCoords.FLAT_MODE else Vector3(0, -cos(mid), -sin(mid))
		# Adaptive per-segment x-slicing instead of one flat quad spanning
		# the whole width: TerrainHeight.critical_x_values() returns this
		# segment's true feature breakpoints (river/lake/pond/creek/ditch
		# bed+bank edges, wherever they land this segment's meander has
		# shifted them to), guaranteeing the carved terrain is always
		# correctly resolved rather than risking a fixed grid straddling
		# (and nearly erasing) a feature between samples. Away from any
		# water feature this still returns just the two width extremes --
		# one quad, identical to the old unconditional single-quad floor.
		var xs: Array = TerrainHeight.critical_x_values(radius, segments, s0, s1, half_w)
		for k in range(xs.size() - 1):
			var xl: float = xs[k]
			var xr: float = xs[k + 1]
			var p0 := RingCoords.floor_point(radius, segments, s0, xl)
			var p1 := RingCoords.floor_point(radius, segments, s0, xr)
			var p2 := RingCoords.floor_point(radius, segments, s1, xr)
			var p3 := RingCoords.floor_point(radius, segments, s1, xl)
			var u0 := xl / TILE_FLOOR
			var u1 := xr / TILE_FLOOR
			var v0 := s0 / TILE_FLOOR
			var v1 := s1 / TILE_FLOOR
			_quad(st_floor, p0, p1, p2, p3, floor_normal,
				Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v1))
	st_floor.set_material(floor_material)
	st_floor.commit(mesh)

## Builds the ring's mesh (3 surfaces -- floor/ceiling/wall, one material
## each) and a matching trimesh collision shape, as new children of
## `ring_body`. `radius` is the floor's distance from the spin axis;
## `ceiling_height` is floor-to-ceiling (so ceiling sits at
## radius - ceiling_height); `width` is the full wall-to-wall span along
## the spin axis (local X).
static func build(ring_body: Node3D, radius: float, ceiling_height: float,
		width: float, segments: int,
		floor_material: Material, wall_material: Material, ceiling_material: Material, with_floor := true) -> void:
	# TerrainHeight can't reference SpaceStation.WIDTH directly (that would
	# cycle: SpaceStation -> StationRingBuilder -> TerrainHeight -> back to
	# SpaceStation -- see TerrainHeight.gd's header) -- this one-way write
	# is how it learns the ring's width instead.
	TerrainHeight.RING_WIDTH = width
	var ceiling_radius := radius - ceiling_height
	var half_w := width / 2.0
	var mesh := ArrayMesh.new()

	if with_floor:              # the remake world streams its own terrain (MapTerrainMesh.gd)
		build_floor_surface(mesh, radius, segments, half_w, floor_material)

	var st_ceiling := SurfaceTool.new()
	st_ceiling.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(segments):
		var a0 := (TAU / segments) * i
		var a1 := (TAU / segments) * (i + 1)
		var p0 := Vector3(-half_w, ceiling_radius * cos(a0), ceiling_radius * sin(a0))
		var p1 := Vector3(half_w, ceiling_radius * cos(a0), ceiling_radius * sin(a0))
		var p2 := Vector3(half_w, ceiling_radius * cos(a1), ceiling_radius * sin(a1))
		var p3 := Vector3(-half_w, ceiling_radius * cos(a1), ceiling_radius * sin(a1))
		var mid := (a0 + a1) * 0.5
		var ceiling_normal := Vector3(0, cos(mid), sin(mid))  # points outward/down -- the visible underside
		var u0 := -half_w / TILE_CEILING
		var u1 := half_w / TILE_CEILING
		var v0 := (ceiling_radius * a0) / TILE_CEILING
		var v1 := (ceiling_radius * a1) / TILE_CEILING
		_quad(st_ceiling, p0, p1, p2, p3, ceiling_normal,
			Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v1))
	st_ceiling.set_material(ceiling_material)
	st_ceiling.commit(mesh)

	var st_wall := SurfaceTool.new()
	st_wall.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(segments):
		var a0 := (TAU / segments) * i
		var a1 := (TAU / segments) * (i + 1)
		for side: float in [-1.0, 1.0]:
			var x: float = half_w * side
			var pf0 := Vector3(x, radius * cos(a0), radius * sin(a0))
			var pf1 := Vector3(x, radius * cos(a1), radius * sin(a1))
			var pc1 := Vector3(x, ceiling_radius * cos(a1), ceiling_radius * sin(a1))
			var pc0 := Vector3(x, ceiling_radius * cos(a0), ceiling_radius * sin(a0))
			var wall_normal := Vector3(-side, 0, 0)  # points inward, toward the tube's interior
			var u0 := (radius * a0) / TILE_WALL
			var u1 := (radius * a1) / TILE_WALL
			var v0 := 0.0
			var v1 := ceiling_height / TILE_WALL
			_quad(st_wall, pf0, pf1, pc1, pc0, wall_normal,
				Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v1))
	st_wall.set_material(wall_material)
	st_wall.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "RingMesh"
	mesh_instance.mesh = mesh
	ring_body.add_child(mesh_instance)

	_add_collision_segments(ring_body, radius, ceiling_height, width, segments, with_floor)

## Floor collision: one thin convex prism per visual floor TRIANGLE --
## the exact same p0..p3 corners and (a,b,c)/(a,c,d) split build_floor_
## surface()/_quad() render, extruded FLOOR_COLLISION_DEPTH "down" (away
## from the axis). The top face IS the visible ground, so collision can't
## drift off it anywhere.
##
## History, so neither dead end gets retried: (1) a single
## ConcavePolygonShape3D trimesh of the floor passed ray queries but was
## never detected by the player's CharacterBody3D.move_and_slide() -- it
## fell straight through. (2) Flat BoxShape3D "staircase" slices, one per
## segment per x-slice, sat at the segment MIDPOINT's elevation and were
## centered ON the surface: ~0.5m high everywhere, and up to ~4m low
## wherever the terrain rose or fell along a ~33m segment (confirmed live
## at the spawn point, on the river bank at s=0). Convex prisms keep (2)'s
## reliability with move_and_slide() and (1)'s exact fit.
const FLOOR_COLLISION_DEPTH := 1.0

static func _add_floor_collision_slices(ring_body: Node3D, radius: float, segments: int,
		seg_index: int, half_w: float, _chord: float) -> void:
	var d_theta := TAU / segments
	var s0 := d_theta * seg_index * radius
	var s1 := d_theta * (seg_index + 1) * radius
	var down := -RingCoords.floor_basis(radius, segments, (s0 + s1) * 0.5).y * FLOOR_COLLISION_DEPTH
	var xs: Array = TerrainHeight.critical_x_values(radius, segments, s0, s1, half_w)
	for k in range(xs.size() - 1):
		var xl: float = xs[k]
		var xr: float = xs[k + 1]
		var p0 := RingCoords.floor_point(radius, segments, s0, xl)
		var p1 := RingCoords.floor_point(radius, segments, s0, xr)
		var p2 := RingCoords.floor_point(radius, segments, s1, xr)
		var p3 := RingCoords.floor_point(radius, segments, s1, xl)
		_add_prism(ring_body, p0, p1, p2, down)
		_add_prism(ring_body, p0, p2, p3, down)

static func _add_prism(ring_body: Node3D, a: Vector3, b: Vector3, c: Vector3, down: Vector3) -> void:
	var cs := CollisionShape3D.new()
	var shape := ConvexPolygonShape3D.new()
	shape.points = PackedVector3Array([a, b, c, a + down, b + down, c + down])
	cs.shape = shape
	ring_body.add_child(cs)

## Ceiling + wall collision as per-segment BoxShape3D pieces, plus the
## floor (see _add_floor_collision_slices() above). Same 96-segment
## granularity as the visual mesh; `margin` overlaps each box slightly
## along the chord direction so adjacent segments don't leave a seam gap.
static func _add_collision_segments(ring_body: Node3D, radius: float, ceiling_height: float,
		width: float, segments: int, with_floor := true) -> void:
	var ceiling_radius := radius - ceiling_height
	var half_w := width / 2.0
	var d_theta := TAU / segments
	var margin := 1.08

	for i in range(segments):
		var a0 := d_theta * i
		var a1 := d_theta * (i + 1)
		var mid := (a0 + a1) * 0.5
		var n_out := Vector3(0, cos(mid), sin(mid))
		var tangent := Vector3(0, -sin(mid), cos(mid))
		var chord: float = radius * d_theta * margin

		if with_floor:
			_add_floor_collision_slices(ring_body, radius, segments, i, half_w, chord)
		_add_box(ring_body, n_out * ceiling_radius, n_out, tangent, Vector3(width, 1.0, chord))

		var wall_center := n_out * ((radius + ceiling_radius) * 0.5)
		var wall_size := Vector3(1.0, ceiling_height + 1.0, chord)
		_add_box(ring_body, wall_center + Vector3(half_w, 0, 0), n_out, tangent, wall_size)
		_add_box(ring_body, wall_center + Vector3(-half_w, 0, 0), n_out, tangent, wall_size)

## `size` is expressed along the local axes (RIGHT, y_axis, z_axis) in
## that order -- e.g. for the floor, size.x is the wall-to-wall width
## (along world RIGHT), size.y the (thin) radial thickness, size.z the
## chord length along the loop.
static func _add_box(ring_body: Node3D, center: Vector3, y_axis: Vector3, z_axis: Vector3, size: Vector3) -> void:
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	cs.shape = box
	cs.transform = Transform3D(Basis(Vector3.RIGHT, y_axis, z_axis), center)
	ring_body.add_child(cs)

## Ceiling light fixtures: a small emissive strip mesh (reads as a lit
## panel, no real light source needed for most of them) every
## `light_every` segments, at 3 positions spread across the width; plus
## a real OmniLight3D at a subset of those (every `light_every * 4`
## segments) for actual illumination -- kept sparse on purpose at this
## scale so the light count stays reasonable.
static func add_light_fixtures(ring_body: Node3D, radius: float, ceiling_height: float,
		width: float, segments: int, light_every: int) -> void:
	var ceiling_radius := radius - ceiling_height
	var fixture_mat := StandardMaterial3D.new()
	fixture_mat.emission_enabled = true
	fixture_mat.emission = Color(1.0, 0.95, 0.85)
	fixture_mat.emission_energy_multiplier = 4.0
	fixture_mat.albedo_color = Color(1.0, 0.97, 0.9)

	var strip_length: float = (TAU / segments) * radius * 0.7
	var fixture_positions := [-width * 0.3, 0.0, width * 0.3]

	var i := 0
	while i < segments:
		var a := (TAU / segments) * (i + 0.5)
		var n_out := Vector3(0, cos(a), sin(a))
		var tangent := Vector3(0, -sin(a), cos(a))
		var base := n_out * ceiling_radius
		var basis := Basis(tangent, n_out, tangent.cross(n_out)).orthonormalized()

		for fx in fixture_positions:
			var mesh_inst := MeshInstance3D.new()
			var plane := PlaneMesh.new()
			plane.size = Vector2(strip_length, 5.0)
			plane.material = fixture_mat
			mesh_inst.mesh = plane
			mesh_inst.transform = Transform3D(basis, base + Vector3(fx, 0, 0) - n_out * 0.05)
			ring_body.add_child(mesh_inst)

		if i % (light_every * 4) == 0:
			var light := OmniLight3D.new()
			light.light_energy = 3.0
			light.omni_range = 90.0
			light.shadow_enabled = false
			light.position = base - n_out * 1.5
			ring_body.add_child(light)

		i += light_every

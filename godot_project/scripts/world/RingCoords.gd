extends Node
class_name RingCoords

# Foundational placement utility for anything built on the station ring's
# floor (see StationRingBuilder.gd for the geometry these functions must
# match exactly, and SpaceStation.gd for RADIUS/SEGMENTS). The floor is a
# flat-chord polygon, not a smooth cylinder -- one flat quad per segment,
# corners exactly on the true circle of radius `radius`, everything
# between those corners linearly interpolated (bilinear across the quad,
# so along a fixed axial position it's a straight lerp between the two
# corner points). A naive `radius * cos(theta), radius * sin(theta)`
# formula would place points slightly OUTSIDE the actual built floor
# (the true circle bulges past the chord except exactly at segment
# corners) -- everything here instead lerps along the real flat quad, the
# same math StationRingBuilder.build()'s own floor loop already does.
#
# `s` throughout is arc length along the true circle (s = radius * theta,
# theta measured from +Y sweeping toward +Z, matching StationRingBuilder's
# own convention) -- a convenient, continuous scalar for "how far around
# the loop," not literal distance walked along the faceted floor (those
# differ by a negligible amount at this segment count). `x` is the axial
# position (local X, the ring's width direction, unaffected by which
# segment `s` falls in).

## Which segment index `s` falls in, after wrapping into [0, TAU*radius).
static func _segment_index(segments: int, theta: float) -> int:
	var d_theta := TAU / segments
	var i := int(floor(theta / d_theta))
	return mini(i, segments - 1)  # guards float rounding exactly at the TAU wrap edge

## A point on the floor's actual flat quad at arc length `s`, axial
## position `x`. Matches StationRingBuilder.build()'s floor corners
## exactly at segment boundaries, and lerps between them elsewhere (the
## real, flat, built surface -- not the idealized circle) -- then, if
## TerrainHeight carves anything here (river/lake/pond/creek/ditch),
## recesses the point radially outward (away from the spin axis) by
## that depth. Every existing caller (streets, buildings, the player,
## water) gets terrain-aware placement for free through this one
## function, and is completely unaffected wherever nothing is carved.
static func floor_point(radius: float, segments: int, s: float, x: float) -> Vector3:
	var d_theta := TAU / segments
	var theta := fposmod(s / radius, TAU)
	var i := _segment_index(segments, theta)
	var a0 := d_theta * i
	var a1 := d_theta * (i + 1)
	var t := (theta - a0) / d_theta
	var p0 := Vector3(x, radius * cos(a0), radius * sin(a0))
	var p1 := Vector3(x, radius * cos(a1), radius * sin(a1))
	var p := p0.lerp(p1, t)
	var depth := TerrainHeight.depth_at(radius, segments, theta * radius, x)
	if depth > 0.0:
		var mid := (a0 + a1) * 0.5
		var up := Vector3(0, -cos(mid), -sin(mid))
		p -= up * depth
	return p

## The (right/axial, up/radial-inward, forward/tangential) basis at arc
## length `s` -- constant across a whole segment (the quad is flat, so
## its normal doesn't vary within it), taken at the segment's own
## midpoint angle, exactly matching the normal StationRingBuilder.build()
## assigns to that same quad. "up" points toward the spin axis (inward,
## matching StationPlayer's up_direction convention); "forward" is the
## direction of increasing s.
static func floor_basis(radius: float, segments: int, s: float) -> Basis:
	var d_theta := TAU / segments
	var theta := fposmod(s / radius, TAU)
	var i := _segment_index(segments, theta)
	var a0 := d_theta * i
	var a1 := d_theta * (i + 1)
	var mid := (a0 + a1) * 0.5
	var up := Vector3(0, -cos(mid), -sin(mid))
	var tangent := Vector3(0, -sin(mid), cos(mid))
	return Basis(Vector3.RIGHT, up, -tangent)  # x=right, y=up, -z=forward(=tangent)

## Sets `inst`'s global_transform to sit flush on the floor at (s, x),
## facing along the loop (increasing s), optionally yawed by `yaw`
## radians around the local up axis (e.g. to face a building across the
## street instead of along it). A full Basis, not a bare rotation.y --
## the flat-map placement shortcut (MapEditorUI.gd's pattern) only works
## where world "up" is constant, which isn't true here.
static func place_on_ring(inst: Node3D, radius: float, segments: int, s: float, x: float, yaw: float = 0.0) -> void:
	var basis := floor_basis(radius, segments, s)
	if yaw != 0.0:
		basis = basis.rotated(basis.y, yaw)
	inst.global_transform = Transform3D(basis, floor_point(radius, segments, s, x))

## Yields one process frame -- the time-slicing primitive ZoneStreamer.gd's
## background zone-detail loading uses (FarmGenerator/DowntownGenerator/
## ResidentialGenerator/CropFieldGenerator/StreetFurniture's build_detail_
## async() functions `await` this every few placements) so a zone
## streaming in spreads its work across many frames instead of blocking
## one frame for the whole thing -- a farm zone's ~2500 crop stalks +
## building collision generation measured at ~460ms in one synchronous
## call during Phase D/E testing, a real stutter if done all at once.
## `get_tree()` isn't available here (these are plain `static func`s on
## classes nothing ever instantiates) -- Engine.get_main_loop() is the
## instance-free way to reach the same SceneTree.
static func yield_frame() -> void:
	await (Engine.get_main_loop() as SceneTree).process_frame

## Inverse of floor_point()/floor_basis()'s own math: given a world
## position (station-local, since RingBody never moves -- see
## SpaceStation.gd), returns its arc length `s` around the loop. Matches
## StationPlayer._radial_vector()'s own convention (project the axis/X
## component out, leaving a vector in the Y/Z plane) -- ZoneStreamer.gd
## uses this every ~check interval to know which zone(s) the player is
## near, so it has to agree with how the player's own position is
## already interpreted elsewhere in this project, not invent a second
## convention.
static func s_from_position(radius: float, pos: Vector3) -> float:
	var theta := atan2(pos.z, pos.y)
	return fposmod(theta, TAU) * radius

## Recursively adds real (trimesh) collision to every MeshInstance3D
## under `root` that doesn't already have a StaticBody3D sibling --
## confirmed live that a plain `blender_scripts/`-built .glb (no
## dedicated export pipeline generating the "-col"-suffix/StaticBody3D
## setup godot_project/assets/editor_assets/house1.glb's own asset
## already carries, from a lost export script -- see
## scripts/world/SceneryOptimizer.gd's file comment) imports as visual-
## only: a player teleported into one fell straight through every wall,
## zero collision response. MeshInstance3D.create_trimesh_collision() is
## the standard, reliable Godot API for this rather than fighting
## Blender-export naming conventions further. Static-only -- confirmed
## elsewhere in this project (StationRingBuilder.gd's own file comment)
## that a concave trimesh shape collides from only one side on a MOVING/
## rotating body; nothing this is used for moves after being placed, so
## that failure mode doesn't apply here.
static func add_trimesh_collision(root: Node3D) -> void:
	# Collect first, mutate after -- create_trimesh_collision()
	# reparents its MeshInstance3D under a new StaticBody3D, which would
	# corrupt an in-progress tree walk if done during the walk itself.
	var targets: Array = []
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var parent := n.get_parent()
			var has_collision_sibling := false
			if parent:
				for sib in parent.get_children():
					if sib is StaticBody3D:
						has_collision_sibling = true
						break
			if not has_collision_sibling:
				targets.append(n)
		for c in n.get_children():
			stack.append(c)
	for mi in targets:
		(mi as MeshInstance3D).create_trimesh_collision()

## Renames every MeshInstance3D under `root` to include "_structure" in
## its OWN name if it doesn't already -- DistanceCulling.gd's
## HOUSE_KEYWORDS match matches against the GeometryInstance3D node's own
## name, not any ancestor's. Confirmed live that this is the PRE-
## EXISTING convention, not a new one invented here: house1.glb's own
## renderable mesh (from the original, lost export pipeline) is already
## named "house1_94_structure" -- baked into the mesh itself, not just a
## wrapper Node3D -- which is exactly why DistanceCulling's plain
## substring match already worked for those without any code here.
## building_helpers.py's new pipeline (farm/downtown buildings) instead
## keeps each mesh's plain Blender object name ("barn", "storefront_
## bank", ...) and only the WRAPPER Node3D gets "_structure" appended
## (FarmGenerator._place_building()/DowntownGenerator._place_one(), for
## OcclusionSetup's box-occluder host) -- so those buildings got zero
## distance culling until callers also run this on their instantiated
## scene. Idempotent: a mesh that already contains "_structure"
## (residential's house1/2/3) is left alone.
static func tag_structure_meshes(root: Node3D) -> void:
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D and n.name.find("_structure") == -1:
			n.name = n.name + "_structure"
		for c in n.get_children():
			stack.append(c)

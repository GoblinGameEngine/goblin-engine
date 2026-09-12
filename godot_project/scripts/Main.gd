extends Node3D

# Level bootstrap: bakes the navigation mesh over the neighborhood's
# collision geometry (so NPCs can path), then populates background
# civilians -- one per house, standing in its front yard (from
# data/map_layout.json, written by build_neighborhood.py) -- so every
# house reads as inhabited instead of scattering NPCs randomly across
# the map.
#
# Doors and windows are lightweight Godot-side sprite scenes now (see
# OpeningsSetup.gd), placed at the positions build_neighborhood.py records
# in map_layout.json's "openings" list -- not Blender geometry at all.
# Windows are purely decorative (no collision, no script, cheap in bulk);
# doors are real StaticBody3D instances with their own open/closed state
# (Door.gd). This replaced an EARLIER version of this replacement (doors/
# windows as real per-instance leaf/frame Blender objects, each wrapped in
# an Openable StaticBody3D) that was removed entirely for performance --
# 208 individual interactable objects was real per-object runtime cost
# that MultiMesh-batching the visuals never touched. The current design
# keeps that win for windows (no per-instance script/state at all) while
# only paying the individual-object cost for the doors that actually need
# to open (see reference/memory.txt).

const LAYOUT_PATH := "res://data/map_layout.json"
const FRONT_YARD_OFFSET := 2.5  # meters out from the house, toward the street
const WANDERING_CIVILIAN_COUNT := 20  # every house gets one, topped up to this total

const VEHICLE_SCENE_PATHS := {
	"car": "res://scenes/VehicleCar.tscn",
	"pickup": "res://scenes/VehiclePickup.tscn",
	"minivan": "res://scenes/VehicleMinivan.tscn",
}

@onready var nav_region: NavigationRegion3D = $NavRegion
@onready var neighborhood: Node3D = $NavRegion/Neighborhood

func _ready() -> void:
	var opt := SceneryOptimizer.optimize(neighborhood)
	print("Main: scenery optimize -- %d decorative meshes, collapsed %d into %d MultiMeshInstance3D" %
		[opt["decor_total"], opt["collapsed"], opt["multimeshes"]])

	var spawned_vehicles := _spawn_vehicles()
	print("Main: spawned %d vehicles" % spawned_vehicles)

	var occluded := OcclusionSetup.setup(neighborhood)
	print("Main: occlusion culling -- box occluder added to %d houses" % occluded)

	var lake_ok := LakeSetup.setup(neighborhood)
	print("Main: Summit Lake water animation attached: %s" % lake_ok)

	# Doors are real StaticBody3D obstacles, closed by default -- unlike
	# the old bare-hole interior openings, they need to be kept OFF the
	# nav-mesh bake's geometry layer (below), or a closed door reads as a
	# solid wall filling its own doorway. Placed here, before the bake,
	# same as everything else -- ordering doesn't matter for this
	# specifically (the layer mask handles it regardless of timing), but
	# does for MapEditorUI placements just below.
	var opened := OpeningsSetup.setup(neighborhood, _load_openings())
	print("Main: placed %d doors, %d windows" % [opened["doors"], opened["windows"]])

	# Anything placed with the in-game map editor (F2) -- loaded and
	# spawned BEFORE the navigation mesh bakes below, same as everything
	# else here, so a user-placed house/fence's collision is accounted
	# for by NPC pathfinding too, not just physically solid.
	var placed := MapEditorUI.spawn_saved_placements(neighborhood)
	print("Main: spawned %d saved map-editor placements" % placed)

	# Cel shading -- 3D world geometry only (houses, terrain, streets,
	# scenery, doors/windows -- everything under `neighborhood` by this
	# point). Deliberately NOT applied to NPCs (sprite-based already, so
	# never touched by this regardless -- it only walks MeshInstance3D/
	# MultiMeshInstance3D) or the player (weapon view -- staying plain PBR
	# for now, see ToonShading.gd). Placed here, after every last thing
	# that adds children to `neighborhood` (doors/windows, saved map-
	# editor placements) and before the nav-mesh bake, which doesn't care
	# about materials at all.
	var toon_count := ToonShading.apply_to_world(neighborhood)
	print("Main: cel-shaded %d materials" % toon_count)

	# Distance culling -- same "neighborhood, fully populated" timing as
	# cel shading just above (order between the two doesn't matter, they
	# touch different properties on the same nodes). See
	# DistanceCulling.gd for the actual tiers/reasoning.
	var culled := DistanceCulling.apply_to_world(neighborhood)
	print("Main: distance culling -- %d small props, %d trees, %d houses" %
		[culled["small"], culled["tree"], culled["house"]])

	# Screen-space outline pass (shaders/screen_outline.gdshader,
	# ScreenOutline.gd) -- replaces the old per-object inverted-hull
	# outline entirely (ToonShading.apply_to_world() above now only does
	# banded lighting, no outline material/next_pass of its own). See the
	# shader's own comment for why: a world-space vertex offset gets
	# disproportionately thick the closer the camera gets, no matter how
	# well it's tuned per object shape -- a screen-space pass sidesteps
	# that by construction, since its width is in screen pixels. Attached
	# once, here, to the player's own camera.
	var player := get_tree().get_first_node_in_group("player")
	if player:
		var player_cam: Camera3D = player.get_node_or_null("Head/Camera3D")
		if player_cam:
			ScreenOutline.attach_to_camera(player_cam)
		else:
			push_warning("Main: player has no Head/Camera3D -- no screen outline attached")

	var nav_mesh := NavigationMesh.new()
	nav_mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	# Layer 1 only -- excludes doors (collision_layer 16, see Door.tscn/
	# InteriorDoor.tscn) from the bake's source geometry entirely, so a
	# closed door never reads as a wall filling its own doorway. The
	# door itself still physically blocks the PLAYER (their collision_mask
	# includes layer 16, see Player.tscn) until opened. Background NPCs
	# don't collide with doors at all -- they have no door-opening
	# behavior, so making them collide with a door they can never open
	# would just strand them; they harmlessly clip through a shut
	# interior door instead, matching what the navmesh already assumes.
	nav_mesh.geometry_collision_mask = 1
	# 0.37, not the previous 0.4 -- just above NPCBase's own real capsule
	# radius (0.35, see NPCBase.tscn). Finer cell_size/cell_height too
	# (default is 0.25, coarse relative to this map's sub-meter walls,
	# doorways, and stairs).
	#
	# REAL BUG found live, and the reason both of these changed: Recast's
	# erosion needs a genuinely clear ~2*agent_radius before it will
	# produce ANY walkable polygon at all (see HALL_W's own comment in
	# build_neighborhood.py for this exact lesson, learned once already
	# for hallway widths) -- but that erosion is computed in whole VOXEL
	# CELLS, not the raw float radius (the engine's own "agent_radius is
	# ceiled to cell_size voxel units" warning is telling you this
	# directly), so the EFFECTIVE erosion for a given doorway depends on
	# where it happens to land on the fixed voxel grid, not just its
	# width in meters. Confirmed live: a kitchen/bathroom doorway came
	# back from NavigationServer3D.map_get_path() as completely
	# disconnected (both path ends collapsed onto the SAME point) at
	# 0.85m, while an identically-sized bathroom/stairwell doorway in the
	# SAME house connected fine -- ruled out the door itself first
	# (moving doors off this geometry layer, above, didn't fix it alone),
	# then confirmed the real cause with an isolated two-room test scene
	# (scratchpad/test_doorway_navmesh.gd) sweeping gap widths at these
	# exact settings: 0.85m and 0.90m both failed to connect, 1.0m
	# connected reliably regardless of grid position. Interior doorways
	# are now 1.0m wide too (see INT_DOOR_W) rather than a more realistic
	# but voxel-fragile ~0.85m; the finer cell_size here reduces (if it
	# doesn't fully eliminate) this same grid-alignment sensitivity
	# elsewhere on the map.
	nav_mesh.agent_radius = 0.37
	nav_mesh.agent_height = 1.8
	nav_mesh.agent_max_climb = 0.4
	nav_mesh.cell_size = 0.1
	nav_mesh.cell_height = 0.1
	nav_region.navigation_mesh = nav_mesh
	nav_region.bake_finished.connect(_on_nav_baked)
	nav_region.bake_navigation_mesh()

func _on_nav_baked() -> void:
	var points := _load_house_front_yard_points()
	if points.is_empty():
		push_warning("Main: map_layout.json missing/empty, no background NPCs spawned")
		return
	var spawn_points := _top_up_points(points, WANDERING_CIVILIAN_COUNT)
	NPCDirector.populate_at_points(self, spawn_points, "civilian")
	print("Main: nav mesh baked, spawned %d background NPCs (one per house + topped up to %d)" %
		[spawn_points.size(), WANDERING_CIVILIAN_COUNT])
	# The navigation map needs a moment after bake_finished before queries
	# against it (map_get_closest_point/map_get_path) actually see the new
	# polygons -- calling map_get_closest_point() immediately here returned
	# (0,0,0) every time; a short wait first fixed it.
	await get_tree().create_timer(0.2).timeout
	var links := _setup_stair_links()
	print("Main: added %d stairwell nav links (2-story houses)" % links)

## Offsets (metres, along the stairwell's own run axis, both directions)
## tried when looking for a link endpoint that is actually PART OF the
## main connected floor, rather than blindly trusting the single closest
## point to the stairwell's geometric center. See _snap_reachable() for
## why this sweep exists -- naively snapping right at the stairwell
## center repeatedly landed on tiny, real-but-disconnected navmesh slivers
## (a landing/threshold sliver Recast makes right at the stair opening
## that isn't actually joined to the rest of that floor's polygons).
const _STAIR_SNAP_OFFSETS := [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, -0.6, -1.2, -1.8, -2.4, -3.0]

## Snaps `candidate` onto the navmesh and only accepts it if a real path
## search confirms it's walkable-to from `ref_point` (a point already
## known to sit on the floor's main connected navmesh) and that the
## search actually ARRIVES there rather than giving up early. Diagnostic
## sweeps over real houses showed the raw candidate point itself often
## sits 0.8-1.3m from the nearest polygon (candidates land inside/near
## the stairwell hole or the stair steps' own collision, which is real
## empty-navmesh space, not a bug) while still being a perfectly good,
## reachable point once snapped -- so unlike an earlier version of this
## function, the raw candidate-to-snap distance is checked generously
## (just enough to rule out snapping clear across the map) and the real
## acceptance test is the path actually reaching the snapped point.
func _snap_reachable(map_rid: RID, candidate: Vector3, ref_point: Vector3):
	var snapped: Vector3 = NavigationServer3D.map_get_closest_point(map_rid, candidate)
	if snapped.distance_to(candidate) > 2.5:
		return null
	var path := NavigationServer3D.map_get_path(map_rid, ref_point, snapped, true)
	if path.is_empty() or path[-1].distance_to(snapped) > 0.6:
		return null
	return snapped

## Recast's automatic voxelization reliably refuses to connect a stairwell
## on its own, no matter the geometry (tried a smooth ramp sized exactly to
## the true diagonal, thicker ramps, real discrete steps, finer cell_size/
## cell_height, generous agent_max_slope, region_min_size/ledge-span
## tuning, tiny agent_radius, waiting longer after bake_finished -- all
## verified directly with NavigationServer3D.map_get_path() to a real
## point on a real house's 2nd floor, all came back stuck at ground level)
## -- confirmed the two floors' navmesh regions genuinely exist (a
## map_get_closest_point() query DID find a polygon right at 2nd-floor
## height) but Recast just won't auto-bridge them across a stairwell this
## steep/narrow. NavigationLink3D is Godot's actual supported tool for
## exactly this ("connect two navmesh areas that automatic baking can't
## bridge on its own" -- elevators are the other classic example) --
## confirmed first in total isolation (a tiny two-box test scene, deleted
## after) before wiring it into the real map. One link per 2-story house,
## from the base of its stairwell to the top, anchored at the exact WORLD
## stairwell position build_neighborhood.py computes and exports per house
## (h["stair_x"]/h["stair_y"], Blender-space -- see _slim() there) rather
## than re-deriving it here, since the old re-derivation (from split_x/
## split_y, a per-PLAN value reused by many physical houses) was a real
## source of bugs on the Python side once the floor plan stopped being
## symmetric (see reference/memory.txt's floor-plan rewrite writeup).
##
## A first version snapped each endpoint straight to the single closest
## navmesh point at that (x,z,height) and created the link from there --
## it registered fine (confirmed via map_get_links()) but pathfinding
## still got stuck at ground level. Direct path tests isolated why: BOTH
## endpoints were snapping onto small disconnected navmesh slivers right
## at the stairwell opening (islands Recast forms at a stair threshold
## that never get merged into the room's main floor polygon), so the link
## itself worked but nothing could ever walk to either end of it. Fixed
## by sweeping candidate points along the stairwell's own run axis and
## only accepting one that a real path-search confirms is reachable from
## a point already known to be on the main floor (the house's own front
## yard spawn point for the ground end; the house's own footprint center
## at 2nd-floor height for the upper end -- both far enough from the
## stairwell opening itself to reliably land on the main slab).
func _setup_stair_links() -> int:
	if not FileAccess.file_exists(LAYOUT_PATH):
		return 0
	var f := FileAccess.open(LAYOUT_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("rows"):
		return 0
	var map_rid := get_world_3d().get_navigation_map()
	var count := 0
	for row_name in data["rows"].keys():
		for h in data["rows"][row_name]:
			if int(h.get("stories", 1)) != 2:
				continue
			var bx: float = h["x"]
			var by: float = h["y"]
			var rot: float = h["rot"]
			var wall_h: float = h["wall_h"]
			# stair_x/stair_y are already WORLD Blender-space (see
			# build_neighborhood.py's _slim()) -- just the standard
			# Blender-(x,y) -> Godot-(x,-y) mapping used everywhere else
			# in this file, no rotation math needed here at all.
			var gx: float = h["stair_x"]
			var gz: float = -h["stair_y"]
			# World-space direction of the stairwell's local Y axis (its
			# run direction), still needed for the snap-point sweep below.
			var run_x := -sin(rot)
			var run_z := -cos(rot)

			# The ground-floor reference needs to be somewhere ALREADY
			# proven reachable -- a first version used the front-yard NPC
			# spawn point (only 2.5m out from the house's own center),
			# which is still INSIDE the house for this floor plan (rooms
			# comfortably exceed that in every direction), so it carried no
			# actual guarantee. Pushed further out (well past any house's
			# half-depth) along the same front-facing direction so it's
			# unambiguously on the street/sidewalk -- the one part of the
			# navmesh already known-good (NPCs already wander it).
			var ground_ref := _house_front_yard_point(bx, by, rot) + Vector3(sin(rot), 0, cos(rot)) * 8.0
			# upper_ref_x/y (see build_neighborhood.py's build_house()) is a
			# point solidly inside the 2nd floor's front bedroom, exported
			# rather than computed here -- a first version used the house's
			# plain (x,y) center at upper-floor height, which sits right
			# next to the bedroom-splitting partition wall for many houses
			# (that wall's position is a small random offset from center),
			# and was snapping onto the ROOF surface a meter-plus higher up
			# instead of the actual floor, since no floor polygon existed
			# close enough to the query point right at that wall.
			var upper_ref := Vector3(h["upper_ref_x"], wall_h + 0.15, -h["upper_ref_y"])

			var p0 = null
			for t in _STAIR_SNAP_OFFSETS:
				p0 = _snap_reachable(map_rid, Vector3(gx + run_x * t, 0.15, gz + run_z * t), ground_ref)
				if p0 != null:
					break
			if p0 == null:
				p0 = NavigationServer3D.map_get_closest_point(map_rid, Vector3(gx, 0.15, gz))
				push_warning("Main: stair link ground-floor snap for house at (%.1f,%.1f) found no confirmed-reachable point, using unvalidated fallback" % [bx, by])

			var p1 = null
			for t in _STAIR_SNAP_OFFSETS:
				p1 = _snap_reachable(map_rid, Vector3(gx + run_x * t, wall_h + 0.15, gz + run_z * t), upper_ref)
				if p1 != null:
					break
			if p1 == null:
				p1 = NavigationServer3D.map_get_closest_point(map_rid, Vector3(gx, wall_h + 0.15, gz))
				push_warning("Main: stair link upper-floor snap for house at (%.1f,%.1f) found no confirmed-reachable point, using unvalidated fallback" % [bx, by])

			var link := NavigationLink3D.new()
			link.start_position = p0
			link.end_position = p1
			link.bidirectional = true
			nav_region.add_child(link)
			NavigationServer3D.link_set_map(link.get_rid(), map_rid)  # force the same map, in case a dynamically-created link defaults elsewhere
			count += 1
	return count

## Keeps "every house inhabited" (the original `points`, one per front
## yard) but pads the list out to `target` total by reusing house points
## with a small random jitter, so there's still a wandering NPC at every
## house AND the total wandering-civilian count matches `target` even
## though the map only has 15 houses.
func _top_up_points(points: Array, target: int) -> Array:
	var result := points.duplicate()
	var i := 0
	while result.size() < target:
		var base: Vector3 = points[i % points.size()]
		var jitter := Vector3(randf_range(-3.0, 3.0), 0.0, randf_range(-3.0, 3.0))
		result.append(base + jitter)
		i += 1
	return result

## Same front-yard offset formula _load_house_front_yard_points() uses,
## factored out so _setup_stair_links() can use one as a "definitely
## reachable" ground-floor reference point per house.
func _house_front_yard_point(bx: float, by: float, rot: float) -> Vector3:
	var front_x := sin(rot)
	var front_y := -cos(rot)
	var spawn_bx := bx + front_x * FRONT_YARD_OFFSET
	var spawn_by := by + front_y * FRONT_YARD_OFFSET
	return Vector3(spawn_bx, 0.2, -spawn_by)

## Reads the "openings" list from map_layout.json (see
## build_neighborhood.py's ALL_OPENINGS/register_opening()) -- one dict
## per door/window, already carrying everything OpeningsSetup.gd needs
## (world position, hinge point, rotation, width/height) so no geometry
## re-derivation happens on this side at all.
func _load_openings() -> Array:
	if not FileAccess.file_exists(LAYOUT_PATH):
		return []
	var f := FileAccess.open(LAYOUT_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("openings"):
		return []
	return data["openings"]

## Reads every house's (x, y, rot) from map_layout.json and returns one
## Godot-space Vector3 per house, offset toward the street from the front
## door -- see build_neighborhood.py's place_row_horizontal/vertical for
## the rot convention this front-direction formula matches (verified
## against the same rot values that orient the houses themselves).
func _load_house_front_yard_points() -> Array:
	var points: Array = []
	if not FileAccess.file_exists(LAYOUT_PATH):
		return points
	var f := FileAccess.open(LAYOUT_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("rows"):
		push_error("Main: malformed %s" % LAYOUT_PATH)
		return points
	for row_name in data["rows"].keys():
		for house in data["rows"][row_name]:
			var bx: float = house["x"]
			var by: float = house["y"]
			var rot: float = house["rot"]
			points.append(_house_front_yard_point(bx, by, rot))
	return points

## Reads the "vehicles" list from map_layout.json (see build_neighborhood.py's
## compute_new_vehicle_placements()) and instantiates one of the 3 hand-
## modeled Vehicle{Car,Pickup,Minivan}.tscn scenes per entry. Position maps
## Blender-space (x, y) -> Godot-space (x, -y) same as everywhere else in
## this project; rotation.y uses facing_deg directly in radians -- every
## vehicle asset's local -X is its front, and for a -X-front object the
## Blender Z-rotation angle IS the matching Godot Y-rotation angle (verified
## algebraically: both axis conventions agree once the Blender-Z-up ->
## Godot-Y-up glTF conversion is accounted for, since that conversion never
## touches the shared X axis).
func _spawn_vehicles() -> int:
	if not FileAccess.file_exists(LAYOUT_PATH):
		return 0
	var f := FileAccess.open(LAYOUT_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("vehicles"):
		return 0
	var count := 0
	for veh in data["vehicles"]:
		var kind: String = veh["kind"]
		var scene_path: String = VEHICLE_SCENE_PATHS.get(kind, "")
		if scene_path == "" or not ResourceLoader.exists(scene_path):
			push_warning("Main: no vehicle scene for kind '%s' (%s) -- skipped" % [kind, scene_path])
			continue
		var scene: PackedScene = load(scene_path)
		var inst: Node3D = scene.instantiate()
		var bx: float = veh["x"]
		var by: float = veh["y"]
		var facing_deg: float = veh["facing_deg"]
		inst.position = Vector3(bx, 0.0, -by)
		inst.rotation.y = deg_to_rad(facing_deg)
		add_child(inst)
		ToonShading.apply_to_world(inst)
		count += 1
	return count

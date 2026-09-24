extends RefCounted
class_name RemakeWorld

## Places the remake's built structures (godot_project/remake/placement.json, from
## remake/tools/placement.py) on the ring floor.
##
## Each structure stands at its map position (s, x), turned by its yaw about the floor's up so
## its front faces its street (StationGeo convention), on its pad -- MapTerrain levels its lot to
## the graded ground at its front edge -- or, for a crossing, at its deck height, which the roads
## ramp to.  Its foundations reach 4 m down.  Drawing goes through
## RemakeLodClusters (full detail near, LOD1, LOD2/LOD3 merged per cell beyond).
##
## build(root, settlements) -- a coroutine (a building per frame); settlements: names to place (the inventory's),
## or [] for everything; farmsteads and crossings are included when their name is listed as
## "farms" / "crossings" (or when placing everything).


static func build(root: Node3D, settlements: Array) -> Dictionary:
	var pl: Array = JSON.parse_string(FileAccess.get_file_as_string("res://remake/placement.json")).structures
	var entries := []
	for e in pl:
		var group: String = e.settlement if e.settlement != null else ("farms" if e.kind == "farm" else "crossings")
		if not settlements.is_empty() and not settlements.has(group):
			continue
		var s: float = e.s
		var x: float = e.x
		var yaw: float = e.yaw
		var basis := StationGeo.basis(s, yaw)
		# its pad (MapTerrain levels the lot to it) or, for a crossing, its deck (the roads ramp to it)
		var h := MapTerrain.pad_height(e.id)
		if is_nan(h):
			h = MapTerrain.elevation(s, x)
		entries.append(_entry(e, s, x, basis, h))
	var t0 := Time.get_ticks_msec()
	var info: Dictionary = await RemakeLodClusters.build(root, entries, false)      # full detail streams (RemakeDetailStreamer)
	info["ms"] = Time.get_ticks_msec() - t0
	return info


static func _entry(e: Dictionary, s: float, x: float, basis: Basis, h: float) -> Dictionary:
	var cell2 := RemakeLodClusters.CELL2
	var cell3 := RemakeLodClusters.CELL3
	return {"id": e.id, "xform": Transform3D(basis, StationGeo.point(s, x, h)),
		"key2": Vector2i(floori(s / cell2), floori(x / cell2)),
		"key3": Vector2i(floori(s / cell3), floori(x / cell3))}

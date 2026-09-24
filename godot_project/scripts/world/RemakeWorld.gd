extends RefCounted
class_name RemakeWorld

## Places the remake's built structures (godot_project/remake/placement.json, from
## remake/tools/placement.py) on the ring floor.
##
## Each structure stands at its map position (s, x), turned by its yaw about the floor's up so
## its front faces its street (StationGeo convention), at the HIGHEST ground under its massing
## footprint (fmin/fmax) -- its foundations reach 4 m down, so on a slope they meet the lower
## ground instead of the building floating or burying its ground floor.  Drawing goes through
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
		# the highest ground under the footprint: corners, edge midpoints and centre
		var h := -1e9
		var c := cos(yaw)
		var sn := sin(yaw)
		for lx in [e.fmin[0], (e.fmin[0] + e.fmax[0]) * 0.5, e.fmax[0]]:
			for lz in [e.fmin[1], (e.fmin[1] + e.fmax[1]) * 0.5, e.fmax[1]]:
				# local (lx, lz) -> map offsets: local +x turns to (x: cos, s: sin), local +z to (x: sin, s: -cos)
				var dx: float = lx * c + lz * sn
				var ds: float = lx * sn - lz * c
				h = maxf(h, MapTerrain.elevation(s + ds, x + dx))
		var pos := StationGeo.point(s, x, h)
		var cell2 := RemakeLodClusters.CELL2
		var cell3 := RemakeLodClusters.CELL3
		entries.append({"id": e.id, "xform": Transform3D(basis, pos),
			"key2": Vector2i(floori(s / cell2), floori(x / cell2)),
			"key3": Vector2i(floori(s / cell3), floori(x / cell3))})
	var t0 := Time.get_ticks_msec()
	var info: Dictionary = await RemakeLodClusters.build(root, entries, false)      # full detail streams (RemakeDetailStreamer)
	info["ms"] = Time.get_ticks_msec() - t0
	return info

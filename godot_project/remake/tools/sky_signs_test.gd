extends SceneTree
## Headless: build every island's SkySigns (no game), report time, counts, triangles.
##   godot4 --headless --path . --script res://remake/tools/sky_signs_test.gd

func _init() -> void:
	var lay: Dictionary = JSON.parse_string(DataFile.text("res://remake/sky/islands.json"))
	var can: Dictionary = JSON.parse_string(DataFile.text("res://remake/bible/sky_islands.json"))
	var by_id := {}
	for c in can.islands:
		by_id[c.id] = c
	if OS.get_environment("STYLES") != "":
		SkySigns.STYLES = OS.get_environment("STYLES")
	var sys := SkyIslands.new()
	sys.models = lay.get("models", {})
	var tot := {}
	var worst_ms := 0.0
	var worst_tris := 0
	var sum_ms := 0.0
	var ids: Array = lay.islands
	for i in ids.size():
		var isl := SkyIsland.new()
		var cn: Dictionary = by_id.get(ids[i].id, {}).duplicate()
		if OS.get_environment("STYLE") != "" and i < 3:
			cn["style"] = OS.get_environment("STYLE")
		isl.setup(sys, i, ids[i], cn)
		var s := SkySigns.new()
		s.setup(isl)
		var t0 := Time.get_ticks_usec()
		while not s._todo.is_empty():
			(s._todo.pop_front() as Callable).call()
		var ms := (Time.get_ticks_usec() - t0) / 1000.0
		sum_ms += ms
		worst_ms = maxf(worst_ms, ms)
		var tris := 0
		for c in s.get_children():
			if c is MeshInstance3D:
				var m: Mesh = (c as MeshInstance3D).mesh
				for si in m.get_surface_count():
					tris += (m.surface_get_arrays(si)[Mesh.ARRAY_VERTEX] as PackedVector3Array).size() / 3
		worst_tris = maxi(worst_tris, tris)
		for k in s.count:
			tot[k] = tot.get(k, 0) + s.count[k]
		if i < 3:
			print("%s: %.0f ms, %d tris, %s" % [ids[i].id, ms, tris, s.count])
		s.free()
		isl.free()
	print("all 100: %.0f ms total, worst %.0f ms, worst %d tris" % [sum_ms, worst_ms, worst_tris])
	print("totals: ", tot)
	quit()

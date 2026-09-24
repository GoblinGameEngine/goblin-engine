extends Node3D
## LOD stress test: N buildings (cycling through `ids`) on a grid, drawn either at full detail
## everywhere (mode=full) or through the distance chain (mode=lod: full -> lod1 -> lod2 -> lod3 by
## visibility range, the ranges scaled by each building's size).  Reports frame time, draw calls and
## primitives after it settles.
##   godot4 --path . res://remake/scenes/lod_perf.tscn -- ids=HF-037,B-004 n=700 spacing=45 mode=lod
##
## Switch distances for a ~10 m building; a building k times bigger switches k times farther.
const D1 := 60.0
const D2 := 200.0
const D3 := 600.0
const MARGIN := 0.08            # hysteresis at each switch, as a fraction of the distance

var report := {}


func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() == 2:
			args[kv[0]] = kv[1]
	var ids: PackedStringArray = String(args.get("ids", "HF-037")).split(",", false)
	var n := int(args.get("n", "700"))
	var spacing := float(args.get("spacing", "45"))
	var mode := String(args.get("mode", "lod"))
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 30, 0)
	sun.shadow_enabled = true
	add_child(sun)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.62, 0.68, 0.74)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.55, 0.58, 0.62)
	add_child(env)
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(spacing * 40, spacing * 40)
	ground.mesh = pm
	add_child(ground)
	var side := int(ceil(sqrt(n)))
	var scenes := {}
	for id in ids:
		scenes[id] = [load("res://remake/buildings/%s.glb" % id)]
		for l in [1, 2, 3]:
			scenes[id].append(load("res://remake/buildings/%s.lod%d.glb" % [id, l]))
	for i in n:
		var id: String = ids[i % ids.size()]
		var pos := Vector3((i % side - side / 2.0) * spacing, 0, (i / side - side / 2.0) * spacing)
		var root := Node3D.new()
		root.position = pos
		root.rotation.y = (i % 4) * PI / 2
		add_child(root)
		var full := RemakeBuilding.new()
		root.add_child(full)
		full.load_building(scenes[id][0])
		if mode != "lod":
			continue
		var k := clampf(_size(full) / 12.0, 0.7, 4.0)
		var d := [0.0, D1 * k, D2 * k, D3 * k, 0.0]
		_ranges(full, d[0], d[1])
		_light_fade(full, d[1])
		for l in [1, 2, 3]:
			var inst: Node3D = scenes[id][l].instantiate()
			root.add_child(inst)
			RemakeBuilding.prepare_lod(inst, "res://remake/buildings/%s.lod%d.glb" % [id, l])
			_ranges(inst, d[l], d[l + 1])
	var cam := Camera3D.new()
	cam.fov = 75.0
	cam.far = 4000.0
	add_child(cam)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	report = {"n": n, "mode": mode, "ids": ids.size()}
	# street level, then an overview that sees the whole grid (the ring's far side overhead)
	var views := {"street": [Vector3(3, 1.7, 3), Vector3(spacing * side, 1.7, spacing * side * 0.6)],
				  "overview": [Vector3(-spacing * side * 0.7, spacing * side * 0.35, -spacing * side * 0.7), Vector3.ZERO]}
	for v in views:
		cam.position = views[v][0]
		cam.look_at(views[v][1])
		await get_tree().create_timer(3.0).timeout
		var ft := []
		for f in 240:
			await get_tree().process_frame
			ft.append(get_process_delta_time() * 1000.0)
		ft.sort()
		report[v] = {"frame_ms_median": snappedf(ft[ft.size() / 2], 0.01), "frame_ms_p95": snappedf(ft[int(ft.size() * 0.95)], 0.01),
			"draw_calls": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
			"primitives": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),
			"objects": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)}
	report["video_mem_mb"] = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED) / 1048576
	print("LOD_PERF ", JSON.stringify(report))


func _size(n: Node) -> float:
	var box := AABB()
	var first := true
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is MeshInstance3D and str(c.name).ends_with("_visual"):
			var ab: AABB = (c as MeshInstance3D).get_aabb()
			box = ab if first else box.merge(ab)
			first = false
	return maxf(box.size.x, maxf(box.size.y, box.size.z))


func _ranges(n: Node, begin: float, end: float) -> void:
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			var g := c as GeometryInstance3D
			g.visibility_range_begin = begin
			g.visibility_range_begin_margin = begin * MARGIN
			g.visibility_range_end = end
			g.visibility_range_end_margin = end * MARGIN


func _light_fade(n: Node, end: float) -> void:
	# room lights out beyond the interior range (lit windows stand in later)
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is Light3D:
			var l := c as Light3D
			l.distance_fade_enabled = true
			l.distance_fade_begin = minf(40.0, end * 0.6)
			l.distance_fade_length = 10.0

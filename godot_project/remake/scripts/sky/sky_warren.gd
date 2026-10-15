extends RefCounted
class_name SkyWarren

## A sky island's city (research/sky_islands/warrens/: r4_design.md §5, format.md): one fused warren grown offline on a
## 3 m lattice (tools/sky/warren/) and stored as placements of SHARED kit pieces -- no per-island meshes.  Here the
## placements are merged into chunk meshes (8 x 8 cells, every level) on worker threads and drawn as RenderingServer
## instances, not scene nodes: an island moves every tick, and nodes on it cost per node per tick (the lesson of
## research/perf_learnings.md).  SkyIsland calls place() whenever it is placed.
##
##   LOD0  < LOD0_M     the pieces themselves, a surface per material slot (wall, trim, frame, glass, ...): the
##                      glass interior-mapped (window_glass.gdshader: a fake room, lit by the hour at night)
##   LOD1  .. LOD1_M    each piece as its bounding box (lod1 "box"), crowns kept ("keep"), clutter dropped: one surface,
##                      lod_vc.gdshader (lit window grid at night)
##   LOD2  .. near end  a quadrant of 4 x 4 chunks' LOD1 merged into one instance
## Colour: the placement's kit palette variant (pieces.json palettes[civ][variant][slot], FORMAT.md v2 "kit_variant")
## baked into the vertex colour of a per-(piece, variant, mirror) copy of the piece, then copied with the placement's
## transform (`xf * verts`, append_array: in C++, no per-vertex GDScript).
## Collision: the chunks within COLLIDE_M of the player, on the island's one body ("WarrenBody", shapes on the body).
## Lights (the json "lights" [x, y, z, kind, colour]): at night a glare sprite on the brightest and a pool of light on the
## ground under the street ones -- two MultiMeshes.

const DIR := "res://remake/sky/warrens/"
const PIECES := "res://remake/sky/warrens/pieces.json"
const CELL := 3.0
const STOREY := 3.2
const LOD0_M := 70.0                 # the pieces within (per civ: LOD0_CIV, or the twin json's "lod0_m")
## heavy civs draw full detail nearer: Kowloon averages ~44k triangles a chunk, ~1M within 87 m (r4: <= 700k near)
const LOD0_CIV := {"kowloon_walled": 40.0}
const LOD1_M := 220.0
const NEAR_END := 520.0              # (SkyIsland.NEAR + margin: past it the island's own LOD glbs draw)
const CH := 8                        # cells a chunk's side
const COLLIDE_M := 40.0
const COLLIDE_DROP := 55.0
const UPLOAD_USEC := 3000            # main-thread time a frame for uploads
const MAX_TASKS := 2                 # merges at once, an island
const MAX_TASKS_ALL := 3             # ... and all the near warrens together (48 islands have one: several build at once)
static var _tasks_all := 0
static var _up_frame := -1           # the frame whose upload budget _up_used counts (shared by every warren)
static var _up_used := 0
const FLARES := 300
const FLARE_M := 150.0
const POOLS := 700
const FLARE_SH := preload("res://remake/shaders/warren_flare.gdshader")
const POOL_SH := preload("res://remake/shaders/warren_pool.gdshader")
const POOL_M := 120.0
## the draw groups: every slot that is plain vertex colour on a rough surface shares one surface ("solid") -- a chunk
## draws in at most 5 calls, not one per slot
const MAT_OF := {"metal": "metal", "glass": "glass", "emissive": "emissive", "water": "water"}
## (accent, accent2: KIT's bright paint and gilt per family, 2026-10-15: plain vertex colour, the "solid" group)
const SLOTS := ["wall", "trim", "frame", "glass", "screen", "roof", "metal", "fabric", "emissive", "tile", "water",
	"ground", "plant", "accent", "accent2"]

static var _pieces := {}             # id -> {surfs: [[slot, arrays]], aabb, lod1, collide}
static var _pieces_loaded := false
static var _variants := {}           # "id|civ|variant|mirror" -> {slot: arrays} (the palette baked)
static var _box_variants := {}       # "id|wall colour" -> its bounding box (arrays)
static var _palettes := {}           # pieces.json palettes: civ -> [variant {slot: "#rrggbb"}]
static var _mats := {}               # slot -> Material
static var _lod_vc: Material
static var _vmutex := Mutex.new()

var isl: Node3D                      # SkyIsland
var id := ""
var head := {}
var side := {}                       # the readable side (<id>.json): travel, anchors, walk, lights
var chunks: Array = []               # {ci, cj, recs: PackedByteArray, n, centre, box: AABB, state, ...}
var groups := {}                     # Vector2i quadrant -> {chunks: [], inst, mesh, state}
var ready := false
var _decode_task := -1
var _prep_task := -1
var _tasks := {}                     # task id -> chunk
var _gtasks := {}                    # task id -> group key
var _queue: Array = []               # chunks waiting for a worker
var _results: Array = []             # [chunk, lod0 arrays per slot, lod1 arrays, faces] from workers
var _gresults: Array = []
var _rmutex := Mutex.new()
var _xf := Transform3D.IDENTITY
var _visible := true
var _body: StaticBody3D
var _flare_mm: MultiMeshInstance3D
var _pool_mm: MultiMeshInstance3D
var lod0_m := LOD0_M
var _col_t := 0.0
var _scenario: RID
var built := 0
var built_ms := -1                  # ms from start to the last chunk in
var merge_usec: Array = []          # each chunk's worker time
var _t_start := 0


static func has_file(island_id: String) -> bool:
	return FileAccess.file_exists(DIR + island_id + ".bin.gz")


func _init(p_isl: Node3D) -> void:
	isl = p_isl
	id = str(isl.data.id)
	_scenario = isl.get_world_3d().scenario
	_xf = isl.global_transform
	_t_start = Time.get_ticks_msec()
	_decode_task = WorkerThreadPool.add_task(_decode, false, "warren decode " + id)


# ------------------------------------------------------------------ decoding (a worker)
## The file is tools/sky/warren/FORMAT.md's (the GENERATOR's writer.py): "WRN1", u16 version, civ, x0 z0 cell storey,
## nx nz levels, the palette (sRGB), the piece-id and species tables, the chunk table [ci, cj, first, count], the records
## (7 bytes: u16 piece, u8 i, u8 j (GLOBAL cells), u8 level, u8 rot_flags, u8 pal_epoch), units, doors, the arrival point,
## the foliage.  Version 2: rot_flags bits 0-1 rot, bit 2 DECK (y = the deck at the cell centre), bit 3 MIRROR, bits 4-7
## the mount (0 cell centre, 1 face, 2 corner); pal_epoch bits 0-3 the kit palette variant, 4-7 the epoch.
var _buf := PackedByteArray()
var _p := 0


func _u8() -> int:
	_p += 1
	return _buf.decode_u8(_p - 1)


func _u16() -> int:
	_p += 2
	return _buf.decode_u16(_p - 2)


func _u32() -> int:
	_p += 4
	return _buf.decode_u32(_p - 4)


func _f32() -> float:
	_p += 4
	return _buf.decode_float(_p - 4)


func _str() -> String:
	var n := _u16()
	_p += n
	return _buf.slice(_p - n, _p).get_string_from_utf8()


func _decode() -> void:
	var sp := DIR + id + ".json"                       # (the readable side: travel, anchors, walk -- parsed here too)
	if DataFile.exists(sp):
		var d = JSON.parse_string(DataFile.text(sp))
		if d is Dictionary:
			side = d
	# (plain gzip, as Python writes it: FileAccess.open_compressed reads only Godot's own compressed format)
	var raw := FileAccess.get_file_as_bytes(DIR + id + ".bin.gz")
	if raw.is_empty():
		return
	_buf = raw.decompress_dynamic(-1, FileAccess.COMPRESSION_GZIP)
	if _buf.size() < 12 or _buf.slice(0, 4).get_string_from_ascii() != "WRN1":
		push_warning("SkyWarren %s: not a warren file" % id)
		return
	_p = 4
	var h := {}
	h.version = _u16()
	if h.version < 2:
		push_warning("SkyWarren %s: format v%d (v2 needed: rerun tools/sky/warren)" % [id, h.version])
		return
	h.civ = _str()
	lod0_m = float(side.get("lod0_m", LOD0_CIV.get(h.civ, LOD0_M)))
	h.x0 = _f32()
	h.z0 = _f32()
	h.cell = _f32()
	h.storey = _f32()
	h.nx = _u16()
	h.nz = _u16()
	h.levels = _u8()
	var pal: Array = []
	for k in _u8():
		pal.append(Color8(_u8(), _u8(), _u8()))
	h.palette = pal
	var pieces: Array = []
	for k in _u16():
		pieces.append(_str())
	h.pieces = pieces
	var species: Array = []
	for k in _u16():
		species.append(_str())
	h.species = species
	var table: Array = []
	for k in _u16():
		table.append([_u8(), _u8(), _u32(), _u32()])
	var nrec := _u32()
	var rec0 := _p
	_p += nrec * 7
	var units: Array = []
	for k in _u16():
		units.append([_u8(), _u8(), _u8(), _u16()])
	h.units = units
	var doors: Array = []
	for k in _u16():
		doors.append([_u16(), _u8(), _u8(), _u8(), _u8(), _u8()])
	h.doors = doors
	h.travel = [_f32(), _f32(), _f32(), _f32()]
	var fol: Array = []
	if _p + 4 <= _buf.size():
		for k in _u32():
			var spc := _u8()
			var x := (_buf.decode_s16(_p)) * 0.1
			var z := (_buf.decode_s16(_p + 2)) * 0.1
			_p += 4
			fol.append([spc, x, _u8() * 0.25, z, _u8() / 256.0 * TAU, _u8() / 64.0])
	h.foliage = fol
	for t in table:
		var ci: int = t[0]
		var cj: int = t[1]
		var recs := _buf.slice(rec0 + int(t[2]) * 7, rec0 + (int(t[2]) + int(t[3])) * 7)
		var x0 := float(h.x0) + CELL * CH * ci
		var z0 := float(h.z0) + CELL * CH * cj
		var top := 0
		for r in int(t[3]):
			top = maxi(top, recs.decode_u8(r * 7 + 4))
		var box := AABB(Vector3(x0, -2.0, z0), Vector3(CELL * CH, STOREY * (top + 1) + 4.0, CELL * CH))
		chunks.append({"ci": ci, "cj": cj, "recs": recs, "n": int(t[3]), "box": box,
			"centre": Vector3(x0 + CELL * CH * 0.5, 0.0, z0 + CELL * CH * 0.5),
			"state": 0, "inst0": RID(), "inst1": RID(), "faces": PackedVector3Array(), "owner": -1})
	_buf = PackedByteArray()
	head = h


# ------------------------------------------------------------------ the frame's work (SkyIsland._process_inner)
func step(delta: float) -> void:
	if _decode_task >= 0:
		if not WorkerThreadPool.is_task_completed(_decode_task):
			return
		WorkerThreadPool.wait_for_task_completion(_decode_task)
		_decode_task = -1
		if head.is_empty():
			return
		_prep_task = WorkerThreadPool.add_task(_prepare, false, "warren variants " + id)   # (the kit, then the variants)
	if _prep_task >= 0:
		if not WorkerThreadPool.is_task_completed(_prep_task):
			return
		WorkerThreadPool.wait_for_task_completion(_prep_task)
		_prep_task = -1
		for k in ["solid", "metal", "glass", "emissive", "water"]:   # (the workers only read them)
			_mat(k)
		_lod_vc = RemakeBuilding.lod_vc_material(true)
		_queue = chunks.duplicate()
		# nearest the player first
		var pl := _player_local()
		_queue.sort_custom(func(a, b): return (a.centre as Vector3).distance_squared_to(pl) < (b.centre as Vector3).distance_squared_to(pl))
		for c in chunks:
			var gk := Vector2i(int(c.ci) / 4, int(c.cj) / 4)
			if not groups.has(gk):
				groups[gk] = {"chunks": [], "inst": RID(), "mesh": RID(), "state": 0}
			groups[gk].chunks.append(c)
		_make_body()
	# dispatch
	# (the island the player is on or nearest first: the others wait while it has work)
	var cap := MAX_TASKS_ALL if _player_local().length() < 400.0 else 1
	while _tasks.size() < MAX_TASKS and _tasks_all < cap and not _queue.is_empty():
		var c: Dictionary = _queue.pop_front()
		var tid := WorkerThreadPool.add_task(_merge_chunk.bind(c), false, "warren chunk")
		_tasks[tid] = c
		_tasks_all += 1
	for tid in _tasks.keys():
		if WorkerThreadPool.is_task_completed(tid):
			WorkerThreadPool.wait_for_task_completion(tid)
			_tasks.erase(tid)
			_tasks_all -= 1
	for tid in _gtasks.keys():
		if WorkerThreadPool.is_task_completed(tid):
			WorkerThreadPool.wait_for_task_completion(tid)
			_gtasks.erase(tid)
	# uploads, within the frame budget
	Prof.begin("warren.upload")
	var fr := Engine.get_process_frames()
	if fr != _up_frame:
		_up_frame = fr
		_up_used = 0
	var t0 := Time.get_ticks_usec()
	while _up_used + Time.get_ticks_usec() - t0 < UPLOAD_USEC:
		_rmutex.lock()
		var r: Array = _results.pop_front() if not _results.is_empty() else []
		var g: Array = _gresults.pop_front() if r.is_empty() and not _gresults.is_empty() else []
		_rmutex.unlock()
		if not r.is_empty():
			_upload_chunk(r)
		elif not g.is_empty():
			_upload_group(g)
		else:
			break
	_up_used += Time.get_ticks_usec() - t0
	Prof.end("warren.upload")
	# quadrants whose chunks are all in: merge their LOD1 into the LOD2
	for gk in groups:
		var gr: Dictionary = groups[gk]
		if gr.state == 0 and (gr.chunks as Array).all(func(c): return int(c.state) == 2):
			gr.state = 1
			var tid := WorkerThreadPool.add_task(_merge_group.bind(gk), false, "warren lod2")
			_gtasks[tid] = gk
	if not ready and _queue.is_empty() and _tasks.is_empty() and chunks.all(func(c): return int(c.state) == 2):
		ready = true
		Prof.begin("warren.lights")
		_make_flares()
		_make_plants()
		Prof.end("warren.lights")
	_ref_t -= delta
	_refresh()
	_col_t -= delta
	if _col_t <= 0.0:
		_col_t = 0.1
		Prof.begin("warren.collide")
		_collision()
		Prof.end("warren.collide")


func _player_local() -> Vector3:
	var pl: Node3D = isl.sys.player if isl.sys else null
	if pl == null:
		return Vector3.ZERO
	return isl.global_transform.affine_inverse() * pl.global_position


func _cam_local() -> Vector3:
	## where the view is, in the island frame (what draws is decided from there: the player's camera, a lark's, ...)
	var cam := isl.get_viewport().get_camera_3d() if isl.is_inside_tree() else null
	if cam == null:
		return _player_local()
	return isl.global_transform.affine_inverse() * cam.global_position


# ------------------------------------------------------------------ pieces (the shared kit)
## pieces.json (KIT: remake/blender/sky/warren_kit) names the kit's meshes in remake/sky/warrens/kit/kit.glb.  Since
## FORMAT.md v2 the GENERATOR writes KIT's own ids and frames (a wall on z 0 facing +Z, mounted on the cell's face by the
## placement's mount bits): the pieces are taken as they are; an id the kit lacks is a placeholder box (counted in missing).
static var _kit := {}                # KIT id -> {surfs: [[slot, arrays]], aabb, lod1, collide, group}
static var missing := {}             # generator ids drawn as placeholders (reported)


static var _kit_mutex := Mutex.new()


func _prepare() -> void:
	## (a worker) the kit, once for all islands, then this island's variants
	_kit_mutex.lock()
	_load_pieces()
	_kit_mutex.unlock()
	_prepare_variants()
	_lights_prep()
	_plants_prep()
	_walk_prep()


static func _load_pieces() -> void:
	if _pieces_loaded:
		return
	_pieces_loaded = true
	if not DataFile.exists(PIECES):
		return
	var d = JSON.parse_string(DataFile.text(PIECES))
	if not (d is Dictionary):
		return
	var scenes := {}
	for pid in (d.get("pieces", {}) as Dictionary):
		var spec: Dictionary = d.pieces[pid]
		var glb := str(spec.get("glb", ""))
		if not ResourceLoader.exists(glb):
			continue
		if not scenes.has(glb):
			scenes[glb] = (load(glb) as PackedScene).instantiate()
		var root: Node = scenes[glb]
		var mi := root.find_child(str(spec.get("mesh", pid)), true, false) as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var group := str(spec.get("group", "cell"))
		var surfs: Array = []
		var slots: Array = spec.get("slots", [])
		var box := AABB()
		var first := true
		for si in mi.mesh.get_surface_count():
			var m: Material = mi.mesh.surface_get_material(si)
			var slot := str(m.resource_name).trim_prefix("wk_") if m else ""
			if not SLOTS.has(slot):
				slot = str(slots[si]) if si < slots.size() else "wall"
			var arrays: Array = mi.mesh.surface_get_arrays(si)
			var vs: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for k in vs.size():
				box = AABB(vs[k], Vector3.ZERO) if first else box.expand(vs[k])
				first = false
			arrays[Mesh.ARRAY_TANGENT] = null
			surfs.append([slot, arrays])
		_kit[pid] = {"surfs": surfs, "aabb": box, "lod1": str(spec.get("lod1", "box")), "group": group,
			"collide": spec.get("collide", true) is bool and bool(spec.get("collide", true)) or str(spec.get("collide")) == "ramp"}
	for k in scenes:
		(scenes[k] as Node).free()
	_palettes = d.get("palettes", {})


static func _piece(gid: String) -> Dictionary:
	var key := gid
	_vmutex.lock()
	var have = _pieces.get(key)
	_vmutex.unlock()
	if have != null:
		return have
	var kid := gid if _kit.has(gid) else ""
	var pc: Dictionary
	if kid != "":
		pc = _kit[kid]
	else:
		pc = _placeholder(gid)
	_vmutex.lock()
	if kid == "":
		missing[gid] = true
	_pieces[key] = pc
	_vmutex.unlock()
	return pc


static func _placeholder(pid: String) -> Dictionary:
	## a stand-in for a piece pieces.json doesn't have yet: boxes in the piece frame (format.md), by the id's kind
	var g := {}
	var lod1 := "box"
	var collide := true
	if pid.begins_with("wall"):
		_bx(g, "wall", Vector3(-1.5, 0, -1.5), Vector3(1.5, 3.2, -1.2))
		if pid.contains("window"):
			var n := 2 if pid.contains("pair") else 1
			for k in n:
				var cx := 0.0 if n == 1 else (-0.7 if k == 0 else 0.7)
				_bx(g, "frame", Vector3(cx - 0.55, 0.95, -1.56), Vector3(cx + 0.55, 2.45, -1.5))
				_bx(g, "glass", Vector3(cx - 0.45, 1.05, -1.6), Vector3(cx + 0.45, 2.35, -1.56))
		elif pid.contains("door"):
			_bx(g, "frame", Vector3(-0.6, 0.0, -1.58), Vector3(0.6, 2.3, -1.5))
		elif pid.contains("shopfront"):
			_bx(g, "glass", Vector3(-1.2, 0.2, -1.6), Vector3(1.2, 2.4, -1.5))
			_bx(g, "emissive", Vector3(-1.3, 2.5, -1.62), Vector3(1.3, 2.75, -1.5))
		elif pid.contains("screen"):
			_bx(g, "screen", Vector3(-0.8, 0.9, -1.95), Vector3(0.8, 2.6, -1.5))
	elif pid.begins_with("corner"):
		_bx(g, "trim", Vector3(-1.55, 0, -1.55), Vector3(-1.2, 3.2, -1.2))
	elif pid.begins_with("roof"):
		_bx(g, "roof", Vector3(-1.5, -0.12, -1.5), Vector3(1.5, 0.04, 1.5))
	elif pid.begins_with("parapet") or pid.begins_with("edge") or pid.begins_with("eave"):
		_bx(g, "wall", Vector3(-1.5, 0.0, -1.5), Vector3(1.5, 0.95, -1.25))
		_bx(g, "trim", Vector3(-1.55, 0.95, -1.55), Vector3(1.55, 1.05, -1.2))
	elif pid.begins_with("pave") or pid.begins_with("interior_floor"):
		_bx(g, "paving", Vector3(-1.5, 0.0, -1.5), Vector3(1.5, 0.06, 1.5))
		collide = false
	elif pid.contains("lantern") or pid.contains("lamp") or pid.contains("festoon"):
		_bx(g, "emissive", Vector3(-0.25, 0.7, -0.25), Vector3(0.25, 1.2, 0.25))
		lod1 = "drop"
		collide = false
	elif pid.contains("tank") or pid.contains("minaret") or pid.contains("shack"):
		_bx(g, "metal", Vector3(-0.7, 0.1, -0.7), Vector3(0.7, 1.7, 0.7))
		lod1 = "keep"
	else:
		_bx(g, "metal", Vector3(-0.45, 1.8, -2.0), Vector3(0.45, 2.4, -1.5))
		lod1 = "drop"
		collide = false
	var surfs: Array = []
	var box := AABB()
	var first := true
	for slot in g:
		var a: Array = g[slot]
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = a[0]
		arrays[Mesh.ARRAY_NORMAL] = a[1]
		arrays[Mesh.ARRAY_TEX_UV] = a[2]
		arrays[Mesh.ARRAY_INDEX] = a[3]
		surfs.append([slot, arrays])
		for v in (a[0] as PackedVector3Array):
			if first:
				box = AABB(v, Vector3.ZERO)
				first = false
			else:
				box = box.expand(v)
	return {"surfs": surfs, "aabb": box, "lod1": lod1, "collide": collide}


static func _bx(g: Dictionary, slot: String, lo: Vector3, hi: Vector3) -> void:
	## a box into g[slot] = [verts, normals, uvs, indices]: six faces, front faces clockwise (Godot).  (Packed arrays
	## inside an Array are values: taken out, appended to, and put back.)
	if not g.has(slot):
		g[slot] = [PackedVector3Array(), PackedVector3Array(), PackedVector2Array(), PackedInt32Array()]
	var a: Array = g[slot]
	var vs: PackedVector3Array = a[0]
	var ns: PackedVector3Array = a[1]
	var us: PackedVector2Array = a[2]
	var ix: PackedInt32Array = a[3]
	var c := (lo + hi) * 0.5
	var e := (hi - lo) * 0.5
	for n: Vector3 in [Vector3.RIGHT, Vector3.LEFT, Vector3.UP, Vector3.DOWN, Vector3.BACK, Vector3.FORWARD]:
		var upr: Vector3 = Vector3.UP if absf(n.y) < 0.5 else (Vector3.FORWARD if n.y > 0.0 else Vector3.BACK)
		var u: Vector3 = upr.cross(n)
		var v: Vector3 = n.cross(u)
		var fc := c + n * (e * n.abs()).length()
		var hu := (e * u.abs()).length()
		var hv := (e * v.abs()).length()
		var base := vs.size()
		for q: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
			vs.append(fc + u * hu * q.x + v * hv * q.y)
			ns.append(n)
			us.append(Vector2(q.x * hu, q.y * hv))
		for k in [0, 2, 1, 0, 3, 2]:
			ix.append(base + k)
	g[slot] = [vs, ns, us, ix]


func _pal(pv: int, slot := "wall") -> Color:
	## a slot's colour in this civ's kit palette variant pv (pieces.json palettes[civ][pv][slot])
	var vs: Array = _palettes.get(str(head.get("civ", "")), [])
	if vs.is_empty():
		var pals: Array = head.get("palette", [])
		return SLOT_DEFAULT.get(slot, pals[clampi(pv, 0, pals.size() - 1)] if not pals.is_empty() else Color(0.85, 0.8, 0.7))
	var v: Dictionary = vs[clampi(pv, 0, vs.size() - 1)]
	if v.has(slot):
		return Color.html(str(v[slot]))
	return SLOT_DEFAULT.get(slot, Color.html(str(v.get("wall", "#d0c8b8"))))


const SLOT_DEFAULT := {"trim": Color(0.93, 0.9, 0.84), "frame": Color(0.36, 0.24, 0.15), "glass": Color(0.62, 0.7, 0.76),
	"screen": Color(0.42, 0.29, 0.18), "metal": Color(0.44, 0.46, 0.48), "fabric": Color(0.66, 0.28, 0.22),
	"emissive": Color(1.0, 0.84, 0.6), "water": Color(0.3, 0.45, 0.5), "plant": Color(0.37, 0.48, 0.24),
	"tile": Color(0.2, 0.45, 0.35), "ground": Color(0.7, 0.64, 0.52), "paving": Color(0.7, 0.64, 0.52),
	"accent": Color(0.75, 0.2, 0.15), "accent2": Color(0.83, 0.68, 0.3)}


func _vkey(pk: int, pv: int, mirror: bool) -> String:
	return "%s|%s|%d|%d" % [str(head.pieces[pk]), str(head.civ), pv, int(mirror)]


## Variants are kept CPU-side, unindexed, per slot: {slot: [verts, normals, uvs, colours]}.  A placement is then
## `xf * verts` and `append_array` -- both in C++ -- with no reads back from the RenderingServer (SurfaceTool.append_from
## read each source mesh's arrays back from the server per call: a near island took minutes).
var _vlocal := {}                    # Vector3i(piece, palette variant, mirror) -> variant (this island's, ready)
var _blocal := {}                    # Vector2i(piece, palette variant) -> its LOD1 box variant
var _plocal := {}                    # piece index -> the piece (lod1, collide, aabb)


func _prepare_variants() -> void:
	## (a worker, once per island) every (piece, palette variant, mirror) its chunks use, the colours baked in
	for c in chunks:
		var recs: PackedByteArray = c.recs
		for r in int(c.n):
			var o := r * 7
			var pk := recs.decode_u16(o)
			var mir := (recs.decode_u8(o + 5) >> 3) & 1
			var pv := recs.decode_u8(o + 6) & 15
			var key := Vector3i(pk, pv, mir)
			if _vlocal.has(key):
				continue
			_vlocal[key] = _variant(pk, pv, mir == 1)
			var bk := Vector2i(pk, pv)
			if not _blocal.has(bk):
				_blocal[bk] = _box_variant(pk, pv)
			if not _plocal.has(pk):
				_plocal[pk] = _piece(str(head.pieces[pk]))


static func _unindex(src: Array, mirror: bool) -> Array:
	## [verts, normals, uvs] of a surface, as plain triangles (mirrored in x, winding turned, if asked)
	var v: PackedVector3Array = src[Mesh.ARRAY_VERTEX]
	var n: PackedVector3Array = src[Mesh.ARRAY_NORMAL] if src[Mesh.ARRAY_NORMAL] != null else PackedVector3Array()
	var u: PackedVector2Array = src[Mesh.ARRAY_TEX_UV] if src[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
	var c: PackedColorArray = src[Mesh.ARRAY_COLOR] if src[Mesh.ARRAY_COLOR] != null else PackedColorArray()
	var ix: PackedInt32Array = src[Mesh.ARRAY_INDEX] if src[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	if ix.is_empty():
		ix.resize(v.size())
		for k in v.size():
			ix[k] = k
	var ov := PackedVector3Array()
	var on := PackedVector3Array()
	var ou := PackedVector2Array()
	var oc := PackedColorArray()
	var has_n := n.size() == v.size()
	var has_u := u.size() == v.size()
	var has_c := c.size() == v.size()
	ov.resize(ix.size())
	on.resize(ix.size())
	ou.resize(ix.size())
	oc.resize(ix.size())
	for t in range(0, ix.size() - 2, 3):
		var tri := [ix[t], ix[t + 2], ix[t + 1]] if mirror else [ix[t], ix[t + 1], ix[t + 2]]
		for k in 3:
			var a: int = tri[k]
			var p := v[a]
			var nn := n[a] if has_n else Vector3.UP
			if mirror:
				p.x = -p.x
				nn.x = -nn.x
			ov[t + k] = p
			on[t + k] = nn
			ou[t + k] = u[a] if has_u else Vector2.ZERO
			oc[t + k] = c[a] if has_c else Color(1, 1, 1)
	return [ov, on, ou, oc]


func _variant(pk: int, pv: int, mirror: bool) -> Dictionary:
	var key := _vkey(pk, pv, mirror)
	_vmutex.lock()
	var have = _variants.get(key)
	_vmutex.unlock()
	if have != null:
		return have
	var pc := _piece(str(head.pieces[pk]))
	var out := {}
	for sf in pc.surfs:
		var slot: String = sf[0]
		var a := _unindex(sf[1], mirror)
		var col := _pal(pv, slot)
		var cs: PackedColorArray = a[3]
		for k in cs.size():
			cs[k] = col * cs[k]                       # (KIT's COLOR_0: a grey shade, times the slot's colour)
		a[3] = cs
		if out.has(slot):                             # (two surfaces of one slot: one run)
			var b: Array = out[slot]
			for k in 4:
				b[k].append_array(a[k])
			out[slot] = b
		else:
			out[slot] = a
	_vmutex.lock()
	_variants[key] = out
	_vmutex.unlock()
	return out


func _bkey(pk: int, pv: int) -> String:
	return "%s|%s" % [str(head.pieces[pk]), _pal(pv).to_html()]


func _box_variant(pk: int, pv: int) -> Array:
	var key := _bkey(pk, pv)
	_vmutex.lock()
	var have = _box_variants.get(key)
	_vmutex.unlock()
	if have != null:
		return have
	var pc := _piece(str(head.pieces[pk]))
	var box: AABB = pc.aabb
	var g := {}
	_bx(g, "wall", box.position, box.end)
	var a: Array = g.wall
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = a[0]
	arrays[Mesh.ARRAY_NORMAL] = a[1]
	arrays[Mesh.ARRAY_TEX_UV] = a[2]
	arrays[Mesh.ARRAY_INDEX] = a[3]
	var out := _unindex(arrays, false)
	var cs: PackedColorArray = out[3]
	cs.fill(_pal(pv))
	out[3] = cs
	_vmutex.lock()
	_box_variants[key] = out
	_vmutex.unlock()
	return out


# ------------------------------------------------------------------ merging (workers)
func _rec_xf(c: Dictionary, recs: PackedByteArray, o: int) -> Transform3D:
	## a placement's transform about its chunk's centre (FORMAT.md v2): the cell's floor centre (or the deck there: DECK),
	## turned, then out to the face (mount 1) or the corner (mount 2)
	var i := recs.decode_u8(o + 2)
	var j := recs.decode_u8(o + 3)
	var k := recs.decode_u8(o + 4)
	var fl := recs.decode_u8(o + 5)
	var x := float(head.x0) + CELL * i + 1.5
	var z := float(head.z0) + CELL * j + 1.5
	var y: float = isl.deck_y(x, z) if (fl & 4) != 0 else STOREY * k
	var b := Basis(Vector3.UP, (fl & 3) * PI * 0.5)
	var p := Vector3(x, y, z) - (c.centre as Vector3)
	match fl >> 4:
		1:
			p += b * Vector3(0, 0, 1.5)
		2:
			p += b * Vector3(1.5, 0, 1.5)
	return Transform3D(b, p)


static func _acc(dst: Dictionary, slot: String, a: Array, xf: Transform3D) -> void:
	if not dst.has(slot):
		dst[slot] = [PackedVector3Array(), PackedVector3Array(), PackedVector2Array(), PackedColorArray()]
	var d: Array = dst[slot]
	var v: PackedVector3Array = d[0]
	var n: PackedVector3Array = d[1]
	var u: PackedVector2Array = d[2]
	var c: PackedColorArray = d[3]
	v.append_array(xf * (a[0] as PackedVector3Array))
	n.append_array(Transform3D(xf.basis, Vector3.ZERO) * (a[1] as PackedVector3Array))
	u.append_array(a[2])
	c.append_array(a[3])
	dst[slot] = [v, n, u, c]


func _merge_chunk(c: Dictionary) -> void:
	var t0 := Time.get_ticks_usec()
	var recs: PackedByteArray = c.recs
	var lod0 := {}                      # slot -> [verts, normals, uvs, colours]
	var lod1 := {}                      # "lod1" -> the same, one run
	var faces := PackedVector3Array()
	for r in int(c.n):
		var o := r * 7
		var pk := recs.decode_u16(o)
		var pv := recs.decode_u8(o + 6) & 15
		var vm = _vlocal.get(Vector3i(pk, pv, (recs.decode_u8(o + 5) >> 3) & 1))
		var pc = _plocal.get(pk)
		if vm == null or pc == null:
			continue
		var xf := _rec_xf(c, recs, o)
		for slot in vm:
			_acc(lod0, MAT_OF.get(slot, "solid"), vm[slot], xf)
		match str(pc.lod1):
			"keep":
				for slot in vm:
					_acc(lod1, "lod1", vm[slot], xf)
			"box":
				_acc(lod1, "lod1", _blocal[Vector2i(pk, pv)], xf)
		if bool(pc.collide):
			_box_faces(faces, xf, pc.aabb)
	# the meshes made here too (resources not in the tree may be made on a worker; the RenderingServer queues the
	# upload): an ArrayMesh made on the main thread from a big chunk's arrays took 25-40 ms of a frame
	var m0: ArrayMesh = null
	var tris := 0
	for slot in lod0:
		var a: Array = lod0[slot]
		if (a[0] as PackedVector3Array).is_empty():
			continue
		if m0 == null:
			m0 = ArrayMesh.new()
		m0.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _arrays(a))
		m0.surface_set_material(m0.get_surface_count() - 1, _mats[str(slot)])
		tris += (a[0] as PackedVector3Array).size() / 3
	var l1: Array = lod1.get("lod1", [])
	var m1: ArrayMesh = null
	if not l1.is_empty() and not (l1[0] as PackedVector3Array).is_empty():
		m1 = ArrayMesh.new()
		m1.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _arrays(l1))
		m1.surface_set_material(0, _lod_vc)
	_rmutex.lock()
	_results.append([c, m0, l1, faces, Time.get_ticks_usec() - t0, m1, tris])
	_rmutex.unlock()


static func _box_faces(faces: PackedVector3Array, xf: Transform3D, b: AABB) -> void:
	var p := []
	for k in 8:
		p.append(xf * (b.position + b.size * Vector3(k & 1, (k >> 1) & 1, (k >> 2) & 1)))
	for q in [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]:
		faces.append_array([p[q[0]], p[q[1]], p[q[2]], p[q[0]], p[q[2]], p[q[3]]])


func _merge_group(gk: Vector2i) -> void:
	var gr: Dictionary = groups[gk]
	var centre := Vector3.ZERO
	for c in gr.chunks:
		centre += c.centre
	centre /= maxf(1.0, (gr.chunks as Array).size())
	var acc := {}
	for c in gr.chunks:
		var a = c.get("lod1_arrays")
		if a == null or (a as Array).is_empty():
			continue
		_acc(acc, "lod1", a, Transform3D(Basis(), (c.centre as Vector3) - centre))
	var a: Array = acc.get("lod1", [])
	var sd: ArrayMesh = null
	if not a.is_empty() and not (a[0] as PackedVector3Array).is_empty():
		sd = ArrayMesh.new()
		sd.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _arrays(a))
		sd.surface_set_material(0, _lod_vc)
	_rmutex.lock()
	_gresults.append([gk, a, centre, sd])
	_rmutex.unlock()


static func _arrays(a: Array) -> Array:
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = a[0]
	arr[Mesh.ARRAY_NORMAL] = a[1]
	arr[Mesh.ARRAY_TEX_UV] = a[2]
	arr[Mesh.ARRAY_COLOR] = a[3]
	return arr


# ------------------------------------------------------------------ uploads (main thread)
static func _mat(slot: String) -> Material:
	if _mats.has(slot):
		return _mats[slot]
	var m: Material
	match slot:
		"glass":
			var g := RemakeBuilding.window_glass("warren_glass", {"color": [0.62, 0.7, 0.76], "alpha": 0.2}, true)
			g.set_shader_parameter("near_m", 0.0)
			g.set_shader_parameter("far_m", 0.5)              # (no real rooms behind: the fake room from half a metre)
			m = g
		"water":
			var w := StandardMaterial3D.new()
			w.vertex_color_use_as_albedo = true
			w.vertex_color_is_srgb = true
			w.roughness = 0.08
			w.metallic_specular = 0.8
			m = w
		"emissive":
			var s := ShaderMaterial.new()
			s.shader = load("res://remake/shaders/warren_emissive.gdshader")
			m = s
		_:
			var sm := StandardMaterial3D.new()
			sm.vertex_color_use_as_albedo = true
			sm.vertex_color_is_srgb = true
			sm.roughness = 0.35 if slot == "metal" else 0.9
			sm.metallic = 0.3 if slot == "metal" else 0.0
			m = sm
	_mats[slot] = m
	return m


func _upload_chunk(r: Array) -> void:
	var c: Dictionary = r[0]
	c.faces = r[3]
	c.lod1_arrays = r[2]
	merge_usec.append(int(r[4]))
	var m0: ArrayMesh = r[1]
	if m0:
		c.mesh0_res = m0
		c.tris0 = int(r[6])
		c.surfs0 = m0.get_surface_count()
		c.inst0 = _instance(m0.get_rid(), 0.0, lod0_m, true)
		_entry(c.inst0, c.centre, (c.centre as Vector3) + m0.get_aabb().get_center(), 0.0, lod0_m)
	var m1: ArrayMesh = r[5]
	if m1:
		c.mesh1_res = m1
		c.inst1 = _instance(m1.get_rid(), lod0_m, LOD1_M, false)
		_entry(c.inst1, c.centre, (c.centre as Vector3) + m1.get_aabb().get_center(), lod0_m, LOD1_M)
	c.state = 2
	built += 1
	if built == chunks.size():
		built_ms = Time.get_ticks_msec() - _t_start


func _upload_group(g: Array) -> void:
	var gr: Dictionary = groups[g[0]]
	gr.centre = g[2]
	var m: ArrayMesh = g[3]
	if m == null:
		gr.state = 2
		return
	gr.mesh_res = m
	gr.inst = _instance(m.get_rid(), LOD1_M, NEAR_END, false)
	gr.state = 2
	_entry(gr.inst, gr.centre, (gr.centre as Vector3) + m.get_aabb().get_center(), LOD1_M, NEAR_END)


func _instance(mesh: RID, begin: float, end: float, shadows: bool) -> RID:
	var inst := RenderingServer.instance_create2(mesh, _scenario)
	RenderingServer.instance_geometry_set_visibility_range(inst, begin, end, begin * 0.06, end * 0.06,
		RenderingServer.VISIBILITY_RANGE_FADE_DISABLED)
	RenderingServer.instance_geometry_set_cast_shadows_setting(inst,
		RenderingServer.SHADOW_CASTING_SETTING_ON if shadows else RenderingServer.SHADOW_CASTING_SETTING_OFF)
	RenderingServer.instance_set_visible(inst, false)          # (shown when it is in range: _refresh)
	return inst


# ------------------------------------------------------------------ placing (SkyIsland.moved: every tick it moves)
## Only the instances that can be seen are kept up with the island: each is an entry with the range of distances (from
## the player) in which it draws, and _refresh (every REFRESH s, or as soon as the player has moved REFRESH_M) shows
## and places the ones in range (with a margin) and hides the rest -- a hidden instance's stale transform is harmless.
## place() then pushes only those: a near island moves every tick, and each push is a call from GDScript.
const REFRESH := 0.25
const REFRESH_M := 6.0
const MARGIN_M := 14.0
var _ents: Array = []                # [rid, local origin, visual centre (island frame), near, far, shown]
var _act_rid: Array[RID] = []
var _act_xf: Array[Transform3D] = []
var _ref_t := 0.0
var _act_dirty := false
var _ref_at := Vector3(INF, INF, INF)
var place_usec := 0                  # (stats: the last place()'s time)


func _entry(rid: RID, origin: Vector3, vc: Vector3, near: float, far: float) -> void:
	var e := [rid, Transform3D(Basis(), origin), vc, near * 0.94 - MARGIN_M, far * 1.06 + MARGIN_M, false]
	_ents.append(e)
	_show(e, _cam_local())
	_act_dirty = true                     # (the pushed list is rebuilt at the next _refresh)


func _show(e: Array, pl: Vector3) -> bool:
	## (e in or out of range now) -- true if it changed
	var d := (e[2] as Vector3).distance_to(pl)
	var want := _visible and d >= float(e[3]) and d < float(e[4])
	if want == bool(e[5]):
		return false
	e[5] = want
	if want:
		RenderingServer.instance_set_transform(e[0], _xf * (e[1] as Transform3D))
	RenderingServer.instance_set_visible(e[0], want)
	return true


func _refresh(force := false) -> void:
	var pl := _cam_local()
	if not force and not _act_dirty and pl.distance_to(_ref_at) < REFRESH_M and _ref_t > 0.0:
		return
	_ref_t = REFRESH
	_ref_at = pl
	var changed := force or _act_dirty
	_act_dirty = false
	for e in _ents:
		if _show(e, pl):
			changed = true
	if changed:
		_act_rid.clear()
		_act_xf.clear()
		for e in _ents:
			if bool(e[5]):
				_act_rid.append(e[0])
				_act_xf.append(e[1])


func place(xf: Transform3D) -> void:
	var t0 := Time.get_ticks_usec()
	_xf = xf
	for k in _act_rid.size():
		RenderingServer.instance_set_transform(_act_rid[k], xf * _act_xf[k])
	place_usec = Time.get_ticks_usec() - t0


func set_visible(on: bool) -> void:
	_visible = on
	_refresh(true)
	if _flare_mm:
		_flare_mm.visible = on
	if _pool_mm:
		_pool_mm.visible = on


func free_all() -> void:
	for tid in _tasks:
		WorkerThreadPool.wait_for_task_completion(tid)
		_tasks_all -= 1
	for tid in _gtasks:
		WorkerThreadPool.wait_for_task_completion(tid)
	if _decode_task >= 0:
		WorkerThreadPool.wait_for_task_completion(_decode_task)
	if _prep_task >= 0:
		WorkerThreadPool.wait_for_task_completion(_prep_task)
	_tasks.clear()
	_gtasks.clear()
	for c in chunks:
		for k in ["inst0", "inst1"]:
			if c.has(k) and (c[k] as RID).is_valid():
				RenderingServer.free_rid(c[k])
				c[k] = RID()
	for gk in groups:
		for k in ["inst"]:
			if groups[gk].get(k, RID()).is_valid():
				RenderingServer.free_rid(groups[gk][k])
	for p in _plants:
		RenderingServer.free_rid(p[0])
		RenderingServer.free_rid(p[1])
	_plants.clear()
	chunks.clear()
	groups.clear()
	_ents.clear()
	_act_rid.clear()
	_act_xf.clear()


# ------------------------------------------------------------------ collision (near the player only)
func _make_body() -> void:
	var near: Node = isl.get_node_or_null("Near")
	if near == null:
		return
	_body = StaticBody3D.new()
	_body.name = "WarrenBody"
	near.add_child(_body)


func _collision() -> void:
	if _body == null or not is_instance_valid(_body):
		return
	var pl := _player_local()
	var added := 0
	for c in chunks:
		if int(c.state) != 2:
			continue
		var d := (c.box as AABB).grow(0.0).get_center().distance_to(pl) - (c.box as AABB).size.x * 0.7
		if int(c.owner) < 0 and d < COLLIDE_M and (c.faces as PackedVector3Array).size() > 0 and added < 1:
			added += 1                                    # (one shape a call: a big chunk's takes ~10 ms to build)
			var sh := ConcavePolygonShape3D.new()
			sh.set_faces(c.faces)
			var o := _body.create_shape_owner(_body)
			_body.shape_owner_add_shape(o, sh)
			_body.shape_owner_set_transform(o, Transform3D(Basis(), c.centre))   # (the faces are about the chunk's centre)
			c.owner = o
		elif int(c.owner) >= 0 and d > COLLIDE_DROP:
			_body.remove_shape_owner(int(c.owner))
			c.owner = -1


func near_ready() -> bool:
	## is the city round the player solid yet? (fast travel holds the traveller until it is)
	if head.is_empty() and _decode_task < 0:
		return true                                   # (nothing to wait for)
	if chunks.is_empty():
		return false
	var pl := _player_local()
	for c in chunks:
		var d := (c.box as AABB).get_center().distance_to(pl) - (c.box as AABB).size.x * 0.7
		if d < COLLIDE_M * 0.5:
			if int(c.state) != 2 or ((c.faces as PackedVector3Array).size() > 0 and int(c.owner) < 0):
				return false
	return true


# ------------------------------------------------------------------ the city's side: travel, anchors, walk, flares
func travel() -> Array:
	return side.get("travel", head.get("travel", []))


func anchors() -> Array:
	return side.get("anchors", [])


func walk() -> Dictionary:
	return side.get("walk", {})


## kind -> [flare strength (0: none), pool radius m (0: none)]; "lamp" is an interior lamp (it lights its window)
const LIGHT_KIND := {"lantern": [0.9, 3.2], "festoon": [0.5, 2.6], "fluoro": [0.6, 3.0], "shop": [0.8, 3.6],
	"door": [0.6, 2.8], "stall": [0.7, 3.4], "fountain": [0.5, 3.0], "minaret": [1.0, 0.0], "tower": [0.7, 0.0],
	"lamp": [0.0, 0.0]}


var _fl_buf := PackedFloat32Array()  # (prepared on a worker: _lights_prep) the flares' and pools' MultiMesh buffers
var _pl_buf := PackedFloat32Array()
var _pgroups: Array = []             # (prepared on a worker: _plants_prep) [species, centre, buffer, count]


func _lights_prep() -> void:
	## (a worker) which lights get a flare, which a pool -- the json "lights" [x, y, z, kind, "#rrggbb"]; with none, the
	## sign anchors stand in for flares
	var fl: Array = []
	var pools: Array = []
	var taken := {}
	for l in side.get("lights", []):
		var p := Vector3(l[0], l[1], l[2])
		var kind := str(l[3]) if l.size() > 3 else "lantern"
		var col := Color.html(str(l[4])) if l.size() > 4 else Color(1.0, 0.85, 0.6)
		var kv: Array = LIGHT_KIND.get(kind, [0.5, 2.8])
		if float(kv[0]) > 0.0:
			fl.append([p, float(kv[0]), col, float(kv[0]) - p.y * 0.01])
		if float(kv[1]) > 0.0:
			# the ground below: the floor of its storey (a lamp hangs ~2.5 m up), or the deck there
			var gy := maxf(isl.deck_y(p.x, p.z), floorf((p.y - 0.4) / STOREY) * STOREY)
			var cell := Vector3i(floori(p.x / 2.5), floori(gy), floori(p.z / 2.5))
			if p.y - gy < 6.0 and not taken.has(cell):           # (one pool per 2.5 m: overlapping pools blow out)
				taken[cell] = true
				pools.append([Vector3(p.x, gy + 0.07, p.z), float(kv[1]), col, -p.y])
	if fl.is_empty():
		for a in anchors():
			if str(a[0]).begins_with("sign_"):
				fl.append([Vector3(a[1], float(a[2]) + 0.4, a[3]), 0.7, Color(1.0, 0.85, 0.6), 0.7])
	# the brightest first and street level before rooftops; the pools lowest first
	fl = _top(fl, FLARES)
	pools = _top(pools, POOLS)
	_fl_buf = _mm_buf(fl, func(e): return Transform3D(Basis().scaled(Vector3.ONE * (0.6 + float(e[1]))), e[0]))
	_pl_buf = _mm_buf(pools, func(e): return Transform3D(Basis().scaled(Vector3(e[1], 1.0, e[1])), e[0]))


static func _top(list: Array, n: int) -> Array:
	## the n entries with the highest key (entry[3]): a plain sort of the keys, not a sort_custom over thousands
	if list.size() <= n:
		return list
	var keys := PackedFloat32Array()
	for e in list:
		keys.append(float(e[3]))
	keys.sort()
	var cut := keys[keys.size() - n]
	return list.filter(func(e): return float(e[3]) >= cut).slice(0, n)


func _mm_buf(pts: Array, xf_of: Callable) -> PackedFloat32Array:
	## a MultiMesh buffer (TRANSFORM_3D, colours, custom data: 20 floats an instance); custom r a phase, g the strength
	var buf := PackedFloat32Array()
	buf.resize(pts.size() * 20)
	var o := 0
	for i in pts.size():
		var t: Transform3D = xf_of.call(pts[i])
		var c: Color = pts[i][2]
		var vals := [t.basis.x.x, t.basis.y.x, t.basis.z.x, t.origin.x, t.basis.x.y, t.basis.y.y, t.basis.z.y, t.origin.y,
			t.basis.x.z, t.basis.y.z, t.basis.z.z, t.origin.z, c.r, c.g, c.b, 1.0,
			float(hash(i + id.hash()) % 1000) / 1000.0, float(pts[i][1]), 0.0, 0.0]
		for v in vals:
			buf[o] = v
			o += 1
	return buf


func _make_flares() -> void:
	## at night a glare sprite on each of the brightest lights within FLARE_M, and a pool of the light's colour on the
	## ground under each street light (two MultiMeshes) -- they make the night glitter and the lanes readable
	var near: Node = isl.get_node_or_null("Near")
	if near == null:
		return
	if not _fl_buf.is_empty():
		var q := QuadMesh.new()
		q.size = Vector2(1.0, 1.0)
		var m := ShaderMaterial.new()
		m.shader = FLARE_SH
		m.set_shader_parameter("range_m", FLARE_M)
		q.material = m
		_flare_mm = _light_mm(q, _fl_buf, "Flares", FLARE_M + 200.0)
		near.add_child(_flare_mm)
	if not _pl_buf.is_empty():
		var q2 := PlaneMesh.new()
		q2.size = Vector2(2.0, 2.0)
		var m2 := ShaderMaterial.new()
		m2.shader = POOL_SH
		m2.set_shader_parameter("range_m", POOL_M)
		q2.material = m2
		_pool_mm = _light_mm(q2, _pl_buf, "Pools", POOL_M + 60.0)
		near.add_child(_pool_mm)


func _light_mm(mesh: Mesh, buf: PackedFloat32Array, nm: String, end: float) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.use_custom_data = true
	mm.mesh = mesh
	mm.instance_count = buf.size() / 20
	mm.buffer = buf
	var mi := MultiMeshInstance3D.new()
	mi.name = nm
	mi.multimesh = mm
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.visibility_range_end = end
	mi.visible = _visible
	return mi


# ------------------------------------------------------------------ plants (SkyPlants, r4 §6)
const PLANT_M := 180.0
var _plants: Array = []              # [instance, multimesh, species, count]


func _plants_prep() -> void:
	## (a worker) the .bin's foliage ([species, x, y, z, rot, scale]) grouped one MultiMesh per species per quadrant (4 x 4
	## chunks), its instances about the quadrant's centre, and the species' meshes built
	var fol: Array = head.get("foliage", [])
	var span := CELL * CH * 4.0
	var by := {}                         # Vector3i(species, gi, gj) -> [[Transform3D, tint, custom]]
	var occ := {}                        # level -> rows (the twin json's lattice: '#' a room)
	for lv in side.get("levels", []):
		occ[int(lv.level)] = lv.rows
	for f in fol:
		var sp := str(head.species[int(f[0])]) if int(f[0]) < (head.species as Array).size() else "shrub"
		var p := Vector3(f[1], f[2], f[3])
		var yaw: float = f[4]
		var ci := floori((p.x - float(head.x0)) / CELL)
		var cj := floori((p.z - float(head.z0)) / CELL)
		var rows: Array = occ.get(roundi(p.y / STOREY), [])
		var inside := ci >= 0 and ci < rows.size() and cj >= 0 and cj < str(rows[ci]).length() and str(rows[ci])[cj] == "#"
		if inside or (rows.is_empty() and SkyPlants.WALL_HUNG.has(sp)):
			# on a lane wall (civ foliage "lane_wall"): the generator gives the house cell (scattered in it -- inside a
			# room, which is how it is told) and the face as its rot 0..3 (in radians): out onto that face, facing out
			# (tools/sky/warren/pick.py FACE: 0 -Z, 1 -X, 2 +Z, 3 +X)
			var face := posmod(roundi(yaw), 4)
			var dir: Vector3 = [Vector3(0, 0, -1), Vector3(-1, 0, 0), Vector3(0, 0, 1), Vector3(1, 0, 0)][face]
			var cx := float(head.x0) + CELL * floorf((p.x - float(head.x0)) / CELL) + 1.5
			var cz := float(head.z0) + CELL * floorf((p.z - float(head.z0)) / CELL) + 1.5
			var along := Vector3(dir.z, 0, -dir.x) * ((p.x - cx) * dir.z - (p.z - cz) * dir.x) * 0.5
			p = Vector3(cx, p.y, cz) + dir * 1.5 + along
			yaw = atan2(dir.x, dir.z)
		var sc: float = f[5]
		var h := absi(hash(Vector3i(roundi(p.x * 10), roundi(p.y * 10), roundi(p.z * 10))))
		var tint := Color.from_hsv(0.0, 0.0, 0.9 + float(h % 97) / 97.0 * 0.2).lerp(Color(1.0, 0.95, 0.8), float(h / 97 % 7) / 7.0 * 0.25)
		var key := Vector3i(int(f[0]), floori((p.x - float(head.x0)) / span), floori((p.z - float(head.z0)) / span))
		if not by.has(key):
			by[key] = []
		by[key].append([Transform3D(Basis(Vector3.UP, yaw).scaled(Vector3.ONE * sc), p), tint,
			Color(float(h % 1000) / 1000.0, fposmod(yaw / TAU, 1.0), 0, 0)])
	for key: Vector3i in by:
		var list: Array = by[key]
		var sp := str(head.species[key.x]) if key.x < (head.species as Array).size() else "shrub"
		var cen := Vector3.ZERO
		for e in list:
			cen += (e[0] as Transform3D).origin
		cen /= list.size()
		cen.y = 0.0
		var buf := PackedFloat32Array()
		buf.resize(list.size() * 20)
		var o := 0
		for e in list:
			var t: Transform3D = e[0]
			t.origin -= cen
			var c: Color = e[1]
			var u: Color = e[2]
			for v in [t.basis.x.x, t.basis.y.x, t.basis.z.x, t.origin.x, t.basis.x.y, t.basis.y.y, t.basis.z.y, t.origin.y,
					t.basis.x.z, t.basis.y.z, t.basis.z.z, t.origin.z, c.r, c.g, c.b, 1.0, u.r, u.g, u.b, u.a]:
				buf[o] = v
				o += 1
		SkyPlants.arrays(sp)                 # (the species' mesh: built here, off the main thread)
		_pgroups.append([sp, cen, buf, list.size()])


func _make_plants() -> void:
	for g in _pgroups:
		var sp: String = g[0]
		var cen: Vector3 = g[1]
		var mm := RenderingServer.multimesh_create()
		RenderingServer.multimesh_allocate_data(mm, int(g[3]), RenderingServer.MULTIMESH_TRANSFORM_3D, true, true)
		RenderingServer.multimesh_set_mesh(mm, SkyPlants.mesh(sp).get_rid())
		RenderingServer.multimesh_set_buffer(mm, g[2])
		var inst := RenderingServer.instance_create2(mm, _scenario)
		RenderingServer.instance_geometry_set_visibility_range(inst, 0.0, PLANT_M, 0.0, 20.0,
			RenderingServer.VISIBILITY_RANGE_FADE_DISABLED)
		RenderingServer.instance_geometry_set_cast_shadows_setting(inst, RenderingServer.SHADOW_CASTING_SETTING_ON
			if SkyPlants.SHADOWS.has(sp) else RenderingServer.SHADOW_CASTING_SETTING_OFF)
		RenderingServer.instance_set_visible(inst, false)
		_plants.append([inst, mm, sp, int(g[3])])
		_entry(inst, cen, cen + RenderingServer.multimesh_get_aabb(mm).get_center(), 0.0, PLANT_M)


# ------------------------------------------------------------------ the islanders' graph (SkyFolk)
var folk_graph := {}                 # {nodes: PackedVector2Array (x, z), ys, adj, bridge_node} -- SkyFolk._graph's shape


func _walk_prep() -> void:
	## (a worker) the walk graph as SkyFolk walks it, and the node nearest each bridge's foot
	var w: Dictionary = walk()
	var nodes := PackedVector2Array()
	var ys := PackedFloat32Array()
	var adj: Array = []
	for n in w.get("nodes", []):
		nodes.append(Vector2(n[0], n[2]))
		ys.append(float(n[1]))
		adj.append([])
	for e in w.get("edges", []):
		adj[e[0]].append(e[1])
		adj[e[1]].append(e[0])
	var bn := {}
	var d: Dictionary = isl.data
	var f: Dictionary = d.get("faces", {})
	for b in d.get("bridges", []):
		var al: float = b.along
		var p: Vector2 = {"N": Vector2(f.N, al), "S": Vector2(f.S, al), "E": Vector2(al, f.E), "W": Vector2(al, f.W)}[b.side]
		var best := -1
		var bd := INF
		for k in nodes.size():
			var dd := nodes[k].distance_squared_to(p)
			if dd >= bd or ys[k] > isl.deck_y(nodes[k].x, nodes[k].y) + 1.0:
				continue                                  # (a bridge lands on the deck: ground-level nodes only)
			if dd < bd:
				bd = dd
				best = k
		if best >= 0 and bd < 225.0:
			bn["%s:%.2f" % [b.side, al]] = best
	folk_graph = {"nodes": nodes, "adj": adj, "bridge_node": bn, "ys": ys}


func stats() -> Dictionary:
	var tris := 0
	var draws := 0
	for c in chunks:
		draws += int(c.get("surfs0", 0))
		tris += int(c.get("tris0", 0))
	var mu := 0
	var mx := 0
	for u in merge_usec:
		mu += int(u)
		mx = maxi(mx, int(u))
	return {"chunks": chunks.size(), "built": built, "built_ms": built_ms, "merge_ms_avg": mu / 1000.0 / maxf(1, merge_usec.size()),
		"merge_ms_max": mx / 1000.0, "variants": _vlocal.size(), "lod0_tris": tris, "lod0_surfaces": draws, "groups": groups.size(),
		"ready": ready, "plants": _plants.size(), "active": _act_rid.size(), "entries": _ents.size(), "place_us": place_usec}

extends Node3D
class_name SkyMooringSite

## One market's mooring, on the floor and in the air (research/flea_markets/00_plan.md §5.2-5.6; handoff_sky.md):
##   CREW_DOWN  the drop cage on the davit's hoist line, 24 aboard (12 m/s: the crews' expert drop)
##   ANCHOR     the hawsers, one by one, from the line houses to the deadmen (the host's also to the masts' heads)
##   LOGISTICS  the Mooring Office, the Weigh House, the Crew Tent (and a crew tent per ground follower)
##   RIGGING    the ground stations bolted on their plinths, then the track and haul ropes
##   SERVICE    the jig-back: two cabins per ropeway, counterweighted (one up while the other comes down), 8 m/s,
##              ~85 s a trip and a dwell at each end; 28 aboard and a warden; cargo cabins 07:00-19:00 only (after
##              hours: people only); the cabins stop in a wind over SkyMooring.WIND_LIMIT
##   FAIR       (3+ in service) the trading tents on the market's tent slots, ring by ring, over three hours; their
##              festoons, poles and lanterns; Bright Week (5+): the Skein lights strung over every lot row and aisle
##              and the Lantern Top; the Sky Holiday (7+, towns and villages): the same, brighter
##   STRIKE / CAST_OFF   tents down, the crew up last, the hawsers slipped
## The player rides: a passenger cabin is a moving platform (AnimatableBody3D, its frame boxes and doors), carrying
## whoever stands in it (StationPlayer.carrier_velocity); board at the ground berth, alight at the island's.
##
## Draws: the static chunks (64 m) in ONE vertex-coloured material (the kit's groups as emission in the colour's
## alpha: emissive 2.0, glow 0.9, canvas 0.35 at night) plus the atlas groups; the bulbs one MultiMesh; the ropes one
## line mesh; a cabin one draw (+ doors); the cage one.

const CHUNK := 64.0
const NEAR_R := 260.0
const MID_R := 1800.0
const SPEED := 8.0
const ACC := 1.0
const DWELL := 60.0
const DWELL_NIGHT := 120.0
const CAGE_SPEED := 12.0
const SAG := 0.015                  # of a span: the track ropes' sag at mid-span
const RIDE_R := 400.0               # cabins with collision within this of the player
const WARDEN_R := 120.0
const VENDOR_R := 70.0
const MAX_VENDORS := 18
const TENT_RAMP_H := 3.0            # game hours the tents take to go up
const TENT_DOWN_H := 2.0
const FOLK_SEED := 7714
const BULB_COLS := [Color(1.0, 0.36, 0.33), Color(1.0, 0.82, 0.32), Color(0.36, 1.0, 0.48), Color(0.36, 0.7, 1.0),
	Color(1.0, 0.5, 0.95), Color(1.0, 0.93, 0.75)]
const LANTERNS := ["skein_lantern_pierced", "skein_lantern_fanous", "skein_lantern_paper", "skein_lantern_globe",
	"skein_lantern_star", "skein_lantern_bell"]
const SKY_GOODS := ["fm_goods_sky_knit", "fm_goods_sky_rope", "fm_goods_sky_lights", "fm_goods_sky_food",
	"fm_goods_sky_smoked", "fm_goods_sky_wonders", "fm_goods_sky_pets"]
const EMIT := {"emissive": 1.0, "glow": 0.45, "canvas": 0.175}

var sys: SkyIslands
var M: Dictionary
var market_id := ""
var lamps: Array = []               # [[world pos, Color, range, energy]] (the borrowed real lights)
var mem: Array = []                 # this tick's members at the market (see _eval)
var fair := false
var celebration := false
var holiday := false
var n_tents := 0

var _t := 0.0
var _rope_t := 0.0
var _key := ""
var _job := -1
var _mx := Mutex.new()
var _done: Variant = null
var _chunks := {}                   # Vector2i -> {node, key}
var _bulbs: MultiMeshInstance3D
var _lines: MeshInstance3D
var _wires: MeshInstance3D
var _ways := {}                     # "island:station" -> ropeway {T, G, gs xf, cabins: [cab, cab], cargo, phase0}
var _cages := {}                    # island index -> {node, line top, y}
var _props := {}                    # island index -> Node3D on the SkyIsland (the MID mooring pieces)
var _gbody: StaticBody3D            # the ground stations' collision
var _gbody_key := ""
var _people := {}                   # key -> {npc, anim, pid}
var _people_job := {}
var _tent_spots: Array = []         # [[world pos, facing, island id, key]] the vendors' spots this build
var _night := 0.0
var _released := false

static var _vc_mat: ShaderMaterial
static var _bulb_mat: ShaderMaterial
static var _line_mat: StandardMaterial3D
static var _wire_mat: StandardMaterial3D
static var _cab_mesh := {}          # "pax|<colour>" -> ArrayMesh
static var _warren_mid: Node
static var _prop_mat: StandardMaterial3D


func _ready() -> void:
	name = "Mooring_" + market_id
	process_physics_priority = -9
	FleaKit.load_all()
	_fix_kit()
	_mats()
	_lines = MeshInstance3D.new()
	_lines.name = "Ropes"
	_lines.mesh = ImmediateMesh.new()
	_lines.material_override = _line_mat
	_lines.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_lines)
	_wires = MeshInstance3D.new()
	_wires.name = "Wires"
	_wires.material_override = _wire_mat
	_wires.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_wires.visibility_range_end = 700.0
	add_child(_wires)


static var _kit_fixed := false


static func _fix_kit() -> void:
	## Godot's glTF import turns a node named "*_wheel" into a VehicleWheel3D (an import hint) and renames its mesh
	## child to the name less "_wheel": kit.glb's ground_station_wheel arrived as a second "ground_station" (2
	## surfaces) and FleaKit kept that one.  Re-read both glbs' MeshInstances here: a wheel's child under its own
	## name + "_wheel", the real piece under its own (requests.md S4)
	if _kit_fixed:
		return
	_kit_fixed = true
	for g in ["res://remake/markets/kit.glb", "res://remake/markets/kit_mid.glb"]:
		if not ResourceLoader.exists(g):
			continue
		var ps = load(g)
		if not (ps is PackedScene):
			continue
		var kr: Node = (ps as PackedScene).instantiate()
		for n in kr.find_children("*", "VehicleWheel3D", true, false):
			for c in n.get_children():
				if c is MeshInstance3D:
					var mi := c as MeshInstance3D
					FleaKit._mesh["%s|%s_wheel" % [g, str(mi.name)]] = _surfs(mi, (n as Node3D).transform * mi.transform)
					# (and the piece it shadowed: the plain MeshInstance of that name)
					var real := kr.find_child(str(mi.name), false, false) as MeshInstance3D
					if real:
						FleaKit._mesh["%s|%s" % [g, str(mi.name)]] = _surfs(real, real.transform)
		kr.free()


static func _surfs(mi: MeshInstance3D, xf: Transform3D) -> Array:
	var surfs: Array = []
	var mesh: Mesh = mi.mesh
	for si in mesh.get_surface_count():
		var mat := mesh.surface_get_material(si)
		var slot := str(mat.resource_name).trim_prefix("mk_") if mat else "wall"
		var a := mesh.surface_get_arrays(si)
		var v: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
		var nn: PackedVector3Array = a[Mesh.ARRAY_NORMAL] if a[Mesh.ARRAY_NORMAL] != null else PackedVector3Array()
		var c: PackedColorArray = a[Mesh.ARRAY_COLOR] if a[Mesh.ARRAY_COLOR] != null else PackedColorArray()
		var uv: PackedVector2Array = a[Mesh.ARRAY_TEX_UV] if a[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
		var idx: PackedInt32Array = a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
		if xf != Transform3D.IDENTITY:
			for i in v.size():
				v[i] = xf * v[i]
			for i in nn.size():
				nn[i] = (xf.basis * nn[i]).normalized()
		surfs.append([slot, v, nn, c, uv, idx])
	return surfs


static func _mats() -> void:
	if _vc_mat:
		return
	var sh := Shader.new()
	sh.code = """shader_type spatial;
render_mode cull_back;
uniform float night = 0.0;
varying vec3 vcol;
varying float vem;
vec3 lin(vec3 c) { return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c)); }
void vertex() { vcol = lin(COLOR.rgb); vem = COLOR.a; }
void fragment() {
	ALBEDO = vcol;
	ROUGHNESS = 0.8;
	EMISSION = vcol * vem * 2.0 * night;
}"""
	_vc_mat = ShaderMaterial.new()
	_vc_mat.shader = sh
	var bs := Shader.new()
	bs.code = """shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
uniform float night = 0.0;
varying vec3 col;
void vertex() {
	col = COLOR.rgb;
	// a camera-facing bulb (the MultiMesh's own scale is its size)
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0), vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, 1.0, 0.0), vec4(0.0, 0.0, 0.0, 1.0));
}
void fragment() {
	float d = length(UV - vec2(0.5)) * 2.0;
	if (d > 1.0) { discard; }
	float core = 1.0 - smoothstep(0.0, 1.0, d);
	ALBEDO = col * mix(0.55, 2.4, night) * (0.6 + 0.4 * core);
}"""
	_bulb_mat = ShaderMaterial.new()
	_bulb_mat.shader = bs
	_line_mat = StandardMaterial3D.new()
	_line_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_line_mat.albedo_color = Color(0.16, 0.15, 0.14)
	_wire_mat = StandardMaterial3D.new()
	_wire_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_wire_mat.albedo_color = Color(0.1, 0.1, 0.1)
	_prop_mat = StandardMaterial3D.new()
	_prop_mat.vertex_color_use_as_albedo = true
	_prop_mat.albedo_color = Color(0.92, 0.86, 0.76)
	_prop_mat.roughness = 0.85


func idle() -> bool:
	return mem.is_empty() and _chunks.is_empty() and _ways.is_empty()


func release() -> void:
	_released = true
	if _job >= 0:
		WorkerThreadPool.wait_for_task_completion(_job)
		_job = -1
	for i in _props:
		if is_instance_valid(_props[i]):
			(_props[i] as Node).queue_free()
	_props.clear()
	for k in _people:
		if is_instance_valid(_people[k].npc):
			(_people[k].npc as Node).queue_free()
	_people.clear()
	if sys and sys.player:
		sys.player.sheltered = false


func _exit_tree() -> void:
	if not _released:
		release()


# ------------------------------------------------------------------ the state (from the calendar and the layout)
func _eval(T: float) -> void:
	var mo := sys.drift.mooring
	mem.clear()
	for i in mo.at_market(market_id):
		var st: Dictionary = mo.members[i]
		var rec: Dictionary = st.layout.members[int(st.k)]
		mem.append({"i": i, "st": st, "rec": rec, "phase": str(st.phase), "A": float(st.e.arrive),
			"S": float(st.e.service), "Lv": float(st.e.leave), "ground": bool(st.ground), "k": int(st.k),
			"id": str(rec.island)})
	mem.sort_custom(func(a, b) -> bool: return a.k < b.k)
	var day := floori(T / 24.0)
	var ins := 0
	for m in mem:
		if m.S <= T and T < m.Lv:
			ins += 1
	fair = ins >= FleaCalendar.FAIR_N
	holiday = FleaCalendar.is_holiday(M, day)
	celebration = holiday or FleaCalendar.is_celebration(M, day)


func _fair_window(T: float) -> Vector2:
	## the interval round T with 3 or more in service (Vector2.INF if none)
	var ev: Array = []
	for m in mem:
		ev.append([m.S, 1])
		ev.append([m.Lv, -1])
	ev.sort_custom(func(a, b) -> bool: return a[0] < b[0])
	var n := 0
	var start := INF
	for e in ev:
		var was := n
		n += int(e[1])
		if was < FleaCalendar.FAIR_N and n >= FleaCalendar.FAIR_N:
			start = float(e[0])
		elif was >= FleaCalendar.FAIR_N and n < FleaCalendar.FAIR_N:
			if start <= T and T < float(e[0]):
				return Vector2(start, float(e[0]))
			start = INF
	if start <= T:
		return Vector2(start, start + 24.0 * 21.0)
	return Vector2.INF


func _elements(T: float) -> Dictionary:
	## what stands on the floor now: {gs: [[island, station rec]], lt: [[piece, slot k, island]], tents: n, cel: bool}
	var out := {"gs": [], "lt": [], "tents": 0, "cel": celebration}
	var nl := 0
	for m in mem:
		var rec: Dictionary = m.rec
		if not m.ground:
			continue
		var dt: float = T - m.A
		if T < m.Lv:
			# the logistics tents: the host's three, a crew tent per ground follower
			var kinds: Array = ["tent_logistics_office", "tent_logistics_weigh", "tent_logistics_crew"] if m.k == 0 \
				else ["tent_logistics_crew"]
			for j in kinds.size():
				if dt >= SkyMooring.PH.LOGISTICS + 0.6 * j:
					out.lt.append([kinds[j], nl, m.id])
				nl += 1
			if dt >= SkyMooring.PH.RIGGING + 0.5:
				for sp in _specs(m):
					out.gs.append([m.id, sp.key])
	var fw := _fair_window(T)
	if fw.is_finite():
		var want := 0
		for m in mem:
			if m.S <= T and T < m.Lv:
				want += 6 + 3 * int(FleaData.island(m.id).get("blocks", 3))
		var slots: int = (M.get("tent_slots", []) as Array).size()
		want = mini(want, slots)
		var up_f := clampf((T - fw.x) / TENT_RAMP_H, 0.0, 1.0)
		var down_f := clampf((fw.y - T) / TENT_DOWN_H, 0.0, 1.0)
		out.tents = int(floor(want * minf(up_f, down_f)))
	n_tents = out.tents
	return out


# ------------------------------------------------------------------ every frame
func _process(delta: float) -> void:
	if sys == null or _released:
		return
	_t -= delta
	_mx.lock()
	var d = _done
	_done = null
	_mx.unlock()
	if d != null:
		_commit(d)
	if _t <= 0.0:
		_t = 0.5
		Prof.begin("moor.tick")
		var T := sys.sky.now_hours() if sys.sky else 0.0
		_eval(T)
		var dl: float = sys.sky.daylight() if sys.sky and sys.sky.has_method("daylight") else 1.0
		_night = clampf((0.78 - dl) / 0.45, 0.0, 1.0)
		_vc_mat.set_shader_parameter("night", _night)
		_bulb_mat.set_shader_parameter("night", _night)
		var el := _elements(T)
		var key := JSON.stringify(el)
		if key != _key and _job < 0:
			_key = key
			var job := {"el": el, "T": T, "mem": _mem_snapshot()}
			_job = WorkerThreadPool.add_task(_build.bind(job), true, "mooring site " + market_id)
		_ways_update(T)
		_island_props()
		_people_step()
		Prof.end("moor.tick")
	_rope_t -= delta
	if _rope_t <= 0.0:
		_rope_t = 0.1
		_draw_ropes()


func _mem_snapshot() -> Array:
	var out: Array = []
	for m in mem:
		var isl: SkyIsland = sys.islands[m.i]
		out.append({"i": m.i, "id": m.id, "rec": m.rec, "k": m.k, "ground": m.ground, "xf": isl.global_transform})
	return out


# ------------------------------------------------------------------ the static chunks (a worker)
class Chunk:
	var c: Vector2
	var h: float
	var bas: Basis
	var org: Vector3
	var acc := {}                      # the kit's full pieces by group
	var mid := {}                      # their MID pieces
	var ids: Array = []                # what's in it (its key)
	var boxes: Array = []              # [Transform3D local, Vector3 size]
	var ramps := PackedVector3Array()   # triangles (local)

	func _init(cc: Vector2) -> void:
		c = cc
		h = MapTerrain.elevation(cc.x, cc.y)
		bas = StationGeo.basis(cc.x)
		org = StationGeo.point(cc.x, cc.y, h)

	func local(s: float, x: float, hh: float) -> Vector3:
		return Vector3(x - c.y, hh - h, -StationGeo.wrap_ds(s - c.x))


func _chunk_of(chunks: Dictionary, p: Vector2) -> Chunk:
	var k := Vector2i(floori(p.x / CHUNK), floori(p.y / CHUNK))
	if not chunks.has(k):
		chunks[k] = Chunk.new(Vector2((k.x + 0.5) * CHUNK, (k.y + 0.5) * CHUNK))
	return chunks[k]


func _site_dir(u: float, v: float) -> Vector3:
	var a := float((M.frame as Dictionary).get("yaw", 0.0))
	var ds := u * cos(a) - v * sin(a)
	var dx := u * sin(a) + v * cos(a)
	return Vector3(dx, 0.0, -ds)


func _at(chunks: Dictionary, sx: Vector2, fwd: Vector3) -> Array:
	## [chunk, Transform3D in it] of a piece standing at (s, x) with its +z along fwd (a chunk-frame direction)
	var ch := _chunk_of(chunks, sx)
	var p := ch.local(sx.x, sx.y, MapTerrain.elevation(sx.x, sx.y))
	var f := fwd.normalized()
	var r := Vector3.UP.cross(f).normalized()
	return [ch, Transform3D(Basis(r, Vector3.UP, f), p)]


func _put(ch: Chunk, piece: String, xf: Transform3D, variant := 0, over := {}, collide := false, dress := true) -> void:
	if not FleaKit.has(piece):
		return
	FleaKit.put(ch.acc, piece, xf, variant, over, false)
	if str(FleaKit.info(piece).get("lod1", "drop")) == "keep":
		FleaKit.put(ch.mid, piece, xf, variant, over, true)
	if collide:
		for b in FleaKit.info(piece).get("frame", []):
			var lo := Vector3(float(b[0][0]), float(b[0][1]), float(b[0][2]))
			var hi := Vector3(float(b[1][0]), float(b[1][1]), float(b[1][2]))
			ch.boxes.append([xf * Transform3D(Basis(), (lo + hi) * 0.5), hi - lo])
		for q in FleaKit.info(piece).get("ramps", []):
			var pts: Array = []
			for p in q:
				pts.append(xf * Vector3(float(p[0]), float(p[1]), float(p[2])))
			ch.ramps.append_array(PackedVector3Array([pts[0], pts[1], pts[2], pts[0], pts[2], pts[3]]))
	if dress:
		for dd in FleaKit.info(piece).get("dress", []):
			var dx := Transform3D(Basis(Vector3.UP, deg_to_rad(float(dd[4]))), Vector3(float(dd[1]), float(dd[2]), float(dd[3])))
			_put(ch, str(dd[0]), xf * dx, variant, over, false, false)


func _clan(iid: String) -> Dictionary:
	## an island's clan colours on a tent: alternating gores, the lining its first colour darkened
	var cs: Array = FleaData.island(iid).get("colors", [])
	if cs.is_empty():
		return {}
	var a := Color(str(cs[0]))
	var b := Color(str(cs[1 % cs.size()]))
	var c := Color(str(cs[2 % cs.size()]))
	if c.get_luminance() < 0.2:
		c = a.lightened(0.45)
	return {"canvas_a": "#" + a.to_html(false), "canvas_b": "#" + b.to_html(false), "canvas_c": "#" + c.to_html(false),
		"lining": "#" + a.darkened(0.35).to_html(false), "accent": "#" + a.to_html(false)}


func _field_slots() -> Array:
	## the logistics tents' places on the mooring field (u, v, yaw), nearest its middle first: a 9.6 x 15.4 m tent
	## (long along v) clear of the deadmen (3 m), the masts (6 m), the ground-station plinths (11 m) and each other
	var mf: Array = M.get("mooring", [])
	if mf.size() < 4:
		return []
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for p in mf:
		lo = Vector2(minf(lo.x, float(p[0])), minf(lo.y, float(p[1])))
		hi = Vector2(maxf(hi.x, float(p[0])), maxf(hi.y, float(p[1])))
	var c := (lo + hi) * 0.5
	var busy: Array = []
	for d in M.get("deadmen", []):
		busy.append([Vector2(float(d[0]), float(d[1])), 3.0])
	for d in M.get("masts", []):
		busy.append([Vector2(float(d[0]), float(d[1])), 6.0])
	for d in M.get("stations", []):
		busy.append([Vector2(float(d[0]), float(d[1])), 11.0])
	var cands: Array = []
	var u := lo.x + 5.0
	while u <= hi.x - 5.0:
		var v := lo.y + 8.0
		while v <= hi.y - 8.0:
			cands.append(Vector2(u, v))
			v += 2.5
		u += 2.5
	cands.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.distance_squared_to(c) < b.distance_squared_to(c))
	var out: Array = []
	var hx := 4.8
	var hz := 7.7
	for p: Vector2 in cands:
		var ok := true
		for b in busy:
			var q: Vector2 = b[0]
			var dx := maxf(absf(q.x - p.x) - hx, 0.0)
			var dz := maxf(absf(q.y - p.y) - hz, 0.0)
			if Vector2(dx, dz).length() < float(b[1]):
				ok = false
				break
		if ok:
			for o in out:
				if absf(float(o[0]) - p.x) < hx * 2.0 + 2.0 and absf(float(o[1]) - p.y) < hz * 2.0 + 2.0:
					ok = false
					break
		if ok:
			# (the door, +z, toward the market side of the field: -v)
			out.append([p.x, p.y, PI])
		if out.size() >= 8:
			break
	return out


func _build(job: Dictionary) -> void:
	var chunks := {}
	var bulbs: Array = []              # [world pos, Color, size]
	var wires: Array = []              # world segment pairs
	var lamps_: Array = []
	var spots: Array = []
	var el: Dictionary = job.el
	var memo := {}
	for m in job.mem:
		memo[m.id] = m
	# -- ground stations
	for g in el.gs:
		var m: Dictionary = memo.get(g[0], {})
		if m.is_empty():
			continue
		for sp in _specs(m):
			if str(sp.key) != str(g[1]):
				continue
			var G: Vector2 = sp.G
			var yaw := float(sp.gyaw)
			# (the station's +x toward the island: ring direction (ds, dx) = (sin yaw, cos yaw) -> chunk (dx, 0, -ds))
			var d := Vector3(cos(yaw), 0.0, -sin(yaw))
			var P := _at(chunks, G, d)
			var ch: Chunk = P[0]
			var xf: Transform3D = P[1]
			xf.basis = Basis(d, Vector3.UP, d.cross(Vector3.UP))
			_put(ch, "ground_station", xf, 0, _clan(str(g[0])), true)
			_put(ch, "ground_station_wheel", xf * FleaKit.anchor("ground_station", "bull_wheel"), 0, {}, false)
			ch.ids.append("gs:" + str(g[1]))
			var wp := ch.bas * (xf * Vector3(2.0, 3.2, 0.0)) + ch.org
			lamps_.append([wp, Color(1.0, 0.85, 0.62), 16.0, 1.2])
	# -- logistics tents
	var fs := _field_slots()
	for lt in el.lt:
		var k := int(lt[1])
		if k >= fs.size():
			continue
		var fsl: Array = fs[k]
		var w := FleaData.to_world(M, float(fsl[0]), float(fsl[1]))
		var P2 := _at(chunks, w, _site_dir(sin(float(fsl[2])), cos(float(fsl[2]))))
		var ch2: Chunk = P2[0]
		_put(ch2, str(lt[0]), P2[1], 0, {}, true)
		ch2.ids.append("lt:%d:%s" % [k, lt[0]])
	# -- the trading tents, ring by ring
	var slots: Array = M.get("tent_slots", [])
	var ord: Array = range(slots.size())
	ord.sort_custom(func(a, b) -> bool: return int(slots[a][4]) < int(slots[b][4]) or (int(slots[a][4]) == int(slots[b][4]) and a < b))
	var owners: Array = []
	for m in job.mem:
		owners.append(m.id)
	var hid := int(M.get("hid", 0))
	var tents_at: Array = []           # [world front point (a pole spot), ring, slot index]
	for n in mini(int(el.tents), ord.size()):
		var si: int = ord[n]
		var sl: Array = slots[si]
		var iid: String = owners[n % maxi(owners.size(), 1)] if not owners.is_empty() else ""
		var u := float(sl[0])
		var v := float(sl[1])
		var yw := float(sl[2])
		var big := int(sl[3]) >= 9
		var r := FleaData.u(hid, si, 71)
		var piece := "tent_event_9" if big else ("tent_canopy_striped" if r < 0.25 else "tent_bazaar_6")
		var w2 := FleaData.to_world(M, u, v)
		var f := _site_dir(sin(yw), cos(yw))
		var P3 := _at(chunks, w2, f)
		var ch3: Chunk = P3[0]
		var xf3: Transform3D = P3[1]
		var over := _clan(iid)
		_put(ch3, piece, xf3, int(r * 7.0), over, true)
		ch3.ids.append("t:%d" % si)
		# goods on its shelves (the island's trade), its lanterns, its vendors
		for dd in FleaKit.info(piece).get("dress", []):
			if str(dd[0]) == "tent_shelf":
				var sx := xf3 * Transform3D(Basis(Vector3.UP, deg_to_rad(float(dd[4]))), Vector3(float(dd[1]), float(dd[2]), float(dd[3])))
				for gk in ["g0", "g1", "g2", "g3"]:
					var gp: String = SKY_GOODS[int(FleaData.u(hid, si, gk.hash()) * SKY_GOODS.size())]
					_put(ch3, gp, sx * FleaKit.anchor("tent_shelf", gk), 0, {}, false, false)
		var half := 4.6 if big else 3.1
		var front := xf3 * Vector3(0.0, 0.0, half + 0.4)
		var lan: String = LANTERNS[int(r * 997.0) % LANTERNS.size()]
		_put(ch3, lan, xf3 * Transform3D(Basis(), Vector3(-half + 0.4, 2.45, half + 0.15)), 0, over, false, false)
		_put(ch3, lan, xf3 * Transform3D(Basis(), Vector3(half - 0.4, 2.45, half + 0.15)), 0, over, false, false)
		var wl := ch3.bas * (xf3 * Vector3(0.0, 2.3, half)) + ch3.org
		lamps_.append([wl, Color(1.0, 0.78, 0.5), 9.0, 0.9])
		for vk in ["vendor_0", "vendor_1", "vendor_2"]:
			var an := FleaKit.anchor(piece, vk)
			if an == Transform3D.IDENTITY:
				continue
			var vx := xf3 * an
			spots.append([ch3.bas * vx.origin + ch3.org, ch3.bas * (vx.basis.z), iid, "%d:%s" % [si, vk]])
		tents_at.append([ch3.bas * front + ch3.org, int(sl[4]), si, ch3.bas * (xf3.basis.x)])
	# -- the strings of lights: a pole between neighbouring tents, festoons from pole to pole, a lantern mid-span
	var poles: Array = []
	for k in tents_at.size():
		var a: Array = tents_at[k]
		var pw: Vector3 = a[0]
		var right: Vector3 = a[3]
		for sd in [-1.0, 1.0]:
			poles.append([pw + right * sd * 3.4, a[1], a[2]])
	var pk: Array = []
	for p in poles:
		var dup := false
		for q in pk:
			if (q[0] as Vector3).distance_to(p[0]) < 1.2:
				dup = true
				break
		if not dup:
			pk.append(p)
	poles = pk
	for k in poles.size():
		var p: Array = poles[k]
		var wpos: Vector3 = p[0]
		var sx2 := Vector2(StationGeo.s_of(wpos), wpos.x)
		var Pp := _at(chunks, sx2, Vector3.FORWARD)
		_put(Pp[0], "festoon_pole", Pp[1], 0, {}, false, false)
	var hooks: Array = []
	for p in poles:
		var wpos2: Vector3 = p[0]
		var up := StationGeo.up(StationGeo.s_of(wpos2))
		var g2 := StationGeo.point(StationGeo.s_of(wpos2), wpos2.x, MapTerrain.elevation(StationGeo.s_of(wpos2), wpos2.x))
		hooks.append([g2 + up * 4.6, p[1], p[2]])
	for k in hooks.size():
		for k2 in range(k + 1, mini(k + 4, hooks.size())):
			var A: Vector3 = hooks[k][0]
			var B: Vector3 = hooks[k2][0]
			var L := A.distance_to(B)
			if L < 1.0 or L > 14.0 or hooks[k][1] != hooks[k2][1]:
				continue
			_festoon(A, B, 0.07, bulbs, wires, hid + k)
			# a lantern at the middle of the longer spans
			if L > 5.0:
				var mpt := (A + B) * 0.5 - StationGeo.up(StationGeo.s_of(A)) * L * 0.07
				var ch4 := _chunk_of(chunks, Vector2(StationGeo.s_of(mpt), mpt.x))
				var lp := ch4.bas.inverse() * (mpt - ch4.org)
				_put(ch4, LANTERNS[(k + k2) % LANTERNS.size()], Transform3D(Basis(), lp), 0, {}, false, false)
			break
	# -- Bright Week / the Sky Holiday: the Skein's lights over every lot row and aisle, and the Lantern Top
	if el.cel:
		var lot: Dictionary = M.get("lot", {})
		for row in lot.get("rows", []):
			var u0 := float(row[0])
			var u1 := float(row[1])
			var vv := float(row[2])
			var nseg := maxi(1, int((u1 - u0) / 9.0))
			for s_ in nseg:
				var a2 := _uv_world(lerpf(u0, u1, float(s_) / nseg), vv, 6.0)
				var b2 := _uv_world(lerpf(u0, u1, float(s_ + 1) / nseg), vv, 6.0)
				_festoon(a2, b2, 0.05, bulbs, wires, s_ + int(vv * 10.0))
		for ln in M.get("lanes", []):
			var lu0 := float(ln[0])
			var lv0 := float(ln[1])
			var lu1 := float(ln[2])
			var lv1 := float(ln[3])
			var along_u := absf(lu1 - lu0) >= absf(lv1 - lv0)
			var a3 := _uv_world(lu0, (lv0 + lv1) * 0.5, 4.6) if along_u else _uv_world((lu0 + lu1) * 0.5, lv0, 4.6)
			var b3 := _uv_world(lu1, (lv0 + lv1) * 0.5, 4.6) if along_u else _uv_world((lu0 + lu1) * 0.5, lv1, 4.6)
			var L3 := a3.distance_to(b3)
			var nseg2 := maxi(1, int(L3 / 9.0))
			for s_ in nseg2:
				_festoon(a3.lerp(b3, float(s_) / nseg2), a3.lerp(b3, float(s_ + 1) / nseg2), 0.05, bulbs, wires, s_ + 7)
		var ap: Array = M.get("apron", [])
		if not ap.is_empty() and (int(el.tents) > 0):
			var poly: Array = ap[0]
			var lo := Vector2(INF, INF)
			var hi := Vector2(-INF, -INF)
			for p in poly:
				lo = Vector2(minf(lo.x, float(p[0])), minf(lo.y, float(p[1])))
				hi = Vector2(maxf(hi.x, float(p[0])), maxf(hi.y, float(p[1])))
			if hi.x - lo.x >= 26.0 or hi.y - lo.y >= 26.0:
				var cc := (lo + hi) * 0.5
				var P5 := _at(chunks, FleaData.to_world(M, cc.x, cc.y), _site_dir(1.0, 0.0) if hi.x - lo.x < hi.y - lo.y else _site_dir(0.0, 1.0))
				_put(P5[0], "tent_lantern_top", P5[1], 0, _clan(owners[0] if not owners.is_empty() else ""), true)
				(P5[0] as Chunk).ids.append("lantern_top")
	# -- out of the accumulators: one vertex-coloured surface (+ the atlas groups) per chunk and tier
	var out := {}
	for k in chunks:
		var ch: Chunk = chunks[k]
		ch.ids.sort()
		out[k] = {"key": ",".join(ch.ids) + "|%d|%d" % [ch.boxes.size(), (ch.acc.get("solid", [PackedVector3Array()])[0] as PackedVector3Array).size()],
			"xf": Transform3D(ch.bas, ch.org), "near": _merge(ch.acc), "mid": _merge(ch.mid), "boxes": ch.boxes,
			"ramps": ch.ramps}
	_mx.lock()
	_done = {"chunks": out, "bulbs": bulbs, "wires": wires, "lamps": lamps_, "spots": spots}
	_mx.unlock()


func _uv_world(u: float, v: float, hh: float) -> Vector3:
	var w := FleaData.to_world(M, u, v)
	return StationGeo.point(w.x, w.y, MapTerrain.elevation(w.x, w.y) + hh)


func _festoon(A: Vector3, B: Vector3, sag: float, bulbs: Array, wires: Array, seed_: int) -> void:
	## a catenary string of bulbs (one every 0.6 m), the Skein's colours in turn, and its wire
	var L := A.distance_to(B)
	var n := maxi(2, int(L / 0.6))
	var up := StationGeo.up(StationGeo.s_of((A + B) * 0.5))
	var prev := A
	for k in range(n + 1):
		var t := float(k) / n
		var p := A.lerp(B, t) - up * (4.0 * t * (1.0 - t) * L * sag)
		if k > 0:
			wires.append(prev)
			wires.append(p)
		prev = p
		if k > 0 and k < n:
			bulbs.append([p - up * 0.1, BULB_COLS[(k + seed_) % BULB_COLS.size()], 0.16])


static func _merge(acc: Dictionary) -> Dictionary:
	## the kit's groups -> {"vc": arrays (emission in the colour's alpha), "<tex group>": arrays}
	var out := {}
	var vs := PackedVector3Array()
	var ns := PackedVector3Array()
	var cs := PackedColorArray()
	var ix := PackedInt32Array()
	for g in acc:
		var A: Array = acc[g]
		var v: PackedVector3Array = A[0]
		if v.is_empty():
			continue
		if str(g).begins_with("tex_"):
			var arr := []
			arr.resize(Mesh.ARRAY_MAX)
			arr[Mesh.ARRAY_VERTEX] = A[0]
			arr[Mesh.ARRAY_NORMAL] = A[1]
			arr[Mesh.ARRAY_COLOR] = A[2]
			arr[Mesh.ARRAY_TEX_UV] = A[3]
			arr[Mesh.ARRAY_INDEX] = A[4]
			out[g] = arr
			continue
		var em: float = EMIT.get(g, 0.0)
		var base := vs.size()
		vs.append_array(v)
		ns.append_array(A[1])
		var c: PackedColorArray = A[2]
		for q in c.size():
			c[q].a = em
		cs.append_array(c)
		for q in (A[4] as PackedInt32Array):
			ix.append(base + q)
	if not vs.is_empty():
		var arr2 := []
		arr2.resize(Mesh.ARRAY_MAX)
		arr2[Mesh.ARRAY_VERTEX] = vs
		arr2[Mesh.ARRAY_NORMAL] = ns
		arr2[Mesh.ARRAY_COLOR] = cs
		arr2[Mesh.ARRAY_INDEX] = ix
		out["vc"] = arr2
	return out


func _commit(d: Dictionary) -> void:
	if _job >= 0:
		WorkerThreadPool.wait_for_task_completion(_job)
		_job = -1
	var chunks: Dictionary = d.chunks
	for k in _chunks.keys():
		if not chunks.has(k):
			(_chunks[k].node as Node).queue_free()
			_chunks.erase(k)
	for k in chunks:
		var e: Dictionary = chunks[k]
		if _chunks.has(k) and str(_chunks[k].key) == str(e.key):
			continue
		if _chunks.has(k):
			(_chunks[k].node as Node).queue_free()
		var holder := Node3D.new()
		holder.name = "C_%d_%d" % [k.x, k.y]
		holder.transform = e.xf
		add_child(holder)
		for tier in ["near", "mid"]:
			for g in (e[tier] as Dictionary):
				var am := ArrayMesh.new()
				am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, e[tier][g])
				var mi := MeshInstance3D.new()
				mi.mesh = am
				mi.material_override = _vc_mat if g == "vc" else FleaKit.material(g)
				if tier == "near":
					mi.visibility_range_end = NEAR_R
				else:
					mi.visibility_range_begin = NEAR_R
					mi.visibility_range_end = MID_R
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if tier == "near" and g == "vc" \
					else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				holder.add_child(mi)
		if not (e.boxes as Array).is_empty() or not (e.ramps as PackedVector3Array).is_empty():
			var body := StaticBody3D.new()
			holder.add_child(body)
			for bx in e.boxes:
				var cs := CollisionShape3D.new()
				var sh := BoxShape3D.new()
				sh.size = (bx[1] as Vector3).abs() + Vector3(0.001, 0.001, 0.001)
				cs.shape = sh
				cs.transform = bx[0]
				body.add_child(cs)
			if not (e.ramps as PackedVector3Array).is_empty():
				var cs2 := CollisionShape3D.new()
				var cp := ConcavePolygonShape3D.new()
				cp.backface_collision = true
				cp.set_faces(e.ramps)
				cs2.shape = cp
				body.add_child(cs2)
		_chunks[k] = {"node": holder, "key": e.key}
	# the bulbs and their wires
	if _bulbs:
		_bulbs.queue_free()
		_bulbs = null
	var bl: Array = d.bulbs
	if not bl.is_empty():
		var q := QuadMesh.new()
		q.size = Vector2(1.0, 1.0)
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = q
		mm.instance_count = bl.size()
		for k in bl.size():
			var sz := float(bl[k][2])
			mm.set_instance_transform(k, Transform3D(Basis().scaled(Vector3(sz, sz, sz)), bl[k][0]))
			mm.set_instance_color(k, bl[k][1])
		_bulbs = MultiMeshInstance3D.new()
		_bulbs.name = "Bulbs"
		_bulbs.multimesh = mm
		_bulbs.material_override = _bulb_mat
		_bulbs.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_bulbs.visibility_range_end = 2600.0
		add_child(_bulbs)
	var wl: Array = d.wires
	if wl.is_empty():
		_wires.mesh = null
	else:
		var im := ImmediateMesh.new()
		im.surface_begin(Mesh.PRIMITIVE_LINES)
		for p in wl:
			im.surface_add_vertex(p)
		im.surface_end()
		_wires.mesh = im
	lamps = d.lamps
	_tent_spots = d.spots


# ------------------------------------------------------------------ the island side seen from below (MID pieces)
static func _warren_mesh(piece: String) -> Mesh:
	if _warren_mid == null:
		var ps = load("res://remake/sky/warrens/kit/kit_mid.glb")
		if ps is PackedScene:
			_warren_mid = (ps as PackedScene).instantiate()
	if _warren_mid == null:
		return null
	var mi := _warren_mid.find_child(piece, true, false) as MeshInstance3D
	return mi.mesh if mi else null


func _island_props() -> void:
	## the stations, line houses and davit of every island here, from the warren kit's MID models, while the island
	## isn't near (the warren draws its own then)
	var seen := {}
	for m in mem:
		var i: int = m.i
		seen[i] = true
		var isl: SkyIsland = sys.islands[i]
		if not _props.has(i):
			var root := Node3D.new()
			root.name = "MooringProps"
			for mo in sys.drift.mooring.moor.get(str(m.id), []):
				var mesh := _warren_mesh(str(mo.piece))
				if mesh == null:
					continue
				var mi := MeshInstance3D.new()
				mi.mesh = mesh
				mi.material_override = _prop_mat
				var o: Array = mo.origin
				mi.transform = Transform3D(Basis(Vector3.UP, float(mo.yaw)), Vector3(float(o[0]), float(o[1]), float(o[2])))
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				root.add_child(mi)
			isl.add_child(root)
			_props[i] = root
		(_props[i] as Node3D).visible = isl.tier < 2
	for i in _props.keys():
		if not seen.has(i):
			if is_instance_valid(_props[i]):
				(_props[i] as Node).queue_free()
			_props.erase(i)


# ------------------------------------------------------------------ the ropeways
static func _specs(m: Dictionary) -> Array:
	## a ground member's ropeways: [{key, st, G, gyaw, pax}] -- its passenger one, and its cargo one where it has it
	var rec: Dictionary = m.rec
	var out: Array = []
	if not m.ground:
		return out
	if not (rec.station as Dictionary).is_empty() and (rec.gstation as Vector2).is_finite():
		out.append({"key": "%s:%s" % [m.id, str((rec.station as Dictionary).get("cell", ""))], "st": rec.station,
			"G": rec.gstation, "gyaw": float(rec.gyaw), "pax": str((rec.station as Dictionary).get("kind", "pax")) == "pax"})
	var cg: Dictionary = rec.get("cargo", {})
	if not cg.is_empty():
		out.append({"key": "%s:%s" % [m.id, str((cg.station as Dictionary).get("cell", ""))], "st": cg.station,
			"G": cg.gstation, "gyaw": float(cg.gyaw), "pax": false})
	return out


func _ways_update(T: float) -> void:
	## which ropeways run (RIGGING done: the ropes are up), their cabins made once; cargo cabins 07:00-19:00 (after
	## hours the gondolas carry people only)
	var want := {}
	var gond := str(FleaCalendar.state(M, floori(T / 24.0), fposmod(T, 24.0)).get("gondolas", "all"))
	for m in mem:
		var dt: float = T - float(m.A)
		var ph: String = m.phase
		if dt < SkyMooring.PH.RIGGING + 1.0 or ph == "CAST_OFF" or ph == "":
			continue
		for sp in _specs(m):
			var key: String = sp.key
			want[key] = m
			if not _ways.has(key):
				_ways[key] = _make_way(m, sp)
			var w: Dictionary = _ways[key]
			w.running = (dt >= SkyMooring.PH.SERVICE and ph != "STRIKE") or (ph == "STRIKE" and T < float(m.Lv) - 0.25)
			if not w.pax and gond != "all":
				w.running = false
	for key in _ways.keys():
		if not want.has(key):
			for c in _ways[key].cabins:
				if is_instance_valid(c.node):
					(c.node as Node).queue_free()
				if c.body and is_instance_valid(c.body):
					(c.body as Node).queue_free()
			_ways.erase(key)


func _make_way(m: Dictionary, sp: Dictionary) -> Dictionary:
	var w := {"i": m.i, "id": m.id, "st": sp.st, "G": sp.G, "gyaw": float(sp.gyaw), "cabins": [], "pax": bool(sp.pax),
		"running": false, "phase0": FleaData.u(int(FleaData.island(m.id).get("hid", 0)), str(sp.key).hash()) * 280.0}
	for b in 2:
		w.cabins.append(_make_cabin(m.id, bool(sp.pax)))
	return w


func _cab_arrays(pax: bool, over: Dictionary) -> Dictionary:
	var acc := {}
	if pax:
		FleaKit.put(acc, "gondola_cabin_pax", Transform3D.IDENTITY, 0, over)
	else:
		FleaKit.put(acc, "gondola_cabin_cargo", Transform3D.IDENTITY, 0, over)
		FleaKit.put(acc, "fm_crate_stack", Transform3D(Basis(), Vector3(0.0, 0.0, 0.0)), 0, over)
	FleaKit.put(acc, "gondola_carriage", Transform3D(Basis(), Vector3(0.0, 5.2, 0.0)), 0, over)
	return _merge(acc)


func _make_cabin(iid: String, pax: bool) -> Dictionary:
	var over := _clan(iid)
	var ck := "%s|%s" % [pax, over.get("accent", "")]
	if not _cab_mesh.has(ck):
		var mg := _cab_arrays(pax, over)
		var am := ArrayMesh.new()
		for g in mg:
			am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, mg[g])
			am.surface_set_material(am.get_surface_count() - 1, _vc_mat if g == "vc" else FleaKit.material(g))
		_cab_mesh[ck] = am
	var node := Node3D.new()
	node.name = "Cabin"
	add_child(node)
	var mi := MeshInstance3D.new()
	mi.mesh = _cab_mesh[ck]
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.visibility_range_end = 3000.0
	node.add_child(mi)
	var cab := {"node": node, "pax": pax, "doors": [], "body": null, "xf": Transform3D.IDENTITY, "prev": Transform3D.IDENTITY,
		"warden": null, "open": 0.0}
	if pax:
		var dm := ArrayMesh.new()
		var dacc := {}
		FleaKit.put(dacc, "gondola_cabin_door", Transform3D.IDENTITY, 0, over)
		var dg := _merge(dacc)
		for g in dg:
			dm.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, dg[g])
			dm.surface_set_material(dm.get_surface_count() - 1, _vc_mat if g == "vc" else FleaKit.material(g))
		for side in ["n", "s"]:
			var di := MeshInstance3D.new()
			di.mesh = dm
			di.visibility_range_end = 400.0
			node.add_child(di)
			cab.doors.append({"mi": di, "closed": FleaKit.anchor("gondola_cabin_pax", "door_%s_closed" % side),
				"open": FleaKit.anchor("gondola_cabin_pax", "door_%s_open" % side), "shape": null})
	return cab


func _way_points(w: Dictionary, b: int) -> Array:
	## the cabin's pivot path for track b (world): the ground berth, out of its station, the span, into the island
	## station, its berth there
	var isl: SkyIsland = sys.islands[w.i]
	var IX := isl.global_transform
	var st: Dictionary = w.st
	var an: Dictionary = st.get("anchors", {})
	var G: Vector2 = w.G
	var gy := MapTerrain.elevation(G.x, G.y)
	var gb := StationGeo.basis(G.x)
	var yaw: float = w.gyaw
	var d := Vector3(cos(yaw), 0.0, -sin(yaw))
	var gbas := gb * Basis(d, Vector3.UP, d.cross(Vector3.UP))
	var gorg := StationGeo.point(G.x, G.y, gy)
	var gxf := Transform3D(gbas, gorg)
	var pv: Array = []
	var ex: Array = []
	for k in 2:
		pv.append(gxf * _an3("ground_station", "pivot_%d" % k))
		ex.append(gxf * (_an3("ground_station", "rope_exit_%d" % k) - Vector3(0.0, 0.9, 0.0)))
	var ip: Array = []
	var ie: Array = []
	for k in 2:
		var p: Array = an.get("pivot_%d" % k, an.get("berth_%d" % k, st.origin))
		ip.append(IX * Vector3(float(p[0]), float(p[1]) + (5.2 if not an.has("pivot_%d" % k) else 0.0), float(p[2])))
		var e: Array = an.get("rope_exit_%d" % k, p)
		ie.append(IX * Vector3(float(e[0]), float(e[1]) - 0.9, float(e[2])))
	# (the uncrossed pairing of the ground's berths with the island's)
	var straight: float = (ex[0] as Vector3).distance_to(ie[0]) + (ex[1] as Vector3).distance_to(ie[1])
	var crossed: float = (ex[0] as Vector3).distance_to(ie[1]) + (ex[1] as Vector3).distance_to(ie[0])
	var ib := b if straight <= crossed else 1 - b
	return [pv[b], ex[b], ie[ib], ip[ib], gxf]


static func _an3(piece: String, name: String) -> Vector3:
	return FleaKit.anchor(piece, name).origin


func _path_at(pts: Array, s: float) -> Array:
	## [point, direction] at arc length s along P0 -> P1 -> (the sagging span) -> P2 -> P3
	var P0: Vector3 = pts[0]
	var P1: Vector3 = pts[1]
	var P2: Vector3 = pts[2]
	var P3: Vector3 = pts[3]
	var l0 := P0.distance_to(P1)
	var l1 := P1.distance_to(P2)
	var l2 := P2.distance_to(P3)
	if s <= l0:
		return [P0.lerp(P1, s / maxf(l0, 0.01)), (P1 - P0).normalized()]
	s -= l0
	if s <= l1:
		var t := s / maxf(l1, 0.01)
		var up := StationGeo.up(StationGeo.s_of(P1.lerp(P2, t)))
		var p := P1.lerp(P2, t) - up * (4.0 * t * (1.0 - t) * l1 * SAG)
		var dd := (P2 - P1).normalized() + up * (4.0 * (2.0 * t - 1.0) * SAG)
		return [p, dd.normalized()]
	s -= l1
	return [P2.lerp(P3, clampf(s / maxf(l2, 0.01), 0.0, 1.0)), (P3 - P2).normalized()]


static func _travel(S: float) -> float:
	return S / SPEED + SPEED / ACC


static func _dist_at(S: float, t: float) -> float:
	## distance covered t s into a trip of S m (trapezoid: accelerate at ACC to SPEED, cruise, brake)
	var ta := SPEED / ACC
	var tt := _travel(S)
	if t <= 0.0:
		return 0.0
	if t >= tt:
		return S
	if t < ta:
		return 0.5 * ACC * t * t
	if t > tt - ta:
		var r := tt - t
		return S - 0.5 * ACC * r * r
	return 0.5 * ACC * ta * ta + SPEED * (t - ta)


func _cabin_step(w: Dictionary, now_s: float, windy: bool, night_lull: bool) -> void:
	for b in 2:
		var cab: Dictionary = w.cabins[b]
		var pts := _way_points(w, b)
		var L := (pts[0] as Vector3).distance_to(pts[1]) + (pts[1] as Vector3).distance_to(pts[2]) + (pts[2] as Vector3).distance_to(pts[3])
		var tt := _travel(L)
		var dw := DWELL_NIGHT if night_lull else DWELL
		var C := 2.0 * (tt + dw)
		var ph := fposmod(now_s + float(w.phase0) + (C * 0.5 if b == 1 else 0.0), C)
		if not w.running or windy:
			# (stopped: the cabins wait at their berths -- the first at the ground, the second at the island)
			ph = dw * 0.5 if b == 0 else tt + dw * 1.5
		var s := 0.0
		var open := 0.0
		if ph < dw:
			s = 0.0
			open = clampf(minf(ph - 1.0, dw - 1.0 - ph) / 2.5, 0.0, 1.0)
		elif ph < dw + tt:
			s = _dist_at(L, ph - dw)
		elif ph < 2.0 * dw + tt:
			s = L
			open = clampf(minf(ph - dw - tt - 1.0, 2.0 * dw + tt - 1.0 - ph) / 2.5, 0.0, 1.0)
		else:
			s = L - _dist_at(L, ph - 2.0 * dw - tt)
		var pd := _path_at(pts, s)
		var p: Vector3 = pd[0]
		var up := StationGeo.up(StationGeo.s_of(p))
		var dir: Vector3 = (pd[1] as Vector3).slide(up)
		if dir.length() < 0.01:
			dir = (pts[3] as Vector3 - (pts[0] as Vector3)).slide(up)
		dir = dir.normalized()
		var bas := Basis(dir, up, dir.cross(up))
		cab.prev = cab.xf
		cab.xf = Transform3D(bas, p - up * 5.2)
		(cab.node as Node3D).global_transform = cab.xf
		cab.open = open
		cab.s = s
		cab.L = L
		for dr in cab.doors:
			var c: Transform3D = dr.closed
			var o: Transform3D = dr.open
			(dr.mi as MeshInstance3D).transform = Transform3D(c.basis, c.origin.lerp(o.origin, open))
			if dr.shape:
				(dr.shape as CollisionShape3D).transform = Transform3D(c.basis, c.origin.lerp(o.origin, open)) * Transform3D(Basis(), Vector3(0.0, 1.1, 0.0))


func _physics_process(delta: float) -> void:
	if sys == null or _released:
		return
	Prof.begin("moor.ways")
	var now_s := Time.get_ticks_msec() / 1000.0
	var T := sys.sky.now_hours() if sys.sky else 0.0
	var hr := fposmod(T, 24.0)
	var windy := sys.drift.mooring.wind(market_id) > SkyMooring.WIND_LIMIT
	var pl := sys.player
	var pp := pl.global_position if pl else Vector3.INF
	for key in _ways:
		var w: Dictionary = _ways[key]
		_cabin_step(w, now_s, windy, hr < 6.0)
		for cab in w.cabins:
			var near := (cab.xf as Transform3D).origin.distance_to(pp) < RIDE_R
			if near and cab.body == null:
				_cabin_body(cab)
			elif not near and cab.body != null:
				(cab.body as Node).queue_free()
				cab.body = null
				for dr in cab.doors:
					dr.shape = null
			if cab.body:
				(cab.body as AnimatableBody3D).global_transform = cab.xf
	# the rider: carried by the cabin they stand in
	if pl and not pl.is_seated():
		for key in _ways:
			for cab in _ways[key].cabins:
				if not cab.pax:
					continue
				var prev: Transform3D = cab.prev
				var lp := prev.affine_inverse() * pp
				if absf(lp.x) < 2.85 and absf(lp.z) < 1.42 and lp.y > 0.2 and lp.y < 2.9:
					pl.carrier_velocity = ((cab.xf as Transform3D) * lp - pp) / maxf(delta, 1e-4)
					pl.sheltered = true
					pl.gravity_k = 1.0
					cab.rider = true
				elif cab.get("rider", false):
					cab.rider = false
					pl.sheltered = false
	_cage_step(T)
	Prof.end("moor.ways")


func _cabin_body(cab: Dictionary) -> void:
	var body := AnimatableBody3D.new()
	body.sync_to_physics = false
	add_child(body)
	for b in FleaKit.info("gondola_cabin_pax" if cab.pax else "gondola_cabin_cargo").get("frame", []):
		var lo := Vector3(float(b[0][0]), float(b[0][1]), float(b[0][2]))
		var hi := Vector3(float(b[1][0]), float(b[1][1]), float(b[1][2]))
		var cs := CollisionShape3D.new()
		var sh := BoxShape3D.new()
		sh.size = (hi - lo).abs() + Vector3(0.001, 0.001, 0.001)
		cs.shape = sh
		cs.position = (lo + hi) * 0.5
		body.add_child(cs)
	for dr in cab.doors:
		var cs2 := CollisionShape3D.new()
		var sh2 := BoxShape3D.new()
		sh2.size = Vector3(1.24, 2.2, 0.06)
		cs2.shape = sh2
		body.add_child(cs2)
		dr.shape = cs2
	body.global_transform = cab.xf
	cab.body = body


func board_player() -> bool:
	## the player into the passenger cabin nearest its ground berth (a test / the PDA's "ride the gondola")
	var best := {}
	var bs := INF
	for key in _ways:
		for cab in _ways[key].cabins:
			if cab.pax and float(cab.get("s", INF)) < bs:
				bs = float(cab.get("s", INF))
				best = cab
	if best.is_empty() or sys.player == null:
		return false
	var xf: Transform3D = best.xf
	sys.player.global_transform = Transform3D(xf.basis, xf * Vector3(-1.2, 1.6, 0.0))
	sys.player.velocity = Vector3.ZERO
	return true


# ------------------------------------------------------------------ the drop cage and the ropes
func _cage_step(T: float) -> void:
	var seen := {}
	for m in mem:
		if not m.ground:
			continue
		var rec: Dictionary = m.rec
		var hk: Array = rec.davit
		if hk.is_empty():
			continue
		var dt := T - float(m.A)
		var ph: String = m.phase
		if ph in ["", "TRIM", "APPROACH", "HOLD"]:
			continue
		var isl: SkyIsland = sys.islands[m.i]
		var top := isl.global_transform * Vector3(float(hk[0]), float(hk[1]), float(hk[2]))
		var s_ := StationGeo.s_of(top)
		var up := StationGeo.up(s_)
		var depth := StationGeo.h_of(top) - MapTerrain.elevation(s_, top.x) - 5.7
		var down := 0.0
		if ph == "CREW_DOWN":
			down = clampf((dt - SkyMooring.PH.CREW_DOWN) * SkyMooring.HOUR_S * CAGE_SPEED, 0.0, depth)
		elif ph == "CAST_OFF":
			down = clampf(depth - (T - float(m.Lv)) * SkyMooring.HOUR_S * CAGE_SPEED, 0.0, depth)
		else:
			down = depth
		if down <= 0.5:
			continue
		seen[m.i] = true
		if not _cages.has(m.i):
			var acc := {}
			FleaKit.put(acc, "gondola_drop_cage", Transform3D.IDENTITY, 0, _clan(str(m.id)))
			var mg := _merge(acc)
			var am := ArrayMesh.new()
			for g in mg:
				am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, mg[g])
				am.surface_set_material(am.get_surface_count() - 1, _vc_mat if g == "vc" else FleaKit.material(g))
			var mi := MeshInstance3D.new()
			mi.name = "DropCage"
			mi.mesh = am
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(mi)
			_cages[m.i] = {"mi": mi}
		var c: Dictionary = _cages[m.i]
		c.top = top
		# (it swings a little on its way down)
		var sw := sin(Time.get_ticks_msec() / 1700.0 + m.i) * 0.6 * (1.0 if ph == "CREW_DOWN" or ph == "CAST_OFF" else 0.0)
		var fwd := StationGeo.forward(s_)
		var cp := top - up * (down + 5.54) + fwd * sw
		(c.mi as MeshInstance3D).global_transform = Transform3D(StationGeo.basis(s_), cp)
		c.hook = cp + up * 5.54
	for i in _cages.keys():
		if not seen.has(i):
			(_cages[i].mi as Node).queue_free()
			_cages.erase(i)


func _draw_ropes() -> void:
	var im: ImmediateMesh = _lines.mesh
	im.clear_surfaces()
	if mem.is_empty():
		return
	var T := sys.sky.now_hours() if sys.sky else 0.0
	var segs := PackedVector3Array()
	var k_ := SkyMooring._k(SkyMooring.MOOR_H)
	for m in mem:
		if not m.ground:
			continue
		var isl: SkyIsland = sys.islands[m.i]
		var IX := isl.global_transform
		var rec: Dictionary = m.rec
		var dt := T - float(m.A)
		var ph: String = m.phase
		if ph in ["", "TRIM", "APPROACH"]:
			continue
		# the hawsers, lowered one by one through ANCHOR (each ~2 game minutes), slipped at CAST_OFF
		var hw: Array = rec.hawsers
		for j in hw.size():
			var t0: float = SkyMooring.PH.ANCHOR + (SkyMooring.PH.LOGISTICS - SkyMooring.PH.ANCHOR) * j / maxf(hw.size(), 1)
			var f := clampf((dt - t0) / 0.033, 0.0, 1.0)
			if ph == "CAST_OFF":
				f = 1.0 - clampf((T - float(m.Lv)) / 0.25, 0.0, 1.0)
			if f <= 0.0:
				continue
			var fr: Array = hw[j].from
			var A := IX * Vector3(float(fr[0]), float(fr[1]), float(fr[2]))
			var to: Vector2 = hw[j].to
			var hh := (31.2 if str(M.tier) == "city" else 23.2) if hw[j].mast else 0.07
			var B := StationGeo.point(to.x, to.y, MapTerrain.elevation(to.x, to.y) + hh)
			if f < 1.0:
				var up0 := StationGeo.up(StationGeo.s_of(A))
				var depth := A.distance_to(B)
				B = A - up0 * depth * f                    # (paying out, still hanging)
			_curve(segs, A, B, 0.01, 10)
		# the ropeways' ropes once RIGGING has them down: two track ropes and the haul rope's two legs
		var rf := clampf((dt - SkyMooring.PH.RIGGING - 0.5) / 1.5, 0.0, 1.0)
		if ph == "CAST_OFF" or rf <= 0.0:
			continue
		for sp in _specs(m):
			var w: Dictionary = _ways.get(sp.key, {"i": m.i, "st": sp.st, "G": sp.G, "gyaw": sp.gyaw})
			for b in 2:
				var pts := _way_points(w, b)
				var P1: Vector3 = pts[1]
				var P2: Vector3 = pts[2]
				if rf < 1.0:
					P1 = P2.lerp(P1, rf)                      # (coming down from the island)
				var up1 := StationGeo.up(StationGeo.s_of(P1))
				for dz in [0.9, 0.37]:
					var a1: Vector3 = P1 + up1 * float(dz)
					var a2: Vector3 = P2 + StationGeo.up(StationGeo.s_of(P2)) * float(dz)
					_curve(segs, a2, a1, SAG if dz > 0.5 else SAG * 1.4, 14)
	# the cage's hoist line
	for i in _cages:
		var c: Dictionary = _cages[i]
		if c.has("top") and c.has("hook"):
			segs.append(c.top)
			segs.append(c.hook)
	if segs.is_empty():
		return
	im.surface_begin(Mesh.PRIMITIVE_LINES)
	for p in segs:
		im.surface_add_vertex(p)
	im.surface_end()


static func _curve(segs: PackedVector3Array, A: Vector3, B: Vector3, sag: float, n: int) -> void:
	var L := A.distance_to(B)
	var up := StationGeo.up(StationGeo.s_of((A + B) * 0.5))
	var prev := A
	for k in range(1, n + 1):
		var t := float(k) / n
		var p := A.lerp(B, t) - up * (4.0 * t * (1.0 - t) * L * sag)
		segs.append(prev)
		segs.append(p)
		prev = p


# ------------------------------------------------------------------ the islanders: the tents' vendors, the wardens
func _people_step() -> void:
	if sys.player == null:
		return
	var pp := sys.player.global_position
	var want := {}
	var cand: Array = []
	for sp in _tent_spots:
		var d := (sp[0] as Vector3).distance_to(pp)
		if d < VENDOR_R:
			cand.append([d, "v:" + str(sp[3]), sp[0], sp[1], str(sp[2]), null])
	for key in _ways:
		for b in 2:
			var cab: Dictionary = _ways[key].cabins[b]
			if cab.pax and (cab.xf as Transform3D).origin.distance_to(pp) < WARDEN_R:
				cand.append([0.0, "w:%s:%d" % [key, b], Vector3.ZERO, Vector3.ZERO, str(_ways[key].id), cab])
	cand.sort_custom(func(a, b) -> bool: return a[0] < b[0])
	for c in cand.slice(0, MAX_VENDORS):
		want[c[1]] = c
	for k in _people.keys():
		if not want.has(k):
			if is_instance_valid(_people[k].npc):
				(_people[k].npc as Node).queue_free()
			_people.erase(k)
	# (one new person a tick: the mesh is made on a worker, uploaded here)
	for k in _people_job.keys():
		var j: Dictionary = _people_job[k]
		if not WorkerThreadPool.is_task_completed(j.task):
			continue
		WorkerThreadPool.wait_for_task_completion(j.task)
		_people_job.erase(k)
		if not want.has(k) or (j.data as Dictionary).is_empty():
			continue
		var npc := NpcCharacter.from_prepared(j.data)
		var c: Array = want[k]
		if c[5] != null:
			var cab: Dictionary = c[5]
			(cab.node as Node3D).add_child(npc)
			npc.transform = FleaKit.anchor("gondola_cabin_pax", "warden")
		else:
			add_child(npc)
			var p: Vector3 = c[2]
			var up := StationGeo.up(StationGeo.s_of(p))
			var f := ((c[3] as Vector3)).slide(up).normalized()
			if f.length() < 0.1:
				f = StationGeo.forward(StationGeo.s_of(p))
			npc.global_transform = Transform3D(Basis(up.cross(f), up, f).orthonormalized() * Basis(Vector3.UP, PI), p)
		var anim := NpcAnimator.attach(npc)
		if anim:
			anim.speed = 0.0
		_people[k] = {"npc": npc, "anim": anim}
		break
	for k in want:
		if _people.has(k) or _people_job.has(k) or _people_job.size() >= 2:
			continue
		var c2: Array = want[k]
		var pid := "%s:%s" % [market_id, k]
		var job_name := "cabin_warden" if c2[5] != null else "shopkeeper"
		var v := NpcTraits.shared().sky_folk(FOLK_SEED, pid, str(c2[4]), job_name, ["L0", "L1"])
		var j2 := {"data": {}}
		j2.task = WorkerThreadPool.add_task(func(): j2.data = NpcCharacter.prepare(v, pid, FOLK_SEED, "work"), false, "moor folk")
		_people_job[k] = j2


func stats() -> Dictionary:
	var draws := 0
	var tris := 0
	for k in _chunks:
		for h in (_chunks[k].node as Node).get_children():
			if h is MeshInstance3D:
				draws += 1
	var cabins := 0
	for key in _ways:
		cabins += (_ways[key].cabins as Array).size()
	draws += cabins * 3 + _cages.size() + (1 if _bulbs else 0) + 2
	return {"members": mem.size(), "chunks": _chunks.size(), "cabins": cabins, "ways": _ways.size(), "tents": n_tents,
		"bulbs": _bulbs.multimesh.instance_count if _bulbs else 0, "cages": _cages.size(), "people": _people.size(),
		"draws_est": draws, "fair": fair, "celebration": celebration, "holiday": holiday, "lamps": lamps.size()}

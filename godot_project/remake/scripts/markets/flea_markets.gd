extends Node3D
class_name FleaMarkets

## The flea markets in the world (research/flea_markets/00_plan.md §6, stream D: the static market). One node for all
## 22 (remake/markets/flea_markets.json, FleaData); a market within BUILD_R of the player is built, in 64 m chunks:
##   - its sheds (portal frames, gable roofs, back walls, bay partitions, roll shutters -- down unless that bay's
##     tenant is trading), open pitches (painted outlines; a table, goods and, for most, a pop-up canopy when its
##     tenant is there), double pitches, food trucks on their pads, the islanders' stalls in their clan colours;
##   - the office, gate house and restrooms, the entrance arch, the pylon with the market's own sign (remake/signs/
##     markets.png, its night glow from markets_emit.png), the mooring masts and anchor blocks;
##   - box colliders for the solid parts (sheds' back walls, buildings, trucks, the pylon, the masts).
## The lot's stalls and its P signs are road_furniture's (the lot record), its 9 m poles and the aisles' festoons
## StreetLights' (lamp kind 5, scheme 4). What is open comes from FleaCalendar.state and FleaVendors.roster, checked
## once a second; a market is rebuilt (on a worker) when its day or its open/closed state changes.
##
## Until the KIT stream's pieces land (research/flea_markets/requests.md W2) the stalls, sheds and trucks are drawn
## here as vertex-coloured boxes: one opaque material, one draw per chunk and LOD band, the sign one more.
##
##   FleaMarkets.vendor_spot(pid, day)          -> (s, x) where a vendor stands today (behind their table), or INF
##   FleaMarkets.shopper_spot(market, pid, day, k) -> (s, x) the k-th stall front a shopper browses
##   stats()                                    -> {built, chunks, draws_est, verts}

const BUILD_R := 900.0               # a market nearer than this is built (MID tier, 00 §6)
const FREE_R := 1100.0
const NEAR_R := 260.0                # goods, tables and canopies are drawn to here (NEAR)
const MID_R := 950.0
const CHUNK := 64.0
const TICK := 1.0
const SIGNS := "res://remake/signs/signs.json"
const SIGN_PNG := "res://remake/signs/markets.png"
const SIGN_EMIT := "res://remake/signs/markets_emit.png"
const SHED_COL := {"north": Color(0.56, 0.17, 0.13), "river": Color(0.9, 0.86, 0.74), "south": Color(0.7, 0.72, 0.73)}
const CANVAS := [Color(0.85, 0.2, 0.18), Color(0.15, 0.4, 0.75), Color(0.95, 0.95, 0.92), Color(0.2, 0.55, 0.3),
	Color(0.95, 0.7, 0.15), Color(0.55, 0.25, 0.6), Color(0.1, 0.55, 0.6), Color(0.9, 0.45, 0.2)]
const GOODS := {"antiques": Color(0.45, 0.3, 0.18), "collectibles": Color(0.7, 0.55, 0.2), "household": Color(0.75, 0.75, 0.7),
	"furniture": Color(0.42, 0.28, 0.16), "clothing_used": Color(0.5, 0.35, 0.55), "clothing_new": Color(0.85, 0.3, 0.45),
	"tools": Color(0.35, 0.37, 0.4), "salvage": Color(0.45, 0.4, 0.33), "electronics": Color(0.15, 0.17, 0.2),
	"books": Color(0.55, 0.2, 0.15), "toys": Color(0.95, 0.75, 0.1), "crafts": Color(0.7, 0.45, 0.3),
	"produce": Color(0.35, 0.6, 0.15), "plants": Color(0.2, 0.5, 0.2), "food": Color(0.85, 0.65, 0.4), "sky": Color(0.3, 0.75, 0.9)}

var target: Node3D
var _sky: Node
var _t := 0.0
var _built := {}                     # market id -> {node, key, chunks}
var _jobs := {}                      # market id -> task id
var _mx := Mutex.new()
var _done: Array = []
var _mat: StandardMaterial3D
var _paint_mat: StandardMaterial3D
var _sign_mat: ShaderMaterial
var _sign_uv := {}                   # market id -> Rect2 (uv in markets.png)
var _night := 0.0
var _verts := 0


func setup() -> void:
	name = "FleaMarkets"
	FleaData.markets()
	FleaKit.load_all()
	_mat = StandardMaterial3D.new()
	_mat.vertex_color_use_as_albedo = true
	_mat.roughness = 0.85
	_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	_paint_mat = StandardMaterial3D.new()
	_paint_mat.vertex_color_use_as_albedo = true
	_paint_mat.roughness = 0.9
	_paint_mat.shading_mode = BaseMaterial3D.SHADING_MODE_PER_VERTEX
	var sj = DataFile.json(SIGNS)
	if sj is Dictionary:
		for M in FleaData.markets():
			var c = (sj.get("cells", {}) as Dictionary).get(str(M.get("sign", "")) + "_main")
			if c is Dictionary:
				var uv: Array = c.uv
				_sign_uv[M.id] = Rect2(float(uv[0]), float(uv[1]), float(uv[2]), float(uv[3]))
	if ResourceLoader.exists(SIGN_PNG):
		var sh := Shader.new()
		sh.code = """shader_type spatial;
render_mode cull_disabled;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap;
uniform sampler2D emit_tex : hint_default_black, filter_linear_mipmap;
uniform float night = 0.0;
void fragment() {
	vec4 c = texture(albedo_tex, UV);
	if (c.a < 0.5) { discard; }
	ALBEDO = c.rgb;
	ROUGHNESS = 0.7;
	EMISSION = c.rgb * texture(emit_tex, UV).r * 2.0 * night;
}"""
		_sign_mat = ShaderMaterial.new()
		_sign_mat.shader = sh
		_sign_mat.set_shader_parameter("albedo_tex", load(SIGN_PNG))
		if ResourceLoader.exists(SIGN_EMIT):
			_sign_mat.set_shader_parameter("emit_tex", load(SIGN_EMIT))
	set_process(true)


func _process(delta: float) -> void:
	_mx.lock()
	var done := _done
	_done = []
	_mx.unlock()
	for d in done:
		_commit(d)
	_t -= delta
	if _t > 0.0 or target == null:
		return
	_t = TICK
	Prof.begin("flea.tick")
	if _sky == null or not is_instance_valid(_sky):
		_sky = get_parent().get_node_or_null("DaySkySystem")
	var day := int(_sky.get("day")) if _sky and _sky.get("day") != null else 0
	var hour := float(_sky.time_of_day) * 24.0 if _sky and _sky.get("time_of_day") != null else 12.0
	var dl: float = _sky.daylight() if _sky and _sky.has_method("daylight") else 1.0
	_night = clampf((0.78 - dl) / 0.45, 0.0, 1.0)
	if _sign_mat:
		_sign_mat.set_shader_parameter("night", _night)
	FleaKit.set_night(_night)
	var p := target.global_position
	var here := Vector2(StationGeo.s_of(p), p.x)
	for M in FleaData.markets():
		if not M.get("sited", false):
			continue
		var d := NpcPlaces.dist(here, FleaData.centre(M))
		var id: String = M.id
		if d > FREE_R:
			if _built.has(id):
				(_built[id].node as Node).queue_free()
				_built.erase(id)
			continue
		if d > BUILD_R and not _built.has(id):
			continue
		var st := FleaCalendar.state(M, day, hour)
		# rebuilt when the day or what's out changes (stalls set out at SETUP, packed up after TEARDOWN)
		var out := str(st.phase) in ["SETUP", "OPEN", "LANTERN", "TEARDOWN"]
		var key := "%d|%s|%s|%s" % [day, out, st.local_open, st.islander_open]
		if _built.has(id) and str(_built[id].key) == key:
			continue
		if _jobs.has(id):
			continue
		var job := {"id": id, "day": day, "out": out, "key": key, "local": bool(st.local_open) or out and str(st.mode) != "ISLANDER",
			"islander": bool(st.islander_open) or (out and int(st.in_service) > 0)}
		_jobs[id] = WorkerThreadPool.add_task(_build.bind(job), true, "flea market " + id)
	Prof.end("flea.tick")


# ------------------------------------------------------------------ building (worker)
class Chunk:
	var c: Vector2                   # (s, x) of the chunk's middle
	var h: float
	var bas: Basis
	var org: Vector3
	var mid := SurfaceTool.new()     # sheds, trucks, buildings, masts: drawn to MID_R
	var near := SurfaceTool.new()    # tables, canopies, goods: to NEAR_R
	var paint := SurfaceTool.new()   # pitch outlines on the ground
	var nm := 0
	var nn := 0
	var np := 0
	var boxes: Array = []            # [Transform3D local, Vector3 size]
	var ramps := PackedVector3Array()   # walkable triangles (both faces) from the kit's `ramps` quads
	var kn := {}                     # the kit's full pieces by group (to NEAR_R)
	var km := {}                     # the kit's MID pieces by group (NEAR_R to MID_R)

	func _init(cc: Vector2) -> void:
		c = cc
		h = MapTerrain.elevation(cc.x, cc.y)
		bas = StationGeo.basis(cc.x)
		org = StationGeo.point(cc.x, cc.y, h)
		for st in [mid, near, paint]:
			st.begin(Mesh.PRIMITIVE_TRIANGLES)


var _M: Dictionary
var _ca := 1.0
var _sa := 0.0


func _local(ch: Chunk, s: float, x: float, hh: float) -> Vector3:
	## a ring point (s, x, height above the datum) in the chunk's frame (right = +x, up, -z = +s)
	return Vector3(x - ch.c.y, hh - ch.h, -StationGeo.wrap_ds(s - ch.c.x))


func _site_dir(u: float, v: float) -> Vector3:
	## a site-frame direction (u, v) in a chunk's local frame
	var ds := u * _ca - v * _sa
	var dx := u * _sa + v * _ca
	return Vector3(dx, 0.0, -ds)


func _chunk(chunks: Dictionary, p: Vector2) -> Chunk:
	var k := Vector2i(floori(p.x / CHUNK), floori(p.y / CHUNK))
	if not chunks.has(k):
		chunks[k] = Chunk.new(Vector2((k.x + 0.5) * CHUNK, (k.y + 0.5) * CHUNK))
	return chunks[k]


func _box(st: SurfaceTool, c: Vector3, r: Vector3, f: Vector3, sz: Vector3, col: Color) -> int:
	## a box centred at c, sz along (r, up, f)
	var up := Vector3.UP
	var hx := r * sz.x * 0.5
	var hy := up * sz.y * 0.5
	var hz := f * sz.z * 0.5
	var v := [c - hx - hy - hz, c + hx - hy - hz, c + hx + hy - hz, c - hx + hy - hz,
		c - hx - hy + hz, c + hx - hy + hz, c + hx + hy + hz, c - hx + hy + hz]
	var faces := [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [3, 7, 6, 2], [0, 4, 7, 3], [1, 2, 6, 5]]
	var nrm := [-f, f, -up, up, -r, r]
	for fi in 6:
		var fc: Array = faces[fi]
		st.set_color(col)
		st.set_normal(nrm[fi])
		for i in [0, 1, 2, 0, 2, 3]:
			st.add_vertex(v[fc[i]])
	return 36


func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, col: Color) -> int:
	var n := (b - a).cross(d - a).normalized()
	st.set_color(col)
	st.set_normal(n)
	for p in [a, b, c, a, c, d]:
		st.add_vertex(p)
	return 6


static func _pier_h(M: Dictionary, u: float, v: float) -> float:
	## the walking height on a pier market at site (u, v): its decks, its gangway (sloping to the landing); NAN off it
	var pr = M.get("pier")
	if not (pr is Dictionary):
		return NAN
	for dk in pr.decks:
		if u >= float(dk[0]) - 0.05 and u <= float(dk[2]) + 0.05 and v >= float(dk[1]) - 0.05 and v <= float(dk[3]) + 0.05:
			return float(pr.deck_h)
	var rp: Array = pr.ramp
	if absf(u - float(rp[0])) <= 1.4 and v >= float(rp[1]) - float(rp[3]) * 0.5 and v <= float(rp[1]) + float(rp[3]) * 0.5:
		var t := (v - (float(rp[1]) - float(rp[3]) * 0.5)) / float(rp[3])
		return lerpf(float(pr.landing_h), float(pr.deck_h), t)
	return NAN


func _ground_h(M: Dictionary, u: float, v: float, w: Vector2) -> float:
	var h := _pier_h(M, u, v)
	return h if not is_nan(h) else MapTerrain.elevation(w.x, w.y)


static var _piers: Array = []
static var _piers_ok := false


static func deck_h(s: float, x: float) -> float:
	## the deck height under (s, x) if it is on a pier market (NpcPopulation: people walk on the deck, not the lake bed)
	if not _piers_ok:
		_piers_ok = true
		for M in FleaData.markets():
			if M.get("sited", false) and M.get("pier") is Dictionary:
				_piers.append(M)
	for M in _piers:
		var c := FleaData.centre(M)
		if absf(StationGeo.wrap_ds(s - c.x)) > 140.0 or absf(x - c.y) > 140.0:
			continue
		var f: Dictionary = M.frame
		var a := float(f.yaw)
		var ds := StationGeo.wrap_ds(s - float(f.s))
		var dx := x - float(f.x)
		var h := _pier_h(M, ds * cos(a) + dx * sin(a), -ds * sin(a) + dx * cos(a))
		if not is_nan(h):
			return h
	return NAN


func _piece(chunks: Dictionary, u: float, v: float, yaw: float) -> Array:
	## [chunk, centre (local, on the ground), r, f] for a piece at site (u, v) facing yaw
	var w := FleaData.to_world(_M, u, v)
	var ch := _chunk(chunks, w)
	var cl := _local(ch, w.x, w.y, _ground_h(_M, u, v, w))
	var f := _site_dir(sin(yaw), cos(yaw)).normalized()
	var r := _site_dir(cos(yaw), -sin(yaw)).normalized()
	return [ch, cl, r, f]


func _build(job: Dictionary) -> void:
	var M := FleaData.market(job.id)
	_M = M
	var a := float((M.frame as Dictionary).get("yaw", 0.0))
	_ca = cos(a)
	_sa = sin(a)
	var chunks := {}
	var hid := int(M.hid)
	var band := "north" if str(M.region) in ["north_shore", "northland"] else ("south" if str(M.region) in ["southland", "south_shore"] else "river")
	var shed_col: Color = SHED_COL[band]
	var roster := FleaVendors.roster(M, int(job.day)) if job.out else {}
	var kinds: PackedByteArray = roster.get("kind", PackedByteArray())
	var cats: PackedByteArray = roster.get("cat", PackedByteArray())
	var who: PackedInt32Array = roster.get("who", PackedInt32Array())
	var steel := Color(0.42, 0.44, 0.46)
	var white := Color(0.92, 0.92, 0.88)
	var stalls: Array = M.stalls
	if FleaKit.ok() and M.get("pier") is Dictionary:
		_build_pier(chunks, M)
	if FleaKit.ok():
		_kit_stalls(chunks, M, job, kinds, cats, who, hid, band)
	else:
		_stand_in_stalls(chunks, M, job, kinds, cats, who, hid, shed_col, steel, white)
	# -- the buildings, the arch and pylon, the mooring ground
	var arch: Array = M.arch
	var Pa := _piece(chunks, float(arch[0]), float(arch[1]), float(arch[2]))
	var cha: Chunk = Pa[0]
	var aw := float(arch[3])
	var kit := FleaKit.ok()
	var sign_p := "sign_" + str(M.get("sign", ""))
	var board_p := "fm_board_" + str(M.get("sign", ""))
	var arch_p: String = {"north": "fm_arch_timber", "river": "fm_arch_truss", "south": "fm_arch_googie"}[band]
	if kit and FleaKit.has(arch_p):
		var xa := Transform3D(Basis(Pa[2], Vector3.UP, Pa[3]), Pa[1])
		_kput(cha, arch_p, xa, 0)
		if FleaKit.has(board_p):
			for an in ["board", "board_back"]:
				_kput(cha, board_p, xa * FleaKit.anchor(arch_p, an), 0)
	for sd: float in ([] if kit and FleaKit.has(arch_p) else [-1.0, 1.0]):
		cha.nm += _box(cha.mid, Pa[1] + Pa[2] * sd * aw * 0.5 + Vector3.UP * 2.6, Pa[2], Pa[3], Vector3(0.5, 5.2, 0.5), shed_col)
		cha.boxes.append([Transform3D(Basis(Pa[2], Vector3.UP, Pa[3]), Pa[1] + Pa[2] * sd * aw * 0.5 + Vector3.UP * 2.6), Vector3(0.5, 5.2, 0.5)])
	if not (kit and FleaKit.has(arch_p)):
		cha.nm += _box(cha.mid, Pa[1] + Vector3.UP * 5.4, Pa[2], Pa[3], Vector3(aw + 1.0, 0.5, 0.6), shed_col.darkened(0.2))
	for b in [[float(arch[0]) + 10.0, float(arch[1]) + 4.0, Vector3(8.0, 3.2, 6.0), "office"],
			[float(arch[0]) - 10.0, float(arch[1]) + 4.0, Vector3(5.0, 2.8, 4.0), "gate"],
			[float(arch[0]) - 20.0, float(arch[1]) + 4.0, Vector3(6.0, 3.0, 8.0), "restroom"]]:
		if M.get("pier") is Dictionary:
			continue                                         # (a pier market's office is its landing's pylon board)
		var Pb := _piece(chunks, b[0], b[1], 0.0)
		var chb: Chunk = Pb[0]
		var sz: Vector3 = b[2]
		var kp: String = {"office": "fm_office", "gate": "fm_gatehouse", "restroom": "fm_restroom"}[b[3]]
		if kit and FleaKit.has(kp):
			_kput(chb, kp, Transform3D(Basis(Pb[2], Vector3.UP, Pb[3]), Pb[1]), {"north": 0, "river": 1, "south": 2}[band], {}, true)
			continue
		chb.nm += _box(chb.mid, Pb[1] + Vector3.UP * sz.y * 0.5, Pb[2], Pb[3], sz, white.darkened(0.08))
		chb.nm += _box(chb.mid, Pb[1] + Vector3.UP * (sz.y + 0.15), Pb[2], Pb[3], Vector3(sz.x + 0.6, 0.3, sz.z + 0.6), shed_col)
		chb.boxes.append([Transform3D(Basis(Pb[2], Vector3.UP, Pb[3]), Pb[1] + Vector3.UP * sz.y * 0.5), sz])
	var py: Array = M.pylon
	var Pp := _piece(chunks, float(py[0]), float(py[1]), float(py[2]))
	var chp: Chunk = Pp[0]
	var ph := 12.0 if str(M.tier) == "city" else (9.0 if str(M.tier) == "town" else 7.0)
	var signs_: Array = []
	if kit and FleaKit.has(sign_p):
		# the market's own pylon (07 §2: the rope knot, the lobster pot, the screen tower ...)
		_kput(chp, sign_p, Transform3D(Basis(Pp[2], Vector3.UP, Pp[3]), Pp[1]), 0, {}, true)
	else:
		chp.nm += _box(chp.mid, Pp[1] + Vector3.UP * ph * 0.5, Pp[2], Pp[3], Vector3(0.6, ph, 0.6), steel.darkened(0.3))
		chp.boxes.append([Transform3D(Basis(Pp[2], Vector3.UP, Pp[3]), Pp[1] + Vector3.UP * ph * 0.5), Vector3(0.6, ph, 0.6)])
		signs_.append([chp, Pp[1] + Vector3.UP * (ph + 2.6), Pp[2], Pp[3], 6.0])
	if not (kit and FleaKit.has(arch_p) and FleaKit.has(board_p)):
		signs_.append([cha, Pa[1] + Vector3.UP * 6.6, Pa[2], Pa[3], minf(aw, 6.0)])
	var mast_p := "mooring_mast_city" if str(M.tier) == "city" else "mooring_mast_town"
	for mp in (M.masts if not (kit and FleaKit.has(mast_p)) else []):
		var Pm := _piece(chunks, float(mp[0]), float(mp[1]), 0.0)
		var chm: Chunk = Pm[0]
		chm.nm += _box(chm.mid, Pm[1] + Vector3.UP * 15.0, Pm[2], Pm[3], Vector3(0.9, 30.0, 0.9), Color(0.75, 0.2, 0.15))
		chm.nm += _box(chm.mid, Pm[1] + Vector3.UP * 30.4, Pm[2], Pm[3], Vector3(2.0, 0.8, 2.0), steel)
		chm.boxes.append([Transform3D(Basis(Pm[2], Vector3.UP, Pm[3]), Pm[1] + Vector3.UP * 15.0), Vector3(1.2, 30.0, 1.2)])
	if kit and FleaKit.has(mast_p):
		for mp in M.masts:
			var Pm := _piece(chunks, float(mp[0]), float(mp[1]), 0.0)
			var xm := Transform3D(Basis(Pm[2], Vector3.UP, Pm[3]), Pm[1])
			_kput(Pm[0], mast_p, xm, 0, {}, true)
			var head := mast_p.replace("mooring_mast_", "mooring_mast_head_")
			if FleaKit.has(head):
				_kput(Pm[0], head, xm * FleaKit.anchor(mast_p, "head"), 0)
	for dm in M.deadmen:
		var Pd := _piece(chunks, float(dm[0]), float(dm[1]), 0.0)
		var chd: Chunk = Pd[0]
		var dp := "fm_pier_bollard" if M.get("pier") is Dictionary else "deadman_ring"
		if kit and FleaKit.has(dp):
			_kput(chd, dp, Transform3D(Basis(Pd[2], Vector3.UP, Pd[3]), Pd[1]), 0, {}, dp == "fm_pier_bollard")
			continue
		chd.nm += _box(chd.mid, Pd[1] + Vector3.UP * 0.05, Pd[2], Pd[3], Vector3(1.4, 0.12, 1.4), Color(0.6, 0.6, 0.58))
		chd.nm += _box(chd.mid, Pd[1] + Vector3.UP * 0.25, Pd[2], Pd[3], Vector3(0.5, 0.3, 0.1), steel.darkened(0.4))
	# -- out of the SurfaceTools into arrays (the main thread makes the meshes)
	var out := []
	for k in chunks:
		var ch: Chunk = chunks[k]
		var e := {"xf": Transform3D(ch.bas, ch.org), "boxes": ch.boxes, "ramps": ch.ramps}
		for nm in ["mid", "near", "paint"]:
			var n_: int = {"mid": ch.nm, "near": ch.nn, "paint": ch.np}[nm]
			if n_ > 0:
				e[nm] = (ch.get(nm) as SurfaceTool).commit_to_arrays()
		e["kn"] = FleaKit.commit(ch.kn)
		e["km"] = FleaKit.commit(ch.km)
		out.append(e)
	var sg := []
	for sgn in signs_:
		var ch2: Chunk = sgn[0]
		sg.append({"xf": Transform3D(ch2.bas, ch2.org), "c": sgn[1], "r": sgn[2], "f": sgn[3], "w": sgn[4]})
	_mx.lock()
	_done.append({"id": job.id, "key": job.key, "chunks": out, "signs": sg})
	_mx.unlock()


func _build_pier(chunks: Dictionary, M: Dictionary) -> void:
	## a floating pier market (tools/markets/market_pier.py): 6 m deck modules over every deck, edge rails but where the
	## decks meet and at the gangway, the gangway from the landing (its rise scaled to the shore), the bike racks
	var pr: Dictionary = M.pier
	var decks: Array = pr.decks
	for dk in decks:
		var u0 := float(dk[0])
		var v0 := float(dk[1])
		var u1 := float(dk[2])
		var v1 := float(dk[3])
		var nu := maxi(1, roundi((u1 - u0) / 6.0))
		var nv := maxi(1, roundi((v1 - v0) / 6.0))
		var su := (u1 - u0) / nu
		var sv := (v1 - v0) / nv
		for i in nu:
			for j in nv:
				var P := _piece(chunks, u0 + su * (i + 0.5), v0 + sv * (j + 0.5), 0.0)
				var xf := Transform3D(Basis(P[2], Vector3.UP, P[3]) * Basis.from_scale(Vector3(su / 6.0, 1.0, sv / 6.0)), P[1])
				_kput(P[0], "fm_pier_deck_6", xf, 0, {}, true)
		# the rails: each 6 m of edge that no other deck (nor the gangway) meets
		for e in [[u0, v0, u1, v0], [u1, v0, u1, v1], [u1, v1, u0, v1], [u0, v1, u0, v0]]:
			var a := Vector2(float(e[0]), float(e[1]))
			var b := Vector2(float(e[2]), float(e[3]))
			var L := a.distance_to(b)
			var n := maxi(1, floori(L / 6.0))
			for k in n:
				var m_ := a.lerp(b, (k + 0.5) / float(n))
				var out_ := (b - a).normalized().rotated(-PI * 0.5) * 0.6
				var q := m_ + out_
				var joined := false
				for dk2 in decks:
					if dk2 != dk and q.x >= float(dk2[0]) - 0.1 and q.x <= float(dk2[2]) + 0.1 and q.y >= float(dk2[1]) - 0.1 and q.y <= float(dk2[3]) + 0.1:
						joined = true
				if absf(m_.x) < 4.5 and absf(m_.y - float(pr.ramp[1]) - float(pr.ramp[3]) * 0.5) < 1.0:
					joined = true                          # (the gangway's opening)
				if joined:
					continue
				var dir := (b - a).normalized()
				var yaw := atan2(-dir.y, dir.x)            # (the rail runs along its piece +X = the site's (cos yaw, -sin yaw))
				var P := _piece(chunks, m_.x, m_.y, yaw)
				var xr := Transform3D(Basis(P[2], Vector3.UP, P[3]) * Basis.from_scale(Vector3(L / n / 6.0, 1.0, 1.0)), P[1])
				_kput(P[0], "fm_pier_rail_6", xr, 0, {}, true)
	# the gangway: its landing end at the shore (its rise the shore's height over the deck)
	var rp: Array = pr.ramp
	var Pr := _piece(chunks, float(rp[0]), float(rp[1]), 0.0)
	var rise := clampf(float(pr.landing_h) - float(pr.deck_h), 0.2, 2.5)
	var ch: Chunk = Pr[0]
	# (_piece put it at the ramp's mid height: lower it to the deck end's frame, the piece rises from y 0 there)
	var w := FleaData.to_world(M, float(rp[0]), float(rp[1]))
	var base := _local(ch, w.x, w.y, float(pr.deck_h))
	_kput(ch, "fm_pier_ramp", Transform3D(Basis(Pr[2], Vector3.UP, Pr[3]), base), 1, {}, true, rise / 1.0, 0.0)
	for br in (M.get("lot", {}) as Dictionary).get("bike_racks", []):
		var Pb := _piece(chunks, float(br[0]), float(br[1]), float(br[2]))
		_kput(Pb[0], "fm_bike_rack", Transform3D(Basis(Pb[2], Vector3.UP, Pb[3]), Pb[1]), 0, {}, true)


func _kput(ch: Chunk, p: String, xf: Transform3D, variant := 0, over := {}, collide := false, yscale := 1.0, ypivot := 0.0) -> void:
	## a kit piece into the chunk: the full mesh to NEAR_R, its MID beyond when the kit keeps it at LOD1
	var inf := FleaKit.info(p)
	FleaKit.put(ch.kn, p, xf, variant, over, false, yscale, ypivot)
	if str(inf.get("lod1", "drop")) == "keep":
		FleaKit.put(ch.km, p, xf, variant, over, true, yscale, ypivot)
	if collide and str(inf.get("collide", "")) == "frame":
		var fr: Array = inf.get("frame", [])
		for k in mini(fr.size(), 12):
			var lo := Vector3(float(fr[k][0][0]), float(fr[k][0][1]), float(fr[k][0][2]))
			var hi := Vector3(float(fr[k][1][0]), float(fr[k][1][1]), float(fr[k][1][2]))
			# (a scaled piece: the box's size scaled, its basis kept orthonormal -- physics takes no scaled shapes)
			ch.boxes.append([Transform3D(xf.basis.orthonormalized(), xf * ((lo + hi) * 0.5)), (hi - lo).abs() * xf.basis.get_scale().abs()])
		for rq in inf.get("ramps", []):
			var q: Array = []
			for pt in rq:
				var lp := Vector3(float(pt[0]), float(pt[1]), float(pt[2]))
				if yscale != 1.0:
					lp.y = ypivot + (lp.y - ypivot) * yscale
				q.append(xf * lp)
			for tri in [[0, 1, 2], [0, 2, 3], [2, 1, 0], [3, 2, 0]]:
				for k in tri:
					ch.ramps.append(q[k])


const GOODS_PIECE := {"antiques": ["fm_goods_antiques"], "collectibles": ["fm_goods_maps", "fm_goods_antiques"],
	"household": ["fm_goods_household"], "furniture": ["fm_goods_rocking_chair", "fm_goods_rolled_rug"],
	"clothing_used": ["fm_goods_clothing"], "clothing_new": ["fm_goods_clothing", "fm_goods_quilts"],
	"tools": ["fm_goods_tools"], "salvage": ["fm_goods_machines", "fm_goods_tools"], "electronics": ["fm_goods_machines"],
	"books": ["fm_goods_books", "fm_goods_maps"], "toys": ["fm_goods_toys", "fm_goods_bicycle"], "crafts": ["fm_goods_quilts"],
	"produce": ["fm_goods_produce", "fm_bin_produce"], "plants": ["fm_goods_plants"], "food": ["fm_goods_eggs_honey"],
	"sky": ["fm_goods_sky_knit", "fm_goods_sky_lights", "fm_goods_sky_rope", "fm_goods_sky_food", "fm_goods_sky_smoked", "fm_goods_sky_wonders"]}


func _goods_piece(cat: String, hid: int, i: int, k: int) -> String:
	var ps: Array = GOODS_PIECE.get(cat, ["fm_goods_household"])
	var p: String = ps[posmod(FleaData.h(hid, i, 19, k), ps.size())]
	return p if FleaKit.has(p) else "fm_goods_household"


func _kit_stalls(chunks: Dictionary, M: Dictionary, job: Dictionary, kinds: PackedByteArray, cats: PackedByteArray, who: PackedInt32Array, hid: int, band: String) -> void:
	var stalls: Array = M.stalls
	var shed_var: int = {"north": 0, "river": 1, "south": 2}[band]
	var board_p := "fm_board_" + str(M.get("sign", ""))
	var cat_of := func(i: int) -> String:
		return FleaData.categories[cats[i]] if i < cats.size() and cats[i] < FleaData.categories.size() else "household"
	var open_of := func(i: int) -> bool:
		if i >= kinds.size() or kinds[i] == 0:
			return false
		return bool(job.islander) if kinds[i] == FleaVendors.K_ISLANDER else bool(job.local)
	# the shed bays and their two stalls, slice by slice
	var by_slice := {}
	for i in stalls.size():
		var st: Array = stalls[i]
		if int(st[5]) >= 0:
			var key := Vector2i(int(st[5]), roundi(float(st[0]) * 10.0))
			if not by_slice.has(key):
				by_slice[key] = []
			by_slice[key].append(i)
	var sheds: Array = M.sheds
	for si in sheds.size():
		var sh: Dictionary = sheds[si]
		var u0 := float(sh.u0)
		var vm := (float(sh.v0) + float(sh.v1)) * 0.5
		var n_sl := roundi((float(sh.u1) - u0) / 3.0)
		for j in n_sl:
			var uc := u0 + 3.0 * (j + 0.5)
			var P := _piece(chunks, uc, vm, 0.0)
			var ch: Chunk = P[0]
			var vloc := _site_dir(0.0, 1.0).normalized()
			var uloc := _site_dir(1.0, 0.0).normalized()
			# piece +X = site -v, +Z = site +u (the bays tile along the shed's length)
			var xb := Transform3D(Basis(-vloc, Vector3.UP, uloc), P[1])
			_kput(ch, "fm_shed_bay", xb, shed_var, {}, j == 0 or j == n_sl - 1 or j % 4 == 0)
			if j == 0:
				var xe := xb * Transform3D(Basis(Vector3.UP, PI), Vector3(0, 0, -1.5))
				_kput(ch, "fm_shed_end_near", xe, shed_var)
				if FleaKit.has(board_p):
					_kput(ch, board_p, xe * FleaKit.anchor("fm_shed_end_near", "board"), 0)
			if j == n_sl - 1:
				_kput(ch, "fm_shed_end_far", xb * Transform3D(Basis(), Vector3(0, 0, 1.5)), shed_var)
			for i in by_slice.get(Vector2i(si, roundi(uc * 10.0)), []):
				var side := "R" if float(stalls[i][1]) < vm else "L"
				var op: bool = open_of.call(i)
				var xs := xb * FleaKit.anchor("fm_shed_bay", "shutter_" + side)
				_kput(ch, "fm_shutter", xs, shed_var, {}, false, 0.1 if op else 1.0, 2.6)
				if op:
					var cat: String = cat_of.call(i)
					for k in 3:
						var an := "g%d_%s" % [[0, 1, 4][k], side]
						_kput(ch, _goods_piece(cat, hid, i, k), xb * FleaKit.anchor("fm_shed_bay", an), FleaData.h(hid, i, k))
	# open pitches, doubles, food pads
	for i in stalls.size():
		var st: Array = stalls[i]
		var kind := int(st[3])
		if kind == FleaData.KIND_SHED and int(st[5]) >= 0:
			continue
		var yaw := float(st[2])
		var P := _piece(chunks, float(st[0]), float(st[1]), yaw)
		var ch: Chunk = P[0]
		var c: Vector3 = P[1]
		var r: Vector3 = P[2]
		var f: Vector3 = P[3]
		var x0 := Transform3D(Basis(r, Vector3.UP, f), c)
		var op: bool = open_of.call(i)
		var isl := i < kinds.size() and kinds[i] == FleaVendors.K_ISLANDER
		var over := {}
		var var_ := FleaData.h(hid, i, 23)
		if isl and who[i] <= -10:
			var cs: Array = (FleaData.islands()[-10 - who[i]] as Dictionary).get("colors", [])
			if cs.size() >= 2:
				over = {"fabric": cs[0], "accent": cs[1]}
		var on_pier := M.get("pier") is Dictionary
		if kind == FleaData.KIND_FOOD and not on_pier:
			if op and FleaKit.has("fm_food_truck_a"):
				_kput(ch, "fm_food_truck_a" if FleaData.h(hid, i, 29) % 2 == 0 else "fm_food_truck_b", x0, var_, over, true)
			elif op:
				# (no kit food truck yet: a stand-in box truck)
				var tc: Color = CANVAS[posmod(FleaData.h(hid, i, 9), CANVAS.size())]
				ch.nm += _box(ch.mid, c + Vector3.UP * 1.55, r, f, Vector3(2.3, 2.5, 6.2), tc)
				ch.nm += _box(ch.mid, c + f * 2.2 + Vector3.UP * 1.9, r, f, Vector3(2.32, 0.9, 1.0), Color(0.1, 0.1, 0.12))
				ch.boxes.append([Transform3D(Basis(r, Vector3.UP, f), c + Vector3.UP * 1.55), Vector3(2.3, 2.8, 6.2)])
			continue
		var offs: Array = [-1.5, 1.5] if kind == FleaData.KIND_DOUBLE else [0.0]
		var canopy := op and (isl or kind != FleaData.KIND_OPEN or FleaData.u(hid, i, 11) < 0.62)
		for o: float in offs:
			var xo := x0 * Transform3D(Basis(), Vector3(o, 0, 0))
			if not op:
				_kput(ch, "fm_paint_pitch", xo, 0)
				continue
			var cat: String = cat_of.call(i)
			var pp := "fm_pitch_table_long" if cat.begins_with("clothing") and FleaKit.has("fm_pitch_table_long") else "fm_pitch_open"
			_kput(ch, pp, xo, var_, over)
			for k in 3:
				_kput(ch, _goods_piece(cat, hid, i, k + int(o)), xo * FleaKit.anchor(pp, "g%d" % k), FleaData.h(hid, i, k))
			if canopy and kind != FleaData.KIND_DOUBLE:
				_kput(ch, "fm_canopy_3x3", xo * FleaKit.anchor(pp, "canopy"), var_, over)
		if canopy and kind == FleaData.KIND_DOUBLE and FleaKit.has("fm_canopy_3x6"):
			_kput(ch, "fm_canopy_3x6", x0 * Transform3D(Basis(Vector3.UP, PI * 0.5), Vector3.ZERO), var_, over)


func _stand_in_stalls(chunks: Dictionary, M: Dictionary, job: Dictionary, kinds: PackedByteArray, cats: PackedByteArray, who: PackedInt32Array, hid: int, shed_col: Color, steel: Color, white: Color) -> void:
	## (no kit yet: sheds and stalls as vertex-coloured boxes)
	var stalls: Array = M.stalls
	# -- sheds: per 3 m slice (its own ground height), portal frame, gable roof, back walls, partitions
	var shed_stalls := {}
	for i in stalls.size():
		var s: Array = stalls[i]
		if int(s[5]) >= 0:
			shed_stalls[Vector2i(int(s[5]), roundi(float(s[0]) * 10.0))] = shed_stalls.get(Vector2i(int(s[5]), roundi(float(s[0]) * 10.0)), []) + [i]
	for sh in M.sheds:
		var u0 := float(sh.u0)
		var v0 := float(sh.v0)
		var v1 := float(sh.v1)
		var n_sl := roundi((float(sh.u1) - u0) / 3.0)
		var vm := (v0 + v1) * 0.5
		for j in n_sl:
			var uc := u0 + 3.0 * (j + 0.5)
			var P := _piece(chunks, uc, vm, 0.0)
			var ch: Chunk = P[0]
			var c: Vector3 = P[1]
			var r: Vector3 = P[2]
			var f: Vector3 = P[3]
			var half := (v1 - v0) * 0.5
			# roof: two slopes from the eaves (3.6 m) to the ridge (4.7 m)
			var e0 := c - f * (half + 0.6) + Vector3.UP * 3.6
			var e1 := c + f * (half + 0.6) + Vector3.UP * 3.6
			var rg := c + Vector3.UP * 4.7
			ch.nm += _quad(ch.mid, e0 - r * 1.5, e0 + r * 1.5, rg + r * 1.5, rg - r * 1.5, shed_col)
			ch.nm += _quad(ch.mid, rg - r * 1.5, rg + r * 1.5, e1 + r * 1.5, e1 - r * 1.5, shed_col)
			# back walls on both long sides, the bay partitions, a column every 6 m
			for sd: float in [-1.0, 1.0]:
				var wc: Vector3 = c + f * sd * (half - 0.1) + Vector3.UP * 1.7
				ch.nm += _box(ch.mid, wc, r, f, Vector3(3.0, 3.4, 0.16), shed_col.darkened(0.15))
				if j % 2 == 0:
					ch.nm += _box(ch.mid, c + f * sd * (half - 0.25) - r * 1.5 + Vector3.UP * 1.8, r, f, Vector3(0.22, 3.6, 0.22), steel)
				ch.nm += _box(ch.mid, c + f * sd * (half - 2.5) - r * 1.5 + Vector3.UP * 1.2, r, f, Vector3(0.06, 2.4, 3.0), shed_col.lightened(0.25))
			if j == 0 or j == n_sl - 1:
				ch.boxes.append([Transform3D(Basis(r, Vector3.UP, f), c + Vector3.UP * 1.7), Vector3(3.0, 3.4, (v1 - v0))])
			else:
				for sd: float in [-1.0, 1.0]:
					ch.boxes.append([Transform3D(Basis(r, Vector3.UP, f), c + f * sd * (half - 0.1) + Vector3.UP * 1.7), Vector3(3.0, 3.4, 0.3)])
	# -- the stalls
	for i in stalls.size():
		var s: Array = stalls[i]
		var kind := int(s[3])
		var yaw := float(s[2])
		var P := _piece(chunks, float(s[0]), float(s[1]), yaw)
		var ch: Chunk = P[0]
		var c: Vector3 = P[1]
		var r: Vector3 = P[2]
		var f: Vector3 = P[3]
		var held := i < kinds.size() and kinds[i] != 0
		var isl := held and kinds[i] == FleaVendors.K_ISLANDER
		var open_: bool = held and ((isl and bool(job.islander)) or (not isl and bool(job.local)))
		var gcol: Color = GOODS.get(FleaData.categories[cats[i]] if i < cats.size() and cats[i] < FleaData.categories.size() else "household", Color(0.6, 0.6, 0.6))
		var cloth: Color = CANVAS[posmod(FleaData.h(hid, i, 7), CANVAS.size())]
		if isl:
			var isl_d: Dictionary = FleaData.islands()[-10 - who[i]] if who[i] <= -10 else {}
			var cs: Array = isl_d.get("colors", [])
			if not cs.is_empty():
				cloth = Color(str(cs[posmod(i, cs.size())]))
		match kind:
			FleaData.KIND_SHED:
				# the roll shutter at the bay's front: down, or rolled up when its tenant trades
				var fr := c + f * 1.45
				if open_:
					ch.nm += _box(ch.mid, fr + Vector3.UP * 2.35, r, f, Vector3(2.9, 0.35, 0.3), steel)
					ch.nn += _box(ch.near, c + f * 0.6 + Vector3.UP * 0.4, r, f, Vector3(2.4, 0.8, 0.7), Color(0.5, 0.36, 0.22))
					ch.nn += _goods(ch.near, c + f * 0.6 + Vector3.UP * 0.8, r, f, gcol, hid, i)
					ch.nn += _box(ch.near, c - f * 1.2 + Vector3.UP * 1.0, r, f, Vector3(2.6, 2.0, 0.08), gcol.lightened(0.3))
					if isl:
						ch.nn += _box(ch.near, fr + Vector3.UP * 2.0, r, f, Vector3(2.8, 0.5, 0.04), cloth)
				else:
					ch.nm += _box(ch.mid, fr + Vector3.UP * 1.25, r, f, Vector3(2.9, 2.5, 0.06), steel.lightened(0.2))
			FleaData.KIND_FOOD:
				ch.np += _outline(ch.paint, c, r, f, 4.0, 8.0)
				if open_:
					var tc: Color = CANVAS[posmod(FleaData.h(hid, i, 9), CANVAS.size())]
					ch.nm += _box(ch.mid, c + Vector3.UP * 1.55, r, f, Vector3(2.3, 2.5, 6.2), tc)
					ch.nm += _box(ch.mid, c + f * 2.2 + Vector3.UP * 1.9, r, f, Vector3(2.32, 0.9, 1.0), Color(0.1, 0.1, 0.12))
					ch.nm += _box(ch.mid, c + f * 3.15 + Vector3.UP * 1.0, r, f, Vector3(2.0, 0.08, 0.3), white)
					ch.boxes.append([Transform3D(Basis(r, Vector3.UP, f), c + Vector3.UP * 1.55), Vector3(2.3, 2.8, 6.2)])
			_:
				var w_ := 6.0 if kind == FleaData.KIND_DOUBLE else 3.0
				ch.np += _outline(ch.paint, c, r, f, w_, 3.0)
				if open_:
					var tw := 2.0 if kind != FleaData.KIND_DOUBLE else 4.6
					ch.nn += _box(ch.near, c + f * 0.55 + Vector3.UP * 0.74, r, f, Vector3(tw, 0.05, 0.8), Color(0.88, 0.86, 0.8))
					for lx: float in [-tw * 0.45, tw * 0.45]:
						ch.nn += _box(ch.near, c + f * 0.55 + r * lx + Vector3.UP * 0.36, r, f, Vector3(0.05, 0.72, 0.7), steel)
					ch.nn += _goods(ch.near, c + f * 0.55 + Vector3.UP * 0.77, r, f, gcol, hid, i)
					if isl or FleaData.u(hid, i, 11) < 0.62:
						# a pop-up canopy (3 x 3, 2.4 m), its cloth in the vendor's colour
						for lx: float in [-w_ * 0.47, w_ * 0.47]:
							for lz: float in [-1.4, 1.4]:
								ch.nn += _box(ch.near, c + r * lx + f * lz + Vector3.UP * 1.2, r, f, Vector3(0.04, 2.4, 0.04), steel)
						var top := c + Vector3.UP * 2.45
						var pk := c + Vector3.UP * 3.0
						var hw := w_ * 0.5
						for q in [[-r * hw - f * 1.5, r * hw - f * 1.5], [r * hw - f * 1.5, r * hw + f * 1.5],
								[r * hw + f * 1.5, -r * hw + f * 1.5], [-r * hw + f * 1.5, -r * hw - f * 1.5]]:
							ch.nn += _tri(ch.near, top + q[0], top + q[1], pk, cloth)


func _tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, col: Color) -> int:
	st.set_color(col)
	st.set_normal((b - a).cross(c - a).normalized())
	for p in [a, b, c]:
		st.add_vertex(p)
	return 3


func _outline(st: SurfaceTool, c: Vector3, r: Vector3, f: Vector3, w: float, d: float) -> int:
	## a pitch's painted outline: four 8 cm lines, 2 cm above the ground
	var n := 0
	var col := Color(0.86, 0.86, 0.8)
	var up := Vector3.UP * 0.03
	for e in [[-r * w * 0.5 - f * d * 0.5, r * w * 0.5 - f * d * 0.5, f], [-r * w * 0.5 + f * d * 0.5, r * w * 0.5 + f * d * 0.5, f],
			[-r * w * 0.5 - f * d * 0.5, -r * w * 0.5 + f * d * 0.5, r], [r * w * 0.5 - f * d * 0.5, r * w * 0.5 + f * d * 0.5, r]]:
		var a: Vector3 = c + e[0] + up
		var b: Vector3 = c + e[1] + up
		var o: Vector3 = (e[2] as Vector3) * 0.04
		n += _quad(st, a - o, b - o, b + o, a + o, col)
	return n


func _goods(st: SurfaceTool, top: Vector3, r: Vector3, f: Vector3, col: Color, hid: int, i: int) -> int:
	## a few boxes and stacks on the table in the category's colours (the KIT's fm_goods_* replace these)
	var n := 0
	for k in 4:
		var u := FleaData.u(hid, i, 13, k)
		var sx := 0.25 + 0.3 * u
		var sy := 0.08 + 0.35 * FleaData.u(hid, i, 17, k)
		var lx := (k - 1.5) * 0.45
		n += _box(st, top + r * lx + Vector3.UP * sy * 0.5, r, f, Vector3(sx, sy, 0.3 + 0.2 * u), col.lightened(0.25 * u).darkened(0.2 * (1.0 - u)))
	return n


# ------------------------------------------------------------------ main thread
func _commit(d: Dictionary) -> void:
	var id: String = d.id
	if _jobs.has(id):
		WorkerThreadPool.wait_for_task_completion(_jobs[id])
		_jobs.erase(id)
	if _built.has(id):
		(_built[id].node as Node).queue_free()
	var root := Node3D.new()
	root.name = "FleaMarket_" + id
	add_child(root)
	var verts := 0
	for e in d.chunks:
		var holder := Node3D.new()
		holder.transform = e.xf
		root.add_child(holder)
		for nm in ["mid", "near", "paint"]:
			if not e.has(nm):
				continue
			var am := ArrayMesh.new()
			am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, e[nm])
			verts += (e[nm][Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
			var mi := MeshInstance3D.new()
			mi.mesh = am
			mi.material_override = _paint_mat if nm == "paint" else _mat
			mi.visibility_range_end = MID_R if nm == "mid" else NEAR_R
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if nm == "mid" else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			holder.add_child(mi)
		for tier in ["kn", "km"]:
			for g in (e.get(tier, {}) as Dictionary):
				var arr: Array = e[tier][g]
				var am2 := ArrayMesh.new()
				am2.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
				verts += (arr[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
				var mk := MeshInstance3D.new()
				mk.mesh = am2
				mk.material_override = FleaKit.material(g)
				if tier == "kn":
					mk.visibility_range_end = NEAR_R
				else:
					mk.visibility_range_begin = NEAR_R
					mk.visibility_range_end = MID_R
				mk.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if g in ["solid", "metal"] else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				holder.add_child(mk)
		if not (e.get("ramps", PackedVector3Array()) as PackedVector3Array).is_empty():
			var rb := StaticBody3D.new()
			holder.add_child(rb)
			var rcs := CollisionShape3D.new()
			var cps := ConcavePolygonShape3D.new()
			cps.set_faces(e.ramps)
			rcs.shape = cps
			rb.add_child(rcs)
		if not (e.boxes as Array).is_empty():
			var body := StaticBody3D.new()
			holder.add_child(body)
			for bx in e.boxes:
				var cs := CollisionShape3D.new()
				var sh := BoxShape3D.new()
				sh.size = bx[1]
				cs.shape = sh
				cs.transform = bx[0]
				body.add_child(cs)
	if _sign_mat and _sign_uv.has(id):
		var uv: Rect2 = _sign_uv[id]
		for sg in d.signs:
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			var c: Vector3 = sg.c
			var r: Vector3 = sg.r
			var w := float(sg.w)
			var hh := w * 0.5
			# both faces: toward the road (-f) and back
			for fs: float in [-1.0, 1.0]:
				var off: Vector3 = (sg.f as Vector3) * 0.05 * fs
				var rr: Vector3 = r * (-float(fs))
				var q := [c - rr * hh - Vector3.UP * hh + off, c + rr * hh - Vector3.UP * hh + off, c + rr * hh + Vector3.UP * hh + off, c - rr * hh + Vector3.UP * hh + off]
				var uvs := [Vector2(uv.position.x, uv.end.y), Vector2(uv.end.x, uv.end.y), Vector2(uv.end.x, uv.position.y), Vector2(uv.position.x, uv.position.y)]
				st.set_normal((sg.f as Vector3) * fs)
				for k in [0, 1, 2, 0, 2, 3]:
					st.set_uv(uvs[k])
					st.add_vertex(q[k])
			var mi := MeshInstance3D.new()
			mi.mesh = st.commit()
			mi.material_override = _sign_mat
			mi.visibility_range_end = 2400.0
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var holder := Node3D.new()
			holder.transform = sg.xf
			root.add_child(holder)
			holder.add_child(mi)
	_built[id] = {"node": root, "key": d.key, "chunks": (d.chunks as Array).size(), "verts": verts}


func _exit_tree() -> void:
	for id in _jobs:
		WorkerThreadPool.wait_for_task_completion(_jobs[id])
	_jobs.clear()


func stats() -> Dictionary:
	var draws := 0
	var verts := 0
	for id in _built:
		var n: Node = _built[id].node
		for h in n.get_children():
			draws += h.get_child_count()
		verts += int(_built[id].verts)
	return {"built": _built.keys(), "draws_est": draws, "verts": verts, "jobs": _jobs.size()}


# ------------------------------------------------------------------ where people stand (NpcPopulation)
static func stall_point(M: Dictionary, i: int, ahead: float) -> Vector2:
	## (s, x) of a point `ahead` m in front of stall i (negative: behind its table)
	var s: Array = (M.stalls as Array)[i]
	var yaw := float(s[2])
	var reach := ahead + (4.0 if int(s[3]) == FleaData.KIND_FOOD else 0.0)
	return FleaData.to_world(M, float(s[0]) + sin(yaw) * reach, float(s[1]) + cos(yaw) * reach)


static func vendor_spot(pid: String, day: int) -> Vector2:
	var v := FleaVendors.vending(pid, day)
	if v.is_empty():
		return Vector2.INF
	return stall_point(FleaData.market(str(v.market)), int(v.stall), -0.4)


static func shopper_spot(market: String, pid: String, day: int, k: int) -> Vector2:
	var M := FleaData.market(market)
	if M.is_empty() or (M.stalls as Array).is_empty():
		return Vector2.INF
	var n := (M.stalls as Array).size()
	# a browse along one aisle: a hashed start stall, then its neighbours in the row
	var h0 := NpcRng.fnv1a64(pid)
	var i0 := int(FleaData.u(h0, day, 3) * n)
	var i := clampi(i0 + k * (1 if FleaData.u(h0, day, 5) < 0.5 else -1), 0, n - 1)
	return stall_point(M, i, 2.4 + FleaData.u(h0, day, 7 + k) * 1.0)

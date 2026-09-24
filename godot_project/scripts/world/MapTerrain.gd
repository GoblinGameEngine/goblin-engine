extends RefCounted
class_name MapTerrain

## The ring floor's terrain as tools/map_preview.py draws it -- the map the remake world is built
## to (settlements, structures, roads and water all come from it).  A pure leaf: no other
## class_name script is called from here, so TerrainHeight can delegate to it without a cycle.
##
## Closed-form (ported from map_preview.py, same parameters):
##   river centreline  rx(s)        A1/A2/A3 harmonic stack (identical to TerrainHeight.river_x)
##   Lake Tamsin       lake_params  1,000 m x 300 m, necked 130 m at both ends, centred s = pi/4 R
##   bluffs            base_elev    asymmetric: cut-bank side steep and close, point-bar side
##                                  far and gentle; the lake's +x (Harrow Falls) shore is bluff;
##                                  a k=1 regional tilt; gentle noise (periodic here -- the
##                                  preview's isn't, and would step 2 m at s = 0)
## Data (res://remake/terrain.json, written by map_preview.py --terrain): creeks and spurs
## (polylines), ponds (ellipses), oxbow lakes (polygons), field ditches (runs along s).
##
## elevation(s, x) = base_elev - water_depth: + up (toward the axis), metres.

const PATH := "res://remake/terrain.json"
const CELL := 64.0                   # spatial grid for the polyline/polygon features

static var _d: Dictionary = {}
static var _grid: Dictionary = {}    # Vector2i -> Array of [kind, index]
static var R := 500.0
static var C := TAU * 500.0


static func _load() -> void:
	if not _d.is_empty():
		return
	_d = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	R = _d.R
	C = TAU * R
	# index every feature's bounding box (grown by its bank) into the grid
	for i in _d.creeks.size():
		var cr: Dictionary = _d.creeks[i]
		var pts: Array = cr.pts
		for k in pts.size() - 1:
			_index(["seg", i, k], pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], cr.hw + 4.0)
	for i in _d.ponds.size():
		var p: Dictionary = _d.ponds[i]
		_index(["pond", i], p.s - p.a, p.x - p.a, p.s + p.a, p.x + p.a, 8.0)
	for i in _d.oxbows.size():
		var poly: Array = _d.oxbows[i].poly
		var lo := Vector2(1e9, 1e9)
		var hi := Vector2(-1e9, -1e9)
		for q in poly:
			lo = Vector2(minf(lo.x, q[0]), minf(lo.y, q[1]))
			hi = Vector2(maxf(hi.x, q[0]), maxf(hi.y, q[1]))
		_index(["oxbow", i], lo.x, lo.y, hi.x, hi.y, 8.0)
	for i in _d.ditches.size():
		var dt: Dictionary = _d.ditches[i]
		_index(["ditch", i], dt.s0, dt.x, dt.s1, dt.x, dt.hw + 2.0)


static func _index(item: Array, s0: float, x0: float, s1: float, x1: float, grow: float) -> void:
	for cs in range(floori((minf(s0, s1) - grow) / CELL), floori((maxf(s0, s1) + grow) / CELL) + 1):
		for cx in range(floori((minf(x0, x1) - grow) / CELL), floori((maxf(x0, x1) + grow) / CELL) + 1):
			var key := Vector2i(posmod(cs, ceili(C / CELL)), cx)
			if not _grid.has(key):
				_grid[key] = []
			_grid[key].append(item)


static func _wrap(ds: float) -> float:
	return fposmod(ds + C * 0.5, C) - C * 0.5


# ------------------------------------------------------------------ river and lake
static func rx(s: float) -> float:
	_load()
	var r: Dictionary = _d.river
	var th := s / R
	var env: float = r.A[0] * (1.0 + 0.3 * sin(2.0 * th + r.phi[3]))
	return env * sin(6.0 * th + r.phi[0]) + r.A[1] * sin(13.0 * th + r.phi[1]) + r.A[2] * sin(th + r.phi[2])


static func lake_params(s: float) -> Vector4:
	## (taper t 0..1, centre x, half-width toward -x, half-width toward +x); t = 0 away from the lake
	_load()
	var lk: Dictionary = _d.lake
	var ch: float = _d.river.ch_half
	var d := _wrap(s - lk.s)
	var t := clampf((lk.half_len - absf(d)) / lk.neck, 0.0, 1.0)
	t = t * t * (3.0 - 2.0 * t)
	var cx := rx(s) * (1.0 - t)
	var ht: float = ch + (lk.hw - ch + 22.0 * sin(d / 41.0) + 12.0 * sin(d / 17.0 + 1.3)) * t
	var hb: float = ch + (lk.hw - ch + 6.0 * sin(d / 63.0 + 0.4)) * t
	return Vector4(t, cx, ht, hb)


static func water_edges(s: float) -> Vector2:
	## (-x edge, +x edge) of the river / lake at s
	var lp := lake_params(s)
	var ch: float = _d.river.ch_half
	if lp.x > 0.0:
		return Vector2(minf(lp.y - ch, lp.y - lp.z), maxf(lp.y + ch, lp.y + lp.w))
	return Vector2(lp.y - ch, lp.y + ch)


# ------------------------------------------------------------------ terrain
static func base_elev(s: float, x: float) -> float:
	## The bluff / floodplain terrain before any water is carved.
	_load()
	var r: Dictionary = _d.river
	var th := s / R
	var lp := lake_params(s)
	var t := lp.x
	var b := tanh(1.5 * sin(6.0 * th + r.phi[0])) / tanh(1.5)
	b = b * (1.0 - t) + t                          # the lake: bluff on the +x shore
	var side := -1.0 if x < lp.y else 1.0
	var e := water_edges(s)
	var dist := (e.x - x) if x < e.x else ((x - e.y) if x > e.y else 0.0)
	var w_cut := 0.5 * (1.0 + b * side)
	var d0_cut := 60.0 * (1.0 - t) + 140.0 * t
	var d0 := 230.0 - (230.0 - d0_cut) * w_cut
	var lb := 160.0 - 85.0 * w_cut
	var hgt: float = _d.bluff.H * (1.0 + 0.3 * sin(2.0 * th + r.phi[3]))
	# the preview's noise, made periodic round the ring (5 and 15 cycles ~ its 97 m / 211 m waves)
	var noise := 1.2 * sin(TAU * 5.0 * s / C + x / 131.0) + 0.8 * sin(x / 53.0 - TAU * 15.0 * s / C)
	return hgt * maxf(0.0, tanh((dist - d0) / lb)) - _d.bluff.Z1 * cos(th - PI * 0.25) + noise


static func _trap(au: float, bed_hw: float, bank_w: float, depth: float) -> float:
	if au <= bed_hw:
		return depth
	if au >= bed_hw + bank_w:
		return 0.0
	var f := (au - bed_hw) / bank_w
	return depth * (1.0 - f * f * (3.0 - 2.0 * f))


static func water_depth(s: float, x: float) -> float:
	## How far the floor is carved down at (s, x) by any water feature (0 on dry land).
	_load()
	s = fposmod(s, C)
	var r: Dictionary = _d.river
	var lp := lake_params(s)
	var dep := 0.0
	# river channel (it runs through the lake too, as the deepest line)
	dep = maxf(dep, _trap(absf(x - lp.y), r.bed_half, r.ch_half - r.bed_half + 4.0, r.depth))
	if lp.x > 0.0:
		var lk: Dictionary = _d.lake
		var lo := lp.y - lp.z
		var hi := lp.y + lp.w
		if x > lo - 6.0 and x < hi + 6.0:
			var inside := minf(x - lo, hi - x)                  # metres in from the shore (<0 outside)
			dep = maxf(dep, lk.depth * lp.x * smoothstep(-6.0, lk.shelf, inside))
	var key := Vector2i(floori(s / CELL), floori(x / CELL))
	for it in _grid.get(key, []):
		match it[0]:
			"seg":
				var cr: Dictionary = _d.creeks[it[1]]
				var a: Array = cr.pts[it[2]]
				var bq: Array = cr.pts[it[2] + 1]
				dep = maxf(dep, _trap(_seg_dist(s, x, a[0], a[1], bq[0], bq[1]), cr.hw, 3.0, cr.depth))
			"pond":
				var p: Dictionary = _d.ponds[it[1]]
				var ds := _wrap(s - p.s)
				var dx: float = x - p.x
				var rot: float = p.rot
				var u: float = (ds * cos(rot) + dx * sin(rot)) / p.a
				var v: float = (-ds * sin(rot) + dx * cos(rot)) / p.b
				var rr := sqrt(u * u + v * v)                      # 1 at the shore
				dep = maxf(dep, p.depth * smoothstep(1.15, 0.7, rr))
			"oxbow":
				var ox: Dictionary = _d.oxbows[it[1]]
				var inside := _poly_inside_dist(ox.poly, s, x)
				dep = maxf(dep, ox.depth * smoothstep(-4.0, 10.0, inside))
			"ditch":
				var dt: Dictionary = _d.ditches[it[1]]
				if s >= dt.s0 - 1.0 and s <= dt.s1 + 1.0:
					dep = maxf(dep, _trap(absf(x - dt.x), dt.hw, 1.5, dt.depth))
	return dep


static func elevation(s: float, x: float) -> float:
	return base_elev(s, x) - water_depth(s, x)


static func water_level(s: float) -> float:
	## Height of the river / lake surface at s: just below the lower bank.
	var e := water_edges(s)
	return minf(base_elev(s, e.x - 1.0), base_elev(s, e.y + 1.0)) - 0.35


# ------------------------------------------------------------------ geometry helpers
static func _seg_dist(s: float, x: float, s0: float, x0: float, s1: float, x1: float) -> float:
	var ps := _wrap(s - s0)
	var bs := _wrap(s1 - s0)
	var px := x - x0
	var bx := x1 - x0
	var l2 := bs * bs + bx * bx
	var t := 0.0 if l2 < 1e-6 else clampf((ps * bs + px * bx) / l2, 0.0, 1.0)
	return Vector2(ps - bs * t, px - bx * t).length()


static func _poly_inside_dist(poly: Array, s: float, x: float) -> float:
	## Signed distance to a polygon's edge: + inside, - outside.
	var inside := false
	var dmin := 1e9
	var n := poly.size()
	for i in n:
		var a: Array = poly[i]
		var bq: Array = poly[(i + 1) % n]
		dmin = minf(dmin, _seg_dist(s, x, a[0], a[1], bq[0], bq[1]))
		var sa := _wrap(a[0] - s)
		var sb := _wrap(bq[0] - s)
		if ((a[1] > x) != (bq[1] > x)) and (0.0 < sa + (sb - sa) * (x - a[1]) / (bq[1] - a[1])):
			inside = not inside
	return dmin if inside else -dmin

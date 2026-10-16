extends RefCounted
class_name FleaData

## The flea markets' data (research/flea_markets/00_plan.md §3.2): remake/markets/flea_markets.json (the 22 sited
## markets: frames, stalls, lot rows, poles, tent slots ...), the islands that moor at them (remake/bible/
## sky_islands.json) and the shared hash every pure market function draws from.
##
##   FleaData.markets()          -> [market dict]   (the file's, plus "hid", "ix", "kind" PackedByteArray, "perm" PackedByteArray)
##   FleaData.market("FM-SOL")   -> market dict ({} if none)
##   FleaData.of_town("Calder")  -> market dict
##   FleaData.islands()          -> [{id, hid, name, pop, blocks, specialty, factor, eligible, colors}]
##   FleaData.u(a, b, c, d)      -> a hash in [0, 1) of four ints (pure; the same on every machine)
##   FleaData.to_world(m, u, v)  -> Vector2(s, x) of a point in the market's site frame

const PATH := "res://remake/markets/flea_markets.json"
const ISLANDS := "res://remake/bible/sky_islands.json"
const SEED := 0x5ca1ab1e                 # the markets' stream (the world seed 1 is folded in: change both together)
const KIND_SHED := 0
const KIND_OPEN := 1
const KIND_DOUBLE := 2
const KIND_FOOD := 3
# what an island must trade to host a market mooring (00 §5.1: specialty in a trade set, or factors >= 10)
const TRADE_SET := ["trade", "knitwear", "honey", "bells", "ice", "fish", "dried", "cordage", "skycloth", "brewing", "wool",
	"gardens", "moss", "down", "larks"]

static var _loaded := false
static var _markets: Array = []
static var _by_id := {}
static var _by_town := {}
static var _islands: Array = []
static var _isl_by_id := {}
static var categories: Array = []
static var _mx := Mutex.new()


static func _load() -> void:
	if _loaded:
		return
	_mx.lock()
	if _loaded:
		_mx.unlock()
		return
	var d = DataFile.json(PATH)
	if d is Dictionary:
		categories = d.get("categories", [])
		var i := 0
		for m in d.get("markets", []):
			var st: Array = m.get("stalls", [])
			var kind := PackedByteArray()
			kind.resize(st.size())
			var perm := PackedByteArray()
			perm.resize(st.size())
			var nfood := 0
			for s in st:
				if int(s[3]) == KIND_FOOD:
					nfood += 1
			var food_i := 0
			for k in st.size():
				var kk := int(st[k][3])
				kind[k] = kk
				if kk == KIND_SHED:
					perm[k] = 1
				elif kk == KIND_FOOD:
					perm[k] = 1 if food_i < nfood / 2 else 0       # (food pads: half permanent, half rotating)
					food_i += 1
			m["kind"] = kind
			m["perm"] = perm
			m["hid"] = NpcRng.fnv1a64(str(m.id))
			m["ix"] = i
			i += 1
			_markets.append(m)
			_by_id[m.id] = m
			_by_town[m.town] = m
	else:
		push_warning("FleaData: %s missing (tools/markets/make_markets.py)" % PATH)
	var b = DataFile.json(ISLANDS)
	if b is Dictionary:
		for isl in b.get("islands", []):
			var fac := int((isl.get("jobs", {}) as Dictionary).get("factor", 0))
			var e := {"id": isl.id, "hid": NpcRng.fnv1a64(str(isl.id)), "name": isl.get("name", isl.id),
				"pop": int(isl.get("population", 500)), "blocks": int(isl.get("blocks", 3)),
				"specialty": str(isl.get("specialty", "")), "factor": fac, "colors": isl.get("colors", []),
				"trade": isl.get("trade", [])}
			e["eligible"] = fac >= 10 or str(e.specialty) in TRADE_SET
			e["ix"] = _islands.size()
			_islands.append(e)
			_isl_by_id[e.id] = e
	_loaded = true
	_mx.unlock()


static func markets() -> Array:
	_load()
	return _markets


static func market(id: String) -> Dictionary:
	_load()
	return _by_id.get(id, {})


static func of_town(town: String) -> Dictionary:
	_load()
	return _by_town.get(town, {})


static func islands() -> Array:
	_load()
	return _islands


static func island(id: String) -> Dictionary:
	_load()
	return _isl_by_id.get(id, {})


# -- the hash ---------------------------------------------------------------------------------------------------

static func mix(z: int) -> int:
	## splitmix64's finaliser (GDScript ints wrap: the unsigned maths, with logical right shifts)
	z = (z ^ NpcRng.lsr(z, 30)) * NpcRng.MIX1
	z = (z ^ NpcRng.lsr(z, 27)) * NpcRng.MIX2
	return z ^ NpcRng.lsr(z, 31)


static func h(a: int, b: int = 0, c: int = 0, d: int = 0) -> int:
	var x := mix(SEED + a * NpcRng.GOLDEN)
	x = mix(x ^ (b + NpcRng.GOLDEN))
	x = mix(x ^ (c * 31 + NpcRng.GOLDEN))
	return mix(x ^ (d * 131 + NpcRng.GOLDEN))


static func u(a: int, b: int = 0, c: int = 0, d: int = 0) -> float:
	## [0, 1)
	return float(NpcRng.lsr(h(a, b, c, d), 11)) / NpcRng.TWO53


# -- geometry ---------------------------------------------------------------------------------------------------

static func to_world(m: Dictionary, uu: float, vv: float) -> Vector2:
	var f: Dictionary = m.get("frame", {})
	var a := float(f.get("yaw", 0.0))
	return Vector2(fposmod(float(f.get("s", 0.0)) + uu * cos(a) - vv * sin(a), StationGeo.CIRC),
		float(f.get("x", 0.0)) + uu * sin(a) + vv * cos(a))


static func centre(m: Dictionary) -> Vector2:
	## the market floor's middle on the ring (s, x)
	var c = m.get("centre_sx")
	if c is Array and c.size() == 2:
		return Vector2(float(c[0]), float(c[1]))
	var f: Dictionary = m.get("frame", {})
	return Vector2(float(f.get("s", 0.0)), float(f.get("x", 0.0)))

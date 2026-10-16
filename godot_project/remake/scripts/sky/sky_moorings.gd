extends Node
class_name SkyMoorings

## The market moorings near the player (research/flea_markets/00_plan.md §5; handoff_sky.md): one SkyMooringSite per
## market with an island booked there (SkyMooring, inside SkyDrift), within SITE_R of the camera -- the drop cage,
## the hawsers, the logistics tents, the ground stations and the jig-back ropeways, the islanders' trading tents and
## their lights.  Child of SkyIslands (it reads the drift, the islands and the player).
##
##   sites                    market id -> SkyMooringSite
##   stats()                  {sites, cabins, tents, bulbs, draws_est, ...}
##   ride(market_id)          the player into the nearest passenger cabin at its ground berth (tests, the PDA)
##   claims                   [[world pos, colour, range, energy]] the sites' borrowed lights (StreetLights takes <= 8)

const SITE_R := 3200.0
const FREE_R := 3800.0
const TICK := 0.5

var sys: SkyIslands
var sites := {}
var _t := 0.0
var _lights: Node


func _ready() -> void:
	name = "SkyMoorings"
	process_physics_priority = -9                  # (after SkyIslands placed the islands, before the player moves)


func _process(delta: float) -> void:
	if sys == null or not sys.is_ready() or sys.drift == null or sys.drift.mooring == null:
		return
	_t -= delta
	if _t > 0.0:
		return
	_t = TICK
	Prof.begin("sky.moorings")
	var cam := sys.player.camera.global_position if sys.player and sys.player.camera else Vector3.ZERO
	var here := Vector2(StationGeo.s_of(cam), cam.x)
	var mk := sys.drift.mooring.markets()
	for id in mk:
		var M := FleaData.market(str(id))
		if M.is_empty() or not M.get("sited", false):
			continue
		var c := FleaData.centre(M)
		var d := Vector2(StationGeo.wrap_ds(c.x - here.x), c.y - here.y).length()
		if d < SITE_R and not sites.has(id):
			var s := SkyMooringSite.new()
			s.sys = sys
			s.M = M
			s.market_id = str(id)
			add_child(s)
			sites[id] = s
	for id in sites.keys():
		var s: SkyMooringSite = sites[id]
		var c := FleaData.centre(s.M)
		var d := Vector2(StationGeo.wrap_ds(c.x - here.x), c.y - here.y).length()
		if d > FREE_R or (not mk.has(id) and s.idle()):
			s.release()
			s.queue_free()
			sites.erase(id)
	# the borrowed real lights: the nearest of every site's lamps (StreetLights places <= 8 of them)
	if _lights == null or not is_instance_valid(_lights):
		_lights = get_tree().current_scene.find_child("StreetLights", true, false) if get_tree().current_scene else null
	if _lights and "borrowed" in _lights:
		var cl: Array = []
		for id in sites:
			cl.append_array((sites[id] as SkyMooringSite).lamps)
		_lights.borrowed = cl
	Prof.end("sky.moorings")


func ride(market_id: String) -> bool:
	var s: SkyMooringSite = sites.get(market_id)
	return s != null and s.board_player()


func stats() -> Dictionary:
	var out := {"sites": sites.size()}
	for id in sites:
		var st: Dictionary = (sites[id] as SkyMooringSite).stats()
		for k in st:
			if typeof(st[k]) in [TYPE_INT, TYPE_FLOAT]:
				out[k] = out.get(k, 0) + st[k]
			else:
				out[str(id) + "." + k] = st[k]
	return out

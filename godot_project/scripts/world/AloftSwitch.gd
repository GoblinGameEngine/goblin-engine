extends Node
class_name AloftSwitch

## High above the floor -- aboard a sky island, in a lark at cruising height -- the ground is only seen from far off and
## from above, so it is drawn as the far side is: the baked top-down images (remake/farside/f_*.webp by day, n_*.webp
## at night) on the terrain's coarse far tier, and nothing else (the user, 2026-10-14: "at the altitude of the islands,
## we don't need models for the ground, only textures").  Going up past ENTER m above the ground the near terrain tiers
## are dropped, the far side takes the whole floor, and the ground's models and simulations stop: road furniture, the
## street lamps' posts, pools and real lights (their far bulbs and the night image stay), the coastal walks, parked
## cars and bicycles, the people, the traffic and the trams.  Coming down past EXIT m it all comes back, streaming in
## well before the ground is close enough to see it.  StationGeo.aloft says which it is now.

const ENTER := 450.0                  # m above the ground (the camera): aloft above this ...
const EXIT := 380.0                   # ... and back on the ground below this
const CHECK := 0.25

var station: Node
var _t := 0.0


func _ready() -> void:
	name = "AloftSwitch"
	process_priority = -20


func _process(delta: float) -> void:
	_t -= delta
	if _t > 0.0 or station == null:
		return
	_t = CHECK
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var p := cam.global_position
	var s := StationGeo.s_of(p)
	var above := StationGeo.h_of(p) - maxf(MapTerrain.elevation(s, p.x), 0.0)
	var want := above > ENTER if not StationGeo.aloft else above > EXIT
	if want != StationGeo.aloft:
		set_aloft(want)


func set_aloft(on: bool) -> void:
	StationGeo.aloft = on
	print("AloftSwitch: %s" % ("aloft: the ground as images" if on else "down: the ground's models back"))
	var terrain := station.get_node_or_null("Terrain")
	if terrain and terrain.has_method("set_aloft"):
		terrain.set_aloft(on)
	var far := station.get_node_or_null("FarSide")
	if far and far.has_method("set_aloft"):
		far.set_aloft(on)
	for c in station.get_children():
		if c is StreetLights:
			(c as StreetLights).set_aloft(on)
	# what's only near the ground: hidden and stopped (process off also takes the parked and NPC bodies out of physics)
	for n in ["RoadFurniture", "Walks", "GroundVehicles", "Bicycles"]:
		_park(station.get_node_or_null(n), on)
	for v in ["npcs", "traffic", "transit"]:
		var nd = station.get(v)
		if nd is Node:
			_park(nd as Node, on)


static func _park(n: Node, on: bool) -> void:
	if n == null:
		return
	if n is Node3D:
		(n as Node3D).visible = not on
	n.process_mode = Node.PROCESS_MODE_DISABLED if on else Node.PROCESS_MODE_INHERIT

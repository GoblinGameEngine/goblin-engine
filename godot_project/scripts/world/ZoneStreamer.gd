extends Node
class_name ZoneStreamer

# Background zone-detail streaming, driven by the player's own arc-length
# position on the ring (RingCoords.s_from_position()) -- requested
# directly: only the buildings/crops/furniture NEAR the player should
# ever be resident; everything else stays as just its road skeleton
# (NeighborhoodGenerator.build_skeleton(), always-on, cheap) until the
# player gets close enough to warrant streaming the detail in.
#
# Checked on a timer (CHECK_INTERVAL), not every physics frame -- this is
# a coarse, infrequent decision (LOAD_RADIUS is hundreds of meters; the
# player can't cross that in one tick), so there's no reason to spend
# every frame's budget on it. Load and unload thresholds are DIFFERENT
# (hysteresis) so a player idling near a boundary doesn't repeatedly
# stream the same zone in and out.
#
# The actual load itself (NeighborhoodGenerator.load_zone_detail_async())
# is time-sliced internally (every zone generator's build_detail_async()
# awaits RingCoords.yield_frame() periodically) -- this script fires it
# WITHOUT awaiting (see _stream_in_zone_async() below), so it runs in the
# background across many frames while everything else, including the
# player's own movement, keeps going normally. That's the actual "quiet"
# part: nothing here blocks a frame waiting for a zone to finish loading.

enum ZoneState { IDLE, LOADING, LOADED }

static var CHECK_INTERVAL := 0.4
static var LOAD_RADIUS := 400.0
static var UNLOAD_RADIUS := 550.0  # > LOAD_RADIUS: hysteresis gap, see file comment

var _root: Node3D
var _station: Node3D  # global_position origin for RingCoords.s_from_position() -- see StationPlayer._radial_vector()'s identical convention
var _radius: float
var _segments: int
var _zone_info: Array = []
var _state: Array = []
var _loaded_nodes: Array = []
var _accum := 0.0
var _player: Node3D

## Called once by SpaceStation._build_ring() right after
## NeighborhoodGenerator.build_skeleton() -- resets all tracked state,
## since rebuild_ring() frees the whole previous ring (including any
## ZoneDetail_* nodes this streamer thought were loaded) before calling
## this again.
func init(root: Node3D, station: Node3D, radius: float, segments: int, zone_info: Array, player: Node3D) -> void:
	_root = root
	_station = station
	_radius = radius
	_segments = segments
	_zone_info = zone_info
	_player = player
	_state = []
	_loaded_nodes = []
	for i in range(zone_info.size()):
		_state.append(ZoneState.IDLE)
		_loaded_nodes.append(null)
	_accum = 0.0

func _process(delta: float) -> void:
	if _zone_info.is_empty() or _player == null or not is_instance_valid(_player):
		return
	_accum += delta
	if _accum < CHECK_INTERVAL:
		return
	_accum = 0.0
	_check_zones()

## Circular (wraparound-aware) arc-length distance from `s` to the
## nearest point in [s_start, s_end] (s_start < s_end, un-wrapped -- true
## for every zone's own range) -- 0.0 if s is already inside. `rel` is
## the forward (increasing-s) distance from s_start to s around the
## circle; s is inside the range exactly when that's <= the range's own
## span. Otherwise the answer is the shorter of the circular distance to
## each edge.
static func _dist_to_range(s: float, s_start: float, s_end: float, circumference: float) -> float:
	var rel := fposmod(s - s_start, circumference)
	var span := s_end - s_start
	if rel <= span:
		return 0.0
	var to_start := minf(rel, circumference - rel)
	var rel_end := fposmod(s - s_end, circumference)
	var to_end := minf(rel_end, circumference - rel_end)
	return minf(to_start, to_end)

func _check_zones() -> void:
	var rel: Vector3 = _player.global_position - _station.global_position
	var s_player := RingCoords.s_from_position(_radius, rel)
	var circumference := TAU * _radius

	for i in range(_zone_info.size()):
		var info: Dictionary = _zone_info[i]
		var dist := _dist_to_range(s_player, info["s_start"], info["s_end"], circumference)
		match _state[i]:
			ZoneState.IDLE:
				if dist < LOAD_RADIUS:
					_state[i] = ZoneState.LOADING
					_stream_in_zone_async(i)
			ZoneState.LOADED:
				if dist > UNLOAD_RADIUS:
					_unload_zone(i)
			ZoneState.LOADING:
				pass  # let it finish -- see file comment on why this can't cheaply cancel mid-flight

func _stream_in_zone_async(i: int) -> void:
	var node: Node3D = await NeighborhoodGenerator.load_zone_detail_async(_root, _radius, _segments, i, _zone_info[i])
	if node == null:
		_state[i] = ZoneState.IDLE
		return
	_loaded_nodes[i] = node
	_state[i] = ZoneState.LOADED
	# If the player already left UNLOAD_RADIUS again while this was
	# streaming in (can't be cancelled mid-flight -- see file comment),
	# free it right away instead of waiting for the next check tick to
	# notice.
	if _player and is_instance_valid(_player):
		var rel: Vector3 = _player.global_position - _station.global_position
		var s_player := RingCoords.s_from_position(_radius, rel)
		var info: Dictionary = _zone_info[i]
		if _dist_to_range(s_player, info["s_start"], info["s_end"], TAU * _radius) > UNLOAD_RADIUS:
			_unload_zone(i)

func _unload_zone(i: int) -> void:
	var node: Node3D = _loaded_nodes[i]
	if node and is_instance_valid(node):
		node.free()  # immediate, not queue_free() -- same reasoning as SpaceStation.rebuild_ring()'s own teardown: this can free and reload the same zone within one check interval if the player reverses course, and a freshly-instanced building/manifest name needs the old one's name slot free right away
	_loaded_nodes[i] = null
	_state[i] = ZoneState.IDLE

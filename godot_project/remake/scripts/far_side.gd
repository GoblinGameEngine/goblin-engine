extends Node
class_name RemakeFarSide

## The far side of the cylinder, drawn flat.  Beyond FLAT_ARC of arc round the ring from the
## player (central angle ~105 deg, ~790 m away), a building's relief is a few pixels and you see
## the floor almost face-on, so everything there is drawn as the baked top-down image of itself
## (remake/farside.png, FarsideBake.tscn) on the terrain's coarse far tier.  Hidden there:
## every non-landmark building and merged district mesh, the trees, roads and water.  The tall
## landmarks (spires, elevators, towers, silos -- what shows at that range) keep their own far
## versions.  Checked every CHECK s with HYST m of hysteresis.

const FLAT_ARC := 1.0e9              # off until farside.png is re-baked for the 3 km ring (then ~1,500 m of arc)
const HYST := 30.0
const CHECK := 0.25

var target: Node3D
var _entries: Array = []             # [Node3D, s of its centre, far now]
var _terrain: MapTerrainMesh
var _far_mat: ShaderMaterial              # the terrain's far tier (farside.gdshader)
var _t := 0.0


func setup(p_target: Node3D, terrain: MapTerrainMesh, detail: Texture2D) -> void:
	## Call before the terrain builds its far tier (it takes this material for it).
	target = p_target
	_terrain = terrain
	_far_mat = ShaderMaterial.new()
	_far_mat.shader = load("res://remake/shaders/farside.gdshader")
	_far_mat.set_shader_parameter("farside", load("res://remake/farside.png"))
	_far_mat.set_shader_parameter("detail", detail)
	_far_mat.set_shader_parameter("flat_arc", FLAT_ARC)
	_far_mat.set_shader_parameter("circ", StationGeo.CIRC)
	_far_mat.set_shader_parameter("image_w", StationGeo.FARSIDE_W)
	terrain.far_material = _far_mat


func add_node(n: Node3D) -> void:
	## Something the far side hides; its s is taken from its drawn centre (or its position).
	var c := n.global_position
	if n is GeometryInstance3D:
		c = (n as GeometryInstance3D).global_transform * (n as VisualInstance3D).get_aabb().get_center()
	_entries.append([n, StationGeo.s_of(c), false])


func add_children_of(parent: Node, skip: Callable = Callable()) -> void:
	for c in parent.get_children():
		if c is Node3D and (not skip.is_valid() or not skip.call(c)):
			add_node(c)


func _process(delta: float) -> void:
	_t -= delta
	if _t > 0.0 or target == null:
		return
	_t = CHECK
	var sp := StationGeo.s_of(target.global_position)
	for e in _entries:
		var n: Node3D = e[0]
		if not is_instance_valid(n):
			continue
		var d := absf(StationGeo.wrap_ds(e[1] - sp))
		var far: bool = d > FLAT_ARC + (-HYST if e[2] else HYST)
		if far != e[2]:
			e[2] = far
			n.visible = not far
	# the terrain's far tier switches per pixel (farside.gdshader): tell it where the player is
	_far_mat.set_shader_parameter("player_s", sp)

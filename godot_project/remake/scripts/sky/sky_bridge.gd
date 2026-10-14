extends Node3D
class_name SkyBridge

## One retractable bridge on a sky island's dock face (remake/sky/bridges/<style>.glb, bridge_styles.json from
## remake/blender/sky/parts_bridges.py).  Origin on the face, deck top at y 0, +Z out of the island.  Every style is
## animated the same way: each moving node has keys [deploy, {pos, rot (quaternion), scl}] local to its parent,
## lerped (slerped) between; deploy 0 is stowed, 1 is down, reaching 13 m to meet the other island's bridge nose to
## nose.  Its walking surface (the style's colliders, boxes on the moving nodes) only collides once it's down.

static var _styles := {}
static var _scenes := {}

var style := ""
var deploy := 0.0              # now
var target := 0.0              # where it's going
var seconds := 30.0            # stowed to down
var _nodes: Array = []         # [Node3D, keys]
var _bodies: Array[StaticBody3D] = []


static func styles() -> Dictionary:
	if _styles.is_empty():
		_styles = (JSON.parse_string(DataFile.text("res://remake/sky/bridges/bridge_styles.json")) as Dictionary).styles
	return _styles


func setup(p_style: String) -> void:
	style = p_style
	var st: Dictionary = styles().get(style, {})
	if st.is_empty():
		push_warning("SkyBridge: no style %s" % style)
		return
	seconds = float(st.get("seconds", 30.0))
	if not _scenes.has(style):
		_scenes[style] = load(st.glb)
	var inst: Node3D = (_scenes[style] as PackedScene).instantiate()
	add_child(inst)
	for e in st.nodes:
		var n := inst.find_child(e.node, true, false) as Node3D
		if n:
			_nodes.append([n, e["keys"]])
	for c in st.get("colliders", []):
		var host := inst.find_child(c.node, true, false) as Node3D
		if host == null:
			continue
		var body := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(c.size[0], c.size[1], c.size[2])
		cs.shape = box
		cs.position = Vector3(c.center[0], c.center[1], c.center[2])
		body.add_child(cs)
		host.add_child(body)
		_bodies.append(body)
	_pose()


func _process(delta: float) -> void:
	if deploy == target:
		return
	deploy = move_toward(deploy, target, delta / seconds)
	_pose()


func snap(d: float) -> void:
	deploy = d
	target = d
	_pose()


func _pose() -> void:
	for nk in _nodes:
		(nk[0] as Node3D).transform = _at(nk[1], deploy)
	var down := deploy >= 0.98
	for b in _bodies:
		b.collision_layer = 1 if down else 0


static func _at(keys: Array, d: float) -> Transform3D:
	var k1 := 0
	while k1 < keys.size() - 1 and float(keys[k1 + 1][0]) < d:
		k1 += 1
	var a: Dictionary = keys[k1][1]
	var b: Dictionary = keys[mini(k1 + 1, keys.size() - 1)][1]
	var d0: float = keys[k1][0]
	var d1: float = keys[mini(k1 + 1, keys.size() - 1)][0]
	var f := 0.0 if d1 <= d0 else clampf((d - d0) / (d1 - d0), 0.0, 1.0)
	var pa := Vector3(a.pos[0], a.pos[1], a.pos[2])
	var pb := Vector3(b.pos[0], b.pos[1], b.pos[2])
	var qa := Quaternion(a.rot[0], a.rot[1], a.rot[2], a.rot[3]).normalized()
	var qb := Quaternion(b.rot[0], b.rot[1], b.rot[2], b.rot[3]).normalized()
	var sa := Vector3(a.scl[0], a.scl[1], a.scl[2])
	var sb := Vector3(b.scl[0], b.scl[1], b.scl[2])
	return Transform3D(Basis(qa.slerp(qb, f)) * Basis.from_scale(sa.lerp(sb, f)), pa.lerp(pb, f))

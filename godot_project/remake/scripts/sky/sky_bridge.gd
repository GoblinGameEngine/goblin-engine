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
var nose_y := 0.0              # the style's nose deck height (telescoping decks step down a little)
var reach := 13.0
var _base := Transform3D()     # where the island mounted it (match() raises or lowers it from there)
var _plate: Node3D             # the joint plate over the meeting noses (down only)
const PLATE_LEN := 1.2


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
	nose_y = float(st.get("nose_y", 0.0))
	reach = float(st.get("reach", 13.0))
	_base = transform
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
	# every part is solid (the user, 2026-10-14: "all part of the bridge need to be solid"): one body per moving node
	# (and one for the fixed housing), holding a trimesh of each of its own meshes -- not a body per mesh: an island
	# moves every tick, and every body on it moves with it
	var movers := {}
	for nk in _nodes:
		movers[nk[0]] = true
	var stack: Array = [[inst, inst]]                  # [node, the body-owner it belongs to]
	var shapes := {}                                   # owner -> [[shape, transform in owner]]
	while not stack.is_empty():
		var it: Array = stack.pop_back()
		var c: Node = it[0]
		var owner_: Node3D = it[1]
		if c != inst and movers.has(c):
			owner_ = c
		if c is MeshInstance3D and (c as MeshInstance3D).mesh:
			var rel := _rel_to(c as Node3D, owner_)
			shapes[owner_] = shapes.get(owner_, []) + [[(c as MeshInstance3D).mesh.create_trimesh_shape(), rel]]
		for ch in c.get_children():
			if ch is Node3D:
				stack.append([ch, owner_])
	for owner_ in shapes:
		var body := StaticBody3D.new()
		body.name = "solid"
		for sh in shapes[owner_]:
			var cs := CollisionShape3D.new()
			cs.shape = sh[0]
			cs.transform = sh[1]
			body.add_child(cs)
		(owner_ as Node3D).add_child(body)
	_make_plate(float(st.get("width", 3.6)))
	_pose()


static func _rel_to(n: Node3D, owner_: Node3D) -> Transform3D:
	## n's transform in owner_'s frame (owner_ an ancestor, or n itself)
	var t := Transform3D.IDENTITY
	var c: Node = n
	while c != owner_ and c != null:
		t = (c as Node3D).transform * t
		c = c.get_parent()
	return t


func _make_plate(w: float) -> void:
	## a steel plate laid over the two noses where they meet: one even surface across the joint
	_plate = StaticBody3D.new()
	_plate.name = "joint_plate"
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(w, 0.04, PLATE_LEN)
	cs.shape = box
	_plate.add_child(cs)
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = box.size
	mi.mesh = bm
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.32, 0.33, 0.35)
	m.metallic = 0.6
	m.roughness = 0.5
	mi.material_override = m
	_plate.add_child(mi)
	_plate.position = Vector3(0.0, nose_y + 0.02, reach)
	add_child(_plate)


func match(partner_nose_y: float) -> void:
	## two styles whose noses sit at different heights: each takes up half the difference at its mount, so they meet
	var mid := (nose_y + partner_nose_y) * 0.5
	transform = _base.translated_local(Vector3(0.0, mid - nose_y, 0.0))


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
	if _plate:
		_plate.visible = down
		_plate.collision_layer = 1 if down else 0


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

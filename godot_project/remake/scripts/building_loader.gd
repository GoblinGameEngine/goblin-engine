extends Node3D
class_name RemakeBuilding

## Instances one remake building .glb and wires up what the Blender side encoded in node
## names (see remake/blender/gblib.py header):
##   door_*    -> hinged RemakeDoor bodies with box collision that swings with the leaf
##   light_*   -> OmniLight3D
## "-col"/"-colonly" collision is handled by Godot's own glTF import hints.

@export var scene: PackedScene
@export var light_energy := 1.2

var doors: Array[RemakeDoor] = []


func _ready() -> void:
	if scene:
		load_building(scene)


## Shared material library: the glbs carry no images, each surface's material is named by the hash
## of its definition (<building>.mats.json, written by gblib) and built here once for every building.
static var _mat_cache := {}
const TEX_ROOT := "res://remake/textures/"


func load_building(ps: PackedScene) -> void:
	var kit_defs := merge_kit(ps)    # (the streamer has done it on a worker: then only the defs)
	var inst := ps.instantiate()
	add_child(inst)
	_apply_materials(inst, ps.resource_path.get_basename() + ".mats.json", kit_defs)
	var door_nodes: Array[Node3D] = []
	var light_nodes: Array[Node3D] = []
	var ladder_nodes: Array[Node3D] = []
	_collect(inst, door_nodes, light_nodes, ladder_nodes)
	for n in ladder_nodes:
		_make_ladder(n)
	for n in door_nodes:
		_make_door(n)
	for l in light_nodes:
		if l.name.begins_with("light_locked_"):
			continue            # a closed-up room (vacant store): no power
		var lamp := OmniLight3D.new()
		lamp.omni_range = 7.0
		lamp.light_energy = light_energy
		lamp.light_color = Color(1.0, 0.9, 0.75)
		lamp.shadow_enabled = false
		l.add_child(lamp)
	# pair up the leaves of double doors (same id before the _L/_R suffix)
	var by_id := {}
	for d in doors:
		var base := d.door_id.trim_suffix("_L").trim_suffix("_R")
		by_id[base] = by_id.get(base, []) + [d]
	for base in by_id:
		var leaves: Array = by_id[base]
		for d in leaves:
			for other in leaves:
				if other != d:
					d.partners.append(other)


func _collect(n: Node, door_nodes: Array[Node3D], light_nodes: Array[Node3D], ladder_nodes: Array[Node3D]) -> void:
	for c in n.get_children():
		if c is Node3D and String(c.name).begins_with("door_"):
			door_nodes.append(c)
			continue
		if c is Node3D and String(c.name).begins_with("light_"):
			light_nodes.append(c)
		if c is MeshInstance3D and String(c.name).begins_with("ladder_"):
			ladder_nodes.append(c)
		_collect(c, door_nodes, light_nodes, ladder_nodes)


## ladder_* meshes become climb zones: an Area3D slightly larger than the ladder that tells
## any body with set_ladder() when it is on it (the player then climbs instead of falling).
func _make_ladder(n: Node3D) -> void:
	var mi := n as MeshInstance3D
	var aabb := mi.get_aabb()
	var area := Area3D.new()
	area.name = "LadderZone"
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = aabb.size + Vector3(0.7, 0.4, 0.7)
	cs.shape = box
	cs.position = aabb.get_center()
	area.add_child(cs)
	area.add_to_group("ladder")
	n.add_child(area)
	area.body_entered.connect(func(b): if b.has_method("set_ladder"): b.set_ladder(1, cs))
	area.body_exited.connect(func(b): if b.has_method("set_ladder"): b.set_ladder(-1, cs))


func _make_door(n: Node3D) -> void:
	var parts := String(n.name).split("__")
	var id := parts[0].trim_prefix("door_")
	var sign := -1.0 if parts.size() > 1 and parts[1] == "n" else 1.0
	var is_locked := parts.has("locked")
	var body := RemakeDoor.new()
	body.name = "DoorBody_" + id
	# transform must be set before entering the tree and physics sync left off: with
	# sync_to_physics on, the body snaps back to wherever the physics server first saw it
	body.sync_to_physics = false
	body.transform = n.transform
	var parent := n.get_parent()
	parent.add_child(body)
	parent.remove_child(n)
	body.add_child(n)
	n.transform = Transform3D.IDENTITY
	# collision box = the leaf mesh's local AABB
	var mi := n as MeshInstance3D
	if mi == null:
		for c in n.get_children():
			if c is MeshInstance3D:
				mi = c
				break
	if mi:
		var aabb := mi.get_aabb()
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = aabb.size
		cs.shape = box
		cs.position = aabb.get_center()
		body.add_child(cs)
	body.setup(id, sign, is_locked)
	doors.append(body)


## Interior doors are seen only up close (through a window, or inside): past INNER_DOOR_M they aren't drawn and they
## never cast a shadow.  Calder's busy street had 104 door leaves in view, 90 of them inside buildings (~200 draws,
## 2026-10-13).  A leaf within 1 m of the building's outer bounds is a facade's and keeps the building's range.
## (After RemakeLodClusters._ranges, which sets every range of the building.)
const INNER_DOOR_M := 18.0


func cull_inner_doors() -> void:
	var vis: MeshInstance3D = null
	for mi in find_children("*_visual", "MeshInstance3D", true, false):
		vis = mi
	if vis == null:
		return
	var bx := vis.get_aabb()
	var inv := vis.global_transform.affine_inverse()
	for d in doors:
		var lp := inv * d.global_position
		var edge := minf(minf(lp.x - bx.position.x, bx.end.x - lp.x), minf(lp.z - bx.position.z, bx.end.z - lp.z))
		if edge < 1.0:
			continue
		for mi in d.find_children("*", "GeometryInstance3D", true, false):
			var g := mi as GeometryInstance3D
			g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			g.visibility_range_end = minf(g.visibility_range_end, INNER_DOOR_M) if g.visibility_range_end > 0.0 else INNER_DOOR_M
			g.visibility_range_end_margin = 0.0


## A distance version (<id>.lodN.glb from gblod): its textured surfaces use the building's own
## sidecar, everything else the shared vertex-colour material (one material for every LOD2/3 mesh,
## so a district's worth of them can be merged into a single draw call).
static var _defs_cache := {}


static func prepare_lod(inst: Node, glb_path: String) -> void:
	var sidecar := glb_path.get_basename().get_basename() + ".mats.json"
	if not _defs_cache.has(sidecar):                    # one read per building, not per LOD
		_defs_cache[sidecar] = JSON.parse_string(DataFile.text(sidecar)) if DataFile.exists(sidecar) else {}
	var defs: Dictionary = _defs_cache[sidecar]
	_apply_defs(inst, defs)
	# these ARE the level-of-detail chain: keep Godot's import-time automatic LOD from decimating
	# them further (it strips exactly the thin truss outlines and small panes they keep on purpose)
	var stack: Array[Node] = [inst]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		if n is GeometryInstance3D:
			(n as GeometryInstance3D).lod_bias = 1000.0


static var _lod_vc: StandardMaterial3D = null


static func lod_vc_material() -> StandardMaterial3D:
	if _lod_vc == null:
		_lod_vc = StandardMaterial3D.new()
		_lod_vc.resource_name = "LOD_VC"
		_lod_vc.vertex_color_use_as_albedo = true
		_lod_vc.vertex_color_is_srgb = false
		_lod_vc.roughness = 0.9
	return _lod_vc


## Shared parts (research/buildings/kit_design.md, remake/blender/gbkit.py): a building's repeated items (windows,
## doors, furniture ...) are not in its glb.  <ID>.kit.json lists them as [piece, x, y, z, yaw] in the building's
## Blender frame, or [piece, node name] for a door leaf; each piece is one mesh in remake/buildings/kit/.  They are
## folded back into the building's visual mesh, one surface per material as before, so the kit saves disk but no draw
## calls (a MultiMesh per piece cost Calder 17-21% more draws and 10-14% fps); a leaf's placeholder mesh becomes its
## piece, and the pieces' collision (<pid>-colonly) joins the building's own trimesh.  Once per model: the merged
## meshes and shape are the model's shared resources, marked with meta "kit".
const KIT_ROOT := "res://remake/buildings/kit/"
static var _kit_lock := Mutex.new()       # (held while a model merges -- on a worker; the main thread asks _merged)
static var _merged := {}                  # PackedScene instance id -> its kit defs: merged already
static var _merged_mx := Mutex.new()      # (guards _merged only, never held across engine calls)
static var _kit_raw := {}            # piece -> [Mesh, its material defs, its collision faces]


## Folds <ID>.kit.json's pieces into the model's visual mesh (safe on a worker thread).  Returns the kit's material
## defs (to apply with the building's own).
static func merge_kit(ps: PackedScene) -> Dictionary:
	var pkey := ps.get_instance_id()         # (a reloaded scene is a new instance: merged afresh)
	_merged_mx.lock()
	var done = _merged.get(pkey)
	_merged_mx.unlock()
	if done != null:
		return done
	var kit_path := ps.resource_path.get_basename() + ".kit.json"
	if not DataFile.exists(kit_path):
		return {}
	_kit_lock.lock()
	var n := ps.instantiate()
	var vis: MeshInstance3D = null
	var leaf := {}                   # door leaf node name -> its placeholder mesh
	var col: ConcavePolygonShape3D = null      # the building's collision (<ID>_collision-colonly)
	var col_inv := Transform3D.IDENTITY
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is MeshInstance3D and String(c.name).ends_with("_visual"):
			vis = c
		elif c is CollisionShape3D and (c as CollisionShape3D).shape is ConcavePolygonShape3D and col == null \
				and String(c.get_parent().name).contains("_collision"):
			col = (c as CollisionShape3D).shape
			col_inv = _frame_in(c, n).affine_inverse()
		elif c is MeshInstance3D and String(c.name).begins_with("door_") and (c as MeshInstance3D).mesh is ArrayMesh:
			leaf[String(c.name)] = (c as MeshInstance3D).mesh
	var m: ArrayMesh = vis.mesh as ArrayMesh if vis else null
	var frame_inv := vis.transform.affine_inverse() if vis else Transform3D.IDENTITY
	n.free()
	if m == null or m.has_meta("kit"):
		_kit_lock.unlock()
		var d: Dictionary = m.get_meta("kit", {}) if m else {}
		_merged_mx.lock()
		_merged[pkey] = d
		_merged_mx.unlock()
		return d
	var rows = JSON.parse_string(DataFile.text(kit_path))
	var defs := {}
	var adds := {}                   # material name -> [[mesh, surface, transform], ...]
	var col_add := PackedVector3Array()        # the pieces' collision faces, in the building's collision frame
	var mats := {}                   # material name -> the piece's material (for one the building doesn't have)
	for r in (rows if rows is Array else []):
		if str(r[0]) == "T":         # lettering: ["T", text, font, material, 3x4 matrix taking a 1 m em to the sign]
			var tmesh := _text_mesh(String(r[2]), String(r[1]))
			if tmesh == null:
				continue
			var mm: Array = r[4]
			var tx := Transform3D(Basis(Vector3(mm[0], mm[4], mm[8]), Vector3(mm[1], mm[5], mm[9]), Vector3(mm[2], mm[6], mm[10])),
				Vector3(mm[3], mm[7], mm[11]))
			var tkey := String(r[3])
			if not adds.has(tkey):
				adds[tkey] = []
				var named := StandardMaterial3D.new()
				named.resource_name = tkey               # (_apply_defs dresses it from the building's sidecar)
				mats[tkey] = named
			adds[tkey].append([tmesh, 0, frame_inv * tx])
			continue
		var k = _kit_piece(String(r[0]))
		if k == null:
			continue
		defs.merge(k[1])
		if r.size() == 2:            # a door leaf, placed by name: its placeholder becomes the piece
			var lm: ArrayMesh = leaf.get(String(r[1]))
			if lm != null:
				lm.clear_surfaces()
				lm.shadow_mesh = null
				for si in (k[0] as Mesh).get_surface_count():
					var lst := SurfaceTool.new()
					lst.create_from(k[0], si)
					lst.commit(lm)
					lm.surface_set_material(lm.get_surface_count() - 1, (k[0] as Mesh).surface_get_material(si))
			continue
		# Blender (x, y, z) is the glb's (x, z, -y); a turn about Blender's z is the same turn about Godot's y
		var at := Transform3D(Basis(Vector3.UP, deg_to_rad(float(r[4]))), Vector3(float(r[1]), float(r[3]), -float(r[2])))
		var xf := frame_inv * at
		if not (k[2] as PackedVector3Array).is_empty():
			col_add.append_array((col_inv * at) * (k[2] as PackedVector3Array))
		var km: Mesh = k[0]
		for si in km.get_surface_count():
			var mat := km.surface_get_material(si)
			var key := mat.resource_name if mat else ""
			if not adds.has(key):
				adds[key] = []
				mats[key] = mat
			adds[key].append([km, si, xf])
	var surfs := []                  # [SurfaceTool, material]
	for si in m.get_surface_count():
		var mat := m.surface_get_material(si)
		var key := mat.resource_name if mat else ""
		var st := SurfaceTool.new()
		st.create_from(m, si)
		for a in adds.get(key, []):
			st.append_from(a[0], a[1], a[2])
		adds.erase(key)
		surfs.append([st, mat])
	for key in adds:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for a in adds[key]:
			st.append_from(a[0], a[1], a[2])
		surfs.append([st, mats[key]])
	surfs = _plain_merged(surfs, ps.resource_path.get_basename() + ".mats.json", defs)
	m.clear_surfaces()
	m.shadow_mesh = null             # (the import's shadow copy has the old surfaces: the renderer indexes it in step)
	for sm in surfs:
		(sm[0] as SurfaceTool).commit(m)
		m.surface_set_material(m.get_surface_count() - 1, sm[1])
	if not col_add.is_empty():
		if col != null:
			var faces := col.get_faces()
			faces.append_array(col_add)
			col.set_faces(faces)
		else:
			push_warning("merge_kit: %s has piece collision but no collision shape of its own" % kit_path)
	m.set_meta("kit", defs)
	_kit_lock.unlock()
	_merged_mx.lock()
	_merged[pkey] = defs
	_merged_mx.unlock()
	return defs


static func _kit_piece(pid: String):
	if not _kit_raw.has(pid):
		var mesh: Mesh = null
		var faces := PackedVector3Array()          # its collision (<pid>-colonly), in the piece's frame
		var ps := load(KIT_ROOT + pid + ".glb") as PackedScene
		if ps:
			var n := ps.instantiate()
			var stack: Array[Node] = [n]
			while stack.size() > 0:
				var c: Node = stack.pop_back()
				stack.append_array(c.get_children())
				if c is MeshInstance3D and (c as MeshInstance3D).mesh and mesh == null:
					mesh = (c as MeshInstance3D).mesh
				elif c is CollisionShape3D and (c as CollisionShape3D).shape is ConcavePolygonShape3D:
					faces.append_array(_frame_in(c, n) * ((c as CollisionShape3D).shape as ConcavePolygonShape3D).get_faces())
			n.free()
		var defs = JSON.parse_string(DataFile.text(KIT_ROOT + pid + ".mats.json")) \
			if DataFile.exists(KIT_ROOT + pid + ".mats.json") else {}
		_kit_raw[pid] = [mesh, defs if defs is Dictionary else {}, faces] if mesh else null
	return _kit_raw[pid]


## Plain colours, one draw: a building's untextured, opaque, unlit surfaces (34 surfaces a building in Calder, 19 of
## them plain) become one vertex-coloured surface per (roughness, metal) group -- each surface was a draw call, and
## another per shadow cascade.  The colours go in as vertex colours (sRGB, as albedo_color has them).
static var _plain_mat := {}


static func _plain_merged(surfs: Array, sidecar: String, kit_defs: Dictionary) -> Array:
	var all_defs = DataFile.json(sidecar)
	if not all_defs is Dictionary:
		return surfs
	all_defs.merge(kit_defs)
	var keep := []
	var groups := {}                 # "rough|metal" -> SurfaceTool
	for sm in surfs:
		var mat: Material = sm[1]
		var d = all_defs.get(mat.resource_name if mat else "")
		if not (d is Dictionary) or d.get("tex") or d.get("alpha") != null or d.get("emission"):
			keep.append(sm)
			continue
		var arrays: Array = (sm[0] as SurfaceTool).commit_to_arrays()
		var n: int = (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
		if n == 0:
			continue
		var c = d.get("color", [0.8, 0.8, 0.8])
		var cols := PackedColorArray()
		cols.resize(n)
		cols.fill(Color(c[0], c[1], c[2]).linear_to_srgb())
		arrays[Mesh.ARRAY_COLOR] = cols
		var one := ArrayMesh.new()
		one.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var gk := "%.1f|%d" % [snappedf(float(d.get("rough", 0.6)), 0.2), 1 if float(d.get("metal", 0.0)) > 0.5 else 0]
		if not groups.has(gk):
			var gst := SurfaceTool.new()
			gst.begin(Mesh.PRIMITIVE_TRIANGLES)
			groups[gk] = gst
		(groups[gk] as SurfaceTool).append_from(one, 0, Transform3D.IDENTITY)
	for gk in groups:
		if not _plain_mat.has(gk):
			var pm := StandardMaterial3D.new()
			pm.resource_name = "PLAIN_" + gk              # (no def by that name: _apply_defs leaves it as it is)
			pm.vertex_color_use_as_albedo = true
			pm.vertex_color_is_srgb = true
			var parts: PackedStringArray = gk.split("|")
			pm.roughness = float(parts[0])
			pm.metallic = float(parts[1])
			_plain_mat[gk] = pm
		keep.append([groups[gk], _plain_mat[gk]])
	return keep


const FONTS := "res://remake/fonts/"
static var _texts := {}              # font|text -> TextMesh (an em of 1 m, centred as Blender centres it)


static func _text_mesh(font_name: String, text: String) -> Mesh:
	var key := font_name + "|" + text
	if not _texts.has(key):
		if _texts.size() > 4000:
			_texts.clear()
		var font := load(FONTS + font_name + ".ttf") as Font
		if font == null:
			_texts[key] = null
		else:
			var tm := TextMesh.new()
			tm.font = font
			tm.text = text
			tm.font_size = 64
			tm.pixel_size = 1.0 / 64.0
			tm.depth = 0.0                   # (flat, one-sided: the front faces +z, as the sign's reader)
			tm.curve_step = 4.0              # (about Blender's resolution_u 4)
			tm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			tm.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			_texts[key] = tm
	return _texts[key]


static func _frame_in(c: Node, root: Node) -> Transform3D:
	## c's transform in root's frame (nodes outside the tree: no global_transform)
	var t := Transform3D.IDENTITY
	while c != null and c != root:
		if c is Node3D:
			t = (c as Node3D).transform * t
		c = c.get_parent()
	return t


func _apply_materials(inst: Node, sidecar: String, extra := {}) -> void:
	if not DataFile.exists(sidecar):
		return
	var defs = JSON.parse_string(DataFile.text(sidecar))
	if defs is Dictionary:
		defs.merge(extra)
		_apply_defs(inst, defs)


## Lit windows at night (the user, 2026-10-05: "make the nights darker and the lights on buildings and cars more
## pronounced"): about LIT_SHARE of buildings get warm glowing glass, chosen by the building's name (the same
## windows every load); DaySkySystem drives the glow with set_night().
const LIT_SHARE := 60
const WINDOW_GLOW := Color(1.0, 0.76, 0.42)
static var night_glass: Array[StandardMaterial3D] = []
static var night_level := 0.0


static func set_night(n: float) -> void:
	night_level = n
	for m in night_glass:
		m.emission_energy_multiplier = n * 2.4
		m.albedo_color.a = lerpf(float(m.get_meta("alpha")), 0.92, n)


static func _is_glass(d: Dictionary) -> bool:
	var a = d.get("alpha")
	return a != null and float(a) < 0.6


static func lit_glass(key: String, d: Dictionary) -> StandardMaterial3D:
	var k := key + "#lit"
	if _mat_cache.has(k):
		return _mat_cache[k]
	var m := library_material(key, d).duplicate() as StandardMaterial3D
	m.resource_name = k
	m.emission_enabled = true
	m.emission = WINDOW_GLOW
	m.set_meta("alpha", m.albedo_color.a)
	m.emission_energy_multiplier = night_level * 2.4
	m.albedo_color.a = lerpf(m.albedo_color.a, 0.92, night_level)
	night_glass.append(m)
	_mat_cache[k] = m
	return m


static func _apply_defs(inst: Node, defs: Dictionary) -> void:
	var lit := posmod(hash(str(inst.name)), 100) < LIT_SHARE
	var stack: Array[Node] = [inst]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		var mi := n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(i)
			if m and m.resource_name == "LOD_VC":
				mi.set_surface_override_material(i, lod_vc_material())
			elif m and defs.has(m.resource_name):
				var d: Dictionary = defs[m.resource_name]
				mi.set_surface_override_material(i, lit_glass(m.resource_name, d) if lit and _is_glass(d)
					else library_material(m.resource_name, d))


static func library_material(key: String, d: Dictionary) -> StandardMaterial3D:
	if _mat_cache.has(key):
		return _mat_cache[key]
	var m := StandardMaterial3D.new()
	m.resource_name = key
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	m.roughness = d.get("rough", 0.6)
	m.metallic = d.get("metal", 0.0)
	var tex = d.get("tex")
	if tex:
		var base: String = TEX_ROOT + tex
		m.albedo_texture = load(base + "_albedo.webp")
		var tint = d.get("tint")
		m.albedo_color = Color(tint[0], tint[1], tint[2]) if tint else Color.WHITE   # tints are stored sRGB
		if ResourceLoader.exists(base + "_rough.webp"):
			m.roughness_texture = load(base + "_rough.webp")
			m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
			m.roughness = 1.0
		if ResourceLoader.exists(base + "_normal.webp"):
			m.normal_enabled = true
			m.normal_texture = load(base + "_normal.webp")
	else:
		var c = d.get("color", [0.8, 0.8, 0.8])
		# Blender colours are linear; albedo_color is sRGB
		m.albedo_color = Color(c[0], c[1], c[2]).linear_to_srgb()
	var a = d.get("alpha")
	if a != null:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.albedo_color.a = a
	var e = d.get("emission")
	if e:
		m.emission_enabled = true
		m.emission = Color(e[0], e[1], e[2])
		m.emission_energy_multiplier = 2.0
	_mat_cache[key] = m
	return m

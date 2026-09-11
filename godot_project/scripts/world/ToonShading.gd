extends Node
class_name ToonShading

# Applies cel shading (banded lighting + a black outline, see
# shaders/toon.gdshader and shaders/toon_outline.gdshader) to 3D world
# geometry -- houses, terrain, streets, scenery, doors/windows, vehicles.
# Deliberately NOT applied to NPCs (already sprite-based, Sprite3D, never
# touched by this since it only walks MeshInstance3D/MultiMeshInstance3D),
# the player (weapon view models -- slated to become a sprite too, kept
# as plain PBR for now on purpose), or any UI. Call apply_to_world() once
# per subtree that should get the look -- Main.gd calls it on the
# `neighborhood` node (everything imported from neighborhood.glb: houses,
# streets, scenery, curbs, fences, plus the doors/windows OpeningsSetup.gd
# parents there at runtime) and again on each spawned vehicle instance.

const TOON_SHADER := preload("res://shaders/toon.gdshader")
const OUTLINE_SHADER := preload("res://shaders/toon_outline.gdshader")

## Ground-level civic infrastructure never gets the outline pass (still
## gets normal banded toon shading, just no next_pass) -- REAL BUG found
## live: a black line was showing up out in the middle of the road, well
## clear of the actual curb. Root cause: the outline is an inverted-hull
## effect done PER MESH OBJECT, and the road/curb/sidewalk network is
## built as several separate flat segments placed edge-to-edge (cut at
## every cross-street, see build_neighborhood.py's _segments_excluding())
## -- each segment is its own watertight box with its OWN silhouette, so
## the outline pass dutifully drew a border around every one of those
## internal seams too, not just the network's true outer edges. Rather
## than try to weld every segment into one seamless mesh, simplest and
## arguably more correct for the style: a flat ground plane doesn't
## really want a cel outline at all (compare Wind Waker's terrain/ocean,
## which isn't outlined, vs. its props and characters, which are).
const NO_OUTLINE_KEYWORDS := ["road", "curb", "sidewalk", "driveway", "street"]

static func _wants_outline(node_name: String) -> bool:
	var lower := node_name.to_lower()
	for kw in NO_OUTLINE_KEYWORDS:
		if lower.find(kw) != -1:
			return false
	return true

## One shared outline material per DISTINCT texture (keyed by resource
## path) rather than truly one-per-surface -- the outline pass now has to
## sample the same texture as the main pass (see toon_outline.gdshader's
## own comment on why: it has to discard the same cutout texels the main
## pass does, or a fence/railing/window gets a solid black silhouette
## instead of an outline around its actual visible bars), but most
## surfaces sharing a texture can still share one outline instance --
## only the (rare) untextured solid-color materials fall back to one
## further-shared "no texture" instance.
static var _outline_mat_cache: Dictionary = {}  # texture path (or "") -> ShaderMaterial

static func _outline_material_for(tex: Texture2D) -> ShaderMaterial:
	var key: String = tex.resource_path if tex else ""
	if not _outline_mat_cache.has(key):
		var m := ShaderMaterial.new()
		m.shader = OUTLINE_SHADER
		m.set_shader_parameter("use_texture", tex != null)
		if tex:
			m.set_shader_parameter("albedo_texture", tex)
		_outline_mat_cache[key] = m
	return _outline_mat_cache[key]

## Builds the toon-shaded replacement for one existing material, carrying
## over just what the toon shader actually uses (the albedo texture and
## tint) -- everything else about the original PBR material (roughness,
## metallic, normal maps) is deliberately dropped, since a banded toon
## surface doesn't use any of it.
static func _toon_material_for(src: Material, want_outline: bool = true) -> ShaderMaterial:
	var mat := ShaderMaterial.new()
	mat.shader = TOON_SHADER
	var tex: Texture2D = null
	var color := Color(1, 1, 1, 1)
	if src is BaseMaterial3D:
		tex = (src as BaseMaterial3D).albedo_texture
		color = (src as BaseMaterial3D).albedo_color
	mat.set_shader_parameter("use_texture", tex != null)
	if tex:
		mat.set_shader_parameter("albedo_texture", tex)
	mat.set_shader_parameter("albedo_color", color)
	if want_outline:
		mat.next_pass = _outline_material_for(tex)
	return mat

## Recursively walks `root`, replacing every MeshInstance3D surface
## material and every MultiMeshInstance3D's material with a toon-shaded
## equivalent. Returns how many materials were converted (for a one-line
## log, same convention as OpeningsSetup.setup()'s own return dict).
static func apply_to_world(root: Node) -> int:
	var count := 0
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			var outline := _wants_outline(mi.name)
			if mi.mesh:
				for i in range(mi.mesh.get_surface_count()):
					var src_mat := mi.get_active_material(i)
					mi.set_surface_override_material(i, _toon_material_for(src_mat, outline))
					count += 1
		elif n is MultiMeshInstance3D:
			var mm := n as MultiMeshInstance3D
			var src_mat: Material = mm.material_override
			if src_mat == null and mm.multimesh and mm.multimesh.mesh and mm.multimesh.mesh.get_surface_count() > 0:
				src_mat = mm.multimesh.mesh.surface_get_material(0)
			mm.material_override = _toon_material_for(src_mat, _wants_outline(mm.name))
			count += 1
		for c in n.get_children():
			stack.append(c)
	return count

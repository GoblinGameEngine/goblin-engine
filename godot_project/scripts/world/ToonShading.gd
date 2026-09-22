extends Node
class_name ToonShading

# Applies cel shading (banded lighting only -- see shaders/toon.gdshader)
# to 3D world geometry -- houses, terrain, streets, scenery, doors/
# windows, vehicles. Deliberately NOT applied to NPCs (already sprite-
# based, Sprite3D, never touched by this since it only walks
# MeshInstance3D/MultiMeshInstance3D), the player (weapon view models --
# slated to become a sprite too, kept as plain PBR for now on purpose),
# or any UI. Call apply_to_world() once per subtree that should get the
# look -- Main.gd calls it on the `neighborhood` node (everything
# imported from neighborhood.glb: houses, streets, scenery, curbs,
# fences, plus the doors/windows OpeningsSetup.gd parents there at
# runtime) and again on each spawned vehicle instance.
#
# The black OUTLINE used to be this script's job too (a per-object
# inverted-hull next_pass, shaders/toon_outline.gdshader) -- retired
# entirely. That technique offsets a mesh's own vertices outward by a
# flat WORLD-SPACE distance, which turned out to have three real failure
# modes chased down live, one at a time, across two sessions: false
# seams between adjacent flat segments (roads cut at cross-streets),
# disproportionate width on thin rods (sign posts), and a complete
# breakdown on flat QuadMesh sprites (windows/doors -- every vertex
# shares one normal, so the "outward offset" just slides the whole plane
# forward as a solid black slab instead of outlining it). Even with all
# three fixed, a FOURTH problem remained that no per-object tuning could
# fix: a fixed world-space offset is a bigger fraction of the screen the
# closer the camera gets, full stop -- "looks fine far away, breaks up
# close" is that technique's own math, not a bug to isolate. Replaced
# with a screen-space depth/normal edge-detection pass (see
# shaders/screen_outline.gdshader, ScreenOutline.gd) that draws outline
# width in screen PIXELS instead of world meters, which is distance-
# correct by construction and needs none of the per-object shape
# detection this file used to carry. See reference/memory.txt for the
# full history if any of this needs revisiting.

const TOON_SHADER := preload("res://shaders/toon.gdshader")

# Node-name prefixes that get the shader's fixed-Y billboard vertex()
# override (see toon.gdshader's own comment) -- CropFieldGenerator.gd's
# corn_*/soy_* stalks, matched the same way SceneryOptimizer.
# DECOR_PREFIXES matches decor for batching (a MultiMeshInstance3D
# produced from them keeps the "<first stalk name>_multimesh" name, so
# begins_with still matches after batching).
const BILLBOARD_PREFIXES := ["corn_", "soy_"]

static func _wants_billboard(node_name: String) -> bool:
	for prefix in BILLBOARD_PREFIXES:
		if node_name.begins_with(prefix):
			return true
	return false

## REAL BUG found live, root-caused only after a long screen-space-
## outline investigation kept measuring a completely wrong depth-buffer
## value for tree canopies specifically (a tree 11m from the camera
## reading back as 147m -- ~13x too far -- while ordinary geometry read
## correctly at every distance tested all session): decorative scenery's
## own textures (neighborhood_conifer_3.png, the leaf/bush noise
## textures, etc.) are plain RGB with NO ALPHA CHANNEL AT ALL, yet
## toon.gdshader's fragment() unconditionally tested `base.a < 0.5` and
## discarded on it. Sampling an alpha-less texture reliably returns 1.0
## in the ordinary forward color pass (matching what's actually visible
## on screen -- these objects render fine), but evidently NOT
## consistently in whatever separate pass populates the depth/normal
## buffers hint_depth_texture/hint_normal_roughness_texture read -- this
## project didn't chase that discrepancy into Godot's own internals, but
## the fix doesn't need to: a texture with no real alpha data should
## never have been a discard candidate in the first place, regardless of
## mechanism. Detected here via Image.detect_alpha() (real cutout
## textures -- fences, railings, window panes, door glass, all the
## chroma-key-to-alpha textures this project actually generates with
## real transparency -- correctly keep discarding; plain opaque
## decorative noise textures like this one now never do).
static func _texture_has_real_alpha(tex: Texture2D) -> bool:
	if tex == null:
		return false
	var img := tex.get_image()
	if img == null:
		return false
	return img.detect_alpha() != Image.ALPHA_NONE

## Builds the toon-shaded replacement for one existing material, carrying
## over just what the toon shader actually uses (the albedo texture and
## tint) -- everything else about the original PBR material (roughness,
## metallic, normal maps) is deliberately dropped, since a banded toon
## surface doesn't use any of it.
static func _toon_material_for(src: Material, billboard_y: bool = false) -> ShaderMaterial:
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
	mat.set_shader_parameter("has_alpha", _texture_has_real_alpha(tex))
	mat.set_shader_parameter("billboard_y", billboard_y)
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
			var billboard := _wants_billboard(n.name)
			if mi.mesh:
				for i in range(mi.mesh.get_surface_count()):
					var src_mat := mi.get_active_material(i)
					mi.set_surface_override_material(i, _toon_material_for(src_mat, billboard))
					count += 1
		elif n is MultiMeshInstance3D:
			var mm := n as MultiMeshInstance3D
			var src_mat: Material = mm.material_override
			if src_mat == null and mm.multimesh and mm.multimesh.mesh and mm.multimesh.mesh.get_surface_count() > 0:
				src_mat = mm.multimesh.mesh.surface_get_material(0)
			mm.material_override = _toon_material_for(src_mat, _wants_billboard(n.name))
			count += 1
		for c in n.get_children():
			stack.append(c)
	return count

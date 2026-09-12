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

## REAL BUG found live: a sign post's outline read as a fat black tube
## wrapped loosely around a much thinner pole, not a thin line hugging
## it. The inverted-hull technique (toon_outline.gdshader) offsets EVERY
## vertex outward along its own normal by a flat, WORLD-SPACE distance --
## fine when that distance is a small fraction of what's on screen (a
## wall, a roof, a sign board), but a sign post is only ~0.09m across, so
## the same flat 0.07m offset very nearly doubles its visible diameter.
##
## Detected geometrically rather than by keyword (so it self-applies to
## every thin cylindrical object -- posts, handrails, lamp poles -- not
## just the one this was noticed on): sort an object's local AABB extents
## ascending. A flat plate (a wall, a sign board, a roof panel) has ONE
## small dimension (its thickness) and two large ones. A rod (a post, a
## handrail) has TWO small dimensions (its cross-section) and one long
## one. Only the rod case gets its outline scaled down, capped to a
## fraction of its own cross-section so it can never balloon past the
## object's actual silhouette again, however thin that object gets.
const OUTLINE_BASE_WIDTH := 0.07
const ROD_RATIO_THRESHOLD := 3.0
const ROD_OUTLINE_FRACTION := 0.4
const ROD_OUTLINE_MIN := 0.006

static func _outline_width_for_aabb(aabb: AABB) -> float:
	var extents := [aabb.size.x, aabb.size.y, aabb.size.z]
	extents.sort()
	var e0: float = extents[0]
	var e1: float = extents[1]
	if e0 > 0.001 and e1 <= e0 * ROD_RATIO_THRESHOLD:
		return clamp(e0 * ROD_OUTLINE_FRACTION, ROD_OUTLINE_MIN, OUTLINE_BASE_WIDTH)
	return OUTLINE_BASE_WIDTH

## REAL BUG found live (reported as "corners disappear" and "outline
## beyond the edges" while standing INSIDE a house near a window): a
## window's mullions and a door's panel lines aren't 3D geometry at all
## -- Window.tscn/Door.tscn are each a single flat QuadMesh, painted with
## a texture, exactly like the sprites this whole engine is moving
## toward. The inverted-hull technique fundamentally cannot outline a
## flat plane: every vertex on a QuadMesh shares the SAME normal (there's
## no curvature/volume for normals to radiate outward from), so
## `VERTEX += NORMAL * outline_width` doesn't enlarge the plane's
## silhouette at all -- it just SLIDES THE WHOLE PLANE forward by
## outline_width as one rigid, undistorted copy. Depending on viewing
## angle that shows up as a solid black slab roughly the size of the
## whole window/door, offset from and overlapping the real one -- which
## reads exactly like "the outline doesn't follow the geometry" and
## swallows real corners/edges under it, because at close range it
## mostly does.
##
## The rod-vs-plate test above (_outline_width_for_aabb) doesn't catch
## this: it only SCALES the outline down for a thin object, but a true
## zero-thickness plane needs the outline pass skipped entirely, not
## thinned -- there is no valid inverted-hull outline for it at any
## width. Detected the same geometric way, one step further: a real
## plate (a wall, a roof panel, a sign board) still has some actual
## thickness; a QuadMesh's local AABB has exactly zero depth on its
## normal axis. Below FLAT_PLANE_MAX_DEPTH counts as that degenerate
## case.
const FLAT_PLANE_MAX_DEPTH := 0.005

static func _is_degenerate_plane(aabb: AABB) -> bool:
	var extents := [aabb.size.x, aabb.size.y, aabb.size.z]
	extents.sort()
	return extents[0] < FLAT_PLANE_MAX_DEPTH

## One shared outline material per DISTINCT (texture, outline width) pair
## rather than truly one-per-surface -- the outline pass now has to
## sample the same texture as the main pass (see toon_outline.gdshader's
## own comment on why: it has to discard the same cutout texels the main
## pass does, or a fence/railing/window gets a solid black silhouette
## instead of an outline around its actual visible bars), but most
## surfaces sharing a texture AND a width tier can still share one
## outline instance -- only the (rare) untextured solid-color materials
## fall back to one further-shared "no texture" instance per width.
static var _outline_mat_cache: Dictionary = {}  # "<texture path>|<width>" -> ShaderMaterial

static func _outline_material_for(tex: Texture2D, width: float = OUTLINE_BASE_WIDTH) -> ShaderMaterial:
	var key := "%s|%.4f" % [(tex.resource_path if tex else ""), width]
	if not _outline_mat_cache.has(key):
		var m := ShaderMaterial.new()
		m.shader = OUTLINE_SHADER
		m.set_shader_parameter("use_texture", tex != null)
		if tex:
			m.set_shader_parameter("albedo_texture", tex)
		m.set_shader_parameter("outline_width", width)
		_outline_mat_cache[key] = m
	return _outline_mat_cache[key]

## Builds the toon-shaded replacement for one existing material, carrying
## over just what the toon shader actually uses (the albedo texture and
## tint) -- everything else about the original PBR material (roughness,
## metallic, normal maps) is deliberately dropped, since a banded toon
## surface doesn't use any of it.
static func _toon_material_for(src: Material, want_outline: bool = true, outline_width: float = OUTLINE_BASE_WIDTH) -> ShaderMaterial:
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
		mat.next_pass = _outline_material_for(tex, outline_width)
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
			if mi.mesh:
				var aabb := mi.mesh.get_aabb()
				var outline := _wants_outline(mi.name) and not _is_degenerate_plane(aabb)
				var width := _outline_width_for_aabb(aabb)
				for i in range(mi.mesh.get_surface_count()):
					var src_mat := mi.get_active_material(i)
					mi.set_surface_override_material(i, _toon_material_for(src_mat, outline, width))
					count += 1
		elif n is MultiMeshInstance3D:
			var mm := n as MultiMeshInstance3D
			var src_mat: Material = mm.material_override
			if src_mat == null and mm.multimesh and mm.multimesh.mesh and mm.multimesh.mesh.get_surface_count() > 0:
				src_mat = mm.multimesh.mesh.surface_get_material(0)
			var width := OUTLINE_BASE_WIDTH
			var outline := _wants_outline(mm.name)
			if mm.multimesh and mm.multimesh.mesh:
				var aabb := mm.multimesh.mesh.get_aabb()
				width = _outline_width_for_aabb(aabb)
				outline = outline and not _is_degenerate_plane(aabb)
			mm.material_override = _toon_material_for(src_mat, outline, width)
			count += 1
		for c in n.get_children():
			stack.append(c)
	return count

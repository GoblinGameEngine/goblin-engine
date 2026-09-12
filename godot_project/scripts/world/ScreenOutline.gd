extends Node
class_name ScreenOutline

# Sets up the screen-space depth/normal outline pass (shaders/
# screen_outline.gdshader) -- see that shader's own comment for the full
# rationale on why this replaced the old per-object inverted-hull system.
# One full-screen quad, parented to whichever Camera3D is passed in, so
# it always covers the view regardless of where the camera moves; the
# shader's own vertex() hijacks POSITION into clip space directly, so
# the quad's actual size/transform past "in front of the camera" doesn't
# matter.

const OUTLINE_SHADER := preload("res://shaders/screen_outline.gdshader")

## Call once, after the camera that should get outlines exists (Main.gd,
## once Player is in the tree). Returns the MeshInstance3D in case a
## caller wants to tweak shader params later (e.g. a debug menu).
static func attach_to_camera(camera: Camera3D) -> MeshInstance3D:
	var quad := QuadMesh.new()
	quad.size = Vector2(2.0, 2.0)

	var mat := ShaderMaterial.new()
	mat.shader = OUTLINE_SHADER

	var mi := MeshInstance3D.new()
	mi.name = "ScreenOutline"
	mi.mesh = quad
	mi.material_override = mat
	# Not real 3D geometry to be culled/shadowed/navmeshed like anything
	# else in the scene -- it only ever exists to draw a full-screen
	# overlay in front of whatever camera it's parented to.
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.extra_cull_margin = 16384.0  # never let frustum culling drop it
	mi.transform.origin = Vector3(0, 0, -0.1)
	camera.add_child(mi)
	return mi

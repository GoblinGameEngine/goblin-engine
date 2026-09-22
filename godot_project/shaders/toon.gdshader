shader_type spatial;
// Cel-shading main pass -- 3D world geometry only (houses, terrain,
// streets, scenery, vehicles, doors/windows). Deliberately NOT applied to
// NPCs (sprite-based already), the player (weapon view -- slated to
// become a sprite too, see reference/memory.txt), or any UI -- see
// ToonShading.gd for exactly what this does and doesn't get attached to.
//
// Quantizes the direct-light diffuse term into 3 hard bands instead of a
// smooth falloff -- the classic cel-shaded look -- while leaving Godot's
// own ambient/GI contribution alone (added separately, after light()
// runs) so shadow-side surfaces still pick up a little environment fill
// instead of going pure black. Specular is fully disabled: a smooth
// specular highlight on top of flat-banded diffuse reads as a lighting
// bug, not a style, on flat siding/roof/floor textures like these.
// cull_disabled (not cull_back) -- some of what this gets applied to
// (Door.tscn/Window.tscn, a flat QuadMesh meant to be visible from both
// sides) relies on double-sided rendering already; NORMAL is flipped for
// back-facing fragments below instead so lighting still reads correctly
// from either side, matching what StandardMaterial3D's own cull_disabled
// does automatically (this is a raw shader, so that has to be explicit).
//
// REAL BUG, found live: this used to be `blend_mix` with ALPHA set from
// the texture's own alpha channel -- but every alpha-cutout texture in
// this project (porch railings, fences, window panes, door glass -- the
// chroma-key-to-alpha technique used everywhere, see reference/memory.txt)
// is meant to be a hard cutout (fully see-through or fully opaque, no
// in-between), not a soft blend. blend_mix blends toward whatever color
// sits in the "transparent" texels instead of actually showing what's
// behind them, and without correct back-to-front transparency sorting
// (which this bulk conversion has no way to set up per-object), those
// blended fragments were drawing solid black over already-opaque
// geometry behind them -- confirmed live as a repeating row of solid
// black rectangles exactly matching a porch railing's baluster gaps.
// Fixed by discarding fully-transparent texels outright instead of
// blending them -- renders as ordinary opaque geometry with holes
// punched in it, which is what a hard cutout actually is, and needs no
// transparency sorting at all.
render_mode cull_disabled, specular_disabled;

uniform sampler2D albedo_texture : source_color, filter_nearest, repeat_enable;
uniform vec4 albedo_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform bool use_texture = true;
// REAL BUG found live (see ToonShading.gd's own comment on
// _texture_has_real_alpha() for the full story): a plain RGB texture
// with no alpha channel at all was still being alpha-discard-tested
// below, and evidently sampled inconsistently between the ordinary
// color pass and whatever separate pass populates the depth/normal
// buffers a later screen-space effect reads -- discarding only makes
// sense for a texture that actually HAS real alpha data to discard on.
uniform bool has_alpha = true;

// Fixed-axis billboard for crop sprites (CropFieldGenerator.gd's corn_*/
// soy_* stalks) -- rotates the quad around its own local "up" axis to
// face the camera, WITHOUT tilting it to face up/down (a true spherical
// billboard would lay a standing stalk flat when viewed from above/
// below, which reads as broken rather than stylized). Deliberately uses
// each instance's own MODEL_MATRIX Y column as "up," not a hardcoded
// world Vector3(0,1,0): this project's station-ring floor is curved, so
// "up" varies by position (see RingCoords.gd) -- CropFieldGenerator.gd
// places each stalk with a real per-position ring basis specifically so
// this shader has the right axis to read back per instance, including
// under MultiMesh instancing (MODEL_MATRIX already carries each
// instance's own transform there, same as for a single MeshInstance3D).
uniform bool billboard_y = false;

// Band edges (in NdotL, 0..1) and the brightness multiplier for each band.
uniform float band_edge_1 : hint_range(0.0, 1.0) = 0.25;
uniform float band_edge_2 : hint_range(0.0, 1.0) = 0.6;
uniform float shade_dark : hint_range(0.0, 1.5) = 0.5;
uniform float shade_mid : hint_range(0.0, 1.5) = 0.78;
uniform float shade_lit : hint_range(0.0, 1.5) = 1.05;

void vertex() {
	if (billboard_y) {
		vec3 up = normalize(MODEL_MATRIX[1].xyz);
		vec3 world_pos = MODEL_MATRIX[3].xyz;
		vec3 cam_pos = INV_VIEW_MATRIX[3].xyz;
		vec3 to_cam = cam_pos - world_pos;
		to_cam -= up * dot(to_cam, up);  // project out the up component -- rotate only around "up"
		float to_cam_len = length(to_cam);
		vec3 fwd = to_cam_len > 0.0001 ? to_cam / to_cam_len : normalize(MODEL_MATRIX[2].xyz);
		vec3 right = normalize(cross(up, fwd));
		vec3 true_up = cross(fwd, right);

		vec3 scale = vec3(
			length(MODEL_MATRIX[0].xyz),
			length(MODEL_MATRIX[1].xyz),
			length(MODEL_MATRIX[2].xyz)
		);

		mat4 billboard_model = mat4(
			vec4(right * scale.x, 0.0),
			vec4(true_up * scale.y, 0.0),
			vec4(fwd * scale.z, 0.0),
			vec4(world_pos, 1.0)
		);
		MODELVIEW_MATRIX = VIEW_MATRIX * billboard_model;
	}
}

void fragment() {
	vec4 tex_color = use_texture ? texture(albedo_texture, UV) : vec4(1.0);
	vec4 base = tex_color * albedo_color;
	if (has_alpha && base.a < 0.5) {
		discard;
	}
	ALBEDO = base.rgb;
	NORMAL = FRONT_FACING ? NORMAL : -NORMAL;
}

void light() {
	float ndotl = dot(NORMAL, LIGHT);
	float band;
	if (ndotl > band_edge_2) {
		band = shade_lit;
	} else if (ndotl > band_edge_1) {
		band = shade_mid;
	} else {
		band = shade_dark;
	}
	DIFFUSE_LIGHT += ALBEDO * band * LIGHT_COLOR * ATTENUATION;
}

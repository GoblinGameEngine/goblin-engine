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

// Band edges (in NdotL, 0..1) and the brightness multiplier for each band.
uniform float band_edge_1 : hint_range(0.0, 1.0) = 0.25;
uniform float band_edge_2 : hint_range(0.0, 1.0) = 0.6;
uniform float shade_dark : hint_range(0.0, 1.5) = 0.5;
uniform float shade_mid : hint_range(0.0, 1.5) = 0.78;
uniform float shade_lit : hint_range(0.0, 1.5) = 1.05;

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

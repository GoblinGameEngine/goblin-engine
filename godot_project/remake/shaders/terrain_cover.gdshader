shader_type spatial;
// The ground: land cover coloured per pixel from remake/landcover.png (so field and shore edges stay
// sharp whatever the mesh density), MapTerrainMesh's vertex colour where it knows better (town areas,
// mud and river beds, steep earth: vertex alpha 1), and the neutral grass grain over it all.
// UV is (x, s) / TEX_M.  Colours are the same table as MapTerrainMesh._cover_tint (sRGB).

uniform sampler2D detail : source_color, filter_linear_mipmap, repeat_enable;
#include "res://remake/shaders/land_cover.gdshaderinc"
#include "res://remake/shaders/spindle_light.gdshaderinc"

uniform bool coarse = false;          // a coarse tier's material (MapTerrainMesh.coarse_material): cut by terrain_cut

void fragment() {
	if (coarse && cut_here(UV)) {
		discard;
	}
	vec3 c = mix(cover(UV), COLOR.rgb, COLOR.a);
	ALBEDO = to_linear(c) * texture(detail, UV).rgb;
}

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	sl_up_v = (VIEW_MATRIX * vec4(sl_up_world(wp), 0.0)).xyz;
	sl_ax_v = (VIEW_MATRIX * vec4(1.0, 0.0, 0.0, 0.0)).xyz;
	sl_xh = vec2(wp.x, 10000.0 - length(wp.yz));
}

void light() {
	// the sun or moon from the Spindle right overhead wherever this ground is (spindle_light.gdshaderinc)
	DIFFUSE_LIGHT += sl_diffuse(LIGHT_IS_DIRECTIONAL, NORMAL, LIGHT, LIGHT_COLOR, ATTENUATION);
}

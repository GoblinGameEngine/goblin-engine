// The terrain's coarse far tier.  Beyond flat_arc of arc round the ring from the player it is
// the far side of the cylinder, drawn flat: the baked top-down image of the finished world
// (remake/farside/f_SS_XX.webp, one per far tile: UV2 is map metres, tile_rect where this tile's image lies) -- roofs, roads, fields, trees and water as surface colour, lit
// by the Spindle overhead like everything else (spindle_light.gdshaderinc: each point from its own Spindle, so the whole
// ring is sunlit by day and moonlit by night).  Nearer, the ordinary ground: land cover per pixel
// (or the vertex colour where it says so, alpha 1) on the neutral detail texture.  The switch is per pixel, so it lands exactly where the
// far side's objects are hidden (RemakeFarSide).
//
// At night the towns light up across the ring (the user, 2026-10-14: "We need to see lights baked into the farside
// texture"): night_lights (remake/farside/n_SS_XX.webp, tools/farside_night.py: windows, street lamps, harbours, the
// south coast's coloured festoons, over the same tile_rect) glow as emission, twinkling a little.  Nearer than the far
// side, from NIGHT_IN on, the same lights fade in on the coarse ground so nothing pops at flat_arc: there, under the
// real buildings they're hidden, and on the streets they read as the lamps' pools.
shader_type spatial;
render_mode cull_back;

uniform sampler2D farside : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D detail : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D night_lights : source_color, filter_linear_mipmap, repeat_disable;
uniform bool has_night = false;
uniform float night_gain = 9.0;
uniform float flat_arc = 916.0;
uniform vec4 tile_rect = vec4(0.0, 0.0, 1.0, 1.0);    // (s0, x0, w, h) m: the area this tile's image covers
global uniform float farside_player_s;      // the player's s (RemakeFarSide)
global uniform float daylight;            // 1 by day, 0 at night (DaySkySystem)
#include "res://remake/shaders/land_cover.gdshaderinc"
#include "res://remake/shaders/spindle_light.gdshaderinc"

const float NIGHT_IN = 700.0;          // m: the baked lights start fading in here (full by flat_arc)

float hash12(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	sl_up_v = (VIEW_MATRIX * vec4(sl_up_world(wp), 0.0)).xyz;
	sl_ax_v = (VIEW_MATRIX * vec4(1.0, 0.0, 0.0, 0.0)).xyz;
	sl_xh = vec2(wp.x, 10000.0 - length(wp.yz));
}

void fragment() {
	if (cut_here(UV)) {
		discard;                                // (the fine ground is complete here: MapTerrainMesh._cut)
	}
	float s = UV2.x;
	float d = abs(mod(s - farside_player_s + circ * 0.5, circ) - circ * 0.5);
	vec2 tuv = (UV2 - tile_rect.xy) / tile_rect.zw;
	if (d > flat_arc) {
		ALBEDO = texture(farside, tuv).rgb;
	} else {
		vec3 c = to_linear(mix(cover(UV), COLOR.rgb, COLOR.a));
		ALBEDO = c * texture(detail, UV).rgb;
	}
	ROUGHNESS = 0.95;
	if (has_night) {
		float night = clamp((0.75 - daylight) / 0.5, 0.0, 1.0);
		// (within flat_arc the real buildings' windows and the street lamps are drawn: the baked lights only beyond it,
		// and the towns' soft halo only from well across the ring -- seen low from inside a town, the halo of the
		// ground round it read as a blinding white band at the horizon)
		float reach = smoothstep(flat_arc, flat_arc + 1000.0, d);
		float near_k = 1.0 - smoothstep(flat_arc + 1000.0, 6000.0, d);
		if (night * reach > 0.001) {
			vec3 nl = texture(night_lights, tuv).rgb;
			nl = mix(nl, max(nl - vec3(0.35), vec3(0.0)) * 1.5, near_k);     // (near: the points, not the halo)
			// a slow twinkle, per 8 m cell: the far towns glitter
			vec2 cell = floor(UV2 / 8.0);
			float h = hash12(cell);
			float tw = 0.8 + 0.2 * sin(TIME * (0.6 + 2.2 * h) + h * 40.0);
			EMISSION = min(nl * nl * night_gain, vec3(mix(2.2, 1.0, near_k))) * night * reach * tw;   // (squared: the bright points stay bright, the halo dim; capped: no white blow-outs)
		}
	}
}

void light() {
	// the sun or moon from the Spindle right overhead wherever this ground is -- the far side, the ring's sides
	DIFFUSE_LIGHT += sl_diffuse(LIGHT_IS_DIRECTIONAL, NORMAL, LIGHT, LIGHT_COLOR, ATTENUATION);
}

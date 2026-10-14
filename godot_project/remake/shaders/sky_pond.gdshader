shader_type spatial;
// A sky island's pond or lake (SkyIsland._build_water).  It's cold in the clouds (the user, 2026-10-14: "a scant ice
// texture along the shoreline with lots of breaks. The ponds will not be frozen, just frosty"): dark cold water, a milky
// frost haze drifting over it, and thin plates of shore ice in the shallows -- broken into floes, many of them gone.
// Depth comes from the island's own height grid (height_tex, metres; `grid` maps it): depth = level - deck height.
render_mode blend_mix, depth_draw_always, cull_disabled, specular_schlick_ggx;

uniform sampler2D height_tex : filter_linear, repeat_disable;
uniform vec4 grid;                    // x0, z0 of the first sample's cell edge, and the grid's size in metres
uniform float level = -0.25;
uniform float ice_reach = 0.9;        // m of depth the shore ice reaches out over
uniform float floe_m = 1.7;           // m: a floe's size
uniform float keep = 0.42;            // the share of floes still there

varying vec3 lpos;

void vertex() {
	lpos = VERTEX;                    // (the island's own frame: the floes ride with it)
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// a cellular field: x the distance to the nearest cell edge, y the cell's id
vec2 floes(vec2 p) {
	vec2 n = floor(p);
	vec2 f = fract(p);
	float d1 = 8.0;
	float d2 = 8.0;
	vec2 id = vec2(0.0);
	for (int j = -1; j <= 1; j++) {
		for (int i = -1; i <= 1; i++) {
			vec2 g = vec2(float(i), float(j));
			vec2 o = vec2(hash(n + g), hash(n + g + 17.3)) * 0.8 + 0.1;
			float d = length(g + o - f);
			if (d < d1) {
				d2 = d1;
				d1 = d;
				id = n + g;
			} else if (d < d2) {
				d2 = d;
			}
		}
	}
	return vec2(d2 - d1, hash(id + 3.7));
}

void fragment() {
	vec2 uv = (lpos.xz - grid.xy) / grid.zw;
	float h = texture(height_tex, uv).r;
	float depth = level - h;
	vec3 shallow = vec3(0.20, 0.31, 0.34);
	vec3 deep = vec3(0.05, 0.11, 0.15);
	vec3 col = mix(shallow, deep, smoothstep(0.0, 3.0, depth));
	// frost: a faint milky haze, slowly drifting
	float haze = noise(lpos.xz * 0.12 + TIME * 0.01) * 0.6 + noise(lpos.xz * 0.45) * 0.4;
	col = mix(col, vec3(0.74, 0.81, 0.85), 0.10 + 0.14 * haze);
	// shore ice: floes in the shallows, scant and broken
	vec2 fl = floes(lpos.xz / floe_m);
	float reach = ice_reach * (0.6 + 0.8 * fl.y);
	float shore = 1.0 - smoothstep(reach * 0.55, reach, depth);
	float there = step(1.0 - keep, fract(fl.y * 7.13));
	float crack = smoothstep(0.03, 0.11, fl.x);
	float ice = shore * there * crack;
	vec3 ice_col = mix(vec3(0.80, 0.88, 0.92), vec3(0.93, 0.96, 0.98), noise(lpos.xz * 2.0));
	ALBEDO = mix(col, ice_col, ice);
	ROUGHNESS = mix(0.08, 0.6, ice);
	SPECULAR = 0.6;
	ALPHA = mix(0.9, 1.0, ice);
}

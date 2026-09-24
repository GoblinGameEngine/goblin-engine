// High cirrus (RemakeClouds): flat translucent ribbons wrapped round the central shaft.  The wisps
// are procedural -- fibrous noise stretched along the ribbon (UV.x runs round the axis, UV.y
// across it), feathered at every edge.  Lit evenly from either side (thin cloud scatters, it has no dark face).
shader_type spatial;
render_mode blend_mix, cull_disabled, depth_draw_never, specular_disabled, shadows_disabled;

uniform vec3 color : source_color = vec3(1.0, 1.0, 1.0);
uniform float opacity = 0.75;
varying float seed;

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise2(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash2(i), hash2(i + vec2(1, 0)), f.x), mix(hash2(i + vec2(0, 1)), hash2(i + vec2(1, 1)), f.x), f.y);
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int k = 0; k < 5; k++) {
		v += a * noise2(p);
		p = p * 2.03 + vec2(1.7, 9.2);
		a *= 0.5;
	}
	return v;
}

void vertex() {
	seed = UV2.x;               // per ribbon (RemakeClouds merges a band's ribbons into one mesh)
}

void fragment() {
	vec2 uv = UV;
	// fibres: noise squashed along the ribbon, bent by a slow wave across it
	float bend = (fbm(vec2(uv.x * 2.0, seed)) - 0.5) * 0.35;
	vec2 p = vec2(uv.x * 3.0, (uv.y + bend) * 22.0) + vec2(seed * 13.0, seed * 7.0);
	float fib = fbm(p);
	float body = fbm(vec2(uv.x * 5.0 + seed * 3.0, uv.y * 3.0));
	float a = smoothstep(0.45, 0.8, fib * 0.6 + body * 0.6);
	// feathered edges: thin at both ends of the ribbon and at its sides
	a *= smoothstep(0.0, 0.2, uv.x) * smoothstep(1.0, 0.8, uv.x);
	a *= smoothstep(0.0, 0.35, uv.y) * smoothstep(1.0, 0.65, uv.y);
	ALBEDO = color;
	ALPHA = a * opacity;
	ROUGHNESS = 1.0;
}

void light() {
	DIFFUSE_LIGHT += LIGHT_COLOR * ATTENUATION * 0.6 / PI;
}

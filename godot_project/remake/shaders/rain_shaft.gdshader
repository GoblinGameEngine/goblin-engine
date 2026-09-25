// A storm's rain seen from outside it (RemakeRain): an open cylinder from the cloud base to the
// floor with fine falling streaks -- thin, many, short, two layers at different speeds over a
// soft grey haze -- faded at the top and bottom and thinned by intensity.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, blend_mix, shadows_disabled;

uniform float intensity = 1.0;
uniform float height = 300.0;
uniform vec3 tint : source_color = vec3(0.6, 0.63, 0.7);

float hash(float n) { return fract(sin(n * 12.9898) * 43758.5453); }

float streaks(vec2 uv, float cols, float len, float speed, float seed) {
	float col = floor(uv.x * cols);
	float h = hash(col + seed);
	float y = fract(uv.y * height / (len * (0.7 + 0.6 * h)) - TIME * speed * (0.8 + 0.4 * h) + h);
	return smoothstep(0.0, 0.04, y) * smoothstep(0.3, 0.06, y) * step(0.45, hash(col * 1.7 + seed));
}

void fragment() {
	// UV.x round the cylinder, UV.y from its top (0) to the floor (1)
	float s = streaks(UV, 3000.0, 3.0, 9.0, 0.0) + 0.7 * streaks(UV, 2200.0, 2.2, 7.0, 31.0);
	float a = (0.16 + 0.22 * s) * intensity;
	a *= smoothstep(0.0, 0.08, UV.y) * smoothstep(1.0, 0.9, UV.y);
	ALBEDO = tint;
	ALPHA = clamp(a, 0.0, 0.6);
}

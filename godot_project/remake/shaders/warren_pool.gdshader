shader_type spatial;
// A pool of light on the ground under a warren street light at night (SkyWarren._make_flares, one MultiMesh of 2 m
// planes scaled to the pool's radius): a soft additive disc in the light's colour, fading out by range_m, gone by day.
// INSTANCE_CUSTOM: r a phase, g strength; COLOR the light's colour.
render_mode unshaded, blend_add, depth_draw_never, cull_back, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float range_m = 120.0;
uniform float gain = 0.22;

varying float fade;
varying vec3 tint;

void vertex() {
	float d = length((MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz);
	fade = 1.0 - smoothstep(range_m * 0.6, range_m, d);
	tint = COLOR.rgb;
}

void fragment() {
	float night = clamp((0.75 - daylight) / 0.45, 0.0, 1.0);
	if (night * fade < 0.01) {
		discard;
	}
	vec2 p = UV * 2.0 - 1.0;
	float r2 = dot(p, p);
	float a = exp(-r2 * 3.2) * (1.0 - smoothstep(0.7, 1.0, r2));
	ALBEDO = mix(tint, vec3(1.0, 0.92, 0.8), 0.35) * a * gain * night * fade;
}

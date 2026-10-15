shader_type spatial;
// Lens flare on a warren's brightest lights at night (SkyWarren._make_flares, one MultiMesh): a camera-facing soft glare
// with a faint horizontal streak, fading out by range_m and invisible by day.  INSTANCE_CUSTOM: r a phase, g strength; COLOR the light's colour.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float range_m = 150.0;

varying float fade;
varying float phase;
varying float strength;
varying vec3 tint;

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0), vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0),
		vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0), vec4(0.0, 0.0, 0.0, 1.0));
	float d = length((MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz);
	fade = 1.0 - smoothstep(range_m * 0.6, range_m, d);
	phase = INSTANCE_CUSTOM.r;
	strength = INSTANCE_CUSTOM.g;
	tint = COLOR.rgb;
}

void fragment() {
	float night = clamp((0.75 - daylight) / 0.45, 0.0, 1.0);
	if (night * fade < 0.01) {
		discard;
	}
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float core = exp(-r * r * 9.0);
	float halo = exp(-r * r * 2.2) * 0.35;
	float streak = exp(-abs(p.y) * 28.0) * (1.0 - smoothstep(0.3, 1.0, abs(p.x))) * 0.35;
	float edge = 1.0 - smoothstep(0.55, 1.0, r);   // (nothing at the quad's edge: no visible square)
	float tw = 0.85 + 0.15 * sin(TIME * (1.3 + phase * 2.0) + phase * 30.0);
	vec3 c = mix(mix(tint, vec3(1.0), 0.25), vec3(1.0, 0.97, 0.9), core);   // a white-hot core in the light's colour
	ALBEDO = c * (core + halo + streak) * edge * night * fade * tw * (0.6 + strength);
}

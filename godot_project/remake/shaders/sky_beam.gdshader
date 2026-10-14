shader_type spatial;
// A searchlight sweeping the night sky from a roof (SkySigns: the grand openings, the lashings' welcome): a long
// soft cone, additive, turning about the island's up and nodding.  The mesh is a cone along +Y from the origin;
// INSTANCE-free: per material speed / phase / colour.  Night only.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform vec3 color : source_color = vec3(0.85, 0.9, 1.0);
uniform float speed = 0.25;           // rad/s round
uniform float phase = 0.0;
uniform float tilt = 0.45;            // rad from straight up, swinging +-0.2

varying float along;
varying float across;

void vertex() {
	along = UV.y;
	across = UV.x;
	float a = TIME * speed + phase;
	float t = tilt + 0.2 * sin(TIME * speed * 1.7 + phase * 3.0);
	// tilt about X, then turn about Y
	vec3 v = VERTEX;
	v = vec3(v.x, v.y * cos(t) - v.z * sin(t), v.y * sin(t) + v.z * cos(t));
	v = vec3(v.x * cos(a) + v.z * sin(a), v.y, -v.x * sin(a) + v.z * cos(a));
	VERTEX = v;
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night < 0.01) {
		discard;
	}
	float edge = pow(sin(3.14159 * across), 2.0);
	float fade = pow(1.0 - along, 1.6) * smoothstep(0.0, 0.03, along);
	ALBEDO = color * edge * fade * 0.55 * night;
}

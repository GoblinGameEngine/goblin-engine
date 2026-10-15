// The Spindle's light, at every point of the floor (the user, 2026-10-14: "The moonlight should illuminate the entire
// ring, not just the slice where the character is standing").  The one DirectionalLight (DaySkySystem) is aimed from the
// sleeve down at the player: anywhere else round the ring it would come in at a slant, sideways, or from below.  But the
// light is the Spindle overhead everywhere, so a shader including this lights each point from ITS own Spindle above it,
// slanted toward the active sleeve along the axis and weaker the further the sleeve is (DaySkySystem's own fall-off) --
// at the player exactly what the DirectionalLight gives; round the ring, the same sun or moon.  Other lights (lamps,
// headlights) light as usual.
//   Include it; in vertex() set the varyings (Godot allows that only there):
//       vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
//       sl_up_v = (VIEW_MATRIX * vec4(sl_up_world(wp), 0.0)).xyz;
//       sl_ax_v = (VIEW_MATRIX * vec4(1.0, 0.0, 0.0, 0.0)).xyz;
//       sl_xh = vec2(wp.x, 10000.0 - length(wp.yz));
//   and add sl_diffuse(...) to DIFFUSE_LIGHT in light().
global uniform vec4 moon_sleeve;      // x: the active sleeve's x (m), y: its fall-off at the player (DaySkySystem)

varying vec3 sl_up_v;                 // this point's up (toward the axis), view space
varying vec3 sl_ax_v;                 // the axis (+x), view space
varying vec2 sl_xh;                   // its x and height over the floor

vec3 sl_up_world(vec3 wp) {
	return -normalize(vec3(0.0, wp.y, wp.z) + vec3(0.0, 1e-4, 0.0));
}

float sl_falloff(float x, float h) {
	float hgt = 8000.0 - h;               // (R - SHAFT_R - h)
	float dx = x - moon_sleeve.x;
	return clamp(pow(hgt / sqrt(dx * dx + hgt * hgt), 1.5), 0.33, 1.0);
}

vec3 sl_light_dir() {
	// toward the active sleeve on the Spindle, seen from here
	float hgt = 8000.0 - sl_xh.y;
	return normalize(normalize(sl_up_v) * hgt + normalize(sl_ax_v) * (moon_sleeve.x - sl_xh.x));
}

vec3 sl_diffuse(bool directional, vec3 normal, vec3 light, vec3 light_color, float attenuation) {
	if (directional) {
		float k = sl_falloff(sl_xh.x, sl_xh.y) / max(moon_sleeve.y, 0.33);
		return light_color * attenuation * max(dot(normal, sl_light_dir()), 0.0) * k / PI;
	}
	return light_color * attenuation * max(dot(normal, light), 0.0) / PI;
}

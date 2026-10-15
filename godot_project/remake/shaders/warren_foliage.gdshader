shader_type spatial;
// The warrens' plants (SkyPlants: one MultiMesh per species per island quadrant).  Toon-lit vertex colour; the plant
// sways in its own frame: UV2.x the bend weight (0 at the root), UV2.y the flutter (leaves).  The wind is given in the
// island's frame and turned into the plant's by its yaw (INSTANCE_CUSTOM.g, a turn 0..1); INSTANCE_CUSTOM.r is the
// phase, hashed from where the plant stands on the island (so a moving island's plants don't reshuffle); the instance
// colour tints it.
render_mode diffuse_toon, specular_disabled, cull_disabled;

global uniform float daylight;
uniform vec2 wind = vec2(0.8, 0.6);          // the island frame's x, z
uniform float bend = 0.18;                   // m at the crown, at bend weight 1
uniform float flutter = 0.05;

void vertex() {
	float phase = INSTANCE_CUSTOM.r * 6.2832;
	float yaw = INSTANCE_CUSTOM.g * 6.2832;
	vec2 w = vec2(wind.x * cos(yaw) + wind.y * sin(yaw), -wind.x * sin(yaw) + wind.y * cos(yaw));   // (turned back by yaw)
	float t = TIME;
	float gust = 0.6 + 0.4 * sin(t * 0.37 + phase * 0.5);
	float b = UV2.x * UV2.x * bend * gust * (0.7 + 0.3 * sin(t * 1.3 + phase));
	float f = UV2.y * flutter * sin(t * 7.0 + phase * 3.0 + VERTEX.x * 2.1 + VERTEX.z * 1.7);
	VERTEX.xz += w * b + vec2(f, -f * 0.6);
	VERTEX.y += f * 0.5 - b * b * 0.3;
}

void fragment() {
	ALBEDO = pow(COLOR.rgb, vec3(2.2));             // (the colours are sRGB, as the kit's)
	ROUGHNESS = 1.0;
	// (by night a touch of the lamps' warmth on the near side: the street lights don't light them)
	float night = clamp((0.75 - daylight) / 0.45, 0.0, 1.0);
	EMISSION = ALBEDO * vec3(0.12, 0.09, 0.06) * night;
}

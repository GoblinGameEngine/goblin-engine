shader_type spatial;
// Grass blades on a warren's greens, banks and garden beds (SkyWarren._grass: one MultiMesh of blade clumps per
// chunk).  UV.y is up the blade (the sway weight); the wind is in the island's frame (clumps aren't turned, so the
// mesh frame is the island's), phased by INSTANCE_CUSTOM.r (hashed from where the clump stands on the island); the
// instance colour is the civ's grass with a little variation.  Past fade_from the blades sink into the ground by
// range_m: no pop, no transparency.
render_mode diffuse_toon, specular_disabled, cull_disabled, shadows_disabled;

uniform vec2 wind = vec2(0.8, 0.6);
uniform float bend = 0.12;
uniform float fade_from = 26.0;
uniform float range_m = 40.0;

varying float tip;

void vertex() {
	float d = length((MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz);
	float keep = 1.0 - smoothstep(fade_from, range_m, d);
	float ph = INSTANCE_CUSTOM.r * 6.2832;
	float t = TIME;
	float w = UV.y * UV.y * bend * (0.6 + 0.4 * sin(t * 1.7 + ph + VERTEX.x * 3.0)) * (0.7 + 0.3 * sin(t * 0.4 + ph * 0.3));
	VERTEX.xz += wind * w;
	VERTEX.y *= keep;
	tip = UV.y;
}

void fragment() {
	vec3 c = pow(COLOR.rgb, vec3(2.2));
	ALBEDO = mix(c * 0.55, c * 1.15, tip);       // (darker at the root: reads as depth)
	ROUGHNESS = 1.0;
	NORMAL = mix(NORMAL, (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz, 0.6);   // (lit like the ground: no flicker)
}

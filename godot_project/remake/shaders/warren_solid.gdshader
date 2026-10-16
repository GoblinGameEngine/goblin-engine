shader_type spatial;
// A warren's opaque surfaces (SkyWarren: the "solid" and "metal" groups of every chunk, LOD0 and MID): the vertex colour
// (the kit's shade x its palette slot), and at night the light of the warren's own lamps falling on them -- the pools
// (the user, 2026-10-16: "pools of light from the light sources that spill over ... cumulatively fade as the player
// gains distance from the light sources").  The island's lamp field (SkyWarren._field: every light of the twin json
// splatted into a 3D grid of the island, 2 m across, 2 m up, falling off over metres, stored 1 - exp(-sum)) is sampled per fragment in the
// island's frame: bright at and under each lamp, dark between them.  No lights, one texture fetch.
render_mode diffuse_lambert, specular_schlick_ggx;

global uniform float daylight;
uniform float roughness_k = 0.9;
uniform float metallic_k = 0.0;
uniform sampler3D field : filter_linear, repeat_disable, hint_default_black;
uniform vec3 field_origin = vec3(0.0);       // island frame: the grid's corner
uniform vec3 field_size = vec3(1.0);         // m the grid spans
uniform float field_gain = 1.2;              // emission at a saturated pool, x albedo (sunlight ~1)
instance uniform vec3 chunk_origin;          // island frame: this chunk's centre (its mesh is about it)

varying vec3 lp;

void vertex() {
	lp = VERTEX + chunk_origin;
}

void fragment() {
	ALBEDO = pow(COLOR.rgb, vec3(2.2));
	ROUGHNESS = roughness_k;
	METALLIC = metallic_k;
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night > 0.001) {
		vec3 q = (lp - field_origin) / field_size;
		vec3 uvw = vec3(q.x, q.z, q.y);          // (SkyWarren._field_materials: images x by z, layers up y)
		vec3 l = texture(field, uvw).rgb * field_gain;
		EMISSION = ALBEDO * l * night;
	}
}

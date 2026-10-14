// Low cumulus (RemakeClouds): opaque, cartoon cel-shaded -- a bright sunlit side, a cool
// blue-grey shade side, one hard terminator between -- so the screen outline pass inks only
// the silhouette.  The albedo is kept below white so the ambient alone doesn't wash it out.
shader_type spatial;
render_mode cull_back, specular_disabled;

uniform vec3 body_color : source_color = vec3(0.74, 0.77, 0.86);
uniform vec3 sun_color : source_color = vec3(1.0, 0.98, 0.94);
uniform vec3 front_color : source_color = vec3(0.58, 0.6, 0.66);
// the plain cloud's colour: the sunlit side is sun_color for it, and darker for a darker body (a storm
// cell, a front's cloud) -- dividing by body_color itself made every cell's sunny side white
uniform vec3 plain_color : source_color = vec3(0.74, 0.77, 0.86);
instance uniform float shade = 0.0;     // 0..1: how deep in a weather front the cloud is (RemakeClouds._life_step)

void fragment() {
	ALBEDO = mix(body_color, front_color, shade);
	ROUGHNESS = 1.0;
}

void light() {
	// two hard bands: in the sun, or in shade (ambient only)
	float d = dot(NORMAL, LIGHT) * ATTENUATION;
	float lit = step(0.2, d);
	DIFFUSE_LIGHT += sun_color / plain_color * LIGHT_COLOR * lit * 0.55 / PI;
}

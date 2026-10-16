shader_type spatial;
// An island shop sign's blank (SkySigns._wblank: the SIGNS agent's sky_a / sky_b atlas cells): its painted face lit
// like any surface by day; at night only what the art marks as lit (the atlas's _emit mask) glows, at the lit-face
// scale of SIGN_EMIT (<= 0.9: under the glow threshold, so the letters on it keep their contrast).
render_mode cull_disabled, specular_disabled;   // (SkySigns._quad winds counter-clockwise: draw both sides)

global uniform float daylight;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D emit_tex : filter_linear_mipmap, repeat_disable;
uniform float face_emit = 0.8;

void fragment() {
	vec3 c = texture(albedo_tex, UV).rgb;
	ALBEDO = c;
	ROUGHNESS = 0.8;
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	EMISSION = c * texture(emit_tex, UV).r * face_emit * night;
}

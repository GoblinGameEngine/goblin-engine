shader_type spatial;
// Snow on a sky island (SkyIsland: the material_overlay of every mesh of its near and mid tiers).  `snow` 0..1 is how
// much has fallen: snow_coverage.png's R is a rank-equalised low-frequency field, so snow lies wherever R < snow --
// patches that spread and join into a blanket as it builds, and shrink back the same way as it melts (the user,
// 2026-10-14: "a slowly changing texture that leads to a blanket of snow").  Only on faces turned up (up is away from
// the axis -- every point's own up on the cylinder); G breaks the patches' edges, B glints.
render_mode blend_mix, depth_draw_never, cull_back, diffuse_lambert, specular_disabled;

uniform float snow = 0.0;
uniform sampler2D snow_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D cover_tex : filter_linear_mipmap, repeat_enable;
uniform float patch_m = 23.0;        // m: the coverage field's tile
uniform float grain_m = 2.5;         // m: the snow texture's tile

varying vec3 lpos;
varying vec3 wpos;
varying vec3 wnrm;

void vertex() {
	lpos = VERTEX;                                       // (the mesh's own frame: the pattern rides with the island)
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	if (snow <= 0.001) {
		discard;
	}
	vec3 up = -normalize(vec3(0.0, wpos.y, wpos.z));
	float facing = dot(normalize(wnrm), up);
	// more snow lets it creep further down slopes
	float lie = smoothstep(mix(0.75, 0.35, snow), mix(0.92, 0.6, snow), facing);
	vec2 uv = lpos.xz;
	vec3 cv = texture(cover_tex, uv / patch_m).rgb;
	float edge = (cv.g - 0.5) * 0.08;
	float cover = smoothstep(-0.025, 0.025, snow * 1.04 - cv.r + edge);
	float a = cover * lie;
	if (a < 0.01) {
		discard;
	}
	vec3 grain = texture(snow_tex, uv / grain_m).rgb;
	ALBEDO = grain * 0.97;
	ROUGHNESS = 0.85;
	EMISSION = vec3(0.6) * cv.b * step(0.82, cv.b) * cover * 0.3;   // a glint here and there
	ALPHA = a;
}

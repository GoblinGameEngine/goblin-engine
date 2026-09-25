// Land cover per pixel from remake/landcover.png (MapTerrainMesh.make_material / RemakeFarSide set the
// uniforms); the same colour table as MapTerrainMesh._cover_tint (sRGB).  UV is (x, s) / tex_m.

uniform sampler2D landcover : filter_nearest, repeat_disable;
uniform float tex_m = 8.0;
uniform float lc_step = 4.0;
uniform float circ = 18849.56;
uniform float half_len = 4000.0;

const vec3 GRASS = vec3(0.42, 0.53, 0.27);
const vec3 FIELD[6] = vec3[6](vec3(0.28, 0.45, 0.15), vec3(0.5, 0.6, 0.24), vec3(0.7, 0.6, 0.33),
	vec3(0.4, 0.58, 0.27), vec3(0.45, 0.53, 0.3), vec3(0.56, 0.53, 0.35));
const float FIELD_VAR[4] = float[4](0.9, 0.97, 1.03, 1.1);

vec3 cover(vec2 uv) {
	float s = mod(uv.y * tex_m, circ);
	float x = uv.x * tex_m + half_len;
	ivec2 size = textureSize(landcover, 0);
	ivec2 p = clamp(ivec2(floor(vec2(s, x) / lc_step)), ivec2(0), size - 1);
	vec4 t = texelFetch(landcover, p, 0);
	int cls = int(round(t.r * 255.0));
	int g = int(round(t.g * 255.0));
	if (cls == 2) return vec3(0.46, 0.6, 0.32);
	if (cls == 3) return vec3(0.2, 0.32, 0.14);
	if (cls == 4) return FIELD[min(g % 8, 5)] * FIELD_VAR[(g / 8) % 4];
	if (cls == 5) return vec3(0.22, 0.34, 0.15);
	if (cls == 6) return vec3(0.83, 0.76, 0.58);
	if (cls == 7) return vec3(0.46, 0.43, 0.39);
	return GRASS;
}

vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}


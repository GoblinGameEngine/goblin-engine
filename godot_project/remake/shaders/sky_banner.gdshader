shader_type spatial;
// The islands' banners, dock flags and rooftop pennants (SkyBanners: MultiMeshes for the whole sky).  The mesh is a
// 1 m strip hanging from y 0 down to -len_m (UV.y 0 at the top .. 1 at the foot), scaled 10-20 m wide per island.  A
// banner hangs mostly flat and facing out, so its lettering reads: a gentle billow, a slow sway, hardly any twist,
// weighted at the foot by a batten -- phased by the banner (INSTANCE_CUSTOM.r, hashed in the island's frame), so a
// moving island's banners don't reshuffle -- and cut to its furled length (INSTANCE_CUSTOM.g).  A flag (`flag`) is the same
// strip turned out sideways from its mast.  Colour: the clan's colours in bands with a woven motif (COLOR: colour A;
// INSTANCE_CUSTOM.b: colour B packed 0xRRGGBB), or the SIGNS atlas cell (INSTANCE_CUSTOM.a mod 1000) when bound.
// Lit softly from within at night: they read against the dark sky.
render_mode cull_disabled, diffuse_toon, specular_disabled;

global uniform float daylight;
uniform float len_m = 300.0;
uniform bool flag = false;
uniform bool has_atlas = false;
uniform sampler2D atlas : source_color, filter_linear_mipmap, repeat_disable;
uniform sampler2D atlas_emit : filter_linear_mipmap, repeat_disable;
uniform vec2 atlas_grid = vec2(8.0, 8.0);
uniform vec3 wind = vec3(1.0, 0.0, 0.35);     // (in the island's frame: islands don't turn)
uniform bool has_names = false;
uniform sampler2D names : filter_linear_mipmap, repeat_disable;   // (SkyBanners._bake_names: a name down each cell)
uniform vec2 name_grid = vec2(32.0, 4.0);

varying vec3 col_b;
varying float t_along;
varying float cell;
varying float name_cell;

vec3 unpack(float p) {
	float r = floor(p / 65536.0);
	float g = floor((p - r * 65536.0) / 256.0);
	float b = p - r * 65536.0 - g * 256.0;
	return vec3(r, g, b) / 255.0;
}

void vertex() {
	float ph = INSTANCE_CUSTOM.r * 6.2832;
	float lenk = INSTANCE_CUSTOM.g;
	col_b = unpack(INSTANCE_CUSTOM.b);
	cell = mod(INSTANCE_CUSTOM.a, 1000.0) - 1.0;      // (stored + 1: -1 none)
	name_cell = floor(COLOR.a * 255.0);
	float t = UV.y;
	t_along = t;
	float L = len_m * (flag ? 1.0 : lenk);
	float y = -t * L;
	float x = VERTEX.x;
	float tm = TIME;
	if (flag) {
		// out from the mast along +x, the cloth waving in z
		float wv = sin(t * 9.0 - tm * 6.0 + ph) * 0.35 * t + sin(t * 4.0 - tm * 3.1 + ph * 2.0) * 0.2 * t;
		VERTEX = vec3(t * L, x - t * 0.4, wv);
	} else {
		// down, weighted: a gentle billow out of its plane, a slow sway, a little lean downwind, the foot steadied
		float foot = 1.0 - smoothstep(0.85, 1.0, t);                // (the batten: stiller at the very foot)
		float billow = (sin(t * 5.0 - tm * 0.9 + ph) * 1.2 + sin(t * 11.0 - tm * 1.7 + ph * 2.0) * 0.4) * t * foot;
		float edge = (abs(UV.x - 0.5) * 2.0);
		billow += sin(tm * 0.8 + ph + t * 3.0) * 0.25 * edge * t;     // (the edges ripple a little more)
		float sway = sin(tm * 0.21 + ph) * 0.025 * t * t * L;         // (a slow pendulum: ~7 m at the foot of 300 m)
		float tw = sin(tm * 0.17 + ph * 2.0) * 0.12 * t;               // (hardly any twist: the face stays out)
		vec2 xz = vec2(x * cos(tw), x * sin(tw));
		vec3 lean = normalize(wind) * (t * t * L * 0.03);              // (weighted: hangs nearly plumb)
		VERTEX = vec3(xz.x + sway, y, xz.y + billow) + lean;
	}
}

void fragment() {
	vec3 a = COLOR.rgb;
	vec3 c;
	float lit = 0.55;                          // night emission (x albedo); the lettering's own: SIGN_EMIT
	if (has_atlas && cell >= 0.0 && !flag) {
		// the SIGNS agent's banner (signs.json banner_atlas): its cell down the whole length, cap at the top, tail below
		vec2 g = vec2(mod(cell, atlas_grid.x), floor(cell / atlas_grid.x));
		vec4 tx = texture(atlas, (g + vec2(UV.x, t_along)) / atlas_grid);
		if (tx.a < 0.5) {
			discard;                                  // (the forked tails)
		}
		c = pow(tx.rgb, vec3(1.0 / 2.2));             // (source_color already linear: ALBEDO below re-linearises)
		lit = mix(0.08, 1.6, texture(atlas_emit, (g + vec2(UV.x, t_along)) / atlas_grid).r);
	} else if (!flag && has_names) {
		// (until SIGNS' strips land) the island's name down the banner on its colour A, repeated, framed in B with the
		// woven motif in the border, a dark batten at the foot
		float rep = 3.0;
		float seg = fract(t_along * rep);
		vec2 g = vec2(mod(name_cell, name_grid.x), floor(name_cell / name_grid.x));
		float m = texture(names, (g + vec2(UV.x * 0.9 + 0.05, seg)) / name_grid).r;
		float border = step(0.86, abs(UV.x - 0.5) * 2.0);
		vec2 q = vec2(UV.x * 2.0, fract(t_along * 60.0));
		float dia = abs(fract(q.x) - 0.5) + abs(q.y - 0.5);
		c = mix(a, col_b, smoothstep(0.35, 0.65, m));
		lit = mix(0.12, 1.6, smoothstep(0.35, 0.65, m));   // (the letters lit, the ground dim: they read at night)
		c = mix(c, mix(col_b, a, step(dia, 0.3)), border);
		c = mix(c, vec3(0.12), step(0.985, t_along));
	} else {
		// bands of the clan's colours, a woven diamond motif in each A band, edged in B
		float band = floor(t_along * (flag ? 3.0 : 14.0));
		bool isA = mod(band, 2.0) < 1.0;
		vec2 q = vec2(UV.x, fract(t_along * (flag ? 3.0 : 14.0)));
		float dia = abs(q.x - 0.5) + abs(q.y - 0.5);
		float motif = step(dia, 0.28) * step(0.16, dia);
		float edge = step(0.92, abs(UV.x - 0.5) * 2.0);
		c = isA ? mix(a, col_b, motif) : col_b;
		c = mix(c, isA ? col_b : a, edge);
	}
	ALBEDO = pow(c, vec3(2.2));
	ROUGHNESS = 0.9;
	float night = clamp((0.75 - daylight) / 0.45, 0.0, 1.0);
	EMISSION = ALBEDO * lit * night;
}

shader_type spatial;
// Comic-book outlines, take 2: screen-space depth/normal edge detection,
// replacing the old per-object inverted-hull system (ToonShading.gd's
// retired outline material/next_pass code, shaders/toon_outline.gdshader
// -- deleted, not just unused, since nothing references the old
// technique anymore).
//
// WHY THE SWITCH: inverted-hull offsets a copy of each mesh outward by a
// flat WORLD-SPACE distance. That has three known failure modes, and
// after fixing the first two live (thin rods reading as fat tubes, flat
// QuadMesh sprites producing solid black slabs -- see ToonShading.gd's
// git history / reference/memory.txt for both), a THIRD, more
// fundamental one remained: a fixed world-space offset is a bigger
// fraction of the screen the closer the camera gets, regardless of the
// object's own shape -- there's no per-object width tuning that fixes
// this, because it isn't a per-object problem. This is why the producer
// reported outlines "looking good far away" but getting worse at medium
// then close range: that's the technique's own math, not a bug to
// isolate and patch.
//
// This shader sidesteps the whole class of bug: outline THICKNESS is
// defined in screen pixels (outline_thickness_px), so it's already
// naturally distance-correct by construction -- nothing to tune per
// object, per shape, or per distance. It draws exactly ONE full-screen
// pass reading the depth and normal buffers the renderer already
// produced for the frame (no second geometry pass per outlined object,
// unlike inverted-hull's next_pass), comparing each pixel to its
// neighbors: a sharp jump in depth means a real silhouette edge (this
// object is in front of something else); a sharp jump in normal means a
// real crease (two faces meeting at an angle, e.g. a wall/ceiling
// seam) even when depth is continuous. Both together cover what
// inverted-hull was trying to approximate with actual geometry.
//
// REQUIRES the Forward+ renderer -- hint_normal_roughness_texture is not
// available under Mobile (confirmed: attempting to compile this shader
// under Mobile fails). Measured live on this project's own dev hardware
// before committing to the switch (see reference/memory.txt): Forward+
// measured ~15% slower than Mobile as a bare renderer change (12-13fps
// -> 10-12fps, same test scene/position), a real but survivable cost --
// expected to be more than paid back by retiring inverted-hull's
// per-object double-draw entirely. Verify this project's own real
// before/after numbers rather than trusting that expectation blindly.
//
// Rendered as a full-screen overlay: a plain QuadMesh, parented to the
// active Camera3D (see ScreenOutline.gd), whose vertex shader below
// hijacks POSITION directly into clip space -- the mesh's own world
// transform stops mattering the moment this runs, which is what makes
// "just place a quad anywhere in view of the camera" a working
// full-screen effect instead of needing exact near-plane math.
//
// REAL BUG, found live and chased at length: a wide, solid black region
// covered everything past ~45-48m from the camera on any long, fairly
// flat sightline (a straight road). Root cause: a flat surface viewed at
// a shallow/grazing angle has a depth-per-SCREEN-PIXEL gradient that
// grows with distance (ordinary perspective foreshortening) -- at the
// outline's original thickness (1.4px), a "1 pixel over" neighbor
// sample at 50m+ lands a real, non-trivial world-space distance away
// from the center sample, on ground that -- while visually flat and
// continuous -- has enough genuine small-scale variation over that
// distance to read as an edge. Several fixes were attempted first that
// LOOKED plausible and were even individually correct on their own
// terms (a NaN guard in view_normal() for a near-zero background-pixel
// decode; an isnan() guard on normal_jump directly; capping depth
// samples before differencing) but none of them was actually what fixed
// the visible bug -- confirmed each time by adding a debug mode that
// outputs the raw internal values as precisely-decodable colors and
// reading them back pixel-by-pixel with PIL, rather than trusting a
// screenshot by eye. What actually worked, verified the same way: simply
// making outline_thickness_px itself smaller (1.4 -> 0.4) shrinks the
// real-world sampling gap enough that ordinary ground never trips the
// sensitivity thresholds, at any distance tested. A more elaborate
// distance-based fade on depth_jump/normal_jump was also tried and its
// math checked out on paper, but empirically it never reduced the
// values it was supposed to reduce for reasons that didn't resolve under
// direct measurement -- removed rather than shipped half-understood.
// The NaN guards stayed since they're correct regardless.

render_mode unshaded, depth_draw_never, depth_test_disabled, cull_disabled, fog_disabled;

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest;
uniform sampler2D normal_tex : hint_normal_roughness_texture, filter_nearest;

// REAL BUG, found live, superseding the note this replaces (which
// claimed 0.4 was "verified live" -- it wasn't verified rigorously
// enough: the earlier tests happened to sample pixels where this still
// produced a stray edge by chance, not because the technique generally
// worked): depth_tex/normal_tex are both filter_nearest, and a screen
// fragment's own SCREEN_UV sits pixel-CENTERED -- i.e. already at the
// midpoint of its own texel. Offsetting that UV by anything under half
// a texel width, in either direction, rounds straight back to the SAME
// texel under nearest filtering; it never reaches a neighbor to diff
// against. At 0.4px (well under half of a 1px-wide texel) this isn't an
// occasional miss, it's unconditional: EVERY fragment's four neighbor
// taps collapsed onto its own center sample, so depth_jump and
// normal_jump came out exactly 0.0 everywhere, at every distance,
// including dead-on silhouette edges -- confirmed by a temporary
// debug_mode dumping the raw reconstructed d_c value next to debug_mode
// 3's raw texture sample: d_c varied correctly with real scene structure
// on its own, but the neighbor-difference math built on top of it read
// uniformly black across the whole screen. 1.0px is the real floor for
// this technique to detect anything at all under nearest filtering, so
// that's the new default and the new hint_range minimum -- also happens
// to satisfy "give outlines a minimum width so distant objects don't
// lose them" for free, since this is screen-space and already
// distance-independent by construction once it's actually sampling a
// neighbor. If the old 45-48m grazing-angle false-positive (see file
// header) comes back at 1.0px where it didn't at 0.4, that means 0.4 was
// only ever "fixing" it by being too small to detect ANY edge, not by
// being a real fix -- the right follow-up there is a grazing-angle-aware
// sensitivity term, not shrinking this back below the functional floor.
uniform float outline_thickness_px : hint_range(1.0, 4.0) = 1.0;
// Relative depth jump (fraction of the pixel's own view-space distance
// from camera) that counts as a silhouette edge -- relative, not
// absolute, so the same threshold works whether the edge is 2m or 200m
// away (an absolute-meters threshold would either miss distant edges
// entirely or false-positive on every close-up texture bump).
uniform float depth_sensitivity : hint_range(0.005, 0.2) = 0.03;
// 1 - dot(neighbor normals) that counts as a real crease.
uniform float normal_sensitivity : hint_range(0.05, 1.0) = 0.35;
uniform vec4 outline_color : source_color = vec4(0.02, 0.02, 0.02, 1.0);
// Live-toggleable diagnostic (set_shader_parameter, no relaunch needed):
// 1 = raw edge boolean, 2 = depth_jump (R, /2 scale) + normal_jump (G,
// /4 scale), 3 = raw depth_tex sample (G) + log-scaled unprojected d_c
// (R) -- for exact PIL pixel readback when chasing a bug like the ones
// above again. hint_range's upper bound was still 2 despite mode 3
// existing since it was added -- fixed, it's only an editor slider bound
// anyway, never a runtime clamp, but a stale one is still worth fixing.
uniform int debug_mode : hint_range(0, 3) = 0;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

// REAL BUG found live: INV_PROJECTION_MATRIX is one of the Godot shader
// built-ins that's only visible directly inside vertex()/fragment(), not
// from a helper function called from them (compile error: "Unknown
// identifier in expression: 'INV_PROJECTION_MATRIX'") -- passed in
// explicitly as a parameter instead.
float view_depth(vec2 uv, mat4 inv_proj) {
	float d = texture(depth_tex, uv).r;
	vec4 ndc = vec4(uv * 2.0 - 1.0, d, 1.0);
	vec4 view = inv_proj * ndc;
	view.xyz /= view.w;
	return -view.z;
}

// REAL BUG found live: pixels where nothing meaningful was rendered
// (background/sky, wherever NORMAL_ROUGHNESS_TEXTURE was never written)
// read back as a neutral mid-gray (0.5, 0.5, 0.5), which decodes to
// (0,0,0) BEFORE normalizing -- normalize() of a zero-length vector is
// 0/0, i.e. NaN, in every component. Fixed at the source: treat a
// near-zero (un-normalizable) sample as "no real surface here,"
// explicitly, before normalize() ever runs.
vec3 view_normal(vec2 uv) {
	vec3 raw = texture(normal_tex, uv).rgb * 2.0 - 1.0;
	if (length(raw) < 0.01) {
		return vec3(0.0, 0.0, 1.0);
	}
	return normalize(raw);
}

void fragment() {
	vec2 texel = outline_thickness_px / VIEWPORT_SIZE;
	vec2 uv = SCREEN_UV;
	mat4 inv_proj = INV_PROJECTION_MATRIX;

	float d_c = view_depth(uv, inv_proj);
	float d_l = view_depth(uv - vec2(texel.x, 0.0), inv_proj);
	float d_r = view_depth(uv + vec2(texel.x, 0.0), inv_proj);
	float d_u = view_depth(uv + vec2(0.0, texel.y), inv_proj);
	float d_d = view_depth(uv - vec2(0.0, texel.y), inv_proj);
	float depth_jump = (abs(d_c - d_l) + abs(d_c - d_r) + abs(d_c - d_u) + abs(d_c - d_d)) / max(d_c, 0.05);

	vec3 n_c = view_normal(uv);
	vec3 n_l = view_normal(uv - vec2(texel.x, 0.0));
	vec3 n_r = view_normal(uv + vec2(texel.x, 0.0));
	vec3 n_u = view_normal(uv + vec2(0.0, texel.y));
	vec3 n_d = view_normal(uv - vec2(0.0, texel.y));
	float normal_jump = (1.0 - dot(n_c, n_l)) + (1.0 - dot(n_c, n_r)) + (1.0 - dot(n_c, n_u)) + (1.0 - dot(n_c, n_d));
	// Belt-and-suspenders NaN guard -- see view_normal()'s own comment;
	// this catches it if it ever reaches this far regardless.
	if (isnan(normal_jump)) {
		normal_jump = 0.0;
	}

	float edge = max(step(depth_sensitivity, depth_jump), step(normal_sensitivity, normal_jump));

	if (debug_mode == 1) {
		ALBEDO = vec3(edge, edge, edge);
		ALPHA = 1.0;
	} else if (debug_mode == 2) {
		float depth_nan = isnan(depth_jump) ? 1.0 : 0.0;
		ALBEDO = vec3(clamp(depth_jump / 2.0, 0.0, 1.0), clamp(normal_jump / 4.0, 0.0, 1.0), depth_nan);
		ALPHA = 1.0;
	} else if (debug_mode == 3) {
		// Raw d_c, log-scaled so both a 15m tree and a "huge/wrong" sky
		// value are distinguishable in one 0-255 channel: R = log2(d_c+1)/16.
		float raw_d = texture(depth_tex, uv).r;
		ALBEDO = vec3(clamp(log2(d_c + 1.0) / 16.0, 0.0, 1.0), raw_d, 0.0);
		ALPHA = 1.0;
	} else {
		ALBEDO = outline_color.rgb;
		ALPHA = edge * outline_color.a;
	}
}

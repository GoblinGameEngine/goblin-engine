shader_type canvas_item;

// Simple multi-tap blur of whatever's behind this control, tinted dark and
// translucent -- used for the dialog box background.
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform float blur_amount : hint_range(0.0, 8.0) = 4.0;
uniform vec4 tint_color : source_color = vec4(0.0, 0.0, 0.0, 0.55);

void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 texel = blur_amount / vec2(textureSize(screen_tex, 0));
	vec4 sum = vec4(0.0);
	for (int x = -2; x <= 2; x++) {
		for (int y = -2; y <= 2; y++) {
			vec2 offset = vec2(float(x), float(y)) * texel;
			sum += textureLod(screen_tex, uv + offset, 0.0);
		}
	}
	vec3 blurred = (sum / 25.0).rgb;
	vec3 final_rgb = mix(blurred, tint_color.rgb, tint_color.a);
	COLOR = vec4(final_rgb, 1.0);
}

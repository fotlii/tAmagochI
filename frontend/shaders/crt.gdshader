// CRT / ambient glow post-process shader.
// Applied to the root viewport for a retro terminal look.
// Adds subtle vignette, scanlines, and phosphor bloom.

shader_type canvas_item;

uniform float scanline_strength : hint_range(0.0, 0.5) = 0.06;
uniform float vignette_strength : hint_range(0.0, 1.0) = 0.35;
uniform float aberration        : hint_range(0.0, 0.02) = 0.003;
uniform vec4  tint_color        : source_color = vec4(0.0, 0.9, 1.0, 1.0);
uniform float tint_amount       : hint_range(0.0, 0.3) = 0.05;

void fragment() {
	vec2 uv = UV;

	// Chromatic aberration
	float r = texture(TEXTURE, uv + vec2(aberration, 0.0)).r;
	float g = texture(TEXTURE, uv).g;
	float b = texture(TEXTURE, uv - vec2(aberration, 0.0)).b;
	float a = texture(TEXTURE, uv).a;
	vec4 col = vec4(r, g, b, a);

	// CRT scanlines
	float scanline = sin(UV.y * SCREEN_PIXEL_SIZE.y * 800.0 * 3.14159) * 0.5 + 0.5;
	col.rgb -= scanline * scanline_strength;

	// Vignette
	vec2 vig_uv = uv * (1.0 - uv.yx);
	float vig = pow(vig_uv.x * vig_uv.y * 15.0, vignette_strength);
	col.rgb *= vig;

	// Subtle teal tint for ambiance
	col.rgb = mix(col.rgb, tint_color.rgb, tint_amount * col.a);

	COLOR = col;
}

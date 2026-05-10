// Glitch shader for the creature's stressed state.
// Applies horizontal scan-line displacement, chromatic aberration,
// and digital noise. Parameters controlled by GDScript.

shader_type canvas_item;

uniform float glitch_intensity : hint_range(0.0, 1.0) = 0.0;
uniform float time_scale : hint_range(0.1, 5.0) = 1.0;

// Pseudo-random function
float rand(vec2 co) {
	return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 uv = UV;
	float t = TIME * time_scale;

	if (glitch_intensity > 0.0) {
		// Horizontal band displacement
		float band_y = floor(uv.y * 20.0) / 20.0;
		float noise   = rand(vec2(band_y, floor(t * 8.0)));
		float shift   = (noise - 0.5) * 0.04 * glitch_intensity;

		// Only shift some rows
		if (rand(vec2(band_y + 0.1, t)) > 0.7) {
			uv.x += shift;
		}

		// Chromatic aberration
		float ca_amount = 0.006 * glitch_intensity;
		vec4 col_r = texture(TEXTURE, uv + vec2(ca_amount, 0.0));
		vec4 col_g = texture(TEXTURE, uv);
		vec4 col_b = texture(TEXTURE, uv - vec2(ca_amount, 0.0));

		COLOR = vec4(col_r.r, col_g.g, col_b.b, col_g.a);

		// Scanline flicker
		float scanline = sin(uv.y * 80.0 + t * 10.0) * 0.04 * glitch_intensity;
		COLOR.rgb -= scanline;

		// Digital noise speckles
		float speckle = rand(uv + vec2(t * 0.1, 0.0));
		if (speckle > 0.97 && glitch_intensity > 0.4) {
			COLOR.rgb = vec3(1.0, 0.2, 0.6) * speckle;
		}
	} else {
		COLOR = texture(TEXTURE, uv);
	}
}

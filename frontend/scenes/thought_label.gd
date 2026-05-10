## thought_label.gd
## Displays short ambient thoughts from the creature.
## Text is now larger and centered for better readability.

extends Label

var _fade_tween: Tween = null

func _ready() -> void:
	modulate.a = 0.0
	# Vibrant, readable color
	add_theme_color_override("font_color", Color(1.0, 1.0, 1.0, 1.0))
	horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vertical_alignment = VERTICAL_ALIGNMENT_CENTER

func show_thought(thought_text: String, duration: float = 4.0) -> void:
	if _fade_tween:
		_fade_tween.kill()

	text = thought_text
	_fade_tween = create_tween()
	_fade_tween.set_trans(Tween.TRANS_SINE)
	_fade_tween.set_ease(Tween.EASE_IN_OUT)
	
	# Fade in and scale slightly for emphasis
	modulate.a = 0.0
	_fade_tween.tween_property(self, "modulate:a", 1.0, 0.6)
	
	# Hold
	_fade_tween.tween_interval(duration)
	
	# Fade out
	_fade_tween.tween_property(self, "modulate:a", 0.0, 1.0)

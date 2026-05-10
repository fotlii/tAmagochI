## creature.gd
## The visual creature. Uses AnimatedSprite2D with SpriteFrames.
##
## Animation convention:
##   "<state>_intro"  — plays once when entering state (optional)
##   "<state>_loop"   — loops indefinitely while in state
##   "blink"          — plays once, returns to loop (timer-driven)
##
## Each emotional state maps to an intro+loop pair.
## If no intro exists for a state, it jumps straight to the loop.

extends Node2D

# ── State tracking ─────────────────────────────────────────────────────────────
var current_state: String = "idle"
var emotional_vars: Dictionary = {}
var state_duration: float = 0.0
var idle_seconds: float = 0.0

# ── Node references ────────────────────────────────────────────────────────────
@onready var sprite      : AnimatedSprite2D = $Sprite
@onready var glow_light  : PointLight2D     = $GlowLight
@onready var blink_timer : Timer            = $BlinkTimer
@onready var micro_timer : Timer            = $MicroTimer
@onready var eyes_node   : Node2D           = $Eyes

# ── Animation state machine ────────────────────────────────────────────────────
var _in_intro: bool = false
var _pending_loop: String = ""   # loop animation to start after intro
var _currently_blinking: bool = false

# ── Glow lerp targets ──────────────────────────────────────────────────────────
var _target_glow_color  : Color = Color(0.30, 0.82, 0.88)
var _target_glow_energy : float = 0.5

# ── Breathing / procedural ────────────────────────────────────────────────────
var _breathing_phase : float = 0.0
var _base_position   : Vector2 = Vector2.ZERO
var _look_target     : Vector2 = Vector2.ZERO
var _look_current    : Vector2 = Vector2.ZERO

# ── State → visual config ──────────────────────────────────────────────────────
const STATE_CONFIGS := {
	"idle": {
		"intro":         "",
		"loop":          "idle_loop",
		"glow_color":    Color(0.30, 0.82, 0.88),
		"glow_energy":   0.4,
		"breathe_speed": 0.55,
		"breathe_amp":   2.0,
	},
	"sleeping": {
		"intro":         "sleep_intro",
		"loop":          "sleep_loop",
		"glow_color":    Color(0.10, 0.14, 0.48),
		"glow_energy":   0.15,
		"breathe_speed": 0.20,
		"breathe_amp":   1.0,
	},
	"curious": {
		"intro":         "curious_intro",
		"loop":          "curious_loop",
		"glow_color":    Color(0.50, 0.80, 0.76),
		"glow_energy":   0.7,
		"breathe_speed": 0.9,
		"breathe_amp":   3.0,
	},
	"focused": {
		"intro":         "focused_intro",
		"loop":          "focused_loop",
		"glow_color":    Color(0.0, 0.90, 1.0),
		"glow_energy":   0.95,
		"breathe_speed": 0.4,
		"breathe_amp":   1.5,
	},
	"stressed": {
		"intro":         "stressed_intro",
		"loop":          "stressed_loop",
		"glow_color":    Color(1.0, 0.25, 0.51),
		"glow_energy":   0.85,
		"breathe_speed": 1.4,
		"breathe_amp":   4.5,
	},
	"lonely": {
		"intro":         "",
		"loop":          "idle_loop",
		"glow_color":    Color(0.33, 0.43, 0.48),
		"glow_energy":   0.2,
		"breathe_speed": 0.35,
		"breathe_amp":   1.5,
	},
	"happy": {
		"intro":         "happy_intro",
		"loop":          "happy_loop",
		"glow_color":    Color(1.0, 0.5, 0.8),
		"glow_energy":   0.8,
		"breathe_speed": 1.0,
		"breathe_amp":   3.0,
	},
	"gaming": {
		"intro":         "gaming_intro",
		"loop":          "gaming_loop",
		"glow_color":    Color(0.6, 0.2, 1.0),
		"glow_energy":   0.8,
		"breathe_speed": 1.2,
		"breathe_amp":   2.5,
	},
	"watching": {
		"intro":         "curious_intro",
		"loop":          "curious_loop",
		"glow_color":    Color(0.8, 0.8, 0.4),
		"glow_energy":   0.6,
		"breathe_speed": 0.5,
		"breathe_amp":   2.0,
	},
}


# ── Lifecycle ──────────────────────────────────────────────────────────────────

func _ready() -> void:
	_base_position = position
	sprite.animation_finished.connect(_on_animation_finished)

	blink_timer.wait_time = randf_range(3.0, 8.0)
	blink_timer.start()
	micro_timer.wait_time = randf_range(10.0, 22.0)
	micro_timer.start()

	_transition_to("idle")


func _process(delta: float) -> void:
	_update_breathing(delta)
	_update_look(delta)
	_update_glow_lerp(delta)


# ── Public API ─────────────────────────────────────────────────────────────────

func apply_state(data: Dictionary) -> void:
	var new_state: String = data.get("state", "idle")
	emotional_vars  = data.get("vars", {})
	state_duration  = data.get("state_duration", 0.0)
	idle_seconds    = data.get("idle_seconds", 0.0)

	if new_state != current_state:
		_transition_to(new_state)


func react_to_stimulus(event: String, intensity: float) -> void:
	match event:
		"build_failure":
			_flash_glitch(intensity)
		"new_app":
			_quick_look_around()
		"music":
			_gentle_bob()
		"long_ai_chat":
			_brighten_briefly()
		"varied_activity":
			_quick_look_around()


# ── State machine ──────────────────────────────────────────────────────────────

func _transition_to(new_state: String) -> void:
	current_state = new_state
	var cfg = STATE_CONFIGS.get(new_state, STATE_CONFIGS["idle"])

	_target_glow_color  = cfg["glow_color"]
	_target_glow_energy = cfg["glow_energy"]

	var is_glitchy = (new_state == "stressed")
	_set_glitch(0.3 if is_glitchy else 0.0)

	var intro: String = cfg.get("intro", "")
	var loop:  String = cfg.get("loop", "idle_loop")

	if intro != "" and _has_animation(intro):
		_in_intro = true
		_pending_loop = loop
		_play_animation(intro, false)
	else:
		_in_intro = false
		_pending_loop = ""
		_play_animation(loop, true)


func _on_animation_finished() -> void:
	if _in_intro and _pending_loop != "":
		_in_intro = false
		_play_animation(_pending_loop, true)
	elif _currently_blinking:
		_currently_blinking = false
		var cfg = STATE_CONFIGS.get(current_state, STATE_CONFIGS["idle"])
		var loop = cfg.get("loop", "idle_loop")
		_play_animation(loop, true)


# ── Animation helpers ──────────────────────────────────────────────────────────

func _play_animation(anim_name: String, looping: bool) -> void:
	if not _has_animation(anim_name):
		anim_name = "idle_loop"
		looping = true

	if sprite.sprite_frames:
		sprite.sprite_frames.set_animation_loop(anim_name, looping)

	sprite.play(anim_name)


func _has_animation(anim_name: String) -> bool:
	if sprite == null or sprite.sprite_frames == null:
		return false
	if not sprite.sprite_frames.has_animation(anim_name):
		return false
	return sprite.sprite_frames.get_frame_count(anim_name) > 0


# ── Glitch shader ──────────────────────────────────────────────────────────────

func _set_glitch(intensity: float) -> void:
	if sprite.material and sprite.material is ShaderMaterial:
		sprite.material.set_shader_parameter("glitch_intensity", intensity)


# ── Procedural animation ───────────────────────────────────────────────────────

func _update_breathing(delta: float) -> void:
	var cfg = STATE_CONFIGS.get(current_state, STATE_CONFIGS["idle"])
	var speed: float = cfg.get("breathe_speed", 0.55)
	var amp:   float = cfg.get("breathe_amp", 2.0)

	_breathing_phase = fmod(_breathing_phase + delta * speed, TAU)
	var offset_y = sin(_breathing_phase) * amp

	if current_state == "stressed":
		offset_y += randf_range(-1.2, 1.2)

	position.y = _base_position.y + offset_y


func _update_look(delta: float) -> void:
	if current_state in ["curious", "focused"]:
		var mouse_world = get_global_mouse_position()
		_look_target = (mouse_world - global_position).limit_length(7.0)
	elif current_state == "sleeping":
		_look_target = Vector2.ZERO
	else:
		if randf() < 0.004:
			_look_target = Vector2(randf_range(-5, 5), randf_range(-3, 3))

	_look_current = _look_current.lerp(_look_target, delta * 3.0)
	if eyes_node:
		eyes_node.position = _look_current


func _update_glow_lerp(delta: float) -> void:
	if glow_light:
		glow_light.color  = glow_light.color.lerp(_target_glow_color, delta * 1.5)
		glow_light.energy = lerp(glow_light.energy, _target_glow_energy, delta * 1.5)


# ── Micro-reactions ────────────────────────────────────────────────────────────

func _flash_glitch(intensity: float) -> void:
	_set_glitch(min(intensity, 1.0))
	var t = create_tween()
	t.tween_callback(func(): _set_glitch(0.3 if current_state == "stressed" else 0.0)).set_delay(0.5)


func _quick_look_around() -> void:
	if _in_intro or _currently_blinking:
		return
	var t = create_tween()
	t.tween_property(eyes_node if eyes_node else self, "position:x",
		(eyes_node.position.x if eyes_node else 0) + 6, 0.15)
	t.tween_property(eyes_node if eyes_node else self, "position:x",
		(eyes_node.position.x if eyes_node else 0) - 6, 0.3)
	t.tween_property(eyes_node if eyes_node else self, "position:x",
		eyes_node.position.x if eyes_node else 0, 0.2)


func _gentle_bob() -> void:
	var t = create_tween()
	t.set_ease(Tween.EASE_IN_OUT)
	t.tween_property(self, "position:y", _base_position.y - 4, 0.3)
	t.tween_property(self, "position:y", _base_position.y, 0.4)


func _brighten_briefly() -> void:
	if not glow_light:
		return
	var orig = glow_light.energy
	var t = create_tween()
	t.tween_property(glow_light, "energy", min(orig + 0.4, 1.5), 0.5)
	t.tween_property(glow_light, "energy", orig, 1.5)


# ── Timer callbacks ────────────────────────────────────────────────────────────

func _on_blink_timer_timeout() -> void:
	if current_state == "sleeping" or _in_intro or _currently_blinking:
		blink_timer.wait_time = randf_range(2.0, 6.0)
		blink_timer.start()
		return

	if _has_animation("blink"):
		_currently_blinking = true
		_play_animation("blink", false)

	blink_timer.wait_time = randf_range(3.0, 9.0)
	blink_timer.start()


func _on_micro_timer_timeout() -> void:
	if not _in_intro and not _currently_blinking:
		match randi() % 4:
			0: _quick_look_around()
			1: _gentle_bob()
			2: pass
			3: pass
	micro_timer.wait_time = randf_range(10.0, 25.0)
	micro_timer.start()

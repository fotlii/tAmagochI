## main.gd
## Root scene script — manages WebSocket connection and UI updates.

extends Node

const WS_URL := "ws://127.0.0.1:8765"
const RECONNECT_DELAY := 3.0

var _socket: WebSocketPeer
var _reconnect_timer: float = 0.0
var _connected: bool = false

@onready var creature = $Creature
@onready var thought_label = $ThoughtLabel
@onready var status_label = $StatusLabel
@onready var debug_label = $DebugOverlay

# HUD Elements (Updated for Rings)
@onready var stress_bar = $HUD/StatsPanel/StressBar
@onready var focus_bar = $HUD/StatsPanel/FocusBar
@onready var social_bar = $HUD/StatsPanel/SocialBar
@onready var cpu_ring = $HUD/SysVisuals/CPU_Ring
@onready var ram_ring = $HUD/SysVisuals/RAM_Ring


func _ready() -> void:
	_connect_to_backend()
	# Force exact window size and position (Top-Left 0,0)
	get_window().size = Vector2i(320, 480)
	get_window().position = Vector2i(0, 15)
	get_window().transparent_bg = true
	get_window().borderless = true
	get_window().always_on_top = true


func _process(delta: float) -> void:
	if _socket == null:
		return

	_socket.poll()
	var state = _socket.get_ready_state()

	match state:
		WebSocketPeer.STATE_OPEN:
			if not _connected:
				_connected = true
				debug_label.text = "alive ✦"
				debug_label.modulate = Color(0.2, 1.0, 0.6, 0.4)

			while _socket.get_available_packet_count() > 0:
				var raw = _socket.get_packet().get_string_from_utf8()
				_handle_message(raw)

		WebSocketPeer.STATE_CLOSED:
			if _connected:
				_connected = false
				debug_label.text = "reconnecting..."
				debug_label.modulate = Color(1.0, 0.4, 0.2, 0.3)
			_reconnect_timer += delta
			if _reconnect_timer >= RECONNECT_DELAY:
				_reconnect_timer = 0.0
				_connect_to_backend()

func _connect_to_backend() -> void:
	_socket = WebSocketPeer.new()
	_socket.connect_to_url(WS_URL)

func _handle_message(raw: String) -> void:
	var parsed = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_DICTIONARY:
		return

	var msg_type = parsed.get("type", "")

	match msg_type:
		"state_update":
			creature.apply_state(parsed)
			
			# Update Status
			var state_name = parsed.get("state", "idle")
			status_label.text = "state: " + state_name
			
			# Update HUD Bars
			var vars = parsed.get("vars", {})
			_update_bar(stress_bar, vars.get("stress", 0.0) * 100.0)
			_update_bar(focus_bar, vars.get("focus", 0.0) * 100.0)
			_update_bar(social_bar, vars.get("social_energy", 0.0) * 100.0)
			
			# Update System Rings (CPU / RAM)
			var cpu = parsed.get("cpu_load", 0.0)
			var ram = parsed.get("ram_usage", 0.0)
			_update_ring(cpu_ring, cpu)
			_update_ring(ram_ring, ram)

		"thought":
			var text: String = parsed.get("text", "")
			var duration: int = parsed.get("duration_ms", 4000)
			thought_label.show_thought(text, duration / 1000.0)

		"stimulus":
			var event: String = parsed.get("event", "")
			var intensity: float = parsed.get("intensity", 1.0)
			creature.react_to_stimulus(event, intensity)

func _update_bar(bar: ProgressBar, target_value: float) -> void:
	var tween = create_tween()
	tween.tween_property(bar, "value", target_value, 0.5).set_trans(Tween.TRANS_SINE)

func _update_ring(ring: Control, target_value: float) -> void:
	var tween = create_tween()
	tween.tween_property(ring, "value", target_value, 0.5).set_trans(Tween.TRANS_SINE)

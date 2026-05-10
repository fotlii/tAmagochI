## ring_gauge.gd
## Draws a circular gauge for system stats.
## Optimized for small screens.

extends Control

@export var ring_color: Color = Color(0.3, 0.8, 1.0, 0.6)
@export var bg_color: Color = Color(0.2, 0.2, 0.2, 0.3)
@export var thickness: float = 3.0

var value: float = 0.0:
	set(v):
		value = clamp(v, 0.0, 100.0)
		queue_redraw()

func _draw() -> void:
	var center = size / 2.0
	var radius = (min(size.x, size.y) / 2.0) - (thickness / 2.0)
	
	# Draw background circle
	draw_arc(center, radius, 0, TAU, 64, bg_color, thickness, true)
	
	# Draw value arc (starting from top)
	var start_angle = -PI / 2.0
	var end_angle = start_angle + (TAU * (value / 100.0))
	draw_arc(center, radius, start_angle, end_angle, 64, ring_color, thickness, true)

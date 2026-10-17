extends Area3D

func _ready() -> void:
	set_as_top_level(true)
	body_entered.connect(_on_body_entered)
	get_tree().create_timer(20.0).timeout.connect(queue_free)

func _on_body_entered(body: Node) -> void:
	if body is RCCar:
		body.pisar_aceite()
		queue_free()

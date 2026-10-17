extends Area3D

@export var velocidad: float = 38.0
@export var fuerza_explosion: float = 300.0
@export var vida_util: float = 4.0

var vector_direccion: Vector3 = Vector3.FORWARD
var creador: Node = null

func disparar(dir: Vector3, shooter: Node) -> void:
	vector_direccion = dir.normalized()
	creador = shooter
	set_as_top_level(true)

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	get_tree().create_timer(vida_util).timeout.connect(queue_free)

func _physics_process(delta: float) -> void:
	global_position += vector_direccion * velocidad * delta

func _on_body_entered(body: Node) -> void:
	if body == creador:
		return

	if body is RCCar:
		body.recibir_impacto_cohete(global_position, fuerza_explosion)
	elif body is RigidBody3D:
		var dir = (body.global_position - global_position).normalized()
		body.apply_central_impulse(dir * 120.0)

	queue_free()

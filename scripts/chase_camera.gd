extends Camera3D

@export var objetivo: Node3D
@export var distancia_atras: float = 2.4
@export var altura: float = 0.75
@export var suavizado_posicion: float = 12.0
@export var suavizado_rotacion: float = 8.0
@export var fov_base: float = 78.0
@export var fov_max: float = 95.0

func _physics_process(delta: float) -> void:
	if not objetivo:
		return

	var pos_atras: Vector3 = objetivo.global_transform.origin + (objetivo.global_transform.basis.z * distancia_atras) + (Vector3.UP * altura)
	global_position = global_position.lerp(pos_atras, suavizado_posicion * delta)

	var rot_objetivo = Transform3D().looking_at(objetivo.global_position + Vector3.UP * 0.25 - global_position, Vector3.UP).basis
	global_basis = global_basis.slerp(rot_objetivo, suavizado_rotacion * delta)

	if objetivo is RigidBody3D:
		var vel: float = (objetivo as RigidBody3D).linear_velocity.length()
		var fov_dinamico: float = clamp(fov_base + (vel * 0.6), fov_base, fov_max)
		fov = lerp(fov, fov_dinamico, 5.0 * delta)

extends Camera3D

@export var objetivo: RCCar
@export var distancia_atras: float = 2.4
@export var altura: float = 0.75
@export var suavizado_posicion: float = 14.0
@export var suavizado_rotacion: float = 9.0
@export var fov_base: float = 78.0
@export var fov_max: float = 98.0

func _physics_process(delta: float) -> void:
	if not objetivo:
		return

	var invert_sign: float = -1.0 if objetivo.mirando_atras else 1.0
	var pos_deseada: Vector3 = objetivo.global_position + (objetivo.global_transform.basis.z * distancia_atras * invert_sign) + (Vector3.UP * altura)
	global_position = global_position.lerp(pos_deseada, suavizado_posicion * delta)

	var punto_mira: Vector3 = objetivo.global_position + Vector3.UP * 0.25
	var rot_objetivo = Transform3D().looking_at(punto_mira - global_position, Vector3.UP).basis
	global_basis = global_basis.slerp(rot_objetivo, suavizado_rotacion * delta)

	var vel: float = objetivo.linear_velocity.length()
	var fov_dinamico: float = clamp(fov_base + (vel * 0.7), fov_base, fov_max)
	fov = lerp(fov, fov_dinamico, 6.0 * delta)

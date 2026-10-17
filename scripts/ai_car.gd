extends VehicleBody3D
class_name AICar

@export var waypoints_root: Node3D
@export var velocidad_crucero: float = 380.0

var waypoints: Array[Node3D] = []
var indice_objetivo: int = 0
var distancia_umbral: float = 5.5

func _ready() -> void:
	mass = 40.0
	center_of_mass_mode = RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
	center_of_mass = Vector3(0.0, -0.16, 0.0)
	
	if waypoints_root:
		for child in waypoints_root.get_children():
			if child is Node3D:
				waypoints.append(child)

func _physics_process(delta: float) -> void:
	if waypoints.is_empty():
		return

	var wp_pos = waypoints[indice_objetivo].global_position
	var a_wp = wp_pos - global_position
	a_wp.y = 0.0

	if a_wp.length() < distancia_umbral:
		indice_objetivo = (indice_objetivo + 1) % waypoints.size()
		return

	var frente = -transform.basis.z
	frente.y = 0.0
	frente = frente.normalized()
	var dir_norm = a_wp.normalized()

	var angulo = frente.signed_angle_to(dir_norm, Vector3.UP)
	steering = lerp(steering, clamp(angulo * 1.5, -0.52, 0.52), 6.0 * delta)

	if abs(angulo) > 0.4:
		engine_force = velocidad_crucero * 0.55
		brake = 2.0
	else:
		engine_force = velocidad_crucero
		brake = 0.0

func recibir_impacto_cohete(pos: Vector3, fuerza: float) -> void:
	var dir = (global_position - pos).normalized()
	dir.y += 0.5
	apply_central_impulse(dir * fuerza)
	engine_force = 0.0
	brake = 10.0

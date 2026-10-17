extends VehicleBody3D
class_name RCCar

enum PowerUp { NONE, ROCKET, OIL }

@export var max_fuerza_motor: float = 380.0
@export var max_fuerza_freno: float = 18.0
@export var max_angulo_giro: float = 0.52
@export var velocidad_retorno_giro: float = 6.0
@export var masa_chasis: float = 45.0

@export var rocket_scene: PackedScene = preload("res://scenes/Rocket.tscn")
@export var oil_scene: PackedScene = preload("res://scenes/OilSlick.tscn")

@onready var weapon_spawn_front: Marker3D = $WeaponFront
@onready var weapon_spawn_rear: Marker3D = $WeaponRear

var current_powerup: PowerUp = PowerUp.NONE
var angulo_actual_giro: float = 0.0
var esta_patinando: bool = false
var tiempo_patinaje: float = 0.0

func _ready() -> void:
	mass = masa_chasis
	center_of_mass_mode = RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
	center_of_mass = Vector3(0.0, -0.15, 0.0)

func _physics_process(delta: float) -> void:
	if esta_patinando:
		_procesar_trompo(delta)
		return

	_procesar_direccion(delta)
	_procesar_motor()
	_procesar_acciones()

func _procesar_direccion(delta: float) -> void:
	var dir_input: float = Input.get_axis("girar_der", "girar_izq")
	var objetivo: float = dir_input * max_angulo_giro
	angulo_actual_giro = lerp(angulo_actual_giro, objetivo, velocidad_retorno_giro * delta)
	steering = angulo_actual_giro

func _procesar_motor() -> void:
	var accel_input: float = Input.get_axis("frenar", "acelerar")
	var marcha_adelante_dot: float = linear_velocity.dot(-transform.basis.z)

	if accel_input > 0.0:
		engine_force = accel_input * max_fuerza_motor
		brake = 0.0
	elif accel_input < 0.0:
		if marcha_adelante_dot > 0.5:
			engine_force = 0.0
			brake = max_fuerza_freno
		else:
			engine_force = accel_input * (max_fuerza_motor * 0.55)
			brake = 0.0
	else:
		engine_force = 0.0
		brake = 1.2

func _procesar_acciones() -> void:
	if Input.is_action_just_pressed("usar_item"):
		activar_arma()

	if Input.is_action_just_pressed("reset_auto"):
		voltear_coche()

func activar_arma() -> void:
	match current_powerup:
		PowerUp.ROCKET:
			if rocket_scene and weapon_spawn_front:
				var cohete = rocket_scene.instantiate()
				get_tree().root.add_child(cohete)
				cohete.global_transform = weapon_spawn_front.global_transform
				cohete.disparar(-transform.basis.z, self)
			current_powerup = PowerUp.NONE
		PowerUp.OIL:
			if oil_scene and weapon_spawn_rear:
				var aceite = oil_scene.instantiate()
				get_tree().root.add_child(aceite)
				aceite.global_transform = weapon_spawn_rear.global_transform
			current_powerup = PowerUp.NONE
		PowerUp.NONE:
			pass

func recibir_arma(tipo: PowerUp) -> void:
	current_powerup = tipo

func pisar_aceite() -> void:
	if esta_patinando:
		return
	esta_patinando = true
	tiempo_patinaje = 1.3
	apply_torque_impulse(Vector3.UP * 70.0)

func _procesar_trompo(delta: float) -> void:
	tiempo_patinaje -= delta
	engine_force = 0.0
	brake = 0.5
	if tiempo_patinaje <= 0.0:
		esta_patinando = false
		angular_velocity = Vector3.ZERO

func recibir_impacto_cohete(pos_explosion: Vector3, fuerza: float) -> void:
	var direccion: Vector3 = (global_position - pos_explosion).normalized()
	direccion.y += 0.5
	apply_central_impulse(direccion.normalized() * fuerza)
	pisar_aceite()

func voltear_coche() -> void:
	var dir_frente: Vector3 = -transform.basis.z
	dir_frente.y = 0.0
	if dir_frente.length_squared() < 0.01:
		dir_frente = Vector3.FORWARD
	else:
		dir_frente = dir_frente.normalized()

	global_transform.basis = Basis.looking_at(dir_frente, Vector3.UP)
	global_position.y += 0.8
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO

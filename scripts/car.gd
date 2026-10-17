extends VehicleBody3D
class_name RCCar

enum PowerUp { NONE, ROCKET, OIL }

@export_group("Potencia y Traccion")
@export var max_fuerza_motor: float = 480.0
@export var max_fuerza_freno: float = 24.0
@export var max_angulo_giro: float = 0.55
@export var velocidad_retorno_giro: float = 7.0
@export var masa_chasis: float = 38.0

@export_group("Giroscopio y Control")
@export var giroscopio_activo: bool = false
@export var sensibilidad_giro: float = 0.4
@export var zona_muerta_giro: float = 0.25

@export_group("Armas")
@export var rocket_scene: PackedScene = preload("res://scenes/Rocket.tscn")
@export var oil_scene: PackedScene = preload("res://scenes/OilSlick.tscn")

@onready var front_left_wheel: VehicleWheel3D = $WheelFrontLeft
@onready var front_right_wheel: VehicleWheel3D = $WheelFrontRight
@onready var rear_left_wheel: VehicleWheel3D = $WheelRearLeft
@onready var rear_right_wheel: VehicleWheel3D = $WheelRearRight
@onready var weapon_front: Marker3D = $WeaponFront
@onready var weapon_rear: Marker3D = $WeaponRear
@onready var drift_particles_left: GPUParticles3D = $WheelRearLeft/DriftSmoke
@onready var drift_particles_right: GPUParticles3D = $WheelRearRight/DriftSmoke

var sound_manager: Node = null
var current_powerup: PowerUp = PowerUp.NONE
var angulo_actual_giro: float = 0.0
var esta_patinando: bool = false
var tiempo_patinaje: float = 0.0
var derrapando: bool = false
var mirando_atras: bool = false
var velocidad_kmh: float = 0.0

func _ready() -> void:
	mass = masa_chasis
	center_of_mass_mode = RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
	center_of_mass = Vector3(0.0, -0.18, 0.0)
	sound_manager = get_node_or_null("/root/SoundManager")

func _physics_process(delta: float) -> void:
	velocidad_kmh = linear_velocity.length() * 3.6

	if sound_manager:
		sound_manager.actualizar_motor(clamp(linear_velocity.length() / 25.0, 0.0, 1.0))

	if esta_patinando:
		_procesar_trompo(delta)
		return

	_procesar_direccion(delta)
	_procesar_motor()
	_procesar_estabilidad_aire(delta)
	_procesar_efectos_derrape()
	_procesar_acciones()

func _procesar_direccion(delta: float) -> void:
	var dir_input: float = Input.get_axis("girar_der", "girar_izq")

	if giroscopio_activo:
		var sensor_accel = Input.get_accelerometer()
		var raw_tilt = -sensor_accel.y
		if abs(raw_tilt) > zona_muerta_giro:
			var filtrado = (raw_tilt - (sign(raw_tilt) * zona_muerta_giro)) * sensibilidad_giro
			if abs(dir_input) < 0.1:
				dir_input = clamp(filtrado, -1.0, 1.0)

	derrapando = Input.is_action_pressed("freno_mano")

	if derrapando:
		rear_left_wheel.wheel_friction_slip = 0.75
		rear_right_wheel.wheel_friction_slip = 0.75
		dir_input *= 1.35
	else:
		rear_left_wheel.wheel_friction_slip = 2.6
		rear_right_wheel.wheel_friction_slip = 2.6

	var objetivo: float = dir_input * max_angulo_giro
	angulo_actual_giro = lerp(angulo_actual_giro, objetivo, velocidad_retorno_giro * delta)
	steering = angulo_actual_giro

func _procesar_motor() -> void:
	var accel_input: float = Input.get_axis("frenar", "acelerar")
	var adelante_dot: float = linear_velocity.dot(-transform.basis.z)
	var turbo = 1.45 if Input.is_action_pressed("turbo_bocina") else 1.0

	if accel_input > 0.0:
		engine_force = accel_input * max_fuerza_motor * turbo
		brake = 0.0
	elif accel_input < 0.0:
		if adelante_dot > 0.6:
			engine_force = 0.0
			brake = max_fuerza_freno
		else:
			engine_force = accel_input * (max_fuerza_motor * 0.6)
			brake = 0.0
	else:
		engine_force = 0.0
		brake = 1.4

func _procesar_estabilidad_aire(delta: float) -> void:
	# Si las 4 ruedas están en el aire, permitir inclinación acrobática tipo RC
	if not front_left_wheel.is_in_contact() and not rear_left_wheel.is_in_contact():
		var pitch = Input.get_axis("frenar", "acelerar")
		var roll = Input.get_axis("girar_der", "girar_izq")
		apply_torque(transform.basis.x * pitch * 8.0 * delta)
		apply_torque(transform.basis.z * roll * 6.0 * delta)

func _procesar_efectos_derrape() -> void:
	var humo_activo = derrapando and rear_left_wheel.is_in_contact() and velocidad_kmh > 12.0
	if drift_particles_left:
		drift_particles_left.emitting = humo_activo
	if drift_particles_right:
		drift_particles_right.emitting = humo_activo

	if sound_manager:
		sound_manager.reproducir_derrape(humo_activo)

func _procesar_acciones() -> void:
	if Input.is_action_just_pressed("usar_item"):
		activar_arma()

	if Input.is_action_just_pressed("reset_auto"):
		voltear_coche()

	mirando_atras = Input.is_action_pressed("mirar_atras")

func activar_arma() -> void:
	match current_powerup:
		PowerUp.ROCKET:
			if rocket_scene and weapon_front:
				var cohete = rocket_scene.instantiate()
				get_tree().root.add_child(cohete)
				cohete.global_transform = weapon_front.global_transform
				cohete.disparar(-transform.basis.z, self)
				if sound_manager:
					sound_manager.reproducir_disparo()
			current_powerup = PowerUp.NONE
		PowerUp.OIL:
			if oil_scene and weapon_rear:
				var aceite = oil_scene.instantiate()
				get_tree().root.add_child(aceite)
				aceite.global_transform = weapon_rear.global_transform
			current_powerup = PowerUp.NONE

func recibir_arma(tipo: PowerUp) -> void:
	current_powerup = tipo
	if sound_manager:
		sound_manager.reproducir_pickup()

func pisar_aceite() -> void:
	if esta_patinando:
		return
	esta_patinando = true
	tiempo_patinaje = 1.4
	apply_torque_impulse(Vector3.UP * 85.0)

func _procesar_trompo(delta: float) -> void:
	tiempo_patinaje -= delta
	engine_force = 0.0
	brake = 0.8
	if tiempo_patinaje <= 0.0:
		esta_patinando = false
		angular_velocity = Vector3.ZERO

func recibir_impacto_cohete(pos_explosion: Vector3, fuerza: float) -> void:
	var dir = (global_position - pos_explosion).normalized()
	dir.y += 0.65
	apply_central_impulse(dir.normalized() * fuerza)
	pisar_aceite()
	if sound_manager:
		sound_manager.reproducir_explosion()

func voltear_coche() -> void:
	var dir_frente = -transform.basis.z
	dir_frente.y = 0.0
	dir_frente = dir_frente.normalized() if dir_frente.length_squared() > 0.01 else Vector3.FORWARD
	global_transform.basis = Basis.looking_at(dir_frente, Vector3.UP)
	global_position.y += 0.95
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO

func alternar_giroscopio() -> bool:
	giroscopio_activo = !giroscopio_activo
	return giroscopio_activo

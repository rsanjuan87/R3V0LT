import os
import zipfile

# Definición de todos los archivos del proyecto
archivos = {
    # 1. Configuración de Proyecto (Con controles W, A, S, D, Espacio y R ya pre-mapeados)
    "project.godot": """config_version=5

[application]

config/name="ReVolt RC Clone"
run/main_scene="res://scenes/MainTrack.tscn"
config/features=PackedStringArray("4.3", "Forward Plus")

[input]

acelerar={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":87,"physical_keycode":0,"key_label":0,"unicode":119,"echo":false,"script":null)
]
}
frenar={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":83,"physical_keycode":0,"key_label":0,"unicode":115,"echo":false,"script":null)
]
}
girar_izq={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":65,"physical_keycode":0,"key_label":0,"unicode":97,"echo":false,"script":null)
]
}
girar_der={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":68,"physical_keycode":0,"key_label":0,"unicode":100,"echo":false,"script":null)
]
}
usar_item={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":32,"echo":false,"script":null)
]
}
reset_auto={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":82,"physical_keycode":0,"key_label":0,"unicode":114,"echo":false,"script":null)
]
}
""",

    # 2. Presets de exportación para compilar en Linux y Windows
    "export_presets.cfg": """[preset.0]

name="Linux/X11"
platform="Linux/X11"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="./builds/linux/ReVoltRC.x86_64"

[preset.0.options]

binary_format/embed_pck=true

[preset.1]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="./builds/windows/ReVoltRC.exe"

[preset.1.options]

binary_format/embed_pck=true
""",

    # 3. Scripts
    "scripts/car.gd": """extends VehicleBody3D
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
""",

    "scripts/chase_camera.gd": """extends Camera3D

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
""",

    "scripts/item_box.gd": """extends Area3D

@export var tiempo_reaparicion: float = 5.0
@onready var visual_mesh: MeshInstance3D = $MeshInstance3D
@onready var colision: CollisionShape3D = $CollisionShape3D

var activa: bool = true

func _ready() -> void:
	body_entered.connect(_on_body_entered)

func _process(delta: float) -> void:
	if activa and visual_mesh:
		visual_mesh.rotate_y(3.5 * delta)
		visual_mesh.position.y = sin(Time.get_ticks_msec() * 0.004) * 0.1

func _on_body_entered(body: Node) -> void:
	if not activa:
		return
	if body is RCCar:
		var car = body as RCCar
		if car.current_powerup == RCCar.PowerUp.NONE:
			var item_asignado = RCCar.PowerUp.ROCKET if randf() > 0.5 else RCCar.PowerUp.OIL
			car.recibir_arma(item_asignado)
			desactivar()

func desactivar() -> void:
	activa = false
	visual_mesh.visible = false
	colision.set_deferred("disabled", true)
	await get_tree().create_timer(tiempo_reaparicion).timeout
	activa = true
	visual_mesh.visible = true
	colision.set_deferred("disabled", false)
""",

    "scripts/rocket.gd": """extends Area3D

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
""",

    "scripts/oil_slick.gd": """extends Area3D

func _ready() -> void:
	set_as_top_level(true)
	body_entered.connect(_on_body_entered)
	get_tree().create_timer(20.0).timeout.connect(queue_free)

func _on_body_entered(body: Node) -> void:
	if body is RCCar:
		body.pisar_aceite()
		queue_free()
""",

    "scripts/checkpoint.gd": """extends Area3D
class_name Checkpoint

@export var indice: int = 0
signal vehiculo_paso(car: RCCar, checkpoint_idx: int)

func _ready() -> void:
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node) -> void:
	if body is RCCar:
		vehiculo_paso.emit(body, indice)
""",

    "scripts/race_manager.gd": """extends Node

@export var total_vueltas: int = 3
@export var label_hud: Label

var checkpoints: Array[Checkpoint] = []
var siguiente_checkpoint: int = 0
var vuelta_actual: int = 1
var carrera_finalizada: bool = false

func _ready() -> void:
	for child in get_tree().get_nodes_in_group("checkpoints"):
		if child is Checkpoint:
			checkpoints.append(child)
			child.vehiculo_paso.connect(_on_checkpoint_cruzado)
	actualizar_hud()

func _on_checkpoint_cruzado(car: RCCar, idx: int) -> void:
	if carrera_finalizada:
		return

	if idx == siguiente_checkpoint:
		siguiente_checkpoint += 1
		if siguiente_checkpoint >= checkpoints.size():
			siguiente_checkpoint = 0
			vuelta_actual += 1
			if vuelta_actual > total_vueltas:
				carrera_finalizada = true
				if label_hud:
					label_hud.text = "¡CARRERA TERMINADA! GANASTE"
				return
		actualizar_hud()

func actualizar_hud() -> void:
	if label_hud and not carrera_finalizada:
		label_hud.text = "Vuelta: %d / %d\\nCheckpoint: %d / %d" % [vuelta_actual, total_vueltas, siguiente_checkpoint, checkpoints.size()]
""",

    # 4. Escenas (.tscn)
    "scenes/Car.tscn": """[gd_scene load_steps=8 format=3]

[ext_resource type="Script" path="res://scripts/car.gd" id="1_car"]

[sub_resource type="BoxShape3D" id="BoxShape3D_chasis"]
size = Vector3(0.65, 0.28, 1.25)

[sub_resource type="StandardMaterial3D" id="Mat_Car"]
albedo_color = Color(0.95, 0.15, 0.05, 1)
roughness = 0.3

[sub_resource type="BoxMesh" id="BoxMesh_visual"]
material = SubResource("Mat_Car")
size = Vector3(0.65, 0.25, 1.25)

[sub_resource type="StandardMaterial3D" id="Mat_Rueda"]
albedo_color = Color(0.1, 0.1, 0.1, 1)

[sub_resource type="CylinderMesh" id="CylinderMesh_rueda"]
material = SubResource("Mat_Rueda")
top_radius = 0.16
bottom_radius = 0.16
height = 0.12

[node name="Car" type="VehicleBody3D"]
mass = 45.0
script = ExtResource("1_car")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.18, 0)
shape = SubResource("BoxShape3D_chasis")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.18, 0)
mesh = SubResource("BoxMesh_visual")

[node name="WheelFrontLeft" type="VehicleWheel3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.38, 0.15, -0.42)
use_as_steering = true
wheel_roll_influence = 0.1
wheel_radius = 0.16
suspension_travel = 0.18
suspension_stiffness = 45.0
damping_compression = 2.0
damping_relaxation = 2.8

[node name="Mesh" type="MeshInstance3D" parent="WheelFrontLeft"]
transform = Transform3D(-4.37114e-08, -1, 0, 1, -4.37114e-08, 0, 0, 0, 1, 0, 0, 0)
mesh = SubResource("CylinderMesh_rueda")

[node name="WheelFrontRight" type="VehicleWheel3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -0.38, 0.15, -0.42)
use_as_steering = true
wheel_roll_influence = 0.1
wheel_radius = 0.16
suspension_travel = 0.18
suspension_stiffness = 45.0
damping_compression = 2.0
damping_relaxation = 2.8

[node name="Mesh" type="MeshInstance3D" parent="WheelFrontRight"]
transform = Transform3D(-4.37114e-08, -1, 0, 1, -4.37114e-08, 0, 0, 0, 1, 0, 0, 0)
mesh = SubResource("CylinderMesh_rueda")

[node name="WheelRearLeft" type="VehicleWheel3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.38, 0.15, 0.42)
use_as_traction = true
wheel_roll_influence = 0.1
wheel_radius = 0.16
suspension_travel = 0.18
suspension_stiffness = 45.0
damping_compression = 2.0
damping_relaxation = 2.8

[node name="Mesh" type="MeshInstance3D" parent="WheelRearLeft"]
transform = Transform3D(-4.37114e-08, -1, 0, 1, -4.37114e-08, 0, 0, 0, 1, 0, 0, 0)
mesh = SubResource("CylinderMesh_rueda")

[node name="WheelRearRight" type="VehicleWheel3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -0.38, 0.15, 0.42)
use_as_traction = true
wheel_roll_influence = 0.1
wheel_radius = 0.16
suspension_travel = 0.18
suspension_stiffness = 45.0
damping_compression = 2.0
damping_relaxation = 2.8

[node name="Mesh" type="MeshInstance3D" parent="WheelRearRight"]
transform = Transform3D(-4.37114e-08, -1, 0, 1, -4.37114e-08, 0, 0, 0, 1, 0, 0, 0)
mesh = SubResource("CylinderMesh_rueda")

[node name="WeaponFront" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.18, -0.8)

[node name="WeaponRear" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.05, 0.8)
""",

    "scenes/Rocket.tscn": """[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/rocket.gd" id="1_rocket"]

[sub_resource type="SphereShape3D" id="SphereShape3D_1"]
radius = 0.25

[sub_resource type="StandardMaterial3D" id="Mat_Rocket"]
albedo_color = Color(1, 0.7, 0, 1)
emission_enabled = true
emission = Color(1, 0.4, 0, 1)
emission_energy_multiplier = 3.0

[sub_resource type="CylinderMesh" id="CylinderMesh_1"]
material = SubResource("Mat_Rocket")
top_radius = 0.04
bottom_radius = 0.08
height = 0.4

[node name="Rocket" type="Area3D"]
script = ExtResource("1_rocket")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("SphereShape3D_1")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, -4.37114e-08, 1, 0, -1, -4.37114e-08, 0, 0, 0)
mesh = SubResource("CylinderMesh_1")
""",

    "scenes/OilSlick.tscn": """[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/oil_slick.gd" id="1_oil"]

[sub_resource type="CylinderShape3D" id="CylinderShape3D_1"]
height = 0.05
radius = 0.8

[sub_resource type="StandardMaterial3D" id="Mat_Oil"]
albedo_color = Color(0.05, 0.05, 0.05, 0.95)
roughness = 0.05

[sub_resource type="CylinderMesh" id="CylinderMesh_1"]
material = SubResource("Mat_Oil")
top_radius = 0.8
bottom_radius = 0.8
height = 0.02

[node name="OilSlick" type="Area3D"]
script = ExtResource("1_oil")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.025, 0)
shape = SubResource("CylinderShape3D_1")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.01, 0)
mesh = SubResource("CylinderMesh_1")
""",

    "scenes/ItemBox.tscn": """[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/item_box.gd" id="1_itembox"]

[sub_resource type="BoxShape3D" id="BoxShape3D_1"]
size = Vector3(0.6, 0.6, 0.6)

[sub_resource type="StandardMaterial3D" id="Mat_Box"]
albedo_color = Color(0.1, 0.8, 1, 0.8)
roughness = 0.1
emission_enabled = true
emission = Color(0, 0.5, 1, 1)

[sub_resource type="BoxMesh" id="BoxMesh_1"]
material = SubResource("Mat_Box")
size = Vector3(0.5, 0.5, 0.5)

[node name="ItemBox" type="Area3D"]
script = ExtResource("1_itembox")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.35, 0)
shape = SubResource("BoxShape3D_1")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.35, 0)
mesh = SubResource("BoxMesh_1")
""",

    "scenes/Checkpoint.tscn": """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/checkpoint.gd" id="1_check"]

[sub_resource type="BoxShape3D" id="BoxShape3D_gate"]
size = Vector3(10.0, 3.0, 1.0)

[node name="Checkpoint" type="Area3D" groups=["checkpoints"]]
script = ExtResource("1_check")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
shape = SubResource("BoxShape3D_gate")
""",

    "scenes/MainTrack.tscn": """[gd_scene load_steps=15 format=3]

[ext_resource type="PackedScene" path="res://scenes/Car.tscn" id="1_car"]
[ext_resource type="Script" path="res://scripts/chase_camera.gd" id="2_cam"]
[ext_resource type="PackedScene" path="res://scenes/ItemBox.tscn" id="3_box"]
[ext_resource type="PackedScene" path="res://scenes/Checkpoint.tscn" id="4_cp"]
[ext_resource type="Script" path="res://scripts/race_manager.gd" id="5_rm"]

[sub_resource type="ProceduralSkyMaterial" id="SkyMat_1"]
sky_top_color = Color(0.35, 0.65, 0.95, 1)

[sub_resource type="Sky" id="Sky_1"]
sky_material = SubResource("SkyMat_1")

[sub_resource type="Environment" id="Env_1"]
background_mode = 2
sky = SubResource("Sky_1")
tonemap_mode = 2

[sub_resource type="BoxShape3D" id="BoxShape3D_suelo"]
size = Vector3(120, 1, 120)

[sub_resource type="StandardMaterial3D" id="Mat_Suelo"]
albedo_color = Color(0.25, 0.28, 0.3, 1)

[sub_resource type="BoxMesh" id="BoxMesh_suelo"]
material = SubResource("Mat_Suelo")
size = Vector3(120, 1, 120)

[sub_resource type="CylinderShape3D" id="CylinderShape3D_lata"]
height = 0.5
radius = 0.18

[sub_resource type="StandardMaterial3D" id="Mat_Lata"]
albedo_color = Color(0.9, 0.8, 0.1, 1)

[sub_resource type="CylinderMesh" id="CylinderMesh_lata"]
material = SubResource("Mat_Lata")
top_radius = 0.18
bottom_radius = 0.18
height = 0.5

[node name="MainTrack" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Env_1")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866, -0.353, 0.353, 0, 0.707, 0.707, -0.5, -0.612, 0.612, 0, 20, 0)
shadow_enabled = true

[node name="PistaSuelo" type="StaticBody3D" parent="."]

[node name="CollisionShape3D" type="CollisionShape3D" parent="PistaSuelo"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -0.5, 0)
shape = SubResource("BoxShape3D_suelo")

[node name="MeshInstance3D" type="MeshInstance3D" parent="PistaSuelo"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -0.5, 0)
mesh = SubResource("BoxMesh_suelo")

[node name="Car" parent="." instance=ExtResource("1_car")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.2, 0)

[node name="ChaseCamera" type="Camera3D" parent="." node_paths=PackedStringArray("objetivo")]
transform = Transform3D(1, 0, 0, 0, 0.965926, 0.258819, 0, -0.258819, 0.965926, 0, 1.2, 2.5)
script = ExtResource("2_cam")
objetivo = NodePath("../Car")

[node name="Checkpoints" type="Node3D" parent="."]

[node name="CP0_Meta" parent="Checkpoints" instance=ExtResource("4_cp")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, -5)

[node name="CP1" parent="Checkpoints" instance=ExtResource("4_cp")]
transform = Transform3D(-4.37114e-08, 0, 1, 0, 1, 0, -1, 0, -4.37114e-08, 20, 0, -25)
indice = 1

[node name="CP2" parent="Checkpoints" instance=ExtResource("4_cp")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, -45)
indice = 2

[node name="ItemBoxes" type="Node3D" parent="."]

[node name="ItemBox1" parent="ItemBoxes" instance=ExtResource("3_box")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, -15)

[node name="ItemBox2" parent="ItemBoxes" instance=ExtResource("3_box")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 15, 0, -25)

[node name="ObstaculosLata" type="Node3D" parent="."]

[node name="Lata1" type="RigidBody3D" parent="ObstaculosLata"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.8, 0.3, -10)
mass = 0.25

[node name="Collision" type="CollisionShape3D" parent="ObstaculosLata/Lata1"]
shape = SubResource("CylinderShape3D_lata")

[node name="Mesh" type="MeshInstance3D" parent="ObstaculosLata/Lata1"]
mesh = SubResource("CylinderMesh_lata")

[node name="Lata2" type="RigidBody3D" parent="ObstaculosLata"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -0.6, 0.3, -10.2)
mass = 0.25

[node name="Collision" type="CollisionShape3D" parent="ObstaculosLata/Lata2"]
shape = SubResource("CylinderShape3D_lata")

[node name="Mesh" type="MeshInstance3D" parent="ObstaculosLata/Lata2"]
mesh = SubResource("CylinderMesh_lata")

[node name="RaceManager" type="Node" parent="." node_paths=PackedStringArray("label_hud")]
script = ExtResource("5_rm")
label_hud = NodePath("../HUD/MarginContainer/Label")

[node name="HUD" type="CanvasLayer" parent="."]

[node name="MarginContainer" type="MarginContainer" parent="HUD"]
offset_right = 260.0
offset_bottom = 80.0
theme_override_constants/margin_left = 20
theme_override_constants/margin_top = 20

[node name="Label" type="Label" parent="HUD/MarginContainer"]
layout_mode = 2
theme_override_font_sizes/font_size = 22
text = "Vuelta: 1 / 3"
""",

    # 5. Pipeline de CI/CD para GitHub Actions
    ".github/workflows/export.yml": """name: "Compilar y Exportar ReVolt Godot 4"

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  export-game:
    name: Exportar Juego
    runs-on: ubuntu-latest
    container:
      image: barichello/godot-ci:4.3
    steps:
      - name: Descargar repositorio (Checkout)
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Configurar plantillas de exportacion
        run: |
          mkdir -v -p ~/.local/share/godot/export_templates
          mv /root/.local/share/godot/export_templates/* ~/.local/share/godot/export_templates/ 2>/dev/null || true

      - name: Crear directorios de salida
        run: |
          mkdir -v -p builds/windows
          mkdir -v -p builds/linux

      - name: Compilar para Linux
        run: godot --headless --verbose --export-release "Linux/X11" ./builds/linux/ReVoltRC.x86_64

      - name: Compilar para Windows (.exe)
        run: godot --headless --verbose --export-release "Windows Desktop" ./builds/windows/ReVoltRC.exe

      - name: Subir artefacto compilado para Windows
        uses: actions/upload-artifact@v4
        with:
          name: ReVoltRC-Windows
          path: ./builds/windows/

      - name: Subir artefacto compilado para Linux
        uses: actions/upload-artifact@v4
        with:
          name: ReVoltRC-Linux
          path: ./builds/linux/
"""
}

# Crear carpetas, escribir archivos y comprimir a .zip
zip_filename = "revolt_godot4.zip"

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for ruta, contenido in archivos.items():
        directorio = os.path.dirname(ruta)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
        
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
            
        zip_file.write(ruta)
        print(f"-> Escrito y empaquetado: {ruta}")

print(f"\n¡Éxito! Archivo '{zip_filename}' creado con todos los archivos listos.")
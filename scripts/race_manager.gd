extends Node

@export var total_vueltas: int = 3
@export var player_car: RCCar
@export var ai_car: AICar
@export var label_lap: Label
@export var label_speed: Label
@export var label_time: Label
@export var label_position: Label

var checkpoints: Array[Checkpoint] = []
var siguiente_cp_player: int = 0
var vuelta_player: int = 1
var tiempo_carrera: float = 0.0
var mejor_tiempo: float = 9999.0
var finalizado: bool = false

func _ready() -> void:
	for child in get_tree().get_nodes_in_group("checkpoints"):
		if child is Checkpoint:
			checkpoints.append(child)
			child.vehiculo_paso.connect(_on_checkpoint_cruzado)

func _process(delta: float) -> void:
	if not finalizado:
		tiempo_carrera += delta
		_actualizar_hud()

func _on_checkpoint_cruzado(car: RCCar, idx: int) -> void:
	if finalizado:
		return

	if idx == siguiente_cp_player:
		siguiente_cp_player += 1
		if siguiente_cp_player >= checkpoints.size():
			siguiente_cp_player = 0
			vuelta_player += 1
			if vuelta_player > total_vueltas:
				finalizado = true
				if label_position:
					label_position.text = "¡1º PUESTO! - VICTORIA"
					label_position.modulate = Color(1.0, 0.84, 0.0)

func _actualizar_hud() -> void:
	if label_lap:
		label_lap.text = "VUELTA: %d / %d" % [min(vuelta_player, total_vueltas), total_vueltas]
	if label_speed and player_car:
		label_speed.text = "%03d KM/H" % int(player_car.velocidad_kmh)
	if label_time:
		var mins = int(tiempo_carrera / 60.0)
		var secs = fmod(tiempo_carrera, 60.0)
		label_time.text = "TIEMPO: %02d:%05.2f" % [mins, secs]
	if label_position and not finalizado:
		var pos_str = "POS: 1º / 2"
		if ai_car and player_car:
			if ai_car.global_position.distance_to(checkpoints[siguiente_cp_player].global_position) < player_car.global_position.distance_to(checkpoints[siguiente_cp_player].global_position):
				pos_str = "POS: 2º / 2"
		label_position.text = pos_str

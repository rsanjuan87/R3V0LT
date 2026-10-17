extends Node

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
		label_hud.text = "Vuelta: %d / %d\nCheckpoint: %d / %d" % [vuelta_actual, total_vueltas, siguiente_checkpoint, checkpoints.size()]

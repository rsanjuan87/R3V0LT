extends Area3D
class_name Checkpoint

@export var indice: int = 0
signal vehiculo_paso(car: RCCar, checkpoint_idx: int)

func _ready() -> void:
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node) -> void:
	if body is RCCar:
		vehiculo_paso.emit(body, indice)

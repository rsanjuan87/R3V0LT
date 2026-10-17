extends Area3D

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

extends CanvasLayer

@export var car: RCCar

@onready var btn_left: Control = $LeftPanel/BtnLeft
@onready var btn_right: Control = $LeftPanel/BtnRight
@onready var btn_gas: Control = $RightPanel/BtnGas
@onready var btn_brake: Control = $RightPanel/BtnBrake
@onready var btn_item: Control = $TopRightPanel/BtnItem
@onready var btn_reset: Control = $TopLeftPanel/BtnReset
@onready var btn_gyro: Button = $TopLeftPanel/BtnGyro

var toques_activos: Dictionary = {}

func _ready() -> void:
	btn_gyro.pressed.connect(_on_gyro_pressed)
	_actualizar_boton_giroscopio(false)

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			_evaluar_toque(event.index, event.position)
		else:
			_liberar_toque(event.index)
	elif event is InputEventScreenDrag:
		_evaluar_toque(event.index, event.position)

func _evaluar_toque(index: int, pos: Vector2) -> void:
	var accion_detectada: String = ""

	if btn_gas.get_global_rect().has_point(pos):
		accion_detectada = "acelerar"
	elif btn_brake.get_global_rect().has_point(pos):
		accion_detectada = "frenar"
	elif btn_left.get_global_rect().has_point(pos):
		accion_detectada = "girar_izq"
	elif btn_right.get_global_rect().has_point(pos):
		accion_detectada = "girar_der"
	elif btn_item.get_global_rect().has_point(pos):
		accion_detectada = "usar_item"
	elif btn_reset.get_global_rect().has_point(pos):
		accion_detectada = "reset_auto"

	if toques_activos.has(index):
		var accion_antigua = toques_activos[index]
		if accion_antigua != accion_detectada:
			Input.action_release(accion_antigua)
			toques_activos.erase(index)

	if accion_detectada != "":
		toques_activos[index] = accion_detectada
		Input.action_press(accion_detectada)

func _liberar_toque(index: int) -> void:
	if toques_activos.has(index):
		var accion = toques_activos[index]
		Input.action_release(accion)
		toques_activos.erase(index)

func _on_gyro_pressed() -> void:
	if car:
		var estado = car.alternar_giroscopio()
		_actualizar_boton_giroscopio(estado)
		$LeftPanel.visible = !estado

func _actualizar_boton_giroscopio(activo: bool) -> void:
	if activo:
		btn_gyro.text = "GIROSCOPIO: ON"
		btn_gyro.modulate = Color(0.2, 1.0, 0.3)
	else:
		btn_gyro.text = "GIROSCOPIO: OFF"
		btn_gyro.modulate = Color(1.0, 1.0, 1.0)

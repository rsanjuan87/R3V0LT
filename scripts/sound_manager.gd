extends Node

# Sintetizador procedural que crea efectos de sonido WAV en memoria
var sfx_motor: AudioStreamPlayer
var sfx_skid: AudioStreamPlayer
var sfx_shoot: AudioStreamPlayer
var sfx_boom: AudioStreamPlayer
var sfx_pickup: AudioStreamPlayer

func _ready() -> void:
	sfx_motor = _crear_reproductor(_generar_tono_motor())
	sfx_skid = _crear_reproductor(_generar_ruido_derrape())
	sfx_shoot = _crear_reproductor(_generar_disparo())
	sfx_boom = _crear_reproductor(_generar_explosion())
	sfx_pickup = _crear_reproductor(_generar_pickup())

	sfx_motor.volume_db = -12.0
	sfx_motor.play()

func _crear_reproductor(stream: AudioStream) -> AudioStreamPlayer:
	var player = AudioStreamPlayer.new()
	player.stream = stream
	add_child(player)
	return player

func actualizar_motor(velocidad_relativa: float) -> void:
	if sfx_motor:
		sfx_motor.pitch_scale = clamp(0.7 + (velocidad_relativa * 1.8), 0.6, 2.5)

func reproducir_derrape(activo: bool) -> void:
	if activo and not sfx_skid.playing:
		sfx_skid.volume_db = -8.0
		sfx_skid.play()
	elif not activo and sfx_skid.playing:
		sfx_skid.stop()

func reproducir_disparo() -> void:
	sfx_shoot.stop()
	sfx_shoot.play()

func reproducir_explosion() -> void:
	sfx_boom.stop()
	sfx_boom.play()

func reproducir_pickup() -> void:
	sfx_pickup.stop()
	sfx_pickup.play()

func _generar_tono_motor() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	var sample_count = 2205
	var bytes = PackedByteArray()
	bytes.resize(sample_count * 2)
	for i in range(sample_count):
		var phase = float(i) / float(sample_count)
		var val = int((sin(phase * TAU * 12.0) + (sin(phase * TAU * 24.0) * 0.4)) * 12000.0)
		bytes.encode_s16(i * 2, val)
	wav.data = bytes
	return wav

func _generar_ruido_derrape() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	var sample_count = 4410
	var bytes = PackedByteArray()
	bytes.resize(sample_count * 2)
	var prev = 0.0
	for i in range(sample_count):
		var white = (randf() * 2.0 - 1.0)
		prev = lerp(prev, white, 0.25)
		var val = int(prev * 14000.0)
		bytes.encode_s16(i * 2, val)
	wav.data = bytes
	return wav

func _generar_disparo() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var sample_count = 5512
	var bytes = PackedByteArray()
	bytes.resize(sample_count * 2)
	for i in range(sample_count):
		var t = float(i) / 22050.0
		var freq = lerp(880.0, 220.0, float(i) / float(sample_count))
		var envelope = 1.0 - (float(i) / float(sample_count))
		var val = int(sin(t * freq * TAU) * envelope * 22000.0)
		bytes.encode_s16(i * 2, val)
	wav.data = bytes
	return wav

func _generar_explosion() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var sample_count = 8820
	var bytes = PackedByteArray()
	bytes.resize(sample_count * 2)
	var noise = 0.0
	for i in range(sample_count):
		var env = pow(1.0 - (float(i) / float(sample_count)), 2.0)
		noise = lerp(noise, (randf() * 2.0 - 1.0), 0.15)
		var val = int(noise * env * 28000.0)
		bytes.encode_s16(i * 2, val)
	wav.data = bytes
	return wav

func _generar_pickup() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var sample_count = 6615
	var bytes = PackedByteArray()
	bytes.resize(sample_count * 2)
	for i in range(sample_count):
		var t = float(i) / 22050.0
		var freq = 587.33 if i < 3300 else 880.0
		var env = 1.0 - (float(i % 3300) / 3300.0)
		var val = int(sin(t * freq * TAU) * env * 20000.0)
		bytes.encode_s16(i * 2, val)
	wav.data = bytes
	return wav

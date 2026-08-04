extends Node

## Headless gameplay/audio MVP: use the Output panel for status feedback.
## D-pad Down: instrument selection. D-pad Up: return to playing.
## In play mode: L1, L2, R1, R2, R3 play C, E, G, A, D respectively.

enum Mode { PLAY, INSTRUMENT_SELECT }

const NOTES := {
	"note_c": "C4",
	"note_e": "E4",
	"note_g": "G4",
	"note_a": "A4",
	"note_d": "D4",
}

const INSTRUMENTS := {
	"note_c": "piano",
	"note_e": "harp",
	"note_g": "violin",
	"note_a": "xylophone",
}

const TRIGGER_PRESS_THRESHOLD := 0.35
const MAX_ACTIVE_VOICES := 3

var mode: Mode = Mode.PLAY
var selected_instrument := "piano"
var stream_cache: Dictionary = {}
var voice_pool: Array[AudioStreamPlayer] = []
var active_voices: Array[AudioStreamPlayer] = []
var trigger_pressed := {
	JOY_AXIS_TRIGGER_LEFT: false,
	JOY_AXIS_TRIGGER_RIGHT: false,
}
var trigger_idle := {}


func _ready() -> void:
	remove_trigger_button("note_e", 13)
	remove_trigger_button("note_a", 14)
	for instrument: String in INSTRUMENTS.values():
		var first_note := NOTES.values()[0] as String
		if stream_cache.has("%s_%s" % [instrument, first_note]):
			continue
		for note: String in NOTES.values():
			var path := "res://sounds/%s_%s.wav" % [instrument, note]
			stream_cache["%s_%s" % [instrument, note]] = load(path) as AudioStream
	for slot in MAX_ACTIVE_VOICES:
		var player := AudioStreamPlayer.new()
		player.name = "Voice_%d" % (slot + 1)
		add_child(player)
		voice_pool.append(player)
	var connected_devices := Input.get_connected_joypads()
	if connected_devices.is_empty():
		push_warning("Kein Gamepad erkannt. Controller verbinden und das Spiel neu starten.")
	else:
		for device: int in connected_devices:
			print("Gamepad erkannt: %s (Gerät %d)" % [Input.get_joy_name(device), device])
			trigger_idle[JOY_AXIS_TRIGGER_LEFT] = Input.get_joy_axis(device, JOY_AXIS_TRIGGER_LEFT)
			trigger_idle[JOY_AXIS_TRIGGER_RIGHT] = Input.get_joy_axis(device, JOY_AXIS_TRIGGER_RIGHT)
	print("Instrument MVP bereit. Aktives Instrument: %s" % instrument_label())
	print("D-Pad Down: Auswahl | D-Pad Up: Spielen")
	print("Spielmodus: L1=C4 | L2=E4 | R1=G4 | R2=A4 | R3=D4")


func _input(event: InputEvent) -> void:
	if event is InputEventJoypadButton and event.pressed:
		print("RAW Gamepad: Gerät %d, Button %d" % [event.device, event.button_index])


func _process(_delta: float) -> void:
	for device: int in Input.get_connected_joypads():
		process_trigger_axis(device, JOY_AXIS_TRIGGER_LEFT)
		process_trigger_axis(device, JOY_AXIS_TRIGGER_RIGHT)


func process_trigger_axis(device: int, axis: JoyAxis) -> void:
	var value := Input.get_joy_axis(device, axis)
	var idle: float = trigger_idle.get(axis, 0.0)
	# Some drivers idle at -1 and others at 0. Normalize both to 0..1.
	var level := clampf((value - idle) / (1.0 - idle), 0.0, 1.0) if idle < -0.5 else clampf(value, 0.0, 1.0)
	var is_pressed := level >= TRIGGER_PRESS_THRESHOLD
	var was_pressed: bool = trigger_pressed[axis]
	if is_pressed == was_pressed:
		return
	trigger_pressed[axis] = is_pressed
	var label := "LT" if axis == JOY_AXIS_TRIGGER_LEFT else "RT"
	get_window().title = "Harpeace | Trigger %s: %s" % [label, "gedrückt" if is_pressed else "losgelassen"]
	print("Trigger %s: %s" % [label, "PRESSED" if is_pressed else "RELEASED"])
	if is_pressed:
		process_note_action("note_e" if axis == JOY_AXIS_TRIGGER_LEFT else "note_a")


func remove_trigger_button(action: String, button: int) -> void:
	for input_event: InputEvent in InputMap.action_get_events(action):
		if input_event is InputEventJoypadButton and input_event.button_index == button:
			InputMap.action_erase_event(action, input_event)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("instrument_mode"):
		mode = Mode.INSTRUMENT_SELECT
		print("INSTRUMENT-AUSWAHL: L1 Piano | L2 Harfe | R1 Violine | R2 Xylophon")
		get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("play_mode"):
		mode = Mode.PLAY
		print("SPIELMODUS: %s" % instrument_label())
		get_viewport().set_input_as_handled()
		return

	for action: String in NOTES:
		if event.is_action_pressed(action) and not event.is_echo():
			process_note_action(action)
			get_viewport().set_input_as_handled()
			return


func process_note_action(action: String) -> void:
	if mode == Mode.PLAY:
		play_note(NOTES[action])
	elif INSTRUMENTS.has(action):
		selected_instrument = INSTRUMENTS[action]
		preview_instrument()


func play_note(note: String) -> void:
	var key := "%s_%s" % [selected_instrument, note]
	var stream := stream_cache.get(key) as AudioStream
	if stream == null:
		push_warning("Sound fehlt: %s_%s.wav. Starte audio_generator/generate_sounds.py." % [selected_instrument, note])
		return
	var player := acquire_voice()
	player.stop()
	player.stream = stream
	player.volume_db = 0.0
	player.play()
	active_voices.append(player)
	print("%s: %s" % [instrument_label(), note])


func acquire_voice() -> AudioStreamPlayer:
	for index in range(active_voices.size() - 1, -1, -1):
		if not active_voices[index].is_playing():
			active_voices.remove_at(index)
	if active_voices.size() >= MAX_ACTIVE_VOICES:
		return active_voices.pop_front()
	for player: AudioStreamPlayer in voice_pool:
		if not player.is_playing():
			return player
	# Safety fallback: this should only be reached if a driver reports stale state.
	return active_voices.pop_front()


func preview_instrument() -> void:
	print("Ausgewählt: %s (Vorschau C4)" % instrument_label())
	play_note("C4")


func instrument_label() -> String:
	return selected_instrument.replace("_", " ").capitalize()

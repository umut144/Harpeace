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

var mode: Mode = Mode.PLAY
var selected_instrument := "harp"
var players: Dictionary = {}


func _ready() -> void:
	for note: String in NOTES.values():
		var player := AudioStreamPlayer.new()
		player.name = "Player_%s" % note
		add_child(player)
		players[note] = player
	print("Instrument MVP bereit. Aktives Instrument: %s" % selected_instrument.capitalize())
	print("D-Pad Down: Auswahl | D-Pad Up: Spielen")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("instrument_mode"):
		mode = Mode.INSTRUMENT_SELECT
		print("INSTRUMENT-AUSWAHL: L1 Piano | L2 Harfe | R1 Violine | R2 Xylophon")
		get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("play_mode"):
		mode = Mode.PLAY
		print("SPIELMODUS: %s" % selected_instrument.capitalize())
		get_viewport().set_input_as_handled()
		return

	for action: String in NOTES:
		if event.is_action_pressed(action) and not event.is_echo():
			if mode == Mode.PLAY:
				play_note(NOTES[action])
			elif INSTRUMENTS.has(action):
				selected_instrument = INSTRUMENTS[action]
				preview_instrument()
			get_viewport().set_input_as_handled()
			return


func play_note(note: String) -> void:
	var path := "res://sounds/%s_%s.wav" % [selected_instrument, note]
	var stream := load(path) as AudioStream
	if stream == null:
		push_warning("Sound fehlt: %s. Starte audio_generator/generate_sounds.py." % path)
		return
	var player := players[note] as AudioStreamPlayer
	player.stream = stream
	player.play()
	print("%s: %s" % [selected_instrument.capitalize(), note])


func preview_instrument() -> void:
	print("Ausgewählt: %s (Vorschau C4)" % selected_instrument.capitalize())
	play_note("C4")

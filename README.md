# Harpeace — Gamepad Instrument MVP

This repository contains one Godot project and a small standard-library Python audio generator.

## First run

1. Generate the audio files from the repository root:

   ```sh
   python3 audio_generator/generate_sounds.py
   ```

2. Import and open this folder in Godot, then run `Main.tscn`.
3. Use the Godot **Output** panel for mode and note feedback.

## Controller mapping

| Input | Play mode | Instrument-selection mode |
| --- | --- | --- |
| L1 | C4 | Piano |
| L2 | E4 | Harp |
| R1 | G4 | Violin |
| R2 | A4 | Xylophone |
| R3 | D4 | — |
| D-pad Down | Enter selection mode | Enter selection mode |
| D-pad Up | Return to play mode | Confirm and return to play mode |

The generated sounds are intentionally synthetic placeholders. They are useful for testing input, timing, the scale, and the instrument-mode flow before final audio assets are chosen.

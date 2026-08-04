# Gamepad instrument MVP

## Scope

Harpeace is a Godot gamepad-controlled instrument prototype for a future Bard
character. It uses five notes from C major pentatonic:

```text
C4, E4, G4, A4, D4
```

The note order deliberately puts the more colour-like D4 on the fifth button.
The four primary buttons alone produce a stable musical subset.

## Controls

| Input | Play mode | Instrument selection |
| --- | --- | --- |
| L1 | C4 | Piano |
| LT/L2 | E4 | Harp |
| RB/R1 | G4 | Violin |
| RT/R2 | A4 | Xylophone |
| R3 | D4 | — |
| D-pad Down | Enter selection | — |
| D-pad Up | Return to play mode | Confirm selection and return |

Xbox LT/RT are reported by macOS/Godot as axes, not digital buttons. `main.gd`
therefore polls each trigger, normalizes its rest value, and emits one note on
the threshold crossing. Holding a trigger does not retrigger it.

## Runtime audio architecture

`main.gd` uses a shared three-voice FIFO pool:

```text
first note  -> Voice_1
second note -> Voice_2
third note  -> Voice_3
fourth note -> stop oldest voice, reuse it for the new note
```

The pool is global across all instruments and is intentionally limited to three
simultaneous sounds. This was the first configuration that remained clean in
manual tests with the current generated samples.

Do not replace this with `AudioStreamPolyphonic` without re-running the audio
foundation tests. Its capacity handling rejected new voices when full, which is
not the desired Bard interaction.

## Asset layout

Each approved instrument lives in its own folder:

```text
sounds/foundation_piano/
sounds/foundation_harp/
sounds/foundation_violin/
sounds/foundation_xylophone/
```

Every folder must contain exactly one WAV per note, named
`<instrument>_<note>.wav`, for example `harp_C4.wav`.

`main.gd` loads these paths at startup. If a path or import is missing, Godot
prints a warning instead of playing a fallback sound.

## Adding or revising an instrument

1. Add a dedicated generator under `audio_generator/generate_foundation_*.py`.
2. Generate mono 44.1 kHz, 16-bit PCM source WAVs with peak `0.25` and 10 ms
   fades.
3. Put its five files in `sounds/foundation_<instrument>/`.
4. In Godot, import the new WAVs as PCM/Uncompressed, with loop, normalize,
   trim and force-8-bit disabled.
5. Test it alone through the three-voice pool before adding it to `INSTRUMENTS`.
6. Test three rapid notes, same-note retriggering, and instrument switching.

Keep the Python source and regenerated WAV outputs together in the same commit.

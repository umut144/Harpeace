# Audio foundation reset

This branch rebuilds audio in controlled stages. Do not change multiple stages
at once: every stage answers one question about the signal path.

## Rules for every test sample

- Mono, 44.1 kHz, 16-bit PCM WAV source file.
- Peak at or below `0.25` (-12 dBFS) for reference tests.
- 10 ms fade-in and fade-out; no loop.
- One dedicated WAV file per playable note; never use pitch scaling for this test.
- In Godot's **Import** dock, set `Compress > Mode` to **PCM (Uncompressed)**,
  `Force > 8 Bit` off, `Edit > Normalize` off, `Edit > Trim` off, and loop
  mode disabled. Click **Reimport** after changing options.

Godot 4.7's default WAV import uses lossy QOA compression. It is fine for many
assets, but the foundation tests deliberately use PCM to rule out import
artifacts.

## Stage 1 — reference sine samples

Generate five clean tones:

```sh
python3 audio_generator/generate_reference_sines.py
```

The output appears in `sounds/reference_sine/`. First verify that each file
sounds clean outside Godot. Then import them using the settings above.

## Stage 2 — one voice

Play only one reference sine through one plain `AudioStreamPlayer`. There must
be no pitch shift, bus effect, limiter, compressor, reverb, or looping.

## Stage 3 — controlled polyphony

Use the same reference samples and increase voices from 1 to 2, then 3, then 5.
At each level, test a repeated note and different notes. If a problem appears,
stop there: the audio architecture is the cause, not the instrument sound.

## Stage 4 — replace one instrument at a time

Replace the sine samples with one instrument family, starting with piano.
Keep the same headroom and import settings. Only introduce effects after the
dry multi-voice test is clean.

The first foundation instrument set is generated with:

```sh
python3 audio_generator/generate_foundation_piano.py
```

It writes to `sounds/foundation_piano/`. Select those five WAV files in Godot,
apply the same PCM import settings, and click **Reimport** before running the
Phase 4 test.

The approved foundation sets are stored under `sounds/foundation_piano/`,
`sounds/foundation_harp/`, `sounds/foundation_violin/`, and
`sounds/foundation_xylophone/`. Once each set passes the isolated test, the MVP
uses the same two-voice pool and restores D-pad instrument selection.

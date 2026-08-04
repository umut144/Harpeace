# Audio foundation

This is the approved audio baseline for the gamepad instrument MVP. It was
validated with piano, harp, violin, and xylophone. When investigating a new
audio issue, change only one layer at a time: source generation, Godot import,
or playback architecture.

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

## Generate the samples

Generate five clean tones:

```sh
python3 audio_generator/generate_reference_sines.py
```

The output appears in `sounds/reference_sine/`. These files are intentionally
plain diagnostic assets: if they do not play cleanly, do not tune an instrument
yet—inspect the Godot import and playback path first.

The production MVP uses one generator per instrument:

```sh
python3 audio_generator/generate_foundation_piano.py
python3 audio_generator/generate_foundation_harp.py
python3 audio_generator/generate_foundation_violin.py
python3 audio_generator/generate_foundation_xylophone.py
```

Each script writes five WAV files (`C4`, `D4`, `E4`, `G4`, `A4`) into its
matching `sounds/foundation_<instrument>/` directory. Preserve those paths: the
runtime builds its asset paths from the instrument and note names.

The scripts deliberately generate mono 44.1 kHz / 16-bit PCM files, limit the
source peak to `0.25`, and apply short edge fades. The headroom prevents normal
two-note sums from clipping; the fades prevent clicks when a voice is replaced.

## Godot import

For every newly generated WAV, select it in Godot and apply the settings in
“Rules for every test sample”, then click **Reimport**. The `.wav.import` files
for the foundation sets are kept in version control so these choices are shared.

Do not add a limiter, compressor, reverb, pitch scaling, or looping while
validating dry source audio. In this MVP, the Master bus is deliberately dry.

## Playback architecture

`main.gd` creates a global pool of two plain `AudioStreamPlayer` nodes. Notes
are assigned FIFO:

1. the first two notes use the two free players;
2. a third note stops and reuses the oldest currently playing voice;
3. finished voices are removed from the active queue before the next note.

This gives immediate input response and a hard, deterministic two-voice cap.
It is intentional that it is not `AudioStreamPolyphonic`: the earlier
polyphonic test refused new voices once its limit was occupied, rather than
using the desired oldest-voice replacement behaviour.

## Safe tuning workflow

1. Regenerate exactly one instrument family.
2. Reimport only its five WAV files as PCM in Godot.
3. Test one note, two overlapping notes, and a fast third note.
4. Only then change its synthesis parameters or the voice limit.

If distortion returns, first replay `sounds/reference_sine/`. Clean sine tones
point to the generated instrument or its import settings; distorted sine tones
point to the Godot playback/mix path. Do not try to hide either problem with a
limiter before finding its source.

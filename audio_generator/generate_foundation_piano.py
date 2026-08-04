"""Generate the first instrument set for the audio-foundation branch.

The tone model is the existing procedural piano, but the final files obey the
foundation rules: 44.1 kHz mono PCM WAV, -12 dBFS peak and 10 ms safety fades.
Run from the repository root:
    python3 audio_generator/generate_foundation_piano.py
"""

from __future__ import annotations

from pathlib import Path

from generate_sounds import NOTES, SAMPLE_RATE, normalise, piano, stable_seed, write_wav

PEAK = 0.25
FADE_SECONDS = 0.01
OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "sounds" / "foundation_piano"


def apply_safety_fades(samples: list[float]) -> list[float]:
    result = samples.copy()
    fade_samples = int(SAMPLE_RATE * FADE_SECONDS)
    for index in range(fade_samples):
        ratio = index / fade_samples
        result[index] *= ratio
        result[-(index + 1)] *= ratio
    return result


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for note, frequency in NOTES.items():
        samples = piano(frequency, stable_seed("foundation_piano", note))
        samples = apply_safety_fades(samples)
        path = OUTPUT_DIRECTORY / f"piano_{note}.wav"
        # write_wav normalises once, after all synthesis and fades are applied.
        write_wav(path, samples, target_peak=PEAK)
        print(f"created {path.relative_to(OUTPUT_DIRECTORY.parent.parent)}")


if __name__ == "__main__":
    main()

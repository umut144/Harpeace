"""Generate the second controlled instrument set: a foundation harp.

Run from the repository root:
    python3 audio_generator/generate_foundation_harp.py
"""

from __future__ import annotations

from pathlib import Path

from generate_foundation_piano import PEAK, apply_safety_fades
from generate_sounds import NOTES, harp, stable_seed, write_wav

OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "sounds" / "foundation_harp"


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for note, frequency in NOTES.items():
        samples = harp(frequency, stable_seed("foundation_harp", note))
        path = OUTPUT_DIRECTORY / f"harp_{note}.wav"
        write_wav(path, apply_safety_fades(samples), target_peak=PEAK)
        print(f"created {path.relative_to(OUTPUT_DIRECTORY.parent.parent)}")


if __name__ == "__main__":
    main()

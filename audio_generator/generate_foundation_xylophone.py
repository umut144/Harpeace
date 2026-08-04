"""Generate controlled xylophone samples for the audio-foundation branch."""

from __future__ import annotations

from pathlib import Path

from generate_foundation_piano import PEAK, apply_safety_fades
from generate_sounds import NOTES, write_wav, xylophone

OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "sounds" / "foundation_xylophone"


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for note, frequency in NOTES.items():
        samples = xylophone(frequency)
        path = OUTPUT_DIRECTORY / f"xylophone_{note}.wav"
        write_wav(path, apply_safety_fades(samples), target_peak=PEAK)
        print(f"created {path.relative_to(OUTPUT_DIRECTORY.parent.parent)}")


if __name__ == "__main__":
    main()

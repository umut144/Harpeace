"""Generate clean reference tones for the audio-foundation test.

These files intentionally contain no synthesis model, noise, detuning or
compression. They isolate the Godot import and mixer path.

Run from the repository root:
    python3 audio_generator/generate_reference_sines.py
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44_100
DURATION_SECONDS = 1.5
PEAK = 0.25  # -12 dBFS: safe headroom for several simultaneous voices.
FADE_SECONDS = 0.01
NOTES = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00}
OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "sounds" / "reference_sine"


def envelope(index: int, count: int) -> float:
    fade_samples = int(SAMPLE_RATE * FADE_SECONDS)
    if index < fade_samples:
        return index / fade_samples
    if index >= count - fade_samples:
        return (count - index - 1) / fade_samples
    return 1.0


def write_sine(note: str, frequency: float) -> None:
    count = int(SAMPLE_RATE * DURATION_SECONDS)
    samples = []
    for index in range(count):
        time = index / SAMPLE_RATE
        sample = PEAK * math.sin(math.tau * frequency * time) * envelope(index, count)
        samples.append(max(-1.0, min(1.0, sample)))
    payload = b"".join(struct.pack("<h", round(sample * 32767)) for sample in samples)
    path = OUTPUT_DIRECTORY / f"sine_{note}.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(payload)
    print(f"created {path.relative_to(OUTPUT_DIRECTORY.parent.parent)}")


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for note, frequency in NOTES.items():
        write_sine(note, frequency)


if __name__ == "__main__":
    main()

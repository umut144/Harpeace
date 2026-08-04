"""Create five C-major-pentatonic WAV samples for each MVP instrument.

This has no external dependencies. Run from the repository root:
    python3 audio_generator/generate_sounds.py
"""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44_100
DURATION_SECONDS = 1.8
NOTES = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00}
OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "sounds"


def stable_seed(instrument: str, note: str) -> int:
    """Avoid Python's deliberately randomised hash() so regeneration is repeatable."""
    return sum((index + 1) * ord(character) for index, character in enumerate(f"{instrument}:{note}"))


def envelope(index: int, total: int, decay: float, attack_seconds: float = 0.004) -> float:
    attack = max(1, int(SAMPLE_RATE * attack_seconds))
    if index < attack:
        return index / attack
    remaining = total - index
    release = max(1, int(SAMPLE_RATE * 0.012))
    fade_out = min(1.0, remaining / release)
    return math.exp(-decay * index / total) * fade_out


def plucked(freq: float, brightness: float, decay: float, seed: int) -> list[float]:
    """A small Karplus-Strong string model, suitable for harp and piano colours."""
    randomizer = random.Random(seed)
    period = max(2, round(SAMPLE_RATE / freq))
    line = [randomizer.uniform(-1.0, 1.0) for _ in range(period)]
    samples: list[float] = []
    count = int(SAMPLE_RATE * DURATION_SECONDS)
    damping = 0.9915 if decay < 3.0 else 0.985
    for index in range(count):
        value = line[index % period]
        samples.append(value * envelope(index, count, decay))
        following = (index + 1) % period
        line[index % period] = damping * (brightness * line[index % period] + (1.0 - brightness) * line[following])
    return samples


def xylophone(freq: float) -> list[float]:
    count = int(SAMPLE_RATE * DURATION_SECONDS)
    result: list[float] = []
    for index in range(count):
        time = index / SAMPLE_RATE
        tone = (
            math.sin(math.tau * freq * time)
            + 0.40 * math.sin(math.tau * freq * 3.99 * time)
            + 0.18 * math.sin(math.tau * freq * 10.65 * time)
        )
        result.append(tone * envelope(index, count, 8.0, 0.001))
    return result


def violin(freq: float) -> list[float]:
    count = int(SAMPLE_RATE * DURATION_SECONDS)
    result: list[float] = []
    attack = int(SAMPLE_RATE * 0.10)
    release = int(SAMPLE_RATE * 0.20)
    for index in range(count):
        time = index / SAMPLE_RATE
        vibrato = 1.0 + 0.004 * math.sin(math.tau * 5.2 * time)
        tone = math.sin(math.tau * freq * vibrato * time) + 0.23 * math.sin(math.tau * freq * 2.0 * vibrato * time)
        amp = min(1.0, index / attack) * min(1.0, (count - index) / release)
        result.append(tone * amp * 0.42)
    return result


def normalise(samples: list[float]) -> list[float]:
    peak = max(abs(sample) for sample in samples) or 1.0
    return [max(-1.0, min(1.0, sample / peak * 0.85)) for sample in samples]


def write_wav(path: Path, samples: list[float]) -> None:
    payload = b"".join(struct.pack("<h", round(sample * 32767)) for sample in normalise(samples))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(payload)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    for note, frequency in NOTES.items():
        sounds = {
            "harp": plucked(frequency, brightness=0.52, decay=3.5, seed=stable_seed("harp", note)),
            "piano": plucked(frequency, brightness=0.60, decay=1.6, seed=stable_seed("piano", note)),
            "xylophone": xylophone(frequency),
            "violin": violin(frequency),
        }
        for instrument, samples in sounds.items():
            target = OUTPUT_DIRECTORY / f"{instrument}_{note}.wav"
            write_wav(target, samples)
            print(f"created {target.relative_to(OUTPUT_DIRECTORY.parent)}")


if __name__ == "__main__":
    main()

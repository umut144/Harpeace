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
VIOLIN_DURATION_SECONDS = 0.9
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


def plucked(freq: float, brightness: float, decay: float, seed: int, duration_seconds: float = DURATION_SECONDS) -> list[float]:
    """A small Karplus-Strong string model, suitable for harp and piano colours."""
    randomizer = random.Random(seed)
    period = max(2, round(SAMPLE_RATE / freq))
    line = [randomizer.uniform(-1.0, 1.0) for _ in range(period)]
    samples: list[float] = []
    count = int(SAMPLE_RATE * duration_seconds)
    damping = 0.9915 if decay < 3.0 else 0.985
    for index in range(count):
        value = line[index % period]
        samples.append(value * envelope(index, count, decay))
        following = (index + 1) % period
        line[index % period] = damping * (brightness * line[index % period] + (1.0 - brightness) * line[following])
    return samples


def harp(freq: float, seed: int) -> list[float]:
    """Bright, short and bell-like: deliberately unlike the darker piano model."""
    string = plucked(freq, brightness=0.38, decay=5.3, seed=seed)
    count = len(string)
    result: list[float] = []
    for index, value in enumerate(string):
        time = index / SAMPLE_RATE
        shimmer = (
            0.62 * value
            + 0.22 * math.sin(math.tau * freq * 2.0 * time)
            + 0.10 * math.sin(math.tau * freq * 3.0 * time)
        )
        result.append(shimmer * envelope(index, count, 4.8, 0.002))
    return result


def piano(freq: float, seed: int) -> list[float]:
    """Three subtly detuned, long strings with a soft low register reinforcement."""
    strings = [
        plucked(freq * 0.9975, brightness=0.78, decay=0.60, seed=seed),
        plucked(freq, brightness=0.76, decay=0.60, seed=seed + 1),
        plucked(freq * 1.0025, brightness=0.78, decay=0.60, seed=seed + 2),
    ]
    count = len(strings[0])
    result: list[float] = []
    previous = 0.0
    hammer_random = random.Random(seed + 7919)
    for index in range(count):
        time = index / SAMPLE_RATE
        strings_mix = sum(string[index] for string in strings) / len(strings)
        low_body = 0.13 * math.sin(math.tau * (freq / 2.0) * time) * envelope(index, count, 1.5)
        # A short hammer transient separates the piano attack from the harp's softer pluck.
        hammer_decay = math.exp(-95.0 * time)
        hammer_noise = hammer_random.uniform(-1.0, 1.0) * hammer_decay * 0.16
        hammer_tone = (
            0.13 * math.sin(math.tau * freq * time)
            + 0.08 * math.sin(math.tau * freq * 2.7 * time)
            + 0.04 * math.sin(math.tau * freq * 5.1 * time)
        ) * hammer_decay
        previous = 0.68 * previous + 0.32 * (strings_mix + low_body)
        result.append(previous + hammer_noise + hammer_tone)
    return result


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
    count = int(SAMPLE_RATE * VIOLIN_DURATION_SECONDS)
    result: list[float] = []
    attack = int(SAMPLE_RATE * 0.10)
    release = int(SAMPLE_RATE * 0.12)
    for index in range(count):
        time = index / SAMPLE_RATE
        vibrato = 1.0 + 0.004 * math.sin(math.tau * 5.2 * time)
        tone = math.sin(math.tau * freq * vibrato * time) + 0.23 * math.sin(math.tau * freq * 2.0 * vibrato * time)
        amp = min(1.0, index / attack) * min(1.0, (count - index) / release)
        result.append(tone * amp * 0.42)
    return result


def normalise(samples: list[float], target_peak: float = 0.85) -> list[float]:
    peak = max(abs(sample) for sample in samples) or 1.0
    return [max(-1.0, min(1.0, sample / peak * target_peak)) for sample in samples]


def write_wav(path: Path, samples: list[float], target_peak: float = 0.85) -> None:
    payload = b"".join(struct.pack("<h", round(sample * 32767)) for sample in normalise(samples, target_peak))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(payload)


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    for note, frequency in NOTES.items():
        sounds = {
            "harp": harp(frequency, seed=stable_seed("harp", note)),
            "piano": piano(frequency, seed=stable_seed("piano", note)),
            "xylophone": xylophone(frequency),
            "violin": violin(frequency),
        }
        for instrument, samples in sounds.items():
            target = OUTPUT_DIRECTORY / f"{instrument}_{note}.wav"
            # Two violin voices often overlap; extra headroom prevents summed clipping.
            target_peak = 0.55 if instrument == "violin" else 0.85
            write_wav(target, samples, target_peak)
            print(f"created {target.relative_to(OUTPUT_DIRECTORY.parent)}")


if __name__ == "__main__":
    main()

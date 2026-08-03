#!/usr/bin/env python3
"""Describe an audio file objectively, since the agent cannot listen to it.

Reports duration, level, stereo width and a coarse spectral balance, enough to tell shaped ambience from
raw noise.
"""
import struct
import sys
import wave
from pathlib import Path

path = Path(sys.argv[1])
with wave.open(str(path), "rb") as handle:
    channels = handle.getnchannels()
    width = handle.getsampwidth()
    rate = handle.getframerate()
    frames = handle.getnframes()
    raw = handle.readframes(frames)

print(f"{channels} channel(s), {rate} Hz, {width * 8} bits, {frames / rate:.1f} s")

samples = struct.unpack(f"<{len(raw) // 2}h", raw)
left = samples[0::channels]
right = samples[1::channels] if channels > 1 else left

peak = max(abs(value) for value in left)
mean = sum(abs(value) for value in left) / len(left)
print(f"peak {peak / 32768:.2f} of full scale, average level {mean / 32768:.3f}")

difference = sum(abs(a - b) for a, b in zip(left[:rate], right[:rate])) / rate
print(f"stereo difference {difference / 32768:.3f} (0 means mono)")

# Zero crossing rate separates low rumble from hiss without needing a full spectrum.
crossings = sum(1 for a, b in zip(left, left[1:]) if (a >= 0) != (b >= 0))
print(f"zero crossing rate {crossings / (frames / rate):.0f} per second")

# Envelope over time tells whether anything actually evolves, or whether it is a flat wall of sound.
window = rate // 2
levels = []
for start in range(0, len(left) - window, window):
    chunk = left[start:start + window]
    levels.append(sum(abs(value) for value in chunk) / window / 32768)
print("half-second envelope:", " ".join(f"{level:.3f}" for level in levels))

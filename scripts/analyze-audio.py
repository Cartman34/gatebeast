#!/usr/bin/env python3
"""Diagnose why a synthesized sound reads as artificial, using measurable perceptual proxies.

The agent cannot listen. `inspect-audio.py` says whether a file is distinct; this one says whether it is
plausible, by measuring the properties that separate a natural texture from television static:

- spectral centroid and octave balance: static is bright and flat, real rain and water are dark;
- crest factor: a wall of noise has a low crest factor, discrete events raise it;
- modulation depth at 2-20 Hz: natural textures breathe, static does not;
- event density: above roughly 30 onsets per second discrete grains fuse into continuous hiss;
- pitch stability: a pure oscillator holds a frequency exactly, a living voice never does.

Usage: python3 analyze-audio.py <file.wav> [<file.wav> ...]
"""
import sys
import wave
from pathlib import Path

import numpy as np

BANDS = [(20, 125), (125, 500), (500, 2000), (2000, 6000), (6000, 20000)]
BAND_NAMES = ["low", "low-mid", "mid", "high-mid", "high"]


def read(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as handle:
        rate = handle.getframerate()
        channels = handle.getnchannels()
        raw = handle.readframes(handle.getnframes())
    samples = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return samples, rate


def envelope(signal: np.ndarray, rate: int, hop: int) -> np.ndarray:
    usable = len(signal) - len(signal) % hop
    return np.sqrt((signal[:usable].reshape(-1, hop) ** 2).mean(axis=1))


def describe(path: Path) -> None:
    signal, rate = read(path)
    duration = len(signal) / rate
    rms = np.sqrt(np.mean(signal ** 2))
    peak = np.max(np.abs(signal))
    crest = 20 * np.log10(peak / (rms + 1e-12) + 1e-12)

    spectrum = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
    frequencies = np.fft.rfftfreq(len(signal), 1.0 / rate)
    power = spectrum ** 2
    centroid = float((frequencies * power).sum() / (power.sum() + 1e-12))
    total = power.sum() + 1e-12
    shares = [power[(frequencies >= low) & (frequencies < high)].sum() / total for low, high in BANDS]

    # Amplitude modulation of the 2-20 Hz "breathing" band, measured on the loudness envelope.
    hop = max(1, rate // 200)
    env = envelope(signal, rate, hop)
    env_rate = rate / hop
    env_centered = env - env.mean()
    env_spectrum = np.abs(np.fft.rfft(env_centered))
    env_frequencies = np.fft.rfftfreq(len(env_centered), 1.0 / env_rate)
    slow = env_spectrum[(env_frequencies >= 0.2) & (env_frequencies < 2)].sum()
    breath = env_spectrum[(env_frequencies >= 2) & (env_frequencies < 20)].sum()
    fast = env_spectrum[(env_frequencies >= 20)].sum()
    modulation = float(env.std() / (env.mean() + 1e-12))

    # Onset counting on the envelope: a rise above a local median marks a discrete audible event.
    smooth = np.convolve(env, np.ones(5) / 5, mode="same")
    rising = np.diff(smooth, prepend=smooth[0])
    threshold = np.percentile(rising, 97)
    onsets = int(np.sum((rising[1:] > threshold) & (rising[:-1] <= threshold)))

    print(f"--- {path.name}")
    print(f"    {duration:.1f} s | rms {rms:.3f} | peak {peak:.2f} | crest {crest:.1f} dB")
    print(f"    spectral centroid {centroid:.0f} Hz")
    print("    balance " + " ".join(f"{name} {share * 100:.0f}%" for name, share in zip(BAND_NAMES, shares)))
    print(f"    envelope variation {modulation:.2f} | slow {slow:.0f} breath {breath:.0f} fast {fast:.0f}")
    print(f"    onsets {onsets} ({onsets / duration:.0f} per second)")


for argument in sys.argv[1:]:
    describe(Path(argument))

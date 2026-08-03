#!/usr/bin/env python3
"""Probe what kinds of sound can actually be produced on this machine.

The agent cannot listen, so capability is established by producing a deliberately varied battery — short
effects, ambiences and a scene — and then measuring each result. Only what is measured is claimed.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "assets" / "audio-probe"
TARGET.mkdir(parents=True, exist_ok=True)

SOUNDS = {
    "step-grass": "a single soft footstep on grass, about half a second, dry and close",
    "water-stream": "a small forest stream flowing over stones, looping, about 10 seconds",
    "bird-call": "a short whistled bird call of two or three notes, about 1.5 seconds, no background",
    "gate-hum": "a low mysterious magical hum with a faint shimmering overtone, as if a glowing portal were "
                "humming, looping, about 8 seconds",
    "ui-confirm": "a short pleasant interface confirmation chime, two rising notes, about 0.5 second",
    "rain-canopy": "steady rain falling on a forest canopy, looping, about 10 seconds",
    "creature-cry": "a small friendly creature's short cry, curious and warm, not scary, about 1 second",
    "scene-clearing": "a full ambience scene of a forest clearing at dusk, layering soft wind, distant "
                      "birds, faint rustling leaves and a far away stream, about 20 seconds",
}

INSTRUCTION = (
    "Produce this sound: {description}. Save it as a 16 bit stereo WAV file to ./{name}.wav in the current "
    "directory. Synthesize it with whatever is available (python, ffmpeg, sox). Shape it deliberately: it "
    "must be recognisable as the thing described, not generic noise. If it is impossible, write "
    "./{name}-IMPOSSIBLE.txt explaining precisely why."
)


def produce(item):
    name, description = item
    if (TARGET / f"{name}.wav").is_file():
        return name, True
    prompt = INSTRUCTION.format(description=description, name=name)
    subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", prompt],
        cwd=TARGET, capture_output=True, text=True, timeout=900,
    )

    return name, (TARGET / f"{name}.wav").is_file()


with ThreadPoolExecutor(max_workers=8) as pool:
    outcomes = list(pool.map(produce, SOUNDS.items()))

failures = [name for name, produced in outcomes if not produced]
for name, produced in outcomes:
    print(f"{'OK' if produced else 'FAILED'} {name}")

inspector = Path(__file__).resolve().parent / "inspect-audio.py"
for name, produced in outcomes:
    if produced:
        print(f"\n--- {name}")
        subprocess.run([sys.executable, str(inspector), str(TARGET / f"{name}.wav")])

sys.exit(1 if failures else 0)

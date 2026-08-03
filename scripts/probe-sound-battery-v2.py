#!/usr/bin/env python3
"""Second sound battery: the four sounds the owner rejected, resynthesized from a technical diagnosis.

The first battery described the wanted *result* and let the generator choose its technique. It produced
filtered noise walls: television static for the natural textures, bare oscillators for the living sounds.
Measurement of that batch (see analyze-audio.py) showed the common cause — every rejected sound had a
crest factor of 6 to 12 dB and an envelope variation below 0.30, while the only sound the owner liked,
the clearing scene, had 17.2 dB of crest and 0.50 of variation. The failures were dynamically flat.

So this battery prescribes the *synthesis method*, not the result, and sets numeric acceptance targets on
the properties that separate a plausible sound from static. Each prompt names the model to use, the
randomization required, the layer structure, and the forbidden shortcuts.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "assets" / "audio-probe-v2"
TARGET.mkdir(parents=True, exist_ok=True)

# Applies to all four: the first batch died of dynamic flatness, so headroom is a hard requirement.
COMMON = """
Write a Python 3 script named ./{name}.py using numpy and the standard `wave` module, run it, and leave
both the script and the resulting ./{name}.wav in the current directory. 48000 Hz, 16 bit, stereo.

MANDATORY ACROSS THE WHOLE JOB — the previous attempt at this sound failed exactly here:

1. NEVER apply tanh saturation, limiting, compression or peak normalization to a fixed loud level. The
   previous version ended with `np.tanh(x * 2.15)` then a normalize to 0.91 of full scale, which crushed
   the crest factor to 8-12 dB and turned discrete events into one flat wall of noise. Instead: build the
   layers at their natural relative gains, then apply ONE global scalar so the absolute peak lands at
   {peak} of full scale. Nothing else touches the dynamics.
2. The result must measure a crest factor (peak over RMS, in dB) of at least {crest} dB and an overall
   RMS between {rms_low} and {rms_high}. Compute these in your script and print them. If the crest factor
   is below target, the sound is too dense or too compressed: reduce the number of simultaneous events
   and lower the continuous background layer, do not raise the peak.
3. Every repeated element must be individually randomized — pitch, duration, gain, stereo position,
   timbre and start time all drawn per event from a random distribution, never a constant, never a
   regular grid. Two events of the same kind must never be identical samples.
4. Layer several distinct sound populations rather than perfecting one. The one sound the owner accepted
   was the one with the most independent layers.

Verify by re-reading the written file with `wave` and asserting the format, and print the measured
duration, peak, RMS, crest factor and spectral centroid. If you cannot meet a target, still write the
file and write ./{name}-NOTES.txt stating which target you missed and by how much.
"""

SOUNDS = {
    "water-stream": {
        "peak": "0.70", "crest": "16", "rms_low": "0.04", "rms_high": "0.09",
        "brief": """
A small forest stream flowing over stones, seamless 12 second loop, heard from two or three metres away.

DIAGNOSIS OF THE FAILED VERSION: it was band-passed white noise with an envelope variation of 0.13 and
80% of its energy spread evenly across 125-2000 Hz. Continuous filtered noise is what a detuned
television sounds like. Water does not sound like water because of its noise band; it sounds like water
because of discrete resonant bubbles.

REQUIRED SYNTHESIS METHOD — build exactly these four layers:

LAYER 1, the bubbles, which carry the entire identity and must dominate the character. Use the standard
bubble physical model: a bubble is a decaying sinusoid whose frequency RISES over its lifetime. For each
bubble draw a base frequency f0 log-uniformly between 300 and 2500 Hz, and a lifetime d between 8 and
120 ms; the instantaneous frequency is f0 * (1 + rise * t / d) with rise drawn between 0.3 and 1.2, and
the amplitude is exp(-t / (0.35 * d)) with a 1 ms raised-cosine attack. Small bubbles are high and short,
large bubbles are low and long — correlate f0 and d inversely. Place 40 to 70 bubbles per second at
random times (Poisson, not a grid), pan each one randomly, and vary their gains over a 12 dB range so a
few pop out clearly above the rest. Small bubbles are far more numerous than large ones: draw sizes from
a distribution weighted heavily towards the short high ones.

LAYER 2, the flow bed: pink-to-brown noise, spectral slope around -1.0, low-passed hard so that almost
nothing survives above 2000 Hz. Keep it QUIET — clearly below the bubbles, a bed and not the subject.

LAYER 3, breathing: modulate the bed amplitude with the sum of three slow random sine waves between 0.1
and 0.8 Hz, total modulation depth around 30%. Water volume shifts continuously; a constant level reads
as machine noise.

LAYER 4, sparse accents: 6 to 10 louder gurgles across the loop, each a short cluster of 5 to 12 bubbles
sharing a falling pitch centre, 150 to 400 ms long, panned to one side.

The owner said the previous version was "too fast", like a violent waterfall. Aim deliberately slow and
sparse: individual audible plops, gaps between them, low overall energy. Spectral centroid must land
between 400 and 1000 Hz and less than 5% of the energy may sit above 6000 Hz.

Make it loop seamlessly by wrapping every event circularly around the buffer end.
""",
    },
    "rain-canopy": {
        "peak": "0.70", "crest": "16", "rms_low": "0.04", "rms_high": "0.09",
        "brief": """
Steady rain falling on a forest canopy, seamless 12 second loop, heard from underneath the trees.

DIAGNOSIS OF THE FAILED VERSION: its spectral centroid was 7582 Hz with 39% of all energy above 6000 Hz,
and it fired roughly 190 droplets per second. That is precisely television static — bright broadband
hiss. Two independent errors: the spectrum was far too bright, and the droplet density was far above the
roughly 30 events per second at which the ear stops hearing separate impacts and hears continuous noise.

REQUIRED SYNTHESIS METHOD:

SPECTRUM: rain under a canopy is DARK. Leaves absorb the highs. The noise bed must use a spectral slope
near -1.2 and be low-passed so that above 4000 Hz there is almost nothing. Final spectral centroid must
land between 700 and 1800 Hz, with less than 10% of total energy above 6000 Hz. This is the single most
important constraint of this job.

DROPLET DENSITY: total no more than 25 discrete droplet events per second, all layers combined. The
listener must be able to pick out individual impacts. Do not exceed this to make it sound fuller — if it
sounds thin, thicken the bed, never the droplet count.

Build these layers:

LAYER 1, leaf impacts, about 18 per second: each a very short filtered noise burst, 4 to 15 ms, with a
1 ms attack and exponential decay, band-limited between 600 and 3000 Hz — a dull leaf slap, not a bright
tick. Randomize duration, centre frequency, gain over a 15 dB range, and pan widely.

LAYER 2, heavy drips falling from the canopy edge onto the ground or a leaf below, about 4 per second:
use the bubble model, a decaying sinusoid of 150 to 700 Hz whose frequency rises over a 30 to 90 ms
lifetime. These are the drips the ear latches onto — make them clearly audible above the bed.

LAYER 3, the distant sheet of rain: dark noise as described above, quiet, with a stereo-decorrelated
pair so it has width without a centre image.

LAYER 4, gusts: modulate the whole bed with slow random sines between 0.07 and 0.4 Hz at 40% depth, so
the rain visibly swells and recedes. Flat rain reads as static; breathing rain reads as weather.

LAYER 5, three or four one-off events across the loop: a small cascade of accumulated water sliding off a
branch, 300 to 800 ms, a rapid burst of 10 to 20 drips with a falling density envelope, panned off-centre.

The owner said the previous one was "too fast, almost continuous". Err towards sparse and slow.
Wrap every event circularly so the loop is seamless.
""",
    },
    "bird-call": {
        "peak": "0.75", "crest": "14", "rms_low": "0.06", "rms_high": "0.14",
        "brief": """
A small forest bird calling: a short phrase of three or four notes, about 2.5 seconds including the
silence between notes, no background at all.

DIAGNOSIS OF THE FAILED VERSION: 99% of its energy sat in a single 2000-6000 Hz band with literally
nothing anywhere else, and its crest factor was 6.4 dB. It was one bare sine whistle with a smooth pitch
line and no noise. The owner heard "a very high child's scream, not a bird". A real bird call is not a
pure tone: it has a fast unstable pitch trajectory, a weak second harmonic, and audible breath noise at
the attack.

REQUIRED SYNTHESIS METHOD:

PITCH TRAJECTORY — this is what makes it a bird. Each note is a fast glide, not a held pitch. Per note,
draw a start and end frequency between 1800 and 4500 Hz with a ratio between them of at least 1.4, and
sweep between them on a curve that is NOT linear: use an exponential or S-curve, and include an
overshoot at the start of the note where the pitch shoots past the target within the first 15 ms and
settles back. A bird syrinx cannot hold a steady pitch — superimpose a vibrato of 4 to 7% depth at 25 to
60 Hz, itself randomly varying in rate over the note, plus a fine random jitter of 1 to 2%.

NOTE DURATION: 60 to 180 ms each. These are short, brilliant, articulated notes. Between notes leave
silences of 90 to 300 ms, all different lengths — never an even rhythm.

TIMBRE: the fundamental plus a second harmonic at about -18 dB and a third at about -28 dB. That small
amount of harmonic content removes the "pure electronic whistle" quality without making it buzzy. Do not
add more harmonics than that.

BREATH: at the onset of each note, a 10 to 20 ms burst of band-passed noise around the note's starting
frequency, at about -20 dB relative to the note, decaying immediately. This attack noise is what makes it
read as produced by a living throat rather than by an oscillator.

ENVELOPE: 5 to 12 ms attack, then a gentle decay, then a 20 to 40 ms release. Never an instantaneous
attack, never a rectangular envelope.

PHRASE SHAPE: the notes are not equal. Make the second note the loudest, and the last one shorter and
quieter, dropping in pitch, as though trailing off. Vary each note's gain by up to 6 dB.

SPACE: a very short bright early reflection, 20 to 45 ms delayed, at about -22 dB, to place the bird in
open air rather than in a vacuum. Very light stereo.

The energy must NOT sit in a single band: at least three of the bands 500-2000, 2000-6000 and 6000-20000
Hz must each hold a measurable share. Do not exceed a 4500 Hz fundamental — the previous one was too
shrill.
""",
    },
    "creature-cry": {
        "peak": "0.75", "crest": "14", "rms_low": "0.06", "rms_high": "0.14",
        "brief": """
A small friendly creature's short cry, curious and warm, not scary, about 1.2 seconds. Think of a young
animal chirruping a question, an organic voice — no background.

DIAGNOSIS OF THE FAILED VERSION: all of its energy sat between 125 and 2000 Hz with a smooth pitch and a
crest factor of 8.6 dB. It was a stable oscillator through a fixed filter, which is why the owner said
"if it is a robot then maybe — it lacks naturalness, it is very electronic". A stable oscillator is
inherently electronic. Naturalness in a voice comes from the source being irregular and from the filter
being a set of resonant formants, not from the waveform.

REQUIRED SYNTHESIS METHOD — build a source-filter vocal model, not an oscillator:

THE SOURCE must be a glottal pulse train, not a sine or a saw. Generate it pulse by pulse: each glottal
period emits one asymmetric pulse — a fast rise over about 40% of the period and a faster closing phase,
for instance a raised-cosine rise followed by an exponential fall. Build the signal by placing these
pulses one after another at the current period.

JITTER AND SHIMMER — this is the whole point, and its absence is why the last one sounded synthetic.
Every single glottal period must be perturbed: the period length randomly varied by 2 to 4% (jitter) and
the pulse amplitude randomly varied by 8 to 15% (shimmer), redrawn for every period. These micro
irregularities are what the ear reads as "alive". Without them the result is a machine, however good the
rest is.

PITCH CONTOUR: base frequency between 220 and 400 Hz — a small creature, but keep it in voice range, not
a whistle. The contour must be non-monotonic and expressive: a fast upward chirp over the first 60 ms,
a brief plateau, then a rise at the end, like a question. Superimpose an irregular vibrato of 5 to 7 Hz
whose depth grows towards the end of the cry.

THE FILTER: pass the source through four resonant formant filters (two-pole resonators). Use formant
centres in the region of 600, 1200, 2600 and 3600 Hz with bandwidths of 80 to 150 Hz, and MOVE them over
the duration of the cry — sweep the first two formants by 20 to 40% across the sound, as a real mouth
opening and closing would. Static formants sound like a fixed filter; moving formants sound like a
creature articulating.

BREATH: mix in band-passed noise at about -25 dB, its level following the amplitude envelope, plus a
slightly louder breath burst in the first 30 ms and a short exhale after the voiced part ends.

SUBHARMONIC WARMTH: add a little energy one octave below at about -20 dB, amplitude-modulated
irregularly, to give the creature body rather than thinness.

ENVELOPE: 25 ms attack, a body of variable level that is not flat — let it dip slightly in the middle
and swell again — and a 150 to 250 ms release with the breath tail.

SPACE: light early reflections around 30 ms at -24 dB.

The energy must be spread across at least three frequency bands, with a measurable share above 2000 Hz
coming from the upper formants and the breath. Warm and curious, not menacing, not electronic.
""",
    },
}


def produce(item):
    name, recipe = item
    if (TARGET / f"{name}.wav").is_file():
        return name, True
    prompt = recipe["brief"].strip() + "\n\n" + COMMON.format(
        name=name, peak=recipe["peak"], crest=recipe["crest"],
        rms_low=recipe["rms_low"], rms_high=recipe["rms_high"],
    ).strip()
    subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", prompt],
        cwd=TARGET, capture_output=True, text=True, timeout=1800,
    )

    return name, (TARGET / f"{name}.wav").is_file()


with ThreadPoolExecutor(max_workers=4) as pool:
    outcomes = list(pool.map(produce, SOUNDS.items()))

for name, produced in outcomes:
    print(f"{'OK' if produced else 'FAILED'} {name}")

analyzer = Path(__file__).resolve().parent / "analyze-audio.py"
produced_files = [str(TARGET / f"{name}.wav") for name, produced in outcomes if produced]
if produced_files:
    subprocess.run([sys.executable, str(analyzer), *produced_files])

sys.exit(0 if all(produced for _, produced in outcomes) else 1)

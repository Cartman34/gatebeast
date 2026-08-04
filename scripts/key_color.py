"""The key colour — the single service that owns the magenta backdrop and every decision made on it.

Same rule as the tile scale: a pivot value lives in one service with the operations that consume it.
The key colour and its two thresholds were copied into both the cutout and the measurement tool, each
with its own name for the same idea; tune one and the two disagree about what counts as background,
which shows up as a sprite that measures clean and cuts out ragged.

WHAT THIS SERVICE OWNS
  the colour     MAGENTA, the backdrop the generator is asked for
  the distance   distance(), the one way this project decides how far a pixel is from that backdrop
  the thresholds HARD and SOFT, and the alpha ramp between them
  the verdicts   is_background / is_subject, so no caller writes its own comparison

WHY THESE THRESHOLDS — measured, not chosen by taste. On the three POC images the distance to pure
magenta is bimodal with an empty valley: the flat field sits at or under 33, the subject starts at 160,
and about one pixel in a thousand lies between — the anti-aliased rim, and nothing else.

  HARD = 60   above the field's worst speckle (33), far below the subject (160).
  SOFT = 150  just short of the darkest subject pixel observed, so no subject pixel is ever made
              even slightly transparent.

Pure magenta appears in no material of this world — grass, stone, wood, water, fur — so keying it out
cannot eat into a subject.
"""
import numpy

# The backdrop the generator is asked for. Not bit-exact in what comes back, hence the thresholds.
MAGENTA = numpy.array([255, 0, 255], dtype=numpy.int16)

HARD = 60    # at or below this distance, the pixel is background
SOFT = 150   # at or above, the pixel is subject


def distance(rgb):
    """Per-pixel distance to the key colour: the largest gap over the three channels.

    Accepts a single pixel or a whole image array; returns a scalar or a matching array.
    """
    values = numpy.asarray(rgb, dtype=numpy.int16)

    return numpy.max(numpy.abs(values - MAGENTA), axis=-1)


def alpha_ramp(measured):
    """0 below HARD, 1 above SOFT, linear in between — what keeps the rim smooth instead of jagged."""
    ramp = (numpy.asarray(measured, dtype=numpy.float32) - HARD) / (SOFT - HARD)

    return numpy.clip(ramp, 0.0, 1.0)


def is_background(measured):
    """True where the pixel is the backdrop and nothing else."""
    return numpy.asarray(measured) <= HARD


def is_subject(measured):
    """True where the pixel belongs to the subject beyond any doubt."""
    return numpy.asarray(measured) >= SOFT


def describe():
    """The thresholds, stated from the one place that holds them."""
    return f"seuils de détourage {HARD} / {SOFT} sur la distance au magenta"

#!/usr/bin/env python3
"""The single vocabulary of a SHAPE — the one thing every tool that draws or checks a tracing piece
must agree on, and the one place that says so.

WHY THIS MODULE EXISTS
The fifteen edge combinations a track can reach were copied by hand into five different tools before
this module existed: the frozen asset catalogue, the composition-plan builder, the fence campaign, the
catalogue's own self-test, and the referentiel checker. None of the five knew the other four existed,
and nothing kept their copies in step — one of them did not even list the fifteen in the same order as
the others. That is the exact cost a copied list pays, silently, until the day two of its copies are
compared and found to disagree.

THE RULE FROM HERE ON: nobody defines a shape, an edge combination, or the fifteen list a second time.
Every tool that needs to know whether a shape is well-formed, which edges it reaches, or wants the
canonical list of combinations, asks this module. A second copy anywhere is exactly the defect this
module exists to rule out — the same discipline the tile scale already holds for pixel sizes
(tile_scale.py), which have not diverged since it became the one place that states them.

WHAT THIS MODULE DOES NOT DO
It never reads assets/sujets.json and never invents what it declares — which shapes a type actually
uses, or a sujet's own shape. It only says whether a shape NAME is well-formed and what it means as a
set of edges. Whether that particular shape is the right one for a given sujet is the referentiel's
call, never this module's.
"""

# The four compass edges a case has, in the one order the design fixes (sujets-et-variantes.md,
# decision 26): n, e, s, w. Diagonals are meant to join them later without rewriting anything — this
# tuple is the one place that would grow.
EDGES = ("n", "e", "s", "w")

# The value every subject that does not assemble end to end carries, and the only shape that is never
# written into an address (sujets-et-variantes.md, decision 25).
DEFAULT_SHAPE = "plain"


def edge_combinations():
    """The fifteen non-empty edge combinations, each written in the canonical n, e, s, w order —
    GENERATED, never listed by hand, so a sixth copy of "the fifteen" can never drift from this one."""
    combinations = []
    for mask in range(1, 1 << len(EDGES)):
        combinations.append("".join(edge for index, edge in enumerate(EDGES) if mask & (1 << index)))

    return sorted(combinations, key=lambda name: (len(name), [EDGES.index(edge) for edge in name]))


def valid_shape(shape):
    """A shape is "plain", or a bare edge combination written n before e before s before w
    (sujets-et-variantes.md, decision 26) — never repeated, never out of order."""
    if shape == DEFAULT_SHAPE:
        return True
    if not shape or any(character not in "nesw" for character in shape):
        return False

    return list(shape) == sorted(shape, key="nesw".index) and len(set(shape)) == len(shape)


def edges_of(shape):
    """The edges a shape reaches. A subject that does not assemble ("plain") reaches none.

    Does not validate: a caller that needs to refuse a malformed shape calls valid_shape first, the
    same way the emprise and the height are checked before anything is built from them.
    """
    return [] if shape == DEFAULT_SHAPE else list(shape)

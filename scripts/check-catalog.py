#!/usr/bin/env python3
"""Self-validation of the catalogue module: addressing, parsing, fallback, round-trip, missing lists.

USAGE
  python3 scripts/check-catalog.py       the verdict: how many checks passed, and which profiles are incomplete
  python3 scripts/check-catalog.py -v    the walk-through, check by check
  python3 scripts/check-catalog.py -h    this text

INTENTION
  Generates nothing and writes nothing outside its own sandbox file. A failing check raises on the spot, carrying the label of what it was proving.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gatebeast" / "scripts"))

import asset_catalog
import shape_vocab
from asset_catalog import Catalog, Image, Profile, Variant, parse_address

checks = 0
# A CHECKER PRINTS ITS VERDICT, NOT ITS REASONING (methode/execution.md, "Une sortie qui inonde le contexte"). Seventy-three "ok" lines landed in the caller's
# context on every run, one per check that passed — nothing a reader acts on, and the cost is paid by everything they do next. What fails still speaks: an
# assertion carries the label of the check it broke. `--detail` brings the walk-through back when one wants to read it.
DETAIL = "-v" in sys.argv or "--verbose" in sys.argv
if "-h" in sys.argv or "--help" in sys.argv:
    print(__doc__.strip())
    raise SystemExit(0)


def expect(condition, label):
    global checks
    checks += 1
    assert condition, f"FAILED: {label}"
    if DETAIL:
        print(f"  ok  {label}")


def section(title):
    if DETAIL:
        print(title)


section("ADDRESSING — directions are written only when they leave the default")
expect(Variant("south").address(1) == "orientation-south_action-idle_frame-01",
       "main view address")
expect(Variant("south", "idle", {"gaze": "north"}).address(1)
       == "orientation-south_action-idle_frame-01",
       "a direction at its default is not written")
expect(Variant("south", "point", {"gaze": "east", "left-hand": "up"}).address(1)
       == "orientation-south_action-point_gaze-east_left-hand-up_frame-01",
       "the design's own example is reproduced")
expect(Variant("south", "walk").address(12) == "orientation-south_action-walk_frame-12",
       "frames are numbered on two digits")
expect(Variant("south", "point", {"left-hand": "up", "gaze": "east"}).address(1)
       == Variant("south", "point", {"gaze": "east", "left-hand": "up"}).address(1),
       "parts are sorted, so one posture has exactly one address")

section("\nSHAPE — the set of edges a track reaches")
expect(asset_catalog.EDGE_SHAPES[:6] == ["n", "e", "s", "w", "ne", "ns"],
       "the fifteen edge sets are generated in the canonical n, e, s, w order")
expect(len(asset_catalog.EDGE_SHAPES) == 15, "fifteen combinations, no diagonals")
expect("nesw" in asset_catalog.EDGE_SHAPES and "es" in asset_catalog.EDGE_SHAPES,
       "a full crossing and an angle are both edge sets")
expect(asset_catalog.edges_of("nes") == ["n", "e", "s"], "a shape reads back as its edges")
expect(asset_catalog.edges_of("plain") == [], "a subject that does not assemble reaches no edge")
expect(asset_catalog.EDGE_SHAPES == shape_vocab.edge_combinations(),
       "the catalogue's fifteen combinations are shape_vocab's, not a copy of its own")

section("\nA LAYOUT IS CHECKED BY CALCULATION")
# A fence running west to east along three tiles: a dead end, a line, a dead end.
run = {(0, 0): "e", (1, 0): "ew", (2, 0): "w"}
expect(asset_catalog.check_layout(run) == [], "a straight run of three tiles is consistent")
# The same run with its middle tile turned into a corner: the east side no longer meets its neighbour.
broken = dict(run)
broken[(1, 0)] = "nw"
faults = asset_catalog.check_layout(broken)
# Two breaks, and both are real: the corner now points north into nothing, and the tile east of it
# has lost the neighbour it was reaching for.
expect(len(faults) == 2, "a corner in the middle of a run is caught")
expect({(fault["tile"], fault["edge"]) for fault in faults} == {((1, 0), "n"), ((2, 0), "w")},
       "each fault names the tile and the edge that disagrees")
expect(asset_catalog.joins("ew", "ew", "e"), "two lines side by side agree across their shared edge")
expect(not asset_catalog.joins("ew", "ns", "e"), "a line running into a crossing bar does not agree")
corner_run = {(0, 0): "e", (1, 0): "sw", (1, 1): "n"}
expect(asset_catalog.check_layout(corner_run) == [],
       "a run that turns a corner and stops is consistent")

section("\nSHAPE IN AN ADDRESS — written only when it leaves plain")
expect(Variant("south", "idle", shape="plain").address(1)
       == "orientation-south_action-idle_frame-01",
       "the default shape is never written")
expect(Variant("north", "idle", shape="ne").address(1)
       == "orientation-north_action-idle_shape-ne_frame-01",
       "the design's own shape example is reproduced")
expect(Variant("south", "idle", shape="ew").address(1)
       == "orientation-south_action-idle_shape-ew_frame-01",
       "the shape sits immediately after the action")
expect(Variant("south", "point", {"gaze": "east"}, "ne").address(1)
       == "orientation-south_action-point_shape-ne_gaze-east_frame-01",
       "the shape comes before the directions")
try:
    Variant("south", "idle", shape="banana")
    expect(False, "an unknown shape is refused")
except ValueError:
    expect(True, "an unknown shape is refused")

section("\nPARSING — an address reads back into what produced it")
for address in ["orientation-south_action-idle_frame-01",
                "orientation-north-east_action-run_gaze-north-west_frame-03",
                "orientation-north_action-idle_shape-ne_frame-01",
                "orientation-south_action-point_shape-nes_gaze-east_left-hand-up_frame-01",
                "orientation-south_action-point_gaze-east_left-hand-up_frame-01"]:
    variant, frame = parse_address(address)
    expect(variant.address(frame) == address, f"round trip {address}")
expect(parse_address("orientation-north_action-idle_shape-ne_frame-01")[0].shape == "ne",
       "the shape is read back off an address")
expect(parse_address("orientation-south_action-idle_frame-01")[0].shape == "plain",
       "an address without a shape means plain")
variant, _ = parse_address("orientation-north-east_action-run_gaze-north-west_frame-03")
expect(variant.directions == {"gaze": "north-west"},
       "a compound direction is not mistaken for its suffix")

section("\nFALLBACK — a variant never fails")
profile = Profile("TR-001", "vegetation", images=[
    Image("orientation-south_action-idle_frame-01", "a.png"),
    Image("orientation-south_action-walk_frame-01", "b.png"),
    Image("orientation-south_action-walk_frame-02", "c.png"),
    Image("orientation-west_action-idle_frame-01", "d.png"),
])
expect(profile.resolve("orientation-south_action-walk_frame-02").path == "c.png", "exact hit")
expect(profile.resolve("orientation-south_action-walk_frame-09").path == "b.png",
       "an absent frame falls back to frame-01")
expect(profile.resolve("orientation-south_action-idle_gaze-east_frame-01").path == "a.png",
       "an absent direction falls back to north")
expect(profile.resolve("orientation-south_action-jump_frame-01").path == "a.png",
       "an absent action falls back to idle")
expect(profile.resolve("orientation-north-west_action-idle_frame-01").path == "d.png",
       "an absent orientation falls back to the nearest available")
expect(profile.resolve("orientation-east_action-jump_gaze-up_frame-07") is not None,
       "everything absent at once still resolves")

section("\nTHE THREE QUESTIONS")
expect(profile.variants() == ["orientation-south_action-idle", "orientation-south_action-walk",
                              "orientation-west_action-idle"], "variants of a subject")
expect(profile.files() == ["a.png", "b.png", "c.png", "d.png"], "files of a subject")
expect(profile.frames("orientation-south_action-walk") == [1, 2], "frames of one posture")
expect(profile.missing("v0") == [], "a vegetation profile with its main view lacks nothing in v0")

human = Profile("PR-001", "human", height=2)
human.images.append(Image("orientation-south_action-idle_frame-01", "x.png"))
expect(len(human.missing("v0")) == 3, "a human with one view lacks its three other orientations in v0")
expect(len(human.missing("target")) == 7, "and seven images against the target lot")
path = Profile("CH-019", "path")
expect(len(path.missing("v0")) == 2 and len(path.missing("target")) == 5,
       "a path lacks 2 drawings in v0 and 5 in target — the renderer turns it for the rest")
expect(path.layer == "ground-decor", "a path is drawn in the ground-decor family")
expect(path.required("v0") == ["orientation-south_action-idle_shape-ns_frame-01",
                               "orientation-south_action-idle_shape-ne_frame-01"],
       "a path's v0 lot is addressed on the shape axis")
expect(path.required("target") == ["orientation-south_action-idle_shape-n_frame-01",
                                   "orientation-south_action-idle_shape-ns_frame-01",
                                   "orientation-south_action-idle_shape-ne_frame-01",
                                   "orientation-south_action-idle_shape-nes_frame-01",
                                   "orientation-south_action-idle_shape-nesw_frame-01"],
       "a path's target lot is the five drawings: dead end, line, angle, three-way, crossing")

fence = Profile("OB-010", "fence")
expect(fence.layer == "world", "a fence is drawn in the world family")
expect(len(fence.missing("v0")) == 6,
       "a fence lacks its six edge combinations — a volume is never turned by the renderer")
expect(fence.required("v0")[1] == "orientation-south_action-idle_shape-ew_frame-01",
       "the fence lot carries the line running east to west, the park's main view")

section("\nFALLBACK — the shape is part of the ask and never falls back")
fenced = Profile("OB-011", "fence", images=[
    Image("orientation-north_action-idle_shape-ns_frame-01", "line-north.png"),
    Image("orientation-east_action-idle_shape-ne_frame-01", "angle-east.png"),
])
expect(fenced.resolve("orientation-south_action-idle_shape-ne_frame-01").path == "angle-east.png",
       "a missing angle falls back to another angle, never to a line")
expect(fenced.resolve("orientation-south_action-idle_shape-ns_frame-01").path
       == "line-north.png", "a missing line falls back to another line")

section("\nROUND TRIP — the catalogue survives being written and read back")
sandbox = Path(__file__).resolve().parent / "catalogue-roundtrip.json"
Catalog([profile, human, path, fenced]).save(sandbox)
reread = asset_catalog.load(sandbox)
expect(sorted(reread.profiles) == ["CH-019", "OB-011", "PR-001", "TR-001"],
       "every profile came back")
expect(reread.profile("OB-011").images[0].variant.shape in ("ns", "ne"),
       "a shape survives being written and read back")
expect(reread.profile("PR-001").height == 2, "the declared height came back")
expect(reread.profile("TR-001").files() == profile.files(), "every file came back")
expect(reread.profile("TR-001").anchor == {"x": 0.5, "y": 1.0},
       "the pose point is the middle of the bottom edge of the footprint")

section("\nTHE REAL CATALOGUE")
real = asset_catalog.load()
expect(len(real.profiles) >= 1, f"the catalogue holds {len(real.profiles)} profile(s)")
expect("CH-001" in real.profiles, "the produced grass is inscribed")
for code in real.profiles:
    for image in real.profile(code).images:
        expect((ROOT / "gatebeast" / image.path).is_file(), f"{code}: {image.path} exists")
        expect((ROOT / "gatebeast" / image.source).is_file(), f"{code}: source {image.source} exists")
# WHAT IS CHECKED IS THE AGGREGATION, NOT THE ROSTER. Naming the incomplete profiles here froze a state of the catalogue: the fence lot grew to six edge
# combinations, OB-010 became incomplete, and this check went red on a catalogue that had told the truth. What must hold is that the catalogue-wide list says
# exactly what each profile says, and names nobody who lacks nothing.
incomplete = {code: profile.missing("v0") for code, profile in real.profiles.items() if profile.missing("v0")}
expect(real.missing(lot="v0") == incomplete,
       f"the catalogue-wide missing list only names what is incomplete ({', '.join(incomplete) or 'nobody'})")

sandbox.unlink()
print(f"{checks} checks passed. Incomplete in v0: {', '.join(incomplete) or 'nobody'}."
      + ("" if DETAIL else " Run with -v for the walk-through."))

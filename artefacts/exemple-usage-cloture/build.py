#!/usr/bin/env python3
"""Build the review page of a usage sample: the composition plan asked for, and the image obtained.

USAGE
  python3 artefacts/exemple-usage-cloture/build.py
  Writes page.html beside this script, ready to publish.

INTENTION
  A usage sample is judged by comparison, not on its own: the only question worth asking is whether
  the image follows the plan that was asked for. The page therefore shows the two side by side, at
  the same width, and nothing else — no verdict, no commentary written in advance. The operator works
  in a terminal where no image is displayed, so this page is the only way the image reaches them.

  The plan travels as SVG, which weighs nothing; the image is embedded as data, since a published
  page can make no outside request.
"""
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLOTURE = REPO / "assets" / "poc" / "cloture"

PLAN = CLOTURE / "plan-composition-OB-010-usage.svg"
GEOMETRY = CLOTURE / "plan-composition-OB-010-usage-geometrie.svg"


def samples():
    """Every version of the sample, oldest first — nothing is thrown away, so nothing is hidden.

    A version is only judged against the one before it: what changed in the prompt shows there and
    nowhere else.
    """
    found = sorted(CLOTURE.glob("usage-OB-010*.png"))
    return [{
        "name": path.stem,
        "prompt": path.with_suffix(".txt").read_text(encoding="utf-8")
        if path.with_suffix(".txt").exists()
        else (CLOTURE / "prompt-usage-OB-010.txt").read_text(encoding="utf-8"),
        "image": "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii"),
    } for path in found]


def build() -> int:
    data = {
        "title": "Clôture OB-010 — exemple d'usage",
        "lede": ("Une seule génération, à partir du plan de composition validé. Le plan demandé et "
                 "l'image obtenue sont mis côte à côte : c'est la comparaison qui juge, pas l'image "
                 "seule."),
        # The images carry alpha; without a checker behind them, a missing background reads as white
        # and the transparency cannot be judged at all.
        "samples": samples(),
        "plan": PLAN.read_text(encoding="utf-8"),
        # The geometry is drawn from measurements taken on the produced image, so it specifies
        # something the generator has already proved it can make — not what an agent supposed.
        "geometry": GEOMETRY.read_text(encoding="utf-8") if GEOMETRY.exists() else "",
        # The joint studied on its own, large: on the whole assembly a two-unit defect is invisible,
        # and several drawings were validated wrong for exactly that reason.
        "study": (REPO / "local" / "geometrie-essai.svg").read_text(encoding="utf-8")
        if (REPO / "local" / "geometrie-essai.svg").exists() else "",
        "facts": [
            "définition demandée 1344 × 1344 px, soit 7 × 7 cases carrées",
            "25 cases de clôture, les quinze formes de tracé exercées",
            "consigne figée à côté de l'image, elle ne sera plus réécrite",
        ],
    }

    template = (HERE / "template.html").read_text(encoding="utf-8")
    page = template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (HERE / "page.html").write_text(page, encoding="utf-8")

    print(f"page écrite : {(HERE / 'page.html').stat().st_size / 1024:.0f} Ko")

    return 0


if __name__ == "__main__":
    raise SystemExit(build())

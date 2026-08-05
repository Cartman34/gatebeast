#!/usr/bin/env python3
"""Build the gallery of every usage-example image produced so far.

USAGE
  python3 artefacts/exemples-usage/build.py
  Writes page.html beside this script, ready to publish.

INTENTION
  A usage example is a style-reference image — one subject alone, meant to be judged against the
  composition plan that asked for it, never used as a sprite. The operator works in a terminal where
  no image renders, so this page is the only way any of these images reach them. It used to show only
  the fence; it now discovers every "usage-*.png" under assets/poc/, grouped by the subject it shows,
  each next to its composition plan when one exists — so a usage example produced tomorrow appears
  without touching this file. Nothing here is a hand-written list.

  The whole page is rendered as static HTML by this script, not built in the browser from a data
  blob: a page whose content only exists once a script runs is not robust — if that script fails to
  run in the viewer, for any reason, the page shows nothing (this happened once already, on the
  inventory-audit page; see execution.md, "On ne corrige pas ce qu'on n'a pas expliqué").

  The images are heavy (1344x1344 RGBA, hundreds of kB each): the page embeds a resized thumbnail —
  double its displayed width, for dense screens — never the original file. Pillow is already part of
  this project's toolchain (scripts/resize-image.py, scripts/build-thumbnails.py); this reuses the
  same resizing approach rather than inventing a second one.
"""
import base64
import html
import io
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ASSETS = REPO / "assets"
POC = ASSETS / "poc"
INVENTAIRE = REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"

# usage-OB-010.png, usage-OB-010-v2.png, usage-CH-019.png...
SAMPLE_PATTERN = re.compile(r"^usage-([A-Z]{2,3}-\d{3})(?:-v(\d+))?\.png$")

# The image is shown at this CSS width; the embedded thumbnail is rendered wider, so a dense
# (retina) screen still gets a sharper image without embedding the full 1344 px original. 1.5x
# was chosen by measurement: 2x roughly doubled the page's total weight (2.3 MB vs 1.3 MB across
# today's four examples) for a sharpness gain a style-reference thumbnail does not need.
DISPLAY_WIDTH = 420
THUMBNAIL_WIDTH = round(DISPLAY_WIDTH * 1.5)


def escape(text: str) -> str:
    """Shorthand: HTML-escape a piece of French text before it goes into the page."""
    return html.escape(text, quote=True)


def discover_samples() -> dict[str, list[tuple[int, Path]]]:
    """Every usage example on disk, grouped by the subject code it shows and sorted oldest first
    within a subject. An unmarked file (no "-vN") is the first version — it was written before any
    later version existed to be numbered against."""
    grouped: dict[str, list[tuple[int, Path]]] = {}
    for path in sorted(POC.rglob("usage-*.png")):
        match = SAMPLE_PATTERN.match(path.name)
        if not match:
            continue
        code, version = match.group(1), int(match.group(2) or 1)
        grouped.setdefault(code, []).append((version, path))
    for versions in grouped.values():
        versions.sort(key=lambda item: item[0])
    return grouped


def find_plan_svg(code: str) -> str | None:
    """The composition plan that produced this subject's usage examples, if one was declared —
    same naming the plan-composition tool itself writes."""
    matches = sorted(POC.rglob(f"plan-composition-{code}-usage.svg"))
    return matches[0].read_text(encoding="utf-8") if matches else None


def find_label(code: str) -> str | None:
    """The plain-language name of a subject, read from the inventory rather than guessed — e.g.
    "barrière en rondins" for OB-010. Absent if the code is not (yet) listed there."""
    pattern = re.compile(rf"\*\*{re.escape(code)}\s+([^*]+)\*\*")
    for path in sorted(INVENTAIRE.glob("*.md")):
        match = pattern.search(path.read_text(encoding="utf-8"))
        if match:
            return match.group(1).strip()
    return None


def make_thumbnail(path: Path) -> str:
    """A resized copy of the image, embedded as a data URI — never the original file, which would
    make the page itself as heavy as the images it shows."""
    with Image.open(path) as image:
        if image.width > THUMBNAIL_WIDTH:
            height = round(image.height * THUMBNAIL_WIDTH / image.width)
            image = image.resize((THUMBNAIL_WIDTH, height), Image.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def render_plan(svg: str) -> str:
    """The composition plan, inserted as real markup (not an <img>) so it stays sharp at any size —
    it is vector, produced by our own tool, not user input."""
    return f'<figure class="plan"><figcaption>Plan de composition</figcaption>{svg}</figure>'


def render_version(code: str, version: int, path: Path) -> str:
    """One image: its thumbnail, and which version of that subject's usage example it is.

    The thumbnail's data URI is written once — an <a href="..."> wrapper for a click-to-enlarge
    affordance would repeat the same base64 text a second time in the page, doubling its weight for
    a gesture that only reveals the same resolution again."""
    label = f"Version {version}"
    alt = escape(f"Exemple d'usage de {code}, {label.lower()}")
    return f"""
<figure class="sample">
  <figcaption>{escape(label)}<span>{escape(path.name)}</span></figcaption>
  <div class="frame"><img src="{make_thumbnail(path)}" alt="{alt}" width="{DISPLAY_WIDTH}"></div>
</figure>"""


def render_subject(code: str, versions: list[tuple[int, Path]]) -> str:
    """One subject: its code, its plain-language name if the inventory has one, its composition
    plan if it was declared, and every usage example produced for it, oldest first."""
    label = find_label(code)
    heading = f"{code} — {label}" if label else code
    plan_svg = find_plan_svg(code)
    plan_html = render_plan(plan_svg) if plan_svg else ""
    samples_html = "".join(render_version(code, version, path) for version, path in versions)
    return f"""
<section class="subject">
  <h2>{escape(heading)}</h2>
  <div class="gallery">
    {plan_html}
    {samples_html}
  </div>
</section>"""


def build() -> int:
    grouped = discover_samples()
    if not grouped:
        raise SystemExit(f"No usage example found under {POC} — nothing to publish.")

    body = "".join(render_subject(code, versions) for code, versions in sorted(grouped.items()))
    template = (HERE / "exemples-usage.html").read_text(encoding="utf-8")
    page = template.replace("__BODY__", body)
    (HERE / "page.html").write_text(page, encoding="utf-8")

    total_versions = sum(len(versions) for versions in grouped.values())
    print(f"sujets {len(grouped)} · exemples {total_versions}")
    for code, versions in sorted(grouped.items()):
        print(f"  {code}: {len(versions)} exemple(s)")
    print(f"page écrite : {(HERE / 'page.html').stat().st_size / 1024:.0f} Ko")

    return 0


if __name__ == "__main__":
    raise SystemExit(build())

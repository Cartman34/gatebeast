#!/usr/bin/env python3
"""Build the human-scale calibration review page: every attempt, its grid, its measures, its prompt."""
import base64
import io
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "revue-da"
TILES_X, TILES_Y = 16, 8

ATTEMPTS = [
    ("calibration-humains", "Essai 1 — pixels absolus, consigne en anglais",
     "Hauteurs demandées en pixels (96 px debout). Résultat : tout est 1,5 à 2 fois trop grand.",
     [("homme debout", "2 cases", "3,12"), ("femme debout", "2 cases", "3,10"),
      ("enfant debout", "~1,25", "2,48"), ("homme assis", "~1,25", "2,33"),
      ("largeur max", "1 case", "1,94")]),
    ("calibration-humains-v2", "Essai 2 — rapports d'image, consigne en français",
     "« Les humains doivent sembler petits », tailles en fractions de la hauteur d'image. Résultat : "
     "légèrement trop petit (~0,85×), largeurs tenues.",
     [("homme debout", "2 cases", "1,69"), ("femme debout", "2 cases", "1,65"),
      ("enfant debout", "~1,25", "1,38"), ("homme assis", "~1,25", "1,46"),
      ("largeur max", "1 case", "1,00")]),
    ("calibration-humains-v3", "Essai 3 — même homme debout et assis, rapport ajusté",
     "L'assis est le même fermier que le debout ; adultes visés dans la fourchette 1,75–2 cases "
     "(« un petit tiers » de la hauteur d'image). Résultat : 1,71–1,73 — à un cheveu du plancher.",
     [("homme debout", "1,75–2 cases", "1,73"), ("femme debout", "1,75–2", "1,71"),
      ("enfant debout", "plus petit", "1,40"), ("le même homme, assis", "plus bas", "1,42"),
      ("largeur max", "1 case", "1,04")]),
    ("calibration-humains-v4", "Essai 4 — huit personnages, debout et assis",
     "3 hommes, 3 femmes, 2 enfants ; rangée haute debout, rangée basse les mêmes assis. Adultes "
     "debout tous DANS la fourchette 1,75–2 cases.",
     [("adultes debout (6)", "1,75–2 cases", "1,90–1,96"), ("les mêmes assis", "plus bas", "1,38–1,58"),
      ("enfants debout (2)", "~1,25", "1,56–1,69"), ("largeur max", "1 case", "1,12 (fermier)")]),
]


def encode(path: Path) -> str:
    image = Image.open(path).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('ascii')}"


def section(key: str, title: str, note: str, rows: list) -> str:
    path = ASSETS / f"{key}.png"
    # The grid adapts to each attempt's frame: one tile is 48 px on the source image.
    with Image.open(path) as source:
        tiles_x, tiles_y = source.width // 48, source.height // 48
    prompt_path = ASSETS / f"prompt-{key}.txt"
    prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
    prompt = prompt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = "".join(f"<tr><td>{name}</td><td>{target}</td><td>{measured}</td></tr>"
                    for name, target, measured in rows)
    return f"""
    <section>
      <h2>{title}</h2>
      <p class="note">{note}</p>
      <div class="cadre"><img src="{encode(path)}" alt="{title}"><div class="grille"
        style="background-size:calc(100% / {tiles_x}) calc(100% / {tiles_y});"></div></div>
      <p class="legende"><strong>{path.name}</strong> — grille {tiles_x} × {tiles_y} cases affichée ;
        un adulte debout doit tenir entre 1,75 et 2 cases de haut, 1 case de large.</p>
      <table><tr><th>figure</th><th>cible</th><th>mesuré (cases)</th></tr>{lines}</table>
      <details><summary>Consigne exacte — {len(prompt)} caractères</summary><pre>{prompt}</pre></details>
    </section>"""


# Most recent attempt first: the owner reads the latest state at the top.
SECTIONS = "\n".join(section(*attempt) for attempt in reversed(ATTEMPTS))

PAGE = f"""<title>GateBeast — Calibration de l'échelle humaine</title>
<style>
  :root{{--fond:#fbf8f3; --fond2:#fff; --encre:#1d1a24; --doux:#6b6478; --trait:#e3ddd2;
    --accent:#0f8f8f;}}
  @media (prefers-color-scheme:dark){{:root{{--fond:#15131a; --fond2:#1e1b25; --encre:#f2eee8;
    --doux:#a49dae; --trait:#312c3b; --accent:#3fc3bd;}}}}
  :root[data-theme="dark"]{{--fond:#15131a; --fond2:#1e1b25; --encre:#f2eee8; --doux:#a49dae;
    --trait:#312c3b; --accent:#3fc3bd;}}
  :root[data-theme="light"]{{--fond:#fbf8f3; --fond2:#fff; --encre:#1d1a24; --doux:#6b6478;
    --trait:#e3ddd2; --accent:#0f8f8f;}}
  body{{background:var(--fond); color:var(--encre); font:16px/1.6 ui-sans-serif,system-ui,sans-serif;
    margin:0; padding:2.5rem 1.25rem 4rem;}}
  .page{{max-width:1100px; margin:0 auto;}}
  h1{{font-size:1.8rem; margin:0 0 .3rem;}}
  .sous{{color:var(--doux); margin:0 0 2rem;}}
  section{{background:var(--fond2); border:1px solid var(--trait); border-radius:.9rem;
    padding:1.2rem; margin-bottom:2rem;}}
  h2{{margin:0 0 .3rem; font-size:1.2rem;}}
  .note{{color:var(--doux); margin:0 0 .8rem;}}
  .cadre{{position:relative; line-height:0;}}
  .cadre img{{width:100%; display:block; border-radius:.4rem;}}
  .grille{{position:absolute; inset:0; pointer-events:none;
    background-image:linear-gradient(to right, rgba(255,0,90,.55) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255,0,90,.55) 1px, transparent 1px);
    background-size:calc(100% / {TILES_X}) calc(100% / {TILES_Y});}}
  .legende{{font-size:.85rem; color:var(--doux);}}
  table{{border-collapse:collapse; font-size:.9rem; margin:.6rem 0 1rem;}}
  th,td{{border:1px solid var(--trait); padding:.3rem .8rem; text-align:left;}}
  details{{font-size:.85rem; color:var(--doux);}}
  summary{{cursor:pointer; color:var(--accent);}}
  pre{{white-space:pre-wrap; background:var(--fond); border:1px solid var(--trait);
    border-radius:.5rem; padding:.7rem .8rem; font-size:.78rem; max-height:24rem; overflow:auto;}}
  @media (max-width: 900px){{
    body{{padding:1.2rem .6rem 2.5rem; font-size:15px;}}
    section{{padding:.8rem;}}
    table{{display:block; overflow-x:auto;}}
  }}
</style>
<div class="page">
  <h1>Calibration de l'échelle humaine</h1>
  <p class="sous">Essais successifs pour obtenir des humains à 2 cases debout, grille affichée
    (1 case = 1 mètre). Quatre figures : homme debout, femme debout, enfant debout, homme assis.</p>
{SECTIONS}
</div>
"""

target = ASSETS / "revue-calibration.html"
target.write_text(PAGE, encoding="utf-8")
print(f"OK {target} {round(target.stat().st_size / 1024)} KB")

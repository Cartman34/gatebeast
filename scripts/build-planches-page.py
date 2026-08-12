#!/usr/bin/env python3
"""Build the reference plates review page.

Plates are large and detailed, so each one is shown full width, zoomable, with the tile grid available as
an overlay and its generation prompt readable underneath. Answers are kept in the browser.
"""
import base64
import io
import json
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "revue-da"

TILES_X, TILES_Y = 32, 24

# The world map: two rows of three, exactly as planned. A plate not yet produced keeps its place.
SERIES = [
    ("Série en cours", [
        [("p1-campagne-v8", "P1 — Campagne boisée",
          "Meilleures mesures du lot : lumière 122,8 / 3,9 % et saturation 77,1, au-dessus de la "
          "référence. Route du sud et ru enfin parallèles à une case d'écart, tous deux coupés par le "
          "bord bas. Réserves : SP-010 reste un cerf réel, SP-008 vire au faon, une voie court encore "
          "sous la chaumière."),
         ("p2-bourg-v7", "P2 — Bourg",
          "Première planche à tenir la cible de lumière (121,6 / 7,8 %). Règle des pavés appliquée : "
          "chaque ensemble bâti est ceinturé et relié au réseau, l'herbe occupe le reste. SP-001 et "
          "SP-005 enfin conformes. Réserves : SP-011 reste chevalin, charge 94 % (le pavage texturé "
          "gonfle la mesure), saturation 61,5."),
         ("p3-contreforts-v6", "P3 — Contreforts",
          "DE VRAIS PINS enfin obtenus (tronc roux nu, houppier en parasol) en décrivant l'arbre forme "
          "par forme. Lumière dans la cible (125,2 / 5,5 %), crevasse et enclos conservés. Réserves : "
          "bergerie encore sous son emprise, raccord gauche rangée 8 absent, saturation 52,6.")],
        [("p4-marais-v8", "P4 — Marais",
          "Lumière dans la cible (125,5 / 2,3 %) : eau turquoise éclatante, feuillage clair. "
          "L'escalier de la seconde hutte aboutit sur la passerelle, plus une marche dans l'eau. "
          "Réserve : SP-017 dessinée en plusieurs exemplaires, saturation 60,1."),
         ("p5-falaise-v5", "P5 — Falaise",
          "L'escalier taillé est enfin dessiné — marches de granite et main courante — en lui donnant "
          "sa propre emprise. Plateau rempli par masses listées : charge de 43,8 à 75,8 %. Lumière "
          "124,5 / 1,0 %. Réserves : SP-001 rendu en renard réel, SP-002 en double, saturation 58,0."),
         ("p6-plage-v5", "P6 — Plage",
          "Trois défauts de v4 traités : densité (habillage à une case sur trois, massifs littoraux "
          "élargis, laisse de mer), lumière (sable doré soutenu, jamais de blanc brûlé), chemins "
          "(les huit segments martelés comme les seuls, rappelés en fin de consigne). Échelle humaine "
          "rappelée à côté de chaque personnage.")],
    ]),
]

PLATES = [plate for _, rows in SERIES for row in rows for plate in row]


def encode(path: Path, width: int, quality: int) -> str:
    image = Image.open(path).convert("RGB")
    if image.width > width:
        height = round(image.height * width / image.width)
        image = image.resize((width, height), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)

    return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode('ascii')}"


def meta(path: Path) -> str:
    if not path.is_file():
        return "Planche en cours de génération"
    width, height = Image.open(path).size
    exact = "exact" if width % TILES_X == 0 and height % TILES_Y == 0 else "NON ENTIER"

    return (f"<strong>{path.name}</strong> &nbsp;·&nbsp; {width} × {height} px &nbsp;·&nbsp; "
            f"{TILES_X} × {TILES_Y} cases &nbsp;·&nbsp; "
            f"{width / TILES_X:.0f} px par case ({exact}) &nbsp;·&nbsp; cliquez pour agrandir")


def prompt(key: str) -> str:
    path = ASSETS / f"prompt-{key}.txt"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return (f'<details class="consigne"><summary>Consigne de génération — {len(text)} caractères</summary>'
            f'<pre>{escaped}</pre></details>')


def plan(key: str) -> str:
    """The composition plan: what was asked, to compare with what was produced. SVG when it exists
    (layout of elements and their bounds, per the operator), ASCII kept as fallback."""
    stem = re.sub(r"-v\d+$", "", key)
    svg = ASSETS / f"plan-{stem}.svg"
    if svg.is_file():
        return (f'<details class="consigne"><summary>Plan de la composition — ce qui était demandé'
                f'</summary><div class="plan-svg">{svg.read_text(encoding="utf-8")}</div></details>')
    path = ASSETS / f"plan-{stem}.txt"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")

    return (f'<details class="consigne"><summary>Plan de la composition — ce qui était demandé</summary>'
            f'<pre class="plan">{text}</pre></details>')


def report(key: str) -> str:
    """The plate's report: the score alone by default, the full table one click away.

    Built by build-plate-reports.py — mechanical checks recomputed from the image and the prompt, eye
    observations carried as data. The page only renders what that script wrote.
    """
    path = ASSETS / f"rapport-{key}.json"
    if not path.is_file():
        return ""
    data = json.loads(path.read_text(encoding="utf-8"))
    passed, total = data["score"]["reussis"], data["score"]["total"]
    share = passed / total if total else 0
    shade = "bon" if share >= 0.8 else ("moyen" if share >= 0.6 else "faible")
    mark = {"ok": ("réussi", "ok"), "faute": ("échec", "faute"),
            "remarque": ("remarque", "remarque")}

    rows = []
    for check in data["mecanique"]:
        label, css = mark[check["verdict"]]
        reading = f'<br><span class="lecture">{check["note"]}</span>' if check["note"] else ""
        rows.append(
            f'<tr><td>{check["nom"]}</td><td><span class="pastille {css}">{label}</span></td>'
            f'<td>{check["mesure"]}{reading}</td><td>{check["cible"]}</td></tr>')
    observations = []
    for view in data["critique"]:
        label, css = mark[view["verdict"]]
        observations.append(
            f'<tr><td>{view["nom"]}</td><td><span class="pastille {css}">{label}</span></td>'
            f'<td>{view["note"]}</td></tr>')

    return f"""<details class="consigne rapport">
        <summary><span class="score {shade}">{passed}/{total}</span> Rapport de la planche —
          {passed} contrôles réussis sur {total}</summary>
        <h4>Vérification mécanique</h4>
        <table><thead><tr><th>Contrôle</th><th>Résultat</th><th>Mesure</th><th>Cible</th></tr></thead>
          <tbody>{"".join(rows)}</tbody></table>
        <h4>Passe critique</h4>
        <table><thead><tr><th>Observation</th><th>Résultat</th><th>Détail</th></tr></thead>
          <tbody>{"".join(observations)}</tbody></table>
      </details>"""


def section(key: str, name: str, note: str) -> str:
    path = ASSETS / f"planche-{key}.png"
    pending = not path.is_file()
    plan_svg = ASSETS / f"plan-{re.sub(r'-v[0-9]+$', '', key)}.svg"
    # No image yet but a plan exists: the plan takes the image's place, and the review controls stay
    # active — the operator gives feedback on the plan before any generation.
    plan_as_visual = pending and plan_svg.is_file()
    disabled = " disabled" if pending and not plan_as_visual else ""
    if not pending:
        visuel = f'<img src="{encode(path, 1500, 82)}" alt="{name}">'
    elif plan_as_visual:
        visuel = f'<div class="plan-visuel">{plan_svg.read_text(encoding="utf-8")}</div>'
    else:
        visuel = ('<svg class="attente" viewBox="0 0 32 24"><rect width="32" height="24" '
                  'fill="currentColor" opacity="0.06"/><text x="16" y="12" text-anchor="middle" '
                  'font-size="1.4" fill="currentColor" fill-opacity="0.5">génération en cours</text></svg>')

    return f"""
    <section class="planche{' en-attente' if pending else ''}">
      <header>
        <span class="code">{key.upper()}</span>
        <p class="titre">{name}</p>
      </header>
      <figure>
        <div class="cadre">{visuel}<div class="grille-calque" hidden></div></div>
        <figcaption>{"<strong>" + plan_svg.name + "</strong> &nbsp;·&nbsp; planche non générée — "
                     "plan de composition affiché, vos retours dessus sont bienvenus"
                     if plan_as_visual else meta(path)}</figcaption>
      </figure>
      <div class="corps">
        <p class="note">{note}</p>
        {"" if plan_as_visual else
         f'<button class="comparer" data-comparer="{key}"{disabled}>Comparer à la référence</button>'}
        <div class="choix">
          <label><input type="radio" name="v-{key}" value="Retenir"{disabled}><span>Retenir</span></label>
          <label><input type="radio" name="v-{key}" value="À retravailler"{disabled}><span>À retravailler</span></label>
          <label><input type="radio" name="v-{key}" value="Écarter"{disabled}><span>Écarter</span></label>
        </div>
        <textarea data-note="{key}" placeholder="Dire pourquoi — ce qui accroche, ce qui gêne."{disabled}></textarea>
      </div>
      {"" if plan_as_visual else report(key)}
      {"" if plan_as_visual else plan(key)}
      {prompt(key)}
    </section>"""


VIEWS = "\n".join(
    f'<h2 class="serie">{titre}</h2>\n<div class="carte-monde">'
    + "\n".join(section(key, name, note) for row in rows for key, name, note in row)
    + "</div>"
    for titre, rows in SERIES
)
REFERENCE = (f'<img src="{encode(ASSETS / "da-b4-r15-scene.png", 1500, 82)}" '
             f'alt="Image de référence de la direction artistique">')
ORIGINE = (f'<img src="{encode(ASSETS / "da-gb-b4v6-scene.png", 1500, 82)}" '
           f'alt="Référence d\'origine de la direction artistique">')
# Every re-run of the reference prompt (da-b4-r15-scene-b, -c, ...), shown only in the comparison
# overlay opened from the RÉFÉRENCE DA block — never on the base page.
RETIRAGES = "\n".join(
    f'<figure><img src="{encode(path, 1500, 82)}" alt="Retirage {path.stem}">'
    f'<figcaption><strong>{path.name}</strong></figcaption></figure>'
    for path in sorted(ASSETS.glob("da-b4-r15-scene-*.png"))
)
CATALOGUE = json.dumps([{"cle": key, "nom": name} for key, name, _ in PLATES], ensure_ascii=False)

PAGE = f"""<title>GateBeast — Planches de référence</title>
<style>
  :root{{--fond:#fbf8f3; --fond2:#fff; --encre:#1d1a24; --doux:#6b6478; --trait:#e3ddd2; --accent:#0f8f8f;}}
  @media (prefers-color-scheme:dark){{:root{{--fond:#15131a; --fond2:#1e1b25; --encre:#f2eee8;
    --doux:#a49dae; --trait:#312c3b; --accent:#3fc3bd;}}}}
  :root[data-theme="dark"]{{--fond:#15131a; --fond2:#1e1b25; --encre:#f2eee8; --doux:#a49dae;
    --trait:#312c3b; --accent:#3fc3bd;}}
  :root[data-theme="light"]{{--fond:#fbf8f3; --fond2:#fff; --encre:#1d1a24; --doux:#6b6478;
    --trait:#e3ddd2; --accent:#0f8f8f;}}
  body{{background:var(--fond); color:var(--encre); font:16px/1.6 ui-sans-serif,system-ui,-apple-system,
    "Segoe UI",sans-serif; margin:0; padding:2.5rem 1.25rem 7rem;}}
  .page{{max-width:3400px; margin:0 auto;}}
  .grille-planches{{display:grid; gap:1.5rem; grid-template-columns:repeat(auto-fit,minmax(680px,1fr));}}
  /* The world map: three columns, so a plate sits where it belongs on the map. */
  .carte-monde{{display:grid; gap:1rem; grid-template-columns:repeat(3,1fr); margin:0 0 2.5rem;}}
  .serie{{font-size:1.25rem; margin:2rem 0 .8rem;}}
  .reference{{background:var(--fond2); border:1px solid var(--accent); border-radius:.9rem;
    overflow:hidden; margin:0;}}
  .bandeau-reference{{margin-bottom:1.5rem; grid-template-columns:1fr 1fr;}}
  .comparer{{background:transparent; color:var(--accent); border:1px solid var(--trait);
    border-radius:.5rem; padding:.35rem .8rem; font:inherit; font-size:.85rem; cursor:pointer;
    margin:0 0 .7rem;}}
  #face-a-face, #retirages{{position:fixed; inset:0; z-index:60; background:rgba(0,0,0,.94);
    display:none; padding:1rem; overflow:auto;}}
  #face-a-face.visible, #retirages.visible{{display:block;}}
  #retirages .duo{{display:grid; grid-template-columns:1fr 1fr; gap:.8rem; align-items:start;}}
  #retirages img{{width:100%; display:block; border-radius:.4rem;}}
  #retirages figure{{margin:0 0 .8rem;}}
  #retirages figcaption{{color:#fff; opacity:.75; font-size:.85rem; padding:.3rem 0;}}
  #retirages .fermer{{position:sticky; top:0; float:right; z-index:2;}}
  #retirages .duo > figure{{position:sticky; top:0;}}
  #face-a-face .duo{{display:grid; grid-template-columns:1fr 1fr; gap:.8rem; align-items:start;}}
  #face-a-face img{{width:100%; display:block; border-radius:.4rem;}}
  #face-a-face figcaption{{color:#fff; opacity:.75; font-size:.85rem; padding:.3rem 0;}}
  #face-a-face .fermer{{position:sticky; top:0; float:right; z-index:2;}}
  .reference header{{padding:1rem 1.2rem .4rem;}}
  .reference .cadre img{{cursor:zoom-in;}}
  .reference-corps{{padding:.4rem 1.2rem 1.2rem; color:var(--doux); font-size:.95rem;}}
  h1{{font-size:1.9rem; margin:0 0 .3rem; letter-spacing:-.02em;}}
  .sous{{color:var(--doux); margin:0 0 .4rem;}}
  .cachet{{color:var(--doux); font-size:.85rem; font-variant:all-small-caps; letter-spacing:.06em;}}
  .rappel{{background:var(--fond2); border:1px solid var(--trait); border-left:3px solid var(--accent);
    border-radius:.6rem; padding:.9rem 1.1rem; margin:1.6rem 0 2.2rem;}}
  .rappel p{{margin:.3rem 0;}}
  .planche{{background:var(--fond2); border:1px solid var(--trait); border-radius:.9rem; overflow:hidden;
    margin-bottom:2rem;}}
  .planche header{{padding:1rem 1.2rem .4rem;}}
  .code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.78rem; color:var(--accent);
    letter-spacing:.04em;}}
  .titre{{font-size:1.2rem; font-weight:650; margin:.1rem 0 0;}}
  figure{{margin:0;}}
  .cadre{{position:relative; line-height:0;}}
  .cadre img{{width:100%; display:block; cursor:zoom-in; background:#fff;}}
  .attente{{width:100%; display:block; color:var(--encre);}}
  .grille-calque{{position:absolute; inset:0; pointer-events:none;
    background-image:linear-gradient(to right, rgba(255,0,90,.5) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255,0,90,.5) 1px, transparent 1px);
    background-size:calc(100% / {TILES_X}) calc(100% / {TILES_Y});}}
  figcaption{{font-size:.75rem; color:var(--doux); padding:.4rem 1.2rem; font-variant:all-small-caps;
    letter-spacing:.06em;}}
  .corps{{padding:.4rem 1.2rem 1.2rem;}}
  .note{{color:var(--doux); font-size:.95rem; margin:0 0 .7rem;}}
  .choix{{display:flex; flex-wrap:wrap; gap:.5rem; margin:0 0 .7rem;}}
  .choix label{{border:1px solid var(--trait); border-radius:2rem; padding:.28rem .85rem; font-size:.88rem;
    cursor:pointer; user-select:none;}}
  .choix input{{margin-right:.35rem; accent-color:var(--accent);}}
  .choix input:checked+span{{font-weight:650; color:var(--accent);}}
  textarea{{width:100%; box-sizing:border-box; min-height:3.6rem; resize:vertical; padding:.6rem .7rem;
    border:1px solid var(--trait); border-radius:.5rem; background:var(--fond); color:var(--encre);
    font:inherit; font-size:.9rem;}}
  .consigne{{margin:0 1.2rem 1rem; font-size:.85rem; color:var(--doux);}}
  .consigne summary{{cursor:pointer; color:var(--accent);}}
  /* The plate report: the score is the whole summary, the tables live behind the fold. */
  .rapport summary{{color:var(--encre); font-weight:600;}}
  .score{{display:inline-block; min-width:3.1rem; text-align:center; border-radius:.4rem;
    padding:.1rem .4rem; margin-right:.5rem; font-variant-numeric:tabular-nums; color:#fff;}}
  .score.bon{{background:#2e8b57;}} .score.moyen{{background:#c98a1e;}} .score.faible{{background:#c0392b;}}
  .rapport table{{width:100%; border-collapse:collapse; margin:.3rem 0 1rem; font-size:.8rem;}}
  .rapport th{{text-align:left; font-weight:600; border-bottom:1px solid var(--trait);
    padding:.35rem .4rem; color:var(--encre);}}
  .rapport td{{border-bottom:1px solid var(--trait); padding:.35rem .4rem; vertical-align:top;}}
  .rapport h4{{margin:.9rem 0 .1rem; font-size:.9rem; color:var(--encre);}}
  .lecture{{font-size:.72rem; opacity:.8; font-style:italic;}}
  .pastille{{display:inline-block; border-radius:2rem; padding:.05rem .5rem; font-size:.72rem;
    white-space:nowrap; color:#fff;}}
  .pastille.ok{{background:#2e8b57;}} .pastille.faute{{background:#c0392b;}}
  .pastille.remarque{{background:#8a8296;}}
  .plan{{font-size:.72rem; line-height:1.15; letter-spacing:.04em; max-height:none;}}
  .plan-svg{{background:var(--fond); border:1px solid var(--trait); border-radius:.5rem;
    padding:.5rem;}}
  .plan-svg svg{{width:100%; height:auto; display:block;}}
  .plan-visuel{{line-height:0;}}
  .plan-visuel svg{{width:100%; height:auto; display:block;}}
  .consigne pre{{white-space:pre-wrap; background:var(--fond); border:1px solid var(--trait);
    border-radius:.5rem; padding:.7rem .8rem; font-size:.78rem; max-height:22rem; overflow:auto;}}
  .zone-recap{{margin-top:2.4rem; border-top:1px solid var(--trait); padding-top:1.2rem;}}
  #recap{{width:100%; box-sizing:border-box; margin-top:1rem; min-height:8rem;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.82rem;}}
  .barre{{position:fixed; left:0; right:0; bottom:0; z-index:20; display:flex; flex-wrap:wrap; gap:.8rem;
    align-items:center; padding:.7rem 1.25rem; background:var(--fond2); border-top:1px solid var(--trait);
    box-shadow:0 -6px 20px rgba(0,0,0,.08);}}
  button{{background:var(--accent); color:#fff; border:0; border-radius:.5rem; padding:.6rem 1.15rem;
    font:inherit; font-weight:600; cursor:pointer;}}
  button.secondaire{{background:transparent; color:var(--accent); border:1px solid var(--trait);}}
  #etat{{color:var(--doux); font-size:.88rem;}}
  #loupe{{position:fixed; inset:0; z-index:50; background:rgba(0,0,0,.9); display:none;
    align-items:center; justify-content:center; padding:1rem; cursor:zoom-out; overflow:auto;}}
  #loupe.visible{{display:flex;}}
  #loupe img{{max-width:none; width:auto; height:auto;}}
  /* Mobile: one column everywhere, tighter paddings, stacked comparisons. */
  @media (max-width: 900px){{
    body{{padding:1.2rem .6rem 7rem; font-size:15px;}}
    .carte-monde{{grid-template-columns:1fr;}}
    .grille-planches, .bandeau-reference{{grid-template-columns:1fr;}}
    #face-a-face .duo, #retirages .duo{{grid-template-columns:1fr;}}
    #retirages .duo > figure{{position:static;}}
    .barre{{gap:.4rem; padding:.5rem .6rem;}}
    .barre button{{padding:.45rem .7rem; font-size:.85rem;}}
    #etat{{flex-basis:100%;}}
  }}
</style>

<div class="page">
  <h1>GateBeast — Planches de référence</h1>
  <p class="sous">Six planches de biomes différents, sans élément commun, pour figer la direction
    artistique sur beaucoup de contenu. Les deux premières sont adjacentes et partagent un chemin.</p>
  <p class="cachet">Premier jet — bourg et campagne</p>

  <div class="rappel">
    <p><strong>Ce qui se juge ici</strong> : la tenue de la direction artistique sur du contenu abondant et
      varié, et la cohérence interne de chaque planche — rien qui se termine dans le vide.</p>
    <p><strong>Ce qui ne se juge pas</strong> : le choix de la direction, déjà tranché en faveur du toon
      volume. Ces planches servent à le figer, pas à le rejouer.</p>
    <p><strong>À venir</strong> : contreforts, marais, falaise et plage, dont l'inventaire est déjà rédigé.</p>
  </div>

  <div class="grille-planches bandeau-reference">
  <section class="reference">
    <header>
      <span class="code">RÉFÉRENCE DA</span>
      <p class="titre">La direction artistique retenue</p>
    </header>
    <figure><div class="cadre">{REFERENCE}<div class="grille-calque" hidden></div></div>
      <figcaption><strong>da-b4-r15-scene.png</strong></figcaption></figure>
    <div class="reference-corps">Toon volume : volumes sculptés, ombrage en deux bandes nettes, sans
      contour, couleurs franches. C'est le rendu que toutes les planches doivent reproduire — elles se
      jugent par rapport à lui, jamais entre elles.
      <div><button class="comparer" id="voir-retirages">Voir les retirages</button></div>
    </div>
    {prompt("b4-r15-scene")}
  </section>
  <section class="reference">
    <header>
      <span class="code">RÉF D'ORIGINE</span>
      <p class="titre">La référence d'origine — image du tour 6</p>
    </header>
    <figure><div class="cadre">{ORIGINE}<div class="grille-calque" hidden></div></div>
      <figcaption><strong>da-gb-b4v6-scene.png</strong></figcaption></figure>
    <div class="reference-corps">da-gb-b4v6-scene : l'image sur laquelle la consigne de la référence DA
      s'ancre. C'est la vraie référence de fond — végétation dense, couleurs franches et riches.</div>
  </section>
  </div>

{VIEWS}

  <div class="zone-recap">
    <h2>Votre récapitulatif</h2>
    <p>Il se met à jour tout seul. Vos réponses sont conservées dans ce navigateur.</p>
    <textarea id="recap" readonly></textarea>
  </div>
</div>

<div class="barre">
  <button id="grille" class="secondaire">Afficher la grille</button>
  <button id="copier">Copier le récapitulatif</button>
  <button id="recharger" class="secondaire">Rafraîchir</button>
  <span id="etat"></span>
</div>

<div id="loupe"><img alt=""></div>

<div id="retirages">
  <button class="fermer" id="fermer-retirages">Fermer</button>
  <div class="duo">
    <figure><img src="{encode(ASSETS / 'da-b4-r15-scene.png', 1500, 82)}"
      alt="Référence de la direction artistique">
      <figcaption><strong>da-b4-r15-scene.png</strong> — la référence en service</figcaption></figure>
    <div class="colonne-retirages">{RETIRAGES}</div>
  </div>
</div>

<div id="face-a-face">
  <button class="fermer" id="fermer-duo">Fermer</button>
  <div class="duo">
    <figure><img id="duo-reference" alt="Référence de la direction artistique">
      <figcaption>Référence — la direction artistique retenue</figcaption></figure>
    <figure><img id="duo-planche" alt="Planche comparée">
      <figcaption id="duo-titre"></figcaption></figure>
  </div>
</div>

<script>
  const planches = {CATALOGUE};
  const recap = document.getElementById('recap');
  const etat = document.getElementById('etat');
  const STOCKAGE = 'gatebeast-planches-v1';

  function construire(){{
    const lignes = ['Revue planches GateBeast', ''];
    let repondues = 0;
    for(const planche of planches){{
      const choisi = document.querySelector('input[name="v-' + planche.cle + '"]:checked');
      const note = document.querySelector('textarea[data-note="' + planche.cle + '"]').value.trim();
      if(choisi){{ repondues++; }}
      lignes.push(planche.nom + ' : ' + (choisi ? choisi.value : 'sans réponse'));
      if(note){{ lignes.push('  parce que ' + note); }}
    }}
    return {{texte:lignes.join('\\n'), repondues:repondues}};
  }}

  function rafraichir(){{
    const resultat = construire();
    recap.value = resultat.texte;
    etat.textContent = resultat.repondues + ' planche(s) sur ' + planches.length + ' renseignée(s).';
  }}

  function enregistrer(){{
    const etatReponses = {{}};
    for(const planche of planches){{
      const choisi = document.querySelector('input[name="v-' + planche.cle + '"]:checked');
      etatReponses[planche.cle] = {{
        verdict: choisi ? choisi.value : '',
        note: document.querySelector('textarea[data-note="' + planche.cle + '"]').value,
      }};
    }}
    try{{ localStorage.setItem(STOCKAGE, JSON.stringify(etatReponses)); }}catch(erreur){{ /* ignoré */ }}
  }}

  function restaurer(){{
    let etatReponses = null;
    try{{ etatReponses = JSON.parse(localStorage.getItem(STOCKAGE) || 'null'); }}catch(erreur){{ return; }}
    if(!etatReponses){{ return; }}
    for(const planche of planches){{
      const sauvegarde = etatReponses[planche.cle];
      if(!sauvegarde){{ continue; }}
      if(sauvegarde.verdict){{
        const bouton = document.querySelector(
          'input[name="v-' + planche.cle + '"][value="' + sauvegarde.verdict + '"]');
        if(bouton){{ bouton.checked = true; }}
      }}
      document.querySelector('textarea[data-note="' + planche.cle + '"]').value = sauvegarde.note || '';
    }}
  }}

  function copier(texte){{
    const zone = document.createElement('textarea');
    zone.value = texte;
    zone.style.position = 'fixed';
    zone.style.opacity = '0';
    document.body.appendChild(zone);
    zone.select();
    let reussi = false;
    try{{ reussi = document.execCommand('copy'); }}catch(erreur){{ reussi = false; }}
    document.body.removeChild(zone);

    return reussi;
  }}

  const suivre = () => {{ rafraichir(); enregistrer(); }};
  document.addEventListener('input', suivre);
  document.addEventListener('change', suivre);

  document.getElementById('copier').addEventListener('click', () => {{
    rafraichir();
    if(copier(recap.value)){{
      etat.textContent = 'Récapitulatif copié — collez-le dans la conversation.';

      return;
    }}
    recap.select();
    etat.textContent = 'Copie refusée par le navigateur : le texte est sélectionné, Ctrl+C.';
  }});

  // Plates are published one by one: reloading is how the operator sees a newly published one from his
  // phone. Answers are in localStorage, so a reload keeps them.
  document.getElementById('recharger').addEventListener('click', () => {{
    location.reload();
  }});

  const boutonGrille = document.getElementById('grille');
  boutonGrille.addEventListener('click', () => {{
    const calques = document.querySelectorAll('.grille-calque');
    const afficher = calques[0] && calques[0].hidden;
    for(const calque of calques){{ calque.hidden = !afficher; }}
    boutonGrille.textContent = afficher ? 'Masquer la grille' : 'Afficher la grille';
  }});

  // Side by side comparison: the only reliable way to judge whether a plate holds the direction.
  const faceAFace = document.getElementById('face-a-face');
  const duoReference = document.getElementById('duo-reference');
  const duoPlanche = document.getElementById('duo-planche');
  const duoTitre = document.getElementById('duo-titre');
  const imageReference = document.querySelector('.reference .cadre img');

  for(const bouton of document.querySelectorAll('[data-comparer]')){{
    bouton.addEventListener('click', () => {{
      const cle = bouton.getAttribute('data-comparer');
      const section = bouton.closest('.planche');
      const image = section.querySelector('.cadre img');
      if(!image){{ return; }}
      duoReference.src = imageReference.src;
      duoPlanche.src = image.src;
      duoTitre.textContent = section.querySelector('.titre').textContent;
      faceAFace.classList.add('visible');
      window.scrollTo(0, 0);
    }});
  }}
  document.getElementById('fermer-duo').addEventListener('click', () => {{
    faceAFace.classList.remove('visible');
  }});

  // Re-runs of the reference prompt, compared against the reference in service.
  const retirages = document.getElementById('retirages');
  document.getElementById('voir-retirages').addEventListener('click', () => {{
    retirages.classList.add('visible');
    window.scrollTo(0, 0);
  }});
  document.getElementById('fermer-retirages').addEventListener('click', () => {{
    retirages.classList.remove('visible');
  }});

  const loupe = document.getElementById('loupe');
  const loupeImage = loupe.querySelector('img');
  for(const image of document.querySelectorAll('.cadre img')){{
    image.addEventListener('click', () => {{
      loupeImage.src = image.src;
      loupe.classList.add('visible');
    }});
  }}
  loupe.addEventListener('click', () => loupe.classList.remove('visible'));

  restaurer();
  rafraichir();
</script>
"""

target = ASSETS / "revue-planches.html"
target.write_text(PAGE, encoding="utf-8")
print(f"OK {target} {round(target.stat().st_size / 1024)} KB")

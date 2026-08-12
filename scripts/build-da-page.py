#!/usr/bin/env python3
"""Build the art direction review page with every image embedded as a data URI.

The artifact runtime forbids external requests, so images are downscaled and inlined as JPEG to keep the
page light enough to load comfortably.
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "revue-da"

DIRECTIONS = [
    ("b10-r15", "Village sculpté",
     "Volumes sculptés aux surfaces mates, silhouettes nettes, sol rangé, ombrage de contact doux, aucun "
     "contour. <em>Nouvelle piste, inspirée des jeux de village vus de dessus.</em>"),
    ("b4-r15", "Toon volume",
     "Volumes sculptés, ombrage en deux bandes nettes, sans contour. <em>Ancrage renforcé sur l'image du "
     "tour 6, plus eau calme, herbe sobre, ombres simples, couleurs franches et runes réduites.</em>"),
]


def encode(path: Path, width: int, quality: int) -> str:
    image = Image.open(path).convert("RGB")
    if image.width > width:
        height = round(image.height * width / image.width)
        image = image.resize((width, height), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    return f"data:image/jpeg;base64,{encoded}"


# A validated creature is never regenerated: some directions reuse an earlier round's creature file.
CREATURES = {"b4-r15": "gb-b4v7", "b10-r15": "gb-b7v7"}

# The grid the scenes are composed on. Tiles are square and divide the frame exactly.
TILES_X, TILES_Y = 32, 24


def placeholder(label: str) -> str:
    """An image still being generated: say so plainly rather than leave an empty frame."""
    return (
        '<svg class="attente" viewBox="0 0 1200 750" preserveAspectRatio="xMidYMid slice" role="img">'
        '<rect width="1200" height="750" fill="currentColor" opacity="0.06"/>'
        '<g fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-width="4">'
        '<circle cx="600" cy="330" r="70"/><path d="M600 260v70l48 30"/></g>'
        f'<text x="600" y="470" text-anchor="middle" font-size="34" fill="currentColor" '
        f'fill-opacity="0.55" font-family="sans-serif">{label}</text></svg>'
    )


def visual(path: Path, width: int, quality: int, alt: str, label: str, kind: str) -> str:
    if path.is_file():
        return f'<img src="{encode(path, width, quality)}" alt="{alt}">'

    return placeholder(label if kind == "scene" else "En cours…")


def meta(path: Path) -> str:
    """Dimensions, tile count and pixels per tile: the only way to tell a zoom from a proportion change."""
    if not path.is_file():
        return "Scène en cours de génération — cliquez pour agrandir une fois disponible"
    width, height = Image.open(path).size
    par_case = f"{width / TILES_X:.0f} × {height / TILES_Y:.0f}"
    exact = "exact" if width % TILES_X == 0 and height % TILES_Y == 0 else "NON ENTIER"

    return (f"{width} × {height} px &nbsp;·&nbsp; {TILES_X} × {TILES_Y} cases &nbsp;·&nbsp; "
            f"{par_case} px par case ({exact}) &nbsp;·&nbsp; cliquez pour agrandir")


def prompt(key: str) -> str:
    """The exact prompt used to produce the scene, so it can be judged alongside the result."""
    path = ASSETS / f"prompt-{key}-scene.txt"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return (f'<details class="consigne"><summary>Consigne de génération — {len(text)} caractères, '
            f'{len(text.split())} mots</summary><pre>{escaped}</pre></details>')


def section(key: str, name: str, note: str) -> str:
    code = f"DA-GB-{key.upper()}"
    creature_file = ASSETS / f"da-{CREATURES.get(key, key)}-creature.png"
    scene_file = ASSETS / f"da-{key}-scene.png"
    pending = not (creature_file.is_file() and scene_file.is_file())
    disabled = " disabled" if pending else ""
    etat = ('<span class="attente-cachet">Génération en cours — revenez dans quelques minutes</span>'
            if pending else "")

    return f"""
    <section class="vue{' en-attente' if pending else ''}">
      <header class="entete">
        <div>
          <span class="code">{code}</span>
          <p class="titre">{name}</p>
          {etat}
        </div>
      </header>
      <figure class="large">
        <div class="cadre">
          {visual(scene_file, 1400, 82, f"Scène de jeu — {name}", "Scène en cours de génération", "scene")}
          <div class="grille-calque" hidden></div>
        </div>
        <figcaption>{meta(scene_file)}</figcaption>
      </figure>
      {prompt(key)}
      <div class="bas">
        <figure class="petite">
          {visual(creature_file, 640, 80, f"Créature témoin — {name}", "En cours…", "creature")}
          <figcaption>La créature, même style</figcaption>
        </figure>
        <div class="corps">
          <p class="note">{note}</p>
          <div class="choix">
            <label><input type="radio" name="v-{key}" value="Retenir"{disabled}><span>Retenir</span></label>
            <label><input type="radio" name="v-{key}" value="À retravailler"{disabled}><span>À retravailler</span></label>
            <label><input type="radio" name="v-{key}" value="Écarter"{disabled}><span>Écarter</span></label>
          </div>
          <textarea data-note="{key}" placeholder="Dire pourquoi — ce qui accroche, ce qui gêne."{disabled}></textarea>
        </div>
      </div>
    </section>"""


VIEWS = "\n".join(section(key, name, note) for key, name, note in DIRECTIONS)
# JSON encoding, never string interpolation: French labels contain apostrophes that would break the script.
CATALOGUE = json.dumps(
    [{"cle": key, "code": f"DA-GB-{key.upper()}", "nom": name} for key, name, _ in DIRECTIONS],
    ensure_ascii=False,
)

PAGE = f"""<title>GateBeast — Revue de direction artistique</title>
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
  .page{{max-width:1080px; margin:0 auto;}}
  h1{{font-size:1.9rem; margin:0 0 .3rem; letter-spacing:-.02em;}}
  .sous{{color:var(--doux); margin:0 0 .4rem;}}
  .cachet{{color:var(--doux); font-size:.85rem; font-variant:all-small-caps; letter-spacing:.06em;}}
  .rappel{{background:var(--fond2); border:1px solid var(--trait); border-left:3px solid var(--accent);
    border-radius:.6rem; padding:.9rem 1.1rem; margin:1.6rem 0 2.2rem;}}
  .rappel p{{margin:.3rem 0;}}
  .vue{{background:var(--fond2); border:1px solid var(--trait); border-radius:.9rem; overflow:hidden;
    margin-bottom:2rem;}}
  .entete{{display:flex; flex-wrap:wrap; gap:.8rem; align-items:center; justify-content:space-between;
    padding:1rem 1.2rem;}}
  .code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.78rem; color:var(--accent);
    letter-spacing:.04em;}}
  .titre{{font-size:1.2rem; font-weight:650; margin:.1rem 0 0;}}
  figure{{margin:0;}}
  .large img{{width:100%; display:block; cursor:zoom-in; background:#fff;}}
  figcaption{{font-size:.75rem; color:var(--doux); padding:.4rem 1.2rem; font-variant:all-small-caps;
    letter-spacing:.06em;}}
  .bas{{display:grid; grid-template-columns:minmax(160px,220px) 1fr; gap:1.2rem; padding:.6rem 1.2rem 1.3rem;
    align-items:start;}}
  @media (max-width:700px){{.bas{{grid-template-columns:1fr;}}}}
  .petite img{{width:100%; display:block; border-radius:.6rem; cursor:zoom-in; background:#fff;}}
  .petite figcaption{{padding:.35rem 0 0;}}
  .note{{color:var(--doux); font-size:.95rem; margin:0 0 .7rem;}}
  .note strong{{color:var(--encre); font-weight:600;}}
  .choix{{display:flex; flex-wrap:wrap; gap:.5rem; margin:0 0 .7rem;}}
  .choix label{{border:1px solid var(--trait); border-radius:2rem; padding:.28rem .85rem; font-size:.88rem;
    cursor:pointer; user-select:none;}}
  .choix input{{margin-right:.35rem; accent-color:var(--accent);}}
  .choix input:checked+span{{font-weight:650; color:var(--accent);}}
  textarea{{width:100%; box-sizing:border-box; min-height:3.6rem; resize:vertical; padding:.6rem .7rem;
    border:1px solid var(--trait); border-radius:.5rem; background:var(--fond); color:var(--encre);
    font:inherit; font-size:.9rem;}}
  .barre{{position:fixed; left:0; right:0; bottom:0; z-index:20; display:flex; flex-wrap:wrap; gap:.8rem;
    align-items:center; padding:.7rem 1.25rem; background:var(--fond2);
    border-top:1px solid var(--trait); box-shadow:0 -6px 20px rgba(0,0,0,.08);}}
  button{{background:var(--accent); color:#fff; border:0; border-radius:.5rem; padding:.6rem 1.15rem;
    font:inherit; font-weight:600; cursor:pointer;}}
  button.secondaire{{background:transparent; color:var(--accent); border:1px solid var(--trait);}}
  #etat{{color:var(--doux); font-size:.88rem;}}
  #recap{{width:100%; box-sizing:border-box; margin-top:1rem; min-height:8rem;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.82rem;}}
  .zone-recap{{margin-top:2.4rem; border-top:1px solid var(--trait); padding-top:1.2rem;}}
  .zone-recap h2{{font-size:1.1rem; margin:0 0 .3rem;}}
  .zone-recap p{{color:var(--doux); font-size:.9rem; margin:0;}}
  .glossaire{{margin-top:2.6rem; border-top:1px solid var(--trait); padding-top:1.2rem; color:var(--doux);
    font-size:.9rem;}}
  .glossaire code{{color:var(--accent);}}
  .cadre{{position:relative; line-height:0;}}
  .grille-calque{{position:absolute; inset:0; pointer-events:none;
    background-image:linear-gradient(to right, rgba(255,0,90,.55) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255,0,90,.55) 1px, transparent 1px);
    background-size:calc(100% / {TILES_X}) calc(100% / {TILES_Y});}}
  .consigne{{margin:.2rem 1.2rem .6rem; font-size:.85rem; color:var(--doux);}}
  .consigne summary{{cursor:pointer; color:var(--accent);}}
  .consigne pre{{white-space:pre-wrap; background:var(--fond); border:1px solid var(--trait);
    border-radius:.5rem; padding:.7rem .8rem; font-size:.78rem; max-height:22rem; overflow:auto;}}
  .attente{{width:100%; display:block; color:var(--encre);}}
  .en-attente{{opacity:.75;}}
  .en-attente .choix label{{cursor:not-allowed; opacity:.5;}}
  .en-attente textarea{{opacity:.5;}}
  .attente-cachet{{display:inline-block; margin-top:.2rem; font-size:.78rem; color:var(--accent);
    border:1px dashed var(--accent); border-radius:2rem; padding:.1rem .7rem;}}
  #loupe{{position:fixed; inset:0; z-index:50; background:rgba(0,0,0,.85); display:none;
    align-items:center; justify-content:center; padding:1.5rem; cursor:zoom-out;}}
  #loupe.visible{{display:flex;}}
  #loupe img{{max-width:100%; max-height:100%; border-radius:.4rem;}}
</style>

<div class="page">
  <h1>GateBeast — Revue de direction artistique</h1>
  <p class="sous">Trois directions encore en lice, chacune reprise selon vos remarques. La scène est au
    cadrage réel du jeu ; la créature montre le même style de près.</p>
  <p class="cachet">Version 6 — troisième tour, créature de référence tenue d'une vue à l'autre —
    1er août 2026</p>

  <div class="rappel">
    <p><strong>Déjà acté</strong> : univers original, ton positif et familial, plan parallèle implicite au
      début, caméra vue de dessus, style constant entre toutes les vues d'une direction.</p>
    <p><strong>Se décide ici</strong> : la direction artistique — donc le design de l'interface et le coût
      de production du bestiaire.</p>
    <p><strong>N'est pas jugé ici</strong> : la créature et le décor eux-mêmes, témoins jetables identiques
      partout. Les directions écartées au tour précédent ont été retirées.</p>
  </div>

{VIEWS}

  <div class="zone-recap">
    <h2>Votre récapitulatif</h2>
    <p>Il se met à jour tout seul. Sélectionnez-le et copiez-le, ou utilisez le bouton en bas d'écran.
      Vos réponses sont conservées dans ce navigateur : vous pouvez fermer la page sans rien perdre.</p>
    <textarea id="recap" readonly></textarea>
  </div>

  <div class="glossaire">
    <p>Les codes de vue sont stables : <code>DA-GB-B1V3</code>, <code>DA-GB-B2V3</code>,
      <code>DA-GB-B4V3</code> — <em>V3</em> marque le troisième tour d'une même direction. Citez-les pour
      désigner une vue sans ambiguïté.</p>
    <p>Cette page n'est pas la conception : rien n'y fait foi. Ce que vous validez est ensuite gravé dans le
      référentiel visuel de GateBeast.</p>
  </div>
</div>

<div class="barre">
  <button id="grille" class="secondaire">Afficher la grille</button>
  <button id="copier">Copier le récapitulatif</button>
  <button id="selectionner" class="secondaire">Tout sélectionner</button>
  <span id="etat"></span>
</div>

<div id="loupe"><img alt=""></div>

<script>
  const vues = {CATALOGUE};
  const recap = document.getElementById('recap');
  const etat = document.getElementById('etat');

  function construire(){{
    const lignes = ['Revue DA GateBeast — version 6 (1er août 2026)', ''];
    let repondues = 0;
    for(const vue of vues){{
      const choisi = document.querySelector('input[name="v-' + vue.cle + '"]:checked');
      const note = document.querySelector('textarea[data-note="' + vue.cle + '"]').value.trim();
      if(choisi){{ repondues++; }}
      lignes.push(vue.code + ' ' + vue.nom + ' : ' + (choisi ? choisi.value : 'sans réponse'));
      if(note){{ lignes.push('  parce que ' + note); }}
    }}
    return {{texte:lignes.join('\\n'), repondues:repondues}};
  }}

  function rafraichir(){{
    const resultat = construire();
    recap.value = resultat.texte;
    etat.textContent = resultat.repondues + ' vue(s) sur ' + vues.length + ' renseignée(s).';
  }}

  function copier(texte){{
    const zone = document.createElement('textarea');
    zone.value = texte;
    zone.setAttribute('readonly', '');
    zone.style.position = 'fixed';
    zone.style.opacity = '0';
    document.body.appendChild(zone);
    zone.select();
    zone.setSelectionRange(0, texte.length);
    let reussi = false;
    try{{ reussi = document.execCommand('copy'); }}catch(erreur){{ reussi = false; }}
    document.body.removeChild(zone);

    return reussi;
  }}

  // Answers are kept in this browser: nothing is lost on reload or on a stray click.
  const STOCKAGE = 'gatebeast-revue-da-v6';

  function enregistrer(){{
    const etatReponses = {{}};
    for(const vue of vues){{
      const choisi = document.querySelector('input[name="v-' + vue.cle + '"]:checked');
      etatReponses[vue.cle] = {{
        verdict: choisi ? choisi.value : '',
        note: document.querySelector('textarea[data-note="' + vue.cle + '"]').value,
      }};
    }}
    try{{ localStorage.setItem(STOCKAGE, JSON.stringify(etatReponses)); }}catch(erreur){{ /* ignoré */ }}
  }}

  function restaurer(){{
    let etatReponses = null;
    try{{ etatReponses = JSON.parse(localStorage.getItem(STOCKAGE) || 'null'); }}catch(erreur){{ return; }}
    if(!etatReponses){{ return; }}
    for(const vue of vues){{
      const sauvegarde = etatReponses[vue.cle];
      if(!sauvegarde){{ continue; }}
      if(sauvegarde.verdict){{
        const bouton = document.querySelector(
          'input[name="v-' + vue.cle + '"][value="' + sauvegarde.verdict + '"]');
        if(bouton){{ bouton.checked = true; }}
      }}
      document.querySelector('textarea[data-note="' + vue.cle + '"]').value = sauvegarde.note || '';
    }}
  }}

  // 'change' as well as 'input': radio buttons do not emit 'input' in every browser.
  const suivre = () => {{ rafraichir(); enregistrer(); }};
  document.addEventListener('input', suivre);
  document.addEventListener('change', suivre);
  for(const champ of document.querySelectorAll('input[type=radio], textarea[data-note]')){{
    champ.addEventListener('click', suivre);
    champ.addEventListener('keyup', suivre);
  }}

  document.getElementById('copier').addEventListener('click', () => {{
    rafraichir();
    if(copier(recap.value)){{
      etat.textContent = 'Récapitulatif copié — collez-le dans la conversation.';

      return;
    }}
    if(navigator.clipboard){{
      navigator.clipboard.writeText(recap.value).then(() => {{
        etat.textContent = 'Récapitulatif copié — collez-le dans la conversation.';
      }}).catch(() => {{
        recap.select();
        etat.textContent = 'Copie refusée par le navigateur : le texte est sélectionné, Ctrl+C.';
      }});

      return;
    }}
    recap.select();
    etat.textContent = 'Copie indisponible : le texte est sélectionné, Ctrl+C.';
  }});

  document.getElementById('selectionner').addEventListener('click', () => {{
    rafraichir();
    recap.scrollIntoView({{behavior:'smooth', block:'center'}});
    recap.focus();
    recap.select();
    etat.textContent = 'Texte sélectionné — Ctrl+C pour copier.';
  }});

  restaurer();

  const boutonGrille = document.getElementById('grille');
  boutonGrille.addEventListener('click', () => {{
    const calques = document.querySelectorAll('.grille-calque');
    const afficher = calques[0] && calques[0].hidden;
    for(const calque of calques){{ calque.hidden = !afficher; }}
    boutonGrille.textContent = afficher ? 'Masquer la grille' : 'Afficher la grille';
  }});

  const loupe = document.getElementById('loupe');
  const loupeImage = loupe.querySelector('img');
  for(const image of document.querySelectorAll('.large img, .petite img')){{
    image.addEventListener('click', () => {{
      loupeImage.src = image.src;
      loupe.classList.add('visible');
    }});
  }}
  loupe.addEventListener('click', () => loupe.classList.remove('visible'));

  rafraichir();
</script>
"""

target = ASSETS / "revue-da.html"
target.write_text(PAGE, encoding="utf-8")
print(f"OK {target} {round(target.stat().st_size / 1024)} KB")

#!/usr/bin/env python3
"""Build the sound review page, with every sound embedded and playable.

Sounds are downmixed to mono and resampled before being inlined, since the artifact runtime forbids
external requests and the original stereo files are far too heavy to embed. Each sound also gets a
waveform drawn as inline SVG, so its shape can be read before pressing play.
"""
import audioop
import base64
import io
import json
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "audio-probe"
RATE = 22050

ASSETS_V2 = HERE.parent / "assets" / "audio-probe-v2"

# Second battery: the four rejected sounds, resynthesized from a technical diagnosis. Shown first, since
# they are what needs judging now.
SOUNDS_V2 = [
    ("water-stream", "Ruisseau — 2e essai", "ambiance",
     "Refait en bulles résonnantes discrètes plutôt qu'en bruit filtré, sans compression finale. "
     "Précédemment jugé « grésillement de téléviseur »."),
    ("rain-canopy", "Pluie sur la canopée — 2e essai", "ambiance",
     "Refaite en gouttes individuelles tirées au hasard sur plusieurs couches. Précédemment jugée "
     "« grésillement de téléviseur »."),
    ("bird-call", "Chant d'oiseau — 2e essai", "détail",
     "Refait avec des transitions de hauteur et un timbre variables. Précédemment jugé « plus cri très "
     "aigu d'enfant qu'oiseau »."),
    ("creature-cry", "Cri de créature — 2e essai", "effet",
     "Refait avec une part de souffle et des irrégularités volontaires. Précédemment jugé « très électro, "
     "manque de naturel »."),
]

SOUNDS = [
    ("step-grass", "Pas dans l'herbe", "effet",
     "Un froissement très bref et très aigu, une demi-seconde. Doit se répéter des milliers de fois sans "
     "lasser : c'est le son le plus exigeant du lot."),
    ("creature-cry", "Cri de créature", "effet",
     "Court et tonal, dans le médium. Doit sonner curieux et chaleureux, jamais inquiétant."),
    ("ui-confirm", "Confirmation d'interface", "effet",
     "Deux notes brèves et franchement musicales. C'est le son que le joueur entendra le plus souvent."),
    ("bird-call", "Chant d'oiseau", "détail",
     "Sifflement modulé d'une seconde et demie, seconde note plus forte. Sert à animer une ambiance sans "
     "la charger."),
    ("gate-hum", "Bourdonnement de passage", "ambiance",
     "Très grave, très stable, avec une lente respiration. C'est la signature sonore du plan parallèle : "
     "il doit intriguer sans inquiéter."),
    ("water-stream", "Ruisseau", "ambiance",
     "Flux dense et régulier, le plus large en stéréo de tout le lot. Donne de l'espace à une zone."),
    ("rain-canopy", "Pluie sur la canopée", "ambiance",
     "Le son le plus aigu du lot, crépitement dense et continu. Test d'une météo variable."),
    ("scene-clearing", "Scène — clairière au crépuscule", "scène",
     "Vingt secondes à plusieurs couches, nettement plus discrètes que les autres et qui varient tout du "
     "long. C'est l'essai le plus ambitieux : une ambiance complète, pas une texture unique."),
]


def load(name: str, base: Path = None):
    with wave.open(str((base or ASSETS) / f"{name}.wav"), "rb") as handle:
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())
    if channels > 1:
        frames = audioop.tomono(frames, width, 0.5, 0.5)
    frames, _ = audioop.ratecv(frames, width, 1, rate, RATE, None)

    return frames, width


def encode(frames: bytes, width: int) -> str:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(width)
        handle.setframerate(RATE)
        handle.writeframes(frames)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    return f"data:audio/wav;base64,{encoded}"


def waveform(frames: bytes, width: int, points: int = 220) -> str:
    total = len(frames) // width
    step = max(1, total // points)
    peaks = []
    for index in range(0, total - step, step):
        chunk = frames[index * width:(index + step) * width]
        peaks.append(audioop.max(chunk, width) / 32768)
    top = max(peaks) or 1
    coordinates = " ".join(
        f"{position * 100 / len(peaks):.2f},{50 - value / top * 46:.2f}"
        for position, value in enumerate(peaks)
    )
    mirror = " ".join(
        f"{position * 100 / len(peaks):.2f},{50 + value / top * 46:.2f}"
        for position, value in reversed(list(enumerate(peaks)))
    )

    return (f'<svg class="onde" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
            f'<polygon points="{coordinates} {mirror}"/></svg>')


def section(name: str, title: str, kind: str, note: str, base: Path = None, suffix: str = "") -> str:
    frames, width = load(name, base)
    source = encode(frames, width)
    key = f"{name}{suffix}"

    return f"""
    <section class="son">
      <header>
        <span class="genre">{kind}</span>
        <p class="titre">{title}</p>
      </header>
      {waveform(frames, width)}
      <audio controls preload="none" src="{source}"></audio>
      <p class="note">{note}</p>
      <div class="choix">
        <label><input type="radio" name="s-{key}" value="Bon"><span>Bon</span></label>
        <label><input type="radio" name="s-{key}" value="Passable"><span>Passable</span></label>
        <label><input type="radio" name="s-{key}" value="Mauvais"><span>Mauvais</span></label>
      </div>
      <textarea data-note="{key}" placeholder="Dire pourquoi — ce qui marche, ce qui cloche."></textarea>
    </section>"""


VIEWS_V2 = "\n".join(
    section(name, title, kind, note, ASSETS_V2, "-v2") for name, title, kind, note in SOUNDS_V2)
VIEWS = "\n".join(section(name, title, kind, note) for name, title, kind, note in SOUNDS)
# JSON encoding, never string interpolation: French names contain apostrophes that would break the script.
CATALOGUE = json.dumps(
    [{"cle": f"{name}-v2", "nom": title} for name, title, _, _ in SOUNDS_V2]
    + [{"cle": name, "nom": title} for name, title, _, _ in SOUNDS],
    ensure_ascii=False,
)

PAGE = f"""<title>GateBeast — Revue sonore</title>
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
  .page{{max-width:1000px; margin:0 auto;}}
  h1{{font-size:1.9rem; margin:0 0 .3rem; letter-spacing:-.02em;}}
  .sous{{color:var(--doux); margin:0 0 .4rem;}}
  .cachet{{color:var(--doux); font-size:.85rem; font-variant:all-small-caps; letter-spacing:.06em;}}
  .rappel{{background:var(--fond2); border:1px solid var(--trait); border-left:3px solid var(--accent);
    border-radius:.6rem; padding:.9rem 1.1rem; margin:1.6rem 0 2.2rem;}}
  .rappel p{{margin:.3rem 0;}}
  .groupe{{font-size:1.25rem; margin:2.4rem 0 .2rem;}}
  .grille{{display:grid; gap:1.3rem; grid-template-columns:repeat(auto-fit,minmax(320px,1fr));}}
  .son{{background:var(--fond2); border:1px solid var(--trait); border-radius:.9rem; padding:1rem 1.1rem
    1.2rem; display:flex; flex-direction:column; gap:.6rem;}}
  .son header{{display:flex; flex-direction:column; gap:.1rem;}}
  .genre{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.72rem; color:var(--accent);
    letter-spacing:.08em; text-transform:uppercase;}}
  .titre{{font-size:1.1rem; font-weight:650; margin:0;}}
  .onde{{width:100%; height:56px; display:block;}}
  .onde polygon{{fill:var(--accent); opacity:.6;}}
  audio{{width:100%;}}
  .note{{color:var(--doux); font-size:.92rem; margin:0;}}
  .choix{{display:flex; flex-wrap:wrap; gap:.5rem;}}
  .choix label{{border:1px solid var(--trait); border-radius:2rem; padding:.26rem .8rem; font-size:.86rem;
    cursor:pointer; user-select:none;}}
  .choix input{{margin-right:.35rem; accent-color:var(--accent);}}
  .choix input:checked+span{{font-weight:650; color:var(--accent);}}
  textarea{{width:100%; box-sizing:border-box; min-height:3.4rem; resize:vertical; padding:.6rem .7rem;
    border:1px solid var(--trait); border-radius:.5rem; background:var(--fond); color:var(--encre);
    font:inherit; font-size:.9rem;}}
  .barre{{position:fixed; left:0; right:0; bottom:0; z-index:20; display:flex; flex-wrap:wrap; gap:.8rem;
    align-items:center; padding:.7rem 1.25rem; background:var(--fond2); border-top:1px solid var(--trait);
    box-shadow:0 -6px 20px rgba(0,0,0,.08);}}
  button{{background:var(--accent); color:#fff; border:0; border-radius:.5rem; padding:.6rem 1.15rem;
    font:inherit; font-weight:600; cursor:pointer;}}
  button.secondaire{{background:transparent; color:var(--accent); border:1px solid var(--trait);}}
  #etat{{color:var(--doux); font-size:.88rem;}}
  #recap{{width:100%; box-sizing:border-box; margin-top:1rem; min-height:11rem;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.82rem;}}
  .zone-recap{{margin-top:2.4rem; border-top:1px solid var(--trait); padding-top:1.2rem;}}
  .zone-recap h2{{font-size:1.1rem; margin:0 0 .3rem;}}
  .zone-recap p{{color:var(--doux); font-size:.9rem; margin:0;}}
  .glossaire{{margin-top:2.4rem; border-top:1px solid var(--trait); padding-top:1.2rem; color:var(--doux);
    font-size:.9rem;}}
</style>

<div class="page">
  <h1>GateBeast — Revue sonore</h1>
  <p class="sous">Huit essais de natures volontairement différentes, pour établir ce que la production
    sonore sait faire — et ce qu'elle ne sait pas faire.</p>
  <p class="cachet">Version 1 — premier lot d'essais — 1er août 2026</p>

  <div class="rappel">
    <p><strong>Ce qui se décide ici</strong> : si la synthèse sonore atteint un niveau suffisant pour entrer
      dans le jeu, et sur quelles familles de sons elle tient la route.</p>
    <p><strong>Ce qui n'est pas jugé ici</strong> : l'identité sonore du jeu, qui viendra bien plus tard.
      Ces sons sont des essais de capacité, pas des propositions artistiques.</p>
    <p><strong>À savoir</strong> : il s'agit de synthèse procédurale, pas d'un modèle audio. La musique n'a
      pas été essayée. Les sons sont ramenés en mono et allégés pour tenir dans cette page ; les originaux
      sont en stéréo et de meilleure qualité.</p>
  </div>

  <h2 class="groupe">Second essai — les quatre sons rejetés, refaits</h2>
  <p class="sous">Même sujet, méthode de synthèse entièrement différente : plus aucune compression finale,
    des couches indépendantes, et chaque événement tiré au hasard. C'est ce lot qu'il faut juger.</p>
  <div class="grille">
{VIEWS_V2}
  </div>

  <h2 class="groupe">Premier essai — le lot d'origine</h2>
  <p class="sous">Conservé pour comparaison. Vos verdicts sont déjà enregistrés dans la conception ; inutile
    de les redonner.</p>
  <div class="grille">
{VIEWS}
  </div>

  <div class="zone-recap">
    <h2>Votre récapitulatif</h2>
    <p>Il se met à jour tout seul. Sélectionnez-le et copiez-le, ou utilisez le bouton en bas d'écran.
      Vos réponses sont conservées dans ce navigateur : vous pouvez fermer la page sans rien perdre.</p>
    <textarea id="recap" readonly></textarea>
  </div>

  <div class="glossaire">
    <p>Cette page n'est pas la conception : rien n'y fait foi. Ce que vous validez est ensuite gravé dans le
      référentiel technique et le plan d'action de GateBeast.</p>
  </div>
</div>

<div class="barre">
  <button id="copier">Copier le récapitulatif</button>
  <button id="selectionner" class="secondaire">Tout sélectionner</button>
  <span id="etat"></span>
</div>

<script>
  const sons = {CATALOGUE};
  const recap = document.getElementById('recap');
  const etat = document.getElementById('etat');

  function construire(){{
    const lignes = ['Revue sonore GateBeast — version 1 (1er août 2026)', ''];
    let repondues = 0;
    for(const son of sons){{
      const choisi = document.querySelector('input[name="s-' + son.cle + '"]:checked');
      const note = document.querySelector('textarea[data-note="' + son.cle + '"]').value.trim();
      if(choisi){{ repondues++; }}
      lignes.push(son.nom + ' : ' + (choisi ? choisi.value : 'sans réponse'));
      if(note){{ lignes.push('  parce que ' + note); }}
    }}
    return {{texte:lignes.join('\\n'), repondues:repondues}};
  }}

  function rafraichir(){{
    const resultat = construire();
    recap.value = resultat.texte;
    etat.textContent = resultat.repondues + ' son(s) sur ' + sons.length + ' renseigné(s).';
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
  const STOCKAGE = 'gatebeast-revue-son-v1';

  function enregistrer(){{
    const etatReponses = {{}};
    for(const son of sons){{
      const choisi = document.querySelector('input[name="s-' + son.cle + '"]:checked');
      etatReponses[son.cle] = {{
        verdict: choisi ? choisi.value : '',
        note: document.querySelector('textarea[data-note="' + son.cle + '"]').value,
      }};
    }}
    try{{ localStorage.setItem(STOCKAGE, JSON.stringify(etatReponses)); }}catch(erreur){{ /* ignoré */ }}
  }}

  function restaurer(){{
    let etatReponses = null;
    try{{ etatReponses = JSON.parse(localStorage.getItem(STOCKAGE) || 'null'); }}catch(erreur){{ return; }}
    if(!etatReponses){{ return; }}
    for(const son of sons){{
      const sauvegarde = etatReponses[son.cle];
      if(!sauvegarde){{ continue; }}
      if(sauvegarde.verdict){{
        const bouton = document.querySelector(
          'input[name="s-' + son.cle + '"][value="' + sauvegarde.verdict + '"]');
        if(bouton){{ bouton.checked = true; }}
      }}
      document.querySelector('textarea[data-note="' + son.cle + '"]').value = sauvegarde.note || '';
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

  // One player at a time, so sounds are compared rather than layered.
  const lecteurs = Array.from(document.querySelectorAll('audio'));
  for(const lecteur of lecteurs){{
    lecteur.addEventListener('play', () => {{
      for(const autre of lecteurs){{ if(autre !== lecteur){{ autre.pause(); }} }}
    }});
  }}

  rafraichir();
</script>
"""

target = ASSETS / "revue-son.html"
target.write_text(PAGE, encoding="utf-8")
print(f"OK {target} {round(target.stat().st_size / 1024)} KB")

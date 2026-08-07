<?php
/**
 * Usage: php review-server/parc/monter.php
 *
 * Builds review-server/parc/maquette.html — the park mock-up itself: every sprite the plan declares, laid on its own cell, at the scale of the world.
 *
 * Intention: the plan says which subject stands on which cell; the referentiel says which image is that subject's current one; the tile scale says what a cell measures on
 * screen. Mounting the mock-up is nothing more than putting those three together — and it is the first time the sprites are seen TOGETHER, which is the only way to judge
 * whether they belong to the same world.
 *
 * A MISSING SPRITE IS SHOWN AS MISSING, never quietly skipped: its cell is drawn in the colour the chain uses for what is left to produce, with the subject's code on it. A
 * mock-up that hid its holes would look finished while being unusable, and the whole point of mounting it now is to see what is still owed.
 *
 * The ground comes first, then what stands on it, in reading order — the same order the game's renderer uses. A path may therefore run UNDER a building, which is exactly
 * what the operator asked for so that a path can reach a door that does not sit on the sprite's bottom edge.
 */

$root = __DIR__ . '/../..';
require_once "$root/scripts/Capture.php";
require_once "$root/review-server/bootstrap.php";
bootBuild();
// THE SERVED ROUTE IS THE THIRD ARGUMENT: this mounter produces the mock-up served at /parc/maquette, but also a SOURCE of the Campagne page, melted elsewhere. A source carries no reload notice —
// the final page would otherwise hold two of them, on a route that is not its own. That absence of a route is `null`, never an empty string: an empty string is a string holding nothing, which is
// not the same as having no route at all. A command line can only carry text, so the emptiness it hands over is brought back to null right here.
$route = ($argv[3] ?? '/parc/maquette') ?: null;

// Services are taken here, at the top, once — and so is what they render: the template below only has to lay down variables, with no call in the middle of the HTML.
$favicon = Favicon::get();
$reload = Reload::get();
$faviconTag = $favicon->tag();
$reloadStyles = $route === null ? '' : $reload->styles();
$reloadMarkup = $route === null ? '' : $reload->markup();
$reloadScript = $route === null ? '' : $reload->script($route);

const SCREEN_PIXELS_PER_TILE = 24;   // ce qu'une case mesure à l'écran — la valeur par défaut du projet, tenue par scripts/tile_scale.py
const GROUND_TYPES = ['sol', 'chemin', 'herbe'];

// LE PLAN ET LA SORTIE SE DONNENT EN ARGUMENT, le parc n'étant que la valeur par défaut : il y aura d'autres maquettes — la scène de référence de 32 × 24 d'abord (opérateur,
// 2026-08-06) —, et un monteur qui ne sait monter qu'une carte oblige à le recopier pour la suivante. Un seul monteur, autant de maquettes.
$planPath = $argv[1] ?? "$root/assets/maquette/plan-parc-a.json";
$outputPath = $argv[2] ?? __DIR__ . '/maquette.html';
$plan = json_decode(file_get_contents($planPath), true, 512, JSON_THROW_ON_ERROR);
$sujets = json_decode(file_get_contents("$root/assets/sujets.json"), true, 512, JSON_THROW_ON_ERROR)['sujets'];

/** The image a subject shows on THIS cell: the variant whose shape matches what the cell joins, and its current representation.
 *
 * LA FORME COMPTE, ET L'IGNORER RUINE LA MAQUETTE. Une barrière, un chemin, un cours d'eau ont un dessin par forme — ligne, angle, extrémité —, et le plan dit pour chaque
 * case quels bords elle rejoint. Prendre le premier variant venu posait la même ligne est-ouest sur cent dix-sept cases de clôture, angles compris : la maquette montrait
 * alors un tracé qui ne se raccorde nulle part. Le repli sur le premier variant ne vaut que pour un sujet qui n'a pas de formes.
 */
function currentImage(array $sujets, string $code, array $joins = []): ?string
{
    $sujet = $sujets[$code] ?? null;
    if (!$sujet) {
        return null;
    }
    sort($joins);
    $wanted = $joins ? implode('', $joins) : null;

    $fallback = null;
    foreach ($sujet['variants'] as $variant) {
        $representations = $variant['representations'] ?? [];
        $image = null;
        foreach (array_reverse($representations) as $representation) {
            if (($representation['statut'] ?? '') === 'courante' && !empty($representation['path'])) {
                $image = $representation['path'];
                break;
            }
        }
        if ($image === null) {
            continue;
        }
        $shape = $variant['shape'] ?? null;
        if ($wanted !== null && $shape === $wanted) {
            return $image;
        }
        $fallback = $fallback ?? $image;
    }

    return $fallback;
}

$columns = $plan['grid']['columns'];
$rows = $plan['grid']['rows'];
$capture = new Capture();

// Les cases se posent dans l'ordre du rendu : le sol d'abord, puis ce qui se dresse dessus, de haut en bas — un sujet plus bas passe devant celui qui est derrière lui.
$ground = [];
$standing = [];
foreach ($plan['cells'] as $cell) {
    $type = $sujets[$cell['subject']]['type'] ?? '';
    if (in_array($type, GROUND_TYPES, true)) {
        $ground[] = $cell;
    } else {
        $standing[] = $cell;
    }
}
usort($standing, fn ($one, $other) => $one['row'] <=> $other['row']);

$missing = [];
$atlas = [];
$placed = 0;

$capture->start();
foreach (array_merge($ground, $standing) as $cell) {
    $code = $cell['subject'];
    $image = currentImage($sujets, $code, $cell['joins'] ?? []);
    $wide = $cell['columns'] ?? 1;
    $high = $cell['rows'] ?? 1;
    $left = ($cell['column'] - 1) * SCREEN_PIXELS_PER_TILE;
    $top = ($cell['row'] - 1) * SCREEN_PIXELS_PER_TILE;
    $width = $wide * SCREEN_PIXELS_PER_TILE;

    if ($image === null || !is_file("$root/assets/$image")) {
        $missing[$code] = ($missing[$code] ?? 0) + 1;
        ?>
<div class="trou" style="left: <?= $left ?>px; top: <?= $top ?>px; width: <?= $width ?>px; height: <?= $high * SCREEN_PIXELS_PER_TILE ?>px"><?= htmlspecialchars($code, ENT_QUOTES) ?></div>
        <?php
        continue;
    }

    // LA SPRITE EST POSÉE SUR LA LARGEUR DE SON EMPRISE, sa hauteur suivant ses propres proportions : un sujet qui se dresse déborde vers le HAUT de sa case, jamais vers le
    // bas — c'est son pied qui est planté là. On l'accroche donc par le bas de sa case, et on la laisse monter.
    // LA LARGEUR À L'ÉCRAN EST CELLE DU COUVERT, PAS DE L'EMPRISE. L'image a été demandée à la largeur de ce que le volume surplombe : la poser à la largeur du pied
    // rétrécirait la couronne d'un chêne de six cases jusqu'à deux, et tout le parc paraîtrait planté de bonsaïs. Elle se centre alors sur son emprise, qui reste ce qui
    // touche le sol.
    $spread = $sujets[$code]['couvert'] ?? $sujets[$code]['emprise'] ?? ['columns' => $wide, 'rows' => $high];
    $width = $spread['columns'] * SCREEN_PIXELS_PER_TILE;
    $left -= ($width - $wide * SCREEN_PIXELS_PER_TILE) / 2;

    [$imageWidth, $imageHeight] = getimagesize("$root/assets/$image");
    $height = (int) round($width * $imageHeight / $imageWidth);
    $bottom = $top + $high * SCREEN_PIXELS_PER_TILE;
    $placed++;
    // L'IMAGE EST EMBARQUÉE UNE FOIS, PAS MILLE. Une case ne porte qu'une classe ; l'image elle-même vit dans une règle de style, en clair dans la page. Répétée en adresse
    // sur chaque case, elle pèserait mille fois son poids ; laissée en chemin de fichier, elle ne s'afficherait pas du tout, un artefact n'étant qu'une page seule.
    // La classe porte l'IMAGE, pas le sujet : deux formes d'une même clôture sont deux dessins différents et ne peuvent pas partager une règle de style.
    $token = preg_replace('/[^a-z0-9]+/', '-', strtolower(pathinfo($image, PATHINFO_FILENAME)));
    $atlas[$token] = $image;
    ?>
<?php
    // L'EMPILEMENT SUIT LA PROFONDEUR, ET RIEN D'AUTRE : ce qui est planté plus près de la caméra se dessine PAR-DESSUS ce qui est derrière, quel que soit son type. Sans ça,
    // une touffe d'herbe posée devant un arbre passait sous son tronc (opérateur, 2026-08-06). La rangée du PIED décide — c'est là que le sujet touche le sol —, et c'est
    // exactement ainsi que le jeu affichera sa carte. La rangée est comptée depuis 1, donc l'ordre est directement lisible.
    $depth = (int) ($bottom / SCREEN_PIXELS_PER_TILE);
    ?>
<div class="pose s-<?= $token ?>" title="<?= htmlspecialchars($code, ENT_QUOTES) ?>"
     style="left: <?= $left ?>px; top: <?= $bottom - $height ?>px; width: <?= $width ?>px; height: <?= $height ?>px; z-index: <?= $depth ?>"></div>
    <?php
}
$scene = $capture->take();

$manquants = '';
ksort($missing);
foreach ($missing as $code => $count) {
    $manquants .= '<li><span class="code">' . htmlspecialchars($code, ENT_QUOTES) . '</span> '
        . $count . ' case' . ($count > 1 ? 's' : '') . '</li>';
}
$manquants = $manquants ?: '<li>Aucun : toutes les cases déclarées ont leur image.</li>';

// Le sol du parc : la sprite de la cellule par défaut, celle que le plan déclare, embarquée une fois et carrelée sur toute la scène.
$defaultImage = currentImage($sujets, $plan['default_cell']);
if ($defaultImage === null || !is_file("$root/assets/$defaultImage")) {
    throw new RuntimeException("la cellule par défaut {$plan['default_cell']} n'a aucune image courante — le sol de la scène serait inventé");
}
$defaultTile = base64_encode(file_get_contents("$root/assets/$defaultImage"));

$styles = '';
foreach ($atlas as $token => $image) {
    $data = base64_encode(file_get_contents("$root/assets/$image"));
    $styles .= ".pose.s-$token { background-image: url(data:image/png;base64,$data); }\n";
}

// CE QU'IL Y A SUR CHAQUE CASE, pour que le survol le dise. Dressé ici comme il l'est sur la page du plan : le même besoin, la même réponse.
$occupancy = [];
foreach ($plan['cells'] as $cell) {
    for ($c = $cell['column']; $c < $cell['column'] + ($cell['columns'] ?? 1); $c++) {
        for ($r = $cell['row']; $r < $cell['row'] + ($cell['rows'] ?? 1); $r++) {
            $occupancy["$c,$r"] = $cell['subject'];
        }
    }
}
const NOMS = ['BT-001' => 'Centre de soin', 'BT-002' => 'Maison de ferme', 'CH-001' => 'Herbe rase', 'CH-019' => 'Chemin',
              'CH-020' => 'Cours d\'eau', 'OB-010' => 'Barrière', 'TR-060' => 'Grand chêne', 'TR-061' => 'Bosquet de sapins',
              'TR-062' => 'Herbe haute', 'TR-063' => 'Pommier', 'TR-064' => 'Herbe clairsemée', 'TR-065' => 'Sapin'];

$capture->start();
?>
<title>Le parc — maquette montée</title>
<?= $faviconTag ?>
<style>
  :root { color-scheme: light dark; --paper: #e8ece6; --surface: #fff; --ink: #12211b; --muted: #5d6f63; --line: #c7d1c6; --accent: #2d6b3c;
          --sans: "Segoe UI", system-ui, sans-serif; --mono: ui-monospace, "Cascadia Mono", monospace; }
  @media (prefers-color-scheme: dark) {
    :root { --paper: #0f1512; --surface: #161e19; --ink: #e3eae2; --muted: #93a597; --line: #28352c; --accent: #7cc182; }
  }
  :root[data-theme="dark"] { --paper: #0f1512; --surface: #161e19; --ink: #e3eae2; --muted: #93a597; --line: #28352c; --accent: #7cc182; }
  :root[data-theme="light"] { --paper: #e8ece6; --surface: #fff; --ink: #12211b; --muted: #5d6f63; --line: #c7d1c6; --accent: #2d6b3c; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans); line-height: 1.55; }
  .wrap { width: min(100%, 1760px); margin: 0 auto; padding: 2rem 1rem 4rem; display: flex; flex-direction: column; gap: 1.4rem; }
  .eyebrow { margin: 0; font-family: var(--mono); font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); }
  h1 { margin: .3rem 0 0; font-size: clamp(1.6rem, 4vw, 2.3rem); font-weight: 650; letter-spacing: -.02em; }
  .lede { margin: .5rem 0 0; max-width: 64ch; color: var(--muted); }
  /* La scène est un cadre à taille fixe où chaque sprite est posée par ses coordonnées : c'est la carte, pas une mise en page.
     LE CADRE NE GRANDIT PAS AVEC LE ZOOM : il garde la taille de la fenêtre et fait défiler ce qui dépasse, dans les deux sens. C'est la piste, à l'intérieur, qui porte la
     taille agrandie. Autrement, agrandir la case à 32 ou 48 pixels poussait la scène hors de la page sans rien laisser à faire défiler. */
  /* LE DÉFILEMENT EST HORIZONTAL, ET LUI SEUL. En hauteur, la page s'allonge et la carte se lit d'un bout à l'autre en descendant ; borner la hauteur du cadre
     ajoutait un second défilement à l'intérieur du premier, et la molette ne savait plus lequel elle poussait (opérateur, 2026-08-06). */
  .scene-cadre { overflow-x: auto; overflow-y: hidden; background: var(--surface); border: 1px solid var(--line); border-radius: 3px; max-width: 100%; overscroll-behavior-x: contain; }
  .scene-cadre.tire { cursor: grabbing; }
  .scene-piste { position: relative; }
  /* LE FOND EST LA SPRITE DE LA CELLULE PAR DÉFAUT, RÉPÉTÉE — pas une couleur inventée. Le plan déclare l'herbe rase comme sol partout où rien n'est posé : peindre un vert
     approximatif à sa place montrait un parc qui n'est celui de personne, et cachait ce que la matière validée donne réellement une fois carrelée. */
  .scene {
    position: relative; background-repeat: repeat;
    background-image: url(data:image/png;base64,<?= $defaultTile ?>);
    background-size: <?= SCREEN_PIXELS_PER_TILE ?>px <?= SCREEN_PIXELS_PER_TILE ?>px;
  }
  .pose { position: absolute; background-size: 100% 100%; background-repeat: no-repeat; }
<?= $styles ?>
  /* Un trou se voit : magenta, la couleur que la chaîne détoure, donc ici ce qui reste à produire. */
  .trou {
    position: absolute; display: flex; align-items: center; justify-content: center;
    background: rgba(214, 0, 160, .28); outline: 1px solid rgba(214, 0, 160, .7);
    font-family: var(--mono); font-size: 8px; color: #4a0038;
  }
  /* L'OUTIL DE REVUE, LE MÊME QUE SUR LE PLAN. Le code est repris et adapté plutôt que partagé : celui du plan travaille sur le repère d'un SVG, la maquette est une scène
     posée en pixels. L'opérateur a accepté la duplication pour ne pas immobiliser la page du plan, dont il se sert. Les deux doivent converger un jour. */
  .barre { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem; }
  .mode { margin: 0; flex: 1 1 20rem; color: var(--muted); font-size: .9rem; }
  button { font: inherit; padding: .35rem .9rem; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 3px; cursor: pointer; }
  .zone { position: relative; }
  .zooms { display: inline-flex; gap: .3rem; }
  .zoom[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); font-weight: 600; }
  /* Le zoom agrandit la scène entière d'un seul geste : tout y est posé en pixels d'une case de 24, donc une mise à l'échelle suffit et rien n'est recalculé. Le cadre, lui,
     prend la taille qu'occupe la scène agrandie, sans quoi il continuerait de réserver la place de la petite. */
  .scene { cursor: crosshair; transform-origin: top left; }
  /* AU-DESSUS DE TOUTE LA CARTE : les sprites s'empilent désormais par leur profondeur, sur des niveaux qui vont jusqu'au nombre de rangées du plan. Ce qui appartient à la
     revue — le survol, la marque d'une remarque, la saisie — se pose donc bien plus haut, sinon une sprite de la rangée quarante passerait devant. */
  .survol {
    position: absolute; z-index: 1001; pointer-events: none; padding: .25rem .55rem;
    font-family: var(--mono); font-size: .78rem; white-space: nowrap;
    color: var(--paper); background: var(--ink); border-radius: 3px;
  }
  .survol[hidden] { display: none; }
  .marque { position: absolute; pointer-events: none; z-index: 1000; background: rgba(194, 65, 12, .4); outline: 2px solid #c2410c; }
  .saisie {
    position: absolute; z-index: 1002; width: min(26rem, calc(100% - 1.5rem));
    display: flex; flex-direction: column; gap: .55rem; padding: .9rem 1rem;
    background: var(--surface); border: 1px solid var(--accent); border-radius: 3px; box-shadow: 0 12px 28px rgba(8, 16, 10, .28);
  }
  .saisie[hidden] { display: none; }
  .saisie-ou { margin: 0; font-family: var(--mono); font-size: .8rem; color: var(--accent); }
  .saisie textarea { font: inherit; padding: .5rem .6rem; color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 3px; resize: vertical; }
  .saisie-boutons { display: flex; gap: .5rem; }
  .remarques { display: flex; flex-direction: column; gap: .7rem; max-width: 78ch; }
  .remarques-head { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
  .remarques-head h3 { margin: 0; font-size: 1.05rem; flex: 1 1 auto; }
  .remarques-vides { margin: 0; color: var(--muted); font-size: .9rem; }
  .remarques-vides[hidden] { display: none; }
  .remarques ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .4rem; }
  .remarques li { display: flex; align-items: baseline; gap: .7rem; padding: .45rem .8rem; background: var(--surface); border: 1px solid var(--line); border-radius: 3px; }
  .remarques li .quoi { flex: 1 1 auto; }
  .remarques .ou { font-family: var(--mono); font-size: .78rem; color: #c2410c; font-variant-numeric: tabular-nums; }
  .remarques li button { padding: .15rem .6rem; font-size: .8rem; }

  .manquants { margin: 0; padding-left: 1.2rem; color: var(--muted); display: flex; flex-direction: column; gap: .2rem; max-width: 64ch; }
  .manquants .code { font-family: var(--mono); color: var(--ink); }
  .compte { margin: 0; font-family: var(--mono); font-size: .8rem; color: var(--muted); }
<?= $reloadStyles ?>
</style>
<?= $reloadMarkup ?>

<div class="wrap">
  <header>
    <p class="eyebrow">GateBeast · maquette montée</p>
    <h1><?= htmlspecialchars($plan['title'], ENT_QUOTES) ?> — montée</h1>
    <p class="lede">Chaque sprite posée sur sa case, d'après le plan et le référentiel : le sol d'abord, puis ce qui se dresse dessus, de haut en bas. C'est la première fois
    que les sujets se voient ensemble, et donc la première fois qu'on peut juger s'ils appartiennent au même monde.</p>
  </header>

  <div class="barre">
    <p class="mode">Clique une case pour lui attacher une remarque. Les cases commentées se marquent en rouge.</p>
    <?php // Les trois tailles de case que le jeu fera varier : le zoom ne change QUE cette valeur, jamais les images — les sprites sont livrées assez fines pour les tenir. ?>
    <span class="zooms">
      <button type="button" class="zoom" data-zoom="24" aria-pressed="true">24 px</button>
      <button type="button" class="zoom" data-zoom="32" aria-pressed="false">32 px</button>
      <button type="button" class="zoom" data-zoom="48" aria-pressed="false">48 px</button>
    </span>
    <button type="button" class="copier">Copier le récapitulatif</button>
  </div>

  <div class="zone">
    <?php // LA PISTE PORTE LA TAILLE AGRANDIE, LE CADRE RESTE À LA TAILLE DE L'ÉCRAN. Sans elle, le zoom agrandissait le cadre lui-même : la scène débordait de la page et
          // il n'y avait plus rien à faire défiler, donc plus moyen de naviguer (opérateur, 2026-08-06). Un agrandissement se prévoit avec son moyen de se déplacer dedans. ?>
    <div class="scene-cadre">
      <div class="scene-piste">
      <div class="scene" id="scene" data-cote="<?= SCREEN_PIXELS_PER_TILE ?>" data-colonnes="<?= $columns ?>" data-lignes="<?= $rows ?>"
           data-defaut="<?= htmlspecialchars(NOMS[$plan['default_cell']] ?? $plan['default_cell'], ENT_QUOTES) ?>"
           data-cases="<?= htmlspecialchars(json_encode($occupancy, JSON_UNESCAPED_UNICODE), ENT_QUOTES) ?>"
           data-noms="<?= htmlspecialchars(json_encode(NOMS, JSON_UNESCAPED_UNICODE), ENT_QUOTES) ?>"
           style="width: <?= $columns * SCREEN_PIXELS_PER_TILE ?>px; height: <?= $rows * SCREEN_PIXELS_PER_TILE ?>px">
<?= $scene ?>
      </div>
      </div>
    </div>

    <div class="survol" hidden></div>

    <div class="saisie" hidden>
      <p class="saisie-ou"></p>
      <textarea rows="3" placeholder="Ce qui devrait changer ici."></textarea>
      <div class="saisie-boutons">
        <button type="button" class="poser">Attacher la remarque</button>
        <button type="button" class="supprimer" hidden>Supprimer</button>
        <button type="button" class="annuler">Annuler</button>
      </div>
    </div>
  </div>

  <div class="remarques">
    <div class="remarques-head">
      <h3>Les remarques</h3>
      <button type="button" class="copier">Copier le récapitulatif</button>
      <button type="button" class="effacer">Tout effacer</button>
    </div>
    <p class="remarques-vides">Aucune remarque pour l'instant.</p>
    <ul></ul>
  </div>

  <p class="compte"><?= $placed ?> sprites posées sur <?= $columns ?> × <?= $rows ?> cases, à <?= SCREEN_PIXELS_PER_TILE ?> pixels la case.</p>

  <div>
    <p class="lede">Ce qui manque encore — chaque case en magenta est une image qui reste à produire :</p>
    <ul class="manquants"><?= $manquants ?></ul>
  </div>
</div>

<script>
(function () {
  var scene = document.getElementById('scene');
  var zone = scene.closest('.zone');
  var survol = zone.querySelector('.survol');
  var saisie = zone.querySelector('.saisie');
  var saisieOu = zone.querySelector('.saisie-ou');
  var saisieTexte = zone.querySelector('textarea');
  var supprimer = zone.querySelector('.supprimer');
  var liste = document.querySelector('.remarques ul');
  var vide = document.querySelector('.remarques-vides');
  var effacer = document.querySelector('.effacer');

  var cote = Number(scene.dataset.cote);
  var colonnes = Number(scene.dataset.colonnes);
  var lignes = Number(scene.dataset.lignes);
  var cases = JSON.parse(scene.dataset.cases);
  var noms = JSON.parse(scene.dataset.noms);
  var defaut = scene.dataset.defaut;

  var echelle = 1;
  var piste = scene.parentNode;

  function zoomer(pixels) {
    var cadre = scene.closest('.scene-cadre');
    // Le point de la carte qui est au CENTRE de la fenêtre avant l'agrandissement, en cases : c'est lui qu'on remet au centre après, sinon un zoom envoie l'opérateur ailleurs
    // sur la carte et il doit se retrouver à chaque fois.
    var centreX = (cadre.scrollLeft + cadre.clientWidth / 2) / (cote * echelle);
    var centreY = (cadre.scrollTop + cadre.clientHeight / 2) / (cote * echelle);
    echelle = pixels / cote;
    scene.style.transform = 'scale(' + echelle + ')';
    // LA PISTE réserve la place que la scène occupe RÉELLEMENT une fois agrandie — une mise à l'échelle ne change pas la place qu'un élément demande à sa mise en page. Le CADRE,
    // lui, garde la taille de la fenêtre et fait défiler : c'est ce qui permet de se déplacer dans une carte plus grande que l'écran.
    piste.style.width = (colonnes * cote * echelle) + 'px';
    piste.style.height = (lignes * cote * echelle) + 'px';
    cadre.scrollLeft = centreX * cote * echelle - cadre.clientWidth / 2;
    cadre.scrollTop = centreY * cote * echelle - cadre.clientHeight / 2;
    Array.prototype.forEach.call(document.querySelectorAll('.zoom'), function (bouton) {
      bouton.setAttribute('aria-pressed', Number(bouton.dataset.zoom) === pixels ? 'true' : 'false');
    });
  }

  // SE DÉPLACER À LA SOURIS, en tirant la carte : les barres de défilement suffisent à la rigueur, mais on lit une carte en la faisant glisser. Le clic simple continue d'attacher
  // une remarque — seul un vrai glissement, au-delà de quelques pixels, compte comme un déplacement.
  var tire = null;
  var glisse = false;
  var cadreScene = scene.closest('.scene-cadre');
  cadreScene.addEventListener('mousedown', function (evenement) {
    tire = {x: evenement.clientX, y: evenement.clientY, gauche: cadreScene.scrollLeft, haut: cadreScene.scrollTop};
    glisse = false;
  });
  window.addEventListener('mousemove', function (evenement) {
    if (!tire) {
      return;
    }
    var dx = evenement.clientX - tire.x;
    var dy = evenement.clientY - tire.y;
    if (!glisse && Math.abs(dx) + Math.abs(dy) < 5) {
      return;
    }
    glisse = true;
    cadreScene.classList.add('tire');
    cadreScene.scrollLeft = tire.gauche - dx;
    cadreScene.scrollTop = tire.haut - dy;
    evenement.preventDefault();
  });
  window.addEventListener('mouseup', function () {
    tire = null;
    cadreScene.classList.remove('tire');
  });

  Array.prototype.forEach.call(document.querySelectorAll('.zoom'), function (bouton) {
    bouton.addEventListener('click', function () { zoomer(Number(bouton.dataset.zoom)); });
  });

  var MEMOIRE = 'gatebeast-maquette-parc-remarques';
  var remarques = [];
  var vise = null;

  try {
    remarques = JSON.parse(localStorage.getItem(MEMOIRE)) || [];
  } catch (erreur) {
    remarques = [];
  }

  function retenir() {
    try {
      localStorage.setItem(MEMOIRE, JSON.stringify(remarques));
    } catch (erreur) {
      // Une mémoire indisponible ne coûte que la survie au rechargement.
    }
  }

  /* La case sous un point de l'écran. La scène est posée en pixels, pas dans un repère à échelle : la case se lit directement, au décalage du cadre près et à ce que le
     cadre a défilé de côté. */
  function caseSous(x, y) {
    var cadre = scene.getBoundingClientRect();
    // La case se lit à l'échelle du moment : le cadre mesuré est déjà celui de la scène agrandie, donc la taille d'une case à l'écran l'est aussi.
    var pas = cote * echelle;
    var colonne = Math.floor((x - cadre.left) / pas) + 1;
    var ligne = Math.floor((y - cadre.top) / pas) + 1;
    if (colonne < 1 || ligne < 1 || colonne > colonnes || ligne > lignes) {
      return null;
    }

    return {colonne: colonne, ligne: ligne};
  }

  function nature(ou) {
    var code = cases[ou.colonne + ',' + ou.ligne];

    return code ? (noms[code] || code) + ' · ' + code : defaut;
  }

  function marquer() {
    Array.prototype.forEach.call(scene.querySelectorAll('.marque'), function (ancien) { ancien.remove(); });
    remarques.forEach(function (remarque) {
      var carre = document.createElement('div');
      carre.className = 'marque';
      carre.style.left = ((remarque.colonne - 1) * cote) + 'px';
      carre.style.top = ((remarque.ligne - 1) * cote) + 'px';
      carre.style.width = cote + 'px';
      carre.style.height = cote + 'px';
      scene.appendChild(carre);
    });
  }

  function afficher() {
    liste.innerHTML = '';
    vide.hidden = remarques.length > 0;
    remarques.forEach(function (remarque) {
      var ligne = document.createElement('li');
      var ou = document.createElement('span');
      ou.className = 'ou';
      ou.textContent = '(' + remarque.colonne + ',' + remarque.ligne + ')';
      var quoi = document.createElement('span');
      quoi.className = 'quoi';
      quoi.textContent = remarque.texte;
      var retirer = document.createElement('button');
      retirer.type = 'button';
      retirer.textContent = 'Retirer';
      retirer.addEventListener('click', function () {
        remarques.splice(remarques.indexOf(remarque), 1);
        retenir();
        marquer();
        afficher();
      });
      ligne.appendChild(ou);
      ligne.appendChild(quoi);
      ligne.appendChild(retirer);
      liste.appendChild(ligne);
    });
  }

  scene.addEventListener('mousemove', function (evenement) {
    var ou = caseSous(evenement.clientX, evenement.clientY);
    if (!ou) {
      survol.hidden = true;
      return;
    }
    var cadre = zone.getBoundingClientRect();
    survol.textContent = '(' + ou.colonne + ',' + ou.ligne + ') ' + nature(ou);
    survol.hidden = false;
    survol.style.left = Math.max(4, Math.min(evenement.clientX - cadre.left + 14, cadre.width - survol.offsetWidth - 4)) + 'px';
    survol.style.top = Math.max(4, evenement.clientY - cadre.top - survol.offsetHeight - 10) + 'px';
  });

  scene.addEventListener('mouseleave', function () { survol.hidden = true; });

  scene.addEventListener('click', function (evenement) {
    // Un glissement de carte n'attache pas de remarque : sans ça, chaque déplacement à la souris ouvrirait la saisie sur la case où le doigt s'est levé.
    if (glisse) {
      glisse = false;
      return;
    }
    var ou = caseSous(evenement.clientX, evenement.clientY);
    if (!ou) {
      return;
    }
    vise = ou;
    saisieOu.textContent = 'Case (' + ou.colonne + ',' + ou.ligne + ') — ' + nature(ou);
    var deja = remarques.filter(function (remarque) {
      return remarque.colonne === ou.colonne && remarque.ligne === ou.ligne;
    })[0];
    saisieTexte.value = deja ? deja.texte : '';
    supprimer.hidden = !deja;
    saisie.hidden = false;

    var cadre = zone.getBoundingClientRect();
    var gauche = evenement.clientX - cadre.left + 14;
    var dessus = evenement.clientY - cadre.top + 14;
    saisie.style.left = Math.max(8, Math.min(gauche, cadre.width - saisie.offsetWidth - 8)) + 'px';
    saisie.style.top = Math.max(8, Math.min(dessus, cadre.height - saisie.offsetHeight - 8)) + 'px';
    saisieTexte.focus({preventScroll: true});
  });

  zone.querySelector('.poser').addEventListener('click', function () {
    var texte = saisieTexte.value.trim();
    if (!vise || !texte) {
      return;
    }
    remarques = remarques.filter(function (remarque) {
      return !(remarque.colonne === vise.colonne && remarque.ligne === vise.ligne);
    });
    remarques.push({colonne: vise.colonne, ligne: vise.ligne, texte: texte});
    retenir();
    saisie.hidden = true;
    vise = null;
    marquer();
    afficher();
  });

  supprimer.addEventListener('click', function () {
    if (!vise) {
      return;
    }
    remarques = remarques.filter(function (remarque) {
      return !(remarque.colonne === vise.colonne && remarque.ligne === vise.ligne);
    });
    retenir();
    saisie.hidden = true;
    vise = null;
    marquer();
    afficher();
  });

  zone.querySelector('.annuler').addEventListener('click', function () {
    saisie.hidden = true;
    vise = null;
  });

  Array.prototype.forEach.call(document.querySelectorAll('.copier'), function (copier) {
    copier.addEventListener('click', function () {
      var texte = 'Maquette du parc\n' + (remarques.length ? remarques.map(function (remarque) {
        return '(' + remarque.colonne + ',' + remarque.ligne + ') : ' + remarque.texte;
      }).join('\n') : 'Aucune remarque.');
      // La copie passe par un champ caché : l'appel direct au presse-papiers est refusé dans le cadre où vit cet artefact.
      var holder = document.createElement('textarea');
      holder.value = texte;
      holder.setAttribute('readonly', 'readonly');
      holder.style.position = 'fixed';
      holder.style.opacity = '0';
      document.body.appendChild(holder);
      holder.select();
      var done = false;
      try {
        done = document.execCommand('copy');
      } catch (erreur) {
        done = false;
      }
      document.body.removeChild(holder);
      copier.textContent = done ? 'Copié' : 'Copie refusée';
      setTimeout(function () { copier.textContent = 'Copier le récapitulatif'; }, 1600);
    });
  });

  effacer.addEventListener('click', function () {
    remarques = [];
    retenir();
    marquer();
    afficher();
  });

  document.addEventListener('keydown', function (evenement) {
    if (evenement.key === 'Escape' && !saisie.hidden) {
      saisie.hidden = true;
      vise = null;
    }
  });

  marquer();
  afficher();
})();
</script>
<?= $reloadScript ?>
<?php
file_put_contents($outputPath, $capture->take());
printf("%s — %d sprites posées, %d sujet(s) sans image\n", $outputPath, $placed, count($missing));

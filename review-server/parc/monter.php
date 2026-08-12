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
// Le tracé de rune n'est pas un service que toute page charge : seule la maquette compose des sujets sur des cases, donc seule elle en a besoin.
require_once "$root/review-server/lib/Rune.php";
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
// A source melted into another page has no route of its own: its remarks are those of the final page, which carries the link to the server.
$notesScript = $route === null ? '' : Notes::get()->script($route);

// A PROJECTED TILE IS NOT SQUARE: 24 wide, 21 deep. Under the world's camera a ground depth is seen foreshortened, so a map laid on square cells was a map seen
// from straight above — not from the camera every sprite is drawn for. Both figures are the project's, held by scripts/tile_scale.py, and the ladder scales
// cleanly: at 32 the tile is 32 × 28, at 48 it is 48 × 42, so the zoom stays a plain scale factor and nothing is recomputed.
const SCREEN_TILE_WIDTH = 24;
const SCREEN_TILE_DEPTH = 21;
const SCREEN_PIXELS_PER_TILE = SCREEN_TILE_WIDTH;
/**
 * THE FIVE LAYER FAMILIES, IN THEIR STACKING ORDER, as the design settles it (rendu-en-calques.md): the ground, the ground decor, the world, the overhead, the
 * interface. This array decides nothing — it ORDERS what the referential declares, every type carrying its own `layer`.
 *
 * IT REPLACES A HARD-CODED LIST OF TYPES, `['sol', 'chemin', 'herbe']`, which guessed the layer instead of reading it and knew only two: the ground and the rest.
 * It already filed two types the wrong way, and it showed on the mock-up. Grass declares the `monde` layer — it stands up, it must sort by depth alongside trees
 * and characters — and ended up in the ground: a character standing behind a tuft would have been drawn in front of it. A stream declares `decor-au-sol` — one
 * walks on it — and was sorted by depth alongside buildings. A second truth beside the referential always ends up contradicting it; this one already had.
 */
const LAYER_ORDER = ['ground', 'ground-decor', 'world', 'above', 'interface'];
// Depth sorting applies ONLY within the living world: that is where what stands and what moves are found. A ground sorted by depth means nothing, and an
// overhead layer sorted by depth would fall behind what it is meant to cover.
const DEPTH_SORTED_LAYER = 'world';

// THE PLAN AND THE OUTPUT ARE ARGUMENTS, the park being only the default: there will be other mock-ups — the 32 × 24 reference scene first (operator, 2026-08-06) — and a mounter that can only
// mount one map forces you to copy it for the next. One mounter, as many mock-ups as needed.
$planPath = $argv[1] ?? "$root/assets/maquette/plan-parc-a.json";
$outputPath = $argv[2] ?? __DIR__ . '/maquette.html';
$plan = json_decode(file_get_contents($planPath), true, 512, JSON_THROW_ON_ERROR);
$referential = json_decode(file_get_contents("$root/assets/subjects.json"), true, 512, JSON_THROW_ON_ERROR);
$subjects = $referential['subjects'];
// Each type's layer, read from the referential and never guessed: it is what decides the stacking order, and it has no second source.
$layerOfType = array_map(fn (array $type): string => $type['layer'] ?? DEPTH_SORTED_LAYER, $referential['types']);

/**
 * The name of the shape that joins these edges, in the project's own order.
 *
 * THE ORDER IS THE COMPASS, NEVER THE ALPHABET, and getting that wrong made three shapes unreachable without a word. The referential names them `ne`, `nes`, `nesw` — north, east, south, west —
 * while sorting the letters gives `en`, `ens`, `ensw`, which match nothing. The pieces were drawn, declared and correct; the cell simply never asked for them by the name they carry, and fell back
 * on another shape. A trace that does not join up is what that looks like from the outside.
 */
function shapeKey(array $joins): string
{
    $key = '';
    foreach (['n', 'e', 's', 'w'] as $edge) {
        $key .= in_array($edge, $joins, true) ? $edge : '';
    }

    return $key;
}

/**
 * The rune of the individual this cell declares, traced over the sprite — nothing at all when the cell declares none.
 *
 * L'INDIVIDU EST UNE DONNÉE DE LA SCÈNE, PAS DE L'IMAGE (opérateur, 2026-08-12) : la sprite est celle de l'espèce, et c'est la case qui dit qui se tient là. Sans
 * ce nom il n'y a rien à tracer, et c'est un silence normal, pas une faute — la plupart des cases ne portent pas de créature.
 *
 * DEUX ÉCHELLES SE CROISENT ICI, ET LES CONFONDRE POSE LA MARQUE À CÔTÉ. L'ancre est déclarée dans les pixels de l'image LIVRÉE ; la scène affiche cette image à
 * une autre largeur. Le point se ramène donc au rapport des deux, et la taille de la rune se prend sur la case telle qu'elle est vue à l'écran, jamais sur
 * l'image. La rune manquante d'un individu déclaré, elle, lève : une case qui nomme quelqu'un et ne le marque pas serait un silence qu'on ne verrait jamais.
 */
function runeOn(array $subjects, array $cell, string $image, float $width, int $imageWidth, int $columns): string
{
    if (empty($cell['individual'])) {
        return '';
    }
    $anchor = null;
    foreach ($subjects[$cell['subject']]['variants'] ?? [] as $variant) {
        foreach ($variant['representations'] ?? [] as $representation) {
            if (($representation['path'] ?? '') === $image) {
                $anchor = $representation['rune_anchor_px'] ?? null;
            }
        }
    }
    if ($anchor === null) {
        throw new RuntimeException("la case ({$cell['column']},{$cell['row']}) déclare l'individu « {$cell['individual']} », et l'image {$image} n'a pas "
            . "d'ancre de rune — posez-la par « python3 scripts/set-rune-anchor.py » avant de le poser dans la scène.");
    }
    $scale = $width / $imageWidth;

    return Rune::get()->svg($cell['individual'], [
        'x' => $anchor['x'] * $scale,
        'y' => $anchor['y'] * $scale,
        'tilt_deg' => $anchor['tilt_deg'] ?? 0,
    ], $width / $columns);
}

/** The image a subject shows on THIS cell: the variant whose shape matches what the cell joins, and its current representation.
 *
 * THE SHAPE MATTERS, AND IGNORING IT RUINS THE MOCK-UP. A fence, a path, a watercourse have one drawing per shape — line, corner, end — and the plan says, for every cell, which edges it joins.
 * Taking the first variant that came laid the same east-west line on a hundred and seventeen fence cells, corners included: the mock-up then showed a trace that joined nothing. Falling back on the
 * first variant is only ever right for a subject that has no shapes.
 */
function currentImage(array $subjects, string $code, array $joins = [], array $fields = []): ?string
{
    $subject = $subjects[$code] ?? null;
    if (!$subject) {
        return null;
    }
    $wanted = $joins ? shapeKey($joins) : null;

    $fallback = null;
    foreach ($subject['variants'] as $variant) {
        $representations = $variant['representations'] ?? [];
        $image = null;
        foreach (array_reverse($representations) as $representation) {
            if (($representation['status'] ?? '') === 'current' && !empty($representation['path'])) {
                $image = $representation['path'];
                break;
            }
        }
        if ($image === null) {
            continue;
        }
        // WHAT THE CELL ASKS FOR BEYOND ITS SHAPE. A cell used to be able to name only its subject and the edges it joins, so a fence crossed by a path could not
        // be told to carry a GATE — the four gate drawings existed, declared and current, and no plan could reach them. The cell now names the variant fields it
        // wants; a variant matches only if it carries every one of them.
        $matches = true;
        foreach ($fields as $field => $value) {
            if (($variant[$field] ?? null) !== $value) {
                $matches = false;
                break;
            }
        }
        if (!$matches) {
            continue;
        }
        $shape = $variant['shape'] ?? null;
        if ($wanted !== null && $shape === $wanted) {
            return $image;
        }
        // THE FALLBACK IS FOR A SUBJECT WITHOUT SHAPES, AND FOR NOTHING ELSE.
        if ($wanted === null) {
            $fallback = $fallback ?? $image;
        }
    }

    // A SHAPE THAT WAS ASKED FOR AND IS NOT DRAWN IS A HOLE, NOT A NEIGHBOUR'S DRAWING. The fallback used to answer here too: an east-west end of a path, whose
    // `e` shape has never been drawn, came back carrying the crossroads drawing instead — laid on the map without a word, while the page announced that every
    // declared cell had its image. A substituted drawing is worse than a missing one: the hole is seen and fixed, the substitution is believed.
    return $wanted === null ? $fallback : null;
}

$columns = $plan['grid']['columns'];
$rows = $plan['grid']['rows'];
$capture = new Capture();

// CELLS ARE LAID IN LAYER ORDER, AND ONLY THE WORLD SORTS BY DEPTH — the design's two-step stacking. A subject lower in the scene passes in front of the one
// behind it, but only among its own kind: a path never passes in front of a building on the grounds of being lower, it belongs to a layer underneath.
$byLayer = array_fill_keys(LAYER_ORDER, []);
foreach ($plan['cells'] as $cell) {
    $type = $subjects[$cell['subject']]['type'] ?? '';
    $layer = $layerOfType[$type] ?? DEPTH_SORTED_LAYER;
    if (!isset($byLayer[$layer])) {
        throw new RuntimeException("le type « {$type} » déclare le calque « {$layer} », qui n'est pas une des cinq familles : " . implode(', ', LAYER_ORDER));
    }
    $byLayer[$layer][] = $cell;
}
usort($byLayer[DEPTH_SORTED_LAYER], fn ($one, $other) => $one['row'] <=> $other['row']);
$ordered = array_merge(...array_values($byLayer));

$missing = [];
$atlas = [];
$placed = 0;

$capture->start();
foreach ($ordered as $cell) {
    $code = $cell['subject'];
    $image = currentImage($subjects, $code, $cell['joins'] ?? [], $cell['variant'] ?? []);
    $wide = $cell['columns'] ?? 1;
    $high = $cell['rows'] ?? 1;
    $left = ($cell['column'] - 1) * SCREEN_PIXELS_PER_TILE;
    $top = ($cell['row'] - 1) * SCREEN_TILE_DEPTH;
    $width = $wide * SCREEN_PIXELS_PER_TILE;

    if ($image === null || !is_file("$root/assets/$image")) {
        $missing[$code] = ($missing[$code] ?? 0) + 1;
        ?>
<div class="trou" style="left: <?= $left ?>px; top: <?= $top ?>px; width: <?= $width ?>px; height: <?= $high * SCREEN_TILE_DEPTH ?>px"><?= htmlspecialchars($code, ENT_QUOTES) ?></div>
        <?php
        continue;
    }

    // THE SPRITE IS LAID ON THE WIDTH OF ITS FOOTPRINT, its height following its own proportions: a subject that stands overflows UPWARD out of its cell, never downward — its foot is what is
    // planted there. So it hangs from the bottom of its cell and is left to rise.
    // THE WIDTH ON SCREEN IS THE CANOPY'S, NOT THE FOOTPRINT'S. The image was ordered at the width of what the volume overhangs: laying it at the width of the foot would shrink the crown of a
    // six-cell oak down to two, and the whole park would look planted with bonsais. It is then centred on its footprint, which remains what touches the ground.
    $spread = $subjects[$code]['cover'] ?? $subjects[$code]['footprint'] ?? ['columns' => $wide, 'rows' => $high];
    $width = $spread['columns'] * SCREEN_PIXELS_PER_TILE;
    $left -= ($width - $wide * SCREEN_PIXELS_PER_TILE) / 2;

    [$imageWidth, $imageHeight] = getimagesize("$root/assets/$image");
    $height = (int) round($width * $imageHeight / $imageWidth);
    $bottom = $top + $high * SCREEN_TILE_DEPTH;
    $placed++;
    // THE IMAGE IS CARRIED ONCE, NOT A THOUSAND TIMES. A cell carries only a class; the image itself lives in a style rule, in clear inside the page. Repeated on every cell it would weigh a
    // thousand times its own weight; left as a file path it would not show at all, an artifact being a single page.
    // The class carries the IMAGE, not the subject: two shapes of the same fence are two different drawings and cannot share a style rule.
    $token = preg_replace('/[^a-z0-9]+/', '-', strtolower(pathinfo($image, PATHINFO_FILENAME)));
    $atlas[$token] = $image;
    ?>
<?php
    // STACKING FOLLOWS DEPTH, AND NOTHING ELSE: what is planted closer to the camera is drawn OVER what is behind, whatever its type. Without this, a tuft of grass laid in front of a tree went
    // under its trunk (operator, 2026-08-06). The row of the FOOT decides — that is where the subject touches the ground — and it is exactly how the game will draw its map. The row is counted
    // from 1, so the order reads directly.
    $depth = (int) ($bottom / SCREEN_TILE_DEPTH);
    ?>
<div class="pose s-<?= $token ?>" title="<?= htmlspecialchars($code, ENT_QUOTES) ?>"
     style="left: <?= $left ?>px; top: <?= $bottom - $height ?>px; width: <?= $width ?>px; height: <?= $height ?>px; z-index: <?= $depth ?>"><?=
     runeOn($subjects, $cell, $image, $width, $imageWidth, $spread['columns']) ?></div>
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

// The ground of the scene: the sprite of the default cell, the one the plan declares, carried once and tiled over the whole scene.
$defaultImage = currentImage($subjects, $plan['default_cell']);
if ($defaultImage === null || !is_file("$root/assets/$defaultImage")) {
    throw new RuntimeException("la cellule par défaut {$plan['default_cell']} n'a aucune image courante — le sol de la scène serait inventé");
}
$defaultTile = base64_encode(file_get_contents("$root/assets/$defaultImage"));

$styles = '';
foreach ($atlas as $token => $image) {
    $data = base64_encode(file_get_contents("$root/assets/$image"));
    $styles .= ".pose.s-$token { background-image: url(data:image/png;base64,$data); }\n";
}

// WHAT SITS ON EVERY CELL, so that hovering can say it. Drawn up here as it is on the plan page: the same need, the same answer.
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
<?= Theme::get()->css('graphite') ?>
  /* The mounted scene's own names, said in the shared ones — same reason as the plan: the Campagne page is assembled from both documents, and two palettes
     side by side could not be redressed together. */
  :root { --paper: var(--bg); --surface: var(--card); }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans); line-height: 1.55; }
  /* La largeur et les marges viennent du format commun (Layout) ; ne reste ici que ce qui est propre à cette page : sa colonne et l'espace entre ses blocs. */
  .wrap { display: flex; flex-direction: column; gap: 1.4rem; }
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
    background-size: <?= SCREEN_TILE_WIDTH ?>px <?= SCREEN_TILE_DEPTH ?>px;
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
  </div>

  <div class="zone">
    <?php // LA PISTE PORTE LA TAILLE AGRANDIE, LE CADRE RESTE À LA TAILLE DE L'ÉCRAN. Sans elle, le zoom agrandissait le cadre lui-même : la scène débordait de la page et
          // there was nothing left to scroll, and therefore no way to navigate (operator, 2026-08-06). A zoom is planned together with the means of moving inside it. ?>
    <div class="scene-cadre">
      <div class="scene-piste">
      <div class="scene" id="scene" data-cote="<?= SCREEN_TILE_WIDTH ?>" data-profondeur="<?= SCREEN_TILE_DEPTH ?>" data-colonnes="<?= $columns ?>" data-lignes="<?= $rows ?>"
           data-defaut="<?= htmlspecialchars(NOMS[$plan['default_cell']] ?? $plan['default_cell'], ENT_QUOTES) ?>"
           data-cases="<?= htmlspecialchars(json_encode($occupancy, JSON_UNESCAPED_UNICODE), ENT_QUOTES) ?>"
           data-noms="<?= htmlspecialchars(json_encode(NOMS, JSON_UNESCAPED_UNICODE), ENT_QUOTES) ?>"
           style="width: <?= $columns * SCREEN_PIXELS_PER_TILE ?>px; height: <?= $rows * SCREEN_TILE_DEPTH ?>px">
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
        <?php // LA MAQUETTE HÉRITE DE LA RÉOUVERTURE EN REJOIGNANT L'OUTIL COMMUN : le plan savait classer une remarque traitée et la rouvrir, elle non, alors
              // que le besoin y était le même. C'est le seul écart de comportement assumé par la convergence, et il ajoute au lieu de retirer. ?>
        <button type="button" class="rouvrir" hidden>Rouvrir</button>
        <button type="button" class="annuler">Annuler</button>
      </div>
    </div>
  </div>

  <div class="remarques">
    <div class="remarques-head">
      <h3>Les remarques</h3>
      <?php // PLUS AUCUN RELEVÉ À COPIER (opérateur, 2026-08-12 : « tous les mécanismes avec relevé doivent disparaitre, tout doit être mis sur le serveur »).
            // Même raison que sur le plan : les remarques vont au serveur en s'écrivant, et se lisent par `php scripts/remarks.php list`. ?>
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
  // Les éléments de l'outil de remarques ne se cherchent plus ici : l'outil commun les prend lui-même, par les sélecteurs que l'adaptateur lui donne en entier.

  var cote = Number(scene.dataset.cote);
  // LA PROFONDEUR EST UN SECOND PAS, ET ELLE VAUT POUR L'AXE VERTICAL. Une case projetee fait 24 sur 21 : se servir de la largeur pour les deux axes decale la
  // lecture d'une case tous les sept rangs, et un clic finit par designer la voisine du dessous.
  var profondeur = Number(scene.dataset.profondeur);
  var colonnes = Number(scene.dataset.colonnes);
  var lignes = Number(scene.dataset.lignes);
  var cases = JSON.parse(scene.dataset.cases);
  var noms = JSON.parse(scene.dataset.noms);
  var defaut = scene.dataset.defaut;

  var echelle = 1;
  var piste = scene.parentNode;

  function zoomer(pixels) {
    var cadre = scene.closest('.scene-cadre');
    // The point of the map at the CENTRE of the window before zooming, in cells: it is what gets put back in the centre afterwards, otherwise a zoom sends the operator elsewhere on the map and he
    // has to find his way again every time.
    var centreX = (cadre.scrollLeft + cadre.clientWidth / 2) / (cote * echelle);
    var centreY = (cadre.scrollTop + cadre.clientHeight / 2) / (profondeur * echelle);
    echelle = pixels / cote;
    scene.style.transform = 'scale(' + echelle + ')';
    // THE TRACK reserves the room the scene REALLY takes once scaled — scaling does not change the room an element asks of its layout. THE FRAME keeps the size of the window and scrolls: that is
    // what makes it possible to move around a map larger than the screen.
    piste.style.width = (colonnes * cote * echelle) + 'px';
    piste.style.height = (lignes * profondeur * echelle) + 'px';
    cadre.scrollLeft = centreX * cote * echelle - cadre.clientWidth / 2;
    cadre.scrollTop = centreY * profondeur * echelle - cadre.clientHeight / 2;
    Array.prototype.forEach.call(document.querySelectorAll('.zoom'), function (bouton) {
      bouton.setAttribute('aria-pressed', Number(bouton.dataset.zoom) === pixels ? 'true' : 'false');
    });
  }

  // MOVING WITH THE MOUSE, by dragging the map: scrollbars would do at a pinch, but a map is read by sliding it. A plain click still attaches a remark — only a real drag, beyond a few pixels,
  // counts as a movement.
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

  /* L'OUTIL DE REMARQUES EST CELUI DU PLAN, IL N'EN EXISTE PLUS DEUX (opérateur, 2026-08-12 : « tu dois unifier les fonctionnements autant que possible et en
     évitant absolument les régressions »). Quatre cent cinquante lignes vivaient ici, à l'identique de celles du plan : l'état des remarques, la saisie, la
     liste, le retrait, l'effacement, l'échappement, le dialogue avec le serveur. Elles ont divergé — le plan savait classer une remarque traitée et la rouvrir,
     la maquette ne l'a jamais su, alors que le besoin y était le même. Ce que la maquette hérite au passage, c'est exactement ce classement.
     NE RESTE ICI QUE CE QUI DÉPEND DU SUPPORT : où est la case sous le curseur, comment on marque une case, sous quel nom la section range ses remarques, et si
     un clic est bien un clic — cette scène se déplace à la souris, le plan non. */
  /* LA SECTION EST L'ENVELOPPE ENTIÈRE, PAS LA ZONE DU DESSIN, et c'est une distinction qui casse tout si on la manque : la liste des remarques, le compte des
     vides et le bouton d'effacement vivent À CÔTÉ de la zone, pas dedans. Cherchés depuis la zone, ils ne se trouvent pas — et l'outil s'attacherait à une
     section dont il ne trouve aucun élément. La zone, elle, reste le repère où se posent la saisie et le survol : c'est ce que `zone` dit à l'outil. */
  window.gatebeastRemarks.attach(scene.closest('.wrap'), {
    selectors: {
      'saisie': '.saisie',
      'saisie-ou': '.saisie-ou',
      'poser': '.poser',
      'annuler': '.annuler',
      'supprimer': '.supprimer',
      'rouvrir': '.rouvrir',
      'remarques-liste': '.remarques ul',
      'remarques-vides': '.remarques-vides',
      'effacer': '.effacer',
      'survol': '.survol'
    },
    section: 'maquette',
    surface: scene,
    zone: zone,
    titre: 'Maquette du parc',

    /* La case sous un point de l'écran. La scène est posée en pixels, pas dans un repère à échelle : la case se lit directement, au décalage du cadre près.
       La profondeur est un SECOND PAS, pour l'axe vertical — une case projetée fait 24 sur 21, et se servir de la largeur pour les deux axes décale la lecture
       d'une case tous les sept rangs. */
    caseSous: function (x, y) {
      var cadre = scene.getBoundingClientRect();
      var colonne = Math.floor((x - cadre.left) / (cote * echelle)) + 1;
      var ligne = Math.floor((y - cadre.top) / (profondeur * echelle)) + 1;
      if (colonne < 1 || ligne < 1 || colonne > colonnes || ligne > lignes) {
        return null;
      }

      return {colonne: colonne, ligne: ligne};
    },

    nature: function (ou) {
      var code = cases[ou.colonne + ',' + ou.ligne];

      return code ? (noms[code] || code) + ' · ' + code : defaut;
    },

    /* Le déplacement de la carte se termine par un clic sur la case où le doigt s'est relevé : sans ce refus, chaque déplacement ouvrait la saisie. */
    clicIgnore: function () {
      if (!glisse) {
        return false;
      }
      glisse = false;

      return true;
    },

    /* Les marques se posent PAR-DESSUS la scène, en pixels de son repère à elle : la scène est une pile d'éléments, pas un dessin vectoriel. */
    marquer: function (marques) {
      Array.prototype.forEach.call(scene.querySelectorAll('.marque'), function (ancien) { ancien.remove(); });
      marques.forEach(function (marque) {
        var carre = document.createElement('div');
        /* LA CLASSE S'ÉCRIT EN CLAIR, JAMAIS DANS UN TERNAIRE, et le contrôle des sélecteurs l'a prouvé sur-le-champ : la passe de renommage de la page fusionnée
           reconnaît `className = 'marque'`, pas `className = a ? 'marque …' : 'marque'`. L'élément gardait alors l'ancien nom pendant que la règle et le nettoyage
           prenaient le nouveau — la marque devenait invisible et rien ne l'aurait dit. Le classement se voit par l'opacité, posée ici, sans classe à inventer. */
        carre.className = 'marque';
        carre.style.opacity = marque.reglee ? '0.35' : '1';
        carre.style.left = ((marque.colonne - 1) * cote) + 'px';
        carre.style.top = ((marque.ligne - 1) * profondeur) + 'px';
        carre.style.width = cote + 'px';
        carre.style.height = profondeur + 'px';
        scene.appendChild(carre);
      });
    }
  });
})();
</script>
<?= $notesScript ?>
<?= $reloadScript ?>
<?php
file_put_contents($outputPath, $capture->take());
printf("%s — %d sprites posées, %d sujet(s) sans image\n", $outputPath, $placed, count($missing));

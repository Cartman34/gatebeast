<?php
/**
 * Usage: php review-server/parc/build.php
 *
 * Builds review-server/parc/page.html — the page of the park mock-up: the composition plan retained for it, commentable cell by cell, and later the mounted mock-up itself.
 *
 * Intention: this is the last link of a chain that never varies, and the chain is the rule — A RESOURCE IS PRODUCED BY A SCRIPT, THEN INCLUDED AS IT STANDS. Nothing is ever
 * made on the fly by a page. Here the plan is DECLARED in JSON, case by case ; scripts/build-composition-plan.py checks that declaration and draws the SVG from it ; and this
 * script starts from the same declaration — to discover the plans, and to read their title, their grid and their notes — then includes the drawing already produced, without
 * ever redrawing it. A plan declared but never drawn stops the build instead of slipping by unnoticed.
 *
 * THE PLAN IS SHOWN AT ITS FULL WIDTH, IN THE PAGE, and commented where it stands. It was briefly opened in a popin, which cannot work here: this page lives in a frame that
 * grows with its content, so "the whole height" is the whole document's height — the drawing ran off the screen and the wheel scrolled the background behind it. With a single
 * plan to look at, the page IS the plan, and the page's own scrolling is all it ever needed.
 *
 * Why PHP and not Python: PHP is this project's default language for lasting tooling, and this script needs nothing Python alone provides — it reads JSON, counts, and writes
 * markup.
 */

$root = __DIR__ . '/../..';
require_once $root . '/review-server/bootstrap.php';
bootBuild();
// THE SERVED ROUTE IS THE THIRD ARGUMENT: this page is served at /parc, but the same builder also produces a SOURCE of the Campagne page, melted into another one. A source carries no reload notice
// — the final page would otherwise hold two of them, on a route that is not its own. That absence of a route is `null`, never an empty string: an empty string is a string holding nothing, which is
// not the same as having no route at all. A command line can only carry text, so the emptiness it hands over is brought back to null right here.
$route = ($argv[3] ?? '/parc') ?: null;

// Services are taken here, at the top, once.
$favicon = Favicon::get();
$reload = Reload::get();
// LE PLAN ET LA SORTIE SE DONNENT EN ARGUMENT, le parc n'étant que la valeur par défaut : il y a d'autres plans à présenter — la scène de référence de 32 × 24 d'abord —, et
// un constructeur qui ne sait bâtir qu'une page oblige à le recopier pour la suivante. Sans argument, il découvre les plans du parc comme avant.
$declarations = isset($argv[1]) ? [$argv[1]] : glob("$root/assets/maquette/plan-*.json");
$outputPath = $argv[2] ?? __DIR__ . '/page.html';
sort($declarations);
if ($declarations === []) {
    throw new RuntimeException('aucun plan déclaré sous assets/maquette/');
}

// Les libellés des sujets : la seule prose de ce script, et elle ne décrit aucun parc — elle dit ce qu'un code désigne, ce que le référentiel des sujets ne donne pas en clair.
const LABELS = [
    'BT-001' => 'Centre de soin',
    'BT-002' => 'Maison de ferme',
    'CH-001' => 'Herbe rase',
    'CH-019' => 'Chemin',
    'CH-020' => 'Cours d\'eau',
    'OB-010' => 'Barrière',
    'TR-060' => 'Grand chêne',
    'TR-061' => 'Bosquet de sapins',
    'TR-062' => 'Herbe haute',
    'TR-063' => 'Pommier',
    'TR-064' => 'Herbe clairsemée',
    'TR-065' => 'Sapin',
];

function label(string $code): string
{
    return LABELS[$code] ?? $code;
}

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES);
}

require_once "$root/scripts/Capture.php";

$capture = new Capture();
$sections = '';
// THE PAGE TITLE COMES FROM THE PLAN, it is not written here: this builder also produces the Campagne scene, and announced it as "Le parc" — the operator caught it on 2026-08-07, no longer knowing
// which mock-up he was looking at. The plan carries its title, and that is what stands. With several plans at once, the page holds them all and none can name the whole.
$title = count($declarations) === 1
    ? json_decode(file_get_contents($declarations[0]), true, 512, JSON_THROW_ON_ERROR)['title']
    : 'Les plans de composition';
foreach ($declarations as $file) {
    $drawing = substr($file, 0, -strlen('.json')) . '.svg';
    if (!is_file($drawing)) {
        // Le dessin ne se fabrique pas ici : son absence dit que le plan n'a jamais été dessiné, ou jamais redessiné depuis que sa déclaration a changé. Les deux se corrigent
        // en relançant l'outil de dessin, jamais en s'en passant.
        throw new RuntimeException(basename($drawing) . ' manque : lancer scripts/build-composition-plan.py sur sa déclaration');
    }
    $plan = json_decode(file_get_contents($file), true, 512, JSON_THROW_ON_ERROR);
    $svg = file_get_contents($drawing);
    $source = str_replace("$root/", '', $file);
    $columns = $plan['grid']['columns'];
    $rows = $plan['grid']['rows'];

    // La géométrie de la grille, ANNONCÉE PAR LE DESSIN et jamais recalculée ici : c'est elle qui permet de retrouver la case sous le pointeur. La recalculer reviendrait à
    // tenir une seconde vérité, qui se tromperait le jour où le dessin change de proportions.
    if (!preg_match('/data-tile="([0-9.]+)" data-top="([0-9.]+)"/', $svg, $box)) {
        throw new RuntimeException("$source : le dessin n'annonce pas sa grille, la case sous le pointeur serait invention");
    }
    $side = (float) $box[1];
    $topOffset = (float) $box[2];

    // CE QU'IL Y A SUR CHAQUE CASE, dressé ici une fois pour toutes depuis la déclaration : la page s'en sert pour dire au survol ce qu'on a sous le pointeur. Une case dont
    // rien n'est déclaré porte la cellule par défaut — c'est le sol du parc, et c'est une réponse, pas un trou.
    $occupancy = [];
    foreach ($plan['cells'] as $cell) {
        $wide = $cell['columns'] ?? 1;
        $high = $cell['rows'] ?? 1;
        for ($c = $cell['column']; $c < $cell['column'] + $wide; $c++) {
            for ($r = $cell['row']; $r < $cell['row'] + $high; $r++) {
                $occupancy["$c,$r"] = $cell['subject'];
            }
        }
    }

    $tally = [];
    foreach ($plan['cells'] as $cell) {
        $tally[$cell['subject']] = ($tally[$cell['subject']] ?? 0) + 1;
    }
    ksort($tally);

    $key = preg_replace('/[^a-z0-9]+/', '-', strtolower(basename($file, '.json')));
    $declared = count($plan['cells']);

    $capture->start();
    ?>
<section class="plan" data-plan="<?= escape($plan['title']) ?>">
  <h2><?= escape($plan['title']) ?></h2>

  <div class="barre">
    <p class="mode">Clique une case du plan pour lui attacher une remarque. Les cases commentées se marquent en rouge.</p>
    <?php // LES TROIS TAILLES DE CASE, comme sur la maquette montée : le plan se lit à la même échelle que la scène, et la comparaison entre les deux cesse d'être un
          // exercice de mémoire. La taille est FIXE, elle ne s'ajuste pas à la fenêtre — ce qui dépasse se parcourt, le cadre défile et se tire à la souris. ?>
    <span class="zooms">
      <button type="button" class="zoom" data-zoom="24" aria-pressed="true">24 px</button>
      <button type="button" class="zoom" data-zoom="32" aria-pressed="false">32 px</button>
      <button type="button" class="zoom" data-zoom="48" aria-pressed="false">48 px</button>
    </span>
    <button type="button" class="taille">Ajuster à la fenêtre</button>
    <?php // Le récapitulatif se copie AUSSI d'ici, en tête du plan : la page vit dans un cadre qui ne défile pas de lui-même, donc un bouton posé tout en bas se cherche. ?>
    <button type="button" class="copier">Copier le récapitulatif</button>
  </div>

  <div class="zone">
    <div class="dessin" data-cle="<?= $key ?>" data-colonnes="<?= $columns ?>" data-lignes="<?= $rows ?>"
         data-cote="<?= $side ?>" data-haut="<?= $topOffset ?>" data-defaut="<?= escape(label($plan['default_cell'])) ?>"
         data-resolus="<?= escape(json_encode($plan['resolved'] ?? [], JSON_UNESCAPED_UNICODE)) ?>"
         data-cases="<?= escape(json_encode($occupancy, JSON_UNESCAPED_UNICODE)) ?>"
         data-noms="<?= escape(json_encode(LABELS, JSON_UNESCAPED_UNICODE)) ?>"><?= $svg ?></div>

    <div class="survol" hidden></div>

    <div class="saisie" hidden>
      <p class="saisie-ou"></p>
      <textarea rows="3" placeholder="Ce qui devrait changer ici."></textarea>
      <div class="saisie-boutons">
        <button type="button" class="poser">Attacher la remarque</button>
        <button type="button" class="supprimer" hidden>Supprimer</button>
        <button type="button" class="rouvrir" hidden>Rouvrir</button>
        <button type="button" class="annuler">Annuler</button>
      </div>
    </div>
  </div>

  <?php // CE QUE DIT LE PLAN, SOUS LE DESSIN ET EN HTML. C'était écrit dans l'image, où le texte est figé à la taille du tracé et ne se sélectionne pas. ?>
  <div class="dit">
    <ul class="notes">
      <?php foreach ($plan['notes'] as $note) { ?>
      <li><?= escape($note) ?></li>
      <?php } ?>
    </ul>

    <ul class="tally">
      <?php foreach ($tally as $code => $number) { ?>
      <li><span class="code"><?= escape($code) ?></span> <span><?= escape(label($code)) ?></span><span class="number"><?= $number ?></span></li>
      <?php } ?>
      <li class="rest"><span><?= escape(label($plan['default_cell'])) ?></span><span class="number">partout ailleurs</span></li>
    </ul>

    <p class="source"><?= escape($source) ?> · <?= $columns ?> × <?= $rows ?> cases · <?= $declared ?> cases déclarées</p>
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
</section>
    <?php
    $sections .= $capture->take();
}

$faviconTag = $favicon->tag();
// A source melted into another page carries no notice: no route puts out all three pieces at once, without the template having to know about that case.
$reloadStyles = $route === null ? '' : $reload->styles();
$reloadMarkup = $route === null ? '' : $reload->markup();
$reloadScript = $route === null ? '' : $reload->script($route);
$page = <<<HTML
<title>Le parc — maquette</title>
{$faviconTag}
<style>
  :root {
    color-scheme: light dark;
    --paper: #e8ece6;
    --surface: #ffffff;
    --ink: #12211b;
    --muted: #5d6f63;
    --line: #c7d1c6;
    --accent: #2d6b3c;
    --marque: #c2410c;
    --sans: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", sans-serif;
    --mono: ui-monospace, "SF Mono", "Cascadia Mono", "Roboto Mono", monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root { --paper: #0f1512; --surface: #161e19; --ink: #e3eae2; --muted: #93a597; --line: #28352c; --accent: #7cc182; --marque: #f97316; }
  }
  :root[data-theme="dark"] { --paper: #0f1512; --surface: #161e19; --ink: #e3eae2; --muted: #93a597; --line: #28352c; --accent: #7cc182; --marque: #f97316; }
  :root[data-theme="light"] { --paper: #e8ece6; --surface: #ffffff; --ink: #12211b; --muted: #5d6f63; --line: #c7d1c6; --accent: #2d6b3c; --marque: #c2410c; }

  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans); font-size: 16px; line-height: 1.55; }
  /* Le plan mène la largeur : il fait soixante-quatre cases de large et ne se lit qu'étalé. Le texte, lui, reste à sa mesure de lecture, quelle que soit celle de la page. */
  .wrap {
    width: min(100%, 1760px);
    margin: 0 auto;
    padding: clamp(1.5rem, 4vw, 3rem) clamp(1rem, 3vw, 2rem) 5rem;
    display: flex;
    flex-direction: column;
    gap: clamp(1.6rem, 3vw, 2.6rem);
  }

  .eyebrow { margin: 0; font-family: var(--mono); font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); }
  h1 { margin: .3rem 0 0; font-size: clamp(1.7rem, 4vw, 2.5rem); font-weight: 650; letter-spacing: -.02em; text-wrap: balance; }
  .lede { margin: .6rem 0 0; max-width: 64ch; color: var(--muted); }

  .plan { display: flex; flex-direction: column; gap: 1rem; }
  .plan h2 { margin: 0; font-size: 1.35rem; font-weight: 620; letter-spacing: -.01em; }
  .dit { display: flex; flex-direction: column; gap: .8rem; }
  .notes { margin: 0; padding-left: 1.2rem; max-width: 78ch; color: var(--muted); display: flex; flex-direction: column; gap: .25rem; }
  .notes li::marker { color: var(--accent); }

  .tally { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .4rem; }
  .tally li {
    display: flex;
    align-items: baseline;
    gap: .5rem;
    padding: .3rem .7rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 2px;
    font-size: .85rem;
  }
  .tally .code { font-family: var(--mono); font-size: .74rem; color: var(--muted); }
  .tally .number { font-family: var(--mono); font-variant-numeric: tabular-nums; font-weight: 600; color: var(--accent); }
  .tally .rest { border-style: dashed; }
  .tally .rest .number { font-weight: 400; color: var(--muted); }

  .barre { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem; }
  .mode { margin: 0; flex: 1 1 20rem; color: var(--muted); font-size: .9rem; }
  button {
    font: inherit;
    padding: .35rem .9rem;
    color: var(--ink);
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 3px;
    cursor: pointer;
  }
  button:disabled { opacity: .45; cursor: default; }

  .dessin { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 3px; cursor: crosshair; }
  .dessin svg { display: block; width: 100%; height: auto; }
  /* Taille réelle : le dessin reprend ses propres dimensions et la bande défile de côté — seule façon de lire une case dans un plan de soixante-quatre cases de large. */
  .dessin.reelle svg { width: auto; max-width: none; }
  /* LES TROIS TAILLES DE CASE, et la taille est FIXE : le dessin ne s'écrase plus pour tenir dans la fenêtre, il garde ses cases à 24, 32 ou 48 pixels et ce qui
     dépasse se parcourt — en largeur seulement, la page s'allongeant d'elle-même en hauteur. */
  .zooms { display: inline-flex; gap: .3rem; }
  .zoom[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); font-weight: 600; }
  .zone { overflow-x: auto; overflow-y: visible; }
  .dessin.fixe svg { width: auto; max-width: none; }
  .source { margin: 0; font-family: var(--mono); font-size: .72rem; color: var(--muted); }

  .zone { position: relative; }
  /* L'étiquette de survol : elle dit la nature de la case sous le pointeur, et rien d'autre. Elle ne prend jamais le clic — sans quoi elle se mettrait entre le pointeur et
     la case qu'on vise. */
  .survol {
    position: absolute;
    z-index: 2;
    pointer-events: none;
    padding: .25rem .55rem;
    font-family: var(--mono);
    font-size: .78rem;
    white-space: nowrap;
    color: var(--paper);
    background: var(--ink);
    border-radius: 3px;
  }
  .survol[hidden] { display: none; }
  /* La saisie s'ouvre SUR le plan, à l'endroit cliqué. Posée sous le dessin, elle obligeait à quitter des yeux la case dont on parle, et le champ qui prend le clavier
     ramenait la page tout en bas — on commentait à l'aveugle. */
  .saisie {
    position: absolute;
    z-index: 3;
    width: min(26rem, calc(100% - 1.5rem));
    display: flex;
    flex-direction: column;
    gap: .55rem;
    padding: .9rem 1rem;
    background: var(--surface);
    border: 1px solid var(--accent);
    border-radius: 3px;
    box-shadow: 0 12px 28px rgba(8, 16, 10, .28);
  }
  .saisie[hidden] { display: none; }
  .saisie-ou { margin: 0; font-family: var(--mono); font-size: .8rem; color: var(--accent); }
  .saisie textarea {
    font: inherit;
    padding: .5rem .6rem;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 3px;
    resize: vertical;
  }
  .saisie-boutons { display: flex; gap: .5rem; }

  /* PLEINE LARGEUR : une remarque est une phrase de l'opérateur, pas un paragraphe à lire au long — la borner à 78 caractères la repliait sur trois lignes courtes au milieu d'une page large, avec
     des marges vides de part et d'autre. La mesure de confort de lecture vaut pour de la prose, jamais pour une liste de notes courtes qu'on parcourt. */
  .remarques { display: flex; flex-direction: column; gap: .7rem; }
  .remarques-head { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
  .remarques-head h3 { margin: 0; font-size: 1.05rem; flex: 1 1 auto; }
  .remarques-vides { margin: 0; color: var(--muted); font-size: .9rem; }
  .remarques-vides[hidden] { display: none; }
  .remarques ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .4rem; }
  .remarques li {
    display: flex;
    align-items: baseline;
    gap: .7rem;
    padding: .45rem .8rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 3px;
  }
  .remarques li .quoi { flex: 1 1 auto; }
  .remarques .ou { font-family: var(--mono); font-size: .78rem; color: var(--marque); font-variant-numeric: tabular-nums; }
  /* Une remarque réglée reste dans la liste, en retrait : elle témoigne de ce qui a été fait sans réclamer l'attention de ce qui attend encore. */
  .remarques li.remarque--reglee { opacity: .5; }
  .remarques li.remarque--reglee .ou { color: var(--muted); }
  .remarques li button { padding: .15rem .6rem; font-size: .8rem; }

  footer { color: var(--muted); font-size: .9rem; max-width: 64ch; }
{$reloadStyles}
</style>
{$reloadMarkup}

<div class="wrap">
  <header>
    <p class="eyebrow">GateBeast · plan de composition</p>
    <h1>{$title}</h1>
    <p class="lede">Le plan retenu, déclaré case par case dans son propre fichier ; le dessin en est tiré, puis vérifié — chaque raccord doit être annoncé des deux côtés.
    Clique une case pour dire ce qui devrait y changer.</p>
  </header>

$sections
  <footer>
    <p>Deux choses manquent encore : le chemin n'a qu'une version dont la couleur est trop jaune, et le sapin isolé n'a plus de version courante. L'ouverture de la barrière est
    un trou dans la clôture, pas un portillon : un portillon est un variant de la barrière, et un plan ne déclare aujourd'hui que des sujets et leurs raccords.</p>
    <p>Reste à venir sur cette page : la maquette montée.</p>
  </footer>
</div>
HTML;

$page .= <<<'HTML'

<script>
document.querySelectorAll('.plan').forEach(function (section) {
  var dessin = section.querySelector('.dessin');
  var svg = dessin.querySelector('svg');
  var saisie = section.querySelector('.saisie');
  var saisieOu = section.querySelector('.saisie-ou');
  var saisieTexte = section.querySelector('textarea');
  var supprimer = section.querySelector('.supprimer');
  var rouvrir = section.querySelector('.rouvrir');
  var liste = section.querySelector('.remarques ul');
  var vide = section.querySelector('.remarques-vides');
  // TOUS les boutons de copie, pas le premier venu : la page en porte deux — un en tête du plan, un sous les remarques —, et n'en câbler qu'un laissait l'autre inerte. L'opérateur a cliqué celui du
  // bas, sous le compte des cases déclarées, et rien ne s'est produit : le bouton existait, il n'écoutait rien.
  var copiers = Array.prototype.slice.call(section.querySelectorAll('.copier'));
  var effacer = section.querySelector('.effacer');
  var taille = section.querySelector('.taille');

  var survol = section.querySelector('.survol');
  var titre = section.getAttribute('data-plan');
  var memoire = 'gatebeast-remarques-' + dessin.dataset.cle;
  var cote = Number(dessin.dataset.cote);
  var haut = Number(dessin.dataset.haut);
  var cases = JSON.parse(dessin.dataset.cases);
  var noms = JSON.parse(dessin.dataset.noms);
  var defaut = dessin.dataset.defaut;
  var remarques = [];
  var vise = null;

  /* UNE REMARQUE TRAITÉE SE RANGE, ELLE NE DISPARAÎT PAS. Le plan publié porte la liste des cases dont je me suis occupé ; la page les marque résolues : leur croix passe au
     gris pâle sur le dessin, elles sortent du récapitulatif, et le texte reste consultable d'un clic. L'opérateur peut en rouvrir une : elle redevient active chez lui, et
     ce choix ne vit que dans son navigateur — moi je ne sais que ce que le plan déclare. */
  var traitees = {};
  JSON.parse(dessin.dataset.resolus || '[]').forEach(function (cle) { traitees[cle] = true; });

  var MEMOIRE_ROUVERTES = memoire + '-rouvertes';
  var rouvertes = {};
  try {
    rouvertes = JSON.parse(localStorage.getItem(MEMOIRE_ROUVERTES)) || {};
  } catch (erreur) {
    rouvertes = {};
  }

  function resolue(remarque) {
    var cle = remarque.colonne + ',' + remarque.ligne;

    return Boolean(traitees[cle]) && !rouvertes[cle] && !remarque.neuve;
  }

  /* La case sous un point de l'écran, dans le repère du dessin : le dessin est affiché à la largeur que la page lui laisse, donc tout passe par son échelle du moment. Rend
     null hors de la grille — les marges, le titre et les notes ne sont pas des cases. */
  function caseSous(x, y) {
    var cadre = svg.getBoundingClientRect();
    var echelle = cadre.width / svg.viewBox.baseVal.width;
    var colonne = Math.floor((x - cadre.left) / echelle / cote) + 1;
    var ligne = Math.floor(((y - cadre.top) / echelle - haut) / cote) + 1;
    if (colonne < 1 || ligne < 1 || colonne > Number(dessin.dataset.colonnes) || ligne > Number(dessin.dataset.lignes)) {
      return null;
    }

    return {colonne: colonne, ligne: ligne};
  }

  function nature(ou) {
    var code = cases[ou.colonne + ',' + ou.ligne];

    return code ? (noms[code] || code) + ' · ' + code : defaut;
  }

  try {
    remarques = JSON.parse(localStorage.getItem(memoire)) || [];
  } catch (erreur) {
    remarques = [];
  }

  function retenir() {
    try {
      localStorage.setItem(memoire, JSON.stringify(remarques));
    } catch (erreur) {
      // Une mémoire indisponible ne coûte que la survie au rechargement : les remarques de la séance en cours, elles, restent lisibles et copiables.
    }
  }

  /* Les cases commentées se marquent SUR le dessin, dans son propre repère : le repère suit l'ajustement et la taille réelle tout seul, là où une pastille posée par-dessus
     en pixels se décalerait dès que la largeur change. */
  function marquer() {
    svg.querySelectorAll('[data-marque]').forEach(function (ancien) { ancien.remove(); });
    remarques.forEach(function (remarque) {
      var carre = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      carre.setAttribute('x', (remarque.colonne - 1) * cote);
      carre.setAttribute('y', (remarque.ligne - 1) * cote + haut);
      carre.setAttribute('width', cote);
      carre.setAttribute('height', cote);
      // Une remarque traitée reste visible, mais discrète : gris pâle et trait fin, elle ne réclame plus l'œil comme celles qui attendent encore.
      var reglee = resolue(remarque);
      carre.setAttribute('fill', reglee ? '#8a8f88' : '#c2410c');
      carre.setAttribute('fill-opacity', reglee ? '0.15' : '0.4');
      carre.setAttribute('stroke', reglee ? '#8a8f88' : '#c2410c');
      carre.setAttribute('stroke-width', Math.max(1, cote * (reglee ? 0.06 : 0.15)));
      carre.setAttribute('data-marque', '1');
      svg.appendChild(carre);
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
      if (resolue(remarque)) {
        ligne.className = 'remarque--reglee';
      }
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
    // Les deux commandes restent OFFERTES, même sans remarque : un bouton qui apparaît et disparaît selon l'état oblige à deviner s'il existe, et l'opérateur a constaté
    // l'écart avec la page des sprites, où ils sont toujours là. Copier un récapitulatif vide ne coûte rien ; ne pas trouver le bouton, si.
    copiers.forEach(function (bouton) { bouton.disabled = false; });
    effacer.disabled = false;
  }

  dessin.addEventListener('mousemove', function (evenement) {
    var ou = caseSous(evenement.clientX, evenement.clientY);
    if (!ou) {
      survol.hidden = true;
      return;
    }
    var zone = section.querySelector('.zone').getBoundingClientRect();
    survol.textContent = '(' + ou.colonne + ',' + ou.ligne + ') ' + nature(ou);
    survol.hidden = false;
    survol.style.left = Math.max(4, Math.min(evenement.clientX - zone.left + 14, zone.width - survol.offsetWidth - 4)) + 'px';
    survol.style.top = Math.max(4, evenement.clientY - zone.top - survol.offsetHeight - 10) + 'px';
  });

  dessin.addEventListener('mouseleave', function () {
    survol.hidden = true;
  });

  dessin.addEventListener('click', function (evenement) {
    var ou = caseSous(evenement.clientX, evenement.clientY);
    if (!ou) {
      return;
    }
    var colonne = ou.colonne;
    var ligne = ou.ligne;
    vise = ou;
    saisieOu.textContent = 'Case (' + colonne + ',' + ligne + ') — ' + nature(ou);
    // Une case déjà commentée rouvre SA remarque, pour la corriger ou la compléter : un champ vide inviterait à la réécrire, et on se retrouverait avec deux avis sur la
    // même case sans savoir lequel est le bon.
    var deja = remarques.filter(function (remarque) {
      return remarque.colonne === colonne && remarque.ligne === ligne;
    })[0];
    saisieTexte.value = deja ? deja.texte : '';
    // Le bouton de suppression n'apparaît que là où il y a quelque chose à supprimer : sur une case vierge il ne voudrait rien dire.
    supprimer.hidden = !deja;
    // Une remarque réglée se rouvre d'un clic : elle redevient active, ressort au récapitulatif, et sa marque reprend sa couleur.
    rouvrir.hidden = !(deja && resolue(deja));
    saisie.hidden = false;

    // La carte s'ouvre à l'endroit cliqué, puis se rabat dans la zone si elle en sortirait : une saisie qui déborde du plan est une saisie qu'on va chercher au lieu de la lire.
    var zone = section.querySelector('.zone').getBoundingClientRect();
    var gauche = evenement.clientX - zone.left + 14;
    var dessus = evenement.clientY - zone.top + 14;
    saisie.style.left = Math.max(8, Math.min(gauche, zone.width - saisie.offsetWidth - 8)) + 'px';
    saisie.style.top = Math.max(8, Math.min(dessus, zone.height - saisie.offsetHeight - 8)) + 'px';
    // preventScroll : sans lui, donner le clavier au champ ramène la page sur lui, et le plan disparaît de l'écran au moment précis où on le commente.
    saisieTexte.focus({preventScroll: true});
  });

  section.querySelector('.poser').addEventListener('click', function () {
    var texte = saisieTexte.value.trim();
    if (!vise || !texte) {
      return;
    }
    // Une case ne porte qu'une remarque : celle qu'on vient d'écrire remplace la précédente au lieu de s'ajouter à côté d'elle.
    remarques = remarques.filter(function (remarque) {
      return !(remarque.colonne === vise.colonne && remarque.ligne === vise.ligne);
    });
    // NEUVE : écrite APRÈS la résolution que le plan déclare. Sans cette marque, une remarque posée sur une case déjà traitée naissait grise, donc lue comme réglée alors qu'elle venait d'être écrite
    // — l'opérateur l'a constaté sur « (47,43) Herbe rase ». Ce que le plan déclare résolu, ce sont les remarques d'avant lui, jamais celles qui suivront.
    remarques.push({colonne: vise.colonne, ligne: vise.ligne, texte: texte, neuve: true});
    retenir();
    saisie.hidden = true;
    vise = null;
    marquer();
    afficher();
  });

  rouvrir.addEventListener('click', function () {
    if (!vise) {
      return;
    }
    rouvertes[vise.colonne + ',' + vise.ligne] = true;
    try {
      localStorage.setItem(MEMOIRE_ROUVERTES, JSON.stringify(rouvertes));
    } catch (erreur) {
      // Sans mémoire, la réouverture ne survit pas au rechargement : le texte, lui, n'est jamais en jeu.
    }
    rouvrir.hidden = true;
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

  section.querySelector('.annuler').addEventListener('click', function () {
    saisie.hidden = true;
    vise = null;
  });

  saisieTexte.addEventListener('keydown', function (evenement) {
    if (evenement.key === 'Enter' && (evenement.metaKey || evenement.ctrlKey)) {
      section.querySelector('.poser').click();
    }
  });

  copiers.forEach(function (copier) {
  copier.addEventListener('click', function () {
    // Le récapitulatif ne porte QUE ce qui attend encore : renvoyer une remarque déjà traitée la ferait refaire.
    var vivantes = remarques.filter(function (remarque) { return !resolue(remarque); });
    var texte = titre + '\n' + (vivantes.length ? vivantes.map(function (remarque) {
      return '(' + remarque.colonne + ',' + remarque.ligne + ') : ' + remarque.texte;
    }).join('\n') : 'Aucune remarque.');
    // LA COPIE PASSE PAR UN CHAMP CACHÉ, comme sur la page des sprites où elle a toujours fonctionné. L'appel direct au presse-papiers est refusé dans le cadre où vit cet
    // artefact : il échoue sans rien dire, et le bouton paraît cassé. Sélectionner le texte dans un champ et le copier marche partout.
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

    if (done) {
      copier.textContent = 'Copié';
      setTimeout(function () { copier.textContent = 'Copier le récapitulatif'; }, 1600);
      return;
    }
    // Rien n'a pu être copié : le texte est mis sous les yeux et déjà sélectionné, plutôt que laissé à reconstituer.
    saisieOu.textContent = 'Récapitulatif — à copier à la main';
    saisieTexte.value = texte;
    saisie.hidden = false;
    supprimer.hidden = true;
    saisie.style.left = '8px';
    saisie.style.top = '8px';
    saisieTexte.select();
  });
  });

  effacer.addEventListener('click', function () {
    remarques = [];
    retenir();
    marquer();
    afficher();
  });

  /* LA TAILLE DE CASE COMMANDE LA LARGEUR DU DESSIN, et elle est fixe : vingt-quatre, trente-deux ou quarante-huit pixels, comme sur la maquette montée, pour que
     le plan et la scène se lisent à la même échelle. Ce qui dépasse se parcourt en largeur ; « Ajuster à la fenêtre » rend la main à la mise en page. */
  /* LA LARGEUR SE CALCULE SUR LE DESSIN ENTIER, PAS SUR LES SEULES CASES : le tracé porte aussi son titre, ses marges et sa légende, tous comptés dans son repère.
     Poser la largeur à « colonnes fois la taille de case » donnait donc des cases plus grandes que demandé — le dessin entier faisait la taille de sa grille seule.
     On passe par le rapport du repère : une case du repère vaut « cote » unités, on veut qu'elle en fasse « pixels » à l'écran, et tout le reste suit. */
  function largeurPour(pixels) {
    return svg.viewBox.baseVal.width / Number(dessin.dataset.cote) * pixels;
  }

  function zoomer(pixels) {
    dessin.classList.add('fixe');
    svg.style.width = largeurPour(pixels) + 'px';
    taille.textContent = 'Ajuster à la fenêtre';
    Array.prototype.forEach.call(section.querySelectorAll('.zoom'), function (bouton) {
      bouton.setAttribute('aria-pressed', Number(bouton.dataset.zoom) === pixels ? 'true' : 'false');
    });
  }

  Array.prototype.forEach.call(section.querySelectorAll('.zoom'), function (bouton) {
    bouton.addEventListener('click', function () { zoomer(Number(bouton.dataset.zoom)); });
  });

  taille.addEventListener('click', function () {
    var fixe = dessin.classList.toggle('fixe');
    svg.style.width = fixe ? largeurPour(24) + 'px' : '';
    taille.textContent = fixe ? 'Ajuster à la fenêtre' : 'Taille par case';
    Array.prototype.forEach.call(section.querySelectorAll('.zoom'), function (bouton) {
      bouton.setAttribute('aria-pressed', fixe && Number(bouton.dataset.zoom) === 24 ? 'true' : 'false');
    });
  });

  zoomer(24);

  document.addEventListener('keydown', function (evenement) {
    if (evenement.key === 'Escape' && !saisie.hidden) {
      saisie.hidden = true;
      vise = null;
    }
  });

  marquer();
  afficher();
});
</script>
{$reloadScript}
HTML;

file_put_contents($outputPath, $page);
printf("%s — %d plan(s), %.1f Ko\n", $outputPath, count($declarations), strlen($page) / 1024);

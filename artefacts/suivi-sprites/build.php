<?php
/**
 * Usage: php artefacts/suivi-sprites/build.php [sortie.html]
 *
 * Builds the sprite tracking page in PHP: a grid of subjects, and one full-screen popin per subject holding its variants, their versions and the actions.
 *
 * Intention: this is the PHP side of the migration decided on 2026-08-06. It is written BESIDE the Python builder, which stays in place and keeps producing the published page — nothing can break
 * while the two are compared. It is also the first page assembled from the shared modules of artefacts/lib/ rather than from its own copy of everything: the inventory reader, the thumbnail factory
 * and the relevé all live there and serve the other pages too.
 *
 * WHAT IT DELIBERATELY DOES NOT DO YET, and which the Python one still does: the filters by state, the measured criteria and their reports, the judgements, the frozen consigne shown beside an image,
 * the stray files found on disk. They come next, module by module — a page that claims to replace another must be compared to it feature by feature, not declared equivalent.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/artefacts/lib/Inventaire.php';
require_once $root . '/artefacts/lib/Vignette.php';
require_once $root . '/artefacts/lib/Releve.php';
require_once $root . '/artefacts/lib/Theme.php';

const SCREEN_PIXELS_PER_TILE = 24;   // ce qu'une case mesure à l'écran — la valeur du projet, tenue par scripts/tile_scale.py
const COMPARE_PIXELS_PER_TILE = 48;  // ce qu'une case mesure dans la FSP, où l'on juge et compare (opérateur, 2026-08-06)

$outputPath = $argv[1] ?? __DIR__ . '/page-php.html';
$inventaire = new Inventaire($root);
$vignettes = new Vignette($root);

const TYPE_LABELS = [
    'sol' => 'Sol', 'chemin' => 'Chemin', 'cours-d-eau' => "Cours d'eau", 'cloture' => 'Clôture et mur',
    'arbre' => 'Arbre', 'bosquet-arbres' => "Bosquet d'arbres", 'herbe' => 'Herbe',
    'batiment' => 'Bâtiment', 'humain' => 'Humain', 'creature' => 'Créature',
];

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES);
}

/** La première lettre en majuscule, et elle seule — la règle d'affichage du projet. */
function capitale(string $text): string
{
    return mb_strtoupper(mb_substr($text, 0, 1)) . mb_substr($text, 1);
}

/** L'image d'une représentation, réduite à la taille demandée, ou null si le fichier manque — un trou se montre, il ne se cache pas. */
function image(Vignette $vignettes, array $representation, int $width): ?array
{
    try {
        return $vignettes->reduire($representation['path'], $width);
    } catch (RuntimeException $fault) {
        fwrite(STDERR, $fault->getMessage() . "\n");

        return null;
    }
}

$sections = '';
$popins = '';
$missing = [];
$compte = [];

foreach ($inventaire->types() as $typeName => $type) {
    $codes = $inventaire->sujetsOfType($typeName);
    if (!$codes) {
        continue;
    }
    $tiles = '';
    foreach ($codes as $code) {
        $sujet = $inventaire->sujet($code);
        $spread = $inventaire->spread($sujet);
        $main = $inventaire->mainVariant($sujet);
        $current = $main ? $inventaire->currentRepresentation($main) : null;
        $produced = 0;
        foreach ($sujet['variants'] as $variant) {
            $produced += $variant['representations'] ? 1 : 0;
        }
        $picture = '<span class="tuile-vide">à produire</span>';
        if ($current) {
            $shot = image($vignettes, $current, SCREEN_PIXELS_PER_TILE * $spread['columns']);
            if ($shot) {
                $picture = sprintf('<img src="%s" width="%d" height="%d" alt="">', $shot[0], $shot[1], $shot[2]);
            } else {
                $missing[] = $current['path'];
            }
        }
        // L'ÉTAT DU SUJET EST CELUI DE SES VARIANTS, et le plus fort mène : un sujet dont une seule image est à reprendre est à reprendre, quoi que disent les
        // autres. C'est sur cet état que les filtres agissent, et c'est celui qu'on cherche quand on ouvre la page — ce qui reste dû, pas ce qui est fini.
        $etats = [];
        foreach ($sujet['variants'] as $variant) {
            $etats[] = etatDuVariant($inventaire, $variant);
        }
        $etat = in_array('a-reprendre', $etats, true) ? 'a-reprendre'
            : (in_array('a-produire', $etats, true) ? 'a-produire'
            : (in_array('validee', $etats, true) ? 'validee' : 'produite'));
        $compte[$etat] = ($compte[$etat] ?? 0) + 1;
        $tiles .= sprintf(
            '        <button type="button" class="tuile" data-sujet="%s" data-etat="%s"><span class="tuile-image">%s</span>'
            . '<span class="tuile-nom">%s</span><span class="tuile-compte">%d/%d variant%s</span></button>' . "\n",
            escape($code), escape($etat), $picture, escape(capitale($inventaire->label($code))), $produced, count($sujet['variants']),
            count($sujet['variants']) > 1 ? 's' : ''
        );
        $popins .= popin($inventaire, $vignettes, $root, $code, $sujet);
    }
    $sections .= sprintf(
        "    <section class=\"type\">\n      <h2>%s <span class=\"slug\">%s</span></h2>\n      <div class=\"grille\">\n%s      </div>\n    </section>\n",
        escape(TYPE_LABELS[$typeName] ?? $typeName), escape($typeName), $tiles
    );
}

/** L'état d'un variant, en un mot : ce sur quoi les filtres de la grille agissent. */
function etatDuVariant(Inventaire $inventaire, array $variant): string
{
    $current = $inventaire->currentRepresentation($variant);
    if (!$current) {
        return 'a-produire';
    }

    return $current['verdict'] ?? 'produite';
}

/** Les mesures d'une image, dites en clair : ce que l'export a constaté sur le fichier livré. Rien n'est recalculé ici — la page montre ce qui est écrit. */
/**
 * TOUTES les mensurations d'une image, et pas une sélection : ce que le sujet déclare — emprise, couvert, hauteur — et ce que l'export a mesuré sur le fichier.
 * Choisir trois chiffres à montrer, c'est décider à la place de l'opérateur lequel compte, et c'est justement ce qu'il regarde quand une image lui paraît fausse.
 */
function mesures(array $representation, array $sujet): string
{
    $lignes = [];
    $emprise = $sujet['emprise'];
    $couvert = $sujet['couvert'] ?? null;
    // CHAQUE MESURE SUR SA LIGNE, et l'emprise, le couvert et la hauteur d'abord : ce sont les trois seuils contre lesquels une image se juge. Groupées sur une
    // ligne, elles se lisaient comme une phrase et il fallait les chercher au milieu.
    $lignes[] = ['Emprise au sol', sprintf('%d × %d case%s', $emprise['columns'], $emprise['rows'], $emprise['columns'] > 1 ? 's' : '')];
    $lignes[] = ['Couvert', $couvert ? sprintf('%d × %d cases', $couvert['columns'], $couvert['rows']) : 'égal à l\'emprise'];
    $lignes[] = ['Hauteur déclarée', sprintf('%s case%s', $sujet['hauteur'] ?? '—', ($sujet['hauteur'] ?? 0) > 1 ? 's' : '')];

    $measures = $representation['mesures'] ?? null;
    if ($measures) {
        if (isset($measures['delivered_px'])) {
            $lignes[] = ['Livrée', sprintf('%d × %d px', $measures['delivered_px']['width'], $measures['delivered_px']['height'])];
        }
        if (isset($measures['master_size_px'])) {
            $lignes[] = ['Maître', sprintf('%d × %d px', $measures['master_size_px']['width'], $measures['master_size_px']['height'])];
        }
        if (isset($measures['silhouette_px'])) {
            $s = $measures['silhouette_px'];
            $part = $measures['silhouette_share'] ?? null;
            $lignes[] = ['Silhouette', sprintf('%d × %d px%s', $s['width'], $s['height'],
                $part ? sprintf(' · %s %% de la largeur, %s %% de la hauteur', $part['width'], $part['height']) : '')];
        }
        if (isset($measures['contact_px'])) {
            $lignes[] = ['Contact au sol', sprintf('%d px, de %d à %d', $measures['contact_px']['width'], $measures['contact_px']['left'], $measures['contact_px']['right'])];
        }
        if (isset($measures['anchor_px'])) {
            $lignes[] = ['Point de pose', sprintf('%s, %s px', $measures['anchor_px']['x'], $measures['anchor_px']['y'])];
        }
        if (isset($measures['hauteur'])) {
            $lignes[] = [$measures['hauteur']['tenue'] ? 'Hauteur tenue' : 'HAUTEUR HORS FOURCHETTE', $measures['hauteur']['constat']];
        }
    }

    $markup = '';
    foreach ($lignes as [$nom, $valeur]) {
        $markup .= sprintf('<dt>%s</dt><dd>%s</dd>', escape($nom), escape($valeur));
    }

    return '<dl class="mesures">' . $markup . '</dl>';
}

/**
 * La consigne figée à côté du maître, et le rapport de production s'il existe.
 *
 * Les trois vont ensemble et nulle part ailleurs : l'image dit ce qui est sorti, la consigne ce qui était demandé, le rapport comment on l'a obtenu. Juger sur
 * l'une des trois seule est ce qui a fait chercher la mauvaise cause plus d'une fois. Absentes, elles se taisent : les premières images du projet sont
 * antérieures à la règle qui fige une consigne.
 */
function consigne(string $root, array $representation): string
{
    $master = $representation['maitre'] ?? null;
    if (!$master) {
        return '';
    }
    $frozen = $root . '/assets/' . preg_replace('/\.png$/', '.txt', $master);
    $name = pathinfo($master, PATHINFO_FILENAME);
    $report = $root . '/var/generations/sprites/' . $name . '-rapport.md';
    $blocks = '';
    // UN TEXTE SE LIT EN GRAND ET SE COPIE : replié dans une carte de deux cent soixante pixels, il ne sert à rien. Le résumé ouvre la FSP du texte, où il tient
    // toute la page et se sélectionne d'un bouton.
    if (is_file($frozen)) {
        $blocks .= '<button type="button" class="voir-texte" data-titre="La consigne envoyée">La consigne envoyée</button>'
            . '<script type="text/plain" class="texte-source">' . str_replace('</script', '<\/script', file_get_contents($frozen)) . '</script>';
    }
    if (is_file($report)) {
        $blocks .= '<button type="button" class="voir-texte" data-titre="Le rapport de génération">Le rapport de génération</button>'
            . '<script type="text/plain" class="texte-source">' . str_replace('</script', '<\/script', file_get_contents($report)) . '</script>';
    }

    return $blocks;
}

/** La FSP d'un sujet : ses variants, la version courante de chacun en grand, les antérieures, les mesures, la consigne, le verdict et les actions. */
function popin(Inventaire $inventaire, Vignette $vignettes, string $root, string $code, array $sujet): string
{
    $spread = $inventaire->spread($sujet);
    $blocks = '';
    foreach ($sujet['variants'] as $variant) {
        $ref = $variant['ref'];
        $current = $inventaire->currentRepresentation($variant);
        $picture = '<p class="a-produire">À produire</p>';
        if ($current) {
            $shot = image($vignettes, $current, COMPARE_PIXELS_PER_TILE * $spread['columns']);
            $picture = $shot ? sprintf('<img src="%s" width="%d" height="%d" alt="">', $shot[0], $shot[1], $shot[2])
                : '<p class="a-produire">Image illisible</p>';
        }
        $verdict = $current['verdict'] ?? null;
        $comment = $current['commentaire_operateur'] ?? '';
        $previous = $inventaire->previousRepresentations($variant);
        $identifier = $code . ' ' . $ref;
        $anciennes = '';
        foreach ($previous as $old) {
            // Chaque ancienne version est cliquable et s'ouvre en grand : une vignette de la moitié d'une case ne sert qu'à savoir qu'elle existe, pas à la juger.
            $shot = image($vignettes, $old, COMPARE_PIXELS_PER_TILE * $spread['columns']);
            if ($shot) {
                $anciennes .= sprintf('<figure><button type="button" class="voir-image" data-src="%s" data-titre="%s"><img src="%s" width="%d" height="%d" alt=""></button>'
                    . '<figcaption>%s</figcaption></figure>',
                    $shot[0], escape(basename($old['path'])), $shot[0], (int) ($shot[1] / 2), (int) ($shot[2] / 2), escape(basename($old['path'])));
            }
        }
        $blocks .= sprintf(
            '          <article class="variant" data-etat="%s">%s'
            . '<p class="variant-ref">%s</p><div class="variant-image">%s</div>%s%s%s%s'
            . '<div class="actes" data-id="%s">%s</div>'
            . '<div class="mot-zone"><button type="button" class="effacer-mot" data-id="%s" title="Effacer" aria-label="Effacer le commentaire">✕</button>'
            . '<textarea class="mot" data-id="%s" rows="2" placeholder="Ce qui devrait changer.">%s</textarea></div></article>' . "\n",
            escape(etatDuVariant($inventaire, $variant)),
            // COMPARER N'APPARAÎT QUE S'IL Y A DE QUOI COMPARER : un sujet à variant unique n'offre pas une case qui ne peut rien faire.
            count($sujet['variants']) > 1
                ? sprintf('<label class="variant-choix"><input type="checkbox" class="comparer" data-ref="%s"> Comparer</label>', escape($ref))
                : '',
            escape($ref), $picture,
            $verdict ? sprintf('<p class="verdict verdict--%s">%s</p>', escape($verdict), escape(capitale(str_replace('-', ' ', $verdict)))) : '',
            $current ? mesures($current, $sujet) : '',
            $anciennes ? '<details class="pli"><summary>' . count($previous) . ' version' . (count($previous) > 1 ? 's' : '')
                . ' antérieure' . (count($previous) > 1 ? 's' : '') . '</summary><div class="anciennes">' . $anciennes . '</div></details>' : '',
            $current ? consigne($root, $current) : '',
            escape(cleDeRevue($identifier, $current)), actes(cleDeRevue($identifier, $current)),
            escape(cleDeRevue($identifier, $current)), escape(cleDeRevue($identifier, $current)), escape($comment)
        );
    }

    return sprintf(
        "      <div class=\"fsp\" id=\"fsp-%s\" hidden>\n        <div class=\"fsp-barre\"><p class=\"fsp-titre\">%s <span class=\"slug\">%s</span></p>"
        . "<button type=\"button\" class=\"fsp-fermer\" aria-label=\"Fermer\">✕</button></div>\n"
        . "        <div class=\"fsp-corps\">\n          <div class=\"variants\">\n%s          </div>\n        </div>\n      </div>\n",
        escape($code), escape(capitale($inventaire->label($code))), escape($code), $blocks
    );
}

/** Les trois actions, TOUJOURS offertes quel que soit l'état courant : l'opérateur change d'avis quand il veut, et un bouton qui disparaît selon l'état oblige à deviner qu'il existe. */
/**
 * UNE REVUE PORTE SUR UNE IMAGE, PAS SUR UN VARIANT : la clé de rangement est le chemin de la version affichée. Une image regénérée est une image neuve, et le
 * verdict de la précédente ne la juge pas — il restait pourtant collé au variant, si bien qu'un bosquet refait revenait « à reprendre » avec le commentaire de son
 * ancêtre (opérateur, 2026-08-06). Le libellé, lui, reste celui du variant : c'est ce qui se lit dans le relevé.
 */
function cleDeRevue(string $identifier, ?array $current): string
{
    return $current['path'] ?? $identifier;
}

function actes(string $identifier): string
{
    // DES BOUTONS, PAS DES CASES À COCHER GRISES. Une action se clique et s'allume ; une case à cocher nue au milieu d'une carte se lit comme un formulaire
    // administratif, et l'opérateur l'a dit dès qu'elle est apparue. La case reste dessous — c'est elle qui porte l'état — mais elle est masquée et c'est le
    // libellé qui devient le bouton.
    $markup = '';
    foreach (['valider' => 'Valider', 'reprendre' => 'À reprendre', 'ecarter' => 'Écarter'] as $key => $label) {
        $markup .= sprintf('<label class="acte acte--%s"><input type="checkbox" data-id="%s" data-acte="%s"><span>%s</span></label>',
            $key, escape($identifier), $key, escape($label));
    }

    return $markup;
}

// Le gabarit ne s'interpole PAS tout seul : ses marques sont remplacées juste après, d'un seul geste. Sinon PHP substituerait des variables qui n'existent pas encore
// et laisserait des trous silencieux à leur place — ce qui est arrivé, et la page est sortie sans un seul style.
$page = <<<'HTML'
<title>Suivi des sprites</title>

<style>
{$theme}
  body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 ui-sans-serif, system-ui, sans-serif; }
  .wrap { width: min(100%, 1600px); margin: 0 auto; padding: 24px 16px 96px; }
  h1 { margin: 0 0 4px; font-size: 1.6rem; }
  .lede { margin: 0 0 24px; color: var(--muted); max-width: 90ch; }
  .type { margin-top: 28px; }
  .type h2 { margin: 0 0 10px; font-size: 1.15rem; }
  .slug { font-family: ui-monospace, monospace; font-size: .8rem; color: var(--muted); font-weight: 400; }

  .grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); gap: 6px; }
  .tuile { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 2px; padding: 6px;
           background: var(--card); border: 1px solid var(--line); border-radius: 4px; color: inherit; font: inherit; text-align: center; cursor: pointer; }
  .tuile:hover { border-color: var(--accent); }
  .tuile-image { display: flex; align-items: flex-end; justify-content: center; min-height: 26px; margin-top: auto; }
  .tuile-image img { max-width: 100%; height: auto; }
  .tuile-nom { font-weight: 600; font-size: .9rem; }
  .tuile-compte, .tuile-vide { font-size: .74rem; color: var(--muted); }

  .fsp { position: fixed; inset: 0; z-index: 90; display: flex; flex-direction: column; background: var(--bg); overflow: auto; }
  .fsp[hidden] { display: none; }
  .fsp-barre { position: sticky; top: 0; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; background: var(--card); border-bottom: 1px solid var(--line); }
  .fsp-titre { margin: 0; font-size: 1.1rem; font-weight: 600; }
  .fsp-fermer { padding: 4px 12px; background: none; border: 1px solid var(--line); border-radius: 4px; color: inherit; cursor: pointer; }
  .fsp-corps { padding: 16px; }
  .variants { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; align-items: start; }
  .variants.comparaison { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
  .variants.comparaison .variant:not(.retenu) { display: none; }
  .variant { padding: 10px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; }
  .variant-ref { margin: 6px 0; font-family: ui-monospace, monospace; font-size: .76rem; color: var(--muted); word-break: break-all; }
  /* LE DAMIER DIT OÙ EST LA TRANSPARENCE, et c'est la première chose qu'on juge sur une sprite détourée : sans lui, un fond opaque sombre se confond avec le fond
     de la page et un halo ne se voit pas du tout. */
  .variant-image {
    display: flex; align-items: flex-end; justify-content: center; min-height: 48px; padding: 6px; border-radius: 3px;
    background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 16px 16px;
  }
  .anciennes figure img { background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 12px 12px; }
  .variant-image img { max-width: 100%; height: auto; }
  .verdict { margin: 6px 0 0; font-size: .82rem; }
  .verdict--a-reprendre { color: #d08a3a; }
  .verdict--validee { color: var(--accent); }
  .anterieures, .a-produire { margin: 4px 0 0; font-size: .78rem; color: var(--muted); }
  .actes { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
  .acte { position: relative; }
  .acte input { position: absolute; opacity: 0; width: 0; height: 0; }
  .acte span { display: inline-block; padding: 4px 10px; background: var(--bg); border: 1px solid var(--line); border-radius: 4px; font-size: .8rem; cursor: pointer; }
  .acte:hover span { border-color: var(--accent); }
  .acte input:focus-visible + span { outline: 2px solid var(--accent); outline-offset: 2px; }
  .acte--valider input:checked + span { background: #2f5c3a; border-color: #4e8a5e; color: #eaf6ec; }
  .acte--reprendre input:checked + span { background: #6b4a1c; border-color: #a4762c; color: #fbf1e0; }
  .acte--ecarter input:checked + span { background: #5c2f2f; border-color: #8a4e4e; color: #f6eaea; }
  /* LE CHAMP TIENT DANS SA CARTE : sans box-sizing, ses bordures et son remplissage s'ajoutent aux cent pour cent de largeur et il déborde de quelques pixels — ce
     qui se voit tout de suite sur une grille de cartes. */
  /* LA CROIX EST COLLÉE AU CHAMP, en haut à droite : c'est le geste courant pour vider une saisie, et un bouton posé à côté avec son mot écrit prenait la place
     d'un tiers du champ pour dire ce qu'une croix dit sans un mot. */
  .mot-zone { position: relative; margin-top: 8px; }
  .mot { display: block; width: 100%; box-sizing: border-box; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; color: inherit; font: inherit; font-size: .82rem; line-height: 1.4; padding: 6px; resize: vertical; }
  .effacer-mot { align-self: stretch; padding: 0 10px; background: none; border: 1px solid var(--line); border-radius: 3px; color: var(--muted); font: inherit; font-size: .8rem; cursor: pointer; }
  .effacer-mot:hover { border-color: var(--accent); color: var(--accent); }
  .variant { box-sizing: border-box; }
  .mesures { display: grid; grid-template-columns: auto 1fr; gap: 1px 8px; margin: 8px 0 0; font-size: .74rem; color: var(--muted); }
  .mesures dt { font-weight: 600; white-space: nowrap; }
  .mesures dd { margin: 0; }
  .voir-texte { display: block; width: 100%; margin-top: 6px; padding: 5px 8px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; color: inherit; font: inherit; font-size: .78rem; text-align: left; cursor: pointer; }
  .voir-texte:hover { border-color: var(--accent); color: var(--accent); }
  .fsp-outils { display: flex; gap: 8px; }
  .fsp-outils button { padding: 4px 12px; background: none; border: 1px solid var(--line); border-radius: 4px; color: inherit; cursor: pointer; }
  #fsp-texte-corps { white-space: pre-wrap; font-size: .82rem; line-height: 1.5; }
  .fsp-corps--image { display: flex; align-items: center; justify-content: center; }
  #fsp-image-corps { max-width: 100%; max-height: 80vh; background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 24px 24px; }
  .anciennes .voir-image { padding: 0; background: none; border: 0; cursor: pointer; }
  .pli { margin-top: 6px; font-size: .8rem; color: var(--muted); }
  .pli summary { cursor: pointer; }
  .pli pre { max-height: 40vh; overflow: auto; white-space: pre-wrap; font-size: .74rem; }
  .anciennes { display: flex; flex-wrap: wrap; gap: 8px; }
  .anciennes figure { margin: 0; text-align: center; }
  .anciennes figcaption { font-size: .68rem; word-break: break-all; }
  .filtres { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }
  .filtre { padding: 5px 12px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; color: inherit; font: inherit; cursor: pointer; }
  .filtre[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); font-weight: 600; }
  .filtre span { color: var(--muted); }
  .orphelines { margin: 0; padding-left: 1.2rem; color: var(--muted); font-family: ui-monospace, monospace; font-size: .78rem; }
  .tuile[hidden] { display: none; }
  .type[hidden] { display: none; }
{$releveStyles}
</style>

<div class="wrap">
  <h1>Suivi des sprites</h1>
  <div class="fsp" id="fsp-image" hidden>
    <div class="fsp-barre"><p class="fsp-titre" id="fsp-image-titre"></p>
      <button type="button" class="fsp-fermer" aria-label="Fermer">✕</button></div>
    <div class="fsp-corps fsp-corps--image"><img id="fsp-image-corps" src="" alt=""></div>
  </div>

  <div class="fsp" id="fsp-texte" hidden>
    <div class="fsp-barre"><p class="fsp-titre" id="fsp-texte-titre"></p>
      <span class="fsp-outils"><button type="button" id="fsp-texte-copier">Copier</button>
      <button type="button" class="fsp-fermer" aria-label="Fermer">✕</button></span></div>
    <div class="fsp-corps"><pre id="fsp-texte-corps"></pre></div>
  </div>

  <p class="lede">Une vignette par sujet. Un clic ouvre le sujet en plein écran, avec ses variants, leurs versions, leurs mesures, la consigne qui les a produits et les actions — toutes
  offertes, toujours. Cochez « Comparer » sur plusieurs variants pour ne garder qu'eux, côte à côte, à quarante-huit pixels par case.</p>

  <div class="filtres">{$filtres}</div>

{$sections}
{$horsModele}
{$releveMarkup}
</div>

{$popins}

<script>
(function () {
  var MEMOIRE = 'gatebeast-suivi-sprites';
  var etat = {};
  try { etat = JSON.parse(localStorage.getItem(MEMOIRE)) || {}; } catch (error) { etat = {}; }

  function retenir() {
    try { localStorage.setItem(MEMOIRE, JSON.stringify(etat)); } catch (error) { /* un cadre peut refuser le stockage : la page marche quand même, pour la visite en cours */ }
  }

  Array.prototype.forEach.call(document.querySelectorAll('.actes input'), function (box) {
    var id = box.getAttribute('data-id');
    var acte = box.getAttribute('data-acte');
    box.checked = Boolean(etat[id] && etat[id][acte]);
    box.addEventListener('change', function () {
      etat[id] = etat[id] || {};
      etat[id][acte] = box.checked;
      retenir();
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll('.mot'), function (field) {
    var id = field.getAttribute('data-id');
    if (etat[id] && etat[id].mot) { field.value = etat[id].mot; }
    field.addEventListener('input', function () {
      etat[id] = etat[id] || {};
      etat[id].mot = field.value;
      retenir();
    });
  });

  /* LA COMPARAISON : cocher plusieurs variants ne garde qu'eux à l'écran, côte à côte et plus grands. Décocher tout revient à la liste entière. */
  Array.prototype.forEach.call(document.querySelectorAll('.comparer'), function (box) {
    box.addEventListener('change', function () {
      var liste = box.closest('.variants');
      var retenus = liste.querySelectorAll('.comparer:checked');
      Array.prototype.forEach.call(liste.querySelectorAll('.variant'), function (variant) {
        variant.classList.toggle('retenu', variant.querySelector('.comparer').checked);
      });
      liste.classList.toggle('comparaison', retenus.length > 0);
    });
  });

  /* EFFACER UN COMMENTAIRE NE LE DÉTRUIT PAS : le texte effacé est gardé, et le bouton propose de le rétablir tant qu'on n'a pas écrit autre chose. L'opérateur a
     demandé une solution sans perte — effacer d'un clic ne doit pas détruire ce qu'on vient d'écrire. */
  Array.prototype.forEach.call(document.querySelectorAll('.effacer-mot'), function (button) {
    var field = button.parentNode.querySelector('.mot');
    var id = button.getAttribute('data-id');
    var garde = null;
    function rendre() {
      button.textContent = garde === null ? 'Effacer' : 'Rétablir';
    }
    button.addEventListener('click', function () {
      if (garde === null) {
        garde = field.value;
        field.value = '';
      } else {
        field.value = garde;
        garde = null;
      }
      etat[id] = etat[id] || {};
      etat[id].mot = field.value;
      retenir();
      rendre();
    });
    field.addEventListener('input', function () { garde = null; rendre(); });
    rendre();
  });

  /* LES FILTRES agissent sur la grille : ils cachent les vignettes qui ne sont pas dans l'état demandé, et une section entièrement vide se cache avec elles —
     une rubrique qui reste ouverte sur rien fait croire qu'il n'y a rien à voir alors qu'on a simplement filtré. */
  Array.prototype.forEach.call(document.querySelectorAll('.filtre'), function (button) {
    button.addEventListener('click', function () {
      var voulu = button.getAttribute('data-filtre');
      Array.prototype.forEach.call(document.querySelectorAll('.filtre'), function (other) {
        other.setAttribute('aria-pressed', other === button ? 'true' : 'false');
      });
      Array.prototype.forEach.call(document.querySelectorAll('.tuile'), function (tile) {
        tile.hidden = voulu !== 'tout' && tile.getAttribute('data-etat') !== voulu;
      });
      Array.prototype.forEach.call(document.querySelectorAll('.type'), function (section) {
        var tiles = section.querySelectorAll('.tuile');
        var visible = Array.prototype.filter.call(tiles, function (tile) { return !tile.hidden; });
        section.hidden = tiles.length > 0 && visible.length === 0;
      });
    });
  });

  /* UNE IMAGE S'OUVRE EN GRAND, elle aussi : une vignette de la moitié d'une case dit qu'une version existe, elle ne permet pas de la juger. */
  var imagePopin = document.getElementById('fsp-image');
  var imageCorps = document.getElementById('fsp-image-corps');
  var imageTitre = document.getElementById('fsp-image-titre');
  Array.prototype.forEach.call(document.querySelectorAll('.voir-image'), function (button) {
    button.addEventListener('click', function () {
      imageCorps.src = button.getAttribute('data-src');
      imageTitre.textContent = button.getAttribute('data-titre');
      fermer();
      imagePopin.hidden = false;
      document.body.style.overflow = 'hidden';
      ouverte = imagePopin;
    });
  });

  /* UN TEXTE S'OUVRE EN GRAND, dans sa propre popin plein écran, et se copie d'un bouton. Replié dans une carte, il ne servait à personne. */
  var texteCorps = document.getElementById('fsp-texte-corps');
  var texteTitre = document.getElementById('fsp-texte-titre');
  var textePopin = document.getElementById('fsp-texte');
  Array.prototype.forEach.call(document.querySelectorAll('.voir-texte'), function (button) {
    button.addEventListener('click', function () {
      var porteur = button.nextElementSibling;
      texteTitre.textContent = button.getAttribute('data-titre');
      texteCorps.textContent = porteur ? porteur.textContent : '';
      fermer();
      textePopin.hidden = false;
      textePopin.scrollTop = 0;
      document.body.style.overflow = 'hidden';
      ouverte = textePopin;
    });
  });
  document.getElementById('fsp-texte-copier').addEventListener('click', function () {
    var holder = document.createElement('textarea');
    holder.value = texteCorps.textContent;
    holder.setAttribute('readonly', 'readonly');
    holder.style.position = 'fixed';
    holder.style.opacity = '0';
    document.body.appendChild(holder);
    holder.select();
    var done = false;
    try { done = document.execCommand('copy'); } catch (error) { done = false; }
    document.body.removeChild(holder);
    this.textContent = done ? 'Copié' : 'Sélectionne et copie à la main';
    var button = this;
    window.setTimeout(function () { button.textContent = 'Copier'; }, 2000);
  });

  var ouverte = null;
  function fermer() {
    if (!ouverte) { return; }
    ouverte.hidden = true;
    document.body.style.overflow = '';
    ouverte = null;
  }
  Array.prototype.forEach.call(document.querySelectorAll('.tuile'), function (tile) {
    tile.addEventListener('click', function () {
      var popin = document.getElementById('fsp-' + tile.getAttribute('data-sujet'));
      if (!popin) { return; }
      fermer();
      popin.hidden = false;
      popin.scrollTop = 0;
      document.body.style.overflow = 'hidden';
      ouverte = popin;
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('.fsp-fermer'), function (button) { button.addEventListener('click', fermer); });
  document.addEventListener('keydown', function (event) { if (event.key === 'Escape') { fermer(); } });

  /* CE QUE LA PAGE MET DANS LE RELEVÉ ; le module dit comment il se copie. */
  window.construireReleve = function () {
    var lignes = ['SUIVI DES SPRITES — RELEVÉ OPÉRATEUR', new Date().toISOString().slice(0, 10), ''];
    var actes = {valider: 'VALIDÉES', reprendre: 'À REPRENDRE', ecarter: 'ÉCARTÉES'};
    Object.keys(actes).forEach(function (acte) {
      var pris = Object.keys(etat).filter(function (id) { return etat[id] && etat[id][acte]; });
      if (!pris.length) { return; }
      lignes.push(actes[acte] + ' (' + pris.length + ')');
      pris.forEach(function (id) { lignes.push('  - ' + id); });
      lignes.push('');
    });
    var mots = Object.keys(etat).filter(function (id) { return etat[id] && etat[id].mot; });
    if (mots.length) {
      lignes.push('COMMENTAIRES (' + mots.length + ')');
      mots.forEach(function (id) { lignes.push('  - ' + id); lignes.push('      ' + etat[id].mot); });
    }
    return lignes.join('\n');
  };
})();
{$releveScript}
</script>
HTML;

// LES ORPHELINS : toute image livrée sous assets/cutout/ que l'inventaire ne réclame pas. Une image qui existe sans être inscrite n'existe pour personne — elle
// n'apparaît nulle part, personne ne peut la juger, et elle se refait. La page les montre plutôt que de laisser croire que tout est rangé.
$reclamees = [];
foreach ($inventaire->sujets() as $sujet) {
    foreach ($sujet['variants'] as $variant) {
        foreach ($variant['representations'] ?? [] as $representation) {
            $reclamees[$representation['path']] = true;
        }
    }
}
$orphelines = [];
$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/assets/cutout'));
foreach ($iterator as $file) {
    if ($file->isFile() && strtolower($file->getExtension()) === 'png') {
        $relative = 'cutout/' . substr($file->getPathname(), strlen($root . '/assets/cutout/'));
        if (!isset($reclamees[$relative])) {
            $orphelines[] = $relative;
        }
    }
}
sort($orphelines);
$horsModele = $orphelines
    ? '  <section class="type"><h2>Hors modèle <span class="slug">' . count($orphelines) . ' image(s) livrée(s) qu\'aucun variant ne réclame</span></h2><ul class="orphelines"><li>'
      . implode('</li><li>', array_map('escape', $orphelines)) . '</li></ul></section>'
    : '  <section class="type"><h2>Hors modèle <span class="slug">rien</span></h2><p class="lede">Chaque image livrée est réclamée par un variant.</p></section>';

$filtres = '';
foreach (['tout' => 'Tout', 'a-reprendre' => 'À reprendre', 'a-produire' => 'À produire', 'produite' => 'Produites', 'validee' => 'Validées'] as $key => $label) {
    $filtres .= sprintf('<button type="button" class="filtre" data-filtre="%s" aria-pressed="%s">%s%s</button>',
        $key, $key === 'tout' ? 'true' : 'false', escape($label), $key === 'tout' ? '' : ' <span>' . ($compte[$key] ?? 0) . '</span>');
}

$page = strtr($page, [
    '{$theme}' => Theme::css('encre'),
    '{$filtres}' => $filtres,
    '{$horsModele}' => $horsModele,
    '{$releveStyles}' => Releve::styles(),
    '{$releveMarkup}' => Releve::markup('Votre relevé, à me coller en conversation'),
    '{$releveScript}' => Releve::script(),
    '{$sections}' => $sections,
    '{$popins}' => $popins,
]);

file_put_contents($outputPath, $page);
printf("%s — %d sujets, %.1f ko%s\n", $outputPath, count($inventaire->sujets()), strlen($page) / 1024,
    $missing ? ', ' . count($missing) . ' image(s) illisible(s)' : '');
if ($inventaire->sansLibelle) {
    fwrite(STDERR, 'SANS LIBELLÉ : ' . implode(', ', $inventaire->sansLibelle) . "\n");
}

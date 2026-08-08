<?php
/**
 * Usage: php review-server/suivi-sprites/build.php [sortie.html]
 *
 * Builds the sprite tracking page in PHP: a grid of subjects, and one full-screen popin per subject holding its variants, their versions and the actions.
 *
 * Intention: this is the migration decided on 2026-08-06, and since 2026-08-07 it is the only builder of this page — the Python one it was written beside has been removed on the operator's order,
 * review-server holding no Python at all. It is also the first page assembled from the shared modules of review-server/lib/ rather than from its own copy of everything: the inventory reader, the
 * thumbnail factory and the relevé all live there and serve the other pages too.
 *
 * What the Python builder did and this one does NOT: the judgements — dead matter anyway, the agent that scored sprites was unplugged on 2026-08-04 — and the listing of stray files found on disk.
 * Everything else it announced as missing has since been caught up: the filters by state, the measures, the frozen consigne and the production report are all here.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Inventory.php';
require_once $root . '/review-server/lib/Thumbnail.php';
bootBuild();

const SCREEN_PIXELS_PER_TILE = 24;   // ce qu'une case mesure à l'écran — la valeur du projet, tenue par scripts/tile_scale.py
const COMPARE_PIXELS_PER_TILE = 48;  // ce qu'une case mesure dans la FSP, où l'on juge et compare (opérateur, 2026-08-06)
// ORPHAN_WIDTH is a width in pixels, not a count of tiles: an unclaimed image has no variant, so nothing declares how many tiles it covers. Wide enough to recognize the subject at a glance.
const ORPHAN_WIDTH = 160;
// Le raccourci d'une longueur au sol qui s'enfonce, sous la caméra à 60 degrés — le sinus de l'angle. Écrit ici en attendant que la page le demande au service qui
// détient l'échelle, qui est en Python : c'est la seule valeur du modèle que cette page recopie, et elle est à supprimer dès que les deux côtés se parlent.
const GROUND_DEPTH_FACTOR = 0.8660;

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$inventory = new Inventory($root);
$thumbnails = new Thumbnail($root);
$theme = Theme::get();
$favicon = Favicon::get();
$releve = Releve::get();
$reload = Reload::get();

// Les images manquantes plus bas ne sont PAS des fautes : elles se rapportent et se montrent comme des trous. Un trou qui se voit est ce qui dit à l'opérateur ce qui reste dû.

const TYPE_LABELS = [
    'sol' => 'Sol', 'chemin' => 'Chemin', 'cours-d-eau' => "Cours d'eau", 'cloture' => 'Clôture et mur',
    'arbre' => 'Arbre', 'bosquet-arbres' => "Bosquet d'arbres", 'herbe' => 'Herbe',
    'batiment' => 'Bâtiment', 'humain' => 'Humain', 'creature' => 'Créature', 'pont' => 'Pont',
];

// THE STATES A SUBJECT CAN BE IN, prefixed and spelled in English like every value the code compares. What a human reads is the label, and only the label.
const STATE_TO_REWORK = 'to-rework';
const STATE_DISMISSED = 'dismissed';
const STATE_TO_PRODUCE = 'to-produce';
const STATE_TO_JUDGE = 'to-judge';
const STATE_VALIDATED = 'validated';
const STATE_ALL = 'all';

// THE STATE OF A SUBJECT, SAID IN ONE WORD, and the same word everywhere: on the tile, in the filter that keeps it, in the count that announces it. Two wordings
// for one state would make the operator do the translation the page should have done. In French, because a label is read by a human — the keys stay English.
const STATE_LABELS = [
    STATE_TO_REWORK => 'À reprendre',
    STATE_DISMISSED => 'Écarté',
    STATE_TO_PRODUCE => 'À produire',
    STATE_TO_JUDGE => 'À juger',
    STATE_VALIDATED => 'Validé',
];

// THE VERDICTS THE REFERENTIEL STORES, in French, and the state each one means. This table is the only bridge between the stored wording and the page's vocabulary.
const VERDICT_STATES = [
    'validee' => STATE_VALIDATED,
    'a-reprendre' => STATE_TO_REWORK,
    'ecartee' => STATE_DISMISSED,
];

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES);
}

/** La première lettre en majuscule, et elle seule — la règle d'affichage du projet. */
function capitalize(string $text): string
{
    return mb_strtoupper(mb_substr($text, 0, 1)) . mb_substr($text, 1);
}

/** L'image d'une représentation, réduite à la taille demandée, ou null si le fichier manque — un trou se montre, il ne se cache pas. */
function image(Thumbnail $thumbnails, array $representation, int $width): ?array
{
    try {
        return $thumbnails->shrink($representation['path'], $width);
    } catch (RuntimeException $fault) {
        fwrite(STDERR, $fault->getMessage() . "\n");

        return null;
    }
}

$sections = '';
$popins = '';
$missing = [];
$compte = [];

foreach ($inventory->types() as $typeName => $type) {
    $codes = $inventory->sujetsOfType($typeName);
    if (!$codes) {
        continue;
    }
    $tiles = '';
    foreach ($codes as $code) {
        $sujet = $inventory->sujet($code);
        $spread = $inventory->spread($sujet);
        $main = $inventory->mainVariant($sujet);
        $current = $main ? $inventory->currentRepresentation($main) : null;
        $produced = 0;
        foreach ($sujet['variants'] as $variant) {
            $produced += $variant['representations'] ? 1 : 0;
        }
        $picture = '<span class="tile-empty">à produire</span>';
        if ($current) {
            $shot = image($thumbnails, $current, SCREEN_PIXELS_PER_TILE * $spread['columns']);
            if ($shot) {
                $picture = sprintf('<img src="%s" width="%d" height="%d" alt="">', $shot[0], $shot[1], $shot[2]);
            } else {
                $missing[] = $current['path'];
            }
        }
        $etat = subjectState($inventory, $sujet);
        $compte[$etat] = ($compte[$etat] ?? 0) + 1;
        // THE STATE SHOWS ON THE TILE, AND IT IS THE FIRST THING ONE LOOKS FOR THERE (operator, 2026-08-08): does this subject need judging, is it fully validated,
        // fully produced, or is something left to rework? The tile carried its state as an attribute, so the filters knew it and the eye did not.
        $tiles .= sprintf(
            '        <button type="button" class="tile" data-sujet="%s" data-etat="%s"><span class="tile-image">%s</span>'
            . '<span class="tile-name">%s</span><span class="tile-state">%s</span><span class="tile-count">%d/%d variant%s</span></button>' . "\n",
            escape($code), escape($etat), $picture, escape(capitalize($inventory->label($code))), escape(STATE_LABELS[$etat]),
            $produced, count($sujet['variants']), count($sujet['variants']) > 1 ? 's' : ''
        );
        $popins .= popin($inventory, $thumbnails, $root, $code, $sujet);
    }
    $sections .= sprintf(
        "    <section class=\"type\">\n      <h2>%s <span class=\"slug\">%s</span></h2>\n      <div class=\"grid\">\n%s      </div>\n    </section>\n",
        escape(TYPE_LABELS[$typeName] ?? $typeName), escape($typeName), $tiles
    );
}

/** L'état d'un variant, en un mot : ce sur quoi les filtres de la grille agissent. */
/**
 * THE STATE OF A SUBJECT, READ OFF ALL ITS VARIANTS AT ONCE — one word for the whole subject, which is what the grid shows and what the filters act on.
 *
 * THE ORDER IS WHAT MAKES IT USEFUL, and it runs from what is owed to what is finished. The list the operator gave is deliberately not exhaustive (2026-08-08:
 * "it is up to you to think about all the needs"), so it is derived from what a variant can actually be rather than from a list to copy:
 *
 *   1. TO REWORK wins over everything. One image judged wrong is work due, whatever the others say, and it is the state one hunts for.
 *   2. DISMISSED comes next. It is not the same as "to rework": nothing is to be corrected, a new image is owed — and unlike a variant never drawn, a dismissed one
 *      still shows an image on the page, so without its own word it would read as produced.
 *   3. TO PRODUCE, for a variant that carries no image at all.
 *   4. TO JUDGE, for everything produced that is not fully judged. This is the state the operator asked for by name: it says the review is what is missing.
 *   5. VALIDATED, and it takes EVERY variant — a subject where two views out of three are judged is not a judged subject.
 *
 * A subject declared without a single variant reads as "to produce": it owes every image it has, which is all of them.
 */
function subjectState(Inventory $inventory, array $sujet): string
{
    $states = [];
    foreach ($sujet['variants'] ?? [] as $variant) {
        $states[] = variantState($inventory, $variant);
    }
    if (!$states) {
        return STATE_TO_PRODUCE;
    }
    foreach ([STATE_TO_REWORK, STATE_DISMISSED, STATE_TO_PRODUCE] as $owed) {
        if (in_array($owed, $states, true)) {
            return $owed;
        }
    }

    return array_unique($states) === [STATE_VALIDATED] ? STATE_VALIDATED : STATE_TO_JUDGE;
}

/**
 * The state of one variant, in the page's own vocabulary.
 *
 * THE REFERENTIEL STILL SPELLS ITS VERDICTS IN FRENCH — "validee", "a-reprendre", "ecartee" — and this is the one place that translates them. Renaming the stored
 * values is a data migration of its own, with its own point in the pile; until then, the French stays where it is written and never leaks into the code around it.
 */
function variantState(Inventory $inventory, array $variant): string
{
    $current = $inventory->currentRepresentation($variant);
    if (!$current) {
        return STATE_TO_PRODUCE;
    }

    return VERDICT_STATES[$current['verdict'] ?? ''] ?? STATE_TO_JUDGE;
}

/** Les mesures d'une image, dites en clair : ce que l'export a constaté sur le fichier livré. Rien n'est recalculé ici — la page montre ce qui est écrit. */
/**
 * TOUTES les mensurations d'une image, et pas une sélection : ce que le sujet déclare — emprise, couvert, hauteur — et ce que l'export a mesuré sur le fichier.
 * Choisir trois chiffres à montrer, c'est décider à la place de l'opérateur lequel compte, et c'est justement ce qu'il regarde quand une image lui paraît fausse.
 */
function measurements(array $representation, array $sujet): string
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

    return '<dl class="measures">' . $markup . '</dl>';
}

/**
 * La consigne figée à côté du maître, et le rapport de production s'il existe.
 *
 * Les trois vont ensemble et nulle part ailleurs : l'image dit ce qui est sorti, la consigne ce qui était demandé, le rapport comment on l'a obtenu. Juger sur
 * l'une des trois seule est ce qui a fait chercher la mauvaise cause plus d'une fois. Absentes, elles se taisent : les premières images du projet sont
 * antérieures à la règle qui fige une consigne.
 */
function frozenPrompt(string $root, array $representation): string
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
        $blocks .= '<button type="button" class="open-text" data-titre="La consigne envoyée">La consigne envoyée</button>'
            . '<script type="text/plain" class="text-source">' . str_replace('</script', '<\/script', file_get_contents($frozen)) . '</script>';
    }
    if (is_file($report)) {
        $blocks .= '<button type="button" class="open-text" data-titre="Le rapport de génération">Le rapport de génération</button>'
            . '<script type="text/plain" class="text-source">' . str_replace('</script', '<\/script', file_get_contents($report)) . '</script>';
    }

    return $blocks;
}

/**
 * La grille posée sur une sprite : son emprise au sol, son couvert s'il déborde, et les deux axes.
 *
 * TOUT EST DIT EN CASES ET RENDU EN POURCENTAGE de la vignette, jamais en pixels : la vignette change de taille selon l'emprise du sujet et selon le zoom, alors
 * qu'une case reste une case. Écrire des pixels ici les ferait diverger de l'image dès qu'une taille change.
 *
 * L'IMAGE EST POSÉE SUR LA LARGEUR DU COUVERT, pas de l'emprise — c'est ce que fait la fabrique de vignettes juste au-dessus. L'emprise au sol se dessine donc
 * comme une part de cette largeur, centrée, et non comme la vignette entière : c'est exactement ce qu'on veut voir d'un chêne dont la couronne déborde de son pied.
 */
/**
 * The delivered file on show and when it was written, under the variant's label.
 *
 * ONE LOOKS AT AN IMAGE WITHOUT KNOWING WHICH ONE — the card carried the variant's ref, which never changes, and nothing about the version actually displayed nor
 * its age. After an evening of reworks, whether the sprite under one's eyes came out of the last generation or last week is the first thing one wants to read.
 *
 * THE DATE COMES FROM THE DELIVERED FILE ITSELF, never from a value copied into the referentiel: a hand-written date falls out of step with the file at the first
 * forgotten export, and it then lies with authority.
 *
 * Written the French way, day first (operator, 2026-08-07): this page is read by a human. The sortable international form stays where dates are data — file names,
 * tracking documents.
 */
function version(string $root, ?array $current): string
{
    if (!$current) {
        return '';
    }
    $file = $root . '/assets/' . $current['path'];
    $when = is_file($file) ? date('d/m/Y à H\hi', filemtime($file)) : 'date inconnue';

    return sprintf('<p class="variant-version"><span class="variant-file">%s</span><span class="variant-date">%s</span></p>',
        escape(basename($current['path'])), escape($when));
}

function grid(array $sujet, array $spread, int $width, int $height): string
{
    $footprint = $sujet['emprise'];
    $covers = ($spread['columns'] !== $footprint['columns']) || ($spread['rows'] !== $footprint['rows']);
    // La case, en pourcentage de la vignette : la largeur porte les colonnes du couvert, et la hauteur suit la même échelle puisque l'image n'est jamais déformée.
    $tile = 100 / $spread['columns'];
    // UNE CASE DE PROFONDEUR NE SE PROJETTE PAS COMME UNE CASE DE LARGEUR, et l'oublier faisait descendre le cadre d'emprise bien plus bas que le sol du sujet —
    // deux cases de vide devant le bâtiment, relevées par l'opérateur. Sous la caméra du monde, une longueur au sol qui s'enfonce est vue raccourcie ; le service
    // qui détient l'échelle porte ce facteur, et c'est à lui qu'on le demande plutôt que de le retaper ici.
    $tileY = $tile * $width / max($height, 1) * GROUND_DEPTH_FACTOR;
    $footWidth = 100 * $footprint['columns'] / $spread['columns'];
    $footHeight = $tileY * $footprint['rows'];

    return sprintf(
        '<span class="footprint" style="--case: %.4f%%; --case-y: %.4f%%">'
        . '<span class="footprint-ground" style="width: %.4f%%; height: %.4f%%" title="Emprise au sol : %d × %d cases"></span>'
        . '%s'
        . '<span class="footprint-axis footprint-axis--x"></span><span class="footprint-axis footprint-axis--y"></span>'
        . '</span>',
        $tile, $tileY, $footWidth, $footHeight,
        (int) $footprint['columns'], (int) $footprint['rows'],
        $covers ? sprintf('<span class="footprint-cover" title="Couvert : %d × %d cases"></span>',
            (int) $spread['columns'], (int) $spread['rows']) : ''
    );
}

/**
 * ONE VERSION OF A VARIANT, RENDERED THE ONE WAY THERE IS: its file name and date, its picture with the footprint grid, its verdict, its measurements, and the prompt it was drawn from.
 *
 * THE CURRENT VERSION AND THE EARLIER ONES GO THROUGH HERE ALIKE (operator, 2026-08-07: "same presentation, no specificity"). Earlier versions used to show a half-size thumbnail and a file name,
 * which is enough to know one exists and not enough to judge it — and judging one against the current is the only reason to open them. Two renderings of the same thing also drift: the footprint
 * grid, the date and the measurements were all added to the current one alone, and the gap widened at every addition. One function, called twice, cannot drift.
 */
function representation(Thumbnail $thumbnails, string $root, array $sujet, array $spread, array $representation): string
{
    // L'ÉCHELLE EST FIXE ET LA MÊME POUR TOUS LES SUJETS : quarante-huit pixels par case dans la fiche, la case restant une case d'un sujet à l'autre.
    // Un grand chêne occupe donc quatre fois la largeur d'une clôture, ce qui est la vérité du monde ; des vignettes toutes de même largeur ne
    // permettaient ni de comparer deux sujets, ni de voir qu'une sprite déborde — ce que l'emprise et le couvert servent justement à montrer.
    $shot = image($thumbnails, $representation, COMPARE_PIXELS_PER_TILE * $spread['columns']);
    // LA GRILLE SE POSE SUR L'IMAGE, À L'ÉCHELLE OÙ ELLE EST MONTRÉE (opérateur, 2026-08-07) : sans elle, une sprite se juge dans le vide — on ne voit ni ce
    // qu'elle occupe au sol, ni ce qu'elle surplombe, ni où sont ses axes. Les trois se lisent à des couleurs différentes, et les valeurs sont celles du
    // référentiel, jamais recalculées ici.
    // L'IMAGE ET SA GRILLE SONT ENFERMÉES ENSEMBLE : sans cette enveloppe qui épouse l'image, la grille se cale sur la carte entière et son cadre d'emprise
    // s'étire sur toute la largeur, en annonçant une sprite bien plus large qu'elle n'est.
    $picture = $shot
        ? sprintf('<span class="picture"><img src="%s" width="%d" height="%d" alt="">%s</span>', $shot[0], $shot[1], $shot[2], grid($sujet, $spread, $shot[1], $shot[2]))
        : '<p class="to-produce">Image illisible</p>';
    $state = VERDICT_STATES[$representation['verdict'] ?? ''] ?? null;

    return sprintf('%s<div class="variant-image">%s</div>%s%s%s',
        version($root, $representation),
        $picture,
        // THE VERDICT IS SHOWN THROUGH THE SAME VOCABULARY AS EVERYTHING ELSE: the stored French value is translated once, and the page speaks one language to itself.
        $state ? sprintf('<p class="verdict verdict--%s">%s</p>', escape($state), escape(STATE_LABELS[$state])) : '',
        measurements($representation, $sujet),
        // LES VERSIONS ANTÉRIEURES PASSENT SOUS LA CONSIGNE ET LE RAPPORT DE LA VERSION COURANTE (opérateur, 2026-08-07) : intercalées entre les mesures et
        // eux, elles séparaient une version de ses propres pièces justificatives et l'on ne savait plus à laquelle se rapportait quoi.
        frozenPrompt($root, $representation)
    );
}

/** La FSP d'un sujet : ses variants, la version courante de chacun en grand, les antérieures, les mesures, la consigne, le verdict et les actions. */
function popin(Inventory $inventory, Thumbnail $thumbnails, string $root, string $code, array $sujet): string
{
    $spread = $inventory->spread($sujet);
    $blocks = '';
    foreach ($sujet['variants'] as $variant) {
        $ref = $variant['ref'];
        $current = $inventory->currentRepresentation($variant);
        $courante = $current
            ? representation($thumbnails, $root, $sujet, $spread, $current)
            : '<div class="variant-image"><p class="to-produce">À produire</p></div>';
        $comment = $current['commentaire_operateur'] ?? '';
        $previous = $inventory->previousRepresentations($variant);
        $identifier = $code . ' ' . $ref;
        $anciennes = '';
        foreach ($previous as $old) {
            // MÊME PRÉSENTATION QUE LA COURANTE, AUCUNE SPÉCIFICITÉ (opérateur, 2026-08-07) : son image à la même échelle avec sa grille d'emprise, son nom de
            // fichier, sa date, son verdict, ses mesures et sa consigne. C'est en la mettant en regard de la courante qu'on décide si la reprise a servi.
            $anciennes .= sprintf('<article class="previous">%s</article>', representation($thumbnails, $root, $sujet, $spread, $old));
        }
        $key = reviewKey($identifier, $current);
        // LE BLOC DE JUGEMENT SE CONSTRUIT AVANT, ET C'EST UNE LEÇON PAYÉE : je l'avais rendu conditionnel À L'INTÉRIEUR du gabarit, en laissant des marques de
        // substitution dans la branche vide. Elles consommaient quand même leurs arguments et les recrachaient en clair — le balisage des actions se retrouvait
        // déversé au milieu de la page, qui s'est disloquée. Un gabarit ne porte pas de condition ; ce qui varie se calcule avant et n'y entre qu'une fois décidé.
        $review = '';
        if ($current) {
            $review = sprintf(
                '<div class="acts" data-id="%s">%s'
                . '<button type="button" class="open-comment" data-open="%s" aria-expanded="false" aria-label="Commentaire" title="Commentaire">+</button></div>'
                . '<div class="comment-zone" data-more="%s" hidden>'
                . '<textarea class="comment" data-id="%s" rows="2" placeholder="Ce qui devrait changer.">%s</textarea>'
                . '<button type="button" class="clear-comment" data-id="%s" title="Effacer le commentaire" aria-label="Effacer le commentaire" hidden>×</button></div>',
                escape($key), actions($key), escape($key), escape($key), escape($key), escape($comment), escape($key)
            );
        }
        // LA ZONE DE SAISIE EST REPLIÉE, ET C'EST LE BOUTON « ＋ » QUI L'OUVRE (opérateur, 2026-08-06 puis 2026-08-07). Dépliée d'office, elle prend autant de hauteur que
        // les trois actes réunis sur chaque carte, pour un champ qu'on ne remplit qu'une fois sur dix. Cocher « À reprendre » ou « Écarter » l'ouvre toute seule : un refus
        // demande son motif, un accord n'a rien à justifier.
        $blocks .= sprintf(
            '          <article class="variant" data-etat="%s">%s'
            // LE LIBELLÉ FRANÇAIS D'ABORD, LA RÉFÉRENCE TECHNIQUE ENSUITE ET EN PETIT : la carte disait « orientation-south_action-idle_shape-e_frame-01 » et rien d'autre, ce qui n'apprend
            // rien à qui regarde une image (opérateur, 2026-08-07). Le libellé vient du référentiel, jamais composé ici — une page qui compose du vocabulaire en invente.
            . '<p class="variant-name">%s%s</p>%s%s'
            // RIEN NE SE JUGE SUR UNE IMAGE QUI N'EXISTE PAS (opérateur, 2026-08-07) : un variant à produire n'offre ni verdict, ni commentaire, ni comparaison — valider une image absente ne
            // veut rien dire, et la case « Comparer » proposait de la mettre en regard d'une autre. La carte dit ce qui reste dû, et c'est tout ce qu'elle a à dire.
            . '%s</article>' . "\n",
            escape(variantState($inventory, $variant)),
            // COMPARER N'APPARAÎT QUE S'IL Y A DE QUOI COMPARER : un sujet à variant unique n'offre pas une case qui ne peut rien faire, et un variant qui n'a pas d'image non plus.
            count($sujet['variants']) > 1 && $current
                ? sprintf('<label class="variant-pick"><input type="checkbox" class="compare" data-ref="%s"> Comparer</label>', escape($ref))
                : '',
            // LE VARIANT PRINCIPAL SE VOIT (opérateur, 2026-08-07) : le constructeur d'origine distinguait la vue principale, la reprise l'avait perdue, et une planche de quinze formes où rien
            // ne dit laquelle fait référence oblige à ouvrir le référentiel pour le savoir. L'information y est déjà, chaque sujet portant un variant marqué principal.
            escape($variant['libelle'] ?? 'Vue principale'),
            ($variant['principale'] ?? false) ? '<span class="variant-main" title="Le variant de référence du sujet">principal</span>' : '',
            $courante,
            $anciennes ? '<details class="fold"><summary>' . count($previous) . ' version' . (count($previous) > 1 ? 's' : '')
                . ' antérieure' . (count($previous) > 1 ? 's' : '') . '</summary><div class="previous-list">' . $anciennes . '</div></details>' : '',
            $review
        );
    }

    return sprintf(
        "      <div class=\"fsp\" id=\"fsp-%s\" hidden>\n        <div class=\"fsp-bar\"><p class=\"fsp-title\">%s <span class=\"slug\">%s</span></p>"
        . "<button type=\"button\" class=\"fsp-close\" aria-label=\"Fermer\">✕</button></div>\n"
        . "        <div class=\"fsp-body\">\n          <div class=\"variants\">\n%s          </div>\n        </div>\n      </div>\n",
        escape($code), escape(capitalize($inventory->label($code))), escape($code), $blocks
    );
}

/** Les trois actions, TOUJOURS offertes quel que soit l'état courant : l'opérateur change d'avis quand il veut, et un bouton qui disparaît selon l'état oblige à deviner qu'il existe. */
/**
 * UNE REVUE PORTE SUR UNE IMAGE, PAS SUR UN VARIANT : la clé de rangement est le chemin de la version affichée. Une image regénérée est une image neuve, et le
 * verdict de la précédente ne la juge pas — il restait pourtant collé au variant, si bien qu'un bosquet refait revenait « à reprendre » avec le commentaire de son
 * ancêtre (opérateur, 2026-08-06). Le libellé, lui, reste celui du variant : c'est ce qui se lit dans le relevé.
 */
function reviewKey(string $identifier, ?array $current): string
{
    return $current['path'] ?? $identifier;
}

function actions(string $identifier): string
{
    // DES BOUTONS, PAS DES CASES À COCHER GRISES. Une action se clique et s'allume ; une case à cocher nue au milieu d'une carte se lit comme un formulaire
    // administratif, et l'opérateur l'a dit dès qu'elle est apparue. La case reste dessous — c'est elle qui porte l'état — mais elle est masquée et c'est le
    // libellé qui devient le bouton.
    $markup = '';
    foreach (['valider' => 'Valider', 'reprendre' => 'À reprendre', 'ecarter' => 'Écarter'] as $key => $label) {
        $markup .= sprintf('<label class="act act--%s"><input type="checkbox" data-id="%s" data-acte="%s"><span>%s</span></label>',
            $key, escape($identifier), $key, escape($label));
    }

    return $markup;
}

// Le gabarit ne s'interpole PAS tout seul : ses marques sont remplacées juste après, d'un seul geste. Sinon PHP substituerait des variables qui n'existent pas encore
// et laisserait des trous silencieux à leur place — ce qui est arrivé, et la page est sortie sans un seul style.
$page = <<<'HTML'
<title>Suivi des sprites</title>
{$favicon}

<style>
{$theme}
  /* L'ÉCHELLE TYPOGRAPHIQUE VIENT DU CONSTRUCTEUR D'ORIGINE, ET ELLE NE SE RÉINVENTE PAS (opérateur, redemandée trois fois). Chasse fixe en base, quinze pixels,
     interligne 1,55 : c'est une page d'atelier, où l'on lit des noms de fichiers, des mesures et des codes bien plus que des phrases. La reprise avait pris la
     police du système à seize pixels, ce qui aplatissait toute la hiérarchie — un titre de section ne se distinguait plus d'un nom de sujet. */
  body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace; -webkit-font-smoothing: antialiased; }
  /* LA PAGE GRANDIT AVEC L'ÉCRAN au lieu de tenir une largeur fixe, mais jamais bord à bord : un plafond garde la lecture confortable et les marges délibérées. */
  .wrap { width: min(100%, 1760px); margin: 0 auto; padding: 40px clamp(12px, 3vw, 48px) 132px; }
  h1 { margin: 0; font-size: clamp(29px, 5vw, 42px); line-height: 1.07; font-weight: 700; letter-spacing: -.025em; text-wrap: balance; max-width: 21ch; }
  /* LE TEXTE COURANT GARDE SA PROPRE MESURE, plus étroite que la page : rien ne se lit sur toute la largeur d'un grand écran. Et il passe en police à chasse
     variable — c'est de la phrase, pas de la donnée. */
  .lede { margin: 14px 0 0; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 16px; line-height: 1.6; color: var(--muted); max-width: 62ch; }
  /* LES SECTIONS RESPIRENT : cinquante-quatre pixels au-dessus de chacune. Serrées à vingt-huit, la planche se lisait comme une seule liste continue. */
  .type { margin-top: 54px; }
  .type h2 { margin: 0 0 14px; font-size: 21px; font-weight: 700; letter-spacing: -.01em; }
  .slug { font-family: ui-monospace, monospace; font-size: .8rem; color: var(--muted); font-weight: 400; }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); gap: 6px; }
  .tile { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 2px; padding: 8px 6px;
           background: var(--card); border: 1px solid var(--line); border-radius: 3px; color: inherit; font: inherit; text-align: center; cursor: pointer; }
  .tile:hover { border-color: var(--accent); }
  .tile-image { display: flex; align-items: flex-end; justify-content: center; min-height: 26px; margin-top: auto; }
  .tile-image img { max-width: 100%; height: auto; }
  .tile-name { font-weight: 700; font-size: 15px; letter-spacing: -.012em; }
  /* LE COMPTE EST UNE ÉTIQUETTE, PAS UNE PHRASE : petites capitales espacées, comme toutes les étiquettes de la page d'origine. */
  .tile-count, .tile-empty { font-size: 11.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }

  .fsp { position: fixed; inset: 0; z-index: 90; display: flex; flex-direction: column; background: var(--bg); overflow: auto; }
  .fsp[hidden] { display: none; }
  .fsp-bar { position: sticky; top: 0; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px;
               background: var(--card); border-bottom: 1px solid var(--line); }
  .fsp-title { margin: 0; font-size: 1.1rem; font-weight: 600; }
  /* UNE CROIX SANS HABILLAGE, MAIS UNE CIBLE DE CLIC LARGE (opérateur, 2026-08-07) : le bouton faisait vingt pixels et il fallait viser pour fermer un panneau
     plein écran. Le signe reste petit et discret, c'est la SURFACE qui grandit — quarante-quatre pixels de côté, la taille d'une cible qu'on atteint sans regarder.
     Ni bordure, ni fond, ni survol, ni cerne de focus : rien à styler, tout à cliquer. */
  .fsp-close {
    width: 44px; height: 44px; padding: 0; margin: -8px -8px -8px 0;
    display: flex; align-items: center; justify-content: center;
    background: none; border: 0; border-radius: 0; color: inherit; font-size: 20px; line-height: 1; cursor: pointer;
  }
  .fsp-body { padding: 16px; }
  .variants { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; align-items: start; }
  .variants.comparison { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
  .variants.comparison .variant:not(.picked) { display: none; }
  .variant { padding: 10px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; }
  .variant-name { margin: 6px 0 2px; font-size: 19px; font-weight: 700; letter-spacing: -.012em; }
  /* LE VARIANT PRINCIPAL PORTE SA MARQUE À CÔTÉ DE SON NOM, pas ailleurs : c'est en lisant le nom qu'on cherche à savoir lequel fait référence, et une pastille
     posée plus bas se cherche. Discrète et non grasse — elle informe, elle ne réclame pas l'œil comme un verdict. */
  .variant-main {
    margin-left: 6px; padding: 1px 6px; border: 1px solid var(--accent); border-radius: 10px;
    font-size: .62rem; font-weight: 400; letter-spacing: .04em; text-transform: uppercase; color: var(--accent); vertical-align: middle;
  }
  .variant-ref { margin: 0 0 6px; font-family: ui-monospace, monospace; font-size: .7rem; color: var(--faint, var(--muted)); word-break: break-all; }
  /* LE FICHIER AFFICHÉ ET SA DATE, sous le libellé : c'est ce qu'on cherche en premier après une séance de reprises, pour savoir si l'on regarde la dernière. */
  .variant-version { display: flex; flex-wrap: wrap; gap: 4px 10px; margin: 0 0 6px; font-family: ui-monospace, monospace; font-size: .7rem; }
  .variant-file { color: var(--ink); word-break: break-all; }
  .variant-date { color: var(--accent); }
  /* LE DAMIER DIT OÙ EST LA TRANSPARENCE, et c'est la première chose qu'on juge sur une sprite détourée : sans lui, un fond opaque sombre se confond avec le fond
     de la page et un halo ne se voit pas du tout. */
  .variant-image {
    display: flex; align-items: flex-end; justify-content: center; min-height: 48px; padding: 6px; border-radius: 3px;
    background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 16px 16px;
  }
  /* L'ENVELOPPE ÉPOUSE L'IMAGE, et c'est elle qui sert de repère à la grille : posée sur la carte, la grille annonçait une sprite large de toute la carte. */
  .picture { position: relative; display: inline-block; line-height: 0; }
  .variant-image img { max-width: 100%; height: auto; display: block; }
  /* LA GRILLE D'EMPRISE NE S'APPELLE PAS « grille » : ce nom-là est celui de la grille des vignettes, plus haut, et le lui reprendre a rendu toute la page absolue —
     sections vides, trois vignettes flottant hors de la page. Un nom déjà pris dans la même feuille est un nom pris, et une classe ne se choisit pas au plus évident.
     LA GRILLE NE MASQUE JAMAIS L'IMAGE : des traits d'un pixel, semi-transparents, et rien de plein — on juge la sprite, la grille ne fait que la situer. */
  .footprint { position: absolute; inset: 0; pointer-events: none; }
  .footprint::before {
    content: ""; position: absolute; inset: 0;
    background-image: linear-gradient(to right, rgba(255, 255, 255, .16) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(255, 255, 255, .16) 1px, transparent 1px);
    background-size: var(--case) var(--case-y);
    background-position: bottom left;
  }
  /* L'EMPRISE AU SOL EST ANCRÉE EN BAS ET CENTRÉE : c'est là que le sujet touche le sol, et c'est sur ce rectangle que le plan le pose. */
  .footprint-ground {
    position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
    border: 1px solid var(--accent); background: rgba(217, 164, 65, .10);
  }
  /* LE COUVERT EST CE QUE LE VOLUME SURPLOMBE — la vignette entière, puisque c'est sur lui qu'elle est posée. Il ne se dessine que s'il déborde de l'emprise. */
  .footprint-cover { position: absolute; inset: 0; border: 1px dashed rgba(255, 255, 255, .30); }
  .footprint-axis { position: absolute; background: rgba(255, 255, 255, .22); }
  .footprint-axis--x { left: 0; right: 0; bottom: 0; height: 1px; }
  .footprint-axis--y { top: 0; bottom: 0; left: 50%; width: 1px; }
  /* ONE COLOR PER STATE, DECLARED ONCE IN THE THEME AND NEVER RETYPED (operator, 2026-08-08). A hex code copied into three rules cannot be changed in one place,
     and the copies drift — the verdict line and the tile badge would end up two different oranges for the same state. */
  .verdict { margin: 6px 0 0; font-size: .82rem; }
  .verdict--to-rework { color: var(--state-rework-edge); }
  .verdict--dismissed { color: var(--state-dismissed-edge); }
  .verdict--validated { color: var(--state-validated-edge); }
  .previous-count, .to-produce { margin: 4px 0 0; font-size: .78rem; color: var(--muted); }
  /* THE STATE READS AT A GLANCE ON THE TILE: a small colored label under the name, in the same words as the filters. Color alone would say nothing to anyone who
     does not know the code, and a word alone would need reading — the two together are recognized before being read. */
  .tile-state {
    font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; padding: 1px 6px; border-radius: 2px;
    border: 1px solid var(--state-edge); color: var(--state-edge);
  }
  .tile[data-etat="to-rework"] { --state-edge: var(--state-rework-edge); }
  .tile[data-etat="dismissed"] { --state-edge: var(--state-dismissed-edge); }
  .tile[data-etat="to-produce"] { --state-edge: var(--state-to-produce-edge); }
  .tile[data-etat="to-judge"] { --state-edge: var(--state-to-judge-edge); }
  .tile[data-etat="validated"] { --state-edge: var(--state-validated-edge); }
  /* L'ÉCHELLE VIENT DU CONSTRUCTEUR PYTHON D'ORIGINE, ET ELLE NE SE RÉINVENTE PAS : chasse fixe, dix pixels, remplissage 3/6, rayon 2. La version PHP avait pris la
     taille du texte courant — seize pixels — et des remplissages larges, ce qui grossissait toute la carte d'un tiers sans que personne l'ait décidé. */
  .acts { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
  .act { display: inline-flex; position: relative; }
  .act input { position: absolute; inset: 0; width: 1px; height: 1px; opacity: 0; margin: 0; clip-path: inset(50%); overflow: hidden; }
  .act span, .open-comment {
    display: inline-block; font-family: ui-monospace, monospace; font-size: 10px; letter-spacing: .03em;
    padding: 3px 6px; border: 1px solid var(--line); border-radius: 2px; background: var(--card);
    color: var(--muted); cursor: pointer; user-select: none;
  }
  /* LE BOUTON D'OUVERTURE PORTE UN SIGNE ASCII, JAMAIS UN GLYPHE DÉCORATIF : le « ＋ » pleine chasse d'origine sort en carré vide dès qu'une police ne le porte pas,
     et c'est ce que la page a montré au premier contrôle. Un bouton dont le signe manque est un bouton qu'on ne clique pas. */
  .open-comment { min-width: 22px; text-align: center; }
  .act:hover span, .open-comment:hover { border-color: var(--accent); color: var(--accent); }
  .act input:focus-visible + span, .open-comment:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  /* DEUX ÉTATS, DEUX SIGNES : le bouton s'allume quand un commentaire est écrit dessous, et se marque simplement quand le champ est ouvert et vide. Les confondre
     laissait un champ vidé continuer d'annoncer un texte qui n'existait plus. */
  .open-comment[data-filled="true"] { border-color: var(--accent); color: var(--accent); }
  .open-comment[aria-expanded="true"][data-filled="false"] { border-color: var(--muted); color: var(--ink); }
  .act--valider input:checked + span { background: #2f5c3a; border-color: #4e8a5e; color: #eaf6ec; }
  .act--reprendre input:checked + span { background: #6b4a1c; border-color: #a4762c; color: #fbf1e0; }
  .act--ecarter input:checked + span { background: #5c2f2f; border-color: #8a4e4e; color: #f6eaea; }
  /* LE CHAMP TIENT DANS SA CARTE : sans box-sizing, ses bordures et son remplissage s'ajoutent aux cent pour cent de largeur et il déborde de quelques pixels — ce
     qui se voit tout de suite sur une grille de cartes. */
  /* LA CROIX EST COLLÉE AU CHAMP, en haut à droite : c'est le geste courant pour vider une saisie, et un bouton posé à côté avec son mot écrit prenait la place
     d'un tiers du champ pour dire ce qu'une croix dit sans un mot. */
  .comment-zone { position: relative; margin-top: 4px; }
  .comment-zone[hidden] { display: none; }
  .comment { display: block; width: 100%; box-sizing: border-box; background: var(--bg); border: 1px solid var(--line); border-radius: 2px; color: var(--ink);
         font-family: ui-monospace, monospace; font-size: 11px; line-height: 1.45; padding: 4px 22px 4px 6px; resize: vertical; }
  /* LA CROIX EST DANS LE COIN HAUT DROIT DU CHAMP, POSÉE DESSUS — demandée trois fois par l'opérateur, et perdue deux fois en réécrivant la carte. Le champ lui
     réserve sa place à droite par son propre remplissage, pour qu'elle ne vienne jamais sur le texte. Sa règle est éprouvée par scripts/check-review-pages.php. */
  .clear-comment {
    position: absolute; top: 4px; right: 4px; width: 18px; height: 18px; padding: 0; line-height: 1;
    display: flex; align-items: center; justify-content: center;
    font-family: ui-monospace, monospace; font-size: 13px;
    border: 1px solid var(--line); border-radius: 2px; background: var(--card); color: var(--muted); cursor: pointer;
  }
  .clear-comment:hover { border-color: var(--accent); color: var(--accent); }
  .clear-comment[hidden] { display: none; }
  .variant { box-sizing: border-box; }
  /* LES MESURES SUIVENT L'ÉCHELLE D'ORIGINE : l'intitulé est une étiquette — onze pixels, petites capitales espacées —, la valeur est un chiffre qu'on compare d'une
     ligne à l'autre, donc en chasse tabulaire pour que les colonnes s'alignent d'elles-mêmes. Toutes deux au même gris que le reste : ce sont des constats, pas des
     verdicts. */
  .measures { display: grid; grid-template-columns: auto 1fr; gap: 2px 12px; margin: 8px 0 0; padding: 6px 0 0; border-top: 1px solid var(--line); }
  .measures dt { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); white-space: nowrap; }
  .measures dd { margin: 0; font-size: 13.5px; font-variant-numeric: tabular-nums; }
  .open-text { display: block; width: 100%; margin-top: 6px; padding: 5px 8px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; color: inherit;
                font: inherit; font-size: .78rem; text-align: left; cursor: pointer; }
  .open-text:hover { border-color: var(--accent); color: var(--accent); }
  .fsp-tools { display: flex; gap: 8px; }
  .fsp-tools button { padding: 4px 12px; background: none; border: 1px solid var(--line); border-radius: 4px; color: inherit; cursor: pointer; }
  #drawer-body { white-space: pre-wrap; font-size: .82rem; line-height: 1.5; }
  /* LE TEXTE SE LIT À CÔTÉ DE L'IMAGE, JAMAIS PAR-DESSUS (opérateur, 2026-08-08). En panneau plein écran, la consigne recouvrait la sprite qu'elle décrit — or on ne
     juge une image qu'en confrontant ce qui était demandé à ce qui est sorti, et un aller-retour entre deux écrans ne remplace pas un regard. Le panneau est accolé
     au bord droit, et la page ouverte se resserre d'autant : rien n'est recouvert, tout se lit d'un même regard. */
  .drawer {
    position: fixed; top: 0; right: 0; bottom: 0; z-index: 200; display: flex; flex-direction: column; width: min(38vw, 560px);
    background: var(--card, var(--bg)); border-left: 1px solid var(--line); overflow: auto;
  }
  .drawer[hidden] { display: none; }
  .drawer-close {
    padding: 2px 8px; background: none; border: 1px solid var(--line); border-radius: 4px; color: inherit; font-size: 1rem; line-height: 1.2; cursor: pointer;
  }
  /* LA PAGE SE RESSERRE, ELLE NE SE DÉCALE PAS : un décalage ferait sortir la moitié droite de l'écran, alors qu'on veut voir la fiche entière et le texte. */
  body.drawer-open .fsp, body.drawer-open > .wrap { padding-right: min(38vw, 560px); }
  /* SUR UN ÉCRAN ÉTROIT, LE TEXTE PASSE DESSOUS : à moins de mille pixels, deux colonnes ne laissent la place ni à l'une ni à l'autre. */
  @media (max-width: 1000px) {
    .drawer { top: auto; left: 0; width: auto; height: 50vh; border-left: 0; border-top: 1px solid var(--line); }
    body.drawer-open .fsp, body.drawer-open > .wrap { padding-right: 0; padding-bottom: 50vh; }
  }
  .fsp-body--image { display: flex; align-items: center; justify-content: center; }
  #fsp-image-corps { max-width: 100%; max-height: 80vh; background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 24px 24px; }
  /* UNE VERSION ANTÉRIEURE EST UNE CARTE COMME LA COURANTE, simplement plus discrète : même largeur, même grille, même mesures, un fond un cran plus sourd pour
     qu'on ne la confonde pas avec celle qui fait foi. Elles s'alignent en colonne, la plus récente en haut, comme le référentiel les range. */
  .previous { padding: 8px; border: 1px dashed var(--line); border-radius: 4px; opacity: .85; }
  /* AGRANDIE SUR PLACE : la vignette double de taille sans quitter la rangée, donc les autres versions restent visibles autour d'elle — c'est tout l'objet, on compare. */
  .fold { margin-top: 6px; font-size: .8rem; color: var(--muted); }
  .fold summary { cursor: pointer; }
  .fold pre { max-height: 40vh; overflow: auto; white-space: pre-wrap; font-size: .74rem; }
  .previous-list { display: flex; flex-direction: column; gap: 10px; }
  .filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }
  .filter { padding: 5px 12px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; color: inherit; font: inherit; cursor: pointer; }
  .filter[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); font-weight: 600; }
  .filter span { color: var(--muted); }
  /* UNE ORPHELINE SE REGARDE : c'est en la voyant qu'on décide si c'est un reste, une sonde, ou une sprite dont l'inscription s'est perdue. Le damier dit sa transparence, comme partout ailleurs. */
  .orphans { display: flex; flex-wrap: wrap; gap: 10px; margin: 0; }
  .orphan { margin: 0; display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 8px; background: var(--card); border: 1px solid var(--line); border-radius: 3px; }
  .orphan img {
    max-width: 100%; height: auto; display: block;
    background: repeating-conic-gradient(var(--damier-a) 0 25%, var(--damier-b) 0 50%) top left / 16px 16px;
  }
  .orphan figcaption { color: var(--muted); font-family: ui-monospace, monospace; font-size: .7rem; word-break: break-all; max-width: 176px; text-align: center; }
  .tile[hidden] { display: none; }
  .type[hidden] { display: none; }
{$releveStyles}
{$reloadStyles}
</style>

<div class="wrap">
  <h1>Suivi des sprites</h1>
  <div class="fsp" id="fsp-image" hidden>
    <div class="fsp-bar"><p class="fsp-title" id="fsp-image-titre"></p>
      <button type="button" class="fsp-close" aria-label="Fermer">✕</button></div>
    <div class="fsp-body fsp-body--image"><img id="fsp-image-corps" src="" alt=""></div>
  </div>

  <aside class="drawer" id="drawer" hidden aria-label="Le texte d'une version">
    <div class="fsp-bar"><p class="fsp-title" id="drawer-title"></p>
      <span class="fsp-tools"><button type="button" id="drawer-copy">Copier</button>
      <button type="button" class="drawer-close" aria-label="Fermer">✕</button></span></div>
    <div class="fsp-body"><pre id="drawer-body"></pre></div>
  </aside>

  <p class="lede">Une vignette par sujet. Un clic ouvre le sujet en plein écran, avec ses variants, leurs versions, leurs mesures, la consigne qui les a produits et les actions — toutes
  offertes, toujours. Cochez « Comparer » sur plusieurs variants pour ne garder qu'eux, côte à côte, à quarante-huit pixels par case.</p>

  <div class="filters">{$filtres}</div>

{$sections}
{$horsModele}
{$releveMarkup}
</div>
{$reloadMarkup}

{$popins}

<script>
(function () {
  var MEMOIRE = 'gatebeast-suivi-sprites';
  var etat = {};
  try { etat = JSON.parse(localStorage.getItem(MEMOIRE)) || {}; } catch (error) { etat = {}; }

  function retenir() {
    try { localStorage.setItem(MEMOIRE, JSON.stringify(etat)); } catch (error) { /* un cadre peut refuser le stockage : la page marche quand même, pour la visite en cours */ }
  }

  Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
    var id = box.getAttribute('data-id');
    var acte = box.getAttribute('data-acte');
    box.checked = Boolean(etat[id] && etat[id][acte]);
    box.addEventListener('change', function () {
      etat[id] = etat[id] || {};
      /* UN VERDICT EST UN SEUL DES TROIS (opérateur, 2026-08-08 : « je peux cocher les 3 »). Valider, à reprendre et écarter s'excluent : une image ne peut pas être
         acceptée et rejetée à la fois, et un relevé qui la porterait dans deux colonnes ne dit plus rien à celui qui le lit. Ce sont des cases à cocher parce que
         l'apparence le demande — on les décoche pour revenir en arrière —, mais elles se comportent comme un choix unique : cocher l'une décoche les autres. */
      if (box.checked) {
        Array.prototype.forEach.call(document.querySelectorAll('.acts input[data-id="' + id + '"]'), function (other) {
          if (other !== box) {
            other.checked = false;
            etat[id][other.getAttribute('data-acte')] = false;
          }
        });
      }
      etat[id][acte] = box.checked;
      retenir();
      /* REFUSER UNE IMAGE, C'EST DIRE POURQUOI : cocher « À reprendre » ou « Écarter » ouvre la zone de saisie et lui donne le clavier. Sans le motif, la reprise
         repart à l'aveugle — c'est ce qui a coûté trois tentatives sur le sapin. « Valider » n'ouvre rien : un accord n'a rien à justifier. */
      if (box.checked && (acte === 'reprendre' || acte === 'ecarter')) {
        var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
        var ouvrir = document.querySelector('.open-comment[data-open="' + id + '"]');
        if (zone) {
          zone.hidden = false;
          if (ouvrir) { ouvrir.setAttribute('aria-expanded', 'true'); }
          var champ = zone.querySelector('.comment');
          if (champ) { champ.focus({preventScroll: true}); }
        }
      }
    });
  });

  /* LE BOUTON « ＋ » OUVRE ET REFERME LA ZONE DE SAISIE, et la zone s'ouvre d'elle-même quand elle porte déjà un commentaire : un texte écrit qui ne se voit pas est
     un texte perdu pour celui qui rouvre la page. */
  Array.prototype.forEach.call(document.querySelectorAll('.open-comment'), function (button) {
    var id = button.getAttribute('data-open');
    var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
    if (!zone) { return; }
    if (etat[id] && etat[id].comment) { zone.hidden = false; button.setAttribute('aria-expanded', 'true'); }
    button.addEventListener('click', function () {
      zone.hidden = !zone.hidden;
      button.setAttribute('aria-expanded', zone.hidden ? 'false' : 'true');
      if (!zone.hidden) { zone.querySelector('.comment').focus(); }
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
    var id = field.getAttribute('data-id');
    if (etat[id] && etat[id].comment) { field.value = etat[id].comment; }
    field.addEventListener('input', function () {
      etat[id] = etat[id] || {};
      etat[id].comment = field.value;
      retenir();
    });
  });

  /* SORTIR D'UNE COMPARAISON SANS SORTIR DU SUJET (opérateur, 2026-08-07) : la seule façon d'en sortir était de décocher chaque variant un par un, ou de fermer le
     panneau — ce qui faisait perdre le sujet qu'on jugeait. Un bouton la quitte d'un geste, et il n'apparaît que pendant qu'elle dure. */
  function quitterComparaison(liste) {
    Array.prototype.forEach.call(liste.querySelectorAll('.compare'), function (box) { box.checked = false; });
    Array.prototype.forEach.call(liste.querySelectorAll('.variant'), function (variant) { variant.classList.remove('picked'); });
    liste.classList.remove('comparison');
  }

  /* UNE COMPARAISON NE SURVIT PAS À LA FERMETURE DU SUJET : rouvrir une fiche doit la montrer entière, pas dans l'état où on l'avait laissée trois sujets plus tôt.
     Une sélection oubliée fait croire à un sujet qui n'a plus que deux variants. */
  Array.prototype.forEach.call(document.querySelectorAll('.fsp-close'), function (button) {
    button.addEventListener('click', function () {
      var panneau = button.closest('.fsp');
      var liste = panneau ? panneau.querySelector('.variants') : null;
      if (liste) { quitterComparaison(liste); }
    });
  });

  /* LA COMPARAISON : cocher plusieurs variants ne garde qu'eux à l'écran, côte à côte et plus grands. Décocher tout revient à la liste entière. */
  Array.prototype.forEach.call(document.querySelectorAll('.compare'), function (box) {
    box.addEventListener('change', function () {
      var liste = box.closest('.variants');
      var retenus = liste.querySelectorAll('.compare:checked');
      Array.prototype.forEach.call(liste.querySelectorAll('.variant'), function (variant) {
        variant.classList.toggle('picked', variant.querySelector('.compare').checked);
      });
      /* LA COMPARAISON N'ENGAGE QU'À PARTIR DE DEUX : à un seul variant coché, elle masquait tous les autres, donc la case du second n'était plus là pour être cochée.
         On ne pouvait jamais comparer que le premier avec lui-même (opérateur, 2026-08-07). */
      liste.classList.toggle('comparison', retenus.length > 1);
    });
  });

  /* EFFACER UN COMMENTAIRE NE LE DÉTRUIT PAS : le texte effacé est gardé, et le bouton propose de le rétablir tant qu'on n'a pas écrit autre chose. L'opérateur a
     demandé une solution sans perte — effacer d'un clic ne doit pas détruire ce qu'on vient d'écrire. */
  Array.prototype.forEach.call(document.querySelectorAll('.clear-comment'), function (button) {
    var field = button.parentNode.querySelector('.comment');
    var id = button.getAttribute('data-id');
    var ouvrir = document.querySelector('.open-comment[data-open="' + id + '"]');
    var garde = null;
    /* LA CROIX RESTE UNE CROIX, ET C'EST TOUT LE POINT : elle porte « × » pour vider, « ↺ » pour rétablir, jamais un mot. Écrire « Effacer » dedans lui faisait perdre
       sa place et sa forme — c'est ainsi que la croix demandée trois fois a disparu deux fois. Elle se cache quand il n'y a rien à effacer. */
    function rendre() {
      button.textContent = garde === null ? '×' : '↺';
      button.hidden = !field.value.trim() && garde === null;
      if (ouvrir) { ouvrir.setAttribute('data-filled', field.value.trim() ? 'true' : 'false'); }
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
      etat[id].comment = field.value;
      retenir();
      rendre();
    });
    field.addEventListener('input', function () { garde = null; rendre(); });
    rendre();
  });

  /* LE BOUTON D'OUVERTURE DIT S'IL Y A UN TEXTE DESSOUS, dès l'ouverture de la page et à chaque frappe : sans ça, une carte repliée ne laisse rien deviner de ce
     qu'elle contient, et il faut toutes les déplier pour retrouver ce qu'on a écrit. */
  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
    var id = field.getAttribute('data-id');
    var ouvrir = document.querySelector('.open-comment[data-open="' + id + '"]');
    if (!ouvrir) { return; }
    function dire() { ouvrir.setAttribute('data-filled', field.value.trim() ? 'true' : 'false'); }
    field.addEventListener('input', dire);
    dire();
  });

  /* LES FILTRES agissent sur la grille : ils cachent les vignettes qui ne sont pas dans l'état demandé, et une section entièrement vide se cache avec elles —
     une rubrique qui reste ouverte sur rien fait croire qu'il n'y a rien à voir alors qu'on a simplement filtré. */
  Array.prototype.forEach.call(document.querySelectorAll('.filter'), function (button) {
    button.addEventListener('click', function () {
      var voulu = button.getAttribute('data-filtre');
      Array.prototype.forEach.call(document.querySelectorAll('.filter'), function (other) {
        other.setAttribute('aria-pressed', other === button ? 'true' : 'false');
      });
      Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (tile) {
        tile.hidden = voulu !== '{$stateAll}' && tile.getAttribute('data-etat') !== voulu;
      });
      Array.prototype.forEach.call(document.querySelectorAll('.type'), function (section) {
        var tiles = section.querySelectorAll('.tile');
        var visible = Array.prototype.filter.call(tiles, function (tile) { return !tile.hidden; });
        section.hidden = tiles.length > 0 && visible.length === 0;
      });
    });
  });

  /* L'AGRANDISSEMENT D'UNE VERSION ANTÉRIEURE N'A PLUS D'OBJET : elle est désormais montrée à la même échelle que la courante, avec sa grille, ses mesures et sa consigne
     (opérateur, 2026-08-07 : « même présentation, aucune spécificité »). Il n'y a plus de vignette à demi-taille à agrandir — la comparaison se fait à l'œil, sur place. */

  /* UN TEXTE S'OUVRE À CÔTÉ DE L'IMAGE, dans le panneau accolé au bord droit, et se copie d'un bouton. Il ne passe PAS par la pile des panneaux plein écran : il ne
     recouvre rien, donc il n'a rien à empiler, et la touche d'échappement doit le fermer LUI avant de fermer la fiche qu'on est en train de lire. */
  var drawerBody = document.getElementById('drawer-body');
  var drawerTitle = document.getElementById('drawer-title');
  var drawer = document.getElementById('drawer');
  function openDrawer(titre, contenu) {
    drawerTitle.textContent = titre;
    drawerBody.textContent = contenu;
    drawer.hidden = false;
    drawer.scrollTop = 0;
    document.body.classList.add('drawer-open');
  }
  function closeDrawer() {
    drawer.hidden = true;
    document.body.classList.remove('drawer-open');
  }
  Array.prototype.forEach.call(document.querySelectorAll('.open-text'), function (button) {
    button.addEventListener('click', function () {
      var porteur = button.nextElementSibling;
      openDrawer(button.getAttribute('data-titre'), porteur ? porteur.textContent : '');
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('.drawer-close'), function (button) {
    button.addEventListener('click', closeDrawer);
  });
  document.getElementById('drawer-copy').addEventListener('click', function () {
    var holder = document.createElement('textarea');
    holder.value = drawerBody.textContent;
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

  /* UNE FSP S'OUVRE PAR-DESSUS UNE AUTRE, ELLE NE LA REMPLACE PAS (opérateur, 2026-08-07). En fermer une fait réapparaître celle du dessous, et on remonte ainsi jusqu'à la page. Remplacer
     faisait perdre le sujet qu'on était en train de juger dès qu'on ouvrait un texte : il fallait rouvrir la vignette et refaire défiler jusqu'au variant. */
  var pile = [];
  /* LE RECHARGEMENT AUTOMATIQUE DE PAGE (RAP) DOIT RENDRE LA PAGE OÙ ON L'A LAISSÉE, PANNEAUX COMPRIS (opérateur, 2026-08-08 : « ça recharge la page et ça ne me
     ré-ouvre PAS la popin où j'étais »). Le défilement était déjà rendu ; la pile des panneaux ouverts ne l'était pas, si bien qu'une reconstruction pendant qu'on
     juge un sujet renvoyait à la planche entière, à rouvrir et refaire défiler. La pile est donc écrite à chaque ouverture et à chaque fermeture, dans le stockage
     de session — elle appartient à cet onglet et à cette visite, pas à la machine. */
  var MEMOIRE_PILE = 'gatebeast-sprites-panneaux';
  function retenirPile() {
    try {
      sessionStorage.setItem(MEMOIRE_PILE, JSON.stringify(pile.map(function (popin) { return popin.id; })));
    } catch (error) { /* un cadre peut refuser le stockage : la page marche quand même */ }
  }
  function empiler(popin) {
    if (!popin) { return; }
    popin.hidden = false;
    popin.scrollTop = 0;
    /* CHAQUE PANNEAU EMPILÉ PASSE AU-DESSUS DU PRÉCÉDENT, et c'est ce qui manquait : tous partageaient le même plan, donc celui du texte — écrit AVANT les panneaux
       de sujet dans la page — s'ouvrait DERRIÈRE celui qu'on regardait. Le bouton semblait mort alors qu'il faisait son travail : une sonde a montré le panneau
       ouvert, avec ses milliers de caractères de texte, simplement invisible. Trois lectures du code n'avaient rien donné ; un clic simulé a tranché en une fois. */
    popin.style.zIndex = String(90 + pile.length + 1);
    document.body.style.overflow = 'hidden';
    pile.push(popin);
    retenirPile();
  }
  function fermer() {
    /* LE TEXTE APPARTIENT À LA FICHE OUVERTE : la laisser derrière une fiche fermée montrerait la consigne d'un sujet qu'on ne regarde plus. */
    closeDrawer();
    var haut = pile.pop();
    if (!haut) { return; }
    haut.hidden = true;
    haut.style.zIndex = '';
    if (!pile.length) { document.body.style.overflow = ''; }
    retenirPile();
  }
  /* On rouvre dans l'ordre où c'était empilé, sinon le panneau du dessous passerait au-dessus. Un panneau disparu de la page — un sujet retiré entre deux
     constructions — est simplement sauté : on ne rouvre pas ce qui n'existe plus, et on ne refuse pas la page pour autant. */
  try {
    JSON.parse(sessionStorage.getItem(MEMOIRE_PILE) || '[]').forEach(function (id) {
      empiler(document.getElementById(id));
    });
  } catch (error) { /* stockage refusé ou illisible : la page s'ouvre simplement fermée */ }
  Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (tile) {
    tile.addEventListener('click', function () {
      empiler(document.getElementById('fsp-' + tile.getAttribute('data-sujet')));
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('.fsp-close'), function (button) { button.addEventListener('click', fermer); });
  /* LE PANNEAU ACCOLÉ SE FERME EN PREMIER : il est ouvert PAR-DESSUS une fiche qu'on est en train de lire, donc échapper doit rendre la fiche, pas la fermer avec lui. */
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') { return; }
    if (!drawer.hidden) { closeDrawer(); return; }
    fermer();
  });

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
    var mots = Object.keys(etat).filter(function (id) { return etat[id] && etat[id].comment; });
    if (mots.length) {
      lignes.push('COMMENTAIRES (' + mots.length + ')');
      mots.forEach(function (id) { lignes.push('  - ' + id); lignes.push('      ' + etat[id].comment); });
    }
    return lignes.join('\n');
  };
})();
{$releveScript}
</script>
{$reloadScript}
HTML;

// LES ORPHELINS : toute image livrée sous assets/cutout/ que l'inventaire ne réclame pas. Une image qui existe sans être inscrite n'existe pour personne — elle
// n'apparaît nulle part, personne ne peut la juger, et elle se refait. La page les montre plutôt que de laisser croire que tout est rangé.
$reclamees = [];
foreach ($inventory->sujets() as $sujet) {
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
// AN ORPHAN IS SHOWN, NOT NAMED (operator, 2026-08-08: "it must go back to the old display where the images could be seen, see the py version"). A file name says an image exists and nothing about
// what it is: deciding whether an unclaimed image is a leftover, a probe or a sprite whose record was lost takes one look at it. Naming it forces the operator to open it by hand, one by one.
$orphanCards = '';
foreach ($orphelines as $orphan) {
    $shot = $thumbnails->shrink($orphan, ORPHAN_WIDTH);
    $orphanCards .= sprintf('<figure class="orphan">%s<figcaption>%s</figcaption></figure>',
        $shot ? sprintf('<img src="%s" width="%d" height="%d" alt="" loading="lazy">', $shot[0], $shot[1], $shot[2]) : '<p class="to-produce">Image illisible</p>',
        escape($orphan));
}
$horsModele = $orphelines
    ? '  <section class="type"><h2>Hors modèle <span class="slug">' . count($orphelines) . ' image(s) livrée(s) qu\'aucun variant ne réclame</span></h2>'
      . '<div class="orphans">' . $orphanCards . '</div></section>'
    : '  <section class="type"><h2>Hors modèle <span class="slug">rien</span></h2><p class="lede">Chaque image livrée est réclamée par un variant.</p></section>';

$filtres = '';
// THE FILTERS CARRY THE SAME STATES AS THE TILES, in the same order and in the same words: "to judge" replaced "produced", which did not say what was left to do.
// A produced subject whose images nobody has judged is exactly what one opens this page looking for.
foreach ([STATE_ALL => 'Tout'] + STATE_LABELS as $key => $label) {
    $filtres .= sprintf('<button type="button" class="filter" data-filtre="%s" aria-pressed="%s">%s%s</button>',
        $key, $key === STATE_ALL ? 'true' : 'false', escape($label), $key === STATE_ALL ? '' : ' <span>' . ($compte[$key] ?? 0) . '</span>');
}

$page = strtr($page, [
    // LA PALETTE EST CELLE DU CONSTRUCTEUR PYTHON, pas celle des autres pages : la migration avait emporté l'habillage de cette page-là, ce que personne n'avait demandé. Les autres pages gardent
    // « encre », les changer n'a jamais été demandé non plus.
    '{$theme}' => $theme->css('origine'),
    '{$favicon}' => $favicon->tag(),
    '{$reloadStyles}' => $reload->styles(),
    '{$reloadMarkup}' => $reload->markup(),
    '{$reloadScript}' => $reload->script('/sprites'),
    // THE STATE THAT MEANS "NO FILTER" IS WRITTEN ONCE, in the constant, and handed to the script rather than retyped in it: a filter button and the code that
    // reads it must agree on the word, and two spellings of it would silently show nothing.
    '{$stateAll}' => STATE_ALL,
    '{$filtres}' => $filtres,
    '{$horsModele}' => $horsModele,
    '{$releveStyles}' => $releve->styles(),
    '{$releveMarkup}' => $releve->markup('Votre relevé, à me coller en conversation'),
    '{$releveScript}' => $releve->script(),
    '{$sections}' => $sections,
    '{$popins}' => $popins,
]);

file_put_contents($outputPath, $page);
printf("%s — %d sujets, %.1f ko%s\n", $outputPath, count($inventory->sujets()), strlen($page) / 1024,
    $missing ? ', ' . count($missing) . ' image(s) illisible(s)' : '');
if ($inventory->sansLibelle) {
    fwrite(STDERR, 'SANS LIBELLÉ : ' . implode(', ', $inventory->sansLibelle) . "\n");
}

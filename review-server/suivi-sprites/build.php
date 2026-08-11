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
// THE TWO FAMILIES OF IMAGES UNDER assets/: the master as it comes out of the generator, and the cutout delivered to the game. Both words are those of the paths
// the referential records — `master` and `path` — and they were typed out wherever the page swept the disk.
const MASTER_DIRECTORY = 'poc';
const DELIVERABLE_DIRECTORY = 'cutout';
// Le raccourci d'une longueur au sol qui s'enfonce, sous la caméra à 60 degrés — le sinus de l'angle. Écrit ici en attendant que la page le demande au service qui
// détient l'échelle, qui est en Python : c'est la seule valeur du modèle que cette page recopie, et elle est à supprimer dès que les deux côtés se parlent.
const GROUND_DEPTH_FACTOR = 0.8660;

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$inventory = new Inventory($root);
$thumbnails = new Thumbnail($root);
$theme = Theme::get();
$favicon = Favicon::get();
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
    'rework' => STATE_TO_REWORK,
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
$expected = 0;
$produced_total = 0;

foreach ($inventory->types() as $typeName => $type) {
    $codes = $inventory->subjectsOfType($typeName);
    if (!$codes) {
        continue;
    }
    $tiles = '';
    foreach ($codes as $code) {
        $subject = $inventory->subject($code);
        $spread = $inventory->spread($subject);
        $main = $inventory->mainVariant($subject);
        $current = $main ? $inventory->currentRepresentation($main) : null;
        $produced = 0;
        foreach ($subject['variants'] as $variant) {
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
        $etat = subjectState($inventory, $subject);
        $compte[$etat] = ($compte[$etat] ?? 0) + 1;
        // THE EXPECTED TOTAL IS WHAT NOBODY SAYS, and it is what the original builder announced under its title. The filters count SUBJECTS by state; this counts
        // IMAGES, produced and expected, across every subject — the only measure that says where the production as a whole stands.
        $expected += count($subject['variants']);
        $produced_total += $produced;
        // THE STATE SHOWS ON THE TILE, AND IT IS THE FIRST THING ONE LOOKS FOR THERE (operator, 2026-08-08): does this subject need judging, is it fully validated,
        // fully produced, or is something left to rework? The tile carried its state as an attribute, so the filters knew it and the eye did not.
        $tiles .= sprintf(
            '        <button type="button" class="tile" data-subject="%s" data-state="%s"><span class="tile-image">%s</span>'
            . '<span class="tile-name">%s</span><span class="tile-state">%s</span><span class="tile-count">%d/%d variant%s</span></button>' . "\n",
            escape($code), escape($etat), $picture, escape(capitalize($inventory->label($code))), escape(STATE_LABELS[$etat]),
            $produced, count($subject['variants']), count($subject['variants']) > 1 ? 's' : ''
        );
        $popins .= popin($inventory, $thumbnails, $root, $code, $subject);
    }
    // THE SECTION HEADER OF THE ORIGINAL BUILDER: title and code on the left, THE COUNT ON THE RIGHT, a rule underneath. The count on the right is what gives the
    // page the look of a survey rather than a pile — one reads at a glance how many subjects each family carries, without counting them by eye.
    $sections .= sprintf(
        "    <section class=\"type\">\n      <header class=\"type-head\"><h2>%s <span class=\"slug\">%s</span></h2>"
        . "<span class=\"type-count\">%d sujet%s</span></header>\n      <div class=\"grid\">\n%s      </div>\n    </section>\n",
        escape(TYPE_LABELS[$typeName] ?? $typeName), escape($typeName),
        count($codes), count($codes) > 1 ? 's' : '', $tiles
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
function subjectState(Inventory $inventory, array $subject): string
{
    $states = [];
    foreach ($subject['variants'] ?? [] as $variant) {
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
 * THE REFERENTIEL STILL SPELLS ITS VERDICTS IN FRENCH — "validee", "rework", "ecartee" — and this is the one place that translates them. Renaming the stored
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
function measurements(array $representation, array $subject): string
{
    $lignes = [];
    $footprint = $subject['footprint'];
    $cover = $subject['cover'] ?? null;
    // CHAQUE MESURE SUR SA LIGNE, et l'emprise, le couvert et la hauteur d'abord : ce sont les trois seuils contre lesquels une image se juge. Groupées sur une
    // ligne, elles se lisaient comme une phrase et il fallait les chercher au milieu.
    $lignes[] = ['Emprise au sol', sprintf('%d × %d case%s', $footprint['columns'], $footprint['rows'], $footprint['columns'] > 1 ? 's' : '')];
    $lignes[] = ['Couvert', $cover ? sprintf('%d × %d cases', $cover['columns'], $cover['rows']) : 'égal à l\'emprise'];
    $lignes[] = ['Hauteur déclarée', sprintf('%s case%s', $subject['height'] ?? '—', ($subject['height'] ?? 0) > 1 ? 's' : '')];

    $measures = $representation['measures'] ?? null;
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
        if (isset($measures['height'])) {
            $lignes[] = [$measures['height']['tenue'] ? 'Hauteur tenue' : 'HAUTEUR HORS FOURCHETTE', $measures['height']['constat']];
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
/**
 * The button that opens a text, and the text itself, folded into the page.
 *
 * THE PATH BELONGS TO THE DRAWER, NEITHER TO THE BUTTON NOR TO THE DRAWER TITLE (operator, 2026-08-11). It is still shown, relative to the project root — one has
 * to know which file is being read in order to correct it, open it elsewhere or quote it, and two prompts from two versions of the same variant look alike enough
 * to be confused. But under a button label it turns a one-line control into a two-line block of monospace, and in the title it pushes the label out of sight. It
 * travels on the button as data, and the drawer displays it beside the text it came from.
 */
function textButton(string $label, string $path, string $root): string
{
    $relative = str_replace($root . '/', '', $path);

    return sprintf(
        '<button type="button" class="open-text" data-title="%s" data-path="%s">%s</button>'
        . '<script type="text/plain" class="text-source">%s</script>',
        escape($label), escape($relative), escape($label),
        str_replace('</script', '<\/script', file_get_contents($path))
    );
}

function frozenPrompt(string $root, array $representation): string
{
    $master = $representation['master'] ?? null;
    if (!$master) {
        return '';
    }
    $frozen = $root . '/assets/' . preg_replace('/\.png$/', '.txt', $master);
    $name = pathinfo($master, PATHINFO_FILENAME);
    $report = $root . '/var/generations/sprites/' . $name . '-rapport.md';
    $blocks = '';
    // UN TEXTE SE LIT EN GRAND ET SE COPIE : replié dans une carte de deux cent soixante pixels, il ne sert à rien. Le résumé ouvre la FSP du texte, où il tient
    // toute la page et se sélectionne d'un bouton.
    // A DISPLAYED TEXT SAYS WHERE IT COMES FROM (operator, 2026-08-08). Without its path, one has to guess which file is being read in order to correct it, open
    // it in an editor or quote it — and two prompts from two versions of the same variant look alike enough to be confused. The path is given RELATIVE TO THE
    // PROJECT ROOT: that is what copies straight into a command, where an absolute path only means something on this machine.
    if (is_file($frozen)) {
        $blocks .= textButton('La consigne envoyée', $frozen, $root);
    }
    if (is_file($report)) {
        $blocks .= textButton('Le rapport de génération', $report, $root);
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

function grid(array $subject, array $spread, int $width, int $height): string
{
    $footprint = $subject['footprint'];
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
function representation(Thumbnail $thumbnails, string $root, array $subject, array $spread, array $representation): string
{
    // THE SCALE IS FIXED AND THE SAME FOR EVERY SUBJECT: forty-eight pixels per tile in the panel, a tile staying a tile from one subject to the next. A large oak
    // therefore takes four times the width of a fence, which is the truth of the world; thumbnails all of one width let you neither compare two subjects nor see
    // that a sprite overflows — which is precisely what the footprint and the cover are there to show.
    $shot = image($thumbnails, $representation, COMPARE_PIXELS_PER_TILE * $spread['columns']);
    // LA GRILLE SE POSE SUR L'IMAGE, À L'ÉCHELLE OÙ ELLE EST MONTRÉE (opérateur, 2026-08-07) : sans elle, une sprite se juge dans le vide — on ne voit ni ce
    // qu'elle occupe au sol, ni ce qu'elle surplombe, ni où sont ses axes. Les trois se lisent à des couleurs différentes, et les valeurs sont celles du
    // référentiel, jamais recalculées ici.
    // L'IMAGE ET SA GRILLE SONT ENFERMÉES ENSEMBLE : sans cette enveloppe qui épouse l'image, la grille se cale sur la carte entière et son cadre d'emprise
    // s'étire sur toute la largeur, en annonçant une sprite bien plus large qu'elle n'est.
    $picture = $shot
        ? sprintf('<span class="picture"><img src="%s" width="%d" height="%d" alt="">%s</span>', $shot[0], $shot[1], $shot[2], grid($subject, $spread, $shot[1], $shot[2]))
        : '<p class="to-produce">Image illisible</p>';
    $state = VERDICT_STATES[$representation['verdict'] ?? ''] ?? null;

    return sprintf('%s<div class="variant-image">%s</div>%s%s%s',
        version($root, $representation),
        $picture,
        // THE VERDICT IS SHOWN THROUGH THE SAME VOCABULARY AS EVERYTHING ELSE: the stored French value is translated once, and the page speaks one language to itself.
        $state ? sprintf('<p class="verdict verdict--%s">%s</p>', escape($state), escape(STATE_LABELS[$state])) : '',
        measurements($representation, $subject),
        // LES VERSIONS ANTÉRIEURES PASSENT SOUS LA CONSIGNE ET LE RAPPORT DE LA VERSION COURANTE (opérateur, 2026-08-07) : intercalées entre les mesures et
        // eux, elles séparaient une version de ses propres pièces justificatives et l'on ne savait plus à laquelle se rapportait quoi.
        frozenPrompt($root, $representation)
    );
}

/** La FSP d'un sujet : ses variants, la version courante de chacun en grand, les antérieures, les mesures, la consigne, le verdict et les actions. */
function popin(Inventory $inventory, Thumbnail $thumbnails, string $root, string $code, array $subject): string
{
    $spread = $inventory->spread($subject);
    $blocks = '';
    foreach ($subject['variants'] as $variant) {
        $ref = $variant['ref'];
        $current = $inventory->currentRepresentation($variant);
        // TWO NAMES BECAUSE THEY ARE TWO THINGS: $current is the current representation, a piece of data; $rendered is its markup. They shared one name for a
        // moment, during a vocabulary migration, and the page stopped building — the markup arrived where the data was expected.
        $rendered = $current
            ? representation($thumbnails, $root, $subject, $spread, $current)
            : '<div class="variant-image"><p class="to-produce">À produire</p></div>';
        $comment = $current['operator_comment'] ?? '';
        $previous = $inventory->previousRepresentations($variant);
        $identifier = $code . ' ' . $ref;
        $anciennes = '';
        foreach ($previous as $old) {
            // MÊME PRÉSENTATION QUE LA COURANTE, AUCUNE SPÉCIFICITÉ (opérateur, 2026-08-07) : son image à la même échelle avec sa grille d'emprise, son nom de
            // fichier, sa date, son verdict, ses mesures et sa consigne. C'est en la mettant en regard de la courante qu'on décide si la reprise a servi.
            $anciennes .= sprintf('<article class="previous">%s</article>', representation($thumbnails, $root, $subject, $spread, $old));
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
            '          <article class="variant" data-state="%s">%s'
            // LE LIBELLÉ FRANÇAIS D'ABORD, LA RÉFÉRENCE TECHNIQUE ENSUITE ET EN PETIT : la carte disait « orientation-south_action-idle_shape-e_frame-01 » et rien d'autre, ce qui n'apprend
            // rien à qui regarde une image (opérateur, 2026-08-07). Le libellé vient du référentiel, jamais composé ici — une page qui compose du vocabulaire en invente.
            . '<p class="variant-name">%s%s</p>%s%s'
            // RIEN NE SE JUGE SUR UNE IMAGE QUI N'EXISTE PAS (opérateur, 2026-08-07) : un variant à produire n'offre ni verdict, ni commentaire, ni comparaison — valider une image absente ne
            // veut rien dire, et la case « Comparer » proposait de la mettre en regard d'une autre. La carte dit ce qui reste dû, et c'est tout ce qu'elle a à dire.
            . '%s</article>' . "\n",
            escape(variantState($inventory, $variant)),
            // COMPARER N'APPARAÎT QUE S'IL Y A DE QUOI COMPARER : un sujet à variant unique n'offre pas une case qui ne peut rien faire, et un variant qui n'a pas d'image non plus.
            count($subject['variants']) > 1 && $current
                ? sprintf('<label class="variant-pick"><input type="checkbox" class="compare" data-ref="%s"> Comparer</label>', escape($ref))
                : '',
            // LE VARIANT PRINCIPAL SE VOIT (opérateur, 2026-08-07) : le constructeur d'origine distinguait la vue principale, la reprise l'avait perdue, et une planche de quinze formes où rien
            // ne dit laquelle fait référence oblige à ouvrir le référentiel pour le savoir. L'information y est déjà, chaque sujet portant un variant marqué principal.
            escape($variant['label'] ?? 'Vue principale'),
            ($variant['main'] ?? false) ? '<span class="variant-main" title="Le variant de référence du sujet">principal</span>' : '',
            $rendered,
            $anciennes ? '<details class="fold"><summary>' . count($previous) . ' version' . (count($previous) > 1 ? 's' : '')
                . ' antérieure' . (count($previous) > 1 ? 's' : '') . '</summary><div class="previous-list">' . $anciennes . '</div></details>' : '',
            $review
        );
    }

    return sprintf(
        "      <div class=\"fsp\" id=\"fsp-%s\" hidden>\n        <div class=\"fsp-bar\"><p class=\"fsp-title\">%s <span class=\"slug\">%s</span></p>"
        . "<button type=\"button\" class=\"fsp-close\" aria-label=\"Fermer\">✕</button></div>\n"
        . "        <div class=\"fsp-body\">\n          <div class=\"variants\">\n"
        . "            <button type=\"button\" class=\"quit-comparison\">Quitter la comparaison</button>\n%s          </div>\n        </div>\n      </div>\n",
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
    // THE THREE ACTS CARRY THE REFERENTIAL'S OWN WORDS, AND THAT IS THE WHOLE POINT: approved, rework and discarded are the values `verdict` takes in the data, so
    // what the page records reads straight against it, with no lookup table to keep in step. The displayed labels stay French.
    foreach (['approved' => 'Valider', 'rework' => 'À reprendre', 'discarded' => 'Écarter'] as $key => $label) {
        $markup .= sprintf('<label class="act act--%s"><input type="checkbox" data-id="%s" data-act="%s"><span>%s</span></label>',
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
</style>
<!-- LE STYLE ET LE SCRIPT DE CETTE PAGE VIVENT DANS LEURS PROPRES FICHIERS (opérateur, 2026-08-09). Ce qui reste ici est ce qui ne peut pas en sortir : les
     variables du thème, les modules injectés, et la valeur que le filtre compare.
     CHEMIN RELATIF, ET C'EST MESURÉ : la page construite s'ouvre aussi comme un simple fichier, et un chemin absolu n'y résout pas — la sonde a montré une page
     entièrement muette. Les trois fichiers vivent dans le même dossier, donc le nom suffit, servi comme ouvert à la main. -->
<link rel="stylesheet" href="/review-server/suivi-sprites/page.css">
<style>
{$reloadStyles}
</style>

<div class="wrap">
  <p class="overline">GateBeast — revue</p>
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
    <p class="drawer-path" id="drawer-path"></p>
    <div class="fsp-body"><pre id="drawer-body"></pre></div>
  </aside>

  <p class="lede">Une vignette par sujet. Un clic ouvre le sujet en plein écran, avec ses variants, leurs versions, leurs mesures, la consigne qui les a produits et les actions — toutes
  offertes, toujours. Cochez « Comparer » sur plusieurs variants pour ne garder qu'eux, côte à côte, à quarante-huit pixels par case.</p>

  <p class="production"><span class="production-label">État de la production</span> {$production}</p>
  <div class="filters" role="group" aria-labelledby="filter-label">
    <p class="filter-label" id="filter-label">N'afficher que</p>
{$filters}</div>
  <p class="filter-state" id="filter-state" role="status" aria-live="polite"></p>

{$sections}
{$outsideModel}
</div>
{$reloadMarkup}

{$popins}

{$notesScript}

<script>
/* THE VALUES THE SCRIPT CANNOT CARRY: the state words, their labels and the order that ranks them. They come from the referential, hence from the template — a
   static file cannot hold them. Declared here, before the script, and read there: otherwise the script would retype them, and two spellings of the same state
   would never meet. THE ORDER IS THE ONE IN subjectState(), in a single place: what is owed comes before what is finished. */
window.GATEBEAST_STATE_ALL = '{$stateAll}';
window.GATEBEAST_STATE_LABELS = {$stateLabels};
window.GATEBEAST_STATE_OWED = {$stateOwed};
window.GATEBEAST_STATE_VALIDATED = '{$stateValidated}';
window.GATEBEAST_STATE_TO_JUDGE = '{$stateToJudge}';
</script>
<script src="/review-server/suivi-sprites/page.js"></script>
{$reloadScript}
HTML;

// LES ORPHELINS : toute image présente sur le disque que l'inventaire ne réclame pas. Une image qui existe sans être inscrite n'existe pour personne — elle
// n'apparaît nulle part, personne ne peut la juger, et elle se refait. La page les montre plutôt que de laisser croire que tout est rangé.
// BOTH DIRECTORIES, AS THE ORIGINAL BUILDER DID: « présents sur le disque, sous assets/poc/ ou assets/cutout/ ». The rewrite swept the deliverables only, so a
// MASTER that nothing claims — an abandoned shape, a trial plate — appeared nowhere, while that is exactly the kind of image one opens this section to find. A
// representation claims both of the files it names, its cutout and its master.
$claimed = [];
foreach ($inventory->subjects() as $subject) {
    foreach ($subject['variants'] as $variant) {
        foreach ($variant['representations'] ?? [] as $representation) {
            $claimed[$representation['path']] = true;
            if (isset($representation['master'])) {
                $claimed[$representation['master']] = true;
            }
        }
    }
}
$orphans = [];
foreach ([DELIVERABLE_DIRECTORY, MASTER_DIRECTORY] as $family) {
    $base = $root . '/assets/' . $family;
    if (!is_dir($base)) {
        throw new RuntimeException("FAULT le répertoire d'images « {$base} » n'existe pas.");
    }
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($base)) as $file) {
        if ($file->isFile() && strtolower($file->getExtension()) === 'png') {
            $relative = $family . '/' . substr($file->getPathname(), strlen($base . '/'));
            if (!isset($claimed[$relative])) {
                $orphans[] = $relative;
            }
        }
    }
}
sort($orphans);
// AN ORPHAN IS SHOWN, NOT NAMED (operator, 2026-08-08: "it must go back to the old display where the images could be seen, see the py version"). A file name says an image exists and nothing about
// what it is: deciding whether an unclaimed image is a leftover, a probe or a sprite whose record was lost takes one look at it. Naming it forces the operator to open it by hand, one by one.
$orphanCards = '';
foreach ($orphans as $orphan) {
    $shot = $thumbnails->shrink($orphan, ORPHAN_WIDTH);
    // MASTER OR DELIVERABLE, SAID ON THE CARD — the original builder carried it, and without it two images of the same subject look alike enough that one cannot
    // tell which is the master out of the generator and which is the delivered cutout. The information is already in the path; it is read, never asked for.
    $kind = str_starts_with($orphan, MASTER_DIRECTORY . '/') ? 'Brute (poc)' : 'Livrable';
    $orphanCards .= sprintf('<figure class="orphan">%s<figcaption><span class="orphan-kind">%s</span>%s</figcaption></figure>',
        $shot ? sprintf('<img src="%s" width="%d" height="%d" alt="" loading="lazy">', $shot[0], $shot[1], $shot[2]) : '<p class="to-produce">Image illisible</p>',
        escape($kind), escape($orphan));
}
$outsideModel = $orphans
    ? '  <section class="type"><header class="type-head"><h2>Hors modèle <span class="slug">image(s) livrée(s) qu\'aucun variant ne réclame</span></h2>'
      . '<span class="type-count">' . count($orphans) . ' image' . (count($orphans) > 1 ? 's' : '') . '</span></header>'
      . '<div class="orphans">' . $orphanCards . '</div></section>'
    : '  <section class="type"><header class="type-head"><h2>Hors modèle</h2><span class="type-count">rien</span></header>'
      . '<p class="lede">Chaque image livrée est réclamée par un variant.</p></section>';

// THE SENTENCE THE ORIGINAL BUILDER PUT UNDER ITS TITLE, in its own words: how many images the model expects, over how many subjects, and how many are drawn.
// The filters tell the state of the subjects; this one tells how far the production has come, which nothing else says.
$production = sprintf('%d images attendues, réparties sur %d sujets — %d produites', $expected, count($inventory->subjects()), $produced_total);

$filters = '';
// THE FILTERS CARRY THE SAME STATES AS THE TILES, in the same order and in the same words: "to judge" replaced "produced", which did not say what was left to do.
// A produced subject whose images nobody has judged is exactly what one opens this page looking for.
foreach ([STATE_ALL => 'Tout'] + STATE_LABELS as $key => $label) {
    $filters .= sprintf('<button type="button" class="filter" data-filter="%s" aria-pressed="%s">%s%s</button>',
        $key, $key === STATE_ALL ? 'true' : 'false', escape($label), $key === STATE_ALL ? '' : ' <span>' . ($compte[$key] ?? 0) . '</span>');
}

$page = strtr($page, [
    // THE PAGE GOES BACK TO « ENCRE », THE THEME IT WAS MIGRATED WITH, and the history says so rather than my memory (operator, 2026-08-11: « il y avait un
    // thème avant celui là, je veux le récupérer !!! »). Read off the repository: on 2026-08-06 the page moved to PHP with `Theme::css('encre')` — a near-black
    // slightly blue ground, amber accent. On 2026-08-08 a `origine` theme was written from the PYTHON builder's DARK block, a very dark green, and the page was
    // switched to it. That green is what the operator has been looking at and refusing. `origine.css` stays on disk, unused: nothing is thrown away here.
    '{$theme}' => $theme->css('graphite'),
    '{$favicon}' => $favicon->tag(),
    '{$reloadStyles}' => $reload->styles(),
    '{$reloadMarkup}' => $reload->markup(),
    '{$reloadScript}' => $reload->script('/sprites'),
    // THE SAME MODULE AS THE CAMPAGNE PAGE, AND THAT IS THE WHOLE POINT: this page's verdicts reach the repository through the road that already exists, rather
    // than a second mechanism to keep in step beside it. The route names the file — review-server/notes/sprites.json.
    '{$notesScript}' => Notes::get()->script('/sprites'),
    // THE STATE THAT MEANS "NO FILTER" IS WRITTEN ONCE, in the constant, and handed to the script rather than retyped in it: a filter button and the code that
    // reads it must agree on the word, and two spellings of it would silently show nothing.
    '{$stateAll}' => STATE_ALL,
    // THE SAME WORDS AND THE SAME ORDER AS subjectState(), HANDED OVER RATHER THAN RETYPED: the page recomputes a subject's state as soon as a verdict is ticked,
    // and it must decide it exactly as the build did — one image to rework outweighs everything, and « validated » takes every variant.
    '{$stateLabels}' => json_encode(STATE_LABELS, JSON_UNESCAPED_UNICODE),
    '{$stateOwed}' => json_encode([STATE_TO_REWORK, STATE_DISMISSED, STATE_TO_PRODUCE]),
    '{$stateValidated}' => STATE_VALIDATED,
    '{$stateToJudge}' => STATE_TO_JUDGE,
    '{$filters}' => $filters,
    '{$production}' => $production,
    '{$outsideModel}' => $outsideModel,
    '{$sections}' => $sections,
    '{$popins}' => $popins,
]);

file_put_contents($outputPath, $page);
printf("%s — %d sujets, %.1f ko%s\n", $outputPath, count($inventory->subjects()), strlen($page) / 1024,
    $missing ? ', ' . count($missing) . ' image(s) illisible(s)' : '');
if ($inventory->sansLibelle) {
    fwrite(STDERR, 'SANS LIBELLÉ : ' . implode(', ', $inventory->sansLibelle) . "\n");
}

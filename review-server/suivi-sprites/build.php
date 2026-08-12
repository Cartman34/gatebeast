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
// The rune service is still required although the page draws no rune for now (see runeMark): the drawing comes back by calling it again, and dropping the
// require with the call would turn a one-line return into a hunt through the history.
require_once $root . '/review-server/lib/Rune.php';
bootBuild();

const SCREEN_PIXELS_PER_TILE = 24;   // what a tile measures on screen — the project's own value, held by scripts/tile_scale.py
const COMPARE_PIXELS_PER_TILE = 48;  // what a tile measures inside the full-screen panel, where images are judged and compared (operator, 2026-08-06)
// ORPHAN_WIDTH is a width in pixels, not a count of tiles: an unclaimed image has no variant, so nothing declares how many tiles it covers. Wide enough to recognize the subject at a glance.
const ORPHAN_WIDTH = 160;
// THE TWO FAMILIES OF IMAGES UNDER assets/: the master as it comes out of the generator, and the cutout delivered to the game. Both words are those of the paths
// the referential records — `master` and `path` — and they were typed out wherever the page swept the disk.
const MASTER_DIRECTORY = 'poc';
const DELIVERABLE_DIRECTORY = 'cutout';
// How much a ground length running away from the eye is foreshortened under the 60-degree camera — the sine of the angle. Written here until the page can ask
// the service that holds the scale, which is in Python: this is the ONE model value this page copies, and it goes as soon as the two sides can talk.
const GROUND_DEPTH_FACTOR = 0.8660;

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$inventory = new Inventory($root);
$thumbnails = new Thumbnail($root);
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();

// The missing images below are NOT faults: they are reported and shown as holes. A hole one can see is what tells the operator what is still owed.

const TYPE_LABELS = [
    // THE KEY IS THE REFERENTIAL'S OWN VALUE, English since 2026-08-12; the label stays French, which is what the rule reserves for what is displayed.
    'ground' => 'Sol', 'path' => 'Chemin', 'stream' => "Cours d'eau", 'fence' => 'Clôture et mur',
    'tree' => 'Arbre', 'grove' => "Bosquet d'arbres", 'grass' => 'Herbe',
    'building' => 'Bâtiment', 'human' => 'Humain', 'creature' => 'Créature', 'bridge' => 'Pont',
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

// THE VERDICTS THE REFERENTIAL STORES, English since 2026-08-12, and the state each one means. They are now the same three words the page writes into the
// remarks: two vocabularies for one verdict meant a translation to keep in step on both sides — and it was already half done, the file carrying both `validee`
// and `discarded`.
const VERDICT_STATES = [
    'approved' => STATE_VALIDATED,
    'rework' => STATE_TO_REWORK,
    'discarded' => STATE_DISMISSED,
];

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES);
}

/** The first letter capitalised, and only that one — the project's display rule. */
function capitalize(string $text): string
{
    return mb_strtoupper(mb_substr($text, 0, 1)) . mb_substr($text, 1);
}

/** A representation's image, shrunk to the width asked for, or null when the file is missing — a hole is shown, never hidden. */
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
 * THE REFERENTIAL SPELLS ITS VERDICTS IN ENGLISH SINCE 2026-08-12, and this is the one place that maps them onto the page's states. It used to hold French
 * values and translate them here; the migration is done, so what is left is a mapping between two English vocabularies — a verdict on an image, a state on a
 * variant — and they stay distinct because they are not the same thing.
 */
function variantState(Inventory $inventory, array $variant): string
{
    $current = $inventory->currentRepresentation($variant);
    if (!$current) {
        return STATE_TO_PRODUCE;
    }

    return VERDICT_STATES[$current['verdict'] ?? ''] ?? STATE_TO_JUDGE;
}

/**
 * An image's measurements, spelled out: what the export observed on the delivered file. Nothing is recomputed here — the page shows what is written.
 *
 * ALL OF THEM, NOT A SELECTION: what the subject declares — footprint, cover, height — and what the export measured on the file. Picking three figures to show
 * decides for the operator which one matters, and those are exactly what he reaches for when an image looks wrong to him.
 */
function measurements(array $representation, array $subject): string
{
    $lignes = [];
    $footprint = $subject['footprint'];
    $cover = $subject['cover'] ?? null;
    // ONE MEASUREMENT PER LINE, and the footprint, the cover and the height first: they are the three thresholds an image is judged against. Grouped on one
    // line they read as a sentence and had to be hunted for in the middle of it.
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

/**
 * The frozen prompt kept beside the master, and the production report when there is one.
 *
 * THE THREE GO TOGETHER AND NOWHERE ELSE: the image says what came out, the prompt what was asked, the report how it was obtained. Judging on one of the three
 * alone is what sent the search after the wrong cause more than once. When they are absent they say nothing: the project's first images predate the rule that
 * freezes a prompt beside its master.
 */
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
    // A TEXT IS READ LARGE AND COPIED: folded into a card two hundred and sixty pixels wide it is of no use. The button opens it where it takes the whole width
    // and can be selected in one click.
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

/**
 * The grid laid over a sprite: its ground footprint, its cover when it overhangs, and the two axes.
 *
 * EVERYTHING IS SAID IN TILES AND RENDERED IN PERCENTAGES of the thumbnail, never in pixels: the thumbnail changes size with the subject's footprint and with the
 * magnification, while a tile stays a tile. Writing pixels here would make them drift from the image the moment a size changes.
 *
 * THE IMAGE IS LAID OUT ON THE COVER'S WIDTH, not the footprint's — that is what the thumbnail factory does. The ground footprint is therefore drawn as a PART of
 * that width, centred, and not as the whole thumbnail: which is exactly what one wants to see of an oak whose crown overhangs its foot.
 */
function grid(array $subject, array $spread, int $width, int $height): string
{
    $footprint = $subject['footprint'];
    $covers = ($spread['columns'] !== $footprint['columns']) || ($spread['rows'] !== $footprint['rows']);
    // The tile, as a percentage of the thumbnail: the width carries the cover's columns, and the height follows the same scale since the image is never distorted.
    $tile = 100 / $spread['columns'];
    // A TILE OF DEPTH IS NOT PROJECTED LIKE A TILE OF WIDTH, and forgetting it dropped the footprint frame far below the subject's ground — two tiles of emptiness
    // in front of the building, which the operator spotted. Under the world's camera a ground length running away is seen foreshortened; the service that holds
    // the scale carries that factor, and it is asked for rather than retyped here.
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
/**
 * The rune laid over a creature's representation — NOTHING FOR NOW, and this function is what says so.
 *
 * NO RUNE IS DRAWN ON THIS PAGE (operator, 2026-08-12: « pour l'instant, ne mets pas les runes sur les générations », then « SP-001 vue principale a une rune
 * mal posée, faut la faire enlever », then « mais les autres variants aussi ont une rune mal posée en fait »). What was wrong was the ANCHOR, never the drawing:
 * one point was placed on the front view and the same value written onto the turned views, where it lands nowhere. A mark shown at a spot nobody chose is worse
 * than no mark — it reads as a decision. The anchors went with it, so `python3 scripts/set-rune-anchor.py --list` now tells the truth: these representations
 * await a point.
 *
 * NOTHING ELSE IS REMOVED, and the drawing comes back by calling Rune again here: the shapes, the colours, the constant size and the placing tool are untouched,
 * and `php local/scripts/see-placed-rune.php` still draws a placed rune outside this page. What this waits on is S53 rune-creature. The mechanism itself is in
 * the history — `git show HEAD:review-server/suivi-sprites/build.php` — and is taken back from there rather than rewritten from memory.
 */
function runeMark(string $code, array $subject, array $representation, int $shownWidth): string
{
    return '';
}

/**
 * The notes of ONE version: its three acts and its comment, filed under the path of its own image.
 *
 * FACING THE VERSION THEY JUDGE, NO LONGER ON THE VARIANT (operator, 2026-08-12: « les notes de chaque version doivent être en face de la version »). A remark
 * has always been filed under the image's path — that is what stops one image's verdict from judging the next — but only the current version showed any: an
 * earlier one kept its own in the repository with nothing on screen to display it.
 *
 * THE ENTRY ZONE STAYS FOLDED AND THE « + » BUTTON OPENS IT (operator, 2026-08-06 then 2026-08-07): unfolded by default it takes as much height as the three
 * acts together, for a field filled one time in ten.
 */
function notes(string $key, string $comment): string
{
    return sprintf(
        '<div class="acts" data-id="%s">%s'
        . '<button type="button" class="open-comment" data-open="%s" aria-expanded="false" aria-label="Commentaire" title="Commentaire">+</button></div>'
        . '<div class="comment-zone" data-more="%s" hidden>'
        . '<textarea class="comment" data-id="%s" rows="2" placeholder="Ce qui devrait changer.">%s</textarea>'
        . '<button type="button" class="clear-comment" data-id="%s" title="Effacer le commentaire" aria-label="Effacer le commentaire" hidden>×</button></div>',
        escape($key), actions($key), escape($key), escape($key), escape($key), escape($comment), escape($key)
    );
}

function representation(Thumbnail $thumbnails, string $root, string $code, array $subject, array $spread, array $representation): string
{
    // THE SCALE IS FIXED AND THE SAME FOR EVERY SUBJECT: forty-eight pixels per tile in the panel, a tile staying a tile from one subject to the next. A large oak
    // therefore takes four times the width of a fence, which is the truth of the world; thumbnails all of one width let you neither compare two subjects nor see
    // that a sprite overflows — which is precisely what the footprint and the cover are there to show.
    $shot = image($thumbnails, $representation, COMPARE_PIXELS_PER_TILE * $spread['columns']);
    // THE GRID IS LAID ON THE IMAGE, AT THE SCALE IT IS SHOWN AT (operator, 2026-08-07): without it a sprite is judged in a vacuum — one sees neither what it
    // occupies on the ground, nor what it overhangs, nor where its axes are. The three read in different colours, and the values are the referential's own,
    // never recomputed here.
    // THE IMAGE AND ITS GRID ARE WRAPPED TOGETHER: without that wrapper hugging the image, the grid measures itself against the whole card and its footprint
    // frame stretches across the full width, announcing a sprite far wider than it is.
    // A CREATURE IS CLICKED TO PLACE ITS RUNE, AND ONLY A CREATURE: it is the one type that carries one. The image states its path and its scale, because the
    // anchor is declared in the pixels of the DELIVERED image while the page shows it at another width — without the ratio, the click would land elsewhere.
    $anchorable = '';
    if (($subject['type'] ?? '') === 'creature' && $shot) {
        $delivered = $representation['measures']['delivered_px'] ?? null;
        if ($delivered) {
            $anchorable = sprintf(' data-anchor-for="%s" data-delivered="%d" title="Cliquez pour poser la rune"', escape($representation['path']), $delivered['width']);
        }
    }
    $picture = $shot
        ? sprintf('<span class="picture"%s><img src="%s" width="%d" height="%d" alt="">%s%s</span>',
            $anchorable, $shot[0], $shot[1], $shot[2], grid($subject, $spread, $shot[1], $shot[2]), runeMark($code, $subject, $representation, $shot[1]))
        : '<p class="to-produce">Image illisible</p>';
    $state = VERDICT_STATES[$representation['verdict'] ?? ''] ?? null;

    // A VERSION'S CARD KEEPS ONLY WHAT IS NEEDED TO CHOOSE IT, ALL THE REST IS IN THE DRAWER (operator, 2026-08-12: « dans la liste des versions, on voit donc
    // bien moins de détails dans le variant, tout est dans le panel à droite »). Its name, its date, its image, its verdict — and the button that opens the
    // drawer. The measurements, the prompt and the report no longer clutter the list: they are asked for on the version one wants to look at.
    $key = $representation['path'] ?? '';

    return sprintf('%s<div class="variant-image">%s</div>%s%s'
        . '<button type="button" class="open-version" data-for="%s">Voir cette version</button>'
        . '<div class="version-full" data-version="%s" hidden>%s%s</div>',
        version($root, $representation),
        $picture,
        // THE VERDICT IS SHOWN THROUGH THE SAME VOCABULARY AS EVERYTHING ELSE: the stored French value is translated once, and the page speaks one language to itself.
        $state ? sprintf('<p class="verdict verdict--%s">%s</p>', escape($state), escape(STATE_LABELS[$state])) : '',
        // THE JUDGEMENT STAYS ON THE GRID, IT IS NOT IN THE DRAWER (operator, 2026-08-12: « ça devait rester sur la grille de variant, faut que je puisse le
        // donner rapidement »). Moved into the drawer, a verdict asked for two more gestures — open, then close — for an image one knows what to think of on
        // sight. It stays filed under the path of ITS image, so every version keeps its own, earlier ones included.
        notes($key, $representation['operator_comment'] ?? ''),
        escape($key), escape($key),
        // THE IMAGE IS NOT COPIED HERE, AND THAT IS A FAULT CAUGHT AT BUILD TIME: written a second time, it took the page from 37 to 71 MB — a thumbnail is a
        // file written out IN FULL inside the page. The drawer picks it up from the card at the moment it opens, so none is ever duplicated.
        measurements($representation, $subject),
        frozenPrompt($root, $representation)
    );
}

/** A subject's full-screen panel: its variants, each one's current version, the earlier ones, the measurements, the prompt, the verdict and the actions. */
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
            ? representation($thumbnails, $root, $code, $subject, $spread, $current)
            : '<div class="variant-image"><p class="to-produce">À produire</p></div>';
        $comment = $current['operator_comment'] ?? '';
        $previous = $inventory->previousRepresentations($variant);
        $identifier = $code . ' ' . $ref;
        $anciennes = '';
        foreach ($previous as $old) {
            // THE SAME PRESENTATION AS THE CURRENT ONE, NO SPECIAL CASE (operator, 2026-08-07): its image at the same scale with its footprint grid, its file
            // name, its date, its verdict, its measurements and its prompt. It is by holding it against the current one that one decides whether the retake served.
            // AN EARLIER VERSION CARRIES ITS PATH IN THE MARKUP, and that is what makes its comments findable: a remark is filed under the path of the image it
            // judges, so without that path the page has no way of knowing a text exists on an older one.
            $anciennes .= sprintf('<article class="previous" data-version="%s">%s</article>',
                escape($old['path'] ?? ''), representation($thumbnails, $root, $code, $subject, $spread, $old));
        }
        // THE JUDGEMENT BLOCK LEFT THE VARIANT FOR THE VERSION (operator, 2026-08-12): every version now carries its own notes under its own image, earlier ones
        // included, which showed none. The variant keeps none, and the line announcing « an older version carries a comment » has lost its reason — the older one
        // shows it itself, right there. Checked before removal, as the task asked.
        $review = '';
        $blocks .= sprintf(
            '          <article class="variant" data-state="%s">%s'
            // THE FRENCH LABEL FIRST, THE TECHNICAL REF AFTER AND SMALL: the card used to read « orientation-south_action-idle_shape-e_frame-01 » and nothing
            // else, which teaches nothing to whoever is looking at an image (operator, 2026-08-07). The label comes from the referential, never composed here —
            // a page that composes vocabulary invents it.
            . '<p class="variant-name">%s%s</p>%s%s'
            // NOTHING IS JUDGED ON AN IMAGE THAT DOES NOT EXIST (operator, 2026-08-07): a variant still to produce offers no verdict, no comment and no
            // comparison — validating an absent image means nothing. The card says what is still owed, and that is all it has to say.
            . '%s</article>' . "\n",
            escape(variantState($inventory, $variant)),
            // THE VARIANT'S HEAD LINE: « Comparer » on the left, ITS STATE ON THE RIGHT (operator, 2026-08-12: « à droite je veux qu'on voie le statut actuel du
            // variant : à juger, à reprendre, validé… »). A variant's state could only be read on the subject tile, which sums up the whole subject: faced with a
            // board of fifteen variants, nothing said which one was judged. The word is the model's own, taken from the same table as everywhere else, and the
            // page rewrites it at every verdict — see refreshStates().
            // COMPARE ONLY APPEARS WHEN THERE IS SOMETHING TO COMPARE: a subject with a single variant is not offered a box that can do nothing, and neither is
            // a variant with no image.
            sprintf('<p class="variant-head">%s<span class="variant-state">%s</span></p>',
                count($subject['variants']) > 1 && $current
                    ? sprintf('<label class="variant-pick"><input type="checkbox" class="compare" data-ref="%s"> Comparer</label>', escape($ref))
                    : '<span class="variant-pick"></span>',
                escape(STATE_LABELS[variantState($inventory, $variant)] ?? variantState($inventory, $variant))),
            // THE MAIN VARIANT IS VISIBLE (operator, 2026-08-07): the original builder set the main view apart, the rewrite had lost it, and a board of fifteen
            // shapes where nothing says which is the reference forces one to open the referential to find out. The information is already there, every subject
            // carrying one variant marked as the main one.
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
 * A REVIEW BEARS ON AN IMAGE, NOT ON A VARIANT: the filing key is the path of the version displayed. A regenerated image is a new image, and the previous one's
 * verdict does not judge it — yet it stayed stuck to the variant, so a regrown grove came back « to rework » carrying its ancestor's comment (operator,
 * 2026-08-06). The label, on the other hand, stays the variant's: that is what is read in a report.
 */
function reviewKey(string $identifier, ?array $current): string
{
    return $current['path'] ?? $identifier;
}

function actions(string $identifier): string
{
    // BUTTONS, NOT GREY CHECKBOXES. An action is clicked and lights up; a bare checkbox in the middle of a card reads like an administrative form, and the
    // operator said so the moment one appeared. The box stays underneath — it is what carries the state — but it is hidden, and the label becomes the button.
    $markup = '';
    // THE THREE ACTS CARRY THE REFERENTIAL'S OWN WORDS, AND THAT IS THE WHOLE POINT: approved, rework and discarded are the values `verdict` takes in the data, so
    // what the page records reads straight against it, with no lookup table to keep in step. The displayed labels stay French.
    foreach (['approved' => 'Valider', 'rework' => 'À reprendre', 'discarded' => 'Écarter'] as $key => $label) {
        $markup .= sprintf('<label class="act act--%s"><input type="checkbox" data-id="%s" data-act="%s"><span>%s</span></label>',
            $key, escape($identifier), $key, escape($label));
    }

    return $markup;
}

// The template does NOT interpolate by itself: its marks are replaced just below, in one gesture. Otherwise PHP would substitute variables that do not exist yet
// and leave silent holes in their place — which happened, and the page came out without a single style.
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

// THE ORPHANS: every image on disk that the inventory does not claim. An image that exists without being inscribed exists for nobody — it appears nowhere, no
// one can judge it, and it gets drawn again. The page shows them rather than let one believe everything is filed.
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

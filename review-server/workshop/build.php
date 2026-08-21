<?php
/**
 * Usage: php review-server/workshop/build.php [output.html] — builds the page that shows the consigne trials, served at /workshop.
 *        php review-server/workshop/build.php -h|--help — this text, and nothing is built.
 *
 * Intention: A GENERATION PRODUCES FOUR THINGS THAT LIVED IN FOUR PLACES, so nobody could tie a defect in the image back to the sentence that caused it. The
 * consigne sent, its cut-up by level, the prompt the agent passed on to its OWN image model, and the image itself are shown here side by side, for one trial at
 * a time — with the critiques anchored on the very sentences they put in question.
 *
 * WHAT IT READS AND NEVER RECOMPUTES: the cut-up and its fingerprint are read by `PromptParts`, the anchored critiques by `Critiques`. This page HAD its own
 * copy of the split, and it had already drifted: it checked a `sha256` key the chain never wrote, so the fingerprint was NEVER verified and sentences could be
 * attributed to the wrong level in silence. That is the duplication this repository pays for most often, and it is why nothing is recomputed here.
 *
 * AND IT NO LONGER COMPARES OUR TEXT TO THE TRANSMITTED ONE SENTENCE BY SENTENCE (operator, 2026-08-17): the agent rewrites rather than relays, so looking for
 * our sentences word for word in what it sent could only ever report « lost ». The transmitted consigne is still shown, whole, beside the version that produced
 * it — reading it is what tells whether a clause survived, and no count can stand in for that.
 *
 * A TRIAL IS NOT A DELIVERABLE: it lives under var/generations/trials/, is not versioned, enters no referential, appears on no sprite page, and burns no version
 * of a subject. It therefore vanishes on a cleanup, and this page says so rather than letting an absent trial read as one that never existed.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/PromptParts.php';
require_once $root . '/review-server/lib/Critiques.php';
require_once $root . '/review-server/lib/WordDiff.php';
require_once $root . '/review-server/lib/Inventory.php';
require_once $root . '/review-server/lib/FootprintGrid.php';
require_once $root . '/review-server/lib/SpriteMeasures.php';
require_once $root . '/review-server/lib/Consignes.php';
require_once $root . '/review-server/lib/TransmittedNumbers.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();
$parts = PromptParts::get();
$critiques = Critiques::get();
$inventory = new Inventory($root);

/** The projected tile, in pixels of the delivered image — the published ratio, 96 across by 84 deep, and never the sine of the camera angle. */
const TX_PIXELS = 96;
const TY_PIXELS = 84;

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * The consignes the workshop works on, one directory each, in subject order.
 *
 * A CONSIGNE IS NAMED BY ITS SUBJECT, NEVER BY A DATE (`S99 consigne-structuree`). The home used to be `var/generations/trials/2026-08-13-BT-001/`, which said
 * WHEN a generation happened and nothing about what is being worked on — so writing a consigne differently raised the false question « faut-il un dossier
 * neuf ? ». The subject is the work; the date belongs to a version, which records its own.
 *
 * AND THE WHOLE CHAIN LIVES IN ONE FOLDER, ROOT INCLUDED. It used to straddle two, of which one was disposable: a chain whose v1 can vanish leaves every later
 * diff without an origin. The single foyer is declared by `Consignes`, and by it alone — this page is one of its four readers.
 */
function consignes(): array
{
    $found = [];
    foreach (Consignes::get()->subjects() as $subject) {
        $found[] = [
            'name' => $subject,
            'code' => $subject,
            'versions' => versionsOf($subject),
        ];
    }

    return $found;
}

/**
 * The versions of one consigne, from the oldest to the newest — the last of the list is the one that holds authority.
 *
 * WE NO LONGER WORK BY REGENERATING, WE WORK BY MODIFYING WHAT WAS GENERATED (operator, 2026-08-13: « on ne travaille plus en regénérant, on travaille en
 * modifiant ce qui a été généré ») : a clean consigne is first written end to end, and only what works then goes back into the code. Each retouch therefore
 * produces a whole VERSION, `v2.txt`, `v3.txt`, and **the diff runs from one version to the next**.
 *
 * A FILE NAME SAYS WHOSE IT IS AND WHAT IT IS: `<SUJET>.v<N>.<quoi>.<ext>` (operator, 2026-08-17: « je préfère que le nom des fichiers soit préfixés par le
 * sujet et qu'il porte toujours ce que c'est »). Torn from its directory, `v3.png` says nothing, and an extension alone does not tell the generated image from a
 * probe shot nor the prompt from any other text. The « what » is English like every file name here — `prompt`, `image`, `edits`, `generation`.
 *
 * A VERSION CARRIES ITS OWN IMAGE, AND THAT IS WHAT MAKES IT TESTABLE (operator, 2026-08-17: « il faut que le système te permette d'avoir un suivi sur ces
 * tests »). Absent, the version has not been generated, and the page says so instead of showing another version's image as though this text had produced it.
 */
function versionsOf(string $subject): array
{
    $consignes = Consignes::get();
    $versions = [];
    foreach ($consignes->ranksOf($subject) as $rank) {
        $image = $consignes->file($subject, $rank, 'image');
        // LA CONSIGNE TRANSMISE APPARTIENT À UNE VERSION, comme son image et sa session : c'est le texte que l'agent a envoyé à son propre modèle EN LISANT
        // CETTE VERSION-LÀ. La chercher au rang 1 pour tout le monde — ce que faisait ce fichier — la montrait pour une version et la cachait pour les autres.
        $transmitted = $consignes->file($subject, $rank, 'transmitted');
        $versions[] = ['label' => "v$rank", 'path' => $consignes->file($subject, $rank, 'prompt'),
            'image' => is_file($image) ? $image : null,
            'transmitted' => is_file($transmitted) ? $transmitted : null,
            'meta' => metaOf($consignes->file($subject, $rank, 'generation'))];
    }

    return $versions;
}

/**
 * What the reader must be told about the ACTIVE version before reading a single line of it: which one it is, and whether the image beside it came from it.
 *
 * A VERSION WRITTEN AFTER THE GENERATION HAS NEVER BEEN TESTED, AND NOTHING SAID SO (operator, 2026-08-17: « on avait fait des corrections mais on ne l'avait pas
 * testé. il faut que le système te permette d'avoir un suivi sur ces tests »). The panel puts the image and the active text side by side, which reads as "this
 * text produced this image" — true for v1 only. For every later version it is false, and it is false in the silent way this repository pays the most for: the
 * page looks right. The full per-correction tracking is its own point, `suivi-tests-consigne`; what cannot wait is the page ceasing to imply a test that never
 * ran.
 */
/**
 * The trial's image, with the tile grid laid over it.
 *
 * A SPRITE IS ALWAYS SHOWN WITH ITS TILES ON A TOOL, AND NOT ONLY ON THE SPRITES PAGE (operator, 2026-08-17: « on doit voir les cases représentées. ça doit
 * toujours être le cas sur les outils, hors maquette »). Judged without them, an image is judged in a vacuum: nothing says what it covers on the ground, what
 * its volume overhangs, nor where its axes fall — which is exactly what this page exists to tie back to a sentence of the consigne. The mock-up is the one
 * exception, because there the sprite is being looked at IN a scene rather than measured.
 *
 * NOTHING IS REDRAWN HERE: `FootprintGrid` holds the paving, the markup and the reserve for every page that shows a sprite, and this one calls it like the
 * sprites page does.
 *
 * AND IT SAYS WHAT IT CANNOT DO RATHER THAN DRAWING A GRID IT CANNOT JUSTIFY: the paving is measured against the subject's footprint AS THE REFERENTIAL
 * DECLARES IT. A trial whose code is not declared there gets its picture and a sentence naming what is missing — a footprint is never guessed from the image,
 * which would show a grid that agrees with the drawing by construction and could therefore never contradict it.
 */
function pictureMarkup(string $root, Inventory $inventory, array $trial, ?string $path): string
{
    if ($path === null) {
        return '<p class="missing">Pas d\'image : cette version-là n\'a pas été générée.</p>';
    }
    $source = '/' . substr($path, strlen($root) + 1);
    $subject = $trial['code'] === null ? null : $inventory->subject($trial['code']);
    if ($subject === null) {
        return sprintf('<img src="%s" alt=""><p class="missing">Pas de grille de cases : le sujet « %s » n\'est pas déclaré au référentiel,'
            . ' et une emprise ne se devine pas depuis l\'image.</p>', escape($source), escape((string) $trial['code']));
    }
    $size = getimagesize($path);
    if ($size === false) {
        throw new RuntimeException(sprintf('FAULT l\'image « %s » ne se lit pas, et ses dimensions sont nécessaires au pavage.'
            . ' Solution — vérifier le fichier livré par la génération.', $path));
    }
    $grid = FootprintGrid::get();
    $spread = $inventory->spread($subject);
    $tiling = $grid->tiling($trial['code'], $spread, $size[0], $size[1]);

    return sprintf('<span class="picture" style="%s"><img src="%s" width="%d" height="%d" alt="">%s</span>',
        $grid->pictureStyle($tiling), escape($source), $size[0], $size[1], $grid->markup($subject, $spread, $tiling));
}

/**
 * What a version CHANGED, edit by edit, with the reason of each and whether it has been tested.
 *
 * THE STATE PER EDIT IS THE GRAIN THAT DECIDES A REPORT INTO THE CODE (`S98 suivi-tests-consigne`), and it lived in a file nobody opened. A version carries a
 * handful of corrections; some are proven by its image, some are not observable on that essai, and only the proven ones are owed to the code. Shown as one
 * version-wide verdict, they cannot be told apart — and reporting them all is how a correction that never worked ends up in the socle.
 *
 * « NON TESTÉE » IS THE HONEST DEFAULT AND IT STAYS UNTIL A MEASURE SAYS OTHERWISE. « Tenue » is posted on a measure or on the operator's verdict, never on an
 * impression from re-reading the text — an agent judging his own correction by looking at it will find it good every time.
 */
function editsMarkup(array $journal): string
{
    if ($journal['fault'] !== null) {
        return '<p class="missing">' . escape($journal['fault']) . '</p>';
    }
    if ($journal['edits'] === []) {
        return '';
    }
    $states = ['tenue' => 'intact', 'non tenue' => 'lost', 'non testée' => 'unknown'];
    $items = '';
    foreach ($journal['edits'] as $edit) {
        $state = $edit['test'] ?? 'non testée';
        $items .= sprintf('<li><span class="state %s">%s</span> <strong>%s</strong><p class="edit-why">%s</p>%s</li>',
            escape($states[$state] ?? 'unmeasurable'), escape($state), escape($edit['id'] ?? 'sans identifiant'),
            escape($edit['intention'] ?? 'Aucune intention écrite — on ne saura pas pourquoi cette correction a été faite.'),
            isset($edit['observation']) ? '<p class="edit-why">Observé : ' . escape($edit['observation']) . '</p>' : '');
    }
    $note = $journal['note'] === null ? '' : '<p class="edit-note">' . escape($journal['note']) . '</p>';

    return sprintf('<h3 class="transmise">Ce que cette version a changé, et ce qu\'on en sait</h3>%s<ul class="edits">%s</ul>', $note, $items);
}

/**
 * The transmitted text, cut into the PASSES the agent says it sent — one block each, with its own heading.
 *
 * THE AGENT WORKS IN SEVERAL PASSES, AND ONLY ONE OF THEM DRAWS. The `v6` sent two: the one that produced the building, and one that repainted the background
 * magenta for the cutout. Shown as a single block, the second reads as a continuation of the first, and one looks for the drawing clause inside a text that only
 * talks about background colour — which is exactly the confusion that cost three days in August.
 *
 * TWO HEADINGS ARE RECOGNISED, AND NEITHER IS INVENTED HERE. `===== PASSE n =====` is written by `extract-transmitted.php` when the agent emits several marked
 * blocks; « Consigne n — ce qu'elle produisait : » is what the agent writes itself, because the consigne asks it for « une ligne disant ce qu'elle produisait ».
 * Anything else stays one block: a text nobody can cut is shown whole rather than cut at a guess.
 */
function passesOf(string $transmitted): array
{
    $parts = preg_split('/^(===== PASSE \d+ =====|Consigne \d+[^\n]*)$/m', $transmitted, -1, PREG_SPLIT_DELIM_CAPTURE);
    if (count($parts) < 3) {
        return [['title' => null, 'text' => $transmitted]];
    }
    $passes = [];
    // What precedes the first heading belongs to no pass: it is a preamble, and it is shown as such rather than attached to one at random.
    if (trim($parts[0]) !== '') {
        $passes[] = ['title' => null, 'text' => trim($parts[0])];
    }
    for ($rank = 1; $rank < count($parts); $rank += 2) {
        $passes[] = ['title' => trim($parts[$rank]), 'text' => trim($parts[$rank + 1] ?? '')];
    }

    return $passes;
}

/** The transmitted text as one block per pass, each under its heading. */
function passesMarkup(string $transmitted): string
{
    $passes = passesOf($transmitted);
    if (count($passes) === 1 && $passes[0]['title'] === null) {
        return '<pre class="whole">' . escape($passes[0]['text']) . '</pre>';
    }
    $blocks = '';
    foreach ($passes as $pass) {
        $blocks .= $pass['title'] === null ? '' : '<h4 class="passe">' . escape($pass['title']) . '</h4>';
        $blocks .= '<pre class="whole">' . escape($pass['text']) . '</pre>';
    }

    return sprintf('<p class="state">%d passe(s) transmise(s) — une seule d\'entre elles dessine, les autres retouchent.</p>%s',
        count($passes), $blocks);
}

/**
 * What the transmission lost, said above the transmitted text — or that it lost nothing, which is just as much an answer.
 *
 * IT SAYS WHAT IT MEASURES IN THE SAME BREATH: presence of a figure, never respect of a constraint. « Rien de chiffré n'a été perdu » on a version whose image
 * is wrong must not read as « la consigne a été suivie » — the numbers arrived, that is all it can see, and the picture is judged elsewhere.
 */
function lossMarkup(array $verdict): string
{
    if ($verdict['lost'] === []) {
        return sprintf('<p class="state intact">Aucune contrainte chiffrée perdue en chemin — les %d nombres de la consigne sont dans ce texte.'
            . ' Cela dit qu\'ils sont ARRIVÉS, jamais que l\'image les respecte.</p>', $verdict['wanted']);
    }
    $items = '';
    foreach ($verdict['lost'] as $number => $line) {
        $items .= sprintf('<li><strong>%s</strong> — %s</li>', escape((string) $number), escape(mb_strimwidth($line, 0, 150, '…')));
    }

    return sprintf('<p class="state lost">%d contrainte(s) chiffrée(s) perdue(s) en chemin, sur %d : le nombre n\'apparaît nulle part dans ce que'
        . ' l\'agent a envoyé.</p><ul class="lost-numbers">%s</ul>', count($verdict['lost']), $verdict['wanted'], $items);
}

/** What a generation recorded of itself — its session above all. Absent, the version was never generated, or was generated before the record existed. */
function metaOf(string $path): ?array
{
    return is_file($path) ? json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR) : null;
}

/**
 * What is printed UNDER an image: the session that produced it, the date, its measures, and the verdict on the parallel projection.
 *
 * THE SESSION IS THE FIRST OF THEM (operator, 2026-08-17: « pour chaque génération, donc chaque version, je dois pouvoir retrouver l'id de la session sous
 * l'image »). It is what reopens the conversation with the generator — `codex exec resume <id>` — and it exists nowhere else once the terminal is closed.
 *
 * AND THE MEASURES ARE READ FROM THE IMAGE BY THE SERVICE THAT THE CHECK USES, never recomputed here: `scripts/check-parallel-projection.php` and this line must
 * never be able to disagree about whether a building leans.
 */
function figuresMarkup(array $version): string
{
    if ($version['image'] === null) {
        return '';
    }
    $meta = $version['meta'];
    $lines = [];
    if ($meta === null) {
        $lines[] = '<span class="unplaceable">Session inconnue : cette génération n\'a rien enregistré d\'elle-même.</span>';
    } elseif (($meta['session'] ?? null) === null) {
        $lines[] = '<span class="unplaceable">Session perdue — ' . escape($meta['session_lost'] ?? 'non enregistrée.') . '</span>';
    } else {
        $lines[] = 'Session <code>' . escape($meta['session']) . '</code>';
    }
    if (($meta['generated'] ?? null) !== null) {
        $lines[] = 'Générée le ' . escape(substr($meta['generated'], 0, 16));
    }

    $measures = SpriteMeasures::get();
    $of = $measures->of($version['image'], TX_PIXELS, TY_PIXELS);
    $lines[] = sprintf('Toile %.2f TX × %.2f TY · encre %.2f TX × %.2f TY', $of['box']['tx'], $of['box']['ty'], $of['ink']['tx'], $of['ink']['ty']);
    $lines[] = sprintf('Marges — nord %.2f TY · sud %.2f TY · ouest %.2f TX · est %.2f TX',
        $of['margins']['north'], $of['margins']['south'], $of['margins']['west'], $of['margins']['east']);

    $verdict = $measures->parallelism($version['image']);
    $lines[] = $verdict['held']
        ? '<span class="held">Projection parallèle tenue : aucune arête de la silhouette ne dérive.</span>'
        : sprintf('<span class="unplaceable">Projection parallèle PERDUE — %d arête(s) dérivent, la pire de %+d px sur %d rangées'
            . ' (%.3f px par pixel de descente, attendu 0).</span>',
            count($verdict['faults']), $verdict['worst']['end'] - $verdict['worst']['start'], $verdict['worst']['span'], $verdict['worst']['slope']);

    return '<p class="figures">' . implode('<br>', $lines) . '</p>';
}

/**
 * The version the page opens on: THE LAST ONE THAT HAS AN IMAGE (operator, 2026-08-17: « par défaut, je vois la dernière image avec le dernier diff »).
 *
 * Failing any image at all, the last version — there is nothing tested to open on, and opening on the first would hide every correction written since.
 */
function defaultVersion(array $versions): string
{
    $default = $versions[count($versions) - 1]['label'];
    foreach ($versions as $version) {
        if ($version['image'] !== null) {
            $default = $version['label'];
        }
    }

    return $default;
}

/**
 * What one version's view says of itself: whose image is shown, which text is read beside it, and what the diff between them means.
 *
 * A VERSION'S TAB LOOKS FORWARD: its image, and the text of the NEXT one marked with the diff between them (operator, 2026-08-19: « sur la v7, il semble que je
 * vois le diff entre v6 et v7 au lieu du diff entre v7 et v8 »). One looks at an image while reading what has been corrected SINCE it — that is « what is left
 * to prove ». So a generated version's diff still moves, and that is intended: it follows the corrections written for the next one, until that one is generated
 * in turn and takes over with its own diff.
 *
 * THIS VIEW WAS REMOVED AND PUT BACK THE SAME DAY, and the mistake is worth writing down: on a remark saying the last version's corrections could not be seen,
 * the tab was turned backwards. The real cause was elsewhere — NO pending version existed at that moment, so there was nothing to show. A page that is empty
 * because there is nothing to see is not a wrong page, and turning its meaning around to fill the screen broke what worked.
 */
function viewState(array $version, ?array $next, int $generated): string
{
    $carries = "Image : {$version['label']}, produite par le texte de cette version.";
    if ($next === null) {
        return "$carries Elle est la dernière des $generated versions générées, et aucune version en attente ne la suit :"
            . " il n'y a donc pas de diff tant que la suivante n'est pas écrite.";
    }

    return "$carries Le texte ci-contre est celui de la {$next['label']}, qui n'est pas encore générée, et le diff montre ce qui a changé"
        . " DEPUIS cette image — donc ce qui reste à éprouver. Sur $generated versions générées.";
}

/**
 * The sections of the consigne, read from the HEADINGS THE TEXT CARRIES, and not from a cut-up written beside it.
 *
 * WHY NOT `PromptParts` HERE: its cut-up is signed with the fingerprint of the text the chain produced, and it REFUSES — rightly — to speak of a text rewritten
 * since. Yet the rewritten text is precisely what is being looked at. Reading the headings is not redoing its work: the consigne explains its own format in its
 * first paragraph — « une section porte son titre sous la forme "Titre (mot)" » —, the level is IN the heading, and it is the document that is read, not a
 * derived datum. The chain's cut-up remains what holds authority on the version it produced, and `php scripts/show-prompt-parts.php` reads it there.
 */
function sectionsOf(string $body): array
{
    $sections = [];
    $boundaries = [];
    $group = null;
    $offset = 0;
    foreach (preg_split('/(?<=\n)/', $body, -1, PREG_SPLIT_NO_EMPTY) as $line) {
        $length = strlen($line);
        $bare = rtrim($line, "\n");
        if (preg_match('/^(#{2,3}) (.+?) \((\w+)\)$/u', $bare, $found)) {
            $boundaries[] = $offset;
            $sections[] = ['group' => $found[1] === '###' ? $group : null, 'title' => $found[2], 'level' => $found[3], 'offset' => $offset + $length,
                'length' => 0];
        } elseif (str_starts_with($bare, '## ')) {
            // A GROUP TITLE IS A BOUNDARY TOO, though it opens no section of its own: the block before it stops at its line, not at the next section's heading.
            $boundaries[] = $offset;
            $group = substr($bare, 3);
        }
        $offset += $length;
    }
    $boundaries[] = strlen($body);
    foreach ($sections as $rank => $section) {
        foreach ($boundaries as $boundary) {
            if ($boundary > $section['offset'] - 1) {
                $sections[$rank]['length'] = $boundary - $section['offset'];
                break;
            }
        }
    }

    return $sections;
}

/**
 * The text of one block, with the sentences quoted by a critique HIGHLIGHTED at their exact place.
 *
 * THE ANCHORS ARE LAID FROM THE END TOWARD THE START, and that is not a matter of style: inserting markup shifts everything that follows, so that laying them
 * left to right would slide each following anchor by the length of the tags already written — the highlighting would drift off on the later critiques.
 */
function marked(string $body, string $ops, array $removals, int $offset, int $length, array $anchors): string
{
    $kinds = [];
    foreach ($anchors as $anchor) {
        for ($at = $anchor['offset']; $at < $anchor['offset'] + $anchor['length']; $at++) {
            $kinds[$at] = $anchor['kind'];
        }
    }
    $shown = '';
    $run = '';
    $state = null;
    for ($at = $offset, $stop = $offset + $length; $at <= $stop; $at++) {
        $here = $at < $stop ? [$ops[$at], $kinds[$at] ?? null] : null;
        if ($here !== $state || isset($removals[$at])) {
            $shown .= wrapped($run, $state);
            $run = '';
            $state = $here;
        }
        if (isset($removals[$at])) {
            $shown .= '<del>' . escape($removals[$at]) . '</del>';
        }
        if ($at < $stop) {
            $run .= $body[$at];
        }
    }

    return $shown . wrapped($run, $state);
}

/** One span of text carrying the same pair — the diff operation, and the critique it is anchored to — dressed in one go. */
function wrapped(string $text, ?array $state): string
{
    if ($text === '' || $state === null) {
        return escape($text);
    }
    [$op, $kind] = $state;
    $shown = $op === WordDiff::ADD[0] ? '<ins>' . escape($text) . '</ins>' : escape($text);

    return $kind === null ? $shown : '<mark class="ancre ' . escape($kind) . '">' . $shown . '</mark>';
}

/**
 * The diff from one version to the next, brought back ONTO THE ACTIVE TEXT: one operation code per byte of the active text, and the removed passages filed at
 * the place where they used to read.
 *
 * WHY PER BYTE RATHER THAN IN CHUNKS: the critiques anchor, too, on byte ranges of the active text. Two markups laid one after the other would overlap and
 * produce crossed HTML; brought back to the same frame of reference, they render together, in a single pass.
 */
function diffOverText(?string $previous, string $active): array
{
    if ($previous === null) {
        return [str_repeat(WordDiff::KEEP[0], strlen($active)), []];
    }
    $ops = '';
    $removals = [];
    foreach (WordDiff::get()->versions($previous, $active) as $run) {
        if ($run['op'] === WordDiff::REMOVE) {
            $removals[strlen($ops)] = ($removals[strlen($ops)] ?? '') . $run['text'];
            continue;
        }
        $ops .= str_repeat($run['op'][0], strlen($run['text']));
    }

    // THE DIFF MUST COVER THE ACTIVE TEXT EXACTLY, or rendering would read past its end or leave its tail with no operation — and it would say so through a PHP
    // warning rather than a visible defect. A divergence here is not recovered from, it is reported.
    if (strlen($ops) !== strlen($active)) {
        throw new RuntimeException(sprintf('le diff de versions recouvre %d octets pour un texte actif qui en fait %d.', strlen($ops), strlen($active)));
    }

    return [$ops, $removals];
}

/**
 * What the clause would become, shown IN the text: the removed runs of words struck through, the added ones underlined, the rest intact.
 *
 * NO « BEFORE / AFTER » COLUMN, AND THAT IS THE POINT (operator, 2026-08-13: « je dois pouvoir voir les changements que tu proposes avec un diff inline dans le
 * texte »). Two blocks side by side leave the reader the work the diff exists to do, and on clauses written in capitals they look alike down to the word.
 */
function inlineDiff(string $before, string $after): string
{
    $shown = '';
    foreach (WordDiff::get()->runs($before, $after) as $run) {
        $shown .= match ($run['op']) {
            WordDiff::REMOVE => '<del>' . escape($run['text']) . '</del>',
            WordDiff::ADD => '<ins>' . escape($run['text']) . '</ins>',
            default => escape($run['text']),
        } . ' ';
    }

    return rtrim($shown);
}

/** One critique, as it reads under the section it puts in question — or under the trial when it lands nowhere. */
function critiqueMarkup(array $one): string
{
    $unplaceable = $one['unplaceable'] === null
        ? ''
        : '<p class="unplaceable">Non plaçable : ' . escape($one['unplaceable']) . '</p>';
    // THE QUOTE IS NOT REPEATED WHEN IT IS ALREADY HIGHLIGHTED three lines above — it only serves to show what an unplaceable critique was aiming at.
    $quote = $one['quote'] === null || $one['unplaceable'] === null
        ? ''
        : '<blockquote>' . escape($one['quote']) . '</blockquote>';

    return sprintf('<article class="critique %s"><h4><span class="kind">%s</span> %s</h4>%s%s<p>%s</p></article>',
        escape($one['kind']), escape(Critiques::KINDS[$one['kind']]), escape($one['title']), $quote, $unplaceable, escape($one['text']));
}

$trials = consignes();
$panels = '';
foreach ($trials as $trial) {
    $versions = $trial['versions'];
    if ($versions === []) {
        $panels .= sprintf('<section class="trial"><h2>%s</h2><p class="missing">Ce sujet ne porte aucune version de consigne :'
            . ' il n\'y a rien à lire ni à attribuer.</p></section>', escape($trial['name']));
        continue;
    }

    // UNE VUE PAR VERSION, ET ON NAVIGUE ENTRE ELLES (opérateur, 2026-08-17 : « chaque image conserve son prompt et on peut voir le diff de cette image avec la
    // suivante pour voir ce qui a changé. par défaut, je vois la dernière image avec le dernier diff mais je peux retrouver son prompt initial et naviguer
    // entre les différentes versions »). La vue d'une version montre SON image et le texte de la version SUIVANTE, marqué du diff qui les sépare : c'est cela,
    // « ce qui a changé depuis cette image ».
    //
    // AND THE DIFF NEVER LOOKS BACK: a diff towards the PREVIOUS version would show changes the image ALREADY carries, and a freshly generated version would
    // display covered in red and green while nothing awaits it. The last version has no successor and therefore shows its bare text, saying so — as long as no
    // pending version exists there is nothing to compare, and that is an answer, not a defect.
    // AND A VERSION WITHOUT AN IMAGE HAS NO TAB (operator, 2026-08-19: « le bouton v8 ne doit être dispo que si la v8 est générée, c'est comme ça pour la
    // version à venir, on ne la voit pas. Elle sera présente dans l'interface quand générée »). Its text is ALREADY readable, in the diff of the last generated
    // version: giving it a tab of its own would show it twice — once marked with the diff, once bare — with nothing saying which is which. A tab is therefore
    // the address of an IMAGE, and a pending version has none.
    $views = '';
    $tabs = '';
    $consignes = Consignes::get();
    $default = defaultVersion($versions);
    $generated = 0;
    foreach ($versions as $version) {
        $generated += $version['image'] === null ? 0 : 1;
    }
    if ($generated === 0) {
        $panels .= sprintf('<section class="trial"><h2>%s</h2><p class="missing">Aucune version de ce sujet n\'a été générée :'
            . ' il n\'y a pas encore d\'image à regarder, donc rien à juger.</p></section>', escape($trial['name']));
        continue;
    }
    foreach ($versions as $index => $version) {
        $next = $versions[$index + 1] ?? null;
        if ($version['image'] === null) {
            continue;
        }
        $shown = $next ?? $version;
        $body = file_get_contents($shown['path']);
        $earlier = $next === null ? null : file_get_contents($version['path']);
        $filed = $critiques->read($shown['path'], $body, $root);
        // C'EST LA CONSIGNE TRANSMISE DE LA VERSION QUI PORTE L'IMAGE, puisque c'est elle que l'agent lisait quand il l'a envoyée à son modèle.
        $transmitted = $version['transmitted'] === null ? null : file_get_contents($version['transmitted']);

        [$ops, $removals] = diffOverText($earlier, $body);
        // THE TEXT SHOWN IS THE ONE THE GENERATOR READS, HEADINGS REMOVED: title and level already stand above it, and repeating them in the body would make the
        // same line be read twice.
        $blocks = '';
        $rendered = [];
        // LA HIÉRARCHIE SE VOIT, ELLE NE SE RECOPIE PAS SUR CHAQUE SECTION (opérateur, 2026-08-17 : « on est censé avoir un titre de section, avoir des sous
        // sections et certaines sections indiquent un domaine »). Le groupe s'écrivait en fil d'Ariane devant chaque titre — « Comment travailler › Ce que tu
        // nous rapportes common » —, si bien qu'il se répétait à l'identique quatre fois de suite et qu'on ne voyait plus ce qui contenait quoi. Il s'écrit
        // maintenant UNE fois, en tête des sections qu'il regroupe, et le niveau devient une étiquette au lieu d'un mot collé au titre.
        $group = null;
        foreach (sectionsOf($body) as $part) {
            if ($part['group'] !== $group) {
                $group = $part['group'];
                if ($group !== null) {
                    $blocks .= '<h3 class="group">' . escape($group) . '</h3>';
                }
            }
            $from = $part['offset'];
            $content = substr($body, $from, $part['length']);
            // AUCUN ÉTAT DE SECTION N'EST AFFICHÉ, ET C'EST DÉLIBÉRÉ (opérateur, 2026-08-17 : « ça n'a pas été demandé car ça ne peut pas fonctionner »).
            // Chercher nos phrases MOT POUR MOT dans la consigne transmise ne peut rien mesurer : l'agent réécrit au lieu de relayer, et deux sections qui
            // disent elles-mêmes « tu ne la transmets pas » sortaient marquées « Disparue » — une alarme sur un succès. Un indicateur qui se trompe de sens
            // sur les cas les plus simples n'est pas un indicateur incomplet, c'est du bruit.
            $anchored = $critiques->within($filed['critiques'], $from, strlen($content));
            foreach ($anchored as $one) {
                $rendered[$one['offset']] = true;
            }
            $blocks .= sprintf(
                '<article class="section%s"><h4>%s <span class="level" title="Le niveau de notre système d\'où vient cette section">%s</span></h4>'
                . '<pre>%s</pre>%s</article>',
                $part['group'] === null ? ' section--alone' : '',
                escape($part['title']),
                escape($part['level']),
                marked($body, $ops, $removals, $from, strlen($content), $anchored),
                implode('', array_map('critiqueMarkup', $anchored))
            );
        }
        // A PLACED CRITIQUE RENDERED NOWHERE DOES NOT VANISH IN SILENCE. It anchored on a section heading, hence outside the matter the generator reads; it joins
        // the unanchored ones saying so, rather than evaporating between two loops.
        foreach ($filed['critiques'] as $rank => $one) {
            if ($one['offset'] !== null && !isset($rendered[$one['offset']])) {
                $filed['critiques'][$rank]['offset'] = null;
                $filed['critiques'][$rank]['unplaceable'] = 'sa citation tombe sur un titre de section, pas sur la matière que le générateur lit.'
                    . ' Solution — citer une phrase du corps de la section.';
            }
        }

        $loose = $critiques->loose($filed['critiques']);
        $looseBlock = $loose === []
            ? ''
            : '<div class="loose"><h3>Ce que je vois sur l\'image</h3>' . implode('', array_map('critiqueMarkup', $loose)) . '</div>';
        if ($filed['fault'] !== null) {
            $looseBlock = '<p class="missing">' . escape($filed['fault']) . '</p>' . $looseBlock;
        }

        // LA CONSIGNE TRANSMISE VIT DANS LA VUE DE SA VERSION, et non plus en pied de panneau : hors de la version, elle donnait à croire qu'un seul texte avait
        // été transmis pour toute la chaîne. Absente, on dit lequel des deux cas c'est — l'agent n'a rien rapporté, ou la version n'a jamais été générée.
        //
        // AND WHAT IT LOST IS READ ABOVE IT, not only at the command line. Since the agent is asked to TRANSLATE, nobody can see by eye whether a constraint
        // survived the journey: the words changed on purpose. The verdict comes from the same service as `review-server/workshop/check-transmitted.php` —
        // nothing is recomputed here, or the page and the command would end up contradicting each other.
        $transmittedBlock = $transmitted !== null
            ? lossMarkup(TransmittedNumbers::get()->compare(file_get_contents($version['path']), $transmitted))
                . passesMarkup($transmitted)
            : ($version['image'] === null
                ? '<p class="missing">Cette version n\'a pas été générée : il n\'y a pas de consigne transmise.</p>'
                : '<p class="missing">L\'agent n\'a rien rapporté entre ses marqueurs pour cette version. Sans ce texte, on ne peut pas distinguer une clause'
                    . ' qui prescrivait mal d\'une clause perdue à sa reformulation. À retenter :'
                    . ' <code>php review-server/workshop/extract-transmitted.php ' . escape($trial['name']) . ' ' . escape($version['label']) . '</code></p>');

        $current = $version['label'] === $default;
        $tabs .= sprintf('<button type="button" class="version-tab%s" data-version="%s"%s>%s%s</button>',
            $current ? ' current' : '', escape($version['label']), $current ? ' aria-current="true"' : '',
            escape($version['label']), $version['image'] === null ? '' : ' <span class="dot" title="Cette version a une image">●</span>');
        // THE PER-EDIT STATE BEARS ON THE TEXT ONE READS, so on the version shown in the column — the next one when it exists. Its corrections are the ones
        // being judged, and what will be reported into the code depends on them.
        $named = $consignes->partsOf($shown['path']);
        $edits = $named === null ? ['edits' => [], 'note' => null, 'fault' => null] : $consignes->editsOf($named['subject'], $named['rank']);
        $views .= sprintf('<div class="version-view%s" data-version="%s"%s><p class="version">%s</p>'
            . '<div class="split"><div class="image">%s%s</div><div class="prompt">%s</div></div>'
            . '<h3 class="transmise">Ce que l\'agent a transmis à son modèle d\'images, pour cette version</h3>%s%s</div>',
            $current ? '' : ' hidden', escape($version['label']), $current ? '' : ' hidden',
            escape(viewState($version, $next, $generated)),
            pictureMarkup($root, $inventory, $trial, $version['image']) . figuresMarkup($version), $looseBlock, $blocks,
            $transmittedBlock, editsMarkup($edits));
    }

    $panels .= sprintf(
        '<section class="trial" data-trial="%s"><h2>%s</h2><nav class="versions" aria-label="Les versions de cette consigne">'
        . '<span class="versions-label">Versions</span>%s<button type="button" class="plain-toggle" aria-pressed="false">Masquer le diff</button></nav>%s</section>',
        escape($trial['name']), escape($trial['name']), $tabs, $views
    );
}

$page = <<<'HTML'
<title>L'atelier de génération</title>
{$favicon}
<!-- LA GRILLE DE CASES EST LA MÊME SUR TOUS LES OUTILS, donc sa feuille vit avec son service et se charge ici comme sur la page des sprites. -->
<link rel="stylesheet" href="/review-server/lib/footprint-grid.css">
<!-- TOUTE PAGE DIT SON CHEMIN D'ACCÈS ET REMONTE À L'INDEX (opérateur, 2026-08-17). Deux niveaux au plus pour l'instant, l'index étant le premier : une page
     servie qui n'affiche pas d'où elle vient est une page qu'on atteint par son adresse et qu'on ne retrouve jamais. -->
<nav class="arbo" aria-label="Chemin d'accès"><a href="/">Index</a> <span aria-hidden="true">›</span> <span>L'atelier de génération</span></nav>
<h1>L'atelier de génération</h1>
<p class="lede">{$tally}</p>
<p class="legende"><span><del>Texte barré</del> — retiré depuis l'image affichée</span><span><ins>Texte vert</ins> — ajouté depuis
l'image affichée</span><span><mark class="ancre">Texte souligné</mark> — la phrase qu'une critique met en cause</span><span>● — cette version a une
image</span></p>
<p class="lede">Une consigne vit sous var/generations/consignes/, un répertoire par sujet, chaîne entière — racine comprise. Ce sont des essais, jamais
commités : ce qui doit leur survivre n'est pas leur texte mais ce qu'ils ont appris. Les règles se définissent une seule fois sous
review-server/workshop/source/, et php review-server/workshop/check-source.php refuse qu'un bloc parle de ce qu'un autre gouverne. Page construite le
{$built}.</p>
{$reloadMarkup}
{$trials}
<style>
{$theme}
{$layout}
{$reloadStyles}
  .trial { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--trait); }
  .split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 1.5rem; align-items: start; }
  /* THE CONSIGNE SCROLLS IN ITS OWN COLUMN, AND ITS HEIGHT IS BOUNDED (operator, 2026-08-18: « la colonne de droite avec la consigne doit être d'une hauteur
     limitée sinon ça scroll longtemps et je ne peux pas voir ce qui est envoyé réellement au générateur »). Unbounded, the sixteen thousand characters of the
     consigne pushed the TRANSMITTED one — the only text saying what the image model actually read — screens away, and comparing the two, which is why this
     page exists, could not be done. */
  .prompt { max-height: calc(100vh - 6rem); overflow: auto; padding-right: .75rem; }
  /* L'image SUIT LA LECTURE de la consigne : on juge une phrase en la regardant, et une image restée en haut de page oblige à remonter à chaque critique. */
  .image { position: sticky; top: 1rem; }
  .image img { max-width: 100%; height: auto; image-rendering: pixelated; }
  /* L'enveloppe de l'image se rétrécit avec elle : la grille est en pourcentages de cette enveloppe, et sans cela elle resterait à la taille de l'image livrée
     pendant que le dessin, lui, tient dans la colonne. */
  .image .picture { max-width: 100%; }
  /* LA NAVIGATION ENTRE VERSIONS EST UNE BARRE, ET LA PASTILLE DIT LAQUELLE A UNE IMAGE — c'est le seul repère qui distingue une version éprouvée d'un texte
     écrit depuis, et sans lui on choisit un onglet sans savoir ce qu'on va y trouver. */
  .versions { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; margin: .5rem 0 1rem; }
  .versions-label { font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; margin-right: .3rem; }
  .version-tab {
    font: inherit; font-size: .85rem; padding: .25rem .6rem; cursor: pointer;
    color: var(--ink); background: transparent; border: 1px solid var(--trait); border-radius: 3px;
  }
  .version-tab.current { border-color: #6a8ac0; }
  .version-tab .dot { color: #6aa06a; font-size: .7rem; }
  .plain-toggle {
    font: inherit; font-size: .8rem; padding: .25rem .6rem; margin-left: auto; cursor: pointer;
    color: var(--ink); background: transparent; border: 1px dashed var(--trait); border-radius: 3px;
  }
  /* MASQUER LE DIFF REND LE PROMPT NU DE LA VERSION AFFICHÉE (opérateur, 2026-08-17 : « je peux retrouver son prompt initial »). Le retiré disparaît, l'ajouté
     reprend la couleur du texte : ce qui reste est exactement le fichier, à l'octet. */
  .trial.plain del { display: none; }
  .trial.plain ins { color: inherit; }
  /* LE GROUPE EST UN TITRE, SES SECTIONS SONT EN DESSOUS ET DÉCALÉES : c'est le décalage qui dit ce qui contient quoi, sans avoir à répéter le nom du groupe
     sur chaque section. Une section sans groupe — un « ## Titre (niveau) » du texte — n'est pas décalée, parce qu'elle n'est sous rien. */
  .group {
    margin: 1.75rem 0 .5rem; font-size: 1.02rem; font-weight: 700;
    padding-bottom: .2rem; border-bottom: 1px solid var(--trait);
  }
  .group:first-child { margin-top: 0; }
  .section { margin-bottom: 1.25rem; padding-left: 1rem; border-left: 1px solid var(--trait); }
  .section--alone { padding-left: 0; border-left: none; }
  .section h4 { margin: 0 0 .25rem; font-size: .92rem; font-weight: 600; }
  /* LE NIVEAU EST UNE ÉTIQUETTE, PAS UN MOT DU TITRE : collé derrière le titre en texte nu, il se lisait comme la fin de la phrase — « Ce que tu nous rapportes
     common ». Il dit d'où vient la section dans NOTRE système, il ne décrit rien de l'image. */
  .level {
    font-weight: 400; font-size: .7rem; text-transform: uppercase; letter-spacing: .04em;
    padding: .1rem .4rem; margin-left: .35rem; border: 1px solid var(--trait); border-radius: 2px; opacity: .75;
  }
  pre { white-space: pre-wrap; word-break: break-word; margin: 0; font-size: .82rem; line-height: 1.45; }
  .whole { max-height: 32rem; overflow: auto; }
  .state { display: inline-block; font-size: .8rem; margin-bottom: .25rem; }
  .state.intact { color: #6aa06a; }
  .state.partial { color: #c09a4a; }
  .state.lost { color: #c06a6a; }
  .state.unmeasurable, .state.unknown { opacity: .65; }
  .lost-numbers { margin: .25rem 0 .75rem 1.2rem; padding: 0; font-size: .82rem; }
  .lost-numbers li { margin-bottom: .2rem; }
  /* A PASS IS A BLOCK OF ITS OWN, AND ITS HEADING SAYS SO: run together, the pass that draws and the one that repaints the background read as a single text. */
  h4.passe { margin: 1rem 0 .3rem; font-size: .88rem; font-weight: 600; }
  /* WHAT A VERSION CHANGED, EDIT BY EDIT: that grain is what decides a report into the code, not a version-wide verdict. */
  .edits { margin: .5rem 0 0; padding: 0; list-style: none; }
  .edits li { margin-bottom: .9rem; padding-left: .75rem; border-left: 1px solid var(--trait); }
  .edit-why { margin: .2rem 0 0; font-size: .84rem; opacity: .85; }
  .edit-note { margin: .3rem 0 .8rem; font-size: .84rem; opacity: .85; }
  /* TROIS COULEURS, TROIS SENS, ET AUCUNE N'EN PORTE DEUX : rouge ce qui disparaît, vert ce qui s'ajoute, bleu la phrase qu'une critique met en cause. La
     couleur de l'ancre passe par le SOULIGNÉ et jamais par le texte, sinon elle se mélangerait au rouge et au vert du diff sur les passages qui sont les deux. */
  del { color: #c06a6a; text-decoration: line-through; text-decoration-thickness: 1px; }
  ins { color: #6aa06a; text-decoration: none; }
  mark.ancre { background: transparent; color: inherit; border-bottom: 2px solid #6a8ac0; padding-bottom: 1px; }
  .critique { margin: .5rem 0 .5rem 1rem; padding: .5rem .75rem; border-left: 3px solid #6a8ac0; font-size: .85rem; }
  .legende { display: flex; flex-wrap: wrap; gap: 1.25rem; font-size: .82rem; margin: .5rem 0 1.5rem; }
  .legende span { opacity: .9; }
  .critique h4 { margin: 0 0 .25rem; font-size: .88rem; }
  .critique .kind { text-transform: uppercase; font-size: .72rem; letter-spacing: .04em; opacity: .8; margin-right: .4rem; }
  .critique blockquote { margin: .25rem 0; padding-left: .6rem; border-left: 1px solid var(--trait); opacity: .8; font-style: italic; }
  .critique p { margin: .25rem 0 0; }
  .unplaceable { color: #c09a4a; }
  .loose { margin-top: 1rem; }
  .loose h3 { font-size: .95rem; margin: 0 0 .5rem; }
  .missing { font-size: .85rem; opacity: .8; }
  /* THE UNTESTED STATE IS A WARNING, NOT A CAPTION: it says the text beside the image did not produce it, so it carries the amber the page already uses to say
     "this cannot be concluded from". */
  .version { font-size: .85rem; margin: .25rem 0 1rem; padding: .5rem .75rem; border-left: 3px solid #c09a4a; }
  /* LES CHIFFRES VIVENT SOUS L'IMAGE, parce que c'est là qu'on les lit — en la regardant. La session vient en premier : c'est elle qui rouvre la conversation
     avec le générateur, et elle n'existe nulle part ailleurs une fois le terminal fermé. */
  .arbo { font-size: .8rem; margin: 0 0 .5rem; opacity: .85; }
  .arbo a { color: inherit; }
  .figures { font-size: .78rem; line-height: 1.6; margin: .6rem 0 0; opacity: .9; }
  .figures code { font-size: .95em; word-break: break-all; }
  .figures .held { color: #6aa06a; }
</style>
<script>
// LA NAVIGATION EST ENTIÈREMENT DANS LA PAGE, sans requête : toutes les versions sont construites en même temps qu'elle, et changer d'onglet ne fait que
// dévoiler celle qu'on demande. Une page d'atelier tient quatre versions d'un même texte ; aller les chercher une par une au serveur ajouterait un aller-retour
// et un état à tenir pour un contenu déjà écrit.
document.querySelectorAll('.trial').forEach(function (trial) {
  trial.querySelectorAll('.version-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      var wanted = tab.dataset.version;
      trial.querySelectorAll('.version-tab').forEach(function (other) {
        var on = other.dataset.version === wanted;
        other.classList.toggle('current', on);
        // L'ÉTAT COURANT EST DIT AUX DEUX LECTURES, la visuelle et celle du lecteur d'écran : sans `aria-current`, la barre n'a plus d'onglet actif pour qui
        // ne voit pas la bordure.
        if (on) { other.setAttribute('aria-current', 'true'); } else { other.removeAttribute('aria-current'); }
      });
      trial.querySelectorAll('.version-view').forEach(function (view) {
        view.hidden = view.dataset.version !== wanted;
      });
    });
  });
  var plain = trial.querySelector('.plain-toggle');
  plain.addEventListener('click', function () {
    var on = trial.classList.toggle('plain');
    plain.setAttribute('aria-pressed', on ? 'true' : 'false');
    plain.textContent = on ? 'Montrer le diff' : 'Masquer le diff';
  });
});
</script>
{$reloadScript}
HTML;

$page = strtr($page, [
    '{$theme}' => $theme->css('graphite'),
    '{$layout}' => Layout::get()->css(),
    '{$favicon}' => $favicon->tag(),
    '{$reloadStyles}' => $reload->styles(),
    '{$reloadMarkup}' => $reload->markup(),
    '{$reloadScript}' => $reload->script('/workshop'),
    '{$tally}' => sprintf('%d essai(s) de consigne.', count($trials)),
    '{$built}' => date('Y-m-d à H:i'),
    '{$trials}' => $panels ?: '<p class="missing">Aucun essai pour l\'instant.</p>',
]);

file_put_contents($outputPath, $page);
printf("%s — %d essai(s), %.1f ko\n", $outputPath, count($trials), strlen($page) / 1024);

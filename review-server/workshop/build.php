<?php
/**
 * Usage: php review-server/workshop/build.php [output.html] — builds the page that shows the consigne trials, served at /workshop.
 *        php review-server/workshop/build.php -h|--help — this text, and nothing is built.
 *
 * Intention: A GENERATION PRODUCES FOUR THINGS THAT LIVED IN FOUR PLACES, so nobody could tie a defect in the image back to the sentence that caused it. The
 * consigne sent, its cut-up by level, the prompt the agent passed on to its OWN image model, and the image itself are shown here side by side, for one trial at
 * a time — with the critiques anchored on the very sentences they put in question.
 *
 * WHAT IT READS AND NEVER RECOMPUTES: the cut-up and its fingerprint are read by `PromptParts`, the sentence-by-sentence comparison by `PromptDiff`, the anchored
 * critiques by `Critiques`. This page HAD its own copies of the first two, and both had already drifted: the copy of the split checked a `sha256` key the chain
 * never wrote — so the fingerprint was NEVER verified and sentences could be attributed to the wrong level in silence — and the copy of the comparison had no
 * evidence floor, counting « OUI. » found in a page of text as a clause that came through. That is the duplication this repository pays for most often, and it
 * is why nothing is recomputed here.
 *
 * A TRIAL IS NOT A DELIVERABLE: it lives under var/generations/trials/, is not versioned, enters no referential, appears on no sprite page, and burns no version
 * of a subject. It therefore vanishes on a cleanup, and this page says so rather than letting an absent trial read as one that never existed.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/PromptParts.php';
require_once $root . '/review-server/lib/PromptDiff.php';
require_once $root . '/review-server/lib/Critiques.php';
require_once $root . '/review-server/lib/WordDiff.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();
$parts = PromptParts::get();
$diff = PromptDiff::get();
$critiques = Critiques::get();

/** Where the trials live. Under `var/` because a page of the application reads them: `local/` belongs to the agent, `var/` belongs to the application. */
const TRIALS = 'var/generations/trials';

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * The trials present on disk, newest first.
 *
 * A TRIAL IS A DIRECTORY, and what it carries is recognized by the suffixes the chain already uses beside a produced image — no name is invented here. Every
 * piece may be missing, and that is the rule rather than the exception: the agent does not always report the consigne it transmitted, and an old trial has no
 * cut-up. What is missing is named in its place on the page, never replaced by a fallback value.
 */
function trials(string $root): array
{
    $directory = "$root/" . TRIALS;
    if (!is_dir($directory)) {
        return [];
    }
    $found = [];
    foreach (scandir($directory) as $entry) {
        if ($entry === '.' || $entry === '..' || !is_dir("$directory/$entry")) {
            continue;
        }
        $prompt = null;
        foreach (glob("$directory/$entry/*.txt") as $candidate) {
            if (!str_ends_with($candidate, '.transmitted.txt')) {
                $prompt = $candidate;
            }
        }
        $stem = $prompt ? substr($prompt, 0, -4) : null;
        $found[] = [
            'name' => $entry,
            'prompt' => $prompt,
            'versions' => $prompt ? versionsOf($root, $entry, basename($prompt, '.txt'), $prompt) : [],
            'transmitted' => $stem && is_file("$stem.transmitted.txt") ? "$stem.transmitted.txt" : null,
            'image' => $stem && is_file("$stem.png") ? "$stem.png" : null,
        ];
    }
    // A trial's name opens with its date, so reversing the name order gives newest first — no date is read back to obtain it.
    usort($found, fn($one, $other) => strcmp($other['name'], $one['name']));

    return $found;
}

/**
 * The versions of one consigne, from the oldest to the active one — the last of the list is the one that holds authority.
 *
 * WE NO LONGER WORK BY REGENERATING, WE WORK BY MODIFYING WHAT WAS GENERATED (operator, 2026-08-13: « on ne travaille plus en regénérant, on travaille en
 * modifiant ce qui a été généré ») : a clean consigne is first written end to end, and only what works then goes back into the code. Each retouch therefore
 * produces a whole VERSION, `<consigne>.v2.txt`, `.v3.txt`, and **the diff runs from one version to the next** — regenerating from a modified version makes that
 * one the active one, and the retouches after it refer to it.
 *
 * Version 1 is the text the chain produced, under var/; the following ones live beside the critiques, the only place open both to the agent's writing and to the
 * application's reading.
 */
function versionsOf(string $root, string $trial, string $stem, string $generated): array
{
    $versions = [['label' => 'v1', 'path' => $generated]];
    $directory = "$root/review-server/critiques/$trial";
    $rank = 2;
    while (is_file($path = "$directory/$stem.v$rank.txt")) {
        $versions[] = ['label' => "v$rank", 'path' => $path];
        $rank++;
    }

    return $versions;
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

$trials = trials($root);
$panels = '';
foreach ($trials as $trial) {
    $transmitted = $trial['transmitted'] ? file_get_contents($trial['transmitted']) : null;
    $versions = $trial['versions'];
    $active = $versions === [] ? null : $versions[count($versions) - 1];
    $body = $active === null ? null : file_get_contents($active['path']);
    $earlier = count($versions) > 1 ? file_get_contents($versions[count($versions) - 2]['path']) : null;
    $filed = $body === null ? ['critiques' => [], 'fault' => null] : $critiques->read($active['path'], $body, $root);

    $blocks = '';
    if ($body === null) {
        $blocks = '<p class="missing">Cet essai ne porte aucune consigne : il n\'y a rien à lire ni à attribuer.</p>';
    } else {
        [$ops, $removals] = diffOverText($earlier, $body);
        // THE TEXT SHOWN IS THE ONE THE GENERATOR READS, HEADINGS REMOVED: title and level already stand above it, and repeating them in the body would make the
        // same line be read twice.
        $rendered = [];
        foreach (sectionsOf($body) as $part) {
            $from = $part['offset'];
            $content = substr($body, $from, $part['length']);
            $sentences = $diff->sentencesOf($body, $from, strlen($content));
            $compared = $diff->compare($sentences, $transmitted);
            // THE STATE IS SHOWN ONLY WHEN IT SAYS SOMETHING. With no transmitted consigne there is nothing to compare, and repeating that under each of the
            // thirteen sections fills the page with a sentence that never varies — the trial says it once, at its head.
            $state = $compared['state'] === null
                ? ''
                : sprintf('<span class="state %s">%s — %d/%d phrase(s) retrouvée(s) mot pour mot</span>', escape($compared['state']),
                    escape(PromptDiff::SECTION_LABELS[$compared['state']]), $compared['found'], $compared['found'] + $compared['missing']);
            $anchored = $critiques->within($filed['critiques'], $from, strlen($content));
            foreach ($anchored as $one) {
                $rendered[$one['offset']] = true;
            }
            $blocks .= sprintf(
                '<article class="section"><h3>%s%s <span class="level">%s</span></h3>%s<pre>%s</pre>%s</article>',
                $part['group'] ? escape($part['group']) . ' › ' : '',
                escape($part['title']),
                escape($part['level']),
                $state,
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
    }

    $image = $trial['image']
        ? '<img src="/' . escape(substr($trial['image'], strlen($root) + 1)) . '" alt="">'
        : '<p class="missing">Pas d\'image : la génération n\'a rien livré dans ce dossier.</p>';

    $loose = $critiques->loose($filed['critiques']);
    $looseBlock = $loose === []
        ? ''
        : '<div class="loose"><h3>Ce que je vois sur l\'image</h3>' . implode('', array_map('critiqueMarkup', $loose)) . '</div>';
    if ($filed['fault'] !== null) {
        $looseBlock = '<p class="missing">' . escape($filed['fault']) . '</p>' . $looseBlock;
    }

    $transmittedBlock = $transmitted === null
        ? '<p class="missing">Pas de consigne transmise : l\'agent ne l\'a pas rapportée. Sans elle, on ne peut pas distinguer une clause qui prescrivait mal '
            . 'd\'une clause perdue à sa reformulation.</p>'
        : '<pre class="whole">' . escape($transmitted) . '</pre>';

    $panels .= sprintf(
        '<section class="trial"><h2>%s</h2><div class="split"><div class="image">%s%s</div><div class="consigne">%s</div></div>'
        . '<h3 class="transmise">Ce que l\'agent a transmis à son modèle d\'images</h3>%s</section>',
        escape($trial['name']), $image, $looseBlock, $blocks, $transmittedBlock
    );
}

$page = <<<'HTML'
<h1>L'atelier de génération</h1>
<p class="lede">{$tally}</p>
<p class="legende"><span><del>Texte barré</del> — retiré depuis la version précédente</span><span><ins>Texte vert</ins> — ajouté depuis la version
précédente</span><span><mark class="ancre">Texte souligné</mark> — la phrase qu'une critique met en cause</span></p>
<p class="lede">Les essais vivent sous var/generations/trials/, qui n'est pas versionné : cette page liste ce qui existait quand elle a été construite, le
{$built}. Un essai nettoyé depuis reste lisible ici et disparaîtra à la construction suivante.</p>
{$reloadMarkup}
{$trials}
<style>
{$theme}
{$layout}
{$reloadStyles}
  .trial { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--trait); }
  .split { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 3fr); gap: 1.5rem; align-items: start; }
  /* L'image SUIT LA LECTURE de la consigne : on juge une phrase en la regardant, et une image restée en haut de page oblige à remonter à chaque critique. */
  .image { position: sticky; top: 1rem; }
  .image img { max-width: 100%; height: auto; image-rendering: pixelated; }
  .section { margin-bottom: 1.25rem; }
  .section h3 { margin: 0 0 .25rem; font-size: .95rem; font-weight: 600; }
  .level { font-weight: 400; opacity: .7; font-size: .85rem; }
  pre { white-space: pre-wrap; word-break: break-word; margin: 0; font-size: .82rem; line-height: 1.45; }
  .whole { max-height: 32rem; overflow: auto; }
  .state { display: inline-block; font-size: .8rem; margin-bottom: .25rem; }
  .state.intact { color: #6aa06a; }
  .state.partial { color: #c09a4a; }
  .state.lost { color: #c06a6a; }
  .state.unmeasurable, .state.unknown { opacity: .65; }
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
</style>
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

<?php
/**
 * Usage: php review-server/workshop/build.php [output.html] — builds the page that shows the consigne trials, served at /workshop.
 *        php review-server/workshop/build.php -h|--help — this text, and nothing is built.
 *
 * Intention: A GENERATION PRODUCES FOUR THINGS THAT LIVED IN FOUR PLACES, so nobody could tie a defect in the image back to the sentence that caused it. The
 * consigne sent, its cut-up by level, the prompt the agent passed on to its OWN image model, and the image itself are shown here side by side, for one trial at
 * a time.
 *
 * WHAT IT READS AND NEVER RECOMPUTES: the cut-up and its fingerprint are written by the chain beside the consigne, and `php scripts/show-prompt-parts.php`
 * already reads and checks them. Rebuilding either here would make a second version that drifts — the fault this repository pays most often.
 *
 * A TRIAL IS NOT A DELIVERABLE: it lives under var/generations/trials/, is not versioned, enters no referential, appears on no sprite page, and burns no version
 * of a subject. It therefore vanishes on a cleanup, and this page says so rather than letting an absent trial read as one that never existed.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();

/** Où vivent les essais. Sous `var/` parce qu'une page de l'application les lit : `local/` est à l'agent, `var/` est à l'application. */
const TRIALS = 'var/generations/trials';

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * Les essais présents sur le disque, le plus récent d'abord.
 *
 * UN ESSAI EST UN DOSSIER, et ce qu'il porte se reconnaît aux suffixes que la chaîne emploie déjà à côté d'une image produite — aucun nom n'est inventé ici.
 * Chaque pièce peut manquer, et c'est la règle plutôt que l'exception : l'agent ne rapporte pas toujours sa consigne transmise, et un essai ancien n'a pas de
 * découpage. Ce qui manque est nommé à sa place dans la page, jamais remplacé par une valeur de repli.
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
        $consigne = null;
        foreach (glob("$directory/$entry/*.txt") as $candidate) {
            if (!str_ends_with($candidate, '.transmitted.txt')) {
                $consigne = $candidate;
            }
        }
        $stem = $consigne ? substr($consigne, 0, -4) : null;
        $found[] = [
            'name' => $entry,
            'consigne' => $consigne,
            'parts' => $stem && is_file("$stem.parts.json") ? "$stem.parts.json" : null,
            'transmitted' => $stem && is_file("$stem.transmitted.txt") ? "$stem.transmitted.txt" : null,
            'image' => $stem && is_file("$stem.png") ? "$stem.png" : null,
        ];
    }
    // Le nom d'un essai commence par sa date, donc l'ordre inverse du nom est l'ordre du plus récent au plus ancien — aucune date n'est relue pour cela.
    usort($found, fn($one, $other) => strcmp($other['name'], $one['name']));

    return $found;
}

/**
 * Le découpage d'une consigne, relu et éprouvé plutôt que cru sur parole.
 *
 * L'EMPREINTE ET LE PAVAGE SONT VÉRIFIÉS ICI COMME LE LECTEUR EN LIGNE DE COMMANDE LE FAIT : un découpage qui ne porte pas sur CE texte-là, ou qui laisse un
 * trou, ferait attribuer une phrase au mauvais niveau — ce qui enverrait porter un correctif là où la phrase n'est pas. Rendre null fait dire à la page qu'elle
 * ne peut pas attribuer, ce qui est la seule réponse honnête.
 */
function sections(?string $partsPath, ?string $consignePath): ?array
{
    if (!$partsPath || !$consignePath) {
        return null;
    }
    $parts = json_decode(file_get_contents($partsPath), true);
    $text = file_get_contents($consignePath);
    if (!is_array($parts) || !isset($parts['parts'])) {
        return null;
    }
    if (isset($parts['sha256']) && $parts['sha256'] !== hash('sha256', $text)) {
        return null;
    }
    $sections = [];
    $covered = 0;
    foreach ($parts['parts'] as $part) {
        $offset = $part['offset'] ?? null;
        $length = $part['length'] ?? null;
        if ($offset === null || $length === null || $offset !== $covered) {
            return null;
        }
        $covered += $length;
        $sections[] = [
            'level' => $part['level'] ?? '',
            'title' => $part['title'] ?? '',
            'group' => $part['group'] ?? null,
            'text' => substr($text, $offset, $length),
        ];
    }

    return $covered === strlen($text) ? $sections : null;
}

/**
 * Ce que la page CALCULE, et la seule chose : phrase par phrase, notre texte a-t-il été retrouvé mot pour mot dans celui que l'agent a transmis.
 *
 * AUCUN SCORE DE SIMILARITÉ, ET C'EST DÉLIBÉRÉ. Une phrase absente au mot près peut être présente en idée, et aucune mesure mécanique ne tranche cela sans
 * inventer une certitude — un outil qui ne peut pas conclure dit qu'il ne peut pas conclure, ce n'est pas un verdict favorable. La page dit donc ce qu'elle a
 * CHERCHÉ et ce qu'elle a TROUVÉ, et le lecteur peut refaire la recherche lui-même. Un vrai jugement de sens vient d'un agent qui lit.
 */
function survival(string $ours, string $transmitted): array
{
    $normalise = fn(string $text) => preg_replace('/\s+/u', ' ', mb_strtolower(trim($text)));
    $haystack = $normalise($transmitted);
    $found = 0;
    $total = 0;
    foreach (preg_split('/(?<=[.;:!?])\s+/u', $ours) as $sentence) {
        $needle = $normalise($sentence);
        if (mb_strlen($needle) < 12) {
            continue;
        }
        $total++;
        $found += str_contains($haystack, $needle) ? 1 : 0;
    }

    return ['found' => $found, 'total' => $total];
}

$trials = trials($root);
$panels = '';
foreach ($trials as $trial) {
    $sections = sections($trial['parts'], $trial['consigne']);
    $transmitted = $trial['transmitted'] ? file_get_contents($trial['transmitted']) : null;

    $blocks = '';
    if ($sections === null) {
        $blocks = '<p class="missing">Pas de découpage exploitable : soit la chaîne n\'en a écrit aucun, soit son empreinte ne correspond plus à cette '
            . 'consigne. La page ne peut donc attribuer aucune phrase à un niveau, et elle ne le devine pas.</p>';
        if ($trial['consigne']) {
            $blocks .= '<pre class="whole">' . escape(file_get_contents($trial['consigne'])) . '</pre>';
        }
    } else {
        foreach ($sections as $section) {
            $verdict = '';
            if ($transmitted !== null) {
                $counted = survival($section['text'], $transmitted);
                $word = $counted['found'] === 0 ? 'disparue' : ($counted['found'] === $counted['total'] ? 'intacte' : 'partielle');
                $verdict = sprintf('<span class="survival %s">%s — %d/%d phrase(s) retrouvée(s) mot pour mot</span>',
                    $word, $word, $counted['found'], $counted['total']);
            }
            $blocks .= sprintf(
                '<article class="section"><h3>%s%s <span class="level">%s</span></h3>%s<pre>%s</pre></article>',
                $section['group'] ? escape($section['group']) . ' › ' : '',
                escape($section['title']),
                escape($section['level']),
                $verdict,
                escape($section['text'])
            );
        }
    }

    $image = $trial['image']
        ? '<img src="/' . escape(substr($trial['image'], strlen($root) + 1)) . '" alt="">'
        : '<p class="missing">Pas d\'image : la génération n\'a rien livré dans ce dossier.</p>';

    $transmittedBlock = $transmitted === null
        ? '<p class="missing">Pas de consigne transmise : l\'agent ne l\'a pas rapportée. Sans elle, on ne peut pas distinguer une clause qui prescrivait mal '
            . 'd\'une clause perdue à sa reformulation.</p>'
        : '<pre class="whole">' . escape($transmitted) . '</pre>';

    $panels .= sprintf(
        '<section class="trial"><h2>%s</h2><div class="split"><div class="image">%s</div><div class="consigne">%s</div></div>'
        . '<h3 class="transmise">Ce que l\'agent a transmis à son modèle d\'images</h3>%s</section>',
        escape($trial['name']), $image, $blocks, $transmittedBlock
    );
}

$page = <<<'HTML'
<h1>L'atelier de génération</h1>
<p class="lede">{$tally}</p>
<p class="lede">Les essais vivent sous var/generations/trials/, qui n'est pas versionné : cette page liste ce qui existait quand elle a été construite, le
{$built}. Un essai nettoyé depuis reste lisible ici et disparaîtra à la construction suivante.</p>
{$reloadMarkup}
{$trials}
<style>
{$theme}
{$layout}
{$reloadStyles}
  .trial { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--trait); }
  .split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 1.5rem; align-items: start; }
  .image img { max-width: 100%; height: auto; image-rendering: pixelated; }
  .section { margin-bottom: 1rem; }
  .section h3 { margin: 0 0 .25rem; font-size: .95rem; font-weight: 600; }
  .level { font-weight: 400; opacity: .7; font-size: .85rem; }
  pre { white-space: pre-wrap; word-break: break-word; margin: 0; font-size: .82rem; line-height: 1.45; }
  .whole { max-height: 32rem; overflow: auto; }
  .survival { display: inline-block; font-size: .8rem; margin-bottom: .25rem; }
  .survival.intacte { color: #4f8a4f; }
  .survival.partielle { color: #a07a2a; }
  .survival.disparue { color: #a04a4a; }
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

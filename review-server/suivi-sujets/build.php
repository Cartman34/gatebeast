<?php
/**
 * Usage: php review-server/suivi-sujets/build.php [sortie.html] — builds the open-points page of the review server (RS), served at /sujets.
 *
 * Intention: what is left to do had no page. It lived as prose in SUIVI.md, where nothing could sort it or count it, and the operator had to read a long document to know what came next. The data
 * lives in review-server/subjects.json now, written only by scripts/backlog.php; this page is its reading, in priority order, open points first.
 *
 * The long description is Markdown and is rendered as such — a point that cannot say what it means in more than a label is a point nobody can pick up cold.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Backlog.php';
bootBuild();

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
$backlog = new Backlog($root);
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * Le Markdown d'une description, rendu au strict nécessaire : gras, code, titres de niveau trois, listes et paragraphes.
 *
 * ÉCRIT ICI PLUTÔT QU'EMPRUNTÉ : PHP n'embarque pas de lecteur Markdown, et en installer un est une dépendance à poser sur toute machine où le projet tourne — ce qui appartient à l'opérateur. Ce
 * qu'on écrit dans une description tient dans ces cinq marques ; le jour où ça déborde, c'est une bibliothèque qu'il faudra demander, pas une marque de plus à bricoler ici.
 */
function markdown(string $text): string
{
    $blocks = preg_split('/\n{2,}/', trim($text));
    $html = '';
    foreach ($blocks as $block) {
        $block = escape(trim($block));
        $block = preg_replace('/\*\*(.+?)\*\*/s', '<strong>$1</strong>', $block);
        $block = preg_replace('/`(.+?)`/s', '<code>$1</code>', $block);
        if (str_starts_with($block, '### ')) {
            $html .= '<h3>' . substr($block, 4) . "</h3>\n";
            continue;
        }
        if (preg_match('/^[-*] /', $block)) {
            $items = preg_split('/\n[-*] /', preg_replace('/^[-*] /', '', $block));
            $html .= "<ul>\n" . implode('', array_map(fn (string $i) => '<li>' . nl2br($i) . "</li>\n", $items)) . "</ul>\n";
            continue;
        }
        $html .= '<p>' . nl2br($block) . "</p>\n";
    }

    return $html;
}

$open = $backlog->ordered(true);
$closed = array_values(array_filter($backlog->ordered(), fn (array $p) => !in_array($p['status'], Backlog::OPEN_STATUSES, true)));

/** Une carte de point : sa référence, son libellé, ses métadonnées, puis sa description en entier. Rien n'est replié — cette page se lit pour savoir quoi faire, pas pour survoler. */
function card(array $point, int $rank = null): string
{
    return sprintf(
        '  <article class="point" data-statut="%s">' . "\n"
        . '    <p class="point-tete"><span class="point-ref">%s</span><span class="point-statut">%s</span>'
        . '<span class="point-prio">priorité %d</span><span class="point-attend">attend : %s</span>%s</p>' . "\n"
        . '    <h2>%s</h2>' . "\n"
        . '    <div class="point-corps">%s</div>' . "\n"
        . '    <p class="point-pied">Créé le %s · repris le %s</p>' . "\n"
        . "  </article>\n",
        escape($point['status']),
        escape($point['ref']),
        // L'ATTENDU SE LIT AVEC LE STATUT : une carte « en attente » qui ne dit pas de quoi oblige à ouvrir la description pour savoir si elle réclame quelque chose de l'opérateur.
        escape((Backlog::STATUS_LABELS[$point['status']] ?? $point['status']) . (isset($point['waits_on']) ? ' : ' . $point['waits_on'] : '')),
        $point['priority'], escape($point['waiting'] === Backlog::WAITING_OPERATOR ? 'opérateur' : 'agent'),
        $rank !== null ? sprintf('<span class="point-rang">%s</span>', $rank === 1 ? 'le prochain' : (string) $rank) : '',
        escape($point['label']), markdown($point['description']),
        escape($point['created']), escape($point['updated'])
    );
}

$openMarkup = '';
foreach ($open as $index => $point) {
    $openMarkup .= card($point, $index + 1);
}
$closedMarkup = '';
foreach ($closed as $point) {
    $closedMarkup .= card($point);
}

$page = <<<'HTML'
<title>Suivi des sujets</title>
{$favicon}

<style>
{$theme}
  body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 ui-sans-serif, system-ui, sans-serif; }
  .wrap { width: min(100%, 1100px); margin: 0 auto; padding: 24px 16px 96px; }
  h1 { margin: 0 0 4px; font-size: 1.6rem; }
  .lede { margin: 0 0 8px; color: var(--muted); max-width: 90ch; }
  .compte { margin: 0 0 24px; font-family: ui-monospace, monospace; font-size: .8rem; color: var(--muted); }
  .point { margin: 0 0 10px; padding: 12px 14px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; }
  .point h2 { margin: 6px 0 8px; font-size: 1.05rem; font-weight: 600; }
  .point-tete { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin: 0;
                font-family: ui-monospace, monospace; font-size: 10px; letter-spacing: .03em; color: var(--muted); }
  .point-ref { padding: 2px 7px; background: var(--bg); border: 1px solid var(--line); border-radius: 2px; color: var(--ink); font-weight: 700; }
  .point-rang { margin-left: auto; padding: 2px 7px; border: 1px solid var(--accent); border-radius: 2px; color: var(--accent); }
  .point-corps { font-size: .92rem; }
  .point-corps p { margin: 0 0 8px; }
  .point-corps ul { margin: 0 0 8px; padding-left: 20px; }
  .point-corps code { font-family: ui-monospace, monospace; font-size: .85em; color: var(--accent); }
  .point-pied { margin: 8px 0 0; font-size: .72rem; color: var(--muted); }
  /* LE STATUT SE VOIT AVANT D'ÊTRE LU : une pile où tout se ressemble oblige à lire chaque carte pour savoir laquelle bouge. */
  .point[data-statut="in-progress"] { border-left: 3px solid var(--accent); }
  .point[data-statut="pending-decision"] { border-left: 3px solid var(--state-rework-edge); }
  .point[data-statut="pending-dependency"] { border-left: 3px solid var(--muted); }
  .point[data-statut="waiting-external"] { border-left: 3px solid var(--state-dismissed-edge); }
  .point[data-statut="done"], .point[data-statut="dismissed"] { opacity: .55; }
  .clos { margin-top: 40px; }
  .clos summary { cursor: pointer; color: var(--muted); font-size: .9rem; }
{$reloadStyles}
</style>

<div class="wrap">
  <h1>Suivi des sujets</h1>
  <p class="lede">Ce qui reste à faire, dans l'ordre où je le dépile. Les points ouverts d'abord, du plus prioritaire au moins prioritaire ; à priorité égale, le plus ancien passe devant.
  Cette page se lit, elle ne s'édite pas : une seule commande écrit les points, et elle reconstruit la page en sortant.</p>
  <p class="compte">{$compte}</p>
{$ouverts}
  <details class="clos">
    <summary>Les points fermés</summary>
{$fermes}
  </details>
</div>
{$reloadMarkup}
{$reloadScript}
HTML;

$page = strtr($page, [
    '{$theme}' => $theme->css('encre'),
    '{$favicon}' => $favicon->tag(),
    '{$reloadStyles}' => $reload->styles(),
    '{$reloadMarkup}' => $reload->markup(),
    '{$reloadScript}' => $reload->script('/sujets'),
    '{$compte}' => sprintf('%d ouvert(s) · %d fermé(s) · php scripts/backlog.php next', count($open), count($closed)),
    '{$ouverts}' => $openMarkup !== '' ? $openMarkup : "  <p class=\"lede\">Aucun point ouvert.</p>\n",
    '{$fermes}' => $closedMarkup,
]);

file_put_contents($outputPath, $page);
printf("%s — %d point(s) ouvert(s), %d fermé(s), %.1f ko\n", $outputPath, count($open), count($closed), strlen($page) / 1024);

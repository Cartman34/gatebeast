<?php
/**
 * Usage: served at / by the local review server — never built, never written to disk.
 *
 * Intention: the door to every published artifact. It is the only dynamic page of this server (operator, 2026-08-07), and rightly so: an index has no content of its own, only the state of what it
 * lists, so building it ahead of time freezes a list that goes stale.
 *
 * WRITTEN AFTER A FAULT, and the fault is worth remembering: the first version was a NEW page — other content, other structure, other style — because "dynamic" was read as licence to redesign. It
 * says when a page is rendered, never what it shows. A conversion that changes what it converts can no longer be checked by comparing before and after, which is the one thing that made the whole
 * migration safe. Its markup and its style are therefore still, line for line, those of the Python builder it replaced.
 *
 * THE DATA COMES FROM review-server/artefacts.json, AND NOT FROM THE TRACKING DOCUMENT. It used to be read from a table in SUIVI.md, which is the agent's own working document: it is rewritten
 * constantly and has no business being a data source for an application (operator, 2026-08-07). The rules that govern the registry — the four states, what archiving means — stay in doc/artefacts.md,
 * which holds no values of its own. One datum, one place, and it is the place the tool reads from.
 */

$root = dirname(__DIR__);
$registryPath = __DIR__ . '/artefacts.json';
require_once __DIR__ . '/bootstrap.php';

// ONE WAY TO FAIL: every PHP error becomes an exception, and every uncaught exception becomes a readable page. The operator saw the browser's own blank "HTTP ERROR 500", which says nothing — the
// reader has to know whether the registry is broken or whether a file was simply caught half-written.
bootApp(static function (Throwable $fault): void {
    faultPage('Une faute a arrêté la construction de la page : ' . $fault->getMessage()
        . ' (' . basename($fault->getFile()) . ', ligne ' . $fault->getLine() . ').');
});

// Services are taken here, at the top, once.
$favicon = Favicon::get();
// THE HOME PAGE TAKES THE SAME THEME AS THE OTHERS (operator, 2026-08-11: « Sombre et appliqué partout »). It carried its own palette, in its own names, so the
// four review pages could not be changed together — which is exactly what a theme exists to prevent.
$theme = Theme::get();
$reload = Reload::get();

// The four states the registry documents, and the badge each one wears. Any other state in the data is an error told on the page, never a silent guess.
const CATEGORY_BADGES = ['alive' => 'Vivant', 'archived' => 'Archivé', 'closed' => 'Clos', 'forbidden' => 'À ne pas rouvrir'];

/**
 * HTML-escape exactly as the Python builder did, apostrophe included.
 *
 * PHP writes an apostrophe &#039; where Python writes &#x27;. The two render the same character, so nothing would be visible — but the two pages would then differ byte for byte, and the comparison
 * that proves the conversion faithful would be lost over a detail no reader can even see. The check is only worth anything while it is exact.
 */
function escape(string $text): string
{
    return str_replace('&#039;', '&#x27;', htmlspecialchars($text, ENT_QUOTES));
}

/**
 * Capitalize only the first letter of a displayed label, per the project's rule.
 *
 * A leading code span keeps its exact casing — the rule that carves out technical codes and addresses applies here too — so text starting with a backtick is left untouched.
 */
function capitalizeFirst(string $text): string
{
    if ($text === '' || $text[0] === '`') {
        return $text;
    }

    return mb_strtoupper(mb_substr($text, 0, 1)) . mb_substr($text, 1);
}

/**
 * Render the small subset of inline Markdown used in SUIVI.md: `code`, **bold**, *italic*.
 *
 * Everything else is HTML-escaped as plain text. Any Markdown-looking construct this function cannot render (a link, a strikethrough, an unmatched backtick) is left as escaped plain text but
 * reported in $warnings — a mark that isn't handled must be named, not silently passed through as if it were punctuation.
 */
function renderInlineMarkdown(string $text, string $location, array &$warnings): string
{
    $pattern = '/`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*/u';
    $rendered = preg_replace_callback($pattern, function (array $match): string {
        if (($match[1] ?? '') !== '') {
            return '<code>' . escape($match[1]) . '</code>';
        }
        if (($match[2] ?? '') !== '') {
            return '<strong>' . escape($match[2]) . '</strong>';
        }

        return '<em>' . escape($match[3]) . '</em>';
    }, escape($text));

    $remainder = preg_replace($pattern, '', $text);
    if (str_contains($remainder, '`')) {
        $warnings[] = "{$location} : accent grave non apparié dans « {$text} »";
    }
    if (preg_match('/\[[^\]]+\]\([^)]+\)/u', $remainder)) {
        $warnings[] = "{$location} : lien Markdown non rendu dans « {$text} »";
    }
    if (str_contains($remainder, '~~')) {
        $warnings[] = "{$location} : texte barré Markdown non rendu dans « {$text} »";
    }
    if (preg_match('/(?<!\w)_[^_]+_(?!\w)/u', $remainder)) {
        $warnings[] = "{$location} : emphase en tiret bas non rendue dans « {$text} »";
    }

    return $rendered;
}

/**
 * The page shown instead of the index when the registry has drifted — it names exactly what is missing rather than serve an empty or partial list.
 *
 * IT CARRIES THE RELOAD WATCHER, and that is the whole point (operator, 2026-08-07): a fault here is usually transient — a file caught half-written — and is fixed seconds later. But the browser was
 * then stranded on a dead page, because the watcher lived in the page that had failed to render. The error page now watches like any other, and comes back on its own once the fault is gone.
 */
function faultPage(string $message): never
{
    $reload = Reload::get();
    http_response_code(500);
    header('Content-Type: text/html; charset=utf-8');
    printf('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>GateBeast — Index</title><style>%s
body { margin: 0; padding: 2rem 1.5rem; background: #17151d; color: #eeecf3; font-family: system-ui, sans-serif; }</style></head>
<body><h1>Index</h1><p>%s</p><p>Cette page se recharge d\'elle-même dès que la faute est levée.</p>%s%s</body></html>',
        $reload->styles(), escape($message), $reload->markup(), $reload->script('/'));
    exit;
}

/**
 * Read the registry and return its artifacts, plus the entries that could not be used.
 *
 * A malformed entry does not stop the page: it is skipped and reported at the bottom, with what is wrong with it. A registry that cannot be read at all does stop it — an index silently emptied is
 * worse than no index, because nothing tells the reader that what he is looking at is not the truth.
 */
function loadArtifacts(string $registryPath): array
{
    if (!is_file($registryPath)) {
        throw new RuntimeException("'{$registryPath}' est introuvable — impossible de construire l'index des artefacts.");
    }
    // Aucun test de retour ici : une lecture qui échoue lève désormais, comme tout le reste. C'est ce que change « une seule façon d'échouer » — le code décrit le cas normal, les fautes remontent.
    $raw = file_get_contents($registryPath);
    $registry = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
    if (!isset($registry['artefacts']) || !is_array($registry['artefacts'])) {
        throw new RuntimeException("'{$registryPath}' ne porte pas de liste « artefacts » — format inattendu.");
    }

    $artifacts = [];
    $anomalies = [];
    $stateWarnings = [];
    foreach ($registry['artefacts'] as $rank => $entry) {
        $place = 'entrée ' . ($rank + 1);
        if (($entry['name'] ?? '') === '') {
            $anomalies[] = [$place, json_encode($entry, JSON_UNESCAPED_UNICODE), 'sans nom'];
            continue;
        }
        $state = $entry['state'] ?? '';
        if (!isset(CATEGORY_BADGES[$state])) {
            $anomalies[] = [$place, $entry['name'], "état « {$state} » inconnu — les seuls sont : " . implode(', ', array_keys(CATEGORY_BADGES))];
            continue;
        }
        $address = $entry['address'] ?? null;
        if ($address !== null && !str_starts_with($address, 'http://') && !str_starts_with($address, 'https://')) {
            $anomalies[] = [$place, $entry['name'], 'adresse qui ne commence ni par http:// ni par https://'];
            continue;
        }
        $artifacts[] = [
            'name' => $entry['name'],
            'description' => $entry['description'] ?? '',
            'address' => $address,
            'state' => $entry['state_text'] ?? CATEGORY_BADGES[$state],
            'category' => $state,
            'line' => $place,
        ];
    }

    if (!$artifacts) {
        throw new RuntimeException("Aucune entrée exploitable dans '{$registryPath}' (" . count($anomalies) . ' anormale(s)) — impossible de construire une page non vide.');
    }

    return [$artifacts, $anomalies, $stateWarnings];
}

/**
 * Where a card leads: the local address when this server serves the page, the published one otherwise.
 *
 * Intention: the index kept sending to claude.ai for pages that are served here (operator, 2026-08-07). A door that opens onto the old building is worse than no door — one clicks it without
 * noticing, and comments the wrong copy. The published address is not lost: it stays written in the registry, doc/artefacts.md, which is where an address belongs.
 *
 * THE MATCH IS ON THE NAME, and that is the weak point: an artifact renamed on one side and not the other stops matching. It fails loudly rather than quietly — a served page whose name matches no
 * artifact is reported at the bottom of this page, under "Signalé à la relecture".
 */
function localRoutes(): array
{
    // LE NOM DE L'INDEX EST ÉCRIT ICI ET AU REGISTRE, et le rapprochement se fait dessus : les deux se renomment dans le même geste, sinon la card perd son lien local sans un mot.
    $routes = ['Index' => '/'];
    foreach (require __DIR__ . '/pages.php' as $page) {
        $routes[$page['title']] = $page['route'];
    }

    return $routes;
}

/** One artifact as a self-contained card. The whole card is the link: an address written out took three lines and broke in the middle of an identifier, and nobody read it. */
function renderCard(array $artifact, array &$warnings): string
{
    $location = "{$artifact['name']} (ligne {$artifact['line']})";
    $nameHtml = renderInlineMarkdown(capitalizeFirst($artifact['name']), $location, $warnings);
    $descriptionHtml = $artifact['description'] === ''
        ? ''
        : '<p class="card-description">' . renderInlineMarkdown(capitalizeFirst($artifact['description']), $location, $warnings) . '</p>';
    $stateHtml = renderInlineMarkdown(capitalizeFirst($artifact['state']), $location, $warnings);
    $warningHtml = $artifact['category'] === 'forbidden' ? '<p class="card-warning">Ne jamais republier sur cette adresse.</p>' : '';
    $badgeHtml = '<span class="card-badge card-badge-' . $artifact['category'] . '">' . escape(CATEGORY_BADGES[$artifact['category']]) . '</span>';

    $local = localRoutes()[$artifact['name']] ?? null;
    $serviHtml = $local === null ? '' : '<p class="card-servi">Servie ici</p>';

    $inside = "  {$badgeHtml}\n  <h3 class=\"card-name\">{$nameHtml}</h3>\n  {$descriptionHtml}\n  <p class=\"card-state\">{$stateHtml}</p>\n  {$serviHtml}{$warningHtml}";

    if ($local !== null) {
        return "\n<a class=\"card card-{$artifact['category']}\" href=\"" . escape($local) . "\">\n{$inside}\n</a>";
    }

    if ($artifact['address'] === null) {
        return "\n<article class=\"card card-{$artifact['category']}\">\n{$inside}\n  <p class=\"card-address\"><span class=\"card-no-address\">pas encore ouvert</span></p>\n</article>";
    }

    return "\n<a class=\"card card-{$artifact['category']}\" href=\"" . escape($artifact['address']) . "\" target=\"_blank\" rel=\"noopener\">\n{$inside}\n</a>";
}

/** One category group — its heading plus its cards — or nothing if empty. */
function renderGroup(string $title, array $artifacts, string $groupClass, array &$warnings): string
{
    if (!$artifacts) {
        return '';
    }
    $cards = [];
    foreach ($artifacts as $artifact) {
        $cards[] = renderCard($artifact, $warnings);
    }
    $cardsHtml = implode("\n", $cards);

    return "\n<section class=\"group group-{$groupClass}\">\n  <h2 class=\"group-title\">" . escape($title) . "</h2>\n  <div class=\"group-cards\">\n    {$cardsHtml}\n  </div>\n</section>";
}

/** A notice listing lines that could not be read, or reading warnings. Nothing here blocks the page: a real drift in SUIVI.md must be noticed, not silently passed through. */
function renderNotice(string $title, array $items): string
{
    if (!$items) {
        return '';
    }
    $itemsHtml = implode("\n", $items);

    return "\n<section class=\"anomalies\">\n  <h2 class=\"anomalies-title\">" . escape($title) . "</h2>\n  <ul class=\"anomalies-list\">\n    {$itemsHtml}\n  </ul>\n</section>";
}

[$artifacts, $anomalies, $stateWarnings] = loadArtifacts($registryPath);
$markdownWarnings = $stateWarnings;

$byCategory = ['alive' => [], 'archived' => [], 'closed' => [], 'forbidden' => []];
foreach ($artifacts as $artifact) {
    $byCategory[$artifact['category']][] = $artifact;
}

// CHAQUE PAGE SERVIE EST JOIGNABLE DEPUIS L'INDEX, ET LA LISTE VIENT DU REGISTRE DES PAGES (opérateur, 2026-08-17 : « chaque page est accessible par
// l'index »). Cet index se construisait depuis le SEUL registre des artefacts publiés, si bien qu'une page pouvait être servie, répondre, et n'apparaître nulle
// part — c'est arrivé à /workshop, servie pendant quatre jours sans qu'aucun lien n'y mène. Les deux listes existent pour deux choses différentes et aucune
// n'est tenue à la main : `pages.php` dit ce qui est servi ici, `artefacts.json` ce qui est publié ailleurs.
//
// SEULES CELLES QUI MANQUENT SONT LISTÉES : une page déjà présente au registre porte déjà sa carte et son lien, et la répéter donnerait deux entrées pour une
// page — l'index cesserait de dire ce qu'il y a.
$known = [];
foreach ($artifacts as $artifact) {
    $known[$artifact['name']] = true;
}
$servedItems = '';
foreach (require __DIR__ . '/pages.php' as $page) {
    if (isset($known[$page['title']])) {
        continue;
    }
    $servedItems .= sprintf("\n<a class=\"card card-alive\" href=\"%s\">\n  <h3 class=\"card-name\">%s</h3>\n"
        . "  <p class=\"card-state\">Servie ici, et absente du registre des artefacts.</p>\n</a>",
        escape($page['route']), escape($page['title']));
}
$servedHtml = $servedItems === ''
    ? ''
    : "\n<section class=\"group group-alive\">\n  <h2 class=\"group-title\">Servies ici, et nulle part ailleurs</h2>\n  <div class=\"group-cards\">\n    "
        . $servedItems . "\n  </div>\n</section>";
$groupsHtml = $servedHtml
    . renderGroup('Vivants', $byCategory['alive'], 'alive', $markdownWarnings)
    . renderGroup('Archivés', $byCategory['archived'], 'archived', $markdownWarnings)
    . renderGroup('Clos', $byCategory['closed'], 'closed', $markdownWarnings)
    . renderGroup('À ne pas rouvrir', $byCategory['forbidden'], 'forbidden', $markdownWarnings);

$anomalyItems = [];
foreach ($anomalies as [$lineNumber, $rawLine, $reason]) {
    $anomalyItems[] = '<li>' . escape($lineNumber) . ' : ' . escape($reason) . ' — <code>' . escape($rawLine) . '</code></li>';
}
$warningItems = [];
foreach ($markdownWarnings as $warning) {
    $warningItems[] = '<li>' . escape($warning) . '</li>';
}
// A served page whose name matches no artifact in the registry: the match is made on the name, so renaming on one side only breaks the link to the local page and nothing else — the card would go
// on sending to the published page, silently. The fault is told here rather than discovered by clicking.
foreach (array_keys(localRoutes()) as $servedName) {
    foreach ($artifacts as $artifact) {
        if ($artifact['name'] === $servedName) {
            continue 2;
        }
    }
    $warningItems[] = '<li>' . escape("La page « {$servedName} » est servie ici mais ne correspond à aucun artefact du registre — sa carte mènera à la page publiée.") . '</li>';
}

$anomaliesHtml = renderNotice('Lignes ignorées dans SUIVI.md', $anomalyItems) . renderNotice('Signalé à la relecture', $warningItems);

header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>GateBeast — Index</title>
<?= $favicon->tag() ?>
<style>
<?= $theme->css('graphite') ?>
  /* THE HOME PAGE'S OWN NAMES, SAID IN THE SHARED ONES — nothing of its markup moves, only where its colours come from. It had its own palette in `--fg`,
     `--card-bg`, `--border` and five badge colours, so changing the review's dressing meant editing it twice and forgetting it once. Its names stay, because
     renaming them would be a rewrite; they simply point at the theme now, and the day the theme changes this page follows without being touched. */
  :root {
    --fg: var(--ink);
    --border: var(--line);
    --card-bg: var(--card);
    --warning-fg: var(--warn);
    --warning-bg: var(--warn-field);
    --warning-border: var(--warn);
    --alive-badge-bg: var(--state-validated);
    --alive-badge-fg: var(--state-validated-edge);
    --archived-badge-bg: var(--state-rework);
    --archived-badge-fg: var(--state-rework-edge);
    --closed-badge-bg: var(--card-sunk);
    --closed-badge-fg: var(--muted);
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 2rem 1.5rem 4rem;
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, sans-serif;
  }
  h1 {
    font-size: 1.6rem;
    margin: 0 0 0.25rem;
  }
  /* PAS DE PLAFOND DE LARGEUR SUR L'INTRODUCTION (opérateur, 2026-08-07) : bridée à 65 caractères, elle se repliait au tiers de l'écran et se lisait comme un retour forcé, alors que
     c'était un plafond de lisibilité hérité de la page d'origine. Elle suit désormais la largeur du contenu, comme les cards en dessous. */
  .page-intro {
    color: var(--muted);
    margin: 0 0 2.5rem;
  }
  .group {
    margin: 0 0 2.5rem;
  }
  .group-title {
    font-size: 1.15rem;
    margin: 0 0 1rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border);
  }
  .group-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }
  /* LA CARTE ENTIÈRE EST LE LIEN : on clique la carte, pas une adresse écrite en clair qui prenait trois lignes et se coupait au milieu d'un identifiant. */
  .card {
    display: block;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    background: var(--card-bg);
    color: inherit;
    text-decoration: none;
  }
  a.card:hover {
    border-color: var(--alive-badge-fg);
  }
  a.card:focus-visible {
    outline: 2px solid var(--alive-badge-fg);
    outline-offset: 2px;
  }
  .card-name {
    font-size: 1.05rem;
    margin: 0 0 0.4rem;
  }
  /* La description dit ce qu'est l'artefact, pas ce qu'il contient : elle se lit d'un coup d'œil sur une carte, et une carte n'est pas un paragraphe. Plus petite
     que le nom, et bornée en hauteur pour qu'une description longue ne fasse pas grandir sa carte au-dessus de ses voisines. */
  .card-description {
    color: var(--muted);
    font-size: 0.84rem;
    line-height: 1.45;
    margin: 0 0 0.6rem;
  }
  .card-address {
    margin: 0 0 0.35rem;
    word-break: break-all;
    font-size: 0.78rem;
  }
  .card-link {
    color: inherit;
  }
  .card-no-address {
    color: var(--muted);
    font-style: italic;
  }
  .card-state {
    color: var(--muted);
    font-size: 0.78rem;
    margin: 0;
  }
  /* Says the card leads here, not to the published page: without that word, two neighbouring cards open two different places with nothing to show for it. */
  .card-servi {
    color: var(--alive-badge-fg);
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.35rem 0 0;
  }

  /* The badge names the état on every card, so archivé and clos read apart even out of
     their section — a colored pill is a stronger, faster cue than opacity alone. */
  .card-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    margin: 0 0 0.55rem;
  }
  .card-badge-alive {
    background: var(--alive-badge-bg);
    color: var(--alive-badge-fg);
  }
  .card-badge-archived {
    background: var(--archived-badge-bg);
    color: var(--archived-badge-fg);
  }
  .card-badge-closed {
    background: var(--closed-badge-bg);
    color: var(--closed-badge-fg);
  }
  .card-badge-forbidden {
    background: var(--warning-border);
    color: var(--warning-fg);
  }

  /* Archived artifacts: still valid and consultable, just mildly receded — never confused
     with closed, which reads distinctly smaller and dimmer below. */
  .group-archived .card {
    opacity: 0.9;
  }

  /* Closed artifacts: kept, but visibly receded — smaller and dimmer than archived. */
  .group-closed .card {
    opacity: 0.68;
    padding: 0.75rem 0.9rem;
  }
  .group-closed .card-name {
    font-size: 0.95rem;
  }

  /* Forbidden artifacts: cannot be mistaken for a live one. */
  .group-forbidden .card {
    background: var(--warning-bg);
    border-color: var(--warning-border);
    color: var(--warning-fg);
  }
  .group-forbidden .card-description,
  .group-forbidden .card-state {
    color: var(--warning-fg);
    opacity: 0.85;
  }
  .group-forbidden .card-link {
    color: var(--warning-fg);
    text-decoration: line-through;
  }
  .card-warning {
    margin: 0.5rem 0 0;
    font-weight: 600;
    font-size: 0.85rem;
  }

  .anomalies {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px dashed var(--warning-border);
  }
  .anomalies-title {
    font-size: 1rem;
    color: var(--warning-fg);
    margin: 0 0 0.75rem;
  }
  .anomalies-list {
    margin: 0;
    padding-left: 1.2rem;
    color: var(--muted);
    font-size: 0.85rem;
  }
  .anomalies-list code {
    font-size: 0.85em;
  }
<?= $reload->styles() ?>
</style>
</head>
<body>
<h1>Index</h1>
<p class="page-intro">Une seule adresse à retenir : la porte d'entrée vers toutes les pages de revue du projet
GateBeast — celles qui sont servies ici et celles qui ont été publiées. Construite depuis deux registres et rien
d'autre : <code>review-server/artefacts.json</code> pour ce qui est publié, <code>review-server/pages.php</code>
pour ce qui est servi ici. Aucune page n'y est ajoutée à la main, et aucune ne peut manquer.</p>
<?= $groupsHtml ?>

<?= $anomaliesHtml ?>

<?= $reload->markup() ?>
<?= $reload->script('/') ?>
</body>
</html>

<?php
/**
 * USAGE
 *   php scripts/check-page-selectors.php [pages construites] — checks that every class, id and data- attribute the JavaScript of a built page looks for actually
 *   EXISTS in that page's markup. Without arguments it checks every built review page. Exits non-zero on any miss.
 *   php scripts/check-page-selectors.php -h|--help — this text
 *
 * INTENTION
 *   A SELECTOR THAT MATCHES NOTHING FAILS IN SILENCE, AND THAT IS THE WHOLE PROBLEM. `document.querySelectorAll('.tile')` returning an empty list throws no
 *   error, logs nothing, and leaves a page that looks perfectly built — only the button does nothing. On 2026-08-08 a vocabulary migration renamed the tile
 *   attribute to `data-subject` in the markup and left the handler reading `data-sujet`: the full-screen panel stopped opening on click, no console error, and
 *   it was the operator who found it. The same evening, three other renames had been caught only because they crashed something.
 *
 *   IT READS THE BUILT PAGE, NOT THE BUILDER, for the same reason as check-review-pages.php: what matters is what reaches the screen. And it needs no browser —
 *   comparing what the script asks for against what the markup carries is text against text, so it costs nothing and can run on every build.
 *
 *   IT ONLY REPORTS WHAT IS CERTAINLY ABSENT. A selector built at runtime by string concatenation is skipped rather than guessed at: this check must never cry
 *   wolf, or it will be switched off within a week like every noisy check before it.
 */

$root = dirname(__DIR__);
require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$pages = $argv;
array_shift($pages);
if (!$pages) {
    $pages = glob($root . '/review-server/*/page.html') ?: [];
}

$faults = [];
foreach ($pages as $path) {
    if (!is_file($path)) {
        fwrite(STDERR, "FAULT page introuvable : {$path}\n");
        exit(1);
    }
    $html = file_get_contents($path);
    $relative = str_replace($root . '/', '', $path);

    // What the markup actually carries. Data attributes are collected by name alone: the name is what gets renamed, never the value.
    preg_match_all('/\bclass="([^"]*)"/', $html, $found);
    $classes = [];
    foreach ($found[1] as $list) {
        foreach (preg_split('/\s+/', trim($list)) as $one) {
            if ($one !== '') {
                $classes[$one] = true;
            }
        }
    }
    preg_match_all('/\bid="([^"]+)"/', $html, $found);
    $ids = array_fill_keys($found[1], true);
    preg_match_all('/\s(data-[a-z0-9-]+)=/i', $html, $found);
    $data = array_fill_keys(array_map('strtolower', $found[1]), true);

    // WHAT THE SCRIPT MAKES ITSELF COUNTS AS PRESENT. A page sets markers at run time — `setAttribute('data-marque', ...)`, `classList.add(...)` — and those
    // names obviously do not exist in the built markup. Reporting them would be exactly the crying wolf that gets a check switched off: three false positives
    // appeared on the first run, on the Campagne page, all of them created at run time.
    preg_match_all("/setAttribute\('(data-[a-z0-9-]+)'/i", $html, $made);
    foreach ($made[1] as $name) {
        $data[strtolower($name)] = true;
    }
    preg_match_all("/(?:classList\.(?:add|toggle|remove)|className\s*=)\s*\(?'([a-z0-9 _-]+)'/i", $html, $made);
    foreach ($made[1] as $list) {
        foreach (preg_split('/\s+/', trim($list)) as $one) {
            if ($one !== '') {
                $classes[$one] = true;
            }
        }
    }

    // WHAT THE SCRIPT ASKS FOR, and only when it asks in PLAIN TEXT: a literal string handed to querySelector, querySelectorAll, getAttribute or closest. A
    // selector assembled by concatenation is skipped — it cannot be verified here, and guessing at it would make the check cry wolf.
    preg_match_all("/querySelector(?:All)?\('([^']+)'\)/", $html, $selectors);
    foreach ($selectors[1] as $selector) {
        foreach (preg_split('/\s*,\s*/', $selector) as $one) {
            if (preg_match_all('/\.([a-z][a-z0-9_-]*)/i', $one, $names)) {
                foreach ($names[1] as $name) {
                    if (!isset($classes[$name])) {
                        $faults[] = "  {$relative} : le script cherche la classe « .{$name} », absente du balisage";
                    }
                }
            }
            if (preg_match('/^#([a-z][a-z0-9_-]*)$/i', $one, $name) && !isset($ids[$name[1]])) {
                $faults[] = "  {$relative} : le script cherche l'identifiant « #{$name[1]} », absent du balisage";
            }
            if (preg_match_all('/\[(data-[a-z0-9-]+)[\]=]/i', $one, $names)) {
                foreach ($names[1] as $name) {
                    if (!isset($data[strtolower($name)])) {
                        $faults[] = "  {$relative} : le script cherche l'attribut « {$name} », absent du balisage";
                    }
                }
            }
        }
    }
    preg_match_all("/getAttribute\('(data-[a-z0-9-]+)'\)/i", $html, $asked);
    foreach (array_unique($asked[1]) as $name) {
        if (!isset($data[strtolower($name)])) {
            $faults[] = "  {$relative} : le script lit l'attribut « {$name} », qu'aucun élément ne porte";
        }
    }
}

if ($faults) {
    $faults = array_values(array_unique($faults));
    // UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`), et ici les deux causes appellent des gestes opposés — dire laquelle est la moitié du
    // travail. Le sélecteur a été renommé d'un côté seulement, ou le balisage qu'il visait a disparu : réparer le mauvais des deux déplace le défaut.
    fwrite(STDERR, count($faults) . " sélecteur(s) sans cible :\n" . implode("\n", $faults) . "\n"
        . "\nUn sélecteur qui ne trouve rien ne lève aucune erreur : le bouton ne fait simplement plus rien.\n"
        . "  Solution — ouvrir le balisage nommé ci-dessus et chercher ce que le sélecteur visait : ou bien il a été renommé d'un seul côté, et c'est le\n"
        . "  script qui suit ; ou bien l'élément a disparu, et c'est le comportement qu'il faut rebrancher, pas le sélecteur qu'il faut adapter.\n"
        . "  Reconstruire la page d'abord — « php review-server/build.php <route> » —, car un balisage périmé donne des cibles qui n'existent plus.\n");
    exit(1);
}

printf("%d page(s) : chaque sélecteur du script trouve sa cible dans le balisage.\n", count($pages));

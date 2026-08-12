<?php
/**
 * USAGE
 *   php scripts/check-asset-theme.php — checks the asset theme is honoured: no theme name written outside the module that owns it, every recorded image sitting under the current theme's subtree,
 *   and a coverage report saying how complete the theme is. Exits non-zero on a defect.
 *   php scripts/check-asset-theme.php -h|--help — this text
 *
 * INTENTION
 *   A theme answers for the whole game or it is not the current theme, and the current one is chosen in one place in the code (operator, 2026-08-07). Neither half of that holds by itself: a theme
 *   name copied into a second file makes the switch a lie, and a theme missing subjects makes the mock-ups silently fall back to nothing. Both are invisible until an image is missing from a scene.
 *
 *   COMPLETENESS IS REPORTED, NOT REFUSED, FOR THE LEGACY THEME. gb-gen is in production and known incomplete — twenty-one path shapes are still to be drawn. Failing on it would make this check
 *   useless from its first run, so it states the coverage and only fails a theme that claims to be current while missing subjects, which is what the rule is actually about.
 */

$root = dirname(__DIR__);
require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

/** Le module qui détient la valeur. C'est le SEUL fichier où un nom de thème a le droit d'être écrit. */
const THEME_MODULE = 'scripts/asset_theme.py';

/** Là où un nom de thème écrit en dur serait un défaut : le code, jamais la documentation, qui a le droit de nommer ce qu'elle décrit. */
const SCANNED_TREES = ['scripts', 'review-server'];

/** Ce qu'on lit dans le module pour ne pas le recopier ici : la valeur courante, celle du thème historique, et les thèmes déclarés. */
function themeNames(string $root): array
{
    $source = file_get_contents($root . '/' . THEME_MODULE);
    if (!preg_match("/^CURRENT = '([^']+)'/m", $source, $current)) {
        throw new RuntimeException('FAULT ' . THEME_MODULE . " ne déclare plus de thème courant — le contrôle ne sait plus sur quoi porter.");
    }
    preg_match("/^LEGACY = '([^']+)'/m", $source, $legacy);
    preg_match_all("/^\s*'([a-z0-9-]+)':/m", $source, $declared);

    return [$current[1], $legacy[1] ?? $current[1], array_unique($declared[1])];
}

/** Les fichiers de code où un nom de thème ne doit pas apparaître. */
function scannedFiles(string $root): array
{
    $files = [];
    foreach (SCANNED_TREES as $tree) {
        $walk = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
        foreach ($walk as $file) {
            if ($file->isFile() && in_array($file->getExtension(), ['php', 'py', 'sh', 'js', 'html'], true)) {
                $files[] = $file->getPathname();
            }
        }
    }

    return $files;
}

[$current, $legacy, $declared] = themeNames($root);
$faults = [];

// 1. AUCUN NOM DE THÈME HORS DE SON MODULE. C'est ce qui rend la bascule vraie : changer une ligne doit suffire.
foreach (scannedFiles($root) as $file) {
    $relative = substr($file, strlen($root) + 1);
    if ($relative === THEME_MODULE) {
        continue;
    }
    $content = file_get_contents($file);
    foreach ($declared as $name) {
        if (str_contains($content, "'{$name}'") || str_contains($content, "\"{$name}\"")) {
            $faults[] = "le thème « {$name} » est écrit en dur dans {$relative} — seul " . THEME_MODULE . ' a le droit de le nommer';
        }
    }
}

// 2. TOUTE IMAGE INSCRITE VIT SOUS LE SOUS-ARBRE DU THÈME COURANT. Le thème historique n'en a pas : ses images sont sous leur type, directement.
$subtree = $current === $legacy ? '' : $current;
$data = json_decode(file_get_contents($root . '/assets/subjects.json'), true, 512, JSON_THROW_ON_ERROR);
$recorded = 0;
$offTheme = [];
$variants = 0;
$drawn = 0;
foreach ($data['subjects'] as $code => $subject) {
    foreach ($subject['variants'] ?? [] as $variant) {
        $variants++;
        $has = false;
        foreach ($variant['representations'] ?? [] as $representation) {
            $path = $representation['path'] ?? '';
            $recorded++;
            $has = true;
            // Le chemin est relatif à assets/ : cutout/<sous-arbre>/<type>/… Un sous-arbre vide veut dire « directement sous le type ».
            if ($subtree !== '' && !str_contains($path, '/' . $subtree . '/')) {
                $offTheme[] = "{$code} — {$path}";
            }
        }
        $drawn += $has ? 1 : 0;
    }
}
foreach (array_slice($offTheme, 0, 10) as $one) {
    $faults[] = "hors du thème courant : {$one}";
}

// 3. LA COMPLÉTUDE. Un thème répond pour tout le jeu ou il n'est pas le thème courant — mais le thème historique est en production et incomplet, donc on le dit sans refuser.
$missing = $variants - $drawn;
if ($missing > 0 && $current !== $legacy) {
    $faults[] = "le thème « {$current} » se dit courant alors qu'il manque {$missing} variant(s) sur {$variants} — un thème répond pour tout le jeu ou il n'est pas le thème courant";
}

if ($faults) {
    fwrite(STDERR, count($faults) . " défaut(s) sur le thème des sprites :\n  " . implode("\n  ", $faults) . "\n");
    exit(1);
}

printf("Thème « %s » : %d image(s) inscrite(s), %d variant(s) dessiné(s) sur %d%s.\n",
    $current, $recorded, $drawn, $variants, $missing > 0 ? sprintf(', %d à produire', $missing) : '');

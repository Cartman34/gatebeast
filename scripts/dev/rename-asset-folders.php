<?php
/**
 * USAGE
 *   php scripts/dev/rename-asset-folders.php --dry-run — what would move and what would be rewritten, without touching anything.
 *   php scripts/dev/rename-asset-folders.php --apply — renames the folders with `git mv` and rewrites every recorded path in the same gesture.
 *   php scripts/dev/rename-asset-folders.php -h|--help — this text, and nothing moves.
 *
 * INTENTION
 *   THE IMAGE FOLDERS CARRY FRENCH NAMES, AND EVERYTHING THE MACHINE READS IS ENGLISH (`S80 dossiers-en-anglais`). Four of the six are French — `batiment`,
 *   `cloture`, `personnage`, `sol` — while `vegetation` and `creature` happen to be spelled the same in both languages and do not move.
 *
 *   RENAMING AND REWRITING ARE ONE GESTURE, NEVER TWO. Six hundred and sixty-five files change address, and their paths are recorded in the referential, in the
 *   judgements, in the thumbnails, in the OPERATOR'S REMARKS — which are filed BY IMAGE PATH — and in the frozen consigne beside each master. A rename that
 *   forgets one of those does not fail: it silently detaches a verdict from its image, or a sprite from the text that produced it, and nothing says so.
 *
 *   IT IS REPLAYABLE AND IT DRY-RUNS FIRST, because a hundred and eighty renames cannot be checked by reading a diff. The dry run prints exactly what the apply
 *   would do; the apply refuses to start on a dirty working tree, so that `git status` afterwards is a true account of what this script did and of nothing else.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

/**
 * The folders that move, and what they become. `vegetation` and `creature` are already English and are absent on purpose.
 *
 * THE KEY IS ALSO A TYPE OF `asset_common.TYPES`, whose keys serve as folder names when a master is shot: the two tables must move together, in this one
 * gesture, or the chain would write into a folder that no longer exists.
 */
const FOLDERS = [
    'batiment' => 'building',
    'cloture' => 'fence',
    'personnage' => 'character',
    'sol' => 'ground',
];
/** The layout family carried by those types, French like them. */
const FAMILIES = ['tuile' => 'tile'];
/** Where images live, under `assets/`. */
const HOMES = ['cutout', 'poc'];
/**
 * Where citations are looked for. NOT WHICH FILES — a hand-held list keeps a dead path in whatever it forgot, silently (operator, 2026-08-19: « aucun fichier
 * n'est à analyser en dur, ça n'a aucun sens »).
 *
 * ITS FIRST VERSION HELD ELEVEN NAMES AND MISSED ONE: `scripts/build-fence-geometry-svg.py` cites the image it took its measurements from, in a comment, and
 * that citation would have stayed dead — `check-tools.php` caught it after the fact. What is swept is now discovered, and the sweep is what makes the rename
 * one gesture instead of a list to maintain.
 */
const SEARCHED_TREES = ['assets', 'scripts', 'review-server', 'doc'];
/** Extensions that can carry a path. Images and archives are skipped: they are what MOVES, never what names. */
const SEARCHED_EXTENSIONS = ['json', 'php', 'py', 'md', 'sh', 'js', 'css', 'txt'];
/** Not swept: unversioned by design, or the images themselves. */
const SKIPPED = ['assets/cutout', 'assets/poc', 'assets/maquette', 'var', 'local'];
/**
 * Two files that carry the old names ON PURPOSE and must keep them.
 *
 * The session journal cites what existed the day it was written — rewriting it would falsify the record it exists to hold. This script itself carries both
 * names, in the very table that maps one to the other.
 */
const KEPT = ['doc/journal-des-seances.md', 'scripts/dev/rename-asset-folders.php'];

$apply = in_array('--apply', $argv, true);
$dry = in_array('--dry-run', $argv, true);
if (!$apply && !$dry) {
    fwrite(STDERR, "USAGE : php scripts/dev/rename-asset-folders.php --dry-run | --apply\n"
        . "  Solution — commencer par « --dry-run », qui ne touche à rien et imprime ce que « --apply » ferait.\n");
    exit(2);
}

if ($apply) {
    exec('git -C ' . escapeshellarg($root) . ' status --porcelain', $status);
    if ($status !== []) {
        fwrite(STDERR, "FAULT l'arbre de travail n'est pas propre, et ce renommage doit être le seul changement qu'il porte.\n"
            . "  Solution — enregistrer ou remiser ce qui est en cours, puis relancer : « git status » après coup doit rendre compte de ce script et de rien\n"
            . "  d'autre, sinon personne ne pourra relire cent quatre-vingts renommages.\n");
        exit(1);
    }
}

$moves = [];
foreach (HOMES as $home) {
    foreach (FOLDERS as $french => $english) {
        $from = "assets/$home/$french";
        if (is_dir($root . '/' . $from)) {
            $moves[] = [$from, "assets/$home/$english"];
        }
    }
}

printf("%d répertoire(s) à renommer :\n", count($moves));
foreach ($moves as [$from, $to]) {
    $count = iterator_count(new FilesystemIterator($root . '/' . $from, FilesystemIterator::SKIP_DOTS));
    printf("  %s → %s (%d fichier(s))\n", $from, $to, $count);
}

/** Every file of the swept trees that could carry a path — discovered, never listed. */
function searched(string $root): array
{
    $found = [];
    foreach (SEARCHED_TREES as $tree) {
        if (!is_dir($root . '/' . $tree)) {
            continue;
        }
        $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $file) {
            if (!$file->isFile() || !in_array($file->getExtension(), SEARCHED_EXTENSIONS, true)) {
                continue;
            }
            $relative = substr($file->getPathname(), strlen($root) + 1);
            if (in_array($relative, KEPT, true)) {
                continue;
            }
            foreach (SKIPPED as $skipped) {
                if (str_starts_with($relative, $skipped . '/')) {
                    continue 2;
                }
            }
            $found[] = $relative;
        }
    }
    sort($found);

    return $found;
}

$rewrites = [];
foreach (searched($root) as $relative) {
    $body = file_get_contents($root . '/' . $relative);
    $hits = 0;
    foreach (HOMES as $home) {
        foreach (FOLDERS as $french => $english) {
            // THE TRAILING SLASH IS OPTIONAL, and forgetting that missed a citation. A comment naming « assets/poc/sol » at the end of a sentence carries no
            // slash after it, and would have kept the dead name — the exact silent leftover this script exists to prevent.
            $hits += preg_match_all('~\b' . preg_quote("$home/$french", '~') . '(?![\p{L}\d_-])~u', $body);
        }
    }
    if ($hits > 0) {
        $rewrites[$relative] = $hits;
    }
}

printf("\n%d fichier(s) portant des chemins à réécrire :\n", count($rewrites));
foreach ($rewrites as $relative => $hits) {
    printf("  %s — %d occurrence(s)\n", $relative, $hits);
}

if (!$apply) {
    printf("\nRien n'a été touché. « --apply » exécute ce qui précède.\n");
    exit(0);
}

foreach ($moves as [$from, $to]) {
    exec('git -C ' . escapeshellarg($root) . ' mv ' . escapeshellarg($from) . ' ' . escapeshellarg($to) . ' 2>&1', $output, $code);
    if ($code !== 0) {
        fwrite(STDERR, "FAULT le renommage « $from » → « $to » a échoué : " . implode(' ', $output) . "\n"
            . "  Solution — les renommages déjà faits sont dans l'index : « git status » les montre, et « git reset --hard » revient en arrière.\n");
        exit(1);
    }
}

$changed = 0;
foreach (array_keys($rewrites) as $relative) {
    $path = $root . '/' . $relative;
    $body = file_get_contents($path);
    foreach (HOMES as $home) {
        foreach (FOLDERS as $french => $english) {
            $body = preg_replace('~\b' . preg_quote("$home/$french", '~') . '(?![\p{L}\d_-])~u', "$home/$english", $body);
        }
    }
    file_put_contents($path, $body);
    $changed++;
}

// THE TWO TABLES OF `asset_common.py` CARRY THE SAME NAMES AS FOLDERS, and they are what the chain reads to decide where to write. They move here, in the same
// run, because a folder renamed without them would be written into under its old name at the very next generation.
$commonPath = $root . '/scripts/asset_common.py';
$common = file_get_contents($commonPath);
foreach (FOLDERS as $french => $english) {
    $common = str_replace('"' . $french . '"', '"' . $english . '"', $common);
}
foreach (FAMILIES as $french => $english) {
    $common = str_replace('"' . $french . '"', '"' . $english . '"', $common);
}
file_put_contents($commonPath, $common);

printf("\n%d répertoire(s) renommé(s), %d fichier(s) réécrit(s), et les tables de asset_common.py avec eux.\n", count($moves), $changed);
printf("  À lancer maintenant — « python3 scripts/check-subjects.py », « php scripts/check-cited-paths.php » et « bash scripts/diff-prompts.sh »,\n");
printf("  ce dernier disant si une consigne a bougé, ce qui ne doit PAS arriver.\n");

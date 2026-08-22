<?php
/**
 * USAGE
 *   php scripts/check-implemented-coverage.php — every versioned command, page, service and guard of the repository is named somewhere under doc/implemented/,
 *   or belongs to a family that folder declares as covered wholesale. Exit code 0 while that holds, 1 otherwise.
 *   php scripts/check-implemented-coverage.php -v — each uncovered file, grouped by directory.
 *   php scripts/check-implemented-coverage.php -h|--help — this text.
 *
 * INTENTION
 *   A DOCUMENTATION OF WHAT EXISTS DRIFTS SILENTLY, AND THIS REPOSITORY HAS THE RECEIPT: the tool map named three deleted scripts for weeks, and nobody saw it
 *   (`W22 audit-journal`). Nothing compared it to the disk, because the only check that read documents — `check-cited-paths.php` — verifies that a link leads
 *   somewhere, never that what it says is still true.
 *
 *   IT CHECKS COVERAGE, NOT ACCURACY, and says so plainly. A file named in a document may be described wrongly and this will not see it; what it does see is the
 *   ONE fault a machine can catch — a command that exists and that no document mentions at all. That is the fault which grows: a file nobody documented is a
 *   file nobody will document, and in a year it is read by nobody either.
 *
 *   THE WHOLESALE FAMILIES ARE READ FROM THE DOCUMENTATION, NEVER WRITTEN HERE. `doc/implemented/index.md` carries a table naming each family and its pattern;
 *   this reads that table. An exemption hidden in the tool is an exemption nobody re-reads — and the whole point of the folder is that what it does not cover is
 *   stated where it can be argued with.
 *
 *   IT READS WHAT GIT TRACKS, and only that. A file under `local/` or `var/` belongs to nobody outside this machine and documenting it would be documenting a
 *   scratchpad.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);
$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);

$home = $root . '/doc/implemented';
if (!is_dir($home)) {
    fwrite(STDERR, "FAUTE le dossier « doc/implemented » est absent : il n'y a rien à confronter.\n"
        . "  Solution — l'écrire, en commençant par son index ; le point « S104 doc-implemented » dit ce qu'il doit porter.\n");
    exit(1);
}

$documents = glob($home . '/*.md') ?: [];
$said = '';
foreach ($documents as $path) {
    $said .= file_get_contents($path) . "\n";
}

/**
 * THE FAMILIES COVERED WHOLESALE, read from the index's own table. A row of that table names the family, then its patterns between backticks — and it is those
 * patterns that are honoured here. Writing them in this file instead would hide, inside a tool, the decision not to document something.
 */
$families = [];
foreach (explode("\n", file_get_contents($home . '/index.md')) as $line) {
    if (!str_starts_with($line, '|') || !str_contains($line, '`')) {
        continue;
    }
    $cells = array_map('trim', explode('|', $line));
    if (count($cells) < 4) {
        continue;
    }
    preg_match_all('~`([^`]+)`~', $cells[2], $found);
    foreach ($found[1] as $pattern) {
        $families[$pattern] = $cells[1];
    }
}
if ($families === []) {
    fwrite(STDERR, "FAUTE « doc/implemented/index.md » ne déclare aucune famille couverte en bloc, et ce contrôle en dépend.\n"
        . "  Solution — y rétablir le tableau « Ce qui est couvert en bloc », dont la deuxième colonne porte les motifs entre accents graves.\n");
    exit(1);
}

/** What has to be covered: the versioned files a person could be asked to work on. Data, assets and documents are not commands and describe themselves. */
const COVERED = ['scripts/', 'review-server/'];
const KINDS = ['php', 'py', 'sh'];

exec('git -C ' . escapeshellarg($root) . ' ls-files', $tracked);
$uncovered = [];
$byFamily = [];
$read = 0;
foreach ($tracked as $relative) {
    $inScope = false;
    foreach (COVERED as $where) {
        $inScope = $inScope || str_starts_with($relative, $where);
    }
    if (!$inScope || !in_array(pathinfo($relative, PATHINFO_EXTENSION), KINDS, true)) {
        continue;
    }
    $read++;
    if (str_contains($said, basename($relative))) {
        continue;
    }
    $covered = null;
    foreach ($families as $pattern => $name) {
        if (fnmatch($pattern, $relative) || fnmatch($pattern, basename($relative))) {
            $covered = $name;
            break;
        }
    }
    if ($covered !== null) {
        $byFamily[$covered] = ($byFamily[$covered] ?? 0) + 1;
        continue;
    }
    $uncovered[dirname($relative)][] = basename($relative);
}

printf("%d fichier(s) à couvrir, dans %d document(s) de doc/implemented/.\n", $read, count($documents));
foreach ($byFamily as $name => $count) {
    printf("  couverts en bloc — %-28s %3d\n", $name, $count);
}

$total = array_sum(array_map('count', $uncovered));
printf("\n%d fichier(s) que rien ne nomme.\n", $total);
if ($total === 0) {
    exit(0);
}
foreach ($uncovered as $where => $names) {
    printf("  %-24s %3d\n", $where . '/', count($names));
    if ($detail) {
        foreach ($names as $name) {
            printf("      %s\n", $name);
        }
    }
}
echo "\n  Solution — dire ce que fait chacun dans le nœud de doc/implemented/ qui le concerne, ou, si c'est une famille entière qui n'a rien à\n"
    . "  apprendre une par une, l'ajouter au tableau « Ce qui est couvert en bloc » de doc/implemented/index.md — avec la raison.\n";
if (!$detail) {
    echo "  « -v » les nomme.\n";
}

exit(1);

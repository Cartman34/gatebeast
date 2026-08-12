<?php
/**
 * USAGE
 *   php scripts/check-cited-paths.php        the verdict: how many paths the versioned documents name that do not exist
 *   php scripts/check-cited-paths.php -v     each dead citation, with the document and the line that carries it
 *   php scripts/check-cited-paths.php -h     this text
 *
 * INTENTION
 *   A DOCUMENT THAT NAMES A FILE WHICH IS NOT THERE SENDS ITS READER NOWHERE, and it does so with authority — the reader assumes the tool exists and looks for
 *   his own mistake. The repository already holds the rule (« un fichier cité doit être versionné, sinon la référence est morte pour tout le monde »); nothing
 *   held it. Fifty-four tools changed directory on 2026-08-12 and their citations had to be rewritten by hand, which is exactly the kind of pass that leaves one
 *   behind.
 *
 *   IT READS THE DOCUMENTS, NOT THE CODE: a path written in a comment or a sentence is a promise made to a human, and it is that promise this checks.
 *
 *   THE CODE HAS ITS OWN READER, AND THE TWO ARE NOT A DUPLICATE — said here so that nobody merges them in six months believing they are. `scripts/check-tools.php`
 *   judges the paths a COMMAND names, in its header and in its body: there a dead path does not mislead, it CRASHES. Two natures of fault, so two sets of rules,
 *   legitimately different — this one tolerates the generic and the illustrative, which the code's reader cannot afford. Merging them would mean giving one of
 *   the two the other's tolerance.
 *
 *   WHAT IT DELIBERATELY IGNORES: anything under var/ and local/, which are unversioned by design and whose absence is normal; and a path carrying a wildcard or
 *   a placeholder, which names a family rather than a file.
 */

$root = dirname(__DIR__);
$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    foreach (array_slice(file(__FILE__, FILE_IGNORE_NEW_LINES), 2, 5) as $line) {
        echo trim(preg_replace('~^\s*\*\s?~', '', $line)), "\n";
    }
    exit(0);
}

/** The documents a human reads, and where they live. Code is not swept: a wrong path there is a fault the program raises by itself. */
const DOCUMENTS = ['SUIVI.md', 'PLAN-ACTION.md', 'CLAUDE.md'];
const DOCUMENT_TREES = ['doc'];
/** Unversioned by design: what they hold comes and goes, and its absence proves nothing. */
const TRANSIENT = ['var/', 'local/'];

$files = [];
foreach (DOCUMENTS as $name) {
    if (is_file($root . '/' . $name)) {
        $files[] = $name;
    }
}
foreach (DOCUMENT_TREES as $tree) {
    $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
    foreach ($iterator as $file) {
        if ($file->isFile() && $file->getExtension() === 'md') {
            $files[] = substr($file->getPathname(), strlen($root) + 1);
        }
    }
}
sort($files);

$dead = [];
$seen = 0;
foreach ($files as $relative) {
    foreach (file($root . '/' . $relative, FILE_IGNORE_NEW_LINES) as $number => $line) {
        // TWO FORMS PROMISE A FILE, AND ONLY THEM: the TARGET of a markdown link, and a path inside backticks. The visible LABEL of a link is prose — reading it
        // as a citation reported eight dead paths that were only shortened for display, the label naming a tail of the very path its target spells in full.
        preg_match_all('~\]\(([^)]+)\)~', $line, $links);
        preg_match_all('~`([^`]+)`~', $line, $quoted);
        $candidates = [];
        foreach (array_merge($links[1], $quoted[1]) as $piece) {
            // A CITATION CARRIES A DIRECTORY. A bare `hook-stop.php` in a sentence is a NAME, not an address: it tells the reader which tool is being discussed,
            // not where to find it, and checking it as a path reported a hundred false deaths in one journal.
            $piece = trim($piece);
            if (str_contains($piece, '/') && preg_match('~^[A-Za-z0-9_./-]+\.(?:php|py|sh|json|md|css|js|png)$~', $piece) === 1) {
                $candidates[] = $piece;
            }
        }
        foreach ($candidates as $cited) {
            if (str_contains($cited, '*') || str_contains($cited, '<')) {
                continue;
            }
            foreach (TRANSIENT as $transient) {
                if (str_starts_with($cited, $transient)) {
                    continue 2;
                }
            }
            $seen++;
            // A MARKDOWN LINK IS RELATIVE TO ITS OWN DOCUMENT, and reading every path from the repository root reported twelve dead citations that all resolve:
            // doc/conception/referentiels/visuel/assets/lots-de-variantes.md is cited as plain `assets/…` from its own directory. Both readings are tried, and
            // only a path that resolves under NEITHER is dead.
            $beside = dirname($relative) . '/' . $cited;
            if (!is_file($root . '/' . $cited) && !is_file($root . '/' . $beside)) {
                $dead[] = sprintf('%s:%d — « %s »', $relative, $number + 1, $cited);
            }
        }
    }
}

printf("%d chemin(s) cité(s) dans %d document(s) : %d ne mène(nt) nulle part.\n", $seen, count($files), count($dead));
if ($detail) {
    foreach ($dead as $line) {
        printf("  %s\n", $line);
    }
} elseif ($dead) {
    echo "« -v » les nomme.\n";
}

exit($dead ? 1 : 0);

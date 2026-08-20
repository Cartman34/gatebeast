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

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);
$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);

/**
 * Where the documents are looked for. NOT WHICH ONES — the list of documents is not written anywhere (operator, 2026-08-19: « aucun fichier n'est à analyser en
 * dur, ça n'a aucun sens »).
 *
 * A HAND-HELD LIST OF FILES STOPS BEING TRUE THE DAY A FILE IS RENAMED, AND NOTHING SAYS SO. This check held three names, one of which — `CLAUDE.md` — had just
 * been deleted: it would have swept a document that no longer exists, silently, since an absent file was not a fault here. And a document added tomorrow would
 * never have been swept at all. Every `.md` of these trees is read, whatever it is called.
 */
const DOCUMENT_TREES = ['.', 'doc'];
/** Unversioned by design: what they hold comes and goes, and its absence proves nothing. */
const TRANSIENT = ['var/', 'local/'];
/** Not swept, and each for its own reason: unversioned by design, or not a document of this project. */
const SKIPPED_TREES = ['var', 'local', 'node_modules', 'vendor', '.git', 'assets'];
/**
 * A DOCUMENT OF RECORD CITES WHAT EXISTED THE DAY IT WAS WRITTEN, and that is its whole nature — the session journal names tools, images and referentials that
 * have since been renamed or removed, and rewriting it to keep this check green would falsify the record it exists to hold.
 *
 * IT IS NAMED BY WHAT IT IS, NOT BY ITS PATH: a check that stays red forever stops being read, which is exactly the fault this file was written to prevent in
 * others. Four dead citations sat in it permanently, so the verdict was « 4 ne mènent nulle part » on a healthy repository, every single day.
 */
const RECORDS = ['doc/journal-des-seances.md'];

$files = [];
foreach (DOCUMENT_TREES as $tree) {
    $home = $tree === '.' ? $root : $root . '/' . $tree;
    if (!is_dir($home)) {
        continue;
    }
    // LA RACINE NE SE PARCOURT PAS EN PROFONDEUR : ses sous-répertoires sont du code, des images ou du jetable, et `doc/` est balayé pour lui-même juste après.
    $iterator = $tree === '.'
        ? new IteratorIterator(new FilesystemIterator($home, FilesystemIterator::SKIP_DOTS))
        : new RecursiveIteratorIterator(new RecursiveDirectoryIterator($home, FilesystemIterator::SKIP_DOTS));
    foreach ($iterator as $file) {
        if (!$file->isFile() || $file->getExtension() !== 'md') {
            continue;
        }
        $relative = substr($file->getPathname(), strlen($root) + 1);
        if (in_array($relative, RECORDS, true)) {
            continue;
        }
        foreach (SKIPPED_TREES as $skipped) {
            if (str_starts_with($relative, $skipped . '/')) {
                continue 2;
            }
        }
        $files[] = $relative;
    }
}
$files = array_values(array_unique($files));
sort($files);
if ($files === []) {
    fwrite(STDERR, "FAULT aucun document Markdown trouvé sous " . implode(', ', DOCUMENT_TREES) . " : un balayage qui ne lit rien ne peut rien conclure.\n");
    exit(1);
}

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
if ($dead) {
    // UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`), et ici les deux issues sont opposées : ou le chemin a bougé, ou la promesse est morte.
    echo "  Solution — si le fichier a été déplacé ou renommé, corriger la citation ; s'il n'existe plus, RETIRER la phrase qui le promet plutôt que de la\n";
    echo "  laisser envoyer le lecteur nulle part. Un document d'historique, lui, cite ce qui existait le jour où il a été écrit : il ne se réécrit pas, il\n";
    echo "  se déclare à la constante RECORDS de ce fichier.\n";
}

exit($dead ? 1 : 0);

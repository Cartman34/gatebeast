<?php
/**
 * USAGE
 *   php scripts/check-comment-language.php [fichiers…] — the code comments are in English. Without arguments, the whole of `scripts/` and `review-server/`.
 *   php scripts/check-comment-language.php -v — each French comment, with its file and its line.
 *   php scripts/check-comment-language.php -h|--help — this text.
 *
 * INTENTION
 *   NOTHING WATCHED FOR THIS, AND THAT IS WHY IT SPREAD (`W30 comments-en-anglais`, operator on 2026-08-12: « y'a jamais d'aucune manière que ce soit la
 *   possibilité d'avoir un commentaire de code en FR, si tu en vois, c'est une erreur que tu as faite, évite absolument de propager tes propres erreurs »).
 *   `check-code-language.py` judges NAMES and compared VALUES; the language of the prose beside them was checked by nobody. An agent then aligns on what
 *   surrounds it — the exact fault the first rule of this repository forbids — and one French comment becomes twenty.
 *
 *   THE OPERATOR'S QUOTES ARE RESERVED, AND THEY ARE THE REASON THIS CHECK CANNOT SIMPLY LOOK FOR ACCENTS. A comment quoting him keeps his words, in French,
 *   « between these guillemets ». Those passages are removed before judging: what is left must be English. Same for a French path or a French data key named
 *   in passing — they are code, and `check-code-language.py` owns them.
 *
 *   IT JUDGES BY COMMON WORDS, NOT BY ACCENTS. « The » and « une » cannot be confused, whereas an accent appears in an English comment quoting a French label.
 *   A line is French when it carries at least two of the words below outside any quote — one alone catches « la » in « la Palma » and other proper nouns.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);

/** Where comments are judged when no file is given. `local/` is the agent's own and `var/` is not versioned. */
const TREES = ['scripts', 'review-server'];
/** The extensions that carry code comments. */
const EXTENSIONS = ['php', 'js', 'css', 'sh'];
/**
 * The French words that decide, and they are chosen for having NO English homograph — « the », « for » and « and » would match English prose. Two of them on
 * one line make it French; one alone is a proper noun or a quoted label.
 */
const FRENCH = ['le', 'la', 'les', 'une', 'des', 'du', 'qui', 'que', 'pour', 'dans', 'est', 'sont', 'avec', 'pas', 'sur', 'ce', 'cette', 'ne', 'se', 'par',
    'plus', 'donc', 'mais', 'où', 'aux', 'leur', 'elle', 'il', 'nous', 'vous', 'tout', 'toute', 'quand', 'alors', 'ainsi', 'chaque', 'sans', 'sous'];

$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
$given = array_values(array_filter(array_slice($argv, 1), static fn (string $arg): bool => !str_starts_with($arg, '-')));

$files = [];
if ($given !== []) {
    $files = $given;
} else {
    foreach (TREES as $tree) {
        $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $file) {
            if ($file->isFile() && in_array($file->getExtension(), EXTENSIONS, true)) {
                $files[] = substr($file->getPathname(), strlen($root) + 1);
            }
        }
    }
    sort($files);
}
if ($files === []) {
    fwrite(STDERR, "FAULT aucun fichier à contrôler : un balayage qui ne lit rien ne peut rien conclure.\n"
        . "  Solution — donner des fichiers en argument, ou vérifier que « " . implode(' » et « ', TREES) . " » existent.\n");
    exit(1);
}

/**
 * The file with the operator's quotes removed — WHOLE, before anything is cut into lines.
 *
 * A QUOTE SPANS SEVERAL LINES, AND REMOVING IT LINE BY LINE REMOVES ONLY ITS FIRST. That was this check's own first fault: an English comment quoting the
 * operator over three lines had its opening line cleared and the two following ones reported as French — the check crying on comments that obey the rule, which
 * is how a check stops being run. The quotes go first, on the whole text; what remains is then cut into lines.
 */
function withoutQuotes(string $body): string
{
    // The closing guillemet is optional: a quote may run to the end of the comment block without one, and stopping at the next « would swallow real prose.
    $body = preg_replace('~«.*?(»|(?=\n\s*\n))~su', ' ', $body);

    return preg_replace('~"[^"]*"|`[^`]*`~su', ' ', $body);
}

/** Whether that line of comment is written in French. */
function isFrench(string $comment): bool
{
    $words = preg_split('~[^\p{L}]+~u', mb_strtolower($comment), -1, PREG_SPLIT_NO_EMPTY) ?: [];
    $hits = 0;
    foreach ($words as $word) {
        if (in_array($word, FRENCH, true)) {
            $hits++;
        }
    }

    return $hits >= 2;
}

/** The comment lines of a file, each with its line number. Strings are not comments, and a `//` inside one is not a comment opener. */
function commentsOf(string $body): array
{
    $found = [];
    $inBlock = false;
    foreach (explode("\n", $body) as $number => $line) {
        $bare = trim($line);
        if ($inBlock) {
            $found[$number + 1] = ltrim($bare, '* ');
            if (str_contains($bare, '*/')) {
                $inBlock = false;
            }
            continue;
        }
        if (str_starts_with($bare, '/*')) {
            $found[$number + 1] = ltrim(substr($bare, 2), '* ');
            $inBlock = !str_contains($bare, '*/');
            continue;
        }
        // UN `//` DANS UNE CHAÎNE N'OUVRE PAS UN COMMENTAIRE — « https:// » en est plein —, donc seul un commentaire qui OUVRE sa ligne est jugé. Ce qui est
        // laissé de côté est dit ici plutôt que découvert : un commentaire en fin de ligne de code échappe à ce contrôle.
        if (str_starts_with($bare, '//') || (str_starts_with($bare, '#') && !str_starts_with($bare, '#!'))) {
            $found[$number + 1] = ltrim($bare, '/# ');
        }
    }

    return $found;
}

$faults = [];
foreach ($files as $relative) {
    $path = str_starts_with($relative, '/') ? $relative : $root . '/' . $relative;
    if (!is_file($path)) {
        fwrite(STDERR, "FAULT le fichier « $relative » est absent.\n  Solution — vérifier le chemin donné en argument.\n");
        exit(1);
    }
    foreach (commentsOf(withoutQuotes(file_get_contents($path))) as $number => $comment) {
        if ($comment !== '' && isFrench($comment)) {
            $faults[] = "$relative:$number — " . mb_strimwidth($comment, 0, 120, '…');
        }
    }
}

printf("%d fichier(s) : %d commentaire(s) en français.\n", count($files), count($faults));
if ($faults === []) {
    exit(0);
}
if ($detail) {
    foreach ($faults as $fault) {
        printf("  %s\n", $fault);
    }
} else {
    printf("« -v » les nomme.\n");
}
printf("  Solution — les réécrire en anglais américain : un commentaire est du code qui explique le code. Seules les CITATIONS de l'opérateur restent\n");
printf("  en français, entre guillemets français — elles se rapportent mot pour mot et ce contrôle les écarte déjà.\n");
exit(1);

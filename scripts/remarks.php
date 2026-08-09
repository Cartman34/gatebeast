<?php
/**
 * USAGE
 *   php scripts/remarks.php list                                  the remarks still waiting, and the ones already dealt with
 *   php scripts/remarks.php handle <chemin de l'image> "<raison>"  marks one remark as dealt with, with the reason it is over
 *   php scripts/remarks.php reopen <chemin de l'image>             takes that mark off again
 *
 * INTENTION
 *   A REMARK LEAVES WHEN IT HAS BEEN DEALT WITH, NEVER WHEN IT IS WRITTEN. A verdict and a comment bear on ONE IMAGE, and a retake produces a new representation
 *   which starts with no verdict — that rule is already written in doc/outils/referentiel-des-sujets.md and settles every case where a new image is produced. It
 *   leaves exactly one case open: the operator VALIDATES the image as it stands, so no new image will ever come, and the remark on it would stay active for ever.
 *   He asked for this on 2026-08-09 : « c'est à toi de faire une proposition pour que tu puisses noter dans le fichier que la remarque a été traitée sans
 *   génération d'image (car image validée) ».
 *
 *   THE MARK CARRIES ITS REASON, AND THAT IS THE POINT. « Dealt with » alone says nothing a month later — image validated as it stands, prompt corrected, remark
 *   made moot by another change: those are different stories, and the one that applies is what the next reader needs. Nothing is ever deleted: the remark stays
 *   readable, it only stops being counted as due.
 *
 *   ONE WRITER FOR THIS FILE, AND IT REFUSES WHAT IT DOES NOT KNOW. An unknown path is a fault, not an entry to create: it would put a remark on an image nobody
 *   ever commented, and it would look exactly like a real one.
 */

$root = dirname(__DIR__);
$notes = $root . '/review-server/notes/sprites.json';
const SECTION = 'verdicts';

$command = $argv[1] ?? 'list';

/** The whole notes file, or an empty section when it does not exist yet. */
function read(string $path): array
{
    if (!is_file($path)) {
        return [SECTION => []];
    }
    $content = file_get_contents($path);
    if ($content === false) {
        throw new RuntimeException("FAUTE le fichier de remarques « {$path} » est illisible");
    }
    $data = json_decode($content, true);
    if (!is_array($data)) {
        throw new RuntimeException("FAUTE le fichier de remarques « {$path} » ne contient pas du JSON exploitable");
    }
    $data[SECTION] = $data[SECTION] ?? [];

    return $data;
}

function write(string $path, array $data): void
{
    $written = file_put_contents($path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
    if ($written === false) {
        throw new RuntimeException("FAUTE le fichier de remarques « {$path} » n'a pas pu être écrit");
    }
}

if ($command === 'list') {
    $data = read($notes);
    $waiting = [];
    $done = [];
    foreach ($data[SECTION] as $image => $entry) {
        if (!is_array($entry) || ($entry['comment'] ?? '') === '') {
            continue;
        }
        if (isset($entry['handled'])) {
            $done[$image] = $entry;
            continue;
        }
        $waiting[$image] = $entry;
    }
    printf("%d remarque(s) en attente\n", count($waiting));
    foreach ($waiting as $image => $entry) {
        printf("  %s\n      %s\n", $image, $entry['comment']);
    }
    printf("\n%d remarque(s) traitée(s)\n", count($done));
    foreach ($done as $image => $entry) {
        printf("  %s — %s, %s\n", $image, $entry['handled']['date'] ?? '?', $entry['handled']['reason'] ?? '?');
    }
    exit(0);
}

if ($command === 'handle' || $command === 'reopen') {
    $image = $argv[2] ?? null;
    if ($image === null) {
        throw new RuntimeException("FAUTE usage : php scripts/remarks.php {$command} <chemin de l'image> [\"<raison>\"]");
    }
    $data = read($notes);
    if (!isset($data[SECTION][$image])) {
        throw new RuntimeException("FAUTE aucune remarque ne porte sur « {$image} » — php scripts/remarks.php list");
    }
    if ($command === 'reopen') {
        unset($data[SECTION][$image]['handled']);
        write($notes, $data);
        printf("%s : la remarque redevient active\n", $image);
        exit(0);
    }
    $reason = $argv[3] ?? null;
    if ($reason === null || trim($reason) === '') {
        throw new RuntimeException('FAUTE une remarque traitée dit POURQUOI elle l\'est — « image validée telle quelle », « consigne corrigée »…');
    }
    $data[SECTION][$image]['handled'] = ['date' => date('Y-m-d'), 'reason' => trim($reason)];
    write($notes, $data);
    printf("%s : remarque traitée — %s\n", $image, trim($reason));
    exit(0);
}

throw new RuntimeException("FAUTE « {$command} » n'est pas une sous-commande — list, handle, reopen.");

<?php
/**
 * USAGE
 *   php scripts/remarks.php list                                  the remarks still waiting, and the ones already dealt with
 *   php scripts/remarks.php new                                   ONLY what the operator has judged or written since it was last read — exit 1 when there is any
 *   php scripts/remarks.php seen                                  records the current state as read, so `new` stops naming it
 *   php scripts/remarks.php handle <chemin de l'image> "<raison>"  marks one remark as dealt with, with the reason it is over
 *   php scripts/remarks.php reopen <chemin de l'image>             takes that mark off again
 *   php scripts/remarks.php -h|--help                             this text
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
require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$notes = $root . '/review-server/notes/sprites.json';
/**
 * WHAT THE AGENT HAS ALREADY READ, KEPT APART FROM WHAT THE OPERATOR WRITES. The operator judges on the page while the agent works, and nothing warned it: on
 * 2026-08-11 three images were judged and the agent found out an hour later, by opening the remarks file for another reason — and two of those verdicts
 * overturned a written rule. This ledger is what turns « the data is there » into « I have been told ».
 *
 * IT LIVES UNDER var/ AND NEVER INSIDE HIS FILE: a mark of what the agent has read has nothing to do in the operator's data, and writing there would risk the
 * very thing the review page exists to protect. Losing this file costs one thing only — everything reads as new once.
 */
$ledger = $root . '/var/verdicts-seen.json';
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

/**
 * What ONE entry says, in a single string — the three acts and the comment.
 *
 * THE FINGERPRINT IS TAKEN ON WHAT THE OPERATOR DECIDED, NOTHING ELSE: the mark the agent puts on a dealt-with remark is deliberately left out, or handling a
 * remark would make it look freshly changed and it would come back as new for ever.
 */
function fingerprint(array $entry): string
{
    return md5(json_encode([
        'approved' => (bool) ($entry['approved'] ?? false),
        'rework' => (bool) ($entry['rework'] ?? false),
        'discarded' => (bool) ($entry['discarded'] ?? false),
        'comment' => (string) ($entry['comment'] ?? ''),
    ]));
}

/** What every image says right now, by its path. */
function fingerprints(array $data): array
{
    $now = [];
    foreach ($data[SECTION] as $image => $entry) {
        if (is_array($entry)) {
            $now[$image] = fingerprint($entry);
        }
    }

    return $now;
}

/** What a verdict says in one word, for a line the agent reads at a glance. */
function verdictWord(array $entry): string
{
    foreach (['approved' => 'validé', 'rework' => 'À REPRENDRE', 'discarded' => 'ÉCARTÉ'] as $act => $word) {
        if ($entry[$act] ?? false) {
            return $word;
        }
    }

    return 'sans verdict';
}

if ($command === 'new' || $command === 'seen') {
    $data = read($notes);
    $now = fingerprints($data);
    $read = is_file($ledger) ? (json_decode(file_get_contents($ledger), true) ?: []) : [];

    if ($command === 'seen') {
        @mkdir(dirname($ledger), 0777, true);
        write($ledger, $now);
        printf("%d verdict(s) marqué(s) comme lus.\n", count($now));
        exit(0);
    }

    $fresh = [];
    foreach ($now as $image => $print) {
        if (($read[$image] ?? null) !== $print) {
            $fresh[$image] = $data[SECTION][$image];
        }
    }
    if (!$fresh) {
        printf("Aucun verdict neuf — %d lus.\n", count($now));
        exit(0);
    }
    // THE EXIT CODE IS WHAT MAKES IT USABLE BY A HOOK: 1 says « something awaits », 0 says « nothing ». A message alone would have to be parsed, and a parsed
    // message is a promise nobody keeps.
    printf("%d verdict(s) neuf(s) depuis la dernière lecture — « php scripts/remarks.php seen » les marque lus :\n", count($fresh));
    foreach ($fresh as $image => $entry) {
        printf("  %s — %s\n", $image, verdictWord($entry));
        if (($entry['comment'] ?? '') !== '') {
            printf("      %s\n", $entry['comment']);
        }
    }
    exit(1);
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

throw new RuntimeException("FAUTE « {$command} » n'est pas une sous-commande — list, new, seen, handle, reopen.");

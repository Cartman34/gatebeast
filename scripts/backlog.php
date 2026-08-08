<?php
/**
 * USAGE
 *   php scripts/backlog.php <subcommand> [arguments] — the one way the open points of the project are read and edited. Every subcommand that writes rebuilds the /sujets page on its way out.
 *
 *     next                                   the next point to take, and nothing else
 *     list [--all]                           the open points in priority order; --all adds the closed ones
 *     show <REF>                             one point in full, description included
 *     add <SERIES> <priority> <label>        a new point; its long description is read from standard input
 *     set <REF> <field> <value>              change one field: priorite, statut, libelle, attend
 *     describe <REF>                         replace the long description, read from standard input
 *     close <REF> [why]                      status "fait", with an optional closing sentence
 *
 * INTENTION
 *   The pile was prose in SUIVI.md: nothing could sort it, count it, or answer "what is next" without a human reading the whole document. Now a single command answers that, and the same command is
 *   the only thing that writes — a point edited by hand in two places diverges, which is exactly what happened between the SUIVI table and the artefact registry.
 *
 *   REBUILDING THE PAGE IS PART OF WRITING, not a step to remember: a page that lags behind the data is worse than no page, because it looks current. The operator asked for exactly this.
 */

$root = dirname(__DIR__);
require_once $root . '/review-server/lib/Backlog.php';

$backlog = new Backlog($root);
$command = $argv[1] ?? 'next';

/** Le jour, en toutes lettres — une date relative ne veut plus rien dire une semaine plus tard. */
function today(): string
{
    return date('Y-m-d');
}

/** Reconstruit la page servie. Toute écriture passe par là : c'est ce qui garantit que la page ne ment jamais sur l'état de la pile. */
function republish(string $root): void
{
    exec(sprintf('php %s /sujets 2>&1', escapeshellarg($root . '/review-server/build.php')), $lines, $status);
    if ($status !== 0) {
        fwrite(STDERR, "La page n'a pas pu être reconstruite :\n" . implode("\n", $lines) . "\n");
    }
}

/** Une ligne de liste : la référence, la priorité, le statut, le libellé. Assez pour choisir, jamais plus. */
function line(array $point): string
{
    // LA REF EST UN SLUG DE VINGT CARACTÈRES, PAS UN COMPTEUR (opérateur, 2026-08-07) : « S34 » n'apprend rien, il faut ouvrir la tâche pour savoir de quoi il
    // s'agit. Le compteur reste comme code interne, entre parenthèses, parce que tout l'historique du projet le cite.
    return sprintf('%-20s (%-4s) p%-3d %-17s %s', $point['ref'], $point['code'] ?? '', $point['priority'], $point['status'], $point['label']);
}

if ($command === 'next') {
    $open = $backlog->ordered(true);
    if (!$open) {
        echo "Rien à dépiler : aucun point ouvert.\n";
        exit(0);
    }
    $point = $open[0];
    printf("%s\n\n%s\n", line($point), $point['description']);
    $waiting = array_values(array_filter($open, fn (array $p) => $p['status'] === 'pending-decision'));
    if ($waiting) {
        printf("\nEt %d point(s) attendent une décision de l'opérateur : %s\n", count($waiting),
            implode(', ', array_column($waiting, 'ref')));
    }
    exit(0);
}

if ($command === 'list') {
    $withClosed = in_array('--all', $argv, true);
    $points = $backlog->ordered(!$withClosed);
    foreach ($points as $point) {
        echo line($point) . "\n";
    }
    printf("\n%d point(s)%s.\n", count($points), $withClosed ? '' : ' ouverts');
    exit(0);
}

if ($command === 'show') {
    $point = $backlog->find($argv[2] ?? '');
    if (!$point) {
        throw new RuntimeException("FAULT le point « " . ($argv[2] ?? '') . " » n'existe pas.");
    }
    printf("%s — %s\n\nPriorité %d · statut %s · attend %s · créé le %s · repris le %s\n\n%s\n",
        $point['ref'], $point['label'], $point['priority'], Backlog::STATUS_LABELS[$point['status']] ?? $point['status'],
        $point['waiting'], $point['created'], $point['updated'], $point['description']);
    exit(0);
}

if ($command === 'add') {
    $series = $argv[2] ?? null;
    $priority = $argv[3] ?? null;
    $label = $argv[4] ?? null;
    if ($series === null || $priority === null || $label === null) {
        throw new RuntimeException('FAULT usage : php scripts/backlog.php add <SÉRIE> <priorité> <libellé>, la description longue arrivant sur l\'entrée standard.');
    }
    $description = trim(stream_get_contents(STDIN));
    // A POINT CARRIES BOTH: the slug it is read by, and the series code the whole project cites. Creation used to write the code into the ref, which produced a bare "Q1" among twenty-character
    // slugs and a duplicate code with it. Both are derived here, in that order, because the slug falls back to the code when the label collides.
    $code = $backlog->nextRef($series);
    $ref = $backlog->slugFor($label, $code);
    $backlog->save([
        'ref' => $ref,
        'code' => $code,
        'label' => $label,
        'description' => $description !== '' ? $description : $label,
        'status' => 'todo',
        'priority' => (int) $priority,
        'waiting' => 'agent',
        'created' => today(),
        'updated' => today(),
    ]);
    republish($root);
    printf("%s créé, priorité %d.\n", $ref, (int) $priority);
    exit(0);
}

if ($command === 'set') {
    [$ref, $field, $value] = [$argv[2] ?? '', $argv[3] ?? '', $argv[4] ?? ''];
    $point = $backlog->find($ref);
    if (!$point) {
        throw new RuntimeException("FAULT le point « {$ref} » n'existe pas.");
    }
    if (!in_array($field, ['priority', 'status', 'label', 'waiting'], true)) {
        throw new RuntimeException("FAULT « {$field} » n'est pas modifiable — priority, status, label, waiting.");
    }
    if ($field === 'status' && !in_array($value, Backlog::STATUSES, true)) {
        throw new RuntimeException("FAULT « {$value} » n'est pas un statut — " . implode(', ', Backlog::STATUSES) . '.');
    }
    // UN POINT QUI ATTEND UNE DÉCISION EST UNE QUESTION (opérateur, 2026-08-07), et l'outil le tient plutôt que la vigilance : deux décisions avaient été écrites sous un sujet et une proposition,
    // si bien que la série des questions paraissait vide alors que deux arbitrages attendaient — exactement ce que les codes existent pour rendre visible d'un coup d'œil.
    if ($field === 'status' && $value === 'pending-decision' && !str_starts_with($point['ref'], 'Q')) {
        throw new RuntimeException("FAULT « {$point['ref']} » ne peut pas passer « à trancher » : un point qui attend une décision de l'opérateur est une QUESTION, et sa référence commence par Q. "
            . "Créez-le dans la série Q et classez celui-ci en renvoyant vers lui.");
    }
    $point[$field] = $field === 'priority' ? (int) $value : $value;
    $point['updated'] = today();
    $backlog->save($point);
    republish($root);
    printf("%s : %s = %s\n", $point['ref'], $field, $value);
    exit(0);
}

if ($command === 'describe') {
    $point = $backlog->find($argv[2] ?? '');
    if (!$point) {
        throw new RuntimeException("FAULT le point « " . ($argv[2] ?? '') . " » n'existe pas.");
    }
    $point['description'] = trim(stream_get_contents(STDIN));
    $point['updated'] = today();
    $backlog->save($point);
    republish($root);
    printf("%s : description reprise, %d caractères.\n", $point['ref'], strlen($point['description']));
    exit(0);
}

if ($command === 'close') {
    $point = $backlog->find($argv[2] ?? '');
    if (!$point) {
        throw new RuntimeException("FAULT le point « " . ($argv[2] ?? '') . " » n'existe pas.");
    }
    $point['status'] = 'done';
    $point['updated'] = today();
    if (isset($argv[3])) {
        $point['description'] .= "\n\n**Fermé le " . today() . '** — ' . $argv[3];
    }
    $backlog->save($point);
    republish($root);
    printf("%s fermé.\n", $point['ref']);
    exit(0);
}

throw new RuntimeException("FAULT « {$command} » n'est pas une sous-commande — next, list, show, add, set, describe, close.");

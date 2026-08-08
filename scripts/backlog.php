<?php
/**
 * USAGE
 *   php scripts/backlog.php <subcommand> [arguments] — the one way the open points of the project are read and edited. Every subcommand that writes rebuilds the /sujets page on its way out.
 *
 *     next                                     the next point to take, and nothing else
 *     list [--all]                             the open points in priority order; --all adds the closed ones
 *     show <REF>                               one point in full, description included
 *     add <SERIES> <priority> <label> [ref]    a new point; its long description is read from standard input
 *     set <REF> <field> <value> [waits-on]     change one field: priority, status, label, waiting
 *     describe <REF>                           replace the long description, read from standard input
 *     close <REF> [why]                        status "done", with an optional closing sentence
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

/** Today, spelled out — a relative date means nothing a week later. */
function today(): string
{
    return date('Y-m-d');
}

/** Rebuilds the served page. Every write goes through here: that is what keeps the page from ever lying about the state of the pile. */
function republish(string $root): void
{
    exec(sprintf('php %s /sujets 2>&1', escapeshellarg($root . '/review-server/build.php')), $lines, $status);
    if ($status !== 0) {
        fwrite(STDERR, "La page n'a pas pu être reconstruite :\n" . implode("\n", $lines) . "\n");
    }
}

/** One line of the listing: the ref, the priority, the status, the label. Enough to choose from, never more. */
function line(array $point): string
{
    // THE REF IS A TWENTY-CHARACTER SLUG, NOT A COUNTER (operator, 2026-08-07): "S34" teaches nothing, one has to open the task to learn what it is about. The
    // counter stays as an internal code, in parentheses, because the whole history of the project cites it.
    // WHAT A POINT WAITS ON SHOWS NEXT TO ITS STATUS, never in the card alone: one picks what to take by reading the listing, and "waiting" without its subject helps nobody.
    $waiting = isset($point['waits_on']) ? ' ← ' . $point['waits_on'] : '';

    return sprintf('%-20s (%-4s) p%-3d %-19s %s%s', $point['ref'], $point['code'] ?? '', $point['priority'], $point['status'], $point['label'], $waiting);
}

if ($command === 'next') {
    $open = $backlog->ordered(true);
    if (!$open) {
        echo "Rien à dépiler : aucun point ouvert.\n";
        exit(0);
    }
    // `next` ONLY ANSWERS WITH A TAKEABLE POINT: "the first one to take" means nothing if it cannot be taken. The three waiting statuses stay open, and so stay
    // counted and shown by `list`, but they are not offered — otherwise the agent reopens a point waiting on the operator every single turn, reads its whole
    // analysis, finds again that it cannot move, and puts it back. The order itself does not change: it is `ordered()`'s, where an engaged point comes first.
    $takeable = array_values(array_filter($open, fn (array $p) => in_array($p['status'], Backlog::STATUSES_TAKEABLE, true)));
    if (!$takeable) {
        printf("Rien à dépiler : les %d point(s) ouverts attendent tous quelque chose. `list` dit quoi.\n", count($open));
        exit(0);
    }
    $point = $takeable[0];
    printf("%s\n\n%s\n", line($point), $point['description']);
    $waiting = array_values(array_filter($open, fn (array $p) => $p['status'] === Backlog::STATUS_PENDING_DECISION));
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
    printf("%s — %s\n\nPriorité %d · statut %s%s · attend %s · créé le %s · repris le %s\n\n%s\n",
        $point['ref'], $point['label'], $point['priority'], Backlog::STATUS_LABELS[$point['status']] ?? $point['status'],
        isset($point['waits_on']) ? ' : ' . $point['waits_on'] : '',
        $point['waiting'], $point['created'], $point['updated'], $point['description']);
    exit(0);
}

if ($command === 'add') {
    $series = $argv[2] ?? null;
    $priority = $argv[3] ?? null;
    $label = $argv[4] ?? null;
    if ($series === null || $priority === null || $label === null) {
        throw new RuntimeException('FAULT usage : php scripts/backlog.php add <SÉRIE> <priorité> <libellé> [ref], la description longue arrivant sur l\'entrée standard.');
    }
    $description = trim(stream_get_contents(STDIN));
    // A POINT CARRIES BOTH: the slug it is read by, and the series code the whole project cites. Creation used to write the code into the ref, which produced a bare "Q1" among twenty-character
    // slugs and a duplicate code with it. Both are derived here, in that order, because the slug falls back to the code when the label collides.
    $code = $backlog->nextRef($series);
    // THE REF IS GIVEN, NOT GUESSED (operator, 2026-08-08): a label cut at twenty characters rarely names the point, and that is how refs ended on padding dashes. Whoever creates the point knows
    // better than the machine what it will be called in conversation. Deriving it stays for quick creations, never as the intent.
    $ref = $backlog->slugFor($label, $code);
    if (isset($argv[5]) && trim($argv[5]) !== '') {
        // A GIVEN REF IS NEVER TRIMMED SILENTLY: "regle-noms-composants" shortened without a word became "regle-noms", which no longer names the point. A silent truncation hands back a name nobody
        // chose — exactly what giving the ref was meant to avoid. Refuse, state the limit, let the author decide.
        $ref = trim($argv[5]);
        if (strlen($ref) > 20 || $ref !== trim($ref, '-') || !preg_match('/^[a-z0-9-]+$/', $ref)) {
            throw new RuntimeException("FAULT la ref « {$ref} » ne convient pas : vingt caractères au plus, minuscules, chiffres et tirets, et jamais un tiret au bord.");
        }
    }
    if ($backlog->find($ref) !== null) {
        throw new RuntimeException("FAULT la ref « {$ref} » est déjà prise — donnez-en une autre.");
    }
    $backlog->save([
        'ref' => $ref,
        'code' => $code,
        'label' => $label,
        'description' => $description !== '' ? $description : $label,
        // UN SUJET NEUF EST PROPOSÉ, PAS À FAIRE (opérateur, 2026-08-08). L'agent tient le suivi, il ne décide pas de ce sur quoi le projet travaille : ce qu'il
        // ouvre de lui-même attend la validation, et `next` ne le proposera pas. Quand c'est l'opérateur qui demande le point, `--demande` le met directement à faire.
        'status' => in_array('--demande', $argv, true) ? Backlog::STATUS_TODO : Backlog::STATUS_PROPOSED,
        'priority' => (int) $priority,
        'waiting' => Backlog::WAITING_AGENT,
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
    // NO WAIT WITHOUT ITS SUBJECT NAMED (operator, 2026-08-08): a bare "blocked" does not say whether the point waits on an answer, on another point, or on an install. Two points sat blocked by
    // nothing, and a question that did not exist was put to the operator. The fifth argument is what was missing, and it is mandatory.
    if ($field === 'status' && in_array($value, Backlog::WAITING_STATUSES, true)) {
        $waitsOn = $argv[5] ?? '';
        if (trim($waitsOn) === '') {
            throw new RuntimeException("FAULT « {$value} » exige de nommer l'attendu : php scripts/backlog.php set {$point['ref']} status {$value} \"ce qu'il attend\".");
        }
        $point['waits_on'] = trim($waitsOn);
    }
    if ($field === 'status' && !in_array($value, Backlog::WAITING_STATUSES, true)) {
        unset($point['waits_on']);
    }
    // THE SERIES IS READ FROM THE CODE, NOT FROM THE REF (2026-08-08): refs have been slugs since the migration, so none starts with Q any more and this guard refused every question.
    if ($field === 'status' && $value === Backlog::STATUS_PENDING_DECISION && !str_starts_with($point['code'] ?? '', Backlog::SERIES_QUESTION)) {
        throw new RuntimeException("FAULT « {$point['ref']} » ne peut pas passer « à trancher » : un point qui attend une décision de l'opérateur est une QUESTION, et son code commence par Q. "
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
    $point['status'] = Backlog::STATUS_DONE;
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

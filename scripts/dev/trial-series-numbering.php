<?php
/**
 * USAGE
 *   php scripts/dev/trial-series-numbering.php — proves how a series is numbered: continuous while a point stays open, back to 1 when it empties, and never
 *   jumping over the numbers of closed points. Exit code 0 when every case is green, 1 otherwise.
 *   php scripts/dev/trial-series-numbering.php -h|--help — this text.
 *
 * INTENTION
 *   THIS COLLISION HAS COME BACK TWICE, AND NOTHING WATCHED FOR IT. On 2026-08-08 refs became slugs and every new point was numbered 1, producing a second
 *   « Q1 ». The fix read the code field instead of the ref. On 2026-08-13 it returned by the other end: the used-numbers survey swept ALL points, closed
 *   included, while the restart flag looked only at open ones — so an empty series restarted at 1, correctly, and the NEXT add jumped to the historical maximum.
 *   Two questions opened the same day got « Q1 » and « Q24 », and « Q1 » had already belonged to a closed point.
 *
 *   A DEFECT THAT COMES BACK IS A DEFECT NOBODY MEASURES. Both fixes were right and neither was proven, so the third form of the same bug would pass unseen
 *   again. This trial holds the three cases that define the rule, on a backlog of its own — it never touches the project's tasks.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Backlog.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$work = $root . '/local/tmp/trial-series-numbering';
if (!is_dir($work) && !mkdir($work, 0o777, true) && !is_dir($work)) {
    fwrite(STDERR, "FAULT le répertoire d'essai « $work » ne se crée pas.\n");
    exit(1);
}

/**
 * A backlog holding exactly those points, under a root of the trial's own — never the project's.
 *
 * `Backlog` takes a REPOSITORY ROOT and appends `review-server/tasks.json` itself, so the trial builds that tree rather than handing it a file path. Written
 * down because the first version of this trial passed a file path and every case came back « Q1 »: the backlog found no tasks file, read an empty list, and
 * answered correctly for a backlog that does not exist. **A trial that measures its own mistake looks exactly like a broken feature.**
 */
function backlogOf(string $home, array $points): Backlog
{
    $folder = $home . '/review-server';
    if (!is_dir($folder) && !mkdir($folder, 0o777, true) && !is_dir($folder)) {
        fwrite(STDERR, "FAULT le répertoire d'essai « $folder » ne se crée pas.\n");
        exit(1);
    }
    $tasks = [];
    foreach ($points as $rank => $point) {
        $tasks[] = ['ref' => 'essai-' . $rank, 'code' => $point['code'], 'status' => $point['status'],
            'label' => 'point d\'essai', 'priority' => 50, 'created' => '2026-08-19'];
    }
    file_put_contents($folder . '/tasks.json', json_encode(['format' => 'gatebeast-tasks', 'version' => 1, 'tasks' => $tasks],
        JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");

    return new Backlog($home);
}

$cases = [
    ['name' => 'une série vide repart à 1', 'points' => [], 'expected' => 'Q1'],
    ['name' => 'un point ouvert : on continue après lui', 'points' => [['code' => 'Q3', 'status' => 'todo']], 'expected' => 'Q4'],
    ['name' => 'une série entièrement close repart à 1', 'points' => [['code' => 'Q23', 'status' => 'done']], 'expected' => 'Q1'],
    // LE CAS QUI A CASSÉ DEUX FOIS, et c'est le seul qui distingue le correctif juste du faux : un point clos très haut, un point ouvert très bas.
    ['name' => 'un clos haut et un ouvert bas : on suit l\'OUVERT, pas l\'historique',
        'points' => [['code' => 'Q23', 'status' => 'done'], ['code' => 'Q1', 'status' => 'todo']], 'expected' => 'Q2'],
    ['name' => 'une autre série n\'influence pas celle-ci',
        'points' => [['code' => 'S9', 'status' => 'todo'], ['code' => 'Q2', 'status' => 'todo']], 'expected' => 'Q3'],
    ['name' => 'un point proposé compte comme ouvert',
        'points' => [['code' => 'Q5', 'status' => 'proposed']], 'expected' => 'Q6'],
];

$red = 0;
foreach ($cases as $rank => $case) {
    $given = backlogOf($work . '/cas-' . $rank, $case['points'])->nextRef('Q');
    $green = $given === $case['expected'];
    $red += $green ? 0 : 1;
    printf("%s — %s : attendu %s, obtenu %s\n", $green ? 'VERT ' : 'ROUGE', $case['name'], $case['expected'], $given);
}

if ($red > 0) {
    printf("\n%d cas sur %d sont rouges.\n", $red, count($cases));
    exit(1);
}

printf("\nLes %d cas sont verts.\n", count($cases));

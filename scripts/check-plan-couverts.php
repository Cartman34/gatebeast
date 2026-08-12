<?php
/**
 * Usage: php scripts/check-plan-couverts.php <plan.json> [<plan.json>...]
 *        php scripts/check-plan-couverts.php -h|--help — this text
 *
 * Reports every subject standing inside another subject's couvert — a whole tree growing under an oak's crown, which does not happen.
 *
 * Intention: a plan already refuses two subjects on one cell, and that check is right to block, because two footprints on the same ground is an impossibility of the plan
 * itself. A footprint inside someone else's CANOPY is different: it is a fault of NATURE, not of declaration. Two crowns may brush against each other, and an operator may
 * deliberately want a sapling under a big tree one day. So this tool REPORTS AND NEVER BLOCKS, and it is run by hand — after a new plan, or after a large edit — rather than
 * wired into the drawing chain (operator, 2026-08-05).
 *
 * It reads the couvert from assets/subjects.json, never from the plan: what a subject overhangs is a property of the subject.
 *
 * Why PHP and not Python: PHP is this project's default language for lasting tooling, and this needs nothing Python alone provides.
 */

$root = __DIR__ . '/..';
require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$plans = array_slice($argv, 1);
if ($plans === []) {
    fwrite(STDERR, "Usage: php scripts/check-plan-couverts.php <plan.json> [<plan.json>...]\n");
    exit(2);
}

$subjects = json_decode(file_get_contents("$root/assets/subjects.json"), true, 512, JSON_THROW_ON_ERROR)['subjects'];
$faults = 0;

foreach ($plans as $file) {
    if (!is_file($file)) {
        fwrite(STDERR, "ABSENT $file\n");
        $faults++;
        continue;
    }
    $plan = json_decode(file_get_contents($file), true, 512, JSON_THROW_ON_ERROR);
    echo basename($file) . " — " . count($plan['cells']) . " cases déclarées\n";

    // Ce que chaque case porte, et ce que chaque sujet surplombe. Le couvert est CENTRÉ sur l'emprise : c'est ainsi qu'il est dessiné sur le plan, et une couronne ne pousse
    // pas d'un seul côté du tronc.
    $ground = [];
    $canopies = [];
    foreach ($plan['cells'] as $cell) {
        $code = $cell['subject'];
        $wide = $cell['columns'] ?? 1;
        $high = $cell['rows'] ?? 1;
        for ($c = $cell['column']; $c < $cell['column'] + $wide; $c++) {
            for ($r = $cell['row']; $r < $cell['row'] + $high; $r++) {
                $ground["$c,$r"] = $code;
            }
        }
        $subject = $subjects[$code] ?? null;
        $spread = $subject['cover'] ?? null;
        if ($spread === null || ($spread['columns'] <= $wide && $spread['rows'] <= $high)) {
            continue;
        }
        $left = $cell['column'] - intdiv($spread['columns'] - $wide, 2);
        $top = $cell['row'] - intdiv($spread['rows'] - $high, 2);
        $canopies[] = ['code' => $code, 'column' => $cell['column'], 'row' => $cell['row'],
                       'left' => $left, 'top' => $top,
                       'right' => $left + $spread['columns'] - 1, 'bottom' => $top + $spread['rows'] - 1];
    }

    // Un sujet SOUS un couvert n'est un problème que s'il se dresse : l'herbe et le sol poussent très bien à l'ombre d'un arbre, et c'est même ce qu'on veut.
    // Un cours d'eau est aussi plat qu'un chemin : il coule sous les branches sans gêner personne, et l'oublier faisait déplacer la rivière pour préserver un arbre.
    // Les valeurs de type sont en anglais depuis le 2026-08-12 ; le calque « sol », lui, garde son nom — deux notions, un seul mot autrefois.
    $flat = ['ground', 'path', 'grass', 'stream'];
    foreach ($canopies as $canopy) {
        for ($c = $canopy['left']; $c <= $canopy['right']; $c++) {
            for ($r = $canopy['top']; $r <= $canopy['bottom']; $r++) {
                $other = $ground["$c,$r"] ?? null;
                if ($other === null || $other === $canopy['code']) {
                    continue;
                }
                if (in_array($subjects[$other]['type'] ?? '', $flat, true)) {
                    continue;
                }
                // LE TYPE DE CHACUN EST DIT, ET C'EST CE QUI PERMET DE JUGER. « TR-063 sous TR-060 » n'apprend rien à qui ne connaît pas les codes par cœur ; « un arbre sous
                // un arbre » se juge tout de suite, et « un cours d'eau sous un arbre » se reconnaît comme un faux problème — c'est exactement l'erreur que ce contrôle a
                // faite une fois, en rangeant une rivière parmi les sujets qui se dressent.
                printf("  DANS LE COUVERT  %s (%s) en (%d,%d) est sous le couvert %d × %d de %s (%s) posé en (%d,%d)\n",
                    $other, $subjects[$other]['type'] ?? 'type inconnu', $c, $r,
                    $subjects[$canopy['code']]['cover']['columns'], $subjects[$canopy['code']]['cover']['rows'],
                    $canopy['code'], $subjects[$canopy['code']]['type'] ?? 'type inconnu',
                    $canopy['column'], $canopy['row']);
                $faults++;
            }
        }
    }
}

echo $faults === 0 ? "AUCUN SUJET SOUS UN COUVERT\n" : "$faults constat(s) — à corriger ou à assumer, ce contrôle ne bloque rien\n";
exit(0);

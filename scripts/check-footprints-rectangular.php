<?php
/**
 * USAGE
 *   php scripts/check-footprints-rectangular.php — every footprint of the referential is a FULL RECTANGLE, which is what the whole chain assumes today.
 *   Exit code 0 while that holds, 1 the day it stops.
 *   php scripts/check-footprints-rectangular.php <référentiel.json> — the same, on that file: this is what its trial hands over.
 *   php scripts/check-footprints-rectangular.php -h|--help — this text.
 *
 * INTENTION
 *   A FOOTPRINT ONLY KNOWS HOW TO BE A RECTANGLE, AND THE DAY THAT STOPS BEING TRUE, THREE THINGS BECOME FALSE AT ONCE (`S95 emprise-non-rect`, and the
 *   operator's warning of 2026-08-13: « demain si je te donne un bâtiment en L à produire, ça ne doit pas se retrouver faux »). The referential would declare
 *   160 occupied tiles for an L that occupies 110; the composition plan would believe that space taken; and the consigne would prescribe « un rectangle plein »
 *   to a subject that is not one — which the generator would obey, since it is the most concrete clause it receives about the ground.
 *
 *   THE POINT ITSELF SAYS NOT TO FIX THIS NOW, AND IT IS RIGHT: every footprint IS rectangular today, the clause says true, and the camera's geometric tests
 *   lean on that rectangle to be checkable by eye. Rewriting them for a case that does not exist would cost the very defect we just spent three days removing.
 *
 *   SO WHAT IS BUILT HERE IS THE TRIGGER, NOT THE FIX. The point waits on an event — the first subject whose footprint is not a full rectangle — and an event
 *   nobody watches for is an event discovered too late, after generations have been spent on a consigne prescribing the wrong ground plan. This check watches,
 *   and it names the point to open.
 *
 *   IT READS `footprint` AND NOTHING ELSE: `passage` already names tiles one by one, so the notion of an individual tile exists in the model — it is the
 *   footprint alone that has no right to it. A footprint that grows a `tiles` key, or whose `columns`/`rows` stop being two plain positive integers, is the
 *   signal.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);

// THE REFERENTIAL IS HANDED OVER, AND THAT IS WHAT MAKES THIS CHECK PROVABLE: its trial feeds it broken footprints without ever touching the project's own.
$path = $argv[1] ?? $root . '/assets/subjects.json';
if (!is_file($path)) {
    fwrite(STDERR, "FAULT le référentiel « $path » est absent.\n");
    exit(1);
}
$referential = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
$subjects = $referential['subjects'] ?? [];
if ($subjects === []) {
    fwrite(STDERR, "FAULT le référentiel ne déclare aucun sujet : un contrôle qui n'a rien lu ne peut rien conclure.\n");
    exit(1);
}

/** The keys a rectangular footprint may carry, and no other. Anything else is the shape this chain cannot express. */
const RECTANGULAR_KEYS = ['columns', 'rows'];

$faults = [];
foreach ($subjects as $code => $subject) {
    $footprint = $subject['footprint'] ?? null;
    if (!is_array($footprint)) {
        $faults[] = "« $code » ne déclare aucune emprise, alors que toute la chaîne en lit une.";
        continue;
    }
    foreach (array_keys($footprint) as $key) {
        if (!in_array($key, RECTANGULAR_KEYS, true) && !str_starts_with($key, '_')) {
            $faults[] = "« $code » porte une emprise avec la clé « $key » : elle n'est plus un simple rectangle.";
        }
    }
    foreach (RECTANGULAR_KEYS as $key) {
        $value = $footprint[$key] ?? null;
        if (!is_int($value) || $value < 1) {
            $faults[] = "« $code » déclare « $key » = " . var_export($value, true) . ", alors qu'un rectangle plein demande un entier d'au moins 1.";
        }
    }
}

if ($faults === []) {
    printf("Les %d sujets déclarent une emprise rectangulaire pleine : la chaîne dit vrai.\n", count($subjects));
    exit(0);
}
foreach ($faults as $fault) {
    fwrite(STDERR, "FAULT $fault\n");
}
fwrite(STDERR, "\nCE N'EST PAS UN DÉFAUT À CORRIGER ICI, C'EST LE SIGNAL QU'ATTENDAIT « S95 emprise-non-rect ».\n"
    . "  Solution — ouvrir ce point AVANT de produire ce sujet : le référentiel mentirait sur les cases occupées, et la consigne\n"
    . "  prescrirait un rectangle plein à un sujet qui n'en est pas un. « php scripts/backlog.php show emprise-non-rect » dit tout.\n");
exit(1);

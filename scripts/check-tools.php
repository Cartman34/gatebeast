<?php
/**
 * USAGE
 *   php scripts/check-tools.php        the verdict: which commands lack their usage block, their help, or name — anywhere in their header or their code — a file that no longer exists
 *   php scripts/check-tools.php -v     the same, with every finding spelled out
 *   php scripts/check-tools.php -h     this text
 *
 * INTENTION
 *   NO COMMAND EXISTS WITHOUT ITS HELP AND WITHOUT BEING REFERENCED, and a rule only vigilance applies is a rule that does not apply (opérateur, 2026-08-12 :
 *   « une commande/script du projet ne doit JAMAIS exister sans aide ni être référencée, sinon c'est juste poubelle, ça sert à rien »). This is what holds it.
 *
 *   THREE FAULTS, AND EACH ONE HAS BEEN PAID FOR:
 *     - NO USAGE BLOCK: nobody can tell what the command does without reading it whole, so nobody uses it, so it withers — and the next agent writes it again.
 *     - NO HELP ON `-h` / `--help`: the inventory says what a command is for, its help says how to call it. A command answering nothing to the two flags
 *       everyone tries first is a command one gives up on.
 *     - A FILE NAMED THAT NO LONGER EXISTS, and it is read in the WHOLE file, not only in the usage block: worse than silence, it sends the reader to something
 *       that is not there — and when the name sits in an executed line rather than in a help, it does not mislead, it CRASHES. `scripts/sprite-queue.py` called
 *       two generators that had been merged away days earlier; its header described the dead chain and its code called it, and the check read neither because
 *       both sat outside the usage block. Only paths written in full are judged — see Tools::deadPaths, which says why one the code assembles cannot be.
 *
 *   THE REFERENCE ITSELF NEEDS NO CHECKING, because it is generated: `php scripts/tools.php list` reads the commands rather than a list kept beside them, so a
 *   command cannot be absent from it. What can be missing is what a command says about itself, and that is what is checked here.
 *
 *   THE DOCUMENTS HAVE THEIR OWN READER, AND THE TWO ARE NOT A DUPLICATE — said here so that nobody merges them in six months believing they are.
 *   `scripts/check-cited-paths.php` judges the paths a DOCUMENT names: there a dead path is a promise made to a human, who then looks for his own mistake. Here
 *   it sits in something that runs, so it crashes instead. Two natures of fault, so two sets of rules, legitimately different — the documents' reader tolerates
 *   the generic and the illustrative, which this one cannot afford.
 */

require_once __DIR__ . '/Tools.php';

$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    echo implode("\n", Tools::get()->usageOf(__FILE__) ?? []), "\n";
    exit(0);
}

$tools = Tools::get();
$mute = [];
$helpless = [];
$dead = [];
foreach ($tools->all() as $relative => $name) {
    $path = dirname(__DIR__) . '/' . $relative;
    $usage = $tools->usageOf($path);
    if ($usage === null) {
        $mute[] = $relative;
        continue;
    }
    // A FILE THAT IS ONLY REQUIRED IS NOT ASKED FOR A HELP IT CAN NEVER GIVE: its own usage says so, and asking anyway would be the checker crying on what it
    // announces it ignores — the failure that switches a checker off.
    if ($tools->isCalled($usage) && !$tools->answersHelp($path)) {
        $helpless[] = $relative;
    }
    // A TRIAL IS NOT ASKED WHETHER ITS PATHS EXIST, BECAUSE ITS JOB IS TO INVENT ONES THAT DO NOT. Feeding a guard the payload it must refuse means naming files
    // nobody ever wrote, on purpose, under whichever directory the rule being tried is about. Reported, they made the check red for doing its work exactly
    // right, which is how a check stops being run. What is lost is small and said here rather than discovered: a trial that cites a REAL script gone missing,
    // in its own header, is not caught by this.
    if (!str_starts_with($name, 'trial-') && !str_starts_with($name, 'test-')) {
        foreach ($tools->deadPaths($path) as [$line, $missing]) {
            $dead[] = "{$relative}:{$line} — nomme « {$missing} », qui n'existe pas";
        }
    }
}

$total = count($mute) + count($helpless) + count($dead);
printf("%d commande(s) : %d sans bloc d'usage, %d sans aide sur -h/--help, %d qui nomme(nt) un fichier disparu.\n",
    count($tools->all()), count($mute), count($helpless), count($dead));

if ($detail) {
    foreach (['SANS BLOC D\'USAGE' => $mute, 'SANS AIDE SUR -h/--help' => $helpless, 'NOMME UN FICHIER DISPARU' => $dead] as $title => $lines) {
        if (!$lines) {
            continue;
        }
        printf("\n%s\n", $title);
        foreach ($lines as $line) {
            printf("  %s\n", $line);
        }
    }
} elseif ($total > 0) {
    printf("« -v » les nomme.\n");
}

exit($total > 0 ? 1 : 0);

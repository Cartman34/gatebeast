<?php
/**
 * USAGE
 *   php scripts/tools.php [list]        every command of the project, by family, with the one line that says what it does
 *   php scripts/tools.php show <name>   one command in full: its usage block, as its own file states it
 *   php scripts/tools.php -h|--help     this text
 *
 * INTENTION
 *   NO COMMAND EXISTS WITHOUT ITS HELP AND WITHOUT BEING REFERENCED (opérateur, 2026-08-12 : « une commande/script du projet ne doit JAMAIS exister sans aide ni
 *   être référencée, sinon c'est juste poubelle, ça sert à rien »). This is the reference, and it is the first place to look before writing a new command — an
 *   inventory nobody can consult is what makes each of us rebuild what already exists.
 *
 *   IT IS READ OFF THE COMMANDS, NEVER KEPT BY HAND. A hand-written list is a copy: it drifts the first time someone in a hurry adds a tool, and that is exactly
 *   what happened — eight probes and ten readers lived outside the list the tracking document held, while that same list promised tools that no longer ran. This
 *   one opens each file and quotes its own usage block, so it can lie neither about what exists nor about what it does.
 *
 *   WHAT IT KNOWS LIVES IN A SERVICE, `scripts/Tools.php`, shared with `check-tools.php` which refuses the commands that say nothing about themselves. Two copies
 *   of « what counts as a command » would answer differently the day one of them learns about a new directory.
 */

require_once __DIR__ . '/Tools.php';

$tools = Tools::get();
$command = $argv[1] ?? 'list';

// THE HELP IS `-h` AND `--help`, NEVER A SUBCOMMAND (opérateur, 2026-08-12 : « surtout jamais une sous-commande »). It is what everyone tries first, and what
// every other command on the system answers; a `help` subcommand has to be looked for, and it collides with the real subcommands of the tool.
if (in_array($command, ['-h', '--help'], true)) {
    echo implode("\n", $tools->usageOf(__FILE__) ?? []), "\n";
    exit(0);
}

if ($command === 'show') {
    $wanted = $argv[2] ?? '';
    $matches = array_filter($tools->all(), fn (string $name) => $name === $wanted || pathinfo($name, PATHINFO_FILENAME) === $wanted);
    if (!$matches) {
        throw new RuntimeException("FAUTE aucune commande ne s'appelle « {$wanted} » — « php scripts/tools.php list » les donne toutes.");
    }
    foreach (array_keys($matches) as $relative) {
        $usage = $tools->usageOf(dirname(__DIR__) . '/' . $relative);
        printf("%s\n%s\n", $relative, str_repeat('—', mb_strlen($relative)));
        echo $usage === null ? "  AUCUN BLOC D'USAGE — cette commande ne dit pas ce qu'elle fait.\n" : '  ' . implode("\n  ", $usage) . "\n";
    }
    exit(0);
}

if ($command !== 'list') {
    throw new RuntimeException("FAUTE « {$command} » n'est pas une sous-commande — list, show. L'aide est « -h » ou « --help ».");
}

$byFamily = [];
$mute = 0;
foreach ($tools->all() as $relative => $name) {
    $usage = $tools->usageOf(dirname(__DIR__) . '/' . $relative);
    $mute += $usage === null ? 1 : 0;
    // ONE LINE PER COMMAND IN THE LIST, WHICH IS WHAT MAKES IT READABLE: the first line of its usage block. The whole block is one `show` away.
    $byFamily[$tools->familyOf($name)][] = [$relative, $usage[0] ?? null];
}

printf("%d commande(s) — « php scripts/tools.php show <nom> » ouvre l'une d'elles en entier.\n", count($tools->all()));
foreach (array_merge(array_values(Tools::FAMILIES), [Tools::FAMILY_LOOK, Tools::FAMILY_REST]) as $title) {
    if (empty($byFamily[$title])) {
        continue;
    }
    printf("\n%s\n", $title);
    foreach ($byFamily[$title] as [$relative, $first]) {
        printf("  %-52s %s\n", $relative, $first ?? 'SANS BLOC D\'USAGE — elle ne dit pas ce qu\'elle fait');
    }
}

if ($mute > 0) {
    printf("\n%d commande(s) sans bloc d'usage — « php scripts/check-tools.php » en fait une faute.\n", $mute);
}

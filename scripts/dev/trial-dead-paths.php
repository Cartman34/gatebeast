<?php
/**
 * USAGE
 *   php scripts/dev/trial-dead-paths.php            feeds Tools::deadPaths the lines it must report and the ones it must ignore, and reports
 *   php scripts/dev/trial-dead-paths.php -h|--help  this text
 *
 *   Writes one sample file under var/tmp/ and reads nothing else. Exits non-zero as soon as one case answers the wrong way.
 *
 * INTENTION
 *   THE CHECK WAS WIDENED FROM THE USAGE BLOCK TO THE WHOLE FILE, code included (opérateur, 2026-08-12), and widening it is exactly what makes it able to be
 *   wrong at scale: it now reads every line of a hundred commands instead of five lines of each. The first run proved it — nine of its twenty finds were Python
 *   attributes read as shell scripts, `self.shape` reported as `self.sh`, because the suffix was matched without a word boundary. That mistake cost nothing
 *   because the finds were read; the same mistake in the other direction — a real dead path stopped being reported — would have cost nothing to notice either,
 *   and that is the problem.
 *
 *   SO BOTH DIRECTIONS ARE PINNED HERE, and the silent one first: what the check must NOT say is the half nobody can see. A path the code assembles from
 *   variables cannot be judged and must stay quiet; an argument the operator supplies, `<requests.json>`, is not a file of this repository; `var/tmp/` holds
 *   what a program throws away. Each of those is a reason to be quiet that a later change could break without anyone noticing.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$root = dirname(__DIR__, 2);
$sample = $root . '/var/tmp/trial-dead-paths/sample.txt';
if (!is_dir(dirname($sample))) {
    mkdir(dirname($sample), 0777, true);
}

// One case per line, so a line number IS the case. Keep the two lists below in step with it.
file_put_contents($sample, implode("\n", [
    'CE QUI DOIT RESTER MUET',
    'shape = self.shape                                     # un attribut, pas un script shell',
    'text = asset_common.sheet_description(sheet, code)     # idem, sur deux mots',
    'queue = REPO / "local" / "sprite-queue.jsonl"          # une extension qui en contient une autre',
    'php scripts/sprite-queue.py add <requests.json>        # un argument fourni par l opérateur',
    'run("rm -f var/tmp/probe.png")                         # le jetable d un programme',
    'target = REPO / directory / name                       # un chemin assemblé, invérifiable',
    'require_once "$root/scripts/Tools.php";                # un chemin vivant, barre oblique de tête',
    'CE QUI DOIT ÊTRE SIGNALÉ',
    'python3 scripts/pas-la.py --generate',
    'require_once "$root/scripts/absente.php";',
    'command = ["python3", str(REPO / "scripts" / "disparue.py")]',
]) . "\n");

$found = [];
foreach (Tools::get()->deadPaths($sample) as [$line, $missing]) {
    $found[$line] = $missing;
}

$silent = [2, 3, 4, 5, 6, 7, 8];
$reported = [10 => 'scripts/pas-la.py', 11 => 'scripts/absente.php', 12 => 'disparue.py'];

$failures = 0;
echo "Ce que le contrôle doit taire\n";
foreach ($silent as $line) {
    if (isset($found[$line])) {
        printf("  RATÉ  ligne %d — aurait dû se taire, il signale « %s »\n", $line, $found[$line]);
        $failures++;
        continue;
    }
    printf("  OK    ligne %d\n", $line);
}

echo "Ce que le contrôle doit signaler\n";
foreach ($reported as $line => $expected) {
    if (($found[$line] ?? null) !== $expected) {
        printf("  RATÉ  ligne %d — attendait « %s », a rendu « %s »\n", $line, $expected, $found[$line] ?? 'rien');
        $failures++;
        continue;
    }
    printf("  OK    ligne %d — %s\n", $line, $expected);
}

echo "\n";
if ($failures === 0) {
    echo "Les chemins morts se signalent, et ce qui ne se vérifie pas reste muet.\n";
    exit(0);
}
printf("%d cas répondent à l'envers.\n", $failures);
exit(1);

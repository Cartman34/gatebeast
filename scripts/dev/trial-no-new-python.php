<?php
/**
 * USAGE
 *   php scripts/dev/trial-no-new-python.php            feeds PythonFreeze a repository of its own and checks what it refuses and what it lets through
 *   php scripts/dev/trial-no-new-python.php -h|--help  this text
 *
 *   Builds a throwaway git repository under var/tmp/ and never reads the real roll. Exits non-zero as soon as one case answers the wrong way.
 *
 * INTENTION
 *   THE RULE IS HELD BY THIS CHECK ALONE, so what the check gets wrong, the rule gets wrong. Two directions matter and only one of them is visible: a new file
 *   that stops being refused looks exactly like a repository where nobody added Python. Nothing would say otherwise until someone counted the files by hand,
 *   which is the day the rule turns out to have been off for weeks.
 *
 *   IT WORKS ON A REPOSITORY IT BUILDS ITSELF, never on this one. Asking the real roll would make the trial pass or fail with whatever the project happens to
 *   carry today, so it would stop testing the code and start testing the repository — and it could not exercise the one case that matters, a file that is not on
 *   the roll, without adding Python to the project it is defending.
 */

require_once dirname(__DIR__) . '/PythonFreeze.php';
require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$sandbox = dirname(__DIR__, 2) . '/var/tmp/trial-no-new-python';
exec(sprintf('rm -rf %s && mkdir -p %s/scripts', escapeshellarg($sandbox), escapeshellarg($sandbox)));
exec(sprintf('git -C %s init -q 2>&1', escapeshellarg($sandbox)), $output, $status);
if ($status !== 0) {
    throw new RuntimeException("le dépôt d'essai ne s'initialise pas : " . implode("\n", $output));
}

/**
 * Puts these files in the sandbox and tracks them, so `git ls-files` sees exactly this set.
 *
 * IT CLEARS THE SOURCES ONE BY ONE AND NEVER THE DIRECTORY: the roll lives under `scripts/` too, and wiping the folder took it away with them — the service then
 * raised « le relevé manque » in the middle of the trial, which is the right answer to the wrong question.
 */
function track(string $sandbox, array $files): void
{
    exec(sprintf('git -C %s rm -r --cached -q . 2>&1', escapeshellarg($sandbox)));
    foreach (glob($sandbox . '/scripts/*.{py,php}', GLOB_BRACE) ?: [] as $stale) {
        unlink($stale);
    }
    foreach ($files as $file) {
        file_put_contents($sandbox . '/' . $file, "# essai\n");
    }
    exec(sprintf('git -C %s add -A 2>&1', escapeshellarg($sandbox)));
}

$failures = 0;

function expect(string $what, array $wanted, array $got): void
{
    global $failures;
    sort($wanted);
    sort($got);
    if ($wanted === $got) {
        printf("  OK    %s\n", $what);

        return;
    }
    printf("  RATÉ  %s — attendait [%s], a rendu [%s]\n", $what, implode(', ', $wanted), implode(', ', $got));
    $failures++;
}

$freeze = new PythonFreeze($sandbox);

echo "Le relevé se fige sur ce qui est suivi\n";
track($sandbox, ['scripts/un.py', 'scripts/deux.py', 'scripts/garde.php']);
$frozen = $freeze->freeze();
expect('deux fichiers Python figés, le PHP écarté', ['scripts/deux.py', 'scripts/un.py'], $frozen);

echo "Ce qui ne doit rien lever\n";
$freeze = new PythonFreeze($sandbox);
expect('le dépôt inchangé', [], $freeze->added());

track($sandbox, ['scripts/un.py', 'scripts/garde.php']);
$freeze = new PythonFreeze($sandbox);
expect('un fichier Python SUPPRIMÉ — le Python peut décroître', [], $freeze->added());

track($sandbox, ['scripts/un.py', 'scripts/deux.py', 'scripts/garde.php', 'scripts/neuf.php']);
$freeze = new PythonFreeze($sandbox);
expect('un fichier PHP neuf', [], $freeze->added());

echo "Ce qui doit être refusé\n";
track($sandbox, ['scripts/un.py', 'scripts/deux.py', 'scripts/neuf.py', 'scripts/garde.php']);
$freeze = new PythonFreeze($sandbox);
expect('un fichier Python neuf', ['scripts/neuf.py'], $freeze->added());

track($sandbox, ['scripts/un.py', 'scripts/deux.py', 'scripts/neuf.py', 'scripts/autre.py']);
$freeze = new PythonFreeze($sandbox);
expect('deux fichiers Python neufs', ['scripts/autre.py', 'scripts/neuf.py'], $freeze->added());

track($sandbox, ['scripts/neuf.py', 'scripts/garde.php']);
$freeze = new PythonFreeze($sandbox);
expect('un Python neuf ET un ancien retiré — seul le neuf compte', ['scripts/neuf.py'], $freeze->added());

echo "\n";
if ($failures === 0) {
    echo "Le Python neuf est refusé, le Python retiré ne dit rien, et le PHP passe.\n";
    exit(0);
}
printf("%d cas répondent à l'envers.\n", $failures);
exit(1);

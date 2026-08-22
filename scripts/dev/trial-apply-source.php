<?php
/**
 * USAGE
 *   php scripts/dev/trial-apply-source.php — proves that a version written by apply-source.php can be REBUILT from its edits journal. Exit code 0 when every
 *   case is green, 1 otherwise.
 *   php scripts/dev/trial-apply-source.php -h|--help — this text.
 *
 * INTENTION
 *   THE DEFECT THIS GUARDS AGAINST LOOKED EXACTLY LIKE CORRECT WORK (`W36 edits-incomplets`). `apply-source.php` wrote the version and inscribed nothing: the
 *   journal stayed well-formed, replayed without raising a single fault, and produced a DIFFERENT text from the one on the page. No check could see it, because
 *   nothing compared the two — so this trial does exactly that, and it is the only thing that can.
 *
 *   IT WORKS ON A SUBJECT OF ITS OWN, `ZZ-000`, created and removed by the trial. The workshop's real subjects are the operator's data: a trial that writes on
 *   them would be a probe that alters what it observes, and this repository has already paid for that twice.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Prompts.php';

Tools::get()->helpIfAsked($argv, __FILE__);

const SUBJECT = 'ZZ-000';
const BLOCK = 'projection';

$prompts = Prompts::get();
$home = $prompts->homeOf(SUBJECT);

/** Everything the trial wrote goes away, whether it succeeded or not — a leftover subject would show up in the workshop as a real one. */
function sweep(string $home): void
{
    foreach (glob($home . '/*') ?: [] as $path) {
        unlink($path);
    }
    if (is_dir($home)) {
        rmdir($home);
    }
}

/**
 * REJOUE UN JOURNAL D'ÉDITS, et le rejeu vit ICI plutôt que dans un script appelé. Deux raisons, et la seconde est la vraie : un essai versionné ne peut pas
 * dépendre d'un fichier de `local/`, qui n'est pas versionné et peut n'exister sur aucune autre machine ; et ce que cet essai vérifie, c'est la RÈGLE du rejeu —
 * un « before » qui se trouve exactement une fois —, pas le comportement d'un outil particulier.
 */
function replay(string $text, array $edits, ?string &$why): ?string
{
    foreach ($edits as $rank => $edit) {
        $found = substr_count($text, $edit['before']);
        if ($found !== 1) {
            $why = sprintf('l\'édit %d trouve %d occurrence(s) de son texte source, il en faut exactement une', $rank + 1, $found);

            return null;
        }
        $text = str_replace($edit['before'], $edit['after'], $text);
    }

    return $text;
}

sweep($home);
if (!mkdir($home, 0o777, true) && !is_dir($home)) {
    fwrite(STDERR, "FAULT le foyer d'essai « $home » ne se crée pas.\n");
    exit(1);
}

/**
 * A GENERATED v1, because that is what the chain starts from: `pendingRank()` names the version FOLLOWING the last one that carries an image, so without an
 * image there is no pending version and apply-source has nothing to write into.
 */
$first = <<<'TEXTE'
## CE QUE TU PRODUIS

Une sprite d'essai, et rien d'autre.

### Caméra (common)
Une phrase de caméra que le bloc de source doit remplacer entièrement.

### Le sujet (description)
Un sujet d'essai, décrit en une ligne.
TEXTE;
file_put_contents($prompts->file(SUBJECT, 1, 'prompt'), $first . "\n");
file_put_contents($prompts->file(SUBJECT, 1, 'image'), base64_decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='));

$applied = $root . '/review-server/workshop/apply-source.php';
exec('php ' . escapeshellarg($applied) . ' ' . SUBJECT . ' ' . BLOCK . ' 2>&1', $said, $code);
if ($code !== 0) {
    fwrite(STDERR, "FAULT apply-source.php a refusé sur le sujet d'essai :\n  " . implode("\n  ", $said) . "\n");
    sweep($home);
    exit(1);
}

$green = true;

/** CASE 1 — the journal exists at all. Before the fix it simply was not written, and that is the whole defect in one line. */
$journalPath = $prompts->file(SUBJECT, 2, 'edits');
if (!is_file($journalPath)) {
    fwrite(STDERR, "ROUGE le journal d'édits n'a pas été écrit : « " . basename($journalPath) . " » est absent.\n");
    sweep($home);
    exit(1);
}
printf("VERT   le journal d'édits est écrit — %s\n", basename($journalPath));

/** CASE 2 — it carries one edit, named after the block it came from, so a reader knows where the text is to be corrected. */
$journal = json_decode(file_get_contents($journalPath), true, 512, JSON_THROW_ON_ERROR);
$edits = $journal['edits'] ?? [];
if (count($edits) !== 1 || ($edits[0]['id'] ?? '') !== 'source-' . BLOCK) {
    fwrite(STDERR, sprintf("ROUGE le journal porte %d édit(s), d'identifiants « %s » — attendu un seul, « source-%s ».\n",
        count($edits), implode(', ', array_column($edits, 'id')), BLOCK));
    $green = false;
} else {
    printf("VERT   il porte un édit, « %s »\n", $edits[0]['id']);
}

/** CASE 3 — AND THIS IS THE ONE THAT MATTERS: replaying the journal on v1 gives back v2, byte for byte. */
$rebuilt = replay(file_get_contents($prompts->file(SUBJECT, 1, 'prompt')), $edits, $why);
if ($rebuilt === null) {
    fwrite(STDERR, "ROUGE le rejeu du journal a échoué : $why\n");
    $green = false;
} elseif ($rebuilt !== file_get_contents($prompts->file(SUBJECT, 2, 'prompt'))) {
    fwrite(STDERR, "ROUGE le rejeu donne un AUTRE texte que la version écrite — c'est exactement le défaut W36.\n");
    $green = false;
} else {
    printf("VERT   rejouer le journal sur la v1 redonne la v2, octet pour octet\n");
}

/** CASE 4 — applying the same block twice does not lose the first state: two edits, and the replay still reconstructs. */
exec('php ' . escapeshellarg($applied) . ' ' . SUBJECT . ' ' . BLOCK . ' 2>&1', $again, $againCode);
$journal = json_decode(file_get_contents($journalPath), true, 512, JSON_THROW_ON_ERROR);
if ($againCode !== 0 || count($journal['edits'] ?? []) !== 2) {
    fwrite(STDERR, sprintf("ROUGE une deuxième application donne %d édit(s), attendu 2.\n", count($journal['edits'] ?? [])));
    $green = false;
} else {
    printf("VERT   une deuxième application s'ajoute au journal au lieu d'écraser la première\n");
}

sweep($home);
echo $green ? "Tous les cas sont verts.\n" : "Des cas sont rouges.\n";
exit($green ? 0 : 1);

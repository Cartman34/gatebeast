<?php
/**
 * USAGE
 *   php scripts/generate-version.php <consigne.txt> — generates the image of one VERSION of a consigne and records what produced it.
 *   php scripts/generate-version.php -h|--help — this text, and nothing is generated.
 *
 *   The image is written beside the consigne, under the same stem — `BT-001.v3.prompt.txt` gives `BT-001.v3.image.png` — which is where the workshop page looks
 *   for it. An existing image is never overwritten: one generation per version, and a relaunch is the operator's call.
 *
 * INTENTION
 *   A GENERATION MUST RECORD ITS SESSION, AND NO AGENT MUST HAVE TO REMEMBER TO (operator, 2026-08-17: « pour chaque génération, donc chaque version, je dois
 *   pouvoir retrouver l'id de la session sous l'image »). Calling the wrapper by hand prints « SESSION <file> <id> » to a terminal and nowhere else: the v4 of
 *   BT-001 lost its session the moment its command was interrupted, and the id that reopens the conversation with the generator — `codex exec resume <id>` — is
 *   gone for good. Written to a file beside the image, it survives the terminal, the summary and the session.
 *
 *   IT RECORDS WHAT IT OBSERVED, NEVER WHAT IT HOPED. No session line in the output means no session written and a command that fails loudly, rather than a
 *   sidecar carrying an empty field that reads, three days later, as a generator that returned nothing.
 */

$root = dirname(__DIR__);
require_once __DIR__ . '/Tools.php';
require_once $root . '/review-server/lib/Prompts.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$prompt = $argv[1] ?? null;
if ($prompt === null || !is_file($prompt)) {
    fwrite(STDERR, "USAGE : php scripts/generate-version.php <SUJET.vN.prompt.txt>\n");
    exit(2);
}
// THE NAME SAYS THE SUBJECT, THE RANK AND WHAT IT IS, and `Prompts` is what reads that mould and hands back the sibling files. Deducing it here by swapping
// an extension would give `…prompt.png`, which names nothing — and would write a convention that already lives elsewhere a second time, in another dialect.
$prompts = Prompts::get();
$named = $prompts->partsOf($prompt);
if ($named === null || $named['what'] !== 'prompt') {
    fwrite(STDERR, "FAULT « $prompt » n'est pas une version de consigne : elle se nomme <SUJET>.v<N>.prompt.txt.\n");
    exit(1);
}
$image = $prompts->beside($prompt, 'image');
if (is_file($image)) {
    fwrite(STDERR, "FAULT « $image » existe déjà : une seule génération par version, et une relance se décide.\n"
        . "  Solution — supprimer l'image pour la refaire, ou écrire une version neuve.\n");
    exit(1);
}

// THE OUTPUT IS CAPTURED RATHER THAN STREAMED, and that is the whole point of this wrapper: the session id is printed once, on a line of that output, and a
// streamed line belongs to the terminal alone. It is echoed back below, so nothing is hidden — only kept.
$command = sprintf('php %s %s @%s', escapeshellarg($root . '/scripts/generate-image.php'), escapeshellarg($image), escapeshellarg($prompt));
exec($command . ' 2>&1', $lines, $status);
echo implode("\n", $lines), "\n";
if ($status !== 0) {
    fwrite(STDERR, "FAULT la génération a échoué (code $status) : rien n'est enregistré.\n");
    exit(1);
}
if (!is_file($image)) {
    fwrite(STDERR, "FAULT la génération s'est terminée sans écrire « $image ».\n");
    exit(1);
}

$session = null;
foreach ($lines as $line) {
    if (preg_match('/^SESSION\s+\S*' . preg_quote(basename($image), '/') . '\s+(\S+)$/', $line, $found)) {
        $session = $found[1];
    }
}
if ($session === null) {
    fwrite(STDERR, "FAULT l'image est écrite mais aucune ligne « SESSION » ne la nomme : la session est perdue et ne se retrouve pas après coup.\n");
    exit(1);
}

$meta = [
    'format' => 'gatebeast-generation',
    'version' => 1,
    'image' => basename($image),
    'prompt' => basename($prompt),
    'session' => $session,
    'generated' => date('c'),
];
file_put_contents($prompts->beside($prompt, 'generation'),
    json_encode($meta, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");

printf("%s — image écrite, session %s\n", $image, $session ?? 'NON RETROUVÉE (le journal du générateur ne la porte pas)');

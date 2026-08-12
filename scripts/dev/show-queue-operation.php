<?php
/**
 * USAGE
 *   php scripts/dev/show-queue-operation.php <transcript.jsonl> — prints the last queue operations found in the transcript: their operation and their content.
 *   php scripts/dev/show-queue-operation.php -h|--help — this text
 *
 * INTENTION
 *   The transcript carries a `queue-operation` entry type beside the `attachment` one that already gives the queued messages. Reading its content as an order would
 *   be wrong if the operation can be a removal — a message the operator cancelled would then be obeyed. So the values are looked at before anything is wired.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$path = $argv[1] ?? null;
if ($path === null || !is_file($path)) {
    throw new RuntimeException('FAUTE usage : php scripts/dev/show-queue-operation.php <transcript.jsonl>');
}

$handle = fopen($path, 'r');
$seen = [];
while (($line = fgets($handle)) !== false) {
    $entry = json_decode($line, true);
    if (!is_array($entry) || ($entry['type'] ?? '') !== 'queue-operation') {
        continue;
    }
    $content = $entry['content'] ?? '';
    $seen[] = sprintf('%-10s %s', (string) ($entry['operation'] ?? '(aucune)'),
        is_string($content) ? str_replace(["\n", "\r"], '⏎', mb_substr($content, 0, 60)) : json_encode($content, JSON_UNESCAPED_UNICODE));
}
fclose($handle);

printf("%d opération(s) de file\n", count($seen));
foreach (array_slice($seen, -12) as $line) {
    printf("  %s\n", $line);
}

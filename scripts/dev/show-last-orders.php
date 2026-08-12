<?php
/**
 * USAGE
 *   php scripts/dev/show-last-orders.php <transcript.jsonl> [count] — prints the last operator messages exactly as the Stop hook reads them, one per line, with
 *   the entry type and the first characters of the text.
 *   php scripts/dev/show-last-orders.php -h|--help — this text
 *
 * INTENTION
 *   THE HOOK'S TEST FEEDS IT A TRANSCRIPT THE AGENT WROTE HIMSELF, which proves the code works on what it is handed and nothing more. On 2026-08-09 the operator
 *   sent STOP twice while the agent was working, the guard refused the end of turn both times, and the hook's own trace showed it had never recognised the word.
 *   Something about a real transcript does not match what the reader expects, and guessing what is exactly the mistake this point exists to forbid. This looks.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$path = $argv[1] ?? null;
if ($path === null) {
    throw new RuntimeException('FAUTE usage : php scripts/dev/show-last-orders.php <transcript.jsonl> [nombre]');
}
if (!is_file($path)) {
    throw new RuntimeException("FAUTE le transcrit « {$path} » n'existe pas");
}
$wanted = (int) ($argv[2] ?? 12);

$handle = fopen($path, 'r');
if ($handle === false) {
    throw new RuntimeException("FAUTE lecture impossible de « {$path} »");
}

$seen = [];
while (($line = fgets($handle)) !== false) {
    $entry = json_decode($line, true);
    if (!is_array($entry)) {
        continue;
    }
    $type = $entry['type'] ?? '(sans type)';
    $content = $entry['message']['content'] ?? null;
    if (is_string($content)) {
        $seen[] = [$type, 'chaîne', $content];
        continue;
    }
    if (!is_array($content)) {
        continue;
    }
    foreach ($content as $chunk) {
        if (!is_array($chunk)) {
            continue;
        }
        $seen[] = [$type, $chunk['type'] ?? '(sans type)', $chunk['text'] ?? ''];
    }
}
fclose($handle);

// Only the tail matters: the question is what the reader sees at the end of the conversation, where the order lives.
$tail = array_slice($seen, -$wanted);
foreach ($tail as [$type, $kind, $text]) {
    $flat = str_replace(["\n", "\r"], '⏎', $text);
    printf("%-10s %-14s %s\n", $type, $kind, mb_substr($flat, 0, 90));
}

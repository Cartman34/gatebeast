<?php
/**
 * USAGE
 *   php scripts/dev/trim-to-ceiling.php <file>...
 *   php scripts/dev/trim-to-ceiling.php -h|--help — this text, and no file is touched
 *
 * INTENTION
 *   Rewraps to 200 the lines that overshoot it by a hair — the exact case a hand fix keeps reintroducing, because moving one word to the next line changes
 *   that line's width too. Only touches lines already within 40 characters of the ceiling, and never a Markdown table row, which cannot be folded at all.
 *   One-shot: a real reflow of the older documents is another job, and this one only closes the overshoot the checker just reported.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

foreach (array_slice($argv, 1) as $path) {
    $lines = explode("\n", file_get_contents($path));
    $changed = 0;
    foreach ($lines as $index => $line) {
        $width = mb_strlen($line);
        if ($width <= 200 || $width > 240 || preg_match('/^\s*\|/u', $line)) {
            continue;
        }
        $indent = preg_match('/^(\s*)/u', $line, $found) ? $found[1] : '';
        $cut = mb_strrpos(mb_substr($line, 0, 201), ' ');
        $lines[$index] = rtrim(mb_substr($line, 0, $cut)) . "\n" . $indent . ltrim(mb_substr($line, $cut));
        $changed++;
    }
    file_put_contents($path, implode("\n", $lines));
    echo "{$path} : {$changed} ligne(s) repliée(s) au plafond\n";
}

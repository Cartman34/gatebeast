<?php
/**
 * USAGE
 *   php scripts/dev/find-orphan-lines.php <file>...
 *   php scripts/dev/find-orphan-lines.php -h|--help — this text
 *
 * INTENTION
 *   Finds the damage a careless rewrap leaves behind: a line pushed to the ceiling followed by a stub of one or two words. Reports them so they can be repaired by hand — repairing them by script is
 *   exactly what caused them. One-shot, kept out of the repository.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

foreach (array_slice($argv, 1) as $path) {
    $lines = explode("\n", file_get_contents($path));
    foreach ($lines as $index => $line) {
        $previous = $index > 0 ? $lines[$index - 1] : '';
        if (mb_strlen($previous) > 180 && mb_strlen(trim($line)) > 0 && mb_strlen(trim($line)) < 25) {
            $number = $index + 1;
            echo "{$path}:{$number} : « " . trim($line) . " » orphelin après une ligne de " . mb_strlen($previous) . "\n";
        }
    }
}

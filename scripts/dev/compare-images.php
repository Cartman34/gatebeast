<?php
/**
 * Usage: php scripts/dev/compare-images.php <sortie.png> <image.png…>   — puts the given images side by side, blown up, on a neutral background.
 *        php scripts/dev/compare-images.php -h|--help — this text.
 *
 * Intention: one-shot, never committed. A sprite is ninety-six pixels wide and is judged on details that do not survive that size — where a piece stops, whether an end is an end. Seen alone each
 * one looks plausible; side by side, a line pretending to be an extremity is obvious. The background is mid-grey so that transparency reads as transparency, not as white.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$outputPath = $argv[1] ?? null;
$paths = array_slice($argv, 2);
if ($outputPath === null || !$paths) {
    throw new RuntimeException('usage : php scripts/dev/compare-images.php <sortie.png> <image.png…>');
}

const BLOW_UP = 3;
const GAP = 16;

$images = [];
foreach ($paths as $path) {
    $images[] = imagecreatefrompng($path);
}

$width = 0;
$height = 0;
foreach ($images as $image) {
    $width += imagesx($image) * BLOW_UP + GAP;
    $height = max($height, imagesy($image) * BLOW_UP);
}

$board = imagecreatetruecolor($width + GAP, $height + 2 * GAP);
imagefill($board, 0, 0, imagecolorallocate($board, 110, 110, 110));
$at = GAP;
foreach ($images as $image) {
    imagecopyresized($board, $image, $at, GAP, 0, 0, imagesx($image) * BLOW_UP, imagesy($image) * BLOW_UP, imagesx($image), imagesy($image));
    $at += imagesx($image) * BLOW_UP + GAP;
}
imagepng($board, $outputPath);

printf("%s — %d image(s) côte à côte, agrandies %d fois\n", $outputPath, count($images), BLOW_UP);

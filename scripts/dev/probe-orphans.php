<?php
/**
 * USAGE
 *   php scripts/dev/probe-orphans.php — screenshots the « Hors modèle » section of the served sprites page, so the unclaimed images are looked at rather than
 *   counted.
 *   php scripts/dev/probe-orphans.php -h|--help — this text
 *
 * INTENTION
 *   That section came back to scanning both image directories, masters included, and each card now says whether it holds a master or a deliverable. A count in
 *   the markup proves the cards exist, not that they read: the checkerboard behind a transparent image, the label and the path all have to be seen together.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$server = ReviewServer::get();
$served = $server->urlFor('/sprites');
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}

// THE IMAGES OF THAT SECTION LOAD LAZILY, and a browser without a screen never asks for them: the first shot came out entirely blank. They are claimed outright
// before anything else.
// AND A HEADLESS SHOT PHOTOGRAPHS THE TOP OF THE PAGE WHATEVER ONE SCROLLS — two empty shots proved it. Everything before the section is hidden instead, which
// brings it to the top: it is still the served page, with its style and its images, only shortened.
$probe = "<script>window.addEventListener('load', function () {"
    . "Array.prototype.forEach.call(document.querySelectorAll('.orphan img'), function (image) {"
    . "  image.loading = 'eager'; image.src = image.src;"
    . "});"
    . "var section = document.querySelector('.orphans').closest('.type');"
    . "var below = false;"
    . "Array.prototype.forEach.call(section.parentNode.children, function (sibling) {"
    . "  if (sibling === section) { below = true; return; }"
    . "  if (!below) { sibling.style.display = 'none'; }"
    . "});"
    . "});</script>";
$copy = $root . '/var/tmp/orphans-probe.html';
file_put_contents($copy, $html . $probe);

$shot = $root . '/var/tmp/tir-orphans.png';
Browser::get()->shot($server->urlFor('/var/tmp/' . basename($copy)), $shot, 1400, 760, 12000);
printf("hors modèle — tir d'écran dans %s\n", $shot);

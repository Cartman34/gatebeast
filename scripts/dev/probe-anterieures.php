<?php
/**
 * USAGE
 *   php scripts/dev/probe-anterieures.php <code du sujet> — opens that subject's panel with its earlier versions unfolded, and screenshots them.
 *   php scripts/dev/probe-anterieures.php -h|--help — this text
 *
 * INTENTION
 *   Earlier versions now claim the same presentation as the current one — same scale, same grid, same measurements. That claim is about pixels, so it is checked on pixels. Throwaway probe.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'BT-001';
$page = file_get_contents($root . '/review-server/suivi-sprites/page.html');
$opened = str_replace("<div class=\"fsp\" id=\"fsp-{$code}\" hidden>", "<div class=\"fsp\" id=\"fsp-{$code}\">", $page);
if ($opened === $page) {
    throw new RuntimeException("FAULT le sujet « {$code} » n'a pas de panneau dans la page construite.");
}

$opened .= "<script>window.addEventListener('load', function () {"
    . "var d = document.querySelectorAll('#fsp-{$code} details.fold');"
    . "Array.prototype.forEach.call(d, function (one) { one.open = true; });"
    . "});</script>";

$out = $root . '/var/tmp/probe-anterieures.html';
@mkdir(dirname($out), 0777, true);
file_put_contents($out, $opened);

$shot = $root . '/var/tmp/probe-anterieures.png';
Browser::get()->shot($out, $shot, 1400, 1400);
printf("%s — versions antérieures de %s dépliées, tir d'écran dans %s\n", $out, $code, $shot);

<?php
/**
 * USAGE
 *   php scripts/dev/probe-texte-cote.php <code du sujet> — opens that subject's panel, clicks its first "prompt" button, and screenshots the result.
 *   php scripts/dev/probe-texte-cote.php -h|--help — this text
 *
 * INTENTION
 *   The whole point of the docked text panel is that the picture stays visible beside it. That claim cannot be checked by reading CSS: it is a question of pixels, and the operator asked for it
 *   precisely because the previous answer looked right in the markup and was useless on screen. Throwaway probe — it exists to look before showing.
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

// LE CLIC EST UN VRAI CLIC : c'est le gestionnaire de la page qui remplit le panneau, et le simuler à la main montrerait un panneau que personne n'a ouvert.
$opened .= "<script>window.addEventListener('load', function () {"
    . "var b = document.querySelector('#fsp-{$code} .open-text'); if (b) { b.click(); }"
    . "});</script>";

$out = $root . '/var/tmp/probe-texte-cote.html';
@mkdir(dirname($out), 0777, true);
file_put_contents($out, $opened);

$shot = $root . '/var/tmp/probe-texte-cote.png';
Browser::get()->shot($out, $shot, 1400, 1100);
printf("%s — texte de %s ouvert à côté de l'image, tir d'écran dans %s\n", $out, $code, $shot);

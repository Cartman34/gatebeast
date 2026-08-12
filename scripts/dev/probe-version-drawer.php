<?php
/**
 * USAGE
 *   php scripts/dev/probe-version-drawer.php [code] — opens that subject's panel in a copy of the served sprites page, clicks the first « Voir cette version »,
 *   and photographs what the drawer shows.
 *   php scripts/dev/probe-version-drawer.php -h|--help — this text
 *
 * INTENTION
 *   Le panneau porte désormais UNE VERSION, pas un texte : son image en grand et ses sections. Rien de cela ne se lit dans le code — le contenu est DÉPLACÉ dans
 *   le panneau à l'ouverture, et c'est le navigateur, seul, qui dit si l'image y est grande et si les sections y sont. Trois défauts d'affichage ont été
 *   diagnostiqués faux en une soirée en lisant le code ; un tir d'écran les a tranchés en une fois.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'TR-063';
$served = ReviewServer::get()->urlFor('/sprites');
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}
$opened = str_replace("<div class=\"fsp\" id=\"fsp-{$code}\" hidden>", "<div class=\"fsp\" id=\"fsp-{$code}\">", $html);
if ($opened === $html) {
    throw new RuntimeException("FAULT le sujet « {$code} » n'a pas de panneau dans la page construite.");
}

$probe = "<script>window.addEventListener('load', function () {"
    . "setTimeout(function () {"
    . "  var panneau = document.getElementById(" . json_encode("fsp-{$code}") . ");"
    . "  var bouton = panneau.querySelector('.open-version');"
    . "  if (bouton) { bouton.click(); }"
    . "}, 600);"
    . "});</script>";

$copy = $root . '/var/tmp/sonde-panneau-version.html';
file_put_contents($copy, $opened . $probe);
$shot = $root . '/var/tmp/panneau-version.png';
Browser::get()->shot(ReviewServer::get()->urlFor('/var/tmp/' . basename($copy)), $shot, 1500, 1100, 12000);
printf("%s — panneau de %s, première version ouverte\n", $shot, $code);

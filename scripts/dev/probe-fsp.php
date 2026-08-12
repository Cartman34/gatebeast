<?php
/**
 * USAGE
 *   php scripts/dev/probe-fsp.php <code du sujet> — writes var/tmp/probe-fsp.html, the built sprites page with that subject's panel already open, ready to be screenshotted.
 *   php scripts/dev/probe-fsp.php -h|--help — this text
 *
 * INTENTION
 *   The panel only opens on a click, and this machine has no scriptable browser to click with — Playwright's browsers are on disk but its Python module is not installed. Un-hiding the panel in a
 *   copy of the page gives the same pixels without driving anything: the markup and the styles are the page's own, untouched. Throwaway probe, kept under local/ because the agent must look at what
 *   it just built before showing it — five defects in a row reached the operator because nobody opened the page.
 *
 *   ET LA COPIE S'OUVRE PAR LE SERVEUR, PLUS PAR LE DISQUE (2026-08-12, point W21). Depuis que le style et le script de la page vivent dans leurs propres fichiers, atteints par un chemin absolu, une
 *   copie ouverte en `file://` sort NUE : ni style, ni script, ni verdicts. La sonde montrait alors une page qui ne ressemble à rien de ce que l'opérateur voit — et rendait une image, donc un verdict
 *   favorable rendu sans avoir rien pu contrôler. Écrite sous `var/tmp/`, que le serveur sert déjà, elle est de la même origine et tout se charge.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once $root . '/review-server/lib/Probe.php';
require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'OB-010';
$page = Probe::get()->page('/sprites');
$opened = str_replace("<div class=\"fsp\" id=\"fsp-{$code}\" hidden>", "<div class=\"fsp\" id=\"fsp-{$code}\">", $page);
if ($opened === $page) {
    throw new RuntimeException("FAULT le sujet « {$code} » n'a pas de panneau dans la page construite.");
}
$address = Probe::get()->serve($opened, '', 'probe-fsp');

// LE TIR D'ÉCRAN EST DANS LE SCRIPT, PAS DANS UNE COMMANDE TAPÉE (opérateur, 2026-08-07 : « interdiction de demander des permissions, si tu dois automatiser des
// process, fais un script »). Une longue commande au chemin absolu redemande son autorisation à chaque appel ; un script s'autorise une fois et se relance sans rien.
$shot = $root . '/var/tmp/probe-fsp.png';
Browser::get()->shot($address, $shot, 1400, 1100);
printf("%s — panneau de %s ouvert, tir d'écran dans %s\n", $address, $code, $shot);

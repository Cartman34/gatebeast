<?php
/**
 * USAGE
 *   php scripts/dev/shoot-page.php <page or served address> [width] [height] — screenshots a review page as it opens, without clicking anything.
 *   php scripts/dev/shoot-page.php -h|--help — this text.
 *
 * INTENTION
 *   The panel probes open one subject; nothing showed the page one actually lands on — the grid of subjects, its sections and its type scale. That is precisely what the operator judges first, and
 *   what a rebuilt stylesheet is most likely to break. Throwaway probe: it exists so the agent looks before showing.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$page = $argv[1] ?? $root . '/review-server/suivi-sprites/page.html';
$width = (int) ($argv[2] ?? 1400);
$height = (int) ($argv[3] ?? 1100);
// TOUT SE TIRE PAR LE SERVEUR, ADRESSE COMME FICHIER (point W21). Les pages de revue chargent leur style et leur script par un chemin absolu et lisent leur état
// par une requête : ouvertes en fichier, elles sortent nues et le tir montre un défaut que le tir a créé lui-même. Et ce qu'on ouvre est une COPIE MUSELÉE, parce
// qu'une page de revue écrit d'elle-même au chargement — regarder doit rester regarder.
$address = Probe::get()->copyOf($page, 'tir-page');

// The shot is named after what was shot, so two pages compared side by side do not overwrite each other.
$name = preg_replace('/[^a-z0-9]+/i', '-', trim(parse_url($page, PHP_URL_PATH) ?: basename($page), '/'));
$shot = $root . '/var/tmp/tir-' . strtolower(trim($name, '-')) . '.png';
@mkdir(dirname($shot), 0777, true);
Browser::get()->shot($address, $shot, $width, $height);
printf("%s — tir d'écran dans %s\n", $page, $shot);

<?php
/**
 * USAGE
 *   php scripts/dev/probe-theme-shot.php <route> <dark|light> — screenshots a served review page with the theme forced by `data-theme`, as the original page
 *   allowed. Example: php scripts/dev/probe-theme-shot.php /sprites dark
 *   php scripts/dev/probe-theme-shot.php -h|--help — this text
 *
 * INTENTION
 *   The restored palette declares three states — clear by default, dark when the system asks, and either one forced explicitly. A headless browser follows the
 *   system, so a plain screenshot only ever shows one of the three, and the other two would be claimed rather than seen. This forces the attribute the page
 *   itself honours, and shoots what the operator would get by choosing.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$server = ReviewServer::get();
$route = $argv[1] ?? '/sprites';
$theme = $argv[2] ?? 'dark';
if (!in_array($theme, ['dark', 'light'], true)) {
    throw new RuntimeException("FAULT le thème « {$theme} » n'existe pas — dark ou light.");
}
$served = $server->urlFor($route);
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}

// Appended at the end of the file, never before </body>: a built page carries no such tag, and a replacement on it would silently change nothing.
$forcing = "<script>document.documentElement.setAttribute('data-theme', " . json_encode($theme) . ");</script>";
$copy = $root . '/var/tmp/theme-shot-' . $theme . '.html';
file_put_contents($copy, $html . $forcing);

// Through the server, same origin: opened from the disk the page loses its style, its script and its state, and the shot would show a defect it created itself.
$shot = $root . '/var/tmp/tir-theme-' . $theme . '.png';
Browser::get()->shot($server->urlFor('/var/tmp/' . basename($copy)), $shot, 1400, 1100, 9000);
printf("%s en thème %s — tir d'écran dans %s\n", $route, $theme, $shot);

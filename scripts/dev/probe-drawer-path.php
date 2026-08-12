<?php
/**
 * USAGE
 *   php scripts/dev/probe-drawer-path.php — clicks the first text button of the built sprites page and reports the drawer's state: hidden or not, its title,
 *   its path line, and the first characters of the text it shows.
 *   php scripts/dev/probe-drawer-path.php -h|--help — this text
 *
 * INTENTION
 *   The path of a displayed text moved from the button label to the drawer (operator, 2026-08-11). Reading the handler does not say whether the drawer really
 *   opens with its three parts filled — the generic click probe only reports THAT a panel appeared, never WHAT it holds, and that is the whole question here.
 *   It also captures any script error, because a silent one would look exactly like a drawer that refuses to open.
 *
 *   IT GOES THROUGH THE SERVER, NEVER THROUGH THE FILE. The page links its style and its script by an absolute address — /review-server/…/page.js —, which under
 *   file:// points at the root of the disk and resolves to nothing: opened as a file, the page is bare and every button is dead, whatever the code does. Probing
 *   the file therefore measures the probe, not the page. The served copy is fetched, the probe appended, and the whole thing loaded with a base address so the
 *   links keep pointing at the server.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$served = ReviewServer::get()->urlFor('/sprites');
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}

// THE PROBE IS APPENDED AT THE END OF THE FILE, never before </body>: the built page carries no such tag, so a replacement on it would change nothing and the
// probe would report a clean run on a page it never touched.
$probe = "<script>window.addEventListener('error', function (e) {"
    . "var box = document.getElementById('sonde') || document.body.appendChild(document.createElement('div'));"
    . "box.id = 'sonde'; box.textContent = 'ERREUR DE SCRIPT : ' + e.message; });"
    . "window.addEventListener('load', function () {"
    . "var out = document.getElementById('sonde') || document.body.appendChild(document.createElement('div'));"
    . "out.id = 'sonde';"
    . "var b = document.querySelector('.open-text');"
    . "if (!b) { out.textContent = 'BOUTON INTROUVABLE'; return; }"
    . "var label = b.textContent.trim();"
    . "try { b.click(); } catch (e) { out.textContent = 'ERREUR AU CLIC : ' + e.message; return; }"
    . "var drawer = document.getElementById('drawer');"
    . "var path = document.getElementById('drawer-path');"
    . "out.textContent = 'LIBELLE DU BOUTON : [' + label + ']'"
    . " + ' — TIROIR : ' + (drawer.hidden ? 'FERME' : 'OUVERT')"
    . " + ' — TITRE : [' + document.getElementById('drawer-title').textContent + ']'"
    . " + ' — CHEMIN : [' + (path ? path.textContent : 'ELEMENT ABSENT') + ']'"
    . " + ' — TEXTE : [' + document.getElementById('drawer-body').textContent.slice(0, 60) + ']';"
    . "});</script>";

$copy = $root . '/var/tmp/drawer-path-probe.html';
file_put_contents($copy, '<base href="' . $served . '">' . $html . $probe);

$dom = Browser::get()->dom($copy);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$copy}");

<?php
/**
 * USAGE
 *   php scripts/dev/probe-debordement.php <built page> — reports whether the page scrolls sideways, by how much, and NAMES the widest elements responsible.
 *   php scripts/dev/probe-debordement.php -h|--help — this text
 *
 * INTENTION
 *   A page wider than its window is invisible until something is aligned to the right and gets cut — which is how it was found on the sprites page: a section
 *   count reading « 1 » instead of « 1 sujet ». Reading the stylesheet to guess which rule overflows is exactly the kind of three-wrong-diagnoses evening the
 *   other probes exist to end. The browser knows the answer; this asks it.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once $root . '/review-server/lib/Probe.php';
require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$page = $argv[1] ?? null;
if ($page === null || !is_file($page)) {
    throw new RuntimeException('FAULT usage : php scripts/dev/probe-debordement.php <fichier html>');
}

$probe = "<script>window.addEventListener('load', function () {"
    . "var lines = [];"
    . "var doc = document.documentElement;"
    . "lines.push('FENÊTRE ' + doc.clientWidth + 'px — CONTENU ' + doc.scrollWidth + 'px' "
    . "  + (doc.scrollWidth > doc.clientWidth ? ' — DÉBORDE de ' + (doc.scrollWidth - doc.clientWidth) + 'px' : ' — pas de débordement'));"
    . "var guilty = [];"
    . "Array.prototype.forEach.call(document.querySelectorAll('body *'), function (el) {"
    . "  if (el.offsetParent === null && el.tagName !== 'BODY') { return; }"
    . "  var box = el.getBoundingClientRect();"
    . "  if (box.right > doc.clientWidth + 1) {"
    . "    guilty.push({tag: el.tagName.toLowerCase(), cls: el.className || '(sans classe)', right: Math.round(box.right), width: Math.round(box.width)});"
    . "  }"
    . "});"
    . "guilty.slice(0, 12).forEach(function (g) {"
    . "  lines.push('  ' + g.tag + '.' + String(g.cls).split(' ')[0] + ' — bord droit ' + g.right + 'px, largeur ' + g.width + 'px');"
    . "});"
    . "if (!guilty.length) { lines.push('  aucun élément visible ne dépasse'); }"
    . "var out = document.createElement('pre'); out.id = 'sonde';"
    . "out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "});</script>";

// LA COPIE S'OUVRE PAR LE SERVEUR (point W21) : ouverte en `file://`, elle perd son style — et une page sans style ne déborde pas de la même façon, quand elle
// déborde encore. La sonde mesurait alors une mise en page qui n'existe nulle part.
$address = Probe::get()->serve(file_get_contents($page), $probe, 'probe-debordement');

$shot = $root . '/var/tmp/probe-debordement.png';
Browser::get()->shot($address, $shot, 1400, 900);
printf("Tir d'écran : %s\n", $shot);

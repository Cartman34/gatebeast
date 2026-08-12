<?php
/**
 * USAGE
 *   php scripts/dev/click-bouton.php <fichier html> <sélecteur> — copies the built page, makes it click that button on load, and reports what changed.
 *   php scripts/dev/click-bouton.php -h|--help — this text.
 *
 * INTENTION
 *   A dead button is not diagnosed by reading its handler — three wrong diagnoses in one evening proved it. Clicking it and looking at what the page becomes is
 *   the only account that settles the matter. The copy is written under var/tmp so the served page is never touched.
 *
 *   IT REPORTS WHATEVER OPENED, NOT ONE NAMED PANEL. It used to look only at the text drawer, whatever button it had been given: asked on 2026-08-08 whether a
 *   TILE opened its full-screen panel, it answered « panneau TOUJOURS MASQUÉ » about the drawer — true, irrelevant, and read as a failure. A probe that answers a
 *   question nobody asked is worse than no probe: it is a wrong answer with the authority of a measurement. It now lists every panel visible before and after,
 *   and says which ones appeared.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$page = $argv[1] ?? null;
$selector = $argv[2] ?? '.open-text';
if ($page === null || !is_file($page)) {
    throw new RuntimeException('FAULT usage : php scripts/dev/click-bouton.php <fichier html> <sélecteur>');
}

$probe = "<script>window.addEventListener('load', function () {"
    // WHAT COUNTS AS A PANEL: anything the page hides with the `hidden` attribute and shows by removing it — the full-screen subject panels, the side drawer, the
    // comment zones. Named by their id when they have one, by their class otherwise, so the report says WHICH one opened and not merely that something did.
    . "function nommer(el) { return el.id ? '#' + el.id : '.' + String(el.className || el.tagName).split(' ')[0]; }"
    . "function ouverts() {"
    . "  return Array.prototype.filter.call(document.querySelectorAll('.fsp, .drawer, .comment-zone'), function (el) { return !el.hidden; }).map(nommer);"
    . "}"
    . "var avant = ouverts();"
    . "var b = document.querySelector(" . json_encode($selector) . ");"
    . "var out = document.createElement('div'); out.id = 'sonde';"
    . "if (!b) { out.textContent = 'BOUTON INTROUVABLE'; document.body.appendChild(out); return; }"
    . "try { b.click(); } catch (e) { out.textContent = 'ERREUR AU CLIC : ' + e.message; document.body.appendChild(out); return; }"
    . "out.textContent = 'CLIC FAIT sur ' + nommer(b) + ' — ouverts avant : ' + (avant.join(', ') || 'aucun')"
    . " + ' — ouverts après : ' + (ouverts().join(', ') || 'aucun')"
    . " + ' — APPARUS : ' + (ouverts().filter(function (n) { return avant.indexOf(n) < 0; }).join(', ') || 'AUCUN');"
    . "document.body.appendChild(out);"
    . "});</script>";

// LA COPIE S'OUVRE PAR LE SERVEUR, ET L'ENVOI EST MUSELÉ AVANT LE PREMIER CLIC (point W21). Ouverte en `file://`, la page n'a ni style ni script : le bouton
// qu'on vient interroger n'a alors AUCUN gestionnaire, et la sonde rapporte « rien ne s'est ouvert » sur une page qu'elle a désarmée elle-même. Et un clic est un
// geste d'opérateur : muselée, la copie ne peut plus déposer de verdict dans review-server/notes/sprites.json, ce qui est déjà arrivé dix fois.
$address = Probe::get()->serve(file_get_contents($page), $probe, 'sonde-clic');

$dom = Browser::get()->dom($address);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
echo "La sonde n'a rien rapporté — la page n'a peut-être pas fini de se charger.\n";

<?php
/**
 * USAGE
 *   php scripts/dev/probe-state-refresh.php [CODE] — opens the served sprites page, reads the tile state of that subject, ticks every verdict in turn, and
 *   reads the tile again after each one. Without an argument it takes the first subject that has more than one variant.
 *   php scripts/dev/probe-state-refresh.php -h|--help — this text
 *
 * INTENTION
 *   « Quand j'ai jugé tous les variants d'un sujet, il apparait toujours À juger » (operator, 2026-08-11). The state used to be computed at build time only, so
 *   reading the code proves nothing: the question is whether the tile changes UNDER the verdicts, in the page, and whether the filter counts follow. Four
 *   situations are reported in one run — every variant validated, one sent back to rework, one dismissed, and everything cleared — because the operator asked
 *   for all of them and a single case would hide the three others.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$server = ReviewServer::get();
$wanted = $argv[1] ?? null;
$served = $server->urlFor('/sprites');
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}

// A PROBE NEVER WRITES INTO THE OPERATOR'S DATA, and this one did before this line existed: the page saves every verdict to the server the moment it is ticked,
// so ticking in order to measure wrote for real — ten empty entries left in review-server/notes/sprites.json on 2026-08-11, and the risk of overwriting a true
// verdict. Sending is therefore neutralised BEFORE any click: the page behaves as usual, the server hears nothing.
$probe = "<script>(function () { var send = XMLHttpRequest.prototype.send;"
    . "XMLHttpRequest.prototype.send = function () { if (this.__reading) { return send.apply(this, arguments); } };"
    . "var open = XMLHttpRequest.prototype.open;"
    . "XMLHttpRequest.prototype.open = function (method) { this.__reading = String(method).toUpperCase() === 'GET'; return open.apply(this, arguments); };"
    . "}());</script>"
    . "<script>window.addEventListener('load', function () {"
    . "var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
    . "var wanted = " . json_encode($wanted) . ";"
    . "var tile = null;"
    . "Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (one) {"
    . "  if (tile) { return; }"
    . "  var panel = document.getElementById('fsp-' + one.getAttribute('data-subject'));"
    . "  var boxes = panel ? panel.querySelectorAll('.act--approved input') : [];"
    . "  if (wanted ? one.getAttribute('data-subject') === wanted : boxes.length > 1) { tile = one; }"
    . "});"
    . "if (!tile) { out.textContent = 'AUCUN SUJET NE CONVIENT'; return; }"
    . "var code = tile.getAttribute('data-subject');"
    . "var panel = document.getElementById('fsp-' + code);"
    . "function read() { return tile.getAttribute('data-state') + ' / ' + tile.querySelector('.tile-state').textContent; }"
    . "function tick(kind, wantedValue) {"
    . "  Array.prototype.forEach.call(panel.querySelectorAll('.act--' + kind + ' input'), function (box) {"
    . "    if (box.checked !== wantedValue) { box.click(); }"
    . "  });"
    . "}"
    . "var report = ['SUJET ' + code + ' — ' + panel.querySelectorAll('.variant').length + ' variant(s)', 'AU DÉPART : ' + read()];"
    . "tick('approved', true); report.push('TOUS VALIDÉS : ' + read());"
    // One variant sent back to rework must outweigh every other verdict, whatever they say.
    . "var first = panel.querySelector('.act--rework input'); if (first) { first.click(); }"
    . "report.push('UN À REPRENDRE : ' + read());"
    . "if (first) { first.click(); }"
    . "var dismissed = panel.querySelector('.act--discarded input'); if (dismissed) { dismissed.click(); }"
    . "report.push('UN ÉCARTÉ : ' + read());"
    . "if (dismissed) { dismissed.click(); }"
    . "tick('approved', false); report.push('TOUT EFFACÉ : ' + read());"
    . "var counter = document.querySelector('.filter[data-filter=\"to-judge\"] span');"
    . "report.push('COMPTE DU FILTRE À JUGER : ' + (counter ? counter.textContent : 'absent'));"
    . "out.textContent = report.join(' || ');"
    . "});</script>";

$copy = $root . '/var/tmp/state-refresh-probe.html';
file_put_contents($copy, $html . $probe);

$dom = Browser::get()->dom($server->urlFor('/var/tmp/' . basename($copy)), 12000);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$copy}");

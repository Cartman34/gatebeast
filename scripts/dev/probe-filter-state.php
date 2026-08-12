<?php
/**
 * USAGE
 *   php scripts/dev/probe-filter-state.php [état] — clicks that filter on the served sprites page and reports the line under the row, the number of tiles left
 *   visible, and whether the two agree. Without an argument it clicks « à juger ».
 *   php scripts/dev/probe-filter-state.php -h|--help — this text
 *
 * INTENTION
 *   The line that says what a filter left visible was restored from the original builder (S39). A line that never updates looks exactly like a line that does,
 *   as long as the page opens unfiltered — so it is measured after a real click, through the server, and against the tiles actually shown rather than against
 *   itself.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$server = ReviewServer::get();
$state = $argv[1] ?? 'to-judge';
$served = $server->urlFor('/sprites');
$html = @file_get_contents($served);
if ($html === false) {
    throw new RuntimeException("FAULT la revue ne répond pas sur {$served} — lancez php review-server/serve.php.");
}

$probe = "<script>window.addEventListener('load', function () {"
    . "var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
    . "var button = document.querySelector('.filter[data-filter=' + JSON.stringify(" . json_encode($state) . ") + ']');"
    . "if (!button) { out.textContent = 'FILTRE INTROUVABLE'; return; }"
    . "var before = document.getElementById('filter-state').textContent;"
    . "button.click();"
    . "var shown = Array.prototype.filter.call(document.querySelectorAll('.tile'), function (tile) { return !tile.hidden; }).length;"
    . "var after = document.getElementById('filter-state').textContent;"
    . "out.textContent = 'AVANT LE CLIC : [' + before + '] — APRÈS : [' + after + ']'"
    . " + ' — VIGNETTES VISIBLES : ' + shown"
    . " + ' — ACCORD : ' + (after.indexOf(String(shown)) === 0 ? 'OUI' : 'NON');"
    . "});</script>";

$copy = $root . '/var/tmp/filter-state-probe.html';
file_put_contents($copy, $html . $probe);

$dom = Browser::get()->dom($server->urlFor('/var/tmp/' . basename($copy)), 9000);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$copy}");

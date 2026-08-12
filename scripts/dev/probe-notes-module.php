<?php
/**
 * USAGE
 *   php scripts/dev/probe-notes-module.php — appends a probe to the BUILT sprites page, loads it THROUGH THE SERVER, and reports what the notes module does when
 *   it is called directly: whether load answers, and whether a save lands in the repository. The review server must be running. Rebuild the page afterwards.
 *   php scripts/dev/probe-notes-module.php -h|--help — this text
 *
 * INTENTION
 *   THE SERVER SIDE IS ALREADY PROVEN — a POST on a throwaway route is written and read back — so what remains is the page's own call. Testing the module rather
 *   than the page separates « the module cannot save » from « the page never asks it to », and those two need opposite corrections. It reads the notes back through
 *   the server rather than trusting the answer of the very call under test.
 *
 *   IT WRITES ON THE REAL NOTES OF THE PAGE, on purpose: a throwaway route would prove the server again, not the page's own route. The file is versioned, so what
 *   this probe adds is removed with `git checkout review-server/notes/sprites.json`.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$page = $root . '/review-server/suivi-sprites/page.html';
$served = ReviewServer::get()->urlFor('/sprites');

if (@file_get_contents($served, false, stream_context_create(['http' => ['timeout' => 3]])) === false) {
    throw new RuntimeException('FAULT le serveur de revue ne répond pas — php review-server/serve.php');
}

$mark = 'SONDE-MODULE-' . date('His');
$probe = "<script>(function () {"
    . "var lines = [];"
    . "lines.push('MODULE : ' + typeof window.gatebeastNotes);"
    . "window.gatebeastNotes.load('verdicts', function (received) {"
    . "  lines.push('LOAD A RÉPONDU — type ' + (Array.isArray(received) ? 'tableau' : typeof received)"
    . "    + ', ' + Object.keys(received || {}).length + ' entrée(s)');"
    . "  var copy = received && !Array.isArray(received) ? received : {};"
    . "  copy['sonde/{$mark}.png'] = {approved: false, discarded: false, rework: true, comment: '{$mark}'};"
    . "  window.gatebeastNotes.save('verdicts', copy);"
    . "  lines.push('SAVE APPELÉ');"
    . "  window.setTimeout(function () {"
    // `data-built` IS THE ONLY MARK page.js LEAVES ON THE DOCUMENT, and its own render sets it — a render called from the load callback written at the very end
    // of the file. So a variant carrying it proves the script parsed and ran to that last line; none carrying it means the script threw earlier and everything
    // after the fault, the save call included, never ran. It is read here rather than on load because the mark appears when the store answers, not at parse time.
    // The former sentinel, `window.construireReleve`, went away with the survey bar and answered « NON » whatever happened — a fault the probe invented.
    . "    lines.push('page.js EST ALLÉ AU BOUT : ' + (document.querySelector('.variant[data-built]') ? 'OUI' : 'NON'));"
    . "    var call = new XMLHttpRequest();"
    . "    call.open('GET', '/notes?page=/sprites', false);"
    . "    call.send();"
    . "    lines.push('LE DÉPÔT PORTE LA MARQUE : ' + (call.responseText.indexOf('{$mark}') !== -1 ? 'OUI' : 'NON'));"
    . "    say();"
    . "  }, 1200);"
    . "  say();"
    . "});"
    . "function say() {"
    . "  var out = document.getElementById('sonde') || document.createElement('pre');"
    . "  out.id = 'sonde';"
    . "  out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "  out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "}"
    . "say();"
    . "})();</script>";

file_put_contents($page, file_get_contents($page) . $probe);

$shot = $root . '/var/tmp/probe-notes-module.png';
Browser::get()->shot($served, $shot, 1400, 700, 12000);

printf("Tir d'écran : %s\n", $shot);
printf("La marque « %s » est-elle dans le fichier ? %s\n", $mark,
    str_contains((string) file_get_contents($root . '/review-server/notes/sprites.json'), $mark) ? 'OUI' : 'NON');
echo "Nettoyage : git checkout review-server/notes/sprites.json — puis php review-server/build.php /sprites\n";

<?php
/**
 * USAGE
 *   php scripts/dev/probe-remarque-course.php — appends a probe to the BUILT sprites page, loads it THROUGH THE SERVER, writes a remark in a comment field
 *   BEFORE the server has answered, and reports whether the text survived and whether the repository holds it. The review server must be running. Rebuild the page
 *   afterwards to remove the probe.
 *   php scripts/dev/probe-remarque-course.php -h|--help — this text
 *
 * INTENTION
 *   THE DEFECT THIS EXISTS FOR IS INVISIBLE BY DESIGN: a remark typed while the page was still asking the server for its notes was not saved, and the answer then
 *   overwrote the field with what the repository held. The text left the screen with nothing said and nothing kept. The correction — keeping what was typed and
 *   pouring it back over the answer — can only be trusted if it is seen working on the real page, at the real moment, and that window is a few hundred
 *   milliseconds wide. So the probe writes at the earliest instant it can: right after the page's own script, while the request is still in flight.
 *
 *   IT LOADS THROUGH THE SERVER, like probe-verdicts.php and for the same reason: a file:// origin cannot call the server, so the very request under test would
 *   never happen.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$page = $root . '/review-server/suivi-sprites/page.html';
$notes = $root . '/review-server/notes/sprites.json';
$served = ReviewServer::get()->urlFor('/sprites');

if (@file_get_contents($served, false, stream_context_create(['http' => ['timeout' => 3]])) === false) {
    throw new RuntimeException('FAULT le serveur de revue ne répond pas — php review-server/serve.php');
}

// The probe runs as soon as it is parsed, so before the notes request comes back — that is the whole point. It types, then waits, then reports.
$mark = 'SONDE-COURSE-' . date('His');
$probe = "<script>(function () {"
    . "var lines = [];"
    . "window.onerror = function (message, source, line) { lines.push('ERREUR JS : ' + message + ' (' + source + ':' + line + ')'); say(); };"
    // A COUNTER ON THE SAVE CALL, wrapped before anything is typed. Without it the probe can only see the outcome — nothing in the repository — which reads the
    // same whether the page never asked to save or asked and failed. Those two need opposite corrections.
    . "var saves = 0;"
    . "var realSave = window.gatebeastNotes.save;"
    . "window.gatebeastNotes.save = function (section, notes) { saves++; return realSave.apply(null, arguments); };"
    . "var field = document.querySelector('.comment');"
    . "if (!field) { lines.push('AUCUN CHAMP DE COMMENTAIRE DANS LA PAGE'); say(); return; }"
    . "var id = field.getAttribute('data-id');"
    . "lines.push('CHAMP TROUVÉ — ' + id);"
    . "field.value = '{$mark}';"
    . "field.dispatchEvent(new Event('input', {bubbles: true}));"
    . "lines.push('ÉCRIT AVANT LA RÉPONSE DU SERVEUR : {$mark}');"
    . "window.setTimeout(function () {"
    // `data-built` IS THE ONLY MARK page.js LEAVES ON THE DOCUMENT, and its own render sets it — a render called from the load callback written at the very end
    // of the file. A variant carrying it proves the script parsed and ran to that last line; none carrying it means it threw earlier, and the whole race this
    // probe measures never took place. It is read after the wait because the mark appears when the store answers, not at parse time. The former sentinel,
    // `window.construireReleve`, went away with the survey bar and answered « NON » whatever happened — a fault the probe invented.
    . "  lines.push('page.js EST ALLÉ AU BOUT : ' + (document.querySelector('.variant[data-built]') ? 'OUI' : 'NON'));"
    . "  lines.push('LE CHAMP PORTE ENCORE : ' + (field.value || '(vide)'));"
    . "  lines.push('LA PAGE A DEMANDÉ L ENREGISTREMENT : ' + saves + ' fois');"
    . "  var call = new XMLHttpRequest();"
    . "  call.open('GET', '/notes?page=/sprites', false);"
    . "  call.send();"
    . "  lines.push('LE DÉPÔT PORTE LA REMARQUE : ' + (call.responseText.indexOf('{$mark}') !== -1 ? 'OUI' : 'NON'));"
    . "  say();"
    . "}, 2000);"
    . "function say() {"
    . "  var out = document.getElementById('sonde') || document.createElement('pre');"
    . "  out.id = 'sonde';"
    . "  out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "  out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "}"
    . "say();"
    . "})();</script>";

file_put_contents($page, file_get_contents($page) . $probe);

// THE OPERATOR'S NOTES ARE PUT BACK, like `probe-verdicts.php` does and for the same reason: this probe TYPES a remark to prove the typing survives the answer,
// so it cannot be muzzled — being written is what it measures. What it can do is remember the file and restore it, or it leaves a remark nobody wrote.
$before = is_file($notes) ? file_get_contents($notes) : null;

$shot = $root . '/var/tmp/probe-remarque-course.png';
Browser::get()->shot($served, $shot, 1400, 700, 12000);

$after = is_file($notes) ? file_get_contents($notes) : null;
printf("Tir d'écran : %s\n", $shot);
printf("La remarque « %s » est-elle dans le dépôt ? %s\n", $mark, str_contains((string) $after, $mark) ? 'OUI' : 'NON');

if ($after !== $before) {
    if ($before === null) {
        unlink($notes);
    } else {
        file_put_contents($notes, $before);
    }
    echo "LA REMARQUE ÉCRITE PAR CETTE SONDE A ÉTÉ RETIRÉE : les données de l'opérateur sont revenues à leur état d'avant.\n";
}
echo "Reconstruis la page pour retirer la sonde : php review-server/build.php /sprites\n";

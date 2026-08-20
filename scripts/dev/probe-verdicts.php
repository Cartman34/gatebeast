<?php
/**
 * USAGE
 *   php scripts/dev/probe-verdicts.php — appends a probe to the BUILT sprites page, loads it THROUGH THE SERVER, ticks the first verdict box, and reports what
 *   the server holds afterwards. Rebuilds the page at the end, which removes the probe. The review server must be running.
 *   php scripts/dev/probe-verdicts.php -h|--help — this text
 *
 * INTENTION
 *   The verdicts left the browser for the repository, and the only thing that proves it is a real click reaching the file. The other probes cannot do it: they
 *   open a page as a FILE, and a file:// origin cannot call the address the review is served on — the very request under test is the one the browser refuses. Loading the page
 *   from the server puts the probe in the same origin as the call it wants to observe. Appending to the built page is safe because that file is produced by a
 *   command: rebuilding it is how the probe is removed, not a repair.
 *
 *   READ THE SCREEN, NOT THE FILE, FOR THE VERDICT OF THIS PROBE. The page reloads itself when its source changes, and the probe rides along on the built page:
 *   a rebuild during the browser's time budget makes the page reload and the probe CLICK A SECOND TIME, which un-ticks the box and saves `false`. The line the
 *   probe prints is taken right after its own click and is therefore the true one; the file may have been toggled again afterwards.
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

$probe = "<script>window.addEventListener('load', function () {"
    . "var lines = [];"
    . "lines.push('MODULE gatebeastNotes : ' + typeof window.gatebeastNotes"
    . "  + ' — load ' + (window.gatebeastNotes ? typeof window.gatebeastNotes.load : 'n/a'));"
    . "window.onerror = function (message, source, line) { lines.push('ERREUR JS : ' + message + ' (' + source + ':' + line + ')'); dire(); };"
    . "var box = document.querySelector('.acts input');"
    . "if (!box) { lines.push('AUCUNE CASE DE VERDICT DANS LA PAGE'); }"
    . "else {"
    . "  lines.push('CASE TROUVÉE — sujet ' + box.getAttribute('data-id') + ', acte ' + box.getAttribute('data-act'));"
    . "  window.setTimeout(function () {"
    . "    box.click();"
    . "    window.setTimeout(function () {"
    . "      var call = new XMLHttpRequest();"
    . "      call.open('GET', '/notes?page=/sprites', false);"
    . "      call.send();"
    . "      lines.push('CE QUE LE SERVEUR GARDE APRÈS LE CLIC : ' + call.responseText.slice(0, 300));"
    . "      dire();"
    . "    }, 600);"
    . "  }, 600);"
    . "}"
    . "function dire() {"
    . "  var out = document.getElementById('sonde') || document.createElement('pre');"
    . "  out.id = 'sonde';"
    . "  out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "  out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "}"
    . "dire();"
    . "});</script>";

file_put_contents($page, file_get_contents($page) . $probe);

// THE OPERATOR'S VERDICTS ARE PUT BACK, AND THIS PROBE IS THE ONLY ONE THAT HAS TO. Every other probe muzzles its copy before clicking; this one exists to prove
// the click REACHES the file, so it cannot. What it can do is remember the file and restore it — otherwise it leaves a verdict nobody gave. It left « validé »
// on the grass tile on 2026-08-19, exactly the accident of 2026-08-11 that the repository rule was written for: ten empty entries, removed one by one.
$before = is_file($notes) ? file_get_contents($notes) : null;

$shot = $root . '/var/tmp/probe-verdicts.png';
Browser::get()->shot($served, $shot, 1400, 700, 12000);

$after = is_file($notes) ? file_get_contents($notes) : null;
printf("Tir d'écran : %s\n", $shot);
printf("Le fichier du dépôt contenait, juste après le clic :\n%s\n", $after ?? '(rien)');

if ($after !== $before) {
    if ($before === null) {
        unlink($notes);
    } else {
        file_put_contents($notes, $before);
    }
    echo "LE VERDICT ÉCRIT PAR CETTE SONDE A ÉTÉ RETIRÉ : les données de l'opérateur sont revenues à leur état d'avant.\n";
} else {
    echo "AUCUNE ÉCRITURE N'A ATTEINT LE FICHIER — c'est le défaut que cette sonde cherche, et il est là.\n";
}
echo "Reconstruis la page pour retirer la sonde : php review-server/build.php /sprites\n";

<?php
/**
 * USAGE
 *   php scripts/dev/probe-comparaison.php [subject code] — opens that subject's panel in a copy of the built sprites page, ticks its first two "compare" boxes,
 *   then clicks the quit button, and reports what the page looked like at each of the three steps. Writes var/tmp/probe-comparaison.html and .png.
 *   php scripts/dev/probe-comparaison.php -h|--help — this text
 *
 * INTENTION
 *   The exit button only exists while a comparison is running, so neither probe-fsp.php (which only un-hides a panel) nor click-bouton.php (which clicks one
 *   selector once) can reach it: the state has to be built up before the button is there to click. Reading the handler is not an account — a dead button was
 *   misdiagnosed three times in one evening by reading code, and a simulated click settled it in one go. This drives the real scenario in the real page.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once $root . '/review-server/lib/Probe.php';
require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'OB-010';
// THE LAST STEP HIDES WHAT WE CAME TO LOOK AT: quitting the comparison removes the button, so a screenshot of the finished scenario never shows it. "hold" stops
// one step earlier and leaves the comparison on screen — the numbers say the button is 196px wide, only the picture says whether it looks like a button.
$hold = ($argv[2] ?? '') === 'hold' ? 'true' : 'false';
// LA PAGE SE PREND AU SERVEUR, PAS AU DISQUE (2026-08-12, point W21) : son style et son script vivent dans leurs propres fichiers, atteints par un chemin absolu.
// Ouverte en `file://`, la copie sort nue — et une sonde qui mesure une page sans style mesure la sonde, pas la page. Le service porte les deux moitiés du geste.
$page = Probe::get()->page('/sprites');
$opened = str_replace("<div class=\"fsp\" id=\"fsp-{$code}\" hidden>", "<div class=\"fsp\" id=\"fsp-{$code}\">", $page);
if ($opened === $page) {
    throw new RuntimeException("FAULT le sujet « {$code} » n'a pas de panneau dans la page construite.");
}

// THE REPORT IS BUILT IN THE PAGE ITSELF, then screenshotted with it: a verdict computed here, outside the browser, would only repeat what this script assumed.
// What matters is what the browser actually laid out — whether the button is displayed, and whether the comparison really ended.
$probe = "<script>window.addEventListener('load', function () {"
    . "var panel = document.getElementById(" . json_encode("fsp-{$code}") . ");"
    . "var list = panel.querySelector('.variants');"
    . "var quit = list.querySelector('.quit-comparison');"
    . "var lines = [];"
    . "function shown(el) { return el ? window.getComputedStyle(el).display !== 'none' : false; }"
    . "function visibleVariants() { return Array.prototype.filter.call(list.querySelectorAll('.variant'), shown).length; }"
    . "lines.push('AU DEPART — bouton ' + (shown(quit) ? 'VISIBLE (FAUTE)' : 'masque') + ', ' + visibleVariants() + ' variants montres');"
    . "var boxes = list.querySelectorAll('.compare');"
    . "if (boxes.length < 2) { lines.push('SUJET INUTILISABLE — ' + boxes.length + ' case(s) a cocher, il en faut deux'); }"
    . "else {"
    . "  boxes[0].click(); boxes[1].click();"
    . "  lines.push('DEUX COCHEES — bouton ' + (shown(quit) ? 'visible' : 'MASQUE (FAUTE)') + ', ' + visibleVariants() + ' variants montres'"
    . "    + ', largeur bouton ' + Math.round(quit.getBoundingClientRect().width) + 'px sur ' + Math.round(list.getBoundingClientRect().width) + 'px de liste');"
    . "  lines.push('  DETAIL — cases cochees ' + list.querySelectorAll('.compare:checked').length"
    . "    + ', variants .picked ' + list.querySelectorAll('.variant.picked').length"
    . "    + ', classe de la liste \\'' + list.className + '\\''"
    . "    + ', total cases ' + boxes.length + ', total variants ' + list.querySelectorAll('.variant').length);"
    . "  if (" . $hold . ") { lines.push('ARRET DEMANDE — la comparaison reste a l ecran'); }"
    . "  else {"
    . "  quit.click();"
    . "  lines.push('APRES LE CLIC — bouton ' + (shown(quit) ? 'TOUJOURS VISIBLE (FAUTE)' : 'masque') + ', ' + visibleVariants() + ' variants montres'"
    . "    + ', ' + list.querySelectorAll('.compare:checked').length + ' case(s) encore cochee(s)'"
    . "    + ', classe comparison ' + (list.classList.contains('comparison') ? 'ENCORE LA (FAUTE)' : 'retiree'));"
    . "  }"
    . "}"
    . "var out = document.createElement('pre'); out.id = 'sonde';"
    . "out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "});</script>";

// LE SCRIPT EST AJOUTÉ EN FIN DE FICHIER, JAMAIS AVANT </body> : la page construite ne porte pas cette balise, donc un str_replace dessus ne change rien et la
// sonde rend un essai « propre » sur une page qu'elle n'a jamais touchée. C'est arrivé ici même au premier essai. Le service tient cette règle pour toutes.
$address = Probe::get()->serve($opened, $probe, 'probe-comparaison');

$shot = $root . '/var/tmp/probe-comparaison.png';
Browser::get()->shot($address, $shot, 1400, 1100);
printf("Sonde servie : %s\nTir d'écran : %s\n", $address, $shot);

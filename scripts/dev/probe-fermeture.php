<?php
/**
 * USAGE
 *   php scripts/dev/probe-fermeture.php [subject code] — opens that subject's panel the way a reload does, WITHOUT the in-memory stack knowing about it, then
 *   clicks the close button and reports whether the panel actually went away. Writes var/tmp/probe-fermeture.html and .png.
 *   php scripts/dev/probe-fermeture.php -h|--help — this text
 *
 * INTENTION
 *   The stack lives in memory and is refilled from session storage at load; the failure the operator hit is the case where a panel is on screen and the stack is
 *   empty, which makes the close button do nothing and leaves the page stuck behind a panel that cannot be dismissed. Un-hiding the panel in a copy of the page
 *   reproduces exactly that state — visible panel, empty stack — which no ordinary click on the served page can. check-review-pages.php pins the code that fixes
 *   it; this says whether the code works.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once $root . '/review-server/lib/Probe.php';
require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'OB-010';
// LA PAGE SE PREND AU SERVEUR ET LA COPIE S'OUVRE PAR LUI (point W21) : lue sur le disque puis ouverte en `file://`, elle sortait NUE — ni style, ni script, donc
// un bouton de fermeture qui ne pouvait pas fonctionner et une sonde qui l'accusait. Le service porte ce geste pour toutes les sondes.
$page = Probe::get()->page('/sprites');
$opened = str_replace("<div class=\"fsp\" id=\"fsp-{$code}\" hidden>", "<div class=\"fsp\" id=\"fsp-{$code}\">", $page);
if ($opened === $page) {
    throw new RuntimeException("FAULT le sujet « {$code} » n'a pas de panneau dans la page construite.");
}

// APPENDED, NEVER INJECTED BEFORE </body>: the built page carries no </body> tag, so a str_replace on it changes nothing and the probe would report a clean run
// over a page it never touched.
$probe = "<script>window.addEventListener('load', function () {"
    . "var panel = document.getElementById(" . json_encode("fsp-{$code}") . ");"
    . "var lines = [];"
    . "lines.push('AU DEPART — panneau ' + (panel.hidden ? 'MASQUE (la sonde a rate son coup)' : 'visible')"
    . "  + ', pile restituee ' + (sessionStorage.getItem('gatebeast-sprites-panneaux') || 'vide'));"
    . "panel.querySelector('.fsp-close').click();"
    . "lines.push('APRES LE CLIC — panneau ' + (panel.hidden ? 'ferme' : 'TOUJOURS OUVERT (FAUTE)')"
    . "  + ', defilement du corps ' + (document.body.style.overflow === 'hidden' ? 'ENCORE BLOQUE (FAUTE)' : 'rendu'));"
    . "var out = document.createElement('pre'); out.id = 'sonde';"
    . "out.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;margin:0;padding:10px;background:#111;color:#0f0;font:12px monospace;white-space:pre-wrap';"
    . "out.textContent = lines.join('\\n'); document.body.appendChild(out);"
    . "});</script>";

$address = Probe::get()->serve($opened, $probe, 'probe-fermeture');

$shot = $root . '/var/tmp/probe-fermeture.png';
Browser::get()->shot($address, $shot, 1400, 900);
printf("Sonde servie : %s\nTir d'écran : %s\n", $address, $shot);

<?php
/**
 * USAGE
 *   php scripts/dev/probe-variant-card.php [code] — opens the sprites page, opens that subject's full-screen card, and shoots what it shows.
 *   php scripts/dev/probe-variant-card.php -h|--help — this text
 *
 * INTENTION
 *   A variant card is never visible on the page as it loads: it lives inside a panel a click opens. Looking at the footprint colours, at the head that carries
 *   the variant's state or at the verdict form therefore means DRIVING the page, not screenshotting it — and the operator's own screenshots are of that card,
 *   so it is the only place a change to it can be checked.
 *
 *   IT GOES THROUGH THE SERVER, NEVER THROUGH THE FILE (point W21). The page calls its stylesheet and its script by an absolute address and reads its verdicts by
 *   a request: opened from the disk it has neither style, nor script, nor state, and the probe would report a defect it created itself. The driven copy is
 *   written under var/tmp and loaded from the server's own origin.
 *
 *   AND IT NEVER WRITES: it clicks a tile, which opens a panel and nothing else. No verdict is ticked, so nothing reaches review-server/notes/.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

// UNE OPTION N'EST PAS UNE DIMENSION, ET C'EST ENCORE UNE SONDE QUI MENTAIT : `--drawer` donné en deuxième place était lu comme une LARGEUR, donc zéro, et la
// capture retombait sur une fenêtre étroite — elle photographiait la mise en page repliée d'un petit écran, que l'opérateur ne voit jamais, et rien ne le disait.
// Les options se retirent avant de lire les places, et une dimension nulle est refusée plutôt que subie.
$positional = array_values(array_filter(array_slice($argv, 1), fn (string $one): bool => !str_starts_with($one, '-')));
$code = $positional[0] ?? 'SP-001';
$width = (int) ($positional[1] ?? 1600);
$height = (int) ($positional[2] ?? 1200);
if ($width < 1 || $height < 1) {
    throw new RuntimeException("FAULT dimensions illisibles ({$width} × {$height}) — usage : php scripts/dev/probe-variant-card.php <CODE> [largeur] [hauteur] [--drawer]");
}

// THE PROBE IS APPENDED AT THE VERY END OF THE FILE, never before </body>: the built page carries no such tag, so a str_replace on it would change nothing and
// the probe would report a clean run on a page it never touched.
// A SECOND CLICK IS OPTIONAL, AND IT IS THE DRAWER'S: `--drawer` opens the first version of the card, which is the only way to look at the magnified image, at
// its footprint grid and at the title the drawer announces.
$drawer = in_array('--drawer', $argv, true);
$probe = "<script>window.addEventListener('load', function () {"
    . "var tile = document.querySelector('.tile[data-subject=' + JSON.stringify(" . json_encode($code) . ") + ']');"
    . "if (!tile) { document.title = 'AUCUNE VIGNETTE'; return; }"
    . "tile.click();"
    . ($drawer ? "var open = document.querySelector('.fsp:not([hidden]) .open-version'); if (open) { open.click(); }" : '')
    . "});</script>";

// LE SERVICE PORTE LES DEUX GESTES : la copie s'ouvre par le serveur, et l'envoi est muselé avant le premier clic. Cette sonde CLIQUE — une vignette, puis le
// bouton d'une version : sans muselière, un clic malheureux déposerait un verdict dans review-server/notes/sprites.json, ce qui est déjà arrivé dix fois.
$url = Probe::get()->serve(Probe::get()->page('/sprites'), $probe, 'sonde-variant');
$shot = $root . '/var/tmp/tir-variant-' . $code . '.png';
Browser::get()->shot($url, $shot, $width, $height);
printf("%s — %s\n", $code, $shot);

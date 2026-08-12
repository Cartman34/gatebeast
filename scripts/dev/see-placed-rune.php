<?php
/**
 * USAGE
 *   php scripts/dev/see-placed-rune.php [individu] — writes a served page showing the creature's sprite with its rune traced on its anchor, and photographs it.
 *   php scripts/dev/see-placed-rune.php -h|--help — this text.
 *   Default: SP-001-1, the reference cub. The picture lands in var/tmp/ and is meant to be LOOKED AT.
 *
 * INTENTION
 *   Four declared values meet here for the first time — the shape's path, the individual's colour, the size in tiles, and the anchor posed by eye on the image —
 *   and nothing but the eye can say whether they agree. A unit test would confirm the numbers are the numbers; it would not see a rune sitting on an ear.
 *
 *   IT DRAWS AT THREE SIZES, and that is the point: the rule says the mark is CONSTANT and never scales with its bearer. Shown at one size that claim cannot be
 *   checked at all — three renderings of the same sprite show immediately whether the rune keeps its place and its proportion, or drifts.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Rune.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$code = $argv[1] ?? 'SP-001-1';
$rune = Rune::get();
$species = $rune->individual($code)['species'];

$data = json_decode(file_get_contents($root . '/assets/subjects.json'), true, 512, JSON_THROW_ON_ERROR);
$representation = null;
foreach ($data['subjects'][$species]['variants'] ?? [] as $variant) {
    foreach ($variant['representations'] ?? [] as $candidate) {
        if (($candidate['status'] ?? 'current') === 'current') {
            $representation = $candidate;
            break 2;
        }
    }
}
if ($representation === null) {
    throw new RuntimeException("FAULT {$species} n'a aucune représentation marquée `current` — rien à regarder.");
}
if (!isset($representation['rune_anchor_px'])) {
    throw new RuntimeException("FAULT {$representation['path']} n'a pas d'ancre de rune — posez-la par php... set-rune-anchor.py avant de regarder.");
}

$anchor = $representation['rune_anchor_px'];
$delivered = $representation['measures']['delivered_px'];
$blocks = '';
foreach ([1, 2, 4] as $zoom) {
    // L'ANCRE EST DANS LES PIXELS DE L'IMAGE LIVRÉE : au grossissement, elle se multiplie comme l'image, sans quoi la marque resterait collée en haut à gauche.
    $placed = ['x' => $anchor['x'] * $zoom, 'y' => $anchor['y'] * $zoom, 'tilt_deg' => $anchor['tilt_deg'] ?? 0];
    $blocks .= sprintf(
        '<figure style="position:relative;margin:0 24px 0 0;width:%dpx"><img src="/assets/%s" width="%d" height="%d" style="display:block;image-rendering:pixelated">%s'
        . '<figcaption style="color:#8a8f98;font:12px system-ui;margin-top:8px">%d fois</figcaption></figure>',
        $delivered['width'] * $zoom, $representation['path'], $delivered['width'] * $zoom, $delivered['height'] * $zoom,
        $rune->svg($code, $placed, 96 * $zoom), $zoom
    );
}

$page = '<!doctype html><meta charset="utf-8"><title>Rune posée</title>'
    . '<body style="margin:24px;background:#16171b;color:#e6e8ec;font:14px system-ui">'
    . sprintf('<p>%s sur %s — ancre (%s, %s), taille %s case</p>', $code, $representation['path'], $anchor['x'], $anchor['y'], $rune->sizeTx())
    . sprintf('<div style="display:flex;align-items:flex-start">%s</div>', $blocks);

$copy = $root . '/var/tmp/rune-posee.html';
file_put_contents($copy, $page);
$shot = $root . '/var/tmp/rune-posee.png';
Browser::get()->shot(ReviewServer::get()->urlFor('/var/tmp/' . basename($copy)), $shot, 1200, 700);
printf("%s — %s posée sur %s\n", $shot, $code, $representation['path']);

<?php
/**
 * USAGE
 *   php scripts/check-height-bands.php            the verdict: how many declared height bands no longer contain the canvas the model builds for their subject
 *   php scripts/check-height-bands.php <file>     the same, on the referential given instead of assets/subjects.json
 *   php scripts/check-height-bands.php -v         each band at fault, with its subject, its variant, the canvas and what is declared
 *   php scripts/check-height-bands.php -h|--help  this text
 *
 * INTENTION
 *   A HEIGHT BAND IS DECLARED BY HAND AND NOTHING EVER LOOKS AT IT AGAIN. It lives on the variant, « height_min_ty » and « height_max_ty », and tile_scale
 *   refuses to compute it on purpose — « aucun script ne peut savoir qu'une herbe est courte et qu'un arbre grand » (opérateur, 2026-08-10). That judgement is
 *   right and this does not touch it. What it holds is the other half: the band is declared ONCE, while the subject's cover, footprint and height go on changing
 *   underneath it, and nothing puts the two back face to face.
 *
 *   WHAT THAT COSTS, AND IT IS MEASURED. The operator asked THREE TIMES for the apple tree to come back shorter. A tile of cover was removed on the first ask —
 *   that is what he had named — but the band kept the figure computed for the old cover. So the image kept coming back at the same height AND kept being declared
 *   conforming: the height check compares the IMAGE to the band, never the band to the SUBJECT. Two wrong things that agree look exactly like a correct chain.
 *
 *   WHAT IT CATCHES, AND WHAT IT LETS THROUGH — measured, not assumed, so nobody trusts it further than it goes. A band's tolerance covers the STANDING part
 *   alone (tile_scale.STANDING_TOLERANCE_LOW/HIGH, a quarter either way); its GROUND part is geometry and carries none. So a row gained or lost by the extent
 *   moves the canvas by a whole TY against a slack of a quarter of the standing height, and falls outside as soon as that standing height is under four TY. The
 *   apple tree is the case that produced this tool and it is caught with room to spare: TR-063 lost a row of cover on 2026-08-12, its canvas fell from 4,71 to
 *   3,71 TY, and the band left behind ran from 4,29 to 5,14. A very tall subject is the blind spot: the oak stands 4,57 TY, so a quarter of it is more than a
 *   whole row, and one row of cover can move under its band without leaving it. Nothing here pretends otherwise.
 *
 *   IT NEVER PROPOSES A VALUE, and that is the whole of its restraint. It says the band no longer contains the canvas; WHICH of the two is wrong — the band, the
 *   cover, the height — is a judgement, and the judgement stays with the operator. A checker that suggested a band would be recomputing the very thing
 *   tile_scale refuses to compute.
 *
 *   THE MODEL IS ASKED, NEVER REWRITTEN — and this is the one design decision worth reading before changing anything here. The pixel ladder, the foreshortening,
 *   the canvas and the TY unit all live in scripts/tile_scale.py, which is authoritative and must stay the only place they exist; copying four pivot values into
 *   PHP is the fault this repository pays most often. So the arithmetic is not done here at all: BRIDGE below hands the model a list of extents and reads back
 *   one figure per extent, and every multiplication stays on the model's side of the fence. What PHP does is what PHP is for here — read the data, apply the
 *   rule, render the verdict.
 *
 *   In PHP because it is the project's default language for durable tooling. The bridge is the only Python, it is a CALL and not a program, and it must stay
 *   that way: the day it grows a branch of its own, the model has quietly gained a second home.
 */

require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

const REFERENTIAL = 'assets/subjects.json';

/** The two figures a variant declares — its own judgement of how tall the drawing must come back, in TY. Read as they are written, never derived. */
const BAND_MIN = 'height_min_ty';
const BAND_MAX = 'height_max_ty';

/**
 * The call handed to the model. It computes nothing of its own: for each extent it asks tile_scale for the canvas it builds, and for what one TY is worth in
 * that same canvas — both public operations of the module — and returns their quotient, which is the canvas expressed in the unit the bands are declared in.
 *
 * IT MUST STAY A CALL. Reading it as a place to « just add » a condition, a default or a rounding is how a model gets a second home; anything of that kind
 * belongs in tile_scale.py, where the operations already live.
 */
const BRIDGE = <<<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
import tile_scale
extents = json.load(sys.stdin)
json.dump([
    tile_scale.master_definition(columns, rows, height=height)["height"] / tile_scale.ty_in_pixels(columns, rows)
    for columns, rows, height in extents
], sys.stdout)
PY;

$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
$given = array_values(array_filter(array_slice($argv, 1), fn (string $argument): bool => !str_starts_with($argument, '-')));
$root = dirname(__DIR__);
$path = $given ? $given[0] : $root . '/' . REFERENTIAL;

/**
 * The canvas of each extent, in TY, straight from the model.
 *
 * ONE CALL FOR THE WHOLE REFERENTIAL, not one per variant: a hundred interpreter starts turn a check into a chore nobody runs, which is the surest way to lose
 * one. A failure of the bridge is raised with what it wrote — a checker that could not reach the model has not found « nothing wrong ».
 */
function canvasesInTy(string $root, array $extents): array
{
    $process = proc_open(
        ['python3', '-c', BRIDGE, $root . '/scripts'],
        [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
        $pipes
    );
    if (!is_resource($process)) {
        throw new RuntimeException('python3 ne démarre pas — le modèle de scripts/tile_scale.py ne peut pas être interrogé.');
    }
    fwrite($pipes[0], json_encode(array_values($extents)));
    fclose($pipes[0]);
    $answer = stream_get_contents($pipes[1]);
    $complaint = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $status = proc_close($process);
    if ($status !== 0) {
        throw new RuntimeException("le modèle s'est arrêté (code {$status}) : " . trim($complaint));
    }

    return array_combine(array_keys($extents), json_decode($answer, true, 512, JSON_THROW_ON_ERROR));
}

/** A figure as the operator reads it: in TY, to one decimal, with the comma French uses. */
function inTy(float $value): string
{
    return str_replace('.', ',', (string) round($value, 1)) . ' TY';
}

$data = json_decode((string) file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);

// THE EXTENT IS TAKEN EXACTLY AS THE PRODUCTION COMMAND TAKES IT — the cover when the subject declares one, the footprint otherwise (scripts/generate-sprite.py,
// « spread = subject.get("cover") or subject["footprint"] »). An oak stands on two tiles and spreads its crown over six: judging it on its footprint compares a
// six-tile drawing to a two-tile band, which is how TR-060 and TR-063 were called wrong on 2026-08-10.
$asked = [];
$judged = [];
$bandless = [];
foreach ($data['subjects'] as $code => $subject) {
    $spread = $subject['cover'] ?? $subject['footprint'] ?? null;
    if ($spread === null) {
        continue;
    }
    $extent = [$spread['columns'], $spread['rows'], $subject['height'] ?? null];
    $key = implode('/', array_map(fn ($figure): string => var_export($figure, true), $extent));
    $asked[$key] = $extent;
    foreach ($subject['variants'] ?? [] as $variant) {
        if (!isset($variant[BAND_MIN], $variant[BAND_MAX])) {
            $bandless[] = sprintf('%s / %s', $code, $variant['ref'] ?? '?');
            continue;
        }
        $judged[] = [$code, $variant['ref'] ?? '?', $key, (float) $variant[BAND_MIN], (float) $variant[BAND_MAX]];
    }
}

$canvases = canvasesInTy($root, $asked);

$faults = [];
foreach ($judged as [$code, $reference, $key, $minimum, $maximum]) {
    $canvas = $canvases[$key];
    if ($canvas >= $minimum && $canvas <= $maximum) {
        continue;
    }
    $faults[] = sprintf(
        '%s / %s — la toile du modèle fait %s, la fourchette déclarée va de %s à %s',
        $code,
        $reference,
        inTy($canvas),
        inTy($minimum),
        inTy($maximum)
    );
}

printf(
    "%d variante(s) jugée(s) : %d fourchette(s) ne contiennent plus la toile du modèle. %d variante(s) sans fourchette, hors de portée de ce contrôle.\n",
    count($judged),
    count($faults),
    count($bandless)
);
if ($detail) {
    foreach ($faults as $line) {
        printf("  %s\n", $line);
    }
    foreach ($bandless as $line) {
        printf("  SANS FOURCHETTE  %s\n", $line);
    }
} elseif ($faults) {
    echo "« -v » les nomme.\n";
}

exit($faults ? 1 : 0);

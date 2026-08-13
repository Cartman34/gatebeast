<?php
/**
 * USAGE
 *   php scripts/build-projection-plate.php [<sortie.png>]
 *
 *   Draws the project's projection reference plate — one bare built volume under the world's camera — and writes TWO images from the one calculation, each as an
 *   SVG converted to PNG with rsvg-convert:
 *     <sortie>.png          the bare plate, the one the generator is given: no text, no dimension, no grid, no frame
 *     <sortie>-annotee.png  the same drawing plus its reading layer, the one the operator checks it on: tile grid, dimensions in TILES, name of every face
 *
 *   Without an argument both land in local/planches/, which is where an agent's own output belongs and which the review server already serves. Give a path and
 *   the annotated one takes the same name with « -annotee » appended. Prints the figures it drew from, so the drawing can be checked against the scale it claims.
 *
 *   php scripts/build-projection-plate.php -h|--help — this text
 *
 * INTENTION
 *   WHAT THE GENERATOR SEES OUTWEIGHS WHAT IT READS, and this plate exists for no other reason. The prompt prescribes the parallel projection four times, in the
 *   most operational terms it has — every rectangular face is a parallelogram, a roof slope that narrows towards the ridge is a refusal, no vanishing point
 *   anywhere — and buildings still come back with roofs that close in towards the top. A fifth wording is precisely what must not be added: a projection is a
 *   geometric constraint a draughtsman holds by LOOKING, not by reading. So the reference is built by code, exact by construction, and copied instead of deduced.
 *
 *   THE PROJECTION HAS A NAME, AND IT IS ORTHOGONAL TRIMETRIC AXONOMETRY AT AZIMUTH ZERO. Orthogonal because the rays are parallel and meet the picture plane
 *   square on — no vanishing point, anywhere. Trimetric because the three world axes are each reduced by a DIFFERENT factor: width untouched at 1, ground depth at
 *   0.875, standing height at 0.5. Isometry is the special case where the three are equal, which this is not and must never be drawn as. Azimuth zero because
 *   there is no rotation about the vertical: one looks straight down the world grid, so a north-south face is seen exactly edge-on and has no width at all. The
 *   project calls the whole thing PA60, sixty degrees of plunge; the two names describe one camera.
 *
 *   IT MAKES NO CLAIM BEYOND THE PROJECTION. No texture, no material colour, no cast shadow, no style, no caption and no figure — flat greys and clean black
 *   edges, and nothing else. Whatever else were drawn here would be copied too, and the plate would then be teaching something nobody decided.
 *
 *   AND THAT IS WHY THERE ARE TWO IMAGES RATHER THAN ONE ANNOTATED IMAGE. A human cannot check a drawing whose tiles, dimensions and faces are unnamed; a
 *   generator copies every mark it is shown, so a grid or a dimension put on the plate comes back drawn INSIDE the sprite. The two needs cannot share one image.
 *   BOTH COME OUT OF THE SAME project() AND THE SAME faces(), the annotated one being the bare markup translated into a wider canvas with layers added on top —
 *   never a second drawing. Computed twice, they would drift, and the annotated plate would stop proving anything about the one that is actually used.
 *
 *   THE SCALE IS ASKED OF tile_scale AND NEVER RETYPED HERE. A pivot value rewritten somewhere else is the fault this repository pays for most often, so the
 *   three figures the projection rests on are read out of the module that owns them, through a python3 call. The standing height is the one that is not published
 *   as a pixel constant: it is TX foreshortened by STANDING_HEIGHT_FACTOR, computed exactly as scripts/asset_common.py already computes it for the prompt.
 *
 *   EVERY FACE IS AN AXIS-ALIGNED RECTANGLE, AND THAT IS THE WHOLE LESSON. Under PA60 with no rotation about the vertical (doc/conception/referentiels/visuel/
 *   angle-de-vue.md), an axis-aligned box projects to rectangles with horizontal and vertical edges — nothing slants, nothing tapers, nothing converges. So the
 *   ridge runs east-west and is drawn as a horizontal straight line; the defect this plate answers, a roof slope narrowing towards the ridge, is then a departure
 *   from a rectangle, which anyone catches without measuring anything.
 *
 *   A RIDGE TURNED NORTH-SOUTH WAS DRAWN FIRST AND REFUSED, and its failure is the reason this file says so much. It is just as exact: the gable faces us, the two
 *   slopes are parallelograms, and every parallel the standard demands holds — measured, not assumed. But it READS as a concave corner, an open box seen from
 *   inside, and the first reader took the wall for the ground, the ground for a frame and the roof for a three-quarter view. A reference is copied on sight and
 *   never measured by the one copying it: being exact is not enough, being read right the first time is the requirement.
 *
 *   NOTHING IS OUTLINED EXCEPT THE VOLUME. A stroked ground rectangle reads as a frame around the image, and a frame gets copied like any other thing that is
 *   there to be seen — the same reason there is no text, no figure, no dimension and no grid.
 */

require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

/** The volume itself, in tiles: four across, three deep, walls two high, ridge one tile above the walls. */
const BUILDING_COLUMNS = 4;
const BUILDING_ROWS = 3;
const WALL_TILES = 2;
const RIDGE_TILES = 3;

/** The ground left to each side of the volume, in tiles. At zero the ground is EXACTLY as wide as the volume, so its two horizontal edges are the volume's own
 * width and are compared against it on sight — and the ground then shows only as a band above and below, which reads as background rather than as ground. Raise
 * it and the volume visibly stands ON something, at the price of a ground wider than the footprint. */
const GROUND_COLUMNS_ASIDE = 0;
const PLATE_COLUMNS = BUILDING_COLUMNS + 2 * GROUND_COLUMNS_ASIDE;

/** The ground left in front of the volume and behind it, in tiles.
 *
 * NOTHING EVER SHOWS BELOW THE FOOT OF THE WALL, AND THAT IS WHY THE FRONT STRIP IS ZERO. The volume and its footprint are the SAME ground rectangle: the
 * building does not stand behind its footprint, it covers it whole. The base of the front wall is therefore the front edge of the first row, and the footprint
 * runs from that edge AWAY from the camera, upwards in the image. A strip of ground drawn below the wall reads as footprint shown in front of the building,
 * which is a volume set down in the wrong place — the fault this constant carried until 2026-08-13, at one tile, invisible on the bare plate because a plain
 * grey band reads as background and only nameable once the annotated plate labelled it.
 *
 * WHAT IS LEFT BEHIND IS A DIFFERENT MATTER, and it is not the footprint: it is ground BEYOND the building, which the camera does see. It has to exceed the
 * volume's own rise, 96 px, or the roof would run past the ground's back edge; two tiles of depth leave a clear band of 72 px.
 */
const GROUND_ROWS_IN_FRONT = 0;
const GROUND_ROWS_BEHIND = 2;
const PLATE_ROWS = GROUND_ROWS_IN_FRONT + BUILDING_ROWS + GROUND_ROWS_BEHIND;

/** The free band around the ground, in pixels — just enough that the ground's own edges are edges, and that no stroke is clipped. */
const MARGIN_PX = 16;

/** Flat greys, and they say ONE thing: this face is not that face. No light is stated, nothing is shaded and nothing casts — a value read here as sunlight would
 * be copied as sunlight, and the plate would be making a claim about light it has no business making. */
const INK = '#000000';
const STROKE_PX = 3;
const GROUND_FILL = '#dcdcdc';
const NEAR_ROOF_FILL = '#f2f2f2';
const FAR_ROOF_FILL = '#bcbcbc';
const FRONT_WALL_FILL = '#8a8a8a';
const BACKGROUND = '#ffffff';

/** The reading layer, and it exists ONLY on the annotated plate. Coloured on purpose: nothing in the bare drawing is anything but grey, so a reader can never
 * mistake a mark of the layer for a part of the volume. */
const GRID_INK = '#c0392b';
const NOTE_INK = '#14406b';
const HIDDEN_INK = '#1a7a4c';
const NOTE_SIZE_PX = 18;

/** The room the reading layer needs around the drawing, in pixels. Dimensions stand off to the left, face names to the right, the width dimension underneath. */
const GUTTER_LEFT_PX = 200;
const GUTTER_RIGHT_PX = 330;
const GUTTER_TOP_PX = 30;
const GUTTER_BOTTOM_PX = 90;

/**
 * The three lengths the whole drawing is built on, in pixels, read out of scripts/tile_scale.py.
 *
 * A FAILED READ STOPS EVERYTHING. There is no defensible fallback: a plate drawn on guessed figures would look exactly as convincing as a right one, and it is
 * meant to be the reference other images are measured against.
 */
function projectionUnits(): array
{
    $root = dirname(__DIR__);
    $program = 'import json, sys; sys.path.insert(0, ' . var_export($root . '/scripts', true) . '); import tile_scale; '
        . 'print(json.dumps({"width": tile_scale.FILE_TILE_WIDTH, "depth": tile_scale.FILE_TILE_DEPTH, '
        . '"standing": round(tile_scale.FILE_TILE_WIDTH * tile_scale.STANDING_HEIGHT_FACTOR)}))';
    exec('python3 -c ' . escapeshellarg($program) . ' 2>&1', $output, $status);
    $raw = implode("\n", $output);
    if ($status !== 0) {
        throw new RuntimeException("scripts/tile_scale.py ne se lit pas depuis PHP (python3 a rendu {$status}) : {$raw}");
    }

    return json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
}

/**
 * A point of the world — a column across, a row into the depth, a height standing — turned into its place in the image.
 *
 * THE THREE AXES DO NOT SHARE A FACTOR, and that is the whole of PA60: width is untouched, ground depth is barely squashed, standing height is halved. Writing
 * them as one scale is exactly the mistake the plate exists to rule out.
 */
function project(array $units, float $column, float $row, float $height): array
{
    return [
        MARGIN_PX + $column * $units['width'],
        MARGIN_PX + (PLATE_ROWS - $row) * $units['depth'] - $height * $units['standing'],
    ];
}

/** One flat face: a closed polygon of world points, filled, and outlined unless it is the ground — a stroked ground rectangle reads as a FRAME around the image,
 * and a frame is copied like anything else that is seen. Its edges stay perfectly measurable as the boundary of its own fill. */
function face(array $units, array $points, string $fill, bool $outlined = true): string
{
    $drawn = [];
    foreach ($points as [$column, $row, $height]) {
        [$x, $y] = project($units, $column, $row, $height);
        $drawn[] = sprintf('%.2f,%.2f', $x, $y);
    }
    $outline = $outlined ? ' stroke="' . INK . '" stroke-width="' . STROKE_PX . '" stroke-linejoin="miter"' : '';

    return '<polygon points="' . implode(' ', $drawn) . '" fill="' . $fill . '"' . $outline . '/>';
}

/**
 * Every visible face of the plate, back to front, each as a list of world points, the grey it takes and whether it is outlined.
 *
 * ONLY WHAT THE CAMERA SEES IS LISTED, and under this camera that is very little: the back wall is behind the volume, and the two gable ends run north-south, so
 * they are seen exactly edge-on and have zero apparent width. None is drawn and none is faked into view — a visible flank is a rotation about the vertical, which
 * is the very defect this plate exists to refuse.
 */
function faces(): array
{
    $front = GROUND_ROWS_IN_FRONT;
    $back = $front + BUILDING_ROWS;
    $ridge = $front + BUILDING_ROWS / 2;
    $left = GROUND_COLUMNS_ASIDE;
    $right = $left + BUILDING_COLUMNS;

    return [
        // The ground. Its front and back edges are the same length because the projection has no vanishing point, and both are left clear of the volume so that
        // this can be SEEN rather than taken on trust.
        [[[0, 0, 0], [PLATE_COLUMNS, 0, 0], [PLATE_COLUMNS, PLATE_ROWS, 0], [0, PLATE_ROWS, 0]], GROUND_FILL, false],
        // The far slope, from the ridge going away and down. It shows small: moving one tile back raises a point by a tile of ground depth, dropping one tile of
        // standing height lowers it by half a tile, and here the two work against each other.
        [[[$left, $ridge, RIDGE_TILES], [$right, $ridge, RIDGE_TILES], [$right, $back, WALL_TILES], [$left, $back, WALL_TILES]], FAR_ROOF_FILL, true],
        // The near slope, from the ridge coming forward and down. The same real surface as the far one, more than twice as tall on screen — the two gains adding
        // up this time. Nothing but the plunge produces that difference.
        [[[$left, $ridge, RIDGE_TILES], [$right, $ridge, RIDGE_TILES], [$right, $front, WALL_TILES], [$left, $front, WALL_TILES]], NEAR_ROOF_FILL, true],
        // The front wall, standing straight: full width, half height. It is the face that states the ratio at a glance — a tile across keeps its whole length, a
        // tile standing keeps half of it.
        [[[$left, $front, 0], [$right, $front, 0], [$right, $front, WALL_TILES], [$left, $front, WALL_TILES]], FRONT_WALL_FILL, true],
    ];
}

/**
 * The drawing itself — the polygons and nothing else, in one string shared by both plates.
 *
 * THE VOLUME MUST NOT REACH OVER THE GROUND'S BACK EDGE, and the check sits here rather than in a comment because the plate is silently wrong if it does: the two
 * ground edges could no longer be compared, and the drawing would still look perfectly plausible. Read off the points actually drawn, never off the one point
 * someone believed to be the highest.
 */
function volume(array $units): string
{
    $drawn = faces();
    $groundBack = project($units, 0, PLATE_ROWS, 0)[1];
    $parts = [];
    foreach ($drawn as [$points, $fill, $outlined]) {
        foreach ($points as [$column, $row, $standing]) {
            if ($standing > 0 && project($units, $column, $row, $standing)[1] <= $groundBack) {
                throw new RuntimeException('Le volume dépasse le bord du fond du sol : la planche perd le bord qu\'elle sert à comparer. Creuser GROUND_ROWS_BEHIND.');
            }
        }
        $parts[] = face($units, $points, $fill, $outlined);
    }

    return implode("\n", $parts);
}

/** An SVG document around a body, with the body shifted by the gutters the reading layer needs. The bare plate asks for no gutter at all, so its body sits where
 * project() puts it and the two drawings are the same markup at the same scale — the whole point of building them from one calculation. */
function document(array $units, string $body, int $left = 0, int $top = 0, int $right = 0, int $bottom = 0): string
{
    $width = PLATE_COLUMNS * $units['width'] + 2 * MARGIN_PX + $left + $right;
    $height = PLATE_ROWS * $units['depth'] + 2 * MARGIN_PX + $top + $bottom;

    return sprintf('<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">', $width, $height, $width, $height) . "\n"
        . sprintf('<rect width="%.0f" height="%.0f" fill="%s"/>', $width, $height, BACKGROUND) . "\n"
        . sprintf('<g transform="translate(%d,%d)">', $left, $top) . "\n" . $body . "\n</g>\n</svg>\n";
}

/** A dimension standing off to the left of the drawing: a line between two heights of the image, a tick at each end, and what it measures IN TILES.
 *
 * ITS LABEL IS TURNED ALONG THE LINE, and that is not a matter of taste: written flat, three stacked dimensions need as much gutter as the drawing is wide, and
 * the outermost one runs clean off the canvas — which is what the first annotated plate did. */
function verticalNote(float $x, float $top, float $bottom, string $label): string
{
    $tick = 9;
    $middle = ($top + $bottom) / 2;

    return sprintf('<path d="M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2" fill="none"/>',
            $x, $top, $x, $bottom, $x - $tick, $top, $x + $tick, $top, $x - $tick, $bottom, $x + $tick, $bottom, NOTE_INK)
        . sprintf('<text x="%.1f" y="%.1f" text-anchor="middle" transform="rotate(-90 %.1f %.1f)" font-family="sans-serif" font-size="%d" fill="%s">%s</text>',
            $x - 12, $middle, $x - 12, $middle, NOTE_SIZE_PX, NOTE_INK, $label);
}

/** The same, lying under the drawing. */
function horizontalNote(float $y, float $left, float $right, string $label): string
{
    $tick = 9;

    return sprintf('<path d="M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2" fill="none"/>',
            $left, $y, $right, $y, $left, $y - $tick, $left, $y + $tick, $right, $y - $tick, $right, $y + $tick, NOTE_INK)
        . sprintf('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="sans-serif" font-size="%d" fill="%s">%s</text>',
            ($left + $right) / 2, $y + NOTE_SIZE_PX + 8, NOTE_SIZE_PX, NOTE_INK, $label);
}

/** The name of one face, written to the right of the drawing with a leader running back to the middle of the face it names. */
function faceNote(float $fromX, float $fromY, float $toX, float $toY, string $label): string
{
    return sprintf('<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2" fill="none"/><circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>',
            $fromX, $fromY, $toX, $toY, NOTE_INK, $fromX, $fromY, NOTE_INK)
        . sprintf('<text x="%.1f" y="%.1f" text-anchor="start" font-family="sans-serif" font-size="%d" fill="%s">%s</text>',
            $toX + 10, $toY + NOTE_SIZE_PX / 3, NOTE_SIZE_PX, NOTE_INK, $label);
}

/**
 * The reading layer: the tile grid, the dimensions and the names of the faces. Everything here is measured through project(), so it can only ever agree with the
 * drawing it annotates.
 *
 * EVERY DIMENSION IS SAID IN TILES AND NEVER IN PIXELS (règles du dépôt). A figure in pixels makes its reader divide before knowing what he is looking at, and it
 * stops meaning anything the day the master's fineness changes — while « trois cases » stays true whatever the scale.
 */
function readingLayer(array $units): string
{
    $front = GROUND_ROWS_IN_FRONT;
    $back = $front + BUILDING_ROWS;
    $ridge = $front + BUILDING_ROWS / 2;
    $left = GROUND_COLUMNS_ASIDE;
    $right = $left + BUILDING_COLUMNS;
    $parts = [];

    // THE GRID IS THE GROUND'S OWN TILES, DRAWN OVER EVERYTHING. Drawn underneath, it would be hidden by the volume — which is exactly where the reader needs it,
    // to count how many tiles the building covers.
    $lines = [];
    for ($column = 0; $column <= PLATE_COLUMNS; $column++) {
        [$x, $y] = project($units, $column, 0, 0);
        [, $top] = project($units, $column, PLATE_ROWS, 0);
        $lines[] = sprintf('M %.1f %.1f L %.1f %.1f', $x, $y, $x, $top);
    }
    for ($row = 0; $row <= PLATE_ROWS; $row++) {
        [$x, $y] = project($units, 0, $row, 0);
        [$end] = project($units, PLATE_COLUMNS, $row, 0);
        $lines[] = sprintf('M %.1f %.1f L %.1f %.1f', $x, $y, $end, $y);
    }
    $parts[] = sprintf('<path d="%s" stroke="%s" stroke-width="1.5" fill="none" opacity="0.55" stroke-dasharray="7 5"/>', implode(' ', $lines), GRID_INK);

    // THE FOOTPRINT IS DRAWN WHERE IT ACTUALLY IS, WHICH IS BEHIND THE BUILDING, and it is drawn as a HIDDEN LINE — broken stroke, translucent wash — because
    // that is what technical drawing uses to say « this is masked ». Moving it into the clear to make it visible would be drawing the volume off its own ground,
    // and an annotated plate that lies about the geometry it annotates proves nothing about the bare one.
    $footprint = [];
    foreach ([[$left, $front], [$right, $front], [$right, $back], [$left, $back]] as [$column, $row]) {
        [$x, $y] = project($units, $column, $row, 0);
        $footprint[] = sprintf('%.1f,%.1f', $x, $y);
    }
    $parts[] = sprintf('<polygon points="%s" fill="%s" fill-opacity="0.08" stroke="%s" stroke-width="2.5" stroke-dasharray="14 8"/>',
        implode(' ', $footprint), HIDDEN_INK, HIDDEN_INK);

    // The dimensions, in the left gutter, each at its own stand-off so two of them never sit on the same line.
    [$xLeft, $wallFoot] = project($units, $left, $front, 0);
    [, $wallTop] = project($units, $left, $front, WALL_TILES);
    [, $ridgeTop] = project($units, $left, $ridge, RIDGE_TILES);
    [, $ridgeGround] = project($units, $left, $ridge, 0);
    [, $groundFront] = project($units, $left, $front, 0);
    [, $groundBack] = project($units, $left, $back, 0);
    $parts[] = verticalNote($xLeft - 40, $wallTop, $wallFoot, 'Mur : 2 cases de haut');
    $parts[] = verticalNote($xLeft - 105, $ridgeTop, $ridgeGround, 'Faîte : 3 cases de haut');
    $parts[] = verticalNote($xLeft - 170, $groundBack, $groundFront, 'Emprise : 3 cases de profondeur');

    // The width, underneath the ground.
    [$xRight] = project($units, $right, 0, 0);
    [, $groundBottom] = project($units, 0, 0, 0);
    $parts[] = horizontalNote($groundBottom + 40, $xLeft, $xRight, 'Volume : 4 cases de large');

    // The names, in the right gutter, each leader starting at the middle of the face it names.
    $rail = $xRight + 90;
    [, $farMiddle] = project($units, 0, ($ridge + $back) / 2, (RIDGE_TILES + WALL_TILES) / 2);
    [, $nearMiddle] = project($units, 0, ($ridge + $front) / 2, (RIDGE_TILES + WALL_TILES) / 2);
    [, $wallMiddle] = project($units, 0, $front, WALL_TILES / 2);
    // The footprint is named at ITS OWN centre, under the roof — the leader has to end on the hidden rectangle, or the name would point at nothing.
    [, $footprintMiddle] = project($units, 0, ($front + $back) / 2, 0);
    $centre = ($xLeft + $xRight) / 2;
    $parts[] = faceNote($centre, $farMiddle, $rail, $farMiddle, 'Versant arrière');
    $parts[] = faceNote($centre, $nearMiddle, $rail, $nearMiddle, 'Versant avant');
    $parts[] = faceNote($centre, $wallMiddle, $rail, $wallMiddle, 'Mur de façade');
    $parts[] = faceNote($centre, $footprintMiddle, $rail, $footprintMiddle, 'Emprise au sol (masquée)');

    return implode("\n", $parts);
}

/** SVG to PNG, through the project's validated converter (doc/outils-exterieurs.md). Its absence is said out loud, never worked around. */
function convert(string $svgPath, string $pngPath): void
{
    exec('command -v rsvg-convert', $found, $status);
    if ($status !== 0) {
        throw new RuntimeException('rsvg-convert est absent : la planche reste en SVG et personne ne peut la regarder.');
    }
    exec('rsvg-convert -o ' . escapeshellarg($pngPath) . ' ' . escapeshellarg($svgPath) . ' 2>&1', $output, $status);
    if ($status !== 0) {
        throw new RuntimeException("rsvg-convert a échoué ({$status}) : " . implode("\n", $output));
    }
}

/** Writes one plate, SVG then PNG, and says where it landed. */
function write(string $pngPath, string $svg, string $what): void
{
    $svgPath = preg_replace('/\.png$/i', '', $pngPath) . '.svg';
    if (file_put_contents($svgPath, $svg) === false) {
        throw new RuntimeException("{$svgPath} ne s'écrit pas.");
    }
    convert($svgPath, $pngPath);
    echo "{$what} : {$pngPath}\n";
    echo "  SVG : {$svgPath}\n";
}

// local/planches/ AND NOT var/tmp/: `var/` belongs to the application and holds what a program writes while running, `local/` belongs to the agent and holds
// what it produces for itself (règles du dépôt, deux portées). A plate is the agent's own output, and the review server already serves local/.
$target = $argv[1] ?? dirname(__DIR__) . '/local/planches/planche-projection.png';
$directory = dirname($target);
if (!is_dir($directory) && !mkdir($directory, 0o777, true) && !is_dir($directory)) {
    throw new RuntimeException("{$directory} ne se crée pas : la planche n'a nulle part où s'écrire.");
}

$units = projectionUnits();
$body = volume($units);
write($target, document($units, $body), 'Planche nue, pour le générateur');
$annotated = preg_replace('/\.png$/i', '', $target) . '-annotee.png';
write($annotated, document($units, $body . "\n" . readingLayer($units), GUTTER_LEFT_PX, GUTTER_TOP_PX, GUTTER_RIGHT_PX, GUTTER_BOTTOM_PX),
    "Planche annotée, pour l'opérateur");

echo "Échelle lue dans tile_scale : une case de large {$units['width']} px, une case de profondeur au sol {$units['depth']} px, une case de hauteur debout {$units['standing']} px.\n";
echo 'Volume : ' . BUILDING_COLUMNS . ' cases de large, ' . BUILDING_ROWS . ' de profondeur, murs à ' . WALL_TILES . " cases, faîte à " . RIDGE_TILES . " cases.\n";

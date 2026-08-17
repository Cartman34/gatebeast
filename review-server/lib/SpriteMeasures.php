<?php
/**
 * USAGE
 *   What a delivered image measures, and whether it obeys the parallel projection. `SpriteMeasures::get()->of($path)` returns the box, the ink and the margins;
 *   `->edges($path)` returns the silhouette's west and east boundary row by row; `->parallelism($path)` turns those edges into a verdict.
 *
 * INTENTION
 *   THE TWO EQUALITIES OF THE SOCLE ARE MEASURABLE, AND ONLY A MEASURE SETTLES THEM. Under an orthographic projection at azimuth zero, every line running
 *   north-south — a ground edge, a wall foot, a roof eave — projects VERTICAL: its abscissa does not move. A silhouette boundary that drifts steadily as it
 *   descends is therefore a vanishing point, which this projection forbids. It is the one defect the eye argues about for three sessions and a column of figures
 *   settles in one command.
 *
 *   IT IS A SERVICE BECAUSE TWO THINGS NEED IT: the workshop page prints these figures under each image, and `scripts/check-parallel-projection.php` renders a
 *   verdict on them. Written twice, the two would disagree the first time the opacity threshold or the straight-run tolerance moved, and nothing on screen would
 *   say which was right.
 *
 *   WHAT IT CANNOT DO, SAID HERE RATHER THAN DISCOVERED LATER: it reads the SILHOUETTE, not the walls. Above the eaves the boundary may legitimately be a roof
 *   rake, which slopes. So it reports WHERE the boundary stops being vertical and by how much, and never claims to name the part at fault — that reading belongs
 *   to whoever looks at the image beside it.
 */

class SpriteMeasures
{
    private static ?self $instance = null;

    /** A pixel counts as drawn above this opacity, on 255. Just under opaque, so a chroma-key fringe left at a few percent does not move the measured edge. */
    public const OPAQUE = 120;

    /** How far an edge may drift over a run and still count as vertical, in pixels of abscissa per pixel of descent. Below it, the wobble is the drawing's own. */
    public const VERTICAL_TOLERANCE = 0.02;

    /** The shortest run of rows that counts as an edge rather than a corner: below it, a stair step or a moulding would read as a leaning wall. */
    public const RUN_MINIMUM = 40;

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The image, opened and its alpha readable — a single place to raise when a file cannot be read, rather than three callers each with their own message. */
    private function open(string $path): \GdImage
    {
        if (!is_file($path)) {
            throw new RuntimeException(sprintf('FAULT l\'image « %s » est absente : il n\'y a rien à mesurer.', $path));
        }
        $image = @imagecreatefrompng($path);
        if ($image === false) {
            throw new RuntimeException(sprintf('FAULT l\'image « %s » ne se lit pas comme un PNG.'
                . ' Solution — vérifier le fichier livré par la génération.', $path));
        }
        imagealphablending($image, false);

        return $image;
    }

    /** True when this pixel is drawn. In GD the alpha runs 0 (opaque) to 127 (transparent) — the reverse of the usual reading, inverted here once. */
    private function drawn(\GdImage $image, int $x, int $y): bool
    {
        return (127 - ((imagecolorat($image, $x, $y) >> 24) & 0x7F)) * 2 >= self::OPAQUE;
    }

    /**
     * The box, the ink and the four margins, in tiles.
     *
     * THE INK IS WHAT IS MEASURED, NEVER THE BOX (critique of BT-001 v1, 2026-08-13): the chain pads the canvas with transparent bands to reach the height asked
     * for, and « hauteur tenue » was once recorded on emptiness.
     */
    public function of(string $path, int $txPixels, int $tyPixels): array
    {
        $image = $this->open($path);
        $width = imagesx($image);
        $height = imagesy($image);
        $minX = $width;
        $maxX = -1;
        $minY = $height;
        $maxY = -1;
        for ($y = 0; $y < $height; $y++) {
            for ($x = 0; $x < $width; $x++) {
                if (!$this->drawn($image, $x, $y)) {
                    continue;
                }
                $minX = min($minX, $x);
                $maxX = max($maxX, $x);
                $minY = min($minY, $y);
                $maxY = max($maxY, $y);
            }
        }
        if ($maxX < 0) {
            throw new RuntimeException(sprintf('FAULT l\'image « %s » est entièrement transparente : il n\'y a rien à mesurer.', $path));
        }

        return [
            'box' => ['width' => $width, 'height' => $height, 'tx' => $width / $txPixels, 'ty' => $height / $tyPixels],
            'ink' => ['width' => $maxX - $minX + 1, 'height' => $maxY - $minY + 1,
                'tx' => ($maxX - $minX + 1) / $txPixels, 'ty' => ($maxY - $minY + 1) / $tyPixels],
            'margins' => ['north' => $minY / $tyPixels, 'south' => ($height - 1 - $maxY) / $tyPixels,
                'west' => $minX / $txPixels, 'east' => ($width - 1 - $maxX) / $txPixels],
        ];
    }

    /** The silhouette's west and east boundary for every row that carries ink, in pixels. */
    public function edges(string $path): array
    {
        $image = $this->open($path);
        $width = imagesx($image);
        $height = imagesy($image);
        $rows = [];
        for ($y = 0; $y < $height; $y++) {
            $left = null;
            $right = null;
            for ($x = 0; $x < $width; $x++) {
                if (!$this->drawn($image, $x, $y)) {
                    continue;
                }
                $left ??= $x;
                $right = $x;
            }
            if ($left !== null) {
                $rows[$y] = ['west' => $left, 'east' => $right];
            }
        }

        return $rows;
    }

    /**
     * The longest straight runs of each boundary, and their slope — the figures a verdict on the parallel projection is made of.
     *
     * A RUN IS A STRETCH OF ROWS WHOSE EDGE MOVES AT A CONSTANT RATE, and it is cut as soon as that rate changes: a corner, an eave, a doorway. Each run then
     * carries one number, its slope in abscissa per row. Zero is the projection the socle demands; anything else is what the image actually did.
     */
    public function runs(string $path, string $side): array
    {
        $rows = $this->edges($path);
        $ys = array_keys($rows);
        $runs = [];
        $start = null;
        $previous = null;
        $rate = null;
        foreach ($ys as $index => $y) {
            $value = $rows[$y][$side];
            if ($previous === null || $y !== $ys[$index - 1] + 1) {
                $start = $y;
                $previous = $value;
                $rate = null;
                continue;
            }
            $step = $value - $previous;
            // A RUN HOLDS WHILE THE STEP STAYS WITHIN ONE PIXEL OF ITS RATE: an edge drawn at a slope of a third of a pixel per row advances 0, 0, 1, 0, 0, 1 —
            // demanding an identical step would cut it into six runs of nothing and hide the very slope being looked for.
            if ($rate !== null && abs($step - $rate) > 1) {
                $runs[] = ['from' => $start, 'to' => $ys[$index - 1], 'start' => $rows[$start][$side], 'end' => $previous];
                $start = $ys[$index - 1];
                $rate = null;
            }
            $rate = $rate === null ? $step : ($rate + $step) / 2;
            $previous = $value;
        }
        if ($start !== null && $previous !== null) {
            $runs[] = ['from' => $start, 'to' => end($ys), 'start' => $rows[$start][$side], 'end' => $previous];
        }

        $kept = [];
        foreach ($runs as $run) {
            $span = $run['to'] - $run['from'];
            if ($span < self::RUN_MINIMUM) {
                continue;
            }
            $run['span'] = $span;
            $run['slope'] = ($run['end'] - $run['start']) / $span;
            $kept[] = $run;
        }
        usort($kept, fn (array $one, array $other) => $other['span'] <=> $one['span']);

        return $kept;
    }

    /**
     * The verdict: does the silhouette hold the parallel projection, and where does it stop?
     *
     * IT NAMES THE WORST RUN RATHER THAN A SCORE. « 0,18 px par pixel entre y=285 et y=641 » can be gone and looked at; a percentage of conformity cannot, and it
     * would let a small drift everywhere pass for a clean image.
     */
    public function parallelism(string $path): array
    {
        $faults = [];
        $worst = null;
        foreach (['west', 'east'] as $side) {
            foreach ($this->runs($path, $side) as $run) {
                if (abs($run['slope']) <= self::VERTICAL_TOLERANCE) {
                    continue;
                }
                $run['side'] = $side;
                $faults[] = $run;
                if ($worst === null || abs($run['slope']) * $run['span'] > abs($worst['slope']) * $worst['span']) {
                    $worst = $run;
                }
            }
        }
        usort($faults, fn (array $one, array $other) => abs($other['slope']) * $other['span'] <=> abs($one['slope']) * $one['span']);

        return ['held' => $faults === [], 'faults' => $faults, 'worst' => $worst];
    }
}

<?php
/**
 * USAGE
 *   The tile grid laid over a sprite, wherever a sprite is shown: what it covers on the ground, what its volume overhangs, its two axes, and the paving of whole
 *   tiles the whole thing is read against. `FootprintGrid::get()->tiling(...)` gives the paving in figures, `->markup(...)` gives the grid to lay on the picture,
 *   and `->pictureStyle(...)` gives the wrapper the room the grid takes above the image.
 *
 * INTENTION
 *   TWO PAGES SHOW THE SAME SPRITE AND MUST SHOW THE SAME GRID. It was born on the sprites review page and the workshop page needs it exactly: written twice, the
 *   two would answer differently the first time the projected tile, the rise or a class name moved — and nothing on screen would say which one was right. The
 *   repository's rule is plain, « un concept existant ne se recrée jamais » : it moves here, and both pages call it.
 *
 *   THE PROJECTED TILE IS THE ONE MODEL VALUE THIS CODE COPIES, and it is the PUBLISHED RATIO, 84 over 96 — never the sine of the camera angle. Its source,
 *   `scripts/tile_scale.py`, says so in as many words: « THE PIXEL LADDER IS AUTHORITATIVE, NOT THE FACTOR […] THE RATIO IS READ FROM THOSE TWO NUMBERS AND NEVER
 *   FROM sin(60°) ». The copy said 0.8660 until 2026-08-13, one percent off, which nothing showed while the grid merely drew lines — and which turned glaring the
 *   day whole tiles were counted: a flat piece delivered at 96 × 84, exactly one tile tall, measured 1.01 tiles and bought a second, empty row.
 */

class FootprintGrid
{
    private static ?self $instance = null;

    /**
     * How much a ground length running away from the eye is foreshortened under the 60-degree camera: the projected tile is 96 wide by 84 deep.
     *
     * Written here until the pages can ask the service that holds the scale, which is in Python — see the intention above for why it is this ratio and not the sine.
     */
    public const GROUND_DEPTH_FACTOR = 84 / 96;

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * How a thumbnail is paved in tiles: the tile itself, the whole rows that cover the image, and how far the last of them rises above it.
     *
     * HELD IN ONE PLACE BECAUSE TWO THINGS NEED IT, and they must never answer differently: the grid draws the paving, and the wrapper reserves the room the paving
     * takes above the image. Computed twice, the reserve would fall out of step with the drawing at the first change of factor — and nothing on screen would say so,
     * beyond a grid quietly climbing over the card above it.
     */
    public function tiling(string $code, array $spread, int $width, int $height): array
    {
        if ($width <= 0 || $height <= 0) {
            throw new RuntimeException(sprintf('La vignette de %s est annoncée %d × %d px : une grille ne se pose pas sur une image sans surface.'
                . ' Reconstruire les vignettes — php review-server/build.php /sprites — ou vérifier l\'image livrée de ce sujet.', $code, $width, $height));
        }
        // A TILE OF DEPTH IS NOT PROJECTED LIKE A TILE OF WIDTH, and forgetting it dropped the footprint frame far below the subject's ground — two tiles of
        // emptiness in front of the building, which the operator spotted. Under the world's camera a ground length running away is seen foreshortened.
        $tileYPixels = $width / $spread['columns'] * self::GROUND_DEPTH_FACTOR;
        // HOW MANY WHOLE ROWS COVER THE IMAGE, and how far above it the last of them reaches. The epsilon is float safety alone: an image exactly four tiles tall
        // must give four rows and no rise, and 4.0000000001 would otherwise buy an empty fifth row.
        $rows = max(1, (int) ceil($height / $tileYPixels - 1e-6));

        return [
            // The tile as a percentage of the thumbnail: the width carries the cover's columns, and the height follows the same scale since the image is never distorted.
            'tile' => 100 / $spread['columns'],
            // The vertical tile as a percentage of the IMAGE, which is what the ground footprint is measured against — it is anchored on the image's own bottom edge.
            'tileY' => $tileYPixels / $height * 100,
            'rows' => $rows,
            'risePercent' => ($rows * $tileYPixels - $height) / $height * 100,
            'risePixels' => $rows * $tileYPixels - $height,
        ];
    }

    /**
     * The style the picture wrapper carries: the room the risen grid takes above the image.
     *
     * IT IS A MARGIN, NEVER A PADDING. The grid rises out of the image to close its top tile, and without that reserve it climbs over whatever the page prints
     * above the picture. A margin leaves the wrapper's own box exactly on the image, which is what the rune anchor measures and what the grid is laid on; padding
     * would move both by the height of the rise.
     *
     * IT IS IN PIXELS BECAUSE A PERCENTAGE HERE WOULD MEASURE THE WRONG THING: a vertical margin is a percentage of the container's WIDTH, which is the card's,
     * not the image's. The thumbnail's size is known when this is written, so the reserve is the rise itself.
     *
     * AND IT IS NEVER SHORT, WHICH IS THE PROPERTY THAT MATTERS. A card narrower than its thumbnail shrinks it — `max-width: 100%` on the image — and the grid,
     * being in percentages, shrinks with it while this reserve does not. CSS only ever shrinks here, never magnifies, so the reserve is at worst larger than the
     * rise: a little empty ground above a very wide subject, never a tile climbing over the card.
     */
    public function pictureStyle(array $tiling): string
    {
        return sprintf('margin-top: %.2fpx', $tiling['risePixels']);
    }

    /**
     * The grid laid over a sprite: its ground footprint, its cover when it overhangs, and the two axes.
     *
     * EVERYTHING IS SAID IN TILES AND RENDERED IN PERCENTAGES of the thumbnail, never in pixels: the thumbnail changes size with the subject's footprint and with
     * the magnification, while a tile stays a tile. Writing pixels here would make them drift from the image the moment a size changes.
     *
     * THE IMAGE IS LAID OUT ON THE COVER'S WIDTH, not the footprint's — that is what the thumbnail factory does. The ground footprint is therefore drawn as a PART
     * of that width, centred, and not as the whole thumbnail: which is exactly what one wants to see of an oak whose crown overhangs its foot.
     *
     * AND A TILE IS ALWAYS DRAWN WHOLE, EVEN WHERE THE IMAGE DOES NOT FILL IT (operator, 2026-08-12, capture in hand: « il ne doit jamais y avoir de demi case, une
     * case doit être affichée entière même si incomplète »). The thumbnail is a whole number of tiles ACROSS, because that is the width it is made at, and never a
     * whole number DOWN, because its height is the delivered image's: TR-063-v19 is 3.4 tiles tall. Paved from the ground up, the top row was then a fraction with
     * no line to close it — a half tile. The grid therefore rises ABOVE the image up to the next whole tile, and it is the GRID that grows, never the image: the
     * sprite keeps its size and its place, and it is the sprite that stops short inside a tile drawn whole. Growing the image instead would change what is judged.
     */
    public function markup(array $subject, array $spread, array $tiling): string
    {
        $footprint = $subject['footprint'];
        $covers = ($spread['columns'] !== $footprint['columns']) || ($spread['rows'] !== $footprint['rows']);
        $footWidth = 100 * $footprint['columns'] / $spread['columns'];
        $footHeight = $tiling['tileY'] * $footprint['rows'];

        return sprintf(
            // THE PAVING IS SAID IN THE RISEN GRID'S OWN TERMS, never in the image's: `--tile-y` is a percentage of a box that is exactly `$rows` tiles tall, so one
            // row is one row-th of it and no rounding can make the last one a sliver. `--tile` stays a percentage of the width, which the rise does not touch.
            '<span class="footprint" style="--tile: %.4f%%; --tile-y: %.4f%%; --tile-rise: %.4f%%">'
            . '<span class="footprint-ground" style="width: %.4f%%; height: %.4f%%" title="Emprise au sol : %d × %d cases"></span>'
            . '%s'
            . '<span class="footprint-axis footprint-axis--x"></span><span class="footprint-axis footprint-axis--y"></span>'
            . '</span>',
            $tiling['tile'], 100 / $tiling['rows'], $tiling['risePercent'], $footWidth, $footHeight,
            (int) $footprint['columns'], (int) $footprint['rows'],
            $covers ? sprintf('<span class="footprint-cover" title="Couvert : %d × %d cases"></span>',
                (int) $spread['columns'], (int) $spread['rows']) : ''
        );
    }
}

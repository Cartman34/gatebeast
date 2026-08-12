<?php
/**
 * USAGE
 *   Draw the rune of one individual over its sprite: `Rune::get()->svg('SP-001-1', $anchor, $tilePixels)` returns the SVG markup to lay on top of the image,
 *   already scaled, placed, tilted and coloured. `Rune::get()->individual('SP-001-1')` gives what the data says of it, for a caller that needs the raw values.
 *
 * INTENTION
 *   NOTHING HERE IS DECIDED, EVERYTHING IS APPLIED (referentiels/technique/rendu-en-calques.md). The renderer never looks for a forehead and never follows a
 *   posture: the shape and the colour come from the individual, the point and the tilt from the image, the size from the rule. Four declared values, one drawing.
 *
 *   THE SIZE IS CONSTANT AND NEVER MULTIPLIED BY THE BEARER. `size_tx` is a fraction of a tile, so a big creature wears the same mark as a small one — it looks
 *   smaller on her, and that is the decision (referentiels/visuel/index.md). Scaling it with the sprite is the one mistake that cannot be caught by eye later:
 *   every image looks plausible on its own.
 *
 *   THE PATH IS DRAWN IN A HUNDRED-UNIT SQUARE, and lands as an SVG `viewBox` rather than recomputed coordinates: a transform is exact, a recomputation drifts,
 *   and the day a shape is redrawn nobody has to touch this file.
 */

class Rune
{
    private static ?self $instance = null;

    /** Le carré de référence dans lequel vivent tous les tracés, et il ne se déduit pas : c'est la donnée qui le déclare. */
    private const SQUARE = 100;

    /** L'épaisseur du trait, dans les unités de ce carré — la règle du visuel : un seul trait continu, bouts et jointures arrondis. */
    private const STROKE = 8;

    private array $data;

    public function __construct()
    {
        $path = dirname(__DIR__, 2) . '/assets/runes.json';
        if (!is_file($path)) {
            throw new RuntimeException('la donnée des runes est absente : assets/runes.json');
        }
        $this->data = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** Ce que la donnée dit d'un individu : son espèce, sa forme, sa couleur. */
    public function individual(string $code): array
    {
        $individuals = $this->data['individuals'] ?? [];
        if (!isset($individuals[$code])) {
            throw new RuntimeException("l'individu « {$code} » n'est pas déclaré dans assets/runes.json — aucune rune ne peut être tracée pour lui.");
        }
        return $individuals[$code];
    }

    /** Tous les individus déclarés, avec leur espèce, leur forme et leur couleur. */
    public function individuals(): array
    {
        return $this->data['individuals'] ?? [];
    }

    /** La taille de la rune, en largeur de case. Constante, et lue à son foyer. */
    public function sizeTx(): float
    {
        if (!isset($this->data['size_tx'])) {
            throw new RuntimeException('assets/runes.json ne déclare pas « size_tx » — le rendu ne peut pas savoir à quelle taille tracer.');
        }
        return (float) $this->data['size_tx'];
    }

    /**
     * Le tracé d'un individu, posé sur son ancre.
     *
     * `$anchor` est la clé `rune_anchor_px` de la représentation — `x`, `y` et `tilt_deg` —, dans les pixels de l'image livrée ; `$tilePixels` est la largeur
     * d'une case dans le rendu où l'on dessine. Les deux viennent de l'appelant parce que lui seul sait à quelle échelle il compose.
     */
    public function svg(string $code, array $anchor, float $tilePixels): string
    {
        foreach (['x', 'y'] as $key) {
            if (!isset($anchor[$key])) {
                throw new RuntimeException("l'ancre de rune de « {$code} » n'a pas de « {$key} » — un point incomplet poserait la marque n'importe où.");
            }
        }
        $individual = $this->individual($code);
        $shape = $this->data['shapes'][$individual['shape']] ?? null;
        if ($shape === null) {
            throw new RuntimeException("la forme « {$individual['shape']} » de « {$code} » n'a aucune géométrie déclarée.");
        }
        $side = $this->sizeTx() * $tilePixels;
        // LE CARRÉ SE CENTRE SUR L'ANCRE : l'ancre est le point du corps où la marque se pose, pas le coin d'une boîte. Posée par son coin, la rune apparaîtrait
        // en bas à droite du point choisi à l'œil, et le décalage grandirait avec la taille du rendu — invisible sur une vignette, flagrant en grand.
        $left = $anchor['x'] - $side / 2;
        $top = $anchor['y'] - $side / 2;
        $tilt = (float) ($anchor['tilt_deg'] ?? 0);
        // L'ÉPAISSEUR RESTE DANS LES UNITÉS DU CARRÉ, et c'est tout l'intérêt du viewBox : elle suit l'échelle sans qu'on la recalcule, donc un trait de huit
        // reste un trait de huit quelle que soit la taille du rendu. Recalculée en pixels, elle dérivait d'un rendu à l'autre.
        return sprintf(
            '<svg class="rune" viewBox="0 0 %d %d" width="%.2f" height="%.2f" style="position:absolute;left:%.2fpx;top:%.2fpx;transform:rotate(%.2fdeg)" '
            . 'aria-hidden="true"><path d="%s" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            self::SQUARE, self::SQUARE, $side, $side, $left, $top, $tilt,
            htmlspecialchars($shape['path'], ENT_QUOTES), htmlspecialchars($individual['color'], ENT_QUOTES), self::STROKE
        );
    }
}

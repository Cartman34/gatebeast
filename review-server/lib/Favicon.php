<?php
/**
 * USAGE
 *   require_once __DIR__ . '/../lib/Favicon.php';
 *   $favicon = Favicon::get();     // the service instance, taken once
 *   echo $favicon->tag();          // to be put in the page's <head>
 *
 * INTENTION
 *   Every review page carries the same favicon, written once here: a tab is what tells a review page apart from twenty others, and four pages each writing their own would end up not all carrying it.
 *   The motif is the project's reference creature (operator, 2026-08-07) — a creature collection game is recognised by a creature.
 *
 *   IT IS MADE FROM THE SPRITE, NEVER BY HAND: the day the reference creature is redrawn, the favicon follows without anyone thinking about it.
 *
 *   THE WHOLE FACE IS KEPT, fitted in the square. A crop on the head was tried first, and looked at: it caught the TAIL, which rises higher than the ears, and cut the muzzle off — nothing tells a
 *   machine where a head is. The two values that locate the face are therefore written out and set by eye.
 *
 *   A served page is still a single file: the image is copied into the page, in clear, never linked. The file stays the source, the copy is only transport — same as the theme.
 */

class Favicon
{
    private static ?self $instance = null;

    /** The sprite the favicon is taken from. Only one creature exists so far; this is it, and this path is the only place to change if another replaces it. */
    private const SOURCE = 'assets/cutout/creature/SP-001-1.png';
    private const SIZE = 32;

    /**
     * Where the face sits within the silhouette, in parts of its height: how far down the square starts, and how long its side is.
     *
     * TWO VALUES WRITTEN OUT AND SET BY EYE, for want of anything better: nothing tells a machine where a head is. The first automatic crop — the top of the silhouette — caught the tail, which
     * rises higher than the ears, and cut off the muzzle. These are revisited by looking at the preview, and will be revisited the day the reference creature changes.
     */
    private const FACE_START = 0.25;
    private const FACE_HEIGHT = 0.65;

    /** The repository root, held by the service: its callers no longer have to hand it over on every call. */
    private string $root;

    public function __construct()
    {
        $this->root = dirname(__DIR__, 2);
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The tag to put in the <head>, image included. */
    public function tag(): string
    {
        return '<link rel="icon" type="image/png" href="data:image/png;base64,' . base64_encode($this->png()) . '">';
    }

    /** The favicon image, made then kept under var/tmp/ — it only changes when the sprite changes. */
    public function png(): string
    {
        $source = $this->root . '/' . self::SOURCE;
        if (!is_file($source)) {
            throw new RuntimeException('FAULT the favicon sprite is missing: ' . self::SOURCE . ' — the favicon is made from it, never by hand.');
        }
        // THE CROP GOES INTO THE KEPT FILE'S NAME, just like the sprite's date: without it, a revisited setting returned the old image without a word, and looked to have no effect.
        $cache = sprintf('%s/var/tmp/favicon-%d-%s-%s-%d.png', $this->root, self::SIZE, self::FACE_START, self::FACE_HEIGHT, filemtime($source));
        if (is_file($cache)) {
            return file_get_contents($cache);
        }

        $image = imagecreatefrompng($source);
        if ($image === false) {
            throw new RuntimeException('FAULT the favicon sprite cannot be read: ' . self::SOURCE);
        }
        [$left, $top, $right, $bottom] = $this->silhouette($image);
        $width = $right - $left + 1;
        $height = $bottom - $top + 1;
        // The square never runs outside the silhouette: wider than it, it would bring emptiness in on the sides and shrink the face by as much.
        $side = min($width, (int) round($height * self::FACE_HEIGHT));
        $faceTop = $top + (int) round($height * self::FACE_START);
        $faceLeft = $left + intdiv($width - $side, 2);

        $icon = imagecreatetruecolor(self::SIZE, self::SIZE);
        imagealphablending($icon, false);
        imagesavealpha($icon, true);
        imagefill($icon, 0, 0, imagecolorallocatealpha($icon, 0, 0, 0, 127));
        imagecopyresampled($icon, $image, 0, 0, $faceLeft, $faceTop, self::SIZE, self::SIZE, $side, $side);

        ob_start();
        imagepng($icon);
        $png = ob_get_clean();
        imagedestroy($icon);
        imagedestroy($image);

        if (!is_dir(dirname($cache))) {
            mkdir(dirname($cache), 0o775, true);
        }
        file_put_contents($cache, $png);

        return $png;
    }

    /**
     * The bounds of what is actually drawn, the emptiness around it ignored.
     *
     * A sprite is framed on its cell, not on the beast: taking the image as it stands would give a favicon three quarters empty. So the non-transparent pixels are what is looked for.
     */
    private function silhouette(\GdImage $image): array
    {
        $width = imagesx($image);
        $height = imagesy($image);
        $left = $width;
        $top = $height;
        $right = -1;
        $bottom = -1;
        for ($y = 0; $y < $height; $y++) {
            for ($x = 0; $x < $width; $x++) {
                if (((imagecolorat($image, $x, $y) >> 24) & 0x7F) >= 120) {
                    continue;
                }
                $left = min($left, $x);
                $right = max($right, $x);
                $top = min($top, $y);
                $bottom = max($bottom, $y);
            }
        }
        if ($right < 0) {
            throw new RuntimeException('FAULT the favicon sprite is fully transparent: ' . self::SOURCE);
        }

        return [$left, $top, $right, $bottom];
    }
}

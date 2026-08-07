<?php
/**
 * USAGE
 *   Put a picture in a page without carrying its full weight, whenever the page shows it smaller than the file is.
 *
 * INTENTION
 *   Turns an image on disk into what a page can carry: reduced to the size it will actually be SHOWN at, and embedded as a data URI. An artifact is one single file — it cannot fetch anything — so
 *   every picture travels inside it, and a page that embedded its images at full definition weighed sixteen times what it needed and stopped applying its own styles in the browser.
 *
 *   THE WIDTH ASKED FOR IS A WIDTH ON SCREEN, IN PIXELS, and the height follows the image's own proportions: a sprite is laid down by its width in tiles, never squeezed into a box. Nothing is
 *   cropped, nothing is padded — reducing is a delivery step, never a correction of the image.
 *
 *   Every reduction is CACHED under var/tmp/vignettes/, keyed by the file and the width: a page holds hundreds of pictures and is rebuilt a dozen times an hour. The cache is truly disposable — it
 *   rebuilds itself from the images — so it lives under var/tmp/ rather than beside the durable traces.
 *
 *   In PHP with gd, constated present on this machine: nothing here needs a library that only Python has.
 */

class Thumbnail
{
    private string $cache;

    public function __construct(private string $root = __DIR__ . '/../..')
    {
        $this->cache = $this->root . '/var/tmp/vignettes';
        if (!is_dir($this->cache)) {
            mkdir($this->cache, 0775, true);
        }
    }

    /**
     * The image reduced to `$width` pixels wide, as [data URI, width, height].
     *
     * Raises rather than returning a placeholder: an image a page cannot read is a fact its builder must report, and a silent grey square would let it ship looking finished.
     */
    public function shrink(string $relative, int $width): array
    {
        $path = $this->root . '/assets/' . $relative;
        if (!is_file($path)) {
            throw new RuntimeException("FAULT {$relative} est introuvable sous assets/ — une page ne montre pas une image qu'elle n'a pas lue.");
        }
        $key = $this->cache . '/' . substr(md5($relative . '@' . $width . '@' . filemtime($path)), 0, 16) . '.png';
        if (!is_file($key)) {
            $this->ecrire($path, $key, $width);
        }
        $size = getimagesize($key);

        return ['data:image/png;base64,' . base64_encode(file_get_contents($key)), $size[0], $size[1]];
    }

    private function ecrire(string $path, string $target, int $width): void
    {
        $source = imagecreatefrompng($path);
        if ($source === false) {
            throw new RuntimeException("FAULT {$path} n'est pas un PNG lisible.");
        }
        $sourceWidth = imagesx($source);
        $sourceHeight = imagesy($source);
        // Jamais D'AGRANDISSEMENT : une image déjà plus petite que la taille demandée reste telle quelle. L'agrandir ne rendrait pas un pixel de détail et ferait
        // croire à une finesse qui n'existe pas.
        $height = (int) max(1, round($width * $sourceHeight / $sourceWidth));
        if ($width >= $sourceWidth) {
            copy($path, $target);
            imagedestroy($source);

            return;
        }
        $reduced = imagecreatetruecolor($width, $height);
        // LA TRANSPARENCE SE PRÉSERVE, et c'est tout l'objet de ces trois lignes : une sprite détourée posée sur un fond opaque montrerait un rectangle noir.
        imagealphablending($reduced, false);
        imagesavealpha($reduced, true);
        imagefill($reduced, 0, 0, imagecolorallocatealpha($reduced, 0, 0, 0, 127));
        imagecopyresampled($reduced, $source, 0, 0, 0, 0, $width, $height, $sourceWidth, $sourceHeight);
        imagepng($reduced, $target, 9);
        imagedestroy($reduced);
        imagedestroy($source);
    }
}

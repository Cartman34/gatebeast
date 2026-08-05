<?php
/**
 * Usage:
 *   require_once __DIR__ . '/../../scripts/Capture.php';
 *   $capture = new Capture();
 *   $capture->start();
 *   ?><section class="plan"><h2><?= htmlspecialchars($title) ?></h2></section><?php
 *   $markup = $capture->take();
 *
 * Intention: let a PHP script WRITE HTML AS HTML instead of gluing it out of quoted fragments. A page built by concatenation — '<h2>' . $x . '</h2>' — hides its own structure
 * behind quotes and dots: nothing lines up, no editor colours it, a missing closing tag is invisible, and every value carries its own pair of quotes. Written between a start
 * and a take, the same markup is plain HTML with <?= ?> where it varies, and it reads like the page it produces.
 *
 * NO TEMPLATE FILE, AND THAT IS THE POINT (operator, 2026-08-05): a template in its own file needs an engine, or at least a convention for handing it the variables it needs,
 * and it stops seeing the scope it was written next to. Capturing in place keeps every variable exactly where it already is.
 *
 * The class exists rather than a bare ob_start() so that an unbalanced capture FAILS LOUDLY. PHP's own buffer is global and silent: a take() with no start() would quietly
 * hand back whatever some other part of the program was writing, and a start() never taken would swallow the rest of the output.
 */

final class Capture
{
    private int $depth = 0;

    /** Begins capturing everything the script outputs from here on. */
    public function start(): void
    {
        ob_start();
        $this->depth++;
    }

    /** Ends the innermost capture and returns what was written during it. */
    public function take(): string
    {
        if ($this->depth === 0) {
            throw new LogicException('Capture::take() sans start() : rien n\'a été mis en capture, et le tampon rendu serait celui de quelqu\'un d\'autre.');
        }
        $this->depth--;

        return ob_get_clean();
    }

    /** True while a capture is open — what a caller checks before deciding to write straight out. */
    public function running(): bool
    {
        return $this->depth > 0;
    }
}

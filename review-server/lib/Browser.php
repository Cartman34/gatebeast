<?php
/**
 * USAGE
 *   Drive the headless browser the probes look at a page with: `Browser::get()->shot($url, $out, 1400, 900)` for a picture, `->dom($url)` for the page once its script has run, `->console($url)` for
 *   what it printed on the way. Nobody assembles a browser command line, and nobody writes where the browser is.
 *
 * INTENTION
 *   THE REPETITION IS THE FAULT, AND IT WAS ALREADY PAID ONCE TODAY (opérateur, 2026-08-12 : « la répétition est interdite »). The path to the binary was written out in SEVENTEEN probe scripts, with
 *   a pinned build number inside it — `chromium-1223`. That number moves the day the browser is reinstalled, and nineteen scripts then fail at once, each with its own bare exit code and none of them
 *   naming what is missing. It is the same fault the port had, one layer further: a value of the environment copied into every caller that needs it.
 *
 *   THE PATH IS CONFIGURED, NOT DEDUCED: it lives in review-server/config.json next to the address of the review, because it is the same kind of value — something about this machine that the tooling
 *   has to be told. It is written with a leading `~` so the file carries no home directory of anyone's, and expanded here, once.
 *
 *   A MISSING BROWSER SAYS SO. Called through a bare `exec`, an absent binary returned status 127 and the probe reported "le tir d'écran a échoué (code 127)" — which reads as a broken page rather
 *   than a missing tool. The binary is checked before it is called, and the fault names the path it looked at.
 */

class Browser
{
    private static ?self $instance = null;

    /** The flags every call shares. Headless with no sandbox is what runs in this environment; the rest is what a probe always wants. */
    private const FLAGS_COMMON = '--headless --disable-gpu --no-sandbox';

    /** How long the browser is given to let a page finish its work before the picture is taken, in milliseconds. */
    public const BUDGET_DEFAULT = 8000;

    private string $binary;

    public function __construct()
    {
        $this->binary = Config::get()->path('browser');
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** Saves a picture of the page at that address, in a window of that size. */
    public function shot(string $url, string $out, int $width, int $height, int $budget = self::BUDGET_DEFAULT): void
    {
        // THE PREVIOUS PICTURE IS REMOVED FIRST, and that is the whole point of the line: left in place, it would be found by the check below and pass for the one that was just taken. A probe would
        // then report on an image from an earlier run — an error that shows nothing at all, which is the family this project forbids by name.
        if (is_file($out)) {
            unlink($out);
        }
        $this->run(sprintf('%s --hide-scrollbars --window-size=%d,%d --screenshot=%s --virtual-time-budget=%d %s 2>/dev/null',
            self::FLAGS_COMMON, $width, $height, escapeshellarg($out), $budget, escapeshellarg($url)), $url);
        if (!is_file($out)) {
            throw new RuntimeException("le navigateur n'a écrit aucune image dans {$out} pour {$url}.");
        }
    }

    /** The page as it stands once its script has run — what a probe reads to answer "did the button do anything?". */
    public function dom(string $url, int $budget = self::BUDGET_DEFAULT): string
    {
        return implode("\n", $this->run(sprintf('%s --virtual-time-budget=%d --dump-dom %s 2>/dev/null', self::FLAGS_COMMON, $budget, escapeshellarg($url)), $url));
    }

    /** What the page printed on its console, the page itself thrown away: the only way to see a script that fails without a word. */
    public function console(string $url, int $budget = self::BUDGET_DEFAULT): string
    {
        return implode("\n", $this->run(sprintf('%s --enable-logging=stderr --v=0 --virtual-time-budget=%d --dump-dom %s 2>&1 1>/dev/null', self::FLAGS_COMMON, $budget, escapeshellarg($url)), $url));
    }

    /** Runs one browser command, having made sure the browser is there, and stops on a non-zero status instead of leaving the caller with an empty result. */
    private function run(string $arguments, string $url): array
    {
        if (!is_file($this->binary)) {
            throw new RuntimeException("le navigateur est absent de {$this->binary} — la sonde ne peut rien regarder. Vérifiez la clé « browser » de " . Config::PATH . '.');
        }
        exec(escapeshellarg($this->binary) . ' ' . $arguments, $lines, $status);
        if ($status !== 0) {
            throw new RuntimeException("le navigateur a échoué (code {$status}) sur {$url}.");
        }
        return $lines;
    }
}

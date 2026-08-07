<?php
/**
 * USAGE
 *   Make failures visible and uniform, at the start of anything that runs — a command or a served page. Not called directly: the bootstrap wires it.
 *
 * INTENTION
 *   ONE WAY TO FAIL, AND ONLY ONE: an exception (operator, 2026-08-07). PHP has two error systems living side by side — its own warnings and notices, which by default print half a line and let the
 *   code carry on with wrong values, and exceptions, which stop. Two systems mean every failure has to be handled twice, and the first one is always the one that gets forgotten.
 *
 *   A warning that lets the code continue is the worst of the two: a file read that fails returns false, false gets used as a string, and the page comes out empty with nothing to say why. Turned
 *   into an exception, that same warning stops on the spot and names the file and the line.
 *
 *   The service does not decide WHAT is shown — a command writes on the error output, a page renders itself. It decides that nothing ever fails silently.
 */

class Faults
{
    private static ?self $instance = null;

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** Every PHP error — warning, notice, whatever — becomes an exception, so there is a single way to fail and a single way to catch it. */
    public function asExceptions(): void
    {
        set_error_handler(static function (int $severity, string $message, string $file, int $line): bool {
            // A severity muted by the current error_reporting level is left alone: silencing is a decision someone took, and turning it into an exception would override it.
            if (!(error_reporting() & $severity)) {
                return false;
            }

            throw new ErrorException($message, 0, $severity, $file, $line);
        });
    }

    /** For a command: an uncaught exception is reported on the error output, and the command fails — so a chain that calls it stops instead of carrying on with nothing. */
    public function onConsole(): void
    {
        set_exception_handler(static function (Throwable $fault): void {
            fwrite(STDERR, 'FAULT ' . $fault->getMessage() . ' (' . basename($fault->getFile()) . ', ligne ' . $fault->getLine() . ")\n");
            exit(1);
        });
    }

    /** For a served page: an uncaught exception is handed to the closure, which renders whatever the page wants to show instead of the browser's blank error. */
    public function onPage(callable $render): void
    {
        set_exception_handler(static function (Throwable $fault) use ($render): void {
            $render($fault);
        });
    }
}

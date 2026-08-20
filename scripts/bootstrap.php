<?php
/**
 * USAGE
 *   Start a command of `scripts/` by wiring how it fails and loading what every command needs: `require_once __DIR__ . '/bootstrap.php'; bootCommand($argv);`
 *   It returns the repository root, which is what a command asks for first.
 *
 * INTENTION
 *   ONE WAY TO FAIL, AND ONE PLACE THAT SHOWS IT (`W31 fautes-unifiees`, operator on 2026-08-12: « pourquoi tu n'utilises pas que des exceptions et une seule
 *   façon unie de les afficher ? »). The served pages had it — `review-server/bootstrap.php` wires it for everything running in the review server — and the
 *   commands did not. So a PHP warning let a command carry on with a false value, and each one invented its own message format: a `fwrite(STDERR)` here, a bare
 *   exception there, an `exit(1)` elsewhere. A chain calling them could recognise none of the three.
 *
 *   IT IS A BOOTSTRAP AND NOT A LINE TO COPY, AND THAT IS THE WHOLE POINT. Three lines repeated at the head of a hundred and twenty commands are three lines the
 *   next command will not have. What a bootstrap wires, it wires for whoever requires it — including the command written tomorrow by someone who never read this
 *   file.
 *
 *   LOADING IT DOES NOTHING; THE CALL IS THE EFFECT (operator, 2026-08-07, on the review server's own bootstrap). A require that registers handlers behind your
 *   back cannot be read, cannot be skipped, and cannot be told apart from a plain include.
 *
 *   AND IT CHANGES BEHAVIOUR, WHICH IS WHY IT IS ADOPTED COMMAND BY COMMAND: `asExceptions()` turns warnings into exceptions, so a command that used to live
 *   with a silent warning now stops dead. That is the intent, and it is discovered by RUNNING each command, never by editing them in a series.
 */

require_once dirname(__DIR__) . '/review-server/lib/Faults.php';
require_once __DIR__ . '/Tools.php';

/**
 * Wire a command's failures and hand back the repository root.
 *
 * `$argv` is taken so `-h|--help` is answered here as well: every command owes that answer, `check-tools.php` enforces it, and a command that boots has already
 * declared its usage block — the two go together.
 */
function bootCommand(?array $argv = null): string
{
    $faults = Faults::get();
    $faults->asExceptions();
    $faults->onConsole();
    if ($argv !== null) {
        // THE CALLER'S FILE IS WHAT CARRIES THE USAGE BLOCK, not this one: `debug_backtrace` names it, so no command has to pass its own path to be helped.
        $caller = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 1)[0]['file'] ?? __FILE__;
        Tools::get()->helpIfAsked($argv, $caller);
    }

    return dirname(__DIR__);
}

<?php
/**
 * Usage: start anything that runs in the review server — a served page or a build command — by wiring what it needs to fail properly and loading the shared services.
 *
 * Intention: THIS FILE DOES NOTHING BY BEING LOADED — it only defines functions (operator, 2026-08-07). Loading a file must never have effects of its own: a require that registers handlers behind
 * your back cannot be read, cannot be skipped, and cannot be told apart from a plain include. Here the call is the effect, and it is written where it happens.
 *
 * Why two functions and not one: a served page and a command fail differently and must fail differently. A page renders its fault as a readable page, since a blank browser error tells the reader
 * nothing. A command writes on the error output and fails, so the chain calling it stops instead of carrying on with a page that was never written. Everything else they need is the same, and that
 * sameness was being copied into six files before this one existed.
 */

// The services every page uses. The inventory and the thumbnail factory are NOT here: they take the repository root and are built by their caller, the only one that knows it.
require_once __DIR__ . '/lib/Faults.php';
require_once __DIR__ . '/lib/Notes.php';
require_once __DIR__ . '/lib/Favicon.php';
require_once __DIR__ . '/lib/Reload.php';
require_once __DIR__ . '/lib/Releve.php';
require_once __DIR__ . '/lib/Theme.php';

/**
 * For a command that produces a page: PHP errors become exceptions, and an uncaught exception stops the command with its message on the error output.
 *
 * The inventory and the thumbnail factory are NOT loaded here: they take the repository root and are built by their caller, which is the only one that knows it. A bootstrap wires what everyone
 * needs the same way; the rest stays where it is chosen.
 */
function bootBuild(): void
{
    $faults = Faults::get();
    $faults->asExceptions();
    $faults->onConsole();
}

/**
 * For a page served on the fly: PHP errors become exceptions, and an uncaught exception is rendered by the page itself.
 *
 * The closure belongs to the caller because only it knows what its fault page looks like — the index dresses its own, the router dresses another. What is shared is that neither ever lets the
 * browser show its blank error.
 */
function bootApp(callable $renderFault): void
{
    $faults = Faults::get();
    $faults->asExceptions();
    $faults->onPage($renderFault);
}

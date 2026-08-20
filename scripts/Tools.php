<?php
/**
 * USAGE
 *   require_once __DIR__ . '/Tools.php'; then Tools::get()->all(), ->usageOf($path), ->familyOf($name) — what the project's commands are, and what each says
 *   about itself. Used by scripts/tools.php, which lists them, and by scripts/check-tools.php, which refuses the ones that say nothing.
 *
 * INTENTION
 *   ONE PLACE KNOWS WHAT A COMMAND IS, and both the inventory and its checker ask it rather than each holding a copy. Two copies of « what counts as a command »
 *   would answer differently the day one of them learns about a new directory, and the checker would then guard a set the inventory does not show.
 *
 *   THE SET IS READ OFF THE DISK, NEVER LISTED BY HAND: a hand-kept list drifts at the first tool someone adds in a hurry, which is exactly what happened to the
 *   probe roster the tracking document used to hold — eight probes lived outside it while it promised tools that no longer ran.
 */

class Tools
{
    private static ?self $instance = null;

    /** The directories that hold the project's commands. `local/scripts/` is deliberately absent: it is the agent's throwaway, and nothing there is a command. */
    public const TREES = ['scripts', 'review-server'];
    /** What a command is, by its extension — a file the operator or an agent runs. */
    public const SUFFIXES = ['php', 'py', 'sh'];
    /** The trees a written path may name. Wider than TREES: the code cites its data and its documents too, and a dead one there is a dead one all the same. */
    public const PATH_TREES = ['scripts', 'review-server', 'assets', 'doc', 'local', 'var'];

    /** The families, in reading order: what controls, what builds, what produces, what runs by itself. */
    public const FAMILIES = [
        'check-' => 'LES CONTRÔLES — ils disent si une règle tient',
        'build-' => 'LES CONSTRUCTEURS — ils écrivent une page ou un document',
        'generate-' => 'LA PRODUCTION D\'IMAGES — chaque appel coûte une génération',
        'hook-' => 'LES HOOKS — ils s\'exécutent tout seuls, autour d\'un tour',
        'probe-' => 'LES SONDES — elles regardent une page servie au lieu de supposer',
    ];
    public const FAMILY_LOOK = 'LES REGARDS ET LES LECTEURS — ils consultent sans rien écrire';
    public const FAMILY_REST = 'LE RESTE — leur nom ne dit pas leur famille';
    private const LOOK_PREFIXES = ['see-', 'show-', 'list-', 'draw-', 'measure-'];

    private string $root;
    private ?array $fileNames = null;

    public function __construct(?string $root = null)
    {
        $this->root = $root ?? dirname(__DIR__);
    }

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * Whether a file is a library rather than a command — something other code calls, with nothing to answer on a command line.
     *
     * THE TEST IS THE FILE'S OWN SHAPE, NOT A LIST KEPT HERE: a list would be wrong the day someone adds a module and forgets to add it. Under `lib/`, by the
     * project's own convention; a PHP file whose name is a class name, capitalised; a Python file with no `__main__` guard, which is exactly how Python says
     * « this is imported, not run ».
     */
    public function isLibrary(string $path, string $name): bool
    {
        if (str_contains($path, '/lib/') || preg_match('/^[A-Z]/', $name) === 1) {
            return true;
        }
        if (str_ends_with($name, '.py')) {
            return !str_contains((string) file_get_contents($path), '__main__');
        }

        return false;
    }

    /** Every command of the project, its path relative to the root pointing at its base name. */
    public function all(): array
    {
        $found = [];
        foreach (self::TREES as $tree) {
            $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($this->root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
            foreach ($iterator as $file) {
                if (!$file->isFile() || !in_array($file->getExtension(), self::SUFFIXES, true)) {
                    continue;
                }
                if ($this->isLibrary($file->getPathname(), $file->getBasename())) {
                    continue;
                }
                $found[substr($file->getPathname(), strlen($this->root) + 1)] = $file->getBasename();
            }
        }
        ksort($found);

        return $found;
    }

    /**
     * The usage block of one file: the lines between « USAGE » and the next heading of the block, whatever the comment syntax.
     *
     * A COMMAND WITHOUT THIS BLOCK IS REPORTED, NEVER GUESSED AT. Inventing a description from the file name is how an inventory starts saying something other
     * than what the tools do, which is the very drift it exists to remove.
     *
     * A BLANK LINE DOES NOT END THE BLOCK, and that was a real loss: a usage that lists subcommands separates them from its opening sentence with one empty
     * comment line, so the block was cut at its first line and the help printed one line out of twelve. What ends it is what actually ends it — the INTENTION
     * heading, or the close of the comment the block lives in.
     */
    public function usageOf(string $path): ?array
    {
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        if ($lines === false) {
            return null;
        }
        $taken = [];
        $inside = false;
        $docstring = false;
        foreach (array_slice($lines, 0, 60) as $line) {
            $raw = trim($line);
            // A PYTHON DOCSTRING CARRIES NO MARKER ON ITS LINES, so the only way to know its lines are still comment is to remember that one opened. Tracked
            // before the block opens as well: the « USAGE » of a Python tool sits inside a docstring that started on the very first line of the file.
            if (!$docstring && preg_match('~^(?:[ru]?["\']{3})~i', $raw) === 1) {
                $docstring = true;
                $raw = substr($raw, strspn($raw, 'ruRU"\''));
            } elseif ($docstring && str_contains($raw, '"""') === false && str_contains($raw, "'''") === false) {
                // still inside it
            } elseif ($docstring) {
                $docstring = false;
                if ($inside) {
                    break;
                }
            }
            // THE DELIMITER IS NOT `#`, AND THAT IS NOT A DETAIL: `#` opens a shell comment, so it belongs INSIDE this pattern — used as the delimiter as well,
            // it closed the expression early and PHP warned on every line of every file, five hundred kilobytes of it in one call.
            $clean = trim(preg_replace('~^\s*(/\*\*?|\*/|\*|//|#|"""|\'\'\')\s?~', '', $line));
            if (preg_match('/^USAGE\b/i', $clean) === 1) {
                $inside = true;
                // « Usage: php scripts/x.php … » carries its line with it; « USAGE » alone opens the lines below.
                $rest = trim(preg_replace('/^USAGE\s*:?/i', '', $clean));
                if ($rest !== '') {
                    $taken[] = $rest;
                }
                continue;
            }
            if (!$inside) {
                continue;
            }
            if (preg_match('/^INTENTION\b/i', $clean) === 1 || $this->endsComment($raw, $docstring)) {
                break;
            }
            $taken[] = $clean;
        }
        // The blank comment line that separated the block from its INTENTION is kept by the walk above; it belongs to neither, and it is dropped here.
        while ($taken && end($taken) === '') {
            array_pop($taken);
        }

        return $taken ?: null;
    }

    /** Whether a raw line closes the comment the usage block lives in — the only thing, besides an INTENTION heading, that ends that block. */
    private function endsComment(string $raw, bool $docstring): bool
    {
        if ($docstring) {
            return false;
        }

        return str_contains($raw, '*/') || ($raw !== '' && preg_match('~^(\*|//|#|/\*)~', $raw) !== 1);
    }

    /**
     * Whether this file is really CALLED — a command — or only required by other code.
     *
     * ITS OWN USAGE DECIDES, and that is the honest test: a command's usage shows how to invoke it, `php …`, `python3 …`, `bash …`. A router, a bootstrap, a page
     * registry or a hook library says instead « require this file » or « never called by hand », and asking it for a `--help` it can never answer would be the
     * checker crying on what it announces it ignores — the failure that switches a checker off.
     */
    public function isCalled(?array $usage): bool
    {
        foreach ($usage ?? [] as $line) {
            if (preg_match('/^(php|python3|bash)\s+\S/', $line) === 1) {
                return true;
            }
        }

        return false;
    }

    /**
     * Whether a command answers the two flags everyone tries first.
     *
     * READ IN THE SOURCE, NEVER ASKED OF THE COMMAND: asking would mean running it, and some of them write to the referential or spend a generation. Finding the
     * two flags written somewhere in the file is crude, and it is wrong loudly rather than quietly — the way this repository asks a check to be wrong.
     */
    public function answersHelp(string $path): bool
    {
        $source = (string) file_get_contents($path);
        // A COMMAND THAT BOOTS HAS ALREADY ANSWERED: `bootCommand($argv)` wires the failures and hands the help question to this very service, so the two flags
        // no longer appear in the file itself. Without this, adopting the bootstrap made every command it touched look as though it had lost its help.
        if (preg_match('~bootCommand\(\s*\$argv~', $source)) {
            return true;
        }

        return str_contains($source, '--help') && str_contains($source, '-h');
    }

    /**
     * Prints the caller's own usage block and stops, when the command line asks for it. Called at the top of every PHP command: `Tools::get()->helpIfAsked($argv, __FILE__)`.
     *
     * THE HELP IS THE USAGE BLOCK ITSELF, NEVER A SECOND COPY OF IT. A help text written beside the block is a duplicate, and it drifts at the first option
     * added — the block stays right because the file is read to change it, the copy stays wrong because nobody looks at it. Here the two cannot differ: there
     * is only one text, and this reads it off the file that is running.
     *
     * The two flags stay spelled out in each caller's usage block, which is what makes them discoverable without running anything — and what the checker reads.
     */
    public function helpIfAsked(array $argv, string $file): void
    {
        if (!in_array('-h', $argv, true) && !in_array('--help', $argv, true)) {
            return;
        }
        $usage = $this->usageOf($file);
        if ($usage === null) {
            throw new RuntimeException(basename($file) . " n'a pas de bloc d'usage à montrer — « php scripts/check-tools.php -v » le dit déjà.");
        }
        echo implode("\n", $usage), "\n";
        exit(0);
    }

    /** Where a command belongs, read off its name. */
    public function familyOf(string $name): string
    {
        foreach (self::FAMILIES as $prefix => $title) {
            if (str_starts_with($name, $prefix)) {
                return $title;
            }
        }
        foreach (self::LOOK_PREFIXES as $prefix) {
            if (str_starts_with($name, $prefix)) {
                return self::FAMILY_LOOK;
            }
        }

        return self::FAMILY_REST;
    }

    /**
     * Every file name the project's own trees carry, whatever its depth — the index a bare name is looked up in.
     *
     * Built once and kept, because it is asked a question per candidate and per file; walking the trees again each time would turn a check into a chore nobody
     * runs.
     */
    private function fileNames(): array
    {
        if ($this->fileNames === null) {
            $this->fileNames = [];
            foreach (self::TREES as $tree) {
                $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($this->root . '/' . $tree, FilesystemIterator::SKIP_DOTS));
                foreach ($iterator as $file) {
                    if ($file->isFile()) {
                        $this->fileNames[$file->getBasename()] = true;
                    }
                }
            }
        }

        return $this->fileNames;
    }

    /**
     * The paths a whole FILE names — header and code alike — and which of them lead nowhere. Each find is `[line number, path]`.
     *
     * IT READS THE CODE AND NOT ONLY THE USAGE BLOCK, and that is the whole reason it was widened (opérateur, 2026-08-12). A dead path in a help misleads a
     * reader; a dead path in an executed line CRASHES, and nothing says so until someone runs it. `scripts/sprite-queue.py` called two generators that had been
     * merged away days earlier — its header described the dead chain, its code called it, and the check looked at neither because both sat outside the usage.
     *
     * ONLY PATHS WRITTEN IN FULL ARE JUDGED, NEVER ONE THE CODE ASSEMBLES. A path built from a variable or a concatenation is not knowable without running the
     * program, so reporting it would be guessing — and a check that guesses gets switched off. Two forms are therefore read, and no others: a path under one of
     * the project's own trees, a leading slash allowed so that `"$root/scripts/Capture.php"` is still judged on the half that is written down; and a BARE FILE
     * NAME, which is how a real path gets assembled — `REPO / "scripts" / "generate-sprite-subject.py"` writes its directories apart from its file. A bare name
     * is looked up by name alone, anywhere in the trees, so moving a file never makes it a find.
     *
     * A BARE NAME COUNTS ONLY WHEN IT ENDS IN CODE — `.php`, `.py`, `.sh`. The other suffixes name what a command is GIVEN rather than what it calls, and every
     * usage block is full of them: `<requests.json>`, `<plan.json>`, `<image.png>` are arguments the operator supplies, and none of them is a file of this
     * repository. Judged like the rest, they would make every command look broken, which is the fastest way to make a check worthless.
     */
    public function deadPaths(string $path): array
    {
        $dead = [];
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        if ($lines === false) {
            throw new RuntimeException("{$path} ne se lit pas — le contrôle ne peut pas conclure sur ses chemins.");
        }
        foreach ($lines as $index => $line) {
            // A PATH IS RECOGNISED BY THE TREE IT STARTS FROM, WHEREVER THAT TREE BEGINS ON THE LINE. Reading the candidate from the first character that could
            // belong to a path made `"$root/scripts/absente.php"` come out as `root/scripts/absente.php`, which starts from no tree of this project and was
            // dropped in silence — the concatenation the widening was meant to handle. The match now starts AT the tree, and only refuses to be preceded by
            // something a name is made of, so a leading slash or a variable before it changes nothing while `myscripts/x.py` is still not `scripts/x.py`.
            //
            // THE SUFFIX MUST END THE WORD, and forgetting that turned every Python attribute into a shell script: `self.shape` read as `self.sh`,
            // `asset_common.sheet_description` as `asset_common.sh` — nine of the first twenty finds, all method calls. `.jsonl` fell the same way.
            $suffixes = 'php|py|sh|json|md|png';
            preg_match_all('~(?<![A-Za-z0-9_.-])((?:' . implode('|', self::PATH_TREES) . ")/[A-Za-z0-9_./-]+\.(?:{$suffixes}))(?![A-Za-z0-9_])~", $line, $written);
            foreach ($written[1] as $candidate) {
                // `var/tmp/` HOLDS WHAT A PROGRAM WRITES AND THROWS AWAY, so a file named there is expected to be absent between two runs — a trial's payload,
                // a probe's output. Judging it would make the check red for doing exactly what the repository asks of that directory.
                if (str_starts_with($candidate, 'var/tmp/') || is_file($this->root . '/' . $candidate)) {
                    continue;
                }
                $dead[$candidate] = [$index + 1, $candidate];
            }
            // A BARE NAME, which is how a real path gets assembled one piece at a time. Never preceded by a slash: what follows one belongs to a path, and that
            // path was already judged above, or deliberately left alone for being built from something this cannot read.
            preg_match_all('~(?<![A-Za-z0-9_./-])([A-Za-z0-9_-]+\.(?:php|py|sh))(?![A-Za-z0-9_])~', $line, $bare);
            foreach ($bare[1] as $candidate) {
                if (!isset($this->fileNames()[$candidate])) {
                    $dead[$candidate] = [$index + 1, $candidate];
                }
            }
        }

        return array_values($dead);
    }
}

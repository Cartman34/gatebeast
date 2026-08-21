<?php
/**
 * USAGE
 *   Every path of the workshop's consignes, computed HERE and nowhere else. `Prompts::get()->home()` is the directory that holds one folder per subject,
 *   `->homeOf('BT-001')` that subject's folder, `->file('BT-001', 3, 'image')` the path of one file of one version, and `->beside($promptPath, 'critiques')`
 *   the file that sits next to a version whose path one already holds. `->partsOf($path)` reads a name back into its subject, rank and what.
 *
 * INTENTION
 *   ONE FOYER, DECLARED IN ONE PLACE. The consignes moved under `var/` on 2026-08-17 and three readers kept their own copy of the old path: the workshop page
 *   read the new one while `apply-source.php` refused every subject as having no foyer, `extract-transmitted.php` wrote beside a directory that no longer
 *   existed, and `Critiques.php` found no critique file and reported none — a page saying « aucune critique » over a file sitting on disk. A path copied into
 *   four readers is four truths, and the first migration shows which of them nobody updated.
 *
 *   AND THE NAME IS A TABLE, NEVER A SUBSTITUTION (operator, 2026-08-17: « pas de bricolage pour déduire le chemin »). Every reader used to rebuild the name by
 *   hand — a string concatenation here, a `substr` on a suffix there, a regular expression stripping `.prompt` somewhere else. Each one is a private copy of the
 *   convention, and each drifts on its own: swapping an extension turns `…prompt.txt` into `…prompt.png`, which names nothing. The convention is `PARTS` below,
 *   and the only way to a path is a method of this class.
 *
 *   UNDER `var/`, DELIBERATELY (operator, 2026-08-17). These are trials: one version's image weighs three megabytes, more than all the code of this repository
 *   put together. What must survive a trial is not its text but what it taught, and that is reported to the source blocks and to the code.
 *
 *   A FILE NAME SAYS WHOSE IT IS AND WHAT IT IS: `<SUBJECT>.v<N>.<what>.<ext>`. Torn from its directory, `v3.png` says nothing, and an extension alone does not
 *   tell the generated image from a probe shot. The « what » is English like every file name here.
 */

class Prompts
{
    /** Where the workshop keeps its consignes: one directory per subject, and inside it every version with its own files. Relative to the repository root. */
    public const HOME = 'var/generations/prompts';

    /**
     * What a version can carry, and the extension each one wears. THE LIST IS CLOSED: a « what » absent from it is refused by name rather than composed anyway,
     * because a path built from an unknown word points at a file that will never exist and says nothing about why.
     */
    public const PARTS = [
        'prompt' => 'txt',
        'image' => 'png',
        'edits' => 'json',
        'generation' => 'json',
        'transmitted' => 'txt',
        'critiques' => 'json',
        'parts' => 'json',
    ];

    private static ?self $instance = null;

    private string $root;

    private string $home;

    /** `$home` is what a probe hands over: it builds from a fixture folder rather than from the consignes of the machine it runs on. */
    public function __construct(?string $root = null, ?string $home = null)
    {
        $this->root = $root ?? dirname(__DIR__, 2);
        $this->home = $home ?? $this->root . '/' . self::HOME;
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** Where this instance reads its consignes from — said out loud because the page prints it, and because a probe builds from another folder. */
    public function home(): string
    {
        return $this->home;
    }

    /** One subject's folder. Its existence is NOT asserted here: each caller says what an absent foyer means for it, and none of them mean the same thing. */
    public function homeOf(string $subject): string
    {
        return $this->home . '/' . $subject;
    }

    /** The subjects that have a folder, in name order. An empty list is an answer, not a fault: no consigne has been opened yet. */
    public function subjects(): array
    {
        if (!is_dir($this->home)) {
            return [];
        }
        $found = [];
        foreach (scandir($this->home) as $entry) {
            if ($entry === '.' || $entry === '..' || !is_dir($this->home . '/' . $entry)) {
                continue;
            }
            $found[] = $entry;
        }
        sort($found);

        return $found;
    }

    /** The stem every file of one version shares — `<SUBJECT>.v<N>`, with its folder. Nothing outside this class rebuilds it. */
    public function stem(string $subject, int $rank): string
    {
        return $this->homeOf($subject) . '/' . $subject . '.v' . $rank;
    }

    /**
     * The path of one file of one version, whether it exists or not — the name is the contract, and the caller looks at the disk.
     *
     * AN UNKNOWN « WHAT » RAISES, it is never composed. A typo would otherwise give a path that simply never matches a file, and the caller would report the
     * version as carrying no image while the image lies right there under its real name.
     */
    public function file(string $subject, int $rank, string $what): string
    {
        if (!isset(self::PARTS[$what])) {
            throw new InvalidArgumentException(sprintf('FAULT « %s » n\'est pas une pièce de version : les pièces connues sont %s.',
                $what, implode(', ', array_keys(self::PARTS))));
        }

        return $this->stem($subject, $rank) . '.' . $what . '.' . self::PARTS[$what];
    }

    /**
     * What a path names: its `subject`, its `rank` and its `what` — or null when the name does not follow the convention.
     *
     * READING THE NAME IS THE ONLY WAY BACK. A caller holding a consigne's path and wanting the critiques beside it used to strip a suffix with a regular
     * expression, which is the convention written a second time, in a dialect, in a file that has no business knowing it.
     */
    public function partsOf(string $path): ?array
    {
        $name = basename($path);
        foreach (self::PARTS as $what => $extension) {
            $suffix = '.' . $what . '.' . $extension;
            if (!str_ends_with($name, $suffix)) {
                continue;
            }
            if (!preg_match('/^(.+)\.v(\d+)$/', substr($name, 0, -strlen($suffix)), $found)) {
                return null;
            }

            return ['subject' => $found[1], 'rank' => (int) $found[2], 'what' => $what];
        }

        return null;
    }

    /**
     * The file of the SAME version that carries `$what`, given the path of any other file of it.
     *
     * It raises on a path that does not name a version, because every caller of this method holds a path it just read from this foyer: one that does not parse
     * means the convention was broken upstream, and silently returning null would turn that into « this version has no critiques ».
     */
    public function beside(string $path, string $what): string
    {
        $parts = $this->partsOf($path);
        if ($parts === null) {
            throw new InvalidArgumentException(sprintf('FAULT « %s » ne nomme pas une version : le moule est <SUJET>.v<N>.<quoi>.<ext>.', basename($path)));
        }

        return $this->file($parts['subject'], $parts['rank'], $what);
    }

    /**
     * The edits one version applied, each with its reason and its test state — or the reason the journal cannot be read.
     *
     * Returns `['edits' => array, 'note' => string|null, 'fault' => string|null]`. An absent journal is not a fault: the first version of a chain derives from
     * nothing. A journal that does not parse IS one, and it is named rather than swallowed — a version whose corrections cannot be listed is a version nobody
     * can decide to report into the code.
     */
    public function editsOf(string $subject, int $rank): array
    {
        $path = $this->file($subject, $rank, 'edits');
        if (!is_file($path)) {
            return ['edits' => [], 'note' => null, 'fault' => null];
        }
        try {
            $journal = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $badly) {
            return ['edits' => [], 'note' => null, 'fault' => '« ' . basename($path) . ' » n\'est pas lisible comme du JSON : ' . $badly->getMessage()
                . '. Solution — rouvrir le fichier et le refermer ; les corrections d\'une version ne se devinent pas.'];
        }

        return ['edits' => $journal['edits'] ?? [], 'note' => $journal['note'] ?? null, 'fault' => null];
    }

    /** The versions of one subject, by rank, from 1 up to the first missing prompt — a chain has no holes, and a hole is the end of it. */
    public function ranksOf(string $subject): array
    {
        $ranks = [];
        for ($rank = 1; is_file($this->file($subject, $rank, 'prompt')); $rank++) {
            $ranks[] = $rank;
        }

        return $ranks;
    }

    /** The highest rank that carries an image, or 0 when none was ever generated. A version without an image was written and never tested. */
    public function generatedRank(string $subject): int
    {
        $generated = 0;
        foreach ($this->ranksOf($subject) as $rank) {
            if (is_file($this->file($subject, $rank, 'image'))) {
                $generated = $rank;
            }
        }

        return $generated;
    }

    /**
     * The rank of the ONE pending version: the one that follows the last generated.
     *
     * MODIFYING A VERSION IS NOT CREATING ONE (operator, 2026-08-17: « le diff d'une version peut être modifié tant que la version suivante n'est pas générée »).
     * As long as it carries no image, every correction rewrites it in place and the diff one reads stays that of a single version. Stacking a version per
     * correction — done three times in a row — gives a chain no link of which was ever tested, and a diff that relates to nothing.
     */
    public function pendingRank(string $subject): int
    {
        return $this->generatedRank($subject) + 1;
    }
}

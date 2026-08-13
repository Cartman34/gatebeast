<?php
/**
 * USAGE
 *   Read the generation trials — one folder each under `var/generations/trials/` — and hand back what each one holds: its image, the consigne we sent, the split
 *   of that consigne, the consigne the agent says it transmitted, its facts, and the critiques written on it. `Trials::get()->all()`, or `->one($id)`.
 *
 * INTENTION
 *   A TRIAL IS NOT A DELIVERABLE. It records itself in no referential, appears on no sprites page, and consumes no version of a subject: it exists to be looked
 *   at once, beside the image it produced, and thrown away. That is why it lives under `var/` — l'application y écrit ce qu'elle produit en tournant — and why
 *   nothing here is versioned: a trial can vanish between two builds, which is the ordinary case and not an accident.
 *
 *   NOTHING IS RECOMPUTED, EVER. The split, the fingerprint, the delivered measures and the generator session are written by the chain; deriving any of them a
 *   second time here would make a second version that drifts. What is not on disk is reported ABSENT, by name, with where it should have come from — never
 *   replaced by a plausible value. An incomplete trial is the rule: the agent may not report what it transmitted, and an older consigne carries no split at all.
 */

require_once __DIR__ . '/PromptParts.php';

class Trials
{
    private static ?self $instance = null;

    /** Where the chain writes its trials. Under `var/`, which the review server already serves, and which is never versioned. */
    public const HOME = 'var/generations/trials';

    /** The facts of a trial, written by the chain beside its image. English, like every data file of this repository. */
    public const FACTS_FILE = 'trial.json';

    /** The critiques written on a trial, filed inside the trial's own folder — they are working matter and disappear with it, deliberately. */
    public const CRITIQUES_FILE = 'critiques.json';

    /** The facts a trial is expected to declare, and what each one is for. A key that is missing is NAMED on the page rather than filled in. */
    public const FACTS_EXPECTED = [
        'subject' => 'le code du sujet, par exemple TR-063',
        'variant' => 'la ref du variant',
        'produced_at' => 'la date de la génération, en ISO 8601',
        'session' => 'l\'identifiant de session du générateur',
        'delivered_px' => 'les mesures de l\'image livrée, « width » et « height »',
    ];

    private string $root;

    private string $home;

    /** `$home` is what a probe hands over: it builds the page from a fixture folder rather than from the trials of the machine it runs on. */
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

    /** Where this instance reads its trials from — said out loud because the page prints it, and because a probe builds from another folder. */
    public function home(): string
    {
        return $this->home;
    }

    /** Every trial on disk, the most recent first. An empty list is an answer, not a fault: no trial has been run yet. */
    public function all(): array
    {
        if (!is_dir($this->home)) {
            return [];
        }
        $trials = [];
        foreach (scandir($this->home) as $name) {
            if ($name === '.' || $name === '..' || !is_dir($this->home . '/' . $name)) {
                continue;
            }
            $trials[] = $this->one($name);
        }
        // The folder name opens with the date, so their names sort exactly as their dates do — and the sort is on the name because that is what the page shows.
        usort($trials, static fn (array $left, array $right): int => strcmp($right['id'], $left['id']));

        return $trials;
    }

    /**
     * One trial, read whole: what it holds, and NAMED for each thing it does not.
     *
     * The four files are recognised by the suffixes the chain already writes beside a produced image — nothing invented here: `.png` the image, `.txt` the
     * consigne, `.parts.json` its split, `.transmitted.txt` what the agent passed on.
     */
    public function one(string $id): array
    {
        $folder = $this->home . '/' . $id;
        $missing = [];
        $image = $this->firstEnding($folder, '.png');
        if ($image === null) {
            $missing[] = 'aucune image dans le dossier : la génération n\'est pas allée jusqu\'au bout, ou son fichier a été retiré.';
        }
        // THE CONSIGNE IS THE `.txt` THAT IS NOT THE TRANSMITTED ONE. Both end in `.txt`, and taking the first would show the agent's rewriting as if it were
        // ours — the one confusion this whole page exists to lift.
        $prompt = $this->firstEnding($folder, '.txt', '.transmitted.txt');
        if ($prompt === null) {
            $missing[] = 'aucune consigne : « <nom>.txt » est absent, alors que la chaîne la fige à côté de l\'image.';
        }
        $transmitted = $this->firstEnding($folder, '.transmitted.txt');
        if ($transmitted === null) {
            $missing[] = 'aucune consigne transmise : l\'agent n\'a pas rapporté ce qu\'il a passé à son modèle d\'images, donc la chaîne n\'a rien écrit —'
                . ' un fichier vide aurait dit « il n\'a rien transmis », ce qui est autre chose.';
        }
        $split = $prompt === null ? ['body' => null, 'parts' => [], 'fault' => null] : PromptParts::get()->read($prompt);

        return [
            'id' => $id,
            'folder' => $folder,
            'image' => $image,
            'prompt' => $prompt,
            'body' => $split['body'],
            'parts' => $split['parts'],
            'partsFault' => $split['fault'],
            'transmitted' => $transmitted === null ? null : file_get_contents($transmitted),
            'facts' => $this->factsOf($folder),
            'critiques' => $this->critiques($id),
            'missing' => $missing,
        ];
    }

    /**
     * The facts a trial declares, and the list of those it does not.
     *
     * NONE OF THEM IS DEDUCED FROM THE FOLDER. The session lives in the production report, the measures in the referential, and a trial is written into neither:
     * rebuilding them here would be the second version the point forbids — right until the day it silently disagrees with the chain.
     */
    public function factsOf(string $folder): array
    {
        $path = $folder . '/' . self::FACTS_FILE;
        if (!is_file($path)) {
            return ['held' => null, 'missing' => array_keys(self::FACTS_EXPECTED),
                'fault' => 'l\'essai ne déclare pas ses faits : « ' . self::FACTS_FILE . ' » est absent du dossier. Solution — c\'est la chaîne qui l\'écrit,'
                    . ' au moment de la génération ; un essai antérieur à ce fichier n\'en a pas, et rien ne le reconstitue après coup.'];
        }
        try {
            $held = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $badly) {
            return ['held' => null, 'missing' => array_keys(self::FACTS_EXPECTED),
                'fault' => '« ' . self::FACTS_FILE . ' » n\'est pas lisible comme du JSON : ' . $badly->getMessage() . '.'];
        }
        $missing = [];
        foreach (self::FACTS_EXPECTED as $key => $what) {
            if (!isset($held[$key]) || $held[$key] === '' || $held[$key] === []) {
                $missing[] = $key;
            }
        }

        return ['held' => $held, 'missing' => $missing, 'fault' => null];
    }

    /** The critiques written on a trial, keyed by the anchor they hang on. An absent file means none written yet, which is not a fault. */
    public function critiques(string $id): array
    {
        $path = $this->home . '/' . $id . '/' . self::CRITIQUES_FILE;
        if (!is_file($path)) {
            return ['held' => [], 'fault' => null];
        }
        try {
            $held = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $badly) {
            // A critique file that cannot be read is REPORTED, not swallowed: silence here would show a trial as never criticised while its remarks sit on disk.
            return ['held' => [], 'fault' => '« ' . self::CRITIQUES_FILE . ' » est illisible : ' . $badly->getMessage()
                . ' Solution — le fichier est du JSON écrit par le serveur ; s\'il a été modifié à la main, revenir à sa forme « ancre : critique ».'];
        }

        return ['held' => is_array($held) ? $held : [], 'fault' => null];
    }

    /**
     * Whether that name is a trial of this folder — asked before anything is ever written into it.
     *
     * A NAME THAT COMES FROM A REQUEST IS NEVER PASTED INTO A PATH. Compared against the folders that actually exist, a « ../ » matches nothing and the write is
     * refused; built by concatenation, it would write wherever it liked. This is a writing door, and it is treated as one even on a local server.
     */
    public function exists(string $id): bool
    {
        foreach ($this->all() as $trial) {
            if ($trial['id'] === $id) {
                return true;
            }
        }

        return false;
    }

    /** The first file of that folder ending in `$suffix`, skipping the ones ending in `$except`, or null when there is none. */
    private function firstEnding(string $folder, string $suffix, ?string $except = null): ?string
    {
        if (!is_dir($folder)) {
            return null;
        }
        $found = [];
        foreach (scandir($folder) as $name) {
            if (str_ends_with($name, $suffix) && ($except === null || !str_ends_with($name, $except))) {
                $found[] = $folder . '/' . $name;
            }
        }
        sort($found);

        return $found[0] ?? null;
    }
}

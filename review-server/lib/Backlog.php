<?php
/**
 * USAGE
 *   Read and write the open points of the project — what is left to do, in priority order. Used by the command that edits them and by the page that shows them.
 *
 * INTENTION
 *   The pile lived in SUIVI.md, a document written for people: a point could only be found by reading prose, its state was a word in a table cell, and nothing could sort it or count it. It is now
 *   data, in one file, and the document keeps what it is good at — the reasoning, the constats, the decisions and why they were taken.
 *
 *   THE WORD "SUJET" IS THE OPERATOR'S, AND IT COLLIDES WITH THE GAME'S OWN VOCABULARY: a sujet in assets/sujets.json is a creature or a piece of scenery. These two never meet, because this one
 *   lives under review-server/ and is only ever reached through this class — but the collision is real and is the reason the file is not called assets/sujets.json's neighbour.
 *
 *   ONLY THE AGENT WRITES HERE, through the command: a point edited by hand in two places diverges, which is exactly what the SUIVI table did against the artefact registry before it was moved out.
 */

class Backlog
{
    private static ?self $instance = null;

    /**
     * The statuses, from most open to most closed. The order matters: it is the one the page and the command sort by.
     *
     * IN ENGLISH, LIKE EVERY STORED VALUE THAT IS NOT FREE TEXT (opérateur, 2026-08-07). A status is a token the code compares, not a sentence a human reads — it belongs to the same family as the
     * keys around it, which the project already requires in English. Only the label and the description are free text, and those stay French. The French wording lives in STATUS_LABELS, at display
     * time and nowhere else.
     */
    /**
     * UN STATUT S'ÉCRIT UNE FOIS, ICI, ET SE CITE PAR SA CONSTANTE (opérateur, 2026-08-08). A literal repeated across the code cannot be renamed, cannot be found, and a typo in one of its copies is
     * a silent no-match rather than an error — which is exactly how a guard came to test a ref that no longer existed.
     */
    public const STATUS_TODO = 'todo';
    public const STATUS_IN_PROGRESS = 'in-progress';
    public const STATUS_PENDING_DEPENDENCY = 'pending-dependency';
    public const STATUS_PENDING_DECISION = 'pending-decision';
    public const STATUS_WAITING_EXTERNAL = 'waiting-external';
    public const STATUS_DONE = 'done';
    public const STATUS_DISMISSED = 'dismissed';

    /** Qui doit bouger pour qu'un point avance : l'agent, ou l'opérateur. */
    public const WAITING_AGENT = 'agent';
    public const WAITING_OPERATOR = 'operator';

    /** La série des questions. Un point qui attend une décision de l'opérateur en fait partie, et son code commence par cette lettre. */
    public const SERIES_QUESTION = 'Q';

    public const STATUSES = [
        self::STATUS_TODO, self::STATUS_IN_PROGRESS, self::STATUS_PENDING_DEPENDENCY,
        self::STATUS_PENDING_DECISION, self::STATUS_WAITING_EXTERNAL, self::STATUS_DONE, self::STATUS_DISMISSED,
    ];

    /** Ce qu'un statut veut dire, en une phrase — la page l'affiche, pour que personne n'ait à deviner la nuance entre « fait » et « classé ». Le seul endroit où un statut se dit en français. */
    public const STATUS_LABELS = [
        self::STATUS_TODO => "À faire — dû, personne n'y travaille",
        self::STATUS_IN_PROGRESS => 'En cours — engagé maintenant',
        self::STATUS_PENDING_DEPENDENCY => 'En attente — un autre point de la pile doit passer avant',
        self::STATUS_PENDING_DECISION => "À trancher — attend une décision de l'opérateur",
        self::STATUS_WAITING_EXTERNAL => 'En attente — quelque chose hors du projet, que personne ici ne peut faire avancer',
        self::STATUS_DONE => 'Fait — le travail est allé au bout',
        self::STATUS_DISMISSED => 'Classé — abandonné ou sans objet, et on dit pourquoi',
    ];

    /**
     * THE THREE WAITING STATUSES, AND WHAT EACH ONE OWES (opérateur, 2026-08-08). A single "blocked" covered three situations at once — waiting on another task, waiting on the operator, waiting on
     * something outside the project — so nothing could tell a point that needed an answer from a point that only needed its turn. Two points sat "blocked" by nothing at all, and the operator was
     * asked to arbitrate a question that did not exist. Each of these statuses must name what it waits on: an unnamed wait is exactly the state that produced the false questions.
     */
    public const WAITING_STATUSES = [self::STATUS_PENDING_DEPENDENCY, self::STATUS_PENDING_DECISION, self::STATUS_WAITING_EXTERNAL];

    /** Les statuts qui restent du travail. Le reste est de l'histoire, et la page les sépare. */
    public const OPEN_STATUSES = [
        self::STATUS_TODO, self::STATUS_IN_PROGRESS, self::STATUS_PENDING_DEPENDENCY, self::STATUS_PENDING_DECISION, self::STATUS_WAITING_EXTERNAL,
    ];

    private string $path;

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    public function __construct(?string $root = null)
    {
        $this->path = ($root ?? dirname(__DIR__, 2)) . '/review-server/tasks.json';
    }

    /** Tous les points, tels qu'ils sont écrits. */
    public function all(): array
    {
        if (!is_file($this->path)) {
            return [];
        }
        $data = json_decode(file_get_contents($this->path), true, 512, JSON_THROW_ON_ERROR);

        return $data['tasks'] ?? [];
    }

    /**
     * Les points dans l'ordre où ils se dépilent : ce qui est engagé d'abord, puis les autres ouverts par priorité croissante, et à priorité égale le plus ancien passe devant.
     *
     * WHAT IS ALREADY UNDER WAY COMES FIRST, WHATEVER ITS PRIORITY (operator, 2026-08-08). An engaged point holds context nobody else has — half a page rewritten, a decision half applied — and that
     * context is what a stop throws away. Starting a higher-priority point on top of it does not gain a day, it loses the one already spent. A point that cannot move because it waits on another is
     * not engaged: it goes back to todo, or to pending-dependency with the point it waits on named.
     *
     * LA PRIORITÉ EST UN NOMBRE, PAS UN RANG : deux points peuvent la partager, et intercaler un point n'oblige à renuméroter personne. Un rang unique se renumérote à chaque insertion, et c'est
     * ainsi qu'un ordre finit par ne plus vouloir rien dire.
     */
    public function ordered(bool $openOnly = false): array
    {
        $points = $this->all();
        if ($openOnly) {
            $points = array_filter($points, fn (array $p) => in_array($p['status'], self::OPEN_STATUSES, true));
        }
        usort($points, function (array $a, array $b): int {
            $openA = in_array($a['status'], self::OPEN_STATUSES, true);
            $openB = in_array($b['status'], self::OPEN_STATUSES, true);
            if ($openA !== $openB) {
                return $openA ? -1 : 1;
            }
            $engagedA = $a['status'] === self::STATUS_IN_PROGRESS;
            $engagedB = $b['status'] === self::STATUS_IN_PROGRESS;
            if ($engagedA !== $engagedB) {
                return $engagedA ? -1 : 1;
            }

            return [$a['priority'], $a['created']] <=> [$b['priority'], $b['created']];
        });

        return $points;
    }

    /** Une tâche se retrouve par sa ref — le slug — ou par son code interne : tout ce qui est déjà écrit dans le projet cite le second, et le premier est celui qui se lit. */
    public function find(string $ref): ?array
    {
        foreach ($this->all() as $point) {
            if (strcasecmp($point['ref'], $ref) === 0 || strcasecmp($point['code'] ?? '', $ref) === 0) {
                return $point;
            }
        }

        return null;
    }

    /** Écrit un point, neuf ou repris. Le fichier est réécrit en entier : il tient dans un souffle, et une écriture partielle est une occasion de le corompre. */
    public function save(array $point): void
    {
        $points = $this->all();
        $found = false;
        foreach ($points as $index => $existing) {
            if (strcasecmp($existing['ref'], $point['ref']) === 0) {
                $points[$index] = $point;
                $found = true;
                break;
            }
        }
        if (!$found) {
            $points[] = $point;
        }
        $this->write($points);
    }

    private function write(array $points): void
    {
        $data = [
            'format' => 'gatebeast-tasks',
            'version' => 1,
            '_intention' => "Les tâches du projet — ce qui reste à faire, dans l'ordre des priorités. Seule la commande scripts/backlog.php écrit ici ; la page les lit. "
                . "Le mot « sujet » est réservé aux créatures et aux décors du jeu, et ne désigne jamais une tâche.",
            'tasks' => array_values($points),
        ];
        file_put_contents($this->path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
    }

    /** La prochaine référence libre d'une série — `S`, `Q`, `P`, `T`, `W`. La numérotation est continue tant qu'un point de la série reste ouvert, et repart à 1 quand la série se vide. */
    public function nextRef(string $series): string
    {
        $series = strtoupper($series);
        $used = [];
        $open = false;
        // THE SERIES NUMBER LIVES IN THE CODE, NEVER IN THE REF (2026-08-08): refs became twenty-character slugs, so matching them against "letters + digits" matched nothing at all and every new
        // point was numbered 1. The first add since the slug migration produced a second "Q1" — the field that carries the counter is the one that must be read.
        foreach ($this->all() as $point) {
            if (preg_match('/^([A-Z]+)(\d+)$/', $point['code'] ?? '', $found) && $found[1] === $series) {
                $used[] = (int) $found[2];
                $open = $open || in_array($point['status'], self::OPEN_STATUSES, true);
            }
        }

        return $series . ($open && $used ? max($used) + 1 : 1);
    }

    /**
     * The slug a point is read by, derived from its label when the author does not give one.
     *
     * A SLUG NEVER ENDS ON A DASH, AND IT IS NOT PADDED (opérateur, 2026-08-08). Refs used to be padded to a fixed width so the listing would line up, which wrote "maison-de-ferme-----": five
     * characters of nothing that a reader takes for a truncation. Alignment belongs to the listing, which pads its own columns; it has no business inside the value. The twenty characters remain a
     * ceiling, and the cut falls on a word boundary rather than mid-word.
     *
     * DERIVING IT IS THE FALLBACK, NOT THE RULE: a label cut at twenty characters rarely names the point well, so the author is expected to pass the ref. This only keeps a bad label from producing
     * an unusable ref.
     */
    public function slugFor(string $label, string $code): string
    {
        // ACCENTS ARE FOLDED, NEVER DROPPED: without this, "Écrire à la méthode" opens on a dash and reads as a stub. Every ref written by the slug migration folds them, and a ref is a name one
        // recognizes at a glance — a leading dash costs that recognition on exactly the words French starts its sentences with.
        $folded = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $label);
        $base = trim(preg_replace('/[^a-z0-9]+/', '-', strtolower($folded)), '-');
        $slug = self::trimSlug($base, 20);
        if ($this->find($slug) !== null) {
            $slug = self::trimSlug($base, 20 - strlen($code) - 1) . '-' . strtolower($code);
        }

        return $slug;
    }

    /** Cuts a slug to its maximum length, leaving neither a dash at either end nor a half word: one word less beats one word cut. */
    public static function trimSlug(string $slug, int $length): string
    {
        if (strlen($slug) <= $length) {
            return trim($slug, '-');
        }
        $cut = substr($slug, 0, $length);
        $lastWord = strrpos($cut, '-');

        return trim($lastWord !== false && $lastWord > 0 ? substr($cut, 0, $lastWord) : $cut, '-');
    }
}

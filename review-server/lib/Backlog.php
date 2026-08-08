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
    public const STATUSES = ['todo', 'in-progress', 'blocked', 'pending-decision', 'done', 'dismissed'];

    /** Ce qu'un statut veut dire, en une phrase — la page l'affiche, pour que personne n'ait à deviner la nuance entre « fait » et « classé ». Le seul endroit où un statut se dit en français. */
    public const STATUS_LABELS = [
        'todo' => "À faire — dû, personne n'y travaille",
        'in-progress' => 'En cours — engagé maintenant',
        'blocked' => "Bloqué — attend quelque chose d'extérieur",
        'pending-decision' => "À trancher — attend une décision de l'opérateur",
        'done' => 'Fait — le travail est allé au bout',
        'dismissed' => 'Classé — abandonné ou sans objet, et on dit pourquoi',
    ];

    /** Les statuts qui restent du travail. Le reste est de l'histoire, et la page les sépare. */
    public const OPEN_STATUSES = ['todo', 'in-progress', 'blocked', 'pending-decision'];

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
     * Les points dans l'ordre où ils se dépilent : les ouverts d'abord, par priorité croissante, et à priorité égale le plus ancien passe devant.
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
        // THE SERIES NUMBER LIVES IN THE CODE, NEVER IN THE REF (2026-08-08): refs became twenty-character slugs, so matching them against "letter+digits" matched nothing at all and every new point
        // was numbered 1. The first add since the slug migration produced a second "Q1", colliding with the existing one — the field that carries the counter is the one that must be read.
        foreach ($this->all() as $point) {
            if (preg_match('/^([A-Z]+)(\d+)$/', $point['code'] ?? '', $found) && $found[1] === $series) {
                $used[] = (int) $found[2];
                $open = $open || in_array($point['status'], self::OPEN_STATUSES, true);
            }
        }

        return $series . ($open && $used ? max($used) + 1 : 1);
    }

    /**
     * The twenty-character slug a point is read by, derived from its label. Anything that is not a letter or a digit becomes a dash, and a short label is padded to the full width so every ref lines
     * up in the listing. A slug already taken gets the point's code appended, which is what the slug migration did and what keeps two similar labels apart.
     */
    public function slugFor(string $label, string $code): string
    {
        // ACCENTS ARE FOLDED, NEVER DROPPED: without this, "Écrire à la méthode" opens on a dash and reads as a stub. Every ref written by the slug migration folds them, and a ref is a label one
        // recognises at a glance — a leading dash costs that recognition on exactly the words French starts sentences with.
        $folded = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $label);
        $base = preg_replace('/[^a-z0-9]+/', '-', strtolower($folded));
        $slug = str_pad(mb_substr($base, 0, 20), 20, '-');
        if ($this->find($slug) !== null) {
            $slug = mb_substr($slug, 0, 20 - mb_strlen($code) - 1) . '-' . mb_strtolower($code);
        }

        return $slug;
    }
}

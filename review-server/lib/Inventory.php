<?php
/**
 * USAGE
 *   Read the subject inventory — types, subjects, variants, versions — whenever a page has to show what the project has produced.
 *
 * INTENTION
 *   Reads THE inventory of subjects — assets/subjects.json — and nothing else, for every page that shows what the project has produced. Three pages read it today, each with its own copy of the same
 *   twenty lines, and the copies had already drifted: one knew about a variant field the others ignored. One reader, one behaviour.
 *
 *   IT READS, IT NEVER INVENTS. A name comes from the inventory documents, where a human wrote it; a subject the documents cannot name is reported rather than given a made-up label. A ref is read on
 *   the variant, never recomposed from its fields — the model says a ref is written, and two builders recomposing it their own way is exactly how file names and page labels stop agreeing.
 *
 *   In PHP because it is the project's default language for durable tooling, and reading JSON needs nothing that only Python has.
 */

class Inventory
{
    private array $data;
    private array $labels;

    /** @var string[] Codes the inventory documents could not put a name to — reported, never papered over with the code itself. */
    public array $unlabelled = [];

    public function __construct(private string $root = __DIR__ . '/../..')
    {
        $path = $this->root . '/assets/subjects.json';
        if (!is_file($path)) {
            throw new RuntimeException("FAULT {$path} est introuvable — aucune page ne se construit sans l'inventaire des sujets.");
        }
        $this->data = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        $this->labels = $this->readLabels();
    }

    public function types(): array
    {
        return $this->data['types'];
    }

    public function subjects(): array
    {
        return $this->data['subjects'];
    }

    public function subject(string $code): ?array
    {
        return $this->data['subjects'][$code] ?? null;
    }

    /** The subjects of one type, in code order — the order a page lists them in, and the only one the inventory itself implies. */
    public function subjectsOfType(string $type): array
    {
        $codes = array_keys(array_filter($this->data['subjects'], fn (array $subject) => $subject['type'] === $type));
        sort($codes);

        return $codes;
    }

    /** The French name of a subject, read from the inventory documents where a human wrote it. Falls back to the code, and says so in unlabelled. */
    public function label(string $code): string
    {
        return $this->labels[$code] ?? $code;
    }

    /**
     * The extra variant fields a type declares, in a fixed alphabetical order.
     *
     * A variant field is any type key ending in "s" whose value carries both "values" and "default" — the shape `compositions` and `portillons` already have, and whichever comes next without a
     * change here. Alphabetical because the inventory orders nothing itself, and a ref and a caption must agree on the same order everywhere.
     */
    public function variantFields(array $type): array
    {
        $fields = [];
        foreach ($type as $key => $value) {
            if (str_ends_with($key, 's') && is_array($value) && isset($value['values'], $value['default'])) {
                $fields[] = $key;
            }
        }
        sort($fields);

        return $fields;
    }

    /** The values a variant carries that are NOT its field's default — a default is never written, so writing it back would only make the others harder to read. */
    public function variantValues(array $type, array $variant): array
    {
        $values = [];
        foreach ($this->variantFields($type) as $key) {
            $field = substr($key, 0, -1);
            $value = $variant[$field] ?? null;
            if ($value && $value !== $type[$key]['default']) {
                $values[] = $value;
            }
        }

        return $values;
    }

    /** The version shown today for a variant: the one marked `courante`, or the single one that carries no status yet — a tolerated gap, never a silent guess. */
    public function currentRepresentation(array $variant): ?array
    {
        $representations = $variant['representations'] ?? [];
        foreach ($representations as $representation) {
            if (($representation['status'] ?? '') === 'current') {
                return $representation;
            }
        }

        return count($representations) === 1 ? $representations[0] : null;
    }

    /** The earlier versions of a variant, most recent first — what a comparison offers beside the current one. */
    public function previousRepresentations(array $variant): array
    {
        return array_values(array_filter($variant['representations'] ?? [],
            fn (array $representation) => ($representation['status'] ?? '') === 'previous'));
    }

    /** The variant a subject shows first: the one it marks `principale`, or its first — a subject always has one (sujets-et-variantes.md). */
    public function mainVariant(array $subject): ?array
    {
        foreach ($subject['variants'] as $variant) {
            if ($variant['main'] ?? false) {
                return $variant;
            }
        }

        return $subject['variants'][0] ?? null;
    }

    /** What the subject covers on screen: its couvert when it declares one, its emprise otherwise — the same reading the generation and the export do. */
    public function spread(array $subject): array
    {
        return $subject['cover'] ?? $subject['footprint'];
    }

    private function readLabels(): array
    {
        $directory = $this->root . '/doc/conception/referentiels/visuel/inventaire';
        $texts = [];
        foreach (glob($directory . '/*.md') ?: [] as $path) {
            $texts[] = file_get_contents($path);
        }
        $labels = [];
        foreach (array_keys($this->data['subjects']) as $code) {
            foreach ($texts as $text) {
                if (preg_match('/\*\*' . preg_quote($code, '/') . '\s+([^*]+)\*\*/u', $text, $found)) {
                    $labels[$code] = trim($found[1]);
                    continue 2;
                }
            }
            $this->unlabelled[] = $code;
        }

        return $labels;
    }
}

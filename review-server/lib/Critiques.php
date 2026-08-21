<?php
/**
 * USAGE
 *   Read the critiques filed against one trial — the `<consigne>.critiques.json` written beside the consigne — and anchor each one ON THE SENTENCE of the consigne
 *   it puts in question. `Critiques::get()->read('…/BT-001.txt')` gives them back with a byte range in the consigne, or says why it cannot place one.
 *
 * INTENTION
 *   A CRITIQUE IS NOT A NOTE IN THE MARGIN. Told beside the consigne, « the building is too short » sends nobody anywhere; anchored on the clause that fixes the
 *   height, it names the level that wrote that clause, and therefore WHERE the fix goes. That is the whole difference between a remark and an actionable one.
 *
 *   AN ANCHOR THAT CANNOT BE PLACED IS A REFUSAL, NEVER A CRITIQUE SHOWN LOOSE. A quote that no longer appears in the consigne means the consigne was rewritten
 *   under it: printing the critique anyway would hang yesterday's judgement on today's text, and printing nothing would lose it silently. It is shown, named, and
 *   said to be unplaceable — the reader decides.
 *
 *   AND AN AMBIGUOUS ANCHOR IS REFUSED TOO. A quote found twice would highlight one of the two at random, which is a coin toss dressed as a measurement. Quoting
 *   one more clause of the surrounding sentence settles it, and the message says so.
 *
 *   THEY DO NOT SURVIVE THEIR TRIAL, AND THAT IS DELIBERATE (operator, 2026-08-13: « tes critiques n'ont pas à survivre, tu ne dois garder que les conclusions dans
 *   la doc et le code »). What must remain is what a critique CHANGED — the rule written to the referential, the fix in the socle. So no durable home is built for
 *   them here, on purpose.
 *
 *   THEY LIVE BESIDE THE VERSION THEY JUDGE, and their path is DEDUCED from the consigne's — `<SUBJECT>.v<N>.critiques.json` in the same folder, whose foyer is
 *   `Prompts::HOME`. Holding a second folder in parallel is what made this service report « aucune critique » while the file sat on disk one directory away,
 *   after the consignes moved under var/ on 2026-08-17. A critique names the version it judges, so it is filed under that version's name.
 *
 *   AND ITS FOYER IS NOT A DURABLE HOME. Being on disk does not make a critique a record to keep: it is deleted with its trial, and nothing reads it afterwards.
 *   What survives a trial is what its critiques CHANGED, at its own foyer — the source block, the code.
 */

require_once __DIR__ . '/Prompts.php';

class Critiques
{
    /** The format the file declares. A file that does not carry it is not a critique file, whatever its name. */
    public const FORMAT = 'gatebeast-prompt-critiques';

    /** What a critique claims, and the list is closed — each one says what the reader is expected to DO with it. */
    public const KINDS = [
        'faute' => 'Faute',
        'manque' => 'Manque',
        'constat' => 'Constat',
    ];

    private static ?self $instance = null;

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * The critiques filed against one consigne, each placed in its text — or the reason none can be shown.
     *
     * Returns `['critiques' => array, 'fault' => string|null]`. Each critique carries `kind`, `title`, `text`, and either an `offset`/`length` in the consigne or
     * an `unplaceable` sentence saying why it has none. A critique that deliberately targets the IMAGE rather than the text quotes nothing and is placed nowhere:
     * it is not a failure, and `unplaceable` stays null.
     */
    public function read(string $promptPath, string $body, string $root): array
    {
        // THEY LIVE BESIDE THE VERSION THEY JUDGE, and `Prompts` computes that path — this file does not know the naming mould and has no business knowing
        // it. Holding a second copy here made the page say « aucune critique » while the file sat on disk one directory away.
        $path = Prompts::get()->beside($promptPath, 'critiques');
        if (!is_file($path)) {
            return ['critiques' => [], 'fault' => null];
        }
        try {
            $filed = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $badly) {
            return ['critiques' => [], 'fault' => '« ' . basename($path) . ' » n\'est pas lisible comme du JSON : ' . $badly->getMessage()
                . '. Solution — rouvrir le fichier et le refermer, aucune critique ne se devine.'];
        }
        if (($filed['format'] ?? null) !== self::FORMAT) {
            return ['critiques' => [], 'fault' => '« ' . basename($path) . ' » ne déclare pas le format ' . self::FORMAT . ' — ce ne sont pas des critiques.'];
        }
        $read = [];
        foreach ($filed['critiques'] ?? [] as $rank => $one) {
            $read[] = $this->place($one, $rank, $body);
        }

        return ['critiques' => $read, 'fault' => null];
    }

    /** The critiques that fall inside one block of the consigne, in the order they appear in its text. */
    public function within(array $critiques, int $offset, int $length): array
    {
        $inside = array_filter($critiques, static fn (array $one): bool =>
            $one['offset'] !== null && $one['offset'] >= $offset && $one['offset'] < $offset + $length);
        usort($inside, static fn (array $a, array $b): int => $a['offset'] <=> $b['offset']);

        return $inside;
    }

    /** The critiques that hang on nothing — those about the image, and those whose anchor could not be placed. Neither belongs under a section. */
    public function loose(array $critiques): array
    {
        return array_values(array_filter($critiques, static fn (array $one): bool => $one['offset'] === null));
    }

    /**
     * One critique, placed in the consigne by its quote.
     *
     * THE SEARCH IS WHITESPACE-BLIND AND NOTHING ELSE. Our consignes are hard-wrapped, so a quote spanning a line break would never be found literally, and a
     * critique would read as unplaceable on a sentence that is right there. Case and wording are NOT relaxed: a quote that no longer matches word for word is a
     * quote of a text that has changed, and that is precisely what must be reported rather than smoothed over.
     */
    private function place(array $one, int $rank, string $body): array
    {
        $placed = [
            'kind' => isset(self::KINDS[$one['kind'] ?? '']) ? $one['kind'] : 'constat',
            'title' => $one['title'] ?? 'Critique ' . ($rank + 1),
            'text' => $one['text'] ?? '',
            'quote' => $one['quote'] ?? null,
            // KEPT FOR CRITIQUES WRITTEN BEFORE VERSIONS EXISTED, and read by nothing today: a proposed rewrite is now a VERSION of the whole consigne, and the
            // diff runs from one version to the next. Dropping the field would make those files fail to load for no gain; nothing new should carry it.
            'proposal' => $one['proposal'] ?? null,
            'offset' => null,
            'length' => 0,
            'unplaceable' => null,
        ];
        if ($placed['quote'] === null) {
            return $placed;
        }
        $pattern = '/' . implode('\s+', array_map('preg_quote', preg_split('/\s+/u', trim($placed['quote'])))) . '/u';
        if (!preg_match_all($pattern, $body, $found, PREG_OFFSET_CAPTURE)) {
            $placed['unplaceable'] = 'sa citation ne se trouve plus dans la consigne : le texte a été réécrit depuis, et cette critique porte sur une phrase qui'
                . ' n\'y est plus. Solution — la relire contre la consigne actuelle avant de la reporter.';

            return $placed;
        }
        if (count($found[0]) > 1) {
            $placed['unplaceable'] = sprintf('sa citation apparaît %d fois dans la consigne : la placer reviendrait à en choisir une au hasard.'
                . ' Solution — citer une clause de plus autour d\'elle.', count($found[0]));

            return $placed;
        }
        $placed['offset'] = $found[0][0][1];
        $placed['length'] = strlen($found[0][0][0]);

        return $placed;
    }
}

<?php
/**
 * USAGE
 *   Hold our consigne against the one the agent says it handed to its own image model, and say — sentence by sentence, section by section — what came through
 *   word for word and what did not. `PromptDiff::get()->compare($ourSentences, $transmitted)`.
 *
 * INTENTION
 *   OUR CONSIGNE IS NOT READ BY AN IMAGE MODEL, IT IS READ BY AN AGENT, which rewrites it for its own generator. Between what we write and what is drawn there is
 *   therefore a rewriting nobody had ever seen. What is lost there and what was badly prescribed in the first place are two causes calling for opposite fixes,
 *   and they were confused for three days on the parallel projection.
 *
 *   THIS COMPARES ONLY WHAT CAN BE CHECKED, AND THAT IS A DECISION, NOT A LIMITATION (endorsed by the operator's rule on a tool that cannot conclude: it says so,
 *   and that is not a favourable verdict). The transmitted consigne is a free rewriting: no sections, no headings, nothing that lines up structurally. So the one
 *   thing said here is the one thing a reader can redo by hand — an EXACT search for each of our sentences in the transmitted text, whitespace collapsed and case
 *   set aside. A sentence is FOUND WORD FOR WORD, or it is NOT FOUND. Nothing else is claimed.
 *
 *   WHAT IS DELIBERATELY NOT WRITTEN HERE: a similarity score deciding « reformulated » rather than « lost ». A sentence absent to the word may well be present in
 *   idea, and no mechanical measure settles that without inventing a certainty. « Reformulée » names the partly-found case; it is not a judgement of meaning
 *   rendered by a machine. A real judgement of meaning comes from an agent that reads, and it is written as an anchored critique — which the page carries.
 *
 *   AND A FRAGMENT TOO SHORT PROVES NOTHING. « OUI. » found in a page of text is not evidence that a clause came through; it is evidence that both texts are in
 *   French. Below the floor, a sentence is counted apart and says so, rather than padding either column.
 */

class PromptDiff
{
    private static ?self $instance = null;

    /** Under this many characters, finding a sentence proves nothing — see the intention. Counted in characters, not bytes: our consignes are accented. */
    public const EVIDENCE_FLOOR = 16;

    /** The states a section can be in, prefixed, and there are exactly four. */
    public const SECTION_INTACT = 'intact';

    public const SECTION_PARTIAL = 'partial';

    public const SECTION_LOST = 'lost';

    public const SECTION_UNMEASURABLE = 'unmeasurable';

    public const SECTION_LABELS = [
        self::SECTION_INTACT => 'Arrivée intacte',
        self::SECTION_PARTIAL => 'Arrivée en partie',
        self::SECTION_LOST => 'Disparue',
        self::SECTION_UNMEASURABLE => 'Rien de mesurable',
    ];

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * Cut a block of our consigne into the sentences the comparison works on, each with WHERE IT IS in the whole consigne.
     *
     * THE OFFSET TRAVELS WITH THE SENTENCE, in bytes of the consigne, because it is the anchor a critique is filed under — the same vocabulary the split already
     * speaks. A second identity, a rank or a hash of the text, would have to be kept in step with this one.
     *
     * A sentence ends at « . », « ! », « ? », « : » or at a line break, whichever comes first — our consignes are written in shouted paragraphs and in lists, and
     * a splitter that only knew full stops would hand back a whole list as one sentence, which no search would ever find in a rewriting.
     */
    public function sentencesOf(string $body, int $offset, int $length): array
    {
        $text = substr($body, $offset, $length);
        $sentences = [];
        $start = 0;
        $at = 0;
        $stop = strlen($text);
        while ($at < $stop) {
            $char = $text[$at];
            $ends = $char === "\n" || (strpos('.!?:', $char) !== false && ($at + 1 >= $stop || $text[$at + 1] === ' ' || $text[$at + 1] === "\n"));
            $at++;
            if (!$ends) {
                continue;
            }
            $sentences[] = $this->sentence($text, $start, $at - $start, $offset);
            $start = $at;
        }
        if ($start < $stop) {
            $sentences[] = $this->sentence($text, $start, $stop - $start, $offset);
        }

        return array_values(array_filter($sentences, static fn (?array $one): bool => $one !== null));
    }

    /**
     * What became of each of our sentences in the transmitted text, and the state of the section they form.
     *
     * `$transmitted` at null is not an empty rewriting, it is an UNKNOWN one: the agent did not report what it passed on. Saying « disparue » of every sentence
     * would turn a missing trace into a finding, which is the transparent error this repository forbids by name.
     */
    public function compare(array $sentences, ?string $transmitted): array
    {
        if ($transmitted === null) {
            return ['state' => null, 'sentences' => $sentences, 'found' => 0, 'missing' => 0, 'short' => 0];
        }
        [$flat, $map] = $this->flatten($transmitted);
        $found = 0;
        $missing = 0;
        $short = 0;
        foreach ($sentences as $rank => $one) {
            if ($one['short']) {
                $sentences[$rank]['found'] = null;
                $short++;
                continue;
            }
            $at = strpos($flat, $one['flat']);
            $sentences[$rank]['found'] = $at !== false;
            if ($at === false) {
                $missing++;
                continue;
            }
            $found++;
            // WHERE IT LANDED IN THE TRANSMITTED TEXT, in the ORIGINAL text's own bytes: the search runs on a flattened copy, so its offsets mean nothing to a
            // reader. The map built with that copy takes them back, which is what lets the page highlight the real text rather than a normalised ghost.
            $sentences[$rank]['transmitted'] = ['offset' => $map[$at], 'end' => $map[$at + strlen($one['flat']) - 1] + 1];
        }

        return ['state' => $this->stateOf($found, $missing, $short), 'sentences' => $sentences, 'found' => $found, 'missing' => $missing, 'short' => $short];
    }

    /** The section's own state, read off its counts and nothing else. */
    private function stateOf(int $found, int $missing, int $short): string
    {
        if ($found === 0 && $missing === 0) {
            return self::SECTION_UNMEASURABLE;
        }
        if ($missing === 0) {
            return self::SECTION_INTACT;
        }

        return $found === 0 ? self::SECTION_LOST : self::SECTION_PARTIAL;
    }

    /** One sentence, kept only if it carries anything at all beyond spaces. */
    private function sentence(string $text, int $start, int $length, int $offset): ?array
    {
        $raw = substr($text, $start, $length);
        $flat = $this->collapse($raw);
        if ($flat === '') {
            return null;
        }

        return [
            'text' => $raw,
            'flat' => $flat,
            'offset' => $offset + $start,
            'length' => $length,
            'short' => mb_strlen($flat) < self::EVIDENCE_FLOOR,
        ];
    }

    /**
     * A string in the form both sides are compared in: whitespace collapsed, lowercased, trimmed.
     *
     * IT GOES THROUGH THE SAME CODE AS THE HAYSTACK, and that is the point of the line: two normalisations written separately agree until one of them meets a
     * character the other lowers differently, and the search then fails on a sentence that is right there. One path, one answer.
     */
    private function collapse(string $text): string
    {
        return $this->flatten($text)[0];
    }

    /**
     * The transmitted text in its compared form, WITH the way back: for each byte of the flattened copy, the byte of the original it came from.
     *
     * Built together in one pass rather than reconstructed afterwards — a second traversal computing the same positions is exactly where an off-by-one lives, and
     * it would show as a highlight sliding a character to the left on accented text.
     */
    private function flatten(string $text): array
    {
        $flat = '';
        $map = [];
        $space = false;
        // WALKED CHARACTER BY CHARACTER, NEVER BYTE BY BYTE, AND THE MAP IS FED PER BYTE OF THE RESULT. Lowercasing can change a character's byte length, and our
        // consignes shout in accented capitals: a map built on the assumption that a lowered character weighs what it weighed would slide by one byte after the
        // first « É » and highlight half a word. Each byte of the lowered character points back at the character it came from, so no assumption is made at all.
        foreach (preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY | PREG_SPLIT_OFFSET_CAPTURE) as [$char, $at]) {
            if (preg_match('/\s/u', $char)) {
                $space = $flat !== '';
                continue;
            }
            if ($space) {
                $flat .= ' ';
                $map[] = $at;
                $space = false;
            }
            $lowered = mb_strtolower($char);
            $flat .= $lowered;
            for ($byte = 0, $weight = strlen($lowered); $byte < $weight; $byte++) {
                $map[] = $at;
            }
        }

        return [$flat, $map];
    }
}

<?php
/**
 * USAGE
 *   Hold two versions of the SAME passage against each other and hand back what changed, in runs of words: `WordDiff::get()->runs($before, $after)` returns a list
 *   of `['op' => 'keep'|'remove'|'add', 'text' => string]`, in reading order.
 *
 * INTENTION
 *   A PROPOSED REWRITE IS UNREADABLE AS TWO BLOCKS OF TEXT SIDE BY SIDE. The reader ends up comparing them word by word himself, which is exactly the work the
 *   diff is supposed to do — and on a consigne whose clauses are shouted paragraphs, the two blocks look identical at a glance while differing on the one word
 *   that mattered.
 *
 *   AND A LINE-BY-LINE DIFF IS THE WRONG GRAIN HERE (operator, 2026-08-13: « pas ligne par ligne mais lot de mots par lot de mots »). Our consignes are
 *   hard-wrapped, so changing one word marks the whole line as replaced and the eye has to find the difference inside it anyway. Words are the unit a sentence is
 *   actually edited in.
 *
 *   RUNS, NOT WORDS, IS WHAT COMES BACK. Three consecutive deleted words are one deletion, not three: rendered one by one they would be three struck-through
 *   fragments separated by live spaces, which reads as a broken sentence rather than as a removed clause.
 *
 *   WHITESPACE IS NOT COMPARED, AND THE REWRITE IS REJOINED WITH SINGLE SPACES. Our consignes are wrapped at a fixed width, so the same sentence re-wrapped one
 *   column further would show as entirely changed if spacing counted. What is being proposed is the wording, never the wrapping.
 */

class WordDiff
{
    public const KEEP = 'keep';

    public const REMOVE = 'remove';

    public const ADD = 'add';

    /**
     * The share of the NEW text that must survive from the old one for a change to still read as a retouch rather than a rewrite.
     *
     * A THIRD, and the figure is a judgement rather than a measure: below it, what two texts share is the grammar of the language — articles, prepositions,
     * relative pronouns — and marking those as « kept » says nothing about the meaning. It is declared here so that raising it is a decision, not a habit.
     */
    public const REWRITE_FLOOR = 0.35;

    /**
     * Below this many characters, a run matching both texts proves nothing about having been KEPT — see merged().
     *
     * The figure is `PromptDiff::EVIDENCE_FLOOR`, and it is stated here rather than borrowed: the two answer different questions — one asks whether a sentence
     * survived a rewriting, the other whether a match is a coincidence — and tying them together would make a change to either drag the other along.
     */
    public const EVIDENCE_FLOOR = 16;

    private static ?self $instance = null;

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * What changed between two whole VERSIONS of a text, as runs in reading order — the same three operations, over a document rather than a sentence.
     *
     * LINES FIRST, THEN WORDS INSIDE WHAT MOVED, and that is a necessity rather than a refinement. A word-level comparison of two consigne versions is quadratic
     * in their two thousand words — four million cells, for a text where nine tenths of the lines are untouched. Matching lines first costs a hundred squared,
     * and the word comparison then runs only inside the hunks that actually differ, where it is both cheap and the grain the reader wants.
     *
     * KEPT LINES KEEP THEIR LINE BREAKS. The consignes are hard-wrapped and read as such: rejoining untouched paragraphs with single spaces would show the whole
     * document as reflowed, which is the noise this exists to remove.
     */
    public function versions(string $before, string $after): array
    {
        // LINES KEEP THEIR OWN LINE BREAK rather than having one appended back when rendering: a text ending in a break otherwise yields a last empty line, that
        // line gets a break added to it, and the diff then covers one byte more than the text it describes.
        $old = preg_split('/(?<=\n)/', $before, -1, PREG_SPLIT_NO_EMPTY);
        $new = preg_split('/(?<=\n)/', $after, -1, PREG_SPLIT_NO_EMPTY);
        $steps = $this->walk($old, $new, $this->common($old, $new));
        $runs = [];
        $removed = [];
        $added = [];
        // Hunks are closed on the first KEPT line after them: only there is it known that both sides of the change are complete. The sentinel closes the last one.
        foreach ([...$steps, [self::KEEP, null]] as [$op, $line]) {
            if ($op === self::REMOVE) {
                $removed[] = $line;
                continue;
            }
            if ($op === self::ADD) {
                $added[] = $line;
                continue;
            }
            if ($removed !== [] || $added !== []) {
                $runs = [...$runs, ...$this->hunk(implode('', $removed), implode('', $added))];
                $removed = [];
                $added = [];
            }
            if ($line !== null) {
                $runs[] = ['op' => self::KEEP, 'text' => $line];
            }
        }

        return $runs;
    }

    /**
     * One changed hunk, compared word by word — or a pure removal or addition, which needs no comparison at all.
     *
     * UN PARAGRAPHE ENTIÈREMENT RÉÉCRIT EST UN PARAGRAPHE SUPPRIMÉ ET UN PARAGRAPHE AJOUTÉ, PAS DES BOUTS (opérateur, 2026-08-17 : « quand un paragraphe est
     * entièrement ré-écrit, c'est un paragraphe entier supprimé et un entier ajouté, pas de petits bouts en petits bouts »). Deux rédactions différentes du même
     * sujet partagent des dizaines de mots vides — « de », « la », « et », « qui » — et un diff de mots les épingle un à un, rendant les deux textes en confettis
     * rouges et verts où l'on ne lit plus ni l'ancien ni le nouveau. Sous le plancher de survie, le mot à mot ne renseigne plus : il obscurcit.
     *
     * LE PLANCHER PORTE SUR CE QUI SURVIT, pas sur ce qui change, et il se mesure sur le texte NEUF : c'est celui qu'on lit. Au-dessus, une retouche se voit mieux
     * mot à mot ; en dessous, on veut voir les deux rédactions entières, l'une après l'autre.
     */
    private function hunk(string $removed, string $added): array
    {
        if ($removed === '') {
            return [['op' => self::ADD, 'text' => $added]];
        }
        if ($added === '') {
            return [['op' => self::REMOVE, 'text' => $removed]];
        }
        $runs = $this->runs($removed, $added);
        $kept = 0;
        foreach ($runs as $run) {
            if ($run['op'] === self::KEEP) {
                $kept += strlen($run['text']);
            }
        }
        if (strlen($added) > 0 && $kept / strlen($added) < self::REWRITE_FLOOR) {
            return [['op' => self::REMOVE, 'text' => $removed], ['op' => self::ADD, 'text' => $added]];
        }

        return $runs;
    }

    /**
     * What changed between the two passages, as runs of words in reading order.
     *
     * THE KEPT AND ADDED RUNS TILE `$after` BYTE FOR BYTE, and that is a contract, not an implementation detail: the page maps these runs onto the active text to
     * place the critiques' anchors in the same pass. Rejoining the words with single spaces — the obvious way to write this — silently drops the line breaks and
     * double spaces of a hard-wrapped consigne, so the runs come out shorter than the text they describe and every anchor after the first change slides. Each run
     * therefore carries a SPAN of the original text, from its first word to the first word of the next run, whitespace included.
     */
    public function runs(string $before, string $after): array
    {
        $old = $this->words($before);
        $new = $this->words($after);
        $steps = $this->walk(array_column($old, 0), array_column($new, 0), $this->common(array_column($old, 0), array_column($new, 0)));
        $runs = [];
        $i = 0;
        $j = 0;
        foreach ($steps as [$op, $word]) {
            $from = $op === self::REMOVE ? $old[$i][1] : $new[$j][1];
            if ($runs !== [] && $runs[count($runs) - 1]['op'] === $op) {
                $runs[count($runs) - 1]['stop'] = $from + strlen($word);
            } else {
                $runs[] = ['op' => $op, 'start' => $from, 'stop' => $from + strlen($word)];
            }
            $op === self::REMOVE ? $i++ : ($op === self::ADD ? $j++ : ($i++ && $j++));
        }

        return $this->merged($this->spans($runs, $before, $after));
    }

    /**
     * The runs with the ACCIDENTAL matches folded back into the change around them.
     *
     * A WHOLLY NEW PARAGRAPH MUST READ AS ONE COLOUR (operator, 2026-08-13, on an inserted clause coming back green, then white, then green: « vert jaune blanc →
     * une seule couleur »). Inside a rewritten passage, « le », « la », « haut » match the old text by coincidence, not because they were kept: rendering them as
     * unchanged breaks an insertion into speckles and makes the reader hunt for a difference that is not there.
     *
     * SO A KEPT RUN MUST EARN ITS STATUS, and the bar is the same evidence floor `PromptDiff` uses on the transmitted consigne. Below it, the run belongs to the
     * new text like everything around it, and it is shown as added. Above it, a genuinely untouched clause still shows through, which is the point of comparing
     * word by word rather than line by line.
     */
    private function merged(array $runs): array
    {
        $folded = [];
        foreach ($runs as $run) {
            $op = $run['op'] === self::KEEP && ($run['weight'] ?? strlen($run['text'])) < self::EVIDENCE_FLOOR ? self::ADD : $run['op'];
            if ($folded !== [] && $folded[count($folded) - 1]['op'] === $op) {
                $folded[count($folded) - 1]['text'] .= $run['text'];
                continue;
            }
            $folded[] = ['op' => $op, 'text' => $run['text']];
        }

        return $folded;
    }

    /** The words of a text, each with WHERE it starts — the offsets are what lets a run be cut out of the original rather than rebuilt from its words. */
    private function words(string $text): array
    {
        preg_match_all('/\S+/u', $text, $found, PREG_OFFSET_CAPTURE);

        return $found[0];
    }

    /**
     * The runs turned into text, the kept and added ones tiling `$after` from its first word to its end.
     *
     * A run stops where the NEXT kept-or-added run starts, never at its own last word: the whitespace between two runs belongs to the text and has to be carried
     * by one of them. Giving it to the run that precedes it keeps the tiling contiguous with no special case at the end.
     */
    private function spans(array $runs, string $before, string $after): array
    {
        $spanned = [];
        foreach ($runs as $rank => $run) {
            if ($run['op'] === self::REMOVE) {
                $spanned[] = ['op' => self::REMOVE, 'weight' => $run['stop'] - $run['start'],
                    'text' => substr($before, $run['start'], $run['stop'] - $run['start'])];
                continue;
            }
            $next = null;
            foreach (array_slice($runs, $rank + 1) as $later) {
                if ($later['op'] !== self::REMOVE) {
                    $next = $later['start'];
                    break;
                }
            }
            // The very first span carries whatever precedes the first word, otherwise the leading whitespace would belong to nobody and the tiling would gap.
            $start = $spanned === [] || !array_filter($spanned, static fn(array $one): bool => $one['op'] !== self::REMOVE) ? 0 : $run['start'];
            // THE WEIGHT IS THE MATCHED WORDS ALONE, never the span they carry. A span runs to the start of the next one, so a two-letter match sitting near the
            // end of a hunk drags the whole tail along with it — judged on that length it would pass for a kept clause, and the insertion would come back
            // speckled white exactly where it should read as one block.
            $spanned[] = ['op' => $run['op'], 'weight' => $run['stop'] - $run['start'],
                'text' => substr($after, $start, ($next ?? strlen($after)) - $start)];
        }

        return $spanned;
    }

    /**
     * The length of the longest common subsequence of every pair of suffixes — the table the walk reads backwards.
     *
     * Built from the end so that `$table[$i][$j]` answers for the suffixes starting at `$i` and `$j`, which is the direction the walk needs. Quadratic in the
     * number of words, on passages of a sentence or two: the cost is nothing and the alternative — a heuristic — would drop a match and show a moved clause as a
     * deletion plus an insertion.
     */
    private function common(array $old, array $new): array
    {
        $table = array_fill(0, count($old) + 1, array_fill(0, count($new) + 1, 0));
        for ($i = count($old) - 1; $i >= 0; $i--) {
            for ($j = count($new) - 1; $j >= 0; $j--) {
                $table[$i][$j] = $old[$i] === $new[$j] ? $table[$i + 1][$j + 1] + 1 : max($table[$i + 1][$j], $table[$i][$j + 1]);
            }
        }

        return $table;
    }

    /** The table walked once, word by word, into a flat list of operations. */
    private function walk(array $old, array $new, array $table): array
    {
        $steps = [];
        $i = 0;
        $j = 0;
        while ($i < count($old) && $j < count($new)) {
            if ($old[$i] === $new[$j]) {
                $steps[] = [self::KEEP, $old[$i++]];
                $j++;
                continue;
            }
            // A REMOVAL IS PREFERRED WHEN THE TWO BRANCHES TIE, and the tie is common: it puts the old wording before the new one, which is the order a reader
            // expects — what it said, then what it would say.
            if ($table[$i + 1][$j] >= $table[$i][$j + 1]) {
                $steps[] = [self::REMOVE, $old[$i++]];
                continue;
            }
            $steps[] = [self::ADD, $new[$j++]];
        }
        while ($i < count($old)) {
            $steps[] = [self::REMOVE, $old[$i++]];
        }
        while ($j < count($new)) {
            $steps[] = [self::ADD, $new[$j++]];
        }

        return $steps;
    }

    /** Consecutive words carrying the same operation, joined into one run. */
    private function group(array $steps): array
    {
        $runs = [];
        foreach ($steps as [$op, $word]) {
            if ($runs !== [] && $runs[count($runs) - 1]['op'] === $op) {
                $runs[count($runs) - 1]['text'] .= ' ' . $word;
                continue;
            }
            $runs[] = ['op' => $op, 'text' => $word];
        }

        return $runs;
    }
}

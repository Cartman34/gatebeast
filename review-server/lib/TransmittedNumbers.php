<?php
/**
 * USAGE
 *   What a version lost between our consigne and what the agent actually sent to its image model. `TransmittedNumbers::get()->compare($prompt, $transmitted)`
 *   returns `['wanted' => int, 'given' => int, 'lost' => [number => sentence]]`.
 *
 * INTENTION
 *   COMPARING THE WORDS CANNOT WORK ANY MORE, AND THAT IS BY DESIGN. Until the `v7` of `BT-001` the agent relayed our prose, so a word-for-word diff meant
 *   something. Since the `v7` we ASK it to translate — into English, into the terms its image model knows — so a word-for-word diff would report « Disparue » on
 *   everything, including on what arrived perfectly. Measuring the resemblance of the words measures our own instruction, not its execution.
 *
 *   WHAT SURVIVES TRANSLATION IS THE NUMBER. « 16 TX » becomes « exactly 16 TX drawn width », « deux cases de haut » becomes « exactly 2 tiles high », and in
 *   both cases the FIGURE is still there — it is the one thing a translator cannot restate in other words without changing the constraint.
 *
 *   IT MEASURES PRESENCE, NEVER MEANING. A number found says the constraint survived transmission; it does not say the image respects it — that is what the
 *   measures on the picture are for. A check that claimed more than it can see would be exactly the transparent error this repository chases.
 *
 *   ONE SERVICE, TWO READERS: the command `review-server/workshop/check-transmitted.php` and the workshop page. Written twice, the two would drift, and the page
 *   would show a verdict the command contradicts.
 */

class TransmittedNumbers
{
    /**
     * The sections that address the AGENT and are never transmitted — their figures are not owed to the image.
     *
     * Counting them would demand in the image what we explicitly asked not to put there: this is the consigne's second register, the one that never reaches the
     * model. They are recognised by their heading, which the consigne carries itself.
     */
    public const NOT_TRANSMITTED = ['Comment lire cette consigne', 'Ce que tu nous rapportes'];

    private static ?self $instance = null;

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** What the consigne asks for, what was transmitted, and what was lost between the two. */
    public function compare(string $prompt, string $transmitted): array
    {
        $wanted = $this->numbersOf($this->transmittable($prompt));
        $given = $this->numbersOf($transmitted);
        $lost = [];
        foreach ($wanted as $number => $lines) {
            if (!isset($given[$number])) {
                $lost[$number] = $lines[0];
            }
        }

        return ['wanted' => count($wanted), 'given' => count($given), 'lost' => $lost];
    }

    /** The consigne without the sections that address the agent. */
    public function transmittable(string $prompt): string
    {
        foreach (self::NOT_TRANSMITTED as $title) {
            $prompt = preg_replace('/^### ' . preg_quote($title, '/') . ' \(\w+\)$.*?(?=^#{2,3} )/ms', '', $prompt);
        }

        return $prompt;
    }

    /**
     * The numbers a text carries, each with the lines that hold them.
     *
     * THE DECIMAL COMMA AND THE DECIMAL POINT ARE THE SAME NUMBER: we write « 0,5 TX » and the agent writes « 0.5 », which is a translation and not a loss. The
     * separator is normalised on both sides, or every decimal of the consigne would be reported missing.
     */
    public function numbersOf(string $text): array
    {
        $found = [];
        foreach (explode("\n", $text) as $line) {
            if (!preg_match_all('/\d+(?:[.,]\d+)?/', $line, $matches)) {
                continue;
            }
            foreach ($matches[0] as $number) {
                $found[str_replace(',', '.', $number)][] = trim($line);
            }
        }

        return $found;
    }
}

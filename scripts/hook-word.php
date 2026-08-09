<?php
/**
 * USAGE
 *   require_once'd by hook-prompt.php and hook-stop.php, which then call HookWord::get()->order($text) and HookWord::get()->probes($text).
 *
 * INTENTION
 *   THE TWO HOOKS MUST READ THE OPERATOR'S WORD THE SAME WAY, AND THEY USED TO HOLD TWO COPIES OF THE RULE. One reads the prompt payload, the other the
 *   transcript, but what counts as an order is a single notion — and a notion that lives in two places drifts. It lives here.
 *
 *   WHAT COUNTS: the word alone on its own line, anywhere in the message. The repository rule says no sentence is read as a green light, and that stays true — but
 *   a message is not a sentence. Measured on 2026-08-09: both hooks collapsed the whole message before comparing, so « STOP » followed by a blank line and an
 *   instruction became STOPREGARDEPLUTÔT and matched nothing. The order was there, alone on its line, plain to any reader, and the guard stayed armed. Reading
 *   line by line keeps « attends, stop ça » out — the word is not alone there — and lets the operator say what he wants after his order.
 *
 *   THE LAST ORDER WINS, AND NOTHING ELSE REVOKES ONE. The prompt hook hands it a single message; the Stop hook hands it everything the operator has said, in
 *   order. An order stands until another replaces it: a STOP survives everything said after it, and only a GO lifts it.
 */

class HookWord
{
    private static ?self $instance = null;

    /** The two orders, and the probe word that commands nothing. */
    private const ORDERS = ['GO', 'STOP'];

    /**
     * THE PROBE WORD COMMANDS NOTHING, AND THAT IS ITS WHOLE VALUE. Measuring whether a message reaches a hook used to mean sending a real GO or a real STOP,
     * which changes the dequeue on the spot — the measurement could only be made by disturbing what it measured. This one is recognised, traced, and acted upon
     * by nobody. It is deliberately kept out of the order chain, so a probe sent after a STOP never shadows the STOP.
     */
    private const PROBE = 'PING';

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The last order the text carries — GO, STOP — or null when it carries none. */
    public function order(string $text): ?string
    {
        $found = null;
        foreach ($this->words($text) as $word) {
            if (in_array($word, self::ORDERS, true)) {
                $found = $word;
            }
        }

        return $found;
    }

    /** How many lines of the text carry the probe word alone. */
    public function probes(string $text): int
    {
        $count = 0;
        foreach ($this->words($text) as $word) {
            if ($word === self::PROBE) {
                $count++;
            }
        }

        return $count;
    }

    /**
     * Each line reduced to the word it would be if it carried nothing else: spaces removed, upper-cased. A line holding a sentence comes back as that whole
     * sentence glued together, which matches no order — that is exactly how « attends, stop ça » is kept out.
     *
     * @return array<int, string>
     */
    private function words(string $text): array
    {
        $words = [];
        foreach (preg_split('/\R/u', $text) ?: [] as $line) {
            $words[] = mb_strtoupper((string) preg_replace('/\s+/u', '', $line));
        }

        return $words;
    }
}

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
            // UN ORDRE S'ÉCRIT EN CAPITALES, LES DEUX, ET UNE MINUSCULE NE VAUT RIEN (operator, 2026-08-11 : « GO n'est pas censé accepter les minuscules non
            // plus »). Les deux mots sont trop courants en français ordinaire — « stop, attends », « on y go » — pour qu'une minuscule engage quoi que ce soit.
            // Les capitales sont le geste délibéré qui distingue l'ordre de la conversation, et il n'y a pas de raison qu'un des deux mots soit plus tolérant
            // que l'autre : c'est la même garde qu'ils commandent.
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
     * The order word each line OPENS with, upper-cased — or the line glued together when it opens with something else, which matches nothing.
     *
     * THE WORD IS THE FIRST OF ITS LINE, AND WHAT FOLLOWS IT IS EITHER A WHITESPACE CHARACTER OR NOTHING (operator, 2026-08-11). Three cases, and the rule
     * settles all three: « STOP » alone counts, « stop regarde plutôt ça » counts because the order opens the line, and « attends, stop ça » does not because the
     * word does not open anything. Case does not matter — a lower-case stop is a stop.
     *
     * ANYTHING GLUED TO IT REFUSES THE LINE, and that is deliberate: « STOPPE », « STOP! », « GO2 » are not orders. Only a whitespace character, or the end of the
     * line, closes the word. The previous rule crushed every space before comparing, so a line carrying an order AND a sentence came back as one long token and
     * matched nothing — the operator had to send his word alone, on its own line, and say the rest afterwards.
     *
     * @return array<int, string>
     */
    private function words(string $text): array
    {
        $words = [];
        foreach (preg_split('/\R/u', $text) ?: [] as $line) {
            // LA CASSE EST CONSERVÉE ICI, et c'est `order()` qui décide de ce qu'elle vaut : STOP exige ses capitales, GO non. Écraser la casse dès la lecture
            // rendait cette distinction impossible à exprimer.
            if (preg_match('/^\s*([A-Za-z]+)(\s|$)/u', $line, $found) === 1) {
                $words[] = $found[1];
                continue;
            }
            $words[] = (string) preg_replace('/\s+/u', '', $line);
        }

        return $words;
    }
}

<?php
/**
 * USAGE
 *   Read the split of an assembled consigne — the `<consigne>.parts.json` written beside it by `scripts/generate-sprite.py` — and hand back its blocks with the
 *   level that wrote each one. `PromptParts::get()->read('…/TR-063-v19.txt')` gives the body, the blocks, and, when it cannot conclude, WHY in one sentence.
 *
 * INTENTION
 *   QUAND UNE IMAGE REVIENT FAUSSE, LA QUESTION UTILE N'EST PAS « QUE DIT LA CONSIGNE » MAIS « QUEL NIVEAU A ÉCRIT CETTE PHRASE » (operator, 2026-08-13). That is
 *   what decides where the correction goes, and getting it wrong costs a generation every time: a clause corrected in the subject's description when it came from
 *   the socle comes back identical at the next version, and on every other subject too.
 *
 *   IT TRUSTS NOTHING, AND THAT IS THE WHOLE POINT. A split that has gone stale would attribute sentences to the wrong level with nothing to say so — the very
 *   fault it exists to prevent, made worse by carrying a tool's authority. Three controls before anything is handed back: the fingerprint of the text, the blocks
 *   paving the consigne edge to edge, and the heading read back from the text at the place the split announces. One of them failing is a REFUSAL.
 *
 *   BUT A REFUSAL IS RETURNED, NEVER THROWN. This serves a page that shows trials, where a missing or stale split is the ordinary case rather than an accident:
 *   the page must say « je ne peux pas attribuer ces phrases » beside the consigne it can still show, not collapse and take the whole page down with it. The
 *   caller is told in one sentence, and it is that sentence the page prints. `scripts/show-prompt-parts.php` holds the same three controls for the command line
 *   and refuses outright, which is right for a command; the day it delegates here, it will read this file's answer and exit on it.
 */

class PromptParts
{
    private static ?self $instance = null;

    /** The format the split file declares. A file that does not carry it is not a split, whatever its name. */
    public const FORMAT = 'gatebeast-prompt-parts';

    /** The two heading depths. They match those of generate-sprite.py (GROUP_MARK, GROUPED_MARK) and must move with them. */
    private const GROUP_MARK = '## ';

    private const GROUPED_MARK = '### ';

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * The blocks of one consigne, read and proved — or the reason nothing can be said of them.
     *
     * Returns `['body' => string|null, 'parts' => array, 'fault' => string|null]`. A fault always names the gesture that repairs it: telling a reader it is stuck
     * without telling it how out is half a message.
     */
    public function read(string $promptPath): array
    {
        if (!is_file($promptPath)) {
            return $this->refusal("la consigne « " . basename($promptPath) . " » est absente de l'essai.");
        }
        $partsPath = preg_replace('/\.txt$/', '', $promptPath) . '.parts.json';
        if (!is_file($partsPath)) {
            return $this->refusal('cette consigne n\'a pas de découpage à côté d\'elle : « ' . basename($partsPath) . ' » est absent. Les consignes assemblées'
                . ' avant que le découpage existe n\'en portent pas, et cela ne se rattrape pas en l\'inventant.');
        }
        $body = file_get_contents($promptPath);
        try {
            $split = json_decode(file_get_contents($partsPath), true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $badly) {
            return $this->refusal('le découpage « ' . basename($partsPath) . ' » n\'est pas lisible comme du JSON : ' . $badly->getMessage() . '.');
        }
        if (($split['format'] ?? null) !== self::FORMAT) {
            return $this->refusal('« ' . basename($partsPath) . ' » ne déclare pas le format ' . self::FORMAT . ' — ce n\'est pas un découpage de consigne.');
        }
        // L'EMPREINTE DIT QUE C'EST BIEN CE TEXTE-LÀ. Des décalages seuls vieillissent en silence le jour où la consigne est réassemblée ; liés à l'empreinte de ce
        // texte exact, ils sont REFUSÉS au lieu d'attribuer des phrases au mauvais niveau.
        if (($split['fingerprint'] ?? '') !== 'sha256:' . hash('sha256', $body)) {
            return $this->refusal('le découpage porte l\'empreinte d\'un autre texte : la consigne a été réassemblée depuis, et attribuer ses phrases d\'après'
                . ' ce découpage les rattacherait au mauvais niveau.');
        }
        $offset = 0;
        foreach ($split['parts'] as $rank => $part) {
            if ($part['offset'] !== $offset) {
                return $this->refusal(sprintf('le découpage ne pave pas la consigne : le bloc « %s » commence à l\'octet %d alors que le précédent s\'arrête à'
                    . ' %d. Un trou ou un recouvrement veut dire qu\'un morceau de texte n\'appartient à aucun niveau, ou à deux.', $part['title'],
                    $part['offset'], $offset));
            }
            $opening = $this->headingOf($part, $rank > 0 ? $split['parts'][$rank - 1] : null);
            if (substr($body, $part['offset'], strlen($opening)) !== $opening) {
                return $this->refusal(sprintf('le bloc de rang %d devrait s\'ouvrir par « %s » et le texte dit autre chose à cet endroit — le découpage et la'
                    . ' consigne ne s\'accordent plus, ni sur les blocs ni sur le niveau qui les a écrits.', $rank, rtrim($opening)));
            }
            $offset += $part['length'];
        }
        if ($offset !== strlen($body)) {
            return $this->refusal(sprintf('le découpage recouvre %d octets pour une consigne qui en fait %d : la fin de la consigne n\'appartient à aucun bloc.',
                $offset, strlen($body)));
        }

        return ['body' => $body, 'parts' => $split['parts'], 'fault' => null];
    }

    /** The content of one block, its heading lines removed — what the generator reads under that title, and nothing else. */
    public function contentOf(string $body, array $part, ?array $previous): string
    {
        return substr(substr($body, $part['offset'], $part['length']), strlen($this->headingOf($part, $previous)));
    }

    /**
     * The heading lines that open a block, AS THEY ARE WRITTEN in the consigne: its group's title when it opens it, then its own, followed by the level that wrote
     * it in brackets. A section on its own has no group and is written one notch shallower.
     *
     * The level is therefore said twice — in the text the generator reads, and in the split beside it — and that is deliberate: two statements of the same fact
     * that a program can compare catch a divergence neither would show alone. Rebuilt here rather than read back, so that the comparison bites.
     */
    private function headingOf(array $part, ?array $previous): string
    {
        if ($part['group'] === null) {
            return self::GROUP_MARK . $part['title'] . ' (' . $part['level'] . ")\n";
        }
        // A group's title belongs to the first of its blocks, and to it alone: that is what keeps the paving flat, with a single sum to check.
        $opens = $previous === null || ($previous['group'] ?? null) !== $part['group'];

        return ($opens ? self::GROUP_MARK . $part['group'] . "\n" : '') . self::GROUPED_MARK . $part['title'] . ' (' . $part['level'] . ")\n";
    }

    /** A refusal, with the gesture that repairs it — the reader must never be told it is stuck without being told the way out. */
    private function refusal(string $why): array
    {
        return ['body' => null, 'parts' => [], 'fault' => $why
            . ' Solution — refaire le découpage en réassemblant la consigne : « python3 scripts/generate-sprite.py <SUJET> <VARIANTE> » sans --generate, qui'
            . ' n\'engage aucune image.'];
    }
}

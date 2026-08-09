<?php
/**
 * USAGE
 *   require_once'd by hook-stop.php, which calls HookTranscript::get()->operatorSaid($path) and ->lastAgentText($path).
 *
 * INTENTION
 *   A TRANSCRIPT IS A JSONL FILE, AND READING IT IS NOT THE STOP HOOK'S JOB. The hook decides; this reads. Keeping the two apart is what lets the reading be
 *   probed on its own — and it had to be, on 2026-08-09, when a STOP the operator had certainly sent turned out to be nowhere in the file.
 *
 *   A LINE THAT DOES NOT PARSE IS SKIPPED, AND THAT IS DELIBERATE: a transcript is written by another program, live, and its last line may well be half-written
 *   when the hook reads it. That is not a fault of this project and must not stop a turn from ending.
 */

class HookTranscript
{
    private static ?self $instance = null;

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * Everything the operator typed, in order, one message per line. A tool result is also a « user » entry, so only text blocks count — otherwise the hook would
     * read its own output back and find orders in it.
     */
    public function operatorSaid(string $path): string
    {
        return trim(implode("\n", $this->operatorMessages($path)));
    }

    /**
     * The same messages, kept apart instead of joined. Counting them is what tells a message that never arrived from a message that arrived and was misread — the
     * question the whole of 2026-08-09 turned on.
     *
     * @return array<int, string>
     */
    public function operatorMessages(string $path): array
    {
        $said = [];
        $this->shapes = [];
        foreach ($this->entries($path) as $entry) {
            $type = (string) ($entry['type'] ?? '(sans type)');
            $this->note($type, $entry);
            // A MESSAGE SENT WHILE THE AGENT WORKS IS WRITTEN DOWN TOO, UNDER ITS OWN TYPE. It is not a « user » entry and it carries its text in `prompt`, not in
            // message.content — which is why a reader that only knew « user » found nothing and concluded the word had never arrived. Measured on 2026-08-09:
            // the operator's STOP was in the file all along, one field away.
            if ($type === 'attachment') {
                $attachment = $entry['attachment'] ?? [];
                if (is_array($attachment) && ($attachment['type'] ?? '') === 'queued_command') {
                    $queued = trim((string) ($attachment['prompt'] ?? ''));
                    if ($queued !== '') {
                        $said[] = $queued;
                    }
                }
                continue;
            }
            if ($type !== 'user') {
                continue;
            }
            $text = $this->text($entry);
            if ($text !== '') {
                $said[] = $text;
            }
        }

        return $said;
    }

    /**
     * The LAST thing the agent said, and only the last. Reading the whole history found the sentinel word in PREVIOUS turns, so the condition could never be
     * satisfied again and the refusal replayed forever — seen on the first self-test, 2026-08-07.
     */
    public function lastAgentText(string $path): string
    {
        $last = '';
        foreach ($this->entries($path) as $entry) {
            if (($entry['type'] ?? '') !== 'assistant') {
                continue;
            }
            $text = $this->text($entry);
            if ($text !== '') {
                $last = $text;
            }
        }

        return $last;
    }

    /**
     * The entry types met in the last reading, each with the keys it carried, and whether the reader knew what to do with it. NOTHING IS SKIPPED IN SILENCE: an
     * operator message hid for a whole morning behind a type this reader ignored, and no amount of re-reading the code would have shown it — only looking at the
     * object the client actually sends. This is what makes the next unknown carrier visible on the first turn instead of the tenth.
     *
     * @var array<string, string>
     */
    private array $shapes = [];

    /** @return array<string, string> */
    public function shapes(): array
    {
        return $this->shapes;
    }

    /** @return iterable<int, array<string, mixed>> */
    private function entries(string $path): iterable
    {
        $handle = fopen($path, 'r');
        if ($handle === false) {
            throw new RuntimeException("FAUTE le transcrit « {$path} » est illisible");
        }
        while (($line = fgets($handle)) !== false) {
            $entry = json_decode($line, true);
            if (is_array($entry)) {
                yield $entry;
            }
        }
        fclose($handle);
    }

    /** Records the shape of one entry: its type, its keys, and — for an attachment — the kind of thing it carries, which is where a message can hide. */
    private function note(string $type, array $entry): void
    {
        if (isset($this->shapes[$type])) {
            return;
        }
        $keys = implode(', ', array_keys($entry));
        $attachment = $entry['attachment'] ?? null;
        if (is_array($attachment)) {
            $keys .= ' | attachment.' . ((string) ($attachment['type'] ?? '(sans type)'));
        }
        $this->shapes[$type] = $keys;
    }

    /** The text of one entry, whatever shape its content takes. */
    private function text(array $entry): string
    {
        $content = $entry['message']['content'] ?? null;
        if (is_string($content)) {
            return $content;
        }
        if (!is_array($content)) {
            return '';
        }
        $blocks = [];
        foreach ($content as $chunk) {
            if (is_array($chunk) && ($chunk['type'] ?? '') === 'text') {
                $blocks[] = (string) ($chunk['text'] ?? '');
            }
        }

        return implode("\n", $blocks);
    }
}

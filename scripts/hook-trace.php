<?php
/**
 * USAGE
 *   require_once'd by the project hooks, which call HookTrace::get() then write(), arm(), disarm(), armedAt() and clearArmed().
 *
 * INTENTION
 *   THE HOOKS SHARE ONE DIRECTORY AND ONE SET OF GESTURES, and they used to spell them out twice each. Where the state lives, how a line is dated, how the armed
 *   file is written and read: none of that belongs to a particular hook.
 *
 *   UNDER var/, NEVER UNDER local/: local belongs to the agent and the tooling writes nothing there — a file a script drops there has no owner any more. Every
 *   trace of an execution goes under var/, which is local but kept, and never versioned.
 *
 *   THE DIRECTORY CAN BE OVERRIDDEN, AND ONLY A TEST EVER DOES IT. Trying a hook on a few payloads used to ARM THE REAL DEQUEUE — a test writing production
 *   state, and one the agent is forbidden to undo, so it had to be reported to the operator to be cleared. A test says where it writes; production never sets it.
 */

class HookTrace
{
    private static ?self $instance = null;

    private string $directory;

    /** Where the machine's own zone is declared. PHP CLI ignores it and falls back to UTC, which is exactly the trap this reads it to avoid. */
    private const SYSTEM_TIMEZONE = '/etc/timezone';

    private function __construct()
    {
        $this->useSystemTimezone();
        $override = getenv('GATEBEAST_HOOK_DIR');
        $this->directory = $override === false || $override === '' ? dirname(__DIR__) . '/var/hooks' : $override;
        if (!is_dir($this->directory) && !mkdir($this->directory, 0o777, true) && !is_dir($this->directory)) {
            throw new RuntimeException("FAUTE le répertoire d'état « {$this->directory} » n'a pas pu être créé");
        }
    }

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** One dated line appended to the named log. The word that follows the date is the decision itself, so the log reads as a column. */
    public function write(string $log, string $line): void
    {
        $path = $this->directory . '/' . $log;
        if (file_put_contents($path, date('Y-m-d H:i:s') . '  ' . $line . "\n", FILE_APPEND) === false) {
            throw new RuntimeException("FAUTE la trace « {$path} » n'a pas pu être écrite");
        }
    }

    /**
     * EVERY MESSAGE OF THE OPERATOR THAT REACHES A HOOK, WRITTEN DOWN WHOLE (operator, 2026-08-09 : « je veux que tu logs tous mes messages qui passent pour être
     * sûr »). The decision logs say what a hook concluded; this one says what it received, which is a different question and the only one that settles « my word
     * never arrived » against « my word arrived and was misread ».
     *
     * Line breaks become ⏎ so one message stays one line: a log where an entry can span twenty lines cannot be counted, and counting is the whole point.
     */
    public function record(string $source, string $message): void
    {
        $flat = (string) preg_replace('/\R/u', '⏎', $message);
        $this->write('messages-log', sprintf('[%s] %s', $source, $flat));
    }

    /**
     * The shape of one kind of transcript entry, written once and never again. The file becomes the inventory of what the client sends — the thing that was
     * missing on 2026-08-09, when a message sat under `attachment.prompt` and the reader looked for it at the top level.
     */
    public function noteShape(string $type, string $keys): void
    {
        $path = $this->path('shapes-log');
        $known = is_file($path) ? (string) file_get_contents($path) : '';
        if (str_contains($known, "\n" . $type . ' :') || str_starts_with($known, $type . ' :')) {
            return;
        }
        file_put_contents($path, $type . ' : ' . $keys . "\n", FILE_APPEND);
    }

    /** How many operator messages the end-of-turn hook has already written down, so a turn only records the newcomers. */
    public function seen(): int
    {
        $path = $this->path('messages-seen');

        return is_file($path) ? (int) trim((string) file_get_contents($path)) : 0;
    }

    public function rememberSeen(int $count): void
    {
        file_put_contents($this->path('messages-seen'), (string) $count);
    }

    /** Records that the dequeue is armed, at this instant. Only the prompt hook calls it, and only on the operator's GO. */
    public function arm(): void
    {
        if (file_put_contents($this->armedPath(), (string) time()) === false) {
            throw new RuntimeException('FAUTE l\'état d\'armement n\'a pas pu être écrit');
        }
    }

    /** Lifts the armed state. Only the operator's STOP leads here, whichever hook reads it. */
    public function disarm(): void
    {
        if (is_file($this->armedPath())) {
            unlink($this->armedPath());
        }
    }

    /** When the dequeue was armed, or null when it is not armed at all. Throws when the file exists and cannot be read: an unreadable state is a fault. */
    public function armedAt(): ?int
    {
        $path = $this->armedPath();
        if (!is_file($path)) {
            return null;
        }
        $content = file_get_contents($path);
        if ($content === false) {
            throw new RuntimeException("FAUTE l'état d'armement « {$path} » est illisible");
        }

        return (int) trim($content);
    }

    public function path(string $name): string
    {
        return $this->directory . '/' . $name;
    }

    private function armedPath(): string
    {
        return $this->directory . '/dequeue-armed';
    }

    /**
     * THE LOG MUST BE ON THE SAME CLOCK AS EVERYTHING ELSE. PHP CLI runs on UTC unless its ini says otherwise, while the shell hooks it replaced used the machine
     * zone: the migration of 2026-08-09 therefore wrote lines two hours in the past, so the file stopped being chronological and could no longer be read beside
     * var/hooks/prompt-log at all. An unreadable machine zone is reported rather than silently accepted — a log on the wrong clock is worse than no log.
     */
    private function useSystemTimezone(): void
    {
        if (!is_file(self::SYSTEM_TIMEZONE)) {
            fwrite(STDERR, "Le fuseau de la machine n'est pas déclaré (" . self::SYSTEM_TIMEZONE . ") : les traces seront horodatées en UTC.\n");

            return;
        }
        $zone = trim((string) file_get_contents(self::SYSTEM_TIMEZONE));
        if ($zone === '' || !date_default_timezone_set($zone)) {
            fwrite(STDERR, "Le fuseau « {$zone} » est refusé par PHP : les traces seront horodatées en UTC.\n");
        }
    }
}

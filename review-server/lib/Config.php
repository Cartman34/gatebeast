<?php
/**
 * USAGE
 *   Read what this machine has to be told: `Config::get()->value('port')`, `Config::get()->path('browser')` for a value that names a file. One file, read once, whatever asks for it.
 *
 * INTENTION
 *   ONE READER, SO THAT THE FILE IS NEVER READ TWICE. Two services opening the same configuration is the copy this whole family exists to prevent — and it was about to happen: the address service had
 *   grown a method handing out the path of the browser, which is none of its business, purely because it was the one that already had the file open. The name of a service must say what it holds.
 *
 *   IT RESOLVES `~`, AND THAT IS AN OPERATION, NOT A DETAIL: the file carries no home directory of anyone's, so it stays true on another machine, and the expansion happens at the one moment the value
 *   has to be a real path. A caller doing it itself would do it slightly differently, which is how two spellings of the same path come to exist.
 *
 *   A MISSING KEY STOPS EVERYTHING AND NAMES ITSELF. A configuration silently falling back on a value typed into the code is the transparent error this project forbids: the tool would go on working
 *   at an address nobody serves, and a page that never loads looks exactly like a page that has nothing to show.
 */

class Config
{
    private static ?self $instance = null;

    /** Where this machine's settings live, relative to the repository root. Named here because the fault messages have to say it, and because the Python probe reads the same path. */
    public const PATH = 'review-server/config.json';

    private array $values;

    public function __construct()
    {
        $path = dirname(__DIR__, 2) . '/' . self::PATH;
        if (!is_file($path)) {
            throw new RuntimeException('la configuration est absente : ' . self::PATH);
        }
        $this->values = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** One configured value, or a fault naming the key that was missing. */
    public function value(string $key): mixed
    {
        if (!isset($this->values[$key])) {
            throw new RuntimeException("la clé « {$key} » manque dans " . self::PATH . ' — l\'outillage ne peut pas deviner ce qu\'elle vaut.');
        }
        return $this->values[$key];
    }

    /** One configured value that names a file, its leading `~` expanded. */
    public function path(string $key): string
    {
        $value = (string) $this->value($key);
        if (!str_starts_with($value, '~/')) {
            return $value;
        }
        $home = getenv('HOME');
        if ($home === false || $home === '') {
            throw new RuntimeException("la clé « {$key} » commence par « ~ » et HOME est vide — impossible de la résoudre.");
        }
        return $home . substr($value, 1);
    }
}

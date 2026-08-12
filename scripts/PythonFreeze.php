<?php
/**
 * USAGE
 *   require_once __DIR__ . '/PythonFreeze.php'; then PythonFreeze::get()->present(), ->frozen(), ->added(), ->freeze() — which Python files the repository
 *   tracks, which ones the roll allows, and which ones are new. Used by scripts/check-no-new-python.php, which refuses the new ones.
 *
 * INTENTION
 *   ONE PLACE KNOWS WHAT « A PYTHON FILE OF THIS REPOSITORY » MEANS, so the check and its trial ask it rather than each holding a reading of their own. The two
 *   would answer differently the day one of them learns about a directory, and the check would then guard a set its trial never exercises.
 *
 *   THE SET IS READ OFF THE VERSIONING, NEVER OFF THE DISK. What the rule forbids is ADDING Python to the project, and a file becomes part of the project when
 *   it is tracked — before that it is a draft in a working tree, which the agent is free to write and throw away. Reading the disk instead would refuse the
 *   scratch file `local/` exists to hold, and a check that fires on what the repository explicitly allows is a check somebody switches off.
 */

class PythonFreeze
{
    private static ?self $instance = null;

    /** Where the roll lives. Versioned, because a roll that only exists on one machine guards only that machine. */
    public const ROLL = 'scripts/python-inventory.json';

    private string $root;
    private ?array $present = null;

    public function __construct(?string $root = null)
    {
        $this->root = $root ?? dirname(__DIR__);
    }

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * The Python files the repository tracks right now, sorted.
     *
     * IT RAISES WHEN IT CANNOT ASK, and does not fall back to an empty list: no answer read as « no Python file » would make the check announce that everything
     * is in order precisely when it was unable to look — the silent pass this repository forbids by name.
     */
    public function present(): array
    {
        if ($this->present === null) {
            exec(sprintf('git -C %s ls-files -- "*.py" 2>&1', escapeshellarg($this->root)), $lines, $status);
            if ($status !== 0) {
                throw new RuntimeException("git ne répond pas dans {$this->root} — le relevé des fichiers Python ne peut pas être établi : " . implode("\n", $lines));
            }
            sort($lines);
            $this->present = $lines;
        }

        return $this->present;
    }

    /** The roll: the Python files that existed when it was last frozen, and which are therefore allowed to stay. */
    public function frozen(): array
    {
        $path = $this->root . '/' . self::ROLL;
        if (!is_file($path)) {
            throw new RuntimeException(self::ROLL . " manque — le relevé des fichiers Python n'existe pas, lancez « php scripts/check-no-new-python.php --freeze ».");
        }
        $data = json_decode((string) file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        if (!isset($data['files']) || !is_array($data['files'])) {
            throw new RuntimeException(self::ROLL . " ne porte pas de liste « files » — le relevé est illisible, il ne se devine pas.");
        }

        return $data['files'];
    }

    /**
     * The Python files present today that the roll does not allow — the whole verdict of the rule.
     *
     * A FILE THAT LEFT THE ROLL IS NOT A FAULT AND IS NOT REPORTED. The rule is that Python does not GROW; it may shrink freely, and a deletion needs no
     * ceremony. Comparing both ways would turn every legitimate removal into a red check and make refreezing a chore, which is how the roll would end up
     * refrozen by reflex — the one gesture that must stay deliberate.
     */
    public function added(): array
    {
        return array_values(array_diff($this->present(), $this->frozen()));
    }

    /** Writes the roll from what the repository tracks today. Nothing else in this class writes. */
    public function freeze(): array
    {
        $files = $this->present();
        $data = [
            '_intention' => "Les fichiers Python que ce dépôt porte, figés. PHP est le langage de l'outillage : aucun fichier Python neuf ne s'ajoute, et "
                . "scripts/check-no-new-python.php refuse ceux qui n'ont pas leur ligne ici. Refiger est un geste que l'opérateur autorise, jamais une "
                . "commodité qu'on s'accorde pour faire passer un ajout — un relevé qu'on refige à volonté ne garde rien.",
            'frozen_on' => date('Y-m-d'),
            'files' => $files,
        ];
        file_put_contents($this->root . '/' . self::ROLL, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");

        return $files;
    }
}

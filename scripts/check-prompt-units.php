<?php
/**
 * USAGE
 *   php scripts/check-prompt-units.php            the verdict: how many pixel units and image ratios the consigne sources carry outside the socle
 *   php scripts/check-prompt-units.php <file>...  the same, on the files given instead of the default scope — a .json is read as the subject referential, anything else line by line
 *   php scripts/check-prompt-units.php -v         each find, with the rule it breaks and the file and the line or the key that carries it
 *   php scripts/check-prompt-units.php -h|--help  this text
 *
 * INTENTION
 *   A SHEET SPEAKS IN TILES, AND THE PROJECTION BELONGS TO THE SOCLE ALONE, scripts/asset_common.py. Two rules follow from that one fact, and this holds both. They live, with their reasons, at
 *   doc/conception/referentiels/visuel/assets/ecriture-des-consignes.md, « LES MESURES SE DISENT EN CASES ».
 *
 *   THE PIXEL (opérateur, 2026-08-12 : « les calculs de mesure en PX sont interdits dans les descriptions », puis « strictement interdit »). A pixel is the product of a projection the socle already
 *   owns, interpolated there from scripts/tile_scale.py. A sheet that converts freezes a copy of that projection, which drifts the day the scale moves, and it can apply the wrong factor — « 96 pixels
 *   de haut » was written for a two-tile door by using the ground scale on a height. Nothing in the image ever says so: the generator obeys the figure, and the sheet keeps looking right.
 *
 *   THE IMAGE RATIO, and it is the graver of the two because it cost generations on the day it was found. Under this camera a standing height is halved while a width is not, so a door of two tiles by
 *   one appears SQUARE. BT-002 read « deux fois plus haute que large, nettement, et non une ouverture presque carrée »: the sentence forbade the correct result and commanded an elevation, and since
 *   the sheet sized the whole building on that door, it tipped the entire image. BT-001 and TR-065 carried the same fault.
 *
 *   EACH RULE LOOKS FOR WHAT IS UNAMBIGUOUS, AND NOTHING ELSE — noise is what switches a checker off. `px` inside a word is a word, so a letter on either side disqualifies it while a digit does not:
 *   « 96px » is exactly the forbidden form. A ratio is caught by its COMPARISON, « fois plus … que … » and « plus … que … », never by « carré » — see IMAGE_RATIO for why that word is left alone.
 *
 *   WHAT IT DELIBERATELY LEAVES OUT, and the two are said here so nobody widens it by surprise. The SOCLE is out of scope by the rule itself. The ASSEMBLER, scripts/generate-sprite.py, is left out
 *   because it does not convert by hand either: like the socle it interpolates from tile_scale, so it duplicates nothing — what it emits is reported to the operator rather than gated here.
 *
 *   In PHP because it is the project's default language for durable tooling, and this needs no library that only Python has.
 */

require_once __DIR__ . '/bootstrap.php';

bootCommand($argv);

/** The consigne sources a subject author writes, and the only ones. The socle is excluded by the rule; the assembler by the intention above. */
const DESCRIPTIONS = 'assets/descriptions';
const REFERENTIAL = 'assets/subjects.json';

/**
 * A pixel unit, and nothing that merely contains its letters. A digit before the token is kept on purpose — « 96px » is a measure — while a letter on either side
 * makes it part of a word: « pixelisé » names a style, not a length, and « PXL-002 » is a code.
 */
const PIXEL_UNIT = '/(?<!\p{L})(px|pixels?)(?!\p{L})/iu';

/**
 * A ratio OF THE IMAGE, which no sheet may state: « deux fois plus haute que large », « plus haut que large ». The comparison is what gives it away, and it is
 * unambiguous — a sheet comparing its subject's two dimensions is describing what the drawing must look like, never the thing itself.
 *
 * « CARRÉ » IS DELIBERATELY NOT MATCHED, though the rule forbids it too. The word legitimately describes a thing OF THE WORLD — a tile is a square metre, a slab
 * can be square — and nothing in the sentence separates that use from the forbidden one. Matching it would cry on what is right, which is how a checker gets
 * switched off; the comparative forms carry the same fault and carry it without ambiguity.
 */
const IMAGE_RATIO = '/(?:fois plus (?:haute?|large)|plus haute? que (?:large|haute?)|plus large que (?:haute?|large))(?!\p{L})/iu';

/** The two families, named as they are reported. A find says which rule it breaks, because the two are not repaired the same way. */
const RULES = ['unité de pixel' => PIXEL_UNIT, 'rapport visuel' => IMAGE_RATIO];

/**
 * Keys of the referential that carry no consigne. A leading underscore marks a comment written for whoever edits the file, and « representations » holds what came
 * BACK from a generation — file paths, verdicts, the operator's own words — never what is asked of it.
 */
const REPRESENTATIONS_KEY = 'representations';

$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
$paths = array_values(array_filter(array_slice($argv, 1), fn (string $argument): bool => !str_starts_with($argument, '-')));

/** The excerpt shown for a find: enough of the line to recognise it, never the whole clause. */
function excerpt(string $text): string
{
    $flat = trim(preg_replace('/\s+/u', ' ', $text));

    return mb_strlen($flat) > 120 ? mb_substr($flat, 0, 117) . '…' : $flat;
}

/** Every fault a text file carries, as « path:line — rule — excerpt ». A line breaking both rules is reported once per rule: the two are repaired differently. */
function findInText(string $path): array
{
    $found = [];
    foreach (file($path, FILE_IGNORE_NEW_LINES) as $index => $line) {
        foreach (RULES as $rule => $pattern) {
            if (preg_match($pattern, $line) === 1) {
                $found[] = sprintf('%s:%d — %s — « %s »', $path, $index + 1, $rule, excerpt($line));
            }
        }
    }

    return $found;
}

/** Every fault the subject referential carries, as « path — key — rule — excerpt ». Walks the values, so a key is named by its path in the tree. */
function findInReferential(string $path): array
{
    $data = json_decode((string) file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
    $found = [];
    $walk = function ($node, string $key) use (&$walk, &$found, $path): void {
        if (is_string($node)) {
            foreach (RULES as $rule => $pattern) {
                if (preg_match($pattern, $node) === 1) {
                    $found[] = sprintf('%s — %s — %s — « %s »', $path, $key, $rule, excerpt($node));
                }
            }

            return;
        }
        if (!is_array($node)) {
            return;
        }
        foreach ($node as $name => $value) {
            if (is_string($name) && (str_starts_with($name, '_') || $name === REPRESENTATIONS_KEY)) {
                continue;
            }
            $walk($value, $key . '/' . $name);
        }
    };
    $walk($data, '');

    return $found;
}

/** The files swept when none is given: every sheet, plus the referential. */
function defaultScope(string $root): array
{
    $files = [];
    foreach (scandir($root . '/' . DESCRIPTIONS) as $name) {
        if (str_ends_with($name, '.md')) {
            $files[] = DESCRIPTIONS . '/' . $name;
        }
    }
    sort($files);
    $files[] = REFERENTIAL;

    return $files;
}

$root = dirname(__DIR__);
if (!$paths) {
    chdir($root);
    $paths = defaultScope($root);
}

$found = [];
foreach ($paths as $path) {
    if (is_dir($path)) {
        foreach (scandir($path) as $name) {
            if (str_ends_with($name, '.md')) {
                $found = array_merge($found, findInText(rtrim($path, '/') . '/' . $name));
            }
        }
        continue;
    }
    if (!is_file($path)) {
        // An absent file is not a clean file: saying nothing here would be a check answering « tout va bien » on what it could not read at all.
        throw new RuntimeException("ABSENT : {$path} — la source de consigne à contrôler n'existe pas.");
    }
    $found = array_merge($found, str_ends_with($path, '.json') ? findInReferential($path) : findInText($path));
}

$byRule = [];
foreach (array_keys(RULES) as $rule) {
    $byRule[] = sprintf('%d %s', count(array_filter($found, fn (string $line): bool => str_contains($line, " {$rule} — "))), $rule);
}
printf("%d source(s) de consigne : %d écart(s) — %s.\n", count($paths), count($found), implode(', ', $byRule));
if ($detail) {
    foreach ($found as $line) {
        printf("  %s\n", $line);
    }
} elseif ($found) {
    echo "« -v » les nomme.\n";
}

exit($found ? 1 : 0);

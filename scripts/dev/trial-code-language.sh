#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/trial-code-language.sh            feeds the language checker the cases it must report and the ones it must ignore, and reports
#   bash scripts/dev/trial-code-language.sh -h|--help  this text
#
#   Writes only under var/tmp/ and reads no file of the project. Exits non-zero as soon as one case answers the wrong way.
#
# INTENTION
#   THE CHECKER'S SILENCE IS AS LOAD-BEARING AS ITS NOISE, AND ONLY ONE OF THE TWO EVER GETS TESTED. What it reports is visible; what it stops reporting is not,
#   so a heuristic that quietly starts swallowing real finds looks exactly like a codebase that got cleaner. Three of them were written on 2026-08-12 — a block
#   comment followed from line to line, a line of markup read for its code only, a regular expression left alone — and each one buys quiet at the price of a
#   possible blind spot. This is what keeps that price honest: every case below states which way the answer must go, and the file is the whole input.
#
#   IT EXISTS BECAUSE THE CHECKER HAD ALREADY BEEN SWITCHED OFF ONCE for crying on what it announced it ignored, and the repair is a second chance to get it
#   wrong in the other direction. A checker nobody trusts and a checker that finds nothing are the same checker.

set -u
repo="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$repo/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

sample="$repo/var/tmp/trial-code-language/sample.php"
mkdir -p "$(dirname "$sample")"
cat > "$sample" <<'PHP'
<?php
/* Un commentaire de bloc qui parle de largeur et de hauteur ; il ne doit rien lever. */
/* Deuxième ligne d'un bloc :
   la largeur et le fichier y sont cités, et la ponctuation ; ne change rien. */
echo "<p class=\"lede\">Ce que le monde contient, sujet par sujet, avec sa hauteur.</p>";
preg_match('/hauteur\s+(\d+)\s+cases?/u', $text, $found);
$statut = 'courante';
$point['libelle'] = 'x';
$page = <<<HTML
  <span class="etat">{$statut}</span>
HTML;
?>
<style>
  .point[data-statut="done"] { opacity: .55; }
</style>
PHP

# A SECOND SAMPLE, IN SHELL, because the rule is not the same there: a heredoc is a payload a script hands to another command, not code it runs. Its own marker
# differs from the one wrapping it, or the outer heredoc would close on the inner one's.
shell_sample="$repo/var/tmp/trial-code-language/sample.sh"
cat > "$shell_sample" <<'SHELL'
#!/usr/bin/env bash
cat > /tmp/x.php <<'PAYLOAD'
$statut = 'courante';
$point['libelle'] = 'x';
PAYLOAD
libelle="ce qui est hors du heredoc reste du code"
SHELL

report="$repo/var/tmp/trial-code-language/report.txt"
python3 "$repo/scripts/check-code-language.py" "$sample" "$shell_sample" -v > "$report" 2>&1 || true

failures=0

expect() {
    local how="$1" what="$2" pattern="$3"
    if [ "$how" = "reported" ]; then
        if grep -q "$pattern" "$report"; then
            printf 'OK    signalé — %s\n' "$what"
        else
            printf 'RATÉ  aurait dû être signalé — %s\n' "$what"
            failures=$((failures + 1))
        fi
    elif grep -q "$pattern" "$report"; then
        printf 'RATÉ  aurait dû se taire — %s\n' "$what"
        failures=$((failures + 1))
    else
        printf 'OK    tu — %s\n' "$what"
    fi
}

# EVERY PATTERN NAMES ITS SAMPLE, because two files are read now and a bare line number matches in either. « :6 » alone found sample.sh's line 6, which is
# reported on purpose, and declared the regular-expression case broken while it was passing.
printf 'Ce que le contrôle doit taire\n'
expect silent "un commentaire de bloc, sur sa première ligne" 'sample.php:2 —'
expect silent "la continuation d un commentaire de bloc" 'sample.php:4 —'
expect silent "la prose derrière une balise" 'sample.php:5 —'
expect silent "un motif qui lit de la prose française" 'sample.php:6 —'

printf 'Ce que le contrôle doit signaler\n'
expect reported "une valeur comparée en français" "sample.php:7 .*courante"
expect reported "une variable en français" "sample.php:7 .*statut"
expect reported "une clé de données en français" "sample.php:8 .*libelle"
expect reported "une variable interpolée dans du balisage" "sample.php:10 .*statut"
expect reported "un attribut de données en français, en CSS" "sample.php:14 .*statut"

printf 'En shell, un heredoc est une charge utile et non du code\n'
expect silent "le français à l intérieur d un heredoc shell" 'sample.sh:3'
expect silent "une clé française à l intérieur d un heredoc shell" 'sample.sh:4'
expect reported "une variable française HORS du heredoc" 'sample.sh:6 .*libelle'

printf '\n'
if [ "$failures" -eq 0 ]; then
    printf 'Le contrôle de langue signale ce qu il doit et se tait sur ce qu il annonce ignorer.\n'
    exit 0
fi
printf '%d cas répondent à l envers.\n' "$failures"
exit 1

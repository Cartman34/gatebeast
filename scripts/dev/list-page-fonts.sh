#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/list-page-fonts.sh — for every commit that touched the sprites review page, prints the font its body carried at that point.
#   bash scripts/dev/list-page-fonts.sh -h|--help — this text
#
# INTENTION
#   « La police est restée changée, pour moi tu n'as pas vraiment bien restauré » (operator, 2026-08-11). Which font the page must come back to is a fact of the
#   repository, not a memory: the same mistake was already made once today by trusting the last builder instead of reading the history. This reads the body rule
#   out of each version and prints it, so the answer is looked up rather than believed.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$REPO/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

cd "$REPO"

CANDIDATES="artefacts/suivi-sprites/page.html artefacts/suivi-sprites/build.py"
CANDIDATES="$CANDIDATES review-server/suivi-sprites/page.html review-server/suivi-sprites/page.css"

for commit in $(git log --format=%h -- artefacts/suivi-sprites review-server/suivi-sprites); do
    date=$(git show -s --format=%ad --date=short "$commit")
    subject=$(git show -s --format=%s "$commit")
    printf '\n== %s  %s  %s\n' "$commit" "$date" "$subject"
    for candidate in $CANDIDATES; do
        content=$(git show "$commit:$candidate" 2>/dev/null || true)
        [ -n "$content" ] || continue
        found=$(printf '%s\n' "$content" | grep -oE -- 'font-family: *[^;]{0,70}|font: *[0-9][^;]{0,60}' | head -3 | tr '\n' '|' || true)
        [ -n "$found" ] || continue
        printf -- '   %-44s %s\n' "$candidate" "$found"
    done
done

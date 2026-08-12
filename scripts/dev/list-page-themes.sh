#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/list-page-themes.sh — for every commit that touched the sprites review page, prints its date, its subject, and the page's ground colour as
#   it stood then. Read it to find WHICH past theme is meant, instead of assuming the last one is the right one.
#   bash scripts/dev/list-page-themes.sh -h|--help — this text
#
# INTENTION
#   Restoring « the theme from before » requires knowing which themes ever existed, and when. Guessing from the last deleted builder was wrong (operator,
#   2026-08-11: « il y avait un thème avant celui là, je veux le récupérer !!! »). This walks the history and reports the palette at each step, so the answer is
#   read off the repository rather than believed. The BUILT page is read first when it exists: it carries the style that was actually served that day.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$REPO/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

cd "$REPO"

CANDIDATES="artefacts/suivi-sprites/page.html artefacts/suivi-sprites/build.py artefacts/revue-sprites.html"
CANDIDATES="$CANDIDATES review-server/suivi-sprites/page.html review-server/lib/themes/origine.css review-server/lib/themes/encre.css"

for commit in $(git log --format=%h -- artefacts/suivi-sprites artefacts/revue-sprites.html review-server/suivi-sprites review-server/lib/themes); do
    date=$(git show -s --format=%ad --date=short "$commit")
    subject=$(git show -s --format=%s "$commit")
    printf '\n== %s  %s  %s\n' "$commit" "$date" "$subject"
    for candidate in $CANDIDATES; do
        content=$(git show "$commit:$candidate" 2>/dev/null || true)
        [ -n "$content" ] || continue
        colour='#[0-9A-Fa-f]{3,8}'
        wanted="--ground: *$colour|--bg: *$colour|--surface: *$colour|--card: *$colour|--ink: *$colour|--key: *$colour|--accent: *$colour"
        found=$(printf '%s\n' "$content" | grep -oE -- "$wanted" | head -6 | tr '\n' ' ' || true)
        [ -n "$found" ] || continue
        printf -- '   %-46s %s\n' "$candidate" "$found"
    done
done

#!/usr/bin/env bash
# Usage: bash scripts/dev/show-language-debt.sh — the French findings of the versioned tooling, in full, without the agent's throwaway directory.
#        bash scripts/dev/show-language-debt.sh -h|--help — this text
#
# Intention: the checker sweeps three directories at once and `local/scripts/` carries nine tenths of the findings, which buries the debt that actually has to be
# paid. Passing a directory to the checker makes it treat it as a single file and it finds nothing, so the file list is expanded here instead.
#
# THE OPTION IS `-v`, AND IT WAS `--detail` HERE UNTIL THE CHECKER RENAMED IT. The old spelling did not fail: the checker takes anything that is not an option as
# a file to read, so `--detail` became a path that does not exist, was skipped in silence, and the listing this script exists for simply never came out. A flag
# that turns into a target rather than an error is the quietest way for a tool to stop doing its job.
set -euo pipefail
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")/../.." && pwd)/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

cd "$(dirname "$0")/../.."
# shellcheck disable=SC2046
python3 scripts/check-code-language.py $(git ls-files 'scripts/*' 'review-server/*') -v

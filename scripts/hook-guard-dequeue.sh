#!/usr/bin/env bash
# Usage: declared as a PreToolUse hook in .claude/settings.json, on Bash, Write and Edit. Reads the hook payload on stdin and refuses, with exit code 2, any call
# that would erase, move, rewrite or neutralise the dequeue armed state — or this guard itself. Anything else passes through untouched.
#
# Intention: THE AGENT MUST NOT BE ABLE TO DISARM ITS OWN GUARD. On 2026-08-08 the agent deleted var/hooks/dequeue-armed by itself, reasoning that an operator
# interruption had consumed the GO. The reasoning was about its own conduct and it was not wrong there — but the state file is the OPERATOR's control, not the
# agent's: GO arms it, STOP disarms it, and it expires on its own. An agent that can remove the file can end its own dequeue at any moment, silently, and the
# guard becomes a suggestion. The operator's words: « supprimer le dépilement est strictement interdit, tu dois t'empêcher de pouvoir le faire. »
#
# It guards itself for the same reason: a guard the agent can rewrite is a guard the agent can remove in two steps instead of one. The operator edits both freely
# — nothing here binds a human, and hooks are not a security boundary. This closes the path an agent takes by accident, while reasoning its way to it.

set -u
payload=$(cat)

read -r -d '' verdict <<'PYTHON' || true
import json, re, sys

payload = json.load(sys.stdin)
name = payload.get("tool_name", "")
args = payload.get("tool_input", {}) or {}

# WHAT IS PROTECTED: the armed state the GO writes, and this guard's own script. Named by their tail, never by an absolute path — the repository is cloned to
# different places, and a path written here would stop matching the day someone moves it.
GUARDED = ("var/hooks/dequeue-armed", "hook-guard-dequeue.sh")

def refuse(what):
    print(what, file=sys.stderr)
    sys.exit(2)

if name in ("Write", "Edit", "NotebookEdit"):
    target = str(args.get("file_path", ""))
    if any(g in target for g in GUARDED):
        refuse("REFUSÉ — « %s » tient l'armement du dépilement ou la garde qui le protège. Seul le STOP de l'opérateur désarme, jamais l'agent." % target)
    sys.exit(0)

if name != "Bash":
    sys.exit(0)

command = str(args.get("command", ""))
if not any(g in command for g in GUARDED) and "var/hooks" not in command:
    sys.exit(0)

# READING IS ALWAYS FINE, and the agent needs it: it reports whether the dequeue is armed. Only what CHANGES the file is refused, so the check looks for the verbs
# that write rather than trying to recognise the ones that read — an unknown command must fall on the safe side, not slip through.
WRITES = r"(\brm\b|\brmdir\b|\bmv\b|\bunlink\b|\bshred\b|\btruncate\b|\btee\b|\bchmod\b|\bchown\b|-delete\b|\bsed\b[^|]*-i|>)"
if re.search(WRITES, command):
    refuse(
        "REFUSÉ — cette commande touche à l'armement du dépilement (var/hooks/dequeue-armed) ou à la garde qui le protège.\n"
        "CE FICHIER N'APPARTIENT PAS À L'AGENT, DANS AUCUN DES DEUX SENS. Le GO de l'opérateur l'arme, son STOP le désarme, il expire seul au bout de trois heures,\n"
        "et le hook du prompt est le seul à l'écrire. L'agent ne le supprime pas — il s'affranchirait de sa propre garde. Il ne le crée pas non plus — il se donnerait\n"
        "un ordre que l'opérateur n'a pas donné.\n"
        "TU N'AS AUCUNE RAISON D'Y TOUCHER : ton arrêt sur interruption est une règle de CONDUITE, elle ne te demande pas de mettre l'état à jour ; et un hook qui\n"
        "n'arme pas est un défaut à constater et à inscrire à la pile, jamais à compenser à la main. Dis-le à l'opérateur, ne le contourne pas."
    )
sys.exit(0)
PYTHON

printf '%s' "$payload" | python3 -c "$verdict"
exit $?

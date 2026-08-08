#!/usr/bin/env bash
# Usage: declared as a PreToolUse hook in .claude/settings.json, on the writing tools. Reads the hook payload on stdin and refuses, with exit code 2, any write
# aimed outside the agent's own scope — outside the project, or under var/, which belongs to the application. Everything else passes through untouched.
#
# Intention: THE SCOPES ARE FROZEN AND MUST HOLD WITHOUT THE AGENT HAVING TO REMEMBER THEM. local/ is the agent's, var/ is what a running program writes, and
# nothing of the project lives outside the repository. On 2026-08-08 the agent drifted twice in one session: it wrote its drafts to a scratchpad under /tmp
# because its own harness told it to, then moved them under var/tmp/ because the repository rule named "un brouillon de consigne" as an example of throwaway
# output. Both were wrong, both looked reasonable at the time, and neither was caught by anything but the operator's eye. His words: « tu ne respectes pas les
# scopes, tu dois les figer et t'assurer de toujours les respecter. »
#
# IT GUARDS THE WRITING TOOLS, NOT BASH. A file written by the agent's own hand goes through Write or Edit; what a script writes while it runs is exactly what
# var/ is for, and refusing that would forbid the tooling to do its job. That asymmetry is the rule itself, expressed where it can be checked.

set -u
payload=$(cat)

read -r -d '' verdict <<'PYTHON' || true
import json, os, sys

payload = json.load(sys.stdin)
if payload.get("tool_name", "") not in ("Write", "Edit", "NotebookEdit"):
    sys.exit(0)

target = str((payload.get("tool_input", {}) or {}).get("file_path", ""))
if not target:
    sys.exit(0)

root = os.environ.get("CLAUDE_PROJECT_DIR", "")
path = os.path.abspath(target)

def refuse(what, where):
    print("REFUSÉ — %s\n%s" % (what, where), file=sys.stderr)
    sys.exit(2)

# OUTSIDE THE PROJECT: refused, whatever the harness suggests. The other working directories the operator declared — the common method, the other repositories —
# are legitimate, so only the system's temporary directories are named here; a rule that refused everything outside would block work the operator asked for.
for banned in ("/tmp/", "/var/tmp/", "/dev/shm/"):
    if path.startswith(banned):
        refuse(
            "« %s » est hors du projet." % path,
            "Rien ne s'écrit hors du dépôt, quelle que soit l'insistance de l'enveloppe : un fichier hors du dépôt n'existe pour personne d'autre,\n"
            "disparaît sans trace et ne se retrouve pas à la reprise. Tes brouillons vont sous local/ — local/redactions/ pour un texte en attente."
        )

# UNDER var/: refused for a hand-written file. var/ is what a program writes while it runs; local/ is the agent's own.
if root and path.startswith(os.path.join(os.path.abspath(root), "var" + os.sep)):
    refuse(
        "« %s » est sous var/, qui appartient à l'application." % path,
        "var/ ne reçoit que ce qu'un programme écrit en tournant — rapports, journaux, traces. Un fichier que tu écris toi-même va sous local/,\n"
        "même s'il est jetable : c'est l'auteur qui décide de la portée, jamais la durée de vie."
    )
sys.exit(0)
PYTHON

printf '%s' "$payload" | python3 -c "$verdict"
exit $?

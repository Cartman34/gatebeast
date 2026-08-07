#!/usr/bin/env python3
"""A production queue for sprites: requests pile up, run in parallel, and each one is exported and
published to the review page the moment it lands — the queue never waits for the rest of the batch.

USAGE
  python3 scripts/sprite-queue.py add <requests.json>   # a JSON list of request dicts
  python3 scripts/sprite-queue.py run [--workers N]      # drain the queue continuously
  python3 scripts/sprite-queue.py status                 # print how many requests are in each state

A request dict is one of:
  {"kind": "subject", "code": "TR-063", "reference": "path/relative.png" | None}
  {"kind": "trace",   "code": "OB-010", "shape": "ns", "posts": 1, "reference": "..." | None}

INTENTION
  Ordering a sprite used to mean calling the generator by hand, one code at a time, then waiting for
  the whole batch to finish before anything could be checked. This tool inverts that: requests are
  queued once, several run at a time, and each image is exported and shown as soon as it exists —
  nothing here waits on its neighbours, and adding more requests never means starting over.

  The queue itself lives at local/sprite-queue.jsonl, one JSON object per line rather than one JSON
  array, because a line is self-contained: two processes writing at once can each finish their own
  line without the other's half-written array corrupting the file. Every read-modify-write on that
  file still goes through a single OS lock (see _locked_queue) — the JSONL format is a second line of
  defence, not a replacement for actually serializing access.

WHAT "run" ACTUALLY CHAINS, PER REQUEST
  1. scripts/generate-sprite-subject.py <code> [--ref R] --generate, or
     scripts/generate-sprite-trace.py <code> <shape> --posts N [--ref R] --generate
  2. scripts/export-asset.py <the image the step above produced>
  3. php review-server/suivi-sprites/build.php

  Steps 2 and 3 run right after step 1 lands for THAT request, not once the whole queue is empty.
  Step 3 touches one shared page, so it is the one step this script serializes across workers — step
  1 and step 2 stay fully parallel.

  Each request's step 1 is its own OS subprocess (see _generate_command / _run_entry): "run" spawns up
  to --workers of them at once, one thread per in-flight request driving one subprocess.run each, so a
  slow or crashing generation never blocks or brings down its neighbours.

TESTING WITHOUT SPENDING A REAL GENERATION
  Set SPRITE_QUEUE_TEST_GENERATOR to the path of a stand-in script before calling "run", and step 1
  invokes that script instead of the real generator (see _generate_command). Production never sets
  this variable.
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import threading
import uuid
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE_PATH = REPO / "local" / "sprite-queue.jsonl"
LOCK_PATH = QUEUE_PATH.with_suffix(".lock")


@contextmanager
def _locked_queue():
    """Hold an exclusive OS lock across one read-modify-write cycle on the queue file.

    The queue file is touched by "add", by "status" and by every worker thread inside "run", possibly
    from several processes at once — an operator can queue more requests while the queue is draining.
    Locking the whole read-modify-write cycle, not just the final write, is what stops two writers
    from computing their new content from the same stale snapshot and one silently erasing the
    other's update.
    """
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_PATH, "w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _read_entries_unlocked() -> list[dict]:
    if not QUEUE_PATH.is_file():
        return []
    entries = []
    for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def _write_entries_unlocked(entries: list[dict]) -> None:
    # Written to a sibling file and swapped in with one rename, so a reader outside this script's own
    # locking discipline (a human "cat", an editor) never observes a half-written file either.
    tmp = QUEUE_PATH.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries),
                    encoding="utf-8")
    tmp.replace(QUEUE_PATH)


def _read_entries() -> list[dict]:
    with _locked_queue():
        return _read_entries_unlocked()


def _update_entry(entry_id: str, **changes) -> None:
    """Apply changes to exactly the one row with this id, leaving every other row untouched.

    Rewriting the whole file for a single field change is cheap at this queue's scale and keeps the
    format flat (append-only rows plus in-place edits), rather than growing a second index file just
    to avoid it.
    """
    with _locked_queue():
        entries = _read_entries_unlocked()
        for entry in entries:
            if entry["id"] == entry_id:
                entry.update(changes)
                break
        _write_entries_unlocked(entries)


def enqueue(requests: list[dict]) -> int:
    """Ajoute des demandes à la file et rend le nombre ajouté."""
    fresh = []
    for request in requests:
        entry = dict(request)
        entry.setdefault("reference", None)
        # "code" alone is not a stable handle: the same code can be requeued after a failure, so each
        # row gets its own id to be updated by, independent of what it is a request for.
        entry["id"] = uuid.uuid4().hex
        entry["state"] = "pending"
        entry["image"] = None
        fresh.append(entry)
    with _locked_queue():
        entries = _read_entries_unlocked()
        entries.extend(fresh)
        _write_entries_unlocked(entries)
    return len(fresh)


def _log(code: str, event: str) -> None:
    # Flushed explicitly: a worker can sit inside a fifteen-minute generation, and the operator
    # watching this output needs every prior event visible immediately, not buffered until exit.
    print(f"{code} {event}", flush=True)


def _tail(text: str | None) -> str:
    """The last non-blank line of a tool's output — usually the one line that names what went wrong."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _fail(entry: dict, reason: str, image: str | None = None) -> None:
    changes = {"state": "failed", "error": reason}
    if image is not None:
        changes["image"] = image
    _update_entry(entry["id"], **changes)
    _log(entry["code"], f"ÉCHEC {reason}")


def _find_image_path(stdout: str) -> str | None:
    """The exact path the generator tool printed right before calling its own image generator."""
    prefix = "génération vers "
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def _generate_command(entry: dict) -> list[str]:
    """The subprocess command for one entry's generation step.

    SPRITE_QUEUE_TEST_GENERATOR, when set, names an executable substituted for the real generator —
    invoked with (kind, code) instead of the real tool's own arguments. This exists solely to prove
    this queue's process-level parallelism (a real, distinct OS process per request, several running
    at once) without spending a real, costly generation on every proof run; production runs never set
    the variable, so this branch never fires for them.
    """
    reference = entry.get("reference")
    ref_args = ["--ref", str(REPO / reference)] if reference else []
    test_generator = os.environ.get("SPRITE_QUEUE_TEST_GENERATOR")
    if test_generator:
        return ["python3", test_generator, entry["kind"], entry["code"]]
    if entry["kind"] == "subject":
        return ["python3", str(REPO / "scripts" / "generate-sprite-subject.py"), entry["code"],
                *ref_args, "--generate"]
    if entry["kind"] == "trace":
        return ["python3", str(REPO / "scripts" / "generate-sprite-trace.py"), entry["code"],
                entry["shape"], "--posts", str(entry.get("posts", 1)), *ref_args, "--generate"]
    raise ValueError(f"unknown request kind: {entry['kind']!r}")


def _run_entry(entry: dict, build_lock: threading.Lock) -> bool:
    code = entry["code"]
    _log(code, "lancée")

    generated = subprocess.run(_generate_command(entry), cwd=REPO.parent,
                                capture_output=True, text=True)
    # Generation only, now — the tool no longer chains its own export or page rebuild, so its
    # returncode is a clean signal of whether the image itself was produced.
    if generated.returncode:
        reason = _tail(generated.stderr) or _tail(generated.stdout) or "génération en échec"
        _fail(entry, reason)
        return False

    # The version suffix (v2, v3, ...) is decided by the tool from what already exists on disk at the
    # moment it runs; reading the path back off its own stdout avoids recomputing — and racing — that
    # same decision independently in this process.
    image_rel = _find_image_path(generated.stdout)
    image_abs = REPO / image_rel if image_rel else None
    if image_abs is None or not image_abs.is_file():
        _fail(entry, "génération réussie mais chemin d'image introuvable dans sa sortie")
        return False
    _log(code, "image")

    exported = subprocess.run(
        ["python3", str(REPO / "scripts" / "export-asset.py"), str(image_abs)],
        cwd=REPO.parent, capture_output=True, text=True)
    if exported.returncode:
        reason = _tail(exported.stderr) or _tail(exported.stdout) or "export-asset.py en échec"
        _fail(entry, reason, image_rel)
        return False
    _log(code, "exportée")

    # The page is the one resource every request shares: two images landing together must not
    # rebuild it at the same time. Generation and export above stay fully parallel; only this step is
    # serialized, and only for the requests this process itself is driving.
    with build_lock:
        built = subprocess.run(
            ["php", str(REPO / "review-server" / "suivi-sprites" / "build.php")],
            cwd=REPO.parent, capture_output=True, text=True)
    if built.returncode:
        reason = _tail(built.stderr) or _tail(built.stdout) or "build.php en échec"
        _fail(entry, reason, image_rel)
        return False
    _log(code, "page reconstruite")

    _update_entry(entry["id"], state="done", image=image_rel)
    return True


def _process_entry(entry: dict, build_lock: threading.Lock) -> bool:
    try:
        return _run_entry(entry, build_lock)
    except Exception as exc:  # a fault here must fail this one request, never take down the queue
        _fail(entry, str(exc))
        return False


def run(workers: int = 6, poll_seconds: float = 2.0) -> int:
    """Vide la file en continu et rend le nombre d'échecs."""
    failures = 0
    in_flight: dict = {}
    # Shared across every worker thread this call spawns, so it serializes step 3 across all of them
    # regardless of which request gets there first.
    build_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=max(workers, 1)) as pool:
        while True:
            # Re-read every pass: a request queued mid-run by another "add" invocation must be picked
            # up here without this loop, or the process running it, ever restarting.
            pending = [entry for entry in _read_entries() if entry["state"] == "pending"]
            free_slots = max(workers - len(in_flight), 0)
            for entry in pending[:free_slots]:
                # Marked running before the thread even starts, so the very next read of the file
                # (by "status", or by this same loop) never lists it as pending twice.
                _update_entry(entry["id"], state="running")
                future = pool.submit(_process_entry, entry, build_lock)
                in_flight[future] = entry["id"]

            if not in_flight:
                # Nothing running and this pass found nothing waiting either: the queue is genuinely
                # empty right now, not just between two polls.
                break

            done, _still_running = wait(list(in_flight.keys()), timeout=poll_seconds,
                                         return_when=FIRST_COMPLETED)
            for future in done:
                del in_flight[future]
                if not future.result():
                    failures += 1
    return failures


def _print_status() -> None:
    entries = _read_entries()
    labels = [("pending", "en attente"), ("running", "en cours"),
              ("done", "faites"), ("failed", "échouées")]
    for state, label in labels:
        group = [entry for entry in entries if entry["state"] == state]
        codes = ", ".join(entry["code"] for entry in group)
        suffix = f" : {codes}" if codes else ""
        print(f"{label} ({len(group)}){suffix}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    command, rest = argv[0], argv[1:]
    if command == "add":
        if not rest:
            print(__doc__)
            return 2
        requests = json.loads(Path(rest[0]).read_text(encoding="utf-8"))
        added = enqueue(requests)
        print(f"{added} demande(s) ajoutée(s)")
        return 0

    if command == "run":
        workers = int(rest[rest.index("--workers") + 1]) if "--workers" in rest else 6
        return run(workers=workers)

    if command == "status":
        _print_status()
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""Time every step of one image's production and leave a validation report beside the image.

USAGE
  run = Run("OB-010_shape-ew_posts-2_portillon-gate-open")
  with run.step("consigne"):
      prompt = assemble()
  with run.step("génération"):
      generate(prompt)
  run.write(image_path, prompt, extras)

  Every step prints its START and its END as it happens, the end carrying the step's own duration in
  minutes and seconds, and the whole run its total. The same records are then written to
  "<image stem>-rapport.md" beside the image, together with the consigne that produced it and the
  measures taken on it.

INTENTION
  A generation used to be a silent wait of unknown length ending in a file, with the report — when there was one — written by an agent reading the picture.
  Two things came out of that: nobody could say where the time went, and the report cost a model call and carried a model's opinion.

  Both belong to the tool. What can be counted is counted here, stamped, and written down; what cannot be counted is not this file's business. The report
  is a PRODUCT of the run, never a story told about it afterwards. Timestamps are local and written to the second: a human compares one run against the
  next with them, nothing parses them.

  WHY PYTHON AND NOT PHP, the project's default: this module is imported by the generation tools that call it, which are themselves in Python because the
  chain's measuring step depends on Pillow and NumPy — reading an image's alpha channel and its luminance, which have no equivalent in PHP here. A report
  written in PHP would mean a second process and a second file format between a tool and its own timings. It moves to PHP the day those tools do.
"""
from __future__ import annotations

import json
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECK_ASSET = REPO / "scripts" / "check-asset.py"
# Where a run's traces live. NOT beside the image: assets/ holds assets, and a report or an event log is a trace of execution, not a deliverable —
# versioning them would put megabytes of transcript next to every picture. Everything a sprite's generation leaves behind sits under one folder, so it is
# found in one place rather than hunted for across the tree.
TRACES = REPO / "var" / "generations"


def stamp(moment: float) -> str:
    """A moment, to the second, as a human reads it."""
    return datetime.fromtimestamp(moment).strftime("%Y-%m-%d %H:%M:%S")


def duration(seconds: float) -> str:
    """A span in minutes and seconds — never a bare float, which nobody reads at a glance."""
    whole = int(round(seconds))

    return f"{whole // 60} min {whole % 60:02d} s"


class Run:
    """One image's production, step by step.

    A step that raises is recorded as failed and the exception goes on rising: a fault must reach the
    launcher, and a report that hid it would be worse than no report at all (execution.md, "Une erreur
    remonte toujours"). The report is still written by whoever catches it, holding the steps that did
    run and the one that broke.
    """

    def __init__(self, label: str, kind: str = "sprites"):
        # What is being produced, which is also where its traces go: `sprites` for a sprite, `subjects` for a usage sample. Everything one kind of run
        # leaves behind sits under one folder, so a trace is found in one place rather than hunted for across a mirrored tree.
        self.traces = TRACES / kind
        self.label = label
        self.started = time.time()
        self.records: list[dict] = []
        # The generator session's id, and the directory it ran in. Both are needed to reopen it: a session belongs to the folder it was launched from and
        # is not offered anywhere else, so an id alone leaves the reader hunting for where it lives.
        self.session: str | None = None
        self.session_dir: Path | None = None
        # The model the image was produced on. Empty means the agent's own configured default, which is what a report must then say — a run compared with
        # another one is only comparable when both name what they ran on.
        self.model: str | None = None

    @contextmanager
    def step(self, name: str):
        began = time.time()
        print(f"▶ {name} — début {stamp(began)}", flush=True)
        outcome = "faite"
        try:
            yield
        except BaseException:
            outcome = "EN ÉCHEC"
            raise
        finally:
            ended = time.time()
            self.records.append({"name": name, "began": began, "ended": ended,
                                 "seconds": ended - began, "outcome": outcome})
            print(f"■ {name} — fin {stamp(ended)} · durée {duration(ended - began)} · {outcome}",
                  flush=True)

    def total(self) -> float:
        return time.time() - self.started

    @staticmethod
    def session_of(output: str) -> str | None:
        """The generator session's own id, taken from the line the wrapper prints for it.

        It is what makes a generation reopenable afterwards — `codex exec resume <id>` replays what the agent actually did — so it belongs in the report
        rather than scrolling past in a terminal. Returns None when the wrapper could not find one, which the report then says in as many words.
        """
        for line in (output or "").splitlines():
            if line.startswith("SESSION "):
                found = line.rsplit(" ", 1)[-1].strip()
                return None if found == "inconnue" else found

        return None

    def measures(self, image: Path) -> str:
        """The mechanical measures of the produced image, taken by the project's own measuring tool —
        never re-implemented here, so a report can never disagree with a direct measure."""
        done = subprocess.run(["python3", str(CHECK_ASSET), str(image)],
                              cwd=REPO.parent, capture_output=True, text=True)
        return (done.stdout or "").strip() or (done.stderr or "").strip() or "aucune mesure rendue"

    # Les libellés des critères, en français et pour l'opérateur : l'outil de mesure les nomme en anglais parce qu'il est du code, le rapport se lit.
    CRITERIA = {"transparency": "Fond transparent", "footprint": "Emprise au sol", "light": "Lumière dans la bande",
                "tiling": "Raccord bord à bord", "regularity": "Régularité de la matière"}

    def evaluation(self, image: Path) -> list:
        """The stored evaluation, rendered as a Markdown table — read from the file the measuring tool has just written, never recomputed here.

        Its absence is said out loud rather than passed over: an image whose evaluation is missing has not been examined, and a report that stayed silent about it would let
        it pass for examined and found good.
        """
        stored = self.traces / f"{image.stem}-evaluation.json"
        if not stored.is_file():
            return ["", "**Aucune évaluation** — l'outil de mesure n'en a pas produit pour cette image."]

        evaluation = json.loads(stored.read_text(encoding="utf-8"))
        score = evaluation["score"]
        lines = ["", f"**Score : {score['met']} / {score['total']} critères tenus** — évaluation stockée dans `{stored.relative_to(REPO)}`", "",
                 "| Critère | Verdict |", "|---|---|"]
        for criterion in evaluation["criteria"]:
            name = self.CRITERIA.get(criterion["name"], criterion["name"])
            lines.append(f"| {name} | {'tenu' if criterion['met'] else '**ÉCHEC**'} |")

        return lines

    def write(self, image: Path, prompt: str, extras: dict | None = None) -> Path:
        """Write the report beside the image and return its path.

        `extras` holds the additional generation instructions this image was given, if any — the sheet's
        and the referentiel's. Both are shown when both are provided, neither is required.
        """
        session = self.session or "non remontée par le générateur"
        # The generator always runs at the project root — one place where every session of the project lives and can be listed (generate-image.php).
        where = str(self.session_dir or REPO)
        # The two files this run leaves behind, named in the report itself: the image it produced, and the generator's own events beside it. A report that
        # does not say where its image and its log are forces whoever reads it to go looking for both.
        log = self.traces / f"{image.stem}-generateur.jsonl"
        lines = [f"# Rapport de production — {self.label}", "",
                 f"**Image :** `{image.relative_to(REPO)}`  ",
                 f"**Journal du générateur :** `{log.relative_to(REPO)}`"
                 + ("" if log.is_file() else " — absent") + "  ",
                 f"**Lancée le :** {stamp(self.started)}  ",
                 f"**Durée totale :** {duration(self.total())}  ",
                 f"**Modèle :** `{self.model or 'défaut configuré du générateur'}`  ",
                 f"**Session du générateur :** `{session}`  ",
                 f"**À rouvrir depuis** `{where}` — une session n'existe que dans le dossier où elle a "
                 f"été lancée : `cd {where}` puis `codex exec resume {session}`", "",
                 "## Étapes", "",
                 "| Étape | Début | Fin | Durée | État |", "|---|---|---|---|---|"]
        for record in self.records:
            lines.append(f"| {record['name']} | {stamp(record['began'])} | {stamp(record['ended'])} "
                         f"| {duration(record['seconds'])} | {record['outcome']} |")

        for title, text in (extras or {}).items():
            if text:
                lines += ["", f"## {title}", "", text.strip()]

        # L'évaluation d'abord, les mesures ensuite : le score dit en une ligne si l'image vaut qu'on l'ouvre, et le détail chiffré ne se lit qu'après, quand on veut savoir
        # POURQUOI. Le tableau est en Markdown parce qu'un rapport se lit, se cite et s'affiche dans une page — le bloc de mesures, lui, reste tel que l'outil l'a rendu.
        measured = self.measures(image)
        lines += ["", "## Évaluation"] + self.evaluation(image)
        lines += ["", "## Mesures de l'image", "", "```", measured, "```",
                  "", "## Consigne envoyée", "", "```", prompt.strip(), "```", ""]

        report = self.traces / f"{image.stem}-rapport.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("\n".join(lines), encoding="utf-8")
        print(f"rapport écrit : {report.relative_to(REPO)}", flush=True)

        return report

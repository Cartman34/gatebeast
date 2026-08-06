#!/usr/bin/env python3
"""Build the artifact index: the single page that lists every published artifact.

The problem this page solves: published artifacts (review pages, tracking
pages...) accumulate over the project's life, and their addresses only ever
exist scattered across chat messages. The operator needs one address to
remember, that leads to every other one.

The single source of truth is the "Les revues publiées" table in SUIVI.md, at
the repository root. This script reads that table AND NOTHING ELSE: no list
of artifacts is hard-coded here. An artifact added to SUIVI.md tomorrow must
appear on the page next run, with no code change.

Reading discipline:
  - If SUIVI.md is unreadable, or the "Les revues publiées" section or its
    table cannot be found, the script fails loudly (non-zero exit, message
    naming exactly what is missing) rather than emit an empty or partial
    page.
  - A malformed row (wrong number of columns) does not stop the build: it is
    skipped, but reported on stdout with its line number and raw content so
    it can be found and fixed in SUIVI.md.
  - A row with no address (an artifact announced but not yet opened) is kept
    and shown as such, with no link, rather than dropped.

Run from the repository root:

    python3 artefacts/index/build.py

Writes artefacts/index/page.html.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUIVI_PATH = REPO_ROOT / "SUIVI.md"
OUTPUT_PATH = Path(__file__).resolve().parent / "page.html"

SECTION_HEADING = "## Les revues publiées"

# SUIVI.md documents exactly four canonical États for a published artifact: vivant, archivé,
# clos, à ne pas rouvrir. Recognized here by keyword, in this priority order: an état
# mentioning both "clos" and "supprimer" would be unusual, but if it ever happens the
# stronger warning (forbidden) wins.
FORBIDDEN_KEYWORDS = ("supprimer", "rouvrir")
STATE_PREFIXES = (
    ("clos", "closed"),
    ("archiv", "archived"),  # matches "archivé" (and a possible unaccented "archive")
    ("vivant", "alive"),
)

# Badge text shown on every card, on top of the section it sits in — the operator asked for
# "archivé" and "clos" to be told apart at a glance, not just by which section a card is in.
CATEGORY_BADGES = {
    "alive": "Vivant",
    "archived": "Archivé",
    "closed": "Clos",
    "forbidden": "À ne pas rouvrir",
}


@dataclass(frozen=True)
class Artifact:
    """One row of the "Les revues publiées" table, parsed."""

    name: str
    description: str
    address: str | None  # None when not yet opened
    state_text: str  # the État column, verbatim (markdown emphasis stripped)
    category: str  # "alive", "archived", "closed" or "forbidden"
    source_line: int


@dataclass(frozen=True)
class Anomaly:
    """A table row that could not be parsed, kept for the build report."""

    line_number: int
    raw_line: str
    reason: str


def capitalize_first(text: str) -> str:
    """Capitalize only the first letter of a displayed label, per the project's rule.

    A leading code span (an address or a path, e.g. "`assets/poc/`, ...") keeps its exact
    casing — the rule that carves out technical codes and addresses applies here too — so
    text starting with a backtick is left untouched.
    """
    if not text or text[0] == "`":
        return text
    return text[0].upper() + text[1:]


def render_inline_markdown(text: str, location: str, warnings: list[str]) -> str:
    """Render the small subset of inline Markdown used in SUIVI.md: `code`, **bold**, *italic*.

    Everything else is HTML-escaped as plain text. SUIVI.md is a Markdown document; this page
    must render its marks, not print them literally. Any Markdown-looking construct this
    function does not know how to render (a link, a strikethrough, an unmatched backtick...) is
    left as escaped plain text but reported in `warnings` — a mark that isn't handled must be
    named, not silently passed through as if it were plain punctuation.
    """
    token_pattern = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*")
    pieces: list[str] = []
    last_end = 0
    for match in token_pattern.finditer(text):
        pieces.append(html.escape(text[last_end : match.start()]))
        code, bold, italic = match.groups()
        if code is not None:
            pieces.append(f"<code>{html.escape(code)}</code>")
        elif bold is not None:
            pieces.append(f"<strong>{html.escape(bold)}</strong>")
        else:
            pieces.append(f"<em>{html.escape(italic)}</em>")
        last_end = match.end()
    pieces.append(html.escape(text[last_end:]))

    # Look for Markdown constructs this function cannot render, in whatever text the
    # recognized tokens above did not already consume.
    remainder = token_pattern.sub("", text)
    if "`" in remainder:
        warnings.append(f"{location} : accent grave non apparié dans « {text} »")
    if re.search(r"\[[^\]]+\]\([^)]+\)", remainder):
        warnings.append(f"{location} : lien Markdown non rendu dans « {text} »")
    if "~~" in remainder:
        warnings.append(f"{location} : texte barré Markdown non rendu dans « {text} »")
    if re.search(r"(?<!\w)_[^_]+_(?!\w)", remainder):
        warnings.append(f"{location} : emphase en tiret bas non rendue dans « {text} »")

    return "".join(pieces)


def strip_markdown_emphasis(text: str) -> str:
    """Strip bold/italic markers from a cell, without touching its wording.

    Handles two shapes seen in SUIVI.md: a cell entirely wrapped in emphasis
    (e.g. an italicized deprecated entry, "*Name — note*"), and emphasis
    wrapping only part of the text (e.g. "**Name** — description").
    """
    text = text.strip()
    if text.startswith("**") and text.endswith("**") and len(text) >= 4:
        text = text[2:-2].strip()
    elif text.startswith("*") and text.endswith("*") and len(text) >= 2:
        text = text[1:-1].strip()
    # Any remaining bold span wrapping part of the text (e.g. "**Name** — rest").
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return text.strip()


def split_name_and_description(cell: str) -> tuple[str, str]:
    """Split an "Artefact" cell into its name and its one-sentence description.

    The convention in SUIVI.md is "**Name** — description", the name in bold
    (or, for deprecated entries, the whole cell in italics). Once emphasis is
    stripped, the plain text is split on the first em dash.
    """
    plain = strip_markdown_emphasis(cell)
    if " — " in plain:
        name, description = plain.split(" — ", 1)
        return name.strip(), description.strip()
    return plain.strip(), ""


def parse_address(cell: str) -> str | None:
    """Parse the "Adresse" cell: a real address, or None when not opened yet.

    A row without an address (e.g. "*pas encore créé*") is kept, not
    dropped — the requirement is to show it for what it is, not to omit it.
    """
    plain = strip_markdown_emphasis(cell)
    if plain.startswith("http://") or plain.startswith("https://"):
        return plain
    return None


def classify_state(state_text: str, has_address: bool) -> tuple[str, bool]:
    """Sort an artifact into "alive", "archived", "closed" or "forbidden" from its État text.

    This drives the page layout: alive artifacts are shown first and prominently, archived
    ones next (still valid, just no longer active), closed ones after that, and forbidden
    ones (marked for deletion, or "never republish here") carry a warning that cannot be
    mistaken for a live artifact.

    Returns the category plus whether the état text was actually recognized as one of the
    four canonical values SUIVI.md documents. A row with no address yet (an artifact
    announced but not opened) is exempt: its état is necessarily provisional, not one of the
    four, and that is expected rather than a drift to flag.
    """
    lowered = state_text.lower()
    if any(keyword in lowered for keyword in FORBIDDEN_KEYWORDS):
        return "forbidden", True
    for prefix, category in STATE_PREFIXES:
        if lowered.startswith(prefix):
            return category, True
    if not has_address:
        return "alive", True
    return "alive", False


def is_separator_row(cells: list[str]) -> bool:
    """True for a markdown table's header/body separator row (the "|---|---|" line)."""
    return all(re.fullmatch(r":?-{1,}:?", cell.strip()) for cell in cells)


def parse_row(line: str) -> list[str]:
    """Split one markdown table line into its cell texts."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def find_table_lines(markdown_text: str) -> list[tuple[int, str]]:
    """Return every table line (1-based line number, raw text) under SECTION_HEADING.

    Scans from the heading to the next level-2 heading (or end of file).
    Fails loudly if the heading itself is missing, or if it holds no table:
    an operator relying on this page must know immediately if SUIVI.md has
    drifted, rather than get a silently empty or partial page.
    """
    lines = markdown_text.splitlines()

    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == SECTION_HEADING:
            start_index = index
            break
    if start_index is None:
        raise SystemExit(
            f"SUIVI.md ne contient pas la section '{SECTION_HEADING}' — "
            f"impossible de construire l'index des artefacts. "
            f"Vérifier que le titre exact existe dans '{SUIVI_PATH}'."
        )

    table_lines: list[tuple[int, str]] = []
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            table_lines.append((index + 1, line))

    if not table_lines:
        raise SystemExit(
            f"La section '{SECTION_HEADING}' de SUIVI.md ne contient aucun tableau "
            f"(aucune ligne commençant par '|' entre ce titre et le suivant) — "
            f"impossible de construire l'index des artefacts."
        )

    return table_lines


def load_artifacts() -> tuple[list[Artifact], list[Anomaly], list[str]]:
    """Read SUIVI.md and parse the "Les revues publiées" table.

    Returns the successfully parsed artifacts (in table order), the anomalies found along the
    way (malformed rows that were skipped rather than guessed at), and any état text that
    could not be matched to one of the four canonical values SUIVI.md documents (kept on the
    page under "alive" by default, but flagged rather than silently misclassified).
    """
    if not SUIVI_PATH.exists():
        raise SystemExit(
            f"'{SUIVI_PATH}' est introuvable — impossible de construire l'index des artefacts."
        )
    try:
        markdown_text = SUIVI_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"'{SUIVI_PATH}' est illisible : {error}") from error

    table_lines = find_table_lines(markdown_text)

    if len(table_lines) < 2:
        raise SystemExit(
            f"Le tableau sous '{SECTION_HEADING}' n'a pas de ligne de séparation "
            f"(l'en-tête suivi de '|---|---|...') — format inattendu, "
            f"impossible de construire l'index des artefacts."
        )

    header_cells = parse_row(table_lines[0][1])
    separator_cells = parse_row(table_lines[1][1])
    if not is_separator_row(separator_cells):
        raise SystemExit(
            f"La ligne {table_lines[1][0]} de SUIVI.md, sous '{SECTION_HEADING}', "
            f"n'est pas la ligne de séparation attendue d'un tableau markdown "
            f"(reçu : '{table_lines[1][1].strip()}') — format inattendu."
        )
    if len(header_cells) != 3:
        raise SystemExit(
            f"L'en-tête du tableau (ligne {table_lines[0][0]} de SUIVI.md) a "
            f"{len(header_cells)} colonne(s) au lieu de 3 (Artefact, Adresse, État) "
            f"— format inattendu."
        )

    artifacts: list[Artifact] = []
    anomalies: list[Anomaly] = []
    state_warnings: list[str] = []

    for line_number, raw_line in table_lines[2:]:
        cells = parse_row(raw_line)
        if len(cells) != 3:
            anomalies.append(
                Anomaly(
                    line_number=line_number,
                    raw_line=raw_line.strip(),
                    reason=f"{len(cells)} colonne(s) au lieu de 3",
                )
            )
            continue

        artifact_cell, address_cell, state_cell = cells
        name, description = split_name_and_description(artifact_cell)
        if not name:
            anomalies.append(
                Anomaly(
                    line_number=line_number,
                    raw_line=raw_line.strip(),
                    reason="colonne Artefact vide une fois l'emphase retirée",
                )
            )
            continue

        state_text = strip_markdown_emphasis(state_cell)
        if not state_text:
            anomalies.append(
                Anomaly(
                    line_number=line_number,
                    raw_line=raw_line.strip(),
                    reason="colonne État vide",
                )
            )
            continue

        address = parse_address(address_cell)
        category, recognized = classify_state(state_text, has_address=address is not None)
        if not recognized:
            state_warnings.append(
                f"{name} (ligne {line_number}) : état '{state_text}' ne correspond à aucun "
                f"des quatre états canoniques (vivant, archivé, clos, à ne pas rouvrir) "
                f"— classé par défaut parmi les vivants."
            )

        artifacts.append(
            Artifact(
                name=name,
                description=description,
                address=address,
                state_text=state_text,
                category=category,
                source_line=line_number,
            )
        )

    if not artifacts:
        raise SystemExit(
            f"Aucune ligne exploitable dans le tableau sous '{SECTION_HEADING}' "
            f"({len(anomalies)} ligne(s) anormale(s) rencontrée(s)) — "
            f"impossible de construire une page non vide."
        )

    return artifacts, anomalies, state_warnings


def render_card(artifact: Artifact, warnings: list[str]) -> str:
    """Render one artifact as a self-contained card.

    Name, description and état come from a Markdown document and are displayed labels: each
    is rendered through render_inline_markdown() (so `code`, **bold** and *italic* show up as
    such, not as literal punctuation) and capitalized on its first letter, per project rule.
    """
    location = f"{artifact.name} (ligne {artifact.source_line})"

    name_html = render_inline_markdown(capitalize_first(artifact.name), location, warnings)
    description_html = (
        f'<p class="card-description">'
        f"{render_inline_markdown(capitalize_first(artifact.description), location, warnings)}"
        f"</p>"
        if artifact.description
        else ""
    )
    state_html = render_inline_markdown(capitalize_first(artifact.state_text), location, warnings)

    # L'ADRESSE NE S'ÉCRIT PLUS EN CLAIR : c'est la carte entière qui mène à l'artefact. Une adresse affichée prend trois lignes, se coupe au milieu d'un
    # identifiant, et personne ne la lit — ce qu'on veut, c'est cliquer. Une carte sans adresse reste un bloc mort et le dit.
    if artifact.address is None:
        address_html = '<span class="card-no-address">pas encore ouvert</span>'

    warning_html = (
        '<p class="card-warning">Ne jamais republier sur cette adresse.</p>'
        if artifact.category == "forbidden"
        else ""
    )
    badge_html = (
        f'<span class="card-badge card-badge-{artifact.category}">'
        f"{html.escape(CATEGORY_BADGES[artifact.category])}</span>"
    )

    inside = f"""  {badge_html}
  <h3 class="card-name">{name_html}</h3>
  {description_html}
  <p class="card-state">{state_html}</p>
  {warning_html}"""

    if artifact.address is None:
        return f"""
<article class="card card-{artifact.category}">
{inside}
  <p class="card-address">{address_html}</p>
</article>"""

    return f"""
<a class="card card-{artifact.category}" href="{html.escape(artifact.address)}" target="_blank" rel="noopener">
{inside}
</a>"""


def render_group(title: str, artifacts: list[Artifact], group_class: str, warnings: list[str]) -> str:
    """Render one category group (its heading plus its cards), or nothing if empty."""
    if not artifacts:
        return ""
    cards_html = "\n".join(render_card(artifact, warnings) for artifact in artifacts)
    return f"""
<section class="group group-{group_class}">
  <h2 class="group-title">{html.escape(title)}</h2>
  <div class="group-cards">
    {cards_html}
  </div>
</section>"""


def render_anomalies(anomalies: list[Anomaly]) -> str:
    """Render the anomaly notice shown at the bottom of the page, or nothing if none."""
    if not anomalies:
        return ""
    items_html = "\n".join(
        f"<li>Ligne {anomaly.line_number} : {html.escape(anomaly.reason)} "
        f"— <code>{html.escape(anomaly.raw_line)}</code></li>"
        for anomaly in anomalies
    )
    return f"""
<section class="anomalies">
  <h2 class="anomalies-title">Lignes ignorées dans SUIVI.md</h2>
  <ul class="anomalies-list">
    {items_html}
  </ul>
</section>"""


def render_markdown_warnings(warnings: list[str]) -> str:
    """Render the notice for build-time warnings (unrendered Markdown, unrecognized états).

    Nothing here blocks the build: these are surfaced so a real drift in SUIVI.md — a
    typo'd état, a Markdown mark this page cannot render — gets noticed at the next read,
    instead of silently passing through.
    """
    if not warnings:
        return ""
    items_html = "\n".join(f"<li>{html.escape(warning)}</li>" for warning in warnings)
    return f"""
<section class="anomalies">
  <h2 class="anomalies-title">Signalé à la relecture</h2>
  <ul class="anomalies-list">
    {items_html}
  </ul>
</section>"""


def render_page(
    artifacts: list[Artifact], anomalies: list[Anomaly], state_warnings: list[str]
) -> tuple[str, list[str]]:
    """Assemble the full, self-contained HTML page.

    Returns the page markup and the list of Markdown-rendering warnings collected along the
    way, so the caller can also report them on stdout.
    """
    markdown_warnings: list[str] = list(state_warnings)

    alive = [artifact for artifact in artifacts if artifact.category == "alive"]
    archived = [artifact for artifact in artifacts if artifact.category == "archived"]
    closed = [artifact for artifact in artifacts if artifact.category == "closed"]
    forbidden = [artifact for artifact in artifacts if artifact.category == "forbidden"]

    groups_html = (
        render_group("Vivants", alive, "alive", markdown_warnings)
        + render_group("Archivés", archived, "archived", markdown_warnings)
        + render_group("Clos", closed, "closed", markdown_warnings)
        + render_group("À ne pas rouvrir", forbidden, "forbidden", markdown_warnings)
    )
    anomalies_html = render_anomalies(anomalies) + render_markdown_warnings(markdown_warnings)

    page_html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>GateBeast — Index des artefacts</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #ffffff;
    --fg: #1d1a24;
    --muted: #5c5468;
    --border: #d8d3e0;
    --card-bg: #faf9fc;
    --warning-fg: #7a1f1f;
    --warning-bg: #fbe6e6;
    --warning-border: #d98c8c;
    --alive-badge-bg: #e1f3e6;
    --alive-badge-fg: #1f6b3a;
    --archived-badge-bg: #fdedd3;
    --archived-badge-fg: #8a5a10;
    --closed-badge-bg: #e2e1e6;
    --closed-badge-fg: #4a4753;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #17151d;
      --fg: #eeecf3;
      --muted: #a79fb5;
      --border: #3a3546;
      --card-bg: #1f1c27;
      --warning-fg: #f3b4b4;
      --warning-bg: #3a1f1f;
      --warning-border: #7a3a3a;
      --alive-badge-bg: #1e3a27;
      --alive-badge-fg: #8fdba8;
      --archived-badge-bg: #40320f;
      --archived-badge-fg: #ecc880;
      --closed-badge-bg: #322f3a;
      --closed-badge-fg: #c3bfcc;
    }}
  }}
  :root[data-theme="light"] {{
    --bg: #ffffff; --fg: #1d1a24; --muted: #5c5468; --border: #d8d3e0;
    --card-bg: #faf9fc; --warning-fg: #7a1f1f; --warning-bg: #fbe6e6; --warning-border: #d98c8c;
    --alive-badge-bg: #e1f3e6; --alive-badge-fg: #1f6b3a;
    --archived-badge-bg: #fdedd3; --archived-badge-fg: #8a5a10;
    --closed-badge-bg: #e2e1e6; --closed-badge-fg: #4a4753;
  }}
  :root[data-theme="dark"] {{
    --bg: #17151d; --fg: #eeecf3; --muted: #a79fb5; --border: #3a3546;
    --card-bg: #1f1c27; --warning-fg: #f3b4b4; --warning-bg: #3a1f1f; --warning-border: #7a3a3a;
    --alive-badge-bg: #1e3a27; --alive-badge-fg: #8fdba8;
    --archived-badge-bg: #40320f; --archived-badge-fg: #ecc880;
    --closed-badge-bg: #322f3a; --closed-badge-fg: #c3bfcc;
  }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 2rem 1.5rem 4rem;
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, sans-serif;
  }}
  h1 {{
    font-size: 1.6rem;
    margin: 0 0 0.25rem;
  }}
  .page-intro {{
    color: var(--muted);
    margin: 0 0 2.5rem;
    max-width: 65ch;
  }}
  .group {{
    margin: 0 0 2.5rem;
  }}
  .group-title {{
    font-size: 1.15rem;
    margin: 0 0 1rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border);
  }}
  .group-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }}
  /* LA CARTE ENTIÈRE EST LE LIEN : on clique la carte, pas une adresse écrite en clair qui prenait trois lignes et se coupait au milieu d'un identifiant. */
  .card {{
    display: block;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    background: var(--card-bg);
    color: inherit;
    text-decoration: none;
  }}
  a.card:hover {{
    border-color: var(--alive-badge-fg);
  }}
  a.card:focus-visible {{
    outline: 2px solid var(--alive-badge-fg);
    outline-offset: 2px;
  }}
  .card-name {{
    font-size: 1.05rem;
    margin: 0 0 0.4rem;
  }}
  /* La description dit ce qu'est l'artefact, pas ce qu'il contient : elle se lit d'un coup d'œil sur une carte, et une carte n'est pas un paragraphe. Plus petite
     que le nom, et bornée en hauteur pour qu'une description longue ne fasse pas grandir sa carte au-dessus de ses voisines. */
  .card-description {{
    color: var(--muted);
    font-size: 0.84rem;
    line-height: 1.45;
    margin: 0 0 0.6rem;
  }}
  .card-address {{
    margin: 0 0 0.35rem;
    word-break: break-all;
    font-size: 0.78rem;
  }}
  .card-link {{
    color: inherit;
  }}
  .card-no-address {{
    color: var(--muted);
    font-style: italic;
  }}
  .card-state {{
    color: var(--muted);
    font-size: 0.78rem;
    margin: 0;
  }}

  /* The badge names the état on every card, so archivé and clos read apart even out of
     their section — a colored pill is a stronger, faster cue than opacity alone. */
  .card-badge {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    margin: 0 0 0.55rem;
  }}
  .card-badge-alive {{
    background: var(--alive-badge-bg);
    color: var(--alive-badge-fg);
  }}
  .card-badge-archived {{
    background: var(--archived-badge-bg);
    color: var(--archived-badge-fg);
  }}
  .card-badge-closed {{
    background: var(--closed-badge-bg);
    color: var(--closed-badge-fg);
  }}
  .card-badge-forbidden {{
    background: var(--warning-border);
    color: var(--warning-fg);
  }}

  /* Archived artifacts: still valid and consultable, just mildly receded — never confused
     with closed, which reads distinctly smaller and dimmer below. */
  .group-archived .card {{
    opacity: 0.9;
  }}

  /* Closed artifacts: kept, but visibly receded — smaller and dimmer than archived. */
  .group-closed .card {{
    opacity: 0.68;
    padding: 0.75rem 0.9rem;
  }}
  .group-closed .card-name {{
    font-size: 0.95rem;
  }}

  /* Forbidden artifacts: cannot be mistaken for a live one. */
  .group-forbidden .card {{
    background: var(--warning-bg);
    border-color: var(--warning-border);
    color: var(--warning-fg);
  }}
  .group-forbidden .card-description,
  .group-forbidden .card-state {{
    color: var(--warning-fg);
    opacity: 0.85;
  }}
  .group-forbidden .card-link {{
    color: var(--warning-fg);
    text-decoration: line-through;
  }}
  .card-warning {{
    margin: 0.5rem 0 0;
    font-weight: 600;
    font-size: 0.85rem;
  }}

  .anomalies {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px dashed var(--warning-border);
  }}
  .anomalies-title {{
    font-size: 1rem;
    color: var(--warning-fg);
    margin: 0 0 0.75rem;
  }}
  .anomalies-list {{
    margin: 0;
    padding-left: 1.2rem;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  .anomalies-list code {{
    font-size: 0.85em;
  }}
</style>
</head>
<body>
<h1>Index des artefacts</h1>
<p class="page-intro">Une seule adresse à retenir : la porte d'entrée vers tous les artefacts publiés du projet
GateBeast. Construite depuis la table &laquo;&nbsp;Les revues publiées&nbsp;&raquo; de <code>SUIVI.md</code>, seule
source de vérité — rien ici n'est ajouté à la main.</p>
{groups_html}
{anomalies_html}
</body>
</html>
"""

    return page_html, markdown_warnings


def build() -> int:
    artifacts, anomalies, state_warnings = load_artifacts()
    page_html, markdown_warnings = render_page(artifacts, anomalies, state_warnings)
    OUTPUT_PATH.write_text(page_html, encoding="utf-8")

    alive = sum(1 for artifact in artifacts if artifact.category == "alive")
    archived = sum(1 for artifact in artifacts if artifact.category == "archived")
    closed = sum(1 for artifact in artifacts if artifact.category == "closed")
    forbidden = sum(1 for artifact in artifacts if artifact.category == "forbidden")

    print(
        f"{len(artifacts)} artefact(s) trouvé(s) — {alive} vivant(s), {archived} archivé(s), "
        f"{closed} clos, {forbidden} à ne pas rouvrir."
    )
    for artifact in artifacts:
        print(f"  - [{artifact.category}] {artifact.name} (ligne {artifact.source_line})")

    if anomalies:
        print(f"{len(anomalies)} ligne(s) anormale(s) signalée(s) sur la page :")
        for anomaly in anomalies:
            print(f"  - ligne {anomaly.line_number} : {anomaly.reason} — {anomaly.raw_line}")

    if markdown_warnings:
        print(f"{len(markdown_warnings)} signalement(s) à la relecture, sur la page :")
        for warning in markdown_warnings:
            print(f"  - {warning}")

    print(f"Page écrite : {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())

#!/usr/bin/env python3
"""Build the inventory-audit review page: static HTML rendered from data.json, plus a small
progressive-enhancement script.

The page lists every gap found between the subject inventory and the six reference plates — a
contradiction (fiche and plate disagree) or an absence (drawn on a plate, no fiche at all) — and
collects one verdict per line, plus a per-category shortcut. Nothing on it is invented: the entries
come from a survey already handed over; this script only lays them out.

Every visible line — title, notice, section and category names, item text, verdict labels — is
rendered as real HTML text by this script, not injected by client-side JavaScript from a data blob.
A first version relied on JavaScript to build the whole page from an embedded JSON island; if that
script failed to run in the viewer for any reason, the page showed nothing but its static skeleton
(a title-less header and "0 éléments relevés"). The lesson: a page's content must be visible with no
script running at all. What little JavaScript remains (the per-category bulk buttons, the copied
recap, the browser-side save of a verdict already chosen) only touches markup that already exists —
it enhances the page, it never authors it.

Reads  data.json and audit-inventaire.html (the template, holding __TITLE__, __NOTICE__, __LEDE__,
       __TOTAL__ and __BODY__)
Writes page.html, the file that gets published.
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def escape(text: str) -> str:
    """Shorthand: HTML-escape a piece of French text before it goes into an attribute or a tag."""
    return html.escape(text, quote=True)


def render_notice(lines: list[str]) -> str:
    """The warning banner at the top of the page: several short paragraphs, always visible."""
    return "".join(f"<p>{escape(line)}</p>" for line in lines)


def render_verdict_inputs(item_code: str, verdicts: list[dict]) -> str:
    """One radio button per possible verdict for a single item — plain HTML, works with no script."""
    labels = []
    for verdict in verdicts:
        labels.append(
            f'<label><input type="radio" name="{escape(item_code)}" value="{escape(verdict["value"])}">'
            f'<span>{escape(verdict["label"])}</span></label>'
        )
    return "".join(labels)


def render_item(item: dict, verdicts: list[dict], placeholder: str, section_name: str) -> str:
    """One line of the audit: its code, its name, why it is here, and its verdict choices.

    Carries data-section itself (rather than making the recap script walk up to a
    ".section-intro" it is not actually nested inside — that element is a preceding sibling of
    the enclosing ".cat-block", not an ancestor of the item)."""
    say = f'<p class="say">{escape(item["say"])}</p>' if item.get("say") else ""
    why = f'<p class="why">{escape(item["why"])}</p>' if item.get("why") else ""
    return f"""
<div class="item" data-code="{escape(item['code'])}" data-section="{escape(section_name)}">
  <div class="what">
    <div class="ref"><b>{escape(item['code'])}  </b>{escape(item['ref'])}</div>
    {say}
    {why}
  </div>
  <div class="pick">{render_verdict_inputs(item['code'], verdicts)}</div>
  <div class="note"><textarea data-note="{escape(item['code'])}"
    placeholder="{escape(placeholder)}"></textarea></div>
</div>"""


def render_bulk_buttons(category_code: str, verdicts: list[dict]) -> str:
    """The per-category shortcuts: one button per verdict, each ticking every item in the category
    at once. Enhancement only — the radios above already work without these."""
    buttons = []
    for verdict in verdicts:
        label = "Tout : " + verdict["label"].lower()
        buttons.append(
            f'<button type="button" class="bulk-btn" data-cat="{escape(category_code)}" '
            f'data-value="{escape(verdict["value"])}">{escape(label)}</button>'
        )
    return "".join(buttons)


def render_category(category: dict, verdicts: list[dict], placeholder: str, section_name: str) -> str:
    """One category: its heading, its optional note, and every one of its items."""
    note = f'<p class="cat-note">{escape(category["note"])}</p>' if category.get("note") else ""
    items = "".join(
        render_item(item, verdicts, placeholder, section_name) for item in category["items"]
    )
    return f"""
<section class="cat-block">
  <div class="cat">
    <span class="code">{escape(category['code'])}</span>
    <h3>{escape(category['name'])}</h3>
    <div class="bulk">{render_bulk_buttons(category['code'], verdicts)}</div>
  </div>
  {note}
  {items}
</section>"""


def render_section(section: dict, placeholder: str) -> str:
    """One section (contradictions, or absences): its title, then its categories."""
    categories = "".join(
        render_category(category, section["verdicts"], placeholder, section["name"])
        for category in section["categories"]
    )
    return f"""
<div class="section-intro"><h2 class="section-title">{escape(section['name'])}</h2></div>
{categories}"""


def count_items(data: dict) -> int:
    """Every item across every section — the total the tally starts from."""
    return sum(
        len(category["items"])
        for section in data["sections"]
        for category in section["categories"]
    )


def build() -> int:
    data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
    template = (HERE / "audit-inventaire.html").read_text(encoding="utf-8")

    total = count_items(data)
    body = "".join(render_section(section, data["placeholder"]) for section in data["sections"])

    page = (template
            .replace("__SCREEN__", escape(data["screen"]))
            .replace("__TITLE__", escape(data["title"]))
            .replace("__LEDE__", escape(data["lede"]))
            .replace("__NOTICE__", render_notice(data["notice"]))
            .replace("__TOTAL__", str(total))
            .replace("__BODY__", body)
            .replace("__PLACEHOLDER__", escape(data["placeholder"]))
            .replace("__COPIED__", escape(data["copied"]))
            .replace("__COPY_REFUSED__", escape(data["copyRefused"])))
    (HERE / "page.html").write_text(page, encoding="utf-8")

    print(f"sections {len(data['sections'])} · éléments {total}")
    print(f"page écrite : {(HERE / 'page.html')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(build())

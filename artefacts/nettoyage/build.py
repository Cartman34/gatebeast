#!/usr/bin/env python3
"""Build the cleanup review page: the template plus its data, in one self-contained file.

The page lists everything found to clean and collects one verdict per line, plus a per-category
shortcut. Nothing on it is invented: the entries come from a survey of the working tree.

French labels travel as JSON and are written into the DOM as text, never concatenated into markup —
an apostrophe in a French label breaks a page silently otherwise.

Reads  data.json and nettoyage.html (the template, holding __DATA__)
Writes page.html, the file that gets published.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build() -> int:
    data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
    template = (HERE / "nettoyage.html").read_text(encoding="utf-8")

    encoded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = template.replace("__DATA__", encoded)
    (HERE / "page.html").write_text(page, encoding="utf-8")

    count = sum(len(category["items"]) for category in data["categories"])
    print(f"catégories {len(data['categories'])} · éléments {count}")
    print(f"page écrite : {(HERE / 'page.html')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(build())

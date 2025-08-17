#!/usr/bin/env python3
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CSV_PATH = Path("data/items.csv")
README_PATH = Path("README.md")
START = "<!-- CSV-TABLE:START -->"
END = "<!-- CSV-TABLE:END -->"

REQUIRED = ["categories", "title", "link", "comments"]

def esc(s: str) -> str:
    return (s or "").replace("|", r"\|").strip()

def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        headers = [h.lower().strip() for h in (r.fieldnames or [])]
        missing = [h for h in REQUIRED if h not in headers]
        if missing:
            raise SystemExit(f"CSV missing headers: {missing}. Expected {REQUIRED}")
        for row in r:
            yield {
                "categories": esc(row.get("Categories") or row.get("categories") or ""),
                "title": esc(row.get("Title") or row.get("title") or ""),
                "link": (row.get("Link") or row.get("link") or "").strip(),
                "comments": esc(row.get("Comments") or row.get("comments") or ""),
            }

def build_grouped_tables(rows):
    # group by category (case-insensitive key, but display original text)
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["categories"]].append(r)

    # sort categories by name; sort items by Title within each category
    ordered_categories = sorted(grouped.keys(), key=lambda c: c.lower())
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    out = []
    out.append(f"_Auto-generated from `data/items.csv` at {ts} UTC_")
    out.append("")
    for cat in ordered_categories:
        items = sorted(grouped[cat], key=lambda r: r["title"].lower())
        out.append(f"### {cat}")
        out.append("")
        out.append("| Title | Link | Comments |")
        out.append("|---|---|---|")
        for r in items:
            link_cell = f"[link]({r['link']})" if r["link"] else ""
            out.append(f"| {r['title']} | {link_cell} | {r['comments']} |")
        out.append("")  # blank line after each category table
    return "\n".join(out)

def insert_between(markdown: str, payload: str) -> str:
    if START in markdown and END in markdown:
        before = markdown.split(START, 1)[0]
        after = markdown.split(END, 1)[1]
        return f"{before}{START}\n{payload}\n{END}{after}"
    else:
        return markdown.rstrip() + f"\n\n{START}\n{payload}\n{END}\n"

def main():
    rows = list(read_rows(CSV_PATH))
    section = build_grouped_tables(rows)
    readme = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else "# README\n\n"
    updated = insert_between(readme, section)
    if updated != readme:
        README_PATH.write_text(updated, encoding="utf-8")
        print("README.md updated.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()

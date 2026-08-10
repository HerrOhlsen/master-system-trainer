"""Copy the JSON data into index.html so the app stays a single file.

Run after every change to data/master-system.json or data/mnemonica.json.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mastersystem  # noqa: E402
import stack  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

START = "<!-- DATA:START -->"
END = "<!-- DATA:END -->"
STACK_START = "<!-- STACK:START -->"
STACK_END = "<!-- STACK:END -->"


def replace(html, start, end, block):
    """Swap the marked region, or return None when the markers are missing."""
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(html):
        return None
    return pattern.sub(lambda _: block, html)


def main():
    data = mastersystem.load()
    stack_data = stack.load()
    problems = mastersystem.check(data) + stack.check(stack_data)
    if problems:
        print("Abbruch, Daten sind nicht sauber:")
        for problem in problems:
            print("  " + problem)
        return 1

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    stack_payload = json.dumps(stack_data, ensure_ascii=False, separators=(",", ":"))

    html = INDEX.read_text(encoding="utf-8")
    html = replace(html, START, END,
                   f'{START}\n<script id="master-data" type="application/json">{payload}</script>\n{END}')
    if html is None:
        print("Marker DATA nicht gefunden.")
        return 1
    html = replace(html, STACK_START, STACK_END,
                   f'{STACK_START}\n<script id="stack-data" type="application/json">{stack_payload}</script>\n{STACK_END}')
    if html is None:
        print("Marker STACK nicht gefunden.")
        return 1

    INDEX.write_text(html, encoding="utf-8")
    print(f"{len(data['eintraege'])} Einträge und {len(stack_data['stapel'])} Karten in index.html eingebettet "
          f"({(len(payload) + len(stack_payload)) / 1024:.1f} KB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Copy the JSON data into index.html so the app stays a single file.

Run after every change to data/master-system.json.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mastersystem  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

START = "<!-- DATA:START -->"
END = "<!-- DATA:END -->"


def main():
    data = mastersystem.load()
    problems = mastersystem.check(data)
    if problems:
        print("Abbruch, Daten sind nicht sauber:")
        for problem in problems:
            print("  " + problem)
        return 1

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    block = (
        f'{START}\n<script id="master-data" type="application/json">{payload}</script>\n{END}'
    )

    html = INDEX.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(html):
        print("Marker nicht gefunden.")
        return 1
    INDEX.write_text(pattern.sub(lambda _: block, html), encoding="utf-8")
    print(f"{len(data['eintraege'])} Einträge in index.html eingebettet ({len(payload) / 1024:.1f} KB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

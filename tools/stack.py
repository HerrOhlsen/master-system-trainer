"""Load and check the memorised deck order (Mnemonica).

Same idea as mastersystem.py: the JSON file is the source, this module is the
only place that knows what a valid stack looks like. inject_data.py refuses to
write a stack that does not hold every card exactly once.
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mnemonica.json"

VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = {"C": "Kreuz", "D": "Karo", "H": "Herz", "S": "Pik"}


def split(code):
    """Return (value, suit) for a card code like '10D', or None if malformed."""
    if len(code) < 2:
        return None
    value, suit = code[:-1], code[-1]
    if value not in VALUES or suit not in SUITS:
        return None
    return value, suit


def load():
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def check(data):
    """Return a list of human readable problems found in the stack."""
    problems = []
    stack = data.get("stapel", [])

    if len(stack) != 52:
        problems.append(f"Der Stapel hat {len(stack)} Karten, erwartet sind 52")

    for index, code in enumerate(stack, start=1):
        if split(code) is None:
            problems.append(f"Position {index}: '{code}' ist kein gueltiges Kartenkuerzel")

    seen = {}
    for index, code in enumerate(stack, start=1):
        seen.setdefault(code, []).append(index)
    for code, positions in sorted(seen.items()):
        if len(positions) > 1:
            problems.append(f"{code} liegt mehrfach im Stapel: Positionen {positions}")

    complete = {f"{value}{suit}" for value in VALUES for suit in SUITS}
    missing = sorted(complete - set(stack))
    if missing:
        problems.append(f"Es fehlen {len(missing)} Karten: {', '.join(missing)}")

    return problems


if __name__ == "__main__":
    data = load()
    problems = check(data)
    print(f"{len(data['stapel'])} Karten geladen.")
    if problems:
        print(f"\n{len(problems)} Auffaelligkeit(en):")
        for problem in problems:
            print("  " + problem)
    else:
        print("Jede Karte liegt genau einmal im Stapel.")

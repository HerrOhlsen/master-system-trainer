"""Shared helpers: load the master system data and encode words back to digits.

The encoder is the single source of truth for the rules described in Stenger's
book. The JavaScript version inside index.html must stay behaviourally identical.
"""

import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "master-system.json"

# Digraphs are matched before single letters.
DIGRAPHS = {
    "sch": "6",
    "ch": "6",
    "ck": "7",
}

SINGLES = {
    "s": "0", "z": "0",
    "t": "1", "d": "1",
    "n": "2",
    "m": "3",
    "r": "4",
    "l": "5",
    "k": "7", "c": "7", "g": "7",
    "f": "8", "v": "8", "w": "8",
    "p": "9", "b": "9",
}

UMLAUTS = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "s", "é": "e", "è": "e"})

# Words the book lists that do not strictly follow the rule. Kept because they
# are in the printed source, but excluded from the consistency check.
KNOWN_BOOK_DEVIATIONS = {"Keks"}


def normalize(word):
    return word.lower().translate(UMLAUTS)


def encode(word):
    """Return the digit string a word encodes to, following the master system."""
    text = normalize(word)
    text = re.sub(r"[^a-z]", "", text)
    digits = []
    i = 0
    previous_letter = ""
    while i < len(text):
        matched = False
        for digraph, digit in DIGRAPHS.items():
            if text.startswith(digraph, i):
                digits.append(digit)
                previous_letter = digraph[-1]
                i += len(digraph)
                matched = True
                break
        if matched:
            continue
        letter = text[i]
        if letter in SINGLES:
            # Double consonants count only once (Tanne = 12, not 122).
            if letter != previous_letter:
                digits.append(SINGLES[letter])
            previous_letter = letter
        else:
            previous_letter = ""
        i += 1
    return "".join(digits)


def load():
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def check(data):
    """Return a list of human readable problems found in the data."""
    problems = []
    entries = data["eintraege"]

    numbers = [e["zahl"] for e in entries]
    if numbers != list(range(100)):
        missing = sorted(set(range(100)) - set(numbers))
        duplicates = sorted({n for n in numbers if numbers.count(n) > 1})
        problems.append(f"Zahlenreihe unvollständig. Fehlend: {missing}, doppelt: {duplicates}")

    for entry in entries:
        number = entry["zahl"]
        expected = f"{number:02d}" if number > 9 else str(number)
        for word in [entry["wort"]] + entry["alternativen"]:
            if word in KNOWN_BOOK_DEVIATIONS:
                continue
            got = encode(word)
            # A single digit number may be written as "0" or "00".
            if got != expected and not (number <= 9 and got == expected.lstrip("0")):
                problems.append(f"{number:>2}  {word:<10} codiert zu {got or '(nichts)'}, erwartet {expected}")

    for entry in entries:
        if not entry["bilder"]:
            problems.append(f"{entry['zahl']:>2}  keine Visualisierungsanregung")

    return problems


if __name__ == "__main__":
    data = load()
    problems = check(data)
    print(f"{len(data['eintraege'])} Einträge geladen.")
    if problems:
        print(f"\n{len(problems)} Auffälligkeit(en):")
        for problem in problems:
            print("  " + problem)
    else:
        print("Alle Merkwörter passen zur Konsonantenregel.")

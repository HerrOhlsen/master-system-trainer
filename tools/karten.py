"""Prüft die Kartenwörter gegen die Konsonantenregel.

Ein Kartenwort trägt die Farbe im ersten Konsonanten und den Wert in den
folgenden. Weil s, z und ß dieselbe Ziffer tragen (ebenso k, c, g und p, b),
wird nicht der Buchstabe geprüft, sondern die Ziffernfolge. Herz ist der
Sonderfall: h ist im Master-System frei, ein Herzwort codiert nur den Wert.

Bube, Dame und König sind Personen und lassen sich nicht codieren. Bei ihnen
wird nur geprüft, dass der erste Konsonant zur Farbe passt.
"""

import json
from pathlib import Path

import mastersystem

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "kartensystem.json"

# Farbe -> (Buchstabe fürs Auge, Ziffer im Code, None bei Herz)
FARBEN = {
    "C": ("z", "0"),
    "D": ("k", "7"),
    "S": ("p", "9"),
    "H": ("h", None),
}
# Ziffern, die als Anfangskonsonant für die Farbe durchgehen
FARB_BUCHSTABEN = {
    "C": set("szß"),
    "D": set("kcg"),
    "S": set("pb"),
    "H": set("h"),
}
WERTE = {
    "A": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
    "7": "7", "8": "8", "9": "9", "10": "10",
}
BILDKARTEN = {"J", "Q", "K"}


def split(code):
    return code[:-1], code[-1]


def load():
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def erwarteter_code(karte):
    """Die Ziffernfolge, zu der ein Kartenwort codieren muss."""
    wert, farbe = split(karte)
    if wert in BILDKARTEN:
        return None
    farb_ziffer = FARBEN[farbe][1]
    return (farb_ziffer or "") + WERTE[wert]


def erster_konsonant(wort):
    text = mastersystem.normalize(wort)
    for buchstabe in text:
        if buchstabe in mastersystem.SINGLES or buchstabe == "h":
            return buchstabe
    return ""


def check(data, zahlwoerter=None):
    """Liste lesbarer Probleme, leer wenn alles passt."""
    probleme = []
    karten = data.get("karten", [])

    codes = [k["karte"] for k in karten]
    erwartet = {f"{wert}{farbe}" for wert in list(WERTE) + sorted(BILDKARTEN) for farbe in FARBEN}
    fehlend = sorted(erwartet - set(codes))
    if fehlend:
        probleme.append(f"Es fehlen {len(fehlend)} Karten: {', '.join(fehlend)}")
    doppelt = sorted({c for c in codes if codes.count(c) > 1})
    if doppelt:
        probleme.append(f"Doppelte Karten: {', '.join(doppelt)}")

    woerter = [k["wort"] for k in karten]
    mehrfach = sorted({w for w in woerter if woerter.count(w) > 1})
    if mehrfach:
        probleme.append(f"Wort mehrfach vergeben: {', '.join(mehrfach)}")

    for eintrag in karten:
        karte, wort = eintrag["karte"], eintrag["wort"]
        wert, farbe = split(karte)
        if farbe not in FARBEN:
            probleme.append(f"{karte}: unbekannte Farbe")
            continue
        anfang = erster_konsonant(wort)
        if anfang not in FARB_BUCHSTABEN[farbe]:
            erlaubt = ", ".join(sorted(FARB_BUCHSTABEN[farbe]))
            probleme.append(f"{karte:>4}  {wort:<18} beginnt mit '{anfang}', für diese Farbe erlaubt: {erlaubt}")
        if eintrag.get("art") == "person":
            if wert not in BILDKARTEN:
                probleme.append(f"{karte:>4}  {wort:<18} ist als Person markiert, ist aber keine Bildkarte")
            continue
        if wert in BILDKARTEN:
            probleme.append(f"{karte:>4}  {wort:<18} ist eine Bildkarte, muss als Person markiert sein")
            continue
        soll = erwarteter_code(karte)
        ist = mastersystem.encode(wort)
        if ist != soll:
            probleme.append(f"{karte:>4}  {wort:<18} codiert zu {ist or '(nichts)'}, erwartet {soll}")
        if not eintrag.get("bild"):
            probleme.append(f"{karte:>4}  {wort:<18} hat keine Visualisierungsanregung")

    if zahlwoerter:
        for eintrag in karten:
            if eintrag["wort"] in zahlwoerter:
                probleme.append(f"{eintrag['karte']:>4}  {eintrag['wort']} ist schon ein Zahlwort")

    return probleme


def zahlwoerter_aus(data):
    woerter = set()
    for eintrag in data["eintraege"]:
        woerter.add(eintrag["wort"])
        woerter.update(eintrag["alternativen"])
    return woerter


if __name__ == "__main__":
    data = load()
    probleme = check(data, zahlwoerter_aus(mastersystem.load()))
    print(f"{len(data['karten'])} Kartenwörter geladen.")
    if probleme:
        print(f"\n{len(probleme)} Auffälligkeit(en):")
        for problem in probleme:
            print("  " + problem)
    else:
        print("Jedes Wort passt zu Farbe und Wert, keine Kollision mit den Zahlwörtern.")

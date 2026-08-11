# Master-System Trainer

Eine Lern-App fürs Handy, mit der man die 100 Merkwörter des Master-Systems
(Major-System) so weit automatisiert, dass jede Zahl von 0 bis 99 sofort ein
Bild auslöst. Grundlage sind die Merkwörter und Visualisierungsanregungen aus
Christiane Stengers „Warum fällt das Schaf vom Baum?".

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | Die komplette App: Markup, Styles, Logik und die eingebetteten Daten |
| `data/master-system.json` | Die Datenquelle. Hier wird inhaltlich geändert, nirgends sonst |
| `data/mnemonica.json` | Die Stapelreihenfolge für den Kartenbereich |
| `data/kartensystem.json` | Die 52 Kartenwörter nach der Konsonantenregel |
| `tools/mastersystem.py` | Encoder und Konsistenzprüfung, gemeinsame Basis der Skripte |
| `tools/stack.py` | Prüft den Kartenstapel auf Vollständigkeit |
| `tools/karten.py` | Prüft die Kartenwörter gegen Farbe, Wert und die Zahlwörter |
| `tools/inject_data.py` | Schreibt die JSON-Daten in `index.html` |
| `tools/build_docx.py` | Baut den druckbaren Spickzettel |
| `tools/build_icons.py` | Erzeugt die App-Icons |
| `sw.js`, `manifest.webmanifest` | Offline-Betrieb und Homescreen-Symbol |

Nach jeder Änderung an einer Datei unter `data/`:

```
python tools/inject_data.py
python tools/build_docx.py
```

`inject_data.py` bricht ab, wenn ein Merkwort nicht zu seiner Zahl passt. Die
Prüfung rechnet jedes Wort über die Konsonantenregel zurück, so fallen
Tippfehler sofort auf.

## Die Regeln des Systems

Konsonanten tragen die Ziffern, Vokale sind frei:

```
0 = s, z      5 = l
1 = t, d      6 = sch, ch
2 = n         7 = k (auch c, g, ck)
3 = m         8 = f, v, w
4 = r         9 = p, b
```

Doppelkonsonanten zählen einmal (Tanne = 12, nicht 122). Ein vergessenes
Merkwort lässt sich rekonstruieren, indem man die Konsonanten hinschreibt und
die Vokale der Reihe nach durchprobiert.

Der Encoder in `tools/mastersystem.py` und die Funktion `segment()` in
`index.html` setzen dieselben Regeln um und müssen sich gleich verhalten.

## Lernlogik

Jede Zahl ist zwei Karten: Zahl zu Wort und Wort zu Zahl. Beide laufen getrennt
durch eine Leitner-Box mit fünf Fächern (0, 1, 3, 7, 16 Tage). Eine Karte steigt
nur auf, wenn die Antwort richtig **und** schnell war, denn das Ziel ist ein
reflexhafter Abruf. Falsch beantwortete Karten fallen in Fach 1 zurück und
kommen in derselben Sitzung noch einmal.

Der Fortschritt liegt in `localStorage`, pro Gerät. Export und Import als
JSON-Datei gleichen zwei Geräte ab.

## Ketten in „Wort zu Zahl"

In den Einstellungen steht, wie viele Wörter eine Aufgabe zeigt: einzeln, zwei
oder drei. Bei zwei oder drei stehen die Bilder untereinander und die ganze
Ziffernfolge wird am Stück getippt, aus drei Wörtern wird also eine sechs
stellige Zahl. Das ist näher am eigentlichen Zweck des Systems, wo eine Reihe
am Stück zurückgelesen wird.

Gewertet wird trotzdem pro Zahl: jede Karte bekommt ihr eigenes Ergebnis, die
Zeit wird gleichmäßig über die Kette geteilt, und nur die verfehlten Zahlen
kommen in derselben Sitzung noch einmal. Ketten nehmen ausschließlich Zahlen ab
10, weil ein Wort für 0 bis 9 nur eine Ziffer trägt und die Reihe sonst
verrutscht. Solange dafür zu wenig freigeschaltet ist, läuft der Modus einzeln.

## Darstellung

Hell und dunkel sind zwei Fassungen derselben Idee: Tinte und Messing bei Nacht,
warmes Papier und Bronze bei Tag. Alle Farben liegen als Tokens in
`:root[data-theme="dark"]` und `:root[data-theme="light"]`, im Stylesheet steht
kein fester Farbwert mehr. Ein kleines Skript im `<head>` setzt `data-theme`
schon vor dem ersten Bildaufbau, damit nichts aufblitzt.

Voreinstellung ist „Automatisch", die App folgt dann dem Systemmodus und
reagiert auf einen Wechsel im laufenden Betrieb. In den Einstellungen lässt sich
fest auf hell oder dunkel stellen.

## Kartenstapel (Mnemonica)

Zusatzbereich, hinter einem Schalter in den Einstellungen und voreingestellt
aus. Er lernt die Reihenfolge eines gedächtnisgeordneten Kartenspiels, aktuell
Mnemonica von Juan Tamariz aus `data/mnemonica.json`.

Der Trick ist, dass die Positionen 1 bis 52 keine eigene Route brauchen: sie
hängen an den Zahlenbildern, die hier ohnehin sitzen. Position 34 ist Meer,
darauf liegt Pik-Zehn, fertig ist der Anker. Das gibt wahlfreien Zugriff in
beide Richtungen, was eine Route nicht kann, denn dort müsste man immer von
vorn durchlaufen.

Der Bereich läuft in zwei Stufen, weil beides gleichzeitig nicht geht.

**Stufe 1, die Kartenbilder.** Jede Karte bekommt ihr eigenes Bild, unabhängig
davon, wo sie liegt. Drei Modi: Bilder kennenlernen, Karte zu Wort, Wort zu
Karte. Gelernt wird farbweise, also 13 Karten am Stück.

**Stufe 2, die Reihenfolge.** Vier Modi: Reihenfolge kennenlernen, Position zu
Karte, Karte zu Position, Nachbarn. Freigeschaltet wird in Blöcken zu 13, und
ein Block fragt nach, solange die Bilder der dreizehn Karten darin nicht sitzen:
eine Zahl an eine Karte zu hängen, die man selbst noch suchen muss, bringt
nichts. Verboten wird es nicht, „Trotzdem öffnen" steht daneben.

„Heute üben" mischt beide Stufen und nimmt die Bilder zuerst.

Die 52 Kartenwörter stehen in `data/kartensystem.json` und folgen derselben
Konsonantenregel: der erste Konsonant trägt die Farbe (z Kreuz, k Karo, p Pik,
h Herz, gleichwertige Buchstaben erlaubt), die folgenden den Wert. Herz ist der
Sonderfall, weil h keine Ziffer trägt, ein Herzwort codiert deshalb nur den
Wert. Bube, Dame und König gehen nicht phonetisch, weil alle Konsonanten von 0
bis 9 vergeben sind: sie sind Personen, die Art der Person nennt den Rang, der
Anfangslaut die Farbe. `tools/karten.py` rechnet jedes Wort zurück und bricht
ab, wenn eines nicht passt oder mit einem Zahlwort kollidiert.

Wort und Bild gehören der Karte, nicht der Position, und überleben damit einen
Stapelwechsel. Beides lässt sich in der Kartenliste überschreiben. Die
Kartenwerkstatt zerlegt ein eingetipptes Wort und sagt, welche Karte darin
steckt, samt Warnung, wenn es schon als Zahlwort oder bei einer anderen Karte
vergeben ist.

Gelernt wird mit derselben Leitner-Box wie die Zahlen, nur in einem eigenen
Fächersatz unter `state.stack`. Die Zahlenkarten bleiben davon unberührt, und
wer den Bereich nie einschaltet, merkt nichts davon.

## Offline und Updates

Der Service Worker liefert zuerst aus dem Cache und holt die neue Fassung im
Hintergrund. Damit startet die App immer sofort, auch wenn das Telefon gerade
aufwacht und das Netz noch nicht steht. Vorher lief es umgekehrt, und ein
halb verbundenes WLAN ließ `fetch()` hängen statt scheitern: die App blieb weiß,
bis man sie beendet und neu gestartet hat.

Der Preis ist ein Start Verzögerung: nach einem Deployment zeigt der erste Start
noch die alte Fassung und lädt die neue nach, der zweite zeigt sie. In den Cache
kommen nur saubere Antworten vom eigenen Server, damit ein 404 aus einem halb
fertigen Deployment oder die Anmeldeseite eines Hotspots die App nicht ersetzt.

## Eigene Merkwörter

Stenger empfiehlt ausdrücklich, schlecht sitzende Bilder zu ersetzen. Über das
Zahlenraster lässt sich pro Zahl ein eigenes Merkwort und eine eigene
Bildnotiz hinterlegen. Die App prüft dabei, ob das eigene Wort zur Zahl passt,
verbietet aber nichts.

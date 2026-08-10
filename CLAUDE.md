# Arbeitsanweisungen für dieses Repo

Lern-App für das Master-System, gebaut für Malte und seine Frau. Live unter
https://herrohlsen.github.io/master-system-trainer/ (GitHub Pages baut
automatisch bei jedem Push auf `main`).

## Sprache

Deutsch, mit echten Umlauten und ß. Niemals ASCII-Ersatz wie ae/oe/ue/ss, auch
nicht in Code, Kommentaren oder sichtbarem UI-Text. Keine Gedankenstriche im
Geviert. Code-Kommentare auf Englisch, alles andere auf Deutsch.

## Die eine Regel, die alles zusammenhält

`data/master-system.json` ist die einzige Datenquelle für die Zahlen,
`data/mnemonica.json` die Stapelreihenfolge, `data/kartensystem.json` die
Kartenwörter. Nach jeder inhaltlichen Änderung:

```
python tools/inject_data.py     # schreibt die Daten in index.html
python tools/build_docx.py      # baut den Spickzettel neu
```

Niemals den Datenblock in `index.html` direkt bearbeiten, er wird überschrieben.

`tools/mastersystem.py` prüft jedes Merkwort, indem es über die
Konsonantenregel zurückrechnet. `inject_data.py` bricht bei Abweichungen ab.
Bekannte Ausnahme: Stengers Alternativwort „Keks" für 77 codiert eigentlich 770,
das steht als Buchabweichung in einer Ausnahmeliste.

Der Encoder existiert zweimal: `encode()` in `tools/mastersystem.py` und
`segment()` in `index.html`. Beide müssen sich gleich verhalten. Wer einen
ändert, ändert den anderen mit.

`tools/stack.py` prüft den Kartenstapel: 52 Positionen, jede Karte genau einmal.
`tools/karten.py` rechnet jedes Kartenwort über dieselbe Konsonantenregel zurück
und prüft, dass es zu Farbe und Wert passt und nicht schon ein Zahlwort ist.
`inject_data.py` schreibt alle drei Datenblöcke und bricht bei jedem Problem ab.

## Was den Nutzern gehört

Der Lernfortschritt liegt in `localStorage` unter `master-system-v1`, pro Gerät,
ohne Server und ohne Backup. Deshalb:

- Den Speicherschlüssel nicht ändern.
- Das Format nur additiv erweitern. Beim Laden werden fehlende Felder aus
  `DEFAULTS` ergänzt, so überleben alte Stände ein Update.
- Vor Änderungen am Speicher prüfen, ob Export und Import weiter zusammenpassen.

Das gilt auch für eigene Merkwörter und Bildnotizen in `state.custom` sowie für
die Kartenbilder und Verknüpfungen in `state.stack`. Die sind handgeschrieben
und nirgends sonst vorhanden.

## Testen

Kein Test-Framework. Lokaler Server plus Browser:

```
python -m http.server 8765
```

Danach `http://localhost:8765/` öffnen und die Modi durchgehen: Kennenlernen,
beide Abfragerichtungen, Blitz, Zahlenreihe, Werkstatt, Kartenansicht,
Einstellungen. Der Kartenstapel liegt hinter dem Schalter in den Einstellungen
und hat eigene Modi (Kennenlernen, beide Richtungen, Nachbarn, Kartenbilder). In hellem **und** dunklem Modus prüfen, im Stylesheet darf kein
fester Farbwert stehen, alle Farben kommen aus den Theme-Tokens.

Der Service Worker liefert aus dem Cache und aktualisiert im Hintergrund. Nach
einem Deployment also zweimal starten: der erste Start zeigt noch die alte
Fassung und holt die neue, der zweite zeigt sie. Bei größeren Änderungen `CACHE`
in `sw.js` hochzählen, dann wird alles neu vorgeladen.

## Plattform

Entwickelt unter Windows. `tools/build_docx.py` läuft überall (python-docx), der
PDF-Export lief bisher über Word per COM und ist damit Windows-spezifisch. Unter
macOS stattdessen:

```
soffice --headless --convert-to pdf master-system-spickzettel.docx
```

Der Spickzettel landet standardmäßig im Ordner über dem Repo, neben dem Buch.
Ein anderer Zielpfad geht als erstes Argument.

## Was nicht hierher gehört

Kein Geräte-Sync über Supabase. Maltes Pro-Account erlaubt nur ein Projekt, und
das gehört der Schule. Der Abgleich zwischen Geräten läuft bewusst über Export
und Import.

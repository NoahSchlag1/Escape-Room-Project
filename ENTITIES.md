# Escape Room „Raumschiff“ – Entities und ihre Beziehungen

## Die Story in drei Sätzen

Du bist im Flur eines Raumschiffs, durchs Fenster siehst du schon den fremden Zielplaneten.
Eine Durchsage meldet: Zwei Räume weiter hat ein Meteorit das Schiff am Labor gestreift und den Sauerstoffgenerator beschädigt. Repariere ihn, bevor der Timer abläuft.
Die automatische Tür ist durch die Erschütterung kaputt. Du brauchst eine Brechstange, um sie aufzuhebeln.

Den genauen Ablauf beschreibt [DESIGN.md](DESIGN.md).

---

## Überblick: die 6 Entities

| Entity | Was sie ist | Beispiel aus der Story |
|---|---|---|
| **Player** | Der Spielstand dieser Partie | Du: im Flur, Inventar leer, 10:00 min Sauerstoff |
| **Room** | Ein Ort, den man betreten kann (auch die Enden) | Flur, Crew-Quartier, Labor, Ende „Gerettet“ |
| **Item** | Ein Gegenstand, den man aufheben kann | Logbuch, Brechstange, Zugangskarte, Schraubenzieher |
| **Blocker** | Ein Hindernis auf einem Weg, das ein bestimmtes Item braucht | Defekte Automatiktür |
| **Puzzle** | Ein Rätsel in einem Raum, das bei Erfolg ein Item gibt | Spind mit Zahlenschloss |
| **Map** | Alle Wege zwischen den Räumen | Flur → Crew-Quartier → Labor |

Dazu kommen die **Hotspots**. Sie sind keine Spielregel, sondern nur die klickbaren Stellen im Szenenbild (siehe unten).

---

## Die Beziehungen

```
                 ┌──────────────────── Map ────────────────────┐
                 │                                             │
  Player ──steht in (genau 1)──▶ Room ─────Weg─────▶ Room      │
    │  │                          │  │          │              │
    │  │ hat geöffnet (0..n)      │  │ enthält  │ kann blockiert sein (0..1)
    │  └──────────────────────────┼──┼──────────┼─▶ Blocker    │
    │                             │  │ (0..n)   │       │      │
    │ trägt (0..n)        enthält │  ▼          │       │ braucht (genau 1)
    ▼                      (0..n) │ Puzzle      │       ▼      │
   Item ◀─────────────────────────┘  │ gibt (genau 1) ─▶ Item  │
                 └─────────────────────────────────────────────┘
```

| Von | Beziehung | Zu | Anzahl | Beispiel |
|---|---|---|---|---|
| Player | steht in | Room | genau 1 | Du stehst im Flur |
| Player | trägt (Inventar) | Item | 0 bis n | Du trägst das Logbuch |
| Player | hat geöffnet | Blocker | 0 bis n | Du hast die defekte Tür geöffnet |
| Room | enthält am Start | Item | 0 bis n | Im Flur liegen Logbuch und Schraubenzieher |
| Room | enthält | Puzzle | 0 bis n | Im Flur steht der Spind |
| Puzzle | gibt bei Erfolg | Item | genau 1 | Der Spind gibt die Brechstange |
| Map | besteht aus Wegen zwischen | Room → Room | n Wege | Flur → Crew-Quartier |
| Weg | kann blockiert sein durch | Blocker | 0 oder 1 | Flur → Crew-Quartier hat die defekte Tür |
| Blocker | steht auf | Weg | genau 1 | Die defekte Tür steht nur auf Flur → Crew-Quartier |
| Blocker | braucht zum Öffnen | Item | genau 1 | Die Tür braucht die Brechstange |

### Die wichtigsten Gedanken

1. **Der Blocker gehört zum Weg, nicht zum Raum.**
   Die Tür steht nicht „im Flur“ oder „im Crew-Quartier“, sondern *zwischen* den beiden. Deshalb hängt der Blocker an der Verbindung in der Map.

2. **Ein Item ist immer an genau einer Stelle: im Room, im Puzzle oder beim Player.**
   Hebt der Player das Logbuch auf, wandert es vom Raum ins Inventar. Es kann nicht an zwei Orten gleichzeitig sein, und man kann es deshalb auch nicht doppelt aufheben. Benutzen verbraucht ein Item nicht.

3. **Wege haben eine Richtung, und der Blocker steht nur auf der Hinrichtung.**
   Für jede Verbindung gibt es zwei Wege: hin (`flur → crew`, mit Blocker) und zurück (`crew → flur`, frei).
   Der Rückweg braucht keinen Blocker, denn im Crew-Quartier kann man nur stehen, wenn man die Tür schon geöffnet hat.
   Sobald der Player den Blocker geöffnet hat, kann er beliebig hin und zurück laufen.

4. **Blocker und Puzzle sind zwei verschiedene Sperren.**

   |  | Blocker | Puzzle |
   |---|---|---|
   | sperrt | einen **Weg** | ein **Item** |
   | geht auf durch | ein **Item** | eine **Lösung** (Code, Kabelfolge) |
   | steht | auf einem Weg der Map | in einem Room |

   Daraus entsteht die Kette: *Puzzle → gibt Item → öffnet Blocker → nächster Raum.*

5. **Die Enden sind Rooms.**
   „Gerettet“ ist ein Raum, den man über den Weg `labor → ende_gerettet` erreicht. Auf diesem Weg steht der Blocker „beschädigter Generator“, der den Schraubenzieher braucht.
   „Luft aus“ hat keinen Weg dorthin. Läuft der Timer ab, setzt das Spiel den Player direkt in diesen Raum.
   Dafür ist keine neue Entity nötig.

---

## Die Entities im Detail

### Player
Der Player ist das einzige, was sich während des Spiels ändert. Alles, was gespeichert werden muss, hängt an ihm.

| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `current_room_id` | In welchem Raum er gerade steht | `"flur"` |
| `inventory` | Welche Items er trägt | `["logbuch", "brechstange"]` |
| `opened_blockers` | Welche Blocker er schon geöffnet hat | `["defekte_tuer"]` |
| `remaining_seconds` | Wie viel Sauerstoff noch übrig ist. Gespeichert werden die Sekunden statt einer Uhrzeit, damit Fortsetzen auch Tage später funktioniert | `431` |
| `status` | `playing`, `won` oder `lost` | `"playing"` |

Gelöste Puzzles werden **nicht** extra gespeichert. Jedes Puzzle gibt genau ein Item. Trägt der Player die Brechstange, ist der Spind also gelöst.

### Room
| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `id` | Eindeutiger Name | `"flur"` |
| `name` | Anzeigename | `"Flur"` |
| `description` | Text, den der Spieler liest | „Rotes Alarmlicht flackert …“ |
| `image` | Bild für die Szene | `flur.png` |
| `image_after` | Danach-Bild: alle Objekte im veränderten Zustand. Das Spiel blendet daraus nur die Stellen ein, die sich verändert haben (leer = keins) | `Flur after.jpeg` |
| `ending` | Leer für normale Räume, `won` oder `lost` für ein Ende | `""` |
| `map_x`, `map_y` | Position auf der Mini-Map (leer bei den Enden) | `0`, `0` |

### Item
| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `id` | Eindeutiger Name | `"brechstange"` |
| `name` | Anzeigename | `"Brechstange"` |
| `description` | Was man beim Ansehen im Inventar liest | „Schwer, kalt, leicht verbogen.“ |
| `start_room_id` | Wo das Item am Spielanfang liegt (leer, wenn es aus einem Puzzle kommt) | `"flur"` |

### Blocker
| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `id` | Eindeutiger Name | `"defekte_tuer"` |
| `name` | Anzeigename | `"Defekte Automatiktür"` |
| `required_item_id` | Welches Item ihn öffnet | `"brechstange"` |
| `locked_text` | Text, wenn man es ohne Item versucht | „Die Tür klemmt. Mit bloßen Händen keine Chance.“ |
| `opened_text` | Text, wenn man ihn öffnet | „Mit einem Ruck hebelst du die Tür auf.“ |

### Puzzle
| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `id` | Eindeutiger Name | `"spind"` |
| `room_id` | In welchem Raum es steht | `"flur"` |
| `name` | Anzeigename | `"Spind mit Zahlenschloss"` |
| `kind` | Welche Eingabe angezeigt wird: `code` oder `cables` | `"code"` |
| `prompt` | Text beim Öffnen des Rätsels | „Ein vierstelliges Zahlenschloss …“ |
| `solution` | Die richtige Lösung | `"2073"` |
| `reward_item_id` | Welches Item man bei Erfolg bekommt | `"brechstange"` |
| `solved_text` | Text bei richtiger Lösung | „Klick! Der Spind springt auf.“ |
| `wrong_text` | Text bei falscher Lösung | „Das Schloss piept rot.“ |

### Map (die Wege)
Die Map ist keine einzelne Sache, sondern eine **Liste von Wegen**. Jeder Weg ist eine Zeile und hat eine Richtung. Damit man zurückgehen kann, gibt es pro Verbindung zwei Zeilen.

| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `from_room_id` | Startraum | `"flur"` |
| `to_room_id` | Zielraum | `"crew"` |
| `label` | Anzeigetext | `"Tür zum Crew-Quartier"` |
| `blocker_id` | Hindernis auf diesem Weg (leer = frei); steht nur auf der Hinrichtung | `"defekte_tuer"` |

### Hotspot (nur Darstellung, keine Spielregel)
Ein Hotspot ist eine klickbare Fläche im Szenenbild. Er entscheidet nichts selbst, sondern **verweist** auf eine Entity. Was dann passiert, regeln Item, Puzzle und Blocker.

| Attribut | Bedeutung | Beispiel |
|---|---|---|
| `id` | Eindeutiger Name | `"wandfach"` |
| `room_id` | In welchem Bild er liegt | `"flur"` |
| `label` | Name beim Überfahren/Anklicken | `"Wandfach"` |
| `x`, `y`, `w`, `h` | Fläche im Bild in Prozent (0–100) | `62, 40, 10, 12` |
| `text` | Text beim Anklicken | „Ein kleines Wandfach …“ |
| `done_text` | Text, wenn Item schon genommen bzw. Puzzle gelöst | „Das Wandfach ist leer.“ |
| `item_id` | Klick hebt dieses Item auf | `"logbuch"` |
| `puzzle_id` | Klick öffnet dieses Puzzle | |
| `to_room_id` | Klick nimmt den Weg in diesen Raum (inkl. Blocker-Prüfung) | |
| `popup` | Besonderes Pop-up der Oberfläche, z. B. `cable_note` (Notiz mit Kabelplan) | |

Höchstens eine der letzten drei Spalten ist gefüllt. Sind alle leer, zeigt der Hotspot nur Text an (Fenster, Feuerlöscher …).

---

## Statische Daten vs. Spielstand

| Ändert sich nie (Spielwelt) | Ändert sich beim Spielen (Spielstand) |
|---|---|
| Room, Item, Blocker, Puzzle, Map, Hotspot | Player |
| `rooms.csv`, `items.csv`, `blockers.csv`, `puzzles.csv`, `exits.csv`, `hotspots.csv` | `save.csv` |
| Ist für jeden Spieler gleich | Wird nach jeder Aktion gespeichert, beim Neustart gelöscht |

Daraus folgt: **„Die Tür ist offen“ ist kein Attribut der Tür, sondern des Players.**
Die Tür selbst bleibt in `blockers.csv` immer gleich. Gespeichert wird nur: *Dieser Player hat die Tür schon geöffnet.*

---

## Durchgespielt: der Flur

1. Der Player steht im **Room** `flur`. Die **Map** zeigt einen Weg `flur → crew` mit **Blocker** `defekte_tuer`.
2. Er klickt auf die Tür.
   Prüfung: Ist der Blocker schon geöffnet? Nein. Hat der Player das nötige **Item** `brechstange`? Nein.
   → `locked_text` wird angezeigt, **nichts am Spielstand ändert sich** (A1).
3. Er klickt auf das Wandfach. Das **Item** `logbuch` wandert vom Room ins Inventar. Im Logbuch liest er: Baujahr 2073.
4. Er klickt auf den Spind. Das **Puzzle** `spind` öffnet sich, er gibt `2073` ein.
   → `solved_text`, und das **Item** `brechstange` kommt ins Inventar.
5. Er klickt erneut auf die Tür. Jetzt hat er das Item.
   → `opened_text`, `defekte_tuer` wird beim Player als geöffnet gespeichert, er steht in `crew`. Die Brechstange bleibt im Inventar (A2).
6. Er nimmt den Rückweg `crew → flur` und geht wieder ins Crew-Quartier. Die Tür ist **schon offen**. Das ist die „dauerhafte Folge“ aus dem Brief.

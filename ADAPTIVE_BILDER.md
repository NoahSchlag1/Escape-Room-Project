# Adaptive Bilder: Räume, die sich verändern

## Die Idee: ein „Danach“-Bild pro Raum

Im Flur ändern sich vier Dinge unabhängig voneinander. Für jede Kombination ein eigenes Bild wären 2⁴ = 16 Bilder.
Stattdessen gibt es pro Raum **ein Danach-Bild**, auf dem **alle** Veränderungen schon zu sehen sind.
Das Spiel nimmt aus dem Danach-Bild nur den Bereich des Objekts, das sich gerade verändert hat, und legt ihn mit weichem Rand über das Grundbild.

| Raum | Grundbild (gibt es schon) | Neues Danach-Bild |
|---|---|---|
| Flur | `Flur.jpeg` | **`Flur after.jpeg`** |
| Crew-Quartier | `Crew Cabin.jpeg` | **`Crew Cabin after.jpeg`** |
| Labor | `Laboratory.jpeg` | nicht nötig: Sobald der Generator repariert ist, beginnt das Outro |

Du musst also nur **2 Bilder** erzeugen.

## Was sich verändert

| Raum | Objekt | Ändert sich, wenn … | Im Danach-Bild |
|---|---|---|---|
| Flur | Wandfach | das Logbuch genommen wurde | Klappe offen, Fach leer |
| Flur | Schraubenzieher am Boden | er genommen wurde | Boden leer |
| Flur | Spind | der Code eingegeben wurde | Spindtür offen, Spind leer, Tastenfeld leuchtet grün |
| Flur | Tür zum Crew-Quartier | sie mit der Brechstange aufgehebelt wurde | Tür aufgestemmt, man sieht in den nächsten Raum |
| Crew | Wandpanel | das Kabelrätsel gelöst wurde | Kabel stecken in den Buchsen, kleines Fach offen und leer |
| Crew | Sicherheitsschott | es mit der Zugangskarte geöffnet wurde | Schott offen, Kartenleser leuchtet grün |

## Wichtig, damit es funktioniert

1. **Erst die Grundbilder fertig machen** (z. B. das Umstylen im No-Man's-Sky-Stil).
   Das Danach-Bild muss aus dem **fertigen** Grundbild entstehen, sonst passt der Stil nicht zusammen.
2. In Gemini **das fertige Grundbild hochladen** und den Bearbeitungs-Prompt unten schicken.
   Gemini soll das Bild **bearbeiten**, nicht neu malen.
3. Prüfen: Alles außer den genannten Objekten muss **exakt gleich** bleiben, also Kamerawinkel, Licht, Farben und alle anderen Objekte.
   Hat sich etwas verschoben, noch einmal mit dem Zusatz versuchen:
   *„The rest of the image must stay pixel-identical. Do not move, add or remove anything else.“*
4. Gleiche Größe wie das Grundbild (1376×768), gespeichert unter dem Dateinamen oben in `images/`.

---

## Prompt: `Flur after.jpeg`

*(Grundbild `Flur.jpeg` hochladen)*

> Edit this image. Change ONLY the following four things and keep everything else exactly the same – same camera angle, framing, lighting, colors, style and every other object in the same position:
> 1. The small wall compartment on the right side of the cylindrical tank below the window: its hatch is now open, the compartment inside is empty.
> 2. The screwdriver on the floor below the window is gone; the floor there is empty.
> 3. The tall locker on the left: its door is now swung open and the locker is empty inside; the small keypad on it glows green.
> 4. The broken sliding door on the far right: it has been forced open with a crowbar, now wide enough to walk through; you can see a dimly lit room behind it. The sparking control panel next to it stays.
> No text, no letters, no watermark.

## Prompt: `Crew Cabin after.jpeg`

*(Grundbild `Crew Cabin.jpeg` hochladen)*

> Edit this image. Change ONLY the following two things and keep everything else exactly the same – same camera angle, framing, lighting, colors, style and every other object in the same position:
> 1. The open electrical wall panel in the center: the four cables are now plugged in – red into socket 1, yellow into socket 2, green into socket 3, blue into socket 4 – and a small compartment in the panel below the sockets is open and empty.
> 2. The heavy security bulkhead on the far right: it has slid open, and you can see a softly lit laboratory behind it; the card reader next to it glows green.
> No text, no letters, no watermark.

---

## Danach

Leg die zwei Bilder in `images/`. Das Überblenden ist schon eingebaut (Branch `design-futuristic`), sie werden automatisch verwendet.
Ragt ein verändertes Objekt über seine Klickfläche hinaus (z. B. eine weit aufschwingende Spindtür), wird es am Rand abgeschnitten.
Schick mir dann das Bild, ich vergrößere die Fläche in `data/hotspots.csv`.
Fehlt ein Danach-Bild, zeigt das Spiel einfach weiter das Grundbild, nichts geht kaputt.

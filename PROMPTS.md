# Bild-Prompts: vorhandene Bilder umstylen (No Man's Sky, Baujahr 2073)

Wir erzeugen **keine neuen Motive**. Jedes vorhandene Bild aus `images/` wird nur umgestylt:
gleicher Inhalt, gleicher Bildaufbau, gleiche Positionen, aber futuristisch statt retro.
So passen die Klickflächen in `data/hotspots.csv` weiterhin.

Die Prompts sind auf Englisch, weil Bildgeneratoren damit zuverlässiger arbeiten.

## So gehst du vor

1. Öffne in Gemini einen neuen Chat und **lade das Originalbild hoch** (z. B. `images/Flur.jpeg`).
2. Schreib den **Umstyle-Prompt** unten und hänge den Teil für dieses Bild an.
3. Speichere das Ergebnis **unter genau demselben Dateinamen** in `images/` und ersetze damit das alte Bild.
4. Mach alle Bilder im selben Chat. Ab dem zweiten Bild schreibst du dazu: *„Same style as the previous image.“*
5. Schick mir danach die neuen Raumbilder (Flur, Crew Cabin, Laboratory). Ich prüfe, ob die Klickflächen noch sitzen.

Verschiebt Gemini Objekte, hilft der Zusatz: *„Do not move, add or remove any objects.“*

## Umstyle-Prompt (bei jedem Bild verwenden)

> Restyle this exact image. Keep the composition, camera angle, framing and every object in exactly the same position and size. Only change the visual style: futuristic sci-fi of the year 2073 in the style of No Man's Sky. Replace retro elements (rivets, CRT monitors, chunky toggle switches, beige riveted metal) with sleek, smooth composite surfaces, seamless rounded panels, slim glowing holographic displays and thin light strips. Muted, dusty color palette of rust red, ochre and burnt orange with small desaturated teal accents; no bright pink or neon colors. Hazy atmosphere, soft volumetric light, painterly concept-art rendering. No text, no letters, no watermark.

---

## Intro (im Weltall)

**`Intro 1.jpeg`**: Blick aus dem Cockpit auf den Planeten
> Keep: the cockpit interior with its three large front windows, the consoles in front and on the sides, and the pilot seat on the right. Through the windows the red planet with canyons and dunes, seen from high orbit. Turn the consoles into sleek 2073 controls with holographic screens. Remove the small creatures on the dunes.

**`Intro 2.jpeg`**: Das Schiff fliegt auf den Planeten zu
> Keep: the spaceship in the center seen from behind, flying toward the planet, three glowing engines on the left side, the curved red planet filling the right half, black space with stars and distant galaxies on the left. Make the ship a sleek 2073 design with a smooth hull, no rivets and no old screens, keeping its shape and position. Turn the bright pink atmosphere glow into a thin dusty orange haze.

**`Intro 3.jpeg`**: Der Meteorit streift das Schiff
> Keep: the same spaceship and planet as before, the meteorite on the right scraping along the side of the hull, the torn gash with orange sparks flying to the left and the white plume of escaping air. Make the ship the same sleek 2073 design as in the previous image. Turn the bright pink atmosphere glow into a thin dusty orange haze.

---

## Räume (mit Klickflächen – Positionen auf keinen Fall verändern)

**`Flur.jpeg`**: Flur
> Keep exactly in place: the large window in the upper center with the red planet, the tall locker with the small keypad on the left, the red fire extinguisher on the far left wall, the cylindrical tank below the window with the small wall compartment and latch on its right side, the screwdriver on the floor below the window, the broken sliding door on the right with the sparking control panel, and the red emergency lights on the ceiling.

**`Crew Cabin.jpeg`**: Crew-Quartier
> Keep exactly in place: the open door on the left, the framed crew photo on the wall, the bunk bed with the paper note pinned to it, the diary on the small shelf below the bed, the open wall panel in the center with four numbered sockets and the red, yellow, green and blue cables, the round porthole with the red planet, the coffee machine on the small table, the knocked-over mug on the floor, and the locked bulkhead on the right with the red glowing card reader.

**`Laboratory.jpeg`**: Labor mit Generator
> Keep exactly in place: the open door on the left, the three glowing green glass tanks, the crack in the wall in the upper center with the foam patch and the red warning light, the small computer terminal, the damaged smoking oxygen generator on the right with its loose cover panel, and the two wrenches on the floor. Optional: replace the creatures in the tanks with rock and plant samples.

---

## Outro und Enden

**`Outro 1.jpeg`**: Eintritt in die Atmosphäre
> Keep: the spaceship in the center wrapped in flames as it enters the atmosphere, the fiery trail behind it, the red desert with canyons below and the dark sky above. Make the ship the same sleek 2073 design as in the intro.

**`Outro 2.jpeg`**: Das Schiff über dem Planeten
> Keep: the spaceship on the left seen from behind with its three glowing engines, the curved red planet with canyons on the right, black space with stars. Make the ship the same sleek 2073 design as in the intro. Turn the bright pink atmosphere glow into a thin dusty orange haze.

**`Outro saved.jpeg`**: Endbildschirm „Saved“
> Keep: the landed spaceship on its legs in the center right, the tall rock spires on the left, the sunset sky with two small moons, the red desert in the foreground. Make the ship the same sleek 2073 design as in the intro. Optional: remove the small creatures in the foreground.

**`Outro Out of oxygen.jpeg`**: Endbildschirm „Out of Air“
> Keep: the dark corridor in central perspective, the frosted windows on both sides with ice, the red ceiling light, the window at the end with the planet, the two small warning screens on the left wall showing a flat oxygen line and a warning sign. Turn the screens into slim holographic displays.

---

## Wenn ein Item noch im Bild zu sehen ist, obwohl man es schon genommen hat

Im Flur sieht man den Schraubenzieher am Boden auch dann noch, wenn er schon im Inventar ist. Nur seine Markierung verschwindet. Dafür gibt es zwei Lösungen:
- Er bleibt im Bild. Klickt man ihn noch einmal an, erscheint „This is where the screwdriver was.“ Das ist schon eingebaut.
- Du erzeugst zusätzlich eine Version des Flur-Bildes ohne Schraubenzieher. Dann kann das Spiel je nach Inventar das passende Bild zeigen. Das können wir später einbauen.

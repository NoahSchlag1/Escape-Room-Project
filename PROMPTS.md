# Bild-Prompts für die Szenen

Die Prompts sind auf Englisch, weil Bildgeneratoren damit zuverlässiger arbeiten.

## So gehst du vor

1. Erzeuge alle Bilder **im selben Chat bzw. Projekt**. Dann bleibt der Stil einheitlich.
   Nimm zuerst den Flur. Bei allen weiteren Bildern schreibst du dazu: *„Same style as the previous image.“*
2. Wähle das Format **16:9** (z. B. 1792×1024 oder 1600×900).
3. Speichere jedes Bild als **PNG mit genau dem angegebenen Dateinamen** in `images/`.
4. Starte das Spiel und schalte in der Seitenleiste **„Klickbereiche anzeigen“** ein.
   Liegen die Objekte im Bild woanders als die Klickflächen, passt du `x`, `y`, `w`, `h` in `data/hotspots.csv` an (Angaben in Prozent der Bildbreite bzw. Bildhöhe).
   Das ist einfacher, als den Bildgenerator auf den Pixel genau zu steuern.

## Gemeinsamer Stil (an jeden Prompt anhängen)

> Cinematic semi-realistic digital painting, retro-futuristic 1970s spaceship design (chunky switches, rounded panels, beige and brushed steel surfaces, small CRT screens), muted teal and steel color palette with warm red emergency light accents, soft volumetric lighting, slightly worn and lived-in, wide 16:9 composition, eye-level view, no people, no text, no letters, no watermark.

Das Schiff ist von 1973. Deshalb passt der Retro-Sci-Fi-Look zum Logbuch.

---

## Intro

**`intro_1.png`**: Der Zielplanet in Nahaufnahme
> Extreme close-up of an alien planet surface seen from low orbit, red and rust-colored like Mars, deep canyons and dunes, thin pink atmosphere glowing at the horizon. Barely visible on the surface: strange six-legged creatures casting long shadows. Mysterious, awe-inspiring mood. + Stil

**`intro_2.png`**: Das Schiff auf dem Weg dorthin
> A small retro-futuristic 1970s spaceship flying through dark space toward a large red Mars-like planet, the planet fills the right half of the image, stars in the background, the ship's engines glow warm orange. Calm before the storm. + Stil

**`intro_3.png`**: Der Meteorit streift das Schiff
> A glowing meteorite grazing along the side of a retro-futuristic spaceship, not a direct hit but a glancing blow: it scrapes across the hull leaving a long torn gash, a trail of sparks and metal fragments spraying into space, a thin white plume of escaping air from the damaged section. The meteorite continues past the ship on its trajectory. The red planet in the background. Dramatic, tense, frozen-moment mood. + Stil

---

## Räume (mit Klickflächen)

Die Positionsangaben im Prompt sind nur grobe Vorgaben. Feinjustiert wird hinterher in `hotspots.csv`.

**`flur.png`**: Flur
> Interior of a spaceship corridor, front view of one wall. In the upper center a large rectangular window showing the red alien planet, close and huge. On the left side a tall narrow metal locker with a small 4-digit combination lock, next to it, further left and lower, a red fire extinguisher mounted on the wall. To the right of the window a small closed wall compartment with a latch. On the far right edge a heavy sliding automatic door, stuck slightly open, with sparks from a broken control panel. On the floor below the window, small and easy to overlook, a screwdriver with a star-shaped tip. Red emergency lights flashing, alarm atmosphere. + Stil

**`crew.png`**: Crew-Quartier
> Crew quarters on a retro-futuristic spaceship, front view of one wall. On the far left edge a sliding door back to the corridor. Left of center a bunk bed with a crumpled paper note pinned to it, below it on a small shelf a personal diary. Upper left center a framed photo on the wall, upper right center a small round porthole showing the red planet. In the exact center an open electrical wall panel with four numbered sockets and four loose cables in red, yellow, green and blue. Right of center a small coffee machine on a counter. On the far right edge a heavy locked security bulkhead with a card reader glowing red. Dim blue emergency lighting, a knocked-over mug on the floor. + Stil

**`labor.png`**: Labor mit Generator
> Research laboratory on a retro-futuristic spaceship, front view. On the left several tall glowing green glass tanks, each containing a strange six-legged alien creature floating in liquid. In the upper center a jagged crack in the wall, patched with emergency foam, from a meteorite impact. On the right a large bulky oxygen generator machine, damaged and smoking, its cover panel held by star-shaped special screws, warning lights blinking. On the far left edge the open bulkhead door leading back. Tense atmosphere, haze in the air. + Stil

---

## Enden und Outro

**`outro_1.png`**: Eintritt in die Atmosphäre
> A retro-futuristic spaceship entering the atmosphere of a red Mars-like planet, glowing heat shield, flames trailing behind, red sky and dunes below. Triumphant mood. + Stil

**`outro_2.png`**: Gelandet
> View through a spaceship window onto the surface of a red alien planet after landing: rolling red dunes, strange rock formations, a pink sky with two small moons. Curious six-legged alien creatures approaching the ship, friendly and strange. Hopeful, wondrous mood. + Stil

**`ende_gerettet.png`**: Endbildschirm „Gerettet“
> The spaceship standing safely on the red alien planet at sunset, landing legs extended, warm light from its windows, small six-legged creatures gathered curiously around it. Peaceful, victorious mood. + Stil

**`ende_luft_aus.png`**: Endbildschirm „Luft aus“
> The spaceship corridor in darkness, only a single red emergency light, frost on the window, the red planet outside unreachable, a blinking warning screen showing a flat oxygen line. Quiet, melancholic, game-over mood. + Stil

---

## Wenn ein Item noch im Bild zu sehen ist, obwohl man es schon genommen hat

Im Flur sieht man den Schraubenzieher am Boden auch dann noch, wenn er schon im Inventar ist. Dafür gibt es zwei Lösungen:
- Er bleibt im Bild. Klickt man ihn noch einmal an, erscheint „Hier lag der Schraubenzieher.“ Das ist schon eingebaut.
- Du erzeugst eine zweite Version des Bildes ohne Schraubenzieher. Das Spiel müsste dann je nach Inventar das passende Bild wählen. Das können wir später einbauen.

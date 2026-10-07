# Bild-Prompts: vorhandene Bilder umstylen (No Man's Sky, Baujahr 2073)

Wir erzeugen **keine neuen Motive**. Jedes vorhandene Bild aus `images/` wird nur umgestylt:
gleicher Inhalt, gleicher Bildaufbau, gleiche Positionen, aber futuristisch statt retro.
So passen die Klickflächen in `data/hotspots.csv` weiterhin.

Die Prompts sind auf Englisch, weil Bildgeneratoren damit zuverlässiger arbeiten.

## So gehst du vor

1. Öffne in Gemini **für jedes Bild einen neuen Chat** und **lade das Originalbild hoch** (z. B. `images/Intro 2.jpeg`).
   Kein „Same style as the previous image“: Gemini übernimmt dabei sonst auch Inhalte aus dem vorherigen Bild,
   z. B. ein zweites Raumschiff. Der einheitliche Stil kommt allein vom gleichen Umstyle-Prompt.
2. Schreib den **Umstyle-Prompt** unten und hänge den Teil für dieses Bild an.
3. **Vergleiche das Ergebnis mit dem Original:** gleiche Anzahl Objekte, gleiche Positionen?
   Wenn nicht, im selben Chat nachschieben: *„Wrong: you added/moved objects. Use only my uploaded image as the base. Keep exactly the same objects – nothing added, nothing removed – and only change the style.“*
4. Speichere das Ergebnis **unter genau demselben Dateinamen** in `images/` und ersetze damit das alte Bild.
5. Schick mir danach die neuen Raumbilder (Flur, Crew Cabin, Laboratory). Ich prüfe, ob die Klickflächen noch sitzen.

## Das Schiff muss überall gleich aussehen

Das Schiff kommt in fünf Bildern vor: Intro 2, Intro 3, Outro 1, Outro 2 und Outro saved.
Damit es überall identisch ist:

1. **Mach `Intro 2.jpeg` zuerst.** Das fertige Bild ist ab dann die **Vorlage für das Schiff**.
2. Bei Intro 3, Outro 1, Outro 2 und Outro saved lädst du **zwei Bilder** hoch:
   - **Bild 1:** das Originalbild, das umgestylt werden soll
   - **Bild 2:** dein fertiges neues `Intro 2.jpeg` als Vorlage für das Schiff
3. In jedem dieser Prompts steht außerdem dieselbe feste Schiffsbeschreibung (Form, Farben, Streifen, Triebwerke).
4. Vergleich das Schiff mit der Vorlage. Weicht es ab, im selben Chat nachschieben:
   *„The ship does not match image 2. Make it identical to the ship in image 2 – same shape, colors, stripes, cockpit and engines.“*

## Umstyle-Prompt (bei jedem Bild verwenden)

> Restyle this exact uploaded image – use only this image as the base. Keep the composition, camera angle, framing and every object in exactly the same position and size. Do not add, duplicate or remove anything: the result must contain exactly the same objects as the uploaded image. Only change the visual style: futuristic sci-fi of the year 2073 in the style of No Man's Sky. Replace retro elements (rivets, CRT monitors, chunky toggle switches, beige riveted metal) with sleek, smooth composite surfaces, seamless rounded panels, slim glowing displays and thin light strips. Holographic displays exist only inside the ship, built into its consoles and walls – never outside: no holograms, floating screens, HUD overlays or interface graphics in space, in the sky, on the planet or on the outer hull. Muted, dusty color palette of rust red, ochre and burnt orange with small desaturated teal accents; no bright pink or neon colors. Hazy atmosphere, soft volumetric light, painterly concept-art rendering. No text, no letters, no watermark.

---

## Intro (im Weltall)

**`Intro 1.jpeg`**: Blick aus dem Cockpit auf den Planeten
> Keep: the cockpit interior with its three large front windows, the consoles in front and on the sides, and the pilot seat on the right. Through the windows the red planet with canyons and dunes, seen from high orbit. Turn the consoles into sleek 2073 controls with holographic screens. Remove the small creatures on the dunes.

**`Intro 2.jpeg`**: Das Schiff fliegt auf den Planeten zu
> The image contains exactly ONE spaceship – keep it as the only ship, do not add a second one. Keep: this single ship in the center seen from behind, flying toward the planet, with its three glowing engines on the left side; the curved red planet filling the right half; black space with stars and distant galaxies on the left. Restyle this same ship in place, keeping its silhouette, size and position, to match this exact design: a compact, rounded shuttle built in 2073 with a smooth matte off-white composite hull, two rust-orange stripes along each side, dark grey seamless panel joints, a tinted dark cockpit canopy at the front, and three round engines at the rear – one large in the middle, two smaller ones beside it – glowing pale orange-white. No rivets, no screens, no markings or text on the hull. Turn the bright pink atmosphere glow into a thin dusty orange haze.

**`Intro 3.jpeg`**: Der Meteorit streift das Schiff
> The image contains exactly ONE spaceship and ONE meteorite – do not add any other ships or rocks. Keep: this single ship in the center seen from behind with its three glowing engines, the meteorite on the right scraping along the side of the hull, the torn gash with orange sparks flying to the left, the white plume of escaping air, and the curved red planet on the right. Restyle this same ship in place, keeping its silhouette, size and position, to match this exact design: a compact, rounded shuttle built in 2073 with a smooth matte off-white composite hull, two rust-orange stripes along each side, dark grey seamless panel joints, a tinted dark cockpit canopy at the front, and three round engines at the rear – one large in the middle, two smaller ones beside it – glowing pale orange-white. No rivets, no screens, no markings or text on the hull. Image 2 is the reference for the ship: the ship must look exactly like the ship in image 2 – same hull shape, colors, stripes, cockpit and engines. Take only the ship's appearance from image 2, nothing else. Turn the bright pink atmosphere glow into a thin dusty orange haze.

---

## Räume (mit Klickflächen – Positionen auf keinen Fall verändern)

**`Flur before.jpeg`**: Flur
> Keep exactly in place: the large window in the upper center with the red planet, the tall locker with the small keypad on the left, the red fire extinguisher on the far left wall, the cylindrical tank below the window with the small wall compartment and latch on its right side, the screwdriver on the floor below the window, the broken sliding door on the right with the sparking control panel, and the red emergency lights on the ceiling.

**`Cabin Crew before.jpeg`**: Crew-Quartier
> Keep exactly in place: the open door on the left, the framed crew photo on the wall, the bunk bed with the paper note pinned to it, the diary on the small shelf below the bed, the open wall panel in the center with four numbered sockets and the red, yellow, green and blue cables, the round porthole with the red planet, the coffee machine on the small table, the knocked-over mug on the floor, and the locked bulkhead on the right with the red glowing card reader.

**`Laboratory.jpeg`**: Labor mit Generator
> Keep exactly in place: the open door on the left, the three glowing green glass tanks, the crack in the wall in the upper center with the foam patch and the red warning light, the small computer terminal, the damaged smoking oxygen generator on the right with its loose cover panel, and the two wrenches on the floor. Optional: replace the creatures in the tanks with rock and plant samples.

---

## Danach-Bilder (veränderte Räume)

Pro Raum gibt es ein zweites Bild, auf dem **alle Veränderungen auf einmal** zu sehen sind.
Das Spiel blendet daraus nur die Stelle ein, die sich gerade verändert hat (z. B. nur den offenen Spind).
Einzelbilder pro Zustand brauchst du nicht. Für das Labor gibt es kein Danach-Bild.

**Reihenfolge:** Erst das Grundbild umstylen (oben). Dann **genau dieses neue Grundbild** in einem neuen Chat hochladen
und mit dem Prompt unten bearbeiten lassen. Nur so passen beide Bilder pixelgenau übereinander.
Speichere das Ergebnis unter dem angegebenen Dateinamen in `images/`, in gleicher Größe wie das Grundbild.

Hat sich außer den genannten Objekten etwas verändert, im selben Chat nachschieben:
*„The rest of the image must stay pixel-identical. Do not move, add or remove anything else.“*

### `Flur after.jpeg`

*(Grundbild `Flur before.jpeg` hochladen)*

> Edit this image. Change ONLY the following four things and keep everything else exactly the same – same camera angle, framing, lighting, colors, style and every other object in the same position:
> 1. The small wall compartment on the right side of the cylindrical tank below the window: its hatch is now open, the compartment inside is empty.
> 2. The screwdriver on the floor below the window is gone; the floor there is empty.
> 3. The tall locker on the left: its door is now swung open and the locker is empty inside; the small keypad on it glows green.
> 4. The broken sliding door on the far right: it has been forced open with a crowbar, now wide enough to walk through; you can see a dimly lit room behind it. The sparking control panel next to it stays.
> No text, no letters, no watermark.

### `Cabin crew after.jpeg`

*(Grundbild `Cabin Crew before.jpeg` hochladen)*

> Edit this image. Change ONLY the following two things and keep everything else exactly the same – same camera angle, framing, lighting, colors, style and every other object in the same position:
> 1. The open electrical wall panel in the center: the four cables are now plugged in – red into socket 1, yellow into socket 2, green into socket 3, blue into socket 4 – and a small compartment in the panel below the sockets is open and empty.
> 2. The heavy security bulkhead on the far right: it has slid open, and you can see a softly lit laboratory behind it; the card reader next to it glows green.
> No text, no letters, no watermark.

---

## Outro und Enden

**`Outro 1.jpeg`**: Eintritt in die Atmosphäre
> The image contains exactly ONE spaceship – do not add another. Keep: this single ship in the center wrapped in flames as it enters the atmosphere, the fiery trail behind it, the red desert with canyons below and the dark sky above. Restyle this same ship in place, keeping its silhouette, size and position, to match this exact design: a compact, rounded shuttle built in 2073 with a smooth matte off-white composite hull, two rust-orange stripes along each side, dark grey seamless panel joints, a tinted dark cockpit canopy at the front, and three round engines at the rear – one large in the middle, two smaller ones beside it – glowing pale orange-white. No rivets, no screens, no markings or text on the hull. Image 2 is the reference for the ship: the ship must look exactly like the ship in image 2 – same hull shape, colors, stripes, cockpit and engines. Take only the ship's appearance from image 2, nothing else.

**`Outro 2.jpeg`**: Das Schiff über dem Planeten
> The image contains exactly ONE spaceship – do not add another. Keep: this single ship on the left seen from behind with its three glowing engines, the curved red planet with canyons on the right, black space with stars. Restyle this same ship in place, keeping its silhouette, size and position, to match this exact design: a compact, rounded shuttle built in 2073 with a smooth matte off-white composite hull, two rust-orange stripes along each side, dark grey seamless panel joints, a tinted dark cockpit canopy at the front, and three round engines at the rear – one large in the middle, two smaller ones beside it – glowing pale orange-white. No rivets, no screens, no markings or text on the hull. Image 2 is the reference for the ship: the ship must look exactly like the ship in image 2 – same hull shape, colors, stripes, cockpit and engines. Take only the ship's appearance from image 2, nothing else. Turn the bright pink atmosphere glow into a thin dusty orange haze.

**`Outro saved.jpeg`**: Endbildschirm „Saved“
> The image contains exactly ONE spaceship – do not add another. Keep: this single landed ship on its legs in the center right, the tall rock spires on the left, the sunset sky with two small moons, the red desert in the foreground. Restyle this same ship in place, keeping its silhouette, size and position, to match this exact design: a compact, rounded shuttle built in 2073 with a smooth matte off-white composite hull, two rust-orange stripes along each side, dark grey seamless panel joints, a tinted dark cockpit canopy at the front, and three round engines at the rear – one large in the middle, two smaller ones beside it – glowing pale orange-white. No rivets, no screens, no markings or text on the hull. Image 2 is the reference for the ship: the ship must look exactly like the ship in image 2 – same hull shape, colors, stripes, cockpit and engines. Take only the ship's appearance from image 2, nothing else. Optional: remove the small creatures in the foreground.

**`Outro out of oxygen.jpeg`**: Endbildschirm „Out of Air“
> Keep: the dark corridor in central perspective, the frosted windows on both sides with ice, the red ceiling light, the window at the end with the planet, the two small warning screens on the left wall showing a flat oxygen line and a warning sign. Turn the screens into slim holographic displays.

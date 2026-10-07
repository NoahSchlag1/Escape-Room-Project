# Bild-Prompts für die Szenen (Stil: No Man's Sky)

Die Prompts sind auf Englisch, weil Bildgeneratoren damit zuverlässiger arbeiten.

## So gehst du vor

1. Erzeuge alle Bilder **im selben Chat**. Dann bleibt der Stil einheitlich.
   Fang mit dem Flur an. Bei allen weiteren Bildern schreibst du dazu: *„Same style as the previous image.“*
2. Wähle das Format **16:9** (z. B. 1376×768 oder 1792×1024).
3. Speichere jedes Bild **unter genau dem angegebenen Dateinamen** in `images/` und ersetze damit das alte Bild.
   Dann musst du im Code nichts ändern.
4. Starte das Spiel und prüfe, ob die leuchtenden Sechsecke auf den richtigen Objekten sitzen.
   Wenn nicht, passt du `x`, `y`, `w`, `h` in `data/hotspots.csv` an (Prozent der Bildbreite bzw. Bildhöhe).
   Am einfachsten schickst du mir die neuen Bilder, dann passe ich die Klickflächen an.

**Wichtig für die Raumbilder:** Die Objekte sollten ungefähr an denselben Stellen liegen wie bisher, so wie es in den Prompts beschrieben ist.
Dann bleiben die Klickflächen fast unverändert.

## Gemeinsamer Stil (an jeden Prompt anhängen)

> Vibrant painterly sci-fi illustration in the style of No Man's Sky and 1970s science-fiction paperback cover art. Bold, saturated colors: teal, amber orange, magenta and soft pastel sky tones. Clean futuristic surfaces with chunky panel lines, rounded hatches and glowing holographic displays, soft atmospheric haze and light rays, a sense of wonder. Wide 16:9 composition, eye-level view, no people, no text, no letters, no watermark.

---

## Intro

**`Intro 1.jpeg`**: Der Zielplanet in Nahaufnahme
> Close-up of a huge alien planet seen from orbit: a saturated red-orange surface like Mars with deep canyons and dunes, a glowing pastel pink-and-teal atmosphere at the horizon, a thin planetary ring and two small moons in a colorful nebula sky. Awe-inspiring, mysterious mood. + Stil

**`Intro 2.jpeg`**: Das Schiff auf dem Weg dorthin
> A sleek retro-futuristic spaceship with bold orange and white hull panels flying through a colorful nebula toward the large red ringed planet, which fills the right half of the image. The engines glow bright teal. Calm before the storm. + Stil

**`Intro 3.jpeg`**: Der Meteorit streift das Schiff
> A glowing meteorite grazing along the side of the orange-and-white spaceship, not a direct hit but a glancing blow: it scrapes across the hull leaving a long torn gash, a bright trail of sparks and metal fragments, a thin white plume of escaping air. The meteorite continues past the ship. The red ringed planet and a colorful nebula in the background. Dramatic, frozen-moment mood. + Stil

---

## Räume (mit Klickflächen)

**`Flur.jpeg`**: Flur
> Interior of a futuristic spaceship corridor, front view of one wall. In the upper center a large rectangular window showing the huge red ringed planet. On the left side a tall narrow locker with a small glowing 4-digit keypad lock; further left and lower, a red fire extinguisher mounted on the wall. To the right of the window, at mid height, a small closed wall compartment with a latch. On the far right edge a heavy sliding automatic door, stuck slightly open, with sparks from a broken control panel. On the floor below the window, small and easy to overlook, a screwdriver with a star-shaped tip. Pulsing red-orange emergency lights. + Stil

**`Crew Cabin.jpeg`**: Crew-Quartier
> Crew quarters on a futuristic spaceship, front view of one wall. On the far left edge an open sliding door back to the corridor. Left of center a bunk bed with a crumpled paper note pinned to it, and below it a small shelf with a personal diary. Upper left center a framed photo on the wall; upper right center a round porthole showing the red ringed planet. In the exact center an open electrical wall panel with four numbered sockets (1 and 2 on top, 3 and 4 below) and four loose cables in red, yellow, green and blue. Right of center a small coffee machine on a counter. On the far right edge a heavy locked security bulkhead with a card reader glowing red. A knocked-over mug on the floor. Cool teal ambient light with warm amber accents. + Stil

**`Laboratory.jpeg`**: Labor mit Generator
> Research laboratory on a futuristic spaceship, front view. On the left several tall glowing glass tanks with colorful plant and rock samples from the planet floating in liquid. In the upper center a jagged crack in the wall, patched with glowing emergency foam. On the right a large bulky oxygen generator machine, damaged and smoking, its cover panel held by star-shaped special screws, warning lights blinking. On the floor in front, two ordinary wrenches. On the far left edge the open bulkhead door leading back. Haze in the air, teal and magenta light. + Stil

---

## Enden und Outro

**`Outro 1.jpeg`**: Eintritt in die Atmosphäre
> The orange-and-white spaceship entering the atmosphere of the red planet, glowing heat shield and bright trails, a pastel pink sky, the planetary ring arching overhead, red dunes and canyons far below. Triumphant mood. + Stil

**`Outro 2.jpeg`**: Gelandet
> View through a spaceship window onto the surface of the red planet after landing: rolling red dunes, giant crystalline rock arches, strange glowing flora, a pastel sky with the planetary ring and two moons. Hopeful, wondrous mood. + Stil

**`Outro saved.jpeg`**: Endbildschirm „Saved“
> The spaceship standing safely on the red planet at sunset, landing legs extended, warm light from its windows, crystalline rock arches and the planetary ring glowing in a magenta-and-orange sky. Peaceful, victorious mood. + Stil

**`Outro Out of oxygen.jpeg`**: Endbildschirm „Out of Air“
> The spaceship corridor in darkness, only a single red emergency light, frost creeping over the window, the red planet outside unreachable, a holographic warning display showing a flat oxygen line. Quiet, melancholic, game-over mood. + Stil

---

## Wenn ein Item noch im Bild zu sehen ist, obwohl man es schon genommen hat

Im Flur sieht man den Schraubenzieher am Boden auch dann noch, wenn er schon im Inventar ist. Nur seine Markierung verschwindet. Dafür gibt es zwei Lösungen:
- Er bleibt im Bild. Klickt man ihn noch einmal an, erscheint „This is where the screwdriver was.“ Das ist schon eingebaut.
- Du erzeugst zusätzlich eine Version des Flur-Bildes ohne Schraubenzieher. Dann kann das Spiel je nach Inventar das passende Bild zeigen. Das können wir später einbauen.

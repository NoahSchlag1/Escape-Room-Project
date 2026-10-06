# Escape Room „Raumschiff“ – Spieldesign

Hier steht, *was* im Spiel passiert. Wie die Entities zusammenhängen, steht in [ENTITIES.md](ENTITIES.md).

## Setting

- Du bist auf einem **Raumschiff** auf dem Weg zu einem fremden Planeten. Er sieht aus wie der Mars, aber dort leben seltsame Kreaturen.
- Ein Meteorit hat das Schiff gestreift und dabei den **Sauerstoffgenerator** beschädigt, zwei Räume vom Flur entfernt. Wenn er nicht repariert wird, geht die Luft aus.
- Timer: **10 Minuten**. Der Wert wird durch Testspielen angepasst.

## Ablauf

### Intro (2–3 Bild-Slides, weiter per Klick)
1. Der Zielplanet in Nahaufnahme (Makro): rote Oberfläche, seltsame Kreaturen.
2. –3. Überleitung auf das Schiff: „Du bist im Flur …“

### Raum 1: Flur
- **Start:** Durchs Fenster sieht man den **Zielplaneten**. Dann gehen das rote Alarmlicht und die Durchsage los: Ein Meteorit hat das Schiff gestreift, der Sauerstoffgenerator ist beschädigt. Ab jetzt läuft der Timer.
- **Objekte:**
  - **Fenster:** Blick auf den Zielplaneten, nur Atmosphäre
  - **Feuerlöscher:** Ablenkung ohne Nutzen
  - **Spezial-Schraubenzieher:** liegt unauffällig am Boden unter dem Fenster. Man übersieht ihn leicht, erst im Labor merkt man, dass er fehlt
  - **Wandfach:** darin liegt das **Logbuch**
  - **Spind** mit Zahlenschloss
  - **Defekte Automatiktür** zu Raum 2
- **Lösungsweg:**
  1. Das Wandfach öffnen und das Logbuch nehmen. Es wandert ins Inventar und lässt sich jederzeit aufklappen.
  2. Im aufgeklappten Logbuch steht das Baujahr des Schiffs: **1973**.
  3. Am Spind öffnet sich ein Zahlenschloss-Interface. Wer `1973` eingibt, bekommt die **Brechstange**.
  4. Mit der Brechstange die defekte Tür aufhebeln. Weiter geht es nach Raum 2.

### Raum 2: Crew-Quartier
- Schlafkojen, persönliche Gegenstände der Crew, Aufenthaltsbereich.
- **Objekte zum Ansehen:** Crew-Foto, Bullauge (der Zielplanet ist näher gekommen), persönliches Tagebuch (Eintrag über die Kreaturen), Kaffeemaschine (Ablenkung mit witzigem Text).
- **Rätsel „Stromkreis verbinden“:** 4 farbige Kabel (rot, blau, gelb, grün) müssen den richtigen 4 Buchsen zugeordnet werden. Die richtige Zuordnung steht auf einer **Notiz an einer Koje**. Ist alles richtig verbunden, springt ein Fach auf. Darin liegt die **Zugangskarte**.
- **Sicherheitsschott** zu Raum 3. Es ist verriegelt und braucht die Zugangskarte.

### Raum 3: Labor (mit Sauerstoffgenerator)
- Hier steht der **beschädigte Sauerstoffgenerator**.
- **Reparatur:** Man braucht den **Spezial-Schraubenzieher**. Er liegt im Flur (Raum 1).
  - Ohne Schraubenzieher erscheint beim Klick auf den Generator nur ein Hinweis, z. B.: „Diese Spezialschrauben bekommst du mit bloßen Händen nicht auf … Vielleicht hast du im Flur etwas übersehen?“
  - Mit Schraubenzieher ist der Generator repariert. Das führt zum Ende „Gerettet“.
- **Aussehen:** Proben vom Planeten in leuchtenden Glastanks, darin seltsame Kreaturen. Der Generator steht qualmend in der Ecke, in der Wand ein Riss, wo der Meteorit die Außenwand gestreift hat.

## Enden
- **Gerettet:** Der Sauerstoffgenerator ist rechtzeitig repariert. Das Schiff landet auf dem Planeten, danach kommen Outro-Bilder vom Planeten und seinen Kreaturen.
- **Luft aus:** Der Timer ist abgelaufen.
- Es gibt nur diese zwei Enden. „Gerettet“ hängt davon ab, ob der Player den Schraubenzieher gefunden hat. Das erfüllt die Vorgabe im BRD, dass ein Ende von einem Item abhängt.

## Benutzeroberfläche
- **Mini-Map unten rechts**, immer sichtbar: Alle Räume sind von Anfang an zu sehen. Der aktuelle Raum leuchtet, und der beschädigte Generator blinkt rot als Ziel.
- Timer und Inventar sind immer sichtbar.
- **Klickbare Objekte direkt im Szenenbild**, keine Buttons. Für jedes Objekt ist ein Bereich im Bild festgelegt. Ein Klick darauf zeigt einen Text, öffnet ein Rätsel, hebt ein Item auf oder führt durch eine Tür.

## Folgen für das Modell
| Spielelement | Entity |
|---|---|
| Logbuch, Brechstange, Zugangskarte, Schraubenzieher | **Item** |
| Wandfach | Ist kein eigenes Element. Hier liegt das Logbuch im Flur (Room enthält Item). „Wandfach öffnen“ = Logbuch aufheben |
| Spind mit Zahlenschloss | **Puzzle** im Flur: Lösung `1973`, Belohnung Brechstange |
| Stromkreis | **Puzzle** im Crew-Quartier, Belohnung Zugangskarte |
| Defekte Tür | **Blocker** auf dem Weg Flur → Crew-Quartier, braucht die Brechstange |
| Sicherheitsschott | **Blocker** auf dem Weg Crew-Quartier → Labor, braucht die Zugangskarte |
| Generator-Reparatur | **Blocker** auf dem Weg Labor → Ende „Gerettet“, braucht den Schraubenzieher. Der Hinweis ist der `locked_text` |
| Enden (Gerettet, Luft aus) | **Room** ohne Ausgänge. „Luft aus“ wird nicht über einen Weg erreicht, sondern wenn der Timer abläuft |
| Fenster, Feuerlöscher, Crew-Foto, Bullauge, Tagebuch, Kaffeemaschine | Objekte zum Ansehen, ohne Wirkung. *Noch offen, wie sie modelliert werden. Siehe „Klickbare Objekte“* |
| Mini-Map | Wird aus der **Map** (Wege) und `Player.current_room_id` gezeichnet. Jeder Room braucht dafür eine Position auf der Karte |

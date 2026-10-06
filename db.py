"""Lesen und Schreiben der CSV-Dateien in data/.

Die Spielwelt (Room, Item, Blocker, Puzzle, Map, Hotspot) wird nur gelesen.
Der Spielstand (Player) wird gelesen, geschrieben und beim Neustart gelöscht.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

SAVE_FIELDS = ["current_room_id", "inventory", "opened_blockers", "remaining_seconds", "status"]
LIST_SEPARATOR = ";"


def read_table(filename, data_dir=DATA_DIR):
    """Liest eine CSV-Datei und gibt eine Liste von Zeilen (dicts) zurück."""
    with open(data_dir / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_id(rows):
    """Macht aus einer Liste von Zeilen ein dict, damit man per id nachschlagen kann."""
    return {row["id"]: row for row in rows}


def load_world(data_dir=DATA_DIR):
    """Lädt die komplette Spielwelt. Sie ändert sich während des Spiels nie."""
    return {
        "rooms": by_id(read_table("rooms.csv", data_dir)),
        "items": by_id(read_table("items.csv", data_dir)),
        "blockers": by_id(read_table("blockers.csv", data_dir)),
        "puzzles": by_id(read_table("puzzles.csv", data_dir)),
        "exits": read_table("exits.csv", data_dir),        # die Map: eine Liste von Wegen
        "hotspots": read_table("hotspots.csv", data_dir),
    }


# ---------- Spielstand (Player) ----------

def save_player(player, data_dir=DATA_DIR):
    """Speichert den Player. Listen werden als 'a;b;c' in eine Zelle geschrieben."""
    row = {
        "current_room_id": player["current_room_id"],
        "inventory": LIST_SEPARATOR.join(player["inventory"]),
        "opened_blockers": LIST_SEPARATOR.join(player["opened_blockers"]),
        "remaining_seconds": player["remaining_seconds"],
        "status": player["status"],
    }
    with open(data_dir / "save.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SAVE_FIELDS)
        writer.writeheader()
        writer.writerow(row)


def load_player(data_dir=DATA_DIR):
    """Lädt den gespeicherten Player oder gibt None zurück, wenn es keinen Spielstand gibt."""
    path = data_dir / "save.csv"
    if not path.exists():
        return None
    rows = read_table("save.csv", data_dir)
    if not rows:
        return None
    row = rows[0]
    return {
        "current_room_id": row["current_room_id"],
        "inventory": split_list(row["inventory"]),
        "opened_blockers": split_list(row["opened_blockers"]),
        "remaining_seconds": int(row["remaining_seconds"]),
        "status": row["status"],
    }


def delete_save(data_dir=DATA_DIR):
    """Löscht den Spielstand, die Datei bleibt mit leerer Kopfzeile bestehen."""
    with open(data_dir / "save.csv", "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=SAVE_FIELDS).writeheader()


def split_list(text):
    """'a;b' -> ['a', 'b'] und '' -> []"""
    return [part for part in text.split(LIST_SEPARATOR) if part]

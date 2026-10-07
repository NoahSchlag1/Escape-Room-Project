"""Die Spielregeln.

Jede Aktion bekommt die Spielwelt (`world`) und den Player und gibt einen
*neuen* Player plus eine Nachricht zurück. Der alte Player wird nie verändert.
Wird eine Aktion abgelehnt, ist der neue Player identisch mit dem alten.

Player (dict):
    current_room_id    in welchem Room er steht
    inventory          Liste von Item-ids
    opened_blockers    Liste von Blocker-ids, die er schon geöffnet hat
    remaining_seconds  wie viel Sauerstoff noch übrig ist
    status             "playing", "won" oder "lost"
"""

import copy

START_ROOM_ID = "flur"
START_SECONDS = 10 * 60


def new_game():
    """Ein frischer Player am Spielanfang."""
    return {
        "current_room_id": START_ROOM_ID,
        "inventory": [],
        "opened_blockers": [],
        "remaining_seconds": START_SECONDS,
        "status": "playing",
    }


# ---------- Abfragen (ändern nichts) ----------

def items_in_room(world, player, room_id):
    """Items, die noch im Room liegen: Startort ist dieser Room und der Player trägt sie nicht."""
    return [
        item_id
        for item_id, item in world["items"].items()
        if item["start_room_id"] == room_id and item_id not in player["inventory"]
    ]


def exits_from(world, room_id):
    """Alle Wege der Map, die in diesem Room beginnen."""
    return [exit for exit in world["exits"] if exit["from_room_id"] == room_id]


def find_exit(world, from_room_id, to_room_id):
    for exit in exits_from(world, from_room_id):
        if exit["to_room_id"] == to_room_id:
            return exit
    return None


def is_puzzle_solved(world, player, puzzle_id):
    """Ein Puzzle ist gelöst, sobald der Player dessen Belohnung trägt."""
    return world["puzzles"][puzzle_id]["reward_item_id"] in player["inventory"]


def is_hotspot_changed(world, player, hotspot):
    """Hat sich das Objekt hinter diesem Hotspot verändert? (für die adaptiven Bilder)

    Item genommen, Rätsel gelöst oder Blocker auf dem Weg geöffnet.
    """
    if hotspot["item_id"]:
        return hotspot["item_id"] in player["inventory"]
    if hotspot["puzzle_id"]:
        return is_puzzle_solved(world, player, hotspot["puzzle_id"])
    if hotspot["to_room_id"]:
        exit = find_exit(world, hotspot["room_id"], hotspot["to_room_id"])
        return bool(exit and exit["blocker_id"] and exit["blocker_id"] in player["opened_blockers"])
    return False


def hotspots_in_room(world, room_id):
    return [h for h in world["hotspots"] if h["room_id"] == room_id]


def ending_room_id(world, ending):
    """Die id des Rooms mit diesem Ende ('won' oder 'lost')."""
    for room_id, room in world["rooms"].items():
        if room["ending"] == ending:
            return room_id
    raise ValueError(f"Kein Room mit ending={ending!r}")


def goal_room_id(world):
    """Der Room, von dem aus ein Weg zum Ende 'won' führt (für die Mini-Map)."""
    won_room_id = ending_room_id(world, "won")
    for exit in world["exits"]:
        if exit["to_room_id"] == won_room_id:
            return exit["from_room_id"]
    return None


def is_playing(player):
    return player["status"] == "playing"


GAME_OVER_TEXT = "The game is over. Start a new game."


# ---------- Aktionen ----------

def pick_up(world, player, item_id):
    """Item aus dem aktuellen Room ins Inventar nehmen."""
    if not is_playing(player):
        return player, GAME_OVER_TEXT
    item = world["items"][item_id]
    if item_id in player["inventory"]:
        return player, f"You already have the {item['name']}."
    if item_id not in items_in_room(world, player, player["current_room_id"]):
        return player, f"The {item['name']} isn't here."

    new_player = copy.deepcopy(player)
    new_player["inventory"].append(item_id)
    return new_player, f"You take the {item['name']}."


def move(world, player, to_room_id):
    """Über einen Weg der Map in einen anderen Room gehen und dabei den Blocker prüfen."""
    if not is_playing(player):
        return player, GAME_OVER_TEXT
    exit = find_exit(world, player["current_room_id"], to_room_id)
    if exit is None:
        return player, "There is no way there from here."

    new_player = copy.deepcopy(player)
    message = ""

    blocker_id = exit["blocker_id"]
    if blocker_id and blocker_id not in player["opened_blockers"]:
        blocker = world["blockers"][blocker_id]
        if blocker["required_item_id"] not in player["inventory"]:
            return player, blocker["locked_text"]          # A1: nichts ändert sich
        new_player["opened_blockers"].append(blocker_id)  # A2: Item bleibt im Inventar
        message = blocker["opened_text"] + "\n\n"

    new_player["current_room_id"] = to_room_id
    target = world["rooms"][to_room_id]
    if target["ending"] == "won":
        new_player["status"] = "won"
    return new_player, message + target["description"]


def solve_puzzle(world, player, puzzle_id, answer):
    """Eine Lösung für ein Puzzle im aktuellen Room ausprobieren."""
    if not is_playing(player):
        return player, GAME_OVER_TEXT
    puzzle = world["puzzles"][puzzle_id]
    if puzzle["room_id"] != player["current_room_id"]:
        return player, "That puzzle isn't here."
    if is_puzzle_solved(world, player, puzzle_id):
        return player, "You have already solved that."
    if normalize(answer) != normalize(puzzle["solution"]):
        return player, puzzle["wrong_text"]

    new_player = copy.deepcopy(player)
    new_player["inventory"].append(puzzle["reward_item_id"])
    return new_player, puzzle["solved_text"]


def normalize(answer):
    """'Red, Yellow ,green' und 'red,yellow,green' sollen gleich zählen."""
    text = str(answer).lower().replace(" ", "")
    return text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")


def tick(world, player, seconds):
    """Zeit vergeht. Ist der Sauerstoff aufgebraucht, ist das Spiel verloren."""
    if not is_playing(player):
        return player
    new_player = copy.deepcopy(player)
    new_player["remaining_seconds"] = max(0, player["remaining_seconds"] - seconds)
    if new_player["remaining_seconds"] == 0:
        new_player["status"] = "lost"
        new_player["current_room_id"] = ending_room_id(world, "lost")
    return new_player


# ---------- Hotspots: Klick im Bild -> passende Aktion ----------

def click_hotspot(world, player, hotspot_id):
    """Führt aus, worauf der Hotspot verweist.

    Gibt (player, message, puzzle_id) zurück. puzzle_id ist gesetzt, wenn die
    Oberfläche jetzt die Eingabe für ein Rätsel öffnen soll.
    """
    if not is_playing(player):
        return player, GAME_OVER_TEXT, None
    hotspot = next(h for h in world["hotspots"] if h["id"] == hotspot_id)
    if hotspot["room_id"] != player["current_room_id"]:
        return player, "That isn't here.", None

    if hotspot["item_id"]:
        if hotspot["item_id"] in player["inventory"]:
            return player, hotspot["done_text"], None
        new_player, message = pick_up(world, player, hotspot["item_id"])
        return new_player, f"{hotspot['text']}\n\n{message}", None

    if hotspot["puzzle_id"]:
        if is_puzzle_solved(world, player, hotspot["puzzle_id"]):
            return player, hotspot["done_text"], None
        return player, world["puzzles"][hotspot["puzzle_id"]]["prompt"], hotspot["puzzle_id"]

    if hotspot["to_room_id"]:
        new_player, message = move(world, player, hotspot["to_room_id"])
        return new_player, message, None

    return player, hotspot["text"], None

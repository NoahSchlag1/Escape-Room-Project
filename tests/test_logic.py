"""Tests für die Spielregeln, angelehnt an die Abnahmekriterien A1–A6 aus dem BRD."""

import shutil

import pytest

import db
import logic


@pytest.fixture
def world():
    return db.load_world()


@pytest.fixture
def data_dir(tmp_path):
    """Kopie von data/, damit Tests nie den echten Spielstand überschreiben."""
    shutil.copytree(db.DATA_DIR, tmp_path / "data")
    return tmp_path / "data"


def play(world, player, *steps):
    """Hilfsfunktion: führt mehrere Aktionen hintereinander aus."""
    for action, *args in steps:
        if action == "take":
            player, _ = logic.pick_up(world, player, *args)
        elif action == "go":
            player, _ = logic.move(world, player, *args)
        elif action == "solve":
            player, _ = logic.solve_puzzle(world, player, *args)
    return player


WINNING_PATH = [
    ("take", "logbuch"),
    ("take", "schraubenzieher"),
    ("solve", "spind", "2073"),
    ("go", "crew"),
    ("solve", "kabel", "red,yellow,green,blue"),
    ("go", "labor"),
    ("go", "ende_gerettet"),
]


# ---------- A1: gesperrter Weg ohne Item ----------

def test_a1_blocked_route_changes_nothing(world):
    player = logic.new_game()
    new_player, message = logic.move(world, player, "crew")
    assert new_player == player
    assert message == world["blockers"]["defekte_tuer"]["locked_text"]


# ---------- A2: Item öffnet Weg und bleibt im Inventar ----------

def test_a2_item_opens_route_and_is_kept(world):
    player = play(world, logic.new_game(), ("solve", "spind", "2073"))
    player, message = logic.move(world, player, "crew")
    assert player["current_room_id"] == "crew"
    assert "defekte_tuer" in player["opened_blockers"]
    assert "brechstange" in player["inventory"]
    assert world["blockers"]["defekte_tuer"]["opened_text"] in message


def test_opened_blocker_stays_open_both_ways(world):
    player = play(world, logic.new_game(), ("solve", "spind", "2073"), ("go", "crew"), ("go", "flur"))
    player, message = logic.move(world, player, "crew")
    assert player["current_room_id"] == "crew"
    assert world["blockers"]["defekte_tuer"]["opened_text"] not in message


# ---------- A3: Item nur einmal einsammeln ----------

def test_a3_item_collected_only_once(world):
    player, _ = logic.pick_up(world, logic.new_game(), "logbuch")
    again, _ = logic.pick_up(world, player, "logbuch")
    assert again["inventory"].count("logbuch") == 1
    assert "logbuch" not in logic.items_in_room(world, again, "flur")


def test_a3_puzzle_reward_only_once(world):
    player = play(world, logic.new_game(), ("solve", "spind", "2073"))
    again, message = logic.solve_puzzle(world, player, "spind", "2073")
    assert again["inventory"].count("brechstange") == 1
    assert message == "You have already solved that."


def test_cannot_take_item_from_other_room(world):
    player = logic.new_game()
    new_player, _ = logic.pick_up(world, player, "zugangskarte")
    assert new_player == player


# ---------- Rätsel ----------

def test_wrong_code_changes_nothing(world):
    player = logic.new_game()
    new_player, message = logic.solve_puzzle(world, player, "spind", "1234")
    assert new_player == player
    assert message == world["puzzles"]["spind"]["wrong_text"]


def test_cable_answer_is_normalized(world):
    player = play(world, logic.new_game(), ("solve", "spind", "2073"), ("go", "crew"))
    player, _ = logic.solve_puzzle(world, player, "kabel", "Red, Yellow, Green, Blue")
    assert "zugangskarte" in player["inventory"]


def test_generator_needs_screwdriver(world):
    steps = [s for s in WINNING_PATH if s != ("take", "schraubenzieher")][:-1]
    player = play(world, logic.new_game(), *steps)
    assert player["current_room_id"] == "labor"
    new_player, message = logic.move(world, player, "ende_gerettet")
    assert new_player == player
    assert "corridor" in message


# ---------- A4: Fortsetzen ----------

def test_a4_resume_restores_everything(world, data_dir):
    player = play(world, logic.new_game(), *WINNING_PATH[:4])
    player = logic.tick(world, player, 95)
    db.save_player(player, data_dir)
    assert db.load_player(data_dir) == player


def test_no_save_means_no_resume(data_dir):
    db.delete_save(data_dir)
    assert db.load_player(data_dir) is None


# ---------- A5: zwei Spiele, zwei Enden ----------

def test_a5_win(world):
    player = play(world, logic.new_game(), *WINNING_PATH)
    assert player["status"] == "won"
    assert player["current_room_id"] == "ende_gerettet"


def test_a5_lose_when_time_runs_out(world):
    player = logic.tick(world, logic.new_game(), logic.START_SECONDS)
    assert player["status"] == "lost"
    assert player["current_room_id"] == "ende_luft_aus"


def test_no_actions_after_ending(world):
    player = logic.tick(world, logic.new_game(), logic.START_SECONDS)
    new_player, message = logic.pick_up(world, player, "logbuch")
    assert new_player == player
    assert message == logic.GAME_OVER_TEXT


# ---------- A6: Neustart ----------

def test_a6_restart_resets_progress_but_keeps_world(world, data_dir):
    player = play(world, logic.new_game(), *WINNING_PATH[:4])
    db.save_player(player, data_dir)

    # Abbrechen: es passiert nichts, der Spielstand bleibt
    assert db.load_player(data_dir) == player

    # Bestätigen: Spielstand gelöscht, neuer Player, Spielwelt unverändert
    db.delete_save(data_dir)
    fresh = logic.new_game()
    assert db.load_player(data_dir) is None
    assert fresh["inventory"] == [] and fresh["current_room_id"] == "flur"
    assert db.load_world(data_dir) == world


# ---------- Hotspots ----------

def test_hotspot_opens_puzzle_then_shows_done_text(world):
    player = logic.new_game()
    _, _, puzzle_id = logic.click_hotspot(world, player, "spind")
    assert puzzle_id == "spind"
    player = play(world, player, ("solve", "spind", "2073"))
    _, message, puzzle_id = logic.click_hotspot(world, player, "spind")
    assert puzzle_id is None
    assert message == "The locker is open and empty."


def test_world_references_are_consistent(world):
    """Jede id, auf die verwiesen wird, muss es auch geben."""
    rooms, items = world["rooms"], world["items"]
    for item in items.values():
        assert item["start_room_id"] in rooms or item["start_room_id"] == ""
    for blocker in world["blockers"].values():
        assert blocker["required_item_id"] in items
    for puzzle in world["puzzles"].values():
        assert puzzle["room_id"] in rooms and puzzle["reward_item_id"] in items
    for exit in world["exits"]:
        assert exit["from_room_id"] in rooms and exit["to_room_id"] in rooms
        assert exit["blocker_id"] in world["blockers"] or exit["blocker_id"] == ""
    for h in world["hotspots"]:
        assert h["room_id"] in rooms
        if h["to_room_id"]:
            assert logic.find_exit(world, h["room_id"], h["to_room_id"]) is not None


def test_every_csv_row_has_all_columns():
    """Fängt Zeilen ab, die durch ein Komma ohne Anführungszeichen zerbrochen sind."""
    import csv
    for path in db.DATA_DIR.glob("*.csv"):
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert all(len(row) == len(rows[0]) for row in rows), path.name


def test_hotspot_changes_follow_player_state(world):
    """Grundlage der adaptiven Bilder: Was hat sich im Raum sichtbar verändert?"""
    spots = {h["id"]: h for h in world["hotspots"]}
    player = logic.new_game()
    assert not any(logic.is_hotspot_changed(world, player, h) for h in world["hotspots"])

    player = play(world, player, ("take", "logbuch"), ("solve", "spind", "2073"), ("go", "crew"))
    changed = {h["id"] for h in world["hotspots"] if logic.is_hotspot_changed(world, player, h)}
    assert changed == {"wandfach", "spind", "tuer_crew"}   # Schraubenzieher liegt noch da
    assert not logic.is_hotspot_changed(world, player, spots["fenster"])

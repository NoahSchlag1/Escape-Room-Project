"""Die Oberfläche (Einstiegspunkt). Starten mit: streamlit run app.py

Hier steht nur, *wie* etwas angezeigt wird. Was erlaubt ist, entscheidet logic.py.
"""

import html
import math
import random
import time
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates

import db
import logic

IMAGE_DIR = Path(__file__).parent / "images"
IMAGE_SIZE = (1600, 900)
FONT_FILES = ["Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]

INTRO_SLIDES = [
    ("Intro 1.jpeg", "Ein fremder Planet. Rot wie der Mars – doch auf seiner Oberfläche bewegt sich etwas."),
    ("Intro 2.jpeg", "Seit 212 Tagen ist dein Raumschiff unterwegs zu ihm. Nur noch wenige Stunden bis zur Landung."),
    ("Intro 3.jpeg", "Du gehst gerade durch den Flur, als ein dumpfer Schlag das ganze Schiff erschüttert …"),
]
OUTRO_SLIDES = [
    ("Outro 1.jpeg", "Der Generator läuft. Das Schiff tritt in die Atmosphäre des roten Planeten ein."),
    ("Outro 2.jpeg", "Sanfte Landung. Durch das Fenster siehst du rote Dünen – und neugierige Kreaturen mit sechs Beinen."),
]
ALARM_TEXT = (
    "🚨 **DURCHSAGE:** Meteoriteneinschlag im Labor! Der Sauerstoffgenerator ist beschädigt. "
    "Restluft: 10 Minuten. Die automatischen Türen sind ausgefallen."
)


# ---------- Zustand der Sitzung ----------

@st.cache_data
def get_world():
    return db.load_world()


def init_state():
    defaults = {
        "screen": "start",      # start | intro | game
        "slide": 0,             # aktuelle Intro- oder Outro-Folie
        "player": None,
        "deadline": None,       # Zeitpunkt (time.time()), an dem die Luft ausgeht
        "message": "",
        "last_click": None,     # unix_time des zuletzt verarbeiteten Klicks
        "open_dialog": None,    # ("puzzle", id) | ("item", id) | ("restart",)
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def start_new_game():
    db.delete_save()
    st.session_state.player = logic.new_game()
    st.session_state.screen = "intro"
    st.session_state.slide = 0
    st.session_state.message = ""


def resume_game():
    player = db.load_player()
    st.session_state.player = player
    st.session_state.deadline = time.time() + player["remaining_seconds"]
    st.session_state.screen = "game"
    st.session_state.slide = 0
    world = get_world()
    st.session_state.message = world["rooms"][player["current_room_id"]]["description"]


def begin_mission():
    """Nach dem Intro: Timer starten, Alarm auslösen."""
    player = st.session_state.player
    st.session_state.deadline = time.time() + player["remaining_seconds"]
    st.session_state.screen = "game"
    st.session_state.slide = 0
    st.session_state.message = ALARM_TEXT + "\n\n" + get_world()["rooms"]["flur"]["description"]
    db.save_player(player)


def sync_time():
    """Rechnet die vergangene Zeit in den Player ein und speichert ihn."""
    player = st.session_state.player
    if not logic.is_playing(player):
        return
    remaining_now = max(0, math.ceil(st.session_state.deadline - time.time()))
    player = logic.tick(get_world(), player, player["remaining_seconds"] - remaining_now)
    st.session_state.player = player
    db.save_player(player)


def apply(new_player, message):
    st.session_state.player = new_player
    st.session_state.message = message
    db.save_player(new_player)


# ---------- Bilder ----------

def font(size):
    """Eine Schrift mit Umlauten; die eingebaute Pillow-Schrift kann kein ä/ö/ü."""
    for name in FONT_FILES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def load_image(filename, title, hotspots=(), planet=False):
    """Lädt ein Bild aus images/. Fehlt es, wird ein Platzhalter gezeichnet."""
    path = IMAGE_DIR / filename
    if path.exists():
        image = Image.open(path).convert("RGB").resize(IMAGE_SIZE)
        if st.session_state.get("show_hotspots"):
            draw_hotspots(image, hotspots)
        return image

    image = Image.new("RGB", IMAGE_SIZE, (8, 12, 28))
    draw = ImageDraw.Draw(image)
    rng = random.Random(filename)
    for _ in range(250):
        x, y = rng.randrange(IMAGE_SIZE[0]), rng.randrange(IMAGE_SIZE[1])
        draw.point((x, y), fill=(200, 210, 255))
    if planet:
        draw.ellipse((900, 150, 1500, 750), fill=(170, 60, 35), outline=(230, 120, 80), width=6)
    draw.text((40, 30), title, fill=(220, 230, 255), font=font(48))
    draw.text((40, IMAGE_SIZE[1] - 50), f"Platzhalter – lege images/{filename} an", fill=(120, 130, 160),
              font=font(24))
    draw_hotspots(image, hotspots)
    return image


def draw_hotspots(image, hotspots):
    overlay = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    label_font = font(26)
    w, h = IMAGE_SIZE
    for spot in hotspots:
        box = (float(spot["x"]) / 100 * w, float(spot["y"]) / 100 * h,
               (float(spot["x"]) + float(spot["w"])) / 100 * w, (float(spot["y"]) + float(spot["h"])) / 100 * h)
        draw.rounded_rectangle(box, radius=12, fill=(90, 200, 255, 40), outline=(90, 200, 255, 200), width=3)
        draw.text((box[0] + 8, box[1] + 6), spot["label"], fill=(230, 245, 255, 255), font=label_font)
    image.paste(overlay, (0, 0), overlay)


def find_hotspot(hotspots, click):
    """Welcher Hotspot liegt unter dem Klick? Koordinaten in Prozent des angezeigten Bildes."""
    px = click["x"] / click["width"] * 100
    py = click["y"] / click["height"] * 100
    for spot in hotspots:
        x, y, w, h = (float(spot[k]) for k in ("x", "y", "w", "h"))
        if x <= px <= x + w and y <= py <= y + h:
            return spot
    return None


# ---------- Bausteine der Oberfläche ----------

def inject_css(alarm):
    alarm_css = """
        .stApp::after {
            content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 999;
            box-shadow: inset 0 0 160px rgba(255, 30, 30, 0.55);
            animation: alarm 1.6s ease-in-out infinite;
        }
        @keyframes alarm { 0%, 100% { opacity: 0.15; } 50% { opacity: 1; } }
    """ if alarm else ""
    st.markdown(f"""<style>
        .block-container {{ max-width: 1200px; padding-top: 2rem; }}
        .message {{
            background: rgba(10, 25, 45, 0.85); border: 1px solid #2c5d80; border-radius: 10px;
            padding: 1rem 1.2rem; color: #d6ecff; font-size: 1.05rem; line-height: 1.5;
        }}
        .timer {{ font-family: monospace; font-size: 2.2rem; text-align: right; color: #7fd3ff; }}
        .timer.low {{ color: #ff5050; animation: alarm 1s steps(2) infinite; }}
        .minimap {{
            position: fixed; right: 20px; bottom: 20px; z-index: 1000; pointer-events: none;
            background: rgba(5, 12, 25, 0.85); border: 1px solid #2c5d80; border-radius: 10px; padding: 8px;
        }}
        .minimap .goal {{ animation: goal 1s ease-in-out infinite; }}
        @keyframes goal {{ 0%, 100% {{ stroke: #ff3030; }} 50% {{ stroke: transparent; }} }}
        .logbook {{
            background: #f3e9d2; color: #3b2f1e; font-family: Georgia, serif; padding: 1.5rem;
            border-radius: 6px; box-shadow: inset 0 0 30px rgba(120, 90, 40, 0.35);
        }}
        {alarm_css}
    </style>""", unsafe_allow_html=True)


def show_message(text):
    if text:
        st.markdown(f'<div class="message">{markdown_to_html(text)}</div>', unsafe_allow_html=True)


def markdown_to_html(text):
    """Escaped Text mit **fett** und Zeilenumbrüchen."""
    parts = html.escape(text).split("**")
    text = "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))
    return text.replace("\n", "<br>")


@st.fragment(run_every=1)
def timer():
    """Läuft jede Sekunde neu, ohne die ganze Seite neu zu laden."""
    sync_time()
    player = st.session_state.player
    if not logic.is_playing(player):
        st.rerun()  # ganze Seite neu laden, damit das Ende angezeigt wird
    seconds = player["remaining_seconds"]
    css = "timer low" if seconds <= 60 else "timer"
    st.markdown(f'<div class="{css}">🫁 {seconds // 60:02d}:{seconds % 60:02d}</div>', unsafe_allow_html=True)


def minimap(world, player):
    """Mini-Map unten rechts: gezeichnet aus den Rooms (Position) und der Map (Wege)."""
    rooms = {rid: r for rid, r in world["rooms"].items() if r["map_x"] != ""}
    goal = logic.goal_room_id(world)
    box_w, box_h, gap = 90, 44, 40

    def pos(room):
        return 10 + int(room["map_x"]) * (box_w + gap), 10 + int(room["map_y"]) * (box_h + gap)

    parts = []
    drawn = set()
    for exit in world["exits"]:
        a, b = exit["from_room_id"], exit["to_room_id"]
        if a not in rooms or b not in rooms or frozenset((a, b)) in drawn:
            continue
        drawn.add(frozenset((a, b)))
        blockers = [e["blocker_id"] for e in world["exits"]
                    if {e["from_room_id"], e["to_room_id"]} == {a, b} and e["blocker_id"]]
        locked = any(bid not in player["opened_blockers"] for bid in blockers)
        (ax, ay), (bx, by) = pos(rooms[a]), pos(rooms[b])
        x1, y1, x2, y2 = ax + box_w, ay + box_h / 2, bx, by + box_h / 2
        dash = 'stroke-dasharray="4 4"' if locked else ""
        color = "#ff6060" if locked else "#5fb3e0"
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" {dash}/>')
        if locked:
            parts.append(f'<text x="{(x1 + x2) / 2}" y="{y1 - 8}" font-size="14" text-anchor="middle">🔒</text>')

    for rid, room in rooms.items():
        x, y = pos(room)
        here = rid == player["current_room_id"]
        fill = "#1f7fb8" if here else "#0d1d33"
        css = 'class="goal"' if rid == goal else ""
        stroke = "#ff3030" if rid == goal else "#5fb3e0"
        parts.append(f'<rect {css} x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="6" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x + box_w / 2}" y="{y + box_h / 2 + 5}" font-size="12" fill="#e0f2ff" '
                     f'text-anchor="middle" font-family="sans-serif">{html.escape(room["name"])}</text>')
        if here:
            parts.append(f'<circle cx="{x + box_w - 9}" cy="{y + 9}" r="5" fill="#7dffb0"/>')

    width = 20 + max(int(r["map_x"]) for r in rooms.values()) * (box_w + gap) + box_w
    height = 20 + max(int(r["map_y"]) for r in rooms.values()) * (box_h + gap) + box_h
    st.markdown(f'<div class="minimap"><svg width="{width}" height="{height}">{"".join(parts)}</svg></div>',
                unsafe_allow_html=True)


# ---------- Dialoge ----------

@st.dialog("Rätsel")
def puzzle_dialog(puzzle_id):
    world = get_world()
    puzzle = world["puzzles"][puzzle_id]
    st.subheader(puzzle["name"])
    st.write(puzzle["prompt"])

    if puzzle["kind"] == "code":
        cols = st.columns(4)
        digits = [c.selectbox(f"Ziffer {i + 1}", list("0123456789"), key=f"digit_{i}") for i, c in enumerate(cols)]
        answer = "".join(digits)
        label = "🔓 Öffnen"
    else:
        colors = ["–", "rot", "gelb", "grün", "blau"]
        cols = st.columns(4)
        chosen = [c.selectbox(f"Buchse {i + 1}", colors, key=f"cable_{i}") for i, c in enumerate(cols)]
        answer = ",".join(chosen)
        label = "⚡ Verbinden"

    if st.button(label, type="primary", width="stretch"):
        sync_time()
        player = st.session_state.player
        new_player, message = logic.solve_puzzle(world, player, puzzle_id, answer)
        if new_player == player:
            st.error(message)
        else:
            apply(new_player, message)
            st.rerun()


@st.dialog("Inventar")
def item_dialog(item_id):
    item = get_world()["items"][item_id]
    st.subheader(item["name"])
    if item_id == "logbuch":
        st.markdown(f'<div class="logbook">{html.escape(item["description"])}</div>', unsafe_allow_html=True)
    else:
        st.write(item["description"])


@st.dialog("Neues Spiel?")
def restart_dialog():
    st.write("Dein aktueller Fortschritt geht dabei verloren.")
    cancel, confirm = st.columns(2)
    if cancel.button("Abbrechen", width="stretch"):
        st.rerun()
    if confirm.button("Neu starten", type="primary", width="stretch"):
        start_new_game()
        st.rerun()


def open_pending_dialog():
    pending = st.session_state.open_dialog
    st.session_state.open_dialog = None
    if pending is None:
        return
    kind, *args = pending
    if kind == "puzzle":
        puzzle_dialog(*args)
    elif kind == "item":
        item_dialog(*args)
    elif kind == "restart":
        restart_dialog()


# ---------- Bildschirme ----------

def start_screen():
    inject_css(alarm=False)
    st.title("🚀 Sauerstoff-Alarm")
    st.write("Ein Escape Room an Bord eines Raumschiffs. Du hast 10 Minuten.")
    saved = db.load_player()
    left, right = st.columns(2)
    if left.button("Neues Spiel", type="primary", width="stretch"):
        if saved:
            st.session_state.open_dialog = ("restart",)  # A6: erst nachfragen
        else:
            start_new_game()
        st.rerun()
    if saved and right.button("Fortsetzen", width="stretch"):
        resume_game()
        st.rerun()


def slides_screen(slides, on_finish, finish_label):
    inject_css(alarm=False)
    index = st.session_state.slide
    filename, text = slides[index]
    st.image(load_image(filename, f"Folie {index + 1}", planet=True), width="stretch")
    show_message(text)
    st.write("")
    if index < len(slides) - 1:
        if st.button("Weiter ▶", type="primary"):
            st.session_state.slide += 1
            st.rerun()
    elif st.button(finish_label, type="primary"):
        on_finish()
        st.rerun()


def ending_screen(world, player):
    room = world["rooms"][player["current_room_id"]]
    inject_css(alarm=False)
    st.title("✅ Gerettet!" if player["status"] == "won" else "💀 Luft aus")
    st.image(load_image(room["image"], room["name"], planet=player["status"] == "won"), width="stretch")
    show_message(room["description"])
    st.write("")
    if st.button("Neues Spiel", type="primary"):
        start_new_game()
        st.rerun()


def game_screen(world):
    player = st.session_state.player
    room = world["rooms"][player["current_room_id"]]
    hotspots = logic.hotspots_in_room(world, room["id"])
    inject_css(alarm=True)

    with st.sidebar:
        st.header("🎒 Inventar")
        if not player["inventory"]:
            st.caption("Noch leer.")
        for item_id in player["inventory"]:
            if st.button(world["items"][item_id]["name"], key=f"inv_{item_id}", width="stretch"):
                st.session_state.open_dialog = ("item", item_id)
        st.divider()
        st.checkbox("Klickbereiche anzeigen", key="show_hotspots")
        if st.button("🔄 Neues Spiel", width="stretch"):
            st.session_state.open_dialog = ("restart",)

    title, clock = st.columns([3, 1])
    title.title(room["name"])
    with clock:
        timer()

    image = load_image(room["image"], room["name"], hotspots)
    click = streamlit_image_coordinates(image, key=f"scene_{room['id']}", use_column_width="always", cursor="pointer")
    # Nur neue Klicks verarbeiten: Die Komponente liefert den letzten Klick bei jedem Neuladen erneut.
    if click and click["unix_time"] > (st.session_state.last_click or 0):
        st.session_state.last_click = click["unix_time"]
        spot = find_hotspot(hotspots, click)
        sync_time()
        if spot is None:
            st.session_state.message = "Da ist nichts Besonderes."
        else:
            new_player, message, puzzle_id = logic.click_hotspot(world, st.session_state.player, spot["id"])
            apply(new_player, message)
            if puzzle_id:
                st.session_state.open_dialog = ("puzzle", puzzle_id)
        st.rerun()

    show_message(st.session_state.message)
    minimap(world, player)


def main():
    st.set_page_config(page_title="Sauerstoff-Alarm", page_icon="🚀", layout="wide")
    init_state()
    world = get_world()
    screen = st.session_state.screen

    if screen == "start":
        start_screen()
    elif screen == "intro":
        slides_screen(INTRO_SLIDES, begin_mission, "🚨 Mission starten")
    else:
        player = st.session_state.player
        if player["status"] == "won" and st.session_state.slide < len(OUTRO_SLIDES):
            def finish_outro():
                st.session_state.slide = len(OUTRO_SLIDES)
            slides_screen(OUTRO_SLIDES, finish_outro, "Weiter ▶")
        elif player["status"] in ("won", "lost"):
            ending_screen(world, player)
        else:
            game_screen(world)

    open_pending_dialog()


main()

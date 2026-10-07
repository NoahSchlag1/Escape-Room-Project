"""Die Oberfläche (Einstiegspunkt). Starten mit: streamlit run app.py

Hier steht nur, *wie* etwas angezeigt wird. Was erlaubt ist, entscheidet logic.py.
Alle Texte, die der Spieler sieht, sind auf Englisch.
"""

import html
import json
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
IMAGE_SIZE = (1376, 768)  # Größe der Szenenbilder, auch für Platzhalter
FONT_FILES = ["Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]

INTRO_SLIDES = [
    ("Intro 1.jpeg", "An alien planet. Red like Mars – and your destination."),
    ("Intro 2.jpeg", "Your ship has been travelling towards it for 212 days. Only a few hours left until landing."),
    ("Intro 3.jpeg", "You are walking down the corridor when a screeching scrape shakes the whole ship …"),
]
OUTRO_SLIDES = [
    ("Outro 1.jpeg", "The generator is running. The ship enters the atmosphere of the red planet."),
    ("Outro 2.jpeg", "A soft landing. Through the window you see red dunes stretching to the horizon."),
]
ALARM_TEXT = (
    "🚨 **ANNOUNCEMENT:** A meteorite has scraped the ship! The hull near the lab is torn open "
    "and the oxygen generator is damaged. Air remaining: 10 minutes. The automatic doors have failed."
)
ITEM_ICONS = {"logbuch": "📖", "schraubenzieher": "🪛", "brechstange": "🛠️", "zugangskarte": "💳"}


# ---------- Zustand der Sitzung ----------

def get_world():
    """Spielwelt aus dem Cache – wird neu geladen, sobald eine CSV-Datei geändert wurde."""
    return load_world_cached(tuple(path.stat().st_mtime for path in sorted(db.DATA_DIR.glob("*.csv"))))


@st.cache_data
def load_world_cached(csv_mtimes):  # Änderungszeiten sind Teil des Cache-Schlüssels
    return db.load_world()


def init_state():
    defaults = {
        "screen": "start",      # start | intro | game
        "slide": 0,             # aktuelle Intro- oder Outro-Folie
        "player": None,
        "deadline": None,       # Zeitpunkt (time.time()), an dem die Luft ausgeht
        "message": "",
        "last_click": None,     # unix_time des zuletzt verarbeiteten Klicks
        "open_dialog": None,    # ("puzzle", id) | ("read", id) | ("inventory",) | ("restart",) | ("cable_note",)
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
    if player is None:  # Spielstand wurde inzwischen gelöscht
        st.session_state.screen = "start"
        return
    st.session_state.player = player
    st.session_state.deadline = time.time() + player["remaining_seconds"]
    st.session_state.screen = "game"
    st.session_state.slide = 0
    st.session_state.message = get_world()["rooms"][player["current_room_id"]]["description"]


def begin_mission():
    """Nach dem Intro: Timer starten, Alarm auslösen."""
    player = st.session_state.player
    st.session_state.deadline = time.time() + player["remaining_seconds"]
    st.session_state.screen = "game"
    st.session_state.slide = 0
    st.session_state.message = ALARM_TEXT
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


def load_image(filename, title):
    """Lädt ein Bild aus images/. Fehlt es, wird ein Platzhalter gezeichnet."""
    path = IMAGE_DIR / filename
    if path.exists():
        return Image.open(path).convert("RGB")

    image = Image.new("RGB", IMAGE_SIZE, (8, 12, 28))
    draw = ImageDraw.Draw(image)
    rng = random.Random(filename)
    for _ in range(250):
        draw.point((rng.randrange(IMAGE_SIZE[0]), rng.randrange(IMAGE_SIZE[1])), fill=(200, 210, 255))
    draw.text((40, 30), title, fill=(220, 230, 255), font=font(48))
    draw.text((40, IMAGE_SIZE[1] - 50), f"Placeholder – add images/{filename}", fill=(120, 130, 160), font=font(24))
    return image


@st.cache_data(show_spinner=False)
def scene_image(filename, title, markers, image_mtime=0):
    """Szenenbild mit einem leuchtenden Kreis auf jedem klickbaren Objekt.

    markers: Tupel aus (x, y, w, h) in Prozent – nur Hotspots, die noch etwas tun.
    """
    image = load_image(filename, title)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = image.size
    r = width / 90  # Kreisgröße passt sich der Bildbreite an
    for x, y, w, h in markers:
        cx, cy = (x + w / 2) / 100 * width, (y + h / 2) / 100 * height
        draw.ellipse((cx - r * 1.7, cy - r * 1.7, cx + r * 1.7, cy + r * 1.7), fill=(63, 182, 255, 45))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(6, 18, 32, 150), outline=(150, 225, 255, 240),
                     width=max(2, int(r / 5)))
        draw.ellipse((cx - r / 3, cy - r / 3, cx + r / 3, cy + r / 3), fill=(200, 242, 255, 255))
    image.paste(overlay, (0, 0), overlay)
    return image


def visible_markers(world, player, hotspots):
    """Kreise nur dort, wo noch etwas passiert: genommene Items und gelöste Rätsel verschwinden."""
    markers = []
    for spot in hotspots:
        if spot["item_id"] and spot["item_id"] in player["inventory"]:
            continue
        if spot["puzzle_id"] and logic.is_puzzle_solved(world, player, spot["puzzle_id"]):
            continue
        markers.append(tuple(float(spot[k]) for k in ("x", "y", "w", "h")))
    return tuple(markers)


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

def inject_css(alarm=False):
    aspect = IMAGE_SIZE[0] / IMAGE_SIZE[1]
    alarm_css = """
        .stApp::after {
            content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 999;
            box-shadow: inset 0 0 160px rgba(255, 30, 30, 0.55);
            animation: pulse 1.6s ease-in-out infinite;
        }
    """ if alarm else ""
    st.markdown(f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Caveat:wght@500&display=swap');

        /* Vollbild: keine Kopfzeile, keine Seitenleiste, kein Rand */
        header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background: #000; }}
        [data-testid="stMainBlockContainer"] {{
            padding: 0 !important; margin: 0 auto;
            max-width: min(100vw, calc(100vh * {aspect:.4f})) !important;
        }}
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: 0; }}
        iframe {{ display: block; }}

        h1, h2, h3, .stButton button {{ font-family: 'Orbitron', sans-serif !important; letter-spacing: .04em; }}

        /* Anzeige oben rechts: Timer, Inventar, Neustart */
        .st-key-hud {{
            position: fixed; top: 14px; right: 14px; z-index: 1001; width: auto !important;
            background: rgba(4, 10, 20, .8); border: 1px solid #24506f; border-radius: 12px;
            padding: 6px 10px; backdrop-filter: blur(4px); align-items: center; flex-wrap: nowrap;
        }}
        .st-key-hud button {{ white-space: nowrap; }}
        .timer {{ font-family: 'Orbitron', monospace; font-size: 1.6rem; color: #7fd3ff; padding: 0 8px; }}
        .timer.low {{ color: #ff5050; animation: pulse 1s steps(2) infinite; }}

        .room-title {{
            position: fixed; top: 14px; left: 18px; z-index: 1000; pointer-events: none;
            font-family: 'Orbitron', sans-serif; font-size: 1.3rem; color: #d6ecff;
            background: rgba(4, 10, 20, .75); border: 1px solid #24506f; border-radius: 10px; padding: 6px 14px;
        }}
        .message {{
            position: fixed; left: 18px; bottom: 18px; z-index: 1000; pointer-events: none;
            max-width: min(46vw, 620px, calc(100vw - 480px)); min-width: 260px; background: rgba(4, 12, 24, .85); border: 1px solid #2c5d80;
            border-radius: 10px; padding: .9rem 1.1rem; color: #d6ecff; font-size: 1.02rem; line-height: 1.45;
        }}

        /* Textfeld mit Button unten mittig (Start, Intro, Outro, Ende) */
        .st-key-caption {{
            position: fixed; left: 50%; transform: translateX(-50%); bottom: 28px; z-index: 1001;
            width: min(760px, 92vw) !important; background: rgba(4, 10, 20, .85); border: 1px solid #24506f;
            border-radius: 14px; padding: 18px 22px; gap: .8rem !important;
        }}

        .minimap {{
            position: fixed; right: 18px; bottom: 18px; z-index: 1000; pointer-events: none;
            background: rgba(4, 10, 20, .85); border: 1px solid #24506f; border-radius: 10px; padding: 8px;
        }}
        .minimap .goal {{ animation: goal 1s ease-in-out infinite; }}

        /* Pop-ups im Spieldesign */
        [role="dialog"] {{  /* Streamlit rendert Pop-ups als <section role="dialog"> */
            background: linear-gradient(160deg, #0c1a2c, #060d18) !important; color: #d6ecff;
            border: 1px solid #2c7fb8; box-shadow: 0 0 40px rgba(63, 182, 255, .25);
        }}
        .slot {{
            border: 1px solid #2c7fb8; border-radius: 12px; background: rgba(20, 45, 70, .55);
            padding: 14px 10px; min-height: 190px; text-align: center; margin-bottom: 8px;
        }}
        .slot.empty {{ border-style: dashed; background: rgba(10, 20, 35, .4); color: #4f7390; }}
        .slot .icon {{ font-size: 2.6rem; line-height: 1.4; }}
        .slot .name {{ font-family: 'Orbitron', sans-serif; font-size: .9rem; margin: 4px 0 6px; }}
        .slot .desc {{ font-size: .85rem; color: #9cc4e0; }}
        .logbook {{
            background: radial-gradient(circle at 30% 20%, #f2e6c9, #dcc89c); color: #2d2216;
            font-family: 'Caveat', cursive; font-size: 1.5rem; line-height: 1.3;
            padding: 22px 32px; border-radius: 6px; box-shadow: inset 0 0 40px rgba(120, 90, 40, .45);
        }}

        /* Rätsel: Metallplatte mit leeren Eingabefeldern statt Auswahlmenüs */
        .puzzle-prompt {{ font-size: 1.05rem; color: #cfe6f7; margin-bottom: 16px; }}
        .st-key-lockpad, .st-key-cablepanel {{
            background: linear-gradient(145deg, #3a4652, #1b232c); border: 2px solid #56636f; border-radius: 16px;
            padding: 22px 26px; box-shadow: inset 0 2px 0 rgba(255, 255, 255, .08), 0 10px 30px rgba(0, 0, 0, .6);
        }}
        .st-key-lockpad [data-testid="stTextInputRootElement"], .st-key-lockpad [data-baseweb="input"] {{
            height: 84px;
            background: #041018; border: 2px solid #2c7fb8; border-radius: 10px;
            box-shadow: inset 0 0 14px rgba(0, 0, 0, .8);
        }}
        .st-key-lockpad input {{
            text-align: center; font-family: 'Orbitron', monospace !important; color: #7dffb0 !important;
            background: transparent !important; caret-color: #7dffb0;
        }}
        .st-key-lockpad input {{ font-size: 2.6rem !important; height: 100% !important; padding: 0 !important; }}
        [data-testid="InputInstructions"] {{ display: none; }}
        .panel-head {{
            font-family: 'Orbitron', sans-serif; font-size: .8rem; letter-spacing: .18em; color: #aebdcb;
            display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
        }}
        .led {{ width: 12px; height: 12px; border-radius: 50%; background: #ff3b3b; box-shadow: 0 0 10px #ff3b3b; }}
        .st-key-cablepanel [data-testid="stWidgetLabel"] p {{
            font-family: 'Orbitron', sans-serif; font-size: .75rem; letter-spacing: .12em; color: #aebdcb;
        }}
        .denied {{ color: #ff6b6b; font-family: 'Orbitron', sans-serif; font-size: .9rem; margin-top: 14px; }}

        .logbook p {{ margin: 0 0 .6em; }}
        .logbook p:last-child {{ margin-bottom: 0; }}

        /* Nebenbuttons und Kabel-Knöpfe im Spieldesign statt schwarz */
        [data-testid="stBaseButton-secondary"], [data-testid="stButtonGroup"] button {{
            background: #0f2033 !important; border: 1px solid #2c7fb8 !important; color: #d6ecff !important;
        }}
        [data-testid="stBaseButton-secondary"]:hover, [data-testid="stButtonGroup"] button:hover {{
            border-color: #7fd3ff !important; color: #fff !important;
        }}

        @keyframes pulse {{ 0%, 100% {{ opacity: .15; }} 50% {{ opacity: 1; }} }}
        @keyframes goal {{ 0%, 100% {{ stroke: #ff3030; }} 50% {{ stroke: transparent; }} }}
        {alarm_css}
    </style>""", unsafe_allow_html=True)


def markdown_to_html(text):
    """Escaped Text mit **fett** und Zeilenumbrüchen."""
    parts = html.escape(text).split("**")
    text = "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))
    return text.replace("\n", "<br>")


def show_message(text):
    if text:
        st.markdown(f'<div class="message">{markdown_to_html(text)}</div>', unsafe_allow_html=True)


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
    box_w, box_h, gap = 100, 44, 36

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


def read_aloud_button(text):
    """Kleiner Button, der den Text mit der Sprachausgabe des Browsers vorliest."""
    st.iframe(f"""
        <style>body {{ margin: 0; padding: 2px; }}</style>
        <button id="speak" style="font-family: sans-serif; font-size: 15px; color: #d6ecff; cursor: pointer;
            background: #0f2033; border: 1px solid #2c7fb8; border-radius: 8px; padding: 8px 16px;">
            🔊 Read aloud</button>
        <script>
            const text = {json.dumps(text)};
            document.getElementById("speak").onclick = () => {{
                speechSynthesis.cancel();
                const voice = new SpeechSynthesisUtterance(text);
                voice.lang = "en-GB"; voice.rate = 0.95;
                speechSynthesis.speak(voice);
            }};
        </script>""", height=52)  # eigener Text aus items.csv, kein Fremdinhalt


# ---------- Pop-ups ----------

@st.dialog("Puzzle", width="large")
def puzzle_dialog(puzzle_id):
    world = get_world()
    puzzle = world["puzzles"][puzzle_id]
    st.subheader(puzzle["name"])
    st.markdown(f'<div class="puzzle-prompt">{html.escape(puzzle["prompt"])}</div>', unsafe_allow_html=True)

    if puzzle["kind"] == "code":
        answer = code_lock(puzzle_id)
    else:
        answer = cable_panel(puzzle_id)

    if answer is not None:  # der Spieler hat abgeschickt
        sync_time()
        player = st.session_state.player
        new_player, message = logic.solve_puzzle(world, player, puzzle_id, answer)
        if new_player == player:
            st.markdown(f'<div class="denied">✖ {html.escape(message)}</div>', unsafe_allow_html=True)
        else:
            apply(new_player, message)
            st.rerun()


def code_lock(puzzle_id):
    """Zahlenschloss: vier leere Ziffernfelder auf einer Metallplatte.

    Ein Formular schickt erst beim Klick auf UNLOCK (oder Enter) ab.
    Gibt den Code zurück oder None, solange nicht abgeschickt wurde.
    """
    with st.container(key="lockpad"):
        st.markdown('<div class="panel-head"><span class="led"></span>SECURITY LOCK · ENTER 4-DIGIT CODE</div>',
                    unsafe_allow_html=True)
        with st.form(key=f"form_{puzzle_id}", border=False):
            digits = [col.text_input(f"Digit {i + 1}", max_chars=1, key=f"{puzzle_id}_digit_{i}",
                                     label_visibility="collapsed")
                      for i, col in enumerate(st.columns(4))]
            submitted = st.form_submit_button("🔓 UNLOCK", type="primary", width="stretch")
    return "".join(d.strip() for d in digits) if submitted else None


CABLE_COLORS = {"red": "#e0393e", "yellow": "#f2c230", "green": "#3bb54a", "blue": "#2f7fe0"}
CABLE_EMOJIS = {"red": "🔴", "yellow": "🟡", "green": "🟢", "blue": "🔵"}


def sockets_svg(plugged, paper):
    """Die vier Anschlüsse im 2×2-Raster wie auf dem Wandpanel im Bild (1 2 / 3 4).

    plugged: Liste mit 4 Farben (oder None), je eine pro Anschluss.
    paper:   True = handgezeichnet auf der Notiz, False = Metallpanel im Rätsel.
    """
    ink = "#3b2f1e" if paper else "#aebdcb"
    font_family = "Caveat, cursive" if paper else "Orbitron, sans-serif"
    sockets = [(130, 80), (290, 80), (130, 190), (290, 190)]
    starts = [30, 390, 170, 250]  # wo die Kabel unten herkommen: obere Reihe außen herum, untere innen
    parts = []
    for i, ((sx, sy), color) in enumerate(zip(sockets, plugged)):
        parts.append(f'<text x="{sx - 50}" y="{sy - 26}" font-size="{26 if paper else 15}" fill="{ink}" '
                     f'font-family="{font_family}">{i + 1}</text>')
        if paper:
            parts.append(f'<rect x="{sx - 32}" y="{sy - 32}" width="64" height="64" rx="8" fill="none" '
                         f'stroke="{ink}" stroke-width="2.5" stroke-dasharray="7 3"/>')
        else:
            parts.append(f'<rect x="{sx - 32}" y="{sy - 32}" width="64" height="64" rx="10" fill="#141b22" '
                         f'stroke="#56636f" stroke-width="2"/>')
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="14" fill="#000" stroke="#2b3540" stroke-width="3"/>')
        if color:
            hex_color = CABLE_COLORS[color]
            x0 = starts[i]
            path = f"M {x0} 270 C {x0} {sy + 40}, {sx} {sy + 40}, {sx} {sy + 18}"
            if not paper:  # dunkler Rand, damit das Kabel auf dem Metall plastisch wirkt
                parts.append(f'<path d="{path}" stroke="#000" stroke-width="13" fill="none" stroke-linecap="round"/>')
            parts.append(f'<path d="{path}" stroke="{hex_color}" stroke-width="{7 if paper else 9}" fill="none" '
                         f'stroke-linecap="round"/>')
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="15" fill="{hex_color}" stroke="{ink if paper else "#000"}" '
                         f'stroke-width="2"/>')
    return f'<svg viewBox="0 0 420 270" width="100%" style="max-width:400px; display:block; margin:0 auto">' \
           f'{"".join(parts)}</svg>'


def cable_panel(puzzle_id):
    """Schaltpanel: dieselben vier Anschlüsse wie auf der Notiz. Pro Anschluss wählt man eine Kabelfarbe."""
    keys = [f"{puzzle_id}_socket_{i}" for i in range(4)]
    with st.container(key="cablepanel"):
        st.markdown('<div class="panel-head"><span class="led"></span>POWER CIRCUIT · PLUG A CABLE INTO EACH SOCKET'
                    '</div>', unsafe_allow_html=True)
        drawing, choices = st.columns([1, 1], vertical_alignment="center")
        with choices:
            for i, key in enumerate(keys):
                st.pills(f"SOCKET {i + 1}", list(CABLE_COLORS), key=key, format_func=lambda c: f"{CABLE_EMOJIS[c]} {c}")
        plugged = [st.session_state.get(k) for k in keys]
        drawing.markdown(sockets_svg(plugged, paper=False), unsafe_allow_html=True)  # nach der Auswahl zeichnen
        submitted = st.button("⚡ CONNECT", type="primary", width="stretch")
    return ",".join(c or "" for c in plugged) if submitted else None


@st.dialog("Note", width="large")
def cable_note_dialog():
    """Die Notiz am Bett: zeigt, welches Kabel in welchen Anschluss gehört (aus der Lösung des Rätsels)."""
    world = get_world()
    room_id = st.session_state.player["current_room_id"]
    puzzle = next(p for p in world["puzzles"].values() if p["kind"] == "cables" and p["room_id"] == room_id)
    plugged = puzzle["solution"].split(",")
    st.markdown(f'<div class="logbook"><div style="text-align:center">Power panel – plug them in like this. '
                f'Don\'t mix them up again!</div>{sockets_svg(plugged, paper=True)}</div>', unsafe_allow_html=True)


@st.dialog("Inventory", width="large")
def inventory_dialog():
    """Ein Platz pro Item im Spiel. Leer, solange das Item noch nicht gefunden wurde."""
    world, player = get_world(), st.session_state.player
    items = list(world["items"].items())
    for col, (item_id, item) in zip(st.columns(len(items)), items):
        with col:
            if item_id not in player["inventory"]:
                st.markdown('<div class="slot empty"><div class="icon">?</div>'
                            '<div class="name">Not found yet</div></div>', unsafe_allow_html=True)
                continue
            st.markdown(f'<div class="slot"><div class="icon">{ITEM_ICONS.get(item_id, "📦")}</div>'
                        f'<div class="name">{html.escape(item["name"])}</div>'
                        f'<div class="desc">{html.escape(item["description"])}</div></div>', unsafe_allow_html=True)
            if item["read_text"] and st.button("📖 Read", key=f"read_{item_id}", width="stretch"):
                st.session_state.open_dialog = ("read", item_id)
                st.rerun()


@st.dialog("Reading", width="large")
def read_dialog(item_id):
    item = get_world()["items"][item_id]
    st.subheader(f"{ITEM_ICONS.get(item_id, '')} {item['name']}")
    paragraphs = "".join(f"<p>{html.escape(part).replace(chr(10), '<br>')}</p>"
                         for part in item["read_text"].split("\n\n"))
    st.markdown(f'<div class="logbook">{paragraphs}</div>', unsafe_allow_html=True)
    st.write("")
    read_aloud_button(item["read_text"])


@st.dialog("New game?")
def restart_dialog():
    st.write("Your current progress will be lost.")
    cancel, confirm = st.columns(2)
    if cancel.button("Cancel", width="stretch"):
        st.rerun()
    if confirm.button("Start over", type="primary", width="stretch"):
        start_new_game()
        st.rerun()


def open_pending_dialog():
    pending = st.session_state.open_dialog
    st.session_state.open_dialog = None
    if pending is None:
        return
    kind, *args = pending
    dialogs = {"puzzle": puzzle_dialog, "read": read_dialog, "inventory": inventory_dialog, "restart": restart_dialog,
               "cable_note": cable_note_dialog}
    dialogs[kind](*args)


# ---------- Bildschirme ----------

def start_screen():
    inject_css()
    st.image(load_image("Intro 1.jpeg", "Oxygen Alert"), width="stretch")
    saved = db.load_player()
    with st.container(key="caption"):
        st.title("OXYGEN ALERT")
        st.write("An escape room aboard a spaceship. Repair the oxygen generator before the air runs out.")
        left, right = st.columns(2)
        if left.button("New game", type="primary", width="stretch"):
            if saved:
                st.session_state.open_dialog = ("restart",)  # A6: erst nachfragen
            else:
                start_new_game()
            st.rerun()
        if saved and right.button("Continue", width="stretch"):
            resume_game()
            st.rerun()


def slides_screen(slides, on_finish, finish_label):
    inject_css()
    index = st.session_state.slide
    filename, text = slides[index]
    st.image(load_image(filename, f"Slide {index + 1}"), width="stretch")
    with st.container(key="caption"):
        st.markdown(f"<div style='font-size: 1.15rem'>{html.escape(text)}</div>", unsafe_allow_html=True)
        if index < len(slides) - 1:
            if st.button("Next ▶", type="primary"):
                st.session_state.slide += 1
                st.rerun()
        elif st.button(finish_label, type="primary"):
            on_finish()
            st.rerun()


def ending_screen(world, player):
    room = world["rooms"][player["current_room_id"]]
    inject_css()
    st.image(load_image(room["image"], room["name"]), width="stretch")
    with st.container(key="caption"):
        st.title("✅ Saved!" if player["status"] == "won" else "💀 Out of Air")
        st.write(room["description"])
        if st.button("New game", type="primary"):
            start_new_game()
            st.rerun()


def game_screen(world):
    player = st.session_state.player
    room = world["rooms"][player["current_room_id"]]
    hotspots = logic.hotspots_in_room(world, room["id"])
    inject_css(alarm=True)

    with st.container(key="hud", horizontal=True, wrap=False):
        timer()
        if st.button("🎒 Inventory", key="inventory_button"):
            st.session_state.open_dialog = ("inventory",)
        if st.button("⟲", key="restart_button", help="New game"):
            st.session_state.open_dialog = ("restart",)
    st.markdown(f'<div class="room-title">{html.escape(room["name"])}</div>', unsafe_allow_html=True)

    path = IMAGE_DIR / room["image"]
    mtime = path.stat().st_mtime if path.exists() else 0
    image = scene_image(room["image"], room["name"], visible_markers(world, player, hotspots), mtime)
    click = streamlit_image_coordinates(image, key=f"scene_{room['id']}", use_column_width="always",
                                        cursor="pointer", image_format="JPEG", jpeg_quality=90)
    # Nur neue Klicks verarbeiten: Die Komponente liefert den letzten Klick bei jedem Neuladen erneut.
    if click and click["unix_time"] > (st.session_state.last_click or 0):
        st.session_state.last_click = click["unix_time"]
        spot = find_hotspot(hotspots, click)
        sync_time()
        if spot is None:
            st.session_state.message = "Nothing special there."
        else:
            before = st.session_state.player
            new_player, message, puzzle_id = logic.click_hotspot(world, before, spot["id"])
            apply(new_player, message)
            new_items = [i for i in new_player["inventory"] if i not in before["inventory"]]
            readable = [i for i in new_items if world["items"][i]["read_text"]]
            if puzzle_id:
                st.session_state.open_dialog = ("puzzle", puzzle_id)
            elif readable:
                st.session_state.open_dialog = ("read", readable[0])  # z. B. Logbuch sofort aufschlagen
            elif spot["popup"]:
                st.session_state.open_dialog = (spot["popup"],)  # z. B. die Notiz mit dem Kabelplan
        st.rerun()

    show_message(st.session_state.message)
    minimap(world, player)


def main():
    st.set_page_config(page_title="Oxygen Alert", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
    init_state()
    world = get_world()
    screen = st.session_state.screen

    if screen == "start":
        start_screen()
    elif screen == "intro":
        slides_screen(INTRO_SLIDES, begin_mission, "🚨 Start mission")
    else:
        player = st.session_state.player
        if player["status"] == "won" and st.session_state.slide < len(OUTRO_SLIDES):
            def finish_outro():
                st.session_state.slide = len(OUTRO_SLIDES)
            slides_screen(OUTRO_SLIDES, finish_outro, "Next ▶")
        elif player["status"] in ("won", "lost"):
            ending_screen(world, player)
        else:
            game_screen(world)

    open_pending_dialog()


main()

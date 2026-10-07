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
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates

import db
import logic

IMAGE_DIR = Path(__file__).parent / "images"
IMAGE_SIZE = (1376, 768)  # Größe der Szenenbilder, auch für Platzhalter
FONT_FILES = ["Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]

INTRO_SLIDES = [
    ("Intro 1.jpeg", "Earth has fallen silent. A worldwide apocalypse – endless wars, a collapsing climate, "
                     "oceans that stopped giving life – wiped out humanity on its home planet. "
                     "Only a small crew escaped in time, aboard a single ship."),
    ("Intro 2.jpeg", "Your mission: find a new world where humans can survive. After 212 days in deep space, "
                     "the scanners finally picked one up – a red desert planet with water beneath its surface "
                     "and air that can be breathed. In a few hours, you will be the first humans to land."),
    ("Intro 3.jpeg", "You are walking down the corridor when a screeching scrape shakes the whole ship. "
                     "Alarms howl. Somewhere, air is hissing out into space …"),
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

# Große Zeichnungen für die Einblendung „You found …“ (Belohnung eines Rätsels)
ITEM_ART = {
    # nachgezeichnet nach der Brechstange im Bild „Flur after.jpeg“: dunkler, abgenutzter Stahl,
    # oben ein gebogener Haken mit Klaue, unten ein gespaltenes, gespreiztes Ende
    "brechstange": """<svg viewBox="0 0 200 200" width="230" height="230">
        <defs><linearGradient id="steel" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#6b5d53"/><stop offset=".5" stop-color="#3f3530"/>
            <stop offset="1" stop-color="#2a221e"/></linearGradient></defs>
        <g fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M62 166 L138 58 C144 48 152 42 161 44 C169 46 172 54 167 61"
                  stroke="#16110e" stroke-width="10"/>
            <path d="M62 166 L138 58 C144 48 152 42 161 44 C169 46 172 54 167 61"
                  stroke="url(#steel)" stroke-width="6.5"/>
            <path d="M66 158 L136 60 C141 52 148 47 156 47" stroke="#c9b8a6" stroke-width="2" opacity=".55"/>
            <path d="M167 61 L163 68 M167 61 L171 67" stroke="#3f3530" stroke-width="5"/>
            <path d="M62 166 L47 184 M62 166 L57 189" stroke="#16110e" stroke-width="9"/>
            <path d="M62 166 L47 184 M62 166 L57 189" stroke="#4a3f38" stroke-width="5.5"/>
        </g>
    </svg>""",
    "zugangskarte": """<svg viewBox="0 0 200 200" width="220" height="220">
        <rect x="30" y="55" width="140" height="90" rx="12" fill="#10283a" stroke="#2ee6d6" stroke-width="4"/>
        <rect x="46" y="78" width="30" height="24" rx="4" fill="#ffb321"/>
        <rect x="46" y="118" width="108" height="8" rx="4" fill="#2ee6d6" opacity=".7"/>
        <rect x="90" y="80" width="64" height="6" rx="3" fill="#f6f1e7" opacity=".6"/>
        <rect x="90" y="94" width="44" height="6" rx="3" fill="#f6f1e7" opacity=".4"/>
    </svg>""",
}


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


def end_game():
    """Nach einem Ende zurück zum Startbildschirm. Die Partie ist vorbei, deshalb wird der Spielstand gelöscht."""
    db.delete_save()
    st.session_state.player = None
    st.session_state.screen = "start"
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
def scene_image(filename, after_filename, title, patches, markers, image_mtimes=()):
    """Szenenbild: Grundbild + veränderte Stellen aus dem Danach-Bild + Sechsecke auf klickbaren Objekten.

    patches: Tupel aus (x, y, w, h) in Prozent – Objekte, die sich verändert haben (z. B. offener Spind).
             Diese Stellen werden aus dem Danach-Bild mit weichem Rand über das Grundbild gelegt.
    markers: Tupel aus (x, y, w, h) in Prozent – nur Hotspots, die noch etwas tun.
    image_mtimes: Änderungszeiten der Bilddateien, damit ein ersetztes Bild neu geladen wird.
    """
    image = load_image(filename, title)
    after_path = IMAGE_DIR / after_filename if after_filename else None
    if patches and after_path and after_path.exists():
        after = Image.open(after_path).convert("RGB").resize(image.size)
        image.paste(after, (0, 0), patch_mask(image.size, patches))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = image.size
    r = width / 85  # Größe passt sich der Bildbreite an

    def hexagon(cx, cy, radius):
        return [(cx + radius * math.cos(math.radians(60 * i)), cy + radius * math.sin(math.radians(60 * i)))
                for i in range(6)]

    for x, y, w, h in markers:
        cx, cy = (x + w / 2) / 100 * width, (y + h / 2) / 100 * height
        draw.polygon(hexagon(cx, cy, r * 1.8), fill=(255, 179, 33, 40))                       # Schein
        draw.polygon(hexagon(cx, cy, r), fill=(20, 12, 40, 160), outline=(255, 190, 70, 245),
                     width=max(2, int(r / 5)))                                                 # Rahmen
        d = r / 2.6
        draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], fill=(255, 236, 190, 255))  # Raute
    image.paste(overlay, (0, 0), overlay)
    return image


def rect(spot):
    return tuple(float(spot[k]) for k in ("x", "y", "w", "h"))


def visible_markers(world, player, hotspots):
    """Sechsecke nur dort, wo noch etwas passiert: genommene Items und gelöste Rätsel verschwinden.

    Türen behalten ihr Sechseck, auch wenn sie offen sind – man kann ja weiter durchgehen.
    """
    return tuple(rect(spot) for spot in hotspots
                 if not ((spot["item_id"] or spot["puzzle_id"]) and logic.is_hotspot_changed(world, player, spot)))


def changed_patches(world, player, hotspots):
    """Bereiche, die aus dem Danach-Bild genommen werden: alle Objekte, die sich verändert haben."""
    return tuple(rect(spot) for spot in hotspots if logic.is_hotspot_changed(world, player, spot))


def patch_mask(size, patches, padding=1.5):
    """Graustufen-Maske: weiß = Danach-Bild, schwarz = Grundbild, mit weichem Übergang am Rand."""
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for x, y, w, h in patches:
        draw.rectangle(((x - padding) / 100 * width, (y - padding) / 100 * height,
                        (x + w + padding) / 100 * width, (y + h + padding) / 100 * height), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(width / 120))


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
    """Das komplette Aussehen: holografische Glas-Panels im Stil von No Man's Sky.

    Alle Farben stehen oben als CSS-Variablen, damit man das Design an einer Stelle ändern kann.
    """
    aspect = IMAGE_SIZE[0] / IMAGE_SIZE[1]
    alarm_css = """
        .stApp::after {
            content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 999;
            box-shadow: inset 0 0 180px rgba(255, 70, 40, .5);
            animation: pulse 1.8s ease-in-out infinite;
        }
    """ if alarm else ""
    st.markdown(f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Exo+2:wght@400;500&family=Caveat:wght@500&display=swap');

        :root {{
            --glass: rgba(16, 11, 36, .72);       /* dunkles, leicht violettes Glas */
            --glass-strong: rgba(20, 13, 44, .94);
            --line: rgba(255, 255, 255, .18);
            --amber: #ffb321;                     /* Hauptakzent (wie die Markierungen in NMS) */
            --amber-deep: #ff7a18;
            --holo: #2ee6d6;                      /* holografisches Türkis */
            --magenta: #ff4fa3;
            --text: #f6f1e7;
            --muted: #b8b0cf;
            --danger: #ff4d4d;
            --cut: 12px;                          /* abgeschrägte Ecken */
            --chamfer: polygon(var(--cut) 0, 100% 0, 100% calc(100% - var(--cut)),
                               calc(100% - var(--cut)) 100%, 0 100%, 0 var(--cut));
        }}

        /* Vollbild: keine Kopfzeile, keine Seitenleiste, kein Rand */
        header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
        [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{ display: none !important; }}
        .stApp {{ background: radial-gradient(ellipse at center, #1a0f2e 0%, #05030a 75%); color: var(--text); }}
        [data-testid="stMainBlockContainer"] {{
            padding: 0 !important; margin: 0 auto;
            max-width: min(100vw, calc(100vh * {aspect:.4f})) !important;
        }}
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: 0; }}
        iframe {{ display: block; }}

        html, body, .stApp, p, li, input {{ font-family: 'Exo 2', sans-serif; }}
        h1, h2, h3, .stButton button, [data-testid="stFormSubmitButton"] button {{
            font-family: 'Chakra Petch', sans-serif !important; text-transform: uppercase; letter-spacing: .14em;
        }}
        h1 {{ font-weight: 700 !important; }}

        /* Glas-Panel mit abgeschrägten Ecken und Akzentkante – Grundlage für alle Anzeigen */
        .st-key-hud, .room-title, .message, .st-key-caption, .minimap {{
            background: var(--glass); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
            border: 1px solid var(--line); clip-path: var(--chamfer); color: var(--text);
        }}

        /* Buttons: Hauptaktion in Orange, Nebenaktionen als Glas mit Türkis-Rand */
        [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {{
            background: linear-gradient(90deg, var(--amber), var(--amber-deep)) !important; color: #1b0d00 !important;
            border: none !important; border-radius: 0 !important; clip-path: var(--chamfer); font-weight: 700;
            box-shadow: 0 0 18px rgba(255, 179, 33, .35);
        }}
        [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover {{
            filter: brightness(1.12);
        }}
        [data-testid="stBaseButton-secondary"], [data-testid="stButtonGroup"] button {{
            background: rgba(46, 230, 214, .08) !important; border: 1px solid rgba(46, 230, 214, .55) !important;
            color: var(--text) !important; border-radius: 0 !important; clip-path: var(--chamfer);
        }}
        [data-testid="stBaseButton-secondary"]:hover, [data-testid="stButtonGroup"] button:hover {{
            background: rgba(46, 230, 214, .2) !important; border-color: var(--holo) !important;
        }}
        [data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[kind$="Active"] {{
            background: rgba(255, 179, 33, .22) !important; border-color: var(--amber) !important;
        }}

        /* Anzeige oben rechts: Lebenserhaltung, Inventar, Neustart */
        .st-key-hud {{
            position: fixed; top: 14px; right: 14px; z-index: 1001; width: auto !important;
            padding: 8px 12px; align-items: center; flex-wrap: nowrap; gap: 10px !important;
            border-left: 3px solid var(--holo);
        }}
        .st-key-hud button {{ white-space: nowrap; }}
        .o2 {{ width: 190px; padding-right: 4px; }}
        .o2-head {{
            display: flex; justify-content: space-between; align-items: baseline;
            font-family: 'Chakra Petch', sans-serif; letter-spacing: .14em; font-size: .7rem; color: var(--muted);
        }}
        .o2-time {{ font-size: 1.35rem; letter-spacing: .06em; color: var(--text); font-weight: 600; }}
        .o2-bar {{ height: 6px; margin-top: 4px; background: rgba(255, 255, 255, .1); }}
        .o2-bar div {{ height: 100%; box-shadow: 0 0 10px currentColor; transition: width .9s linear; }}
        .o2.low .o2-time {{ color: var(--danger); animation: pulse 1s steps(2) infinite; }}

        .room-title {{
            position: fixed; top: 14px; left: 18px; z-index: 1000; pointer-events: none;
            padding: 8px 18px 8px 14px; border-left: 3px solid var(--amber);
        }}
        .room-title small {{
            display: block; font-family: 'Chakra Petch', sans-serif; font-size: .65rem; letter-spacing: .25em;
            color: var(--muted);
        }}
        .room-title span {{
            font-family: 'Chakra Petch', sans-serif; font-size: 1.25rem; font-weight: 600; letter-spacing: .16em;
            text-transform: uppercase;
        }}
        .message {{
            position: fixed; left: 18px; bottom: 18px; z-index: 1000; pointer-events: none;
            max-width: min(46vw, 620px, calc(100vw - 480px)); min-width: 260px;
            border-left: 3px solid var(--holo); padding: .9rem 1.2rem; font-size: 1.02rem; line-height: 1.5;
        }}
        .message b {{ color: var(--amber); }}

        /* Textfeld mit Button unten mittig (Start, Intro, Outro, Ende) */
        .st-key-caption {{
            position: fixed; left: 50%; transform: translateX(-50%); bottom: 28px; z-index: 1001;
            width: min(760px, 92vw) !important; padding: 20px 26px; gap: .8rem !important;
            border-left: 3px solid var(--amber);
        }}
        .st-key-caption .stButton {{ margin-top: .8rem; }}
        .st-key-caption h1 {{ font-size: 2.6rem; letter-spacing: .22em; text-shadow: 0 0 24px rgba(255, 179, 33, .4); }}

        .minimap {{ position: fixed; right: 18px; bottom: 18px; z-index: 1000; pointer-events: none; padding: 10px; }}
        .minimap .goal {{ animation: goal 1.2s ease-in-out infinite; }}

        /* Pop-ups: großes Hologramm-Panel */
        [role="dialog"] {{  /* Streamlit rendert Pop-ups als <section role="dialog"> */
            background: linear-gradient(160deg, rgba(34, 18, 66, .97), rgba(8, 24, 42, .97)) !important;
            color: var(--text); border: 1px solid rgba(46, 230, 214, .45) !important; border-radius: 0 !important;
            border-top: 3px solid var(--amber) !important; box-shadow: 0 0 60px rgba(46, 230, 214, .18);
        }}
        [role="dialog"] h2 {{ color: var(--amber); }}
        .slot {{
            background: rgba(46, 230, 214, .07); border: 1px solid rgba(46, 230, 214, .45);
            clip-path: var(--chamfer); padding: 16px 10px; min-height: 190px; text-align: center; margin-bottom: 8px;
        }}
        .slot.empty {{ background: rgba(255, 255, 255, .03); border: 1px dashed var(--line); color: var(--muted); }}
        .slot .icon {{
            font-size: 2.2rem; width: 70px; height: 62px; margin: 0 auto 6px; display: grid; place-items: center;
            background: rgba(255, 179, 33, .14);
            clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%);  /* Sechseck */
        }}
        .slot.empty .icon {{ background: rgba(255, 255, 255, .05); }}
        .slot .name {{
            font-family: 'Chakra Petch', sans-serif; font-size: .85rem; letter-spacing: .12em; text-transform: uppercase;
            margin: 4px 0 6px;
        }}
        .slot .desc {{ font-size: .85rem; color: var(--muted); }}
        .logbook {{
            background: radial-gradient(circle at 30% 20%, #f2e6c9, #dcc89c); color: #2d2216;
            font-family: 'Caveat', cursive; font-size: 1.5rem; line-height: 1.3;
            padding: 22px 32px; clip-path: var(--chamfer); box-shadow: inset 0 0 40px rgba(120, 90, 40, .45);
        }}
        .logbook p {{ margin: 0 0 .6em; }}
        .logbook p:last-child {{ margin-bottom: 0; }}

        /* Rätsel: holografische Bedienfelder */
        .puzzle-prompt {{ font-size: 1.05rem; color: var(--muted); margin-bottom: 16px; }}
        .st-key-lockpad, .st-key-cablepanel {{
            background: linear-gradient(160deg, rgba(46, 230, 214, .10), rgba(46, 230, 214, .02));
            border: 1px solid rgba(46, 230, 214, .5); clip-path: var(--chamfer); padding: 22px 26px;
            box-shadow: inset 0 0 40px rgba(46, 230, 214, .08);
        }}
        .st-key-lockpad [data-testid="stTextInputRootElement"], .st-key-lockpad [data-baseweb="input"] {{
            height: 84px; background: rgba(5, 4, 14, .85); border: 1px solid rgba(255, 179, 33, .6);
            border-radius: 0; clip-path: var(--chamfer); box-shadow: inset 0 0 18px rgba(0, 0, 0, .8);
        }}
        .st-key-lockpad input {{
            text-align: center; font-family: 'Chakra Petch', monospace !important; color: var(--amber) !important;
            background: transparent !important; caret-color: var(--amber); text-shadow: 0 0 12px rgba(255, 179, 33, .7);
            font-size: 2.6rem !important; height: 100% !important; padding: 0 !important;
        }}
        [data-testid="InputInstructions"] {{ display: none; }}
        .panel-head {{
            font-family: 'Chakra Petch', sans-serif; font-size: .78rem; letter-spacing: .22em; color: var(--holo);
            display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
        }}
        .led {{
            width: 10px; height: 10px; background: var(--danger); box-shadow: 0 0 10px var(--danger);
            transform: rotate(45deg);  /* Raute statt Kreis */
        }}
        .st-key-cablepanel [data-testid="stWidgetLabel"] p {{
            font-family: 'Chakra Petch', sans-serif; font-size: .72rem; letter-spacing: .2em; color: var(--muted);
        }}
        .denied {{
            color: var(--danger); font-family: 'Chakra Petch', sans-serif; letter-spacing: .1em; font-size: .9rem;
            margin-top: 14px; text-transform: uppercase;
        }}

        /* „You found …“: 3 Sekunden einblenden, dann verschwinden */
        .found {{
            position: fixed; inset: 0; z-index: 1002; pointer-events: none;
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
            background: radial-gradient(circle at center, rgba(255, 179, 33, .22), rgba(5, 3, 10, .6) 55%);
            animation: found 3s ease-in-out forwards;
        }}
        .found-art {{
            filter: drop-shadow(0 0 14px rgba(255, 179, 33, .95)) drop-shadow(0 0 42px rgba(255, 179, 33, .6));
            animation: float 3s ease-in-out;
        }}
        .found-text {{
            font-family: 'Chakra Petch', sans-serif; font-size: 2rem; font-weight: 700; letter-spacing: .2em;
            text-transform: uppercase; color: var(--text); text-shadow: 0 0 22px rgba(255, 179, 33, .8);
            background: var(--glass); padding: 10px 26px; border-left: 3px solid var(--amber); clip-path: var(--chamfer);
        }}
        @keyframes found {{
            0% {{ opacity: 0; transform: scale(.92); }}  12% {{ opacity: 1; transform: scale(1); }}
            82% {{ opacity: 1; }}  100% {{ opacity: 0; visibility: hidden; }}
        }}
        @keyframes float {{ 0% {{ transform: translateY(14px) rotate(-6deg); }} 100% {{ transform: translateY(0) rotate(0); }} }}

        @keyframes pulse {{ 0%, 100% {{ opacity: .2; }} 50% {{ opacity: 1; }} }}
        @keyframes goal {{ 0%, 100% {{ stroke: var(--magenta); }} 50% {{ stroke: transparent; }} }}
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


def show_found_item(item):
    """Leuchtendes Item in der Bildmitte, blendet nach 3 Sekunden von selbst aus (reines CSS)."""
    art = ITEM_ART.get(item["id"], f'<div style="font-size:7rem">{ITEM_ICONS.get(item["id"], "📦")}</div>')
    name = item["name"].lower()
    article = "an" if name[0] in "aeiou" else "a"
    st.markdown(f'<div class="found"><div class="found-art">{art}</div>'
                f'<div class="found-text">You found {article} {html.escape(name)}</div></div>', unsafe_allow_html=True)


@st.fragment(run_every=1)
def timer():
    """Läuft jede Sekunde neu, ohne die ganze Seite neu zu laden."""
    sync_time()
    player = st.session_state.player
    if not logic.is_playing(player):
        st.rerun()  # ganze Seite neu laden, damit das Ende angezeigt wird
    seconds = player["remaining_seconds"]
    share = seconds / logic.START_SECONDS
    color = "#2ee6d6" if share > .5 else "#ffb321" if share > .2 else "#ff4d4d"  # Türkis -> Orange -> Rot
    css = "o2 low" if seconds <= 60 else "o2"
    st.markdown(f'<div class="{css}"><div class="o2-head"><span>LIFE SUPPORT</span>'
                f'<span class="o2-time">{seconds // 60:02d}:{seconds % 60:02d}</span></div>'
                f'<div class="o2-bar"><div style="width:{share * 100:.1f}%; background:{color}; color:{color}"></div>'
                f'</div></div>', unsafe_allow_html=True)


def minimap(world, player):
    """Mini-Map unten rechts: gezeichnet aus den Rooms (Position) und der Map (Wege)."""
    rooms = {rid: r for rid, r in world["rooms"].items() if r["map_x"] != ""}
    goal = logic.goal_room_id(world)
    box_w, box_h, gap = 126, 44, 30

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
        color = "#ff4d4d" if locked else "#2ee6d6"
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" {dash}/>')
        if locked:
            parts.append(f'<text x="{(x1 + x2) / 2}" y="{y1 - 8}" font-size="14" text-anchor="middle">🔒</text>')

    for rid, room in rooms.items():
        x, y = pos(room)
        here = rid == player["current_room_id"]
        fill = "rgba(255,179,33,.28)" if here else "rgba(255,255,255,.05)"
        css = 'class="goal"' if rid == goal else ""
        stroke = "#ff4fa3" if rid == goal else "#ffb321" if here else "rgba(255,255,255,.35)"
        c = 8  # abgeschrägte Ecken wie bei den Panels
        corners = (f"{x + c},{y} {x + box_w},{y} {x + box_w},{y + box_h - c} "
                   f"{x + box_w - c},{y + box_h} {x},{y + box_h} {x},{y + c}")
        parts.append(f'<polygon {css} points="{corners}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x + box_w / 2}" y="{y + box_h / 2 + 4}" font-size="10.5" fill="#f6f1e7" '
                     f'text-anchor="middle" letter-spacing="1.5" font-family="Chakra Petch, sans-serif">'
                     f'{html.escape(room["name"].upper())}</text>')
        if here:
            parts.append(f'<polygon points="{x + box_w - 10},{y + 4} {x + box_w - 5},{y + 9} '
                         f'{x + box_w - 10},{y + 14} {x + box_w - 15},{y + 9}" fill="#ffb321"/>')

    width = 20 + max(int(r["map_x"]) for r in rooms.values()) * (box_w + gap) + box_w
    height = 20 + max(int(r["map_y"]) for r in rooms.values()) * (box_h + gap) + box_h
    st.markdown(f'<div class="minimap"><svg width="{width}" height="{height}">{"".join(parts)}</svg></div>',
                unsafe_allow_html=True)


def read_aloud_button(text):
    """Kleiner Button, der den Text mit der Sprachausgabe des Browsers vorliest."""
    st.iframe(f"""
        <style>body {{ margin: 0; padding: 2px; }}</style>
        <button id="speak" style="font-family: sans-serif; font-size: 14px; letter-spacing: 2px; color: #f6f1e7;
            cursor: pointer; background: rgba(46,230,214,.12); border: 1px solid #2ee6d6; padding: 8px 16px;">
            🔊 READ ALOUD</button>
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
            apply(new_player, "")  # kein Meldungsfeld – stattdessen die große Einblendung
            st.session_state.found_item = world["puzzles"][puzzle_id]["reward_item_id"]
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
    ink = "#3b2f1e" if paper else "#b8b0cf"
    font_family = "Caveat, cursive" if paper else "Chakra Petch, sans-serif"
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
            parts.append(f'<rect x="{sx - 32}" y="{sy - 32}" width="64" height="64" fill="rgba(5,4,14,.7)" '
                         f'stroke="#2ee6d6" stroke-opacity=".6" stroke-width="1.5"/>')
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="14" fill="#000" stroke="#2ee6d6" stroke-opacity=".35" '
                         f'stroke-width="3"/>')
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
        if st.button("End Game", type="primary"):
            end_game()
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
    st.markdown(f'<div class="room-title"><small>LOCATION</small><span>{html.escape(room["name"])}</span></div>',
                unsafe_allow_html=True)

    mtimes = tuple((IMAGE_DIR / name).stat().st_mtime if name and (IMAGE_DIR / name).exists() else 0
                   for name in (room["image"], room["image_after"]))
    image = scene_image(room["image"], room["image_after"], room["name"],
                        changed_patches(world, player, hotspots), visible_markers(world, player, hotspots), mtimes)
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
    found = st.session_state.pop("found_item", None)  # nur einmal zeigen
    if found:
        show_found_item(world["items"][found])
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

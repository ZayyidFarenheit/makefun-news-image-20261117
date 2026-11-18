#!/usr/bin/env python3
"""Draw the news-image-20261117 entry.

A newspaper front page (1024x1024) summing up Tuesday 17 November 2026
world news in one image. Copies the rank-1 winner's layout closely:
huge serif masthead, a top row of 3 large illustrated stories, a grid of
10 smaller illustrated stories, a world map with numbered pins, a numbered
brief list (14-43) and a sources footer. One change: a slim "BY THE
NUMBERS" strip under the masthead.

Deterministic: no network, no randomness, no timestamps. Pure Pillow.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (25, 25, 25)
RED = (168, 35, 42)
GREY_TXT = (70, 70, 70)
RULE = (40, 40, 40)

NAVY = (31, 58, 95)
BLUE = (43, 94, 167)
ORANGE = (192, 122, 26)
BRICK = (178, 74, 32)
PURPLE = (122, 79, 163)
GREEN = (46, 125, 79)
TEAL = (31, 122, 109)
REDK = (176, 39, 39)
DARKRED = (122, 31, 31)
GREY = (85, 85, 85)
BLACK = (26, 26, 26)
SPORT = (107, 26, 26)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(d, text, f, maxw, max_lines=None):
    """Greedy word wrap; returns a list of lines (at most max_lines)."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
            if max_lines and len(lines) >= max_lines:
                break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    return lines


def fit(d, text, path, maxw, start, minimum=8):
    """Largest font size (<= start) at which text fits maxw."""
    size = start
    while size > minimum and d.textlength(text, font=font(path, size)) > maxw:
        size -= 1
    return font(path, size)


def center_text(d, cx, y, text, f, fill):
    d.text((cx, y), text, font=f, fill=fill, anchor="ma")


def pill(d, x, y, w, h, fill, text, size=10, tfill=(255, 255, 255)):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    f = font(SANS_B, size)
    tw = d.textlength(text, font=f)
    while tw > w - 8 and size > 7:
        size -= 1
        f = font(SANS_B, size)
        tw = d.textlength(text, font=f)
    d.text((x + w / 2, y + h / 2 - size / 2 - 1), text, font=f, fill=tfill,
           anchor="ma")


# ---------------------------------------------------------------- data
TOP3 = [
    dict(num=1, region="EUROPE · UKRAINE WAR", color=BLUE,
         headline="Ukraine says a Crimean Bridge road span fell into the sea",
         deck="Second strike in two days; Zelensky hails an \u201cunprecedented "
              "operation\u201d. The Kremlin vows to rebuild.",
         strip="KERCH STRAIT · STRUCK FOR A SECOND DAY", strip_color=NAVY,
         ill="bridge"),
    dict(num=2, region="MIDDLE EAST · IRAN WAR", color=BRICK,
         headline="Iran sends drones at a US radar in Bahrain; US hits back",
         deck="Bahrain and the US say all were downed; US jets then strike "
              "Qeshm. Iran says tankers hit mines in Hormuz.",
         strip=None, strip_color=None, ill="gulf"),
    dict(num=3, region="ASIA · DIPLOMACY", color=PURPLE,
         headline="Trump holds his first Quad summit, in Manila",
         deck="The four unveil critical-minerals deals; Putin reaches "
              "Shenzhen for Thursday\u2019s talks with Trump and Xi.",
         strip="NEW CRITICAL-MINERALS DEALS", strip_color=PURPLE,
         ill="quad"),
]

GRID = [
    dict(num=4, region="AFRICA · HEALTH", color=GREEN,
         headline="Ebola cases in DR Congo top 11,000, WHO says",
         deck="Cases more than doubled in three months; about 5,400 have died.",
         strip="DR CONGO · EBOLA", strip_color=GREEN, ill="ebola"),
    dict(num=5, region="GLOBAL · CLIMATE", color=TEAL,
         headline="COP31 divided over a fossil-fuel phase-out",
         deck="Nations weigh the first draft; the Antalya talks end Friday.",
         strip="COP31 ANTALYA · ENDS FRI", strip_color=TEAL, ill="cop31"),
    dict(num=6, region="AMERICAS · HEALTH", color=REDK,
         headline="US, Mexico and Bolivia lose measles-free status",
         deck="PAHO cites a year of spread; the US has 5,700+ cases in 2026.",
         strip="MEASLES-FREE STATUS REVOKED", strip_color=REDK, ill="measles"),
    dict(num=7, region="US · BUSINESS", color=BLACK,
         headline="Nvidia\u2019s quarterly sales double to $115.8bn",
         deck="Reported after the close. Earlier the Dow fell 849 points (-1.6%).",
         strip="NVIDIA QUARTER · WALL STREET", strip_color=BLACK, ill="nvidia"),
    dict(num=8, region="MIDDLE EAST · GAZA", color=DARKRED,
         headline="Gaza truce at risk of collapse, UN is told",
         deck="Board of Peace report; UN agencies say 1.4m face acute hunger.",
         strip="GAZA · WINTER AID HELD UP", strip_color=DARKRED, ill="gaza"),
    dict(num=9, region="ASIA · POLITICS", color=TEAL,
         headline="Mongolia\u2019s president says he will resign",
         deck="Kh\u00fcrels\u00fckh denies a $25m bribe claim; parliament must accept.",
         strip="ULAANBAATAR · GRAFT CLAIM DENIED", strip_color=TEAL,
         ill="mongolia"),
    dict(num=10, region="EUROPE · POLITICS", color=BLUE,
         headline="Serbia\u2019s student-led majority takes its seats",
         deck="Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into "
              "opposition.",
         strip="BELGRADE · PARLIAMENT SWORN IN", strip_color=BLUE,
         ill="serbia"),
    dict(num=11, region="ASIA · LABOUR", color=GREEN,
         headline="Bangladesh police tear-gas garment workers",
         deck="They want Tk 30,000 a month, up from 12,500; 37 factories shut.",
         strip="DHAKA · SAVAR · GAZIPUR", strip_color=GREEN, ill="garment"),
    dict(num=12, region="RUSSIA · AIR CRASH", color=GREY,
         headline="Russian An-12 crash in Siberia kills all 19",
         deck="The air force plane came down near Kemerovo; a fault is suspected.",
         strip="KEMEROVO · ALL 19 ABOARD KILLED", strip_color=GREY, ill="an12"),
    dict(num=13, region="AFRICA · JUSTICE", color=TEAL,
         headline="Mozambique puts opposition leader on trial",
         deck="Ven\u00e2ncio Mondlane faces 5 charges over deadly 2024 protests.",
         strip="MAPUTO · SUPREME COURT", strip_color=TEAL, ill="trial"),
]

# (number, place, text, badge colour) for the "ALSO ON TUESDAY" list.
ALSO = [
    (14, "Russia", "says it downed a record 1,441 drones overnight", BLUE),
    (15, "Kyiv", "missiles hit the North and South Dnipro bridges", BLUE),
    (16, "UN", "Ukraine\u2019s civilian deaths this year top all of 2025", GREY),
    (17, "Prague", "two trains collide; 46 people injured", BLUE),
    (18, "France", "public-sector strike; 146,000 march (CGT: 500,000)", BLUE),
    (19, "Poland", "Tusk\u2019s government survives a no-confidence vote", BLUE),
    (20, "Germany", "Deutsche Bank shares fall after a huge data leak", BLUE),
    (21, "Moldova", "shuts its airspace as a drone nears Chi\u0219in\u0103u", BLUE),
    (22, "Turkey", "police seize opposition broadcaster S\u00f6zc\u00fc TV", ORANGE),
    (23, "Football", "Norway win 3-2 in Denmark; Haaland scores twice", SPORT),
    (24, "Vatican", "Pope Leo XIV returns from his South America tour", GREY),
    (25, "UK", "sanctions 8 settlement firms and Tzav 9", BLUE),
    (26, "Israel", "Eisenkot ally Matan Kahana elected speaker, 66-52", ORANGE),
    (27, "West Bank", "settlers kill a woman, 72, near Jericho", ORANGE),
    (28, "Oman", "Iran\u2019s Araghchi holds shipping-safety talks", ORANGE),
    (29, "India", "Cyclone Akvan strengthens; Odisha evacuates", PURPLE),
    (30, "India", "bus falls into an Uttarakhand gorge, 8 dead", PURPLE),
    (31, "Japan", "protests a Russian airspace intrusion near Fukuoka", PURPLE),
    (32, "China-Canada", "more tariff cuts after Carney-Xi talks", PURPLE),
    (33, "Malaysia", "Macron visit seals a strategic partnership", PURPLE),
    (34, "Thailand", "pledges to scrap tariffs on US goods", PURPLE),
    (35, "South Korea", "IMF lifts 2026 growth forecast to 3.9%", PURPLE),
    (36, "Football", "India beat Pakistan 2-1 in SAFF final", SPORT),
    (37, "Kenya", "WFP aids 30,000 who fled Ethiopia clashes", GREEN),
    (38, "Football", "Togo beat Algeria 3-0 in AFCON qualifier", SPORT),
    (39, "Haiti", "Aristide\u2019s party will field no candidates", REDK),
    (40, "US Senate", "Van Hollen challenges Schumer for leader", REDK),
    (41, "Australia", "eases planned backpacker visa curbs", TEAL),
    (42, "Darwin", "M6.6 quake off Indonesia felt; no tsunami", TEAL),
    (43, "Apple", "Pay, iCloud and App Store outage; not a hack", REDK),
]

# (lon, lat) for map pins 1-13 and dots 14-43.
PINS = {
    1: (34.0, 45.3, BLUE), 2: (50.5, 26.2, ORANGE), 3: (121.0, 14.6, PURPLE),
    4: (23.0, -2.0, GREEN), 5: (30.7, 37.5, GREY), 6: (-95.0, 38.0, REDK),
    7: (-74.0, 40.7, REDK), 8: (34.5, 31.0, ORANGE), 9: (106.9, 47.9, PURPLE),
    10: (20.5, 44.8, BLUE), 11: (90.4, 23.8, PURPLE), 12: (86.0, 55.4, BLUE),
    13: (32.6, -25.9, GREEN),
}
DOTS = {
    14: (37.0, 55.0, BLUE), 15: (30.5, 50.4, BLUE), 16: (34.0, 48.0, GREY),
    17: (14.4, 50.0, BLUE), 18: (2.3, 48.8, BLUE), 19: (21.0, 52.2, BLUE),
    20: (13.4, 52.5, BLUE), 21: (28.8, 47.0, BLUE), 22: (32.8, 39.9, ORANGE),
    23: (12.6, 55.7, BLUE), 24: (12.5, 41.9, BLUE), 25: (-0.1, 51.5, BLUE),
    26: (35.2, 31.8, ORANGE), 27: (35.9, 31.6, ORANGE), 28: (58.4, 23.6, ORANGE),
    29: (85.8, 20.3, PURPLE), 30: (79.0, 30.3, PURPLE), 31: (130.4, 33.6, PURPLE),
    32: (116.4, 39.9, PURPLE), 33: (101.7, 3.1, PURPLE), 34: (100.5, 13.7, PURPLE),
    35: (127.0, 37.5, PURPLE), 36: (77.2, 28.6, PURPLE), 37: (36.8, -1.3, GREEN),
    38: (1.2, 6.1, GREEN), 39: (-72.3, 18.5, REDK), 40: (-77.0, 38.9, REDK),
    41: (149.1, -35.3, TEAL), 42: (130.8, -12.5, TEAL), 43: (-122.0, 37.3, REDK),
}

# Simplified continent outlines in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-85, 20), (-90, 15), (-95, 18), (-105, 22), (-115, 30), (-125, 40),
     (-125, 48), (-135, 58), (-155, 60), (-168, 66)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-25, 75),
     (-40, 78), (-58, 75), (-60, 68), (-55, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -20), (-40, -30), (-50, -35), (-60, -40), (-70, -45),
     (-70, -55), (-75, -50), (-75, -35), (-80, -20), (-80, -10), (-80, 10)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (50, 10), (48, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -30), (12, -18), (13, -5), (9, 4), (0, 5), (-8, 5),
     (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (23, 58), (28, 60), (30, 62), (30, 68), (25, 70),
     (18, 70), (12, 65), (5, 60), (5, 58), (0, 52), (-5, 50), (-10, 45),
     (-10, 36)],
    [(30, 36), (35, 36), (40, 38), (45, 40), (50, 40), (55, 45), (60, 45),
     (65, 50), (70, 55), (75, 60), (80, 65), (90, 70), (100, 72), (110, 73),
     (120, 72), (130, 70), (140, 72), (150, 70), (160, 66), (170, 66),
     (178, 65), (170, 60), (162, 58), (158, 52), (150, 60), (142, 55),
     (140, 50), (135, 45), (130, 40), (127, 38), (122, 32), (120, 28),
     (115, 22), (110, 20), (105, 10), (103, 5), (100, 8), (98, 12),
     (95, 16), (92, 20), (90, 22), (85, 20), (80, 15), (77, 8), (75, 15),
     (72, 20), (68, 23), (65, 25), (60, 25), (57, 27), (52, 28), (50, 30),
     (48, 30), (45, 32), (42, 35), (38, 36), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -35), (125, -33), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -30), (150, -25),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
]


# ------------------------------------------------------- illustrations
def _smoke(d, cx, cy, r, col=(120, 120, 120)):
    for dx, dy, rr in ((-r, 0, r * 0.7), (0, -r * 0.5, r * 0.8),
                       (r * 0.8, 0, r * 0.65), (0, r * 0.4, r * 0.6)):
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr],
                  fill=col)


def _plane(d, cx, cy, s, col=(30, 30, 30)):
    d.polygon([(cx - s, cy), (cx + s, cy - s * 0.25), (cx + s * 0.4, cy),
               (cx + s, cy + s * 0.25)], fill=col)
    d.polygon([(cx - s * 0.2, cy), (cx + s * 0.2, cy - s * 0.7),
               (cx + s * 0.5, cy)], fill=col)


def _flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for i in range(7):
        if i % 2 == 0:
            d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                        fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.42, y + h * 0.55], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 2 + c * w * 0.09, y + 2 + r * h * 0.16,
                       x + 4 + c * w * 0.09, y + 4 + r * h * 0.16],
                      fill=(255, 255, 255))


def _flag_india(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 153, 51))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(19, 136, 8))
    d.ellipse([x + w / 2 - h / 6, y + h / 3, x + w / 2 + h / 6,
               y + 2 * h / 3], outline=(0, 0, 128))


def _flag_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.ellipse([x + w / 2 - h / 4, y + h / 4, x + w / 2 + h / 4,
               y + 3 * h / 4], fill=(188, 0, 45))


def _flag_australia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    d.rectangle([x, y, x + w * 0.5, y + h * 0.5], fill=(200, 200, 200))
    d.line([x, y, x + w * 0.5, y + h * 0.5], fill=(188, 0, 45), width=2)
    d.line([x + w * 0.5, y, x, y + h * 0.5], fill=(188, 0, 45), width=2)
    for sx, sy in ((0.72, 0.3), (0.85, 0.6), (0.7, 0.75)):
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2,
                   y + h * sy + 2], fill=(255, 255, 255))


def _strip(d, x, y, w, h, color, text):
    d.rectangle([x, y, x + w, y + h], fill=color)
    f = fit(d, text, SANS_B, w - 10, 10)
    d.text((x + w / 2, y + h / 2 - 1), text, font=f, fill=(255, 255, 255),
           anchor="mm")


def ill_bridge(d, x, y, w, h):
    # Pale sky, blue water, thin clean deck with a clear fallen gap.
    d.rectangle([x, y, x + w, y + h], fill=(202, 224, 236))
    d.rectangle([x, y + 44, x + w, y + h], fill=(88, 138, 173))
    for wy in (52, 60, 68):
        for wx in range(0, w, 30):
            d.arc([x + wx, y + wy - 3, x + wx + 24, y + wy + 5], 0, 180,
                  fill=(140, 182, 210))
    cx = x + w // 2
    # Slender pillars (none under the fallen gap).
    for px in (x + 30, x + 95, cx + 70, cx + 130, x + w - 28):
        d.rectangle([px, y + 44, px + 4, y + 80], fill=(70, 76, 84))
    # Thin deck, split where the span fell.
    d.rectangle([x, y + 40, cx - 36, y + 44], fill=(55, 60, 68))
    d.rectangle([cx + 36, y + 40, x + w, y + 44], fill=(55, 60, 68))
    # Fallen span: a thin tilted deck segment dropping into the water.
    d.polygon([(cx - 36, y + 40), (cx - 28, y + 44), (cx - 12, y + 66),
               (cx - 20, y + 68)], fill=(55, 60, 68))
    # Small white splash where the span meets the water.
    d.line([cx - 26, y + 68, cx - 18, y + 64], fill=(255, 255, 255), width=2)
    d.line([cx - 22, y + 68, cx - 14, y + 68], fill=(255, 255, 255), width=2)
    # Orange flash at the break point.
    d.polygon([(cx, y + 28), (cx + 4, y + 34), (cx + 10, y + 34),
               (cx + 5, y + 38), (cx + 7, y + 44), (cx, y + 40),
               (cx - 7, y + 44), (cx - 5, y + 38), (cx - 10, y + 34),
               (cx - 4, y + 34)], fill=(230, 160, 30))
    d.ellipse([cx - 3, y + 32, cx + 3, y + 38], fill=(250, 210, 60))
    # Soft smoke plume rising from the break.
    d.ellipse([cx - 12, y + 8, cx + 2, y + 22], fill=(175, 175, 175))
    d.ellipse([cx - 2, y + 2, cx + 12, y + 16], fill=(185, 185, 185))
    d.ellipse([cx + 4, y + 12, cx + 16, y + 24], fill=(170, 170, 170))
    # Two jets, well clear of the labels.
    _plane(d, x + 78, y + 14, 9)
    _plane(d, x + w - 96, y + 16, 9)
    f = font(SANS_B, 10)
    d.text((x + 6, y + 6), "CRIMEA", font=f, fill=(60, 60, 60))
    d.text((x + w - 46, y + 6), "RUSSIA", font=f, fill=(60, 60, 60))


def ill_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 200, 216))
    d.polygon([(x, y), (x + w, y), (x + w, y + 26), (x + w * 0.62, y + 34),
               (x + w * 0.45, y + 22), (x + w * 0.2, y + 30), (x, y + 24)],
              fill=(232, 217, 176))
    d.ellipse([x + w * 0.30, y + 46, x + w * 0.36, y + 56], fill=(232, 217, 176))
    d.ellipse([x + w * 0.72, y + 52, x + w * 0.86, y + 60], fill=(232, 217, 176))
    f = font(SANS_B, 10)
    d.text((x + w * 0.44, y + 4), "IRAN", font=f, fill=(90, 70, 40))
    d.text((x + w * 0.24, y + 58), "BAHRAIN", font=f, fill=(70, 60, 40))
    d.text((x + w * 0.66, y + 40), "QESHM", font=f, fill=(70, 60, 40))
    d.text((x + w * 0.82, y + 64), "HORMUZ", font=f, fill=(70, 60, 40))
    for i in range(9):
        t = i / 8.0
        px = x + w * 0.30 + t * w * 0.28
        py = y + 52 - t * 16
        if i % 2 == 0:
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5],
                      fill=(176, 39, 39))
    d.line([x + w * 0.60, y + 62, x + w * 0.78, y + 50], fill=(43, 94, 167),
           width=2)
    for i in range(5):
        t = i / 4.0
        px = x + w * 0.60 + t * w * 0.18
        py = y + 62 - t * 12
        if i % 2 == 0:
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5],
                      fill=(43, 94, 167))
    d.line([x + w * 0.34, y + 46, x + w * 0.38, y + 50], fill=(176, 39, 39),
           width=3)
    d.line([x + w * 0.34, y + 50, x + w * 0.38, y + 46], fill=(176, 39, 39),
           width=3)
    d.polygon([(x + w * 0.92, y + 42), (x + w * 0.96, y + 48),
               (x + w * 0.92, y + 54), (x + w * 0.88, y + 48)],
              fill=(230, 160, 30))
    pill(d, x + w * 0.36, y + 24, 96, 15, (176, 39, 39), "DRONES DOWNED", 9)
    pill(d, x + w * 0.52, y + 62, 78, 15, (43, 94, 167), "US STRIKES", 9)


def ill_quad(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 221, 240))
    d.rectangle([x, y, x + w, y + 20], fill=PURPLE)
    center_text(d, x + w / 2, y + 3, "QUAD LEADERS\u2019 SUMMIT · MANILA",
                font(SANS_B, 11), (255, 255, 255))
    fw, fh = 56, 26
    gap = (w - 4 * fw) / 5
    flags = [_flag_us, _flag_india, _flag_japan, _flag_australia]
    names = ["US", "INDIA", "JAPAN", "AUSTRALIA"]
    for i, fn in enumerate(flags):
        fx = x + gap + i * (fw + gap)
        fn(d, fx, y + 26, fw, fh)
        d.rectangle([fx, y + 26, fx + fw, y + 26 + fh], outline=(120, 120, 120))
        center_text(d, fx + fw / 2, y + 54, names[i], font(SANS_B, 8),
                    (60, 60, 60))
    d.rectangle([x, y + 66, x + w, y + 70], fill=(120, 80, 40))
    _strip(d, x, y + 70, w, h - 70, PURPLE, "NEW CRITICAL-MINERALS DEALS")


def ill_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 242, 228))
    d.rectangle([x + 18, y + 30, x + 78, y + 60], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.polygon([(x + 14, y + 30), (x + 48, y + 16), (x + 82, y + 30)],
              fill=(176, 39, 39))
    d.rectangle([x + 44, y + 38, x + 52, y + 54], fill=(176, 39, 39))
    d.rectangle([x + 38, y + 44, x + 58, y + 48], fill=(176, 39, 39))
    d.rectangle([x + 8, y + 8, x + 30, y + 20], fill=(0, 122, 178))
    d.polygon([(x + 8, y + 8), (x + 14, y + 8), (x + 8, y + 20)],
              fill=(206, 16, 33))
    d.ellipse([x + 19, y + 12, x + 23, y + 16], fill=(247, 214, 22))
    d.rectangle([x + 92, y + 34, x + 108, y + 60], fill=(120, 120, 120))
    d.ellipse([x + 96, y + 22, x + 104, y + 30], fill=(220, 190, 150))
    d.rectangle([x + 92, y + 30, x + 108, y + 34], fill=(255, 255, 255))
    pill(d, x + w - 78, y + 6, 72, 15, (176, 39, 39), "11,000+ CASES", 9)


def ill_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 238, 242))
    d.ellipse([x + 10, y + 16, x + 50, y + 56], fill=(90, 140, 190))
    d.ellipse([x + 18, y + 22, x + 32, y + 34], fill=(120, 190, 110))
    d.ellipse([x + 32, y + 40, x + 44, y + 50], fill=(120, 190, 110))
    # Wide white box so all three lines fit without overflow.
    d.rectangle([x + 56, y + 8, x + 140, y + 54], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.text((x + 60, y + 12), "DRAFT:", font=font(SANS_B, 9), fill=(30, 30, 30))
    d.text((x + 60, y + 23), "PHASE OUT", font=font(SANS_B, 9),
           fill=(30, 30, 30))
    d.text((x + 60, y + 34), "FOSSIL FUELS?", font=font(SANS_B, 9),
           fill=(30, 30, 30))
    d.rectangle([x + 148, y + 12, x + 154, y + 46], fill=(200, 200, 200),
                outline=(120, 120, 120))
    d.rectangle([x + 150, y + 22, x + 152, y + 44], fill=(200, 60, 40))
    d.ellipse([x + 144, y + 44, x + 158, y + 58], fill=(200, 60, 40))
    import math
    d.ellipse([x + 167, y + 37, x + 181, y + 51], fill=(247, 214, 22))
    for a in range(0, 360, 45):
        dx = math.cos(math.radians(a))
        dy = math.sin(math.radians(a))
        d.line([x + 174 + dx * 10, y + 44 + dy * 10, x + 174 + dx * 13,
                y + 44 + dy * 13], fill=(230, 160, 30), width=2)


def ill_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(247, 234, 217))
    _flag_us(d, x + 12, y + 8, 34, 18)
    d.rectangle([x + 62, y + 8, x + 96, y + 26], fill=(0, 104, 71))
    d.rectangle([x + 62, y + 8, x + 96, y + 14], fill=(0, 104, 71))
    d.rectangle([x + 62, y + 14, x + 96, y + 20], fill=(255, 255, 255))
    d.rectangle([x + 62, y + 20, x + 96, y + 26], fill=(206, 17, 38))
    d.ellipse([x + 76, y + 14, x + 82, y + 20], fill=(140, 60, 40))
    d.rectangle([x + 112, y + 8, x + 146, y + 26], fill=(214, 0, 28))
    d.rectangle([x + 112, y + 8, x + 146, y + 14], fill=(214, 0, 28))
    d.rectangle([x + 112, y + 14, x + 146, y + 20], fill=(247, 214, 22))
    d.rectangle([x + 112, y + 20, x + 146, y + 26], fill=(0, 122, 61))
    for cx, cy, r in ((150, 48, 9), (40, 52, 8), (100, 50, 7)):
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(200, 60, 60))
        for a in range(0, 360, 45):
            import math
            dx = math.cos(math.radians(a)) * (r + 3)
            dy = math.sin(math.radians(a)) * (r + 3)
            d.line([x + cx, y + cy, x + cx + dx, y + cy + dy],
                   fill=(200, 60, 60), width=2)
    d.text((x + 8, y + 34), "US", font=font(SANS_B, 8), fill=(90, 90, 90))
    d.text((x + 70, y + 30), "MEXICO", font=font(SANS_B, 8), fill=(90, 90, 90))
    d.text((x + 116, y + 30), "BOLIVIA", font=font(SANS_B, 8),
           fill=(90, 90, 90))


def ill_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 31, 20))
    d.rectangle([x + 10, y + 14, x + 42, y + 46], fill=(30, 90, 50),
                outline=(80, 200, 120))
    d.line([x + 14, y + 22, x + 26, y + 22, x + 26, y + 30, x + 38, y + 30],
           fill=(120, 220, 140), width=2)
    d.line([x + 14, y + 38, x + 22, y + 38, x + 22, y + 30, x + 38, y + 30],
           fill=(120, 220, 140), width=2)
    pts = [(58, 54), (74, 48), (90, 50), (106, 40), (122, 42), (138, 26),
           (154, 28), (170, 14)]
    for i in range(len(pts) - 1):
        d.line([x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
                y + pts[i + 1][1]], fill=(80, 220, 110), width=3)
    for px, ph in ((62, 14), (82, 20), (102, 12), (122, 26), (142, 18),
                   (162, 30)):
        d.rectangle([x + px, y + 56 - ph, x + px + 10, y + 56],
                    fill=(60, 180, 90))
    d.text((x + 52, y + 4), "$115.8BN", font=font(SANS_B, 15),
           fill=(90, 230, 120))
    d.text((x + 54, y + 24), "DOW -849", font=font(SANS_B, 11),
           fill=(230, 80, 80))


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 224, 204))
    d.polygon([(x + 16, y + 56), (x + 36, y + 30), (x + 56, y + 56)],
              fill=(245, 245, 240))
    d.polygon([(x + 62, y + 56), (x + 84, y + 34), (x + 106, y + 56)],
              fill=(220, 220, 210))
    d.rectangle([x + 118, y + 38, x + 168, y + 56], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.rectangle([x + 118, y + 38, x + 138, y + 56], fill=(200, 200, 200))
    d.text((x + 142, y + 42), "AID", font=font(SANS_B, 11), fill=(30, 30, 30))
    d.ellipse([x + 124, y + 56, x + 130, y + 62], fill=(30, 30, 30))
    d.ellipse([x + 156, y + 56, x + 162, y + 62], fill=(30, 30, 30))
    pill(d, x + w - 108, y + 6, 102, 15, (122, 31, 31),
         "1.4M FACE ACUTE HUNGER", 8)


def ill_mongolia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 226, 210))
    d.rectangle([x + 10, y + 12, x + 18, y + 40], fill=(206, 16, 33))
    d.rectangle([x + 18, y + 12, x + 26, y + 40], fill=(0, 80, 160))
    d.rectangle([x + 26, y + 12, x + 34, y + 40], fill=(206, 16, 33))
    d.ellipse([x + 12, y + 16, x + 16, y + 20], fill=(247, 214, 22))
    d.rectangle([x + 46, y + 34, x + 106, y + 58], fill=(200, 200, 200))
    d.polygon([(x + 42, y + 34), (x + 76, y + 20), (x + 110, y + 34)],
              fill=(150, 150, 150))
    for cx in (54, 66, 78, 90, 100):
        d.rectangle([x + cx, y + 40, x + cx + 4, y + 58], fill=(120, 120, 120))
    d.rectangle([x + 118, y + 10, x + 176, y + 34], fill=(255, 255, 255),
                outline=(120, 120, 120))
    d.text((x + 124, y + 13), "RESIGNATION", font=font(SANS_B, 9),
           fill=(30, 30, 30))
    d.line([x + 124, y + 28, x + 168, y + 28], fill=(120, 120, 120))


def ill_serbia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 232, 242))
    cx, cy, r = x + 96, y + 58, 42
    import math
    for i in range(21):
        a = math.radians(180 + i * 9)
        px = cx + r * math.cos(a)
        py = cy + r * 0.75 * math.sin(a)
        col = (176, 39, 39) if i < 12 else (43, 94, 167)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)
    d.text((x + 8, y + 6), "STUDENTS", font=font(SANS_B, 8), fill=(90, 90, 90))
    d.text((x + 8, y + 16), "140", font=font(SANS_B, 16), fill=(176, 39, 39))
    d.text((x + w - 52, y + 6), "VU\u010cI\u0106", font=font(SANS_B, 8),
           fill=(90, 90, 90))
    d.text((x + w - 52, y + 16), "103", font=font(SANS_B, 16),
           fill=(43, 94, 167))
    d.rectangle([x + 76, y + 48, x + 116, y + 58], fill=(120, 90, 60))


def ill_garment(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 220))
    d.rectangle([x + 10, y + 22, x + 62, y + 56], fill=(150, 150, 150))
    d.rectangle([x + 66, y + 30, x + 100, y + 56], fill=(120, 120, 120))
    d.rectangle([x + 16, y + 12, x + 22, y + 22], fill=(100, 100, 100))
    d.rectangle([x + 70, y + 18, x + 76, y + 30], fill=(100, 100, 100))
    d.rectangle([x + 16, y + 28, x + 26, y + 36], fill=(247, 214, 22))
    d.rectangle([x + 40, y + 28, x + 50, y + 36], fill=(247, 214, 22))
    for i, px in enumerate((112, 124, 136, 148, 160)):
        d.ellipse([x + px, y + 34, x + px + 6, y + 40], fill=(220, 190, 150))
        d.rectangle([x + px - 1, y + 40, x + px + 7, y + 56], fill=(60, 60, 90))
    d.rectangle([x + 100, y + 6, x + 190, y + 30], fill=(255, 255, 255),
                outline=(46, 125, 79))
    d.text((x + 104, y + 8), "TK 30,000 MINIMUM", font=font(SANS_B, 9),
           fill=(30, 30, 30))


def ill_an12(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(216, 226, 234))
    d.polygon([(x, y + h), (x + 50, y + 30), (x + 100, y + h)],
              fill=(140, 150, 160))
    d.polygon([(x + 80, y + h), (x + 140, y + 22), (x + 192, y + h)],
              fill=(160, 168, 176))
    _smoke(d, x + 138, y + 26, 8, (110, 110, 110))
    d.polygon([(x + 78, y + 40), (x + 128, y + 28), (x + 140, y + 34),
               (x + 92, y + 48)], fill=(90, 90, 90))
    d.polygon([(x + 96, y + 34), (x + 112, y + 18), (x + 120, y + 30)],
              fill=(90, 90, 90))
    d.polygon([(x + 128, y + 30), (x + 146, y + 24), (x + 140, y + 34)],
              fill=(90, 90, 90))


def ill_trial(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.rectangle([x + 22, y + 30, x + 98, y + 58], fill=(245, 245, 240),
                outline=(150, 150, 150))
    d.polygon([(x + 18, y + 30), (x + 60, y + 14), (x + 102, y + 30)],
              fill=(180, 180, 180))
    for cx in (30, 46, 62, 78, 90):
        d.rectangle([x + cx, y + 34, x + cx + 4, y + 58], fill=(140, 140, 140))
    d.rectangle([x + 8, y + 8, x + 26, y + 22], fill=(0, 122, 61))
    d.rectangle([x + 8, y + 8, x + 26, y + 13], fill=(0, 122, 61))
    d.rectangle([x + 8, y + 13, x + 26, y + 17], fill=(0, 0, 0))
    d.rectangle([x + 8, y + 17, x + 26, y + 22], fill=(247, 214, 22))
    d.rectangle([x + 118, y + 34, x + 168, y + 40], fill=(120, 80, 40))
    d.rectangle([x + 140, y + 20, x + 148, y + 40], fill=(120, 80, 40))
    d.rectangle([x + 118, y + 40, x + 168, y + 46], fill=(90, 60, 30))
    pill(d, x + w - 64, y + 6, 58, 15, (176, 39, 39), "5 CHARGES", 9)


ILLUSTRATIONS = {
    "bridge": ill_bridge, "gulf": ill_gulf, "quad": ill_quad,
    "ebola": ill_ebola, "cop31": ill_cop31, "measles": ill_measles,
    "nvidia": ill_nvidia, "gaza": ill_gaza, "mongolia": ill_mongolia,
    "serbia": ill_serbia, "garment": ill_garment, "an12": ill_an12,
    "trial": ill_trial,
}


# ------------------------------------------------------------- layout
def draw_header(d):
    d.text((16, 10), "THE WORLD IN ONE PICTURE", font=font(SANS_B, 13),
           fill=RED)
    right = "43 STORIES · 6 CONTINENTS · TUESDAY 17 NOVEMBER 2026"
    d.text((1008, 11), right, font=font(SANS_B, 12), fill=INK, anchor="ra")
    f = fit(d, "Tuesday 17 November 2026", SERIF_B, 992, 74)
    d.text((16, 24), "Tuesday 17 November 2026", font=f, fill=INK)
    d.rectangle([16, 100, 1008, 102], fill=RULE)
    d.rectangle([16, 105, 1008, 106], fill=RULE)


def draw_numbers_strip(d):
    d.rectangle([16, 108, 1008, 132], fill=(240, 231, 198))
    d.line([16, 108, 1008, 108], fill=(201, 185, 138))
    d.line([16, 132, 1008, 132], fill=(201, 185, 138))
    label = "BY THE NUMBERS"
    lf = font(SANS_B, 12)
    d.text((24, 114), label, font=lf, fill=RED)
    lw = d.textlength(label, font=lf)
    figs = ("11,000+ Ebola cases  ·  $115.8bn Nvidia quarter  ·  "
            "-849 Dow points  ·  1,441 drones downed  ·  "
            "1.4m face acute hunger in Gaza  ·  19 killed in An-12 crash")
    ff = fit(d, figs, SANS, 1008 - 8 - (24 + lw + 12), 12)
    d.text((24 + lw + 12, 114), figs, font=ff, fill=INK)


def draw_kicker(d, x, y, num, region, color, dia):
    d.ellipse([x, y, x + dia, y + dia], fill=color)
    nf = font(SANS_B, 11 if dia >= 17 else 9)
    d.text((x + dia / 2, y + dia / 2 - 1), str(num), font=nf,
           fill=(255, 255, 255), anchor="mm")
    d.text((x + dia + 6, y + (1 if dia >= 17 else 0)), region,
           font=font(SANS_B, 12 if dia >= 17 else 11), fill=color)


def draw_top3(d):
    y0 = 138
    for i, s in enumerate(TOP3):
        x = 16 + i * (324 + 10)
        ILLUSTRATIONS[s["ill"]](d, x, y0, 324, 84)
        if s["strip"]:
            _strip(d, x, y0 + 68, 324, 16, s["strip_color"], s["strip"])
        draw_kicker(d, x, y0 + 89, s["num"], s["region"], s["color"], 17)
        hf = font(SERIF_B, 20)
        lines = wrap(d, s["headline"], hf, 324, max_lines=2)
        yy = y0 + 110
        for ln in lines:
            d.text((x, yy), ln, font=hf, fill=INK)
            yy += 23
        df = font(SANS, 12)
        dlines = wrap(d, s["deck"], df, 324, max_lines=2)
        yy = y0 + 158
        for ln in dlines:
            d.text((x, yy), ln, font=df, fill=(50, 50, 50))
            yy += 15
    d.rectangle([16, 330, 1008, 331], fill=RULE)


def draw_grid(d):
    for row in range(2):
        y0 = 336 + row * 174
        for col in range(5):
            s = GRID[row * 5 + col]
            x = 16 + col * (192 + 8)
            ILLUSTRATIONS[s["ill"]](d, x, y0, 192, 72)
            _strip(d, x, y0 + 59, 192, 13, s["strip_color"], s["strip"])
            draw_kicker(d, x, y0 + 77, s["num"], s["region"], s["color"], 13)
            hf = font(SERIF_B, 15)
            lines = wrap(d, s["headline"], hf, 192, max_lines=2)
            yy = y0 + 94
            for ln in lines:
                d.text((x, yy), ln, font=hf, fill=INK)
                yy += 18
            df = font(SANS, 10)
            dlines = wrap(d, s["deck"], df, 192, max_lines=2)
            yy = y0 + 132
            for ln in dlines:
                d.text((x, yy), ln, font=df, fill=(50, 50, 50))
                yy += 13
    d.rectangle([16, 684, 1008, 685], fill=RULE)


def _project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 170.0) / 360.0 * w
    py = y0 + (78.0 - lat) / 136.0 * h
    return (px, py)


def draw_map(d):
    x0, y0, w, h = 16, 710, 300, 232
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(211, 230, 239))
    for poly in CONTINENTS:
        pts = [_project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        d.polygon(pts, fill=(233, 220, 192), outline=(201, 185, 138))
    for n in sorted(DOTS):
        lon, lat, col = DOTS[n]
        px, py = _project(lon, lat, x0, y0, w, h)
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=col)
    for n in sorted(PINS):
        lon, lat, col = PINS[n]
        px, py = _project(lon, lat, x0, y0, w, h)
        d.ellipse([px - 5.5, py - 5.5, px + 5.5, py + 5.5], fill=col,
                  outline=(255, 255, 255))
        d.text((px, py - 1), str(n), font=font(SANS_B, 8),
               fill=(255, 255, 255), anchor="mm")
    d.text((16, 690), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=RED)
    legend = [("Americas", REDK), ("Europe", BLUE), ("Middle East", ORANGE),
              ("Asia", PURPLE), ("Africa", GREEN)]
    legend2 = [("Oceania", TEAL), ("Global & space", GREY)]
    ly = 946
    lx = 16
    lf = font(SANS, 9)
    for name, col in legend:
        d.ellipse([lx, ly + 2, lx + 6, ly + 8], fill=col)
        d.text((lx + 9, ly), name, font=lf, fill=INK)
        lx += 9 + d.textlength(name, font=lf) + 10
    lx = 16
    ly = 959
    for name, col in legend2:
        d.ellipse([lx, ly + 2, lx + 6, ly + 8], fill=col)
        d.text((lx + 9, ly), name, font=lf, fill=INK)
        lx += 9 + d.textlength(name, font=lf) + 10
    d.text((lx + 6, ly), "Pins 1\u201313 · dots 14\u201343", font=lf,
           fill=GREY_TXT)


def draw_list(d):
    d.text((330, 690), "ALSO ON TUESDAY 17 NOVEMBER", font=font(SANS_B, 13),
           fill=RED)
    for idx, (num, place, text, col) in enumerate(ALSO):
        ci = idx // 15
        ri = idx % 15
        x = 330 if ci == 0 else 676
        y = 710 + ri * 18
        d.ellipse([x, y + 1, x + 13, y + 14], fill=col)
        d.text((x + 6.5, y + 7), str(num), font=font(SANS_B, 8),
               fill=(255, 255, 255), anchor="mm")
        tx = x + 18
        maxw = (664 if ci == 0 else 1008) - tx
        size = 10
        while size >= 9:
            bf = font(SANS_B, size)
            rf = font(SANS, size)
            tw = (d.textlength(place + ": ", font=bf)
                  + d.textlength(text, font=rf))
            if tw <= maxw:
                break
            size -= 1
        d.text((tx, y + 1), place + ": ", font=bf, fill=INK)
        pw = d.textlength(place + ": ", font=bf)
        d.text((tx + pw, y + 1), text, font=rf, fill=(50, 50, 50))


def draw_footer(d):
    d.rectangle([16, 984, 1008, 985], fill=RULE)
    f = font(SANS, 10)
    d.text((16, 990),
           "Every story here happened or was first reported on Tuesday "
           "17 November 2026. Contested claims are marked as claims.",
           font=f, fill=GREY_TXT)
    d.text((1008, 990),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. "
           "Original drawings.", font=f, fill=GREY_TXT, anchor="ra")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_numbers_strip(d)
    draw_top3(d)
    draw_grid(d)
    draw_map(d)
    draw_list(d)
    draw_footer(d)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

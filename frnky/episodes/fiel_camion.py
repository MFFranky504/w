"""«Mi bro, el más fiel del mundo… espera SU camión» — 22 s, zona segura, mezcla -14 LUFS, registro MÉXICO.
Premisa en 1 s: Piero lleva 40 min esperando el 52 y no se sube a ningún otro. Contador visible de camiones que pasaron.
Un solo remate: llega el 52… lleno, y pasa de largo."""
import math
import random

from PIL import ImageDraw

from .. import audio
from ..bg import emote, speed_lines, txt
from ..cast import make_cast
from ..engine import cam_at
from ..sprite import draw_char, CHARS
from .. import scenes3 as S3
from . import bro_juega_bien as B
from .bro_juega_bien import sm

K = 1.0
T = 22.0
SEAM = 20.0
CUTS = []
META = dict(id="fiel-camion", category="fiel", topic="fiel",
            title="Mi bro, el más fiel del mundo, espera SU camión",
            caption_hook="Si tu camión nunca llega, ¿te subes a otro o esperas? A o B",
            caption="Si tu camión nunca llega, ¿te subes a otro o esperas? A o B",
            tags=["#fidelidad", "#pixelart", "#humor", "#amigos", "#shorts"])
_n = 0
while True:
    CAST = make_cast(META["id"] + ("" if _n == 0 else f"-{_n}"), register="MX", names={"bro": "Piero", "a": "Memo"})
    st = [CHARS[CAST[r]["sprite"]]["style"] for r in ("bro", "a")]
    if st[0] in ("spiky", "cap", "curly") and st[0] != st[1]:
        break
    _n += 1
SPRITE = {"piero": CAST["bro"]["sprite"], "memo": CAST["a"]["sprite"]}
VOICES = {"piero": dict(label="PIERO", color=(226, 200, 120), pitch=230), "memo": dict(label="MEMO", color=(130, 190, 210), pitch=300)}
LINES = [
    (1.1, 2.5, "memo", "¡Otro camión! ¡Súbete, wey!"),
    (2.6, 4.0, "piero", "No. Es el 52 o nada."),
    (4.1, 5.4, "memo", "Neta, llevas 40 minutos."),
    (5.5, 6.9, "piero", "Mi ruta no me falla."),
    (10.8, 12.1, "piero", "Mojado, pero fiel."),
    (12.6, 13.9, "memo", "¡Este sí para! ¡Súbete!"),
    (14.0, 14.9, "piero", "Jamás. Soy fiel."),
    (15.3, 16.7, "piero", "¡Es el 52! ¡Ya llegó!"),
    (17.0, 18.5, "piero", "…Mañana sí, mi amor."),
]
HOOK = "ESPERA SU CAMIÓN... Y NO SE SUBE A OTRO"
CTA_MID = "¿Te subes o esperas?\nA: me subo / B: espero"
CTA_FINAL = {"ab": "¿Cuánto esperarías?\nResponde A o B", "etiqueta": "Etiqueta a tu bro que haría esto"}
B.LINES_ACTIVE[0] = LINES
SC, FEET = 2.9, 505
XP, XM = 85, 195
# (inicio, fin, ruta, color, tipo) — tipo: pass | stop | full
BUSES = [(0.5, 1.5, "17", (230, 170, 60), "pass"), (9.0, 10.6, "31", (90, 160, 220), "pass"),
         (12.2, 14.6, "8", (120, 190, 110), "stop"), (15.0, 18.4, "52", (220, 90, 70), "full")]


def bus_x(b, t):
    a, z, _, _, kind = b
    if kind == "pass":
        return -150 + 660 * sm((t - a) / (z - a)) if a <= t <= z else None
    if kind == "stop":
        if t < a or t > z: return None
        if t < a + 0.9: return -150 + 350 * sm((t - a) / 0.9)
        if t < z - 0.9: return 200
        return 200 + 310 * sm((t - (z - 0.9)) / 0.9)
    if t < a or t > z: return None
    if t < a + 1.0: return -150 + 350 * sm((t - a) / 1.0)
    if t < a + 1.8: return 200
    return 200 + 310 * sm((t - a - 1.8) / (z - a - 1.8))


def draw_bus(c, x, route, color, full=False, open_door=False, t=0.0):
    d = ImageDraw.Draw(c)
    w, h, y = 190, 92, 346
    x0 = x - w // 2
    o = (30, 18, 44)
    d.rectangle([x0 - 2, y - h - 2, x0 + w + 2, y + 2], fill=o)
    d.rectangle([x0, y - h, x0 + w, y], fill=color)
    d.rectangle([x0, y - h, x0 + w, y - h + 5], fill=tuple(min(255, int(v * 1.2)) for v in color))
    d.rectangle([x0, y - 14, x0 + w, y], fill=tuple(int(v * 0.7) for v in color))
    for k in range(5):                                                  # ventanas con siluetas de pasajeros
        wx = x0 + 10 + k * 28
        d.rectangle([wx, y - h + 14, wx + 22, y - 38], fill=(150, 200, 236), outline=o)
        if full:
            d.ellipse([wx + 5, y - h + 20, wx + 17, y - h + 32], fill=(60, 50, 80)); d.rectangle([wx + 3, y - h + 32, wx + 19, y - 38], fill=(60, 50, 80))
    d.rectangle([x0 + w - 36, y - h + 14, x0 + w - 6, y - 8], fill=(150, 200, 236), outline=o)          # parabrisas / puerta
    if open_door:
        d.rectangle([x0 + w - 34, y - h + 16, x0 + w - 8, y - 10], fill=(40, 40, 64))
    d.rectangle([x0 + 6, y - h - 12, x0 + 54, y - h], fill=o); txt(d, (x0 + 30, y - h - 6), route, 9, (255, 214, 90), outline=o)   # letrero de ruta
    if full:
        d.rectangle([x0 + 60, y - h - 12, x0 + 130, y - h], fill=(200, 40, 50)); txt(d, (x0 + 95, y - h - 6), "LLENO", 9, (255, 255, 255), outline=(120, 20, 30))
    for wxc in (x0 + 34, x0 + w - 44):
        d.ellipse([wxc - 14, y - 12, wxc + 14, y + 16], fill=o); d.ellipse([wxc - 7, y - 5, wxc + 7, y + 9], fill=(160, 160, 180))
    d.rectangle([x0 + w - 4, y - 22, x0 + w + 4, y - 14], fill=(255, 244, 150))                          # faro


def ch(c, t, key, **kw):
    sp = B.speaking(t)
    expr = kw.get("expr", "neutral")
    if key in sp and int(t * 7) % 2 == 0:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    elif expr in ("neutral", "sad", "shy") and ((t * 24 + kw["x"] * 0.37) % 76) < 3:
        kw["expr"] = "blink"
    x = kw.pop("x"); shake = kw.pop("shake", 0)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 2.6 + x) * 1.5 + math.sin(t * 5 + x) * .6)
    draw_char(c, SPRITE[key], x, FEET, ox=ox, oy=oy, scale=SC, **kw)


def rain(c, t):
    d = ImageDraw.Draw(c)
    rnd = random.Random(int(t * 24))
    for _ in range(70):
        x, y = rnd.randint(0, 360), rnd.randint(0, 640)
        d.line([x, y, x - 3, y + 14], fill=(190, 210, 245))


def passed(t):
    return sum(1 for b in BUSES if bus_x(b, t) is None and t > b[1]) if t < SEAM else 0


def frame(t):
    te = t if t < SEAM else t - T
    c = S3.parada(te)
    tt = t if t < SEAM else 0.0
    for b in BUSES:
        x = bus_x(b, tt)
        if x is not None:
            draw_bus(c, x, b[2], b[3], full=b[4] == "full", open_door=(b[4] == "stop" and 13.1 <= tt < 14.0), t=tt)
    splash = 9.7 <= tt < 10.4
    wet = tt >= 10.0
    p_exp = "sad" if wet and tt < 12.2 else ("shock" if 15.0 <= tt < 17.0 else ("sad" if tt >= 17.0 else "neutral"))
    m_exp = "shock" if (0.5 <= tt < 1.5 or 12.2 <= tt < 14.0) else ("shy" if tt >= 17.0 else "neutral")
    ch(c, te, "memo", x=XM, expr=m_exp, pose="point" if 12.6 <= tt < 13.9 else "down", flip=True, fx=("sweat",) if m_exp == "shock" else ())
    ch(c, te, "piero", x=XP, expr=p_exp, pose="down", look=1 if (tt < 15 and int(tt * 1.5) % 2) else -1,
       fx=("sweat",) if wet and tt < 12.2 else (("tear",) if tt >= 17.0 else ()), shake=2 if splash else 0)
    d = ImageDraw.Draw(c)
    if splash:                                                       # salpicadura de charco
        u = (tt - 9.7) / 0.7
        rnd = random.Random(5)
        for _ in range(16):
            px = XP - 30 + rnd.randint(-40, 40) + rnd.randint(-20, 20) * u
            py = FEET - 20 - 60 * math.sin(math.pi * u) * rnd.random()
            d.ellipse([px, py, px + 8, py + 8], fill=(150, 180, 230), outline=(60, 80, 130))
    if 0.5 < tt < 1.4:
        speed_lines(c, 200, 330, te, int(120 * (1 - (tt - 0.5) / 0.9)))
    if 15.3 < tt < 16.8:
        emote(c, XP, 300, "!", tt - 15.3)
    rain(c, te)
    FY = 345
    keys = [(0, 40, 150, FY), (1.0, 40, 150, FY), (1.1, 36, 135, FY), (4.0, 36, 150, FY), (7.0, 36, 150, FY), (9.0, 36, 140, FY),
            (12.4, 36, 150, FY), (14.9, 36, 150, FY), (15.3, 36, 150, 345), (18.3, 36, 150, 345), (19.5, 40, 150, FY), (T, 40, 150, FY)]
    return c, cam_at(keys, t), (5 if 0.5 <= tt < 1.0 else 0)


def hud(t):
    n = 0 if t >= SEAM else sum(1 for b in BUSES if t >= b[0] + 0.6)
    return [("ESPERA", "40 MIN"), ("CAMIONES", str(n))]


def music(track):
    audio.groove(track, 0, 22.0, 104, "min", layers=("bass", "pad", "arp"), mel="b")
    audio.groove(track, 15.0, 19.5, 104, "maj", layers=("pad", "lead"), mel="b", vol=0.8)
    audio.ambient(track, 0, 22.0, "street", 1.0)


def sfx(track):
    A = audio
    n = int(22 * A.SR)
    A.put(track, 0.0, A._lp(A.rng.uniform(-1, 1, n), 6) * 0.1)                      # lluvia constante
    A.whoosh(track, 0.0, 0.3, 0.2); A.zombie_hit(track, 0.5)                          # camión 17 irrumpe
    for t0, t1, who, _ in LINES:
        A.put(track, t0, A.blip(VOICES[who]["pitch"] * 1.6, 0.3)); A.put(track, t0 + 0.07, A.blip(VOICES[who]["pitch"] * 2.0, 0.3))
    A.sting(track, 7.0)
    A.whoosh(track, 9.0, 0.7, 0.18); A.airhorn(track, 9.3, 0.1)                       # camión 31 + claxon
    A.put(track, 9.7, A.noise(0.35, 0.35, 0.25)); A.boing(track, 10.1)               # splash
    A.whoosh(track, 12.2, 0.6, 0.14); A.step(track, 13.1, 0.12); A.boing(track, 13.3)    # camión 8 frena, abre puerta
    A.whoosh(track, 14.2, 0.6, 0.14)
    A.ding(track, 15.0); A.whoosh(track, 15.0, 0.6, 0.16)                              # llega el 52
    A.trombone(track, 16.9); A.pop(track, 16.8)
    A.riser_short(track, 20.8, 1.2)


EP = dict(T=T, hooks=[(0.0, 2.5, HOOK)], cuts=[], voices=VOICES, punches=[(a, 2.5) for a, _, _, _ in LINES],
          lines=LINES, frame=frame, hud=hud, banner=lambda t: "", music=music, sfx=sfx, meta=META,
          safe=True, mix="pro", cta_mid=(7.0, 9.0, CTA_MID), final_cta=CTA_FINAL["ab"], cta_options=CTA_FINAL,
          flash=lambda: [0.52, 0.56, 0.6])

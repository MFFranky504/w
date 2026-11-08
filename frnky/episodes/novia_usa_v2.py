"""V2 tras la crítica de 7 revisores. Premisa visible en 1 s (contador FAVORES 47 vs ELLA 0), regla visual que escala (ella señala, él carga: torre de bolsas),
Dani no explica (solo señala), diálogos mexicanos naturales, UN giro merecido: las bolsas estaban vacías. Pregunta con dos bandos y CTA de etiquetar."""
import math
import random

from PIL import ImageDraw

from .. import audio
from ..bg import emote, speed_lines
from ..cast import make_cast
from ..engine import cam_at
from ..sprite import draw_char, CHARS
from .. import scenes3 as S3
from . import bro_juega_bien as B
from .bro_juega_bien import sm

T, SEAM = 22.0, 20.0
META = dict(id="novia-usa-v2", category="crush", topic="crush",
            title="¿Qué pasaría si mi bro se diera cuenta de que su novia solo lo usa?",
            caption_hook="Mi bro lleva 47 favores y ella, cero. ¿Tierno o tonto? A o B",
            caption="Mi bro lleva 47 favores y ella, cero. ¿Tierno o tonto? A o B",
            tags=["#pareja", "#pixelart", "#humor", "#amigos", "#shorts"])
_n = 0
while True:
    CAST = make_cast(META["id"] + ("" if _n == 0 else f"-{_n}"), register="MX", names={"bro": "Beto", "a": "Lupita", "b": "Dani"})
    st = [CHARS[CAST[r]["sprite"]]["style"] for r in ("bro", "a", "b")]
    if st[0] in ("spiky", "cap", "curly") and st[1] in ("pony", "bun") and st[2] != st[0]:
        break
    _n += 1
SPRITE = {"beto": CAST["bro"]["sprite"], "lupita": CAST["a"]["sprite"], "dani": CAST["b"]["sprite"]}
VOICES = {"beto": dict(label="BETO", color=(226, 200, 120), pitch=230), "lupita": dict(label="LUPITA", color=(255, 150, 190), pitch=340),
          "dani": dict(label="DANI", color=(130, 190, 210), pitch=270)}
LINES = [
    (1.1, 2.5, "lupita", "Ándale, ¿me invitas unos tacos?"),
    (2.6, 3.9, "beto", "Va, yo invito."),
    (4.0, 5.4, "lupita", "Cárgame esto, ¿sí?"),
    (5.5, 6.9, "beto", "Ya, ya las cargo."),
    (9.2, 10.6, "dani", "Bro, te trae de chalán."),
    (10.7, 12.0, "beto", "No manches, ¿en serio?"),
    (13.8, 15.0, "beto", "¡Ya no! ¡Se acabó!"),
    (15.4, 16.7, "lupita", "Eran puro aire, amor."),
    (16.8, 18.2, "beto", "¿Y mi plata, entonces?"),
    (18.3, 19.4, "lupita", "Esa sí fue real."),
]
HOOK = "MI BRO LLEVA 47 FAVORES... ELLA, CERO"
CTA_MID = "¿Beto: tierno o tonto?\nA: tierno / B: tonto"
CTA_FINAL = {"ab": "Etiqueta a tu amigo\nque siempre paga todo", "etiqueta": "Etiqueta a tu bro que haría esto"}
B.LINES_ACTIVE[0] = LINES
SC, FEET = 3.0, 500
XB, XL, XD = 80, 190, 295
# cada bolsa/favor: (tiempo, +1). Torre: 3 al inicio y sube hasta 8 antes del «¡Ya no!»; a 15.0 revienta (aire).
GROW = [2.6, 4.0, 10.0, 10.5, 11.0, 11.5, 12.0, 12.6, 13.1]


def tower(t):
    if t >= SEAM or t < 2.6:
        return 3
    if t >= 15.0:
        return 0
    return min(8, 3 + sum(1 for x in GROW if t >= x))


def favors(t):
    if t >= SEAM or t < 2.6:
        return 47
    if t >= 15.0:
        return 47 + 9
    return 47 + sum(1 for x in GROW if t >= x)


def draw_tower(c, x, t, n, sway=1.0):
    d = ImageDraw.Draw(c)
    cols = [(230, 90, 120), (90, 170, 230), (250, 200, 70), (110, 200, 130), (170, 110, 220), (240, 150, 70), (90, 200, 200), (230, 120, 200)]
    for i in range(n):
        bx = x - 24 + int(math.sin(t * 5 + i * 0.7) * (2 + i * 1.2) * sway) + (6 if i % 2 else -4)
        by = FEET - 118 - i * 30
        d.rectangle([bx - 1, by - 1, bx + 49, by + 29], fill=(30, 18, 44)); d.rectangle([bx, by, bx + 48, by + 28], fill=cols[i % 8])
        d.rectangle([bx, by, bx + 6, by + 28], fill=tuple(min(255, int(v * 1.2)) for v in cols[i % 8])); d.rectangle([bx + 18, by + 8, bx + 30, by + 20], fill=(250, 250, 250))
        d.line([bx + 10, by - 8, bx + 18, by], fill=(30, 18, 44), width=2); d.line([bx + 38, by - 8, bx + 30, by], fill=(30, 18, 44), width=2)


def ch(c, t, key, **kw):
    sp = B.speaking(t)
    expr = kw.get("expr", "neutral")
    if key in sp and int(t * 7) % 2 == 0:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    elif expr in ("neutral", "sad", "shy") and ((t * 24 + kw["x"] * 0.37) % 76) < 3:
        kw["expr"] = "blink"
    x = kw.pop("x"); shake = kw.pop("shake", 0); hop = kw.pop("hop", 0)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 2.6 + x) * 1.5 + math.sin(t * 5 + x) * .6) - (round(abs(math.sin(t * 9 + x)) * hop) if hop else 0)
    draw_char(c, SPRITE[key], x, FEET, ox=ox, oy=oy, scale=SC, **kw)


def dani_x(t):
    if t < 8.4 or t >= SEAM - 0.5:
        return 450
    if t < 9.2:
        return 450 - 155 * sm((t - 8.4) / 0.8)
    return XD


def frame(t):
    te = t if t < SEAM else t - T
    tt = t if t < SEAM else 0.0
    c = S3.taqueria(te)
    d = ImageDraw.Draw(c)
    n = tower(tt)
    points = 1.1 <= tt < 2.5 or 4.0 <= tt < 5.4 or 10.0 <= tt < 13.4
    b_exp = "happy" if tt < 6.9 else ("shock" if tt < 12.0 else ("sad" if tt < 13.8 else ("angry" if tt < 15.0 else ("shock" if tt < 17.0 else "sad"))))
    l_exp = "happy" if tt < 15.0 else ("shy" if tt < 16.7 else "happy")
    ch(c, te, "lupita", x=XL, expr=l_exp, pose="point" if points else ("cheer" if 15.4 <= tt < 16.7 else "down"), flip=True)
    ch(c, te, "beto", x=XB, expr=b_exp, pose="down", look=1, fx=("sweat",) if 9 <= tt < 15 else (), shake=(2 if 10.0 <= tt < 13.6 else 0))
    if n:
        draw_tower(c, XB, tt, n, 1.0 if tt < 13.8 else 2.0)
    dx = dani_x(tt)
    if dx < 420:
        ch(c, te, "dani", x=dx, expr="neutral" if tt < 9.2 else "shy", pose="point" if 9.2 <= tt < 10.7 else "down", flip=True)
    if 11.4 <= tt < 13.4:                                          # billetera exprimida: monedas vuelan a la mano de Lupita
        rn = random.Random(9)
        for k in range(10):
            u = ((tt - 11.4) * 1.1 + k * 0.1) % 1.0
            px = XB + 20 + (XL - XB - 20) * u; py = FEET - 150 - 70 * math.sin(math.pi * u)
            d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(250, 214, 80), outline=(30, 18, 44), width=2)
    if 15.0 <= tt < 15.6:                                          # las bolsas revientan: puff de aire
        u = (tt - 15.0) / 0.6
        for k in range(10):
            a = k * 0.63
            px = XB + math.cos(a) * 120 * u; py = FEET - 200 + math.sin(a) * 90 * u
            r = 14 + 22 * (1 - u)
            d.ellipse([px - r, py - r, px + r, py + r], fill=(245, 245, 250), outline=(180, 190, 220))
    if tt >= 15.4:                                                 # bolsas vacías aplastadas en el piso
        for i in range(5):
            bx = XB - 80 + i * 30; by = FEET - 14 + (i % 2) * 6
            d.polygon([(bx, by), (bx + 38, by + 4), (bx + 34, by + 14), (bx - 2, by + 10)], fill=(240, 190, 120), outline=(30, 18, 44))
    if 0.3 < tt < 1.3:
        emote(c, XB, 260, "!", tt - 0.3)
    if 10.7 < tt < 12.2:
        emote(c, XB, 260, "?", tt - 10.7)
    if 0.12 < tt < 0.9:
        speed_lines(c, XL, 330, te, int(100 * (1 - (tt - 0.12) / 0.78)))
    FY = 345
    keys = [(0, 40, 150, FY), (1.0, 40, 150, FY), (1.1, 36, 185, FY), (2.5, 36, 185, FY), (2.6, 36, 100, FY), (4.0, 36, 185, FY),
            (5.5, 36, 100, FY), (7.0, 40, 150, FY), (9.0, 38, 190, FY), (10.7, 36, 100, FY), (12.0, 36, 150, FY), (13.7, 36, 150, FY),
            (13.8, 34, 90, FY), (15.0, 36, 120, FY), (15.4, 36, 185, FY), (16.8, 36, 100, FY), (18.3, 36, 185, FY), (19.5, 40, 150, FY), (T, 40, 150, FY)]
    return c, cam_at(keys, t), (4 if (0.12 <= tt < 0.6 or 15.0 <= tt < 15.3) else 0)


def hud(t):
    return [("FAVORES", str(favors(t))), ("ELLA", "0")]


def music(track):
    audio.groove(track, 0, 22.0, 108, "maj", layers=("bass", "pad", "arp"), mel="b")
    audio.groove(track, 9.0, 13.8, 140, "min", layers=("bass", "pad", "arp", "drums"), vol=0.9)        # el montaje acelera
    audio.groove(track, 15.0, 19.5, 108, "maj", layers=("pad", "lead"), mel="b", vol=0.8)
    audio.ambient(track, 0, 22.0, "street", 1.0)


def sfx(track):
    A = audio
    A.whoosh(track, 0.0, 0.3, 0.2); A.hit(track, 0.5)
    for t0, t1, who, _ in LINES:
        A.put(track, t0, A.blip(VOICES[who]["pitch"] * 1.6, 0.3)); A.put(track, t0 + 0.07, A.blip(VOICES[who]["pitch"] * 2.0, 0.3))
    for x in GROW:
        A.coin(track, x, 0.12); A.click(track, x)                       # ding por cada favor/bolsa
    A.sting(track, 7.0)
    for k in range(5):
        A.step(track, 8.4 + 0.16 * k, 0.1)
    A.boing(track, 9.2); A.riser_short(track, 10.0, 3.3, 0.14)           # tensión del montaje
    for k in range(10):
        A.coin(track, 11.4 + 0.2 * k, 0.07)                              # monedas volando
    A.hit(track, 13.8); A.boing(track, 14.0)                             # «¡Ya no!»
    A.hit(track, 15.0); A.put(track, 15.0, A.noise(0.35, 0.3, 0.25)); A.ding(track, 15.1)    # bolsas revientan: aire
    A.laugh(track, 15.7); A.trombone(track, 18.3)
    A.riser_short(track, 20.8, 1.2)


EP = dict(T=T, hooks=[(0.0, 2.5, HOOK)], cuts=[], voices=VOICES, punches=[(a, 2.5) for a, _, _, _ in LINES],
          lines=LINES, frame=frame, hud=hud, banner=lambda t: "", music=music, sfx=sfx, meta=META,
          safe=True, mix="pro", cta_mid=(7.0, 9.0, CTA_MID), final_cta=CTA_FINAL["ab"], cta_options=CTA_FINAL,
          flash=lambda: [0.12, 0.16, 0.2])

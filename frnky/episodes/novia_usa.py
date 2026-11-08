"""«¿Qué pasaría si mi bro se diera cuenta de que su novia solo lo usa?» — 22 s, zona segura, mezcla -14 LUFS, México.
Premisa visible en 1 s: Beto carga bolsas y paga; HUD cuenta FAVORES y su CARTERA. Un remate: «¿Y si yo pago un taco?» «…Trato.»
Humor sano: ella es simpática y exagerada, nadie sale herido."""
import math

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
META = dict(id="novia-usa", category="crush", topic="crush",
            title="¿Qué pasaría si mi bro se diera cuenta de que su novia solo lo usa?",
            caption_hook="Si tu pareja solo te usa, ¿te das cuenta o te haces el ciego? A o B",
            caption="Si tu pareja solo te usa, ¿te das cuenta o te haces el ciego? A o B",
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
    (1.1, 2.5, "lupita", "Amor, ¿me pagas los tacos?"),
    (2.6, 3.9, "beto", "Claro, mi vida."),
    (4.0, 5.4, "lupita", "Y llévame las bolsas."),
    (5.5, 6.9, "beto", "Aquí están, mi reina."),
    (9.2, 10.7, "dani", "Wey, ¡tu novia solo te usa!"),
    (10.8, 12.3, "beto", "¿Neta? ¿Solo me usa?"),
    (12.6, 14.2, "lupita", "Amor, ¿me das tu cargador?"),
    (15.3, 16.6, "beto", "Neta, ya me di cuenta."),
    (16.7, 18.2, "lupita", "¿Y si yo pago un taco?"),
    (18.3, 19.4, "beto", "…Trato."),
]
HOOK = "SU NOVIA SOLO LO USA... Y ÉL SE DIO CUENTA"
CTA_MID = "¿Ya se dio cuenta?\nA: sí / B: todavía no"
CTA_FINAL = {"ab": "¿Tú pagarías el taco?\nResponde A o B", "etiqueta": "Etiqueta a tu bro que haría esto"}
B.LINES_ACTIVE[0] = LINES
SC, FEET = 3.0, 500
XB, XL, XD = 80, 185, 290
FAVOR_T = [2.6, 4.0, 5.5, 10.0, 10.25, 10.5, 10.75, 11.0, 11.25]      # cada favor sube el contador (gag 1 = ráfaga)


def favors(t):
    if t >= SEAM or t < 2.6:
        return 3
    if t >= 15.0:
        return 0 if t < 18.3 else 0
    return 3 + sum(1 for x in FAVOR_T if t >= x and x != 2.6) + (1 if t >= 2.6 else 0) - 0


def bags_n(t):
    return 0 if 15.0 <= t < SEAM else min(6, favors(t))


def draw_bags(c, x, t, n):
    d = ImageDraw.Draw(c)
    cols = [(230, 90, 120), (90, 170, 230), (250, 200, 70), (110, 200, 130), (170, 110, 220), (240, 150, 70)]
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        bx = x + side * (46 + 14 * (i // 2)) - 11
        by = FEET - 112 + 10 * (i // 2) + int(math.sin(t * 4 + i) * 2)
        d.line([bx + 5, by - 14, bx + 11, by], fill=(30, 18, 44), width=2); d.line([bx + 17, by - 14, bx + 11, by], fill=(30, 18, 44), width=2)
        d.rectangle([bx - 1, by - 1, bx + 23, by + 33], fill=(30, 18, 44)); d.rectangle([bx, by, bx + 22, by + 32], fill=cols[i % 6])
        d.rectangle([bx, by, bx + 4, by + 32], fill=tuple(min(255, int(v * 1.2)) for v in cols[i % 6]))


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
        return 450 if t < 8.4 else 450
    if t < 9.2:
        return 450 - 160 * sm((t - 8.4) / 0.8)
    return XD


def frame(t):
    te = t if t < SEAM else t - T
    tt = t if t < SEAM else 0.0
    c = S3.taqueria(te)
    d = ImageDraw.Draw(c)
    n = bags_n(tt)
    drop = 15.0 <= tt < 15.4
    b_exp = "shy" if tt < 9.2 else ("shock" if tt < 12.5 else ("shy" if tt < 15 else ("angry" if tt < 17 else "happy" if tt >= 18.3 else "shy")))
    l_exp = "happy" if (tt < 12.6 or tt >= 16.7) else ("shock" if tt >= 15.0 else "happy")
    ch(c, te, "lupita", x=XL, expr=l_exp, pose="point" if (1.1 <= tt < 2.5 or 4.0 <= tt < 5.4) else ("phone" if 12.6 <= tt < 14.2 else "down"), flip=True)
    ch(c, te, "beto", x=XB, expr=b_exp, pose="down", look=1, fx=("sweat",) if tt < 15 else (), shake=2 if 10.8 <= tt < 12.3 else 0)
    draw_bags(c, XB, tt, n)
    dx = dani_x(tt)
    if dx < 420:
        ch(c, te, "dani", x=dx, expr="shock" if 9.2 <= tt < 10.8 else "neutral", pose="point" if 9.2 <= tt < 10.7 else "down", flip=True)
    if 15.0 <= tt < 17.5:                                          # las bolsas caen
        u = min(1.0, (tt - 15.0) / 0.4)
        for i in range(5):
            bx = XB - 80 + i * 36; by = FEET - 112 + 110 * u
            cc = [(230, 90, 120), (90, 170, 230), (250, 200, 70), (110, 200, 130), (170, 110, 220)][i]
            d.rectangle([bx - 1, by - 1, bx + 23, by + 33], fill=(30, 18, 44)); d.rectangle([bx, by, bx + 22, by + 32], fill=cc)
    if 16.7 <= tt < 18.4:                                          # moneda para el taco
        cy = 330 + 8 * math.sin(tt * 6)
        d.ellipse([XL - 14, cy - 14, XL + 14, cy + 14], fill=(250, 214, 80), outline=(30, 18, 44), width=2); d.rectangle([XL - 2, cy - 7, XL + 2, cy + 7], fill=(200, 150, 40))
    if 0.3 < tt < 1.3:
        emote(c, XB, 300, "!", tt - 0.3)
    if 10.8 < tt < 12.2:
        emote(c, XB, 300, "?", tt - 10.8)
    if 0.12 < tt < 0.9:
        speed_lines(c, XL, 330, te, int(100 * (1 - (tt - 0.12) / 0.78)))
    FY = 345
    keys = [(0, 40, 150, FY), (1.0, 40, 150, FY), (1.1, 36, 185, FY), (2.5, 36, 185, FY), (2.6, 36, 100, FY), (4.0, 36, 185, FY),
            (5.5, 36, 100, FY), (7.0, 40, 150, FY), (9.0, 38, 190, FY), (10.8, 36, 100, FY), (12.5, 36, 185, FY), (15.0, 36, 130, FY),
            (16.7, 36, 150, FY), (18.4, 36, 110, FY), (19.5, 40, 150, FY), (T, 40, 150, FY)]
    return c, cam_at(keys, t), (4 if 0.12 <= tt < 0.6 else 0)


def hud(t):
    f = favors(t)
    return [("FAVORES", str(f)), ("CARTERA", f"${max(0, 500 - 50 * f)}")]


def music(track):
    audio.groove(track, 0, 22.0, 108, "maj", layers=("bass", "pad", "arp"), mel="b")
    audio.groove(track, 15.0, 19.5, 108, "min", layers=("pad", "lead"), mel="b", vol=0.8)
    audio.ambient(track, 0, 22.0, "street", 1.0)


def sfx(track):
    A = audio
    A.whoosh(track, 0.0, 0.3, 0.2); A.zombie_hit(track, 0.5) if False else A.hit(track, 0.5)
    for t0, t1, who, _ in LINES:
        A.put(track, t0, A.blip(VOICES[who]["pitch"] * 1.6, 0.3)); A.put(track, t0 + 0.07, A.blip(VOICES[who]["pitch"] * 2.0, 0.3))
    for x in (2.6, 4.0, 5.5):
        A.coin(track, x, 0.12)
    A.sting(track, 7.0)
    for k in range(5):
        A.step(track, 8.4 + 0.16 * k, 0.1)                       # Dani entra
    for x in FAVOR_T[3:]:
        A.coin(track, x, 0.12); A.click(track, x)                # ráfaga de favores
    A.boing(track, 13.3)
    A.ding(track, 15.0); A.boing(track, 15.0)
    A.pop(track, 16.8); A.laugh(track, 19.0)
    A.riser_short(track, 20.8, 1.2)


EP = dict(T=T, hooks=[(0.0, 2.5, HOOK)], cuts=[], voices=VOICES, punches=[(a, 2.5) for a, _, _, _ in LINES],
          lines=LINES, frame=frame, hud=hud, banner=lambda t: "", music=music, sfx=sfx, meta=META,
          safe=True, mix="pro", cta_mid=(7.0, 9.0, CTA_MID), final_cta=CTA_FINAL["ab"], cta_options=CTA_FINAL,
          flash=lambda: [0.12, 0.16, 0.2])

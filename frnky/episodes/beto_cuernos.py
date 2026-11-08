"""«Mi bro ama a su novia… y ella lo usa y le pone los cuernos» — versión larga (34.5 s), 4 actos y bucle que se repite.
Acto 1: Beto no ve nada. Acto 2: descubre la verdad. Acto 3: la confronta y terminan. Acto 4: llega una mejor… y todo se repite.
Más larga que el estándar de 22 s: es una prueba de duración (una sola variable frente a los videos cortos)."""
import math
import random

from PIL import Image, ImageDraw

from .. import audio
from ..bg import emote, speed_lines, sparkles, txt
from ..cast import make_cast
from ..engine import cam_at
from ..sprite import draw_char, CHARS
from .. import scenes3 as S3
from . import bro_juega_bien as B
from .bro_juega_bien import sm

T = 34.5
SEAM = 32.0
META = dict(id="beto-cuernos", category="crush", topic="crush",
            title="Mi bro ama a su novia… hasta que se da cuenta",
            caption_hook="Mi bro no veía nada… hasta que lo vio. ¿Tú lo hubieras visto antes? A o B",
            caption="Mi bro no veía nada… hasta que lo vio. ¿Tú lo hubieras visto antes? A o B",
            tags=["#pareja", "#pixelart", "#humor", "#amigos", "#shorts"])
def _distinct(cs):
    """Los 5 personajes se distinguen a simple vista: pelo y camiseta lejos entre sí."""
    L = [(CHARS[c["sprite"]]["hair"], CHARS[c["sprite"]]["coat"]) for c in cs]
    far = lambda a, b: sum(abs(x - y) for x, y in zip(a, b)) >= 110
    return all(far(L[i][0], L[j][0]) or far(L[i][1], L[j][1]) for i in range(len(L)) for j in range(i + 1, len(L))) and \
        all(far(L[i][1], L[j][1]) for i in range(len(L)) for j in range(i + 1, len(L)) if i < 3 and j < 3)


_n = 0
while True:
    K1 = make_cast(META["id"] + ("" if _n == 0 else f"-{_n}"), register="MX", names={"bro": "Beto", "a": "Lupita", "b": "Dani"})
    K2 = make_cast(META["id"] + f"-b{_n}", register="MX", names={"bro": "Chuy", "a": "Vale"})
    s1 = [CHARS[K1[r]["sprite"]]["style"] for r in ("bro", "a", "b")]
    s2 = [CHARS[K2[r]["sprite"]]["style"] for r in ("bro", "a")]
    if (s1[0] in ("spiky", "cap", "curly") and s1[1] in ("pony", "bun") and s2[1] in ("pony", "bun") and s1[2] != s1[0]
            and CHARS[K1["a"]["sprite"]]["hair"] != CHARS[K2["a"]["sprite"]]["hair"] and s2[0] != s1[0]
            and _distinct([K1["bro"], K1["a"], K1["b"], K2["bro"], K2["a"]])):
        break
    _n += 1
SPRITE = {"beto": K1["bro"]["sprite"], "lupita": K1["a"]["sprite"], "dani": K1["b"]["sprite"], "chuy": K2["bro"]["sprite"], "vale": K2["a"]["sprite"]}
VOICES = {"beto": dict(label="BETO", color=(226, 200, 120), pitch=230), "lupita": dict(label="LUPITA", color=(255, 150, 190), pitch=340),
          "dani": dict(label="DANI", color=(130, 190, 210), pitch=270), "chuy": dict(label="CHUY", color=(222, 140, 130), pitch=180),
          "vale": dict(label="VALE", color=(170, 226, 150), pitch=320)}
LINES = [
    (1.1, 2.5, "lupita", "Ándale, ¿me invitas unos tacos?"),
    (2.6, 3.9, "beto", "Va, yo invito, mi amor."),
    (4.0, 5.4, "dani", "Bro, te trae de chalán."),
    (5.5, 6.9, "beto", "No, wey, ella me ama."),
    (11.6, 13.0, "beto", "Le caigo con flores. Sorpresa."),
    (13.2, 14.5, "lupita", "Tranquilo, Beto paga todo."),
    (14.6, 15.8, "chuy", "¿Y no se da cuenta?"),
    (15.9, 17.1, "lupita", "Jamás. Es un ángel."),
    (17.3, 18.8, "beto", "¿Lupita? ¿Qué es esto?"),
    (19.8, 21.1, "beto", "¡Me pusiste los cuernos!"),
    (21.2, 22.4, "lupita", "¡Amor, puedo explicarlo!"),
    (22.5, 23.7, "beto", "¿Y mi plata, también?"),
    (23.8, 24.9, "lupita", "…Era para los tacos."),
    (25.0, 26.4, "beto", "Terminamos. Dame mi tarjeta."),
    (27.0, 28.3, "vale", "Hola, Beto. Yo invito."),
    (28.4, 29.6, "beto", "¿Neta? ¿Tú pagas?"),
    (29.7, 30.9, "vale", "Claro. ¿Me cargas esto?"),
    (31.0, 32.0, "beto", "…Va, wey."),
]
HOOK = "BETO ESTÁ ENAMORADO... Y NO VE NADA"
CTA_MID = "¿Tú sí lo viste?\nA: sí / B: no"
CTA_FINAL = {"ab": "Etiqueta a tu amigo\nque merece algo mejor", "etiqueta": "Etiqueta a tu bro que haría esto"}
B.LINES_ACTIVE[0] = LINES
SC, FEET = 3.0, 500
XB, XL, XD = 80, 190, 295
CARD = (90, 150, 240)


def tower(t):
    if t < 2.6: return 3
    if t < 4.0: return 4
    if t < 11.0: return 5
    if t >= 29.7 and t < SEAM: return 3
    return 0


def hud(t):
    amor = "100%" if (t < 17.4 or t >= 26.9) else "0%"
    if t >= SEAM or t < 2.6: cart = "$500"
    elif t < 12.0: cart = "$400"
    elif t < 14.0: cart = "$200"
    else: cart = "$20"
    return [("AMOR", amor), ("CARTERA", cart)]


def ch(c, t, key, **kw):
    sp = B.speaking(t)
    expr = kw.get("expr", "neutral")
    if key in sp and int(t * 7) % 2 == 0:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    elif expr in ("neutral", "sad", "shy") and ((t * 24 + kw["x"] * 0.37) % 76) < 3:
        kw["expr"] = "blink"
    x = kw.pop("x"); shake = kw.pop("shake", 0); hop = kw.pop("hop", 0); walk = kw.pop("walk", 0)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 2.6 + x) * 1.5 + math.sin(t * 5 + x) * .6) - (round(abs(math.sin(t * 9 + x)) * hop) if hop else 0)
    draw_char(c, SPRITE[key], x, FEET, ox=ox, oy=oy, scale=SC, walk=walk, **kw)


def draw_tower(c, x, t, n):
    d = ImageDraw.Draw(c)
    cols = [(230, 90, 120), (90, 170, 230), (250, 200, 70), (110, 200, 130), (170, 110, 220)]
    for i in range(n):
        bx = x - 24 + int(math.sin(t * 5 + i * 0.7) * (2 + i)) + (6 if i % 2 else -4)
        by = FEET - 118 - i * 30
        d.rectangle([bx - 1, by - 1, bx + 49, by + 29], fill=(30, 18, 44)); d.rectangle([bx, by, bx + 48, by + 28], fill=cols[i % 5])
        d.rectangle([bx, by, bx + 6, by + 28], fill=tuple(min(255, int(v * 1.2)) for v in cols[i % 5])); d.rectangle([bx + 18, by + 8, bx + 30, by + 20], fill=(250, 250, 250))


def heart(d, x, y, r, col=(240, 70, 110)):
    d.ellipse([x - r, y - r, x, y], fill=col); d.ellipse([x, y - r, x + r, y], fill=col); d.polygon([(x - r, y - r / 2), (x + r, y - r / 2), (x, y + r)], fill=col)


def card(d, x, y, w=54):
    d.rectangle([x - 1, y - 1, x + w + 1, y + 35], fill=(30, 18, 44)); d.rectangle([x, y, x + w, y + 34], fill=CARD)
    d.rectangle([x, y + 8, x + w, y + 14], fill=(30, 40, 90)); d.rectangle([x + 4, y + 22, x + 24, y + 26], fill=(250, 250, 250))


def dani_x(t):
    if t < 3.0 or t >= 9.0: return 450
    if t < 3.8: return 450 - 155 * sm((t - 3.0) / 0.8)
    if t < 8.2: return XD
    return XD + 155 * sm((t - 8.2) / 0.8)


def state(tt, te):
    """Un cuadro en el instante tt (0..32). te = fase de animación."""
    d = None
    if tt < 11.0 or tt >= 26.6:
        c = S3.taqueria(te)
    elif tt < 19.4:
        c = S3.parada(te)
    else:
        c = S3.azotea(te)
    d = ImageDraw.Draw(c)
    FY = 345
    shake = 0
    if tt < 11.0:                                                     # ACTO 1: Beto no ve nada
        n = tower(tt)
        clue = 7.0 <= tt < 9.0
        ch(c, te, "lupita", x=XL, expr="happy", pose="phone" if clue else ("point" if (1.1 <= tt < 2.5 or 4.0 <= tt < 5.4) else "down"), flip=True)
        ch(c, te, "beto", x=XB, expr="happy", pose="down", look=1)
        draw_tower(c, XB, tt, n)
        dx = dani_x(tt)
        if dx < 420:
            ch(c, te, "dani", x=dx, expr="neutral" if tt < 5.5 else "shock", pose="point" if 4.0 <= tt < 5.4 or clue else "down", flip=True, walk=(1 + int(tt * 6) % 2) if 3.0 <= tt < 3.8 or 8.2 <= tt < 9.0 else 0)
        if clue:                                                      # el celular suena: «CHUY ♥»
            bx, by = XL + 20, 300
            d.rounded_rectangle([bx, by, bx + 150, by + 44], radius=10, fill=(250, 250, 255), outline=(30, 18, 44), width=3)
            txt(d, (bx + 62, by + 22), "CHUY", 16, (30, 18, 44), outline=(250, 250, 255)); heart(d, bx + 128, by + 26, 11)
        if 0.3 < tt < 1.3: emote(c, XB, 260, "!", tt - 0.3)
        keys = [(0, 40, 150, FY), (1.0, 40, 150, FY), (1.1, 36, 185, FY), (2.5, 36, 185, FY), (2.6, 36, 100, FY), (4.0, 36, 230, FY),
                (5.5, 36, 100, FY), (7.0, 36, 190, FY), (9.0, 40, 150, FY), (11.0, 40, 150, FY)]
        return c, keys, (4 if 0.12 <= tt < 0.6 else 0)
    if tt < 19.4:                                                     # ACTO 2: la verdad
        bx = -30 + 110 * sm((tt - 11.0) / 1.8) if tt < 12.8 else XB
        walking = tt < 12.8
        ch(c, te, "beto", x=bx, expr="happy" if tt < 17.3 else ("shock" if tt < 18.8 else "sad"), pose="down", walk=(1 + int(tt * 7) % 2) if walking else 0, flip=False)
        # ramo de flores en la mano
        fx = bx + 32
        d.line([fx, FEET - 105, fx + 6, FEET - 70], fill=(60, 140, 70), width=4)
        for k, cc in enumerate(((240, 80, 120), (250, 210, 70), (240, 120, 190))):
            d.ellipse([fx - 10 + k * 9, FEET - 130 - (k % 2) * 6, fx + 4 + k * 9, FEET - 114 - (k % 2) * 6], fill=cc, outline=(30, 18, 44))
        ch(c, te, "lupita", x=215, expr="happy", pose="phone" if 13.2 <= tt < 14.5 else "down", flip=True)
        ch(c, te, "chuy", x=300, expr="happy", pose="down", flip=True)
        if 13.0 <= tt < 17.3:
            heart(d, 258, 295 + 6 * math.sin(tt * 4), 14)
            card(d, 225, 400)                                          # la tarjeta de Beto en manos de Lupita
        if 17.2 <= tt < 18.4:                                          # corazón roto
            dx = XB - 6; dy = 285
            heart(d, dx, dy, 18, (200, 60, 90)); d.line([dx, dy - 20, dx - 5, dy - 4, dx + 5, dy + 6, dx, dy + 20], fill=(30, 18, 44), width=4)
        if 17.3 < tt < 18.8: emote(c, bx, 260, "?", tt - 17.3)
        keys = [(11.0, 40, 150, FY), (11.6, 36, 80, FY), (13.0, 36, 80, FY), (13.1, 36, 200, FY), (15.8, 36, 220, FY), (17.2, 36, 150, FY),
                (18.8, 36, 100, FY), (19.4, 40, 150, FY)]
        return c, keys, (3 if 17.2 <= tt < 17.6 else 0)
    if tt < 26.6:                                                     # ACTO 3: confrontación y ruptura
        ch(c, te, "beto", x=XB, expr="angry" if tt < 24.9 else "sad", pose="point" if 19.8 <= tt < 21.1 else "down", fx=("vein",) if tt < 22.5 else (), shake=2 if 19.8 <= tt < 21.1 else 0)
        ch(c, te, "lupita", x=XL, expr="shock" if tt < 23.8 else "shy", pose="down", flip=True, fx=("sweat",))
        if 19.9 < tt < 21.2: speed_lines(c, XB, 320, te, int(110 * (1 - (tt - 19.9) / 1.3)))
        if tt < 25.3:
            if tt >= 22.5: card(d, 150, 380 + int(6 * math.sin(tt * 5)))
        else:                                                          # Beto parte la tarjeta en dos
            u = min(1.0, (tt - 25.3) / 0.9)
            for sgn in (-1, 1):
                d.polygon([(150 + sgn * 30 * u, 380 + 40 * u), (177 + sgn * 30 * u, 380 + 40 * u + 2), (177 + sgn * 34 * u, 414 + 40 * u), (150 + sgn * 34 * u, 412 + 40 * u)], fill=CARD, outline=(30, 18, 44))
        if 25.3 <= tt < 26.0:
            heart(d, 135, 270, 22, (200, 60, 90)); d.line([135, 248, 130, 266, 140, 276, 135, 292], fill=(30, 18, 44), width=4)
        keys = [(19.4, 40, 150, FY), (19.8, 36, 100, FY), (21.1, 36, 100, FY), (21.2, 36, 185, FY), (23.7, 36, 150, FY), (23.8, 36, 185, FY),
                (25.0, 36, 100, FY), (26.6, 40, 150, FY)]
        return c, keys, (4 if 25.3 <= tt < 25.6 else 0)
    # ACTO 4: llega una mejor… y todo se repite
    n = tower(tt)
    ch(c, te, "vale", x=XL, expr="happy", pose="point" if tt >= 29.7 else "down", flip=True, hop=3 if 27.0 <= tt < 28.3 else 0)
    ch(c, te, "beto", x=XB, expr="shock" if 27.0 <= tt < 29.6 else ("shy" if tt >= 31.0 else "happy"), pose="down", look=1)
    draw_tower(c, XB, tt, n)
    if 26.7 < tt < 28.5: sparkles(c, te, XL, 330, 6, 90)
    if 27.0 < tt < 28.4:
        heart(d, XL + 30, 255 + 4 * math.sin(tt * 5), 12)
    if 28.4 <= tt < 29.6:                                              # ella paga
        for k in range(6):
            u = ((tt - 28.4) * 1.0 + k * 0.15) % 1.0
            d.ellipse([XL - 70 * u - 8, 330 - 50 * math.sin(math.pi * u) - 8, XL - 70 * u + 8, 330 - 50 * math.sin(math.pi * u) + 8], fill=(250, 214, 80), outline=(30, 18, 44), width=2)
    keys = [(26.6, 40, 150, FY), (27.0, 36, 190, FY), (28.3, 36, 190, FY), (28.4, 36, 100, FY), (29.6, 36, 100, FY), (29.7, 36, 190, FY),
            (31.0, 36, 100, FY), (32.0, 40, 150, FY)]
    return c, keys, 0


def start_state():
    """Estado del segundo 0 (para el cierre en bucle)."""
    return state(0.0, 0.0)


def frame(t):
    tt = min(t, SEAM - 0.001)
    te = t if t < SEAM else t - T
    c, keys, sh = state(tt, tt if t < SEAM else te)
    if t >= T - 0.45:                                                   # el final se funde con el primer fotograma: se repite
        u = sm((t - (T - 0.45)) / 0.42)
        c0, _, _ = state(0.0, 0.0)
        c = Image.blend(c.convert("RGB"), c0.convert("RGB"), u).convert("RGBA")
        sh = 0
    return c, cam_at(keys + [(T, 40, 150, 345)], t), sh


def music(track):
    A = audio
    A.groove(track, 0, 11.0, 108, "maj", layers=("bass", "pad", "arp"), mel="b")                         # acto 1: dulce
    A.groove(track, 11.0, 19.4, 88, "min", layers=("bass", "pad", "lead"), mel="b", vol=0.9)             # acto 2: tensión
    A.groove(track, 19.4, 26.6, 128, "min", layers=("bass", "pad", "arp", "drums"))                      # acto 3: pelea
    A.groove(track, 26.6, 34.5, 116, "maj", mel="b", vol=0.9)                                            # acto 4: alivio y repetición
    A.ambient(track, 0, 34.5, "street", 1.0)


def sfx(track):
    A = audio
    A.whoosh(track, 0.0, 0.3, 0.2); A.hit(track, 0.5)
    for t0, t1, who, _ in LINES:
        A.put(track, t0, A.blip(VOICES[who]["pitch"] * 1.6, 0.3)); A.put(track, t0 + 0.07, A.blip(VOICES[who]["pitch"] * 2.0, 0.3))
    A.coin(track, 2.6, 0.12); A.coin(track, 4.0, 0.12)
    for x in (7.2, 8.0): A.notify(track, x)                                  # el celular suena
    for k in range(5): A.step(track, 3.0 + 0.16 * k, 0.1)
    A.sting(track, 9.0)
    for k in range(7): A.step(track, 11.0 + 0.25 * k, 0.1)                   # Beto llega con flores
    A.sparkle(track, 13.1)
    A.scratch(track, 17.2); A.hit(track, 17.3); A.trombone(track, 17.8)       # lo descubre
    A.boing(track, 19.8); A.hit(track, 19.8); A.airhorn(track, 19.8, 0.08)
    A.hit(track, 25.3); A.put(track, 25.3, A.noise(0.3, 0.3, 0.2))            # parte la tarjeta
    A.jingle(track, 26.8); A.sparkle(track, 27.0)
    for k in range(6): A.coin(track, 28.4 + 0.15 * k, 0.1)                   # ella paga
    A.pop(track, 29.7); A.laugh(track, 31.1)
    A.riser_short(track, 32.6, 1.5)


EP = dict(T=T, hooks=[(0.0, 2.5, HOOK)], cuts=[], voices=VOICES, punches=[(a, 2.5) for a, _, _, _ in LINES],
          lines=LINES, frame=frame, hud=hud, banner=lambda t: "", music=music, sfx=sfx, meta=META,
          safe=True, mix="pro", cta_mid=(9.0, 11.0, CTA_MID), final_cta=CTA_FINAL["ab"], cta_options=CTA_FINAL,
          flash=lambda: [0.12, 0.16, 0.2])

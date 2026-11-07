"""«Últimos en la tierra… y una sola bolsa de papas» — versión 2 (22 s, estándar de zona segura y mezcla -14 LUFS).
Piero y Memo, registro MÉXICO (wey / neta / qué onda). Un solo remate: Piero le da UNA papa al zombi y el zombi comparte su cerebro.
Variante A: el zombi irrumpe en 0 s (shake + flash). Variante B: pregunta estática (mismo guion, misma hora)."""
import math

from PIL import ImageDraw

from .. import audio
from ..bg import sparkles, emote, speed_lines
from ..cast import make_cast
from ..engine import cam_at
from ..sprite import draw_char, CHARS
from .. import scenes3 as S3
from . import bro_juega_bien as B
from .bro_juega_bien import sm

STATE = {"variant": "A"}
K = 1.0
T = 22.0                              # 22.0 s = 528 fotogramas exactos
CUTS = []                             # sin cortes: el gancho es un flash, el resto es plano continuo
META = dict(id="ultimos-zombis", category="ultimo-hombre", topic="ultimo-hombre",
            title="Últimos en la tierra y una sola bolsa de papas",
            caption_hook="Si fueras el último en la tierra, ¿compartes la última papa? A o B",
            caption="Si fueras el último en la tierra, ¿compartes la última papa? A o B",
            tags=["#zombis", "#pixelart", "#humor", "#amigos", "#shorts"])

_n = 0
while True:                           # Piero sin peinado de coleta/chongo
    CAST = make_cast(META["id"] + ("" if _n == 0 else f"-{_n}"), register="MX", names={"bro": "Piero", "a": "Memo"})
    if CHARS[CAST["bro"]["sprite"]]["style"] in ("spiky", "cap", "curly") and CHARS[CAST["a"]["sprite"]]["style"] != CHARS[CAST["bro"]["sprite"]]["style"]:
        break
    _n += 1
SPRITE = {"piero": CAST["bro"]["sprite"], "memo": CAST["a"]["sprite"], "zombi": "zombi"}
VOICES = {
    "piero": dict(label="PIERO", color=(226, 200, 120), pitch=230),
    "memo": dict(label="MEMO", color=(130, 190, 210), pitch=300),
    "zombi": dict(label="ZOMBI", color=(150, 220, 140), pitch=110),
}
# Cajas: máx. 8 palabras, 1 línea. Sin flags. Jerga: México.
LINES = [
    (1.1, 2.4, "memo", "Bro, hay que huir."),
    (2.5, 3.9, "piero", "Primero las papas."),
    (4.1, 5.5, "memo", "Dale, tírale algo."),
    (5.6, 6.9, "piero", "¡Neta, wey, no!"),
    (9.2, 10.7, "piero", "¿Qué onda? ¡Son mías!"),
    (11.0, 12.4, "memo", "Wey, el zombi tiene hambre."),
    (12.6, 14.2, "piero", "Neta, me da cosa, wey."),
    (15.3, 16.6, "zombi", "…gracias, bro."),
    (16.8, 18.3, "memo", "¡Me traicionaste por un zombi!"),
]
HOOK = {"A": "ÚLTIMOS EN LA TIERRA... Y UNA SOLA BOLSA DE PAPAS",
        "B": "¿QUÉ HARÍAS SI FUERAS EL ÚLTIMO EN LA TIERRA CON UNA BOLSA DE PAPAS?"}
CTA_MID = "¿Tú huyes o compartes?\nA: huyo / B: comparto"
CTA_FINAL = {"ab": "¿Quién da la última papa?\nResponde A o B", "etiqueta": "Etiqueta a tu bro que haría esto"}
B.LINES_ACTIVE[0] = LINES
SC, ZC = 3.2, 3.4
FEET = 467
XP, XM, XZ = 72, 175, 288
SEAM = 20.0                          # desde aquí el video regresa al estado del segundo 0 (bucle)


def zombie_x(t):
    """Posición del zombi. A: irrumpe en 0 s (shake + flash) y se aleja. B: entra caminando a los 4 s. Ambas vuelven al estado del segundo 0."""
    v = STATE["variant"]
    if t < 4.0:
        if v == "B" or t >= 1.5: return 440
        if t < 0.5: return XZ
        if t < 0.9: return XZ - 38 * sm((t - 0.5) / 0.15)
        return XZ - 38 + (440 - XZ + 38) * sm((t - 0.9) / 0.6)
    if t < 7.0: return 440 - (440 - XZ) * sm((t - 4.0) / 3.0)
    if t < 19.5: return XZ
    return XZ if v == "A" else XZ + (440 - XZ) * sm((t - 19.5) / 1.2)


zombie_x_final = zombie_x


def blink_or_talk(t, key, kw):
    sp = B.speaking(t)
    expr = kw.get("expr", "neutral")
    if key in sp and int(t * 7) % 2 == 0:
        kw["mouth"] = "big" if expr == "happy" else ("o" if expr == "shock" else "open")
    elif expr in ("neutral", "sad", "shy") and ((t * 24 + kw["x"] * 0.37) % 76) < 3:
        kw["expr"] = "blink"
    return kw


def ch(c, t, key, **kw):
    kw = blink_or_talk(t, key, kw)
    x = kw.pop("x"); sc = kw.pop("scale", SC); shake = kw.pop("shake", 0); hop = kw.pop("hop", 0)
    ox = round(math.sin(t * 61) * shake) if shake else 0
    oy = round(math.sin(t * 2.6 + x) * 1.5 + math.sin(t * 5 + x) * .6) - (round(abs(math.sin(t * 9 + x)) * hop) if hop else 0)
    draw_char(c, SPRITE[key], x, kw.pop("feet", FEET), ox=ox, oy=oy, scale=sc, **kw)


def bag(c, x, y, t, hug=True, squeeze=0.0):
    d = ImageDraw.Draw(c)
    w, h = 44 + int(6 * squeeze), 56 - int(5 * squeeze)
    x0, y0 = x - w // 2, y - h // 2
    d.rectangle([x0 - 2, y0 - 2, x0 + w + 2, y0 + h + 2], fill=(30, 18, 44))
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(250, 200, 70)); d.rectangle([x0, y0, x0 + 6, y0 + h], fill=(255, 228, 130))
    d.rectangle([x0 + w - 6, y0, x0 + w, y0 + h], fill=(220, 160, 40)); d.rectangle([x0 + 6, y0 + 12, x0 + w - 6, y0 + 28], fill=(220, 60, 60))
    for k in range(5):                                                      # sello superior zigzag
        d.rectangle([x0 + k * (w // 5), y0 - 6, x0 + k * (w // 5) + w // 10, y0 - 1], fill=(250, 200, 70))


def frame(t):
    v = STATE["variant"]
    st = t if t < SEAM else t - T                       # fase de animación negativa al final = estado del segundo 0
    start_state = t < 0.5 or t >= SEAM
    c = S3.calle_vacia(st)
    zx = zombie_x_final(t)
    z_in = zx < 400
    shake = 0
    pz = "point"
    # --- Piero y Memo ---
    hug = True
    p_exp, m_exp, look = "shock", "shock", -1
    if v == "A" and start_state:
        p_exp, m_exp = "shock", "shock"
    elif 1.5 <= t < 4.0 or (v == "B" and t < 4.0):
        p_exp, m_exp = "shy", "neutral"
    elif t < 7.0:
        p_exp, m_exp = "shock", "angry"
    elif t < 15.0:
        p_exp, m_exp = ("sad" if 12.5 <= t < 15.0 else "shock"), ("shock" if t < 11 else "sad")
    elif t < 18.0:
        p_exp, m_exp = "happy" if t >= 15.0 else "shy", "shock" if t < 17.5 else "sad"
    else:
        p_exp, m_exp = "happy", "shy"
    if t >= SEAM:
        p_exp, m_exp = ("shock", "shock") if v == "A" else ("shy", "neutral")
    look = -1 if (t < 4.0 or t >= SEAM) else (1 if int(t * 1.6) % 2 == 0 else -1) if 9 <= t < 15 else 1
    hide = 9.4 <= t < 12.0                              # gag 1: esconde la bolsa
    give = 15.0 <= t < 15.6
    squeeze = 1.0 if (1.95 < t < 2.35 or 9.4 < t < 9.7) else 0.0
    ch(c, t, "memo", x=XM, expr=m_exp, pose="cheer" if (t >= 18.0 and t < 19.5 and False) else "down", fx=("sweat",) if m_exp in ("shock", "angry") else ())
    ch(c, t, "piero", x=XP, expr=p_exp, pose="down", look=look, fx=("sweat",) if p_exp in ("shock", "sad") else (), shake=1 if (12.5 <= t < 15.0) else 0)
    if not hide:                                         # bolsa abrazada (o escondida a la espalda en el gag 1)
        if not (give and False):
            bag(c, XP + 4, FEET - 84, t, squeeze=squeeze)
    else:
        d = ImageDraw.Draw(c); d.rectangle([XP - 50, FEET - 120, XP - 40, FEET - 88], fill=(250, 200, 70))
    # --- zombi ---
    if z_in:
        zshake = 3 if (v == "A" and t < 1.4) else 0
        zexp = "sad" if t < 15.0 else "happy"
        zpose = "point" if (t < 16.6 or t >= 18.5) else "cheer"
        if t >= 7.0 and t < 9.0 or 12.5 <= t < 14.2:
            zexp = "shock"
        ch(c, t, "zombi", x=zx, scale=ZC, expr=zexp, pose=zpose, flip=True, walk=(1 + int(t * 5) % 2) if (4.0 <= t < 7.0 or 19.5 <= t) else 0, shake=zshake)
    # --- props del remate ---
    d = ImageDraw.Draw(c)
    if give:                                              # UNA papa vuela de Piero al zombi
        u = (t - 15.0) / 0.6
        px, py = XP + 30 + (zx - XP - 60) * u, FEET - 140 - 50 * math.sin(math.pi * u)
        d.polygon([(px, py), (px + 14, py + 4), (px + 8, py + 14)], fill=(255, 214, 90), outline=(30, 18, 44))
    if 16.7 <= t < 18.4:                                  # el zombi comparte su cerebro
        u = min(1.0, (t - 16.7) / 0.5)
        bx, by = zx - 60 - (zx - XM - 70) * 0.55 * u, FEET - 150
        d.ellipse([bx - 18, by - 14, bx + 18, by + 14], fill=(240, 140, 170), outline=(30, 18, 44), width=2)
        d.line([bx - 6, by - 8, bx - 10, by + 6], fill=(200, 90, 130), width=2); d.line([bx + 6, by - 8, bx + 10, by + 6], fill=(200, 90, 130), width=2)
        d.line([bx, by - 12, bx, by + 12], fill=(200, 90, 130), width=2)
    if 0.3 < t < 1.2 and v == "A":
        speed_lines(c, zx, 340, st, int(120 * (1 - (t - 0.3) / 0.9)))
    if 18.0 <= t < 19.2:
        sparkles(c, t, zx - 30, 330, 6, 80)
    # --- cámara (más cerrada; los pies caen ~73% de la altura y el techo de las cabezas queda bajo la caja de diálogo) ---
    F = {40: 320, 36: 335, 34: 342}
    def K_(tt, k, fx): return (tt, k, fx, F[k])
    if v == "A":
        keys = [K_(0, 40, 180), K_(1.0, 40, 180), K_(1.1, 36, 135), K_(4.0, 36, 135), K_(4.3, 34, 205), K_(7.0, 34, 205),
                K_(9.0, 36, 190), K_(12.4, 36, 150), K_(14.9, 36, 150), K_(15.3, 34, 205), K_(18.3, 34, 205),
                K_(19.5, 40, 180), K_(T, 40, 180)]
    else:
        keys = [K_(0, 40, 180), K_(4.0, 36, 150), K_(4.3, 34, 205), K_(7.0, 34, 205), K_(9.0, 36, 190), K_(12.4, 36, 150),
                K_(14.9, 36, 150), K_(15.3, 34, 205), K_(18.3, 34, 205), K_(19.5, 40, 180), K_(T, 40, 180)]
    cam = cam_at(keys, t)
    sh = 3 if (v == "A" and (t < 1.2 or t >= SEAM + 0.0 and False)) else 0
    if v == "A" and (0.5 <= t < 1.0):
        sh = 5
    return c, cam, sh


def flash_frames():
    return [0.04, 0.08, 0.12] if STATE["variant"] == "A" else []


def hud(t):
    return [("SOBREVIVIENTES", "2"), ("PAPAS", "1" if t < 15.0 or t >= SEAM else "0")]


def music(track):
    audio.groove(track, 0, 22.0, 100, "min", layers=("bass", "pad", "arp"), mel="b")
    audio.groove(track, 15.0, 19.5, 100, "maj", layers=("pad", "lead"), mel="b", vol=0.8)
    audio.ambient(track, 0, 22.0, "street", 1.0)


def blip_box(track, t0, pitch):
    audio.put(track, t0, audio.blip(pitch * 1.6, 0.3)); audio.put(track, t0 + 0.07, audio.blip(pitch * 2.0, 0.3))


SFX_TIMELINE = [  # (t en s, efecto)
    (0.0, "whoosh"), (0.5, "zombie_hit"), (1.1, "blip(memo)"), (2.0, "crinkle"), (2.5, "blip(piero)"), (4.0, "zombie_steps 4-7"),
    (4.1, "blip(memo)"), (5.6, "blip(piero)"), (7.0, "sting CTA"), (9.2, "blip(piero)"), (9.4, "crinkle (gag 1)"), (10.0, "gulp (gag 1)"),
    (10.6, "boing (gag 1)"), (11.0, "blip(memo)"), (12.6, "blip(piero)"), (12.6, "growl (gag 2)"), (13.5, "boing (gag 2)"), (14.2, "gulp (gag 2)"),
    (15.0, "ding (remate)"), (15.3, "blip(zombi)"), (16.8, "blip(memo)"), (16.9, "squish (cerebro)"), (18.0, "risa/pop"), (20.8, "riser antes del loop"),
]


def sfx(track):
    A = audio
    if STATE["variant"] == "A":
        A.whoosh(track, 0.0, 0.3, 0.2); A.zombie_hit(track, 0.5)
    else:
        A.whoosh(track, 0.0, 0.25, 0.1)
    for t0, t1, who, _ in LINES:
        blip_box(track, t0, VOICES[who]["pitch"])
    A.crinkle(track, 2.0)
    A.zombie_steps(track, 4.0, 7.0)
    A.sting(track, 7.0)
    A.crinkle(track, 9.4); A.gulp(track, 10.0); A.boing(track, 10.6)
    A.growl(track, 12.6, 0.8); A.boing(track, 13.5); A.gulp(track, 14.2)
    A.ding(track, 15.0)
    A.squish(track, 16.9)
    A.laugh(track, 18.0)
    A.riser_short(track, 20.8, 1.2)


EP = dict(
    T=T, hooks=[(0.0, 2.5, "")], hook_text=lambda: HOOK[STATE["variant"]], cuts=[], voices=VOICES, punches=[(a, 2.5) for a, _, _, _ in LINES],
    lines=LINES, frame=frame, hud=hud, banner=lambda t: "", music=music, sfx=sfx, meta=META,
    safe=True, mix="pro", cta_mid=(7.0, 9.0, CTA_MID), final_cta=CTA_FINAL["ab"], cta_options=CTA_FINAL, flash=flash_frames)

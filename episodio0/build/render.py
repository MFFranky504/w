"""Render del Episodio 0 (convocatoria) — pixel art 360x640 escalado x3 a 1080x1920.

Uso:
  python3 render.py                 # video completo -> out/episodio0_convocatoria.mp4
  python3 render.py --fotos 1 6 20  # fotogramas sueltos (segundos) -> out/preview_*.png
"""
import json, math, subprocess, sys, pathlib
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import fuente, guion

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
W, H, FPS, ESC = 360, 640, 30, 3

P = dict(bg0=(10, 9, 16), bg1=(20, 17, 31), bg2=(34, 29, 51), bg3=(56, 48, 80), bg4=(84, 74, 112),
         amber=(255, 176, 32), amber_d=(190, 108, 18), amber_l=(255, 224, 130),
         bone=(241, 233, 210), bone_d=(150, 142, 128), bone_dd=(92, 86, 82),
         red=(232, 68, 58), red_d=(140, 34, 40), ghost=(150, 215, 228), ghost_d=(70, 120, 140),
         out=(6, 5, 10))

B4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
BAYER = np.tile(B4, (H // 4, W // 4))


def hsh(*a):
    """Hash determinista -> [0,1)."""
    x = 0
    for v in a:
        x = (x * 1000003 + int(v * 1000) + 0x9E3779B9) & 0xFFFFFFFF
        x ^= x >> 15
        x = (x * 0x2C1B3C6D) & 0xFFFFFFFF
        x ^= x >> 12
    return (x & 0xFFFFFF) / 0x1000000


# ------------------------------------------------------------------ fondos (numpy, con dithering)
def mezcla_dither(c0, c1, f):
    m = (f > BAYER[: f.shape[0], : f.shape[1]])[..., None]
    return np.where(m, np.array(c1, np.uint8), np.array(c0, np.uint8)).astype(np.uint8)


def fondo_sala(luz=1.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = mezcla_dither(P["bg0"], P["bg1"], np.clip(yy / 390, 0, 1) * 0.9)
    piso = yy >= 390
    img[piso] = mezcla_dither(P["bg1"], P["bg2"], np.clip((yy - 390) / 250, 0, 1))[piso]
    # cono de luz
    medio = 18 + (yy / 400) * 95
    f = np.clip(1 - np.abs(xx - 180) / medio, 0, 1) * np.clip(1 - yy / 430, 0, 1) * 0.55 * luz
    cono = mezcla_dither(P["bg0"], P["bg3"], f)
    sel = (f > 0.02) & ~piso
    img[sel] = np.where((f[..., None] > BAYER[..., None] * 0.9)[sel], cono[sel], img[sel])
    # charco de luz en el piso
    e = ((xx - 180) / 120) ** 2 + ((yy - 405) / 26) ** 2
    f2 = np.clip(1 - e, 0, 1) * 0.95 * luz
    charco = mezcla_dither(P["bg2"], P["bg4"], f2)
    sel2 = f2 > 0.01
    img[sel2] = charco[sel2]
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    # líneas de fuga del piso
    for k in range(-9, 10):
        d.line([(180 + k * 9, 390), (180 + k * 70, 640)], fill=P["bg1"] if abs(k) > 2 else P["bg2"])
    for j in range(1, 9):
        y = 390 + int(250 * (j / 9) ** 1.8)
        d.line([(0, y), (W, y)], fill=P["bg1"])
    d.line([(0, 390), (W, 390)], fill=P["bg3"])
    return im


def fondo_oscuro(brillo=0.35, cy=230):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    r = np.sqrt(((xx - 180) / 200) ** 2 + ((yy - cy) / 260) ** 2)
    f = np.clip(1 - r, 0, 1) * brillo * 2
    img = mezcla_dither(P["bg0"], P["bg1"], np.clip(f, 0, 1))
    f2 = np.clip(f - 0.55, 0, 1) * 1.6
    img2 = mezcla_dither(P["bg1"], P["bg2"], f2)
    img = np.where((f2 > 0.01)[..., None], img2, img)
    return Image.fromarray(img)


def mascara_vineta():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    r = np.sqrt(((xx - 180) / 230) ** 2 + ((yy - 300) / 400) ** 2)
    f = np.clip((r - 0.62) / 0.5, 0, 1)
    niveles = np.array([1.0, 0.82, 0.66, 0.5])
    q = np.clip((f * 3 + BAYER).astype(int), 0, 3)
    return niveles[q][..., None]


# ------------------------------------------------------------------ sprites
def sprite(filas, pal, esc=1, transl=None):
    h, w = len(filas), len(filas[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, fila in enumerate(filas):
        for x, c in enumerate(fila):
            if c in pal and pal[c] is not None:
                if transl and c in transl and (x + y) % 2:
                    continue
                px[x, y] = tuple(pal[c]) + (255,)
    if esc != 1:
        im = im.resize((w * esc, h * esc), Image.NEAREST)
    return im


HEROE = ["...ooooo...", "..ohhhhho..", ".ohHhhhhho.", ".ohhfffhho.", ".ohfefefho.", ".ohfffffho.",
         "..ohhhhho..", ".oobbbbboo.", "obbbbbbbbbo", "obbiiiiibbo", "obobbbbbobo", "obobbbbbobo",
         "oko.bbb.oko", "...obbbo...", "...ob.bo...", "...ob.bo...", "...oo.oo..."]
HEROE_PASO = HEROE[:13] + ["..obbbbbo..", "..ob...bo..", ".ob.....bo.", ".oo.....oo."]
PAL_HEROE = {"o": P["out"], "h": (70, 62, 98), "H": (112, 100, 142), "f": (16, 13, 24), "e": P["bone"],
             "b": (48, 42, 70), "i": P["amber"], "k": (30, 26, 44)}
PAL_FANT = {"o": P["ghost"], "h": P["ghost_d"], "H": P["ghost"], "f": None, "e": P["bone"],
            "b": P["ghost_d"], "i": P["ghost"], "k": P["ghost_d"]}
SIL = [".###.", "#e#e#", ".###.", ".###.", "#####", "#####", ".#.#.", ".#.#."]
MINI = [".#.", "###", "###", "#.#"]

ICONOS = {
    "fuego": ([".....#......", "....##......", "....###.#...", "...####.##..", "..#####.###.", "..#########.",
               ".###########", ".####oo#####", ".###oyyo####", ".###oyyo###.", "..##oyyo##..", "...######..."],
              {"#": P["red"], "o": P["amber"], "y": P["amber_l"]}),
    "rayo": ([".......####.", "......####..", ".....####...", "....####....", "...#######..", "......####..",
              ".....####...", "....###.....", "...###......", "..##........", ".#..........", "............"],
             {"#": P["amber"]}),
    "estrella": ([".....##.....", ".....##.....", "....####....", "############", ".##########.", "..########..",
                  "...######...", "..###..###..", "..##....##..", ".##......##.", "............", "............"],
                 {"#": P["amber_l"]}),
}

_txt_cache = {}


def texto(txt, color, esc=1, sombra=None):
    k = (txt, color, esc, sombra)
    if k not in _txt_cache:
        w = fuente.ancho_texto(txt, esc) + esc + 1
        im = Image.new("RGBA", (max(1, w), fuente.H_CELDA * esc + esc + 1), (0, 0, 0, 0))
        fuente.dibujar(im, 0, 0, txt, tuple(color) + (255,), esc,
                       sombra=(tuple(sombra) + (255,)) if sombra else None)
        _txt_cache[k] = im
    return _txt_cache[k]


def pegar(img, spr, x, y):
    img.paste(spr, (int(x), int(y)), spr)


def pegar_centrado(img, spr, cx, y):
    pegar(img, spr, cx - spr.width // 2, y)


def txt_c(img, s, cx, y, color, esc=1, sombra=None):
    pegar_centrado(img, texto(s, color, esc, sombra), cx, y)


def desintegrar(img, spr, x, y, p, semilla, color_part):
    """p: 0 -> intacto, 1 -> desaparecido. Píxeles se apagan al azar y suben chispas."""
    if p <= 0:
        pegar(img, spr, x, y)
        return
    if p >= 1.3:
        return
    a = np.array(spr)
    hgt, wid = a.shape[:2]
    yy, xx = np.mgrid[0:hgt, 0:wid]
    ruido = (np.sin(xx * 12.9898 + yy * 78.233 + semilla) * 43758.5453) % 1
    a = a.copy()
    a[..., 3] = np.where(ruido < p, 0, a[..., 3])
    s2 = Image.fromarray(a)
    pegar(img, s2, x, y)
    d = ImageDraw.Draw(img)
    for k in range(6):
        px = x + hsh(semilla, k) * wid
        py = y + hgt * (0.2 + 0.7 * hsh(semilla, k, 1)) - p * (10 + 25 * hsh(semilla, k, 2))
        if p < 1.2 and hsh(semilla, k, 3) < 1.1 - p * 0.7:
            d.point((px, py), fill=color_part)


def fundido(img, a, color=(0, 0, 0)):
    """a=1 -> todo color. Fundido con dithering ordenado."""
    if a <= 0:
        return img
    arr = np.array(img)
    m = (BAYER < a)[..., None]
    arr = np.where(m, np.array(color, np.uint8), arr)
    return Image.fromarray(arr.astype(np.uint8))


def glitch_filas(img, t, intens=6, semilla=0):
    arr = np.array(img)
    for k in range(10):
        y0 = int(hsh(t, k, semilla) * (H - 20))
        h = 2 + int(hsh(t, k, 9) * 14)
        dx = int((hsh(t, k, 5) - 0.5) * 2 * intens)
        arr[y0:y0 + h] = np.roll(arr[y0:y0 + h], dx, axis=1)
    return Image.fromarray(arr)


# ------------------------------------------------------------------ recursos precalculados
print("precalculando fondos...")
SALA = [fondo_sala(l) for l in (0.6, 0.8, 1.0, 1.25, 1.5)]
OSCURO = fondo_oscuro()
OSCURO_LOGO = fondo_oscuro(0.5, 200)
VIG = mascara_vineta()
SPR_H = {e: (sprite(HEROE, PAL_HEROE, e), sprite(HEROE_PASO, PAL_HEROE, e)) for e in (2, 3, 4, 5)}
SPR_F = {e: sprite(HEROE, PAL_FANT, e, transl={"h", "b", "k"}) for e in (2, 3, 4)}
SPR_MINI = sprite(SIL, {"#": P["bone_d"], "e": P["bg0"]})
SPR_MINI_R = sprite(SIL, {"#": P["red"], "e": P["bg0"]})
SPR_ICO = {k: sprite(f, p, 2) for k, (f, p) in ICONOS.items()}


def multitud_miembros():
    filas = [  # (y_pie, escala, paso, color_cuerpo, color_ojo)
        (300, 1, 7, (30, 27, 45), (80, 72, 64)),
        (314, 1, 7, (36, 32, 54), (100, 90, 78)),
        (330, 1, 6, (42, 37, 62), (120, 108, 90)),
        (352, 2, 11, (50, 44, 72), (150, 140, 120)),
        (374, 2, 11, (58, 51, 82), (170, 160, 140)),
        (396, 2, 13, (66, 58, 92), P["bone_d"]),
        (436, 3, 19, (40, 35, 58), P["bone_d"]),
        (482, 4, 26, (22, 19, 33), P["amber_d"]),
    ]
    m = []
    for fi, (yp, esc, paso, col, ojo) in enumerate(filas):
        x = -8 + (fi % 2) * paso // 2
        while x < W + 8:
            jx = (hsh(fi, x) - 0.5) * paso * 0.4
            heroe = fi == 5 and abs(x + jx - 180) < paso / 2
            m.append(dict(x=x + jx, y=yp, esc=esc, col=col, ojo=ojo, fi=fi, heroe=heroe,
                          bob=hsh(x, fi, 3) * 6.28, td=hsh(x, fi, 7)))
            x += paso
    # garantiza un héroe exacto al centro
    m = [mm for mm in m if not mm["heroe"]]
    m.append(dict(x=180, y=396, esc=2, col=(66, 58, 92), ojo=P["amber"], fi=5, heroe=True, bob=0, td=0))
    m.sort(key=lambda mm: (mm["y"], mm["x"]))
    return m


MULTITUD = multitud_miembros()
_sil_cache = {}


def sil(col, ojo, esc):
    k = (col, ojo, esc)
    if k not in _sil_cache:
        _sil_cache[k] = sprite(SIL, {"#": col, "e": ojo, ".": None}, esc)
    return _sil_cache[k]


# ------------------------------------------------------------------ escenas
def esc_multitud(img, t, L, ctx):
    """L01 + L02: la multitud llena la sala; luego se desintegra salvo uno."""
    l2 = L["K02"]
    td0, td1 = l2["inicio"] + 0.12, l2["fin"] - 0.12
    prog_der = np.clip((t - td0) / (td1 - td0), 0, 1)
    luz = 2 if prog_der < 0.5 else (3 if prog_der < 1 else 4)
    img.paste(SALA[luz])
    for m in MULTITUD:
        spr = sil(m["col"], m["ojo"], m["esc"])
        bob = 1 if math.sin(t * 2.2 + m["bob"]) > 0.6 else 0
        x = m["x"] - spr.width / 2
        y = m["y"] - spr.height - bob
        if m["heroe"]:
            if prog_der >= 1:
                s = SPR_H[2][0]
                pegar(img, s, 180 - s.width / 2, 396 - s.height)
            else:
                pegar(img, spr, x, y)
            continue
        tm = td0 + m["td"] * (td1 - td0 - 0.3)
        p = (t - tm) / 0.3
        desintegrar(img, spr, x, y, p, m["x"] * 7 + m["fi"], P["amber"] if m["fi"] >= 3 else P["bone_dd"])
    if prog_der >= 0.8:
        tag_id(img, 180, 396 - SPR_H[2][0].height - 36, "J-????", 2)
    return img


def emblema(img, cx, y, esc_j, t_ini, t):
    sJ = texto("J", P["amber"], esc_j, sombra=P["red_d"])
    w, h = sJ.width + esc_j * 6, sJ.height + esc_j * 3
    x0, y0 = cx - w // 2, y
    d = ImageDraw.Draw(img)
    g = max(2, esc_j // 3)
    L = esc_j * 2
    for (ax, ay, sx, sy) in ((x0, y0, 1, 1), (x0 + w, y0, -1, 1), (x0, y0 + h, 1, -1), (x0 + w, y0 + h, -1, -1)):
        d.rectangle([min(ax, ax + sx * L), min(ay, ay + sy * g), max(ax, ax + sx * L), max(ay, ay + sy * g)], fill=P["bone_d"])
        d.rectangle([min(ax, ax + sx * g), min(ay, ay + sy * L), max(ax, ax + sx * g), max(ay, ay + sy * L)], fill=P["bone_d"])
    dt = t - t_ini
    if 0 <= dt < 0.2:
        pegar(img, texto("J", P["red"], esc_j), cx - sJ.width // 2 - 3, y0 + esc_j * 1.5)
        pegar(img, texto("J", P["ghost"], esc_j), cx - sJ.width // 2 + 3, y0 + esc_j * 1.5)
    pegar(img, sJ, cx - sJ.width // 2 + esc_j // 2, y0 + esc_j * 1.5)
    return y0 + h


def esc_logo(img, t, L, ctx):
    l = L["K03"]
    t0 = l["inicio"] - 0.12
    img.paste(OSCURO_LOGO)
    yb = emblema(img, 180, 112, 14, t0, t)
    txt_c(img, guion.NOMBRE_PANTALLA, 180, yb + 22, P["amber"], 3, sombra=P["red_d"])
    if t > t0 + 0.5:
        txt_c(img, "TEMPORADA 1", 180, yb + 70, P["bone_d"], 2)
    if t - t0 < 0.07:
        img = fundido(img, 0.6, P["bone"])
    if t - t0 < 0.4:
        img = glitch_filas(img, round(t * FPS), 10)
    return img


def pop(t, ts, esc):
    if t < ts:
        return None
    return esc + 2 if t - ts < 0.07 else esc


def esc_conteo(img, t, L, ctx):
    l = L["K04"]
    img.paste(OSCURO)
    txt_c(img, "TEMPORADA 1", 180, 196, P["bone_dd"], 2)
    cols = [(100, 0, "6", "JUEGOS"), (260, 2, "1", "GANADOR")]
    d = ImageDraw.Draw(img)
    for cx, ti, num, lab in cols:
        ts = l["tokens"][ti]["s"] - 0.05
        e = pop(t, ts, 9)
        if e is None:
            continue
        final = num == "1"
        color = P["bone"] if final else P["amber"]
        s = texto(num, color, e, sombra=P["red_d"] if not final else P["amber_d"])
        pegar_centrado(img, s, cx, 245 - (e - 9) * 5)
        txt_c(img, lab, cx, 332, P["bone_d"] if not final else P["amber"], 2)
        if final and (t - ts) % 0.5 < 0.35:
            d.rectangle([cx - 62, 230, cx + 62, 362], outline=P["amber"], width=2)
    return img


def tag_id(img, cx, y, txt, esc):
    s = texto(txt, P["bone"], esc)
    w, h = s.width + 8 * esc // 2 + 6, s.height + 6
    d = ImageDraw.Draw(img)
    d.rectangle([cx - w // 2, y, cx + w // 2, y + h], fill=P["bg0"], outline=P["amber"], width=max(1, esc // 2))
    d.polygon([(cx - 4, y + h), (cx + 4, y + h), (cx, y + h + 5)], fill=P["amber"])
    pegar_centrado(img, s, cx + esc // 2, y + 4)


def esc_id(img, t, L, ctx):
    l5, l6 = L["K06"], L["K07"]
    zoom = t >= l6["inicio"] - 0.12
    img.paste(SALA[3] if zoom else SALA[2])
    t0 = l5["inicio"] - 0.12
    camina = np.clip((t - t0) / 1.6, 0, 1)
    if not zoom:
        x = -40 + (180 + 40) * (1 - (1 - camina) ** 2)
        paso = camina < 1 and int(t * 7) % 2 == 1
        s = SPR_H[3][1 if paso else 0]
        bob = 0 if camina < 1 else (1 if math.sin(t * 3) > 0.7 else 0)
        pegar(img, s, x - s.width / 2, 400 - s.height - bob)
        rueda = l5["tokens"][4]["s"] - 0.1 <= t < l5["fin"]
        if camina >= 1:
            dig = "".join(str(int(hsh(int(t * 15), k) * 10)) for k in range(4)) if rueda else "????"
            tag_id(img, 180, 400 - s.height - 40, "J-" + dig, 2)
    else:
        dz = t - (l6["inicio"] - 0.12)
        e = 3 if dz < 0.1 else (4 if dz < 0.2 else 5)
        s = SPR_H[e][0]
        pegar(img, s, 180 - s.width / 2, 410 - s.height)
        tag_id(img, 180, 410 - s.height - 58, "J-????", 3)
        if (dz % 0.8) < 0.5:
            txt_c(img, "TU NÚMERO", 180, 410 - s.height - 80, P["amber"], 1)
    return img


def esc_reglas(img, t, L, ctx):
    l = L["K08"]
    img.paste(OSCURO)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 74, 118, 286, 366
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=P["bg0"])
    d.rectangle([x0, y0, x1, y1], fill=P["bg1"], outline=P["bone_dd"], width=2)
    txt_c(img, "REGLAS", 180, y0 + 12, P["amber"], 2)
    d.line([(x0 + 12, y0 + 40), (x1 - 12, y0 + 40)], fill=P["bone_dd"])
    t_lock = l["tokens"][-1]["s"]
    escribir = np.clip((t - l["inicio"]) / ((t_lock - l["inicio"]) * 0.85), 0, 1)
    anchos = [150, 128, 168, 110, 140, 96, 154]
    n = len(anchos)
    for k, wb in enumerate(anchos):
        p = np.clip(escribir * n - k, 0, 1)
        if p > 0:
            yb = y0 + 54 + k * 17
            d.rectangle([x0 + 18, yb, x0 + 18 + int(wb * p), yb + 5], fill=P["bone_dd"])
            d.rectangle([x0 + 18, yb, x0 + 18 + min(int(wb * p), 6), yb + 5], fill=P["bone_d"])
    # candado
    cerrado = t >= t_lock
    cx, cy = 180, 305
    col = P["amber"] if cerrado else P["bone_d"]
    dy = 0 if cerrado else -8
    d.rectangle([cx - 9, cy - 16 + dy, cx + 9, cy + dy], outline=col, width=3)
    d.rectangle([cx - 4, cy - 12 + dy, cx + 4, cy + 2 + dy], fill=P["bg1"])
    d.rectangle([cx - 14, cy, cx + 14, cy + 22], fill=col)
    d.rectangle([cx - 2, cy + 7, cx + 2, cy + 14], fill=P["bg0"])
    if cerrado:
        if t - t_lock < 0.08:
            d.rectangle([x0, y0, x1, y1], outline=P["amber_l"], width=3)
        txt_c(img, "SELLADAS", 180, cy + 30, P["amber"], 1)
    txt_c(img, "SE PUBLICAN ANTES DE JUGAR", 180, y1 + 14, P["bone_dd"], 1)
    return img


class Particulas:
    def __init__(self, n=72):
        self.n = n

    def col_en(self, i, t):
        """Columna objetivo de la partícula i en el tiempo t (cambia cada ~1 s)."""
        seg = int(t * 0.9 + hsh(i, 1) * 3)
        return int(hsh(i, seg) * 3), seg

    def pos(self, i, t):
        cols = [62, 180, 298]
        c, seg = self.col_en(i, t)
        tseg = (seg - hsh(i, 1) * 3) / 0.9
        cprev, _ = self.col_en(i, tseg - 0.01)
        a = np.clip((t - tseg) / 0.55, 0, 1)
        a = a * a * (3 - 2 * a)
        x = cols[cprev] + (cols[c] - cols[cprev]) * a + (hsh(i, 4) - 0.5) * 70
        y = 228 + hsh(i, 5) * 70 + (2 if a < 1 and int(t * 10 + i) % 2 else 0)
        return x, y, c


PART = Particulas()


def esc_elecciones(img, t, L, ctx):
    l = L["K09"]
    img.paste(SALA[1])
    d = ImageDraw.Draw(img)
    t_cierre = l["tokens"][-1]["s"]
    cols = [62, 180, 298]
    cuenta = [0, 0, 0]
    pos = []
    for i in range(PART.n):
        x, y, c = PART.pos(i, min(t, t_cierre) - l["inicio"] + 3)
        pos.append((x, y, c))
        cuenta[c] += 1
    if "cerrada" not in ctx and t >= t_cierre:
        ctx["cerrada"] = int(np.argmax(cuenta))
    cerrada = ctx.get("cerrada") if t >= t_cierre else None
    for k, cx in enumerate(cols):
        col = P["red"] if cerrada == k else P["bg3"]
        d.rectangle([cx - 18, 130, cx + 18, 190], fill=P["bg2"], outline=col, width=2)
        d.rectangle([cx - 12, 136, cx + 12, 160], outline=P["bg1"])
        d.rectangle([cx - 12, 165, cx + 12, 186], outline=P["bg1"])
        d.point((cx + 11, 172), fill=P["amber_d"])
        txt_c(img, "ABC"[k], cx, 108, P["red"] if cerrada == k else P["bone_d"], 2)
        if cerrada == k:
            d.line([(cx - 18, 130), (cx + 18, 190)], fill=P["red"], width=3)
            d.line([(cx + 18, 130), (cx - 18, 190)], fill=P["red"], width=3)
        alto = int(cuenta[k] / PART.n * 150)
        d.rectangle([cx - 14, 360 - alto, cx + 14, 360], fill=P["red_d"] if cerrada == k else P["amber_d"])
        d.rectangle([cx - 14, 360 - alto, cx + 14, 360 - alto + 2], fill=P["red"] if cerrada == k else P["amber"])
    for i, (x, y, c) in enumerate(pos):
        if cerrada is not None and c == cerrada:
            p = (t - t_cierre - hsh(i, 8) * 0.3) / 0.25
            desintegrar(img, SPR_MINI_R, x, y, p, i, P["red"])
        else:
            pegar(img, SPR_MINI, x, y)
    return img


def esc_fantasma(img, t, L, ctx):
    l9, l10 = L["K10"], L["K11"]
    if t < l10["inicio"] - 0.12:
        img.paste(SALA[3])
        t_cae = l9["tokens"][tk_idx(l9, "CAES", 4)]["s"]
        s = SPR_H[4][0]
        x, y = 180 - s.width / 2, 404 - s.height
        p = (t - t_cae) / 0.45
        if p < 1.3:
            desintegrar(img, s, x, y, p, 77, P["ghost"])
        tf = t_cae + 0.6
        if t > tf:
            g = SPR_F[4]
            flot = math.sin((t - tf) * 3) * 4
            a = np.clip((t - tf) / 0.4, 0, 1)
            capa = img.copy()
            pegar(capa, g, 180 - g.width / 2, 404 - g.height - 10 - (t - tf) * 6 + flot)
            img = Image.fromarray(np.where((BAYER < a)[..., None], np.array(capa), np.array(img)).astype(np.uint8))
        return img
    # votos de los fantasmas
    img.paste(OSCURO)
    d = ImageDraw.Draw(img)
    txt_c(img, "FANTASMAS", 180, 116, P["ghost"], 2)
    urna = (150, 300, 210, 352)
    t0 = l10["inicio"]
    puntos = [(60, 262), (112, 214), (180, 196), (248, 214), (300, 262)]
    brillo = 0
    for k, (gx, gy) in enumerate(puntos):
        g = SPR_F[2]
        flot = math.sin(t * 2.5 + k) * 3
        pegar(img, g, gx - g.width / 2, gy - g.height + flot)
        tl = t0 + 0.35 + k * 0.42
        tr = t - (tl - 0.35)
        if 0 <= tr < 0.35:
            a = tr / 0.35
            bx = gx + (180 - gx) * a
            by = gy - 10 + (urna[1] - 4 - (gy - 10)) * a - math.sin(a * math.pi) * 40
            d.rectangle([bx - 3, by - 2, bx + 3, by + 2], fill=P["bone"])
        if 0 <= t - tl < 0.12:
            brillo = 1
    d.rectangle(urna, fill=P["bg3"], outline=P["amber"] if brillo else P["bg4"], width=2)
    d.rectangle([168, urna[1] - 2, 192, urna[1] + 2], fill=P["bg0"])
    txt_c(img, "VOTO", 180, urna[1] + 18, P["amber"] if brillo else P["bone_d"], 1)
    return img


def esc_comentario(img, t, L, ctx):
    l = L["K12"]
    img.paste(OSCURO)
    d = ImageDraw.Draw(img)
    txt_c(img, "COMENTA ASÍ:", 180, 132, P["bone"], 2)
    x0, y0, x1, y1 = 30, 168, 330, 232
    d.rectangle([x0 + 3, y0 + 3, x1 + 3, y1 + 3], fill=P["bg0"])
    d.rectangle([x0, y0, x1, y1], fill=P["bg2"], outline=P["bg4"], width=1)
    cab = SPR_H[2][0].crop((0, 0, 22, 14 * 2))
    d.rectangle([x0 + 8, y0 + 10, x0 + 44, y0 + 46], fill=P["bg1"])
    pegar(img, cab, x0 + 15, y0 + 16)
    t_esc = l["tokens"][tk_idx(l, "ENTRO", 1)]["s"]
    palabra = "ENTRO"
    n = int(np.clip((t - t_esc) / 0.09, 0, len(palabra)))
    xs = x0 + 56
    if n:
        s = texto(palabra[:n], P["bone"], 3)
        pegar(img, s, xs, y0 + 16)
        xs += s.width + 6
    if n == len(palabra):
        dt = t - (t_esc + 0.09 * len(palabra))
        ico = ["fuego", "rayo", "estrella"][int(dt / 0.55) % 3]
        pegar(img, SPR_ICO[ico], xs, y0 + 19)
    elif int(t * 4) % 2 == 0:
        d.rectangle([xs, y0 + 16, xs + 2, y0 + 48], fill=P["amber"])
    txt_c(img, "EJEMPLO · TÚ ELIGES EL EMOJI", 180, y1 + 12, P["bone_d"], 1)
    txt_c(img, "EN LOS COMENTARIOS DE ESTE VIDEO", 180, y1 + 28, P["amber"], 1)
    # flecha hacia el botón de comentarios
    if int(t * 3) % 2 == 0:
        fx, fy = 318, 300
        for k in range(6):
            d.line([(fx - k, fy + k), (fx + k, fy + k)], fill=P["amber"])
        d.rectangle([fx - 1, fy - 14, fx + 1, fy], fill=P["amber"])
    return img


def esc_fecha(img, t, L, ctx):
    l = L["K13"]
    img.paste(OSCURO)
    d = ImageDraw.Draw(img)
    t0 = l["inicio"] - 0.12
    caida = np.clip((t - t0) / 0.14, 0, 1)
    oy = int((1 - caida) * -30)
    x0, y0, x1, y1 = 42, 190 + oy, 318, 390 + oy
    d.rectangle([x0 + 4, y0 + 4, x1 + 4, y1 + 4], fill=P["bg0"])
    d.rectangle([x0, y0, x1, y1], fill=P["bg1"], outline=P["bg4"], width=2)
    d.rectangle([x0, y0, x1, y0 + 34], fill=P["red_d"])
    txt_c(img, "CIERRE DE INSCRIPCIONES", 180, y0 + 12, P["bone"], 1)
    if int(t * 2) % 2 == 0:
        d.rectangle([x0 + 10, y0 + 13, x0 + 15, y0 + 18], fill=P["red"])
    fecha, hora, utc = guion.CIERRE_PANTALLA
    if t >= l["tokens"][2]["s"] - 0.05:
        txt_c(img, fecha, 180, y0 + 58, P["bone"], 4, sombra=P["bg0"])
    if t >= l["tokens"][5]["s"] - 0.05:
        txt_c(img, hora, 180, y0 + 120, P["amber"], 2)
    if t >= l["tokens"][6]["s"] - 0.05:
        txt_c(img, utc, 180, y0 + 160, P["bone_d"], 1)
    return img


def sello(img, s, cx, y, ts, t, color):
    if t < ts:
        return
    dt = t - ts
    d = ImageDraw.Draw(img)
    big = dt < 0.08
    sx = int((hsh(int(t * 30), 1) - 0.5) * 4) if dt < 0.2 else 0
    w, h = s.width + 20, s.height + 14
    if big:
        w, h = w + 10, h + 8
    d.rectangle([cx - w // 2 + sx, y, cx + w // 2 + sx, y + h], outline=color, width=3)
    pegar_centrado(img, s, cx + sx + 2, y + (h - s.height) // 2 + 1)


def esc_gratis(img, t, L, ctx):
    l = L["L13"]
    img.paste(OSCURO)
    sello(img, texto("GRATIS", P["amber"], 4), 180, 150, l["tokens"][1]["s"] - 0.05, t, P["amber"])
    sello(img, texto("100% DIGITAL", P["bone"], 3), 180, 244, l["tokens"][5]["s"] - 0.05, t, P["bone"])
    if t > l["tokens"][5]["s"] + 0.35:
        txt_c(img, "SIN COMPRAS · SIN RETOS FÍSICOS", 180, 318, P["bone_d"], 1)
        txt_c(img, "SOLO TU ID. NADA PERSONAL.", 180, 334, P["bone_d"], 1)
    return img


def esc_puertas(img, t, L, ctx):
    l = L["K14"]
    img.paste(SALA[0])
    d = ImageDraw.Draw(img)
    t_abre = l["tokens"][3]["s"]
    luz = np.clip((t - t_abre) / 0.8, 0, 1)
    txt_c(img, "LA PRIMERA PUERTA", 180, 112, P["bone_d"], 1)
    txt_c(img, guion.INICIO_JUEGO1, 180, 128, P["amber"], 3, sombra=P["red_d"])
    for k, cx in enumerate((72, 180, 288)):
        x0, y0, x1, y1 = cx - 34, 196, cx + 34, 388
        d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1], fill=P["bg3"])
        d.rectangle([x0, y0, x1, y1], fill=P["bg2"])
        d.rectangle([x0 + 8, y0 + 10, x1 - 8, y0 + 80], outline=P["bg1"], width=2)
        d.rectangle([x0 + 8, y0 + 96, x1 - 8, y1 - 12], outline=P["bg1"], width=2)
        d.rectangle([x1 - 12, y0 + 86, x1 - 8, y0 + 90], fill=P["amber_d"])
        txt_c(img, "ABC"[k], cx, y0 - 26, P["bone_d"], 2)
        parp = 0.75 + 0.25 * math.sin(t * 13 + k * 2)
        f = (0.35 + 0.65 * luz) * parp
        col = P["amber_l"] if luz > 0.5 else P["amber"]
        d.rectangle([x0, y1 - 2, x1, y1], fill=col)
        for r in range(1, 1 + int(4 + 14 * luz)):
            dens = f * (1 - r / (5 + 14 * luz))
            yy = y1 + r
            for xx in range(x0 - r, x1 + r):
                if 0 <= xx < W and dens > B4[yy % 4][xx % 4]:
                    d.point((xx, yy), fill=P["amber_d"] if r > 3 else col)
    return img


def tk_idx(l, pref, default=0):
    for i, tk in enumerate(l["tokens"]):
        if tk["txt"].upper().startswith(pref):
            return i
    return default


def fondo_rojo():
    base = np.array(fondo_oscuro(0.55, 300)).astype(np.float32)
    base = base * np.array([2.2, 0.7, 0.75]) + np.array([16, 0, 4])
    arr = np.clip(base, 0, 255).astype(np.uint8)
    arr[::4] = (arr[::4].astype(np.float32) * 0.72).astype(np.uint8)   # líneas de barrido
    return Image.fromarray(arr)


ROJO = fondo_rojo()


def hazard(img, y0, h, t, col=None, col2=None):
    col = col or P["red"]
    col2 = col2 or P["bg0"]
    arr = np.array(img)
    xs = np.arange(W)[None, :]
    ys = np.arange(h)[:, None]
    m = (((xs + ys + int(t * 60)) // 8) % 2 == 0)[..., None]
    arr[y0:y0 + h] = np.where(m, np.array(col, np.uint8), np.array(col2, np.uint8))
    return Image.fromarray(arr)


_tj = {}
CARD_X, CARD_Y, CARD_W, CARD_H = 30, 200, 300, 70


def tarjeta(escrito, ico, cursor=False):
    """Tarjeta de comentario (la misma en el primer y en el último fotograma: bucle)."""
    k = (escrito, ico, cursor)
    if k in _tj:
        return _tj[k]
    im = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CARD_W - 1, CARD_H - 1], fill=P["bg2"], outline=P["bg4"])
    d.rectangle([10, 16, 46, 52], fill=P["bg1"])
    cab = SPR_H[2][0].crop((0, 0, 22, 28))
    im.paste(cab, (17, 20), cab)
    x = 58
    if escrito:
        sp = texto(escrito, P["bone"], 3)
        im.paste(sp, (x, 18), sp)
        x += sp.width + 6
    if ico:
        sp = SPR_ICO[ico]
        im.paste(sp, (x, 22), sp)
    if cursor:
        d.rectangle([x, 18, x + 2, 50], fill=P["amber"])
    _tj[k] = im
    return im


def esc_hook(img, t, L, ctx):
    """K01 — gancho: la frase completa está en pantalla desde el fotograma 0."""
    l = L["K01"]
    ts = l["tokens"][3]["s"]                      # "ELIMINARTE."
    f = math.floor(t * FPS)
    antes = t < ts
    img.paste(ROJO)
    img = hazard(img, 108, 10, t)
    img = hazard(img, 420, 10, -t)

    def j(k, a=2):
        return int((hsh(f, k) - 0.5) * 2 * (a if antes else a * 2))

    txt_c(img, "ESTE COMENTARIO", 180 + j(1), 150, P["bone"], 3, sombra=P["red_d"])
    card = tarjeta("ENTRO", "fuego")
    if antes:
        pegar(img, card, CARD_X + j(2), CARD_Y + j(3))
        if int(t * 8) % 2 == 0:
            ImageDraw.Draw(img).rectangle([CARD_X - 3, CARD_Y - 3, CARD_X + CARD_W + 2, CARD_Y + CARD_H + 2],
                                          outline=P["red"], width=2)
    else:
        desintegrar(img, card, CARD_X, CARD_Y, (t - ts) / 0.45, 11, P["red"])
    txt_c(img, "PUEDE", 180 + j(4), 300, P["bone"], 3, sombra=P["red_d"])
    pegar_centrado(img, texto("ELIMINARTE.", P["red"], 4, sombra=P["bg0"]), 180 + j(5, 3), 346)
    if t < 0.35:
        img = glitch_filas(img, f, 14, 5)
    return img


def esc_tease(img, t, L, ctx):
    """K05 — lazo abierto: 'REGLA ?' (se resuelve en K10, REGLA 4)."""
    l = L["K05"]
    t0 = l["inicio"] - 0.12
    f = int(t * FPS)
    img.paste(OSCURO)
    d = ImageDraw.Draw(img)
    txt_c(img, "REGLA", 180, 112, P["bone_d"], 3)
    col = P["red"] if hsh(f // 2, 1) < 0.35 else P["amber"]
    pegar_centrado(img, texto("?", col, 9, sombra=P["red_d"]), 180 + int((hsh(f, 2) - 0.5) * 8), 150)
    d.rectangle([116, 148, 244, 248], outline=P["bg4"], width=2)
    for k in range(4):
        d.rectangle([116 + k * 34, 244, 118 + k * 34, 252], fill=P["bg4"])
    if t - t0 < 0.5:
        img = glitch_filas(img, f, 12, 2)
    return img


def esc_final(img, t, L, ctx):
    """K15 — mismo encuadre que el gancho (bucle): tarjeta en el mismo lugar."""
    l = L["K15"]
    t0 = l["inicio"] - 0.12
    f = int(t * FPS)
    img.paste(ROJO)
    img = hazard(img, 108, 10, t - TL["duracion"])
    img = hazard(img, 420, 10, TL["duracion"] - t)
    txt_c(img, "COMENTA ASÍ", 180, 150, P["bone"], 3, sombra=P["red_d"])
    n = int(np.clip((t - t0) / 0.07, 0, 5))
    ico = ["fuego", "rayo", "estrella"][int((t - t0) / 0.3) % 3] if n == 5 else None
    pegar(img, tarjeta("ENTRO"[:n], ico, cursor=n < 5), CARD_X, CARD_Y)
    pegar_centrado(img, texto("¿ENTRAS?", P["bone"], 6, sombra=P["red_d"]), 180 + (int((hsh(f, 3) - 0.5) * 4) if t - t0 < 0.3 else 0), 300)
    fch, hr, _ = guion.CIERRE_PANTALLA
    txt_c(img, "CIERRA " + fch + " · " + hr, 180, 384, P["amber"], 1)
    txt_c(img, "GRATIS · 100% DIGITAL · PREMIO SIMBÓLICO", 180, 400, P["bone_d"], 1)
    if t - t0 < 0.06:
        img = fundido(img, 0.55, P["bone"])
    if t - t0 < 0.3:
        img = glitch_filas(img, f, 9)
    return img


ESCENAS = {"hook": esc_hook, "derez": esc_multitud, "logo": esc_logo, "conteo": esc_conteo, "tease": esc_tease,
           "id": esc_id, "id_zoom": esc_id, "reglas": esc_reglas, "elecciones": esc_elecciones,
           "fantasma": esc_fantasma, "votos": esc_fantasma, "comentario": esc_comentario, "fecha": esc_fecha,
           "puertas": esc_puertas, "final": esc_final}
SIN_SUBTITULOS = {"hook", "logo", "conteo", "fecha", "final"}
SIN_HUD = {"hook", "derez", "logo", "final", "tease"}
CONTINUAS = {("id", "id_zoom"), ("fantasma", "votos")}
CHIPS = {"id": 1, "id_zoom": 1, "reglas": 2, "elecciones": 3, "fantasma": 4, "votos": 4}
SLAM_Y = {"tease": 292}


# ------------------------------------------------------------------ subtítulos
CAP_CX, CAP_Y, CAP_MAXW = 160, 410, 270


def paginas(linea):
    """Agrupa tokens en páginas de máx. 2 renglones."""
    pags, cur = [], []
    for tk in linea["tokens"]:
        prueba = cur + [tk]
        if len(renglones(prueba)) > 2 and cur:
            pags.append(cur)
            cur = [tk]
        else:
            cur = prueba
    if cur:
        pags.append(cur)
    return pags


def renglones(toks):
    filas, fila = [], []
    for tk in toks:
        prueba = fila + [tk]
        if fuente.ancho_texto(" ".join(x["txt"] for x in prueba), 2) > CAP_MAXW and fila:
            filas.append(fila)
            fila = [tk]
        else:
            fila = prueba
    if fila:
        filas.append(fila)
    return filas


def subtitulos(img, t, lineas):
    for i, l in enumerate(lineas):
        if l["escena"] in SIN_SUBTITULOS:
            continue
        fin_vis = min(l["fin"] + 0.3, lineas[i + 1]["inicio"] - 0.12 if i + 1 < len(lineas) else 1e9)
        if not (l["tokens"][0]["s"] - 0.1 <= t < fin_vis):
            continue
        pags = paginas(l)
        for j, pg in enumerate(pags):
            ini = pg[0]["s"] - 0.1
            fin = pags[j + 1][0]["s"] - 0.1 if j + 1 < len(pags) else fin_vis
            if ini <= t < fin:
                dibujar_pagina(img, pg, t)
        return


def dibujar_pagina(img, pg, t):
    filas = renglones(pg)
    arr = np.array(img)
    y0 = CAP_Y - 6
    y1 = CAP_Y + len(filas) * 26 + 4
    banda = arr[y0:y1, 8:312]
    m = ((np.add.outer(np.arange(y0, y1), np.arange(8, 312)) % 2) == 0)[..., None]
    arr[y0:y1, 8:312] = np.where(m, np.array(P["bg0"], np.uint8), banda // 2)
    img.paste(Image.fromarray(arr))
    for r, fila in enumerate(filas):
        total = fuente.ancho_texto(" ".join(x["txt"] for x in fila), 2)
        x = CAP_CX - total // 2
        y = CAP_Y + r * 26
        for tk in fila:
            if tk["s"] <= t < tk["e"] + 0.05:
                col = P["amber"]
            elif t >= tk["e"]:
                col = P["amber"] if tk["enf"] else P["bone"]
            else:
                col = P["bone_dd"]
            s = texto(tk["txt"], col, 2, sombra=P["bg0"])
            pegar(img, s, x, y)
            x += fuente.ancho_texto(tk["txt"] + " ", 2) + 2


def hud(img, t):
    s = texto("EP.00 · CONVOCATORIA", P["bone_dd"], 1)
    pegar(img, s, 14, 46)
    s2 = texto("INSCRIPCIÓN ABIERTA", P["bone_dd"], 1)
    pegar(img, s2, W - 14 - s2.width, 46)
    if int(t * 2) % 2 == 0:
        ImageDraw.Draw(img).rectangle([W - 22 - s2.width, 48, W - 18 - s2.width, 52], fill=P["red"])


# ------------------------------------------------------------------ fotograma
TL = json.loads((OUT / "timeline.json").read_text())
LINEAS = TL["lineas"]
LMAP = {l["id"]: l for l in LINEAS}
CTX = {}

# eventos de cámara: (tiempo, fuerza, slam)
EVENTOS = []
for _i, _l in enumerate(LINEAS):
    EVENTOS.append((_l["inicio"] - 0.12 if _i else 0.0, 0.07, False))
    for _tk in _l["tokens"]:
        if _tk["slam"]:
            EVENTOS.append((_tk["s"], 0.12, True))
        elif _tk["enf"]:
            EVENTOS.append((_tk["s"], 0.05, False))

CHIP_T0 = {}
for _l in LINEAS:
    _n = CHIPS.get(_l["escena"])
    if _n and _n not in CHIP_T0:
        CHIP_T0[_n] = _l["inicio"] - 0.12


def chip(img, n, t):
    dt = t - CHIP_T0[n]
    e = 4 if dt < 0.1 else 3
    pegar_centrado(img, texto(f"REGLA {n}/4", P["amber"], e, sombra=P["red_d"]), 180, 62)


def slam(img, t, l):
    for tk in l["tokens"]:
        if tk["slam"] and tk["s"] <= t < tk["e"] + 0.5:
            dt = t - tk["s"]
            for e in (7, 6, 5, 4, 3):
                lineas = fuente.partir(tk["txt"], 300, e)
                if len(lineas) <= 2 and all(fuente.ancho_texto(x, e) <= 300 for x in lineas):
                    break
            alto = fuente.H_CELDA * e + 6
            y0 = SLAM_Y.get(l["escena"], 215)
            h = len(lineas) * alto + 24
            arr = np.array(img)
            arr[y0 - 12:y0 - 12 + h] = arr[y0 - 12:y0 - 12 + h] // 5
            img = Image.fromarray(arr)
            col = P["ghost"] if tk["txt"].startswith("NO TE") else P["bone"]
            for k, ln in enumerate(lineas):
                jx = int((hsh(int(t * FPS), k) - 0.5) * 6) if dt < 0.18 else 0
                txt_c(img, ln, 180 + jx, y0 + k * alto, col, e + (1 if dt < 0.06 else 0), sombra=P["red"])
            if dt < 0.05:
                img = fundido(img, 0.45, P["bone"])
    return img


def golpe_camara(img, t):
    k = 0.0
    fuerte = 0.0
    for te, f, sl in EVENTOS:
        dt = t - te
        if 0 <= dt < 0.4:
            k += f * math.exp(-dt / 0.11)
            if sl and dt < 0.16:
                fuerte = max(fuerte, f)
    if k < 0.004:
        return img
    s = 1 + k
    cw, ch = W / s, H / s
    ox = (W - cw) / 2 + ((hsh(int(t * FPS), 8) - 0.5) * 10 * fuerte / 0.12 if fuerte else 0)
    oy = (H - ch) / 2 + ((hsh(int(t * FPS), 9) - 0.5) * 10 * fuerte / 0.12 if fuerte else 0)
    return img.transform((W, H), Image.EXTENT, (ox, oy, ox + cw, oy + ch), Image.NEAREST)


T_FIN = TL["duracion"]


def _zoom(img, k):
    if k < 0.004:
        return img
    s_ = 1 + k
    cw, ch = W / s_, H / s_
    ox, oy = (W - cw) / 2, (H - ch) / 2
    return img.transform((W, H), Image.EXTENT, (ox, oy, ox + cw, oy + ch), Image.NEAREST)


def _post_bucle(img, t, T):
    img = _zoom(img, 0.07 * (t - (T - LOOP_ZOOM)) / LOOP_ZOOM) if t >= T - LOOP_ZOOM else img
    arr = (np.array(img).astype(np.float32) * VIG).astype(np.uint8)
    return Image.fromarray(arr)


LOOP_M = 0.45      # s: el final se transforma en el gancho
LOOP_ZOOM = 0.2    # s: el zoom sube hasta igualar el golpe del fotograma 0


def fotograma(t):
    T = TL["duracion"]
    if t >= T - LOOP_M:
        p = (t - (T - LOOP_M)) / LOOP_M
        if t >= T - 0.12 or hsh(int(t * FPS), 77) < p ** 0.8:
            # el gancho, renderizado con tiempo negativo => continúa sin saltos en t=0
            img = esc_hook(Image.new("RGB", (W, H), P["bg0"]), t - T, LMAP, {})
            return _post_bucle(img, t, T)
    idx = 0
    for i, l in enumerate(LINEAS):
        if t >= (l["inicio"] - 0.12 if i else 0):
            idx = i
    l = LINEAS[idx]
    img = Image.new("RGB", (W, H), P["bg0"])
    img = ESCENAS[l["escena"]](img, t, LMAP, CTX.setdefault(l["escena"], {}))
    if l["escena"] not in SIN_HUD:
        hud(img, t)
    n = CHIPS.get(l["escena"])
    if n:
        chip(img, n, t)
    img = slam(img, t, l)
    subtitulos(img, t, LINEAS)
    # corte con glitch en cambios de escena (salvo continuidad)
    t_ini = l["inicio"] - 0.12
    prev = LINEAS[idx - 1]["escena"] if idx else None
    if idx and (prev, l["escena"]) not in CONTINUAS and 0 <= t - t_ini < 2 / FPS and l["escena"] not in ("logo", "final"):
        img = glitch_filas(img, round(t * FPS), 7, 3)
    img = golpe_camara(img, t)
    if t >= T_FIN - LOOP_ZOOM:
        img = _zoom(img, 0.07 * (t - (T_FIN - LOOP_ZOOM)) / LOOP_ZOOM)
    arr = (np.array(img).astype(np.float32) * VIG).astype(np.uint8)
    return Image.fromarray(arr)


def main():
    if "--fotos" in sys.argv:
        for s in sys.argv[sys.argv.index("--fotos") + 1:]:
            t = float(s)
            fotograma(t).resize((W * ESC, H * ESC), Image.NEAREST).save(OUT / f"preview_{t:05.2f}.png")
        return
    T = TL["duracion"]
    n = int(math.ceil(T * FPS))
    dest = OUT / "episodio0_convocatoria.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(OUT / "audio.wav"),
           "-vf", f"scale={W * ESC}:{H * ESC}:flags=neighbor,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "animation", "-profile:v", "high",
           "-r", str(FPS), "-g", str(FPS * 2), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", str(dest)]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        pr.stdin.write(fotograma(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"  {i}/{n}", flush=True)
    pr.stdin.close()
    pr.wait()
    print("listo:", dest)


if __name__ == "__main__":
    main()

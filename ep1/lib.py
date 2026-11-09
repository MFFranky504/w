import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1920
WW, WH = 2160, 3840
FD = '/usr/share/fonts/opentype/inter/'
def font(s, w='Bold'): return ImageFont.truetype(FD + f'Inter-{w}.otf', s)
def serif(s): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', s)
rng = np.random.default_rng(7)

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x

def text_c(d, xy, s, f, fill=(235, 235, 235), stroke=0, sf=(0, 0, 0), anchor='mm'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)

# ---------- textures ----------
def wood(w, h, plank=120, base=(74, 48, 30), seed=0, vertical=True):
    r = np.random.default_rng(seed)
    if not vertical: w, h = h, w
    x = np.arange(w)[None, :]; y = np.arange(h)[:, None]
    n = w // plank + 2
    pid = x // plank
    nb = r.uniform(.72, 1.15, n)[pid] * np.ones((h, 1))
    ph = r.uniform(0, 100, n)[pid]
    grain = np.sin(y * 0.017 + ph + np.sin(y * 0.004 + ph * 3) * 3 + x * 0.03) * 0.07
    noise = r.random((h, w)) * 0.035 - 0.0175
    gap = ((x % plank) < 5) * -0.55
    f = nb * (1 + grain + noise) + gap
    arr = np.clip(np.array(base)[None, None, :] * f[..., None], 0, 255).astype(np.uint8)
    if not vertical: arr = arr.transpose(1, 0, 2)
    return Image.fromarray(np.ascontiguousarray(arr))

def radial(size, color, power=2.0):
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.clip(1 - np.hypot(x - size / 2, y - size / 2) / (size / 2), 0, 1) ** power
    return (d[..., None] * np.array(color, np.float32)[None, None, :]).astype(np.float32)
GLOW = {'warm': radial(256, (255, 150, 60)), 'red': radial(256, (255, 20, 10)), 'cold': radial(256, (90, 130, 255)), 'white': radial(256, (255, 255, 255))}

def add_glow(arr, sx, sy, rad, kind, k=1.0):
    rad = int(rad)
    if rad < 4: return
    g = np.array(Image.fromarray(np.clip(GLOW[kind], 0, 255).astype(np.uint8)).resize((rad * 2, rad * 2), Image.BILINEAR), np.float32) * k
    x0, y0 = int(sx - rad), int(sy - rad)
    ax0, ay0 = max(0, x0), max(0, y0); ax1, ay1 = min(W, x0 + 2 * rad), min(H, y0 + 2 * rad)
    if ax1 <= ax0 or ay1 <= ay0: return
    arr[ay0:ay1, ax0:ax1] = np.minimum(255, arr[ay0:ay1, ax0:ax1] + g[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0])

def vignette(strength=0.85):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((x - W / 2) / (W * .72), (y - H / 2) / (H * .66))
    return (1 - np.clip(d, 0, 1.2) ** 2.2 * strength)[..., None].astype(np.float32)
VIG = vignette()
GRAIN = [(np.random.default_rng(100 + i).normal(0, 7, (H, W, 1))).astype(np.float32) for i in range(6)]

def lighting(img, lights, amb=0.30, tint=(0.8, 0.9, 1.1)):
    h, w = img.size[1], img.size[0]
    arr = np.array(img, np.float32) * (np.array(tint, np.float32) * amb)[None, None, :]
    y, x = np.mgrid[0:h:4, 0:w:4].astype(np.float32)
    acc = np.zeros((y.shape[0], y.shape[1], 3), np.float32)
    for (lx, ly, r, col, k) in lights:
        d = np.clip(1 - np.hypot(x - lx, y - ly) / r, 0, 1) ** 1.6
        acc += d[..., None] * np.array(col, np.float32)[None, None, :] * k
    acc = np.array(Image.fromarray(np.clip(acc * 100, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 100
    arr = np.array(img, np.float32) * (np.array(tint, np.float32) * amb)[None, None, :] + np.array(img, np.float32) * acc
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

# ---------- flags & characters ----------
def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .4
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)

def flag_img(n, w=340, h=230):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    def vb(c):
        s = w / len(c)
        for i, col in enumerate(c): d.rectangle((i * s, 0, (i + 1) * s + 1, h), fill=col)
    def hb(c, fr=None):
        fr = fr or [1 / len(c)] * len(c); y = 0
        for col, f in zip(c, fr): d.rectangle((0, y, w, y + f * h + 1), fill=col); y += f * h
    WH_ = (255, 255, 255)
    if n == 'mex':
        vb([(0, 104, 71), WH_, (206, 17, 38)]); d.ellipse((w / 2 - 36, h / 2 - 36, w / 2 + 36, h / 2 + 36), fill=(150, 105, 60)); d.arc((w / 2 - 44, h / 2 - 44, w / 2 + 44, h / 2 + 44), 20, 340, fill=(0, 104, 71), width=8)
    elif n == 'gtm':
        vb([(75, 151, 201), WH_, (75, 151, 201)]); d.ellipse((w / 2 - 34, h / 2 - 34, w / 2 + 34, h / 2 + 34), outline=(40, 120, 60), width=9); d.ellipse((w / 2 - 12, h / 2 - 12, w / 2 + 12, h / 2 + 12), fill=(230, 190, 40))
    elif n == 'arg':
        hb([(116, 172, 223), WH_, (116, 172, 223)])
        for i in range(16):
            a = i * math.pi / 8; d.line((w / 2 + 30 * math.cos(a), h / 2 + 30 * math.sin(a), w / 2 + 46 * math.cos(a), h / 2 + 46 * math.sin(a)), fill=(246, 180, 14), width=5)
        d.ellipse((w / 2 - 28, h / 2 - 28, w / 2 + 28, h / 2 + 28), fill=(246, 180, 14))
    elif n == 'chl':
        d.rectangle((0, 0, w, h / 2), fill=WH_); d.rectangle((0, h / 2, w, h), fill=(213, 43, 30)); d.rectangle((0, 0, w / 3, h / 2), fill=(0, 57, 166)); star(d, w / 6, h / 4, 30, WH_)
    elif n == 'per':
        vb([(217, 16, 35), WH_, (217, 16, 35)]); d.rounded_rectangle((w / 2 - 22, h / 2 - 28, w / 2 + 22, h / 2 + 28), 10, fill=(190, 150, 60)); d.rectangle((w / 2 - 22, h / 2 - 28, w / 2, h / 2 + 28), fill=(30, 130, 70))
    elif n == 'pri':
        hb([(237, 41, 57), WH_, (237, 41, 57), WH_, (237, 41, 57)]); d.polygon([(0, 0), (w * .42, h / 2), (0, h)], fill=(0, 80, 239)); star(d, w * .13, h / 2, 26, WH_)
    elif n == 'ven':
        hb([(255, 204, 0), (0, 36, 125), (207, 20, 43)])
        for i in range(8):
            a = math.pi * (0.1 + 0.8 * i / 7); star(d, w / 2 + 90 * math.cos(a + math.pi), h / 2 + 15 - 70 * math.sin(a) * .0 + (-1) * 40 * math.sin(a) + 40, 10, WH_)
    elif n == 'col':
        hb([(255, 205, 0), (0, 48, 135), (206, 17, 38)], [.5, .25, .25])
    elif n == 'ecu':
        hb([(255, 221, 0), (0, 80, 160), (237, 28, 36)], [.5, .25, .25]); d.ellipse((w / 2 - 28, h / 2 - 32, w / 2 + 28, h / 2 + 32), fill=(130, 100, 70))
    elif n == 'slv':
        hb([(15, 71, 175), WH_, (15, 71, 175)]); d.polygon([(w / 2, h / 2 - 34), (w / 2 + 32, h / 2 + 24), (w / 2 - 32, h / 2 + 24)], outline=(60, 130, 60), width=6)
    return im

NAMES = {'mex': 'MÉXICO', 'gtm': 'GUATEMALA', 'arg': 'ARGENTINA', 'chl': 'CHILE', 'per': 'PERÚ', 'pri': 'PUERTO RICO', 'ven': 'VENEZUELA', 'col': 'COLOMBIA', 'ecu': 'ECUADOR', 'slv': 'EL SALVADOR'}
INK = (22, 15, 12)

def char_sprite(n, expr, w=340, h=230, mouth=0.0):
    pad = 34
    S = Image.new('RGBA', (w + 2 * pad, h + 2 * pad + 20), (0, 0, 0, 0))
    sh = Image.new('RGBA', S.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((pad + 10, pad + h - 14, pad + w - 10, pad + h + 30), fill=(0, 0, 0, 150))
    S.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    fl = flag_img(n, w, h).convert('RGBA'); m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=255)
    ov = np.zeros((h, w, 4), np.uint8); yy = np.linspace(0, 1, h)[:, None]; xx = np.linspace(-1, 1, w)[None, :]
    ov[..., 3] = np.clip(yy * 90 + np.abs(xx) ** 3 * 70, 0, 150)
    fl.alpha_composite(Image.fromarray(ov)); fl.putalpha(m); S.alpha_composite(fl, (pad, pad))
    d = ImageDraw.Draw(S); d.rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), 30, outline=(15, 10, 8), width=7)
    ex = [pad + w * .33, pad + w * .67]; ey = pad + h * .40
    for i, cx in enumerate(ex):
        sgn = -1 if i == 0 else 1
        if expr in ('sleep',):
            d.arc((cx - 38, ey - 14, cx + 38, ey + 26), 10, 170, fill=INK, width=8)
        elif expr == 'dead':
            d.line((cx - 24, ey - 24, cx + 24, ey + 24), fill=INK, width=9); d.line((cx - 24, ey + 24, cx + 24, ey - 24), fill=INK, width=9)
        else:
            d.ellipse((cx - 40, ey - 48, cx + 40, ey + 48), fill=(246, 246, 240), outline=INK, width=6)
            px = cx + (sgn * -6 if expr in ('worried', 'angry') else 0); py = ey + (14 if expr == 'sad' else 6)
            d.ellipse((px - 17, py - 17, px + 17, py + 17), fill=INK); d.ellipse((px - 9, py - 12, px - 1, py - 4), fill=(255, 255, 255))
            if expr == 'sad': d.pieslice((cx - 42, ey - 50, cx + 42, ey + 46), 180, 360, fill=(30, 22, 20))
            if expr == 'angry': d.polygon([(cx - 46, ey - 60 + (30 if sgn < 0 else 0)), (cx + 46, ey - 60 + (0 if sgn < 0 else 30)), (cx + 46, ey - 20), (cx - 46, ey - 20)], fill=(30, 22, 20)); d.line((cx - 46, ey - 62 + (34 if sgn < 0 else 0), cx + 46, ey - 62 + (0 if sgn < 0 else 34)), fill=INK, width=12)
            if expr == 'worried': d.line((cx - 40, ey - 70 + (-8 if sgn < 0 else 14), cx + 40, ey - 70 + (14 if sgn < 0 else -8)), fill=INK, width=10)
            if expr == 'sad': d.line((cx - 40, ey - 62 + (14 if sgn < 0 else -4), cx + 40, ey - 62 + (-4 if sgn < 0 else 14)), fill=INK, width=10)
    my = pad + h * .74; mx = pad + w / 2
    if mouth > 0.05: d.ellipse((mx - 32, my - 10, mx + 32, my - 10 + 14 + 44 * mouth), fill=(40, 12, 14), outline=INK, width=6)
    elif expr in ('sad', 'worried', 'angry', 'dead'): d.arc((mx - 34, my - 4, mx + 34, my + 34), 200, 340, fill=INK, width=8)
    else: d.line((mx - 28, my + 8, mx + 28, my + 8), fill=INK, width=8)
    return S

SPR = {}
def spr(n, expr, mouth=0.0):
    k = (n, expr, round(mouth * 4))
    if k not in SPR: SPR[k] = char_sprite(n, expr, mouth=round(mouth * 4) / 4)
    return SPR[k]

# ---------- object sprites ----------
def steel(w, h, a=(170, 178, 188), b=(80, 86, 96)):
    y = np.linspace(0, 1, h)[:, None, None]
    return Image.fromarray((np.array(a)[None, None, :] * (1 - y) + np.array(b)[None, None, :] * y).repeat(w, 1).astype(np.uint8))

def obj_axe():
    S = Image.new('RGBA', (1000, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    hd = wood(700, 60, 700, (112, 74, 40), 3, False).convert('RGBA'); hm = Image.new('L', hd.size, 0); ImageDraw.Draw(hm).rounded_rectangle((0, 0, 699, 59), 22, fill=255); hd.putalpha(hm); S.alpha_composite(hd, (40, 230))
    head = Image.new('RGBA', (300, 400)); st = steel(300, 400).convert('RGBA'); mk = Image.new('L', (300, 400), 0)
    ImageDraw.Draw(mk).polygon([(0, 110), (150, 90), (230, 10), (290, 200), (230, 390), (150, 310), (0, 290)], fill=255); st.putalpha(mk); S.alpha_composite(st, (650, 55))
    d.polygon([(880, 66), (940, 200), (880, 355), (900, 345), (950, 200), (895, 55)], fill=(225, 232, 240)); d.line((650, 165, 800, 150), fill=(40, 44, 52), width=5)
    d.rectangle((640, 215, 700, 305), fill=(40, 28, 20)); d.polygon([(650, 55), (800, 40), (880, 66)], outline=(30, 32, 38), fill=None)
    for i in range(6): d.line((60 + i * 110, 238, 90 + i * 110, 290), fill=(70, 44, 24), width=3)
    return S

def obj_lighter():
    S = Image.new('RGBA', (800, 480), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    b = steel(740, 440, (205, 208, 214), (96, 100, 108)).convert('RGBA'); m = Image.new('L', b.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 739, 439), 46, fill=255); b.putalpha(m); S.alpha_composite(b, (30, 20))
    d.line((40, 170, 760, 170), fill=(60, 62, 68), width=6); d.rounded_rectangle((300, 4, 520, 40), 10, fill=(130, 134, 142), outline=(50, 52, 58), width=4)
    for i, (cx, cy, r) in enumerate([(400, 110, 22)]): d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 62, 68), width=5)
    for off, col in ((3, (240, 242, 246)), (0, (62, 64, 72))): text_c(d, (400, 320 + off), 'UNA SOLA CHISPA', font(66, 'ExtraBold'), col)
    rr = np.random.default_rng(3)
    for _ in range(40):
        x = int(rr.integers(60, 700)); y = int(rr.integers(190, 430)); d.line((x, y, x + int(rr.integers(10, 50)), y + int(rr.integers(-8, 8))), fill=(60, 64, 70, 90), width=2)
    return S

def obj_knife():
    S = Image.new('RGBA', (1000, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    bl = steel(660, 120, (200, 206, 214), (110, 116, 126)).convert('RGBA'); m = Image.new('L', bl.size, 0); ImageDraw.Draw(m).polygon([(0, 8), (560, 0), (655, 70), (0, 118)], fill=255); bl.putalpha(m); S.alpha_composite(bl, (330, 70))
    d.line((340, 80, 900, 72), fill=(240, 244, 250), width=4)
    hd = wood(360, 110, 360, (60, 38, 26), 5, False).convert('RGBA'); hm = Image.new('L', hd.size, 0); ImageDraw.Draw(hm).rounded_rectangle((0, 0, 359, 109), 40, fill=255); hd.putalpha(hm); S.alpha_composite(hd, (10, 75))
    for cx in (80, 170, 260): d.ellipse((cx - 11, 118, cx + 11, 140), fill=(170, 150, 90), outline=(40, 30, 20), width=3)
    return S

def hatch(d, box, step=14, col=(70, 50, 35), w=2):
    x0, y0, x1, y1 = box
    for k in range(-(y1 - y0), x1 - x0, step): d.line((x0 + k, y1, x0 + k + (y1 - y0), y0), fill=col, width=w)

def obj_map():
    Wd, Ht = 820, 1120
    r = np.random.default_rng(9)
    yy, xx = np.mgrid[0:Ht, 0:Wd].astype(np.float32)
    edge = np.minimum(np.minimum(xx, Wd - xx), np.minimum(yy, Ht - yy)); f = 0.55 + 0.45 * np.clip(edge / 70, 0, 1)
    base = np.array([214, 192, 146], np.float32)[None, None, :] * f[..., None] * (0.95 + 0.1 * r.random((Ht, Wd, 1)))
    P = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(P)
    ink = (62, 42, 26)
    text_c(d, (410, 70), 'CABAÑA', serif(54), ink); d.line((200, 118, 620, 118), fill=ink, width=4)
    d.rectangle((110, 190, 710, 720), outline=ink, width=8)
    d.rectangle((112, 192, 708, 226), fill=(190, 168, 124)); hatch(d, (112, 192, 708, 226), 12, ink, 2)  # muro norte piedra
    d.rectangle((130, 226, 300, 350), outline=ink, width=6); hatch(d, (132, 228, 298, 348), 18, ink, 2); text_c(d, (215, 392), 'CHIMENEA', font(32, 'Bold'), ink)
    xc, yc = 352, 262
    d.line((xc - 24, yc - 24, xc + 24, yc + 24), fill=(165, 22, 22), width=11); d.line((xc - 24, yc + 24, xc + 24, yc - 24), fill=(165, 22, 22), width=11)
    d.rectangle((300, 715, 520, 726), fill=(214, 192, 146)); text_c(d, (410, 760), 'PUERTA', font(30, 'Bold'), ink)
    d.rectangle((706, 380, 714, 540), fill=(110, 140, 170)); text_c(d, (640, 430), 'VENTANA', font(26, 'Bold'), ink)
    d.rectangle((400, 560, 580, 660), outline=ink, width=5); text_c(d, (490, 610), 'MESA', font(28, 'Bold'), ink)
    d.polygon([(660, 100), (640, 150), (680, 150)], fill=ink); text_c(d, (660, 170), 'N', font(30, 'Bold'), ink)
    d.rectangle((90, 850, 730, 1060), outline=ink, width=5)
    d.rectangle((120, 885, 190, 925), fill=(190, 168, 124), outline=ink, width=3); hatch(d, (121, 886, 189, 924), 12, ink, 2); text_c(d, (210, 905), 'PIEDRA · 40 cm', font(34, 'Bold'), ink, anchor='lm')
    d.rectangle((120, 955, 190, 995), fill=(150, 112, 70), outline=ink, width=3); text_c(d, (210, 975), 'MADERA · 5 cm', font(34, 'Bold'), ink, anchor='lm')
    d.line((120, 1030, 700, 1030), fill=ink, width=2)
    return P

def obj_candles():
    S = Image.new('RGBA', (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    d.ellipse((30, 520, 870, 620), fill=(80, 82, 90), outline=(30, 30, 34), width=6); d.ellipse((60, 530, 840, 600), fill=(112, 116, 126))
    for i, hh in enumerate([300, 380, 250, 340, 280]):
        cx = 120 + i * 165; top = 560 - hh
        d.rounded_rectangle((cx - 48, top, cx + 48, 570), 18, fill=(232, 220, 190), outline=(120, 108, 84), width=5)
        d.rectangle((cx - 44, top + 8, cx - 22, 566), fill=(248, 238, 214))
        d.ellipse((cx - 30, top + 40, cx - 10, top + 100), fill=(240, 230, 200)); d.line((cx, top, cx, top - 38), fill=(25, 20, 18), width=6)
    return S

def obj_logs(dry):
    S = Image.new('RGBA', (1000, 620), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    base = (196, 156, 106) if dry else (66, 46, 34)
    for i, (y, x0, x1) in enumerate([(430, 80, 900), (250, 150, 960), (80, 60, 880)]):
        hh = 150
        lg = wood(x1 - x0, hh, x1 - x0, base, 11 + i, False).convert('RGBA'); m = Image.new('L', lg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, lg.size[0] - 1, hh - 1), 55, fill=255); lg.putalpha(m); S.alpha_composite(lg, (x0, y + 10))
        d.ellipse((x1 - 70, y + 10, x1 + 10, y + hh + 10), fill=tuple(int(c * 1.25) for c in base) + (255,), outline=(30, 20, 14), width=5)
        for r_ in (14, 30): d.ellipse((x1 - 30 - r_, y + hh / 2 + 10 - r_, x1 - 30 + r_, y + hh / 2 + 10 + r_), outline=(80, 56, 34), width=3)
        if dry:
            for _ in range(4): xx_ = int(np.random.default_rng(i * 9 + _).integers(x0 + 40, x1 - 100)); d.line((xx_, y + 30, xx_ + 40, y + 120), fill=(110, 80, 50), width=3)
        else:
            for _ in range(14):
                xx_ = int(np.random.default_rng(i * 31 + _).integers(x0 + 30, x1 - 60)); yy_ = y + 20 + int(np.random.default_rng(i * 17 + _).integers(0, 120)); d.ellipse((xx_, yy_, xx_ + 12, yy_ + 20), fill=(150, 190, 220, 200))
            d.ellipse((x0 + 100, y + 30, x0 + 300, y + 80), fill=(52, 84, 52, 140))
    return S

def obj_wallicon():
    S = Image.new('RGB', (420, 360), (64, 64, 70)); d = ImageDraw.Draw(S); r = np.random.default_rng(2)
    for row in range(6):
        x = -r.integers(0, 60)
        while x < 420:
            wd = int(r.integers(90, 150)); c = int(r.integers(70, 105)); d.rectangle((x, row * 60, x + wd, row * 60 + 56), fill=(c, c, c + 6), outline=(36, 36, 40), width=3); x += wd + 4
    return S

OBJ = {}
def objs():
    if not OBJ:
        OBJ.update(axe=obj_axe(), lighter=obj_lighter(), knife=obj_knife(), map=obj_map(), candles=obj_candles(), wet=obj_logs(False), dry=obj_logs(True), wall=obj_wallicon())
    return OBJ

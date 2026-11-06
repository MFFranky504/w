"""TU CONF.IA - motor pixel-art. Mundo lógico 160x284 px (se escala x8 -> 1280x2272, cámara 1080x1920)."""
import numpy as np, math, random
from PIL import Image, ImageDraw

WW, WH = 160, 284
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16
BAY = np.tile(B4, (WH // 4 + 1, WW // 4 + 1))[:WH, :WW]
YY, XX = np.mgrid[0:WH, 0:WW]
OUT = (16, 12, 28)


def C(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    if isinstance(c, str): c = C(c)
    return tuple(max(0, min(255, int(v * f))) for v in c)


def vgrad(stops):
    ys = np.linspace(0, 1, WH)
    cols = np.array([C(c) for _, c in stops], float)
    pos = np.array([p for p, _ in stops])
    arr = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], -1)
    return np.repeat(arr[:, None, :], WW, 1)


def outline(im, col=OUT):
    a = np.array(im)
    al = a[..., 3] > 0
    p = np.pad(al, 1)
    d = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    pa = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    edge = d & ~np.pad(al, 1)[1:-1, 1:-1] if False else None
    al_p = np.pad(al, 1)
    dil = np.zeros_like(al_p)
    dil[:-1] |= al_p[1:]; dil[1:] |= al_p[:-1]; dil[:, :-1] |= al_p[:, 1:]; dil[:, 1:] |= al_p[:, :-1]
    edge = dil & ~al_p
    out = pa.copy()
    out[edge] = (*col, 255)
    return Image.fromarray(out.astype('uint8'), 'RGBA')


class Canvas:
    def __init__(s, bg):
        s.im = Image.fromarray(np.clip(bg, 0, 255).astype('uint8')).convert('RGBA')
        s.d = ImageDraw.Draw(s.im)
        s.emis = Image.new('RGBA', (WW, WH), (0, 0, 0, 0))
        s.ed = ImageDraw.Draw(s.emis)
        s.lights = []
        s.amb = (1, 1, 1)
        s.vig = 0.0

    def R(s, x, y, w, h, c, d=None):
        (d or s.d).rectangle([x, y, x + w - 1, y + h - 1], fill=c)

    def blit(s, sp, x, y, flip=False, ol=True, tint=None):
        if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        if ol: sp = outline(sp)
        if tint is not None:
            a = np.array(sp).astype(float)
            m = a[..., 3] > 0
            a[m, :3] = np.array(tint)
            sp = Image.fromarray(a.astype('uint8'), 'RGBA')
        o = 1 if ol else 0
        s.im.paste(sp, (int(x) - o, int(y) - o), sp)

    def light(s, x, y, rx, ry, col, k=1.0):
        s.lights.append((x, y, rx, ry, col, k))

    def render(s):
        arr = np.array(s.im.convert('RGB')).astype(float) * np.array(s.amb)
        for x, y, rx, ry, col, k in s.lights:
            dd = np.sqrt(((XX - x) / rx) ** 2 + ((YY - y) / ry) ** 2)
            f = np.clip(1 - dd, 0, 1) ** 1.6 * k
            arr += f[..., None] * np.array(col, float)
        e = np.array(s.emis).astype(float)
        al = e[..., 3:4] / 255
        arr = arr * (1 - al) + e[..., :3] * al
        if s.vig:
            dd = np.sqrt(((XX - 80) / 95) ** 2 + ((YY - 142) / 160) ** 2)
            arr *= (1 - s.vig * np.clip(dd - 0.35, 0, 1) ** 1.4)[..., None]
        lv = 255 / 31
        arr = np.floor(arr / lv + BAY[..., None]) * lv
        return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


# ---------------------------------------------------------------- fuente pixel 3x5
G = {
    'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
    'E': '111100110100111', 'G': '011100101101011', 'H': '101101111101101', 'I': '111010010010111',
    'K': '101101110101101', 'L': '100100100100111', 'M': '101111111101101', 'N': '111101101101101',
    'O': '010101101101010', 'P': '110101110100100', 'R': '110101110101101', 'S': '011100010001110',
    'T': '111010010010010', 'U': '101101101101111', '0': '111101101101111', '1': '010110010010111',
    '2': '110001010100111', '3': '110001010001110', '4': '101101111001001', '5': '111100110001110',
    '6': '011100111101111', '7': '111001010100100', '8': '111101111101111', '9': '111101111001110',
    '$': '011110111011110', '.': '000000000000010', ',': '000000000000010', ' ': '0' * 15,
}


def ptext(d, x, y, txt, col, k=1, sh=None):
    cx = x
    for ch in txt.upper():
        g = G.get(ch, G[' '])
        for i, b in enumerate(g):
            if b == '1':
                px, py = cx + (i % 3) * k, y + (i // 3) * k
                if sh: d.rectangle([px + k, py + k, px + 2 * k - 1, py + 2 * k - 1], fill=sh)
        for i, b in enumerate(g):
            if b == '1':
                px, py = cx + (i % 3) * k, y + (i // 3) * k
                d.rectangle([px, py, px + k - 1, py + k - 1], fill=col)
        cx += 4 * k
    return cx


def ptext_w(txt, k=1): return len(txt) * 4 * k - k


# ---------------------------------------------------------------- personajes
def person(skin='#e0b28c', hair='#1c1820', top='#aa3c32', top2=None, pants='#34507f', shoes='#2a2026',
           glasses=False, long=False, tie=None, cap=None, apron=None, expr='n', arm_l=None, arm_r=None,
           legs=True, skirt=False, wide=False):
    im = Image.new('RGBA', (28, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R = lambda x, y, w, h, c: d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)
    sk = C(skin); skd = shade(skin, .82)
    if legs:
        if skirt:
            R(8, 28, 12, 9, pants); R(8, 36, 12, 1, shade(pants, .8)); R(9, 37, 4, 8, skin); R(15, 37, 4, 8, skin)
            R(8, 45, 5, 3, shoes); R(15, 45, 5, 3, shoes)
        else:
            R(9, 30, 5, 15, pants); R(14, 30, 5, 15, pants); R(13, 30, 1, 15, shade(pants, .7)); R(17, 30, 2, 15, shade(pants, .85))
            R(8, 45, 6, 3, shoes); R(14, 45, 6, 3, shoes)
    # torso
    R(8, 14, 12, 17, top)
    R(17, 14, 3, 17, shade(top, .8))
    if top2:
        for yy in range(15, 31, 4): R(8, yy, 12, 1, top2)
        for xx in range(9, 20, 4): R(xx, 14, 1, 17, top2)
    if apron:
        R(10, 20, 8, 11, apron); R(10, 20, 8, 1, shade(apron, 1.2))
    R(12, 12, 4, 3, skd)
    R(12, 14, 4, 1, '#f0f0f0')
    if tie: R(13, 15, 2, 9, tie); R(13, 15, 2, 1, shade(tie, 1.3))
    # arms
    for pts, base in ((arm_l or [(9, 16), (6, 22), (6, 29)], 'l'), (arm_r or [(19, 16), (22, 22), (22, 29)], 'r')):
        d.line(pts, fill=top, width=3)
        hx, hy = pts[-1]
        R(hx - 1, hy - 1, 3, 3, skin)
    # head
    hairc = C(hair)
    if long:
        R(7, 4, 3, 16, hairc); R(18, 4, 3, 16, hairc); R(8, 18, 12, 2, hairc)
    R(7, 0, 14, 4, hairc); R(6, 2, 2, 6, hairc); R(20, 2, 2, 6, hairc)
    R(9, 3, 10, 9, skin)
    R(18, 4, 1, 8, skd)
    R(9, 3, 10, 2, hairc)
    R(9, 5, 2, 1, hairc) if not long else None
    R(7, 0, 14, 1, shade(hair, 1.4))
    if cap:
        R(7, 0, 14, 3, cap); R(6, 2, 16, 2, shade(cap, .8)); R(16, 3, 7, 1, shade(cap, .7))
    # cara
    ey = 7
    if glasses:
        d.rectangle([9, 6, 13, 9], outline=(24, 22, 34)); d.rectangle([15, 6, 19, 9], outline=(24, 22, 34)); R(14, 7, 1, 1, (24, 22, 34))
        R(10, 7, 2, 2, (250, 250, 255)); R(16, 7, 2, 2, (250, 250, 255))
    R(11, ey, 1, 2, (28, 24, 40)); R(17, ey, 1, 2, (28, 24, 40))
    if expr == 'sad':
        R(10, 5, 3, 1, hairc); R(16, 5, 3, 1, hairc); R(12, 11, 4, 1, (150, 80, 72))
    elif expr == 'smile':
        R(12, 10, 4, 1, (150, 80, 72)); R(11, 9, 1, 1, (150, 80, 72)); R(16, 9, 1, 1, (150, 80, 72))
    else:
        R(12, 10, 4, 1, (160, 88, 76))
    return im


KING = dict(skin='#e2b48e', hair='#17141c', top='#b2443a', top2='#6a2428', pants='#3a5688', shoes='#2a2026', glasses=True)
KING_T = dict(skin='#e2b48e', hair='#17141c', top='#cfc8b8', pants='#5a4a3a', shoes='#2a2026', glasses=True, tie='#2c4c7c')
TAB = dict(skin='#eec0a0', hair='#6a3c28', top='#d6a03c', pants='#3c5c78', shoes='#4a2c28', long=True, expr='n')
TAB_UNI = dict(skin='#eec0a0', hair='#6a3c28', top='#f06a98', apron='#ffb070', pants='#f3f3f3', shoes='#c8c8c8', long=False, cap='#f06a98')


# ---------------------------------------------------------------- retrato grande (64x84)
def portrait(who='king', expr='n', look=(0, 0), blink=False, top=None, w=72, h=92):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w // 2
    if who == 'king':
        skin, skd, hair, tp, tp2 = C('#e2b48e'), C('#bf8a6a'), C('#17141c'), C('#b2443a'), C('#6a2428')
    else:
        skin, skd, hair, tp, tp2 = C('#eec0a0'), C('#c89878'), C('#6a3c28'), C('#d6a03c'), C('#a67a24')
    if top: tp = C(top)
    # hombros
    d.polygon([(2, h), (6, h - 20), (cx - 12, h - 26), (cx + 12, h - 26), (w - 6, h - 20), (w - 2, h)], fill=tp)
    for yy in range(h - 24, h, 4): d.line([(5, yy), (w - 5, yy)], fill=tp2) if who == 'king' else None
    if who == 'king':
        for xx in range(8, w - 6, 6): d.line([(xx, h - 22), (xx, h)], fill=tp2)
    d.polygon([(cx - 12, h - 26), (cx + 12, h - 26), (cx, h - 16)], fill=shade(tp, .7))
    d.rectangle([cx - 6, h - 36, cx + 6, h - 24], fill=skd)  # cuello
    if who == 'tab':  # pelo largo detrás
        d.polygon([(cx - 22, 20), (cx - 26, h - 22), (cx + 26, h - 22), (cx + 22, 20)], fill=hair)
    # cara
    d.rounded_rectangle([cx - 17, 14, cx + 17, 62], radius=13, fill=skin)
    d.polygon([(cx + 8, 20), (cx + 17, 24), (cx + 17, 50), (cx + 12, 58), (cx + 6, 60)], fill=skd)
    d.rectangle([cx - 19, 36, cx - 17, 43], fill=skin); d.rectangle([cx + 17, 36, cx + 19, 43], fill=skd)  # orejas
    # pelo
    if who == 'king':
        d.polygon([(cx - 20, 34), (cx - 19, 16), (cx - 10, 7), (cx, 4), (cx + 12, 7), (cx + 20, 16), (cx + 19, 34), (cx + 15, 24), (cx + 4, 18), (cx - 8, 20), (cx - 16, 26)], fill=hair)
        d.polygon([(cx - 6, 4), (cx - 2, -0), (cx + 4, 5)], fill=hair)
        d.line([(cx - 12, 9), (cx + 6, 7)], fill=shade('#17141c', 2.4), width=1)
    else:
        d.polygon([(cx - 21, 40), (cx - 20, 16), (cx - 8, 6), (cx + 6, 6), (cx + 19, 16), (cx + 21, 40), (cx + 17, 26), (cx + 2, 17), (cx - 6, 19), (cx - 17, 28)], fill=hair)
        d.line([(cx - 10, 9), (cx + 8, 9)], fill=shade('#6a3c28', 1.6), width=1)
    # ojos
    ex = [cx - 9, cx + 9]
    ey = 38
    lx, ly = look
    for e in ex:
        if blink:
            d.line([(e - 4, ey + 1), (e + 4, ey + 1)], fill=(40, 28, 36), width=1)
        else:
            d.rectangle([e - 4, ey - 2, e + 4, ey + 2], fill=(250, 248, 250))
            d.rectangle([e - 1 + lx, ey - 2 + ly // 2 + 0, e + 2 + lx, ey + 2], fill=(52, 84, 140) if who == 'king' else (84, 52, 36))
            d.rectangle([e + lx, ey - 1, e + 1 + lx, ey + 1], fill=(14, 12, 22))
            d.point((e + 1 + lx, ey - 1), fill=(255, 255, 255))
            d.line([(e - 4, ey - 3), (e + 4, ey - 3)], fill=(60, 40, 40))
    # cejas
    bc = hair
    if expr == 'sad':
        d.line([(ex[0] - 5, ey - 6), (ex[0] + 4, ey - 9)], fill=bc, width=2); d.line([(ex[1] - 4, ey - 9), (ex[1] + 5, ey - 6)], fill=bc, width=2)
    elif expr == 'wow':
        d.line([(ex[0] - 4, ey - 10), (ex[0] + 4, ey - 10)], fill=bc, width=2); d.line([(ex[1] - 4, ey - 10), (ex[1] + 4, ey - 10)], fill=bc, width=2)
    else:
        d.line([(ex[0] - 5, ey - 7), (ex[0] + 4, ey - 7)], fill=bc, width=2); d.line([(ex[1] - 4, ey - 7), (ex[1] + 5, ey - 7)], fill=bc, width=2)
    if who == 'king':
        for e in ex: d.rectangle([e - 7, ey - 5, e + 7, ey + 5], outline=(22, 20, 32))
        d.line([(ex[0] + 7, ey - 1), (ex[1] - 7, ey - 1)], fill=(22, 20, 32))
        d.line([(ex[0] - 7, ey - 3), (ex[0] - 14, ey - 4)], fill=(22, 20, 32)); d.line([(ex[1] + 7, ey - 3), (ex[1] + 14, ey - 4)], fill=(22, 20, 32))
    # nariz
    d.line([(cx + 1, 44), (cx + 3, 49)], fill=skd, width=1); d.line([(cx - 1, 50), (cx + 3, 50)], fill=skd)
    # boca
    my = 55
    if expr == 'sad':
        d.line([(cx - 5, my + 2), (cx - 1, my), (cx + 4, my), (cx + 6, my + 2)], fill=(150, 80, 72))
    elif expr == 'smile':
        d.line([(cx - 6, my - 1), (cx - 3, my + 2), (cx + 3, my + 2), (cx + 6, my - 1)], fill=(160, 76, 70), width=1)
        d.line([(cx - 3, my + 1), (cx + 3, my + 1)], fill=(250, 244, 244))
    elif expr == 'wow':
        d.ellipse([cx - 3, my - 1, cx + 3, my + 4], fill=(120, 50, 56))
    else:
        d.line([(cx - 5, my), (cx + 5, my)], fill=(160, 84, 76))
    return im


# ---------------------------------------------------------------- props
def paper_ball(s=6, col=(238, 236, 228)):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=col)
    d.point((1, 2), fill=shade(col, .78)); d.point((3, 3), fill=shade(col, .7)); d.point((2, s - 2), fill=shade(col, .85)); d.point((s - 2, 1), fill=(255, 255, 255))
    return im


def trash_can(w=24, h=28):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([1, 4, w - 2, h - 1], fill=(112, 120, 142))
    d.rectangle([w - 7, 4, w - 2, h - 1], fill=(82, 88, 108))
    d.rectangle([2, 4, 4, h - 1], fill=(150, 158, 178))
    for yy in (9, 15, 21): d.line([(1, yy), (w - 2, yy)], fill=(70, 76, 96))
    d.rectangle([0, 2, w - 1, 4], fill=(140, 148, 168)); d.rectangle([0, 4, w - 1, 4], fill=(90, 96, 116))
    return im


def stack_pages(n=3, w=13, h=9):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(n): d.rectangle([0, h - 3 - i * 2, w - 1, h - 1 - i * 2], fill=(244, 242, 232), outline=(180, 176, 168))
    return im


def typewriter():
    im = Image.new('RGBA', (22, 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([2, 5, 19, 13], fill=(70, 96, 90)); d.rectangle([2, 5, 19, 6], fill=(110, 140, 130))
    d.rectangle([0, 11, 21, 13], fill=(52, 72, 70))
    for xx in range(4, 18, 2): d.point((xx, 9), fill=(220, 220, 210)); d.point((xx, 11), fill=(200, 200, 190))
    d.rectangle([1, 3, 20, 4], fill=(40, 52, 52))
    return im


def book(w=34, h=48, title='CARRIE'):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(150, 20, 34))
    d.rectangle([0, 0, 3, h - 1], fill=(100, 12, 24)); d.rectangle([w - 3, 0, w - 1, h - 1], fill=(190, 40, 52))
    d.rectangle([5, 4, w - 5, 6], fill=(20, 10, 16))
    ptext(d, 6, 12, title, (250, 232, 220), 1) if len(title) <= 6 else None
    d.ellipse([w // 2 - 7, 26, w // 2 + 5, 42], fill=(24, 8, 14)); d.rectangle([w // 2 - 4, 30, w // 2 + 2, 34], fill=(200, 40, 50))
    return im


def pine(h=40, snow=True):
    w = int(h * 0.62) // 2 * 2 + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tiers = 4
    for i in range(tiers):
        y0 = int(i * (h - 6) / tiers) + 1
        hw = int((i + 1.4) / (tiers + .4) * w / 2)
        d.polygon([(w // 2, y0), (w // 2 - hw, y0 + (h - 6) // tiers + 5), (w // 2 + hw, y0 + (h - 6) // tiers + 5)], fill=(20, 58, 56))
        d.polygon([(w // 2, y0), (w // 2 + hw, y0 + (h - 6) // tiers + 5), (w // 2 + hw // 3, y0 + (h - 6) // tiers + 5)], fill=(14, 40, 44))
        if snow: d.polygon([(w // 2, y0), (w // 2 - hw // 2, y0 + 5), (w // 2 + hw // 2, y0 + 5)], fill=(214, 226, 246))
    d.rectangle([w // 2 - 1, h - 5, w // 2 + 1, h - 1], fill=(60, 36, 32))
    return im


def trailer(w=84, h=44):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 8], radius=9, fill=(214, 206, 186))
    d.rectangle([0, h - 20, w - 1, h - 8], fill=(214, 206, 186))
    d.rectangle([0, h - 20, w - 1, h - 15], fill=(52, 128, 140))  # franja
    d.rectangle([0, h - 10, w - 1, h - 8], fill=(150, 144, 128))
    d.rectangle([0, 2, w - 1, 4], fill=(236, 232, 214))  # brillo techo
    d.rectangle([w - 4, 6, w - 1, h - 9], fill=(170, 164, 148))
    d.rectangle([w - 7, h - 8, w - 1, h - 1], fill=(40, 32, 40))  # skirting oscuro
    d.rectangle([0, h - 7, w - 8, h - 1], fill=(60, 54, 60))
    for xx in (8, 16, 52, 62): d.ellipse([xx, h - 8, xx + 8, h], fill=(20, 18, 24)); d.ellipse([xx + 2, h - 6, xx + 6, h - 2], fill=(90, 90, 100))
    d.rectangle([3, 5, 10, 8], fill=(150, 144, 128))
    return im


# ---------------------------------------------------------------- partículas
def rain(c, t, n=70, seed=1, speed=150, col=(150, 176, 220), x0=-10, x1=WW + 10, y1=WH):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1); y0 = rnd.uniform(0, WH); sp = speed * rnd.uniform(.8, 1.2)
        y = (y0 + t * sp) % (WH + 20) - 10
        xx = x - y * 0.18
        c.d.line([(xx, y), (xx - 1, y + 3)], fill=col)


def snow(c, t, n=90, seed=2, col=(236, 242, 255)):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(0, WW); y0 = rnd.uniform(0, WH); sp = rnd.uniform(10, 24); ph = rnd.uniform(0, 6.28)
        y = (y0 + t * sp) % WH
        xx = x + math.sin(t * 1.3 + ph) * 3
        c.d.point((xx, y), fill=col)
        if i % 5 == 0: c.d.point((xx + 1, y), fill=col)


def stars(c, t, n=70, seed=3, ymax=140):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.randrange(WW); y = rnd.randrange(ymax); ph = rnd.uniform(0, 6.28)
        v = 0.6 + 0.4 * math.sin(t * 2 + ph)
        col = tuple(int(200 * v + 40) for _ in range(3))
        c.d.point((x, y), fill=col)
        if i % 9 == 0: c.d.point((x + 1, y), fill=col); c.d.point((x, y + 1), fill=col)


def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)

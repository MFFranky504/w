"""Chibi pixel-art sprite + idle animation (hand-built, no AI)."""
import numpy as np
from PIL import Image

S = 1.5                      # design units -> final pixels
W, H = 96, 120
yy, xx = np.mgrid[0:H, 0:W]
X = (xx + 0.5) / S           # design-space coords of pixel centres
Y = (yy + 0.5) / S


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], dtype=np.uint8)


P = {k: hexc(v) for k, v in dict(
    ol='#1c1229',
    c_hi='#effeff', c_lt='#8cf3ff', c_b='#4fd9f3', c_sh='#35b2e6', c_dk='#2a86c9', c_line='#1b5a92',
    p_hi='#ffd9d0', p_lt='#ffbcb1', p_b='#f6a196', p_sh='#e07f7c', p_dk='#b85a63', white='#ffffff',
    h_lt='#a8653a', h_b='#71401f', h_sh='#4f2a15', h_line='#2e170c',
    s_lt='#ffe2c8', s_b='#f8c49c', s_sh='#e39b78', s_dk='#c47562', blush='#f7958a',
    brow='#3a1f10', eye_k='#1f0f14', iris_d='#4a200f', iris='#86401c', iris_l='#c9843f', eye_w='#ffffff',
    scl='#f3eef6', mouth='#5a1d24', teeth='#ffffff', teeth_sh='#d9d2e6',
    o_lt='#ff9447', o_b='#f2681f', o_sh='#c84b16', o_dk='#9c3712',
    b_lt='#4d8bff', b_b='#2563e8', b_sh='#1b45b3', b_dk='#16348a',
    lav='#b49cf5', col_sh='#d5d9ee',
    n_lt='#2448c4', n_b='#112d93', n_sh='#0a1d66', n_dk='#071449',
    cf_lt='#5679e4', cf_b='#2f52c4', cf_sh='#213b99',
    sh_b='#f6f3f9', sh_sh='#d3c9e0',
).items()}


def ellipse(cx, cy, rx, ry):
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1.0


def rect(x0, y0, x1, y1):           # inclusive design-pixel range
    return (X >= x0) & (X < x1 + 1) & (Y >= y0) & (Y < y1 + 1)


def band(y0, y1):
    return (Y >= y0) & (Y < y1)


def poly(pts):
    pts = np.array(pts, dtype=float)
    inside = np.zeros((H, W), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cond = (y1 > Y) != (y2 > Y)
        xint = (x2 - x1) * (Y - y1) / (y2 - y1 + 1e-12) + x1
        inside ^= cond & (X < xint)
    return inside


def shift(m, dx, dy):
    out = np.zeros_like(m)
    out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = \
        m[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
    return out


def edge(m, dx, dy, k=1):
    """pixels of m within k final pixels of its boundary on the (dx,dy) side"""
    r = np.zeros_like(m)
    for i in range(1, k + 1):
        r |= m & ~shift(m, -dx * i, -dy * i)
    return r


class Canvas:
    def __init__(self):
        self.c = np.zeros((H, W, 4), np.uint8)
        self.g = np.full((H, W), -1, int)
        self.lines = {}

    def put(self, mask, color, group=None):
        self.c[mask] = color
        if group is not None:
            self.g[mask] = group

    def clear(self, mask):
        self.c[mask] = 0
        self.g[mask] = -1

    def interior_lines(self, default, custom, skip):
        g = self.g
        new = self.c.copy()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            gn = np.full_like(g, -1)
            gn[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)] = \
                g[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)]
            m_any = (g >= 0) & (gn > g)
            for a, b in set(zip(g[m_any].tolist(), gn[m_any].tolist())):
                if (a, b) in skip:
                    continue
                col = custom.get((a, b), self.lines.get(a, default))
                if col is None:
                    continue
                new[(g == a) & (gn == b)] = col
        self.c = new

    def outline(self, col):
        solid = self.c[..., 3] > 0
        ring = np.zeros_like(solid)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ring |= shift(solid, dx, dy)
        self.c[ring & ~solid] = col


def sprite(cv, x0, y0, rows, cmap):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in '. ':
                continue
            x, y = x0 + i, y0 + j
            if 0 <= x < W and 0 <= y < H:
                cv.c[y, x] = cmap[ch]


G = dict(shoes=0, arms=1, pants=2, cuffs=3, hem=4, torso=5, sleeves=6, neck=7, collar=8,
         dome=9, hairb=10, face=11, bangs=12, brim=13, circle=14)

CM = {'K': P['eye_k'], 'D': P['iris_d'], 'I': P['iris'], 'L': P['iris_l'], 'W': P['eye_w'],
      'w': P['scl'], 'p': P['eye_k'], 'B': P['brow'], 'M': P['mouth'], 'T': P['teeth'],
      't': P['teeth_sh'], 'S': P['s_sh'], 'P': P['blush'], 'k': P['s_dk'], 'h': P['h_lt']}

L_OPEN = [
    "KK.......",
    ".KKKKK...",
    ".KKKKKKKK",
    ".wWWDDDDK",
    ".wWWDDDDK",
    ".wWDDpDDK",
    ".wDDppDI.",
    "..IDppII.",
    "..IIIIWI.",
    "..ILLLLI.",
    "...LLLL..",
    "...kkkk..",
]
R_OPEN = [
    ".......KK",
    "...KKKKK.",
    "KKKKKKKK.",
    "KWWDDDDw.",
    "KWWDDDDw.",
    "KWDDpDDw.",
    ".IDppDDw.",
    ".IIppDI..",
    ".IIIIWI..",
    ".ILLLLI..",
    "..LLLL...",
    "..kkkk...",
]


def lid(rows, n, left):
    """lower the upper lid by n rows"""
    flick = rows[0]
    blank = '.' * len(rows[0])
    lash1 = rows[1].replace('.', '.')
    out = [flick] + [blank] * n + [rows[1].replace('K', 'K'), rows[2]] + rows[3 + n:]
    return out[:len(rows)]


EYES = {
    'open': (L_OPEN, R_OPEN),
    'half': (lid(L_OPEN, 3, True), lid(R_OPEN, 3, False)),
    'closed': ([L_OPEN[0]] + ['.........'] * 6 + [".KKKKKKKK", "..KKKKKK."] + ['.........'] * 3,
               [R_OPEN[0]] + ['.........'] * 6 + ["KKKKKKKK.", ".KKKKKK.."] + ['.........'] * 3),
}


def render(hdy=0, bdy=0, cdy=0, eyes='open', sparkle=0):
    cv = Canvas()
    hy = hdy / S          # head offset (design units) – hdy is in final px
    by = bdy / S          # torso offset
    cy_ = cdy / S         # cap-ball follow-through

    # ---------------- legs ----------------
    shoes = (ellipse(25.2, 76.0, 4.8, 1.9) | ellipse(38.8, 76.0, 4.8, 1.9)) & (Y >= 74.5)
    cv.put(shoes, P['sh_b'], G['shoes'])
    cv.put(shoes & edge(shoes, 0, 1, 1), P['sh_sh'])

    larm = poly([(16.4, 52 + by), (21.6, 52 + by), (24.6, 64), (20.4, 64)])
    rarm = poly([(47.6, 52 + by), (42.4, 52 + by), (39.4, 64), (43.6, 64)])
    arms = larm | rarm
    cv.put(arms, P['s_b'], G['arms'])
    cv.put(larm & edge(larm, 1, 0, 2), P['s_sh'])
    cv.put(rarm & edge(rarm, 1, 0, 3), P['s_sh'])
    cv.put(arms & (Y < 55 + by), P['s_sh'])
    cv.put(larm & edge(larm, -1, 0, 1) & (Y >= 55 + by), P['s_lt'])

    lleg = poly([(21.5, 58), (32.6, 58), (32.1, 75), (18.0, 75)])
    rleg = poly([(31.4, 58), (42.5, 58), (46.0, 75), (31.9, 75)])
    pants = lleg | rleg
    cv.put(pants, P['n_b'], G['pants'])
    cv.put(pants & edge(pants, 1, 0, 4), P['n_sh'])
    cv.put(lleg & edge(lleg, -1, 0, 2) & (Y > 63), P['n_lt'])
    cv.put(poly([(25.0, 64), (26.4, 64), (26.0, 71), (24.6, 71)]), P['n_lt'])
    cv.put(poly([(37.8, 65), (38.8, 65), (39.6, 71), (38.6, 71)]), P['n_sh'])
    # pockets
    cv.put(poly([(20.6, 60.2), (25.6, 60.2), (25.0, 63.4), (22.6, 63.4)]) & ~arms, P['n_sh'])
    cv.put(poly([(43.4, 60.2), (38.4, 60.2), (39.0, 63.4), (41.4, 63.4)]) & ~arms, P['n_dk'])
    gap = poly([(31.5, 65.0), (32.5, 65.0), (34.8, 76.5), (29.2, 76.5)])
    cv.clear(gap)

    lcuff = poly([(17.4, 71), (31.0, 71), (30.9, 75.6), (17.2, 75.6)])
    rcuff = poly([(33.0, 71), (46.6, 71), (46.8, 75.6), (33.1, 75.6)])
    cuffs = lcuff | rcuff
    cv.put(cuffs, P['cf_b'], G['cuffs'])
    cv.put(cuffs & edge(cuffs, 0, -1, 1), P['cf_lt'])
    cv.put(cuffs & edge(cuffs, 0, 1, 2), P['cf_sh'])
    cv.put(cuffs & edge(cuffs, 1, 0, 3), P['cf_sh'])
    cv.put(cuffs & band(73.2, 73.9) & ~edge(cuffs, 1, 0, 3), P['cf_sh'])

    # ---------------- torso ----------------
    hem = rect(23, 56.5 + by, 41, 59 + by)
    cv.put(hem, P['white'], G['hem'])
    cv.put(hem & edge(hem, 0, 1, 1), P['col_sh'])
    cv.put(hem & edge(hem, 1, 0, 3), P['col_sh'])

    top = 44 + by

    def paint_shirt(mask, group, dark):
        rel = Y - top
        orange = mask & ((rel < 4) | ((rel >= 7) & (rel < 10)) | (rel >= 12.3))
        blue = mask & ~orange
        cv.put(orange, P['o_b'], group)
        cv.put(blue, P['b_b'], group)
        cv.put(orange & edge(orange, 0, -1, 1) & (rel > 1), P['o_lt'])
        cv.put(blue & edge(blue, 0, -1, 1), P['b_lt'])
        cv.put(orange & dark, P['o_sh'])
        cv.put(blue & dark, P['b_sh'])

    torso = poly([(22.6, 44 + by), (41.4, 44 + by), (42.3, 57.4 + by), (21.7, 57.4 + by)])
    sl = poly([(25, 43.6 + by), (19, 45 + by), (14.4, 53.8 + by), (22.6, 53.8 + by), (23.5, 47 + by)])
    sr = poly([(39, 43.6 + by), (45, 45 + by), (49.6, 53.8 + by), (41.4, 53.8 + by), (40.5, 47 + by)])
    sleeves = sl | sr
    paint_shirt(torso, G['torso'], edge(torso, 1, 0, 4) | (torso & edge(torso, 0, 1, 2)))
    paint_shirt(sleeves, G['sleeves'], (sr & ~edge(sr, -1, 0, 3)) | (sleeves & edge(sleeves, 0, 1, 1)))
    cv.put(sl & edge(sl, -1, 0, 1) & band(46.5 + by, 52 + by), P['lav'])
    cv.put(sr & edge(sr, 1, 0, 1) & band(47 + by, 52 + by), P['lav'])

    neck = rect(29, 39 + hy, 35, 46 + by)
    cv.put(neck, P['s_sh'], G['neck'])
    cv.put(neck & edge(neck, -1, 0, 2), P['s_b'])
    vshirt = poly([(28.4, 44 + by), (35.6, 44 + by), (32, 49.6 + by)])
    cv.put(vshirt, P['white'], G['collar'])
    vneck = poly([(29.5, 43.4 + by), (34.5, 43.4 + by), (32, 47.8 + by)])
    cv.put(vneck, P['s_sh'], G['neck'])
    lcol = poly([(23.0, 44.4 + by), (29.6, 41.8 + by), (31.5, 47.4 + by), (27.4, 47.2 + by)])
    rcol = poly([(41.0, 44.4 + by), (34.4, 41.8 + by), (32.5, 47.4 + by), (36.6, 47.2 + by)])
    cols = lcol | rcol
    cv.put(cols, P['white'], G['collar'])
    cv.put(rcol & edge(rcol, 0, 1, 2), P['col_sh'])
    cv.put(lcol & edge(lcol, 0, 1, 1), P['col_sh'])

    # ---------------- head ----------------
    cx, cy = 32, 22.5 + hy
    rx, ry = 21.4, 19.6
    dome = ellipse(cx, cy, rx, ry) & ~((Y >= 38 + hy) & (np.abs(X - 32) < 12.5))
    nx, ny = (X - cx) / rx, (Y - cy) / ry
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    Lv = np.array([-0.45, -0.7, 0.55]); Lv /= np.linalg.norm(Lv)
    inten = nx * Lv[0] + ny * Lv[1] + nz * Lv[2]
    cv.put(dome, P['c_b'], G['dome'])
    cv.put(dome & (inten > 0.66), P['c_lt'])
    cv.put(dome & (inten < 0.25), P['c_sh'])
    cv.put(dome & (inten < -0.08), P['c_dk'])
    gloss = ellipse(20.0, 12.0 + hy, 5.6, 2.8) & ~ellipse(21.6, 13.8 + hy, 5.6, 2.8) & dome
    cv.put(gloss, P['c_hi'])
    cv.put(dome & ellipse(14.6, 18.8 + hy, 0.9, 1.6), P['c_hi'])
    cv.put(dome & ellipse(47.5, 9.5 + hy, 2.2, 1.0) & ~ellipse(47.5, 10.4 + hy, 2.2, 1.0), P['c_lt'])
    cv.put(dome & edge(dome, 0, 1, 1) & (Y > 30 + hy), P['c_line'])
    cv.lines[G['dome']] = P['c_line']

    hairb = ellipse(32, 28.5 + hy, 15.4, 11.6) & (Y < 37.2 + hy + 1.3 * np.sin(X * 1.9))
    cv.put(hairb, P['h_b'], G['hairb'])
    cv.put(hairb & (Y >= 32.5 + hy), P['h_sh'])
    cv.put(hairb & (X > 32) & (Y >= 29 + hy), P['h_sh'])
    cv.put(hairb & poly([(18.4, 26 + hy), (19.4, 26 + hy), (19.6, 32 + hy), (18.8, 32 + hy)]), P['h_lt'])
    cv.lines[G['hairb']] = P['h_line']

    face = ellipse(32, 30.3 + hy, 11.6, 12.3)
    cv.put(face, P['s_b'], G['face'])
    cv.put(face & edge(face, 1, 0, 3), P['s_sh'])
    cv.put(face & edge(face, 0, 1, 1) & (X >= 30), P['s_sh'])
    cv.put(face & edge(face, -1, 0, 1) & band(28 + hy, 36 + hy), P['s_lt'])
    cv.lines[G['face']] = P['s_dk']

    zig = [(45.2, 34), (44.0, 31), (42.8, 27.6), (41.4, 26.4), (40.4, 24.4), (39.2, 26.0), (37.8, 23.4),
           (36.4, 25.2), (35.0, 23.0), (33.6, 24.6), (32.3, 22.2), (31.0, 24.4), (29.6, 22.8),
           (28.2, 25.2), (26.8, 23.2), (25.4, 25.6), (24.0, 24.0), (22.8, 26.8), (21.4, 27.8),
           (20.2, 31), (18.8, 34)]
    bangs = poly([(18.8, 16 + hy), (45.2, 16 + hy)] + [(x, y + 1.0 + hy) for x, y in zig])
    bangs &= ellipse(32, 29 + hy, 13.4, 15.2)
    cv.put(bangs, P['h_b'], G['bangs'])
    cv.put(bangs & edge(bangs, 0, 1, 1), P['h_sh'])
    cv.put(bangs & (X >= 39.5), P['h_sh'])
    cv.put(bangs & band(21.6 + hy, 22.4 + hy) & ((np.abs(X - 26) < 0.7) | (np.abs(X - 30.5) < 0.7) |
                                                   (np.abs(X - 35) < 0.7)), P['h_lt'])
    cv.lines[G['bangs']] = P['h_line']

    t = (X - 12.6) / 38.8
    btop = 19.0 - 2.4 * np.sin(np.pi * np.clip(t, 0, 1))
    bbot = 22.4 + 0.9 * np.sin(3 * np.pi * t + 0.3) - 1.8 * np.abs(2 * t - 1) ** 3
    brim = (t >= 0) & (t <= 1) & (Y >= btop + hy) & (Y <= bbot + hy)
    crown = poly([(25.4, 10 + cy_ + hy), (38.6, 10 + cy_ + hy), (44.2, 19 + hy), (19.8, 19 + hy)])
    cap = brim | crown
    cv.put(cap, P['p_b'], G['brim'])
    cv.put(cap & edge(cap, 0, 1, 2), P['p_sh'])
    cv.put(brim & edge(brim, 0, -1, 1) & ~crown, P['p_lt'])
    cv.put(cap & (X >= 43.5) & ~edge(cap, 0, -1, 1), P['p_sh'])
    cv.put(crown & band(15.6 + hy, 17.4 + hy) & (X >= 23) & (X <= 26.5), P['p_lt'])
    cv.lines[G['brim']] = P['p_dk']

    circ = ellipse(32, 10.6 + cy_ + hy, 7.3, 6.9)
    cv.put(circ, P['white'], G['circle'])
    inner = ellipse(32, 10.6 + cy_ + hy, 6.2, 5.8)
    cv.put(inner, P['p_b'])
    cv.put(inner & edge(inner, 1, 1, 2), P['p_sh'])
    cv.put(inner & ellipse(29.4, 8.3 + cy_ + hy, 2.4, 1.5), P['p_lt'])
    cv.put(inner & ellipse(28.9, 8.0 + cy_ + hy, 1.1, 0.7), P['p_hi'])

    skip = {(G['hairb'], G['bangs']), (G['collar'], G['dome']), (G['neck'], G['dome']),
            (G['shoes'], G['cuffs']), (G['torso'], G['hem'])}
    custom = {(G['face'], G['bangs']): P['s_sh'], (G['face'], G['brim']): P['h_line'],
              (G['bangs'], G['brim']): P['h_line'], (G['hairb'], G['brim']): P['h_line'],
              (G['neck'], G['face']): P['s_dk'], (G['neck'], G['collar']): P['s_dk'],
              (G['torso'], G['collar']): P['o_dk'], (G['torso'], G['neck']): P['o_dk'],
              (G['hem'], G['torso']): P['col_sh'], (G['arms'], G['sleeves']): P['s_dk'],
              (G['pants'], G['cuffs']): P['n_dk'], (G['pants'], G['hem']): P['n_dk'],
              (G['arms'], G['pants']): P['s_dk'], (G['arms'], G['torso']): P['s_dk'],
              (G['torso'], G['sleeves']): P['o_dk'],
              (G['hairb'], G['face']): P['h_line'], (G['collar'], G['face']): P['col_sh'],
              (G['brim'], G['circle']): P['p_dk']}
    cv.interior_lines(P['ol'], custom, skip)

    # ---------------- face details (final-pixel sprites) ----------------
    o = hdy
    sprite(cv, 31, 37 + o, [
        "BBBB.........",
        ".BBBBBBB.....",
        "...BBBBBBBBB.",
        ".......BBBBBB",
    ], CM)
    sprite(cv, 52, 36 + o, [
        ".........BBBB",
        ".....BBBBBBB.",
        ".BBBBBBBBB...",
        "BBBBBB.......",
    ], CM)
    le, re = EYES[eyes]
    sprite(cv, 33, 41 + o, le, CM)
    sprite(cv, 54, 41 + o, re, CM)
    cv.c[53 + o, 48] = P['s_sh']
    cv.c[54 + o, 49] = P['s_sh']
    sprite(cv, 33, 53 + o, ["PPP"], CM)
    sprite(cv, 61, 53 + o, ["PPP"], CM)
    sprite(cv, 41, 55 + o, [
        "..........MM",
        "......MMMMTM",
        "MMMMMMTTTTTM",
        ".....MTtTTM.",
        "......MMMM..",
        ".......kk...",
    ], CM)

    cv.outline(P['ol'])

    if sparkle:
        sx, sy = 22, 13 + hdy
        pts = {1: [(0, 0)],
               2: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
               3: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]}[sparkle]
        for dx, dy in pts:
            cv.c[sy + dy, sx + dx] = P['white']
    return cv.c


def on_bg(frame, bg=(236, 241, 252)):
    im = Image.fromarray(frame)
    out = Image.new('RGBA', im.size, bg + (255,))
    out.alpha_composite(im)
    return out


if __name__ == '__main__':
    import sys
    f = render()
    on_bg(f).resize((W * 5, H * 5), Image.NEAREST).save('preview2.png')
    on_bg(f).crop((24, 24, 72, 72)).resize((48 * 12, 48 * 12), Image.NEAREST).save('face2.png')

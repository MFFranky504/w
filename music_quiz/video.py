import numpy as np, math, random, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
from tl import *
W, H, S = 270, 480, 4
FW, FH = W * S, H * S
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda sz: ImageFont.truetype(MONO, sz)
BODY = ImageFont.truetype(SANS, 54)
GOLD = (255, 205, 60); WHITE = (250, 245, 235); DARK = (14, 8, 34)
ease = lambda x: (lambda c: c * c * (3 - 2 * c))(min(max(x, 0), 1))
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

def dgrad(w, h, c0, c1, steps=8):
    v = (np.arange(h)[:, None] * np.ones((1, w))) / max(h - 1, 1)
    q = v * steps; base = np.floor(q); frac = q - base
    thr = np.tile(B4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    idx = np.clip(base + (frac > thr), 0, steps) / steps
    c0 = np.array(c0, float); c1 = np.array(c1, float)
    return (c0 + (c1 - c0) * idx[..., None]).astype(np.uint8)

def paste_arr(im, arr, y0):
    im.paste(Image.fromarray(arr), (0, y0))

def glow(arr, cx, cy, r, col, k=1.0):
    x0, x1 = max(int(cx - r), 0), min(int(cx + r), W); y0, y1 = max(int(cy - r), 0), min(int(cy + r), H)
    if x0 >= x1 or y0 >= y1: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    a = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 2 * k
    arr[y0:y1, x0:x1] = np.clip(arr[y0:y1, x0:x1] + a[..., None] * np.array(col), 0, 255)

def beam(arr, x_top, x_bot, y0, y1, wtop, wbot, col, k=.25):
    ys = np.arange(y0, y1); fr = (ys - y0) / (y1 - y0)
    for y, f in zip(ys, fr):
        cx = x_top + (x_bot - x_top) * f; hw = (wtop + (wbot - wtop) * f) / 2
        xa, xb = max(int(cx - hw), 0), min(int(cx + hw), W)
        if xa < xb: arr[y, xa:xb] = np.clip(arr[y, xa:xb] + np.array(col) * k * (1 - f * .5), 0, 255)

# ---------------- sprites ----------------
def make_sprite(hat=False, h=92):
    m = Image.new("L", (48, 96), 0); d = ImageDraw.Draw(m)
    d.ellipse((13, 5, 33, 28), fill=255); d.rectangle((19, 26, 27, 32), fill=255)
    d.rounded_rectangle((7, 30, 39, 68), 5, fill=255)
    d.rectangle((1, 32, 9, 64), fill=255); d.rectangle((37, 32, 45, 64), fill=255)
    d.rectangle((11, 66, 22, 93), fill=255); d.rectangle((25, 66, 36, 93), fill=255)
    d.rectangle((9, 90, 22, 95), fill=255); d.rectangle((25, 90, 38, 95), fill=255)
    if hat:
        d.rectangle((8, 8, 38, 11), fill=255); d.rectangle((15, -1, 31, 9), fill=255)
    a = np.array(m) > 0
    rgba = np.zeros((96, 48, 4), np.uint8); rgba[a] = (14, 8, 34, 255)
    left = a & ~np.roll(a, 1, 1); right = a & ~np.roll(a, -1, 1); top = a & ~np.roll(a, 1, 0)
    rgba[left] = (70, 230, 255, 255); rgba[right] = (255, 70, 190, 255); rgba[top & ~left & ~right] = (255, 215, 90, 255)
    ey = 17 if not hat else 18
    for ex in (17, 26):   # eyes: magenta body + highlight pixel
        rgba[ey:ey + 3, ex:ex + 4] = (255, 60, 150, 255); rgba[ey, ex + 1] = (255, 235, 245, 255)
    return Image.fromarray(rgba, "RGBA")
SPR = make_sprite(); SPR_HAT = make_sprite(hat=True)
QM = ["01110", "10001", "00001", "00110", "00100", "00000", "00100"]
def qmark(im, x, y, sc=2, col=GOLD):
    d = ImageDraw.Draw(im)
    for j, row in enumerate(QM):
        for i, c in enumerate(row):
            if c == "1":
                d.rectangle((x + i * sc + 1, y + j * sc + 1, x + i * sc + sc, y + j * sc + sc), fill=(60, 25, 0))
                d.rectangle((x + i * sc, y + j * sc, x + i * sc + sc - 1, y + j * sc + sc - 1), fill=col)
def sil(im, x, feet_y, t, hat=False, phase=0.0, q=True):
    s = SPR_HAT if hat else SPR
    bob = 1 if int((t + phase) * 2.2) % 2 else 0
    im.paste(s, (int(x - 24), int(feet_y - 96 + bob)), s)
    if ((t + phase) * .45) % 1 < .05:   # blink
        d_ = ImageDraw.Draw(im); ey = int(feet_y - 96 + bob) + (18 if hat else 17)
        for ex in (17, 26): d_.rectangle((int(x - 24) + ex, ey, int(x - 24) + ex + 3, ey + 2), fill=(14, 8, 34))
    if q:
        qmark(im, int(x + 22), int(feet_y - 100 + 3 * math.sin(t * 3 + phase)), 2)
        if hat: pass

# ---------------- scene bases ----------------
rnd = random.Random(5)
def palm(d, x, by, h, sway, col=(12, 6, 28)):
    pts = [(x + sway * (i / 6) ** 2 * 6, by - h * i / 6) for i in range(7)]
    for a_, b_ in zip(pts, pts[1:]): d.line([a_, b_], fill=col, width=4)
    cx, cy = pts[-1]
    for ang in (-170, -140, -110, -75, -45, -10, 25, 155, 190):
        r = math.radians(ang); c_, s_ = math.cos(r), math.sin(r)
        tip = (cx + c_ * 30, cy - s_ * 8 + 16 * abs(c_) + 4)
        mid = (cx + c_ * 16, cy - s_ * 14 - 3)
        d.polygon([(cx, cy), (mid[0] - 3 * s_, mid[1] - 4), tip, (mid[0] + 3 * s_, mid[1] + 3)], fill=col)

def base_sunset():
    a = np.zeros((H, W, 3), np.uint8)
    a[:150] = dgrad(W, 150, (28, 8, 58), (190, 45, 120), 8)
    a[150:250] = dgrad(W, 100, (190, 45, 120), (255, 160, 60), 8)
    a[250:270] = dgrad(W, 20, (60, 20, 100), (25, 10, 55), 4)
    a[270:] = (20, 10, 38)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.ellipse((135 - 50, 205 - 50, 135 + 50, 205 + 50), fill=(255, 210, 80))
    d.ellipse((135 - 50, 205 - 50 + 6, 135 + 50, 205 + 50), fill=(255, 190, 70)); d.ellipse((135 - 50, 215 - 50, 135 + 50, 205 + 50), fill=(255, 205, 80))
    for i in range(7):  # retro sun stripes
        y = 214 + i * 6; d.rectangle((80, y, 190, y + i // 2), fill=tuple(int(v) for v in a[y, 5]))
    d.rectangle((0, 250, W, 252), fill=(255, 120, 90))
    x = 0
    while x < W:  # skyline
        w = rnd.randint(7, 15); h = rnd.randint(8, 30); d.rectangle((x, 250 - h, x + w, 250), fill=(30, 12, 54))
        for wy in range(250 - h + 3, 248, 5):
            if rnd.random() < .4: d.point((x + rnd.randint(1, w - 1), wy), fill=(255, 190, 90))
        x += w + 1
    d.rectangle((0, 238, 74, 250), fill=(20, 8, 42)); d.rectangle((10, 226, 20, 238), fill=(160, 50, 60)); d.rectangle((28, 224, 38, 238), fill=(160, 50, 60)); d.rectangle((46, 226, 56, 238), fill=(160, 50, 60))
    for cx in (210, 240):  # cranes
        d.line([(cx, 250), (cx, 205)], fill=(30, 12, 54), width=2); d.line([(cx - 20, 208), (cx + 12, 208)], fill=(30, 12, 54), width=2)
    return im
SUNSET = base_sunset()
STARS = [(rnd.randint(0, W), rnd.randint(0, 120), rnd.random() * 6) for _ in range(40)]

def dyn_sunset(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (x, y, p) in STARS:
        if math.sin(t * 2 + p) > .3: d.point((x, y), fill=(255, 235, 200))
    for i in range(6):  # water shimmer
        y = 254 + i * 3; w = 20 - i * 2 + int(3 * math.sin(t * 3 + i)); d.line([(135 - w, y), (135 + w, y)], fill=(255, 170, 80))
    sw = math.sin(t * 1.3) * 1.2
    palm(d, 24, 266, 90, sw); palm(d, 250, 266, 76, -sw * 1.2); palm(d, 232, 266, 52, sw)
    # perspective grid floor
    for k in range(-9, 10):
        d.line([(135, 270), (135 + k * 60, H)], fill=(120, 40, 140), width=1)
    for j in range(10):
        y = 270 + ((j + (t * .6) % 1) ** 2) * 2.3
        if y < H: d.line([(0, y), (W, y)], fill=(120, 40, 140))
    # lowrider
    cx = int((t * 14) % (W + 90)) - 45; cy = 268
    d.rectangle((cx, cy - 7, cx + 38, cy), fill=(150, 60, 200)); d.rectangle((cx + 8, cy - 12, cx + 28, cy - 7), fill=(120, 40, 170))
    d.rectangle((cx + 11, cy - 11, cx + 17, cy - 8), fill=(255, 220, 150)); d.rectangle((cx + 20, cy - 11, cx + 26, cy - 8), fill=(255, 220, 150))
    d.rectangle((cx + 1, cy - 4, cx + 37, cy - 3), fill=(255, 205, 80))
    for wx in (cx + 7, cx + 30): d.ellipse((wx - 4, cy - 3, wx + 4, cy + 4), fill=(10, 5, 20)); d.point((wx, cy), fill=GOLD)
    for k in range(10):  # dust
        x = (k * 29 + t * 5) % W; y = 200 - ((t * 9 + k * 31) % 150); d.point((x, y), fill=(255, 215, 120))

CONF = [(rnd.random() * W, rnd.random() * H, rnd.uniform(25, 60), rnd.choice([(255, 210, 60), (255, 80, 170), (80, 240, 230), (170, 130, 255)]), rnd.random() * 6) for _ in range(70)]

# ---------------- Brooklyn night (recap) ----------------
def base_brooklyn():
    a = np.zeros((H, W, 3), np.uint8)
    a[:266] = dgrad(W, 266, (6, 8, 34), (96, 34, 96), 10); a[266:] = (24, 16, 34)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.ellipse((190, 30, 222, 62), fill=(255, 240, 200)); d.ellipse((198, 34, 226, 62), fill=a[48, 205].tolist() and tuple(int(v) for v in a[48, 205]))
    # bridge tower + cables (left)
    d.rectangle((6, 110, 26, 266), fill=(52, 38, 66)); d.rectangle((54, 110, 74, 266), fill=(52, 38, 66)); d.rectangle((6, 108, 74, 118), fill=(60, 44, 74))
    for x0 in (10, 58): d.pieslice((x0, 130, x0 + 12, 160), 180, 360, fill=(14, 8, 28)); d.rectangle((x0, 145, x0 + 12, 190), fill=(14, 8, 28))
    for i in range(0, 14): d.line([(74 + i * 14, 224 - int((i * 14 - 0) ** 2 / 400)), (74 + i * 14, 236)], fill=(120, 90, 130))
    d.line([(74, 112), (110, 190), (160, 226)], fill=(150, 110, 160)); d.line([(26, 112), (-10, 190)], fill=(150, 110, 160))
    d.rectangle((0, 236, W, 241), fill=(60, 44, 74))
    # brownstones
    x = 80
    while x < W:
        w = rnd.randint(30, 44); h = rnd.randint(70, 110); c = rnd.choice([(74, 38, 60), (88, 46, 56), (62, 34, 66)])
        d.rectangle((x, 266 - h, x + w, 266), fill=c); d.rectangle((x - 2, 266 - h - 4, x + w + 2, 266 - h), fill=(40, 22, 44))
        for wy in range(266 - h + 10, 250, 18):
            for wx in range(x + 5, x + w - 8, 12):
                d.rectangle((wx, wy, wx + 6, wy + 9), fill=(255, 205, 110) if rnd.random() < .55 else (30, 20, 50))
        d.rectangle((x + w // 2 - 4, 254, x + w // 2 + 4, 266), fill=(20, 12, 30)); d.rectangle((x + 2, 262, x + w - 2, 266), fill=(110, 80, 90))
        x += w + 3
    # water tower
    d.rectangle((222, 96, 244, 120), fill=(60, 36, 50)); d.polygon([(220, 96), (246, 96), (233, 86)], fill=(40, 24, 38))
    for lx in (224, 242): d.line([(lx, 120), (lx - 2, 150)], fill=(40, 24, 38))
    # street
    d.rectangle((0, 266, W, 270), fill=(110, 80, 90))
    for y in range(272, H, 9):
        for x2 in range(0 if (y // 9) % 2 else -9, W, 18): d.rectangle((x2, y, x2 + 16, y + 7), fill=(36, 24, 48))
    return im
BROOK = base_brooklyn()
CONF2 = [(rnd.uniform(-70, 70), rnd.uniform(-110, -20), rnd.choice([(255, 205, 60), (255, 80, 170), (80, 240, 230), (170, 130, 255), (255, 255, 255)])) for _ in range(90)]
def dyn_brooklyn(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (x, y, p) in STARS:
        if math.sin(t * 2 + p) > .2: d.point((x, y), fill=(255, 235, 200))
    arr = np.array(im)
    if ts < REVEAL:
        k = min(1, ts / 2.5)
        for kk, bx in enumerate((50, 220)):
            beam(arr, bx, 135 + math.sin(t * 3 + kk * 3) * 40, 0, 266, 4, 40, (255, 60, 120), .20 * k)
        glow(arr, 135, 220, 70 * (.6 + .4 * k), (255, 120, 60), .5 * k)
    else:
        e = ts - REVEAL
        beam(arr, 135, 135, 0, 266, 10, 90, (255, 215, 120), .35 * min(1, e / .3)); glow(arr, 135, 210, 100, (255, 190, 80), .55)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    # neon BROOKLYN sign
    if int(t * 4) % 9 != 0 or ts > REVEAL:
        d.rectangle((182, 172, 258, 190), fill=(20, 8, 30), outline=(255, 205, 60)); d.fontmode = "1"
        d.text((220, 181), "BROOKLYN", font=F(11), fill=(255, 205, 60), anchor="mm")
    if ts >= REVEAL:
        e = ts - REVEAL
        for (vx, vy, c) in CONF2:
            px = 135 + vx * 1.6 * min(e, 1.6) ** .8; py = 190 + vy * 2.2 * min(e, 1.2) + 40 * e * e
            if 0 <= px < W and 0 <= py < H: d.rectangle((px, py, px + 1, py + 2), fill=c)
        for (x, y, v, c, p) in CONF[:40]:
            yy = (y + v * (t + 1)) % H; d.rectangle((x, yy, x + 1, yy + 2), fill=c)

def notes(im, t):
    d = ImageDraw.Draw(im)
    for k in range(7):
        x = (k * 41 + 20 + math.sin(t * 1.5 + k) * 8) % W; y = 262 - ((t * 14 + k * 37) % 210)
        c = [(255, 205, 60), (255, 90, 170), (90, 235, 255)][k % 3]
        d.rectangle((x + 2, y, x + 2, y + 6), fill=c); d.rectangle((x, y + 5, x + 2, y + 7), fill=c); d.rectangle((x + 3, y, x + 5, y + 1), fill=c)

# ---------------- UI ----------------
def lt(d, xy, s, sz, fill, shadow=(10, 4, 30), anchor="mm"):
    f = F(sz); d.fontmode = "1"
    d.text((xy[0] + 1, xy[1] + 1), s, font=f, fill=shadow, anchor=anchor); d.text(xy, s, font=f, fill=fill, anchor=anchor)
DIFFC = [(235, 60, 60), (255, 140, 40), (255, 215, 60), (80, 230, 120)]
def layout(text):
    chars = []; hl = False
    for ch in text:
        if ch == "*": hl = not hl
        else: chars.append((ch, hl))
    words = []; cur = []
    for ch, h in chars:
        if ch == " ": words.append(cur); cur = []
        else: cur.append((ch, h))
    words.append(cur)
    probe = ImageDraw.Draw(Image.new("RGB", (4, 4))); sp = probe.textlength(" ", font=BODY)
    def runs(w):
        r = []
        for ch, h in w:
            if r and r[-1][1] == h: r[-1] = (r[-1][0] + ch, h)
            else: r.append((ch, h))
        return [(t, h, probe.textlength(t, font=BODY)) for t, h in r]
    lines = []; line = []; wd = 0
    for w in words:
        rs = runs(w); ww = sum(r[2] for r in rs)
        if line and wd + sp + ww > 900: lines.append(line); line = []; wd = 0
        wd += (sp if line else 0) + ww; line.append((rs, ww))
    lines.append(line); return lines, sp
LAY = [layout(c["text"]) for c in CLUES]



# ======================= v4: Snoop (crip walk), Nas-inspired NYC scenes =======================
def snoop_layer(t, mode="col"):
    col = mode == "col"; OUT = (14, 8, 34, 255); DK = (14, 8, 34, 255)
    L_ = Image.new("RGBA", (100, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L_)
    SKIN = (150, 98, 68, 255); SHIRT = (34, 34, 50, 255); PANT = (62, 88, 160, 255); PANTD = (44, 64, 124, 255)
    CAP = (24, 24, 34, 255); BRAID = (50, 32, 28, 255); SHOE = (240, 240, 248, 255); GOLDC = (255, 215, 80, 255)
    C = (lambda c: c) if col else (lambda c: DK)
    def line(p, q, w, c):
        if col: d.line([p, q], fill=OUT, width=w + 2)
        d.line([p, q], fill=C(c), width=w)
    ph = t * 13.0; fy = 124; sway = 2 * math.sin(ph * .5)
    hx, hy = 50 - sway, fy - 52; sx, sy = 50 + sway, fy - 90; cx, cy = sx + sway * .5, sy - 14
    for s in (-1, 1):                                   # braids (behind)
        for k in (0, 1):
            wig = math.sin(ph * .5 + k + s) * 2
            line((cx + s * 7, cy + 2), (cx + s * (9 + k * 2) + wig, sy + 14), 2, BRAID)
    for s in (-1, 1):                                   # legs: crip-walk slide / heel-toe flick
        p = ph + (0 if s < 0 else math.pi)
        fx = 50 + s * 3 + 15 * math.sin(p); fyy = fy - 6 * max(0, math.sin(p + 1.2))
        knee = ((hx + fx) / 2 + s * 3 + 3 * math.sin(p), (hy + fyy) / 2 + 3)
        line((hx + s * 4, hy), knee, 8, PANT); line(knee, (fx, fyy - 3), 7, PANTD)
        sg = 1 if math.cos(p) > 0 else -1
        x0, x1 = sorted((fx - 3 * sg, fx + 7 * sg))
        d.rectangle((x0, fyy - 4, x1, fyy), fill=C(SHOE), outline=OUT if col else DK)
    d.polygon([(sx - 13, sy), (sx + 13, sy), (hx + 10, hy + 4), (hx - 10, hy + 4)], fill=C(SHIRT), outline=OUT if col else DK)
    if col: d.line([(hx - 10, hy + 2), (hx + 10, hy + 2)], fill=(80, 80, 112, 255), width=1)
    for s in (-1, 1):                                   # arms swing + cross
        shd = (sx + s * 13, sy + 3); a1 = .35 * s + .9 * math.sin(ph + (0 if s < 0 else math.pi) + .5)
        el = (shd[0] + 16 * math.sin(a1), shd[1] + 16 * math.cos(a1))
        a2 = a1 - s * .9 + 1.0 * math.sin(2 * ph + s * 1.3)
        hd = (el[0] + 14 * math.sin(a2), el[1] + 14 * math.cos(a2))
        line(shd, el, 7, SHIRT); line(el, hd, 5, SKIN)
        d.ellipse((hd[0] - 3, hd[1] - 3, hd[0] + 3, hd[1] + 3), fill=C(SKIN), outline=OUT if col else DK)
    line((sx - 5, sy + 1), (sx, sy + 12), 1, GOLDC); line((sx + 5, sy + 1), (sx, sy + 12), 1, GOLDC)
    d.rectangle((sx - 2, sy + 12, sx + 2, sy + 16), fill=C(GOLDC))
    d.ellipse((cx - 8, cy - 10, cx + 8, cy + 10), fill=C(SKIN), outline=OUT if col else DK)
    d.polygon([(cx - 9, cy - 3), (cx - 9, cy - 9), (cx, cy - 14), (cx + 9, cy - 9), (cx + 9, cy - 3)], fill=C(CAP), outline=OUT if col else DK)
    d.rectangle((cx - 10, cy - 4, cx + 13, cy - 2), fill=C(CAP))
    if col:
        d.rectangle((cx - 7, cy - 1, cx + 7, cy + 2), fill=(15, 12, 22, 255)); d.point((cx - 5, cy - 1), fill=(255, 255, 255, 255)); d.point((cx + 2, cy - 1), fill=(255, 255, 255, 255))
        d.line([(cx - 3, cy + 6), (cx + 3, cy + 6)], fill=(70, 40, 32, 255))
    if col: return L_
    a = np.array(L_)[..., 3] > 0; arr = np.zeros((130, 100, 4), np.uint8); arr[a] = (14, 8, 34, 255)
    left = a & ~np.roll(a, 1, 1); right = a & ~np.roll(a, -1, 1); top = a & ~np.roll(a, 1, 0)
    arr[left] = (70, 230, 255, 255); arr[right] = (255, 70, 190, 255); arr[top & ~left & ~right] = (255, 215, 90, 255)
    return Image.fromarray(arr, "RGBA")
def snoop(im, t, x=135, feet=266, mode="col"):
    l_ = snoop_layer(t, mode); im.paste(l_, (int(x - 50), int(feet - 124)), l_)
SPR_HAT_M = SPR_HAT.transpose(Image.FLIP_LEFT_RIGHT)
def dim_top(im, n=140):
    a = np.array(im); a[:n] = (a[:n] * np.linspace(.55, 1, n)[:, None, None]).astype(np.uint8); return Image.fromarray(a)
def dots(d, arr_pts, c): [d.point(p, fill=c) for p in arr_pts]

# ---- clue 1: block party, Queensbridge-style red brick towers ----
def base_block():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = dgrad(W, 266, (6, 8, 32), (92, 38, 92), 10); a[266:] = (30, 22, 38)
    im = Image.fromarray(a); d = ImageDraw.Draw(im); x = 0
    while x < W:
        w = rnd.randint(6, 14); h = rnd.randint(14, 50); d.rectangle((x, 246 - h, x + w, 246), fill=(22, 16, 48)); x += w + 1
    for (x0, w, h) in [(-6, 60, 150), (58, 52, 110), (114, 56, 164), (174, 50, 120), (228, 52, 140)]:
        d.rectangle((x0, 266 - h, x0 + w, 266), fill=(104, 44, 54))
        for by in range(266 - h, 266, 6): d.line([(x0, by), (x0 + w, by)], fill=(86, 34, 46))
        for wy in range(266 - h + 8, 252, 12):
            for wx in range(x0 + 5, x0 + w - 6, 10): d.rectangle((wx, wy, wx + 4, wy + 6), fill=(255, 200, 110) if rnd.random() < .5 else (36, 22, 44))
        d.rectangle((x0 - 1, 266 - h - 3, x0 + w + 1, 266 - h), fill=(60, 26, 40))
    d.rectangle((137, 266 - 164 - 22, 155, 266 - 164 - 4), fill=(70, 40, 50)); d.polygon([(135, 266 - 164 - 22), (157, 266 - 164 - 22), (146, 266 - 164 - 32)], fill=(46, 26, 40))
    for y in range(268, H, 12):
        for x2 in range(0, W, 20):
            o = 10 if (y // 12) % 2 else 0; d.rectangle((x2 + o, y, x2 + o + 18, y + 10), fill=(38, 28, 48))
    d.rectangle((0, 262, W, 267), fill=(120, 96, 110))
    return dim_top(im)
BLOCK = base_block()
CROWD_B = [(rnd.randint(8, 262), rnd.uniform(0, 6), rnd.choice([(34, 18, 52), (28, 14, 44), (44, 22, 60)])) for _ in range(14)]
def dyn_block(im, t, ts, tag):
    d = ImageDraw.Draw(im); arr = np.array(im)
    beat = (t * 94 / 60) % 1
    glow(arr, 135, 250, 120, (255, 140, 80), .22)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(18):                                          # string lights between poles
        x = k * 15.5; y = 64 + 12 * math.sin(k / 17 * math.pi) + 2 * math.sin(k)
        c = [(255, 210, 90), (255, 90, 170), (90, 235, 255)][k % 3]
        if math.sin(t * 5 + k * 1.7) > -.5: d.rectangle((x, y, x + 2, y + 2), fill=c)
        d.point((x + 1, y - 1), fill=(90, 70, 90))
    for (x, p, c) in CROWD_B:                                    # crowd silhouettes bobbing
        b = int(2 * abs(math.sin(t * 4 + p))); d.ellipse((x - 3, 242 - b, x + 3, 248 - b), fill=c); d.rectangle((x - 4, 248 - b, x + 4, 264), fill=c)
        if int(t * 2 + p) % 2: d.line([(x - 4, 250 - b), (x - 7, 243 - b)], fill=c, width=2)
    for k in range(4):                                           # grill smoke
        y = 236 - ((t * 20 + k * 17) % 60); x = 236 + 4 * math.sin(t * 2 + k)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(150, 130, 150))
    d.rectangle((222, 246, 250, 262), fill=(24, 18, 28), outline=(90, 70, 90)); d.rectangle((224, 246, 248, 249), fill=(255, 110, 40))
    pul = 1 if beat < .2 else 0                                  # boombox
    d.rectangle((14, 248, 58, 264), fill=(30, 22, 40), outline=(120, 110, 140))
    for cx_ in (24, 48): d.ellipse((cx_ - 6 - pul, 256 - 6 - pul, cx_ + 6 + pul, 256 + 6 + pul), fill=(60, 50, 80), outline=(160, 150, 190)); d.point((cx_, 256), fill=GOLD)
    d.rectangle((30, 250, 42, 252), fill=(255, 205, 60))
    d.rectangle((170, 252, 214, 264), fill=(26, 18, 34), outline=(110, 100, 130))      # DJ table
    for cx_ in (182, 202):
        d.ellipse((cx_ - 7, 247, cx_ + 7, 257), fill=(14, 10, 20), outline=(150, 140, 170)); a_ = t * 5; d.line([(cx_, 252), (cx_ + 5 * math.cos(a_), 252 + 3 * math.sin(a_))], fill=GOLD)

# ---- clue 2: jazz club ----
def base_jazz():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = (92, 14, 46); a[266:] = (70, 44, 36)
    for x in range(0, W, 14): a[:266, x:x + 5] = (70, 8, 36); a[:266, x + 5:x + 8] = (112, 22, 58)
    for y in range(268, H, 10): a[y:y + 9] = (110, 70, 48) if (y // 10) % 2 else (90, 56, 40)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 22), fill=(60, 6, 30)); [d.polygon([(x, 22), (x + 14, 22), (x + 7, 34)], fill=(60, 6, 30)) for x in range(0, W, 14)]
    d.rectangle((8, 196, 66, 266), fill=(14, 10, 22), outline=(60, 50, 80)); d.rectangle((4, 190, 70, 198), fill=(22, 16, 32))   # piano
    d.rectangle((12, 226, 62, 238), fill=(240, 236, 226)); [d.line([(x, 226), (x, 238)], fill=(20, 16, 26)) for x in range(17, 62, 5)]
    d.rectangle((12, 204, 62, 222), fill=(30, 24, 44))
    d.ellipse((212, 214, 250, 252), fill=(150, 80, 36), outline=(60, 28, 16)); d.ellipse((218, 192, 244, 220), fill=(150, 80, 36), outline=(60, 28, 16))
    d.rectangle((229, 150, 233, 196), fill=(60, 36, 24)); d.ellipse((222, 140, 240, 156), fill=(60, 36, 24))
    d.line([(231, 150), (231, 252)], fill=(220, 210, 180)); d.rectangle((0, 264, W, 269), fill=(190, 140, 50))
    return dim_top(im)
JAZZ = base_jazz()
def dyn_jazz(im, t, ts, tag):
    arr = np.array(im)
    for k, bx in enumerate((90, 180)):
        beam(arr, bx, bx + 22 * math.sin(t * .8 + k * 2), 0, 266, 6, 74, (255, 200, 130), .2)
    glow(arr, 135, 210, 90, (255, 130, 90), .3)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if int(t * 7) % 23 != 0:                                      # neon JAZZ
        d.rectangle((92, 134, 178, 160), fill=(24, 8, 30), outline=(90, 235, 255)); d.fontmode = "1"
        d.text((136, 148), "JAZZ", font=F(24), fill=(255, 90, 170), anchor="mm"); d.text((135, 147), "JAZZ", font=F(24), fill=(255, 190, 220), anchor="mm")
    for k in range(7):                                            # smoke haze
        x = (k * 43 + t * 6) % (W + 40) - 20; y = 110 + 30 * math.sin(t * .4 + k) + k * 12
        d.ellipse((x - 18, y - 4, x + 18, y + 4), outline=(140, 80, 110))

# ---- clue 3: Queensboro bridge + Manhattan skyline at dusk (Queensbridge) ----
def base_qb():
    a = np.zeros((H, W, 3), np.uint8); a[:215] = dgrad(W, 215, (28, 14, 70), (255, 140, 90), 12)
    a[215:266] = dgrad(W, 51, (120, 60, 90), (20, 16, 48), 5); a[266:] = (22, 16, 34)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.ellipse((60, 160, 130, 230), fill=(255, 210, 120))
    x = 100
    while x < W:
        w = rnd.randint(8, 16); h = rnd.randint(30, 90); d.rectangle((x, 215 - h, x + w, 215), fill=(20, 22, 58))
        for wy in range(215 - h + 4, 212, 6):
            if rnd.random() < .7: d.point((x + rnd.randint(1, w - 1), wy), fill=(255, 205, 120))
        x += w + 1
    d.rectangle((196, 100, 206, 215), fill=(24, 26, 64)); d.polygon([(196, 100), (206, 100), (201, 72)], fill=(24, 26, 64)); d.line([(201, 72), (201, 50)], fill=(150, 150, 190))
    d.rectangle((0, 196, W, 204), fill=(30, 32, 60))                                         # bridge deck
    for x in range(0, W, 12): d.line([(x, 196), (x + 6, 170 - int(18 * math.sin(x / W * math.pi))), (x + 12, 196)], fill=(40, 44, 76))
    for x in range(0, W, 12): d.line([(x, 204), (x, 214)], fill=(30, 32, 60))
    d.rectangle((0, 156, 6, 215), fill=(30, 32, 60)); d.rectangle((120, 150, 126, 215), fill=(30, 32, 60))
    d.polygon([(0, 150), (123, 150), (123, 158), (0, 164)], fill=(36, 38, 68))
    d.rectangle((0, 262, W, 267), fill=(110, 90, 110))
    for fx in range(0, W, 5): d.line([(fx, 236), (fx, 262)], fill=(60, 54, 80))
    d.line([(0, 236), (W, 236)], fill=(80, 74, 100)); d.rectangle((0, 70, 56, 266), fill=(98, 42, 56))                  # foreground tower
    for by in range(70, 266, 6): d.line([(0, by), (56, by)], fill=(80, 32, 46))
    for wy in range(80, 240, 14):
        for wx in range(6, 50, 12): d.rectangle((wx, wy, wx + 5, wy + 7), fill=(255, 200, 110) if rnd.random() < .5 else (36, 22, 44))
    for y in range(268, H, 12):
        for x2 in range(0, W, 20):
            o = 10 if (y // 12) % 2 else 0; d.rectangle((x2 + o, y, x2 + o + 18, y + 10), fill=(34, 26, 46))
    return dim_top(im, 130)
QB = base_qb()
def dyn_qb(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(9):                                            # river light streaks
        y = 220 + k * 5; w = 30 - k * 2 + 4 * math.sin(t * 2 + k); d.line([(95 - w, y), (95 + w, y)], fill=(255, 190, 120))
    for k in range(5):                                            # cars on the bridge
        x = ((t * 28 + k * 54) % (W + 20)) - 10; d.rectangle((x, 192, x + 3, 194), fill=(255, 230, 150)); d.point((x + 4, 193), fill=(255, 80, 80))
    d.rectangle((60, 222, 66, 224), fill=(40, 30, 50)); b = int((t * 8) % 150); d.point((20 + b, 236), fill=(255, 230, 150))  # boat
    for k in range(4):
        x = (k * 70 + t * 14) % W; y = 120 + 10 * math.sin(t * 2 + k); d.line([(x, y), (x + 3, y - 2), (x + 6, y)], fill=(30, 20, 40))
    for k in range(25):
        if math.sin(t * 1.6 + k * 2.3) > .4: d.point((110 + (k * 37) % 150, 130 + (k * 53) % 80), fill=(255, 220, 140))

# ---- clue 4: the battle (Ether) — rival silhouettes, red vs blue strobe ----
def base_battle():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = dgrad(W, 266, (8, 4, 20), (40, 12, 56), 8); a[266:] = (12, 8, 22)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.rectangle((0, 8, W, 14), fill=(60, 56, 80)); [d.rectangle((x, 14, x + 6, 20), fill=(90, 86, 110)) for x in range(10, W, 30)]
    for y in range(268, H, 10): d.line([(0, y), (W, y)], fill=(30, 20, 50))
    for k in range(-9, 10): d.line([(135, 266), (135 + k * 40, H)], fill=(30, 20, 50))
    d.rectangle((0, 264, W, 268), fill=(120, 40, 80))
    return im
BATTLE = base_battle()
CROWD_C = [(rnd.randint(4, 266), rnd.uniform(0, 6)) for _ in range(40)]
def dyn_battle(im, t, ts, tag):
    arr = np.array(im); ph = int(t * 4) % 2
    for k, (bx, col) in enumerate(((20, (255, 50, 70)), (250, (60, 120, 255)))):
        on = (ph == k) or int(t * 12) % 5 == 0
        beam(arr, bx, 135, 14, 266, 6, 90, col, .34 if on else .12)
    glow(arr, 135, 170, 70, (200, 120, 255), .35)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for (x, p) in CROWD_C:                                        # crowd silhouettes with raised hands
        b = int(2 * abs(math.sin(t * 5 + p))); d.ellipse((x - 3, 250 - b, x + 3, 256 - b), fill=(18, 10, 30)); d.rectangle((x - 4, 256 - b, x + 4, 270), fill=(18, 10, 30))
        if int(t * 3 + p) % 2: d.line([(x + 3, 256 - b), (x + 6, 247 - b)], fill=(18, 10, 30), width=2)
    if int(t * 14) % 11 == 0: d.line([(135, 90), (126, 130), (140, 134), (130, 180)], fill=(255, 255, 255), width=2)
    pu = 1 + int(2 * (1 if (t * 3) % 1 < .25 else 0)); d.fontmode = "1"
    d.text((136 + 2, 172 + 2), "VS", font=F(40 + pu), fill=(255, 50, 70), anchor="mm"); d.text((136 - 2, 172 - 2), "VS", font=F(40 + pu), fill=(60, 120, 255), anchor="mm"); d.text((136, 172), "VS", font=F(40 + pu), fill=WHITE, anchor="mm")
    for (mx) in (66, 206): d.line([(mx, 266), (mx, 226)], fill=(110, 100, 130), width=2); d.ellipse((mx - 3, 220, mx + 3, 227), fill=(70, 60, 90), outline=(160, 150, 190))

# ---- outro / hook helpers: Nueva York + globo dorado ----
def draw_globe(im, t, cx=135, cy=205, r=50):
    d = ImageDraw.Draw(im); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(10, 28, 78), outline=GOLD)
    for k in range(4):
        w = int(abs(math.cos(t * .9 + k * math.pi / 4)) * r); d.ellipse((cx - w, cy - r, cx + w, cy + r), outline=(255, 205, 60))
    for lat in (-.6, -.3, 0, .3, .6):
        dy = int(r * lat); hw = int(math.sqrt(max(r * r - dy * dy, 0))); d.line([(cx - hw, cy + dy), (cx + hw, cy + dy)], fill=(255, 205, 60))
    d.arc((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), 200, 260, fill=(255, 245, 190), width=2)
def dyn_outro(im, t, ts, tag):
    dyn_brooklyn(im, t, 2.4, tag); arr = np.array(im); glow(arr, 135, 205, 90, (255, 190, 80), .4); im.paste(Image.fromarray(arr)); draw_globe(im, t)
def dyn_recap(im, t, ts, tag):
    dyn_sunset(im, t, ts, tag); arr = np.array(im)
    if ts < REVEAL:
        k = min(1, ts / 2.5)
        for kk, bx in enumerate((50, 220)): beam(arr, bx, 135 + math.sin(t * 3 + kk * 3) * 40, 0, 266, 4, 40, (255, 60, 120), .2 * k)
        glow(arr, 135, 220, 70 * (.6 + .4 * k), (255, 120, 60), .5 * k)
    else:
        beam(arr, 135, 135, 0, 266, 10, 90, (255, 215, 120), .3 * min(1, (ts - REVEAL) / .3)); glow(arr, 135, 210, 100, (255, 190, 80), .45)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if ts >= REVEAL:
        e = ts - REVEAL
        for (vx, vy, c) in CONF2:
            px = 135 + vx * 1.6 * min(e, 1.6) ** .8; py = 190 + vy * 2.2 * min(e, 1.2) + 40 * e * e
            if 0 <= px < W and 0 <= py < H: d.rectangle((px, py, px + 1, py + 2), fill=c)
        for (x, y, v, c, p) in CONF[:40]:
            yy = (y + v * (t + 1)) % H; d.rectangle((x, yy, x + 1, yy + 2), fill=c)
def dyn_win(im, t, ts, tag): dyn_recap(im, t, REVEAL + 1.5 + ts, tag)
SCENES = [(BROOK, dyn_brooklyn), (SUNSET, dyn_recap), (SUNSET, dyn_win), (BLOCK, dyn_block), (JAZZ, dyn_jazz), (QB, dyn_qb), (BATTLE, dyn_battle), (BROOK, dyn_outro)]


# ======================= UI / winners / render (v4) =======================
def pill(d, cx, y0, y1, w, fill, outline=None):
    d.rectangle((cx - w // 2, y0, cx + w // 2, y1), fill=fill, outline=outline)

def ui_low(seg, ts, t):
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
    if seg == S_HOOK:
        if ts < 1.0:
            if int(ts * 15) % 3 != 2:
                lt(d, (135, 70), "¿QUIÉN", 40, WHITE, shadow=(255, 60, 150)); lt(d, (135, 118), "ES?", 44, GOLD, shadow=(70, 230, 255))
            return ui
        k = ease((ts - 1.0) / .3); dy = int((1 - k) * -30)
        lt(d, (135, 46 + dy), "¡SOLO LOS REALES", 17, WHITE); lt(d, (135, 70 + dy), "LO ADIVINAN!", 24, GOLD, shadow=(120, 50, 0))
        if ts > 1.4: pill(d, 135, 300, 322, 222, (14, 8, 34), GOLD); lt(d, (135, 311), "¿LO ADIVINAS EN LA PISTA 1?", 11, WHITE)
        if ts > 1.9: lt(d, (135, 342), "ARTISTA MISTERIOSO · PARTE 9", 10, (255, 200, 120))
        if ts > 2.3: lt(d, (135, 362), "PERO PRIMERO... ¿QUIÉN FUE EL ANTERIOR?", 8, WHITE)
        return ui
    if seg == S_RECAP:
        if ts < REVEAL:
            k = ease(ts / .35); dy = int((1 - k) * -30)
            lt(d, (135, 46 + dy), "EL ARTISTA ANTERIOR", 17, WHITE); lt(d, (135, 76 + dy), "FUE...", 34, GOLD, shadow=(120, 50, 0))
            if ts > .5: lt(d, (135, 112), "." * (1 + int(ts * 3) % 3), 28, (255, 120, 170))
        else:
            e = ts - REVEAL; k = ease(e / .25); dy = int((1 - k) * -20)
            lt(d, (135, 46 + dy), "SNOOP", 34, WHITE, shadow=(255, 70, 190)); lt(d, (135, 90 + dy), "DOGG", 46, GOLD, shadow=(120, 50, 0))
            if e > .5: pill(d, 135, 120, 140, 196, (14, 8, 34), GOLD); lt(d, (135, 130), "LONG BEACH, CALIFORNIA", 9, (255, 200, 120))
            if ts > 6.4:
                b = int(2 * math.sin(t * 10)); pill(d, 135, 150 + b, 172 + b, 214, GOLD); lt(d, (135, 161 + b), "¡AHORA LOS GANADORES!", 11, DARK, shadow=(255, 230, 140))
        return ui
    if seg == S_WIN:
        k = ease(ts / .35); dy = int((1 - k) * -26)
        lt(d, (135, 24 + dy), "GANADORES · PARTE 8", 20, GOLD, shadow=(110, 50, 0))
        lt(d, (135, 46 + dy), "ORDENADOS POR PISTA Y LIKES", 10, WHITE)
        lt(d, (135, 60 + dy), f"{len(WINNERS)} PERSONAS LO ADIVINARON", 9, (255, 200, 120))
        return ui
    if seg == S_OUT:
        sw = ts > 3.2
        a_, b_ = ("¿CUÁNTOS PUNTOS", "SACASTE?") if sw else ("¿YA SABES", "QUIÉN ES?")
        ka = ease(ts / .3) if not sw else ease((ts - 3.2) / .25); dy = int((1 - ka) * -26)
        lt(d, (135, 52 + dy), a_, 23 if not sw else 17, WHITE); lt(d, (135, 88 + dy), b_, 34 if not sw else 30, GOLD, shadow=(120, 50, 0))
        if ts > .6 and not sw: pill(d, 135, 112, 134, 242, GOLD); lt(d, (135, 123), "ESCRÍBELO EN LOS COMENTARIOS", 11, DARK, shadow=(255, 230, 140))
        if ts > 1.2 and not sw:
            o = 2 if int(t * 3) % 2 else 0
            for ox in (-24, 0, 24): d.polygon([(135 + ox - 6, 148 + o), (135 + ox + 6, 148 + o), (135 + ox, 158 + o)], fill=(255, 200, 120))
        if ts > 2.0: pill(d, 135, 274, 292, 130, (14, 8, 34), GOLD); lt(d, (135, 283), "NUEVA YORK", 12, GOLD)
        if ts > 3.5:
            pill(d, 135, 306, 328, 246, GOLD); lt(d, (135, 317), "REVELO AL ARTISTA EN EL PRÓXIMO VIDEO", 8, DARK, shadow=(255, 230, 140))
            lt(d, (135, 342), "LOS QUE ACIERTEN SALEN EN LA PARTE 10", 9, WHITE); lt(d, (135, 358), "SÍGUEME PARA NO PERDÉRTELO", 9, (255, 200, 120))
        return ui
    c = CLUES[seg - S_C1]; n = c["n"]; seg_len = T[seg + 1] - T[seg]
    k = ease(ts / .3); dy = int((1 - k) * -30)
    lt(d, (135, 46 + dy), f"PISTA {n} / 4", 24, GOLD, shadow=(110, 50, 0))
    for i in range(4):
        fill = DIFFC[n - 1] if i < n and ts > .45 + i * .11 else (50, 36, 80)
        d.rectangle((66 + i * 36, 66 + dy, 98 + i * 36, 70 + dy), fill=fill)
    lt(d, (135, 80 + dy), f"DIFICULTAD: {c['diff']}", 11, DIFFC[n - 1])
    lt(d, (135, 92 + dy), f"VALE {c['pts']} PUNTO{'S' if c['pts'] > 1 else ''}", 10, (255, 230, 170))
    if ts > .9:
        f = F(18); w = int(d.textlength(c["chip"], font=f)) + 16; x0 = 135 - w // 2; fl = ts < 1.0
        d.rectangle((x0 - 2, 100, x0 + w + 2, 126), fill=(255, 205, 60)); d.rectangle((x0, 102, x0 + w, 124), fill=WHITE if fl else (14, 8, 34))
        lt(d, (135, 114), c["chip"], 18, DARK if fl else GOLD, shadow=(60, 30, 0))
    if ts > .6:
        rem = min(max(1 - max(0, ts - TW0) / (seg_len - TW0 - .2), 0), 1); urgent = rem < .3 and int(t * 6) % 2
        d.rectangle((12, 12, 258, 18), fill=(14, 8, 34)); d.rectangle((14, 14, 14 + int(242 * rem), 16), fill=(255, 255, 255) if urgent else DIFFC[n - 1])
    if seg in BANNERS and BANNER_T <= ts < BANNER_T + 1.6:
        e = ts - BANNER_T; kk = ease(e / .2); by = 208 + int((1 - kk) * 40) + int(2 * math.sin(t * 12))
        pill(d, 135, by, by + 22, 232, GOLD); lt(d, (135, by + 11), BANNERS[seg], 11, DARK, shadow=(255, 230, 140))
    return ui

PCOL = {1: (255, 205, 60), 2: (90, 235, 255), 3: (255, 90, 170), 0: (190, 170, 255)}
PTXT = {1: "PISTA 1", 2: "PISTA 2", 3: "PISTA 3", 0: "SIN PISTA INDICADA"}
F_ROW = {}
def fnt(sz):
    if sz not in F_ROW: F_ROW[sz] = ImageFont.truetype(SANS, sz)
    return F_ROW[sz]
def draw_winners(img, ts):
    k = ease(ts / .35)
    if k <= 0: return
    dy = int((1 - k) * 70); y0, y1 = 800 + dy, 1540 + dy; d = ImageDraw.Draw(img)
    d.rectangle((44, y0 - 8, 1036, y1 + 8), fill=(14, 10, 36)); d.rectangle((52, y0, 1028, y1), fill=(24, 42, 150), outline=(255, 205, 60), width=8)
    d.rectangle((60, y0 + 8, 1020, y0 + 38), fill=(120, 70, 10)); d.fontmode = "1"
    d.text((540, y0 + 24), "ORDEN: PISTA > LIKES > QUIÉN COMENTÓ ANTES", font=F(22), fill=(255, 235, 170), anchor="mm"); d.fontmode = "L"
    wx0, wy0, ww, wh = 64, y0 + 44, 952, WIN_WH
    win = Image.new("RGB", (ww, wh), (24, 42, 150)); wd = ImageDraw.Draw(win)
    off = min(max(ts - WIN_START, 0) * WIN_SPEED, max(0, len(ROWS) * ROW_H - wh))
    for i, r in enumerate(ROWS):
        y = i * ROW_H - off
        if y < -ROW_H or y > wh: continue
        col = PCOL[r["pk"]]
        if r["kind"] == "hdr":
            wd.rounded_rectangle((6, y + 8, ww - 6, y + ROW_H - 8), 12, fill=(14, 10, 36), outline=col, width=3)
            wd.text((ww // 2, y + ROW_H // 2 - 2), f"★  {PTXT[r['pk']]}  ★", font=fnt(38), fill=col, anchor="mm"); continue
        top = r["rank"] == 1
        wd.rounded_rectangle((6, y + 6, ww - 6, y + ROW_H - 8), 14, fill=(255, 205, 60) if top else (40, 66, 190))
        wd.rectangle((6, y + 12, 14, y + ROW_H - 14), fill=col)
        wd.ellipse((26, y + 14, 94, y + ROW_H - 16), fill=(14, 10, 36)); wd.text((60, y + ROW_H // 2 - 4), str(r["rank"]), font=fnt(32), fill=col, anchor="mm")
        badge = ("1º EN ADIVINAR · " if r["h"] in SPECIAL else "") + f"♥{r['lk']}" + ("  TT" if r["pl"] == "TT" else "")
        fb = fnt(26 if r["h"] in SPECIAL else 32); bw = int(wd.textlength(badge, font=fb))
        sz = 44; avail = ww - 110 - bw - 40
        while sz > 22 and wd.textlength(r["h"], font=fnt(sz)) > avail: sz -= 2
        wd.text((110, y + ROW_H // 2 - 4), r["h"], font=fnt(sz), fill=DARK if top else WHITE, anchor="lm")
        wd.text((ww - 24, y + ROW_H // 2 - 4), badge, font=fb, fill=(150, 20, 60) if top else (255, 170, 205), anchor="rm")
    img.paste(win, (wx0, wy0))

def draw_panel_text(img, seg, ts):
    c = CLUES[seg - S_C1]; lines, sp = LAY[seg - S_C1]
    k = ease((ts - 1.5) / .3)
    if k <= 0: return
    dy = int((1 - k) * 50); y0 = 272 * S + dy
    d = ImageDraw.Draw(img)
    d.rectangle((12 * S - 8, y0 - 8, 258 * S + 8, 378 * S + 8 + dy), fill=(14, 10, 36))
    d.rectangle((12 * S, y0, 258 * S, 378 * S + dy), fill=(24, 42, 150), outline=(140, 175, 255), width=8)
    d.rectangle((12 * S + 8, y0 + 8, 258 * S - 8, y0 + 38), fill=(12, 24, 90))
    d.fontmode = "1"
    d.text((135 * S, y0 + 24), "ADIVINA AL ARTISTA · COMÉNTALO", font=F(26), fill=(190, 210, 255), anchor="mm")
    d.fontmode = "L"
    n_show = max(0, int((ts - TW0) / TWS)) if ts >= TW0 else 0
    lh = 74; top = y0 + 52 + ((378 * S + dy) - (y0 + 52) - lh * len(lines)) // 2 + 4
    count = 0
    for li, line in enumerate(lines):
        tot = sum(ww for _, ww in line) + sp * (len(line) - 1); x = 540 - tot / 2
        for rs, ww in line:
            for t_, h, w_ in rs:
                if count >= n_show: return
                part = t_[: n_show - count]; col = GOLD if h else WHITE
                d.text((x + 2, top + li * lh + 3), part, font=BODY, fill=(5, 8, 40)); d.text((x, top + li * lh), part, font=BODY, fill=col)
                count += len(t_); x += w_
            count += 1; x += sp

# wipe

STRIPE = [(255, 205, 60), (255, 70, 160), (60, 240, 225), (150, 110, 255)]
def wipe(img, p):
    if p <= 0 or p >= 1: return img
    d = ImageDraw.Draw(img); bh = FH // 8
    for i in range(8):
        u = min(max((p - i * .02) / .86, 0), 1)
        xf = FW * (1 - ease(min(1, u * 2))); xt = FW * (1 - ease(max(0, u * 2 - 1)))
        if u <= 0 or u >= 1: continue
        d.rectangle((xf, i * bh, xt, (i + 1) * bh), fill=STRIPE[i % 4])
    return img


def seg_of(t):
    s_ = 0
    for i in range(1, 8):
        if t >= T[i]: s_ = i
    return s_

def shake_amp(seg, ts):
    if seg == S_RECAP:
        if .4 < ts < REVEAL: return 2 + 7 * ((ts - .4) / (REVEAL - .4)) ** 2
        if REVEAL <= ts < REVEAL + .6: return 22 * (1 - (ts - REVEAL) / .6)
    if S_C1 <= seg <= S_C1 + 3 and 1.0 < ts < 1.3: return 10 * (1 - (ts - 1.0) / .3)
    return 0

def glitch(img, t, strength):
    arr = np.array(img); rng = np.random.default_rng(int(t * 30) + 11)
    arr[..., 0] = np.roll(arr[..., 0], int(18 * strength), 1); arr[..., 2] = np.roll(arr[..., 2], -int(18 * strength), 1)
    for _ in range(7):
        y = int(rng.integers(0, FH - 120)); h = int(rng.integers(20, 120)); arr[y:y + h] = np.roll(arr[y:y + h], int(rng.integers(-140, 140)), 1)
    return Image.fromarray(arr)

SHIFT = 70
def render(t):
    seg = seg_of(t); ts = t - T[seg]
    base, dyn = SCENES[seg]
    im = base.copy(); dyn(im, t, ts, None)
    if seg not in (S_RECAP, S_WIN): notes(im, t)
    if seg == S_RECAP: snoop(im, t, mode="sil" if ts < REVEAL else "col"); (qmark(im, 140, 138 + int(3 * math.sin(t * 4)), 3) if ts < REVEAL else None)
    elif seg == S_WIN: snoop(im, t)
    elif seg == S_C1 + 3:
        sil(im, 98, 266, t, q=False); im.paste(SPR_HAT_M, (178 - 24, 266 - 96), SPR_HAT_M); qmark(im, 134, 150 + int(3 * math.sin(t * 3)), 2)
    else: sil(im, 135, 266, t)
    if seg == S_WIN:
        im2 = Image.new("RGB", (W, H), (20, 10, 38)); im2.paste(im, (0, -SHIFT)); im = im2
    seg_len = (T[seg + 1] if seg < 7 else END) - T[seg]
    punch = .03 * max(0, 1 - (ts - 1.0) / .25) if S_C1 <= seg <= S_C1 + 3 and ts > 1.0 else 0
    z = 1.04 + .05 * (ts / seg_len) + punch
    big = im.resize((FW, FH), Image.NEAREST)
    cw, ch = FW / z, FH / z; amp = shake_amp(seg, ts); rg = np.random.default_rng(int(t * 30))
    ox = (FW - cw) / 2 + (math.sin(t * .5) * 6 if seg else 0) + rg.uniform(-amp, amp); oy = (FH - ch) * .55 + rg.uniform(-amp, amp)
    ox = min(max(ox, 0), FW - cw); oy = min(max(oy, 0), FH - ch)
    big = big.crop((int(ox), int(oy), int(ox + cw), int(oy + ch))).resize((FW, FH), Image.NEAREST)
    ui = ui_low(seg, ts, t).resize((FW, FH), Image.NEAREST)
    big = big.convert("RGBA"); big.alpha_composite(ui); big = big.convert("RGB")
    if S_C1 <= seg <= S_C1 + 3: draw_panel_text(big, seg, ts)
    if seg == S_WIN: draw_winners(big, ts)
    if seg == S_HOOK and t < 1.0: big = glitch(big, t, 1.0)
    elif seg == S_RECAP and REVEAL <= ts < REVEAL + .25: big = glitch(big, t, .6)
    if seg == S_RECAP and REVEAL <= ts < REVEAL + .3:
        big = Image.blend(big, Image.new("RGB", (FW, FH), (255, 255, 255)), .9 * (1 - (ts - REVEAL) / .3))
    for i in range(1, 8):
        p = (t - (T[i] - WIPE / 2)) / WIPE
        if 0 < p < 1: wipe(big, p)
    if t < .12: big = Image.blend(Image.new("RGB", (FW, FH)), big, t / .12)
    if t > END - .5: big = Image.blend(Image.new("RGB", (FW, FH)), big, max(0, (END - t) / .5))
    return big

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for tt_ in map(float, sys.argv[2:]): render(tt_).save(f"still_{tt_:.1f}.png")
    else:
        out = sys.argv[1]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{FW}x{FH}", "-r", str(FPS), "-i", "-",
                              "-i", "audio.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                              "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        for f in range(int(END * FPS)):
            p.stdin.write(render(f / FPS).tobytes())
        p.stdin.close(); p.wait()

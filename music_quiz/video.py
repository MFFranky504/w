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
def make_sprite(hat=False, h=92, helmet=None):
    m = Image.new("L", (48, 96), 0); d = ImageDraw.Draw(m)
    d.ellipse((13, 5, 33, 28), fill=255); d.rectangle((19, 26, 27, 32), fill=255)
    d.rounded_rectangle((7, 30, 39, 68), 5, fill=255)
    d.rectangle((1, 32, 9, 64), fill=255); d.rectangle((37, 32, 45, 64), fill=255)
    d.rectangle((11, 66, 22, 93), fill=255); d.rectangle((25, 66, 36, 93), fill=255)
    d.rectangle((9, 90, 22, 95), fill=255); d.rectangle((25, 90, 38, 95), fill=255)
    if hat:
        d.rectangle((8, 8, 38, 11), fill=255); d.rectangle((15, -1, 31, 9), fill=255)
    if helmet: d.rounded_rectangle((11, 1, 35, 30), 6, fill=255); d.rectangle((9, 14, 11, 22), fill=255); d.rectangle((35, 14, 37, 22), fill=255)
    a = np.array(m) > 0
    rgba = np.zeros((96, 48, 4), np.uint8); rgba[a] = (14, 8, 34, 255)
    left = a & ~np.roll(a, 1, 1); right = a & ~np.roll(a, -1, 1); top = a & ~np.roll(a, 1, 0)
    rgba[left] = (70, 230, 255, 255); rgba[right] = (255, 70, 190, 255); rgba[top & ~left & ~right] = (255, 215, 90, 255)
    ey = 17 if not hat else 18
    if helmet:                                           # robot helmet: glowing visor band + side pieces, no eyes
        rgba[12:20, 14:32] = helmet; rgba[13, 15:31] = (255, 255, 255, 255); rgba[14:22, 9:12] = (170, 170, 190, 255); rgba[14:22, 35:38] = (170, 170, 190, 255)
    else:
        for ex in (17, 26):   # eyes: magenta body + highlight pixel
            rgba[ey:ey + 3, ex:ex + 4] = (255, 60, 150, 255); rgba[ey, ex + 1] = (255, 235, 245, 255)
    return Image.fromarray(rgba, "RGBA")
SPR = make_sprite(); SPR_HAT = make_sprite(hat=True)
SPR_ROBOT_A = make_sprite(helmet=(70, 230, 255, 255)); SPR_ROBOT_B = make_sprite(helmet=(255, 205, 60, 255))
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
def diffc(n, nb):
    stops = [(235, 60, 60), (255, 140, 40), (255, 215, 60), (80, 230, 120)]; x = (n - 1) / max(nb - 1, 1) * 3; i = min(int(x), 2); f = x - i
    return tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3))
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
from dance_data import DANCE, DANCE_FRAME
NEAR_MEAN = (sum(r[4] for r in DANCE) / len(DANCE) + 5, sum(r[5] for r in DANCE) / len(DANCE))
def dance_at(t):
    n = len(DANCE); x = (t / DANCE_FRAME) % n; i = int(x); f = x - i; p, q = DANCE[i], DANCE[(i + 1) % n]
    return [p[k] + (q[k] - p[k]) * f for k in range(8)]
def ik(p0, p1, l1, l2, pick):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; dist = max(min(math.hypot(dx, dy), l1 + l2 - .05), abs(l1 - l2) + .05)
    ux, uy = dx / max(math.hypot(dx, dy), 1e-6), dy / max(math.hypot(dx, dy), 1e-6)
    a_ = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist); h_ = math.sqrt(max(l1 * l1 - a_ * a_, 0))
    mx, my = p0[0] + ux * a_, p0[1] + uy * a_; c1 = (mx - uy * h_, my + ux * h_); c2 = (mx + uy * h_, my - ux * h_)
    el = max((c1, c2), key=pick); return el, (p0[0] + ux * dist, p0[1] + uy * dist)
def snoop_layer(t, mode="col"):
    """Snoop doing the side-to-side groove: motion measured from the reference GIF (2.2 s loop, hand circles every 0.73 s)."""
    col = mode == "col"; OUT = (14, 8, 34, 255); DK = (14, 8, 34, 255)
    L_ = Image.new("RGBA", (110, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L_)
    SKIN = (150, 98, 68, 255); SHIRT = (28, 28, 40, 255); SLEEVE = (238, 238, 246, 255); PANT = (30, 32, 48, 255); PANTD = (22, 24, 38, 255)
    CAP = (22, 22, 30, 255); SHOE = (240, 240, 248, 255); GOLDC = (255, 215, 80, 255)
    C = (lambda c: c) if col else (lambda c: DK)
    def line(p, q, w, c):
        if col: d.line([p, q], fill=OUT, width=w + 2)
        d.line([p, q], fill=C(c), width=w)
    hdx, hdy, tdx, ldx, nxx, nyy, fxx, fyy = dance_at(t); fy = 124; X0 = 55            # layer is 110 wide (x offset 5)
    sx, sy = X0 + tdx + .3 * hdx, fy - 90 + .4 * hdy; hx, hy = X0 + .3 * tdx + .7 * ldx, fy - 52
    cx, cy = X0 + hdx, sy - 10 + hdy * .6; look = max(-1, min(1, hdx / 8))
    BR, BRH = (74, 46, 34, 255), (128, 90, 66, 255)
    for s in (-1, 1):                                                   # two braids (one per side), hanging BEHIND the body
        sw = 1.6 * math.sin(t * 8.6 + s) + .35 * hdx
        p0 = (cx + s * 6, cy + 4); mid = (sx + s * 14 + sw * .5, sy + 8); p1 = (sx + s * 16 + sw, sy + 30)
        for (a_, b_) in ((p0, mid), (mid, p1)):
            if col:
                d.line([a_, b_], fill=OUT, width=5); d.line([a_, b_], fill=BR, width=3)
            else: d.line([a_, b_], fill=DK, width=5)
        if col:
            for j in range(1, 9):
                q = ((p0[0] + (mid[0] - p0[0]) * j / 8, p0[1] + (mid[1] - p0[1]) * j / 8) if j <= 4 else (mid[0] + (p1[0] - mid[0]) * (j - 4) / 5, mid[1] + (p1[1] - mid[1]) * (j - 4) / 5))
                d.point(q, fill=BRH)
            d.rectangle((p1[0] - 2, p1[1], p1[0] + 2, p1[1] + 3), fill=(200, 170, 90, 255))        # bead tip
    for s in (-1, 1):                                                   # legs: planted, counter-shifting like the reference
        hip = (hx + s * 5, hy + 6); ank = (X0 + s * 7 + ldx, fy - 1)
        knee, _ = ik(hip, ank, 23.5, 23.5, lambda c, s=s: s * c[0])
        line(hip, knee, 9, PANT); line(knee, ank, 8, PANTD)
        d.rectangle((ank[0] - 5, ank[1] - 3, ank[0] + 5, ank[1] + 1), fill=C(SHOE), outline=OUT if col else DK)
    d.polygon([(sx - 15, sy), (sx + 15, sy), (hx + 13, hy + 12), (hx - 13, hy + 12)], fill=C(SHIRT), outline=OUT if col else DK)
    if col:
        d.ellipse((sx - 2, sy + 8, sx + 8, sy + 18), outline=(240, 240, 248, 255)); d.line([(hx - 13, hy + 10), (hx + 13, hy + 10)], fill=(60, 60, 84, 255))
        d.polygon([(sx - 5, sy - 1), (sx + 5, sy - 1), (sx, sy + 5)], fill=(238, 238, 246, 255))         # white tee collar
    for s in (1, -1):                                                   # s=-1 circling hand (viewer's left), s=+1 low palm-down hand
        shd = (sx + s * 14, sy + 3)
        if s == -1:                                                     # elbow stays near the body; the forearm sweeps the circle
            tgt = (nxx + 5, nyy); el = (shd[0] - 1 + .25 * (tgt[0] - NEAR_MEAN[0]), shd[1] + 13 + .25 * (tgt[1] - NEAR_MEAN[1]))
            vx, vy = tgt[0] - el[0], tgt[1] - el[1]; r = max(9.0, min(16.0, math.hypot(vx, vy))); k = math.hypot(vx, vy) or 1
            hd = (el[0] + vx / k * r, el[1] + vy / k * r)
        else:
            tgt = (fxx + 5, fyy); el, hd = ik(shd, tgt, 15, 15, lambda c: c[0])
        line(shd, el, 9, SHIRT); line(el, hd, 6, SLEEVE)
        if s == -1: d.ellipse((hd[0] - 3, hd[1] - 3, hd[0] + 3, hd[1] + 3), fill=C(SKIN), outline=OUT if col else DK)
        else: d.rectangle((hd[0] - 4, hd[1], hd[0] + 4, hd[1] + 3), fill=C(SKIN), outline=OUT if col else DK)
    line((sx - 5, sy + 4), (sx, sy + 14), 1, GOLDC); line((sx + 5, sy + 4), (sx, sy + 14), 1, GOLDC); d.rectangle((sx - 2, sy + 14, sx + 2, sy + 17), fill=C(GOLDC))
    d.ellipse((cx - 8, cy - 10, cx + 8, cy + 10), fill=C(SKIN), outline=OUT if col else DK)                     # head sits right on the shoulders (no neck)
    d.polygon([(cx - 9, cy - 3), (cx - 9, cy - 9), (cx, cy - 14), (cx + 9, cy - 9), (cx + 9, cy - 3)], fill=C(CAP), outline=OUT if col else DK)
    bx = cx + 3 * look; d.rectangle((bx - 10, cy - 4, bx + 10, cy - 2), fill=C(CAP))
    if col:
        for ex in (-5, 2):                                              # eyes (no sunglasses): heavy lids, white, pupil
            d.rectangle((cx + ex + look * 1.5, cy - 1, cx + ex + 3 + look * 1.5, cy - 1), fill=(30, 18, 16, 255))
            d.rectangle((cx + ex + look * 1.5, cy, cx + ex + 3 + look * 1.5, cy + 1), fill=(245, 240, 235, 255))
            px_ = int(cx + ex + 1 + (1 if look > .3 else 0) - (1 if look < -.3 else 0)); d.rectangle((px_, cy, px_ + 1, cy + 1), fill=(20, 12, 12, 255))
        d.rectangle((cx - 2 + look, cy + 6, cx + 2 + look, cy + 9), fill=(40, 26, 24, 255))
    if col: return L_
    a = np.array(L_)[..., 3] > 0; arr = np.zeros((130, 110, 4), np.uint8); arr[a] = (14, 8, 34, 255)
    left = a & ~np.roll(a, 1, 1); right = a & ~np.roll(a, -1, 1); top = a & ~np.roll(a, 1, 0)
    arr[left] = (70, 230, 255, 255); arr[right] = (255, 70, 190, 255); arr[top & ~left & ~right] = (255, 215, 90, 255)
    return Image.fromarray(arr, "RGBA")
def snoop(im, t, x=135, feet=266, mode="col"):
    l_ = snoop_layer(t, mode); im.paste(l_, (int(x - 55), int(feet - 124)), l_)
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

# ======================= v5: Nas (previous-answer reveal) + Daft Punk scenes =======================
def _outline_sil(im):
    a = np.array(im)[..., 3] > 0; ol = np.zeros_like(a)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): ol |= np.roll(np.roll(a, dy, 0), dx, 1)
    ol &= ~a; arr = np.array(im); arr[ol] = (14, 8, 34, 255); full = a | ol
    sil = np.zeros_like(arr); sil[full] = (14, 8, 34, 255)
    left = full & ~np.roll(full, 1, 1); right = full & ~np.roll(full, -1, 1); top = full & ~np.roll(full, 1, 0)
    sil[left] = (70, 230, 255, 255); sil[right] = (255, 70, 190, 255); sil[top & ~left & ~right] = (255, 215, 90, 255)
    return Image.fromarray(arr, "RGBA"), Image.fromarray(sil, "RGBA")
def make_nas():
    w, h = 64, 110; SK = (138, 90, 62); SKD = (102, 64, 44); HAIR = (20, 14, 16)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x0 in (17, 34): d.rectangle((x0, 88, x0 + 13, 105), fill=(54, 70, 122)); d.rectangle((x0, 88, x0 + 2, 105), fill=(38, 50, 92))
    for x0 in (14, 33): d.rectangle((x0, 102, x0 + 17, 109), fill=(240, 240, 248)); d.rectangle((x0, 107, x0 + 17, 109), fill=(150, 150, 175))
    d.rounded_rectangle((8, 44, 56, 92), 6, fill=(32, 32, 42)); d.rectangle((0, 48, 10, 88), fill=(32, 32, 42)); d.rectangle((54, 48, 64, 88), fill=(32, 32, 42))
    d.rectangle((9, 52, 14, 86), fill=(52, 52, 70)); d.rectangle((50, 52, 55, 86), fill=(52, 52, 70)); d.line([(32, 66), (32, 92)], fill=(70, 70, 92), width=1)
    d.rectangle((1, 86, 9, 94), fill=SK); d.rectangle((55, 86, 63, 94), fill=SK); d.rectangle((1, 91, 9, 94), fill=SKD)
    d.polygon([(23, 44), (41, 44), (32, 66)], fill=(238, 238, 246))
    d.line([(23, 46), (32, 68), (41, 46)], fill=(255, 215, 80), width=2); d.ellipse((27, 66, 37, 76), fill=(255, 215, 80), outline=(170, 115, 20)); d.rectangle((31, 70, 33, 72), fill=(170, 115, 20))
    d.rectangle((26, 38, 38, 46), fill=SKD)
    d.ellipse((17, 12, 47, 44), fill=SK); d.rectangle((15, 27, 18, 33), fill=SKD); d.rectangle((46, 27, 49, 33), fill=SKD)
    d.ellipse((18, 8, 46, 24), fill=HAIR); d.rectangle((18, 17, 20, 22), fill=HAIR); d.rectangle((44, 17, 46, 22), fill=HAIR)
    d.rectangle((22, 24, 28, 25), fill=HAIR); d.rectangle((36, 24, 42, 25), fill=HAIR)                       # brows
    for ex in (22, 36): d.rectangle((ex, 27, ex + 5, 29), fill=(245, 240, 235)); d.rectangle((ex + 2, 27, ex + 4, 29), fill=(20, 12, 12))
    d.rectangle((30, 31, 34, 34), fill=SKD); d.rectangle((27, 36, 37, 37), fill=(60, 30, 28))
    d.polygon([(25, 38), (39, 38), (36, 44), (28, 44)], fill=(46, 30, 26))                                   # goatee
    return _outline_sil(im)
NAS_COL, NAS_SIL = make_nas()
CROWN = ["0010010010", "0110110110", "0111111110", "1111111111", "1311211311", "1111111111"]
def crown(im, x, y):
    d = ImageDraw.Draw(im)
    for j, row in enumerate(CROWN):
        for i, c in enumerate(row):
            if c != "0": d.rectangle((x + i * 2, y + j * 2, x + i * 2 + 1, y + j * 2 + 1), fill={"1": (255, 205, 60), "2": (255, 245, 170), "3": (240, 60, 130)}[c])
def prev_draw(im, t, ts):
    """Sprite of the previous episode's artist (reveal = 'la respuesta de ayer')."""
    kind = PREV["sprite"]
    if kind == "snoop": snoop(im, t, mode="sil" if ts < REVEAL else "col"); (qmark(im, 140, 138 + int(3 * math.sin(t * 4)), 3) if ts < REVEAL else None); return
    if ts < REVEAL:
        im.paste(NAS_SIL, (135 - 32, 266 - 110 + (1 if int(t * 2.2) % 2 else 0)), NAS_SIL); qmark(im, 129, 128 + int(3 * math.sin(t * 4)), 3)
    else:
        e = ts - REVEAL; jump = -int(abs(14 * math.exp(-e * 3.5) * math.cos(e * 16)))
        im.paste(NAS_COL, (135 - 32, 266 - 110 + jump + (1 if int(t * 2.2) % 2 else 0)), NAS_COL)
        crown(im, 125, 266 - 130 + jump + int(2 * math.sin(t * 3)))

# ---- Daft Punk clue 1: 1993 music-press desk (corkboard, flyers, the review with red pen) ----
def base_press():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = (28, 40, 56); a[266:] = (84, 54, 38)
    for y in range(268, H, 10): a[y:y + 1] = (60, 38, 28)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.rectangle((12, 134, 258, 218), fill=(156, 108, 64), outline=(72, 46, 28), width=2)
    for _ in range(16):
        x = rnd.randint(18, 220); y = rnd.randint(138, 176); w = rnd.randint(22, 40); hh = rnd.randint(26, 38)
        c = rnd.choice([(250, 220, 90), (240, 110, 150), (110, 220, 235), (236, 236, 226), (170, 130, 240)])
        d.rectangle((x, y, x + w, y + hh), fill=c)
        for ly in range(y + 4, y + hh - 3, 5): d.line([(x + 3, ly), (x + w - 3 - rnd.randint(0, 8), ly)], fill=tuple(int(q * .55) for q in c))
        d.ellipse((x + w // 2 - 1, y - 1, x + w // 2 + 2, y + 2), fill=(220, 40, 50))
    d.rectangle((92, 140, 180, 214), fill=(244, 240, 228), outline=(60, 50, 40)); d.rectangle((96, 144, 176, 156), fill=(30, 30, 36))     # the review page
    for ly in range(162, 212, 5): d.line([(98, ly), (96 + rnd.randint(60, 78), ly)], fill=(90, 86, 80))
    d.ellipse((133, 138, 139, 144), fill=(220, 40, 50))
    d.rectangle((10, 236, 62, 266), fill=(46, 82, 150)); d.rectangle((14, 232, 66, 240), fill=(220, 90, 70)); d.rectangle((8, 226, 56, 234), fill=(240, 200, 80))   # magazine stack
    for k in range(3): d.ellipse((206 - k * 2, 244 - k * 4, 250 - k * 2, 262 - k * 4), fill=(18, 14, 22), outline=(80, 76, 96)); d.ellipse((223 - k * 2, 249 - k * 4, 233 - k * 2, 257 - k * 4), fill=(220, 50, 90))
    return dim_top(im, 150)
PRESS = base_press()
def dyn_press(im, t, ts, tag):
    arr = np.array(im); fl = .85 + .15 * math.sin(t * 13) * (1 if int(t * 3) % 7 == 0 else .2)
    glow(arr, 60, 150, 110, (255, 190, 100), .42 * fl); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if ts > 1.4:                                                    # red pen underlines the key phrase
        k = ease((ts - 1.4) / .8); x1 = 100 + int(70 * k); d.line([(100, 160), (x1, 160 + int(2 * math.sin(k * 20)))], fill=(230, 40, 50), width=2)
    for k in range(12):
        x = (k * 23 + t * 3) % W; y = 150 + 40 * math.sin(t * .5 + k) + k * 4; d.point((x, y), fill=(255, 220, 160))

# ---- Daft Punk clue 2 / outro: Paris at dusk, Eiffel tower with rotating beacon ----
def base_paris():
    a = np.zeros((H, W, 3), np.uint8); a[:215] = dgrad(W, 215, (10, 10, 44), (170, 70, 100), 12); a[215:266] = dgrad(W, 51, (50, 40, 90), (14, 14, 40), 5); a[266:] = (30, 26, 40)
    im = Image.fromarray(a); d = ImageDraw.Draw(im); d.ellipse((30, 40, 58, 68), fill=(255, 240, 210))
    x = -4
    while x < 150:                                                  # Haussmann-style buildings with mansard roofs
        w = rnd.randint(24, 36); h = rnd.randint(46, 72); c = rnd.choice([(176, 160, 150), (164, 150, 150), (150, 140, 150)])
        d.rectangle((x, 232 - h, x + w, 232), fill=c); d.polygon([(x - 2, 232 - h), (x + w + 2, 232 - h), (x + w - 4, 232 - h - 12), (x + 4, 232 - h - 12)], fill=(52, 56, 74))
        for wy in range(232 - h + 6, 226, 12):
            for wx in range(x + 4, x + w - 6, 9): d.rectangle((wx, wy, wx + 4, wy + 7), fill=(255, 205, 120) if rnd.random() < .6 else (50, 44, 70))
        x += w + 1
    for (x0, x1) in ((150, 275),):                                  # far bank
        d.rectangle((x0, 214, x1, 232), fill=(40, 36, 70))
    cx = 205                                                        # Eiffel tower
    for y in range(232, 70, -1):
        f = (232 - y) / 162; hw = int(36 * (1 - f) ** 1.7 + 2)
        d.line([(cx - hw, y), (cx - hw + 2, y)], fill=(70, 52, 60)); d.line([(cx + hw - 2, y), (cx + hw, y)], fill=(70, 52, 60))
    for (y0, wdt) in ((200, 24), (156, 14), (112, 8)): d.rectangle((cx - wdt, y0, cx + wdt, y0 + 4), fill=(96, 74, 80))
    for y in range(110, 232, 8):
        f = (232 - y) / 162; hw = int(36 * (1 - f) ** 1.7 + 2); d.line([(cx - hw, y), (cx + hw, y + 8)], fill=(60, 44, 52)); d.line([(cx + hw, y), (cx - hw, y + 8)], fill=(60, 44, 52))
    d.pieslice((cx - 16, 206, cx + 16, 250), 180, 360, fill=(30, 26, 40)); d.line([(cx, 72), (cx, 56)], fill=(110, 84, 90), width=2)
    d.rectangle((0, 232, W, 266), fill=(20, 44, 70)); d.rectangle((0, 262, W, 267), fill=(110, 96, 120))
    for y in range(268, H, 12):
        for x2 in range(0, W, 14):
            o = 7 if (y // 12) % 2 else 0; d.rectangle((x2 + o, y, x2 + o + 12, y + 10), fill=(44, 38, 56))
    return dim_top(im, 130)
PARIS = base_paris()
def dyn_paris(im, t, ts, tag):
    arr = np.array(im); a_ = t * 1.1
    for sgn in (-1, 1): beam(arr, 205, 205 + sgn * (40 + 90 * abs(math.sin(a_))), 52, 200, 3, 40, (255, 240, 180), .22)
    glow(arr, 205, 56, 30, (255, 250, 210), .7); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(26):                                             # tower sparkle
        if int(t * 8 + k * 3) % 9 == 0: d.point((205 + (k * 13) % 40 - 20, 80 + (k * 29) % 140), fill=WHITE)
    for k in range(7):
        y = 238 + k * 4; d.line([(80 - 20 + 3 * math.sin(t * 2 + k), y), (80 + 20, y)], fill=(255, 190, 120))
    bx = (t * 10) % 330 - 30; d.rectangle((bx, 246, bx + 16, 250), fill=(30, 24, 34)); d.point((bx + 3, 244), fill=(255, 220, 140))

# ---- Daft Punk clue 3: Coachella desert night, LED pyramid with lasers ----
def base_pyramid():
    a = np.zeros((H, W, 3), np.uint8); a[:250] = dgrad(W, 250, (4, 4, 26), (64, 24, 80), 11); a[250:] = (34, 22, 40)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for (base, amp, c) in ((236, 50, (24, 18, 50)), (246, 34, (18, 12, 38))):
        pts = [(0, 250)] + [(x, base - amp * (.5 + .5 * math.sin(x / 31 + base))) for x in range(0, W + 8, 8)] + [(W, 250)]; d.polygon(pts, fill=c)
    for (px, h) in ((16, 86), (252, 74)): palm(d, px, 262, h, 0, (10, 6, 22))
    d.rectangle((0, 262, W, 268), fill=(54, 36, 56))
    for y in range(270, H, 12): d.line([(0, y), (W, y)], fill=(40, 28, 46))
    return dim_top(im, 120)
PYRAMID = base_pyramid()
STARS2 = [(rnd.randint(0, W), rnd.randint(0, 150), rnd.random() * 6) for _ in range(60)]
def dyn_pyramid(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (x, y, p) in STARS2:
        if math.sin(t * 2 + p) > 0: d.point((x, y), fill=(255, 240, 210))
    ax, ay, bl, br, by_ = 135, 106, 62, 208, 250                    # LED pyramid, panels cycle colours
    rows = 9
    for r in range(rows):
        y0 = ay + (by_ - ay) * r / rows; y1 = ay + (by_ - ay) * (r + 1) / rows
        for c in range(r * 2 + 1):
            f0 = (r + 0.0) / rows; hw0 = (br - bl) / 2 * (r + 1) / rows; xs = ax - hw0 + c * (2 * hw0) / (r * 2 + 1); xe = xs + (2 * hw0) / (r * 2 + 1)
            hue = (t * .6 + r * .07 + c * .05) % 1.0
            col = [(255, 80, 170), (80, 235, 255), (255, 205, 60), (170, 120, 255)][int(hue * 4) % 4]
            on = math.sin(t * 6 + r * 1.3 + c * .9) > -.3
            d.rectangle((xs + 1, y0 + 1, xe - 1, y1 - 1), fill=col if on else (20, 16, 40))
    arr = np.array(im)
    for k in range(5):                                              # lasers from the apex
        ang = (k - 2) * 28 + 22 * math.sin(t * 1.6 + k); tx = ax + math.tan(math.radians(ang)) * 150
        beam(arr, ax, tx, ay, 20, 2, 18, [(255, 80, 170), (80, 235, 255), (255, 205, 60), (170, 120, 255), (255, 255, 255)][k], .35)
    glow(arr, ax, 190, 100, (160, 90, 255), .3); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(26):                                             # crowd with raised hands
        x = 4 + k * 10.5; b = int(2 * abs(math.sin(t * 5 + k))); d.ellipse((x - 3, 252 - b, x + 3, 258 - b), fill=(10, 6, 20)); d.rectangle((x - 4, 258 - b, x + 4, 270), fill=(10, 6, 20))
        if int(t * 3 + k) % 2: d.line([(x + 3, 258 - b), (x + 6, 249 - b)], fill=(10, 6, 20), width=2)

# ---- Daft Punk clue 4: Grammy stage (gold gramophones, flashes) ----
def base_grammy():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = dgrad(W, 266, (10, 6, 16), (70, 22, 34), 9); a[266:] = (90, 14, 34)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for x in range(0, W, 18): d.rectangle((x, 0, x + 9, 266), fill=(24, 8, 18))                     # velvet folds
    for y in range(270, H, 14): d.line([(0, y), (W, y)], fill=(120, 24, 48))
    d.rectangle((0, 262, W, 268), fill=(230, 180, 60))
    def gramophone(cx, base_y, sc):
        g = (255, 205, 70); gd = (170, 120, 20)
        d.rectangle((cx - 8 * sc, base_y - 6 * sc, cx + 8 * sc, base_y), fill=gd); d.rectangle((cx - 5 * sc, base_y - 14 * sc, cx + 5 * sc, base_y - 6 * sc), fill=g)
        d.ellipse((cx - 11 * sc, base_y - 20 * sc, cx + 11 * sc, base_y - 12 * sc), fill=g, outline=gd)
        d.polygon([(cx - 2 * sc, base_y - 18 * sc), (cx + 4 * sc, base_y - 18 * sc), (cx + 16 * sc, base_y - 40 * sc), (cx + 2 * sc, base_y - 34 * sc)], fill=g, outline=gd)
        d.ellipse((cx + 2 * sc, base_y - 46 * sc, cx + 20 * sc, base_y - 32 * sc), fill=(255, 240, 160), outline=gd)
    for (cx, by_, sc) in ((34, 240, 2), (236, 240, 2), (70, 206, 1), (200, 206, 1)): gramophone(cx, by_, sc); d.rectangle((cx - 12 * sc, by_, cx + 12 * sc, by_ + 22 * sc if sc == 2 else by_ + 12), fill=(30, 20, 30))
    return dim_top(im, 130)
GRAMMY = base_grammy()
def dyn_grammy(im, t, ts, tag):
    arr = np.array(im)
    for k, bx in enumerate((50, 135, 220)): beam(arr, bx, 135 + 50 * math.sin(t * 1.2 + k * 2), 0, 266, 6, 70, (255, 215, 120), .22)
    glow(arr, 135, 215, 90, (255, 190, 90), .35); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(40):                                             # gold confetti + camera flashes
        x = (k * 29 + math.sin(t + k) * 6) % W; y = (t * 30 + k * 47) % 270; d.rectangle((x, y, x + 1, y + 2), fill=(255, 205 + (k % 3) * 15, 70))
    for k in range(5):
        if int(t * 7 + k * 3) % 11 == 0: x = 20 + (k * 53) % 230; y = 190 + (k * 17) % 60; d.rectangle((x - 1, y - 1, x + 2, y + 2), fill=WHITE); d.line([(x - 4, y), (x + 5, y)], fill=WHITE)

# ---- Daft Punk clue 5: neon grid, two helmeted silhouettes ----
def base_robots():
    a = np.zeros((H, W, 3), np.uint8); a[:200] = dgrad(W, 200, (6, 6, 30), (92, 20, 100), 11); a[200:] = (12, 8, 34)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.pieslice((60, 120, 210, 270), 180, 360, fill=(255, 90, 150))
    for i in range(8): d.rectangle((60, 190 + i * 4, 210, 190 + i * 4 + i // 2), fill=(12, 8, 34))
    d.rectangle((0, 198, W, 200), fill=(80, 235, 255))
    return dim_top(im, 120)
ROBOTS = base_robots()
def dyn_robots(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(22):                                             # equalizer bars
        x = 6 + k * 12; hh = int(8 + 40 * abs(math.sin(t * 4 + k * .7)) * (.4 + .6 * abs(math.sin(k * 1.3 + t))))
        d.rectangle((x, 198 - hh, x + 7, 198), fill=(80, 235, 255) if k % 2 else (255, 80, 170))
    for k in range(-12, 13): d.line([(135, 200), (135 + k * 70, H)], fill=(160, 70, 230))
    for j in range(12):
        y = 200 + ((j + (t * .8) % 1) ** 2) * 2.4
        if y < H: d.line([(0, y), (W, y)], fill=(160, 70, 230))
    for k in range(40):
        x = (k * 61) % W; y = (k * 37) % 120
        if math.sin(t * 2 + k) > .3: d.point((x, y), fill=WHITE)

REG = {"brook": (BROOK, dyn_brooklyn), "sunset": (SUNSET, dyn_recap), "block": (BLOCK, dyn_block), "jazz": (JAZZ, dyn_jazz), "qb": (QB, dyn_qb),
       "battle": (BATTLE, dyn_battle), "press": (PRESS, dyn_press), "paris": (PARIS, dyn_paris), "pyramid": (PYRAMID, dyn_pyramid),
       "grammy": (GRAMMY, dyn_grammy), "robots": (ROBOTS, dyn_robots)}
_outro = (BROOK, dyn_outro) if EP["outro_scene"] == "brook" else REG[EP["outro_scene"]]
_hook = REG[EP.get("hook_scene", "brook")]
SCENES = [_hook, REG[PREV["scene"]], (SUNSET, dyn_win)] + [REG[c["scene"]] for c in CLUES] + [_outro]



# ======================= UI / winners / render (v4) =======================
def pill(d, cx, y0, y1, w, fill, outline=None):
    d.rectangle((cx - w // 2, y0, cx + w // 2, y1), fill=fill, outline=outline)

def ui_low(seg, ts, t):
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
    if seg == S_HOOK:
        if EP["hook"] == "b":                           # NEW HOOK (first 2 s): "Solo el 1% adivina este artista"
            on = ts > .45 or int(ts * 15) % 3 != 2
            if on:
                k = ease(ts / .25); dy = int((1 - k) * -24)
                lt(d, (135, 44 + dy), "SOLO EL", 24, WHITE, shadow=(255, 60, 150)); lt(d, (135, 100 + dy), "1%", 62, GOLD, shadow=(70, 230, 255))
                lt(d, (135, 146 + dy), "ADIVINA ESTE ARTISTA", 14, WHITE)
            if ts > 1.0: pill(d, 135, 300, 322, 222, (14, 8, 34), GOLD); lt(d, (135, 311), "¿LO ADIVINAS EN LA PISTA 1?", 11, WHITE)
            if ts > 1.4: lt(d, (135, 342), f"ARTISTA MISTERIOSO · PARTE {EP['part']}", 10, (255, 200, 120))
            return ui
        if ts < 1.0:                                    # hook A (original): "¿Quién es?" + "Solo los reales lo adivinan"
            if int(ts * 15) % 3 != 2:
                lt(d, (135, 70), "¿QUIÉN", 40, WHITE, shadow=(255, 60, 150)); lt(d, (135, 118), "ES?", 44, GOLD, shadow=(70, 230, 255))
            return ui
        k = ease((ts - 1.0) / .3); dy = int((1 - k) * -30)
        lt(d, (135, 46 + dy), "¡SOLO LOS REALES", 17, WHITE); lt(d, (135, 70 + dy), "LO ADIVINAN!", 24, GOLD, shadow=(120, 50, 0))
        if ts > 1.4: pill(d, 135, 300, 322, 222, (14, 8, 34), GOLD); lt(d, (135, 311), "¿LO ADIVINAS EN LA PISTA 1?", 11, WHITE)
        if ts > 1.9: lt(d, (135, 342), f"ARTISTA MISTERIOSO · PARTE {EP['part']}", 10, (255, 200, 120))
        if ts > 2.3: lt(d, (135, 362), "PERO PRIMERO... ¿QUIÉN FUE EL ANTERIOR?", 8, WHITE)
        return ui
    if seg == S_RECAP:                                   # "LA RESPUESTA DE AYER"
        if ts < REVEAL:
            k = ease(ts / .35); dy = int((1 - k) * -30)
            lt(d, (135, 46 + dy), "LA RESPUESTA DE AYER", 15, WHITE); lt(d, (135, 76 + dy), "FUE...", 34, GOLD, shadow=(120, 50, 0))
            if ts > .5: lt(d, (135, 112), "." * (1 + int(ts * 3) % 3), 28, (255, 120, 170))
        else:
            e = ts - REVEAL; k = ease(e / .25); dy = int((1 - k) * -20); lines = PREV["lines"]
            if len(lines) == 2:
                lt(d, (135, 46 + dy), lines[0], 34, WHITE, shadow=(255, 70, 190)); lt(d, (135, 90 + dy), lines[1], 46, GOLD, shadow=(120, 50, 0)); py = 120
            else:
                lt(d, (135, 40 + dy), "LA RESPUESTA DE AYER", 11, (255, 200, 120)); lt(d, (135, 82 + dy), lines[0], 56, GOLD, shadow=(120, 50, 0), anchor="mm"); py = 120
            if e > .5: pill(d, 135, py, py + 20, 196, (14, 8, 34), GOLD); lt(d, (135, py + 10), PREV["sub"], 9, (255, 200, 120))
            if ts > RECAP_LEN - 2.6:
                b = int(2 * math.sin(t * 10)); msg = "¡AHORA LOS GANADORES!" if WINNERS else "¡HOY: UN NUEVO ARTISTA!"
                pill(d, 135, 150 + b, 172 + b, 214, GOLD); lt(d, (135, 161 + b), msg, 11, DARK, shadow=(255, 230, 140))
        return ui
    if seg == S_WIN:
        k = ease(ts / .35); dy = int((1 - k) * -26)
        lt(d, (135, 24 + dy), f"GANADORES · PARTE {PREV['winners_part']}", 20, GOLD, shadow=(110, 50, 0))
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
        if ts > 2.0 and EP["outro_sign"]: pill(d, 135, 274, 292, 130, (14, 8, 34), GOLD); lt(d, (135, 283), EP["outro_sign"], 12, GOLD)
        if ts > 3.5:                                     # CTA: bring them back for tomorrow's answer + follow
            pill(d, 135, 300, 322, 238, GOLD); lt(d, (135, 311), "MAÑANA REVELO LA RESPUESTA", 10, DARK, shadow=(255, 230, 140))
            pill(d, 135, 330, 354, 222, (14, 8, 34), GOLD); lt(d, (135, 342), "SÍGUEME PARA VER LA RESPUESTA", 9, WHITE)
            lt(d, (135, 372), f"LOS QUE ACIERTEN SALEN EN LA PARTE {EP['next_part']}", 8, (255, 200, 120))
        return ui
    c = CLUES[seg - S_C1]; n = c["n"]; seg_len = T[seg + 1] - T[seg]; last = seg == S_C1 + NCL - 1; col_ = diffc(n, NCL)
    k = ease(ts / .3); dy = int((1 - k) * -30)
    lt(d, (135, 46 + dy), f"PISTA {n} / {NCL}", 24, GOLD, shadow=(110, 50, 0))
    bw = 26 if NCL >= 5 else 32; step = bw + 4; x0b = 135 - (NCL * step - 4) // 2
    for i in range(NCL):
        fill = diffc(i + 1, NCL) if i < n and ts > .45 + i * .11 else (50, 36, 80)
        d.rectangle((x0b + i * step, 66 + dy, x0b + i * step + bw, 70 + dy), fill=fill)
    lt(d, (135, 80 + dy), f"DIFICULTAD: {c['diff']}", 11, col_)
    lt(d, (135, 92 + dy), f"VALE {c['pts']} PUNTO{'S' if c['pts'] > 1 else ''}", 10, (255, 230, 170))
    if ts > .9:
        f = F(18); w = int(d.textlength(c["chip"], font=f)) + 16; x0 = 135 - w // 2; fl = ts < 1.0
        d.rectangle((x0 - 2, 100, x0 + w + 2, 126), fill=(255, 205, 60)); d.rectangle((x0, 102, x0 + w, 124), fill=WHITE if fl else (14, 8, 34))
        lt(d, (135, 114), c["chip"], 18, DARK if fl else GOLD, shadow=(60, 30, 0))
    if ts > .6:
        rem = min(max(1 - max(0, ts - TW0) / (seg_len - TW0 - .2), 0), 1); urgent = rem < .3 and int(t * 6) % 2
        d.rectangle((12, 12, 258, 18), fill=(14, 8, 34)); d.rectangle((14, 14, 14 + int(242 * rem), 16), fill=(255, 255, 255) if urgent else col_)
    if seg in BANNERS and BANNER_T <= ts < BANNER_T + 1.6:
        e = ts - BANNER_T; kk = ease(e / .2); by = 208 + int((1 - kk) * 40) + int(2 * math.sin(t * 12))
        pill(d, 135, by, by + 22, 232, GOLD); lt(d, (135, by + 11), BANNERS[seg], 11, DARK, shadow=(255, 230, 140))
    if last and ts >= seg_len - 3.0:                     # 3-2-1 countdown on the easiest clue
        num = int(math.ceil(seg_len - ts)); fr = (seg_len - ts) % 1.0; sz = 64 + int(14 * (1 - fr))
        lt(d, (135, 192), str(max(num, 1)), sz, WHITE, shadow=(255, 60, 150))
        lt(d, (135, 236), "¡ÚLTIMA OPORTUNIDAD!" if num == 3 else "¡ESCRÍBELO YA!", 11, GOLD)
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
        badge = " · ".join(([SPECIAL[r["h"]]] if r["h"] in SPECIAL else []) + ([f"♥{r['lk']}"] if r["lk"] else []) + (["TT"] if r["pl"] == "TT" else []))
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
    for i in range(1, S_OUT + 1):
        if t >= T[i]: s_ = i
    return s_

def shake_amp(seg, ts):
    if seg == S_RECAP:
        if .4 < ts < REVEAL: return 2 + 7 * ((ts - .4) / max(REVEAL - .4, .5)) ** 2
        if REVEAL <= ts < REVEAL + .6: return 22 * (1 - (ts - REVEAL) / .6)
    if S_C1 <= seg < S_C1 + NCL:
        if 1.0 < ts < 1.3: return 10 * (1 - (ts - 1.0) / .3)
        if seg == S_C1 + NCL - 1 and T[seg + 1] - T[seg] - ts <= 3.0:       # countdown beats
            fr = (T[seg + 1] - T[seg] - ts) % 1.0; return 8 * max(0, 1 - (1 - fr) / .25)
    return 0

def glitch(img, t, strength):
    arr = np.array(img); rng = np.random.default_rng(int(t * 30) + 11)
    arr[..., 0] = np.roll(arr[..., 0], int(18 * strength), 1); arr[..., 2] = np.roll(arr[..., 2], -int(18 * strength), 1)
    for _ in range(7):
        y = int(rng.integers(0, FH - 120)); h = int(rng.integers(20, 120)); arr[y:y + h] = np.roll(arr[y:y + h], int(rng.integers(-140, 140)), 1)
    return Image.fromarray(arr)

SHIFT = 70
IS_CLUE = lambda seg: S_C1 <= seg < S_C1 + NCL
def render(t):
    seg = seg_of(t); ts = t - T[seg]
    base, dyn = SCENES[seg]
    im = base.copy(); dyn(im, t, ts, None)
    if seg not in (S_RECAP, S_WIN): notes(im, t)
    scn = CLUES[seg - S_C1]["scene"] if IS_CLUE(seg) else None
    if seg == S_RECAP: prev_draw(im, t, ts)
    elif seg == S_WIN: snoop(im, t)
    elif scn == "battle":
        sil(im, 98, 266, t, q=False); im.paste(SPR_HAT_M, (178 - 24, 266 - 96), SPR_HAT_M); qmark(im, 134, 150 + int(3 * math.sin(t * 3)), 2)
    elif scn == "robots":                                    # last clue: the two helmeted silhouettes finally show up
        b1 = 1 if int(t * 4.5) % 2 else 0; im.paste(SPR_ROBOT_A, (98 - 24, 266 - 96 + b1), SPR_ROBOT_A); im.paste(SPR_ROBOT_B, (172 - 24, 266 - 96 + 1 - b1), SPR_ROBOT_B)
    else: sil(im, 135, 266, t)
    if seg == S_WIN:
        im2 = Image.new("RGB", (W, H), (20, 10, 38)); im2.paste(im, (0, -SHIFT)); im = im2
    seg_len = (T[seg + 1] if seg < S_OUT else END) - T[seg]
    punch = .03 * max(0, 1 - (ts - 1.0) / .25) if IS_CLUE(seg) and ts > 1.0 else 0
    z = 1.04 + .05 * (ts / seg_len) + punch
    big = im.resize((FW, FH), Image.NEAREST)
    cw, ch = FW / z, FH / z; amp = shake_amp(seg, ts); rg = np.random.default_rng(int(t * 30))
    ox = (FW - cw) / 2 + (math.sin(t * .5) * 6 if seg else 0) + rg.uniform(-amp, amp); oy = (FH - ch) * .55 + rg.uniform(-amp, amp)
    ox = min(max(ox, 0), FW - cw); oy = min(max(oy, 0), FH - ch)
    big = big.crop((int(ox), int(oy), int(ox + cw), int(oy + ch))).resize((FW, FH), Image.NEAREST)
    ui = ui_low(seg, ts, t).resize((FW, FH), Image.NEAREST)
    big = big.convert("RGBA"); big.alpha_composite(ui); big = big.convert("RGB")
    if IS_CLUE(seg): draw_panel_text(big, seg, ts)
    if seg == S_WIN and WINNERS: draw_winners(big, ts)
    if seg == S_HOOK and (t < 1.0 if EP["hook"] == "a" else t < .5): big = glitch(big, t, 1.0)
    elif seg == S_RECAP and REVEAL <= ts < REVEAL + .25: big = glitch(big, t, .6)
    if seg == S_RECAP and REVEAL <= ts < REVEAL + .3:
        big = Image.blend(big, Image.new("RGB", (FW, FH), (255, 255, 255)), .9 * (1 - (ts - REVEAL) / .3))
    for i in range(1, S_OUT + 1):
        if i > 1 and T[i] == T[i - 1]: continue
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

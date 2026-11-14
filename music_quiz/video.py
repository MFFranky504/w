import os
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
    if kind == "tyler": return tyler_draw(im, t, ts)
    if kind == "freddie_gba": return freddie_gba(im, t, ts)
    if kind == "kurt_gba": return kurt_gba(im, t, ts)
    if kind == "mic": return mic_draw(im, t, ts)
    if kind == "nas2": return nas2_draw(im, t, ts)
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

# ---- Daft Punk clue 1: 1978 disco floor with mirror ball ----
def base_disco():
    a = np.zeros((H, W, 3), np.uint8); a[:236] = dgrad(W, 236, (30, 8, 58), (160, 34, 120), 11); a[236:] = (20, 10, 30)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for (x0, x1) in ((6, 40), (230, 264)):
        d.rectangle((x0, 170, x1, 236), fill=(16, 10, 24), outline=(90, 70, 110))
        for cy_ in (186, 218): d.ellipse((x0 + 4, cy_ - 11, x1 - 4, cy_ + 11), fill=(34, 26, 48), outline=(130, 110, 150)); d.ellipse((x0 + 12, cy_ - 3, x1 - 12, cy_ + 3), fill=(80, 60, 110))
    d.line([(135, 0), (135, 126)], fill=(120, 110, 140))
    return dim_top(im, 130)
DISCO = base_disco()
def dyn_disco(im, t, ts, tag):
    d = ImageDraw.Draw(im); cx, cy, r = 135, 148, 21
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 150, 170), outline=(230, 230, 250))
    for k in range(-3, 4):
        a_ = t * 1.5 + k * .45; w = int(abs(math.cos(a_)) * r)
        d.ellipse((cx - w, cy - r, cx + w, cy + r), outline=(90, 90, 120))
    for j in (-14, -7, 0, 7, 14): hw = int(math.sqrt(max(r * r - j * j, 0))); d.line([(cx - hw, cy + j), (cx + hw, cy + j)], fill=(100, 100, 130))
    for k in range(40):                                              # light spots flying around the room
        ang = t * .8 + k * .63; rr = 60 + (k * 37) % 120; x = cx + math.cos(ang) * rr * 1.1; y = 120 + math.sin(ang * 1.3 + k) * 70 + rr * .25
        if 0 <= x < W and 0 <= y < 232 and math.sin(t * 4 + k) > -.2: d.rectangle((x, y, x + 2, y + 2), fill=[(255, 240, 200), (255, 120, 200), (120, 230, 255)][k % 3])
    for i in range(10):                                              # lit dance-floor tiles
        for j in range(3):
            c = [(255, 80, 170), (80, 235, 255), (255, 205, 60), (170, 120, 255)][int(i + j + t * 4) % 4] if math.sin(t * 5 + i * 1.7 + j) > -.4 else (30, 14, 44)
            d.rectangle((i * 27 + 1, 238 + j * 9, i * 27 + 25, 238 + j * 9 + 7), fill=c)
    arr = np.array(im); glow(arr, cx, cy, 90, (255, 150, 220), .25); im.paste(Image.fromarray(arr))

# ---- Daft Punk clue 3: 1994 rave tent (lasers, strobes, DJ booth) ----
def base_rave():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = dgrad(W, 266, (4, 6, 20), (34, 12, 64), 10); a[266:] = (10, 8, 20)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for k in range(-4, 5): d.line([(135, 0), (135 + k * 40, 90)], fill=(60, 56, 90))                 # tent truss
    d.line([(0, 90), (W, 90)], fill=(60, 56, 90)); d.line([(0, 20), (135, 0), (W, 20)], fill=(60, 56, 90))
    d.rectangle((184, 226, 262, 266), fill=(24, 18, 36), outline=(110, 100, 140)); d.rectangle((188, 220, 258, 228), fill=(40, 32, 60))
    for cx_ in (204, 242): d.ellipse((cx_ - 9, 222, cx_ + 9, 230), fill=(14, 10, 20), outline=(160, 150, 190))
    for y in range(268, H, 12): d.line([(0, y), (W, y)], fill=(26, 18, 40))
    return dim_top(im, 120)
RAVE = base_rave()
def dyn_rave(im, t, ts, tag):
    arr = np.array(im)
    for k in range(6):
        ang = (k - 2.5) * 22 + 26 * math.sin(t * 1.9 + k); col = [(255, 60, 160), (60, 235, 255), (120, 255, 120), (255, 210, 60), (170, 110, 255), (255, 255, 255)][k]
        beam(arr, 135 + (k - 2.5) * 40, 135 + (k - 2.5) * 40 + math.tan(math.radians(ang)) * 180, 8, 260, 2, 30, col, .33)
    if int(t * 6) % 9 == 0: arr = np.clip(arr + 70, 0, 255).astype(np.uint8)                        # strobe
    glow(arr, 135, 230, 120, (150, 80, 255), .3); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for cx_ in (204, 242): a_ = t * 5; d.line([(cx_, 226), (cx_ + 6 * math.cos(a_), 226 + 3 * math.sin(a_))], fill=GOLD)
    for k in range(30):
        x = 4 + k * 9; b = int(2 * abs(math.sin(t * 5 + k))); d.ellipse((x - 3, 248 - b, x + 3, 254 - b), fill=(8, 6, 18)); d.rectangle((x - 4, 254 - b, x + 4, 270), fill=(8, 6, 18))
        if int(t * 3 + k) % 2: d.line([(x + 3, 254 - b), (x + 6, 245 - b)], fill=(8, 6, 18), width=2)
    for k in range(6):
        x = (k * 51 + t * 7) % W; y = 200 + 30 * math.sin(t * .6 + k); d.ellipse((x - 14, y - 3, x + 14, y + 3), outline=(100, 90, 130))

# ======================= v6: Tyler, The Creator (detailed sprite) + garden + background gags =======================
def make_tyler():
    """Igor-era look: platinum bob wig, round tinted glasses, pastel pink suit, baby-blue slacks, yellow sneakers, teal polka-dot tie."""
    w, h = 72, 122; SK = (152, 98, 66); SKS = (122, 76, 52); SKL = (170, 116, 82)
    PINK = (255, 150, 196); PINKS = (232, 118, 170); PINKL = (255, 192, 222); BLUE = (172, 212, 255); BLUES = (136, 178, 238)
    HAIR = (250, 226, 140); HAIRL = (255, 248, 214); HAIRS = (224, 188, 100); YEL = (255, 214, 60); WHITE_ = (250, 248, 244)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x0 in (16, 40):                                              # slacks + crease
        d.rectangle((x0, 76, x0 + 15, 108), fill=BLUE); d.rectangle((x0 + 11, 76, x0 + 15, 108), fill=BLUES); d.line([(x0 + 6, 80), (x0 + 6, 107)], fill=(200, 228, 255))
    d.rectangle((16, 70, 56, 82), fill=BLUE)
    for x0 in (14, 38):                                              # striped socks + chunky yellow sneakers
        for k in range(3): d.rectangle((x0 + 2, 106 + k * 2, x0 + 17, 107 + k * 2), fill=(240, 70, 80) if k % 2 == 0 else WHITE_)
        d.rounded_rectangle((x0 - 2, 111, x0 + 20, 121), 4, fill=YEL); d.rectangle((x0 - 2, 118, x0 + 20, 121), fill=WHITE_); d.rectangle((x0 + 10, 111, x0 + 20, 114), fill=(255, 240, 150))
        for k in range(3): d.point((x0 + 6 + k * 3, 112), fill=WHITE_)
        d.rectangle((x0 - 2, 116, x0 + 20, 117), fill=(240, 150, 40))
    d.rounded_rectangle((8, 38, 64, 90), 7, fill=PINK); d.rectangle((54, 42, 64, 88), fill=PINKS)             # jacket + shade
    d.rectangle((0, 44, 11, 84), fill=PINK); d.rectangle((61, 44, 72, 84), fill=PINK); d.rectangle((66, 46, 72, 84), fill=PINKS)
    d.rectangle((0, 80, 11, 86), fill=WHITE_); d.rectangle((61, 80, 72, 86), fill=WHITE_)                          # white cuffs
    d.rectangle((1, 86, 10, 95), fill=SK); d.rectangle((62, 86, 71, 95), fill=SK); d.rectangle((1, 92, 10, 95), fill=SKS)
    d.polygon([(30, 38), (42, 38), (36, 62)], fill=WHITE_)                                                         # shirt
    d.polygon([(30, 38), (24, 62), (34, 62), (30, 38)], fill=PINKL); d.polygon([(42, 38), (48, 62), (38, 62), (42, 38)], fill=PINKL)   # lapels
    d.polygon([(34, 40), (38, 40), (40, 64), (36, 70), (32, 64)], fill=(56, 214, 204))                             # tie
    for (tx, ty) in ((35, 46), (37, 52), (35, 58), (37, 64)): d.point((tx, ty), fill=YEL)
    d.polygon([(14, 58), (22, 58), (18, 54)], fill=YEL); d.rectangle((14, 58, 22, 60), fill=(255, 240, 150))        # pocket square
    for by in (70, 78): d.rectangle((35, by, 37, by + 1), fill=YEL)                                                # buttons
    d.line([(36, 62), (36, 90)], fill=PINKS); d.line([(8, 88), (64, 88)], fill=PINKS)
    d.rectangle((30, 34, 42, 42), fill=SKS)                                                                        # neck (short)
    d.ellipse((20, 10, 52, 42), fill=SK); d.polygon([(44, 14), (52, 24), (50, 36), (44, 40)], fill=SKS); d.ellipse((22, 18, 30, 30), fill=SKL)
    d.ellipse((17, 22, 23, 32), fill=SK); d.ellipse((49, 22, 55, 32), fill=SKS); d.ellipse((16, 30, 19, 34), fill=(255, 215, 80)); d.ellipse((53, 30, 56, 34), fill=(255, 215, 80))   # ears + earrings
    d.ellipse((12, 0, 60, 30), fill=HAIR)                                                                          # wig: crown
    d.rectangle((12, 12, 24, 42), fill=HAIR); d.rectangle((48, 12, 60, 42), fill=HAIR)                              # side panels to the jaw
    d.rectangle((12, 36, 24, 42), fill=(255, 170, 212)); d.rectangle((48, 36, 60, 42), fill=(255, 170, 212))      # pastel-pink tips
    d.rectangle((50, 10, 60, 40), fill=HAIRS)
    d.polygon([(20, 8), (52, 8), (52, 18), (46, 14), (40, 19), (34, 14), (28, 19), (22, 14), (20, 18)], fill=HAIR)  # fringe
    for (x0, y0, x1, y1) in ((24, 4, 34, 6), (16, 14, 18, 26), (26, 11, 30, 12), (14, 30, 16, 36)): d.rectangle((x0, y0, x1, y1), fill=HAIRL)
    for cx_ in (28, 44):                                                                                           # round tinted glasses
        d.ellipse((cx_ - 7, 18, cx_ + 7, 32), fill=(255, 215, 80)); d.ellipse((cx_ - 5, 20, cx_ + 5, 30), fill=(126, 74, 170)); d.rectangle((cx_ - 4, 21, cx_ - 2, 23), fill=(232, 205, 255)); d.rectangle((cx_ + 1, 27, cx_ + 3, 28), fill=(170, 120, 215))
    d.line([(35, 24), (37, 24)], fill=(255, 215, 80), width=1)
    d.rectangle((35, 28, 37, 31), fill=SKS)                                                                        # nose
    d.rectangle((28, 33, 44, 38), fill=(70, 24, 34)); d.rectangle((29, 34, 43, 36), fill=WHITE_); d.rectangle((28, 37, 44, 38), fill=(196, 92, 96)); d.line([(36, 34), (36, 36)], fill=(200, 200, 205))   # big grin
    return _outline_sil(im)
TYLER_COL, TYLER_SIL = make_tyler()

def sunflower(d, x, y, r=5, t=0.0, petals=10):
    for k in range(petals):
        a = k / petals * 6.283 + t; d.ellipse((x + math.cos(a) * r - 2, y + math.sin(a) * r - 2, x + math.cos(a) * r + 2, y + math.sin(a) * r + 2), fill=(255, 214, 60))
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(120, 70, 30)); d.point((x - 1, y - 1), fill=(170, 110, 50))
def cloud(d, x, y, w, col=(255, 255, 255), sh=(220, 230, 255)):
    for (dx, dy, r) in ((0, 0, 8), (w // 3, -4, 10), (2 * w // 3, 0, 9), (w, 2, 7)): d.ellipse((x + dx - r, y + dy - r // 2 - 1, x + dx + r, y + dy + r // 2 + 4), fill=col)
    d.rectangle((x - 4, y + 4, x + w + 6, y + 8), fill=sh)
def shades(d, cx, cy, w=7, col=(20, 14, 30)):
    d.rectangle((cx - w, cy - 1, cx - 1, cy + 2), fill=col); d.rectangle((cx + 1, cy - 1, cx + w, cy + 2), fill=col); d.line([(cx - 1, cy), (cx + 1, cy)], fill=col)
def bee(d, x, y, t):
    d.ellipse((x - 3, y - 2, x + 3, y + 2), fill=(255, 214, 60)); d.rectangle((x - 1, y - 2, x, y + 2), fill=(20, 14, 20)); d.rectangle((x + 1, y - 2, x + 2, y + 2), fill=(20, 14, 20))
    d.ellipse((x - 3, y - 6 + int(1.5 * math.sin(t * 40)), x + 1, y - 2), fill=(230, 245, 255))

def base_garden():
    a = np.zeros((H, W, 3), np.uint8)
    a[:130] = dgrad(W, 130, (255, 160, 215), (200, 190, 255), 9); a[130:240] = dgrad(W, 110, (200, 190, 255), (255, 236, 190), 9); a[240:] = (70, 170, 96)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for i, c in enumerate([(255, 90, 100), (255, 160, 70), (255, 224, 80), (110, 220, 130), (90, 190, 255), (150, 120, 255)]):   # rainbow
        d.arc((-40 + i * 3, 118 + i * 3, 150 - i * 3, 330 - i * 3), 180, 360, fill=c, width=4)
    for (base, amp, c) in ((218, 22, (150, 220, 160)), (232, 18, (96, 196, 118)), (246, 14, (64, 168, 92))):
        pts = [(0, 266)] + [(x, base - amp * (.5 + .5 * math.sin(x / 38 + base))) for x in range(0, W + 8, 8)] + [(W, 266)]; d.polygon(pts, fill=c)
    for _ in range(110):                                              # flower meadow
        x = rnd.randint(0, W); y = rnd.randint(224, 262); c = rnd.choice([(255, 90, 150), (255, 224, 80), (255, 255, 255), (170, 130, 255), (255, 140, 60), (90, 200, 255)])
        d.line([(x, y), (x, y + 4)], fill=(40, 130, 70)); d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=c); d.point((x, y), fill=(255, 240, 150))
    for x in range(0, W, 9):                                          # picket fence
        d.rectangle((x, 244, x + 5, 266), fill=(250, 248, 244)); d.polygon([(x, 244), (x + 5, 244), (x + 2, 240)], fill=(250, 248, 244)); d.rectangle((x + 4, 246, x + 5, 266), fill=(214, 220, 236))
    d.rectangle((0, 250, W, 252), fill=(214, 220, 236)); d.rectangle((0, 258, W, 260), fill=(214, 220, 236))
    for y in range(268, H, 10): d.rectangle((0, y, W, y + 4), fill=(80, 184, 106) if (y // 10) % 2 else (70, 170, 96))
    for k, (sx_, sy_) in enumerate(((135, 282), (122, 298), (146, 314), (128, 330), (144, 346), (134, 362))):          # stepping stones
        d.ellipse((sx_ - 9, sy_ - 4, sx_ + 9, sy_ + 4), fill=(206, 196, 186), outline=(150, 140, 136)); d.ellipse((sx_ - 6, sy_ - 3, sx_ + 4, sy_ + 1), fill=(226, 218, 208))
    for _ in range(46):                                               # big lawn flowers + mushrooms
        x = rnd.randint(4, W - 4); y = rnd.randint(276, 392)
        if abs(x - 135) < 16: continue
        if rnd.random() < .18:
            d.rectangle((x - 1, y, x + 1, y + 5), fill=(250, 240, 230)); d.ellipse((x - 5, y - 4, x + 5, y + 2), fill=(240, 70, 80)); d.point((x - 2, y - 2), fill=WHITE); d.point((x + 2, y - 1), fill=WHITE)
        else:
            c = rnd.choice([(255, 90, 150), (255, 224, 80), (255, 255, 255), (170, 130, 255), (255, 140, 60), (90, 200, 255)])
            d.line([(x, y), (x, y + 7)], fill=(40, 130, 70)); [d.ellipse((x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2), fill=c) for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3))]; d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(255, 224, 80))
    return im
GARDEN = base_garden()
BIGFL = [(24, 214, 16, .0), (66, 206, 12, 1.1), (222, 210, 14, 2.1), (254, 216, 11, 3.0)]
def dyn_garden(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (cx_, cy_, w_, sp) in ((40, 36, 30, 6), (150, 52, 26, 4), (230, 24, 28, 5)):                          # drifting clouds (one wears shades)
        x = (cx_ + t * sp) % (W + 80) - 40; cloud(d, x, cy_, w_)
        if cx_ == 150: shades(d, x + w_ // 2 + 2, cy_ + 2, 5); d.arc((x + w_ // 2 - 3, cy_ + 3, x + w_ // 2 + 5, cy_ + 9), 20, 160, fill=(120, 80, 130))
    sx, sy = 240, 176; d.ellipse((sx - 12, sy - 12, sx + 12, sy + 12), fill=(255, 224, 80), outline=(255, 160, 60))   # sun with sunglasses and a grin
    for k in range(12): a = k / 12 * 6.283 + t * .5; d.line([(sx + math.cos(a) * 15, sy + math.sin(a) * 15), (sx + math.cos(a) * 21, sy + math.sin(a) * 21)], fill=(255, 200, 70), width=2)
    shades(d, sx, sy - 2, 7); d.arc((sx - 6, sy + 1, sx + 6, sy + 9), 20, 160, fill=(150, 70, 40), width=2)
    for (x, y, r, ph) in BIGFL:                                       # swaying giant flowers
        sw = 3 * math.sin(t * 1.4 + ph); d.line([(x, 262), (x + sw, y)], fill=(40, 140, 74), width=3); d.ellipse((x + 2, 238, x + 12, 244), fill=(60, 170, 90)); sunflower(d, x + sw, y, r * .45, t * .4 + ph)
    for k in range(3):                                                # bees (figure-8) and butterflies
        bee(d, 135 + 60 * math.sin(t * 1.3 + k * 2), 180 + 18 * math.sin(t * 2.6 + k * 2) + k * 10, t)
    for k in range(2):
        x = 60 + k * 120 + 20 * math.sin(t * .8 + k); y = 150 + 20 * math.sin(t * 1.5 + k * 3); f = abs(math.sin(t * 9 + k))
        d.ellipse((x - 6, y - 4, x - 1, y + 2 + 2 * f), fill=(255, 130, 190)); d.ellipse((x + 1, y - 4, x + 6, y + 2 + 2 * f), fill=(150, 190, 255)); d.line([(x, y - 3), (x, y + 3)], fill=(60, 30, 60))
    ex = (t * 9) % (W + 30) - 15; d.ellipse((ex - 3, 262, ex + 3, 266), fill=(235, 50, 60)); d.point((ex - 1, 263), fill=(20, 10, 20)); d.point((ex + 1, 264), fill=(20, 10, 20))   # ladybug on the fence
    gx = (t * 3.5) % (W + 30) - 15; gy = 396                                      # snail crossing the lawn
    d.ellipse((gx - 8, gy - 8, gx + 2, gy + 2), fill=(230, 150, 70), outline=(150, 80, 30)); d.arc((gx - 6, gy - 6, gx, gy), 0, 270, fill=(150, 80, 30)); d.rectangle((gx - 10, gy, gx + 8, gy + 3), fill=(190, 200, 120))
    d.line([(gx + 8, gy), (gx + 11, gy - 5)], fill=(190, 200, 120)); d.point((gx + 11, gy - 6), fill=(20, 10, 20))
    for k in range(18):                                                           # sprinkler arcs
        a = (t * 2 + k * .09) % 1.0; sxx = 38 + 34 * math.cos(math.pi * (.2 + .6 * ((t * .6) % 1))) * a * 1.4; syy = 336 - 40 * a * (1 - a) * 4
        d.point((sxx, syy), fill=(150, 220, 255))
    d.rectangle((36, 336, 40, 342), fill=(90, 90, 110)); d.rectangle((34, 342, 42, 344), fill=(60, 60, 80))
    d.polygon([(214, 342), (232, 342), (223, 318)], fill=(230, 50, 70)); d.ellipse((216, 336, 230, 352), fill=(250, 220, 200)); d.polygon([(216, 346), (230, 346), (223, 362)], fill=(250, 250, 250))   # garden gnome with shades
    shades(d, 223, 343, 5); d.rectangle((216, 362, 230, 372), fill=(60, 100, 200))
    arr = np.array(im)
    if ts < REVEAL:
        k = min(1, ts / 2.2)
        for kk, bx in enumerate((50, 220)): beam(arr, bx, 135 + math.sin(t * 3 + kk * 3) * 40, 0, 266, 4, 40, (255, 90, 200), .22 * k)
        arr = (arr * (1 - .28 * k) + np.array([40, 10, 70]) * .28 * k).astype(np.uint8)       # the garden dims while the mystery builds
    else:
        beam(arr, 135, 135, 0, 266, 10, 90, (255, 240, 170), .3 * min(1, (ts - REVEAL) / .3)); glow(arr, 135, 200, 100, (255, 200, 240), .45)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if ts >= REVEAL:
        e = ts - REVEAL
        for (vx, vy, c) in CONF2:
            px = 135 + vx * 1.6 * min(e, 1.6) ** .8; py = 190 + vy * 2.2 * min(e, 1.2) + 40 * e * e
            if 0 <= px < W and 0 <= py < H: d.rectangle((px, py, px + 2, py + 2), fill=c)
        for k in range(14):                                           # falling petals + hearts
            x = (k * 41 + math.sin(t * 2 + k) * 8) % W; y = ((t - T[1]) * 26 + k * 37) % 270; c = [(255, 130, 190), (255, 224, 80), (255, 255, 255)][k % 3]
            if k % 4 == 0: d.rectangle((x, y, x + 1, y + 1), fill=(255, 70, 110)); d.rectangle((x + 3, y, x + 4, y + 1), fill=(255, 70, 110)); d.rectangle((x, y + 1, x + 4, y + 2), fill=(255, 70, 110))
            else: d.ellipse((x, y, x + 3, y + 2), fill=c)
def tyler_draw(im, t, ts):
    if ts < REVEAL:
        im.paste(TYLER_SIL, (135 - 36, 266 - 122 + (1 if int(t * 2.2) % 2 else 0)), TYLER_SIL); qmark(im, 134, 124 + int(3 * math.sin(t * 4)), 3)
    else:
        e = ts - REVEAL; jump = -int(abs(16 * math.exp(-e * 3.2) * math.cos(e * 15))); bob = 1 if int(t * 2.6) % 2 else 0
        y0 = 266 - 122 + jump + bob; im.paste(TYLER_COL, (135 - 36, y0), TYLER_COL)
        d = ImageDraw.Draw(im); sw = 2 * math.sin(t * 3)                                         # flower in his hand + glasses glint
        d.line([(135 - 33, y0 + 92), (135 - 34 + sw, y0 + 70)], fill=(40, 140, 74), width=2); sunflower(d, 135 - 34 + sw, y0 + 66, 5, t)
        g = int((t * 6) % 12)
        if g < 3: d.rectangle((135 - 11 + g * 3, y0 + 20, 135 - 10 + g * 3, y0 + 23), fill=(255, 255, 255)); d.point((135 - 10 + g * 3, y0 + 19), fill=(255, 255, 255))

# ---------------- background gags / extra detail (drawn on top of each scene's own animation) ----------------
def _cat(d, x, y, t, col=(18, 10, 28), eye=(255, 220, 60), tail=True):
    d.ellipse((x - 6, y - 5, x + 6, y + 6), fill=col); d.ellipse((x - 4, y - 11, x + 4, y - 3), fill=col)
    d.polygon([(x - 4, y - 10), (x - 2, y - 14), (x, y - 10)], fill=col); d.polygon([(x + 4, y - 10), (x + 2, y - 14), (x, y - 10)], fill=col)
    if int(t * 1.1) % 5: d.point((x - 2, y - 7), fill=eye); d.point((x + 2, y - 7), fill=eye)
    if tail:
        sw = 4 * math.sin(t * 3); d.line([(x + 6, y + 3), (x + 11, y + 1), (x + 12 + sw, y - 5)], fill=col, width=2)
def _person(d, x, y, col, t=0.0, ph=0.0, arms=True):
    b = int(2 * abs(math.sin(t * 5 + ph))); d.ellipse((x - 3, y - 14 - b, x + 3, y - 8 - b), fill=col); d.rectangle((x - 4, y - 8 - b, x + 4, y), fill=col)
    if arms and int(t * 3 + ph) % 2: d.line([(x + 3, y - 7 - b), (x + 6, y - 15 - b)], fill=col, width=2)
def extra_hook(im, t, ts):
    d = ImageDraw.Draw(im); x = (t * 22) % (W + 90) - 45; y = 36 + 8 * math.sin(t * 1.2)             # UFO abducting a vinyl record
    if 50 < x < 220:
        for k in range(14):
            yy = y + 6 + k * 12; hw = 3 + k * 1.6
            if yy < 236: d.point((x - hw, yy), fill=(255, 255, 170)); d.point((x + hw, yy), fill=(255, 255, 170))
        ry = 232 - ((t * 34) % 190); d.ellipse((x - 5, ry - 2, x + 5, ry + 2), fill=(18, 14, 24), outline=(220, 60, 100))
    d.ellipse((x - 14, y - 3, x + 14, y + 4), fill=(170, 182, 206), outline=(90, 100, 130)); d.ellipse((x - 7, y - 10, x + 7, y), fill=(130, 232, 255), outline=(60, 140, 170))
    for k in range(3): d.point((x - 8 + k * 8, y + 1), fill=[(255, 90, 170), (255, 224, 80), (110, 255, 160)][int(t * 6 + k) % 3])
    d.rectangle((215, 238, 217, 266), fill=(90, 70, 60)); d.rectangle((194, 222, 238, 238), fill=(24, 96, 60), outline=WHITE)   # roadside sign
    d.fontmode = "1"; d.text((216, 230), "¿QUIÉN?", font=F(7), fill=WHITE if int(t * 2.5) % 2 else GOLD, anchor="mm")
    _cat(d, 31, 205, t)                                                                                   # sleepy cat up the palm
    s = (t * .7) % 4.5
    if s < 1: d.line([(250 - s * 80, 8 + s * 30), (258 - s * 80, 5 + s * 30)], fill=WHITE, width=1); d.point((250 - s * 80, 8 + s * 30), fill=(255, 255, 200))
def extra_disco(im, t, ts):
    d = ImageDraw.Draw(im); arr = np.array(im)
    for k in range(4): beam(arr, 135, 135 + 120 * math.sin(t * .9 + k * 1.6), 150, 236, 2, 40, [(255, 100, 200), (100, 230, 255), (255, 220, 80), (180, 130, 255)][k], .22)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    sx = (t * 34) % (W + 70) - 35; sy = 236                                                              # roller skater with an afro
    ph = math.sin(t * 9); d.ellipse((sx - 7, sy - 36, sx + 7, sy - 22), fill=(70, 38, 24)); d.ellipse((sx - 3, sy - 30, sx + 3, sy - 24), fill=(150, 98, 66))
    d.rectangle((sx - 4, sy - 22, sx + 4, sy - 10), fill=(255, 90, 170)); d.line([(sx - 4, sy - 20), (sx - 9 - ph * 3, sy - 14)], fill=(150, 98, 66), width=2); d.line([(sx + 4, sy - 20), (sx + 9 + ph * 3, sy - 14)], fill=(150, 98, 66), width=2)
    for s_ in (-1, 1): d.line([(sx + s_ * 2, sy - 10), (sx + s_ * (3 + 3 * ph * s_), sy - 2)], fill=(60, 80, 160), width=2); d.ellipse((sx + s_ * 3 - 2, sy - 2, sx + s_ * 3 + 2, sy + 2), fill=(240, 240, 250))
    _person(d, 66, 244, (30, 12, 46), t, 0); _person(d, 78, 244, (30, 12, 46), t, 1.5)                  # dancing couple
    d.rectangle((196, 232, 220, 236), fill=(60, 40, 60)); d.line([(208, 236), (208, 246)], fill=(60, 40, 60), width=2)                   # cocktail table
    d.polygon([(204, 222), (214, 222), (209, 230)], fill=(255, 120, 190)); d.line([(209, 230), (209, 234)], fill=WHITE); d.line([(212, 222), (216, 215)], fill=(120, 255, 160)); d.ellipse((214, 213, 219, 217), fill=(255, 90, 90))
def extra_press(im, t, ts):
    d = ImageDraw.Draw(im)
    d.rectangle((20, 142, 52, 178), fill=(250, 232, 90), outline=(60, 40, 20))                           # band poster with three cartoon faces
    for k in range(3): d.ellipse((24 + k * 9, 146, 31 + k * 9, 153), fill=(255, 190, 150)); d.point((26 + k * 9, 149), fill=(20, 10, 10)); d.point((29 + k * 9, 149), fill=(20, 10, 10))
    d.rectangle((24, 160, 48, 164), fill=(30, 20, 40)); d.rectangle((24, 168, 40, 170), fill=(220, 40, 60))
    _cat(d, 40, 223, t, col=(40, 36, 52), eye=(120, 255, 160))                                           # cat on the magazine pile
    p = (t % 3.0)
    if p > 2.0: d.line([(48, 224), (58 + (p - 2) * 12, 230 + (p - 2) * 14)], fill=(40, 36, 52), width=2)         # paw pushing a pen off the desk
    d.rectangle((60, 252, 78, 254), fill=(240, 200, 60) if p < 2.6 else (240, 200, 60))
    d.rectangle((166, 252, 178, 264), fill=(240, 240, 235), outline=(90, 80, 80)); d.rectangle((178, 255, 181, 259), outline=(240, 240, 235))   # coffee mug
    for k in range(3): d.point((170 + k * 3 + 2 * math.sin(t * 3 + k), 248 - ((t * 10 + k * 5) % 14)), fill=(230, 230, 240))
    d.ellipse((230, 108, 246, 124), fill=WHITE, outline=(40, 40, 50)); a = t * .5; d.line([(238, 116), (238 + 5 * math.cos(a), 116 + 5 * math.sin(a))], fill=(20, 10, 10)); d.line([(238, 116), (238 + 4 * math.cos(a * 12), 116 + 4 * math.sin(a * 12))], fill=(220, 40, 60))   # wall clock
    fx = 70 + 18 * math.sin(t * 3.1); fy = 190 + 10 * math.sin(t * 4.7); d.point((fx, fy), fill=(20, 10, 10)); d.point((fx + 1, fy - 1), fill=(200, 220, 255))
def extra_rave(im, t, ts):
    d = ImageDraw.Draw(im); gx, gy = 58, 238                                                              # glow-stick dancer
    for s_ in (-1, 1):
        for k in range(6):
            a = t * 7 + s_ * 1.2 - k * .35; hx = gx + s_ * 8 + math.cos(a) * 12; hy = gy - 20 + math.sin(a * 1.3) * 10
            d.point((hx, hy), fill=[(100, 255, 160), (255, 100, 200)][(s_ > 0) * 1] if k < 5 else (255, 255, 255))
    d.ellipse((gx - 3, gy - 30, gx + 3, gy - 24), fill=(14, 10, 24)); d.rectangle((gx - 4, gy - 24, gx + 4, gy - 8), fill=(14, 10, 24)); d.line([(gx - 3, gy - 8), (gx - 5 + 3 * math.sin(t * 8), gy)], fill=(14, 10, 24), width=2); d.line([(gx + 3, gy - 8), (gx + 5 - 3 * math.sin(t * 8), gy)], fill=(14, 10, 24), width=2)
    px = 24; d.polygon([(px - 5, 240), (px + 5, 240), (px, 226)], fill=(255, 130, 40)); d.rectangle((px - 6, 240, px + 6, 242), fill=WHITE)          # guy with a traffic cone on his head
    d.ellipse((px - 4, 241, px + 4, 249), fill=(14, 10, 24)); d.rectangle((px - 5, 249, px + 5, 262), fill=(14, 10, 24))
    d.line([(170, 200), (170, 242)], fill=(190, 190, 210), width=2)                                       # acid-house smiley flag, waving
    for i in range(14):
        wv = int(2 * math.sin(t * 6 + i * .5)); d.line([(171 + i, 202 + wv), (171 + i, 216 + wv)], fill=(255, 224, 40))
    d.point((176, 207), fill=(20, 10, 10)); d.point((177, 208), fill=(20, 10, 10)); d.point((178, 207), fill=(20, 10, 10)); d.point((181, 207), fill=(20, 10, 10)); d.point((182, 208), fill=(20, 10, 10)); d.point((183, 207), fill=(20, 10, 10))
    d.arc((174, 206, 184, 214), 20, 160, fill=(20, 10, 10)); b = int(2 * abs(math.sin(t * 6)))
    d.ellipse((212, 206 - b, 220, 214 - b), fill=(14, 10, 24)); d.line([(210, 212 - b), (206, 204 - b)], fill=(14, 10, 24), width=2); d.line([(222, 212 - b), (226, 204 - b)], fill=(14, 10, 24), width=2)    # DJ with headphones
    d.arc((210, 204 - b, 222, 214 - b), 180, 360, fill=(255, 100, 200), width=2)
def extra_pyramid(im, t, ts):
    d = ImageDraw.Draw(im); cx, cy, r = 30, 172, 28                                                       # festival Ferris wheel
    d.line([(cx, cy), (cx - 14, 262)], fill=(60, 56, 90), width=2); d.line([(cx, cy), (cx + 14, 262)], fill=(60, 56, 90), width=2); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(110, 100, 160))
    for k in range(10):
        a = t * .5 + k * .628; x = cx + math.cos(a) * r; y = cy + math.sin(a) * r; d.line([(cx, cy), (x, y)], fill=(70, 66, 110)); d.rectangle((x - 2, y, x + 2, y + 4), fill=[(255, 90, 170), (90, 235, 255), (255, 224, 80)][k % 3])
    tx = (t * 26) % (W + 40) - 20; d.ellipse((tx - 6, 252, tx + 6, 264), outline=(150, 110, 60))                  # tumbleweed
    for k in range(4): a = t * 5 + k * 1.6; d.line([(tx, 258), (tx + 6 * math.cos(a), 258 + 6 * math.sin(a))], fill=(150, 110, 60))
    x0 = 238; d.rectangle((x0 - 4, 232, x0 + 4, 262), fill=(40, 150, 80)); d.rectangle((x0 - 12, 240, x0 - 6, 244), fill=(40, 150, 80)); d.rectangle((x0 - 12, 234, x0 - 9, 244), fill=(40, 150, 80)); d.rectangle((x0 + 6, 244, x0 + 12, 248), fill=(40, 150, 80)); d.rectangle((x0 + 9, 238, x0 + 12, 248), fill=(40, 150, 80))
    shades(d, x0, 238, 4, (14, 10, 20)); d.rectangle((x0 - 6, 229, x0 + 6, 231), fill=(255, 90, 90)); d.rectangle((x0 - 3, 224, x0 + 3, 229), fill=(255, 90, 90))    # cactus with shades and a party hat
    bx = 222 + 14 * math.sin(t * .3); by = 128 + 8 * math.sin(t * .5); d.ellipse((bx - 8, by - 10, bx + 8, by + 6), fill=(255, 140, 60))
    for k in range(-1, 2): d.arc((bx - 8 + k * 5, by - 10, bx + 8 - k * 5, by + 6), 90, 270, fill=(255, 230, 120))
    d.line([(bx - 4, by + 6), (bx - 2, by + 12)], fill=(120, 90, 60)); d.line([(bx + 4, by + 6), (bx + 2, by + 12)], fill=(120, 90, 60)); d.rectangle((bx - 3, by + 12, bx + 3, by + 16), fill=(150, 100, 60))
    s = (t * .6) % 5
    if s < 1: d.line([(20 + s * 90, 20 + s * 30), (28 + s * 90, 23 + s * 30)], fill=WHITE)
def extra_grammy(im, t, ts):
    d = ImageDraw.Draw(im)
    for k in range(4):                                                                                    # velvet-rope posts
        x = 20 + k * 78; d.rectangle((x - 1, 246, x + 1, 264), fill=(230, 180, 60)); d.ellipse((x - 3, 242, x + 3, 248), fill=(255, 215, 90))
        if k < 3: d.arc((x, 246, x + 78, 270), 20, 160, fill=(190, 30, 60), width=2)
    for k in range(9):                                                                                    # paparazzi with flashes
        x = 8 + k * 30; d.ellipse((x - 3, 252, x + 3, 258), fill=(10, 6, 16)); d.rectangle((x - 4, 258, x + 4, 272), fill=(10, 6, 16)); d.rectangle((x + 2, 253, x + 7, 257), fill=(10, 6, 16))
        if int(t * 5 + k * 2.3) % 13 == 0: d.rectangle((x + 6, 252, x + 9, 258), fill=WHITE); d.line([(x + 2, 254), (x + 14, 254)], fill=WHITE); d.line([(x + 7, 249), (x + 7, 260)], fill=WHITE)
    for k in range(4):                                                                                    # gold balloons
        x = 60 + k * 50 + 5 * math.sin(t + k); y = 250 - ((t * 12 + k * 40) % 220); d.ellipse((x - 4, y - 6, x + 4, y + 4), fill=(255, 215, 80), outline=(190, 140, 30)); d.line([(x, y + 4), (x + 2, y + 14)], fill=(220, 200, 160))
    p = (t % 3.2)
    if p < 1.2:                                                                                           # confetti cannon
        for k in range(18): a = -1.2 + k * .14; d.rectangle((10 + math.cos(a) * 60 * p, 250 + math.sin(a) * 90 * p + 60 * p * p, 12 + math.cos(a) * 60 * p, 252 + math.sin(a) * 90 * p + 60 * p * p), fill=[(255, 215, 80), (255, 90, 170), (90, 235, 255)][k % 3])
def extra_paris(im, t, ts):
    d = ImageDraw.Draw(im); x = (t * 20) % (W + 70) - 35; y = 252                                          # cyclist with a baguette
    for wx in (x - 7, x + 7): d.ellipse((wx - 5, y - 5, wx + 5, y + 5), outline=(20, 14, 26)); a = t * 8; d.line([(wx - 4 * math.cos(a), y - 4 * math.sin(a)), (wx + 4 * math.cos(a), y + 4 * math.sin(a))], fill=(60, 50, 70))
    d.line([(x - 7, y), (x, y - 8), (x + 7, y)], fill=(20, 14, 26)); d.ellipse((x - 3, y - 17, x + 3, y - 11), fill=(20, 14, 26)); d.rectangle((x - 3, y - 11, x + 3, y - 4), fill=(60, 80, 170)); d.rectangle((x - 2, y - 18, x + 2, y - 16), fill=(220, 50, 70))
    d.line([(x + 2, y - 8), (x + 17, y - 14)], fill=(230, 180, 90), width=3)                              # baguette
    px = W + 60 - (t * 26) % (W + 200); py = 24 + 3 * math.sin(t * 1.5)                                  # plane towing a banner
    d.rectangle((px - 8, py - 2, px + 8, py + 2), fill=(240, 240, 250)); d.polygon([(px - 8, py - 2), (px - 12, py - 7), (px - 8, py + 2)], fill=(220, 50, 70)); d.line([(px - 2, py - 5), (px - 2, py + 5)], fill=(160, 160, 190), width=2)
    d.rectangle((px + 10, py - 4, px + 56, py + 6), fill=WHITE, outline=(40, 40, 70)); d.fontmode = "1"; d.text((px + 33, py + 1), "¿QUIÉN?", font=F(7), fill=(220, 50, 70), anchor="mm")
    _cat(d, 22, 154, t)                                                                                   # cat on a mansard roof
    if int(t * 2) % 7: d.rectangle((84, 206, 112, 218), fill=(24, 8, 30), outline=(255, 90, 170)); d.text((98, 212), "CAFÉ", font=F(9), fill=(255, 120, 190), anchor="mm")   # neon sign
    bx = 60 + 14 * math.sin(t * .25); by = 92 + 6 * math.sin(t * .4); d.ellipse((bx - 9, by - 11, bx + 9, by + 7), fill=(240, 240, 250))
    d.pieslice((bx - 9, by - 11, bx + 1, by + 7), 90, 270, fill=(40, 80, 190)); d.pieslice((bx - 1, by - 11, bx + 9, by + 7), 270, 90, fill=(220, 50, 70)); d.rectangle((bx - 3, by + 12, bx + 3, by + 16), fill=(150, 100, 60)); d.line([(bx - 5, by + 7), (bx - 3, by + 12)], fill=(120, 90, 60)); d.line([(bx + 5, by + 7), (bx + 3, by + 12)], fill=(120, 90, 60))

def _wrap(dyn, extra): return lambda im, t, ts, tag: (dyn(im, t, ts, tag), extra(im, t, ts))[0]

# ======================= v7: Tyler, The Creator — "Call Me If You Get Lost" look (traced from the user's references) =======================
def make_tyler2():
    """Tall + slim 'Call Me If You Get Lost' look: baby-blue faux-fur trapper hat with gold pin, leopard collar, turquoise cardigan,
    gem chain, gold studs, brown shorts, long legs, tall white socks, two suitcases (brown leather + cream)."""
    w, h = 100, 140; r = random.Random(4)
    SK = (128, 80, 54); SKS = (98, 60, 42); SKL = (150, 94, 62)
    HAT = (176, 222, 248); HATS = (136, 192, 228); HATL = (224, 244, 255)
    CARD = (122, 206, 228); CARDS = (88, 170, 202); CARDL = (172, 230, 244); CUFF = (150, 218, 234)
    LEO = (238, 216, 178); SPOT = (152, 98, 58); WHITE_ = (248, 248, 250)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x0 in (40, 54):                                                           # long legs, tall white socks, shoes
        d.rectangle((x0, 106, x0 + 7, 124), fill=SK); d.rectangle((x0 + 5, 106, x0 + 7, 124), fill=SKS)
        d.rectangle((x0 - 1, 118, x0 + 8, 133), fill=WHITE_); d.rectangle((x0 + 6, 118, x0 + 8, 133), fill=(214, 216, 224))
        for k in range(4): d.line([(x0 - 1, 120 + k * 3), (x0 + 8, 120 + k * 3)], fill=(224, 226, 234))
        d.rounded_rectangle((x0 - 3, 131, x0 + 11, 138), 2, fill=(98, 60, 40)); d.rectangle((x0 - 3, 137, x0 + 11, 139), fill=(58, 34, 24))
    d.rectangle((37, 92, 63, 108), fill=(74, 46, 34)); d.polygon([(37, 104), (63, 104), (65, 111), (35, 111)], fill=(74, 46, 34)); d.rectangle((54, 92, 63, 108), fill=(56, 34, 26)); d.line([(50, 96), (50, 110)], fill=(52, 32, 24))
    # suitcases: brown leather (left), cream (right)
    d.rectangle((6, 104, 26, 124), fill=(150, 96, 58)); d.rectangle((6, 104, 26, 107), fill=(184, 128, 84)); d.rectangle((6, 120, 26, 124), fill=(108, 64, 40)); d.rectangle((21, 104, 26, 124), fill=(124, 76, 46))
    for (cx_, cy_) in ((6, 104), (23, 104), (6, 121), (23, 121)): d.rectangle((cx_, cy_, cx_ + 3, cy_ + 3), fill=(192, 188, 182))
    d.rectangle((14, 112, 18, 116), fill=(255, 215, 80)); d.line([(10, 104), (13, 99), (20, 99), (23, 104)], fill=(100, 60, 38), width=2)
    d.rectangle((74, 108, 94, 126), fill=(238, 212, 180)); d.rectangle((74, 108, 94, 111), fill=(255, 232, 206)); d.rectangle((74, 122, 94, 126), fill=(214, 172, 130)); d.rectangle((89, 108, 94, 126), fill=(214, 184, 150))
    d.rectangle((82, 112, 87, 116), fill=(196, 192, 186)); d.point((84, 114), fill=(255, 215, 80)); d.line([(78, 108), (81, 103), (88, 103), (91, 108)], fill=(190, 150, 110), width=2)
    # cardigan: slim torso, narrow sleeves
    d.rounded_rectangle((36, 48, 64, 98), 5, fill=CARD); d.rectangle((57, 52, 64, 96), fill=CARDS); d.rectangle((39, 54, 44, 82), fill=CARDL)
    d.rectangle((36, 93, 64, 99), fill=CARDS); d.rectangle((36, 95, 64, 96), fill=(70, 150, 184))
    d.polygon([(36, 50), (27, 57), (22, 97), (31, 99), (36, 64)], fill=CARD); d.polygon([(64, 50), (73, 57), (78, 97), (69, 99), (64, 64)], fill=CARD)
    d.polygon([(73, 57), (78, 97), (73, 98), (70, 62)], fill=CARDS); d.polygon([(22, 96), (31, 98), (31, 92), (22, 90)], fill=CUFF); d.polygon([(78, 96), (69, 98), (69, 92), (78, 90)], fill=CUFF)
    d.rectangle((21, 97, 31, 105), fill=SK); d.rectangle((69, 97, 79, 105), fill=SK); d.rectangle((21, 102, 31, 105), fill=SKS)
    for by in (64, 74, 84): d.ellipse((48, by, 52, by + 4), fill=(132, 140, 148)); d.point((49, by + 1), fill=(200, 208, 216))
    d.line([(50, 58), (50, 98)], fill=CARDS); d.rectangle((39, 80, 46, 88), outline=CARDS)
    d.rectangle((45, 42, 55, 52), fill=SKS); d.polygon([(45, 47), (55, 47), (53, 61), (50, 66), (47, 61)], fill=WHITE_)
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)                    # leopard collar flaps
    md.polygon([(45, 45), (35, 49), (31, 61), (44, 67), (48, 54)], fill=255); md.polygon([(55, 45), (65, 49), (69, 61), (56, 67), (52, 54)], fill=255)
    lay = Image.new("RGBA", (w, h), LEO + (255,)); ld = ImageDraw.Draw(lay)
    for _ in range(38):
        sx_, sy_ = r.randint(28, 72), r.randint(44, 70); ld.ellipse((sx_, sy_, sx_ + r.randint(3, 5), sy_ + r.randint(2, 4)), outline=SPOT); ld.point((sx_ + 1, sy_ + 1), fill=SPOT)
        if r.random() < .5: ld.rectangle((sx_ + 3, sy_ + 3, sx_ + 4, sy_ + 4), fill=(110, 66, 36))
    im.paste(lay, (0, 0), mask)
    d.line([(45, 45), (49, 55)], fill=(196, 160, 118)); d.line([(55, 45), (51, 55)], fill=(196, 160, 118))
    pts = [(38, 50), (41, 57), (45, 62), (50, 64), (55, 62), (59, 57), (62, 50)]
    for a_, b_ in zip(pts, pts[1:]): d.line([a_, b_], fill=(220, 224, 232), width=1)
    for (gx_, gy_, gc) in ((43, 60, (220, 40, 60)), (47, 63, (40, 170, 90)), (51, 65, (50, 90, 220)), (55, 62, (255, 120, 190)), (59, 57, (255, 215, 80))):
        d.ellipse((gx_ - 2, gy_ - 2, gx_ + 2, gy_ + 2), fill=gc, outline=(210, 214, 222)); d.point((gx_ - 1, gy_ - 1), fill=(255, 255, 255))
    d.ellipse((38, 12, 62, 50), fill=SK); d.polygon([(56, 18), (62, 28), (60, 42), (56, 48)], fill=SKS); d.ellipse((39, 34, 46, 44), fill=SKL); d.ellipse((54, 34, 61, 44), fill=SKL)   # slim face
    d.ellipse((35, 26, 39, 40), fill=SK); d.ellipse((61, 26, 65, 40), fill=SKS); d.rectangle((35, 38, 37, 40), fill=(255, 215, 80)); d.rectangle((63, 38, 65, 40), fill=(255, 215, 80))
    for (ex, dx_) in ((41, 3), (54, 2)):
        d.rectangle((ex, 27, ex + 5, 30), fill=(238, 230, 222)); d.rectangle((ex + dx_, 27, ex + dx_ + 1, 30), fill=(36, 22, 18)); d.point((ex + dx_, 27), fill=(255, 255, 255))
    d.line([(40, 25), (46, 23)], fill=(36, 22, 18), width=2); d.line([(54, 23), (60, 25)], fill=(36, 22, 18), width=2)
    d.rectangle((48, 31, 52, 37), fill=SKL); d.rectangle((47, 37, 53, 39), fill=SKS); d.point((47, 38), fill=(60, 30, 24)); d.point((53, 38), fill=(60, 30, 24))
    d.rectangle((45, 41, 55, 43), fill=(112, 52, 52)); d.rectangle((46, 44, 54, 46), fill=(156, 88, 84)); d.line([(46, 43), (54, 43)], fill=(54, 22, 26)); d.rectangle((44, 48, 56, 50), fill=SKS)
    d.ellipse((31, -3, 69, 20), fill=HAT); d.rectangle((34, 9, 66, 15), fill=HAT)                                         # trapper hat
    for k in range(10): d.ellipse((34 + k * 3.4 - 2, 12, 34 + k * 3.4 + 3, 18), fill=HAT)
    for (x0, x1) in ((31, 38), (62, 69)): d.rectangle((x0, 10, x1, 28), fill=HAT); d.ellipse((x0 - 1, 24, x1 + 1, 34), fill=HAT)
    d.rectangle((65, 10, 69, 28), fill=HATS); d.ellipse((64, 24, 70, 34), fill=HATS); d.ellipse((56, -1, 69, 14), fill=HATS)
    d.ellipse((34, -1, 50, 8), fill=HATL); d.rectangle((32, 12, 35, 26), fill=HATL)
    for _ in range(120):
        px_, py_ = r.randint(30, 70), r.randint(-2, 34)
        if 0 <= py_ < h and 0 <= px_ < w and im.getpixel((px_, py_))[:3] in (HAT, HATS): d.point((px_, py_), fill=r.choice([HATL, (150, 204, 236), (200, 234, 252)]))
    d.rectangle((58, 3, 60, 5), fill=(255, 215, 80)); d.point((59, 4), fill=(255, 245, 190))
    return _outline_sil(im)
TYLER_COL, TYLER_SIL = make_tyler2()
TYLER_W, TYLER_H, TYLER_X = 100, 140, 50
GEMS = ((43, 60), (47, 63), (51, 65), (55, 62), (59, 57))
def tyler_draw(im, t, ts):
    if ts < REVEAL:
        im.paste(TYLER_SIL, (135 - TYLER_X, 266 - TYLER_H + (1 if int(t * 2.2) % 2 else 0)), TYLER_SIL); qmark(im, 129, 106 + int(3 * math.sin(t * 4)), 3)
    else:
        e = ts - REVEAL; jump = -int(abs(16 * math.exp(-e * 3.2) * math.cos(e * 15))); bob = 1 if int(t * 2.4) % 2 else 0
        y0 = 266 - TYLER_H + jump + bob; im.paste(TYLER_COL, (135 - TYLER_X, y0), TYLER_COL)
        d = ImageDraw.Draw(im); g = int((t * 5) % 10); ox = 135 - TYLER_X
        if g < 3: d.point((ox + 59, y0 + 4), fill=WHITE); d.point((ox + 58 + g, y0 + 2), fill=(255, 255, 255)); d.point((ox + 60, y0 + 6), fill=(255, 255, 255))
        gx_, gy_ = GEMS[int((t * 4) % 5)]; d.point((ox + gx_ + 2, y0 + gy_ - 2), fill=WHITE); d.point((ox + gx_ + 3, y0 + gy_ - 3), fill=WHITE)

# ---- "lost" scene from the album-cover mood: peach sky, red mountains, lake with a sailboat, ringing payphone ----
def base_travel():
    a = np.zeros((H, W, 3), np.uint8)
    a[:200] = dgrad(W, 200, (248, 214, 178), (196, 196, 190), 10); a[200:236] = dgrad(W, 36, (196, 196, 190), (130, 184, 200), 5)
    a[236:266] = dgrad(W, 30, (132, 184, 200), (86, 138, 168), 5); a[266:] = (216, 168, 126)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for _ in range(8):                                               # painterly clouds with teal shadows
        cx_, cy_ = rnd.randint(10, 260), rnd.randint(20, 150); wd = rnd.randint(36, 70)
        for k in range(6): d.ellipse((cx_ + k * wd // 6 - 10, cy_ - rnd.randint(4, 12), cx_ + k * wd // 6 + 14, cy_ + rnd.randint(6, 14)), fill=(255, 248, 238))
        d.rectangle((cx_ - 6, cy_ + 6, cx_ + wd + 10, cy_ + 12), fill=(150, 190, 204))
    for (base, amp, c, hi) in ((236, 62, (172, 108, 74), (206, 140, 96)), (240, 40, (122, 72, 52), (158, 98, 70))):
        pts = [(0, 244)]; x = 0
        while x < W + 12: pts.append((x, base - amp * rnd.uniform(.35, 1.0))); x += rnd.randint(10, 22)
        pts += [(W, 244)]; d.polygon(pts, fill=c)
        for (p, q) in zip(pts[1:-2], pts[2:-1]): d.line([p, (p[0] + (q[0] - p[0]) // 2, p[1] + 14)], fill=hi)
    d.rectangle((0, 234, W, 240), fill=(60, 74, 64))                  # far shore trees
    for k in range(6): d.line([(0, 246 + k * 5), (W, 246 + k * 5)], fill=(150, 200, 214))
    for y in range(268, H, 9):                                        # sand ripples + pebbles
        d.arc((-30, y, W + 30, y + 14), 200, 340, fill=(200, 152, 112))
    for _ in range(40): x, y = rnd.randint(0, W), rnd.randint(272, 400); d.ellipse((x, y, x + rnd.randint(2, 4), y + rnd.randint(1, 3)), fill=rnd.choice([(190, 146, 110), (236, 200, 168), (160, 118, 90)]))
    for k in range(7): d.ellipse((120 + (k % 2) * 10 + k, 276 + k * 14, 126 + (k % 2) * 10 + k, 282 + k * 14), fill=(190, 142, 104)); d.ellipse((130 - (k % 2) * 10 - k, 282 + k * 14, 136 - (k % 2) * 10 - k, 288 + k * 14), fill=(190, 142, 104))
    for _ in range(9): x, y = rnd.randint(10, 260), rnd.randint(280, 395); d.pieslice((x, y, x + 8, y + 8), 180, 360, fill=(250, 226, 210)); d.line([(x + 4, y + 3), (x + 4, y + 7)], fill=(214, 170, 150))     # shells
    return im
TRAVEL = base_travel()
def dyn_travel(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (cx_, cy_, w_, sp) in ((30, 40, 36, 5), (160, 62, 30, 4)):
        x = (cx_ + t * sp) % (W + 90) - 45; cloud(d, x, cy_, w_, (255, 250, 242), (170, 204, 216))
        if cx_ == 160: shades(d, x + w_ // 2 + 2, cy_ + 2, 5)
    bx = 40 + ((t * 5) % 190); by = 250 + int(1.5 * math.sin(t * 2))                                             # sailboat crossing the lake
    d.polygon([(bx - 12, by), (bx + 12, by), (bx + 8, by + 5), (bx - 8, by + 5)], fill=(130, 80, 50)); d.line([(bx, by), (bx, by - 26)], fill=(110, 70, 46), width=1)
    d.polygon([(bx + 1, by - 25), (bx + 1, by - 2), (bx + 14, by - 2)], fill=(250, 246, 238)); d.polygon([(bx - 1, by - 20), (bx - 1, by - 2), (bx - 11, by - 2)], fill=(238, 232, 222))
    for k in range(5): d.point((bx - 14 - k * 3, by + 6 + (k % 2)), fill=(226, 244, 250))
    for k in range(3):                                                                                           # seagulls
        gx = (k * 90 + t * 12) % (W + 40) - 20; gy = 70 + k * 22 + 5 * math.sin(t * 1.4 + k); f = int(t * 6 + k) % 2
        d.line([(gx - 5, gy + (2 if f else -1)), (gx, gy), (gx + 5, gy + (2 if f else -1))], fill=(60, 50, 60), width=1)
    px = 36 + int(math.sin(t * 40) * (1 if int(t * 1.6) % 2 == 0 else 0)); py = 292                               # payphone booth: it's ringing ("call me if you get lost")
    d.rectangle((px - 14, py - 46, px + 14, py + 22), fill=(200, 44, 52), outline=(110, 20, 28)); d.rectangle((px - 11, py - 42, px + 11, py - 6), fill=(150, 214, 230))
    d.line([(px, py - 42), (px, py - 6)], fill=(200, 44, 52)); d.line([(px - 11, py - 24), (px + 11, py - 24)], fill=(200, 44, 52)); d.rectangle((px - 16, py - 50, px + 16, py - 46), fill=(110, 20, 28))
    d.rectangle((px - 5, py - 18, px + 5, py - 10), fill=(40, 40, 52)); d.ellipse((px - 7, py - 22, px + 7, py - 16), fill=(20, 20, 28))
    if int(t * 1.6) % 2 == 0:
        d.ellipse((px + 14, py - 66, px + 54, py - 46), fill=WHITE, outline=(60, 40, 40)); d.polygon([(px + 18, py - 48), (px + 24, py - 48), (px + 16, py - 42)], fill=WHITE)
        d.fontmode = "1"; d.text((px + 34, py - 56), "¡RING!", font=F(8), fill=(200, 44, 52), anchor="mm")
    sx = 232; d.rectangle((sx - 2, 266, sx + 2, 330), fill=(110, 76, 50)); sw = int(2 * math.sin(t * 1.2))
    for k, (tx, c) in enumerate((("ALLÁ", (240, 190, 90)), ("ACÁ", (240, 130, 110)), ("¿?", (150, 214, 230)))):
        yy = 270 + k * 14; d.polygon([(sx - 22 + sw * (k - 1), yy), (sx + 8, yy), (sx + 14, yy + 5), (sx + 8, yy + 10), (sx - 22 + sw * (k - 1), yy + 10)], fill=c, outline=(80, 50, 30)); d.fontmode = "1"; d.text((sx - 6, yy + 5), tx, font=F(7), fill=(60, 30, 20), anchor="mm")
    cx = (t * 14) % (W + 40) - 20; cy = 372                                                                      # crab scuttling sideways
    d.ellipse((cx - 7, cy - 4, cx + 7, cy + 4), fill=(226, 70, 56), outline=(130, 30, 30)); d.point((cx - 3, cy - 5), fill=WHITE); d.point((cx + 3, cy - 5), fill=WHITE)
    for s_ in (-1, 1):
        d.line([(cx + s_ * 7, cy - 1), (cx + s_ * (11 + int(2 * math.sin(t * 8))), cy - 7)], fill=(226, 70, 56), width=2); d.ellipse((cx + s_ * 11 - 2, cy - 10, cx + s_ * 11 + 2, cy - 6), fill=(226, 70, 56))
        for k in range(3): d.line([(cx + s_ * 4, cy + 3), (cx + s_ * (8 + k * 2), cy + 7 + int(math.sin(t * 12 + k)))], fill=(150, 40, 40))
    arr = np.array(im)
    if ts < REVEAL:
        k = min(1, ts / 2.2)
        for kk, bx_ in enumerate((50, 220)): beam(arr, bx_, 135 + math.sin(t * 3 + kk * 3) * 40, 0, 266, 4, 40, (255, 150, 90), .22 * k)
        arr = (arr * (1 - .26 * k) + np.array([50, 20, 60]) * .26 * k).astype(np.uint8)
    else:
        beam(arr, 135, 135, 0, 266, 10, 90, (255, 240, 190), .3 * min(1, (ts - REVEAL) / .3)); glow(arr, 135, 200, 100, (255, 214, 170), .45)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if ts >= REVEAL:
        e = ts - REVEAL
        for (vx, vy, c) in CONF2:
            px_ = 135 + vx * 1.6 * min(e, 1.6) ** .8; py_ = 190 + vy * 2.2 * min(e, 1.2) + 40 * e * e
            if 0 <= px_ < W and 0 <= py_ < H: d.rectangle((px_, py_, px_ + 2, py_ + 2), fill=c)
        for k in range(16):
            x = (k * 37 + math.sin(t * 2 + k) * 8) % W; y = ((t - T[1]) * 28 + k * 41) % 270; d.rectangle((x, y, x + 2, y + 2), fill=[(176, 222, 248), (255, 215, 80), (255, 255, 255), (220, 40, 60)][k % 4])

# ======================= v8: MEGA DIFÍCIL scenes (Tyler, The Creator) =======================
def _gradient_bg(top, bot, steps=10, split=266, floor=(20, 14, 30)):
    a = np.zeros((H, W, 3), np.uint8); a[:split] = dgrad(W, split, top, bot, steps); a[split:] = floor; return Image.fromarray(a)

# ---- hook: danger zone ----
def base_danger():
    im = _gradient_bg((10, 4, 12), (120, 14, 24), 10, 266, (16, 6, 12)); d = ImageDraw.Draw(im)
    for y in range(268, H, 12): d.line([(0, y), (W, y)], fill=(60, 14, 22))
    for k in range(-9, 10): d.line([(135, 266), (135 + k * 40, H)], fill=(60, 14, 22))
    return im
DANGER = base_danger()
def _skull(d, cx, cy, s, t, glow=True):
    d.ellipse((cx - 9 * s, cy - 10 * s, cx + 9 * s, cy + 8 * s), fill=(238, 232, 220), outline=(120, 110, 100)); d.rectangle((cx - 5 * s, cy + 6 * s, cx + 5 * s, cy + 12 * s), fill=(238, 232, 220), outline=(120, 110, 100))
    for ex in (-4, 4): d.ellipse((cx + ex * s - 3 * s, cy - 4 * s, cx + ex * s + 3 * s, cy + 3 * s), fill=(18, 8, 14)); d.point((cx + ex * s, cy - 1 * s), fill=(255, 60, 60) if glow and int(t * 4) % 2 else (140, 20, 30))
    d.polygon([(cx, cy + 2 * s), (cx - 2 * s, cy + 5 * s), (cx + 2 * s, cy + 5 * s)], fill=(18, 8, 14))
    for k in range(-2, 3): d.line([(cx + k * 2 * s, cy + 8 * s), (cx + k * 2 * s, cy + 12 * s)], fill=(120, 110, 100))
def dyn_danger(im, t, ts, tag):
    arr = np.array(im); pulse = .5 + .5 * math.sin(t * 6)
    for k, bx in enumerate((20, 250)): beam(arr, bx, 135 + 70 * math.sin(t * 2.5 + k * 3), 0, 266, 5, 60, (255, 40, 50), .18 + .2 * pulse)
    glow(arr, 135, 270, 140, (255, 90, 30), .5); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for (y0, sgn) in ((206, 1), (240, -1)):                                  # fluttering caution tape
        for i in range(0, W + 16, 12):
            yy = y0 + sgn * ((i - 135) * .09) + 2 * math.sin(t * 3 + i * .1)
            d.polygon([(i, yy - 7), (i + 8, yy - 7), (i + 12, yy + 7), (i + 4, yy + 7)], fill=(255, 214, 40) if (i // 12) % 2 == 0 else (16, 10, 14))
    d.fontmode = "1"; d.text((135 + int(math.sin(t * 2) * 2), 206), "¡PELIGRO!", font=F(9), fill=(16, 10, 14), anchor="mm")
    _skull(d, 40, 112, 1, t); _skull(d, 230, 112, 1, t)                      # skulls (one wears shades)
    shades(d, 230, 109, 7, (10, 6, 12))
    for x in range(0, W, 7):                                                 # flames along the floor
        hh = 18 + 12 * math.sin(t * 9 + x * .7) ** 2; d.polygon([(x - 4, 266), (x, 266 - hh), (x + 4, 266)], fill=(240, 60, 30)); d.polygon([(x - 2, 266), (x, 266 - hh * .6), (x + 2, 266)], fill=(255, 190, 50))
    for k in range(18): d.point(((k * 41 + t * 6) % W, 262 - ((t * 36 + k * 29) % 190)), fill=(255, 210, 80))

# ---- clue 1: film set (the director who signs as Wolf Haley) ----
def base_set():
    im = _gradient_bg((12, 14, 28), (44, 34, 66), 9); d = ImageDraw.Draw(im)
    d.rectangle((30, 40, 240, 236), fill=(26, 150, 84)); d.rectangle((30, 40, 240, 46), fill=(18, 110, 60))                  # green-screen cloth
    for k in range(10): d.line([(40 + k * 22, 46), (36 + k * 22 + (k % 3) * 3, 236)], fill=(20, 126, 70))
    for x0 in (8, 252):                                                                                                   # light stands
        d.line([(x0, 120), (x0 - 10, 266)], fill=(70, 70, 90), width=2); d.line([(x0, 120), (x0 + 10, 266)], fill=(70, 70, 90), width=2); d.line([(x0, 120), (x0, 266)], fill=(90, 90, 110), width=2)
        d.rectangle((x0 - 10, 96, x0 + 10, 124), fill=(30, 30, 40), outline=(120, 120, 140))
    d.rectangle((0, 266, W, 270), fill=(70, 60, 90))
    for y in range(272, H, 14): d.line([(0, y), (W, y)], fill=(34, 26, 52))
    for (x, y) in ((60, 286), (210, 300), (135, 330)): d.line([(x - 5, y - 5), (x + 5, y + 5)], fill=(255, 224, 80), width=2); d.line([(x - 5, y + 5), (x + 5, y - 5)], fill=(255, 224, 80), width=2)      # floor marks
    d.rectangle((10, 238, 46, 266), fill=(40, 40, 52), outline=(110, 110, 130))                                          # camera on tripod
    d.rectangle((14, 226, 42, 240), fill=(24, 24, 34), outline=(150, 150, 170)); d.ellipse((38, 229, 46, 237), fill=(60, 60, 80))
    d.rectangle((180, 236, 232, 266), fill=(150, 108, 60), outline=(90, 60, 30))                                          # director's chair
    d.rectangle((184, 218, 228, 236), fill=(250, 240, 220)); d.fontmode = "1"; d.text((206, 227), "DIRECTOR", font=F(7), fill=(40, 30, 30), anchor="mm")
    return dim_top(im, 150)
SET = base_set()
def dyn_set(im, t, ts, tag):
    arr = np.array(im)
    for x0 in (8, 252): glow(arr, x0, 108, 70, (255, 230, 170), .5 * (.85 + .15 * math.sin(t * 17 + x0))); beam(arr, x0, 135, 108, 250, 6, 70, (255, 235, 190), .14)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    if int(t * 2.5) % 2: d.ellipse((38, 229, 42, 233), fill=(255, 30, 40))                                                  # REC light
    for k in range(2): a = t * 6 + k * 3; d.ellipse((16 + k * 12 - 4, 220 - 4, 16 + k * 12 + 4, 220 + 4), outline=(200, 200, 220)); d.line([(16 + k * 12, 220), (16 + k * 12 + 3 * math.cos(a), 220 + 3 * math.sin(a))], fill=(200, 200, 220))
    p = (t % 3.0); open_ = 18 if p < 2.4 else int(18 * (1 - (p - 2.4) / .2)) if p < 2.6 else 0                              # clapperboard
    d.rectangle((110, 246, 150, 266), fill=(24, 24, 30), outline=WHITE); d.polygon([(110, 246), (150, 246 - open_ // 3), (150, 241 - open_ // 3), (110, 241)], fill=(240, 240, 240))
    for k in range(6): d.polygon([(112 + k * 7, 246), (117 + k * 7, 246 - open_ // 3 * (k + 1) // 6), (120 + k * 7, 241 - open_ // 3 * (k + 1) // 6), (115 + k * 7, 241)], fill=(24, 24, 30)) if open_ else None
    d.fontmode = "1"; d.text((130, 257), "TOMA 1", font=F(7), fill=WHITE, anchor="mm")
    if 2.6 <= p < 2.9: d.text((130, 236), "¡CLAC!", font=F(8), fill=GOLD, anchor="mm")
    bx = 80 + 90 * math.sin(t * .7); d.line([(bx, 30), (bx + 40, 70)], fill=(120, 120, 140), width=2); d.ellipse((bx + 36, 66, bx + 48, 78), fill=(70, 66, 80))        # swinging boom mic
    _cat(d, 206, 214, t, col=(40, 36, 52))                                                                                 # cat napping on the director's chair
def _tree(d, x, y, t, s=1):
    d.rectangle((x - 2 * s, y, x + 2 * s, y + 8 * s), fill=(90, 56, 30))
    for k, (w, yy) in enumerate(((22, 0), (17, -14), (12, -26))): d.polygon([(x - w * s, y + yy), (x + w * s, y + yy), (x, y + yy - 18 * s)], fill=(24, 120, 60)); d.polygon([(x + 2, y + yy), (x + w * s, y + yy), (x, y + yy - 18 * s)], fill=(16, 92, 46))
    for k in range(18):
        a = k * 2.4; lx = x + math.sin(a) * (4 + (k % 6) * 3) * s; ly = y - 8 * s - (k * 2) * s * 1.1
        if math.sin(t * 4 + k) > -.3: d.point((lx, ly), fill=[(255, 90, 90), (255, 224, 80), (90, 235, 255), (255, 130, 220)][k % 4])
    d.polygon([(x, y - 50 * s), (x + 3 * s, y - 44 * s), (x - 3 * s, y - 44 * s)], fill=(255, 224, 80))
# ---- clue 2: Christmas 2009 bedroom studio ----
def base_bedroom():
    im = _gradient_bg((44, 28, 62), (92, 56, 84), 8); d = ImageDraw.Draw(im)
    d.rectangle((20, 132, 96, 200), fill=(18, 24, 56), outline=(220, 220, 240), width=2); d.line([(58, 132), (58, 200)], fill=(220, 220, 240)); d.line([(20, 166), (96, 166)], fill=(220, 220, 240))     # window
    d.ellipse((70, 142, 84, 156), fill=(255, 248, 220)); d.rectangle((16, 200, 100, 204), fill=(200, 200, 215))
    d.rectangle((0, 266, W, 272), fill=(110, 70, 50)); d.rectangle((20, 220, 118, 266), fill=(90, 58, 40)); d.rectangle((24, 224, 114, 232), fill=(120, 80, 54))        # desk
    d.rectangle((30, 196, 74, 222), fill=(40, 40, 52), outline=(130, 130, 150)); d.rectangle((86, 168, 88, 222), fill=(110, 110, 130)); d.ellipse((82, 160, 92, 172), fill=(60, 60, 76), outline=(160, 160, 180))   # laptop + mic stand
    d.rectangle((150, 266 - 18, 200, 266), fill=(200, 40, 50), outline=(120, 20, 30)); d.line([(175, 248), (175, 266)], fill=(255, 224, 80)); d.line([(150, 257), (200, 257)], fill=(255, 224, 80))     # presents
    d.rectangle((206, 250, 236, 266), fill=(60, 130, 220), outline=(30, 70, 140)); d.line([(221, 250), (221, 266)], fill=(255, 255, 255))
    for k in range(4): x = 130 + k * 10; d.polygon([(x, 150), (x + 8, 150), (x + 4, 166)], fill=[(220, 40, 50), (240, 240, 240)][k % 2])                                     # stockings garland
    d.line([(124, 148), (176, 148)], fill=(180, 160, 120))
    for y in range(274, H, 12): d.line([(0, y), (W, y)], fill=(130, 40, 50))
    return dim_top(im, 120)
BEDROOM = base_bedroom()
def dyn_bedroom(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(26): x = 24 + (k * 37 + t * 8) % 70; y = 136 + (t * 20 + k * 23) % 62; d.rectangle((x, y, x + 1, y + 1), fill=WHITE)         # snow outside
    _tree(d, 218, 236, t, 1.0)
    d.rectangle((36, 200, 68, 216), fill=(20, 24, 40))
    for k in range(14): d.line([(38 + k * 2, 214), (38 + k * 2, 214 - int(3 + 8 * abs(math.sin(t * 6 + k * .8))))], fill=(90, 235, 255))   # laptop waveform
    d.polygon([(80, 158), (94, 158), (87, 150)], fill=(220, 40, 50)); d.ellipse((85, 146, 89, 150), fill=WHITE)                                  # Santa hat on the mic
    _cat(d, 132, 258, t, col=(30, 22, 36)); d.polygon([(128, 246), (138, 246), (133, 238)], fill=(220, 40, 50)); d.point((133, 237), fill=WHITE)    # cat in a Santa hat
    for k in range(8): x = 134 + k * 12 + 2 * math.sin(t * 3 + k); d.ellipse((x - 1, 150 + (k % 2) * 3, x + 2, 153 + (k % 2) * 3), fill=[(255, 90, 90), (90, 235, 255), (255, 224, 80)][k % 3])
# ---- clue 3: the 2012 sketch-comedy TV show ----
def base_tv():
    im = _gradient_bg((60, 20, 92), (130, 40, 110), 9, 266, (60, 30, 70)); d = ImageDraw.Draw(im)
    for x in range(0, W, 16): d.rectangle((x, 0, x + 7, 266), fill=(78, 28, 108))
    d.rectangle((10, 168, 96, 232), fill=(110, 70, 40), outline=(60, 36, 20)); d.rectangle((16, 174, 90, 226), fill=(30, 30, 36)); d.rectangle((0, 232, 100, 266), fill=(90, 58, 34))      # CRT cabinet
    d.rectangle((150, 240, 262, 266), fill=(220, 90, 70), outline=(120, 40, 30)); d.rectangle((150, 226, 262, 244), fill=(240, 120, 90))                                                # couch
    d.rectangle((226, 160, 232, 226), fill=(170, 150, 110)); d.polygon([(214, 160), (244, 160), (238, 138), (220, 138)], fill=(255, 224, 120))                                              # lamp
    for y in range(268, H, 14): d.line([(0, y), (W, y)], fill=(80, 40, 90))
    return dim_top(im, 130)
TVROOM = base_tv()
def dyn_tv(im, t, ts, tag):
    d = ImageDraw.Draw(im); arr = np.array(im); glow(arr, 232, 140, 80, (255, 220, 140), .4); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    f = int(t * 12) % 7
    for k in range(7): d.rectangle((16 + k * 10.5, 174, 16 + (k + 1) * 10.5, 226), fill=[(250, 250, 250), (250, 224, 40), (60, 230, 230), (60, 230, 70), (240, 60, 230), (240, 50, 50), (50, 70, 240)][(k + f) % 7])     # test pattern
    for k in range(18): d.line([(16, 176 + k * 3), (90, 176 + k * 3)], fill=(0, 0, 0)) if (k + int(t * 20)) % 5 == 0 else None
    d.line([(36, 168), (22 + int(3 * math.sin(t * 4)), 140)], fill=(200, 200, 210)); d.line([(70, 168), (86 + int(3 * math.sin(t * 4 + 2)), 138)], fill=(200, 200, 210))     # antenna
    if int(t * 2) % 2: d.ellipse((84, 228, 88, 232), fill=(255, 30, 40))
    hx = 190; by = int(4 * abs(math.sin(t * 6)))                                                                                 # dancing hot dog
    d.ellipse((hx - 22, 206 - by, hx + 22, 222 - by), fill=(236, 170, 80), outline=(150, 90, 30)); d.ellipse((hx - 18, 208 - by, hx + 18, 220 - by), fill=(200, 60, 40))
    for k in range(-3, 4): d.point((hx + k * 5, 214 - by + (k % 2)), fill=(255, 224, 60))
    d.ellipse((hx - 8, 209 - by, hx - 4, 213 - by), fill=WHITE); d.ellipse((hx + 4, 209 - by, hx + 8, 213 - by), fill=WHITE); d.point((hx - 6, 211 - by), fill=(20, 10, 10)); d.point((hx + 6, 211 - by), fill=(20, 10, 10))
    d.line([(hx - 22, 214 - by), (hx - 30, 204 - by - int(5 * math.sin(t * 8)))], fill=(236, 170, 80), width=2); d.line([(hx + 22, 214 - by), (hx + 30, 204 - by + int(5 * math.sin(t * 8)))], fill=(236, 170, 80), width=2)
    for k in range(8): x = 100 + (k * 23 + t * 10) % 60; y = 120 + 30 * math.sin(t * 2 + k) - k * 3; d.ellipse((x, y, x + 3, y + 3), fill=(255, 246, 210))        # popcorn
    d.rectangle((196, 140, 244, 154), fill=(255, 30, 40), outline=WHITE); d.fontmode = "1"; d.text((220, 147), "EN VIVO", font=F(8), fill=WHITE if int(t * 2) % 2 else (255, 200, 200), anchor="mm")
# ---- clue 4: the clothing brand (2011) ----
def base_store():
    im = _gradient_bg((255, 214, 232), (255, 244, 200), 8, 266, (240, 210, 170)); d = ImageDraw.Draw(im)
    for y in range(268, H, 22):
        for x in range(0, W, 44): o = 22 if (y // 22) % 2 else 0; d.rectangle((x + o, y, x + o + 21, y + 10), fill=(250, 236, 200)); d.rectangle((x + o + 22, y + 11, x + o + 43, y + 21), fill=(236, 214, 176))
    for k in range(3):                                                                                                       # sneaker wall
        for j in range(8): x = 6 + j * 33; y = 118 + k * 22; c = [(255, 90, 150), (90, 200, 255), (255, 214, 60), (130, 220, 130), (200, 140, 255), (255, 150, 60)][(j + k * 2) % 6]; d.rectangle((x, y, x + 24, y + 12), fill=c, outline=(80, 50, 70)); d.rectangle((x, y + 9, x + 24, y + 12), fill=WHITE)
    d.rectangle((0, 116, W, 118), fill=(120, 80, 60))
    for (y0, cols) in ((196, [(255, 90, 150), (90, 200, 255), (255, 214, 60), (130, 220, 130)]), (232, [(200, 140, 255), (255, 150, 60), (90, 235, 200), (255, 120, 120)])):      # clothing racks
        d.line([(4, y0), (266, y0)], fill=(120, 120, 140), width=2)
        for k in range(14): x = 10 + k * 18; c = cols[k % 4]; d.polygon([(x, y0), (x + 14, y0), (x + 14, y0 + 8), (x + 10, y0 + 6), (x + 4, y0 + 6), (x, y0 + 8)], fill=c); d.rectangle((x + 1, y0 + 6, x + 13, y0 + 22), fill=c); d.line([(x + 7, y0), (x + 7, y0 - 3)], fill=(120, 120, 140))
    return dim_top(im, 110)
STORE = base_store()
def dyn_store(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    if int(t * 3) % 11: d.rectangle((92, 138, 178, 160), fill=(20, 10, 30), outline=(255, 90, 170), width=2); d.fontmode = "1"; d.text((135, 149), "LOOKBOOK", font=F(10), fill=(255, 120, 190), anchor="mm")
    sx = (t * 40) % (W + 80) - 40; d.rectangle((sx - 12, 262, sx + 12, 265), fill=(240, 80, 120)); d.ellipse((sx - 10, 265, sx - 6, 269), fill=(40, 40, 50)); d.ellipse((sx + 6, 265, sx + 10, 269), fill=(40, 40, 50))   # runaway skateboard
    for k in range(3): d.point((sx - 14 - k * 3, 267 + k % 2), fill=(255, 224, 80))
    px = 232 + int(2 * math.sin(t * 2)); d.polygon([(px - 7, 240), (px + 7, 240), (px + 5, 252), (px - 5, 252)], fill=(255, 224, 80), outline=(160, 120, 20)); d.fontmode = "1"; d.text((px, 246), "$$", font=F(7), fill=(160, 40, 40), anchor="mm")   # price tag
    d.rectangle((12, 238, 38, 266), fill=(190, 120, 220), outline=(110, 60, 140)); cu = int(2 * math.sin(t * 2))                  # fitting room with a peeking pair of feet
    d.rectangle((10 + cu, 236, 20 + cu, 266), fill=(255, 150, 200)); d.rectangle((28, 260, 32, 266), fill=(250, 200, 160)); d.rectangle((33, 260, 37, 266), fill=(250, 200, 160))
    bx, by = 252, 214; d.ellipse((bx - 9, by - 16, bx + 9, by + 2), fill=(240, 230, 200)); d.rectangle((bx - 11, by - 8, bx + 11, by - 5), fill=(255, 90, 150)); d.rectangle((bx - 6, by + 2, bx + 6, by + 26), fill=(240, 230, 200)); d.line([(bx, by + 26), (bx, 266)], fill=(120, 120, 140), width=2)   # mannequin with a bucket hat
# ---- clue 5: awards stage, giant moon + astronaut trophy (2011) ----
def base_awards():
    im = _gradient_bg((6, 6, 30), (60, 26, 96), 10); d = ImageDraw.Draw(im)
    d.ellipse((70, 70, 200, 200), fill=(220, 224, 240)); d.ellipse((74, 74, 204, 204), fill=(236, 238, 248))
    for (cx_, cy_, r_) in ((110, 110, 10), (160, 140, 14), (130, 170, 8), (176, 98, 6), (96, 150, 6)): d.ellipse((cx_ - r_, cy_ - r_, cx_ + r_, cy_ + r_), fill=(200, 204, 222), outline=(176, 180, 204))
    d.rectangle((0, 266, W, 270), fill=(200, 150, 255))
    for y in range(272, H, 14): d.line([(0, y), (W, y)], fill=(70, 36, 110))
    for x in (30, 240):                                                                                                      # astronaut trophies on pedestals
        d.rectangle((x - 14, 228, x + 14, 266), fill=(40, 34, 60), outline=(150, 130, 190)); d.ellipse((x - 8, 196, x + 8, 212), fill=(255, 215, 80), outline=(170, 120, 20)); d.rectangle((x - 7, 210, x + 7, 228), fill=(255, 215, 80), outline=(170, 120, 20))
        d.line([(x + 7, 214), (x + 20, 196)], fill=(255, 215, 80), width=2); d.polygon([(x + 20, 188), (x + 34, 192), (x + 20, 198)], fill=(220, 50, 70)); d.line([(x + 20, 186), (x + 20, 214)], fill=(200, 200, 210))
        d.rectangle((x - 5, 200, x + 5, 206), fill=(80, 130, 200))
    return dim_top(im, 120)
AWARDS = base_awards()
def dyn_awards(im, t, ts, tag):
    arr = np.array(im)
    for k, bx in enumerate((50, 135, 220)): beam(arr, bx, 135 + 60 * math.sin(t * 1.3 + k * 2), 0, 266, 6, 80, (200, 150, 255), .2)
    glow(arr, 135, 135, 90, (210, 200, 255), .3); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for (cx_, cy_) in ((120, 130),):                                                                                          # the moon winks
        d.rectangle((cx_ - 12, cy_ - 2, cx_ - 4, cy_ + 1), fill=(60, 50, 90)); d.arc((cx_ + 8, cy_ - 4, cx_ + 18, cy_ + 4), 200, 340, fill=(60, 50, 90), width=2) if int(t * 1.4) % 3 == 0 else d.rectangle((cx_ + 8, cy_ - 2, cx_ + 16, cy_ + 1), fill=(60, 50, 90))
        d.arc((cx_ - 10, cy_ + 10, cx_ + 16, cy_ + 24), 20, 160, fill=(60, 50, 90), width=2)
    rx = (t * 22) % (W + 60) - 30; ry = 40 + 10 * math.sin(t * 1.5); d.polygon([(rx, ry - 6), (rx + 14, ry), (rx, ry + 6)], fill=(236, 236, 246), outline=(120, 120, 150)); d.polygon([(rx - 6, ry - 3), (rx, ry - 3), (rx, ry + 3), (rx - 6, ry + 3)], fill=(255, 130, 40)); d.point((rx - 8, ry), fill=(255, 220, 80))    # tiny rocket
    for k in range(34):
        x = (k * 37 + math.sin(t + k) * 5) % W; y = (t * 30 + k * 47) % 270; d.rectangle((x, y, x + 1, y + 2), fill=[(255, 215, 80), (255, 90, 170), (90, 235, 255), (200, 150, 255)][k % 4])
    for k in range(6):
        if int(t * 6 + k * 3.1) % 12 == 0: x = 14 + k * 44; y = 236 + (k * 13) % 20; d.rectangle((x - 1, y - 1, x + 2, y + 2), fill=WHITE); d.line([(x - 4, y), (x + 5, y)], fill=WHITE); d.line([(x, y - 4), (x, y + 5)], fill=WHITE)
    for k in range(10): x = 6 + k * 27; b = int(2 * abs(math.sin(t * 5 + k))); d.ellipse((x - 3, 254 - b, x + 3, 260 - b), fill=(8, 4, 20)); d.rectangle((x - 4, 260 - b, x + 4, 272), fill=(8, 4, 20))

# ---- recap prop: golden microphone reveal (no character) ----
def mic_draw(im, t, ts, x=135, feet=266):
    pre = ts < REVEAL; e = max(ts - REVEAL, 0); jump = -int(abs(14 * math.exp(-e * 3.2) * math.cos(e * 15))) if not pre else 0
    col = (14, 8, 34) if pre else (255, 214, 70); hi = (14, 8, 34) if pre else (255, 246, 190); sh = (14, 8, 34) if pre else (170, 120, 20)
    d = ImageDraw.Draw(im); y0 = feet - 118 + jump
    d.rectangle((x - 18, feet - 6, x + 18, feet), fill=sh); d.rectangle((x - 3, y0 + 62, x + 3, feet - 6), fill=col); d.rectangle((x - 3, y0 + 62, x - 1, feet - 6), fill=hi)           # stand
    d.rectangle((x - 9, y0 + 40, x + 9, y0 + 62), fill=sh); d.rectangle((x - 7, y0 + 42, x + 7, y0 + 60), fill=col)
    d.ellipse((x - 20, y0, x + 20, y0 + 44), fill=col, outline=sh)
    if not pre:
        for k in range(-3, 4): d.line([(x + k * 5, y0 + 4), (x + k * 5, y0 + 40)], fill=sh); d.line([(x - 18, y0 + 22 + k * 5), (x + 18, y0 + 22 + k * 5)], fill=sh)
        d.ellipse((x - 14, y0 + 4, x - 4, y0 + 14), fill=hi)
        a = int(t * 6) % 6
        if a < 2: d.point((x - 12 + a * 2, y0 + 8), fill=WHITE)
        crown(im, x - 10, y0 - 16 + int(2 * math.sin(t * 3)))
    else: qmark(im, x - 6, y0 - 22 + int(3 * math.sin(t * 4)), 3)

# ======================= v9: Nas as a character (traced from the user's reference photo) =======================
def make_nas2():
    """Grey baseball cap (brim to the side), grey varsity jacket with a navy sleeve, red/white ribbed collar, red script swoosh
    (no team logo/text), long chain with a diamond cross, thin moustache + chin hair, baggy dark jeans, white sneakers; bat behind him."""
    w, h = 100, 140; r = random.Random(9)
    SK = (112, 70, 48); SKS = (86, 52, 36); SKL = (134, 86, 60)
    CAP = (198, 202, 212); CAPS = (150, 156, 170); CAPD = (116, 122, 138)
    JK = (184, 190, 202); JKS = (146, 152, 168); JKL = (212, 216, 226); NAVY = (34, 40, 72); NAVYL = (60, 68, 108); RED = (196, 38, 50)
    SIL = (226, 230, 240); WHITE_ = (248, 248, 250)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(66, 0), (71, 0), (74, 70), (68, 70)], fill=(220, 182, 112)); d.line([(67, 2), (70, 66)], fill=(240, 206, 140)); d.line([(70, 2), (73, 66)], fill=(186, 146, 84))   # bat behind him
    for x0 in (36, 51):                                                                 # baggy dark jeans + white sneakers
        d.rectangle((x0, 94, x0 + 13, 132), fill=(50, 64, 108)); d.rectangle((x0 + 9, 94, x0 + 13, 132), fill=(38, 48, 86)); d.line([(x0 + 4, 104), (x0 + 6, 128)], fill=(70, 86, 132))
        d.rectangle((x0, 124, x0 + 13, 132), fill=(44, 56, 98))
        d.rounded_rectangle((x0 - 3, 130, x0 + 15, 139), 3, fill=WHITE_); d.rectangle((x0 - 3, 137, x0 + 15, 139), fill=(190, 194, 206)); d.line([(x0 + 1, 134), (x0 + 11, 132)], fill=NAVY)
    d.rounded_rectangle((33, 46, 67, 98), 5, fill=JK); d.rectangle((59, 50, 67, 94), fill=JKS); d.rectangle((36, 52, 41, 80), fill=JKL)          # varsity jacket
    for k in range(4): d.rectangle((33, 90 + k * 2, 67, 90 + k * 2), fill=RED if k % 2 == 0 else WHITE_)                                        # ribbed hem
    d.polygon([(33, 48), (26, 56), (22, 96), (31, 98), (35, 62)], fill=NAVY); d.polygon([(26, 56), (22, 96), (25, 96), (29, 60)], fill=NAVYL)     # navy sleeve (down)
    for k in range(3): d.rectangle((21, 92 + k * 2, 31, 92 + k * 2), fill=RED if k % 2 == 0 else WHITE_)
    d.rectangle((21, 98, 31, 106), fill=SK); d.rectangle((21, 103, 31, 106), fill=SKS)
    d.polygon([(67, 48), (76, 54), (82, 66), (76, 70), (70, 62), (66, 62)], fill=JK); d.polygon([(76, 54), (82, 66), (79, 68), (74, 58)], fill=JKS)   # raised arm: upper arm out
    d.polygon([(76, 70), (82, 66), (86, 50), (80, 48)], fill=JK); d.polygon([(82, 66), (86, 50), (84, 49), (80, 64)], fill=JKS)                      # forearm up
    for k in range(3): d.line([(79, 50 + k * 2), (86, 52 + k * 2)], fill=RED if k % 2 == 0 else WHITE_)
    d.polygon([(78, 48), (88, 48), (90, 42), (86, 40), (82, 44), (78, 42)], fill=SK); d.point((88, 41), fill=SKL); d.line([(80, 44), (82, 46)], fill=SKS)   # open hand, palm up
    d.polygon([(32, 74), (44, 66), (56, 64), (68, 60), (68, 68), (56, 70), (44, 74), (34, 82)], fill=RED); d.line([(32, 74), (44, 66), (56, 64), (68, 60)], fill=NAVY)   # script swoosh
    d.line([(34, 82), (44, 74), (56, 70), (68, 68)], fill=NAVY); d.arc((36, 66, 46, 80), 90, 270, fill=NAVY); d.arc((48, 64, 56, 74), 90, 270, fill=WHITE_)
    d.polygon([(43, 44), (57, 44), (55, 58), (50, 62), (45, 58)], fill=WHITE_)                                                                    # white tee
    for k, (c1) in enumerate((RED, WHITE_, RED)): d.line([(41 + k, 44 + k), (50, 56 + k)], fill=c1, width=1); d.line([(59 - k, 44 + k), (50, 56 + k)], fill=c1, width=1)   # ribbed collar
    d.rectangle((44, 40, 56, 48), fill=SKS)
    pts = [(42, 48), (44, 58), (47, 68), (50, 74), (53, 68), (56, 58), (58, 48)]                                                                  # long silver chain + diamond cross
    for a_, b_ in zip(pts, pts[1:]): d.line([a_, b_], fill=SIL, width=1)
    for (px_, py_) in pts[1:-1]: d.point((px_, py_), fill=WHITE_)
    d.rectangle((48, 74, 52, 92), fill=SIL); d.rectangle((44, 78, 56, 82), fill=SIL)
    for (px_, py_) in ((49, 76), (51, 80), (49, 84), (51, 88), (46, 79), (54, 81)): d.point((px_, py_), fill=WHITE_)
    d.rectangle((48, 74, 52, 92), outline=(150, 156, 172)); d.rectangle((44, 78, 56, 82), outline=(150, 156, 172))
    d.ellipse((39, 14, 61, 50), fill=SK); d.polygon([(55, 20), (61, 30), (59, 44), (55, 48)], fill=SKS); d.ellipse((40, 34, 46, 44), fill=SKL)     # slim face
    d.ellipse((36, 26, 40, 38), fill=SK); d.ellipse((60, 26, 64, 38), fill=SKS)
    for (ex, dx_) in ((42, 3), (53, 2)):                                                                                                          # narrowed eyes, heavy lids
        d.rectangle((ex, 29, ex + 5, 31), fill=(232, 222, 214)); d.rectangle((ex + dx_, 29, ex + dx_ + 1, 31), fill=(30, 18, 14)); d.line([(ex - 1, 28), (ex + 6, 28)], fill=(40, 22, 18))
    d.line([(41, 26), (47, 25)], fill=(30, 18, 14), width=2); d.line([(53, 25), (59, 26)], fill=(30, 18, 14), width=2)
    d.rectangle((48, 32, 52, 37), fill=SKL); d.rectangle((47, 37, 53, 38), fill=SKS)
    d.line([(45, 39), (55, 39)], fill=(36, 20, 16)); d.rectangle((45, 41, 55, 44), fill=(92, 46, 42)); d.line([(45, 42), (55, 42)], fill=(54, 24, 22))   # thin moustache + full lips
    d.rectangle((48, 46, 52, 49), fill=(44, 26, 20)); d.point((43, 36), fill=(60, 34, 26))                                                        # chin hair + mole
    d.ellipse((37, 3, 63, 24), fill=CAP); d.rectangle((38, 14, 62, 20), fill=CAP); d.ellipse((54, 4, 63, 20), fill=CAPS)                        # cap
    for k in range(3): d.line([(50, 4), (40 + k * 10, 18)], fill=CAPS)
    d.ellipse((48, 2, 52, 5), fill=CAPS)
    d.polygon([(52, 16), (72, 13), (76, 18), (74, 22), (54, 22)], fill=CAP); d.polygon([(54, 20), (74, 20), (74, 22), (54, 22)], fill=CAPD); d.line([(52, 16), (72, 13)], fill=CAPS)   # brim to the side
    d.rectangle((42, 8, 43, 15), fill=NAVY); d.rectangle((46, 8, 47, 15), fill=NAVY); d.line([(43, 9), (46, 14)], fill=NAVY)                        # small navy emblem (generic, not a team logo)
    d.rectangle((38, 19, 62, 21), fill=CAPD)
    return _outline_sil(im)
NAS2_COL, NAS2_SIL = make_nas2()
def nas2_draw(im, t, ts):
    W_, H_, X_ = 100, 140, 50
    if ts < REVEAL:
        im.paste(NAS2_SIL, (135 - X_, 266 - H_ + (1 if int(t * 2.2) % 2 else 0)), NAS2_SIL); qmark(im, 129, 106 + int(3 * math.sin(t * 4)), 3)
        return
    e = ts - REVEAL; jump = -int(abs(16 * math.exp(-e * 3.2) * math.cos(e * 15))); bob = 1 if int(t * 2.2) % 2 else 0
    y0 = 266 - H_ + jump + bob; ox = 135 - X_; im.paste(NAS2_COL, (ox, y0), NAS2_COL); d = ImageDraw.Draw(im)
    p = (t * .9) % 1.0; up = 30 * 4 * p * (1 - p)                                                                     # baseball tossed up and caught
    bx, by = ox + 85, y0 + 34 - up; d.ellipse((bx - 5, by - 5, bx + 5, by + 5), fill=(250, 248, 244), outline=(60, 50, 50))
    d.arc((bx - 9, by - 5, bx - 1, by + 5), 300, 60, fill=(210, 40, 50)); d.arc((bx + 1, by - 5, bx + 9, by + 5), 120, 240, fill=(210, 40, 50))
    k = int((t * 5) % 6)
    if k < 2: d.point((ox + 50 + (k * 2 - 1), y0 + 77), fill=WHITE); d.point((ox + 50, y0 + 75 + k), fill=WHITE)            # cross sparkle

# ======================= v10: ultra-hard Tyler scenes: café job, 12 schools, UK ban airport =======================
def base_cafe():
    im = _gradient_bg((70, 44, 34), (130, 86, 58), 8, 266, (60, 40, 30)); d = ImageDraw.Draw(im)
    d.rectangle((150, 130, 262, 210), fill=(150, 200, 230), outline=(60, 40, 30), width=3); d.line([(206, 130), (206, 210)], fill=(60, 40, 30), width=2)     # street window
    d.rectangle((150, 196, 262, 210), fill=(90, 90, 100))
    d.rectangle((10, 132, 128, 196), fill=(30, 36, 34), outline=(150, 110, 70), width=3); d.fontmode = "1"                                                # chalk menu
    for k, (tx, c) in enumerate((("LATTE ....... 4", WHITE), ("MOCHA ....... 5", (255, 220, 160)), ("FRAPPÉ ...... 6", (190, 230, 255)), ("¿?????? ..... 9", (255, 150, 190)))): d.text((16, 140 + k * 13), tx, font=F(8), fill=c)
    d.rectangle((0, 222, W, 266), fill=(120, 76, 44)); d.rectangle((0, 218, W, 224), fill=(170, 120, 74))                                                 # counter
    d.rectangle((14, 190, 58, 222), fill=(190, 194, 206), outline=(100, 100, 116)); d.rectangle((20, 196, 52, 206), fill=(60, 60, 72)); d.rectangle((30, 206, 34, 214), fill=(80, 80, 90))   # espresso machine
    d.rectangle((196, 196, 258, 222), fill=(220, 236, 244), outline=(120, 130, 140))                                                                     # pastry case
    for k in range(4): d.ellipse((200 + k * 14, 206, 210 + k * 14, 214), fill=[(220, 160, 80), (200, 120, 70), (240, 200, 120), (150, 90, 50)][k])
    for y in range(272, H, 12):
        for x in range(0, W, 24): o = 12 if (y // 12) % 2 else 0; d.rectangle((x + o, y, x + o + 11, y + 11), fill=(70, 46, 34))
    return dim_top(im, 120)
CAFE = base_cafe()
def dyn_cafe(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    vx = (t * 30) % (W + 220) + 40                                                                                    # delivery van passing the window
    if 140 < vx < 300: d.rectangle((vx - 40, 168, vx, 196), fill=(110, 70, 170)); d.rectangle((vx - 12, 172, vx - 2, 182), fill=(180, 220, 240)); d.ellipse((vx - 36, 192, vx - 28, 200), fill=(30, 30, 36)); d.ellipse((vx - 12, 192, vx - 4, 200), fill=(30, 30, 36))
    d.rectangle((150, 130, 262, 133), fill=(60, 40, 30)); d.rectangle((262, 130, W, 210), fill=(110, 70, 50)); d.rectangle((126, 130, 150, 210), fill=(110, 70, 50))
    for k in range(5): d.point((32 + 2 * math.sin(t * 3 + k), 188 - ((t * 12 + k * 6) % 26)), fill=(236, 236, 240))                                 # steam
    if int(t * 2) % 3: d.line([(32, 206), (32, 212)], fill=(90, 50, 30))
    cx = 88; d.rectangle((cx - 9, 202, cx + 9, 222), fill=(250, 248, 240), outline=(120, 110, 100)); d.rectangle((cx - 10, 198, cx + 10, 202), fill=(40, 120, 70))   # cup with a misspelled name
    d.fontmode = "1"; d.text((cx, 212), "TAILER", font=F(6), fill=(30, 30, 30), anchor="mm")
    for k in range(3): d.point((cx - 3 + k * 3, 194 - ((t * 10 + k * 4) % 10)), fill=(236, 236, 240))
    bx = 110; by = 214 - (abs(math.sin(t * 2.2)) * 6 if int(t / 2.9) % 2 else 0); d.rectangle((bx - 8, by - 8, bx + 8, by + 6), fill=(200, 150, 90), outline=(120, 80, 40)); d.text((bx, by - 1), "FRÁGIL", font=F(5), fill=(200, 40, 40), anchor="mm")

def base_school():
    im = _gradient_bg((200, 210, 180), (226, 214, 170), 8, 266, (150, 110, 80)); d = ImageDraw.Draw(im)
    d.rectangle((50, 126, 220, 196), fill=(36, 74, 52), outline=(150, 110, 70), width=4); d.rectangle((50, 196, 220, 200), fill=(150, 110, 70))                      # chalkboard
    for x0 in (4, 228):
        for k in range(2):
            d.rectangle((x0 + k * 19, 130, x0 + k * 19 + 17, 262), fill=(60, 110, 170), outline=(30, 60, 110))
            for s in range(4): d.line([(x0 + k * 19 + 4, 140 + s * 3), (x0 + k * 19 + 13, 140 + s * 3)], fill=(30, 60, 110))
            d.rectangle((x0 + k * 19 + 13, 196, x0 + k * 19 + 15, 204), fill=(200, 200, 210))
    for k in range(3):                                                                                                    # desks
        x = 40 + k * 80; d.rectangle((x, 238, x + 50, 244), fill=(190, 140, 80)); d.rectangle((x + 4, 244, x + 8, 266), fill=(110, 110, 120)); d.rectangle((x + 42, 244, x + 46, 266), fill=(110, 110, 120))
    for y in range(272, H, 16):
        for x in range(0, W, 32): o = 16 if (y // 16) % 2 else 0; d.rectangle((x + o, y, x + o + 15, y + 15), fill=(170, 130, 96))
    return dim_top(im, 120)
SCHOOL = base_school()
def dyn_school(im, t, ts, tag):
    d = ImageDraw.Draw(im); d.fontmode = "1"
    n = min(12, int((t * 2.4) % 16))                                                                                       # tally marks being chalked up to 12
    for k in range(n):
        g, i = divmod(k, 5); x = 64 + g * 34 + i * 5
        if i == 4: d.line([(x - 22, 160), (x - 1, 146)], fill=(240, 240, 230), width=2)
        else: d.line([(x, 144), (x, 164)], fill=(240, 240, 230), width=2)
    d.text((168, 152), "ESCUELA", font=F(8), fill=(240, 240, 230), anchor="mm"); d.text((168, 166), f"#{max(n, 1)}", font=F(12), fill=(255, 230, 120), anchor="mm")
    d.ellipse((120, 104, 140, 124), fill=WHITE, outline=(40, 40, 50)); a = t * 2; d.line([(130, 114), (130 + 7 * math.cos(a), 114 + 7 * math.sin(a))], fill=(220, 40, 50)); d.line([(130, 114), (130 + 5 * math.cos(a / 12), 114 + 5 * math.sin(a / 12))], fill=(20, 20, 20))
    px = 40 + (t * 46) % 200; py = 214 + 14 * math.sin(t * 3)                                                              # paper plane
    d.polygon([(px, py), (px - 12, py - 4), (px - 8, py), (px - 12, py + 4)], fill=WHITE, outline=(150, 150, 170))
    for k in range(6):
        x = 70 + (k * 23 + t * 6) % 120; y = 200 + ((t * 18 + k * 9) % 30); d.point((x, y), fill=(236, 236, 228))       # chalk dust
    bx = (t * 26) % (W + 120) - 60                                                                                        # backpack-carrying kid silhouette switching schools
    d.ellipse((bx - 3, 222, bx + 3, 228), fill=(30, 26, 40)); d.rectangle((bx - 3, 228, bx + 3, 240), fill=(30, 26, 40)); d.rectangle((bx - 8, 228, bx - 3, 238), fill=(230, 60, 80))
    d.line([(bx - 2, 240), (bx - 4 + 3 * math.sin(t * 9), 248)], fill=(30, 26, 40), width=2); d.line([(bx + 2, 240), (bx + 4 - 3 * math.sin(t * 9), 248)], fill=(30, 26, 40), width=2)

def base_airport():
    im = _gradient_bg((150, 190, 230), (230, 236, 244), 9, 266, (186, 190, 204)); d = ImageDraw.Draw(im)
    d.rectangle((0, 126, W, 214), fill=(170, 210, 240))
    for x in range(0, W + 1, 45): d.rectangle((x - 2, 126, x + 2, 214), fill=(80, 90, 110))
    d.rectangle((0, 198, W, 214), fill=(120, 126, 140)); d.rectangle((0, 214, W, 218), fill=(80, 90, 110))
    d.rectangle((12, 222, 120, 236), fill=(30, 30, 40), outline=(120, 120, 140))                                          # departures board
    d.rectangle((150, 236, 262, 262), fill=(90, 94, 110)); [d.line([(150 + k * 14, 236), (150 + k * 14, 262)], fill=(70, 74, 90)) for k in range(9)]
    for y in range(272, H, 20): d.line([(0, y), (W, y)], fill=(200, 204, 218))
    for k in range(-8, 9): d.line([(135, 266), (135 + k * 50, H)], fill=(200, 204, 218))
    return dim_top(im, 120)
AIRPORT = base_airport()
def dyn_airport(im, t, ts, tag):
    d = ImageDraw.Draw(im); d.fontmode = "1"
    p = (t * .22) % 1.0; px = -30 + p * 330; py = 196 - max(0, p - .35) * 120                                               # plane taking off (without him)
    d.polygon([(px - 18, py), (px + 18, py - 2), (px + 22, py + 2), (px - 18, py + 4)], fill=(250, 250, 252), outline=(140, 150, 170)); d.polygon([(px - 2, py), (px + 8, py), (px - 8, py + 10)], fill=(220, 226, 236)); d.polygon([(px - 18, py), (px - 14, py - 10), (px - 10, py)], fill=(220, 50, 70))
    for k, (tx, st) in enumerate((("LONDRES", "CANCELADO"),)):
        flip = int(t * 8) % 14
        d.text((18, 229), tx, font=F(7), fill=(255, 214, 60), anchor="lm"); d.text((116, 229), st if flip > 2 else "########", font=F(7), fill=(255, 70, 70), anchor="rm")
    for k in range(5):                                                                                                    # suitcases on the carousel
        x = 150 + (k * 26 + t * 18) % 112; d.rectangle((x, 238, x + 14, 248), fill=[(220, 60, 80), (60, 130, 220), (240, 200, 60), (90, 180, 110), (150, 100, 200)][k], outline=(40, 40, 50)); d.line([(x + 4, 238), (x + 10, 238)], fill=(40, 40, 50))
    q = (t % 3.0)                                                                                                         # passport + DENEGADO stamp slamming down
    d.rectangle((206, 150, 252, 186), fill=(40, 60, 120), outline=(255, 214, 60)); d.rectangle((210, 154, 248, 182), fill=(244, 236, 214))
    if q > 1.6:
        s = 1 + max(0, (1.8 - q)) * 4; d.rectangle((229 - 17 * s, 162 - 6 * s, 229 + 17 * s, 174 + 6 * s), outline=(220, 30, 40), width=2); d.text((229, 168), "DENEGADO", font=F(6), fill=(220, 30, 40), anchor="mm")
    else: hy = 130 + q * 20; d.rectangle((222, hy, 236, hy + 8), fill=(120, 80, 50)); d.rectangle((226, hy - 10, 232, hy), fill=(90, 60, 40))

# ======================= v11: Queen episode scenes (workshop 1963, Live Aid 1985) =======================
def base_workshop():
    im = _gradient_bg((60, 40, 28), (110, 74, 48), 8, 266, (74, 50, 34)); d = ImageDraw.Draw(im)
    d.rectangle((12, 130, 130, 200), fill=(150, 108, 70), outline=(70, 46, 30), width=2)                                         # pegboard with tools
    for k in range(7): x = 20 + k * 15; d.line([(x, 140), (x, 156 + (k % 3) * 6)], fill=(200, 200, 214), width=2); d.rectangle((x - 2, 136, x + 2, 142), fill=(120, 70, 40))
    d.rectangle((20, 172, 120, 175), fill=(110, 110, 124)); d.polygon([(30, 176), (50, 176), (40, 192)], fill=(190, 190, 204)); d.ellipse((64, 177, 80, 193), outline=(190, 190, 204), width=2)
    d.rectangle((0, 214, W, 266), fill=(120, 80, 48)); d.rectangle((0, 210, W, 216), fill=(170, 122, 78))                    # workbench
    d.rectangle((190, 120, 262, 134), fill=(150, 96, 58), outline=(90, 56, 30)); d.rectangle((194, 134, 258, 210), fill=(60, 44, 40), outline=(90, 56, 30))   # old fireplace mantel
    d.rectangle((200, 150, 252, 210), fill=(24, 18, 18))
    d.polygon([(40, 200), (92, 190), (100, 206), (70, 214), (44, 212)], fill=(190, 40, 40), outline=(100, 20, 20)); d.line([(96, 198), (150, 196)], fill=(150, 96, 58), width=5)   # half-built red guitar
    d.rectangle((10, 196, 30, 214), fill=(90, 90, 104), outline=(50, 50, 60)); d.rectangle((14, 186, 26, 198), fill=(120, 120, 134))                                         # vise
    for y in range(272, H, 14): d.line([(0, y), (W, y)], fill=(90, 62, 40))
    return dim_top(im, 120)
WORKSHOP = base_workshop()
def dyn_workshop(im, t, ts, tag):
    d = ImageDraw.Draw(im); arr = np.array(im); sw = 6 * math.sin(t * 1.4)
    glow(arr, 150 + sw, 70, 80, (255, 210, 130), .5); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    d.line([(150, 0), (150 + sw, 60)], fill=(60, 50, 40)); d.polygon([(142 + sw, 60), (158 + sw, 60), (162 + sw, 70), (138 + sw, 70)], fill=(255, 224, 140))                     # swinging bare-bulb lamp
    for k in range(18): x = 60 + (k * 11 + 3 * math.sin(t + k)) % 90; y = 150 + ((t * 24 + k * 13) % 62); d.point((x, y), fill=(236, 210, 160))                                  # sawdust
    for k in range(4): c = ((t * 3 + k * .25) % 1.0); d.arc((90 + k * 10, 178 - c * 10, 100 + k * 10, 192 - c * 10), 200, 340, fill=(214, 170, 110))                                 # wood curls
    d.rectangle((222, 70, 252, 100), fill=(240, 232, 214), outline=(70, 50, 40)); a = t * .5; d.line([(237, 85), (237 + 8 * math.cos(a), 85 + 8 * math.sin(a))], fill=(30, 20, 20)); d.line([(237, 85), (237 + 6 * math.cos(a * 12), 85 + 6 * math.sin(a * 12))], fill=(200, 40, 40))   # wall clock
    ax = (t * 12) % (W + 40) - 20; d.rectangle((ax, 252, ax + 14, 260), fill=(220, 220, 230)); d.polygon([(ax + 14, 252), (ax + 22, 256), (ax + 14, 260)], fill=(150, 150, 164))       # runaway hand saw
    d.fontmode = "1"; d.text((262, 60), "1963", font=F(7), fill=(255, 224, 140), anchor="rm")
def base_wembley():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = dgrad(W, 266, (30, 30, 90), (230, 110, 120), 11); a[266:] = (30, 70, 40)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for k in range(5): d.rectangle((0, 150 + k * 20, W, 168 + k * 20), fill=(28 + k * 4, 30 + k * 4, 70 + k * 4))                                  # stands
    for (x0, x1) in ((0, 22), (248, 270)): d.rectangle((x0, 60, x1, 266), fill=(50, 50, 80))
    d.polygon([(70, 160), (200, 160), (190, 120), (80, 120)], fill=(40, 36, 70), outline=(200, 200, 230)); d.rectangle((92, 128, 178, 156), fill=(20, 20, 40))   # stage + big screen
    for y in range(268, H, 12): d.line([(0, y), (W, y)], fill=(40, 90, 54))
    return dim_top(im, 120)
WEMBLEY = base_wembley()
def dyn_wembley(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(180):                                                                                      # crowd doing "la ola" + camera flashes
        x = (k * 17) % W; y = 152 + (k * 29) % 108; up = math.sin(t * 3 - x * .05) > .6
        d.rectangle((x, y - (3 if up else 0), x + 1, y + 1), fill=[(255, 220, 160), (255, 120, 140), (160, 200, 255)][k % 3])
    d.fontmode = "1"; d.text((135, 142), "?", font=F(20), fill=(255, 224, 120) if int(t * 2) % 2 else WHITE, anchor="mm")
    hx = (t * 26) % (W + 120) - 60; hy = 54 + 4 * math.sin(t * 2)                                             # helicopter towing a "?" banner
    d.rectangle((hx - 12, hy, hx + 10, hy + 7), fill=(40, 44, 60)); d.line([(hx - 16, hy - 4), (hx + 16, hy - 4)], fill=(200, 200, 220), width=1); d.line([(hx - 12, hy + 2), (hx - 22, hy)], fill=(40, 44, 60), width=2)
    d.rectangle((hx - 52, hy + 4, hx - 26, hy + 14), fill=WHITE, outline=(40, 40, 70)); d.text((hx - 39, hy + 9), "?", font=F(9), fill=(220, 40, 60), anchor="mm")
    arr = np.array(im)
    for k, bx in enumerate((30, 135, 240)): beam(arr, bx, 135 + 80 * math.sin(t * 1.2 + k * 2), 40, 260, 5, 70, (255, 240, 200), .16)
    im.paste(Image.fromarray(arr))

# ======================= v12: GBA-style scenes from the Parte 12 sprite sheets =======================
SPR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte12")
def _png(name, mode="RGBA"):
    p = os.path.join(SPR_DIR, name); return Image.open(p).convert(mode) if os.path.exists(p) else None
def _sil_rgba(im):
    a = np.array(im)[..., 3] > 0; s = np.zeros(a.shape + (4,), np.uint8); s[a] = (14, 8, 34, 255)
    l = a & ~np.roll(a, 1, 1); r = a & ~np.roll(a, -1, 1); t_ = a & ~np.roll(a, 1, 0)
    s[l] = (70, 230, 255, 255); s[r] = (255, 70, 190, 255); s[t_ & ~l & ~r] = (255, 215, 90, 255); return Image.fromarray(s, "RGBA")
G_BG = [_png(f"fondo_{i}.png", "RGB") for i in range(7)]
G_ART = [_png(f"artista_{k}.png") for k in range(6)]; G_QUE = [_png(f"ayer_queen_{k}.png") for k in range(6)]
G_ART_SIL = [_sil_rgba(G_ART[k]) for k in range(1, 5)] if G_ART[1] else []
_D13 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte13")
def _p13(name, mode="RGBA"):
    p = os.path.join(_D13, name); return Image.open(p).convert(mode) if os.path.exists(p) else None
G13_BG = [_p13(f"fondo_{i}.png", "RGB") for i in range(6)]
G13_ART = [_p13(f"artista_{k}.png") for k in range(6)]
G13_SIL = [_sil_rgba(G13_ART[k]) for k in range(1, 5)] if G13_ART[1] else []
if EP.get("gba_dir") == "parte13" and G13_SIL: G_ART_SIL = G13_SIL      # mystery silhouette of this episode
GY = 266 - 139                                            # sprite cell is 100x140, feet on its row 138 (+1 outline)
def gba_sil(im, t):
    f = G_ART_SIL[int(t * 6) % 4]; bob = 1 if int(t * 2.2) % 2 else 0
    im.paste(f, (85, GY + bob), f); qmark(im, 142, 98 + int(3 * math.sin(t * 3)), 3)
def kurt_gba(im, t, ts):                                      # reveal of Parte 12's answer (colour sprite from the Parte 12 sheet)
    bob = 1 if int(t * 2.4) % 2 else 0
    if ts < REVEAL: f = G_ART[0]; im.paste(f, (85, GY + bob), f); qmark(im, 142, 98 + int(3 * math.sin(t * 4)), 3); return
    e = ts - REVEAL; jump = -int(abs(16 * math.exp(-e * 3.2) * math.cos(e * 15))); f = G_ART[1 + int(t * 6) % 4]
    im.paste(f, (85, GY + jump + bob), f)
def freddie_gba(im, t, ts):
    bob = 1 if int(t * 2.4) % 2 else 0
    if ts < REVEAL: im.paste(G_QUE[0], (85, GY + bob), G_QUE[0]); qmark(im, 130, 98 + int(3 * math.sin(t * 4)), 3); return
    e = ts - REVEAL; jump = -int(abs(16 * math.exp(-e * 3.2) * math.cos(e * 15))); f = G_QUE[1 + int(t * 5) % 4]
    im.paste(f, (85, GY + jump + bob), f)
def dyn_g_hook(im, t, ts, tag):
    arr = np.array(im)
    for k, (x, col) in enumerate(((50, (255, 70, 90)), (100, (90, 230, 255)), (170, (255, 210, 90)), (220, (255, 80, 200)))):
        beam(arr, x, x + 40 * math.sin(t * 1.3 + k * 1.7), 48, 266, 5, 46, col, .22)
    glow(arr, 135, 262, 130, (255, 150, 90), .25); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    rs = random.Random(int(t * 12))
    for _ in range(70): d.point((rs.randint(195, 227), rs.randint(153, 167)), fill=rs.choice([(236, 240, 244), (110, 120, 130), (28, 32, 38)]))   # TV static
    for k in range(22): d.point(((k * 41 + t * 9) % W, 56 + (k * 53 + t * 14) % 200), fill=(255, 230, 200))                                       # haze / dust
def dyn_g_outro(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(80): x = (k * 37 + t * 24) % W; y = (t * 160 + k * 53) % 262; d.line([(x, y), (x - 2, y + 6)], fill=(176, 196, 232))               # rain
    if int(t * 1.5) % 2: d.ellipse((197, 85, 203, 91), fill=(255, 60, 60)); d.point((200, 88), fill=(255, 220, 220))                                  # Space Needle beacon
    for k in range(6):
        if int(t * 2 + k * 1.7) % 4 == 0: d.rectangle((8 + (k * 41) % 52, 150 + (k * 29) % 70, 12 + (k * 41) % 52, 156 + (k * 29) % 70), fill=(255, 236, 160))   # flickering windows
    x = (t * 40) % (W + 60) - 30; d.rectangle((x, 256, x + 14, 262), fill=(20, 22, 40)); d.rectangle((x + 12, 257, x + 15, 259), fill=(255, 240, 180)); d.rectangle((x, 257, x + 2, 259), fill=(255, 80, 80))   # passing car
    for px in (30, 160, 100):
        for k in range(3): d.point((px + k * 6 + int(2 * math.sin(t * 3 + k)), 296 + (px // 30)), fill=(255, 224, 150))                                  # puddle glints
def dyn_g_wembley(im, t, ts, tag):
    arr = np.array(im)
    if ts < REVEAL:
        k = min(1, ts / 2.2)
        for kk, bx in enumerate((60, 210)): beam(arr, bx, 135 + math.sin(t * 3 + kk * 3) * 40, 0, 266, 4, 40, (255, 60, 120), .2 * k)
        arr = (arr * (1 - .3 * k) + np.array([30, 10, 60]) * .3 * k).astype(np.uint8)
    else:
        beam(arr, 135, 135, 0, 266, 10, 90, (255, 230, 160), .3 * min(1, (ts - REVEAL) / .3)); glow(arr, 135, 200, 100, (255, 190, 120), .4)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(14):
        if int(t * 6 + k * 3.7) % 9 == 0: x = 10 + (k * 53) % 250; y = 204 + (k * 29) % 50; d.point((x, y), fill=WHITE); d.point((x + 1, y), fill=(255, 240, 200)); d.point((x, y - 1), fill=(255, 240, 200))
    if ts >= REVEAL:
        e = ts - REVEAL
        for (vx, vy, c) in CONF2:
            px = 135 + vx * 1.6 * min(e, 1.6) ** .8; py = 190 + vy * 2.2 * min(e, 1.2) + 40 * e * e
            if 0 <= px < W and 0 <= py < H: d.rectangle((px, py, px + 2, py + 2), fill=c)
def dyn_g_garage(im, t, ts, tag):
    arr = np.array(im); fl = .85 + .15 * math.sin(t * 13) * (1 if int(t * 3) % 7 == 0 else .3)
    glow(arr, 75, 160, 70, (255, 210, 120), .3 * fl); im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for k in range(30): x = 152 + (k * 19) % 106; y = 44 + (t * 90 + k * 23) % 76; d.line([(x, y), (x - 2, y + 4)], fill=(214, 230, 252))
    if int(t * 8) % 5 == 0: d.line([(178, 194), (206, 194)], fill=WHITE)
def dyn_g_studio(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (cx, cy) in ((96, 92), (174, 92)):
        d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(60, 60, 70)); d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(200, 200, 210))
        for k in range(3): a = t * 4 + k * 2.1; d.line([(cx, cy), (cx + 12 * math.cos(a), cy + 12 * math.sin(a))], fill=(150, 150, 162))
        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(60, 60, 70))
    for k in range(18):
        x = 34 + k * 12; on = math.sin(t * 5 + k * 1.3) > -.3
        d.ellipse((x - 2, 206, x + 2, 210), fill=[(255, 90, 90), (90, 220, 120), (255, 210, 80)][(k + int(t * 3)) % 3] if on else (60, 60, 70))
        y = 190 + int(5 * abs(math.sin(t * 2 + k))); d.rectangle((x - 2, y, x + 2, y + 3), fill=(240, 240, 240))
def dyn_g_aberdeen(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(70): x = (k * 37 + t * 20) % W; y = (t * 150 + k * 53) % 262; d.line([(x, y), (x - 2, y + 6)], fill=(206, 224, 244))
    for k in range(6): x = (k * 47 + t * 14) % W; d.line([(x, 226 + (k % 3) * 3), (x + 8, 226 + (k % 3) * 3)], fill=(236, 248, 252))
    if int(t * 2) % 5: d.rectangle((40, 182, 45, 188), fill=(255, 236, 150))
def dyn_g_pool(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(18):
        x = (k * 41 + math.sin(t * 2 + k) * 5) % W; y = 260 - ((t * 34 + k * 37) % 210); r = 1 + k % 3; d.ellipse((x - r, y - r, x + r, y + r), outline=(230, 250, 255))
    for (c, fy, sp, fl) in (((255, 160, 60), 110, 12, 1), ((255, 120, 190), 210, 9, -1), ((120, 230, 200), 232, 7, 1)):
        x = (t * sp * fl + fy * 3) % (W + 30) - 15; d.ellipse((x - 6, fy - 3, x + 6, fy + 3), fill=c, outline=DARK); d.polygon([(x - 6 * fl, fy), (x - 10 * fl, fy - 4), (x - 10 * fl, fy + 4)], fill=c, outline=DARK)
    for k in range(5):
        if int(t * 4 + k * 3) % 8 == 0: x = 20 + (k * 53) % 230; y = 262; d.point((x, y), fill=WHITE); d.point((x + 1, y), fill=(255, 240, 150))

# ---- Parte 13 (The Beatles) scene animation ----
def _birds(d, t, y0, col, n=3, sp=14):
    for k in range(n): x = (k * 90 + t * sp) % (W + 40) - 20; y = y0 + k * 16 + 5 * math.sin(t * 1.5 + k); f = int(t * 6 + k) % 2; d.line([(x - 5, y + (2 if f else -1)), (x, y), (x + 5, y + (2 if f else -1))], fill=col)
def dyn_g13_port(im, t, ts, tag):
    d = ImageDraw.Draw(im); _birds(d, t, 60, (250, 250, 250))
    for k in range(10): y = 190 + k * 5; x = (k * 53 + t * 18) % W; d.line([(x, y), (x + 10, y)], fill=(255, 220, 190))            # sun glitter on the river
    a = t * .3; d.line([(118, 83), (118 + 5 * math.sin(a), 83 - 5 * math.cos(a))], fill=(200, 40, 40))                              # clock hand
    for k in range(5): d.point((61 + 2 * math.sin(t * 3 + k), 184 - ((t * 10 + k * 6) % 30)), fill=(220, 220, 230))               # ferry funnel smoke
def dyn_g13_hamburg(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    if int(t * 3) % 5: d.rectangle((60, 86, 210, 112), outline=(255, 90, 170), width=2)                                              # flickering neon
    else: d.rectangle((60, 86, 210, 112), outline=(90, 30, 60), width=2)
    for k in range(6): x = 120 + k * 6 + 3 * math.sin(t * 2 + k); y = 200 - ((t * 14 + k * 9) % 70); d.point((x, y), fill=(130, 110, 140))   # smoke from the cellar
    for k in range(4): x = 80 + k * 30; h = 3 + 3 * abs(math.sin(t * 7 + k)); d.rectangle((x, 236 - h, x + 2, 236), fill=(255, 214, 80))  # light pulsing out of the door
def dyn_g13_fete(im, t, ts, tag):
    d = ImageDraw.Draw(im); _birds(d, t, 70, (60, 60, 80))
    for k in range(14):                                                                                                               # bunting flutter
        x = 4 + k * 19; y = 20 + 8 * math.sin(math.pi * k / 13) + 2 * math.sin(t * 4 + k); d.polygon([(x, y), (x + 14, y), (x + 7, y + 12)], fill=[(230, 60, 60), (250, 250, 250), (60, 110, 220)][k % 3], outline=DARK)
    n = int(t * 8) % 2; d.line([(32, 150), (46 + n, 200)], fill=(255, 255, 255))                                                   # tea-chest string vibrating
    for k in range(3): x = 236 + 6 * math.sin(t * 2 + k); y = 200 - ((t * 8 + k * 7) % 20); d.point((x, y), fill=(240, 240, 240))    # tea steam
def dyn_g13_audition(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for cx in (200, 236): a = t * 5; d.line([(cx, 64), (cx + 10 * math.cos(a), 64 + 10 * math.sin(a))], fill=(200, 200, 210))      # tape reels spinning
    for k in range(6): x = 22 + (k * 13 + t * 4) % 76; y = 42 + (t * 12 + k * 11) % 66; d.point((x, y), fill=WHITE)                  # snow falling outside
    if int(t * 1.5) % 3 == 0: d.rectangle((194, 170, 224, 186), outline=(255, 60, 60), width=2)                                    # the stamp flashes
def dyn_g13_rooftop(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(5): x = (k * 61 + t * 40) % (W + 20) - 10; y = 120 + k * 14; d.line([(x, y), (x + 14, y)], fill=(235, 238, 245))   # cold wind
    up = 2 * abs(math.sin(t * .8)); d.pieslice((236, 186 - up, 256, 210 - up), 180, 360, fill=(20, 24, 50), outline=DARK)           # police helmet bobbing
    if int(t * 4) % 2: d.ellipse((96, 211, 120, 217), fill=(255, 240, 140), outline=DARK)                                          # cymbal shimmer
def dyn_g13_crossing(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for k in range(30):
        if math.sin(t * 3 + k * 1.9) > .6: d.point(((k * 47) % W, (k * 29) % 150), fill=(255, 255, 255))
    for x in (44, 226):                                                                                                               # belisha beacons blink
        if int(t * 2) % 2: d.ellipse((x - 7, 185, x + 7, 199), fill=(255, 220, 90), outline=DARK)
    s = (t * .5) % 4
    if s < .7: x = 240 - s * 260; y = 20 + s * 90; d.line([(x, y), (x + 14, y - 8)], fill=(255, 250, 210), width=2)

REG = {"brook": (BROOK, dyn_brooklyn), "sunset": (SUNSET, dyn_recap), "block": (BLOCK, dyn_block), "jazz": (JAZZ, dyn_jazz), "qb": (QB, dyn_qb),
       "battle": (BATTLE, dyn_battle), "press": (PRESS, _wrap(dyn_press, extra_press)), "paris": (PARIS, _wrap(dyn_paris, extra_paris)),
       "pyramid": (PYRAMID, _wrap(dyn_pyramid, extra_pyramid)), "grammy": (GRAMMY, _wrap(dyn_grammy, extra_grammy)), "robots": (ROBOTS, dyn_robots),
       "disco": (DISCO, _wrap(dyn_disco, extra_disco)), "rave": (RAVE, _wrap(dyn_rave, extra_rave)), "garden": (GARDEN, dyn_garden), "travel": (TRAVEL, dyn_travel),
       "hook_sunset": (SUNSET, _wrap(dyn_sunset, extra_hook)),
       "g_hook": (G_BG[0], dyn_g_hook), "g13_hook": (G13_BG[0], dyn_g13_port), "g13_hamburg": (G13_BG[1], dyn_g13_hamburg), "g13_fete": (G13_BG[2], dyn_g13_fete), "g13_audition": (G13_BG[3], dyn_g13_audition), "g13_rooftop": (G13_BG[4], dyn_g13_rooftop), "g13_outro": (G13_BG[5], dyn_g13_crossing), "g_outro": (G_BG[6], dyn_g_outro), "g_wembley": (G_BG[1], dyn_g_wembley), "g_garage": (G_BG[2], dyn_g_garage), "g_studio": (G_BG[3], dyn_g_studio), "g_aberdeen": (G_BG[4], dyn_g_aberdeen), "g_pool": (G_BG[5], dyn_g_pool),
       "danger": (DANGER, dyn_danger), "set": (SET, dyn_set), "bedroom": (BEDROOM, dyn_bedroom), "tv": (TVROOM, dyn_tv), "store": (STORE, dyn_store), "awards": (AWARDS, dyn_awards),
       "workshop": (WORKSHOP, dyn_workshop), "wembley": (WEMBLEY, dyn_wembley), "cafe": (CAFE, dyn_cafe), "school": (SCHOOL, dyn_school), "airport": (AIRPORT, dyn_airport)}
_outro = (BROOK, dyn_outro) if EP["outro_scene"] == "brook" else REG[EP["outro_scene"]]
_hook = REG[EP.get("hook_scene", "brook")]
_pb, _pd = REG[PREV["scene"]]
_win = (SUNSET, dyn_win) if PREV["sprite"] == "snoop" else (_pb, lambda im, t, ts, tag: _pd(im, t, REVEAL + 1.5 + ts, tag))
SCENES = [_hook, REG[PREV["scene"]], _win] + [REG[c["scene"]] for c in CLUES] + [_outro]



# ======================= UI / winners / render (v4) =======================
LIGHT_RECAP = PREV["sprite"] == "tyler"; LIGHTBG_TXT = (70, 20, 120)
def pill(d, cx, y0, y1, w, fill, outline=None):
    d.rectangle((cx - w // 2, y0, cx + w // 2, y1), fill=fill, outline=outline)

def ui_low(seg, ts, t):
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
    if seg == S_HOOK:
        if EP["hook"] == "c":                           # MEGA DIFÍCIL hook
            on = ts > .45 or int(ts * 15) % 3 != 2
            if on:
                k = ease(ts / .25); dy = int((1 - k) * -24)
                lt(d, (135, 46 + dy), "MODO", 24, WHITE, shadow=(255, 40, 60)); lt(d, (135, 96 + dy), "MEGA", 64, GOLD, shadow=(220, 20, 40)); lt(d, (135, 150 + dy), "DIFÍCIL", 40, WHITE, shadow=(220, 20, 40))
            if ts > 1.0: pill(d, 135, 300, 322, 222, (14, 8, 34), (255, 40, 60)); lt(d, (135, 311), f"{NCL} PISTAS · 0 FÁCILES", 11, WHITE)
            if ts > 1.4: lt(d, (135, 342), f"ARTISTA MISTERIOSO · PARTE {EP['part']}", 10, (255, 200, 120))
            if ts > 1.2: lt(d, (135, 362), f"¡SOLO {CLUE_LEN:g} SEGUNDOS POR PISTA!", 10, (255, 90, 90))
            return ui
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
            lt(d, (135, 46 + dy), "LA RESPUESTA DE AYER", 15, LIGHTBG_TXT if LIGHT_RECAP else WHITE, shadow=(255, 255, 255) if LIGHT_RECAP else (10, 4, 30)); lt(d, (135, 76 + dy), "FUE...", 34, GOLD, shadow=(120, 50, 0))
            if ts > .5: lt(d, (135, 112), "." * (1 + int(ts * 3) % 3), 28, (255, 120, 170))
        else:
            e = ts - REVEAL; k = ease(e / .25); dy = int((1 - k) * -20); lines = PREV["lines"]
            if len(lines) == 2:
                s0 = min(34, int(252 / (.62 * len(lines[0])))); s1 = min(46, int(252 / (.62 * len(lines[1]))))
                lt(d, (135, 46 + dy), lines[0], s0, LIGHTBG_TXT if LIGHT_RECAP else WHITE, shadow=(255, 255, 255) if LIGHT_RECAP else (255, 70, 190)); lt(d, (135, 90 + dy), lines[1], s1, GOLD, shadow=(120, 50, 0)); py = 120
            else:
                lt(d, (135, 40 + dy), "LA RESPUESTA DE AYER", 11, (255, 200, 120)); lt(d, (135, 82 + dy), lines[0], 56, GOLD, shadow=(120, 50, 0), anchor="mm"); py = 120
            if PREV["sprite"] in ("tyler", "nas2", "freddie_gba", "kurt_gba"): py = 109
            if e > .5: pill(d, 135, py, py + 16, 196, (14, 8, 34), GOLD); lt(d, (135, py + 8), PREV["sub"], 9, (255, 200, 120))
            if ts > RECAP_LEN - 2.6:
                b = int(2 * math.sin(t * 10)); msg = "¡AHORA LOS GANADORES!" if WINNERS else "¡HOY: UN NUEVO ARTISTA!"
                pill(d, 135, 284 + b, 306 + b, 214, GOLD); lt(d, (135, 295 + b), msg, 11, DARK, shadow=(255, 230, 140))
        return ui
    if seg == S_WIN:
        if EP.get("gba"): d.rectangle((0, 10, 270, 72), fill=(14, 8, 34, 150))
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
    c = CLUES[seg - S_C1]; n = c["n"]; seg_len = T[seg + 1] - T[seg]; last = seg == S_C1 + NCL - 1; NB = EP.get("diff_nb", NCL); col_ = diffc(n, NB)
    k = ease(ts / .3); dy = int((1 - k) * -30)
    if EP.get("gba"):                                    # compact header: the bottom name box already shows clue number + difficulty
        lt(d, (135, 22 + dy), f"VALE {c['pts']} PUNTO{'S' if c['pts'] > 1 else ''}", 10, (255, 230, 170))
        if ts > .5:
            f = F(18); w = int(d.textlength(c["chip"], font=f)) + 16; x0 = 135 - w // 2; fl = ts < .6
            d.rectangle((x0 - 2, 32, x0 + w + 2, 58), fill=(255, 205, 60)); d.rectangle((x0, 34, x0 + w, 56), fill=WHITE if fl else (14, 8, 34))
            lt(d, (135, 46), c["chip"], 18, DARK if fl else GOLD, shadow=(60, 30, 0))
    else:
        lt(d, (135, 46 + dy), f"PISTA {n} / {NCL}", 24, GOLD, shadow=(110, 50, 0))
        bw = 26 if NCL >= 5 else 32; step = bw + 4; x0b = 135 - (NCL * step - 4) // 2
        for i in range(NCL):
            fill = diffc(i + 1, NB) if i < n and ts > .45 + i * .11 else (50, 36, 80)
            d.rectangle((x0b + i * step, 66 + dy, x0b + i * step + bw, 70 + dy), fill=fill)
        lt(d, (135, 80 + dy), f"DIFICULTAD: {c['diff']}", 11, col_)
        lt(d, (135, 92 + dy), f"VALE {c['pts']} PUNTO{'S' if c['pts'] > 1 else ''}", 10, (255, 230, 170))
        if ts > .9:
            f = F(18); w = int(d.textlength(c["chip"], font=f)) + 16; x0 = 135 - w // 2; fl = ts < 1.0
            d.rectangle((x0 - 2, 100, x0 + w + 2, 126), fill=(255, 205, 60)); d.rectangle((x0, 102, x0 + w, 124), fill=WHITE if fl else (14, 8, 34))
            lt(d, (135, 114), c["chip"], 18, DARK if fl else GOLD, shadow=(60, 30, 0))
    if ts > .6:
        rem = min(max(1 - max(0, ts - TW0) / (seg_len - TW0 - .2), 0), 1); urgent = rem < .3 and int(t * 6) % 2
        if EP.get("gba"):
            d.rectangle((12, 390, 258, 420), fill=(20, 16, 40), outline=(24, 16, 40)); d.rectangle((14, 392, 256, 418), outline=(255, 214, 80))
            lt(d, (22, 400), f"PISTA {n}/{NCL}", 9, (255, 230, 120), anchor="lm"); lt(d, (250, 400), c["diff"], 8, (255, 255, 255) if urgent else col_, anchor="rm")
            for kk in range(10): d.rectangle((22 + kk * 23, 407, 22 + kk * 23 + 20, 412), fill=(col_ if kk < math.ceil(rem * 10) else (60, 50, 90)), outline=(24, 16, 40))
        else:
            d.rectangle((12, 12, 258, 18), fill=(14, 8, 34)); d.rectangle((14, 14, 14 + int(242 * rem), 16), fill=(255, 255, 255) if urgent else col_)
    if seg in BANNERS and BANNER_T <= ts < BANNER_T + 1.6:
        e = ts - BANNER_T; kk = ease(e / .2); by = 208 + int((1 - kk) * 40) + int(2 * math.sin(t * 12))
        pill(d, 135, by, by + 22, 232, GOLD); lt(d, (135, by + 11), BANNERS[seg], 11, DARK, shadow=(255, 230, 140))
    if last and ts >= seg_len - 3.0:                     # 3-2-1 countdown on the easiest clue
        num = int(math.ceil(seg_len - ts)); fr = (seg_len - ts) % 1.0; sz = 64 + int(14 * (1 - fr))
        lt(d, (135, 192), str(max(num, 1)), sz, WHITE, shadow=(255, 60, 150))
        lt(d, (135, 236), "¡ÚLTIMA OPORTUNIDAD!" if num == 3 else "¡ESCRÍBELO YA!", 11, GOLD)
    return ui

PCOL = {1: (255, 205, 60), 2: (90, 235, 255), 3: (255, 90, 170), 4: (130, 235, 140), 0: (190, 170, 255)}
PTXT = {1: "PISTA 1", 2: "PISTA 2", 3: "PISTA 3", 4: "PISTA 4", 0: "SIN PISTA INDICADA"}
F_ROW = {}
def fnt(sz):
    if sz not in F_ROW: F_ROW[sz] = ImageFont.truetype(SANS, sz)
    return F_ROW[sz]
def draw_winners(img, ts):
    k = ease(ts / .35)
    if k <= 0: return
    dy = int((1 - k) * 70); wb = 800 if PREV["sprite"] == "snoop" else 840; y0, y1 = wb + dy, wb + 740 + dy; d = ImageDraw.Draw(img)
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
        badge = " · ".join(([SPECIAL[r["h"]]] if r["h"] in SPECIAL else []) + ([f"♥{r['lk']}"] if r["lk"] else []) + ([r["pl"]] if r["pl"] in ("TT", "YT") else []))
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
    elif seg == S_WIN: (snoop(im, t) if PREV["sprite"] == "snoop" else prev_draw(im, t, REVEAL + 6.0))
    elif scn == "battle":
        sil(im, 98, 266, t, q=False); im.paste(SPR_HAT_M, (178 - 24, 266 - 96), SPR_HAT_M); qmark(im, 134, 150 + int(3 * math.sin(t * 3)), 2)
    elif scn == "robots":                                    # last clue: the two helmeted silhouettes finally show up
        b1 = 1 if int(t * 4.5) % 2 else 0; im.paste(SPR_ROBOT_A, (98 - 24, 266 - 96 + b1), SPR_ROBOT_A); im.paste(SPR_ROBOT_B, (172 - 24, 266 - 96 + 1 - b1), SPR_ROBOT_B)
    elif EP.get("gba"): gba_sil(im, t)
    else: sil(im, 135, 266, t)
    if seg == S_WIN:
        im2 = Image.new("RGB", (W, H), (20, 10, 38)); im2.paste(im, (0, -(SHIFT if PREV["sprite"] == "snoop" else 58))); im = im2
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

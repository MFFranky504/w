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

def base_home():
    a = np.zeros((H, W, 3), np.uint8)
    for x in range(0, W, 12): a[:266, x:x + 6] = (52, 28, 82); a[:266, x + 6:x + 12] = (44, 22, 70)
    a[190:266] = (62, 34, 52); a[188:190] = (140, 90, 60)
    for y in range(266, H, 10): a[y:y + 9] = (96, 54, 42) if (y // 10) % 2 else (80, 44, 36)
    return Image.fromarray(a)
HOME = base_home()
def halftone(d, x0, y0, x1, y1, col):
    for y in range(y0, y1, 4):
        for x in range(x0 + (2 if (y // 4) % 2 else 0), x1, 4): d.point((x, y), fill=col)
def dyn_home(im, t, ts, tag):
    d = ImageDraw.Draw(im); arr = np.array(im)
    glow(arr, 250, 50, 110, (255, 190, 90), .45); glow(arr, 40, 100, 100, (255, 150, 80), .25)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    d.rectangle((236, 24, 264, 29), fill=(120, 80, 40)); d.polygon([(238, 29), (262, 29), (257, 50), (243, 50)], fill=(255, 210, 120))  # lamp
    panels = [(8, 0.5), (92, 0.8), (176, 1.1)]; cols = [(130, 200, 255), (255, 240, 170), (255, 170, 200)]
    for i, ((x, st), c) in enumerate(zip(panels, cols)):
        k = ease((ts - st) / .25)
        if k <= 0: continue
        h = int(40 * k); y0 = 164 - h
        d.rectangle((x - 2, y0 - 2, x + 78, 166), fill=(20, 12, 30)); d.rectangle((x, y0, x + 76, 164), fill=c)
        if h < 38: continue
        halftone(d, x + 2, 126, x + 75, 163, tuple(int(v * .82) for v in c))
        if i == 0:  # kennel + dog silhouette on roof
            d.rectangle((x + 20, 150, x + 56, 168), fill=(150, 60, 50)); d.polygon([(x + 16, 150), (x + 38, 136), (x + 60, 150)], fill=(200, 80, 60))
            d.ellipse((x + 33, 154, x + 43, 166), fill=(20, 10, 30))
            d.ellipse((x + 22, 128, x + 48, 138), fill=(15, 8, 25)); d.ellipse((x + 44, 124, x + 56, 136), fill=(15, 8, 25)); d.rectangle((x + 52, 130, x + 62, 133), fill=(15, 8, 25)); d.polygon([(x + 46, 124), (x + 50, 124), (x + 48, 132)], fill=(15, 8, 25))
        else:
            d.ellipse((x + 12, 134, x + 64, 158), fill=WHITE, outline=(20, 12, 30)); d.polygon([(x + 28, 156), (x + 24, 164), (x + 36, 157)], fill=WHITE, outline=(20, 12, 30))
            d.rectangle((x + 13, 140, x + 63, 152), fill=WHITE)
            txt = "..." if i == 1 else "HA HA"
            n = len(txt) if i == 2 else (int(t * 3) % 4)
            d.text((x + 38, 146), (txt if i == 2 else "." * n)[: len(txt)] if (i == 2 and int(t * 2) % 2 == 0) or i == 1 else "", font=F(11), fill=(20, 12, 30), anchor="mm")
    d.rectangle((0, 262, W, 266), fill=(120, 70, 50))

def base_studio():
    a = np.zeros((H, W, 3), np.uint8); a[:266] = (38, 20, 48)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for r, y in enumerate(range(0, 266, 8)):
        off = 0 if r % 2 else 9
        for x in range(-9, W, 18):
            c = rnd.choice([(48, 26, 58), (42, 22, 52), (54, 30, 62)]); d.rectangle((x + off, y, x + off + 16, y + 6), fill=c)
    for (x0, x1) in ((6, 42), (228, 264)):
        d.rectangle((x0 - 2, 52, x1 + 2, 132), fill=(20, 10, 30)); d.ellipse((x0 - 2, 36, x1 + 2, 80), fill=(20, 10, 30))
        d.rectangle((x0, 54, x1, 132), fill=(255, 190, 70)); d.ellipse((x0, 38, x1, 78), fill=(255, 190, 70))
        for gx in range(x0 + 12, x1, 12): d.line([(gx, 40), (gx, 132)], fill=(120, 60, 30))
        d.line([(x0, 92), (x1, 92)], fill=(120, 60, 30))
    for y in range(266, H, 12):
        for x in range(0, W, 24): d.rectangle((x + (12 if (y // 12) % 2 else 0), y, x + (12 if (y // 12) % 2 else 0) + 11, y + 11), fill=(26, 14, 38))
    d.rectangle((0, 264, W, 268), fill=(190, 140, 50))
    return im
STUDIO = base_studio()
def dyn_studio(im, t, ts, tag):
    arr = np.array(im)
    for k, bx in enumerate((70, 200)):
        sw = 22 * math.sin(t * .9 + k * 2)
        beam(arr, bx, bx + sw + (k - .5) * 50, 0, 266, 6, 70, (255, 200, 120), .22)
    glow(arr, 135, 215, 80, (255, 160, 60), .35)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    cx, cy, R = 135, 212, 46   # vinyl halo
    d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), fill=(255, 200, 70)); d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(18, 14, 24))
    for r in range(8, R, 5): d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(44, 38, 56))
    a = t * 2.0; d.line([(cx, cy), (cx + math.cos(a) * R, cy + math.sin(a) * R)], fill=(70, 60, 90))
    d.line([(cx, cy), (cx + math.cos(a + 3.14) * R, cy + math.sin(a + 3.14) * R)], fill=(70, 60, 90))
    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(220, 50, 90)); d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(14, 8, 34))
    d.line([(cx + math.cos(a) * 4, cy + math.sin(a) * 4), (cx + math.cos(a) * 12, cy + math.sin(a) * 12)], fill=(255, 220, 90))
    for i in range(2): d.arc((cx - R - 6 - i * 4, cy - R - 6 - i * 4, cx + R + 6 + i * 4, cy + R + 6 + i * 4), 200, 250, fill=(255, 235, 150))
    # speaker stack (left) pulsing to beat
    pul = 1 if (t * 92 / 60) % 1 < .18 else 0
    d.rectangle((12, 190, 52, 266), fill=(24, 14, 30), outline=(90, 60, 100))
    for cy2 in (208, 244): d.ellipse((20 - pul, cy2 - 12 - pul, 44 + pul, cy2 + 12 + pul), fill=(40, 28, 50), outline=(130, 100, 150)); d.ellipse((28, cy2 - 4, 36, cy2 + 4), fill=(90, 70, 110))
    # billboard chart (right): bars climb, #1 crown late
    hs = [14, 24, 36, 50, 66]
    for i, hh in enumerate(hs):
        k = ease((ts - 1.8 - i * .5) / .5); hh = int(hh * k)
        if hh: d.rectangle((196 + i * 12, 266 - hh, 205 + i * 12, 266), fill=(255, 90, 160) if i < 4 else (255, 205, 60))
    if ts > 4.6:
        pop = 1 + int(2 * (ts - 4.6 < .25))
        d.polygon([(244, 190), (248, 182), (252, 188), (256, 180), (260, 190), (260, 195), (244, 195)], fill=GOLD)
        d.text((252, 180 - pop), "1", font=F(24), fill=WHITE, anchor="mm"); d.text((253, 181 - pop), "1", font=F(24), fill=(255, 205, 60), anchor="mm")
        for k in range(6):
            a2 = ts * 6 + k; d.point((252 + math.cos(a2) * 18, 190 + math.sin(a2) * 12), fill=WHITE)

def base_night():
    a = np.zeros((H, W, 3), np.uint8)
    a[:266] = dgrad(W, 266, (6, 8, 30), (78, 24, 72), 9); a[266:] = (16, 8, 26)
    im = Image.fromarray(a); d = ImageDraw.Draw(im); x = -4
    while x < W:
        w = rnd.randint(18, 34); h = rnd.randint(60, 150); d.rectangle((x, 266 - h, x + w, 266), fill=(14, 10, 32), outline=(26, 18, 52))
        x += w + rnd.randint(0, 3)
    return im
NIGHT = base_night()
WINS = [(rnd.randint(2, W - 3), rnd.randint(100, 262), rnd.random() * 9) for _ in range(90)]
def flame(d, x, base, h, t, seed):
    tip = h * (.7 + .3 * math.sin(t * 9 + seed * 2.3)) * (.6 + .4 * math.sin(t * 5.1 + seed))
    d.polygon([(x - 5, base), (x - 1 + math.sin(t * 7 + seed) * 2, base - tip * .7), (x + math.sin(t * 8 + seed) * 3, base - tip), (x + 2, base - tip * .6), (x + 5, base)], fill=(230, 50, 30))
    d.polygon([(x - 3, base), (x, base - tip * .75), (x + 3, base)], fill=(255, 160, 40))
    d.polygon([(x - 1, base), (x, base - tip * .45), (x + 1, base)], fill=(255, 240, 150))
def dyn_night(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (x, y, p) in WINS:
        if math.sin(t * .8 + p) > -.2: d.point((x, y), fill=(255, 200, 100) if p > 4 else (120, 220, 255))
    arr = np.array(im); k = ease((ts - .4) / .8)
    glow(arr, 135, 262, 150, (255, 90, 30), .55 * k)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    d.rectangle((0, 266, W, 270), fill=(70, 30, 50))
    for x in range(2, W, 9): flame(d, x, 268, 46 * k + 6 * k, t, x)
    for x in range(6, W, 17): flame(d, x, 274, 30 * k, t + .4, x * 3)
    for i in range(22):  # sparks
        x = (i * 37 + math.sin(t * 2 + i) * 6) % W; y = 262 - ((t * 40 + i * 53) % 200) * k
        d.point((x, y), fill=(255, 200 - (i % 3) * 50, 60))

def base_stadium():
    a = np.zeros((H, W, 3), np.uint8)
    a[:266] = dgrad(W, 266, (4, 14, 36), (20, 70, 90), 9)
    a[266:] = (22, 94, 52)
    for i, y in enumerate(range(266, H, 14)):
        if i % 2: a[y:y + 14] = (28, 108, 60)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for k in range(4):   # stands
        y = 140 + k * 28; d.rectangle((0, y, W, y + 26), fill=(18 + k * 4, 22 + k * 4, 52 + k * 5))
    for x in (40, 230):
        d.rectangle((x - 2, 90, x + 2, 266), fill=(40, 40, 60)); d.rectangle((x - 18, 62, x + 18, 92), fill=(30, 30, 46))
    d.line([(0, 266), (W, 266)], fill=(240, 240, 240))
    for k in range(-6, 7): d.line([(135 + k * 5, 268), (135 + k * 70, H)], fill=(60, 140, 80))
    return im
STAD = base_stadium()
CROWD = [(rnd.randint(0, W), rnd.randint(150, 260), rnd.random() * 6, rnd.choice([(255, 210, 90), (255, 90, 160), (90, 230, 255), (240, 240, 240)])) for _ in range(260)]
CONF = [(rnd.random() * W, rnd.random() * H, rnd.uniform(25, 60), rnd.choice([(255, 210, 60), (255, 80, 170), (80, 240, 230), (170, 130, 255)]), rnd.random() * 6) for _ in range(70)]
def dyn_stadium(im, t, ts, tag):
    d = ImageDraw.Draw(im)
    for (x, y, p, c) in CROWD:
        if math.sin(t * 6 + p * 3) > -.1: d.point((x, y), fill=c)
    arr = np.array(im)
    for x in (40, 230): glow(arr, x, 76, 70, (255, 250, 220), .8)
    for k, bx in enumerate((60, 210)):
        beam(arr, 135 + (k - .5) * 120, 135 + math.sin(t * 1.1 + k * 2) * 80 + (k - .5) * 20, 70, 266, 6, 60, (200, 230, 255), .14)
    im.paste(Image.fromarray(arr)); d = ImageDraw.Draw(im)
    for x in (40, 230):
        for r in range(3):
            for c in range(4): d.rectangle((x - 15 + c * 8, 64 + r * 8, x - 10 + c * 8, 69 + r * 8), fill=(255, 255, 235))
    for (bt, bx, by) in ((3.0, 80, 100), (5.2, 195, 90)):  # fireworks
        e = ts - bt
        if 0 < e < 1.2:
            for k in range(14):
                a2 = k / 14 * 6.283; r = 36 * ease(e / 1.0); c = [(255, 210, 60), (255, 80, 170), (90, 240, 255)][k % 3]
                d.rectangle((bx + math.cos(a2) * r, by + math.sin(a2) * r + 10 * e * e, bx + math.cos(a2) * r + 2, by + math.sin(a2) * r + 2 + 10 * e * e), fill=c)
    for (x, y, v, c, p) in CONF:   # confetti
        yy = (y + v * t) % H; xx = x + math.sin(t * 2 + p) * 6
        d.rectangle((xx, yy, xx + 1, yy + 2), fill=c)


# ---------------- Biggie (original pixel-art tribute) ----------------
def make_biggie():
    w, h = 64, 110
    SK = (150, 98, 68); SKD = (112, 70, 48); SKL = (184, 126, 92)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x0 in (17, 34):
        d.rectangle((x0, 88, x0 + 13, 105), fill=(46, 58, 120)); d.rectangle((x0, 88, x0 + 2, 105), fill=(32, 42, 92))
    for x0 in (14, 33):
        d.rectangle((x0, 102, x0 + 17, 109), fill=(240, 240, 248)); d.rectangle((x0, 107, x0 + 17, 109), fill=(150, 150, 175))
    # sweater (zig-zag bands) masked to torso+arms
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)
    md.rounded_rectangle((8, 44, 56, 92), 6, fill=255); md.rectangle((0, 48, 10, 86), fill=255); md.rectangle((54, 48, 64, 86), fill=255)
    layer = Image.new("RGBA", (w, h), (255, 205, 60, 255)); ld = ImageDraw.Draw(layer)
    bands = [(255, 80, 160), (80, 230, 255), (150, 110, 255), (255, 205, 60)]
    for i, y in enumerate(range(44, 96, 6)):
        for x in range(0, w):
            yy = y + (2 if (x // 4) % 2 else 0); ld.rectangle((x, yy, x, yy + 2), fill=bands[i % 4])
    im.paste(layer, (0, 0), mask)
    d.rectangle((1, 86, 9, 94), fill=SK); d.rectangle((55, 86, 63, 94), fill=SK); d.rectangle((1, 91, 9, 94), fill=SKD)
    d.rectangle((26, 38, 38, 46), fill=SKD)
    d.line([(24, 46), (32, 64), (40, 46)], fill=(255, 215, 80), width=2); d.ellipse((27, 62, 37, 72), fill=(255, 215, 80), outline=(170, 115, 20)); d.rectangle((31, 66, 33, 68), fill=(170, 115, 20))
    d.ellipse((17, 12, 47, 44), fill=SK); d.rectangle((15, 27, 18, 33), fill=SKD); d.rectangle((46, 27, 49, 33), fill=SKD)
    d.rectangle((23, 20, 29, 21), fill=SKL)
    d.polygon([(19, 33), (45, 33), (43, 43), (21, 43)], fill=(72, 44, 34)); d.rectangle((28, 36, 36, 37), fill=(40, 20, 22))
    d.rectangle((19, 25, 31, 31), fill=(15, 12, 22)); d.rectangle((33, 25, 45, 31), fill=(15, 12, 22)); d.rectangle((31, 27, 33, 28), fill=(15, 12, 22))
    d.point((21, 26), fill=WHITE); d.point((22, 26), fill=WHITE); d.point((35, 26), fill=WHITE); d.point((36, 26), fill=WHITE)
    d.ellipse((20, 2, 44, 20), fill=(78, 54, 140)); d.rectangle((14, 15, 50, 19), fill=(54, 38, 104)); d.rectangle((20, 14, 44, 15), fill=(255, 205, 60))
    d.rectangle((24, 5, 30, 6), fill=(130, 100, 200))
    a = np.array(im)[..., 3] > 0
    ol = np.zeros_like(a)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): ol |= np.roll(np.roll(a, dy, 0), dx, 1)
    ol &= ~a
    arr = np.array(im); arr[ol] = (14, 8, 34, 255)
    col = Image.fromarray(arr, "RGBA")
    full = a | ol
    sil = np.zeros_like(arr); sil[full] = (14, 8, 34, 255)
    left = full & ~np.roll(full, 1, 1); right = full & ~np.roll(full, -1, 1); top = full & ~np.roll(full, 1, 0)
    sil[left] = (70, 230, 255, 255); sil[right] = (255, 70, 190, 255); sil[top & ~left & ~right] = (255, 215, 90, 255)
    return col, Image.fromarray(sil, "RGBA")
BIG_COL, BIG_SIL = make_biggie()
CROWN = ["0010010010", "0110110110", "0111111110", "1111111111", "1311211311", "1111111111"]
def crown(im, x, y):
    d = ImageDraw.Draw(im)
    for j, row in enumerate(CROWN):
        for i, c in enumerate(row):
            if c != "0": d.rectangle((x + i * 2, y + j * 2, x + i * 2 + 1, y + j * 2 + 1), fill={"1": (255, 205, 60), "2": (255, 245, 170), "3": (240, 60, 130)}[c])
def biggie(im, t, ts, x=135, feet=266):
    if ts < REVEAL:
        im.paste(BIG_SIL, (x - 32, feet - 110 + (1 if int(t * 2.2) % 2 else 0)), BIG_SIL)
        qmark(im, x - 6, feet - 138 + int(3 * math.sin(t * 4)), 3)
    else:
        e = ts - REVEAL; jump = -int(abs(14 * math.exp(-e * 3.5) * math.cos(e * 16)))
        dance = 1 if (int(t * 92 / 60 * 2) % 2 and ts > WIN0) else 0
        im.paste(BIG_COL, (x - 32 + dance, feet - 110 + jump + (1 if int(t * 2.2) % 2 else 0)), BIG_COL)
        crown(im, x - 10, feet - 130 + jump + int(2 * math.sin(t * 3)))

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

SCENES = [(SUNSET, dyn_sunset), (BROOK, dyn_brooklyn), (HOME, dyn_home), (STUDIO, dyn_studio), (NIGHT, dyn_night), (STAD, dyn_stadium), (SUNSET, dyn_sunset)]

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

def pill(d, cx, y0, y1, w, fill, outline=None):
    d.rectangle((cx - w // 2, y0, cx + w // 2, y1), fill=fill, outline=outline)

def ui_low(seg, ts, t):
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
    if seg == 0:                                    # ---- hook
        if ts < 1.0:
            on = int(ts * 15) % 3 != 2
            if on:
                lt(d, (135, 70), "¿QUIÉN", 40, WHITE, shadow=(255, 60, 150)); lt(d, (135, 118), "ES?", 44, GOLD, shadow=(70, 230, 255))
            return ui
        k = ease((ts - 1.0) / .3); dy = int((1 - k) * -30)
        lt(d, (135, 46 + dy), "¡SOLO LOS REALES", 17, WHITE); lt(d, (135, 70 + dy), "LO ADIVINAN!", 24, GOLD, shadow=(120, 50, 0))
        if ts > 1.4: pill(d, 135, 300, 322, 222, (14, 8, 34), GOLD); lt(d, (135, 311), "¿LO ADIVINAS EN LA PISTA 1?", 11, WHITE)
        if ts > 1.9: lt(d, (135, 342), "ARTISTA MISTERIOSO · PARTE 8", 10, (255, 200, 120))
        if ts > 2.3: lt(d, (135, 362), "PERO PRIMERO... ¿QUIÉN FUE EL ANTERIOR?", 8, (255, 255, 255))
        return ui
    if seg == 1:                                    # ---- recap: artista anterior + ganadores
        if ts < REVEAL:
            k = ease(ts / .35); dy = int((1 - k) * -30)
            lt(d, (135, 46 + dy), "EL ARTISTA ANTERIOR", 17, WHITE); lt(d, (135, 76 + dy), "FUE...", 34, GOLD, shadow=(120, 50, 0))
            if ts > .5: lt(d, (135, 112), "." * (1 + int(ts * 3) % 3), 28, (255, 120, 170))
        elif ts < WIN0:
            e = ts - REVEAL; k = ease(e / .25); dy = int((1 - k) * -20)
            lt(d, (135, 42 + dy), "THE NOTORIOUS", 17, WHITE); lt(d, (135, 76 + dy), "B.I.G.", 38, GOLD, shadow=(120, 50, 0))
            if e > .5: lt(d, (135, 108), "(BIGGIE)", 14, (255, 120, 170))
        else:
            e = ts - WIN0; k = ease(e / .3); dy = int((1 - k) * -26)
            lt(d, (135, 44 + dy), "¡LO ADIVINARON!", 22, GOLD, shadow=(110, 50, 0))
            lt(d, (135, 70 + dy), "THE NOTORIOUS B.I.G.", 12, WHITE)
            if ts > WIN0 + .5: lt(d, (135, 96), "GRACIAS A LOS QUE ACERTARON", 9, (255, 200, 120))
            if ts > 12.9:
                bounce = int(2 * math.sin(t * 10)); pill(d, 135, 138 + bounce, 160 + bounce, 200, GOLD); lt(d, (135, 149 + bounce), "¿SERÁS EL SIGUIENTE?", 12, DARK, shadow=(255, 230, 140))
        return ui
    if seg == 6:                                    # ---- outro
        sw = ts > 3.2
        a_, b_ = ("¿CUÁNTOS PUNTOS", "SACASTE?") if sw else ("¿YA SABES", "QUIÉN ES?")
        ka = ease(ts / .3) if not sw else ease((ts - 3.2) / .25); dy = int((1 - ka) * -26)
        lt(d, (135, 52 + dy), a_, 23 if not sw else 17, WHITE); lt(d, (135, 88 + dy), b_, 34 if not sw else 30, GOLD, shadow=(120, 50, 0))
        if ts > .6 and not sw: pill(d, 135, 112, 134, 242, GOLD); lt(d, (135, 123), "ESCRÍBELO EN LOS COMENTARIOS", 11, DARK, shadow=(255, 230, 140))
        if ts > 1.2 and not sw:
            o = 2 if int(t * 3) % 2 else 0
            for ox in (-24, 0, 24): d.polygon([(135 + ox - 6, 148 + o), (135 + ox + 6, 148 + o), (135 + ox, 158 + o)], fill=(255, 200, 120))
        if ts > 2.0: pill(d, 135, 274, 292, 130, (14, 8, 34), GOLD); lt(d, (135, 283), "LONG BEACH", 12, GOLD)
        if ts > 3.5:
            pill(d, 135, 306, 328, 246, GOLD); lt(d, (135, 317), "REVELO AL ARTISTA EN EL PRÓXIMO VIDEO", 8, DARK, shadow=(255, 230, 140))
            lt(d, (135, 342), "LOS QUE ACIERTEN SALEN EN LA PARTE 9", 9, WHITE); lt(d, (135, 358), "SÍGUEME PARA NO PERDÉRTELO", 9, (255, 200, 120))
        return ui
    c = CLUES[seg - 2]; n = c["n"]                  # ---- clues (seg 2..5)
    seg_len = T[seg + 1] - T[seg]
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
    if ts > .6:                                     # countdown bar
        rem = 1 - max(0, ts - TW0) / (seg_len - TW0 - .2); rem = min(max(rem, 0), 1)
        urgent = rem < .3 and int(t * 6) % 2
        d.rectangle((12, 12, 258, 18), fill=(14, 8, 34)); d.rectangle((14, 14, 14 + int(242 * rem), 16), fill=(255, 255, 255) if urgent else DIFFC[n - 1])
    if seg in BANNERS and BANNER_T <= ts < BANNER_T + 1.6:
        e = ts - BANNER_T; kk = ease(e / .2); by = 208 + int((1 - kk) * 40) + int(2 * math.sin(t * 12))
        pill(d, 135, by, by + 22, 232, GOLD); lt(d, (135, by + 11), BANNERS[seg], 11, DARK, shadow=(255, 230, 140))
    return ui

def draw_winners(img, ts):
    if ts < WIN0 - .1:
        k = ease((ts - .6) / .3)
        if k <= 0: return
        dy = int((1 - k) * 50); y0 = 272 * S + dy; d = ImageDraw.Draw(img)
        d.rectangle((12 * S - 8, y0 - 8, 258 * S + 8, 378 * S + 8 + dy), fill=(14, 10, 36))
        d.rectangle((12 * S, y0, 258 * S, 378 * S + dy), fill=(24, 42, 150), outline=(140, 175, 255), width=8)
        a_, b_ = (("En la parte 7,", "la respuesta fue" + "." * (1 + int(ts * 3) % 3)) if ts < REVEAL else ("¡La respuesta", "de la parte 7!"))
        d.text((540, y0 + 140), a_, font=BODY, fill=WHITE, anchor="mm"); d.text((540, y0 + 220), b_, font=BODY, fill=GOLD, anchor="mm")
        return
    k = ease((ts - WIN0 + .1) / .3)
    if k <= 0: return
    dy = int((1 - k) * 50); y0 = 272 * S + dy; d = ImageDraw.Draw(img)
    d.rectangle((12 * S - 8, y0 - 8, 258 * S + 8, 378 * S + 8 + dy), fill=(14, 10, 36))
    d.rectangle((12 * S, y0, 258 * S, 378 * S + dy), fill=(24, 42, 150), outline=(255, 205, 60), width=8)
    d.rectangle((12 * S + 8, y0 + 8, 258 * S - 8, y0 + 38), fill=(120, 70, 10))
    d.fontmode = "1"; d.text((135 * S, y0 + 24), "GANADORES · PARTE 7", font=F(26), fill=(255, 235, 170), anchor="mm"); d.fontmode = "L"
    wx0, wy0, wx1, wy1 = 12 * S + 12, y0 + 44, 258 * S - 12, 378 * S + dy - 10
    ww, wh = wx1 - wx0, wy1 - wy0
    win = Image.new("RGB", (ww, wh), (24, 42, 150)); wd = ImageDraw.Draw(win)
    off = min(max(ts - WIN0, 0) * WIN_SPEED, len(WINNERS) * ROW_H)
    f1 = ImageFont.truetype(SANS, 44); f2 = ImageFont.truetype(SANS, 34)
    for i, (h, badge) in enumerate(WINNERS):
        y = wh + i * ROW_H - off
        if y < -ROW_H or y > wh: continue
        top = i == 0
        wd.rounded_rectangle((6, y + 6, ww - 6, y + ROW_H - 10), 14, fill=(255, 205, 60) if top else (40, 66, 190))
        wd.text((46, y + ROW_H // 2 - 2), "★", font=f1, fill=(120, 60, 0) if top else GOLD, anchor="mm")
        wd.text((92, y + ROW_H // 2 - 2), h, font=f1, fill=DARK if top else WHITE, anchor="lm")
        if badge: wd.text((ww - 24, y + ROW_H // 2 - 2), badge, font=f2, fill=(150, 20, 60) if top else (255, 160, 200), anchor="rm")
    img.paste(win, (wx0, wy0))

def draw_panel_text(img, seg, ts):
    c = CLUES[seg - 2]; lines, sp = LAY[seg - 2]
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
    for i in range(1, 7):
        if t >= T[i]: s_ = i
    return s_

def shake_amp(seg, ts):
    if seg == 1:
        if .4 < ts < REVEAL: return 2 + 7 * ((ts - .4) / (REVEAL - .4)) ** 2
        if REVEAL <= ts < REVEAL + .6: return 22 * (1 - (ts - REVEAL) / .6)
    if 2 <= seg <= 5 and 1.0 < ts < 1.3: return 10 * (1 - (ts - 1.0) / .3)
    return 0

def glitch(img, t, strength):
    arr = np.array(img); rng = np.random.default_rng(int(t * 30) + 11)
    arr[..., 0] = np.roll(arr[..., 0], int(18 * strength), 1); arr[..., 2] = np.roll(arr[..., 2], -int(18 * strength), 1)
    for _ in range(7):
        y = int(rng.integers(0, FH - 120)); h = int(rng.integers(20, 120)); arr[y:y + h] = np.roll(arr[y:y + h], int(rng.integers(-140, 140)), 1)
    return Image.fromarray(arr)

def render(t):
    seg = seg_of(t); ts = t - T[seg]
    base, dyn = SCENES[seg]
    im = base.copy(); dyn(im, t, ts, None)
    if seg != 1: notes(im, t)
    if seg == 1: biggie(im, t, ts)
    elif seg == 4:
        sil(im, 100, 266, t, q=False); sil(im, 172, 266, t, hat=True, phase=.35, q=False); qmark(im, 136, 166 + int(3 * math.sin(t * 3)), 2)
    else: sil(im, 135, 266, t)
    seg_len = (T[seg + 1] if seg < 6 else END) - T[seg]
    punch = .03 * max(0, 1 - (ts - 1.0) / .25) if 2 <= seg <= 5 and ts > 1.0 else 0
    z = 1.04 + .05 * (ts / seg_len) + punch
    big = im.resize((FW, FH), Image.NEAREST)
    cw, ch = FW / z, FH / z; amp = shake_amp(seg, ts); rg = np.random.default_rng(int(t * 30))
    ox = (FW - cw) / 2 + (math.sin(t * .5) * 6 if seg else 0) + rg.uniform(-amp, amp); oy = (FH - ch) * .55 + rg.uniform(-amp, amp)
    ox = min(max(ox, 0), FW - cw); oy = min(max(oy, 0), FH - ch)
    big = big.crop((int(ox), int(oy), int(ox + cw), int(oy + ch))).resize((FW, FH), Image.NEAREST)
    ui = ui_low(seg, ts, t).resize((FW, FH), Image.NEAREST)
    big = big.convert("RGBA"); big.alpha_composite(ui); big = big.convert("RGB")
    if 2 <= seg <= 5: draw_panel_text(big, seg, ts)
    if seg == 1: draw_winners(big, ts)
    if seg == 0 and t < 1.0: big = glitch(big, t, 1.0)
    elif seg == 1 and REVEAL <= ts < REVEAL + .25: big = glitch(big, t, .6)
    if seg == 1 and REVEAL <= ts < REVEAL + .3:       # reveal flash
        big = Image.blend(big, Image.new("RGB", (FW, FH), (255, 255, 255)), .9 * (1 - (ts - REVEAL) / .3))
    for i in range(1, 7):
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

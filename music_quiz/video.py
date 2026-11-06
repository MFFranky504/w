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

SCENES = [(SUNSET, dyn_sunset), (HOME, dyn_home), (STUDIO, dyn_studio), (NIGHT, dyn_night), (STAD, dyn_stadium), (SUNSET, dyn_sunset)]

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

def ui_low(seg, ts, t):
    """returns low-res RGBA UI layer and extra info"""
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
    if seg == 0:
        k = ease(ts / .35); dy = int((1 - k) * -30)
        lt(d, (135, 46 + dy), "¡SOLO LOS REALES", 17, WHITE); lt(d, (135, 70 + dy), "LO ADIVINAN!", 24, GOLD, shadow=(120, 50, 0))
        sc = 1 if ts > 1.2 else 0
        if ts > 1.2:
            d.rectangle((24, 300, 246, 322), fill=(14, 8, 34), outline=GOLD); lt(d, (135, 311), "¿LO ADIVINAS EN LA PISTA 1?", 11, WHITE)
        if ts > 1.8: lt(d, (135, 342), "ARTISTA MISTERIOSO · PARTE 8", 10, (255, 200, 120))
        return ui
    if seg == 5:
        sw = ts > 3.2
        a, b = ("¿CUÁNTOS PUNTOS", "SACASTE?") if sw else ("¿YA SABES", "QUIÉN ES?")
        ka = ease(ts / .3) if not sw else ease((ts - 3.2) / .25); dy = int((1 - ka) * -26)
        lt(d, (135, 52 + dy), a, 23 if not sw else 17, WHITE); lt(d, (135, 88 + dy), b, 34 if not sw else 30, GOLD, shadow=(120, 50, 0))
        if ts > .6 and not sw:
            d.rectangle((14, 112, 256, 134), fill=GOLD); lt(d, (135, 123), "ESCRÍBELO EN LOS COMENTARIOS", 11, DARK, shadow=(255, 230, 140))
        if ts > 1.2 and not sw: [d.polygon([(135 + o - 6, 148 + (2 if int(t * 3) % 2 else 0)), (135 + o + 6, 148 + (2 if int(t * 3) % 2 else 0)), (135 + o, 158 + (2 if int(t * 3) % 2 else 0))], fill=(255, 200, 120)) for o in (-24, 0, 24)]
        if ts > 3.5:
            d.rectangle((12, 306, 258, 328), fill=GOLD); lt(d, (135, 317), "REVELO AL ARTISTA EN EL PRÓXIMO VIDEO", 8, DARK, shadow=(255, 230, 140))
            lt(d, (135, 342), "SÍGUEME PARA LA PARTE 9", 10, WHITE)
        d.rectangle((70, 274, 200, 292), fill=(14, 8, 34), outline=GOLD) if ts > 2.0 else None
        if ts > 2.0: lt(d, (135, 283), "LONG BEACH", 12, GOLD)
        return ui
    c = CLUES[seg - 1]; n = c["n"]
    k = ease(ts / .3); dy = int((1 - k) * -30)
    lt(d, (135, 46 + dy), f"PISTA {n} / 4", 24, GOLD, shadow=(110, 50, 0))
    for i in range(4):
        fill = DIFFC[n - 1] if i < n and ts > .45 + i * .11 else (50, 36, 80)
        d.rectangle((66 + i * 36, 66 + dy, 98 + i * 36, 70 + dy), fill=fill)
    lt(d, (135, 80 + dy), f"DIFICULTAD: {c['diff']}", 11, DIFFC[n - 1])
    lt(d, (135, 92 + dy), f"VALE {c['pts']} PUNTO{'S' if c['pts'] > 1 else ''}", 10, (255, 230, 170))
    if ts > 1.0:
        f = F(18); w = int(d.textlength(c["chip"], font=f)) + 16; x0 = 135 - w // 2; fl = ts < 1.1
        d.rectangle((x0 - 2, 100, x0 + w + 2, 126), fill=(255, 205, 60)); d.rectangle((x0, 102, x0 + w, 124), fill=WHITE if fl else (14, 8, 34))
        lt(d, (135, 114), c["chip"], 18, DARK if fl else GOLD, shadow=(60, 30, 0))
    return ui

def draw_panel_text(img, seg, ts):
    c = CLUES[seg - 1]; lines, sp = LAY[seg - 1]
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
    s = 0
    for i in range(1, 6):
        if t >= T[i]: s = i
    return s

def render(t):
    seg = seg_of(t); ts = t - T[seg]
    base, dyn = SCENES[seg]
    im = base.copy(); dyn(im, t, ts, None)
    # silhouettes
    if seg == 3:
        sil(im, 100, 266, t, q=False); sil(im, 172, 266, t, hat=True, phase=.35, q=False); qmark(im, 136, 166 + int(3 * math.sin(t * 3)), 2)
    else:
        sil(im, 135, 266, t)
    # camera push (art only)
    seg_len = (T[seg + 1] if seg < 5 else END) - T[seg]
    z = 1.0 + .05 * (ts / seg_len) + (.03 * max(0, 1 - (ts - 1.0) / .25) if seg in (1, 2, 3, 4) and ts > 1.0 else 0)
    big = im.resize((FW, FH), Image.NEAREST)
    cw, ch = FW / z, FH / z; ox = (FW - cw) / 2 + (math.sin(t * .5) * 6 if seg else 0); oy = (FH - ch) * .55
    big = big.crop((int(ox), int(oy), int(ox + cw), int(oy + ch))).resize((FW, FH), Image.NEAREST) if z > 1.001 else big
    # vignette-less; UI layer
    ui = ui_low(seg, ts, t).resize((FW, FH), Image.NEAREST)
    big = big.convert("RGBA"); big.alpha_composite(ui); big = big.convert("RGB")
    if 1 <= seg <= 4: draw_panel_text(big, seg, ts)
    # wipe: nearest boundary
    for i in range(1, 6):
        p = (t - (T[i] - WIPE / 2)) / WIPE
        if 0 < p < 1: wipe(big, p)
    # fade in/out
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

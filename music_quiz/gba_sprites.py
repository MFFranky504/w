"""GBA-style (Kirby: Amazing Mirror-like) original pixel art for Parte 12 — sprite sheets only.
Original drawings: no tiles or sprites are copied from the references; they only guide the look
(dark outlines, 3-4 tone ramps, painterly backdrops framed by chunky foreground tiles).
usage: python3 gba_sprites.py  -> sprites/parte12/*.png"""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 270, 480                       # video canvas (low-res); the character stands on y=266
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte12")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F = lambda s: ImageFont.truetype(MONO, s)
INK = (24, 16, 40)                     # outline colour used everywhere (dark purple-navy, like GBA Kirby)
R = random.Random(12)
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

# ---------------------------------------------------------------- helpers
def grad(w, h, stops, steps=12):
    """vertical dithered gradient through a list of colours"""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w)); q = v * steps; base = np.floor(q)
    thr = np.tile(B4, (h // 4 + 1, w // 4 + 1))[:h, :w]; idx = np.clip(base + ((q - base) > thr), 0, steps) / steps
    st = np.array(stops, float); pos = idx * (len(stops) - 1); i = np.clip(pos.astype(int), 0, len(stops) - 2); f = (pos - i)[..., None]
    return Image.fromarray((st[i] + (st[i + 1] - st[i]) * f).astype(np.uint8))

def outline(im, col=INK):
    """1px dark outline around every opaque pixel of an RGBA image"""
    a = np.array(im); m = a[..., 3] > 0; o = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): o |= np.roll(np.roll(m, dy, 0), dx, 1)
    o &= ~m; a[o] = col + (255,); return Image.fromarray(a, "RGBA")

def silhouette(im):
    """channel-style mystery silhouette: navy fill + cyan/pink/gold rim light"""
    a = np.array(im)[..., 3] > 0; s = np.zeros(a.shape + (4,), np.uint8); s[a] = (14, 8, 34, 255)
    l = a & ~np.roll(a, 1, 1); r = a & ~np.roll(a, -1, 1); t = a & ~np.roll(a, 1, 0)
    s[l] = (70, 230, 255, 255); s[r] = (255, 70, 190, 255); s[t & ~l & ~r] = (255, 215, 90, 255)
    return Image.fromarray(s, "RGBA")

def cloud(d, x, y, w, base, shade, light):
    """painted GBA cloud: puffy top, flat shaded underside, highlight rim"""
    n = max(3, w // 12)
    for k in range(n):
        cx = x + k * w / (n - 1); r = R.randint(7, 12) if 0 < k < n - 1 else R.randint(5, 8)
        d.ellipse((cx - r, y - r, cx + r, y + r * .8), fill=base)
    d.rectangle((x - 4, y + 2, x + w + 4, y + 8), fill=base); d.rectangle((x, y + 6, x + w, y + 9), fill=shade)
    for k in range(n - 1):
        cx = x + k * w / (n - 1) + 2; d.arc((cx - 7, y - 9, cx + 6, y + 2), 200, 300, fill=light)

def pine(d, x, base_y, h, c=(40, 110, 80), cs=(26, 78, 60), cl=(76, 150, 104)):
    for k in range(4):
        w = h * (.42 - k * .08); y0 = base_y - h * k * .22
        d.polygon([(x - w, y0), (x + w, y0), (x, y0 - h * .38)], fill=c, outline=INK)
        d.polygon([(x + 1, y0 - 1), (x + w - 2, y0 - 1), (x, y0 - h * .36)], fill=cs)
        d.line([(x - w + 3, y0 - 2), (x - 2, y0 - h * .3)], fill=cl)
    d.rectangle((x - 2, base_y, x + 2, base_y + 6), fill=(110, 70, 44), outline=INK)

def mountains(d, base_y, peaks, col, snow, shade):
    pts = [(0, base_y)]
    for (px, ph) in peaks: pts += [(px - 34, base_y - ph * .35), (px, base_y - ph)]
    pts += [(W, base_y - 20), (W, base_y)]; d.polygon(pts, fill=col)
    for (px, ph) in peaks:
        d.polygon([(px, base_y - ph), (px - 9, base_y - ph + 12), (px - 3, base_y - ph + 9), (px + 2, base_y - ph + 13), (px + 9, base_y - ph + 11)], fill=snow)
        d.polygon([(px, base_y - ph), (px + 22, base_y - ph * .4), (px + 4, base_y - ph * .45)], fill=shade)

# foreground tiles (16x16), drawn with outline + ramp + texture
def tile_grass(x, y, d, top=True):
    dirt, dd, dl = (176, 110, 58), (130, 76, 40), (214, 150, 86)
    d.rectangle((x, y, x + 15, y + 15), fill=dirt)
    for _ in range(3): px, py = x + R.randint(1, 13), y + R.randint(4, 13); d.ellipse((px, py, px + 2, py + 2), fill=dd); d.point((px, py), fill=dl)
    if top:
        d.rectangle((x, y, x + 15, y + 5), fill=(92, 186, 72)); d.rectangle((x, y, x + 15, y + 1), fill=(160, 228, 110))
        for k in range(0, 16, 4): d.polygon([(x + k, y + 5), (x + k + 4, y + 5), (x + k + 2, y + 8)], fill=(92, 186, 72))
        d.line([(x, y + 6), (x + 15, y + 6)], fill=(56, 130, 52))
def tile_rock(x, y, d, base=(120, 130, 160), sh=(80, 86, 120), li=(170, 180, 210)):
    d.rectangle((x, y, x + 15, y + 15), fill=base, outline=INK)
    d.polygon([(x + 1, y + 1), (x + 14, y + 1), (x + 9, y + 6), (x + 1, y + 8)], fill=li)
    d.polygon([(x + 14, y + 4), (x + 14, y + 14), (x + 4, y + 14)], fill=sh)
def tile_metal(x, y, d):
    base, sh, li = (72, 196, 196), (36, 120, 140), (170, 248, 240)
    d.rectangle((x, y, x + 15, y + 15), fill=base, outline=INK); d.rectangle((x + 1, y + 1, x + 14, y + 3), fill=li)
    d.rectangle((x + 1, y + 12, x + 14, y + 14), fill=sh); d.rectangle((x + 5, y + 6, x + 10, y + 9), fill=(255, 170, 60), outline=INK)
def tile_wood(x, y, d, w=16):
    d.rectangle((x, y, x + w - 1, y + 7), fill=(196, 128, 70), outline=INK); d.line([(x + 1, y + 1), (x + w - 2, y + 1)], fill=(236, 176, 110))
    d.line([(x + 1, y + 6), (x + w - 2, y + 6)], fill=(140, 84, 44))
    for k in range(x + 7, x + w - 2, 8): d.line([(k, y + 2), (k, y + 5)], fill=(140, 84, 44))
def ground(d, y0, kind="grass", x0=0, x1=W):
    for x in range(x0, x1, 16):
        for k, y in enumerate(range(y0, H, 16)):
            if kind == "grass": tile_grass(x, y, d, top=(k == 0))
            elif kind == "metal": (tile_metal if k == 0 else (lambda a, b, c: tile_rock(a, b, c, (60, 90, 130), (40, 60, 96), (90, 130, 170))))(x, y, d)
            elif kind == "stone": tile_rock(x, y, d)
            elif kind == "tile_pool": tile_rock(x, y, d, (220, 236, 244), (160, 186, 206), (255, 255, 255))
            elif kind == "wood":
                d.rectangle((x, y, x + 15, y + 15), fill=(150, 96, 56)); d.line([(x, y), (x + 15, y)], fill=INK)
                d.line([(x, y + 1), (x + 15, y + 1)], fill=(210, 150, 90)); d.line([(x + 15, y), (x + 15, y + 15)], fill=(104, 64, 36))
    d.line([(x0, y0 - 1), (x1, y0 - 1)], fill=INK)
def side_walls(d, kind="stone", top=180, w=32):
    for x0 in (0, W - w):
        for x in range(x0, x0 + w, 16):
            for y in range(top, 266, 16):
                (tile_rock if kind == "stone" else (lambda a, b, c: tile_grass(a, b, c, top=(b == top))))(x, y, d)
        d.line([(x0 + (w if x0 == 0 else -1), top), (x0 + (w if x0 == 0 else -1), 266)], fill=INK)
def star(d, cx, cy, r=6, col=(255, 230, 80), sh=(232, 150, 30)):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * .45; pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=INK); d.polygon([pts[0], pts[1], (cx, cy), pts[9]], fill=(255, 250, 200)); d.polygon([(cx, cy), pts[4], pts[5], pts[6]], fill=sh)

# ---------------------------------------------------------------- backgrounds (270x480, foreground at y 266)
def bg_hook():
    im = grad(W, H, [(20, 24, 80), (40, 40, 120), (70, 48, 140), (40, 30, 90)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    for _ in range(90): x, y = R.randint(0, W), R.randint(0, 250); d.point((x, y), fill=R.choice([(200, 240, 255), (120, 220, 220), (255, 255, 255)]))
    for _ in range(10): x, y = R.randint(10, 260), R.randint(10, 240); d.line([(x - 2, y), (x + 2, y)], fill=(160, 250, 240)); d.line([(x, y - 2), (x, y + 2)], fill=(160, 250, 240))
    d.ellipse((150, 50, 250, 150), fill=(255, 236, 150)); d.ellipse((128, 40, 228, 140), fill=(40, 40, 120))          # crescent moon
    d.arc((150, 50, 250, 150), 20, 120, fill=(255, 252, 220), width=2)
    for k in range(3): cloud(d, 10 + k * 90, 196 + (k % 2) * 10, 60, (110, 90, 170), (78, 62, 136), (170, 150, 220))
    for x in range(0, W, 40):                                                                   # metal girders (ref: teal walkway)
        d.rectangle((x + 16, 266, x + 24, H), fill=(54, 150, 160), outline=INK); d.rectangle((x + 17, 266, x + 18, H), fill=(140, 230, 230))
    for y in range(290, H, 22): d.line([(0, y), (W, y + 10)], fill=(90, 70, 150)); d.line([(0, y + 10), (W, y)], fill=(90, 70, 150))   # chain-link mesh
    for x in range(0, W, 16): tile_metal(x, 252, d)
    d.line([(0, 251), (W, 251)], fill=INK)
    for (x, y) in ((40, 330), (210, 360), (120, 410), (60, 440)): star(d, x, y, 5)
    return im

def bg_wembley():                                                       # recap: Queen's Live Aid (1985) — stadium at sunset
    im = grad(W, H, [(80, 120, 200), (250, 170, 140), (250, 210, 150)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(4): cloud(d, 6 + k * 70, 40 + (k % 2) * 26, 48, (255, 236, 220), (236, 170, 160), (255, 255, 250))
    d.polygon([(0, 200), (W, 200), (W, 150), (0, 150)], fill=(90, 80, 130))                                             # stands
    for k in range(5): d.rectangle((0, 152 + k * 9, W, 156 + k * 9), fill=(110, 100, 150))
    for _ in range(260): x, y = R.randint(0, W), R.randint(152, 198); d.point((x, y), fill=R.choice([(255, 220, 180), (250, 120, 140), (180, 210, 255), (255, 255, 255)]))
    for x0 in (40, 230):                                                                                                 # twin towers
        d.rectangle((x0 - 12, 70, x0 + 12, 150), fill=(236, 232, 226), outline=INK); d.rectangle((x0 + 4, 72, x0 + 11, 150), fill=(196, 190, 186))
        d.polygon([(x0 - 14, 70), (x0 + 14, 70), (x0, 54)], fill=(236, 232, 226), outline=INK); d.line([(x0, 54), (x0, 44)], fill=INK)
        for y in range(80, 146, 12): d.rectangle((x0 - 6, y, x0 + 2, y + 6), fill=(110, 130, 180), outline=INK)
    d.rectangle((70, 170, 200, 236), fill=(40, 40, 70), outline=INK); d.rectangle((60, 162, 210, 172), fill=(70, 70, 110), outline=INK)   # stage
    for x in (74, 196): d.rectangle((x - 3, 172, x + 3, 236), fill=(60, 60, 90), outline=INK)
    for k in range(5): d.rectangle((84 + k * 22, 178, 98 + k * 22, 194), fill=(30, 30, 50), outline=(120, 120, 160))      # speaker stacks
    d.rectangle((0, 236, W, 266), fill=(70, 170, 80)); [d.line([(x, 236), (x + 40, 266)], fill=(90, 190, 96)) for x in range(-40, W, 30)]
    side_walls(d, "stone", 150, 16)
    ground(d, 266, "stone")
    for (x, y) in ((40, 300), (230, 330)): star(d, x, y, 5)
    return im

def bg_garage():                                                        # clue 1: the band's many early names — garage rehearsal
    im = grad(W, H, [(120, 80, 60), (170, 116, 80)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    for x in range(0, W, 14): d.rectangle((x, 0, x + 13, 266), fill=(170, 116, 80) if (x // 14) % 2 else (156, 104, 72), outline=(110, 70, 48))   # plank wall
    d.rectangle((150, 40, 262, 170), fill=(200, 200, 210), outline=INK)                                                  # roll-up door
    for y in range(44, 170, 9): d.line([(151, y), (261, y)], fill=(150, 150, 166))
    d.rectangle((150, 160, 262, 170), fill=(120, 120, 136), outline=INK)
    names = ["SKID ROW", "PEN CAP CHEW", "BLISS", "TED ED FRED"]                                                          # flyers, all crossed out
    for k, n in enumerate(names):
        x, y = 10 + (k % 2) * 66, 40 + (k // 2) * 50; c = [(255, 230, 120), (180, 230, 255), (255, 170, 200), (200, 255, 180)][k]
        d.rectangle((x, y, x + 60, y + 38), fill=c, outline=INK); d.ellipse((x + 28, y - 2, x + 32, y + 2), fill=(220, 40, 50), outline=INK)
        d.text((x + 30, y + 16), n, font=F(7 if len(n) > 9 else 8), fill=INK, anchor="mm"); d.line([(x + 4, y + 26), (x + 56, y + 30)], fill=(210, 30, 40), width=2)
        d.text((x + 30, y + 33), "?", font=F(7), fill=(120, 80, 60), anchor="mm")
    d.rectangle((14, 196, 54, 250), fill=(40, 34, 40), outline=INK); d.rectangle((18, 200, 50, 232), fill=(70, 62, 70)); [d.line([(18, y), (50, y)], fill=(54, 46, 54)) for y in range(204, 232, 4)]   # amp
    d.rectangle((14, 236, 54, 250), fill=(30, 26, 30)); [d.ellipse((20 + k * 8, 240, 24 + k * 8, 244), fill=(220, 220, 220)) for k in range(4)]
    d.ellipse((196, 206, 246, 250), fill=(200, 40, 50), outline=INK); d.ellipse((204, 214, 238, 242), fill=(250, 240, 230), outline=INK)   # kick drum
    d.ellipse((178, 190, 206, 198), fill=(240, 210, 80), outline=INK); d.line([(192, 198), (192, 250)], fill=(150, 150, 160), width=2)   # cymbal
    d.ellipse((236, 196, 262, 204), fill=(240, 210, 80), outline=INK); d.line([(249, 204), (249, 250)], fill=(150, 150, 160), width=2)
    d.polygon([(60, 160), (90, 160), (75, 140)], fill=(250, 240, 220), outline=INK); d.line([(75, 160), (75, 266)], fill=(110, 80, 50))     # hanging bulb
    ground(d, 266, "wood")
    for (x, y) in ((24, 300), (240, 300)): star(d, x, y, 5)
    return im

def bg_studio():                                                        # clue 2: a debut album that cost $606.17
    im = grad(W, H, [(40, 40, 70), (70, 60, 110)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    for y in range(0, 266, 16):
        for x in range(-((y // 16) % 2) * 8, W, 16): d.rectangle((x, y, x + 15, y + 15), fill=(60, 56, 96), outline=(40, 38, 70)); d.polygon([(x + 2, y + 2), (x + 13, y + 2), (x + 7, y + 8)], fill=(80, 74, 120))   # acoustic foam
    d.rectangle((60, 60, 210, 130), fill=(120, 160, 200), outline=INK); d.line([(135, 60), (135, 130)], fill=INK)          # control-room window
    d.rectangle((60, 124, 210, 130), fill=(90, 90, 110))
    for (cx, cy) in ((96, 92), (174, 92)):                                                                                # reel-to-reel
        d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(60, 60, 70), outline=INK); d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(200, 200, 210))
        for k in range(3): a = k * 2.1; d.line([(cx, cy), (cx + 13 * math.cos(a), cy + 13 * math.sin(a))], fill=(140, 140, 150))
    d.line([(96, 108), (174, 108)], fill=(90, 60, 40), width=2)
    d.rectangle((20, 200, 250, 250), fill=(70, 70, 86), outline=INK); d.polygon([(20, 200), (250, 200), (240, 186), (30, 186)], fill=(100, 100, 120), outline=INK)   # mixing desk
    for k in range(18):
        x = 34 + k * 12; d.line([(x, 190), (x, 198)], fill=(30, 30, 40)); d.rectangle((x - 2, 190 + (k * 7) % 7, x + 2, 193 + (k * 7) % 7), fill=(240, 240, 240))
        d.ellipse((x - 2, 206, x + 2, 210), fill=[(255, 90, 90), (90, 220, 120), (255, 210, 80)][k % 3])
    d.rectangle((86, 150, 184, 176), fill=(255, 230, 120), outline=INK); d.polygon([(86, 150), (74, 163), (86, 176)], fill=(255, 230, 120), outline=INK)   # price tag
    d.ellipse((80, 160, 85, 165), fill=(250, 250, 250), outline=INK); d.text((137, 163), "$606.17", font=F(13), fill=(170, 40, 40), anchor="mm")
    side_walls(d, "stone", 170, 16)
    ground(d, 266, "stone")
    for (x, y) in ((24, 300), (240, 300)): star(d, x, y, 5)
    return im

def bg_aberdeen():                                                      # clue 3: formed in 1987 in Aberdeen, Washington — rainy logging town
    im = grad(W, H, [(120, 150, 190), (170, 196, 214), (196, 214, 222)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(4): cloud(d, -10 + k * 80, 30 + (k % 2) * 22, 60, (150, 164, 186), (110, 124, 150), (200, 210, 226))
    mountains(d, 200, [(60, 90), (170, 110), (250, 80)], (120, 150, 180), (236, 244, 250), (96, 120, 152))
    for k in range(14): pine(d, 6 + k * 20, 214, 34 + (k % 3) * 8, (60, 120, 110), (44, 92, 90), (90, 150, 130))
    d.rectangle((0, 214, W, 236), fill=(90, 130, 150)); [d.line([(x, 220 + (x // 30) % 3 * 4), (x + 16, 220 + (x // 30) % 3 * 4)], fill=(170, 210, 220)) for x in range(0, W, 30)]   # river
    d.rectangle((0, 206, W, 210), fill=(160, 110, 70), outline=INK)                                                      # bridge deck
    for x in range(0, W, 30): d.rectangle((x + 4, 210, x + 8, 236), fill=(130, 90, 60), outline=INK)
    for x in range(0, W, 20): d.line([(x, 194), (x + 10, 206)], fill=(110, 80, 50)); d.line([(x + 10, 194), (x, 206)], fill=(110, 80, 50))
    d.line([(0, 194), (W, 194)], fill=(110, 80, 50), width=2)
    side_walls(d, "grass", 186, 32)
    for k in range(3): x = 40 + k * 70; d.ellipse((x, 246, x + 54, 262), fill=(176, 120, 70), outline=INK); d.ellipse((x + 44, 246, x + 54, 262), fill=(230, 190, 130), outline=INK); [d.arc((x + 45 + j, 248 + j, x + 53 - j, 260 - j), 0, 360, fill=(190, 140, 90)) for j in (2, 4)]   # log pile
    ground(d, 266, "grass")
    d.rectangle((196, 140, 250, 162), fill=(40, 110, 70), outline=INK); d.text((223, 151), "1987", font=F(10), fill=(250, 250, 240), anchor="mm")   # road sign (year only)
    d.rectangle((221, 162, 225, 186), fill=(150, 150, 160), outline=INK)
    return im

def bg_pool():                                                          # clue 4: the album cover idea — underwater, a bill on a fishhook (no baby)
    im = grad(W, H, [(150, 230, 255), (40, 150, 220), (20, 80, 170), (12, 40, 110)]).convert("RGB"); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((0, 0, W, 40), fill=(230, 250, 255)); [d.arc((x - 20, 30, x + 20, 50), 200, 340, fill=(120, 200, 240), width=2) for x in range(0, W + 40, 34)]   # surface
    for y in range(60, 260, 22):                                                                                          # caustic light net
        for x in range(-((y // 22) % 2) * 17, W, 34): d.arc((x, y, x + 34, y + 22), 200, 340, fill=(130, 220, 255))
    for k in range(-3, 4): d.polygon([(135 + k * 40, 40), (135 + k * 40 + 14, 40), (135 + k * 60 + 24, 266), (135 + k * 60, 266)], fill=None, outline=(110, 200, 250))
    d.line([(180, 0), (180, 150)], fill=(60, 60, 70)); d.arc((170, 144, 190, 164), 0, 200, fill=(170, 170, 180), width=2)   # fishing line + hook
    d.rectangle((150, 160, 210, 186), fill=(150, 210, 140), outline=INK); d.rectangle((154, 164, 206, 182), outline=(80, 150, 90))   # the bill
    d.ellipse((172, 166, 188, 180), fill=(120, 190, 120), outline=(70, 130, 80)); d.text((158, 168), "1", font=F(7), fill=(40, 90, 50)); d.text((198, 176), "1", font=F(7), fill=(40, 90, 50))
    for _ in range(26): x, y, r = R.randint(10, 260), R.randint(60, 250), R.randint(2, 6); d.ellipse((x - r, y - r, x + r, y + r), outline=(220, 250, 255)); d.point((x - r // 2, y - r // 2), fill=WHITE)
    d.rectangle((0, 120, 16, 266), fill=(220, 236, 244), outline=INK); d.rectangle((254, 120, W, 266), fill=(220, 236, 244), outline=INK)   # pool ladder rails
    for y in range(140, 266, 24): d.rectangle((0, y, 16, y + 3), fill=(180, 190, 200), outline=INK); d.rectangle((254, y, W, y + 3), fill=(180, 190, 200), outline=INK)
    ground(d, 266, "tile_pool")
    for x in range(0, W, 16): d.line([(x, 266), (x, H)], fill=(160, 186, 206))
    return im
WHITE = (250, 248, 244)

# ---------------------------------------------------------------- characters (tall and slim, ~100x140 cell, feet at y=138)
def kurt(frame=0):
    """grunge singer-guitarist (original design): shaggy blond hair, white oval sunglasses, fuzzy olive cardigan,
    striped tee, ripped jeans, worn sneakers, left-handed offset guitar. frame 0 idle, 1-3 strum cycle."""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    SK, SKS = (238, 196, 168), (206, 156, 128); HAIR, HAIRS, HAIRL = (226, 188, 96), (186, 146, 64), (250, 226, 150)
    CARD, CARDS, CARDL = (120, 128, 70), (88, 94, 50), (152, 160, 92); JEANS, JS = (110, 140, 190), (82, 106, 150)
    bob = [0, 1, 0, -1][frame]; strum = [0, 1, 2, 1][frame]
    for x0 in (38, 52):                                                       # legs + ripped knees + sneakers
        d.rectangle((x0, 94, x0 + 10, 132), fill=JEANS); d.rectangle((x0 + 7, 94, x0 + 10, 132), fill=JS)
        d.rectangle((x0 + 1, 110, x0 + 8, 113), fill=SK); d.line([(x0 + 1, 110), (x0 + 8, 110)], fill=(240, 240, 250)); d.line([(x0 + 1, 113), (x0 + 8, 113)], fill=(240, 240, 250))
        d.rounded_rectangle((x0 - 2, 130, x0 + 12, 138), 2, fill=(70, 66, 80)); d.rectangle((x0 - 2, 136, x0 + 12, 138), fill=(236, 232, 224))
    d.rectangle((40, 60, 60, 96), fill=(236, 236, 240)); [d.rectangle((40, y, 60, y + 2), fill=(120, 40, 50)) for y in range(62, 96, 6)]   # striped tee
    d.polygon([(34, 52 + bob), (44, 52 + bob), (42, 100), (32, 100)], fill=CARD); d.polygon([(56, 52 + bob), (66, 52 + bob), (68, 100), (58, 100)], fill=CARD)   # cardigan fronts
    d.rectangle((32, 54 + bob, 36, 100), fill=CARDL); d.rectangle((64, 54 + bob, 68, 100), fill=CARDS)
    for y in range(66, 98, 10): d.ellipse((42, y, 45, y + 3), fill=(60, 50, 40))
    for k in range(40): x, y = R.randint(32, 68), R.randint(54, 99); px = im.getpixel((x, y))
    d.polygon([(34, 54 + bob), (26, 62), (24, 96), (30, 98), (34, 70)], fill=CARD); d.rectangle((23, 94, 31, 102), fill=SK)                                   # right arm down
    gx, gy = 50, 90                                                                                                       # left-handed guitar (body on the right)
    d.polygon([(gx - 34, gy - 22), (gx - 30, gy - 26), (gx + 4, gy - 4), (gx, gy)], fill=(120, 80, 50))                   # neck (headstock to the left)
    d.rectangle((gx - 38, gy - 30, gx - 30, gy - 22), fill=(60, 40, 30))
    d.ellipse((gx - 2, gy - 12, gx + 22, gy + 10), fill=(60, 120, 200)); d.ellipse((gx + 6, gy - 4, gx + 30, gy + 16), fill=(60, 120, 200))
    d.ellipse((gx + 2, gy - 8, gx + 16, gy + 4), fill=(240, 240, 236)); d.rectangle((gx + 8, gy - 2, gx + 18, gy + 1), fill=(40, 40, 50))
    d.line([(gx - 30, gy - 24), (gx + 18, gy)], fill=(220, 220, 230))
    hx, hy = 62 + strum * 2, 84 - strum * 3; d.polygon([(66, 54 + bob), (74, 60), (hx + 4, hy), (hx - 2, hy + 2), (68, 66)], fill=CARD); d.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=SK)   # strumming arm
    d.rectangle((45, 42 + bob, 55, 54 + bob), fill=SKS)                                                                   # neck
    d.ellipse((38, 14 + bob, 62, 48 + bob), fill=SK); d.ellipse((50, 18 + bob, 62, 46 + bob), fill=SKS)                  # face
    d.rectangle((44, 41 + bob, 56, 46 + bob), fill=(200, 160, 110)); d.point((47, 43 + bob), fill=(150, 110, 70)); d.point((52, 44 + bob), fill=(150, 110, 70))   # stubble
    d.line([(46, 38 + bob), (54, 38 + bob)], fill=(150, 80, 80))
    for cx in (44, 56): d.ellipse((cx - 6, 26 + bob, cx + 6, 34 + bob), fill=(250, 250, 250), outline=(180, 180, 190)); d.ellipse((cx - 4, 27 + bob, cx + 4, 33 + bob), fill=(30, 30, 44)); d.point((cx - 2, 28 + bob), fill=(160, 170, 255))   # white oval sunglasses
    d.line([(50, 30 + bob), (50, 30 + bob)], fill=(250, 250, 250))
    d.ellipse((32, 6 + bob, 68, 34 + bob), fill=HAIR)                                                                    # shaggy hair, parted, over the ears
    d.polygon([(32, 20 + bob), (40, 18 + bob), (42, 52 + bob), (34, 50 + bob)], fill=HAIR); d.polygon([(68, 20 + bob), (60, 18 + bob), (60, 52 + bob), (68, 48 + bob)], fill=HAIRS)
    d.polygon([(40, 14 + bob), (48, 12 + bob), (46, 28 + bob), (40, 26 + bob)], fill=HAIR); d.polygon([(52, 12 + bob), (62, 16 + bob), (60, 28 + bob), (54, 26 + bob)], fill=HAIR)
    for (x0, y0, x1, y1) in ((36, 10, 46, 16), (34, 24, 36, 40), (60, 22, 62, 34)): d.line([(x0, y0 + bob), (x1, y1 + bob)], fill=HAIRL)
    for (x0, y0) in ((34, 50), (38, 52), (64, 48), (60, 52)): d.line([(x0, y0 + bob), (x0 + R.randint(-2, 2), y0 + 5 + bob)], fill=HAIRS, width=2)
    return outline(im)

def freddie(frame=0):
    """Live Aid 1985 look (original design): short black hair, moustache, white tank top, light-wash jeans, studded armband,
    belt, white high-tops, half mic stand. frame 0 idle, 1 fist up, 2 lunge, 3 fist up (alt)."""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    SK, SKS, SKL = (196, 146, 110), (160, 112, 82), (220, 172, 136); TANK, TS = (248, 248, 250), (210, 214, 224); JE, JS = (150, 186, 220), (116, 150, 190)
    up = frame in (1, 3); lunge = frame == 2; dy = 1 if lunge else 0
    for k, x0 in enumerate((36, 54)):                                                         # legs (wider stance when lunging)
        off = (-4 if k == 0 else 4) if lunge else 0
        d.polygon([(x0 + 2, 92), (x0 + 12, 92), (x0 + 12 + off, 132), (x0 + 2 + off, 132)], fill=JE); d.line([(x0 + 10, 94), (x0 + 11 + off, 130)], fill=JS)
        d.rounded_rectangle((x0 + off, 128, x0 + 14 + off, 138), 2, fill=WHITE); d.rectangle((x0 + off, 136, x0 + 14 + off, 138), fill=(190, 190, 200)); d.line([(x0 + 3 + off, 131), (x0 + 11 + off, 131)], fill=(60, 60, 70))
    d.rectangle((36, 88 + dy, 68, 94 + dy), fill=(70, 50, 40)); d.rectangle((49, 88 + dy, 55, 94 + dy), fill=(230, 210, 120), outline=INK)          # belt + buckle
    d.rounded_rectangle((38, 52 + dy, 66, 90 + dy), 4, fill=TANK); d.rectangle((60, 54 + dy, 66, 90 + dy), fill=TS)                                    # tank top
    d.polygon([(42, 52 + dy), (48, 52 + dy), (52, 62 + dy), (56, 52 + dy), (62, 52 + dy), (60, 46 + dy), (44, 46 + dy)], fill=SK)                    # chest/neckline
    d.rectangle((28, 54 + dy, 38, 60 + dy), fill=SK); d.rectangle((66, 54 + dy, 76, 60 + dy), fill=SK)                                                # shoulders
    d.polygon([(28, 56 + dy), (22, 70 + dy), (24, 92 + dy), (30, 92 + dy), (32, 70 + dy), (36, 60 + dy)], fill=SK)                                    # left arm holds the half mic stand
    d.rectangle((22, 66 + dy, 32, 70 + dy), fill=(30, 30, 36)); [d.point((24 + k * 2, 68 + dy), fill=(220, 220, 230)) for k in range(4)]             # studded armband
    d.line([(26, 92 + dy), (16, 64 + dy)], fill=(180, 180, 190), width=3); d.ellipse((12, 56 + dy, 20, 66 + dy), fill=(60, 60, 70), outline=INK)      # half mic stand + mic
    d.ellipse((22, 88 + dy, 30, 96 + dy), fill=SK)
    if up:                                                                                     # right fist in the air
        d.polygon([(70, 56), (78, 54), (84, 30), (78, 28)], fill=SK); d.polygon([(78, 28), (84, 30), (86, 12), (80, 10)], fill=SK); d.rectangle((77, 2, 89, 12), fill=SK); d.line([(79, 6), (87, 6)], fill=SKS)
    else:
        d.polygon([(68, 56 + dy), (76, 56 + dy), (80, 90 + dy), (72, 92 + dy)], fill=SK); d.ellipse((72, 88 + dy, 80, 96 + dy), fill=SK)
    d.rectangle((46, 40 + dy, 56, 50 + dy), fill=SKS)                                                                       # neck
    d.ellipse((38, 14 + dy, 64, 46 + dy), fill=SK); d.ellipse((54, 18 + dy, 64, 44 + dy), fill=SKS); d.ellipse((40, 30 + dy, 46, 40 + dy), fill=SKL)
    d.ellipse((36, 26 + dy, 40, 36 + dy), fill=SK)
    d.ellipse((38, 8 + dy, 64, 26 + dy), fill=(22, 18, 24)); d.rectangle((38, 16 + dy, 42, 28 + dy), fill=(22, 18, 24)); d.rectangle((60, 16 + dy, 64, 26 + dy), fill=(22, 18, 24))   # short black hair
    d.line([(42, 12 + dy), (50, 10 + dy)], fill=(70, 66, 80))
    for ex in (44, 54): d.rectangle((ex, 27 + dy, ex + 4, 29 + dy), fill=(240, 236, 230)); d.rectangle((ex + 2, 27 + dy, ex + 3, 29 + dy), fill=(30, 20, 18)); d.line([(ex - 1, 25 + dy), (ex + 5, 24 + dy)], fill=(22, 18, 24), width=2)
    d.rectangle((49, 30 + dy, 52, 35 + dy), fill=SKS)
    d.rectangle((44, 36 + dy, 58, 39 + dy), fill=(22, 18, 24))                                                              # moustache
    d.rectangle((46, 40 + dy, 56, 43 + dy), fill=(250, 248, 240) if up or lunge else (150, 80, 80)); d.line([(46, 43 + dy), (56, 43 + dy)], fill=(120, 60, 60))   # open mouth when singing
    return outline(im)

# ---------------------------------------------------------------- tiles + UI parts
def tiles_ui():
    im = Image.new("RGBA", (256, 168), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"; items = []
    def lab(x, y, t): items.append((x, y, t))
    tile_grass(4, 4, d); tile_grass(20, 4, d); tile_grass(4, 20, d, top=False); tile_grass(20, 20, d, top=False); lab(4, 38, "hierba")
    tile_rock(44, 4, d); tile_rock(60, 4, d); tile_rock(44, 20, d); tile_rock(60, 20, d); lab(44, 38, "piedra")
    tile_metal(84, 4, d); tile_metal(100, 4, d); lab(84, 38, "metal")
    tile_wood(84, 22, d, 32); lab(84, 32, "")
    tile_rock(124, 4, d, (220, 236, 244), (160, 186, 206), (255, 255, 255)); tile_rock(140, 4, d, (220, 236, 244), (160, 186, 206), (255, 255, 255)); lab(124, 38, "azulejo")
    for k in range(4): star(d, 176 + k * 20, 16, [9, 8, 6, 8][k], [(255, 230, 80), (255, 240, 140), (255, 250, 200), (255, 240, 140)][k]); lab(164, 38, "estrella x4")
    for k in range(2):                                                               # "?" block (2 frames)
        x = 4 + k * 22; d.rectangle((x, 50, x + 17, 67), fill=(255, 170, 60) if k == 0 else (255, 200, 90), outline=INK); d.rectangle((x + 1, 51, x + 16, 53), fill=(255, 230, 150)); d.rectangle((x + 1, 64, x + 16, 66), fill=(200, 110, 30))
        d.text((x + 9, 59), "?", font=F(12), fill=WHITE, anchor="mm", stroke_width=1, stroke_fill=INK)
    lab(4, 70, "bloque ?")
    for k in range(3):                                                               # music notes
        x = 60 + k * 14; c = [(255, 230, 80), (255, 110, 190), (90, 235, 255)][k]
        d.rectangle((x + 5, 50, x + 6, 62), fill=c, outline=INK); d.ellipse((x, 59, x + 7, 66), fill=c, outline=INK); d.rectangle((x + 6, 50, x + 10, 53), fill=c, outline=INK)
    lab(60, 70, "notas")
    # bottom name box ("solo un poco" HUD): dark panel, gold border, clue name + difficulty bar
    x0, y0 = 4, 84; d.rectangle((x0, y0, x0 + 160, y0 + 26), fill=(20, 16, 40), outline=INK); d.rectangle((x0 + 2, y0 + 2, x0 + 158, y0 + 24), outline=(255, 214, 80))
    d.text((x0 + 8, y0 + 9), "PISTA 1/4", font=F(9), fill=(255, 230, 120), anchor="lm"); d.text((x0 + 152, y0 + 9), "ULTRA DIFÍCIL", font=F(8), fill=(255, 110, 110), anchor="rm")
    for k in range(10): d.rectangle((x0 + 8 + k * 14, y0 + 16, x0 + 19 + k * 14, y0 + 20), fill=(255, 90, 90) if k < 7 else (60, 50, 90), outline=INK)
    lab(x0, y0 + 28, "cuadro inferior (pista + dificultad + tiempo)")
    x0 = 172; d.rectangle((x0, 84, x0 + 78, 104), fill=(14, 8, 34), outline=(255, 214, 80)); d.text((x0 + 39, 94), "$606.17", font=F(11), fill=(255, 214, 80), anchor="mm"); lab(x0, 106, "chip de pista")
    for k in range(4):                                                               # difficulty pips
        d.rectangle((4 + k * 22, 128, 22 + k * 22, 134), fill=[(235, 60, 60), (255, 140, 40), (255, 215, 60), (80, 230, 120)][k], outline=INK)
    lab(4, 138, "dificultad 1-4")
    qm = ["01110", "10001", "00001", "00110", "00100", "00000", "00100"]             # big "?" pickup
    q = Image.new("RGBA", (24, 30), (0, 0, 0, 0)); qd = ImageDraw.Draw(q)
    for j, row in enumerate(qm):
        for i, c in enumerate(row):
            if c == "1": qd.rectangle((2 + i * 4, 1 + j * 4, 5 + i * 4, 4 + j * 4), fill=(255, 214, 80)); qd.point((2 + i * 4, 1 + j * 4), fill=(255, 246, 190))
    q = outline(q); im.alpha_composite(q, (108, 122))
    lab(104, 148, "? del misterio")
    return im, items

# ---------------------------------------------------------------- sheets
def label(d, x, y, t, s=14, col=(255, 240, 200)): d.text((x, y), t, font=F(s), fill=col, stroke_width=2, stroke_fill=(10, 6, 20))

def main():
    os.makedirs(OUT, exist_ok=True)
    bgs = [("HOOK (noche estrellada)", bg_hook()), ("AYER: QUEEN · Live Aid 1985", bg_wembley()), ("PISTA 1 · los nombres de antes", bg_garage()),
           ("PISTA 2 · el álbum de $606.17", bg_studio()), ("PISTA 3 · 1987, pueblo maderero", bg_aberdeen()), ("PISTA 4 · la portada (anzuelo)", bg_pool())]
    s = 2; cw, ch = W * s, H * s; sheet = Image.new("RGB", (3 * cw + 40, 2 * ch + 120), (16, 12, 30)); d = ImageDraw.Draw(sheet)
    label(d, 10, 10, "PARTE 12 · FONDOS (270x480, ×2) · estilo GBA original", 22)
    for i, (t, im) in enumerate(bgs):
        x, y = 10 + (i % 3) * (cw + 10), 50 + (i // 3) * (ch + 34); sheet.paste(im.resize((cw, ch), Image.NEAREST), (x, y)); label(d, x, y + ch + 4, t, 16)
        im.save(os.path.join(OUT, f"fondo_{i}.png"))
    sheet.save(os.path.join(OUT, "parte12_fondos.png"))
    s = 4; K = [kurt(f) for f in range(4)]; Q = [freddie(f) for f in range(4)]
    sheet = Image.new("RGB", (6 * 100 * s + 70, 2 * 140 * s + 140), (40, 34, 70)); d = ImageDraw.Draw(sheet)
    label(d, 10, 10, "PARTE 12 · PERSONAJES (100x140, ×4) · altos y delgados, contorno GBA", 22)
    rows = [("ARTISTA (misterio)", [silhouette(K[0])] + K + [silhouette(K[2])], ["silueta", "quieto", "rasgueo 1", "rasgueo 2", "rasgueo 3", "silueta 2"]),
            ("AYER: QUEEN", [silhouette(Q[0])] + Q + [silhouette(Q[1])], ["silueta", "quieto", "puño arriba", "zancada", "puño 2", "silueta 2"])]
    for r, (name, frames, tags) in enumerate(rows):
        y = 50 + r * (140 * s + 44)
        for k, fr in enumerate(frames):
            x = 10 + k * (100 * s + 10); bg = Image.new("RGBA", fr.size, (90, 80, 140, 255) if k in (0, 5) else (180, 170, 220, 255)); bg.alpha_composite(fr)
            sheet.paste(bg.convert("RGB").resize((100 * s, 140 * s), Image.NEAREST), (x, y)); label(d, x + 6, y + 6, tags[k], 18)
        label(d, 10, y + 140 * s + 4, name, 20)
        for k, fr in enumerate(frames): fr.save(os.path.join(OUT, f"{'artista' if r == 0 else 'ayer_queen'}_{k}.png"))
    sheet.save(os.path.join(OUT, "parte12_personajes.png"))
    t, items = tiles_ui(); s = 4; sheet = Image.new("RGB", (t.width * s + 20, t.height * s + 70), (60, 52, 96)); d = ImageDraw.Draw(sheet)
    label(d, 10, 10, "PARTE 12 · TILES Y UI (×4)", 22); sheet.paste(t.resize((t.width * s, t.height * s), Image.NEAREST), (10, 50), t.resize((t.width * s, t.height * s), Image.NEAREST))
    for (x, y, txt) in items:
        if txt: label(d, 10 + x * s, 50 + y * s, txt, 14)
    sheet.save(os.path.join(OUT, "parte12_tiles_ui.png")); t.save(os.path.join(OUT, "tiles_ui.png"))
    print("ok", OUT)

if __name__ == "__main__":
    main()

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

def masonry(d, x0, y0, x1, y1, base=(124, 132, 164), sh=(86, 92, 126), li=(176, 184, 214), mortar=(70, 72, 100), seed=3):
    """continuous irregular stone wall: staggered stones of varying width, rounded, mortar lines (no per-tile outline)"""
    r = random.Random(seed); d.rectangle((x0, y0, x1, y1), fill=mortar); y = y0; row = 0
    while y <= y1:
        h = r.randint(9, 13); x = x0 - r.randint(0, 14)
        while x <= x1:
            w = r.randint(14, 26); bx0, by0, bx1, by1 = x + 1, y + 1, min(x + w - 1, x1), min(y + h - 1, y1)
            if bx1 > bx0 + 5 and by1 > by0 + 5:
                c = tuple(max(0, min(255, v + r.randint(-8, 8))) for v in base)
                d.rounded_rectangle((bx0, by0, bx1, by1), 3, fill=c)
                d.line([(bx0 + 2, by0 + 1), (bx1 - 3, by0 + 1)], fill=li); d.line([(bx0 + 1, by0 + 2), (bx0 + 1, by1 - 3)], fill=li)
                d.line([(bx0 + 3, by1), (bx1 - 1, by1)], fill=sh); d.line([(bx1, by0 + 3), (bx1, by1 - 1)], fill=sh)
                for _ in range(r.randint(0, 3)): px, py = r.randint(bx0 + 2, bx1 - 2), r.randint(by0 + 2, by1 - 2); d.point((px, py), fill=sh)
                if r.random() < .12: d.line([(bx0 + 3, by0 + 3), (bx0 + 6, by0 + 6), (bx0 + 5, by0 + 9)], fill=sh)        # crack
            x += w
        y += h; row += 1

def pool_tiles(d, x0, y0, x1, y1, size=10, base=(206, 234, 246), grout=(150, 186, 206), li=(244, 252, 255), deep=(150, 200, 228)):
    """continuous glazed tiles: thin grout grid, soft glaze highlight, colour deepening with depth (no black outlines)"""
    for y in range(y0, y1 + 1, size):
        f = min(1, (y - y0) / max(y1 - y0, 1)); c = tuple(int(base[k] + (deep[k] - base[k]) * f) for k in range(3))
        for x in range(x0, x1 + 1, size):
            d.rectangle((x, y, x + size - 1, y + size - 1), fill=c)
            d.line([(x + 1, y + 1), (x + 4, y + 1)], fill=li); d.point((x + 1, y + 2), fill=li)
        d.line([(x0, y), (x1, y)], fill=grout)
    for x in range(x0, x1 + 1, size): d.line([(x, y0), (x, y1)], fill=grout)

def ground(d, y0, kind="grass", x0=0, x1=W):
    for x in range(x0, x1, 16):
        for k, y in enumerate(range(y0, H, 16)):
            if kind == "grass": tile_grass(x, y, d, top=(k == 0))
            elif kind == "metal": (tile_metal if k == 0 else (lambda a, b, c: tile_rock(a, b, c, (60, 90, 130), (40, 60, 96), (90, 130, 170))))(x, y, d)
            elif kind in ("stone", "tile_pool"): pass
            elif kind == "wood":
                d.rectangle((x, y, x + 15, y + 15), fill=(150, 96, 56)); d.line([(x, y), (x + 15, y)], fill=INK)
                d.line([(x, y + 1), (x + 15, y + 1)], fill=(210, 150, 90)); d.line([(x + 15, y), (x + 15, y + 15)], fill=(104, 64, 36))
    if kind == "stone": masonry(d, x0, y0, x1, H, seed=y0)
    if kind == "tile_pool": pool_tiles(d, x0, y0, x1, H)
    d.line([(x0, y0 - 1), (x1, y0 - 1)], fill=INK)
def side_walls(d, kind="stone", top=180, w=32):
    for x0 in (0, W - w):
        if kind == "stone": masonry(d, x0, top, x0 + w - 1, 265, seed=x0 + top)
        else:
            for x in range(x0, x0 + w, 16):
                for y in range(top, 266, 16): tile_grass(x, y, d, top=(y == top))
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
    pool_tiles(d, 0, 120, 15, 265); pool_tiles(d, 254, 120, W, 265); d.line([(16, 120), (16, 266)], fill=INK); d.line([(253, 120), (253, 266)], fill=INK)   # tiled pool walls
    for y in range(140, 266, 24): d.rectangle((0, y, 16, y + 3), fill=(180, 190, 200), outline=INK); d.rectangle((254, y, W, y + 3), fill=(180, 190, 200), outline=INK)
    ground(d, 266, "tile_pool")
    return im
WHITE = (250, 248, 244)


# ---------------------------------------------------------------- detail passes (more colour, light and props)
def glow(im, cx, cy, r, col, k=.5):
    a = np.array(im).astype(float); yy, xx = np.mgrid[0:im.height, 0:im.width]
    m = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 2 * k; a = np.clip(a + m[..., None] * np.array(col), 0, 255)
    return Image.fromarray(a.astype(np.uint8))
def beam(im, x0, x1, y0, y1, w0, w1, col, k=.25):
    a = np.array(im).astype(float)
    for y in range(max(y0, 0), min(y1, im.height)):
        f = (y - y0) / max(y1 - y0, 1); cx = x0 + (x1 - x0) * f; hw = (w0 + (w1 - w0) * f) / 2
        xa, xb = max(int(cx - hw), 0), min(int(cx + hw), im.width)
        if xa < xb: a[y, xa:xb] = np.clip(a[y, xa:xb] + np.array(col) * k * (1 - f * .6), 0, 255)
    return Image.fromarray(a.astype(np.uint8))
def noise(im, box, cols, n):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = box
    for _ in range(n): d.point((R.randint(x0, x1), R.randint(y0, y1)), fill=R.choice(cols))
def string_lights(d, x0, x1, y, sag=10):
    for k in range(int((x1 - x0) / 10) + 1):
        x = x0 + k * 10; yy = y + sag * math.sin(math.pi * k * 10 / (x1 - x0)); d.point((x, yy - 1), fill=(60, 50, 60))
        c = [(255, 90, 90), (255, 220, 80), (90, 230, 120), (90, 190, 255), (230, 120, 255)][k % 5]; d.rectangle((x - 1, yy, x + 1, yy + 3), fill=c, outline=INK)
def plant(d, x, y):
    d.polygon([(x - 7, y), (x + 7, y), (x + 5, y + 12), (x - 5, y + 12)], fill=(200, 100, 70), outline=INK); d.line([(x - 6, y + 2), (x + 6, y + 2)], fill=(236, 140, 100))
    for a in (-60, -30, 0, 30, 60): r = math.radians(a - 90); d.line([(x, y), (x + 12 * math.cos(r), y + 12 * math.sin(r))], fill=(60, 160, 80), width=3)
def fish(d, x, y, c, flip=1):
    d.ellipse((x - 6, y - 3, x + 6, y + 3), fill=c, outline=INK); d.polygon([(x - 6 * flip, y), (x - 10 * flip, y - 4), (x - 10 * flip, y + 4)], fill=c, outline=INK); d.point((x + 3 * flip, y - 1), fill=INK)

def more_hook(im):
    im = glow(im, 200, 100, 120, (120, 90, 200), .5); d = ImageDraw.Draw(im); d.fontmode = "1"
    for (cx, cy, r, c, ring) in ((60, 70, 14, (240, 130, 170), (255, 210, 230)), (230, 180, 6, (130, 230, 200), None)):   # planets
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c, outline=INK); d.ellipse((cx - r + 3, cy - r + 3, cx, cy), fill=tuple(min(255, v + 40) for v in c))
        if ring: d.arc((cx - r - 8, cy - 5, cx + r + 8, cy + 6), 0, 180, fill=ring, width=2)
    for k in range(5):                                                       # hanging stars on strings
        x = 30 + k * 52; y = 140 + (k % 2) * 30; d.line([(x, 0), (x, y - 6)], fill=(110, 100, 170)); star(d, x, y, 7)
    for _ in range(40):
        x, y = R.randint(0, W), R.randint(0, 240); d.point((x, y), fill=R.choice([(255, 200, 240), (170, 250, 255)]))
    for k in range(6): x = 18 + k * 46; d.rectangle((x, 240, x + 6, 251), fill=(255, 210, 90), outline=INK); d.point((x + 3, 238), fill=(255, 255, 200))   # walkway lamps
    for x in range(0, W, 40): d.rectangle((x + 16, 340, x + 24, H), fill=(36, 96, 120))
    return im
def more_wembley(im):
    im = glow(im, 135, 150, 170, (255, 170, 110), .45)
    for k, x in enumerate((70, 135, 200)): im = beam(im, x, x + (k - 1) * 60, 170, 20, 4, 60, [(255, 120, 160), (255, 240, 180), (120, 200, 255)][k], .22)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(3): cloud(d, 20 + k * 90, 110 + (k % 2) * 8, 40, (255, 210, 200), (240, 170, 170), (255, 240, 236))
    for k in range(9): x = 20 + k * 29; d.line([(x, 150), (x, 138)], fill=INK); d.polygon([(x, 138), (x + 9, 141), (x, 144)], fill=[(220, 40, 60), (250, 250, 250), (40, 80, 200)][k % 3], outline=INK)   # flags
    d.rectangle((96, 120, 174, 150), fill=(30, 30, 50), outline=INK)                                                     # big screen
    for y in range(122, 149, 2): d.line([(98, y), (172, y)], fill=[(255, 120, 160), (255, 200, 120), (140, 200, 255)][(y // 6) % 3])
    d.text((135, 135), "LIVE", font=F(12), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=INK)
    for _ in range(200): x, y = R.randint(0, W), R.randint(236, 264); d.point((x, y), fill=R.choice([(255, 220, 180), (250, 120, 140), (180, 210, 255), (255, 240, 120), (40, 30, 60)]))   # crowd on the pitch
    for k in range(30): x = 4 + k * 9; d.line([(x, 250), (x + 2, 240 - (k % 3) * 2)], fill=(60, 40, 70), width=2)      # raised arms
    return im
def more_garage(im):
    d = ImageDraw.Draw(im); d.fontmode = "1"
    noise(im, (0, 0, 148, 180), [(150, 98, 66), (186, 128, 90), (140, 92, 62)], 600)
    string_lights(d, 0, W, 8, 8)
    d.rectangle((150, 40, 262, 170), fill=(140, 170, 210), outline=INK); [d.line([(151, y), (261, y)], fill=(170, 196, 226)) for y in range(44, 170, 9)]   # half-open door with rain outside
    for _ in range(60): x, y = R.randint(152, 260), R.randint(44, 120); d.line([(x, y), (x - 2, y + 5)], fill=(200, 220, 250))
    d.rectangle((150, 120, 262, 170), fill=(200, 200, 210), outline=INK); [d.line([(151, y), (261, y)], fill=(150, 150, 166)) for y in range(124, 170, 9)]
    d.rectangle((10, 140, 140, 144), fill=(110, 70, 44), outline=INK)                                                     # shelf with paint cans + cassette
    for k, c in enumerate([(220, 60, 60), (60, 140, 220), (240, 200, 60), (90, 190, 110)]): d.rectangle((14 + k * 14, 128, 24 + k * 14, 140), fill=c, outline=INK); d.line([(15 + k * 14, 130), (23 + k * 14, 130)], fill=(255, 255, 255))
    d.rectangle((76, 132, 100, 140), fill=(40, 40, 50), outline=INK); d.ellipse((80, 134, 84, 138), fill=WHITE); d.ellipse((92, 134, 96, 138), fill=WHITE)
    d.ellipse((104, 122, 134, 140), fill=(40, 40, 46), outline=INK); d.ellipse((112, 126, 126, 136), fill=(150, 108, 72))   # old tyre
    d.rectangle((60, 236, 130, 266), fill=(150, 50, 70), outline=INK); [d.line([(62, y), (128, y)], fill=(190, 80, 100)) for y in range(240, 266, 6)]   # rug
    d.rectangle((140, 222, 176, 252), fill=(70, 66, 80), outline=INK); d.rectangle((144, 226, 172, 244), fill=(40, 38, 50)); [d.ellipse((147 + k * 8, 246, 151 + k * 8, 250), fill=(220, 220, 220)) for k in range(3)]   # second amp
    d.line([(54, 236), (100, 250), (140, 240)], fill=(30, 30, 36), width=2)                                               # cable
    im = glow(im, 75, 160, 90, (255, 200, 120), .45)
    return im
def more_studio(im):
    d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((90, 154, 188, 180), fill=(20, 16, 30))                                                                    # drop shadow of the tag (redrawn on top)
    d.rectangle((86, 150, 184, 176), fill=(255, 230, 120), outline=INK); d.polygon([(86, 150), (74, 163), (86, 176)], fill=(255, 230, 120), outline=INK)
    d.ellipse((80, 160, 85, 165), fill=(250, 250, 250), outline=INK); d.text((137, 163), "$606.17", font=F(13), fill=(170, 40, 40), anchor="mm")
    for k in range(2):                                                                                                  # VU meters
        x = 30 + k * 190; d.rectangle((x, 150, x + 30, 172), fill=(250, 240, 200), outline=INK); d.arc((x + 3, 156, x + 27, 180), 200, 340, fill=(200, 60, 60)); d.line([(x + 15, 170), (x + 22 - k * 10, 158)], fill=INK)
    for k in range(10): d.rectangle((24 + k * 22, 252, 36 + k * 22, 256), fill=[(255, 60, 90), (255, 160, 60), (255, 230, 80), (90, 230, 120), (90, 190, 255)][k % 5])   # LED strip
    plant(d, 248, 236); d.rectangle((6, 70, 40, 120), fill=(230, 90, 110), outline=INK); d.text((23, 84), "ON", font=F(10), fill=WHITE, anchor="mm"); d.text((23, 100), "AIR", font=F(10), fill=WHITE, anchor="mm")
    im = glow(im, 23, 95, 50, (255, 80, 110), .5); im = glow(im, 135, 95, 90, (120, 180, 255), .3)
    d = ImageDraw.Draw(im); d.line([(40, 250), (80, 262), (140, 252)], fill=(20, 20, 26), width=2)
    return im
def more_aberdeen(im):
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(3): x = 30 + k * 30; d.rectangle((x, 176, x + 22, 194), fill=[(200, 90, 80), (90, 140, 190), (230, 200, 120)][k], outline=INK); d.polygon([(x - 2, 176), (x + 24, 176), (x + 11, 166)], fill=(90, 60, 50), outline=INK); d.rectangle((x + 4, 182, x + 9, 188), fill=(255, 230, 140), outline=INK)   # houses
    d.rectangle((150, 150, 160, 194), fill=(150, 90, 70), outline=INK); d.rectangle((130, 172, 186, 194), fill=(120, 110, 100), outline=INK)   # sawmill + chimney smoke
    for k in range(6): r = 4 + k * 2; d.ellipse((155 - r - k * 4, 140 - k * 10 - r, 155 + r - k * 4, 140 - k * 10 + r), fill=(220, 226, 236))
    for _ in range(170): x, y = R.randint(0, W), R.randint(0, 262); d.line([(x, y), (x - 2, y + 6)], fill=(200, 220, 240))   # rain
    for x in range(0, W, 14): d.line([(x, 226 + (x // 14) % 3 * 3), (x + 7, 226 + (x // 14) % 3 * 3)], fill=(230, 246, 250))   # water glints
    d.rectangle((96, 236, 150, 250), fill=(200, 60, 50), outline=INK); d.rectangle((140, 230, 160, 250), fill=(200, 60, 50), outline=INK); d.rectangle((144, 233, 156, 240), fill=(150, 200, 230))   # log truck
    for x in (104, 128, 152): d.ellipse((x - 5, 246, x + 5, 256), fill=(30, 30, 36), outline=INK)
    for k in range(3): d.ellipse((98 + k * 12, 226, 112 + k * 12, 236), fill=(176, 120, 70), outline=INK)
    for x in (40, 230): d.ellipse((x - 5, 258, x + 5, 264), fill=(230, 60, 60), outline=INK); d.rectangle((x - 1, 262, x + 1, 266), fill=WHITE); d.point((x - 2, 260), fill=WHITE)   # mushrooms
    return im
def more_pool(im):
    for x in (70, 150, 220): im = beam(im, x, x + 30, 40, 266, 10, 40, (255, 255, 230), .18)
    d = ImageDraw.Draw(im)
    for k in range(-1, 18): x = k * 16; d.rectangle((x, 40, x + 7, 44), fill=(255, 70, 70) if k % 2 else WHITE, outline=INK)   # lane rope
    fish(d, 60, 110, (255, 160, 60)); fish(d, 220, 210, (255, 120, 190), -1); fish(d, 100, 230, (120, 230, 200))
    for _ in range(30):
        x, y, r = R.randint(10, 260), R.randint(60, 250), R.randint(1, 3); d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 245, 255), outline=(255, 255, 255))
    for k in range(6): x = 40 + k * 38; d.ellipse((x, 258, x + 7, 263), fill=(255, 214, 80), outline=INK)                 # coins on the floor
    dd = ImageDraw.Draw(im)                                                                                                # blue lane-marker stripe inlaid in the tiles
    for y in range(300, 311): dd.line([(0, y), (W, y)], fill=(70, 140, 214))
    for x in range(0, W, 10): dd.line([(x, 300), (x, 310)], fill=(110, 170, 226))
    dd.line([(0, 300), (W, 300)], fill=(110, 170, 226)); dd.line([(0, 310), (W, 310)], fill=(110, 170, 226))
    return im

# ---------------------------------------------------------------- characters (tall and slim, 100x140 cell, feet at y=138)
# skeleton (≈5.3 heads): head y10-36 (20 wide) · neck 36-43 · shoulders y44 (30 wide, rounded) · waist y84 (22 wide)
# legs y92-130 tapering 9->7 px · feet y130-138 · upper arm 22 px · forearm 20 px · elbow pixel + thumb on every hand
def limb(d, p0, p1, w0, w1, col, sh, li=None):
    """tapered limb with a shade side (right) and an optional light side (left)"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    q = [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2), (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]
    d.polygon(q, fill=col)
    d.polygon([q[2], q[3], ((q[3][0] * 2 + q[0][0]) / 3, (q[3][1] * 2 + q[0][1]) / 3), ((q[2][0] * 2 + q[1][0]) / 3, (q[2][1] * 2 + q[1][1]) / 3)], fill=sh)
    if li: d.line([((q[0][0] * 3 + q[3][0]) / 4, (q[0][1] * 3 + q[3][1]) / 4), ((q[1][0] * 3 + q[2][0]) / 4, (q[1][1] * 3 + q[2][1]) / 4)], fill=li)
    d.ellipse((p1[0] - w1 / 2, p1[1] - w1 / 2, p1[0] + w1 / 2, p1[1] + w1 / 2), fill=col)
def hand(d, c, col, sh, fist=False, flip=1):
    x, y = c
    if fist:
        d.rounded_rectangle((x - 4, y - 4, x + 4, y + 4), 2, fill=col); d.line([(x - 3, y - 1), (x + 3, y - 1)], fill=sh); d.line([(x - 3, y + 2), (x + 3, y + 2)], fill=sh)
        tx = x + 4 if flip > 0 else x - 5; d.rectangle((tx, y - 3, tx + 1, y + 1), fill=col)      # thumb
    else:
        d.ellipse((x - 3, y - 3, x + 3, y + 4), fill=col); d.line([(x - 2, y + 3), (x + 2, y + 3)], fill=sh); d.point((x - 3 * flip, y - 2), fill=col); d.point((x - 4 * flip, y - 2), fill=col)
def shoe(d, x, y, col, toe, sole, flip=1):
    d.rounded_rectangle((x - 5, y, x + 7, y + 7), 3, fill=col); d.rectangle((x + (2 if flip > 0 else -5), y + 3, x + (7 if flip > 0 else 0), y + 6), fill=toe)
    d.rectangle((x - 5, y + 6, x + 7, y + 7), fill=sole)
def texture(im, box, cols, n):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = R.randint(x0, x1), R.randint(y0, y1)
        if 0 <= x < im.width and 0 <= y < im.height and im.getpixel((x, y))[3] > 0: d.point((x, y), fill=R.choice(cols))

def kurt(frame=0):
    """grunge singer-guitarist (original design, slim): shaggy blond hair to the jaw, white oval sunglasses, fuzzy olive cardigan,
    red/white striped tee, ripped light jeans, black sneakers, LEFT-HANDED sunburst offset guitar (right hand frets the neck)."""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK, SKS, SKL = (240, 200, 172), (206, 158, 130), (252, 222, 196); HAIR, HAIRS, HAIRL, HAIRD = (232, 196, 104), (190, 148, 66), (252, 232, 160), (150, 110, 46)
    CARD, CARDS, CARDL = (128, 136, 74), (92, 98, 52), (164, 172, 100); JE, JS, JL = (120, 156, 206), (86, 114, 164), (166, 196, 232)
    bob = [0, 1, 0, -1][frame]; st = [0, 6, 11, 6][frame]
    for side, x0 in ((-1, 44), (1, 56)):                                                      # legs: tapered, slight gap
        limb(d, (x0, 92), (x0 + side, 130), 10, 7, JE, JS, JL)
        d.rectangle((x0 - 3 + side, 108, x0 + 2 + side, 111), fill=SK); d.line([(x0 - 4 + side, 107), (x0 + 3 + side, 107)], fill=(244, 246, 252)); d.line([(x0 - 4 + side, 112), (x0 + 3 + side, 112)], fill=(244, 246, 252))
        shoe(d, x0 + side * 2 - 1, 130, (40, 36, 46), (236, 232, 222), (236, 232, 222), side)
    d.polygon([(40, 84), (60, 84), (62, 94), (38, 94)], fill=JE); d.line([(50, 86), (50, 94)], fill=JS)          # hips
    d.polygon([(41, 46 + bob), (59, 46 + bob), (60, 86), (40, 86)], fill=(240, 238, 242))                         # striped tee
    for y in range(50, 86, 5): d.line([(41, y + bob // 2), (59, y + bob // 2)], fill=(176, 40, 56), width=2)
    d.polygon([(35, 46 + bob), (43, 46 + bob), (44, 90), (34, 90)], fill=CARD); d.polygon([(57, 46 + bob), (65, 46 + bob), (66, 90), (56, 90)], fill=CARD)    # open cardigan
    d.line([(36, 50 + bob), (35, 88)], fill=CARDL); d.line([(64, 50 + bob), (65, 88)], fill=CARDS, width=2); d.rectangle((34, 86, 44, 90), fill=CARDS); d.rectangle((56, 86, 66, 90), fill=CARDS)
    for y in range(58, 86, 8): d.ellipse((42, y, 44, y + 2), fill=(70, 54, 40))
    texture(im, (34, 46, 66, 90), [CARDL, CARDS], 60)
    gx, gy = 58, 86                                                                           # guitar: neck to viewer's left (lefty)
    hx, hy = 8, 62
    d.polygon([(hx, hy - 3), (gx - 6, gy - 5), (gx - 4, gy), (hx + 2, hy + 2)], fill=(146, 98, 56)); d.line([(hx + 2, hy), (gx - 6, gy - 2)], fill=(206, 160, 104))
    for k in range(1, 9): fx = hx + k * (gx - 6 - hx) / 9; fy = hy + k * (gy - 4 - hy) / 9; d.point((fx, fy - 1), fill=(230, 220, 200))
    d.polygon([(hx - 6, hy - 6), (hx + 2, hy - 4), (hx + 2, hy + 3), (hx - 6, hy + 1)], fill=(60, 40, 30)); [d.point((hx - 4 + k * 2, hy - 5 + (k % 2)), fill=(220, 220, 230)) for k in range(4)]
    body = [(gx - 8, gy - 10), (gx + 6, gy - 13), (gx + 18, gy - 6), (gx + 20, gy + 6), (gx + 10, gy + 14), (gx - 6, gy + 13), (gx - 12, gy + 4)]
    d.polygon(body, fill=(214, 86, 34)); d.polygon([(gx - 4, gy - 6), (gx + 8, gy - 8), (gx + 14, gy), (gx + 10, gy + 8), (gx - 2, gy + 8), (gx - 6, gy + 2)], fill=(250, 170, 60))   # sunburst
    d.ellipse((gx - 1, gy - 3, gx + 7, gy + 4), fill=(255, 214, 110)); d.polygon([(gx - 10, gy + 2), (gx + 2, gy + 10), (gx - 4, gy + 12)], fill=(250, 246, 236))       # pickguard
    d.rectangle((gx + 2, gy - 3, gx + 12, gy - 1), fill=(40, 36, 40)); d.rectangle((gx + 4, gy + 3, gx + 14, gy + 5), fill=(40, 36, 40)); d.line([(gx - 6, gy - 2), (gx + 16, gy + 2)], fill=(232, 232, 240))
    for k in range(3): d.ellipse((gx + 12 + k * 3, gy + 6 + k * 2, gx + 14 + k * 3, gy + 8 + k * 2), fill=(250, 246, 236))
    sx, sy = 36, 48 + bob                                                                      # his right arm: elbow out, hand on the neck
    limb(d, (sx, sy), (26, 64), 8, 7, CARD, CARDS, CARDL); limb(d, (26, 64), (18, 64), 7, 6, CARD, CARDS); d.rectangle((19, 60, 22, 67), fill=CARDS)
    hand(d, (16, 63), SK, SKS, flip=-1)
    ex, ey = 68, 66 + bob                                                                      # his left arm strums over the body
    limb(d, (64, 48 + bob), (ex, ey), 8, 7, CARD, CARDS, CARDL); limb(d, (ex, ey), (60 + st // 3, 82 + st // 2), 7, 6, CARD, CARDS); hand(d, (59 + st // 3, 86 + st // 2), SK, SKS)
    d.rectangle((46, 36 + bob, 54, 46 + bob), fill=SKS); d.line([(46, 44 + bob), (54, 44 + bob)], fill=(196, 146, 118))           # neck
    d.ellipse((40, 12 + bob, 60, 40 + bob), fill=SK); d.ellipse((52, 16 + bob, 61, 38 + bob), fill=SKS); d.ellipse((42, 26 + bob, 47, 32 + bob), fill=SKL)   # face
    d.ellipse((38, 24 + bob, 42, 32 + bob), fill=SK); d.ellipse((58, 24 + bob, 62, 32 + bob), fill=SKS)
    for cx in (45, 55):                                                                        # white oval sunglasses with dark lenses
        d.ellipse((cx - 5, 22 + bob, cx + 5, 29 + bob), fill=(250, 250, 250)); d.ellipse((cx - 3, 23 + bob, cx + 3, 28 + bob), fill=(28, 26, 44)); d.point((cx - 2, 24 + bob), fill=(170, 180, 255))
    d.line([(50, 25 + bob), (50, 25 + bob)], fill=(250, 250, 250)); d.rectangle((49, 29 + bob, 51, 32 + bob), fill=SKS)
    d.line([(46, 34 + bob), (54, 34 + bob)], fill=(176, 100, 96)); [d.point((44 + k * 2, 36 + bob + (k % 2)), fill=(196, 160, 100)) for k in range(7)]           # mouth + stubble
    d.ellipse((36, 4 + bob, 64, 26 + bob), fill=HAIR)                                          # shaggy hair, centre part, falls to the jaw
    d.polygon([(36, 16 + bob), (42, 14 + bob), (43, 42 + bob), (40, 44 + bob), (35, 38 + bob)], fill=HAIR); d.polygon([(64, 16 + bob), (58, 14 + bob), (58, 42 + bob), (61, 44 + bob), (65, 38 + bob)], fill=HAIRS)
    d.polygon([(42, 8 + bob), (49, 7 + bob), (47, 21 + bob), (42, 19 + bob)], fill=HAIR); d.polygon([(51, 7 + bob), (59, 10 + bob), (58, 21 + bob), (53, 19 + bob)], fill=HAIRS)
    d.line([(50, 6 + bob), (50, 12 + bob)], fill=HAIRD)
    for (x0, y0, x1, y1, c) in ((39, 9, 46, 6, HAIRL), (37, 18, 38, 34, HAIRL), (44, 10, 45, 18, HAIRL), (60, 18, 61, 36, HAIRD), (55, 10, 56, 18, HAIRD)): d.line([(x0, y0 + bob), (x1, y1 + bob)], fill=c)
    for (x0, y0) in ((36, 38), (39, 42), (62, 40), (59, 42), (42, 20), (57, 20)): d.line([(x0, y0 + bob), (x0 + R.choice((-1, 1)), y0 + 4 + bob)], fill=HAIRS)
    return outline(im)

def freddie(frame=0):
    """Live Aid 1985 look (original design, slim): short black hair, thick moustache, white ribbed tank top, light-wash jeans,
    studded armband on the right bicep, belt with buckle, white high-tops, half mic stand. 0 idle · 1 fist up · 2 lunge · 3 fist up (sing)."""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK, SKS, SKL = (200, 150, 112), (164, 116, 84), (224, 178, 140); T, TS, TL = (250, 250, 252), (206, 212, 226), (255, 255, 255)
    JE, JS, JL = (156, 192, 226), (118, 152, 194), (196, 222, 244)
    up = frame in (1, 3); lunge = frame == 2; dy = 2 if lunge else 0
    for side, x0 in ((-1, 44), (1, 56)):
        foot = x0 + (side * 7 if lunge else side)
        limb(d, (x0, 92 + dy), ((x0 + foot) / 2, 112), 10, 9, JE, JS, JL); limb(d, ((x0 + foot) / 2, 112), (foot, 130), 9, 7, JE, JS, JL)
        d.point(((x0 + foot) / 2 - 2, 114), fill=JL); d.point(((x0 + foot) / 2 + 1, 118), fill=JL)
        d.rounded_rectangle((foot - 5, 126, foot + 6, 132), 2, fill=T); shoe(d, foot, 131, (248, 248, 250), (220, 224, 236), (176, 180, 196), side)
        d.line([(foot - 3, 128), (foot + 3, 128)], fill=(40, 60, 140)); d.line([(foot - 3, 130), (foot + 3, 130)], fill=(40, 60, 140))
    d.polygon([(40, 84 + dy), (60, 84 + dy), (62, 94 + dy), (38, 94 + dy)], fill=JE)
    d.rectangle((39, 84 + dy, 61, 88 + dy), fill=(80, 56, 40)); d.rectangle((47, 83 + dy, 53, 89 + dy), fill=(236, 210, 120)); d.rectangle((49, 85 + dy, 51, 87 + dy), fill=(170, 130, 60))
    d.polygon([(40, 46 + dy), (60, 46 + dy), (61, 85 + dy), (39, 85 + dy)], fill=T); d.polygon([(55, 48 + dy), (60, 46 + dy), (61, 85 + dy), (56, 85 + dy)], fill=TS)   # tank top
    for y in range(52, 84, 3): d.line([(41, y + dy), (54, y + dy)], fill=(240, 242, 248))
    d.polygon([(42, 44 + dy), (46, 44 + dy), (50, 56 + dy), (54, 44 + dy), (58, 44 + dy), (56, 40 + dy), (44, 40 + dy)], fill=SK); d.line([(48, 46 + dy), (50, 52 + dy)], fill=SKS)   # neckline + chest
    d.ellipse((34, 42 + dy, 44, 52 + dy), fill=SK); d.ellipse((56, 42 + dy, 66, 52 + dy), fill=SKS)                      # rounded shoulders
    limb(d, (38, 48 + dy), (32, 68 + dy), 9, 8, SK, SKS, SKL); limb(d, (32, 68 + dy), (28, 86 + dy), 8, 6, SK, SKS, SKL)  # his right arm holds the half stand
    d.rectangle((30, 57 + dy, 38, 61 + dy), fill=(26, 24, 30)); [d.point((31 + k * 2, 59 + dy), fill=(230, 230, 240)) for k in range(4)]
    d.line([(28, 90 + dy), (20, 60 + dy)], fill=(196, 196, 206), width=3); d.line([(27, 90 + dy), (19, 60 + dy)], fill=(240, 240, 248))
    d.ellipse((15, 52 + dy, 23, 61 + dy), fill=(70, 70, 82)); [d.point((17 + k * 2, 55 + dy + (k % 2)), fill=(150, 150, 164)) for k in range(3)]
    hand(d, (28, 88 + dy), SK, SKS, fist=True, flip=-1)
    if up:                                                                                     # left fist in the air (elbow bent)
        limb(d, (62, 48), (72, 32), 9, 8, SK, SKS, SKL); limb(d, (72, 32), (74, 14), 8, 7, SK, SKS, SKL); hand(d, (74, 10), SK, SKS, fist=True)
    else:
        limb(d, (62, 48 + dy), (68, 68 + dy), 9, 8, SK, SKS, SKL); limb(d, (68, 68 + dy), (70, 86 + dy), 8, 6, SK, SKS, SKL); hand(d, (70, 89 + dy), SK, SKS)
    d.rectangle((46, 34 + dy, 54, 44 + dy), fill=SKS)                                                                         # neck
    d.ellipse((40, 12 + dy, 60, 40 + dy), fill=SK); d.ellipse((52, 16 + dy, 61, 38 + dy), fill=SKS); d.ellipse((42, 24 + dy, 47, 32 + dy), fill=SKL)
    d.ellipse((38, 22 + dy, 42, 30 + dy), fill=SK); d.ellipse((58, 22 + dy, 62, 30 + dy), fill=SKS)
    d.ellipse((39, 6 + dy, 61, 22 + dy), fill=(26, 20, 26)); d.rectangle((39, 14 + dy, 42, 26 + dy), fill=(26, 20, 26)); d.rectangle((58, 14 + dy, 61, 24 + dy), fill=(26, 20, 26))   # short hair
    d.line([(44, 9 + dy), (52, 8 + dy)], fill=(80, 74, 96)); d.point((56, 11 + dy), fill=(80, 74, 96))
    for ex in (43, 52):
        d.rectangle((ex, 24 + dy, ex + 4, 26 + dy), fill=(244, 240, 234)); d.rectangle((ex + 2, 24 + dy, ex + 3, 26 + dy), fill=(40, 26, 20)); d.line([(ex - 1, 22 + dy), (ex + 5, 21 + dy)], fill=(26, 20, 26), width=2)
    d.rectangle((49, 27 + dy, 51, 31 + dy), fill=SKS)
    d.rectangle((44, 32 + dy, 56, 34 + dy), fill=(26, 20, 26)); d.point((44, 35 + dy), fill=(26, 20, 26)); d.point((56, 35 + dy), fill=(26, 20, 26))     # moustache
    if up or lunge: d.rectangle((46, 35 + dy, 54, 38 + dy), fill=(110, 40, 46)); d.line([(46, 35 + dy), (54, 35 + dy)], fill=(250, 248, 240))
    else: d.line([(46, 36 + dy), (54, 36 + dy)], fill=(140, 76, 70))
    return outline(im)

# ---------------------------------------------------------------- tiles + UI parts
def tiles_ui():
    im = Image.new("RGBA", (256, 168), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"; items = []
    def lab(x, y, t): items.append((x, y, t))
    tile_grass(4, 4, d); tile_grass(20, 4, d); tile_grass(4, 20, d, top=False); tile_grass(20, 20, d, top=False); lab(4, 38, "hierba")
    masonry(d, 44, 4, 75, 35, seed=7); d.rectangle((44, 4, 75, 35), outline=INK); lab(44, 38, "piedra")
    tile_metal(84, 4, d); tile_metal(100, 4, d); lab(84, 38, "metal")
    tile_wood(84, 22, d, 32); lab(84, 32, "")
    pool_tiles(d, 124, 4, 155, 35); d.rectangle((124, 4, 155, 35), outline=INK); lab(124, 38, "azulejo")
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
    bgs = [("HOOK (noche estrellada)", more_hook(bg_hook())), ("AYER: QUEEN · Live Aid 1985", more_wembley(bg_wembley())), ("PISTA 1 · los nombres de antes", more_garage(bg_garage())),
           ("PISTA 2 · el álbum de $606.17", more_studio(bg_studio())), ("PISTA 3 · 1987, pueblo maderero", more_aberdeen(bg_aberdeen())), ("PISTA 4 · la portada (anzuelo)", more_pool(bg_pool()))]
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

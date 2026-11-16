"""Parte 14 (Michael Jackson) — original GBA-style PROCEDURAL backgrounds (same engine as Parte 12) + mystery dancer sprite.
No names/logos/faces: the dancer is a generic silhouette character (fedora, jacket, one white glove).
usage: python3 gba_p14.py -> sprites/parte14/fondo_0..6.png, artista_0..5.png + preview sheets
fondos: 0 hook · 1 Gary (clue 1) · 2 Grammys (clue 2) · 3 Motown 25 (clue 3) · 4 crown/fedora/glove (clue 4) · 5 outro night · 6 recap Beatles (Abbey-Road crossing)"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw
from gba_sprites import (W, H, F, INK, WHITE, grad, outline, silhouette, cloud, masonry, ground, side_walls, star, glow, beam, noise,
                         string_lights, plant, limb, hand, shoe, texture, label, mountains, pine)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte14")
R = random.Random(14)
GOLD, GOLD_S, GOLD_L = (250, 200, 60), (190, 120, 30), (255, 244, 170)

def canvas(stops, h=266, base=(20, 14, 30)):
    im = Image.new("RGB", (W, H), base); im.paste(grad(W, h, stops).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"; return im, d
def fog(im, y, h, col, a, seed=1):
    """soft low fog bank: translucent ellipses"""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov); r = random.Random(seed)
    for k in range(18): x = r.randint(-20, W); w = r.randint(50, 110); od.ellipse((x, y + r.randint(0, h // 2), x + w, y + h), fill=col + (a,))
    im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")); return ImageDraw.Draw(im)
def twinkles(d, box, n, cols=((255, 255, 255), (255, 230, 150), (170, 220, 255))):
    for _ in range(n): d.point((R.randint(box[0], box[2]), R.randint(box[1], box[3])), fill=R.choice(cols))
def trophy(d, x, y):
    d.rectangle((x - 7, y + 14, x + 7, y + 18), fill=GOLD_S, outline=INK); d.rectangle((x - 5, y + 14, x + 5, y + 15), fill=GOLD_L)
    d.rectangle((x - 1, y + 5, x + 1, y + 14), fill=GOLD)
    d.ellipse((x - 8, y + 2, x + 6, y + 8), fill=GOLD, outline=INK)
    d.polygon([(x - 1, y + 4), (x + 10, y - 10), (x + 15, y - 5), (x + 5, y + 6)], fill=GOLD, outline=INK); d.line([(x + 1, y + 2), (x + 10, y - 8)], fill=GOLD_L)
    d.line([(x + 6, y - 3), (x + 13, y - 6)], fill=GOLD_S); d.line([(x - 6, y + 4), (x - 10, y - 2)], fill=(210, 210, 220), width=1)
def glove(d, x, y, s=1.0):
    W_, WS = (250, 250, 255), (176, 184, 214)
    d.rectangle((x - 7, y, x + 7, y + 13), fill=W_, outline=INK); d.rectangle((x + 3, y + 1, x + 7, y + 12), fill=WS)
    for k, (fx, fh) in enumerate(((-7, 10), (-3, 13), (1, 13), (5, 10))): d.rectangle((x + fx, y - fh, x + fx + 3, y + 1), fill=W_, outline=INK)
    d.polygon([(x - 8, y + 4), (x - 15, y - 2), (x - 12, y - 5), (x - 6, y + 1)], fill=W_, outline=INK); d.rectangle((x - 8, y + 12, x + 8, y + 17), fill=(170, 176, 200), outline=INK)
    for _ in range(12): d.point((x + R.randint(-6, 6), y + R.randint(-10, 12)), fill=R.choice([(120, 220, 255), (255, 200, 250), (255, 255, 160)]))
def fedora(d, x, y):
    d.ellipse((x - 17, y + 6, x + 17, y + 15), fill=(24, 22, 30), outline=INK); d.line([(x - 12, y + 8), (x + 8, y + 8)], fill=(80, 80, 104))
    d.polygon([(x - 9, y + 10), (x - 8, y - 6), (x - 3, y - 9), (x + 3, y - 9), (x + 8, y - 6), (x + 9, y + 10)], fill=(30, 28, 38), outline=INK)
    d.rectangle((x - 9, y + 3, x + 9, y + 7), fill=(230, 230, 240), outline=INK); d.line([(x - 3, y - 8), (x - 3, y - 2)], fill=(56, 54, 70))
def crown(d, x, y):
    d.polygon([(x - 16, y + 14), (x - 18, y - 6), (x - 9, y + 4), (x - 5, y - 10), (x, y + 2), (x + 5, y - 10), (x + 9, y + 4), (x + 18, y - 6), (x + 16, y + 14)], fill=GOLD, outline=INK)
    d.rectangle((x - 16, y + 9, x + 16, y + 15), fill=GOLD_S, outline=INK); d.line([(x - 14, y + 10), (x + 14, y + 10)], fill=GOLD_L)
    for (gx, c) in ((-10, (230, 50, 80)), (0, (60, 190, 255)), (10, (80, 230, 130))): d.ellipse((gx + x - 3, y + 10, gx + x + 3, y + 15), fill=c, outline=INK)
    for gx in (-18, -5, 5, 18): d.ellipse((x + gx - 2, y - 12 if abs(gx) == 5 else y - 8, x + gx + 2, y - 8 if abs(gx) == 5 else y - 4), fill=(255, 255, 255), outline=INK)

# ------------------------------------------------------------------ 0 HOOK: dark theatre stage, spotlights, glowing dance floor, mirror ball
def bg_hook():
    im, d = canvas([(6, 4, 22), (26, 12, 54), (52, 22, 84)])
    for k in range(0, W, 12): d.rectangle((k, 0, k + 11, 250), fill=(36, 16, 60) if (k // 12) % 2 else (26, 12, 46))
    for k in range(0, W, 12): d.line([(k + 5, 0), (k + 5, 250)], fill=(58, 28, 90))
    d.rectangle((6, 12, 264, 22), fill=(70, 70, 92), outline=INK)
    for x in range(26, 264, 38): d.rectangle((x - 7, 22, x + 7, 34), fill=(40, 40, 54), outline=INK); d.ellipse((x - 5, 31, x + 5, 38), fill=(255, 244, 210), outline=INK)
    for (x, c) in ((26, (255, 110, 190)), (102, (255, 244, 210)), (140, (255, 244, 210)), (216, (110, 200, 255))): im = beam(im, x, 135 + (x - 135) // 3, 36, 266, 6, 90, c, .26)
    im = glow(im, 135, 250, 140, (255, 220, 160), .35); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.line([(135, 0), (135, 60)], fill=(150, 150, 170)); d.ellipse((119, 60, 151, 92), fill=(190, 196, 214), outline=INK)                    # mirror ball
    for a in range(0, 360, 30):
        for r_ in (6, 12): d.rectangle((135 + r_ * math.cos(math.radians(a)) - 2, 76 + r_ * .8 * math.sin(math.radians(a)) - 2, 135 + r_ * math.cos(math.radians(a)) + 2, 76 + r_ * .8 * math.sin(math.radians(a)) + 2), fill=R.choice([(255, 255, 255), (150, 210, 255), (255, 170, 230)]))
    for (x, y, c) in ((34, 120, (255, 90, 190)), (236, 130, (90, 230, 255))): star(d, x, y, 14, c, (120, 40, 130)); star(d, x, y, 9, WHITE, c)    # neon stars
    twinkles(d, (0, 0, W, 240), 90)
    d.rectangle((0, 236, W, 266), fill=(28, 16, 48)); d.line([(0, 236), (W, 236)], fill=(120, 80, 190))
    for x in range(0, W, 30): d.rectangle((x + 4, 236, x + 18, 244), fill=(54, 30, 86), outline=INK)                              # stage edge speakers
    for y in range(266, H, 16):                                                                                                    # dance floor: dark glass tiles, some lit
        for x in range(0, W, 18):
            lit = R.random() < .16; c = R.choice([(255, 80, 190), (90, 230, 255), (255, 230, 90), (130, 255, 150)]) if lit else (22 + (y // 16) % 2 * 6, 16, 40)
            d.rectangle((x, y, x + 17, y + 15), fill=c, outline=(60, 40, 110)); d.line([(x + 1, y + 1), (x + 6, y + 1)], fill=(255, 255, 255) if lit else (70, 56, 120))
    d.line([(0, 265), (W, 265)], fill=INK); fog(im, 226, 50, (200, 180, 255), 38, 3)
    return im

# ------------------------------------------------------------------ 1 CLUE 1: Gary, Indiana steel town at dusk, "#1" billboard, old radio
def bg_gary():
    im, d = canvas([(40, 30, 86), (150, 64, 98), (248, 142, 84), (255, 214, 130)])
    for k in range(5): cloud(d, -20 + k * 62, 30 + (k % 3) * 28, 56, (214, 110, 130), (160, 72, 110), (255, 186, 160))
    im = glow(im, 60, 230, 150, (255, 160, 70), .5); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((0, 150, W, 236), fill=(66, 40, 80))                                                                              # mill: far plant
    for (x, w, h, c) in ((10, 26, 110, (92, 56, 90)), (44, 18, 70, (80, 48, 84)), (150, 30, 96, (92, 56, 90)), (192, 20, 130, (84, 50, 86))):   # smokestacks
        d.rectangle((x, 236 - h, x + w, 236), fill=c, outline=INK)
        for y in range(236 - h, 232, 12): d.rectangle((x, y, x + w, y + 4), fill=(210, 60, 60) if (y // 12) % 2 else (240, 236, 230))
        d.rectangle((x - 3, 236 - h - 4, x + w + 3, 236 - h), fill=(70, 44, 70), outline=INK)
    for (x, h) in ((14, 110), (196, 130), (154, 96)):                                                                                  # smoke plumes
        for k in range(7): r_ = 5 + k * 3; d.ellipse((x + 8 + k * 6 - r_, 236 - h - 12 - k * 12 - r_, x + 8 + k * 6 + r_, 236 - h - 12 - k * 12 + r_), fill=(150 + k * 6, 110 + k * 6, 140 + k * 4))
    for x in range(70, 150, 20): d.rectangle((x, 176, x + 14, 236), fill=(80, 46, 80), outline=INK); d.rectangle((x + 3, 186, x + 11, 200), fill=(255, 150, 60)); d.rectangle((x + 5, 188, x + 9, 198), fill=(255, 230, 130))   # furnaces
    d.line([(60, 190), (240, 150)], fill=(60, 36, 64), width=3); d.line([(60, 200), (240, 164)], fill=(60, 36, 64), width=2)
    d.rectangle((0, 206, W, 236), fill=(86, 50, 76))
    for k in range(5):                                                                                                                 # row houses
        x = 8 + k * 52; c = [(214, 120, 100), (120, 160, 210), (236, 206, 130), (140, 190, 140), (196, 130, 190)][k]
        d.rectangle((x, 188, x + 44, 236), fill=c, outline=INK); d.polygon([(x - 3, 188), (x + 47, 188), (x + 22, 168)], fill=(110, 56, 60), outline=INK)
        d.rectangle((x + 6, 200, x + 16, 214), fill=(255, 226, 140), outline=INK); d.rectangle((x + 28, 200, x + 38, 214), fill=(255, 226, 140) if k % 2 else (60, 50, 90), outline=INK)
        d.rectangle((x + 17, 216, x + 27, 236), fill=(100, 60, 50), outline=INK); d.rectangle((x - 2, 230, x + 46, 236), fill=(170, 160, 150), outline=INK)
    d.rectangle((96, 100, 176, 150), fill=(250, 244, 220), outline=INK, width=2); d.line([(110, 150), (110, 188)], fill=(80, 60, 50), width=3); d.line([(162, 150), (162, 188)], fill=(80, 60, 50), width=3)   # billboard
    d.rectangle((100, 104, 172, 146), outline=(210, 60, 60), width=2); d.text((136, 124), "N°1", font=F(26), fill=(210, 50, 60), anchor="mm", stroke_width=1, stroke_fill=INK)
    for k in range(9): d.ellipse((98 + k * 9, 96, 102 + k * 9, 100), fill=(255, 240, 160), outline=INK)
    d.rectangle((0, 236, W, 266), fill=(120, 92, 96)); d.line([(0, 236), (W, 236)], fill=INK)
    for x in range(0, W, 24): d.rectangle((x + 4, 250, x + 18, 252), fill=(220, 200, 120))                                         # road dashes
    d.rectangle((206, 214, 246, 236), fill=(146, 86, 56), outline=INK); d.rectangle((210, 218, 242, 232), fill=(210, 150, 100), outline=INK)   # old radio on the stoop
    d.ellipse((214, 221, 228, 231), fill=(60, 40, 40), outline=INK); [d.line([(214, y), (228, y)], fill=(90, 70, 70)) for y in range(223, 231, 2)]
    d.ellipse((233, 222, 239, 228), fill=(240, 220, 160), outline=INK); d.line([(240, 214), (252, 192)], fill=(210, 210, 220))
    for (x, y) in ((250, 186), (258, 176)): d.text((x, y), "♪", font=F(11), fill=(255, 240, 160), anchor="mm")
    for x in (24, 112, 200):
        d.line([(x, 266), (x, 196)], fill=(60, 44, 56), width=2); d.rectangle((x - 5, 192, x + 5, 198), fill=(255, 220, 130), outline=INK)
    masonry(d, 0, 266, W, H, base=(112, 82, 88), sh=(80, 56, 66), li=(158, 122, 120), mortar=(50, 34, 48), seed=61); d.line([(0, 265), (W, 265)], fill=INK)
    for (px, py, pw) in ((20, 292, 44), (160, 310, 56), (90, 336, 36)): d.ellipse((px, py, px + pw, py + 8), fill=(180, 110, 100), outline=(110, 60, 70)); d.line([(px + 6, py + 3), (px + pw - 6, py + 3)], fill=(255, 210, 150))
    return im

# ------------------------------------------------------------------ 2 CLUE 2: Grammys — 8 golden gramophones, big glowing "8"
def bg_grammy():
    im, d = canvas([(24, 12, 44), (60, 24, 76), (96, 34, 90)])
    for y in range(0, 266, 10):
        for x in range(-((y // 10) % 2) * 10, W, 20): d.rectangle((x, y, x + 18, y + 8), fill=(50 + (x + y) % 9, 26, 70), outline=(36, 18, 54))
    for x0 in (0, 232):
        for k in range(0, 38, 6): d.rectangle((x0 + k, 0, x0 + k + 5, 266), fill=(150, 24, 48) if (k // 6) % 2 else (110, 16, 36))
        d.line([(x0 + (37 if x0 == 0 else 0), 0), (x0 + (37 if x0 == 0 else 0), 266)], fill=INK)
    for x in range(0, W, 18): d.pieslice((x, -8, x + 18, 22), 0, 180, fill=(170, 34, 58), outline=INK)
    for x in (46, 224): d.line([(x, 20), (x, 40)], fill=GOLD_S, width=2); d.ellipse((x - 4, 36, x + 4, 46), fill=GOLD, outline=INK)
    d.rectangle((62, 54, 208, 150), fill=(14, 8, 30), outline=GOLD, width=3)
    for k in range(26): d.ellipse((60 + k * 5.7, 51, 64 + k * 5.7, 55), fill=(255, 240, 170), outline=INK); d.ellipse((60 + k * 5.7, 148, 64 + k * 5.7, 152), fill=(255, 240, 170), outline=INK)
    d.text((137, 104), "8", font=F(70), fill=GOLD, anchor="mm", stroke_width=3, stroke_fill=GOLD_S)
    d.text((135, 102), "8", font=F(70), fill=GOLD_L, anchor="mm")
    for (x, c) in ((48, (255, 230, 170)), (222, (255, 230, 170)), (135, (255, 200, 240))): im = beam(im, x, 135, 30, 190, 8, 70, c, .2)
    im = glow(im, 135, 100, 120, (255, 190, 60), .28); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((24, 188, 246, 200), fill=(110, 60, 30), outline=INK); d.line([(26, 190), (244, 190)], fill=(214, 150, 90)); d.rectangle((30, 200, 240, 236), fill=(80, 40, 28), outline=INK)
    for x in range(44, 240, 40): d.rectangle((x - 8, 206, x + 8, 230), fill=(100, 52, 36), outline=(60, 30, 22)); d.ellipse((x - 2, 214, x + 2, 218), fill=GOLD)
    for k in range(8): trophy(d, 38 + k * 28, 166)
    for _ in range(90): x, y = R.randint(0, W), R.randint(0, 260); d.rectangle((x, y, x + 1, y + 2), fill=R.choice([GOLD, (255, 90, 150), (120, 220, 255), (255, 255, 255)]))   # confetti
    twinkles(d, (60, 40, 210, 160), 30)
    d.rectangle((0, 236, W, 266), fill=(120, 20, 40))
    for y in range(238, 266, 4): d.line([(0, y), (W, y)], fill=(138, 28, 50) if (y // 4) % 2 else (104, 14, 34))
    d.line([(0, 236), (W, 236)], fill=INK)
    for y in range(266, H, 14):
        for x in range(0, W, 14): d.rectangle((x, y, x + 13, y + 13), fill=(138 + (x + y) % 5 * 3, 22, 44), outline=(104, 14, 34))                      # red carpet
    for x in (6, 256): d.rectangle((x - 2, 276, x + 2, 330), fill=GOLD_S, outline=INK); d.ellipse((x - 6, 268, x + 6, 280), fill=GOLD, outline=INK)
    d.line([(8, 286), (60, 300)], fill=(190, 30, 60), width=3); d.line([(262, 286), (210, 300)], fill=(190, 30, 60), width=3)
    d.line([(0, 265), (W, 265)], fill=INK)
    return im

# ------------------------------------------------------------------ 3 CLUE 3: TV studio — Motown 25 (1983): big "25" marquee, ON AIR, cameras, glossy checker floor
def bg_motown():
    im, d = canvas([(8, 8, 28), (22, 18, 56), (44, 30, 86)])
    twinkles(d, (0, 0, W, 230), 220)
    for k in range(5): d.line([(20 + k * 56, 0), (60 + k * 40, 236)], fill=(34, 28, 74))
    d.rectangle((52, 44, 218, 160), fill=(20, 12, 40), outline=INK)
    for k in range(18): d.ellipse((54 + k * 9, 46, 59 + k * 9, 51), fill=(255, 220, 120) if k % 2 else (255, 120, 190), outline=INK); d.ellipse((54 + k * 9, 153, 59 + k * 9, 158), fill=(255, 220, 120) if k % 2 else (255, 120, 190), outline=INK)
    for k in range(7): d.ellipse((50, 54 + k * 15, 55, 59 + k * 15), fill=(255, 220, 120) if k % 2 else (255, 120, 190), outline=INK); d.ellipse((215, 54 + k * 15, 220, 59 + k * 15), fill=(255, 220, 120) if k % 2 else (255, 120, 190), outline=INK)
    d.text((137, 102), "25", font=F(66), fill=(255, 90, 170), anchor="mm", stroke_width=3, stroke_fill=(130, 30, 100)); d.text((135, 100), "25", font=F(66), fill=(255, 220, 240), anchor="mm")
    d.rectangle((8, 70, 44, 108), fill=(220, 40, 70), outline=INK); d.text((26, 84), "ON", font=F(11), fill=WHITE, anchor="mm"); d.text((26, 99), "AIR", font=F(11), fill=WHITE, anchor="mm")
    im = glow(im, 26, 90, 60, (255, 60, 90), .5); im = glow(im, 135, 100, 120, (255, 90, 200), .25)
    for (x, c) in ((20, (255, 230, 170)), (250, (170, 220, 255)), (135, (255, 255, 255))): im = beam(im, x, 135 + (x - 135) // 2, 10, 250, 6, 80, c, .22)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((6, 176, 264, 190), fill=(46, 40, 80), outline=INK); d.rectangle((6, 190, 264, 236), fill=(30, 24, 56), outline=INK)                                # raised stage
    for x in range(6, 264, 22): d.line([(x, 190), (x, 236)], fill=(50, 42, 90)); d.rectangle((x + 2, 196, x + 18, 200), fill=(120, 90, 190))
    for x in (24, 226):                                                                                                                                         # TV cameras on tripods
        d.polygon([(x - 14, 232), (x - 2, 200), (x + 2, 200), (x + 14, 232)], fill=(70, 70, 82)); d.line([(x, 200), (x, 236)], fill=(110, 110, 124), width=2)
        d.rectangle((x - 16, 176, x + 16, 198), fill=(200, 200, 212), outline=INK); d.rectangle((x - 12, 180, x + 8, 194), fill=(150, 150, 164)); d.ellipse((x + 6, 180, x + 22, 196), fill=(40, 44, 70), outline=INK); d.ellipse((x + 10, 184, x + 18, 192), fill=(110, 170, 240))
        d.rectangle((x - 10, 168, x + 8, 176), fill=(90, 90, 110), outline=INK); d.ellipse((x + 4, 170, x + 8, 174), fill=(255, 60, 60))
    d.line([(40, 236), (100, 250), (150, 242), (210, 252)], fill=(20, 20, 26), width=2)
    for y in range(236, 266, 7):
        for x in range(-((y // 7) % 2) * 9, W, 18): d.rectangle((x, y, x + 17, y + 6), fill=(16, 14, 28) if ((x // 18) + (y // 7)) % 2 else (64, 56, 104))
    d.line([(0, 236), (W, 236)], fill=INK)
    for y in range(266, H, 14):
        for x in range(0, W, 18):
            c = (14, 12, 26) if ((x // 18) + (y // 14)) % 2 else (70 - (y - 266) // 8, 60 - (y - 266) // 8, 112 - (y - 266) // 6); d.rectangle((x, y, x + 17, y + 13), fill=c)
    d.line([(0, 265), (W, 265)], fill=INK); im = glow(im, 135, 270, 150, (150, 120, 255), .3); return im

# ------------------------------------------------------------------ 4 CLUE 4: theatre hall — crown, fedora and one sparkly glove on pedestals
def bg_crown():
    im, d = canvas([(40, 20, 70), (86, 40, 100), (130, 60, 110)])
    for y in range(0, 266, 14):
        for x in range(-((y // 14) % 2) * 14, W, 28): d.rectangle((x, y, x + 26, y + 12), fill=(80 + (x + y) % 9, 38, 96), outline=(56, 26, 74))
    for x in (30, 135, 240):                                                                                                                                    # arches with gold trim
        d.arc((x - 34, 40, x + 34, 140), 180, 360, fill=GOLD, width=3); d.rectangle((x - 36, 90, x - 30, 236), fill=GOLD_S, outline=INK); d.rectangle((x + 30, 90, x + 36, 236), fill=GOLD_S, outline=INK)
    for x in (56, 214):
        d.line([(x, 0), (x, 36)], fill=GOLD_S); d.ellipse((x - 14, 36, x + 14, 56), fill=(255, 240, 190), outline=INK)
        for k in range(5): d.line([(x - 12 + k * 6, 56), (x - 12 + k * 6, 66)], fill=GOLD)
    im = glow(im, 135, 150, 110, (255, 220, 120), .45); im = beam(im, 135, 135, 0, 236, 30, 130, (255, 244, 200), .26); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((88, 190, 182, 236), fill=(230, 224, 240), outline=INK); d.rectangle((84, 184, 186, 192), fill=(250, 246, 255), outline=INK)
    d.polygon([(104, 168), (166, 168), (160, 184), (110, 184)], fill=(176, 26, 56), outline=INK); crown(d, 135, 138)
    d.rectangle((90, 196, 180, 232), outline=(180, 170, 210))
    d.rectangle((24, 196, 72, 236), fill=(230, 224, 240), outline=INK); d.rectangle((20, 190, 76, 198), fill=(250, 246, 255), outline=INK); fedora(d, 48, 166)
    d.rectangle((198, 196, 246, 236), fill=(230, 224, 240), outline=INK); d.rectangle((194, 190, 250, 198), fill=(250, 246, 255), outline=INK); glove(d, 222, 174)
    for (x, y) in ((140, 120), (122, 130), (150, 150), (48, 150), (222, 156), (206, 170)): d.point((x, y), fill=WHITE); d.line([(x - 3, y), (x + 3, y)], fill=(255, 250, 200)); d.line([(x, y - 3), (x, y + 3)], fill=(255, 250, 200))
    twinkles(d, (0, 0, W, 240), 70)
    d.rectangle((0, 236, W, 266), fill=(150, 130, 170)); d.line([(0, 236), (W, 236)], fill=INK)
    for y in range(266, H, 20):                                                                                                                                 # marble diamond floor
        for x in range(-((y // 20) % 2) * 20, W, 40):
            d.polygon([(x + 20, y), (x + 40, y + 10), (x + 20, y + 20), (x, y + 10)], fill=(236, 230, 244), outline=(176, 166, 196)); d.line([(x + 14, y + 6), (x + 22, y + 3)], fill=WHITE)
            d.polygon([(x + 40, y), (x + 60, y + 10), (x + 40, y + 20), (x + 20, y + 10)], fill=(120, 100, 150), outline=(176, 166, 196))
    d.line([(0, 265), (W, 265)], fill=INK)
    for x in (10, 90, 180, 258): d.rectangle((x - 2, 270, x + 2, 316), fill=GOLD_S, outline=INK); d.ellipse((x - 6, 264, x + 6, 276), fill=GOLD, outline=INK)
    d.line([(10, 280), (90, 292)], fill=(190, 30, 60), width=3); d.line([(180, 292), (258, 280)], fill=(190, 30, 60), width=3)
    return im

# ------------------------------------------------------------------ 5 OUTRO: neon night city, palm trees, searchlights
def bg_night():
    im, d = canvas([(10, 10, 38), (44, 30, 96), (130, 56, 130), (236, 120, 130)])
    twinkles(d, (0, 0, W, 130), 120); d.ellipse((190, 30, 224, 64), fill=(252, 248, 222), outline=(236, 230, 200)); d.ellipse((200, 38, 210, 48), fill=(232, 226, 196))
    for k in range(4): cloud(d, -10 + k * 78, 70 + (k % 2) * 26, 56, (96, 60, 130), (64, 40, 100), (150, 100, 170))
    for (x, c) in ((30, (255, 255, 255)), (110, (255, 244, 200)), (246, (200, 230, 255))): im = beam(im, x, x + (110 - x) // 2 + 40, 236, 0, 8, 46, c, .22)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    x = 0
    while x < W: w = R.randint(14, 26); h = R.randint(40, 100); d.rectangle((x, 236 - h, x + w, 236), fill=(54, 40, 96), outline=(38, 28, 76)); x += w + 1
    for _ in range(120): d.point((R.randint(0, W), R.randint(150, 232)), fill=(255, 214, 140))
    for (x0, x1, h) in ((0, 50, 130), (212, 270, 150)):
        d.rectangle((x0, 266 - h, x1, 266), fill=(36, 30, 74), outline=INK); d.rectangle((x0, 266 - h, x1, 266 - h + 3), fill=(80, 70, 130))
        for wy in range(266 - h + 10, 256, 12):
            for wx in range(x0 + 5, x1 - 6, 10): d.rectangle((wx, wy, wx + 4, wy + 6), fill=(255, 214, 120) if R.random() < .5 else (24, 22, 52))
    d.rectangle((58, 150, 128, 214), fill=(16, 10, 30), outline=INK); d.rectangle((62, 154, 124, 168), fill=(255, 60, 120), outline=INK)                          # cinema marquee (blank)
    for k in range(10): d.ellipse((63 + k * 6, 156, 67 + k * 6, 160), fill=(255, 244, 190) if (k + 1) % 2 else (255, 150, 200))
    d.rectangle((66, 176, 120, 210), fill=(36, 22, 70), outline=(255, 214, 90)); d.line([(93, 176), (93, 210)], fill=(255, 214, 90))
    for (x, base, hgt) in ((158, 266, 120), (192, 266, 100)):
        pts = [(x, base), (x - 6, base - hgt * .5), (x + 4, base - hgt * .8), (x + 2, base - hgt)]; d.line(pts, fill=(60, 40, 40), width=4)
        for a in range(-80, 100, 28): r = math.radians(a - 90); d.polygon([(x + 2, base - hgt), (x + 2 + 26 * math.cos(r), base - hgt + 20 * math.sin(r) + 12), (x + 2 + 14 * math.cos(r + .3), base - hgt + 8)], fill=(40, 120, 90), outline=INK)
    for x in (100, 232): d.line([(x, 266), (x, 214)], fill=(70, 60, 100), width=2); d.rectangle((x - 5, 210, x + 5, 216), fill=(255, 224, 140), outline=INK)
    masonry(d, 0, 266, W, H, base=(78, 70, 116), sh=(52, 46, 86), li=(124, 112, 164), mortar=(30, 24, 52), seed=67); d.line([(0, 265), (W, 265)], fill=INK)
    for (px, py, pw) in ((20, 292, 44), (150, 306, 58), (90, 334, 36)): d.ellipse((px, py, px + pw, py + 8), fill=(90, 70, 140), outline=(50, 40, 90)); d.line([(px + 6, py + 3), (px + pw - 6, py + 3)], fill=(255, 150, 200))
    return im

# ------------------------------------------------------------------ 6 RECAP (yesterday: The Beatles): sunny London street with a zebra crossing, beetle-shaped car, plane trees
def bg_abbey():
    im, d = canvas([(110, 170, 240), (176, 210, 248), (240, 236, 224)])
    for k in range(5): cloud(d, -10 + k * 64, 40 + (k % 3) * 24, 54, (255, 255, 255), (206, 222, 244), (255, 255, 255))
    d.rectangle((0, 150, W, 236), fill=(176, 120, 100), outline=INK)                                                                                        # brick wall + house
    for y in range(152, 236, 8):
        for x in range(-((y // 8) % 2) * 8, W, 16): d.rectangle((x, y, x + 14, y + 6), fill=(190 + (x + y) % 9, 124, 100), outline=(150, 92, 76))
    d.rectangle((96, 120, 250, 190), fill=(244, 240, 232), outline=INK); d.polygon([(90, 120), (256, 120), (173, 80)], fill=(120, 72, 70), outline=INK)
    for x in (110, 150, 190, 226): d.rectangle((x, 132, x + 14, 156), fill=(120, 170, 220), outline=INK); d.line([(x + 7, 132), (x + 7, 156)], fill=INK); d.line([(x, 144), (x + 14, 144)], fill=INK)
    d.rectangle((14, 150, 86, 236), fill=(30, 36, 44), outline=INK)                                                                                         # black gate
    for x in range(18, 86, 6): d.line([(x, 152), (x, 234)], fill=(80, 86, 96))
    d.rectangle((0, 214, 12, 236), fill=(210, 40, 50), outline=INK); d.rectangle((2, 218, 10, 221), fill=(30, 20, 20))                                          # red postbox
    d.rectangle((90, 196, 126, 210), fill=(250, 250, 244), outline=INK); d.line([(94, 203), (122, 203)], fill=(110, 110, 120))                                   # blank street sign
    for (cx, w) in ((24, 54), (240, 60)):
        d.rectangle((cx - 5, 150, cx + 5, 236), fill=(120, 92, 70), outline=INK); d.line([(cx - 2, 160), (cx - 2, 230)], fill=(166, 134, 104))
        for k in range(9): px, py = cx + R.randint(-w // 2, w // 2), R.randint(70, 150); d.ellipse((px - 14, py - 10, px + 14, py + 12), fill=[(70, 150, 70), (96, 176, 84), (52, 124, 66)][k % 3], outline=INK)
        for _ in range(18): d.point((cx + R.randint(-w // 2, w // 2), R.randint(66, 150)), fill=(170, 220, 120))
    d.rectangle((0, 236, W, 266), fill=(140, 144, 156)); d.line([(0, 236), (W, 236)], fill=INK); d.rectangle((0, 262, W, 266), fill=(196, 198, 208), outline=INK)  # pavement + kerb
    cx, cy = 52, 224                                                                                                                                           # parked beetle-shaped car
    d.pieslice((cx - 2, cy - 22, cx + 66, cy + 26), 180, 360, fill=(246, 244, 238), outline=INK); d.rectangle((cx - 2, cy + 2, cx + 66, cy + 14), fill=(246, 244, 238), outline=INK)
    d.pieslice((cx + 14, cy - 16, cx + 50, cy + 6), 180, 360, fill=(150, 196, 226), outline=INK); d.line([(cx + 32, cy - 16), (cx + 32, cy)], fill=INK)
    for wx in (cx + 12, cx + 52): d.ellipse((wx - 8, cy + 6, wx + 8, cy + 22), fill=(30, 30, 38), outline=INK); d.ellipse((wx - 3, cy + 11, wx + 3, cy + 17), fill=(190, 190, 204))
    d.ellipse((cx + 60, cy - 2, cx + 66, cy + 4), fill=(255, 240, 160), outline=INK)
    for x in (178, 250):                                                                                                                                       # belisha beacons
        for k in range(5): d.rectangle((x - 2, 190 + k * 12, x + 2, 196 + k * 12), fill=(30, 30, 34) if k % 2 else WHITE, outline=INK)
        d.ellipse((x - 6, 178, x + 6, 192), fill=(255, 190, 60), outline=INK); d.point((x - 2, 182), fill=WHITE)
    d.rectangle((0, 266, W, H), fill=(88, 90, 102))
    for y in range(266, H, 5): d.line([(0, y), (W, y)], fill=(80 + (y % 3) * 4, 82, 94))
    noise(im, (0, 266, W, H), [(70, 72, 84), (110, 112, 124)], 900)
    for k in range(-1, 9): x = 6 + k * 34; d.rounded_rectangle((x, 272, x + 24, 362), 4, fill=(246, 246, 244), outline=(190, 190, 200))                      # zebra crossing
    d.line([(0, 266), (W, 266)], fill=INK); d.rectangle((0, 400, W, 404), fill=(236, 214, 90))
    return im

# ------------------------------------------------------------------ mystery dancer v3 (original design): SLIM and elegant — black fedora, shoulder-length curls, sequin jacket, cropped trousers, white socks, loafers, ONE white glove
def _glove_hand(d, x, y, flip=1, up=False, down=False):
    Wc, Ws = (252, 252, 255), (178, 188, 220)
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=Wc); d.line([(x - 2, y + 2), (x + 2, y + 2)], fill=Ws)
    for k, fx in enumerate((-3, -1, 1, 3)):                                                         # four slim fingers with 1px gaps
        ln = (4, 6, 5, 4)[k] + (1 if up else 0); y0, y1 = (y + 3, y + 3 + ln) if down else (y - 3 - ln, y - 2)
        d.rectangle((x + fx - 1, min(y0, y1), x + fx - 1, max(y0, y1)), fill=Wc); d.point((x + fx, (min(y0, y1) + max(y0, y1)) // 2), fill=Wc)
    ty = y - 1; d.polygon([(x - 3 * flip, ty), (x - 6 * flip, ty - 2), (x - 6 * flip, ty), (x - 4 * flip, ty + 2)], fill=Wc)          # thumb
    cy = y - 4 if down else y + 3; d.line([(x - 3, cy), (x + 3, cy)], fill=(150, 160, 200), width=2)                                 # cuff
    for _ in range(8): d.point((x + R.randint(-3, 4), y + R.randint(-7, 5)), fill=R.choice([(120, 220, 255), (255, 200, 250), (255, 255, 150), (200, 200, 230)]))
def _loafer(d, x, y, flip=1, toe=False):
    L, LH = (20, 18, 28), (126, 122, 160)
    if toe:                                                                                      # heel raised, only the toe touches the floor (moonwalk)
        d.polygon([(x - 3, y - 6), (x + 2, y - 4), (x + 5 * flip, y + 6), (x - 1 * flip, y + 7), (x - 4 * flip, y + 1)], fill=L); d.line([(x - 1, y - 4), (x + 3 * flip, y + 4)], fill=LH)
    else:
        d.rounded_rectangle((x - 5, y, x + 7, y + 7), 3, fill=L); d.line([(x - 3, y + 1), (x + 4, y + 1)], fill=LH); d.rectangle((x - 5, y + 6, x + 7, y + 7), fill=(8, 6, 14))

def dancer(frame=0):
    """0 hat tip · 1 moonwalk glide + glove to the sky · 2 glove at chest, back arm swings · 3 hat tip + glove point"""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK, SKS, SKL = (226, 182, 150), (190, 142, 112), (244, 208, 178)
    JK, JKS, JKL = (30, 28, 42), (14, 12, 24), (90, 88, 122)
    HT, HTS, HTL = (28, 26, 38), (10, 8, 18), (96, 94, 126)
    bob = [0, 0, 1, 0][frame]
    pose = [dict(rh=((41, 49), (31, 40), (36, 21)), lh=((59, 49), (66, 65), (64, 84)), glove_up=False, legs=("flat", "flat")),
            dict(rh=((41, 49), (32, 66), (40, 82)), lh=((59, 49), (71, 36), (78, 17)), glove_up=True, legs=("toe", "flat")),
            dict(rh=((41, 49), (34, 62), (30, 78)), lh=((59, 49), (69, 60), (63, 52)), glove_up=False, legs=("flat", "toe")),
            dict(rh=((41, 49), (31, 40), (36, 21)), lh=((59, 49), (70, 56), (79, 47)), glove_up=False, legs=("flat", "flat"))][frame]
    # --- legs: slim cropped black trousers, white socks, loafers
    for side, x0, kind in ((-1, 46, pose["legs"][0]), (1, 54, pose["legs"][1])):
        tp = 3 if kind == "toe" else 0; fx = x0 + (side * 5 if kind == "toe" else side)
        limb(d, (x0, 90), (x0 + (fx - x0) // 2, 110), 8, 7, (30, 28, 42), (14, 12, 24), (74, 72, 104)); limb(d, (x0 + (fx - x0) // 2, 110), (fx, 123 - tp), 7, 6, (30, 28, 42), (14, 12, 24), (74, 72, 104))
        d.rectangle((fx - 2, 121 - tp, fx + 2, 129 - tp), fill=(252, 252, 255)); d.line([(fx - 2, 124 - tp), (fx + 2, 124 - tp)], fill=(196, 200, 222))
        _loafer(d, fx, 130 if kind != "toe" else 131, side, kind == "toe")
    d.polygon([(42, 84), (58, 84), (59, 98), (41, 98)], fill=(30, 28, 42))
    # --- torso: slim black sequin jacket, satin lapels, white shirt
    d.polygon([(40, 46 + bob), (60, 46 + bob), (58, 90), (42, 90)], fill=JK); d.line([(59, 48 + bob), (58, 88)], fill=JKS, width=2); d.line([(41, 48 + bob), (42, 88)], fill=JKL)
    d.polygon([(45, 44 + bob), (55, 44 + bob), (50, 74)], fill=(246, 246, 252)); d.line([(50, 54), (50, 74)], fill=(196, 200, 222))
    d.polygon([(45, 44 + bob), (50, 60), (46, 78), (41, 56)], fill=(58, 56, 80)); d.polygon([(55, 44 + bob), (50, 60), (54, 78), (59, 56)], fill=(26, 24, 40))     # satin lapels
    d.line([(45, 47 + bob), (49, 59)], fill=JKL); d.polygon([(46, 44 + bob), (50, 51), (48, 46)], fill=WHITE); d.polygon([(54, 44 + bob), (50, 51), (52, 46)], fill=(214, 218, 236))
    d.ellipse((50, 72, 52, 74), fill=(200, 200, 230)); d.ellipse((50, 80, 52, 82), fill=(200, 200, 230))
    texture(im, (40, 46, 60, 90), [(150, 220, 255), (255, 214, 250), (250, 250, 255), JKL], 60)                      # sequins
    # --- slim arms
    (s1, e1, w1), (s2, e2, w2) = pose["rh"], pose["lh"]
    s1 = (s1[0], s1[1] + bob); s2 = (s2[0], s2[1] + bob)
    limb(d, s1, e1, 6, 5, JK, JKS, JKL); limb(d, e1, w1, 5, 4, JK, JKS, JKL); limb(d, s2, e2, 6, 5, JK, JKS, JKL); limb(d, e2, w2, 5, 4, JK, JKS, JKL)
    texture(im, (24, 14, 86, 90), [(150, 220, 255), (255, 214, 250), WHITE], 18)
    # --- head: small oval face, gentle eyes, soft smile, shoulder-length curls
    hx, hy = 50, 28 + bob
    for sx in (-1, 1):                                                                                                  # curls frame the face down to the shoulders
        for k, (cx, cy) in enumerate(((hx + sx * 9, hy - 2), (hx + sx * 10, hy + 5), (hx + sx * 9, hy + 12), (hx + sx * 9, hy + 18))): d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(22, 18, 26)); d.point((cx - sx, cy - 1), fill=(96, 90, 126))
    d.rectangle((47, 37 + bob, 53, 46 + bob), fill=SKS)
    d.ellipse((hx - 8, hy - 13, hx + 8, hy + 13), fill=SK); d.ellipse((hx + 2, hy - 9, hx + 9, hy + 11), fill=SKS); d.ellipse((hx - 6, hy + 1, hx - 2, hy + 7), fill=SKL)
    d.polygon([(hx - 7, hy + 5), (hx - 3, hy + 13), (hx + 3, hy + 13), (hx + 7, hy + 5), (hx + 4, hy + 12), (hx - 4, hy + 12)], fill=SKS)               # soft jaw shadow
    for k, ex in enumerate((hx - 5, hx + 2)):                                                                         # calm eyes: small, dark iris, tiny highlight, thin soft brows
        d.rectangle((ex, hy - 1, ex + 3, hy + 1), fill=(240, 232, 226)); d.rectangle((ex + 1, hy - 1, ex + 2, hy + 1), fill=(52, 34, 28)); d.point((ex + 1, hy - 1), fill=(200, 190, 190))
        d.line([(ex - 1, hy - 3), (ex + 4, hy - 3)], fill=(70, 46, 40)); d.point((ex + 1 + k, hy - 4), fill=(70, 46, 40))
    d.line([(hx, hy + 1), (hx, hy + 5)], fill=SKS); d.point((hx - 1, hy + 6), fill=(158, 108, 96)); d.point((hx + 1, hy + 6), fill=(158, 108, 96)); d.point((hx, hy + 5), fill=SKL)   # nose
    d.line([(hx - 3, hy + 9), (hx + 3, hy + 9)], fill=(174, 88, 98)); d.point((hx - 4, hy + 8), fill=(174, 88, 98)); d.point((hx + 4, hy + 8), fill=(174, 88, 98)); d.point((hx, hy + 10), fill=(200, 120, 124))   # small smile
    # --- fedora: pinched crown, satin band, tilted brim
    d.polygon([(hx - 8, hy - 13), (hx - 7, hy - 21), (hx - 4, hy - 24), (hx - 1, hy - 22), (hx + 1, hy - 22), (hx + 4, hy - 24), (hx + 7, hy - 21), (hx + 8, hy - 13)], fill=HT)
    d.polygon([(hx - 1, hy - 22), (hx, hy - 19), (hx + 1, hy - 22)], fill=HTS)
    d.rectangle((hx - 8, hy - 17, hx + 8, hy - 14), fill=(60, 58, 84)); d.line([(hx - 7, hy - 16), (hx + 7, hy - 16)], fill=(140, 138, 178))
    d.line([(hx - 6, hy - 21), (hx - 4, hy - 23)], fill=HTL)
    d.polygon([(hx - 16, hy - 8), (hx - 12, hy - 14), (hx + 12, hy - 14), (hx + 15, hy - 11), (hx + 16, hy - 9), (hx + 9, hy - 6), (hx - 9, hy - 6)], fill=HT)
    d.polygon([(hx - 16, hy - 8), (hx - 9, hy - 6), (hx + 9, hy - 6), (hx + 16, hy - 9), (hx + 9, hy - 8), (hx - 9, hy - 8)], fill=HTS); d.line([(hx - 12, hy - 11), (hx - 6, hy - 13)], fill=HTL)
    d.rectangle((hx - 6, hy - 5, hx + 6, hy - 4), fill=(160, 118, 92))                                                    # brim shadow on the forehead
    # --- hands drawn last (the one at the hat brim sits on top of it)
    for (e, w, glove) in ((e1, w1, False), (e2, w2, True)):
        if glove: _glove_hand(d, w[0], w[1] + bob, 1 if w[0] > 50 else -1, pose["glove_up"], down=(w[1] > e[1] + 6))
        else: hand(d, (w[0], w[1] + bob), SK, SKS, flip=1 if w[0] > 50 else -1)
    return outline(im)

def sheet_bgs(items, path, cols=4, s=2):
    cw, ch = W * s, H * s; rows = (len(items) + cols - 1) // cols
    sh = Image.new("RGB", (cols * cw + 10 * (cols + 1), rows * (ch + 34) + 50), (16, 12, 30)); d = ImageDraw.Draw(sh); d.fontmode = "1"; label(d, 10, 10, "PARTE 14 · FONDOS (270x480 ×2) · motor GBA procedural", 20)
    for i, (t, im) in enumerate(items): x, y = 10 + (i % cols) * (cw + 10), 50 + (i // cols) * (ch + 34); sh.paste(im.resize((cw, ch), Image.NEAREST), (x, y)); label(d, x, y + ch + 4, t, 15)
    sh.save(path)

def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".png") or f.endswith(".jpg"): os.remove(os.path.join(OUT, f)) if os.path.isfile(os.path.join(OUT, f)) else None
    bgs = [("HOOK (escenario)", bg_hook()), ("PISTA 1 · Gary, Indiana", bg_gary()), ("PISTA 2 · los 8 Grammys", bg_grammy()), ("PISTA 3 · especial TV 1983", bg_motown()),
           ("PISTA 4 · corona, sombrero, guante", bg_crown()), ("CIERRE (noche)", bg_night()), ("AYER: The Beatles", bg_abbey())]
    for i, (t, im) in enumerate(bgs): im.save(os.path.join(OUT, f"fondo_{i}.png"))
    sheet_bgs(bgs, os.path.join(OUT, "parte14_fondos.png"))
    A = [dancer(f) for f in range(4)]; s = 4
    frames = [silhouette(A[0])] + A + [silhouette(A[2])]; tags = ["silueta", "quieto", "paso 1", "paso 2", "paso 3", "silueta 2"]
    sheet = Image.new("RGB", (6 * 100 * s + 70, 140 * s + 100), (40, 34, 70)); d = ImageDraw.Draw(sheet); d.fontmode = "1"; label(d, 10, 10, "PARTE 14 · ARTISTA MISTERIOSO (100x140, ×4)", 22)
    for k, fr in enumerate(frames):
        x = 10 + k * (100 * s + 10); bg = Image.new("RGBA", fr.size, (90, 80, 140, 255) if k in (0, 5) else (180, 170, 220, 255)); bg.alpha_composite(fr)
        sheet.paste(bg.convert("RGB").resize((100 * s, 140 * s), Image.NEAREST), (x, 50)); label(d, x + 6, 56, tags[k], 18); fr.save(os.path.join(OUT, f"artista_{k}.png"))
    sheet.save(os.path.join(OUT, "parte14_personaje.png")); print("ok", OUT)

if __name__ == "__main__":
    main()

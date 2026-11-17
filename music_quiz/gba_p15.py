"""Parte 15 (Guns N' Roses) — procedural GBA backgrounds (same engine as Parte 12/14) + mystery guitarist sprite (top hat, curls, shades, low-slung guitar).
No names/logos: flyers use icons only. usage: python3 gba_p15.py -> sprites/parte15/fondo_0..5.png, artista_0..5.png + preview sheets
fondos: 0 hook (Sunset Strip night) · 1 club 1985 (two flyers) · 2 London|LA split · 3 Wembley 1992 tribute · 4 $584M tour · 5 outro (hills at night)"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw
from gba_sprites import (W, H, F, INK, WHITE, grad, outline, silhouette, cloud, masonry, ground, side_walls, star, glow, beam, noise,
                         string_lights, limb, hand, shoe, texture, label)
from gba_p14 import canvas, fog, twinkles, sheet_bgs, GOLD, GOLD_S, GOLD_L

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte15")
R = random.Random(15)

def palm(d, x, base, hgt, lean=0, col=(40, 120, 90)):
    pts = [(x, base), (x + lean * .4, base - hgt * .5), (x + lean, base - hgt)]; d.line(pts, fill=(70, 46, 40), width=4)
    for a in range(-80, 100, 26):
        r = math.radians(a - 90); tx, ty = x + lean, base - hgt
        d.polygon([(tx, ty), (tx + 28 * math.cos(r), ty + 20 * math.sin(r) + 14), (tx + 15 * math.cos(r + .35), ty + 9)], fill=col, outline=INK)
def neon(d, box, col, text=None, size=9):
    x0, y0, x1, y1 = box; d.rectangle(box, fill=(14, 8, 24), outline=col, width=2)
    if text: d.text(((x0 + x1) // 2, (y0 + y1) // 2), text, font=F(size), fill=col, anchor="mm")

# ------------------------------------------------------------------ 0 HOOK: Sunset-Strip-style night street, red glow, neon, palms
def bg_strip():
    im, d = canvas([(8, 4, 20), (40, 10, 44), (110, 24, 60), (210, 70, 70)])
    twinkles(d, (0, 0, W, 110), 90); d.ellipse((186, 34, 224, 72), fill=(255, 120, 90), outline=(220, 70, 70)); d.ellipse((196, 44, 208, 56), fill=(236, 100, 80))
    x = 0
    while x < W: w = R.randint(16, 28); h = R.randint(60, 120); d.rectangle((x, 236 - h, x + w, 236), fill=(40, 22, 54), outline=(28, 14, 40)); x += w + 1
    for (x0, x1, h, c) in ((0, 70, 150, (60, 30, 70)), (200, 270, 170, (66, 28, 64))):
        d.rectangle((x0, 266 - h, x1, 266), fill=c, outline=INK)
        for wy in range(266 - h + 12, 256, 14):
            for wx in range(x0 + 6, x1 - 8, 12): d.rectangle((wx, wy, wx + 5, wy + 7), fill=(255, 190, 110) if R.random() < .45 else (24, 14, 36))
    neon(d, (6, 120, 62, 142), (255, 60, 110)); [d.line([(10 + k * 10, 126), (16 + k * 10, 136)], fill=(255, 140, 170)) for k in range(5)]
    neon(d, (206, 110, 262, 132), (90, 230, 255)); d.ellipse((222, 114, 246, 128), outline=(90, 230, 255), width=2)
    neon(d, (92, 90, 178, 130), (255, 214, 90)); d.polygon([(110, 122), (135, 98), (160, 122)], outline=(255, 214, 90))                          # blank billboard + triangle
    palm(d, 84, 266, 120, -6); palm(d, 196, 266, 140, 8)
    for x in (30, 112, 232): d.line([(x, 266), (x, 206)], fill=(70, 50, 80), width=2); d.rectangle((x - 5, 202, x + 5, 208), fill=(255, 224, 140), outline=INK)
    d.rectangle((0, 236, W, 266), fill=(52, 34, 70)); d.line([(0, 236), (W, 236)], fill=INK)
    for x in range(0, W, 26): d.rectangle((x + 4, 250, x + 18, 252), fill=(236, 200, 110))
    im = glow(im, 135, 180, 170, (255, 60, 80), .35); d = ImageDraw.Draw(im); d.fontmode = "1"
    masonry(d, 0, 266, W, H, base=(70, 50, 82), sh=(46, 32, 60), li=(120, 90, 130), mortar=(26, 16, 38), seed=71); d.line([(0, 265), (W, 265)], fill=INK)
    for (px, py, pw) in ((20, 292, 46), (150, 308, 58), (88, 336, 36)): d.ellipse((px, py, px + pw, py + 8), fill=(150, 60, 100), outline=(90, 30, 70)); d.line([(px + 6, py + 3), (px + pw - 6, py + 3)], fill=(255, 150, 190))
    return im

# ------------------------------------------------------------------ 1 CLUE 1: small LA club, marquee, two flyers (icons only) joined by "+"
def bg_club():
    im, d = canvas([(14, 8, 30), (40, 18, 54), (66, 26, 70)])
    for y in range(0, 236, 12):
        for x in range(-((y // 12) % 2) * 12, W, 24): d.rectangle((x, y, x + 22, y + 10), fill=(74 + (x + y) % 9, 38, 58), outline=(48, 24, 40))
    d.rectangle((50, 40, 220, 80), fill=(18, 10, 28), outline=(255, 214, 90), width=3)
    for k in range(17): d.ellipse((52 + k * 10, 38, 57 + k * 10, 43), fill=(255, 240, 160) if k % 2 else (255, 120, 90), outline=INK); d.ellipse((52 + k * 10, 77, 57 + k * 10, 82), fill=(255, 240, 160) if k % 2 else (255, 120, 90), outline=INK)
    d.text((135, 60), "26·03·85", font=F(18), fill=(255, 230, 150), anchor="mm", stroke_width=1, stroke_fill=(120, 50, 20))
    d.rectangle((44, 98, 120, 188), fill=(110, 190, 240), outline=INK, width=2); d.rectangle((150, 98, 226, 188), fill=(226, 60, 70), outline=INK, width=2)                       # two flyers
    d.polygon([(82, 110), (66, 146), (80, 146), (72, 178), (98, 136), (84, 136), (96, 110)], fill=(255, 236, 90), outline=INK)                                                   # bolt
    star(d, 188, 142, 26, (250, 250, 250), (200, 200, 220)); [d.rectangle((160 + k * 12, 178, 166 + k * 12, 182), fill=(255, 220, 220)) for k in range(5)]
    d.rectangle((50, 114, 114, 118), fill=(60, 120, 170)); d.rectangle((158, 182, 218, 185), fill=(160, 30, 44))
    for (x, y) in ((44, 98), (120, 98), (150, 98), (226, 98)): d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(220, 220, 230), outline=INK)
    d.rectangle((127, 130, 143, 146), fill=(255, 230, 90), outline=INK); d.line([(135, 133), (135, 143)], fill=INK, width=3); d.line([(130, 138), (140, 138)], fill=INK, width=3)      # the "+"
    d.rectangle((226, 150, 262, 230), fill=(40, 26, 44), outline=INK); d.rectangle((230, 158, 258, 226), fill=(18, 10, 26)); [d.rectangle((234, 170 + k * 14, 254, 176 + k * 14), fill=(60, 36, 80)) for k in range(4)]   # club door
    for x in (6, 28): d.rectangle((x, 196, x + 14, 236), fill=(54, 34, 64), outline=INK)
    d.rectangle((0, 236, W, 266), fill=(60, 44, 74)); d.line([(0, 236), (W, 236)], fill=INK)
    im = glow(im, 135, 60, 130, (255, 200, 110), .3); im = beam(im, 135, 135, 80, 236, 40, 160, (255, 230, 170), .1); d = ImageDraw.Draw(im); d.fontmode = "1"
    twinkles(d, (0, 0, W, 230), 60)
    masonry(d, 0, 266, W, H, base=(84, 62, 92), sh=(56, 40, 68), li=(130, 100, 140), mortar=(28, 18, 40), seed=73); d.line([(0, 265), (W, 265)], fill=INK)
    return im

# ------------------------------------------------------------------ 2 CLUE 2: split scene — grey London (left) / sunny Los Angeles (right)
def bg_split():
    im, d = canvas([(120, 130, 156), (170, 180, 200)])
    d.rectangle((135, 0, W, 266), fill=(120, 190, 250)); im.paste(grad(135, 266, [(80, 160, 240), (190, 226, 250), (255, 226, 170)]).convert("RGB"), (135, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(3): cloud(d, -10 + k * 50, 36 + (k % 2) * 24, 50, (206, 210, 222), (150, 156, 176), (236, 240, 248))
    for k in range(2): cloud(d, 150 + k * 60, 46 + (k % 2) * 20, 46, (255, 255, 255), (206, 226, 248), (255, 255, 255))
    d.rectangle((14, 60, 54, 236), fill=(176, 150, 110), outline=INK); d.polygon([(10, 60), (58, 60), (34, 28)], fill=(96, 110, 100), outline=INK); d.line([(34, 28), (34, 14)], fill=INK)   # clock tower
    d.ellipse((20, 84, 48, 112), fill=(250, 244, 214), outline=INK, width=2); d.line([(34, 98), (34, 88)], fill=INK); d.line([(34, 98), (42, 102)], fill=INK)
    for y in range(124, 232, 18): d.rectangle((24, y, 44, y + 10), fill=(120, 100, 80), outline=INK)
    d.rectangle((70, 196, 128, 232), fill=(200, 40, 50), outline=INK); d.rectangle((70, 178, 128, 196), fill=(220, 60, 70), outline=INK)                                                  # double-decker bus
    for x in range(74, 126, 14): d.rectangle((x, 182, x + 9, 192), fill=(170, 210, 240), outline=INK); d.rectangle((x, 202, x + 9, 212), fill=(170, 210, 240), outline=INK)
    for x in (84, 116): d.ellipse((x - 7, 226, x + 7, 240), fill=(30, 30, 36), outline=INK)
    d.rectangle((58, 206, 68, 236), fill=(214, 40, 48), outline=INK); d.rectangle((60, 210, 66, 224), fill=(250, 240, 200))                                                                 # red phone box
    for x in range(140, W, 44): palm(d, x + 18, 236, 90 + (x % 3) * 12, (-1) ** (x // 44) * 6)
    d.polygon([(135, 190), (180, 150), (230, 190)], fill=(160, 120, 90), outline=INK); d.polygon([(200, 200), (250, 150), (W, 190), (W, 236), (200, 236)], fill=(190, 140, 100), outline=INK)   # hills
    d.ellipse((220, 30, 252, 62), fill=(255, 236, 140), outline=(250, 190, 80))
    d.line([(135, 0), (135, 266)], fill=(255, 255, 255), width=3); [d.line([(135, y), (135, y + 8)], fill=(210, 40, 60), width=3) for y in range(0, 266, 20)]
    d.rectangle((0, 236, W, 266), fill=(130, 130, 144)); d.rectangle((135, 236, W, 266), fill=(190, 180, 170)); d.line([(0, 236), (W, 236)], fill=INK)
    masonry(d, 0, 266, 135, H, base=(112, 114, 134), sh=(78, 80, 104), li=(160, 162, 184), mortar=(50, 52, 76), seed=75)
    masonry(d, 135, 266, W, H, base=(196, 150, 110), sh=(150, 106, 76), li=(230, 190, 150), mortar=(110, 72, 52), seed=76); d.line([(0, 265), (W, 265)], fill=INK); d.line([(135, 266), (135, H)], fill=(255, 255, 255), width=3)
    return im

# ------------------------------------------------------------------ 3 CLUE 3: Wembley-style stadium night — tribute stage, grand piano, candles, lighters
def bg_tribute():
    im, d = canvas([(8, 10, 34), (26, 22, 70), (60, 40, 110)])
    twinkles(d, (0, 0, W, 120), 100)
    for x0 in (30, 240):
        d.rectangle((x0 - 12, 64, x0 + 12, 150), fill=(230, 226, 220), outline=INK); d.rectangle((x0 + 4, 66, x0 + 11, 150), fill=(190, 184, 184)); d.polygon([(x0 - 14, 64), (x0 + 14, 64), (x0, 46)], fill=(230, 226, 220), outline=INK)
    d.polygon([(0, 200), (W, 200), (W, 146), (0, 146)], fill=(60, 50, 100))
    for k in range(5): d.rectangle((0, 148 + k * 10, W, 152 + k * 10), fill=(80, 68, 124))
    for _ in range(320): d.point((R.randint(0, W), R.randint(148, 198)), fill=R.choice([(255, 220, 140), (250, 120, 150), (180, 210, 255), (255, 255, 255), (40, 30, 70)]))
    d.rectangle((50, 80, 220, 160), fill=(14, 10, 34), outline=(180, 180, 220), width=2); d.rectangle((54, 84, 216, 156), fill=(30, 24, 70))
    d.ellipse((120, 98, 150, 138), fill=(255, 230, 140), outline=INK); d.polygon([(126, 118), (135, 90), (144, 118)], fill=(255, 140, 60), outline=INK)                           # candle flame icon
    d.rectangle((130, 126, 140, 148), fill=(250, 244, 230), outline=INK); d.text((80, 120), "1992", font=F(18), fill=(255, 230, 150), anchor="mm"); d.text((190, 120), "20·4", font=F(14), fill=(255, 230, 150), anchor="mm")
    d.rectangle((40, 200, 230, 238), fill=(46, 40, 86), outline=INK); d.rectangle((30, 194, 240, 204), fill=(84, 70, 130), outline=INK)                                                   # stage
    d.polygon([(150, 204), (214, 204), (214, 214), (200, 214), (200, 232), (194, 232), (194, 214), (160, 214), (160, 232), (154, 232), (154, 214), (150, 214)], fill=(20, 18, 28), outline=INK)  # grand piano
    d.rectangle((152, 196, 212, 204), fill=(250, 250, 250), outline=INK); [d.line([(x, 196), (x, 203)], fill=(30, 30, 40)) for x in range(158, 212, 6)]
    for x in (60, 96, 124): d.line([(x, 238), (x, 206)], fill=(190, 190, 204), width=2); d.ellipse((x - 4, 200, x + 4, 208), fill=(70, 70, 86), outline=INK)
    for (x, c) in ((20, (255, 120, 160)), (135, (255, 244, 210)), (250, (120, 200, 255))): im = beam(im, x, 135 + (x - 135) // 2, 30, 200, 6, 60, c, .2)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    for _ in range(80): x, y = R.randint(0, W), R.randint(238, 262); d.point((x, y), fill=(255, 214, 120)); d.point((x, y - 1), fill=(255, 140, 60))                                  # lighters in the crowd
    d.rectangle((0, 236, W, 266), fill=(40, 34, 76)); d.line([(0, 236), (W, 236)], fill=INK)
    masonry(d, 0, 266, W, H, base=(70, 66, 118), sh=(46, 42, 82), li=(116, 110, 170), mortar=(24, 20, 48), seed=77); d.line([(0, 265), (W, 265)], fill=INK)
    return im

# ------------------------------------------------------------------ 4 CLUE 4: stadium tour — fireworks, gold "$584M" sign, cash raining, coin stacks
def bg_tour():
    im, d = canvas([(10, 8, 32), (36, 20, 80), (92, 40, 130)])
    twinkles(d, (0, 0, W, 110), 90)
    for (x, y, c) in ((40, 60, (255, 90, 90)), (210, 50, (90, 230, 255)), (130, 30, (255, 220, 90)), (82, 100, (255, 130, 230)), (190, 106, (140, 255, 150))):
        for a in range(0, 360, 20): r = math.radians(a); d.line([(x, y), (x + 20 * math.cos(r), y + 20 * math.sin(r))], fill=c); d.point((x + 24 * math.cos(r), y + 24 * math.sin(r)), fill=WHITE)
    d.polygon([(0, 210), (W, 210), (W, 150), (0, 150)], fill=(56, 42, 96))
    for k in range(5): d.rectangle((0, 152 + k * 10, W, 156 + k * 10), fill=(76, 60, 120))
    for _ in range(300): d.point((R.randint(0, W), R.randint(152, 208)), fill=R.choice([(255, 220, 140), (250, 120, 150), (180, 210, 255), (255, 255, 255), (40, 30, 70)]))
    d.rectangle((44, 84, 226, 142), fill=(18, 10, 32), outline=GOLD, width=3)
    for k in range(18): d.ellipse((44 + k * 10, 80, 49 + k * 10, 85), fill=(255, 240, 160) if k % 2 else GOLD, outline=INK); d.ellipse((44 + k * 10, 139, 49 + k * 10, 144), fill=(255, 240, 160) if k % 2 else GOLD, outline=INK)
    d.text((137, 114), "$584M", font=F(34), fill=GOLD_S, anchor="mm", stroke_width=3, stroke_fill=GOLD_S); d.text((135, 112), "$584M", font=F(34), fill=GOLD_L, anchor="mm")
    d.rectangle((30, 206, 240, 240), fill=(44, 36, 90), outline=INK); d.rectangle((22, 200, 248, 210), fill=(86, 70, 140), outline=INK)
    for x in range(40, 232, 28): d.rectangle((x, 212, x + 16, 236), fill=(30, 24, 60), outline=INK); d.ellipse((x + 3, 216, x + 13, 226), fill=(70, 64, 110))
    for (x, y) in ((14, 252), (240, 250), (254, 256)):
        for k in range(4): d.ellipse((x - 9, y - k * 5, x + 9, y - k * 5 + 7), fill=GOLD, outline=INK); d.line([(x - 6, y - k * 5 + 2), (x + 4, y - k * 5 + 2)], fill=GOLD_L)
    for _ in range(26): x, y = R.randint(0, W), R.randint(0, 230); d.rectangle((x, y, x + 7, y + 4), fill=(110, 190, 120), outline=(60, 120, 70)); d.point((x + 3, y + 2), fill=(200, 240, 200))   # cash raining
    d.rectangle((0, 236, W, 266), fill=(50, 40, 90)); d.line([(0, 236), (W, 236)], fill=INK)
    im = glow(im, 135, 112, 120, (255, 200, 60), .3); d = ImageDraw.Draw(im); d.fontmode = "1"
    masonry(d, 0, 266, W, H, base=(78, 66, 126), sh=(52, 44, 88), li=(124, 112, 176), mortar=(28, 22, 52), seed=79); d.line([(0, 265), (W, 265)], fill=INK)
    for (x, y) in ((40, 300), (200, 320), (120, 350), (60, 390), (210, 400)): d.ellipse((x - 7, y - 5, x + 7, y + 5), fill=GOLD, outline=INK); d.line([(x - 4, y - 1), (x + 3, y - 1)], fill=GOLD_L)
    return im

# ------------------------------------------------------------------ 5 OUTRO: LA hills at night — city grid lights, searchlights, palms, tour bus
def bg_hills():
    im, d = canvas([(8, 4, 24), (36, 14, 60), (110, 30, 90), (230, 100, 100)])
    twinkles(d, (0, 0, W, 130), 110); d.ellipse((30, 40, 62, 72), fill=(252, 246, 220), outline=(236, 228, 196)); d.ellipse((38, 48, 48, 58), fill=(232, 224, 192))
    d.polygon([(0, 200), (50, 160), (120, 188), (190, 150), (W, 180), (W, 236), (0, 236)], fill=(44, 24, 56), outline=INK)
    for y in range(190, 236, 5):
        for x in range(((y // 5) % 2) * 4, W, 8): d.point((x, y), fill=R.choice([(255, 214, 140), (255, 140, 110), (140, 200, 255), (40, 24, 56)]))
    for (x, c) in ((70, (255, 255, 255)), (150, (255, 230, 190)), (230, (200, 230, 255))): im = beam(im, x, x + 60, 236, 0, 8, 44, c, .18)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    palm(d, 36, 266, 130, 6); palm(d, 230, 266, 150, -8)
    d.rectangle((84, 226, 174, 262), fill=(30, 26, 44), outline=INK); d.rectangle((84, 226, 174, 234), fill=(90, 70, 130))                                                                  # tour bus
    for x in range(90, 170, 14): d.rectangle((x, 238, x + 9, 248), fill=(255, 224, 140), outline=INK)
    for x in (100, 156): d.ellipse((x - 8, 254, x + 8, 270), fill=(14, 12, 20), outline=INK)
    d.rectangle((0, 236, W, 266), fill=(42, 30, 64)); d.line([(0, 236), (W, 236)], fill=INK)
    masonry(d, 0, 266, W, H, base=(70, 50, 90), sh=(46, 32, 64), li=(116, 90, 136), mortar=(24, 14, 38), seed=81); d.line([(0, 265), (W, 265)], fill=INK)
    for (px, py, pw) in ((20, 292, 46), (150, 308, 58), (88, 336, 36)): d.ellipse((px, py, px + pw, py + 8), fill=(120, 60, 120), outline=(70, 30, 80)); d.line([(px + 6, py + 3), (px + pw - 6, py + 3)], fill=(255, 190, 150))
    return im

# ------------------------------------------------------------------ mystery guitarist (original design): top hat, long dark curls, shades, vest, skinny jeans, boots, low-slung sunburst guitar
def guitarist(frame=0):
    """0 stand · 1 strum · 2 solo (leans back, neck up) · 3 strum"""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK, SKS, SKL = (232, 192, 160), (196, 150, 120), (248, 218, 190)
    BL, BLS, BLL = (30, 28, 40), (14, 12, 22), (90, 88, 120)
    JN, JNS, JNL = (36, 38, 54), (20, 22, 34), (84, 90, 124)
    HR, HRS, HRL = (26, 20, 24), (10, 8, 12), (92, 70, 80)
    lean = [0, 0, 3, 0][frame]; st = [0, 5, 0, 8][frame]; bob = [0, 1, 0, -1][frame]
    for side, x0 in ((-1, 46), (1, 55)):                                                                              # skinny jeans + boots
        limb(d, (x0, 90), (x0 + side, 126), 8, 6, JN, JNS, JNL); d.line([(x0 + side, 100), (x0 + side, 104)], fill=JNL); d.line([(x0 + side - 1, 112), (x0 + side + 1, 114)], fill=JNS)
        d.rounded_rectangle((x0 + side - 5, 124, x0 + side + 7, 134), 3, fill=(36, 24, 22)); d.rectangle((x0 + side - 5, 132, x0 + side + 7, 135), fill=(12, 8, 8)); d.line([(x0 + side - 3, 126), (x0 + side + 4, 126)], fill=(120, 88, 70))
    d.polygon([(42, 84), (58, 84), (59, 96), (41, 96)], fill=JN); d.rectangle((41, 84, 59, 88), fill=(54, 36, 30)); d.rectangle((47, 83, 53, 89), fill=(210, 186, 110)); d.rectangle((49, 85, 51, 87), fill=(140, 110, 50))   # belt + buckle
    d.polygon([(41, 46 + bob), (59, 46 + bob), (58, 86), (42, 86)], fill=(48, 44, 60)); d.line([(50, 50 + bob), (50, 84)], fill=BLS)                                                              # dark tee
    d.polygon([(40, 46 + bob), (47, 46 + bob), (46, 86), (41, 86)], fill=BL); d.polygon([(60, 46 + bob), (53, 46 + bob), (54, 86), (59, 86)], fill=BL); d.line([(41, 50 + bob), (41, 84)], fill=BLL)   # leather vest
    for y in (60, 70, 80): d.ellipse((44, y, 46, y + 2), fill=(190, 190, 210)); d.ellipse((54, y, 56, y + 2), fill=(190, 190, 210))
    texture(im, (40, 46, 60, 86), [BLL, BLS], 24)
    gx, gy = 52, 88                                                                                                         # low-slung sunburst guitar, neck to the viewer's left
    nx, ny = 10, 66 - lean * 3
    d.polygon([(nx, ny - 3), (gx - 8, gy - 6), (gx - 6, gy), (nx + 2, ny + 2)], fill=(120, 80, 48)); d.line([(nx + 2, ny), (gx - 8, gy - 3)], fill=(206, 160, 104))
    for k in range(1, 8): d.point((nx + k * (gx - 8 - nx) / 8, ny + k * (gy - 4 - ny) / 8 - 1), fill=(236, 226, 200))
    d.polygon([(nx - 6, ny - 6), (nx + 2, ny - 4), (nx + 2, ny + 3), (nx - 6, ny + 1)], fill=(50, 34, 28)); [d.point((nx - 4 + k * 2, ny - 5 + (k % 2)), fill=(220, 220, 230)) for k in range(4)]
    d.polygon([(gx - 10, gy - 9), (gx + 6, gy - 12), (gx + 18, gy - 5), (gx + 19, gy + 7), (gx + 8, gy + 15), (gx - 8, gy + 13), (gx - 13, gy + 3)], fill=(176, 70, 24))
    d.polygon([(gx - 5, gy - 6), (gx + 8, gy - 8), (gx + 14, gy), (gx + 9, gy + 9), (gx - 3, gy + 9), (gx - 7, gy + 2)], fill=(244, 160, 56)); d.ellipse((gx - 1, gy - 3, gx + 8, gy + 5), fill=(255, 214, 110))
    d.line([(gx - 12, gy + 3), (gx - 8, gy - 9)], fill=(250, 244, 226)); d.line([(gx + 8, gy + 15), (gx + 18, gy + 7)], fill=(250, 244, 226))
    d.rectangle((gx + 2, gy - 3, gx + 12, gy - 1), fill=(36, 30, 32)); d.rectangle((gx + 4, gy + 3, gx + 14, gy + 5), fill=(36, 30, 32)); d.line([(gx - 6, gy - 2), (gx + 15, gy + 2)], fill=(232, 232, 240))
    d.line([(48, 44 + bob), (gx + 14, gy + 10)], fill=(40, 28, 24), width=2)                                                 # strap
    limb(d, (41, 49 + bob), (30, 62 - lean), 6, 5, SK, SKS, SKL); limb(d, (30, 62 - lean), (nx + 14, ny + 4), 5, 4, SK, SKS, SKL); hand(d, (nx + 13, ny + 4), SK, SKS, flip=-1)           # fretting arm
    limb(d, (59, 49 + bob), (68, 66), 6, 5, SK, SKS, SKL); limb(d, (68, 66), (gx + 6 + st // 2, gy + 6 + st // 3), 5, 4, SK, SKS, SKL); hand(d, (gx + 7 + st // 2, gy + 7 + st // 3), SK, SKS)   # strumming arm
    hx, hy = 50, 29 + bob
    for sx in (-1, 1):                                                                                                       # long curly hair to the chest
        for k, (cx, cy) in enumerate(((hx + sx * 10, hy - 4), (hx + sx * 12, hy + 4), (hx + sx * 12, hy + 13), (hx + sx * 11, hy + 22), (hx + sx * 12, hy + 30), (hx + sx * 9, hy + 36))): d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=HR); d.point((cx - sx, cy - 1), fill=HRL)
    d.rectangle((47, 38 + bob, 53, 46 + bob), fill=SKS)
    d.ellipse((hx - 8, hy - 12, hx + 8, hy + 12), fill=SK); d.ellipse((hx + 2, hy - 8, hx + 9, hy + 10), fill=SKS); d.ellipse((hx - 6, hy + 1, hx - 2, hy + 7), fill=SKL)
    d.rectangle((hx - 8, hy - 3, hx + 8, hy + 2), fill=(12, 10, 18)); d.line([(hx - 8, hy - 3), (hx + 8, hy - 3)], fill=(110, 110, 150)); d.rectangle((hx - 1, hy - 3, hx + 1, hy), fill=(30, 28, 40))    # dark sunglasses
    d.line([(hx - 6, hy - 2), (hx - 3, hy - 2)], fill=(150, 160, 220)); d.line([(hx + 2, hy - 2), (hx + 5, hy - 2)], fill=(150, 160, 220))
    d.line([(hx, hy + 3), (hx - 1, hy + 6)], fill=SKS); d.point((hx - 1, hy + 7), fill=(160, 108, 96)); d.point((hx + 1, hy + 7), fill=(160, 108, 96))
    d.line([(hx - 3, hy + 9), (hx + 3, hy + 9)], fill=(166, 84, 96))                                                          # calm mouth
    d.ellipse((hx - 11, hy - 14, hx + 11, hy - 3), fill=HR)                                                                   # hair on top / fringe under the hat
    d.polygon([(hx - 9, hy - 6), (hx - 3, hy - 4), (hx - 8, hy + 6)], fill=HR); d.polygon([(hx + 9, hy - 6), (hx + 3, hy - 4), (hx + 8, hy + 6)], fill=HRS)
    d.polygon([(hx - 9, hy - 14), (hx - 8, hy - 25), (hx - 5, hy - 27), (hx + 5, hy - 27), (hx + 8, hy - 25), (hx + 9, hy - 14)], fill=(26, 24, 34))          # tall top hat
    d.polygon([(hx - 7, hy - 25), (hx - 4, hy - 27), (hx - 4, hy - 16), (hx - 8, hy - 16)], fill=(70, 68, 96)); d.rectangle((hx - 9, hy - 19, hx + 9, hy - 15), fill=(150, 40, 54)); d.line([(hx - 8, hy - 18), (hx + 8, hy - 18)], fill=(220, 90, 100))
    d.ellipse((hx - 15, hy - 17, hx + 15, hy - 10), fill=(26, 24, 34)); d.line([(hx - 12, hy - 14), (hx - 4, hy - 16)], fill=(96, 94, 126))
    return outline(im)

def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        p = os.path.join(OUT, f)
        if os.path.isfile(p): os.remove(p)
    bgs = [("HOOK (Sunset Strip)", bg_strip()), ("PISTA 1 · club 1985", bg_club()), ("PISTA 2 · Londres | LA", bg_split()), ("PISTA 3 · Wembley 1992", bg_tribute()), ("PISTA 4 · $584M", bg_tour()), ("CIERRE (colinas)", bg_hills())]
    for i, (t, im) in enumerate(bgs): im.save(os.path.join(OUT, f"fondo_{i}.png"))
    sheet_bgs(bgs, os.path.join(OUT, "parte15_fondos.png"), cols=3)
    A = [guitarist(f) for f in range(4)]; s = 4
    frames = [silhouette(A[0])] + A + [silhouette(A[2])]; tags = ["silueta", "quieto", "rasgueo 1", "solo", "rasgueo 2", "silueta 2"]
    sheet = Image.new("RGB", (6 * 100 * s + 70, 140 * s + 100), (40, 34, 70)); d = ImageDraw.Draw(sheet); d.fontmode = "1"; label(d, 10, 10, "PARTE 15 · ARTISTA MISTERIOSO (100x140, ×4)", 22)
    for k, fr in enumerate(frames):
        x = 10 + k * (100 * s + 10); bg = Image.new("RGBA", fr.size, (90, 80, 140, 255) if k in (0, 5) else (180, 170, 220, 255)); bg.alpha_composite(fr)
        sheet.paste(bg.convert("RGB").resize((100 * s, 140 * s), Image.NEAREST), (x, 50)); label(d, x + 6, 56, tags[k], 18); fr.save(os.path.join(OUT, f"artista_{k}.png"))
    sheet.save(os.path.join(OUT, "parte15_personaje.png")); print("ok", OUT)

if __name__ == "__main__":
    main()

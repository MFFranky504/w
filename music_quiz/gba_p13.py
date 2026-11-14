"""Parte 13 (The Beatles) — GBA-style original pixel art: 6 backgrounds + the mystery bassist + sprite sheets.
Reuses gba_sprites.py helpers. No band name, logo or real record cover is drawn (they would give the answer away).
usage: python3 gba_p13.py  -> sprites/parte13/*.png"""
import math, os, random
from PIL import Image, ImageDraw
from gba_sprites import (W, H, F, INK, WHITE, grad, outline, silhouette, cloud, masonry, ground, star,
                         limb, hand, shoe, texture, label)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte13")
R = random.Random(13)

def bricks(d, x0, y0, x1, y1, base, line):
    d.rectangle((x0, y0, x1, y1), fill=base)
    for y in range(y0, y1, 8):
        for x in range(x0 - ((y // 8) % 2) * 8, x1, 16): d.rectangle((x, y, x + 15, y + 7), outline=line)

# ---------------------------------------------------------------- backgrounds (270x480, character stands on y=266)
def bg_port():
    """HOOK: northern port city at dusk — river, cranes, clock tower, ferry (generic, no names)"""
    im = Image.new("RGB", (W, H), (60, 60, 80)); im.paste(grad(W, 210, [(50, 60, 130), (200, 110, 120), (255, 190, 120)]).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(4): cloud(d, -10 + k * 74, 40 + (k % 2) * 24, 54, (255, 190, 170), (210, 120, 130), (255, 220, 200))
    for (x, w, h) in ((10, 40, 70), (52, 30, 50), (180, 34, 60), (220, 44, 80)): d.rectangle((x, 186 - h, x + w, 186), fill=(80, 70, 100))
    d.rectangle((100, 96, 136, 186), fill=(110, 96, 110), outline=INK); d.rectangle((108, 70, 128, 96), fill=(110, 96, 110), outline=INK)   # clock tower
    d.polygon([(106, 70), (130, 70), (118, 52)], fill=(80, 110, 100), outline=INK); d.ellipse((111, 76, 125, 90), fill=(250, 240, 200), outline=INK)
    d.line([(118, 83), (118, 78)], fill=INK); d.line([(118, 83), (122, 84)], fill=INK)
    for x in (160, 240): d.line([(x, 186), (x, 120)], fill=(60, 50, 70), width=3); d.line([(x - 26, 124), (x + 14, 124)], fill=(60, 50, 70), width=3); d.line([(x - 22, 124), (x - 22, 150)], fill=(60, 50, 70))
    d.rectangle((0, 186, W, 236), fill=(60, 90, 130))
    for k in range(10): y = 190 + k * 5; d.line([(R.randint(0, 150), y), (R.randint(80, 270), y)], fill=(150, 170, 200))
    d.rectangle((30, 206, 96, 218), fill=(250, 250, 250), outline=INK); d.rectangle((44, 196, 80, 206), fill=(220, 60, 60), outline=INK); d.rectangle((58, 186, 64, 196), fill=(30, 30, 30))   # ferry
    d.rectangle((0, 236, W, 266), fill=(110, 100, 110)); d.line([(0, 236), (W, 236)], fill=INK)
    for x in range(10, W, 50): d.rectangle((x, 226, x + 6, 236), fill=(50, 50, 60)); d.rectangle((x - 2, 224, x + 8, 228), fill=(70, 70, 80))   # bollards
    masonry(d, 0, 266, W, H, base=(150, 120, 110), sh=(110, 84, 78), li=(190, 160, 150), mortar=(80, 60, 60), seed=51); d.line([(0, 265), (W, 265)], fill=INK)
    return im

def bg_hamburg():
    """CLUE 1: 1960, a cramped club on a neon-lit street in Hamburg"""
    im = Image.new("RGB", (W, H), (20, 18, 30)); d = ImageDraw.Draw(im); d.fontmode = "1"
    im.paste(grad(W, 266, [(10, 10, 30), (40, 20, 60), (80, 30, 70)]).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    bricks(d, 0, 60, W, 236, (70, 40, 50), (50, 28, 36))
    d.rectangle((70, 120, 200, 236), fill=(20, 14, 24), outline=INK)                                                       # club doorway / stairs down
    for k in range(6): d.line([(80 + k * 4, 236 - k * 16), (190 - k * 4, 236 - k * 16)], fill=(60, 40, 60))
    d.rectangle((60, 86, 210, 112), fill=(10, 8, 18), outline=(255, 90, 170), width=2); d.text((135, 99), "CLUB", font=F(14), fill=(255, 120, 190), anchor="mm")
    for (x, c) in ((14, (90, 230, 255)), (226, (255, 214, 80))): d.rectangle((x, 70, x + 30, 140), fill=(10, 8, 18), outline=c, width=2); [d.line([(x + 6, y), (x + 24, y)], fill=c) for y in range(80, 136, 10)]
    d.rectangle((0, 236, W, 266), fill=(50, 50, 64)); d.line([(0, 236), (W, 236)], fill=INK)
    for y in range(240, 266, 6):
        for x in range(-((y // 6) % 2) * 6, W, 12): d.rectangle((x, y, x + 10, y + 4), fill=(66, 66, 82))
    d.rectangle((210, 196, 236, 236), fill=(250, 240, 220), outline=INK); d.text((223, 208), "48", font=F(11), fill=INK, anchor="mm"); d.text((223, 222), "NOCHES", font=F(6), fill=INK, anchor="mm")   # gig poster
    d.rectangle((22, 210, 50, 236), fill=(60, 40, 30), outline=INK); d.ellipse((24, 200, 48, 214), fill=(220, 180, 120), outline=INK)   # beer crate / barrel
    masonry(d, 0, 266, W, H, base=(80, 80, 100), sh=(56, 56, 74), li=(110, 110, 130), mortar=(36, 36, 50), seed=52); d.line([(0, 265), (W, 265)], fill=INK)
    return im

def bg_fete():
    """CLUE 2: a skiffle group named after a school song — church fête stage: washboard, tea-chest bass, bunting"""
    im = Image.new("RGB", (W, H), (90, 160, 90)); im.paste(grad(W, 200, [(110, 170, 240), (190, 220, 250)]).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(4): cloud(d, -10 + k * 74, 30 + (k % 2) * 22, 54, (255, 255, 255), (210, 225, 245), (255, 255, 255))
    d.rectangle((150, 70, 240, 190), fill=(190, 170, 150), outline=INK); d.polygon([(146, 70), (244, 70), (195, 30)], fill=(120, 90, 80), outline=INK)   # church
    d.rectangle((186, 120, 204, 190), fill=(90, 60, 50), outline=INK); d.ellipse((186, 110, 204, 128), fill=(90, 60, 50), outline=INK)
    d.rectangle((160, 90, 176, 110), fill=(150, 200, 230), outline=INK); d.rectangle((214, 90, 230, 110), fill=(150, 200, 230), outline=INK)
    for k in range(14):                                                                                                     # bunting
        x = 4 + k * 19; y = 20 + 8 * math.sin(math.pi * k / 13); d.polygon([(x, y), (x + 14, y), (x + 7, y + 12)], fill=[(230, 60, 60), (250, 250, 250), (60, 110, 220)][k % 3], outline=INK)
    d.line([(0, 20), (W, 20)], fill=(120, 100, 80))
    d.rectangle((0, 190, W, 266), fill=(110, 180, 90)); d.line([(0, 190), (W, 190)], fill=INK)
    d.rectangle((10, 200, 140, 236), fill=(170, 120, 70), outline=INK)                                                       # little wooden stage
    for x in range(10, 140, 13): d.line([(x, 200), (x, 236)], fill=(140, 96, 56))
    d.rectangle((18, 170, 46, 200), fill=(180, 140, 90), outline=INK); d.line([(32, 170), (32, 150)], fill=(90, 60, 40), width=2); d.line([(32, 150), (46, 200)], fill=(230, 230, 230))   # tea-chest bass
    d.rectangle((90, 172, 108, 200), fill=(200, 200, 210), outline=INK); [d.line([(92, y), (106, y)], fill=(150, 150, 164)) for y in range(176, 198, 3)]   # washboard
    d.rectangle((88, 168, 110, 174), fill=(150, 100, 60), outline=INK)
    d.rectangle((210, 210, 260, 236), fill=(250, 250, 240), outline=INK); d.text((235, 222), "TÉ 2p", font=F(7), fill=INK, anchor="mm")   # tea stall
    d.polygon([(206, 210), (264, 210), (258, 200), (212, 200)], fill=(230, 60, 60), outline=INK)
    ground(d, 266, "grass")
    return im

def bg_audition():
    """CLUE 3: 1962, a record-company audition room — tape machine, desk, a stamped rejection letter"""
    im = Image.new("RGB", (W, H), (80, 70, 60)); d = ImageDraw.Draw(im); d.fontmode = "1"
    d.rectangle((0, 0, W, 266), fill=(150, 140, 120))
    for x in range(0, W, 30): d.rectangle((x, 0, x + 28, 150), fill=(160, 150, 130), outline=(130, 120, 104))              # wood panelling
    d.rectangle((20, 40, 100, 110), fill=(220, 230, 240), outline=INK, width=2); d.line([(60, 40), (60, 110)], fill=INK)   # window: winter snow
    for _ in range(30): d.point((R.randint(22, 98), R.randint(42, 108)), fill=WHITE)
    d.rectangle((120, 40, 160, 80), fill=(250, 250, 240), outline=INK); d.text((140, 52), "ENE", font=F(9), fill=(200, 40, 40), anchor="mm"); d.text((140, 68), "1962", font=F(10), fill=INK, anchor="mm")   # calendar
    d.rectangle((180, 40, 256, 116), fill=(70, 70, 80), outline=INK)                                                         # tape machine
    for cx in (200, 236): d.ellipse((cx - 14, 50, cx + 14, 78), fill=(40, 40, 46), outline=INK); d.ellipse((cx - 4, 60, cx + 4, 68), fill=(200, 200, 210))
    d.line([(200, 78), (236, 78)], fill=(120, 80, 50), width=2); [d.ellipse((190 + k * 14, 96, 198 + k * 14, 104), fill=[(220, 60, 60), (240, 240, 240), (240, 240, 240), (60, 200, 90), (240, 240, 240)][k], outline=INK) for k in range(5)]
    d.rectangle((0, 150, W, 266), fill=(120, 40, 40)); d.line([(0, 150), (W, 150)], fill=INK)
    for y in range(156, 266, 10): d.line([(0, y), (W, y)], fill=(100, 30, 30))
    d.rectangle((150, 190, 262, 200), fill=(110, 70, 40), outline=INK); d.rectangle((156, 200, 162, 262), fill=(90, 56, 30)); d.rectangle((250, 200, 256, 262), fill=(90, 56, 30))   # desk
    d.rectangle((170, 176, 214, 190), fill=(250, 250, 240), outline=INK); [d.line([(174, y), (206, y)], fill=(150, 150, 150)) for y in (180, 183, 186)]   # letter
    d.rectangle((196, 172, 222, 184), outline=(220, 30, 40), width=2); d.text((209, 178), "NO", font=F(8), fill=(220, 30, 40), anchor="mm")
    d.rectangle((226, 174, 240, 190), fill=(240, 240, 240), outline=INK); d.ellipse((228, 170, 238, 176), fill=(240, 240, 240), outline=INK)   # tea cup
    d.line([(60, 266), (60, 196)], fill=(180, 180, 190), width=2); d.ellipse((54, 186, 66, 198), fill=(60, 60, 70), outline=INK)   # mic stand
    ground(d, 266, "wood")
    return im

def bg_rooftop():
    """CLUE 4: last public concert on the roof of their London office, 1969 — grey sky, chimneys, amps, wind"""
    im = Image.new("RGB", (W, H), (100, 100, 110)); im.paste(grad(W, 210, [(140, 150, 170), (190, 196, 206), (210, 214, 220)]).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for k in range(6): cloud(d, -10 + k * 50, 30 + (k % 3) * 30, 50, (230, 232, 238), (180, 186, 200), (250, 250, 252))
    x = 0
    while x < W: w = R.randint(18, 34); h = R.randint(30, 80); d.rectangle((x, 200 - h, x + w, 200), fill=(150, 140, 140), outline=(120, 110, 112)); x += w + 2   # London rooftops
    for x in range(10, W, 46): d.rectangle((x, 150, x + 10, 200), fill=(150, 90, 70), outline=INK); [d.rectangle((x + 1 + k * 3, 144, x + 3 + k * 3, 150), fill=(170, 110, 80), outline=INK) for k in range(3)]   # chimney stacks
    d.rectangle((0, 200, W, 266), fill=(120, 120, 128)); d.line([(0, 200), (W, 200)], fill=INK)                              # roof deck planks
    for x in range(0, W, 18): d.line([(x, 200), (x, 266)], fill=(100, 100, 108))
    for (x0, x1) in ((14, 54), (216, 256)):                                                                                  # amps
        d.rectangle((x0, 214, x1, 260), fill=(40, 36, 44), outline=INK); d.rectangle((x0 + 3, 222, x1 - 3, 256), fill=(70, 64, 74)); d.rectangle((x0 + 2, 216, x1 - 2, 220), fill=(200, 190, 170))
    d.rectangle((112, 228, 150, 262), fill=(40, 40, 46), outline=INK); d.ellipse((116, 232, 146, 260), fill=(240, 230, 210), outline=INK)   # drum kit
    d.ellipse((96, 212, 120, 218), fill=(240, 210, 80), outline=INK); d.line([(108, 218), (108, 262)], fill=(150, 150, 160))
    d.rectangle((0, 196, W, 200), fill=(90, 90, 98))                                                                          # parapet
    d.pieslice((236, 186, 256, 210), 180, 360, fill=(20, 24, 50), outline=INK); d.rectangle((244, 182, 248, 188), fill=(200, 200, 210))   # police helmet peeking over
    ground(d, 266, "wood")
    return im

def bg_crossing():
    """OUTRO: a London street at night with a zebra crossing and a parked white beetle-shaped car"""
    im = Image.new("RGB", (W, H), (30, 30, 46)); im.paste(grad(W, 210, [(14, 16, 44), (40, 44, 90), (90, 80, 120)]).convert("RGB"), (0, 0)); d = ImageDraw.Draw(im); d.fontmode = "1"
    for _ in range(50): d.point((R.randint(0, W), R.randint(0, 150)), fill=(255, 255, 255))
    d.ellipse((200, 30, 230, 60), fill=(250, 246, 220))
    for (x, w, h) in ((0, 60, 120), (64, 50, 90), (180, 90, 110)):
        d.rectangle((x, 210 - h, x + w, 210), fill=(70, 60, 80), outline=INK)
        for wy in range(210 - h + 10, 204, 14):
            for wx in range(x + 6, x + w - 8, 12): d.rectangle((wx, wy, wx + 6, wy + 8), fill=(255, 214, 120) if R.random() < .5 else (40, 36, 60))
    for x in (130, 160): d.line([(x, 210), (x, 160)], fill=(120, 120, 130), width=2)
    d.rectangle((0, 210, W, 266), fill=(50, 50, 60)); d.line([(0, 210), (W, 210)], fill=INK)
    for k in range(6): x = 60 + k * 26; d.rectangle((x, 224, x + 16, 258), fill=(240, 240, 240))                              # zebra crossing
    for x in (44, 226): d.line([(x, 266), (x, 196)], fill=(40, 40, 44), width=3); d.ellipse((x - 6, 186, x + 6, 198), fill=(255, 180, 60), outline=INK)   # belisha beacons
    car = (190, 214); d.pieslice((car[0], car[1] - 10, car[0] + 50, car[1] + 30), 180, 360, fill=(240, 240, 236), outline=INK)   # beetle-shaped car
    d.rectangle((car[0], car[1] + 10, car[0] + 50, car[1] + 16), fill=(240, 240, 236), outline=INK); d.pieslice((car[0] + 14, car[1] - 6, car[0] + 36, car[1] + 14), 180, 360, fill=(150, 190, 220))
    for wx in (car[0] + 10, car[0] + 40): d.ellipse((wx - 6, car[1] + 12, wx + 6, car[1] + 24), fill=(30, 30, 36), outline=INK)
    ground(d, 266, "stone")
    return im

# ---------------------------------------------------------------- mystery bassist (original design): mop-top, collarless suit, violin-shaped bass held left-handed
def mopbass(frame=0):
    """0 stand · 1-3 head shake + strum"""
    im = Image.new("RGBA", (100, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK, SKS, SKL = (246, 212, 186), (214, 172, 144), (254, 230, 206)
    SU, SUS, SUL = (150, 150, 158), (110, 110, 120), (190, 190, 198)          # grey collarless suit
    HA, HAS, HAL = (70, 46, 30), (46, 30, 20), (110, 74, 48)                  # brown mop-top
    shake = [0, -2, 0, 2][frame]; st = [0, 4, 8, 4][frame]
    for side, x0 in ((-1, 45), (1, 55)):                                       # slim legs + pointed boots
        limb(d, (x0, 92), (x0 + side, 130), 9, 7, SU, SUS, SUL)
        shoe(d, x0 + side * 2, 130, (30, 26, 32), (60, 56, 64), (20, 18, 24), side)
    d.polygon([(40, 84), (60, 84), (61, 94), (39, 94)], fill=SU)
    d.polygon([(39, 46), (61, 46), (62, 88), (38, 88)], fill=SU); d.line([(60, 48), (61, 86)], fill=SUS, width=3); d.line([(40, 48), (39, 86)], fill=SUL)
    d.polygon([(45, 44), (55, 44), (52, 54), (48, 54)], fill=(248, 248, 250)); d.line([(50, 46), (50, 70)], fill=(20, 20, 24), width=2)   # white shirt + thin black tie
    d.line([(44, 46), (50, 60)], fill=SUS); d.line([(56, 46), (50, 60)], fill=SUS)                                                       # collarless neckline
    for y in (64, 74): d.ellipse((47, y, 49, y + 2), fill=(40, 40, 46))
    texture(im, (38, 46, 62, 88), [SUL, SUS], 26)
    gx, gy = 46, 82                                                             # violin-shaped bass: body on viewer's left of the neck end? (left-handed: neck to viewer's right)
    d.polygon([(gx + 6, gy - 6), (92, gy - 26), (94, gy - 22), (gx + 8, gy)], fill=(70, 46, 30)); d.line([(gx + 8, gy - 4), (92, gy - 24)], fill=(200, 180, 140))
    d.polygon([(88, gy - 30), (98, gy - 28), (98, gy - 20), (90, gy - 22)], fill=(40, 26, 18))
    d.ellipse((gx - 16, gy - 16, gx + 4, gy + 2), fill=(170, 80, 30)); d.ellipse((gx - 18, gy - 4, gx + 6, gy + 18), fill=(170, 80, 30))   # violin body (two bouts)
    d.ellipse((gx - 13, gy - 12, gx - 2, gy - 1), fill=(220, 140, 60)); d.ellipse((gx - 14, gy + 1, gx + 2, gy + 15), fill=(220, 140, 60))
    d.rectangle((gx - 10, gy - 2, gx, gy + 2), fill=(30, 26, 30)); d.rectangle((gx - 12, gy + 6, gx - 2, gy + 8), fill=(220, 220, 230))
    limb(d, (61, 48), (74, 62), 8, 7, SU, SUS, SUL); limb(d, (74, 62), (84, gy - 22), 7, 6, SU, SUS); hand(d, (86, gy - 23), SK, SKS)   # fretting hand on the neck (right side)
    limb(d, (39, 48), (30, 64), 8, 7, SU, SUS, SUL); limb(d, (30, 64), (gx - 6 + st // 2, gy - 2 + st // 3), 7, 6, SU, SUS); hand(d, (gx - 6 + st // 2, gy + st // 3), SK, SKS, flip=-1)
    hx, hy = 50 + shake, 26
    d.rectangle((46, 36, 54, 46), fill=SKS)
    d.ellipse((hx - 10, hy - 14, hx + 10, hy + 14), fill=SK); d.ellipse((hx + 2, hy - 10, hx + 11, hy + 12), fill=SKS); d.ellipse((hx - 8, hy, hx - 3, hy + 6), fill=SKL)
    for ex in (hx - 6, hx + 2): d.rectangle((ex, hy - 1, ex + 3, hy + 1), fill=(244, 240, 234)); d.rectangle((ex + 1, hy - 1, ex + 2, hy + 1), fill=(40, 26, 20))
    d.line([(hx - 7, hy - 4), (hx - 2, hy - 5)], fill=HAS); d.line([(hx + 2, hy - 5), (hx + 7, hy - 4)], fill=HAS)
    d.ellipse((hx - 3, hy + 7, hx + 3, hy + 11), fill=(150, 60, 70))                                                            # singing "ooh"
    d.ellipse((hx - 14, hy - 20, hx + 14, hy + 4), fill=HA)                                                                      # mop-top: round, full fringe down to the brows, covers the ears
    d.polygon([(hx - 14, hy - 8), (hx - 12, hy + 8), (hx - 8, hy + 10), (hx - 8, hy - 4)], fill=HA); d.polygon([(hx + 14, hy - 8), (hx + 12, hy + 8), (hx + 8, hy + 10), (hx + 8, hy - 4)], fill=HAS)
    for k in range(-10, 11, 3): d.line([(hx + k, hy - 6), (hx + k + 1, hy - 3)], fill=HAS)                                    # fringe strands
    d.line([(hx - 9, hy - 17), (hx - 2, hy - 19)], fill=HAL); d.line([(hx - 12, hy - 10), (hx - 11, hy - 2)], fill=HAL)
    return outline(im)

# ---------------------------------------------------------------- sheets
def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    bgs = [("HOOK (puerto al atardecer)", bg_port()), ("PISTA 1 · Hamburgo, 1960", bg_hamburg()), ("PISTA 2 · grupo de skiffle", bg_fete()),
           ("PISTA 3 · la audición de 1962", bg_audition()), ("PISTA 4 · la azotea", bg_rooftop()), ("CIERRE (calle de noche)", bg_crossing())]
    s = 2; cw, ch = W * s, H * s; sheet = Image.new("RGB", (3 * cw + 40, 2 * ch + 120), (16, 12, 30)); d = ImageDraw.Draw(sheet); d.fontmode = "1"
    label(d, 10, 10, "PARTE 13 · FONDOS (270x480, ×2) · estilo GBA original", 22)
    for i, (t, im) in enumerate(bgs):
        x, y = 10 + (i % 3) * (cw + 10), 50 + (i // 3) * (ch + 34); sheet.paste(im.resize((cw, ch), Image.NEAREST), (x, y)); label(d, x, y + ch + 4, t, 16)
        im.save(os.path.join(OUT, f"fondo_{i}.png"))
    sheet.save(os.path.join(OUT, "parte13_fondos.png"))
    A = [mopbass(f) for f in range(4)]; s = 4
    frames = [silhouette(A[0])] + A + [silhouette(A[2])]; tags = ["silueta", "quieto", "toque 1", "toque 2", "toque 3", "silueta 2"]
    sheet = Image.new("RGB", (6 * 100 * s + 70, 140 * s + 100), (40, 34, 70)); d = ImageDraw.Draw(sheet); d.fontmode = "1"
    label(d, 10, 10, "PARTE 13 · ARTISTA MISTERIOSO (100x140, ×4)", 22)
    for k, fr in enumerate(frames):
        x = 10 + k * (100 * s + 10); bg = Image.new("RGBA", fr.size, (90, 80, 140, 255) if k in (0, 5) else (180, 170, 220, 255)); bg.alpha_composite(fr)
        sheet.paste(bg.convert("RGB").resize((100 * s, 140 * s), Image.NEAREST), (x, 50)); label(d, x + 6, 56, tags[k], 18)
        fr.save(os.path.join(OUT, f"artista_{k}.png"))
    sheet.save(os.path.join(OUT, "parte13_personaje.png")); print("ok", OUT)

if __name__ == "__main__":
    main()

"""Fondos RPG a 360x640: sala con TV, ventana con luz, alfombra, tableros; efectos de luz."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 360, 640
OL = (38, 24, 56)


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def _font(size):
    from .engine import pf
    return pf(size)


def txt(d, xy, s, size, fill, outline=OL, anchor="mm"):
    d.fontmode = "1"
    f = _font(size)
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        d.text((x + dx, y + dy), s, font=f, fill=outline, anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def _room_base(t, night=False):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    wall, wall2 = (236, 168, 150), (244, 184, 160)
    # papel tapiz rayado con puntos
    for x in range(0, W, 24):
        d.rectangle([x, 0, x + 11, 330], fill=wall)
        d.rectangle([x + 12, 0, x + 23, 330], fill=wall2)
    for y in range(8, 330, 22):
        for x in range(6, W, 24):
            d.rectangle([x, y, x + 1, y + 1], fill=sh(wall, 0.9))
    d.rectangle([0, 0, W, 12], fill=(150, 90, 100)); d.rectangle([0, 12, W, 15], fill=(110, 60, 80))
    # zócalo de madera
    d.rectangle([0, 250, W, 340], fill=(168, 104, 72))
    for x in range(0, W, 30):
        d.rectangle([x, 262, x + 25, 330], outline=(128, 74, 56), width=2)
        d.rectangle([x + 3, 265, x + 5, 327], fill=(190, 124, 88))
    d.rectangle([0, 246, W, 252], fill=(210, 150, 100)); d.rectangle([0, 252, W, 255], fill=(120, 70, 54))
    d.rectangle([0, 336, W, 342], fill=(104, 60, 50))
    # piso de madera
    d.rectangle([0, 342, W, H], fill=(190, 120, 84))
    rnd = random.Random(7)
    y = 342
    while y < H:
        hh = 16 + (int(y) * 7) % 8
        d.rectangle([0, y, W, y + 1], fill=(120, 72, 56))
        for x0 in range(-(y * 13 % 70), W, 70):
            d.rectangle([x0, y, x0 + 1, y + hh], fill=(130, 80, 60))
            d.rectangle([x0 + 20, y + 5, x0 + 45, y + 6], fill=(200, 134, 96))
        y += hh
    # alfombra rosa con borde turquesa
    d.ellipse([10, 372, 350, 520], fill=(60, 200, 190), outline=OL, width=3)
    d.ellipse([22, 382, 338, 508], fill=(244, 130, 170))
    d.ellipse([40, 392, 320, 496], outline=(255, 170, 200), width=3)
    # ventana con cortinas
    d.rectangle([18, 58, 118, 206], fill=OL)
    sky = (110, 180, 255) if not night else (14, 18, 60)
    for i in range(6):
        d.rectangle([22, 62 + i * 23, 114, 85 + i * 23], fill=sh(sky, 0.92 + 0.04 * i))
    if night:
        d.ellipse([84, 76, 104, 96], fill=(255, 244, 190))
        for sx, sy in ((36, 80), (60, 110), (90, 130), (44, 150), (100, 160)):
            d.rectangle([sx, sy, sx + 1, sy + 1], fill=(255, 255, 255))
    else:
        d.ellipse([84, 72, 106, 94], fill=(255, 236, 120))
        cx = 22 + int(t * 5) % 120 - 30
        for ox, oy, w in ((0, 120, 36), (10, 112, 22), (-8, 126, 28)):
            d.rounded_rectangle([cx + ox, oy, cx + ox + w, oy + 12], radius=6, fill=(255, 255, 255))
    d.rectangle([66, 62, 70, 202], fill=(236, 220, 210)); d.rectangle([22, 132, 114, 136], fill=(236, 220, 210))
    d.rectangle([14, 204, 122, 214], fill=(236, 220, 210)); d.rectangle([14, 212, 122, 216], fill=(150, 110, 90))
    d.polygon([(8, 50), (36, 50), (46, 200), (8, 200)], fill=(220, 90, 140)); d.polygon([(8, 50), (14, 50), (18, 200), (8, 200)], fill=(250, 130, 170))
    d.polygon([(128, 50), (100, 50), (90, 200), (128, 200)], fill=(220, 90, 140)); d.polygon([(128, 50), (122, 50), (118, 200), (128, 200)], fill=(190, 70, 120))
    d.rectangle([4, 44, 132, 52], fill=(120, 70, 60))
    # póster de corazón y de juego
    d.rectangle([276, 60, 346, 140], fill=OL); d.rectangle([279, 63, 343, 137], fill=(250, 200, 215))
    for yy, ww in ((84, 26), (94, 34), (104, 26), (114, 16)):
        d.rectangle([311 - ww // 2, yy, 311 + ww // 2, yy + 8], fill=(232, 70, 110))
    d.ellipse([293, 76, 311, 94], fill=(232, 70, 110)); d.ellipse([311, 76, 329, 94], fill=(232, 70, 110))
    d.rectangle([286, 156, 338, 218], fill=OL); d.rectangle([289, 159, 335, 215], fill=(60, 110, 200))
    d.rectangle([298, 170, 326, 176], fill=(255, 230, 90)); d.rectangle([306, 176, 318, 204], fill=(255, 255, 255))
    # planta
    d.rectangle([300, 222, 334, 248], fill=(210, 110, 80), outline=OL); d.rectangle([300, 222, 334, 228], fill=(240, 150, 110))
    for lx, ly, lw in ((306, 196, 8), (316, 186, 8), (326, 198, 8), (312, 206, 6)):
        d.polygon([(lx + 4, 224), (lx, ly), (lx + lw, ly + 6)], fill=(70, 190, 110), outline=OL)
    # mueble de la TV
    d.rectangle([110, 244, 270, 254], fill=(210, 150, 100), outline=OL)
    d.rectangle([116, 254, 264, 340], fill=(150, 90, 66), outline=OL, width=2)
    d.rectangle([124, 266, 190, 330], outline=(110, 62, 50), width=2); d.rectangle([194, 266, 256, 330], outline=(110, 62, 50), width=2)
    d.rectangle([154, 296, 160, 302], fill=(255, 220, 120)); d.rectangle([220, 296, 226, 302], fill=(255, 220, 120))
    return img


def tv(img, t, score, verdict, label="K / D", night=False, big=None):
    d = ImageDraw.Draw(img)
    d.rectangle([104, 96, 258, 244], fill=OL); d.rectangle([108, 100, 254, 240], fill=(70, 74, 100))
    d.rectangle([108, 100, 254, 104], fill=(120, 126, 160))
    good = score[0] > score[1]
    scr = (24, 110, 70) if good else (110, 30, 50)
    if night:
        scr = (40, 90, 170)
    d.rectangle([114, 108, 248, 228], fill=scr)
    for y in range(108, 228, 4):
        d.rectangle([114, y, 248, y], fill=sh(scr, 0.82))
    d.rectangle([114, 108, 248, 140], fill=sh(scr, 1.2))
    col = (130, 255, 160) if good else (255, 130, 130)
    if night:
        col = (255, 235, 120)
    txt(d, (181, 124), verdict, 18, col)
    txt(d, (181, 152), label, 14, (230, 236, 255))
    txt(d, (181, 188), big if big is not None else f"{score[0]} - {score[1]}", 38 if big is None or len(big) < 7 else 30, (255, 255, 255))
    for i in range(6):   # barrita de vida estilo juego
        d.rectangle([124 + i * 8, 214, 129 + i * 8, 220], fill=col if (i < 4 or not good) else sh(col, .4))
    if int(t * 3) % 2 == 0:
        d.rectangle([118, 112, 124, 118], fill=col)
    # mini-juego animado: héroe azul vs. enemigos rojos
    d.rectangle([114, 226, 248, 228], fill=sh(scr, 0.6))
    hx = 130 + int(abs(math.sin(t * 2.2)) * 90)
    d.rectangle([hx, 222, hx + 6, 228], fill=(90, 160, 255))
    for i in range(3):
        ex = 124 + int((t * (30 + 12 * i) + i * 47) % 118)
        if good and int(t * 4 + i) % 5 == 0:
            d.rectangle([ex - 2, 220, ex + 8, 228], fill=(255, 230, 120))
        else:
            d.rectangle([ex, 222, ex + 5, 228], fill=(240, 90, 90))
    d.rectangle([116, 110, 130, 114], fill=(255, 255, 255, 60)) if False else None
    d.polygon([(118, 112), (150, 112), (126, 164), (118, 164)], fill=None) if False else None


def glow(img, box, color, strength=140, blur=22):
    layer = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(layer).rectangle(box, fill=tuple(int(c * strength / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(img.convert("RGB"), dtype="int16") +
                                                      __import__("numpy").asarray(layer, dtype="int16"), 0, 255).astype("uint8"))


def light_shaft(img, strength=30):
    """Luz diagonal que entra por la ventana."""
    l = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.polygon([(20, 206), (118, 206), (270, 600), (120, 600)], fill=(255, 245, 200, strength))
    d.polygon([(66, 206), (84, 206), (180, 600), (150, 600)], fill=(255, 250, 220, strength // 2))
    img.alpha_composite(l.filter(ImageFilter.GaussianBlur(4)))


def night_grade(img, amount=0.55):
    tint = Image.new("RGBA", img.size, (24, 30, 90, int(255 * amount)))
    img.alpha_composite(tint)


def sparkles(img, t, cx, cy, n=5, spread=70):
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = i * 2.4 + 0.5
        x = cx + math.cos(a) * spread * (0.6 + 0.4 * (i % 2)); y = cy + math.sin(a * 1.3) * spread * 0.9
        if abs(x - cx) < 42 and abs(y - cy) < 75:   # no tapar la cara
            continue
        r = 2 + int((math.sin(t * 6 + i * 1.7) + 1) * 2.2)
        c = (255, 255, 255, 255)
        d.rectangle([x - r, y - 1, x + r, y + 1], fill=c); d.rectangle([x - 1, y - r, x + 1, y + r], fill=c)


def cans(img, n):
    d = ImageDraw.Draw(img)
    cols = [(70, 230, 130), (255, 90, 100), (90, 190, 255)]
    for i in range(n):
        row, col = divmod(i, 9)
        x = 118 + col * 14
        y = 232 - row * 16
        d.rectangle([x, y, x + 10, y + 14], fill=OL)
        d.rectangle([x + 1, y + 1, x + 9, y + 13], fill=cols[i % 3]); d.rectangle([x + 2, y + 1, x + 4, y + 13], fill=(255, 255, 255))
        d.rectangle([x + 1, y + 1, x + 9, y + 3], fill=(200, 200, 215))


def confetti(img, t, n=60):
    d = ImageDraw.Draw(img)
    cols = [(255, 220, 80), (255, 90, 130), (90, 220, 255), (150, 255, 150)]
    for i in range(n):
        x = (i * 71) % W
        y = int((t * 130 + i * 53) % 560) + 20
        d.rectangle([x, y, x + 4, y + 6], fill=cols[i % 4])


DY = 44  # sube toda la escena para que los personajes queden sobre la zona segura


def grade(img, sat=1.18, bright=1.03):
    """Paleta apagada tipo JRPG: baja saturación y brillo, sombras frías."""
    from PIL import ImageEnhance
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(img.convert("RGB")).enhance(sat)).enhance(bright)
    a = __import__("numpy").asarray(rgb, dtype="float32") * __import__("numpy").array([1.0, 1.0, 1.02], dtype="float32")
    return Image.fromarray(a.clip(0, 255).astype("uint8")).convert("RGBA")


def _street_base(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    top, bot = (74, 62, 140), (252, 156, 112)
    for y in range(0, 345, 3):
        u = y / 345
        d.rectangle([0, y, W, y + 3], fill=tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3)))
    d.ellipse([240, 226, 320, 306], fill=(255, 214, 140))
    rnd = random.Random(5)
    x = -10
    while x < W:     # edificios lejanos
        w, h = rnd.randint(40, 70), rnd.randint(110, 190)
        d.rectangle([x, 340 - h, x + w, 340], fill=(92, 78, 150)); x += w - 4
    cols = [(240, 152, 64), (212, 84, 120), (96, 130, 216), (244, 204, 96), (80, 180, 150)]
    x, k = -20, 0
    while x < W:     # edificios cercanos con ventanas encendidas
        w, h = rnd.randint(70, 92), rnd.randint(150, 230)
        c = cols[k % 5]; k += 1
        d.rectangle([x, 346 - h, x + w, 346], fill=OL); d.rectangle([x + 2, 348 - h, x + w - 2, 346], fill=c)
        d.rectangle([x + w - 12, 348 - h, x + w - 2, 346], fill=sh(c, 0.8))
        for wy in range(350 - h + 12, 330, 24):
            for wx in range(x + 10, x + w - 14, 20):
                lit = (wx * 7 + wy * 3) % 5 != 0
                d.rectangle([wx, wy, wx + 9, wy + 12], fill=(255, 232, 140) if lit else sh(c, 0.55), outline=OL)
        x += w + 2
    d.line([0, 150, W, 178], fill=OL, width=2)   # banderines
    for i in range(0, W, 24):
        yy = 150 + (28 * i / W)
        d.polygon([(i, yy), (i + 14, yy), (i + 7, yy + 14)], fill=cols[(i // 24) % 5])
    d.rectangle([0, 346, W, 420], fill=(176, 170, 190)); d.rectangle([0, 346, W, 352], fill=(210, 206, 220))
    for xx in range(0, W, 48):
        d.rectangle([xx, 352, xx + 1, 420], fill=(140, 134, 158))
    d.rectangle([0, 420, W, 428], fill=(120, 116, 136)); d.rectangle([0, 428, W, H], fill=(64, 64, 82))
    for xx in range(0, W, 70):
        d.rectangle([xx, 540, xx + 40, 546], fill=(236, 200, 80))
    d.rectangle([54, 200, 60, 346], fill=OL); d.rectangle([40, 196, 74, 206], fill=OL)   # farola
    d.ellipse([44, 198, 70, 212], fill=(255, 238, 170))
    return img


def _bedroom_base(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 340], fill=(44, 48, 100))
    for x in range(0, W, 30):
        d.rectangle([x, 0, x + 14, 340], fill=(50, 54, 112))
    hue = [(0, 255, 255), (255, 60, 200), (120, 90, 255)][int(t * 1.5) % 3]
    d.rectangle([0, 10, W, 17], fill=hue)                                       # tira LED
    d.rectangle([18, 58, 118, 206], fill=OL); d.rectangle([22, 62, 114, 202], fill=(14, 18, 60))
    d.ellipse([80, 78, 104, 102], fill=(250, 240, 190))
    for sx, sy in ((36, 80), (60, 110), (46, 150), (96, 140)):
        d.rectangle([sx, sy, sx + 1, sy + 1], fill=(255, 255, 255))
    d.rectangle([66, 62, 70, 202], fill=(70, 70, 110))
    d.rectangle([276, 52, 346, 132], fill=OL); d.rectangle([279, 55, 343, 129], fill=(180, 50, 70))
    d.polygon([(290, 118), (311, 66), (332, 118)], fill=(255, 210, 90))
    d.rectangle([286, 150, 338, 212], fill=OL); d.rectangle([289, 153, 335, 209], fill=(40, 150, 140))
    d.ellipse([300, 166, 324, 190], fill=(250, 230, 120))
    d.rectangle([270, 226, 350, 232], fill=(140, 96, 70))
    for tx in (278, 300, 322):
        d.rectangle([tx, 206, tx + 12, 226], fill=(240, 196, 70), outline=OL)
    d.rectangle([60, 244, 300, 258], fill=(150, 104, 76), outline=OL)              # escritorio
    d.rectangle([66, 258, 294, 340], fill=(112, 76, 60), outline=OL, width=2)
    for dx in (80, 190):
        d.rectangle([dx, 270, dx + 90, 326], outline=(80, 52, 44), width=2); d.rectangle([dx + 38, 294, dx + 52, 300], fill=(240, 200, 100))
    d.rectangle([132, 238, 232, 244], fill=(30, 30, 44))                           # teclado RGB
    for i in range(10):
        d.rectangle([134 + i * 10, 239, 140 + i * 10, 243], fill=[(255, 80, 120), (80, 220, 255), (255, 230, 90)][(i + int(t * 6)) % 3])
    d.rectangle([250, 190, 292, 244], fill=OL); d.rectangle([254, 194, 288, 240], fill=(50, 54, 80))
    d.ellipse([260, 204, 282, 226], fill=hue)
    d.rectangle([0, 340, W, H], fill=(60, 44, 74))
    for y in range(352, H, 22):
        d.rectangle([0, y, W, y + 1], fill=(50, 36, 64))
    d.ellipse([-20, 352, 70, 410], fill=(120, 80, 170), outline=OL, width=3)       # puf
    d.ellipse([60, 372, 330, 520], fill=(40, 56, 110), outline=OL, width=3)        # alfombra
    return img


def _arcade_base(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 340], fill=(24, 22, 60))
    for y in range(0, 340, 18):
        for x in range(-(y // 18 % 2) * 20, W, 40):
            d.rectangle([x, y, x + 38, y + 16], outline=(32, 30, 76))
    for r, y in enumerate(range(340, H, 40)):
        for c, x in enumerate(range(0, W, 40)):
            d.rectangle([x, y, x + 39, y + 39], fill=(44, 34, 92) if (r + c) % 2 else (64, 50, 120))
    d.rectangle([0, 340, W, 346], fill=(60, 230, 240))
    flick = 0.7 + 0.3 * math.sin(t * 17)
    for cx0, body in ((8, (52, 62, 140)), (282, (140, 52, 96))):      # máquinas arcade
        d.rectangle([cx0, 120, cx0 + 70, 344], fill=OL); d.rectangle([cx0 + 3, 123, cx0 + 67, 344], fill=body)
        d.rectangle([cx0 + 8, 134, cx0 + 62, 140], fill=(255, 230, 90))
        d.rectangle([cx0 + 10, 146, cx0 + 60, 206], fill=OL)
        scr = (int(60 * flick), int(200 * flick), int(160 * flick)) if cx0 < 100 else (int(240 * flick), int(90 * flick), int(150 * flick))
        d.rectangle([cx0 + 12, 148, cx0 + 58, 204], fill=scr)
        mx = int((t * 30) % 20)
        d.rectangle([cx0 + 20 + mx, 170, cx0 + 28 + mx, 178], fill=(255, 255, 255))
        d.rectangle([cx0 + 8, 214, cx0 + 62, 236], fill=sh(body, 0.7)); d.ellipse([cx0 + 14, 216, cx0 + 24, 226], fill=(255, 70, 70))
        d.ellipse([cx0 + 40, 217, cx0 + 48, 225], fill=(80, 200, 255)); d.ellipse([cx0 + 50, 217, cx0 + 58, 225], fill=(255, 230, 90))
    d.rectangle([84, 48, 276, 92], fill=OL)                                   # letrero de neón
    txt(d, (180, 70), "CIBER 66", 38, (255, 110, 200), outline=(120, 20, 90))
    return img


def glow_img(img, box, color, strength, blur):
    return Image.fromarray(__import__("numpy").asarray(glow(img, box, color, strength, blur))).convert("RGBA")


def _extras(img, kind):
    if kind == "arcade":
        img = glow_img(img, (84, 48, 276, 92), (255, 60, 190), 160, 14)
    if kind == "bedroom":
        img = glow_img(img, (0, 8, W, 20), (90, 220, 255), 120, 10)
    if kind == "street":
        img = glow_img(img, (40, 196, 74, 214), (255, 220, 120), 160, 22)
    return img


def room(t, night=False, score=(0, 14), verdict="DERROTA", label="K / D", cans_n=0, kind="living", big=None, likes=0):
    if kind == "living":
        img = grade(_room_base(t, night))
    else:
        img = _extras(grade({"street": _street_base, "bedroom": _bedroom_base, "arcade": _arcade_base, "patio": _patio_base,
                             "class": _class_base, "phone": lambda tt: _phone_base(tt, likes)}[kind](t), 1.2 if kind != "phone" else 1.0, 1.04 if kind != "phone" else 1.0), kind)
    if night and kind == "living":
        night_grade(img, 0.42)
    if cans_n:
        cans(img, cans_n)
    if kind in ("living", "bedroom", "arcade"):
        tv(img, t, score, verdict, label, night or kind == "bedroom", big)
        if night or kind == "bedroom":
            img = glow_img(img, (104, 96, 258, 244), (70, 110, 220), 130, 26)
    out = Image.new("RGBA", (W, H))
    out.paste(img.crop((0, DY, W, H)), (0, 0))
    out.paste(img.crop((0, H - 2 * DY, W, H - DY)), (0, H - DY))
    return out


def emote(img, x, y, kind, age):
    """Globito de emoción que salta sobre la cabeza (! ? corazón)."""
    d = ImageDraw.Draw(img)
    pop = min(1.0, age / 0.18)
    y = y - 10 * math.sin(min(age, 0.3) / 0.3 * math.pi)
    col = {"!": (255, 214, 60), "?": (90, 160, 230), "love": (240, 90, 130), "skull": (240, 240, 228)}[kind]
    r = int((15 if kind == "skull" else 13) * min(1.0, 0.4 + pop))
    bub = (52, 40, 74) if kind == "skull" else (255, 255, 255)
    d.ellipse([x - r, y - r, x + r, y + r], fill=bub, outline=OL, width=2)
    d.polygon([(x - 4, y + r - 2), (x + 4, y + r - 2), (x, y + r + 6)], fill=bub, outline=OL)
    if kind == "skull":
        pat = ["..11111..", ".1111111.", "111111111", "11o111o11", "11o111o11", "111111111", ".1111111.", "..1.1.1..", "..1.1.1.."]
        for ry, row in enumerate(pat):
            for rx, ch in enumerate(row):
                if ch != ".":
                    d.rectangle([x - 9 + rx * 2, y - 9 + ry * 2, x - 8 + rx * 2, y - 8 + ry * 2],
                                fill=(240, 240, 228) if ch == "1" else (30, 24, 44))
        return
    if kind == "love":
        d.rectangle([x - 6, y - 5, x - 2, y - 1], fill=col); d.rectangle([x + 2, y - 5, x + 6, y - 1], fill=col)
        d.rectangle([x - 6, y - 2, x + 6, y + 2], fill=col); d.rectangle([x - 3, y + 2, x + 3, y + 5], fill=col)
    else:
        txt(d, (x, y), kind, 24, col, outline=OL)


def speed_lines(img, cx, cy, t, strength=110):
    """Líneas de impacto estilo manga/RPG alrededor de un punto."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(int(t * 14))
    for k in range(34):
        a = k * (2 * math.pi / 34) + rnd.uniform(-0.05, 0.05)
        r1, r2 = rnd.randint(90, 130), rnd.randint(190, 330)
        d.line([cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r2, cy + math.sin(a) * r2],
               fill=(255, 255, 255, strength), width=rnd.choice((2, 3, 4)))
    img.alpha_composite(layer)


def boom(img, x, y, text, age, color=(255, 214, 70)):
    """Texto de impacto con rebote (¡PUM!, ¡ZAS!)."""
    d = ImageDraw.Draw(img)
    sc = 1 + 0.5 * math.exp(-age * 9) * math.cos(age * 22)
    txt(d, (x, y), text, int(46 * sc), color, outline=(160, 30, 50))


def sticker(img, x, y, text, age, fill=(236, 54, 84)):
    """Calcomanía de meme (SKILL ISSUE, AURA…): aparece con rebote sobre el personaje."""
    d = ImageDraw.Draw(img)
    f = _font(20)
    w = int(d.textlength(text, font=f)) + 18
    y = y - 14 * max(0.0, math.sin(min(age, 0.28) / 0.28 * math.pi)) * 1.0
    x0, y0 = x - w // 2, y - 15
    d.rounded_rectangle([x0 - 2, y0 - 2, x0 + w + 2, y0 + 30], radius=6, fill=(255, 255, 255))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 28], radius=5, fill=fill)
    txt(d, (x, y0 + 14), text, 20, (255, 255, 255), outline=(60, 10, 30))


def _patio_base(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    for y in range(0, 330, 3):
        u = y / 330
        d.rectangle([0, y, W, y + 3], fill=(int(90 + 120 * u), int(170 + 50 * u), int(250 - 10 * u)))
    cx = int(t * 6) % 420 - 60
    for ox, oy, w in ((0, 60, 60), (40, 48, 36), (-20, 70, 48)):
        d.rounded_rectangle([cx + ox, oy, cx + ox + w, oy + 16], radius=8, fill=(255, 255, 255))
    d.ellipse([290, 40, 330, 80], fill=(255, 236, 120))
    # edificio de la escuela
    d.rectangle([0, 120, W, 340], fill=OL); d.rectangle([3, 123, W - 3, 340], fill=(236, 168, 96))
    d.rectangle([3, 123, W - 3, 134], fill=(190, 72, 80))
    for r, wy in enumerate((146, 226)):
        for wx in range(14, 340, 56):
            if r == 1 and 150 < wx < 220:
                continue
            d.rectangle([wx, wy, wx + 38, wy + 54], fill=OL); d.rectangle([wx + 3, wy + 3, wx + 35, wy + 51], fill=(140, 210, 250))
            d.rectangle([wx + 18, wy + 3, wx + 20, wy + 51], fill=OL); d.rectangle([wx + 3, wy + 26, wx + 35, wy + 28], fill=OL)
    d.rectangle([150, 214, 222, 340], fill=OL); d.rectangle([154, 218, 218, 340], fill=(110, 78, 150)); d.rectangle([185, 218, 187, 340], fill=OL)
    d.rectangle([128, 176, 244, 206], fill=OL); txt(d, (186, 191), "COLE 66", 22, (255, 230, 90))
    d.rectangle([0, 340, W, H], fill=(178, 182, 204))
    for y in range(352, H, 40):
        d.rectangle([0, y, W, y + 1], fill=(150, 154, 180))
    d.arc([60, 380, 300, 560], 180, 360, fill=(250, 250, 250), width=3)         # cancha
    d.rectangle([40, 470, 320, 473], fill=(250, 250, 250)); d.ellipse([150, 440, 210, 500], outline=(250, 230, 90), width=3)
    d.rectangle([300, 190, 306, 340], fill=OL); d.rectangle([276, 170, 330, 200], fill=OL)    # aro de básquet
    d.rectangle([280, 174, 326, 196], fill=(250, 250, 250)); d.rectangle([298, 184, 310, 194], outline=(230, 80, 60), width=2)
    d.rectangle([6, 328, 70, 348], fill=OL); d.rectangle([9, 331, 67, 340], fill=(160, 100, 64))        # banca
    return img


def _class_base(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 340], fill=(238, 200, 128))
    for x in range(0, W, 30):
        d.rectangle([x, 0, x + 14, 340], fill=(244, 210, 140))
    d.rectangle([0, 300, W, 340], fill=(190, 140, 90))
    d.rectangle([40, 58, 320, 226], fill=(150, 98, 64)); d.rectangle([46, 64, 314, 220], fill=OL)       # pizarrón
    d.rectangle([49, 67, 311, 217], fill=(36, 118, 98))
    txt(d, (180, 100), "MATE", 40, (245, 245, 235), outline=(24, 80, 66))
    txt(d, (130, 160), "x2+2x=?", 22, (245, 245, 235), outline=(24, 80, 66))
    d.line([210, 150, 290, 190], fill=(245, 245, 235), width=2); d.ellipse([240, 160, 270, 196], outline=(250, 230, 90), width=2)
    d.rectangle([52, 214, 308, 220], fill=(150, 98, 64))
    d.rectangle([324, 90, 352, 118], fill=OL); d.ellipse([326, 92, 350, 116], fill=(246, 246, 238), outline=OL)  # reloj
    a = t * 0.6; d.line([338, 104, 338 + 8 * math.sin(a), 104 - 8 * math.cos(a)], fill=OL, width=2)
    d.rectangle([0, 340, W, H], fill=(176, 124, 84))
    for y in range(352, H, 28):
        d.rectangle([0, y, W, y + 1], fill=(146, 98, 68))
    for dx in (24, 150, 276):         # pupitres al fondo
        d.rectangle([dx, 478, dx + 64, 490], fill=OL); d.rectangle([dx + 2, 480, dx + 62, 488], fill=(120, 168, 220))
        d.rectangle([dx + 6, 490, dx + 10, 530], fill=OL); d.rectangle([dx + 54, 490, dx + 58, 530], fill=OL)
    d.rectangle([20, 250, 120, 262], fill=OL); d.rectangle([22, 252, 118, 260], fill=(110, 78, 56))      # escritorio del profe
    d.rectangle([60, 236, 90, 250], fill=(250, 90, 80), outline=OL)                                       # manzana/libro
    return img


def _phone_base(t, likes=0):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        u = y / H
        d.rectangle([0, y, W, y + 4], fill=(int(44 + 30 * u), int(30 + 10 * u), int(96 + 40 * u)))
    for k in range(12):
        x = (k * 61) % W; y = (k * 97 + int(t * 20)) % H
        d.rectangle([x, y, x + 2, y + 2], fill=(150, 130, 220))
    x0, y0, x1, y1 = 76, 136, 284, 416
    d.rounded_rectangle([x0 - 7, y0 - 7, x1 + 7, y1 + 7], radius=22, fill=OL)
    d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(20, 22, 44))
    d.rectangle([156, y0 + 3, 204, y0 + 8], fill=OL)
    d.ellipse([x0 + 10, y0 + 18, x0 + 40, y0 + 48], fill=(255, 90, 170), outline=(255, 255, 255), width=2)     # avatar
    txt(d, (x0 + 25, y0 + 33), "C", 18, (255, 255, 255), outline=(150, 20, 90))
    txt(d, (x0 + 48, y0 + 26), "curis_del_cole", 15, (255, 255, 255), outline=(20, 22, 44), anchor="lm")
    txt(d, (x0 + 48, y0 + 42), "cuenta anonima", 11, (150, 160, 200), outline=(20, 22, 44), anchor="lm")
    txt(d, (x1 - 40, y0 + 44), "3:07 AM", 12, (255, 214, 90), outline=(20, 22, 44))
    py = y0 + 58
    d.rectangle([x0 + 6, py, x1 - 6, py + 128], fill=(120, 190, 240))                                       # foto del post
    d.rectangle([x0 + 6, py + 78, x1 - 6, py + 128], fill=(196, 150, 100))
    d.rectangle([x0 + 30, py + 70, x1 - 30, py + 86], fill=(150, 100, 64)); d.rectangle([x0 + 30, py + 70, x1 - 30, py + 73], fill=(190, 140, 90))
    d.ellipse([x0 + 82, py + 40, x0 + 126, py + 80], fill=(166, 114, 84)); d.rectangle([x0 + 82, py + 36, x0 + 128, py + 54], fill=(52, 36, 30))
    d.rectangle([x0 + 96, py + 62, x0 + 104, py + 64], fill=OL); d.rectangle([x0 + 108, py + 62, x0 + 116, py + 64], fill=OL)
    z = int(t * 3) % 3
    for k in range(3):
        txt(d, (x0 + 132 + k * 14, py + 40 - k * 12 - (4 if k == z else 0)), "z", 14 + 4 * k, (255, 255, 255), outline=(60, 90, 160))
    d.rectangle([x0 + 6, py + 106, x1 - 6, py + 128], fill=(14, 14, 28)); txt(d, ((x0 + x1) // 2, py + 117), "MEMO EN MATE", 15, (255, 255, 255), outline=(14, 14, 28))
    iy = py + 138
    hx = x0 + 18
    d.rectangle([hx - 6, iy - 2, hx + 6, iy + 4], fill=(240, 60, 90)); d.rectangle([hx + 6, iy - 2, hx + 18, iy + 4], fill=(240, 60, 90))
    d.polygon([(hx - 6, iy + 3), (hx + 18, iy + 3), (hx + 6, iy + 15)], fill=(240, 60, 90))
    txt(d, (hx + 34, iy + 5), f"{4000 + int(t * 53):,}", 15, (255, 255, 255), outline=(20, 22, 44), anchor="lm")
    txt(d, (x0 + 14, iy + 28), "¿Quien sera el dueno?", 13, (200, 210, 240), outline=(20, 22, 44), anchor="lm")
    txt(d, (x0 + 14, iy + 44), "jajaja ya dime quien es", 12, (150, 160, 200), outline=(20, 22, 44), anchor="lm")
    return img

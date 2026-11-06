"""Fondos RPG a 360x640: sala con TV, ventana con luz, alfombra, tableros; efectos de luz."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 360, 640
OL = (38, 24, 56)


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def txt(d, xy, s, size, fill, outline=OL, anchor="mm"):
    d.fontmode = "1"
    f = _font(size)
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        d.text((x + dx, y + dy), s, font=f, fill=outline, anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def room(t, night=False):
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


def tv(img, t, score, verdict, label="K / D", night=False):
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
    txt(d, (181, 188), f"{score[0]} - {score[1]}", 38, (255, 255, 255))
    for i in range(6):   # barrita de vida estilo juego
        d.rectangle([124 + i * 8, 214, 129 + i * 8, 220], fill=col if (i < 4 or not good) else sh(col, .4))
    if int(t * 3) % 2 == 0:
        d.rectangle([118, 112, 124, 118], fill=col)
    d.rectangle([116, 110, 130, 114], fill=(255, 255, 255, 60)) if False else None
    d.polygon([(118, 112), (150, 112), (126, 164), (118, 164)], fill=None) if False else None


def glow(img, box, color, strength=140, blur=22):
    layer = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(layer).rectangle(box, fill=tuple(int(c * strength / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(img.convert("RGB"), dtype="int16") +
                                                      __import__("numpy").asarray(layer, dtype="int16"), 0, 255).astype("uint8"))


def light_shaft(img, strength=44):
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

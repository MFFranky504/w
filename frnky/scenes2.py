"""Escenarios detallados y animados del episodio de la directora: patio con feria, dirección, sala de profes,
pasillo con casilleros, auditorio con reflectores. Todo se dibuja por código a 360x640 (x3 -> 1080x1920)."""
import math
import random

from PIL import Image, ImageDraw

from .bg import W, H, OL, DY, grade, glow_img, txt, sh, _patio_base
from .sprite import draw_char, CHARS


def _new():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    return img, ImageDraw.Draw(img)


def _finish(img):
    out = Image.new("RGBA", (W, H))
    out.paste(img.crop((0, DY, W, H)), (0, 0))
    out.paste(img.crop((0, H - 2 * DY, W, H - DY)), (0, H - DY))
    return out


def _clock(d, cx, cy, r, t, speed=0.6):
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=OL)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(248, 246, 236))
    for k in range(12):
        a = k * math.pi / 6
        d.rectangle([cx + (r - 3) * math.sin(a) - 1, cy - (r - 3) * math.cos(a) - 1, cx + (r - 3) * math.sin(a), cy - (r - 3) * math.cos(a)], fill=OL)
    a = t * speed
    d.line([cx, cy, cx + (r - 4) * math.sin(a), cy - (r - 4) * math.cos(a)], fill=OL, width=2)
    d.line([cx, cy, cx + (r - 8) * math.sin(a / 12), cy - (r - 8) * math.cos(a / 12)], fill=(210, 40, 40), width=2)


def _dust(img, t, box, n=18):
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for k in range(n):
        x = box[0] + (rnd.random() * (box[2] - box[0]) + math.sin(t * 0.7 + k) * 6) % (box[2] - box[0])
        y = box[1] + (rnd.random() * (box[3] - box[1]) + t * (6 + k % 5 * 2)) % (box[3] - box[1])
        d.rectangle([x, y, x + 1, y + 1], fill=(255, 250, 220, 255))


def patio(t):
    img = _patio_base(t)
    d = ImageDraw.Draw(img)
    # mástil con bandera ondeando
    d.rectangle([22, 40, 26, 340], fill=OL); d.ellipse([19, 34, 29, 44], fill=(250, 220, 90))
    for k in range(20):          # bandera ondeando (tricolor)
        yy = 52 + math.sin(t * 5 + k * 0.5) * 3 + k * 0.15
        for bi, col in enumerate(((250, 210, 60), (30, 70, 190), (210, 40, 50))):
            d.rectangle([27 + k * 3, yy + bi * 13, 30 + k * 3, yy + bi * 13 + 13], fill=col)
    # guirnalda de la feria entre edificio y poste
    for k in range(0, W, 12):
        yy = 136 + 10 * math.sin(k / W * math.pi) + math.sin(t * 3 + k) * 1.5
        d.line([k, yy, k + 12, 136 + 10 * math.sin((k + 12) / W * math.pi)], fill=OL, width=1)
        d.polygon([(k + 3, yy), (k + 9, yy), (k + 6, yy + 9)], fill=[(255, 90, 120), (255, 220, 80), (90, 210, 255), (130, 230, 130)][(k // 12) % 4])
    # globos flotando
    for k, c in enumerate([(255, 80, 110), (80, 200, 255), (255, 220, 80)]):
        bx = 290 + k * 22 + math.sin(t * 1.3 + k) * 4; by = 90 - k * 8 + math.sin(t * 1.7 + k * 2) * 5
        d.ellipse([bx - 8, by - 10, bx + 8, by + 10], fill=c, outline=OL); d.line([bx, by + 10, 300 + k * 6, 170], fill=OL, width=1)
    # pájaros
    for k in range(3):
        bx = (t * (18 + 6 * k) + k * 120) % 420 - 30; by = 50 + k * 26 + math.sin(t * 6 + k) * 3
        wing = 3 if int(t * 8 + k) % 2 else -2
        d.line([bx - 6, by + wing, bx, by], fill=OL, width=2); d.line([bx, by, bx + 6, by + wing], fill=OL, width=2)
    return img


def podium(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 34, y - 20, x + 34, y + 40], fill=OL); d.rectangle([x - 31, y - 17, x + 31, y + 37], fill=(150, 98, 60))
    d.rectangle([x - 31, y - 17, x + 31, y - 10], fill=(196, 136, 84)); d.rectangle([x - 10, y + 6, x + 10, y + 22], fill=(250, 220, 90))
    d.line([x + 8, y - 20, x + 14, y - 40], fill=OL, width=3); d.ellipse([x + 10, y - 48, x + 20, y - 38], fill=(60, 60, 76), outline=OL)


def oficina(t):
    img, d = _new()
    d.rectangle([0, 0, W, 340], fill=(226, 204, 168))
    for x in range(0, W, 24):
        d.rectangle([x, 0, x + 11, 340], fill=(232, 212, 178))
    d.rectangle([0, 238, W, 344], fill=(112, 70, 50))
    for x in range(0, W, 40):
        d.rectangle([x + 4, 246, x + 34, 336], outline=(84, 50, 38), width=2); d.rectangle([x + 7, 249, x + 9, 333], fill=(138, 90, 64))
    d.rectangle([0, 232, W, 240], fill=(190, 132, 84))
    # ventana grande con ciudad y cortinas
    d.rectangle([28, 40, 160, 214], fill=OL)
    for y in range(44, 210, 6):
        d.rectangle([32, y, 156, y + 6], fill=(int(120 + (y - 44) * 0.4), int(190 + (y - 44) * 0.2), 250))
    for bx, bh, c in ((36, 70, (92, 100, 160)), (60, 100, (110, 90, 150)), (86, 60, (92, 120, 170)), (108, 90, (120, 100, 160)), (132, 74, (100, 110, 170))):
        d.rectangle([bx, 210 - bh, bx + 20, 210], fill=c)
        for wy in range(214 - bh, 206, 10):
            d.rectangle([bx + 4, wy, bx + 7, wy + 4], fill=(255, 236, 150)); d.rectangle([bx + 12, wy, bx + 15, wy + 4], fill=(255, 236, 150))
    d.rectangle([92, 44, 96, 210], fill=(236, 220, 200)); d.rectangle([32, 128, 156, 132], fill=(236, 220, 200))
    sway = math.sin(t * 1.2) * 2
    d.polygon([(18, 34), (48 + sway, 34), (58 + sway, 214), (18, 214)], fill=(168, 40, 70)); d.polygon([(18, 34), (26, 34), (30, 214), (18, 214)], fill=(208, 70, 100))
    d.polygon([(170, 34), (140 + sway, 34), (130 + sway, 214), (170, 214)], fill=(168, 40, 70)); d.polygon([(170, 34), (164, 34), (160, 214), (170, 214)], fill=(140, 28, 56))
    d.rectangle([12, 28, 176, 38], fill=(120, 84, 56))
    _clock(d, 218, 46, 20, t, 0.8)
    for k, (fx, c) in enumerate(((190, (250, 214, 90)), (232, (110, 190, 250)), (274, (240, 110, 130)))):  # diplomas
        d.rectangle([fx, 96, fx + 34, 140], fill=OL); d.rectangle([fx + 3, 99, fx + 31, 137], fill=(250, 246, 232))
        d.rectangle([fx + 8, 106, fx + 26, 109], fill=c); d.rectangle([fx + 8, 114, fx + 26, 116], fill=(190, 190, 180)); d.ellipse([fx + 13, 122, fx + 21, 130], fill=c)
    # librero
    d.rectangle([288, 40, 352, 236], fill=OL); d.rectangle([291, 43, 349, 233], fill=(140, 90, 60))
    rnd = random.Random(8)
    for r in range(4):
        by = 48 + r * 46
        d.rectangle([291, by + 38, 349, by + 44], fill=(100, 62, 42))
        x = 294
        while x < 344:
            w = rnd.randint(4, 8); h = rnd.randint(24, 36)
            d.rectangle([x, by + 38 - h, x + w, by + 38], fill=rnd.choice([(210, 60, 70), (60, 120, 210), (240, 190, 60), (70, 170, 110), (160, 80, 190)]), outline=OL)
            x += w + 1
    # escritorio de la directora con compu y lámpara
    d.rectangle([56, 262, 280, 276], fill=OL); d.rectangle([58, 264, 278, 274], fill=(196, 136, 84))
    d.rectangle([62, 276, 274, 342], fill=(132, 84, 56)); d.rectangle([62, 276, 274, 280], fill=(96, 60, 42))
    for dx in (74, 176):
        d.rectangle([dx, 288, dx + 88, 336], outline=(96, 60, 42), width=2); d.rectangle([dx + 36, 308, dx + 52, 314], fill=(250, 214, 90))
    d.rectangle([116, 226, 176, 262], fill=OL); d.rectangle([119, 229, 173, 258], fill=(26, 40, 70))       # monitor con memes que pasan
    for k in range(3):
        yy = (t * 14 + k * 20) % 60 - 6
        if 0 <= yy < 26:
            d.rectangle([122, 230 + yy, 170, 236 + yy], fill=[(255, 110, 140), (110, 210, 255), (255, 220, 90)][k])
    d.rectangle([140, 258, 152, 262], fill=OL)
    d.rectangle([220, 240, 224, 262], fill=OL); d.polygon([(208, 236), (240, 236), (232, 224), (216, 224)], fill=(250, 220, 90), outline=OL)
    d.rectangle([160, 266, 232, 272], fill=(250, 214, 90)); txt(d, (196, 269), "DIRECCION", 9, OL, outline=(250, 214, 90))
    d.rectangle([68, 246, 98, 262], fill=OL); d.rectangle([70, 248, 96, 260], fill=(246, 246, 238))         # papeles
    # piso alfombrado
    d.rectangle([0, 344, W, H], fill=(142, 44, 66))
    for y in range(352, H, 26):
        for x in range(((y // 26) % 2) * 20, W, 40):
            d.rectangle([x, y, x + 18, y + 12], fill=(160, 56, 80))
    d.rectangle([0, 344, W, 352], fill=(220, 180, 90))
    d.ellipse([40, 380, 320, 520], outline=(220, 180, 90), width=3)
    # planta y mástil con bandera
    d.rectangle([4, 220, 24, 256], fill=(190, 100, 70), outline=OL)
    for lx, ly in ((2, 190), (10, 176), (18, 192), (8, 204)):
        d.polygon([(lx + 4, 224), (lx, ly), (lx + 12, ly + 10)], fill=(70, 190, 110), outline=OL)
    img = glow_img(img, (28, 40, 160, 214), (255, 245, 200), 90, 16)
    _dust(img, t, (30, 60, 170, 330))
    return img


def staff(t):
    img, d = _new()
    d.rectangle([0, 0, W, 340], fill=(190, 226, 214))
    for x in range(0, W, 30):
        d.rectangle([x, 0, x + 14, 340], fill=(200, 232, 220))
    d.rectangle([0, 270, W, 344], fill=(120, 170, 160)); d.rectangle([0, 266, W, 272], fill=(240, 244, 236))
    # corcho con avisos
    d.rectangle([24, 50, 170, 172], fill=OL); d.rectangle([28, 54, 166, 168], fill=(204, 150, 96))
    cols = [(255, 230, 110), (255, 140, 170), (130, 220, 255), (170, 240, 150), (255, 190, 100)]
    for k in range(9):
        nx = 34 + (k % 3) * 44; ny = 60 + (k // 3) * 34
        d.rectangle([nx, ny, nx + 34, ny + 26], fill=cols[k % 5], outline=OL); d.rectangle([nx + 4, ny + 6, nx + 28, ny + 8], fill=OL); d.rectangle([nx + 4, ny + 13, nx + 22, ny + 15], fill=OL)
        d.ellipse([nx + 14, ny - 2, nx + 20, ny + 4], fill=(230, 60, 60))
    txt(d, (97, 44), "AVISOS", 14, (255, 250, 230))
    # ventana con persianas
    d.rectangle([220, 50, 330, 190], fill=OL); d.rectangle([224, 54, 326, 186], fill=(130, 200, 250))
    for y in range(58, 186, 10):
        d.rectangle([224, y, 326, y + 6], fill=(236, 230, 210)); d.rectangle([224, y + 6, 326, y + 7], fill=(190, 184, 160))
    _clock(d, 195, 40, 16, t, 0.7)
    # lockers
    d.rectangle([4, 180, 60, 300], fill=OL)
    for k in range(2):
        d.rectangle([7 + k * 26, 183, 31 + k * 26, 297], fill=(70, 140, 200)); d.rectangle([10 + k * 26, 192, 28 + k * 26, 200], fill=(40, 90, 150)); d.rectangle([24 + k * 26, 240, 27 + k * 26, 252], fill=(240, 220, 120))
    # cafetera con lucecita
    d.rectangle([270, 206, 318, 270], fill=OL); d.rectangle([273, 209, 315, 267], fill=(220, 90, 80)); d.rectangle([280, 232, 308, 262], fill=(40, 40, 56))
    d.ellipse([280, 214, 288, 222], fill=(90, 255, 110) if int(t * 2) % 2 else (30, 120, 50))
    # mesa larga con tazas, laptops, vapor
    d.rectangle([40, 276, 330, 292], fill=OL); d.rectangle([42, 278, 328, 290], fill=(190, 130, 84))
    d.rectangle([54, 292, 62, 344], fill=OL); d.rectangle([306, 292, 314, 344], fill=OL)
    for mx, c in ((80, (250, 250, 250)), (140, (255, 140, 60)), (250, (130, 220, 255)), (296, (255, 120, 150))):
        d.rectangle([mx, 262, mx + 14, 278], fill=c, outline=OL)
        for s_ in range(3):
            sy = 258 - ((t * 14 + s_ * 9 + mx) % 28); sx = mx + 6 + math.sin(t * 3 + s_ + mx) * 3
            d.rectangle([sx, sy, sx + 2, sy + 4], fill=(255, 255, 255))
    d.rectangle([180, 258, 226, 278], fill=OL); d.rectangle([183, 261, 223, 275], fill=(110, 200, 255)); d.rectangle([170, 276, 236, 280], fill=(70, 70, 90))
    # piso damero
    for r, y in enumerate(range(344, H, 40)):
        for c, x in enumerate(range(0, W, 40)):
            d.rectangle([x, y, x + 39, y + 39], fill=(236, 226, 196) if (r + c) % 2 else (200, 188, 150))
    d.rectangle([0, 344, W, 350], fill=(150, 140, 110))
    return grade(img, 1.0, 1.0) if False else img


def hall(t):
    img, d = _new()
    d.rectangle([0, 0, W, 340], fill=(208, 220, 240))
    flick = 0.85 + 0.15 * math.sin(t * 17) * (1 if int(t * 5) % 7 == 0 else 0.3)
    for lx in (40, 150, 260):
        d.rectangle([lx, 6, lx + 60, 16], fill=(int(255 * flick), int(252 * flick), int(220 * flick)), outline=OL)
    cols = [(60, 130, 220), (230, 70, 70), (250, 200, 60), (70, 180, 120), (180, 90, 200)]
    for k in range(9):          # casilleros
        x = k * 42 - 4
        c = cols[k % 5]
        d.rectangle([x, 70, x + 42, 300], fill=OL); d.rectangle([x + 2, 72, x + 40, 298], fill=c)
        d.rectangle([x + 2, 72, x + 6, 298], fill=sh(c, 1.15)); d.rectangle([x + 36, 72, x + 40, 298], fill=sh(c, 0.8))
        for vy in (80, 86, 92):
            d.rectangle([x + 10, vy, x + 32, vy + 2], fill=sh(c, 0.6))
        d.rectangle([x + 12, 104, x + 30, 112], fill=(246, 246, 236)); d.rectangle([x + 34, 190, x + 37, 206], fill=(240, 230, 150))
        d.rectangle([x + 2, 160, x + 40, 162], fill=sh(c, 0.7)); d.rectangle([x + 2, 232, x + 40, 234], fill=sh(c, 0.7))
    # afiches pegados
    for px, py, c in ((40, 120, (255, 120, 170)), (172, 130, (120, 220, 255)), (300, 118, (255, 230, 110))):
        d.rectangle([px, py, px + 34, py + 44], fill=(250, 250, 244), outline=OL); d.rectangle([px + 4, py + 4, px + 30, py + 20], fill=c); d.rectangle([px + 4, py + 26, px + 28, py + 28], fill=OL); d.rectangle([px + 4, py + 33, px + 22, py + 35], fill=OL)
    txt(d, (180, 48), "FERIA DEL COLE", 22, (240, 70, 90), outline=(255, 255, 255))
    d.rectangle([0, 300, W, 344], fill=(120, 130, 160))
    d.rectangle([0, 340, W, H], fill=(214, 206, 192))
    for r, y in enumerate(range(344, H, 36)):
        for x in range(((r % 2) * 30), W, 60):
            d.rectangle([x, y, x + 58, y + 34], fill=(226, 218, 204) if (x // 60 + r) % 2 else (206, 198, 184))
    for k in range(5):      # reflejos de las luces en el piso
        rx = 50 + k * 60 + math.sin(t * 1.5 + k) * 4
        d.polygon([(rx, 348), (rx + 22, 348), (rx + 34, 470), (rx - 10, 470)], fill=(236, 244, 255))
    return img


def stage(t):
    img, d = _new()
    d.rectangle([0, 0, W, 340], fill=(24, 22, 60))
    # telón de fondo con banner
    d.rectangle([40, 60, 320, 250], fill=(52, 40, 120)); d.rectangle([40, 60, 320, 70], fill=(240, 200, 80))
    d.rectangle([76, 92, 284, 164], fill=OL); d.rectangle([80, 96, 280, 160], fill=(246, 80, 110))
    txt(d, (180, 118), "FERIA", 34, (255, 244, 200), outline=(130, 20, 60)); txt(d, (180, 146), "DEL COLE", 22, (255, 244, 200), outline=(130, 20, 60))
    for k in range(18):         # foquitos del banner parpadeando
        bx = 80 + k * 11.8
        on = (k + int(t * 4)) % 3
        c = (255, 230, 110) if on == 0 else (255, 120, 170) if on == 1 else (110, 210, 255)
        d.ellipse([bx - 3, 88, bx + 3, 94], fill=c); d.ellipse([bx - 3, 162, bx + 3, 168], fill=c)
    # tablado
    d.rectangle([0, 250, W, 344], fill=(170, 112, 70))
    for x in range(0, W, 36):
        d.rectangle([x, 250, x + 1, 344], fill=(120, 76, 50))
    d.rectangle([0, 340, W, 352], fill=(110, 70, 48))
    # cortinas rojas que se mecen
    sway = math.sin(t * 0.9) * 3
    for side in (0, 1):
        for k in range(8):
            x0 = (k * 10 if side == 0 else W - 80 + k * 10) + (sway if k > 4 else 0) * (1 if side == 0 else -1)
            c = (176, 30, 56) if k % 2 == 0 else (206, 50, 80)
            d.rectangle([x0, 0, x0 + 10, 340 - (k * 5 if side == 0 else (7 - k) * 5)], fill=c)
    d.rectangle([0, 0, W, 22], fill=(120, 20, 44)); d.rectangle([0, 22, W, 26], fill=(240, 200, 80))
    # piso del auditorio con butacas
    d.rectangle([0, 352, W, H], fill=(36, 30, 70))
    for r in range(4):
        by = 470 + r * 34
        for x in range(-10 + (r % 2) * 18, W, 36):
            d.rectangle([x, by, x + 30, by + 22], fill=(150, 34, 66)); d.rectangle([x + 2, by - 8, x + 28, by + 2], fill=(190, 52, 90))
    return img


def beams(img, t, strength=70):
    """Reflectores que barren el escenario."""
    l = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    for k, (sx, col) in enumerate(((60, (255, 240, 150)), (300, (150, 220, 255)))):
        a = math.sin(t * 0.9 + k * 2) * 0.35
        tx = 180 + math.sin(t * 0.9 + k * 2) * 70
        d.polygon([(sx - 6, 20), (sx + 6, 20), (tx + 60, 360), (tx - 60, 360)], fill=col + (strength,))
    img.alpha_composite(l)


_NAMES = [f"s{i}" for i in range(10)]


def crowd(c, t, y_feet, x0=-10, x1=370, step=34, seed=1, jump=0.0, phones=False, scale=1):
    """Multitud de alumnos de fondo (siluetas pequeñas) con rebote; algunos levantan el celular."""
    rnd = random.Random(seed)
    xs = list(range(x0, x1, step))
    for i, x in enumerate(xs):
        n = _NAMES[(i * 3 + seed) % 10]
        ph = rnd.random() * 6
        up = jump * abs(math.sin(t * 6 + ph)) * 10
        pose = "phone" if phones and (i + int(t * 2)) % 3 == 0 else ("cheer" if jump > 0.5 and i % 2 == 0 else "down")
        draw_char(c, n, x + rnd.randint(-5, 5), y_feet - up + rnd.randint(-4, 4), scale=scale, shadow=False,
                  expr="happy" if jump > 0 else ("shock" if i % 3 == 0 else "neutral"), pose=pose, flip=i % 2 == 1)


def walkers(c, t, y_feet, names, speed=60, seed=0):
    for i, n in enumerate(names):
        x = (t * speed * (1 if i % 2 == 0 else -1) + i * 110 + seed * 40) % 480 - 60
        if i % 2 == 1:
            x = 420 - x
        draw_char(c, n, x, y_feet + (i % 2) * 6, scale=1, shadow=False, expr="neutral", pose="down", walk=1 + int(t * 6 + i) % 2, flip=(i % 2 == 1))


def room2(t, kind):
    f = {"patio": patio, "oficina": oficina, "staff": staff, "hall": hall, "stage": stage}[kind]
    img = f(t)
    from .bg import grade as g
    img = g(img, 1.2, 1.04)
    return img


def finish(img):
    return _finish(img)

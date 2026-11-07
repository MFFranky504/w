"""Escenarios chunky (se dibujan a 180x320 y se amplían x2 con NEAREST para que el píxel coincida con los sprites).
Cada objeto lleva contorno oscuro, luz a la izquierda y sombra a la derecha, igual que los personajes."""
import math
import random

from PIL import Image, ImageDraw

from .bg import W, H, glow_img
from .bg import txt as _txt
from .scenes2 import finish as _finish, _dust

LW, LH = 180, 320
OL = (30, 18, 44)


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def _new():
    img = Image.new("RGBA", (LW, LH), (0, 0, 0, 255))
    return img, ImageDraw.Draw(img)


def box(d, x0, y0, x1, y1, c, outline=True):
    """Bloque con contorno, luz izquierda, sombra derecha y base (como body() en los sprites)."""
    if outline:
        d.rectangle([x0 - 1, y0 - 1, x1, y1], fill=OL)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=c)
    d.rectangle([x0, y0, x0, y1 - 1], fill=sh(c, 1.18))
    d.rectangle([x1 - 2, y0, x1 - 1, y1 - 1], fill=sh(c, 0.76))
    d.rectangle([x0, y1 - 2, x1 - 1, y1 - 1], fill=sh(c, 0.82))


def txt(d, xy, s, size, fill, outline=OL, anchor="mm"):
    _txt(d, xy, s, size, fill, outline, anchor)


def _up(img):
    big = img.resize((W, H), Image.NEAREST)
    return big


def _fin(img, extra=None):
    big = _up(img)
    if extra:
        big = extra(big)
    return _finish(big)


def _clothes(d, t, y0, x0, x1):
    d.line([x0, y0, x1, y0 + 6], fill=OL, width=1)
    cols = [(240, 90, 120), (90, 190, 250), (250, 210, 80), (120, 220, 140), (190, 120, 230)]
    for k in range(6):
        x = x0 + 12 + k * ((x1 - x0 - 24) / 5)
        yy = y0 + 6 * (x - x0) / (x1 - x0)
        sw = math.sin(t * 2.2 + k) * 1.5
        box(d, int(x + sw), int(yy) + 1, int(x + sw) + 9, int(yy) + 14, cols[k % 5])
        d.rectangle([int(x), int(yy), int(x) + 1, int(yy) + 1], fill=(250, 250, 250))


def azotea(t):
    img, d = _new()
    top, bot = (92, 70, 170), (255, 170, 110)
    for y in range(0, 150, 2):
        u = y / 150
        d.rectangle([0, y, LW, y + 2], fill=tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3)))
    d.ellipse([112, 98, 150, 136], fill=(255, 226, 150)); d.ellipse([118, 104, 144, 130], fill=(255, 244, 200))
    rnd = random.Random(11)
    for layer, (col, hmin, hmax, y) in enumerate(((  (120, 96, 170), 30, 70, 150), ((98, 76, 150), 40, 90, 150))):
        x = -8
        while x < LW:
            w = rnd.randint(14, 26); h = rnd.randint(hmin, hmax)
            d.rectangle([x, y - h, x + w, y], fill=col)
            for wy in range(y - h + 4, y - 4, 7):
                for wx in range(x + 3, x + w - 4, 6):
                    if (wx * 3 + wy + layer) % 5 and (int(t * 2) + wx) % 11:
                        d.rectangle([wx, wy, wx + 1, wy + 2], fill=(255, 228, 140))
            x += w + 1
    for ax in (20, 70, 150):                                  # antenas
        d.line([ax, 60, ax, 88], fill=OL, width=1); d.line([ax - 6, 70, ax + 6, 70], fill=OL, width=1); d.line([ax - 4, 76, ax + 4, 76], fill=OL, width=1)
    box(d, 140, 82, 164, 112, (150, 100, 70)); box(d, 142, 76, 162, 82, (120, 80, 56))      # tinaco lejano
    for bx in (30, 90, 140):                                  # pájaros
        px = (bx + t * 14) % (LW + 20) - 10; py = 40 + math.sin(t * 3 + bx) * 3
        wing = 2 if int(t * 8 + bx) % 2 else -1
        d.line([px - 3, py + wing, px, py], fill=OL); d.line([px, py, px + 3, py + wing], fill=OL)
    # parapeto de ladrillo
    d.rectangle([0, 150, LW, 168], fill=OL)
    for r, y in enumerate(range(151, 168, 5)):
        for x in range(-(r % 2) * 6, LW, 12):
            d.rectangle([x, y, x + 10, y + 3], fill=(190, 96, 72)); d.rectangle([x, y, x + 10, y], fill=(220, 130, 96))
    d.rectangle([0, 150, LW, 152], fill=(226, 190, 160))
    # piso de concreto con baldosas y charco
    d.rectangle([0, 168, LW, LH], fill=(150, 146, 168))
    for y in range(172, LH, 14):
        d.rectangle([0, y, LW, y], fill=(126, 122, 148))
    for x in range(0, LW, 30):
        d.rectangle([x, 168, x, LH], fill=(130, 126, 152))
    d.ellipse([110, 240, 160, 252], fill=(120, 150, 210)); d.ellipse([116, 242, 150, 248], fill=(170, 200, 240))
    # tendedero con ropa
    d.rectangle([4, 100, 6, 168], fill=OL); d.rectangle([172, 108, 174, 168], fill=OL)
    _clothes(d, t, 104, 5, 173)
    # foquitos
    d.line([0, 22, LW, 34], fill=OL)
    for k in range(10):
        x = k * 18 + 6; y = 22 + 12 * x / LW + 3
        on = (k + int(t * 3)) % 3
        c = [(255, 230, 110), (255, 130, 170), (110, 220, 255)][on]
        d.rectangle([x, int(y), x + 2, int(y) + 3], fill=c)
    # sillón viejo + cojines + planta + parrilla + cajas + gato
    box(d, 8, 150, 52, 176, (120, 70, 90)); box(d, 6, 160, 16, 184, (150, 90, 110)); box(d, 44, 160, 54, 184, (150, 90, 110))
    box(d, 14, 166, 46, 182, (176, 110, 130)); box(d, 20, 158, 30, 168, (250, 200, 80)); box(d, 32, 158, 42, 168, (90, 190, 170))
    box(d, 138, 156, 168, 178, (70, 76, 100)); d.rectangle([140, 150, 166, 156], fill=OL); d.rectangle([141, 151, 165, 155], fill=(150, 156, 180))
    for k in range(5):
        d.rectangle([144 + k * 5, 158, 146 + k * 5, 160], fill=(255, 130 + 40 * ((int(t * 6) + k) % 2), 60))
    for k in range(4):
        sy = 148 - ((t * 20 + k * 11) % 40); d.rectangle([150 + math.sin(t * 3 + k) * 4, sy, 153 + math.sin(t * 3 + k) * 4, sy + 3], fill=(230, 230, 240))
    box(d, 60, 168, 80, 184, (176, 130, 80)); box(d, 66, 160, 84, 176, (196, 150, 96))
    box(d, 96, 160, 106, 172, (200, 110, 80)); d.polygon([(101, 148), (96, 160), (106, 160)], fill=(70, 190, 110), outline=OL)
    d.polygon([(101, 150), (92, 162), (100, 160)], fill=(90, 210, 130)); d.polygon([(101, 150), (110, 162), (102, 160)], fill=(60, 170, 100))
    d.ellipse([122, 170, 134, 180], fill=(250, 150, 80), outline=OL); d.rectangle([121, 168, 124, 172], fill=(250, 150, 80))   # gato
    return _fin(img, lambda b: glow_img(b, (112 * 2, 98 * 2, 150 * 2, 136 * 2), (255, 200, 120), 90, 18))


def oficina(t):
    img, d = _new()
    d.rectangle([0, 0, LW, 168], fill=(214, 224, 238))
    for x in range(0, LW, 15):
        d.rectangle([x, 0, x + 7, 168], fill=(222, 232, 244))
    d.rectangle([0, 150, LW, 168], fill=(120, 132, 160)); d.rectangle([0, 148, LW, 150], fill=(246, 246, 250))
    for lx in (14, 76, 138):                                     # luces + ventilador
        d.rectangle([lx, 2, lx + 30, 7], fill=OL); d.rectangle([lx + 1, 3, lx + 29, 6], fill=(255, 252, 226))
    fx = 90; d.line([fx, 2, fx, 12], fill=OL)
    a = t * 9
    for k in range(3):
        ang = a + k * 2.094
        d.line([fx, 12, fx + 18 * math.cos(ang), 12 + 3 * math.sin(ang)], fill=(90, 90, 110), width=2)
    # ventana grande con persiana y ciudad
    d.rectangle([6, 20, 68, 100], fill=OL)
    for y in range(22, 98, 3):
        d.rectangle([8, y, 66, y + 3], fill=(int(130 + (y - 22) * .35), int(196 + (y - 22) * .2), 250))
    for bx, bh, c in ((10, 36, (92, 100, 160)), (24, 52, (112, 92, 152)), (40, 30, (92, 122, 172)), (52, 46, (122, 102, 162))):
        d.rectangle([bx, 98 - bh, bx + 10, 98], fill=c)
        for wy in range(100 - bh, 94, 5):
            d.rectangle([bx + 2, wy, bx + 3, wy + 2], fill=(255, 236, 150)); d.rectangle([bx + 6, wy, bx + 7, wy + 2], fill=(255, 236, 150))
    for y in range(22, 98, 8):
        d.rectangle([8, y, 66, y + 3], fill=(236, 230, 214))
    d.rectangle([6, 98, 68, 102], fill=(236, 230, 214))
    # reloj, afiche motivacional, pizarra de metas
    d.ellipse([82, 18, 102, 38], fill=OL); d.ellipse([84, 20, 100, 36], fill=(248, 246, 236))
    d.line([92, 28, 92 + 6 * math.sin(t * 1.6), 28 - 6 * math.cos(t * 1.6)], fill=OL, width=1); d.line([92, 28, 92 + 4 * math.sin(t * .13), 28 - 4 * math.cos(t * .13)], fill=(210, 40, 40))
    box(d, 112, 14, 140, 52, (246, 246, 240)); d.polygon([(114, 46), (126, 24), (132, 34), (138, 46)], fill=(90, 150, 210)); d.polygon([(122, 46), (130, 30), (138, 46)], fill=(120, 180, 240))
    d.ellipse([128, 18, 136, 26], fill=(255, 220, 90)); txt(d, (126, 49), "EQUIPO", 6, OL, outline=(246, 246, 240))
    box(d, 146, 14, 176, 64, (250, 250, 246)); txt(d, (161, 20), "METAS", 6, OL, outline=(250, 250, 246))
    for k, (w, c) in enumerate(((20, (90, 190, 120)), (14, (250, 200, 70)), (8, (240, 90, 90)))):
        d.rectangle([150, 28 + k * 9, 150 + w, 33 + k * 9], fill=c)
    # mamparas con monitores al fondo
    for x0 in (4, 62, 120):
        box(d, x0, 104, x0 + 54, 146, (176, 190, 214))
        box(d, x0 + 14, 112, x0 + 40, 132, (30, 40, 70))
        for k in range(5):
            h = 4 + int(10 * abs(math.sin(t * 1.4 + k + x0)))
            d.rectangle([x0 + 17 + k * 5, 128 - h, x0 + 20 + k * 5, 128], fill=[(255, 110, 140), (110, 210, 255), (255, 220, 90)][k % 3])
        d.rectangle([x0 + 24, 132, x0 + 30, 136], fill=OL)
    # fotocopiadora, dispensador, archivero, planta, cafetera
    box(d, 4, 132, 34, 168, (200, 204, 216)); box(d, 8, 136, 30, 146, (60, 70, 96))
    d.rectangle([10, 150, 28, 152], fill=(250, 250, 250)); d.rectangle([24, 138, 27, 141], fill=(90, 255, 110) if int(t * 3) % 2 else (30, 120, 50))
    box(d, 40, 126, 58, 168, (230, 240, 250)); box(d, 42, 118, 56, 126, (150, 210, 250))
    for k in range(3):
        d.ellipse([46, 126 + ((t * 8 + k * 6) % 16), 49, 129 + ((t * 8 + k * 6) % 16)], fill=(255, 255, 255))
    box(d, 130, 130, 150, 168, (150, 160, 180))
    for k in range(3):
        d.rectangle([133, 134 + k * 11, 147, 142 + k * 11], fill=(176, 186, 206)); d.rectangle([138, 137 + k * 11, 142, 139 + k * 11], fill=(250, 220, 90))
    box(d, 154, 150, 168, 168, (196, 110, 80)); d.polygon([(161, 128), (154, 150), (168, 150)], fill=(70, 190, 110), outline=OL)
    d.polygon([(161, 132), (150, 152), (160, 150)], fill=(90, 210, 130))
    box(d, 64, 140, 78, 168, (210, 90, 80)); box(d, 66, 144, 76, 152, (40, 40, 56)); d.ellipse([68, 140, 72, 144], fill=(90, 255, 110) if int(t * 2) % 2 else (30, 120, 50))
    # piso de alfombra con losetas
    d.rectangle([0, 168, LW, LH], fill=(98, 106, 134))
    for r, y in enumerate(range(168, LH, 14)):
        for c, x in enumerate(range(0, LW, 30)):
            d.rectangle([x, y, x + 28, y + 12], fill=(106, 114, 142) if (r + c) % 2 else (94, 102, 128))
    d.rectangle([0, 168, LW, 171], fill=(70, 76, 100))
    img = glow_img(_up(img), (6 * 2, 20 * 2, 68 * 2, 100 * 2), (255, 245, 200), 80, 14)
    _dust(img, t, (10, 40, 340, 330), 16)
    return _finish(img)


def taqueria(t):
    img, d = _new()
    top, bot = (60, 40, 110), (230, 120, 110)
    for y in range(0, 150, 2):
        u = y / 150
        d.rectangle([0, y, LW, y + 2], fill=tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3)))
    for k in range(10):                                           # estrellas
        d.rectangle([(k * 37) % LW, (k * 19) % 40, (k * 37) % LW + 1, (k * 19) % 40 + 1], fill=(255, 255, 255) if (k + int(t * 2)) % 3 else (180, 170, 230))
    cols = [(240, 152, 64), (212, 84, 120), (96, 130, 216), (244, 204, 96), (80, 180, 150)]
    x = -6
    for k in range(5):
        w = 40; hh = [110, 90, 120, 100, 96][k]
        box(d, x, 168 - hh, x + w, 168, cols[k])
        for wy in range(168 - hh + 6, 160, 12):
            for wx in range(x + 5, x + w - 8, 12):
                lit = (wx * 7 + wy * 3 + k) % 5 != 0
                d.rectangle([wx, wy, wx + 6, wy + 8], fill=(255, 232, 140) if lit else sh(cols[k], .55)); d.rectangle([wx, wy, wx + 6, wy], fill=OL)
        x += w
    # puesto de tacos: toldo a rayas con flecos
    d.rectangle([26, 70, 154, 88], fill=OL)
    for k in range(16):
        c = (236, 60, 70) if k % 2 == 0 else (250, 246, 240)
        d.rectangle([27 + k * 8, 71, 34 + k * 8, 86], fill=c)
        d.polygon([(27 + k * 8, 86), (34 + k * 8, 86), (30 + k * 8, 92)], fill=c, outline=OL)
    d.rectangle([26, 70, 154, 72], fill=(255, 130, 130))
    d.rectangle([28, 88, 30, 160], fill=OL); d.rectangle([150, 88, 152, 160], fill=OL)
    # letrero de neón parpadeante + foquitos
    on = int(t * 2.5) % 5 != 0
    box(d, 62, 40, 118, 62, (30, 24, 56))
    txt(d, (90, 51), "TACOS", 14, (255, 90, 190) if on else (120, 50, 100), outline=(110, 20, 90) if on else (40, 20, 50))
    for k in range(8):
        d.rectangle([32 + k * 16, 94, 34 + k * 16, 97], fill=[(255, 230, 110), (255, 130, 170)][(k + int(t * 3)) % 2])
    d.line([30, 94, 150, 94], fill=OL)
    # mostrador con trompo de pastor, salsas, comal y menú
    box(d, 36, 126, 144, 168, (176, 110, 70)); d.rectangle([36, 126, 144, 130], fill=(226, 170, 110))
    for k in range(4):
        d.rectangle([42 + k * 26, 138, 60 + k * 26, 162], outline=(120, 70, 44), width=1)
    ang = t * 3
    for k in range(7):                                            # trompo girando
        wdt = 9 - abs(k - 3) * 1 + int(2 * math.sin(ang + k))
        d.rectangle([62 - wdt // 2 + 6, 104 + k * 3, 62 + wdt // 2 + 8, 106 + k * 3], fill=[(230, 110, 70), (200, 80, 50)][(k + int(t * 4)) % 2])
    d.rectangle([68, 100, 70, 126], fill=OL); d.ellipse([60, 96, 78, 102], fill=(250, 190, 80))
    for k in range(4):
        sy = 96 - ((t * 16 + k * 8) % 26); d.rectangle([66 + math.sin(t * 3 + k) * 4, sy, 69 + math.sin(t * 3 + k) * 4, sy + 3], fill=(240, 240, 250))
    for k, c in enumerate(((236, 60, 60), (90, 190, 90), (250, 190, 60))):
        d.ellipse([92 + k * 14, 118, 102 + k * 14, 128], fill=c, outline=OL); d.rectangle([92 + k * 14, 118, 102 + k * 14, 121], fill=sh(c, 1.2))
    d.rectangle([122, 114, 142, 126], fill=OL); d.rectangle([123, 115, 141, 125], fill=(246, 240, 220)); txt(d, (132, 120), "$1", 8, (200, 40, 40), outline=(246, 240, 220))
    for k in range(3):
        d.ellipse([44 + k * 10, 120, 52 + k * 10, 127], fill=(250, 214, 110), outline=OL)           # tacos
    # banquitos, bici y paloma
    for sx in (14, 156):
        d.rectangle([sx, 150, sx + 12, 154], fill=OL); d.rectangle([sx + 1, 150, sx + 11, 153], fill=(236, 60, 70)); d.rectangle([sx + 5, 154, sx + 7, 168], fill=OL)
    d.ellipse([154, 156, 176, 178], outline=OL, width=2); d.ellipse([132, 156, 154, 178], outline=OL, width=2); d.line([143, 167, 156, 150], fill=(250, 210, 80), width=2); d.line([156, 150, 166, 167], fill=(250, 210, 80), width=2)
    px = 110 + math.sin(t * .8) * 3
    d.ellipse([px, 158, px + 12, 168], fill=(170, 176, 196), outline=OL); d.ellipse([px + 9, 156, px + 15, 162], fill=(150, 156, 180), outline=OL)
    d.rectangle([px + 15, 159, px + 17, 160], fill=(250, 190, 60))
    # adoquines + charco con reflejo del neón
    d.rectangle([0, 168, LW, LH], fill=(88, 84, 112))
    for r, y in enumerate(range(168, LH, 10)):
        for x in range(-(r % 2) * 8, LW, 16):
            d.rectangle([x, y, x + 14, y + 8], fill=(104, 98, 130) if (x + y) % 3 else (96, 90, 122)); d.rectangle([x, y, x + 14, y], fill=(126, 120, 152))
    d.ellipse([20, 252, 90, 270], fill=(70, 76, 130)); d.rectangle([34, 254, 76, 262], fill=(255, 90, 190) if on else (110, 50, 100))
    return _fin(img, lambda b: glow_img(b, (62 * 2, 40 * 2, 118 * 2, 62 * 2), (255, 90, 190), 110 if on else 30, 16))


def calle_vacia(t):
    """Calle post-apocalíptica: coches abandonados, tiendas tapiadas, niebla, cuervos y zombis lejanos."""
    img, d = _new()
    top, bot = (70, 80, 96), (176, 150, 146)
    for y in range(0, 150, 2):
        u = y / 150
        d.rectangle([0, y, LW, y + 2], fill=tuple(int(top[i] + (bot[i] - top[i]) * u) for i in range(3)))
    d.ellipse([28, 44, 62, 78], fill=(236, 226, 206)); d.ellipse([34, 50, 56, 72], fill=(250, 244, 226))
    cols = [(110, 96, 104), (96, 86, 110), (124, 104, 96), (92, 100, 118)]
    x = -8
    for k in range(5):
        w = 40; hh = [120, 96, 130, 104, 112][k]
        box(d, x, 168 - hh, x + w, 168, cols[k % 4])
        for wy in range(168 - hh + 8, 150, 14):
            for wx in range(x + 5, x + w - 9, 13):
                broken = (wx * 5 + wy * 3 + k) % 4 == 0
                d.rectangle([wx, wy, wx + 7, wy + 9], fill=(30, 28, 44) if not broken else (70, 76, 96))
                if broken:
                    d.line([wx, wy, wx + 7, wy + 9], fill=(150, 156, 176))
                if (wx + wy + k) % 11 == 0 and int(t * 2) % 2:
                    d.rectangle([wx + 1, wy + 1, wx + 6, wy + 8], fill=(255, 220, 130))
        x += w
    # tienda tapiada con tablones y letrero que parpadea
    box(d, 60, 124, 120, 168, (84, 74, 92)); d.rectangle([62, 134, 118, 164], fill=(30, 28, 44))
    for k in range(4):
        d.rectangle([64, 138 + k * 7, 116, 142 + k * 7], fill=(150, 112, 76)); d.rectangle([64, 138 + k * 7, 116, 138 + k * 7], fill=(190, 150, 100))
    on = int(t * 3) % 6 != 0
    box(d, 66, 112, 114, 124, (40, 36, 60)); txt(d, (90, 118), "SUPER", 8, (255, 90, 90) if on else (110, 50, 60), outline=(40, 20, 30))
    # poste caído, grafiti y basura que rueda
    d.line([150, 100, 168, 168], fill=OL, width=3); d.line([150, 100, 168, 168], fill=(120, 124, 140), width=1)
    txt(d, (24, 140), "AYUDA", 8, (240, 80, 90), outline=OL)
    # asfalto agrietado, línea y coches
    d.rectangle([0, 168, LW, LH], fill=(78, 80, 96))
    for k in range(0, LW, 24):
        d.rectangle([k + 4, 232, k + 18, 235], fill=(210, 190, 90))
    d.line([20, 180, 40, 200, 34, 224], fill=(44, 44, 58)); d.line([120, 190, 140, 214, 132, 240], fill=(44, 44, 58))
    d.rectangle([0, 168, LW, 174], fill=(120, 120, 140))
    box(d, 118, 150, 172, 176, (170, 70, 70)); box(d, 128, 138, 160, 152, (150, 60, 60)); d.rectangle([132, 141, 156, 150], fill=(110, 150, 190))
    d.line([132, 141, 156, 150], fill=(210, 224, 240))
    d.ellipse([124, 170, 138, 182], fill=OL); d.ellipse([152, 170, 166, 182], fill=OL)
    box(d, 2, 156, 38, 180, (80, 110, 170)); d.rectangle([6, 160, 20, 170], fill=(110, 150, 190)); d.ellipse([6, 174, 18, 186], fill=OL)
    # zombis lejanos que se tambalean y cuervos
    for zx, ph in ((140, 0.0), (160, 1.7)):
        sx = zx + math.sin(t * 1.2 + ph) * 3
        d.rectangle([sx, 138, sx + 5, 156], fill=(40, 60, 48)); d.rectangle([sx + 1, 132, sx + 4, 138], fill=(80, 110, 80))
        d.rectangle([sx - 4, 140 + int(math.sin(t * 2 + ph) * 2), sx, 143], fill=(40, 60, 48))
    for bx in (20, 70, 120):
        px = (bx + t * 9) % (LW + 20) - 10; py = 30 + math.sin(t * 2 + bx) * 4
        w2 = 2 if int(t * 7 + bx) % 2 else -1
        d.line([px - 3, py + w2, px, py], fill=OL); d.line([px, py, px + 3, py + w2], fill=OL)
    # primer plano: el suelo también cuenta la historia (grietas, alcantarilla, conos, cinta, bolsas, charcos)
    d.ellipse([20, 250, 56, 262], fill=(60, 62, 78), outline=OL); d.ellipse([26, 252, 50, 260], outline=(100, 104, 124))
    for gx in range(26, 52, 5):
        d.line([gx, 252, gx + 2, 260], fill=(100, 104, 124))
    box(d, 100, 262, 112, 280, (240, 130, 50)); d.rectangle([100, 268, 112, 272], fill=(250, 250, 250)); d.rectangle([97, 280, 115, 283], fill=(200, 100, 40))
    d.line([60, 292, 84, 300, 108, 292], fill=(250, 214, 60), width=2); d.line([60, 296, 84, 304, 108, 296], fill=(30, 18, 44), width=1)
    d.line([8, 270, 30, 290, 24, 312], fill=(44, 44, 58)); d.line([130, 252, 150, 276, 140, 306], fill=(44, 44, 58))
    d.ellipse([130, 286, 170, 298], fill=(70, 78, 112)); d.ellipse([136, 288, 158, 294], fill=(100, 110, 150))
    d.polygon([(70, 306), (84, 300), (92, 310), (80, 314)], fill=(220, 220, 230), outline=OL)         # papeles tirados
    d.rectangle([150, 306, 166, 318], fill=(250, 200, 70), outline=OL); d.rectangle([152, 308, 156, 316], fill=(255, 228, 130))   # bolsa de papas vacía
    d.rectangle([0, 318, LW, LH], fill=(66, 68, 84))
    # niebla que avanza
    fog = Image.new("RGBA", (LW, LH), (0, 0, 0, 0)); fd = ImageDraw.Draw(fog)
    for k in range(5):
        fx = (k * 50 + t * 6) % (LW + 60) - 30
        fd.ellipse([fx - 30, 150 + (k % 2) * 14, fx + 30, 176 + (k % 2) * 14], fill=(210, 214, 226, 64))
    img.alpha_composite(fog)
    return _fin(img)


def super_vacio(t):
    """Supermercado vacío: pasillos con estantes, carritos tirados, luces que parpadean y piso de losetas."""
    img, d = _new()
    d.rectangle([0, 0, LW, 168], fill=(214, 220, 214))
    fl = 0.55 if int(t * 7) % 9 == 0 else 1.0
    for lx in (10, 70, 130):
        d.rectangle([lx, 2, lx + 40, 8], fill=OL); d.rectangle([lx + 1, 3, lx + 39, 7], fill=(int(255 * fl), int(252 * fl), int(226 * fl)))
    d.rectangle([0, 150, LW, 168], fill=(176, 184, 176))
    box(d, 0, 20, LW, 36, (210, 70, 70)); txt(d, (90, 28), "SUPER MERCADO · OFERTAS", 8, (255, 255, 255), outline=(150, 40, 40))
    rnd = random.Random(4)
    for sx in (4, 62, 120):
        box(d, sx, 54, sx + 54, 168, (150, 140, 160))
        for r in range(4):
            by = 58 + r * 26
            d.rectangle([sx + 2, by + 22, sx + 52, by + 25], fill=(110, 100, 120))
            x = sx + 4
            while x < sx + 48:
                w = rnd.randint(5, 8); h = rnd.randint(12, 20)
                if rnd.random() < .45:
                    d.rectangle([x, by + 22 - h, x + w, by + 22], fill=rnd.choice([(230, 90, 70), (250, 200, 70), (90, 190, 120), (90, 150, 230), (240, 140, 180)]), outline=OL)
                x += w + 2
    box(d, 150, 140, 174, 168, (200, 200, 214)); d.rectangle([152, 144, 172, 148], fill=(90, 90, 110))
    d.rectangle([154, 150, 170, 152], fill=(30, 40, 60)); d.rectangle([156, 144, 160, 146], fill=(90, 255, 110) if int(t * 2) % 2 else (30, 110, 40))
    d.rectangle([0, 168, LW, LH], fill=(200, 206, 214))
    for r, y in enumerate(range(168, LH, 16)):
        for c, x in enumerate(range(0, LW, 32)):
            d.rectangle([x, y, x + 30, y + 14], fill=(210, 216, 224) if (r + c) % 2 else (186, 192, 204))
    for cx_, cy_ in ((100, 200), (30, 240)):          # carritos tirados
        d.rectangle([cx_, cy_, cx_ + 22, cy_ + 14], outline=OL, width=1); d.line([cx_ - 3, cy_ - 6, cx_ + 2, cy_], fill=OL)
        d.ellipse([cx_ + 2, cy_ + 14, cx_ + 8, cy_ + 20], fill=OL); d.ellipse([cx_ + 16, cy_ + 14, cx_ + 22, cy_ + 20], fill=OL)
        for gx in range(cx_ + 2, cx_ + 22, 4):
            d.line([gx, cy_, gx, cy_ + 14], fill=(150, 150, 170))
    d.ellipse([60, 250, 120, 262], fill=(240, 230, 210)); d.rectangle([72, 252, 108, 258], fill=(255, 200, 70))   # papas regadas
    return _fin(img)

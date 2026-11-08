"""Props pixel-art con el mismo tratamiento que los sprites: contorno oscuro de 1 px, 3 tonos (base, sombra, luz) y bordes con color."""
import math
import numpy as np
from PIL import Image, ImageDraw
from sprites import Paint
from lib import shade

_c = {}
def cached(k, f):
    if k not in _c: _c[k] = f()
    return _c[k]

WOOD = (176, 116, 70); WOOD_D = (120, 76, 48); WOOD_L = (222, 160, 104)
CREAM = (250, 242, 222)


def baby_crib():
    def mk():
        P = Paint(52, 40)
        # patas y postes con remates
        for x in (3, 46):
            P.add(lambda d, x=x: d.rectangle([x, 8, x + 3, 38], fill=255), WOOD, edge_k=.45)
            P.add(lambda d, x=x: d.ellipse([x - 1, 3, x + 4, 9], fill=255), WOOD_L, edge_k=.5)
        # colchón + manta con lunares + bebé
        P.add(lambda d: d.rounded_rectangle([6, 22, 46, 32], radius=3, fill=255), (250, 240, 232), edge_k=.55)
        P.add(lambda d: d.ellipse([16, 8, 32, 24], fill=255), (255, 214, 184), edge_k=.5)                 # cabecita
        P.add(lambda d: d.polygon([(16, 13), (19, 7), (25, 5), (31, 8), (32, 14), (27, 11), (21, 11)], fill=255), (150, 98, 62), edge=False, hi=False)   # pelito
        P.px(21, 17, (60, 40, 40)); P.px(22, 17, (60, 40, 40)); P.px(27, 17, (60, 40, 40)); P.px(28, 17, (60, 40, 40))   # ojos cerrados
        P.px(24, 20, (214, 100, 110)); P.px(18, 19, (255, 150, 160)); P.px(30, 19, (255, 150, 160))
        P.add(lambda d: d.rounded_rectangle([12, 22, 44, 36], radius=3, fill=255), (255, 150, 180), edge_k=.5)  # manta rosa
        for (x, y) in ((17, 29), (24, 31), (31, 28), (38, 31), (20, 33), (35, 34)): P.px(x, y, (255, 226, 236))
        P.rect(12, 22, 44, 23, (255, 196, 214))
        # barrotes y travesaños delante
        for x in range(8, 46, 5):
            P.add(lambda d, x=x: d.rectangle([x, 26, x + 1, 38], fill=255), WOOD_L, edge_k=.45, sh=False)
        P.add(lambda d: d.rectangle([2, 24, 49, 27], fill=255), WOOD, edge_k=.45)
        P.add(lambda d: d.rectangle([2, 34, 49, 37], fill=255), WOOD_D, edge_k=.45)
        # móvil de estrellitas colgando
        P.rect(26, 0, 26, 4, (180, 180, 200))
        return P.final()
    return cached('crib', mk)


def stroller():
    def mk():
        P = Paint(46, 46)
        P.add(lambda d: d.pieslice([2, 2, 32, 34], 180, 360, fill=255), (112, 96, 176), edge_k=.45)        # capota
        P.add(lambda d: d.pieslice([6, 6, 28, 30], 180, 360, fill=255), (82, 66, 140), edge=False, hi=False, sh=False)
        for a in (200, 230, 260, 290, 320):                                                              # varillas de la capota
            x = 17 + int(15 * math.cos(math.radians(a))); y = 18 + int(15 * math.sin(math.radians(a)))
            P.line([(17, 18), (x, y)], (150, 132, 210))
        P.add(lambda d: d.rounded_rectangle([2, 18, 36, 32], radius=4, fill=255), (246, 126, 160), edge_k=.5)   # cuerpo
        P.rect(4, 22, 34, 22, (255, 200, 216)); P.rect(4, 26, 34, 26, (206, 92, 126))
        P.add(lambda d: d.ellipse([10, 12, 24, 22], fill=255), (255, 214, 184), edge_k=.5)                 # cabeza del bebé asomando
        P.px(14, 17, (60, 40, 40)); P.px(19, 17, (60, 40, 40)); P.px(16, 19, (214, 100, 110))
        P.add(lambda d: d.rectangle([36, 8, 38, 30], fill=255), (70, 66, 90), edge_k=.5)                  # manillar
        P.add(lambda d: d.rounded_rectangle([34, 6, 44, 10], radius=2, fill=255), (50, 46, 70), edge_k=.5)
        P.add(lambda d: d.rectangle([14, 32, 16, 38], fill=255), (110, 110, 130), edge_k=.5)
        for cx in (8, 32):
            P.add(lambda d, cx=cx: d.ellipse([cx - 5, 34, cx + 5, 44], fill=255), (46, 46, 62), edge_k=.5, sh=False)
            P.add(lambda d, cx=cx: d.ellipse([cx - 2, 37, cx + 2, 41], fill=255), (170, 170, 190), edge=False, sh=False, hi=False)
        return P.final()
    return cached('stroller', mk)


def book_open(w=60, h=30, lines=6, glow=False):
    def mk():
        P = Paint(w, h)
        c = w // 2
        P.add(lambda d: d.polygon([(1, h - 6), (c, h - 11), (w - 2, h - 6), (w - 2, h - 1), (c, h - 4), (1, h - 1)], fill=255), (150, 70, 60), edge_k=.5)          # tapas
        P.add(lambda d: d.polygon([(3, 6), (c - 1, 2), (c - 1, h - 9), (3, h - 5)], fill=255), (254, 250, 238), edge_k=.6)                                      # página izq.
        P.add(lambda d: d.polygon([(c + 1, 2), (w - 4, 6), (w - 4, h - 5), (c + 1, h - 9)], fill=255), (248, 242, 226), edge_k=.6)
        P.rect(c - 1, 2, c + 1, h - 8, (200, 170, 130))                                                                                                         # lomo
        for i in range(lines):
            y = 8 + i * 3
            P.line([(6, y), (c - 5, y - 1)], (110, 100, 140)); P.line([(c + 4, y - 1), (w - 7, y)], (110, 100, 140))
        P.rect(4, h - 7, c - 2, h - 6, (236, 228, 208)); P.rect(c + 2, h - 7, w - 5, h - 6, (232, 224, 204))                                                    # canto de las páginas
        return P.final()
    return cached(('bopen', w, h, lines), mk)


def book_closed(col=(200, 70, 80), w=22, h=7, title=True):
    def mk():
        P = Paint(w, h)
        P.add(lambda d: d.rectangle([0, 0, w - 1, h - 1], fill=255), col, edge_k=.45)
        P.rect(w - 3, 1, w - 2, h - 2, (244, 236, 214))
        P.rect(1, 1, 1, h - 2, shade(col, 1.3)); P.rect(3, 1, 3, h - 2, (240, 200, 90)); P.rect(w - 6, 1, w - 6, h - 2, (240, 200, 90))
        if title: P.rect(6, 2, w - 8, 2, (250, 232, 170)); P.rect(7, 4, w - 10, 4, shade(col, .75)) if h > 6 else None
        return P.final()
    return cached(('bclosed', col, w, h, title), mk)


def envelope(w=28, h=18):
    def mk():
        P = Paint(w, h)
        P.add(lambda d: d.rectangle([0, 0, w - 1, h - 1], fill=255), (246, 238, 216), edge_k=.55)
        P.add(lambda d: d.polygon([(0, 0), (w - 1, 0), (w // 2, h // 2 + 1)], fill=255), (234, 222, 196), edge_k=.6, sh=False)
        P.add(lambda d: d.ellipse([w // 2 - 3, h // 2 - 2, w // 2 + 3, h // 2 + 4], fill=255), (190, 50, 60), edge_k=.5)          # sello de lacre
        P.line([(0, h - 1), (w // 2 - 3, h // 2 + 2)], (206, 192, 164)); P.line([(w - 1, h - 1), (w // 2 + 3, h // 2 + 2)], (206, 192, 164))
        return P.final()
    return cached(('env', w, h), mk)


def teacup():
    def mk():
        P = Paint(18, 12)
        P.add(lambda d: d.ellipse([0, 8, 17, 11], fill=255), (240, 236, 228), edge_k=.55)                   # plato
        P.add(lambda d: d.rounded_rectangle([3, 2, 13, 9], radius=3, fill=255), (252, 250, 244), edge_k=.55)
        P.add(lambda d: d.ellipse([13, 3, 17, 8], outline=255, width=1, fill=0), (252, 250, 244), edge_k=.55, sh=False)
        P.rect(4, 3, 12, 3, (124, 74, 46))                                                                  # té
        return P.final()
    return cached('cup', mk)


def stamp_paper():
    def mk():
        P = Paint(22, 14)
        P.add(lambda d: d.rectangle([0, 0, 21, 13], fill=255), (250, 246, 232), edge_k=.6)
        for y in (3, 6, 9): P.line([(2, y), (19, y)], (150, 146, 170))
        P.rect(14, 2, 19, 4, (214, 60, 70))
        return P.final()
    return cached('paper', mk)


def lamp_table():
    def mk():
        P = Paint(18, 26)
        P.add(lambda d: d.polygon([(2, 12), (16, 12), (13, 1), (5, 1)], fill=255), (255, 214, 120), edge_k=.5)         # pantalla
        P.rect(8, 12, 10, 21, (130, 100, 70)); 
        P.add(lambda d: d.rounded_rectangle([3, 21, 15, 25], radius=2, fill=255), (130, 100, 70), edge_k=.5)
        return P.final()
    return cached('lamp', mk)


def plant():
    def mk():
        P = Paint(22, 30)
        for (x0, y0, x1, y1, c) in ((11, 14, 3, 3, (70, 170, 90)), (11, 14, 18, 2, (60, 150, 80)), (11, 14, 11, 0, (96, 196, 110)), (11, 14, 1, 12, (60, 160, 84)), (11, 14, 20, 11, (80, 180, 96))):
            P.add(lambda d, a=(x0, y0, x1, y1): d.polygon([(a[0] - 2, a[1]), (a[0] + 2, a[1]), (a[2], a[3])], fill=255), c, edge_k=.5)
        P.add(lambda d: d.polygon([(4, 18), (18, 18), (16, 29), (6, 29)], fill=255), (206, 104, 70), edge_k=.5)
        P.rect(4, 18, 18, 19, (230, 140, 100))
        return P.final()
    return cached('plant', mk)


def armchair():
    def mk():
        P = Paint(40, 34)
        P.add(lambda d: d.rounded_rectangle([4, 2, 35, 22], radius=6, fill=255), (176, 60, 70), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([0, 12, 12, 30], radius=4, fill=255), (200, 76, 86), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([27, 12, 39, 30], radius=4, fill=255), (200, 76, 86), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([8, 18, 31, 29], radius=3, fill=255), (214, 92, 100), edge_k=.5)
        for x in (3, 34): P.rect(x, 30, x + 2, 33, (90, 56, 40))
        return P.final()
    return cached('armchair', mk)


def barrel():
    def mk():
        P = Paint(16, 20)
        P.add(lambda d: d.rounded_rectangle([1, 1, 14, 18], radius=4, fill=255), (156, 104, 62), edge_k=.5)
        for y in (5, 14): P.rect(1, y, 14, y + 1, (90, 90, 106))
        for x in (5, 9): P.line([(x, 2), (x, 17)], (120, 76, 46))
        return P.final()
    return cached('barrel', mk)


def pendant(col=(255, 196, 96)):
    def mk():
        P = Paint(18, 14)
        P.add(lambda d: d.polygon([(1, 13), (16, 13), (12, 2), (5, 2)], fill=255), col, edge_k=.5)
        P.rect(8, 0, 9, 2, (60, 50, 50)); P.rect(3, 12, 14, 12, shade(col, 1.2))
        return P.final()
    return cached(('pend', col), mk)


def money_bill():
    def mk():
        P = Paint(16, 8)
        P.add(lambda d: d.rectangle([0, 0, 15, 7], fill=255), (120, 190, 120), edge_k=.5)
        P.add(lambda d: d.ellipse([5, 1, 10, 6], fill=255), (200, 236, 190), edge=False, sh=False, hi=False)
        P.rect(2, 3, 3, 4, (70, 130, 80)); P.rect(12, 3, 13, 4, (70, 130, 80))
        return P.final()
    return cached('bill', mk)


def bill_red():
    def mk():
        P = Paint(20, 14)
        P.add(lambda d: d.rectangle([0, 0, 19, 13], fill=255), (252, 248, 236), edge_k=.6)
        P.rect(2, 2, 17, 4, (206, 54, 66)); 
        for y in (6, 8, 10): P.line([(2, y), (15, y)], (150, 146, 170))
        P.rect(13, 9, 17, 11, (206, 54, 66))
        return P.final()
    return cached('billred', mk)


def keep(c, img, x, y, flip=False):
    """pega un prop (RGBA) con su esquina sup-izq en (x, y)."""
    if flip: img = img.transpose(Image.FLIP_LEFT_RIGHT)
    c.im.alpha_composite(img, (int(x), int(y))) if x >= 0 and y >= 0 else c.im.paste(img, (int(x), int(y)), img)


def palm():
    def mk():
        P = Paint(40, 70)
        for i, (dx, dy) in enumerate(((-16, -2), (-10, -10), (0, -14), (10, -10), (16, -2), (-14, 6), (14, 6))):
            cx, cy = 20, 16
            P.add(lambda d, dx=dx, dy=dy: d.polygon([(cx, cy), (cx + dx // 2, cy + dy - 4), (cx + dx * 2 // 1 if abs(dx) < 15 else cx + dx + dx // 3, cy + dy + 2)], fill=255), (70 + i * 6, 170 - i * 4, 90), edge_k=.5)
        P.add(lambda d: d.polygon([(18, 16), (23, 16), (24, 69), (17, 69)], fill=255), (150, 100, 64), edge_k=.5)
        for y in range(22, 68, 6): P.rect(17, y, 24, y, (110, 72, 46))
        P.add(lambda d: d.ellipse([16, 14, 24, 22], fill=255), (110, 70, 44), edge_k=.5)
        return P.final()
    return cached('palm', mk)


def car():
    def mk():
        P = Paint(56, 26)
        P.add(lambda d: d.rounded_rectangle([2, 10, 53, 20], radius=4, fill=255), (200, 60, 70), edge_k=.5)
        P.add(lambda d: d.polygon([(12, 10), (18, 2), (38, 2), (46, 10)], fill=255), (210, 80, 90), edge_k=.5)
        P.add(lambda d: d.polygon([(15, 9), (20, 4), (28, 4), (28, 9)], fill=255), (150, 200, 240), edge=False, sh=False, hi=False)
        P.add(lambda d: d.polygon([(30, 9), (30, 4), (37, 4), (43, 9)], fill=255), (150, 200, 240), edge=False, sh=False, hi=False)
        P.rect(50, 13, 53, 15, (255, 236, 150)); P.rect(2, 13, 4, 15, (255, 80, 80))
        for cx in (13, 42):
            P.add(lambda d, cx=cx: d.ellipse([cx - 5, 15, cx + 5, 25], fill=255), (36, 36, 50), edge_k=.5, sh=False)
            P.add(lambda d, cx=cx: d.ellipse([cx - 2, 18, cx + 2, 22], fill=255), (190, 190, 206), edge=False, sh=False, hi=False)
        return P.final()
    return cached('car', mk)


def chair_wait():
    def mk():
        P = Paint(20, 24)
        P.add(lambda d: d.rounded_rectangle([2, 2, 17, 12], radius=2, fill=255), (96, 110, 176), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([1, 11, 18, 17], radius=2, fill=255), (116, 130, 200), edge_k=.5)
        P.rect(3, 17, 4, 23, (60, 60, 80)); P.rect(15, 17, 16, 23, (60, 60, 80))
        return P.final()
    return cached('chair', mk)


def check_prop(w=84, h=38, amount=True, filled=1.0):
    def mk():
        P = Paint(w, h)
        P.add(lambda d: d.rectangle([0, 0, w - 1, h - 1], fill=255), (236, 246, 226), edge_k=.55)
        P.rect(2, 2, w - 3, 3, (150, 190, 150)); P.rect(2, h - 4, w - 3, h - 3, (150, 190, 150))
        for x in range(4, w - 4, 4): P.px(x, 5, (170, 200, 170))
        P.rect(w - 22, 8, w - 4, 8, (120, 150, 120)); P.rect(6, h - 10, 30, h - 10, (120, 150, 120)); P.rect(w - 34, h - 10, w - 6, h - 10, (120, 150, 120))
        P.add(lambda d: d.ellipse([w - 18, 11, w - 6, 23], fill=255), (222, 190, 90), edge_k=.55)
        return P.final()
    return cached(('check', w, h, amount, filled), mk)


def calendar_page():
    def mk():
        P = Paint(28, 30)
        P.add(lambda d: d.rectangle([0, 0, 27, 29], fill=255), (252, 250, 240), edge_k=.55)
        P.rect(0, 0, 27, 7, (210, 60, 70)); P.rect(6, 1, 7, 3, (250, 240, 230)); P.rect(20, 1, 21, 3, (250, 240, 230))
        for r in range(3):
            for c_ in range(5): P.rect(3 + c_ * 5, 12 + r * 5, 5 + c_ * 5, 14 + r * 5, (170, 170, 190))
        return P.final()
    return cached('cal', mk)


def box_cardboard(w=22, h=16):
    def mk():
        P = Paint(w, h)
        P.add(lambda d: d.rectangle([0, 0, w - 1, h - 1], fill=255), (196, 150, 98), edge_k=.5)
        P.rect(w // 2 - 2, 0, w // 2 + 2, h - 1, (230, 196, 140)); P.rect(2, 3, 7, 5, (250, 240, 220))
        return P.final()
    return cached(('box', w, h), mk)


def camera_pro():
    def mk():
        P = Paint(20, 16)
        P.add(lambda d: d.rounded_rectangle([1, 4, 18, 14], radius=2, fill=255), (50, 52, 70), edge_k=.5)
        P.add(lambda d: d.ellipse([6, 5, 14, 13], fill=255), (150, 170, 210), edge_k=.5)
        P.rect(3, 1, 8, 4, (90, 92, 110))
        return P.final()
    return cached('cam', mk)


def guitar():
    def mk():
        P = Paint(26, 52)
        P.add(lambda d: d.ellipse([2, 26, 24, 50], fill=255), (200, 130, 70), edge_k=.5)
        P.add(lambda d: d.ellipse([6, 14, 20, 32], fill=255), (214, 146, 84), edge_k=.5)
        P.add(lambda d: d.ellipse([9, 30, 17, 38], fill=255), (50, 30, 24), edge=False, sh=False, hi=False)
        P.add(lambda d: d.rectangle([11, 0, 15, 22], fill=255), (110, 70, 44), edge_k=.5)
        P.rect(10, 0, 16, 4, (70, 44, 30))
        for y in (6, 11, 16): P.rect(11, y, 15, y, (230, 220, 190))
        return P.final()
    return cached('guitar', mk)


def mic_stand():
    def mk():
        P = Paint(12, 60)
        P.add(lambda d: d.rectangle([5, 10, 6, 56], fill=255), (60, 62, 80), edge_k=.5)
        P.add(lambda d: d.ellipse([1, 56, 10, 59], fill=255), (60, 62, 80), edge_k=.5)
        P.add(lambda d: d.ellipse([2, 0, 9, 10], fill=255), (190, 192, 210), edge_k=.5)
        return P.final()
    return cached('mic', mk)


def vinyl(r=12):
    def mk():
        P = Paint(r * 2 + 1, r * 2 + 1)
        P.add(lambda d: d.ellipse([0, 0, r * 2, r * 2], fill=255), (30, 30, 40), edge_k=.6, sh=False)
        P.add(lambda d: d.ellipse([r // 2, r // 2, r + r // 2, r + r // 2], fill=255), (60, 60, 80), edge=False, sh=False, hi=False)
        P.add(lambda d: d.ellipse([r - 3, r - 3, r + 3, r + 3], fill=255), (210, 70, 90), edge=False, sh=False, hi=False)
        P.rect(r - 8, 3, r - 4, 3, (120, 120, 150))
        return P.final()
    return cached(('vinyl', r), mk)


def contract():
    def mk():
        P = Paint(34, 44)
        P.add(lambda d: d.rectangle([0, 0, 33, 43], fill=255), (252, 248, 236), edge_k=.6)
        for y in range(6, 30, 4): P.line([(4, y), (29, y)], (150, 146, 170))
        P.rect(4, 34, 16, 34, (60, 60, 120)); P.add(lambda d: d.ellipse([22, 32, 30, 40], fill=255), (190, 50, 60), edge_k=.5)
        return P.final()
    return cached('contract', mk)


def bus():
    def mk():
        P = Paint(92, 44)
        P.add(lambda d: d.rounded_rectangle([1, 4, 90, 36], radius=5, fill=255), (230, 190, 70), edge_k=.5)
        P.rect(2, 22, 89, 24, (60, 60, 80))
        for k in range(7): P.rect(6 + k * 12, 8, 14 + k * 12, 18, (150, 200, 240))
        P.rect(78, 8, 88, 18, (150, 200, 240))
        for cx in (18, 70):
            P.add(lambda d, cx=cx: d.ellipse([cx - 7, 30, cx + 7, 43], fill=255), (36, 36, 50), edge_k=.5, sh=False)
            P.add(lambda d, cx=cx: d.ellipse([cx - 3, 34, cx + 3, 40], fill=255), (190, 190, 206), edge=False, sh=False, hi=False)
        return P.final()
    return cached('bus', mk)


# ================================================================ historia Hawking
def wheelchair_back(r=14):
    """respaldo y estructura (va DETRÁS de la persona sentada)."""
    def mk():
        w = r * 4 + 6; h = r * 2 + 12
        P = Paint(w, h)
        P.add(lambda d: d.rounded_rectangle([r + 3, 2, w - r - 4, h - 8], radius=3, fill=255), (54, 58, 80), edge_k=.5)
        P.add(lambda d: d.rectangle([r + 5, h - 12, w - r - 6, h - 6], fill=255), (40, 44, 64), edge_k=.5)
        return P.final()
    return cached(('wcb', r), mk)


def wheelchair_front(r=14):
    """ruedas, reposabrazos y reposapiés (va DELANTE)."""
    def mk():
        w = r * 4 + 6; h = r * 2 + 12
        P = Paint(w, h)
        for cx in (r + 2, w - r - 3):
            P.add(lambda d, cx=cx: d.ellipse([cx - r, h - 2 * r - 2, cx + r, h - 2], fill=255), (36, 38, 54), edge_k=.5, sh=False)
            P.add(lambda d, cx=cx: d.ellipse([cx - r + 3, h - 2 * r + 1, cx + r - 3, h - 5], fill=255), (0, 0, 0), edge=False, sh=False, hi=False)
            P.a[(P.a[..., 3] > 0) & (P.a[..., :3] == 0).all(-1)] = 0                                       # hueco de la rueda
            P.add(lambda d, cx=cx: d.ellipse([cx - 2, h - r - 4, cx + 2, h - r], fill=255), (190, 192, 210), edge=False, sh=False, hi=False)
            for k in range(8):
                a = k * math.pi / 4; P.line([(cx, h - r - 2), (cx + int((r - 3) * math.cos(a)), h - r - 2 + int((r - 3) * math.sin(a)))], (130, 134, 160))
        P.add(lambda d: d.rounded_rectangle([r + 4, h - 2 * r + 2, r + 9, h - 14], radius=1, fill=255), (80, 84, 112), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([w - r - 10, h - 2 * r + 2, w - r - 5, h - 14], radius=1, fill=255), (80, 84, 112), edge_k=.5)
        return P.final()
    return cached(('wcf', r), mk)


def telescope():
    def mk():
        P = Paint(34, 48)
        P.add(lambda d: d.polygon([(4, 30), (26, 2), (31, 8), (9, 36)], fill=255), (190, 150, 90), edge_k=.5)
        P.add(lambda d: d.polygon([(2, 32), (8, 24), (13, 30), (6, 38)], fill=255), (120, 84, 50), edge_k=.5)
        P.line([(8, 36), (4, 47)], (96, 70, 50)); P.line([(8, 36), (14, 47)], (96, 70, 50)); P.line([(8, 36), (22, 47)], (96, 70, 50))
        P.rect(26, 2, 31, 8, (240, 214, 150))
        return P.final()
    return cached('telescope', mk)


def hospital_bed():
    def mk():
        P = Paint(76, 40)
        P.add(lambda d: d.rounded_rectangle([2, 14, 73, 28], radius=3, fill=255), (240, 244, 252), edge_k=.55)
        P.add(lambda d: d.rounded_rectangle([4, 10, 22, 20], radius=4, fill=255), (252, 252, 255), edge_k=.55)
        P.add(lambda d: d.rounded_rectangle([20, 16, 73, 28], radius=3, fill=255), (130, 190, 210), edge_k=.55)
        P.rect(2, 4, 3, 36, (170, 176, 200)); P.rect(72, 8, 73, 36, (170, 176, 200)); P.rect(2, 4, 8, 4, (170, 176, 200))
        P.rect(2, 28, 73, 30, (150, 156, 180)); P.rect(6, 31, 8, 38, (90, 96, 120)); P.rect(66, 31, 68, 38, (90, 96, 120))
        return P.final()
    return cached('hbed', mk)


def monitor_ecg(t_unused=0):
    def mk():
        P = Paint(40, 34)
        P.add(lambda d: d.rounded_rectangle([0, 0, 39, 26], radius=3, fill=255), (40, 44, 60), edge_k=.5)
        P.rect(3, 3, 36, 22, (10, 30, 24)); P.rect(14, 26, 25, 32, (70, 74, 96)); P.rect(8, 32, 31, 33, (70, 74, 96))
        return P.final()
    return cached('ecg', mk)


def computer_old():
    def mk():
        P = Paint(40, 38)
        P.add(lambda d: d.rounded_rectangle([2, 0, 37, 26], radius=3, fill=255), (214, 208, 190), edge_k=.5)
        P.rect(5, 3, 34, 22, (20, 50, 40)); P.rect(14, 26, 25, 31, (190, 184, 168))
        P.add(lambda d: d.rounded_rectangle([0, 31, 39, 37], radius=2, fill=255), (200, 194, 176), edge_k=.5)
        for x in range(3, 37, 4): P.rect(x, 33, x + 2, 34, (110, 106, 96))
        return P.final()
    return cached('pc', mk)


def frame_portrait(w=34, h=42, wig=True):
    """retrato enmarcado de un sabio con peluca (Newton)."""
    def mk():
        P = Paint(w, h)
        P.add(lambda d: d.rectangle([0, 0, w - 1, h - 1], fill=255), (190, 140, 60), edge_k=.5)
        P.rect(3, 3, w - 4, h - 4, (46, 38, 60))
        c = w // 2
        P.add(lambda d: d.ellipse([c - 10, 8, c + 10, 34], fill=255), (210, 200, 210), edge=False, sh=False, hi=False)             # peluca
        P.add(lambda d: d.ellipse([c - 6, 12, c + 6, 28], fill=255), (240, 200, 168), edge=False, sh=False, hi=False)              # cara
        P.rect(c - 3, 19, c - 2, 19, (50, 40, 40)); P.rect(c + 2, 19, c + 3, 19, (50, 40, 40)); P.rect(c - 1, 24, c + 1, 24, (180, 90, 90))
        P.add(lambda d: d.rectangle([c - 12, h - 10, c + 12, h - 4], fill=255), (60, 70, 110), edge=False, sh=False, hi=False)
        return P.final()
    return cached(('frame', w, h), mk)


def heart(sz=9, col=(255, 90, 130)):
    def mk():
        P = Paint(sz, sz)
        P.add(lambda d: d.polygon([(sz // 2, sz - 1), (0, sz // 3), (1, 0), (sz // 3, 0), (sz // 2, sz // 4), (sz - sz // 3, 0), (sz - 2, 0), (sz - 1, sz // 3)], fill=255), col, edge_k=.55)
        return P.final()
    return cached(('heart', sz, col), mk)


def book_stack(n=4):
    def mk():
        P = Paint(34, 8 * n + 2)
        cols = ((60, 90, 200), (220, 70, 90), (240, 200, 70), (90, 190, 120))
        for i in range(n):
            y = 8 * (n - 1 - i) + 1; w = 30 - (i % 2) * 3
            P.add(lambda d, y=y, w=w: d.rectangle([1, y, w, y + 6], fill=255), cols[i % 4], edge_k=.45)
            P.rect(w - 2, y + 1, w, y + 5, (244, 236, 214)); P.rect(3, y + 3, 9, y + 3, (250, 232, 170))
        return P.final()
    return cached(('stack', n), mk)


def cane():
    def mk():
        P = Paint(14, 40)
        P.add(lambda d: d.rectangle([5, 6, 7, 39], fill=255), (120, 84, 50), edge_k=.5)
        P.add(lambda d: d.arc([3, 0, 13, 10], 180, 360, fill=255, width=3), (120, 84, 50), edge_k=.5)
        return P.final()
    return cached('cane', mk)


# ================================================================ historia Disney
def film_reel(r=10):
    def mk():
        P = Paint(r * 2 + 1, r * 2 + 1)
        P.add(lambda d: d.ellipse([0, 0, r * 2, r * 2], fill=255), (50, 52, 70), edge_k=.5)
        for k in range(6):
            a = k * math.pi / 3; cx = r + int((r - 4) * math.cos(a)); cy = r + int((r - 4) * math.sin(a))
            P.add(lambda d, cx=cx, cy=cy: d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=255), (14, 14, 24), edge=False, sh=False, hi=False)
        P.add(lambda d: d.ellipse([r - 2, r - 2, r + 2, r + 2], fill=255), (190, 192, 210), edge=False, sh=False, hi=False)
        return P.final()
    return cached(('reel', r), mk)


def drawing_desk():
    def mk():
        P = Paint(64, 44)
        P.add(lambda d: d.polygon([(4, 12), (60, 12), (64, 30), (0, 30)], fill=255), (176, 130, 84), edge_k=.5)
        P.add(lambda d: d.polygon([(10, 14), (54, 14), (57, 27), (7, 27)], fill=255), (250, 246, 232), edge=False, sh=False, hi=False)
        for y in (18, 22): P.line([(14, y), (50, y)], (150, 146, 170))
        P.rect(6, 30, 8, 43, (120, 84, 54)); P.rect(56, 30, 58, 43, (120, 84, 54)); P.rect(2, 3, 5, 12, (200, 200, 220))
        return P.final()
    return cached('ddesk', mk)


def doodle_page(ears=True):
    """hoja con un boceto genérico (círculo y garabatos); sin silueta de ningún personaje real."""
    def mk():
        P = Paint(26, 32)
        P.add(lambda d: d.rectangle([0, 0, 25, 31], fill=255), (252, 248, 236), edge_k=.6)
        P.add(lambda d: d.ellipse([6, 5, 19, 18], fill=255), (60, 56, 80), edge=False, sh=False, hi=False)
        P.add(lambda d: d.ellipse([8, 7, 17, 16], fill=255), (252, 248, 236), edge=False, sh=False, hi=False)
        P.line([(9, 12), (12, 10), (16, 13)], (60, 56, 80))
        for y in (24, 27): P.line([(3, y), (22, y)], (170, 166, 190))
        return P.final()
    return cached(('doodle', ears), mk)


def statuette(h=24):
    def mk():
        P = Paint(h // 2 + 2, h)
        c = (h // 2 + 2) // 2
        P.add(lambda d: d.ellipse([c - 3, 0, c + 3, 6], fill=255), (240, 200, 80), edge_k=.5)
        P.add(lambda d: d.rectangle([c - 2, 6, c + 2, h - 6], fill=255), (232, 188, 72), edge_k=.5)
        P.add(lambda d: d.rectangle([c - 5, h - 6, c + 5, h - 1], fill=255), (150, 110, 40), edge_k=.5)
        return P.final()
    return cached(('stat', h), mk)


def marquee_light(n=14):
    def mk():
        P = Paint(n * 6 + 2, 8)
        P.add(lambda d: d.rectangle([0, 0, n * 6 + 1, 7], fill=255), (50, 30, 40), edge_k=.5)
        for i in range(n): P.rect(2 + i * 6, 2, 4 + i * 6, 5, (255, 230, 130))
        return P.final()
    return cached(('marq', n), mk)


def clapper():
    def mk():
        P = Paint(28, 24)
        P.add(lambda d: d.rectangle([0, 8, 27, 23], fill=255), (40, 40, 52), edge_k=.5)
        P.add(lambda d: d.polygon([(0, 0), (27, 3), (27, 8), (0, 8)], fill=255), (240, 240, 244), edge_k=.5)
        for x in range(2, 26, 6): P.line([(x, 8), (x + 3, 1)], (30, 30, 40))
        return P.final()
    return cached('clap', mk)

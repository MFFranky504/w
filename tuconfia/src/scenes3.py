"""Historia 2 (Messi). Jerarquía de planos: RPG chibi (lejos) · batalla (medio) · portrait (primer plano) · props."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import sprites as SP
import sprites_b as SB
import scenes as S0
import scenes2 as S2

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]
def rpg(who, step=0, outfit=None): return cached(('rpg', who, step, outfit), lambda: SP.rpg(who, outfit=outfit, step=step))
def bat(who, pose='stand', outfit=None): return cached(('bat', who, pose, outfit), lambda: SB.battle2(who, pose, outfit))
def shrink(im, f): return im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.NEAREST)

def shadow(c, x, y, w, k=70):
    lay = Image.new('RGBA', (WW, WH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([x - w / 2, y - 2, x + w / 2, y + 3], fill=(10, 8, 20, k)); c.im.alpha_composite(lay)

def place(c, img, cx, feet, flip=False, sh=True):
    bb = img.getbbox()
    if flip: img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if sh: shadow(c, cx, feet, (bb[2] - bb[0]) * .7)
    c.im.alpha_composite(img, (int(cx - img.width / 2), int(feet - bb[3] + 1))) if (int(cx - img.width / 2) >= 0 and int(feet - bb[3] + 1) >= 0) else c.im.paste(img, (int(cx - img.width / 2), int(feet - bb[3] + 1)), img)


# ================================================================ 1+8. SERVILLETA (props)
def napkin(t, u, mode='hook'):
    c = Canvas(vgrad([(0, '#2a1a14'), (.45, '#5a3a24'), (1, '#3a2418')]))
    # bokeh del restaurante
    rnd = random.Random(4)
    for i in range(26):
        x, y, r = rnd.uniform(0, WW), rnd.uniform(10, 90), rnd.uniform(4, 10)
        col = (int(200 + rnd.random() * 55), int(130 + rnd.random() * 60), int(60 + rnd.random() * 40))
        c.d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * .55) for v in col))
    # mesa de madera
    c.R(0, 100, WW, 190, (134, 88, 54))
    for y in range(104, 290, 9): c.R(0, y, WW, 1, (104, 66, 40)); c.R(0, y + 1, WW, 1, (152, 104, 66))
    for x in range(12, WW, 38): c.R(x, 100, 1, 190, (110, 72, 44))
    c.R(0, 100, WW, 3, (180, 130, 84))
    # taza de café
    c.R(104, 96, 20, 16, (240, 236, 228)); c.R(104, 96, 20, 2, (255, 255, 255)); c.R(124, 100, 5, 8, (240, 236, 228)); c.R(106, 98, 16, 3, (70, 40, 28))
    c.R(98, 112, 32, 3, (226, 220, 210))
    # servilleta (papel con dobleces)
    cx, cy, w, h = 80, 160, 104, 86
    rot = math.sin(t * .4) * .01 + (.04 if mode == 'hook' else -.02)
    def P(x, y): return (cx + (x - cx) * math.cos(rot) - (y - cy) * math.sin(rot), cy + (x - cx) * math.sin(rot) + (y - cy) * math.cos(rot))
    quad = [P(cx - w / 2, cy - h / 2), P(cx + w / 2, cy - h / 2 + 2), P(cx + w / 2 - 2, cy + h / 2), P(cx - w / 2 + 3, cy + h / 2 - 1)]
    sh_ = [(x + 3, y + 4) for x, y in quad]
    c.d.polygon(sh_, fill=(70, 44, 28))
    c.d.polygon(quad, fill=(250, 248, 242))
    c.d.polygon([quad[1], quad[2], (quad[2][0] - 10, quad[2][1] - 2), (quad[1][0] - 8, quad[1][1] + 6)], fill=(236, 232, 224))
    c.d.line([P(cx, cy - h / 2), P(cx, cy + h / 2)], fill=(228, 224, 214)); c.d.line([P(cx - w / 2, cy), P(cx + w / 2, cy)], fill=(228, 224, 214))
    # relieve (puntos de la servilleta)
    for i in range(0, 90, 3):
        for j in range(0, 70, 3):
            if (i + j) % 6 == 0: c.d.point(P(cx - w / 2 + 8 + i, cy - h / 2 + 8 + j), fill=(240, 238, 230))
    # texto manuscrito
    rnd = random.Random(7)
    prog = 1.0 if mode == 'hook' else ease(u * 1.15)
    ink = (28, 36, 120)
    nlines = 7
    penx = peny = None
    for r in range(nlines):
        y0 = cy - h / 2 + 12 + r * 9.5
        L = rnd.uniform(60, 84) if r not in (3, 6) else rnd.uniform(34, 50)
        seg = int(L / 3)
        for k in range(seg):
            f = (r + k / seg) / nlines
            if f > prog: break
            x = cx - w / 2 + 9 + k * 3
            yy = y0 + math.sin(k * 1.7 + r) * 1.6
            c.d.line([P(x, yy), P(x + 2, yy + math.sin(k * 2.3) * 1.5)], fill=ink)
            if k % 4 == 0: c.d.point(P(x + 1, yy - 3), fill=ink)
            penx, peny = P(x + 3, yy)
    # firma
    if prog >= .98 or mode == 'hook':
        c.d.line([P(cx + 8, cy + 36), P(cx + 18, cy + 32), P(cx + 24, cy + 38), P(cx + 34, cy + 31), P(cx + 40, cy + 37)], fill=ink)
    # bolígrafo y mano
    if mode == 'hook':
        px, py = 40 + math.sin(t * 2) * 1.5, 132
        c.d.line([(px, py), (px + 32, py + 14)], fill=(30, 44, 140), width=3); c.d.line([(px + 1, py - 1), (px + 30, py + 12)], fill=(120, 150, 255))
        c.d.polygon([(px - 2, py - 1), (px - 6, py - 2), (px - 3, py + 2)], fill=(30, 30, 40))
    else:
        px, py = (penx or 40), (peny or 120)
        c.d.polygon([(px + 54, py - 100), (px + 74, py - 100), (px + 24, py - 18), (px + 8, py - 16)], fill=(52, 70, 120))
        c.d.polygon([(px + 62, py - 100), (px + 74, py - 100), (px + 30, py - 24), (px + 22, py - 22)], fill=(40, 54, 98))
        c.d.line([(px + 14, py - 12), (px, py)], fill=(30, 44, 140), width=3)
        c.d.ellipse([px + 6, py - 24, px + 24, py - 8], fill=(242, 200, 166)); c.d.ellipse([px + 10, py - 26, px + 20, py - 16], fill=(250, 214, 182))
        c.d.line([(px + 8, py - 12), (px + 14, py - 8)], fill=(214, 168, 136))
    c.light(80, 150, 90, 100, (255, 200, 120), .55)
    c.amb = (.9, .8, .72)
    c.vig = .75
    return c.render()


# ================================================================ 2+3. POTRERO (RPG)
def potrero_bg(c, t):
    sky = vgrad([(0, '#79b6ee'), (.35, '#b8dcf6'), (.5, '#f6e4b0'), (1, '#f6e4b0')])
    c.im.paste(Image.fromarray(np.clip(sky, 0, 255).astype('uint8')), (0, 0))
    # nubes
    for i in range(5):
        x = (i * 41 + t * (2 + i)) % (WW + 60) - 30; y = 40 + (i * 23) % 70
        for j in range(4): c.d.ellipse([x + j * 9, y - (j % 2) * 3, x + j * 9 + 18, y + 7], fill=(255, 255, 255))
    # ciudad lejana
    rnd = random.Random(3)
    x = 0
    while x < WW:
        w = rnd.randint(8, 16); h = rnd.randint(14, 34)
        c.R(x, 172 - h, w, h, (126, 140, 178)); c.R(x, 172 - h, w, 2, (150, 164, 200))
        for yy in range(172 - h + 4, 170, 5):
            for xx in range(x + 2, x + w - 2, 4): c.R(xx, yy, 2, 2, (206, 218, 240))
        x += w + 1
    # reja y árboles
    c.R(0, 172, WW, 4, (70, 84, 90))
    for xx in range(0, WW, 6): c.R(xx, 164, 1, 10, (90, 100, 108))
    c.R(0, 164, WW, 1, (90, 100, 108))
    for (tx, th) in [(10, 30), (140, 34), (66, 24)]:
        c.R(tx, 176 - 8, 3, 10, (90, 60, 44)); c.d.ellipse([tx - 9, 176 - th, tx + 12, 176 - 6], fill=(70, 130, 84)); c.d.ellipse([tx - 5, 176 - th + 3, tx + 6, 176 - th + 11], fill=(110, 170, 110))
    # tierra
    c.R(0, 176, WW, 120, (206, 160, 104))
    rnd = random.Random(5)
    for i in range(160):
        c.d.point((rnd.randrange(WW), rnd.randrange(178, 284)), fill=(rnd.choice([(182, 134, 84), (222, 180, 124), (170, 122, 76)])))
    for i in range(8):
        x = rnd.randrange(0, WW - 20); y = rnd.randrange(190, 270)
        c.d.ellipse([x, y, x + 14, y + 4], fill=(120, 170, 90))
    # líneas de cancha
    c.d.line([(10, 214), (150, 214)], fill=(240, 236, 224)); c.d.ellipse([60, 196, 100, 232], outline=(240, 236, 224))
    # arcos
    for gx in (4, 140):
        c.R(gx, 196, 2, 22, (240, 240, 236)); c.R(gx + 14, 196, 2, 22, (240, 240, 236)); c.R(gx, 196, 16, 2, (240, 240, 236))
        for k in range(0, 16, 3): c.R(gx + k, 198, 1, 20, (200, 204, 210))


def potrero(t, u, mode='small'):
    c = Canvas(np.zeros((WH, WW, 3)))
    potrero_bg(c, t)
    step = int(t * 4) % 2
    if mode == 'small':
        fy = 228
        x_pos = [(22, 'kid_a'), (56, 'kid_b'), (128, 'kid_c')]
        for x, w in x_pos: place(c, rpg(w, step if False else 0), x, fy)
        m = shrink(rpg('messi_kid'), .8)
        place(c, m, 92, fy)
        # línea de altura comparativa
        y_top = fy - rpg('kid_a').getbbox()[3] + 4
        c.d.line([(14, y_top), (146, y_top)], fill=(255, 255, 255)) if False else None
        # balón
        bx = 112 + math.sin(t * 4) * 1; c.d.ellipse([bx, fy - 4, bx + 5, fy + 1], fill=(250, 250, 250), outline=(40, 40, 50))
    else:
        # Leo regatea de izquierda a derecha, los demás lo persiguen
        mx = 24 + ease(u) * 112; my = 232 + math.sin(u * 9) * 14
        for i, (w, d0) in enumerate([('kid_a', .22), ('kid_c', .3), ('kid_b', .4)]):
            ux = max(0, u - d0 * .5)
            kx = 24 + ease(ux) * 112 - 18 - i * 12 + math.sin(t * 5 + i) * 3; ky = 228 + i * 8 + math.sin(t * 3 + i) * 3
            place(c, rpg(w, int(t * 6 + i) % 2), kx, ky)
        place(c, rpg('messi_kid', int(t * 8) % 2), mx, my)
        bx = mx + 8 + math.sin(t * 14) * 3; by = my - 1 + abs(math.sin(t * 12)) * -4
        c.d.ellipse([bx, by - 2, bx + 5, by + 3], fill=(252, 252, 252), outline=(40, 40, 50))
        for k in range(3): c.d.point((mx - 6 - k * 4, my + 1 + (k % 2)), fill=(236, 200, 150))   # polvo
    c.light(120, 70, 90, 90, (255, 220, 150), .5)
    c.amb = (1, .98, .94)
    c.vig = .35
    return c.render()


# ================================================================ 4. CONSULTORIO (batalla)
def consultorio(t, u):
    c = Canvas(vgrad([(0, '#d6ece6'), (1, '#a8cfc6')]))
    c.R(0, 0, WW, 214, (198, 226, 218))
    for x in range(0, WW, 16): c.R(x, 0, 1, 214, (184, 212, 204))
    c.R(0, 100, WW, 3, (150, 190, 180))
    c.R(0, 214, WW, 80, (230, 224, 214))
    for x in range(0, WW, 20): c.R(x, 214, 1, 80, (210, 204, 194))
    c.R(0, 214, WW, 3, (170, 164, 156))
    # ventana con persiana
    c.R(104, 36, 40, 48, (246, 250, 252)); c.R(106, 38, 36, 44, (160, 214, 246), c.ed)
    for yy in range(40, 82, 4): c.R(106, yy, 36, 1, (230, 240, 250))
    # gráfica de crecimiento (pared izquierda)
    c.R(14, 40, 62, 62, (250, 250, 246)); c.R(14, 40, 62, 2, (190, 60, 70))
    for xx in range(20, 72, 10): c.R(xx, 48, 1, 48, (216, 220, 224))
    for yy in range(54, 96, 10): c.R(18, yy, 54, 1, (216, 220, 224))
    c.d.line([(20, 92), (30, 82), (40, 72), (50, 64), (60, 57), (70, 52)], fill=(120, 130, 150))          # promedio
    pts = [(20, 92), (30, 88), (40, 85), (50, 83), (60, 82), (70, 81)]
    k = min(1, u * 2)
    for i in range(len(pts) - 1):
        if i / 5 < k: c.d.line([pts[i], pts[i + 1]], fill=(220, 50, 60), width=2)
    # camilla
    c.R(6, 190, 50, 6, (240, 240, 246)); c.R(8, 196, 46, 14, (120, 160, 190)); c.R(10, 210, 3, 8, (110, 110, 124)); c.R(48, 210, 3, 8, (110, 110, 124))
    # escritorio
    c.R(100, 168, 56, 5, (186, 140, 96)); c.R(102, 173, 52, 40, (150, 108, 70)); c.R(112, 156, 10, 12, (240, 240, 236)); c.R(108, 150, 18, 6, (60, 160, 120))
    ph = int(t * 2) % 2
    place(c, bat('jorge', 'stand'), 34, 232)
    place(c, bat('messi_kid', 'stand'), 74, 236)
    place(c, bat('doctor', 'hold'), 118, 232, flip=True)
    # jeringa/pastilla icon flotando
    c.R(60, 44 + math.sin(t * 2) * 2, 18, 3, (230, 230, 240)); c.R(76, 43 + math.sin(t * 2) * 2, 4, 5, (220, 60, 70))
    c.light(80, 70, 120, 90, (240, 255, 250), .5)
    c.amb = (.92, .96, 1)
    c.vig = .45
    return c.render()


# ================================================================ 5. PISTA / AEROPUERTO (RPG)
def tarmac(t, u):
    c = Canvas(vgrad([(0, '#1c2a66'), (.3, '#8a4a8c'), (.5, '#ff8a5a'), (.62, '#ffd070'), (1, '#ffe8a0')]))
    sy = 150
    c.d.ellipse([60, sy - 18, 100, sy + 18], fill=(255, 238, 180)); c.light(80, sy, 100, 90, (255, 190, 100), .8)
    stars(c, t, 30, 8, 60)
    rnd = random.Random(12)
    for i in range(5):
        x = (rnd.uniform(0, WW) + t * (3 + i)) % (WW + 60) - 30; y = rnd.uniform(60, 130)
        for j in range(4): c.d.ellipse([x + j * 8, y - (j % 2) * 3, x + j * 8 + 16, y + 6], fill=(255, 170 + i * 8, 140 + i * 10))
    c.R(0, 176, WW, 120, (74, 70, 96))
    c.R(0, 176, WW, 2, (110, 104, 130))
    for x in range(0, WW, 30): c.R(x + 4, 232, 18, 3, (240, 220, 120))
    c.R(0, 196, WW, 1, (240, 240, 250))
    # terminal lejana
    c.R(0, 150, 60, 26, (60, 56, 90)); c.R(0, 150, 60, 3, (90, 86, 126))
    for xx in range(4, 56, 8): c.R(xx, 158, 5, 6, (255, 214, 120), c.ed)
    # avión
    ax = 150 - u * 160 if False else 118
    pl = Image.new('RGBA', (88, 34), (0, 0, 0, 0)); d = ImageDraw.Draw(pl)
    d.rounded_rectangle([4, 10, 84, 26], radius=8, fill=(244, 246, 250)); d.rectangle([4, 20, 84, 23], fill=(80, 120, 200))
    d.polygon([(70, 10), (84, 0), (84, 12)], fill=(80, 120, 200)); d.polygon([(26, 22), (52, 22), (40, 34), (26, 34)], fill=(210, 214, 224))
    for xx in range(14, 62, 6): d.rectangle([xx, 14, xx + 2, 16], fill=(120, 170, 230))
    d.polygon([(4, 14), (0, 16), (4, 22)], fill=(200, 204, 216))
    pl = SP.Paint(1, 1).final if False else pl
    c.im.alpha_composite(S0.outline(pl) if hasattr(S0, 'outline') else pl, (60, 176)) if False else c.blit(pl, 52, 168)
    # personajes caminando hacia el avión
    wx = 20 + ease(u) * 40
    place(c, rpg('jorge', int(t * 5) % 2), wx + 24, 236)
    place(c, rpg('messi_kid', int(t * 5 + 1) % 2), wx, 244)
    c.R(int(wx + 36), 232, 8, 10, (140, 90, 60)); c.R(int(wx + 36), 232, 8, 2, (180, 130, 90))   # maleta
    c.amb = (1, 1, 1)
    c.vig = .5
    return c.render()


# ================================================================ 7. RESTAURANTE DEL CLUB (batalla)
def restaurant(t, u):
    c = Canvas(vgrad([(0, '#3a2418'), (1, '#24160e')]))
    c.R(0, 0, WW, 214, (120, 78, 52))
    for x in range(0, WW, 10): c.R(x, 0, 1, 214, (104, 66, 44))
    # ventanal con pistas de tenis
    c.R(10, 30, 140, 84, (60, 44, 34)); c.R(14, 34, 132, 76, (110, 190, 110), c.ed)
    c.R(14, 34, 132, 30, (150, 210, 240), c.ed)
    for xx in range(20, 140, 24): c.R(xx, 78, 14, 1, (250, 250, 250), c.ed)
    c.R(14, 74, 132, 1, (250, 250, 250), c.ed); c.R(80, 66, 1, 44, (60, 44, 34)); c.R(14, 66, 132, 2, (60, 44, 34))
    c.light(80, 70, 100, 70, (255, 244, 200), .5)
    # suelo
    c.R(0, 214, WW, 80, (88, 58, 40))
    for y in range(220, 284, 12): c.R(0, y, WW, 1, (68, 44, 30))
    # personajes detrás de la mesa
    place(c, bat('rexach', 'stand'), 40, 218)
    place(c, bat('jorge', 'stand'), 120, 218, flip=True)
    place(c, bat('messi_kid', 'stand'), 82, 222)
    # mesa con mantel
    c.R(0, 176, WW, 6, (250, 246, 238)); c.R(0, 176, WW, 1, (255, 255, 255)); c.R(0, 182, WW, 60, (236, 232, 222))
    for xx in range(0, WW, 12): c.R(xx, 184, 1, 56, (220, 214, 202))
    for (x, y) in [(22, 170), (130, 170)]:
        c.R(x, y, 9, 7, (250, 250, 250)); c.R(x + 9, y + 2, 2, 3, (250, 250, 250)); c.R(x + 1, y + 1, 7, 2, (80, 44, 30))
    c.R(62, 164, 10, 12, (250, 250, 246)); c.R(63, 162, 8, 3, (250, 250, 246)); c.R(64, 160, 4, 4, (230, 230, 226))   # servilletero con servilletas
    # rótulo con la fecha
    k = min(1, u * 4)
    if k > 0:
        w = ptext_w('DIC. 2000', 2)
        c.R(80 - w // 2 - 4, 8, w + 8, 16, (20, 10, 26)); c.R(80 - w // 2 - 4, 8, w + 8, 2, (255, 216, 74))
        ptext(c.d, 80 - w // 2, 13, 'DIC. 2000', (255, 255, 255), 2)
    c.light(80, 120, 110, 100, (255, 200, 120), .55)
    c.amb = (.95, .88, .82)
    c.vig = .55
    return c.render()


# ================================================================ 9. FINAL EN EL ESTADIO (batalla)
def stadium(t, u):
    c = Canvas(vgrad([(0, '#0a0e2c'), (.5, '#1c2a6a'), (1, '#2a3a8a')]))
    stars(c, t, 40, 9, 90)
    # gradas (multitud)
    rnd = random.Random(8)
    c.d.polygon([(0, 150), (WW, 150), (WW, 230), (0, 230)], fill=(32, 40, 84))
    for row in range(8):
        y = 154 + row * 9
        c.R(0, y + 7, WW, 2, (24, 30, 66))
        for x in range(2, WW, 5):
            col = rnd.choice([(150, 206, 246), (252, 252, 255), (150, 206, 246), (252, 220, 120), (230, 90, 100)])
            hy = y + math.sin(t * 5 + x + row) * 1
            c.R(x, int(hy), 3, 3, (242, 198, 160)); c.R(x, int(hy) + 3, 3, 4, col)
    # torres de luz
    for tx in (14, 146):
        c.R(tx - 1, 70, 3, 82, (60, 64, 90)); c.R(tx - 9, 58, 19, 14, (244, 246, 255), c.ed)
        c.light(tx, 66, 70, 80, (255, 248, 220), .7)
    # césped
    c.R(0, 230, WW, 70, (60, 150, 80))
    for x in range(0, WW, 20): c.R(x, 230, 10, 70, (70, 164, 90))
    c.R(0, 230, WW, 2, (240, 240, 236))
    # Messi con la copa
    c.light(80, 150, 70, 80, (255, 230, 150), .35 * ease(u * 3))
    place(c, bat('messi', 'trophy'), 80, 252)
    hx, hy = 80 + 15 - 2, 252 - 116 + 10          # mano (según el esqueleto)
    tr = Image.new('RGBA', (18, 24), (0, 0, 0, 0)); d = ImageDraw.Draw(tr)
    d.polygon([(2, 0), (16, 0), (14, 9), (11, 13), (7, 13), (4, 9)], fill=(255, 214, 70)); d.rectangle([7, 13, 11, 19], fill=(232, 176, 40)); d.rectangle([3, 19, 15, 23], fill=(200, 140, 30))
    d.line([(4, 2), (4, 8)], fill=(255, 248, 190)); d.rectangle([0, 2, 2, 7], fill=(255, 214, 70)); d.rectangle([16, 2, 18, 7], fill=(255, 214, 70))
    c.blit(tr, hx - 9, hy - 22)
    c.light(hx, hy - 12, 26, 26, (255, 220, 120), .55)
    # confeti
    rnd = random.Random(21)
    cols = [(150, 206, 246), (255, 255, 255), (255, 214, 70), (150, 206, 246)]
    for i in range(80):
        x = rnd.uniform(0, WW); y0 = rnd.uniform(0, WH); s_ = rnd.uniform(20, 60)
        y = (y0 + t * s_) % (WH + 10) - 5
        c.R(int(x + math.sin(t * 2 + i) * 3), int(y), 2, 3, cols[i % 4])
    c.amb = (1, 1, 1)
    c.vig = .55
    return c.render()


# ================================================================ 11. "TÚ" con la servilleta (batalla)
def tu_cafe(t, u):
    c = Canvas(vgrad([(0, '#080b1c'), (.5, '#171c3a'), (1, '#0c0c18')]))
    S0.bricks(c, 40, 210)
    c.R(0, 206, WW, 80, (30, 32, 48))
    for x in range(0, WW, 14): c.R(x, 208 + (x // 14 % 3) * 9, 12, 1, (40, 44, 64))
    c.R(23, 70, 3, 138, (34, 36, 54)); c.R(23, 70, 14, 3, (34, 36, 54)); c.R(33, 72, 7, 3, (250, 220, 150), c.ed)
    c.light(36, 78, 70, 100, (230, 170, 80), .55); c.light(86, 170, 70, 90, (255, 214, 140), .55)
    # cartel del café
    c.R(100, 90, 44, 16, (20, 10, 26)); c.R(100, 90, 44, 1, (255, 200, 90), c.ed); c.R(100, 105, 44, 1, (255, 200, 90), c.ed)
    ptext(c.ed, 106, 95, 'CAFE', (255, 200, 90), 2)
    place(c, bat('you', 'hold'), 80, 228)
    # mesita
    c.R(54, 206, 52, 4, (60, 60, 80)); c.R(54, 206, 52, 1, (110, 110, 140)); c.R(78, 210, 4, 36, (50, 50, 66)); c.R(66, 244, 28, 3, (50, 50, 66))
    c.R(94, 198, 9, 8, (240, 236, 228)); c.R(103, 200, 2, 4, (240, 236, 228))
    # servilleta en primer plano con signo de pregunta
    bob = math.sin(t * 3) * 1.2
    c.R(56, 196 + bob, 24, 11, (250, 248, 242)); c.R(56, 196 + bob, 24, 1, (255, 255, 255)); c.R(56, 206 + bob, 24, 1, (214, 210, 202))
    c.R(58, 199 + bob, 12, 1, (28, 36, 120)); c.R(58, 202 + bob, 16, 1, (28, 36, 120))
    # etiqueta TÚ
    bb = math.sin(t * 3) * 1.5
    c.R(60, 50 + bb, 40, 20, (255, 216, 74)); c.R(60, 50 + bb, 40, 2, (255, 244, 170)); c.R(60, 68 + bb, 40, 2, (190, 150, 30))
    ptext(c.d, 66, 56 + bb, 'TU', (20, 10, 26), 3); c.R(68, 53 + bb, 3, 2, (20, 10, 26))
    c.d.polygon([(76, 70 + bb), (84, 70 + bb), (80, 78 + bb)], fill=(255, 216, 74))
    rain(c, t, 70, 11)
    c.amb = (.66, .7, .92)
    c.vig = .7
    return c.render()

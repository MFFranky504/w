"""Short vertical (160x284) en estilo GBA: Jackie Chan. Una escena por momento de la historia, sin reutilizar escenarios.
Suelo FLY=222; chibi con pies en FLY+2, entrenador (bat) en FLY+30. Lo importante va en x 14..146 (el recorte vertical)."""
import math, random
from PIL import Image
from lib import WW, WH, Canvas, vgrad, ease, stars
import gba as G
import bg
import props as PR
from scenes3 import rpg, bat
from scenes2 import bust
from scenes9 import phased

FLY = 222
FR, FB = FLY + 2, FLY + 30


def cv(): return Canvas(vgrad([(0, '#000000'), (1, '#000000')]))


def put(c, img, cx, feet, flip=False, rot=0):
    """como G.place pero admite giro (golpe, caída)."""
    if not rot: return G.place(c, img, cx, feet, flip)
    sp = G.sprite(img)
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    sp = sp.rotate(rot, expand=True, resample=Image.NEAREST); bb = sp.getbbox()
    c.im.paste(sp, (int(cx - sp.width / 2), int(feet - bb[3])), sp)


def close_up(c, who, expr, t, sc=1.3, x=None):
    b = G.sprite(bust(who, expr, (0, 0), t, sc)); c.im.alpha_composite(b, (int((x or WW / 2) - b.width / 2), WH - b.height))


def fin(c, mood='day', amb=(1, 1, 1), vig=.4):
    c.amb = amb; c.vig = vig
    return G.grade(c.render(), mood)


# ---------------------------------------------------------------- escenarios
def _studio(c, t):
    """plató de 1973: fondo negro, decorado de patio chino (columnas rojas, faroles), focos y suelo de tablas."""
    c.R(0, 0, WW, WH, (14, 12, 22))
    G.sky(c, [(0, (20, 16, 34)), (1, (52, 34, 60))], 0, FLY - 60, bands=6)
    c.R(0, FLY - 70, WW, 70, (120, 52, 40)); c.R(0, FLY - 70, WW, 4, (200, 150, 70))        # muro del decorado
    for x in (18, 70, 122): G.pillar(c, x, 14, (178, 40, 40), FLY - 120, FLY)
    for x in (44, 98):
        sw = math.sin(t * 1.5 + x) * 1.5
        c.d.line([(x, FLY - 130), (x + sw, FLY - 112)], fill=(60, 50, 50))
        c.d.ellipse([x - 7 + sw, FLY - 112, x + 7 + sw, FLY - 98], fill=(230, 70, 50)); c.R(x - 4 + sw, FLY - 110, 8, 1, (255, 200, 120))
        c.light(x + sw, FLY - 105, 26, 26, (255, 170, 90), .35)
    for x in (6, 154):                                                              # focos del rodaje
        c.R(x - 1, 30, 2, FLY - 30, (60, 60, 70)); c.R(x - 6, 26, 12, 8, (90, 90, 100)); c.light(x, 34, 60, 130, (255, 246, 210), .3)
    bg.planks(c, 0, FLY, WW, WH - FLY, (138, 92, 58), seed=17, pw=9); c.R(0, FLY, WW, 2, (200, 150, 100))


def _opera(c, t):
    """escuela de ópera de Pekín al amanecer: tejado de tejas curvas, muro gris, patio de losas."""
    G.sky(c, [(0, (60, 50, 110)), (.6, (210, 120, 110)), (1, (250, 200, 140))], 0, FLY, bands=8)
    G.mountains(c, FLY - 70, 40, (96, 78, 130), seed=5)
    G.haze(c, 0, FLY - 60, (220, 150, 140), .25)
    c.R(0, FLY - 80, WW, 80, (150, 146, 150)); c.R(0, FLY - 80, WW, 3, (196, 192, 196))           # muro
    for x in range(4, WW, 26): c.R(x, FLY - 70, 16, 22, (70, 50, 50)); c.R(x + 1, FLY - 69, 14, 20, (176, 60, 52))   # ventanas rojas
    c.d.polygon([(-10, FLY - 80), (WW + 10, FLY - 80), (WW - 6, FLY - 98), (6, FLY - 98)], fill=(46, 52, 70))      # tejado
    for x in range(0, WW, 6): c.R(x, FLY - 96, 3, 15, (64, 72, 94))
    c.d.polygon([(-10, FLY - 80), (4, FLY - 98), (0, FLY - 104)], fill=(46, 52, 70)); c.d.polygon([(WW + 10, FLY - 80), (WW - 4, FLY - 98), (WW, FLY - 104)], fill=(46, 52, 70))
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (170, 160, 150), tile=18, seed=21, t=t)


def _poster_wall(c, t):
    """calle de Hong Kong de noche: muro de carteles de cine y neones."""
    G.sky(c, [(0, (16, 14, 40)), (1, (60, 30, 80))], 0, FLY, bands=6); stars(c, t, 25, 7, 60)
    bg.skyline(c, FLY - 70, FLY - 60, seed=8, t=t)
    c.R(0, FLY - 120, WW, 120, (110, 100, 96)); bg.brick(c, 0, FLY - 120, WW, 120, (120, 92, 80), (70, 56, 52), seed=3)
    bg.cobble(c, 0, FLY, WW, WH - FLY, (74, 70, 96), seed=9)


def _cinema(c, t):
    """sala de cine en Estados Unidos, casi vacía: pantalla, butacas rojas."""
    c.R(0, 0, WW, WH, (22, 16, 30))
    bg.curtain(c, 0, 26, FLY - 40); bg.curtain(c, WW - 26, 26, FLY - 40)
    c.R(26, 30, WW - 52, 90, (200, 204, 220)); c.light(WW / 2, 75, 70, 60, (220, 230, 255), .35)
    for r, y in enumerate((FLY - 6, FLY + 16, FLY + 38)):
        for x in range(8, WW, 18):
            c.R(x, y - 14, 15, 14, (150, 30, 44)); c.R(x, y - 14, 15, 2, (196, 60, 70)); c.R(x + 1, y, 13, 4, (90, 20, 30))


def _forest(c, t, mood='day'):
    G.sky(c, [(0, (110, 170, 240)), (1, (220, 236, 250))], 0, FLY, bands=8)
    G.clouds(c, t, 40, (250, 252, 255), n=3, seed=4, speed=1.2, scale=.7)
    G.mountains(c, FLY - 50, 60, (130, 160, 210), seed=12, snow=(250, 252, 255))
    G.haze(c, 0, FLY - 40, (200, 224, 250), .3)
    G.meadow(c, FLY - 10, 26, (110, 186, 104), seed=8)
    G.tree_line(c, FLY - 4, (60, 140, 90), seed=14, size=16)
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (176, 124, 82), tile=16, seed=31, grass=(102, 200, 86), t=t)


def _bigtree(c, x, t):
    c.R(x - 6, FLY - 140, 12, 140, (100, 66, 48)); c.R(x - 6, FLY - 140, 3, 140, (130, 90, 64))
    c.d.line([(x, FLY - 110), (x + 50, FLY - 120)], fill=(100, 66, 48), width=5)
    for dx, dy, r in ((-20, -160, 30), (16, -170, 32), (40, -138, 24), (-4, -130, 26)):
        c.d.ellipse([x + dx - r, FLY + dy - r, x + dx + r, FLY + dy + r], fill=(40, 110, 70))
        c.d.ellipse([x + dx - r + 4, FLY + dy - r + 2, x + dx + r - 8, FLY + dy + r - 10], fill=(70, 150, 90))


def _hospital(c, t):
    bg.hospital_wall(c, t)
    PR.keep(c, PR.monitor_ecg(), 118, FLY - 40); PR.keep(c, PR.hospital_bed(), 70, FLY - 6)
    bg.planks(c, 0, FLY, WW, WH - FLY, (180, 186, 196), seed=4, pw=12)


def _rooftops(c, t, k=0.0):
    """tejados de Hong Kong al atardecer (el regreso)."""
    G.sky(c, [(0, (250, 150, 90)), (.7, (250, 210, 140)), (1, (255, 240, 200))], 0, FLY, bands=8)
    G.clouds(c, t, 46, (255, 236, 210), n=3, seed=9, speed=1.6, scale=.7)
    bg.skyline(c, FLY - 30, FLY - 40, cols=((150, 90, 110), (176, 110, 120)), seed=4, lit=.2, t=t)
    G.haze(c, 0, FLY - 20, (250, 200, 160), .25)
    for x0, w in ((-10, 70), (74, 100)):
        G.blocks(c, x0, FLY, w, WH - FLY + 4, (150, 120, 120), tile=14, seed=x0 + 50, grass=None, t=t)
        c.R(x0, FLY - 2, w, 3, (90, 70, 80))


def _premiere(c, t):
    G.sky(c, [(0, (10, 10, 40)), (1, (50, 30, 90))], 0, FLY, bands=6); stars(c, t, 40, 3, 100)
    for i in range(3):
        a = math.sin(t * .8 + i * 2) * .35
        bg.beam(c, 30 + i * 50, FLY - 30, 4, 40, 0, (255, 246, 210), 26)
    c.R(14, FLY - 110, WW - 28, 30, (40, 30, 60))
    for x in range(18, WW - 18, 6): c.R(x, FLY - 108, 3, 3, (255, 220, 120) if (x // 6 + int(t * 6)) % 2 else (180, 120, 60))
    c.R(14, FLY - 80, WW - 28, 80, (60, 40, 70)); c.R(30, FLY - 70, WW - 60, 60, (24, 18, 30))
    bg.crowd(c, FLY + 10, t, seed=6, phones=True)
    c.R(0, FLY + 4, WW, WH - FLY, (150, 20, 40)); c.R(0, FLY + 4, WW, 2, (220, 70, 80))         # alfombra roja


def _sunset_world(c, t):
    G.sky(c, [(0, (60, 60, 150)), (.6, (240, 140, 120)), (1, (255, 210, 150))], 0, FLY, bands=8)
    G.mountains(c, FLY - 30, 70, (120, 90, 150), seed=4)
    G.haze(c, 0, FLY - 30, (240, 170, 150), .25)
    G.meadow(c, FLY - 6, 20, (120, 150, 100), seed=3)
    G.blocks(c, -8, FLY, WW + 16, WH - FLY + 4, (170, 120, 90), tile=16, seed=44, grass=(110, 170, 90), t=t)


# ---------------------------------------------------------------- 1. el golpe
def jc_golpe_a(t, u):
    c = cv(); _studio(c, t)
    hit = u > .55
    put(c, bat('bruce', 'hip'), 54, FB)
    sw = -50 if not hit else 25                                                # el palo baja
    a = math.radians(sw); hx, hy = 66, FB - 74
    c.d.line([(hx, hy), (hx + math.cos(a) * 42, hy + math.sin(a) * 42)], fill=(120, 80, 50), width=3)
    put(c, bat('jackie_y', 'stand'), 112 + (6 if hit else 0), FB, flip=True, rot=-14 if hit else 0)
    if hit:
        for k in range(8):
            ang = k * math.pi / 4 + t; r = 10 + (u - .55) * 40
            c.R(104 + math.cos(ang) * r, FB - 96 + math.sin(ang) * r, 2, 2, (255, 240, 140))
        if u < .62: c.R(0, 0, WW, WH, (255, 255, 255))
    return fin(c, 'dark', (1.05, .98, .95), .55)


def jc_golpe_b(t, u):
    c = cv(); _studio(c, t)
    close_up(c, 'jackie_y', 'worry', t, 1.3)
    for k in range(5):
        ang = k * 1.25 + t * 3; c.R(80 + math.cos(ang) * 30, 120 + math.sin(ang) * 8, 3, 3, (255, 236, 120))
    return fin(c, 'dark', (1.05, .98, .95), .6)


jc_golpe = phased(jc_golpe_a, jc_golpe_b, cuts=(.55,))


# ---------------------------------------------------------------- 2. el doble y la disculpa
def jc_doble_a(t, u):
    c = cv(); _studio(c, t)
    put(c, bat('bruce', 'stand'), 60, FB, rot=-12 * ease(min(1, u * 2)))                # se inclina: disculpa
    put(c, bat('jackie_y', 'stand'), 108, FB, flip=True)
    return fin(c, 'dark', (1.0, .98, .96), .5)


def jc_doble_b(t, u):
    c = cv(); _studio(c, t)
    close_up(c, 'jackie_y', 'n', t, 1.3)
    return fin(c, 'day', (.9, .9, 1.0), .7)


jc_doble = phased(jc_doble_a, jc_doble_b, cuts=(.5,))


# ---------------------------------------------------------------- 3. la escuela de ópera
def jc_opera_a(t, u):
    c = cv(); _opera(c, t)
    for i, x in enumerate((34, 80, 126)):                                         # alumnos haciendo el pino
        put(c, rpg('jackie_k' if i == 1 else 'jackie_k', 0), x, FR + math.sin(t * 3 + i) * 1.5, rot=180)
    return fin(c, 'dark', (1.0, .95, .95), .5)


def jc_opera_b(t, u):
    c = cv(); _opera(c, t)
    put(c, bat('maestro', 'stand'), 46, FB); PR.keep(c, PR.cane(), 64, FB - 40)
    put(c, bat('jackie_k', 'stand').resize((67, 99), Image.NEAREST), 112, FB, flip=True)
    return fin(c, 'dark', (.95, .92, .98), .6)


jc_opera = phased(jc_opera_a, jc_opera_b, cuts=(.5,))


# ---------------------------------------------------------------- 4. la copia fracasada
def _poster(c, x, y, who, crossed):
    c.R(x - 1, y - 1, 38, 52, (20, 14, 20)); c.R(x, y, 36, 50, (200, 60, 40)); c.R(x + 2, y + 2, 32, 46, (236, 200, 120))
    b = bust(who, 'n', (0, 0), 0, 1.0); b = G.sprite(b.resize((max(1, b.width * 44 // b.height), 44), Image.NEAREST))
    c.im.paste(b.crop((b.width // 2 - 16, 0, b.width // 2 + 16, 44)), (x + 2, y + 4), b.crop((b.width // 2 - 16, 0, b.width // 2 + 16, 44)))
    if crossed:
        c.d.line([(x + 2, y + 2), (x + 34, y + 48)], fill=(230, 30, 40), width=3); c.d.line([(x + 34, y + 2), (x + 2, y + 48)], fill=(230, 30, 40), width=3)


def jc_copia_a(t, u):
    c = cv(); _poster_wall(c, t)
    for i, x in enumerate((20, 62, 104)):
        _poster(c, x, FLY - 104, 'bruce' if i == 1 else 'jackie_y', i != 1 and u > .3 + i * .15)
    put(c, rpg('jackie_y', 0), 80, FR)
    return fin(c, 'dark', (1, .95, 1.05), .6)


def jc_copia_b(t, u):
    c = cv(); _poster_wall(c, t)
    close_up(c, 'jackie_y', 'sad', t, 1.3)
    for i in range(30):                                                          # lluvia
        x = (i * 37 + t * 30) % WW; y = (i * 53 + t * 260) % WH; c.d.line([(x, y), (x - 2, y + 7)], fill=(130, 140, 200))
    return fin(c, 'dark', (.9, .92, 1.08), .7)


jc_copia = phased(jc_copia_a, jc_copia_b, cuts=(.5,))


# ---------------------------------------------------------------- 5. kung fu con comedia; Hollywood fracasa
def jc_hollywood_a(t, u):
    c = cv(); _studio(c, t)
    jump = abs(math.sin(t * 4)) * 14
    put(c, bat('jackie_y', 'hip'), 80, FB - jump, rot=math.sin(t * 4) * 10)
    PR.keep(c, PR.clapper(), 128, FB - 16)
    return fin(c, 'day', (1.05, 1.0, .95), .45)


def jc_hollywood_b(t, u):
    c = cv(); _cinema(c, t)
    put(c, bat('jackie', 'stand'), 80, FB + 8)
    return fin(c, 'dark', (.9, .9, 1.05), .7)


jc_hollywood = phased(jc_hollywood_a, jc_hollywood_b, cuts=(.45,))


# ---------------------------------------------------------------- 6. la caída del árbol
def jc_arbol_a(t, u):
    c = cv(); _forest(c, t); _bigtree(c, 40, t)
    k = ease(min(1, max(0, (u - .25) / .55)))
    put(c, rpg('jackie', 0), 86, FLY - 114 + k * 116, rot=k * 200)
    PR.keep(c, PR.camera_pro(), 134, FR)
    return fin(c, 'day', (1, 1, 1), .4)


def jc_arbol_b(t, u):
    c = cv(); _hospital(c, t)
    close_up(c, 'jackie', 'sad', t, 1.3)
    return fin(c, 'dark', (.9, .95, 1.05), .7)


jc_arbol = phased(jc_arbol_a, jc_arbol_b, cuts=(.55,))


# ---------------------------------------------------------------- 7. vuelve (el giro)
def jc_vuelve_a(t, u):
    c = cv(); _rooftops(c, t)
    x = -10 + u * 180; arc = max(0, math.sin(min(1, max(0, (x - 56) / 26)) * math.pi)) * 30
    put(c, rpg('jackie', int(t * 8) % 2), x, FR - arc)
    return fin(c, 'day', (1.06, 1.0, .95), .4)


def jc_vuelve_b(t, u):
    c = cv(); _rooftops(c, t)
    put(c, bat('jackie', 'hip'), 46, FB)
    PR.keep(c, PR.camera_pro(), 120, FR)
    return fin(c, 'day', (1.06, 1.0, .95), .4)


jc_vuelve = phased(jc_vuelve_a, jc_vuelve_b, cuts=(.5,))


# ---------------------------------------------------------------- 8. número 1, Guinness, Óscar
def jc_exito_a(t, u):
    c = cv(); _premiere(c, t)
    put(c, bat('jackie', 'toss'), 80, FB)
    for i in range(14): c.R((i * 29 + t * 20) % WW, (i * 41 + t * 60) % FLY, 2, 2, (255, 230, 130))
    return fin(c, 'day', (1.05, 1.0, 1.0), .45)


def jc_exito_b(t, u):
    c = cv(); _premiere(c, t)
    close_up(c, 'jackie', 'smile', t, 1.3)
    st = G.sprite(PR.statuette(30)); c.im.alpha_composite(st, (120, WH - st.height - 30))
    c.light(130, WH - 50, 26, 30, (255, 220, 120), .5)
    return fin(c, 'day', (1.05, 1.0, 1.0), .5)


jc_exito = phased(jc_exito_a, jc_exito_b, cuts=(.5,))


# ---------------------------------------------------------------- 9. la revelación
def jc_revela_a(t, u):
    c = cv(); _sunset_world(c, t)
    put(c, bat('jackie_y', 'stand'), 50, FB); put(c, bat('jackie', 'stand'), 112, FB, flip=True)
    return fin(c, 'day', (1.04, 1.0, .96), .45)


def jc_revela_b(t, u):
    c = cv(); _sunset_world(c, t)
    close_up(c, 'jackie', 'smile', t, 1.35)
    return fin(c, 'day', (1.04, 1.0, .96), .5)


jc_revela = phased(jc_revela_a, jc_revela_b, cuts=(.4,))

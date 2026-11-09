import sys, math, subprocess, numpy as np
from multiprocessing import Pool
from lib import *

FPS = 24; DUR = 87.4
O = objs()

# ---------------- world ----------------
def build_world():
    im = Image.new('RGB', (WW, WH)); d = None
    im.paste(wood(WW, 2112, 140, (80, 53, 34), 1, True), (0, 0)); im.paste(wood(WW, WH - 2112, 230, (62, 41, 28), 2, False), (0, 2112))
    d = ImageDraw.Draw(im); r = np.random.default_rng(4)
    d.rectangle((0, 0, WW, 130), fill=(34, 22, 15)); d.rectangle((0, 2100, WW, 2130), fill=(30, 20, 14))
    # chimney
    d.rectangle((60, 0, 820, 2112), fill=(96, 92, 90))
    for row in range(0, 2112, 110):
        x = 60 - int(r.integers(0, 90))
        while x < 820:
            wd = int(r.integers(110, 230)); c = int(r.integers(72, 118)); d.rectangle((max(x, 60), row, min(x + wd, 820), row + 104), fill=(c, c - 4, c - 6), outline=(40, 38, 38), width=5); x += wd + 6
    d.rounded_rectangle((250, 1420, 640, 2112), 160, fill=(8, 6, 6)); d.rectangle((250, 1700, 640, 2112), fill=(8, 6, 6)); d.rectangle((200, 1320, 700, 1400), fill=(52, 34, 22), outline=(26, 16, 10), width=6)
    d.rectangle((210, 2090, 690, 2150), fill=(80, 78, 78), outline=(30, 30, 30), width=5)
    for i in range(8): d.ellipse((330 + i * 28, 2070 - (i % 3) * 8, 370 + i * 28, 2100), fill=(36, 34, 34))
    # window
    d.rectangle((1470, 550, 2030, 1270), fill=(26, 17, 11)); g = np.linspace(0, 1, 640)[:, None, None]
    glass = (np.array([20, 40, 90])[None, None, :] * (1 - g) + np.array([60, 90, 150])[None, None, :] * g).repeat(480, 1).astype(np.uint8)
    im.paste(Image.fromarray(glass), (1510, 590)); d.rectangle((1740, 590, 1760, 1230), fill=(26, 17, 11)); d.rectangle((1510, 890, 1990, 910), fill=(26, 17, 11))
    # speaker
    d.rounded_rectangle((920, 250, 1260, 520), 30, fill=(28, 28, 32), outline=(70, 70, 76), width=6); d.rectangle((960, 350, 1220, 480), fill=(14, 14, 16))
    for yy in range(356, 480, 14): d.line((966, yy, 1214, yy), fill=(60, 60, 66), width=4)
    d.ellipse((1074, 285, 1106, 317), fill=(70, 10, 10), outline=(10, 10, 10), width=3)
    # thermometer plaque
    d.rounded_rectangle((1310, 800, 1430, 1300), 20, fill=(176, 170, 156), outline=(40, 30, 20), width=6); d.rounded_rectangle((1356, 840, 1384, 1190), 12, fill=(225, 228, 232)); d.ellipse((1348, 1180, 1392, 1224), fill=(165, 25, 25)); d.rectangle((1362, 1100, 1378, 1190), fill=(165, 25, 25))
    # shelf + stub candle
    d.rectangle((850, 1500, 1250, 1535), fill=(48, 31, 20), outline=(20, 12, 8), width=4); d.polygon([(880, 1535), (940, 1535), (880, 1600)], fill=(40, 26, 16)); d.polygon([(1160, 1535), (1220, 1535), (1220, 1600)], fill=(40, 26, 16))
    d.rectangle((990, 1430, 1030, 1500), fill=(228, 214, 180), outline=(100, 90, 70), width=4); d.line((1010, 1430, 1010, 1415), fill=(20, 16, 14), width=5)
    # table + objects
    d.rectangle((1230, 2230, 2110, 2330), fill=(56, 36, 24), outline=(22, 14, 9), width=6)
    for x in (1260, 2050): d.rectangle((x, 2330, x + 36, 2520), fill=(46, 30, 20))
    for k, (x, y, w_) in {'axe': (1300, 2130, 250), 'lighter': (1590, 2180, 110), 'knife': (1720, 2200, 230), 'candles': (1950, 2090, 170)}.items():
        o = O[k]; o2 = o.resize((w_, int(o.size[1] * w_ / o.size[0])), Image.LANCZOS); im.paste(o2, (x, y), o2)
    o = O['map'].resize((150, 205)); im.paste(o, (1560, 2120), o)
    im = lighting(im, [(1750, 900, 1300, (0.35, 0.55, 1.0), 1.0), (1010, 1400, 520, (1.0, .62, .28), .9), (1700, 2300, 800, (.5, .6, .9), .5), (1080, 3000, 1500, (.55, .65, .9), .9), (1090, 380, 350, (.5, .5, .55), .35)], 0.36)
    return im
WORLD = build_world()
LEAN = 0  # flame lean handled in draw

def cam(cx, cy, z):
    bw = WW / z; bh = bw * H / W
    x0 = min(max(cx - bw / 2, 0), WW - bw); y0 = min(max(cy - bh / 2, 0), WH - bh)
    im = WORLD.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.BILINEAR)
    return im, x0, y0, bw / W

def kf(T, keys):
    if T <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if T <= b[0]:
            e = ease((T - a[0]) / (b[0] - a[0])); return tuple(lerp(p, q, e) for p, q in zip(a[1:], b[1:]))
    return keys[-1][1:]

ROWS = [('mex', 280, 2650, .95), ('gtm', 780, 2650, .95), ('pri', 1280, 2650, .95), ('col', 1780, 2650, .95), ('chl', 380, 2950, 1.2), ('ecu', 1080, 2950, 1.2), ('slv', 1780, 2950, 1.2), ('arg', 480, 3450, 1.55), ('ven', 1080, 3450, 1.55), ('per', 1680, 3450, 1.55)]

def flame(arr, sx, sy, k, lean, T, seed=0, kind='warm'):
    fl = 1 + .12 * math.sin(T * 17 + seed) + .08 * math.sin(T * 29 + seed * 2)
    add_glow(arr, sx, sy, 190 * k * fl, 'warm', .8)
    img = Image.fromarray(arr.astype(np.uint8)) if False else None
    return fl

def draw_flame_pil(im, sx, sy, k, lean, T, seed=0):
    d = ImageDraw.Draw(im); fl = 1 + .1 * math.sin(T * 19 + seed) + .06 * math.sin(T * 31 + seed)
    h = 62 * k * fl; w = 20 * k; ln = lean * 18 * k * fl
    d.polygon([(sx - w, sy), (sx - w * .6 + ln * .3, sy - h * .5), (sx + ln, sy - h), (sx + w * .6 + ln * .3, sy - h * .5), (sx + w, sy)], fill=(255, 170, 50))
    d.polygon([(sx - w * .5, sy), (sx + ln * .6, sy - h * .62), (sx + w * .5, sy)], fill=(255, 232, 150))

def world_scene(T, cx, cy, z, mode):
    im, x0, y0, k = cam(cx, cy, z)
    S = lambda wx, wy: ((wx - x0) / k, (wy - y0) / k)
    # snow in window
    d = ImageDraw.Draw(im)
    for i in range(70):
        sx_ = 1520 + (i * 137 + T * 60 * (1 + i % 3 * .3)) % 470; sy_ = 600 + (i * 71 + T * 110 * (1 + i % 4 * .25)) % 620
        px, py = S(sx_ + 12 * math.sin(T * 2 + i), sy_); r_ = max(1.5, 7 / k * (.6 + i % 3 * .3)); d.ellipse((px - r_, py - r_, px + r_, py + r_), fill=(225, 235, 250))
    # stub candle flame leaning toward chimney (left)
    px, py = S(1010, 1415); draw_flame_pil(im, px, py, 1.9 / k, -1.6, T, 3)
    # chars
    items = ROWS
    for ph, (key, x, y, sc) in enumerate(items):
        ex, mo, dx, dy, rot = char_state(key, T, ph)
        s = spr(key, ex, mo); sc2 = sc / k
        sp = s.resize((max(2, int(s.size[0] * sc2)), max(2, int(s.size[1] * sc2))), Image.BILINEAR)
        if abs(rot) > .2: sp = sp.rotate(rot, expand=True, resample=Image.BICUBIC)
        px, py = S(x + dx, y + dy); im.paste(sp, (int(px - sp.size[0] / 2), int(py - sp.size[1] + 30 * sc2)), sp)
    arr = np.array(im, np.float32)
    px, py = S(1010, 1400); add_glow(arr, px, py, 300 / k * (1 + .08 * math.sin(T * 17)), 'warm', .55)
    if mode == 'speaker' or mode == 'all':
        a = 0.0
        if 7.6 < T < 9.9: a = .6 + .4 * math.sin(T * 9) if T < 8.0 or T > 8.75 else 1.0
        if T >= 17.0: a = .3 + .3 * math.sin(T * 5)
        a = max(a, 0)
        if a > 0: px, py = S(1090, 301); add_glow(arr, px, py, 330 / k, 'red', a)
    return arr

def char_state(key, T, ph):
    bob = 5 * math.sin(T * 2.3 + ph * 1.7)
    if T < 6.4: return 'sleep', 0, 0, bob * .4 + 6, (ph % 3 - 1) * 4
    if T < 9.6:
        e = 'neutral' if (T - 6.4) * (1 + ph % 3 * .3) > 1.0 + ph * .12 else 'sleep'
        return e, 0, 0, bob, (ph % 3 - 1) * 2 * (9.6 - T) / 3
    if T < 17.0 and key == 'arg' and 9.8 < T < 11.9: return 'neutral', .5 + .5 * math.sin(T * 14), 0, bob - 8 * abs(math.sin(T * 4)), 3 * math.sin(T * 5)
    if T < 17.0 and key == 'ven' and 12.1 < T < 13.8: return 'angry', .6 + .4 * math.sin(T * 17), 9 * math.sin(T * 40), bob - 30 * abs(math.sin((T - 12.1) * 7)), 4 * math.sin(T * 33)
    if T < 17.0 and key == 'per' and 14.1 < T < 16.2: return 'sad', .25 + .2 * math.sin(T * 9), 0, 22 + bob * .5, -7
    if T < 17.0 and key == 'ven' and T > 9.6: return 'angry', 0, 0, bob, 2
    if T < 17.0 and key == 'per': return 'sad', 0, 0, bob + 8, -4
    return ('worried' if ph % 2 == 0 else 'neutral'), 0, 0, bob, 2 * math.sin(T * 1.3 + ph)

# ---------------- screen-space backgrounds ----------------
TABLE = wood(W, H, 230, (58, 38, 26), 21, False)
def mkbg(light=1.0):
    a = np.array(TABLE, np.float32) * .55
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); d = np.clip(1 - np.hypot(x - 540, y - 820) / 1000, 0, 1) ** 1.4
    a = a * (0.3 + 1.1 * d[..., None] * light) + d[..., None] * np.array([40, 22, 8], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
BG = mkbg()
DARK = Image.fromarray((np.array(TABLE, np.float32) * .22).astype(np.uint8))

def shadow_paste(im, sp, cx, cy):
    sh = Image.new('RGBA', sp.size, (0, 0, 0, 0)); sh.putalpha(sp.split()[3].point(lambda v: int(v * .7))); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(sh, (int(cx - sp.size[0] / 2 + 18), int(cy - sp.size[1] / 2 + 26)), sh); im.paste(sp, (int(cx - sp.size[0] / 2), int(cy - sp.size[1] / 2)), sp)

def obj_scene(T, t0, t1, key, label, w, rot=0, cy=820, spark=None):
    im = BG.copy(); u = (T - t0) / (t1 - t0); sc = lerp(1.0, 1.09, u)
    o = O[key]; ww = int(w * sc); sp = o.resize((ww, int(o.size[1] * ww / o.size[0])), Image.LANCZOS)
    if rot: sp = sp.rotate(rot + 2 * math.sin(T * 1.3), expand=True, resample=Image.BICUBIC)
    shadow_paste(im, sp, 540 + 3 * math.sin(T * 2), cy)
    d = ImageDraw.Draw(im); text_c(d, (540, 250), label, font(92, 'ExtraBold'), (225, 225, 225), 6)
    arr = np.array(im, np.float32)
    if spark and 0 < T - spark < .25:
        add_glow(arr, 560, 560, 330, 'white', 1.0 - (T - spark) * 3); add_glow(arr, 560, 560, 220, 'warm', .8)
    return arr

def paper_img():
    Wd, Ht = 860, 1260; r = np.random.default_rng(5)
    yy, xx = np.mgrid[0:Ht, 0:Wd].astype(np.float32); edge = np.minimum(np.minimum(xx, Wd - xx), np.minimum(yy, Ht - yy)); f = .5 + .5 * np.clip(edge / 90, 0, 1)
    blot = np.clip(1 - np.hypot(xx - 640, yy - 960) / 260, 0, 1)[..., None] * 25
    a = np.array([218, 198, 156], np.float32)[None, None, :] * f[..., None] * (.94 + .1 * r.random((Ht, Wd, 1))) - blot
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
PAPER = paper_img()
NOTE = [(52.95, 'El frío no se vence con fuerza.'), (55.7, 'Lo que pesa, no te salvará.'), (57.4, 'Lo que brilla poco, gástalo una sola vez, y donde más dure.'), (62.4, 'El humo conoce la salida.')]

def wrap(s, f, wmax):
    out, cur = [], ''
    for wd in s.split():
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) <= wmax: cur = t
        else: out.append(cur); cur = wd
    return out + [cur]

def note_scene(T):
    im = BG.copy(); u = ease((T - 50.0) / .9); ycen = 780 + (1 - u) * 1100
    pap = PAPER.copy(); d = ImageDraw.Draw(pap)
    text_c(d, (430, 120), 'NOTA', serif(60), (70, 40, 25))
    d.line((250, 165, 610, 165), fill=(70, 40, 25), width=4)
    f = serif(62); y = 250
    for t0, s in NOTE:
        ls = wrap(s, f, 700); a = ease((T - t0) / .6) if T >= t0 else 0
        cur = T >= t0 and not any(T >= t1 for t1, _ in NOTE if t1 > t0)
        for l in ls:
            col = (40, 26, 18) if cur else (78, 56, 42)
            if T < t0: y += 82; continue
            d.text((90, y), l, font=f, fill=col); y += 82
        y += 40
    zoom = lerp(1.0, 1.07, (T - 50) / 14); pw = int(860 * zoom)
    p2 = pap.resize((pw, int(1260 * zoom)), Image.LANCZOS).rotate(-1.5 + math.sin(T) * .4, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    m = Image.new('L', p2.size, 255)
    im.paste(p2, (int(540 - p2.size[0] / 2), int(ycen - p2.size[1] / 2)))
    return np.array(im, np.float32)

def termo_bg():
    im = Image.fromarray((np.array(wood(W, H, 150, (70, 46, 30), 31, True), np.float32) * .5).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((330, 250, 750, 1640), 36, fill=(184, 178, 160), outline=(30, 20, 14), width=10)
    d.rounded_rectangle((330, 250, 750, 1640), 36, outline=(110, 100, 84), width=3)
    d.rounded_rectangle((512, 400, 568, 1400), 28, fill=(228, 232, 236), outline=(90, 90, 96), width=4)
    d.ellipse((488, 1380, 592, 1484), fill=(120, 18, 18), outline=(60, 10, 10), width=5)
    for i, t in enumerate(range(10, -11, -1)):
        y = 460 + (10 - t) * 45
        L = 54 if t % 5 == 0 else 28; d.line((470 - L, y, 500, y), fill=(50, 40, 32), width=4); d.line((580, y, 610 + L - 28 if t % 5 else 640, y), fill=(50, 40, 32), width=4)
        if t % 5 == 0: text_c(d, (400, y), str(t), font(40, 'Bold'), (50, 40, 32));
    return im
TERMO = termo_bg()
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
_n = np.array(Image.fromarray((np.random.default_rng(11).random((H // 60, W // 60)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
_e = np.clip(1 - np.minimum(np.minimum(xx_, W - xx_) / (W * .45), np.minimum(yy_, H - yy_) / (H * .35)), 0, 1)
FROST = (np.clip((_n * .6 + _e * 1.0 - .6) * 1.6, 0, 1) * .8)[..., None].astype(np.float32)

def termo_scene(T, temp, big=True, label=None):
    im = TERMO.copy(); d = ImageDraw.Draw(im)
    ytop = 460 + (10 - temp) * 45
    d.rounded_rectangle((522, ytop, 558, 1400), 16, fill=(185, 28, 28)); d.line((528, ytop + 8, 528, 1390), fill=(235, 120, 110), width=4)
    text_c(d, (540, 140), f'{temp:.0f}°C' if abs(temp - round(temp)) < .05 else f'{temp:.1f}°C', font(150, 'ExtraBold'), (205, 226, 240), 5)
    arr = np.array(im, np.float32)
    return arr

# ---------------- subtitles ----------------
SUBS = [(.3, 1.7, 'Diez naciones.'), (1.9, 4.2, 'Una cabaña sepultada en la nieve.'), (4.5, 7.2, 'Nadie sabe por qué están aquí.'), (8.0, 8.8, 'Yo sí.'),
 (9.8, 11.9, 'ARGENTINA: «Tenemos que hablar. Ahora.»'), (12.1, 13.8, 'VENEZUELA: «¡Aquí se viene a pelear!»'), (14.1, 16.2, 'PERÚ: «Ya no queda nada por hacer...»'),
 (17.3, 19.7, 'Bienvenidos a ESCAPE: WORLD SURVIVAL.'), (20.3, 21.8, 'Mis reglas son simples.'), (22.3, 24.3, 'Cada país, una decisión.'), (24.8, 26.8, 'La audiencia decide por ustedes.'),
 (27.3, 28.7, 'Cien de resistencia.'), (29.1, 30.9, 'Cada error cuesta recursos.'), (31.3, 33.4, 'Cero... es la eliminación.'), (34.0, 36.1, 'Y la cabaña empeora.'), (36.3, 37.3, 'Seis grados.'), (37.4, 38.8, 'Cae tres, cada hora.'),
 (39.4, 40.2, 'Un hacha.'), (40.5, 43.6, 'Un encendedor de una sola chispa.'), (44.0, 44.9, 'Un cuchillo.'), (45.2, 46.5, 'Un mapa.'), (46.9, 47.9, 'Cinco velas.'), (48.1, 49.0, 'Troncos húmedos.'), (49.1, 50.0, 'Tres leños secos.'),
 (50.2, 51.0, 'Y una nota.'), (51.4, 52.7, 'Léanla con cuidado.'), (52.95, 55.6, 'El frío no se vence con fuerza.'), (55.7, 57.2, 'Lo que pesa, no te salvará.'), (57.4, 61.8, 'Lo que brilla poco, gástalo una sola vez, y donde más dure.'), (62.4, 63.9, 'El humo conoce la salida.'),
 (64.3, 65.4, 'Tres caminos.'), (65.6, 69.0, 'A: la chimenea, con los leños secos.'), (69.4, 72.5, 'B: el muro, con el hacha.'), (72.9, 75.1, 'C: las cinco velas.'),
 (75.7, 77.6, 'Cada país, una decisión.'), (78.0, 80.6, 'Escriban país y letra en los comentarios.'), (81.0, 82.6, 'Veinticuatro horas.'), (83.0, 85.3, 'Después... no habrá marcha atrás.')]

def subs(im, T):
    for t0, t1, s in SUBS:
        if t0 <= T < t1 + .15:
            d = ImageDraw.Draw(im); f = font(58, 'ExtraBold'); ls = wrap(s, f, 900); y = 1535 - (len(ls) - 1) * 34
            for l in ls:
                x = W / 2
                if ':' in l and l.split(':')[0].isupper() and len(l.split(':')[0]) < 12 and 9 < t0 < 17:
                    pass
                d.text((x, y), l, font=f, fill=(245, 245, 240), anchor='mm', stroke_width=9, stroke_fill=(0, 0, 0)); y += 68
            break
    return im

# ---------------- UI scenes ----------------
def pill(d, box, fill, outline=None, r=26, w=4): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)

def rules1(T):
    im = DARK.copy(); d = ImageDraw.Draw(im)
    if T < 22.0:
        pass
    return im

def scene_title(T):
    arr = world_scene(T, 1080, 2000, lerp(1.4, 1.2, (T - 17) / 5), 'all') * .28
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    u = ease((T - 17.2) / .5); gl = (T - 17.2) < .45 or (int(T * 11) % 23 == 0)
    if T < 20.2:
        for dx, col in ((-7, (200, 20, 20)), (7, (40, 120, 200)), (0, (240, 240, 235))) if gl else ((0, (240, 240, 235)),):
            text_c(d, (540 + dx, 780), 'ESCAPE', font(220, 'Black'), col); text_c(d, (540 + dx, 970), 'WORLD SURVIVAL', font(88, 'ExtraBold'), col)
        d.rectangle((160, 1050, 160 + 760 * u, 1058), fill=(190, 25, 25))
    else:
        u2 = ease((T - 20.3) / .4)
        text_c(d, (540, 820), 'MIS REGLAS', font(150, 'Black'), (240, 240, 235)); text_c(d, (540, 990), 'SON SIMPLES', font(100, 'ExtraBold'), (190, 25, 25)); d.rectangle((160, 1090, 160 + 760 * u2, 1098), fill=(190, 25, 25))
    return np.array(im, np.float32)

CHIPS = list(NAMES.keys())
def scene_vote_rule(T):
    im = DARK.copy(); d = ImageDraw.Draw(im)
    if T < 24.7:
        text_c(d, (540, 190), '1 PAÍS', font(120, 'Black'), (240, 240, 235)); text_c(d, (540, 330), '= 1 DECISIÓN', font(84, 'ExtraBold'), (190, 25, 25))
    else:
        text_c(d, (540, 190), 'LA AUDIENCIA', font(110, 'Black'), (240, 240, 235)); text_c(d, (540, 330), 'DECIDE', font(110, 'Black'), (190, 25, 25))
    for i, k in enumerate(CHIPS):
        a = ease((T - 22.3 - i * .12) / .35)
        if a <= 0: continue
        col, row = i % 2, i // 2; x0 = 50 + col * 500; y0 = 440 + row * 150 + (1 - a) * 40
        pill(d, (x0, y0, x0 + 480, y0 + 134), (26, 24, 28), (80, 78, 84), 24, 3)
        fl = flag_img(k, 180, 122).convert('RGBA'); m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 179, 121), 16, fill=255); im.paste(fl, (int(x0 + 14), int(y0 + 6)), m)
        text_c(d, (x0 + 230, y0 + 67), NAMES[k], font(38 if len(NAMES[k]) > 9 else 46, 'Bold'), (230, 230, 226), 0, anchor='lm')
    if T >= 24.9:
        for j, (nm, let) in enumerate([('Chile', 'B'), ('Perú', 'A'), ('México', 'C')]):
            a = ease((T - 25.2 - j * .45) / .3)
            if a <= 0: continue
            y0 = 1215 + j * 86 - (1 - a) * 30
            pill(d, (140, y0, 940, y0 + 74), (240, 240, 236), None, 36, 0); d.ellipse((156, y0 + 8, 214, y0 + 66), fill=(60, 60, 70)); text_c(d, (240, y0 + 37), f'{nm} {let}', font(42, 'Bold'), (20, 20, 24), anchor='lm')
    return np.array(im, np.float32)

def scene_resist(T):
    im = DARK.copy(); d = ImageDraw.Draw(im)
    v = 100.0
    if T > 29.3: v = lerp(100, 75, ease((T - 29.3) / .35))
    if T > 31.4: v = lerp(75, 0, ease((T - 31.4) / 1.3))
    text_c(d, (540, 150), 'RESISTENCIA', font(80, 'ExtraBold'), (225, 225, 222), 4)
    text_c(d, (540, 380), f'{int(round(v))}', font(300, 'Black'), (235, 235, 230) if v > 20 else (200, 40, 40), 6)
    pill(d, (90, 560, 990, 630), (22, 20, 22), (120, 118, 124), 30, 4)
    if v > 0: pill(d, (96, 566, 96 + 888 * v / 100, 624), (80, 170, 90) if v > 30 else (190, 40, 40), None, 26, 0)
    key = 'chl'; ex = 'dead' if T > 32.2 else ('worried' if T > 29.3 else 'neutral')
    s = spr(key, ex, 0); s = s.resize((int(s.size[0] * 1.5), int(s.size[1] * 1.5)), Image.BILINEAR)
    if T > 32.2: s = Image.fromarray(np.array(s.convert('LA').convert('RGBA')))
    yoff = 20 * math.sin(T * 2) + (math.sin(T * 60) * 12 if 29.3 < T < 29.7 else 0)
    im.paste(s, (int(540 - s.size[0] / 2), int(800 + yoff)), s)
    if 29.3 < T < 32.3:
        a = ease((T - 29.6) / .3)
        if a > 0:
            ax = O['axe'].resize((300, 156)); ax = ax.rotate(20, expand=True); im.paste(ax, (130, 1190), ax); d.line((130, 1190, 440, 1420), fill=(200, 30, 30), width=14); d.line((440, 1190, 130, 1420), fill=(200, 30, 30), width=14)
            text_c(d, (700, 1300), '-25', font(130, 'Black'), (200, 40, 40), 4)
    if T > 32.4:
        st = Image.new('RGBA', (700, 160), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle((0, 0, 699, 159), 20, outline=(200, 30, 30, 255), width=10); text_c(sd, (350, 80), 'ELIMINADO', font(100, 'Black'), (200, 30, 30, 255)); st = st.rotate(-8, expand=True)
        im.paste(st, (int(540 - st.size[0] / 2), 1230), st)
    arr = np.array(im, np.float32)
    if 29.3 < T < 29.6: arr[..., 0] = np.minimum(255, arr[..., 0] + 90 * (1 - (T - 29.3) / .3))
    return arr

def scene_termo_rules(T):
    temp = 6.0
    if T > 37.4: temp = lerp(6, 3, ease((T - 37.4) / 1.3))
    arr = termo_scene(T, temp)
    if T > 37.3:
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); a = ease((T - 37.5) / .3)
        text_c(d, (540, 1760), '-3°C / HORA', font(80, 'Black'), (120, 170, 235))
        arr = np.array(im, np.float32)
    return arr

def scene_options(T):
    im = DARK.copy(); d = ImageDraw.Draw(im)
    text_c(d, (540, 130), 'TRES CAMINOS', font(84, 'Black'), (240, 240, 235))
    specs = [('A', 'ENCENDER LA CHIMENEA', 'con los leños secos', 65.4), ('B', 'ROMPER EL MURO', 'con el hacha', 69.2), ('C', 'ENCENDER LAS 5 VELAS', '', 72.7)]
    for i, (L, t1, t2, t0) in enumerate(specs):
        a = ease((T - t0) / .4);
        if a <= 0: continue
        y0 = int(230 + i * 350 + (1 - a) * 60); x0 = 70
        pill(d, (40, y0, 1040, y0 + 320), (24, 23, 28), (150, 148, 156), 30, 5)
        d.ellipse((70, y0 + 90, 210, y0 + 230), fill=(235, 235, 230)); text_c(d, (140, y0 + 160), L, font(112, 'Black'), (18, 18, 22))
        if L == 'A':
            d.rounded_rectangle((250, y0 + 40, 600, y0 + 290), 70, fill=(8, 6, 6), outline=(80, 78, 78), width=8); o = O['dry'].resize((300, 186)); im.paste(o, (275, y0 + 100), o)
        elif L == 'B':
            w_ = O['wall'].resize((350, 250)); im.paste(w_, (250, y0 + 40)); ax = O['axe'].resize((330, 172)).rotate(25, expand=True, resample=Image.BICUBIC); im.paste(ax, (255, y0 + 70), ax)
        else:
            o = O['candles'].resize((350, 249)); im.paste(o, (250, y0 + 45), o)
        f = font(48, 'ExtraBold'); ls = wrap(t1, f, 400)
        yy = y0 + 150 - (len(ls) + (1 if t2 else 0) - 1) * 30
        for l in ls: d.text((630, yy), l, font=f, fill=(240, 240, 235), anchor='lm'); yy += 60
        if t2: d.text((630, yy), t2, font=font(42, 'Medium'), fill=(170, 170, 176), anchor='lm')
    return np.array(im, np.float32)

def scene_cta(T):
    im = DARK.copy(); d = ImageDraw.Draw(im)
    if T < 78.0:
        text_c(d, (540, 560), 'CADA PAÍS', font(150, 'Black'), (240, 240, 235)); text_c(d, (540, 760), 'UNA DECISIÓN', font(120, 'Black'), (190, 25, 25))
        for i, k in enumerate(CHIPS):
            fl = flag_img(k, 150, 100).convert('RGBA'); m = Image.new('L', fl.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 149, 99), 14, fill=255)
            a = ease((T - 75.9 - i * .06) / .3)
            if a > 0: im.paste(fl, (60 + (i % 5) * 190, 1000 + (i // 5) * 140), m)
    elif T < 80.9:
        text_c(d, (540, 330), 'COMENTA', font(120, 'Black'), (240, 240, 235)); text_c(d, (540, 470), 'PAÍS + LETRA', font(100, 'Black'), (190, 25, 25))
        pill(d, (60, 700, 1020, 900), (240, 240, 236), None, 50, 0); d.ellipse((90, 745, 170, 825), fill=(60, 60, 70))
        s = 'Chile B'; n = int(min(len(s), max(0, (T - 78.6) * 5))); cur = '|' if int(T * 3) % 2 == 0 else ''
        d.text((210, 800), s[:n] + cur, font=font(66, 'Bold'), fill=(20, 20, 24), anchor='lm')
        text_c(d, (540, 1000), 'A  ·  B  ·  C', font(110, 'Black'), (225, 225, 220))
    elif T < 83.0:
        secs = max(0, 86400 - int((T - 81.0) * 5400)); hh, mm, ss = secs // 3600, secs % 3600 // 60, secs % 60
        text_c(d, (540, 450), '24 HORAS', font(150, 'Black'), (240, 240, 235))
        text_c(d, (540, 800), f'{hh:02d}:{mm:02d}:{ss:02d}', font(200, 'Black'), (190, 25, 25))
        d.arc((190, 960, 890, 1660), -90, -90 + 360 * (1 - (T - 81) / 2), fill=(190, 25, 25), width=14)
    elif T < 85.3:
        a = ease((T - 83.0) / .6)
        text_c(d, (540, 760), 'NO HABRÁ', font(170, 'Black'), (int(240 * a), int(240 * a), int(235 * a))); text_c(d, (540, 960), 'MARCHA ATRÁS', font(150, 'Black'), (int(200 * a), int(25 * a), int(25 * a)))
    else:
        text_c(d, (540, 700), 'ESCAPE', font(220, 'Black'), (240, 240, 235)); text_c(d, (540, 890), 'WORLD SURVIVAL', font(88, 'ExtraBold'), (240, 240, 235)); d.rectangle((160, 970, 920, 978), fill=(190, 25, 25))
        text_c(d, (540, 1090), 'EPISODIO 1 · LA ÚLTIMA CHISPA', font(52, 'Bold'), (190, 190, 186)); text_c(d, (540, 1200), 'RESULTADO EN 24 H', font(52, 'Bold'), (190, 25, 25))
    return np.array(im, np.float32)

# ---------------- timeline ----------------
def render(T):
    sub = True
    if T < 4.2: arr = termo_scene(T, 6.0 - 0.0); z = 1 + (T / 4.2) * .12; arr = arr
    elif T < 7.4: arr = world_scene(T, *kf(T, [(4.2, 1080, 3000, 1.0), (7.4, 1080, 3000, 1.35)]), 'all')
    elif T < 9.6: arr = world_scene(T, *kf(T, [(7.4, 1100, 700, 1.7), (9.6, 1090, 420, 3.2)]), 'speaker')
    elif T < 16.4: arr = world_scene(T, *kf(T, [(9.6, 1080, 3000, 1.0), (10.0, 560, 3250, 2.0), (11.9, 520, 3250, 2.0), (12.3, 1080, 3250, 2.0), (13.9, 1080, 3250, 2.0), (14.3, 1600, 3250, 2.0), (16.4, 1080, 3050, 1.1)]), 'all')
    elif T < 17.0: arr = np.zeros((H, W, 3), np.float32) + (30 if int(T * 30) % 5 == 0 else 0)
    elif T < 22.0: arr = scene_title(T)
    elif T < 27.3: arr = scene_vote_rule(T)
    elif T < 33.7: arr = scene_resist(T)
    elif T < 39.2: arr = scene_termo_rules(T)
    elif T < 39.2 + 1.1: arr = obj_scene(T, 39.2, 40.3, 'axe', 'HACHA', 960, -18)
    elif T < 43.8: arr = obj_scene(T, 40.3, 43.8, 'lighter', 'ENCENDEDOR', 940, 0, 800, spark=42.6)
    elif T < 45.0: arr = obj_scene(T, 43.8, 45.0, 'knife', 'CUCHILLO', 1000, -12)
    elif T < 46.9: arr = obj_scene(T, 45.0, 46.9, 'map', 'MAPA', 800, 0, 900)
    elif T < 48.0: arr = obj_scene(T, 46.9, 48.0, 'candles', 'CINCO VELAS', 920, 0)
    elif T < 49.0: arr = obj_scene(T, 48.0, 49.0, 'wet', 'TRONCOS HÚMEDOS', 980, -4)
    elif T < 50.0: arr = obj_scene(T, 49.0, 50.0, 'dry', 'TRES LEÑOS SECOS', 980, 4)
    elif T < 60.0: arr = note_scene(T)
    elif T < 62.3: arr = obj_scene(T, 60.0, 62.3, 'map', 'MAPA', 800, 0, 900)
    elif T < 63.6: arr = note_scene(T) if True else None
    elif T < 64.0: arr = world_scene(T, 900, 1450, 1.9, 'all')
    elif T < 75.25: arr = scene_options(T)
    else: arr = scene_cta(T)
    return arr

def frame(i):
    T = i / FPS; arr = render(T)
    a = np.clip(arr, 0, 255)
    # global fx
    fr = min(.55, max(0, (T - 33.7) / 60)) * (1 if T > 33 else 0)
    if 33.7 <= T < 39.2: fr = .35 + .3 * ease((T - 36.5) / 2.7)
    if 0 < T < 4.2: fr = .25
    a = a * VIG * (1 + .035 * math.sin(T * 23 + 1.3) + .02 * math.sin(T * 7))
    a = a * np.array([.96, 1.0, 1.06], np.float32)[None, None, :]
    a = a + FROST * fr * np.array([70, 100, 130], np.float32)
    a = a + GRAIN[i % 6]
    fade = min(1, T / .8) * min(1, (DUR - T) / .6)
    a = np.clip(a * fade, 0, 255).astype(np.uint8)
    im = Image.fromarray(a)
    if 0 < T < 85.3 or T > 85.3: im = subs(im, T) if not (17.0 <= T < 17.2) and T < 85.3 else im
    return im.tobytes()

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]
        cols = 4; rows = (len(ts) + cols - 1) // cols; sheet = Image.new('RGB', (cols * 360, rows * 640))
        for j, t in enumerate(ts):
            im = Image.frombytes('RGB', (W, H), frame(int(t * FPS))).resize((360, 640)); sheet.paste(im, ((j % cols) * 360, (j // cols) * 640))
        sheet.save('sheet.jpg', quality=82)
    else:
        n = int(DUR * FPS); out = sys.argv[1]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for k, b in enumerate(pool.imap(frame, range(n), chunksize=6)):
                p.stdin.write(b)
                if k % 200 == 0: print(k, n, flush=True)
        p.stdin.close(); p.wait()

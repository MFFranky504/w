"""Portrait v4 (96x112): ojos de la hoja de referencia sobre una cara a escala; pelo generado desde el cráneo
(alineado por construcción); busto con puños, pliegues y detalles de ropa."""
import json, os, math
import numpy as np
from PIL import Image, ImageDraw
from lib import shade
from cast import resolve
from sprites import Paint

W, H, CX = 96, 112, 48
EYE_KIND = None                                                # fuerza 'm' o 'f' (para pruebas)
EYE_F = 'n'                                                    # expresión neutra femenina: 'n' o 'flat'
DY = 6                                                       # la cabeza se baja DY px sobre el cuerpo
HERE = os.path.dirname(os.path.abspath(__file__))
EYES = json.load(open(os.path.join(HERE, 'eye_templates.json')))
SKULL = (CX, 38, 22, 22)            # centro x, y, rx, ry del cráneo (el pelo se genera desde aquí)

# flequillo: puntas (dx, y) de derecha a izquierda; lado = longitud de las patillas / pelo lateral
STYLES = {
    'you':   dict(fringe=[(19, 36), (15, 39), (12, 33), (8, 40), (4, 34), (0, 42), (-4, 34), (-8, 40), (-12, 33), (-16, 38), (-19, 34)], side=40,
                  spikes=[(150, 6, 1), (128, 7, 1), (105, 5, -1), (70, 7, -1), (45, 6, -1), (22, 5, -1)], tuft=True),
    'king':  dict(fringe=[(19, 34), (15, 38), (11, 32), (7, 39), (3, 33), (-1, 40), (-5, 33), (-9, 39), (-14, 33), (-19, 35)], side=38,
                  spikes=[(152, 6, 1), (122, 6, 1), (92, 5, 1), (62, 7, -1), (34, 6, -1)]),
    'shag':  dict(fringe=[(19, 37), (13, 32), (6, 29), (-2, 29), (-10, 32), (-16, 35), (-19, 40)], side=48,
                  spikes=[(156, 6, 1), (132, 8, 1), (108, 6, 1), (80, 4, 1), (24, 5, -1)]),
    'short': dict(fringe=[(19, 35), (13, 29), (4, 25), (-6, 25), (-14, 29), (-19, 35)], side=40, spikes=[(140, 3, 1), (40, 3, -1)]),
    'tab':   dict(fringe=[(19, 36), (15, 40), (11, 33), (7, 41), (3, 34), (-1, 42), (-5, 34), (-9, 41), (-13, 34), (-17, 40), (-19, 36)], side=70,
                  spikes=[]),
}
TOPS = {'hoodie': ((80, 96, 206), (54, 64, 152), (126, 146, 238)), 'grey': ((158, 162, 174), (112, 116, 132), (210, 214, 224)),
        'cardigan': ((230, 176, 72), (184, 130, 44), (250, 210, 120)), 'plaid': ((204, 70, 62), (150, 40, 44), (238, 118, 100)),
        'tux': ((34, 34, 46), (18, 18, 28), (88, 88, 110)), 'teacher': ((236, 232, 220), (196, 192, 182), (252, 252, 248)),
        'blazer': ((54, 72, 124), (34, 46, 86), (100, 124, 184)), 'argentina': ((150, 206, 246), (100, 160, 214), (230, 246, 255)),
        'polo': ((212, 152, 82), (160, 104, 50), (250, 202, 132)), 'coat': ((246, 248, 252), (196, 206, 224), (255, 255, 255)),
        'uniform': ((246, 122, 162), (206, 84, 126), (255, 172, 202)), 'tee_blue': ((70, 130, 220), (40, 86, 170), (130, 180, 250))}


def pts_ellipse(cx, cy, rx, ry, a0, a1, n=28):
    return [(cx + rx * math.cos(math.radians(a)), cy - ry * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def fringe_y(fr, dx):
    xs = [p[0] for p in fr][::-1]; ys = [p[1] for p in fr][::-1]
    return float(np.interp(dx, xs, ys))


def hair_polygon(style):
    st = STYLES[style]; fr = st['fringe']; cx, cy, rx, ry = SKULL; side = st['side']
    arc = pts_ellipse(cx, cy, rx + 1, ry + 1, 0, 180)
    k = .88                                                  # el flequillo se ajusta al cráneo más estrecho
    left = [(cx - rx - 1, side), (cx - 19, side), (cx - 19, fr[-1][1])]
    inner = [(cx + dx * k, min(y, 38)) for dx, y in fr[::-1]]
    right = [(cx + 19, side), (cx + rx + 1, side)]
    return arc + left + inner + right


def build(who='you', expr='n', blink=False, outfit=None, gesture='fists', turn=2):
    CS = resolve(who); style = CS['style']; outfit = outfit or CS['outfit']
    sk = CS['skin']; skd = shade(sk, .86); skdd = shade(sk, .7); skl = shade(sk, 1.05); hc = CS['hair']
    tb, td, tl = TOPS.get(outfit, TOPS['hoodie'])
    PB, PH = Paint(W, H), Paint(W, H)
    P = PB
    cx = CX; fc = cx + turn
    poly = lambda pts, col, **kw: P.add(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255), col, **kw)
    yy, xx = np.indices((H, W))

    # ------------------------------------------------ pelo largo trasero (Tabitha)
    if style == 'tab':
        poly([(25, 30 + DY), (21, 54 + DY), (18, 86 + DY), (24, 100 + DY), (72, 100 + DY), (78, 86 + DY), (75, 54 + DY), (71, 30 + DY)], hc['d'], edge_k=.45)

    # ------------------------------------------------ busto: hombros caídos, cuello de la ropa, pliegues
    torso = [(35, 80), (61, 80), (76, 83), (88, 92), (94, 106), (95, H), (1, H), (2, 106), (8, 92), (20, 83)]
    tm = poly(torso, tb, edge_k=.42)
    def clip(lines, col, w=1):
        im = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(im)
        for l in lines: dd.line(l, fill=255, width=w)
        P.a[(np.array(im) > 0) & tm] = (*col, 255)
    sh_m = P.mask(lambda d: d.polygon([(62, 80), (76, 83), (88, 92), (94, 106), (95, H), (66, H), (62, 96)], fill=255)) & tm
    P.a[sh_m] = (*td, 255)                                                        # sombra lateral (cel)
    lt_m = P.mask(lambda d: d.polygon([(8, 92), (20, 83), (26, 84), (14, 94), (8, 108), (2, 108)], fill=255)) & tm
    P.a[lt_m] = (*tl, 255)                                                        # luz en el hombro
    clip([[(24, 90), (20, 104), (22, H)], [(72, 90), (76, 104), (74, H)], [(40, 100), (38, H)]], td)   # pliegues
    # ------------------------------------------------ cuello (capa del cuerpo; la cabeza lo tapa por arriba)
    poly([(42, 70), (54, 70), (56, 84), (40, 84)], skd, sh=False, hi=False, edge_k=.55)
    neck_sh = P.mask(lambda d: d.polygon([(41, 72), (55, 72), (56, 80), (48, 83), (40, 80)], fill=255))
    P.a[neck_sh & (yy < 77)] = (*skdd, 255); P.a[neck_sh & (yy >= 77)] = (*shade(sk, .76), 255)

    if outfit == 'hoodie':
        poly([(30, 82), (38, 76), (58, 76), (66, 82), (58, 90), (38, 90)], td, edge_k=.5)            # capucha
        poly([(39, 85), (48, 93), (57, 85)], shade(td, .78), sh=False, hi=False)
        P.line([(41, 91), (39, 104)], (246, 246, 252)); P.line([(55, 91), (57, 102)], (246, 246, 252))
        P.rect(38, 104, 40, 107, (220, 220, 232)); P.rect(56, 102, 58, 105, (220, 220, 232))
        poly([(26, 100), (70, 100), (74, 112), (22, 112)], tl, edge_k=.55)                           # bolsillo canguro
    elif outfit == 'grey':
        poly([(37, 80), (59, 80), (55, 88), (41, 88)], td, edge_k=.5)                                  # cuello de canalé
        clip([[(x, 82), (x, 87)] for x in range(40, 57, 3)], shade(td, .8))
        P.line([(16, 98), (28, 96)], td); P.line([(68, 96), (80, 98)], td)
        poly([(28, 102), (68, 102), (72, 112), (24, 112)], tl, edge_k=.55)
    elif outfit == 'cardigan':
        poly([(38, 80), (58, 80), (48, 100)], (252, 242, 226), sh=False, edge_k=.55)
        P.line([(36, 80), (47, 102), (47, H)], td); P.line([(60, 80), (49, 102), (49, H)], td)
        for y in (104, 110): P.rect(51, y, 53, y + 1, (120, 80, 30))
    elif outfit == 'plaid':
        clip([[(3, y), (93, y + 1)] for y in range(90, H, 7)] + [[(x, 84), (x - 1, H)] for x in range(8, 92, 9)], td)
        poly([(38, 80), (58, 80), (48, 94)], (250, 248, 244), edge_k=.6)
        poly([(34, 80), (42, 92), (46, 84)], tl); poly([(62, 80), (54, 92), (50, 84)], tb)
    elif outfit == 'tux':
        poly([(39, 80), (57, 80), (51, 106), (45, 106)], (250, 250, 252), edge_k=.6)
        P.line([(32, 82), (45, 104)], td); P.line([(64, 82), (51, 104)], td)
        poly([(41, 86), (55, 86), (55, 92), (41, 92)], (190, 34, 54), edge_k=.5); P.rect(46, 87, 50, 91, (230, 80, 100))
    else:
        P.rect(30, 100, 66, 100, td)

    # ------------------------------------------------ mangas + puños (capa del cuerpo)
    if gesture == 'fists':                                                                      # mangas: hombro -> puño, con costura y pliegues
        for flip in (0, 1):
            col, hi_, lo_ = (tb, tl, td) if not flip else (td, tb, shade(td, .8))
            pts = [(20, 84), (8, 94), (2, 108), (18, 108), (24, 96)] if not flip else [(76, 84), (88, 94), (94, 108), (78, 108), (72, 96)]
            poly(pts, col, edge_k=.42)
            sx_ = (lambda x: x) if not flip else (lambda x: W - 1 - x)
            P.line([(sx_(20), 87), (sx_(11), 96), (sx_(7), 106)], hi_)                                # costura / luz
            P.line([(sx_(17), 98), (sx_(21), 104)], lo_); P.line([(sx_(13), 100), (sx_(15), 106)], lo_)   # pliegues del codo
    if gesture == 'fists':
        for fx, flip in ((14, 0), (82, 1)):
            fy = 92
            base = sk if not flip else skd
            sg = 1 if not flip else -1
            poly([(fx - 7, fy + 12), (fx + 7, fy + 12), (fx + 9, H), (fx - 9, H)], tb if not flip else td, edge_k=.45)           # puño de la manga
            P.rect(fx - 7, fy + 13, fx + 7, fy + 14, tl if not flip else tb)
            poly([(fx - 9, fy + 3), (fx - 7, fy - 2), (fx - 1, fy - 5), (fx + 6, fy - 4), (fx + 9, fy + 1), (fx + 9, fy + 6), (fx + 6, fy + 12), (fx - 5, fy + 13), (fx - 9, fy + 9)], base, edge_k=.45)   # masa del puño
            for k, wdt in enumerate((14, 14, 11)):                                                                                 # pliegues de los dedos (horizontales)
                P.rect(fx - 8 + (0 if not flip else 2), fy + 1 + k * 3, fx - 8 + wdt - (0 if not flip else 2) + (0 if not flip else 0), fy + 1 + k * 3, skdd)
            poly([(fx - sg * 6, fy - 3), (fx + sg * 3, fy - 5), (fx + sg * 5, fy - 1), (fx - sg * 1, fy + 1), (fx - sg * 6, fy)], shade(sk, 1.05), edge_k=.45)   # pulgar cruzando por arriba

    P = PH                                                                           # a partir de aquí: capa de la cabeza
    # ------------------------------------------------ cabeza: cráneo + mandíbula en V (3/4)
    jr, jh = (21, 20) if CS['strong'] else (20, 19)                                    # radio y alto de la mandíbula
    jaw = [(cx + (fc - cx) * .6 * math.sin(math.radians(t)) + jr * (1 - .22 * math.sin(math.radians(t)) ** 3) * math.cos(math.radians(t)), 47 + jh * math.sin(math.radians(t))) for t in np.linspace(0, 180, 21)]
    FP = [(28, 38), (30, 28), (37, 20), (48, 17), (59, 20), (66, 28), (68, 38)] + jaw + [(28, 38)]
    for ex in (27, 67):                                                                # orejas
        P.add(lambda d, ex=ex: d.ellipse([ex - 2, 42, ex + 4, 52], fill=255), sk if ex < 48 else skd, sh=False, hi=False, edge_k=.5)
    fm = poly(FP, sk, sh=False, hi=False, edge_k=.42)
    def face_fill(pts, col):
        P.a[P.mask(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255)) & fm] = (*col, 255)
    edge_r = fm & ~np.roll(fm, -4, axis=1)                                                  # borde derecho (4 px)
    edge_b = fm & ~np.roll(fm, -3, axis=0) & (xx > fc)                                      # borde inferior derecho (3 px)
    P.a[edge_r | edge_b] = (*skd, 255)                                                      # sombra suave en el contorno
    face_fill([(32, 36), (37, 30), (40, 33), (35, 42)], skl)                                                                         # luz en la frente/sien
    if style in ('tab', 'you'):                                                                                                      # rubor
        P.rect(31, 53, 36, 54, (244, 160, 156)); P.rect(32, 55, 35, 55, (244, 160, 156)); P.rect(59, 53, 64, 54, (236, 150, 146))
    if CS['stubble']:
        stub = tuple(int(a * .8 + b * .2) for a, b in zip(sk, hc['b']))
        face_fill([(32, 56), (38, 62), (44, 64), (fc + 1, 65), (54, 64), (60, 60), (64, 54), (60, 53), (54, 58), (44, 60), (36, 56)], stub)

    # ------------------------------------------------ ojos de la hoja de referencia (+cejas), a escala con la cara
    closed = blink or expr == 'smile'
    ep = {'K': (40, 44, 58), 'w': tuple(int(v * .5 + w * .5) for v, w in zip(sk, (sk[0] * .9, sk[1] * .7, sk[2] * .71))), 'W': (252, 250, 248),
          'H': (255, 240, 222), 'E': tuple(min(255, int(v * 1.25 + 10)) for v in CS['iris'])}
    mood = 'sleepy' if CS['sleepy'] else {'sad': 'sad', 'worry': 'sad', 'wow': 'flat'}.get(expr, 'n')
    kind = EYE_KIND if EYE_KIND else ('f' if style == 'tab' else 'm')
    left, right = EYES[kind + '_' + {'sleepy': 'sleepy', 'sad': 'sad', 'flat': 'flat'}.get(mood, 'n' if kind == 'm' else EYE_F)]
    def fit(rows, target_w=11.0):                    # reescala por filas/columnas repetidas (mantiene el píxel nítido)
        f = max(.85, min(1.25, target_w / len(rows[0])))
        nh, nw = int(round(len(rows) * f)), int(round(len(rows[0]) * f))
        return [''.join(rows[min(len(rows) - 1, int(r / f))][min(len(rows[0]) - 1, int(c / f))] for c in range(nw)) for r in range(nh)]
    left, right = fit(left), fit(right)
    def stamp(rows, x0, y0, pal):
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch != '.' and ch in pal: P.a[y0 + r, x0 + c] = (*pal[ch], 255)
    ey = 39
    if closed:                                                                                       # ojos cerrados: arcos "^" (sonrisa)
        for xs in ((fc - 15, fc - 4), (fc + 4, fc + 15)):
            for k in (0, 1):
                P.line([(xs[0], ey + 8 + k), (xs[0] + 2, ey + 6 + k), (xs[0] + 5, ey + 5 + k), (xs[1] - 2, ey + 6 + k), (xs[1], ey + 8 + k)], (40, 44, 58))
    else:
        stamp(left, fc - 4 - len(left[0]), ey, ep); stamp(right, fc + 4, ey, ep)
    if style == 'tab' and not closed and kind == 'm':                                                                                  # pestañas exteriores (solo con ojos 'm')
        for (x, y) in [(fc - 4 - len(left[0]) - 1, ey + 6), (fc - 4 - len(left[0]) - 2, ey + 5), (fc + 4 + len(right[0]), ey + 6), (fc + 4 + len(right[0]) + 1, ey + 5)]:
            P.px(x, y, (40, 44, 58))
    # nariz y boca mínimos
    P.rect(fc, 50, fc, 52, skdd); P.rect(fc - 1, 53, fc + 1, 53, skdd)
    lip, mouth_dark = (170, 78, 88), (120, 44, 56)
    my = 58
    if expr == 'smile':
        P.rect(fc - 5, my, fc + 5, my, lip); P.rect(fc - 4, my + 1, fc + 4, my + 1, mouth_dark); P.rect(fc - 3, my + 1, fc + 3, my + 1, (250, 248, 248)); P.px(fc - 6, my - 1, lip); P.px(fc + 6, my - 1, lip)
    elif expr == 'wow':
        P.add(lambda d: d.ellipse([fc - 3, my - 2, fc + 3, my + 4], fill=255), mouth_dark, sh=False, hi=False, edge=False)
    elif expr in ('sad', 'worry'):
        P.rect(fc - 4, my + 1, fc + 3, my + 1, lip); P.px(fc - 5, my + 2, lip); P.px(fc + 4, my + 2, lip)
    else:
        P.rect(fc - 4, my, fc + 3, my, lip); P.px(fc - 5, my + 1, shade(lip, .85)); P.px(fc + 4, my - 1, shade(lip, .85))
    # gafas siguiendo a los ojos
    if CS['glasses']:
        g = (34, 30, 48)
        for x0 in (fc - 4 - len(left[0]) - 2, fc + 2):
            P.add(lambda d, x0=x0: d.rounded_rectangle([x0, ey + 3, x0 + 14, ey + 16], radius=3, outline=255, width=2), g, edge=False, sh=False, hi=False)
            P.rect(x0 + 2, ey + 13, x0 + 4, ey + 13, (210, 232, 255))
        P.rect(fc - 4, ey + 9, fc + 3, ey + 10, g)

    # ------------------------------------------------ pelo desde el cráneo (alineado): base + sombra + reflejo + mechones
    hp = hair_polygon(style)
    hm = poly(hp, hc['b'], edge_k=.4)
    sx0, sy0, srx, sry = SKULL
    for ang, ln, slant in STYLES[style].get('spikes', []):
        pa = pts_ellipse(sx0, sy0, srx, sry, ang - 9, ang + 9, 3)
        tip = pts_ellipse(sx0, sy0, srx + ln, sry + ln, ang + 5 * slant, ang + 5 * slant, 1)[0]
        poly([pa[0], tip, pa[-1]], hc['b'], edge_k=.4)
    hm = P.mask(lambda d: None) | hm
    cx_, cy_, rx_, ry_ = SKULL
    P.a[hm & (xx > cx + 7)] = (*hc['d'], 255)                                                 # lado en sombra
    rr = ((xx - cx_) / (rx_ + 1.0)) ** 2 + ((yy - cy_) / (ry_ + 1.0)) ** 2
    P.a[hm & (rr > .52) & (rr < .72) & (yy < 31) & (xx < cx + 6)] = (*hc['l'], 255)         # banda de reflejo
    st = STYLES[style]
    for dx in (-15, -8, -1, 6, 13, 18):                                                       # mechones desde la coronilla
        y1 = int(fringe_y(st['fringe'], dx)) - 1
        P.line([(cx + dx // 2, 19), (cx + dx, y1)], hc['dd'])
    if st.get('tuft'):                                                                        # ahoge
        poly([(cx - 3, 18), (cx + 2, 10), (cx + 6, 19)], hc['b'], edge_k=.4)
    if style == 'tab':                                                                        # mechones largos laterales
        P.line([(27, 40), (25, 80)], hc['dd']); P.line([(69, 40), (71, 80)], hc['dd'])

    # ------------------------------------------------ puños (como los retratos de referencia)
    body = PB.final(); head = PH.final()
    body.alpha_composite(head.crop((0, 0, W + 2, H + 2 - DY)), (0, DY))
    return body


def portrait4(who='you', expr='n', look=(0, 0), blink=False, sc=None, outfit=None, cap=False, gesture='fists'):
    return build(who, expr, blink, outfit, gesture)


if __name__ == '__main__':
    Z = 5
    cfg = [('stallone', 'n', 'grey'), ('you', 'n', None), ('tab', 'n', None), ('king', 'n', None), ('you', 'sad', None), ('tab', 'smile', None)]
    sheet = Image.new('RGBA', (len(cfg) * (W * Z + 16), H * Z), (52, 110, 112, 255))
    for i, (n, e, o) in enumerate(cfg):
        p = build(n, e, False, o)
        sheet.alpha_composite(p.resize((p.width * Z, p.height * Z), Image.NEAREST), (i * (W * Z + 16), 0))
    sheet.save('/home/user/w/tuconfia/out/portrait4_v0.png')

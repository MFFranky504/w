"""Portrait v3: pixel art a mano (plantillas ASCII) estilo retratos HGSS/BW. Lienzo 56x64, se muestra x2."""
import numpy as np
from PIL import Image, ImageDraw
from lib import shade
from cast import resolve
from chars_anime import outline

W, H = 56, 64
HX, HY = 12, 9          # esquina de la plantilla de cabeza (32 de ancho)

# contorno de la cara (columna izq, columna der) por fila de la plantilla de cabeza
CONTOUR = {**{r: (6, 25) for r in range(3, 5)}, **{r: (5, 26) for r in range(5, 15)}, 15: (6, 26), 16: (6, 25), 17: (7, 25), 18: (7, 24), 19: (8, 23),
           20: (9, 22), 21: (10, 21), 22: (11, 19), 23: (12, 17), 24: (13, 15)}

# rasgos estampados sobre la cara: (fila, columna, texto)  '.' = no tocar
EYES_OPEN = [  # ojo lejano (izq, 5 de ancho) y cercano (der, 7 de ancho)
    (10, 16, '.KKKKK.'),
    (11, 7, 'KKKKK'),   (11, 15, 'KKKKKKK'),
    (12, 7, 'WEHPE'),   (12, 15, 'WEHPPEW'),
    (13, 7, 'WePEe'),   (13, 15, 'WeEPPeW'),
    (14, 8, 'kkk'),     (14, 16, 'kkkkk'),
]
EYES_SLEEPY = [
    (11, 7, 'sssss'),   (11, 15, 'sssssss'),
    (12, 7, 'KKKKK'),   (12, 15, 'KKKKKKK'),
    (13, 7, 'WePEe'),   (13, 15, 'WeEPPeW'),
    (14, 8, 'kkk'),     (14, 16, 'kkkkk'),
]
EYES_CLOSED = [(12, 7, '.KKK.'), (13, 7, 'K...K'), (12, 16, '.KKKK.'), (13, 15, 'K.....K')]
BROWS = {'n': [(8, 6, 'KKK'), (9, 9, 'KK'), (8, 18, 'KKKK'), (9, 15, 'KKK')],
         'sad': [(9, 6, 'KK'), (8, 8, 'KKK'), (9, 19, 'KKK'), (8, 15, 'KKKK')]}
NOSE = [(15, 13, 's'), (16, 12, 'tt')]
MOUTHS = {'n': [(19, 12, 'MMM'), (20, 15, 'm')], 'smile': [(19, 11, 'MmmM'), (20, 12, 'MM')], 'sad': [(19, 12, 'mMMm')]}

# pelo frontal (36 de ancho, se coloca en x = HX-2)
HAIR = {
 'you': """
...........AA....A..................
.........AAAAA..AAA..A..............
.......AAABBBAAAAAAAAAA.............
.....AAABBBBAAAAAAAAAAAaa...........
....AAABBBAAAAAAAAAAAAAaaa..........
...AAAAAAAAAAAAAAAAAAAAAaaa.........
...AAAAAAAAAAAAAAAAAAAAAAaaa........
..AAAAAaAAAAAAaAAAAAAAAAAaaa........
..AAAAa.AAAAAa.AAAAA.aAAAAaa........
..AAAa..AAAA...AAAA...aAAAaa........
..AAa...AAa.....AA.....aAAa.........
..AA.....a.......a......AAa.........
..AA....................Aa..........
..Aa....................Aa..........
..A......................a..........
..a.................................
""",
 'shag': """
.........AAAAAAAAAA.................
.......AAABBBBAAAAAAA...............
......AABBBBBAAAAAAAAAa.............
.....AABBBAAAAAAAAAAAAAa............
....AAAAAAAAAAAAAAAAAAAAa...........
....AAAAAAAAAAAAAAAAAAAAAa..........
...AAAAAAAAAAAAAAAAAAAAAAa..........
...AAAAAaaaAAAAAAAAAAAAAAAa.........
...AAAAa...aaAAAAAAAAAAAAAa.........
...AAAa.......aaAAAAAAAAAAa.........
...AAa...........aaaAAAAAAa.........
...AAa...............aAAAAa.........
...AA..................aAAa.........
...AA...................AAa.........
...Aa...................Aa..........
...Aa...................Aa..........
....a....................a..........
""",
 'tab': """
.........AAAAAAAAA..................
.......AAABBBBAAAAAA................
......AABBBBAAAAAAAAAa..............
.....AABBAAAAAAAAAAAAAa.............
....AAAAAAAAAAAAAAAAAAAa............
...AAAAAAAAAAAAAAAAAAAAAa...........
...AAAAAAAAAAAAAAAAAAAAAAa..........
...AAAAaAAAAAaAAAAAaAAAAAa..........
..AAAAa.aAAAa.aAAAa.aAAAAAa.........
..AAAa...aAa...aAa...aAAAAa.........
..AAAa....a.....a.....aAAAa.........
..AAA..................AAAa.........
..AAA..................AAAa.........
..AAa..................aAAa.........
..AAa...................AAa.........
..AAa...................AAa.........
..AAa...................aAa.........
..AA.....................Aa.........
..AA.....................Aa.........
..Aa.....................aa.........
""",
}
BACK_TAB = [(14, 8), (8, 18), (6, 40), (10, 50), (20, 46), (38, 46), (46, 50), (48, 38), (45, 16), (38, 8)]   # pelo largo por detrás (coords de lienzo)

TOPS = {'hoodie': ((80, 96, 206), (54, 64, 152), (126, 146, 238)), 'grey': ((158, 162, 174), (112, 116, 132), (210, 214, 224)),
        'cardigan': ((230, 176, 72), (184, 130, 44), (250, 210, 120)), 'plaid': ((204, 70, 62), (150, 40, 44), (238, 118, 100)),
        'tux': ((32, 32, 44), (18, 18, 28), (84, 84, 106))}


def ramp_skin(sk):
    r, g, b = sk
    return dict(S=sk, s=(int(r * .88), int(g * .74), int(b * .76)), t=(int(r * .72), int(g * .55), int(b * .6)),
                L=(min(255, int(r * 1.03 + 6)), min(255, int(g * 1.04 + 6)), min(255, int(b * 1.04 + 4))))


def stamp(a, items, x0, y0, pal):
    for r, c, txt in items:
        for i, ch in enumerate(txt):
            if ch != '.' and ch in pal: a[y0 + r, x0 + c + i] = (*pal[ch], 255)


def portrait3(who='you', expr='n', blink=False, outfit=None):
    CS = resolve(who); style = CS['style']; outfit = outfit or CS['outfit']
    sk = ramp_skin(CS['skin']); hc = CS['hair']
    iris = CS['iris']
    pal = {**sk, 'K': (34, 24, 40), 'k': shade(CS['skin'], .58), 'W': (250, 248, 252), 'E': shade(iris, .7),
           'e': tuple(min(255, int(v * 1.7 + 40)) for v in iris), 'P': (20, 14, 28), 'H': (255, 255, 255),
           'M': (150, 62, 74), 'm': (196, 110, 112), 'A': hc['b'], 'a': hc['d'], 'B': hc['l'], 'b': hc['dd']}
    tb, td, tl = TOPS.get(outfit, TOPS['hoodie'])
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    # pelo trasero (largo)
    if style == 'tab':
        bk = Image.new('RGBA', (W, H)); ImageDraw.Draw(bk).polygon(BACK_TAB, fill=(*hc['d'], 255))
        out.alpha_composite(outline(bk, shade(hc['dd'], .6)).crop((1, 1, W + 1, H + 1)))
    # cuerpo: hombros caídos + cuello de la ropa
    body = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(body)
    d.polygon([(15, 42), (23, 38), (34, 38), (42, 42), (52, 49), (55, 63), (0, 63), (3, 49)], fill=(*tb, 255))
    d.polygon([(38, 43), (42, 44), (52, 51), (55, 63), (42, 63), (41, 52)], fill=(*td, 255))          # sombra derecha
    d.polygon([(3, 51), (15, 44), (17, 45), (7, 53), (4, 63), (0, 63)], fill=(*tl, 255))             # luz izquierda
    if outfit == 'hoodie':
        d.polygon([(16, 43), (22, 38), (35, 38), (41, 43), (34, 47), (23, 47)], fill=(*td, 255))
        d.line([(25, 47), (24, 56)], fill=(246, 246, 252, 255)); d.line([(32, 47), (33, 55)], fill=(246, 246, 252, 255))
    elif outfit == 'grey':
        d.polygon([(21, 41), (36, 41), (34, 45), (23, 45)], fill=(*td, 255))
        for x in (25, 28, 31): d.line([(x, 47), (x, 50)], fill=(*td, 255))
    elif outfit == 'cardigan':
        d.polygon([(22, 41), (35, 41), (28, 52)], fill=(252, 242, 226, 255)); d.line([(28, 52), (28, 63)], fill=(*td, 255))
    out.alpha_composite(outline(body, shade(td, .5)).crop((1, 1, W + 1, H + 1)))
    # cara (silueta por contorno) + cuello
    face = np.zeros((H, W, 4), np.uint8)
    for y in range(33, 41):                                                   # cuello
        for x in range(HX + 12, HX + 18): face[y, x] = (*sk['s'], 255)
    for y in range(33, 35):
        for x in range(HX + 12, HX + 18): face[y, x] = (*sk['t'], 255)       # sombra bajo la barbilla
    for r, (xl, xr) in CONTOUR.items():
        for c in range(xl, xr + 1):
            face[HY + r, HX + c] = (*sk['S'], 255)
            if c >= xr - 3 and 4 <= r <= 23: face[HY + r, HX + c] = (*sk['s'], 255)     # cel: lado en sombra
    if style != 'tab':                                                          # oreja pequeña (lado derecho)
        for r in range(12, 17): face[HY + r, HX + 27] = (*sk['s'], 255)
        face[HY + 14, HX + 27] = (*sk['t'], 255)
    for r in range(5, 12): face[HY + r, HX + 7] = (*sk['L'], 255); face[HY + r, HX + 8] = (*sk['L'], 255)    # luz frente
    for r in range(16, 19): face[HY + r, HX + 8] = (*sk['L'], 255)                                              # luz pómulo
    if CS.get('stubble'):
        for r in range(18, 25):
            xl, xr = CONTOUR[r]
            for c in range(xl, xr + 1):
                if (c * 3 + r * 2) % 5 == 0 and face[HY + r, HX + c, 3]: face[HY + r, HX + c] = (*sk['s'], 255)
    # rasgos
    eyes = EYES_CLOSED if (blink or expr == 'smile') else (EYES_SLEEPY if CS.get('sleepy') else EYES_OPEN)
    stamp(face, eyes, HX, HY, pal)
    stamp(face, BROWS['sad' if expr in ('sad', 'worry') else 'n'], HX, HY, {'K': hc['dd']})
    stamp(face, NOSE, HX, HY, pal)
    stamp(face, MOUTHS.get(expr, MOUTHS['n']), HX, HY, pal)
    if style == 'tab' and not (blink or expr == 'smile'):
        stamp(face, [(10, 22, 'K'), (11, 22, 'K'), (10, 6, 'K')], HX, HY, pal)                  # pestaña exterior
    if style in ('tab', 'you'):
        stamp(face, [(16, 6, 'mm'), (16, 19, 'mm')], HX, HY, {'m': (240, 150, 150)})                # rubor
    fimg = Image.fromarray(face, 'RGBA')
    out.alpha_composite(outline(fimg, shade(CS['skin'], .45)).crop((1, 1, W + 1, H + 1)))
    # pelo frontal
    rows = [r for r in HAIR[style].strip('\n').split('\n')]
    hair = np.zeros((H, W, 4), np.uint8)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in pal and ch in 'AaBb':
                x, y = HX - 2 + c, HY + r - 3
                if 0 <= x < W and 0 <= y < H: hair[y, x] = (*pal[ch], 255)
    out.alpha_composite(outline(Image.fromarray(hair, 'RGBA'), shade(hc['dd'], .6)).crop((1, 1, W + 1, H + 1)))
    return out


if __name__ == '__main__':
    Z = 6
    names = [('stallone', 'n'), ('you', 'n'), ('tab', 'n'), ('tab', 'smile')]
    sheet = Image.new('RGBA', (len(names) * (W * Z + 20), H * Z), (52, 110, 112, 255))
    for i, (n, e) in enumerate(names):
        p = portrait3(n, e)
        sheet.alpha_composite(p.resize((W * Z, H * Z), Image.NEAREST), (i * (W * Z + 20), 0))
    sheet.save('/home/user/w/tuconfia/out/portrait3_v0.png')

"""Sprite de batalla v2: figura articulada (cintura, cadera, muslo/rodilla/pantorrilla, codos, manos), pose contrapposto."""
import math
import numpy as np
from PIL import Image, ImageDraw
from lib import shade
from sprites import Paint, SKIN, BLUSH
from cast import resolve
import rasgos as RG

def limb(d, p0, p1, r0, r1):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    d.polygon([(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1), (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)], fill=255)
    d.ellipse([x0 - r0, y0 - r0, x0 + r0, y0 + r0], fill=255); d.ellipse([x1 - r1, y1 - r1, x1 + r1, y1 + r1], fill=255)

def chain(d, pts, rs):
    for i in range(len(pts) - 1): limb(d, pts[i], pts[i + 1], rs[i], rs[i + 1])

OUTF = {
 'plaid':   dict(top=(210, 72, 64), top2=(152, 44, 52), under=(250, 248, 244), pants=(70, 106, 176), shoes=(104, 66, 48), sole=(236, 226, 204)),
 'teacher': dict(top=(238, 234, 220), top2=None, under=(252, 252, 250), pants=(128, 104, 80), shoes=(84, 58, 46), sole=(60, 44, 36)),
 'cardigan':dict(top=(236, 182, 76), top2=(190, 134, 48), under=(252, 242, 226), pants=(84, 112, 160), shoes=(116, 70, 54), sole=(236, 226, 204)),
 'uniform': dict(top=(248, 126, 166), top2=(208, 86, 128), under=(255, 255, 255), pants=(252, 252, 254), shoes=(206, 206, 216), sole=(150, 150, 164)),
 'argentina': dict(top=(150, 206, 246), top2=(252, 252, 255), under=(252, 252, 255), pants=(30, 30, 40), shoes=(40, 40, 52), sole=(220, 220, 230), shorts=True, socks=(250, 250, 255)),
 'tee_blue': dict(top=(70, 130, 220), top2=(40, 86, 170), under=(250, 250, 250), pants=(60, 70, 100), shoes=(60, 50, 56), sole=(230, 230, 230)),
 'tee_green': dict(top=(80, 190, 110), top2=(40, 140, 76), under=(250, 250, 250), pants=(70, 76, 110), shoes=(100, 70, 50), sole=(230, 230, 230)),
 'tee_yellow': dict(top=(250, 210, 70), top2=(206, 160, 30), under=(250, 250, 250), pants=(76, 86, 130), shoes=(70, 56, 56), sole=(230, 230, 230)),
 'tee_red': dict(top=(230, 80, 70), top2=(170, 44, 48), under=(250, 250, 250), pants=(60, 74, 110), shoes=(90, 66, 52), sole=(230, 230, 230)),
 'blazer': dict(top=(52, 70, 120), top2=(34, 46, 86), under=(250, 250, 250), pants=(70, 70, 82), shoes=(60, 44, 40), sole=(40, 30, 28)),
 'polo': dict(top=(210, 150, 80), top2=(160, 104, 50), under=(250, 240, 220), pants=(80, 84, 100), shoes=(70, 52, 44), sole=(40, 30, 28)),
 'coat': dict(top=(246, 248, 252), top2=(196, 206, 224), under=(190, 214, 240), pants=(70, 90, 130), shoes=(60, 50, 50), sole=(40, 30, 28)),
 'tux': dict(top=(32, 32, 44), top2=(18, 18, 28), under=(250, 250, 252), pants=(32, 32, 44), shoes=(16, 16, 22), sole=(10, 10, 14)),
 'suit85': dict(top=(44, 46, 62), top2=(26, 28, 42), under=(250, 250, 252), pants=(44, 46, 62), shoes=(20, 20, 26), sole=(10, 10, 14)),
 'turtle': dict(top=(30, 30, 38), top2=(16, 16, 22), under=(30, 30, 38), pants=(70, 104, 168), shoes=(228, 228, 234), sole=(150, 150, 162)),
 'grey': dict(top=(156, 160, 172), top2=(112, 116, 132), under=(206, 210, 220), pants=(70, 78, 110), shoes=(110, 70, 52), sole=(236, 226, 204)),
 'peladito': dict(top=(234, 226, 200), top2=(200, 190, 160), under=(234, 226, 200), pants=(122, 98, 72), shoes=(70, 52, 40), sole=(40, 30, 26)),
 'vest': dict(top=(246, 244, 236), top2=(210, 206, 196), under=(246, 244, 236), pants=(40, 38, 46), shoes=(24, 20, 22), sole=(10, 10, 12)),
 'rebozo': dict(top=(244, 238, 226), top2=(206, 198, 184), under=(244, 238, 226), pants=(60, 90, 150), shoes=(70, 46, 40), sole=(40, 30, 26)),
 'zarape': dict(top=(232, 224, 206), top2=(196, 186, 166), under=(232, 224, 206), pants=(236, 230, 214), shoes=(150, 104, 64), sole=(90, 60, 40)),
 'kungfu': dict(top=(34, 34, 40), top2=(18, 18, 24), under=(34, 34, 40), pants=(30, 30, 36), shoes=(22, 22, 26), sole=(200, 196, 186)),
 'opera': dict(top=(244, 240, 228), top2=(200, 194, 178), under=(244, 240, 228), pants=(30, 30, 38), shoes=(24, 24, 30), sole=(200, 196, 186)),
 'hoodie':  dict(top=(86, 102, 212), top2=(56, 68, 156), under=(246, 246, 252), pants=(52, 58, 106), shoes=(248, 248, 252), sole=(150, 150, 172)),
}
HAIRC = {'king': dict(b=(52, 50, 78), d=(32, 30, 54), l=(110, 120, 176)),
         'tab': dict(b=(150, 88, 54), d=(112, 62, 40), l=(214, 150, 92)),
         'you': dict(b=(72, 86, 160), d=(48, 58, 118), l=(130, 160, 232))}


def battle2(who='king', pose='hold', outfit=None, W=84, H=124):
    P = Paint(W, H)
    cx = W // 2
    CS = resolve(who); style = CS['style']
    outfit = outfit or CS['outfit']
    o = OUTF[outfit]
    sk = CS['skin']; skd = shade(sk, .84); skdd = shade(sk, .68)
    hc = CS['hair']
    fem = style == 'tab'
    lf = .78 if CS['kid'] else RG.HEIGHT[CS.get('height', 'average')]       # piernas: más cortas que antes (la cabeza gana peso) y según la altura
    bs, bw, bt = RG.BUILD[CS.get('build', 'average')]                     # complexión: hombros, cintura, grosor de extremidades
    sh_w, wa_w, hp_w = (9.5 * bs, 6.0 * bw, 8.6 * bw) if fem else (11.0 * bs, 7.4 * bw, 8.6 * max(1, bw * .95))
    T = 1.12 * bt                                                         # extremidades algo más gruesas que antes
    top, pants, shoes = o['top'], o['pants'], o['shoes']
    # ---------------- esqueleto
    hipL, hipR = (cx - 4.5, 66), (cx + 4.5, 68)
    ky = lambda y: 68 + (y - 68) * lf
    kneeL, ankL = (cx - 6, ky(89)), (cx - 7.5, ky(110))
    kneeR, ankR = (cx + 8.5, ky(88)), (cx + 13, ky(110))
    GY = int(ankL[1])
    shL, shR = (cx - sh_w, 31), (cx + sh_w, 30)
    if pose in ('toss', 'trophy'):
        elbR, hndR = (cx + 17, 24), (cx + 15, 10)
    elif pose == 'box':
        elbR, hndR = (cx + 13, 52), (cx + 6, 52)
    elif pose == 'hold':
        elbR, hndR = (cx + 15, 50), (cx + 8, 43)
    elif pose == 'hip':
        elbR, hndR = (cx + 17, 52), (cx + 11, 62)
    else:
        elbR, hndR = (cx + 15, 51), (cx + 17, 67)
    elbL, hndL = (cx - 14.5, 51), (cx - 14, 68)
    if pose == 'box': elbL, hndL = (cx - 13, 52), (cx - 6, 52)
    # ---------------- pierna lejana (derecha del dibujo) y cercana
    lerp = lambda a, c, t: (a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
    if o.get('shorts'):
        for hp, kn, an in ((hipR, kneeR, ankR), (hipL, kneeL, ankL)):
            P.add(lambda d, hp=hp, kn=kn, an=an: chain(d, [hp, kn, an], [6.0 * T, 4.4 * T, 3.2 * T]), sk, edge_k=.45)
            P.add(lambda d, kn=kn, an=an: limb(d, lerp(kn, an, .3), (an[0], an[1] - 1), 4.2, 3.5), o['socks'], edge_k=.5)
            P.add(lambda d, hp=hp, kn=kn: limb(d, hp, lerp(hp, kn, .72), 7.0 * T, 6.4 * T), pants, edge_k=.42)
    else:
        P.add(lambda d: chain(d, [hipR, kneeR, ankR], [6.2 * T, 4.6 * T, 3.4 * T]), pants, edge_k=.42)
        P.add(lambda d: chain(d, [hipL, kneeL, ankL], [6.4 * T, 4.8 * T, 3.5 * T]), pants, edge_k=.42)
    if outfit == 'plaid' or outfit == 'cardigan':   # costura / pliegue en la rodilla
        P.line([(int(kneeL[0]) - 1, int(kneeL[1]) - 4), (int(kneeL[0]) - 2, int(kneeL[1]) + 3)], shade(pants, .75))
    # ---------------- zapatos angulados
    sh_hi = shade(shoes, 1.2)
    P.add(lambda d: d.polygon([(ankL[0] - 5, GY - 2), (ankL[0] + 3, GY - 2), (ankL[0] + 4, GY + 2), (ankL[0] - 10, GY + 4), (ankL[0] - 10, GY + 1)], fill=255), shoes, edge_k=.4)
    P.add(lambda d: d.polygon([(ankR[0] - 3, GY - 2), (ankR[0] + 5, GY - 2), (ankR[0] + 12, GY + 1), (ankR[0] + 12, GY + 4), (ankR[0] - 4, GY + 3)], fill=255), shoes, edge_k=.4)
    P.rect(int(ankL[0]) - 10, GY + 4, int(ankL[0]) + 4, GY + 4, o['sole']); P.rect(int(ankR[0]) - 4, GY + 4, int(ankR[0]) + 12, GY + 4, o['sole'])
    if outfit == 'hoodie':
        P.rect(int(ankL[0]) - 8, GY + 1, int(ankL[0]) + 2, GY + 1, (214, 60, 70)); P.rect(int(ankR[0]) - 2, GY + 1, int(ankR[0]) + 9, GY + 1, (214, 60, 70))
    # ---------------- brazo trasero (izquierda del dibujo) se dibuja antes del torso
    P.add(lambda d: chain(d, [shL, elbL], [3.6 * T, 3.1 * T]), top, edge_k=.42)
    P.add(lambda d: chain(d, [elbL, (hndL[0], hndL[1] - 3)], [3.1 * T, 2.8 * T]), top, edge_k=.42)
    P.add(lambda d: d.ellipse([hndL[0] - 3.5, hndL[1] - 4.5, hndL[0] + 3.5, hndL[1] + 3.5], fill=255), sk, edge_k=.45)
    P.rect(int(hndL[0]) - 1, int(hndL[1]) + 2, int(hndL[0]) + 1, int(hndL[1]) + 4, sk)
    # ---------------- pelo trasero (Tabitha) y volúmenes especiales
    RG.back_b(P, CS, cx, hc)
    if fem and CS.get('hair2') is None:
        P.add(lambda d: d.polygon([(cx - 11, 14), (cx - 12, 8), (cx - 6, 3), (cx + 6, 3), (cx + 12, 8), (cx + 11, 14), (cx + 12, 36), (cx + 9, 52), (cx + 4, 50), (cx - 4, 50), (cx - 9, 52), (cx - 12, 36)], fill=255), hc['d'], edge_k=.4)
    # ---------------- torso con cintura
    def torso(d):
        d.polygon([(cx - sh_w, 30), (cx + sh_w, 29), (cx + sh_w + .5, 34), (cx + sh_w - 1.5, 46), (cx + wa_w, 57), (cx + hp_w, 67), (cx + hp_w + .5, 71), (cx - hp_w - .5, 71), (cx - hp_w, 67), (cx - wa_w, 57), (cx - sh_w + 1.5, 46), (cx - sh_w - .5, 34)], fill=255)
    tm = P.add(torso, top, edge_k=.42)
    def clip_lines(lines, col):
        im = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(im)
        for l in lines: dd.line(l, fill=255)
        m = (np.array(im) > 0) & tm
        P.a[m] = (*col, 255)
    if outfit == 'plaid':
        clip_lines([[(cx - 14, y), (cx + 14, y + 1)] for y in range(36, 70, 6)] + [[(x, 31), (x - 1, 71)] for x in range(cx - 11, cx + 12, 6)], o['top2'])
        P.add(lambda d: d.polygon([(cx - 3, 30), (cx + 3, 30), (cx + 3.5, 46), (cx + 2, 57), (cx + 3, 71), (cx - 3, 71), (cx - 2, 57), (cx - 3.5, 46)], fill=255), o['under'], edge_k=.65)
        P.line([(cx - 8, 30), (cx - 3, 37)], o['under']); P.rect(cx - 9, 70, cx + 9, 71, o['top2'])
    elif outfit in ('tux', 'suit85'):
        P.add(lambda d: d.polygon([(cx - 4, 30), (cx + 4, 30), (cx + 2, 56), (cx - 2, 56)], fill=255), (250, 250, 252), edge_k=.6)
        P.line([(cx - 9, 30), (cx - 2, 46)], o['top2']); P.line([(cx + 9, 30), (cx + 2, 46)], o['top2']); P.rect(cx - 3, 32, cx + 3, 34, (180, 30, 50) if outfit == 'tux' else (22, 26, 60))
    elif outfit == 'grey':
        P.rect(cx - 5, 30, cx + 5, 31, o['top2']); P.add(lambda d: d.polygon([(cx - 8, 56), (cx + 8, 56), (cx + 9.5, 67), (cx - 9.5, 67)], fill=255), o['top2'], edge_k=.55)
    elif outfit == 'argentina':
        clip_lines([[(x, 29), (x, 71)] for x in range(cx - 12, cx + 13, 5)] + [[(x + 1, 29), (x + 1, 71)] for x in range(cx - 12, cx + 13, 5)], (252, 252, 255))
        P.rect(cx - 3, 30, cx + 3, 30, (250, 250, 255))
    elif outfit == 'blazer':
        P.add(lambda d: d.polygon([(cx - 4, 30), (cx + 4, 30), (cx + 2, 56), (cx - 2, 56)], fill=255), (250, 250, 250), edge_k=.6)
        P.line([(cx - 9, 30), (cx - 2, 46)], o['top2']); P.line([(cx + 9, 30), (cx + 2, 46)], o['top2'])
    elif outfit == 'coat':
        P.line([(cx, 30), (cx, 71)], o['top2']); P.rect(cx + 4, 44, cx + 8, 47, (190, 214, 240)); P.rect(cx - 9, 70, cx + 9, 71, o['top2'])
    elif outfit == 'polo':
        P.add(lambda d: d.polygon([(cx - 5, 30), (cx + 5, 30), (cx, 38)], fill=255), (250, 240, 220), sh=False, edge_k=.55)
    elif outfit.startswith('tee'):
        P.rect(cx - 8, 56, cx + 8, 56, o['top2'])
    elif outfit == 'teacher':
        P.add(lambda d: d.polygon([(cx - 2.5, 34), (cx + 2.5, 34), (cx + 3, 54), (cx, 58), (cx - 3, 54)], fill=255), (56, 94, 170), edge_k=.5)
        P.line([(cx - 8, 30), (cx, 36), (cx + 8, 30)], o['under'])
    elif outfit == 'cardigan':
        P.add(lambda d: d.polygon([(cx - 6, 30), (cx + 6, 30), (cx + 1, 50), (cx - 1, 50)], fill=255), o['under'], sh=False, edge_k=.55)
        P.line([(cx - 7, 30), (cx - 1, 56), (cx - 1, 70)], o['top2']); P.line([(cx + 7, 30), (cx + 1, 56), (cx + 1, 70)], o['top2'])
        for y in (58, 63): P.px(cx + 3, y, (124, 82, 34))
        P.rect(cx - 8, 69, cx + 8, 70, o['top2'])
    elif outfit == 'uniform':
        P.add(lambda d: d.polygon([(cx - 7, 30), (cx + 7, 30), (cx, 38)], fill=255), (255, 255, 255), sh=False, edge_k=.55)
        P.add(lambda d: d.polygon([(cx - wa_w - .5, 55), (cx + wa_w + .5, 55), (cx + hp_w + 3, 79), (cx - hp_w - 3, 79)], fill=255), (255, 178, 114), edge_k=.5)
        P.rect(cx + 2, 40, cx + 6, 43, (255, 255, 255)); P.rect(cx + 3, 42, cx + 5, 42, o['top2'])
    elif outfit in ('turtle', 'suit85', 'peladito', 'vest', 'rebozo', 'zarape'):
        pass                                               # sin detalles extra (jersey liso / traje)
    elif outfit in ('kungfu', 'opera'):                   # chaqueta china: cuello mao, botones de lazo y fajín
        P.add(lambda d: d.rounded_rectangle([cx - 5, 26, cx + 5, 31], radius=2, fill=255), o['top2'], edge_k=.5)
        P.rect(cx, 31, cx, 56, o['top2'])
        for yy in (36, 42, 48): P.rect(cx - 2, yy, cx + 2, yy, (210, 200, 170) if outfit == 'kungfu' else (60, 60, 70))
        P.rect(int(cx - wa_w), 56, int(cx + wa_w), 59, (150, 40, 40) if outfit == 'kungfu' else (40, 40, 52))
    else:  # hoodie
        P.rect(cx - 3, 36, cx - 3, 49, o['under']); P.rect(cx + 3, 36, cx + 3, 47, o['under'])
        P.add(lambda d: d.polygon([(cx - 8, 58), (cx + 8, 58), (cx + 9.5, 68), (cx - 9.5, 68)], fill=255), (134, 154, 244), edge_k=.5)
        P.add(lambda d: d.rounded_rectangle([cx - 9, 25, cx + 9, 32], radius=3, fill=255), o['top2'], edge_k=.5)   # capucha
        P.rect(cx - 9, 70, cx + 9, 71, o['top2'])
    # ---------------- cuello y cabeza
    P.add(lambda d: limb(d, (cx, 24), (cx, 30), 3.0, 3.4), skd, sh=False, hi=False, edge=False)
    if outfit == 'turtle': P.add(lambda d: d.rectangle([cx - 4, 24, cx + 4, 31], fill=255), o['top'], edge_k=.4)       # cuello alto
    if outfit == 'hoodie':   # auriculares
        P.add(lambda d: d.arc([cx - 10, 22, cx + 10, 40], 15, 165, fill=255, width=2), (44, 44, 58), sh=False, hi=False, edge_k=.4)
        for sx in (-1, 1):
            P.add(lambda d, sx=sx: d.ellipse([cx + sx * 10 - 3, 26, cx + sx * 10 + 3, 34], fill=255), (56, 56, 76))
            P.rect(cx + sx * 10 - 1, 28, cx + sx * 10 + 1, 32, (255, 170, 64))
    # ---------------- brazo delantero
    P.add(lambda d: chain(d, [shR, elbR], [3.6 * T, 3.1 * T]), top, edge_k=.42)
    P.add(lambda d: chain(d, [elbR, hndR], [3.1 * T, 2.7 * T]), top, edge_k=.42)
    if outfit in ('plaid', 'cardigan', 'uniform'):
        for (a, b) in ((elbL, hndL), (elbR, hndR)):
            mx, my = a[0] * .15 + b[0] * .85, a[1] * .15 + b[1] * .85
            P.add(lambda d, mx=mx, my=my: d.ellipse([mx - 3, my - 1, mx + 3, my + 1.5], fill=255), (126, 232, 196) if outfit != 'uniform' else (255, 255, 255), edge=False, sh=False, hi=False)
    P.add(lambda d: d.ellipse([hndR[0] - 3.5, hndR[1] - 4, hndR[0] + 3.5, hndR[1] + 4], fill=255), sk, edge_k=.45)
    P.rect(int(hndR[0]) - 2, int(hndR[1]) + 3, int(hndR[0]) + 1, int(hndR[1]) + 4, sk)
    # objeto
    if pose == 'hold':
        hx, hy = int(hndR[0]), int(hndR[1])
        P.add(lambda d: d.polygon([(hx - 7, hy - 12), (hx + 3, hy - 11), (hx + 4, hy + 1), (hx - 6, hy)], fill=255), (252, 250, 240), edge_k=.6)
        for i in range(3): P.rect(hx - 5, hy - 9 + i * 3, hx + 1, hy - 9 + i * 3, (130, 132, 150))
        P.add(lambda d: d.ellipse([hx - 3, hy - 2, hx + 3, hy + 3], fill=255), sk, edge_k=.45)
    if pose == 'box':                                                                    # caja de cartón sujeta con las dos manos
        P.add(lambda d: d.polygon([(cx - 13, 44), (cx + 13, 44), (cx + 14, 64), (cx - 14, 64)], fill=255), (196, 150, 98), edge_k=.5)
        P.add(lambda d: d.polygon([(cx - 13, 44), (cx + 13, 44), (cx + 11, 48), (cx - 11, 48)], fill=255), (224, 180, 124), edge=False, sh=False, hi=False)
        P.rect(cx - 2, 44, cx + 2, 56, (234, 216, 172)); P.rect(cx - 9, 54, cx - 4, 58, (250, 248, 240))
        for sx_ in (-1, 1): P.add(lambda d, sx_=sx_: d.ellipse([cx + sx_ * 13 - 3, 53, cx + sx_ * 13 + 3, 60], fill=255), sk, edge_k=.45)
    if pose == 'toss':
        P.add(lambda d: d.ellipse([int(hndR[0]) - 3, int(hndR[1]) - 11, int(hndR[0]) + 5, int(hndR[1]) - 3], fill=255), (248, 246, 238))
    # ---------------- cabeza (≈ 6.5 cabezas de alto)
    fp = [(cx - 8, 8), (cx + 8, 8), (cx + 8.6, 16), (cx + 7, 21), (cx + 4, 25), (cx, 26.5), (cx - 4, 25), (cx - 7, 21), (cx - 8.6, 16)]
    if CS['strong']: fp = [(cx - 8, 8), (cx + 8, 8), (cx + 9.4, 16), (cx + 8.8, 22), (cx + 6, 26), (cx, 27.6), (cx - 6, 26), (cx - 8.8, 22), (cx - 9.4, 16)]
    fp = RG.face_shape(fp, CS, cx, 1)
    P.add(lambda d: d.polygon(fp, fill=255), sk, sh=False, hi=False, edge_k=.42)
    if CS['stubble']:
        for yy in range(22, 28):
            for xx in range(int(cx - 9), int(cx + 10)):
                if P.a[yy, xx, 3] > 0 and tuple(P.a[yy, xx, :3]) == tuple(sk) and (abs(xx - cx) > 3 or yy > 25): P.a[yy, xx] = (*shade(sk, .86), 255)
    for ex in (cx - 11, cx + 8):
        P.add(lambda d, ex=ex: d.ellipse([ex, 15, ex + 3, 20], fill=255), sk, sh=False, hi=False, edge_k=.42)
    m = P.mask(lambda d: d.polygon([(cx + 4, 10), (cx + 8.6, 14), (cx + 7, 21), (cx + 4, 25), (cx + 2, 25.5), (cx + 5, 20), (cx + 5, 14)], fill=255))
    P.a[m & (P.a[..., 3] > 0)] = (*skd, 255)
    # ojos
    for ex in (cx - 5, cx + 3):
        P.rect(ex, 14, ex + 2, 14, (36, 26, 40))
        P.rect(ex, 15, ex + 2, 18, (255, 255, 255)); P.rect(ex + 1, 15, ex + 2, 18, CS['iris'])
        P.rect(ex + 1, 16, ex + 2, 17, (24, 18, 32)); P.px(ex + 1, 15, (255, 255, 255))
    if CS.get('eyes') == 'narrow':                     # ojos rasgados: párpado grueso y 2 filas de iris
        for ex in (cx - 5, cx + 3):
            P.rect(ex, 14, ex + 2, 18, sk); P.rect(ex - 1, 15, ex + 3, 15, (30, 22, 36))
            P.rect(ex, 16, ex + 2, 17, (40, 30, 34)); P.rect(ex + (2 if ex > cx else 0), 16, ex + (2 if ex > cx else 0), 16, (255, 255, 255))
    if CS.get('eyes') == 'small':
        for ex in (cx - 5, cx + 3): P.rect(ex, 14, ex + 2, 18, sk); P.rect(ex, 15, ex + 2, 15, (30, 22, 36)); P.rect(ex + 1, 16, ex + 1, 17, (36, 26, 30))
    if CS.get('eyes') == 'droopy':
        for ex in (cx - 5, cx + 3):
            P.rect(ex, 14, ex + 2, 15, sk); P.rect(ex - 1, 16, ex + 3, 16, (30, 22, 36)); P.px(ex + (3 if ex > cx else -1), 17, (30, 22, 36))
    if CS['sleepy']:
        for ex in (cx - 5, cx + 3): P.rect(ex, 14, ex + 2, 14, skd); P.rect(ex, 15, ex + 2, 15, (30, 22, 40))
    P.rect(cx - 6, 12, cx - 3, 12, hc['d']); P.rect(cx + 3, 12, cx + 6, 12, hc['d'])
    if CS['strong']: P.rect(cx - 6, 11, cx - 3, 11, hc['dd']); P.rect(cx + 3, 11, cx + 6, 11, hc['dd'])
    P.px(cx + 1, 21, skdd); P.rect(cx - 1, 23, cx + 1, 23, (182, 78, 90))
    if style not in ('king', 'short', 'shag'):
        P.rect(cx - 7, 20, cx - 6, 20, BLUSH); P.rect(cx + 6, 20, cx + 7, 20, BLUSH)
    if CS['glasses']:
        for ex in (cx - 7, cx + 2): P.add(lambda d, ex=ex: d.rectangle([ex, 13, ex + 5, 19], outline=255), (36, 32, 50), edge=False, sh=False, hi=False)
        P.rect(cx - 1, 16, cx + 1, 16, (36, 32, 50)); P.px(cx - 6, 18, (210, 232, 255))
    # ---------------- pelo
    RG.face_b(P, CS, cx, hc, sk)
    if RG.front_b(P, CS, cx, hc, sk): pass
    elif style == 'shag':
        P.add(lambda d: d.polygon([(cx - 11, 25), (cx - 11.6, 8), (cx - 6.5, 2), (cx, 0), (cx + 6.5, 1), (cx + 11, 6), (cx + 11.6, 25), (cx + 9, 18), (cx + 8, 11), (cx + 3, 8), (cx - 3, 9), (cx - 8, 12), (cx - 9.5, 19)], fill=255), hc['b'], edge_k=.45)
        P.line([(cx - 7, 4), (cx, 2)], hc['l']); P.line([(cx + 1, 2), (cx + 7, 5)], hc['l'])
    elif style == 'short':
        P.add(lambda d: d.polygon([(cx - 10, 18), (cx - 10.5, 8), (cx - 6, 2), (cx, 0), (cx + 6, 1), (cx + 10, 6), (cx + 10.5, 18), (cx + 8, 11), (cx + 3, 8), (cx - 3, 9), (cx - 7, 12)], fill=255), hc['b'], edge_k=.45)
    elif style == 'king':
        P.add(lambda d: d.polygon([(cx - 10, 17), (cx - 10.5, 8), (cx - 6, 2), (cx, 0), (cx + 6, 1), (cx + 10, 6), (cx + 10.5, 17), (cx + 8, 10), (cx + 5, 13), (cx + 2, 8), (cx - 1, 13), (cx - 4, 8), (cx - 8, 12)], fill=255), hc['b'], edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 5, 2), (cx - 2, -3 + 3), (cx + 1, 2)], fill=255), hc['b'], edge=False)
    elif style == 'tab':
        P.add(lambda d: d.polygon([(cx - 11, 30), (cx - 11.5, 9), (cx - 6, 3), (cx + 1, 1), (cx + 8, 3), (cx + 11.5, 9), (cx + 11, 30), (cx + 9, 18), (cx + 8, 12), (cx + 4, 11), (cx, 8), (cx - 4, 11), (cx - 8, 12), (cx - 9, 20)], fill=255), hc['b'], edge_k=.45)
    else:
        P.add(lambda d: d.polygon([(cx - 10, 17), (cx - 11, 8), (cx - 6, 2), (cx, 0), (cx + 7, 1), (cx + 11, 6), (cx + 10.5, 17), (cx + 8, 10), (cx + 5, 14), (cx + 3, 8), (cx - 1, 13), (cx - 4, 8), (cx - 8, 13)], fill=255), hc['b'], edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 1, 2), (cx + 3, -3 + 3), (cx + 5, 2)], fill=255), hc['b'], edge=False)
    mh = P.mask(lambda d: d.polygon([(cx + 5, 3), (cx + 11, 6), (cx + 11, 17), (cx + 8, 10)], fill=255))
    P.a[mh & (P.a[..., 3] > 0) & (P.a[..., :3] == hc['b']).all(-1)] = (*hc['d'], 255)
    if CS.get('hair2') is None: P.line([(cx - 7, 5), (cx - 3, 3)], hc['l']); P.line([(cx - 2, 3), (cx + 3, 2)], hc['l'])
    if fem and outfit == 'uniform':
        P.add(lambda d: d.polygon([(cx - 10, 9), (cx - 7, 2), (cx, 0), (cx + 7, 2), (cx + 10, 9)], fill=255), o['top'], edge_k=.45)
        P.add(lambda d: d.polygon([(cx - 12, 9), (cx + 14, 9), (cx + 16, 12), (cx - 10, 12)], fill=255), o['top2'], edge_k=.45)
    if CS['beard']:
        P.add(lambda d: d.polygon([(cx - 7.5, 19), (cx - 6, 24), (cx - 3, 27), (cx + 3, 27), (cx + 6, 24), (cx + 7.5, 19), (cx + 4, 22), (cx - 4, 22)], fill=255), hc['d'], edge_k=.5, sh=False)
    if who == 'king': P.rect(cx + 11, 14, cx + 11, 19, (255, 200, 70))
    RG.over_b(P, CS, cx, hc, sk, GY, top)
    return P.final()

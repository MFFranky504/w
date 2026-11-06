"""Portrait v2 — retrato anime pixel-art de alto detalle (lienzo 124x170).
Volumen por piezas con contorno de color (Paint), ojos grandes con doble brillo, mechones de pelo, pliegues y manos."""
import math
import numpy as np
from PIL import Image, ImageDraw
from lib import shade
from sprites import Paint
from cast import resolve

W, H, CX = 124, 170, 62
K = 1.4                       # escala respecto al diseño de pelo antiguo (cx=48, frente y=24)

def T(pts):                    # transforma coordenadas del diseño antiguo (cx=48) al nuevo lienzo
    return [(CX + (x - 48) * K, 27 + (y - 24) * 1.0) for x, y in pts]

C0 = 48
HAIR = {
 'king': [
   ('b', [(C0-22,52),(C0-24,32),(C0-20,18),(C0-12,9),(C0-2,5),(C0+9,6),(C0+18,12),(C0+23,22),(C0+24,34),(C0+22,50),(C0+19,36),(C0+16,40),(C0+13,30),(C0+8,37),(C0+4,28),(C0-1,36),(C0-5,28),(C0-10,36),(C0-14,28),(C0-18,38),(C0-20,32)]),
   ('b', [(C0-8,9),(C0-4,0),(C0,6)]), ('b', [(C0+4,6),(C0+12,0),(C0+13,9)]),
   ('d', [(C0+14,14),(C0+23,22),(C0+24,34),(C0+22,50),(C0+19,36),(C0+18,24)])],
 'short': [
   ('b', [(C0-21,34),(C0-24,20),(C0-18,10),(C0-6,4),(C0+6,3),(C0+16,7),(C0+23,16),(C0+24,28),(C0+21,36),(C0+19,27),(C0+13,20),(C0+4,16),(C0-6,16),(C0-14,20),(C0-18,27)]),
   ('d', [(C0+14,5),(C0+23,16),(C0+24,28),(C0+21,36),(C0+19,27),(C0+17,17)])],
 'shag': [
   ('b', [(C0-24,52),(C0-27,30),(C0-23,14),(C0-13,4),(C0,0),(C0+13,3),(C0+22,10),(C0+27,26),(C0+25,52),(C0+21,42),(C0+19,32),(C0+14,22),(C0+6,16),(C0-4,15),(C0-12,19),(C0-18,26),(C0-21,40)]),
   ('b', [(C0-14,18),(C0-9,27),(C0-5,17)]), ('b', [(C0-3,16),(C0+1,25),(C0+5,16)]), ('b', [(C0+6,16),(C0+10,24),(C0+14,19)]),
   ('d', [(C0+12,5),(C0+22,10),(C0+27,26),(C0+25,52),(C0+21,42),(C0+19,30)])],
 'tab': [
   ('b', [(C0-24,66),(C0-26,34),(C0-21,18),(C0-10,9),(C0+4,7),(C0+17,12),(C0+24,24),(C0+26,40),(C0+24,66),(C0+20,52),(C0+19,36),(C0+14,30),(C0+11,38),(C0+5,26),(C0+1,36),(C0-4,24),(C0-10,34),(C0-14,26),(C0-18,38),(C0-20,52)]),
   ('d', [(C0+14,14),(C0+24,24),(C0+26,40),(C0+24,66),(C0+20,52),(C0+19,30)])],
 'you': [
   ('b', [(C0-22,54),(C0-25,30),(C0-19,15),(C0-8,7),(C0+6,5),(C0+18,11),(C0+24,24),(C0+24,36),(C0+22,52),(C0+19,38),(C0+15,42),(C0+13,32),(C0+7,40),(C0+4,30),(C0-2,40),(C0-5,30),(C0-11,40),(C0-14,32),(C0-18,42),(C0-20,34)]),
   ('b', [(C0-2,7),(C0+3,-1),(C0+6,6)]),
   ('d', [(C0+14,13),(C0+24,24),(C0+24,36),(C0+22,52),(C0+19,38),(C0+18,24)])],
}
# mechones (líneas oscuras que siguen el flujo) y reflejos (curvas claras), en coordenadas antiguas
STRANDS = {
 'king':  [[(C0-12,8),(C0-14,22)], [(C0-2,6),(C0-4,24)], [(C0+8,8),(C0+8,26)], [(C0+16,14),(C0+16,32)]],
 'short': [[(C0-6,6),(C0-9,22)], [(C0+3,6),(C0+3,18)], [(C0+13,10),(C0+14,24)], [(C0-14,12),(C0-17,28)]],
 'shag':  [[(C0-14,6),(C0-18,24)], [(C0-4,3),(C0-8,18)], [(C0+6,3),(C0+4,16)], [(C0+16,8),(C0+18,28)]],
 'tab':   [[(C0-16,12),(C0-21,50)], [(C0-8,9),(C0-13,34)], [(C0+8,9),(C0+14,34)], [(C0+18,14),(C0+22,56)]],
 'you':   [[(C0-12,8),(C0-15,26)], [(C0,6),(C0-3,26)], [(C0+9,7),(C0+10,26)], [(C0+17,12),(C0+19,30)]],
}
SHINE = {
 'king':  [(C0-18,16),(C0-10,10),(C0-2,8),(C0+8,10)], 'short': [(C0-17,17),(C0-8,10),(C0+2,8),(C0+12,12)],
 'shag':  [(C0-20,14),(C0-12,7),(C0-2,4),(C0+10,6)],  'tab':   [(C0-19,18),(C0-10,11),(C0+2,9),(C0+14,13)],
 'you':   [(C0-17,15),(C0-9,9),(C0+1,7),(C0+11,9)],
}

TOPS = {'tux': ((32, 32, 44), (18, 18, 28), (84, 84, 106)), 'grey': ((158, 162, 174), (112, 116, 132), (210, 214, 224)),
        'argentina': ((150, 206, 246), (100, 160, 214), (230, 246, 255)), 'blazer': ((54, 72, 124), (34, 46, 86), (100, 124, 184)),
        'polo': ((212, 152, 82), (160, 104, 50), (250, 202, 132)), 'coat': ((246, 248, 252), (196, 206, 224), (255, 255, 255)),
        'tee_blue': ((70, 130, 220), (40, 86, 170), (130, 180, 250)), 'tee_green': ((80, 190, 110), (40, 140, 76), (150, 230, 170)),
        'tee_yellow': ((250, 210, 70), (206, 160, 30), (255, 240, 150)), 'tee_red': ((230, 80, 70), (170, 44, 48), (255, 140, 120)),
        'plaid': ((204, 70, 62), (150, 40, 44), (238, 118, 100)), 'teacher': ((236, 232, 220), (196, 192, 182), (252, 252, 248)),
        'cardigan': ((230, 176, 72), (184, 130, 44), (250, 210, 120)), 'uniform': ((246, 122, 162), (206, 84, 126), (255, 172, 202)),
        'hoodie': ((80, 96, 206), (54, 64, 152), (126, 146, 238))}


def portrait2(who='king', expr='n', look=(0, 0), blink=False, sc=None, outfit=None, cap=False, gesture='none', turn=0.5):
    CS = resolve(who); style = CS['style']
    sk = CS['skin']; skd = shade(sk, .84); skdd = shade(sk, .68); skl = shade(sk, 1.045)
    hc = CS['hair']
    outfit = outfit or CS['outfit']
    P = Paint(W, H)
    cx = CX
    hxo = int(round(3 * turn))
    Tt = lambda pts: [(x + hxo, y) for x, y in T(pts)]
    poly = lambda pts, col, **kw: P.add(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255), col, **kw)

    # ----------------------------------------------------------- pelo trasero
    if style == 'tab':
        poly(T([(C0-27,30),(C0-31,98),(C0-20,104),(C0+20,104),(C0+31,98),(C0+27,30),(C0+16,12),(C0-16,12)]), hc['d'], edge_k=.45)
    elif style in ('you', 'king', 'shag'):
        poly(T([(C0-23,34),(C0-24,58),(C0-17,60),(C0+17,60),(C0+24,58),(C0+23,34)]), hc['d'], edge_k=.45)

    # ----------------------------------------------------------- cuello (antes del torso: el cuello de la ropa lo tapa)
    poly([(cx-9,84),(cx+9,84),(cx+11,118),(cx-11,118)], skd, sh=False, hi=False, edge_k=.55)
    sh_n = P.mask(lambda d: d.polygon([(cx-9,92),(cx+9,92),(cx+10,104),(cx,108),(cx-10,104)], fill=255))
    yy_n = np.indices((H, W))[0]
    P.a[sh_n & (yy_n < 100)] = (*shade(sk, .66), 255); P.a[sh_n & (yy_n >= 100)] = (*shade(sk, .74), 255)
    # ----------------------------------------------------------- cuerpo (hombros caídos, ligera inclinación)
    tb, td, tl = TOPS[outfit]
    lo = 3                                                           # hombro izquierdo (del dibujo) más bajo
    torso = [(cx-15,111),(cx-9,115),(cx,117),(cx+9,115),(cx+15,111),(cx+36,117),(cx+52,127),(cx+60,148),(cx+62,H),(cx-62,H),(cx-60,148+lo),(cx-52,127+lo),(cx-36,117+lo)]
    tm = poly(torso, tb, edge_k=.42)
    def clip(lines, col, w=1):
        im = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(im)
        for l in lines: dd.line(l, fill=255, width=w)
        m = (np.array(im) > 0) & tm
        P.a[m] = (*col, 255)
    # pliegues genéricos
    clip([[(cx-36,120+lo),(cx-30,140),(cx-34,H)], [(cx+34,120),(cx+28,142),(cx+32,H)], [(cx-8,140),(cx-12,H)]], td)
    # sombra lateral derecha
    sh_m = P.mask(lambda d: d.polygon([(cx+30,116),(cx+52,127),(cx+60,148),(cx+62,H),(cx+36,H),(cx+34,140)], fill=255)) & tm
    P.a[sh_m] = (*td, 255)
    lt_m = P.mask(lambda d: d.polygon([(cx-52,127+lo),(cx-36,117+lo),(cx-30,118+lo),(cx-46,132+lo),(cx-56,150+lo),(cx-60,150+lo)], fill=255)) & tm
    P.a[lt_m] = (*tl, 255)
    under = (250, 248, 244)
    if outfit == 'plaid':
        clip([[(5, y), (W-5, y+1)] for y in range(124, H, 9)] + [[(x, 112), (x-2, H)] for x in range(cx-54, cx+56, 11)], td)
        poly([(cx-10,112),(cx+10,112),(cx,134)], under, edge_k=.65)
        poly([(cx-16,112),(cx-6,126),(cx-1,116)], tl); poly([(cx+16,112),(cx+6,126),(cx+1,116)], tb)
    elif outfit == 'teacher':
        poly([(cx-14,112),(cx,128),(cx+14,112),(cx+8,110),(cx,118),(cx-8,110)], (252,252,250), edge_k=.7)
        poly([(cx-3,118),(cx+3,118),(cx+5,150),(cx,156),(cx-5,150)], (48,84,156), edge_k=.55); P.rect(cx-1,120,cx-1,148,(90,130,206))
    elif outfit == 'cardigan':
        poly([(cx-13,112),(cx,140),(cx+13,112)], (252,242,226), sh=False, edge_k=.55)
        P.line([(cx-14,112),(cx-1,142),(cx-1,H)], td); P.line([(cx+14,112),(cx+1,142),(cx+1,H)], td)
        for y in (148, 158): P.rect(cx+3, y, cx+5, y+2, (120,80,30)); P.px(cx+3, y, (200,150,80))
    elif outfit == 'uniform':
        poly([(cx-15,112),(cx-4,128),(cx,118),(cx+4,128),(cx+15,112),(cx+9,110),(cx,116),(cx-9,110)], (255,255,255), edge_k=.7)
        P.rect(cx+16,134,cx+30,142,(255,255,255)); P.rect(cx+18,138,cx+28,138,td)
    elif outfit == 'hoodie':
        poly([(cx-26,108),(cx-14,98),(cx+14,98),(cx+26,108),(cx+14,118),(cx-14,118)], td, edge_k=.5)           # capucha
        poly([(cx-11,110),(cx,124),(cx+11,110)], shade(td, .78))
        P.line([(cx-6,122),(cx-8,146)], (246,246,252)); P.line([(cx+6,122),(cx+8,142)], (246,246,252))
        P.rect(cx-9,146,cx-7,150,(220,220,232)); P.rect(cx+7,142,cx+9,146,(220,220,232))
    elif outfit == 'tux':
        poly([(cx-10,112),(cx+10,112),(cx+4,150),(cx-4,150)], (250,250,252), edge_k=.6)
        P.line([(cx-16,112),(cx-4,146)], td); P.line([(cx+16,112),(cx+4,146)], td)
        poly([(cx-7,118),(cx+7,118),(cx+7,125),(cx-7,125)], (190,34,54), edge_k=.5); P.rect(cx-2,119,cx+2,124,(230,80,100))
    elif outfit == 'grey':
        poly([(cx-14,110),(cx+14,110),(cx+10,120),(cx-10,120)], td, edge_k=.5)                                   # cuello de canalé
        clip([[(cx-8,126),(cx-8,134)], [(cx-4,126),(cx-4,134)], [(cx,126),(cx,134)], [(cx+4,126),(cx+4,134)], [(cx+8,126),(cx+8,134)]], shade(td,.85))
    elif outfit == 'argentina':
        clip([[(x, 112), (x, H)] for x in range(cx-60, cx+62, 12)], (252,252,255), w=5)
        poly([(cx-9,112),(cx+9,112),(cx,122)], tb, edge_k=.5)
    elif outfit in ('blazer', 'coat'):
        poly([(cx-10,112),(cx+10,112),(cx+3,150),(cx-3,150)], (250,250,250), edge_k=.6)
        P.line([(cx-18,112),(cx-4,146)], td); P.line([(cx+18,112),(cx+4,146)], td)
    elif outfit == 'polo':
        poly([(cx-12,112),(cx+12,112),(cx,126)], (250,240,220), sh=False, edge_k=.55)
    else:
        P.rect(cx-18,150,cx+18,150,td)

    if outfit == 'hoodie':   # auriculares al cuello
        P.add(lambda d: d.arc([cx-28, 84, cx+28, 132], 12, 168, fill=255, width=3), (44,44,58), sh=False, hi=False, edge_k=.4)
        for sx in (-1, 1):
            P.add(lambda d, sx=sx: d.ellipse([cx+sx*30-8, 104, cx+sx*30+8, 124], fill=255), (58,58,80))
            P.add(lambda d, sx=sx: d.ellipse([cx+sx*30-4, 108, cx+sx*30+4, 120], fill=255), (255,170,64), sh=False, hi=False, edge=False)
            P.px(cx+sx*30-3, 109, (255,226,150)); P.px(cx+sx*30-2, 109, (255,226,150))

    # ----------------------------------------------------------- cabeza anime (3/4, barbilla en V, ojos rasgados)
    fc = cx + int(round(7 * turn))                       # eje de la cara (rasgos)
    wl, wr = 22 + 2.5 * turn, 22 - 4 * turn                # semianchos izquierdo / derecho
    strong = CS['strong']
    FP = [(cx-wl*.86,30),(cx-12,25),(cx+12,25),(cx+wr*.86,30),(cx+wr,44),(cx+wr,60),(cx+wr*.94,78),(fc+11,89),(fc+1,97),(fc-11,89),(cx-wl*.95,78),(cx-wl,60),(cx-wl,44)]
    if strong: FP = [(cx-wl*.86,30),(cx-12,25),(cx+12,25),(cx+wr*.86,30),(cx+wr+1,44),(cx+wr+1,62),(cx+wr,78),(fc+14,91),(fc+2,99),(fc-14,91),(cx-wl-1,78),(cx-wl-1,62),(cx-wl-1,44)]
    near_left = turn >= 0
    if abs(turn) < .3 or near_left:                      # oreja izquierda
        P.add(lambda d: d.ellipse([cx-wl-4, 53, cx-wl+3, 69], fill=255), sk, sh=False, hi=False, edge_k=.5); P.rect(int(cx-wl-1), 57, int(cx-wl), 64, skdd)
    if abs(turn) < .3 or not near_left:                  # oreja derecha
        P.add(lambda d: d.ellipse([cx+wr-3, 53, cx+wr+4, 69], fill=255), skd, sh=False, hi=False, edge_k=.5); P.rect(int(cx+wr), 57, int(cx+wr+1), 64, skdd)
    fm = poly(FP, sk, sh=False, hi=False, edge_k=.4)
    def paint_face(pts, col):
        m = P.mask(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255)) & fm
        P.a[m] = (*col, 255)
    far = 1 if near_left else -1                          # lado lejano (derecha si la cara mira a la derecha)
    fx = lambda dx: cx + far * dx
    paint_face([(fx(8),26),(fx(26),44),(fx(26),62),(fx(24),76),(fx(14),90),(fc+far*2,98),(fx(2),94),(fx(10),80),(fx(14),60),(fx(12),40)], skd)          # lado en sombra (cel)
    paint_face([(fx(16),68),(fx(26),62),(fx(24),76),(fx(14),88),(fc+far*2,98),(fx(2),94),(fx(10),80)], shade(sk, .78))                                 # bajo el pómulo
    paint_face([(cx-14,26),(cx+14,26),(cx+12,36),(cx-12,34)], shade(sk, .86))                                                                         # sombra del flequillo (cel)
    # contorno interior: mandíbula y mejilla cercana (línea fina oscura, como en los retratos de referencia)
    jc = shade(sk, .56)
    nx = -far
    P.line([(int(cx+nx*(wl if near_left else wr)*.9), 74), (int(cx+nx*(wl if near_left else wr)*.78), 84), (int(fc+nx*7), 92)], jc)
    # rubor
    if style in ('tab', 'you'):
        bx = int(fc - 17 if near_left else fc + 8)
        P.rect(bx, 72, bx+8, 73, (244,160,156)); P.rect(bx+1, 74, bx+6, 74, (244,160,156))
    # ----------------------------------------------------------- ojos rasgados (párpado grueso en diagonal, iris alto cortado por el párpado)
    iris_d = CS['iris']; iris_m = tuple(min(255, int(v*1.25)) for v in iris_d); iris_l = tuple(min(255, int(v*1.9+40)) for v in iris_d)
    LASH = (28,20,38)
    fem = style in ('tab', 'you')
    yy_all = np.indices((H, W))[0]
    EYEBOX = []
    def aeye(ix, ox, y0, near):
        dirn = 1 if ox > ix else -1
        w = abs(ox - ix)
        pt = lambda u, v: (ix + dirn*u, y0 + v*1.3)
        tilt = -.5 if fem else 1.6                          # comisura exterior: ligeramente alzada (ellas) / caída (ellos)
        EYEBOX.append((min(ix, ox), y0, max(ix, ox), y0+10))
        if blink or expr == 'smile':
            pts = [pt(0,5), pt(.3*w,2.5), pt(.7*w,2.2), pt(w,4+tilt)] if expr == 'smile' else [pt(0,4), pt(.5*w,6), pt(w,4+tilt)]
            for p0, p1 in zip(pts, pts[1:]):
                for k in (0, 1): P.line([(int(p0[0]),int(p0[1])+k),(int(p1[0]),int(p1[1])+k)], LASH)
            return
        poly_pts = [pt(0,4), pt(.28*w,1.2), pt(.7*w,.6), pt(w,2.4+tilt), pt(.82*w,6), pt(.42*w,7.4), pt(.1*w,6.2)]
        wm = P.mask(lambda d: d.polygon([(float(x), float(y)) for x, y in poly_pts], fill=255))
        P.a[wm] = (248,246,250,255)
        icx = ix + dirn*(.5*w + look[0]*.6); icy = y0 + 4.7 + look[1]*.6
        ir = P.mask(lambda d: d.ellipse([icx-.33*w, icy-5.6, icx+.33*w, icy+5.6], fill=255)) & wm
        P.a[ir] = (*iris_m, 255)
        P.a[ir & (yy_all < icy - 1.6)] = (*shade(iris_d, .62), 255)                           # parte alta oscura (sombra del párpado)
        P.a[ir & (yy_all >= icy + 2.4)] = (*iris_l, 255)                                         # banda inferior clara
        pc = P.mask(lambda d: d.ellipse([icx-.14*w, icy-2.8, icx+.14*w, icy+2.8], fill=255)) & wm
        P.a[pc] = (20,14,28,255)
        hx = int(round(icx - dirn*.17*w)); hy = int(round(y0 + 2.2 + look[1]*.6))
        P.rect(min(hx, hx+dirn), hy, max(hx, hx+dirn), hy+1, (255,255,255))                  # brillo cuadrado
        P.px(int(round(icx + dirn*.16*w)), int(round(y0 + 7.4 + look[1]*.6)), (208,226,255))  # brillo menor
        # párpado superior grueso y diagonal (+ cola de la pestaña en ellas)
        top = [pt(-.4,3.8), pt(.28*w,.8), pt(.7*w,.2), pt(w,2.0+tilt), pt(w+(2.4 if fem else .8), 3.6+tilt-(1.6 if fem else 0))]
        for p0, p1 in zip(top, top[1:]):
            for k in (0, 1, 2): P.line([(int(round(p0[0])),int(round(p0[1]))+k),(int(round(p1[0])),int(round(p1[1]))+k)], LASH)
        low = [pt(.14*w,6.7), pt(.45*w,7.9), pt(.82*w,6.4)]                                   # pestaña inferior fina
        for p0, p1 in zip(low, low[1:]): P.line([(int(round(p0[0])),int(round(p0[1]))),(int(round(p1[0])),int(round(p1[1])))], shade(LASH, 1.9))
        P.line([(int(round(pt(.1*w,-.8)[0])),int(round(y0-.8))),(int(round(pt(.8*w,-1.2)[0])),int(round(y0-1.2)))], shade(sk, .6))   # pliegue del párpado
    wn = 14.0; wf = 14.0 - 5*abs(turn)
    eyes_y = 52
    if near_left:
        aeye(fc-4, fc-4-wn, eyes_y, True); aeye(fc+4, fc+4+wf, eyes_y, False)
    else:
        aeye(fc-4, fc-4-wf, eyes_y, False); aeye(fc+4, fc+4+wn, eyes_y, True)
    if CS['sleepy']:
        for (bx0, by0, bx1, by1) in EYEBOX:
            for yy in range(by0, by0+3):
                for xx in range(int(bx0)-1, int(bx1)+2):
                    if P.a[yy, xx, 3] > 0 and tuple(P.a[yy, xx, :3]) not in (tuple(LASH),): P.a[yy, xx] = (*skd, 255)
            for xx in range(int(bx0)-1, int(bx1)+3): P.px(xx, by0+3, LASH); P.px(xx, by0+4, LASH)
    # cejas finas y angulosas
    brc = hc['dd'] if style != 'tab' else hc['d']
    th = 2 if (CS['strong'] or style in ('king', 'short', 'shag')) else 1
    def brow(p0, p1, p2):
        for a_, b_ in ((p0, p1), (p1, p2)):
            for k in range(th): P.line([(int(a_[0]),int(a_[1])+k),(int(b_[0]),int(b_[1])+k)], brc)
    by = eyes_y - 5
    for (ixx, sgn, wd) in ((fc-4, -1, wn if near_left else wf), (fc+4, 1, wf if near_left else wn)):
        inner_dy, outer_dy = {'n': (1, -1), 'smile': (0, -1), 'sad': (-2, 1), 'worry': (-2, 1), 'wow': (-3, -4)}.get(expr, (1, -1))
        if style in ('king', 'short', 'shag', 'you') and expr == 'n': inner_dy, outer_dy = (2, -1)
        brow((ixx, by+inner_dy), (ixx+sgn*wd*.5, by+(inner_dy+outer_dy)//2-1), (ixx+sgn*wd*1.05, by+outer_dy+1))
    # nariz y boca mínimos
    P.line([(fc+1,67),(fc+1,71)], skdd); P.rect(fc-1,72,fc+1,72,skdd)
    lip, dark = (176,80,88), (112,38,52)
    my = 82
    if expr == 'smile':
        poly([(fc-8,my-2),(fc+8,my-2),(fc+6,my+3),(fc-6,my+3)], dark, sh=False, hi=False, edge=False)
        P.rect(fc-6,my-2,fc+6,my-1,(252,250,250)); P.line([(fc-9,my-3),(fc-6,my+3),(fc+6,my+3),(fc+9,my-3)], lip)
    elif expr == 'wow':
        P.add(lambda d: d.ellipse([fc-4,my-3,fc+4,my+6], fill=255), dark, sh=False, hi=False, edge=False)
    elif expr == 'sad':
        P.line([(fc-6,my+2),(fc-2,my),(fc+3,my),(fc+6,my+3)], lip)
    elif expr == 'worry':
        P.line([(fc-6,my+1),(fc-2,my),(fc+2,my+2),(fc+6,my-1)], lip)
    else:
        P.rect(fc-5,my,fc+4,my,lip); P.px(fc-6,my+1,lip) ; P.px(fc+5,my-1,shade(lip,.85))      # boca pequeña con comisura caída (serio)
    # barba de dos días: moteado sutil y disperso en la mandíbula
    if CS['stubble']:
        for yy in range(78, 99):
            for xx in range(cx-30, cx+31):
                if P.a[yy, xx, 3] > 0 and tuple(P.a[yy, xx, :3]) in (tuple(sk), tuple(skd), tuple(shade(sk,.76))) and (xx*5 + yy*11) % 17 == 0 and (yy > 86 or abs(xx-cx) > 9): P.a[yy, xx] = (*shade(sk,.8), 255)
        shade_m = P.mask(lambda d: d.polygon([(cx-26,80),(cx-14,92),(cx,98),(cx+14,92),(cx+26,80),(cx+22,92),(cx+13,98),(cx-13,98),(cx-22,92)], fill=255)) & fm
        yy_, xx_ = np.indices((H, W)); P.a[shade_m & ((xx_+yy_) % 3 == 0) & ((np.abs(xx_-cx) > 8) | (yy_ > 90))] = (*shade(sk,.82), 255)
    # gafas (siguen la posición de cada ojo)
    if CS['glasses']:
        g = (34,30,48)
        for (bx0, by0, bx1, by1) in EYEBOX:
            P.add(lambda d, bx0=bx0, by0=by0, bx1=bx1, by1=by1: d.rounded_rectangle([bx0-3, by0-4, bx1+3, by1+3], radius=4, outline=255, width=2), g, edge=False, sh=False, hi=False)
            P.rect(int(bx0), int(by1)-1, int(bx0)+2, int(by1), (210,232,255)); P.rect(int(bx1)-3, int(by0)-2, int(bx1)-1, int(by0)-2, (220,236,255))
        (a0, _, a1, _), (b0, _, b1, _) = sorted(EYEBOX)[0], sorted(EYEBOX)[1]
        P.rect(int(a1)+3, eyes_y+1, int(b0)-3, eyes_y+2, g)

    # ----------------------------------------------------------- pelo frontal (tonos, mechones y reflejos)
    for tone, pts in HAIR[style]:
        poly(Tt(pts), hc[tone], edge_k=.4)
    # mechones: líneas oscuras siguiendo el flujo
    for stl in STRANDS[style]:
        pts = Tt(stl)
        for a, b in zip(pts, pts[1:]): P.line([(int(a[0]),int(a[1])),(int(b[0]),int(b[1]))], hc['dd'])
    # reflejos: banda curva clara
    sp = Tt(SHINE[style])
    for a, b in zip(sp, sp[1:]):
        P.line([(int(a[0]),int(a[1])),(int(b[0]),int(b[1]))], hc['l']); P.line([(int(a[0]),int(a[1])+1),(int(b[0]),int(b[1])+1)], shade(hc['l'], .8))
    if style == 'tab' and cap:
        poly(T([(C0-22,26),(C0-19,12),(C0-8,5),(C0+8,5),(C0+19,12),(C0+22,26)]), (246,120,160), edge_k=.45)
        poly(T([(C0-24,26),(C0+26,26),(C0+30,31),(C0-22,30)]), (206,82,124), edge_k=.45)
    # ----------------------------------------------------------- gesto: mano que sujeta unas hojas (dedos curvados sobre el borde)
    if gesture == 'hold':
        px0, py0 = cx + 18, 112
        P.add(lambda d: d.polygon([(px0, py0+8), (px0+30, py0), (px0+36, py0+34), (px0+4, py0+44)], fill=255), (250,248,238), edge_k=.62)
        for i in range(6):
            P.line([(px0+5+i//2, py0+13+i*5-(0 if i<3 else 1)), (px0+27+i//3, py0+7+i*5)], (122,124,142))
        # sombra de la hoja sobre la ropa
        # mano: palma por detrás del borde inferior, cuatro dedos redondeados por delante y pulgar
        hx, hy = px0 + 16, py0 + 42
        P.add(lambda d: d.ellipse([hx-12, hy-3, hx+14, hy+16], fill=255), sk, edge_k=.45)
        for fx, fl in [(-10, 9), (-4, 11), (2, 11), (8, 9)]:
            P.add(lambda d, fx=fx, fl=fl: d.rounded_rectangle([hx+fx-2, hy-fl, hx+fx+2, hy+3], radius=2, fill=255), sk, edge_k=.45)
            P.rect(hx+fx-1, hy-fl+1, hx+fx-1, hy-fl+3, skl)
        P.add(lambda d: d.ellipse([hx-17, hy-12, hx-9, hy+2], fill=255), sk, edge_k=.45)                 # pulgar sobre la hoja
        P.line([(hx-3, hy+8), (hx+5, hy+8)], skdd)
    if gesture == 'fists':
        for fxx, flip in ((cx-48, -1), (cx+48, 1)):
            fy = 132
            P.add(lambda d: d.rounded_rectangle([fxx-11, fy, fxx+11, fy+22], radius=5, fill=255), sk if flip < 0 else skd, edge_k=.45)
            for k in range(4):
                P.add(lambda d, k=k: d.rounded_rectangle([fxx-11+k*5.5, fy-5, fxx-6.5+k*5.5, fy+6], radius=2, fill=255), sk if flip < 0 else skd, edge_k=.45)
            P.add(lambda d: d.rounded_rectangle([fxx-9+flip*4, fy+10, fxx+7+flip*4, fy+19], radius=4, fill=255), shade(sk, 1.04), edge_k=.45)         # pulgar sobre los dedos
            P.rect(fxx-7, fy+12, fxx+5, fy+12, skdd)
    return P.final()


if __name__ == '__main__':
    import sys
    from PIL import Image
    names = ['stallone', 'king', 'tab', 'you']
    Wd = Image.new('RGBA', (4 * 520, 700), (52, 110, 112, 255))
    for i, n in enumerate(names):
        p = portrait2(n); Wd.alpha_composite(p.resize((p.width * 4, p.height * 4), Image.NEAREST), (i * 520 + 10, 0))
    Wd.save('/home/user/w/tuconfia/out/portrait2_test.png')

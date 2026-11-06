"""Portrait v2 — retrato anime pixel-art de alto detalle (lienzo 124x170).
Volumen por piezas con contorno de color (Paint), ojos grandes con doble brillo, mechones de pelo, pliegues y manos."""
import math
import numpy as np
from PIL import Image, ImageDraw
from lib import shade
from sprites import Paint
from cast import resolve

W, H, CX = 124, 170, 62
K = 1.55                       # escala respecto al diseño de pelo antiguo (cx=48, frente y=24)

def T(pts):                    # transforma coordenadas del diseño antiguo (cx=48) al nuevo lienzo
    return [(CX + (x - 48) * K, 25 + (y - 24) * K) for x, y in pts]

C0 = 48
HAIR = {
 'king': [
   ('b', [(C0-22,52),(C0-24,32),(C0-20,18),(C0-12,9),(C0-2,5),(C0+9,6),(C0+18,12),(C0+23,22),(C0+24,34),(C0+22,50),(C0+19,36),(C0+16,40),(C0+13,30),(C0+8,37),(C0+4,28),(C0-1,36),(C0-5,28),(C0-10,36),(C0-14,28),(C0-18,38),(C0-20,32)]),
   ('b', [(C0-8,9),(C0-4,0),(C0,6)]), ('b', [(C0+4,6),(C0+12,0),(C0+13,9)]),
   ('d', [(C0+14,14),(C0+23,22),(C0+24,34),(C0+22,50),(C0+19,36),(C0+18,24)])],
 'short': [
   ('b', [(C0-22,40),(C0-24,32),(C0-20,18),(C0-12,9),(C0-2,5),(C0+9,6),(C0+18,12),(C0+23,22),(C0+24,34),(C0+22,40),(C0+19,30),(C0+15,20),(C0+8,15),(C0,13),(C0-10,16),(C0-16,22),(C0-19,32)]),
   ('d', [(C0+14,14),(C0+23,22),(C0+24,34),(C0+22,40),(C0+19,30),(C0+18,22)])],
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


def portrait2(who='king', expr='n', look=(0, 0), blink=False, sc=None, outfit=None, cap=False, gesture='none'):
    CS = resolve(who); style = CS['style']
    sk = CS['skin']; skd = shade(sk, .84); skdd = shade(sk, .68); skl = shade(sk, 1.045)
    hc = CS['hair']
    outfit = outfit or CS['outfit']
    P = Paint(W, H)
    cx = CX
    poly = lambda pts, col, **kw: P.add(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255), col, **kw)

    # ----------------------------------------------------------- pelo trasero
    if style == 'tab':
        poly(T([(C0-27,30),(C0-31,98),(C0-20,104),(C0+20,104),(C0+31,98),(C0+27,30),(C0+16,12),(C0-16,12)]), hc['d'], edge_k=.45)
    elif style in ('you', 'king', 'short', 'shag'):
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

    # ----------------------------------------------------------- cabeza (volumen: base + sombra lateral + luz frontal)
    FP = [(cx-24,30),(cx-15,25),(cx+15,25),(cx+24,30),(cx+28,44),(cx+28,62),(cx+25,76),(cx+18,88),(cx+9,96),(cx,98),(cx-9,96),(cx-18,88),(cx-25,76),(cx-28,62),(cx-28,44)]
    if CS['strong']: FP = [(cx-24,30),(cx-15,25),(cx+15,25),(cx+24,30),(cx+29,44),(cx+30,62),(cx+28,78),(cx+22,90),(cx+13,98),(cx,100),(cx-13,98),(cx-22,90),(cx-28,78),(cx-30,62),(cx-29,44)]
    for sx in (-1, 1):                                                       # orejas
        P.add(lambda d, sx=sx: d.ellipse([cx+sx*29-5, 52, cx+sx*29+5, 70], fill=255), sk if sx < 0 else skd, sh=False, hi=False, edge_k=.5)
        P.rect(cx+sx*29-1, 56, cx+sx*29, 64, skdd)
    fm = poly(FP, sk, sh=False, hi=False, edge_k=.45)
    def paint_face(pts, col):
        m = P.mask(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255)) & fm
        P.a[m] = (*col, 255)
    paint_face([(cx+16,26),(cx+28,44),(cx+28,62),(cx+25,76),(cx+18,88),(cx+9,96),(cx+4,97),(cx+14,84),(cx+19,70),(cx+19,50)], skd)           # sombra lado derecho
    paint_face([(cx+22,64),(cx+27,62),(cx+25,76),(cx+18,88),(cx+9,96),(cx+4,97),(cx+14,82)], shade(sk, .76))                                 # sombra bajo el pómulo/mandíbula
    paint_face([(cx-22,36),(cx-12,28),(cx-6,32),(cx-14,46),(cx-22,52)], skl)                                                                   # luz sobre la frente
    paint_face([(cx-22,66),(cx-12,64),(cx-14,76),(cx-20,78)], skl)                                                                            # luz en el pómulo
    paint_face([(cx-16,26),(cx+16,26),(cx+14,34),(cx-14,34)], shade(sk, .92))                                                                 # sombra del flequillo
    # rubor
    if style in ('tab', 'you'):
        for bx in (cx-22, cx+12):
            col_b = (244,160,156) if bx < cx else (236,150,146)
            P.rect(bx+1, 71, bx+9, 73, col_b); P.rect(bx, 72, bx+10, 72, col_b); P.rect(bx+3, 70, bx+7, 70, shade(col_b, 1.08))
    # ----------------------------------------------------------- ojos
    iris_d = CS['iris']; iris_l = tuple(min(255, int(v*1.7+30)) for v in iris_d)
    LASH = (30,22,40)
    def eye(x0, y0, mirror):
        # forma del ojo: polígono blanco con borde superior grueso; iris + pupila recortados a la forma
        sx = -1 if mirror else 1
        X = lambda dx: x0 + (14-dx if mirror else dx)
        if blink or expr == 'smile':
            pts = [(X(0),y0+7),(X(3),y0+4),(X(7),y0+3),(X(11),y0+4),(X(14),y0+7)] if expr == 'smile' else [(X(0),y0+7),(X(7),y0+9),(X(14),y0+7)]
            for a, b in zip(pts, pts[1:]): P.line([(int(a[0]),int(a[1])),(int(b[0]),int(b[1]))], LASH); P.line([(int(a[0]),int(a[1])+1),(int(b[0]),int(b[1])+1)], LASH)
            return
        wm = P.mask(lambda d: d.polygon([(X(0),y0+6),(X(3),y0+2),(X(8),y0+1),(X(12),y0+3),(X(14),y0+6),(X(11),y0+10),(X(6),y0+11),(X(2),y0+9)], fill=255))
        P.a[wm] = (252,250,254,255)
        ir = P.mask(lambda d: d.ellipse([X(4)+look[0]-(0 if not mirror else 0), y0+1+look[1], X(11)+look[0], y0+11+look[1]] if not mirror else [X(11)+look[0], y0+1+look[1], X(4)+look[0], y0+11+look[1]], fill=255)) & wm
        P.a[ir] = (*iris_d, 255)
        yy = np.indices((H, W))[0]
        low = ir & (yy >= y0+7); P.a[low] = (*iris_l, 255)
        pc = P.mask(lambda d: d.ellipse([min(X(6),X(9))+look[0], y0+4+look[1], max(X(6),X(9))+look[0]+1, y0+8+look[1]], fill=255)) & wm
        P.a[pc] = (22,16,30,255)
        hx = X(5)+look[0] if not mirror else X(5)+look[0]-1
        P.rect(hx, y0+2+look[1], hx+1, y0+3+look[1], (255,255,255)); P.px(X(9)+look[0], y0+8+look[1], (214,232,255))
        # sombra del párpado sobre el ojo + línea de pestañas gruesa + pliegue
        for dx in range(0, 15):
            xx = X(dx)
            for k in (0, 1):
                y = y0 + (2 if 2 <= dx <= 12 else 4) + k - (1 if 4 <= dx <= 10 else 0)
                if 0 <= y < H: P.a[y, xx] = (*LASH, 255)
        P.a[wm & (yy <= y0+3) & (P.a[..., 0] > 200)] = (*shade((252,250,254),.78), 255)
        if style == 'tab' or style == 'you':   # pestaña exterior
            for k in range(3): P.px(X(0)-sx*k, y0+5-k, LASH)
        P.line([(X(2),y0-1),(X(7),y0-2),(X(12),y0)], shade(sk, .62))                                  # pliegue del párpado
        P.line([(X(3),y0+11),(X(10),y0+11)], shade(sk, .8))                                          # bolsa inferior
    ey0 = 52
    eye(cx-23, ey0, False); eye(cx+9, ey0, True)
    if CS['sleepy']:
        for x0 in (cx-23, cx+9):
            for yy in range(ey0-1, ey0+4):
                for xx in range(x0, x0+15):
                    if P.a[yy, xx, 3] > 0: P.a[yy, xx] = (*skd, 255)
            for xx in range(x0, x0+15): P.px(xx, ey0+4, LASH); P.px(xx, ey0+5, LASH)
    # cejas curvas
    brc = hc['dd'] if style != 'tab' else hc['d']
    th = 3 if CS['strong'] else 2
    def brow(pts):
        for a, b in zip(pts, pts[1:]):
            for k in range(th): P.line([(a[0],a[1]+k),(b[0],b[1]+k)], brc)
    by = 42 if expr != 'wow' else 38
    if expr in ('sad', 'worry'):
        brow([(cx-24,by+4),(cx-16,by),(cx-8,by-3)]); brow([(cx+8,by-3),(cx+16,by),(cx+24,by+4)])
    else:
        brow([(cx-24,by+2),(cx-17,by-2),(cx-8,by-1)]); brow([(cx+8,by-1),(cx+17,by-2),(cx+24,by+2)])
    # nariz y boca
    P.line([(cx+1,66),(cx+3,76)], skdd); P.rect(cx-3,78,cx+4,78,skdd); P.px(cx-3,79,shade(sk,.6)); P.px(cx+3,79,shade(sk,.6)); P.px(cx+1,69,skl)
    lip, dark = (184,84,92), (118,40,54)
    my = 86
    if expr == 'smile':
        poly([(cx-8,my-2),(cx+8,my-2),(cx+6,my+3),(cx-6,my+3)], dark, sh=False, hi=False, edge=False)
        P.rect(cx-6,my-2,cx+6,my-1,(252,250,250)); P.line([(cx-9,my-3),(cx-6,my+3),(cx+6,my+3),(cx+9,my-3)], lip); P.rect(cx-4,my+4,cx+4,my+4,shade(lip,1.2))
    elif expr == 'wow':
        P.add(lambda d: d.ellipse([cx-4,my-3,cx+4,my+6], fill=255), dark, sh=False, hi=False, edge=False)
    elif expr == 'sad':
        P.line([(cx-7,my+3),(cx-3,my),(cx+3,my),(cx+7,my+3)], lip); P.line([(cx-6,my+4),(cx-3,my+1)], shade(lip,.8))
    elif expr == 'worry':
        P.line([(cx-7,my+2),(cx-3,my+1),(cx+2,my+3),(cx+7,my)], lip)
    else:
        P.rect(cx-6,my,cx+6,my,lip); P.rect(cx-4,my+1,cx+4,my+2,shade(lip,1.15)); P.px(cx-7,my,shade(lip,.8)); P.px(cx+7,my,shade(lip,.8))
    # barba de dos días: moteado sutil y disperso en la mandíbula
    if CS['stubble']:
        for yy in range(78, 99):
            for xx in range(cx-30, cx+31):
                if P.a[yy, xx, 3] > 0 and tuple(P.a[yy, xx, :3]) in (tuple(sk), tuple(skd), tuple(shade(sk,.76))) and (xx*5 + yy*11) % 17 == 0 and (yy > 86 or abs(xx-cx) > 9): P.a[yy, xx] = (*shade(sk,.8), 255)
        shade_m = P.mask(lambda d: d.polygon([(cx-26,80),(cx-14,92),(cx,98),(cx+14,92),(cx+26,80),(cx+22,92),(cx+13,98),(cx-13,98),(cx-22,92)], fill=255)) & fm
        yy_, xx_ = np.indices((H, W)); P.a[shade_m & ((xx_+yy_) % 3 == 0) & ((np.abs(xx_-cx) > 8) | (yy_ > 90))] = (*shade(sk,.82), 255)
    # gafas
    if CS['glasses']:
        g = (34,30,48)
        for x0 in (cx-27, cx+6):
            P.add(lambda d, x0=x0: d.rounded_rectangle([x0, 47, x0+22, 70], radius=5, outline=255, width=2), g, edge=False, sh=False, hi=False)
            P.rect(x0+3, 66, x0+6, 67, (210,232,255)); P.rect(x0+4, 63, x0+5, 64, (210,232,255)); P.rect(x0+16, 50, x0+18, 50, (220,236,255))
        P.rect(cx-6, 54, cx+6, 55, g); P.line([(cx-27, 52), (cx-33, 54)], g); P.line([(cx+28, 52), (cx+33, 54)], g)

    # ----------------------------------------------------------- pelo frontal (tonos, mechones y reflejos)
    for tone, pts in HAIR[style]:
        poly(T(pts), hc[tone], edge_k=.4)
    # mechones: líneas oscuras siguiendo el flujo
    for stl in STRANDS[style]:
        pts = T(stl)
        for a, b in zip(pts, pts[1:]): P.line([(int(a[0]),int(a[1])),(int(b[0]),int(b[1]))], hc['dd'])
    # reflejos: banda curva clara
    sp = T(SHINE[style])
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
    return P.final()


if __name__ == '__main__':
    import sys
    from PIL import Image
    names = ['stallone', 'king', 'tab', 'you']
    Wd = Image.new('RGBA', (4 * 520, 700), (52, 110, 112, 255))
    for i, n in enumerate(names):
        p = portrait2(n); Wd.alpha_composite(p.resize((p.width * 4, p.height * 4), Image.NEAREST), (i * 520 + 10, 0))
    Wd.save('/home/user/w/tuconfia/out/portrait2_test.png')

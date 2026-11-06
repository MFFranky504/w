"""Personajes estilo anime / retrato Pokémon (pixel-art a 1x, contorno de color, sombreado plano).
Lienzo del busto: 96x116, cx=48. Hombros ~ y 86-92."""
import numpy as np
from PIL import Image, ImageDraw
from lib import C, shade

W, H, CX = 96, 172, 48

PAL = {
    'king': dict(skin=(246, 206, 170), hair=(44, 42, 62), hair_d=(26, 24, 40), hair_l=(96, 104, 150), iris=(58, 96, 168), iris_l=(110, 160, 220), blush=None, brow=(36, 32, 48)),
    'tab': dict(skin=(252, 214, 186), hair=(132, 78, 48), hair_d=(92, 52, 34), hair_l=(196, 132, 80), iris=(110, 62, 38), iris_l=(176, 116, 70), blush=(244, 150, 150), brow=(96, 56, 36)),
    'you': dict(skin=(242, 196, 158), hair=(52, 62, 116), hair_d=(32, 38, 76), hair_l=(110, 136, 206), iris=(70, 50, 40), iris_l=(150, 108, 74), blush=(236, 140, 130), brow=(36, 40, 76)),
}
LASH = (36, 22, 36)
PUP = (22, 16, 30)
WHITE = (252, 252, 255)

# ojo izquierdo (de la imagen), esquina exterior a la izquierda
EYE = {
    'open_f': ["...LLLLL..",
               ".LLLLLLLLL",
               "LL.WDDDDW.",
               "...WDPPDW.",
               "...WDPPDW.",
               "...WDDDDW.",
               "...WIIIIW.",
               "....WIIW..",
               ".....ll..."],
    'open_m': ["..........",
               "..LLLLLLL.",
               ".LLWDDDDWL",
               "...WDPPDW.",
               "...WDPPDW.",
               "...WDDDDW.",
               "...WIIIIW.",
               "....WIIW..",
               ".....ll..."],
    'down': ["..........",
             "..........",
             "...LLLLL..",
             ".LLLLLLLLL",
             "...WDDDDW.",
             "...WIPPIW.",
             "....WIIW..",
             ".....ll..."],
    'happy': ["..........",
              "..........",
              "....LLL...",
              "..LL...LL.",
              ".L.......L",
              "..........",
              "..........",
              ".........."],
    'closed': ["..........",
               "..........",
               "..........",
               "..........",
               ".LLLLLLLL.",
               "..l....l..",
               "..........",
               ".........."],
}


def _stamp(px, tpl, x0, y0, pal, mirror=False, hl=True):
    ir, il = pal['iris'], pal['iris_l']
    cm = {'L': LASH, 'D': ir, 'I': il, 'P': PUP, 'W': WHITE, 'l': shade(pal['skin'], .8)}
    for r, row in enumerate(tpl):
        if mirror: row = row[::-1]
        for c, ch in enumerate(row):
            if ch in cm: px[x0 + c, y0 + r] = (*cm[ch], 255)
    if hl and any('P' in r for r in tpl):
        rows = [i for i, r in enumerate(tpl) if 'D' in r]
        r0 = rows[0]
        cols = [i for i, ch in enumerate(tpl[r0][::-1] if mirror else tpl[r0]) if ch == 'D']
        hx = cols[-1] if not mirror else cols[-1]
        px[x0 + hx, y0 + r0] = (*WHITE, 255); px[x0 + hx, y0 + r0 + 1] = (*WHITE, 255)
        px[x0 + cols[0], y0 + r0 + 3] = (*shade(il, 1.3), 255)


def outline(layer, col):
    a = np.array(layer)
    al = a[..., 3] > 0
    dil = np.zeros_like(al)
    dil[:-1] |= al[1:]; dil[1:] |= al[:-1]; dil[:, :-1] |= al[:, 1:]; dil[:, 1:] |= al[:, :-1]
    edge = dil & ~al
    a[edge] = (*col, 255)
    return Image.fromarray(a, 'RGBA')


def L():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)


def portrait(who='king', expr='n', look=(0, 0), blink=False, sc=None, outfit=None, cap=False):
    from cast import resolve
    CS = resolve(who); style = CS['style']
    hr_ = CS['hair']
    p = dict(skin=CS['skin'], hair=hr_['b'], hair_d=hr_['d'], hair_l=hr_['l'], iris=CS['iris'], iris_l=tuple(min(255, int(v * 1.6 + 20)) for v in CS['iris']),
             blush=None if style in ('king', 'short') else (244, 150, 150), brow=hr_['dd'])
    sk = p['skin']; skd = shade(sk, .84); skdd = shade(sk, .7)
    hb, hd, hl = p['hair'], p['hair_d'], p['hair_l']
    ol_skin = shade(sk, .5); ol_hair = shade(hd, .6)
    outfit = outfit or CS['outfit']
    cx = CX
    final = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    # ------------------------------------------------ pelo trasero
    back, bd = L()
    if style == 'tab':
        bd.polygon([(cx - 27, 30), (cx - 31, 98), (cx - 20, 104), (cx + 20, 104), (cx + 31, 98), (cx + 27, 30), (cx + 16, 12), (cx - 16, 12)], fill=hb)
        bd.polygon([(cx + 18, 40), (cx + 31, 98), (cx + 20, 104), (cx + 22, 60)], fill=hd)
        for x in (cx - 24, cx - 18, cx + 18, cx + 24): bd.line([(x, 70), (x + (2 if x > cx else -2), 100)], fill=hd)
    elif style in ('you', 'king', 'short'):
        bd.polygon([(cx - 23, 34), (cx - 24, 58), (cx - 17, 60), (cx + 17, 60), (cx + 24, 58), (cx + 23, 34)], fill=hd)
    final.alpha_composite(outline(back, ol_hair))

    # ------------------------------------------------ cuerpo
    body, d = L()
    body_full = Image.new('RGBA', (W, H + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(body_full)
    tops = {'argentina': ((150, 206, 246), (100, 160, 214), (230, 246, 255)), 'blazer': ((52, 70, 120), (34, 46, 86), (96, 120, 180)), 'polo': ((210, 150, 80), (160, 104, 50), (250, 200, 130)),
            'coat': ((246, 248, 252), (196, 206, 224), (255, 255, 255)), 'tee_blue': ((70, 130, 220), (40, 86, 170), (130, 180, 250)), 'tee_green': ((80, 190, 110), (40, 140, 76), (150, 230, 170)),
            'tee_yellow': ((250, 210, 70), (206, 160, 30), (255, 240, 150)), 'tee_red': ((230, 80, 70), (170, 44, 48), (255, 140, 120)),
            'plaid': ((198, 66, 60), (150, 40, 44), (232, 110, 96)), 'teacher': ((236, 232, 220), (196, 192, 182), (252, 252, 248)),
            'cardigan': ((226, 172, 70), (184, 130, 44), (246, 206, 116)), 'uniform': ((246, 120, 160), (206, 82, 124), (255, 170, 200)),
            'hoodie': ((76, 92, 200), (52, 62, 150), (120, 140, 236))}
    tb, td, tl = tops[outfit]
    d.polygon([(2, H), (6, 92), (16, 84), (cx - 12, 78), (cx + 12, 78), (W - 16, 84), (W - 6, 92), (W - 2, H)], fill=tb)
    d.polygon([(cx + 14, 80), (W - 16, 84), (W - 6, 92), (W - 2, H), (cx + 26, H)], fill=td)
    d.polygon([(6, 92), (16, 84), (22, 84), (12, 96), (8, H), (2, H)], fill=tl)
    d.line([(26, 96), (24, H)], fill=td); d.line([(W - 26, 96), (W - 24, H)], fill=shade(td, .85))
    if outfit == 'plaid':
        for y in range(88, H, 7): d.line([(4, y), (W - 4, y)], fill=td)
        for x in range(10, W - 4, 9): d.line([(x, 84), (x, H)], fill=td)
        d.polygon([(cx - 9, 78), (cx + 9, 78), (cx, 88)], fill=(250, 248, 244))
        d.polygon([(cx - 13, 78), (cx - 6, 90), (cx - 1, 82)], fill=tl); d.polygon([(cx + 13, 78), (cx + 6, 90), (cx + 1, 82)], fill=tb)
    elif outfit == 'teacher':
        d.polygon([(cx - 12, 78), (cx - 4, 90), (cx, 82), (cx + 4, 90), (cx + 12, 78)], fill=(252, 252, 250))
        d.polygon([(cx - 2, 82), (cx + 2, 82), (cx + 4, 108), (cx, 112), (cx - 4, 108)], fill=(48, 84, 156))
        d.line([(cx - 1, 85), (cx - 1, 108)], fill=(80, 120, 196))
    elif outfit == 'cardigan':
        d.polygon([(cx - 11, 78), (cx, 96), (cx + 11, 78)], fill=(250, 240, 222))
        d.line([(cx - 12, 78), (cx - 1, 98), (cx - 1, H)], fill=td); d.line([(cx + 12, 78), (cx + 1, 98), (cx + 1, H)], fill=td)
        for y in (102, 110): d.point((cx + 4, y), fill=(120, 80, 30))
    elif outfit == 'uniform':
        d.polygon([(cx - 13, 78), (cx - 4, 90), (cx, 84), (cx + 4, 90), (cx + 13, 78)], fill=(255, 255, 255))
        d.rectangle([cx + 12, 98, cx + 24, 104], fill=(255, 255, 255)); d.line([(cx + 14, 101), (cx + 22, 101)], fill=td)
    elif outfit == 'hoodie':
        d.polygon([(cx - 20, 80), (cx - 12, 72), (cx + 12, 72), (cx + 20, 80), (cx + 12, 86), (cx - 12, 86)], fill=td)
        d.polygon([(cx - 9, 80), (cx, 88), (cx + 9, 80)], fill=shade(td, .8))
        d.line([(cx - 5, 86), (cx - 6, 104)], fill=(246, 246, 252)); d.line([(cx + 5, 86), (cx + 6, 102)], fill=(246, 246, 252))
        d.point((cx - 6, 105), fill=(200, 200, 210)); d.point((cx + 6, 103), fill=(200, 200, 210))
    body.alpha_composite(body_full.crop((0, 6, W, H + 6)))
    final.alpha_composite(outline(body, shade(td, .5)))
    if outfit == 'hoodie':  # auriculares al cuello
        hp, hd_ = L()
        hd_.arc([cx - 20, 56, cx + 20, 92], 20, 160, fill=(40, 40, 52), width=2)
        hd_.ellipse([cx - 24, 66, cx - 15, 76], fill=(46, 46, 60)); hd_.ellipse([cx + 15, 66, cx + 24, 76], fill=(46, 46, 60))
        hd_.ellipse([cx - 22, 68, cx - 17, 74], fill=(255, 168, 60)); hd_.ellipse([cx + 17, 68, cx + 22, 74], fill=(255, 168, 60))
        final.alpha_composite(outline(hp, (20, 20, 28)))

    # ------------------------------------------------ cuello + cara
    face, d = L()
    d.rectangle([cx - 6, 62, cx + 6, 76], fill=sk)
    d.rectangle([cx - 6, 62, cx + 6, 70], fill=skd)
    d.polygon([(cx + 2, 70), (cx + 6, 66), (cx + 6, 76), (cx + 2, 76)], fill=skd)
    ears = [(cx - 22, 42, cx - 16, 54), (cx + 16, 42, cx + 22, 54)]
    for e in ears: d.ellipse(e, fill=sk)
    d.point((cx - 19, 47), fill=skd); d.point((cx - 19, 48), fill=skd); d.point((cx + 19, 47), fill=skd); d.point((cx + 19, 48), fill=skd)
    fpoly = [(cx - 18, 24), (cx + 18, 24), (cx + 19, 48), (cx + 15, 58), (cx + 7, 66), (cx, 69), (cx - 7, 66), (cx - 15, 58), (cx - 19, 48)]
    d.polygon(fpoly, fill=sk)
    d.polygon([(cx + 15, 30), (cx + 18, 26), (cx + 19, 48), (cx + 15, 58), (cx + 10, 63), (cx + 14, 52), (cx + 16, 44)], fill=skd)
    final.alpha_composite(outline(face, ol_skin))
    px = final.load()
    # rubor
    if p['blush']:
        for bx in (cx - 14, cx + 9):
            for k in range(3): px[bx + k * 2, 58] = (*p['blush'], 255); px[bx + k * 2 + 1, 57] = (*p['blush'], 255)
    # ojos
    fem = style == 'tab'
    if blink: tpl = EYE['closed']
    elif expr == 'smile': tpl = EYE['happy']
    elif look[1] > 0: tpl = EYE['down']
    else: tpl = EYE['open_f' if fem else 'open_m']
    ey = 44
    _stamp(px, tpl, cx - 15, ey, p)
    _stamp(px, tpl, cx + 5, ey, p, mirror=True)
    # mirada lateral: desplaza pupilas 1 px
    if look[0] and tpl in (EYE['open_f'], EYE['open_m']):
        for x0, mir in ((cx - 15, False), (cx + 5, True)):
            pass
    # cejas
    br = p['brow']
    d = ImageDraw.Draw(final)
    lb, rb = (cx - 14, cx - 6), (cx + 6, cx + 14)
    by = 39
    if expr in ('sad', 'worry'):
        d.line([(lb[0], by + 1), (lb[1], by - 2)], fill=br, width=1); d.line([(lb[0] + 1, by + 2), (lb[1], by - 1)], fill=br)
        d.line([(rb[0], by - 2), (rb[1], by + 1)], fill=br); d.line([(rb[0], by - 1), (rb[1] - 1, by + 2)], fill=br)
    elif expr == 'wow':
        d.line([(lb[0], by - 2), (lb[1], by - 3)], fill=br); d.line([(rb[0], by - 3), (rb[1], by - 2)], fill=br)
    else:
        d.line([(lb[0], by), (lb[0] + 3, by - 1), (lb[1], by - 1)], fill=br); d.line([(rb[0], by - 1), (rb[1] - 3, by - 1), (rb[1], by)], fill=br)
    # nariz
    px[cx + 1, 56] = (*skdd, 255); px[cx, 57] = (*skd, 255)
    # boca
    lip, dark = (196, 88, 92), (120, 40, 52)
    my = 62
    if expr == 'smile':
        d.polygon([(cx - 4, my - 1), (cx + 4, my - 1), (cx + 3, my + 2), (cx - 3, my + 2)], fill=dark)
        d.line([(cx - 3, my - 1), (cx + 3, my - 1)], fill=WHITE); d.line([(cx - 2, my + 2), (cx + 2, my + 2)], fill=(232, 120, 128))
    elif expr == 'wow':
        d.ellipse([cx - 2, my - 2, cx + 2, my + 2], fill=dark)
    elif expr == 'sad':
        d.line([(cx - 3, my + 1), (cx - 1, my), (cx + 1, my), (cx + 3, my + 1)], fill=lip)
    elif expr == 'worry':
        d.line([(cx - 3, my + 1), (cx - 1, my), (cx + 1, my + 1), (cx + 3, my)], fill=lip)
    else:
        d.line([(cx - 2, my), (cx + 2, my)], fill=lip)
    # gafas de King
    if CS['glasses']:
        g = (34, 30, 46)
        for x0 in (cx - 17, cx + 3):
            d.rectangle([x0, ey, x0 + 13, ey + 9], outline=g)
            d.point((x0 + 2, ey + 7), fill=(210, 230, 255)); d.point((x0 + 3, ey + 6), fill=(210, 230, 255))
        d.line([(cx - 3, ey + 2), (cx + 2, ey + 2)], fill=g)
        d.line([(cx - 17, ey + 2), (cx - 20, ey + 1)], fill=g); d.line([(cx + 17, ey + 2), (cx + 20, ey + 1)], fill=g)

    # ------------------------------------------------ pelo frontal
    hair, d = L()
    if style == 'short':
        d.polygon([(cx - 22, 50), (cx - 24, 32), (cx - 20, 18), (cx - 12, 9), (cx - 2, 5), (cx + 9, 6), (cx + 18, 12), (cx + 23, 22), (cx + 24, 34), (cx + 22, 48), (cx + 19, 34), (cx + 15, 24), (cx + 8, 19), (cx, 18), (cx - 10, 20), (cx - 16, 25), (cx - 19, 38)], fill=hb)
        d.polygon([(cx + 14, 14), (cx + 23, 22), (cx + 24, 34), (cx + 22, 48), (cx + 19, 34), (cx + 18, 24)], fill=hd)
        d.line([(cx - 6, 8), (cx - 8, 22)], fill=hd)
        for a, b in [((cx - 16, 17), (cx - 6, 12)), ((cx - 4, 12), (cx + 4, 11)), ((cx + 6, 12), (cx + 13, 15))]: d.line([a, b], fill=hl)
    elif style == 'king':
        d.polygon([(cx - 22, 52), (cx - 24, 32), (cx - 20, 18), (cx - 12, 9), (cx - 2, 5), (cx + 9, 6), (cx + 18, 12), (cx + 23, 22), (cx + 24, 34), (cx + 22, 50),
                   (cx + 19, 36), (cx + 16, 40), (cx + 13, 30), (cx + 8, 37), (cx + 4, 28), (cx - 1, 36), (cx - 5, 28), (cx - 10, 36), (cx - 14, 28), (cx - 18, 38), (cx - 20, 32)], fill=hb)
        d.polygon([(cx - 8, 9), (cx - 4, 0), (cx, 6)], fill=hb); d.polygon([(cx + 4, 6), (cx + 12, 0), (cx + 13, 9)], fill=hb); d.polygon([(cx + 17, 12), (cx + 27, 10), (cx + 22, 19)], fill=hb)
        d.polygon([(cx + 14, 14), (cx + 23, 22), (cx + 24, 34), (cx + 22, 50), (cx + 19, 36), (cx + 18, 24)], fill=hd)
        for a, b in [((cx - 16, 17), (cx - 6, 12)), ((cx - 4, 12), (cx + 4, 11)), ((cx + 6, 12), (cx + 13, 15))]:
            d.line([a, b], fill=hl)
        d.line([(cx - 15, 18), (cx - 7, 13)], fill=hl)
    elif style == 'tab':
        d.polygon([(cx - 24, 66), (cx - 26, 34), (cx - 21, 18), (cx - 10, 9), (cx + 4, 7), (cx + 17, 12), (cx + 24, 24), (cx + 26, 40), (cx + 24, 66),
                   (cx + 20, 52), (cx + 19, 36), (cx + 14, 30), (cx + 11, 38), (cx + 5, 26), (cx + 1, 36), (cx - 4, 24), (cx - 10, 34), (cx - 14, 26), (cx - 18, 38), (cx - 20, 52)], fill=hb)
        d.polygon([(cx + 14, 14), (cx + 24, 24), (cx + 26, 40), (cx + 24, 66), (cx + 20, 52), (cx + 19, 30)], fill=hd)
        d.line([(cx - 17, 17), (cx - 8, 12)], fill=hl); d.line([(cx - 6, 11), (cx + 6, 10)], fill=hl); d.line([(cx - 16, 18), (cx - 9, 14)], fill=hl)
        d.line([(cx - 22, 40), (cx - 22, 58)], fill=hd)
        if cap:
            cp, cpd = (246, 120, 160), (206, 82, 124)
            d.polygon([(cx - 22, 26), (cx - 19, 12), (cx - 8, 5), (cx + 8, 5), (cx + 19, 12), (cx + 22, 26)], fill=cp)
            d.polygon([(cx + 10, 6), (cx + 19, 12), (cx + 22, 26), (cx + 14, 26)], fill=cpd)
            d.polygon([(cx - 24, 26), (cx + 26, 26), (cx + 30, 31), (cx - 22, 30)], fill=cpd)
            d.line([(cx - 12, 10), (cx - 2, 8)], fill=(255, 196, 216))
            d.ellipse([cx - 3, 13, cx + 3, 19], fill=(255, 255, 255))
    else:
        d.polygon([(cx - 22, 54), (cx - 25, 30), (cx - 19, 15), (cx - 8, 7), (cx + 6, 5), (cx + 18, 11), (cx + 24, 24), (cx + 24, 36), (cx + 22, 52),
                   (cx + 19, 38), (cx + 15, 42), (cx + 13, 32), (cx + 7, 40), (cx + 4, 30), (cx - 2, 40), (cx - 5, 30), (cx - 11, 40), (cx - 14, 32), (cx - 18, 42), (cx - 20, 34)], fill=hb)
        d.polygon([(cx - 2, 7), (cx + 3, -1), (cx + 6, 6)], fill=hb)          # ahoge
        d.polygon([(cx - 19, 15), (cx - 28, 14), (cx - 22, 22)], fill=hb)
        d.polygon([(cx + 14, 13), (cx + 24, 24), (cx + 24, 36), (cx + 22, 52), (cx + 19, 38), (cx + 18, 24)], fill=hd)
        d.line([(cx - 16, 16), (cx - 6, 11)], fill=hl); d.line([(cx - 4, 10), (cx + 7, 10)], fill=hl); d.line([(cx - 15, 17), (cx - 8, 13)], fill=hl)
    if CS['beard']:
        d.polygon([(cx - 17, 46), (cx - 16, 58), (cx - 9, 66), (cx, 70), (cx + 9, 66), (cx + 16, 58), (cx + 17, 46), (cx + 11, 54), (cx + 5, 58), (cx - 5, 58), (cx - 11, 54)], fill=hd)
    final.alpha_composite(outline(hair, ol_hair))
    return final


def arm(c, sx, sy, hx, hy, w, sleeve, skin, hand=3.2, nohand=False):
    """brazo con contorno de color (se dibuja en capa y se compone en el lienzo de la escena)."""
    from lib import WW, WH
    lay = Image.new('RGBA', (WW, WH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sleeve = tuple(sleeve)
    d.line([(sx, sy), (hx, hy)], fill=sleeve, width=int(w))
    d.line([(sx + 2, sy), (hx + 2, hy)], fill=shade(sleeve, .82), width=max(1, int(w) // 3))
    if not nohand:
        d.ellipse([hx - hand, hy - hand * .85, hx + hand, hy + hand * .85], fill=skin)
        d.point((hx - 1, hy - 1), fill=shade(skin, 1.08))
    lay = outline(lay, shade(sleeve, .5))
    c.im.alpha_composite(lay)

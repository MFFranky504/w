"""Escena de prueba del estilo GBA (horizontal 320x180 o vertical 160x284 según TC_LAND)."""
import math
from PIL import Image
from lib import WW, WH, Canvas, vgrad, ease
import gba as G
from scenes3 import rpg, bat
from scenes2 import bust
LAND = WW > WH
FLY = 140 if LAND else 222                   # línea de suelo (cima del pasto)


def _world(c, t, cam=0.0, mood='day'):
    day = mood == 'day'
    G.sky(c, [(0, (88, 150, 238) if day else (24, 26, 74)), (.6, (150, 200, 250) if day else (60, 46, 110)), (1, (236, 240, 250) if day else (120, 70, 120))], 0, FLY, bands=8)
    if not day:
        for i in range(40): c.d.point(((i * 53) % WW, (i * 29) % int(FLY * .5)), fill=(240, 240, 255))
        c.d.ellipse([WW - 60, 14, WW - 40, 34], fill=(250, 246, 214))
    G.clouds(c, t, int(FLY * .12) if LAND else 40, (250, 252, 255) if day else (120, 110, 170), n=5 if LAND else 3, seed=2, speed=1.4, scale=1.0 if LAND else .7)
    skyc = (190, 220, 250) if day else (70, 56, 120)
    G.mountains(c, int(FLY * .78), int(FLY * .42), (150, 176, 222) if day else (70, 70, 130), seed=4, off=cam * .2, snow=(250, 252, 255))
    G.haze(c, 0, int(FLY * .8), skyc, .3)                                   # lo más lejano, más claro
    G.mountains(c, int(FLY * .9), int(FLY * .3), (104, 150, 176) if day else (52, 60, 100), seed=9, off=cam * .35)
    G.haze(c, int(FLY * .55), int(FLY * .92), skyc, .15)
    G.meadow(c, int(FLY * .97), int(FLY * .1), (120, 196, 110) if day else (50, 90, 90), seed=3, off=cam * .45)
    G.tree_line(c, int(FLY * .98), (72, 158, 98) if day else (40, 80, 80), seed=6, off=cam * .55, size=12)
    G.blocks(c, -int(cam % 16) - 16, FLY, WW + 48, WH - FLY + 4, (196, 132, 82) if day else (110, 90, 100), tile=16, seed=11, grass=(102, 206, 86) if day else (60, 120, 90), t=t)


def frame(t, u, mood='day', shot='wide'):
    c = Canvas(vgrad([(0, '#000000'), (1, '#000000')])); cam = t * 8
    _world(c, t, cam, mood)
    if shot == 'wide':
        G.place(c, rpg('gdt_y', int(t * 4) % 2), WW * (.38 if LAND else .3) + math.sin(t * .6) * (10 if LAND else 4), FLY + 2)
        G.place(c, rpg('you', int(t * 4 + 1) % 2), WW * (.6 if LAND else .72), FLY + 2, flip=True)
    elif shot == 'close':                                                  # retrato con acabado GBA sobre el mismo mundo
        b = bust('gdt_y', 'worry' if mood == 'dark' else 'smile', (0, 0), t, 1.75 if LAND else 1.3)
        sp = G.sprite(b); c.im.alpha_composite(sp, (int(WW / 2 - sp.width / 2), int(WH - sp.height + (6 if LAND else 0))))
    else:
        G.place(c, bat('gdt_y', 'hold'), WW * .3, FLY + 24 if LAND else FLY + 30)
        G.place(c, bat('you', 'stand'), WW * .7, FLY + 24 if LAND else FLY + 30, flip=True)
    c.amb = (1.0, 1.0, 1.0); c.vig = .35
    return G.grade(c.render(), mood)

"""Fondos: sala (día/noche) con TV, sillón, mesa y latas."""
import math
from .pixel import W, H, OL, WHITE, shade, ptext

DAY = dict(wall=(92, 104, 176), wall2=(104, 118, 192), floor=(158, 108, 76), floor2=(140, 94, 66),
           couch=(176, 70, 84), rug=(70, 150, 150))
NIGHT = dict(wall=(26, 28, 60), wall2=(32, 34, 72), floor=(60, 44, 52), floor2=(52, 38, 46),
             couch=(84, 40, 62), rug=(34, 70, 84))


def room(d, t, score=(0, 14), verdict="DERROTA", night=False, cans=0, label="K / D", clock=True):
    p = NIGHT if night else DAY
    d.rectangle([0, 0, W, 330], fill=p["wall"])
    for x in range(0, W, 30):
        d.rectangle([x, 0, x + 14, 330], fill=p["wall2"])
    d.rectangle([0, 318, W, 330], fill=shade(p["wall"], 0.7))
    d.rectangle([0, 330, W, H], fill=p["floor"])
    for y in range(344, H, 16):
        d.rectangle([0, y, W, y + 1], fill=p["floor2"])
    # ventana
    d.rectangle([10, 100, 66, 170], fill=OL)
    sky = (14, 16, 48) if night else (130, 205, 255)
    d.rectangle([13, 103, 63, 167], fill=sky)
    if night:
        d.rectangle([44, 112, 54, 122], fill=(250, 240, 180))
        for sx, sy in ((20, 112), (30, 140), (50, 150), (24, 156)):
            d.rectangle([sx, sy, sx + 1, sy + 1], fill=WHITE)
    else:
        cx = 14 + int(t * 6) % 70 - 14
        d.rectangle([cx, 120, cx + 22, 128], fill=WHITE); d.rectangle([cx + 6, 114, cx + 16, 120], fill=WHITE)
        d.rectangle([48, 108, 58, 118], fill=(255, 230, 90))
    d.rectangle([37, 103, 38, 167], fill=OL); d.rectangle([13, 134, 63, 135], fill=OL)
    # reloj
    if clock:
        d.rectangle([222, 100, 252, 130], fill=OL); d.rectangle([224, 102, 250, 128], fill=(240, 240, 230))
        a = t * (9 if night else 0.4)
        d.line([237, 115, 237 + 10 * math.sin(a), 115 - 10 * math.cos(a)], fill=OL, width=1)
        d.line([237, 115, 237 + 6 * math.sin(a / 12), 115 - 6 * math.cos(a / 12)], fill=(200, 40, 40), width=1)
    # póster
    d.rectangle([206, 150, 254, 196], fill=OL); d.rectangle([208, 152, 252, 194], fill=(40, 120, 90))
    d.rectangle([224, 160, 236, 184], fill=(230, 230, 240)); d.rectangle([228, 184, 232, 190], fill=(150, 80, 40))
    d.rectangle([214, 156, 218, 160], fill=(255, 220, 80))
    # TV
    d.rectangle([76, 108, 194, 190], fill=OL); d.rectangle([80, 112, 190, 186], fill=(60, 60, 78))
    good = score[0] > score[1]
    scr = (22, 70, 40) if good else (60, 22, 30)
    if night:
        scr = (30, 60, 110)
    d.rectangle([84, 116, 186, 182], fill=scr)
    for y in range(116, 182, 4):
        d.rectangle([84, y, 186, y], fill=shade(scr, 0.8))
    col = (110, 255, 140) if good else (255, 110, 110)
    ptext(d, (135, 126), verdict, 12, col)
    ptext(d, (135, 143), label, 9, (230, 230, 255))
    ptext(d, (135, 162), f"{score[0]} - {score[1]}", 22, WHITE)
    if int(t * 3) % 2 == 0 and not night:
        d.rectangle([88, 120, 92, 124], fill=col)
    if night:   # resplandor del TV
        d.rectangle([76, 190, 194, 194], fill=(60, 90, 160))
    # sillón
    c = p["couch"]
    d.rectangle([0, 262, W, 330], fill=OL); d.rectangle([4, 266, W - 4, 330], fill=shade(c, 0.85))
    # (los personajes se dibujan encima; el frente va después con couch_front)
    # mesa baja
    d.rectangle([40, 392, 230, 404], fill=OL); d.rectangle([42, 394, 228, 402], fill=(120, 84, 60))
    d.rectangle([48, 404, 54, 420], fill=OL); d.rectangle([216, 404, 222, 420], fill=OL)
    # alfombra
    d.rectangle([20, 420, 250, 470], fill=p["rug"])


def couch_front(d, night=False):
    c = (NIGHT if night else DAY)["couch"]
    d.rectangle([0, 318, W, 380], fill=OL)
    d.rectangle([4, 322, W - 4, 376], fill=c)
    d.rectangle([4, 322, W - 4, 330], fill=shade(c, 1.2))
    for x in (66, 132, 198):
        d.rectangle([x, 330, x + 1, 376], fill=shade(c, 0.7))
    d.rectangle([0, 300, 14, 380], fill=OL); d.rectangle([2, 304, 12, 376], fill=shade(c, 0.9))
    d.rectangle([W - 14, 300, W, 380], fill=OL); d.rectangle([W - 12, 304, W - 2, 376], fill=shade(c, 0.9))


def table_items(d, cans=0, pizza=True):
    if pizza:
        d.rectangle([56, 384, 90, 392], fill=OL); d.rectangle([58, 385, 88, 391], fill=(220, 160, 60))
    colors = [(60, 220, 120), (255, 80, 80), (80, 180, 255)]
    for i in range(cans):
        row, col = divmod(i, 8)
        x = 104 + col * 15
        y = 384 - row * 10
        d.rectangle([x, y, x + 9, y + 9], fill=OL)
        d.rectangle([x + 1, y + 1, x + 8, y + 8], fill=colors[i % 3])
        d.rectangle([x + 2, y + 1, x + 3, y + 8], fill=(255, 255, 255))


def confetti(d, t, n=40):
    cols = [(255, 220, 80), (255, 90, 120), (90, 220, 255), (140, 255, 140)]
    for i in range(n):
        x = (i * 53) % W
        y = int((t * 90 + i * 37) % 340) + 20
        d.rectangle([x, y, x + 3, y + 3], fill=cols[i % 4])

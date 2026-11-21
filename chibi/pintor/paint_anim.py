import math
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
import paint as ch

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
SCALE = 4
W, H, K = ch.W, ch.H, ch.K
SPARK = {'w': (255, 255, 255, 255), 'y': (255, 134, 178, 255), 'g': (255, 217, 74, 255), 'o': (26, 16, 36, 255)}
SHAPES = {
    1: ["oyo", "ywy", "oyo"],
    2: [".oyo.", "oyyyo", "yywyy", "oyyyo", ".oyo."],
    3: ["..oyo..", "..oyo..", "ooyyyoo", "yyywyyy", "ooyyyoo", "..oyo..", "..oyo.."],
}


def sparkle(img, px, py, size, gold=False):
    if size == 0:
        return
    rows = SHAPES[size]
    h, w = len(rows), len(rows[0])
    x0, y0 = int(round(px)) - w // 2, int(round(py)) - h // 2
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c == '.':
                continue
            X, Y = x0 + i, y0 + j
            if 0 <= X < W and 0 <= Y < H and img[Y, X, 3] == 0:
                img[Y, X] = SPARK['g' if (gold and c == 'y') else c]


def canvas_screen(phi, du, dv):
    p = ch.canvas_point(du, dv, off=3.0)
    wx = (p[0] - ch.XC) * math.cos(phi) + p[2] * math.sin(phi)
    return (wx + ch.PIV) * K, p[1] * K


def heart_at(progress):
    i = int(round(np.clip(progress, 0, 1) * (len(ch.HEART_PTS) - 1)))
    return tuple(ch.HEART_PTS[i])


def save(frames, durs, name):
    ims = [Image.fromarray(f).resize((W * SCALE, H * SCALE), Image.NEAREST) for f in frames]
    ims[0].save(f'{OUT}/{name}.png', save_all=True, append_images=ims[1:], duration=durs, loop=0,
                disposal=1, blend=0)
    sheet = Image.new('RGBA', (W * len(frames), H))
    for i, f in enumerate(frames):
        sheet.paste(Image.fromarray(f), (i * W, 0))
    sheet.save(f'{OUT}/{name}_spritesheet_{W}x{H}.png')
    sheet.resize((W * len(frames) * SCALE, H * SCALE), Image.NEAREST).save(f'{OUT}/{name}_spritesheet_x{SCALE}.png')


SPOTS = [(-1.25, 1.2, 0), (1.3, 1.15, 2), (1.35, -0.7, 4), (-1.3, -0.9, 1)]

# ---- A) turntable: the whole scene spins while the heart gets painted
N = 24
frames, durs = [], []
for i in range(N):
    phi = 2 * math.pi * i / N
    psi = (math.degrees(phi) + 55) % 360
    if psi < 180:
        prog = min(1.0, psi / 140)
    else:
        prog = 1.0
    hu, hv = heart_at(prog)
    if prog >= 1.0:                       # idle dabbing once the heart is done
        hu, hv = 0.22 + 0.05 * math.sin(i * 1.7), 0.33 + 0.04 * math.cos(i * 2.3)
    f = ch.render(phi, progress=prog if psi < 180 else 1.0, dab=(hu, hv)).copy()
    if 140 <= psi < 180:
        k = int((psi - 140) // 13)
        for j, (du, dv, ph) in enumerate(SPOTS):
            sx, sy = canvas_screen(phi, du, dv)
            sparkle(f, sx, sy, [1, 2, 3, 2][(k + ph) % 4], gold=j % 2 == 1)
    frames.append(f)
    durs.append(80)
save(frames, durs, 'chibi_pintor_girando')

# ---- B) static: painting the heart in 3/4 view, then a little sparkle, then a fresh canvas
phi = math.radians(20)
NP, NH = 20, 6
frames, durs = [], []
for i in range(NP + NH):
    prog = min(1.0, i / (NP - 1))
    if i < NP:
        hu, hv = heart_at(prog)
    else:
        hu, hv = 0.22 + 0.05 * math.sin(i * 1.7), 0.33 + 0.04 * math.cos(i * 2.3)
    f = ch.render(phi, progress=prog, dab=(hu, hv)).copy()
    if i >= NP:
        k = i - NP
        for j, (du, dv, ph) in enumerate(SPOTS):
            sx, sy = canvas_screen(phi, du, dv)
            sparkle(f, sx, sy, [1, 2, 3, 2, 1, 0][(k + ph) % 6], gold=j % 2 == 1)
    frames.append(f)
    durs.append(90 if i < NP else 120)
save(frames, durs, 'chibi_pintor')
print('ok', W * SCALE, H * SCALE)

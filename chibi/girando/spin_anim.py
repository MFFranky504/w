import math
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
import spin

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
N = 16
SCALE = 4
W, H, K = spin.W, spin.H, spin.K

SPARK = {'w': (255, 255, 255, 255), 'y': (255, 214, 92, 255), 'o': (28, 18, 41, 255)}
SHAPES = {
    1: ["oyo", "ywy", "oyo"],
    2: [".oyo.", "oyyyo", "yywyy", "oyyyo", ".oyo."],
    3: ["..oyo..", "..oyo..", "ooyyyoo", "yyywyyy", "ooyyyoo", "..oyo..", "..oyo.."],
}
# (x, y) in model units, phase offset
SPARKLES = [(14, 22, 0), (106, 30, 5), (108, 78, 10), (12, 70, 13)]
CYCLE = [0, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def sparkle(img, ux, uy, size):
    if size == 0:
        return
    rows = SHAPES[size]
    h, w = len(rows), len(rows[0])
    x0 = int(round(ux * K)) - w // 2
    y0 = int(round(uy * K)) - h // 2
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == '.':
                continue
            X, Y = x0 + i, y0 + j
            if 0 <= X < W and 0 <= Y < H and img[Y, X, 3] == 0:
                img[Y, X] = SPARK[ch]


frames = []
for i in range(N):
    phi = 2 * math.pi * i / N
    hop_px = round(3 * abs(math.sin(2 * math.pi * i / N)))
    arm = 25 + 11 * math.sin(4 * math.pi * i / N)
    f = spin.render(phi, hop=hop_px / K, arm=arm).copy()
    for sx, sy, ph in SPARKLES:
        sparkle(f, sx, sy, CYCLE[(i + ph) % N])
    frames.append(f)

ims = [Image.fromarray(f).resize((W * SCALE, H * SCALE), Image.NEAREST) for f in frames]
ims[0].save(f'{OUT}/chibi_girando.png', save_all=True, append_images=ims[1:],
            duration=65, loop=0, disposal=1, blend=0)

sheet = Image.new('RGBA', (W * N, H))
for i, f in enumerate(frames):
    sheet.paste(Image.fromarray(f), (i * W, 0))
sheet.save(f'{OUT}/chibi_girando_spritesheet_{W}x{H}.png')
sheet.resize((W * N * SCALE, H * SCALE), Image.NEAREST).save(f'{OUT}/chibi_girando_spritesheet_x{SCALE}.png')
ims[0].save(f'{OUT}/chibi_girando_frente.png')
print('ok', W * SCALE, H * SCALE)

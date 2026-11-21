import math
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
import pinky as ch

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
N = 16
SCALE = 4
W, H, K = ch.W, ch.H, ch.K

SPARK = {'w': (255, 255, 255, 255), 'y': (255, 134, 178, 255), 'o': (26, 16, 36, 255)}
SHAPES = {
    1: ["oyo", "ywy", "oyo"],
    2: [".oyo.", "oyyyo", "yywyy", "oyyyo", ".oyo."],
    3: ["..oyo..", "..oyo..", "ooyyyoo", "yyywyyy", "ooyyyoo", "..oyo..", "..oyo.."],
}
SPARKLES = [(12, 18, 0), (112, 26, 5), (114, 80, 10), (10, 74, 13)]
CYCLE = [0, 1, 2, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def sparkle(img, ux, uy, size):
    if size == 0:
        return
    rows = SHAPES[size]
    h, w = len(rows), len(rows[0])
    x0 = int(round(ux * K)) - w // 2
    y0 = int(round(uy * K)) - h // 2
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c == '.':
                continue
            X, Y = x0 + i, y0 + j
            if 0 <= X < W and 0 <= Y < H and img[Y, X, 3] == 0:
                img[Y, X] = SPARK[c]


frames = []
for i in range(N):
    phi = 2 * math.pi * i / N
    hop_px = round(3 * abs(math.sin(2 * math.pi * i / N)))
    wave = 9 * math.sin(4 * math.pi * i / N)
    f = ch.render(phi, hop=hop_px / K, wave=wave).copy()
    for sx, sy, ph in SPARKLES:
        sparkle(f, sx, sy, CYCLE[(i + ph) % N])
    frames.append(f)

name = 'chibi_rosa_girando'
ims = [Image.fromarray(f).resize((W * SCALE, H * SCALE), Image.NEAREST) for f in frames]
ims[0].save(f'{OUT}/{name}.png', save_all=True, append_images=ims[1:], duration=65, loop=0,
            disposal=1, blend=0)
sheet = Image.new('RGBA', (W * N, H))
for i, f in enumerate(frames):
    sheet.paste(Image.fromarray(f), (i * W, 0))
sheet.save(f'{OUT}/{name}_spritesheet_{W}x{H}.png')
sheet.resize((W * N * SCALE, H * SCALE), Image.NEAREST).save(f'{OUT}/{name}_spritesheet_x{SCALE}.png')
ims[0].save(f'{OUT}/{name}_frente.png')
print('ok', W * SCALE, H * SCALE)

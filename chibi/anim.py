import sys
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
import sprite2 as sp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
SCALE = 5
BG = (232, 238, 252)
SHADOW = (205, 212, 236)

# 8-frame breathing cycle, played twice; blink in the second cycle
bdy = [0, 0, 1, 1, 1, 1, 0, 0]
hdy = [0, 0, 0, 1, 1, 1, 1, 0]
cdy = [hdy[i - 1] - hdy[i] for i in range(8)]          # cap ball lags one frame
eyes = ['open'] * 8 + ['open', 'open', 'open', 'half', 'closed', 'half', 'open', 'open']
spark = [0, 1, 2, 3, 2, 1, 0, 0] + [0] * 8
dur = [110] * 16
dur[11] = dur[13] = 50
dur[12] = 70

frames = []
for i in range(16):
    j = i % 8
    frames.append(sp.render(hdy=hdy[j], bdy=bdy[j], cdy=cdy[j], eyes=eyes[i], sparkle=spark[i]))

H, W = frames[0].shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
shadow = (((xx + 0.5 - 48) / 22) ** 2 + ((yy + 0.5 - 115.5) / 3.2) ** 2) <= 1


def flatten(f):
    out = np.zeros((H, W, 3), np.uint8)
    out[:] = BG
    out[shadow] = SHADOW
    a = f[..., 3] > 0
    out[a] = f[a, :3]
    return out


def to_gif(rgb_frames, path, transparent=False):
    # shared palette across frames
    cols = {}
    for f in rgb_frames:
        for c in np.unique(f.reshape(-1, f.shape[-1]), axis=0):
            cols.setdefault(tuple(int(v) for v in c), len(cols))
    assert len(cols) <= 256, len(cols)
    pal = [0] * 768
    for c, idx in cols.items():
        pal[idx * 3:idx * 3 + 3] = c[:3]
    ims = []
    for f in rgb_frames:
        flat = f.reshape(-1, f.shape[-1])
        idx = np.array([cols[tuple(int(v) for v in c)] for c in flat], np.uint8).reshape(H, W)
        im = Image.fromarray(idx, 'P')
        im.putpalette(pal)
        ims.append(im.resize((W * SCALE, H * SCALE), Image.NEAREST))
    kw = dict(save_all=True, append_images=ims[1:], duration=dur, loop=0, optimize=False, disposal=2)
    if transparent:
        kw['transparency'] = cols[(0, 0, 0, 0)]
    ims[0].save(path, **kw)


to_gif([flatten(f) for f in frames], f'{OUT}/chibi_pixelart.gif')

tr = []
for f in frames:
    g = f.copy()
    g[g[..., 3] == 0] = 0
    tr.append(g)
to_gif(tr, f'{OUT}/chibi_pixelart_transparente.gif', transparent=True)

# sprite sheet (1x, 16 frames in a row) for game use
sheet = Image.new('RGBA', (W * 16, H))
for i, f in enumerate(frames):
    sheet.paste(Image.fromarray(f), (i * W, 0))
sheet.save(f'{OUT}/chibi_spritesheet_96x120.png')
Image.fromarray(frames[0]).resize((W * 8, H * 8), Image.NEAREST).save(f'{OUT}/chibi_frame_x8.png')
print('ok', len(frames), 'frames')

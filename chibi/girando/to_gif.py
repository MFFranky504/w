"""Convert the animated PNG (APNG) into a transparent GIF."""
import sys
import numpy as np
from PIL import Image

src_path = sys.argv[1] if len(sys.argv) > 1 else 'chibi_girando.png'
out_path = sys.argv[2] if len(sys.argv) > 2 else 'chibi_girando.gif'
src = Image.open(src_path)
frames = []
for i in range(src.n_frames):
    src.seek(i)
    f = np.array(src.convert('RGBA'))
    f[f[..., 3] < 128] = 0
    f[f[..., 3] >= 128, 3] = 255
    frames.append(f)
H, W = frames[0].shape[:2]
cols = {(0, 0, 0, 0): 0}
for f in frames:
    for c in np.unique(f.reshape(-1, 4), axis=0):
        cols.setdefault(tuple(int(v) for v in c), len(cols))
assert len(cols) <= 256, len(cols)
pal = [0] * 768
for c, idx in cols.items():
    pal[idx * 3:idx * 3 + 3] = c[:3]
ims = []
for f in frames:
    idx = np.array([cols[tuple(int(v) for v in c)] for c in f.reshape(-1, 4)], np.uint8).reshape(H, W)
    im = Image.fromarray(idx, 'P')
    im.putpalette(pal)
    ims.append(im)
ims[0].save(out_path, save_all=True, append_images=ims[1:], duration=65, loop=0,
            transparency=0, disposal=2, optimize=False)
print(out_path, len(cols), 'colors')

"""Designed headline text for thumbnails: extrusion, chromatic ghosts, wear, scanlines, red halo.
All colours come from the engine palette; the pixel grid stays chunky (cells are multiples of the text scale)."""
import numpy as np
from PIL import Image, ImageFilter
from engine import P, C, layer, draw_text, text_width, BAYER


def _mask(size, x, y, s, scale, bold=True):
    lay = layer(*size)
    draw_text(lay, x, y, s, "white", scale, bold=bold)
    return np.array(lay)[..., 3] > 0


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    yd, xd = slice(max(0, -dy), min(h, h - dy)), slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = m[yd, xd]
    return out


def _dilate(m, r):
    out = m.copy()
    for dx in range(-r, r + 1, 2):
        for dy in range(-r, r + 1, 2):
            out |= _shift(m, dx, dy)
    return out


def _paint(a, m, color):
    a[m] = P[color] + (255,)


def fx_text(img, x, y, s, scale, ramp, glow_ramp=("red0", "red1", "red2"), ghost=("red2", "green2"),
            extrude=("red0", "red1"), seed=1, wear=0.07, extrude_n=None, scan=0.72, ghost_px=None, bold=True):
    """Draw `s` at (x, y) on RGBA `img` with the full treatment. Returns the text mask."""
    size = img.size
    w, h = size
    m = _mask(size, x, y, s, scale, bold)
    a = np.array(img)
    # 1. red halo (dithered, only brightens)
    blur = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(scale * 2.6))) / 255.0
    ys, xs = np.mgrid[0:h, 0:w]
    idx = np.floor(np.clip(blur * 1.9, 0, 1) * len(glow_ramp) + BAYER[ys % 4, xs % 4]).astype(int)
    cols = np.array([(0, 0, 0)] + [P[c] for c in glow_ramp], dtype=np.int32)[idx.clip(0, len(glow_ramp))]
    lum = lambda c: c[..., 0] * 3 + c[..., 1] * 6 + c[..., 2]
    ok = (idx > 0) & (lum(cols) > lum(a[..., :3].astype(np.int32)))
    a[..., :3][ok] = cols[ok].astype(np.uint8)
    # 2. black keyline behind everything
    _paint(a, _dilate(m, scale), "black")
    # 3. chromatic ghosts (red to the right, green to the left)
    d = ghost_px or max(4, scale)
    if ghost[1]:
        _paint(a, _shift(m, -d, -d // 2), ghost[1])
    if ghost[0]:
        _paint(a, _shift(m, d, d // 2), ghost[0])
    # 4. extrusion: stacked copies down-right, light to dark
    n = extrude_n or scale
    for i in range(n, 0, -1):
        _paint(a, _shift(m, i, i), extrude[0 if i > n // 2 else 1])
    # 5. face: vertical dithered gradient, worn away in chunky 3-px cells
    ys0, ys1 = np.nonzero(m)[0].min(), np.nonzero(m)[0].max()
    t = np.clip((ys - ys0) / max(1, ys1 - ys0), 0, 1)
    fi = np.floor(t * len(ramp) * 0.999 + (BAYER[ys % 4, xs % 4] - 0.5) * 0.8).astype(int).clip(0, len(ramp) - 1)
    face = np.array([P[c] for c in ramp], dtype=np.uint8)[fi]
    cell = 3
    rnd = np.random.RandomState(seed).rand(h // cell + 1, w // cell + 1)
    holes = np.kron(rnd < wear, np.ones((cell, cell), bool))[:h, :w]
    edge = m & ~_shift(m, 0, 4) | m & ~_shift(m, 4, 0)
    holes |= edge & np.kron(rnd < wear * 3.5, np.ones((cell, cell), bool))[:h, :w]
    face_m = m & ~holes
    a[..., :3][face_m] = face[face_m]
    a[..., 3][face_m] = 255
    # 6. scanlines: every 4th row darker inside the face
    row = (ys // 2) % 4 == 0
    dark = np.array([P[ramp[-1]]] * 1, dtype=np.uint8)[0]
    a[..., :3][face_m & row] = (a[..., :3][face_m & row] * scan).astype(np.uint8)
    img.paste(Image.fromarray(a))
    return m

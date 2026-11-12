"""Scene library for the Archivo Cero pixel engine.

Each scene is `name(t, lt, u, p) -> [(depth, RGBA image), ...]`:
  t  = episode time (s), lt = time inside the shot, u = shot progress 0..1,
  p  = shot params (already interpolated).
Depth 1.0 moves with the camera; < 1 is farther (moves less), > 1 is foreground.
Images are native-resolution (640x360 view) and may be larger to allow camera pans.
Static parts are cached with lru_cache; only animated parts are drawn per frame.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import C, P, W, H, snap, layer, ramp_fill, gradient, glow, mask_of, draw_text, text_width

WW, WH = 704, 396  # world size: view + room for a 64x36 px camera move

SKIN = ["skin0", "skin1", "skin2", "skin3", "skin4"]
HAIR = ["hair", "night0", "night1", "night2"]
SHIRT = ["night2", "night3", "night4", "night5", "night6"]
RIM_GREEN = ["green1", "green2", "green3"]


# ------------------------------------------------------------------ helpers
def rng(seed):
    return np.random.RandomState(seed)


def noise(w, h, cell, seed, octaves=3):
    """Smooth value noise 0..1 (deterministic)."""
    acc, amp, tot = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(octaves):
        c = max(1, cell >> o)
        g = rng(seed + o).rand(h // c + 2, w // c + 2).astype(np.float32)
        im = Image.fromarray(g, "F").resize(((w // c + 2) * c, (h // c + 2) * c), Image.BILINEAR)
        acc += np.array(im)[:h, :w] * amp
        tot += amp
        amp *= 0.5
    return acc / tot


def fill(img, mask, color):
    a = np.array(img)
    a[mask] = P[color] + (255,)
    img.paste(Image.fromarray(a))


def shade(img, mask, ramp, light=(-1.0, -0.3), bias=0.0, contrast=1.0, rim=None, rim_w=2):
    """Fill a mask with a dithered ramp lit from `light` (x, y direction the light comes FROM),
    plus an optional rim of coloured light on the lit edge."""
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    nx = (xx - x0) / max(1, x1 - x0) * 2 - 1
    ny = (yy - y0) / max(1, y1 - y0) * 2 - 1
    t = 0.5 + (nx * light[0] + ny * light[1]) * 0.5 * contrast + bias
    m = mask[y0:y1 + 1, x0:x1 + 1]
    ramp_fill(img, t, ramp, m, x0, y0)
    if rim:
        sh = np.zeros_like(m)
        k = rim_w
        if light[0] < 0:
            sh[:, k:] = m[:, :-k]
        else:
            sh[:, :-k] = m[:, k:]
        r = m & ~sh
        ramp_fill(img, np.full(m.shape, 0.55), rim, r, x0, y0)


def pts(ox, oy, s, seq):
    return [(ox + x * s, oy + y * s) for x, y in seq]


def rain(w, h, t, n=220, speed=420, length=9, slant=0.18, colors=("night5", "night6"), seed=1, alpha=255):
    im = layer(w, h)
    d = ImageDraw.Draw(im)
    r = rng(seed)
    x0, y0, sp = r.rand(n) * (w + 80) - 40, r.rand(n) * (h + 60), speed * (0.75 + r.rand(n) * 0.5)
    for i in range(n):
        y = (y0[i] + sp[i] * t) % (h + 60) - 30
        x = x0[i] + slant * y
        d.line([(x, y), (x + slant * length, y + length)], fill=C(colors[i % len(colors)], alpha))
    return im


def splashes(im, t, region, n=40, seed=3, color="night6"):
    """Tiny rain splashes on a wet floor: each lives 0.15 s at a random spot."""
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = region
    period = 0.6
    for i in range(n):
        ph = (t + i * period / n) % period
        k = int((t + i * period / n) // period)
        r = rng(seed * 1000 + i * 31 + k)
        x, y = x0 + r.rand() * (x1 - x0), y0 + r.rand() * (y1 - y0)
        if ph < 0.15:
            s = 1 + int(ph / 0.05)
            d.point([(x - s, y), (x + s, y), (x, y - 1)], fill=C(color))


# ------------------------------------------------------------------ the controller
def head(img, ox, oy, s, t, p):
    """Stylised 3/4 head facing left, lit green from the left (radar screen).
    s = head height in px (crown to chin). p: brows 0..1 (worry), look -1..1, wide 0..1,
    talk 0..1, blink (auto every few seconds unless blink=False), headset (bool)."""
    size = img.size
    M = lambda seq: mask_of(size, lambda d: d.polygon(pts(ox, oy, s, seq), fill=1))
    E = lambda cx, cy, rx, ry: mask_of(size, lambda d: d.ellipse([ox + (cx - rx) * s, oy + (cy - ry) * s,
                                                                 ox + (cx + rx) * s, oy + (cy + ry) * s], fill=1))
    rim_w = max(1, round(s / 40))

    # neck and shirt (bust=False when a body is drawn separately)
    neck = M([(0.28, 0.80), (0.58, 0.80), (0.62, 1.14), (0.30, 1.14)])
    shade(img, neck, SKIN, bias=-0.35, rim=RIM_GREEN, rim_w=rim_w)
    shirt = np.zeros((size[1], size[0]), bool) if not p.get("bust", True) else M([(-0.15, 1.40), (-0.05, 1.12), (0.18, 1.02), (0.38, 1.12), (0.64, 1.00), (0.98, 1.10), (1.12, 1.40)])
    shade(img, shirt, SHIRT, bias=0.05, rim=RIM_GREEN, rim_w=rim_w)
    collar = M([(0.18, 1.02), (0.34, 1.16), (0.40, 1.12), (0.30, 0.98)]) | M([(0.40, 1.12), (0.48, 1.18), (0.66, 1.02), (0.58, 0.96)])
    shade(img, collar, ["night5", "night6", "night7", "paper"], bias=0.1)
    tie = M([(0.38, 1.12), (0.46, 1.12), (0.48, 1.40), (0.34, 1.40)])
    shade(img, tie, ["red0", "red1", "red2"], bias=-0.1)

    # face, ear, hair
    face = M([(0.14, 0.18), (0.10, 0.36), (0.09, 0.42), (0.03, 0.555), (0.09, 0.60), (0.11, 0.66), (0.10, 0.71),
              (0.15, 0.86), (0.26, 0.95), (0.48, 0.90), (0.66, 0.72), (0.68, 0.44), (0.62, 0.22), (0.38, 0.12)])
    shade(img, face, SKIN, light=(-1.0, 0.1), bias=0.02, contrast=1.15, rim=RIM_GREEN, rim_w=rim_w)
    # jaw and under-chin shadow
    shade(img, M([(0.20, 0.90), (0.48, 0.86), (0.60, 0.76), (0.50, 0.92), (0.26, 0.97)]) & face, SKIN, bias=-0.45)
    ear = E(0.70, 0.50, 0.06, 0.09)
    shade(img, ear, SKIN, bias=-0.2)
    hair = M([(0.11, 0.25), (0.17, 0.10), (0.34, 0.02), (0.56, 0.02), (0.75, 0.10), (0.85, 0.27), (0.84, 0.47),
              (0.78, 0.63), (0.68, 0.62), (0.66, 0.40), (0.60, 0.26), (0.42, 0.18), (0.22, 0.21)])
    shade(img, hair, HAIR, light=(-1.0, -0.6), bias=-0.05, rim=["green0", "green1", "green2"], rim_w=rim_w)

    # cheek shadow beside the nose, nostril, tired under-eye
    shade(img, M([(0.11, 0.43), (0.18, 0.56), (0.13, 0.615), (0.10, 0.58)]) & face, SKIN, bias=-0.35)
    shade(img, M([(0.28, 0.475), (0.46, 0.47), (0.42, 0.50), (0.31, 0.505)]) & face, SKIN, bias=-0.3)

    blink = p.get("blink", True) and (t % 3.7) < 0.13
    wide = p.get("wide", 0.0)
    look = p.get("look", 0.0)
    for cx, cy, rx, ry, ir in ((0.175, 0.435, 0.035, 0.018, 0.016), (0.36, 0.435, 0.062, 0.026, 0.026)):
        ry2 = ry * (1 + 0.6 * wide)
        if blink:
            fill(img, M([(cx - rx, cy), (cx + rx, cy), (cx + rx, cy + 0.012), (cx - rx, cy + 0.012)]), "skin0")
            continue
        white = M([(cx - rx, cy + 0.004), (cx - rx * 0.3, cy - ry2), (cx + rx * 0.5, cy - ry2 * 0.95),
                   (cx + rx, cy + 0.002), (cx + rx * 0.3, cy + ry2 * 0.85), (cx - rx * 0.5, cy + ry2 * 0.8)])
        fill(img, white, "night7")
        ix = cx + look * rx * 0.45 - rx * 0.15
        iris = E(ix, cy + 0.002 - 0.004 * wide, ir, ir) & white
        fill(img, iris, "hair")
        if s > 60:
            fill(img, E(ix, cy, ir * 0.45, ir * 0.45) & white, "black")
            fill(img, E(ix - ir * 0.35, cy - ir * 0.35, ir * 0.22, ir * 0.22) & white, "green3")
        # upper lid
        fill(img, M([(cx - rx * 1.1, cy - ry2 * 0.2), (cx - rx * 0.3, cy - ry2 - 0.012), (cx + rx * 0.5, cy - ry2 * 0.95 - 0.012),
                     (cx + rx * 1.1, cy), (cx + rx * 0.5, cy - ry2 * 0.95), (cx - rx * 0.3, cy - ry2)]), "hair")
    b = p.get("brows", 0.0)
    for (x0, y0, x1, y1, inner_left) in ((0.12, 0.370, 0.225, 0.358, False), (0.29, 0.355, 0.47, 0.372, True)):
        lift = -0.035 * b
        y0b, y1b = (y0 + lift, y1) if inner_left else (y0, y1 + lift)
        fill(img, M([(x0, y0b), (x1, y1b), (x1, y1b + 0.022), (x0, y0b + 0.026)]), "hair")

    # moustache and mouth
    fill(img, M([(0.075, 0.625), (0.13, 0.612), (0.26, 0.632), (0.30, 0.668), (0.24, 0.676), (0.12, 0.664), (0.08, 0.66)]), "hair")
    talk = p.get("talk", 0.0) * (0.5 + 0.5 * math.sin(t * 17.0)) * (0.6 + 0.4 * math.sin(t * 5.3))
    if talk > 0.15:
        fill(img, E(0.165, 0.705, 0.06, 0.012 + 0.02 * talk), "skin0")
    else:
        fill(img, M([(0.11, 0.704), (0.24, 0.700), (0.24, 0.708), (0.11, 0.712)]), "skin0")

    if p.get("headset", True):
        d = ImageDraw.Draw(img)
        w = max(1, round(s * 0.03))
        d.arc([ox + 0.36 * s, oy - 0.06 * s, ox + 1.02 * s, oy + 1.00 * s], 205, 330, fill=C("night1"), width=w)
        cup = E(0.70, 0.50, 0.075, 0.11)
        shade(img, cup, ["night0", "night1", "night2", "night4"], rim=["night4", "night5"], rim_w=rim_w)
        d.line(pts(ox, oy, s, [(0.66, 0.60), (0.50, 0.70), (0.30, 0.74), (0.22, 0.73)]), fill=C("night1"),
               width=max(1, round(s * 0.018)), joint="curve")
        fill(img, E(0.205, 0.728, 0.032, 0.026), "night0")


def body_seated(img, ox, oy, s):
    """Torso and arm for the medium tower shot (head drawn separately). s = head height."""
    size = img.size
    M = lambda seq: mask_of(size, lambda d: d.polygon(pts(ox, oy, s, seq), fill=1))
    back = M([(0.05, 1.05), (0.70, 0.98), (1.15, 1.20), (1.25, 2.6), (0.05, 2.6)])
    shade(img, back, SHIRT, bias=0.0, rim=RIM_GREEN, rim_w=max(1, round(s / 30)))
    arm = M([(0.10, 1.12), (0.42, 1.15), (0.38, 2.05), (-0.70, 2.36), (-0.78, 2.22), (0.02, 1.95)])
    shade(img, arm, SHIRT, light=(-1.0, -0.8), bias=0.12, rim=RIM_GREEN, rim_w=max(1, round(s / 30)))
    hand = M([(-0.95, 2.22), (-0.70, 2.20), (-0.66, 2.36), (-0.96, 2.38)])
    shade(img, hand, SKIN, bias=0.1, rim=RIM_GREEN, rim_w=1)


# ------------------------------------------------------------------ shared backdrops
@lru_cache(maxsize=None)
def night_exterior(w=WW, h=WH, horizon=215, lights_y=222, seed=7):
    """Sky, clouds, El Ávila-like mountain silhouette, city glow, airfield light rows. Static."""
    im = layer(w, h)
    gradient(im, (0, 0, w, horizon), ["night0", "night1", "night2", "night3"])
    n = noise(w, horizon, 48, seed)
    t = (n - 0.45) * 2.2
    t[t < 0.15] = -1
    ramp_fill(im, t * 0.8, ["night2", "night3", "night4"], None, 0, 0)
    # mountain silhouette (generic coastal ridge)
    xs = np.arange(w)
    ridge = horizon - 30 - 70 * np.exp(-((xs - w * 0.62) / (w * 0.22)) ** 2) - 18 * noise(w, 1, 32, seed + 5)[0]
    yy = np.arange(h)[:, None]
    mt = (yy >= ridge[None, :]) & (yy < horizon + 4)
    fill(im, mt, "night1")
    d = ImageDraw.Draw(im)
    r = rng(seed + 9)
    for _ in range(140):  # town lights at the foot of the mountain
        x = r.rand() * w
        y = horizon - 2 - r.rand() * 12
        if y > ridge[int(x)]:
            d.point((x, y), fill=C(["lamp3", "lamp2", "paper"][r.randint(3)]))
    fill(im, (yy >= horizon) & np.ones((1, w), bool), "night0")
    gradient(im, (0, horizon, w, h), ["night1", "night0", "black"])
    for i in range(48):  # runway edge light row
        x = 20 + i * (w - 40) / 47
        d.point((x, lights_y), fill=C("lamp4" if i % 2 else "white"))
    for i in range(18):
        d.point((40 + i * 37, lights_y + 9), fill=C("green3" if i % 3 else "lamp3"))
    return im


# ------------------------------------------------------------------ scenes
@lru_cache(maxsize=None)
def _tower_room():
    im = layer(WW, WH)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, WW, 26], fill=C("night0"))
    d.rectangle([0, 196, WW, WH], fill=C("night1"))
    gradient(im, (0, 196, WW, 262), ["night2", "night1", "night0"])
    for i in range(7):  # slanted window mullions of the tower cab
        x = -30 + i * 125
        d.polygon([(x, 26), (x + 12, 26), (x + 4, 196), (x - 8, 196)], fill=C("night0"))
        d.line([(x + 11, 26), (x + 3, 196)], fill=C("night2"))
    d.rectangle([0, 192, WW, 198], fill=C("night0"))
    d.rectangle([0, 22, WW, 27], fill=C("night0"))
    return im


@lru_cache(maxsize=None)
def _tower_desk():
    im = layer(WW, WH)
    d = ImageDraw.Draw(im)
    d.polygon([(0, 262), (WW, 262), (WW, 300), (0, 300)], fill=C("night3"))
    gradient(im, (0, 262, WW, 300), ["night4", "night3", "night2"])
    d.rectangle([0, 300, WW, WH], fill=C("night1"))
    gradient(im, (0, 300, WW, WH), ["night2", "night1", "night0"])
    d.line([(0, 300), (WW, 300)], fill=C("night5"))
    for y in (318, 348, 372):
        d.line([(0, y), (WW, y)], fill=C("night0"))
    # scope bezel (an elliptical scope set into the desk, seen at an angle)
    d.ellipse([196, 262, 304, 298], fill=C("night0"))
    d.ellipse([200, 264, 300, 296], fill=C("night4"))
    # papers and a mug (no text)
    d.polygon([(470, 270), (532, 266), (540, 288), (476, 292)], fill=C("night6"))
    d.polygon([(476, 268), (536, 270), (532, 290), (470, 286)], fill=C("night5"))
    d.rectangle([590, 252, 606, 276], fill=C("night4"))
    d.rectangle([606, 258, 611, 270], outline=C("night4"))
    return im


def _scope_ellipse(im, cx, cy, rx, ry, t, blip=None, sweep_period=4.0):
    """Elliptical radar scope with a rotating sweep and phosphor afterglow."""
    x0, y0 = int(cx - rx), int(cy - ry)
    yy, xx = np.mgrid[y0:int(cy + ry) + 1, x0:int(cx + rx) + 1]
    nx, ny = (xx - cx) / rx, (yy - cy) / ry
    r = np.sqrt(nx ** 2 + ny ** 2)
    inside = r <= 1
    ang = np.arctan2(ny, nx)
    sweep = (t / sweep_period * 2 * math.pi) % (2 * math.pi) - math.pi
    behind = (sweep - ang) % (2 * math.pi)
    v = np.clip(1 - behind / 1.6, 0, 1) * 0.85
    v += ((np.abs(r - 0.33) < 0.035) | (np.abs(r - 0.66) < 0.03)) * 0.25
    if blip:
        bx, by, since = blip
        db = np.sqrt((nx - bx) ** 2 + ((ny - by) * 1.0) ** 2)
        bang = math.atan2(by, bx)
        age = ((sweep - bang) % (2 * math.pi)) / (2 * math.pi) * sweep_period
        if since >= 0:
            v = np.maximum(v, (db < 0.04) * (1.0 - min(age, sweep_period) / sweep_period * 0.7))
    ramp_fill(im, np.where(inside, v, -1), ["green0", "green1", "green2", "green3"], inside, x0, y0)


def tower(t, lt, u, p):
    """Control tower cab at night. p: person (bool), brows, look, talk, blip_at (u when the
    unknown contact appears on the scope), headset_on_desk."""
    ext = night_exterior()
    out = [(0.5, ext), (0.5, rain(WW, WH, t, n=120, speed=300, length=6, colors=("night3", "night4"), seed=2))]
    im = _tower_room().copy()
    # glass: faint reflections and slow droplets
    d = ImageDraw.Draw(im)
    r = rng(11)
    for i in range(70):
        x = r.rand() * WW
        y = 30 + (r.rand() * 160 + (t * (6 + 10 * r.rand()) if i % 3 == 0 else 0)) % 162
        d.point([(x, y), (x, y + 1)], fill=C("night5", 255))
    im.alpha_composite(_tower_desk())
    blip_at = p.get("blip_at")
    blip = (0.45, -0.45, (u - blip_at) if blip_at is not None else -1) if blip_at is not None else None
    _scope_ellipse(im, 250, 280, 48, 15, t, blip)
    glow(im, 250, 282, 64, ["night3", "green0", "green1"], strength=0.5, sy=0.3)
    if p.get("person", True):
        s = 48
        hx, hy = 448, 150
        body_seated(im, hx, hy, s)
        head(im, hx, hy, s, t, dict(p, bust=False))
        im.alpha_composite(_tower_desk().crop((0, 262, WW, WH)), (0, 262))
        _scope_ellipse(im, 250, 280, 48, 15, t, blip)
    elif p.get("headset_on_desk", True):
        d = ImageDraw.Draw(im)
        d.arc([420, 250, 470, 290], 180, 360, fill=C("night1"), width=3)
        d.ellipse([414, 266, 428, 282], fill=C("night2"))
        d.ellipse([462, 266, 476, 282], fill=C("night2"))
        # empty chair back behind the desk
        chair = mask_of(im.size, lambda dd: dd.rounded_rectangle([492, 168, 566, 262], radius=14, fill=1))
        shade(im, chair, ["black", "night0", "night1", "night2"], light=(-1, -0.5), rim=RIM_GREEN, rim_w=2)
        d.rectangle([524, 262, 532, 270], fill=C("night0"))
    # console LEDs
    d = ImageDraw.Draw(im)
    for i in range(22):
        x = 40 + i * 29
        on = (int(t * (1.3 + (i % 5) * 0.4) + i) % 3) != 0
        d.point((x, 330), fill=C(["green3", "lamp3", "red2"][i % 3] if on else "night0"))
    out.append((1.0, im))
    fg = layer(WW + 80, WH)
    ImageDraw.Draw(fg).polygon([(0, WH), (0, 300), (60, 292), (120, 330), (130, WH)], fill=C("black"))
    out.append((1.25, fg))
    return out


def radar(t, lt, u, p):
    """Close-up of the scope. p: blip_at (u)."""
    im = layer(WW, WH)
    d = ImageDraw.Draw(im)
    gradient(im, (0, 0, WW, WH), ["night0", "night1", "night0"])
    cx, cy, R = 352, 198, 168
    d.ellipse([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], fill=C("night2"))
    d.ellipse([cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8], fill=C("night0"))
    blip_at = p.get("blip_at")
    blip = (0.45, -0.42, u - blip_at) if blip_at is not None else None
    _scope_ellipse(im, cx, cy, R, R, t, blip, sweep_period=4.0)
    for a in range(0, 360, 30):
        x, y = cx + math.cos(math.radians(a)) * (R + 13), cy + math.sin(math.radians(a)) * (R + 13)
        d.point((x, y), fill=C("night5"))
    for k in range(-R, R, 6):  # cross-hair ticks
        d.point((cx + k, cy), fill=C("green1"))
        d.point((cx, cy + k), fill=C("green1"))
    # ground clutter near the centre
    r = rng(5)
    for _ in range(60):
        a, rr = r.rand() * 6.28, r.rand() ** 2 * 40
        d.point((cx + math.cos(a) * rr, cy + math.sin(a) * rr), fill=C("green2"))
    # curved glass highlight
    d.arc([cx - R + 20, cy - R + 20, cx + R - 20, cy + R - 20], 200, 240, fill=C("night6"), width=2)
    return [(1.0, im)]


def face(t, lt, u, p):
    """Close-up of the controller. p: zoom (1 = head 210 px), brows, look, wide, talk, blink."""
    bg = layer(WW, WH)
    gradient(bg, (0, 0, WW, WH), ["night1", "night0", "black"], axis="x")
    for i in range(14):  # out-of-focus lights through the window
        r = rng(40 + i)
        glow(bg, 380 + r.rand() * 320, 40 + r.rand() * 160, 8 + r.rand() * 10,
             ["night1", "night2", ["lamp1", "teal0", "night3"][i % 3]], strength=0.8)
    out = [(0.6, bg), (0.6, rain(WW, WH, t, n=60, speed=220, length=5, colors=("night2", "night3"), seed=9))]
    im = layer(WW, WH)
    z = p.get("zoom", 1.0)
    s = 210 * z
    ex, ey = p.get("eye_x", 300), p.get("eye_y", 170)  # where the near eye lands in the view
    head(im, ex + 32 - 0.36 * s, ey + 18 - 0.435 * s, s, t, p)
    glow(im, 40, 300, 160, ["green0", "green0", "green1"], strength=0.35)
    out.append((1.0, im))
    return out


@lru_cache(maxsize=None)
def _runway_ground(w=WW, h=WH, vpx=352, vpy=198, hw=230):
    im = layer(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle([0, vpy, w, h], fill=C("night1"))
    n = noise(w, h - vpy, 24, 21)
    ramp_fill(im, n * 0.8, ["black", "night0", "night1"], None, 0, vpy)
    # runway trapezoid
    left, right = (vpx - hw, h), (vpx + hw, h)
    d.polygon([(vpx - 6, vpy), (vpx + 6, vpy), right, left], fill=C("night2"))
    yy, xx = np.mgrid[vpy:h, 0:w]
    k = (yy - vpy) / (h - vpy)
    inside = np.abs(xx - vpx) <= 6 + k * (hw - 6)
    ramp_fill(im, np.where(inside, 0.2 + 0.5 * noise(w, h - vpy, 6, 23), -1), ["night1", "night2", "night3"], inside, 0, vpy)
    # centreline dashes and edge lights in perspective
    for i in range(1, 60):
        k = 1 / (1 + (i - 1) * 0.35)  # perspective spacing of lights along the runway
        y = vpy + (h - vpy) * k
        if i % 2:
            d.line([(vpx, y), (vpx, y + max(1, 6 * k))], fill=C("night6"))
        for side in (-1, 1):
            x = vpx + side * (6 + k * (hw - 6))
            rr = max(0, int(3 * k))
            col = "green3" if i == 1 else ("lamp4" if i % 2 else "white")
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=C(col))
            if k > 0.25:  # wet reflection streak
                d.line([(x, y + rr + 1), (x, y + rr + 1 + 14 * k)], fill=C("lamp1" if i % 2 else "night5"))
    # distant tower silhouette with lit cab
    d.rectangle([108, 150, 118, vpy], fill=C("night0"))
    d.polygon([(98, 136), (128, 136), (124, 150), (102, 150)], fill=C("night0"))
    d.rectangle([102, 139, 124, 145], fill=C("green2"))
    d.point((113, 132), fill=C("red2"))
    return im


def runway(t, lt, u, p):
    """Runway at night seen from the threshold. p: plane = approach | depart | none, prog 0..1."""
    sky = night_exterior(seed=8)
    out = [(0.35, sky)]
    g = _runway_ground().copy()
    vpx, vpy = 352, 198
    mode, prog = p.get("plane", "none"), p.get("prog", u)
    if mode in ("approach", "depart"):
        if mode == "approach":
            x, y, size = vpx + 4, 150 + 50 * prog ** 2, 1.5 + 9 * prog ** 2
        else:
            x, y, size = vpx + 2, 190 - 120 * prog ** 1.6, 6 * (1 - prog) + 0.6
        bright = 1.0 if mode == "approach" else max(0.0, 1 - max(0, prog - 0.7) / 0.3)
        if bright > 0:
            for dx in (-size * 0.9, size * 0.9):
                glow(g, x + dx, y, size * 2.2, ["night3", "night5", "paper", "white"], strength=bright)
            if (t % 1.0) < 0.12:
                ImageDraw.Draw(g).point((x, y - size * 0.6 - 1), fill=C("red2"))
            if mode == "approach" and prog > 0.2:  # reflection on the wet runway
                d = ImageDraw.Draw(g)
                for i in range(int(20 * prog)):
                    d.point((x + (i % 3 - 1), vpy + 6 + i * 4 * prog), fill=C("paper" if i % 2 else "night6"))
    splashes(g, t, (0, 260, WW, WH), n=50)
    out.append((1.0, g))
    out.append((1.3, rain(WW + 120, WH, t, n=260, speed=520, length=11, colors=("night5", "night6", "night4"), seed=4)))
    return out


@lru_cache(maxsize=None)
def _dc4(scale=1.0):
    """Generic four-engine 1940s-50s airliner in side view, nose left. No livery, no logos.
    Returns (image, ground offset y) with wheels touching the image bottom."""
    L = int(420 * scale)
    w, h = L + 20, int(170 * scale)
    im = layer(w, h)
    s = scale
    oy = int(80 * s)  # fuselage top reference
    Q = lambda seq: [(x * s + 8, y * s + oy) for x, y in seq]
    M = lambda seq: mask_of((w, h), lambda d: d.polygon(Q(seq), fill=1))
    d = ImageDraw.Draw(im)
    fin = M([(330, 4), (360, -60), (378, -72), (398, -70), (404, -10), (410, 2)])
    shade(im, fin, ["night4", "night5", "night6", "night7"], light=(-0.6, -1), bias=0.05)
    body = M([(18, 4), (60, -1), (300, 0), (412, -4), (414, 6), (300, 26), (250, 42), (60, 44), (16, 36), (4, 24), (6, 12)])
    shade(im, body, ["night3", "night4", "night5", "night6", "night7", "paper"], light=(-0.2, -1), bias=0.12, contrast=1.3)
    fill(im, M([(10, 22), (300, 20), (300, 23), (10, 25)]) & body, "night3")  # cheat line
    stab = M([(352, 2), (404, -2), (414, 0), (360, 8)])
    shade(im, stab, ["night3", "night4", "night5"])
    fill(im, M([(14, 8), (40, 3), (44, 12), (16, 14)]), "night0")  # cockpit glazing
    d.line(Q([(20, 6), (40, 4)]), fill=C("green1"))
    for i in range(19):  # cabin windows, lit from inside
        x = 66 + i * 12.5
        col = "lamp3" if i % 5 else "lamp2"
        d.rectangle(Q([(x, 12), (x + 5, 18)]), fill=C(col))
    wing = M([(130, 34), (240, 33), (250, 38), (126, 40)])
    shade(im, wing, ["night2", "night3", "night4"])
    for nx, ny, k in ((150, 38, 1.0), (128, 43, 1.08)):  # inner and outer nacelles of the near wing
        nac = M([(nx, ny), (nx + 52 * k, ny + 1), (nx + 46 * k, ny + 12 * k), (nx + 4, ny + 11 * k), (nx - 4, ny + 6 * k)])
        shade(im, nac, ["night2", "night3", "night5", "night6"], light=(-0.3, -1), bias=0.05)
    # landing gear
    for gx, gy, r in ((178, 52, 11), (198, 52, 11), (40, 42, 7)):
        d.line(Q([(gx, gy - 6), (gx + 2, 82 - r)]), fill=C("night1"), width=max(1, int(3 * s)))
        cx, cy = gx * s + 8 + 2 * s, (82 - r) * s + oy
        d.ellipse([cx - r * s, cy - r * s, cx + r * s, cy + r * s], fill=C("black"))
        d.ellipse([cx - r * s * 0.4, cy - r * s * 0.4, cx + r * s * 0.4, cy + r * s * 0.4], fill=C("night3"))
    return im, 82 * s + oy


def _props(im, ox, oy, s, t, speed):
    """Spinning propeller discs for the two visible engines."""
    d = ImageDraw.Draw(im)
    for nx, ny, k in ((150, 38, 1.0), (128, 43, 1.08)):
        cx, cy = ox + (nx - 5) * s + 8, oy + (ny + 6 * k) * s
        R = 24 * s * k
        for b in range(3):
            a = t * speed + b * 2.094 + nx
            dy = math.cos(a) * R
            d.line([(cx, cy), (cx - 1, cy + dy)], fill=C("night1"))
        for yy in range(int(-R), int(R) + 1, 2):  # faint disc
            if (yy + int(t * 60)) % 4 == 0:
                d.point((cx, cy + yy), fill=C("night5"))


def plane_side(t, lt, u, p):
    """Airliner on the wet apron, rain, rolling left to take off. p: x (plane offset px), props."""
    sky = night_exterior(seed=12, horizon=230, lights_y=236)
    out = [(0.4, sky)]
    g = layer(WW, WH)
    d = ImageDraw.Draw(g)
    gy = 300
    gradient(g, (0, gy, WW, WH), ["night2", "night1", "night0"])
    for i in range(0, WW, 46):  # apron joints
        d.line([(i, gy), (i - 60, WH)], fill=C("night1"))
    plane, ground = _dc4(1.0)
    px = int(140 + p.get("x", 0))
    py = int(gy - ground)
    # reflection: flipped, dithered, dim
    refl = plane.transpose(Image.FLIP_TOP_BOTTOM)
    a = np.array(refl)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    a[..., 3] = np.where(((xx + yy) % 2 == 0) & (yy < a.shape[0] * 0.7), a[..., 3], 0)  # checker dither = 50% see-through
    a[..., :3] = snap((a[..., :3] * 0.45).astype(np.uint8))
    g.alpha_composite(Image.fromarray(a), (px, gy + 2), (0, 0))
    g.alpha_composite(plane, (px, py))
    _props(g, px, py + int(80), 1.0, t, p.get("props", 40))
    if (t % 1.0) < 0.12:  # beacon
        d.ellipse([px + 180, py + 74, px + 184, py + 78], fill=C("red2"))
        glow(g, px + 182, py + 76, 14, ["night2", "red0", "red1"], strength=0.7)
    d.point((px + 425, py + 76), fill=C("white"))
    splashes(g, t, (0, gy + 4, WW, WH), n=70)
    out.append((1.0, g))
    out.append((1.3, rain(WW + 120, WH, t, n=240, speed=520, length=11, colors=("night5", "night6", "night4"), seed=6)))
    return out


@lru_cache(maxsize=None)
def _asphalt():
    im = layer(WW, WH)
    n = noise(WW, WH, 10, 31, octaves=4)
    ramp_fill(im, n, ["black", "night0", "night1", "night2", "night3"], None, 0, 0)
    d = ImageDraw.Draw(im)
    r = rng(33)
    for _ in range(900):
        d.point((r.rand() * WW, r.rand() * WH), fill=C(["night4", "night5", "night3"][r.randint(3)]))
    # puddles
    for cx, cy, rx, ry in ((160, 300, 150, 40), (560, 110, 120, 30)):
        yy, xx = np.mgrid[0:WH, 0:WW]
        m = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 + (noise(WW, WH, 12, 37) - 0.5) * 0.9) < 1
        ramp_fill(im, np.where(m, noise(WW, WH, 20, 35) * 0.6 + 0.2, -1), ["black", "teal0", "night2"], m, 0, 0)
    return im


@lru_cache(maxsize=None)
def _calendar_card():
    """Small pocket calendar, wet. Only legible text: 1955 (drawn with the engine font)."""
    w, h = 230, 158
    im = layer(w, h)
    d = ImageDraw.Draw(im)
    m = mask_of((w, h), lambda dd: dd.rectangle([0, 0, w - 1, h - 1], fill=1))
    shade(im, m, ["night5", "night6", "night7", "paper", "paper_hi"], light=(-0.7, -1), bias=0.12, contrast=0.9)
    gradient(im, (0, 0, w, 50), ["red2", "red1", "red0"])
    draw_text(im, (w - text_width("1955", 5)) // 2, 8, "1955", "paper_hi", 5)
    for row in range(5):  # day grid without numbers
        for col in range(7):
            x, y = 18 + col * 29, 62 + row * 18
            d.rectangle([x, y, x + 10, y + 3], fill=C("night4" if (row * 7 + col) % 6 else "red1"))
    # wet stains on the lower half only, so the year stays legible
    n = noise(w, h, 16, 51)
    stain = np.where((n > 0.62) & (np.arange(h)[:, None] > 56), (n - 0.62) * 2.5, -1)
    ramp_fill(im, stain, ["night6", "night5"], m, 0, 0)
    d.polygon([(w - 1, h - 30), (w - 30, h - 1), (w - 1, h - 1)], fill=(0, 0, 0, 0))
    d.polygon([(w - 1, h - 30), (w - 30, h - 1), (w - 19, h - 19)], fill=C("night5"))
    return im


def calendar(t, lt, u, p):
    """Pocket calendar lying on the wet runway. Light from a passing rotating beacon."""
    g = _asphalt().copy()
    d = ImageDraw.Draw(g)
    card = _calendar_card()
    cx, cy = 250, 110
    d.polygon([(cx + 6, cy + 158), (cx + 230, cy + 158), (cx + 236, cy + 166), (cx + 12, cy + 166)], fill=C("black"))
    # beacon sweep on the asphalt (under the card): a band of light crossing every 3 s
    ph = (t % 3.0) / 3.0
    lx = -200 + ph * (WW + 400)
    glow(g, lx, 200, 150, ["night2", "night3"], strength=0.35, sy=1.6)
    g.alpha_composite(card, (cx, cy))
    # ripples on the puddles
    for i in range(10):
        period = 1.1
        k = int((t + i * 0.37) // period)
        ph2 = ((t + i * 0.37) % period) / period
        r = rng(70 + i * 13 + k)
        pcx, pcy, prx, pry = ((160, 300, 130, 32), (560, 110, 100, 24))[i % 2]
        x, y = pcx + (r.rand() - 0.5) * prx * 1.6, pcy + (r.rand() - 0.5) * pry * 1.4
        rr = 2 + ph2 * 14
        d.ellipse([x - rr, y - rr * 0.35, x + rr, y + rr * 0.35], outline=C("night5" if ph2 < 0.5 else "night3"))
    splashes(g, t, (0, 0, WW, WH), n=60, color="night5")
    return [(1.0, g), (1.3, rain(WW + 120, WH, t, n=200, speed=560, length=12, colors=("night4", "night5"), seed=8))]


def title(t, lt, u, p):
    """Title card: episode name over rain and the scope's glow."""
    g = layer(WW, WH)
    gradient(g, (0, 0, WW, WH), ["black", "night0", "black"])
    glow(g, 352, 198, 220, ["black", "night0", "green0"], strength=0.4)
    txt, sub = p.get("text", "VUELO 914"), p.get("sub", "ARCHIVO CERO")
    draw_text(g, (WW - text_width(txt, 6)) // 2, 168, txt, "paper", 6)
    ImageDraw.Draw(g).line([(WW // 2 - 60, 222), (WW // 2 + 60, 222)], fill=C("red1"))
    draw_text(g, (WW - text_width(sub, 2)) // 2, 232, sub, "night6", 2)
    return [(1.0, g), (1.2, rain(WW + 80, WH, t, n=120, speed=400, length=8, colors=("night2", "night3"), seed=10))]

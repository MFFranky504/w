"""Pink-haired character painting a picture at an easel (chibi pixel art).

Re-uses the hair / head model and helpers from pinky.py. The whole scene
(character + easel) can be rendered at any turn angle; the brush follows a
heart being painted on the canvas.
"""
import math
import numpy as np
from PIL import Image
import pinky as P0
from pinky import (quad, ellipsoid, ell_normal, vsection, unit, sd_ell, axes_from, hair_sdf,
                   hair_parts, march_sdf, sdf_normal, HEAD_C, HEAD_R, I3, hexc)

K = 0.85
WU, HU = 104, 124
W, H = int(round(WU * K)), int(round(HU * K))
yy, xx = np.mgrid[0:H, 0:W]
PIV = WU / 2
XC = 8.0                      # turn axis (local x) = middle of character + easel

RAMPS = dict(P0.RAMPS)
for k, v in {
    'wood':   ['#6b3f1e', '#8a5530', '#b07445', '#cf955f', '#e6b47e', '#4a2a12'],
    'canvas': ['#c9bfa8', '#ddd3bd', '#f2ecdf', '#fffaf0', '#ffffff', '#8f846c'],
    'metal':  ['#6c7080', '#9095a8', '#c3c7d6', '#e6e9f2', '#ffffff', '#3e4150'],
    'sky':    ['#5f9fd6', '#79b6e8', '#9dd0fa', '#bfe2ff', '#d9efff', '#3d6f9e'],
    'grass':  ['#2f8a45', '#3fa357', '#5cc46e', '#7fdb8c', '#a6efb0', '#1d5a2c'],
    'sun':    ['#d9a515', '#f0c020', '#ffd94a', '#ffe98a', '#fff4c0', '#8a6a08'],
    'heart':  ['#b0124a', '#d81f5f', '#ff3d7f', '#ff7aa6', '#ffb3cc', '#7a0c33'],
    'blob_p': ['#5b1fa0', '#7130c0', '#8e4fe0', '#ad7af0', '#cfadff', '#36106a'],
    'blob_b': ['#1f5fb8', '#2f78d8', '#4f98f5', '#80b8ff', '#b3d6ff', '#143c78'],
    'blob_w': ['#c8c8d4', '#e0e0ea', '#ffffff', '#ffffff', '#ffffff', '#8a8a98'],
}.items():
    RAMPS[k] = [hexc(c) for c in v]
OL = P0.OL
FACE = dict(P0.FACE)
FACE.update({k: hexc(v) for k, v in dict(
    D='#3a1858', I='#6b36ad', L='#a678ea', s='#ffffff', w='#ffffff', p='#1a0b2a',
    b='#ff9fb2', c='#ffc4cf').items()})


def torso_ab(y):
    s = np.where(y < 71, np.clip(1 - np.clip((71 - y) / 7.0, 0, 1) ** 2.6, 0, 1) ** (1 / 2.6),
                 1 + (y - 71) * 0.006)
    return 12.4 * s, 9.6 * s

LIGHT = P0.LIGHT

(FACE_SKIN, HAIR, SKIN, GRAY, OVER, BOOT, YEL, POCKET, WOOD, CANVAS, METAL, PAINT) = range(12)
GROUP_RAMP = {FACE_SKIN: 'skin', HAIR: 'hair', SKIN: 'skin', GRAY: 'gray', OVER: 'over', BOOT: 'boot',
              YEL: 'yel', POCKET: 'over', WOOD: 'wood', CANVAS: 'canvas', METAL: 'metal'}
PAINT_RAMPS = ['sky', 'grass', 'sun', 'heart', 'blob_p', 'blob_b', 'blob_w', 'yel', 'hair']

# ---------------------------------------------------------------- easel / canvas frame
CA = math.radians(35)
N_C = np.array([-math.sin(CA), 0, math.cos(CA)])        # canvas faces the painter + viewer
T_C = np.array([math.cos(CA), 0, math.sin(CA)])
UP = np.array([0, 1.0, 0])
BASE = np.array([33.0, 0.0, 4.0])
AX_C = np.stack([T_C, UP, N_C])
C_CAN = BASE + UP * 62.0
CAN_HS = np.array([17.0, 13.5, 0.9])


def cf(a, y, c):
    return BASE + T_C * a + UP * y + N_C * c


def canvas_point(u, v, off=1.2):
    return C_CAN + T_C * (u * CAN_HS[0]) - UP * (v * CAN_HS[1]) + N_C * (CAN_HS[2] + off)


# heart path in canvas uv
def heart_uv(t):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return 0.22 + x / 17 * 0.44, 0.02 + y / 17 * 0.50


HEART_T = np.linspace(0, 2 * math.pi, 241)
HEART_PTS = np.array([heart_uv(t) for t in HEART_T])


def box(o, d, c, ax, hs):
    oo = (o - c) @ ax.T
    dd = d @ ax.T
    big = 1e9
    with np.errstate(divide='ignore', invalid='ignore'):
        inv = np.where(np.abs(dd) < 1e-9, big, 1.0 / dd)
        t1 = (-hs - oo) * inv
        t2 = (hs - oo) * inv
    par = np.abs(dd) < 1e-9
    inside = np.abs(oo) <= hs
    tn = np.where(par, np.where(inside, -big, big), np.minimum(t1, t2))
    tf = np.where(par, np.where(inside, big, -big), np.maximum(t1, t2))
    tmin = tn.max(-1)
    tmax = tf.min(-1)
    hit = (tmax >= tmin) & (tmax > 0)
    axis = tn.argmax(-1)
    sgn = -np.sign(np.take_along_axis(dd, axis[..., None], -1)[..., 0])
    n = ax[axis] * sgn[..., None]
    return np.where(hit, tmin, np.inf), n, axis, sgn


def two_bone(S, Hd, l1, l2, pole):
    v = Hd - S
    d = min(np.linalg.norm(v), l1 + l2 - 1e-3)
    u = v / np.linalg.norm(v)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    p = pole - u * (pole @ u)
    p /= np.linalg.norm(p)
    return S + u * a + p * h


PALETTE_C = np.array([-10.5, 77.0, 11.5])
PAL_N = unit(np.array([0.0, -0.78, 0.62]))
PAL_AX = np.stack([np.array([1.0, 0, 0]), PAL_N, np.cross(np.array([1.0, 0, 0]), PAL_N)])
PAL_R = np.array([9.0, 0.9, 6.6])
BLOBS = [((-5.2, -2.6), 'heart'), ((-1.4, -4.0), 'blob_p'), ((2.8, -3.6), 'sun'),
         ((5.8, -1.0), 'blob_b'), ((3.2, 2.6), 'blob_w'), ((-1.0, 1.0), 'grass')]
SPLATS = [((-3.6, 82.5), 'heart', 1.2), ((5.0, 91.5), 'sun', 0.9), ((-6.8, 97.0), 'blob_b', 0.9),
          ((2.4, 76.0), 'blob_p', 0.85), ((7.2, 101.5), 'heart', 0.85)]


def render(phi, hop=0.0, progress=1.0, dab=(0.0, 0.0)):
    with np.errstate(all='ignore'):
        return _render(phi, hop, progress, dab)


BODY_SHIFT = 7.0                  # neck/torso/arms move up by this much
LEG_N0, LEG_N1 = 81.0, 100.0      # legs: new (world) y range ...
LEG_O0, LEG_O1 = 88.0, 100.0      # ... taken from this model y range (longer legs)
S_HEAD = 0.85                     # smaller head + hair
NECK_OLD = 61.0
NECK_NEW = NECK_OLD - BODY_SHIFT


def body_y(yn):
    return np.where(yn < LEG_N0, yn + BODY_SHIFT,
                    np.where(yn < LEG_N1, LEG_O0 + (yn - LEG_N0) * (LEG_O1 - LEG_O0) / (LEG_N1 - LEG_N0), yn))


def _render(phi, hop, progress, dab):
    cphi, sphi = math.cos(phi), math.sin(phi)
    Xu = (xx + 0.5) / K - PIV
    Yu = (yy + 0.5) / K + hop
    Z0 = 300.0
    o = np.stack([Xu * cphi - Z0 * sphi + XC, Yu, Xu * sphi + Z0 * cphi], -1)
    d = np.broadcast_to(np.array([sphi, 0.0, -cphi]), o.shape)
    o_w = o
    o_b = o.copy()
    o_b[..., 1] = body_y(o[..., 1])
    o_h = (o - np.array([0, NECK_NEW, 0])) / S_HEAD + np.array([0, NECK_OLD, 0])
    d_h = d / S_HEAD
    R = {'o': o_b, 'd': d}
    Y = o_b[..., 1]

    depth = np.full((H, W), np.inf)
    pid = np.full((H, W), -1)
    NL = np.zeros((H, W, 3))
    PL = np.zeros((H, W, 3))
    AUX = np.zeros((H, W), int)

    def commit(t, k, nfun, aux=None):
        m = t < depth
        if not m.any():
            return
        p = R['o'] + t[..., None] * R['d']
        n = nfun(p)
        depth[m] = t[m]
        pid[m] = k
        PL[m] = p[m]
        NL[m] = n[m]
        AUX[m] = 0 if aux is None else aux[m]

    def ell(k, c, ax, r):
        c = np.asarray(c, float)
        t1, _, M = ellipsoid(R['o'], R['d'], c, ax, r)
        commit(t1, k, lambda p: ell_normal(p, c, M))

    def stick(k, p0, p1, r):
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        uu = (p1 - p0) / np.linalg.norm(p1 - p0)
        ell(k, (p0 + p1) / 2, axes_from(uu), (np.linalg.norm(p1 - p0) / 2 + 0.6, r, r))

    def bx(k, c, ax, hs):
        t, n, axis, sgn = box(R['o'], R['d'], np.asarray(c, float), ax, np.asarray(hs, float))
        commit(t, k, lambda p: n, aux=axis * 2 + (sgn > 0))

    # ---------------- head group (scaled down, sits on the raised neck)
    R['o'], R['d'] = o_h, d_h
    ell(1, HEAD_C, I3, HEAD_R)
    for s in (-1, 1):
        ell(2, (s * 17.4, 47.5, -1.0), I3, (2.6, 4.2, 3.4))
    th = march_sdf(o_h, d, hair_sdf, np.array([0, 34.0, -3.0]), 40.0) * S_HEAD
    commit(th, 0, lambda p: sdf_normal(hair_sdf, p))
    # ---------------- body group (raised torso, longer legs)
    R['o'], R['d'] = o_b, d
    o, d = o_b, d
    t1, _ = vsection(o, d, 0, -1.2, 4.8, 4.8, 57, 68)
    commit(t1, 3, lambda p: np.stack([p[..., 0], 0 * p[..., 0], p[..., 2] + 1.5], -1))
    ell(4, (0, 64.2, -2.0), I3, (9.0, 3.6, 7.8))
    a, b = torso_ab(Y)
    t1, _ = vsection(o, d, 0, 0, a, b, 63.4, 88.0)

    def torso_n(p):
        aa, bb = torso_ab(p[..., 1])
        ny = -np.clip((71 - p[..., 1]) / 7.6, 0, 1) ** 1.6 * 0.12
        return np.stack([p[..., 0] / aa ** 2, ny, p[..., 2] / bb ** 2], -1)
    commit(t1, 5, torso_n)

    # brush arm (character's left, local +x): hand follows the brush tip
    tip_u, tip_v = dab
    tip = canvas_point(tip_u, tip_v, off=0.4) + np.array([0, BODY_SHIFT, 0])
    bdir = unit(T_C * 0.72 - N_C * 0.62 + np.array([0, 0.16, 0]))
    hand = tip - bdir * 14.6
    S = np.array([9.4, 67.5, 0.0])
    E = two_bone(S, hand, 10.8, 10.8, np.array([0.2, 1.0, -0.5]))
    for (p0, p1, rr) in ((S, E, 3.6), (E, hand, 3.0)):
        stick(6, p0, p1, rr)
    uu = unit(hand - E)
    ell(7, hand - uu * 2.4, axes_from(uu), (1.7, 3.6, 3.6))
    ell(8, hand + uu * 0.6, I3, (3.6, 3.6, 3.6))
    stick(11, hand - bdir * 3.0, hand + bdir * 10.0, 1.0)          # wooden handle
    stick(12, hand + bdir * 9.8, hand + bdir * 11.4, 1.2)          # ferrule
    ell(13, hand + bdir * 12.8, axes_from(bdir), (2.0, 1.3, 1.3))   # paint-loaded bristles

    # palette arm (character's right, local -x): palette held in front of the belly
    S2 = np.array([-9.4, 67.5, 0.0])
    hand2 = np.array([-9.0, 79.5, 7.8])
    E2 = two_bone(S2, hand2, 10.5, 10.5, np.array([-0.8, 0.6, -0.3]))
    for (p0, p1, rr) in ((S2, E2, 3.6), (E2, hand2, 3.0)):
        stick(6, p0, p1, rr)
    uu = unit(hand2 - E2)
    ell(7, hand2 - uu * 2.4, axes_from(uu), (1.7, 3.6, 3.6))
    ell(14, PALETTE_C, PAL_AX, PAL_R)
    ell(8, hand2 + np.array([0, 1.2, 1.0]), I3, (3.6, 3.6, 3.6))
    ell(8, PALETTE_C + PAL_AX[2] * 3.2 + PAL_AX[0] * -5.0 + PAL_N * 0.9, I3, (1.8, 1.8, 1.8))  # thumb

    # overalls + boots
    hp = np.array([0, 86.8, 0.0])
    t1, _, Mp = ellipsoid(o, d, hp, I3, [11.6, 5.6, 9.0])
    commit(t1, 9, lambda p: ell_normal(p, hp, Mp))
    for s in (-1, 1):
        cxl = s * 6.4
        aa = 4.6 + (Y - 88) * 0.04
        t1, _ = vsection(o, d, cxl, 0, aa, 4.8, 87, 103.5)
        commit(t1, 9, (lambda cxl: lambda p: np.stack(
            [(p[..., 0] - cxl) / (4.6 + (p[..., 1] - 88) * 0.04) ** 2, 0 * p[..., 0], p[..., 2] / 23.0], -1))(cxl))
        t1, _ = vsection(o, d, s * 6.5, 0, 5.0, 5.0, 100.5, 107.5)
        commit(t1, 10, (lambda cx: lambda p: np.stack(
            [(p[..., 0] - cx) / 25.0, 0 * p[..., 0], p[..., 2] / 25.0], -1))(s * 6.5))
        ell(10, (s * 6.6, 108.2, 2.4), I3, (4.6, 3.8, 7.0))

    # ---------------- easel + canvas (world space)
    R['o'], R['d'] = o_w, d
    o = o_w
    top = cf(0, 42.5, -4.0)
    for foot in (cf(-13.0, 112, 2.5), cf(13.0, 112, 2.5), cf(0, 112, -16.0)):
        stick(15, top, foot, 1.25)
    bx(15, cf(0, 76.9, 1.9), AX_C, (18.5, 1.0, 2.6))                # ledge
    bx(15, cf(0, 47.2, 0.2), AX_C, (2.2, 1.6, 1.7))                 # top clamp
    bx(16, C_CAN, AX_C, CAN_HS)                                     # canvas

    # ------------------------------------------------------------ materials
    hit = pid >= 0
    nW = unit(NL)
    nw = np.stack([nW[..., 0] * cphi + nW[..., 2] * sphi, nW[..., 1],
                   -nW[..., 0] * sphi + nW[..., 2] * cphi], -1)
    inten = (nw * LIGHT).sum(-1)
    x, y, z = PL[..., 0], PL[..., 1], PL[..., 2]
    grp = np.full((H, W), -1)
    paint = np.full((H, W), -1)
    part = pid.copy()

    hm = pid == 0
    lidx = np.full((H, W), -1)
    crev = np.zeros((H, W), bool)
    if hm.any():
        dl, ex = hair_parts(PL[hm])
        allp = np.concatenate([dl, ex], 1)
        lidx[hm] = allp.argmin(1)
        crev[hm] = allp.min(1) > 0.6
    grp[hm] = HAIR
    grp[pid == 1] = FACE_SKIN
    grp[np.isin(pid, [2, 3, 8])] = SKIN
    grp[np.isin(pid, [4, 6, 7])] = GRAY
    grp[pid == 9] = OVER
    grp[pid == 10] = BOOT
    grp[np.isin(pid, [11, 14, 15])] = WOOD
    grp[pid == 12] = METAL
    grp[pid == 13] = PAINT
    paint[pid == 13] = PAINT_RAMPS.index('heart')

    m = pid == 5
    ax_ = np.abs(x)
    front = z > 0
    bib = front & (ax_ < 7.4) & (y > 70.2)
    strap = (np.abs(ax_ - 5.8) < 1.8) & (y < 71.5) & front
    back_strap = ~front & (np.abs(ax_ - 5.0 + (y - 66) * 0.10) < 1.7) & (y < 80)
    back_panel = ~front & (ax_ < 7.8) & (y > 78)
    over = bib | strap | back_strap | back_panel | (y > 80.5)
    grp[m] = GRAY
    grp[m & over] = OVER
    button = front & ((((x - 5.8) ** 2 + (y - 71.4) ** 2) < 1.9) | (((x + 5.8) ** 2 + (y - 71.4) ** 2) < 1.9))
    grp[m & button] = YEL
    pocket = front & (ax_ < 3.4) & (y > 73.6) & (y < 78.0)
    grp[m & pocket & ~button] = POCKET
    part[m & over] = 50
    # paint splats on the overalls (front)
    ov = (grp == OVER) & front
    for (sx, sy), col, r in SPLATS:
        sp = ov & (((x - sx) ** 2 + (y - sy) ** 2) < r * r)
        grp[sp] = PAINT
        paint[sp] = PAINT_RAMPS.index(col)

    # palette blobs
    pm = pid == 14
    if pm.any():
        q = (PL - PALETTE_C) @ PAL_AX.T
        top_side = (q[..., 1] < 0)
        for (pa, pc), col in BLOBS:
            bl = pm & top_side & (((q[..., 0] - pa) ** 2 + (q[..., 2] - pc) ** 2) < 2.6)
            grp[bl] = PAINT
            paint[bl] = PAINT_RAMPS.index(col)

    # canvas: painting on the front face, linen on edges, wooden stretcher on the back
    cm = pid == 16
    grp[cm] = CANVAS
    if cm.any():
        q = (PL - C_CAN) @ AX_C.T
        u = q[..., 0] / CAN_HS[0]
        v = -q[..., 1] / CAN_HS[1]
        front_face = cm & (AUX == 5)
        back_face = cm & (AUX == 4)
        sky = front_face
        grass = front_face & (v < -0.38 + 0.16 * np.sin(u * 2.6 + 0.6))
        sun = front_face & (((u + 0.62) / 0.9) ** 2 + (v - 0.55) ** 2 < 0.19 ** 2)
        for msk, col in ((sky, 'sky'), (grass, 'grass'), (sun, 'sun')):
            grp[msk] = PAINT
            paint[msk] = PAINT_RAMPS.index(col)
        # heart painted so far
        n_pts = int(round(progress * (len(HEART_PTS) - 1)))
        if n_pts > 0 and front_face.any():
            pts = HEART_PTS[:n_pts + 1]
            uu_ = u[front_face][:, None]
            vv_ = v[front_face][:, None]
            dmin = np.sqrt(((uu_ - pts[None, :, 0]) * CAN_HS[0] / CAN_HS[1]) ** 2 +
                           (vv_ - pts[None, :, 1]) ** 2).min(1)
            stroke = np.zeros((H, W), bool)
            stroke[front_face] = dmin < 0.13
            grp[stroke] = PAINT
            paint[stroke] = PAINT_RAMPS.index('heart')
            if progress >= 0.999:
                inside = np.zeros((H, W), bool)
                inside[front_face] = _inside_heart(u[front_face], v[front_face])
                grp[inside] = PAINT
                paint[inside] = PAINT_RAMPS.index('heart')
        wood_back = back_face & ((np.abs(u) > 0.84) | (np.abs(v) > 0.8) | (np.abs(u) < 0.08))
        grp[wood_back] = WOOD
        part[cm] = 60

    lvl = np.full((H, W), 2)
    lvl[inten < 0.40] = 1
    lvl[inten < -0.32] = 0
    lvl[inten > 0.80] = 3
    lvl[(grp == BOOT) & (inten > 0.93)] = 4
    lvl[(grp == METAL) & (inten > 0.6)] = 4
    lvl[(grp == YEL) & (inten > 0.6)] = 3
    lvl[crev] = np.clip(lvl[crev] - 1, 0, 3)
    lvl[grp == POCKET] = np.clip(lvl[grp == POCKET] - 1, 0, 3)
    lam = np.arctan2(x, z + 5)
    band_c = 23.5 + 2.5 * np.sin(lam * 1.3 + 0.5)
    shine = hm & (np.abs(y - band_c) < 2.3) & (lvl >= 1)
    lvl[shine] = np.maximum(lvl[shine], 3)
    lvl[shine & (np.abs(y - band_c) < 0.9) & (inten > 0.3)] = 4
    lvl[pid == 3] = np.minimum(lvl[pid == 3], 1)
    # painting reads flat: clamp its shading to two tones
    pmask = (grp == PAINT) & (pid == 16)
    lvl[pmask] = np.clip(lvl[pmask], 1, 2)

    img = np.zeros((H, W, 4), np.uint8)
    for g, rname in GROUP_RAMP.items():
        mm = grp == g
        for L in range(5):
            img[mm & (lvl == L)] = RAMPS[rname][L]
    for i, rname in enumerate(PAINT_RAMPS):
        mm = (grp == PAINT) & (paint == i)
        for L in range(5):
            img[mm & (lvl == L)] = RAMPS[rname][L]

    def nb(a, dx, dy, fill):
        out = np.full_like(a, fill)
        out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = \
            a[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
        return out

    line = np.zeros((H, W), bool)
    soft = np.zeros((H, W), bool)
    lockl = np.zeros((H, W), bool)
    over_edge = np.zeros((H, W), bool)
    canvas_edge = np.zeros((H, W), bool)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dn = nb(depth, dx, dy, np.inf)
        gn = nb(grp, dx, dy, -1)
        pn = nb(part, dx, dy, -1)
        an = nb(AUX, dx, dy, -1)
        line |= hit & (gn >= 0) & (((dn < depth - 2.6) & (pn != part)) | (dn < depth - 9.0))
        line |= (grp == OVER) & (gn == YEL)
        line |= (grp == POCKET) & (gn == OVER) & (np.abs(dn - depth) < 2)
        canvas_edge |= (pid == 16) & (nb(pid, dx, dy, -1) == 16) & (an != AUX)
        over_edge |= (grp == GRAY) & (gn == OVER) & (np.abs(dn - depth) < 2.6)
        soft |= (grp == FACE_SKIN) & (gn == HAIR) & (np.abs(dn - depth) < 2.6)
        li = nb(lidx, dx, dy, -1)
        lockl |= (lidx >= 0) & (li >= 0) & (li != lidx) & (dn < depth - 1.2)
    for g, rname in GROUP_RAMP.items():
        img[line & (grp == g)] = RAMPS[rname][5]
    for i, rname in enumerate(PAINT_RAMPS):
        img[line & (grp == PAINT) & (paint == i)] = RAMPS[rname][5]
    img[canvas_edge & ~line] = RAMPS['canvas'][0]
    img[soft & ~line] = RAMPS['skin'][1]
    img[over_edge & ~line] = RAMPS['over'][5]
    img[lockl & ~line] = RAMPS['hair'][5]

    # ------------------------------------------------------------ face sprites
    def place(lx, ly, variants, cmap, only=(FACE_SKIN,)):
        lz = HEAD_R[2] * math.sqrt(max(0.0, 1 - (lx / HEAD_R[0]) ** 2 - ((ly - HEAD_C[1]) / HEAD_R[1]) ** 2))
        n = np.array([lx / HEAD_R[0] ** 2, (ly - HEAD_C[1]) / HEAD_R[1] ** 2, lz / HEAD_R[2] ** 2])
        n /= np.linalg.norm(n)
        facing = -n[0] * sphi + n[2] * cphi
        rows = None
        for thr, vv in variants:
            if facing >= thr:
                rows = vv
                break
        if rows is None:
            return
        Xw, Yw, Zw = lx * S_HEAD, NECK_NEW + (ly - NECK_OLD) * S_HEAD, lz * S_HEAD
        wx = (Xw - XC) * cphi + Zw * sphi
        px_ = (wx + PIV) * K
        py_ = (Yw - hop) * K
        h_, w_ = len(rows), len(rows[0])
        x0 = int(round(px_ - w_ / 2))
        y0 = int(round(py_ - h_ / 2))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == '.':
                    continue
                X_, Y_ = x0 + i, y0 + j
                if 0 <= X_ < W and 0 <= Y_ < H and grp[Y_, X_] in only:
                    img[Y_, X_] = cmap[ch]

    core = ["KWWDDK", "KWDpDK", "KIppIK", "KIIIwK", ".LLLL.", "..KK.."]
    eye_l = [(0.80, ["KKKKK.", "KKDDKK"] + core),
             (0.55, ["KKKKK", "KWDDK", "KDpDK", "KIIwK", ".LLL."]),
             (0.30, ["KKK", "KWK", "KpK", "KIK", ".L."]),
             (0.16, ["KK", "KD", "KI"])]
    eye_r = [(0.80, [".KKKKK", "KKDDKK"] + core)] + eye_l[1:]
    place(-7.0, 47.6, eye_l, FACE)
    place(7.0, 47.6, eye_r, FACE)
    for s in (-1, 1):
        place(s * 11.6, 52.6, [(0.7, [".bcb.", "bbbbb"]), (0.4, ["bcb", "bbb"]), (0.2, ["b", "b"])], FACE)
    place(0.6, 52.4, [(0.75, [".nn.", "n..n"]), (0.45, ["nn", "n."]), (0.2, ["n"])], FACE)
    place(1.4, 56.0, [(0.75, [".....M", "M...M.", ".MMM.."]), (0.45, ["...M", "MMM."]), (0.2, ["MM"])], FACE)

    solid = img[..., 3] > 0
    ring_ = np.zeros_like(solid)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring_ |= nb(solid, dx, dy, False)
    img[ring_ & ~solid] = OL
    return img


def _inside_heart(u, v):
    # even-odd test against the heart polygon in uv
    px, py = HEART_PTS[:, 0], HEART_PTS[:, 1]
    inside = np.zeros(u.shape, bool)
    n = len(px)
    for i in range(n - 1):
        x1, y1, x2, y2 = px[i], py[i], px[i + 1], py[i + 1]
        cond = (y1 > v) != (y2 > v)
        xint = (x2 - x1) * (v - y1) / (y2 - y1 + 1e-12) + x1
        inside ^= cond & (u < xint)
    return inside


if __name__ == '__main__':
    import sys
    shots = [(0, 0.6), (math.radians(20), 1.0), (math.radians(90), 1.0), (math.radians(200), 1.0)]
    ims = []
    for ph, pr in shots:
        hu, hv = HEART_PTS[int(pr * (len(HEART_PTS) - 1))]
        f = render(ph, progress=pr, dab=(hu, hv))
        im = Image.new('RGBA', (W, H), (236, 241, 252, 255))
        im.alpha_composite(Image.fromarray(f))
        ims.append(im.resize((W * 4, H * 4), Image.NEAREST))
    cs = Image.new('RGB', (W * 16, H * 4), 'white')
    for i, b in enumerate(ims):
        cs.paste(b, (i * W * 4, 0))
    cs.save('paint_zoom.png')
    print(W, H)

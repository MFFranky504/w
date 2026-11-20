"""Chibi pixel-art character spinning happily, arms open, eyes closed.

The character is modelled with simple 3D primitives (ellipsoids / vertical
sections) and ray-cast at pixel resolution with cel shading + outlines, so
every angle of the turn is consistent. Face details are hand-drawn sprites
placed on the head surface.
"""
import math
import numpy as np
from PIL import Image

K = 0.85                     # pixels per model unit (lower = chunkier pixels)
WU, HU = 120, 124            # model canvas in units
W, H = int(round(WU * K)), int(round(HU * K))
yy, xx = np.mgrid[0:H, 0:W]
PIV = 60.0


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


# ramps: dk, sh, b, lt, hi, line
RAMPS = {
    'cyan':   ['#2a86c9', '#35b2e6', '#4fd9f3', '#8cf3ff', '#effeff', '#1b5a92'],
    'cyan_in': ['#185a94', '#1f6fae', '#2a86c9', '#2a86c9', '#2a86c9', '#123f6c'],
    'pink':   ['#c9666d', '#e07f7c', '#f6a196', '#ffbcb1', '#ffd9d0', '#a84f5a'],
    'white':  ['#b9bdd8', '#d5d9ee', '#ffffff', '#ffffff', '#ffffff', '#8f93b8'],
    'hair':   ['#3d2010', '#4f2a15', '#71401f', '#9a5a33', '#b36f42', '#2a1409'],
    'skin':   ['#c47562', '#e39b78', '#f8c49c', '#ffe0c4', '#fff0e2', '#a8584a'],
    'orange': ['#9c3712', '#c84b16', '#f2681f', '#ff9447', '#ffb27a', '#6e260c'],
    'blue':   ['#16348a', '#1b45b3', '#2563e8', '#4d8bff', '#7aa8ff', '#0f2468'],
    'navy':   ['#071449', '#0a1d66', '#112d93', '#2448c4', '#3a60d8', '#040a2c'],
    'cuff':   ['#1a2f80', '#213b99', '#2f52c4', '#5679e4', '#7d97ee', '#111f58'],
    'shoe':   ['#b0a6c4', '#d3c9e0', '#f6f3f9', '#ffffff', '#ffffff', '#6e6487'],
    'lav':    ['#8f74d6', '#a08af0', '#b49cf5', '#c9b8ff', '#e0d6ff', '#5d4aa0'],
}
RAMPS = {k: [hexc(c) for c in v] for k, v in RAMPS.items()}
OL = hexc('#1c1229')
FACE = {k: hexc(v) for k, v in dict(
    K='#2b1410', B='#3a1f10', M='#4a1420', m='#7a1f2e', r='#f0707e', T='#ffffff',
    P='#ff8f8a', p='#ffb3ad', S='#e39b78').items()}

LIGHT = np.array([-0.5, -0.68, 0.55])
LIGHT /= np.linalg.norm(LIGHT)

# material groups
(HELM, HELM_IN, CAP, RING, BALL, FACE_SKIN, HAIR, NECK, SH_O, SH_B, COLLAR, V_SKIN, HEM,
 SL_O, SL_B, ARM, NAVY, CUFF, SHOE) = range(19)
GROUP_RAMP = {HELM: 'cyan', HELM_IN: 'cyan_in', CAP: 'pink', RING: 'white', BALL: 'pink',
              FACE_SKIN: 'skin', HAIR: 'hair', NECK: 'skin', SH_O: 'orange', SH_B: 'blue',
              COLLAR: 'white', V_SKIN: 'skin', HEM: 'white', SL_O: 'orange', SL_B: 'blue',
              ARM: 'skin', NAVY: 'navy', CUFF: 'cuff', SHOE: 'shoe'}


# ---------------------------------------------------------------- geometry
def quad(A, B, C):
    disc = B * B - 4 * A * C
    ok = disc >= 0
    sq = np.sqrt(np.where(ok, disc, 0))
    A2 = np.where(np.abs(A) < 1e-9, 1e-9, 2 * A)
    t1 = np.where(ok, (-B - sq) / A2, np.inf)
    t2 = np.where(ok, (-B + sq) / A2, np.inf)
    return t1, t2


def ellipsoid(o, d, c, axes, r):
    """axes: 3x3 rows = unit axes of the ellipsoid; r radii. returns t1,t2,M"""
    M = np.asarray(axes, float) / np.asarray(r, float)[:, None]
    oo = (o - c) @ M.T
    dd = d @ M.T
    A = (dd * dd).sum(-1)
    B = 2 * (oo * dd).sum(-1)
    C = (oo * oo).sum(-1) - 1
    t1, t2 = quad(A, B, C)
    return t1, t2, M


def ell_normal(p, c, M):
    q = (p - c) @ M.T
    return q @ M


def vsection(o, d, cx, cz, a, b, y0, y1):
    a = np.maximum(a, 1e-3)
    b = np.maximum(b, 1e-3)
    ox, oz = o[..., 0] - cx, o[..., 2] - cz
    dx, dz = d[..., 0], d[..., 2]
    A = (dx / a) ** 2 + (dz / b) ** 2
    B = 2 * (ox * dx / a ** 2 + oz * dz / b ** 2)
    C = (ox / a) ** 2 + (oz / b) ** 2 - 1
    t1, t2 = quad(A, B, C)
    y = o[..., 1]
    valid = (y >= y0) & (y < y1)
    return np.where(valid, t1, np.inf), np.where(valid, t2, np.inf)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


# ---------------------------------------------------------------- model
HELM_C = np.array([0, 40, 0.0]); HELM_R = np.array([31, 30, 31.0])
HEAD_C = np.array([0, 47.5, 0.0]); HEAD_R = np.array([18.2, 16.6, 17.5])
HAIR_C = np.array([0, 46.0, -6.0]); HAIR_R = np.array([22.6, 16.2, 20.5])
BALL_D = np.array([0, -math.sin(math.radians(37)), math.cos(math.radians(37))])
I3 = np.eye(3)

BANG_X = [-17, -15.6, -14.0, -12.0, -10.2, -8.4, -6.6, -4.6, -2.6, -0.6, 1.4, 3.4, 5.4, 7.3,
          9.2, 11.0, 12.8, 14.3, 15.7, 17]
BANG_Y = [53, 47.5, 43.0, 41.2, 39.4, 41.4, 38.6, 40.8, 38.2, 40.4, 38.0, 40.4, 38.4, 40.8,
          38.8, 41.2, 40.0, 43.0, 47.5, 53]


def brim_region(p):
    """pink cap (brim + crown) / ring / ball on the helmet surface (local coords)."""
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    lam = np.arctan2(x, z)
    t = lam / 1.32
    btop = 31.2 + 3.2 * t ** 2
    bbot = 39.4 + 0.9 * np.sin(1.5 * np.pi * (t + 1) + 0.3) - 2.4 * np.abs(t) ** 3
    brim = (z > 0) & (np.abs(t) <= 1) & (y >= btop) & (y <= bbot)
    w = 0.26 + np.clip((y - 21) / 11.5, 0, 1) * 0.62
    crown = (z > 0) & (y >= 21) & (y <= 34) & (np.abs(lam) < w)
    q = unit((p - HELM_C) / HELM_R)
    ang = np.arccos(np.clip((q * BALL_D).sum(-1), -1, 1))
    ball = ang < 0.29
    ring = (ang >= 0.29) & (ang < 0.355)
    return brim | crown, ring, ball


def helm_removed(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    cap, ring, ball = brim_region(p)
    front = (z > 0) & (np.abs(x) < 21.0) & (y > 35.5)
    bottom = (np.abs(x) < 21.0) & (y > 52.5 + 7.5 * np.clip(-z / 20, 0, 1) + 0.006 * x ** 2)
    return (front | bottom) & ~(cap | ring | ball)


def torso_ab(y):
    s = np.where(y < 71, np.clip(1 - np.clip((71 - y) / 7.6, 0, 1) ** 2.6, 0, 1) ** (1 / 2.6),
                 1 + (y - 71) * 0.008)
    return 16.4 * s, 12.4 * s



# ---------------------------------------------------------------- soft hat (SDF ray-march)
def sd_ell(p, c, r):
    q = (p - np.asarray(c, float)) / np.asarray(r, float)
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / np.asarray(r, float), axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


VIS_A = math.radians(16)          # visor tilt (front edge down)
CROWN_C = np.array([0, 22.5, 13.0]); CROWN_R = np.array([16.0, 12.8, 15.5])
TOP_D = np.array([0, -0.74, 0.67]); TOP_D = TOP_D / np.linalg.norm(TOP_D)


def hat_parts(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    dome = sd_ell(p, (0, 35.5, -1.0), (27.5, 25.0, 26.5))
    dome = smax(dome, y - 41.0, 2.0)
    flaps = np.minimum(sd_ell(p, (-21.8, 51.5, -1.5), (5.6, 12.0, 8.6)),
                       sd_ell(p, (21.8, 51.5, -1.5), (5.6, 12.0, 8.6)))
    cyan = smin(dome, flaps, 4.0)
    crown = sd_ell(p, CROWN_C, CROWN_R)
    q = p - np.array([0, 32.0, 24.0])
    ca, sa = math.cos(VIS_A), math.sin(VIS_A)
    qy = q[..., 1] * ca - q[..., 2] * sa
    qz = q[..., 1] * sa + q[..., 2] * ca
    qx = q[..., 0]
    qy = qy - 0.7 * np.sin(qx * 0.42 + 0.4) * np.clip(qz / 13 + 0.6, 0, 1)
    vis = sd_ell(np.stack([qx, qy, qz], -1), (0, 0, 0), (23.5, 2.3, 13.0))
    vis = smax(vis, -qz - 2.0, 1.0)          # only the front part of the plate
    return cyan, crown, vis


def hat_sdf(p):
    cyan, crown, vis = hat_parts(p)
    return np.minimum(np.minimum(cyan, crown), vis)


def march_hat(o, d):
    c = np.array([0, 40.0, 4.0]); R = 42.0
    oc = o - c
    b = (oc * d).sum(-1)
    cc = (oc * oc).sum(-1) - R * R
    disc = b * b - cc
    ok = disc > 0
    sq = np.sqrt(np.where(ok, disc, 0))
    t = np.where(ok, -b - sq, np.inf)
    tmax = np.where(ok, -b + sq, -np.inf)
    t = np.where(ok, t, 0)
    active = ok.copy()
    hit = np.zeros_like(ok)
    for _ in range(220):
        if not active.any():
            break
        p = o + t[..., None] * d
        dist = hat_sdf(p)
        newhit = active & (dist < 0.03)
        hit |= newhit
        active &= ~newhit
        t = np.where(active, t + np.maximum(dist * 0.75, 0.02), t)
        active &= t < tmax
    return np.where(hit, t, np.inf)


def hat_normal(p):
    e = 0.12
    n = np.zeros_like(p)
    for i in range(3):
        dv = np.zeros(3); dv[i] = e
        n[..., i] = hat_sdf(p + dv) - hat_sdf(p - dv)
    return n


def render(phi, hop=0.0, arm=25.0):
    with np.errstate(all='ignore'):
        return _render(phi, hop, arm)


def _render(phi, hop=0.0, arm=25.0):
    cphi, sphi = math.cos(phi), math.sin(phi)
    Xu = (xx + 0.5) / K - PIV
    Yu = (yy + 0.5) / K + hop
    Z0 = 300.0
    o = np.stack([Xu * cphi - Z0 * sphi, Yu, Xu * sphi + Z0 * cphi], -1)
    d = np.broadcast_to(np.array([sphi, 0.0, -cphi]), o.shape)
    Y = o[..., 1]

    depth = np.full((H, W), np.inf)
    pid = np.full((H, W), -1)
    NL = np.zeros((H, W, 3))
    PL = np.zeros((H, W, 3))
    INNER = np.zeros((H, W), bool)

    def commit(t, k, nfun, inner=None):
        m = t < depth
        if not m.any():
            return
        p = o + t[..., None] * d
        n = nfun(p)
        depth[m] = t[m]
        pid[m] = k
        PL[m] = p[m]
        NL[m] = n[m]
        INNER[m] = False if inner is None else inner[m]

    prims = []

    # soft hat (dome + ear flaps) with pink cap on top
    th = march_hat(o, d)
    commit(th, 0, hat_normal)
    prims.append('hat')

    t1, _, M = ellipsoid(o, d, HEAD_C, I3, HEAD_R)
    commit(t1, 1, lambda p: ell_normal(p, HEAD_C, M)); prims.append('head')
    t1, _, M2 = ellipsoid(o, d, HAIR_C, I3, HAIR_R)
    commit(t1, 2, lambda p: ell_normal(p, HAIR_C, M2)); prims.append('hair')

    t1, _ = vsection(o, d, 0, -1.5, 6.0, 6.0, 57, 68)
    commit(t1, 3, lambda p: np.stack([p[..., 0], 0 * p[..., 0], p[..., 2] + 1.5], -1)); prims.append('neck')

    a, b = torso_ab(Y)
    t1, _ = vsection(o, d, 0, 0, a, b, 63.4, 86.5)

    def torso_n(p):
        aa, bb = torso_ab(p[..., 1])
        ny = -np.clip((71 - p[..., 1]) / 7.6, 0, 1) ** 1.6 * 0.12
        return np.stack([p[..., 0] / aa ** 2, ny, p[..., 2] / bb ** 2], -1)
    commit(t1, 4, torso_n); prims.append('torso')

    t1, _ = vsection(o, d, 0, 0, 15.9, 11.9, 84, 89)
    commit(t1, 5, lambda p: np.stack([p[..., 0] / 15.9 ** 2, 0 * p[..., 0], p[..., 2] / 11.9 ** 2], -1))
    prims.append('hem')

    # arms
    al = math.radians(arm)
    for s in (-1, 1):
        sh = np.array([s * 12.0, 68.0, 0.0])
        u = np.array([s * math.cos(al), -math.sin(al), 0.0])
        v = np.array([math.sin(al), s * math.cos(al), 0.0]) * s
        w = np.array([0, 0, 1.0])
        ax = np.stack([u, v, w])
        c = sh + u * 5.0
        t1, _, Ms = ellipsoid(o, d, c, ax, [7.6, 6.3, 6.0])
        commit(t1, 6 + (s > 0), (lambda c, Ms: lambda p: ell_normal(p, c, Ms))(c, Ms))
        c2 = sh + u * 13.2
        t1, _, Mf = ellipsoid(o, d, c2, ax, [6.4, 3.5, 3.5])
        commit(t1, 8 + (s > 0), (lambda c, Mf: lambda p: ell_normal(p, c, Mf))(c2, Mf))
        c3 = sh + u * 19.2
        t1, _, Mh = ellipsoid(o, d, c3, I3, [4.4, 4.4, 4.4])
        commit(t1, 10 + (s > 0), (lambda c, Mh: lambda p: ell_normal(p, c, Mh))(c3, Mh))
    prims += ['sleeveL', 'sleeveR', 'foreL', 'foreR', 'handL', 'handR']
    SHOULDERS = {s: (np.array([s * 12.0, 68.0, 0.0]),
                     np.array([s * math.cos(al), -math.sin(al), 0.0])) for s in (-1, 1)}

    # pants / cuffs / shoes
    HC = np.array([0, 89.5, 0.0])
    t1, _, Mp = ellipsoid(o, d, HC, I3, [15.6, 6.4, 11.6])
    commit(t1, 12, lambda p: ell_normal(p, HC, Mp))
    for s in (-1, 1):
        cxl = s * 8.3
        aa = 6.7 + (Y - 91) * 0.11
        bb = 6.8 + (Y - 91) * 0.06
        t1, _ = vsection(o, d, cxl, 0, aa, bb, 89, 106.5)
        commit(t1, 13, (lambda cxl: lambda p: np.stack(
            [(p[..., 0] - cxl) / (6.7 + (p[..., 1] - 91) * 0.11) ** 2, 0 * p[..., 0],
             p[..., 2] / (6.8 + (p[..., 1] - 91) * 0.06) ** 2], -1))(cxl))
        t1, _ = vsection(o, d, s * 8.5, 0, 8.7, 8.4, 102.4, 108.2)
        commit(t1, 14, (lambda cx: lambda p: np.stack(
            [(p[..., 0] - cx) / 8.7 ** 2, 0 * p[..., 0], p[..., 2] / 8.4 ** 2], -1))(s * 8.5))
        cs = np.array([s * 8.4, 108.8, 2.8])
        t1, _, Mz = ellipsoid(o, d, cs, I3, [5.6, 3.1, 7.8])
        commit(t1, 15, (lambda c, Mz: lambda p: ell_normal(p, c, Mz))(cs, Mz))

    # ------------------------------------------------------------ materials
    hit = pid >= 0
    nW = unit(NL)
    nw = np.stack([nW[..., 0] * cphi + nW[..., 2] * sphi, nW[..., 1],
                   -nW[..., 0] * sphi + nW[..., 2] * cphi], -1)
    inten = (nw * LIGHT).sum(-1)
    grp = np.full((H, W), -1)
    x, y, z = PL[..., 0], PL[..., 1], PL[..., 2]

    m = pid == 0
    cyan_d, crown_d, vis_d = hat_parts(PL)
    pinkpart = np.minimum(crown_d, vis_d) < cyan_d
    q = unit((PL - CROWN_C) / CROWN_R)
    ang = np.arccos(np.clip((q * TOP_D).sum(-1), -1, 1))
    oncrown = crown_d <= vis_d
    grp[m] = HELM
    grp[m & pinkpart] = CAP
    grp[m & pinkpart & oncrown & (ang < 0.56)] = BALL
    grp[m & pinkpart & oncrown & (ang >= 0.56) & (ang < 0.70)] = RING
    part = pid.copy()
    part[m & pinkpart & oncrown] = 16
    part[m & pinkpart & ~oncrown] = 17

    m = pid == 1
    bang = np.interp(x, BANG_X, BANG_Y)
    lam_h = np.arctan2(x / HEAD_R[0], z / HEAD_R[2])
    skin = (z > 0) & (np.abs(lam_h) < 1.02) & (y > bang)
    grp[m] = HAIR
    grp[m & skin] = FACE_SKIN
    grp[pid == 2] = HAIR
    grp[pid == 3] = NECK

    m = pid == 4
    rel = y
    orange = (rel < 68.6) | ((rel >= 72.4) & (rel < 77)) | (rel >= 80.6)
    grp[m] = np.where(orange, SH_O, SH_B)[m]
    ax_ = np.abs(x)
    front = z > 0
    collar = front & (y < 65.6 + np.clip(6.5 - ax_, 0, None) * 0.95) & (ax_ < 11.5)
    collar |= ~front & (y < 66.2)
    vwhite = front & (ax_ < (71.2 - y) * 0.72) & (y < 71.2)
    vskin = front & (ax_ < (69.0 - y) * 0.62) & (y < 69.0)
    grp[m & collar] = COLLAR
    grp[m & vwhite] = COLLAR
    grp[m & vskin] = V_SKIN
    grp[pid == 5] = HEM

    for k, s in ((6, -1), (7, 1)):
        m = pid == k
        sh, u = SHOULDERS[s]
        along = ((PL - sh) * u).sum(-1)
        ring_o = (along < 3.2) | ((along >= 6.4) & (along < 9.4))
        grp[m] = np.where(ring_o, SL_O, SL_B)[m]
    for k in (8, 9, 10, 11):
        grp[pid == k] = ARM
    grp[(pid == 12) | (pid == 13)] = NAVY
    grp[pid == 14] = CUFF
    grp[pid == 15] = SHOE

    # shading level 0..4
    lvl = np.full((H, W), 2)
    lvl[inten < 0.40] = 1
    lvl[inten < -0.32] = 0
    lvl[inten > 0.80] = 3
    hi_groups = np.isin(grp, [BALL])
    lvl[hi_groups & (inten > 0.95)] = 4
    lvl[(grp == HELM_IN)] = np.clip(lvl[grp == HELM_IN] - 1, 0, 2)
    # soft shadow cast by the hat rim / visor
    under = np.isin(grp, [FACE_SKIN, HAIR]) & (y < 43.6)
    lvl[under] = np.clip(lvl[under] - 1, 0, 3)
    lvl[np.isin(grp, [CAP]) & (nw[..., 1] > 0.35)] = np.minimum(lvl[np.isin(grp, [CAP]) & (nw[..., 1] > 0.35)], 1)
    # neck & v-neck sit in shadow
    lvl[np.isin(grp, [NECK, V_SKIN])] = np.minimum(lvl[np.isin(grp, [NECK, V_SKIN])], 1)
    # cuff top rim + fold line
    lvl[(grp == CUFF) & (y < 103.6)] = 3
    lvl[(grp == CUFF) & (y > 105.4) & (y < 106.4)] = np.minimum(lvl[(grp == CUFF) & (y > 105.4) & (y < 106.4)], 1)

    img = np.zeros((H, W, 4), np.uint8)
    for gname, rname in GROUP_RAMP.items():
        mm = grp == gname
        if not mm.any():
            continue
        ramp = RAMPS[rname]
        for L in range(5):
            img[mm & (lvl == L)] = ramp[L]
    # lavender reflected light on the dark side of the sleeves
    img[np.isin(grp, [SL_O, SL_B]) & (lvl == 0) & (nw[..., 0] < 0)] = RAMPS['lav'][2]

    # ------------------------------------------------------------ lines
    def nb(a, dx, dy, fill):
        out = np.full_like(a, fill)
        out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = \
            a[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
        return out

    line = np.zeros((H, W), bool)
    soft = np.zeros((H, W), bool)
    pair_lines = {(HELM, CAP), (HELM, RING), (CAP, RING), (SH_O, COLLAR), (SH_B, COLLAR),
                  (V_SKIN, COLLAR), (HELM, BALL)}
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dn = nb(depth, dx, dy, np.inf)
        gn = nb(grp, dx, dy, -1)
        pn = nb(part, dx, dy, -1)
        line |= hit & (gn >= 0) & (((dn < depth - 2.6) & (pn != part)) | (dn < depth - 9.0))
        for a_, b_ in pair_lines:
            line |= (grp == a_) & (gn == b_)
        soft |= (grp == FACE_SKIN) & (gn == HAIR) & (np.abs(dn - depth) < 2.6)
    for gname, rname in GROUP_RAMP.items():
        mm = line & (grp == gname)
        img[mm] = RAMPS[rname][5]
    img[soft & ~line] = RAMPS['skin'][1]

    # ------------------------------------------------------------ face sprites
    def place(lx, ly, variants, cmap, only=(FACE_SKIN,), anchor='c'):
        lz = HEAD_R[2] * math.sqrt(max(0.0, 1 - (lx / HEAD_R[0]) ** 2 - ((ly - HEAD_C[1]) / HEAD_R[1]) ** 2))
        n = np.array([lx / HEAD_R[0] ** 2, (ly - HEAD_C[1]) / HEAD_R[1] ** 2, lz / HEAD_R[2] ** 2])
        n /= np.linalg.norm(n)
        facing = -n[0] * sphi + n[2] * cphi
        if facing < 0.18:
            return
        wx = lx * cphi + lz * sphi
        px_ = (wx + PIV) * K
        py_ = (ly - hop) * K
        rows = variants[0]
        for thr, v in variants:
            if facing >= thr:
                rows = v
                break
        else:
            return
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

    eye_v = [(0.80, ["..KKKK..", ".KK..KK.", "KK....KK", "K......K"]),
             (0.55, [".KKKK.", "KK..KK", "K....K"]),
             (0.32, [".KK.", "K..K", "K..K"]),
             (0.18, ["KK", "K."])]
    for s in (-1, 1):
        place(s * 7.4, 47.2, eye_v, FACE)
        place(s * 12.4, 51.6, [(0.7, [".PpP.", "PPPPP"]), (0.4, ["PpP", "PPP"]), (0.18, ["P", "P"])], FACE)
    brow_v = [(0.80, ["..BBBB..", ".BBBBBB.", "BB....BB"]),
              (0.55, [".BBBB.", "BB..BB"]),
              (0.32, ["BBB", "B.B"]),
              (0.18, ["B", "B"])]
    for s in (-1, 1):
        place(s * 7.6, 42.4, brow_v, FACE, only=(FACE_SKIN, HAIR))
    mouth_v = [(0.82, ["MMMMMMMMMM", "MTTTTTTTTM", "MmmmmmmmmM", ".MmmrrrmM.", "..MrrrrM..", "...MMMM..."]),
               (0.55, ["MMMMMMM", "MTTTTTM", "MmmmmmM", ".MmrrM.", "..MMM.."]),
               (0.30, ["MMMM", "MTTM", "MmrM", ".MM."]),
               (0.18, ["MM", "Mm", "M."])]
    place(0, 54.6, mouth_v, FACE)

    # ------------------------------------------------------------ outline
    solid = img[..., 3] > 0
    ring_ = np.zeros_like(solid)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring_ |= nb(solid, dx, dy, False)
    img[ring_ & ~solid] = OL
    return img


if __name__ == '__main__':
    import sys
    n = 16
    frames = [render(2 * math.pi * i / n) for i in range(n)]
    big = []
    for f in frames:
        im = Image.new('RGBA', (W, H), (236, 241, 252, 255))
        im.alpha_composite(Image.fromarray(f))
        big.append(im.resize((W * 3, H * 3), Image.NEAREST))
    cs = Image.new('RGB', (W * 3 * 8, H * 3 * 2), 'white')
    for i, b in enumerate(big):
        cs.paste(b, ((i % 8) * W * 3, (i // 8) * H * 3))
    cs.save('spin_contact.png')
    big0 = Image.new('RGBA', (W, H), (236, 241, 252, 255))
    big0.alpha_composite(Image.fromarray(frames[0]))
    big0.resize((W * 6, H * 6), Image.NEAREST).save('spin_front.png')
    print(W, H)

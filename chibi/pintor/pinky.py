"""Chibi pixel-art spin of the pink-haired character (overalls), new pose:
one arm out with the palm up, the other hand on the hip.

Same approach as spin.py: simple 3D primitives / SDFs ray-cast at pixel
resolution with cel shading and outlines; face details are sprites placed on
the head surface so they turn with it.
"""
import math
import numpy as np
from PIL import Image

K = 0.85
WU, HU = 124, 124
W, H = int(round(WU * K)), int(round(HU * K))
yy, xx = np.mgrid[0:H, 0:W]
PIV = WU / 2


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


# ramps: dk, sh, b, lt, hi, line
RAMPS = {
    'hair':  ['#a3164a', '#cf2560', '#f03d74', '#ff86aa', '#ffc2d4', '#6e0d33'],
    'skin':  ['#c98a64', '#eaa77c', '#f9c79f', '#ffdfc2', '#fff0e0', '#9a5238'],
    'gray':  ['#8a8a98', '#adadb9', '#d4d4dc', '#ececf2', '#ffffff', '#5e5e6e'],
    'over':  ['#2b1159', '#3d1a7a', '#5a2aa8', '#7a4ccc', '#9a72e0', '#1a0838'],
    'boot':  ['#1d0c3d', '#2b1557', '#3d207a', '#5a38a8', '#a68ce6', '#120625'],
    'yel':   ['#b08a10', '#d8aa18', '#f5cc2a', '#ffe46e', '#fff4b0', '#6e5208'],
}
RAMPS = {k: [hexc(c) for c in v] for k, v in RAMPS.items()}
OL = hexc('#1a1024')
FACE = {k: hexc(v) for k, v in dict(
    K='#16101c', W='#ffffff', L='#e6d8f0', P='#16101c', n='#9a5238', M='#3a1c18').items()}

LIGHT = np.array([-0.5, -0.68, 0.55])
LIGHT /= np.linalg.norm(LIGHT)

(FACE_SKIN, HAIR, SKIN, GRAY, OVER, BOOT, YEL, POCKET) = range(8)
GROUP_RAMP = {FACE_SKIN: 'skin', HAIR: 'hair', SKIN: 'skin', GRAY: 'gray', OVER: 'over',
              BOOT: 'boot', YEL: 'yel', POCKET: 'over'}
I3 = np.eye(3)


# ---------------------------------------------------------------- geometry helpers
def quad(A, B, C):
    disc = B * B - 4 * A * C
    ok = disc >= 0
    sq = np.sqrt(np.where(ok, disc, 0))
    A2 = np.where(np.abs(A) < 1e-9, 1e-9, 2 * A)
    return np.where(ok, (-B - sq) / A2, np.inf), np.where(ok, (-B + sq) / A2, np.inf)


def ellipsoid(o, d, c, axes, r):
    M = np.asarray(axes, float) / np.asarray(r, float)[:, None]
    oo = (o - c) @ M.T
    dd = d @ M.T
    t1, t2 = quad((dd * dd).sum(-1), 2 * (oo * dd).sum(-1), (oo * oo).sum(-1) - 1)
    return t1, t2, M


def ell_normal(p, c, M):
    return ((p - c) @ M.T) @ M


def vsection(o, d, cx, cz, a, b, y0, y1):
    a = np.maximum(a, 1e-3)
    b = np.maximum(b, 1e-3)
    ox, oz = o[..., 0] - cx, o[..., 2] - cz
    dx, dz = d[..., 0], d[..., 2]
    t1, t2 = quad((dx / a) ** 2 + (dz / b) ** 2, 2 * (ox * dx / a ** 2 + oz * dz / b ** 2),
                  (ox / a) ** 2 + (oz / b) ** 2 - 1)
    valid = (o[..., 1] >= y0) & (o[..., 1] < y1)
    return np.where(valid, t1, np.inf), np.where(valid, t2, np.inf)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def sd_ell(p, c, r):
    q = (p - np.asarray(c, float)) / np.asarray(r, float)
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / np.asarray(r, float), axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def axes_from(u, up=(0, 0, 1.0)):
    u = np.asarray(u, float); u = u / np.linalg.norm(u)
    w = np.asarray(up, float)
    w = w - u * (w @ u)
    if np.linalg.norm(w) < 1e-6:
        w = np.array([0, 1.0, 0]) - u * u[1]
    w /= np.linalg.norm(w)
    v = np.cross(w, u)
    return np.stack([u, v, w])


# ---------------------------------------------------------------- model
HEAD_C = np.array([0, 45.0, 0.0]); HEAD_R = np.array([18.0, 16.8, 17.0])
HC = np.array([0, 31.0, -5.0]); HR = np.array([26.0, 21.0, 24.0])
LOBE_R = 9.6


def _lobes(n=34):
    cs, axs = [], []
    ga = math.pi * (3 - math.sqrt(5))
    down = np.array([0, 1.0, 0])
    for i in range(n):
        uy = 1 - 2 * (i + 0.5) / n
        rad = math.sqrt(1 - uy * uy)
        th = ga * i + 0.4
        u = np.array([math.cos(th) * rad, uy, math.sin(th) * rad])
        c = HC + HR * u * 0.84
        if c[1] > 54:
            continue
        if u[2] > 0.12 and abs(c[0]) < 16.5 and c[1] > 33.5:
            continue
        nrm = (c - HC) / HR ** 2
        nrm /= np.linalg.norm(nrm)
        t = down - nrm * (nrm @ down)
        if np.linalg.norm(t) < 0.25:
            t = np.cross(nrm, np.array([0, 0, 1.0]))
        t /= np.linalg.norm(t)
        beta = 0.55 * (1 if c[0] >= 0 else -1) * (0.4 + 0.6 * min(1, abs(c[0]) / 15))
        bt = np.cross(nrm, t)
        t = t * math.cos(beta) - bt * math.sin(beta)
        t /= np.linalg.norm(t)
        side = np.cross(nrm, t)
        cs.append(c)
        axs.append(np.stack([t, side, nrm]))
    return np.array(cs), np.array(axs)


LOBES, LOBE_AX = _lobes()
LOBE_RR = np.array([12.0, 7.6, 6.4])
BANG_A = math.radians(22)
BANG_C = np.array([-6.0, 39.6, 15.2])
BANG_AX = np.stack([[math.cos(BANG_A), -math.sin(BANG_A), 0], [math.sin(BANG_A), math.cos(BANG_A), 0], [0, 0, 1.0]])
BANG_R = np.array([11.5, 4.8, 5.4])
SIDE = [((-18.2, 54.5, 1.0), (3.6, 5.6, 4.2)), ((18.2, 54.5, 1.0), (3.6, 5.6, 4.2))]
NAPE = ((0, 48.0, -10.0), (19.0, 13.0, 13.0))
TUFTS = []
for c, dv, r in [((-23.0, 22.0, -2.0), (-0.5, 0.86, 0.0), (10.5, 5.8, 5.2)),
                 ((23.0, 19.0, -3.0), (0.55, 0.83, 0.0), (10.5, 5.8, 5.2)),
                 ((-25.0, 37.0, -3.0), (-0.35, 0.94, 0.0), (9.0, 5.2, 4.6)),
                 ((25.0, 35.0, -3.0), (0.4, 0.92, 0.0), (9.0, 5.2, 4.6)),
                 ((-5.0, 10.0, 1.0), (1.0, 0.18, 0.0), (10.5, 4.6, 6.5)),
                 ((10.0, 12.0, -6.0), (0.75, 0.66, 0.0), (8.0, 4.4, 5.5)),
                 ((0.0, 31.0, -27.0), (0.0, 0.95, -0.3), (11.0, 6.2, 5.0))]:
    dv = np.array(dv); dv /= np.linalg.norm(dv)
    TUFTS.append((np.array(c), axes_from(dv), np.array(r)))


def hair_parts(p):
    """distance to every hair piece -> (n_pieces, ...)"""
    flat = p.reshape(-1, 3)
    q = flat[:, None, :] - LOBES[None]
    ql = np.einsum('mni,nji->mnj', q, LOBE_AX) / LOBE_RR
    k0 = np.linalg.norm(ql, axis=-1)
    k1 = np.linalg.norm(ql / LOBE_RR, axis=-1)
    dl = k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
    bang = sd_ell((p - BANG_C) @ BANG_AX.T, (0, 0, 0), BANG_R).reshape(-1)
    extra = [bang] + [sd_ell(p, c, r).reshape(-1) for c, r in SIDE] + [sd_ell(p, *NAPE).reshape(-1)]
    extra += [sd_ell((p - c) @ ax.T, (0, 0, 0), r).reshape(-1) for c, ax, r in TUFTS]
    return dl, np.stack(extra, 1)


def hair_sdf(p):
    core = sd_ell(p, HC, HR - 2.6)
    dl, ex = hair_parts(p)
    h = smin(core.reshape(-1), dl.min(1), 1.2)
    return np.minimum(h, ex.min(1)).reshape(p.shape[:-1])


def march_sdf(o, d, f, c, R, steps=200, k=0.6):
    oc = o - c
    b = (oc * d).sum(-1)
    cc = (oc * oc).sum(-1) - R * R
    disc = b * b - cc
    ok = disc > 0
    sq = np.sqrt(np.where(ok, disc, 0))
    t = np.where(ok, -b - sq, 0.0)
    tmax = np.where(ok, -b + sq, -np.inf)
    active = ok.copy()
    hit = np.zeros_like(ok)
    for _ in range(steps):
        if not active.any():
            break
        idx = np.nonzero(active)
        p = o[idx] + t[idx][..., None] * d[idx]
        dist = f(p)
        nh = dist < 0.03
        hit[tuple(i[nh] for i in idx)] = True
        t[idx] = np.where(nh, t[idx], t[idx] + np.maximum(dist * k, 0.02))
        active[idx] = ~nh & (t[idx] < tmax[idx])
    return np.where(hit, t, np.inf)


def sdf_normal(f, p):
    e = 0.12
    n = np.zeros_like(p)
    for i in range(3):
        dv = np.zeros(3); dv[i] = e
        n[..., i] = f(p + dv) - f(p - dv)
    return n


def torso_ab(y):
    s = np.where(y < 71, np.clip(1 - np.clip((71 - y) / 7.6, 0, 1) ** 2.6, 0, 1) ** (1 / 2.6),
                 1 + (y - 71) * 0.008)
    return 16.0 * s, 12.2 * s


def render(phi, hop=0.0, wave=0.0):
    with np.errstate(all='ignore'):
        return _render(phi, hop, wave)


def _render(phi, hop=0.0, wave=0.0):
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

    def commit(t, k, nfun):
        m = t < depth
        if not m.any():
            return
        p = o + t[..., None] * d
        n = nfun(p)
        depth[m] = t[m]
        pid[m] = k
        PL[m] = p[m]
        NL[m] = n[m]

    def ell(k, c, ax, r):
        c = np.asarray(c, float)
        t1, _, M = ellipsoid(o, d, c, ax, r)
        commit(t1, k, lambda p: ell_normal(p, c, M))

    # head, ears, hair
    ell(1, HEAD_C, I3, HEAD_R)
    for s in (-1, 1):
        ell(2, (s * 17.4, 47.5, -1.0), I3, (2.6, 4.2, 3.4))
    th = march_sdf(o, d, hair_sdf, np.array([0, 34.0, -3.0]), 40.0)
    commit(th, 0, lambda p: sdf_normal(hair_sdf, p))

    # neck + hood collar
    t1, _ = vsection(o, d, 0, -1.5, 6.0, 6.0, 57, 68)
    commit(t1, 3, lambda p: np.stack([p[..., 0], 0 * p[..., 0], p[..., 2] + 1.5], -1))
    ell(4, (0, 64.2, -2.6), I3, (11.8, 4.0, 10.2))

    # torso (shirt + overall bib)
    a, b = torso_ab(Y)
    t1, _ = vsection(o, d, 0, 0, a, b, 63.4, 88.0)

    def torso_n(p):
        aa, bb = torso_ab(p[..., 1])
        ny = -np.clip((71 - p[..., 1]) / 7.6, 0, 1) ** 1.6 * 0.12
        return np.stack([p[..., 0] / aa ** 2, ny, p[..., 2] / bb ** 2], -1)
    commit(t1, 5, torso_n)

    # ---- arms
    arm_parts = []
    # A) character's right arm (local -x): out to the side, palm up
    al = math.radians(12 + wave)
    sh = np.array([-12.0, 67.5, 0.0])
    u = np.array([-math.cos(al), -math.sin(al), 0.0])
    ax = axes_from(u)
    ell(6, sh + u * 5.5, ax, (7.0, 4.7, 4.7))
    ell(6, sh + u * 13.6, ax, (6.4, 4.0, 4.0))
    ell(7, sh + u * 19.2, ax, (2.0, 4.8, 4.8))                    # rolled cuff
    palm_c = sh + u * 25.2 + np.array([0, 0.6, 0])
    pax = np.stack([u, np.array([0, 1.0, 0]) - u * u[1], np.array([0, 0, 1.0])])
    pax[1] /= np.linalg.norm(pax[1])
    ell(8, palm_c, pax, (6.8, 2.6, 6.2))                           # open palm (flat, facing up)
    ell(8, palm_c + np.array([0, -1.4, 5.2]) - u * 2.0, I3, (2.3, 2.3, 2.3))   # thumb
    arm_parts.append(('palm', palm_c, u))
    # B) character's left arm (local +x): hand on the hip
    S = np.array([12.0, 67.5, 0.0]); E = np.array([23.0, 76.5, -3.0]); Hh = np.array([16.6, 86.6, 1.6])
    for (p0, p1, rr, k) in ((S, E, 4.7, 6), (E, Hh, 4.0, 6)):
        uu = (p1 - p0) / np.linalg.norm(p1 - p0)
        ell(k, (p0 + p1) / 2, axes_from(uu), (np.linalg.norm(p1 - p0) / 2 + 1.6, rr, rr))
    uu = (Hh - E) / np.linalg.norm(Hh - E)
    ell(7, Hh - uu * 3.2, axes_from(uu), (1.9, 4.6, 4.6))
    ell(8, Hh + uu * 1.0, I3, (5.0, 5.0, 5.0))                    # fist on the hip

    # ---- overalls pants + boots
    hp = np.array([0, 87.5, 0.0])
    t1, _, Mp = ellipsoid(o, d, hp, I3, [15.4, 6.6, 11.6])
    commit(t1, 9, lambda p: ell_normal(p, hp, Mp))
    for s in (-1, 1):
        cxl = s * 7.9
        aa = 7.0 + (Y - 88) * 0.07
        t1, _ = vsection(o, d, cxl, 0, aa, 7.0, 87, 103.5)
        commit(t1, 9, (lambda cxl: lambda p: np.stack(
            [(p[..., 0] - cxl) / (7.0 + (p[..., 1] - 88) * 0.07) ** 2, 0 * p[..., 0], p[..., 2] / 49.0], -1))(cxl))
        t1, _ = vsection(o, d, s * 8.2, 0, 7.6, 7.6, 100.5, 107.5)
        commit(t1, 10, (lambda cx: lambda p: np.stack(
            [(p[..., 0] - cx) / 57.8, 0 * p[..., 0], p[..., 2] / 57.8], -1))(s * 8.2))
        ell(10, (s * 8.2, 107.8, 2.8), I3, (7.0, 4.4, 9.2))

    # ------------------------------------------------------------ materials
    hit = pid >= 0
    nW = unit(NL)
    nw = np.stack([nW[..., 0] * cphi + nW[..., 2] * sphi, nW[..., 1],
                   -nW[..., 0] * sphi + nW[..., 2] * cphi], -1)
    inten = (nw * LIGHT).sum(-1)
    x, y, z = PL[..., 0], PL[..., 1], PL[..., 2]
    grp = np.full((H, W), -1)
    part = pid.copy()

    # hair pieces (index for per-lock outlines)
    hm = pid == 0
    lidx = np.full((H, W), -1)
    if hm.any():
        dl, ex = hair_parts(PL[hm])
        allp = np.concatenate([dl, ex], 1)
        lidx[hm] = allp.argmin(1)
        crev = np.zeros((H, W), bool)
        crev[hm] = allp.min(1) > 0.6
    else:
        crev = np.zeros((H, W), bool)
    grp[hm] = HAIR
    grp[pid == 1] = FACE_SKIN
    grp[np.isin(pid, [2, 3, 8])] = SKIN
    grp[np.isin(pid, [4, 6, 7])] = GRAY
    grp[pid == 9] = OVER
    grp[pid == 10] = BOOT

    m = pid == 5
    ax_ = np.abs(x)
    front = z > 0
    bib = front & (ax_ < 9.6) & (y > 70.2)
    strap = (np.abs(ax_ - 7.6) < 2.3) & (y < 71.5) & front
    back_strap = ~front & (np.abs(ax_ - 6.6 + (y - 66) * 0.12) < 2.1) & (y < 80)
    back_panel = ~front & (ax_ < 10) & (y > 78)
    waist = y > 80.5
    over = bib | strap | back_strap | back_panel | waist
    grp[m] = GRAY
    grp[m & over] = OVER
    button = front & (((x - 7.6) ** 2 + (y - 71.4) ** 2) < 2.2) | front & (((x + 7.6) ** 2 + (y - 71.4) ** 2) < 2.2)
    grp[m & button] = YEL
    pocket = front & (ax_ < 4.4) & (y > 73.4) & (y < 78.4)
    grp[m & pocket & ~button] = POCKET
    part[m & over] = 50

    lvl = np.full((H, W), 2)
    lvl[inten < 0.40] = 1
    lvl[inten < -0.32] = 0
    lvl[inten > 0.80] = 3
    lvl[(grp == BOOT) & (inten > 0.93)] = 4
    lvl[(grp == YEL) & (inten > 0.6)] = 3
    lvl[crev] = np.clip(lvl[crev] - 1, 0, 3)
    lvl[grp == POCKET] = np.clip(lvl[grp == POCKET] - 1, 0, 3)
    # hair shine band (anime style), turns with the head
    lam = np.arctan2(x, z + 5)
    band_c = 23.5 + 2.5 * np.sin(lam * 1.3 + 0.5)
    shine = hm & (np.abs(y - band_c) < 2.3) & (lvl >= 1)
    lvl[shine] = np.maximum(lvl[shine], 3)
    lvl[shine & (np.abs(y - band_c) < 0.9) & (inten > 0.3)] = 4
    # neck in shadow, hair shadow on the forehead
    lvl[pid == 3] = np.minimum(lvl[pid == 3], 1)

    img = np.zeros((H, W, 4), np.uint8)
    for g, rname in GROUP_RAMP.items():
        mm = grp == g
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
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dn = nb(depth, dx, dy, np.inf)
        gn = nb(grp, dx, dy, -1)
        pn = nb(part, dx, dy, -1)
        line |= hit & (gn >= 0) & (((dn < depth - 2.6) & (pn != part)) | (dn < depth - 9.0))
        line |= (grp == OVER) & (gn == YEL)
        line |= (grp == POCKET) & (gn == OVER) & (np.abs(dn - depth) < 2)
        over_edge |= (grp == GRAY) & (gn == OVER) & (np.abs(dn - depth) < 2.6)
        soft |= (grp == FACE_SKIN) & (gn == HAIR) & (np.abs(dn - depth) < 2.6)
        li = nb(lidx, dx, dy, -1)
        lockl |= (lidx >= 0) & (li >= 0) & (li != lidx) & (dn < depth - 1.2)
    for g, rname in GROUP_RAMP.items():
        img[line & (grp == g)] = RAMPS[rname][5]
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
        for thr, v in variants:
            if facing >= thr:
                rows = v
                break
        if rows is None:
            return
        wx = lx * cphi + lz * sphi
        px_ = (wx + PIV) * K
        py_ = (ly - hop) * K
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

    eye_v = [(0.80, ["..KKK..", ".KLLLK.", "KWWWWWK", "KWWWPPK", "KWWWPPK", "KWWWWWK", ".KWWWK.", "..KKK.."]),
             (0.55, [".KKK.", "KLLLK", "KWWPK", "KWWPK", "KWWWK", ".KKK."]),
             (0.30, [".K.", "KLK", "KPK", "KWK", ".K."]),
             (0.16, ["K", "P", "K"])]
    for s in (-1, 1):
        place(s * 7.0, 46.4, eye_v, FACE)
    place(0.6, 52.4, [(0.75, [".nn.", "n..n"]), (0.45, ["nn", "n."]), (0.2, ["n"])], FACE)
    place(1.4, 56.0, [(0.75, [".....M", "M...M.", ".MMM.."]), (0.45, ["...M", "MMM."]), (0.2, ["MM"])], FACE)

    solid = img[..., 3] > 0
    ring_ = np.zeros_like(solid)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring_ |= nb(solid, dx, dy, False)
    img[ring_ & ~solid] = OL
    return img


if __name__ == '__main__':
    frames = [render(2 * math.pi * a / 16) for a in (0, 2, 4, 8)]
    ims = []
    for f in frames:
        im = Image.new('RGBA', (W, H), (236, 241, 252, 255))
        im.alpha_composite(Image.fromarray(f))
        ims.append(im.resize((W * 4, H * 4), Image.NEAREST))
    cs = Image.new('RGB', (W * 16, H * 4), 'white')
    for i, b in enumerate(ims):
        cs.paste(b, (i * W * 4, 0))
    cs.save('pinky_zoom.png')
    print(W, H, len(LOBES), 'lobes')

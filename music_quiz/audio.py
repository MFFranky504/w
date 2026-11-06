import numpy as np, wave, random
from tl import *
SR = 44100
N = int(END * SR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, g=1.0, pan=0.0, bus=None):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(0, -i); sig = sig[a:]; i = max(i, 0)
    sig = sig[:N - i]
    gl = g * (1 - max(pan, 0)); gr = g * (1 + min(pan, 0))
    (bus[0] if bus else L)[i:i + len(sig)] += sig * gl
    (bus[1] if bus else R)[i:i + len(sig)] += sig * gr

def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, k):  # moving-average lowpass
    c = np.cumsum(np.insert(x, 0, 0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])
def hp(x, k): return x - lp(x, k)
def noise(d): return rng.standard_normal(int(d * SR))

def kick():
    t = tt(.28); f = 42 + 120 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 8) + .3 * np.sin(2*np.pi*900*t) * np.exp(-t * 200)) * 1.0
def snare():
    t = tt(.22); return (hp(noise(.22), 6) * np.exp(-t * 20) * .55 + np.sin(2*np.pi*185*t) * np.exp(-t * 28) * .5)
def hat(o=False):
    d = .22 if o else .05; t = tt(d); return hp(noise(d), 3) * np.exp(-t * (14 if o else 70)) * .22
def mellow_saw(f, t, n=5):
    return sum(np.sin(2*np.pi*f*k*t) / k for k in range(1, n+1)) * .5
def bass(f, d):
    t = tt(d); e = np.minimum(t / .006, 1) * np.exp(-t * 3.2)
    return (np.sin(2*np.pi*f*t) + .3 * np.sin(2*np.pi*2*f*t) + .12 * np.sign(np.sin(2*np.pi*f*t))) * e * .9
def pad(freqs, d):
    t = tt(d); e = np.minimum(t / .25, 1) * np.minimum((d - t) / .35, 1)
    s = sum(mellow_saw(f * (1 + dt), t, 4) for f in freqs for dt in (-.003, .003))
    return s * e / (len(freqs) * 2) * 1.3
def lead(f0, f1, d, vib=1.0):
    t = tt(d); g = np.clip(t / (d * .35), 0, 1); g = g * g * (3 - 2 * g)
    f = f0 + (f1 - f0) * g; f = f * (1 + .006 * vib * np.sin(2*np.pi*5.5*t) * np.minimum(t / .3, 1))
    ph = 2*np.pi*np.cumsum(f) / SR
    e = np.minimum(t / .03, 1) * np.minimum((d - t) / .12, 1)
    return (np.sin(ph) + .25 * np.sin(2*ph) + .1 * np.sin(3*ph)) * e * .8
def pluck(f, d=.12):
    t = tt(d); return np.sign(np.sin(2*np.pi*f*t)) * np.exp(-t * 30) * .35
def whoosh(d=.7):
    t = tt(d); x = noise(d); y = np.zeros_like(x)
    for k, (a, b) in enumerate([(2, 10)]): pass
    # sweep by blending progressively less-filtered noise
    lo = lp(x, 60); mid = lp(x, 14); hi = lp(x, 3)
    p = t / d; w1 = np.clip(1 - 2 * p, 0, 1); w2 = 1 - np.abs(2 * p - 1); w3 = np.clip(2 * p - 1, 0, 1)
    y = lo * w1 * 3 + mid * w2 * 1.6 + hi * w3 * 1.0
    return y * np.sin(np.pi * p) ** 1.5 * .9
def impact(d=.45, f=70):
    t = tt(d); fr = f * 0.6 + f * 1.4 * np.exp(-t * 14); ph = 2*np.pi*np.cumsum(fr)/SR
    return (np.sin(ph) * np.exp(-t * 9) + lp(noise(d), 8) * np.exp(-t * 25) * .5)
def blip(f, d=.09, sq=True):
    t = tt(d); w = np.sign(np.sin(2*np.pi*f*t)) if sq else np.sin(2*np.pi*f*t)
    return w * np.minimum(t / .003, 1) * np.exp(-t * 22) * .5
def coin():
    a = blip(1976, .07); b = blip(2637, .22); return np.concatenate([a, b])
def tick():
    t = tt(.012); return (np.sin(2*np.pi*1500*t) * .5 + hp(noise(.012), 4) * .4) * np.exp(-t * 400) * .5
def boom(d=.9):
    t = tt(d); return (lp(noise(d), 40) * np.exp(-t * 5) * 1.2 + np.sin(2*np.pi*55*t) * np.exp(-t * 7)) * .8
def crackle_bed(d, density, level):
    x = np.zeros(int(d * SR)); n = int(d * density)
    for i in rng.integers(0, len(x) - 400, n):
        k = rng.integers(20, 200); x[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 4)) * rng.uniform(.2, 1)
    return x * level

# ---------------- music ----------------
BPM = 92; BEAT = 60 / BPM; BAR = 4 * BEAT; E8 = BEAT / 2
Gm = lambda n: 98.0 * 2 ** (n / 12)      # G2 = 98 Hz
nf = lambda semis_from_G2: Gm(semis_from_G2)
chords = [[7+12, 10+12, 14+12, 17+12-12+12], [7+12, 10+12, 14+12, 17+12], [3+12, 7+12, 10+12, 14+12], [2+12, 6+12, 9+12, 12+12]]
chords = [[nf(x) for x in c] for c in chords]
bass_pat = [  # per bar: (eighth index, semitone from G2, len in eighths)
    [(0, 0, 2), (2, 0, 1), (3, 0, 1), (5, 3, 1), (6, 5, 1), (7, 7, 1)],
    [(0, 0, 2), (2, 0, 1), (3, 0, 1), (5, 3, 1), (6, 2, 2)],
    [(0, -4, 2), (2, -4, 1), (3, -4, 1), (5, -1, 1), (6, 0, 1), (7, 3, 1)],
    [(0, -5, 2), (2, -5, 1), (3, -5, 1), (5, -3, 1), (6, -1, 1), (7, 0, 1)],
]
G = lambda s: nf(s + 24)  # lead register (G4 base)
lead_pat = [  # per bar: (beat, dur beats, st0, st1)
    [(0, 1.5, 14, 19), (2, 1, 17, 17), (3, 1, 19, 14)],
    [(0, 2, 22, 19), (2.5, 1.5, 17, 14)],
    [(0, 1.5, 15, 15), (1.5, 2.5, 19, 22)],
    [(0, 1, 18, 21), (1, 3, 21, 14)],
]
stems = {k: (np.zeros(N), np.zeros(N)) for k in ["pad", "bass", "hat", "ks", "lead", "arp", "riser"]}
nb = int(END / BAR) + 1
for b in range(nb):
    t0 = b * BAR; c = b % 4
    add(pad(chords[c], BAR + .2), t0, .5, bus=stems["pad"])
    for (e, s, ln) in bass_pat[c]:
        add(bass(nf(s), ln * E8 * .95), t0 + e * E8, .8, bus=stems["bass"])
    for i in range(16):  # 16th hats w/ swing
        sw = (BEAT / 4) * .12 if i % 2 else 0
        add(hat(i % 8 == 6), t0 + i * BEAT / 4 + sw, (1 if i % 4 == 0 else .55) * (.8 + .2 * (i % 2)), pan=.25, bus=stems["hat"])
    for kb in (0, 2.5, 3.25) if c % 2 == 0 else (0, 1.5, 2.5):
        add(kick(), t0 + kb * BEAT, 1.0, bus=stems["ks"])
    for sb in (1, 3): add(snare(), t0 + sb * BEAT, .9, bus=stems["ks"])
    for (bt, dur, a, bb) in lead_pat[c]:
        add(lead(G(a), G(bb), dur * BEAT), t0 + bt * BEAT, .5, pan=.1, bus=stems["lead"])
    for i in range(16):  # arp
        note = chords[c][i % 4] * 4
        add(pluck(note), t0 + i * BEAT / 4, .5, pan=-.3 if i % 2 else .3, bus=stems["arp"])
# riser in hook
r = lp(noise(T[1]), 5) * np.linspace(0, 1, int(T[1] * SR)) ** 2
add(r * .9, 0, .35, bus=stems["riser"])

def curve(pts):
    ts, gs = zip(*pts); return np.interp(np.arange(N) / SR, ts, gs)
R0 = T[1] + REVEAL
g = {
    "pad":  curve([(0, .55), (R0, .6), (T[5], .7), (T[6], .55), (END-1.5, .5), (END, 0)]),
    "bass": curve([(0, 0), (.5, 0), (.6, .7), (T[6], .7), (END-1.5, .5), (END, 0)]),
    "hat":  curve([(0, 0), (T[1]-.01, 0), (T[1], .5), (T[6], .7), (T[6]+.05, .25), (END-1.5, .2), (END, 0)]),
    "ks":   curve([(0, 0), (R0-.01, 0), (R0, .9), (T[2]-.01, .9), (T[2], 0), (T[3]-.01, 0), (T[3], .85), (T[6], .85), (T[6]+.05, 0), (END, 0)]),
    "lead": curve([(0, 0), (R0-.01, 0), (R0, .8), (T[2]-.01, .8), (T[2], 0), (T[4]-.01, 0), (T[4], .7), (T[6], .75), (T[6]+.3, .5), (END-1.5, .45), (END, 0)]),
    "arp":  curve([(0, 0), (T[5]-.01, 0), (T[5], .45), (T[6], .45), (T[6]+.05, 0), (END, 0)]),
    "riser": curve([(0, 1), (T[1], 1), (T[1] + .01, 0), (END, 0)]),
}
MUS_L = sum(stems[k][0] * g[k] for k in stems); MUS_R = sum(stems[k][1] * g[k] for k in stems)
L += MUS_L * .42; R += MUS_R * .42

sfx = (np.zeros(N), np.zeros(N))
def S(sig, t, gg=1.0, pan=0.0): add(sig, t, gg, pan, bus=sfx)
def cymbal(d=1.6):
    t = tt(d); return hp(noise(d), 2) * np.exp(-t * 2.6) * .5
def cheer(d=2.2):
    t = tt(d); x = lp(noise(d), 9) * (np.minimum(t / .3, 1) * np.exp(-t * 1.1)); return x * 1.6
# hook: opening sting + glitch bursts
S(blip(660, .1), .02, .8); S(blip(880, .1), .12, .8); S(blip(1320, .2), .22, .9)
for tg in (.30, .52, .78): S(hp(noise(.06), 2) * np.exp(-tt(.06) * 30) * .9, tg, .8)
S(impact(.5, 80), T[1] - .02, 1.0)
for i in range(1, 7):
    S(whoosh(.8), T[i] - .4, 1.0, pan=.2 if i % 2 else -.2)
    if i > 1: S(impact(.4, 65), T[i], .7)
# recap: header slam, drumroll, reveal, winners
t1 = T[1]
S(impact(.3, 90), t1 + .1, .8); S(blip(440, .08), t1 + .12, .7)
tr, k = .45, 0
while tr < REVEAL - .12:
    S(snare(), t1 + tr, .35 + .5 * (tr / REVEAL), pan=(-1) ** k * .15); tr += max(.05, .26 - .0000 - .075 * k); k += 1
S(lp(noise(REVEAL - .3), 4) * np.linspace(0, 1, int((REVEAL - .3) * SR)) ** 2 * .6, t1 + .3, .5)
S(impact(.9, 55), t1 + REVEAL, 1.2); S(cymbal(), t1 + REVEAL, .9); S(cheer(), t1 + REVEAL + .1, .8)
for j, f in enumerate((523, 659, 784, 1047)): S(blip(f, .16), t1 + REVEAL + .05 + .09 * j, .8)
S(coin(), t1 + REVEAL + .5, .8)
S(whoosh(.7), t1 + WIN0 - .4, .8); S(blip(988, .08), t1 + WIN0, .7); S(blip(1319, .16), t1 + WIN0 + .07, .7)
for i in range(len(WINNERS)):
    S(blip(700 + 40 * (i % 6), .05, False), t1 + WIN0 + .2 + i * ROW_H / WIN_SPEED, .55)
S(coin(), T[2] - 4.6, .7)
# clues
for ci, c in enumerate(CLUES):
    sidx = ci + 2; t0 = T[sidx]; seg = T[sidx + 1] - t0; n = c["n"]
    S(impact(.3, 90), t0 + .1, .8); S(blip(440, .08), t0 + .12, .7)
    for kk in range(n): S(blip(523 * 2 ** (kk / 4), .07), t0 + .45 + .11 * kk, .6)
    S(coin(), t0 + .9, .9); S(impact(.35, 110), t0 + .9, .6)
    S(blip(784, .06), t0 + 1.1, .7); S(blip(1175, .1), t0 + 1.16, .7)
    for i, ch in enumerate(plain(c["text"])):
        if i % 2 == 0 and ch != " ": S(tick(), t0 + TW0 + i * TWS, .6 + .1 * (i % 3), pan=(i % 5 - 2) * .05)
    if n in BANNERS: S(blip(988, .07), t0 + BANNER_T, .7); S(blip(1480, .14), t0 + BANNER_T + .07, .7)
    for kk in (3, 2, 1): S(tick() * 1.3, t0 + seg - kk, .5)       # countdown ticks
    d = seg + .5
    if n == 1:
        S(lp(noise(d), 120) * .12 + np.sin(2*np.pi*60*tt(d)) * .02, t0, 1.0)
        for tp in (.5, .8, 1.1): S(blip(300 + 200 * tp, .06, False), t0 + tp, .8)
    if n == 2:
        S(crackle_bed(d, 55, .5), t0, 1.0); S(boom(.6) * .5, t0 + .3, .8)
        for kk in range(3): S(coin(), t0 + 3.9 + .12 * kk, .6)
    if n == 3:
        S(lp(noise(d), 30) * .22 + crackle_bed(d, 40, .35), t0, 1.0); S(whoosh(.9), t0 + .2, 1.2)
    if n == 4:
        S(lp(noise(d), 10) * (0.1 + .08 * np.sin(2*np.pi*.4*tt(d))), t0, 1.0)
        for tp in (2.4, 4.4): S(boom(1.0), t0 + tp, .9); S(crackle_bed(1.0, 160, .4), t0 + tp + .1, .7)
# outro
S(whoosh(1.0), T[6] + 2.6, 1.0)
S(blip(784, .08), T[6] + .5, .8); S(blip(1175, .12), T[6] + .58, .8)
S(coin(), T[6] + 3.2, .9); S(impact(.5, 70), T[6] + 3.2, .8)
S(blip(988, .1), T[6] + 5.9, .7); S(blip(1319, .3), T[6] + 6.0, .7)
L += sfx[0] * .75; R += sfx[1] * .75
f = np.minimum(np.arange(N) / (.02 * SR), 1) * np.minimum((N - np.arange(N)) / (.9 * SR), 1)
L *= f; R *= f
pk = max(np.abs(L).max(), np.abs(R).max()); L /= pk; R /= pk
out = (np.stack([L, R], 1) * .89 * 32767).astype(np.int16)
with wave.open("raw_audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("ok", N / SR)

import numpy as np, wave
from tl import *
SR = 44100
N = int(END * SR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, g=1.0, pan=0.0, bus=None):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(0, -i); sig = sig[a:]; i = max(i, 0); sig = sig[:N - i]
    gl = g * (1 - max(pan, 0)); gr = g * (1 + min(pan, 0))
    (bus[0] if bus else L)[i:i + len(sig)] += sig * gl
    (bus[1] if bus else R)[i:i + len(sig)] += sig * gr
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, k):
    k = max(int(k), 1); c = np.cumsum(np.insert(x, 0, 0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0] if len(y) else 0), y])[:len(x)]
def hp(x, k): return x - lp(x, k)
def noise(d): return rng.standard_normal(int(d * SR))

# ---------- drums (dusty boom-bap) ----------
def kick():
    t = tt(.34); f = 48 + 90 * np.exp(-t * 26); ph = 2*np.pi*np.cumsum(f)/SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t * 7.5)) * .95
def snare():
    t = tt(.28); n = lp(noise(.28), 3) * np.exp(-t * 17) * .9
    return n + np.sin(2*np.pi*176*t) * np.exp(-t * 24) * .55 + hp(noise(.28), 6) * np.exp(-t * 40) * .25
def hat(o=False):
    d = .2 if o else .05; t = tt(d); return lp(hp(noise(d), 3), 2) * np.exp(-t * (13 if o else 75)) * .3
# ---------- keys / bass / horn ----------
def ep(f, d, vel=1.0):
    t = tt(d); mod = np.sin(2*np.pi*f*t) * np.exp(-t * 7) * (1.1 * vel)
    car = np.sin(2*np.pi*f*t + mod) * np.exp(-t * 2.4)
    tine = np.sin(2*np.pi*f*4*t) * np.exp(-t * 18) * .12
    return (car + tine) * np.minimum(t / .004, 1) * np.minimum((d - t) / .05, 1) * .5
def bass(f, d):
    t = tt(d); e = np.minimum(t / .01, 1) * np.exp(-t * 2.0) * np.minimum((d - t) / .04, 1)
    return np.tanh(1.3 * (np.sin(2*np.pi*f*t) + .25 * np.sin(2*np.pi*2*f*t))) * e * .9
def horn(f0, f1, d):
    t = tt(d); g = np.clip(t / (d * .3), 0, 1); f = f0 + (f1 - f0) * g * g * (3 - 2 * g)
    f = f * (1 + .005 * np.sin(2*np.pi*5.2*t) * np.minimum(t / .35, 1)); ph = 2*np.pi*np.cumsum(f)/SR
    s = sum(np.sin(k * ph) / k for k in (1, 2, 3, 4)) * .55
    e = np.minimum(t / .06, 1) * np.minimum((d - t) / .15, 1)
    return lp(s, 2) * e * .55
def string_pad(freqs, d):
    t = tt(d); e = np.minimum(t / .5, 1) * np.minimum((d - t) / .6, 1)
    return sum(np.sin(2*np.pi*f*(1 + dt)*t) + .3 * np.sin(4*np.pi*f*(1 + dt)*t) for f in freqs for dt in (-.004, .004)) * e / (len(freqs) * 3)
def vinyl(d, level):
    x = np.zeros(int(d * SR)); n = int(d * 38)
    for i in rng.integers(0, len(x) - 300, n):
        k = int(rng.integers(15, 160)); x[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 4)) * rng.uniform(.15, 1)
    return (x + lp(noise(d), 4) * .08 + hp(noise(d), 40) * .02) * level

# ---------- music ----------
stems = {k: (np.zeros(N), np.zeros(N)) for k in ["keys", "bass", "hat", "kick", "snare", "horn", "strings", "riser"]}
STYLE = EP["music"]
if STYLE == "boombap":                                   # 94 BPM, Am9 | D9 | Gmaj9 | Cmaj7 (original, "World Is Yours" mood)
    BPM = 94; BEAT = 60 / BPM; BAR = 4 * BEAT; SW = BEAT * .09
    A2 = 110.0; nfq = lambda s, base=A2: base * 2 ** (s / 12)
    CH = [[12, 15, 19, 22, 26], [17, 21, 24, 27, 31], [22, 26, 29, 33, 36], [15, 19, 22, 26, 30]]
    ROOT = [0, 5, -2, 3]
    HORN = [(0, 0, 1.5, 7, 12), (0, 2, 1, 10, 7), (1, .5, 2, 9, 12), (1, 3, .9, 10, 12), (2, 0, 2, 14, 10), (2, 2.5, 1.2, 12, 10), (3, 0, 1, 7, 10), (3, 1.5, 2.2, 12, 7)]
    ARP = [0, 1, 2, 3, 2, 1, 4, 3]; KICKS = [[0, 1.75, 2.5], [0, .75, 2.25, 3.5]]
    for b in range(int(END / BAR) + 2):
        t0 = b * BAR; c = b % 4
        for i in range(8):
            ts = t0 + i * BEAT / 2 + (SW if i % 2 else 0); idx = ARP[i] % len(CH[c])
            add(ep(nfq(CH[c][idx]), BEAT * .9, .9 + .2 * (i % 3 == 0)), ts, .55 + .2 * (i % 4 == 0), pan=-.2 + .1 * idx, bus=stems["keys"])
        add(ep(nfq(CH[c][0] - 12), BAR * .8, .6), t0, .5, bus=stems["keys"])
        for bt, sm in ((0, 0), (1.5, 7), (2.5, 0), (3.5, 12)):
            add(bass(nfq(ROOT[c] + sm, 55.0), BEAT * (1.4 if bt in (0,) else .8)), t0 + bt * BEAT + (SW if bt % 1 else 0), .9, bus=stems["bass"])
        for i in range(8): add(hat(i % 8 == 7), t0 + i * BEAT / 2 + (SW if i % 2 else 0), (1 if i % 2 == 0 else .6) * (.85 + .15 * ((i * 7) % 3 == 0)), pan=.2, bus=stems["hat"])
        for kb in KICKS[b % 2]: add(kick(), t0 + kb * BEAT + (SW if kb % 1 else 0), 1.0, bus=stems["kick"])
        for sb in (1, 3): add(snare(), t0 + sb * BEAT, .95, bus=stems["snare"])
        for (bar, bt, dur, s0, s1) in HORN:
            if bar == c: add(horn(nfq(s0, 220.0), nfq(s1, 220.0), dur * BEAT), t0 + bt * BEAT, .5, pan=.15, bus=stems["horn"])
        add(string_pad([nfq(x) for x in CH[c][:4]], BAR + .3), t0, .5, bus=stems["strings"])
    PUMP = None
elif STYLE == "trap":                                  # 140 BPM half-time dark trap, Cm | Ab | Eb | Bb (original): 808s, rolls, bells, eerie lead
    BPM = 140; BEAT = 60 / BPM; BAR = 4 * BEAT
    C3 = 130.81; nfq = lambda s, base=C3: base * 2 ** (s / 12)
    CH = [[0, 3, 7, 12], [-4, 0, 3, 8], [3, 7, 10, 15], [-2, 2, 5, 10]]; ROOT = [0, -4, 3, -2]
    def clap():
        t = tt(.2); return hp(noise(.2), 4) * (np.exp(-t * 26) + .7 * np.exp(-((t - .012) * 85) ** 2)) * .8
    def bass808(f, d):
        t = tt(d); fr = f * (1 + 1.6 * np.exp(-t * 28)); ph = 2*np.pi*np.cumsum(fr) / SR
        return np.tanh(2.2 * np.sin(ph) * np.exp(-t * 1.5)) * np.minimum((d - t) / .05, 1) * .95
    def bell(f, d):
        t = tt(d); return (np.sin(2*np.pi*f*t) + .5 * np.sin(2*np.pi*f*2.76*t) * np.exp(-t * 6) + .25 * np.sin(2*np.pi*f*5.4*t) * np.exp(-t * 12)) * np.exp(-t * 3.4) * .5
    for b in range(int(END / BAR) + 2):
        t0 = b * BAR; c = b % 4
        for bt, ln in ((0, 1.6), (1.75, .5), (2.5, .5), (3.25, .6)): add(bass808(nfq(ROOT[c], 65.41), ln * BEAT), t0 + bt * BEAT, .9, bus=stems["bass"])
        add(kick(), t0, 1.0, bus=stems["kick"]); add(kick(), t0 + 2.5 * BEAT, .8, bus=stems["kick"])
        add(clap(), t0 + 2 * BEAT, .95, bus=stems["snare"])
        for i in range(8): add(hat(False), t0 + i * BEAT / 2, .7 if i % 2 == 0 else .45, pan=.2, bus=stems["hat"])
        if b % 4 == 3:
            for i in range(8): add(hat(False), t0 + 3 * BEAT + i * BEAT / 8, .5 + .05 * i, pan=-.2, bus=stems["hat"])                      # hat roll
        for i in range(8):                                                                                                           # bell arpeggio
            n_ = CH[c][[0, 2, 1, 3, 2, 1, 3, 2][i]] + 24
            if (i + b) % 3 != 2: add(bell(nfq(n_), BEAT * .9), t0 + i * BEAT / 2, .5, pan=-.3 + .1 * (i % 4), bus=stems["keys"])
        add(horn(nfq(CH[c][2] + 12), nfq(CH[c][2] + 10), BAR * .9), t0, .45, pan=.1, bus=stems["horn"])
        add(string_pad([nfq(x - 12) for x in CH[c][:3]], BAR + .3), t0, .55, bus=stems["strings"])
    PUMP = None
elif STYLE == "rock":                                  # 138 BPM stadium rock in E (original): distorted power chords, driving drums, crash accents
    BPM = EP.get("bpm", 138); BEAT = 60 / BPM; BAR = 4 * BEAT
    nfq = lambda s, base=82.41: base * 2 ** (s / 12)
    PROG = EP.get("prog", [0, 0, 5, 7, 0, 0, 5, 3]); MEL = [12, 15, 14, 12, 10, 12, 7, 10]
    def power(root, d):
        t = tt(d); x = sum(sum(np.sin(2*np.pi*f*k*t + .3 * k) / k for k in range(1, 8)) for f in (root, root * 1.4983, root * 2))
        return lp(np.tanh(4.5 * x / 3), 3) * np.minimum(t / .006, 1) * np.exp(-t * 3) * np.minimum((d - t) / .03, 1) * .55
    def crash():
        t = tt(1.4); return hp(noise(1.4), 2) * np.exp(-t * 2.8) * .55
    def tom(f):
        t = tt(.3); return np.sin(2*np.pi*(f + 60 * np.exp(-t * 14)) * t) * np.exp(-t * 10) * .8
    for b in range(int(END / BAR) + 2):
        t0 = b * BAR; r_ = PROG[b % 8]
        for i in range(8):                                                       # palm-muted eighths with accents
            add(power(nfq(r_ + 12), BEAT * (.42 if i % 4 else .9)), t0 + i * BEAT / 2, .8 if i % 4 == 0 else .55, pan=-.35, bus=stems["keys"])
            add(power(nfq(r_ + 12), BEAT * (.42 if i % 4 else .9)), t0 + i * BEAT / 2, .5, pan=.35, bus=stems["strings"])
            add(bass(nfq(r_, 41.2) * 2, BEAT * .45), t0 + i * BEAT / 2, .8, bus=stems["bass"])
        for kb in (0, 1.5, 2, 3.5 if b % 2 else 2.5): add(kick(), t0 + kb * BEAT, 1.0, bus=stems["kick"])
        for sb in (1, 3): add(snare(), t0 + sb * BEAT, 1.0, bus=stems["snare"])
        for i in range(8): add(hat(i % 4 == 3), t0 + i * BEAT / 2, .9 if i % 2 == 0 else .5, pan=.25, bus=stems["hat"])
        if b % 4 == 0: add(crash(), t0, .7, bus=stems["hat"])
        if b % 4 == 3:
            for j, f in enumerate((180, 140, 110, 90)): add(tom(f), t0 + 3 * BEAT + j * BEAT / 4, .8, bus=stems["snare"])
        add(horn(nfq(MEL[b % 8] + 12, 82.41 * 2) / 2, nfq(MEL[(b + 1) % 8] + 12, 82.41 * 2) / 2, BAR * .9), t0, .4, pan=.1, bus=stems["horn"])
    PUMP = None
elif STYLE == "tyler":                                 # 88 BPM neo-soul / synth-funk in the Igor-Flower Boy mood (original): Dbmaj9 | Cm9 | Fm9 | Bbm9
    BPM = 88; BEAT = 60 / BPM; BAR = 4 * BEAT; SW = BEAT * .07
    nfq = lambda s, base=130.81: base * 2 ** (s / 12)
    CH = [[1, 5, 8, 12, 15], [0, 3, 7, 10, 14], [5, 8, 12, 15, 19], [-2, 1, 5, 8, 12]]; ROOT = [1, 0, 5, -2]
    def juno(freqs, d):                                   # warm detuned saw pad with slow attack
        t = tt(d); e_ = np.minimum(t / .35, 1) * np.minimum((d - t) / .4, 1)
        s = sum(sum(np.sin(2*np.pi*f*(1 + dt)*k*t) / k for k in range(1, 7)) for f in freqs for dt in (-.006, 0, .006))
        return lp(s, 7) * e_ / (len(freqs) * 3) * .9
    def fuzzbass(f, d):                                   # fuzzy synth bass
        t = tt(d); x = np.sin(2*np.pi*f*t) + .5 * (2 * ((f * t) % 1) - 1)
        return lp(np.tanh(3.2 * x), 3) * np.minimum(t / .01, 1) * np.exp(-t * 1.6) * np.minimum((d - t) / .04, 1) * .55
    def glide(f0, f1, d):                                 # Juno-style square lead with portamento
        t = tt(d); g_ = np.clip(t / .09, 0, 1); f = f0 + (f1 - f0) * g_; f = f * (1 + .007 * np.sin(2*np.pi*5.5*t) * np.minimum(t / .3, 1))
        ph = 2*np.pi*np.cumsum(f) / SR; s = np.sign(np.sin(ph)) * .5 + np.sin(ph) * .5
        return lp(s, 5) * np.minimum(t / .02, 1) * np.minimum((d - t) / .1, 1) * .5
    def shaker():
        t = tt(.06); return hp(noise(.06), 2) * np.exp(-t * 60) * .18
    def clap2():
        t = tt(.2); return hp(noise(.2), 4) * (np.exp(-t * 24) + .6 * np.exp(-((t - .011) * 90) ** 2)) * .55
    MEL = [(0, 0, 1.5, 15, 13), (0, 2, 1, 12, 12), (0, 3, .9, 10, 8), (1, .5, 2, 7, 10), (1, 3, .8, 12, 15),
           (2, 0, 1, 17, 15), (2, 1.5, 2.2, 12, 12), (3, 0, 1, 13, 12), (3, 1.5, 2.3, 8, 5)]
    for b in range(int(END / BAR) + 2):
        t0 = b * BAR; c = b % 4
        add(juno([nfq(x) for x in CH[c][:4]], BAR + .4), t0, .55, bus=stems["strings"])
        for bt in (0, 1.5, 2.5, 3.5):                     # syncopated Rhodes comps
            for n_ in CH[c][1:]: add(ep(nfq(n_), BEAT * .7, .8), t0 + bt * BEAT + (SW if bt % 1 else 0), .22, pan=(n_ % 5 - 2) * .08, bus=stems["keys"])
        for bt, ln, sm in ((0, 1.2, 0), (1.5, .5, 0), (2, .8, 7), (3, .5, 12), (3.5, .5, 10)):
            add(fuzzbass(nfq(ROOT[c], 65.41) * 2 ** (sm / 12), ln * BEAT), t0 + bt * BEAT + (SW if bt % 1 else 0), .9, bus=stems["bass"])
        for kb in ((0, 2.25, 2.75) if b % 2 == 0 else (0, .75, 2.5)): add(kick(), t0 + kb * BEAT + (SW if kb % 1 else 0), .95, bus=stems["kick"])
        for sb in (1, 3): add(snare(), t0 + sb * BEAT, .6, bus=stems["snare"]); add(clap2(), t0 + sb * BEAT + .004, .7, bus=stems["snare"])
        for i in range(16): add(shaker(), t0 + i * BEAT / 4 + (SW / 2 if i % 2 else 0), .6 + .4 * (i % 4 == 2), pan=.25, bus=stems["hat"])
        add(hat(True), t0 + 3.5 * BEAT, .5, pan=-.2, bus=stems["hat"])
        for (bar, bt, dur, s0, s1) in MEL:
            if bar == c: add(glide(nfq(s0, 261.63), nfq(s1, 261.63), dur * BEAT), t0 + bt * BEAT, .5, pan=.1, bus=stems["horn"])
    PUMP = None
else:                                                    # "house": 122 BPM French-touch, Dm9 | Bbmaj7 | F | C (original), 4-on-the-floor + sidechain pump
    BPM = 122; BEAT = 60 / BPM; BAR = 4 * BEAT
    A2 = 110.0; nfq = lambda s, base=A2: base * 2 ** (s / 12)
    CH = [[17, 20, 24, 27, 31], [13, 17, 20, 24], [20, 24, 27, 32], [15, 19, 22, 27]]
    ROOT = [-7, -11, -4, -9]
    def clap():
        t = tt(.2); return hp(noise(.2), 4) * (np.exp(-t * 28) + .6 * np.exp(-((t - .012) * 90) ** 2)) * .7
    def saw_pluck(f, d, cut=6):
        t = tt(d); s = sum(np.sin(2*np.pi*f*k*t) / k for k in range(1, 9)) * .45
        return lp(s, cut) * np.minimum(t / .004, 1) * np.exp(-t * 7) * .8
    def robot(f, d):                                      # bright square-ish synth line (vocoder-ish flavour, no voice)
        t = tt(d); s = np.sign(np.sin(2*np.pi*f*t)) * .5 + np.sin(2*np.pi*f*2*t) * .3
        return lp(s, 3) * np.minimum(t / .003, 1) * np.exp(-t * 11) * .7
    for b in range(int(END / BAR) + 2):
        t0 = b * BAR; c = b % 4
        for i in range(4):                                # 4-on-the-floor + offbeat open hat + 16th ticks
            add(kick(), t0 + i * BEAT, 1.0, bus=stems["kick"])
            add(hat(True), t0 + i * BEAT + BEAT / 2, .9, pan=.25, bus=stems["hat"])
        for i in range(16): add(hat(False), t0 + i * BEAT / 4, .35 + .25 * (i % 4 == 2), pan=-.2, bus=stems["hat"])
        for sb in (1, 3): add(clap(), t0 + sb * BEAT, .9, bus=stems["snare"])
        for i in range(8):                                # pulsing 8th-note bass
            add(bass(nfq(ROOT[c], 55.0 * 2), BEAT * .45), t0 + i * BEAT / 2, .85, bus=stems["bass"])
        for i in range(8):                                # off-beat chord stabs
            if i % 2 == 1 or i in (0, 6):
                for n_ in CH[c][:4]: add(saw_pluck(nfq(n_), BEAT * .4), t0 + i * BEAT / 2, .22, pan=(n_ % 5 - 2) * .1, bus=stems["keys"])
        for i in range(16):                               # robotic 16th arpeggio
            n_ = CH[c][[0, 2, 1, 3, 2, 4 % len(CH[c]), 1, 3][i % 8] % len(CH[c])] + 12
            if (i + b) % 4 != 3: add(robot(nfq(n_), BEAT / 4 * .9), t0 + i * BEAT / 4, .45, pan=.1 if i % 2 else -.1, bus=stems["horn"])
        add(string_pad([nfq(x) for x in CH[c][:4]], BAR + .3), t0, .5, bus=stems["strings"])
    PUMP = 1 - .78 * np.exp(-((np.arange(N) / SR) % BEAT) / .11)       # sidechain-style pump on keys/bass/strings/arp
    for k in ("keys", "bass", "strings", "horn"):
        stems[k][0][:] *= PUMP; stems[k][1][:] *= PUMP
add(lp(noise(T[1]), 5) * np.linspace(0, 1, int(T[1] * SR)) ** 2 * .9, 0, .35, bus=stems["riser"])

def curve(pts):
    ts, gs = zip(*pts); return np.interp(np.arange(N) / SR, ts, gs)
R0 = T[1] + REVEAL; e = lambda t: t - .01
C = [T[S_C1 + i] for i in range(NCL)] + [T[S_OUT]]       # clue starts + outro start
mid = max(1, NCL // 2)
g = {
 "keys":  curve([(0, 0), (e(T[1]), 0), (T[1], .8), (e(T[S_OUT]), .9), (T[S_OUT], .7), (END - 1.5, .6), (END, 0)]),
 "bass":  curve([(0, 0), (.4, 0), (.5, .75), (END - 1.5, .7), (END, 0)]),
 "hat":   curve([(0, 0), (e(T[1]), 0), (T[1], .55), (e(R0), .55), (R0, .8), (e(C[0]), .8), (C[0], .55), (e(T[S_OUT]), .75), (T[S_OUT], .3), (END - 1.5, .25), (END, 0)]),
 "kick":  curve([(0, 0), (e(R0), 0), (R0, .95), (e(C[0]), .95), (C[0], .6 if STYLE == "boombap" else .0), (e(C[1]), .6 if STYLE == "boombap" else .0), (C[1], .85), (e(T[S_OUT]), .85), (T[S_OUT], 0), (END, 0)]),
 "snare": curve([(0, 0), (e(R0), 0), (R0, .9), (e(C[0]), .9), (C[0], 0), (e(C[1]), 0), (C[1], .85), (e(T[S_OUT]), .85), (T[S_OUT], 0), (END, 0)]),
 "horn":  curve([(0, 0), (e(R0), 0), (R0, .8), (e(C[0]), .55), (C[0], 0), (e(C[mid]), 0), (C[mid], .75), (T[S_OUT] + .3, .75), (END - 1.5, .5), (END, 0)]),
 "strings": curve([(0, 0), (e(C[NCL - 1]), 0), (C[NCL - 1], .6), (e(T[S_OUT]), .6), (T[S_OUT], .3), (END - 1.5, .3), (END, 0)]),
 "riser": curve([(0, 1), (e(T[1]), 1), (T[1], 0), (END, 0)]),
}
if STYLE == "house":                                     # clue 1 stays eerie: only pad/bass/ticks, kick returns at clue 2
    g["kick"] = curve([(0, 0), (e(R0), 0), (R0, .95), (e(C[0]), .95), (C[0], 0), (e(C[1]), 0), (C[1], .9), (e(T[S_OUT]), .9), (T[S_OUT], 0), (END, 0)])
ML = sum(stems[k][0] * g[k] for k in stems); MR = sum(stems[k][1] * g[k] for k in stems)
if STYLE == "boombap": ML = lp(ML, 2) * .5 + ML * .5; MR = lp(MR, 2) * .5 + MR * .5
vb = vinyl(END, .06 if STYLE == "boombap" else .015) * curve([(0, 0), (.2, 1), (END - 1, 1), (END, 0)])
L += ML * .42 + vb; R += MR * .42 + vb * .9

# ---------- SFX ----------
sfx = (np.zeros(N), np.zeros(N))
def S(sig, t, gg=1.0, pan=0.0): add(sig, t, gg, pan, bus=sfx)
def whoosh(d=.7):
    t = tt(d); x = noise(d); p = t / d
    y = lp(x, 60) * np.clip(1 - 2*p, 0, 1) * 3 + lp(x, 14) * (1 - np.abs(2*p - 1)) * 1.6 + lp(x, 3) * np.clip(2*p - 1, 0, 1)
    return y * np.sin(np.pi * p) ** 1.5 * .9
def impact(d=.45, f=70):
    t = tt(d); fr = f * .6 + f * 1.4 * np.exp(-t * 14); ph = 2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph) * np.exp(-t * 9) + lp(noise(d), 8) * np.exp(-t * 25) * .5
def blip(f, d=.09, sq=True):
    t = tt(d); w = np.sign(np.sin(2*np.pi*f*t)) if sq else np.sin(2*np.pi*f*t)
    return w * np.minimum(t / .003, 1) * np.exp(-t * 22) * .5
def coin(): return np.concatenate([blip(1976, .07), blip(2637, .22)])
def tick():
    t = tt(.012); return (np.sin(2*np.pi*1500*t) * .5 + hp(noise(.012), 4) * .4) * np.exp(-t * 400) * .5
def boom(d=.9):
    t = tt(d); return (lp(noise(d), 40) * np.exp(-t * 5) * 1.2 + np.sin(2*np.pi*55*t) * np.exp(-t * 7)) * .8
def cymbal(d=1.6): t = tt(d); return hp(noise(d), 2) * np.exp(-t * 2.6) * .5
def cheer(d=2.2): t = tt(d); return lp(noise(d), 9) * (np.minimum(t / .3, 1) * np.exp(-t * 1.1)) * 1.6
def scratch(d=.28):
    t = tt(d); f = 300 + 900 * np.sin(2*np.pi*3.2*t) ; ph = 2*np.pi*np.cumsum(f)/SR
    return (np.sign(np.sin(ph)) * .4 + hp(noise(d), 3) * .5) * np.sin(np.pi * t / d)
def crackle_bed(d, density, level):
    x = np.zeros(int(d * SR))
    for i in rng.integers(0, len(x) - 400, int(d * density)):
        k = int(rng.integers(20, 200)); x[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 4)) * rng.uniform(.2, 1)
    return x * level
# hook: needle drop + scratches + glitch
S(boom(.5) * .6, .02, .8); S(scratch(), .05, .8); S(scratch(.2), .3, .7, pan=.3); S(scratch(.16), .55, .7, pan=-.3)
for tg in (.30, .52, .78): S(hp(noise(.06), 2) * np.exp(-tt(.06) * 30) * .9, tg, .7)
S(impact(.5, 80), T[1] - .02, 1.0)
for i in range(1, S_OUT + 1):
    if i > 1 and T[i] == T[i - 1]: continue
    S(whoosh(.8), T[i] - .4, 1.0, pan=.2 if i % 2 else -.2)
    if i > 1: S(impact(.4, 65), T[i], .7)
# recap: slam, drumroll, reveal ("la respuesta de ayer")
t1 = T[1]
S(impact(.3, 90), t1 + .1, .8); S(blip(440, .08), t1 + .12, .7)
tr, k = .45, 0
while tr < REVEAL - .12:
    S(snare(), t1 + tr, .35 + .5 * (tr / REVEAL), pan=(-1) ** k * .15); tr += max(.05, .26 - .075 * k * (3.4 / REVEAL)); k += 1
S(lp(noise(max(REVEAL - .3, .5)), 4) * np.linspace(0, 1, int(max(REVEAL - .3, .5) * SR)) ** 2 * .6, t1 + .3, .5)
S(impact(.9, 55), t1 + REVEAL, 1.2); S(cymbal(), t1 + REVEAL, .9); S(cheer(), t1 + REVEAL + .1, .8)
for j, f in enumerate((523, 659, 784, 1047)): S(blip(f, .16), t1 + REVEAL + .05 + .09 * j, .8)
S(coin(), t1 + REVEAL + .5, .8)
S(blip(988, .08), T[2] - 3.2, .7); S(blip(1319, .16), T[2] - 3.13, .7)
# winners (only when the previous episode has a list)
t2 = T[2]
if WINNERS:
    S(whoosh(.7), t2 + .0, .8); S(blip(988, .08), t2 + .3, .7); S(blip(1319, .16), t2 + .37, .7)
    for i, r in enumerate(ROWS):
        if r["kind"] == "hdr": S(coin(), t2 + WIN_START + max(0, i * ROW_H - WIN_WH * .85) / WIN_SPEED, .6)
        elif i * ROW_H > WIN_WH: S(blip(700 + 35 * (i % 7), .05, False), t2 + WIN_START + (i * ROW_H - WIN_WH) / WIN_SPEED, .45)
    S(coin(), T[3] - 1.6, .7)
# clues
for ci, c in enumerate(CLUES):
    sidx = S_C1 + ci; t0 = T[sidx]; seg = T[sidx + 1] - t0; n = c["n"]
    S(impact(.3, 90), t0 + .1, .8); S(blip(440, .08), t0 + .12, .7)
    for kk in range(n): S(blip(523 * 2 ** (kk / 4), .07), t0 + .45 + .11 * kk, .6)
    S(coin(), t0 + .9, .9); S(impact(.35, 110), t0 + .9, .6)
    S(blip(784, .06), t0 + 1.1, .7); S(blip(1175, .1), t0 + 1.16, .7)
    for i, ch in enumerate(plain(c["text"])):
        if i % 2 == 0 and ch != " ": S(tick(), t0 + TW0 + i * TWS, .6 + .1 * (i % 3), pan=(i % 5 - 2) * .05)
    if sidx in BANNERS: S(blip(988, .07), t0 + BANNER_T, .7); S(blip(1480, .14), t0 + BANNER_T + .07, .7)
    if ci == NCL - 1:                                     # 3-2-1 countdown on the easiest clue
        for kk in (3, 2, 1): S(impact(.3, 60 + 15 * (3 - kk)), t0 + seg - kk, .9); S(blip(660 + 110 * (3 - kk), .12), t0 + seg - kk, .8)
        S(whoosh(.6), t0 + seg - .45, .9)
    else:
        for kk in (3, 2, 1): S(tick() * 1.3, t0 + seg - kk, .5)
    d = seg + .5
    sc = c.get("scene")
    if sc == "block": S(lp(noise(d), 40) * .12 + crackle_bed(d, 12, .3), t0, 1.0)
    elif sc == "jazz": S(lp(noise(d), 90) * .08, t0, 1.0); S(boom(.6) * .4, t0 + .3, .8)
    elif sc in ("set", "tv", "store", "bedroom", "cafe", "school", "airport"): S(lp(noise(d), 30) * .09, t0, 1.0); S(whoosh(.8), t0 + .2, .8)
    elif sc in ("workshop", "wembley"): S(lp(noise(d), 25) * .1, t0, 1.0); S(whoosh(.8), t0 + .2, .8)
    elif sc in ("g_garage", "g_studio"): S(lp(noise(d), 30) * .09, t0, 1.0); S(whoosh(.8), t0 + .2, .8)
    elif sc == "g_aberdeen": S(hp(noise(d), 2) * .05, t0, 1.0)
    elif sc == "g_pool":
        S(lp(noise(d), 60) * .12, t0, 1.0)
        for i in range(6): S(blip(500 + 80 * i, .05, False), t0 + .8 + i * .7, .4)
    elif sc == "awards":
        S(lp(noise(d), 10) * (.08 + .05 * np.sin(2*np.pi*.4*tt(d))), t0, 1.0)
        for tp in (1.0, 3.5): S(cymbal(.9), t0 + tp, .5)
    elif sc in ("qb", "paris", "press"): S(lp(noise(d), 25) * .1, t0, 1.0); S(whoosh(.9), t0 + .2, 1.0)
    elif sc == "pyramid":
        S(lp(noise(d), 12) * (.1 + .06 * np.sin(2*np.pi*.5*tt(d))), t0, 1.0)             # festival crowd
        for tp in (1.4, 3.6): S(whoosh(1.0), t0 + tp, .7)                                  # laser sweeps
    elif sc == "grammy":
        S(lp(noise(d), 10) * (.08 + .05 * np.sin(2*np.pi*.4*tt(d))), t0, 1.0)             # applause bed
        for tp in (1.0, 3.5): S(cymbal(.9), t0 + tp, .5)
    elif sc in ("battle", "robots", "rave", "disco"):
        for tp in (1.1, 3.3, 5.0): S(boom(.8), t0 + tp, .8); S(hp(noise(.12), 2) * np.exp(-tt(.12) * 20), t0 + tp, .7)
# outro
S(whoosh(1.0), T[S_OUT] + 2.6, 1.0)
S(blip(784, .08), T[S_OUT] + .5, .8); S(blip(1175, .12), T[S_OUT] + .58, .8)
S(coin(), T[S_OUT] + 3.2, .9); S(impact(.5, 70), T[S_OUT] + 3.2, .8)
S(blip(988, .1), T[S_OUT] + 5.9, .7); S(blip(1319, .3), T[S_OUT] + 6.0, .7)
L += sfx[0] * .75; R += sfx[1] * .75
f = np.minimum(np.arange(N) / (.02 * SR), 1) * np.minimum((N - np.arange(N)) / (.9 * SR), 1)
L *= f; R *= f
pk = max(np.abs(L).max(), np.abs(R).max()); L /= pk; R /= pk
out = (np.stack([L, R], 1) * .89 * 32767).astype(np.int16)
with wave.open("raw_audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("ok", N / SR, STYLE)

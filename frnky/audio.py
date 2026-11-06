"""Música y efectos chiptune sintetizados (audio propio, sin licencias externas)."""
import wave
import numpy as np

SR = 44100
rng = np.random.default_rng(66)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def square(f, dur, duty=0.5):
    return np.where((_t(dur) * f) % 1 < duty, 1.0, -1.0)


def tri(f, dur):
    return 2 * np.abs(2 * ((_t(dur) * f) % 1) - 1) - 1


def env(n, a=0.005, rel=0.6):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.linspace(0, 1, n) * (1 / max(rel, 0.01)) * 3)
    return e


def put(track, t0, sig, vol=1.0):
    i = int(t0 * SR)
    if i >= len(track):
        return
    sig = sig[: len(track) - i]
    track[i:i + len(sig)] += sig * vol


def note(f, dur, vol=0.3, kind="sq", duty=0.5, rel=0.5):
    s = square(f, dur, duty) if kind == "sq" else tri(f, dur)
    return s * env(len(s), rel=rel) * vol


def kick(vol=0.5):
    t = _t(0.16)
    f = 130 * np.exp(-t * 22) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * vol


def noise(dur, vol, rel=0.05):
    n = int(dur * SR)
    return rng.uniform(-1, 1, n) * env(n, a=0.001, rel=rel) * vol


def blip(f, vol=0.22):
    d = 0.055
    s = square(f * rng.uniform(0.92, 1.12), d, 0.35)
    return s * np.linspace(1, 0, len(s)) * vol


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


PROG_MIN = [(45, "m"), (41, "M"), (48, "M"), (43, "M")]   # Am F C G
PROG_MAJ = [(48, "M"), (43, "M"), (45, "m"), (41, "M")]   # C G Am F
MEL_MIN = [(0, 76, 1), (1, 76, 1), (2, 79, 2), (4, 81, 2), (6, 79, 1), (7, 76, 1),
           (8, 77, 2), (10, 76, 1), (11, 72, 1), (12, 74, 3), (15, 72, 1),
           (16, 72, 1), (17, 76, 1), (18, 79, 2), (20, 84, 2), (22, 79, 1), (23, 76, 1),
           (24, 74, 2), (26, 76, 1), (27, 74, 1), (28, 71, 3), (31, 74, 1)]
MEL_MAJ = [(0, 79, 1), (1, 79, 1), (2, 84, 2), (4, 86, 2), (6, 84, 1), (7, 79, 1),
           (8, 83, 2), (10, 81, 1), (11, 79, 1), (12, 81, 3), (15, 79, 1),
           (16, 84, 1), (17, 88, 1), (18, 86, 2), (20, 84, 2), (22, 81, 1), (23, 79, 1),
           (24, 77, 2), (26, 79, 1), (27, 81, 1), (28, 84, 3), (31, 79, 1)]


def groove(track, t0, t1, bpm, mode="min", layers=("bass", "pad", "arp", "lead", "drums"), vol=1.0):
    """Loop de 4 compases (Am-F-C-G o C-G-Am-F) con bajo sincopado, pad, arpegio, melodía con eco y batería."""
    step = 60 / bpm / 2
    prog = PROG_MIN if mode == "min" else PROG_MAJ
    mel = MEL_MIN if mode == "min" else MEL_MAJ
    lead = np.zeros(len(track))
    n = int((t1 - t0) / step)
    for i in range(n):
        t = t0 + i * step
        bar, st = (i // 8) % 4, i % 8
        root, q = prog[bar]
        third = 3 if q == "m" else 4
        if "bass" in layers and st in (0, 3, 6):
            put(track, t, note(midi(root - 12 + (12 if st == 6 else 0)), step * 2.2, 0.17, "tri", rel=0.35), vol)
        if "pad" in layers and st == 0:
            for off in (0, third, 7):
                put(track, t, note(midi(root + 12 + off), step * 7.5, 0.035, "tri", rel=1.6), vol)
        if "arp" in layers:
            for sub in (0, 1):
                k = (i * 2 + sub) % 4
                f = midi(root + 24 + (0, third, 7, 12)[k])
                put(track, t + sub * step / 2, note(f, step * 0.45, 0.028, "sq", 0.125, 0.25), vol)
        if "drums" in layers:
            if st in (0, 4) or (st == 7 and bar % 2):
                put(track, t, kick(0.42), vol)
            if st in (2, 6):
                put(track, t, noise(0.1, 0.15, 0.07), vol)
            put(track, t, noise(0.018, 0.04 if st % 2 else 0.06, 0.02), vol)
    if "lead" in layers:
        for k in range(int((t1 - t0) / (step * 32)) + 1):
            for s0, m, ln in mel:
                tt = t0 + (k * 32 + s0) * step
                if tt < t1 - 0.05:
                    f = midi(m)
                    dur = ln * step * 0.95
                    sig = square(f * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * _t(dur))), dur, 0.25)
                    put(lead, tt, sig * env(len(sig), rel=0.5) * 0.085)
        d = int(0.19 * SR)
        lead[d:] += 0.35 * lead[:-d]
        track += lead * vol


def riser(track, t0, t1, root=57, vol=1.0):
    n = 8
    for k in range(n):
        put(track, t0 + (t1 - t0) * k / n, note(midi(root + 4 * k % 12 + 12 * (k // 3)), (t1 - t0) / n * 0.9, 0.12, "sq", 0.25), vol)


def powerup(track, t0, vol=1.0):
    for k, n in enumerate([60, 64, 67, 72, 76, 79, 84]):
        put(track, t0 + k * 0.05, note(midi(n), 0.08, 0.14, "sq", 0.25, 0.3), vol)


def hit(track, t0):
    put(track, t0, kick(0.8))
    put(track, t0, noise(0.12, 0.25, 0.08))


def ding(track, t0):
    for f, v in ((1318, 0.22), (1760, 0.16)):
        put(track, t0, note(f, 0.5, v, "tri", rel=0.6))


def scratch(track, t0):
    n = int(0.28 * SR)
    f = np.linspace(900, 120, n)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.2 * np.linspace(1, 0.2, n)
    put(track, t0, s + noise(0.28, 0.08, 0.3))


def trombone(track, t0):
    for k, (n, d) in enumerate([(58, .28), (57, .28), (56, .28), (53, .7)]):
        sig = square(midi(n) * (1 + 0.008 * np.sin(_t(d) * 40)[0]), d, 0.4) * env(int(d * SR), rel=0.8) * 0.2
        put(track, t0 + sum(x[1] for x in [(58, .28), (57, .28), (56, .28)][:k]), sig)


def jingle(track, t0):
    for k, n in enumerate([67, 72, 76, 79, 84]):
        put(track, t0 + k * 0.07, note(midi(n), 0.2, 0.15, "sq", 0.25, 0.4))


def voice(track, line, pitch):
    t0, t1, text = line
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return
    dt = (t1 - t0 - 0.1) / len(chars)
    for k, c in enumerate(chars):
        put(track, t0 + k * dt, blip(pitch * (1 + (ord(c.lower()) % 5) * 0.06)))


def save(track, path):
    peak = max(1e-6, np.abs(track).max())
    pcm = (track / peak * 0.9 * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def whoosh(track, t0, dur=0.28, vol=0.18):
    n = int(dur * SR)
    x = rng.uniform(-1, 1, n)
    k = np.linspace(0.02, 0.35, n)
    y = np.zeros(n); a = 0.0
    for i in range(n):          # filtro pasabajas que se abre: "fiuuu"
        a += k[i] * (x[i] - a); y[i] = a
    put(track, t0, y * np.sin(np.linspace(0, np.pi, n)) * vol * 4)


def airhorn(track, t0, vol=0.22):
    for f in (392, 494, 587):
        s = (square(f, 0.55, 0.5) + 0.5 * square(f * 1.006, 0.55, 0.3)) * env(int(0.55 * SR), a=0.01, rel=0.9) * vol * 0.5
        put(track, t0, s)


def step(track, t0, vol=0.16):
    put(track, t0, noise(0.05, vol, 0.03)); put(track, t0, kick(0.12))


def click(track, t0, vol=0.12):
    put(track, t0, noise(0.012, vol, 0.01))


def coin(track, t0, vol=0.16):
    put(track, t0, note(midi(83), 0.07, vol, "sq", 0.25, 0.3)); put(track, t0 + 0.07, note(midi(88), 0.35, vol, "sq", 0.25, 0.6))


def levelup(track, t0, vol=0.14):
    for k, n in enumerate([72, 76, 79, 84, 88]):
        put(track, t0 + k * 0.06, note(midi(n), 0.14, vol, "sq", 0.25, 0.35))


def crowd(track, t0, dur=0.9, vol=0.1):
    n = int(dur * SR)
    y = rng.uniform(-1, 1, n)
    k = 0.08
    z = np.zeros(n); a = 0.0
    for i in range(n):
        a += k * (y[i] - a); z[i] = a
    put(track, t0, z * np.sin(np.linspace(0, np.pi, n)) * vol * 6)


def roll(track, t0, t1, vol=0.16):
    n = 12
    for k in range(n):
        u = k / n
        put(track, t0 + (t1 - t0) * (u ** 0.8), noise(0.07, vol * (0.4 + u), 0.05))
    put(track, t1 - 0.01, kick(0.6))


def rimshot(track, t0):
    put(track, t0, noise(0.08, 0.2, 0.05)); put(track, t0 + 0.12, noise(0.08, 0.2, 0.05))
    put(track, t0 + 0.3, noise(0.5, 0.12, 0.5)); put(track, t0 + 0.3, kick(0.5))

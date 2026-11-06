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


def groove(track, t0, t1, bpm, root, minor=True, drums=True, lead=True, vol=1.0):
    step = 60 / bpm / 2
    scale = [0, 3, 7, 10, 12, 15] if minor else [0, 4, 7, 9, 12, 16]
    prog = [0, 0, -4 if minor else 5, -2 if minor else 7]
    i, t = 0, t0
    while t < t1 - 0.05:
        bar = (i // 8) % 4
        r = root + prog[bar]
        if i % 2 == 0:
            put(track, t, note(midi(r - 12), step * 1.8, 0.16, "tri", rel=0.4), vol)
        if lead and i % 2 == 1 or lead and i % 4 == 0:
            n = r + scale[(i * 3) % len(scale)]
            put(track, t, note(midi(n), step * 0.9, 0.07, "sq", 0.25, 0.25), vol)
        if drums:
            if i % 4 == 0:
                put(track, t, kick(0.45), vol)
            if i % 4 == 2:
                put(track, t, noise(0.09, 0.16, 0.06), vol)
            put(track, t, noise(0.02, 0.05, 0.02), vol)
        i += 1
        t += step


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

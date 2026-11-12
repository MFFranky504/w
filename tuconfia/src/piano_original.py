"""Pieza de piano ORIGINAL (sin copyright) para el inicio del documental de Del Toro: nocturna, en La menor, arpegios lentos.
Síntesis aditiva con decaimiento, un poco de desafinación y reverberación. Uso: python3 piano_original.py [segundos]"""
import sys, os, wave
import numpy as np
SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 92.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(1964)
f = lambda midi: 440.0 * 2 ** ((midi - 69) / 12)


def note(midi, dur, vel=.5):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f(midi); y = np.zeros(n, np.float32)
    for k, a in ((1, 1.0), (2, .3), (3, .1), (4, .035), (5, .012)):          # armónicos agudos suaves: menos metálico
        det = 1 + rng.normal(0, .0007)
        y += a * np.sin(2 * np.pi * fr * k * det * t) * np.exp(-t * (1.1 + .9 * k) * (fr / 440) ** .35)
    att = np.minimum(1, t / .012)                                    # ataque un poco más blando
    return (y * att * vel).astype(np.float32)


out = np.zeros((int((DUR + 4) * SR), 2), np.float32)
def put(sig, t0, pan=0.0):
    i = int(t0 * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n, 0] += sig[:n] * (1 - max(0, pan)); out[i:i + n, 1] += sig[:n] * (1 + min(0, pan))


BEAT = 60 / 66                                                    # 66 bpm, compás de 4
PROG = [(57, [0, 3, 7]), (53, [0, 4, 7]), (48, [0, 4, 7]), (52, [0, 3, 7]),        # Am  F  C  Em
        (57, [0, 3, 7]), (50, [0, 3, 7]), (52, [0, 4, 7, 10]), (57, [0, 3, 7])]   # Am  Dm E7  Am
MEL = [[76, None, 74, 72], [72, None, None, 69], [67, None, 69, 72], [71, None, None, None],
       [76, None, 77, 76], [74, None, 72, 69], [71, None, 68, None], [69, None, None, None]]
t, bar = 0.0, 0
while t < DUR:
    root, iv = PROG[bar % 8]
    put(note(root - 12, BEAT * 4.5, .32), t)                            # bajo
    arp = [root + i for i in iv] + [root + 12]
    for k in range(8):                                                  # arpegio en corcheas
        put(note(arp[(k if k < 4 else 7 - k) % len(arp)], BEAT * 1.6, .16 + .03 * (k == 0)), t + k * BEAT / 2, -.25)
    if bar >= 4:                                                        # la melodía entra en la segunda vuelta
        for k, m in enumerate(MEL[bar % 8]):
            if m: put(note(m, BEAT * 2.2, .26), t + k * BEAT, .25)
    t += BEAT * 4; bar += 1
ir_n = int(2.4 * SR); ir = (rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 2.6)).astype(np.float32) * .012
for ch in (0, 1):                                                       # reverberación por convolución (FFT)
    L = len(out) + ir_n; F = np.fft.rfft(out[:, ch], L) * np.fft.rfft(ir, L); out[:, ch] = out[:, ch] * .8 + np.fft.irfft(F, L)[:len(out)].astype(np.float32)
out = out[:int(DUR * SR)]
fade = np.minimum(1, np.minimum(np.arange(len(out)) / SR / 1.5, (len(out) / SR - np.arange(len(out)) / SR) / 3.0))[:, None]
out *= fade; out /= np.abs(out).max() + 1e-9; out *= .8
with wave.open(f'{ROOT}/audio/piano_original.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print('ok', round(len(out) / SR, 1), 's')

"""Narración más viva a partir de las líneas de voz ya generadas (sin gastar créditos): ritmo y tono según la emoción de cada frase,
más ecualización de presencia y compresión suave. Uso: python3 src/narr_viva.py <guion_final.json> <nombre>"""
import json, sys, os, subprocess, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
src, name = sys.argv[1], sys.argv[2]
L = json.load(open(src))
# emoción -> (tempo, tono en semitonos)
EMO = {'excited': (1.09, .9), 'tense': (.98, -.5), 'sad': (.91, -.9), 'warm': (1.0, .1), 'mysterious': (.94, -.4), 'hopeful': (1.04, .5), 'funny': (1.07, .7)}
PAUSE = {'tense': .2, 'sad': .45, 'mysterious': .42, 'warm': .26, 'hopeful': .28, 'excited': .16, 'funny': .2}
FX = "highpass=f=70,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=7500:t=q:w=1:g=1.2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3"


def line(i, emo, ex):
    t, st = EMO.get(emo, (1.0, 0))
    t *= 1.04 * (1.02 if ex else 1.0)
    f = f"rubberband=tempo={t}:pitch={2 ** (st / 12):.4f}:formant=preserved,{FX}"
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{ROOT}/audio/lineas_{name}/l{i:03d}.mp3', '-af', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    env = np.abs(x) > .012
    a = max(0, int(np.argmax(env)) - int(.03 * SR)); b = min(len(x), len(x) - int(np.argmax(env[::-1])) + int(.06 * SR))
    return x[a:b]


out, t, tim = [np.zeros(int(.15 * SR), np.float32)], .15, []
for i, l in enumerate(L):
    if i and l['cap'] != L[i - 1]['cap']:
        g = 2.3; out.append(np.zeros(int(g * SR), np.float32)); t += g
    x = line(i, l['emo'], '*' in l['t'])
    tim.append(dict(i=i, start=round(t, 3), end=round(t + len(x) / SR, 3))); out.append(x); t += len(x) / SR
    p = PAUSE.get(l['emo'], .25) + (.25 if l['t'].rstrip('*').endswith(('...', '…')) else 0)
    out.append(np.zeros(int(p * SR), np.float32)); t += p
y = np.concatenate(out); y = y / (np.abs(y).max() + 1e-9) * .89
with wave.open(f'{ROOT}/audio/narracion_{name}_largo.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
json.dump(tim, open(f'{ROOT}/audio/tiempos_{name}_largo.json', 'w'))
print('duración', round(len(y) / SR, 1), 's')

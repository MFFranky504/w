"""Une las líneas de voz en una narración con pausas de montaje y guarda los tiempos exactos de cada línea.
Uso: python3 src/narr_largo.py <guion_final.json> <nombre>"""
import json, sys, os, subprocess
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
src, name = sys.argv[1], sys.argv[2]
L = json.load(open(src))
PAUSE = {'Un segundo. Dos. *Tres*.': .9, 'Pero él hizo algo *raro*.': .7, 'Él *no*.': .6, 'Piénsalo...': .7, 'Y esta vez... no repite el *éxito*.': .6}


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    env = np.abs(x) > .012
    a = max(0, int(np.argmax(env)) - int(.03 * SR)); b = min(len(x), len(x) - int(np.argmax(env[::-1])) + int(.06 * SR))
    return x[a:b]


out, t, tim = [], 0.15, []
out.append(np.zeros(int(t * SR), np.float32))
for i, l in enumerate(L):
    if i and l['cap'] != L[i - 1]['cap']:
        g = 2.3; out.append(np.zeros(int(g * SR), np.float32)); t += g        # hueco para la tarjeta de capítulo
    x = load(f'{ROOT}/audio/lineas_{name}/l{i:03d}.mp3')
    tim.append(dict(i=i, start=round(t, 3), end=round(t + len(x) / SR, 3)))
    out.append(x); t += len(x) / SR
    p = PAUSE.get(l['t'], .3 if l['t'].rstrip('*').endswith(('...', '…')) else .22)
    out.append(np.zeros(int(p * SR), np.float32)); t += p
y = np.concatenate(out); y = y / (np.abs(y).max() + 1e-9) * .89
import wave
with wave.open(f'{ROOT}/audio/narracion_{name}_largo.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
json.dump(tim, open(f'{ROOT}/audio/tiempos_{name}_largo.json', 'w'))
print('duración', round(len(y) / SR, 1), 's')

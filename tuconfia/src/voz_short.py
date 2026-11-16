"""Voz gratis para un Short: Pollinations es-MX-Grant por línea + ritmo/tono según emoción; escribe narracion_<n>_short.mp3
y alineacion_<n>_short.json (palabras repartidas por longitud dentro de cada línea). Uso: python3 -I src/voz_short.py <nombre>"""
import json, sys, os, subprocess, time, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
name = sys.argv[1]
S = json.load(open(f'{ROOT}/script_{name}_short.json'))['lines']
emo = lambda l: l['gen'].split(']')[0].lstrip('[')
EMO = {'excited': (1.09, .9), 'bold': (1.02, -.2), 'sad': (.91, -.9), 'warmly': (1.0, .1), 'hopeful': (1.04, .5), 'softly': (.94, -.4)}
PAUSE = {'sad': .45, 'softly': .42, 'warmly': .26, 'hopeful': .28, 'excited': .16, 'bold': .2}
FX = "highpass=f=70,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=7500:t=q:w=1:g=1.2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3"
d = f'{ROOT}/audio/lineas_{name}'; os.makedirs(d, exist_ok=True)
for i, l in enumerate(S):
    f = f'{d}/l{i:03d}.mp3'
    if os.path.exists(f) and os.path.getsize(f) > 2000: continue
    body = json.dumps({'model': 'microsoft/mai-voice-2.1', 'input': l['tts'], 'voice': 'es-MX-Grant', 'response_format': 'mp3'})
    for k in range(4):
        r = subprocess.run(['curl', '-s', '-m', '120', '-w', '%{http_code}', '-o', f, 'https://gen.pollinations.ai/v1/audio/speech', '-H', 'Authorization: Bearer proxy-injected',
                            '-H', 'Content-Type: application/json', '-d', body], capture_output=True, text=True)
        if r.stdout.strip() == '200' and os.path.getsize(f) > 2000: break
        if r.stdout.strip() == '402': sys.exit('402: sin saldo gratis hoy en Pollinations')
        time.sleep(5 + 5 * k)
out, t, words = [np.zeros(int(.15 * SR), np.float32)], .15, []
for i, l in enumerate(S):
    tm, st = EMO.get(emo(l), (1.0, 0)); tm *= 1.04 * (1.02 if '*' in l['t'] else 1)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{d}/l{i:03d}.mp3', '-af', f"rubberband=tempo={tm}:pitch={2 ** (st / 12):.4f}:formant=preserved,{FX}", '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); e = np.abs(x) > .012
    x = x[max(0, int(np.argmax(e)) - int(.03 * SR)): len(x) - int(np.argmax(e[::-1])) + int(.06 * SR)]
    ws = l['tts'].split(); L = sum(len(w) + 1 for w in ws); dur = len(x) / SR; c = t
    for w in ws:
        dw = dur * (len(w) + 1) / L; words.append(dict(text=w, start=round(c, 3), end=round(c + dw, 3))); c += dw
    out.append(x); t += dur; p = PAUSE.get(emo(l), .25); out.append(np.zeros(int(p * SR), np.float32)); t += p
y = np.concatenate(out); y = y / (np.abs(y).max() + 1e-9) * .89
wav = f'{ROOT}/audio/narr_{name}_tmp.wav'
with wave.open(wav, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-b:a', '192k', f'{ROOT}/audio/narracion_{name}_short.mp3'], check=True); os.remove(wav)
json.dump(dict(characters=[], words=words, loss=0), open(f'{ROOT}/audio/alineacion_{name}_short.json', 'w'))
print('OK', round(len(y) / SR, 1), 's')

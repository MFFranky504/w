"""Voz del video largo: una petición TTS por línea (Pollinations, Microsoft es-MX-Grant) para tener los tiempos exactos de cada frase.
Uso: python3 src/voz_largo.py <guion_final.json> <nombre>"""
import json, re, sys, os, subprocess, time
from num2words import num2words
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = {'Mike Todd': 'Maik Tod', 'Steve Jobs': 'Stiv Yobs', 'Jobs': 'Yobs', 'Pixar': 'Píksar', 'NeXT': 'Néxt', 'Apple': 'Ápel', 'Lucasfilm': 'Lúcasfilm', 'Universal': 'Iunivérsal', 'Sylvester Stallone': 'Silvéster Stalón', 'Stallone': 'Stalón', 'Rocky': 'Róki', 'Butkus': 'Bútkus', 'Rowling': 'Róuling', 'J. K.': 'Yéi Kéi', 'Bloomsbury': 'Blúmsberi', 'Jim Carrey': 'Yim Kári', 'Carrey': 'Kári', 'Mulholland Drive': 'Malholand Draiv', 'Los Ángeles': 'Los Ánjeles', 'Walt Disney': 'Uólt Dísni', 'Disney': 'Dísni', 'Oswald': 'Ósuald', 'Mickey': 'Míki', 'Steamboat Willie': 'Stímbot Uíli', 'Ub Iwerks': 'Ab Áiuerks', 'Iwerks': 'Áiuerks', 'Al Michaels': 'Al Máikels', 'Harry Potter': 'Jári Póter', 'Passepartout': 'Paspartú', 'Hollywood': 'Jólibud', 'Valentina Ivanova': 'Valentina Ivánova'}


def hablado(t):
    t = t.replace('*', '').replace('«', '').replace('»', '')
    for k, v in EN.items(): t = t.replace(k, v)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)


src, name = sys.argv[1], sys.argv[2]
L = json.load(open(src))
out = f'{ROOT}/audio/lineas_{name}'; os.makedirs(out, exist_ok=True)
for i, l in enumerate(L):
    f = f'{out}/l{i:03d}.mp3'
    if os.path.exists(f) and os.path.getsize(f) > 2000: continue
    body = json.dumps({'model': 'microsoft/mai-voice-2.1', 'input': hablado(l['t']), 'voice': 'es-MX-Grant', 'response_format': 'mp3'})
    for k in range(6):
        r = subprocess.run(['curl', '-s', '-m', '120', '-w', '%{http_code}', '-o', f, 'https://gen.pollinations.ai/v1/audio/speech',
                            '-H', 'Authorization: Bearer proxy-injected', '-H', 'Content-Type: application/json', '-d', body], capture_output=True, text=True)
        if r.stdout.strip() == '200' and os.path.getsize(f) > 2000: break
        print('reintento', i, r.stdout, file=sys.stderr); time.sleep(5 + 5 * k)
    print(i, os.path.getsize(f), file=sys.stderr)
print('OK')

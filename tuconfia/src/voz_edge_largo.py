"""Voz del largo con Microsoft Edge TTS (gratis, por el proxy): una petición por línea en audio/lineas_<n>/. Uso: python3 -I src/voz_edge_largo.py <guion_final.json> <nombre>"""
import json, re, sys, os, asyncio
import edge_tts
from num2words import num2words
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = {'Steven Spielberg': 'Stíven Spílberg', 'Spielberg': 'Spílberg', 'Universal': 'Iunivérsal', 'Amblin': 'Ámblin', 'Duel': 'Dúel', 'Theodor Geisel': 'Tíodor Gáisel', 'Geisel': 'Gáisel', 'Dr. Seuss': 'Doctor Sus',
      'And to Think That I Saw It on Mulberry Street': 'Ánd tu Zink Zat Ai So It on Málberi Estríit', 'Dyson': 'Dáison', 'James': 'Yeims', 'Sara Blakely': 'Sara Bléikli', 'Spanx': 'Spanks', 'Neiman Marcus': 'Níman Márcus',
      'Oprah Winfrey': 'Ópra Uínfri', 'Fortune': 'Fórchun', 'Soichiro Honda': 'Soichiro Jónda', 'Honda': 'Jónda', 'Long Beach': 'Long Bich', 'Dallas': 'Dálas', 'Motor': 'Mótor'}
def hablado(t):
    t = t.replace('*', '').replace('«', '').replace('»', '')
    for k, v in sorted(PH.items(), key=lambda x: -len(x[0])): t = t.replace(k, v)
    t = re.sub(r'(\d+)\.(\d{3})', r'\1\2', t)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)
src, name = sys.argv[1], sys.argv[2]
L = json.load(open(src)); out = f'{ROOT}/audio/lineas_{name}'; os.makedirs(out, exist_ok=True)
VOICE = os.environ.get('VOZ_ID', 'es-CO-GonzaloNeural')
async def one(i, l, sem):
    f = f'{out}/l{i:03d}.mp3'
    if os.path.exists(f) and os.path.getsize(f) > 2000: return
    async with sem:
        await edge_tts.Communicate(hablado(l['t']), VOICE, proxy=os.environ['HTTPS_PROXY'], rate='+0%').save(f)
async def main():
    sem = asyncio.Semaphore(4); await asyncio.gather(*[one(i, l, sem) for i, l in enumerate(L)])
asyncio.run(main()); print('OK', len(L))

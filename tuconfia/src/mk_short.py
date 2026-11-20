"""Short desde una ficha docs/canal/shorts/<n>.json (guion a mano, reparto, escenas, ganchos): voz Edge, render, fotogramas.
Uso: python3 -I src/mk_short.py <nombre>"""
import json, re, os, sys, subprocess
from num2words import num2words
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n = sys.argv[1]
S = json.load(open(f'{ROOT}/docs/canal/shorts/{n}.json'))
def h(t):
    t = t.replace('*', '')
    for k, v in sorted(S['fonetica'].items(), key=lambda x: -len(x[0])): t = t.replace(k, v)
    t = re.sub(r'(\d+)\.(\d{3})', r'\1\2', t)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)
lines = [dict(id=f'L{i + 1}', rol='', t=t, tts=h(t), gen=f'[{e}] {h(t)}', p=.4, tag='') for i, (e, t) in enumerate(S['lines'])]
json.dump(dict(titulo=n, meta=dict(famoso=S['famoso']), lines=lines), open(f'{ROOT}/script_{n}_short.json', 'w'), ensure_ascii=False, indent=1)
c = S['cast']
cast = {k: dict(skin=c['skin'], hair=c['hair'], style=c['style'], outfit=o, beard=c.get('beard', False), glasses=c.get('glasses', False), strong=s) for k, o, s in (('young', c.get('young_outfit', 'tee_red'), False), ('adult', c.get('outfit', 'blazer'), True))}
json.dump(dict(cast=cast, scenes=S['scenes'], turn=S['turn'], hooks=S['hooks']), open(f'{ROOT}/story_{n}.json', 'w'), ensure_ascii=False, indent=1)
for s_ in S['scenes']: assert s_['kit'] in ('e_hook', 'e_flop', 'e_fired', 'e_write', 'e_sign', 'e_one', 'e_oscar', 'close'), s_
for hk in S['hooks']: assert len(hk['l1']) <= 13 and len(hk['l2']) <= 13, hk
env = dict(os.environ, STORY=n)
subprocess.run(['python3', '-I', f'{ROOT}/src/voz_short.py', n], check=True)
subprocess.run(['python3', '-I', f'{ROOT}/src/build_story_short.py'], env=env, check=True)
sh = []
for t in (1, 6, 12, 18, 24, 30):
    subprocess.run(['python3', '-I', f'{ROOT}/src/build_story_short.py', '--still', str(t)], env=env, capture_output=True)
subprocess.run(f"python3 -c \"from PIL import Image;ims=[Image.open('{ROOT}/out/still_%.1f.png'%t).resize((270,480)) for t in (1,6,12,18,24,30)];s=Image.new('RGB',(1620,480));[s.paste(im,(i*270,0)) for i,im in enumerate(ims)];s.save('/tmp/w/sheet_{n}.png')\"", shell=True)
print('OK', n)

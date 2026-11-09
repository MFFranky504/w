"""Short vertical casi automático: Gemini elige hechos, guion, reparto, escenas y ganchos; este script hace voz, alineación, render y QA.
Uso: python3 auto_short.py <nombre> "<famoso>" ["<enfoque>"]   (voz: ElevenLabs por el proxy; Gemini: clave inyectada)"""
import sys, os, re, json, subprocess, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, who = sys.argv[1], sys.argv[2]
angle = sys.argv[3] if len(sys.argv) > 3 else ''
facts = sys.argv[4] if len(sys.argv) > 4 else ''
KITS = """e_hook: escenario/club, el protagonista actúa (gancho musical). e_flop: tienda de discos vacía, protagonista triste (fracaso comercial). e_fired: cocina/restaurante, un jefe le entrega un papel (despido, rechazo en un trabajo normal). e_write: cuarto nocturno, escribe en un escritorio (perseverar). e_sign: oficina, ejecutivo y contrato (firmar, segunda oportunidad). e_one: club con confeti (éxito, número uno). e_oscar: podio con estatuilla dorada (premio).
m_hook: cancha de baloncesto, protagonista driblando (gancho deportivo). m_jv: vestuario con lista en la pared, protagonista y entrenador (rechazo de equipo). m_train: entrena de noche. m_shot: tiro decisivo con confeti. m_draft: oficina con contrato (fichaje/draft). m_win: podio con trofeo.
j_field: campo de fútbol americano de noche (gancho deportivo). j_seven: casa, billetes sobre la mesa (sin dinero). j_dad: gimnasio con mentor (nuevo camino). b_draft: sala de draft con tablero. b_passed: tres personas sentadas (otros elegidos antes). b_bench: banca de suplentes. b_win: podio con trofeo y confeti. b_grind: entrena de noche en el campo.
close: SIEMPRE la última escena (amanecer con el espectador)."""
PROMPT = f"""Eres productor de Shorts motivacionales verticales en español latino para el canal "Tu ConfIA". Famoso: {who}. {angle}
Fórmula fija: gancho "Hasta X fue rechazado/cortado/despedido" o "X podía... pero se negó" → fracaso → giro → frase final → pregunta final reflexiva (sin cliché "tu fracaso es el inicio"). SOLO hechos que sepas con certeza; lo no confirmado con "según ha contado". Nunca "el mejor de la historia". Nada inventado.
HECHOS PERMITIDOS (usa SOLO estos; no añadas ningún otro dato, fecha, edad ni cifra): {facts}
1) Verifica los hechos clave (VERIFICADO/DUDOSO/FALSO) y descarta lo dudoso.
2) Guion de 9 líneas (~40 s), máx 18 palabras por línea. Campo t con *énfasis* en 1-2 palabras y los nombres propios con su ORTOGRAFÍA REAL (nunca fonética); años y cifras en dígitos en t; campo tts: lo hablado con años en palabras y nombres propios en pronunciación fonética española (ej. Michael Jordan = Máicol Yórdan); emo: bold|sad|hopeful|excited|warmly|softly.
3) Reparto visual: "young" y "adult" (el protagonista de joven y ya famoso): skin [r,g,b] realista, hair [r,g,b], style short|tab|king, outfit uno de grey|polo|tee_red|tee_blue|tee_yellow|blazer|hoodie, beard bool, glasses bool, strong bool.
4) Escenas, EN ORDEN, cada una con "kit" y "line" (índice 0-based de la línea con la que arranca; índices estrictamente crecientes; primera line=0; la última escena es kit close en la línea de la frase final). Entre 6 y 8 escenas. Kits disponibles:
{KITS}
Elige los que mejor encajen con lo narrado; si ninguno encaja, el más neutro. No uses kits de otro deporte/género que contradigan la historia (p. ej. no uses cancha para un cantante).
5) "turn": índice de la escena donde ocurre el giro (≥1). "hooks": 4-5 ganchos de pantalla {{"scene":i,"start":0.3,"end":2.6,"l1":"máx 12 caracteres MAYÚSCULAS","l2":"máx 13"}}; el primero en la escena 0 con start 0.15; no pongas gancho en la última escena.
6) "titulo_short" (≤70 caracteres, 1 emoji, sin mentir), "resumen" (2 frases con cifras en números), "pregunta" (la de la última línea), "hashtag" (#Nombre), "riesgos" (lista de datos a confirmar), "fonetica" (objeto {{"ortografía real": "pronunciación fonética española"}} para cada nombre propio o título en inglés, ej. {{"Michael Jordan": "Máicol Yórdan"}}).
Responde SOLO JSON con claves: hechos, lines (lista de objetos {{t,tts,emo}}), cast, scenes, turn, hooks, titulo_short, resumen, pregunta, hashtag, riesgos."""


def gemini(prompt, model="gemini-3.1-flash-lite"):
    """Gemini directo, o NVIDIA NIM si el modelo empieza por 'nvidia/' (MiniMax razona: max_tokens alto)."""
    if model.startswith("nvidia/"):
        url, model, mt = "https://integrate.api.nvidia.com/v1/chat/completions", model[7:], 400
    else:
        url, mt = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", 8000
    req = urllib.request.Request(url, json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": mt}).encode(),
        {"Authorization": "Bearer proxy-injected", "content-type": "application/json"})
    m = json.load(urllib.request.urlopen(req, timeout=170))["choices"][0]["message"]
    return m.get("content") or m.get("reasoning_content") or ""


import time
for attempt in range(5):
    try:
        d = json.loads(re.search(r'\{.*\}', gemini(PROMPT, os.environ.get('SCRIPT_MODEL', 'gemini-3.1-flash-lite')), re.S).group(0))
        sc, ls = d['scenes'], d['lines']
        assert all(isinstance(l, dict) and l.get('t') and l.get('tts') for l in ls), 'lines debe ser lista de objetos t/tts/emo'
        for l in ls: l.setdefault('emo', 'warmly')
        assert len(ls) >= 6 and sc[0]['line'] == 0 and sc[-1]['kit'] == 'close'
        assert all(a['line'] < b['line'] for a, b in zip(sc, sc[1:])) and 1 <= d['turn'] < len(sc) - 1
        assert all(0 <= x['line'] < len(ls) for x in sc) and all(h['scene'] < len(sc) - 1 for h in d['hooks'])
        break
    except Exception as e:
        print('Modelo de guion falló, reintento:', repr(e)[:120]); d = None; time.sleep(30)
if not d: sys.exit('sin guion válido')
from num2words import num2words
def hablado(t):
    t = t.replace('*', '')
    for real, ph in sorted((d.get('fonetica') or {}).items(), key=lambda x: -len(x[0])): t = t.replace(real, ph)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)
EN = {'Harrison Ford': 'Járison Ford', 'Star Wars': 'Star Uars', 'Indiana Jones': 'Índiana Yons', 'American Graffiti': 'Américan Grafiti',
      'Michael Jordan': 'Máicol Yórdan', 'Taylor Swift': 'Téilor Suift', 'Morgan Freeman': 'Mórgan Fríman', 'Eminem': 'Éminem',
      'Lady Gaga': 'Léidi Gágá', 'Albert Einstein': 'Álbert Áinstain', 'ETH Zurich': 'E T H Súrij', 'Nobel': 'Nóbel', 'Dwayne Johnson': 'Duéin Yónson', 'Tom Brady': 'Tom Bréidi', 'Million Dollar Baby': 'Míllion Dólar Béibi',
      'Lose Yourself': 'Lus Yorself', 'The Shawshank Redemption': 'The Shóshank Ridénshon', 'Driving Miss Daisy': 'Dráiving Mis Deisi'}
def hablado_en(t):
    t = t.replace('*', '')
    for k, v in sorted(EN.items(), key=lambda x: -len(x[0])): t = t.replace(k, v)
    return re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='es'), t)
for l in ls: l['tts'] = hablado_en(l['t'])
# reparto: normalizar a {young, adult} con valores numéricos
def _col(v):
    if isinstance(v, str): v = [int(x) for x in re.findall(r'\d+', v)]
    return list(v)
_c = d['cast']
if 'adult' not in _c:
    _c = {'adult': _c, 'young': dict(_c, outfit='tee_red', beard=False)}
d['cast'] = {k: dict(v, skin=_col(v.get('skin', [240, 200, 170])), hair=_col(v.get('hair', [60, 40, 30]))) for k, v in _c.items()}
lines = [dict(id=f"L{i + 1}", rol='', t=l['t'], tts=l['tts'], gen=f"[{l['emo']}] {l['tts']}", p=.4, tag='') for i, l in enumerate(ls)]
json.dump(dict(titulo=name, meta=dict(famoso=who), lines=lines), open(f'{ROOT}/script_{name}_short.json', 'w'), ensure_ascii=False, indent=1)
json.dump(dict(cast=d['cast'], scenes=sc, turn=d['turn'], hooks=d['hooks']), open(f'{ROOT}/story_{name}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(d, open(f'{ROOT}/gemini_{name}.json', 'w'), ensure_ascii=False, indent=1)
tts = ' '.join(l['tts'] for l in lines)
tmp = '/tmp/w/dk'; os.makedirs(tmp, exist_ok=True)
open(f'{tmp}/{name}.json', 'w').write(json.dumps({"text": ' '.join(l['gen'] for l in lines), "model_id": "eleven_v3", "language_code": "es", "seed": 7, "voice_settings": {"stability": 0.0, "similarity_boost": 0.8, "style": 0.8}}))
open(f'{tmp}/{name}_tts.txt', 'w').write(tts)
sh = lambda c: subprocess.run(c, shell=True, check=True)
sh(f"curl -sf -m 180 -X POST 'https://api.elevenlabs.io/v1/text-to-speech/IKne3meq5aSn9XLyUdCD?output_format=mp3_44100_128' -H 'xi-api-key: x' -H 'content-type: application/json' -d @{tmp}/{name}.json -o {tmp}/{name}.mp3")
sh(f'ffmpeg -y -v error -i {tmp}/{name}.mp3 -af "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-45dB:stop_silence=0.3,atempo=1.07" -b:a 192k {ROOT}/audio/narracion_{name}_short.mp3')
sh(f'curl -sf -m 120 -X POST https://api.elevenlabs.io/v1/forced-alignment -H "xi-api-key: x" -F "file=@{ROOT}/audio/narracion_{name}_short.mp3" -F "text=<{tmp}/{name}_tts.txt" -o {ROOT}/audio/alineacion_{name}_short.json')
env = dict(os.environ, STORY=name)
subprocess.run(['python3', '-I', f'{ROOT}/src/build_story_short.py'], env=env, check=True)
stills = []
for t in (1, 5, 10, 15, 20, 25, 30, 35):
    subprocess.run(['python3', '-I', f'{ROOT}/src/build_story_short.py', '--still', str(t)], env=env, capture_output=True)
    stills.append(f'{ROOT}/out/still_{t:.1f}.png')
qa = subprocess.run(['python3', f'{ROOT}/src/gemini_qa.py', f"Eres ABOGADO DEL DIABLO hostil de QA de un Short vertical pixel-art (1080x1920) sobre {who}. Fotogramas en orden a 1,5,10,15,20,25,30,35 s. Zonas fijas por diseño: logo TU CONF.IA arriba, ganchos bajo el logo, subtítulos abajo sobre el cuerpo, tarjeta final al final. Lista SOLO errores reales: texto cortado, sprites flotando, desproporciones, escena que contradice lo narrado, ortografía. Narración: " + ' | '.join(l['t'] for l in lines)] + stills, capture_output=True, text=True).stdout
open(f'{ROOT}/qa_{name}.txt', 'w').write(qa)
H = f"#Motivación #Superación #HistoriasQueInspiran {d['hashtag']}"
for p, extra in (('youtube', '▶️ Suscríbete: una historia que inspira cada día.'), ('tiktok', '➕ Sígueme para más historias que inspiran.'), ('instagram', '➕ Sígueme para más historias que inspiran. (Canal @tu.conf.ia77)')):
    open(f'{ROOT}/caption_{name}_short_{p}.txt', 'w').write(f"{d['titulo_short']}\n\n{d['resumen']}\n\n{d['pregunta']} Cuéntamelo en los comentarios 👇\n\n🔖 Guárdalo para cuando lo necesites.\n\n{H}\n\n{extra}\n")
print(json.dumps({'titulo': d['titulo_short'], 'riesgos': d['riesgos']}, ensure_ascii=False, indent=1)); print(qa[:1800])

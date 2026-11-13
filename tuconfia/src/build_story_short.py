"""TU CONF.IA - montaje. Uso: python3 -I build.py [--preview N_segundos]
Si existe ../audio/narracion.(mp3|wav|m4a) los tiempos se adaptan a la voz real; si no, se estiman."""
import sys, os, json, re, math, subprocess, glob, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import scenes as S
import scenes2 as S2
import scenes3 as S3
import scenes5 as S5
import scenes6 as S6
import scenes13 as S13
import scenes14 as S14
import scenes17 as S17
from cta import draw_cta
from lib import WW, WH, BAY, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, VW, VH = 30, 1080, 1920
LOOP_D = 0.9      # disolvencia final hacia el primer fotograma (bucle)
SR = 44100
STORY = os.environ['STORY']
DYN = os.path.exists(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/story_{STORY}.json')
SC = json.load(open(f'{ROOT}/script_{STORY}_short.json'))
LINES = SC['lines']
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- tiempos
narr = next(iter(glob.glob(f'{ROOT}/audio/narracion_{STORY}_short.*')), None)


def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def load_mono(path, sr):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def align_real(path):
    x = load_mono(path, 16000)
    hop = 160
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    thr = rms.max() * 0.03
    sp = rms > thr
    # huecos de silencio >= 0.2 s
    gaps, i = [], 0
    while i < n:
        if not sp[i]:
            j = i
            while j < n and not sp[j]: j += 1
            if j - i >= 20 and i > 0 and j < n: gaps.append(((i + j) / 2 * hop / 16000, i * hop / 16000, j * hop / 16000))
            i = j
        else: i += 1
    first = int(np.argmax(sp)) * hop / 16000
    last = (n - int(np.argmax(sp[::-1]))) * hop / 16000
    # asignación óptima (programación dinámica) de las fronteras entre líneas a los huecos de silencio detectados
    chars = np.array([len(clean(l['t'])) for l in LINES], float)
    nint = np.array([len(re.findall(r'\.\.\.|[.?!:,;](?=\s*\S)', clean(l['t'][:-1]))) for l in LINES], float)   # pausas internas esperadas
    K = len(LINES) - 1
    G = [((a + b) / 2, a, b) for _, a, b in gaps]
    # cps global: duración total = sum(chars)/cps + 0.4*pausas internas + 0.5*fronteras
    T = last - first
    cps = chars.sum() / max(1e-3, T - 0.4 * nint.sum() - 0.5 * K)
    exp_d = chars / cps + 0.4 * nint + 0.5
    INF = 1e18
    n = len(G)
    best = [[INF] * n for _ in range(K)]; prev = [[-1] * n for _ in range(K)]
    for j in range(n):
        best[0][j] = (G[j][0] - first - exp_d[0]) ** 2 - 2.0 * (G[j][2] - G[j][1])
    for k in range(1, K):
        for j in range(k, n):
            for i in range(k - 1, j):
                c = best[k - 1][i] + (G[j][0] - G[i][0] - exp_d[k]) ** 2 - 2.0 * (G[j][2] - G[j][1])
                if c < best[k][j]: best[k][j] = c; prev[k][j] = i
    tail = [(best[K - 1][j] + (last - G[j][0] - exp_d[-1]) ** 2, j) for j in range(K - 1, n)]
    j = min(tail)[1]
    sel = []
    for k in range(K - 1, -1, -1):
        sel.append(j); j = prev[k][j]
    sel.reverse()
    bounds = [(G[j][1], G[j][2]) for j in sel]
    starts, ends = [first], []
    for a, b in bounds: ends.append(a); starts.append(b)
    ends.append(last)
    return starts, ends, last + .45 + LOOP_D


def estimate():
    t, starts, ends = 0.25, [], []
    for l in LINES:
        d = len(clean(l['t'])) / 16.5
        starts.append(t); ends.append(t + d); t += d + l['p']
    return starts, ends, t + 1.0 + LOOP_D


FA = f'{ROOT}/audio/alineacion_{STORY}_short.json'
LW = {}                                      # palabras con tiempos exactos (alineación forzada de ElevenLabs)
if narr and os.path.exists(FA):
    ws = [w for w in json.load(open(FA))['words'] if w['text'].strip()]
    k_ = 0
    for l in LINES:
        n_ = len(l['tts'].split()); LW[l['id']] = ws[k_:k_ + n_]; k_ += n_
    assert k_ == len(ws), (k_, len(ws))
    st = [LW[l['id']][0]['start'] for l in LINES]; en = [LW[l['id']][-1]['end'] for l in LINES]
    TOTAL = round((en[-1] + 3.2 + LOOP_D) * FPS) / FPS          # nº entero de fotogramas: el bucle encaja al cuadro
    MODE = 'voz real (alineación forzada)'
elif narr:
    st, en, TOTAL = align_real(narr)
    MODE = 'voz real'
else:
    st, en, TOTAL = estimate()
    MODE = 'estimado (sin narración)'
LSTART, LEND = dict(zip([l['id'] for l in LINES], st)), dict(zip([l['id'] for l in LINES], en))
ids = [l['id'] for l in LINES]
print('modo:', MODE, 'duración total', round(TOTAL, 2), file=sys.stderr)

# ---------------------------------------------------------------- escenas
lid = lambda p: next(l['id'] for l in LINES if clean(l['t']).startswith(p))
PS = S2.portrait_scene
Z0 = [(0, 80, 146, 1.0), (1, 80, 150, 1.1)]
cutc = lambda u: [(0, 80, 146, 1.0), (u, 80, 146, 1.0), (u + .0001, 80, 175, 1.25), (1, 80, 175, 1.25)]
if DYN:
    import cast as _cast
    _D = json.load(open(f'{ROOT}/story_{STORY}.json'))
    for _k, _c in _D['cast'].items():
        _cast.CAST[f'x_{STORY}_{_k}'] = dict(style=_c.get('style', 'short'), skin=tuple(_c['skin']), hair=_cast.ramp(tuple(_c['hair'])), iris=(70, 70, 90), outfit=_c.get('outfit', 'grey'), strong=bool(_c.get('strong')), stubble=bool(_c.get('beard')), glasses=bool(_c.get('glasses')))
    _MAP = {n: f'x_{STORY}_adult' for n in ('em', 'mj', 'johnson', 'brady', 'gaga')}
    _MAP.update({n: f'x_{STORY}_young' for n in ('mj_y', 'johnson_y', 'brady_y', 'emw', 'gagaw')})
    _cast.CAST[f'x_{STORY}_extra'] = dict(style='short', skin=(200, 150, 120), hair=_cast.ramp((50, 40, 30)), iris=(60, 44, 36), outfit='polo', stubble=False)
    _MAP.update({n: f'x_{STORY}_extra' for n in ('coachj', 'execg', 'qb2', 'dre', 'prod1', 'prod2')})
    _r, _b = S13.rpg, S13.bat
    for _m in (S13, S14):
        _m.rpg = lambda w, *a, _r=_r, **k: _r(_MAP.get(w, w), *a, **k)
        _m.bat = lambda w, *a, _b=_b, **k: _b(_MAP.get(w, w), *a, **k)
    _sc = _D['scenes']
    CFG = dict(turn=f"s{_D['turn']}", pre=f"s{_D['turn'] - 1}", late=f"s{len(_sc) - 2}",
               sc=[(f's{i}' if i < len(_sc) - 1 else 'cierre', LINES[x['line']]['id'], x['kit']) for i, x in enumerate(_sc)],
               hooks=[(f"s{h['scene']}" if h['scene'] < len(_sc) - 1 else 'cierre', h['start'], h['end'], h['l1'], h['l2'], 520) for h in _D['hooks']])
    SCENES = [dict(n=n_, a=i_, b=i_, fn=(lambda f: (lambda t, u: getattr(S17 if hasattr(S17, f) else S14 if hasattr(S14, f) else S13, f)(t, u)))(f_), cam=cutc(.5)) for n_, i_, f_ in CFG['sc']]
else:
    CFG = {
     'johnson': dict(turn='dad', pre='seven', late='star',
       sc=[('field', 'Hasta Dwayne', 'j_field'), ('nobody', 'Soñaba', 'j_nobody'), ('cut', 'Firmó', 'j_cut'), ('seven', 'Según ha', 'j_seven'), ('dad', 'Su padre', 'j_dad'), ('debut', 'En mil', 'j_debut'), ('star', 'Y el que fue', 'j_star'), ('cierre', 'Ser cortado', 'close')],
       hooks=[('field', .15, 1.4, '¡LO CORTARON!', '', 520), ('cut', .3, 2.8, '¡CORTADO EN', 'DOS MESES!', 520), ('seven', .3, 2.8, '¡SOLO 7', 'DÓLARES!', 520), ('dad', .3, 2.8, '¡UN NUEVO', 'CAMINO!', 520), ('star', .3, 3.0, '¡SE VOLVIÓ', 'UNA ESTRELLA!', 520), ('cierre', 4.0, 6.6, '¿Y TÚ', 'QUÉ HARÁS?', 520)]),
     'brady': dict(turn='injury', pre='bench', late='win',
       sc=[('draft', 'Hasta Tom', 'b_draft'), ('passed', 'Ciento noventa', 'b_passed'), ('bench', 'Empezó', 'b_bench'), ('injury', 'Hasta que', 'b_injury'), ('win', 'Ganó ese', 'b_win'), ('grind', 'Según ha', 'b_grind'), ('cierre', 'No eligieron', 'close')],
       hooks=[('draft', .15, 2.6, '¡EL NÚMERO', '199!', 700), ('passed', .3, 2.9, '¡198 ANTES', 'QUE ÉL!', 700), ('injury', .3, 2.9, '¡LE LLEGÓ', 'SU TURNO!', 520), ('win', .3, 3.0, '¡7 SÚPER', 'BOWLS!', 520), ('cierre', 3.6, 6.2, '¿Y TÚ', 'QUÉ HARÁS?', 520)]),
     'gaga': dict(turn='sign', pre='write', late='one',
       sc=[('hook', 'Hasta Lady', 'g_hook'), ('label', 'En dos mil', 'g_label'), ('diner', 'Según ha', 'g_diner'), ('write', 'Pero no', 'g_write'), ('sign', 'Hasta que', 'g_sign'), ('one', 'Y su primer', 'g_one'), ('cierre', 'A veces', 'close')],
       hooks=[('hook', .15, 1.9, '¡LA', 'DESPIDIERON!', 520), ('label', .3, 3.0, '¡A LOS POCOS', 'MESES!', 520), ('diner', .3, 2.0, '¡DE MESERA!', '', 520), ('sign', .2, 2.0, '¡OTRA', 'OPORTUNIDAD!', 520), ('one', .3, 3.4, '¡NÚMERO UNO', 'EN EL MUNDO!', 520), ('cierre', 5.8, 8.4, '¿Y TÚ', 'QUÉ HARÁS?', 520)]),
     'eminem': dict(turn='dre', pre='write', late='oscar',
       sc=[('hook', 'Hasta Éminem', 'e_hook'), ('flop', 'En mil novecientos noventa y seis', 'e_flop'), ('fired', 'Después', 'e_fired'), ('write', 'Pero siguió', 'e_write'), ('dre', 'En mil novecientos noventa y ocho', 'e_sign'), ('album', 'Un año', 'e_one'), ('oscar', 'Luego', 'e_oscar'), ('cierre', 'Su fracaso', 'close')],
       hooks=[('hook', .15, 2.0, '¡FRACASÓ CON', 'SU 1ER DISCO!', 520), ('fired', .3, 2.6, '¡LO', 'DESPIDIERON!', 520), ('dre', .2, 2.0, '¡UNA NUEVA', 'OPORTUNIDAD!', 520), ('album', .3, 2.6, '¡Y TODO', 'CAMBIÓ!', 520), ('oscar', .3, 2.8, '¡GANÓ UN', 'ÓSCAR!', 520), ('cierre', 5.2, 7.8, '¿Y TÚ', 'QUÉ HARÁS?', 520)]),
     'jordan': dict(turn='shot', pre='train', late='win',
       sc=[('hook', 'Hasta Michael', 'm_hook'), ('jv', 'En su preparatoria', 'm_jv'), ('train', 'Según ha', 'm_train'), ('shot', 'En mil novecientos ochenta y dos', 'm_shot'), ('draft', 'En mil novecientos ochenta y cuatro', 'm_draft'), ('win', 'Y con ellos', 'm_win'), ('cierre', 'Lo cortaron', 'close')],
       hooks=[('hook', .15, 2.0, '¡FUE', 'CORTADO!', 520), ('jv', .3, 2.8, '¡AL EQUIPO', 'JUVENIL!', 520), ('train', .3, 2.8, '¡ENTRENÓ', 'MÁS QUE NADIE!', 520), ('shot', .3, 2.8, '¡EL TIRO', 'GANADOR!', 520), ('win', .3, 2.8, '¡6 TÍTULOS', 'DE LA NBA!', 520)]),
    }[STORY]
    SCENES = []
    for n_, p_, f_ in CFG['sc']:
        cam_ = Z0 if n_ in ('nobody', 'passed') else cutc(.5)
        SCENES.append(dict(n=n_, a=lid(p_), b=lid(p_), fn=(lambda f: (lambda t, u: getattr(S13, f)(t, u)))(f_), cam=cam_))
for i, s in enumerate(SCENES):
    s['t0'] = 0.0 if i == 0 else (LEND[SCENES[i - 1]['b']] + LSTART[s['a']]) / 2 if False else (LSTART[s['a']] if i else 0.0)
    s['t1'] = TOTAL if i == len(SCENES) - 1 else LSTART[SCENES[i + 1]['a']]
SCENES[0]['t0'] = 0.0
# la escena empieza ligeramente antes de la voz (hueco de pausa)
for i in range(1, len(SCENES)):
    prev_end = LEND[SCENES[i - 1]['b']]
    SCENES[i]['t0'] = max(prev_end + 0.05, LSTART[SCENES[i]['a']] - 0.15)
    SCENES[i - 1]['t1'] = SCENES[i]['t0']

TR = 0.28  # dissolve
DROP_T = next(x['t0'] for x in SCENES if x['n'] == CFG['turn']) + .02


def cam_at(kf, u):
    for (u0, *a), (u1, *b) in zip(kf, kf[1:]):
        if u0 <= u <= u1:
            k = ease((u - u0) / (u1 - u0) if u1 > u0 else 1)
            return [p + (q - p) * k for p, q in zip(a, b)]
    return list(kf[-1][1:])


CUTS = []
for s_ in SCENES:
    for (u0, *_), (u1, *_) in zip(s_['cam'], s_['cam'][1:]):
        if u1 - u0 < .001: CUTS.append(s_['t0'] + u0 * (s_['t1'] - s_['t0']))
TKIND = (['dissolve', 'whip', 'dissolve', 'flash', 'whip', 'zoom', 'dissolve', 'dissolve'] * 3)[:len(SCENES) - 1]


def render_scene(i, t, neg=False):
    s = SCENES[i]
    d = max(1e-3, s['t1'] - s['t0'])
    u = max(0, min(1, (t - s['t0']) / d))
    tl = (t - s['t0']) if neg else max(0, t - s['t0'])         # neg: tiempo "virtual" anterior al inicio (para el bucle)
    img = s['fn'](tl, u)
    cx, cy, z = cam_at(s['cam'], u)
    for l in LINES:
        dt = t - LSTART[l['id']]
        if 0 <= dt < .35 and s['t0'] - .2 <= LSTART[l['id']] <= s['t1']: z *= 1 + .075 * math.exp(-dt / .1)
    sh_ = 0
    if 0 <= t - DROP_T < .4: sh_ = math.sin((t - DROP_T) * 90) * 9 * (1 - (t - DROP_T) / .4)
    for tc in CUTS:                                          # sacudida breve en cada corte duro
        if 0 <= t - tc < .25: sh_ += math.sin((t - tc) * 110) * 6 * (1 - (t - tc) / .25)
    cx += math.sin(t * 1.3) * .35; cy += math.cos(t * 1.7) * .3   # balanceo de cámara
    # cámara pixel-perfect: escala ENTERA (8, 9, 10, 12... px por píxel del mundo) y recorte alineado a píxeles del mundo (sin interpolar)
    sc = max(8, int(round(8 * z))); cx += sh_ / 8; cy += sh_ / 11
    big = img.resize((WW * sc, WH * sc), Image.NEAREST)
    vw, vh = VW / sc, VH / sc
    x0 = int(round(min(max(cx - vw / 2, 0), WW - vw))) ; y0 = int(round(min(max(cy - vh / 2, 0), WH - vh)))
    x0 = min(x0, int(WW - vw)); y0 = min(y0, int(WH - vh))
    out = big.crop((x0 * sc, y0 * sc, x0 * sc + VW, y0 * sc + VH))
    out = ImageEnhance.Color(out).enhance(1.28)
    return ImageEnhance.Contrast(out).enhance(1.06)


# patrón de disolvencia ordenada (Bayer) a resolución final
BAYF = np.kron(np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (VH // 32 + 1, VW // 32 + 1)), np.ones((8, 8)))[:VH, :VW]

# ---------------------------------------------------------------- overlay
F = lambda w, s: ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{w}.otf', s)
FL = lambda s: ImageFont.truetype(f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff', s)      # tipografía de subtítulos y marca
YEL, WHITE, DARK = (255, 216, 74), (255, 255, 255), (14, 10, 26)
PURPLE = (139, 92, 246)      # logo TU CONF.IA
BRAND = Image.new('RGBA', (VW, VH), (0, 0, 0, 0))
bd = ImageDraw.Draw(BRAND)
fb = F('Black', 50)
w1 = bd.textlength('TU CONF', font=fb); w2 = bd.textlength('.IA', font=fb)
bx = (VW - (w1 + w2)) / 2
bd.text((bx + 3, 233), 'TU CONF', font=fb, fill=(0, 0, 0, 160)); bd.text((bx, 230), 'TU CONF', font=fb, fill=WHITE)
bd.rounded_rectangle([bx + w1 - 2, 228, bx + w1 + w2 + 10, 292], radius=8, fill=PURPLE)
bd.text((bx + w1 + 4, 230), '.IA', font=fb, fill=WHITE)
MASC = Image.open(f'{ROOT}/assets/mascota_retrato.png').convert('RGBA')
MASC = MASC.resize((MASC.width * 5, MASC.height * 5), Image.NEAREST)

# subtítulos por fragmentos
CHUNKS = []
for l in LINES:
    words = re.findall(r'\*[^*]+\*|\S+', l['t'])
    # re-tokenizar manteniendo marca de énfasis por palabra
    toks = []
    for m in re.finditer(r'\*([^*]+)\*([^\s*]*)|([^\s*]+)', l['t']):
        if m.group(1):
            for w in m.group(1).split(): toks.append((w, True))
            if m.group(2): toks[-1] = (toks[-1][0] + m.group(2), True)
        else: toks.append((m.group(3), False))
    groups, cur, n = [], [], 0
    tokw = [5 if re.fullmatch(r'\d{4}\W*', w) else 1 for w, _ in toks]          # un año se dice con 5 palabras
    for w, e in toks:
        if cur and (n + len(w) > 12 or len(cur) >= 3 or (cur[-1][0][-1] in '.?!…' )):
            groups.append(cur); cur, n = [], 0
        cur.append((w, e)); n += len(w) + 1
    if cur: groups.append(cur)
    tot = sum(len(' '.join(w for w, _ in g)) + 2 for g in groups)
    t0, t1 = LSTART[l['id']], LEND[l['id']]
    if l['id'] in LW and sum(tokw) == len(LW[l['id']]):
        wi, tp, firsts = 0, 0, []                                       # índice de la primera palabra hablada de cada grupo
        for g in groups:
            firsts.append(wi); wi += sum(tokw[tp:tp + len(g)]); tp += len(g)
        starts_ = [LW[l['id']][i]['start'] for i in firsts]
        for gi, g in enumerate(groups):
            a_ = starts_[gi]; b_ = starts_[gi + 1] if gi + 1 < len(groups) else t1 + .12
            CHUNKS.append((a_ if gi else t0 - .05, b_, g, l['id']))
        continue
    a = t0
    for g in groups:
        d = (t1 - t0) * (len(' '.join(w for w, _ in g)) + 2) / tot
        CHUNKS.append((a, a + d, g, l['id'])); a += d


def draw_sub(img, t):
    if t > TOTAL - LOOP_D: return
    ch = next(((a, b, g, lid) for a, b, g, lid in CHUNKS if a <= t < b + 0.0), None)
    if not ch and t >= CHUNKS[-1][1]: ch = CHUNKS[-1]            # la pregunta final se queda en pantalla
    if not ch: return
    a, b, g, lid = ch
    size = 100
    ft = FL(size)
    d = ImageDraw.Draw(img)
    txt = ' '.join(w for w, _ in g).upper()
    GAP = lambda: int(size * .24)
    wid = lambda: d.textlength(txt.replace(' ', ''), font=ft) + GAP() * (len(g) - 1)
    while wid() > 840 and size > 60: size -= 4; ft = FL(size)
    pop = min(1, (t - a) / .09)
    sc = .86 + .14 * (1 - (1 - pop) ** 2)
    layer = Image.new('RGBA', (VW, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    total = wid()
    SUBCX = 500; x = (2 * SUBCX - total) / 2; y = 50
    for w, e in g:
        w = w.upper()
        ld.text((x, y), w, font=ft, fill=YEL if e else WHITE, stroke_width=7, stroke_fill=DARK)
        x += ld.textlength(w, font=ft) + GAP()
    for w, e in g: pass
    # relleno encima del trazo
    x = (2 * SUBCX - total) / 2
    for w, e in g:
        w = w.upper(); ld.text((x, y), w, font=ft, fill=YEL if e else WHITE); x += ld.textlength(w, font=ft) + GAP()
    if sc < 1:
        layer = layer.resize((int(VW * sc), int(220 * sc)), Image.BILINEAR)
        ox, oy = (VW - layer.width) // 2 + (SUBCX - VW // 2), (220 - layer.height) // 2
    else: ox = oy = 0
    ysub = 1170
    img.alpha_composite(layer, (ox, ysub + oy))


CAPS = {'board': ('STEVE JOBS, 30 AÑOS', 'cofundador de Apple'), 'next': ('NeXT Y PIXAR', 'empieza de cero'), 'crash': ('APPLE AL BORDE', 'de la quiebra'), 'devices': ('iMac · iPod · iPhone', 'productos que lideró')}
def draw_caps(img, t):
    for s_ in SCENES:
        if s_['n'] in CAPS and s_['t0'] + .25 < t < s_['t1'] - .1:
            k = min(1, (t - s_['t0'] - .25) / .35) * min(1, (s_['t1'] - .1 - t) / .25)
            a = int(255 * max(0, k)); d = ImageDraw.Draw(img)
            l1, l2 = CAPS[s_['n']]
            d.text((60, 340), l1, font=F('ExtraBold', 46), fill=(255, 255, 255, a), stroke_width=5, stroke_fill=(14, 10, 26, a))
            d.text((60, 398), l2, font=F('Medium', 36), fill=(255, 216, 74, a), stroke_width=4, stroke_fill=(14, 10, 26, a))


HOOKS = CFG['hooks']
SC_ = {s['n']: s for s in SCENES}
HOOK_T = [(SC_[n]['t0'] + a, SC_[n]['t0'] + c_, l1, l2, yy) for n, a, c_, l1, l2, yy in HOOKS]
PLAT = 'yt'          # yt = SUSCRÍBETE, tt/ig = SÍGUEME
END_T0 = LEND[LINES[-1]['id']] + .45
SC_ = {s['n']: s for s in SCENES}
HOOK_T = [(SC_[n]['t0'] + a, SC_[n]['t0'] + c_, l1, l2, yy) for n, a, c_, l1, l2, yy in HOOKS]


AVATAR = Image.open(f'{ROOT}/assets/avatar_canal.png').convert('RGBA').resize((320, 320), Image.LANCZOS)


def draw_endcard(img, t):
    """cierre: seguir el canal. Centrada (y 480-1130): fuera de la zona de botones de Shorts/Reels/TikTok."""
    if t < END_T0 or t > TOTAL - LOOP_D + .25: return
    k = min(1, (t - END_T0) / .35); out = min(1, (TOTAL - LOOP_D + .25 - t) / .25)
    W_, H_ = 900, 660
    lay = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([0, 0, W_, H_], radius=36, fill=(14, 10, 26, 225), outline=PURPLE, width=8)
    lay.alpha_composite(AVATAR, ((W_ - 320) // 2, 36))
    def tx(y, s, size, fill, font=None, stroke=8):
        ft = font or FL(size)
        while ld.textlength(s, font=ft) > W_ - 70 and size > 24: size -= 4; ft = font or FL(size)
        ld.text((W_ // 2, y), s, font=ft, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=DARK)
    tx(420, 'MÁS HISTORIAS QUE INSPIRAN', 40, WHITE)
    ld.rounded_rectangle([110, 462, W_ - 110, 568], radius=22, fill=(230, 30, 40, 255), outline=DARK, width=6)
    ld.polygon([(150, 487), (150, 543), (198, 515)], fill=WHITE)
    tx(516, 'SÍGUEME', 66, WHITE, stroke=0)
    tx(612, '@tu.conf.ia77', 50, (200, 170, 255), stroke=6)
    sc = .8 + .2 * (1 - (1 - k) ** 3)
    lay = lay.resize((int(W_ * sc), int(H_ * sc)), Image.LANCZOS)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
    img.alpha_composite(lay, (540 - lay.width // 2, 800 - lay.height // 2 - 20))


def draw_hooks(img, t):
    for a, c_, l1, l2, yy in HOOK_T:
        if not (a <= t < c_): continue
        k = min(1, (t - a) / .14); out = min(1, (c_ - t) / .15)
        sc = (.6 + .5 * k - .1 * k * k) if k < 1 else 1.0
        d = ImageDraw.Draw(img); ft = FL(92 if max(len(l1), len(l2)) < 13 else (80 if max(len(l1), len(l2)) < 15 else 68))
        w = max(d.textlength(l1, font=ft), d.textlength(l2, font=ft))
        lay = Image.new('RGBA', (900, 230), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for dx, dy, col in ((6, 6, (230, 40, 110)), (0, 0, None)):
            for n_, ln in enumerate((l1, l2)):
                x = (900 - ld.textlength(ln, font=ft)) / 2 + dx; y = 6 + n_ * 100 + dy
                ld.text((x, y), ln, font=ft, fill=col or (YEL if n_ == 0 else WHITE), stroke_width=8, stroke_fill=DARK if col is None else col)
        lay = lay.resize((int(900 * sc), int(230 * sc)), Image.BILINEAR)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
        img.alpha_composite(lay, (500 - lay.width // 2 + int(math.sin(t * 50) * 3 * (1 - k)), yy - lay.height // 2))


def draw_outro(img, t):
    s = SCENES[-1]
    if t < s['t0']: return
    u = min(1, (t - s['t0']) / .5)
    pop = 1 - (1 - u) ** 3
    bob = math.sin((t - s['t0']) * 2.4) * 8
    m = MASC
    y = int(VH - 150 - m.height * pop + (1 - pop) * 200 + bob)
    img.alpha_composite(m, ((VW - m.width) // 2, y))


def overlay(base, t):
    img = base.convert('RGBA')
    img.alpha_composite(BRAND)
    draw_hooks(img, t)
    draw_endcard(img, t)
    draw_sub(img, t)
    # fundido final
    out = img.convert('RGB')
    return out


def first_virtual(t):
    """la primera escena 'continúa' con tiempo negativo: al volver a empezar el movimiento (lluvia, cámara) no se interrumpe."""
    return render_scene(0, t - TOTAL, neg=True)


def frame(fi):
    t = fi / FPS
    idx = max(i for i, s in enumerate(SCENES) if s['t0'] <= t + 1e-6)
    img = render_scene(idx, t)
    HW = .15
    for bi in range(len(SCENES) - 1):
        T = SCENES[bi + 1]['t0']; kind = TKIND[bi]
        if abs(t - T) >= HW: continue
        k = (t - (T - HW)) / (2 * HW)
        a_ = render_scene(bi, t); b_ = render_scene(bi + 1, t)
        if kind == 'dissolve':
            m = (BAYF < ease(k))[..., None]; img = Image.fromarray(np.where(m, np.array(b_), np.array(a_)))
        elif kind == 'flash':
            img = b_ if t >= T else a_
            f = max(0, 1 - abs(t - T) / .09) * .85
            img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 250, 235)), f)
        elif kind == 'whip':
            cat = np.concatenate([np.array(a_), np.array(b_)], 1); off = int(ease(k) * VW)
            img = Image.fromarray(cat[:, off:off + VW]).filter(ImageFilter.GaussianBlur(14 * math.sin(math.pi * k)))
        elif kind == 'zoom':
            src = a_ if k < .5 else b_; s2 = 1 + .5 * (k * 2) ** 2 if k < .5 else 1 + .5 * ((1 - k) * 2) ** 2
            w2, h2 = int(VW / s2), int(VH / s2)
            img = src.crop(((VW - w2) // 2, (VH - h2) // 2, (VW + w2) // 2, (VH + h2) // 2)).resize((VW, VH), Image.BILINEAR)
            img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 255, 255)), .55 * math.sin(math.pi * k))
        break
    for tc in CUTS:                                                  # destello en los cortes duros dentro de una escena
        if 0 <= t - tc < .09: img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 250, 235)), .55 * (1 - (t - tc) / .09))
    if t > TOTAL - LOOP_D:
        k = (t - (TOTAL - LOOP_D)) / LOOP_D
        m = (BAYF < ease(k * 1.08))[..., None]                     # el último cuadro es idéntico al siguiente (el primero)
        img = Image.fromarray(np.where(m, np.array(first_virtual(t)), np.array(img)))
    return overlay(img, t)


# ---------------------------------------------------------------- audio
def synth_audio():
    N = int(TOTAL * SR)
    rng = np.random.default_rng(7)
    L = np.zeros((N, 2), np.float32)
    def add(sig, t0, g=1.0, pan=0.0):
        i0 = int(t0 * SR)
        if i0 >= N or i0 + len(sig) <= 0: return
        a = max(0, -i0); sig = sig[a:]; i0 = max(0, i0)
        n = min(len(sig), N - i0)
        L[i0:i0 + n, 0] += sig[:n] * g * (1 - max(0, pan)); L[i0:i0 + n, 1] += sig[:n] * g * (1 + min(0, pan))
    tt = lambda d: np.arange(int(d * SR)) / SR
    def noise(d, lp=None):
        n = rng.standard_normal(int(d * SR)).astype(np.float32)
        if lp:
            k = max(1, int(SR / lp / 2)); y = np.convolve(n, np.ones(k) / k, 'same')
            return y.astype(np.float32) * math.sqrt(k) * .6
        return n
    def bed(t0, t1, g, lp, lfo=0.15):
        d = t1 - t0
        if d <= 0: return
        n = noise(d, lp); e = (.7 + .3 * np.sin(2 * np.pi * lfo * tt(d))).astype(np.float32)
        fade = np.minimum(1, np.minimum(tt(d), d - tt(d)) / .4).astype(np.float32)
        add(n * e * fade, t0, g)
    s = {x['n']: x for x in SCENES}
    g = lambda n: s[n]
    dur = lambda n: g(n)['t1'] - g(n)['t0']
    sc_ = lambda n: g(n)['t0']
    bed(0, sc_(CFG['turn']), .04, 2800, .2)
    bed(sc_(CFG['turn']) - .1, sc_(CFG['late']), .045, 1800, .15)
    bed(sc_(CFG['late']) - .1, TOTAL, .05, 3000, .15)
    for sc in SCENES[1:]:
        d_ = .4; env = np.sin(np.pi * np.clip(tt(d_) / d_, 0, 1)) ** 2
        add(noise(d_, 1800) * env * .3, sc['t0'] - .2, .5)
    def chime(t0, notes, gain=.35):
        for k_, f in enumerate(notes):
            add((np.sin(2 * np.pi * f * tt(1.2)) + .4 * np.sin(2 * np.pi * 2 * f * tt(1.2))) * np.exp(-tt(1.2) * 4) * .5, t0 + k_ * .1, gain)
    G = sc_(CFG['turn']) + .15                                                      # "¿Y el conejo?": el giro
    SIL = .45
    rd = min(1.2, dur(CFG['pre']) - .3)
    add(noise(rd, 3000) * (tt(rd) / rd) ** 2.2 * .5, G - rd - SIL, .6)
    boom = np.sin(2 * np.pi * (55 * np.exp(-tt(1.8) * 1.2) + 28) * tt(1.8)) * np.exp(-tt(1.8) * 2.2)
    add(boom * .6, G, 1.0); add(noise(1.2, 6000) * np.exp(-tt(1.2) * 4) * .3, G, .6)
    chime(G + .1, [784, 988, 1175, 1568, 1976], .4)
    chime(END_T0 + .1, [988, 1319, 1568], .3)                                # aparece la tarjeta final
    chime(g('cierre')['t0'] + .1, [523, 659, 784, 1047], .35)
    pad = sum(np.sin(2 * np.pi * f * tt(dur('cierre'))) for f in (261.6, 329.6, 392.0, 523.3)) * .06
    add(pad * np.minimum(1, tt(dur('cierre')) / 1.5) * np.minimum(1, (dur('cierre') - tt(dur('cierre'))) / 1.0), g('cierre')['t0'], .5)
    d = .5; env = np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2
    add(noise(d, 1800) * env * .3, TOTAL - LOOP_D - .1, .5)
    for a, c_, l1, l2, yy in HOOK_T:                               # blip de cada gancho de texto
        ft_ = tt(.16); add(np.sign(np.sin(2 * np.pi * (700 + 900 * ft_ / .16) * ft_)) * np.exp(-ft_ * 14) * .22, a, .6)
    for tc in CUTS: add(noise(.14, 4000) * np.exp(-tt(.14) * 30) * .5, tc, .6)
    for bi, kd in enumerate(TKIND):
        T_ = SCENES[bi + 1]['t0']
        if kd == 'flash': add(noise(.2, 5000) * np.exp(-tt(.2) * 16) * .55, T_ - .02, .6)
        if kd == 'whip': add(noise(.3, 1500) * np.sin(np.pi * np.clip(tt(.3) / .3, 0, 1)) * .6, T_ - .15, .6)
    sfx = L.copy()
    # ---- música: "Every Living Breathing Moment" (piano), al volumen único de la serie (rms medido sobre el tramo que suena)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{ROOT}/audio/' + os.environ.get('MUSIC', 'every_moment') + '.m4a', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    song = np.frombuffer(raw, np.float32).reshape(-1, 2)
    S0, XF = 4.0, 1.8
    seg = song[int(S0 * SR):int(S0 * SR) + N].copy()
    sf = float(os.environ.get('MUS_RMS', .105)) / (np.sqrt((seg ** 2).mean()) + 1e-9); seg *= sf
    pre = song[int((S0 - XF) * SR):int(S0 * SR)].copy() * sf
    v = np.arange(len(seg)) / SR
    dip = np.where((v > G - SIL - .05) & (v < G - .012), np.clip(1 - (v - (G - SIL - .05)) / .12, 0, 1), 1.0)
    dip = np.where(v >= G - .012, 1.0, dip)
    swell = np.clip(.95 + .15 * np.clip((v - (G - 3)) / 4, 0, 1), .95, 1.1)
    seg *= (dip * swell)[:, None]
    nx = int(XF * SR); w_ = np.linspace(0, np.pi / 2, nx)[:, None]
    n = min(len(seg), N); m = np.zeros((N, 2), np.float32); m[:n] = seg[:n]
    m[N - nx:N] = m[N - nx:N] * np.cos(w_) + pre[:nx] * np.sin(w_)
    T0 = 0.0
    print(f'canción desde {T0:.2f}s, golpe en G={G:.2f}s', file=sys.stderr)
    voice = None
    if narr:
        vv = subprocess.run(['ffmpeg', '-v', 'error', '-i', narr, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        vv = np.frombuffer(vv, np.float32).reshape(-1, 2)
        voice = np.zeros((N, 2), np.float32); n = min(N, len(vv)); voice[:n] = vv[:n]
        env = np.sqrt(np.convolve(voice[:, 0] ** 2, np.ones(int(.08 * SR)) / int(.08 * SR), 'same'))
        env = np.convolve(env, np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
        gate = np.clip(env / (env.max() * .12 + 1e-9), 0, 1)
        m *= (1 - .4 * gate)[:, None]
        voice *= .14 / (np.sqrt((voice[voice[:, 0] ** 2 > 1e-4] ** 2).mean()) + 1e-9)   # voz al frente (rms hablado ≈ -17 dB)
    mix = m + sfx * .8
    if voice is not None: mix = mix + voice
    mix = np.tanh(mix * 1.15) / np.tanh(1.15) * .92        # limitador suave
    pk = np.abs(mix).max()
    mix = mix / pk * .92 if pk > .92 else mix
    out = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(f'{ROOT}/audio/mezcla_{STORY}.wav', 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())
    return G, T0


if __name__ == '__main__':
    dur = TOTAL
    args = [x for i, x in enumerate(sys.argv[1:]) if x != '--cta' and not (i > 0 and sys.argv[i] == '--cta')]   # --cta yt|tt se puede poner en cualquier posición
    out_name = f'TU_CONFIA_{STORY}_SHORT_Vertical_' + PLAT + ('' if narr else '_PREVIEW_sin_voz') + '.mp4'
    if args and args[0] == '--still':
        t = float(args[1]); fr = frame(int(t * FPS)); fr.save(f'{ROOT}/out/still_{t:.1f}.png'); sys.exit()
    if args and args[0] == '--timing':
        print(json.dumps({'total': TOTAL, 'scenes': [(s['n'], round(s['t0'], 2), round(s['t1'], 2)) for s in SCENES]}, indent=1)); sys.exit()
    G, drop = synth_audio()
    print('drop de la canción en', round(drop, 2), 's -> colocado en vídeo', round(G, 2), 's', file=sys.stderr)
    nf = int(TOTAL * FPS)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                            '-i', f'{ROOT}/audio/mezcla_{STORY}.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-tune', 'animation', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', f'{ROOT}/out/{out_name}'], stdin=subprocess.PIPE)
    for fi in range(nf):
        enc.stdin.write(frame(fi).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', nf, file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print('OK', out_name)

import os
os.environ['TC_LAND'] = '1'          # mundo apaisado 320x180 (x6 = 1920x1080) para YouTube
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
import scenes10 as S10
from cta import draw_cta
from lib import WW, WH, BAY, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, VW, VH = 30, 1920, 1080
LOOP_D = 0.9      # disolvencia final hacia el primer fotograma (bucle)
SR = 44100
SC = json.load(open(f'{ROOT}/script_hawking.json'))
LINES = SC['lines']
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- tiempos
narr = next(iter(glob.glob(f'{ROOT}/audio/narracion_hawking.*')), None)


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


FA = f'{ROOT}/audio/alineacion_hawking.json'
LW = {}                                      # palabras con tiempos exactos (alineación forzada de ElevenLabs)
if narr and os.path.exists(FA):
    ws = [w for w in json.load(open(FA))['words'] if w['text'].strip()]
    k_ = 0
    for l in LINES:
        n_ = len(l['tts'].split()); LW[l['id']] = ws[k_:k_ + n_]; k_ += n_
    assert k_ == len(ws), (k_, len(ws))
    st = [LW[l['id']][0]['start'] for l in LINES]; en = [LW[l['id']][-1]['end'] for l in LINES]
    TOTAL = round((en[-1] + .45 + LOOP_D) * FPS) / FPS          # nº entero de fotogramas: el bucle encaja al cuadro
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
PS = S2.portrait_scene
SCENES = [
    dict(n='sky', a='L1', b='L1', fn=lambda t, u: S10.sky(t, u), cam=[(0, 160, 100, 1.25), (0.5, 160, 100, 1.25), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='oxford', a='L2', b='L2', fn=lambda t, u: S10.oxford(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='cam', a='L4', b='L4', fn=lambda t, u: S10.cam(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='fall', a='L5', b='L5', fn=lambda t, u: S10.fall(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='doctor', a='L6', b='L6', fn=lambda t, u: S10.doctor(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='portS', a='L8', b='L8', fn=lambda t, u: S10.portrait_land(t, 'hawking_y', 'sad', (0, 1), 'cold'), cam=[(0, 160, 90, 1.0), (1, 160, 84, 1.12)]),
    dict(n='love', a='L10', b='L10', fn=lambda t, u: S10.love(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='lab', a='L11', b='L11', fn=lambda t, u: S10.lab(t, u), cam=[(0, 160, 90, 1.0), (0.36, 160, 90, 1.0), (0.3601, 160, 90, 1.0), (0.56, 160, 90, 1.0), (0.5601, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='hole', a='L15', b='L15', fn=lambda t, u: S10.hole(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='royal', a='L17', b='L17', fn=lambda t, u: S10.royal(t, u), cam=[(0, 160, 90, 1.0), (0.42, 160, 90, 1.0), (0.4201, 160, 90, 1.0), (0.72, 160, 90, 1.0), (0.7201, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='hosp', a='L19', b='L19', fn=lambda t, u: S10.hosp(t, u), cam=[(0, 160, 90, 1.0), (0.3, 160, 90, 1.0), (0.3001, 160, 90, 1.0), (0.56, 160, 90, 1.0), (0.5601, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='voice', a='L21', b='L21', fn=lambda t, u: S10.voice(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='books', a='L23', b='L23', fn=lambda t, u: S10.books(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='years', a='L25', b='L25', fn=lambda t, u: S10.years(t, u), cam=[(0, 160, 90, 1.0), (0.55, 160, 90, 1.0), (0.5501, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='portW', a='L27', b='L27', fn=lambda t, u: S10.portrait_land(t, 'hawking', 'warm', (0, 0), 'warm'), cam=[(0, 160, 90, 1.0), (1, 160, 84, 1.12)]),
    dict(n='starry', a='L28', b='L28', fn=lambda t, u: S10.starry(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='final', a='L30', b='L30', fn=lambda t, u: S10.final(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
]
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
DROP_T = next(x['t0'] for x in SCENES if x['n'] == 'years') + .02


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
    sc = max(6, int(round(6 * z))); cx += sh_ / 6; cy += sh_ / 6
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
fb = F('Black', 44)
w1 = bd.textlength('TU CONF', font=fb); w2 = bd.textlength('.IA', font=fb)
bx = 72
bd.text((bx + 3, 63), 'TU CONF', font=fb, fill=(0, 0, 0, 160)); bd.text((bx, 60), 'TU CONF', font=fb, fill=WHITE)
bd.rounded_rectangle([bx + w1 - 2, 58, bx + w1 + w2 + 10, 118], radius=8, fill=PURPLE)
bd.text((bx + w1 + 4, 60), '.IA', font=fb, fill=WHITE)
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
    size = 84
    ft = FL(size)
    d = ImageDraw.Draw(img)
    txt = ' '.join(w for w, _ in g).upper()
    GAP = lambda: int(size * .24)
    wid = lambda: d.textlength(txt.replace(' ', ''), font=ft) + GAP() * (len(g) - 1)
    while wid() > 1500 and size > 48: size -= 4; ft = FL(size)
    pop = min(1, (t - a) / .09)
    sc = .86 + .14 * (1 - (1 - pop) ** 2)
    layer = Image.new('RGBA', (VW, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    total = wid()
    SUBCX = 960; x = (2 * SUBCX - total) / 2; y = 50
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
    ysub = 860
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


HOOKS = [('sky', .15, 2.6, '¡LE DIERON', '2 AÑOS DE VIDA!', 330), ('hosp', 1.4, 4.2, '¡SE QUEDÓ', 'SIN VOZ!', 330), ('books', .3, 3.0, '¡10 MILLONES', 'DE LIBROS!', 330), ('years', 6.7, 9.6, '¡VIVIÓ 55', 'AÑOS MÁS!', 250)]
SC_ = {s['n']: s for s in SCENES}
HOOK_T = [(SC_[n]['t0'] + a, SC_[n]['t0'] + c_, l1, l2, yy) for n, a, c_, l1, l2, yy in HOOKS]
PLAT = (sys.argv[sys.argv.index('--cta') + 1] if '--cta' in sys.argv else 'yt')          # yt = SUSCRÍBETE, tt/ig = SÍGUEME
CTA_T0 = en[-1] - 2.6
SC_ = {s['n']: s for s in SCENES}
HOOK_T = [(SC_[n]['t0'] + a, SC_[n]['t0'] + c_, l1, l2, yy) for n, a, c_, l1, l2, yy in HOOKS]


def draw_hooks(img, t):
    for a, c_, l1, l2, yy in HOOK_T:
        if not (a <= t < c_): continue
        k = min(1, (t - a) / .14); out = min(1, (c_ - t) / .15)
        sc = (.6 + .5 * k - .1 * k * k) if k < 1 else 1.0
        d = ImageDraw.Draw(img); ft = FL(132 if max(len(l1), len(l2)) < 13 else (116 if max(len(l1), len(l2)) < 15 else 100))
        w = max(d.textlength(l1, font=ft), d.textlength(l2, font=ft))
        lay = Image.new('RGBA', (1700, 340), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for dx, dy, col in ((6, 6, (230, 40, 110)), (0, 0, None)):
            for n_, ln in enumerate((l1, l2)):
                x = (1700 - ld.textlength(ln, font=ft)) / 2 + dx; y = 6 + n_ * 150 + dy
                ld.text((x, y), ln, font=ft, fill=col or (YEL if n_ == 0 else WHITE), stroke_width=8, stroke_fill=DARK if col is None else col)
        lay = lay.resize((int(1700 * sc), int(340 * sc)), Image.BILINEAR)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
        img.alpha_composite(lay, (960 - lay.width // 2 + int(math.sin(t * 50) * 3 * (1 - k)), yy - lay.height // 2))


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
    draw_cta(img, t, CTA_T0, TOTAL, PLAT, LOOP_D, ytop=36, cx=1500, scale=1.35)
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
    bed(0, sc_('oxford'), .045, 3200, .25)                                  # noche abierta
    bed(sc_('oxford') - .1, sc_('doctor'), .035, 1800, .2)                  # campus
    bed(sc_('doctor') - .1, sc_('love'), .03, 400, .12)                     # consulta / silencio tenso
    bed(sc_('love') - .1, sc_('lab'), .05, 2600, .3)                        # jardín
    bed(sc_('lab') - .1, sc_('hole'), .03, 700, .15)
    bed(sc_('hole') - .1, sc_('royal'), .06, 500, .08)                      # el cosmos: zumbido grave
    bed(sc_('royal') - .1, sc_('hosp'), .07, 2200, .5)                      # sala con aplausos
    bed(sc_('hosp') - .1, sc_('voice'), .03, 600, .1)                       # hospital
    bed(sc_('voice') - .1, sc_('books'), .03, 900, .2)
    bed(sc_('books') - .1, sc_('years'), .09, 2200, .6)                     # librería llena
    bed(sc_('starry') - .1, TOTAL, .05, 3000, .15)
    for sc in SCENES[1:]:
        d_ = .4; env = np.sin(np.pi * np.clip(tt(d_) / d_, 0, 1)) ** 2
        add(noise(d_, 1800) * env * .3, sc['t0'] - .2, .5)
    t_ = sc_('doctor')                                                      # reloj del consultorio
    while t_ < g('portS')['t0']:
        add(noise(.03, 3000) * np.exp(-tt(.03) * 120) * .7, t_, .4); t_ += 1.0
    t_ = sc_('hosp') + .3                                                   # pitidos del monitor cardíaco
    while t_ < sc_('voice') - .2:
        add(np.sin(2 * np.pi * 1040 * tt(.09)) * np.exp(-tt(.09) * 9) * .4, t_, .3); t_ += .85
    t_ = sc_('voice') + .5                                                  # voz sintetizada: pitidos al teclear
    while t_ < sc_('books') - .3:
        add(np.sign(np.sin(2 * np.pi * rng.choice([420, 520, 640]) * tt(.07))) * np.exp(-tt(.07) * 25) * .25, t_, .35); t_ += rng.choice([.16, .22, .3])
    t_ = sc_('fall') + .4                                                   # pasos y tropiezo
    while t_ < sc_('fall') + dur('fall') * .5:
        add(noise(.05, 700) * np.exp(-tt(.05) * 60) * .8, t_, .5); t_ += .45
    add(np.sin(2 * np.pi * 55 * tt(.5)) * np.exp(-tt(.5) * 10) * .9, sc_('fall') + dur('fall') * .5, .8)
    chime(sc_('love') + .1, [784, 988, 1175], .35) if False else None
    def chime(t0, notes, gain=.35):
        for k_, f in enumerate(notes):
            add((np.sin(2 * np.pi * f * tt(1.2)) + .4 * np.sin(2 * np.pi * 2 * f * tt(1.2))) * np.exp(-tt(1.2) * 4) * .5, t0 + k_ * .1, gain)
    chime(sc_('oxford') + .2, [523, 659, 784], .3); chime(sc_('love') + .2, [784, 988, 1175, 1568], .35)
    chime(sc_('hole') + .2, [392, 587, 880], .3); chime(sc_('hosp') + dur('hosp') * .56, [659, 880, 1319], .35)
    G = sc_('years') + dur('years') * .55                                   # "Él vivió cincuenta y cinco más": el giro
    SIL = .45
    rd = min(1.2, dur('years') * .5)
    add(noise(rd, 3000) * (tt(rd) / rd) ** 2.2 * .5, G - rd - SIL, .6)
    boom = np.sin(2 * np.pi * (55 * np.exp(-tt(1.8) * 1.2) + 28) * tt(1.8)) * np.exp(-tt(1.8) * 2.2)
    add(boom * .6, G, 1.0); add(noise(1.2, 6000) * np.exp(-tt(1.2) * 4) * .3, G, .6)
    chime(G + .1, [784, 988, 1175, 1568, 1976], .4)
    chime(sc_('starry') + .1, [523, 659, 784, 1047], .35)
    chime(CTA_T0 + .1, [988, 1319], .3)                                      # aparece el botón
    chime(g('final')['t0'] + .1, [523, 659, 784, 1047], .35)
    pad = sum(np.sin(2 * np.pi * f * tt(dur('final'))) for f in (261.6, 329.6, 392.0, 523.3)) * .06       # acorde cálido del amanecer
    add(pad * np.minimum(1, tt(dur('final')) / 1.5) * np.minimum(1, (dur('final') - tt(dur('final'))) / 1.0), g('final')['t0'], .5)
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
    # ---- música: "Mrs Magic" (Strawberry Guy): soñadora, crece hacia el final
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{ROOT}/audio/mrs_magic.m4a', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    song = np.frombuffer(raw, np.float32).reshape(-1, 2)
    hw = int(.01 * SR); e0 = np.abs(song[:int(8 * SR), 0])
    T0 = next(i for i in range(0, len(e0) - hw, hw) if e0[i:i + hw].max() > .02) / SR - .02
    T0 = max(0, T0)
    S0 = 4.0                                                           # el vídeo arranca dentro de la canción: hay música "anterior" para empalmar el final con el principio
    XF = 1.8                                                           # segundos de empalme del final con el principio
    seg = song[int(S0 * SR):int(S0 * SR) + N].copy()
    pre = song[int((S0 - XF) * SR):int(S0 * SR)].copy()
    gscale = .12 / (np.sqrt((seg[:int(20 * SR)] ** 2).mean()) + 1e-9)  # música bien presente
    seg *= gscale; pre *= gscale * .78
    v = np.arange(len(seg)) / SR
    dip = np.where((v > G - SIL - .05) & (v < G - .012), np.clip(1 - (v - (G - SIL - .05)) / .12, 0, 1), 1.0)   # el piano se apaga ...
    dip = np.where(v >= G - .012, 1.0, dip)                                                                   # ... y vuelve con el golpe
    swell = np.clip(.78 + .45 * np.clip((v - (G - 4)) / 4, 0, 1), .78, 1.23)                    # el piano crece desde el giro
    seg *= (dip * swell)[:, None]
    nx = int(XF * SR); w_ = np.linspace(0, np.pi / 2, nx)[:, None]            # empalme de potencia constante: el final entra en la música del principio
    seg[N - nx:N] = seg[N - nx:N] * np.cos(w_) + pre[:nx] * np.sin(w_)
    m = np.zeros((N, 2), np.float32); n = min(len(seg), N); m[:n] = seg[:n]
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
    with wave.open(f'{ROOT}/audio/mezcla.wav', 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())
    return G, T0


if __name__ == '__main__':
    dur = TOTAL
    args = [x for i, x in enumerate(sys.argv[1:]) if x != '--cta' and not (i > 0 and sys.argv[i] == '--cta')]   # --cta yt|tt se puede poner en cualquier posición
    out_name = 'TU_CONFIA_Stephen_Hawking_Dos_Anios_De_Vida_HORIZONTAL_' + PLAT + ('' if narr else '_PREVIEW_sin_voz') + '.mp4'
    if args and args[0] == '--still':
        t = float(args[1]); fr = frame(int(t * FPS)); fr.save(f'{ROOT}/out/still_{t:.1f}.png'); sys.exit()
    if args and args[0] == '--timing':
        print(json.dumps({'total': TOTAL, 'scenes': [(s['n'], round(s['t0'], 2), round(s['t1'], 2)) for s in SCENES]}, indent=1)); sys.exit()
    G, drop = synth_audio()
    print('drop de la canción en', round(drop, 2), 's -> colocado en vídeo', round(G, 2), 's', file=sys.stderr)
    nf = int(TOTAL * FPS)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                            '-i', f'{ROOT}/audio/mezcla.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-tune', 'animation', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', f'{ROOT}/out/{out_name}'], stdin=subprocess.PIPE)
    for fi in range(nf):
        enc.stdin.write(frame(fi).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', nf, file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print('OK', out_name)

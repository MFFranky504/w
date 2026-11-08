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
import scenes11 as S11
from cta import draw_cta
from lib import WW, WH, BAY, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, VW, VH = 30, 1920, 1080
LOOP_D = 0.9      # disolvencia final hacia el primer fotograma (bucle)
SR = 44100
SC = json.load(open(f'{ROOT}/script_disney.json'))
LINES = SC['lines']
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- tiempos
narr = next(iter(glob.glob(f'{ROOT}/audio/narracion_disney.*')), None)


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


FA = f'{ROOT}/audio/alineacion_disney.json'
LW = {}                                      # palabras con tiempos exactos (alineación forzada de ElevenLabs)
if narr and os.path.exists(FA):
    ws = [w for w in json.load(open(FA))['words'] if w['text'].strip()]
    k_ = 0
    for l in LINES:
        n_ = len(l['tts'].split()); LW[l['id']] = ws[k_:k_ + n_]; k_ += n_
    assert k_ == len(ws), (k_, len(ws))
    st = [LW[l['id']][0]['start'] for l in LINES]; en = [LW[l['id']][-1]['end'] for l in LINES]
    TOTAL = round((en[-1] + 6.5 + LOOP_D) * FPS) / FPS          # nº entero de fotogramas: el bucle encaja al cuadro
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
SCENES = [
    dict(n='office', a=lid('Walt Disney podía'), b=lid('Walt Disney podía'), fn=lambda t, u: S11.office(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='nyork', a=lid('Nueva York, 1928'), b=lid('Nueva York, 1928'), fn=lambda t, u: S11.nyork(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='worse', a=lid('Pero el distribuidor'), b=lid('Pero el distribuidor'), fn=lambda t, u: S11.worse(t, u), cam=[(0, 160, 90, 1.0), (0.3, 160, 90, 1.0), (0.3001, 160, 90, 1.0), (0.62, 160, 90, 1.0), (0.6201, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='dijo_no', a=lid('Podía quedarse'), b=lid('Podía quedarse'), fn=lambda t, u: S11.dijo_no(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.67, 160, 90, 1.0), (0.6701, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='kansas', a=lid('Y no era su primer'), b=lid('Y no era su primer'), fn=lambda t, u: S11.kansas(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='bros', a=lid('Pero esta vez'), b=lid('Pero esta vez'), fn=lambda t, u: S11.bros(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='amigo', a=lid('Y tenía a uno'), b=lid('Y tenía a uno'), fn=lambda t, u: S11.amigo(t, u), cam=[(0, 160, 90, 1.0), (0.45, 160, 90, 1.0), (0.4501, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='rechazo', a=lid('El primer corto'), b=lid('El primer corto'), fn=lambda t, u: S11.rechazo(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='sonido', a=lid('Entonces apostó'), b=lid('Entonces apostó'), fn=lambda t, u: S11.sonido(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='estreno', a=lid('El 18 de noviembre'), b=lid('El 18 de noviembre'), fn=lambda t, u: S11.estreno(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='amigo_va', a=lid('Pero en 1930'), b=lid('Pero en 1930'), fn=lambda t, u: S11.amigo_va(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='derrumbe', a=lid('Al año siguiente'), b=lid('Al año siguiente'), fn=lambda t, u: S11.derrumbe(t, u), cam=[(0, 160, 90, 1.0), (0.34, 160, 90, 1.0), (0.3401, 160, 90, 1.0), (0.6, 160, 90, 1.0), (0.6001, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='huelga', a=lid('Y no, Walt'), b=lid('Y no, Walt'), fn=lambda t, u: S11.huelga(t, u), cam=[(0, 160, 90, 1.0), (0.5, 160, 90, 1.0), (0.5001, 160, 90, 1.0), (1, 160, 90, 1.0)]),
    dict(n='conejo', a=lid('¿Y el conejo'), b=lid('¿Y el conejo'), fn=lambda t, u: S11.conejo(t, u), cam=[(0, 160, 90, 1.0), (0.35, 160, 90, 1.0), (0.3501, 160, 90, 1.0), (0.52, 160, 90, 1.0), (0.5201, 160, 90, 1.2), (0.7, 160, 90, 1.2), (0.7001, 160, 112, 1.5), (1, 160, 112, 1.5)]),
    dict(n='cierre', a=lid('Perdió su'), b=lid('Perdió su'), fn=lambda t, u: S11.cierre(t, u), cam=[(0, 160, 90, 1.0), (0.22, 160, 90, 1.0), (0.2201, 160, 100, 1.3), (0.55, 160, 100, 1.3), (0.5501, 160, 112, 1.5), (1, 160, 112, 1.5)]),
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
DROP_T = next(x['t0'] for x in SCENES if x['n'] == 'conejo') + .02


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
bd.rounded_rectangle([bx - 14, 46, bx + w1 + w2 + 24, 130], radius=14, fill=(14, 10, 26, 150))
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
    ld.rounded_rectangle([(2 * 960 - total) / 2 - 34, 14, (2 * 960 + total) / 2 + 34, size + 82], radius=22, fill=(10, 6, 22, 105))
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


HOOKS = [('office', .15, 3.0, '¡PODÍA ACEPTAR', 'Y SE NEGÓ!', 440, 780),
         ('sonido', .3, 3.2, '¡DIBUJOS CON', 'SONIDO!', 330), ('conejo', 14.0, 17.0, '¡NUNCA LO', 'VIO VOLVER!', 520)]
SC_ = {s['n']: s for s in SCENES}
HOOK_T = [(SC_[n]['t0'] + a, SC_[n]['t0'] + c_, l1, l2, yy, (rest[0] if rest else 960)) for n, a, c_, l1, l2, yy, *rest in HOOKS]
PLAT = (sys.argv[sys.argv.index('--cta') + 1] if '--cta' in sys.argv else 'yt')          # yt = SUSCRÍBETE, tt/ig = SÍGUEME
CTA_T0 = en[-1] - .2
SC_ = {s['n']: s for s in SCENES}


CHAPS = [('office', 'CAPÍTULO 1 · DIJO QUE NO'), ('bros', 'CAPÍTULO 2 · LO QUE LE QUEDÓ'), ('rechazo', 'CAPÍTULO 3 · OTRO RECHAZO'), ('amigo_va', 'CAPÍTULO 4 · EL AMIGO QUE SE FUE'),
         ('huelga', 'CAPÍTULO 5 · NO FUE PERFECTO'), ('conejo', 'CAPÍTULO 6 · EL CONEJO VUELVE'), ('cierre', 'CAPÍTULO 7 · LO QUE TE QUEDA')]
CHAP_T = [(SC_[n]['t0'] + .25, label) for n, label in CHAPS]


def draw_chapter(img, t):
    for a, label in CHAP_T:
        if not (a <= t < a + 3.4): continue
        k = min(1, (t - a) / .35); out = min(1, (a + 3.4 - t) / .3)
        ft = FL(26); d = ImageDraw.Draw(img)
        w = int(d.textlength(label, font=ft)) + 56
        lay = Image.new('RGBA', (w + 20, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, w, 50], radius=8, fill=(14, 10, 26, 205)); ld.rounded_rectangle([0, 0, 10, 50], radius=5, fill=PURPLE)
        ld.text((28, 25), label, font=ft, fill=WHITE, anchor='lm')
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
        img.alpha_composite(lay, (72 - int((1 - k) * 220), 140))


def draw_hooks(img, t):
    for a, c_, l1, l2, yy, hx in HOOK_T:
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
        img.alpha_composite(lay, (hx - lay.width // 2 + int(math.sin(t * 50) * 3 * (1 - k)), yy - lay.height // 2))


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
    draw_chapter(img, t)
    draw_hooks(img, t)
    draw_cta(img, t, CTA_T0, TOTAL, PLAT, LOOP_D, ytop=36, cx=1500, scale=1.35, show=6.4)
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
    bed(0, sc_('kansas'), .035, 1800, .2)                                   # oficina / ciudad
    bed(sc_('kansas') - .1, sc_('amigo'), .03, 900, .15)
    bed(sc_('amigo') - .1, sc_('estreno'), .03, 1500, .2)
    bed(sc_('estreno') - .1, sc_('amigo_va'), .09, 2200, .6)                # público riendo
    bed(sc_('amigo_va') - .1, sc_('huelga'), .03, 500, .1)
    bed(sc_('huelga') - .1, sc_('conejo'), .04, 1200, .3)
    bed(sc_('conejo') - .1, sc_('cierre'), .04, 2500, .2)
    bed(sc_('cierre') - .1, TOTAL, .05, 3000, .15)
    for sc in SCENES[1:]:
        d_ = .4; env = np.sin(np.pi * np.clip(tt(d_) / d_, 0, 1)) ** 2
        add(noise(d_, 1800) * env * .3, sc['t0'] - .2, .5)
    def chime(t0, notes, gain=.35):
        for k_, f in enumerate(notes):
            add((np.sin(2 * np.pi * f * tt(1.2)) + .4 * np.sin(2 * np.pi * 2 * f * tt(1.2))) * np.exp(-tt(1.2) * 4) * .5, t0 + k_ * .1, gain)
    add(np.sin(2 * np.pi * 60 * tt(.4)) * np.exp(-tt(.4) * 12) * .8, sc_('office') + dur('office') * .66, .7)       # puerta que se cierra
    t_ = sc_('worse')
    while t_ < sc_('worse') + dur('worse') * .3:
        add(np.sin(2 * np.pi * 1500 * tt(.05)) * np.exp(-tt(.05) * 40) * .4, t_, .3); t_ += .18                      # monedas
    add(np.sin(2 * np.pi * 60 * tt(.5)) * np.exp(-tt(.5) * 9) * .9, sc_('dijo_no') + .2, .8)                         # golpe del "no"
    t_ = sc_('amigo') + .4
    while t_ < sc_('amigo') + dur('amigo'):
        add(noise(.09, 5000) * np.sin(np.pi * np.clip(tt(.09) / .09, 0, 1)) * .5, t_, .3); t_ += .13                 # lápiz
    t_ = sc_('estreno') + .3
    while t_ < sc_('amigo_va') - .3:
        add(noise(.12, 3000) * np.sin(np.pi * np.clip(tt(.12) / .12, 0, 1)) * .6, t_, .35); t_ += rng.choice([.22, .3, .4])   # risas
    add(np.sin(2 * np.pi * 70 * tt(.4)) * np.exp(-tt(.4) * 12) * .8, sc_('amigo_va') + dur('amigo_va') * .5, .7)     # puerta del amigo
    t_ = sc_('derrumbe') + .3
    while t_ < sc_('derrumbe') + dur('derrumbe') * .34:
        add(noise(.04, 2500) * np.exp(-tt(.04) * 60) * .7, t_, .35); t_ += .5                                        # papeles
    G = sc_('conejo') + .02                                                  # el pago del bucle: "¿Y el conejo...?"
    SIL = .45
    rd = min(1.2, dur('huelga') - .3)
    add(noise(rd, 3000) * (tt(rd) / rd) ** 2.2 * .5, G - rd - SIL, .6)
    boom = np.sin(2 * np.pi * (55 * np.exp(-tt(1.8) * 1.2) + 28) * tt(1.8)) * np.exp(-tt(1.8) * 2.2)
    add(boom * .6, G, 1.0); add(noise(1.2, 6000) * np.exp(-tt(1.2) * 4) * .3, G, .6)
    chime(G + .1, [784, 988, 1175, 1568, 1976], .4)
    chime(sc_('estreno') + .1, [523, 659, 784, 1047], .35)
    chime(sc_('cierre') + .1, [523, 659, 784, 1047], .35)
    chime(CTA_T0 + .1, [988, 1319], .3)
    chime(g('cierre')['t0'] + .1, [523, 659, 784, 1047], .35)
    pad = sum(np.sin(2 * np.pi * f * tt(dur('cierre'))) for f in (261.6, 329.6, 392.0, 523.3)) * .06       # acorde cálido del amanecer
    add(pad * np.minimum(1, tt(dur('cierre')) / 1.5) * np.minimum(1, (dur('cierre') - tt(dur('cierre'))) / 1.0), g('cierre')['t0'], .5)
    d = .5; env = np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2
    add(noise(d, 1800) * env * .3, TOTAL - LOOP_D - .1, .5)
    for a, c_, l1, l2, yy, hx in HOOK_T:                           # blip de cada gancho de texto
        ft_ = tt(.16); add(np.sign(np.sin(2 * np.pi * (700 + 900 * ft_ / .16) * ft_)) * np.exp(-ft_ * 14) * .22, a, .6)
    for tc in CUTS: add(noise(.14, 4000) * np.exp(-tt(.14) * 30) * .5, tc, .6)
    for bi, kd in enumerate(TKIND):
        T_ = SCENES[bi + 1]['t0']
        if kd == 'flash': add(noise(.2, 5000) * np.exp(-tt(.2) * 16) * .55, T_ - .02, .6)
        if kd == 'whip': add(noise(.3, 1500) * np.sin(np.pi * np.clip(tt(.3) / .3, 0, 1)) * .6, T_ - .15, .6)
    sfx = L.copy()
    # ---- música (video largo: solo piano, variada por secciones con "silencio suspensivo" entre ellas)
    def dec_(path):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        return np.frombuffer(raw, np.float32).reshape(-1, 2)
    TR_ = {k: dec_(f'{ROOT}/audio/{k}.m4a') for k in ('every_moment', 'heard_em_say', 'congratulations')}
    lvl = lambda x_, g_: x_ * (g_ / (np.sqrt((x_[:int(20 * SR)] ** 2).mean()) + 1e-9))
    MUS_RMS = .105                                                     # volumen único de la música (rms), igual en todas las secciones
    S0, XF = 4.0, 1.8                                                  # el video arranca dentro de la canción (4 s): hay música "anterior" para empalmar el final con el principio
    SECT = [('every_moment', S0, 0.0, sc_('kansas'), .12),             # 1. el trato y el "no": piano íntimo
            ('heard_em_say', 2.0, sc_('kansas'), sc_('amigo_va'), .10),  # 2. levantarse con Roy y Ub: más pulso
            ('every_moment', 66.0, sc_('amigo_va'), sc_('conejo'), .12), # 3. el amigo se va, la caída y la huelga
            ('congratulations', 0.0, sc_('conejo'), TOTAL, .12)]       # 4. el regreso del conejo y el cierre
    m = np.zeros((N, 2), np.float32); FD = .9
    for k_, (name_, off_, a_, b_, g_) in enumerate(SECT):
        i0, i1 = int(a_ * SR), min(N, int(b_ * SR)); n_ = i1 - i0
        seg_ = TR_[name_][int(off_ * SR):int(off_ * SR) + n_].copy()
        if len(seg_) < n_: seg_ = np.pad(seg_, ((0, n_ - len(seg_)), (0, 0)))
        sf_ = MUS_RMS / (np.sqrt((seg_ ** 2).mean()) + 1e-9); seg_ *= sf_          # mismo volumen en TODAS las secciones: se mide el tramo que realmente suena
        if k_ == 0: sf0_ = sf_
        print(f'música sección {k_ + 1} ({name_}): factor {sf_:.2f}', file=sys.stderr)
        v_ = np.arange(n_) / SR
        env_ = np.ones(n_, np.float32)
        if k_ > 0: env_ *= np.clip(v_ / FD, 0, 1)                      # entra con fundido
        if k_ < len(SECT) - 1: env_ *= np.clip(((n_ / SR) - v_) / FD, 0, 1)   # sale con fundido (silencio breve entre secciones)
        if k_ == len(SECT) - 1:
            vt_ = v_ + a_
            env_ *= np.where((vt_ > G - SIL - .05) & (vt_ < G - .012), np.clip(1 - (vt_ - (G - SIL - .05)) / .12, 0, 1), 1.0)   # el piano se apaga ...
            env_ = np.where(vt_ >= G - .012, np.maximum(env_, 1.0) * np.clip((vt_ - (G - .012)) / .012, 0, 1), env_)            # ... y vuelve con el golpe
            env_ *= np.clip(.95 + .15 * np.clip((vt_ - (G - 3)) / 4, 0, 1), .95, 1.1)                                          # crece hacia el final
        m[i0:i1] += seg_ * env_[:, None]
    pre = TR_['every_moment'][int((S0 - XF) * SR):int(S0 * SR)].copy() * sf0_
    nx = int(XF * SR); w_ = np.linspace(0, np.pi / 2, nx)[:, None]            # empalme de potencia constante: el final entra en la música del principio
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
    with wave.open(f'{ROOT}/audio/mezcla.wav', 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())
    return G, T0


if __name__ == '__main__':
    dur = TOTAL
    args = [x for i, x in enumerate(sys.argv[1:]) if x != '--cta' and not (i > 0 and sys.argv[i] == '--cta')]   # --cta yt|tt se puede poner en cualquier posición
    out_name = 'TU_CONFIA_Walt_Disney_Podia_Aceptar_Pero_Se_Nego_HORIZONTAL_' + PLAT + ('' if narr else '_PREVIEW_sin_voz') + '.mp4'
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

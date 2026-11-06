"""TU CONF.IA - montaje. Uso: python3 -I build.py [--preview N_segundos]
Si existe ../audio/narracion.(mp3|wav|m4a) los tiempos se adaptan a la voz real; si no, se estiman."""
import sys, os, json, re, math, subprocess, glob, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scenes as S
import scenes2 as S2
import scenes3 as S3
import scenes4 as S4
from lib import WW, WH, BAY, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, VW, VH = 30, 1080, 1920
LOOP_D = 0.9      # disolvencia final hacia el primer fotograma (bucle)
SR = 44100
SC = json.load(open(f'{ROOT}/script_stallone.json'))
LINES = SC['lines']
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- tiempos
narr = next(iter(glob.glob(f'{ROOT}/audio/narracion_stallone.*')), None)


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
    return starts, ends, last + 1.0 + LOOP_D


def estimate():
    t, starts, ends = 0.25, [], []
    for l in LINES:
        d = len(clean(l['t'])) / 16.5
        starts.append(t); ends.append(t + d); t += d + l['p']
    return starts, ends, t + 1.0 + LOOP_D


if narr:
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
    dict(n='liquor', a='L1', b='L1', fn=lambda t, u: S4.liquor(t, u), cam=[(0, 80, 190, 1.25), (1, 82, 198, 1.7)]),
    dict(n='script', a='L2', b='L2', fn=lambda t, u: S4.script_prop(t, u), cam=[(0, 80, 150, 1.1), (1, 70, 150, 1.5)]),
    dict(n='portS', a='L3a', b='L3a', fn=lambda t, u: PS(t, 'stallone', 'n', (0, 1), 'cold', tag='STALLONE'), cam=[(0, 80, 160, 1.3), (1, 80, 150, 1.6)]),
    dict(n='cinema', a='L3b', b='L3b', fn=lambda t, u: S4.cinema(t, u), cam=[(0, 80, 130, 1.0), (1, 60, 190, 1.4)]),
    dict(n='typing', a='L4', b='L4', fn=lambda t, u: S4.typing(t, u), cam=[(0, 80, 150, 1.05), (1, 80, 158, 1.55)]),
    dict(n='offer', a='L5', b='L5', fn=lambda t, u: S4.office(t, u, 'offer'), cam=[(0, 70, 168, 1.1), (1, 100, 176, 1.5)]),
    dict(n='no', a='L6', b='L6', fn=lambda t, u: S4.portrait_no(t, u), cam=[(0, 80, 160, 1.3), (1, 80, 152, 1.6)]),
    dict(n='slam', a='L7', b='L7', fn=lambda t, u: S4.office(t, u, 'slam'), cam=[(0, 66, 170, 1.25), (1, 84, 176, 1.5)]),
    dict(n='deal', a='L8', b='L8', fn=lambda t, u: S4.office(t, u, 'deal'), cam=[(0, 80, 176, 1.1), (1, 96, 174, 1.5)]),
    dict(n='oscar', a='L9', b='L9', fn=lambda t, u: S4.oscars(t, u), cam=[(0, 80, 196, 1.45), (1, 80, 150, 1.0)]),
    dict(n='reunion', a='L10', b='L10', fn=lambda t, u: S4.reunion(t, u), cam=[(0, 80, 210, 1.2), (1, 84, 214, 1.5)]),
    dict(n='sunset', a='L11', b='L11', fn=lambda t, u: S4.sunset(t, u), cam=[(0, 60, 220, 1.4), (1, 80, 170, 1.0)]),
    dict(n='type2', a='L12', b='L12', fn=lambda t, u: S4.typing(t, .99), cam=[(0, 80, 160, 1.5), (1, 80, 150, 1.05)]),
    dict(n='tu', a='L13', b='L13', fn=lambda t, u: S4.tu_script(t, u), cam=[(0, 80, 190, 1.4), (1, 80, 176, 1.1)]),
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
DROP_T = next(x['t0'] for x in SCENES if x['n'] == 'deal') + .02


def cam_at(kf, u):
    for (u0, *a), (u1, *b) in zip(kf, kf[1:]):
        if u0 <= u <= u1:
            k = ease((u - u0) / (u1 - u0) if u1 > u0 else 1)
            return [p + (q - p) * k for p, q in zip(a, b)]
    return list(kf[-1][1:])


def render_scene(i, t):
    s = SCENES[i]
    d = max(1e-3, s['t1'] - s['t0'])
    u = max(0, min(1, (t - s['t0']) / d))
    tl = max(0, t - s['t0'])
    img = s['fn'](tl, u)
    cx, cy, z = cam_at(s['cam'], u)
    for l in LINES:
        dt = t - LSTART[l['id']]
        if 0 <= dt < .35 and s['t0'] - .2 <= LSTART[l['id']] <= s['t1']: z *= 1 + .045 * math.exp(-dt / .09)
    sh_ = 0
    if 0 <= t - DROP_T < .4: sh_ = math.sin((t - DROP_T) * 90) * 9 * (1 - (t - DROP_T) / .4)
    if 1.05 <= t < 1.4: sh_ = math.sin((t - 1.05) * 80) * 7 * (1 - (t - 1.05) / .35)
    big = img.resize((WW * 8, WH * 8), Image.NEAREST); cx += sh_ / 8; cy += sh_ / 11
    cw, ch = VW / z, VH / z
    x0 = min(max(cx * 8 - cw / 2, 0), WW * 8 - cw); y0 = min(max(cy * 8 - ch / 2, 0), WH * 8 - ch)
    return big.resize((VW, VH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


# patrón de disolvencia ordenada (Bayer) a resolución final
BAYF = np.kron(np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (VH // 32 + 1, VW // 32 + 1)), np.ones((8, 8)))[:VH, :VW]

# ---------------------------------------------------------------- overlay
F = lambda w, s: ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{w}.otf', s)
YEL, WHITE, DARK = (255, 216, 74), (255, 255, 255), (14, 10, 26)
PURPLE = (139, 92, 246)      # logo TU CONF.IA
BRAND = Image.new('RGBA', (VW, VH), (0, 0, 0, 0))
bd = ImageDraw.Draw(BRAND)
fb = F('Black', 50)
w1 = bd.textlength('TU CONF', font=fb); w2 = bd.textlength('.IA', font=fb)
bx = (VW - (w1 + w2)) / 2
bd.text((bx + 3, 103), 'TU CONF', font=fb, fill=(0, 0, 0, 160)); bd.text((bx, 100), 'TU CONF', font=fb, fill=WHITE)
bd.rounded_rectangle([bx + w1 - 2, 98, bx + w1 + w2 + 10, 162], radius=8, fill=PURPLE)
bd.text((bx + w1 + 4, 100), '.IA', font=fb, fill=WHITE)
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
    for w, e in toks:
        if cur and (n + len(w) > 17 or len(cur) >= 3 or (cur[-1][0][-1] in '.?!…' )):
            groups.append(cur); cur, n = [], 0
        cur.append((w, e)); n += len(w) + 1
    if cur: groups.append(cur)
    tot = sum(len(' '.join(w for w, _ in g)) + 2 for g in groups)
    t0, t1 = LSTART[l['id']], LEND[l['id']]
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
    size = 96
    ft = F('Black', size)
    d = ImageDraw.Draw(img)
    txt = ' '.join(w for w, _ in g).upper()
    while d.textlength(txt, font=ft) > 940 and size > 56: size -= 4; ft = F('Black', size)
    pop = min(1, (t - a) / .09)
    sc = .86 + .14 * (1 - (1 - pop) ** 2)
    layer = Image.new('RGBA', (VW, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    total = ld.textlength(txt, font=ft)
    x = (VW - total) / 2; y = 50
    for w, e in g:
        w = w.upper()
        ld.text((x, y), w, font=ft, fill=YEL if e else WHITE, stroke_width=11, stroke_fill=DARK)
        x += ld.textlength(w + ' ', font=ft)
    for w, e in g: pass
    # relleno encima del trazo
    x = (VW - total) / 2
    for w, e in g:
        w = w.upper(); ld.text((x, y), w, font=ft, fill=YEL if e else WHITE); x += ld.textlength(w + ' ', font=ft)
    if sc < 1:
        layer = layer.resize((int(VW * sc), int(220 * sc)), Image.BILINEAR)
        ox, oy = (VW - layer.width) // 2, (220 - layer.height) // 2
    else: ox = oy = 0
    ysub = 1230
    img.alpha_composite(layer, (ox, ysub + oy))


CAPT = None
def draw_caps(img, t):
    s = SCENES[1]
    if s['t0'] + .3 < t < s['t1'] - .1:
        k = min(1, (t - s['t0'] - .3) / .4) * min(1, (s['t1'] - .1 - t) / .3)
        d = ImageDraw.Draw(img)
        a = int(255 * max(0, k))
        f1, f2 = F('ExtraBold', 44), F('Medium', 34)
        d.text((60, 250), 'HERMON, MAINE', font=f1, fill=(255, 255, 255, a), stroke_width=5, stroke_fill=(14, 10, 26, a))
        d.text((60, 306), 'principios de los años 70', font=f2, fill=(255, 216, 74, a), stroke_width=4, stroke_fill=(14, 10, 26, a))


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
    draw_sub(img, t)
    # fundido final
    out = img.convert('RGB')
    return out


_FIRST = []
def first_img():
    if not _FIRST: _FIRST.append(render_scene(0, 0.0))
    return _FIRST[0]


def frame(fi):
    t = fi / FPS
    idx = max(i for i, s in enumerate(SCENES) if s['t0'] <= t + 1e-6)
    img = render_scene(idx, t)
    # transición con la siguiente
    if idx + 1 < len(SCENES) and SCENES[idx + 1]['t0'] - t < TR / 2:
        a = 1 - (SCENES[idx + 1]['t0'] - t) / (TR / 2) * 0.0
        k = (t - (SCENES[idx + 1]['t0'] - TR / 2)) / TR
        nxt = render_scene(idx + 1, t)
        m = (BAYF < ease(k))[..., None]
        img = Image.fromarray(np.where(m, np.array(nxt), np.array(img)))
    elif idx > 0 and t - SCENES[idx]['t0'] < TR / 2:
        k = (t - (SCENES[idx]['t0'] - TR / 2)) / TR
        prv = render_scene(idx - 1, t)
        m = (BAYF < ease(k))[..., None]
        img = Image.fromarray(np.where(m, np.array(img), np.array(prv)))
    if t > TOTAL - LOOP_D:
        k = min(1.0, (t - (TOTAL - LOOP_D)) / (LOOP_D - 1.0 / FPS))
        m = (BAYF < ease(k))[..., None]
        img = Image.fromarray(np.where(m, np.array(first_img()), np.array(img)))
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
        if lp:  # paso bajo simple
            a = math.exp(-2 * math.pi * lp / SR); y = np.zeros_like(n)
            # IIR vectorizado vía cumsum aproximado
            from numpy.lib.stride_tricks import sliding_window_view
            k = max(1, int(SR / lp / 2)); y = np.convolve(n, np.ones(k) / k, 'same')
            return y.astype(np.float32) * math.sqrt(k) * .6
        return n
    # ambientes
    def bed(t0, t1, g, lp, lfo=0.15):
        d = t1 - t0
        if d <= 0: return
        n = noise(d, lp); e = (.7 + .3 * np.sin(2 * np.pi * lfo * tt(d))).astype(np.float32)
        fade = np.minimum(1, np.minimum(tt(d), d - tt(d)) / .4).astype(np.float32)
        add(n * e * fade, t0, g)
    s = {x['n']: x for x in SCENES}
    g = lambda n: s[n]
    bed(0, g('portS')['t0'] + .2, .07, 3000, .3)                                      # ciudad / lluvia suave
    bed(g('portS')['t0'] - .1, g('cinema')['t0'] + .2, .02, 400, .15)
    bed(g('cinema')['t0'] - .1, g('typing')['t0'] + .2, .08, 1600, .8)               # público del cine
    bed(g('typing')['t0'] - .1, g('offer')['t0'] + .2, .03, 300, .1)
    bed(g('offer')['t0'] - .1, g('oscar')['t0'] + .2, .025, 700, .2)                  # oficina
    bed(g('oscar')['t0'] - .1, g('reunion')['t0'], .1, 1700, .5)                      # aplausos
    bed(g('reunion')['t0'] - .1, g('tu')['t0'], .03, 800, .2)
    bed(g('tu')['t0'] - .1, TOTAL, .06, 3500, .15)
    # ladrido (hook y reencuentro)
    def bark(t0):
        env = np.exp(-tt(.18) * 14) * np.sin(np.pi * np.clip(tt(.18) / .18, 0, 1) ** .5)
        add((np.sin(2 * np.pi * (310 - 90 * tt(.18) / .18) * tt(.18)) + .5 * noise(.18, 900)) * env * .5, t0, .6)
    bark(.35); bark(g('reunion')['t0'] + .3); bark(g('reunion')['t0'] + 1.1)
    # transiciones
    for sc in SCENES[1:]:
        d = .4; env = np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2
        add(noise(d, 1800) * env * .35, sc['t0'] - .2, .5)
    # máquina de escribir
    r0, r1 = g('typing')['t0'], g('typing')['t1']
    t = r0 + .1
    while t < r1 - .1:
        add((noise(.03, 5000) * np.exp(-tt(.03) * 140) * .9), t, .5, rng.uniform(-.2, .2))
        t += rng.choice([.07, .09, .11, .08, .13])
    # sello NO (golpe) en el prop del guion y en el retrato
    add(np.sin(2 * np.pi * 70 * tt(.5)) * np.exp(-tt(.5) * 10) * .8, g('script')['t0'] + (g('script')['t1'] - g('script')['t0']) * .5, .9)
    add(np.sin(2 * np.pi * 60 * tt(.5)) * np.exp(-tt(.5) * 10) * .8, g('no')['t0'] + (g('no')['t1'] - g('no')['t0']) * .5, .9)
    # riser previo al drop (el drop cae en 'O la protagoniza él...') y golpe
    G = g('deal')['t0'] + .02
    SIL = 0.75        # silencio suspensivo antes de Touch The Sky
    rd = min(1.3, g('slam')['t1'] - g('slam')['t0'] - .35)
    rise = noise(rd, 3000) * (tt(rd) / rd) ** 2.2
    add(rise * .55, G - rd - SIL, .6)                                  # el riser sube y se corta en seco ...
    add(np.sin(2 * np.pi * (80 + 300 * (tt(rd) / rd) ** 3) * tt(rd)) * (tt(rd) / rd) * .25, G - rd - SIL, .6)
    boom = np.sin(2 * np.pi * (55 * np.exp(-tt(1.8) * 1.2) + 28) * tt(1.8)) * np.exp(-tt(1.8) * 2.2)
    add(boom * .6, G, 1.0)
    add(noise(1.2, 6000) * np.exp(-tt(1.2) * 4) * .35, G, .6)
    def chime(t0, notes, gain=.35):
        for k, f in enumerate(notes):
            add((np.sin(2 * np.pi * f * tt(1.0)) + .4 * np.sin(2 * np.pi * 2 * f * tt(1.0))) * np.exp(-tt(1.0) * 4.5) * .5, t0 + k * .09, gain)
    chime(g('oscar')['t0'] + .1, [784, 988, 1175, 1568, 1976], .4)
    add(noise(2.5, 1400) * np.sin(np.pi * np.clip(tt(2.5) / 2.5, 0, 1)) * .5, g('oscar')['t0'], .6)
    chime(g('tu')['t0'] + .05, [659, 880, 1318], .3)
    d = .5; env = np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2
    add(noise(d, 1800) * env * .3, TOTAL - LOOP_D - .1, .5)      # whoosh de la disolvencia al inicio
    sfx = L.copy()
    # ---- música: piano de Runaway (inicio) -> Touch The Sky (desde el principio de la canción, al aceptar)
    def dec(path):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        return np.frombuffer(raw, np.float32).reshape(-1, 2)
    rms = lambda x: float(np.sqrt((x ** 2).mean()) + 1e-9)
    run = dec(f'{ROOT}/audio/runaway.m4a')
    song = dec(f'{ROOT}/audio/cancion.m4a')
    # (1) rejilla de notas del piano: una nota (E6) cada ~1.38 s -> onsets medidos con ventanas de 5 ms
    hw = int(.005 * SR)
    mono = run[:int(37.5 * SR), 0]
    en = np.array([np.sqrt(np.mean(mono[i:i + hw] ** 2)) for i in range(0, len(mono) - hw, hw)])
    df = np.maximum(np.diff(en), 0); thr = np.percentile(df, 99)
    cand = [i * .005 for i in range(2, len(df) - 2) if df[i] > thr and df[i] >= df[i - 1] and df[i] >= df[i + 1]]
    ons = []
    for t_ in cand:
        if not ons or t_ - ons[-1] > .25: ons.append(t_)
    ons = np.array([o for o in ons if o > 2.0])
    per = float(np.median(np.diff(ons)[(np.diff(ons) > 1.3) & (np.diff(ons) < 1.45)]))
    k0 = np.round((ons - ons[0]) / per)
    phase = float(np.mean(ons - k0 * per))
    grid = lambda n: phase + n * per
    # (2) primer sonido de Touch The Sky
    sw = int(.005 * SR); sm = song[:int(6 * SR), 0]
    se = np.array([np.sqrt(np.mean(sm[i:i + sw] ** 2)) for i in range(0, len(sm) - sw, sw)])
    T0 = next(i for i, v in enumerate(se) if v > .12 * se[:800].max()) * .005 - .02
    # (3) una nota del piano cae exactamente en G (inicio de Touch The Sky): el vídeo arranca en r0 del instrumental de Runaway
    n_ = int(np.ceil((G - phase) / per)); r_n = grid(n_)
    while r_n < G: n_ += 1; r_n = grid(n_)
    r0 = r_n - G
    m = np.zeros((N, 2), np.float32)
    seg = run[int(r0 * SR):int((r_n + 1.25) * SR)].copy()
    seg *= .075 / rms(seg[int(2 * SR):int(G * SR)])                                    # nivelar el piano (grabación muy suave)
    tl = len(seg) / SR
    ramp_in = np.minimum(1, np.arange(len(seg)) / (SR * .5))
    # la nota E que cae en G se deja sonar y se apaga justo antes de la siguiente nota
    v = np.arange(len(seg)) / SR                                       # tiempo de vídeo (el tramo empieza en t=0)
    f0, f1 = G - SIL - .4, G - SIL
    gain = np.where(v < f0, 1.0, np.where(v < f1, 1 - (v - f0) / (f1 - f0), 0.0))     # el piano se apaga ...
    back = np.clip((v - (G - .012)) / .012, 0, 1) * np.clip(1 - (v - (G + .15)) / 1.0, 0, 1)   # ... silencio ... y la nota vuelve exactamente en G
    gain = np.where(v >= G - .012, back, gain)
    seg *= (ramp_in * gain)[:, None]
    m[:min(len(seg), N)] += seg[:N]
    # Touch The Sky desde su inicio real, con el primer sonido en G
    p2 = song[int(T0 * SR):int(T0 * SR) + (N - int(G * SR))].copy()
    p2 *= .105 / rms(p2[:int(8 * SR)])
    fi2 = np.minimum(1, np.arange(len(p2)) / (SR * .04))
    fo2 = np.minimum(1, (len(p2) - np.arange(len(p2))) / (SR * 1.3))
    p2 *= (fi2 * fo2)[:, None]
    o = int(G * SR); n2 = min(len(p2), N - o)
    m[o:o + n2] += p2[:n2]
    print(f'piano: periodo {per:.4f}s, nota en G={G:.2f}s (r0={r0:.2f}s del instrumental); TouchTheSky desde {T0:.2f}s del original', file=sys.stderr)
    # ducking con la voz (si existe) o ligero constante
    voice = None
    if narr:
        v = subprocess.run(['ffmpeg', '-v', 'error', '-i', narr, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        v = np.frombuffer(v, np.float32).reshape(-1, 2)
        voice = np.zeros((N, 2), np.float32); n = min(N, len(v)); voice[:n] = v[:n]
        env = np.sqrt(np.convolve(voice[:, 0] ** 2, np.ones(int(.08 * SR)) / int(.08 * SR), 'same'))
        env = np.convolve(env, np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
        gate = np.clip(env / (env.max() * .12 + 1e-9), 0, 1)
        m *= (1 - .55 * gate)[:, None]
        voice *= 1.0
    mix = m + sfx * 1.0
    if voice is not None: mix = mix + voice * 1.0
    pk = np.abs(mix).max()
    mix = mix / pk * .9 if pk > .9 else mix
    out = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(f'{ROOT}/audio/mezcla.wav', 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())
    return G, T0


if __name__ == '__main__':
    dur = TOTAL
    args = sys.argv[1:]
    out_name = 'TU_CONFIA_Stallone_Rocky' + ('' if narr else '_PREVIEW_sin_voz') + '.mp4'
    if args and args[0] == '--still':
        t = float(args[1]); fr = frame(int(t * FPS)); fr.save(f'{ROOT}/out/still_{t:.1f}.png'); sys.exit()
    if args and args[0] == '--timing':
        print(json.dumps({'total': TOTAL, 'scenes': [(s['n'], round(s['t0'], 2), round(s['t1'], 2)) for s in SCENES]}, indent=1)); sys.exit()
    G, drop = synth_audio()
    print('drop de la canción en', round(drop, 2), 's -> colocado en vídeo', round(G, 2), 's', file=sys.stderr)
    nf = int(TOTAL * FPS)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                            '-i', f'{ROOT}/audio/mezcla.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', f'{ROOT}/out/{out_name}'], stdin=subprocess.PIPE)
    for fi in range(nf):
        enc.stdin.write(frame(fi).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', nf, file=sys.stderr)
    enc.stdin.close(); enc.wait()
    print('OK', out_name)

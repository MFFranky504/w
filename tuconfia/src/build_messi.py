"""TU CONF.IA - montaje. Uso: python3 -I build.py [--preview N_segundos]
Si existe ../audio/narracion.(mp3|wav|m4a) los tiempos se adaptan a la voz real; si no, se estiman."""
import sys, os, json, re, math, subprocess, glob, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scenes as S
import scenes2 as S2
import scenes3 as S3
from lib import WW, WH, BAY, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, VW, VH = 30, 1080, 1920
SR = 44100
SC = json.load(open(f'{ROOT}/script_messi.json'))
LINES = SC['lines']
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- tiempos
narr = next(iter(glob.glob(f'{ROOT}/audio/narracion_messi.*')), None)


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
    ch = np.array([len(clean(l['t'])) for l in LINES], float)
    cum = np.cumsum(ch) / ch.sum()
    # tiempo de habla -> tiempo real
    gl = [(a, b) for _, a, b in gaps]
    def real(frac):
        target = first + frac * (last - first)
        return target
    bounds = []
    for k in range(len(LINES) - 1):
        tgt = real(cum[k])
        if gaps:
            g = min(gaps, key=lambda g: abs(g[0] - tgt))
            if abs(g[0] - tgt) < 0.9: bounds.append((g[1], g[2])); continue
        bounds.append((tgt, tgt))
    starts, ends = [first], []
    for a, b in bounds: ends.append(a); starts.append(b)
    ends.append(last)
    return starts, ends, last + 0.9


def estimate():
    t, starts, ends = 0.25, [], []
    for l in LINES:
        d = len(clean(l['t'])) / 15.0
        starts.append(t); ends.append(t + d); t += d + l['p']
    return starts, ends, t + 0.7


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
    dict(n='napkin1', a='L1', b='L1', fn=lambda t, u: S3.napkin(t, u, 'hook'), cam=[(0, 80, 146, 1.25), (1, 80, 152, 1.7)]),
    dict(n='potSmall', a='L2', b='L2', fn=lambda t, u: S3.potrero(t, u, 'small'), cam=[(0, 80, 205, 1.2), (1, 84, 214, 1.85)]),
    dict(n='potPlay', a='L3a', b='L3a', fn=lambda t, u: S3.potrero(t, u, 'play'), cam=[(0, 48, 208, 1.2), (1, 112, 208, 1.2)]),
    dict(n='consult', a='L3b', b='L3b', fn=lambda t, u: S3.consultorio(t, u), cam=[(0, 78, 168, 1.1), (1, 76, 178, 1.55)]),
    dict(n='tarmac', a='L4', b='L4', fn=lambda t, u: S3.tarmac(t, u), cam=[(0, 60, 200, 1.0), (1, 92, 208, 1.4)]),
    dict(n='rexach', a='L6', b='L6', fn=lambda t, u: PS(t, 'rexach', 'n', (0, 0), 'purple', tag='CARLES REXACH'), cam=[(0, 80, 162, 1.25), (1, 80, 150, 1.65)]),
    dict(n='rest', a='L7', b='L7', fn=lambda t, u: S3.restaurant(t, u), cam=[(0, 80, 160, 1.05), (1, 80, 168, 1.45)]),
    dict(n='napkin2', a='L8', b='L8', fn=lambda t, u: S3.napkin(t, u, 'write'), cam=[(0, 80, 150, 1.1), (1, 78, 150, 1.5)]),
    dict(n='stad', a='L9', b='L9', fn=lambda t, u: S3.stadium(t, u), cam=[(0, 80, 196, 1.5), (1, 80, 150, 1.0)]),
    dict(n='kidP', a='L10', b='L10', fn=lambda t, u: PS(t, 'messi_kid', 'smile', (0, 0), 'warm', sparkle=True), cam=[(0, 80, 160, 1.45), (1, 80, 150, 1.15)]),
    dict(n='tu', a='L11', b='L11', fn=lambda t, u: S3.tu_cafe(t, u), cam=[(0, 80, 190, 1.4), (1, 80, 176, 1.1)]),
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
DROP_T = next(x['t0'] for x in SCENES if x['n'] == 'napkin2') + .02


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
    ch = next(((a, b, g, lid) for a, b, g, lid in CHUNKS if a <= t < b + 0.0), None)
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
    bed(0, g('potSmall')['t0'] + .2, .035, 900, .3)                                   # murmullo del bar
    bed(g('potSmall')['t0'] - .1, g('consult')['t0'] + .2, .04, 1300, .25)            # potrero
    bed(g('consult')['t0'] - .1, g('tarmac')['t0'] + .2, .02, 400, .1)
    bed(g('tarmac')['t0'] - .1, g('rexach')['t0'] + .2, .08, 250, .6)                 # motores
    bed(g('rexach')['t0'] - .1, g('napkin2')['t0'], .03, 800, .3)
    bed(g('napkin2')['t0'], g('stad')['t0'] + .2, .02, 600, .2)
    bed(g('stad')['t0'] - .1, g('kidP')['t0'], .1, 1600, .5)                           # multitud
    bed(g('tu')['t0'] - .1, TOTAL, .06, 3500, .15)                                    # lluvia
    # golpes de balón durante el regate
    p0, p1 = g('potPlay')['t0'], g('potPlay')['t1']
    t = p0 + .2
    while t < p1 - .2:
        add(np.sin(2 * np.pi * 130 * tt(.07)) * np.exp(-tt(.07) * 50) * .6, t, .5); t += .26
    # transiciones
    for sc in SCENES[1:]:
        d = .4; env = np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2
        add(noise(d, 1800) * env * .35, sc['t0'] - .2, .5)
    # bolígrafo escribiendo
    n0, n1 = g('napkin2')['t0'], g('napkin2')['t1']
    t = n0 + .15
    while t < n1 - .3:
        add(noise(.05, 4500) * np.exp(-tt(.05) * 25) * .35, t, .5, rng.uniform(-.2, .2)); t += rng.choice([.06, .09, .12, .07])
    # riser previo al drop y golpe (el drop de la canción cae al empezar la servilleta)
    G = g('napkin2')['t0'] + .02
    rd = min(1.3, g('rest')['t1'] - g('rest')['t0'] - .35)
    rise = noise(rd, 3000) * (tt(rd) / rd) ** 2.2
    add(rise * .55, G - rd - .25, .6)
    add(np.sin(2 * np.pi * (80 + 300 * (tt(rd) / rd) ** 3) * tt(rd)) * (tt(rd) / rd) * .25, G - rd - .25, .6)
    boom = np.sin(2 * np.pi * (55 * np.exp(-tt(1.8) * 1.2) + 28) * tt(1.8)) * np.exp(-tt(1.8) * 2.2)
    add(boom * .95, G, 1.0)
    add(noise(1.2, 6000) * np.exp(-tt(1.2) * 4) * .5, G, .6)
    def chime(t0, notes, gain=.35):
        for k, f in enumerate(notes):
            add((np.sin(2 * np.pi * f * tt(1.0)) + .4 * np.sin(2 * np.pi * 2 * f * tt(1.0))) * np.exp(-tt(1.0) * 4.5) * .5, t0 + k * .09, gain)
    chime(g('stad')['t0'] + .1, [784, 988, 1175, 1568, 1976], .4)
    add(noise(2.5, 1400) * np.sin(np.pi * np.clip(tt(2.5) / 2.5, 0, 1)) * .5, g('stad')['t0'], .6)   # rugido de la grada
    chime(g('tu')['t0'] + .05, [659, 880, 1318], .3)
    add(noise(.25, 2500) * np.exp(-tt(.25) * 14) * .3, TOTAL - .2, .5)
    sfx = L.copy()
    # ---- música
    song = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{ROOT}/audio/cancion.m4a', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    song = np.frombuffer(song, np.float32).reshape(-1, 2)
    # inicio del "momento interesante": mayor salto de energía cerca de 31.9 s
    w = int(.01 * SR); a0, a1 = int(31.0 * SR), int(33.0 * SR)
    e = np.array([np.sqrt((song[i:i + w] ** 2).mean()) for i in range(a0, a1, w)])
    dj = np.array([e[i:i + 5].mean() - e[max(0, i - 5):i].mean() for i in range(5, len(e) - 5)])
    drop = 31.0 + (int(np.argmax(dj)) + 5) * .01
    start1 = 2.2
    d1 = min(G - 0.95, 14.0)
    m = np.zeros((N, 2), np.float32)
    p1 = song[int(start1 * SR):int((start1 + d1) * SR)].copy()
    fi_ = np.minimum(1, np.arange(len(p1)) / (SR * .8)); fo_ = np.minimum(1, (len(p1) - np.arange(len(p1))) / (SR * (1.0 if d1 < G - 0.95 else .08)))
    p1 *= (fi_ * fo_)[:, None] * .42
    m[:len(p1)] += p1[:N]
    ps = int((drop - .03) * SR)
    p2 = song[ps:ps + (N - int((G - .03) * SR))].copy()
    fo2 = np.minimum(1, (len(p2) - np.arange(len(p2))) / (SR * .5))
    p2 *= fo2[:, None] * .78
    o = int((G - .03) * SR); n2 = min(len(p2), N - o)
    m[o:o + n2] += p2[:n2]
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
    return G, drop


if __name__ == '__main__':
    dur = TOTAL
    args = sys.argv[1:]
    out_name = 'TU_CONFIA_Messi_Servilleta' + ('' if narr else '_PREVIEW_sin_voz') + '.mp4'
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

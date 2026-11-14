import os
os.environ['TC_LAND'] = '1'          # mundo apaisado 320x180 (x6 = 1920x1080) para YouTube
"""TU CONF.IA - montaje del video largo «súper editado».
Uso: python3 -I build_largo.py <nombre> [--still t | --part i n | --audio | --timing]
Lee docs/largo_<nombre>/guion_final.json (líneas con capítulo, emoción y escenario), audio/tiempos_<nombre>_largo.json
(tiempos exactos de cada línea) y audio/whisper_<nombre>_largo.json (tiempos de cada palabra)."""
import sys, json, re, math, subprocess, wave, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import scenes18 as S18
from cta import draw_cta
from lib import WW, WH, ease

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1]
FPS, VW, VH, SR = 30, 1920, 1080, 44100
LINES = json.load(open(f'{ROOT}/docs/largo_{NAME}/guion_final.json'))
TIM = json.load(open(f'{ROOT}/audio/tiempos_{NAME}_largo.json'))
WORDS = json.load(open(f'{ROOT}/audio/whisper_{NAME}_largo.json'))['words']
NARR = f'{ROOT}/audio/narracion_{NAME}_largo.wav'
for l, tm in zip(LINES, TIM): l['start'], l['end'] = tm['start'], tm['end']
OUTRO = 7.0
TOTAL = round((LINES[-1]['end'] + OUTRO) * FPS) / FPS
CHAP_NAMES = {1: 'EL NIÑO QUE NO TENÍA NADA', 2: 'LA CARPA', 3: 'LA NOCHE EN BLANCO', 4: 'EL CINE DICE QUE NO', 5: 'AHÍ ESTÁ EL DETALLE',
              6: 'HOLLYWOOD', 7: 'EL TROPIEZO', 8: 'LA PALABRA'}
clean = lambda t: t.replace('*', '')

# ---------------------------------------------------------------- palabras de cada línea (Whisper) y momentos de énfasis
for l in LINES: l['words'] = [w for w in WORDS if l['start'] - .15 <= w['start'] < l['end'] + .05]
norm = lambda s: re.sub(r'[^a-záéíóúñü0-9]', '', s.lower())
PUNCH = []                                                    # golpe de zoom en la palabra marcada con *asteriscos*
for l in LINES:
    m = re.search(r'\*([^*]+)\*', l['t'])
    if not m: continue
    key = norm(m.group(1).split()[0])
    hit = next((w for w in l['words'] if norm(w['word']).startswith(key[:5])), None)
    PUNCH.append(hit['start'] if hit else l['end'] - .4)

# ---------------------------------------------------------------- escenas (escenario = grupo de líneas seguidas con el mismo kit) y planos
SCENES = []
for i, l in enumerate(LINES):
    new_chap = i and l['cap'] != LINES[i - 1]['cap']
    if not SCENES or l['kit'] != LINES[i - 1]['kit'] or new_chap:
        t0 = 0.0 if i == 0 else (LINES[i - 1]['end'] + .12 if new_chap else l['start'] - .18)
        SCENES.append(dict(kit=l['kit'], t0=t0, lines=[], chap=l['cap'] if new_chap else None))
    SCENES[-1]['lines'].append(i)
for a, b in zip(SCENES, SCENES[1:]): a['t1'] = b['t0']
SCENES[-1]['t1'] = TOTAL
SHOTS = []                                                    # (t0, escena, índice de plano, nº de frase)
for si, s in enumerate(SCENES):
    k = 0
    for j, li in enumerate(s['lines']):
        l = LINES[li]
        a = s['t0'] if j == 0 else l['start'] - .1
        SHOTS.append((a, si, k, j)); k += 1
        if l['end'] - l['start'] > 4.2:                       # frase larga: un corte más a mitad de frase
            mid = (l['start'] + l['end']) / 2
            w = min(l['words'], key=lambda w: abs(w['start'] - mid)) if l['words'] else None
            SHOTS.append(((w['start'] if w else mid) - .05, si, k, j)); k += 1
SHOT_T = [x[0] for x in SHOTS]
TKIND = (['whip', 'flash', 'zoom', 'dissolve', 'whip', 'flash', 'dissolve', 'zoom'] * 10)[:len(SCENES) - 1]
IMPACT = [LINES[i]['start'] for i, l in enumerate(LINES) if l['kit'] in ('boxing', 'laugh', 'name', 'estreno', 'oscar') and l['emo'] == 'excited']


def shot_at(t):
    i = max(0, np.searchsorted(SHOT_T, t + 1e-6, 'right') - 1)
    return SHOTS[i], i


def cam_for(ix, u):
    """movimiento de cámara del plano: empuje, alejamiento o paneo (alterna) con escala suave."""
    kind = ix % 4
    if kind == 0: return 160, 90, 1.0 + .07 * u
    if kind == 1: return 160, 90, 1.08 - .07 * u
    if kind == 2: return 150 + 20 * u, 90, 1.06
    return 170 - 20 * u, 92, 1.06


def render_scene(si, t, force_shot=None):
    s = SCENES[si]
    (a, _, k, j), ix = shot_at(t) if force_shot is None else force_shot
    if SHOTS[ix][1] != si:                                    # transición: el plano de la otra escena
        cand = [(n, x) for n, x in enumerate(SHOTS) if x[1] == si]
        ix, (a, _, k, j) = (cand[-1] if si < SHOTS[ix][1] else cand[0])
    shots = S18.KITS[s['kit']]
    nxt = SHOT_T[ix + 1] if ix + 1 < len(SHOTS) else TOTAL
    T, tl = t - s['t0'], t - a
    img = shots[k % len(shots)](max(0, T), max(0, tl), j)
    u = max(0, min(1, tl / max(.5, nxt - a)))
    cx, cy, z = cam_for(ix, ease(u))
    for p in PUNCH:                                           # golpe de zoom en la palabra clave
        dt = t - p
        if 0 <= dt < .45: z *= 1 + .09 * math.exp(-dt / .12)
    sh = 0.0
    for p in IMPACT + [SHOT_T[ix]]:                           # sacudida en impactos y cortes
        dt = t - p
        if 0 <= dt < .28: sh += math.sin(dt * 95) * (7 if p in IMPACT else 3) * (1 - dt / .28)
    big = img.resize((VW, VH), Image.NEAREST)
    if z > 1.001 or abs(cx - 160) > .5 or abs(cy - 90) > .5 or sh:
        w, h = VW / z, VH / z
        x0 = min(max((cx - 160) * 6 + (VW - w) / 2 + sh, 0), VW - w); y0 = min(max((cy - 90) * 6 + (VH - h) / 2 + sh * .6, 0), VH - h)
        big = big.resize((VW, VH), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    out = ImageEnhance.Color(big).enhance(1.22)
    return ImageEnhance.Contrast(out).enhance(1.05)


BAYF = np.kron(np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (VH // 32 + 1, VW // 32 + 1)), np.ones((8, 8)))[:VH, :VW]

# ---------------------------------------------------------------- textos en pantalla
F = lambda w, s: ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{w}.otf', s)
FL = lambda s: ImageFont.truetype(f'{ROOT}/assets/fonts/silkscreen-latin-700-normal.woff', s)
YEL, WHITE, DARK, PURPLE, PINK = (255, 216, 74), (255, 255, 255), (14, 10, 26), (139, 92, 246), (230, 40, 110)
BRAND = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); bd = ImageDraw.Draw(BRAND); fb = F('Black', 40)
w1 = bd.textlength('TU CONF', font=fb); w2 = bd.textlength('.IA', font=fb); bx = 60
bd.rounded_rectangle([bx - 12, 40, bx + w1 + w2 + 22, 116], radius=14, fill=(14, 10, 26, 150))
bd.text((bx, 54), 'TU CONF', font=fb, fill=WHITE); bd.rounded_rectangle([bx + w1 - 2, 52, bx + w1 + w2 + 10, 106], radius=8, fill=PURPLE)
bd.text((bx + w1 + 4, 54), '.IA', font=fb, fill=WHITE)
MASC = Image.open(f'{ROOT}/assets/mascota_retrato.png').convert('RGBA'); MASC = MASC.resize((MASC.width * 5, MASC.height * 5), Image.NEAREST)

# subtítulos: grupos de hasta 3 palabras; la palabra que suena se ilumina (karaoke)
CHUNKS = []
for l in LINES:
    toks = []
    for m in re.finditer(r'\*([^*]+)\*([^\s*]*)|([^\s*]+)', l['t']):
        if m.group(1):
            for w in m.group(1).split(): toks.append([w, True])
            if m.group(2): toks[-1][0] += m.group(2)
        else: toks.append([m.group(3), False])
    groups, cur, n = [], [], 0
    for w, e in toks:
        if cur and (n + len(w) > 14 or len(cur) >= 3 or cur[-1][0][-1] in '.?!…:»'):
            groups.append(cur); cur, n = [], 0
        cur.append((w, e)); n += len(w) + 1
    if cur: groups.append(cur)
    ww = l['words']; tot = sum(len(norm(w)) or 1 for w, _ in toks)
    wc = np.cumsum([len(norm(w['word'])) or 1 for w in ww]) if ww else None
    def time_at(frac):                                        # instante en que se ha dicho esa fracción de la frase
        if not ww: return l['start'] + frac * (l['end'] - l['start'])
        tgt = frac * wc[-1]; i = int(np.searchsorted(wc, tgt))
        return ww[min(i, len(ww) - 1)]['start']
    acc = 0
    for g in groups:
        tw = []
        for w, e in g:
            tw.append(time_at(acc / tot)); acc += len(norm(w)) or 1
        CHUNKS.append(dict(a=tw[0], g=g, tw=tw, lid=LINES.index(l)))
for i, ch in enumerate(CHUNKS):
    ch['a'] = max(ch['a'] - .06, LINES[ch['lid']]['start'] - .05)
    ch['b'] = CHUNKS[i + 1]['a'] if i + 1 < len(CHUNKS) and CHUNKS[i + 1]['lid'] == ch['lid'] else LINES[ch['lid']]['end'] + .15


def draw_sub(img, t):
    ch = next((c for c in CHUNKS if c['a'] <= t < c['b']), None)
    if not ch: return
    size = 78; ft = FL(size); d = ImageDraw.Draw(img); GAP = int(size * .26)
    ws = [w.upper() for w, _ in ch['g']]
    total = sum(d.textlength(w, font=ft) for w in ws) + GAP * (len(ws) - 1)
    while total > 1500 and size > 46:
        size -= 4; ft = FL(size); GAP = int(size * .26); total = sum(d.textlength(w, font=ft) for w in ws) + GAP * (len(ws) - 1)
    pop = min(1, (t - ch['a']) / .08); sc = .82 + .18 * (1 - (1 - pop) ** 2)
    lay = Image.new('RGBA', (VW, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([(VW - total) / 2 - 30, 18, (VW + total) / 2 + 30, size + 78], radius=20, fill=(10, 6, 22, 120))
    x = (VW - total) / 2
    for (w, e), wt, W_ in zip(ch['g'], ch['tw'], ws):
        said = t >= wt - .02
        col = YEL if e else (WHITE if said else (190, 190, 205))
        dy = -6 if (said and t - wt < .12) else 0
        ld.text((x, 46 + dy), W_, font=ft, fill=col, stroke_width=7, stroke_fill=DARK)
        x += ld.textlength(W_, font=ft) + GAP
    if sc < 1: lay = lay.resize((int(VW * sc), int(200 * sc)), Image.BILINEAR)
    img.alpha_composite(lay, ((VW - lay.width) // 2, 870 + (200 - lay.height) // 2))


CHAP_T = [(s['t0'], s['chap']) for s in SCENES if s['chap']]


def draw_chapter(img, t):
    for a, n in CHAP_T:
        dur = 2.3
        if not (a <= t < a + dur): continue
        k = ease(min(1, (t - a) / .3)); out = ease(min(1, (a + dur - t) / .3))
        lay = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 380, VW, 700], fill=(10, 6, 22, int(190 * k * out)))
        x_off = int((1 - k) * -VW * .4 + (1 - out) * VW * .4)
        ld.text((VW // 2 + x_off, 450), f'CAPÍTULO {n}', font=FL(52), fill=(*YEL, int(255 * out)), anchor='mm', stroke_width=6, stroke_fill=DARK)
        ld.text((VW // 2 - x_off, 560), CHAP_NAMES[n], font=FL(92 if len(CHAP_NAMES[n]) < 20 else 70), fill=(255, 255, 255, int(255 * out)), anchor='mm', stroke_width=9, stroke_fill=DARK)
        ld.rectangle([VW // 2 - int(400 * k), 625, VW // 2 + int(400 * k), 633], fill=(*PINK, int(255 * out)))
        img.alpha_composite(lay)


# textos grandes que aparecen de golpe (años, nombre, cuenta atrás, palabras clave)
POPS = []
for i, l in enumerate(LINES):
    y = re.search(r'(19\d\d)', l['t']) or re.search(r'(mil novecientos [a-z ]+)', l['t'])
    yy = {'once': 1911, 'treinta y seis': 1936, 'cuarenta': 1940, 'cincuenta y seis': 1956, 'cincuenta y siete': 1957, 'sesenta': 1960, 'noventa y dos': 1992, 'noventa y tres': 1993}
    for k_, v in yy.items():
        if f'mil novecientos {k_}' in clean(l['t']).replace('*', ''): POPS.append((l['start'] + .2, l['start'] + 2.6, str(v), 'año'))
SPECIAL = {'De ahí habría salido el nombre que lo haría famoso: *Cantinflas*.': ('CANTINFLAS', 'big', -1.6),
           'Un segundo. Dos. *Tres*.': ('1 · 2 · 3', 'count', 0), 'Y pasó sin *éxito*.': ('SIN ÉXITO', 'stamp', 0),
           'Y esta vez... no repite el *éxito*.': ('FRACASO', 'stamp', 0), 'Y en mil novecientos cincuenta y siete, él gana el Globo de *Oro*.': ('GLOBO DE ORO', 'big', -1.4),
           'La película gana el Óscar a mejor *película*.': ('ÓSCAR', 'big', -1.0), 'La Real Academia Española incluye un verbo nuevo en su diccionario: *cantinflear*.': ('CANTINFLEAR', 'big', -1.6),
           'Y la carpa... *explotó* de risa.': ('¡JA JA JA!', 'big', -.8), 'Él *no*.': ('ÉL NO.', 'big', -.3),
           '«Ahí está el *detalle*».': ('AHÍ ESTÁ EL DETALLE', 'big', 0), 'Sus funerales duraron tres *días*.': ('3 DÍAS', 'big', -.8)}
for i, l in enumerate(LINES):
    if l['t'] in SPECIAL:
        txt, kind, off = SPECIAL[l['t']]
        POPS.append((l['end'] + off if off else l['start'] + .1, l['end'] + .9, txt, kind))


def draw_pops(img, t):
    for a, b, txt, kind in POPS:
        if not (a <= t < b): continue
        k = min(1, (t - a) / .12); out = min(1, (b - t) / .18)
        if kind == 'año':
            lay = Image.new('RGBA', (600, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([20, 30, 580, 170], radius=18, fill=(*PINK, 230)); ld.text((300, 100), txt, font=FL(110), fill=WHITE, anchor='mm', stroke_width=6, stroke_fill=DARK)
            sc = 1.35 - .35 * ease(k); lay = lay.resize((int(600 * sc), int(200 * sc)), Image.BILINEAR).rotate(-6, expand=True, resample=Image.BILINEAR)
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * out)))
            img.alpha_composite(lay, (VW - 120 - lay.width, 150 - (lay.height - 200) // 2)); continue
        if kind == 'count':
            n = min(3, 1 + int((t - a) / .75)); txt = str(n)
        size = 230 if kind in ('big', 'count') and len(txt) < 10 else 150
        if kind == 'stamp': size = 170
        ft = FL(size); d = ImageDraw.Draw(img)
        tw = d.textlength(txt, font=ft)
        while tw > 1700: size -= 10; ft = FL(size); tw = d.textlength(txt, font=ft)
        lay = Image.new('RGBA', (int(tw) + 80, size + 80), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((40 + 8, 30 + 8), txt, font=ft, fill=PINK if kind != 'stamp' else (120, 10, 20), stroke_width=10, stroke_fill=PINK if kind != 'stamp' else (120, 10, 20))
        ld.text((40, 30), txt, font=ft, fill=YEL if kind != 'stamp' else (240, 50, 60), stroke_width=10, stroke_fill=DARK)
        kk = (t - a) / .75 % 1 if kind == 'count' else k
        sc = 1.6 - .6 * ease(min(1, kk / .16 if kind == 'count' else kk))
        rot = -8 if kind == 'stamp' else math.sin(t * 20) * 2 * (1 - k)
        lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BILINEAR).rotate(rot, expand=True, resample=Image.BILINEAR)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
        img.alpha_composite(lay, ((VW - lay.width) // 2, 400 - lay.height // 2))


HOOK_TXT = [(LINES[0]['start'] + .1, LINES[0]['end'] + .2, 'SU PEOR NOCHE', '¿UNA PALABRA?')]


def draw_hook(img, t):
    for a, b, l1, l2 in HOOK_TXT:
        if not (a <= t < b): continue
        k = min(1, (t - a) / .14); out = min(1, (b - t) / .15)
        lay = Image.new('RGBA', (1700, 360), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for dx, dy, col in ((7, 7, PINK), (0, 0, None)):
            for n_, ln in enumerate((l1, l2)):
                ld.text((850 + dx, 80 + n_ * 170 + dy), ln, font=FL(140), anchor='mm', fill=col or (YEL if n_ == 0 else WHITE), stroke_width=9, stroke_fill=DARK if col is None else col)
        sc = .6 + .5 * k - .1 * k * k
        lay = lay.resize((int(1700 * sc), int(360 * sc)), Image.BILINEAR)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * min(1, k * 2) * out)))
        img.alpha_composite(lay, ((VW - lay.width) // 2 + int(math.sin(t * 50) * 3 * (1 - k)), 330 - lay.height // 2))


def draw_progress(img, t):
    d = ImageDraw.Draw(img); y = VH - 10
    d.rectangle([0, y, VW, VH], fill=(14, 10, 26, 180))
    d.rectangle([0, y, int(VW * min(1, t / (TOTAL - OUTRO))), VH], fill=PINK)
    for a, n in CHAP_T: x = int(VW * a / (TOTAL - OUTRO)); d.rectangle([x - 2, y - 4, x + 2, VH], fill=YEL)


CTA_T0 = LINES[-1]['end'] + .3


def draw_outro(img, t):
    if t < CTA_T0: return
    u = min(1, (t - CTA_T0) / .5); pop = 1 - (1 - u) ** 3; bob = math.sin((t - CTA_T0) * 2.4) * 8
    img.alpha_composite(MASC, ((VW - MASC.width) // 2, int(VH - 150 - MASC.height * pop + (1 - pop) * 200 + bob)))


def overlay(base, t):
    img = base.convert('RGBA'); img.alpha_composite(BRAND)
    draw_chapter(img, t); draw_hook(img, t); draw_pops(img, t)
    draw_cta(img, t, CTA_T0, TOTAL, 'yt', 0.0, ytop=36, cx=1500, scale=1.35, show=6.6)
    draw_outro(img, t); draw_sub(img, t); draw_progress(img, t)
    if t > TOTAL - .6:                                         # fundido final a negro
        img = Image.blend(img.convert('RGB'), Image.new('RGB', (VW, VH), (0, 0, 0)), (t - (TOTAL - .6)) / .6).convert('RGBA')
    return img.convert('RGB')


def frame(fi):
    t = fi / FPS
    si = max(i for i, s in enumerate(SCENES) if s['t0'] <= t + 1e-6)
    img = render_scene(si, t)
    HW = .16
    for bi in range(len(SCENES) - 1):
        T = SCENES[bi + 1]['t0']; kind = TKIND[bi]
        if abs(t - T) >= HW: continue
        k = (t - (T - HW)) / (2 * HW)
        a_ = render_scene(bi, t); b_ = render_scene(bi + 1, t)
        if kind == 'dissolve': img = Image.fromarray(np.where((BAYF < ease(k))[..., None], np.array(b_), np.array(a_)))
        elif kind == 'flash':
            img = b_ if t >= T else a_; img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 250, 235)), max(0, 1 - abs(t - T) / .1) * .85)
        elif kind == 'whip':
            cat = np.concatenate([np.array(a_), np.array(b_)], 1); off = int(ease(k) * VW)
            img = Image.fromarray(cat[:, off:off + VW]).filter(ImageFilter.GaussianBlur(14 * math.sin(math.pi * k)))
        elif kind == 'zoom':
            src = a_ if k < .5 else b_; s2 = 1 + .5 * (k * 2) ** 2 if k < .5 else 1 + .5 * ((1 - k) * 2) ** 2
            w2, h2 = int(VW / s2), int(VH / s2)
            img = src.crop(((VW - w2) // 2, (VH - h2) // 2, (VW + w2) // 2, (VH + h2) // 2)).resize((VW, VH), Image.BILINEAR)
            img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 255, 255)), .5 * math.sin(math.pi * k))
        break
    for st in SHOT_T:                                          # corte duro de plano: destello mínimo
        if 0 <= t - st < .06 and all(abs(st - s['t0']) > .2 for s in SCENES): img = Image.blend(img, Image.new('RGB', (VW, VH), (255, 250, 235)), .35 * (1 - (t - st) / .06))
    return overlay(img, t)


# ---------------------------------------------------------------- audio
def dec(path, mono=False):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1' if mono else '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    return x if mono else x.reshape(-1, 2)


def synth_audio():
    N = int(TOTAL * SR); rng = np.random.default_rng(7)
    sfx = np.zeros((N, 2), np.float32)
    tt = lambda d: np.arange(int(d * SR)) / SR

    def add(sig, t0, g=1.0, pan=0.0):
        i0 = int(t0 * SR)
        if i0 >= N or i0 + len(sig) <= 0: return
        a = max(0, -i0); sig = sig[a:]; i0 = max(0, i0); n = min(len(sig), N - i0)
        sfx[i0:i0 + n, 0] += sig[:n] * g * (1 - max(0, pan)); sfx[i0:i0 + n, 1] += sig[:n] * g * (1 + min(0, pan))

    def noise(d, lp=None):
        n = rng.standard_normal(int(d * SR)).astype(np.float32)
        if lp:
            k = max(1, int(SR / lp / 2)); n = (np.convolve(n, np.ones(k) / k, 'same') * math.sqrt(k) * .6).astype(np.float32)
        return n
    env = lambda d, a=.01, r=None: np.minimum(1, tt(d) / a) * (np.exp(-tt(d) / r) if r else 1)
    whoosh = lambda d=.35: noise(d, 1600) * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2 * .7
    pop = lambda: np.sin(2 * np.pi * (600 + 900 * tt(.12) / .12) * tt(.12)) * np.exp(-tt(.12) * 20) * .5
    thump = lambda: np.sin(2 * np.pi * 52 * tt(.25)) * np.exp(-tt(.25) * 14)
    heartbeat = lambda: np.concatenate([thump(), np.zeros(int(.12 * SR)), thump() * .7])

    def laughs(t0, d, g=.5):                                   # risas: ráfagas de ruido modulado
        n = noise(d, 1800); m = (.6 + .4 * np.sin(2 * np.pi * 4.5 * tt(d) + rng.random() * 6)) * np.minimum(1, np.minimum(tt(d), d - tt(d)) / 1.2)   # entrada y salida suaves
        add(n * m * .5, t0, g)

    def applause(t0, d, g=.5):
        n = noise(d, 5000) * (rng.random(int(d * SR)) > .6) * np.minimum(1, np.minimum(tt(d), d - tt(d)) / .5)
        add(n.astype(np.float32) * .6, t0, g)
    sc = {}
    for s in SCENES: sc.setdefault(s['kit'], []).append(s)
    first = lambda k: sc[k][0]
    for s in SCENES[1:]: add(whoosh(), s['t0'] - .18, .5)
    for st in SHOT_T[1:]: add(whoosh(.18) * .5, st - .05, .35)
    for a, b, txt, kind in POPS: add(pop(), a, .55 if kind != 'año' else .4)
    add(pop(), HOOK_TXT[0][0], .6)
    for p in PUNCH: add(thump() * .35, p, .5)
    for k_ in ('stage', 'freeze'):                             # latido en el escenario
        for s in sc.get(k_, []):
            t_ = s['t0'] + .1
            while t_ < s['t1'] - .3: add(heartbeat(), t_, .9); t_ += .95
    s = first('freeze'); l3 = next(l for l in LINES if l['t'].startswith('Un segundo'))
    for w in l3['words'][:6]: add(np.sin(2 * np.pi * 1800 * tt(.05)) * np.exp(-tt(.05) * 60) * .5, w['start'], .6)   # tic de reloj en "un segundo, dos, tres"
    for k_ in ('babble', 'laugh', 'name'):
        for s in sc.get(k_, []): laughs(s['t0'] + (.6 if k_ == 'babble' else 0), s['t1'] - s['t0'] - .4, .28 if k_ != 'babble' else .16)
    for k_ in ('laugh', 'estreno', 'oscar', 'home'):
        for s in sc.get(k_, []): applause(s['t0'] + .2, min(5, s['t1'] - s['t0'] - .3), .5)
    s = first('boxing')                                        # campana del ring
    for k_ in range(3): add((np.sin(2 * np.pi * 1320 * tt(1.2)) + .5 * np.sin(2 * np.pi * 2650 * tt(1.2))) * np.exp(-tt(1.2) * 3) * .35, s['t0'] + .15 + k_ * .22, .7)
    s = first('bullring'); add(noise(1.6, 900) * np.sin(np.pi * np.clip(tt(1.6) / 1.6, 0, 1)) * .5, s['t0'] + .4, .5)       # ¡olé! del público
    for s in sc.get('estreno', []):                            # flashes de cámara
        t_ = s['t0'] + .3
        while t_ < s['t1']: add(noise(.05, 6000) * np.exp(-tt(.05) * 50), t_, .5); t_ += 1 / 1.2
    for s in sc.get('dictionary', []):                         # máquina de escribir
        t_ = s['t0'] + .3
        for _ in range(11): add(noise(.04, 6000) * np.exp(-tt(.04) * 80) * .8, t_, .45); t_ += 1 / 7
    for s in sc.get('balloon', []):
        for k_ in range(int((s['t1'] - s['t0']) * 3)):
            if k_ % 2 == 0: add(noise(.33, 700) * .5, s['t0'] + k_ / 3, .25)
    for k_ in ('rain',):
        for s in sc.get(k_, []):
            d = s['t1'] - s['t0']; add(noise(d, 4000) * np.minimum(1, np.minimum(tt(d), d - tt(d)) / .5) * .35, s['t0'], .5)
    # ---- música: pista por tramo, mismo volumen, fundidos; silencio en «la noche en blanco» hasta que empieza a hablar sin decir nada
    T_ = lambda k: first(k)['t0']
    SECT = [('jazz3', 0.0, 0.0, T_('city'), .08),
            ('heard_em_say', 0.0, T_('city'), T_('carpa'), .10),
            ('jazz3', 40.0, T_('carpa'), T_('freeze'), .10),
            ('jazz4', 0.0, T_('babble'), T_('cine'), .11),
            ('jazz2', 0.0, T_('cine'), T_('estreno'), .10),
            ('congratulations', 0.0, T_('estreno'), T_('hollywood'), .11),
            ('jazz4', 30.0, T_('hollywood'), T_('pepe'), .11),
            ('jazz2', 70.0, T_('pepe'), T_('home'), .09),
            ('jazz7', 0.0, T_('home'), T_('funeral'), .10),
            ('jazz1', 0.0, T_('funeral'), T_('final'), .09),
            ('jazz7', 60.0, T_('final'), TOTAL, .11)]
    TR = {k: dec(f'{ROOT}/audio/{k}.m4a') for k in set(x[0] for x in SECT)}
    mus = np.zeros((N, 2), np.float32); FD = .8
    for k_, (nm, off, a, b, g) in enumerate(SECT):
        i0, i1 = int(a * SR), min(N, int(b * SR)); n = i1 - i0
        if n <= 0: continue
        seg = TR[nm][int(off * SR):int(off * SR) + n].copy()
        if len(seg) < n: seg = np.concatenate([seg, TR[nm][:n - len(seg)]])
        seg *= g / (np.sqrt((seg ** 2).mean()) + 1e-9)
        v = np.arange(n) / SR; e = np.clip(v / FD, 0, 1) * np.clip((n / SR - v) / FD, 0, 1)
        if k_ == 0: e = np.clip(v / 2.5, .25, 1) * np.clip((n / SR - v) / FD, 0, 1)        # el gancho arranca con la música baja y el latido
        mus[i0:i1] += seg * e[:, None]
        print(f'música {nm} {a:.1f}-{b:.1f}s', file=sys.stderr)
    voice = np.zeros((N, 2), np.float32); vv = dec(NARR); n = min(N, len(vv)); voice[:n] = vv[:n]
    def mavg(x, k):                                        # promedio móvil con suma acumulada (O(n))
        c_ = np.cumsum(np.concatenate([np.zeros(k // 2 + 1), x, np.zeros(k - k // 2)]))
        return ((c_[k:] - c_[:-k]) / k)[:len(x)]
    envv = np.sqrt(np.maximum(mavg(voice[:, 0] ** 2, int(.08 * SR)), 0)); envv = mavg(envv, int(.3 * SR))
    gate = np.clip(envv / (envv.max() * .12 + 1e-9), 0, 1)
    mus *= (1 - .45 * gate)[:, None]
    voice *= .15 / (np.sqrt((voice[voice[:, 0] ** 2 > 1e-4] ** 2).mean()) + 1e-9)
    mix = mus + sfx * .7 + voice
    mix = np.tanh(mix * 1.15) / np.tanh(1.15) * .93
    out = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(f'{ROOT}/audio/mezcla_{NAME}_largo.wav', 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())


if __name__ == '__main__':
    args = sys.argv[2:]
    print('duración', round(TOTAL, 1), 's ·', len(SCENES), 'escenarios ·', len(SHOTS), 'planos', file=sys.stderr)
    if args and args[0] == '--still':
        t = float(args[1]); frame(int(t * FPS)).save(f'{ROOT}/out/still_{t:.1f}.png'); sys.exit()
    if args and args[0] == '--timing':
        print(json.dumps([(s['kit'], round(s['t0'], 2), round(s['t1'], 2), s['chap']) for s in SCENES])); sys.exit()
    if args and args[0] == '--audio':
        synth_audio(); print('OK audio'); sys.exit()
    if args and args[0] == '--range':                         # --range fa fb nombre: tramo de fotogramas (para re-renderizar solo una parte)
        a_, b_, nm = int(args[1]), int(args[2]), args[3]
        enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-tune', 'animation', '-pix_fmt', 'yuv420p', f'{ROOT}/out/{nm}.mp4'], stdin=subprocess.PIPE)
        for fi in range(a_, b_): enc.stdin.write(frame(fi).tobytes())
        enc.stdin.close(); enc.wait(); print('OK', nm); sys.exit()
    if args and args[0] == '--part':
        i_, n_ = int(args[1]), int(args[2]); nf = int(TOTAL * FPS); a_, b_ = nf * i_ // n_, nf * (i_ + 1) // n_
        enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-tune', 'animation', '-pix_fmt', 'yuv420p', f'{ROOT}/out/partL_{i_}.mp4'], stdin=subprocess.PIPE)
        for fi in range(a_, b_):
            enc.stdin.write(frame(fi).tobytes())
            if fi % 300 == 0: print('parte', i_, 'frame', fi, '/', b_, file=sys.stderr)
        enc.stdin.close(); enc.wait(); print('OK parte', i_); sys.exit()

import sys, math, json, subprocess, numpy as np
sys.path.insert(0, '.')
from multiprocessing import Pool
import render as R
from lib import *
FPS = 24
TL = json.load(open('v4/timeline.json')); DUR = TL['dur']; SC = TL['scenes']; CAPS = TL['caps']
ns = [s for s in SC if s[0] == 'note'][0]
R.NOTE = [(50.0 + c[0] - ns[2], c[2]) for c in CAPS if ns[2] <= c[0] < ns[3] and c[2] != 'Y una nota.']
BANDS = {'hook_lighter', 'cabin_sleep', 'speaker', 'arg_talk', 'ven_talk', 'per_talk', 'cta_end'}

def fit(t, mw, s0):
    s = s0
    while font(s, 'Black').getlength(t) > mw: s -= 4
    return font(s, 'Black')

def obj2(lt, dur):
    im = R.BG.copy(); sc = 1 + .06 * lt / dur
    for k, w_, rot, cy in (('axe', 900, -12, 700), ('knife', 900, -6, 1130)):
        o = R.O[k]; ww = int(w_ * sc); sp = o.resize((ww, int(o.size[1] * ww / o.size[0])), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
        R.shadow_paste(im, sp, 540, cy)
    text_c(ImageDraw.Draw(im), (540, 250), 'HACHA Y CUCHILLO', font(92, 'ExtraBold'), (225, 225, 225), 6)
    return np.array(im, np.float32)

def ask(lt):
    im = Image.new('RGB', (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
    text_c(d, (540, 760), '¿QUÉ HACES?', fit('¿QUÉ HACES?', 960, 170), (245, 245, 240), 8); d.rectangle((140, 880, 940, 890), fill=(200, 30, 30))
    for i, (L, tx) in enumerate((('A', 'CHIMENEA'), ('B', 'MURO'), ('C', 'VELAS'))):
        x = 200 + i * 340; d.ellipse((x - 70, 980, x + 70, 1120), fill=(235, 235, 230)); text_c(d, (x, 1050), L, font(100, 'Black'), (18, 18, 22)); text_c(d, (x, 1170), tx, font(44, 'Bold'), (220, 220, 215))
    return np.array(im, np.float32)

def visual(v, T, lt, dur):
    u = min(1, lt / dur)
    if v == 'hook_lighter': return R.obj_scene(lt, 0, dur, 'lighter', '', 980, 0, 820, spark=.35)
    if v == 'cabin_sleep': return R.world_scene(3 + lt * .65, 1080, 3000, 1.0 + .35 * ease(u), 'all')
    if v == 'speaker': return R.world_scene(8.3, 1090, 430, 2.4 + .4 * u, 'speaker')
    if v == 'arg_talk': return R.world_scene(min(9.9 + lt, 11.8), 480, 3250, 2.0, 'all')
    if v == 'ven_talk': return R.world_scene(min(12.2 + lt, 13.7), 1080, 3250, 2.0, 'all')
    if v == 'per_talk': return R.world_scene(min(14.2 + lt, 16.1), 1680, 3250, 2.0, 'all')
    if v == 'rule_vote': return R.scene_vote_rule(22.3 + 4.9 * u)
    if v == 'rule_resist': return R.scene_resist(27.3 + min(lt, 3.6))
    if v == 'rule_elim': return R.scene_resist(min(31.3 + lt * .9, 33.6))
    if v == 'thermo': return R.scene_termo_rules(34.0 + 5.0 * u)
    if v == 'obj_axe': return obj2(lt, dur)
    if v == 'obj_lighter': return R.obj_scene(lt, 0, dur, 'lighter', 'ENCENDEDOR', 940, 0, 800, spark=dur * .55)
    if v == 'obj_map': return R.obj_scene(lt, 0, dur, 'map', 'MAPA', 820, 0, 900)
    if v == 'obj_candles': return R.obj_scene(lt, 0, dur, 'candles', 'CINCO VELAS', 920, 0)
    if v == 'obj_wet': return R.obj_scene(lt, 0, dur, 'wet', 'TRONCOS HÚMEDOS', 980, -4)
    if v == 'obj_dry': return R.obj_scene(lt, 0, dur, 'dry', 'TRES LEÑOS SECOS', 980, 4)
    if v == 'note': return R.note_scene(50.0 + lt)
    if v == 'opt_A': return R.scene_options(65.4 + min(lt, 1.5))
    if v == 'opt_B': return R.scene_options(69.2 + min(lt, 1.5))
    if v == 'opt_C': return R.scene_options(72.7 + min(lt, 1.5))
    if v == 'ask': return ask(lt)
    if v == 'cta_comment': return R.scene_cta(78.0 + min(lt * 1.2, 2.85))
    if v == 'cta_24h': return R.scene_cta(81.0 + 4.2 * u)
    return R.scene_cta(85.6)

def frame(i):
    T = i / FPS
    sc = next((s for s in SC if T < s[3]), SC[-1]); v, tit, st, en = sc; lt = max(0, T - st); dur = en - st
    a = np.clip(visual(v, T, lt, dur), 0, 255)
    if lt < 3 / FPS and st > .2: a = a * (.45 + .55 * lt * FPS / 3)
    fr = .1 + .1 * T / DUR
    a = a * R.VIG * (1 + .03 * math.sin(T * 23 + 1.3)) * np.array([.96, 1.0, 1.06], np.float32)[None, None, :]
    a = a + R.FROST * fr * np.array([60, 85, 110], np.float32) + R.GRAIN[i % 6]
    a = np.clip(a * min(1, (T + .05) / .2) * min(1, (DUR - T) / .6), 0, 255).astype(np.uint8)
    im = Image.fromarray(a); d = ImageDraw.Draw(im, 'RGBA')
    if v in BANDS and tit:
        sh = 5 * math.sin(T * 50) if v == 'hook_lighter' and int(T * 5) % 2 == 0 else 0
        f = fit(tit, 940, 120); wd = f.getlength(tit)
        d.rounded_rectangle((540 - wd / 2 - 40, 200, 540 + wd / 2 + 40, 360), 28, fill=(0, 0, 0, 170))
        text_c(d, (540 + sh, 280), tit, f, (225, 40, 40) if v in ('hook_lighter', 'cta_end') else (245, 245, 240), 6)
    if v not in ('thermo', 'hook_lighter', 'ask') and T > 6:
        temp = 6.0 - 1.5 * (T - 6) / (DUR - 6)
        d.rounded_rectangle((36, 60, 250, 140), 24, fill=(0, 0, 0, 160)); text_c(d, (143, 100), f'{temp:.1f}°C', font(52, 'ExtraBold'), (150, 200, 245))
    for t0, t1, s, who in CAPS:
        if t0 - .05 <= T < t1 + .3:
            if s.startswith(('A. ', 'B. ', 'C. ')) or v == 'note': break
            if who != 'n': s = {'arg': 'ARGENTINA', 'ven': 'VENEZUELA', 'per': 'PERÚ'}[who] + ': «' + s + '»'
            f = font(64, 'ExtraBold'); ls = R.wrap(s, f, 900); y = 1440 - (len(ls) - 1) * 40; wmax = max(f.getlength(l) for l in ls)
            d.rounded_rectangle((540 - wmax / 2 - 30, y - 46, 540 + wmax / 2 + 30, y + 80 * (len(ls) - 1) + 50), 28, fill=(0, 0, 0, 170))
            for l in ls: d.text((540, y), l, font=f, fill=(255, 255, 250), anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0)); y += 80
            break
    return im.tobytes()

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; sh = Image.new('RGB', (4 * 360, ((len(ts) + 3) // 4) * 640))
        for j, t in enumerate(ts): sh.paste(Image.frombytes('RGB', (W, H), frame(int(t * FPS))).resize((360, 640)), ((j % 4) * 360, (j // 4) * 640))
        sh.save('v4/sheet.jpg', quality=80)
    else:
        n = int(DUR * FPS); p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', 'v4/mix.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-maxrate', '8M', '-bufsize', '16M', '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-13:TP=-1:LRA=7', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', sys.argv[1]], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for k, b in enumerate(pool.imap(frame, range(n), chunksize=6)):
                p.stdin.write(b)
                if k % 300 == 0: print(k, n, flush=True)
        p.stdin.close(); p.wait()

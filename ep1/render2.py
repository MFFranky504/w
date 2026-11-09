import sys, math, subprocess, numpy as np
from multiprocessing import Pool
import render as R
from lib import *
FPS = 24; DUR = 64.5
import json
DUR = 74.8
SEGS = [(6.4,10.4,5.6,1.0),(10.4,15.4,22.0,1.06),(15.4,21.4,27.3,1.067),(21.4,27.4,33.7,0.917),(27.4,28.5,39.2,1.0),(28.5,31.6,40.3,1.129),(31.6,32.7,43.8,1.09),(32.7,35.2,45.0,0.76),(35.2,36.3,46.9,1.0),(36.3,37.3,48.0,1.0),(37.3,38.3,49.0,1.0),(38.3,52.3,50.0,1.0),(52.3,53.2,None,0),(53.2,64.45,64.0,1.0),(64.45,71.85,77.9,1.0),(71.85,74.9,85.3,0.8)]
PLACE = json.load(open('place.json'))

def subs(im, T):
    for t0, t1, s in PLACE:
        if t0 - .05 <= T < t1 + .25:
            d = ImageDraw.Draw(im, 'RGBA'); f = font(64, 'ExtraBold'); ls = R.wrap(s, f, 900); y = 1440 - (len(ls) - 1) * 40
            wmax = max(f.getlength(l) for l in ls)
            d.rounded_rectangle((540 - wmax / 2 - 30, y - 46, 540 + wmax / 2 + 30, y + 80 * (len(ls) - 1) + 50), 28, fill=(0, 0, 0, 165))
            for l in ls: d.text((540, y), l, font=f, fill=(255, 255, 250), anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0)); y += 80
            break
    return im

def pause_scene(Tn):
    im = Image.new('RGB', (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
    text_c(d, (540, 900), '¿QUÉ HACES?', font(170, 'Black'), (245, 245, 240), 8); d.rectangle((140, 1020, 940, 1030), fill=(200, 30, 30))
    return np.array(im, np.float32)

def hook(Tn):
    if Tn < 1.6: arr = R.obj_scene(42.4 + Tn * .6, 40.3, 43.8, 'lighter', '', 940 + 90 * Tn, 0, 800, spark=42.6 if Tn < .5 else None)
    elif Tn < 3.2: arr = R.world_scene(Tn + 2.0, *R.kf(Tn, [(1.6, 1080, 3100, 1.0), (3.2, 1080, 3000, 1.45)]), 'all')
    elif Tn < 4.6: arr = R.termo_scene(Tn, 6.0 - 1.6 * ease((Tn - 3.4) / 1.2))
    else: arr = R.obj_scene(40.5 + (Tn - 4.6) * .8, 40.3, 43.8, 'lighter', '', 1000 + 60 * (Tn - 4.6), 0, 760, spark=None)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    sh = 6 * math.sin(Tn * 55) if int(Tn * 5) % 2 == 0 else 0
    if Tn < 4.6:
        d.rounded_rectangle((60, 190, 1020, 600), 30, fill=(0, 0, 0, 160))
        text_c(d, (540 + sh, 320), 'UNA SOLA', font(170, 'Black'), (245, 245, 240), 8); text_c(d, (540 - sh, 490), 'CHISPA.', font(170, 'Black'), (225, 40, 40), 8)
    else:
        d.rounded_rectangle((40, 1010, 1040, 1230), 30, fill=(0, 0, 0, 170))
        text_c(d, (540 + sh, 1120), '¿LA GASTAS?', font(160, 'Black'), (245, 245, 240), 8)
    return np.array(im, np.float32)

def scene(Tn):
    if Tn < 6.0: return hook(Tn), 5.0 + Tn
    for n0, n1, o0, sp in SEGS:
        if Tn < n1:
            if o0 is None: return pause_scene(Tn), 63.0
            To = o0 + (Tn - n0) * sp; return R.render(To), To
    To = 87.3; return R.render(To), To

def frame(i):
    Tn = i / FPS; arr, To = scene(Tn)
    a = np.clip(arr, 0, 255)
    cuts = [1.6, 3.2, 4.6, 6.4, 52.3, 53.2]
    for c in cuts:
        if 0 <= Tn - c < .12: a = a * .6 + 150 * (1 - (Tn - c) / .12) * .4 + a * 0
    fr = .25 if Tn < 6 else min(.55, max(0, (To - 33.7) / 60))
    if 33.7 <= To < 39.2: fr = .35 + .3 * ease((To - 36.5) / 2.7)
    a = a * R.VIG * (1 + .035 * math.sin(Tn * 23 + 1.3) + .02 * math.sin(Tn * 7))
    a = a * np.array([.96, 1.0, 1.06], np.float32)[None, None, :]
    a = a + R.FROST * fr * np.array([70, 100, 130], np.float32) * 0.8 + R.GRAIN[i % 6]
    a = np.clip(a * min(1, (Tn + .05) / .15) * min(1, (DUR - Tn) / .5), 0, 255).astype(np.uint8)
    im = Image.fromarray(a); im = subs(im, Tn) if not (52.3 <= Tn < 53.2) else im
    return im.tobytes()

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; sheet = Image.new('RGB', (4 * 360, ((len(ts) + 3) // 4) * 640))
        for j, t in enumerate(ts): sheet.paste(Image.frombytes('RGB', (W, H), frame(int(t * FPS))).resize((360, 640)), ((j % 4) * 360, (j // 4) * 640))
        sheet.save('sheet2.jpg', quality=80)
    else:
        n = int(DUR * FPS); p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for k, b in enumerate(pool.imap(frame, range(n), chunksize=6)):
                p.stdin.write(b)
                if k % 200 == 0: print(k, n, flush=True)
        p.stdin.close(); p.wait()

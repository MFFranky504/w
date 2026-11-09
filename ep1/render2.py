import sys, math, subprocess, numpy as np
from multiprocessing import Pool
import render as R
from lib import *
FPS = 24; DUR = 64.5
SEGS = [(6.0,9.4,6.2,1.0),(9.4,13.4,22.0,1.325),(13.4,17.9,27.3,1.42),(17.9,21.4,33.7,1.57),(21.4,22.1,39.2,1.57),(22.1,24.1,40.3,1.75),(24.1,24.9,43.8,1.5),(24.9,26.8,45.0,1.0),(26.8,27.6,46.9,1.375),(27.6,28.4,48.0,1.25),(28.4,29.2,49.0,1.25),(29.2,43.2,50.0,1.0),(43.2,54.45,64.0,1.0),(54.45,61.85,77.9,1.0),(61.85,64.6,85.3,0.8)]
SUBS2 = [(.2,1.5,'Diez países.'),(1.6,3.0,'Una cabaña helada.'),(3.1,4.4,'Una sola chispa.'),(4.7,6.0,'¿Tú qué harías?'),(6.3,8.1,'Nadie sabe por qué están aquí.'),(8.4,9.3,'Yo sí.'),
 (9.5,10.9,'Una decisión por país.'),(11.1,12.9,'Ustedes deciden.'),(13.5,15.0,'Cien de resistencia.'),(15.3,17.4,'Cero... eliminado.'),(18.0,21.3,'La cabaña se congela: tres grados menos cada hora.'),
 (21.45,22.2,'Un hacha.'),(22.3,24.0,'Un encendedor.'),(24.95,25.8,'Un cuchillo.'),(25.85,27.2,'Un mapa.'),(27.25,28.0,'Cinco velas.'),(28.05,28.8,'Troncos húmedos.'),(28.85,29.6,'Tres leños secos.'),
 (29.4,30.2,'Y una nota.'),(30.6,31.9,'Léanla con cuidado.'),(32.15,34.8,'El frío no se vence con fuerza.'),(34.9,36.4,'Lo que pesa, no te salvará.'),(36.6,41.0,'Lo que brilla poco, gástalo una sola vez, y donde más dure.'),(41.6,43.1,'El humo conoce la salida.'),
 (43.5,44.6,'Tres caminos.'),(44.8,48.2,'A: la chimenea, con los leños secos.'),(48.6,51.7,'B: el muro, con el hacha.'),(52.1,54.3,'C: las cinco velas.'),
 (54.6,57.2,'Escriban país y letra en los comentarios.'),(57.55,59.2,'Veinticuatro horas.'),(59.55,61.85,'Después... no habrá marcha atrás.'),(62.0,64.0,'¿Qué país caerá primero?')]
R.SUBS = SUBS2

def hook(Tn):
    if Tn < 1.0: arr = R.obj_scene(42.5 + Tn, 40.3, 43.8, 'lighter', '', 940 + 120 * Tn, 0, 800, spark=42.6)
    elif Tn < 2.0: arr = R.world_scene(Tn + 3.0, *R.kf(Tn, [(1.0, 1080, 3100, 1.0), (2.0, 1080, 3000, 1.5)]), 'all')
    elif Tn < 3.0: arr = R.world_scene(8.3, 1090, 430, 2.6 + (Tn - 2) * .8, 'speaker')
    elif Tn < 4.2: arr = R.termo_scene(Tn, 6.0 - 1.6 * ease((Tn - 3.0) / 1.2))
    else: arr = R.obj_scene(40.5 + (Tn - 4.2) * 1.6, 40.3, 43.8, 'lighter', '', 1000 + 80 * (Tn - 4.2), 0, 760, spark=None)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    sh = 8 * math.sin(Tn * 55) if int(Tn * 5) % 2 == 0 else 0
    if Tn < 4.2:
        d.rounded_rectangle((60, 190, 1020, 600), 30, fill=(0, 0, 0, 150))
        text_c(d, (540 + sh, 320), 'UNA SOLA', font(170, 'Black'), (245, 245, 240), 8); text_c(d, (540 - sh, 490), 'CHISPA.', font(170, 'Black'), (225, 40, 40), 8)
    else:
        d.rounded_rectangle((40, 1010, 1040, 1230), 30, fill=(0, 0, 0, 170))
        text_c(d, (540 + sh, 1120), '¿LA GASTAS?', font(160, 'Black'), (245, 245, 240), 8)
    return np.array(im, np.float32)

def scene(Tn):
    if Tn < 6.0: return hook(Tn), 5.0 + Tn
    for n0, n1, o0, sp in SEGS:
        if Tn < n1:
            To = o0 + (Tn - n0) * sp; return R.render(To), To
    To = 87.3; return R.render(To), To

def frame(i):
    Tn = i / FPS; arr, To = scene(Tn)
    a = np.clip(arr, 0, 255)
    cuts = [1.0, 2.0, 3.0, 4.2, 6.0]
    for c in cuts:
        if 0 <= Tn - c < .12: a = a * .6 + 150 * (1 - (Tn - c) / .12) * .4 + a * 0
    fr = .25 if Tn < 6 else min(.55, max(0, (To - 33.7) / 60))
    if 33.7 <= To < 39.2: fr = .35 + .3 * ease((To - 36.5) / 2.7)
    a = a * R.VIG * (1 + .035 * math.sin(Tn * 23 + 1.3) + .02 * math.sin(Tn * 7))
    a = a * np.array([.96, 1.0, 1.06], np.float32)[None, None, :]
    a = a + R.FROST * fr * np.array([70, 100, 130], np.float32) + R.GRAIN[i % 6]
    a = np.clip(a * min(1, (Tn + .05) / .15) * min(1, (DUR - Tn) / .5), 0, 255).astype(np.uint8)
    im = Image.fromarray(a); im = R.subs(im, Tn)
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

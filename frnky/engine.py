"""Motor de render: cámara, subtítulos, gancho (0-2 s), CTA (últimos 2 s), audio y MP4."""
import math
import pathlib
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import audio
from .config import CTA_SECONDS, HOOK_SECONDS
from PIL import ImageChops, ImageFilter
from .bg import W, H

FPS, SCALE = 24, 3
LOOP_FADE = 0.45     # segundos finales en los que el CTA se funde con el gancho inicial
OUT = (W * SCALE, H * SCALE)
FONT_PATH = str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Jersey10-Regular.ttf")  # OFL


def pf(size):
    """Jersey 10: fuente pixel art con ¡ ¿ ñ y tildes bien distinguibles (la C no se confunde con la O)."""
    return ImageFont.truetype(FONT_PATH, int(size * 1.35))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def cam_at(keys, t):
    """keys: [(t, k, fx, fy)], k = unidades de recorte (30 = plano completo)."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = smooth((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * u for i in (1, 2, 3))
    return keys[-1][1:]


def apply_cam(img, k, fx, fy, shake=0, t=0, smooth_=False):
    k = max(20, min(40, round(k)))
    w, h = 9 * k, 16 * k
    ox = round(math.sin(t * 70) * shake) if shake else 0
    oy = round(math.cos(t * 53) * shake) if shake else 0
    x0 = int(max(0, min(W - w, fx - w / 2 + ox)))
    y0 = int(max(0, min(H - h, fy - h / 2 + oy)))
    return img.crop((x0, y0, x0 + w, y0 + h)).resize(OUT, Image.LANCZOS if smooth_ else Image.NEAREST)


def draw_line(img, xy, s, font, fill, anchor="lm", stroke=0, stroke_fill=None):
    """Dibuja texto; la fuente pixel no distingue «¡» de «i», así que se dibuja como «!» girada 180°."""
    d = ImageDraw.Draw(img)
    if "¡" not in s:
        d.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)
        return
    segs = [p for p in s.replace("¡", "\x00¡\x00").split("\x00") if p]
    widths = [d.textlength("!" if p == "¡" else p, font=font) for p in segs]
    x, y = xy
    x0 = x - sum(widths) / 2 if anchor[0] == "m" else x
    for p, w in zip(segs, widths):
        if p == "¡":
            th = int(font.size * 2)
            tile = Image.new("RGBA", (int(w) + 24, th), (0, 0, 0, 0))
            ImageDraw.Draw(tile).text((12, th / 2), "!", font=font, fill=fill, anchor="lm")
            bb = tile.getbbox()
            if bb:
                flipped = Image.new("RGBA", tile.size, (0, 0, 0, 0))
                flipped.paste(tile.crop(bb).rotate(180), (bb[0], bb[1]))
                img.paste(flipped, (int(x0 - 12), int(y - th / 2 + font.size * 0.22)), flipped)  # baja bajo la línea base
        else:
            d.text((x0, y), p, font=font, fill=fill, anchor="lm", stroke_width=stroke, stroke_fill=stroke_fill)
        x0 += w


def _wrap(draw, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        tr = (cur + " " + w).strip()
        if draw.textlength(tr, font=font) <= width:
            cur = tr
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def text_block(img, text, cy, size, fill, stroke=10, width=940, line_gap=1.12, stroke_fill=(10, 8, 20)):
    d = ImageDraw.Draw(img)
    f = pf(size)
    lines = _wrap(d, text, f, width)
    y = cy - (len(lines) - 1) * size * line_gap / 2
    for ln in lines:
        draw_line(img, (OUT[0] / 2, y), ln, f, fill, "mm", stroke, stroke_fill)
        y += size * line_gap


_VIG = None


def post_fx(img):
    """Bloom suave + viñeta + ligero contraste, para el look 'HD pixel' tipo SNES."""
    global _VIG
    small = img.resize((OUT[0] // 4, OUT[1] // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    bloom = small.resize(OUT, Image.BILINEAR)
    img = Image.blend(img, ImageChops.screen(img, bloom), 0.22)
    if _VIG is None:
        yy, xx = np.mgrid[0:OUT[1], 0:OUT[0]]
        r = np.sqrt(((xx - OUT[0] / 2) / (OUT[0] / 2)) ** 2 + ((yy - OUT[1] / 2) / (OUT[1] / 2)) ** 2)
        _VIG = (1 - 0.38 * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None].astype("float32")
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(1.25)
    a = np.asarray(img, dtype="float32") * _VIG
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def kawaii_fx(img, t):
    """Look kawaii: pasteles suaves, resplandor cálido, viñeta rosada y corazones/estrellas flotando."""
    a = np.asarray(img, dtype="float32")
    a = a * 0.86 + 34                                   # sombras levantadas (más pastel)
    a[..., 0] *= 1.03; a[..., 2] *= 1.02
    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))
    glow = img.filter(ImageFilter.GaussianBlur(14))
    img = Image.blend(img, ImageChops.screen(img, glow), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    rnd = np.random.default_rng(7)
    for k in range(9):                                 # corazones y estrellas que suben despacio
        x = (rnd.random() * OUT[0] + math.sin(t * 0.9 + k) * 26) % OUT[0]
        y = OUT[1] - ((t * 90 + rnd.random() * OUT[1]) % (OUT[1] + 80)) + 20
        if 330 < y < 1050 or y > 1500:
            continue
        r = 14 + 6 * math.sin(t * 3 + k)
        if k % 2:
            d.ellipse([x - r, y - r, x, y], fill=(255, 150, 190, 150)); d.ellipse([x, y - r, x + r, y], fill=(255, 150, 190, 150))
            d.polygon([(x - r, y - r / 2), (x + r, y - r / 2), (x, y + r)], fill=(255, 150, 190, 150))
        else:
            d.polygon([(x, y - r), (x + r / 3, y - r / 3), (x + r, y), (x + r / 3, y + r / 3), (x, y + r), (x - r / 3, y + r / 3), (x - r, y), (x - r / 3, y - r / 3)], fill=(255, 240, 150, 170))
    return img


def rpg_box(img, who_label, color, text, shown, flag=None, y0=1150, y1=1370, gold=False):
    """Caja de diálogo estilo JRPG con etiqueta de nombre y texto que se escribe solo."""
    layer = Image.new("RGBA", OUT, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fill, edge = ((40, 32, 14, 246), (206, 172, 92, 255)) if gold else ((22, 28, 78, 244), (214, 218, 236, 255))
    d.rounded_rectangle([64, y0, 930, y1], radius=26, fill=fill, outline=edge, width=7)
    d.rounded_rectangle([80, y0 + 16, 914, y1 - 16], radius=18, outline=(120, 130, 230, 255) if not gold else (190, 140, 30, 255), width=3)
    if who_label:
        f = pf(32)
        fw = 60 if flag else 0
        tw = d.textlength(who_label, font=f) + 44 + fw
        d.rounded_rectangle([80, y0 - 40, 80 + tw, y0 + 10], radius=12, fill=color + (255,), outline=(20, 16, 40, 255), width=5)
        d.text((80 + fw + (tw - fw) / 2, y0 - 15), who_label, font=f, fill=(30, 20, 40), anchor="mm")
        if flag:  # bandera del país del personaje
            fx0, fy0, fx1, fy1 = 96, y0 - 28, 96 + 42, y0 - 2
            for (a, b, c2, d2_, col) in flag:
                d.rectangle([fx0 + a * 42, fy0 + b * 26, fx0 + c2 * 42 - 1, fy0 + d2_ * 26 - 1], fill=col)
            d.rectangle([fx0, fy0, fx1, fy1], outline=(20, 16, 40, 255), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))
    d2 = ImageDraw.Draw(img)
    f = pf(70 if gold else 56)
    vis = text[:shown]
    lines = _wrap(d2, text, f, 700 if gold else 760)
    # respeta el salto de línea de la frase completa para que no "baile" al escribirse
    y = (y0 + y1) / 2 - (len(lines) - 1) * (42 if gold else 34)
    left = shown
    for ln in lines:
        draw_line(img, (497 if gold else 104, y), ln[:max(0, left)], f,
                  (255, 255, 255) if not gold else (255, 236, 130), "mm" if gold else "lm")
        left -= len(ln) + 1
        y += 84 if gold else 68


def title_card(img, text, cy, size=80, width=860):
    """Cartel de título con placa oscura: se lee sobre cualquier fondo (marcador, caras)."""
    d = ImageDraw.Draw(img)
    f = pf(size)
    lines = _wrap(d, text, f, width)
    lw = max(d.textlength(l, font=f) for l in lines)
    h = len(lines) * size * 1.15
    layer = Image.new("RGBA", OUT, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle([OUT[0] / 2 - lw / 2 - 44, cy - h / 2 - 26, OUT[0] / 2 + lw / 2 + 44, cy + h / 2 + 26],
                                            radius=28, fill=(14, 16, 44, 225), outline=(226, 186, 90, 255), width=6)
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))
    text_block(img, text, cy, size, (252, 224, 110), stroke=0, width=width, line_gap=1.15)


def hud(img, items):
    """HUD de píldoras bajo la caja de diálogo (no tapa marcadores ni caras). items = [(etiqueta, valor), ...]"""
    d = ImageDraw.Draw(img)
    f = pf(30)
    cols = [(255, 214, 90), (255, 140, 180)]
    x, y = 64, 1388
    for k, (label, val) in enumerate(items[:2]):
        s_ = f"{label} {val}"
        w = d.textlength(s_, font=f) + 30
        d.rounded_rectangle([x, y, x + w, y + 44], radius=12, fill=(20, 22, 56), outline=cols[k], width=3)
        d.text((x + w / 2, y + 22), s_, font=f, fill=cols[k], anchor="mm")
        x += w + 14


def render_video(ep, cta, out_mp4, workdir):
    """ep: dict con T, hook, lines, cuts, voices, frame(t)->(canvas,cam,shake), music(track), sfx(track)."""
    work = pathlib.Path(workdir); work.mkdir(parents=True, exist_ok=True)
    T = ep["T"]
    n = int(round(T * FPS))
    voices = ep["voices"]
    lines = ep["lines"]
    # Reglas del canal, verificadas al renderizar:
    assert lines[0][0] < 0.5 and ep["hooks"][0][0] == 0 and ep["hooks"][0][1] <= HOOK_SECONDS + 0.5, "el conflicto debe verse desde el segundo 0"
    cta_t0 = T - CTA_SECONDS
    assert all(l[1] <= cta_t0 + 0.01 for l in lines), "ningún diálogo puede pisar el CTA final"

    # --- audio ---
    nA = int(round(n / FPS * audio.SR))           # audio = exactamente los fotogramas del video
    track = np.zeros(nA + int(4 * audio.SR))
    ep["music"](track)
    for c in ep["cuts"]:
        audio.hit(track, c)
        audio.whoosh(track, max(0, c - 0.22))
    for t0, t1, who, text in lines:
        for v in who.split("+"):
            audio.voice(track, (t0, t1, text), voices[v]["pitch"])
    ep["sfx"](track)
    audio.ding(track, cta_t0 + 0.05)
    tail = track[nA:]                                  # bucle de audio: la cola (pads, eco) cae sobre el inicio
    track = track[:nA]
    track[:len(tail)] += tail
    wav = work / "audio.wav"
    audio.save(track, wav)

    # --- video ---
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{OUT[0]}x{OUT[1]}", "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out_mp4)]
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    saved = {}
    cs, cv = None, [0.0, 0.0, 0.0]          # cámara con resorte críticamente amortiguado
    for i in range(n):
        t = i / FPS
        canvas, cam, shake = ep["frame"](t)
        k = cam[0]
        for te, amp in ep.get("punches", ()):          # "golpes" de zoom al empezar cada frase y cada corte
            if 0 <= t - te < 1.0:
                k -= amp * math.exp(-(t - te) * 7)
        tgt = [k, cam[1], cam[2]]
        if cs is None or any(0 <= t - c < 1.5 / FPS for c in ep["cuts"]):
            cs, cv = tgt[:], [0.0, 0.0, 0.0]      # en cada corte la cámara salta (lo tapa el destello)
        else:
            for _ in range(4):                     # zoom con ease-in/ease-out: entra y sale suave
                h = 1 / FPS / 4
                for q in range(3):
                    cv[q] += (170 * (tgt[q] - cs[q]) - 26 * cv[q]) * h
                    cs[q] += cv[q] * h
        cam = tuple(cs)
        kaw = ep.get("style") == "kawaii"
        img = post_fx(apply_cam(canvas.convert("RGB"), *cam, shake=shake, t=t, smooth_=kaw))
        if kaw:
            img = kawaii_fx(img, t)
        for c in ep["cuts"]:                       # glitch cromático (RGB split) breve en cada corte
            if 0 <= t - c < 0.17:
                dx = int(8 * (1 - (t - c) / 0.17))
                a_ = np.asarray(img).copy()
                a_[..., 0] = np.roll(a_[..., 0], dx, axis=1); a_[..., 2] = np.roll(a_[..., 2], -dx, axis=1)
                img = Image.fromarray(a_)
        if "hud" in ep:
            hud(img, ep["hud"](t))

        def overlays(im, tt, cta_on):
            bt = ep["banner"](tt) if "banner" in ep else ""
            if bt:
                title_card(im, bt, 330, 84 if len(bt) < 9 else 64, 900)
            for t0, t1, who, text in lines:        # diálogo estilo RPG (se escribe letra por letra)
                if t0 <= tt < t1:
                    col = voices[who.split("+")[0]]["color"] if "+" not in who else (255, 255, 255)
                    tag = " + ".join(voices[v]["label"] for v in who.split("+"))
                    frac = min(1.0, (tt - t0) / (0.3 * (t1 - t0)))
                    shown = int(len(text) * (max(frac, 0.5) if t0 < 0.5 else frac)) + 1
                    rpg_box(im, tag, col, text, shown, flag=None if '+' in who else voices[who].get('flag'))
            for h0, h1, htext in ep["hooks"]:      # gancho: ya está en el fotograma 0
                if h0 <= tt < h1:
                    pop = 1 + 0.08 * math.sin(min((tt - h0) / 0.25, 1) * math.pi)
                    title_card(im, htext, 330, int(62 * pop), 900)
            if cta_on:                             # CTA en los últimos segundos (caja RPG dorada)
                u = tt - cta_t0
                pop = 1 + 0.06 * math.sin(min(u, 0.3) / 0.3 * math.pi)
                hh = int(116 * pop)
                rpg_box(im, "MISIÓN", (255, 214, 70), cta, len(cta), y0=1260 - hh, y1=1260 + hh, gold=True)
            return im

        if t >= T - LOOP_FADE:
            # BUCLE SIN COSTURA: la escena ya es idéntica al fotograma 0; solo los carteles hacen crossfade
            # (CTA -> gancho inicial), así el último fotograma == el primero.
            a_img = overlays(img.copy(), t, True)
            b_img = overlays(img.copy(), 0.0, False)
            u = smooth((t - (T - LOOP_FADE)) / (LOOP_FADE - 1 / FPS))
            img = Image.blend(a_img, b_img, u)
        else:
            img = overlays(img, t, t >= cta_t0)
        for c in ep["cuts"]:                       # flash en cada corte
            if 0 <= t - c < 2.5 / FPS:
                white = Image.new("RGB", OUT, (255, 255, 255))
                img = Image.blend(img, white, 0.65 if t - c < 1 / FPS else 0.3)
        if i in (0, int(n * 0.25), int(n * 0.55), int(n * 0.9), n - 1):
            saved[i] = img.copy()
        pipe.stdin.write(img.tobytes())
    pipe.stdin.close()
    assert pipe.wait() == 0, "ffmpeg falló"
    for i, im in saved.items():
        im.resize((270, 480), Image.LANCZOS).save(work / f"frame_{i:04d}.png")
    return out_mp4

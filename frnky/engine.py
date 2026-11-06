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
OUT = (W * SCALE, H * SCALE)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


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


def apply_cam(img, k, fx, fy, shake=0, t=0):
    k = max(20, min(40, round(k)))
    w, h = 9 * k, 16 * k
    ox = round(math.sin(t * 70) * shake) if shake else 0
    oy = round(math.cos(t * 53) * shake) if shake else 0
    x0 = int(max(0, min(W - w, fx - w / 2 + ox)))
    y0 = int(max(0, min(H - h, fy - h / 2 + oy)))
    return img.crop((x0, y0, x0 + w, y0 + h)).resize(OUT, Image.NEAREST)


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
    f = ImageFont.truetype(FONT, size)
    lines = _wrap(d, text, f, width)
    y = cy - (len(lines) - 1) * size * line_gap / 2
    for ln in lines:
        d.text((OUT[0] / 2, y), ln, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)
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
    img = ImageEnhance.Color(img).enhance(0.9)
    a = np.asarray(img, dtype="float32") * _VIG
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def rpg_box(img, who_label, color, text, shown, y0=1150, y1=1370, gold=False):
    """Caja de diálogo estilo JRPG con etiqueta de nombre y texto que se escribe solo."""
    layer = Image.new("RGBA", OUT, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fill, edge = ((40, 32, 14, 246), (206, 172, 92, 255)) if gold else ((22, 28, 78, 244), (214, 218, 236, 255))
    d.rounded_rectangle([64, y0, 930, y1], radius=26, fill=fill, outline=edge, width=7)
    d.rounded_rectangle([80, y0 + 16, 914, y1 - 16], radius=18, outline=(120, 130, 230, 255) if not gold else (190, 140, 30, 255), width=3)
    if who_label:
        f = ImageFont.truetype(FONT, 34)
        tw = d.textlength(who_label, font=f) + 44
        d.rounded_rectangle([80, y0 - 40, 80 + tw, y0 + 10], radius=12, fill=color + (255,), outline=(20, 16, 40, 255), width=5)
        d.text((80 + tw / 2, y0 - 15), who_label, font=f, fill=(30, 20, 40), anchor="mm")
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))
    d2 = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 70 if gold else 56)
    vis = text[:shown]
    lines = _wrap(d2, text, f, 700 if gold else 760)
    # respeta el salto de línea de la frase completa para que no "baile" al escribirse
    y = (y0 + y1) / 2 - (len(lines) - 1) * (42 if gold else 34)
    left = shown
    for ln in lines:
        d2.text((497 if gold else 104, y), ln[:max(0, left)], font=f,
                fill=(255, 255, 255) if not gold else (255, 236, 130), anchor="mm" if gold else "lm")
        left -= len(ln) + 1
        y += 84 if gold else 68


def hud(img, level, vibe):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 36)
    for k, (label, val, col) in enumerate((("NIVEL DE BRO", f"{level}", (226, 196, 120)), ("BUENA ONDA", f"{vibe}%", (214, 140, 160)))):
        s = f"{label}: {val}"
        w = d.textlength(s, font=f) + 40
        y = 270 + k * 68
        d.rounded_rectangle([64, y, 64 + w, y + 54], radius=12, fill=(20, 22, 56), outline=col, width=4)
        d.text((84, y + 27), s, font=f, fill=col, anchor="lm")


def render_video(ep, cta, out_mp4, workdir):
    """ep: dict con T, hook, lines, cuts, voices, frame(t)->(canvas,cam,shake), music(track), sfx(track)."""
    work = pathlib.Path(workdir); work.mkdir(parents=True, exist_ok=True)
    T = ep["T"]
    n = int(round(T * FPS))
    voices = ep["voices"]
    lines = ep["lines"]
    # Reglas del canal, verificadas al renderizar:
    assert lines[0][0] <= HOOK_SECONDS and lines[0][0] < 0.5, "el conflicto debe sonar/verse desde el segundo 0"
    cta_t0 = T - CTA_SECONDS
    assert all(l[1] <= cta_t0 + 0.01 for l in lines), "ningún diálogo puede pisar el CTA final"

    # --- audio ---
    track = np.zeros(int(T * audio.SR))
    ep["music"](track)
    for c in ep["cuts"]:
        audio.hit(track, c)
    for t0, t1, who, text in lines:
        for v in who.split("+"):
            audio.voice(track, (t0, t1, text), voices[v]["pitch"])
    ep["sfx"](track)
    audio.ding(track, cta_t0 + 0.05)
    wav = work / "audio.wav"
    audio.save(track, wav)

    # --- video ---
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{OUT[0]}x{OUT[1]}", "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", str(out_mp4)]
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    saved = {}
    for i in range(n):
        t = i / FPS
        canvas, cam, shake = ep["frame"](t)
        img = post_fx(apply_cam(canvas.convert("RGB"), *cam, shake=shake, t=t))
        if "banner" in ep and ep["banner"](t):
            text_block(img, ep["banner"](t), 520, 130, (236, 214, 130), stroke=14)
        if "hud" in ep:
            hud(img, *ep["hud"](t))
        # diálogo estilo RPG (se escribe letra por letra)
        for t0, t1, who, text in lines:
            if t0 <= t < t1:
                col = voices[who.split("+")[0]]["color"] if "+" not in who else (255, 255, 255)
                tag = " + ".join(voices[v]["label"] for v in who.split("+"))
                shown = int(len(text) * min(1.0, (t - t0) / (0.45 * (t1 - t0))) + 1)
                rpg_box(img, tag, col, text, shown)
        # gancho (primeros segundos): arranca ya en el fotograma 0
        if t < HOOK_SECONDS:
            text_block(img, ep["hook"], 592, 72, (236, 214, 130), stroke=11, width=900)
        # flash en cada corte
        for c in ep["cuts"]:
            if 0 <= t - c < 2.5 / FPS:
                white = Image.new("RGB", OUT, (255, 255, 255))
                img = Image.blend(img, white, 0.65 if t - c < 1 / FPS else 0.3)
        # CTA en los últimos segundos (misma caja RPG, en dorado)
        if t >= cta_t0:
            u = t - cta_t0
            pop = 1 + 0.06 * math.sin(min(u, 0.3) / 0.3 * math.pi)
            cy = 1260
            hh = int(116 * pop)
            rpg_box(img, "MISIÓN", (255, 214, 70), cta, len(cta), y0=cy - hh, y1=cy + hh, gold=True)
        if i in (0, int(n * 0.25), int(n * 0.55), int(n * 0.9), n - 1):
            saved[i] = img.copy()
        pipe.stdin.write(img.tobytes())
    pipe.stdin.close()
    assert pipe.wait() == 0, "ffmpeg falló"
    for i, im in saved.items():
        im.resize((270, 480), Image.LANCZOS).save(work / f"frame_{i:04d}.png")
    return out_mp4

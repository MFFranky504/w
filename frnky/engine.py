"""Motor de render: cámara, subtítulos, gancho (0-2 s), CTA (últimos 2 s), audio y MP4."""
import math
import pathlib
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import audio
from .config import CTA_SECONDS, HOOK_SECONDS
from .pixel import W, H

FPS, SCALE = 24, 4
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
    k = max(15, min(30, round(k)))
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
        img = apply_cam(canvas, *cam, shake=shake, t=t)
        # subtítulo
        for t0, t1, who, text in lines:
            if t0 <= t < t1:
                col = voices[who.split("+")[0]]["color"] if "+" not in who else (255, 255, 255)
                tag = " + ".join(voices[v]["label"] for v in who.split("+"))
                text_block(img, tag, 1262, 40, col, stroke=7)
                text_block(img, text, 1370, 74, col)
        # gancho (primeros segundos): arranca ya en el fotograma 0
        if t < HOOK_SECONDS:
            text_block(img, ep["hook"], 395, 92, (255, 235, 90), stroke=12, width=900)
        # flash en cada corte
        for c in ep["cuts"]:
            if 0 <= t - c < 2.5 / FPS:
                white = Image.new("RGB", OUT, (255, 255, 255))
                img = Image.blend(img, white, 0.65 if t - c < 1 / FPS else 0.3)
        # CTA en los últimos segundos
        if t >= cta_t0:
            u = t - cta_t0
            pop = 1 + 0.12 * math.sin(min(u, 0.3) / 0.3 * math.pi) + 0.02 * math.sin(u * 9)
            layer = Image.new("RGBA", OUT, (0, 0, 0, 0))
            dl = ImageDraw.Draw(layer)
            hw, hh = 470 * pop, 190 * pop
            dl.rounded_rectangle([OUT[0] / 2 - hw, 1370 - hh, OUT[0] / 2 + hw, 1370 + hh], radius=46,
                                 fill=(12, 10, 28, 235), outline=(255, 235, 90, 255), width=10)
            img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
            text_block(img, cta.upper(), 1370, int(78 * pop), (255, 235, 90), stroke=8, width=860)
        if i in (0, int(n * 0.25), int(n * 0.55), int(n * 0.9), n - 1):
            saved[i] = img.copy()
        pipe.stdin.write(img.tobytes())
    pipe.stdin.close()
    assert pipe.wait() == 0, "ffmpeg falló"
    for i, im in saved.items():
        im.resize((270, 480), Image.LANCZOS).save(work / f"frame_{i:04d}.png")
    return out_mp4

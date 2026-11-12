#!/usr/bin/env python3
"""Archivo Cero pixel-art engine: storyboard YAML -> narrated, animated MP4.

Usage:
  python3 tools/pixel/engine.py STORYBOARD.yaml            # full render
  python3 tools/pixel/engine.py STORYBOARD.yaml --stills   # one PNG per shot + contact sheet, no encode
  python3 tools/pixel/engine.py STORYBOARD.yaml --short    # also render a 9:16 Short with word captions

Art is drawn by code (tools/pixel/scenes.py) at 640x360 with the fixed 32-colour
palette, then scaled x3 without smoothing. Layers are composed at output
resolution, so camera moves and parallax step in 1/3-pixel increments (fluid 24 fps).
Every frame is a pure function of time: renders are deterministic.
"""
import asyncio, hashlib, json, math, os, subprocess, sys, wave
import numpy as np
import yaml
from PIL import Image, ImageDraw

W, H, S, FPS, SR = 640, 360, 3, 24, 48000
OW, OH = W * S, H * S

# ---------------------------------------------------------------- palette (32)
PALETTE = {
    "black": "050608", "night0": "0b0d14", "night1": "131722", "night2": "1b2131", "night3": "262e42",
    "night4": "344059", "night5": "4b5875", "night6": "6b7a96", "night7": "94a2b8",
    "paper": "c9c6bc", "white": "f4f1ea",
    "hair": "1d1512", "skin0": "2e1d1b", "skin1": "5a3a30", "skin2": "8f5f48", "skin3": "c48a68", "skin4": "e2b48e",
    "lamp0": "2f1e10", "lamp1": "5e3a14", "lamp2": "a3661e", "lamp3": "dfa23c", "lamp4": "f7dc8c",
    "green0": "0a2219", "green1": "155238", "green2": "2f9a5f", "green3": "8fe8a8",
    "red0": "401619", "red1": "7d2a2b", "red2": "bf5546",
    "teal0": "1f3a44", "teal1": "2d5560", "paper_hi": "ece8dc",
}
assert len(PALETTE) == 32
P = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in PALETTE.items()}
PAL = np.array(list(P.values()), dtype=np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


def snap(rgb):
    """Map an (..., 3) uint8 array to the nearest palette colours."""
    flat = rgb.reshape(-1, 3).astype(np.int32)
    d = ((flat[:, None, :] - PAL[None, :, :].astype(np.int32)) ** 2).sum(-1)
    return PAL[d.argmin(1)].reshape(rgb.shape)


def C(name, a=255):
    return P[name] + (a,)


def layer(w=W, h=H):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def bayer(w, h, x0=0, y0=0):
    ys, xs = np.mgrid[y0:y0 + h, x0:x0 + w]
    return BAYER[ys % 4, xs % 4]


def ramp_fill(img, t, ramp, mask=None, x0=0, y0=0):
    """Paint img[y0:, x0:] from a 0..1 value map `t` with ordered dither over a colour ramp.
    t < 0 leaves the pixel untouched; `mask` (bool) limits the area."""
    h, w = t.shape
    a = np.array(img)
    idx = np.floor(np.clip(t, 0, 1) * (len(ramp) - 1) + bayer(w, h, x0, y0)).astype(int).clip(0, len(ramp) - 1)
    cols = np.array([P[c] + (255,) if c else (0, 0, 0, 0) for c in ramp], dtype=np.uint8)[idx]
    keep = np.array([c is not None for c in ramp])[idx]  # None in a ramp = leave pixel as is
    m = (t >= 0) & keep if mask is None else (mask & (t >= 0) & keep)
    view = a[y0:y0 + h, x0:x0 + w]
    view[m[:view.shape[0], :view.shape[1]]] = cols[:view.shape[0], :view.shape[1]][m[:view.shape[0], :view.shape[1]]]
    img.paste(Image.fromarray(a))


def gradient(img, box, ramp, axis="y", mask=None):
    x0, y0, x1, y1 = box
    ys, xs = np.mgrid[0:y1 - y0, 0:x1 - x0]
    t = ys / max(1, y1 - y0 - 1) if axis == "y" else xs / max(1, x1 - x0 - 1)
    ramp_fill(img, t, ramp, None if mask is None else mask[y0:y1, x0:x1], x0, y0)


def glow(img, cx, cy, r, ramp, strength=1.0, sy=1.0):
    """Radial dithered light: inner pixels take the brightest ramp colours, edge keeps the pixel."""
    ramp = [None] + list(ramp)
    x0, y0 = int(cx - r), int((cy - r * sy))
    ys, xs = np.mgrid[y0:int(cy + r * sy) + 1, x0:int(cx + r) + 1]
    d = np.sqrt(((xs - cx) / r) ** 2 + ((ys - cy) / (r * sy)) ** 2)
    t = (1 - d) * strength
    t[t <= 0.08] = -1
    # clip to image
    ox, oy = max(0, -x0), max(0, -y0)
    t = t[oy:, ox:][: img.height - max(0, y0), : img.width - max(0, x0)]
    ramp_fill(img, t, ramp, None, max(0, x0), max(0, y0))


def mask_of(size, draw_fn):
    m = Image.new("L", size, 0)
    draw_fn(ImageDraw.Draw(m))
    return np.array(m) > 0


# ------------------------------------------------------------------ pixel font
G = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#", "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.", "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####", "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####", "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.", "J": "..###|...#.|...#.|...#.|#..#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.", "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.", "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.", "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#", "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####", "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": ".###.|#....|#....|####.|#...#|#...#|.###.", "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.", "9": ".###.|#...#|#...#|.####|....#|....#|.###.",
    ".": ".....|.....|.....|.....|.....|.....|..#..", ",": ".....|.....|.....|.....|.....|..#..|.#...",
    ":": ".....|..#..|.....|.....|.....|..#..|.....", "·": ".....|.....|.....|..#..|.....|.....|.....",
    "-": ".....|.....|.....|.###.|.....|.....|.....", "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "¿": "..#..|.....|..#..|.#...|#....|#...#|.###.", "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "¡": "..#..|.....|..#..|..#..|..#..|..#..|..#..", " ": ".....|.....|.....|.....|.....|.....|.....",
    "'": "..#..|..#..|.....|.....|.....|.....|.....", '"': ".#.#.|.#.#.|.....|.....|.....|.....|.....",
}
ACCENT = {"Á": ("A", "...#.|..#.."), "É": ("E", "...#.|..#.."), "Í": ("I", "...#.|..#.."),
          "Ó": ("O", "...#.|..#.."), "Ú": ("U", "...#.|..#.."), "Ñ": ("N", ".##.#|#.##."), "Ü": ("U", ".....|.#.#.")}


def text_px(s):
    """Pixel list [(x, y)] for a string at scale 1; y may be -2/-1 for accents."""
    pts = []
    for i, ch in enumerate(s.upper()):
        base, acc = ACCENT.get(ch, (ch, None))
        rows = G.get(base, G["?"]).split("|")
        for y, row in enumerate((acc.split("|") if acc else []), start=-2):
            pts += [(i * 6 + x, y) for x, c in enumerate(row) if c == "#"]
        for y, row in enumerate(rows):
            pts += [(i * 6 + x, y) for x, c in enumerate(row) if c == "#"]
    return pts


def text_width(s, scale=1, bold=False):
    return (len(s) * 6 - 1 + (1 if bold else 0)) * scale


def draw_text(img, x, y, s, color, scale=1, bold=False, outline=None):
    d = ImageDraw.Draw(img)
    pts = text_px(s)
    offs = [(0, 0), (1, 0)] if bold else [(0, 0)]
    if outline:
        ring = [(dx, dy) for dx in (-1, 0, 1, 2 if bold else 1) for dy in (-1, 0, 1)]
        for px, py in pts:
            for dx, dy in ring:
                d.rectangle([x + (px + dx) * scale, y + (py + dy) * scale,
                             x + (px + dx + 1) * scale - 1, y + (py + dy + 1) * scale - 1], fill=C(outline))
    for px, py in pts:
        for ox, oy in offs:
            d.rectangle([x + (px + ox) * scale, y + (py + oy) * scale,
                         x + (px + ox + 1) * scale - 1, y + (py + oy + 1) * scale - 1], fill=C(color))


# ------------------------------------------------------------------- timing
def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def interp(v, u):
    """[a, b] -> eased value at u; scalars pass through."""
    if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return v[0] + (v[1] - v[0]) * ease(u)
    return v


async def _tts(text, voice, rate, out_mp3, out_json):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"))
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7])
    json.dump(words, open(out_json, "w"), ensure_ascii=False)


def tts(text, voice, rate, cache):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:12]
    mp3, js = f"{cache}/{key}.mp3", f"{cache}/{key}.json"
    if not (os.path.exists(mp3) and os.path.exists(js)):
        for attempt in range(4):
            try:
                asyncio.run(_tts(text, voice, rate, mp3, js))
                break
            except Exception as e:
                if attempt == 3:
                    raise SystemExit(f"TTS failed: {e}")
    return mp3, json.load(open(js))


def pcm(path_or_lavfi, dur, lavfi=False, filters=None):
    """Decode audio (file or lavfi source) to mono float32 at SR, exactly dur seconds."""
    src = ["-f", "lavfi", "-i", path_or_lavfi] if lavfi else ["-i", path_or_lavfi]
    af = ["-af", filters] if filters else []
    raw = subprocess.run(["ffmpeg", "-v", "error", *src, *af, "-t", f"{dur:.3f}", "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = int(dur * SR)
    return np.pad(a, (0, max(0, n - len(a))))[:n]


def write_wav(path, a):
    with wave.open(path, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


# Sound beds: ffmpeg lavfi sources, all original synthesis (no third-party audio).
SFX = {
    "rain_out": ("anoisesrc=c=pink:a=0.5:r=48000", "highpass=f=300,lowpass=f=7000"),
    "rain_in": ("anoisesrc=c=brown:a=0.7:r=48000", "highpass=f=60,lowpass=f=650"),
    "hum": ("aevalsrc=0.25*sin(2*PI*60*t)+0.12*sin(2*PI*120*t)+0.05*sin(2*PI*180*t):s=48000", None),
    "static": ("anoisesrc=c=white:a=0.35:r=48000", "bandpass=f=1900:width_type=q:w=0.9,tremolo=f=6:d=0.7"),
    "engine": ("aevalsrc=0.45*sin(2*PI*44*t)*(0.65+0.35*sin(2*PI*11*t))+0.25*sin(2*PI*88*t+2*sin(2*PI*3*t)):s=48000",
               "lowpass=f=500"),
    "drone": ("aevalsrc=0.16*sin(2*PI*55*t)+0.11*sin(2*PI*55.35*t)+0.07*sin(2*PI*82.4*t)+0.04*sin(2*PI*110.7*t):s=48000",
              "lowpass=f=320"),
}


# ------------------------------------------------------------------- build
def plan(sb, cache):
    """Narration audio + word timings + shot spans."""
    voice, rate = sb.get("voice", "es-MX-JorgeNeural"), sb.get("rate", "-8%")
    t, voice_parts, shots, words_all = sb.get("lead", 0.12), [], [], []
    for li, line in enumerate(sb["lines"]):
        mp3, words = tts(line["text"], voice, rate, cache)
        a = pcm(mp3, 60)
        nz = np.nonzero(np.abs(a) > 0.003)[0]
        a = a[: nz[-1] + int(0.05 * SR)] if len(nz) else a[:1]
        voice_parts.append((t, a))
        for w in words:
            words_all.append({"text": w[0], "start": t + w[1], "end": t + w[2]})
        line_end = t + len(a) / SR + line.get("pause_after", 0.35)
        cuts = [t] + [t + words[s["at_word"]][1] - 0.05 for s in line["shots"][1:]]
        for s, a0, a1 in zip(line["shots"], cuts, cuts[1:] + [line_end]):
            shots.append(dict(s, start=a0, end=a1))
        t = line_end
    for s in sb.get("tail", []):
        shots.append(dict(s, start=t, end=t + s["dur"]))
        t += s["dur"]
    shots[0]["start"] = 0.0
    return t, voice_parts, shots, words_all


def mix_audio(total, voice_parts, shots, out):
    n = int(total * SR) + 1
    voice = np.zeros(n, np.float32)
    for t0, a in voice_parts:
        i = int(t0 * SR)
        voice[i:i + len(a)] += a[: n - i]
    bed = np.zeros(n, np.float32)
    names = {k for s in shots for k in s.get("sfx", {})}
    tt = np.arange(n) / SR
    for name in names:
        src, flt = SFX[name]
        track = pcm(src, total + 0.1, lavfi=True, filters=flt)[:n]
        env = np.zeros(n, np.float32)
        for s in shots:
            v = s.get("sfx", {}).get(name)
            if v is None:
                continue
            m = (tt >= s["start"]) & (tt < s["end"])
            u = (tt[m] - s["start"]) / max(1e-6, s["end"] - s["start"])
            env[m] = (v[0] + (v[1] - v[0]) * u) if isinstance(v, list) else v
        k = int(0.25 * SR)  # 250 ms crossfade between shots
        env = np.convolve(env, np.ones(k) / k, mode="same")
        bed += track * env
    write_wav(out + ".voice.wav", voice)
    write_wav(out + ".bed.wav", bed * 0.5)
    # voice ducks the bed; loudness to YouTube target
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".voice.wav", "-i", out + ".bed.wav", "-filter_complex",
                    "[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3,asplit[v][sc];"
                    "[1:a][sc]sidechaincompress=threshold=0.03:ratio=4:release=400[b];"
                    "[v][b]amix=2:normalize=0,loudnorm=I=-16:TP=-1.5,aresample=48000[a]",
                    "-map", "[a]", "-ac", "2", out], check=True)
    os.remove(out + ".voice.wav"), os.remove(out + ".bed.wav")


class Frames:
    """Compose a frame: scene layers (native) -> x3 -> offset by camera*depth -> overlay."""

    def __init__(self, scenes):
        self.scenes, self.cache = scenes, {}

    def up(self, img):
        k = id(img)
        if k not in self.cache or self.cache[k][0] is not img:
            if len(self.cache) > 64:
                self.cache.clear()
            self.cache[k] = (img, img.resize((img.width * S, img.height * S), Image.NEAREST))
        return self.cache[k][1]

    def render(self, shot, t, view=(OW, OH), focus=None):
        lt = t - shot["start"]
        u = lt / max(1e-6, shot["end"] - shot["start"])
        p = {k: interp(v, u) for k, v in shot.get("params", {}).items()}
        cam = shot.get("camera", {})
        cx, cy = interp(cam.get("x", 0), u), interp(cam.get("y", 0), u)
        if focus is not None:  # vertical crop: centre the camera on a scene x
            cx += focus - view[0] / S / 2
        frame = Image.new("RGBA", view, C("black"))
        for depth, img in getattr(self.scenes, shot["scene"])(t, lt, u, p):
            frame.alpha_composite(self.up(img), (round(-cx * depth * S), round(-cy * depth * S)))
        return frame


def overlay(frame, shot, scale=S):
    """Badge and on-screen caption at native pixel size (scaled)."""
    ov = layer(frame.width // scale, frame.height // scale)
    if shot.get("badge"):
        b = shot["badge"]
        d = ImageDraw.Draw(ov)
        d.rectangle([6, 6, 6 + text_width(b) + 7, 6 + 13], fill=C("black"))
        draw_text(ov, 10, 10, b, "night7")
    if shot.get("caption"):
        cap = shot["caption"]
        d = ImageDraw.Draw(ov)
        y = ov.height - 22
        d.rectangle([10, y - 4, 10 + text_width(cap) + 8, y + 10], fill=C("black"))
        draw_text(ov, 14, y, cap, "paper")
    frame.alpha_composite(ov.resize(frame.size, Image.NEAREST))
    return frame


def caption_pages(words, max_words=3, gap=0.35, max_chars=16):
    pages, cur = [], []
    for w in words:
        chars = len(" ".join(x["text"] for x in cur + [w]))
        if cur and (len(cur) == max_words or chars > max_chars or w["start"] - cur[-1]["end"] > gap
                    or cur[-1]["text"][-1:] in ".,?"):
            pages.append(cur)
            cur = []
        cur.append(w)
    return pages + ([cur] if cur else [])


def draw_captions(frame, pages, t, scale=9, y=1180):
    """Word-timed caption: current page, one active word in lamp yellow, pop on entry.
    Scale shrinks so the page fits 80% of the frame width (9:16 side safe area)."""
    page = next((p for p in pages if p[0]["start"] - 0.05 <= t < p[-1]["end"] + 0.25), None)
    if not page:
        return
    words = [w["text"].upper() for w in page]
    full = " ".join(words)
    scale = min(scale, int(frame.width * 0.8) // text_width(full, 1, bold=True))
    total_w = text_width(full, scale, bold=True)
    x = (frame.width - total_w) // 2
    for i, w in enumerate(page):
        if t < w["start"] - 0.05:
            break
        nxt = page[i + 1]["start"] if i + 1 < len(page) else w["end"] + 0.25
        active = w["start"] - 0.05 <= t < nxt - 0.05
        pop = min(1.0, (t - w["start"] + 0.05) / 0.12)
        sc = scale if pop >= 1 else max(scale - 2, int(scale * (0.75 + 0.25 * pop)))
        wx = x + text_width(" ".join(words[:i]) + (" " if i else ""), scale, bold=True) + (1 if i else 0) * 0
        draw_text(frame, wx, y + (scale - sc) * 3, words[i], "lamp4" if active else "white", sc, bold=True,
                  outline="black")


def encode(path, size, n_frames, frame_fn, audio):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-tune", "animation", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", path], stdin=subprocess.PIPE)
    for f in range(n_frames):
        p.stdin.write(frame_fn(f).convert("RGB").tobytes())
        if f % (FPS * 5) == 0:
            print(f"  {path.split('/')[-1]}: {f / FPS:.0f}s", flush=True)
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg failed")


def main():
    sb_path = sys.argv[1]
    sb = yaml.safe_load(open(sb_path))
    ep = os.path.dirname(os.path.abspath(sb_path))
    name, ver = sb["name"], sb.get("version", "v01")
    cache = f"{ep}/assets/aud/px"
    os.makedirs(cache, exist_ok=True), os.makedirs(f"{ep}/export", exist_ok=True)
    sys.path.insert(0, os.path.dirname(__file__))
    import scenes

    total, voice_parts, shots, words = plan(sb, cache)
    for s in shots:
        assert hasattr(scenes, s["scene"]), f"unknown scene {s['scene']}"
        assert s["end"] - s["start"] > 0.5, f"shot too short: {s}"
    fr = Frames(scenes)
    shot_at = lambda t: next(s for s in shots if s["start"] <= t < s["end"]) if t < shots[-1]["end"] else shots[-1]
    print(f"{name}: {total:.1f}s, {len(shots)} shots, "
          f"lengths {', '.join(f'{s['end'] - s['start']:.1f}' for s in shots)}")

    if "--stills" in sys.argv:
        out = f"{ep}/edit/{name}_stills"
        os.makedirs(out, exist_ok=True)
        tiles = []
        for i, s in enumerate(shots):
            t = s["start"] + (s["end"] - s["start"]) * s.get("still_at", 0.6)
            im = overlay(fr.render(s, t), s)
            im.convert("RGB").save(f"{out}/{i + 1:02d}_{s['scene']}.png")
            tiles.append(im.resize((OW // 3, OH // 3), Image.NEAREST))
        cols = 3
        sheet = Image.new("RGB", (cols * OW // 3, math.ceil(len(tiles) / cols) * OH // 3))
        for i, im in enumerate(tiles):
            sheet.paste(im.convert("RGB"), ((i % cols) * OW // 3, (i // cols) * OH // 3))
        sheet.save(f"{out}/sheet.png")
        print("stills:", out)
        return

    audio = f"{ep}/edit/{name}_{ver}.m4a.wav"
    os.makedirs(f"{ep}/edit", exist_ok=True)
    mix_audio(total, voice_parts, shots, audio)
    n = int(total * FPS)
    encode(f"{ep}/export/{name}_{ver}.mp4", (OW, OH), n,
           lambda f: overlay(fr.render(shot_at(f / FPS), f / FPS), shot_at(f / FPS)), audio)

    if "--short" in sys.argv:
        pages = caption_pages(words)
        sw, sh, top = 1080, 1920, 420

        def short_frame(f):
            t = f / FPS
            s = shot_at(t)
            img = Image.new("RGBA", (sw, sh), C("black"))
            sq = overlay(fr.render(s, t, view=(sw, sw), focus=s.get("vfocus", W / 2)), s)
            img.alpha_composite(sq, (0, top))
            title = sb.get("short_title", "")
            draw_text(img, (sw - text_width(title, 8, True)) // 2, 200, title, "paper", 8, bold=True)
            draw_captions(img, pages, t)
            return img

        encode(f"{ep}/export/{name}_short_{ver}.mp4", (sw, sh), n, short_frame, audio)
        with open(f"{ep}/export/{name}_short_{ver}.srt", "w") as f:
            for i, p in enumerate(pages, 1):
                ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x % 1 * 1000):03d}"
                f.write(f"{i}\n{ts(p[0]['start'])} --> {ts(p[-1]['end'])}\n{' '.join(w['text'] for w in p)}\n\n")
    os.remove(audio)
    print("done:", f"{ep}/export/{name}_{ver}.mp4")


if __name__ == "__main__":
    main()

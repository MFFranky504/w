#!/usr/bin/env python3
"""Build an Archivo Cero episode from its 02_GUION_PRODUCCION.md.

Usage: python3 tools/build_episode.py episodes/EP-001-vuelo-914 [max_scenes]

Per scene: Edge TTS voice, Cloudflare Flux image, Ken Burns clip with cold grade,
grain and certainty badge. Then: long video + vertical Shorts.
Existing assets are reused, so delete a file to regenerate it.
Needs: ffmpeg, edge-tts (pip), HTTPS_PROXY that injects the Cloudflare key.
"""
import base64, json, os, re, subprocess, sys, time

EP = sys.argv[1].rstrip("/")
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else None
NUM = re.search(r"EP-(\d+)", EP).group(1)
VOICE, RATE, FPS = "es-MX-JorgeNeural", "-8%", 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
STYLE = ("cinematic dark photography, cold desaturated blue-grey palette, single hard side light, "
         "deep shadows, static composition, documentary tone, realistic textures, no text, no watermark")
FLUX = ("https://api.cloudflare.com/client/v4/accounts/0c44d0b72948bf2a54d96ce7046aad8d"
        "/ai/run/@cf/black-forest-labs/flux-1-schnell")
# Cold grade + 35mm-style grain (Biblia §2.4).
GRADE = "eq=saturation=0.3:contrast=1.12:brightness=-0.04,colorbalance=bs=0.10:bm=0.05:rs=-0.05,noise=alls=9:allf=t"


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def parse(md):
    scenes, shorts, cta, block, label, n = [], [], "", 0, "", 0
    for line in md.splitlines():
        m = re.match(r"## BLOQUE (\d+) .*\[(.+)\]", line)
        if m:
            block, label, n = int(m.group(1)), m.group(2), 0
        elif "|||" in line and block:
            n += 1
            text, prompt = (s.strip() for s in line.split("|||"))
            scenes.append(dict(id=f"{block}.{n}", block=block, label=label, text=text, prompt=prompt))
        elif line.startswith("SHORT "):
            shorts.append(line.split(":")[1].split())
        elif line.startswith("CTA:"):
            cta = line[4:].strip()
    for a, b in zip(scenes, scenes[1:] + [None]):
        a["pad"] = 0.6 if b and b["block"] == a["block"] else 2.0  # silence after block (§4.1)
    return scenes, shorts, cta


def tts(text, out):
    if os.path.exists(out) and os.path.getsize(out):
        return
    text = text.replace("DC-4", "DC cuatro")  # the voice reads the hyphen aloud
    for attempt in range(4):
        r = subprocess.run(["edge-tts", "--proxy", os.environ.get("HTTPS_PROXY", ""), "--voice", VOICE,
                            f"--rate={RATE}", "--text", text, "--write-media", out], capture_output=True)
        if r.returncode == 0 and os.path.getsize(out):
            return
        time.sleep(5 * (attempt + 1))
    sys.exit(f"TTS failed: {out}")


def image(prompt, out):
    if os.path.exists(out) and os.path.getsize(out):
        return True
    body = json.dumps({"prompt": f"{prompt} {STYLE}", "steps": 6})
    for attempt in range(5):
        r = subprocess.run(["curl", "-s", "-m", "120", FLUX, "-H", "Authorization: Bearer proxy-injected",
                            "-H", "content-type: application/json", "-d", body], capture_output=True, text=True)
        try:
            open(out, "wb").write(base64.b64decode(json.loads(r.stdout)["result"]["image"]))
            return True
        except Exception:
            if "daily free allocation" in r.stdout:
                return False
            time.sleep(10 * (attempt + 1))
    sys.exit(f"Image failed: {out}\n{r.stdout[:300]}")


def clip(img, aud, pad, label, out, w, h, i, flip=False):
    """Slow Ken Burns move over the square image, cropped to w x h, with the scene audio."""
    if os.path.exists(out):
        return
    frames = int((duration(aud) + pad) * FPS)
    big = 2 * max(w, h)  # oversample so the zoom does not jitter
    zoom = f"1+0.10*on/{frames}" if i % 2 == 0 else f"1.10-0.10*on/{frames}"
    x = f"(iw-iw/zoom)*{(i % 3) / 2}"
    badge = (f",drawtext=fontfile={FONT}:text='{label}':fontcolor=white@0.75:fontsize={h // 45}"
             f":x={h // 27}:y={h // 27}:box=1:boxcolor=black@0.45:boxborderw=10") if label else ""
    vf = ("hflip," if flip else "") + (f"scale={big}:{big}:flags=lanczos,crop={big * w // max(w, h)}:{big * h // max(w, h)},"
          f"zoompan=z='{zoom}':x='{x}':y='(ih-ih/zoom)/2':d={frames}:s={w}x{h}:fps={FPS},{GRADE}{badge}")
    run("ffmpeg", "-y", "-loop", "1", "-i", img, "-i", aud, "-vf", vf, "-af", f"apad=pad_dur={pad}",
        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", out)


def join(clips, out):
    """Concatenate clips; add a low original drone under the voice (§4.3, own production)."""
    lst = out + ".txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    drone = "sine=f=55:r=48000[a1];sine=f=55.7:r=48000[a2];sine=f=82.4:r=48000[a3];[a1][a2][a3]amix=3,volume=0.12,lowpass=f=200[d]"
    # EQ + compression for the free TTS voice (§0.2).
    voice = "[0:a]highpass=f=70,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-16:TP=-1.5,aresample=48000[v]"
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-filter_complex",
        f"{drone};{voice};[v][d]amix=2:duration=first:normalize=0[a]", "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out)
    os.remove(lst)


scenes, shorts, cta = parse(open(f"{EP}/02_GUION_PRODUCCION.md").read())
assert scenes, "no scenes found"
assert all(s["label"] in ("LEYENDA", "HECHO VERIFICADO", "ESPECULACIÓN", "TESTIMONIO") for s in scenes)
by_id = {s["id"]: s for s in scenes}
assert all(i in by_id for sh in shorts for i in sh), "Short references a missing scene"
if LIMIT:
    scenes, shorts = scenes[:LIMIT], []

A = f"{EP}/assets"
for i, s in enumerate(scenes, 1):
    s["n"] = i
    s["aud"], s["img"] = f"{A}/aud/EP{NUM}_{i:03d}_v01.mp3", f"{A}/img/EP{NUM}_{i:03d}_v01.jpg"
    s["vid"] = f"{A}/vid/EP{NUM}_{i:03d}_v01.mp4"
    tts(s["text"], s["aud"])
    s["flip"] = not image(s["prompt"], s["img"])
    if s["flip"]:
        # shortcut: image quota spent, so this scene reuses an earlier image mirrored (clip marked v00);
        # rerun the build next day to generate the real image and a v01 clip.
        s["img"], s["vid"] = scenes[(i - 1) % 15 * 2]["img"], s["vid"].replace("_v01", "_v00")
        print(f"scene {s['id']} PLACEHOLDER image", flush=True)
    clip(s["img"], s["aud"], s["pad"], s["label"], s["vid"], 1920, 1080, i, s["flip"])
    print(f"scene {s['id']} ok", flush=True)

join([s["vid"] for s in scenes], f"{EP}/export/final_v01.mp4")
print("long:", round(duration(f"{EP}/export/final_v01.mp4")), "s")

if shorts:
    cta_aud = f"{A}/aud/EP{NUM}_cta_v01.mp3"
    tts(cta, cta_aud)
for k, ids in enumerate(shorts, 1):
    parts = []
    for j, sid in enumerate(ids + ["cta"]):
        s = by_id.get(sid) or dict(by_id[ids[-1]], aud=cta_aud, label="", n="cta")
        out = f"{A}/vid/EP{NUM}_short{k}_{s['n']}_v01.mp4"
        clip(s["img"], s["aud"], 0.4, s["label"], out, 1080, 1920, j, s.get("flip", False))
        parts.append(out)
    join(parts, f"{EP}/export/short_{k:02d}_v01.mp4")
    print(f"short {k}:", round(duration(f"{EP}/export/short_{k:02d}_v01.mp4")), "s")

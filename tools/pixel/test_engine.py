"""Self-check for the pixel engine. Run: python3 tools/pixel/test_engine.py [STORYBOARD.yaml]"""
import os, sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
import engine
import scenes

# 1. Every scene paints only palette colours (no blending leaks).
pal = {tuple(c) for c in engine.PAL}
for name in ("tower", "radar", "face", "runway", "plane_side", "calendar", "title",
             "phone", "map", "ocean", "card", "timeline", "newsstand", "archive", "portraits"):
    shot = {"scene": name, "start": 0.0, "end": 4.0, "params": {"plane": "approach", "blip_at": 0.2, "route": 0.7, "caracas": 0.5,
            "lines": ["1955 + 30 = 1985", "«PAN AM»"], "reveal": 0.8, "years": ["1985", "1993"], "labels": ["A", "B"], "active": 1.0,
            "show": 1.0, "question": 0.5}}
    frame = engine.overlay(engine.Frames(scenes).render(shot, 2.5), dict(shot, badge="LEYENDA", caption="1985"))
    cols = {tuple(c) for c in np.array(frame.convert("RGB")).reshape(-1, 3)[::7]}
    bad = cols - pal
    assert not bad, f"{name}: {len(bad)} off-palette colours, e.g. {list(bad)[:3]}"

# 2. Font covers every on-screen string of the storyboard (no '?' fallback glyphs).
sb_path = sys.argv[1] if len(sys.argv) > 1 else "episodes/EP-001-vuelo-914/cold_open.yaml"
sb = yaml.safe_load(open(sb_path))
on_screen = [sb.get("short_title", "")] + [s.get(k, "") for l in sb["lines"] for s in l["shots"] for k in ("badge", "caption")]
on_screen += [str(v) for l in sb["lines"] for s in l["shots"] + sb.get("tail", []) for k, v in s.get("params", {}).items() if k in ("text", "sub")]
on_screen += [x for l in sb["lines"] for s in l["shots"] for x in s.get("params", {}).get("lines", []) + s.get("params", {}).get("labels", []) + s.get("params", {}).get("years", [])]
on_screen += [s.get(k, "") for s in sb.get("tail", []) for k in ("badge", "caption")]
on_screen += [w for l in sb["lines"] for w in l["text"].split()]  # Short captions use narration words
for s in on_screen:
    for ch in s.upper():
        assert ch in engine.G or ch in engine.ACCENT, f"glyph missing: {ch!r} in {s!r}"

# 3. Caption pages: max 3 words, break on punctuation, keep order.
words = [{"text": t, "start": i * 0.3, "end": i * 0.3 + 0.25} for i, t in enumerate("Uno dos tres cuatro, cinco seis.".split())]
pages = engine.caption_pages(words)
assert [len(p) for p in pages] == [3, 1, 2], [len(p) for p in pages]
assert all(len(" ".join(w["text"] for w in p)) <= 16 for p in pages)
from PIL import Image
im = Image.new("RGBA", (1080, 1920))
long_page = [[{"text": "novecientos", "start": 0, "end": 1}, {"text": "cincuenta", "start": 1, "end": 2}]]
engine.draw_captions(im, long_page, 1.5)
xs = np.nonzero(np.array(im)[..., 3].any(0))[0]
assert xs.min() >= 1080 * 0.1 - 1 and xs.max() <= 1080 * 0.9 + 1, (xs.min(), xs.max())
assert [w["text"] for p in pages for w in p] == [w["text"] for w in words]

# 4. Interpolation and easing.
assert engine.interp([0, 10], 0) == 0 and engine.interp([0, 10], 1) == 10 and engine.interp("x", 0.5) == "x"
# 5. Music: moods with fixed and ramped levels synthesise without error and stay bounded.
m = engine.synth_music(20.0, [dict(start=0, end=10, music="tension"), dict(start=10, end=20, music={"mood": "calm", "level": [0.9, 0.0]})])
assert m.shape[0] == int(20 * engine.SR) + 1 and np.abs(m).max() < 1.0
# 6. Vertical crop of a camera-less scene is centred on vfocus (title text fully inside the crop).
fr = engine.Frames(scenes)
shot = {"scene": "title", "start": 0.0, "end": 2.0, "params": {"text": "VUELO 914", "sub": "X"}}
sq = np.array(fr.render(shot, 1.0, view=(1080, 1080), focus=352).convert("RGB"))
paper = np.all(sq == engine.P["paper"], axis=-1)
cols = np.nonzero(paper.any(0))[0]
assert cols.min() > 30 and cols.max() < 1050, (cols.min(), cols.max())
print("ok")

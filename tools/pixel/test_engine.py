"""Self-check for the pixel engine. Run: python3 tools/pixel/test_engine.py [STORYBOARD.yaml]"""
import os, sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
import engine
import scenes

# 1. Every scene paints only palette colours (no blending leaks).
pal = {tuple(c) for c in engine.PAL}
for name in ("tower", "radar", "face", "runway", "plane_side", "calendar", "title"):
    shot = {"scene": name, "start": 0.0, "end": 4.0, "params": {"plane": "approach", "blip_at": 0.2}}
    frame = engine.overlay(engine.Frames(scenes).render(shot, 2.5), dict(shot, badge="LEYENDA", caption="1985"))
    cols = {tuple(c) for c in np.array(frame.convert("RGB")).reshape(-1, 3)[::7]}
    bad = cols - pal
    assert not bad, f"{name}: {len(bad)} off-palette colours, e.g. {list(bad)[:3]}"

# 2. Font covers every on-screen string of the storyboard (no '?' fallback glyphs).
sb_path = sys.argv[1] if len(sys.argv) > 1 else "episodes/EP-001-vuelo-914/cold_open.yaml"
sb = yaml.safe_load(open(sb_path))
on_screen = [sb.get("short_title", "")] + [s.get(k, "") for l in sb["lines"] for s in l["shots"] for k in ("badge", "caption")]
on_screen += [str(v) for l in sb["lines"] for s in l["shots"] for k, v in s.get("params", {}).items() if k in ("text", "sub")]
on_screen += [w for l in sb["lines"] for w in l["text"].split()]  # Short captions use narration words
for s in on_screen:
    for ch in s.upper():
        assert ch in engine.G or ch in engine.ACCENT, f"glyph missing: {ch!r} in {s!r}"

# 3. Caption pages: max 3 words, break on punctuation, keep order.
words = [{"text": t, "start": i * 0.3, "end": i * 0.3 + 0.25} for i, t in enumerate("Uno dos tres cuatro, cinco seis.".split())]
pages = engine.caption_pages(words)
assert [len(p) for p in pages] == [3, 1, 2], [len(p) for p in pages]
assert [w["text"] for p in pages for w in p] == [w["text"] for w in words]

# 4. Interpolation and easing.
assert engine.interp([0, 10], 0) == 0 and engine.interp([0, 10], 1) == 10 and engine.interp("x", 0.5) == "x"
print("ok")

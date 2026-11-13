#!/usr/bin/env python3
"""Render the EP-001 pixel-art thumbnail using the shared scene and text engine."""
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "pixel"))

import engine
import scenes


def main():
    # Compose at the channel's 640x360 pixel-art resolution.
    canvas = scenes._asphalt().crop((32, 18, 672, 378)).convert("RGBA")

    # The 1955 pocket calendar is the hero object, enlarged with crisp pixels.
    card = scenes._calendar_card()
    # Cool the card's red header and grid; retain a single red date marker.
    pixels = np.array(card)
    for source, target in (("red0", "night3"), ("red1", "night4"), ("red2", "night5")):
        pixels[np.all(pixels[..., :3] == engine.P[source], axis=2), :3] = engine.P[target]
    card = Image.fromarray(pixels)
    canvas.alpha_composite(card, (205, 28))
    ImageDraw.Draw(canvas).rectangle((205 + 146, 28 + 97, 205 + 152, 28 + 102),
                                     fill=engine.C("red2"))

    # Cold rain and runway reflections keep the setting legible without competing.
    rain = scenes.rain(640, 360, 1.35, n=115, speed=160, length=5,
                       colors=("night4", "night5"), seed=8, alpha=145)
    canvas.alpha_composite(rain)

    # Reserve a dark, clean bottom third for the headline.
    d = ImageDraw.Draw(canvas)
    for y in range(244, 360):
        a = int(220 * min(1.0, (y - 244) / 34))
        d.line((0, y, 639, y), fill=(5, 6, 8, a))

    # Use the engine font for all headline lettering; bold with a pixel outline.
    headline = "30 AÑOS TARDE"
    scale = 7
    x = (640 - engine.text_width(headline, scale, bold=True)) // 2
    engine.draw_text(canvas, x, 270, headline, "white", scale=scale,
                     bold=True, outline="black")

    # Nearest-neighbour scaling preserves the hand-built pixel edges.
    out = canvas.convert("RGB").resize((1280, 720), Image.Resampling.NEAREST)
    path = ROOT / "episodes" / "EP-001-vuelo-914" / "thumbnail_v02.png"
    out.save(path, optimize=True)


if __name__ == "__main__":
    main()

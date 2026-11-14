"""Parte 13 — turns the AI-generated pixel scenes (Pollinations z-image, sprites/parte13/src) into 270x480 GBA-palette backgrounds.
The walkable floor of each scene is aligned to y=266 (the character's feet); below the image the ground strip is mirrored down."""
import os
from PIL import Image, ImageOps
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "parte13")
W, H, FEET = 270, 480, 266
SRC = [("bg0_11.jpg", .82, 14), ("bg1_11.jpg", .82, 0), ("bg2_22.jpg", .77, 0), ("bg3_22.jpg", .76, 0), ("bg4_22.jpg", .80, 0), ("bg5_22.jpg", .78, 0)]
def build(name, f, dx=0):
    im = Image.open(os.path.join(D, "src", name)).convert("RGB")
    S = round(FEET / f); im = im.resize((S, S), Image.LANCZOS)
    x0 = (S - W) // 2 + dx; im = im.crop((x0, 0, x0 + W, S))
    out = Image.new("RGB", (W, H)); out.paste(im, (0, 0))
    strip = im.crop((0, S - 40, W, S)); y = S; k = 0                        # continue the ground: mirrored copies of the bottom strip
    while y < H:
        out.paste(strip if k % 2 else ImageOps.flip(strip), (0, y)); y += 40; k += 1
    import numpy as np                                                       # soft darkening below the floor so the text boxes pop and the mirrored seams disappear
    a = np.asarray(out).astype(np.float32); g = np.clip((np.arange(H) - S) / 60, 0, 1)[:, None, None] * .45; out = Image.fromarray((a * (1 - g)).astype(np.uint8))
    out = out.quantize(colors=72, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")   # hard GBA-like palette, no blur
    return out
if __name__ == "__main__":
    for i, (n, f, dx) in enumerate(SRC): build(n, f, dx).save(os.path.join(D, f"fondo_{i}.png")); print(i, n)

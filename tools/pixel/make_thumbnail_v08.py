import sys; import os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, engine, scenes, fx_text
from PIL import Image, ImageDraw
from engine import OW, OH, draw_text, C, layer, glow
def build(out, lines):
    fr=engine.Frames(scenes)
    bg=fr.render({"scene":"runway","start":0,"end":10,"camera":{"x":32,"y":8},"params":{"plane":"approach","prog":0.93}}, 2.0, view=(OW,OH))
    nat=bg.resize((640,360), Image.NEAREST).convert("RGBA")
    vx,vy=320,189
    glow(nat, vx, vy, 120, ["night3","night5","paper","white"], strength=1.15, sy=0.55)
    glow(nat, vx-10, vy, 26, ["paper","white"], strength=1.6); glow(nat, vx+10, vy, 26, ["paper","white"], strength=1.6)
    d=ImageDraw.Draw(nat)
    for i in range(0,150,2):
        w=max(1,int(10*(i/150))); d.line([(vx-w,vy+8+i),(vx+w,vy+8+i)], fill=C("paper" if (i//2)%2 else "night6"))
    d.line([(vx-110,vy),(vx+110,vy)], fill=C("white"))
    hl=layer(640,360)
    scenes.head(hl, 395, 16, 250, 2.0, {"wide":1.8,"brows":1.0,"look":-1.0,"blink":False,"headset":True})
    nat.alpha_composite(hl)
    th=nat.resize((1280,720), Image.NEAREST)
    yy,xx=np.mgrid[0:720,0:1280]
    k=np.clip(0.30+0.70*(xx/660),0.30,1.0)
    a=np.array(th).astype(np.float32); a[...,:3]*=k[...,None]
    th=Image.fromarray(a.clip(0,255).astype(np.uint8)).convert("RGBA")
    draw_text(th, 40, 40, "1955 - 1985", "night7", 6, bold=True, outline="black")
    bone=["paper_hi","white","paper","night7"]
    for (x,y,s,sc,en,gp,seed) in lines:
        fx_text.fx_text(th, x, y, s, sc, bone, ghost=("red2",None), extrude=("red1","red0"), extrude_n=en, wear=0.02, scan=0.9, ghost_px=gp, seed=seed, bold=False)
    draw_text(th, 44, 612, "VUELO 914", "red2", 7, bold=True, outline="black")
    th.convert("RGB").save(out)
build(os.path.join(os.path.dirname(__file__), "..", "..", "episodes", "EP-001-vuelo-914", "thumbnail_v08.png"), [(48,150,"30 AÑOS",14,6,6,3),(48,335,"TARDE",18,7,7,8)])
print("ok")

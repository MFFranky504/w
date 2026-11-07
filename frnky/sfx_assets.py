"""Exporta cada efecto de sonido como WAV independiente (assets/sfx/) y el timeline con timestamps."""
import json
import pathlib

import numpy as np

from . import audio as A

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "sfx"
FX = {
    "whoosh": (0.6, lambda t: A.whoosh(t, 0.0, 0.3, 0.2)),
    "zombie_hit": (1.0, lambda t: A.zombie_hit(t, 0.0)),
    "blip_piero": (0.4, lambda t: (A.put(t, 0.0, A.blip(230 * 1.6, 0.3)), A.put(t, 0.07, A.blip(230 * 2.0, 0.3)))),
    "blip_memo": (0.4, lambda t: (A.put(t, 0.0, A.blip(300 * 1.6, 0.3)), A.put(t, 0.07, A.blip(300 * 2.0, 0.3)))),
    "blip_zombi": (0.4, lambda t: (A.put(t, 0.0, A.blip(110 * 1.6, 0.3)), A.put(t, 0.07, A.blip(110 * 2.0, 0.3)))),
    "crujido_bolsa": (0.8, lambda t: A.crinkle(t, 0.0)),
    "pasos_zombi": (3.2, lambda t: A.zombie_steps(t, 0.0, 3.0)),
    "sting_cta": (0.8, lambda t: A.sting(t, 0.0)),
    "gulp": (0.4, lambda t: A.gulp(t, 0.0)),
    "boing": (0.5, lambda t: A.boing(t, 0.0)),
    "gruñido": (1.0, lambda t: A.growl(t, 0.0, 0.8)),
    "ding_remate": (0.8, lambda t: A.ding(t, 0.0)),
    "squish_cerebro": (0.5, lambda t: A.squish(t, 0.0)),
    "risa_pop": (0.8, lambda t: A.laugh(t, 0.05)),
    "riser_loop": (1.4, lambda t: A.riser_short(t, 0.0, 1.2)),
}


def export(timeline=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (dur, fn) in FX.items():
        tr = np.zeros(int(dur * A.SR)); fn(tr)
        A.save(tr, OUT / f"{name}.wav")
    if timeline:
        (OUT / "timeline_ultimos-zombis.json").write_text(json.dumps([{"t": t, "efecto": e} for t, e in timeline], ensure_ascii=False, indent=1) + "\n")
    return list(FX)

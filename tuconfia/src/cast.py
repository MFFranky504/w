"""Reparto: cada personaje = estilo de pelo (king/short/tab/you) + paleta + ropa. Todos los renderers (rpg, battle2, portrait) lo leen."""
def ramp(b):
    f = lambda k: tuple(max(0, min(255, int(v * k))) for v in b)
    return dict(b=b, d=f(.72), dd=f(.5), l=tuple(min(255, int(v * 1.5 + 20)) for v in b))

CAST = {
 'king':  dict(style='king',  skin=(250, 212, 178), hair=dict(b=(52, 50, 78), d=(32, 30, 54), dd=(22, 20, 38), l=(110, 120, 176)), iris=(58, 96, 168), outfit='plaid', glasses=True),
 'tab':   dict(style='tab',   skin=(254, 220, 192), hair=dict(b=(150, 88, 54), d=(112, 62, 40), dd=(78, 42, 30), l=(214, 150, 92)), iris=(110, 70, 44), outfit='cardigan'),
 'you':   dict(style='you',   skin=(244, 200, 164), hair=dict(b=(72, 86, 160), d=(48, 58, 118), dd=(32, 38, 82), l=(130, 160, 232)), iris=(58, 80, 150), outfit='hoodie'),
 # --- historia 2: Messi
 'messi_kid':  dict(style='king', skin=(244, 202, 166), hair=ramp((116, 76, 48)), iris=(90, 60, 40), outfit='tee_blue', kid=True),
 'messi':      dict(style='king', skin=(240, 196, 160), hair=ramp((112, 72, 46)), iris=(90, 60, 40), outfit='argentina', beard=True),
 'rexach':     dict(style='short', skin=(242, 200, 166), hair=ramp((170, 170, 180)), iris=(80, 64, 52), outfit='blazer'),
 'jorge':      dict(style='short', skin=(236, 192, 156), hair=ramp((58, 44, 40)), iris=(80, 60, 44), outfit='polo', beard=True),
 'doctor':     dict(style='short', skin=(246, 208, 176), hair=ramp((84, 70, 64)), iris=(60, 84, 120), outfit='coat', glasses=True),
 'kid_a':      dict(style='king', skin=(238, 192, 154), hair=ramp((40, 30, 28)), iris=(70, 50, 40), outfit='tee_green', kid=True),
 'kid_b':      dict(style='you',  skin=(226, 176, 140), hair=ramp((30, 24, 30)), iris=(60, 44, 36), outfit='tee_yellow', kid=True),
 'kid_c':      dict(style='short', skin=(246, 208, 176), hair=ramp((178, 120, 66)), iris=(70, 110, 140), outfit='tee_red', kid=True),

 # --- historia 3: Stallone / Rocky
 'stallone': dict(style='shag', skin=(224, 174, 132), hair=ramp((40, 30, 28)), iris=(66, 46, 36), outfit='grey', sleepy=True, strong=True, stubble=True),
 'stallone_tux': dict(style='shag', skin=(224, 174, 132), hair=ramp((40, 30, 28)), iris=(66, 46, 36), outfit='tux', sleepy=True, strong=True, stubble=True),
 'prod1': dict(style='short', skin=(240, 196, 160), hair=ramp((176, 176, 186)), iris=(80, 64, 52), outfit='blazer', beard=False),
 'prod2': dict(style='short', skin=(236, 190, 154), hair=ramp((60, 52, 50)), iris=(60, 84, 120), outfit='teacher', glasses=True),

 # --- historia 4: Steve Jobs
 'jobs':   dict(style='short', skin=(236, 196, 164), hair=ramp((46, 34, 30)), iris=(70, 52, 40), outfit='turtle', glasses=True),
 'jobs85': dict(style='short', skin=(236, 196, 164), hair=ramp((46, 34, 30)), iris=(70, 52, 40), outfit='suit85'),
}
def resolve(who):
    c = dict(CAST[who]); c.setdefault('glasses', False); c.setdefault('beard', False); c.setdefault('kid', False); c.setdefault('sleepy', False); c.setdefault('strong', False); c.setdefault('stubble', False)
    return c

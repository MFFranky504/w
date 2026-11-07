"""Elenco variable: cada video genera 4 personajes distintos (nacionalidad, piel, pelo, ropa, accesorios)
a partir del id del episodio. Así el canal no repite siempre a los mismos."""
import random
import zlib

from .sprite import CHARS

H = lambda cols: [(0, i / len(cols), 1, (i + 1) / len(cols), c) for i, c in enumerate(cols)]
V = lambda cols: [(i / len(cols), 0, (i + 1) / len(cols), 1, c) for i, c in enumerate(cols)]
Y_, B_, R_, W_, G_, S_ = (252, 209, 22), (0, 56, 147), (206, 17, 38), (240, 240, 240), (0, 104, 71), (116, 172, 223)

NATIONS = {   # nombre, bandera, palabra típica, color de camiseta, nombres
    "MX": dict(name="México", flag=V([G_, W_, R_]), tag="güey", shirt=(32, 150, 84), names=["Chuy", "Lupita", "Beto", "Dani"]),
    "AR": dict(name="Argentina", flag=H([S_, W_, S_]), tag="che", shirt=(110, 190, 245), names=["Nati", "Facu", "Lucho", "Cami"]),
    "VE": dict(name="Venezuela", flag=H([Y_, B_, R_]), tag="chamo", shirt=(160, 34, 62), names=["Memo", "Yuli", "Andrés", "Vale"]),
    "CL": dict(name="Chile", flag=[(0, 0, 1, .5, W_), (0, .5, 1, 1, R_), (0, 0, .36, .5, B_)], tag="po", shirt=(200, 50, 60), names=["Pancho", "Javi", "Fran", "Nacho"]),
    "CO": dict(name="Colombia", flag=[(0, 0, 1, .5, Y_), (0, .5, 1, .75, B_), (0, .75, 1, 1, R_)], tag="parce", shirt=(250, 200, 40), names=["Nico", "Juli", "Sebas", "Karen"]),
    "PE": dict(name="Perú", flag=V([R_, W_, R_]), tag="causa", shirt=(214, 40, 56), names=["Sofi", "Piero", "Lucía", "Diego"]),
    "UY": dict(name="Uruguay", flag=H([W_, S_, W_, S_]), tag="bo", shirt=(120, 180, 236), names=["Tomi", "Mateo", "Flor", "Ale"]),
    "ES": dict(name="España", flag=[(0, 0, 1, .25, R_), (0, .25, 1, .75, Y_), (0, .75, 1, 1, R_)], tag="tío", shirt=(210, 40, 50), names=["Pablo", "Marta", "Álex", "Lola"]),
    "BO": dict(name="Bolivia", flag=H([R_, Y_, G_]), tag="mano", shirt=(40, 140, 80), names=["Rodri", "Mili", "Chino", "Pame"]),
    "EC": dict(name="Ecuador", flag=[(0, 0, 1, .5, Y_), (0, .5, 1, .75, B_), (0, .75, 1, 1, R_)], tag="ñaño", shirt=(250, 210, 50), names=["Joel", "Domi", "Kevin", "Anita"]),
}
SKINS = [(246, 206, 164), (236, 184, 140), (214, 160, 120), (186, 130, 94), (150, 104, 76), (120, 82, 60)]
HAIRS = [(30, 24, 30), (70, 44, 30), (118, 76, 40), (170, 110, 50), (200, 70, 60), (96, 60, 190), (40, 50, 70)]
EYES = [(90, 56, 34), (60, 130, 200), (50, 140, 90), (120, 80, 150), (70, 70, 70)]
STYLES = ["spiky", "cap", "pony", "curly", "spiky", "pony", "bun"]
PANTS = [(66, 92, 150), (46, 52, 74), (96, 100, 120), (60, 60, 80), (110, 90, 70)]
SHOES = [(240, 240, 240), (230, 80, 70), (60, 60, 80), (250, 210, 80)]
COLORS = {"bro": (226, 200, 120), "a": (222, 140, 130), "b": (214, 150, 190), "c": (130, 190, 210)}


def make_cast(episode_id, force=None):
    """Devuelve {rol: dict(sprite, label, color, pitch, flag, tag, nation)} para los roles bro/a/b/c.
    force = {"c": "VE"} obliga la nacionalidad de un rol (p. ej. «josear» es venezolano)."""
    rnd = random.Random(zlib.crc32(episode_id.encode()))
    codes = list(NATIONS)
    rnd.shuffle(codes)
    force = force or {}
    chosen = {}
    for role in ("bro", "a", "b", "c"):
        chosen[role] = force.get(role) or next(c for c in codes if c not in chosen.values())
    cast = {}
    for i, role in enumerate(("bro", "a", "b", "c")):
        nat = NATIONS[chosen[role]]
        style = rnd.choice(STYLES)
        shirt = nat["shirt"] if rnd.random() < .7 else rnd.choice([(58, 96, 214), (230, 90, 60), (60, 170, 110), (240, 120, 170)])
        sid = f"c_{episode_id}_{role}"
        CHARS[sid] = dict(
            skin=rnd.choice(SKINS), hair=rnd.choice(HAIRS), coat=shirt, kind=rnd.choice(["hoodie", "jersey", "jersey"]),
            trim=(244, 244, 240), pants=rnd.choice(PANTS), shoe=rnd.choice(SHOES), sole=rnd.choice([(40, 60, 170), (210, 60, 70), (120, 120, 140)]),
            eye=rnd.choice(EYES), style=style, cap=rnd.choice([(222, 52, 62), (60, 100, 210), (250, 200, 60), (60, 170, 110)]),
            glasses=rnd.random() < .25, band=style == "cap" and rnd.random() < .5)
        CHARS[sid + "_w"] = dict(CHARS[sid], coat=rnd.choice([(52, 64, 98), (70, 70, 80), (40, 90, 80)]), kind="blazer", pants=(70, 74, 96))
        cast[role] = dict(sprite=sid, work=sid + "_w", label=nat["names"][rnd.randrange(4)].upper(), color=COLORS[role],
                          pitch=[230, 170, 340, 270][i], flag=nat["flag"], tag=nat["tag"], nation=nat["name"], code=chosen[role])
    return cast

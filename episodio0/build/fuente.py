"""Fuente bitmap original 5x7 (solo mayúsculas) con acentos españoles.

Celda: 2 filas de acento + 7 de cuerpo + 2 de descendente = 11 de alto.
Ancho proporcional (se recortan columnas vacías); espacio = 3.
"""
from PIL import Image

_G = {
"A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
"B": "####.|#...#|#...#|####.|#...#|#...#|####.",
"C": ".###.|#...#|#....|#....|#....|#...#|.###.",
"D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
"E": "#####|#....|#....|####.|#....|#....|#####",
"F": "#####|#....|#....|####.|#....|#....|#....",
"G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
"H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
"I": "###|.#.|.#.|.#.|.#.|.#.|###",
"J": "..###|...#.|...#.|...#.|#..#.|#..#.|.##..",
"K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
"L": "#....|#....|#....|#....|#....|#....|#####",
"M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
"N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
"O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
"P": "####.|#...#|#...#|####.|#....|#....|#....",
"Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
"R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
"S": ".####|#....|#....|.###.|....#|....#|####.",
"T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
"U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
"V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
"W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.",
"X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
"Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
"Z": "#####|....#|...#.|..#..|.#...|#....|#####",
"0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
"1": ".#.|##.|.#.|.#.|.#.|.#.|###",
"2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
"3": "####.|....#|....#|.###.|....#|....#|####.",
"4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
"5": "#####|#....|####.|....#|....#|#...#|.###.",
"6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
"7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
"8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
"9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
".": ".|.|.|.|.|.|#",
",": "..|..|..|..|..|.#|.#|#.",
":": ".|#|.|.|.|#|.",
";": "..|.#|..|..|..|.#|.#|#.",
"!": "#|#|#|#|#|.|#",
"¡": "#|.|#|#|#|#|#",
"?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
"¿": "..#..|.....|..#..|.#...|#....|#...#|.###.",
"-": "...|...|...|###|...|...|...",
"+": ".....|..#..|..#..|#####|..#..|..#..|.....",
"/": "....#|....#|...#.|..#..|.#...|#....|#....",
"(": "..#|.#.|#..|#..|#..|.#.|..#",
")": "#..|.#.|..#|..#|..#|.#.|#..",
"'": "#|#|.|.|.|.|.",
'"': "#.#|#.#|...|...|...|...|...",
"·": ".|.|.|#|.|.|.",
"%": "##..#|##..#|...#.|..#..|.#...|#..##|#..##",
"#": ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#.",
"@": ".###.|#...#|#.###|#.#.#|#.###|#....|.###.",
"=": ".....|.....|#####|.....|#####|.....|.....",
"_": ".....|.....|.....|.....|.....|.....|#####",
"*": ".....|#.#.#|.###.|#####|.###.|#.#.#|.....",
"<": "...#|..#.|.#..|#...|.#..|..#.|...#",
">": "#...|.#..|..#.|...#|..#.|.#..|#...",
"×": ".....|.....|#...#|.#.#.|..#..|.#.#.|#...#",
}

# Acentos (2 filas sobre el cuerpo), alineados a una letra de 5 columnas
_ACUTE = ["...#.", "..#.."]
_TILDE = [".##.#", "#.##."]
_DIAER = [".....", ".#.#."]
_ACC = {"Á": ("A", _ACUTE), "É": ("E", _ACUTE), "Í": ("I", _ACUTE), "Ó": ("O", _ACUTE),
        "Ú": ("U", _ACUTE), "Ñ": ("N", _TILDE), "Ü": ("U", _DIAER)}

H_CELDA = 11
_cache = {}


def _bitmap(ch):
    """Devuelve lista de filas (11 de alto) con '#'/'.'."""
    if ch in _cache:
        return _cache[ch]
    acento = None
    base = ch
    if ch in _ACC:
        base, acento = _ACC[ch]
    filas = _G.get(base) or _G.get(base.upper())
    if filas is None:
        filas = _G["?"]
    filas = filas.split("|")
    w = len(filas[0])
    cuerpo = filas[:7]
    desc = filas[7:9]
    top = [["."] * w for _ in range(2)]
    if acento:
        # centra el acento de 5 columnas sobre la letra
        off = (5 - w) // 2
        for r in range(2):
            fila = list("." * w)
            for c, px in enumerate(acento[r]):
                cc = c - off
                if 0 <= cc < w and px == "#":
                    fila[cc] = "#"
            top[r] = fila
    rows = ["".join(r) for r in top] + cuerpo + desc
    while len(rows) < H_CELDA:
        rows.append("." * w)
    _cache[ch] = rows
    return rows


def ancho_glifo(ch):
    if ch == " ":
        return 3
    return len(_bitmap(ch)[0])


def ancho_texto(txt, esc=1, sep=1):
    if not txt:
        return 0
    return (sum(ancho_glifo(c) for c in txt) + sep * (len(txt) - 1)) * esc


def dibujar(img, x, y, txt, color, esc=1, sep=1, sombra=None):
    """Dibuja texto en una imagen RGB(A) PIL con píxeles duros. (x, y) = esquina sup. izq. de la celda."""
    px = img.load()
    W, H = img.size
    if sombra is not None:
        dibujar(img, x + esc, y + esc, txt, sombra, esc, sep)
    cx = x
    for ch in txt:
        if ch == " ":
            cx += (3 + sep) * esc
            continue
        rows = _bitmap(ch)
        for r, fila in enumerate(rows):
            for c, v in enumerate(fila):
                if v == "#":
                    for dy in range(esc):
                        for dx in range(esc):
                            X, Y = cx + c * esc + dx, y + r * esc + dy
                            if 0 <= X < W and 0 <= Y < H:
                                px[X, Y] = color
        cx += (len(rows[0]) + sep) * esc
    return cx


def dibujar_centrado(img, cx, y, txt, color, esc=1, sep=1, sombra=None):
    x = cx - ancho_texto(txt, esc, sep) // 2
    return dibujar(img, x, y, txt, color, esc, sep, sombra)


def partir(txt, max_px, esc=1, sep=1):
    """Parte texto en líneas que caben en max_px."""
    lineas, cur = [], ""
    for w in txt.split():
        prueba = (cur + " " + w).strip()
        if ancho_texto(prueba, esc, sep) <= max_px or not cur:
            cur = prueba
        else:
            lineas.append(cur)
            cur = w
    if cur:
        lineas.append(cur)
    return lineas


if __name__ == "__main__":
    img = Image.new("RGB", (360, 120), (10, 9, 16))
    dibujar(img, 4, 4, "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ", (241, 233, 210))
    dibujar(img, 4, 18, "ÁÉÍÓÚÜ 0123456789 .,:;!¡?¿-+/()'\"·%#@=*", (255, 176, 32))
    dibujar(img, 4, 34, "¿ENTRAS? J-???? 20:00 CDMX", (241, 233, 210), esc=2)
    dibujar(img, 4, 62, "IGRAM GAMES", (255, 176, 32), esc=3, sombra=(150, 36, 40))
    img.resize((1080, 360), Image.NEAREST).save("/tmp/claude-0/-home-user-w/5f58d328-15c4-5806-bc4d-5c7b39a06e26/scratchpad/ep0/fuente_test.png")

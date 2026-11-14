"""Piezas estáticas para el lanzamiento: portada del Reel (9:16) y carrusel de bases (4:5)."""
import sys, pathlib
from PIL import Image, ImageDraw
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render as R
import guion

OUT = R.OUT
P = R.P
FECHA, HORA, UTC = guion.CIERRE_PANTALLA


def lienzo(w, h, cy=None):
    full = R.OSCURO_LOGO if cy is None else R.fondo_oscuro(0.45, cy)
    return full.crop((0, (R.H - h) // 2, w, (R.H - h) // 2 + h)).copy() if h < R.H else full.copy()


def guardar(img, nombre):
    img.resize((img.width * R.ESC, img.height * R.ESC), Image.NEAREST).save(OUT / nombre)
    print("ok", nombre)


def portada():
    """Portada del Reel = fotograma 0 del video (el gancho), más la marca abajo."""
    img = R.ROJO.copy()
    img = R.hazard(img, 108, 10, 0)
    img = R.hazard(img, 420, 10, 0)
    R.txt_c(img, "ESTE COMENTARIO", 180, 150, P["bone"], 3, sombra=P["red_d"])
    R.pegar(img, R.tarjeta("ENTRO", "fuego"), R.CARD_X, R.CARD_Y)
    R.txt_c(img, "PUEDE", 180, 300, P["bone"], 3, sombra=P["red_d"])
    R.pegar_centrado(img, R.texto("ELIMINARTE.", P["red"], 4, sombra=P["bg0"]), 180, 346)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 450, R.W, 520], fill=P["bg0"])
    R.txt_c(img, guion.NOMBRE_PANTALLA, 180, 458, P["amber"], 3, sombra=P["red_d"])
    R.txt_c(img, "INSCRIPCIONES ABIERTAS · CIERRA " + FECHA + " · " + HORA, 180, 498, P["bone_d"], 1)
    guardar(img, "portada_reel.png")


def lista(img, items, y, esc=2, color=None, gap=8, maxw=320, x=20):
    import fuente
    for it in items:
        num, txt = it if isinstance(it, tuple) else (None, it)
        xx = x
        if num:
            R.pegar(img, R.texto(num, P["amber"], esc), x, y)
            xx = x + fuente.ancho_texto(num, esc) + 4 * esc
        for ln in fuente.partir(txt, maxw - (xx - x), esc):
            R.pegar(img, R.texto(ln, color or P["bone"], esc), xx, y)
            y += 13 * esc
        y += gap
    return y


def cabecera(img, titulo, n):
    R.txt_c(img, guion.NOMBRE_PANTALLA + " · BASES", 180, 18, P["bone_dd"], 1)
    R.txt_c(img, f"{n}/4", 180, 432, P["bone_dd"], 1)
    R.txt_c(img, titulo, 180, 38, P["amber"], 3, sombra=P["red_d"])
    ImageDraw.Draw(img).line([(20, 76), (340, 76)], fill=P["bg4"])


def carrusel():
    W, H = 360, 450
    # 1 portada
    img = lienzo(W, H, 200)
    R.txt_c(img, "BASES OFICIALES", 180, 40, P["bone_d"], 2)
    yb = R.emblema(img, 180, 82, 11, -9, 0)
    R.txt_c(img, guion.NOMBRE_PANTALLA, 180, yb + 18, P["amber"], 3, sombra=P["red_d"])
    R.txt_c(img, "TEMPORADA 1", 180, yb + 58, P["bone"], 2)
    R.txt_c(img, "LEE ANTES DE ENTRAR  >>", 180, 410, P["amber"], 1)
    guardar(img, "bases_1.png")

    # 2 cómo entrar
    img = lienzo(W, H, 220)
    cabecera(img, "CÓMO ENTRAR", 2)
    y = lista(img, [("1", 'COMENTA "ENTRO" + UN EMOJI EN EL REEL DE CONVOCATORIA.'),
                    ("2", "UNA CUENTA = UN JUGADOR. LOS DUPLICADOS NO CUENTAN."),
                    ("3", "CIERRE: " + FECHA + ", 20:00 HORA CDMX."),
                    ("4", "TRAS EL CIERRE RECIBES TU ID: J-0001, J-0002..."),
                    ], 92)
    lista(img, ["EQUIVALE A " + UTC.strip("()") + ". SOLO CUENTAN LOS COMENTARIOS PUBLICADOS ANTES DEL CIERRE."], y + 6, 1, P["bone_d"], maxw=320)
    guardar(img, "bases_2.png")

    # 3 reglas
    img = lienzo(W, H, 220)
    cabecera(img, "REGLAS", 3)
    y = lista(img, ["GRATIS. SIN COMPRAS.",
                    "PREMIO: TÍTULO DE CAMPEÓN.",
                    "100% DIGITAL.",
                    "REGLAS ANTES DE CADA JUEGO.",
                    "AZAR VERIFICABLE.",
                    "ACOSO O MULTICUENTA: FUERA.",
                    'RETIRO LIBRE: "RETIRO".'], 90, gap=9)
    y = lista(img, ["PREMIO SIMBÓLICO, SIN VALOR MONETARIO. CERO RETOS EN EL MUNDO REAL: TODO OCURRE EN INSTAGRAM. "
                    "EL AZAR USA UNA FUENTE PÚBLICA QUE CUALQUIERA PUEDE COMPROBAR. "
                    'PARA RETIRARTE EN CUALQUIER MOMENTO, COMENTA "RETIRO".'], y + 6, 1, P["bone_d"])
    assert y < 428, y
    guardar(img, "bases_3.png")

    # 4 calendario + aviso legal
    img = lienzo(W, H, 220)
    cabecera(img, "CALENDARIO", 4)
    y = lista(img, [("HOY", "INSCRIPCIÓN ABIERTA"),
                    ("17 NOV", "CIERRE · 20:00 CDMX"),
                    ("18 NOV", "JUEGO 1: LA PRIMERA PUERTA"),
                    ("6 SEM", "6 JUEGOS · 1 CAMPEÓN")], 92)
    lista(img, ["SOLO USAMOS TU ID Y TU ALIAS PÚBLICO. NUNCA DATOS PERSONALES.",
                "EDAD MÍNIMA: LA QUE EXIGEN LOS TÉRMINOS DE INSTAGRAM.",
                "ESTA PROMOCIÓN NO ESTÁ PATROCINADA, AVALADA NI ADMINISTRADA POR INSTAGRAM NI META, NI ASOCIADA A ELLOS."],
          y + 10, 1, P["bone_d"], gap=6, maxw=320)
    guardar(img, "bases_4.png")


if __name__ == "__main__":
    portada()
    carrusel()

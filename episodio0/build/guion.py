"""Guion del Episodio 0 (convocatoria). Fuente única de verdad para VO, subtítulos y escenas.

Estructura de retención (gancho -> micro-ganchos cada 2-3 s -> bucle):
  K01-K02  GANCHO: frase en pantalla desde el fotograma 0 + promesa
  K03-K04  marca y reglas del juego (golpes numéricos)
  K05      LAZO ABIERTO: "una regla que nadie ve venir"  (se cierra en K10)
  K06-K11  4 reglas rápidas con chip "REGLA N/4", cada una con un golpe
  K12-K14  llamada a la acción (cómo, cuándo, qué día abre)
  K15      pregunta final; el último fotograma = primer fotograma (bucle)

Sintaxis de cada línea:
  - palabra suelta   -> se dice y se muestra igual (en mayúsculas)
  - {dicho|MOSTRADO} -> se dice "dicho", en pantalla aparece "MOSTRADO"
  - MOSTRADO con '*' -> palabra de énfasis (ámbar + golpe de zoom + efecto)
  - MOSTRADO con '!' -> SLAM: palabra gigante en el centro con flash y sacudida
"""
import re

# --- Parámetros de la temporada (cambiar aquí y re-renderizar) ---
NOMBRE_DICHO = "Ai-gram Gueims."
NOMBRE_PANTALLA = "IGRAM GAMES"
CIERRE_PANTALLA = ("MAR 17 NOV", "20:00 HORA CDMX", "(02:00 UTC · MIÉ 18 NOV)")
INICIO_JUEGO1 = "MIÉ 18 NOV"

VOZ = {"model": "microsoft/mai-voice-2.1", "voice": "es-MX-Alejo"}
VELOCIDAD = 1.12   # la locución se acelera un 12 % (más energía, mismo tono)

LINEAS = [
    # (id, escena, texto)
    ("K01", "hook", "Este comentario puede {eliminarte.|*ELIMINARTE.}"),
    ("K02", "derez", "O ser el {último|*ÚLTIMO} en pie."),
    ("K03", "logo", "Bienvenido a {" + NOMBRE_DICHO + "|*" + NOMBRE_PANTALLA + ".}"),
    ("K04", "conteo", "{Seis|*6} juegos. {Un solo|*1} ganador."),
    ("K05", "tease", "Y hay una regla que {nadie|!NADIE} ve venir."),
    ("K06", "id", "{Uno.|*1.} Comentas, y recibes un {número.|*NÚMERO.}"),
    ("K07", "id_zoom", "Ese número {eres|*ERES} {tú.|!TÚ.}"),
    ("K08", "reglas", "{Dos.|*2.} Reglas públicas, antes de jugar. Nadie las cambia. {Ni nosotros.|!NI NOSOTROS.}"),
    ("K09", "elecciones", "{Tres.|*3.} Tus decisiones, y las de todos, deciden quién {cae.|!CAE.}"),
    ("K10", "fantasma", "Y la {cuatro.|*4.} Si {caes...|*CAES...} {no te vas.|!NO TE VAS.}"),
    ("K11", "votos", "Los eliminados siguen votando {cómo se juega.|*CÓMO SE JUEGA.}"),
    ("K12", "comentario", "Comenta {entro|*ENTRO} y un emoji. {Ahora.|!AHORA.}"),
    ("K13", "fecha", "Cierra el {martes diecisiete,|*MARTES 17,} a las {ocho de la noche,|*20:00,} {hora de México.|HORA CDMX.}"),
    ("K14", "puertas", "El {miércoles dieciocho,|*MIÉRCOLES 18,} abre la primera {puerta.|*PUERTA.}"),
    ("K15", "final", "{¿Entras?|*¿ENTRAS?}"),
]

# Silencio (s) antes de cada línea. K01 = 0: la voz arranca en el fotograma 0.
PAUSA_ANTES = {"K01": 0.0, "K02": 0.10, "K03": 0.18, "K04": 0.20, "K05": 0.28, "K06": 0.22,
               "K07": 0.08, "K08": 0.22, "K09": 0.20, "K10": 0.30, "K11": 0.10, "K12": 0.24,
               "K13": 0.10, "K14": 0.12, "K15": 0.22}
COLA_FINAL = 0.9  # segundos tras la última línea (el video se corta en seco y repite)


def tokens(texto):
    """Devuelve [(dicho, mostrado, enfasis, slam)]."""
    out = []
    for m in re.finditer(r"\{([^|}]*)\|([^}]*)\}|(\S+)", texto):
        if m.group(3):
            w = m.group(3)
            out.append((w, w.upper(), False, False))
        else:
            disp = m.group(2)
            slam = disp.startswith("!")
            enf = slam or disp.startswith("*")
            out.append((m.group(1), disp.lstrip("*!"), enf, slam))
    return out


def texto_dicho(texto):
    return " ".join(t[0] for t in tokens(texto))

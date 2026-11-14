"""Guion del Episodio 0 (convocatoria). Fuente única de verdad para VO, subtítulos y escenas.

Sintaxis de cada línea:
  - palabra suelta  -> se dice y se muestra igual (en mayúsculas)
  - {dicho|MOSTRADO} -> se dice "dicho", en pantalla aparece "MOSTRADO"
  - MOSTRADO que empieza con '*' -> se resalta en ámbar siempre
"""

# --- Parámetros de la temporada (cambiar aquí y re-renderizar) ---
NOMBRE_DICHO = "Ai-gram Gueims."
NOMBRE_PANTALLA = "IGRAM GAMES"
CIERRE_PANTALLA = ("MAR 17 NOV", "20:00 HORA CDMX", "(02:00 UTC · MIÉ 18 NOV)")
INICIO_JUEGO1 = "MIÉ 18 NOV"

VOZ = {"model": "microsoft/mai-voice-2.1", "voice": "es-MX-Alejo"}

LINEAS = [
    # (id, escena, texto)
    ("L01", "multitud", "Todos pueden entrar."),
    ("L02", "derez", "Solo uno va a ganar."),
    ("L03", "logo", "Esto es {" + NOMBRE_DICHO + "|*" + NOMBRE_PANTALLA + ".}"),
    ("L04", "conteo", "{Seis|*6} semanas. {Seis|*6} juegos. {Un|*1} ganador."),
    ("L05", "id", "Al inscribirte, recibes un número."),
    ("L06", "id_zoom", "Ese número eres tú."),
    ("L07", "reglas", "Las reglas se publican antes de cada juego... y nadie las cambia."),
    ("L08", "elecciones", "Tus decisiones, y las de todos los demás, deciden si sigues."),
    ("L09", "fantasma", "Y si caes... no te vas."),
    ("L10", "votos", "Los eliminados siguen votando cómo se juega."),
    ("L11", "comentario", "Para entrar, comenta {entro|*\"ENTRO\"} y un emoji en este video."),
    ("L12", "fecha", "Las inscripciones cierran el martes {diecisiete|*17} de noviembre, a las {ocho de la noche,|*20:00,} {hora de Ciudad de México.|HORA CDMX.}"),
    ("L13", "gratis", "Es gratis. Y todo es digital."),
    ("L14", "puertas", "La primera puerta se abre el {miércoles dieciocho.|*MIÉRCOLES 18.}"),
    ("L15", "final", "¿Entras?"),
]

# Silencio (s) antes de cada línea
PAUSA_ANTES = {"L01": 0.7, "L02": 0.35, "L03": 0.75, "L04": 0.6, "L05": 0.55, "L06": 0.25,
               "L07": 0.55, "L08": 0.5, "L09": 0.55, "L10": 0.3, "L11": 0.6, "L12": 0.45,
               "L13": 0.5, "L14": 0.5, "L15": 0.8}
COLA_FINAL = 3.2  # segundos tras la última línea


def tokens(texto):
    """Devuelve [(dicho, mostrado, enfasis)]."""
    import re
    out = []
    for m in re.finditer(r"\{([^|}]*)\|([^}]*)\}|(\S+)", texto):
        if m.group(3):
            w = m.group(3)
            out.append((w, w.upper(), False))
        else:
            disp = m.group(2)
            enf = disp.startswith("*")
            out.append((m.group(1), disp.lstrip("*"), enf))
    return out


def texto_dicho(texto):
    return " ".join(t[0] for t in tokens(texto))

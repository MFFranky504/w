"""Captions de TU CONF.IA: gancho fijo, hashtags fijos + 1 de persona, cierre con pregunta personal.
Uso: python3 src/captions.py "Kanye West" "un accidente que casi lo mata" "su primer disco" Kanye
"""
import sys

HASHTAGS_FIJOS = ["#Motivación", "#Superación", "#HistoriasQueInspiran"]
CIERRE = "¿Cuál fue tu mayor rechazo?"          # pregunta final del video y del caption


def gancho(famoso, fracaso, logro):
    return f"¿Sabías que {famoso} transformó {fracaso} en {logro}?"


def hashtag_persona(nombre):
    """un solo hashtag de la persona, sin tildes/espacios (ej. 'Kanye West' -> #KanyeWest)."""
    import unicodedata
    t = unicodedata.normalize('NFD', nombre)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return '#' + ''.join(w.capitalize() for w in t.replace('.', ' ').split())


def caption(famoso, fracaso, logro, persona=None, cuerpo=""):
    partes = [gancho(famoso, fracaso, logro)]
    if cuerpo: partes.append(cuerpo.strip())
    partes.append(CIERRE + " 👇 Cuéntamelo en los comentarios.")
    partes.append(' '.join(HASHTAGS_FIJOS + [hashtag_persona(persona or famoso)]))
    return '\n\n'.join(partes)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    print(caption(a[0], a[1], a[2], a[3] if len(a) > 3 else None))

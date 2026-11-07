# FRNKY66.IA — generador «Mi bro…»

    python3 -m frnky render bro-juega-bien   # MP4 1080x1920 + captions en videos/
    python3 -m frnky plan-week               # 3 variantes (categorías distintas) + calendario 1/día
    python3 -m frnky log <id> --likes 40 --comments 5 --shares 3 --saves 2 --followers 1
    python3 -m frnky report                  # qué categoría rinde mejor (comentarios x8, shares x10)
    python3 -m frnky schedule                # revisa la meta de 1-2 videos/día
    python3 -m frnky ideas                   # banco de ideas (docs/IDEAS.md)
    python3 -m frnky bio                     # texto de la bio

Reglas forzadas por código (`frnky/config.py`, `frnky/engine.py`): gancho visible desde el segundo 0,
CTA en pantalla en los últimos 2.2 s (el render falla si un diálogo lo pisa), el mismo CTA en el caption,
rotación de los 3 CTAs, hashtags siempre `#PixelArt #Comedia #Humor #MiBro`.
La bio hay que pegarla a mano en Instagram: «Un video nuevo cada día para mandarle a tu bro».

## Redes y calendario
- Un solo usuario en todas las redes: `@frnky66.ia`. `python3 -m frnky bio` imprime la bio de cada red (misma línea + dónde encontrar las otras).
- Hashtags: `#MiBro #Humor #Comedia #PixelArt`, siempre igual.
- `python3 -m frnky plan-week`: 3 situaciones nuevas (dinero, trabajo, amor) + variaciones de las ganadoras (`"kind": "ganadora"` en `data/ideas.json`), 1-2 videos al día.

## Elenco y escenarios por video
`frnky/cast.py` genera 4 personajes distintos por episodio (nacionalidad con bandera y muletilla, piel, pelo, ropa, accesorios) desde el id del video; `make_cast(id, force={"c": "VE"})` fija una nacionalidad si el tema lo pide.
`frnky/scenes3.py` tiene escenarios a píxel grueso (azotea, oficina, taquería) con el mismo sombreado que los sprites.

# Plan de publicación y medición (YouTube y TikTok primero)

## Línea base (7-nov-2026)
- YouTube: 34 suscriptores · 957 vistas medias/Short · mejores: Messi 1.355, Jordan 1.290.
- TikTok: 1 seguidor · 399 vistas medias · 1,7 guardados/video · mejor: «el guion que se negó a vender» 972 vistas, 94 likes.
- Instagram: 1 seguidor · 32 likes medios · 0 comentarios → segundo plano.

## Qué tienen en común los que funcionaron (hipótesis, no hechos)
Gancho de **rechazo o negativa** en el primer segundo + figura muy conocida + giro claro. Por eso la plantilla fija usa dos ganchos: «Hasta [famoso] fue rechazado.» y «[Famoso] podía [X]... pero se negó.». Con 3 videos buenos no se puede afirmar la causa: se mide con los 5 nuevos (`metricas.csv`).

## Cadencia
| Plataforma | Frecuencia | Variante del video |
|---|---|---|
| YouTube Shorts | 1–2 al día | botón **SUSCRÍBETE** (`--cta yt`) |
| TikTok | 1–2 al día | botón **SÍGUEME** (`--cta tt`) |
| Instagram Reels | 1 al día | botón **SÍGUEME** (`--cta tt`) |
Mismo guion en las tres, publicado con título/caption propios (`python3 src/captions.py script_X.json`). Probar dos franjas (p. ej. mediodía y noche, hora local) alternadas y anotar `hora_publicacion`.

## Producción realista
- Hoy hay 1 video terminado con la plantilla nueva (Dolly Parton, en las dos variantes de botón) y 4 guiones listos (Swift, Gaga, Johnson, Brady).
- Cuello de botella: la **cuota gratuita de voz** (ElevenLabs, 10.000 caracteres/mes) está agotada hasta el **5-dic-2026**. Opciones: plan de pago, otra cuenta o una voz alternativa.
- Para publicar 1–2 al día (14+ videos por plataforma en 2 semanas) faltan unos 9–13 videos más: ver `IDEAS_15.md` y reciclar con la plantilla los videos ya hechos (Jobs, Rowling, Carrey).

## Registro (`metricas.csv`)
`python3 src/metricas.py add "Dolly Parton (se negó a Elvis)" youtube 2026-11-08 vistas=1200 likes=80 guardados=15 comentarios=9` · `python3 src/metricas.py resumen`
Revisar a las 48 h de cada publicación. No sacar conclusiones con menos de 14 videos por plataforma.

## Reglas fijas de cada video
1. Gancho en los primeros 2 s (tipo «rechazado» o «se negó»). 2. Fracaso → giro → frase final. 3. Pregunta personal final: «¿Cuál fue tu mayor rechazo... y qué hiciste con él?» (en el video y en el caption). 4. En pantalla: «Guárdalo para cuando lo necesites» + botón. 5. Hashtags idénticos: `#Motivación #Superación #HistoriasQueInspiran` + uno de la persona.

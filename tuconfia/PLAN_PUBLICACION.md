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

## Video largo (3 min): Stephen Hawking
- `src/build_hawking.py` + `src/scenes9.py`, guion `guion_hawking.md` (formato de la skill `guiones-reels-videos-cortos`), textos de voz `elevenlabs_hawking_v3.txt` (~3.400 caracteres).
- Se publica como video largo / Short de 3 min en YouTube y como video normal en TikTok e Instagram; el mismo guion se puede recortar a 60 s con las líneas L1, L5-L7, L19, L26-L27 y L30.
- Voz: pendiente por cuota (ver `README.md`).

## Shorts nuevos: Dwayne Johnson y Tom Brady
Archivos: out/TU_CONFIA_johnson_SHORT_Vertical_yt.mp4 y out/TU_CONFIA_brady_SHORT_Vertical_yt.mp4 (vertical 1080x1920, unos 38 s). Textos por plataforma: caption_johnson_short_*.txt y caption_brady_short_*.txt.
Títulos YouTube Shorts: «Lo cortaron... y volvió a casa con 7 dólares 🔥» y «199 jugadores fueron elegidos antes que él 🏈».
Hechos a confirmar antes de publicar: los siete dólares de Johnson se basan en lo que él ha contado (una sola fuente encontrada); el resto coincide con Wikipedia.

## Short Lady Gaga
Archivo: out/TU_CONFIA_gaga_SHORT_Vertical_yt.mp4 (vertical, 37 s). Textos: caption_gaga_short_*.txt.
Título YouTube Shorts: «Hasta Lady Gaga fue despedida... y luego llegó al número uno 🎤».
Comentario fijado: «Cuéntame, ¿cuál es ese "no" que recibiste y que ahora estás transformando en una oportunidad? 👇».
Hechos revisados con Gemini y con conocimiento propio: despido de Island Def Jam en 2006, trabajo de mesera (narrado como «según ha contado»), composiciones para otros, nuevo contrato, The Fame en el número uno de varios países. Confirmar en una fuente antes de publicar: el plazo exacto («pocos meses»).
Aviso visual: la tarjeta final tapa la cara del personaje durante los últimos 2-3 s.

## Short Eminem
Archivo: out/TU_CONFIA_eminem_SHORT_Vertical_yt.mp4 (vertical, 40 s). Textos: caption_eminem_short_*.txt.
Título YouTube Shorts: «Hasta Eminem fracasó con su primer disco... y años después ganó un Óscar 🎤».
Comentario fijado sugerido: «¿Qué estás trabajando en silencio hoy? Cuéntamelo 👇».
Revisión: Gemini verificó los hechos y actuó como abogado del diablo sobre el guion y los fotogramas. Se corrigió: ventas de Infinite narradas como «según se ha reportado», un solo Óscar, sin «leyenda más grande de la historia». Se descartaron sus avisos de «HATA» (era un subtítulo a medias) y del cabello azul (es la mascota del cierre).
Confirmar antes de publicar: ventas de Infinite (cifra reportada), despido del restaurante.

## Short Michael Jordan
Archivo: out/TU_CONFIA_jordan_SHORT_Vertical_yt.mp4 (vertical, 40 s). Textos: caption_jordan_short_*.txt.
Título YouTube Shorts: «Hasta Michael Jordan fue cortado... y terminó con 6 títulos de la NBA 🏀».
Trabajo repartido: Gemini verificó los hechos, escribió el primer borrador y revisó los fotogramas (script src/gemini_qa.py). Claude reescribió el guion porque el de Gemini traía clichés y un error («campeonatos mundiales»), y quitó el gancho final duplicado.
Confirmar antes de publicar: que lo enviaron al equipo juvenil en 1978 (muchos medios dicen «cortado del equipo principal»). Los subtítulos tapan parte del personaje en planos anchos, igual que en los otros Shorts.

## Short Harrison Ford (Gemini + NVIDIA)
Archivo: out/TU_CONFIA_ford_SHORT_Vertical_yt.mp4 (vertical, 35 s). Textos: caption_ford_short_*.txt.
Reparto de IAs: Gemini escribió hechos, guion, reparto, escenas y ganchos. MiniMax (NVIDIA) no entregó la revisión: con guiones largos da 502/429 y con la revisión corta devolvió su razonamiento sin la lista. Gemini revisó los fotogramas; sus avisos eran subtítulos en posición normal, ya descartados en otros Shorts.
Confirmar antes de publicar: que el rechazo de la industria («Hasta Harrison Ford fue rechazado») se sostiene con una fuente; la frase de 1973 (papel pequeño en American Graffiti) es la que aparece en el guion.
Arreglos hechos a mano: pronunciación de nombres en inglés (el modelo la escribió mal) y reparto joven/adulto (Gemini lo dio plano).

## Short Albert Einstein (Gemini + NVIDIA)
Archivo: out/TU_CONFIA_einstein_SHORT_Vertical_yt.mp4 (vertical, 35 s). Textos: caption_einstein_short_*.txt (escritos con Gemini).
NVIDIA (MiniMax) no entregó textos: 502 con prompts largos y con max_tokens de 400 a 1000; cuando responde devuelve el razonamiento, no el texto. Los textos de NVIDIA quedan pendientes; reintentar más tarde.
Hechos a confirmar: rechazo en el examen de ETH Zúrich en 1895 a los 16 años, preparatoria en Aarau, Nobel de 1921 por el efecto fotoeléctrico.

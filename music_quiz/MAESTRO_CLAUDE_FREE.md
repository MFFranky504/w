# 🎤 EL ARTISTA OCULTO — Documento maestro del proyecto
> Pega este archivo completo al inicio de un chat nuevo de Claude (o súbelo como archivo) y escribe: **"Lee el documento maestro y continúa el proyecto. Hoy toca: ___"**.
> Contiene todo lo hecho del Parte 8 al Parte 15: formato, reglas, estilo, historial de episodios, pistas, ganadores, plantillas y prompts.

---

## 0. Cómo usar esto en Claude FREE (léelo primero)

**Lo que Claude Free SÍ puede hacer bien con este documento:**
- Elegir el próximo artista con el criterio que ya funcionó (sección 5).
- Investigar y redactar las 4 pistas, de ultra difícil a media, con fuentes (sección 4). *Pide siempre que busque en la web si tiene búsqueda activada; si no la tiene, que marque cada dato como "por verificar".*
- Procesar ganadores desde capturas o listas: filtrar, quitar repetidos y ordenar (sección 3).
- Escribir la descripción de Instagram y la lista de @ (sección 8).
- Diseñar escenas, fondos y personaje en palabras para el video (sección 6).

**Lo que Claude Free NO puede hacer (eso lo hacía Claude Code en la nube):**
- Renderizar el MP4 (motor Python + ffmpeg), dibujar los sprites o generar la música.
- Usar Gemini, Pollinations ni otras IAs por proxy. Esas claves solo existían en el entorno de Claude Code.
- Recordar chats anteriores: **cada chat nuevo empieza de cero, por eso existe este documento**. Cuando termines un episodio, actualiza las secciones 7 y 10 y vuelve a pegar el archivo.

**Consejo de límites (Free):** los mensajes son limitados. Pide cosas concretas ("dame las 4 pistas verificadas de X"), no "hazlo todo". Para listas de ganadores largas, pega el texto en vez de 30 capturas.

---

## 1. El canal

- **Nombre:** El Artista Oculto (Instagram `@el.artista.oculto.ia`, también TikTok y YouTube Shorts).
- **Idioma:** español, público joven hispanohablante (México, Argentina, Chile, etc.).
- **Formato:** video vertical 1080×1920, de 45 a 70 s, **sin narración (sin voz)**, con música original y efectos de sonido.
- **Concepto:** adivina al artista con 4 pistas (de la más difícil a la más fácil). Al día siguiente se revela la respuesta ("La respuesta de ayer") y aparecen en pantalla **los que acertaron**. Eso es el motor de comentarios: la gente comenta para salir en el siguiente video.
- **Serie:** cada video es una "Parte N". Hasta ahora van de la Parte 8 a la Parte 15.

---

## 2. Estructura de cada video (en orden)

| # | Segmento | Duración | Qué pasa |
|---|---|---|---|
| 1 | **Gancho** | 2–3 s | Empieza en el **cuadro 0**: no se desperdician los primeros 3 segundos. Texto grande + silueta del artista misterioso. |
| 2 | **La respuesta de ayer** | ~6–9 s | "LA RESPUESTA DE AYER FUE…", redoble y revelación del artista anterior (sprite a color, nombre grande y ciudad). |
| 3 | **Ganadores** | 10–25 s | "GANADORES · PARTE N-1" + "X PERSONAS LO ADIVINARON". Lista con scroll, ordenada por pista. Si son muchos (>100), **2 columnas y más rápido, pero legible**. |
| 4 | **4 pistas** | ~7 s cada una (la última ~8.5–9 s con 3-2-1) | Chip arriba ("VALE 4 PUNTOS", "48 NOCHES"…), escena distinta por pista, texto con palabras clave en dorado, barra "PISTA 1/4" con la dificultad. |
| 5 | **Cierre** | ~7 s | "¿YA SABES QUIÉN ES? / ESCRÍBELO EN LOS COMENTARIOS", "¿CUÁNTOS PUNTOS SACASTE?", "MAÑANA REVELO LA RESPUESTA", "SÍGUEME PARA VER LA RESPUESTA", "LOS QUE ACIERTEN SALEN EN LA PARTE N+1". |

**Puntos:** pista 1 = 4 pts, pista 2 = 3, pista 3 = 2, pista 4 = 1.
**Etiquetas de dificultad normales:** ULTRA DIFÍCIL → MUY DIFÍCIL → DIFÍCIL → MEDIA.
**Episodio "ULTRA DIFÍCIL" (Parte 10 y Parte 15, o sea cada 5 partes):** IMPOSIBLE → IMPOSIBLE → ULTRA DIFÍCIL → MUY DIFÍCIL, con menos segundos por pista y carteles "¡NIVEL: ULTRA DIFÍCIL!", "SOLO PARA FANS DE VERDAD" y "NI LA ÚLTIMA ES FÁCIL". La **Parte 20** debería volver a ser ultra difícil.

**Ganchos usados (primeros segundos):**
- **A:** "¿QUIÉN ES?" + "¡SOLO LOS REALES LO ADIVINAN!" (3 s).
- **B:** "SOLO EL 1% ADIVINA ESTE ARTISTA" + "¿LO ADIVINAS EN LA PISTA 1?" (2 s). ⚠️ El "1%" no tiene respaldo real; es una frase de enganche.
- **C:** "MODO MEGA DIFÍCIL" + "4 PISTAS · 0 FÁCILES" (Parte 10).
- **D (Parte 15, el más fuerte):** destello y golpe de audio en el cuadro 0, "PARTE 15 · ULTRA DIFÍCIL", "¿ERES FAN DE VERDAD?" con sacudida, "4 PISTAS IMPOSIBLES", "4 PISTAS · 0 FÁCILES", "¡SOLO 7 SEGUNDOS POR PISTA!", "¿LO ADIVINAS ANTES DE LA ÚLTIMA?" y una barra roja que se agota, con latidos de fondo.

---

## 3. Reglas de ganadores (EXACTAS, no cambiarlas)

1. **Cuenta** quien nombre al artista **o a cualquier integrante o apodo**: "Brian May" y "Freddie" valen para Queen, "Kurt Cobain" para Nirvana, "Paul McCartney" para Beatles, "MJ", "Rey del Pop" o "Mikel Sason" para Michael Jackson. Faltas de ortografía cuentan si se entiende.
2. **Los GIF o imágenes cuentan** (por ejemplo, un GIF de Kurt o una foto de Paul con "THE BEATLES XD").
3. **Cada usuario aparece UNA sola vez.** Si comentó varias veces, se queda su mejor registro (la pista más temprana).
4. **Orden:** pista 1 → pista 2 → pista 3 → pista 4 → **sin pista** (incluye "por la silueta", "desde el inicio" y mención directa) → dentro de cada grupo, **más likes primero** → empate: **quien comentó antes** (más horas o días).
5. Se marca la plataforma: IG (normal), **TT** (TikTok) y **YT** (YouTube).
6. **NO cuentan:** comentarios que no nombran al artista (por ejemplo "es el que se pegó un tiro…" sin decir el nombre), respuestas del creador ni comentarios sin relación.
7. El primer comentario puede llevar una etiqueta especial ("1ER COMENTARIO").
8. **Lista de @ para la descripción:** solo Instagram (sin TT ni YT), **separados por un solo espacio**, en el orden del video.

**Formato para guardar ganadores (una fila por persona):**
`usuario | plataforma (IG/TT/YT) | pista (1-4, o 0 = sin pista) | likes | horas desde que comentó`

---

## 4. Reglas para escribir pistas

- 4 pistas, de la más difícil a la más fácil (en ultra difícil, todas duras).
- **Cada dato debe ser verificable**: busca y anota la fuente. Si las fuentes no coinciden, la pista debe decir solo la parte segura (ejemplo: "nació en Inglaterra" en vez del pueblo exacto, o "en 1983" en vez del día).
- Si es una historia discutida, dilo: "según la historia, les dijeron que…".
- Específicas del artista: nada genérico que sirva para 20 músicos.
- **Nunca** pongas el nombre del artista, de sus canciones más obvias o de sus discos en las pistas 1–3. La 4 puede ser más directa ("Le dicen el Rey del Pop…").
- Palabras clave entre `*asteriscos*` (salen en dorado). Máximo unos 130 caracteres para que quepa en 4–5 líneas.
- Cada pista lleva un **chip** corto (1–2 palabras o una cifra: "48 NOCHES", "$606.17", "A LOS 11") y una **escena** que la ilustre.
- Evita datos sensibles (muertes, suicidio, escándalos).

---

## 5. Cómo elegir artista (lo que aprendimos)

**Lo que funcionó:**
- 🥇 **Michael Jackson (Parte 14): 4 mil vistas, el top 1 de la cuenta, 218 ganadores.**
- **Nirvana (Parte 12):** muy viral (muchas vistas y comentarios) y 105 ganadores.
- **Queen (Parte 11):** 70 ganadores.
- **Patrón:** artistas **legendarios que los jóvenes de HOY siguen amando y descubriendo en TikTok** (Queen, Nirvana, MJ). Eso pesa más que la novedad.

**Lo que no funcionó o se descartó:**
- **The Beatles (Parte 13):** pocas vistas, solo 27 ganadores.
- **Rechazados por el creador:** AC/DC ("muy anticuado"), Linkin Park y Metallica ("no tan virales en jóvenes").
- Las IAs tienden a sugerir pop actual (Bad Bunny, The Weeknd, Dua Lipa). **No es el estilo del canal.**

**Ya usados (no repetir):** Snoop Dogg (P8), Nas (P9), Tyler, The Creator (P10), Queen (P11) y Daft Punk (versión alterna de P11), Nirvana (P12), The Beatles (P13), Michael Jackson (P14), Guns N' Roses (P15). El creador también hizo **Kendrick Lamar** y **Eminem** por su cuenta.

**Candidatos para próximas partes:**
- **Rock y leyendas:** Led Zeppelin, Red Hot Chili Peppers, Jimi Hendrix, David Bowie, Pink Floyd, The Rolling Stones, Bob Marley, Elvis, Arctic Monkeys, Gorillaz, Fleetwood Mac, Oasis, Gustavo Cerati / Soda Stereo (lo pidió un seguidor).
- **Banco viejo con pistas ya redactadas (verificar de nuevo):** Tupac, 50 Cent, Daddy Yankee, Bad Bunny, Karol G, Shakira, Taylor Swift.
- **Peticiones de seguidores en comentarios:** Gustavo Cerati, Natanael Cano, Gorillaz, Blur.

---

## 6. Estilo visual (reglas del creador, todas aprendidas a base de correcciones)

- **Pixel art estilo Game Boy Advance / Kirby Amazing Mirror**: colores vivos, contorno oscuro (morado-azul marino), sombreado con 2–3 tonos y brillos. Resolución base 270×480 escalada ×4.
- **Fondos hechos a mano o con el motor procedural.** ❌ **NO usar fondos generados por IA** (Pollinations o z-image): el creador dijo que "no atraen" y se ven "muy IA".
- Los fondos **no pueden ser planos ni aburridos**: deben tener color, **animación** (luces que parpadean, humo, lluvia, confeti, reflectores, pájaros…), sombras y detalles.
- **La piedra y los azulejos deben ser continuos**, sin cuadros separados con contorno cada uno.
- **El primer fondo (gancho) y el último (cierre) deben tener relación con el artista** (por ejemplo, Seattle de noche para Nirvana o un escenario con bola disco para MJ).
- Cada pista tiene un **fondo distinto que ilustra el dato** (Hamburgo con neones, una gala con 8 gramófonos, Londres | LA partido a la mitad…).
- **Personaje misterioso:** sale en silueta (relleno azul marino con borde cian, rosa y dorado) + "?" flotando, y solo se revela a color en el video siguiente.
- **Proporciones del personaje:** **delgado y alto**, nada "chunky" ni gordo, cabeza proporcionada y **ojos suaves** (iris oscuro pequeño con brillito y cejas finas; nada de ojos grandes con pestañas gruesas que "dan miedo"). Ropa y accesorios icónicos que se lean en la silueta (fedora y guante para MJ, sombrero de copa y rizos para Slash, pelo hongo para Beatles).
- **Sin logos, nombres ni marcas reales** en fondos o carteles. Usa íconos, fechas y cifras.
- **Sombra** bajo el personaje. El texto siempre legible: si el fondo es claro, oscurece la franja de arriba.
- **Música original** (nunca copiar canciones): rock de estadio, house, neo-soul o boom bap según el artista, con loudness alrededor de −15 LUFS.

---

## 7. Historial de episodios (pistas exactas usadas)

### Parte 9 — Nas
- Género: hip hop · Respuesta de ayer: **SNOOP DOGG** (LONG BEACH, CALIFORNIA) · Ganadores mostrados (Parte 8): **48**
  1. **[MUY DIFÍCIL · 4 pts · chip «1991»]** Su primera aparición en un disco fue en 1991, como invitado en un tema del grupo Main Source.
  2. **[DIFÍCIL · 3 pts · chip «JAZZ»]** Su padre, Olu Dara, es músico de jazz y blues. Él creció en Queensbridge, Nueva York.
  3. **[MEDIA · 2 pts · chip «1994»]** Su álbum debut, de 1994, tiene solo 10 canciones y es considerado una obra maestra del hip hop.
  4. **[FÁCIL · 1 pt · chip «ETHER»]** Su guerra de rimas con Jay-Z dejó «Ether» en 2001, una de las mejores canciones de ataque del rap.

### Parte 10 — Tyler, The Creator
- Género: hip hop · Respuesta de ayer: **NAS** (QUEENSBRIDGE · NUEVA YORK) · Ganadores mostrados (Parte 9): **28** · Episodio MEGA DIFÍCIL.
  1. **[IMPOSIBLE · 4 pts · chip «CAFÉ»]** Antes de la fama trabajó más de dos años en Starbucks... y en FedEx duró menos de dos semanas.
  2. **[IMPOSIBLE · 3 pts · chip «12»]** De niño pasó por 12 escuelas distintas en 12 años, entre Los Ángeles y Sacramento.
  3. **[ULTRA DIFÍCIL · 2 pts · chip «2015»]** En 2015 le prohibieron entrar al Reino Unido por letras de sus primeros discos. Volvió en 2019.
  4. **[ULTRA DIFÍCIL · 1 pt · chip «SEUDÓNIMO»]** Dirige todos sus propios videos musicales, pero firma como director con un seudónimo: Wolf Haley.

### Parte 11 — Queen
- Género: rock · Respuesta de ayer: **TYLER THE CREATOR** (LOS ÁNGELES, CALIFORNIA) · Ganadores mostrados (Parte 10): **24**
  1. **[ULTRA DIFÍCIL · 4 pts · chip «1963»]** Su guitarrista construyó su guitarra con su papá, a partir de 1963, usando madera de una repisa de chimenea vieja.
  2. **[MUY DIFÍCIL · 3 pts · chip «ZANZÍBAR»]** Su cantante nació en Zanzíbar y se llamaba Farrokh Bulsara. Entró en la banda Smile en 1970.
  3. **[DIFÍCIL · 2 pts · chip «1985»]** En 1985 tocaron unos 20 minutos en el estadio de Wembley en el Live Aid, y muchos dicen que robaron el show.
  4. **[MEDIA · 1 pt · chip «1975»]** Su álbum de 1975, «A Night at the Opera», incluye «Bohemian Rhapsody».

### Parte 11 — Daft Punk (alterna)
- Género: electrónica · Respuesta de ayer: **TYLER THE CREATOR** (LOS ÁNGELES, CALIFORNIA) · Versión alterna de la Parte 11 (no fue la final).
  1. **[ULTRA DIFÍCIL · 5 pts · chip «1978»]** Su padre fue un compositor y productor de música disco: escribió «Cuba» en 1978 y «D.I.S.C.O.» en 1979.
  2. **[MUY DIFÍCIL · 4 pts · chip «1992»]** En 1992 tuvieron una banda de rock con un tercer amigo, que después se unió a la banda Phoenix.
  3. **[DIFÍCIL · 3 pts · chip «1994»]** Su primer sencillo salió en 1994 en Soma, un sello escocés de techno, tras entregar una maqueta en un rave.
  4. **[MEDIA · 2 pts · chip «2006»]** En 2006 tocaron en Coachella dentro de una pirámide de pantallas y luces LED.
  5. **[FÁCIL · 1 pt · chip «GRAMMY»]** En 2014 ganaron el Grammy a Álbum del Año, con un disco que incluía «Get Lucky» junto a Pharrell.

### Parte 12 — Nirvana
- Género: rock · Respuesta de ayer: **QUEEN** (LONDRES · REINO UNIDO) · Ganadores mostrados (Parte 11): **70** · Primer episodio estilo GBA. Muy viral.
  1. **[ULTRA DIFÍCIL · 4 pts · chip «NOMBRES»]** Antes de su nombre definitivo se llamaron Skid Row, Pen Cap Chew, Bliss y Ted Ed Fred.
  2. **[MUY DIFÍCIL · 3 pts · chip «$606.17»]** Su álbum debut, de 1989, costó solo 606,17 dólares y salió en el sello Sub Pop.
  3. **[DIFÍCIL · 2 pts · chip «1987»]** Se formaron en 1987 en Aberdeen, Washington.
  4. **[MEDIA · 1 pt · chip «1992»]** En enero de 1992 su álbum con un bebé nadando en la portada sacó del #1 a Dangerous de Michael Jackson.

### Parte 13 — The Beatles
- Género: rock · Respuesta de ayer: **NIRVANA** (ABERDEEN · WASHINGTON) · Ganadores mostrados (Parte 12): **105** · Pocas vistas.
  1. **[ULTRA DIFÍCIL · 4 pts · chip «48 NOCHES»]** En 1960 tocaron 48 noches seguidas en un club diminuto de Hamburgo, Alemania.
  2. **[MUY DIFÍCIL · 3 pts · chip «SKIFFLE»]** Empezaron como un grupo de skiffle con el nombre de una escuela. Dos miembros se conocieron en una fiesta de iglesia.
  3. **[DIFÍCIL · 2 pts · chip «RECHAZO»]** Una disquera los rechazó en 1962; según la historia, dijeron que los grupos de guitarras pasaban de moda.
  4. **[MEDIA · 1 pt · chip «AZOTEA»]** Su último concierto público fue en la azotea de su oficina en Londres, en 1969, hasta que llegó la policía.

### Parte 14 — Michael Jackson
- Género: pop · Respuesta de ayer: **THE BEATLES** (LIVERPOOL · INGLATERRA) · Ganadores mostrados (Parte 13): **27** · 🥇 4 mil vistas, top 1 de la cuenta.
  1. **[ULTRA DIFÍCIL · 4 pts · chip «A LOS 11»]** A los 11 años ya tenía un #1 en EE. UU. con un grupo de hermanos: sus primeros cuatro sencillos llegaron al número uno.
  2. **[MUY DIFÍCIL · 3 pts · chip «8 GRAMMYS»]** En 1984 ganó 8 Grammys en una sola noche, un récord que nadie ha superado.
  3. **[DIFÍCIL · 2 pts · chip «1983 · TV»]** En 1983, en un especial de TV por el aniversario de su antigua discográfica, estrenó un paso de baile que parece deslizarse hacia atrás.
  4. **[MEDIA · 1 pt · chip «REY DEL POP»]** Le dicen el Rey del Pop: sombrero fedora, un solo guante brillante y mocasines negros.

### Parte 15 — Guns N' Roses
- Género: rock · Respuesta de ayer: **MICHAEL JACKSON** (GARY · INDIANA) · Ganadores mostrados (Parte 14): **218** · Episodio ULTRA DIFÍCIL, gancho D.
  1. **[IMPOSIBLE · 4 pts · chip «26·03·85»]** Su primer concierto, en 1985, se anunció con los nombres de las dos bandas de Los Ángeles que se fusionaron para crearla.
  2. **[IMPOSIBLE · 3 pts · chip «INGLATERRA»]** Su guitarrista no nació en EE. UU., sino en Inglaterra, y se mudó a Los Ángeles siendo un niño de unos 6 años.
  3. **[ULTRA DIFÍCIL · 2 pts · chip «WEMBLEY 1992»]** En abril de 1992, en Wembley, su cantante cantó un clásico de otra banda junto a sus integrantes originales y Elton John.
  4. **[MUY DIFÍCIL · 1 pt · chip «$584M»]** Su gira de reunión (2016–2019) recaudó 584 millones de dólares: la tercera gira más taquillera de la historia.

**Parte 8 — Snoop Dogg** (sus 48 ganadores salieron en la Parte 9).

**Respuesta de la Parte 15 (Guns N' Roses):** se revela en la **Parte 16**, con sus ganadores.

---

## 8. Plantillas de texto

### 8.1 Descripción de Instagram (formato que le gustó al creador)
Un solo párrafo largo, **sin muchas separaciones**, **máximo 5 hashtags** y **sin decir el artista de hoy**:

```
🎸 ARTISTA MISTERIOSO · PARTE N. ¿Quién es el artista de hoy? Tienes 4 pistas, de la más difícil a la más fácil, y cuanto antes lo adivines, más puntos vale tu respuesta. Pista 1 (ultra difícil, 4 puntos): ___. Pista 2 (muy difícil, 3 puntos): ___. Pista 3 (difícil, 2 puntos): ___. Pista 4 (media, 1 punto): ___. ¿Ya sabes quién es? Escríbelo en los comentarios. Solo cuentan los que nombran al artista o a alguno de sus integrantes, y cada persona cuenta una sola vez. 🏆 RESPUESTA DE AYER: ___. Los ganadores de la Parte N-1 son ___ personas que nombraron a ___, ordenadas por pista, luego por likes y luego por quién comentó primero. Revisa la lista completa en el video. 📅 Mañana revelo la respuesta de hoy, así que sígueme para no perderte el resultado. Los que acierten salen en la Parte N+1. #ArtistaMisterioso #QuizMusical #ElArtistaOculto #___ #Adivinanza
```

### 8.2 Lista de @ (solo IG, un espacio entre cada uno)
`@usuario1 @usuario2 @usuario3 …` → Instagram limita las menciones por comentario: si no caben, divídelas en bloques de ~30.

### 8.3 Respuesta del creador a cada acierto
"@usuario Correcto bro! 🤓" (o "Correcto bro, es la banda 🤓" si nombró a un integrante).

---

## 9. Prompts listos para copiar en Claude Free

**A) Elegir artista**
> Con el documento maestro (sección 5), propón 4 artistas para la Parte __ que los jóvenes de hoy amen como a Queen, Nirvana o Michael Jackson, sin repetir los usados. Da una línea de por qué y recomienda uno.

**B) Pistas verificadas**
> Para la Parte __ (artista: ___), escribe 4 pistas según la sección 4: [normal: ULTRA DIFÍCIL→MUY DIFÍCIL→DIFÍCIL→MEDIA] o [ultra: IMPOSIBLE→IMPOSIBLE→ULTRA DIFÍCIL→MUY DIFÍCIL]. Cada una con chip, escena sugerida y fuente. Busca en la web; si no puedes verificar algo, márcalo "por verificar". Máximo 130 caracteres por pista.

**C) Ganadores desde texto o capturas**
> Aplica las reglas de la sección 3 a estos comentarios del artista ___ (Parte __). Devuélveme: (1) la tabla ordenada `usuario | plataforma | pista | likes | horas`, (2) el conteo por pista, (3) la lista de @ de Instagram separados por un espacio y (4) los dudosos que excluiste y por qué.

**D) Descripción de IG**
> Escribe la descripción de la Parte __ con la plantilla 8.1. Pistas: ___. Respuesta de ayer: ___ con ___ ganadores.

**E) Diseño visual (para pasarlo luego a Claude Code o dibujarlo)**
> Describe 6 fondos pixel art GBA (gancho, 4 pistas, cierre) y el personaje misterioso para ___, siguiendo la sección 6: qué se ve, qué se anima y qué colores lleva, sin logos ni nombres reales.

---

## 10. Pendientes y notas abiertas

- **Parte 16:** revelar a **Guns N' Roses** con sus ganadores. El artista nuevo está por elegir (normal, no ultra).
- **Parte 20:** siguiente episodio ULTRA DIFÍCIL.
- **Tema pendiente:** "muchas vistas, comentarios y likes, pero la gente no me sigue mucho". Ideas a probar:
  - Que el CTA de seguir aparezca antes, no solo al final.
  - Mencionar en el video que "la respuesta solo la ven los que te siguen".
  - Fijar un comentario con la lista de ganadores.
  - Responder a todos, porque ya se hace con "Correcto bro!".
  - Revisar las métricas reales de seguidores por reel en las estadísticas de Instagram.
- **Dudas de datos marcadas:**
  - P15: dónde nació exactamente Slash (Londres o Stoke-on-Trent), por eso la pista dice "Inglaterra"; y "tercera gira más taquillera" era el puesto al cierre de la gira.
  - P14: la emisión del Motown 25 tiene fechas distintas según la fuente, por eso dice "1983".
  - P13: la frase de Decca está disputada, por eso dice "según la historia".
- **Hook "1%":** es una frase de enganche sin dato real detrás. Si el creador quiere ser 100% honesto, conviene cambiarla.

---

## 11. Motor técnico (para cuando vuelvas a Claude Code)

- **Repo:** `github.com/MFFranky504/w`, rama `claude/new-session-sjsm0n`, carpeta `music_quiz/`.
- **Archivos clave:**
  - `episodes.py`: un `dict` por parte con artista, pistas, escenas, gancho, recap y ganadores.
  - `video.py`: render pixel 270×480 ×4 → ffmpeg H.264.
  - `audio.py`: música original sintetizada en numpy y efectos.
  - `tl.py`: línea de tiempo.
  - `captions.py`: textos por plataforma.
  - `gba_sprites.py` (P12), `gba_p14.py`, `gba_p15.py`: fondos y personajes procedurales.
  - `content/ganadores_pNN_*.json`: ganadores.
  - `content/FUENTES_pNN_*.md`: fuentes de cada pista.
  - `delivery/`: los MP4.
- **Construir un episodio:**
  `EPISODE=p15 python3 audio.py && ffmpeg -i raw_audio.wav -af loudnorm=I=-15:TP=-2:LRA=9 -ar 44100 audio.wav -y && EPISODE=p15 python3 video.py delivery/salida.mp4`
- **Opciones útiles por episodio:** `hook` (a/b/c/d), `mega=True` (ultra difícil), `clue_len`, `last_clue_len`, `banners`, `win_cols=2` + `row_h=62` + `win_speed=400` (para listas largas), `win_label` y `win_sub` (texto del orden).
- **Para la Parte 16:** crear `ganadores_p15_guns_n_roses.json`, un episodio `p16` con `prev=dict(sprite=… guitarrista de gba_p15 …, part=15, lines=("GUNS N'", "ROSES"), sub="LOS ÁNGELES · CALIFORNIA")`, fondos nuevos con el motor procedural y verificación de las pistas.

---

## 12. Apéndice: ganadores de las últimas partes (orden del video)

### Parte 14 · Michael Jackson (mostrados en la Parte 15): 218 ganadores
Por pista: pista 1: 114 · pista 2: 10 · pista 3: 3 · sin pista: 91

**@ de Instagram (copiar y pegar):**
```
@martojosebarrancas @angelrock26841 @gipsyy1414 @nosoy._clark @eli.zzapizza @julio_gd18 @gek_rey @dyf_r3nt @matiretrata @fan_cdeg @afbulval @franxd00__ @rodri1.8mr_s @brahian90418 @iamthecounterfeit @hiram._.pantoja._.pro @xanderrni @xndress_.s @andres._.roses @anjo_09_09 @wicho2303 @sxd09._ @memi_rv1 @dilanruiz494 @leonanaya602 @mr.damiann.01 @hide_itzae @_dx.gozz @haly.doll @bernardovj11 @elimxp_ @nosoyadriancreo @_iz.vx_ @agosmendoza2 @joselito.13456 @vannabannana11 @n0b0dy_kn0w5_777 @luketa_paketa @jaav_jpg @siguiendo_tu_creatividad @joseph_cabrera0510 @compapada @platanito_trailero @derek_nunxz @ianmw_64 @evansenriqueschoborgth28 @chuymysterio619 @momazospinochet2 @damian54847 @sanchiti831 @angie.hi1 @2023puel01 @slnw_off @han.sk2501 @montsrock @_aitana_sa @kimiandgeorgelover @mojon_dmps @sebas_loqd14 @_r4p3_m3 @kennyloq68581 @alicegeek30 @myke_onyxs @val_22587 @angelito_2850 @angeldoom_743 @isaac_garcia_7 @neirapromaxx @made.65y @aquiles_sito @katstar.8 @tonatiuh_7777 @matias.cobain_ @tuskact45 @don_kamaron_mariskos @henry.mjf @trini_applehead_1958 @uerp2212 @jonaxp64 @jleiva145 @dexx_.14 @angxl._012lx @ailthonsancheztucto @johnfalze @zomi_1236 @pedrovs4614 @angeljoel9244 @jazmin707546 @mirkin2014 @alpataco_12 @its_strwbrry_ @alejandroo_ykz @fan.de_mj @b3tun_1425 @monit_scorpion @sari.x_land_ @skibidi_yes_yes67 @juanitoo_gh @darkxwolf17till @ricowaos @invader_tori @eduardojamalaab @cheems_ig32h @oscarivanalmendariz @mitimsand @damian_dajh @lumine_rea @yonelitohalamadrid @joaco.aguirre.14 @beni_ciocca @ikzzz_7 @lemoncakee0_0 @off.the.wall._mjj @el_coleccionista_offizyal @taojampascheuing @its_ikelou6793 @alan.m_a_t @samuelsudjdk @ren_nn1215 @puso_100 @personadelomasnormal2026 @santxbass @lowsan_2011 @pedrojj431 @simono.123 @suenostereo_620 @alejandropastor1515 @nomellamodahiane @matetomatepim @_l0k1llo @vladymochis @gaelepap @pato_fgs @arcangel_201 @sp1k3sh4nk_666 @mariangelvcardenasr @soyelgabooficial @elpug1235 @julianbaezam.16 @elpib3acdc @11.bastti @bauti507777 @chris.xsd4 @octa.12.rojas @giuly_k1ngmind @hsberg_110 @bautty_diazz @baturoni_02 @alexander.v_f @ricardo_saav12 @1544c_lol @mateoaquinocerqueda @ciro.perez.alarcia @callme_gabxx_ @thiago_crdz08 @balam_10xd @marcus_barril @restre_004 @therealchriscornell_ @aldelgado_ @manuelgomez22026 @max_box_king @v.17.12.2015 @miawtthiu.exe @im_j.j_vasquez @cardenas.estefano @gl_fabxrm @jonathan425411 @sebaspizzart @nestor.bascunan @avelazquez2000 @mario19lopez_ @d_nielabl @derick_1713 @loroesn @jorayignacio @sebastian.diaz.torres @jade.mallea @yazzz_fearnot1115 @nyanpumpkin @antonio_020813 @yupp.idk666 @lizel.isabeth @josxphd @j.alessandrox @legoshi_musicaaa @ger_glock7 @matte0274 @derek_16112012 @elz_xar096 @pollo_bskt @algi3n_raro @bray4n_h7 @diego.fxz__ @mateo_martinez_ezequiel @joni_hernandez_c @dereksito._133 @brunopantoja029 @9_angel_arellano @seb4s_cast @derek_jezt @soygatoseco_oficial_josexd @fersi_to206 @moonwalkerfansmj @ivv33t @diegoruizmoreno10 @chris_oyarzabal_16 @jimenaluciaherrera @mau.ayala23 @soy_k_aren @elpapayas8264 @cristhian_.xta @joh27music @lucaspizarro_0409 @_.isaaxki._ @gizz_9tw @daniela_linares5 @wtffsalo
```

### Parte 13 · The Beatles (mostrados en la Parte 14): 27 ganadores
Por pista: pista 1: 10 · pista 2: 4 · pista 3: 1 · sin pista: 12

**@ de Instagram (copiar y pegar):**
```
@eli.zzapizza @zz.hendi_ @richard.1034w @11.bastti @d3adcvp1d_zzz @compapada @1544c_lol @th_sahid @manuelgomez22026 @mosh.king2 @hernanwn._.glezz @uerp2212 @juanitoo_gh @alejandroo_ykz @lowsan_2011 @edn_ar_bg @brahian90418 @kennyloq68581 @slnw_off @dylangabrielcruzcastano @lemoncakee0_0 @y1k3s_tvb @elpib3acdc
```
TikTok/YouTube (no se etiquetan): chris (TT), ⚡Josue⚡ (TT), Michael.arts (TT), Xavi.456789 (TT)

### Parte 12 · Nirvana (mostrados en la Parte 13): 105 ganadores
Por pista: pista 1: 23 · pista 2: 13 · pista 3: 5 · pista 4: 1 · sin pista: 63

**@ de Instagram (copiar y pegar):**
```
@henry.mr.222 @alambaruk1 @darkonosew @luan.02316 @edn_ar_bg @deadof.ros3s @jeff_the_land_shark124 @nirvana_fan2329 @im_luiss_2012 @angelfap10 @maxi_berns @crissxzy_c3 @dxiro_s00 @alex_pgochi @zz.hendi_ @luismiguel_x_motleycrue @zoanbm @marianot_tn @leandro1raffin @sanss3015 @adalxx_gh @_.missael98 @not_br4ndn777 @lucianoayala @gonzx.mx @joaco_o968 @quetzarmando @alejandroo_ykz @luketa_paketa @ivv33t @richard.1034w @i.i.c.g_13_ssj @slnw_off @felipe_r431 @abisai_tv @eli.zzapizza @soad_lover_1 @raqxts._.8073 @elwillmaf08 @dede.g.r27 @az_ridah3 @emilin._.kets @lowsan_2011 @alejandropastor1515 @y4h_l3.idk @nose36697 @4nim4lkan1val @compapada @manse_365 @ajolotito912 @fan_cdeg @1345agustin @gnr0s666.humm @josefcomics11011 @iturri_13 @en_bartoprime @pollo_bskt @alonsing_w @lisandrosuarzzz @mati356476 @bolillotactico87 @benjamon1613 @idk_juan710 @claudioandres_1710 @guch0_ruwan1207 @juanitoo_gh @xx.fran.xx16 @elicdtfrver16 @brahian90418 @not.4bdiel @lucaso77712 @migue.cs.34 @garzongodd @ikzzz_7 @simono.123 @regssss31 @arcangel_201 @maximilianolopez.gonzalez @kennyloq68581 @rotten_cd1 @johnfalze @ketorolaco_post @nahuel.galarza12 @sarkypp_ @n_a_z2311 @nekusgmd @im_andrezzzes @xolots_official
```
TikTok/YouTube (no se etiquetan): Kimberly Ixcayau (TT), guminom (TT), Im_black:) (TT), junito123pt (TT), ★◆Samuel◆★ (TT), Jere (TT), chris (TT), A_JOS__☆JX_☆ (TT), DidierGomez-g2h (YT), luisruben41V (YT), lan-215 (YT), Maxmayfield_74 (YT), juegosconDaniel-k4u (YT), SantiagoOrtiz-s1n (YT), SofiaR_13 (YT), Abimael (TT), Paulo (TT)


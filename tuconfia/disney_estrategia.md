# Walt Disney — estrategia de publicación (video largo horizontal 1920×1080)

Guion: `script_disney.json` (28 líneas · `tts` 2.565 caracteres ≈ 151 s a 17 c/s · `gen` 3.101 caracteres). Con las etiquetas `[pause]` debería quedar en **≈2:35-2:50 de voz** + 6 s de tarjeta final.
Verificación: `disney_notas_verificacion.md`.

**Qué cambió frente al borrador:** empieza en Nueva York 1928 (la negativa llega en ~25 s, no en 1:15); se quitó «perdió todo»; Iwerks y Roy tienen crédito explícito; una línea de sombra (huelga de 1941); Blancanieves/Óscar/Disneyland fuera, reemplazados por un segundo golpe real (Iwerks se va en 1930 y Walt se derrumba en 1931) y por la curiosidad final (Oswald vuelve en 2006 a cambio de un narrador deportivo... y Walt nunca lo vio). El bucle abierto de L2 («lo que pasó después con ese personaje... casi nadie lo sabe») se paga en L22-L24.

Nota sobre `hookscore.py`: el gancho elegido saca 35 (en inglés, 44): «WEAK», porque premia «you» y números. Se mantiene «podía... pero se negó» porque es el formato con mejores datos propios del canal (Stallone 972 vistas en TikTok) y la promesa de L2 aporta la curiosidad que la herramienta pide.

---

## 1. Títulos

| # | Título | Caract. | Comentario |
|---|---|---|---|
| **1** | **Walt Disney podía aceptar el trato... pero se negó** | 50 | **Principal.** Fórmula «se negó» del canal; nombre al principio (no se corta en móvil); veraz. |
| 2 | Le quitaron su conejo a Walt Disney... volvió 78 años después | 61 | Para cambiar a las 48 h si el CTR < 4 %. Usa el dato curioso (número + giro). |
| 3 | Hasta Walt Disney perdió a su equipo: la historia antes de Mickey | 65 | Fórmula «Hasta X...»; capta búsqueda «historia de Walt Disney». |

## 2. Miniatura (1280×720)

**A (principal) — texto: «LE QUITARON SU CONEJO»** (4 palabras; no repite el título, que habla de la negativa: el título dice *qué hizo*, la miniatura *qué perdió*).
- **Composición:** regla de tercios. Izquierda (40 %): Walt chibi pixel-art propio (bigote fino, traje de los años 20, pelo engominado) en plano medio, mirando a cámara con **expresión de rabia contenida/ojos brillantes de tristeza**, sujetando un contrato roto en dos. Derecha: una silueta de conejo genérico **gris oscuro, de espaldas, alejándose** por una puerta de oficina iluminada con «1928» en el cristal.
- **Texto:** arriba a la derecha, 2 líneas, «LE QUITARON» blanco / «SU CONEJO» amarillo (#FFD23F), fuente pixel gruesa con contorno negro de 6-8 px. Ocupa ≤ 35 % del área.
- **Colores:** fondo azul noche (#1B2A49) con luz cálida de lámpara sobre Walt (contraste cálido/frío); rojo solo en el contrato roto.
- **NO poner:** Mickey, orejas redondas, Oswald real (pantaloncitos, orejas largas con su forma), logo o castillo Disney, tipografía de Disney, flechas/emojis, más de 4 palabras, la palabra «TODO».

**B (prueba A/B) — texto: «VOLVIÓ 78 AÑOS DESPUÉS»** (4 palabras).
- Mismo Walt chibi, pero en primer plano con mirada nostálgica hacia arriba; a la derecha la misma silueta de conejo ahora **de frente, entrando** por la puerta, con rótulo «2006». «78» enorme en amarillo; el resto en blanco.
- Usa la curiosidad; si gana B, cambiar al título 1 se mantiene (no se repiten palabras).

## 3. Descripción (copiar y pegar)

```
En 1928, Walt Disney podía aceptar un trato peor... pero se negó. Ese "no" le costó su personaje, Oswald, y a casi todo su equipo. Esta es la historia real antes de Mickey, y lo que pasó con ese conejo 78 años después.

👇 Cuéntame en los comentarios: ¿a qué trato injusto le dirías que no... y qué vas a crear que sea solo tuyo?

🔖 Guárdalo para cuando lo necesites.
▶️ Suscríbete a Tu ConfIA: una historia que inspira cada semana.

CAPÍTULOS
[00:00] Dijo que no
[MM:SS] Nueva York, 1928
[MM:SS] Lo que le quedó
[MM:SS] El ratón de Ub Iwerks
[MM:SS] Otro rechazo
[MM:SS] Estreno en Nueva York
[MM:SS] El amigo que se fue
[MM:SS] Cuando se vino abajo
[MM:SS] No fue perfecto
[MM:SS] El conejo vuelve
[MM:SS] Lo que te queda

Historia basada en hechos públicos y biografías. Lo que solo contó él se dice como "según contó". Los personajes del video son dibujos originales del canal, no diseños de Disney. Música: piano instrumental.

#Motivación #Superación #HistoriasQueInspiran #WaltDisney
```

Reglas de capítulos (yt-chapters): el primero debe ser 00:00, mínimo 3, cada uno ≥ 10 s. Si al montar alguno queda < 10 s, fusiónalo con el siguiente («Otro rechazo» + «Estreno en Nueva York» son los candidatos).
Correspondencia: Dijo que no = L1-L2 · Nueva York, 1928 = L3-L8 · Lo que le quedó = L9-L11 · El ratón de Ub Iwerks = L12 · Otro rechazo = L13-L14 · Estreno = L15-L16 · El amigo que se fue = L17-L18 · Cuando se vino abajo = L19-L20 · No fue perfecto = L21 · El conejo vuelve = L22-L24 · Lo que te queda = L25-L28.

**Etiquetas:** walt disney, historia de walt disney, oswald el conejo afortunado, ub iwerks, roy disney, steamboat willie, historia de superación, motivación en español, historias que inspiran, historias reales, superación personal, tu conf ia
**Consultas objetivo (prueba de yt-seo):** «historia de Walt Disney», «Walt Disney Oswald», «Walt Disney fracasos». Las tres palabras clave están en título 1 + primeras 2 líneas.

## 4. Comentario fijado

«Walt pudo aceptar y seguir cobrando... y dijo que NO. ¿A qué trato injusto le dirías que no tú? Te leo y respondo a todos 👇 (Y dime si sabías lo del narrador deportivo 😄)»

## 5. Plan de las primeras 24 h

| Momento | Acción |
|---|---|
| T-0 | Subir como video largo, título 1, miniatura A; activar prueba A/B (A vs B) si el canal la tiene. Pantalla final en los últimos 6 s: suscribirse + video de Hawking. Publicar en la franja de noche local (alternar con la de mediodía de los Shorts y anotarlo en `metricas.csv`). |
| T+0 a 5 min | Publicar y fijar el comentario. |
| T+1 h | Responder a todos los comentarios de la primera hora con una pregunta de vuelta. Publicar un Short vertical de 45-55 s con L1-L7 + L24 + L28 que termine en «video completo en el canal». |
| T+3-4 h | Mismo Short en TikTok/Reels con botón SÍGUEME (`--cta tt`). Compartir el enlace del largo en la comunidad del canal (si está disponible) con la pregunta del comentario fijado. |
| T+24 h | Mirar en Studio: CTR de impresiones, retención en 0:30 y en el minuto 2:00 (L22, el pago del bucle). Registrar en `metricas.csv`. **No** cambiar título ni miniatura hasta las 48 h (la prueba A/B necesita tiempo). |
| T+48 h | Si CTR < 4 %: pasar al título 2. Si la retención cae antes de 0:30: el problema es el arranque, no el empaque. |

## 6. Riesgos de retención y cómo los resuelve el guion

1. **«Ya me sé la historia de Disney» (abandono en 0:10-0:30).** L2 abre un bucle que casi nadie conoce («lo que pasó después con ese personaje») y el video arranca en la reunión de Nueva York, no en Chicago 1901. El pago (L22-L24: 2006, el narrador deportivo, Walt nunca lo vio) llega cerca del final.
2. **Valle a la mitad tras el éxito de Steamboat Willie (~1:20).** Justo después del triunfo (L16) llega el segundo golpe: el amigo que se quedó se va (L17-L18) y Walt se derrumba (L19). La tensión se renueva en lugar de convertirse en un desfile de logros.
3. **Cierre largo que invita a salir antes de la pregunta.** El dato curioso está en L22-L24, a menos de 25 s del final; las frases finales son 3 líneas cortas y un solo pedido (la pregunta). Pregunta directa a mitad de video (L8) para mantener la implicación del espectador.

## 7. Mapa de escenas (15 escenas, corte de plano cada ~5 s)

| # | Escena | Líneas | Lugar / época | Personajes | Qué muestra la pantalla |
|---|---|---|---|---|---|
| 1 | `oficina_mintz` | L1-L2 | Oficina de Nueva York, 1928, noche | Walt chibi, Mintz (silueta de traje a contraluz) | Walt frente a un escritorio; contrato sobre la mesa; texto «¡SE NEGÓ!»; zoom a la cara de Walt; en L2 una puerta que se cierra con una silueta de conejo genérico detrás del cristal (signo de interrogación). |
| 2 | `nueva_york_1928` | L3 | Calle de NY con rascacielos, invierno 1928 | Walt (con sombrero y maletín) | Cartel «NUEVA YORK · 1928»; Walt entrando a un edificio; cartel de cine con silueta del conejo (diseño propio, sin pantalón ni rasgos de Oswald). |
| 3 | `trato_peor` | L4-L6 | Interior de la oficina | Walt, Mintz | Monedas pixel que bajan; documento «DERECHOS: UNIVERSAL» (texto genérico, sin logo); mesas de dibujo con sillas vacías y nombres tachados. |
| 4 | `dijo_no` | L7-L8 | Pasillo/escalera del edificio | Walt solo | Contrato cae al suelo, golpe de sonido; texto «¡Y DIJO NO!»; en L8 plano cercano en silencio con texto «¿Y TÚ?». |
| 5 | `kansas_quiebra` | L9 | Kansas City, 1923 (flashback, tonos sepia) | Walt más joven | Estudio pequeño con cartel rojo «QUIEBRA»; rótulo «1923». |
| 6 | `hermanos_estudio` | L10 | Estudio en Los Ángeles, palmeras | Walt, Roy (chibi con gafas y libro de cuentas) | Roy sumando en un libro contable; Walt dibujando; rótulo «LO QUE LE QUEDÓ». |
| 7 | `amigo_iwerks` | L11-L12 | Tren nocturno → mesa de dibujo | Walt, Ub (chibi con gafas redondas) | Walt garabatea un círculo en el tren; corte: Ub perfecciona un ratón genérico (silueta propia, nunca orejas de Mickey). |
| 8 | `primer_rechazo` | L13 | Sala de proyección vacía | Walt, distribuidores en silueta | Proyector, pantalla en blanco; distribuidores negando con la cabeza; texto «OTRO RECHAZO». |
| 9 | `sonido` | L14 | Estudio de grabación | Walt con micrófono antiguo, músicos | Ondas de sonido pixel sincronizadas con un metrónomo; Walt hablando al micro. |
| 10 | `estreno_colony` | L15-L16 | Marquesina de teatro en NY, 18-nov-1928 | Público chibi | Marquesina «18 · NOV · 1928»; público riendo; confeti. Texto «¡ÉXITO!». |
| 11 | `amigo_se_va` | L17-L18 | Estudio, 1930 | Walt, Ub, Powers (silueta) | Ub sale con una caja de pertenencias; su mesa de dibujo vacía; puerta que se cierra; rótulo «1930». |
| 12 | `derrumbe` | L19-L20 | Despacho de noche → barco/costa al amanecer, 1931 | Walt, médico (silueta) | Walt con la cabeza entre las manos, papeles por el suelo; médico señalando «DESCANSO»; transición al amanecer; en L20 Ub vuelve a entrar por la misma puerta (rótulo «1940»), apretón de manos. |
| 13 | `huelga_1941` | L21 | Exterior del estudio, 1941 | Animadores con carteles en blanco/genéricos | Fila de piquete con carteles sin texto legible; Walt mirando desde una ventana; tono gris, sin música. |
| 14 | `conejo_vuelve` | L22-L24 | Estudio de TV / oficina moderna, 2006 → cielo | Narrador deportivo genérico (silueta con micrófono, sin parecido a Al Michaels), silueta de conejo | Rótulo «2006 · 78 AÑOS DESPUÉS»; balanza: micrófono de un lado, conejo del otro; en L24 corte a una silla vacía de Walt con el conejo de espaldas mirándola. |
| 15 | `cierre_pregunta` | L25-L28 | Amanecer, mesa de dibujo con hoja en blanco | Walt, Roy y Ub juntos (L26), luego el espectador chibi | L25 Walt firma una hoja en blanco; L26 los tres juntos; L27 hoja en blanco iluminada; L28 bucle con la oficina de la escena 1 vacía y la puerta abierta. Tarjeta final 6 s con botón SUSCRÍBETE (solo en pantalla). |

# Episodio 0: Convocatoria (lanzamiento: sábado 14 de noviembre de 2026)

**Inscripción:** desde que se publica el Reel hasta el **martes 17 de noviembre de 2026, 20:00 CDMX** (02:00 UTC del miércoles 18)
**Juego 1:** miércoles 18 de noviembre de 2026

## Archivos para publicar (`episodio0/out/`)

| Archivo | Uso | Formato |
|---|---|---|
| `episodio0_convocatoria.mp4` | Reel de convocatoria | 1080×1920 · 30 fps · 51 s · H.264 + AAC · ≈ −15 LUFS |
| `portada_reel.png` | Portada del Reel (= fotograma 0, el gancho) | 1080×1920; todo lo importante cae dentro del recorte 3:4 de la cuadrícula |
| `bases_1.png` … `bases_4.png` | Carrusel "Bases oficiales" | 1080×1350 (4:5) |

---

## Checklist de hoy, en este orden

1. **Cuenta profesional.** Pasa la cuenta a Creador o Empresa *antes* de publicar. Hace falta para leer los comentarios por API al cierre.
2. **Desactiva los filtros de comentarios.** En Configuración → Palabras ocultas, apaga "Ocultar comentarios" y "Filtro avanzado de comentarios". Si no, Instagram puede esconder inscripciones que parezcan repetidas.
3. **Publica el carrusel de bases** (`bases_1` a `bases_4`) y **fíjalo en el perfil**.
4. **Publica el Reel** con `episodio0_convocatoria.mp4`, usa `portada_reel.png` como portada y pega el texto de abajo. **Anota la hora exacta de publicación**: entra en el registro de auditoría.
5. **Fija el comentario** de instrucciones (texto abajo).
6. **Sube una Historia** con el Reel y el **sticker de cuenta regresiva** hasta el 17 de noviembre a las 20:00. Quien lo active recibe un aviso al terminar.
7. **No respondas IDs a mano.** Los IDs se asignan todos juntos al cierre, por orden de llegada.
8. **No borres comentarios de inscripción.** Si alguno es ofensivo, ocúltalo y anota alias + motivo + hora en una nota aparte (esa nota alimenta la auditoría).
9. **No uses encuestas de Historias para nada oficial**, porque no son auditables. Solo sirven para conversar.

### Recordatorios ya programables

| Cuándo | Dónde | Texto |
|---|---|---|
| Dom 15 nov, 20:00 | Historia | QUEDAN 48 HORAS. Comenta ENTRO + emoji en el Reel fijado. |
| Lun 16 nov, 20:00 | Historia | QUEDAN 24 HORAS. |
| Mar 17 nov, 18:00 | Historia | QUEDAN 2 HORAS. Cierre 20:00 CDMX. |
| Mar 17 nov, 20:00 | Historia | INSCRIPCIONES CERRADAS. Mañana se abre la primera puerta. |

---

## Texto del Reel (caption)

```
🔻 ESTE COMENTARIO PUEDE ELIMINARTE 🔻

IGram Games · Temporada 1 · Inscripciones abiertas.
6 juegos. 6 semanas. 1 campeón. Todo pasa aquí.

▶ CÓMO ENTRAR
Comenta ENTRO + un emoji en este Reel. Ejemplo: ENTRO 🔥
• 1 cuenta = 1 jugador.
• Cierre: martes 17 de noviembre, 20:00 hora CDMX (02:00 UTC del miércoles 18).
• Tras el cierre recibes tu ID (J-0001, J-0002…). Ese número eres tú.

▶ LO QUE DEBES SABER
• Gratis. Premio simbólico: el título de Campeón de la T1 (sin valor monetario).
• 100 % digital. Cero retos en el mundo real.
• Las reglas de cada juego se publican antes de jugar. El azar es verificable públicamente.
• Si te eliminan, no te vas: los eliminados votan cómo se juega.
• Acoso o multicuentas = descalificación. Te puedes retirar cuando quieras comentando RETIRO.

📌 Bases completas en el carrusel fijado del perfil.

La primera puerta se abre el miércoles 18.
¿Entras? 👇

Esta promoción no está patrocinada, avalada ni administrada por Instagram ni Meta, ni está asociada a ellos.

#IGramGames #Temporada1 #PixelArt
```

## Comentario fijado

```
📌 Para entrar: comenta la palabra ENTRO + un emoji (por ejemplo, ENTRO 🔥).
1 cuenta = 1 jugador · Cierre: mar 17 nov, 20:00 CDMX.
```

> Nota para la ingesta: el comentario fijado contiene "ENTRO". El parser **tiene que excluir la cuenta anfitriona**.

---

## Guion con tiempos (salida del pipeline)

| t (s) | Línea | Escena | Texto en pantalla |
|---|---|---|---|
| 00.00 | K01 | hook | ESTE COMENTARIO PUEDE ELIMINARTE. |
| 02.36 | K02 | derez | O SER EL ÚLTIMO EN PIE. |
| 04.24 | K03 | logo | BIENVENIDO A IGRAM GAMES. |
| 06.86 | K04 | conteo | 6 JUEGOS. 1 GANADOR. |
| 11.06 | K05 | tease | Y HAY UNA REGLA QUE NADIE VE VENIR. |
| 14.56 | K06 | id | 1. COMENTAS, Y RECIBES UN NÚMERO. |
| 17.96 | K07 | id_zoom | ESE NÚMERO ERES TÚ. |
| 19.88 | K08 | reglas | 2. REGLAS PÚBLICAS, ANTES DE JUGAR. NADIE LAS CAMBIA. NI NOSOTROS. |
| 26.78 | K09 | elecciones | 3. TUS DECISIONES, Y LAS DE TODOS, DECIDEN QUIÉN CAE. |
| 31.49 | K10 | fantasma | Y LA 4. SI CAES... NO TE VAS. |
| 35.50 | K11 | votos | LOS ELIMINADOS SIGUEN VOTANDO CÓMO SE JUEGA. |
| 38.19 | K12 | comentario | COMENTA ENTRO Y UN EMOJI. AHORA. |
| 41.08 | K13 | fecha | CIERRA EL MARTES 17, A LAS 20:00, HORA CDMX. |
| 45.47 | K14 | puertas | EL MIÉRCOLES 18, ABRE LA PRIMERA PUERTA. |
| 48.81 | K15 | final | ¿ENTRAS? |

## Por qué engancha (estructura de retención)

| Recurso | Dónde | Para qué |
|---|---|---|
| **Gancho en el fotograma 0**: "ESTE COMENTARIO PUEDE ELIMINARTE" con la tarjeta de comentario, rayas de peligro e impacto de audio en el segundo 0 | 0:00–0:02 | Se entiende sin sonido y sin fundido de entrada; abre la pregunta "¿qué pasa si comento?" |
| **Segundo gancho**: "O ser el último en pie" (la multitud se desintegra y queda uno) | 0:02–0:04 | Promesa: la recompensa de entrar |
| **Lazo abierto**: "Una regla que NADIE ve venir…" | 0:11 → se cierra en la regla 4 (0:31) | Retiene hasta el último tercio |
| **Contador "REGLA 1/4 … 4/4"** | 0:14–0:37 | El espectador sabe cuánto falta |
| **SLAM** (palabra gigante + flash + sacudida): NADIE · TÚ · NI NOSOTROS · CAE · NO TE VAS · AHORA | cada 3–6 s | Interrupción de patrón en las frases clave |
| **Golpe de zoom + sonido en cada palabra de énfasis y en cada corte** | continuo | Un cambio visual cada ≈ 1.5–3 s |
| **Silencios dramáticos** antes de "Ni nosotros" y de "¿Entras?" | 0:26 y 0:48 | El contraste hace que el golpe pegue más |
| **Bucle**: el último fotograma es el primero ("¿ENTRAS?" → "ESTE COMENTARIO PUEDE ELIMINARTE") | 0:51 | Cada repetición suma tiempo de visualización |

Subtítulos dentro de la zona segura (inferior libre ≈ 320 px, superior ≈ 120 px, lateral ≈ 120 px).

**Cumplimiento de las Hard Rules:** no hay cifras de participantes, el único ID es `J-????` (o dígitos girando como ruleta), el comentario de muestra lleva la etiqueta "EJEMPLO" y no aparecen handles. La eliminación se muestra como "desconexión" pixelada, sin violencia. Todo el arte, la fuente, la música y los efectos son originales y se generan por código.

---

## Pipeline (reutilizable para los episodios siguientes)

```
build/guion.py    → texto, nombre, fechas y voz (ÚNICA fuente; cambia aquí)
build/tts.py      → locución por línea (Pollinations · MAI-Voice es-MX-Alejo, recortada y a 1.12×) + tiempos por palabra (Whisper)
build/mezcla.py   → línea de tiempo + música/efectos sintetizados + mezcla a −14 LUFS
build/render.py   → escenas pixel art 360×640 → ×3 → MP4 (≈1 min de render)
build/piezas.py   → portada + carrusel de bases
build/fuente.py   → fuente bitmap propia (mayúsculas, acentos, Ñ)
```

Para regenerar todo: `cd episodio0/build && python3 tts.py && python3 mezcla.py && python3 render.py && python3 piezas.py`.
Para cambiar el **nombre** o la **fecha de cierre**, edita `guion.py`, regenera la línea afectada (`python3 tts.py K03`, `K13` o `K14`) y vuelve a correr `mezcla.py`, `render.py` y `piezas.py`.

**Voz:** ElevenLabs no tiene saldo (cuenta gratuita, unos 400 caracteres restantes) y OpenAI no tiene créditos. La locución usa MAI-Voice (es-MX-Alejo) vía Pollinations. Para tener la voz definitiva del Anfitrión en ElevenLabs hace falta un plan de pago.

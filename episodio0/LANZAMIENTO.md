# Episodio 0: Convocatoria (lanzamiento: sábado 14 de noviembre de 2026)

**Inscripción:** desde que se publica el Reel hasta el **martes 17 de noviembre de 2026, 20:00 CDMX** (02:00 UTC del miércoles 18)
**Juego 1:** miércoles 18 de noviembre de 2026

## Archivos para publicar (`episodio0/out/`)

| Archivo | Uso | Formato |
|---|---|---|
| `episodio0_convocatoria.mp4` | Reel de convocatoria | 1080×1920 · 30 fps · 65 s · H.264 + AAC · −14 LUFS |
| `portada_reel.png` | Portada del Reel | 1080×1920; lo importante cae dentro del recorte 3:4 de la cuadrícula |
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
🔻 IGRAM GAMES · TEMPORADA 1 · INSCRIPCIONES ABIERTAS 🔻

Todos pueden entrar. Solo uno va a ganar.
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
¿Entras?

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
| 00.70 | L01 | multitud | TODOS PUEDEN ENTRAR. |
| 02.92 | L02 | derez | SOLO UNO VA A GANAR. |
| 05.54 | L03 | logo | ESTO ES IGRAM GAMES. |
| 08.06 | L04 | conteo | 6 SEMANAS. 6 JUEGOS. 1 GANADOR. |
| 12.93 | L05 | id | AL INSCRIBIRTE, RECIBES UN NÚMERO. |
| 16.59 | L06 | id_zoom | ESE NÚMERO ERES TÚ. |
| 19.01 | L07 | reglas | LAS REGLAS SE PUBLICAN ANTES DE CADA JUEGO... Y NADIE LAS CAMBIA. |
| 25.42 | L08 | elecciones | TUS DECISIONES, Y LAS DE TODOS LOS DEMÁS, DECIDEN SI SIGUES. |
| 30.58 | L09 | fantasma | Y SI CAES... NO TE VAS. |
| 34.16 | L10 | votos | LOS ELIMINADOS SIGUEN VOTANDO CÓMO SE JUEGA. |
| 37.45 | L11 | comentario | PARA ENTRAR, COMENTA "ENTRO" Y UN EMOJI EN ESTE VIDEO. |
| 42.51 | L12 | fecha | LAS INSCRIPCIONES CIERRAN EL MARTES 17 DE NOVIEMBRE, A LAS 20:00, HORA CDMX. |
| 51.05 | L13 | gratis | ES GRATIS. Y TODO ES DIGITAL. |
| 55.29 | L14 | puertas | LA PRIMERA PUERTA SE ABRE EL MIÉRCOLES 18. |
| 60.20 | L15 | final | ¿ENTRAS? |

**Cumplimiento de las Hard Rules:** no hay cifras de participantes, el único ID es `J-????` (o dígitos girando como ruleta), el comentario de muestra lleva la etiqueta "EJEMPLO" y no aparecen handles. La eliminación se muestra como "desconexión" pixelada, sin violencia. Todo el arte, la fuente, la música y los efectos son originales y se generan por código.

---

## Pipeline (reutilizable para los episodios siguientes)

```
build/guion.py    → texto, nombre, fechas y voz (ÚNICA fuente; cambia aquí)
build/tts.py      → locución por línea (Pollinations · MAI-Voice es-MX-Alejo) + tiempos por palabra (Whisper)
build/mezcla.py   → línea de tiempo + música/efectos sintetizados + mezcla a −14 LUFS
build/render.py   → escenas pixel art 360×640 → ×3 → MP4 (≈1 min de render)
build/piezas.py   → portada + carrusel de bases
build/fuente.py   → fuente bitmap propia (mayúsculas, acentos, Ñ)
```

Para regenerar todo: `cd episodio0/build && python3 tts.py && python3 mezcla.py && python3 render.py && python3 piezas.py`.
Para cambiar el **nombre** o la **fecha de cierre**, edita `guion.py`, regenera la línea afectada (`python3 tts.py L03`, `L12` o `L14`) y vuelve a correr `mezcla.py`, `render.py` y `piezas.py`.

**Voz:** ElevenLabs no tiene saldo (cuenta gratuita, unos 400 caracteres restantes) y OpenAI no tiene créditos. La locución usa MAI-Voice (es-MX-Alejo) vía Pollinations. Para tener la voz definitiva del Anfitrión en ElevenLabs hace falta un plan de pago.

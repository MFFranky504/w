# EP-001 — Vuelo 914 — Auditoría según Opus Production Engine 2.0

Fecha: 2026-11-12. Video auditado: `export/final_v02.mp4` (9:42, 44 escenas) y `short_0{1,2,3}_v02.mp4`.
Método: duración medida de cada clip, fotogramas de las 44 escenas en una hoja numerada, primer fotograma, medición de loudness, negros y silencios, lectura del guion completo. **No escuché el audio completo ni vi el video de corrido.**
Segunda opinión: Gemini revisó la hoja numerada. Confirmó texto falso, rostros y duplicados, pero se equivocó de número en varias escenas. Su revisión sirve de confirmación, no de fuente.
**Fase actual: auditoría entregada. No se volvió a renderizar nada. Esperando aprobación.**

---

## 1. Qué funciona y se conserva

- **El caso elegido para un primer episodio:** riesgo legal nulo, monetizable y con un giro claro (la "historia real" es un tabloide).
- **Estructura en 9 bloques** con re-hooks y doble final. Le falta ritmo, pero el esqueleto sirve.
- **Etiqueta de certeza por bloque.** Es la idea diferencial del canal. Se conserva, pero hay que hacerla honesta (ver §4).
- **Audio técnico:** -16.0 LUFS integrado, audio y video sincronizados (diferencia < 0.1 s), cero fotogramas negros y cero cortes de audio.
- **Algunas imágenes con tema concreto:** 6 (terminal de los años 50), 7 (cabina de pasajeros), 9 (torre de control), 15 (consolas de los 80), 16 (micrófono de la torre), 17 (silueta en la torre ante la luz). Son la dirección correcta.
- **El build es reproducible:** el guion en markdown genera voz, imágenes, clips y exports. Reutiliza los assets ya generados.

## 2. Problemas de hook y retención

| # | Problema | Evidencia |
| :-: | :--- | :--- |
| H1 | **Primera imagen genérica:** avión en silueta contra el sol. No aparece nada propio de este caso. | Escena 1, 0:00 |
| H2 | **Primera frase genérica:** "¿Es posible que un avión viaje a través del tiempo...?" Sirve para cualquier video de viajes en el tiempo. | 0:00 |
| H3 | **Esa misma toma dura 14 s.** Ningún plano del video baja de 11.5 s: promedio 13.2 s, máximo 16.8 s. El zoom de 10% en 13 s se ve como imagen fija. | Las 44 escenas |
| H4 | **El primer dato concreto (la fecha) llega en 1:11.** El primer minuto es preámbulo sin información. | Bloque 1 completo |
| H5 | **"Bienvenidos a Archivo Cero" a los 0:56.** Saludo de canal dentro del cold open. | Escena 5 |
| H6 | **Spoiler en 0:40:** "Todo tiene una explicación." Mata la tensión antes de contar la historia. | Escena 4 |
| H7 | **El fondo sonoro es un drone de 55 Hz fijo durante 9:42.** No evoluciona. Además rellena las pausas: no hay ni un silencio de 1.5 s o más, aunque el guion pide 2 s entre bloques. | Medido con silencedetect |
| H8 | **Los Shorts no tienen gancho.** Empiezan a mitad de una escena del largo. Por ejemplo, el Short 1 abre con "El relato cuenta que, décadas tras la desaparición...". | Shorts 1-3 |

## 3. Escenas genéricas o repetidas

**Duplicadas, por la cuota de imágenes agotada:** las escenas 31 a 44 repiten las 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25 y 27. Es el 32% del episodio. Afecta a los bloques 7, 8 y 9 completos: justo el desenlace.

**Genéricas, sin sujeto del caso:**
- 2: pista nocturna vacía.
- 3: pila de mapas.
- 4: lámpara y lupa.
- 8: retícula de radar abstracta.
- 10: nubes.
- 13: punto de luz en negro.
- 18: luz borrosa.
- 19: ventana oscura.
- 22: máquina de escribir.
- 24: espejo roto en un ático (narración: "inconsistencia pura").
- 26: rodillos de imprenta.
- 29: lente de cámara.
- 30: estanterías de archivo.

**Demasiado oscuras para leerse:** 4, 13 y 19.

**Con personas o rostros**, que hay que revisar según la Biblia §5.3: 6 (multitud en la terminal), 17 (silueta con gorra) y 28 (gente en un quiosco).

**Imagen y narración no corresponden:**
- 24: espejo en un ático para hablar de fechas contradictorias.
- 29: lente de cámara para hablar de vender ejemplares.
- 5: el texto dice "radares", pero la imagen muestra un icono de avión sobre una esfera.

## 4. Documentos, fechas y textos incoherentes

| Escena | Texto que inventó el generador | Por qué es grave |
| :-: | :--- | :--- |
| 11 (y 36) | Calendario: "Augusser", "2015" y "1955" juntos | Dos años contradictorios en la "prueba" central del caso |
| 12 | Calendario: "Jarney" | Mes inexistente |
| 14 | Calendario: "10" y "1955" en rojo | Fecha que no existe en el relato |
| 20 | "The Autia News", "The Berts Setceres Lebs" | Titulares sin sentido presentados como prensa |
| 21 (y 41) | "Calender" | Errata |
| 23 (y 42) | "NOAY DATES" y celdas ilegibles | Documento falso |
| 25 (y 43) | "NEWS", "ALIENS GHOSTT", "Clelliars" | Imita una portada del tabloide con errores |
| 28 | "Gumvat", "LAUTONS", "wingnel" | Quiosco con marcas sin sentido |

**Badge falso de certeza:** los bloques 5, 6, 7 y 9 muestran **HECHO VERIFICADO**, pero ninguna fuente de `01_INVESTIGACION.md` fue comprobada por un humano. Es el error de credibilidad más serio del video.

**Afirmaciones del guion sin fuente**, que salen de Gemini y no del dossier:
- Escena 2.4: "los sistemas de seguimiento eran limitados... generaran incertidumbre y miedo entre las autoridades aeronáuticas".
- Escena 2.3: "desapareció de los radares sin emitir señal de socorro". Es parte de la leyenda, pero se narra como si fuera un hecho.

**Frases de relleno** que el Engine 2.0 §9 prohíbe:
- "Empecemos este viaje ahora."
- "Todo aclarado."
- "Absolutamente nada."
- "la aburrida realidad".
- "¿estamos dispuestos a ignorar la verdad científica...?" El caso no trata de ciencia, sino de periodismo.

**Cómo evitarlo:**
1. Ningún prompt pide objetos con texto. Calendarios, periódicos y documentos se piden "blank, no text, no letters, no numbers".
2. Todo texto legible lo pone el build con tipografía real, sacado de un campo del storyboard ya verificado.
3. Antes de montar, Gemini revisa cada imagen por separado (no en hoja: en hoja se equivoca de número). Si detecta texto legible, la imagen se rechaza y se regenera.
4. El build no permite el badge "HECHO VERIFICADO" mientras quede una fuente sin marcar en `01_INVESTIGACION.md`. En su lugar muestra "VERIFICACIÓN PENDIENTE".
5. Nada que imite la portada real de *Weekly World News*. Si se quiere mostrar la portada auténtica, se usa una captura breve con cita, y eso requiere tu aprobación (§12).
6. Cada recurso en pantalla lleva su categoría (archivo, gráfico original, recreación o ambiente). Las recreaciones llevan la marca "RECREACIÓN" en pantalla.

## 5. Cambios concretos

### Storyboard

- **Unidad = plano, no frase.** Cada línea de narración se reparte en 2 o 3 planos de 4 a 8 s. Un plano largo solo se permite si el storyboard dice por qué.
- **Formato por plano:** narración, qué se ve exactamente, categoría del recurso, escala (general, medio, detalle o gráfico), movimiento con su motivo, sonido y función narrativa.
- **Planos concretos para este caso:**
  - Mapa con la ruta Nueva York–Miami (gráfico original) y la ubicación de Maiquetía.
  - Línea de tiempo 1955 → 1985 → años 90 → década de 2010, igual que la cronología del dossier.
  - Comparación lado a lado "versión 1985 / versión años 90": el año del aterrizaje que cambia, en tipografía limpia.
  - Calendario de bolsillo generado en blanco, con "1955" compuesto encima.
  - Torre de Maiquetía en los años 80, de noche: exterior, consola y micrófono.
  - Cuatro motores y cola simple del DC-4 en la recreación del avión.
- **Prohibido el plano "ambiente sin sujeto"** salvo como respiro marcado, como máximo uno por bloque.

### Generación visual

- Prompts sin texto para objetos con texto (ver §4).
- Revisión con Gemini por imagen: texto, rostros y oscuridad. Rechazo automático.
- Los mapas, líneas de tiempo, comparaciones y tarjetas de cita los genera el build con código. Son gratis, ilimitados y exactos. Calculo que cubren entre el 30 y el 40% de los planos.
- **Cuota de Cloudflare:** alcanza para unas 30 imágenes por día. A 4–8 s por plano, un episodio de 10 min necesita entre 75 y 100 planos, o sea, unas 50 imágenes generadas más los gráficos. Producirlo toma 2 días. Un episodio de 20 min toma 4 días.
- Una imagen puede dar dos planos (general y detalle por recorte) solo si la composición cambia de verdad.
- La gradación pasa de "todo azul" a una paleta por época: años 50 más cálida y sepia, años 80 en verde fluorescente de consola, investigación en frío neutro. Esto es un cambio estético y requiere tu aprobación (§12).

### Montaje

- Los cortes caen en los límites de frase. Edge TTS entrega los tiempos de cada palabra, así que un plano no corta a mitad de palabra.
- Movimiento motivado: paneo hacia el sujeto o revelación de un detalle. Se elimina el zoom uniforme de 10%.
- **Cold open sin saludo ni logo.** La marca aparece, si acaso, después del cold open (unos 40 s).
- Sonido por bloque: base que cambia según el lugar (zumbido de terminal, estática de radio en la torre, sala de redacción), silencio real antes de las revelaciones y el drone bajando bajo la voz.
- Los Shorts tienen guion propio de 0–3 s: frase de gancho y el plano más fuerte del caso, por ejemplo el calendario 1955 sobre la pista.

## 6. Herramientas: qué hay de verdad

Probado hoy, 12-11-2026, con una petición mínima a cada una.

| Herramienta | Estado | Uso propuesto |
| :--- | :--- | :--- |
| Gemini `gemini-3.1-flash-lite` | ✅ texto e imagen | Dossier, crítica del guion, QC por imagen |
| NVIDIA `minimaxai/minimax-m3.1-flash` | ✅ solo textos cortos | Hooks alternativos, títulos |
| NVIDIA `deepseek-ai/deepseek-v4.1-flash` | ❌ 502 en dos intentos | Era la segunda opinión estructural. No disponible hoy |
| OpenRouter DeepSeek gratis | ❌ ya no es gratis (404) | — |
| NVIDIA Nemotron super 49B / 120B | ❌ retirado (410) o no habilitado (404) | — |
| OpenRouter `nvidia/nemotron-3.5-super-vl:free` | ✅ responde y acepta imágenes | Segunda opinión de QC visual. **Reemplaza a DeepSeek como crítico estructural** |
| OpenRouter `liquid/lfm-2.5-2.6b:free` | ✅ modelo pequeño | No aporta para este trabajo |
| Z.AI `glm-4.5-flash` | ⚠️ responde, pero gasta los tokens razonando y devuelve el contenido vacío | Solo con `max_tokens` alto |
| Cloudflare Flux schnell | ⚠️ cuota diaria agotada (10.000 neuronas, unas 30 imágenes) | Imágenes. Se renueva cada día |
| Edge TTS `es-MX-JorgeNeural` | ✅ vía proxy | Narración |
| ElevenLabs | ⚠️ plan gratis: 8.571 de 10.000 caracteres usados, quedan 1.429 | Alcanza para un Short o unos efectos de sonido. No para un episodio |
| **Codex** | ❌ no hay CLI `codex` ni plugin instalado. OpenAI sin crédito | Ninguna por ahora |

**Si activas Codex** (plugin instalado más `!codex login` en tu terminal), le asignaría tres tareas:
- Auditar `tools/build_episode.py`.
- Escribir pruebas del parser del storyboard.
- Revisar el corte por tiempos de palabra.

Mientras tanto, esas tareas las hago yo.

## 7. Plan de corrección priorizado por impacto

| P | Cambio | Impacto | Costo |
| :-: | :--- | :--- | :--- |
| 1 | Reescribir el hook y el cold open (0–45 s): tres opciones, elegir una, sin saludo ni spoiler | Retención de los primeros 30 s, la caída más cara | Bajo |
| 2 | Badge de certeza atado a la verificación real, y verificación humana de las 6 fuentes | Credibilidad: hoy el video afirma "verificado" sin serlo | Bajo para mí, 1–2 h tuyas |
| 3 | Planos de 4–8 s cortados en límites de frase | Retención en todo el video | Medio |
| 4 | Cero texto generado: composición tipográfica más QC por imagen | Credibilidad | Medio |
| 5 | Storyboard plano a plano con gráficos originales (mapa, línea de tiempo, comparación) | Especificidad y menos imágenes generadas | Medio |
| 6 | Quitar del guion el relleno y las dos afirmaciones sin fuente | Credibilidad y ritmo | Bajo |
| 7 | Sonido por bloque y silencios reales | Atmósfera | Medio |
| 8 | Shorts con gancho propio | Tráfico de entrada | Bajo |
| 9 | Paleta por época | Variedad visual | Bajo, pero requiere aprobación estética |

Las 14 imágenes de marcador quedan absorbidas por el punto 5: el storyboard nuevo pide imágenes distintas.

## 8. Flujo de producción mejorado

| Fase | Quién | Entregable | Puerta para pasar |
| :-: | :--- | :--- | :--- |
| 0 Auditoría | Opus | Estado de herramientas | — |
| 1 Tema | Opus propone; Gemini y MiniMax aportan alternativas | 3 temas puntuados, 1 recomendado | **Tu aprobación** |
| 2 Dossier | Gemini busca; Opus sintetiza | `01_INVESTIGACION.md` con fuentes marcables | **Tú marcas las fuentes como comprobadas** |
| 3 Hook | Opus escribe 3; Gemini critica | Hook elegido y cold open | **Tu aprobación**; después, autonomía |
| 4 Guion | Opus | Narración con tiempo calculado a 140 ppm y fuente por afirmación | Nemotron-VL o Gemini buscan huecos lógicos |
| 5 Storyboard | Opus | Tabla plano a plano (§5) | Ningún plano sin sujeto ni función |
| 6 Producción | Build: voz, gráficos, imágenes con QC y montaje | Clips por bloque | Rechazo automático por texto, rostro u oscuridad |
| 7 QC | Opus revisa todos los fotogramas por plano; Gemini revisa las imágenes una por una | `03_LEGAL_QC.md` | Checklist completo |
| 8 Entrega | Opus | MP4, títulos, descripción, capítulos, miniatura, comentario fijado, Short y fuentes | El archivo se reproduce y tiene audio |
| 9 Análisis | Opus, con tus métricas | Diagnóstico | — |

**Cambios al pipeline que requieren tu aprobación (§12):**
- Formato de storyboard plano a plano.
- Generador de gráficos.
- Cortes por tiempo de palabra.
- QC automático con Gemini.
- Badge atado a la verificación.

Todo esto extiende `tools/build_episode.py`; no lo reemplaza.

## 9. Decisiones abiertas

1. **Duración vs. tema.** El Engine 2.0 pide 15–25 min. Vuelo 914 da para unos 10–12 min sin relleno: es un artículo de tabloide y su desmentido. Opciones:
   - (a) Dejar EP-001 en 10–12 min y aceptar la excepción.
   - (b) Ampliarlo a "los aviones que volvieron del pasado": el mismo tabloide publicó otros relatos parecidos. Llega a 15–20 min con material real, pero hay que verificar esos otros casos.
   - (c) Archivar Vuelo 914 como piloto y elegir un tema con más fuentes para el estreno.
2. **Voz.** Edge TTS es la única opción con capacidad hoy. La Biblia v2.1 limitaba el TTS gratis a 8–12 min por la fatiga auditiva. Un episodio de 15–25 min con Edge TTS contradice esa regla. Grabar tu voz la resuelve.
3. **Paleta por época** (§5): sí o no.

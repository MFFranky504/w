# Notas del proyecto

## Gemini
El entorno tiene guardada una clave de Gemini para `generativelanguage.googleapis.com`; el proxy la inyecta. Para usarla: `tuconfia/src/gemini.sh "pregunta" [modelo]`. El modelo por defecto es `gemini-3.1-flash-lite`. `gemini-3.8-flash` daba error 502 y `gemini-3.1-pro-preview` se enfría con frecuencia. Si un chat corre en otro entorno, la clave no existe y hay que guardarla de nuevo con el formulario seguro de credenciales.

Uso en el flujo de vídeos: Gemini verifica hechos del guion, hace de abogado del diablo sobre el guion y los fotogramas, y redacta textos. Sus avisos no son definitivos: algunos son errores de lectura (por ejemplo leyó un subtítulo a medias como falta de ortografía), así que se contrastan antes de aplicarlos.

## Shorts casi automáticos (Gemini hace casi todo)
`python3 tuconfia/src/auto_short.py <nombre> "<famoso>" "<enfoque>" "<hechos permitidos>"` pide a Gemini hechos, guion, reparto, escenas y ganchos; genera voz (ElevenLabs), alineación, render, revisión visual y textos de plataforma. Requiere `pip install --no-deps num2words`.
Reglas aprendidas: dar siempre los hechos permitidos (sin ellos Gemini inventa datos, por ejemplo un despido que nunca existió); revisar el tono de piel y el pelo del reparto (Gemini puso a Morgan Freeman con piel clara); los ganchos de pantalla no pueden pasar de 13 caracteres por línea; y mirar si el kit de escena encaja con lo narrado.

## Voz gratis (si se acaba ElevenLabs)
Pollinations (`gen.pollinations.ai`, clave ya guardada en el entorno) tiene voces gratis por `/v1/audio/speech`, en formato OpenAI. Gemini las escuchó y la mejor fue `model: microsoft/mai-voice-2.1`, `voice: es-MX-Grant` (9/10), seguida de `es-MX-Alejo` (8/10). Las de OpenAI (onyx, echo) suenan peor en español. Hay muestras en `tuconfia/audio/muestras_voz/`. Las voces de Gemini no devuelven audio por la ruta OpenAI y la nativa está bloqueada para nuestra clave.

# Notas del proyecto

## Gemini
El entorno tiene guardada una clave de Gemini para `generativelanguage.googleapis.com`; el proxy la inyecta. Para usarla: `tuconfia/src/gemini.sh "pregunta" [modelo]`. El modelo por defecto es `gemini-3.1-flash-lite`. `gemini-3.8-flash` daba error 502 y `gemini-3.1-pro-preview` se enfría con frecuencia. Si un chat corre en otro entorno, la clave no existe y hay que guardarla de nuevo con el formulario seguro de credenciales.

Uso en el flujo de vídeos: Gemini verifica hechos del guion, hace de abogado del diablo sobre el guion y los fotogramas, y redacta textos. Sus avisos no son definitivos: algunos son errores de lectura (por ejemplo leyó un subtítulo a medias como falta de ortografía), así que se contrastan antes de aplicarlos.

## Shorts casi automáticos (Gemini hace casi todo)
`python3 tuconfia/src/auto_short.py <nombre> "<famoso>" "<enfoque>" "<hechos permitidos>"` pide a Gemini hechos, guion, reparto, escenas y ganchos; genera voz (ElevenLabs), alineación, render, revisión visual y textos de plataforma. Requiere `pip install --no-deps num2words`.
Reglas aprendidas: dar siempre los hechos permitidos (sin ellos Gemini inventa datos, por ejemplo un despido que nunca existió); revisar el tono de piel y el pelo del reparto (Gemini puso a Morgan Freeman con piel clara); los ganchos de pantalla no pueden pasar de 13 caracteres por línea; y mirar si el kit de escena encaja con lo narrado.

## Voz gratis (si se acaba ElevenLabs)
Pollinations (`gen.pollinations.ai`, clave ya guardada en el entorno) tiene voces gratis por `/v1/audio/speech`, en formato OpenAI. Gemini las escuchó y la mejor fue `model: microsoft/mai-voice-2.1`, `voice: es-MX-Grant` (9/10), seguida de `es-MX-Alejo` (8/10). Las de OpenAI (onyx, echo) suenan peor en español. Hay muestras en `tuconfia/audio/muestras_voz/`. Las voces de Gemini no devuelven audio por la ruta OpenAI y la nativa está bloqueada para nuestra clave.

## Voces: lo que se probó (16-nov-2026)
- ElevenLabs: plan gratis, 10.000 caracteres al mes (se gastaron 9.592; se renueva ~9 dic). El conector de ElevenLabs (herramientas `creative_*`, `account_get_usage`) gasta esos mismos créditos. Es la mejor voz; subir a un plan de pago (Starter) es la mejora real de calidad.
- Pollinations (`microsoft/mai-voice-2.1`): solo `es-MX-Grant` y `es-MX-Alejo` son gratis; Harper, Valeria y es-ES-Marta piden saldo. Los modelos `openai/gpt-audio-*` (con instrucciones de actuación) también piden saldo (~0,006 $ por frase). **La cuota gratis es diaria**: 138 frases la agotaron y respondió 402 hasta que se renueve. Genera las líneas en tandas.
- MeloTTS (Cloudflare) suena robótica (Gemini 2/10); Grant fue 8/10 y Alejo 3/10.
- Para darle vida a Grant sin gastar: `python3 tuconfia/src/narr_viva.py <guion_final.json> <nombre>` reutiliza las líneas ya generadas (`audio/lineas_<nombre>/`) y varía ritmo y tono según la emoción de cada frase (campo `emo`), con ecualización y compresión. Gemini lo puntuó 8/10 frente a 5/10 del original. Después hay que volver a pasar Whisper (Groq `whisper-large-v3`) para los tiempos de palabra.

## Voz Microsoft Edge TTS (gratis, sin cuota)
`pip install edge-tts`; funciona por el proxy: `edge_tts.Communicate(texto, 'es-MX-JorgeNeural', proxy=os.environ['HTTPS_PROXY'])`. `tuconfia/src/voz_short.py <nombre>` la usa por defecto (`VOZ=pollinations` para Grant) y deja narración + alineación para `build_story_short.py`. Usada en el Short de Oprah (16-nov).

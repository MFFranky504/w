# Estado del proyecto Longform Engine 3.0

Directiva: docs/LONGFORM_ENGINE_3.0.md. Fase actual: **0 (auditoría) terminada; esperando decisiones del usuario antes de la Fase 1**.

## Auditoría (hechos medidos el 12-nov-2026)
- Motor: Python + PIL, procedural; 15.937 líneas en src/. Mundo 320x180 a escala 6 (1920x1080) o 160x284 a escala 8 (vertical).
- Vídeos hechos: 2 largos horizontales de unos 3 min (Hawking 193 s, Disney 177 s) y unos 20 Shorts verticales. Ninguno pasa de 3 min 13 s.
- Render horizontal: 14,5 fotogramas por segundo en 1 núcleo (4 núcleos, 15 GB de RAM). 35 min = 63.000 fotogramas = unos 72 min en 1 núcleo.
- Arranque del largo de Disney: sin fotogramas negros; el logo es solo una marca en la esquina; el gancho de texto entra a los 0,5 s. Volumen de los primeros 20 s: -14,6 LUFS.
- Voz: ElevenLabs plan gratis, 2.435 de 10.000 caracteres usados. El largo de Disney gastó 2.741 caracteres para 170 s (16 por segundo), así que 35 min son unos 33.600 caracteres.
- Escenas: un vídeo de 3 min necesitó 15 escenas programadas a mano. Con la misma densidad, 35 min son unas 175.
- Archivo dañado: out/TU_CONFIA_Stephen_King_Carrie_v2_PREVIEW_sin_voz.mp4 (no se puede abrir).

## Integraciones comprobadas
Responden: Gemini gemini-3.1-flash-lite (ve imágenes; a veces da 502), Cloudflare gpt-oss-120b y llama-3.3-70b, Z.AI glm-4.5-flash, NVIDIA MiniMax (máximo 400 tokens), OpenRouter liquid/lfm-2.5-2.6b:free, Codex (sesión de ChatGPT) y ElevenLabs.
No responden: DeepSeek (Cloudflare 403 en plan gratis, SiliconFlow sin saldo, OpenCode Zen con el cupo gratis agotado), OpenAI por API (sin crédito), Qoder.
Ninguna IA externa tiene acceso a internet. Llamadas: src/ia.py.

## Resultados de las otras IAs (docs/fase0/)
- Codex, código: el coste está en la iluminación por fotograma (lib.py:75-81), en ampliar el mundo entero antes de recortar (build_disney.py:183) y en la mezcla de audio completa en RAM (unos 741 MB por arreglo a 35 min). Cinco mejoras: audio por bloques, recortar antes de escalar, precalcular fondos estáticos, acelerar luces, unificar los build_*.py. No tocar: el arte, la escala entera con NEAREST, las escenas modulares, la caché de props, la salida incremental a FFmpeg.
- Gemini, arranque: veredicto «no me quedaría». Composición estática, expresión neutra, texto encima de los personajes. Pide primer plano, luz dramática y una acción desde el primer fotograma. Conservar la paleta nocturna.
- gpt-oss, abogado del diablo: recomienda un paso intermedio de 8 a 12 min antes de 30-40. Sus cifras de render (70 h) y de coste de voz (150 dólares) no coinciden con lo medido y se descartan.
- llama, temas: lista genérica (Celia Cruz, Che Guevara, Selena, Pablo Escobar, Frida Kahlo, Luis Miguel...) con fuentes sin concretar. No sirve como selección; el tema se decide en la Fase 1 con investigación real.

## Decisiones pendientes del usuario
1. Duración del primer episodio: piloto de 8-12 min o directo a 30-40.
2. Voz: la cuota gratis no alcanza para un episodio largo.
3. Investigación con fuentes: solo Claude tiene búsqueda web.
4. Tema del primer documental.

## Próximo paso exacto
Con las respuestas: Fase 1 (tema) y, en paralelo, las dos primeras mejoras del motor probadas en un clip de 20-30 s (plano de apertura con expresión y luz; escenas descritas por datos).

# Notas del proyecto

## Gemini
El entorno tiene guardada una clave de Gemini para `generativelanguage.googleapis.com`; el proxy la inyecta. Para usarla: `tuconfia/src/gemini.sh "pregunta" [modelo]`. El modelo por defecto es `gemini-3.1-flash-lite`. `gemini-3.8-flash` daba error 502 y `gemini-3.1-pro-preview` se enfría con frecuencia. Si un chat corre en otro entorno, la clave no existe y hay que guardarla de nuevo con el formulario seguro de credenciales.

Uso en el flujo de vídeos: Gemini verifica hechos del guion, hace de abogado del diablo sobre el guion y los fotogramas, y redacta textos. Sus avisos no son definitivos: algunos son errores de lectura (por ejemplo leyó un subtítulo a medias como falta de ortografía), así que se contrastan antes de aplicarlos.

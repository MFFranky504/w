## Hallazgos

La barrera principal es el **costo de CPU por fotograma**. El código fija 30 fps y 1920×1080 en [build_disney.py:18](/home/user/w/tuconfia/src/build_disney.py:18); 35 minutos implican 63.000 fotogramas y unos **3,73 billones de píxeles de salida** que procesar, antes de contar efectos y codificación.

1. **Cuellos de botella**
   - [lib.py:75](/home/user/w/tuconfia/src/lib.py:75) vuelve a convertir la imagen a NumPy y aplica cada luz con operaciones sobre matrices de todo el mundo; después crea más arreglos para emisivos, viñeta y Bayer ([lib.py:76](/home/user/w/tuconfia/src/lib.py:76), [lib.py:81](/home/user/w/tuconfia/src/lib.py:81)). Las escenas llaman `render()` cada fotograma; algunas suman decenas de luces, por ejemplo [scenes11.py:17](/home/user/w/tuconfia/src/scenes11.py:17) y [scenes11.py:323](/home/user/w/tuconfia/src/scenes11.py:323).
   - [build_disney.py:183](/home/user/w/tuconfia/src/build_disney.py:183) amplía el mundo entero antes de recortarlo. En transiciones vuelve a renderizar dos escenas y hace arreglos de salida de 1920×1080 ([build_disney.py:371](/home/user/w/tuconfia/src/build_disney.py:371), [build_disney.py:377](/home/user/w/tuconfia/src/build_disney.py:377)).
   - Escenas con partículas, detalles y aleatoriedad recrean objetos y recorren bucles por fotograma; ejemplos: [scenes3.py:126](/home/user/w/tuconfia/src/scenes3.py:126), [scenes3.py:314](/home/user/w/tuconfia/src/scenes3.py:314), [bg.py:232](/home/user/w/tuconfia/src/bg.py:232).

2. **Memoria y audio**
   - El vídeo se entrega incrementalmente a FFmpeg ([build_disney.py:550](/home/user/w/tuconfia/src/build_disney.py:550)); no se guardan los 63.000 cuadros en una lista.
   - El audio sí escala mal: [build_disney.py:402](/home/user/w/tuconfia/src/build_disney.py:402) crea estéreo float32 de unos **741 MB por arreglo** a 35 min. La música, efectos, voz, mezcla y conversiones se solapan en RAM ([build_disney.py:479](/home/user/w/tuconfia/src/build_disney.py:479), [build_disney.py:517](/home/user/w/tuconfia/src/build_disney.py:517), [build_disney.py:525](/home/user/w/tuconfia/src/build_disney.py:525)); riesgo alto de varios GB.

3. **Duplicación**
   - [build_disney.py:166](/home/user/w/tuconfia/src/build_disney.py:166) y [build_story_short.py:392](/home/user/w/tuconfia/src/build_story_short.py:392) duplican cámara, transiciones y mezcla; los dos generan audio completo en RAM y lo escriben como WAV ([build_disney.py:531](/home/user/w/tuconfia/src/build_disney.py:531), [build_story_short.py:522](/home/user/w/tuconfia/src/build_story_short.py:522)). Corregirlos por separado facilita divergencias.

## Cinco mejoras de mayor impacto

1. Procesar mezcla de audio por bloques y escribirla progresivamente.
2. Evitar ampliar el mundo completo: recortar región visible y escalarla.
3. Precalcular fondos y capas estáticas; componer solo capas animadas.
4. Acelerar iluminación y reutilizar buffers NumPy, máscaras y arreglos temporales.
5. Extraer pipeline común de render/audio para los `build_*.py`, manteniendo parámetros por formato.

## No tocar

Conservar el arte del motor, el pixel-art con `NEAREST` y escala entera, las escenas modulares, el caché existente de props ([props.py:8](/home/user/w/tuconfia/src/props.py:8)) y la salida de vídeo incremental a FFmpeg. Son bases funcionales que las mejoras pueden preservar.

# Plan del canal: semana del 16 al 22 de noviembre de 2026
El usuario dejó el canal en manos de Claude esta semana (autorizó todo, 16-nov). YUP está conectado (cuenta de YouTube Tu ConfIA). La prueba Pro de YUP termina el 23-nov.

## Reglas
- Máximo UNA publicación al día, a las 20:00 UTC (los Shorts que salieron solos a esa hora hicieron ~1.2K; tres Shorts juntos de madrugada hicieron 2-9 vistas).
- No usar Heard 'Em Say, Congratulations, Mrs. Magic ni every_moment. Música: piano_original y jazz.
- Hechos fijados y comprobados antes de subir; lo que solo contó el protagonista, «según contó».
- Miniaturas: una cara grande y máx. 4 palabras. Títulos con pregunta o contraste.
- No borrar nada sin avisar (YUP no puede borrar vídeos publicados fuera de YUP).

## Calendario (el usuario programó a mano sus propios Shorts del martes 17 y miércoles 18)
| Día | Hora UTC | Qué | Estado |
|---|---|---|---|
| Lun 16 | 20:00 | Largo: Cantinflas (versión sin copyright) | programado, post ebecb9989ff217980529 |
| Mar 17 / Mié 18 | — | Shorts del usuario | no tocar |
| Jue 19 | 20:00 | Short: Jackie Chan | programado, post 9b8df836404b37ef6268 |
| Vie 20 | 20:00 | Largo-lista «5 famosos que lo perdieron casi todo y volvieron» | programado, post e9e95fd8701bd60428a6 |
| Sáb 21 | 20:00 | Short «Cayeron y se levantaron»: Oprah Winfrey (sacada del noticiero de las 6 en 1977; NO fue despedida) | guion y reparto listos (script_oprah_short.json, story_oprah.json); hecho y programado, post d699e861470207292e59 (voz Microsoft Edge TTS es-MX-JorgeNeural, gratis por proxy) |
| Dom 22 | — | Revisión de la semana (get_performance) y plan siguiente | |

## Pendiente del usuario (Studio)
- Borrar el vídeo largo de Cantinflas antiguo (GkMMrDDVPQ8 no; el antiguo es 6RLEjgB3_dc, con las 2 canciones con copyright) cuando el nuevo salga.
- Pegar los textos de docs/canal/ajustes_studio.md.


# Semana 22-28 de noviembre (plan hecho el 20-nov tras el análisis del canal)
Diagnóstico (20-nov): Shorts planos en ~900-1.400 vistas; 41→44 suscriptores en 3 días; largos 7-101 vistas, Cantinflas retención media 34 s de 5 min (11 %).
Prueba de 3 formatos de gancho, midiendo vistas a las 24 h: CIFRA (King, Sanders), PREGUNTA (Beethoven, Lucille), CONTRASTE/resultado primero (Lincoln). Voz de los Shorts nuevos: Microsoft Edge es-CO-GonzaloNeural (si el usuario elige otra, VOZ_ID=...).
| Día | Qué | Post YUP |
|---|---|---|
| Sáb 21 | Short Oprah (voz Jorge) | d699e861470207292e59 |
| Dom 22 | Short Stephen King (CIFRA) | 1ec07e42f6df95897008 |
| Lun 23 | Short Beethoven (PREGUNTA) | c253ea2c54632ea376fb |
| Mar 24 | Short Lincoln (CONTRASTE) | 7caeaaa4bdaf73a637c7 |
| Mié 25 | Short Sanders (CIFRA) | 20126021708a2d6aaf36 |
| Jue 26 | Short Lucille Ball (PREGUNTA) | 147b81a3a23f892beca0 |
| Vie 27 | Largo-lista nº2 «5 personas a las que les dijeron que NO» (Spielberg, Seuss, Dyson, Blakely, Honda; 3:31; voz Edge Gonzalo) | a7ac6496ab2b96881ce4 |
| Sáb 28 / Dom 29 | libres: repetir el formato que gane | |
Fichas: docs/canal/shorts/<n>.json; generar con `python3 -I src/mk_short.py <n>`. Hechos: Lincoln perdió en 1832, 1855 y 1858 (Senado: lo eligen las legislaturas) y fue presidente en 1860; Beethoven casi sordo en el estreno del 7-may-1824 (no dirigía de verdad); Sanders: meme exagerado, solo 1952 Pete Harman (Salt Lake City) y el cheque de 105 $ «según se cuenta»; King: 30 rechazos «según contó», adelanto 2.500 $, bolsillo 400.000 $; Lucille: «no talento» según contó ella.

Largo nº2: guion docs/largo_no5/guion_final.json; escenas src/scenes20.py; motor src/build_no5.py (copia de build_famosos); voz src/voz_edge_largo.py + narr_viva.py + Whisper (Groq); miniatura src/miniatura_no5.py. Capítulos: 0:00, 0:18, 0:56, 1:30, 2:02, 2:34, 2:59.

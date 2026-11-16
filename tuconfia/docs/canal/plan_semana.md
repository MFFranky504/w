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
| Sáb 21 | 20:00 | Short «Cayeron y se levantaron»: Oprah Winfrey (sacada del noticiero de las 6 en 1977; NO fue despedida) | guion y reparto listos (script_oprah_short.json, story_oprah.json); falta voz: `python3 -I src/voz_short.py oprah` cuando Pollinations tenga saldo, luego `STORY=oprah python3 -I src/build_story_short.py`; subir a YUP |
| Dom 22 | — | Revisión de la semana (get_performance) y plan siguiente | |

## Pendiente del usuario (Studio)
- Borrar el vídeo largo de Cantinflas antiguo (GkMMrDDVPQ8 no; el antiguo es 6RLEjgB3_dc, con las 2 canciones con copyright) cuando el nuevo salga.
- Pegar los textos de docs/canal/ajustes_studio.md.

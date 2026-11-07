# Experimento: llevar la conversación de Instagram a TikTok y YouTube

**Punto de partida (7-nov-2026):** IG 29 seg. · 34 likes · 15 comentarios/post. TikTok 5 seg. · 119 vistas · 2 coment./video. YouTube 4 subs · 382 vistas · mediana 1,5 likes.
**Meta:** subir los comentarios por video en TikTok y YouTube hacia lo que ya logra Instagram, y que la gente vuelva por "La respuesta de ayer".

## Qué cambia en cada video (ya implementado)
1. Caption tipo juego (sin nombre del artista): `python3 captions.py <episodio>`.
2. El siguiente video abre con "LA RESPUESTA DE AYER" y revela al artista anterior.
3. Pistas de ultra difícil → fácil; la más fácil va al final con cuenta regresiva 3-2-1.
4. Hook de 2 s: "Solo el 1% adivina este artista" (`HOOK=b`) contra el anterior (`HOOK=a`).
5. Hashtags: #MusicQuiz #AdivinaElArtista #HipHop #Música (+ #Shorts solo en YouTube); el género cambia el 3.er tag.
6. Cierre: "Sígueme para ver la respuesta".

## Diseño (para que la comparación sirva)
- Mismo formato, misma hora y mismo CTA en todos los posts; **solo cambia el género** (o el hook, en una segunda ronda; nunca los dos a la vez).
- 3 posts por género: hip hop, reggaetón y pop = 9 posts. Orden alternado (HH, Reg, Pop, HH, Reg, Pop…) para que el día de la semana no favorezca a un género.
- Artistas sugeridos (ver `content/ARTISTAS.md`): HH → Eminem, Tupac, Kendrick · Reg → Daddy Yankee, Bad Bunny, Karol G · Pop → Michael Jackson, Shakira, Taylor Swift.
- Publica el mismo video en IG, TikTok y YouTube Shorts; anota a las 48 h: vistas, likes, comentarios, compartidos y seguidores.
- Registra cada post en `experiment/results.csv` (copia `results_template.csv`) y corre `python3 experiment/compare_genres.py experiment/results.csv genre` (o `hook`).

## Cómo leer el resultado
- Métrica principal: **comentarios por post (mediana) por plataforma**; secundaria: comentarios por 1.000 vistas.
- Con audiencias tan pequeñas, 1 post bueno mueve todo: no declares ganador con menos de 3 posts por género ni con diferencias de 1-2 comentarios.
- Si un género gana en IG pero no en TikTok/YouTube, la audiencia de cada plataforma es distinta: decide por plataforma.

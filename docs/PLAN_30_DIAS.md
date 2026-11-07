# Plan de 30 días (línea base: 1–7 nov 2026, 14–15 videos por red)

| Red | Línea base | Meta 30 d |
|---|---|---|
| YouTube | 20 suscriptores, 816 vistas medias (mediana 890) | mediana x3, top x10, 100 suscriptores |
| TikTok | 3 seguidores, 259 vistas, 0 comentarios, 0.3 compartidos, 54 s | mediana x3, ≥5 comentarios por video, 100 seguidores |
| Instagram | 9 seguidores, 34 likes, 0.7 comentarios | 100 seguidores |

Son **metas de seguimiento, no promesas**: hoy convierten pocas vistas en seguidores (YouTube: 20 suscriptores con 816 vistas por Short).

## Reglas de decisión (`python3 -m frnky analisis`)
- Un tema con más de 2x la mediana → 3 variaciones más.
- Un tema bajo 0.5x la mediana en 3 videos seguidos → se retira.
- Cada experimento cambia una sola variable.
- CTA: se compara comentarios y compartidos medios por texto.

## Cada semana
1. Llena `resultados.csv` (`python3 -m frnky result --fecha … --red … --vistas …`).
2. Corre `python3 -m frnky analisis`.
3. Ajusta `data/calendario.csv` según los ganadores.

## Horarios (hora México)
Principal 16:00 (lun–mié); secundario 07:30; Instagram prueba 19:00 (mié, vie, dom). Máximo 2 videos al día. Los mejores videos salieron 16:00–16:30 martes y miércoles, pero con 14–15 videos por red es una pista, no una prueba.
